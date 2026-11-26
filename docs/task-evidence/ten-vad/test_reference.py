# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local TEN VAD evidence package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import unittest

import reference


class JsonTests(unittest.TestCase):
    def test_canonical_json_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"value": math.nan})

    def test_strict_json_rejects_duplicate_key(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_nan_constant(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":NaN}')

    def test_strict_json_rejects_non_object(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads("[1,2]")


class IdentityTests(unittest.TestCase):
    def test_identity_is_linked_row_only(self) -> None:
        identity = reference.task_row_identity()
        self.assertIs(identity["whole_file_hashed"], False)
        self.assertEqual(identity["source"],
                         "audio-benchmark-platform/plan/swarm/TASKS.json")
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(
            identity["stable_sha256"],
            reference.sha256(reference.canonical_bytes(identity["stable_fields"])))

    def test_identity_matches_contract(self) -> None:
        identity = reference.task_row_identity()
        contract = json.loads((reference.HERE / "contract.json").read_text())
        self.assertEqual(contract["task_row_identity"]["stable_sha256"],
                         identity["stable_sha256"])
        self.assertIs(contract["task_row_identity"]["whole_file_hashed"], False)

    def test_mutable_fields_are_excluded(self) -> None:
        identity = reference.task_row_identity()
        for field in ("owner", "status", "review", "handoff"):
            self.assertNotIn(field, identity["stable_fields"])
            self.assertIn(field, identity["excluded_mutable_fields"])

    def test_no_tasks_json_pin(self) -> None:
        report = reference.build_report()
        labels = set(report["source_pins"]) | set(report["boundary_pins"])
        self.assertFalse(any(label.endswith("TASKS.json") for label in labels))


class FramingTests(unittest.TestCase):
    def test_frame_count_and_partial_tail(self) -> None:
        plan = reference.frame_plan(reference.synthetic_signal())
        self.assertEqual(plan["total_samples"], reference.TOTAL_SAMPLES)
        self.assertEqual(plan["frame_count"], reference.TOTAL_MODEL_FRAMES)
        self.assertEqual(plan["frame_count"], 25)
        self.assertEqual(plan["partial_frame_samples"],
                         reference.TAIL_PARTIAL_SAMPLES)
        self.assertEqual(plan["padded_samples"],
                         reference.MODEL_FRAME_SAMPLES - reference.TAIL_PARTIAL_SAMPLES)

    def test_frame_context_carry_is_exact(self) -> None:
        plan = reference.frame_plan(reference.synthetic_signal())
        self.assertTrue(plan["context_carry_exact"])
        self.assertEqual(plan["frames"][0]["model_input_samples"], 576)
        self.assertEqual(plan["frames"][0]["source_start"], 0)
        self.assertEqual(plan["frames"][0]["source_end"], 512)
        self.assertEqual(plan["frames"][-1]["source_end"],
                         reference.TOTAL_SAMPLES)

    def test_signal_nonfinite_rejected(self) -> None:
        signal = [0.0] * reference.MODEL_FRAME_SAMPLES + [math.inf]
        with self.assertRaises(reference.Reject):
            reference.frame_plan(signal)

    def test_signal_out_of_range_rejected(self) -> None:
        signal = [0.0] * reference.TOTAL_SAMPLES
        signal[0] = 2.0
        with self.assertRaises(reference.Reject):
            reference.frame_plan(signal)


class ProbabilityTests(unittest.TestCase):
    def test_count_mismatch_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.map_probabilities([0.1] * 24, reference.TOTAL_SAMPLES)

    def test_nan_rejected(self) -> None:
        values = [0.0] * reference.TOTAL_MODEL_FRAMES
        values[1] = math.nan
        with self.assertRaises(reference.Reject):
            reference.map_probabilities(values, reference.TOTAL_SAMPLES)

    def test_infinity_rejected(self) -> None:
        values = [0.0] * reference.TOTAL_MODEL_FRAMES
        values[1] = math.inf
        with self.assertRaises(reference.Reject):
            reference.map_probabilities(values, reference.TOTAL_SAMPLES)

    def test_out_of_range_rejected(self) -> None:
        values = [0.0] * reference.TOTAL_MODEL_FRAMES
        values[1] = 1.2
        with self.assertRaises(reference.Reject):
            reference.map_probabilities(values, reference.TOTAL_SAMPLES)

    def test_boolean_rejected(self) -> None:
        values = [0.0] * reference.TOTAL_MODEL_FRAMES
        values[1] = True
        with self.assertRaises(reference.Reject):
            reference.map_probabilities(values, reference.TOTAL_SAMPLES)

    def test_string_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.map_probabilities(["0.5"] * reference.TOTAL_MODEL_FRAMES,
                                        reference.TOTAL_SAMPLES)

    def test_unknown_allowed_and_excluded(self) -> None:
        mapped = reference.map_probabilities(
            [0.0] * (reference.TOTAL_MODEL_FRAMES - 1) + [None],
            reference.TOTAL_SAMPLES)
        self.assertIsNone(mapped["probability_events"][-1]["label"])
        self.assertEqual(mapped["counts"]["unknown_frames"], 1)

    def test_exact_probability_intervals(self) -> None:
        mapped = reference.map_probabilities(reference.CONTROL_TRACE,
                                             reference.TOTAL_SAMPLES)
        self.assertEqual(mapped["probability_events"][0]["start_sample"], 0)
        self.assertEqual(mapped["probability_events"][0]["end_sample"], 512)
        self.assertEqual(mapped["probability_events"][-1]["start_sample"], 24 * 512)
        self.assertEqual(mapped["probability_events"][-1]["end_sample"],
                         reference.TOTAL_SAMPLES)

    def test_speech_events_are_exact(self) -> None:
        mapped = reference.map_probabilities(reference.CONTROL_TRACE,
                                             reference.TOTAL_SAMPLES)
        self.assertEqual(mapped["speech_events"], [
            {"start_sample": 512, "end_sample": 1024},
            {"start_sample": 2048, "end_sample": 7168},
        ])

    def test_unknown_interval_is_exact(self) -> None:
        mapped = reference.map_probabilities(reference.CONTROL_TRACE,
                                             reference.TOTAL_SAMPLES)
        self.assertEqual(mapped["unknown_intervals"], [
            {"start_sample": 12288, "end_sample": 12325},
        ])


class ScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        labels, conditions = reference.control_labels()
        mapped = reference.map_probabilities(reference.CONTROL_TRACE,
                                             reference.TOTAL_SAMPLES)
        decisions = [event["label"] for event in mapped["probability_events"]]
        self.decisions = decisions
        self.score = reference.score_frames(decisions, labels, conditions)

    def test_confusion_counts(self) -> None:
        self.assertEqual(self.score["tp"], 10)
        self.assertEqual(self.score["fn"], 7)
        self.assertEqual(self.score["fp"], 1)
        self.assertEqual(self.score["tn"], 6)
        self.assertEqual(self.score["unknown"], 1)
        self.assertEqual(self.score["miss_rate_fraction"], "7/17")
        self.assertEqual(self.score["false_alarm_rate_fraction"], "1/7")

    def test_stratified_counts(self) -> None:
        strata = self.score["stratified"]
        self.assertEqual(strata["idle_noise"],
                         {"tp": 0, "fn": 0, "fp": 1, "tn": 6, "unknown": 0})
        self.assertEqual(strata["quiet_speech"],
                         {"tp": 5, "fn": 1, "fp": 0, "tn": 0, "unknown": 0})
        self.assertEqual(strata["active_speech"],
                         {"tp": 5, "fn": 1, "fp": 0, "tn": 0, "unknown": 0})
        self.assertEqual(strata["stress_low_snr"],
                         {"tp": 0, "fn": 5, "fp": 0, "tn": 0, "unknown": 0})
        self.assertEqual(strata["unknown_tail"],
                         {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "unknown": 1})

    def test_known_label_with_unknown_decision_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.score_frames([None], [True], ["quiet_speech"])

    def test_invalid_label_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.score_frames([True], ["speech"], ["idle_noise"])

    def test_onset_offset_values(self) -> None:
        result = reference.onset_offset(
            self.decisions,
            [segment for segment in reference.CONTROL_SEGMENTS
             if segment["label"] is True])
        by_id = {item["id"]: item for item in result}
        self.assertEqual(by_id["quiet-a"]["onset_delay_samples"], 512)
        self.assertEqual(by_id["quiet-a"]["offset_delay_samples"], 0)
        self.assertEqual(by_id["active-a"]["onset_delay_samples"], 0)
        self.assertEqual(by_id["active-a"]["offset_delay_samples"], -512)
        self.assertIsNone(by_id["stress-a"]["onset_delay_samples"])
        self.assertIsNone(by_id["stress-a"]["offset_delay_samples"])
        self.assertTrue(by_id["stress-a"]["missed_frames"])


class ControlTests(unittest.TestCase):
    def test_trace_length_matches_frames(self) -> None:
        self.assertEqual(len(reference.CONTROL_TRACE),
                         reference.TOTAL_MODEL_FRAMES)

    def test_validity_separation(self) -> None:
        control = reference.build_control()
        validity = control["validity_separation"]
        self.assertTrue(validity["known_zero"]["counted_as_nonspeech"])
        self.assertFalse(validity["unknown"]["counted_as_nonspeech"])
        self.assertTrue(validity["unknown"]["excluded_from_scoring"])
        self.assertTrue(validity["invalid_rejected"])

    def test_adverse_all_rejected(self) -> None:
        adverse = reference.run_adverse_controls()
        self.assertEqual(len(adverse), 18)
        self.assertTrue(all(item["result"] == "rejected" for item in adverse))

    def test_cross_hop(self) -> None:
        hop = reference.cross_hop(reference.TOTAL_SAMPLES)
        self.assertEqual(hop["sdk_hop_samples"], 160)
        self.assertEqual(hop["model_hop_samples"], 512)
        self.assertEqual(hop["model_frames"], 25)
        self.assertEqual(hop["sdk_partial_samples"],
                         reference.TOTAL_SAMPLES % 160)
        self.assertEqual(hop["timing_claim"], "none")

    def test_control_never_claims_model_execution(self) -> None:
        control = reference.build_control()
        self.assertFalse(control["model_executed"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")


class CallerAssetTests(unittest.TestCase):
    def _manifest(self, root: Path) -> dict:
        model = root / "model.bin"
        model.write_bytes(b"model")
        lock = root / "requirements.lock"
        lock.write_bytes(b"lock")
        rights = root / "LICENSE"
        rights.write_bytes(b"rights")
        return {
            "context_samples": 64,
            "frame_samples": 512,
            "model_path": str(model),
            "model_sha256": reference.sha256(model.read_bytes()),
            "rights_record_path": str(rights),
            "rights_record_sha256": reference.sha256(rights.read_bytes()),
            "runtime_lock_path": str(lock),
            "runtime_lock_sha256": reference.sha256(lock.read_bytes()),
            "runtime_version": "test-runtime-1.0.0",
            "sample_rate_hz": 16000,
            "source_revision": "a" * 40,
            "state_shape": [2, 1, 128],
        }

    def test_complete_manifest_validates_without_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            result = reference.validate_caller_manifest(manifest)
            self.assertTrue(result["accepted"])
            self.assertFalse(result["executed"])
            self.assertFalse(result["loaded"])
            self.assertFalse(result["network_used"])

    def test_missing_field_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.validate_caller_manifest({})

    def test_relative_path_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            manifest["model_path"] = "model.bin"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_wrong_geometry_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            manifest["sample_rate_hz"] = 8000
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_short_revision_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            manifest["source_revision"] = "deadbee"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_extra_field_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            manifest["extra"] = True
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)


class ReportTests(unittest.TestCase):
    def test_report_invariants(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["profile"], "analysis")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertIs(report["qualification"]["candidate_qualified"], False)
        self.assertIs(report["qualification"]
                      ["no_missing_result_qualifies_candidate"], True)
        self.assertIsNone(report["candidate_metrics"])
        self.assertEqual(len(report["gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in report["gates"]))
        self.assertEqual(len({gate["id"] for gate in report["gates"]}), 8)
        self.assertEqual(len(report["exact_blockers"]), 8)
        self.assertEqual(report["analysis_profile"]
                         ["satisfied_for_qualification"], [])
        self.assertFalse(report["asset_audit"]["qualified"])
        self.assertFalse(report["reference_protocol"]["model_executed"])
        self.assertTrue(report["controls"]["adverse_all_rejected"])
        self.assertIs(report["boundary"]["registered"], False)
        self.assertIs(report["boundary"]["enabled_by_default"], False)
        self.assertEqual(report["boundary"]["descriptor_settings"], {})
        self.assertIs(report["scope"]["real_ten_vad_model"], False)
        self.assertIs(report["scope"]["network_used"], False)
        self.assertIs(report["task_row_identity"]["whole_file_hashed"], False)
        self.assertEqual(report["source_reported_context"]["label"],
                         "source_reported_not_measured_here")

    def test_report_is_byte_stable(self) -> None:
        first = reference.canonical_report_bytes(reference.build_report())
        second = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))

    def test_no_tasks_json_digest_in_report(self) -> None:
        payload = reference.canonical_report_bytes(reference.build_report())
        text = payload.decode("utf-8")
        self.assertNotIn('"plan/swarm/TASKS.json":', text)
        self.assertNotIn('TASKS.json": "', text)


if __name__ == "__main__":
    unittest.main()
