# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local PulseVAD blocker package."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import reference

HERE = Path(__file__).resolve().parent


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest_fixture(root: Path) -> dict:
    runtime = root / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    files = {
        "config_path": b"{}",
        "model_path": b"pulsevad.onnx",
        "rights_record_path": b"rights",
        "terms_record_path": b"terms",
    }
    manifest = {
        "channels": reference.CONTROL_CHANNELS,
        "runtime_path": str(runtime),
        "source_revision": "0" * 40,
        "variant": reference.CALLER_VARIANT,
    }
    for field, data in files.items():
        path = root / (field.replace("_path", "") + ".bin")
        path.write_bytes(data)
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = _sha(data)
    return manifest


class JsonAndCanonicalTests(unittest.TestCase):
    def test_canonical_json_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"value": math.nan})

    def test_strict_json_rejects_duplicate_key(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_infinity(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":Infinity}')

    def test_canonical_normalizes_negative_zero(self) -> None:
        self.assertEqual(reference.canonical_bytes({"z": -0.0}), b'{"z":0.0}')

    def test_fraction_text(self) -> None:
        self.assertEqual(reference.fraction_text(reference.Fraction(2, 1)), "2")
        self.assertEqual(reference.fraction_text(reference.Fraction(2, 3)), "2/3")


class SourceAuditTests(unittest.TestCase):
    def test_absence_probes_all_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertEqual(len(audit["absence_probes"]), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(item["exists"] is False for item in audit["absence_probes"]))

    def test_no_runtime_or_rights(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["runtime_present"])
        self.assertFalse(audit["asset_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])
        self.assertFalse(audit["approved_runtime_available"])
        self.assertFalse(audit["source_revision_pinned"])
        self.assertFalse(audit["vendor_terms_reviewed"])


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"], reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "feasibility")
        self.assertFalse(identity["whole_file_hashed"])
        self.assertEqual(identity["claim"]["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(identity["claim"]["branch"], reference.BRANCH)
        expected = _sha(reference.canonical_bytes(identity["stable_fields"]))
        self.assertEqual(identity["stable_sha256"], expected)

    def test_mutable_fields_excluded(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(set(identity["excluded_mutable_fields"]), set(reference.MUTABLE_TASK_FIELDS))
        for field in reference.MUTABLE_TASK_FIELDS:
            self.assertNotIn(field, identity["stable_fields"])


class PcmTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        self.assertEqual(reference.synthetic_input_pcm(), reference.synthetic_input_pcm())
        self.assertEqual(len(reference.synthetic_input_pcm()), reference.CONTROL_SAMPLES)

    def test_pcm_summary(self) -> None:
        summary = reference.pcm_summary(reference.synthetic_input_pcm(), reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertEqual(summary["duration_s"], "1")
        self.assertEqual(summary["channels"], 1)
        self.assertEqual(summary["sample_rate_hz"], 16000)

    def test_validate_pcm_rejects_invalid(self) -> None:
        cases = [
            lambda: reference.validate_pcm([]),
            lambda: reference.validate_pcm(b"ab"),
            lambda: reference.validate_pcm(None),
            lambda: reference.validate_pcm([0.0], 8000),
            lambda: reference.validate_pcm([0.0], 16000, 2),
            lambda: reference.validate_pcm([math.nan]),
            lambda: reference.validate_pcm([math.inf]),
            lambda: reference.validate_pcm([-math.inf]),
            lambda: reference.validate_pcm([1.5]),
            lambda: reference.validate_pcm([True]),
            lambda: reference.validate_pcm(["0.1"]),
        ]
        for action in cases:
            with self.assertRaises(reference.Reject):
                action()


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_complete_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["runtime_executed"])

    def test_manifest_rejects_missing_or_bad_hash(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["model_path"]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["model_path"]).write_bytes(b"tampered")
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_extra_field(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["access_key"] = "secret"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_bad_revision(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["source_revision"] = "main"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)


class AdverseAndReportTests(unittest.TestCase):
    def test_adverse_controls_all_rejected(self) -> None:
        controls = reference.run_adverse_controls()
        self.assertEqual(len(controls), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual([c["case"] for c in controls], list(reference.ADVERSE_CASE_IDS))
        self.assertEqual([c for c in controls if c["result"] != "rejected"], [])

    def test_build_report_defer_shape(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertTrue(report["qualification"]["no_missing_result_qualifies_candidate"])
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))
        self.assertEqual(len(report["exact_blockers"]), 8)
        self.assertIsNone(report["candidate_metrics"])
        self.assertFalse(report["scope"]["model_executed"])
        self.assertFalse(report["scope"]["vendor_runtime_invoked"])
        self.assertTrue(report["controls"]["adverse_all_rejected"])

    def test_contract_matches_report(self) -> None:
        report = reference.build_report()
        contract = reference.build_contract()
        self.assertEqual(contract["schema_id"], reference.CONTRACT_SCHEMA_ID)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification"], report["qualification"])
        self.assertEqual(contract["gates"], report["gates"])
        self.assertEqual(contract["exact_blockers"], report["exact_blockers"])
        self.assertEqual(contract["task_row_identity"], report["task_row_identity"])
        self.assertEqual(contract["caller_asset_contract"], report["caller_asset_contract"])

    def test_report_is_canonical(self) -> None:
        report = reference.build_report()
        payload = reference.canonical_report_bytes(report)
        self.assertTrue(payload.endswith(b"\n"))
        json.loads(payload.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
