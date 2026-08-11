#!/usr/bin/env python3
"""Initialize or migrate a durable-knowledge vault without modifying knowledge notes."""

import argparse
import shutil
import sys
from pathlib import Path

_CONTROL_DIRECTORY = Path("_durable-knowledge")
_LEGACY_CONTROL_DIRECTORY = Path(".llm-wiki")
_MARKER_NAME = "ROOT.md"
_LEGACY_MARKER_NAME = "ROOT"
_MARKER_CONTENT = "durable-knowledge-vault-v1\n"
_DIRECTORIES = (
    Path("Knowledge/Candidates"),
    Path("Knowledge/Papers"),
    Path("Knowledge/Canonical"),
    Path("Knowledge/Artifacts"),
    _CONTROL_DIRECTORY / "Proposals",
    _CONTROL_DIRECTORY / "templates",
)

KNOWLEDGE_README = """# Knowledge

This subtree is managed by the `durable-knowledge` Agent Skill.

- `Candidates/`: captured claims with human-readable review status.
- `Papers/`: grounded notes about individual academic papers.
- `Canonical/`: reviewed semantic owners.
- `Artifacts/`: immutable content-addressed evidence snapshots referenced by managed records.
- `knowledge-browser.base`: optional Obsidian browser for candidates, papers, and canonical knowledge.
- `candidate-review.base`: optional Obsidian view over candidate status, review rationale, and topic properties.

Candidate review is file-based: set `status` to `ready`, `deferred`, or `rejected`, record a
substantive `review_reason` for deferred or rejected candidates, and maintain optional
`topic/<lowercase-kebab-case>` tags in Obsidian or any Markdown editor. Agents integrate only `ready`
candidates. An explicit request to integrate a named non-applied candidate first moves it to `ready`
in the same operation.

Desktop and headless clients may sync separate local replicas of this vault. Markdown and YAML remain
authoritative, and existing notes elsewhere in the vault remain human-owned by default.
"""

RUNTIME_README = """# _durable-knowledge

Operational files for the `durable-knowledge` skill.

This directory is intentionally visible because Obsidian Sync excludes dot-prefixed directories
other than its configuration directory.

- `ROOT.md`: Markdown marker used to resolve the vault safely and sync without extra file-type settings.
- `POLICY.md`: optional vault-owned admission and routing policy within the fixed record model.
- `Proposals/`: optional review artifacts for delayed or high-risk canonical changes.
- `templates/`: optional vault-owned template overrides.
"""


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


class _MigrationConflictError(RuntimeError):
    pass


def _ensure_managed_directory(vault: Path, relative: Path) -> bool:
    current = vault
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise _MigrationConflictError(
                "managed directory path must not contain symlinks"
            )
        if current.exists() and not current.is_dir():
            raise _MigrationConflictError(
                f"managed directory path is not a directory: {current.relative_to(vault)}"
            )

    path = vault / relative
    existed = path.exists()
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.resolve().relative_to(vault)
    except ValueError as error:
        raise _MigrationConflictError(
            "managed directory path escapes the vault"
        ) from error
    return not existed


def _migrate_legacy_control_directory(vault: Path) -> None:
    legacy = vault / _LEGACY_CONTROL_DIRECTORY
    control = vault / _CONTROL_DIRECTORY
    if not legacy.exists():
        return
    if control.exists():
        raise _MigrationConflictError(
            "both .llm-wiki and _durable-knowledge exist; reconcile their contents "
            "manually before running bootstrap"
        )

    legacy.rename(control)


def _migrate_legacy_marker(vault: Path) -> None:
    control = vault / _CONTROL_DIRECTORY
    legacy_marker = control / _LEGACY_MARKER_NAME
    marker = control / _MARKER_NAME
    if marker.exists() and not marker.is_file():
        raise _MigrationConflictError(
            "_durable-knowledge/ROOT.md is not a regular marker file; reconcile it manually"
        )
    if not legacy_marker.exists():
        return
    if not legacy_marker.is_file():
        raise _MigrationConflictError(
            "_durable-knowledge/ROOT is not a regular marker file; reconcile it manually"
        )
    if marker.exists():
        if not marker.is_file() or legacy_marker.read_bytes() != marker.read_bytes():
            raise _MigrationConflictError(
                "_durable-knowledge/ROOT and ROOT.md marker files differ; reconcile them manually"
            )
        legacy_marker.unlink()
        return

    legacy_marker.rename(marker)


def bootstrap(vault: Path, install_policy_copy: bool) -> list[Path]:
    vault = vault.expanduser().resolve()
    vault.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    skill_root = Path(__file__).resolve().parent.parent
    _migrate_legacy_control_directory(vault)
    _migrate_legacy_marker(vault)

    for relative in _DIRECTORIES:
        path = vault / relative
        if _ensure_managed_directory(vault, relative):
            created.append(path)

    marker = vault / _CONTROL_DIRECTORY / _MARKER_NAME
    if write_if_missing(marker, _MARKER_CONTENT):
        created.append(marker)

    knowledge_readme = vault / "Knowledge/README.md"
    if write_if_missing(knowledge_readme, KNOWLEDGE_README):
        created.append(knowledge_readme)

    runtime_readme = vault / _CONTROL_DIRECTORY / "README.md"
    if write_if_missing(runtime_readme, RUNTIME_README):
        created.append(runtime_readme)

    for base_name in ("knowledge-browser.base", "candidate-review.base"):
        base_source = skill_root / "assets" / base_name
        base_destination = vault / "Knowledge" / base_name
        if not base_destination.exists():
            shutil.copyfile(base_source, base_destination)
            created.append(base_destination)

    if install_policy_copy:
        source = skill_root / "references/reference/admission-policy.md"
        destination = vault / _CONTROL_DIRECTORY / "POLICY.md"
        if not destination.exists():
            shutil.copyfile(source, destination)
            created.append(destination)

    return created


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vault", type=Path, required=True, help="Target Obsidian/Markdown vault"
    )
    parser.add_argument(
        "--install-policy-copy",
        action="store_true",
        help="Copy the bundled admission policy into _durable-knowledge/POLICY.md if absent",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    vault = args.vault.expanduser().resolve()
    migrated_legacy_control_directory = (
        vault / _LEGACY_CONTROL_DIRECTORY
    ).exists() and not (vault / _CONTROL_DIRECTORY).exists()
    legacy_marker_was_present = any(
        (vault / directory / _LEGACY_MARKER_NAME).exists()
        for directory in (_LEGACY_CONTROL_DIRECTORY, _CONTROL_DIRECTORY)
    )
    try:
        created = bootstrap(vault, args.install_policy_copy)
    except _MigrationConflictError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Vault: {vault}")
    migrated_legacy_marker = (
        legacy_marker_was_present
        and not (vault / _LEGACY_CONTROL_DIRECTORY / _LEGACY_MARKER_NAME).exists()
        and not (vault / _CONTROL_DIRECTORY / _LEGACY_MARKER_NAME).exists()
        and (vault / _CONTROL_DIRECTORY / _MARKER_NAME).is_file()
    )

    if migrated_legacy_control_directory:
        print("Migrated: .llm-wiki -> _durable-knowledge")
    if migrated_legacy_marker:
        print("Migrated: _durable-knowledge/ROOT -> _durable-knowledge/ROOT.md")
    if created:
        print("Created:")
        for path in created:
            print(f"  - {path.relative_to(vault)}")
    elif not migrated_legacy_control_directory and not migrated_legacy_marker:
        print("No changes; the vault structure already exists.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
