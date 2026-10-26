#!/usr/bin/env python3
"""Build the scan inventory and gate scan completion.

Usage:
  scan-gate.py inventory <target> <scan-dir> [--diff BASE HEAD | --working-tree]
                         [--scope PATH ...] [--exclude PREFIX ...]
  scan-gate.py check <scan-dir>

`inventory` writes <scan-dir>/inventory.json. `check` validates every state file in
<scan-dir> against ../schemas, re-derives the inventory, and enforces the rules that
span files. It exits 0 only when the scan may be marked `completed`; otherwise it
lists each problem and exits 1. Exit 2 means the gate could not run. Standard library only.
"""

# Postponed evaluation lets SchemaNode and InventorySpec annotate their own type in their class bodies.
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import TypedDict, cast

Json = dict[str, "Json"] | list["Json"] | str | int | float | bool | None

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"
STATE_FILES = (
    ("inventory.json", "inventory.schema.json"),
    ("coverage.json", "coverage.schema.json"),
    ("candidates.json", "candidates.schema.json"),
    ("findings.json", "findings.schema.json"),
    ("scan-state.json", "scan-state.schema.json"),
)

# Keep equal to references/severity-policy.md "Matrix" (upstream calibration matrix); read-only.
SEVERITY_MATRIX: dict[str, dict[str, tuple[str, ...]]] = {
    "high": {"high": ("high", "critical"), "medium": ("medium",), "low": ("low",),
             "ignore": ("ignore",), "unknown": ("medium",)},
    "medium": {"high": ("medium",), "medium": ("low",), "low": ("low",),
               "ignore": ("ignore",), "unknown": ("low",)},
    "low": {"high": ("low",), "medium": ("low",), "low": ("low",),
            "ignore": ("ignore",), "unknown": ("low",)},
    "ignore": {level: ("ignore",) for level in ("high", "medium", "low", "ignore", "unknown")},
    "unknown": {"high": ("medium",), "medium": ("low",), "low": ("low",),
                "ignore": ("ignore",), "unknown": ("low",)},
}
REQUIRED_LENSES = ("inverted-assumption", "data-representation")
EXAMPLE_LIMIT = 8
SCHEMA_ERROR_LIMIT = 40


class GateError(Exception):
    """An input the gate cannot evaluate: unreadable target, git failure, bad schema or arguments."""


def _examples(items: Iterable[str]) -> str:
    ordered = sorted(items)
    shown = ", ".join(ordered[:EXAMPLE_LIMIT])
    return shown + (f", ... (+{len(ordered) - EXAMPLE_LIMIT})" if len(ordered) > EXAMPLE_LIMIT else "")


def _duplicates(values: list[str]) -> set[str]:
    return {value for value, count in Counter(values).items() if count > 1}


# ---------------------------------------------------------------------------
# Schema validation: the subset of JSON Schema 2020-12 the bundled schemas use.
# Parsing rejects any other keyword, so a schema can never carry a rule this validator ignores.

SUPPORTED_KEYWORDS = frozenset({
    "$schema", "$id", "title", "description", "$defs", "$ref", "type", "properties",
    "required", "additionalProperties", "items", "enum", "const", "minItems", "maxItems",
    "uniqueItems", "minLength", "minimum", "pattern", "allOf", "if", "then",
})
JSON_TYPES: dict[str, tuple[type, ...]] = {
    "object": (dict,), "array": (list,), "string": (str,), "boolean": (bool,),
    "integer": (int,), "number": (int, float), "null": (type(None),),
}


