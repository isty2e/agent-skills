#!/usr/bin/env python3
"""Validate durable-knowledge Markdown records using only the Python standard library."""

import argparse
import json
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path

_TOP_LEVEL_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?$")
_LOWER_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

_SCALAR_FIELDS: dict[str, frozenset[str]] = {
    "candidate": frozenset(
        {
            "id",
            "record_type",
            "knowledge_kind",
            "status",
            "evidence_state",
            "canonical_id",
            "created",
            "updated",
        }
    ),
    "paper": frozenset(
        {
            "id",
            "record_type",
            "status",
            "citation_key",
            "source_ref",
            "created",
            "updated",
        }
    ),
    "canonical": frozenset(
        {
            "id",
            "record_type",
            "knowledge_kind",
            "lifecycle",
            "evidence_state",
            "created",
            "updated",
        }
    ),
    "proposal": frozenset(
        {
            "id",
            "record_type",
            "decision",
            "target_id",
            "target_path",
            "base_sha256",
            "created",
        }
    ),
}

_NON_EMPTY_SCALAR_FIELDS: dict[str, frozenset[str]] = {
    "candidate": frozenset(
        {
            "id",
            "record_type",
            "knowledge_kind",
            "status",
            "evidence_state",
            "created",
            "updated",
        }
    ),
    "paper": _SCALAR_FIELDS["paper"],
    "canonical": _SCALAR_FIELDS["canonical"],
    "proposal": frozenset({"id", "record_type", "decision", "created"}),
}

_SEQUENCE_FIELDS: dict[str, frozenset[str]] = {
    "candidate": frozenset(
        {"scope", "assumptions", "invalidation_conditions", "source_refs"}
    ),
    "paper": frozenset(),
    "canonical": frozenset(
        {"scope", "assumptions", "invalidation_conditions", "source_refs"}
    ),
    "proposal": frozenset({"candidate_ids", "source_refs"}),
}

_OPTIONAL_SEQUENCE_FIELDS: dict[str, frozenset[str]] = {
    "canonical": frozenset({"aliases"}),
}

_NON_EMPTY_SEQUENCE_FIELDS: dict[str, frozenset[str]] = {
    "candidate": _SEQUENCE_FIELDS["candidate"],
    "canonical": _SEQUENCE_FIELDS["canonical"],
    "proposal": frozenset({"source_refs"}),
}

_ALLOWED: dict[str, frozenset[str]] = {
    "knowledge_kind": frozenset(
        {
            "mechanism",
            "constraint",
            "method",
            "decision-rule",
            "distinction",
            "synthesis",
            "hypothesis",
        }
    ),
    "evidence_state": frozenset(
        {
            "unverified",
            "observed",
            "source-backed",
            "corroborated",
            "contested",
        }
    ),
    "lifecycle": frozenset(
        {"provisional", "reviewed", "stable", "contested", "retired"}
    ),
    "decision": frozenset({"create", "merge", "conflict", "reject", "defer", "retire"}),
}

_EXPECTED_ROOT: dict[str, Path] = {
    "candidate": Path("Knowledge/Candidates"),
    "paper": Path("Knowledge/Papers"),
    "canonical": Path("Knowledge/Canonical"),
    "proposal": Path(".llm-wiki/Proposals"),
}


@dataclass(frozen=True)
class Finding:
    severity: str
    path: str
    message: str


