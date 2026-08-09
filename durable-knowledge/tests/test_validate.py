import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parents[1]
_VALIDATOR = _SKILL_ROOT / "scripts/validate.py"


class ValidateFrontmatterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.vault = Path(self.temporary_directory.name)
        (self.vault / ".llm-wiki").mkdir()
        (self.vault / ".llm-wiki/ROOT").write_text(
            "durable-knowledge-vault-v1\n", encoding="utf-8"
        )
        (self.vault / "Knowledge/Candidates").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def validate_candidate(
        self, scope_yaml: str, *, status_yaml: str = " pending", extra: str = ""
    ) -> subprocess.CompletedProcess[str]:
        candidate = self.vault / "Knowledge/Candidates/example.md"
        candidate.write_text(
            f"""---
id: candidate-20260313t142233123456z-example
record_type: candidate
knowledge_kind: method
status:{status_yaml}
evidence_state: observed
canonical_id: null
scope:{scope_yaml}
assumptions:
  - example assumption
invalidation_conditions:
  - example invalidation
source_refs:
  - artifact:example
created: 2026-03-13T14:22:33Z
updated: 2026-03-13T14:22:33Z
{extra}---

# Example candidate
""",
            encoding="utf-8",
        )
        return subprocess.run(
            [sys.executable, str(_VALIDATOR), "--vault", str(self.vault)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_valid_flat_sequence_passes(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", extra="metadata:\n  nested: ignored\n"
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_empty_required_sequence_fails(self) -> None:
        result = self.validate_candidate(" []")

        self.assertEqual(result.returncode, 1)
        self.assertIn("required sequence fields are empty: scope", result.stdout)

    def test_placeholder_sequence_item_fails(self) -> None:
        result = self.validate_candidate("\n  - <scope>")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "sequence fields contain empty or placeholder items: scope", result.stdout
        )

    def test_comment_only_sequence_item_fails(self) -> None:
        result = self.validate_candidate("\n  - # missing scope")

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "sequence fields contain empty or placeholder items: scope", result.stdout
        )

    def test_scalar_instead_of_sequence_fails(self) -> None:
        result = self.validate_candidate(" example scope")

        self.assertEqual(result.returncode, 1)
        self.assertIn("fields must be flat sequences: scope", result.stdout)

    def test_sequence_instead_of_scalar_fails(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", status_yaml="\n  - pending"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("fields must be scalars: status", result.stdout)

    def test_duplicate_top_level_field_fails(self) -> None:
        result = self.validate_candidate(
            "\n  - example scope", extra="id: duplicate-id\n"
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate top-level field: id", result.stdout)


if __name__ == "__main__":
    unittest.main()
