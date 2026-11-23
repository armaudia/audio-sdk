"""Deterministic unittest coverage for the feed-forward compressor fixture.

Run from this directory with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
"""

from __future__ import annotations

import json
import math
import os
import re
import unittest
from pathlib import Path

import fixture

HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "report.json"
PROVIDER_DIR = HERE / "provider"


def workspace_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT")
    candidates = ([Path(override)] if override else [HERE, *HERE.parents])
    for candidate in candidates:
        if ((candidate / "REALTIME_COMPONENT_CANDIDATES.md").is_file()
                and (candidate / "research").is_dir()):
            return candidate
    raise AssertionError(
        "cannot locate workspace root; set AUDIOML_ROOT to the audioml directory")


def sdk_root() -> Path:
    for candidate in (HERE, *HERE.parents):
        if ((candidate / "api" / "include" / "audio_sdk" / "provider_v0.h").is_file()
                and (candidate / "CONTRACTS.md").is_file()):
            return candidate
    raise AssertionError("cannot locate the SDK worktree root")


class FeedForwardCompressorFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report_bytes = REPORT_PATH.read_bytes()
        cls.report = json.loads(cls.report_bytes)
        cls.fresh = fixture.build_report()
        cls.results = cls.report["results"]

    def test_source_pins_present_and_matching(self) -> None:
        root = workspace_root()
        sdk = sdk_root()
        self.assertEqual(len(fixture.SOURCE_PINS), 4)
        self.assertEqual(len(fixture.BOUNDARY_PINS), 2)
        for collection, base in ((fixture.SOURCE_PINS, root),
                                 (fixture.BOUNDARY_PINS, sdk)):
            for relative, expected in collection.items():
                path = base / relative
                self.assertTrue(path.is_file(), f"missing pinned source: {relative}")
                self.assertEqual(fixture.file_digest(path), expected, relative)

    def test_pinned_base_constant(self) -> None:
        expected = "0673cb354cceb66f2f71faf9af7703b5a5d2fcfa"
        self.assertEqual(fixture.BASE_COMMIT, expected)
        self.assertEqual(self.report["base_commit"], expected)
        self.assertEqual(self.fresh["base_commit"], expected)

    def test_report_is_canonical_and_reproducible(self) -> None:
        rebuilt = fixture.canonical_report(self.fresh)
        self.assertEqual(rebuilt, self.report_bytes)
        self.assertEqual(self.report_bytes[-1:], b"\n")
        self.assertNotIn(b": ", self.report_bytes)
        self.assertEqual(
            self.report_bytes,
            fixture.canonical_report(json.loads(self.report_bytes)))

    def test_report_schema_counts_and_completeness(self) -> None:
        self.assertEqual(self.report["schema_id"], fixture.REPORT_SCHEMA_ID)
        self.assertEqual(self.report["status"], "proposal-only/synthetic")
        self.assertEqual(self.report["completeness"]["missing_results"], [])
        self.assertTrue(self.report["completeness"]["all_present"])
        self.assertEqual(
            set(self.report["completeness"]["present_results"]),
            set(fixture.REQUIRED_RESULTS))
        self.assertEqual(self.report["counts"]["source_pins"], 4)
        self.assertEqual(self.report["counts"]["boundary_pins"], 2)
        self.assertEqual(self.report["counts"]["required_results"], 12)
        self.assertEqual(self.report["counts"]["expected_unittest_cases"], 26)
        self.assertEqual(self.report["counts"]["expected_ctest_runs"], 2)

    def test_qualification_gates_incomplete(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["candidate_qualification"], "not_qualified")
        for name in ("real_speech_listening", "nonlinear_interaction_release",
                     "device_timing"):
            entry = qualification[name]
            self.assertEqual(entry["status"], "incomplete", name)
            self.assertTrue(entry["blocker"], name)
            self.assertTrue(entry["reopen_trigger"], name)

    def test_source_pin_digests_in_report(self) -> None:
        self.assertEqual(self.report["source_pins"], fixture.SOURCE_PINS)
        self.assertEqual(self.report["boundary_pins"], fixture.BOUNDARY_PINS)
        self.assertEqual(self.report["fixture_digest"], self.fresh["fixture_digest"])

    def test_config_validation_accepts_default_and_rejects_adverse(self) -> None:
        self.assertIs(fixture.validate_config(fixture.DEFAULT_CONFIG), fixture.Status.OK)
        self.assertIs(fixture.validate_config(None), fixture.Status.REJECTED_MISSING)
        rejections = self.results["adverse_controls"]["config_rejections"]
        self.assertEqual(len(rejections), 18)
        self.assertTrue(all(value.startswith("rejected_")
                            for value in rejections.values()))

    def test_invalid_controls_are_recorded(self) -> None:
        rejections = self.results["adverse_controls"]["config_rejections"]
        expected = {
            "threshold_below_range": "rejected_invalid",
            "threshold_above_range": "rejected_invalid",
            "threshold_nonfinite": "rejected_nonfinite",
            "ratio_below_range": "rejected_invalid",
            "ratio_above_range": "rejected_invalid",
            "attack_zero": "rejected_invalid",
            "attack_above_range": "rejected_invalid",
            "attack_nonfinite": "rejected_nonfinite",
            "release_zero": "rejected_invalid",
            "release_above_range": "rejected_invalid",
            "makeup_negative": "rejected_invalid",
            "makeup_above_range": "rejected_invalid",
            "makeup_nonfinite": "rejected_nonfinite",
        }
        for key, status in expected.items():
            self.assertEqual(rejections[key], status, key)

    def test_silence_is_zero_and_unity_gain(self) -> None:
        silence = self.results["silence"]
        self.assertEqual(silence["status"], "ok")
        self.assertEqual(silence["frames"], 40)
        self.assertEqual(silence["peak_abs_output"], 0.0)
        self.assertEqual(silence["final_gain_db"], 0.0)
        expected_digest = fixture.tensor_digest(
            (0.0,) * (fixture.FRAME_SAMPLES * 40))
        self.assertEqual(silence["output_digest"], expected_digest)

    def test_impulse_delay_and_no_added_tail(self) -> None:
        impulse = self.results["impulse"]
        self.assertEqual(impulse["status"], "ok")
        self.assertEqual(impulse["peak_sample_index"], 0)
        self.assertEqual(impulse["content_delay_samples"], 0)
        self.assertAlmostEqual(impulse["peak_abs_output"], 0.9, places=9)
        self.assertEqual(impulse["tail_peak_10_to_20_ms"], 0.0)
        self.assertEqual(impulse["tail_peak_100_to_110_ms"], 0.0)

    def test_step_response_and_gain(self) -> None:
        step = self.results["step"]
        self.assertEqual(step["status"], "ok")
        self.assertEqual(step["crossing_samples_from_onset"], 0)
        self.assertAlmostEqual(step["peak_abs_output"], 0.7, places=9)
        expected = fixture.ideal_gain_db(0.7, fixture.DEFAULT_CONFIG)
        self.assertLess(abs(step["steady_gain_db"] - expected), 0.01)

    def test_amplitude_sweep_gain_law_beats_identity(self) -> None:
        sweep = self.results["amplitude_sweep"]
        self.assertEqual(sweep["points"], 100)
        self.assertLess(sweep["gain_law_rmse_db"], sweep["identity_rmse_db"])
        self.assertLess(sweep["gain_law_rmse_db"], 2.0)
        self.assertGreater(sweep["identity_rmse_db"], 10.0)
        self.assertEqual(len(sweep["per_point"]), 100)

    def test_frequency_response_is_flat_within_tolerance(self) -> None:
        response = self.results["frequency_response"]
        self.assertEqual(response["frequencies_hz"], len(fixture.FREQUENCIES_HZ))
        self.assertEqual(len(response["per_frequency"]), 39)
        self.assertLess(response["max_deviation_db"], 1.5)
        self.assertLess(response["min_gain_db"], response["max_gain_db"])

    def test_attack_release_gate_transitions(self) -> None:
        dynamics = self.results["attack_release"]
        self.assertEqual(dynamics["status"], "ok")
        self.assertIsNotNone(dynamics["attack_sample"])
        self.assertIsNotNone(dynamics["release_sample"])
        self.assertLess(dynamics["attack_ms"], 10.0)
        self.assertGreater(dynamics["release_ms"], dynamics["attack_ms"])
        self.assertEqual(len(dynamics["transitions"]), 2)
        self.assertIn("idle->active@", dynamics["transitions"][0])
        self.assertIn("active->idle@", dynamics["transitions"][1])

    def test_clean_speechlike_control_and_envelope_proxy(self) -> None:
        speech = self.results["clean_speechlike"]
        self.assertEqual(speech["frames"], 300)
        self.assertEqual(speech["status"], "ok")
        self.assertGreater(speech["reduced_frames"], 0)
        self.assertIsNotNone(speech["envelope_correlation"])
        self.assertGreater(speech["envelope_correlation"],
                           speech["hard_clip_control_correlation"])
        self.assertEqual(speech["intelligibility_claim"],
                         "none; synthetic envelope proxy only")

    def test_load_control_finite_and_bounded(self) -> None:
        load = self.results["load_control"]
        self.assertEqual(load["frames"], 100)
        self.assertEqual(load["nonfinite_output_samples"], 0)
        self.assertGreater(load["reduced_frames"], 0)
        self.assertLess(load["peak_abs_output"], 1.0)

    def test_peak_overshoot_and_limiter_headroom(self) -> None:
        headroom = self.results["headroom_peak_overshoot"]
        self.assertGreater(headroom["boosted_peak"], 1.0)
        self.assertGreater(headroom["samples_above_full_scale"], 0)
        self.assertLessEqual(headroom["limited_peak"], headroom["limiter_ceiling"])
        self.assertAlmostEqual(headroom["headroom_db"], 0.0, places=6)
        self.assertNotEqual(headroom["boosted_output_digest"],
                            headroom["limited_output_digest"])

    def test_reset_epoch_and_session_isolation(self) -> None:
        state = self.results["state_transitions"]
        self.assertEqual(state["reset_with_old_epoch"], "rejected_invalid")
        self.assertEqual(state["reset_with_higher_epoch"], "ok")
        self.assertTrue(state["reset_output_matches_fresh"])
        self.assertTrue(state["cross_session_isolation"])
        self.assertEqual(state["final_input_valid_count"], 5)
        self.assertEqual(state["final_input_source_first_sample"], 6400)
        self.assertEqual(state["process_after_final"], "rejected_state")

    def test_nonfinite_input_leaves_state_unchanged(self) -> None:
        inputs = self.results["adverse_controls"]["input_rejections"]
        self.assertEqual(inputs["nonfinite_input"], "rejected_nonfinite")
        self.assertTrue(inputs["state_unchanged_after_nonfinite"])
        self.assertTrue(inputs["state_unchanged_after_all_rejects"])
        self.assertEqual(inputs["rejection_counters"]["rejected_nonfinite"], 1)

    def test_wrong_frame_shape_stale_epoch_and_position_rejected(self) -> None:
        inputs = self.results["adverse_controls"]["input_rejections"]
        self.assertEqual(inputs["wrong_frame_shape"], "rejected_tensor")
        self.assertEqual(inputs["stale_epoch"], "rejected_epoch")
        self.assertEqual(inputs["wrong_position"], "rejected_state")
        self.assertEqual(inputs["out_of_range"], "rejected_invalid")

    def test_final_padding_and_flags_rejected(self) -> None:
        inputs = self.results["adverse_controls"]["input_rejections"]
        self.assertEqual(inputs["nonzero_final_padding"], "rejected_tensor")
        self.assertEqual(inputs["unknown_flags"], "rejected_invalid")

    def test_nonlinear_interactions_all_finite_and_order_sensitive(self) -> None:
        interactions = self.results["nonlinear_interactions"]
        self.assertEqual(set(interactions), {
            "compressor_only", "compressor_to_limiter", "limiter_to_compressor",
            "compressor_to_agc", "agc_to_compressor", "compressor_to_compressor"})
        for name, entry in interactions.items():
            self.assertEqual(entry["nonfinite_output_samples"], 0, name)
            self.assertLess(entry["peak_abs_output"], 2.0, name)
            self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", entry["output_digest"]), name)
        self.assertLessEqual(interactions["compressor_to_limiter"]["peak_abs_output"], 0.98)
        self.assertNotEqual(interactions["compressor_to_limiter"]["output_digest"],
                            interactions["limiter_to_compressor"]["output_digest"])
        self.assertEqual(interactions["compressor_to_compressor"]["output_digest"],
                         interactions["compressor_only"]["output_digest"])

    def test_output_digests_are_stable_64_hex(self) -> None:
        found = 0

        def walk(value: object) -> None:
            nonlocal found
            if isinstance(value, dict):
                for key, item in value.items():
                    if key.endswith("_digest") or key == "digest":
                        self.assertRegex(str(item), r"^[0-9a-f]{64}$", key)
                        found += 1
                    else:
                        walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(self.report)
        self.assertGreater(found, 15)
        self.assertEqual(self.report["fixture_digest"], self.fresh["fixture_digest"])

    def test_seeded_generators_are_deterministic(self) -> None:
        first = fixture.synthetic_speech(12, seed=123)
        second = fixture.synthetic_speech(12, seed=123)
        third = fixture.synthetic_speech(12, seed=124)
        self.assertEqual(fixture.tensor_digest(first), fixture.tensor_digest(second))
        self.assertNotEqual(fixture.tensor_digest(first), fixture.tensor_digest(third))
        self.assertEqual(len(first), fixture.FRAME_SAMPLES * 12)

    def test_no_real_assets_or_external_paths_in_report(self) -> None:
        text = self.report_bytes.decode("utf-8")
        for forbidden in (".wav", ".flac", ".mp3", "http://", "https://",
                          "/Users/", "DNS2020", "AMI", "EARS"):
            self.assertNotIn(forbidden, text, forbidden)
        self.assertEqual(len(self.report["non_claims"]), 5)
        self.assertTrue(all(isinstance(item, str) and item
                            for item in self.report["non_claims"]))

    def test_optional_provider_sources_pin_boundary_includes(self) -> None:
        source = (PROVIDER_DIR / "feed_forward_compressor.c").read_text()
        cmake = (PROVIDER_DIR / "CMakeLists.txt").read_text()
        self.assertIn('"audio_sdk/session_v0.h"', source)
        self.assertIn("AS_ENABLE_FEED_FORWARD_COMPRESSOR", cmake)
        self.assertIn("OFF", cmake)
        self.assertIn("find_package(AudioSDK 0.1 CONFIG REQUIRED)", cmake)
        self.assertNotIn("CONTRACTS.md", source)
        self.assertNotIn("add_subdirectory", cmake)
        self.assertTrue((PROVIDER_DIR / "config" / "config.json").is_file())
        self.assertTrue((PROVIDER_DIR / "config" / "descriptor.h.in").is_file())
        self.assertTrue((PROVIDER_DIR / "tests" / "test_provider.c").is_file())


if __name__ == "__main__":
    unittest.main()
