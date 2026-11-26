# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance suite for the SDK-CONVFSENET package.

The suite is offline, stdlib-only and read-only. It exercises strict JSON,
fixture arithmetic, bounded integer gain masking, paired metrics, block
invariance, reset, caller-asset identity validation and the exact adverse
rejection matrix.
"""

from __future__ import annotations

import sys
import unittest

sys.dont_write_bytecode = True

import reference  # noqa: E402


class ReportIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_disposition_is_defer_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification"]["status"],
                         "not_qualified")
        self.assertFalse(self.report["qualification"]["qualifies"])

    def test_eight_blocked_release_gates(self):
        gates = self.report["release_gates"]
        self.assertEqual([row["id"] for row in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(row["status"] == "blocked" for row in gates))

    def test_enhancement_profile_items_are_synthetic_or_blocked(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "enhancement")
        self.assertEqual(len(profile["required_items"]), 12)
        statuses = {row["status"] for row in profile["required_items"].values()}
        self.assertTrue(statuses.issubset({"synthetic_only", "blocked"}))
        blocked = sorted(name for name, row in profile["required_items"].items()
                         if row["status"] == "blocked")
        self.assertEqual(self.report["profile_blockers"], blocked)
        self.assertIn("paired_stoi", blocked)
        self.assertIn("task_matched_baseline", blocked)

    def test_candidate_geometry_is_not_fabricated(self):
        candidate = self.report["candidate"]
        self.assertIsNone(candidate["reported_input_sample_rate_hz"])
        self.assertIsNone(candidate["reported_hop_samples"])
        self.assertIsNone(candidate["reported_frame_samples"])
        self.assertIsNone(candidate["reported_algorithmic_latency_samples"])
        self.assertFalse(candidate["geometry_documented"])
        self.assertFalse(candidate["checkpoint_lineage_verified"])
        self.assertEqual(candidate["reported_parameter_count"], 1450000)
        self.assertEqual(candidate["reported_compact_parameter_count"], 670000)
        self.assertFalse(candidate["source_present"])
        self.assertFalse(candidate["weights_present"])
        self.assertFalse(candidate["runtime_present"])
        self.assertFalse(candidate["exact_numeric_output_present"])

    def test_all_boundary_and_scope_flags_are_false(self):
        self.assertTrue(all(value is False
                            for value in self.report["boundary"].values()))
        scope = self.report["scope"]
        self.assertTrue(scope["synthetic_only"])
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key not in {"synthetic_only", "task_local_only"}:
                self.assertIs(value, False, key)

    def test_no_result_is_promoted(self):
        self.assertTrue(self.report["adverse_all_rejected"])
        for case in self.report["adverse_rejections"]:
            self.assertEqual(case["status"], "rejected")
            self.assertEqual(case["expected_code"], case["observed_code"])
            self.assertTrue(case["state_unchanged"])
        for section in ("paired_metrics", "clean_preservation",
                        "peaks_and_invalid", "pause_attenuation", "stoi",
                        "baseline", "alignment", "streaming", "reset",
                        "final_partial", "state_and_memory", "runtime_timing",
                        "nonfinite"):
            self.assertIs(self.report[section]["qualifies"], False, section)
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_stoi_and_baseline_are_blocked_not_fabricated(self):
        self.assertEqual(self.report["stoi"]["status"], "blocked")
        self.assertIsNone(self.report["stoi"]["value_millis"])
        self.assertEqual(self.report["baseline"]["status"], "blocked")
        self.assertIsNone(self.report["baseline"]["baseline_id"])

    def test_six_exact_blockers(self):
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        identifiers = {row["id"] for row in blockers}
        self.assertIn("pinned_convfsenet_source_weights_runtime_absent",
                      identifiers)
        self.assertIn("candidate_io_geometry_and_quantization_unverified",
                      identifiers)
        self.assertIn("rights_cleared_paired_cohort_and_scorer_absent",
                      identifiers)


class MetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_paired_metrics_are_exact_and_unqualified(self):
        paired = self.report["paired_metrics"]
        self.assertEqual(len(paired["regions"]), 3)
        for region in paired["regions"]:
            self.assertIs(region["qualifies"], False)
            self.assertEqual(region["surrogate_si_sdr_millidb"],
                             region["identity_si_sdr_millidb"]
                             + region["delta_si_sdr_millidb"])
            self.assertGreaterEqual(region["delta_snr_millidb"], -100)
        self.assertTrue(paired["no_noisy_region_degraded"])
        self.assertEqual(paired["min_delta_si_sdr_millidb"],
                         min(row["delta_si_sdr_millidb"]
                             for row in paired["regions"]))

    def test_si_sdr_is_scale_invariant_and_exact(self):
        clean = [0, 1000, -2000, 3000, 0, -1000]
        self.assertEqual(reference.si_sdr_millidb(clean, clean, 0, 6),
                         reference.MAX_MILLIDB)
        scaled = [value * 3 for value in clean]
        self.assertEqual(reference.si_sdr_millidb(clean, scaled, 0, 6),
                         reference.MAX_MILLIDB)
        silent = [0, 0, 0, 0, 0, 0]
        self.assertEqual(reference.si_sdr_millidb(silent, scaled, 0, 6),
                         reference.MIN_MILLIDB)

    def test_clean_preservation(self):
        clean = self.report["clean_preservation"]
        self.assertEqual(len(clean["regions"]), 2)
        for region in clean["regions"]:
            self.assertIs(region["qualifies"], False)
            self.assertGreater(region["si_sdr_millidb"], 30000)
            self.assertLess(abs(region["level_change_millidb"]), 500)
            self.assertLess(region["peak_milli"], 1000)
        self.assertEqual(clean["nonfinite_output_count"], 0)

    def test_peaks_and_pause(self):
        peaks = self.report["peaks_and_invalid"]
        self.assertLess(peaks["max_peak_milli"], peaks["peak_bound_milli"])
        self.assertEqual(peaks["clipped_samples"], 0)
        self.assertEqual(peaks["invalid_output_count"], 0)
        self.assertGreater(self.report["pause_attenuation"][
            "noise_attenuation_millidb"], 0)

    def test_alignment_content_mapping(self):
        alignment = self.report["alignment"]
        self.assertEqual(alignment["surrogate_content_delay_samples"], 0)
        self.assertEqual(alignment["best_shift_samples"], 0)
        self.assertTrue(alignment["zero_shift_best"])
        zero = [row for row in alignment["probes"]
                if row["shift_samples"] == 0][0]
        self.assertTrue(all(row["si_sdr_millidb"] < zero["si_sdr_millidb"]
                            for row in alignment["probes"]
                            if row["shift_samples"] != 0))

    def test_streaming_reset_and_partial(self):
        streaming = self.report["streaming"]
        self.assertTrue(streaming["all_match"])
        self.assertEqual(streaming["accepted_samples"], 12000)
        self.assertEqual(sum(streaming["chunks"]), 12000)
        self.assertFalse(streaming["scheduler_measured"])
        self.assertTrue(self.report["reset"]["matches_fresh"])
        self.assertEqual(self.report["reset"]["epoch"], 2)
        partial = self.report["final_partial"]
        self.assertEqual(partial["valid_count"], 137)
        self.assertEqual(partial["output_samples"], 160)
        self.assertEqual(partial["advanced_samples"], 137)
        self.assertTrue(partial["padding_zero"])
        self.assertTrue(partial["tail_zero"])


class StrictInputTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate_and_nonfinite(self):
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":NaN}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":Infinity}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('[1,2]')

    def test_config_rejects_wrong_geometry(self):
        config = {"sample_rate_hz": 8000, "channels": 1,
                  "frame_samples": 160, "sample_format": "float32",
                  "clock_ppm": 0, "resampling": "none",
                  "algorithmic_latency_samples": 0}
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.validate_config(config)
        self.assertEqual(caught.exception.code, "unsupported_sample_rate")

    def test_nonfinite_and_out_of_range_inputs_are_rejected(self):
        surrogate = reference.GainMaskSurrogate()
        signals = reference.build_fixture()
        frame = [signals["mic"][index] / reference.Q15
                 for index in range(reference.FRAME_SAMPLES)]
        surrogate.process_frame(frame)
        before = surrogate.state_digest
        for bad, code in ((float("nan"), "nonfinite_input:input"),
                          (float("inf"), "nonfinite_input:input"),
                          (1.5, "sample_out_of_range:input"),
                          ("x", "invalid_sample:input"),
                          (True, "invalid_sample:input")):
            with self.assertRaises(reference.ReferenceRejection) as caught:
                surrogate.process_frame([bad] + frame[1:])
            self.assertEqual(caught.exception.code, code)
        self.assertEqual(before, surrogate.state_digest)

    def test_missing_input_and_nonzero_padding_are_rejected(self):
        surrogate = reference.GainMaskSurrogate()
        signals = reference.build_fixture()
        frame = [signals["mic"][index] / reference.Q15
                 for index in range(reference.FRAME_SAMPLES)]
        with self.assertRaises(reference.ReferenceRejection) as caught:
            surrogate.process_frame(None)
        self.assertEqual(caught.exception.code, "missing_input")
        with self.assertRaises(reference.ReferenceRejection) as caught:
            surrogate.process_frame(
                frame[:137] + [1.0] + frame[138:], valid_count=137)
        self.assertEqual(caught.exception.code, "padding_not_zero:input")

    def test_epoch_zero_and_negative_are_rejected(self):
        surrogate = reference.GainMaskSurrogate(epoch=1)
        for epoch in (0, -1, 1):
            with self.assertRaises(reference.ReferenceRejection):
                surrogate.reset(epoch, 0)

    def test_adverse_matrix_is_complete_and_exact(self):
        cases = reference.adverse_rejections()
        self.assertEqual(len(cases), 47)
        self.assertTrue(all(case["status"] == "rejected" for case in cases))
        self.assertTrue(all(case["expected_code"] == case["observed_code"]
                            for case in cases))
        self.assertTrue(all(case["state_unchanged"] for case in cases))
        identifiers = {case["case_id"] for case in cases}
        for required in ("config_stereo", "frame_nonfinite_nan",
                         "frame_nonfinite_inf", "frame_out_of_range",
                         "frame_missing_input",
                         "caller_manifest_bad_model_hash",
                         "caller_manifest_bad_artifact_format",
                         "reset_epoch_not_greater"):
            self.assertIn(required, identifiers)

    def test_fixture_validation_rejects_bad_specs(self):
        spec = reference.fixture_spec()
        spec["length_samples"] = 11999
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)
        spec = reference.fixture_spec()
        spec["segments"] = spec["segments"][:-1]
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)
        spec = reference.fixture_spec()
        spec["segments"] = [dict(segment) for segment in spec["segments"]]
        spec["segments"][0]["noise_amplitude"] = 5000
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(spec)

    def test_caller_manifest_is_identity_only(self):
        manifest = {
            "adapter": "convfsenet-reference",
            "algorithmic_latency_samples": 0,
            "artifact_format": "onnx",
            "channels": 1,
            "frame_samples": 160,
            "input_format": "float32",
            "library_path": "/caller/convfsenet/lib",
            "library_sha256": "3" * 64,
            "model_path": "/caller/convfsenet/model",
            "model_sha256": "0" * 64,
            "precision": "int8",
            "sample_rate_hz": 16000,
            "source_commit": "0" * 40,
            "source_sha256": "1" * 64,
            "variant": "convfsenet-compact",
            "weights_sha256": "2" * 64,
        }
        result = reference.validate_caller_manifest(manifest)
        self.assertEqual(result, {"validated": True, "loaded": False,
                                  "executed": False, "imported": False})
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.validate_caller_manifest(
                {**manifest, "artifact_format": "tflite"})
        self.assertEqual(caught.exception.code,
                         "unsupported_artifact_format")

    def test_canonical_json_is_stable(self):
        value = {"b": [1, 2], "a": {"z": "x"}}
        text = reference.canonical_text(value)
        self.assertEqual(text, '{"a":{"z":"x"},"b":[1,2]}')
        self.assertEqual(reference.object_digest(value),
                         reference.sha256_bytes(text.encode("utf-8")))


class DeterminismTests(unittest.TestCase):
    def test_three_builds_are_byte_identical(self):
        texts = [reference.canonical_report(reference.build_report())[0]
                 for _ in range(3)]
        self.assertEqual(len(set(texts)), 1)
        self.assertEqual(reference.sha256_bytes(texts[0].encode("utf-8")),
                         reference.sha256_bytes(texts[1].encode("utf-8")))

    def test_stable_board_identity(self):
        row = reference.board_row()
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         reference.BOARD_ROW_STABLE_SHA256)

    def test_contract_matches_report(self):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["release_gates"], report["release_gates"])
        self.assertEqual(contract["exact_blockers"], report["exact_blockers"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertIn(reference.TASK_PREFIX + "reference.py",
                      contract["artifact_pins"])


if __name__ == "__main__":
    unittest.main()
