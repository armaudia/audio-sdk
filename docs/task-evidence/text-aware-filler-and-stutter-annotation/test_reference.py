#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

import reference  # noqa: E402


class TestReference(unittest.TestCase):
    def test_task_row_identity_stable(self):
        ident = reference.task_row_identity()
        self.assertFalse(ident["full_tasks_json_hashed"])
        self.assertFalse(ident["whole_file_hashed"])
        self.assertEqual(ident["stable_fields"]["id"], reference.TASK_ID)

    def test_source_and_boundary_pins(self):
        self.assertEqual(len(reference.verify_source_pins()), len(reference.SOURCE_PINS))
        self.assertEqual(len(reference.verify_boundary_pins()), len(reference.BOUNDARY_PINS))

    def test_absence_probes(self):
        probes = reference.absence_probes()
        self.assertGreaterEqual(len(probes), 8)
        self.assertTrue(all(not p["exists"] for p in probes))

    def test_identity_control(self):
        ident = reference.identity_control()
        self.assertTrue(ident["digest_equal"])
        self.assertEqual(ident["qualification_effect"], "none")

    def test_adverse_cases(self):
        cases = reference.adverse_cases()
        self.assertGreaterEqual(len(cases), 20)
        self.assertTrue(all(c["result"] == "rejected" for c in cases))

    def test_report_contract(self):
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["blocked_gate_count"], 8)
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertFalse(report["qualification"]["candidate_qualified"])
        contract = reference.build_contract(report)
        self.assertEqual(contract["schema_id"], reference.CONTRACT_SCHEMA_ID)
        self.assertEqual(contract["blocked_release_gate_count"], 8)

    def test_no_spdx_literal(self):
        for name in ["reference.py", "run.py", "verify.py", "test_reference.py"]:
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("SPDX-License-" + "Identifier:", text.replace(reference.SPDX_ID_LINE, ""))


if __name__ == "__main__":
    unittest.main()
