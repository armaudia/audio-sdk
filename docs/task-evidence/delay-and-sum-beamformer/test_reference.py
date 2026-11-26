# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the synthetic delay-and-sum boundary baseline.

Run from this directory::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py

Every test is deterministic, stdlib-only and synthetic.  No real audio, model,
runtime, device or network is used.
"""

from __future__ import annotations

import json
import unittest

import reference


def geometry(case=None):
    return reference._case_geometry(case or reference.cases()[0])


class ExactSteeringTests(unittest.TestCase):
    def test_linear_endfire_delays_are_exact(self):
        normalized = reference.validate_geometry(geometry())
        self.assertEqual(normalized["relative_num_ns"],
                         [0, -21_437_500, -42_875_000])
        self.assertEqual(normalized["relative_q16"], [0, -65_536, -131_072])
        self.assertTrue(normalized["exact_integer_steering"])

    def test_planar_oblique_delays_are_exact(self):
        normalized = reference.validate_geometry(geometry(reference.cases()[1]))
        self.assertEqual(normalized["relative_num_ns"],
                         [0, -107_187_500, -321_562_500, -428_750_000])
        self.assertEqual(normalized["relative_q16"],
                         [0, -65_536, -196_608, -262_144])
        self.assertTrue(normalized["exact_integer_steering"])

    def test_one_sample_is_62500_ns(self):
        self.assertEqual(reference.SAMPLE_PERIOD_NS, 62_500)
        self.assertEqual(reference.SPEED_OF_SOUND_NM_PER_NS, 343)
        normalized = reference.validate_geometry(geometry())
        self.assertEqual(normalized["relative_num_ns"][1]
                         // normalized["steering_denominator_ns"], -62_500)

    def test_equal_weight_denominator_is_channel_count(self):
        normalized = reference.validate_geometry(geometry(reference.cases()[1]))
        self.assertEqual(normalized["equal_weight_denominator"], 4)
        result = reference.beamform(
            geometry(reference.cases()[1]),
            [[0.0] * 8 for _ in range(4)])
        self.assertEqual(result["equal_weights"], "1/4")

    def test_direction_must_have_integral_norm(self):
        bad = geometry()
        bad["steering_direction"] = [1, 1, 0]
        with self.assertRaises(reference.Reject) as raised:
            reference.validate_geometry(bad)
        self.assertEqual(raised.exception.code,
                         "steering_direction_not_exactly_normalizable")

    def test_zero_direction_rejected(self):
        bad = geometry()
        bad["steering_direction"] = [0, 0, 0]
        with self.assertRaises(reference.Reject) as raised:
            reference.validate_geometry(bad)
        self.assertEqual(raised.exception.code, "zero_steering_direction")

    def test_geometry_is_not_mutated(self):
        value = geometry()
        before = json.dumps(value, sort_keys=True)
        reference.validate_geometry(value)
        self.assertEqual(before, json.dumps(value, sort_keys=True))


class BeamformingTests(unittest.TestCase):
    def test_linear_case_recovers_declared_steering(self):
        result = reference._evaluate_case(reference.cases()[0])
        beamformed = result["beamformed"]
        self.assertTrue(result["arithmetic_exact_only"])
        self.assertEqual(beamformed["relative_q16"], [0, -65_536, -131_072])
        self.assertEqual(beamformed["peak_index"], 8)
        self.assertAlmostEqual(beamformed["peak_value"], 0.5)
        self.assertEqual(beamformed["max_abs_amplitude_error"], 0.0)
        self.assertTrue(beamformed["target_peak_preserved"])

    def test_planar_case_recovers_declared_steering(self):
        result = reference._evaluate_case(reference.cases()[1])
        beamformed = result["beamformed"]
        self.assertTrue(result["arithmetic_exact_only"])
        self.assertEqual(beamformed["relative_q16"],
                         [0, -65_536, -196_608, -262_144])
        self.assertEqual(beamformed["peak_index"], 16)
        self.assertAlmostEqual(beamformed["peak_value"], 0.5)
        self.assertEqual(beamformed["max_abs_amplitude_error"], 0.0)

    def test_fractional_control_is_labelled_non_exact(self):
        result = reference._evaluate_case(reference.fractional_case())
        beamformed = result["beamformed"]
        self.assertFalse(result["arithmetic_exact_only"])
        self.assertEqual(beamformed["relative_q16"], [0, -32_768, 32_768])
        self.assertEqual(beamformed["peak_index"], 8)
        self.assertAlmostEqual(beamformed["peak_value"], 17.0 / 30.0)
        self.assertFalse(beamformed["target_peak_preserved"])

    def test_identity_control_is_bit_identical(self):
        control = reference._identity_control()
        self.assertTrue(control["bit_identical"])
        self.assertEqual(control["input_digest"], control["output_digest"])

    def test_steering_mismatch_control_loses_coherence(self):
        control = reference._steering_mismatch_control()
        self.assertFalse(control["target_peak_preserved"])
        self.assertEqual(control["observed_peak_index"], 8)
        self.assertAlmostEqual(control["observed_peak_value"], 0.25)
        self.assertAlmostEqual(control["peak_value_ratio"], 0.5)

    def test_negative_reads_are_explicit_zero_padding(self):
        case = reference.cases()[0]
        geometry_ = geometry(case)
        fixture = reference.click_fixture(
            geometry_, case["length"], case["source_time_ns"],
            case["amplitudes"])
        result = reference.beamform(geometry_, fixture)
        self.assertEqual(result["relative_q16"], [0, -65_536, -131_072])
        self.assertEqual(len(result["output"]), case["length"])
        self.assertEqual(reference.peak(result["output"])["index"], 8)

    def test_silence_has_no_peak(self):
        case = reference.cases()[0]
        samples = [[0.0] * case["length"] for _ in case["mic_ids"]]
        result = reference.beamform(geometry(case), samples)
        self.assertIsNone(reference.peak(result["output"])["index"])

    def test_beamforming_digests_are_deterministic(self):
        case = reference.cases()[0]
        first = reference._evaluate_case(case)["beamformed"]["output_digest"]
        second = reference._evaluate_case(case)["beamformed"]["output_digest"]
        self.assertEqual(first, second)

    def test_click_out_of_range_rejected(self):
        case = reference.cases()[0]
        with self.assertRaises(reference.Reject) as raised:
            reference.click_fixture(geometry(case), 10, 0, [0.1, 0.1, 0.1])
        self.assertEqual(raised.exception.code, "click_out_of_range")

    def test_amplitude_count_mismatch(self):
        case = reference.cases()[0]
        with self.assertRaises(reference.Reject) as raised:
            reference.click_fixture(geometry(case), 24, 500_000, [0.1])
        self.assertEqual(raised.exception.code, "amplitude_count_mismatch")

    def test_nonfinite_amplitude_rejected(self):
        case = reference.cases()[0]
        with self.assertRaises(reference.Reject) as raised:
            reference.click_fixture(geometry(case), 24, 500_000,
                                    [0.1, float("inf"), 0.1])
        self.assertEqual(raised.exception.code, "nonfinite_amplitude")


class StrictJsonTests(unittest.TestCase):
    def test_valid_json_accepted(self):
        self.assertEqual(reference.parse_strict_json('{"a":[1,2],"b":null}'),
                         {"a": [1, 2], "b": None})

    def test_duplicate_key_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.parse_strict_json('{"a":1,"a":2}')
        self.assertEqual(raised.exception.code, "duplicate_json_key:a")

    def test_nan_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.parse_strict_json('{"a":NaN}')
        self.assertEqual(raised.exception.code, "nonfinite_json_constant:NaN")

    def test_infinity_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.parse_strict_json('{"a":-Infinity}')
        self.assertEqual(raised.exception.code,
                         "nonfinite_json_constant:-Infinity")

    def test_invalid_json_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.parse_strict_json('{"a":}')
        self.assertEqual(raised.exception.code, "invalid_json")

    def test_canonical_bytes_are_sorted_and_compact(self):
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": [2]}),
                         b'{"a":[2],"b":1}')

    def test_canonical_bytes_reject_nonfinite(self):
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"a": float("nan")})

    def test_tensor_digest_is_byte_stable(self):
        self.assertEqual(reference.tensor_digest([0.0, -0.0, 1.0]),
                         reference.tensor_digest([0.0, -0.0, 1.0]))
        self.assertNotEqual(reference.tensor_digest([0.0]),
                            reference.tensor_digest([1.0]))


class GeometryRejectionTests(unittest.TestCase):
    def _reject(self, mutate, code):
        value = geometry()
        mutate(value)
        with self.assertRaises(reference.Reject) as raised:
            reference.validate_geometry(value)
        self.assertEqual(raised.exception.code, code)

    def test_duplicate_position(self):
        self._reject(lambda g: g["microphones"][1].update(
            {"position_nm": [0, 0, 0]}), "duplicate_mic_position")

    def test_duplicate_mic_id(self):
        self._reject(lambda g: g["microphones"][1].update({"id": "m0"}),
                     "duplicate_mic_id")

    def test_unknown_reference(self):
        self._reject(lambda g: g.update({"reference_mic_id": "m9"}),
                     "unknown_reference_mic")

    def test_non_integer_position(self):
        self._reject(lambda g: g["microphones"][1].update(
            {"position_nm": [1.5, 0, 0]}), "invalid_position")

    def test_out_of_range_position(self):
        self._reject(lambda g: g["microphones"][1].update(
            {"position_nm": [reference.MAX_POSITION_NM + 1, 0, 0]}),
            "invalid_position")

    def test_unsupported_sample_rate(self):
        self._reject(lambda g: g.update({"sample_rate_hz": 48000}),
                     "unsupported_sample_rate")

    def test_unsupported_speed_of_sound(self):
        self._reject(lambda g: g.update({"speed_of_sound_nm_per_ns": 340}),
                     "unsupported_speed_of_sound")

    def test_missing_channel(self):
        self._reject(lambda g: g["channels"].pop(), "channel_mic_set_mismatch")

    def test_duplicate_channel(self):
        self._reject(lambda g: g["channels"][1].update({"mic_id": "m0"}),
                     "duplicate_channel_mic")

    def test_unknown_channel(self):
        self._reject(lambda g: g["channels"][1].update({"mic_id": "m9"}),
                     "unknown_channel_mic")

    def test_clock_drift_rejected(self):
        self._reject(lambda g: g["channels"][1].update({"clock_ppm": 5}),
                     "clock_drift_not_supported")

    def test_bool_clock_ppm_rejected(self):
        self._reject(lambda g: g["channels"][1].update({"clock_ppm": False}),
                     "clock_drift_not_supported")

    def test_uncalibrated_channel_rejected(self):
        self._reject(lambda g: g["channels"][1].update(
            {"calibration_gain_q16": 65_535}),
            "uncalibrated_channel_not_supported")

    def test_calibration_must_be_integer(self):
        self._reject(lambda g: g["channels"][1].update(
            {"calibration_gain_q16": 1.0}), "invalid_channel_calibration")

    def test_extra_geometry_field(self):
        self._reject(lambda g: g.update({"unexpected": 1}),
                     "invalid_geometry_fields")

    def test_geometry_not_object(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.validate_geometry([])
        self.assertEqual(raised.exception.code, "geometry_not_object")

    def test_too_few_microphones(self):
        value = geometry()
        value["microphones"] = [value["microphones"][0]]
        value["channels"] = [value["channels"][0]]
        with self.assertRaises(reference.Reject) as raised:
            reference.validate_geometry(value)
        self.assertEqual(raised.exception.code, "invalid_microphone_count")


class SampleRejectionTests(unittest.TestCase):
    def test_nan_sample_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.beamform(geometry(),
                               [[0.0] * 8, [float("nan")] * 8, [0.0] * 8])
        self.assertEqual(raised.exception.code, "nonfinite_sample")

    def test_infinite_sample_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.beamform(geometry(),
                               [[0.0] * 8, [float("inf")] * 8, [0.0] * 8])
        self.assertEqual(raised.exception.code, "nonfinite_sample")

    def test_invalid_sample_type_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.beamform(geometry(),
                               [[0.0] * 8, ["0"] * 8, [0.0] * 8])
        self.assertEqual(raised.exception.code, "invalid_sample_type")

    def test_length_mismatch_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.beamform(geometry(),
                               [[0.0] * 8, [0.0] * 7, [0.0] * 8])
        self.assertEqual(raised.exception.code, "channel_length_mismatch")

    def test_empty_channel_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.beamform(geometry(), [[], [], []])
        self.assertEqual(raised.exception.code, "invalid_channel_length")

    def test_channel_count_mismatch_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.beamform(geometry(), [[0.0] * 8, [0.0] * 8])
        self.assertEqual(raised.exception.code, "channel_count_mismatch")

    def test_oversized_sample_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.beamform(
                geometry(),
                [[0.0] * 8, [reference.MAX_ABS_SAMPLE + 1.0] * 8, [0.0] * 8])
        self.assertEqual(raised.exception.code, "nonfinite_sample")


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.text, cls.digest = reference.canonical_report(cls.report)

    def test_disposition_is_defer_incomplete_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification"]["status"],
                         "not_qualified")
        self.assertFalse(self.report["qualification"]["qualifies"])

    def test_eight_blocked_gates(self):
        self.assertEqual([gate["id"] for gate in self.report["release_gates"]],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in self.report["release_gates"]))

    def test_required_results_are_not_claimed(self):
        qualification = self.report["qualification"]
        self.assertFalse(qualification["all_required_results_present"])
        self.assertFalse(qualification["missing_result_promoted"])
        self.assertFalse(qualification["catalogued_candidate_executed"])
        candidate = self.report["candidate_execution"]
        self.assertEqual(candidate["status"], "blocked")
        self.assertFalse(candidate["present"])
        self.assertFalse(candidate["executed"])
        self.assertIsNone(candidate["result"])

    def test_spatial_profile_has_six_bounded_items(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "spatial")
        self.assertEqual(len(profile["required_items"]), 6)
        self.assertTrue(all(item["status"] in {"synthetic_only", "blocked"}
                            for item in profile["required_items"].values()))

    def test_every_case_is_surrogate_only(self):
        for case in self.report["spatial_cases"]:
            self.assertFalse(case["is_catalogued_candidate"])
            self.assertEqual(case["status"], "surrogate_only_not_qualified")
            self.assertEqual(case["qualification_status"], "not_qualified")
        fractional = self.report["fractional_steering_control"]
        self.assertEqual(fractional["status"], "surrogate_only_not_qualified")
        self.assertFalse(fractional["promoted"])
        mismatch = self.report["steering_mismatch_control"]
        self.assertEqual(mismatch["status"], "control_only_not_qualified")
        self.assertFalse(mismatch["target_peak_preserved"])

    def test_board_identity_is_gated_without_full_hash(self):
        row = self.report["board_row"]
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         row["stable_sha256"])
        self.assertNotIn("full_sha256", row)

    def test_adverse_cases_are_rejected(self):
        self.assertTrue(self.report["adverse_all_rejected"])
        self.assertEqual(len(self.report["adverse_rejections"]), 31)
        self.assertTrue(all(item["status"] == "rejected"
                            for item in self.report["adverse_rejections"]))

    def test_exact_cases_have_zero_error(self):
        for case in self.report["spatial_cases"]:
            self.assertTrue(case["arithmetic_exact_only"])
            beamformed = case["beamformed"]
            self.assertEqual(beamformed["max_abs_amplitude_error"], 0.0)
            self.assertTrue(beamformed["peak_index_match"])
            self.assertTrue(beamformed["peak_amplitude_match"])
            self.assertTrue(beamformed["target_peak_preserved"])

    def test_fractional_control_is_never_promoted(self):
        control = self.report["fractional_steering_control"]
        self.assertFalse(control["arithmetic_exact_only"])
        self.assertFalse(control["promoted"])
        self.assertEqual(control["status"], "surrogate_only_not_qualified")

    def test_repeatability_is_three_identical_digests(self):
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["runs"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["case_matrix_digests"])), 1)

    def test_report_is_byte_identical_across_builds(self):
        second = reference.build_report()
        self.assertEqual(self.text, reference.canonical_report(second)[0])
        self.assertEqual(self.digest, reference.canonical_report(second)[1])

    def test_report_excludes_mutable_board_pin(self):
        self.assertNotIn(reference.TASK_BOARD, self.report["source_pins"])
        self.assertNotIn(reference.TASK_BOARD, self.report["boundary_pins"])

    def test_boundary_claims_no_change(self):
        self.assertTrue(all(value is False
                            for value in self.report["boundary"].values()))

    def test_no_qualified_token_in_canonical_report(self):
        self.assertNotIn('"qualifies":true', self.text)
        self.assertNotIn('"status":"qualified"', self.text)


if __name__ == "__main__":
    unittest.main()
