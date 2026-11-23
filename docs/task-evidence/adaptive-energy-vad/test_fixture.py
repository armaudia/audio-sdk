"""Python unittest coverage for the task-local adaptive-energy VAD fixture."""

import json
import unittest
from pathlib import Path

import fixture
from fixture import (
    AVAILABILITY_OFFSET_NS,
    CONTRACT_ID,
    CONFIG_DIGEST,
    FRAME_SAMPLES,
    NS_PER_SAMPLE,
    SCORED_END_SAMPLE,
    SEGMENTS,
    TOTAL_FRAMES,
    TOTAL_SAMPLES,
    AnalysisBus,
    AnalysisEvent,
    EventKind,
    FrameStatus,
    Status,
    Validity,
    build_report,
    canonical,
    check_frame,
    event_adverse_control,
    frame_adverse_control,
    independence_control,
    invalid_vs_nonspeech_control,
    overlapping_session_control,
    place_events,
    sha256_text,
)

REPORT_PATH = Path(__file__).with_name("report.json")
EXPECTED_PCM = "d29c7b9ab0a3f7c3782a83479f8538fcf37e26b35ad5f64e3e7fa8219fb3eb82"


class AdaptiveEnergyVADFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report_text = REPORT_PATH.read_text(encoding="utf-8")
        cls.report = json.loads(cls.report_text)
        cls.frames, cls.pcm_digest = fixture._generate_pcm()
        cls.flat = [sample for frame in cls.frames for sample in frame]

    def test_report_is_canonical_and_pinned(self):
        self.assertEqual(self.report_text, canonical(build_report()))
        self.assertEqual(sha256_text(self.report_text),
                         sha256_text(canonical(self.report)))
        self.assertEqual(self.report["contract"], CONTRACT_ID)
        self.assertEqual(self.report["status"]["claim"], "proposal-only-synthetic")
        self.assertEqual(self.report["status"]["qualification"], "incomplete")
        self.assertFalse(self.report["status"]["installed_sdk_changed"])
        self.assertEqual(len(self.report["blockers"]), 4)
        self.assertEqual(len(self.report["non_claims"]), 4)

    def test_deterministic_generation_and_digests(self):
        again, again_digest = fixture._generate_pcm()
        self.assertEqual(again, self.frames)
        self.assertEqual(again_digest, EXPECTED_PCM)
        self.assertEqual(self.report["digests"]["pcm_f32_sha256"], EXPECTED_PCM)
        self.assertEqual(self.report["digests"]["audio_view_sha256"],
                         AnalysisBus(1, 0, self.flat).audio_digest)
        self.assertEqual(self.report["fixture"]["config_digest"], CONFIG_DIGEST)
        for key in ("probability_stream_sha256", "speech_events_sha256"):
            self.assertEqual(len(self.report["digests"][key]), 64)

    def test_timeline_counts_and_source_pins(self):
        fixture_spec = self.report["fixture"]
        self.assertEqual(fixture_spec["total_frames"], TOTAL_FRAMES)
        self.assertEqual(fixture_spec["total_samples"], TOTAL_SAMPLES)
        self.assertEqual(fixture_spec["scored_end_sample"], SCORED_END_SAMPLE)
        self.assertEqual(len(SEGMENTS), 8)
        self.assertEqual(len(self.report["source_pins"]), 7)
        for path, digest in self.report["source_pins"].items():
            self.assertEqual(len(digest), 64, path)
        self.assertIn("adapters/adaptive-energy-vad/adapter.json",
                      self.report["source_pins"])

    def test_probability_levels_are_distinct_by_condition(self):
        rows = self.report["probability_stream"]
        for segment in SEGMENTS:
            indices = range(segment.start_frame, segment.end_frame)
            values = [rows[index]["value"] for index in indices]
            self.assertTrue(all(0.0 <= value <= 1.0 for value in values))
            self.assertLess(max(values) - min(values), 1e-6, segment.name)
            if segment.label == "speech":
                self.assertGreater(values[0], 0.5, segment.name)
            elif segment.name == "noise-burst":
                self.assertLess(values[0], 0.5, segment.name)
            elif segment.label == "nonspeech":
                self.assertLess(values[0], 0.5, segment.name)
        idle = rows[0]["value"]
        quiet = rows[60]["value"]
        active = rows[150]["value"]
        self.assertLess(idle, quiet)
        self.assertLess(quiet, active)

    def test_timestamped_probability_events_are_exact(self):
        rows = self.report["probability_stream"]
        self.assertEqual(len(rows), TOTAL_FRAMES)
        for index, row in enumerate(rows):
            self.assertEqual(row["source_start"], index * FRAME_SAMPLES)
            self.assertEqual(row["source_end"], (index + 1) * FRAME_SAMPLES)
            if index >= 300:
                self.assertIsNone(row["available_ns"])
            else:
                self.assertEqual(row["available_ns"],
                                 row["source_end"] * NS_PER_SAMPLE
                                 + AVAILABILITY_OFFSET_NS)
            self.assertEqual(row["validity"],
                             "unknown" if index >= 300 else "known")

    def test_detection_boundaries_and_delays(self):
        events = self.report["speech_events"]
        self.assertEqual(len(events), 3)
        self.assertEqual(
            [(event["source_start"], event["source_end"]) for event in events],
            [(61 * FRAME_SAMPLES, 122 * FRAME_SAMPLES),
             (151 * FRAME_SAMPLES, 212 * FRAME_SAMPLES),
             (241 * FRAME_SAMPLES, 272 * FRAME_SAMPLES)],
        )
        for timing in self.report["scoring"]["timings"]:
            self.assertEqual(timing["status"], "ok")
            self.assertEqual(timing["onset_delay_samples"], FRAME_SAMPLES)
            self.assertEqual(timing["offset_delay_samples"], 2 * FRAME_SAMPLES)
            self.assertEqual(timing["detected_frames"],
                             timing["truth_frames"] + 1)

    def test_detections_and_stratified_counts(self):
        score = self.report["scoring"]
        self.assertEqual(score["totals"],
                         {"tp": 147, "fn": 3, "fp": 6, "tn": 144})
        self.assertEqual(sum(score["totals"].values()), 300)
        self.assertAlmostEqual(score["speech_miss_rate"], 3 / 150)
        self.assertAlmostEqual(score["false_alarm_rate"], 6 / 150)
        self.assertEqual(score["scored_samples"], SCORED_END_SAMPLE)
        self.assertEqual(score["unknown_samples"], 30 * FRAME_SAMPLES)
        self.assertEqual(score["unknown_validity_events"], 30)
        stratified = score["stratified"]
        self.assertEqual(stratified["quiet-a"],
                         {"tp": 59, "fn": 1, "fp": 0, "tn": 0})
        self.assertEqual(stratified["idle-b"],
                         {"tp": 0, "fn": 0, "fp": 2, "tn": 28})
        self.assertEqual(stratified["noise-burst"],
                         {"tp": 0, "fn": 0, "fp": 2, "tn": 28})
        self.assertEqual(stratified["quiet-b"],
                         {"tp": 29, "fn": 1, "fp": 0, "tn": 0})
        self.assertEqual(stratified["idle-a"],
                         {"tp": 0, "fn": 0, "fp": 0, "tn": 60})

    def test_invalid_is_separate_from_nonspeech(self):
        control = self.report["adverse_controls"]["invalid_vs_nonspeech"]
        self.assertEqual(control["statuses"], {
            "known_zero": "ok",
            "nan_probability": "rejected_invalid_event",
            "out_of_range_probability": "rejected_invalid_event",
            "unknown_probability": "ok",
        })
        self.assertEqual(control["admitted_event_ids"], ["known-zero", "unknown"])
        self.assertEqual(control["known_nonspeech_events"], 1)
        self.assertEqual(control["invalid_events_excluded"], 2)
        self.assertEqual(control["unknown_events_excluded"], 1)
        self.assertFalse(control["invalid_counted_as_nonspeech"])
        known_zero = invalid_vs_nonspeech_control()["statuses"]["known_zero"]
        self.assertEqual(known_zero, Status.OK.value)

    def test_invalid_nonfinite_and_wrong_shape_frames(self):
        control = frame_adverse_control()
        self.assertEqual(control,
                         self.report["adverse_controls"]["frame_adverse"])
        self.assertEqual(control["missing"], "rejected_missing_frame")
        self.assertEqual(control["nonfinite"], "rejected_nonfinite")
        self.assertEqual(control["infinite"], "rejected_nonfinite")
        self.assertEqual(control["short"], "rejected_short_frame")
        self.assertEqual(control["long"], "rejected_tensor")
        self.assertEqual(control["wrong_shape"], "rejected_tensor")
        self.assertTrue(control["state_unchanged"])
        self.assertEqual(control["short_final_status"], "ok")
        self.assertEqual(control["short_final_valid_count"], 80)
        self.assertEqual(control["short_final_source_end"], 80)
        self.assertEqual(control["stale_epoch"], "rejected_epoch")
        self.assertEqual(control["wrong_interval"], "rejected_interval")
        self.assertEqual(check_frame([0.0] * FRAME_SAMPLES)[0], FrameStatus.OK)

    def test_stale_and_dropped_events_are_audited(self):
        control = event_adverse_control()
        self.assertEqual(control, self.report["adverse_controls"]["event_adverse"])
        self.assertEqual(control["statuses"]["stale_epoch"], "rejected_stale_epoch")
        self.assertEqual(control["statuses"]["before_first_sample"],
                         "rejected_stale_epoch")
        self.assertEqual(control["statuses"]["stale_availability"],
                         "rejected_bad_clock")
        self.assertEqual(control["statuses"]["wrong_clock"], "rejected_bad_clock")
        self.assertTrue(control["events_unchanged"])
        self.assertEqual(control["dropped_reasons"], [
            "rejected_stale_epoch", "rejected_stale_epoch",
            "rejected_bad_clock", "rejected_bad_clock"])

    def test_independent_state_and_reset(self):
        control = independence_control(self.frames)
        self.assertEqual(control,
                         self.report["adverse_controls"]["independent_state"])
        self.assertTrue(control["independent_noise_estimates"])
        self.assertTrue(control["reset_matches_fresh_run"])
        self.assertEqual(control["left_epoch"], 2)
        self.assertEqual(control["right_epoch"], 7)
        self.assertEqual(control["left_frames"], control["right_frames"])
        bus = AnalysisBus(epoch=1, first_sample=0, audio=self.flat[:FRAME_SAMPLES])
        event = AnalysisEvent("first", EventKind.SPEECH_PROBABILITY,
                              fixture.PRODUCER_ID,
                              fixture.TAP_ID, 1, 0, FRAME_SAMPLES, 0.4,
                              Validity.KNOWN, AVAILABILITY_OFFSET_NS,
                              fixture.CLOCK_ID, CONFIG_DIGEST)
        self.assertEqual(bus.publish(event), Status.OK)
        self.assertEqual(bus.reset(2, 0, self.flat[:FRAME_SAMPLES]), Status.OK)
        self.assertEqual(bus.events, [])
        self.assertEqual(bus.publish(event), Status.REJECTED_STALE_EPOCH)
        self.assertEqual(len(bus.resets), 1)
        self.assertEqual(bus.resets[0]["cancelled_events"], 1)

    def test_overlapping_sessions_do_not_share_events_or_audio(self):
        control = overlapping_session_control(self.frames)
        self.assertEqual(control,
                         self.report["adverse_controls"]["overlapping_sessions"])
        self.assertEqual(control["first_accept"], "ok")
        self.assertEqual(control["second_reject"], "rejected_stale_epoch")
        self.assertEqual((control["first_events"], control["second_events"]),
                         (1, 0))
        self.assertTrue(control["distinct_audio"])

    def test_cross_hop_interval_placement_is_exact(self):
        control = place_events([AnalysisEvent(
            "x", EventKind.SPEECH_PROBABILITY, fixture.PRODUCER_ID,
            fixture.TAP_ID, 1, 150, 330, 0.75, Validity.KNOWN,
            AVAILABILITY_OFFSET_NS, fixture.CLOCK_ID, CONFIG_DIGEST)],
            total_samples=480)
        placement = [(item.frame_index, item.overlap_samples)
                     for item in control["x"]]
        self.assertEqual(placement, [(0, 10), (1, 160), (2, 10)])
        self.assertEqual(self.report["adverse_controls"]["cross_hop"],
                         {"source_interval": [150, 330],
                          "placement": [[0, 10], [1, 160], [2, 10]],
                          "exact": True, "total_overlap": 180})

    def test_source_intervals_and_availability_controls(self):
        controls = self.report["adverse_controls"]
        self.assertTrue(all(controls["source_intervals"].values()))
        self.assertTrue(controls["availability"]["probability_availability_monotonic"])
        self.assertTrue(controls["availability"]["unknown_events_have_no_availability"])
        self.assertEqual(controls["availability"]["offset_ns"],
                         AVAILABILITY_OFFSET_NS)

    def test_adapter_divergence_and_real_qualification_blockers(self):
        blockers = self.report["blockers"]
        self.assertTrue(any("frame_samples=320" in item for item in blockers))
        self.assertTrue(any("matched cohort" in item for item in blockers))
        self.assertTrue(any("licensed/native" in item for item in blockers))
        self.assertTrue(any("not part of the frozen v0 ABI" in item
                            for item in blockers))
        self.assertEqual(fixture.ADAPTER_FRAME_SAMPLES, 320)
        self.assertEqual(FRAME_SAMPLES, 160)

    def test_no_missing_required_results(self):
        required = ("invalid_vs_nonspeech", "frame_adverse", "event_adverse",
                    "independent_state", "overlapping_sessions", "cross_hop",
                    "source_intervals", "availability")
        for name in required:
            self.assertIn(name, self.report["adverse_controls"])
            self.assertIsNotNone(self.report["adverse_controls"][name])
        for key in ("tp", "fn", "fp", "tn"):
            self.assertIsNotNone(self.report["scoring"]["totals"][key])
        for key in ("speech_miss_rate", "false_alarm_rate"):
            self.assertIsNotNone(self.report["scoring"][key])


if __name__ == "__main__":
    unittest.main()
