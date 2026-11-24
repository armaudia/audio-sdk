# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local tests for the synthetic speech-probability fixture.

No skips, no network, no native library, no corpus. Every test runs with the
pinned Python 3.12.16 interpreter from this evidence directory.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference as ref  # noqa: E402 - task-local deterministic module

SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
SDK_ROOT = HERE.parents[2]


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = ref.synthetic_signal()
        cls.report = ref.build_report()

    def test_deterministic_signal_and_counts(self) -> None:
        self.assertEqual(ref.tensor_digest(self.values),
                         self.report["cohort"]["waveform_digest"])
        self.assertEqual(self.values, ref.synthetic_signal())
        self.assertEqual(len(self.values), 32000)
        self.assertEqual(ref.FRAMES, 200)
        self.assertEqual(ref.SAMPLE_RATE_HZ, 16000)
        self.assertEqual(ref.FRAME_SAMPLES, 160)

    def test_source_pins_match_actual_bytes(self) -> None:
        for pin in ref.SOURCE_PINS:
            root = SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT
            path = root / pin["path"]
            self.assertTrue(path.is_file(), f"missing pin {path}")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             pin["sha256"], pin["path"])
        self.assertEqual(
            next(pin["sha256"] for pin in ref.SOURCE_PINS
                 if pin["path"].endswith("rnnoise-side-vad/report.md")),
            "bbda960bd85e62ea096cc77e1305506ba9fc4757994a3ae8e64bfb657f3abe40")

    def test_fully_labeled_cohort_exact_partition(self) -> None:
        labels = [ref.segment_at(index)[0] for index in range(ref.SAMPLES)]
        self.assertEqual(labels.count("speech"), 14400)
        self.assertEqual(labels.count("nonspeech"), 17600)
        self.assertEqual(self.report["cohort"]["unknown_samples"], 0)
        self.assertTrue(self.report["cohort"]["fully_labeled"])
        self.assertEqual(ref.activity_transitions(),
                         (ref.EXPECTED_ONSET_FRAMES, ref.EXPECTED_OFFSET_FRAMES))

    def test_probabilities_finite_and_in_range(self) -> None:
        for method in ref.METHODS:
            values = [ref.probability(method, self.values, frame)
                      for frame in range(ref.FRAMES)]
            self.assertTrue(all(math.isfinite(value) for value in values))
            self.assertTrue(all(0.0 <= value <= 1.0 for value in values))

    def test_probability_class_ordering(self) -> None:
        levels: dict[str, list[float]] = {}
        for frame in range(ref.FRAMES):
            _, content = ref.classify_frame(frame)
            levels.setdefault(content, []).append(
                ref.rnnoise_style_probability(self.values, frame))
        self.assertEqual(set(levels), {"quiet", "active", "idle_loud", "idle_quiet"})
        self.assertGreater(sorted(levels["active"])[20], sorted(levels["quiet"])[20])
        self.assertGreater(sorted(levels["quiet"])[20],
                           sorted(levels["idle_quiet"])[20])

    def test_event_intervals_exact_contiguous_and_keyed(self) -> None:
        integrity = self.report["events"]
        self.assertEqual(integrity["event_count"], 200)
        self.assertTrue(integrity["cover_scored_union_exactly"])
        self.assertEqual(integrity["gap_count"], 0)
        self.assertEqual(integrity["overlap_count"], 0)
        self.assertTrue(integrity["keys_unique"])
        self.assertTrue(integrity["all_known_validity"])
        self.assertTrue(integrity["all_values_finite_in_range"])
        self.assertEqual(integrity["first_source_start"], "0")
        self.assertEqual(integrity["last_source_end_exclusive"], "32000")

    def test_known_decisions_cover_scored_union(self) -> None:
        session = ref.run_session(self.values)
        decisions = ref.known_decisions(session)
        self.assertEqual(len(decisions), 200)
        self.assertEqual(sum(end - start for start, _ in decisions
                             for end in [start + ref.FRAME_SAMPLES]), 32000)

    def test_pinned_confusion_for_every_condition(self) -> None:
        expected = {
            ref.METHOD_PRIMARY: (12960, 1440, 6560, 11040),
            ref.METHOD_VAD: (8800, 5600, 6560, 11040),
            ref.METHOD_SILENT: (0, 14400, 0, 17600),
            ref.METHOD_ALWAYS: (14400, 0, 17600, 0),
        }
        for method, counts in expected.items():
            confusion = self.report["quality"][method]["confusion"]
            actual = (confusion["tp_samples"], confusion["fn_samples"],
                      confusion["fp_samples"], confusion["tn_samples"])
            self.assertEqual(actual, counts, method)
            self.assertEqual(confusion["scored_samples"], 32000)
            self.assertEqual(confusion["speech_samples"], 14400)
            self.assertEqual(confusion["nonspeech_samples"], 17600)

    def test_confusion_identities_and_nonzero_rates(self) -> None:
        for method in ref.METHODS:
            confusion = self.report["quality"][method]["confusion"]
            self.assertEqual(confusion["tp_samples"] + confusion["fn_samples"], 14400)
            self.assertEqual(confusion["fp_samples"] + confusion["tn_samples"], 17600)
            self.assertIsNotNone(confusion["fn_rate"])
            self.assertIsNotNone(confusion["fp_rate"])
        primary = self.report["quality"][ref.METHOD_PRIMARY]["confusion"]
        self.assertEqual(primary["fn_rate"], round(1440 / 14400, 9))
        self.assertEqual(primary["fp_rate"], round(6560 / 17600, 9))

    def test_stratified_fn_fp_denominators_and_regressions(self) -> None:
        strata = self.report["quality"][ref.METHOD_PRIMARY]["stratified"]
        self.assertEqual(strata["fn_by_speech_class"]["quiet"]["fn_samples"], 1440)
        self.assertEqual(strata["fn_by_speech_class"]["active"]["fn_samples"], 0)
        self.assertEqual(strata["fn_by_speech_class"]["quiet"]["speech_samples"], 6400)
        self.assertEqual(strata["fn_by_speech_class"]["active"]["speech_samples"], 8000)
        self.assertEqual(strata["fp_by_nonspeech_class"]["idle_loud"]["fp_samples"], 6400)
        self.assertEqual(strata["fp_by_nonspeech_class"]["idle_quiet"]["fp_samples"], 160)
        self.assertGreater(strata["fn_by_position"]["onset"]["fn_rate"],
                           strata["fn_by_position"]["interior"]["fn_rate"])
        self.assertIsNotNone(strata["fn_by_position"]["offset"]["fn_rate"])
        self.assertGreater(strata["fp_by_boundary_proximity"]["near_speech"]["fp_rate"], 0)
        self.assertGreater(strata["fp_by_boundary_proximity"]["far_from_speech"]["fp_rate"], 0)

    def test_detection_boundaries_and_onset_offset_delays(self) -> None:
        quality = self.report["quality"][ref.METHOD_PRIMARY]
        coverage = quality["detections"]
        self.assertEqual(coverage["detected_samples"], 19520)
        self.assertTrue(coverage["detected_intervals_cover_union_exactly"])
        self.assertEqual(coverage["samples_outside_scored_union"], [])
        delays = quality["onset_offset_delay"]
        self.assertEqual(len(delays), 6)
        for item in delays.values():
            self.assertTrue(item["detected"])
            for key in ("onset_delay_samples", "offset_delay_samples",
                        "local_onset_delay_samples", "local_offset_delay_samples"):
                self.assertIsInstance(item[key], int)
            self.assertIn("negative = detected before it", item["delay_sign_convention"])
        self.assertEqual(delays["[1600,3200)"]["local_onset_delay_samples"], 160)

    def test_availability_is_source_derived_and_decimal_serialized(self) -> None:
        availability = self.report["availability"]
        session = ref.run_session(self.values)
        expected = ref.ORIGIN_NS + int(session.events[-1].window_end) * 62500
        self.assertEqual(int(availability["last_available_ns"]), expected)
        self.assertTrue(availability["monotonic_nondecreasing"])
        self.assertTrue(availability["signal_timestamp_is_not_availability"])
        self.assertGreater(ref.ORIGIN_NS, 2 ** 53)
        for event in session.events:
            as_dict = event.as_dict()
            for key in ("source_start", "source_end", "window_start",
                        "window_end", "available_ns", "epoch"):
                self.assertIsInstance(as_dict[key], str)
                self.assertRegex(as_dict[key], r"^(0|[1-9][0-9]*)$")

    def test_cross_hop_exact_overlap_counts(self) -> None:
        cross = self.report["cross_hop"]
        self.assertTrue(cross["exact_overlap_match"])
        self.assertEqual(cross["per_sdk_frame_overlap_counts"],
                         [2] + [3] * 198 + [2])
        self.assertTrue(cross["placement_by_exact_interval"])
        self.assertGreater(cross["events_crossing_an_sdk_frame_boundary"], 0)

    def test_validity_is_not_nonspeech(self) -> None:
        validity = self.report["validity"]
        self.assertTrue(validity["all_invalid_rejected"])
        self.assertTrue(validity["state_unchanged_by_invalid"])
        self.assertEqual(len(validity["probes"]), 7)
        self.assertEqual(validity["unknown_events_retained"], 1)
        self.assertEqual(validity["invalid_events_retained"], 0)
        self.assertEqual(validity["unknown_frame_truth_class"], "speech")
        self.assertEqual(validity["additional_fn_if_unknown_counted_as_nonspeech"], 160)
        self.assertEqual(validity["actual_added_fn"], 0)
        self.assertEqual(validity["invalid_nonspeech_relabeling"], "none")

    def test_invalid_inputs_rejected_without_state_change(self) -> None:
        session = ref.AnalysisSession(epoch=5)
        session.process_frame(self.values, frame=0)
        before = (session.next_frame, len(session.events), len(session.rejections))
        cases = (
            {"frame": 1, "values_epoch": 4},
            {"frame": 9999},
            {"frame": 0},
        )
        for kwargs in cases:
            with self.assertRaises(ref.Rejection):
                session.process_frame(self.values, **kwargs)
            self.assertEqual((session.next_frame, len(session.events)), before[:2])
        with self.assertRaises(ref.Rejection):
            session.process_frame([float("nan")] * 160, frame=1)
        self.assertEqual(session.next_frame, before[0])

    def test_independent_state_and_reset(self) -> None:
        state = self.report["state"]
        for key in ("sessions_uncoupled", "event_keys_disjoint",
                    "no_global_latest_event_slot", "stale_epoch_event_rejected",
                    "reset_accepted", "reset_clears_events",
                    "other_session_unchanged_by_reset",
                    "old_event_cannot_revive_after_reset",
                    "reset_bit_identical_to_fresh_epoch",
                    "closed_session_rejects_process"):
            self.assertTrue(state[key], key)

    def test_dropped_and_stale_events(self) -> None:
        dropped = self.report["drop_and_stale"]
        self.assertEqual(dropped["explicit_gap_sequence_numbers"], [3, 7])
        self.assertEqual(dropped["dropped_event_count"], 2)
        self.assertEqual(dropped["remaining_event_count"], 18)
        self.assertTrue(dropped["no_fabricated_fill"])
        self.assertTrue(dropped["foreign_epoch_event_rejected"])
        self.assertEqual(dropped["event_count_after_rejection"], 18)

    def test_controls_and_honest_regressions(self) -> None:
        comparison = self.report["comparison"]
        self.assertEqual(comparison["deltas"]["fn_rate_delta_vs_standalone_vad"],
                         round(0.1 - 5600 / 14400, 9))
        self.assertEqual(comparison["deltas"]["fp_rate_delta_vs_standalone_vad"], 0.0)
        self.assertGreaterEqual(self.report["regression_count"], 1)
        self.assertEqual(self.report["regression_count"], len(self.report["regressions"]))
        for item in self.report["regressions"]:
            self.assertGreater(item["delta"], 0)
            self.assertIn("scope", item)
            self.assertIn("metric", item)
        self.assertTrue(any(item["scope"].startswith("threshold_sweep")
                            for item in self.report["regressions"]))

    def test_threshold_sweep_uses_same_probabilities(self) -> None:
        sweep = self.report["threshold_sweep"]
        self.assertEqual(sweep["frozen_threshold"], 0.5)
        self.assertEqual(set(sweep["thresholds"]), {"0.40", "0.50", "0.60", "0.70", "0.90"})
        self.assertEqual(sweep["thresholds"]["0.50"]["confusion"]["fn_samples"], 1440)
        self.assertEqual(sweep["thresholds"]["0.90"]["confusion"]["fp_samples"], 5760)
        self.assertGreater(sweep["regression_count"], 0)

    def test_gates_status_and_no_qualification(self) -> None:
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        self.assertEqual(len(self.report["gates"]), 5)
        self.assertTrue(all(gate["status"] == "blocked" for gate in self.report["gates"]))
        self.assertTrue(all(gate["reopen"] for gate in self.report["gates"]))

    def test_timing_separated_from_quality(self) -> None:
        timing = self.report["timing"]
        self.assertTrue(timing["quality_and_timing_separate"])
        self.assertEqual(timing["qualification_status"], "blocked")
        self.assertEqual(timing["pointer_file"], "runtime-measurements.json")
        measurements = json.loads((HERE / "runtime-measurements.json").read_text())
        self.assertEqual(measurements["qualification_status"], "blocked")
        self.assertFalse(measurements["paced"])
        self.assertIsNone(measurements["deadline_ns"])
        self.assertTrue(measurements["separate_from_quality"])
        self.assertFalse(measurements["quality_metrics_in_this_file"])
        self.assertFalse(measurements["standalone_vad_cost_pooled"])

    def test_adapter_is_optional_unregistered_and_off(self) -> None:
        adapter = self.report["adapter"]
        self.assertFalse(adapter["registered"])
        self.assertFalse(adapter["enabled_by_default"])
        self.assertEqual(adapter["descriptor_settings"], {})
        self.assertFalse(adapter["public_adapter_probability_output"])
        local = json.loads((HERE / "adapter.json").read_text())
        self.assertFalse(local["registered"])
        self.assertFalse(local["enabled_by_default"])
        self.assertEqual(local["descriptor_settings"], {})
        self.assertFalse(local["public_api_abi_change"])
        self.assertEqual(local["native_hop_samples"], 160)

    def test_report_shape_strict_json_and_regeneration(self) -> None:
        raw = (HERE / "report.json").read_bytes()
        report = json.loads(raw, parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(value)))
        self.assertIsInstance(report, dict)
        self.assertEqual(report["profile"], "Analysis")
        self.assertEqual(report["base_commit"], ref.BASE_COMMIT)
        self.assertEqual(report["schema_id"] if "schema_id" in report
                         else ref.SCHEMA_ID, ref.SCHEMA_ID)
        for key in ("adapter", "analysis_boundary", "availability", "cohort",
                    "comparison", "config_digest", "cross_hop", "drop_and_stale",
                    "events", "gates", "profile", "quality", "regressions",
                    "source_context", "state", "status", "timing", "validity"):
            self.assertIn(key, report, key)
        self.assertEqual(ref.canonical_report_bytes(report), raw)
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text().split()[0], digest)

    def test_artifact_pins_and_spdx_headers(self) -> None:
        pins = ref.artifact_pins()
        for pin in pins:
            path = HERE / pin["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             pin["sha256"], pin["path"])
        for path in sorted(HERE.glob("*.py")):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
            self.assertIn("SPDX-License-Identifier: Apache-2.0", head, path.name)
            self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          head, path.name)

    def test_source_context_is_context_only(self) -> None:
        context = self.report["source_context"]
        self.assertEqual(context["source_numbers_status"],
                         "context_only_not_reproduced_or_pooled")
        self.assertEqual(context["source_reported_rnnoise_fn_percent"], 25.64)
        self.assertEqual(context["source_reported_rnnoise_fp_percent"], 5.44)
        self.assertEqual(context["source_reported_silero_fn_percent"], 22.91)
        self.assertEqual(context["source_reported_silero_fp_percent"], 7.64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
