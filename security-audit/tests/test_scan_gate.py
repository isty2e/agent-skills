import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Literal
from unittest.mock import patch

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
    def _git(self, *arguments: str, accept: tuple[int, ...] = (0,)) -> str:
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
        self.assertIn(result.returncode, accept, result.stdout + result.stderr)
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

    def _create_child_repository(self, directory: Path) -> None:
        directory.mkdir()
        self._git("-C", str(directory), "init", "-q")
        (directory / "child.py").write_text("child = True\n")
        self._git("-C", str(directory), "add", ".")
        self._git("-C", str(directory), "commit", "-qm", "test: child source")

    def _add_submodule(self) -> Path:
        source = self.root / "module-source"
        self._create_child_repository(source)
        self._git("-c", "protocol.file.allow=always", "submodule", "add", str(source), "module")
        self._git("commit", "-qm", "test: registered submodule")
        return self.target / "module"

    def _assert_submodule_filter_confined(self, kind: Literal["clean", "process"]) -> None:
        base, _ = self._committed_change()
        module = self._add_submodule()
        (module / ".gitattributes").write_text("*.py filter=child-only\n")
        self._git("-C", str(module), "add", ".")
        self._git("-C", str(module), "commit", "-qm", "test: child attributes")
        self._git("add", "module")
        self._git("commit", "-qm", "test: record child attributes")
        head = self._git("rev-parse", "HEAD")
        self._git("config", "diff.submodule", "diff")
        self._git("config", "submodule.module.ignore", "none")

        marker = self.root / "child-filter-ran"
        command = f"printf touched > {shlex.quote(str(marker))}"
        if kind == "clean":
            command = "cat; " + command
        self._git("-C", str(module), "config", f"filter.child-only.{kind}", command)
        self._git("-C", str(module), "config", "filter.child-only.required", "true")
        source = module / "child.py"
        metadata = source.stat()
        source.write_text("child = None\n")
        os.utime(source, ns=(metadata.st_atime_ns, metadata.st_mtime_ns + 2_000_000_000))
        self._git("-C", str(module), "diff", "--exit-code", "--no-ext-diff", "--no-textconv", "HEAD",
                  "--", "child.py", accept=(1, 128))
        self.assertTrue(marker.exists(), "the child filter canary must be active")
        marker.unlink()

        child_git = Path(self._git("-C", str(module), "rev-parse", "--absolute-git-dir"))
        index = child_git / "index"
        before = index.read_bytes()
        original = (self.target / "app.py").read_bytes()
        for arguments in ((), ("--working-tree",), ("--diff", base, head)):
            with self.subTest(mode=arguments):
                marker.unlink(missing_ok=True)
                if arguments == ("--working-tree",):
                    (self.target / "app.py").write_text("parent_dirty = True\n")
                else:
                    (self.target / "app.py").write_bytes(original)
                self._inventory(*arguments, "--exclude", "module")
                self.assertFalse(marker.exists(), "parent inventory must not execute child filters")
                self.assertEqual(index.read_bytes(), before)

        marker.unlink(missing_ok=True)
        self._gate("inventory", str(module), str(self.root / "child-scan"), "--working-tree")
        self.assertFalse(marker.exists(), "a separate child scan must neutralize its own filters")

    def test_deleted_working_tree_paths_remain_valid_explicit_scopes(self) -> None:
        self._committed_change()
        directory = self.target / "removed[1]"
        directory.mkdir()
        (directory / "old.py").write_text("old = True\n")
        self._git("add", ".")
        self._git("commit", "-qm", "test: removable directory")
        head = self._git("rev-parse", "HEAD")
        for staged in (False, True):
            for scope in ("app.py", "removed[1]"):
                with self.subTest(staged=staged, scope=scope):
                    self._git("reset", "--hard", head)
                    if staged:
                        self._git("rm", "-r", "--", scope)
                    elif scope == "app.py":
                        (self.target / scope).unlink()
                    else:
                        shutil.rmtree(self.target / scope)
                    self._inventory("--working-tree", "--scope", scope)
                    inventory = json.loads((self.scan / "inventory.json").read_text())
                    deleted = "app.py" if scope == "app.py" else "removed[1]/old.py"
                    self.assertEqual(inventory["files"], [deleted])
                    self.assertEqual(inventory["deleted"], [deleted])

    def test_unknown_missing_working_tree_scopes_are_rejected(self) -> None:
        self._committed_change()
        for arguments in ((), ("--working-tree",)):
            with self.subTest(mode=arguments):
                self._inventory(*arguments, "--scope", "never-existed.py", code=2)

    def test_nested_repository_boundaries_require_separate_inventory(self) -> None:
        self._committed_change()
        nested = self.target / "nested"
        self._create_child_repository(nested)
        for arguments in ((), ("--working-tree",)):
            for scope in ((), ("--scope", "nested"), ("--scope", "nested/child.py")):
                with self.subTest(mode=arguments, scope=scope):
                    self._inventory(*arguments, *scope, code=2)
            self._inventory(*arguments, "--scope", "app.py")
            self._inventory(*arguments, "--exclude", "nested")
        self._gate("inventory", str(nested), str(self.root / "nested-scan"))
        inventory = json.loads((self.root / "nested-scan" / "inventory.json").read_text())
        self.assertEqual(inventory["files"], ["child.py"])

    def test_new_nested_repository_invalidates_existing_inventory(self) -> None:
        self._committed_change()
        self._inventory()
        self._attest()
        self._gate("check", str(self.scan))
        before = (self.scan / "inventory.json").read_bytes()
        self._create_child_repository(self.target / "nested")
        self._inventory(code=2)
        self.assertEqual((self.scan / "inventory.json").read_bytes(), before)
        self._gate("check", str(self.scan), code=1)

    @unittest.skipUnless(os.name == "posix", "requires POSIX directory permissions")
    def test_unreadable_untracked_source_never_becomes_coverage(self) -> None:
        self._committed_change()
        self._inventory()
        self._attest()
        self._gate("check", str(self.scan))
        before = (self.scan / "inventory.json").read_bytes()
        denied = self.target / "denied"
        denied.mkdir()
        (denied / "hidden.py").write_text("hidden = True\n")
        denied.chmod(0)
        try:
            if os.access(denied, os.R_OK | os.X_OK):
                self.skipTest("environment bypasses directory permissions")
            self._inventory(code=2)
            self.assertEqual((self.scan / "inventory.json").read_bytes(), before)
            self._gate("check", str(self.scan), code=1)
        finally:
            denied.chmod(0o700)

    def test_uninitialized_gitlink_source_is_not_silently_omitted(self) -> None:
        self._committed_change()
        module = self._add_submodule()
        (module / ".git").unlink()
        for scope in ((), ("--scope", "module"), ("--scope", "module/child.py")):
            with self.subTest(scope=scope):
                self._inventory(*scope, code=2)
        self._gate("inventory", str(module), str(self.root / "module-scan"), code=2)
        self._inventory("--exclude", "module")

    def test_parent_inventory_never_executes_submodule_clean_filters(self) -> None:
        self._assert_submodule_filter_confined("clean")

    def test_parent_inventory_never_executes_submodule_process_filters(self) -> None:
        self._assert_submodule_filter_confined("process")

    def test_submodule_head_drift_prevents_committed_diff(self) -> None:
        base, _ = self._committed_change()
        module = self._add_submodule()
        head = self._git("rev-parse", "HEAD")
        (module / "child.py").write_text("child_changed = True\n")
        self._git("-C", str(module), "add", ".")
        self._git("-C", str(module), "commit", "-qm", "test: child HEAD drift")
        self._inventory("--diff", base, head, "--exclude", "module", code=2)

    def test_deleted_gitlink_remains_in_parent_working_tree_scope(self) -> None:
        self._committed_change()
        self._add_submodule()
        self._git("rm", "-f", "module")
        self._inventory("--working-tree", "--scope", "module")
        inventory = json.loads((self.scan / "inventory.json").read_text())
        self.assertEqual(inventory["files"], ["module"])
        self.assertEqual(inventory["deleted"], ["module"])

    @unittest.skipUnless(hasattr(os, "symlink"), "requires symlinks")
    def test_scoped_symlink_to_nested_repository_is_not_followed(self) -> None:
        self._committed_change()
        self._create_child_repository(self.target / "nested")
        (self.target / "link").symlink_to("nested", target_is_directory=True)
        self._inventory("--scope", "link")
        inventory = json.loads((self.scan / "inventory.json").read_text())
        self.assertEqual(inventory["files"], ["link"])
        before = inventory["snapshot_digest"]
        (self.target / "nested" / "child.py").write_text("out_of_scope_change = True\n")
        self._inventory("--scope", "link")
        after = json.loads((self.scan / "inventory.json").read_text())
        self.assertEqual(after["snapshot_digest"], before)

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

    def test_working_tree_removal_hashes_reintroduced_source(self) -> None:
        _, head = self._committed_change()
        source = self.target / "app.py"
        for removal in ("index-only", "removed-and-recreated"):
            with self.subTest(removal=removal):
                self._git("reset", "--hard", head)
                self._git("rm", *(["--cached"] if removal == "index-only" else []), "app.py")
                source.write_text("changed = 1\n")
                self._inventory("--working-tree")
                inventory = json.loads((self.scan / "inventory.json").read_text())
                self.assertEqual(inventory["files"], ["app.py"])
                self.assertEqual(inventory["deleted"], [])
                self._attest()
                self._gate("check", str(self.scan))

                source.write_text("changed = 2\n")
                self._gate("check", str(self.scan), code=1)

    @unittest.skipUnless(hasattr(os, "symlink"), "requires symlinks")
    def test_working_tree_removal_hashes_reintroduced_dangling_link(self) -> None:
        self._committed_change()
        self._git("rm", "app.py")
        source = self.target / "app.py"
        source.symlink_to("missing-a.py")
        self._inventory("--working-tree")
        inventory = json.loads((self.scan / "inventory.json").read_text())
        self.assertEqual(inventory["deleted"], [])
        self._attest()
        self._gate("check", str(self.scan))

        source.unlink()
        source.symlink_to("missing-b.py")
        self._gate("check", str(self.scan), code=1)

    def test_working_tree_absent_source_is_recorded_as_deleted(self) -> None:
        self._committed_change()
        self._git("rm", "app.py")
        self._inventory("--working-tree")
        inventory = json.loads((self.scan / "inventory.json").read_text())
        self.assertEqual(inventory["files"], ["app.py"])
        self.assertEqual(inventory["deleted"], ["app.py"])
        self._attest()
        self._gate("check", str(self.scan))

    def test_committed_diff_refuses_unchecked_index_entries(self) -> None:
        base, head = self._committed_change()
        self._inventory("--diff", base, head, "--scope", "app.py")
        for flag in ("assume-unchanged", "skip-worktree"):
            for name in ("app.py", "README.md"):
                with self.subTest(flag=flag, path=name):
                    source = self.target / name
                    original = source.read_bytes()
                    self._git("update-index", f"--{flag}", "--", name)
                    try:
                        source.write_text("unchecked source\n")
                        index = self.target / ".git" / "index"
                        before = index.read_bytes()
                        self._inventory("--diff", base, head, "--scope", "app.py", code=2)
                        self.assertEqual(index.read_bytes(), before)
                    finally:
                        source.write_bytes(original)
                        self._git("update-index", f"--no-{flag}", "--", name)

    def test_git_scope_is_a_literal_filename_in_every_inventory_mode(self) -> None:
        base, _ = self._committed_change()
        names = ("data[1].py", "data1.py")
        for name in names:
            (self.target / name).write_text("value = 1\n")
        self._git("add", ".")
        self._git("commit", "-qm", "test: literal filenames")
        head = self._git("rev-parse", "HEAD")
        for arguments in ((), ("--working-tree",), ("--diff", base, head)):
            with self.subTest(mode=arguments):
                self._git("reset", "--hard", head)
                if arguments == ("--working-tree",):
                    for name in names:
                        (self.target / name).write_text("value = 2\n")
                self._inventory(*arguments, "--scope", "data[1].py")
                inventory = json.loads((self.scan / "inventory.json").read_text())
                self.assertEqual(inventory["files"], ["data[1].py"])

    def test_working_tree_refuses_unchecked_index_entries(self) -> None:
        self._committed_change()
        source = self.target / "app.py"
        original = source.read_bytes()
        source.write_text("changed = 1\n")
        self._inventory("--working-tree", "--scope", "app.py")
        for flag in ("assume-unchanged", "skip-worktree"):
            with self.subTest(flag=flag):
                self._git("update-index", f"--{flag}", "--", "app.py")
                try:
                    source.write_text("changed = 1\n")
                    self._inventory("--working-tree", "--scope", "app.py", code=2)
                    self._inventory("--scope", "app.py")
                    self._attest()
                    self._gate("check", str(self.scan))

                    source.write_text("changed = 2\n")
                    self._gate("check", str(self.scan), code=1)
                finally:
                    source.write_bytes(original)
                    self._git("update-index", f"--no-{flag}", "--", "app.py")

    @unittest.skipUnless(os.name == "posix", "requires POSIX transport canaries")
    def test_git_inventory_never_starts_a_lazy_fetch_transport(self) -> None:
        base, head = self._committed_change()
        remote = self.root / "origin.git"
        self._git("clone", "--bare", "--no-hardlinks", str(self.target), str(remote))
        tree = self._git("rev-parse", "HEAD^{tree}")
        self._git("config", "core.repositoryformatversion", "1")
        self._git("config", "extensions.partialclone", "origin")
        self._git("config", "remote.origin.promisor", "true")

        marker = self.root / "transport-ran"
        binary = self.root / "bin"
        binary.mkdir()
        upload_pack = binary / "upload-pack"
        remote_helper = binary / "git-remote-audit-fixture"
        for executable in (upload_pack, remote_helper):
            executable.write_text(f"#!/bin/sh\nprintf touched > {shlex.quote(str(marker))}\nexit 1\n")
            executable.chmod(0o700)
        self._git("config", "remote.origin.uploadpack", str(upload_pack))
        objects = self.target / ".git" / "objects"
        (objects / tree[:2] / tree[2:]).unlink()

        path = str(binary) + os.pathsep + os.environ.get("PATH", "")
        for protocol, url in (("file", str(remote)), ("audit-fixture", "audit-fixture::opaque")):
            with self.subTest(protocol=protocol), patch.dict(os.environ, {"PATH": path}):
                marker.unlink(missing_ok=True)
                self._git("config", "remote.origin.url", url)
                self._git("config", f"protocol.{protocol}.allow", "always")
                self._inventory()
                for arguments in (("--working-tree",), ("--diff", base, head)):
                    git_directory = self.target / ".git"
                    before = {path.relative_to(git_directory): path.read_bytes()
                              for path in git_directory.rglob("*") if path.is_file()}
                    self._inventory(*arguments, code=2)
                    self.assertFalse(marker.exists(), "inventory must not launch a Git transport")
                    self.assertEqual({path.relative_to(git_directory): path.read_bytes()
                                      for path in git_directory.rglob("*") if path.is_file()}, before)

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
        (self.target / "app.py").write_text("filter_fixture = True\n")
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
