# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local TokAN evidence package."""

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
    encoder = root / "encoder"
    runtime = root / "runtime"
    encoder.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    files = {
        "arlm_checkpoint_path": b"arlm-weights",
        "quantizer_checkpoint_path": b"quantizer-weights",
        "hift_checkpoint_path": b"hift-weights",
        "encoder_cache_manifest_path": b"encoder-manifest",
        "config_path": b"sample_rate: 24000\n",
        "license_record_path": b"license-record",
        "runtime_lock_path": b"torch==0.0.0\n",
        "speaker_reference_path": b"RIFF-reference",
        "consent_record_path": b"consent-record",
    }
    manifest = {
        "channels": reference.CHANNELS,
        "encoder_cache_path": str(encoder),
        "runtime_path": str(runtime),
        "sample_rate_input_hz": reference.INPUT_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": reference.OUTPUT_SAMPLE_RATE_HZ,
        "source_revision": reference.TOKAN_COMMIT,
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
    def test_source_checkout_is_exact(self) -> None:
        audit = reference.audit_assets()
        self.assertTrue(audit["source_checkout_present"])
        self.assertEqual(audit["source_revision"], reference.TOKAN_COMMIT)
        self.assertTrue(audit["source_revision_matches"])
        self.assertTrue(audit["source_file_pins_match"])
        self.assertEqual(audit["source_file_mismatches"], [])
        self.assertGreaterEqual(audit["source_files_checked"], 9)

    def test_license_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["license_file_present"])
        self.assertEqual(audit["license_files"], [])

    def test_weights_and_runtime_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["all_checkpoints_present"])
        self.assertEqual(
            set(audit["checkpoints_present"]), set(reference.CHECKPOINT_FILENAMES))
        self.assertTrue(all(value is False
                            for value in audit["checkpoints_present"].values()))
        self.assertFalse(audit["wavlm_cache_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])

    def test_three_demo_clips_only(self) -> None:
        audit = reference.audit_assets()
        self.assertEqual(audit["sample_clip_count"], 3)
        self.assertEqual(len(audit["sample_clips"]), 3)

    def test_requested_geometry(self) -> None:
        config = reference.audit_assets()["requested_config"]
        self.assertEqual(config["input_sample_rate_hz"], 16000)
        self.assertEqual(config["output_sample_rate_hz"], 24000)
        self.assertEqual(config["channels"], 1)
        self.assertEqual(config["hop_size"], 480)
        self.assertEqual(config["feature_dim"], 80)
        self.assertEqual(config["wavlm_layer"], 22)
        self.assertEqual(config["beam_size"], 10)
        self.assertEqual(config["flow_steps"], 32)


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"], reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "implementation")
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
        self.assertRegex(reference.TOKAN_COMMIT, r"^[0-9a-f]{40}$")
        self.assertRegex(reference.BASE_COMMIT, r"^[0-9a-f]{40}$")


class PcmTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        first = reference.synthetic_source_pcm()
        second = reference.synthetic_source_pcm()
        self.assertEqual(first, second)
        self.assertEqual(len(first), reference.CONTROL_SOURCE_SAMPLES)
        self.assertEqual(len(reference.synthetic_output_pcm()),
                         reference.CONTROL_OUTPUT_SAMPLES)

    def test_synthetic_pcm_is_finite_and_bounded(self) -> None:
        source = reference.validate_pcm(
            reference.synthetic_source_pcm(), reference.INPUT_SAMPLE_RATE_HZ)
        output = reference.validate_pcm(
            reference.synthetic_output_pcm(), reference.OUTPUT_SAMPLE_RATE_HZ)
        self.assertTrue(all(math.isfinite(value) for value in source))
        self.assertTrue(all(math.isfinite(value) for value in output))
        self.assertLessEqual(max(abs(v) for v in source), 1.0)
        self.assertLessEqual(max(abs(v) for v in output), 1.0)

    def test_pcm_summary_is_deterministic(self) -> None:
        signal = reference.synthetic_source_pcm()
        first = reference.pcm_summary(signal, reference.INPUT_SAMPLE_RATE_HZ)
        second = reference.pcm_summary(signal, reference.INPUT_SAMPLE_RATE_HZ)
        self.assertEqual(first, second)
        self.assertEqual(first["duration_s"], "3")
        self.assertEqual(first["channels"], 1)

    def test_validate_pcm_accepts_integers(self) -> None:
        self.assertEqual(reference.validate_pcm([0, 0.5, -1]), [0.0, 0.5, -1.0])

    def test_validate_pcm_rejects_invalid(self) -> None:
        cases = [
            lambda: reference.validate_pcm([]),
            lambda: reference.validate_pcm(b"ab"),
            lambda: reference.validate_pcm(None),
            lambda: reference.validate_pcm([0.0], 8000),
            lambda: reference.validate_pcm([0.0], reference.INPUT_SAMPLE_RATE_HZ, 2),
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

    def test_duration_accounting_exact(self) -> None:
        result = reference.duration_accounting(
            reference.CONTROL_SOURCE_SAMPLES, reference.CONTROL_OUTPUT_SAMPLES)
        self.assertEqual(result["source_duration_s"], "3")
        self.assertEqual(result["output_duration_s"], "2")
        self.assertEqual(result["duration_ratio"], "2/3")

    def test_duration_accounting_rejects_bad_counts(self) -> None:
        for value in (0, -1, True, 1.5, "4"):
            with self.assertRaises(reference.Reject):
                reference.duration_accounting(value, 1)
            with self.assertRaises(reference.Reject):
                reference.duration_accounting(1, value)

    def test_alignment_is_offline(self) -> None:
        alignment = reference.alignment_accounting(48000)
        self.assertEqual(alignment["mode"], "offline_whole_utterance")
        self.assertFalse(alignment["streaming_supported"])
        self.assertTrue(alignment["whole_clip_required"])
        self.assertEqual(alignment["tail_samples"], 48000)


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_complete_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["source_revision"], reference.TOKAN_COMMIT)
        self.assertEqual(result["files_checked"], len(reference.CALLER_FILE_PAIRS))
        self.assertFalse(result["model_executed"])

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["hift_checkpoint_path"]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["arlm_checkpoint_path"]).write_bytes(b"tampered")
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
            manifest["config_path"] = "config.yaml"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_revision(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["source_revision"] = "0" * 40
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_streaming_variant(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["variant"] = "incremental_streaming"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_float_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["channels"] = 1.0
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)


class AdverseControlTests(unittest.TestCase):
    def test_all_adverse_cases_are_invoked_and_rejected(self) -> None:
        results = reference.run_adverse_controls()
        self.assertEqual(len(results), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual([item["case"] for item in results],
                         list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(item["result"] == "rejected" for item in results))

    def test_control_is_labelled_synthetic(self) -> None:
        control = reference.build_control()
        self.assertEqual(control["plan_source"],
                         reference.CONTROL_PLAN_PROVENANCE)
        self.assertFalse(control["model_executed"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(control["duration"]["duration_ratio"], "2/3")
        self.assertFalse(control["alignment"]["streaming_supported"])

    def test_acceptance_outcomes_are_all_unmeasured(self) -> None:
        control = reference.build_control()
        self.assertEqual(len(control["acceptance_outcomes"]), 4)
        self.assertTrue(all(item["measured"] is False
                            and item["value"] is None
                            for item in control["acceptance_outcomes"]))


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = json.loads((HERE / "contract.json").read_text())

    def test_top_level_decision(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["profile"], "voice")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIsNone(report["candidate_metrics"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual(
            [gate["id"] for gate in gates],
            [gate for gate, _ in reference.GATE_REQUIREMENTS])

    def test_eight_exact_blockers(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 8)
        self.assertTrue(all(item["state"] == "absent" for item in blockers))
        self.assertIn("source_license_absent",
                      [item["id"] for item in blockers])

    def test_qualification_blocked(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(qualification["no_missing_result_qualifies_candidate"])
        self.assertEqual(qualification["blocked_gate_count"], 8)

    def test_boundary_is_closed(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "production_callback_registered", "descriptor_registry_change",
                    "shared_build_or_ci_change", "installed_v0_behavior_change",
                    "asset_bundled", "weights_vendored", "sdk_callback_invoked",
                    "network_used"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_is_closed(self) -> None:
        scope = self.report["scope"]
        for key in ("real_audio", "real_corpus", "real_tokan_model",
                    "model_executed", "weights_loaded", "weights_downloaded",
                    "runtime_invoked", "vendor_runtime_invoked", "network_used",
                    "device_timing", "listening", "public_benchmark",
                    "release_claim"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["task_local_only"], True)

    def test_weight_requirements_have_no_fabricated_hash(self) -> None:
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertIsNone(requirements["arlm_checkpoint"]["sha256"])
        self.assertIsNone(requirements["quantizer_flow_checkpoint"]["sha256"])
        self.assertIsNone(requirements["hift_checkpoint"]["sha256"])
        self.assertIsNone(requirements["wavlm_large_encoder"]["sha256"])
        self.assertIsNone(requirements["exact_runtime"]["runtime_lock_sha256"])

    def test_voice_profile_has_no_satisfied_item(self) -> None:
        profile = self.report["voice_profile"]
        self.assertEqual(profile["name"], "voice")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_model_metrics"])
        self.assertTrue(all(item["qualification_effect"] == "none"
                            for item in profile["required_items"]))

    def test_audit_is_not_qualified(self) -> None:
        audit = self.report["asset_audit"]
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["audit_result"],
                         "source_present_assets_unqualified")
        self.assertTrue(audit["source_revision_matches"])
        self.assertFalse(audit["license_present"])
        self.assertFalse(audit["all_checkpoints_present"])
        self.assertFalse(audit["wavlm_cache_present"])

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_source_reported_context_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"], "source_reported_not_measured_here")
        self.assertEqual(len(context["clips"]), 3)

    def test_missing_artifacts_recorded(self) -> None:
        self.assertIn(reference.MISSING_WEIGHTS_PATH,
                      self.report["missing_historical_artifacts"])
        self.assertIn(reference.COHORT_MANIFEST_PATH,
                      self.report["missing_historical_artifacts"])

    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_report_bytes(reference.build_report())
        second = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)

    def test_on_disk_report_matches_generator(self) -> None:
        expected = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual((HERE / "report.json").read_bytes(), expected)

    def test_sidecar_matches_report(self) -> None:
        expected = reference.canonical_report_bytes(reference.build_report())
        digest = _sha(expected)
        sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8")
        self.assertEqual(sidecar, f"{digest}  report.json\n")

    def test_contract_matches_report(self) -> None:
        contract = self.contract
        report = self.report
        self.assertEqual(contract["task"], report["task_id"])
        self.assertEqual(contract["decision"], report["decision"])
        self.assertEqual(contract["status"], report["status"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertEqual(
            [gate["id"] for gate in contract["gates"]],
            [gate["id"] for gate in report["gates"]])
        self.assertEqual(
            [item["id"] for item in contract["exact_blockers"]],
            [item["id"] for item in report["exact_blockers"]])
        self.assertEqual(
            contract["task_row_identity"]["stable_sha256"],
            report["task_row_identity"]["stable_sha256"])
        self.assertEqual(contract["qualification"]["blocked_gate_count"], 8)

    def test_sources_manifest_has_no_tasks_json(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line and not line.startswith("#"):
                self.assertNotIn("TASKS.json", line)


if __name__ == "__main__":
    unittest.main()
