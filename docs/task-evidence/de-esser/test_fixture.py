"""Deterministic unittest coverage for the task-local de-esser fixture.

Run from this directory with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py

Licensing for this task-local directory is covered by the repository-level
REUSE annotation for docs/**.
"""

from __future__ import annotations

import json
import os
import re
import unittest
from pathlib import Path
from typing import List

import fixture

HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "report.json"
PROVIDER_DIR = HERE / "provider"
SDK_MARKER = Path("api/include/audio_sdk/provider_v0.h")


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
        if ((candidate / SDK_MARKER).is_file()
                and (candidate / "CONTRACTS.md").is_file()):
            return candidate
    raise AssertionError("cannot locate the SDK worktree root")


class DeesserFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report_bytes = REPORT_PATH.read_bytes()
        cls.report = json.loads(cls.report_bytes)
        cls.fresh = fixture.build_report()
        cls.results = cls.report["results"]

    def test_source_pins_present_and_matching(self) -> None:
        root = workspace_root()
        sdk = sdk_root()
        self.assertEqual(len(fixture.SOURCE_PINS), 5)
        self.assertEqual(len(fixture.BOUNDARY_PINS), 2)
        for collection, base in ((fixture.SOURCE_PINS, root),
                                 (fixture.BOUNDARY_PINS, sdk)):
            for relative, expected in collection.items():
                path = base / relative
                self.assertTrue(path.is_file(), f"missing pinned source: {relative}")
                self.assertEqual(fixture.file_digest(path), expected, relative)

    def test_pinned_base_constant(self) -> None:
        expected = "68e3e292b0b2c4b0a96b5f3d3002bb9cb36282d4"
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

    def test_schema_counts_and_completeness(self) -> None:
        self.assertEqual(self.report["schema_id"], fixture.REPORT_SCHEMA_ID)
        self.assertEqual(self.report["status"], "proposal-only/synthetic")
        self.assertTrue(self.report["completeness"]["all_present"])
        self.assertEqual(self.report["completeness"]["missing_results"], [])
        self.assertEqual(
            set(self.report["completeness"]["present_results"]),
            set(fixture.REQUIRED_RESULTS))
        self.assertEqual(self.report["counts"]["required_results"], 15)
        self.assertEqual(self.report["counts"]["source_pins"], 5)
        self.assertEqual(self.report["counts"]["boundary_pins"], 2)
        self.assertEqual(self.report["counts"]["expected_unittest_cases"], 30)
        self.assertEqual(self.report["counts"]["expected_ctest_runs"], 3)
        self.assertEqual(self.fresh["fixture_digest"],
                         self.report["fixture_digest"])

    def test_every_required_result_has_a_status(self) -> None:
        for name in fixture.REQUIRED_RESULTS:
            self.assertIn(name, self.results, name)
            self.assertTrue(self.results[name]["status"] in ("ok",), name)

    def test_qualification_gates_incomplete(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["candidate_qualification"], "not_qualified")
        for name in ("real_speech_listening", "matched_baseline_and_gain",
                     "device_timing"):
            entry = qualification[name]
            self.assertEqual(entry["status"], "incomplete", name)
            self.assertTrue(entry["blocker"], name)
            self.assertTrue(entry["reopen_trigger"], name)
        self.assertEqual(qualification["installed_sdk_change"]["status"],
                         "not_applicable")

    def test_acceptance_profiles_are_explicit(self) -> None:
        profiles = self.report["acceptance_profiles"]
        self.assertEqual(profiles["dsp"]["status"], "synthetic_applied")
        self.assertEqual(profiles["enhancement"]["status"], "synthetic_subset_only")
        self.assertEqual(profiles["voice"]["status"], "synthetic_subset_only")
        self.assertTrue(profiles["no_listening_claim"])
        self.assertTrue(profiles["no_real_speech_claim"])
        for name in ("dsp", "enhancement", "voice"):
            self.assertTrue(profiles[name]["blocker"], name)

    def test_config_validation_accepts_default_and_rejects_adverse(self) -> None:
        self.assertIs(fixture.validate_config(fixture.DEFAULT_CONFIG),
                      fixture.Status.OK)
        for bad in (None, {}, "config", 17):
            self.assertTrue(str(fixture.validate_config(bad)).startswith(
                "Status.REJECTED_"), bad)
        self.assertIs(fixture.validate_config(fixture.config_with(ratio=6)),
                      fixture.Status.OK)

    def test_silence_is_zero_and_unity_gain(self) -> None:
        silence = self.results["silence"]
        self.assertEqual(silence["status"], "ok")
        self.assertEqual(silence["frames"], 40)
        self.assertEqual(silence["peak_abs_output"], 0.0)
        self.assertEqual(silence["final_gain_db"], 0.0)
        self.assertEqual(silence["output_digest"], fixture.tensor_digest(
            (0.0,) * (fixture.FRAME_SAMPLES * 40)))

    def test_impulse_has_no_content_delay(self) -> None:
        impulse = self.results["impulse"]
        self.assertEqual(impulse["status"], "ok")
        self.assertEqual(impulse["peak_sample_index"], 0)
        self.assertEqual(impulse["content_delay_samples"], 0)
        self.assertAlmostEqual(impulse["peak_abs_output"], 0.9, places=9)

    def test_low_band_step_is_preserved(self) -> None:
        step = self.results["low_band_step"]
        self.assertEqual(step["status"], "ok")
        self.assertEqual(step["crossing_samples_from_onset"], 0)
        self.assertAlmostEqual(step["peak_abs_output"], 0.7, places=9)
        self.assertLess(step["low_band_attenuation_db"], 0.5)

    def test_sibilance_burst_attenuation_and_preservation(self) -> None:
        burst = self.results["sibilance_burst"]
        self.assertEqual(burst["status"], "ok")
        self.assertEqual(burst["frames"], 300)
        self.assertEqual(burst["burst_count"], 2)
        self.assertEqual(len(burst["bursts"]), 2)
        for item in burst["bursts"]:
            self.assertGreater(item["high_band_attenuation_db"], 3.0, item)
            self.assertLess(item["low_band_attenuation_db"], 1.0, item)
            self.assertLessEqual(item["min_gain_db"], -5.0, item)
        self.assertGreater(burst["engaged_samples"], 0)
        transitions = burst["transitions"]
        self.assertTrue(any(value.startswith("idle->active@")
                            for value in transitions))
        self.assertTrue(any(value.startswith("active->idle@")
                            for value in transitions))

    def test_frequency_sweep_records_crossover_control(self) -> None:
        sweep = self.results["sibilance_frequency_sweep"]
        points = sweep["points"]
        self.assertEqual([point["frequency_hz"] for point in points],
                         list(fixture.FREQUENCIES_HZ))
        sibilance_points = [point for point in points
                            if point["frequency_hz"] >= 6000]
        attenuations = [point["high_band_attenuation_db"]
                        for point in sibilance_points]
        self.assertEqual(attenuations, sorted(attenuations))
        self.assertGreater(attenuations[0], 3.0)
        crossover = points[0]
        self.assertEqual(crossover["frequency_hz"], 4000)
        self.assertLessEqual(crossover["high_band_attenuation_db"], 0.0)
        self.assertIn("control", sweep["note"])

    def test_level_sweep_is_monotonic(self) -> None:
        sweep = self.results["sibilance_level_sweep"]
        points = sweep["points"]
        self.assertEqual([point["amplitude"] for point in points],
                         list(fixture.LEVELS))
        reductions = [point["settled_gain_db"] for point in points]
        self.assertEqual(reductions, sorted(reductions, reverse=True))
        self.assertEqual(reductions[0], 0.0)
        self.assertEqual(reductions[-1], -12.0)

    def test_clean_preservation_is_sample_identical(self) -> None:
        clean = self.results["clean_preservation"]
        self.assertEqual(clean["status"], "ok")
        self.assertEqual(clean["frames"], 300)
        self.assertTrue(clean["bit_identical_output"])
        self.assertEqual(clean["matched_gain_db"], 0.0)
        self.assertEqual(clean["max_absolute_gain_db"], 0.0)
        self.assertEqual(clean["reduced_frames"], 0)
        self.assertEqual(clean["envelope_correlation"], 1.0)
        self.assertEqual(clean["input_digest"], clean["output_digest"])

    def test_broadband_control_shows_low_band_damage_avoided(self) -> None:
        control = self.results["broadband_control"]
        self.assertLess(
            control["split_band_low_attenuation_db"],
            control["broadband_low_attenuation_db"] - 5.0)
        self.assertGreater(control["broadband_high_attenuation_db"], 3.0)
        self.assertGreater(control["split_band_high_attenuation_db"], 3.0)

    def test_mixed_noise_shows_selective_attenuation(self) -> None:
        mixed = self.results["mixed_noise"]
        self.assertEqual(mixed["status"], "ok")
        self.assertEqual(mixed["frames"], 150)
        self.assertGreater(mixed["high_band_attenuation_db"], 2.0)
        self.assertLess(mixed["low_band_attenuation_db"], 0.5)
        self.assertLess(mixed["peak_abs_output"], 1.0)

    def test_gain_stability_is_bounded_and_finite(self) -> None:
        stable = self.results["gain_stability"]
        self.assertEqual(stable["status"], "ok")
        self.assertEqual(stable["frames"], 100)
        self.assertEqual(stable["max_gain_db"], 0.0)
        self.assertGreater(stable["min_gain_db"], -12.001)
        self.assertLess(stable["max_sample_to_sample_delta_db"], 0.5)
        self.assertLess(stable["max_frame_to_frame_delta_db"], 12.001)
        self.assertEqual(stable["nonfinite_output_samples"], 0)
        self.assertLess(stable["peak_abs_output"], 2.0)

    def test_headroom_overshoot_and_limiter_control(self) -> None:
        headroom = self.results["headroom_peak_overshoot"]
        self.assertEqual(headroom["status"], "ok")
        self.assertEqual(headroom["makeup_db"], 12.0)
        self.assertGreater(headroom["samples_above_full_scale"], 0)
        self.assertLessEqual(headroom["limited_peak"], 0.98)
        self.assertGreater(headroom["boosted_peak"], headroom["limited_peak"])

    def test_state_transitions_reset_final_and_isolation(self) -> None:
        state = self.results["state_transitions"]
        self.assertEqual(state["status"], "ok")
        self.assertEqual(state["reset_with_old_epoch"], "rejected_invalid")
        self.assertEqual(state["reset_with_higher_epoch"], "ok")
        self.assertTrue(state["reset_output_matches_fresh"])
        self.assertTrue(state["cross_session_isolation"])
        self.assertEqual(state["final_input_valid_count"], 5)
        self.assertEqual(state["final_input_source_first_sample"],
                         40 * fixture.FRAME_SAMPLES)
        self.assertEqual(state["process_after_final"], "rejected_state")
        self.assertEqual(state["fresh_status"], "ok")
        self.assertEqual(state["short_status"], "ok")

    def test_adverse_config_count_and_statuses(self) -> None:
        adverse = self.results["adverse_controls"]
        rejections = adverse["config_rejections"]
        self.assertEqual(adverse["config_rejection_count"], 21)
        self.assertEqual(len(rejections), 21)
        self.assertTrue(all(value.startswith("rejected_")
                            for value in rejections.values()))
        expected = {
            "null_config": "rejected_missing",
            "missing_cutoff": "rejected_missing",
            "cutoff_nonfinite": "rejected_nonfinite",
            "threshold_nonfinite": "rejected_nonfinite",
            "attack_nonfinite": "rejected_nonfinite",
            "unknown_key": "rejected_invalid",
            "wrong_type": "rejected_invalid",
            "bool_type": "rejected_invalid",
        }
        for key, status in expected.items():
            self.assertEqual(rejections[key], status, key)

    def test_invalid_frames_rejected_without_state_advance(self) -> None:
        input_rejections = self.results["adverse_controls"]["input_rejections"]
        self.assertEqual(input_rejections["nonfinite_input"], "rejected_nonfinite")
        self.assertEqual(input_rejections["wrong_frame_shape"], "rejected_tensor")
        self.assertEqual(input_rejections["stale_epoch"], "rejected_epoch")
        self.assertEqual(input_rejections["wrong_position"], "rejected_state")
        self.assertEqual(input_rejections["out_of_range"], "rejected_invalid")
        self.assertEqual(input_rejections["nonzero_final_padding"],
                         "rejected_tensor")
        self.assertEqual(input_rejections["unknown_flags"], "rejected_invalid")
        self.assertTrue(input_rejections["state_unchanged_after_nonfinite"])
        self.assertTrue(input_rejections["state_unchanged_after_all_rejects"])

    def test_invalid_missing_nonfinite_are_explicit(self) -> None:
        invalid = self.results["invalid_missing_nonfinite"]
        self.assertEqual(invalid["missing_config_create"], "rejected_missing")
        self.assertEqual(invalid["missing_frame_input"], "rejected_missing")
        self.assertEqual(invalid["nonfinite_config"], "rejected_nonfinite")
        self.assertEqual(invalid["nonfinite_sample"], "rejected_nonfinite")
        self.assertTrue(invalid["state_unchanged_after_missing"])
        self.assertIn("no missing result qualifies", invalid["rule"].lower())

    def test_missing_result_control_fails_candidate(self) -> None:
        control = self.results["invalid_missing_nonfinite"]["missing_result_control"]
        self.assertEqual(control["simulated_removed_result"], "sibilance_burst")
        self.assertEqual(control["missing_detected"], ["sibilance_burst"])
        self.assertFalse(control["all_present_after_removal"])
        self.assertFalse(control["candidate_qualifies"])

    def test_interaction_configurations_all_present(self) -> None:
        interactions = self.results["nonlinear_interactions"]["configurations"]
        self.assertEqual(set(interactions), {
            "deesser_only", "deesser_to_limiter", "limiter_to_deesser",
            "deesser_to_agc", "agc_to_deesser", "deesser_to_deesser"})
        for name, entry in interactions.items():
            self.assertEqual(entry["nonfinite_output_samples"], 0, name)
            self.assertLess(entry["peak_abs_output"], 2.0, name)
            self.assertRegex(entry["output_digest"], r"^[0-9a-f]{64}$", name)

    def test_scope_and_non_claims_are_explicit(self) -> None:
        self.assertIn("proposal-only", self.report["scope"])
        self.assertIn("no real speech", self.report["scope"])
        self.assertGreaterEqual(len(self.report["non_claims"]), 5)
        self.assertTrue(any("No listening" in value
                            for value in self.report["non_claims"]))
        self.assertTrue(any("No installed SDK" in value
                            for value in self.report["non_claims"]))

    def test_provider_is_task_local_and_opt_in(self) -> None:
        cmake = (PROVIDER_DIR / "CMakeLists.txt").read_text()
        self.assertIn("option(AS_ENABLE_DE_ESSER", cmake)
        self.assertIn(" OFF)", cmake)
        self.assertIn("if(AS_ENABLE_DE_ESSER)", cmake)
        self.assertNotIn("add_subdirectory", cmake)
        source = (PROVIDER_DIR / "de_esser_provider.c").read_text()
        descriptor = (PROVIDER_DIR / "config" / "descriptor.h.in").read_text()
        self.assertIn(fixture.PROVIDER_ID, descriptor)
        self.assertIn("DE_PROVIDER_ID", source)
        self.assertIn("audio_sdk/session_v0.h", source)
        self.assertIn("AS_MODE_PROCESSING_THREAD", source)

    def test_shared_surfaces_untouched_by_this_task(self) -> None:
        sdk = sdk_root()
        root_cmake = (sdk / "CMakeLists.txt").read_text()
        self.assertNotIn(fixture.PROVIDER_ID, root_cmake)
        self.assertNotIn("AS_ENABLE_DE_ESSER", root_cmake)
        contracts = (sdk / "CONTRACTS.md").read_text()
        self.assertNotIn(fixture.PROVIDER_ID, contracts)
        descriptor_template = PROVIDER_DIR / "config" / "descriptor.h.in"
        self.assertIn(fixture.PROVIDER_ID, descriptor_template.read_text())

    def test_python_sources_do_not_carry_generated_header_token(self) -> None:
        forbidden = "SPDX" + "-License-Identifier:"
        for path in HERE.glob("*.py"):
            self.assertNotIn(forbidden, path.read_text(), path.name)

    def test_all_report_digests_are_lowercase_hex(self) -> None:
        digests: List[str] = []

        def collect(value: object) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if key.endswith("digest") and isinstance(item, str):
                        digests.append(item)
                    collect(item)
            elif isinstance(value, list):
                for item in value:
                    collect(item)

        collect(self.report)
        self.assertGreater(len(digests), 15)
        for digest in digests:
            self.assertRegex(digest, r"^[0-9a-f]{64}$", digest)


if __name__ == "__main__":
    unittest.main()
