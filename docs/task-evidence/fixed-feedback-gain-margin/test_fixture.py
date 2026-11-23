"""Deterministic checks for the fixed feedback gain margin evidence bundle."""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

import fixture

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
AUDIOML_ROOT = REPO_ROOT.parents[2]

CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
REPORT_TEXT = (HERE / "report.json").read_text(encoding="utf-8")
REPORT = json.loads(REPORT_TEXT)

REPORT_DIGEST = "c7cd3a0518c315a4871b011bd89d74d09207d2d5bf84105c5877a76bf158b2bf"
FIXTURE_DIGEST = "9c124fa104cfe0666166a3a6131d07040455d01ae5f7782e1220c60dd6d1105d"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def results() -> dict:
    return REPORT["results"]


class FixedFeedbackMarginFixtureTest(unittest.TestCase):
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
        self.assertEqual(fixture.DEFAULT_CONFIG["gain_db"], -5.0)
        self.assertEqual(len(fixture.REQUIRED_LOOP_METRICS), 12)

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
        geometry = results()["format_and_delay"]
        self.assertEqual(geometry["silence"]["status"], "ok")
        self.assertEqual(geometry["silence"]["activations"], 0)
        self.assertEqual(geometry["silence"]["peak_abs_output"], 0.0)
        self.assertEqual(geometry["impulse"]["peak_index"], 0)
        self.assertEqual(geometry["impulse"]["added_delay_samples"], 0)
        self.assertAlmostEqual(geometry["impulse"]["peak_abs_output"],
                               0.28117066259517454, places=12)
        self.assertEqual(geometry["step"]["crossing_samples"], 0)
        self.assertEqual(geometry["step"]["settling_frames"], 0)
        self.assertEqual(geometry["buffering_delay_samples"], 0)
        self.assertEqual(CONTRACT["provider"]["buffering_delay_samples"], 0)

    def test_fixed_gain_response_and_frequency_sweep(self):
        gain = results()["gain_response"]
        self.assertEqual(gain["configured_gain_db"], -5.0)
        self.assertAlmostEqual(gain["measured_linear_gain"],
                               gain["configured_linear_gain"], places=9)
        self.assertAlmostEqual(gain["measured_gain_db"], -5.0, places=3)
        sweep = gain["sweep"]
        rows = sweep["per_frequency"]
        self.assertEqual(len(rows), 39)
        self.assertEqual([row["frequency_hz"] for row in rows],
                         list(fixture.FREQUENCIES_HZ))
        self.assertTrue(all(row["status"] == "ok" for row in rows))
        self.assertTrue(all(math.isfinite(row["measured_linear_gain"]) for row in rows))
        for bound in (sweep["min_measured_linear_gain"],
                      sweep["max_measured_linear_gain"]):
            self.assertAlmostEqual(bound, gain["configured_linear_gain"], places=8)
        self.assertEqual(gain["chirp"]["status"], "ok")
        self.assertEqual(gain["chirp"]["frames"], 300)

    def test_static_gain_attack_release_and_state_transitions(self):
        item = results()["step_and_attack_release"]
        self.assertEqual(item["applicability"], "not_applicable_static_bounded_gain")
        self.assertEqual(item["attack_frames"], 0)
        self.assertEqual(item["release_frames"], 0)
        self.assertEqual(item["gain_changes"], 0)
        self.assertEqual(item["gain_db_constant"], -5.0)
        self.assertIn("processing@0", item["state_transitions"])

    def test_clean_speech_like_and_tonal_control(self):
        clean = results()["clean_speech_like"]
        controls = clean["controls"]
        self.assertEqual(sorted(controls), [
            "bounded_minus3_db", "bounded_minus5_db", "bounded_minus8_db", "identity"])
        expected = {"identity": 1.0, "bounded_minus3_db": 10.0 ** (-3.0 / 20.0),
                    "bounded_minus5_db": 10.0 ** (-5.0 / 20.0),
                    "bounded_minus8_db": 10.0 ** (-8.0 / 20.0)}
        for name, row in controls.items():
            self.assertEqual(row["status"], "ok", name)
            self.assertAlmostEqual(row["rms_ratio"], expected[name], places=8, msg=name)
            self.assertAlmostEqual(row["correlation_to_scaled_program"], 1.0,
                                   places=8, msg=name)
        self.assertGreater(controls["bounded_minus5_db"]["program_sdr_db"],
                           controls["bounded_minus8_db"]["program_sdr_db"])
        vowel = clean["tonal_vowel_control"]
        self.assertEqual(vowel["status"], "ok")
        self.assertAlmostEqual(vowel["output_crest_factor"],
                               vowel["input_crest_factor"], places=5)

    def test_headroom_and_interacting_nonlinearity(self):
        headroom = results()["headroom_and_nonlinearity"]
        self.assertEqual(sorted(headroom), ["none", "tanh_0p8"])
        for row in headroom.values():
            self.assertEqual(row["status"], "ok")
            self.assertEqual(row["nonfinite_output_samples"], 0)
            self.assertLess(row["output_peak"], 4.0)
        self.assertAlmostEqual(headroom["none"]["headroom_db_to_input_peak"], 5.0, places=2)
        self.assertGreater(headroom["tanh_0p8"]["headroom_db_to_input_peak"], 10.0)
        self.assertLess(headroom["tanh_0p8"]["output_peak"],
                        headroom["none"]["output_peak"])

    def test_feedback_path_matrix_is_complete_and_finite(self):
        trials = results()["feedback_path_trials"]
        self.assertEqual(len(trials["path_parameters"]), 2)
        self.assertEqual(len(trials["case_parameters"]), 6)
        cases = trials["cases"]
        self.assertEqual(len(cases), 6)
        for case_name, controls in cases.items():
            self.assertEqual(sorted(controls), [
                "bounded_minus3_db", "bounded_minus5_db", "bounded_minus8_db",
                "identity"], case_name)
            for control_name, row in controls.items():
                label = "%s/%s" % (case_name, control_name)
                self.assertEqual(row["missing_results"], [], label)
                expected_status = ("fail_closed" if row["rejected_frames"]
                                   or row["nonfinite_samples"] else "ok")
                self.assertEqual(row["status"], expected_status, label)
                self.assertEqual(row["nonfinite_samples"], 0, label)
                self.assertLessEqual(row["peak_abs_output"], 4.0, label)
                for key in fixture.REQUIRED_LOOP_METRICS:
                    self.assertIn(key, row, label)
                    value = row[key]
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        self.assertTrue(math.isfinite(value), "%s/%s" % (label, key))
                self.assertIn(row["stability_class"], (
                    "decayed_proxy", "decaying_proxy", "sustained_feedback_proxy",
                    "rejected_frames_fail_closed"), label)

    def test_bounded_gain_response_versus_identity_and_other_margins(self):
        cases = results()["feedback_path_trials"]["cases"]
        for case_name, controls in cases.items():
            identity = controls["identity"]
            minus3 = controls["bounded_minus3_db"]
            minus5 = controls["bounded_minus5_db"]
            minus8 = controls["bounded_minus8_db"]
            self.assertIn(identity["stability_class"], (
                "sustained_feedback_proxy", "rejected_frames_fail_closed"), case_name)
            for row in (minus5, minus8):
                self.assertEqual(row["rejected_frames"], 0, case_name)
                self.assertLess(row["tail_decay_db"], -3.0, case_name)
                self.assertLess(row["feedback_growth_db"], 0.0, case_name)
            self.assertLess(minus8["tail_db_relative_to_program"],
                            minus5["tail_db_relative_to_program"], case_name)
            self.assertGreater(minus5["program_sdr_db"], minus3["program_sdr_db"],
                               case_name)

    def test_no_missing_result_may_qualify_a_candidate(self):
        qualification = results()["qualification"]
        self.assertEqual(qualification["rule"],
                         "no missing result may qualify a candidate")
        self.assertIsNone(qualification["selected"])
        for name, row in qualification["candidates"].items():
            self.assertTrue(row["all_results_present"], name)
            self.assertEqual(row["missing_results"], [], name)
            self.assertFalse(row["eligible_for_selection"], name)
            self.assertTrue(row["release_gates_open"], name)
        complete = [{"case": "a", "missing_results": []}]
        incomplete = [{"case": "a", "missing_results": ["tail_decay_db"]}]
        self.assertTrue(fixture.candidate_eligible(complete, [])[
            "eligible_for_selection"])
        self.assertFalse(fixture.candidate_eligible(incomplete, [])[
            "eligible_for_selection"])
        self.assertFalse(fixture.candidate_eligible(complete, ["gate"])[
            "eligible_for_selection"])

    def test_adverse_frames_and_settings_fail_closed_without_state_change(self):
        adverse = results()["adverse_controls"]
        self.assertEqual(adverse["frame_statuses"], {
            "nonfinite_sample": "rejected_nonfinite",
            "wrong_shape": "rejected_tensor",
            "out_of_range_sample": "rejected_invalid",
            "stale_epoch": "rejected_epoch",
            "wrong_position": "rejected_position",
        })
        self.assertEqual(adverse["config_statuses"], {
            "missing": "rejected_missing",
            "wrong_type": "rejected_invalid",
            "nonfinite": "rejected_nonfinite",
            "out_of_range": "rejected_invalid",
            "above_max_gain": "rejected_invalid",
            "unknown_key": "rejected_invalid",
            "stale_profile": "rejected_invalid",
        })
        self.assertTrue(adverse["state_unchanged"])
        self.assertNotEqual(adverse["work_state_digest"], adverse["reset_state_digest"])
        self.assertEqual(adverse["reset_status"], "ok")
        self.assertEqual(adverse["closed_session_status"], "closed")

    def test_invalid_controls_cannot_mutate_a_live_controller(self):
        controller = fixture.FixedMarginController(fixture.config_with())
        controller.process_stream(fixture.tone(10)[:10 * fixture.FRAME_SAMPLES])
        before = controller.state.digest()
        for frame, epoch, position in (
            ((float("nan"),) * 160, None, None),
            ((0.0,) * 159, None, None),
            ((9.0,) * 160, None, None),
            ((0.0,) * 160, 8, None),
            ((0.0,) * 160, None, 999),
        ):
            result = controller.process(frame, epoch=epoch,
                                        first_input_sample=position)
            self.assertNotEqual(result.status, fixture.Status.OK)
            self.assertEqual(controller.state.digest(), before)
        status, instance = fixture.FixedMarginController.create(None)
        self.assertEqual(status, fixture.Status.REJECTED_MISSING)
        self.assertIsNone(instance)

    def test_reset_close_and_instance_independence(self):
        controller = fixture.FixedMarginController(fixture.config_with())
        other = fixture.FixedMarginController(fixture.config_with())
        original = other.state.digest()
        controller.process_stream(fixture.tone(10)[:10 * fixture.FRAME_SAMPLES])
        self.assertNotEqual(controller.state.digest(), original)
        self.assertEqual(other.state.digest(), original)
        self.assertEqual(controller.reset(epoch=8, first_input_sample=400),
                         fixture.Status.OK)
        self.assertEqual(controller.state.epoch, 8)
        self.assertEqual(controller.state.next_input_sample, 400)
        controller.close()
        self.assertEqual(controller.process((0.0,) * 160).status, fixture.Status.CLOSED)
        self.assertEqual(controller.reset(), fixture.Status.CLOSED)


if __name__ == "__main__":
    unittest.main()
