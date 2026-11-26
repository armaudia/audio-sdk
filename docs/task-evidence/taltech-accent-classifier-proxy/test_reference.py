# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local TalTech accent classifier proxy evidence package."""

from __future__ import annotations

import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class JsonTests(unittest.TestCase):
    def test_canonical_rejects_nonfinite(self):
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"v": math.nan})

    def test_strict_rejects_duplicate_key(self):
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_rejects_infinity(self):
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":Infinity}')

    def test_strict_rejects_trailing(self):
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{}{}')

    def test_strict_rejects_float(self):
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1.5}')


class ManifestTests(unittest.TestCase):
    def test_good_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            manifest = reference._good_manifest_fixture(Path(td))
            self.assertEqual(reference.validate_manifest(manifest), manifest)

    def test_missing_asset_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            manifest = reference._good_manifest_fixture(Path(td))
            Path(manifest["license_record_path"]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_manifest(manifest)

    def test_bad_sha_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            manifest = reference._good_manifest_fixture(Path(td))
            manifest["config_sha256"] = "0" * 64
            with self.assertRaises(reference.Reject):
                reference.validate_manifest(manifest)


class ScoreTests(unittest.TestCase):
    def test_valid_scores(self):
        out = reference.validate_label_scores({"a": 0.2, "b": 0.8})
        self.assertEqual(out["b"], 0.8)

    def test_nan_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.validate_label_scores({"a": math.nan})

    def test_inf_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.validate_label_scores({"a": math.inf})

    def test_negative_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.validate_label_scores({"a": -1})

    def test_zero_total_rejected(self):
        with self.assertRaises(reference.Reject):
            reference.validate_label_scores({"a": 0, "b": 0})

    def test_control_not_qualification(self):
        control = reference.synthetic_label_accounting_control()
        self.assertFalse(control["is_candidate_model_output"])
        self.assertEqual(control["qualification_effect"], "none")
        self.assertTrue(control["classifier_direction_only"])
        self.assertFalse(control["listener_confirmed_accent"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_decision(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")

    def test_eight_gates_blocked(self):
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in gates))
        self.assertEqual(self.report["qualification"]["blocked_gate_count"], 8)

    def test_blockers(self):
        self.assertEqual(len(self.report["exact_blockers"]), 8)

    def test_no_whole_file_tasks_hash(self):
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_proxy_not_taltech_evidence(self):
        ctx = self.report["source_reported_context"]
        self.assertEqual(ctx["label"], "source_reported_not_measured_here")
        self.assertFalse(ctx["treated_as_taltech_evidence"])

    def test_adverse_all_rejected(self):
        controls = self.report["controls"]
        self.assertTrue(controls["adverse_all_rejected"])
        self.assertTrue(all(c["result"] == "rejected" for c in controls["adverse"]))
        self.assertGreaterEqual(len(controls["adverse"]), 19)

    def test_scope_boundary(self):
        for key, value in self.report["boundary"].items():
            if isinstance(value, bool):
                self.assertFalse(value, key)
        for key in ("real_audio", "model_executed", "weights_loaded", "network_used", "device_timing", "listening"):
            self.assertFalse(self.report["scope"][key], key)
        self.assertTrue(self.report["scope"]["task_local_only"])

    def test_deterministic(self):
        a = reference.canonical_report_bytes(reference.build_report())
        b = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(a, b)

    def test_on_disk_matches(self):
        expected = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual((HERE / "report.json").read_bytes(), expected)
        digest = _sha(expected)
        self.assertEqual((HERE / "report.json.sha256").read_text(encoding="utf-8"), f"{digest}  report.json\n")

    def test_contract_alignment(self):
        contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
        report = self.report
        self.assertEqual(contract["task"], report["task_id"])
        self.assertEqual(contract["decision"], report["decision"])
        self.assertEqual(contract["qualification"]["status"], report["qualification"]["status"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertEqual([g["id"] for g in contract["gates"]], [g["id"] for g in report["gates"]])
        self.assertEqual(contract["task_row_identity"]["stable_sha256"], report["task_row_identity"]["stable_sha256"])

    def test_sources_no_tasks_json(self):
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line and not line.startswith("#"):
                self.assertNotIn("TASKS.json", line)


if __name__ == "__main__":
    unittest.main()
