# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-URGENT-BSRNN blocker evidence."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run  # noqa: E402


class UrgentBsrnnEvidenceTests(unittest.TestCase):
    def test_canonical_report_repeatable(self):
        a = reference.canonical_bytes(reference.build_report())
        b = reference.canonical_bytes(reference.build_report())
        self.assertEqual(a, b)

    def test_report_digest_matches_sidecar(self):
        run.main(["all"])
        report = reference.load_strict_json(HERE / "report.json")
        digest = reference.report_digest(report)
        sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
        self.assertEqual(sidecar, digest + "  report.json")

    def test_decision_and_gates(self):
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["qualified"])
        self.assertEqual(len(report["release_gates"]), 8)
        for gate in report["release_gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])

    def test_no_mutable_board_hash(self):
        contract = reference.build_contract()
        self.assertFalse(contract["linked_row_identity"]["mutable_board_hash_used"])
        proj = contract["linked_row_identity"]["projection"]
        for forbidden in ["status", "owner", "claim", "review", "handoff", "blocked_reason", "dispatch_priority"]:
            self.assertNotIn(forbidden, proj)

    def test_absence_probes_fixed(self):
        report = reference.build_report()
        self.assertTrue(report["absence_summary"]["all_absent"])
        self.assertGreaterEqual(report["absence_summary"]["probe_count"], 10)

    def test_strict_json_rejects_duplicate_float_nonfinite(self):
        with self.assertRaises(reference.ReferenceError):
            reference.loads_strict('{"a":1,"a":2}')
        with self.assertRaises(reference.ReferenceError):
            reference.loads_strict('{"a":1.5}')
        with self.assertRaises(reference.ReferenceError):
            reference.loads_strict("[NaN]")
        with self.assertRaises(reference.ReferenceError):
            reference.loads_strict("[Infinity]")

    def test_source_pins_present(self):
        pins = reference.actual_source_pins()
        for k in reference.PLAN_PINS:
            self.assertIn(k, pins)
        self.assertIn("linked-row:SDK-URGENT-BSRNN", pins)

    def test_verify_script_passes(self):
        run.main(["all"])
        proc = subprocess.run(
            [sys.executable, str(HERE / "verify.py")],
            cwd=str(reference.WORKTREE),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS verify.py", proc.stdout)


if __name__ == "__main__":
    unittest.main()