@dataclass(frozen=True)
class SchemaNode:
    """One parsed schema object."""

    json_type: str | None = None
    ref: str | None = None
    properties: dict[str, SchemaNode] = field(default_factory=dict)
    required: tuple[str, ...] = ()
    closed: bool = False
    items: SchemaNode | None = None
    enum: tuple[Json, ...] | None = None
    const: tuple[Json] | None = None
    min_items: int = 0
    max_items: int | None = None
    unique_items: bool = False
    min_length: int = 0
    minimum: float | None = None
    pattern: str | None = None
    all_of: tuple[SchemaNode, ...] = ()
    if_then: tuple[SchemaNode, SchemaNode] | None = None

    def refs(self) -> set[str]:
        children = [*self.properties.values(), *self.all_of, *(self.if_then or ()), *([self.items] if self.items else [])]
        return ({self.ref} if self.ref else set()).union(*(child.refs() for child in children))

    def errors(self, value: Json, defs: dict[str, SchemaNode], where: str) -> list[str]:
        """Every way `value` violates this node, as `<where>: <reason>` lines."""
        errors: list[str] = []

        if self.ref is not None:
            errors += defs[self.ref].errors(value, defs, where)

        if self.json_type is not None:
            is_bool = isinstance(value, bool)
            if not isinstance(value, JSON_TYPES[self.json_type]) or (is_bool and self.json_type in ("integer", "number")):
                return errors + [f"{where}: expected {self.json_type}, got {type(value).__name__}"]

        if self.enum is not None and not any(_same_json(value, option) for option in self.enum):
            errors.append(f"{where}: {value!r} is not one of {list(self.enum)}")
        if self.const is not None and not _same_json(value, self.const[0]):
            errors.append(f"{where}: must be {self.const[0]!r}, got {value!r}")

        if isinstance(value, str):
            if len(value) < self.min_length:
                errors.append(f"{where}: shorter than {self.min_length} characters")
            if self.pattern is not None and not re.search(self.pattern, value):
                errors.append(f"{where}: {value!r} does not match {self.pattern}")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if self.minimum is not None and value < self.minimum:
                errors.append(f"{where}: below minimum {self.minimum:g}")

        if isinstance(value, list):
            if len(value) < self.min_items:
                errors.append(f"{where}: needs at least {self.min_items} items")
            if self.max_items is not None and len(value) > self.max_items:
                errors.append(f"{where}: allows at most {self.max_items} items")
            if self.unique_items:
                seen = Counter(json.dumps(item, sort_keys=True) for item in value)
                duplicates = [item for item, count in seen.items() if count > 1]
                if duplicates:
                    errors.append(f"{where}: duplicate items {_examples(duplicates)}")
            if self.items is not None:
                for index, item in enumerate(value):
                    errors += self.items.errors(item, defs, f"{where}[{index}]")

        if isinstance(value, dict):
            errors += [f"{where}: missing {key!r}" for key in self.required if key not in value]
            for key, sub in self.properties.items():
                if key in value:
                    errors += sub.errors(value[key], defs, f"{where}.{key}")
            if self.closed:
                errors += [f"{where}: unknown field {key!r}" for key in value if key not in self.properties]

        for sub in self.all_of:
            errors += sub.errors(value, defs, where)
        if self.if_then is not None and not self.if_then[0].errors(value, defs, where):
            errors += self.if_then[1].errors(value, defs, where)
        return errors


@dataclass(frozen=True)
class Schema:
    root: SchemaNode
    defs: dict[str, SchemaNode]

    def validate(self, value: Json) -> list[str]:
        return self.root.errors(value, self.defs, "$")


def _same_json(left: Json, right: Json) -> bool:
    return type(left) is type(right) and left == right


def _schema_error(where: str, expected: str) -> GateError:
    return GateError(f"schema {where}: expected {expected}")


def _object(value: Json, where: str) -> dict[str, Json]:
    if not isinstance(value, dict):
        raise _schema_error(where, "object")
    return value


def _array(value: Json, where: str) -> list[Json]:
    if not isinstance(value, list):
        raise _schema_error(where, "array")
    return value


def _string(value: Json, where: str) -> str:
    if not isinstance(value, str):
        raise _schema_error(where, "string")
    return value


