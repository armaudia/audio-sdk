# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit and byte-identity controls for the logistic feedback reference."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import unittest

import reference as ref

HERE = Path(__file__).resolve().parent
REPORT = json.loads((HERE / "report.json").read_text(encoding="utf-8"))
MODEL = json.loads((HERE / "model.json").read_text(encoding="utf-8"))
CROSSCHECK = json.loads((HERE / "crosscheck_vectors.json").read_text(encoding="utf-8"))


class LogisticReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = ref.build_fixture()

    def test_01_fixture_is_deterministic(self):
        self.assertEqual(ref.build_fixture()["digest"], self.fixture["digest"])
        self.assertEqual(self.fixture["digest"], REPORT["fixture"]["digest"])

    def test_02_fixed_v0_format(self):
        self.assertEqual((ref.RATE, ref.FRAME), (16000, 160))
        self.assertEqual(REPORT["scope"]["fixed_v0_format"]["frame_samples"], 160)
        self.assertEqual(REPORT["scope"]["source_uses_256_sample_frames"], 256)

    def test_03_feature_sample_matches_pinned_source(self):
        for local, source in zip(CROSSCHECK["feature_sample_local"],
                                 CROSSCHECK["feature_sample_source"]):
            self.assertLessEqual(abs(local - source), 1e-11)

    def test_04_source_fit_matches_local_fit(self):
        clip = self.fixture["clips"][0]
        path = self.fixture["train_paths"][0]
        target = ref.make_target(clip)
        simulation = ref.simulate_closed_loop(
            target, ref.IdentityController(), path["impulse"], 1.05)
        features, labels = ref.frame_dataset(
            target, simulation["output"], simulation["feedback"])
        fitted = ref.fit_logistic(features, labels)
        expected = CROSSCHECK["local_training"]
        for key in ("weights", "mean", "scale"):
            for actual, wanted in zip(fitted[key], expected[key]):
                self.assertLessEqual(abs(actual - wanted), 1e-12, key)
        self.assertLessEqual(abs(fitted["intercept"] - expected["intercept"]), 1e-12)
        self.assertEqual(fitted["threshold"], expected["threshold"])
        self.assertEqual(fitted["training_frames"], len(labels))

    def test_05_source_detection_counts_match(self):
        local = CROSSCHECK["local_detection"]
        source = CROSSCHECK["source_detection"]
        for key in ("frames", "positive_frames", "true_positive", "false_positive",
                    "false_negative", "true_negative", "precision", "recall",
                    "false_positive_rate"):
            self.assertEqual(local[key], source[key], key)
        self.assertTrue(CROSSCHECK["detection_counts_equal"])

    def test_06_crosscheck_deltas_within_tolerance(self):
        for key, value in CROSSCHECK["max_absolute_deltas"].items():
            self.assertTrue(math.isfinite(value), key)
            self.assertLess(value, 1e-7, key)
        self.assertEqual(CROSSCHECK["source_pins"]["scripts/evaluate_feedback_control_ml.py"],
                         "e6cd1903cce7724a15c6ef162b59b8fc27dbf1a80ba5e47ebaa66a3845276d04")

    def test_07_report_and_model_digests(self):
        report_bytes = (HERE / "report.json").read_bytes()
        digest = hashlib.sha256(report_bytes).hexdigest()
        self.assertEqual(digest, (HERE / "report.json.sha256").read_text().strip())
        self.assertEqual(digest, hashlib.sha256(ref.canonical_bytes(REPORT)).hexdigest())
        self.assertEqual(hashlib.sha256(ref.canonical_bytes(MODEL)).hexdigest(),
                         REPORT["training"]["model_digest"])
        self.assertEqual(REPORT["crosscheck_digest"], ref._digest(CROSSCHECK))

    def test_08_byte_identical_regeneration(self):
        before = (HERE / "report.json").read_bytes()
        before_model = (HERE / "model.json").read_bytes()
        ref.write_outputs()
        self.assertEqual((HERE / "report.json").read_bytes(), before)
        self.assertEqual((HERE / "model.json").read_bytes(), before_model)

    def test_09_heldout_matrix_is_complete(self):
        self.assertEqual(len(REPORT["fixture"]["heldout_runs"]), 27)
        self.assertEqual(len(REPORT["per_run"]), 27 * 4)
        self.assertEqual(len(REPORT["stratified_heldout"]), 9)
        self.assertEqual(REPORT["heldout_detection_metrics"]["frames"], 4050)
        for row in REPORT["per_run"]:
            for key in ("sdr_db", "tail_output_to_speech_db", "output_peak",
                        "headroom_db", "detection_events", "nonfinite_samples"):
                self.assertIn(key, row)

    def test_10_all_candidates_have_results(self):
        self.assertEqual(set(REPORT["candidate_summaries"]),
                         set(ref.fixture_spec()["candidates"]))
        for summary in REPORT["candidate_summaries"].values():
            self.assertEqual(summary["n_runs"], 27)
            self.assertEqual(summary["nonfinite_runs"], 0)
            self.assertEqual(summary["clipped_runs"], 0)

    def test_11_identity_and_static_controls(self):
        identity = REPORT["candidate_summaries"]["identity"]
        static = REPORT["candidate_summaries"]["fixed_gain_minus_5db"]
        logistic = REPORT["candidate_summaries"]["logistic_reference"]
        self.assertIsNone(identity["clean_speech_median_sdr_db"])
        self.assertAlmostEqual(static["clean_speech_median_sdr_db"], 7.177, places=2)
        self.assertIsNone(logistic["clean_speech_median_sdr_db"])
        self.assertGreater(logistic["median_sdr_db"], identity["median_sdr_db"])
        self.assertLess(logistic["median_tail_output_to_speech_db"],
                        identity["median_tail_output_to_speech_db"])

    def test_12_static_fallback_missing_or_invalid_model(self):
        tone = [0.1 * math.sin(2 * math.pi * 1000 * index / ref.RATE)
                for index in range(ref.FRAME)]
        for candidate in (None, dict(MODEL, threshold=1.5),
                          dict(MODEL, weights=[float("nan")] + MODEL["weights"][1:])):
            controller = ref.LogisticGainController(candidate)
            output = controller.process(tone)
            self.assertEqual(controller.mode, "static_fallback")
            self.assertAlmostEqual(output[1] / tone[1], 10 ** (-5 / 20), places=12)
        self.assertEqual(REPORT["static_fallback"]["gain_db"], -5.0)

    def test_13_nonfinite_frames_rejected_without_state_change(self):
        self.assertEqual(REPORT["controls"]["nonfinite_frames_rejected"], 2)
        self.assertTrue(REPORT["controls"]["state_unchanged_after_rejection"])
        controller = ref.LogisticGainController(MODEL)
        tone = [0.1 * math.sin(2 * math.pi * 1000 * index / ref.RATE)
                for index in range(ref.FRAME)]
        controller.process(tone)
        before = (controller.gain, controller.hold, controller.previous_rms,
                  controller.detection_events)
        with self.assertRaises(ValueError):
            controller.process([float("nan")] * ref.FRAME)
        self.assertEqual(before, (controller.gain, controller.hold,
                                  controller.previous_rms, controller.detection_events))

    def test_14_state_reset_and_independence(self):
        self.assertTrue(REPORT["controls"]["reset_replays_exactly"])
        self.assertTrue(REPORT["controls"]["sessions_independent"])

    def test_15_alignment_and_partial_frame(self):
        self.assertEqual(REPORT["controls"]["impulse_added_delay_samples"], 0)
        self.assertTrue(REPORT["controls"]["partial_frame_length_preserved"])
        controller = ref.LogisticGainController(MODEL)
        self.assertEqual(len(controller.process([0.01] * 37)), 37)

    def test_16_headroom_and_finite_behavior(self):
        for row in REPORT["per_run"]:
            self.assertLess(row["output_peak"], 1.0)
            self.assertLess(row["headroom_db"], 0.0)
            self.assertEqual(row["nonfinite_samples"], 0)
            self.assertGreaterEqual(row["final_gain_db"], -12.001)

    def test_17_report_path_has_no_numpy(self):
        source = (HERE / "reference.py").read_text(encoding="utf-8")
        imports = re.findall(r"^\s*(?:import|from)\s+(\w+)", source, re.MULTILINE)
        self.assertNotIn("numpy", imports)
        self.assertNotIn("scipy", imports)
        self.assertNotIn("soundfile", imports)

    def test_18_no_release_claims(self):
        scope = REPORT["scope"]
        self.assertTrue(scope["optional_reference_only"])
        self.assertFalse(scope["real_model_weights"])
        self.assertFalse(scope["downloads"])
        self.assertFalse(scope["device_timing"])
        self.assertFalse(scope["release_claim"])

    def test_19_c_provider_uses_pinned_model_constants(self):
        source = (HERE / "provider/logistic_feedback_provider.c").read_text(encoding="utf-8")
        for name, values in (("kWeights", MODEL["weights"]),
                             ("kMean", MODEL["mean"]),
                             ("kScale", MODEL["scale"])):
            pattern = rf"static const double {name}\[LOGISTIC_FEATURES\] = \{{(.*?)\}};"
            block = re.search(pattern, source, re.DOTALL)
            self.assertIsNotNone(block, name)
            constants = [float(value) for value in re.findall(r"-?\d+\.\d+", block.group(1))]
            self.assertEqual(constants, values, name)
        intercept = re.search(r"static const double kIntercept = ([^;]+);", source)
        threshold = re.search(r"static const double kThreshold = ([^;]+);", source)
        self.assertEqual(float(intercept.group(1)), MODEL["intercept"])
        self.assertEqual(float(threshold.group(1)), MODEL["threshold"])


if __name__ == "__main__":
    unittest.main()
