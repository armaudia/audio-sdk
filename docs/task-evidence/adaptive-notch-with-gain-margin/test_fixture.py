"""Deterministic checks for the notch-plus-bounded-margin evidence bundle."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import fixture

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
AUDIOML_ROOT = REPO_ROOT.parents[2]

CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
REPORT_TEXT = (HERE / "report.json").read_text(encoding="utf-8")
REPORT = json.loads(REPORT_TEXT)

REPORT_DIGEST = "b6732740cab7fafd9e270953d7b8f72b6d7951ee5e6d08c1e344a6e9ed228645"
FIXTURE_DIGEST = "9a1bb542f21987d3309d9debdd0cee38d28b4a28d000db4fdeb669d563a94857"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def results() -> dict:
    return REPORT["results"]


class NotchMarginFixtureTest(unittest.TestCase):
    def test_contract_scope_and_v0_geometry(self):
        self.assertEqual(CONTRACT["task"], fixture.TASK_ID)
        self.assertEqual(CONTRACT["schema_id"], fixture.CONTRACT_ID)
        self.assertEqual(CONTRACT["status"], "optional-task-local-reference")
        self.assertEqual(CONTRACT["format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "f32", "frame_samples": 160})
        self.assertEqual(fixture.SAMPLE_RATE_HZ, 16000)
        self.assertEqual(fixture.CHANNELS, 1)
        self.assertEqual(fixture.FRAME_SAMPLES, 160)
        self.assertEqual(len(fixture.FREQUENCIES_HZ), 39)
        self.assertEqual((fixture.FREQUENCIES_HZ[0], fixture.FREQUENCIES_HZ[-1]),
                         (200, 4000))
        self.assertEqual(CONTRACT["reference_controls"], fixture.DEFAULT_CONFIG)

    def test_pinned_external_sources_match_exact_digests(self):
        self.assertEqual(fixture.SOURCE_PINS, CONTRACT["source_pins"])
        self.assertEqual(fixture.BOUNDARY_PINS, CONTRACT["boundary_pins"])
        for relative, digest in fixture.SOURCE_PINS.items():
            path = AUDIOML_ROOT / relative
            self.assertTrue(path.is_file(), str(path))
            self.assertEqual(sha256_file(path), digest, relative)
        for relative, digest in fixture.BOUNDARY_PINS.items():
            path = REPO_ROOT / relative
            self.assertTrue(path.is_file(), str(path))
            self.assertEqual(sha256_file(path), digest, relative)

    def test_board_is_a_read_only_snapshot(self):
        self.assertEqual(fixture.BOARD_SNAPSHOT, CONTRACT["board_snapshot"])
        self.assertTrue(CONTRACT["board_snapshot"]["mutable"])
        self.assertNotIn(CONTRACT["board_snapshot"]["path"], CONTRACT["source_pins"])
        board = AUDIOML_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
        self.assertTrue(board.is_file())

    def test_local_artifact_pins(self):
        for relative, digest in CONTRACT["artifact_pins"].items():
            path = HERE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(sha256_file(path), digest, relative)

    def test_report_is_canonical_and_byte_reproducible(self):
        text, digest = fixture.canonical_report(fixture.build_report())
        self.assertEqual(text, REPORT_TEXT)
        self.assertEqual(digest, REPORT_DIGEST)
        self.assertEqual(REPORT["fixture_digest"], FIXTURE_DIGEST)
        self.assertEqual(REPORT["boundary_pins"], fixture.BOUNDARY_PINS)
        self.assertTrue((HERE / "report.json.sha256").read_text(encoding="utf-8").startswith(
            REPORT_DIGEST + "  report.json"))

    def test_silence_impulse_step_and_zero_added_delay(self):
        silence = results()["silence"]
        self.assertEqual(silence["status"], "ok")
        self.assertEqual(silence["activations"], 0)
        self.assertEqual(silence["peak_abs_output"], 0.0)
        self.assertEqual(silence["output_digest"],
                         "c65206769723a13afe80c0d925531639ceef9c2eb97eee3b1b542739ec40597f")
        impulse_result = results()["impulse"]
        self.assertEqual(impulse_result["peak_index"], 0)
        self.assertEqual(impulse_result["added_delay_samples"], 0)
        self.assertEqual(impulse_result["peak_abs_output"], 0.5)
        step = results()["step"]
        self.assertEqual(step["crossing_samples"], 0)
        self.assertEqual(step["peak_abs_output"], 0.25)
        self.assertEqual(CONTRACT["provider"]["buffering_delay_samples"], 0)

    def test_fixed_gain_response_and_headroom(self):
        gain = results()["gain_response"]
        self.assertEqual(gain["configured_gain_db"], -5.0)
        self.assertAlmostEqual(gain["measured_linear_gain"],
                               gain["configured_linear_gain"], places=9)
        headroom = results()["headroom_and_nonlinearity"]
        self.assertEqual(headroom["status"], "ok")
        self.assertEqual(headroom["nonfinite_output_samples"], 0)
        self.assertLess(headroom["output_peak"], 0.8)
        self.assertGreater(headroom["headroom_db_to_input_peak"], 10.0)

    def test_sweep_and_chirp_cover_all_frequencies(self):
        sweep = results()["sweep"]
        self.assertEqual(sweep["frames_per_frequency"], 12)
        self.assertEqual(sweep["activated_frequencies"], 39)
        self.assertEqual(len(sweep["per_frequency"]), 39)
        self.assertTrue(all(row["activated"] for row in sweep["per_frequency"]))
        self.assertEqual([row["frequency_hz"] for row in sweep["per_frequency"]],
                         list(fixture.FREQUENCIES_HZ))
        self.assertLess(sweep["min_gain"], 0.01)
        self.assertLess(sweep["max_gain"], 0.2)
        chirp = results()["chirp_sweep"]
        self.assertEqual(chirp["status"], "ok")
        self.assertEqual(chirp["frames"], 300)
        self.assertGreater(chirp["activations"], 0)
        self.assertTrue(chirp["transitions"])

    def test_attack_release_gain_bounds_and_state_transitions(self):
        burst = results()["attack_release"]
        self.assertEqual(burst["status"], "ok")
        self.assertEqual(burst["attack_frames"], 3)
        self.assertEqual(burst["release_frames"], 23)
        self.assertEqual(burst["activations"], 1)
        self.assertEqual(burst["releases"], 1)
        self.assertEqual(burst["margin_min_db"], -3.0)
        self.assertEqual(burst["transitions"],
                         ["idle->active@23:1000", "active->idle@143:1000"])

    def test_clean_speech_like_input_and_false_triggers(self):
        clean = results()["clean_speech"]
        self.assertEqual(clean["notch_only"]["false_activations"], 0)
        self.assertEqual(clean["notch_only"]["false_activation_rate_per_minute"], 0.0)
        self.assertEqual(clean["notch_plus_margin"]["margin_reduction_events"], 0)
        self.assertEqual(clean["notch_plus_margin"]["output_digest"],
                         clean["notch_only"]["output_digest"])
        self.assertEqual(clean["fixed_gain"]["gain_db"], -5.0)
        self.assertNotEqual(clean["fixed_gain"]["output_digest"],
                            clean["notch_only"]["output_digest"])
        tonal = results()["tonal_vowel_stress"]
        self.assertGreater(tonal["false_activations"], 0)
        self.assertGreater(tonal["margin_reduction_events"], 0)
        self.assertGreaterEqual(tonal["margin_min_db"], -12.0)

    def test_tone_artifact_control(self):
        tone = results()["tone_injection"]
        self.assertEqual(tone["status"], "ok")
        self.assertEqual(tone["activations_in_tone_region"], 1)
        self.assertEqual(tone["false_activations_in_clean_region"], 0)
        self.assertGreater(tone["tone_to_total_db_before"], tone["tone_to_total_db_after"])
        self.assertGreater(tone["tone_power_db_before"], tone["tone_power_db_after"])
        self.assertEqual(tone["clean_region_tone_db_before"],
                         tone["clean_region_tone_db_after"])

    def test_closed_loop_matrix_is_complete_and_finite(self):
        loops = results()["closed_loop"]
        self.assertEqual(sorted(loops), [
            "g1_05_linear", "g1_15_dual_paths", "g1_15_linear",
            "g1_15_post_clip", "g1_15_pre_tanh", "g1_3_linear"])
        for case, controls in loops.items():
            self.assertEqual(sorted(controls), [
                "fixed_gain", "identity", "notch_only", "notch_plus_margin"], case)
            for name, item in controls.items():
                self.assertEqual(item["status"], "ok", f"{case}/{name}")
                self.assertEqual(item["nonfinite_frames"], 0, f"{case}/{name}")
                self.assertLessEqual(item["peak_abs_output"], 16.0, f"{case}/{name}")
                self.assertTrue(math_isfinite(item["tail_db_relative_to_program"]))
                self.assertTrue(math_isfinite(item["program_sdr_db"]))
                self.assertTrue(item["stability_class"])

    def test_notch_plus_margin_versus_fixed_gain_control(self):
        loops = results()["closed_loop"]
        for case in ("g1_05_linear", "g1_15_linear", "g1_3_linear",
                     "g1_15_pre_tanh", "g1_15_post_clip", "g1_15_dual_paths"):
            controls = loops[case]
            identity = controls["identity"]
            fixed = controls["fixed_gain"]
            adaptive = controls["notch_plus_margin"]
            self.assertIn(identity["stability_class"],
                          ("rejected_frames_fail_closed", "sustained_feedback"), case)
            self.assertEqual(fixed["rejected_frames"], 0, case)
            self.assertEqual(fixed["stability_class"], "decayed", case)
            self.assertLess(fixed["tail_db_relative_to_program"], -30.0, case)
            self.assertEqual(adaptive["rejected_frames"], 0, case)
            self.assertEqual(adaptive["stability_class"], "decayed", case)
            self.assertLess(adaptive["tail_db_relative_to_program"], -30.0, case)
            self.assertGreater(adaptive["activations"], 0, case)
            self.assertGreater(adaptive["margin_reduction_events"], 0, case)
            self.assertGreaterEqual(adaptive["margin_min_db"], -12.0, case)
            # The fixed -5 dB control remains the level-preservation leader on
            # this synthetic loop; the adaptive path spends margin to suppress.
            self.assertGreater(fixed["program_sdr_db"], adaptive["program_sdr_db"], case)

    def test_adverse_frames_and_settings_fail_closed_without_state_change(self):
        adverse = results()["adverse_controls"]
        expected_frames = {
            "nonfinite_sample": "rejected_nonfinite",
            "wrong_shape": "rejected_tensor",
            "out_of_range_sample": "rejected_invalid",
            "stale_epoch": "rejected_epoch",
            "wrong_position": "rejected_position",
        }
        self.assertEqual(adverse["frame_statuses"], expected_frames)
        self.assertEqual(adverse["config_statuses"], {
            "missing": "rejected_missing",
            "wrong_type": "rejected_invalid",
            "nonfinite": "rejected_nonfinite",
            "out_of_range": "rejected_invalid",
            "unknown_key": "rejected_invalid",
            "stale_profile": "rejected_invalid",
        })
        self.assertTrue(adverse["state_unchanged"])
        self.assertNotEqual(adverse["work_state_digest"], adverse["reset_state_digest"])
        self.assertEqual(adverse["closed_session_status"], "closed")

    def test_invalid_controls_do_not_mutate_a_live_controller(self):
        controller = fixture.MarginController(fixture.config_with())
        controller.process_stream(fixture.tone(10)[:10 * fixture.FRAME_SAMPLES])
        before = controller.state.digest()
        for frame, epoch, position in (
            ((float("nan"),) * 160, None, None),
            ((0.0,) * 159, None, None),
            ((9.0,) * 160, None, None),
            ((0.0,) * 160, 8, None),
            ((0.0,) * 160, None, 999),
        ):
            result = controller.process(frame, epoch=epoch, first_input_sample=position)
            self.assertNotEqual(result.status, fixture.Status.OK)
            self.assertEqual(controller.state.digest(), before)
        status, instance = fixture.MarginController.create(None)
        self.assertEqual(status, fixture.Status.REJECTED_MISSING)
        self.assertIsNone(instance)

    def test_reset_close_and_instance_independence(self):
        controller = fixture.MarginController(fixture.config_with())
        other = fixture.MarginController(fixture.config_with())
        original = other.state.digest()
        controller.process_stream(fixture.tone(10)[:10 * fixture.FRAME_SAMPLES])
        self.assertNotEqual(controller.state.digest(), original)
        self.assertEqual(other.state.digest(), original)
        self.assertEqual(controller.reset(epoch=8, first_input_sample=400), fixture.Status.OK)
        self.assertEqual(controller.state.epoch, 8)
        self.assertEqual(controller.state.next_input_sample, 400)
        controller.close()
        self.assertEqual(controller.process((0.0,) * 160).status, fixture.Status.CLOSED)
        self.assertEqual(controller.reset(), fixture.Status.CLOSED)


def math_isfinite(value) -> bool:
    import math
    return isinstance(value, (int, float)) and math.isfinite(value)


if __name__ == "__main__":
    unittest.main()
