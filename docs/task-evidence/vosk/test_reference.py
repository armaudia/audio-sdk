# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-VOSK blocker evidence package."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run  # noqa: E402


class ReferenceTests(unittest.TestCase):
    def test_contract_report_stable(self):
        c1 = reference.build_contract()
        c2 = reference.build_contract()
        r1 = reference.build_report()
        r2 = reference.build_report()
        self.assertEqual(c1, c2)
        self.assertEqual(r1, r2)
        self.assertEqual(reference.canonical_bytes(r1), reference.canonical_bytes(r2))

    def test_decision_and_gates(self):
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["qualified"])
        self.assertEqual(len(report["release_gates"]), 8)
        for g in report["release_gates"]:
            self.assertEqual(g["status"], "blocked")
            self.assertFalse(g["qualifies"])
        self.assertEqual(len(report["exact_blockers"]), 6)
        for b in report["exact_blockers"]:
            self.assertEqual(b["status"], "open")
            self.assertFalse(b["qualifies"])

    def test_strict_json_rejects_duplicate_and_float(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.json"
            p.write_text('{"a":1,"a":2}\n', encoding="utf-8")
            with self.assertRaises(reference.ReferenceError):
                reference.load_strict_json(p)
            p.write_text('{"a":1.5}\n', encoding="utf-8")
            with self.assertRaises(reference.ReferenceError):
                reference.load_strict_json(p)

    def test_linked_row_identity_stable(self):
        lri = reference.linked_row_identity()
        self.assertFalse(lri["mutable_board_hash_used"])
        self.assertEqual(lri["gating"], "stable_identity_only")
        self.assertEqual(lri["projection"]["id"], "SDK-VOSK")
        self.assertEqual(lri["sha256"], reference.sha256_bytes(reference.canonical_bytes(lri["projection"])))

    def test_absence_probe_shape(self):
        a = reference.probe_absence()
        self.assertTrue(a["all_absent"])
        self.assertFalse(a["runtime_import_attempted"])
        self.assertFalse(a["model_load_attempted"])
        self.assertFalse(a["download_attempted"])

    def test_run_regenerates_byte_identical(self):
        before = (HERE / "report.json").read_bytes() if (HERE / "report.json").exists() else b""
        run.main([])
        a = (HERE / "report.json").read_bytes()
        run.main([])
        b = (HERE / "report.json").read_bytes()
        run.main([])
        c = (HERE / "report.json").read_bytes()
        self.assertEqual(a, b)
        self.assertEqual(b, c)
        if before:
            self.assertEqual(before, a)


class ScopeRegressionTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout.strip()

    def _repo(self, root: Path) -> Path:
        repo = root / "repo"
        repo.mkdir()
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "scope-test")
        self._git(repo, "config", "user.email", "scope@example.invalid")
        self._git(repo, "config", "commit.gpgsign", "false")
        task = repo / reference.TASK_PREFIX
        task.mkdir(parents=True)
        (task / "README.md").write_text("pkg\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "task")
        return repo

    def _add_siblings(self, repo: Path) -> None:
        for name in ["sibling-a", "sibling-b"]:
            p = repo / "docs/task-evidence" / name
            p.mkdir(parents=True)
            (p / "report.json").write_text("{}\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "siblings")

    def test_scope_sibling_additions_after_base_pass(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td))
            historical = self._git(repo, "rev-parse", "HEAD")
            self._add_siblings(repo)
            head = self._git(repo, "rev-parse", "HEAD")
            base = reference.scope_base(repo)
            self.assertEqual(base, head)
            self.assertEqual(reference.scope_changed_paths(repo, base), [])
            historic = reference.scope_changed_paths(repo, historical)
            self.assertTrue(any("sibling-a" in p for p in historic))
            self.assertTrue(reference.scope_violations(historic))

    def test_scope_out_of_tree_change_fails(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td))
            self._add_siblings(repo)
            self._git(repo, "checkout", "-q", "-b", "swarm/SDK-VOSK-scope")
            (repo / "CMakeLists.txt").write_text("bad\n", encoding="utf-8")
            self._git(repo, "add", "CMakeLists.txt")
            self._git(repo, "commit", "-qm", "bad")
            base = reference.scope_base(repo)
            paths = reference.scope_changed_paths(repo, base)
            self.assertEqual(paths, ["CMakeLists.txt"])
            self.assertEqual(reference.scope_violations(paths), ["CMakeLists.txt"])

    def test_scope_missing_base_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td))
            self._git(repo, "branch", "-m", "detached-work")
            self.assertIsNone(reference.scope_base(repo))


if __name__ == "__main__":
    unittest.main()
