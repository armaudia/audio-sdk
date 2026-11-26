# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SDK-PAULSTRETCH blocker evidence."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

import reference

HERE = Path(__file__).resolve().parent


class PaulstretchEvidenceTests(unittest.TestCase):
    def test_inventory_and_board_identity(self):
        self.assertEqual(reference.inventory_row(), reference.EXPECTED_INVENTORY)
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_evidence_entry_exact(self):
        entry = reference.evidence_entry()
        self.assertEqual(entry["line"], 281)
        self.assertIn("GPL", entry["text"])
        self.assertIn("extreme offline stretching", entry["text"])

    def test_source_runtime_weights_absent(self):
        self.assertFalse(reference.source_probe()["present"])
        self.assertFalse(reference.runtime_probe()["present"])
        self.assertFalse(reference.weights_probe()["present"])

    def test_adverse_cases_fail_closed(self):
        adverse = reference.adverse_cases()
        self.assertTrue(adverse["invalid_config_and_input"]["all_rejected"])
        self.assertTrue(adverse["invalid_json_numeric_fields"]["all_rejected"])
        self.assertFalse(adverse["missing_result"]["qualifies_candidate"])
        self.assertTrue(adverse["reset_validation"]["matches_expectation"])

    def test_report_shape_and_decision(self):
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertEqual(report["qualification"]["readiness"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(len(report["release_gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["release_gates"]))
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        self.assertFalse(report["reference"]["candidate_processing"])
        self.assertFalse(report["reference"]["real_paulstretch_executed"])

    def test_stimulus_identity_control(self):
        probe = reference.stimulus_probe()
        self.assertFalse(probe["candidate_processing"])
        self.assertTrue(all(v["byte_identical"] for v in probe["identity_control"].values()))

    def test_canonical_bytes_stable(self):
        b1 = reference.report_bytes()
        b2 = reference.report_bytes()
        self.assertEqual(b1, b2)
        report = json.loads(b1.decode("utf-8"))
        self.assertEqual(report["task"], reference.TASK)


if __name__ == "__main__":
    unittest.main()
