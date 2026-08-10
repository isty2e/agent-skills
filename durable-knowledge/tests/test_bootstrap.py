import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parents[1]
_BOOTSTRAP = _SKILL_ROOT / "scripts/bootstrap.py"


class BootstrapTest(unittest.TestCase):
    def test_bootstrap_installs_both_obsidian_bases_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)

            first = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )
            knowledge_browser = vault / "Knowledge/knowledge-browser.base"
            candidate_review = vault / "Knowledge/candidate-review.base"

            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertTrue(knowledge_browser.is_file())
            self.assertTrue(candidate_review.is_file())
            self.assertIn(
                "file.asLink(if(title.isEmpty(), file.name, title))",
                knowledge_browser.read_text(encoding="utf-8"),
            )
            self.assertIn(
                "file.asLink(if(title.isEmpty(), file.name, title))",
                candidate_review.read_text(encoding="utf-8"),
            )

            knowledge_browser.write_text("customized base\n", encoding="utf-8")
            second = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertIn("No changes", second.stdout)
            self.assertEqual(
                knowledge_browser.read_text(encoding="utf-8"), "customized base\n"
            )


if __name__ == "__main__":
    unittest.main()