def strip_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(
    path: Path,
) -> tuple[dict[str, str | tuple[str, ...]], list[Finding]]:
    """Parse the supported top-level frontmatter subset.

    Parameters
    ----------
    path : Path
        Markdown record to parse.

    Returns
    -------
    tuple[dict[str, str | tuple[str, ...]], list[Finding]]
        Top-level scalar and flat-sequence values plus parsing findings.
    """
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {}, [Finding("error", str(path), "file is not valid UTF-8")]

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, [
            Finding("error", str(path), "missing opening YAML frontmatter delimiter")
        ]

    try:
        end = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration:
        return {}, [
            Finding("error", str(path), "missing closing YAML frontmatter delimiter")
        ]

    parsed: dict[str, str | list[str]] = {}
    current_sequence_key: str | None = None
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if line[0].isspace():
            if current_sequence_key is None or not stripped.startswith("-"):
                current_sequence_key = None
                continue

            current_value = parsed[current_sequence_key]
            if isinstance(current_value, str):
                current_value = []
                parsed[current_sequence_key] = current_value
            item = stripped[1:].strip()
            current_value.append("" if item.startswith("#") else strip_scalar(item))
            continue

        current_sequence_key = None
        match = _TOP_LEVEL_KEY.match(line)
        if match is None:
            continue

        key = match.group(1)
        if key in parsed:
            findings.append(
                Finding("error", str(path), f"duplicate top-level field: {key}")
            )
            continue

        raw_value = match.group(2) or ""
        if raw_value.strip() == "[]":
            parsed[key] = []
        else:
            parsed[key] = strip_scalar(raw_value)
            if not raw_value:
                current_sequence_key = key

    fields = {
        key: tuple(value) if isinstance(value, list) else value
        for key, value in parsed.items()
    }
    if not fields:
        findings.append(
            Finding("error", str(path), "frontmatter has no top-level fields")
        )
    return fields, findings


def _scalar_field(fields: Mapping[str, str | tuple[str, ...]], key: str) -> str:
    value = fields.get(key, "")
    return value if isinstance(value, str) else ""


def is_under(relative: Path, root: Path) -> bool:
    try:
        relative.relative_to(root)
        return True
    except ValueError:
        return False


