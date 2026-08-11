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
            self.assertTrue((vault / "_durable-knowledge/ROOT.md").is_file())
            self.assertFalse((vault / "_durable-knowledge/ROOT").exists())
            self.assertTrue((vault / "Knowledge/Artifacts").is_dir())
            self.assertIn(
                "immutable content-addressed evidence snapshots",
                (vault / "Knowledge/README.md").read_text(encoding="utf-8"),
            )
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
            knowledge_browser_text = knowledge_browser.read_text(encoding="utf-8")
            candidate_review_text = candidate_review.read_text(encoding="utf-8")
            self.assertIn('file.inFolder("Knowledge/Papers")', knowledge_browser_text)
            self.assertIn("name: All knowledge", knowledge_browser_text)
            self.assertIn("name: Papers", knowledge_browser_text)
            self.assertIn("displayName: Topics", knowledge_browser_text)
            self.assertIn("displayName: Topics", candidate_review_text)
            self.assertIn("displayName: Review reason", candidate_review_text)
            self.assertGreaterEqual(candidate_review_text.count("- review_reason"), 4)

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

    def test_bootstrap_rejects_symlinked_knowledge_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            vault = root / "vault"
            vault.mkdir()
            external = root / "external-knowledge"
            external.mkdir()
            (vault / "Knowledge").symlink_to(external, target_is_directory=True)

            result = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "managed directory path must not contain symlinks", result.stderr
            )
            self.assertFalse((external / "Artifacts").exists())

    def test_bootstrap_migrates_legacy_control_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)
            legacy = vault / ".llm-wiki"
            legacy.mkdir()
            (legacy / "ROOT").write_text(
                "durable-knowledge-vault-v1\n", encoding="utf-8"
            )
            (legacy / "POLICY.md").write_text("custom policy\n", encoding="utf-8")
            (legacy / "Proposals").mkdir()
            (legacy / "Proposals/example.md").write_text(
                "legacy proposal\n", encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Migrated: .llm-wiki -> _durable-knowledge", result.stdout)
            self.assertNotIn("No changes", result.stdout)
            self.assertFalse(legacy.exists())
            self.assertFalse((vault / "_durable-knowledge/ROOT").exists())
            self.assertEqual(
                (vault / "_durable-knowledge/ROOT.md").read_text(encoding="utf-8"),
                "durable-knowledge-vault-v1\n",
            )
            self.assertEqual(
                (vault / "_durable-knowledge/POLICY.md").read_text(encoding="utf-8"),
                "custom policy\n",
            )
            self.assertEqual(
                (vault / "_durable-knowledge/Proposals/example.md").read_text(
                    encoding="utf-8"
                ),
                "legacy proposal\n",
            )

    def test_bootstrap_recovers_after_post_migration_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)
            legacy = vault / ".llm-wiki"
            legacy.mkdir()
            (legacy / "ROOT").write_text(
                "durable-knowledge-vault-v1\n", encoding="utf-8"
            )
            (legacy / "POLICY.md").write_text("custom policy\n", encoding="utf-8")
            knowledge_blocker = vault / "Knowledge"
            knowledge_blocker.write_text(
                "blocks directory creation\n", encoding="utf-8"
            )

            failed = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(legacy.exists())
            self.assertEqual(
                (vault / "_durable-knowledge/POLICY.md").read_text(encoding="utf-8"),
                "custom policy\n",
            )

            knowledge_blocker.unlink()
            recovered = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(
                recovered.returncode, 0, recovered.stdout + recovered.stderr
            )
            self.assertTrue((vault / "Knowledge/Candidates").is_dir())
            self.assertTrue((vault / "_durable-knowledge/ROOT.md").is_file())

    def test_bootstrap_migrates_legacy_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)
            control = vault / "_durable-knowledge"
            control.mkdir()
            legacy_marker = control / "ROOT"
            legacy_marker.write_text("durable-knowledge-vault-v1\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(
                "Migrated: _durable-knowledge/ROOT -> _durable-knowledge/ROOT.md",
                result.stdout,
            )
            self.assertFalse(legacy_marker.exists())
            self.assertEqual(
                (control / "ROOT.md").read_text(encoding="utf-8"),
                "durable-knowledge-vault-v1\n",
            )

    def test_bootstrap_removes_matching_legacy_marker_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)
            control = vault / "_durable-knowledge"
            control.mkdir()
            legacy_marker = control / "ROOT"
            marker = control / "ROOT.md"
            marker_content = "durable-knowledge-vault-v1\n"
            legacy_marker.write_text(marker_content, encoding="utf-8")
            marker.write_text(marker_content, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(legacy_marker.exists())
            self.assertEqual(marker.read_text(encoding="utf-8"), marker_content)

    def test_bootstrap_rejects_conflicting_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)
            control = vault / "_durable-knowledge"
            control.mkdir()
            legacy_marker = control / "ROOT"
            marker = control / "ROOT.md"
            legacy_marker.write_text("legacy marker\n", encoding="utf-8")
            marker.write_text("current marker\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("marker files differ", result.stderr)
            self.assertEqual(
                legacy_marker.read_text(encoding="utf-8"), "legacy marker\n"
            )
            self.assertEqual(marker.read_text(encoding="utf-8"), "current marker\n")
            self.assertFalse((vault / "Knowledge").exists())

    def test_bootstrap_rejects_non_file_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)
            control = vault / "_durable-knowledge"
            control.mkdir()
            (control / "ROOT.md").mkdir()

            result = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("ROOT.md is not a regular marker file", result.stderr)
            self.assertFalse((vault / "Knowledge").exists())

    def test_bootstrap_rejects_ambiguous_control_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault = Path(temporary_directory)
            legacy = vault / ".llm-wiki"
            control = vault / "_durable-knowledge"
            legacy.mkdir()
            control.mkdir()
            (legacy / "legacy.txt").write_text("legacy\n", encoding="utf-8")
            (control / "current.txt").write_text("current\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(_BOOTSTRAP), "--vault", str(vault)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("reconcile their contents manually", result.stderr)
            self.assertTrue((legacy / "legacy.txt").is_file())
            self.assertTrue((control / "current.txt").is_file())


if __name__ == "__main__":
    unittest.main()
