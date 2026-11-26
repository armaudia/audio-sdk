# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for VoiceBank+DEMAND/VOiCES/DNS5 blocker evidence."""

from __future__ import annotations

import json
import unittest

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
        self.assertNotIn('TASKS.json": "', payload)


class TrackControlTests(unittest.TestCase):
    def test_control_tracks_deterministic(self) -> None:
        a = reference.evaluate_tracks(reference.CONTROL_TRACKS)
        b = reference.evaluate_tracks(reference.CONTROL_TRACKS)
        self.assertEqual(a, b)
        self.assertEqual(a["track_count"], 3)
        self.assertTrue(a["all_blocked"])
        self.assertFalse(a["pooled_ranking"])
        self.assertTrue(a["acquisition_only_never_scorable"])

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
        self.assertTrue(report["controls"]["tracks_separate"])
        self.assertTrue(report["controls"]["acquisition_only_never_scorable"])
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