def validate_file(
    vault: Path, path: Path
) -> tuple[dict[str, str | tuple[str, ...]], list[Finding]]:
    """Validate one managed Markdown record.

    Parameters
    ----------
    vault : Path
        Root of the resolved durable-knowledge vault.
    path : Path
        Managed Markdown record under the vault.

    Returns
    -------
    tuple[dict[str, str | tuple[str, ...]], list[Finding]]
        Parsed top-level frontmatter and structural findings.
    """
    relative = path.relative_to(vault)
    fields, findings = parse_frontmatter(path)
    if not fields:
        return {}, findings

    record_type = _scalar_field(fields, "record_type")
    if "record_type" in fields and not isinstance(fields["record_type"], str):
        findings.append(
            Finding("error", str(relative), "field record_type must be a scalar")
        )
        return fields, findings

    if record_type not in _SCALAR_FIELDS:
        findings.append(
            Finding(
                "error",
                str(relative),
                f"unknown or missing record_type: {record_type!r}",
            )
        )
        return fields, findings

    required_fields = _SCALAR_FIELDS[record_type] | _SEQUENCE_FIELDS[record_type]
    missing = sorted(required_fields - fields.keys())
    if missing:
        findings.append(
            Finding(
                "error", str(relative), f"missing required fields: {', '.join(missing)}"
            )
        )

    expected_sequence_fields = _SEQUENCE_FIELDS[
        record_type
    ] | _OPTIONAL_SEQUENCE_FIELDS.get(record_type, frozenset())
    wrong_scalar_types = sorted(
        key
        for key in _SCALAR_FIELDS[record_type]
        if key in fields and not isinstance(fields[key], str)
    )
    wrong_sequence_types = sorted(
        key
        for key in expected_sequence_fields
        if key in fields and not isinstance(fields[key], tuple)
    )
    if wrong_scalar_types:
        findings.append(
            Finding(
                "error",
                str(relative),
                f"fields must be scalars: {', '.join(wrong_scalar_types)}",
            )
        )
    if wrong_sequence_types:
        findings.append(
            Finding(
                "error",
                str(relative),
                f"fields must be flat sequences: {', '.join(wrong_sequence_types)}",
            )
        )

    empty_scalars = sorted(
        key
        for key in _NON_EMPTY_SCALAR_FIELDS[record_type]
        if key in fields
        and isinstance(fields[key], str)
        and (not fields[key] or "<" in fields[key] or ">" in fields[key])
    )
    if empty_scalars:
        findings.append(
            Finding(
                "error",
                str(relative),
                f"required scalar fields are empty or contain placeholders: {', '.join(empty_scalars)}",
            )
        )

    empty_sequences = sorted(
        key
        for key in _NON_EMPTY_SEQUENCE_FIELDS.get(record_type, frozenset())
        if key in fields and isinstance(fields[key], tuple) and not fields[key]
    )
    if empty_sequences:
        findings.append(
            Finding(
                "error",
                str(relative),
                f"required sequence fields are empty: {', '.join(empty_sequences)}",
            )
        )

    placeholder_sequences = sorted(
        key
        for key in expected_sequence_fields
        if key in fields
        and isinstance(fields[key], tuple)
        and any(not item or "<" in item or ">" in item for item in fields[key])
    )
    if placeholder_sequences:
        findings.append(
            Finding(
                "error",
                str(relative),
                "sequence fields contain empty or placeholder items: "
                + ", ".join(placeholder_sequences),
            )
        )

    expected_root = _EXPECTED_ROOT[record_type]
    if not is_under(relative, expected_root):
        findings.append(
            Finding(
                "error",
                str(relative),
                f"record_type {record_type!r} must live under {expected_root}",
            )
        )

    filename = path.stem
    if not _LOWER_KEBAB.fullmatch(filename):
        findings.append(
            Finding("warning", str(relative), "filename should be lowercase kebab-case")
        )

    record_id = _scalar_field(fields, "id")
    if not record_id or "<" in record_id or ">" in record_id:
        findings.append(
            Finding(
                "error", str(relative), "id is empty or still contains placeholders"
            )
        )
    elif not _LOWER_KEBAB.fullmatch(record_id):
        findings.append(
            Finding("warning", str(relative), "id should be lowercase kebab-case")
        )

    for key, allowed in _ALLOWED.items():
        value = _scalar_field(fields, key)
        if value and value not in allowed:
            findings.append(
                Finding(
                    "error",
                    str(relative),
                    f"invalid {key}: {value!r}; expected one of {sorted(allowed)}",
                )
            )

    if record_type == "candidate":
        status = _scalar_field(fields, "status")
        candidate_statuses = {
            "pending",
            "ready",
            "deferred",
            "rejected",
            "integrated",
            "contested",
        }
        if status not in candidate_statuses:
            findings.append(
                Finding(
                    "error",
                    str(relative),
                    f"invalid candidate status: {status!r}; expected one of {sorted(candidate_statuses)}",
                )
            )

        deprecated_fields = sorted(
            {"resolution_ref", "resolved_at"}.intersection(fields)
        )
        if deprecated_fields:
            findings.append(
                Finding(
                    "error",
                    str(relative),
                    f"candidate uses deprecated fields: {', '.join(deprecated_fields)}; use canonical_id",
                )
            )

        canonical_id = _scalar_field(fields, "canonical_id")
        null_values = {"", "null", "~"}
        if status in {"pending", "ready", "deferred", "rejected"}:
            if canonical_id not in null_values:
                findings.append(
                    Finding(
                        "error",
                        str(relative),
                        f"candidate status {status!r} requires null canonical_id",
                    )
                )
        elif status in {"integrated", "contested"}:
            if (
                canonical_id in null_values
                or "<" in canonical_id
                or ">" in canonical_id
            ):
                findings.append(
                    Finding(
                        "error",
                        str(relative),
                        f"candidate status {status!r} requires canonical_id",
                    )
                )
            elif not _LOWER_KEBAB.fullmatch(canonical_id):
                findings.append(
                    Finding(
                        "error",
                        str(relative),
                        "candidate canonical_id must be lowercase kebab-case",
                    )
                )
    if record_type == "paper" and _scalar_field(fields, "status") != "source":
        findings.append(
            Finding("error", str(relative), "paper status must be 'source'")
        )

    if record_type == "proposal":
        base_sha = _scalar_field(fields, "base_sha256")
        decision = _scalar_field(fields, "decision")
        if decision in {"create", "reject", "defer"}:
            if base_sha not in {"", "null", "~"}:
                findings.append(
                    Finding(
                        "warning",
                        str(relative),
                        f"{decision} proposal normally has null base_sha256",
                    )
                )
        elif base_sha in {"", "null", "~"} or not _SHA256.fullmatch(base_sha):
            findings.append(
                Finding(
                    "error",
                    str(relative),
                    "non-create proposal requires a 64-hex base_sha256",
                )
            )

    if (
        record_type == "canonical"
        and _scalar_field(fields, "lifecycle") == "stable"
        and _scalar_field(fields, "evidence_state") in {"unverified", "observed"}
    ):
        findings.append(
            Finding(
                "warning",
                str(relative),
                "stable lifecycle with weak evidence state requires explicit review",
            )
        )

    return fields, findings


