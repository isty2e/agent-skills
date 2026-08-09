#!/usr/bin/env python3
"""Initialize a durable-knowledge vault without modifying existing notes."""

import argparse
import shutil
from pathlib import Path

_DIRECTORIES = (
    Path("Knowledge/Candidates"),
    Path("Knowledge/Papers"),
    Path("Knowledge/Canonical"),
    Path(".llm-wiki/Proposals"),
    Path(".llm-wiki/templates"),
)

KNOWLEDGE_README = """# Knowledge

This subtree is managed by the `durable-knowledge` Agent Skill.

- `Candidates/`: captured claims with human-readable review status.
- `Papers/`: grounded notes about individual academic papers.
- `Canonical/`: reviewed semantic owners.
- `candidate-review.base`: optional Obsidian view over candidate properties.

Candidate review is file-based: set `status` to `ready`, `deferred`, or `rejected` in Obsidian or
any Markdown editor. Agents integrate only `ready` candidates. An explicit request to integrate a
named non-applied candidate first moves it to `ready` in the same operation.

Desktop and headless clients may sync separate local replicas of this vault. Markdown and YAML remain
authoritative, and existing notes elsewhere in the vault remain human-owned by default.
"""

RUNTIME_README = """# .llm-wiki

Operational files for the `durable-knowledge` skill.

- `ROOT`: marker used to resolve the vault safely.
- `POLICY.md`: optional vault-owned admission and routing policy within the fixed record model.
- `Proposals/`: optional review artifacts for delayed or high-risk canonical changes.
- `templates/`: optional vault-owned template overrides.
"""


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def bootstrap(vault: Path, install_policy_copy: bool) -> list[Path]:
    vault = vault.expanduser().resolve()
    vault.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    skill_root = Path(__file__).resolve().parent.parent

    for relative in _DIRECTORIES:
        path = vault / relative
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)

    marker = vault / ".llm-wiki/ROOT"
    if write_if_missing(marker, "durable-knowledge-vault-v1\n"):
        created.append(marker)

    knowledge_readme = vault / "Knowledge/README.md"
    if write_if_missing(knowledge_readme, KNOWLEDGE_README):
        created.append(knowledge_readme)

    runtime_readme = vault / ".llm-wiki/README.md"
    if write_if_missing(runtime_readme, RUNTIME_README):
        created.append(runtime_readme)

    base_source = skill_root / "assets/candidate-review.base"
    base_destination = vault / "Knowledge/candidate-review.base"
    if not base_destination.exists():
        shutil.copyfile(base_source, base_destination)
        created.append(base_destination)

    if install_policy_copy:
        source = skill_root / "references/reference/admission-policy.md"
        destination = vault / ".llm-wiki/POLICY.md"
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
        help="Copy the bundled admission policy into .llm-wiki/POLICY.md if absent",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    created = bootstrap(args.vault, args.install_policy_copy)
    vault = args.vault.expanduser().resolve()

    print(f"Vault: {vault}")
    if created:
        print("Created:")
        for path in created:
            print(f"  - {path.relative_to(vault)}")
    else:
        print("No changes; the vault structure already exists.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
