# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local tests for the differentiable-biquad EQ evidence reference."""

from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference

_CACHE = {}


def build_once():
    if "report" not in _CACHE:
        _CACHE["report"] = reference.build_report()
    return _CACHE["report"]


class JsonTests(unittest.TestCase):
    def test_canonical_sorted_and_compact(self) -> None:
        self.assertEqual(reference.canonical_text({"b": 1, "a": [2]}),
                         '{"a":[2],"b":1}')

    def test_canonical_negative_zero_is_positive(self) -> None:
        self.assertEqual(reference.canonical_text({"x": -0.0}), '{"x":0.0}')

    def test_canonical_rejects_nonfinite(self) -> None:
        for value in (float("nan"), float("inf"), -float("inf")):
            with self.assertRaises(reference.Reject):
                reference.canonical_bytes({"x": value})

    def test_strict_rejects_duplicate_and_constants(self) -> None:
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
                     '[1,2]', ''):
            with self.assertRaises(reference.Reject):
                reference.strict_loads(text)

    def test_strict_accepts_object(self) -> None:
        self.assertEqual(reference.strict_loads('{"a":1}'), {"a": 1})


class BiquadTests(unittest.TestCase):
    def test_zero_gain_is_identity_response(self) -> None:
        bands = tuple((freq, quality, 0.0) for freq, quality in
                      reference.MODEL_BANDS)
        for freq in reference.ALL_PROBES:
            self.assertAlmostEqual(reference.response_db(freq, bands), 0.0,
                                   places=12)

    def test_peaking_center_matches_gain(self) -> None:
        for gain in (-12.0, -3.0, 0.5, 6.0, 12.0):
            bands = ((1000.0, 0.9, gain),)
            self.assertAlmostEqual(reference.response_db(1000.0, bands),
                                   gain, places=9)

    def test_cascade_products(self) -> None:
        first = ((125.0, 0.9, 3.0),)
        second = ((4000.0, 0.9, -2.0),)
        for freq in reference.ALL_PROBES:
            combined = reference.response_db(freq, first + second)
            expected = (reference.response_db(freq, first)
                        + reference.response_db(freq, second))
            self.assertAlmostEqual(combined, expected, places=12)

    def test_poles_inside_unit_circle(self) -> None:
        for gain in (-24.0, -6.0, 0.0, 6.0, 24.0):
            for freq, quality in reference.MODEL_BANDS:
                self.assertLess(
                    reference.pole_radius(freq, quality, gain), 1.0)

    def test_zero_gain_impulse_is_identity(self) -> None:
        bands = tuple((freq, quality, 0.0) for freq, quality in
                      reference.MODEL_BANDS)
        impulse = [1.0] + [0.0] * 63
        output, _ = reference.filter_samples(impulse, bands)
        self.assertEqual(output[0], 1.0)
        self.assertTrue(all(value == 0.0 for value in output[1:]))

    def test_frame_and_whole_are_identical(self) -> None:
        signals = reference._synthetic_speech(1600)
        whole, _ = reference.filter_samples(signals, reference.DEVICE_RESPONSE)
        framed = []
        state = None
        for start in range(0, len(signals), reference.SDK_FRAME_SAMPLES):
            chunk, state = reference.filter_samples(
                signals[start:start + reference.SDK_FRAME_SAMPLES],
                reference.DEVICE_RESPONSE, state)
            framed.extend(chunk)
        self.assertEqual(whole, framed)

    def test_reset_isolates_state(self) -> None:
        impulse = [1.0] + [0.0] * 255
        first, _ = reference.filter_samples(impulse,
                                            reference.DEVICE_RESPONSE)
        second, _ = reference.filter_samples(impulse,
                                             reference.DEVICE_RESPONSE)
        self.assertEqual(first, second)

    def test_silence_is_silent(self) -> None:
        output, _ = reference.filter_samples([0.0] * 160,
                                             reference.DEVICE_RESPONSE)
        self.assertTrue(all(value == 0.0 for value in output))

    def test_invalid_inputs_rejected(self) -> None:
        cases = [
            lambda: reference.filter_samples([float("nan")],
                                             reference.MODEL_BANDS),
            lambda: reference.filter_samples([float("inf")],
                                             reference.MODEL_BANDS),
            lambda: reference.filter_samples(["0.1"], reference.MODEL_BANDS),
            lambda: reference.filter_samples([], reference.MODEL_BANDS),
            lambda: reference.biquad_coefficients(1000.0, 0.0, 0.0),
            lambda: reference.biquad_coefficients(1000.0, -1.0, 0.0),
            lambda: reference.biquad_coefficients(0.0, 1.0, 0.0),
            lambda: reference.biquad_coefficients(8000.0, 1.0, 0.0),
            lambda: reference.biquad_coefficients(1000.0, 1.0, float("nan")),
            lambda: reference.biquad_coefficients(1000.0, 1.0, float("inf")),
            lambda: reference.biquad_coefficients(1000.0, 1.0, 24.5),
            lambda: reference.filter_samples([0.1], reference.MODEL_BANDS,
                                             {"sections": []}),
        ]
        for case in cases:
            with self.assertRaises(reference.Reject):
                case()


