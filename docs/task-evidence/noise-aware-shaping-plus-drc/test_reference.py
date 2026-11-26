# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the noise-aware shaping plus DRC package.

No network, no research-module import, no numpy/scipy, no runtime, no real audio
and no skips.  Run after ``run.py`` so the generated artifacts exist::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
"""

from __future__ import annotations

import hashlib
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
REPORT_CACHE = None


def report() -> dict:
    global REPORT_CACHE
    if REPORT_CACHE is None:
        REPORT_CACHE = reference.build_report()
    return REPORT_CACHE


class CanonicalJsonTests(unittest.TestCase):
    def test_canonical_bytes_sorted_and_newline(self):
        data = reference.canonical_bytes({"b": 1, "a": 2})
        self.assertTrue(data.endswith(b"\n"))
        self.assertLess(data.index(b'"a"'), data.index(b'"b"'))

    def test_strict_loads_accepts_object(self):
        self.assertEqual(reference.strict_loads('{"a": 1}'), {"a": 1})

    def test_strict_loads_rejects_duplicate_key(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1, "a": 2}')

    def test_strict_loads_rejects_nan(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": NaN}')

    def test_strict_loads_rejects_infinity(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": Infinity}')

    def test_strict_loads_rejects_non_object(self):
        with self.assertRaises(ValueError):
            reference.strict_loads("[1, 2]")

    def test_strict_loads_rejects_trailing_text(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1} trailing')

    def test_negative_zero_detection(self):
        self.assertTrue(reference.has_negative_zero({"a": -0.0}))
        self.assertFalse(reference.has_negative_zero({"a": 0.0}))

    def test_metric_normalises_zero(self):
        self.assertEqual(reference._metric(-0.0), 0.0)
        self.assertEqual(reference._metric(1.234567890123), 1.23456789)

    def test_metric_rejects_nonfinite(self):
        with self.assertRaises(ValueError):
            reference._metric(math.inf)


class BoardAndIdentityTests(unittest.TestCase):
    def test_board_digest_matches_constant(self):
        self.assertEqual(reference.board_row_digest(),
                         reference.BOARD_ROW_STABLE_SHA256)

    def test_board_digest_excludes_full_file(self):
        self.assertFalse(reference.BOARD_ROW_STABLE_FIELDS.get(
            "full_tasks_json_hashed", False))

    def test_board_digest_is_stable(self):
        self.assertEqual(reference.board_row_digest(),
                         reference.board_row_digest())

    def test_board_depends_on_foundations(self):
        self.assertEqual(
            reference.BOARD_ROW_STABLE_FIELDS["depends_on"],
            ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"])

    def test_board_mode_is_research_control(self):
        self.assertEqual(reference.BOARD_ROW_STABLE_FIELDS["mode"],
                         "research-control")


class FixtureTests(unittest.TestCase):
    def test_total_samples(self):
        for component in reference.FIXTURE_COMPONENTS.values():
            self.assertEqual(len(component), reference.TOTAL_SAMPLES)

    def test_segments_are_frame_aligned(self):
        for segment in reference.SEGMENTS:
            self.assertEqual(segment["start_frame"] % reference.SEGMENT_FRAMES,
                             0)
            self.assertEqual(segment["end_frame"] % reference.SEGMENT_FRAMES,
                             0)

    def test_segments_cover_whole_fixture(self):
        start = 0
        for segment in reference.SEGMENTS:
            self.assertEqual(segment["start_frame"], start)
            start = segment["end_frame"]
        self.assertEqual(start, reference.TOTAL_FRAMES)

    def test_component_digests_cover_all_components(self):
        self.assertEqual(set(reference.FIXTURE_DIGESTS),
                         set(reference.FIXTURE_COMPONENTS))

    def test_fixture_spec_digest_stable(self):
        self.assertEqual(reference.FIXTURE_SPEC_DIGEST,
                         reference.sha256(reference.canonical_bytes(
                             reference.fixture_spec())))

    def test_silence_strata_exactly_zero(self):
        clean = reference.FIXTURE_COMPONENTS["clean"]
        self.assertTrue(all(value == 0 for value in clean[:8000]))
        self.assertTrue(all(value == 0 for value in clean[-8000:]))

    def test_masker_only_in_declared_strata(self):
        masker = reference.FIXTURE_COMPONENTS["masker"]
        self.assertTrue(all(value == 0 for value in masker[:8000]))
        self.assertTrue(all(value == 0 for value in masker[24000:32000]))

    def test_masked_stratum_has_masker(self):
        masker = reference.FIXTURE_COMPONENTS["masker"]
        self.assertTrue(any(value != 0 for value in masker[16000:24000]))

    def test_int16_range(self):
        for component in reference.FIXTURE_COMPONENTS.values():
            self.assertGreaterEqual(min(component), -32768)
            self.assertLessEqual(max(component), 32767)

    def test_mix_differs_from_clean(self):
        self.assertNotEqual(
            reference.FIXTURE_COMPONENTS["mix"][16000:24000],
            reference.FIXTURE_COMPONENTS["clean"][16000:24000])

    def test_impulse_amplitude_engages_guard_under_static_gain(self):
        self.assertGreater(
            max(abs(value) for value in reference.FIXTURE_COMPONENTS["clean"]),
            reference.PEAK_CEILING / 2)


class ConfigTests(unittest.TestCase):
    def test_baseline_accepted(self):
        reference.validate_config(dict(reference.CONFIG))

    def test_unknown_key_rejected(self):
        config = dict(reference.CONFIG)
        config["extra"] = 1
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_sample_rate_rejected(self):
        config = dict(reference.CONFIG)
        config["sample_rate_hz"] = 48000
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_stereo_rejected(self):
        config = dict(reference.CONFIG)
        config["channels"] = 2
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_int16_rejected(self):
        config = dict(reference.CONFIG)
        config["input_format"] = "int16"
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_frame_rejected(self):
        config = dict(reference.CONFIG)
        config["frame_samples"] = 320
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_whole_file_energy_equalization_rejected(self):
        config = dict(reference.CONFIG)
        config["energy_equalization"] = "whole_file"
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_estimated_masker_rejected(self):
        config = dict(reference.CONFIG)
        config["masker_source"] = "estimated_runtime"
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_wrong_band_set_rejected(self):
        config = dict(reference.CONFIG)
        config["bands"] = [100, 250, 500, 1000]
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_real_runtime_rejected(self):
        config = dict(reference.CONFIG)
        config["real_runtime"] = True
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_model_used_rejected(self):
        config = dict(reference.CONFIG)
        config["model_used"] = True
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_surrogate_false_rejected(self):
        config = dict(reference.CONFIG)
        config["surrogate"] = False
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_default_enabled_rejected(self):
        config = dict(reference.CONFIG)
        config["default_enabled"] = True
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_negative_epoch_rejected(self):
        config = dict(reference.CONFIG)
        config["epoch"] = -1
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_bool_epoch_rejected(self):
        config = dict(reference.CONFIG)
        config["epoch"] = True
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_nonfinite_threshold_rejected(self):
        config = dict(reference.CONFIG)
        config["threshold_dbfs"] = float("nan")
        with self.assertRaises(ValueError):
            reference.validate_config(config)

    def test_noise_aware_false_rejected(self):
        config = dict(reference.CONFIG)
        config["noise_aware"] = False
        with self.assertRaises(ValueError):
            reference.validate_config(config)


class FrameTests(unittest.TestCase):
    def test_valid_frame(self):
        self.assertEqual(len(reference.validate_frame([0.0] * 160)), 160)

    def test_short_nonfinal_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_frame([0.0] * 159)

    def test_long_nonfinal_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_frame([0.0] * 161)

    def test_nan_rejected(self):
        frame = [0.0] * 160
        frame[4] = float("nan")
        with self.assertRaises(ValueError):
            reference.validate_frame(frame)

    def test_infinity_rejected(self):
        frame = [0.0] * 160
        frame[4] = float("inf")
        with self.assertRaises(ValueError):
            reference.validate_frame(frame)

    def test_out_of_range_rejected(self):
        frame = [0.0] * 160
        frame[4] = 1.5
        with self.assertRaises(ValueError):
            reference.validate_frame(frame)

    def test_bool_rejected(self):
        frame = [0.0] * 160
        frame[4] = True
        with self.assertRaises(ValueError):
            reference.validate_frame(frame)

    def test_string_outer_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_frame("[0.0]")

    def test_final_partial_accepted(self):
        self.assertEqual(len(reference.validate_frame([0.0] * 37,
                                                       final=True)), 37)

    def test_final_zero_length_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_frame([], final=True)

    def test_masker_length_mismatch_rejected(self):
        session = reference.Session("local_approximation")
        with self.assertRaises(ValueError):
            session.process([0.0] * 160, masker=[0.0] * 159)

    def test_nonfinite_masker_rejected(self):
        session = reference.Session("local_approximation")
        masker = [0.0] * 160
        masker[3] = float("nan")
        with self.assertRaises(ValueError):
            session.process([0.0] * 160, masker=masker)


class ProcessorTests(unittest.TestCase):
    def test_identity_is_bit_exact(self):
        source = reference.as_float(
            reference.FIXTURE_COMPONENTS["clean"][:1600])
        self.assertEqual(reference.run_samples(source, "identity"), source)

    def test_silence_is_exact_zero(self):
        output = reference.run_samples([0.0] * 512,
                                       "local_approximation")
        self.assertTrue(all(value == 0.0 for value in output))

    def test_impulse_has_zero_delay(self):
        result = reference.impulse_control()
        self.assertEqual(result["observed_peak_index"],
                         result["expected_output_index"])

    def test_streaming_parity(self):
        self.assertTrue(reference.streaming_parity_control()["all_identical"])

    def test_reset_matches_fresh_session(self):
        result = reference.reset_control()
        self.assertTrue(result["fresh_matches_reset"])
        self.assertTrue(result["higher_epoch_accepted"])

    def test_reset_epoch_zero_rejected(self):
        self.assertTrue(reference.reset_control()["epoch_zero_rejected"])

    def test_reset_negative_rejected(self):
        self.assertTrue(reference.reset_control()["negative_epoch_rejected"])

    def test_nonfinite_does_not_advance_state(self):
        result = reference.nonfinite_control()
        self.assertEqual(result["nonfinite_rejected"], 5)
        self.assertTrue(result["accepted_counter_unchanged"])
        self.assertTrue(result["state_digest_unchanged"])
        self.assertFalse(result["counted_as_silence"])

    def test_identity_tone_gain_is_zero(self):
        gain = reference.measure_tone_gain("identity", 1000, -24.0)
        self.assertAlmostEqual(gain, 0.0, places=6)

    def test_static_gain_tone_gain(self):
        gain = reference.measure_tone_gain("static_gain", 1000, -24.0)
        self.assertAlmostEqual(gain, reference.STATIC_GAIN_DB, places=2)

    def test_full_band_compressor_slope_below_one(self):
        slope = reference.level_transfer("compressor_only")[
            "slope_db_per_db"]
        self.assertLess(slope, 0.8)

    def test_local_approximation_slope_below_one(self):
        slope = reference.level_transfer("local_approximation")[
            "slope_db_per_db"]
        self.assertLess(slope, 1.0)

    def test_compressor_attack_is_nonzero(self):
        attack = reference.measure_step("compressor_only", True)
        self.assertGreater(attack["transition_ms"], 0.0)

    def test_identity_attack_is_zero(self):
        attack = reference.measure_step("identity", True)
        self.assertEqual(attack["transition_ms"], 0.0)

    def test_all_modes_finite_and_bounded(self):
        for mode in reference.VALID_MODES:
            measurements = reference.measure_mode(mode)
            self.assertEqual(measurements["nonfinite_output_samples"], 0)
            self.assertLessEqual(measurements["max_abs_output"], 1.0)

    def test_shaping_modes_are_energy_neutral(self):
        for mode in ("fixed_tilt", "noise_aware_shaping"):
            measurements = reference.measure_mode(mode)
            self.assertTrue(measurements["energy_neutral"], mode)
            self.assertLessEqual(abs(measurements["gain_db"]), 1.0, mode)

    def test_static_gain_clips_at_ceiling(self):
        measurements = reference.measure_mode("static_gain")
        self.assertGreater(measurements["clipped_output_samples"], 0)
        self.assertAlmostEqual(measurements["max_abs_output"],
                               reference.PEAK_CEILING, places=9)

    def test_band_response_identity_is_flat(self):
        response = reference.band_response("identity")["band_gain_db"]
        for value in response.values():
            self.assertAlmostEqual(value, 0.0, places=6)

    def test_band_response_tilt_is_high_frequency_positive(self):
        response = reference.band_response("fixed_tilt")["band_gain_db"]
        self.assertGreater(response["6"], response["0"])

    def test_band_response_local_is_high_frequency_positive(self):
        response = reference.band_response(
            "local_approximation")["band_gain_db"]
        self.assertGreater(response["6"], response["0"])

    def test_masker_adaptation_direction(self):
        result = reference.masker_response_control()
        self.assertTrue(result["adapts_to_masker_band"])
        self.assertGreater(result["low_minus_high_band_1_db"], 0.0)
        self.assertLess(result["low_minus_high_band_6_db"], 0.0)

    def test_masker_adaptation_does_not_touch_equalizer_for_silence(self):
        result = reference.masker_response_control()
        self.assertLess(abs(result["response"]["low_masker"]["equalizer_db"]),
                        12.0)


class AdverseControlTests(unittest.TestCase):
    def test_config_adverse_all_rejected(self):
        result = reference.config_adverse_control()
        self.assertTrue(result["rejected_all"])
        self.assertGreaterEqual(result["case_count"], 24)

    def test_frame_adverse_all_rejected(self):
        result = reference.frame_adverse_control()
        self.assertTrue(result["rejected_all"])
        self.assertTrue(result["masker_rejected_all"])
        self.assertTrue(result["masker_length_rejected"])
        self.assertGreaterEqual(result["case_count"], 20)

    def test_asset_adverse_all_rejected(self):
        result = reference.asset_controls()
        self.assertTrue(result["rejected_all"])
        self.assertTrue(result["valid_manifest_accepted"])
        self.assertFalse(result["valid_manifest_loaded"])
        self.assertFalse(result["valid_manifest_executed"])
        self.assertFalse(result["pinned_identity_admitted"])

    def test_valid_asset_never_admitted_as_official(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = reference._asset_manifest(Path(directory))
            valid = reference.validate_caller_asset(manifest)
            pinned = reference.pinned_asset_identity(manifest)
        self.assertTrue(valid["valid"])
        self.assertFalse(valid["official_identity"])
        self.assertFalse(pinned["admitted"])
        self.assertEqual(pinned["reason"],
                         "official_and_listener_identity_not_established")

    def test_strict_rejection_examples(self):
        result = reference.strict_rejection_examples()
        self.assertEqual(result["bad_json_rejected"],
                         result["bad_json_total"])
        self.assertEqual(result["bad_pins_rejected"],
                         result["bad_pins_total"])
        self.assertEqual(result["bad_readme_rejected"],
                         result["bad_readme_total"])


class ReportTests(unittest.TestCase):
    def test_report_is_deterministic(self):
        first = reference.canonical_report_bytes(report())
        second = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)

    def test_report_has_no_negative_zero(self):
        self.assertFalse(reference.has_negative_zero(report()))

    def test_report_key_set(self):
        self.assertEqual(set(report()), reference.REQUIRED_REPORT_KEYS)

    def test_contract_key_set(self):
        self.assertEqual(set(reference.contract_payload()),
                         reference.REQUIRED_CONTRACT_KEYS)

    def test_decision_and_status(self):
        payload = report()
        self.assertEqual(payload["decision"], "DEFER")
        self.assertEqual(payload["evidence_status"], "incomplete")
        self.assertEqual(payload["qualification_status"], "not_qualified")
        self.assertEqual(payload["qualification"]["status"],
                         "not_qualified")
        self.assertEqual(payload["qualification"]["readiness"], "incomplete")

    def test_eight_blocked_gates(self):
        gates = report()["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["qualifies"] is False for gate in gates))

    def test_six_exact_blockers(self):
        self.assertGreaterEqual(len(report()["exact_blockers"]), 6)

    def test_local_approximation_is_not_candidate(self):
        local = report()["local_approximation"]
        self.assertFalse(local["is_research_candidate"])
        self.assertFalse(local["is_optfractasii"])
        self.assertFalse(local["candidate_result"])
        self.assertTrue(local["surrogate_only"])
        self.assertTrue(local["model_free"])
        self.assertFalse(local["uses_real_corpus"])

    def test_published_controls_not_reproduced(self):
        published = report()["published_controls_assessment"]
        self.assertFalse(published["optfractasii"]["reproduced"])
        self.assertFalse(published["research_prototype"]["reproduced"])
        self.assertFalse(published["separation"]["pooling_performed"])
        self.assertFalse(published["separation"][
            "historical_research_screen_reproduced"])

    def test_historical_screen_not_candidate_result(self):
        screen = report()["historical_research_screen"]
        self.assertFalse(screen["reproduced"])
        self.assertFalse(screen["verified_independently"])
        self.assertFalse(screen["result_claim"])
        self.assertFalse(screen["is_candidate_result"])
        self.assertEqual(screen["source_pin"],
                         reference.LISTENING_RESEARCH_PATH)

    def test_board_not_full_hashed(self):
        self.assertFalse(report()["board_row"]["full_tasks_json_hashed"])

    def test_boundary_flags_false(self):
        for name, value in report()["boundary"].items():
            if isinstance(value, bool):
                self.assertFalse(value, name)

    def test_scope_is_task_local(self):
        scope = report()["scope"]
        self.assertTrue(scope["task_local_only"])
        for name, value in scope.items():
            if isinstance(value, bool) and name != "task_local_only":
                self.assertFalse(value, name)

    def test_upstream_identity_absent(self):
        upstream = report()["upstream"]
        for key in ("commit", "license", "version", "algorithm_parameters",
                    "reference_output", "runtime"):
            self.assertIsNone(upstream[key], key)
        self.assertTrue(upstream["research_module_present"])
        self.assertFalse(upstream["source_licensed"])

    def test_missing_results_not_promoted(self):
        payload = report()
        self.assertTrue(payload["no_missing_result_qualifies_candidate"])
        self.assertTrue(payload["missing_results"])
        self.assertFalse(payload["qualification"]["missing_result_promoted"])

    def test_contract_digest_matches(self):
        self.assertEqual(
            report()["contract_sha256"],
            hashlib.sha256(reference.contract_bytes()).hexdigest())

    def test_format_preserves_installed_v0(self):
        format_block = report()["format"]
        self.assertEqual(format_block["sdk_v0_sample_rate_hz"], 16000)
        self.assertEqual(format_block["sdk_v0_channels"], 1)
        self.assertEqual(format_block["sdk_v0_frame_samples"], 160)
        self.assertTrue(format_block["sdk_v0_geometry_preserved"])
        self.assertFalse(format_block["upstream_geometry_verified"])

    def test_fixture_digest_present(self):
        fixture = report()["fixture"]
        self.assertEqual(fixture["spec_digest"],
                         reference.FIXTURE_SPEC_DIGEST)
        self.assertEqual(fixture["total_samples"],
                         reference.TOTAL_SAMPLES)

    def test_qualification_flags_absent(self):
        qualification = report()["qualification"]
        for key in (
                "algorithm_identity_verified",
                "candidate_result_present",
                "energy_equalization_contract_verified",
                "geometry_verified",
                "historical_research_reproduced",
                "listener_outcomes_present",
                "listening_present",
                "local_approximation_is_candidate",
                "masker_cohort_rights_cleared",
                "missing_result_promoted",
                "provider_intake_present",
                "published_control_reproduced",
                "quality_result_present",
                "reference_output_present",
                "release_claim",
                "rights_cleared_cohort_present",
                "runtime_present",
                "source_licensed",
                "source_present",
                "timing_result_present"):
            self.assertFalse(qualification[key], key)
        self.assertTrue(qualification["fixed_dsp_separated"])
        self.assertTrue(qualification["all_release_gates_blocked"])
        self.assertTrue(qualification["not_qualified"])


if __name__ == "__main__":
    unittest.main()
