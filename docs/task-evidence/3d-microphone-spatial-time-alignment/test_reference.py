# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the synthetic geometry/alignment boundary model.

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


class ExactGeometryTests(unittest.TestCase):
    def test_axis_tdoa_is_exact(self):
        normalized = reference.validate_geometry(geometry())
        self.assertEqual(normalized["tdoa_ns"], [0, -62_500, -125_000])
        self.assertEqual(normalized["relative_ns"], [0, -187_500, -62_500])
        self.assertEqual(normalized["relative_q16"], [0, -196_608, -65_536])
        self.assertTrue(normalized["exact_integer_alignment"])

    def test_pythagorean_tdoa_is_exact(self):
        normalized = reference.validate_geometry(geometry(reference.cases()[1]))
        self.assertEqual(normalized["tdoa_ns"], [0, -60_000, -80_000, -70_000])
        self.assertEqual(normalized["relative_ns"],
                         [0, -62_500, -125_000, -187_500])
        self.assertEqual(normalized["relative_q16"],
                         [0, -65_536, -131_072, -196_608])
        self.assertTrue(normalized["exact_integer_alignment"])

    def test_one_sample_is_62500_ns(self):
        self.assertEqual(reference.SAMPLE_PERIOD_NS, 62_500)
        self.assertEqual(reference.SPEED_OF_SOUND_NM_PER_NS, 343)
        normalized = reference.validate_geometry(geometry())
        self.assertEqual(normalized["relative_ns"][1] // reference.SAMPLE_PERIOD_NS, -3)

    def test_direction_must_have_integral_norm(self):
        bad = geometry()
        bad["source_direction"] = [1, 1, 0]
        with self.assertRaises(reference.Reject) as raised:
            reference.validate_geometry(bad)
        self.assertEqual(raised.exception.code, "direction_not_exactly_normalizable")

    def test_zero_direction_rejected(self):
        bad = geometry()
        bad["source_direction"] = [0, 0, 0]
        with self.assertRaises(reference.Reject) as raised:
            reference.validate_geometry(bad)
        self.assertEqual(raised.exception.code, "zero_direction")

    def test_geometry_is_not_mutated(self):
        value = geometry()
        before = json.dumps(value, sort_keys=True)
        reference.validate_geometry(value)
        self.assertEqual(before, json.dumps(value, sort_keys=True))


class AlignmentTests(unittest.TestCase):
    def test_axis_case_recovers_declared_delay_and_amplitude(self):
        case = reference.cases()[0]
        result = reference._evaluate_case(case)
        aligned = result["aligned"]
        self.assertTrue(result["exact"])
        self.assertEqual(aligned["recovered_peak_indices"], [8, 8, 8])
        self.assertEqual(aligned["recovered_peak_values"], [0.75, -0.5, 0.25])
        self.assertEqual(aligned["max_abs_amplitude_error"], 0.0)

    def test_planar_case_recovers_declared_delay_and_amplitude(self):
        case = reference.cases()[1]
        result = reference._evaluate_case(case)
        aligned = result["aligned"]
        self.assertTrue(result["exact"])
        self.assertEqual(aligned["recovered_peak_indices"], [16, 16, 16, 16])
        self.assertEqual(aligned["recovered_peak_values"],
                         [1.0, -0.75, 0.5, -0.25])
        self.assertEqual(aligned["max_abs_amplitude_error"], 0.0)

    def test_fractional_control_is_labelled_non_exact(self):
        result = reference._evaluate_case(reference.fractional_case())
        self.assertFalse(result["exact"])
        self.assertEqual(result["aligned"]["relative_q16"], [0, -32_768, 32_768])
        self.assertEqual(result["aligned"]["recovered_peak_indices"], [8, 8, 8])
        self.assertAlmostEqual(result["aligned"]["recovered_peak_values"][1], 0.3)
        self.assertAlmostEqual(result["aligned"]["recovered_peak_values"][2], -0.2)

    def test_reference_channel_is_identity(self):
        control = reference._identity_control()
        self.assertTrue(control["bit_identical"])
        self.assertEqual(control["relative_q16_reference"], 0)

    def test_negative_reads_are_explicit_zero_padding(self):
        case = reference.cases()[0]
        result = reference._evaluate_case(case)
        aligned = reference.align_channels(
            geometry(case), reference.click_fixture(
                geometry(case), case["length"], case["source_time_ns"],
                case["amplitudes"]))
        self.assertEqual(aligned["leading_zeros"][1], 8)
        self.assertEqual(len(aligned["outputs"][1]), case["length"])
        self.assertEqual(result["aligned"]["recovered_peak_indices"][1], 8)

    def test_silence_has_no_peak(self):
        case = reference.cases()[0]
        samples = [[0.0] * case["length"] for _ in case["mic_ids"]]
        aligned = reference.align_channels(geometry(case), samples)
        self.assertEqual([reference.peak(channel)["index"]
                          for channel in aligned["outputs"]], [None] * 3)

    def test_alignment_digests_are_deterministic(self):
        case = reference.cases()[0]
        first = reference._evaluate_case(case)["aligned"]["output_digests"]
        second = reference._evaluate_case(case)["aligned"]["output_digests"]
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
        self.assertEqual(raised.exception.code, "nonfinite_json_constant:-Infinity")

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

    def test_capture_offset_out_of_range(self):
        self._reject(lambda g: g["channels"][1].update(
            {"capture_offset_ns": reference.MAX_CAPTURE_OFFSET_NS + 1}),
            "capture_offset_out_of_range")

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
            reference.align_channels(geometry(),
                                     [[0.0] * 8, [float("nan")] * 8, [0.0] * 8])
        self.assertEqual(raised.exception.code, "nonfinite_sample")

    def test_infinite_sample_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.align_channels(geometry(),
                                     [[0.0] * 8, [float("inf")] * 8, [0.0] * 8])
        self.assertEqual(raised.exception.code, "nonfinite_sample")

    def test_invalid_sample_type_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.align_channels(geometry(),
                                     [[0.0] * 8, ["0"] * 8, [0.0] * 8])
        self.assertEqual(raised.exception.code, "invalid_sample_type")

    def test_length_mismatch_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.align_channels(geometry(),
                                     [[0.0] * 8, [0.0] * 7, [0.0] * 8])
        self.assertEqual(raised.exception.code, "channel_length_mismatch")

    def test_empty_channel_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.align_channels(geometry(), [[], [], []])
        self.assertEqual(raised.exception.code, "invalid_channel_length")

    def test_channel_count_mismatch_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.align_channels(geometry(), [[0.0] * 8, [0.0] * 8])
        self.assertEqual(raised.exception.code, "channel_count_mismatch")

    def test_oversized_sample_rejected(self):
        with self.assertRaises(reference.Reject) as raised:
            reference.align_channels(
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
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertFalse(self.report["qualification"]["qualifies"])

    def test_eight_blocked_gates(self):
        self.assertEqual([gate["id"] for gate in self.report["release_gates"]],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in self.report["release_gates"]))

    def test_required_results_are_not_claimed(self):
        self.assertFalse(self.report["qualification"]["all_required_results_present"])
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])
        self.assertFalse(self.report["real_recordings"]["present"])
        self.assertFalse(self.report["real_recordings"]["executed"])
        self.assertIsNone(self.report["real_recordings"]["result"])

    def test_spatial_profile_has_six_blocked_items(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "spatial")
        self.assertEqual(len(profile["required_items"]), 6)
        self.assertTrue(all(item["status"] in {"synthetic_only", "blocked"}
                            for item in profile["required_items"].values()))

    def test_board_identity_is_gated_without_full_hash(self):
        row = self.report["board_row"]
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         row["stable_sha256"])
        self.assertNotIn("full_sha256", row)

    def test_adverse_cases_are_rejected(self):
        self.assertTrue(self.report["adverse_all_rejected"])
        self.assertEqual(len(self.report["adverse_rejections"]), 23)
        self.assertTrue(all(item["status"] == "rejected"
                            for item in self.report["adverse_rejections"]))

    def test_exact_cases_have_zero_error(self):
        for case in self.report["known_synthetic_delays"]:
            self.assertTrue(case["exact"])
            self.assertEqual(case["aligned"]["max_abs_amplitude_error"], 0.0)
            self.assertTrue(case["aligned"]["index_match"])
            self.assertTrue(case["aligned"]["amplitude_match"])

    def test_fractional_control_is_never_promoted(self):
        control = self.report["fractional_residual_control"]
        self.assertFalse(control["exact"])
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
