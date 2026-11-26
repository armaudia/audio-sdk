# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the PBFDAF/AUMDF blocker evidence package."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class ReferenceTests(unittest.TestCase):
    def test_task_row_identity_ignores_mutable_fields(self):
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertFalse(identity["whole_file_hashed"])
        self.assertIn("owner", identity["excluded_mutable_fields"])
        self.assertIn("status", identity["excluded_mutable_fields"])
        self.assertEqual(len(identity["stable_sha256"]), 64)

    def test_audit_reports_absence(self):
        observed = reference.audit_assets()
        self.assertTrue(observed["all_absence_probes_absent"])
        self.assertFalse(observed["source_checkout_present"])
        self.assertFalse(observed["weights_present"])
        self.assertFalse(observed["rights_record_present"])
        self.assertFalse(observed["cohort_manifest_present"])

    def test_pcm_validation_rejects_invalid(self):
        with self.assertRaises(reference.Reject):
            reference.validate_pcm_input([], 16000, 1)
        with self.assertRaises(reference.Reject):
            reference.validate_pcm_input([float("nan")], 16000, 1)
        with self.assertRaises(reference.Reject):
            reference.validate_pcm_input([0.0], 8000, 1)

    def test_manifest_validation_rejects_missing_asset(self):
        manifest = {
            "schema_id": "audio-sdk/pbfdaf-aumdf/caller-supplied/0.1",
            "candidate": reference.COMPONENT,
            "source_revision": "0" * 40,
            "source_sha256": "1" * 64,
            "runtime_lock_path": "/no/such/runtime.lock",
            "runtime_lock_sha256": "2" * 64,
            "rights_record_path": "/no/such/rights.json",
            "rights_record_sha256": "3" * 64,
            "cohort_manifest_path": "/no/such/cohort.json",
            "cohort_manifest_sha256": "4" * 64,
            "sample_rate_hz": 16000,
            "channels": 1,
            "block_samples": 160,
            "partitions": 4,
            "variant": "partitioned_block_frequency_domain_aec",
        }
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest(manifest)

    def test_adverse_cases_all_rejected(self):
        adverse = reference.run_adverse_cases()
        self.assertEqual(len(adverse), len(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(c["result"] == "rejected" for c in adverse))
        self.assertTrue(all(c["state_unchanged"] for c in adverse))

    def test_control_is_synthetic_and_bounded(self):
        control = reference.build_control()
        self.assertFalse(control["output_is_real_aec"])
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(control["total_samples"], 48000)
        self.assertEqual(control["blocks"], 300)
        self.assertTrue(control["adverse_all_rejected"])

    def test_report_contract_defer_not_qualified(self):
        report = reference.build_report()
        contract = reference.build_contract()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))

    def test_no_whole_tasks_json_digest_in_report(self):
        payload = reference.canonical_report_bytes(reference.build_report()).decode("utf-8")
        self.assertNotIn("3154212165862651640b2388b4ce8dd62b5a71ad808152820f9b3831488beb89", payload)
        self.assertIn('"whole_file_hashed":false', payload)

    def test_run_report_check_is_deterministic(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            cmd = [sys.executable, str(HERE / "run.py"), "report.json", "--out", str(out)]
            r1 = subprocess.run(cmd, cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
            self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
            b1 = (out / "report.json").read_bytes()
            r2 = subprocess.run(cmd, cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            b2 = (out / "report.json").read_bytes()
            self.assertEqual(b1, b2)
            chk = subprocess.run(cmd + ["--check"], cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
            self.assertEqual(chk.returncode, 0, chk.stdout + chk.stderr)


if __name__ == "__main__":
    unittest.main()
