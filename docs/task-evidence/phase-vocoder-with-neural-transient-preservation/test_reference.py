# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the task-local evidence package."""

from __future__ import annotations

import json
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


class ReferenceTest(unittest.TestCase):
    def test_canonical_report_stable(self) -> None:
        a, da = reference.canonical_report()
        b, db = reference.canonical_report()
        self.assertEqual(a, b)
        self.assertEqual(da, db)
        self.assertEqual(len(da), 64)

    def test_contract_and_report_schema(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report()
        self.assertEqual(contract["decision"], reference.DECISION)
        self.assertEqual(report["decision"], reference.DECISION)
        self.assertEqual(report["qualification_status"], reference.QUALIFICATION_STATUS)
        self.assertTrue(report["proposal_only"])
        self.assertTrue(report["incomplete"])
        self.assertEqual(report["contract_sha256"], reference.object_digest(contract))

    def test_gate_and_blocker_shape(self) -> None:
        report = reference.build_report()
        gates = report["release_gates"]
        blockers = report["exact_blockers"]
        self.assertEqual([g["id"] for g in gates], [f"RG-{i:02d}" for i in range(1, 9)])
        self.assertEqual([b["id"] for b in blockers], [f"BLK-{i:02d}" for i in range(1, 7)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])

    def test_absence_all_missing(self) -> None:
        absence = reference.absence_probes()
        self.assertTrue(absence["all_absent"])
        self.assertEqual(absence["present_count"], 0)
        self.assertEqual(absence["probe_count"], 20)

    def test_declaration_rejections(self) -> None:
        schema = reference.asset_declaration_schema()
        self.assertTrue(schema["all_rejected"])
        self.assertTrue(schema["strict_json_all_rejected"])
        self.assertGreaterEqual(schema["rejection_cases"], 40)
        self.assertGreaterEqual(schema["strict_json_cases"], 9)
        reference.validate_asset_declaration(reference.unpopulated_asset_declaration())

    def test_reject_bad_declaration_presence_claim(self) -> None:
        bad = reference.unpopulated_asset_declaration()
        bad["weights"]["declared_present"] = True
        with self.assertRaises(ValueError):
            reference.validate_asset_declaration(bad)

    def test_scope_base_behavior(self) -> None:
        base, paths = reference.committed_paths_since_base(reference.WORKTREE)
        # base may be None in detached environments, but function must not crash
        self.assertTrue(base is None or isinstance(base, str))
        self.assertIsInstance(paths, list)

    def test_run_regenerates_byte_identically(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pvntp-test-") as tmp:
            temp_dir = Path(tmp) / HERE.name
            import shutil
            shutil.copytree(HERE, temp_dir)
            proc = subprocess.run([sys.executable, str(temp_dir / "run.py"), "all"],
                                  capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("byte_identical=true", proc.stdout)
            for name in sorted(reference.EXPECTED_DIR_FILES):
                self.assertEqual((HERE / name).read_bytes(), (temp_dir / name).read_bytes(), name)

    def test_strict_json_rejects_duplicate_keys(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')


if __name__ == "__main__":
    unittest.main()
