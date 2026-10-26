import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
GATE = SKILL_DIR / "scripts" / "scan-gate.py"


class _ScanFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(
            prefix="scan-gate-test-", dir=Path.home()
        )
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.scan = self.root / "scan"
        shutil.copytree(SKILL_DIR / "examples" / "scan", self.scan)
        self.target = self.scan / "target"
        self._inventory()
        self._attest()

    def _gate(self, *arguments: str, code: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, "-B", str(GATE), *arguments],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def _inventory(
        self, *arguments: str, code: int = 0
    ) -> subprocess.CompletedProcess[str]:
        return self._gate(
            "inventory", str(self.target), str(self.scan), *arguments, code=code
        )

    def _attest(self) -> None:
        inventory = json.loads((self.scan / "inventory.json").read_text())
        coverage_path = self.scan / "coverage.json"
        coverage = json.loads(coverage_path.read_text())
        if "snapshot_digest" in inventory:
            coverage["snapshot_digest"] = inventory["snapshot_digest"]
        coverage["reviewed_files"] = [
            receipt
            for receipt in coverage["reviewed_files"]
            if receipt["path"] in inventory["files"]
        ]
        coverage_path.write_text(json.dumps(coverage))


class ScanGateTests(_ScanFixture):
    def test_example_passes(self) -> None:
        self._gate("check", str(self.scan))

    def test_bundled_example_passes_without_rebuilding_inventory(self) -> None:
        bundled = self.root / "bundled-scan"
        shutil.copytree(SKILL_DIR / "examples" / "scan", bundled)
        self._gate("check", str(bundled))

    def test_same_path_content_change_invalidates_receipts(self) -> None:
        (self.target / "app.py").write_text(
            "def handle_upload(body: bytes) -> bytes:\n    return body\n"
        )
        self._gate("check", str(self.scan), code=1)

    def test_inventory_rebuild_does_not_reattest_coverage(self) -> None:
        with (self.target / "app.py").open("a") as source:
            source.write("\nchanged = True\n")
        self._inventory()
        self._gate("check", str(self.scan), code=1)

        self._attest()
        self._gate("check", str(self.scan))

    def test_unchanged_inventory_rebuild_preserves_identity(self) -> None:
        before = (self.scan / "inventory.json").read_bytes()
        self._inventory()
        self.assertEqual((self.scan / "inventory.json").read_bytes(), before)
        self._gate("check", str(self.scan))

    def test_executable_bit_change_invalidates_receipts(self) -> None:
        source = self.target / "app.py"
        source.chmod(source.stat().st_mode ^ 0o100)
        self._gate("check", str(self.scan), code=1)

    def test_moving_scan_and_target_together_preserves_identity(self) -> None:
        moved = self.root / "moved"
        self.scan.rename(moved)
        self._gate("check", str(moved))

    def test_new_file_invalidates_inventory(self) -> None:
        (self.target / "new.py").write_text("value = 1\n")
        self._gate("check", str(self.scan), code=1)

    def test_deleted_file_invalidates_inventory(self) -> None:
        (self.target / "app.py").unlink()
        self._gate("check", str(self.scan), code=1)

    def test_symlink_identity_uses_link_text_not_referent_bytes(self) -> None:
        outside = self.root / "outside.txt"
        outside.write_text("not part of the target")
        link = self.target / "link"
        link.symlink_to(outside)
        self._inventory()

        coverage_path = self.scan / "coverage.json"
        coverage = json.loads(coverage_path.read_text())
        coverage["reviewed_files"].append(
            {
                "path": "link",
                "disposition": "reviewed",
                "read_full": True,
                "items": ["path"],
                "note": "The absolute link is reviewed without following it.",
            }
        )
        coverage_path.write_text(json.dumps(coverage))
        self._attest()
        self._gate("check", str(self.scan))

        outside.write_text("changed outside the scope")
        self._gate("check", str(self.scan))
        link.unlink()
        link.symlink_to(self.root / "missing.txt")
        self._gate("check", str(self.scan), code=1)

    def test_scope_cannot_read_through_a_symlink_parent(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "app.py").write_text("outside = True\n")
        (self.target / "linked").symlink_to(outside, target_is_directory=True)
        self._inventory("--scope", "linked/app.py", code=2)

    def test_empty_scoped_directory_cannot_bypass_symlink_parent_check(self) -> None:
        outside = self.root / "outside"
        (outside / "empty").mkdir(parents=True)
        (self.target / "linked").symlink_to(outside, target_is_directory=True)
        self._inventory("--scope", "linked/empty", code=2)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires POSIX named pipes")
    def test_special_file_is_refused_without_reading_it(self) -> None:
        os.mkfifo(self.target / "pipe")
        self._inventory(code=2)

    def test_inventory_without_content_identity_is_not_accepted(self) -> None:
        path = self.scan / "inventory.json"
        inventory = json.loads(path.read_text())
        inventory.pop("snapshot_digest", None)
        path.write_text(json.dumps(inventory))
        self._gate("check", str(self.scan), code=1)

    def test_every_pass_opening_questions_is_not_quiescence(self) -> None:
        path = self.scan / "scan-state.json"
        state = json.loads(path.read_text())
        for record in state["history"]:
            record["new_questions"] = 1
        path.write_text(json.dumps(state))
        self._gate("check", str(self.scan), code=1)

    def test_an_earlier_quiet_pass_does_not_close_later_questions(self) -> None:
        path = self.scan / "scan-state.json"
        state = json.loads(path.read_text())
        state["history"][-1]["new_questions"] = 1
        path.write_text(json.dumps(state))
        self._gate("check", str(self.scan), code=1)

    def test_a_new_quiet_pass_can_complete_after_questions_close(self) -> None:
        path = self.scan / "scan-state.json"
        state = json.loads(path.read_text())
        state["history"][-1]["new_questions"] = 1
        state["history"].append(
            {
                "pass": 4,
                "lens": "backward",
                "new_findings": 0,
                "new_rejections": 0,
                "new_questions": 0,
                "consumed_gaps": [],
                "note": "No new work after closing the previous questions.",
            }
        )
        path.write_text(json.dumps(state))

        path = self.scan / "findings.json"
        findings = json.loads(path.read_text())
        findings["passes"] = 4
        path.write_text(json.dumps(findings))
        self._gate("check", str(self.scan))

    def test_a_new_finding_resets_required_lenses(self) -> None:
        path = self.scan / "scan-state.json"
        state = json.loads(path.read_text())
        state["history"][-1]["new_findings"] = 1
        path.write_text(json.dumps(state))
        self._gate("check", str(self.scan), code=1)

    def test_missing_file_receipt_fails(self) -> None:
        path = self.scan / "coverage.json"
        coverage = json.loads(path.read_text())
        coverage["reviewed_files"] = coverage["reviewed_files"][1:]
        path.write_text(json.dumps(coverage))
        self._gate("check", str(self.scan), code=1)

    def test_wrong_severity_fails(self) -> None:
        path = self.scan / "findings.json"
        findings = json.loads(path.read_text())
        findings["findings"][0]["severity"] = "critical"
        path.write_text(json.dumps(findings))
        self._gate("check", str(self.scan), code=1)

    def test_missing_candidate_receipts_fail(self) -> None:
        (self.scan / "candidates.json").write_text("[]")
        self._gate("check", str(self.scan), code=1)

    def test_open_gaps_fail_even_with_a_quiet_pass(self) -> None:
        path = self.scan / "scan-state.json"
        state = json.loads(path.read_text())
        state["gaps"] = [
            {
                "id": "q-002",
                "kind": "question",
                "what": "An unresolved boundary",
                "closes_when": "The boundary is established",
                "owner_pass": 4,
            }
        ]
        path.write_text(json.dumps(state))
        self._gate("check", str(self.scan), code=1)