class GradientTests(unittest.TestCase):
    def test_complex_step_matches_finite_difference(self) -> None:
        gains = (0.7, -1.2, 0.4)
        target = reference._target_db(reference.EXACT_TRUTH,
                                      reference.ALL_PROBES)
        cs = reference._gain_gradient(reference.MODEL_BANDS, gains,
                                      reference.ALL_PROBES, target)
        fd = reference._finite_difference_gradient(
            reference.MODEL_BANDS, gains, reference.ALL_PROBES, target)
        for a, b in zip(cs, fd):
            self.assertAlmostEqual(a, b, places=4)

    def test_exact_recovery(self) -> None:
        target = reference._target_db(reference.EXACT_TRUTH,
                                      reference.ALL_PROBES)
        result = reference._fit(reference.MODEL_BANDS, reference.ALL_PROBES,
                                target, reference.EXACT_ITERS,
                                reference.EXACT_LR, 12.0)
        self.assertLess(result["final_rmse_db"], 1e-6)
        for recovered, truth in zip(result["gains_db"],
                                    reference.EXACT_TRUTH):
            self.assertAlmostEqual(recovered, truth[2], places=5)


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_once()
        cls.control = cls.report["reference_protocol"]["synthetic_control"]

    def test_control_is_labelled_and_nonqualifying(self) -> None:
        self.assertEqual(self.control["label"], reference.SURROGATE_LABEL)
        self.assertEqual(self.control["qualification_effect"], "none")
        self.assertIs(self.control["candidate_model_executed"], False)

    def test_gradient_check_passes(self) -> None:
        check = self.control["gradient_check"]
        self.assertIs(check["passes"], True)
        self.assertLess(check["max_abs_difference"], 1e-4)

    def test_device_recovery_respects_gain_limit(self) -> None:
        device = self.control["device_recovery"]
        self.assertIs(device["qualifies"], False)
        self.assertEqual(
            device["split_label"],
            "synthetic_frequency_holdout_not_device_or_speaker_split")
        self.assertGreater(device["train_rmse_db"], 0.0)
        self.assertGreater(device["heldout_rmse_db"], 0.0)
        for gain in device["gains_db"]:
            self.assertLessEqual(abs(gain), device["gain_limit_db"])

    def test_average_controls_do_not_qualify(self) -> None:
        for item in self.control["adverse"]:
            self.assertIs(item["qualifies"], False)
        self.assertEqual(len(self.control["adverse"]), 4)

    def test_dsp_measurements(self) -> None:
        measurements = self.control["dsp_measurements"]
        self.assertIs(measurements["sweep"]["finite"], True)
        self.assertEqual(measurements["impulse"]["delay_samples"], 0)
        self.assertIs(measurements["silence"]["all_zero"], True)
        self.assertIs(measurements["frame_vs_whole"]["identical"], True)
        self.assertIs(measurements["reset"]["isolated"], True)
        self.assertIs(measurements["nonlinear_interaction"]["finite"], True)
        self.assertLessEqual(measurements["nonlinear_interaction"]["peak"], 1.0)
        self.assertGreater(measurements["headroom"]["near_clip_clipped_samples"],
                           0)

    def test_rejections_all_rejected(self) -> None:
        self.assertIs(self.control["rejections"]["all_rejected"], True)
        self.assertEqual(self.control["rejections"]["count"], 12)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_once()
        cls.text, cls.digest = reference.canonical_report(cls.report)

    def test_decision_and_qualification(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["blocked_gate_count"], 8)
        self.assertIs(self.report["qualification"]["candidate_qualified"], False)

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-0{index}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual(len(self.report["exact_blockers"]), 8)

    def test_no_candidate_metric(self) -> None:
        self.assertIsNone(self.report["candidate_metrics"])
        self.assertIsNone(self.report["dsp_profile"]["real_model_metrics"])
        self.assertEqual(
            self.report["dsp_profile"]["satisfied_for_qualification"], [])

    def test_task_identity_never_hashes_whole_file(self) -> None:
        identity = self.report["task_row_identity"]
        self.assertIs(identity["whole_file_hashed"], False)
        stable = identity["stable_fields"]
        self.assertEqual(
            identity["stable_sha256"],
            reference.sha256_bytes(reference.canonical_bytes(stable)))

    def test_admission_controls(self) -> None:
        admission = self.report["admission_controls"]
        self.assertEqual(admission["adverse_count"], 60)
        self.assertIs(admission["adverse_all_rejected"], True)
        self.assertIs(admission["strict_json_all_rejected"], True)
        positive = admission["positive_control"]
        self.assertIs(positive["accepted"], True)
        self.assertIs(positive["qualifies"], False)
        self.assertIs(positive["executed"], False)

    def test_asset_audit_absent(self) -> None:
        audit = self.report["asset_audit"]
        self.assertEqual(audit["audit_result"], "absent")
        self.assertIs(audit["any_present"], False)
        self.assertIs(audit["qualified"], False)

    def test_canonical_round_trip(self) -> None:
        parsed = reference.strict_loads(self.text)
        self.assertEqual(reference.canonical_text(parsed), self.text[:-1])
        self.assertEqual(reference.sha256_bytes(self.text.encode()),
                         self.digest)

    def test_no_boolean_true_qualification_flags(self) -> None:
        encoded = json.dumps(self.report)
        self.assertNotIn("candidate_qualified\": true", encoded)
        self.assertNotIn("accepted_manifest_qualifies\": true", encoded)