def iter_managed_markdown(vault: Path) -> list[Path]:
    roots = tuple(_EXPECTED_ROOT.values())
    paths: list[Path] = []
    for root in roots:
        directory = vault / root
        if directory.exists():
            paths.extend(path for path in directory.rglob("*.md") if path.is_file())
    return sorted(set(paths))


def validate_vault(vault: Path) -> list[Finding]:
    findings: list[Finding] = []
    marker = vault / ".llm-wiki/ROOT"
    if not marker.exists():
        findings.append(Finding("error", ".llm-wiki/ROOT", "vault marker is missing"))

    ids: dict[str, list[str]] = {}
    records: list[tuple[Path, dict[str, str | tuple[str, ...]]]] = []
    for path in iter_managed_markdown(vault):
        fields, file_findings = validate_file(vault, path)
        findings.extend(file_findings)
        records.append((path, fields))
        record_id = _scalar_field(fields, "id")
        if record_id:
            ids.setdefault(record_id, []).append(str(path.relative_to(vault)))

    for record_id, paths in sorted(ids.items()):
        if len(paths) > 1:
            findings.append(
                Finding("error", ", ".join(paths), f"duplicate id {record_id!r}")
            )

    canonical_records: dict[str, dict[str, str | tuple[str, ...]]] = {}
    for _, fields in records:
        if _scalar_field(fields, "record_type") != "canonical":
            continue
        canonical_id = _scalar_field(fields, "id")
        if canonical_id:
            canonical_records[canonical_id] = fields

    for path, fields in records:
        status = _scalar_field(fields, "status")
        if _scalar_field(fields, "record_type") != "candidate" or status not in {
            "integrated",
            "contested",
        }:
            continue

        canonical_id = _scalar_field(fields, "canonical_id")
        canonical = canonical_records.get(canonical_id)
        relative = str(path.relative_to(vault))
        if canonical is None:
            findings.append(
                Finding(
                    "error",
                    relative,
                    f"candidate canonical_id does not identify an existing canonical record: {canonical_id!r}",
                )
            )
            continue

        if status == "contested" and not (
            _scalar_field(canonical, "lifecycle") == "contested"
            or _scalar_field(canonical, "evidence_state") == "contested"
        ):
            findings.append(
                Finding(
                    "error",
                    relative,
                    "contested candidate must reference a canonical record that preserves the conflict",
                )
            )
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, required=True, help="Target vault")
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    vault = args.vault.expanduser().resolve()
    findings = validate_vault(vault)

    if args.json:
        payload = {
            "vault": str(vault),
            "findings": [asdict(finding) for finding in findings],
            "errors": sum(finding.severity == "error" for finding in findings),
            "warnings": sum(finding.severity == "warning" for finding in findings),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif findings:
        for finding in findings:
            print(f"{finding.severity.upper():7} {finding.path}: {finding.message}")
    else:
        print(f"PASS {vault}")

    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
