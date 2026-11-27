# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-WAVLM-LARGE-IN-TOKAN blocker evidence."""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import reference


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def _commit(repo: Path, rel: str, content: str, msg: str) -> str:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


class TestReference(unittest.TestCase):
    def test_decision_qualification_gates(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in report["gates"]))
        self.assertGreaterEqual(len(report["exact_blockers"]), 6)
        self.assertFalse(report["source_reported"]["qualifies"])

    def test_boundary_scope_no_claims(self) -> None:
        report = reference.build_report()
        for k, v in report["boundary"].items():
            if k == "format":
                continue
            self.assertFalse(v, k)
        self.assertTrue(report["scope"]["synthetic_only"])
        self.assertTrue(report["scope"]["task_local_only"])
        for k, v in report["scope"].items():
            if k in {"synthetic_only", "task_local_only"}:
                continue
            self.assertFalse(v, k)
        self.assertFalse(report["evidence_classes"]["real_model_output"])

    def test_absence_and_adverse(self) -> None:
        report = reference.build_report()
        self.assertTrue(report["absence_summary"]["all_absent"])
        adverse = report["adverse"]
        self.assertTrue(adverse["all_rejected"])
        self.assertIsNone(adverse["metrics"])
        self.assertGreaterEqual(len(adverse["manifest_cases"]), 10)
        self.assertGreaterEqual(len(adverse["json_cases"]), 3)

    def test_strict_json_rejects_bad_inputs(self) -> None:
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":1,"a":2}')
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":NaN}')
        with self.assertRaises(Exception):
            reference.strict_loads('[1.5]')

    def test_canonical_bytes_stable(self) -> None:
        a = reference.report_bytes()
        b = reference.report_bytes()
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(b"\n"))

    def test_board_link_stable_identity_only(self) -> None:
        link = reference.board_link()
        self.assertFalse(link["full_tasks_json_hashed"])
        self.assertEqual(link["stable_row"]["id"], reference.TASK_ID)
        self.assertEqual(link["stable_sha256"], reference.sha256_bytes(reference.canonical_bytes(reference.BOARD_STABLE_ROW).rstrip(b"\n")))

    def test_source_and_boundary_pins(self) -> None:
        for rel, digest in reference.SOURCE_PINS.items():
            self.assertEqual(reference.sha256_file(reference.resolve_source(rel)), digest, rel)
        for rel, digest in reference.BOUNDARY_PINS.items():
            self.assertEqual(reference.sha256_file(reference.resolve_worktree(rel)), digest, rel)


class TestScopeRegression(unittest.TestCase):
    def _init_repo(self) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        repo = Path(td.name)
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "test@example.com")
        _git(repo, "config", "user.name", "Test")
        _commit(repo, "README.md", "base\n", "base")
        return repo

    def test_newest_merge_base_origin_main(self) -> None:
        repo = self._init_repo()
        cur = _git(repo, "branch", "--show-current")
        if cur != "main":
            _git(repo, "branch", "-m", cur, "main")
        base0 = _git(repo, "rev-parse", "HEAD")
        _git(repo, "checkout", "-b", "feature")
        _commit(repo, "docs/task-evidence/wavlm-large-in-tokan/x.txt", "x\n", "feat")
        _git(repo, "checkout", "main")
        _commit(repo, "main.txt", "main\n", "main advance")
        main_tip = _git(repo, "rev-parse", "HEAD")
        _git(repo, "checkout", "-b", "origin_tip", base0)
        _commit(repo, "o.txt", "o\n", "origin advance")
        origin_tip = _git(repo, "rev-parse", "HEAD")
        _git(repo, "update-ref", "refs/remotes/origin/main", origin_tip)
        _git(repo, "branch", "-f", "main", main_tip)
        _git(repo, "checkout", "feature")
        _git(repo, "merge", "-q", "--no-edit", "origin_tip")
        # merge-base(feature, origin/main)=origin_tip newer than merge-base(feature, main)=base0
        base = reference.scope_base(repo, ("origin/main", "main"))
        self.assertEqual(base, origin_tip)

    def test_fallback_to_main(self) -> None:
        repo = self._init_repo()
        cur = _git(repo, "branch", "--show-current")
        if cur != "main":
            _git(repo, "branch", "-m", cur, "main")
        base = _git(repo, "rev-parse", "HEAD")
        _git(repo, "checkout", "-b", "feature")
        _commit(repo, "docs/task-evidence/wavlm-large-in-tokan/x.txt", "x\n", "feat")
        self.assertEqual(reference.scope_base(repo, ("origin/main", "main")), base)

    def test_out_of_scope_and_missing_base_fail_closed(self) -> None:
        repo = self._init_repo()
        cur = _git(repo, "branch", "--show-current")
        if cur != "main":
            _git(repo, "branch", "-m", cur, "main")
        base = _git(repo, "rev-parse", "HEAD")
        _git(repo, "checkout", "-b", "feature")
        _commit(repo, "docs/task-evidence/wavlm-large-in-tokan/x.txt", "x\n", "feat")
        _commit(repo, "README.md", "bad\n", "oos")
        changed = reference.scope_changed_paths(repo, base)
        self.assertIn("README.md", reference.scope_violations(changed))
        self.assertIsNone(reference.scope_base(repo, ("origin/missing", "missing")))


if __name__ == "__main__":
    unittest.main()
