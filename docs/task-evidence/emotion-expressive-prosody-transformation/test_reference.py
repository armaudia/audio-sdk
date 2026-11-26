# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local emotion/expressive-prosody package.

No network, no skips and no candidate asset. The tests exercise strict JSON,
the fixed-path absence audit, the deterministic identity-prosody control,
fail-closed target admission, adverse rejection, determinism and the
non-qualification invariants.
"""

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


def _manifest_fixture(root: Path) -> dict:
    source = root / "source"
    runtime = root / "runtime"
    source.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    files = {
        "checkpoint_path": b"prosody-weights",
        "model_config_path": b"model: prosody\n",
        "emotion_label_set_path": b"identity,calm,joyful\n",
        "style_conditioning_path": b"style-conditioning",
        "target_voice_reference_path": b"RIFF-target",
        "target_voice_consent_path": b"consent-record",
        "rights_record_path": b"rights-record",
        "runtime_lock_path": b"torch==0.0.0\n",
    }
    manifest = {
        "asset_storage": "external",
        "channels": reference.CHANNELS,
        "comparison_baseline": reference.COMPARISON_BASELINE,
        "source_checkout_path": str(source),
        "runtime_path": str(runtime),
        "sample_rate_input_hz": reference.SAMPLE_RATE_HZ,
        "sample_rate_output_hz": reference.SAMPLE_RATE_HZ,
        "source_revision": "a" * 40,
        "target_emotion_label": "calm",
        "target_intensity_milli": 700,
        "task_kind": reference.TASK_KIND,
        "variant": reference.CALLER_VARIANT,
    }
    for field, data in files.items():
        path = root / (field.replace("_path", "") + ".bin")
        path.write_bytes(data)
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = _sha(data)
    return manifest


class StrictJsonTests(unittest.TestCase):
    def test_canonical_text_sorted_compact(self) -> None:
        self.assertEqual(reference.canonical_text({"b": 1, "a": [True, None]}),
                         '{"a":[true,null],"b":1}')

    def test_canonical_rejects_float(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.canonical_text({"value": 0.5})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.load_strict_json_text('{"a":1,"a":2}')
        self.assertIn("duplicate_json_key", caught.exception.code)

    def test_nonfinite_constants_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(reference.ReferenceRejection):
                reference.load_strict_json_text('{"a":' + token + "}")

    def test_bom_and_root_type_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceRejection):
            reference.load_strict_json_text('\ufeff{"a":1}')
        with self.assertRaises(reference.ReferenceRejection):
            reference.load_strict_json_object_text("[1,2]")

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

    def test_all_required_assets_absent(self) -> None:
        audit = reference.audit_assets()
        for key in ("license_file_present", "weights_present",
                    "runtime_env_present", "runtime_lock_present",
                    "rights_record_present", "emotion_label_set_present",
                    "target_voice_consent_present",
                    "cohort_manifest_present", "parity_manifest_present",
                    "reference_audio_present"):
            self.assertFalse(audit[key], key)

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
        self.assertEqual(config["target_condition_status"], "unestablished")
        self.assertEqual(config["task_kind"], reference.TASK_KIND)
        self.assertIsNone(config["upstream_revision"])


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK_ID)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "feasibility")
        self.assertFalse(identity["whole_file_hashed"])
        self.assertFalse(identity["full_tasks_json_hashed"])
        self.assertEqual(identity["claim"]["base_commit"],
                         reference.BASE_COMMIT)
        self.assertEqual(identity["claim"]["branch"], reference.BRANCH)
        expected = _sha(reference.canonical_text(
            identity["stable_fields"]).encode("utf-8"))
        self.assertEqual(identity["stable_sha256"], expected)

    def test_mutable_fields_excluded(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(set(identity["excluded_mutable_fields"]),
                         set(reference.MUTABLE_TASK_FIELDS))
        for field in reference.MUTABLE_TASK_FIELDS:
            self.assertNotIn(field, identity["stable_fields"])

    def test_commits_are_full_hex(self) -> None:
        self.assertRegex(reference.BASE_COMMIT, r"^[0-9a-f]{40}$")


class PcmTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        first = reference.synthetic_source_pcm()
        second = reference.synthetic_source_pcm()
        self.assertEqual(first, second)
        self.assertEqual(len(first), reference.CONTROL_SOURCE_SAMPLES)

    def test_synthetic_pcm_is_finite_and_bounded(self) -> None:
        source = reference.validate_pcm(reference.synthetic_source_pcm())
        self.assertTrue(all(math.isfinite(value) for value in source))
        self.assertLessEqual(max(abs(v) for v in source), 1.0)
        self.assertEqual(source[:reference.CONTROL_LEAD_SAMPLES],
                         [0.0] * reference.CONTROL_LEAD_SAMPLES)

    def test_pcm_summary_is_deterministic(self) -> None:
        signal = reference.synthetic_source_pcm()
        first = reference.pcm_summary(signal)
        second = reference.pcm_summary(signal)
        self.assertEqual(first, second)
        self.assertEqual(first["duration_s"], "2")
        self.assertEqual(first["samples"], 32000)
        self.assertEqual(first["channels"], 1)
        self.assertGreater(first["peak_micro"], 0)
        self.assertLessEqual(first["peak_micro"], 1000000)

    def test_validate_pcm_accepts_integers(self) -> None:
        self.assertEqual(reference.validate_pcm([0, 0.5, -1]),
                         [0.0, 0.5, -1.0])

    def test_validate_pcm_rejects_invalid(self) -> None:
        cases = [
            lambda: reference.validate_pcm([]),
            lambda: reference.validate_pcm(b"ab"),
            lambda: reference.validate_pcm(None),
            lambda: reference.validate_pcm([0.0], 8000),
            lambda: reference.validate_pcm([0.0], reference.SAMPLE_RATE_HZ, 2),
            lambda: reference.validate_pcm([math.nan]),
            lambda: reference.validate_pcm([math.inf]),
            lambda: reference.validate_pcm([-math.inf]),
            lambda: reference.validate_pcm([1.5]),
            lambda: reference.validate_pcm([True]),
            lambda: reference.validate_pcm(["0.1"]),
            lambda: reference.validate_pcm([0.0], True),
        ]
        for action in cases:
            with self.assertRaises(reference.ReferenceRejection):
                action()

    def test_identity_transform_is_exact(self) -> None:
        source = reference.synthetic_source_pcm()
        output = reference.identity_transform(source)
        self.assertEqual(output, source)
        self.assertEqual(reference.pcm_summary(source)["sha256"],
                         reference.pcm_summary(output)["sha256"])

    def test_duration_accounting_exact(self) -> None:
        result = reference.duration_accounting(32000, 32000)
        self.assertEqual(result["source_duration_s"], "2")
        self.assertEqual(result["output_duration_s"], "2")
        self.assertEqual(result["duration_ratio"], "1")
        self.assertEqual(result["sample_delta"], 0)

    def test_duration_accounting_rejects_bad_counts(self) -> None:
        for value in (0, -1, True, 1.5, "4"):
            with self.assertRaises(reference.ReferenceRejection):
                reference.duration_accounting(value, 1)
            with self.assertRaises(reference.ReferenceRejection):
                reference.duration_accounting(1, value)

    def test_alignment_is_offline(self) -> None:
        alignment = reference.alignment_accounting(32000)
        self.assertEqual(alignment["mode"], "offline_whole_utterance")
        self.assertFalse(alignment["streaming_supported"])
        self.assertFalse(alignment["incremental_streaming"])
        self.assertTrue(alignment["whole_clip_required"])
        self.assertFalse(alignment["measured"])
        self.assertEqual(alignment["tail_samples"], 32000)


class TargetAdmissionTests(unittest.TestCase):
    def test_identity_control_is_admitted_without_transformation(self) -> None:
        result = reference.admit_target_condition(
            reference.identity_target_condition())
        self.assertTrue(result["accepted"])
        self.assertTrue(result["identity_control"])
        self.assertFalse(result["transformation_performed"])
        self.assertEqual(result["qualification_effect"], "none")

    def test_nonidentity_target_is_rejected(self) -> None:
        condition = reference.identity_target_condition()
        condition["target_emotion_label"] = "joyful"
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.admit_target_condition(condition)
        self.assertIn("absent_candidate_transform", caught.exception.code)

    def test_reduced_intensity_is_rejected(self) -> None:
        condition = reference.identity_target_condition()
        condition["target_intensity_milli"] = 500
        with self.assertRaises(reference.ReferenceRejection):
            reference.admit_target_condition(condition)

    def test_text_tts_and_voice_conversion_are_rejected(self) -> None:
        for kind in ("text_to_speech", "speech_to_speech_voice_conversion"):
            condition = reference.identity_target_condition()
            condition["task_kind"] = kind
            with self.assertRaises(reference.ReferenceRejection):
                reference.admit_target_condition(condition)

    def test_bad_shapes_are_rejected(self) -> None:
        for action in (
                lambda: reference.admit_target_condition([]),
                lambda: reference.admit_target_condition({}),
                lambda: reference.admit_target_condition(
                    dict(reference.identity_target_condition(),
                         extra="x"))):
            with self.assertRaises(reference.ReferenceRejection):
                action()


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_complete_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["source_revision"], "a" * 40)
        self.assertFalse(result["revision_pin_available"])
        self.assertEqual(result["files_checked"],
                         len(reference.CALLER_FILE_PAIRS))
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["audio_read"])

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["style_conditioning_path"]).unlink()
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["checkpoint_path"]).write_bytes(b"tampered")
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["runtime_path"]).rmdir()
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["model_config_path"] = "config.json"
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_short_or_nonhex_revision(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["source_revision"] = "b43a7e1"
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)
            manifest["source_revision"] = "g" * 40
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_task_kind_and_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["task_kind"] = "text_to_speech"
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)
            manifest = _manifest_fixture(Path(raw))
            manifest["comparison_baseline"] = "fixed_style_pipeline"
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_streaming_variant(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["variant"] = "incremental_streaming"
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_float_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["channels"] = 1.0
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_out_of_range_values(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            for field, value in (("sample_rate_input_hz", 4000),
                                 ("sample_rate_output_hz", 384000),
                                 ("target_intensity_milli", 0),
                                 ("target_intensity_milli", 1001)):
                broken = dict(manifest)
                broken[field] = value
                with self.assertRaises(reference.ReferenceRejection):
                    reference.validate_caller_manifest(broken)

    def test_manifest_rejects_empty_emotion_label(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["target_emotion_label"] = ""
            with self.assertRaises(reference.ReferenceRejection):
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
        self.assertEqual(control["duration"]["duration_ratio"], "1")
        self.assertFalse(control["alignment"]["streaming_supported"])
        self.assertFalse(control["geometry"]["candidate_geometry_asserted"])

    def test_identity_baseline_is_exact(self) -> None:
        baseline = reference.build_control()["identity_baseline"]
        self.assertTrue(baseline["sample_count_equal"])
        self.assertTrue(baseline["duration_equal"])
        self.assertTrue(baseline["digest_equal"])
        self.assertTrue(baseline["peak_bounded"])
        self.assertFalse(baseline["transformation_performed"])
        self.assertEqual(baseline["qualification_effect"], "none")

    def test_nonidentity_targets_are_rejected(self) -> None:
        admission = reference.build_control()["target_condition_admission"]
        self.assertTrue(admission["identity_control_accepted"])
        self.assertTrue(admission["nonidentity_rejected"])
        self.assertEqual(admission["accepted_labels"], ["identity"])
        self.assertFalse(admission["transformation_performed"])

    def test_acceptance_outcomes_are_all_unmeasured(self) -> None:
        control = reference.build_control()
        self.assertEqual(len(control["acceptance_outcomes"]), 5)
        self.assertTrue(all(item["measured"] is False
                            and item["value"] is None
                            for item in control["acceptance_outcomes"]))
        self.assertEqual(
            [item["id"] for item in control["acceptance_outcomes"]],
            ["text_and_semantic_preservation", "identity_similarity",
             "target_emotion_realization", "naturalness",
             "alignment_and_output_timing"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = json.loads((HERE / "contract.json").read_text())

    def test_top_level_decision(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK_ID)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["mode"], "feasibility")
        self.assertEqual(report["profile"], "voice")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertTrue(report["proposal_only"])
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
        self.assertEqual(
            [item["id"] for item in blockers],
            [item["id"] for item in reference.EXACT_BLOCKERS])
        self.assertIn("input_speech_transform_model_absent",
                      [item["id"] for item in blockers])
        self.assertIn("target_emotion_condition_absent",
                      [item["id"] for item in blockers])
        self.assertIn("consent_cleared_target_voices_absent",
                      [item["id"] for item in blockers])

    def test_qualification_blocked(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(qualification["no_missing_result_qualifies_candidate"])
        self.assertEqual(qualification["blocked_gate_count"], 8)
        self.assertFalse(qualification["real_candidate_metrics"])

    def test_boundary_is_closed(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "production_callback_registered",
                    "descriptor_registry_change", "shared_build_or_ci_change",
                    "installed_v0_behavior_change", "asset_bundled",
                    "weights_vendored", "network_used", "model_loaded",
                    "processor_exposure"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_is_closed(self) -> None:
        scope = self.report["scope"]
        for key in ("real_audio", "real_corpus", "real_candidate_model",
                    "real_weights", "model_executed", "weights_loaded",
                    "weights_downloaded", "runtime_invoked", "network_used",
                    "device_timing", "listening", "public_benchmark",
                    "release_claim"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["task_local_only"], True)
        self.assertEqual(scope["write_scope"], reference.TASK_PREFIX)

    def test_no_fabricated_identity(self) -> None:
        candidate = self.report["candidate"]
        self.assertIsNone(candidate["source_revision"])
        self.assertIsNone(candidate["source_sha256"])
        self.assertIsNone(candidate["weights_sha256"])
        self.assertFalse(candidate["source_present"])
        self.assertFalse(candidate["weights_present"])
        self.assertFalse(candidate["target_emotion_labels_present"])
        self.assertFalse(candidate["consent_cleared_target_voices_present"])
        self.assertFalse(candidate["geometry_documented"])
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertIsNone(requirements["model_checkpoint"]["sha256"])
        self.assertIsNone(requirements["model_checkpoint"]["byte_count"])
        self.assertIsNone(requirements["model_config"]["sha256"])
        self.assertIsNone(requirements["target_emotion_label_set"]["sha256"])
        self.assertIsNone(
            requirements["style_conditioning_asset"]["sha256"])
        self.assertIsNone(requirements["source_checkout"]["revision"])
        self.assertIsNone(
            requirements["exact_runtime"]["runtime_lock_sha256"])

    def test_voice_profile_has_no_satisfied_item(self) -> None:
        profile = self.report["voice_profile"]
        self.assertEqual(profile["name"], "voice")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_model_metrics"])
        self.assertEqual(len(profile["required_items"]), 8)
        self.assertTrue(all(item["qualification_effect"] == "none"
                            for item in profile["required_items"]))

    def test_audit_is_absent_and_not_qualified(self) -> None:
        audit = self.report["asset_audit"]
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["audit_result"], "absent")
        self.assertFalse(audit["source_present"])
        self.assertFalse(audit["license_present"])
        self.assertFalse(audit["weights_present"])
        self.assertFalse(audit["emotion_label_set_present"])
        self.assertFalse(audit["target_voice_consent_present"])
        self.assertTrue(audit["all_absence_probes_absent"])

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_text(self.report)
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(
            self.report["task_row_identity"]["whole_file_hashed"])
        self.assertFalse(
            self.report["task_row_identity"]["full_tasks_json_hashed"])

    def test_source_reported_context_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"], "source_reported_not_measured_here")
        self.assertEqual(context["record"], reference.CANDIDATE_RECORD)
        self.assertEqual(context["record_status"], "unavailable/blocked")
        self.assertEqual(len(context["sibling_context_not_attributed"]), 4)

    def test_missing_artifacts_recorded(self) -> None:
        for path in (reference.MISSING_SOURCE_PATH,
                     reference.MISSING_WEIGHTS_PATH,
                     reference.LABEL_SET_PATH,
                     reference.TARGET_VOICE_CONSENT_PATH,
                     reference.COHORT_MANIFEST_PATH,
                     reference.PARITY_MANIFEST_PATH,
                     reference.RIGHTS_RECORD_PATH):
            self.assertIn(path, self.report["missing_historical_artifacts"])

    def test_report_contains_no_floats(self) -> None:
        reference.canonical_text(self.report)

    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_report(reference.build_report())
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)

    def test_on_disk_report_matches_generator(self) -> None:
        expected = reference.canonical_report(reference.build_report())[0]
        self.assertEqual((HERE / "report.json").read_text(encoding="utf-8"),
                         expected)

    def test_sidecar_matches_report(self) -> None:
        text, digest = reference.canonical_report(reference.build_report())
        sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8")
        self.assertEqual(sidecar, digest + "\n")
        self.assertEqual(_sha(text.encode("utf-8")), digest)

    def test_contract_matches_report(self) -> None:
        contract = self.contract
        report = self.report
        self.assertEqual(contract["task"], report["task_id"])
        self.assertEqual(contract["decision"], report["decision"])
        self.assertEqual(contract["status"], report["status"])
        self.assertEqual(contract["mode"], report["mode"])
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
        self.assertEqual(contract["write_scope"], reference.TASK_PREFIX)
        self.assertEqual(contract["reproduction"]["cold_start_regenerations"], 3)

    def test_sources_manifest_has_no_tasks_json(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line and not line.startswith("#"):
                self.assertNotIn("TASKS.json", line)


if __name__ == "__main__":
    unittest.main()
