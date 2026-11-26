# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the deterministic task-local evidence package."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class ReferenceTest(unittest.TestCase):
    def test_report_contract_and_determinism(self) -> None:
        r1 = reference.build_report()
        r2 = reference.build_report()
        b1 = reference.canonical_report_bytes(r1)
        b2 = reference.canonical_report_bytes(r2)
        self.assertEqual(b1, b2)
        self.assertTrue(b1.endswith(b"\n"))
        self.assertEqual(r1["decision"], "DEFER")
        self.assertEqual(r1["evidence_status"], "incomplete")
        self.assertEqual(r1["qualification_status"], "not_qualified")
        self.assertFalse(r1["qualification"]["candidate_qualified"])
        self.assertTrue(r1["qualification"]["no_missing_result_qualifies_candidate"])
        self.assertEqual(r1["qualification"]["blocked_gate_count"], 8)
        self.assertEqual(len(r1["release_gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in r1["release_gates"]))
        self.assertEqual(r1["acceptance_profile"]["profile"], "voice")
        self.assertEqual(r1["acceptance_profile"]["satisfied_for_qualification"], [])
        self.assertEqual(r1["task_row_identity"]["whole_file_hashed"], False)
        self.assertEqual(r1["task_row_identity"]["stable_sha256"],
                         reference.SOURCE_PINS["audio-benchmark-platform/plan/swarm/TASKS.json"])
        contract = reference.build_contract()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["profile"], "voice")

    def test_source_reported_context_is_provenance_only(self) -> None:
        report = reference.build_report()
        ctx = report["source_reported_context"]
        self.assertEqual(ctx["label"], "source_reported_not_measured_here")
        self.assertEqual(ctx["local_run"], "not_run")
        self.assertEqual(ctx["local_checkpoint"], "absent")
        self.assertIn("0.8 s", ctx["finding"])
        self.assertIsNone(report["candidate_metrics"])
        self.assertFalse(report["candidate"]["geometry_documented"])

    def test_asset_audit_absent(self) -> None:
        report = reference.build_report()
        audit = report["asset_audit"]
        self.assertEqual(audit["audit_result"], "absent")
        self.assertFalse(audit["qualified"])
        self.assertTrue(all(not row["qualified"] for row in audit["observed"] if row["kind"] != "sample_data_non_qualifying"))

    def test_surrogate_control_and_adverse(self) -> None:
        control = reference.run_surrogate_control()
        self.assertFalse(control["is_candidate_model_output"])
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(control["source_samples"], 48000)
        self.assertEqual(control["target_samples"], 32000)
        self.assertEqual(control["duration_ratio_target_over_source"], "2/3")
        self.assertFalse(control["alignment"]["incremental_streaming_supported"])
        adverse = reference.adverse_controls()
        self.assertEqual(len(adverse), len(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(a["status"] == "rejected" for a in adverse))
        self.assertTrue(all(a["state_unchanged"] is True for a in adverse))

    def test_manifest_validation_rejects_bad_inputs(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest({})
        with self.assertRaises(reference.Reject):
            reference.validate_pcm([0, float("inf")], "pcm")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            files = {}
            for key in ("config", "consent_record", "license_record", "runtime_lock", "source_archive", "source_reference", "target_reference", "weights"):
                f = p / key
                f.write_bytes(key.encode())
                files[key] = f
            manifest = {
                "channels": 1,
                "config_path": str(files["config"]),
                "config_sha256": reference.file_digest(files["config"]),
                "consent_record_path": str(files["consent_record"]),
                "consent_record_sha256": reference.file_digest(files["consent_record"]),
                "license_record_path": str(files["license_record"]),
                "license_record_sha256": reference.file_digest(files["license_record"]),
                "runtime_lock_path": str(files["runtime_lock"]),
                "runtime_lock_sha256": reference.file_digest(files["runtime_lock"]),
                "runtime_path": str(p),
                "sample_rate_input_hz": 16000,
                "sample_rate_output_hz": 16000,
                "source_archive_path": str(files["source_archive"]),
                "source_archive_sha256": reference.file_digest(files["source_archive"]),
                "source_reference_path": str(files["source_reference"]),
                "source_reference_sha256": reference.file_digest(files["source_reference"]),
                "source_revision": "0123456789abcdef0123456789abcdef01234567",
                "target_reference_path": str(files["target_reference"]),
                "target_reference_sha256": reference.file_digest(files["target_reference"]),
                "variant": "offline_whole_utterance",
                "weights_path": str(files["weights"]),
                "weights_sha256": reference.file_digest(files["weights"]),
            }
            result = reference.validate_caller_manifest(manifest)
            self.assertFalse(result["accepted_for_qualification"])
            self.assertEqual(result["admission_status"], "blocked_no_approved_identity")
            bad = dict(manifest)
            bad["weights_sha256"] = "0" * 64
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(bad)

    def test_sources_bytes_and_strict_json(self) -> None:
        payload = reference.sources_bytes()
        self.assertIn(b"pkg:report.json", payload)
        self.assertIn(b"source:audio-benchmark-platform/plan/swarm/TASKS.json", payload)
        with self.assertRaises((reference.Reject, FileNotFoundError, OSError)):
            reference.load_strict_json(Path("/no/such/file.json"))


if __name__ == "__main__":
    unittest.main()
