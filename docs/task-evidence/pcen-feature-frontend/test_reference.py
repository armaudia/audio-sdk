# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local PCEN evidence package."""

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
    source = root / "source"
    runtime = root / "runtime"
    source.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    files = {
        "checkpoint_path": b"pcen-params",
        "config_path": b"n_mels: 40\n",
        "license_record_path": b"license-record",
        "rights_record_path": b"rights-record",
        "runtime_lock_path": b"numpy==0.0.0\n",
        "cohort_manifest_path": b'{"cohort":"fixture"}',
        "degradation_manifest_path": b'{"degradation":"fixture"}',
        "parity_vector_path": b'{"parity":"fixture"}',
    }
    manifest = {
        "channels": reference.CONTROL_CHANNELS,
        "source_checkout_path": str(source),
        "runtime_path": str(runtime),
        "input_sample_rate_hz": reference.CONTROL_SAMPLE_RATE_HZ,
        "frame_samples": reference.CONTROL_FRAME_SAMPLES,
        "n_mels": reference.CONTROL_N_MELS,
        "source_revision": "a" * 40,
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

    def test_strict_json_rejects_infinity_constant(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":Infinity}')

    def test_strict_json_requires_object(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads("[1,2]")

    def test_canonical_normalizes_negative_zero(self) -> None:
        payload = reference.canonical_bytes({"z": -0.0})
        self.assertEqual(payload, b'{"z":0.0}')

    def test_fraction_text(self) -> None:
        from fractions import Fraction
        self.assertEqual(reference.fraction_text(Fraction(2, 3)), "2/3")
        self.assertEqual(reference.fraction_text(Fraction(6, 3)), "2")


class SourceAuditTests(unittest.TestCase):
    def test_source_checkout_is_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["source_checkout_present"])
        self.assertIsNone(audit["source_revision"])
        self.assertFalse(audit["source_revision_pin_available"])
        self.assertFalse(audit["source_revision_matches"])

    def test_no_license_or_weights(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["license_file_present"])
        self.assertEqual(audit["license_files"], [])
        self.assertFalse(audit["weights_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])

    def test_absence_probes_are_all_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertEqual(len(audit["absence_probes"]),
                         len(reference.ABSENCE_PROBES))
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertEqual(
            [item["path"] for item in audit["absence_probes"]],
            list(reference.ABSENCE_PROBES))
        self.assertTrue(all(item["exists"] is False
                            for item in audit["absence_probes"]))

    def test_geometry_is_unestablished(self) -> None:
        config = reference.audit_assets()["requested_config"]
        self.assertEqual(config["geometry_status"], "unestablished")
        self.assertEqual(config["reported_method"], "per_channel_energy_normalization_feature_frontend")
        self.assertIsNone(config["upstream_revision"])
        self.assertEqual(config["control_input_sample_rate_hz"], 16000)
        self.assertEqual(config["control_n_mels"], 40)


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "feasibility")
        self.assertFalse(identity["whole_file_hashed"])
        self.assertEqual(identity["claim"]["base_commit"],
                         reference.BASE_COMMIT)
        self.assertEqual(identity["claim"]["branch"], reference.BRANCH)
        expected = _sha(reference.canonical_bytes(identity["stable_fields"]))
        self.assertEqual(identity["stable_sha256"], expected)

    def test_mutable_fields_excluded(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(set(identity["excluded_mutable_fields"]),
                         set(reference.MUTABLE_TASK_FIELDS))
        for field in reference.MUTABLE_TASK_FIELDS:
            self.assertNotIn(field, identity["stable_fields"])

    def test_commits_are_full_hex(self) -> None:
        self.assertRegex(reference.BASE_COMMIT, r"^[0-9a-f]{40}$")
        self.assertIsNone(reference.UPSTREAM_REVISION)


class PcmTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        first = reference.synthetic_input_pcm()
        second = reference.synthetic_input_pcm()
        self.assertEqual(first, second)
        self.assertEqual(len(first), reference.CONTROL_SAMPLES)

    def test_synthetic_pcm_is_finite_and_bounded(self) -> None:
        source = reference.validate_pcm(
            reference.synthetic_input_pcm(),
            reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertTrue(all(math.isfinite(value) for value in source))
        self.assertLessEqual(max(abs(v) for v in source), 1.0)

    def test_pcm_summary_is_deterministic(self) -> None:
        signal = reference.synthetic_input_pcm()
        first = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        second = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertEqual(first, second)
        self.assertEqual(first["duration_s"], "1")
        self.assertEqual(first["channels"], 1)

    def test_validate_pcm_accepts_integers(self) -> None:
        self.assertEqual(reference.validate_pcm([0, 0.5, -1]), [0.0, 0.5, -1.0])

    def test_validate_pcm_rejects_invalid(self) -> None:
        cases = [
            lambda: reference.validate_pcm([]),
            lambda: reference.validate_pcm(b"ab"),
            lambda: reference.validate_pcm(None),
            lambda: reference.validate_pcm([0.0], 8000),
            lambda: reference.validate_pcm([0.0], reference.CONTROL_SAMPLE_RATE_HZ, 2),
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


class ShapeLedgerTests(unittest.TestCase):
    def test_shape_ledger_is_exact(self) -> None:
        ledger = reference.pcen_shape_ledger(16000, 16000, 160, 40)
        self.assertEqual(ledger["frame_count"], 100)
        self.assertEqual(ledger["remainder_samples"], 0)
        self.assertEqual(ledger["declared_output_shape"], [100, 40])
        self.assertEqual(ledger["declared_output_values"], 4000)
        self.assertFalse(ledger["pcen_performed"])

    def test_shape_ledger_rejects_invalid(self) -> None:
        for args in ((0, 16000, 160, 40), (16000, 8000, 160, 40),
                     (16000, 16000, 0, 40), (16000, 16000, 160, 0),
                     (16000, 16000, 160.0, 40), (16000, 16000, 160, True)):
            with self.assertRaises(reference.Reject):
                reference.pcen_shape_ledger(*args)


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_complete_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["source_revision"], "a" * 40)
        self.assertFalse(result["revision_pin_available"])
        self.assertEqual(result["files_checked"], len(reference.CALLER_FILE_PAIRS))
        self.assertFalse(result["model_executed"])

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["cohort_manifest_path"]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["checkpoint_path"]).write_bytes(b"tampered")
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["runtime_path"]).rmdir()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["config_path"] = "config.json"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_short_or_nonhex_revision(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["source_revision"] = "7dae8a2"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
            manifest["source_revision"] = "g" * 40
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_variant(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["variant"] = "streaming"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_bad_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["channels"] = 0
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
            manifest = _manifest_fixture(Path(raw))
            manifest["frame_samples"] = 0
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
            manifest = _manifest_fixture(Path(raw))
            manifest["n_mels"] = 0
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
            manifest = _manifest_fixture(Path(raw))
            manifest["input_sample_rate_hz"] = 4000
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)


class AdverseAndReportTests(unittest.TestCase):
    def test_adverse_controls_all_rejected(self) -> None:
        controls = reference.run_adverse_controls()
        self.assertEqual(len(controls), len(reference.ADVERSE_CASE_IDS))
        bad = [c for c in controls if c["result"] != "rejected"]
        self.assertEqual(bad, [])
        self.assertEqual([c["case"] for c in controls], list(reference.ADVERSE_CASE_IDS))

    def test_build_report_defer_shape(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertTrue(report["qualification"]["no_missing_result_qualifies_candidate"])
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(g["status"] == "blocked" for g in report["gates"]))
        self.assertIsNone(report["candidate_metrics"])
        self.assertFalse(report["scope"]["model_executed"])
        self.assertFalse(report["scope"]["pcen_performed"])
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

    def test_report_is_canonical(self) -> None:
        report = reference.build_report()
        payload = reference.canonical_report_bytes(report)
        self.assertTrue(payload.endswith(b"\n"))
        self.assertEqual(json.loads(payload.decode("utf-8")), json.loads(payload.decode("utf-8")))


if __name__ == "__main__":
    unittest.main()
