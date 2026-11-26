# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for SpatialNet task-local evidence package."""

from __future__ import annotations

import unittest

import reference


class TestSpatialNetEvidence(unittest.TestCase):
    def test_board_identity(self) -> None:
        link = reference.board_link()
        self.assertEqual(link["stable_sha256"], reference.BOARD_STABLE_SHA256)
        self.assertFalse(link["full_tasks_json_hashed"])

    def test_source_lines_present(self) -> None:
        lines = reference.source_lines()
        self.assertEqual(lines["line_count"], 4)
        ids = [e["id"] for e in lines["entries"]]
        self.assertEqual(ids, ["inventory-blocker", "candidate-matrix", "spatial-trials", "spatial-profile"])

    def test_report_contract_canonical(self) -> None:
        report = reference.report_bytes()
        sidecar = reference.sidecar_bytes(report)
        sources = reference.sources_bytes(report, sidecar)
        obj = reference.strict_loads(report.decode("utf-8"))
        contract = reference.contract_bytes(report, sidecar, sources, obj)
        self.assertEqual(obj["decision"], "DEFER")
        self.assertEqual(obj["evidence_status"], "incomplete")
        self.assertEqual(obj["qualification_status"], "not_qualified")
        self.assertTrue(obj["adverse"]["all_rejected"])
        self.assertTrue(obj["no_missing_result_qualifies_candidate"])
        self.assertEqual(len(obj["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" and g["qualifies"] is False for g in obj["gates"]))
        cobj = reference.strict_loads(contract.decode("utf-8"))
        self.assertEqual(cobj["schema_id"], reference.SCHEMA_CONTRACT)
        self.assertEqual(cobj["report_sha256"], reference.sha256_bytes(report))

    def test_synthetic_control_not_qualifying(self) -> None:
        ctrl = reference.synthetic_control()
        self.assertTrue(ctrl["all_peaks_aligned"])
        self.assertFalse(ctrl["qualifies"])
        self.assertTrue(ctrl["not_spatialnet"])

    def test_adverse_cases_rejected(self) -> None:
        missing = reference.missing_asset_adverse()
        self.assertTrue(missing["all_rejected"])
        self.assertEqual(missing["accepted_count"], 0)

    def test_invalid_json_and_pins(self) -> None:
        self.assertTrue(reference.invalid_json_cases()["all_rejected"])
        self.assertTrue(reference.invalid_pin_cases()["all_rejected"])

    def test_scope_violations(self) -> None:
        self.assertEqual(reference.scope_violations([reference.TASK_PREFIX + "README.md"]), [])
        self.assertEqual(reference.scope_violations(["README.md"]), ["README.md"])


if __name__ == "__main__":
    unittest.main()