class AdmissionTests(unittest.TestCase):
    def test_positive_control_never_qualifies(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbq-test-") as directory:
            manifest = reference._synthetic_admission_tree(Path(directory))
            result = reference.validate_manifest(manifest)
        self.assertIs(result["accepted"], True)
        self.assertIs(result["qualifies"], False)

    def test_missing_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbq-test-") as directory:
            manifest = reference._synthetic_admission_tree(Path(directory))
            manifest.pop("weights_sha256")
            with self.assertRaises(reference.Reject):
                reference.validate_manifest(manifest)

    def test_qualified_claim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbq-test-") as directory:
            manifest = reference._synthetic_admission_tree(Path(directory))
            manifest["claims_qualified"] = True
            with self.assertRaises(reference.Reject):
                reference.validate_manifest(manifest)

    def test_wrong_digest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbq-test-") as directory:
            manifest = reference._synthetic_admission_tree(Path(directory))
            manifest["weights_sha256"] = "0" * 64
            with self.assertRaises(reference.Reject):
                reference.validate_manifest(manifest)

    def test_nonfinite_value_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dbq-test-") as directory:
            manifest = reference._synthetic_admission_tree(Path(directory))
            manifest["gain_limit_db"] = float("nan")
            with self.assertRaises(reference.Reject):
                reference.validate_manifest(manifest)


class SourcePinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_once()

    def test_source_and_boundary_pins_match_files(self) -> None:
        for path, digest in reference.SOURCE_PINS.items():
            target = reference.SOURCE_ROOT / path
            self.assertTrue(target.is_file(), path)
            self.assertEqual(reference.sha256_bytes(target.read_bytes()),
                             digest, path)
        for path, digest in reference.BOUNDARY_PINS.items():
            target = reference.SDK_ROOT / path
            self.assertTrue(target.is_file(), path)
            self.assertEqual(reference.sha256_bytes(target.read_bytes()),
                             digest, path)

    def test_report_pins_are_constant(self) -> None:
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.report["boundary_pins"],
                         reference.BOUNDARY_PINS)


if __name__ == "__main__":
    unittest.main()
