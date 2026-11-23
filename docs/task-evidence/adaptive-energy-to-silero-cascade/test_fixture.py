"""Deterministic unittest suite for the task-local cascade fixture."""

from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

import fixture


REPORT_PATH = fixture.TASK_DIR / "report.json"
REPORT = json.loads(REPORT_PATH.read_text(encoding="utf-8"))


class CascadeFixtureTest(unittest.TestCase):
    def test_01_manifest_resolves(self) -> None:
        pins = fixture.read_source_manifest()
        self.assertGreaterEqual(len(pins), 15)
        for name in pins:
            self.assertTrue(name.startswith(("workspace:", "local:")))
            self.assertTrue(fixture.resolve_pin_path(name).is_file(), name)

    def test_02_all_pins_verify(self) -> None:
        results = fixture.verify_source_manifest()
        self.assertTrue(results)
        self.assertTrue(all(results.values()), results)

    def test_03_report_uses_manifest_pins(self) -> None:
        self.assertEqual(REPORT["source_pins"], fixture.read_source_manifest())
        self.assertTrue(all(REPORT["source_pin_verification"].values()))

    def test_04_report_is_canonical_and_byte_identical(self) -> None:
        data = REPORT_PATH.read_bytes()
        self.assertEqual(data.decode("utf-8"), fixture.canonical(REPORT))
        self.assertEqual(data, fixture.canonical(fixture.build_report()).encode("utf-8"))

    def test_05_report_digest_file(self) -> None:
        digest = hashlib.sha256(REPORT_PATH.read_bytes()).hexdigest()
        recorded = (fixture.TASK_DIR / "report.json.sha256").read_text(
            encoding="utf-8").strip()
        self.assertEqual(recorded, digest)

    def test_06_build_report_deterministic(self) -> None:
        self.assertEqual(fixture.canonical(fixture.build_report()),
                         fixture.canonical(fixture.build_report()))

    def test_07_no_missing_results(self) -> None:
        controls = REPORT["adverse_controls"]
        completeness = controls["control_completeness"]
        self.assertTrue(completeness["all_present"])
        self.assertTrue(completeness["no_missing_results"])
        for name in completeness["required_controls"]:
            self.assertIn(name, controls)
            self.assertIsNotNone(controls[name])
        self.assertNotIn(None, REPORT["scoring"]["timings"])
        for timing in REPORT["scoring"]["timings"]:
            for key, value in timing.items():
                self.assertIsNotNone(value, (timing["segment"], key))

    def test_08_status_is_incomplete_synthetic(self) -> None:
        status = REPORT["status"]
        self.assertEqual(status["claim"], "proposal-only-synthetic")
        self.assertEqual(status["qualification"], "incomplete")
        self.assertFalse(status["installed_sdk_changed"])
        self.assertEqual(status["silero_stage"], "model-free-stub")
        self.assertEqual(REPORT["pinned_base"], fixture.PINNED_BASE)

    def test_09_segments_partition_all_frames(self) -> None:
        segments = REPORT["fixture"]["segments"]
        self.assertEqual([row["start_frame"] for row in segments],
                         [0] + [row["end_frame"] for row in segments[:-1]])
        self.assertEqual(segments[-1]["end_frame"], fixture.TOTAL_FRAMES)
        self.assertEqual(REPORT["fixture"]["total_samples"], fixture.TOTAL_SAMPLES)
        self.assertEqual(REPORT["fixture"]["scored_end_sample"], fixture.SCORED_END_SAMPLE)

    def test_10_pcm_digest_matches_generator(self) -> None:
        _, digest = fixture.generate_frames()
        self.assertEqual(REPORT["digests"]["pcm_f32_sha256"], digest)

    def test_11_probability_streams_present(self) -> None:
        streams = {row["stream"] for row in REPORT["probability_stream"]}
        self.assertEqual(streams, {"gate_probability", "stub_probability",
                                   "cascade_probability"})
        for stream, key in (
            ("gate_probability", "gate_probability_stream_sha256"),
            ("stub_probability", "stub_probability_stream_sha256"),
            ("cascade_probability", "cascade_probability_stream_sha256"),
        ):
            rows = [row for row in REPORT["probability_stream"]
                    if row["stream"] == stream]
            self.assertEqual(fixture.sha256_text(fixture.canonical(rows)),
                             REPORT["digests"][key], stream)

    def test_12_probability_intervals_are_exact(self) -> None:
        for stream in ("gate_probability", "cascade_probability"):
            rows = [row for row in REPORT["probability_stream"]
                    if row["stream"] == stream]
            self.assertEqual(len(rows), fixture.TOTAL_FRAMES, stream)
            for index, row in enumerate(rows):
                self.assertEqual(row["source_start"], index * fixture.FRAME_SAMPLES)
                self.assertEqual(row["source_end"], (index + 1) * fixture.FRAME_SAMPLES)
        stub_rows = [row for row in REPORT["probability_stream"]
                     if row["stream"] == "stub_probability"]
        self.assertTrue(stub_rows)
        self.assertTrue(all(row["stub_invoked"] for row in stub_rows))

    def test_13_probability_values_are_valid(self) -> None:
        for row in REPORT["probability_stream"]:
            self.assertIn(row["validity"], ("known", "unknown"))
            if row["validity"] == "known":
                self.assertTrue(math.isfinite(row["value"]))
                self.assertGreaterEqual(row["value"], 0.0)
                self.assertLessEqual(row["value"], 1.0)
                self.assertIsNotNone(row["available_ns"])
            else:
                self.assertIsNone(row["available_ns"])

    def test_14_availability_is_monotonic(self) -> None:
        control = REPORT["adverse_controls"]["availability"]
        self.assertTrue(control["known_probability_availability_monotonic"])
        self.assertTrue(control["unknown_events_have_no_availability"])
        self.assertEqual(control["bus_dropped_events"], 0)
        self.assertGreater(control["bus_events"], 0)

    def test_15_speech_events_have_boundaries(self) -> None:
        rows = REPORT["speech_events"]
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(row["source_start"] % fixture.FRAME_SAMPLES, 0)
            self.assertEqual(row["source_end"] % fixture.FRAME_SAMPLES, 0)
            self.assertEqual(row["source_start"], row["onset_frame"] * fixture.FRAME_SAMPLES)
            self.assertEqual(row["source_end"], row["offset_frame"] * fixture.FRAME_SAMPLES)
            self.assertLess(row["source_start"], row["source_end"])
        self.assertEqual(fixture.sha256_text(fixture.canonical(rows)),
                         REPORT["digests"]["speech_events_sha256"])

    def test_16_events_inside_scored_region(self) -> None:
        intervals = REPORT["adverse_controls"]["source_intervals"]
        self.assertTrue(intervals["speech_events_frame_aligned"])
        self.assertTrue(intervals["speech_events_inside_scored_region"])
        self.assertTrue(intervals["probability_intervals_contiguous"])
        self.assertEqual(intervals["gate_probability_rows"], fixture.TOTAL_FRAMES)

    def test_17_confusion_counts_sum_to_scored_frames(self) -> None:
        totals = REPORT["scoring"]["totals"]
        self.assertEqual(sum(totals.values()), fixture.SCORED_END_FRAME)
        self.assertEqual(REPORT["scoring"]["known_positives"],
                         totals["tp"] + totals["fn"])
        self.assertEqual(REPORT["scoring"]["known_negatives"],
                         totals["tn"] + totals["fp"])

    def test_18_stratified_counts_match_totals(self) -> None:
        totals = REPORT["scoring"]["totals"]
        accumulated = {key: 0 for key in totals}
        for row in REPORT["scoring"]["stratified"].values():
            for key in totals:
                accumulated[key] += row[key]
        self.assertEqual(accumulated, totals)
        strata = REPORT["scoring"]["strata"]
        accumulated = {key: 0 for key in totals}
        for row in strata.values():
            for key in totals:
                accumulated[key] += row[key]
        self.assertEqual(accumulated, totals)

    def test_19_rates_match_counts(self) -> None:
        scoring = REPORT["scoring"]
        totals = scoring["totals"]
        expected_fn = totals["fn"] / (totals["tp"] + totals["fn"])
        expected_fp = totals["fp"] / (totals["tn"] + totals["fp"])
        self.assertAlmostEqual(scoring["speech_miss_rate"], expected_fn)
        self.assertAlmostEqual(scoring["false_alarm_rate"], expected_fp)
        self.assertEqual(scoring["unknown_samples"], 30 * fixture.FRAME_SAMPLES)

    def test_20_quiet_and_active_speech_detected(self) -> None:
        timings = {row["segment"]: row for row in REPORT["scoring"]["timings"]}
        for name in ("quiet-a", "active-a", "quiet-b"):
            self.assertEqual(timings[name]["status"], "ok", name)
            self.assertGreaterEqual(timings[name]["onset_delay_samples"], 0)

    def test_21_stress_domain_failure_is_recorded(self) -> None:
        stress = REPORT["scoring"]["strata"]["cross-environment-stress"]
        self.assertEqual(stress["tp"], 0)
        self.assertEqual(stress["fn"], 30)
        self.assertEqual(REPORT["scoring"]["stratified"]["stress-low-snr"]["fn"], 30)
        timing = next(row for row in REPORT["scoring"]["timings"]
                      if row["segment"] == "stress-low-snr")
        self.assertEqual(timing["status"], "missed")
        policy = REPORT["adverse_controls"]["cascade_policy"]
        self.assertEqual(policy["stress_stratum_fn"], 30)
        self.assertEqual(policy["stress_stratum_frames"], 30)

    def test_22_onset_offset_delays_recorded(self) -> None:
        detected = [row for row in REPORT["scoring"]["timings"]
                    if row["status"] == "ok"]
        self.assertEqual(len(detected), 3)
        for row in detected:
            self.assertIn("onset_delay_samples", row)
            self.assertIn("offset_delay_samples", row)
            self.assertGreaterEqual(row["detected_frames"], 1)

    def test_23_invalid_separate_from_nonspeech(self) -> None:
        control = REPORT["adverse_controls"]["invalid_vs_nonspeech"]
        statuses = control["statuses"]
        self.assertEqual(statuses["known_zero"], "ok")
        self.assertEqual(statuses["nan_probability"], "rejected_invalid_event")
        self.assertEqual(statuses["out_of_range_probability"], "rejected_invalid_event")
        self.assertEqual(statuses["unknown_probability"], "ok")
        self.assertEqual(control["known_nonspeech_events"], 1)
        self.assertEqual(control["invalid_events_excluded"], 2)
        self.assertEqual(control["unknown_events_excluded"], 1)
        self.assertFalse(control["invalid_counted_as_nonspeech"])

    def test_24_frame_adverse_control(self) -> None:
        control = REPORT["adverse_controls"]["frame_adverse"]
        self.assertTrue(control["state_unchanged"])
        self.assertEqual(control["short_final_status"], "ok")
        self.assertEqual(control["short_final_valid_count"], 80)
        self.assertEqual(control["short_final_source_end"], 80)
        self.assertEqual(control["stale_epoch"], "rejected_epoch")
        self.assertEqual(control["wrong_interval"], "rejected_interval")
        for name in ("missing", "nonfinite", "infinite", "short", "long", "wrong_shape"):
            self.assertTrue(control[name].startswith("rejected_"), name)

    def test_25_event_adverse_and_dropped_audit(self) -> None:
        control = REPORT["adverse_controls"]["event_adverse"]
        self.assertEqual(control["statuses"]["stale_epoch"], "rejected_stale_epoch")
        self.assertEqual(control["statuses"]["before_first_sample"], "rejected_stale_epoch")
        self.assertEqual(control["statuses"]["stale_availability"], "rejected_bad_clock")
        self.assertEqual(control["statuses"]["wrong_clock"], "rejected_bad_clock")
        self.assertEqual(control["statuses"]["closed_stream"], "closed")
        self.assertTrue(control["events_unchanged"])
        self.assertEqual(len(control["dropped_reasons"]), 5)
        self.assertEqual(len(control["dropped_event_ids"]), 5)

    def test_26_independent_state(self) -> None:
        control = REPORT["adverse_controls"]["independent_state"]
        for key in ("independent_noise_estimate", "independent_stub_state",
                    "independent_sleep_state", "reset_matches_fresh_run"):
            self.assertTrue(control[key], key)
        self.assertEqual(control["left_epoch"], 2)
        self.assertEqual(control["right_epoch"], 7)

    def test_27_overlapping_sessions(self) -> None:
        control = REPORT["adverse_controls"]["overlapping_sessions"]
        self.assertEqual(control["first_accept"], "ok")
        self.assertEqual(control["second_reject"], "rejected_stale_epoch")
        self.assertEqual(control["first_events"], 1)
        self.assertEqual(control["second_events"], 0)
        self.assertTrue(control["distinct_audio"])

    def test_28_cross_hop_exact_placement(self) -> None:
        control = REPORT["adverse_controls"]["cross_hop"]
        self.assertTrue(control["exact"])
        self.assertEqual(control["placement"]["cross-hop"], [[0, 10], [1, 160], [2, 10]])
        self.assertEqual(control["placement"]["cross-hop-unaligned"], [[1, 147], [2, 13]])
        self.assertEqual(control["total_overlap"]["cross-hop"], 180)
        self.assertEqual(control["total_overlap"]["cross-hop-unaligned"], 160)

    def test_29_cascade_policy_skips(self) -> None:
        policy = REPORT["adverse_controls"]["cascade_policy"]
        self.assertTrue(policy["projected_compute_only"])
        self.assertGreater(policy["stub_invocations"], 0)
        self.assertGreater(policy["stub_skips"], 0)
        self.assertGreater(policy["gate_wakes"], 0)
        self.assertGreater(policy["crosschecks_while_asleep"], 0)
        self.assertAlmostEqual(
            policy["skipped_stub_fraction"],
            policy["stub_skips"] / fixture.TOTAL_FRAMES)

    def test_30_no_real_asset_claims(self) -> None:
        text = fixture.canonical({
            "blockers": REPORT["blockers"], "non_claims": REPORT["non_claims"],
            "contract": fixture.TASK_DIR.joinpath("contract.json").read_text(
                encoding="utf-8"),
        })
        self.assertIn("no real Silero 6.2.3 weights", text)
        self.assertIn("MODEL-FREE STUB", text)
        self.assertIn("No target-device", text)
        self.assertIn("incomplete", text)

    def test_31_contract_is_proposal_only(self) -> None:
        contract = json.loads((fixture.TASK_DIR / "contract.json").read_text(
            encoding="utf-8"))
        self.assertEqual(contract["task"], fixture.TASK_ID)
        self.assertEqual(contract["qualification"], "incomplete")
        self.assertEqual(contract["pinned_base"], fixture.PINNED_BASE)
        self.assertEqual(contract["format"]["frame_samples"], 160)
        self.assertEqual(contract["format"]["sample_rate_hz"], 16000)
        self.assertIn("unchanged", contract["public_v0_abi"])

    def test_32_provider_is_task_local_and_opt_in(self) -> None:
        cmake = (fixture.TASK_DIR / "provider" / "CMakeLists.txt").read_text(
            encoding="utf-8")
        self.assertIn('option(AS_ENABLE_ADAPTIVE_ENERGY_TO_SILERO_CASCADE', cmake)
        self.assertIn('"Compile and register the task-local model-free cascade stub provider" OFF', cmake)
        self.assertNotIn("install(", cmake)
        self.assertNotIn("add_subdirectory(", cmake)
        source = (fixture.TASK_DIR / "provider" / "src" /
                  "cascade_provider.c").read_text(encoding="utf-8")
        self.assertIn('#include "audio_sdk/session_v0.h"', source)
        self.assertIn('#include "cascade_descriptor.h"', source)
        self.assertIn("MODEL-FREE STUB", source)

    def test_33_historical_frame_divergence_recorded(self) -> None:
        config = REPORT["fixture"]["config"]
        self.assertEqual(config["adapter_energy_frame_samples"], 320)
        self.assertEqual(config["adapter_silero_frame_samples"], 512)
        self.assertEqual(config["adapter_silero_context_samples"], 64)
        self.assertEqual(config["frame_samples"], 160)
        text = fixture.canonical(REPORT["blockers"])
        self.assertIn("100% false negatives", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
