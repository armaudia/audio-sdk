# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance suite for the SDK-BEATNET evidence package.

The suite is offline, stdlib-only and read-only. It exercises strict JSON,
fixture arithmetic, tempo/beat/meter estimation, block invariance, reset,
caller-asset identity validation and the exact adverse rejection matrix.
"""

from __future__ import annotations

import sys
import unittest

sys.dont_write_bytecode = True

import reference  # noqa: E402


class ReportIdentityTests(unittest.TestCase):
    def test_disposition_is_defer_not_qualified(self):
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["qualifies"])

    def test_eight_blocked_release_gates(self):
        gates = reference.build_report()["release_gates"]
        self.assertEqual([row["id"] for row in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(row["status"] == "blocked" for row in gates))

    def test_rate_profile_items_are_synthetic_or_blocked(self):
        profile = reference.build_report()["acceptance_profile"]
        self.assertEqual(profile["profile"], "rate")
        self.assertEqual(len(profile["required_items"]), 8)
        statuses = {row["status"] for row in profile["required_items"].values()}
        self.assertTrue(statuses.issubset({"synthetic_only", "blocked"}))
        blocked = sorted(name for name, row in profile["required_items"].items()
                         if row["status"] == "blocked")
        self.assertEqual(report_blockers(), blocked)

    def test_candidate_rate_conflict_is_explicit(self):
        report = reference.build_report()
        candidate = report["candidate"]
        self.assertEqual(candidate["reported_input_sample_rate_hz"], 22050)
        self.assertEqual(candidate["sdk_v0_sample_rate_hz"], 16000)
        self.assertEqual(candidate["configured_resampling"], "none")
        self.assertFalse(candidate["native_rate_compatible"])
        self.assertFalse(candidate["source_present"])
        self.assertFalse(candidate["weights_present"])
        self.assertFalse(candidate["runtime_present"])

    def test_all_boundary_flags_false(self):
        report = reference.build_report()
        self.assertTrue(all(value is False
                            for value in report["boundary"].values()))
        self.assertTrue(report["scope"]["synthetic_only"])
        self.assertTrue(report["scope"]["task_local_only"])
        for key, value in report["scope"].items():
            if key not in {"synthetic_only", "task_local_only"}:
                self.assertIs(value, False, key)

    def test_no_result_is_promoted(self):
        report = reference.build_report()
        self.assertTrue(report["adverse_all_rejected"])
        for case in report["adverse_rejections"]:
            self.assertEqual(case["status"], "rejected")
            self.assertTrue(case["state_unchanged"])
        for case in report["tempo_tracking"]["cases"]:
            self.assertIs(case["qualifies"], False)
        for case in report["beat_tracking"]["cases"]:
            self.assertIs(case["qualifies"], False)
        for case in report["downbeat_meter"]["cases"]:
            self.assertIs(case["qualifies"], False)
        self.assertFalse(report["qualification"]["missing_result_promoted"])


def report_blockers():
    profile = reference.build_report()["acceptance_profile"]
    return sorted(name for name, row in profile["required_items"].items()
                  if row["status"] == "blocked")


class TempoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.tempo = {row["stimulus"]: row
                     for row in cls.report["tempo_tracking"]["cases"]}

    def test_identity_tempo(self):
        self.assertEqual(self.tempo["steady_music_1x"]["status"], "stable")
        self.assertEqual(self.tempo["steady_music_1x"]["bpm_x100"], 10000)

    def test_rate_projections(self):
        self.assertEqual(self.tempo["rate_0_8"]["bpm_x100"], 8000)
        self.assertEqual(self.tempo["rate_1_2"]["bpm_x100"], 12000)

    def test_tempo_step_segments(self):
        step = self.report["tempo_tracking"]["tempo_step"]
        self.assertEqual(step["observed_segments"], [10000, 15000])
        self.assertTrue(step["exact"])
        self.assertEqual(step["global_status"], "unstable")

    def test_speech_like_is_unstable(self):
        self.assertEqual(self.tempo["speech_like_unfamiliar"]["status"],
                         "unstable")
        self.assertIsNone(self.tempo["speech_like_unfamiliar"]["bpm_x100"])

    def test_silence_has_no_onsets(self):
        self.assertEqual(self.tempo["silence"]["status"], "no_onsets")
        self.assertEqual(self.tempo["silence"]["ioi_frames"], [])

    def test_rebuffer_excludes_cross_gap_ioi(self):
        row = self.tempo["rebuffer_gap"]
        self.assertEqual(row["excluded_ioi_count"], 1)
        self.assertEqual(row["bpm_x100"], 12000)
        self.assertTrue(self.report["rate_profile"]["rebuffer"][
            "cross_gap_ioi_suppressed"])

    def test_drift_has_no_global_tempo(self):
        row = self.tempo["drift_decreasing"]
        self.assertEqual(row["status"], "unstable")
        self.assertIsNone(row["bpm_x100"])
        self.assertTrue(self.report["rate_profile"]["drift"][
            "monotonic_decreasing"])

    def test_tempo_out_of_range_is_unstable(self):
        values = self.tempo["speech_like_unfamiliar"]["ioi_frames"]
        self.assertGreater(len(values), 4)


class BeatMeterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.beats = {row["stimulus"]: row
                     for row in cls.report["beat_tracking"]["cases"]}
        cls.meters = {row["stimulus"]: row
                      for row in cls.report["downbeat_meter"]["cases"]}

    def test_steady_beats_match_exactly(self):
        for name in ("steady_music_1x", "rate_0_8", "rate_1_2"):
            row = self.beats[name]
            self.assertEqual(row["matched"], row["truth"])
            self.assertEqual(row["false_positives"], 0)
            self.assertEqual(row["false_negatives"], 0)
            self.assertEqual(row["f1_x1000"], 1000)

    def test_tempo_step_and_gap_beats_match(self):
        for name in ("tempo_step", "rebuffer_gap", "drift_decreasing",
                     "final_partial"):
            row = self.beats[name]
            self.assertEqual(row["matched"], row["truth"], name)
            self.assertEqual(row["f1_x1000"], 1000, name)

    def test_silence_has_no_beats(self):
        self.assertEqual(self.beats["silence"]["detected"], 0)
        self.assertIsNone(self.beats["silence"]["f1_x1000"])

    def test_meter_estimates_are_synthetic_only(self):
        for name in ("steady_music_1x", "rate_0_8", "rate_1_2"):
            self.assertEqual(self.meters[name]["meter"], 4)
            self.assertTrue(self.meters[name]["correct"])
            self.assertEqual(self.meters[name]["status"], "synthetic_only")
        self.assertEqual(self.meters["syncopated_offbeat"]["status"],
                         "ambiguous")
        self.assertIsNone(self.meters["syncopated_offbeat"]["meter"])
        self.assertFalse(self.report["downbeat_meter"]["truth_available"])


class FormatAndRateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()
        cls.rate = cls.report["rate_profile"]

    def test_duration_spans_are_exact(self):
        self.assertEqual(self.rate["duration"]["max_error_samples"], 0)
        for row in self.rate["duration"]["cases"].values():
            self.assertEqual(row["error_samples"], 0)

    def test_pitch_is_not_claimed(self):
        self.assertEqual(self.rate["pitch"]["status"],
                         "not_measurable_analysis_only")
        self.assertFalse(self.rate["pitch"]["qualifies"])

    def test_final_partial_window(self):
        final = self.rate["final_partial"]
        self.assertEqual(final["valid_count"], 137)
        self.assertTrue(final["padding_zero"])
        self.assertEqual(final["truth_source_start"], 64010)
        self.assertEqual(final["detected_source_start"], 64000)
        self.assertEqual(self.rate["transient_proxy"][
            "final_partial_error_samples"], -10)

    def test_no_audio_or_device_buffering_claim(self):
        buffering = self.rate["playback_buffering"]
        self.assertFalse(buffering["device_buffer_measured"])
        self.assertEqual(buffering["sdk_worker_count"], 0)
        self.assertEqual(buffering["sdk_queue_depth"], 0)
        self.assertFalse(self.rate["source_output_mapping"][
            "audio_output_produced"])

    def test_streaming_chunks_match_offline(self):
        streaming = self.report["streaming"]
        self.assertTrue(streaming["all_match"])
        self.assertEqual(streaming["accepted_samples"], 64137)
        self.assertFalse(streaming["scheduler_measured"])
        self.assertTrue(all(row["matches_offline"]
                            for row in streaming["results"]))

    def test_reset_matches_fresh_session(self):
        self.assertTrue(self.report["reset"]["matches_fresh"])


class StrictInputTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate_and_nonfinite(self):
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":1,"a":2}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":NaN}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":Infinity}')
        with self.assertRaises(ValueError):
            reference.load_strict_json_text('{"a":')

    def test_native_rate_is_rejected(self):
        config = {"sample_rate_hz": 22050, "channels": 1,
                  "frame_samples": 160, "sample_format": "float32",
                  "clock_ppm": 0, "resampling": "none"}
        with self.assertRaises(reference.ReferenceRejection) as caught:
            reference.validate_config(config)
        self.assertEqual(caught.exception.code,
                         "candidate_native_rate_requires_resampling")

    def test_nonfinite_frame_is_rejected_without_state_change(self):
        analyzer = reference.Analyzer()
        signal = reference.generate_signal(reference.STIMULI["steady_music_1x"])
        analyzer.process_frame(signal[:160])
        before = analyzer.state_digest
        with self.assertRaises(reference.ReferenceRejection):
            analyzer.process_frame([float("nan")] + list(signal[161:320]))
        self.assertEqual(before, analyzer.state_digest)

    def test_nonzero_padding_is_rejected(self):
        analyzer = reference.Analyzer()
        signal = reference.generate_signal(reference.STIMULI["steady_music_1x"])
        frame = list(signal[:137]) + [1.0] + list(signal[138:159])
        with self.assertRaises(reference.ReferenceRejection):
            analyzer.process_frame(frame, valid_count=137)

    def test_epoch_zero_and_negative_are_rejected(self):
        analyzer = reference.Analyzer(epoch=1)
        for epoch in (0, -1):
            with self.assertRaises(reference.ReferenceRejection):
                analyzer.reset(epoch, 0)

    def test_adverse_matrix_is_complete(self):
        cases = reference.adverse_rejections()
        self.assertEqual(len(cases), 40)
        self.assertTrue(all(case["status"] == "rejected" for case in cases))
        self.assertTrue(all(case["state_unchanged"] for case in cases))
        identifiers = {case["case_id"] for case in cases}
        self.assertIn("config_22050_hz_candidate_native", identifiers)
        self.assertIn("caller_manifest_bad_hash", identifiers)
        self.assertIn("frame_nonfinite_input", identifiers)

    def test_fixture_validation_rejects_bad_specs(self):
        spec = dict(reference.STIMULI["steady_music_1x"])
        bad = dict(spec)
        bad["beats_frames"] = [0, 60.5, 120, 180, 240, 300, 360]
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_stimuli({**reference.STIMULI,
                                        "steady_music_1x": bad})

    def test_caller_manifest_is_identity_only(self):
        manifest = {
            "adapter": "beatnet-reference",
            "license_id": "CC-BY-4.0",
            "model_sha256": "0" * 64,
            "sample_format": "float32",
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "source_commit": "0" * 40,
            "source_path": "/caller/beatnet/source",
            "source_sha256": "1" * 64,
            "weights_path": "/caller/beatnet/weights",
            "weights_sha256": "2" * 64,
        }
        result = reference.validate_caller_manifest(manifest)
        self.assertEqual(result, {"validated": True, "loaded": False,
                                  "executed": False, "imported": False})

    def test_canonical_json_is_stable(self):
        value = {"b": [1, 2], "a": {"z": "x"}}
        text = reference.canonical_text(value)
        self.assertEqual(text, '{"a":{"z":"x"},"b":[1,2]}')
        self.assertEqual(reference.object_digest(value),
                         reference.sha256_bytes(text.encode("utf-8")))


class DeterminismTests(unittest.TestCase):
    def test_three_builds_are_byte_identical(self):
        texts = [reference.canonical_report(reference.build_report())[0]
                 for _ in range(3)]
        self.assertEqual(len(set(texts)), 1)
        self.assertEqual(reference.sha256_bytes(texts[0].encode("utf-8")),
                         reference.sha256_bytes(texts[1].encode("utf-8")))

    def test_stable_board_identity(self):
        row = reference.board_row()
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(reference.object_digest(row["stable_fields"]),
                         reference.BOARD_ROW_STABLE_SHA256)

    def test_contract_matches_report(self):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(contract["release_gates"], report["release_gates"])
        self.assertEqual(contract["exact_blockers"], report["exact_blockers"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertIn(reference.TASK_PREFIX + "reference.py",
                      contract["artifact_pins"])


if __name__ == "__main__":
    unittest.main()
