import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parents[1]
_ATTACH_ARTIFACT = _SKILL_ROOT / "scripts/attach_artifact.py"


class AttachArtifactTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.vault = self.root / "vault"
        control = self.vault / "_durable-knowledge"
        control.mkdir(parents=True)
        (control / "ROOT.md").write_text(
            "durable-knowledge-vault-v1\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_attach(self, source: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(_ATTACH_ARTIFACT),
                "--vault",
                str(self.vault),
                "--file",
                str(source),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_attach_creates_content_addressed_artifact(self) -> None:
        source = self.root / "evidence.JSON"
        payload = b'{"activations": 0, "decisions": 4096}\n'
        source.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()

        result = self.run_attach(source)

        artifact = (
            self.vault
            / "Knowledge/Artifacts"
            / f"artifact-sha256-{digest}"
            / "payload.json"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(artifact.read_bytes(), payload)
        self.assertIn(f"vault:artifact:sha256:{digest}", result.stdout)
        self.assertIn("Created: yes", result.stdout)

    def test_attach_is_idempotent_for_existing_bytes(self) -> None:
        source = self.root / "evidence.txt"
        source.write_text("proof report\n", encoding="utf-8")

        first = self.run_attach(source)
        second = self.run_attach(source)

        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("Created: no", second.stdout)
        artifacts = list((self.vault / "Knowledge/Artifacts").iterdir())
        self.assertEqual(len(artifacts), 1)

    def test_concurrent_same_payload_attachment_converges(self) -> None:
        source = self.root / "evidence.txt"
        source.write_text("concurrent evidence\n", encoding="utf-8")
        command = [
            sys.executable,
            str(_ATTACH_ARTIFACT),
            "--vault",
            str(self.vault),
            "--file",
            str(source),
        ]

        first = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        second = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        first_stdout, first_stderr = first.communicate()
        second_stdout, second_stderr = second.communicate()

        self.assertEqual(first.returncode, 0, first_stdout + first_stderr)
        self.assertEqual(second.returncode, 0, second_stdout + second_stderr)
        artifacts = list((self.vault / "Knowledge/Artifacts").iterdir())
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(
            sorted(
                line
                for line in (first_stdout + second_stdout).splitlines()
                if line.startswith("Created:")
            ),
            ["Created: no", "Created: yes"],
        )

    def test_concurrent_different_extensions_converge(self) -> None:
        text_source = self.root / "evidence.txt"
        json_source = self.root / "evidence.json"
        payload = b"x" * (1024 * 1024)
        text_source.write_bytes(payload)
        json_source.write_bytes(payload)

        def command(source: Path) -> list[str]:
            return [
                sys.executable,
                str(_ATTACH_ARTIFACT),
                "--vault",
                str(self.vault),
                "--file",
                str(source),
            ]

        first = subprocess.Popen(
            command(text_source),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        second = subprocess.Popen(
            command(json_source),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        first_stdout, first_stderr = first.communicate()
        second_stdout, second_stderr = second.communicate()

        self.assertEqual(first.returncode, 0, first_stdout + first_stderr)
        self.assertEqual(second.returncode, 0, second_stdout + second_stderr)
        artifact_directories = list((self.vault / "Knowledge/Artifacts").iterdir())
        self.assertEqual(len(artifact_directories), 1)
        self.assertEqual(
            len(list(artifact_directories[0].glob("payload.*"))),
            1,
        )

    def test_attach_reuses_same_bytes_with_different_extension(self) -> None:
        text_source = self.root / "evidence.txt"
        json_source = self.root / "evidence.json"
        payload = b"same bytes\n"
        text_source.write_bytes(payload)
        json_source.write_bytes(payload)

        first = self.run_attach(text_source)
        second = self.run_attach(json_source)

        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("Created: no", second.stdout)
        artifacts = list((self.vault / "Knowledge/Artifacts").iterdir())
        self.assertEqual(len(artifacts), 1)
        self.assertTrue((artifacts[0] / "payload.txt").is_file())

    def test_attach_rejects_extensionless_source(self) -> None:
        source = self.root / "evidence"
        source.write_text("extensionless\n", encoding="utf-8")

        result = self.run_attach(source)

        self.assertEqual(result.returncode, 1)
        self.assertIn("source file must have an extension", result.stderr)
        self.assertFalse((self.vault / "Knowledge/Artifacts").exists())

    def test_attach_rejects_symlinked_knowledge_parent(self) -> None:
        source = self.root / "evidence.txt"
        source.write_text("evidence\n", encoding="utf-8")
        external = self.root / "external-knowledge"
        external.mkdir()
        (self.vault / "Knowledge").symlink_to(external, target_is_directory=True)

        result = self.run_attach(source)

        self.assertEqual(result.returncode, 1)
        self.assertIn("managed artifact path must not contain symlinks", result.stderr)
        self.assertFalse((external / "Artifacts").exists())

    def test_attach_rejects_source_symlink(self) -> None:
        source = self.root / "evidence.txt"
        source.write_text("evidence\n", encoding="utf-8")
        symlink = self.root / "evidence-link.txt"
        symlink.symlink_to(source)

        result = self.run_attach(symlink)

        self.assertEqual(result.returncode, 1)
        self.assertIn("source file must not be a symlink", result.stderr)

    def test_attach_does_not_overwrite_integrity_conflict(self) -> None:
        source = self.root / "evidence.txt"
        payload = b"expected evidence\n"
        source.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        artifacts = self.vault / "Knowledge/Artifacts"
        artifacts.mkdir(parents=True)
        target_directory = artifacts / f"artifact-sha256-{digest}"
        target_directory.mkdir()
        target = target_directory / "payload.txt"
        target.write_bytes(b"different bytes\n")

        result = self.run_attach(source)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "existing artifact does not match its content hash", result.stderr
        )
        self.assertEqual(target.read_bytes(), b"different bytes\n")
        self.assertFalse(
            any(path.name.startswith(".artifact-") for path in artifacts.iterdir())
        )


if __name__ == "__main__":
    unittest.main()
