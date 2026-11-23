"""Deterministic unittest suite for the fixed-RMS VAD analysis fixture."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import fixtures  # noqa: E402
import reference  # noqa: E402
import report  # noqa: E402
import run  # noqa: E402

REPORT_PATH = HERE / "report.json"
AUDIOML_ROOT = Path(os.environ.get("AUDIOML_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))


class FixedRmsVadFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report_bytes = REPORT_PATH.read_bytes()
        cls.document = json.loads(cls.report_bytes)
        cls.scenarios = {name: run.run(request) for name, request in report.REQUESTS.items()}
        cls.primary = cls.scenarios["primary"]
        cls.scoring = cls.primary["scoring"]

    def test_report_is_canonical_and_repeatable(self) -> None:
        regenerated = (json.dumps(report.build_report(), sort_keys=True,
                                  separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")
        self.assertEqual(self.report_bytes, regenerated)
        self.assertTrue(self.report_bytes.endswith(b"\n"))
        self.assertEqual(self.document["protocol"], "sdk.fixed-rms-vad.analysis.v1")
        self.assertEqual(self.document["status"], "proposal_only_synthetic")
        self.assertEqual(self.document["base_commit"], report.BASE_COMMIT)

    def test_source_pins_are_present_and_exact(self) -> None:
        pins = self.document["source_pins"]
        self.assertEqual(len(pins), 5)
        self.assertEqual(set(pins), set(fixtures.SOURCE_PINS))
        for relative, digest in pins.items():
            path = AUDIOML_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(report.sha256_path(path), digest, relative)

    def test_geometry_and_fixed_configuration(self) -> None:
        geometry = self.document["geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["sdk_frame_samples"], 160)
        self.assertEqual(geometry["adapter_analysis_window_samples"], 320)
        self.assertEqual(geometry["sdk_frames_per_analysis_window"], 2)
        self.assertEqual(geometry["source_time_mapping"], "identity")
        self.assertEqual(geometry["analysis_content_delay_samples"], 0)
        config = {key: value for key, value in self.document["config"].items()
                  if key != "control"}
        self.assertEqual(config, reference.DEFAULT_CONFIG)

    def test_stream_and_local_digests(self) -> None:
        samples = fixtures.build_samples()
        self.assertEqual(len(samples), fixtures.STREAM_SAMPLES)
        self.assertEqual(reference.digest_samples(samples),
                         self.document["digests"]["stream_f32"])
        self.assertEqual(self.document["digests"]["fixture_spec"],
                         reference.canonical_digest(fixtures.seed_spec()))
        self.assertEqual(self.document["digests"]["adapter_descriptor"],
                         report.sha256_path(report.ADAPTER_PATH))
        self.assertEqual(self.document["digests"]["primary_events"],
                         self.primary["session"]["events_sha256"])

    def test_expected_counts(self) -> None:
        counts = self.document["counts"]
        self.assertEqual(counts["stream_samples"], 16000)
        self.assertEqual(counts["sdk_frames"], 100)
        self.assertEqual(counts["analysis_windows"], 50)
        self.assertEqual(counts["timestamped_probability_events"], 50)
        self.assertEqual(counts["speech_events"], 2)
        self.assertEqual(counts["total_events"], 52)
        self.assertEqual(counts["known_positive_segments"], 3)
        self.assertEqual(counts["known_negative_segments"], 4)
        self.assertEqual(counts["known_positive_samples"], 2720)
        self.assertEqual(counts["known_negative_samples"], 13280)
        self.assertEqual(counts["scored_samples"], 16000)
        self.assertEqual(counts["unknown_samples"], 0)
        self.assertEqual(counts["invalid_samples"], 0)
        self.assertEqual(counts["delivered_events"], 52)
        self.assertEqual(counts["dropped_events"], 2)
        self.assertEqual(counts["adverse_rejections"], 11)
        self.assertEqual(counts["source_pins"], 5)

    def test_timestamped_probabilities_are_valid_and_exact(self) -> None:
        self.assertEqual(self.scoring["status"], "ok")
        self.assertTrue(self.scoring["probability_coverage_ok"])
        self.assertTrue(self.scoring["availability_ok"])
        self.assertTrue(self.scoring["finite_probabilities"])
        self.assertTrue(self.scoring["threshold_decision_consistent"])
        probabilities = self.primary["probability_events"]
        self.assertEqual(len(probabilities), 50)
        for event in probabilities:
            with self.subTest(sequence=event["sequence"]):
                self.assertEqual(event["kind"], "speech_probability")
                self.assertEqual(event["validity"], "known")
                self.assertEqual(event["epoch"], 1)
                self.assertEqual(event["availability_clock_id"], reference.CLOCK_ID)
                self.assertEqual(event["available_ns"],
                                 reference.AVAILABILITY_ORIGIN_NS
                                 + event["source_end"] * reference.NS_PER_SAMPLE)
                self.assertGreaterEqual(event["value"], 0.0)
                self.assertLessEqual(event["value"], 1.0)
        self.assertEqual(
            reference.merge_intervals(
                (event["source_start"], event["source_end"]) for event in probabilities),
            [[0, 16000]],
        )

    def test_event_boundaries_and_detections_are_exact(self) -> None:
        intervals = reference.merge_intervals(self.scoring["hypothesis_intervals"])
        self.assertEqual(intervals, [[640, 960], [1920, 3520]])
        speech_events = self.primary["speech_event_intervals"]
        self.assertEqual(
            [(item["source_start"], item["source_end"]) for item in speech_events],
            [(interval[0], interval[1]) for interval in intervals],
        )
        for item in speech_events:
            # An event is confirmed at the end of the first inactive SDK frame.
            self.assertGreater(item["available_ns"],
                               reference.AVAILABILITY_ORIGIN_NS
                               + item["source_end"] * reference.NS_PER_SAMPLE)
        self.assertLessEqual(speech_events[0]["available_ns"],
                             speech_events[1]["available_ns"])
        self.assertEqual(self.document["boundaries_and_availability"]["speech_event_intervals"],
                         speech_events)

    def test_stratified_known_positives_and_negatives(self) -> None:
        scoring = self.scoring
        self.assertEqual((scoring["tp"], scoring["fn"], scoring["fp"], scoring["tn"]),
                         (1440, 1280, 480, 12800))
        self.assertEqual(scoring["speech_samples"], 2720)
        self.assertEqual(scoring["nonspeech_samples"], 13280)
        by_id = {item["id"]: item for item in scoring["per_segment"]}
        self.assertEqual(by_id["quiet_speech"]["tp"], 320)
        self.assertEqual(by_id["quiet_speech"]["fn"], 480)
        self.assertEqual(by_id["active_speech"]["tp"], 1120)
        self.assertEqual(by_id["active_speech"]["fn"], 0)
        self.assertEqual(by_id["threshold_speech"]["fn"], 800)
        self.assertEqual(by_id["idle_loud"]["fp"], 480)
        self.assertEqual(by_id["idle_tail"]["tn"], 11680)
        self.assertGreater(by_id["idle_loud"]["probability_mean"],
                           by_id["threshold_speech"]["probability_mean"])

    def test_onset_and_offset_delay_are_recorded(self) -> None:
        by_id = {item["id"]: item for item in self.scoring["per_segment"]}
        quiet = by_id["quiet_speech"]
        active = by_id["active_speech"]
        self.assertIsNotNone(quiet["onset_delay_samples"])
        self.assertIsNotNone(quiet["offset_delay_samples"])
        self.assertIsNotNone(active["onset_delay_samples"])
        self.assertIsNotNone(active["offset_delay_samples"])
        self.assertEqual(quiet["onset_delay_samples"], 480)
        self.assertEqual(quiet["offset_delay_samples"], -160)
        self.assertEqual(active["onset_delay_samples"], 160)
        self.assertEqual(active["offset_delay_samples"], 0)
        self.assertIsNone(by_id["threshold_speech"]["detection_start"])

    def test_cross_hop_intervals_are_gap_free(self) -> None:
        session = reference.Session(epoch=1, session_id="cross-hop")
        fixtures.feed_stream(session, fixtures.build_samples())
        decisions = session.frame_decisions
        self.assertEqual(len(decisions), 100)
        self.assertEqual(
            reference.merge_intervals(
                (item["source_start"], item["source_end"]) for item in decisions),
            [[0, 16000]],
        )
        active = [item for item in decisions if item["label"]]
        merged = reference.merge_intervals(
            (item["source_start"], item["source_end"]) for item in active)
        self.assertEqual(merged, [[640, 960], [1920, 3520]])
        second = [item for item in active if item["source_start"] >= 1920]
        self.assertEqual(len({item["window_start"] for item in second}), 5)

    def test_independent_state_and_stale_events(self) -> None:
        state = self.scenarios["independent_state"]
        self.assertTrue(state["distinct_event_digests"])
        self.assertTrue(state["right_unchanged_by_left_reset"])
        self.assertEqual(state["stale_event_rejected_left"]["reason"], "stale_event_epoch")
        self.assertEqual(state["stale_event_rejected_right"]["reason"], "stale_event_epoch")
        self.assertNotEqual(state["before"]["left"]["epoch"], state["before"]["right"]["epoch"])

    def test_dropped_stale_and_invalid_events_are_explicit(self) -> None:
        events = self.scenarios["event_bus"]
        self.assertEqual(events["gaps_recorded"], 2)
        self.assertEqual(events["delivery"]["dropped_sequence_count"], 2)
        self.assertEqual(events["stale_event_rejected"]["reason"], "stale_event_epoch")
        self.assertEqual(events["invalid_event_rejected"]["reason"], "invalid_event_validity")
        self.assertEqual(events["count_after_invalid"], 0)
        gaps = events["delivery"]["gaps"]
        self.assertEqual([gap["missing_sequences"] for gap in gaps], [[1], [3]])

    def test_adverse_controls_reject_without_state_change(self) -> None:
        results = self.scenarios["adverse"]["results"]
        expected = {
            "nonfinite_window": "nonfinite_window",
            "infinite_window": "nonfinite_window",
            "short_frame": "invalid_frame_length",
            "short_valid_count_without_final": "short_frame_without_final",
            "wrong_sample_rate": "invalid_sample_rate",
            "wrong_channel_count": "invalid_channels",
            "wrong_sample_format": "invalid_sample_format",
            "double_size_frame": "invalid_frame_length",
            "stale_epoch": "stale_epoch",
            "bad_source_interval": "invalid_source_interval",
            "nonzero_final_padding": "nonzero_final_padding",
        }
        for name, reason in expected.items():
            with self.subTest(name=name):
                self.assertEqual(results[name]["status"], "rejected")
                self.assertEqual(results[name]["reason"], reason)
                self.assertTrue(results[name]["state_unchanged"])
                self.assertEqual(results[name]["rejection_count"], 1)

    def test_invalid_is_never_nonspeech(self) -> None:
        results = self.scenarios["adverse"]["results"]
        self.assertFalse(results["valid_nonspeech_frame"]["window_label"])
        self.assertTrue(results["valid_nonspeech_frame"]["counted_as_nonspeech_not_invalid"])
        separation = results["invalid_vs_nonspeech_separation"]
        self.assertEqual(separation["invalid_rejections_recorded"], 11)
        self.assertEqual(separation["invalid_samples_in_primary_denominator"], 0)
        self.assertEqual(separation["nonspeech_samples_in_primary_denominator"], 13280)
        self.assertTrue(separation["invalid_never_labeled_nonspeech"])
        validity = self.document["validity_separation"]
        self.assertEqual(validity["known_samples"], 16000)
        self.assertEqual(validity["unknown_samples"], 0)
        self.assertEqual(validity["nonspeech_samples"], 13280)

    def test_final_partial_frame_has_exact_source_interval(self) -> None:
        samples = fixtures.build_samples()
        session = reference.Session(epoch=1, session_id="final-partial")
        first = session.process_frame(samples[:160], epoch=1, first_input_sample=0)
        tail = [0.0] * 160
        tail[:5] = samples[:5]
        second = session.process_frame(tail, epoch=1, first_input_sample=160,
                                       valid_count=5, final=True)
        drain = session.drain()
        self.assertEqual(first["status"], "ok")
        self.assertEqual(second["status"], "ok")
        self.assertEqual(drain["produced_windows"], 0)
        self.assertEqual(drain["status"], "end_of_stream")
        window = second["window"]
        self.assertEqual((window["source_start"], window["source_end"]), (0, 165))
        self.assertEqual(window["padded_samples"], 155)
        self.assertEqual(session.frame_decisions[-1]["source_end"], 165)
        probability_events = [event for event in session.events
                              if event.kind == "speech_probability"]
        self.assertEqual(probability_events[-1].source_end, 165)
        self.assertEqual(probability_events[-1].available_ns,
                         reference.AVAILABILITY_ORIGIN_NS + 165 * reference.NS_PER_SAMPLE)

    def test_adapter_inspect_boundary(self) -> None:
        request = dict(report.REQUESTS["primary"])
        request["operation"] = "inspect"
        for field in ("attempt_id", "session_id", "epoch", "scenario"):
            request.pop(field, None)
        result = run.inspect(request)
        self.assertEqual(result["identity"], reference.IDENTITY)
        self.assertEqual(result["boundary_identity"], reference.ADAPTER_IDENTITY)
        self.assertEqual(result["supported_scenarios"], list(run.SCENARIOS))
        self.assertEqual(result["registration"],
                         "unregistered developer-only fixture; not an SDK provider or bench result")

    def test_cli_roundtrip_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_bytes(run.canonical_bytes(report.REQUESTS["primary"]))
            completed = subprocess.run(
                [sys.executable, str(HERE / "run.py"), "--request", str(request_path),
                 "--result", str(result_path)],
                cwd=str(HERE), capture_output=True, text=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(result_path.read_bytes(),
                             run.canonical_bytes(run.run(report.REQUESTS["primary"])))

    def test_blocked_real_qualification_is_explicit(self) -> None:
        qualification = self.document["qualification"]
        self.assertEqual(qualification["status"], "incomplete")
        self.assertEqual(qualification["release_decision"], "not_qualified")
        self.assertIn("never counted as passes", qualification["missing_result_policy"])
        blocked = self.document["blocked"]
        self.assertEqual(blocked["matched_cohort"]["status"], "blocked")
        self.assertEqual(blocked["intended_execution_profile"]["status"], "blocked")
        self.assertIn("heldout-results.json", blocked["matched_cohort"]["missing_artifact"])
        self.assertGreaterEqual(len(self.document["non_claims"]), 5)


if __name__ == "__main__":
    unittest.main()