@unittest.skipUnless(shutil.which("git"), "requires the git CLI")
class GitInventoryTests(_ScanFixture):
    def _git(self, *arguments: str) -> str:
        environment = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        environment.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
        result = subprocess.run(
            [
                "git",
                "-C",
                str(self.target),
                "-c",
                "user.name=Scan tests",
                "-c",
                "user.email=scan-tests@example.invalid",
                "-c",
                "commit.gpgsign=false",
                "-c",
                "core.hooksPath=/dev/null",
                *arguments,
            ],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
            env=environment,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def _committed_change(self, *, delete: bool = False) -> tuple[str, str]:
        self._git("init", "-q")
        self._git("add", ".")
        self._git("commit", "-qm", "test: base")
        base = self._git("rev-parse", "HEAD")
        if delete:
            (self.target / "app.py").unlink()
        else:
            with (self.target / "app.py").open("a") as source:
                source.write("\nchanged = True\n")
        self._git("add", ".")
        self._git("commit", "-qm", "test: change")
        return base, self._git("rev-parse", "HEAD")

    def test_committed_diff_and_deleted_file_can_be_reviewed(self) -> None:
        base, head = self._committed_change(delete=True)
        self._inventory("--diff", base, head)
        self._attest()
        inventory = json.loads((self.scan / "inventory.json").read_text())
        self.assertEqual(inventory["files"], ["app.py"])
        self.assertEqual(inventory["deleted"], ["app.py"])
        self._gate("check", str(self.scan))

    def test_committed_diff_refuses_a_different_checkout(self) -> None:
        base, head = self._committed_change()
        self._git("checkout", "-q", base)
        self._inventory("--diff", base, head, code=2)

    def test_committed_diff_refuses_dirty_supporting_code(self) -> None:
        base, head = self._committed_change()
        (self.target / "README.md").write_text("dirty supporting context\n")
        self._inventory("--diff", base, head, code=2)

    def test_committed_diff_refuses_untracked_context(self) -> None:
        base, head = self._committed_change()
        (self.target / "new.py").write_text("new = True\n")
        self._inventory("--diff", base, head, code=2)

    def test_working_tree_content_drift_fails_without_path_changes(self) -> None:
        self._committed_change()
        source = self.target / "app.py"
        source.write_text("changed = 1\n")
        self._inventory("--working-tree")
        self._attest()
        self._gate("check", str(self.scan))

        source.write_text("changed = 2\n")
        self._gate("check", str(self.scan), code=1)

    def test_working_tree_base_change_invalidates_unchanged_dirty_bytes(self) -> None:
        self._committed_change()
        (self.target / "app.py").write_text("changed = 1\n")
        self._inventory("--working-tree")
        self._attest()
        self._gate("check", str(self.scan))

        self._git("commit", "--allow-empty", "-qm", "test: new diff base")
        self._gate("check", str(self.scan), code=1)

    def test_git_scope_is_a_literal_path_not_a_glob(self) -> None:
        self._committed_change()
        for name in ("[id]", "i"):
            directory = self.target / "pages" / name
            directory.mkdir(parents=True)
            (directory / "route.py").write_text("route = True\n")
        self._git("add", ".")
        self._git("commit", "-qm", "test: literal route directories")

        self._inventory("--scope", "pages/[id]")
        inventory = json.loads((self.scan / "inventory.json").read_text())
        self.assertEqual(inventory["files"], ["pages/[id]/route.py"])

    def test_git_inventory_does_not_execute_configured_clean_filters(self) -> None:
        self._committed_change()
        marker = self.root / "filter-ran"
        (self.target / ".gitattributes").write_text("*.py filter=scan-fixture\n")
        self._git(
            "config",
            "filter.scan-fixture.clean",
            f"cat; printf touched > {shlex.quote(str(marker))}",
        )
        self._git("config", "filter.scan-fixture.required", "true")
        self._git("add", ".")
        self._git("commit", "-qm", "test: configured filter")
        marker.unlink()

        (self.target / "app.py").write_text("changed = True\n")
        self._inventory("--working-tree")
        self.assertFalse(
            marker.exists(), "inventory must not invoke target-configured commands"
        )

    def test_git_inventory_does_not_start_configured_process_filters(self) -> None:
        self._committed_change()
        marker = self.root / "process-filter-ran"
        (self.target / ".gitattributes").write_text("*.py filter=scan-fixture\n")
        self._git("add", ".")
        self._git("commit", "-qm", "test: filter attributes")
        self._git(
            "config",
            "filter.scan-fixture.process",
            f"printf touched > {shlex.quote(str(marker))}",
        )
        self._git("config", "filter.scan-fixture.required", "true")

        (self.target / "app.py").write_text("changed = True\n")
        self._inventory("--working-tree")
        self.assertFalse(
            marker.exists(), "inventory must not start target-configured processes"
        )


if __name__ == "__main__":
    unittest.main()