def _integer(value: Json, where: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise _schema_error(where, "integer")
    return value


def _parse_node(raw: Json, where: str) -> SchemaNode:
    node = _object(raw, where)
    unsupported = set(node) - SUPPORTED_KEYWORDS
    if unsupported:
        raise GateError(f"schema {where}: unsupported keywords {_examples(unsupported)}")

    json_type = _string(node["type"], f"{where}/type") if "type" in node else None
    if json_type is not None and json_type not in JSON_TYPES:
        raise GateError(f"schema {where}: unsupported type {json_type!r}")
    ref = _string(node["$ref"], f"{where}/$ref") if "$ref" in node else None
    if ref is not None and not ref.startswith("#/$defs/"):
        raise GateError(f"schema {where}: only local #/$defs references are supported")

    if_then = None
    if "if" in node:
        if_then = (_parse_node(node["if"], f"{where}/if"), _parse_node(node.get("then", {}), f"{where}/then"))
    properties = _object(node.get("properties", {}), f"{where}/properties")
    all_of = _array(node.get("allOf", []), f"{where}/allOf")

    return SchemaNode(
        json_type=json_type,
        ref=ref.removeprefix("#/$defs/") if ref is not None else None,
        properties={name: _parse_node(sub, f"{where}/properties/{name}") for name, sub in properties.items()},
        required=tuple(_string(key, f"{where}/required")
                       for key in _array(node.get("required", []), f"{where}/required")),
        closed=node.get("additionalProperties") is False,
        items=_parse_node(node["items"], f"{where}/items") if "items" in node else None,
        enum=tuple(_array(node["enum"], f"{where}/enum")) if "enum" in node else None,
        const=(node["const"],) if "const" in node else None,
        min_items=_integer(node.get("minItems", 0), f"{where}/minItems"),
        max_items=_integer(node["maxItems"], f"{where}/maxItems") if "maxItems" in node else None,
        unique_items=node.get("uniqueItems") is True,
        min_length=_integer(node.get("minLength", 0), f"{where}/minLength"),
        minimum=float(_integer(node["minimum"], f"{where}/minimum")) if "minimum" in node else None,
        pattern=_string(node["pattern"], f"{where}/pattern") if "pattern" in node else None,
        all_of=tuple(_parse_node(sub, f"{where}/allOf/{index}") for index, sub in enumerate(all_of)),
        if_then=if_then,
    )


def _load_schema(name: str) -> Schema:
    raw = _object(json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8")), name)
    defs = {key: _parse_node(sub, f"{name}/$defs/{key}") for key, sub in _object(raw.get("$defs", {}), name).items()}
    root = _parse_node({key: value for key, value in raw.items() if key != "$defs"}, name)

    dangling = set().union(root.refs(), *(node.refs() for node in defs.values())) - set(defs)
    if dangling:
        raise GateError(f"schema {name}: $ref to missing $defs {_examples(dangling)}")
    return Schema(root=root, defs=defs)


# ---------------------------------------------------------------------------
# Validated documents: the fields the cross-file rules read. schemas/ hold the full shape;
# documents are cast to these types only after they pass their schema.

class _InventoryRevisions(TypedDict, total=False):
    base: str
    head: str


class InventoryListing(TypedDict):
    source: str
    files: list[str]
    deleted: list[str]
    snapshot_digest: str


class InventoryDoc(InventoryListing, _InventoryRevisions):
    root: str
    mode: str
    scope: list[str]
    exclude: list[str]


class _FileReceiptOptional(TypedDict, total=False):
    reason: str


class FileReceipt(_FileReceiptOptional):
    path: str
    disposition: str


class SupportingFile(TypedDict):
    path: str


class _UnresolvableOptional(TypedDict, total=False):
    candidate: str


class Unresolvable(_UnresolvableOptional):
    question: str


class CoverageDoc(TypedDict):
    snapshot_digest: str
    reviewed_files: list[FileReceipt]
    supporting_files: list[SupportingFile]
    unresolvable: list[Unresolvable]


class ValidationReceipt(TypedDict):
    disposition: str
    survives: str


class _AttackPathOptional(TypedDict, total=False):
    severity: str


class AttackPathReceipt(_AttackPathOptional):
    decision: str


class Candidate(TypedDict):
    id: str
    validation: ValidationReceipt
    attack_path: AttackPathReceipt


class EvidenceItem(TypedDict):
    id: str


class EvidenceRefs(TypedDict):
    evidenceRefs: list[str]


class Level(TypedDict):
    level: str


class FindingAttackPath(TypedDict):
    dataflow: EvidenceRefs
    impact: Level
    likelihood: Level


class Finding(TypedDict):
    id: str
    severity: str
    codeEvidence: list[EvidenceItem]
    rootCause: EvidenceRefs
    validation: EvidenceRefs
    attackPath: FindingAttackPath


class Rejected(TypedDict):
    id: str


class FindingsDoc(TypedDict):
    passes: int
    findings: list[Finding]
    non_findings: list[Rejected]


class Gap(TypedDict):
    id: str


PassRecord = TypedDict("PassRecord", {"pass": int, "lens": str, "new_findings": int, "new_questions": int})


class _ScanStateOptional(TypedDict, total=False):
    status: str


class ScanStateDoc(_ScanStateOptional):
    gaps: list[Gap]
    history: list[PassRecord]


@dataclass(frozen=True)
class ScanDocuments:
    """All five state files of one scan directory, each already valid against its schema."""

    inventory: InventoryDoc
    coverage: CoverageDoc
    candidates: list[Candidate]
    findings: FindingsDoc
    state: ScanStateDoc

    def summary(self) -> str:
        receipts = self.coverage["reviewed_files"]
        dispositions = Counter(receipt["disposition"] for receipt in receipts)
        reasons = Counter(receipt.get("reason", "") for receipt in receipts if receipt["disposition"] == "excluded")
        states = Counter(_candidate_state(candidate) for candidate in self.candidates)
        excluded = ", ".join(f"{reason} {count}" for reason, count in reasons.most_common()) or "none"
        return (f"{len(receipts)} files ({dispositions['reviewed']} reviewed; excluded: {excluded}); "
                f"{sum(states.values())} candidates ({states['reportable']} reportable, "
                f"{states['rejected']} rejected, {states['deferred']} deferred to unresolvable); "
                f"{len(self.state['history'])} passes")


# ---------------------------------------------------------------------------
# Inventory

@dataclass(frozen=True)
class InventorySpec:
    """What to inventory; recorded in inventory.json so `check` can re-derive it."""

    root: Path
    mode: str
    scope: tuple[str, ...]
    exclude: tuple[str, ...]
    base: str | None = None
    head: str | None = None

    def document(self, scan_dir: Path, listing: InventoryListing) -> InventoryDoc:
        # A target inside the scan directory is recorded relative to it, so the pair can move together.
        root = os.path.relpath(self.root, scan_dir) if self.root.is_relative_to(scan_dir) else str(self.root)
        document = InventoryDoc(root=root, mode=self.mode, scope=list(self.scope), exclude=list(self.exclude),
                                source=listing["source"], files=listing["files"], deleted=listing["deleted"],
                                snapshot_digest=listing["snapshot_digest"])
        if self.base is not None and self.head is not None:
            document["base"], document["head"] = self.base, self.head
        return document

    @classmethod
    def recorded(cls, document: InventoryDoc, scan_dir: Path) -> InventorySpec:
        return cls(root=(scan_dir / document["root"]).resolve(), mode=document["mode"],
                   scope=tuple(_relative_path(path, "scope") for path in document["scope"]),
                   exclude=tuple(_relative_path(path, "exclude") for path in document["exclude"]),
                   base=document.get("base"), head=document.get("head"))


def _relative_path(raw: str, label: str) -> str:
    path = PurePosixPath(raw.replace(os.sep, "/"))
    if path.is_absolute() or ".." in path.parts:
        raise GateError(f"{label} {raw!r} must be relative to the target and stay inside it")
    normalized = str(path)
    return "" if normalized == "." else normalized


def _git(root: Path, *args: str, accept: tuple[int, ...] = (0,)) -> tuple[int, list[str]]:
    # The target is untrusted and read-only: never run its fsmonitor hook or refresh its index.
    # Caller GIT_* variables (GIT_DIR, GIT_WORK_TREE, ...) would point git at another repository.
    overrides: list[str] = []
    if args and args[0] == "diff":
        # Diff can invoke clean/process filters even with external diff and textconv disabled.
        _, keys = _git(root, "config", "--null", "--name-only", "--get-regexp",
                       r"^filter\..*\.(clean|smudge|process|required)$", accept=(0, 1))
        for key in sorted(set(keys)):
            value = "false" if key.endswith(".required") else ""
            overrides.extend(("-c", f"{key}={value}"))

    # check-ignore takes plain paths and rejects pathspec magic, including the literal flag.
    literal = ["--literal-pathspecs"] if args and args[0] in {"diff", "ls-files"} else []
    command = ["git", *literal, "--no-pager", "-c", "core.fsmonitor=false",
               *overrides, "-C", str(root), *args]
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    # Older Git ignores GIT_NO_LAZY_FETCH; deny all protocols to block its transports and helpers too.
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1", GIT_ALLOW_PROTOCOL="")

    try:
        completed = subprocess.run(command, capture_output=True, check=False, env=env)
    except FileNotFoundError as error:
        raise GateError("git is not installed but the target is inside a git work tree") from error
    if completed.returncode not in accept:
        detail = completed.stderr.decode("utf-8", "replace").strip()
        raise GateError(f"git {' '.join(args)} in {root} failed: {detail}")
    entries = completed.stdout.decode("utf-8", "surrogateescape").split("\0")
    return completed.returncode, [entry for entry in entries if entry]


def _git_files(root: Path, *args: str) -> list[str]:
    return _git(root, *args)[1]


def _is_git_work_tree(root: Path) -> bool:
    """True when git decides which files exist: inside a work tree and not ignored by it."""
    if not any((parent / ".git").exists() for parent in (root, *root.parents)):
        return False
    _, answer = _git(root, "rev-parse", "--is-inside-work-tree")
    if [line.strip() for line in answer] != ["true"]:
        return False
    ignored, _ = _git(root, "check-ignore", "-q", "--", ".", accept=(0, 1))
    return ignored == 1


def _unreadable(error: OSError) -> None:
    # An unreadable directory would otherwise vanish from the inventory and look covered.
    raise GateError(f"cannot list {error.filename}: {error.strerror}")


def _walk_files(root: Path, scope: tuple[str, ...]) -> list[str]:
    files: list[str] = []
    for start in scope or ("",):
        top = root / start
        if top.is_symlink() or top.is_file():
            files.append(start)
            continue
        for directory, subdirectories, names in os.walk(top, onerror=_unreadable):
            subdirectories[:] = [name for name in subdirectories if name != ".git"]
            linked_directories = [name for name in subdirectories if (Path(directory) / name).is_symlink()]
            for name in [*names, *linked_directories]:
                files.append((Path(directory) / name).relative_to(root).as_posix())
    return files


def _is_excluded(path: str, exclude: tuple[str, ...]) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in exclude)


def _inventory_path(root: Path, relative: str) -> Path:
    normalized = _relative_path(relative, "inventory path")
    for parent in PurePosixPath(normalized).parents:
        if (root / parent).is_symlink():
            raise GateError(f"cannot snapshot {relative}: a parent is a symlink; scope the link itself")
    return root / normalized


def _source_identity(root: Path, relative: str) -> tuple[str, str, int]:
    path = _inventory_path(root, relative)

    try:
        metadata = path.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            return "symlink", os.readlink(path), 0
        if not stat.S_ISREG(metadata.st_mode):
            raise GateError(f"cannot snapshot {relative}: only regular files and symlinks are supported")

        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        with os.fdopen(os.open(path, flags), "rb") as source:
            metadata = os.fstat(source.fileno())
            if not stat.S_ISREG(metadata.st_mode):
                raise GateError(f"cannot snapshot {relative}: the file type changed")
            digest = hashlib.sha256()
            while block := source.read(1024 * 1024):
                digest.update(block)
        return "file", digest.hexdigest(), metadata.st_mode & 0o111
    except OSError as error:
        raise GateError(f"cannot snapshot {relative}: {error}") from error


def _snapshot_digest(spec: InventorySpec, files: list[str], deleted: set[str], revision: str | None) -> str:
    digest = hashlib.sha256()
    parameters = {"mode": spec.mode, "scope": spec.scope, "exclude": spec.exclude,
                  "base": spec.base, "head": spec.head, "worktree_base": revision}
    digest.update(json.dumps(parameters, sort_keys=True, separators=(",", ":")).encode() + b"\n")
    for path in files:
        identity = ("deleted", "", 0) if path in deleted else _source_identity(spec.root, path)
        digest.update(json.dumps((path, *identity), separators=(",", ":")).encode() + b"\n")
    return "sha256:" + digest.hexdigest()


def _require_checked_index(root: Path, scope: tuple[str, ...] = ()) -> None:
    unchecked = [entry[2:] for entry in _git_files(root, "ls-files", "-v", "-z", "--cached",
                                                "--", *(scope or (".",)))
                 if entry[0].islower() or entry.startswith("S ")]
    if unchecked:
        raise GateError("Git diff modes cannot verify assume-unchanged or skip-worktree entries: "
                        f"{_examples(unchecked)}; use a clean disposable checkout or "
                        "repository mode without either diff option")


def _check_diff_checkout(spec: InventorySpec) -> None:
    head = _git_files(spec.root, "rev-parse", "--verify", "HEAD")[0].strip()
    if head != spec.head:
        raise GateError("committed diff needs a checkout of its recorded head; use a disposable checkout")

    _require_checked_index(spec.root)
    dirty, _ = _git(spec.root, "diff", "--quiet", "--no-ext-diff", "--no-textconv", "HEAD", "--", ".",
                    accept=(0, 1))
    untracked = _git_files(spec.root, "ls-files", "-z", "--others", "--exclude-standard", "--", ".")
    if dirty or untracked:
        raise GateError("committed diff needs a clean target, including supporting code; "
                        "use a clean disposable checkout or --working-tree")


def derive_inventory(spec: InventorySpec) -> InventoryListing:
    """List the in-scope files for `spec`; backs both `inventory` and `check`."""
    if not spec.root.is_dir():
        raise GateError(f"target {spec.root} is not a directory")
    for path in spec.scope:
        _inventory_path(spec.root, path)
    if spec.mode != "diff":
        missing = [path for path in spec.scope if not os.path.lexists(spec.root / path)]
        if missing:
            raise GateError(f"--scope paths do not exist under {spec.root}: {_examples(missing)}")
    pathspec = ["--", *(spec.scope or (".",))]
    deleted: list[str] = []
    revision = None

    if not _is_git_work_tree(spec.root):
        if spec.mode != "repository":
            raise GateError(f"{spec.mode} mode needs a git work tree; {spec.root} is not one")
        source, files = "filesystem", _walk_files(spec.root, spec.scope)
    elif spec.mode == "repository":
        source = "git"
        listed = _git_files(spec.root, "ls-files", "-z", "--cached", "--others", "--exclude-standard", *pathspec)
        # Drop worktree-deleted entries and submodule directories; keep symlinks as entries.
        files = [path for path in listed if os.path.lexists(spec.root / path)
                 and not ((spec.root / path).is_dir() and not (spec.root / path).is_symlink())]
    else:
        source = "git"
        if spec.mode == "diff":
            _check_diff_checkout(spec)
        else:
            _require_checked_index(spec.root, spec.scope)
            revision = _git_files(spec.root, "rev-parse", "--verify", "HEAD")[0].strip()
        diff = ["diff", "--name-only", "-z", "--no-renames", "--relative", "--no-ext-diff", "--no-textconv"]
        revisions = [f"{spec.base}...{spec.head}"] if spec.mode == "diff" else [revision or "HEAD"]
        files = _git_files(spec.root, *diff, *revisions, *pathspec)
        deleted = _git_files(spec.root, *diff, "--diff-filter=D", *revisions, *pathspec)
        if spec.mode == "working-tree":
            files += _git_files(spec.root, "ls-files", "-z", "--others", "--exclude-standard", *pathspec)

    kept = sorted({path for path in files if not _is_excluded(path, spec.exclude)})
    removed = set(deleted) & set(kept)
    if spec.mode == "working-tree":
        removed = {path for path in removed if not os.path.lexists(_inventory_path(spec.root, path))}
    return InventoryListing(source=source, files=kept, deleted=sorted(removed),
                            snapshot_digest=_snapshot_digest(spec, kept, removed, revision))


def run_inventory(args: argparse.Namespace) -> int:
    root = Path(args.target).resolve()
    scan_dir = Path(args.scan_dir).resolve()
    if scan_dir.is_relative_to(root):
        raise GateError(f"the scan directory must be outside the read-only target {root}; use a sibling directory")

    exclude = {_relative_path(prefix, "--exclude") for prefix in args.exclude}
    scope = tuple(sorted({_relative_path(path, "--scope") for path in args.scope} - {""}))

    mode, base, head = "repository", None, None
    if args.diff:
        mode = "diff"
        # Record commits, not refs, so `check` re-derives the diff that was reviewed.
        base, head = (_git_files(root, "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}")[0].strip()
                      for revision in args.diff)
    elif args.working_tree:
        mode = "working-tree"
    spec = InventorySpec(root=root, mode=mode, scope=scope, exclude=tuple(sorted(exclude - {""})),
                         base=base, head=head)

    document = spec.document(scan_dir, derive_inventory(spec))
    scan_dir.mkdir(parents=True, exist_ok=True)
    target = scan_dir / "inventory.json"
    partial = target.with_suffix(".json.partial")
    partial.write_text(json.dumps(document, indent=1) + "\n", encoding="utf-8")
    os.replace(partial, target)
    print(f"inventory: {len(document['files'])} files ({document['source']}, {mode}) -> {target}")
    return 0


# ---------------------------------------------------------------------------
# Completion gate

def _load_state(scan_dir: Path) -> tuple[ScanDocuments | None, str | None, list[str]]:
    """Parse and schema-check every state file; documents are returned only when all are valid."""
    raw: dict[str, Json] = {}
    problems: list[str] = []
    for file_name, schema_name in STATE_FILES:
        try:
            document = json.loads((scan_dir / file_name).read_text(encoding="utf-8"))
        except FileNotFoundError:
            problems.append(f"{file_name}: missing")
            continue
        except (OSError, ValueError) as error:
            problems.append(f"{file_name}: unreadable: {error}")
            continue

        errors = _load_schema(schema_name).validate(document)
        problems += [f"{file_name}: {error}" for error in errors[:SCHEMA_ERROR_LIMIT]]
        if len(errors) > SCHEMA_ERROR_LIMIT:
            problems.append(f"{file_name}: ... {len(errors) - SCHEMA_ERROR_LIMIT} more schema errors")
        raw[file_name] = document

    state = raw.get("scan-state.json")
    status = state.get("status") if isinstance(state, dict) else None
    if problems:
        return None, cast("str | None", status), problems

    # Every file passed its schema above, so each cast narrows JSON to the shape the schema guarantees.
    documents = ScanDocuments(
        inventory=cast(InventoryDoc, raw["inventory.json"]),
        coverage=cast(CoverageDoc, raw["coverage.json"]),
        candidates=cast(list[Candidate], raw["candidates.json"]),
        findings=cast(FindingsDoc, raw["findings.json"]),
        state=cast(ScanStateDoc, raw["scan-state.json"]),
    )
    return documents, documents.state.get("status"), problems


def _check_inventory(inventory: InventoryDoc, scan_dir: Path) -> list[str]:
    try:
        current = derive_inventory(InventorySpec.recorded(inventory, scan_dir))
    except GateError as error:
        return [f"inventory.json: cannot re-derive: {error}"]

    problems = []
    pairs = (("files", inventory["files"], current["files"]), ("deleted", inventory["deleted"], current["deleted"]))
    for key, recorded_list, current_list in pairs:
        recorded, now = set(recorded_list), set(current_list)
        if recorded != now:
            problems.append(f"inventory.json: stale {key}: +{len(now - recorded)} [{_examples(now - recorded)}] "
                            f"-{len(recorded - now)} [{_examples(recorded - now)}]; "
                            "rerun `inventory` and re-disposition")
    if inventory["snapshot_digest"] != current["snapshot_digest"]:
        problems.append("inventory.json: source snapshot changed; rerun `inventory` and revalidate coverage")
    return problems


def _check_coverage(coverage: CoverageDoc, inventory: InventoryDoc) -> list[str]:
    problems = []
    if coverage["snapshot_digest"] != inventory["snapshot_digest"]:
        problems.append("coverage.json: snapshot_digest does not match inventory; "
                        "revalidate receipts before attesting to the new snapshot")
    receipts = coverage["reviewed_files"]
    paths = [receipt["path"] for receipt in receipts]
    inventoried = set(inventory["files"])

    if _duplicates(paths):
        problems.append(f"coverage.json: several receipts for {_examples(_duplicates(paths))}")
    missing = inventoried - set(paths)
    if missing:
        problems.append(f"coverage.json: {len(missing)} inventoried files have no receipt: {_examples(missing)}")
    extra = set(paths) - inventoried
    if extra:
        problems.append(f"coverage.json: {len(extra)} receipts name files outside the inventory "
                        f"(supporting code goes in supporting_files): {_examples(extra)}")

    deferred = {receipt["path"] for receipt in receipts if receipt["disposition"] == "deferred"}
    if deferred:
        problems.append(f"coverage.json: {len(deferred)} files still deferred: {_examples(deferred)}")
    both = {entry["path"] for entry in coverage["supporting_files"]} & inventoried
    if both:
        problems.append(f"coverage.json: inventoried files listed as supporting_files: {_examples(both)}")
    return problems


def _candidate_state(candidate: Candidate) -> str:
    validation = candidate["validation"]["disposition"]
    decision = candidate["attack_path"]["decision"]
    if "deferred" in (validation, decision):
        return "deferred"
    if validation == "reportable" and decision == "reportable":
        return "reportable"
    return "rejected"


def _check_candidates(candidates: list[Candidate], coverage: CoverageDoc) -> list[str]:
    problems = []
    ids = [candidate["id"] for candidate in candidates]
    if _duplicates(ids):
        problems.append(f"candidates.json: duplicate ids {_examples(_duplicates(ids))}")

    for candidate in candidates:
        validation, attack_path = candidate["validation"], candidate["attack_path"]
        if validation["disposition"] in ("suppressed", "not_applicable") and attack_path["decision"] != "ignore":
            problems.append(f"candidates.json: {candidate['id']}: validation is {validation['disposition']} "
                            f"but attack_path decision is {attack_path['decision']} (must be ignore)")
        expected = {"reportable": "yes", "suppressed": "no", "not_applicable": "no"}.get(validation["disposition"])
        if expected and validation["survives"] != expected:
            problems.append(f"candidates.json: {candidate['id']}: validation {validation['disposition']} "
                            f"needs survives={expected}, got {validation['survives']}")

    states = {candidate["id"]: _candidate_state(candidate) for candidate in candidates}
    linked = {entry["candidate"] for entry in coverage["unresolvable"] if "candidate" in entry}
    unlinked = {cid for cid, state in states.items() if state == "deferred"} - linked
    if unlinked:
        problems.append(f"candidates.json: deferred candidates without a coverage.unresolvable record: "
                        f"{_examples(unlinked)}")
    wrong_links = {cid for cid in linked if states.get(cid) != "deferred"}
    if wrong_links:
        problems.append(f"coverage.json: unresolvable records name candidates that are missing or not deferred: "
                        f"{_examples(wrong_links)}")
    return problems


def _check_finding(finding: Finding, candidate: Candidate | None) -> list[str]:
    label = f"findings.json: {finding['id']}"
    problems = []
    evidence_ids = [item["id"] for item in finding["codeEvidence"]]
    if _duplicates(evidence_ids):
        problems.append(f"{label}: duplicate codeEvidence ids {_examples(_duplicates(evidence_ids))}")

    attack_path = finding["attackPath"]
    references = [*finding["rootCause"]["evidenceRefs"], *finding["validation"]["evidenceRefs"],
                  *attack_path["dataflow"]["evidenceRefs"]]
    dangling = set(references) - set(evidence_ids)
    if dangling:
        problems.append(f"{label}: evidenceRefs not in codeEvidence: {_examples(dangling)}")

    impact, likelihood = attack_path["impact"]["level"], attack_path["likelihood"]["level"]
    allowed = SEVERITY_MATRIX[impact][likelihood]
    if allowed == ("ignore",):
        problems.append(f"{label}: impact {impact} x likelihood {likelihood} is ignore; move it to non_findings")
    elif finding["severity"] not in allowed:
        problems.append(f"{label}: severity {finding['severity']} but impact {impact} x likelihood "
                        f"{likelihood} gives {' or '.join(allowed)}")

    if candidate is not None and candidate["attack_path"].get("severity") != finding["severity"]:
        problems.append(f"{label}: severity {finding['severity']} differs from its candidate receipt "
                        f"({candidate['attack_path'].get('severity')})")
    return problems


def _check_findings(findings: FindingsDoc, candidates: list[Candidate]) -> list[str]:
    problems = []
    by_id = {candidate["id"]: candidate for candidate in candidates}
    states = {cid: _candidate_state(candidate) for cid, candidate in by_id.items()}
    reported = [finding["id"] for finding in findings["findings"]]
    rejected = [entry["id"] for entry in findings["non_findings"]]

    if _duplicates(reported + rejected):
        problems.append(f"findings.json: ids appear more than once: {_examples(_duplicates(reported + rejected))}")
    for ids, state, field_name in ((reported, "reportable", "findings"), (rejected, "rejected", "non_findings")):
        unknown = set(ids) - set(by_id)
        if unknown:
            problems.append(f"findings.json: {field_name} without candidate receipts: {_examples(unknown)}")
        mismatched = {cid for cid in ids if cid in states and states[cid] != state}
        if mismatched:
            problems.append(f"findings.json: {field_name} whose candidate receipts are not {state}: "
                            f"{_examples(mismatched)}")
        absent = {cid for cid, actual in states.items() if actual == state} - set(ids)
        if absent:
            problems.append(f"findings.json: {state} candidates missing from {field_name}: {_examples(absent)}")

    for finding in findings["findings"]:
        problems += _check_finding(finding, by_id.get(finding["id"]))
    return problems


def _check_convergence(state: ScanStateDoc, findings: FindingsDoc) -> list[str]:
    problems = []
    history = state["history"]
    if not history:
        return ["scan-state.json: no completed pass in history"]

    numbers = [entry["pass"] for entry in history]
    if numbers != list(range(1, len(history) + 1)):
        problems.append(f"scan-state.json: history passes must be numbered 1..{len(history)} in order, got {numbers}")
    repeats = [entry["pass"] for previous, entry in zip(history, history[1:]) if previous["lens"] == entry["lens"]]
    if repeats:
        problems.append(f"scan-state.json: lens repeated consecutively at passes {repeats}")
    if findings["passes"] != len(history):
        problems.append(f"findings.json: passes is {findings['passes']} but history records {len(history)}")
    if history[-1]["new_findings"] or history[-1]["new_questions"]:
        problems.append("scan-state.json: the final pass must add zero findings and zero questions/gaps")

    if state["gaps"]:
        problems.append(f"scan-state.json: {len(state['gaps'])} open gaps: "
                        f"{_examples(gap['id'] for gap in state['gaps'])}")
    last_finding_pass = max((entry["pass"] for entry in history if entry["new_findings"] > 0), default=0)
    lenses_since = {entry["lens"] for entry in history if entry["pass"] > last_finding_pass}
    for lens in REQUIRED_LENSES:
        if lens not in lenses_since:
            problems.append(f"scan-state.json: no {lens} pass after pass {last_finding_pass}, "
                            "the last pass that added findings")
    return problems


def run_check(args: argparse.Namespace) -> int:
    scan_dir = Path(args.scan_dir).resolve()
    documents, status, problems = _load_state(scan_dir)

    if documents is not None:
        problems += _check_inventory(documents.inventory, scan_dir)
        problems += _check_coverage(documents.coverage, documents.inventory)
        problems += _check_candidates(documents.candidates, documents.coverage)
        problems += _check_findings(documents.findings, documents.candidates)
        problems += _check_convergence(documents.state, documents.findings)
    else:
        problems.append("cross-file rules were not evaluated; fix the schema problems first")

    if problems or documents is None:
        if status == "completed":
            problems.append("scan-state.json: status is completed while the gate fails")
        print("\n".join(problems))
        return 1
    print(f"gate passes: {documents.summary()}; status {status or 'unset'}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)

    inventory = commands.add_parser("inventory", help="write <scan-dir>/inventory.json")
    inventory.add_argument("target")
    inventory.add_argument("scan_dir")
    revisions = inventory.add_mutually_exclusive_group()
    revisions.add_argument("--diff", nargs=2, metavar=("BASE", "HEAD"), help="changed files of BASE...HEAD")
    revisions.add_argument("--working-tree", action="store_true", help="uncommitted and untracked changes")
    inventory.add_argument("--scope", action="append", default=[], metavar="PATH",
                           help="in-scope path relative to the target (repeatable; default: all)")
    inventory.add_argument("--exclude", action="append", default=[], metavar="PREFIX",
                           help="path prefix outside the scan scope (repeatable)")
    inventory.set_defaults(run=run_inventory)

    check = commands.add_parser("check", help="gate scan completion")
    check.add_argument("scan_dir")
    check.set_defaults(run=run_check)

    args = parser.parse_args(argv[1:])
    try:
        return args.run(args)
    except GateError as error:
        print(f"scan-gate: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
