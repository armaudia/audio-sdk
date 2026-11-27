# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the Whisper-Streaming blocker package."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report(cls.contract)

    def test_decision_and_status(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "proposal_only_incomplete")
        self.assertEqual(self.contract["qualification_status"], "not_qualified")
        self.assertTrue(self.contract["proposal_only"])
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")

    def test_eight_blocked_gates(self) -> None:
        gates = self.contract["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in gates))
        self.assertTrue(all(g["qualifies"] is False for g in gates))
        self.assertEqual([g["id"] for g in gates], [f"RG-{i:02d}" for i in range(1, 9)])

    def test_eight_blockers(self) -> None:
        self.assertEqual(len(self.contract["exact_blockers"]), 8)
        self.assertEqual(len(self.report["exact_blockers"]), 8)

    def test_missing_result_never_qualifies(self) -> None:
        q = self.report["qualification"]
        self.assertTrue(q["no_missing_result_qualifies_candidate"])
        self.assertFalse(q["candidate_qualified"])
        self.assertTrue(q["all_release_gates_blocked"])
        for case in self.report["controls"]["adverse"]:
            self.assertEqual(case["result"], "rejected")
            self.assertFalse(case["qualifies"])

    def test_board_identity_not_whole_file(self) -> None:
        tri = self.report["task_row_identity"]
        self.assertFalse(tri["whole_file_hashed"])
        self.assertEqual(tri["stable_sha256"], reference.TASK_ROW_STABLE_SHA256)
        self.assertEqual(set(tri["excluded_mutable_fields"]), set(reference.MUTABLE_TASK_FIELDS))
        text = json.dumps(self.report)
        self.assertNotRegex(text, r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"')

    def test_boundary_and_scope(self) -> None:
        for k, v in reference.BOUNDARY.items():
            self.assertEqual(self.report["boundary"][k], v)
        for k, v in reference.SCOPE.items():
            self.assertEqual(self.report["scope"][k], v)
        self.assertIsNone(self.report["candidate_metrics"])

    def test_rate_profile_rows_blocked(self) -> None:
        rows = self.report["rate_profile"]["rows"]
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(r["status"] == "blocked" for r in rows))

    def test_canonical_bytes_stable(self) -> None:
        b1 = reference.canonical_bytes(self.report)
        b2 = reference.canonical_bytes(json.loads(b1.decode("utf-8")))
        self.assertEqual(b1, b2)


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.json"
            p.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(Exception):
                reference.read_strict_json(p)

    def test_nan_rejected(self) -> None:
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":NaN}')

    def test_inf_rejected(self) -> None:
        with self.assertRaises(Exception):
            reference.strict_loads('{"a":Infinity}')


class ScopeTests(unittest.TestCase):
    def _git(self, repo: Path, *args: str) -> str:
        r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
        return r.stdout.strip()

    def _repo(self, root: Path) -> Path:
        repo = root / "sdk"
        repo.mkdir()
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "config", "user.name", "t")
        self._git(repo, "config", "user.email", "t@example.invalid")
        self._git(repo, "config", "commit.gpgsign", "false")
        task = repo / reference.TASK_PREFIX
        task.mkdir(parents=True)
        (task / "README.md").write_text("x\n", encoding="utf-8")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "base")
        return repo

    def test_sibling_additions_after_base_pass_scope(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td))
            historical = self._git(repo, "rev-parse", "HEAD")
            sib = repo / "docs/task-evidence/sibling"
            sib.mkdir(parents=True)
            (sib / "report.json").write_text("{}\n", encoding="utf-8")
            self._git(repo, "add", "-A")
            self._git(repo, "commit", "-qm", "sibling")
            head = self._git(repo, "rev-parse", "HEAD")
            base = reference.scope_base(repo)
            self.assertEqual(base, head)
            self.assertEqual(reference.scope_changed_paths(repo, base), [])
            hist = reference.scope_changed_paths(repo, historical)
            self.assertIn("docs/task-evidence/sibling/report.json", hist)
            self.assertTrue(reference.scope_violations(hist))

    def test_branch_out_of_scope_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td))
            self._git(repo, "checkout", "-q", "-b", "feat")
            (repo / "CMakeLists.txt").write_text("x\n", encoding="utf-8")
            self._git(repo, "add", "CMakeLists.txt")
            self._git(repo, "commit", "-qm", "bad")
            base = reference.scope_base(repo)
            changed = reference.scope_changed_paths(repo, base)
            self.assertEqual(reference.scope_violations(changed), ["CMakeLists.txt"])

    def test_missing_base_ref_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = self._repo(Path(td))
            self._git(repo, "branch", "-m", "no-main")
            self.assertIsNone(reference.scope_base(repo))


class RegenerationTests(unittest.TestCase):
    def test_run_all_is_byte_identical(self) -> None:
        # run in temp copy to avoid touching committed files except verifying behavior
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sdk = root / "sdk"
            target = sdk / reference.TASK_PREFIX.rstrip("/")
            target.mkdir(parents=True)
            for f in HERE.iterdir():
                if f.is_file():
                    shutil.copyfile(f, target / f.name)
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
            env["SDK_ROOT"] = str(sdk)
            env["SOURCE_ROOT"] = str(reference.SOURCE_ROOT)
            # symlink boundary/source pins into expected locations
            for rel in reference.BOUNDARY_PINS:
                src = reference.SDK_ROOT / rel
                dst = sdk / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.symlink_to(src)
            r = subprocess.run([sys.executable, "run.py", "all"], cwd=target, capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("byte_identical=true", r.stdout)


if __name__ == "__main__":
    unittest.main()
