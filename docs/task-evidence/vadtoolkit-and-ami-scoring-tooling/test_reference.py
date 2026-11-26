# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for VADToolkit/AMI scoring tooling blocker evidence."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import reference


class JsonTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_nan(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":NaN}')

    def test_canonical_bytes_reject_nonfinite(self) -> None:
        with self.assertRaises(Exception):
            reference.canonical_bytes({"a": float("inf")})


class IdentityTests(unittest.TestCase):
    def test_linked_row_identity(self) -> None:
        identity = reference.task_row_identity()
        self.assertIs(identity["whole_file_hashed"], False)
        self.assertEqual(identity["stable_sha256"], reference.TASK_ROW_STABLE_SHA256)
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertNotIn("owner", identity["stable_fields"])
        self.assertIn("owner", identity["excluded_mutable_fields"])

    def test_no_tasks_json_digest_in_report(self) -> None:
        payload = reference.canonical_report_bytes(reference.build_report()).decode("utf-8")
        self.assertNotIn('"plan/swarm/TASKS.json":', payload)
        self.assertNotIn('TASKS.json": "', payload)


class ScoringControlTests(unittest.TestCase):
    def test_control_case_deterministic(self) -> None:
        a = reference.score_case(reference.CONTROL_CASE)
        b = reference.score_case(reference.CONTROL_CASE)
        self.assertEqual(a, b)
        self.assertEqual(a["unknown_samples"], 4)
        self.assertEqual(a["weak_scored_samples"], 0)
        self.assertEqual(a["weak_outside_scored_samples"], 4)
        self.assertEqual(a["tp"], 2)
        self.assertEqual(a["fn"], 2)
        self.assertEqual(a["fp"], 2)
        self.assertEqual(a["tn"], 6)
        self.assertAlmostEqual(a["speech_miss_rate"], 0.5)
        self.assertAlmostEqual(a["false_alarm_rate"], 0.25)

    def test_unknown_never_nonspeech(self) -> None:
        result = reference.score_case(reference.CONTROL_CASE)
        self.assertTrue(result["unknown_never_nonspeech"])
        self.assertEqual(result["scored_samples"] + result["unknown_samples"], result["total_samples"])

    def test_weak_labels_separated(self) -> None:
        result = reference.score_case(reference.CONTROL_CASE)
        self.assertTrue(result["weak_labels_never_accuracy_reference"])
        self.assertGreater(result["weak_outside_scored_samples"], 0)

    def test_adverse_all_rejected(self) -> None:
        adverse = reference.run_adverse_controls()
        self.assertGreaterEqual(len(adverse), 14)
        self.assertTrue(all(x["result"] == "rejected" for x in adverse))


class ReportTests(unittest.TestCase):
    def test_report_invariants(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["profile"], "evidence")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIs(report["qualification"]["candidate_qualified"], False)
        self.assertIs(report["qualification"]["no_missing_result_qualifies_candidate"], True)
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))
        self.assertEqual(len(report["exact_blockers"]), 8)
        self.assertIs(report["boundary"]["registered"], False)
        self.assertIs(report["boundary"]["enabled_by_default"], False)
        self.assertEqual(report["boundary"]["descriptor_settings"], {})
        self.assertIs(report["scope"]["real_corpus"], False)
        self.assertIs(report["scope"]["network_used"], False)
        self.assertIs(report["task_row_identity"]["whole_file_hashed"], False)
        self.assertEqual(report["source_reported_context"]["label"], "source_reported_not_measured_here")
        self.assertTrue(report["controls"]["adverse_all_rejected"])
        self.assertEqual(report["asset_audit"]["audit_result"], "absent")
        self.assertIs(report["asset_audit"]["qualified"], False)

    def test_report_byte_stable(self) -> None:
        a = reference.canonical_report_bytes(reference.build_report())
        b = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(b"\n"))

    def test_contract_matches_identity(self) -> None:
        contract = json.loads((reference.HERE / "contract.json").read_text())
        self.assertEqual(contract["task_row_identity"]["stable_sha256"], reference.TASK_ROW_STABLE_SHA256)
        self.assertIs(contract["task_row_identity"]["whole_file_hashed"], False)
        self.assertEqual(contract["qualification"]["status"], "not_qualified")


if __name__ == "__main__":
    unittest.main()
