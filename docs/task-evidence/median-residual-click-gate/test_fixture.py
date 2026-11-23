"""Offline unittest acceptance checks for the task-local click-gate fixture."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import fixtures  # noqa: E402
import reference  # noqa: E402
import report as report_module  # noqa: E402
import run  # noqa: E402

CONFIG = {
    "control": reference.CONTROL,
    "sample_rate_hz": reference.SAMPLE_RATE_HZ,
    "channels": reference.CHANNELS,
    "sample_format": reference.SAMPLE_FORMAT,
    "sdk_frame_samples": reference.SDK_FRAME_SAMPLES,
    "median_width_samples": reference.DEFAULT_MEDIAN_WIDTH,
    "threshold": reference.DEFAULT_THRESHOLD,
}


def manual_request(stimulus: dict, attempt_id: str = "manual-001") -> dict:
    request = base_request(scenario="manual", attempt_id=attempt_id)
    request.pop("case_id")
    request["stimulus"] = stimulus
    return request


def base_request(**updates: object) -> dict:
    request = {
        "protocol_version": 1, "operation": "run",
        "candidate_ref": {"kind": "reference", "id": "dsp.median-residual-click-gate.ref", "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": "median-residual-click-gate", "revision": 1},
        "configuration": copy.deepcopy(CONFIG),
        "attempt_id": "test-attempt", "session_id": "test-session",
        "epoch": 31, "scenario": "case", "case_id": "speech_1x",
    }
    request.update(updates)
    return request


class MedianResidualClickGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads((ROOT / "report.json").read_text(encoding="utf-8"))
        cls.by_id = {case["case_id"]: case for case in cls.report["cases"]}

    # -- provenance and boundary -------------------------------------------------
    def test_source_pins_verified(self) -> None:
        verification = fixtures.verify_source_pins()
        self.assertEqual(len(verification), len(fixtures.SOURCE_PINS))
        self.assertTrue(all(item["verified"] for item in verification.values()),
                        json.dumps(verification, sort_keys=True))

    def test_report_source_pins_are_constants(self) -> None:
        self.assertEqual(self.report["source_pins"], fixtures.SOURCE_PINS)

    def test_adapter_descriptor_identity_and_digest(self) -> None:
        descriptor = run.adapter_descriptor()
        self.assertEqual(descriptor["identity"], reference.IDENTITY)
        self.assertEqual(descriptor["protocol_version"], 1)
        self.assertEqual(descriptor["weights"], "none")
        digest = hashlib.sha256((ROOT / "adapter.json").read_bytes()).hexdigest()
        self.assertEqual(self.report["boundary"]["adapter_descriptor_sha256"], digest)

    def test_report_file_digests_match(self) -> None:
        names = {
            "adapter_json": "adapter.json", "reference_py": "reference.py",
            "fixtures_py": "fixtures.py", "run_py": "run.py", "report_py": "report.py",
        }
        for name, digest in self.report["digests"].items():
            path = ROOT / names[name]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest, name)

    def test_case_input_digests_match(self) -> None:
        for case_id, digest in self.report["fixtures"]["case_input_digests"].items():
            self.assertEqual(fixtures.case_inputs_digest(case_id), digest, case_id)

    # -- deterministic reference ------------------------------------------------
    def test_config_validation_fail_closed(self) -> None:
        bad = [
            {}, {**CONFIG, "unexpected": 1},
            {**CONFIG, "median_width_samples": 8},
            {**CONFIG, "median_width_samples": 17},
            {**CONFIG, "threshold": 0.0}, {**CONFIG, "threshold": 1.5},
            {**CONFIG, "threshold": "nan"}, {**CONFIG, "sample_rate_hz": 44100},
            {**CONFIG, "channels": 2}, {**CONFIG, "sample_format": "s16"},
        ]
        for config in bad:
            with self.subTest(config=config):
                with self.assertRaises(reference.ControlError):
                    reference.validate_config(config)

    def test_reflected_median_matches_independent_brute_force(self) -> None:
        samples = [reference.f32(value / 11.0) for value in range(20)]
        length = len(samples)

        def brute(index: int) -> float:
            taps = []
            for delta in range(-3, 4):
                j = index + delta
                if j < 0:
                    j = -j
                elif j >= length:
                    j = 2 * (length - 1) - j
                taps.append(samples[j])
            return sorted(taps)[3]

        for index in (0, 1, 2, 3, 7, length - 4, length - 3, length - 2, length - 1):
            decision = reference.median_residual(samples, index, 7, 0.35)
            self.assertEqual(decision["baseline_f32"], reference.f32(brute(index)), index)

    def test_silence_is_identity_and_detector_free(self) -> None:
        result = self.by_id["silence_1x"]
        self.assertEqual(result["detections"]["detected_click_samples"], 0)
        self.assertEqual(result["preservation"]["non_click_samples_changed"], 0)
        self.assertEqual(result["output"]["sha256"], result["source"]["sha256"])

    # -- rate profile -----------------------------------------------------------
    def test_every_case_has_a_result_and_no_missing_qualifies(self) -> None:
        self.assertEqual([case["case_id"] for case in self.report["cases"]],
                         list(fixtures.CASE_IDS))
        self.assertEqual(len(self.report["cases"]), self.report["fixtures"]["case_count"])
        qualification = self.report["missing_results_and_qualification"]
        self.assertTrue(qualification["all_fixture_cases_have_results"])
        self.assertFalse(qualification["candidate_qualified"])
        self.assertFalse(qualification["missing_result_qualifies"])
        for case in self.report["cases"]:
            self.assertFalse(case["qualification"]["candidate_qualified"])

    def test_source_output_mapping_conservation(self) -> None:
        for row in self.report["rate_profile"]["source_output_mapping"]:
            with self.subTest(case_id=row["case_id"]):
                self.assertTrue(row["union_equals_source"])
                self.assertEqual(row["gap_count"], 0)
                self.assertEqual(row["overlap_count"], 0)
                self.assertEqual(row["delivered_valid_samples"], row["source_interval"][1])
                case = self.by_id[row["case_id"]]
                mapping = case["source_output_mapping"]
                produced = len(mapping["frame_map"]) * reference.SDK_FRAME_SAMPLES
                self.assertEqual(produced, mapping["delivered_valid_samples"]
                                 + mapping["startup_padding_samples"]
                                 + mapping["final_padding_samples"])

    def test_1x_duration_and_source_timestamp_map(self) -> None:
        one_x = self.by_id["speech_1x"]
        self.assertEqual(one_x["source"]["sample_count"], 6400)
        self.assertEqual(one_x["playback"]["playback_start_ns"], 0)
        self.assertEqual(one_x["playback"]["playback_end_ns"], 400_000_000)
        self.assertEqual(one_x["playback"]["playback_duration_seconds"], 0.4)
        self.assertEqual(one_x["playback"]["ns_per_source_sample_at_1x"], 62500)
        self.assertEqual(self.by_id["final_partial_speech"]["source"]["sample_count"], 165)
        self.assertEqual(self.by_id["final_partial_speech"]["playback"]["playback_end_ns"],
                         165 * 62500)

    def test_rate_change_rebuffer_and_drift_boundaries(self) -> None:
        changed = self.by_id["speech_rate_125_080"]
        boundaries = changed["playback"]["rate_change_boundaries"]
        self.assertEqual([item["source_sample"] for item in boundaries], [1600, 4800])
        self.assertEqual([item["source_ns"] for item in boundaries],
                         [100_000_000, 300_000_000])
        self.assertEqual([item["playback_ns"] for item in boundaries],
                         [100_000_000, 260_000_000])
        self.assertEqual(changed["playback"]["playback_duration_seconds"], 0.385)
        rebuffer = self.by_id["rebuffer_speech"]["playback"]
        self.assertEqual(rebuffer["total_rebuffer_ns"], 80_000_000)
        self.assertEqual(rebuffer["rate_change_boundaries"][0]["source_ns"], 200_000_000)
        self.assertEqual(rebuffer["rate_change_boundaries"][0]["rebuffer_ns_before"],
                         80_000_000)
        self.assertEqual(rebuffer["playback_duration_ns"], 480_000_000)
        drift = self.by_id["silence_drift"]["playback"]
        self.assertEqual(drift["rate_segments"][0]["rate_num"], 1000250)
        self.assertLess(drift["playback_duration_seconds"], 0.4)
        self.assertEqual(self.by_id["music_rate_08"]["playback"]["playback_duration_seconds"],
                         0.5)

    def test_pitch_proxy_has_no_source_domain_shift(self) -> None:
        for row in self.report["rate_profile"]["pitch_controls"]:
            if row["applicable"]:
                with self.subTest(case_id=row["case_id"]):
                    self.assertEqual(row["delta_samples"], 0)
                    self.assertEqual(row["clean_period_samples"], row["output_period_samples"])

    def test_transient_audibility_controls(self) -> None:
        self.assertEqual(self.report["speech_preservation_proxy"]
                         ["music_transient_preservation_fraction"], 1.0)
        speech = self.by_id["speech_1x"]["preservation"]
        self.assertEqual(speech["transient_samples_preserved"], speech["transient_samples_total"])
        for case_id in ("click_w1_a750", "click_w2_a750", "click_w3_a750", "click_w5_a750"):
            detections = self.by_id[case_id]["detections"]
            self.assertEqual(detections["fp_samples"], 0)

    def test_click_width_and_amplitude_failure_envelope(self) -> None:
        table = self.report["click_and_suppression_counts"]
        for width in ("1", "2", "3"):
            for amplitude in ("0.40", "0.75"):
                row = table[width][amplitude]
                self.assertEqual(row["recall"], 1.0, (width, amplitude))
                self.assertEqual(row["fp_samples"], 0)
        for width in ("1", "2", "3", "5"):
            self.assertEqual(table[width]["0.20"]["recall"], 0.0, width)
        self.assertEqual(table["5"]["0.75"]["recall"], 0.0)

    def test_speech_preservation_proxies(self) -> None:
        self.assertTrue(self.report["speech_preservation_proxy"]
                        ["all_non_click_samples_unchanged_on_clean_cases"])
        for row in self.report["speech_preservation_proxy"]["clean_control_cases"]:
            self.assertEqual(row["non_click_samples_changed"], 0)
            self.assertGreaterEqual(row["envelope_correlation"], 0.0)

    def test_final_partial_window_flags_and_zero_padding(self) -> None:
        detail = self.report["rate_profile"]["playback_buffering_semantics"]["final_partial_case"]
        partial = detail["partial_frame"]
        self.assertEqual(detail["source_samples"], 165)
        self.assertEqual(partial["flags"] & reference.FLAG_FINAL_PADDING,
                         reference.FLAG_FINAL_PADDING)
        self.assertEqual(partial["source_valid_end"], 165)
        self.assertEqual(partial["valid_count"], 8)
        case = fixtures.build_case("final_partial_speech")
        session, _ = self._drive_fixture(case)
        last = session.frames[-1]
        self.assertEqual(last["valid_count"], 8)
        self.assertEqual(last["samples"][last["valid_offset"] + last["valid_count"]:],
                         [0.0] * (reference.SDK_FRAME_SAMPLES
                                  - last["valid_offset"] - last["valid_count"]))

    def test_decisions_tied_to_source_timestamps(self) -> None:
        self.assertTrue(self.report["rate_profile"]["decision_timestamps"]
                        ["all_cases_tied_to_source_index"])
        case = fixtures.build_case("click_w1_a750")
        session, scored = self._drive_fixture(case)
        for decision in session.decisions.values():
            self.assertEqual(decision["source_start_ns"],
                             decision["source_index"] * reference.NS_PER_SAMPLE)
        detected = [d for d in session.decisions.values() if d["detected"]]
        self.assertEqual(scored["detections"]["first_detection_source_ns"],
                         min(d["source_start_ns"] for d in detected))
        self.assertEqual(scored["detections"]["last_detection_source_ns"],
                         max(d["source_end_ns"] for d in detected))

    def test_no_pause_filler_or_resampling_claim(self) -> None:
        self.assertTrue(self.report["method"]["no_sample_rate_conversion"])
        self.assertTrue(self.report["method"]["no_pause_or_filler_insertion"])
        self.assertEqual(self.report["rate_profile"]["decision_timestamps"]
                         ["pause_or_filler_decisions"],
                         "none; suppression is per source sample only")

    # -- adverse and state controls --------------------------------------------
    def test_adverse_controls_observed_with_state_preserved(self) -> None:
        adverse = self.report["adverse_controls"]
        self.assertGreaterEqual(adverse["control_count"], 20)
        self.assertTrue(adverse["all_observed"])
        self.assertTrue(adverse["all_rejected_or_expected"])
        self.assertEqual(adverse["missing_results"], [])
        for row in adverse["controls"]:
            with self.subTest(control=row["id"]):
                self.assertEqual(row["status"], "observed")
                self.assertEqual(row["outcome"], "rejected")
                self.assertTrue(row["state_unchanged"], row["reason"])

    def test_independent_state_and_stale_controls(self) -> None:
        state = self.report["state_controls"]
        self.assertTrue(state["digests_distinct"])
        self.assertTrue(state["right_unchanged_by_left_reset"])
        self.assertEqual(state["stale_epoch_decision"]["reason"], "stale_epoch_decision")
        self.assertEqual(state["stale_session_decision"]["reason"], "stale_session_decision")
        self.assertEqual(state["stale_epoch_frame"]["reason"], "stale_epoch")
        self.assertGreater(state["reset"]["after"]["epoch"], state["reset"]["before"]["epoch"])

    def test_nonfinite_wrong_shape_and_stale_frame_rejected(self) -> None:
        session = reference.Session(CONFIG, session_id="s", epoch=7)
        frame = [0.0] * reference.SDK_FRAME_SAMPLES
        frame[5] = float("nan")
        self.assertEqual(session.process_frame(frame, epoch=7, session_id="s",
                                               first_input_sample=0)["reason"],
                         "nonfinite_input")
        self.assertEqual(session.process_frame([0.0] * 159, epoch=7, session_id="s",
                                               first_input_sample=0)["reason"],
                         "frame_samples_mismatch")
        self.assertEqual(session.process_frame([0.0] * 160, epoch=6, session_id="s",
                                               first_input_sample=0)["reason"],
                         "stale_epoch")
        self.assertEqual(session.process_frame([0.0] * 160, epoch=7, session_id="other",
                                               first_input_sample=0)["reason"],
                         "stale_session")
        self.assertEqual(session.summary()["accepted_samples"], 0)

    def test_manual_stimulus_validation_rejects_nonfinite(self) -> None:
        stimulus = report_module.caller_owned_stimulus()
        stimulus["samples"][3] = float("nan")
        with self.assertRaises(run.RequestError):
            run.dispatch(manual_request(stimulus))

    def test_caller_owned_inputs_are_copied(self) -> None:
        original = report_module.caller_owned_stimulus()
        snapshot = copy.deepcopy(original)
        result = run.dispatch(manual_request(original, "copy-001"))
        digest = result["output"]["sha256"]
        original["samples"][0] = 1.0
        original["clean"][0] = 1.0
        original["labels"][0] = not original["labels"][0]
        original["rate_plan"]["segments"][0]["origin_ns"] = 999
        self.assertEqual(result["output"]["sha256"], digest)
        fresh = run.dispatch(manual_request(snapshot, "copy-002"))
        self.assertEqual(fresh["output"]["sha256"], digest)

    def test_json_reader_rejects_duplicate_keys_and_nonfinite_constant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            duplicate = Path(directory) / "duplicate.json"
            constant = Path(directory) / "constant.json"
            duplicate.write_text('{"protocol_version":1,"protocol_version":2}', encoding="utf-8")
            constant.write_text('{"protocol_version":NaN}', encoding="utf-8")
            with self.assertRaises(run.RequestError):
                run.read_json(duplicate)
            with self.assertRaises(run.RequestError):
                run.read_json(constant)

    # -- canonical report -------------------------------------------------------
    def test_report_is_canonical_json(self) -> None:
        payload = (ROOT / "report.json").read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))
        self.assertNotIn(b"\r", payload)
        self.assertEqual(payload, run.canonical_bytes(json.loads(payload.decode("utf-8"))))

    def test_report_sidecar_matches(self) -> None:
        payload = (ROOT / "report.json").read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual((ROOT / "report.json.sha256").read_text(encoding="ascii"),
                         digest + "  report.json\n")

    def test_report_regeneration_is_byte_identical(self) -> None:
        expected = (ROOT / "report.json").read_bytes()
        expected_sidecar = (ROOT / "report.json.sha256").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "a", Path(directory) / "b"
            report_module.main(["--output-dir", str(first)])
            report_module.main(["--output-dir", str(second)])
            self.assertEqual((first / "report.json").read_bytes(), expected)
            self.assertEqual((second / "report.json").read_bytes(), expected)
            self.assertEqual((first / "report.json.sha256").read_bytes(), expected_sidecar)
            self.assertEqual((second / "report.json.sha256").read_bytes(), expected_sidecar)

    def test_case_result_reproduces_from_fixture(self) -> None:
        for case_id in ("click_w5_a750", "speech_rate_125_080", "rate_change_partial"):
            with self.subTest(case_id=case_id):
                result = run.dispatch(report_module.standard_request(
                    operation="run", scenario="case", case_id=case_id))
                self.assertEqual(result, self.by_id[case_id])

    def test_no_result_promoted_to_qualification(self) -> None:
        for case in self.report["cases"]:
            self.assertFalse(case["qualification"]["candidate_qualified"])
        self.assertEqual(self.report["status"], "synthetic_opt_in_not_qualified")
        self.assertGreaterEqual(len(self.report["missing_results_and_qualification"]["blockers"]), 5)

    # -- helpers ----------------------------------------------------------------
    def _drive_fixture(self, case: dict) -> tuple[reference.Session, dict]:
        return run._drive(CONFIG, case, session_id="test-drive", epoch=91)


if __name__ == "__main__":
    unittest.main()
