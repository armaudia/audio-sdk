# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local SDK-CNN-BILSTM-VAD evidence package."""

from __future__ import annotations

import copy
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

    def test_canonical_bytes_are_sorted_and_compact(self) -> None:
        self.assertEqual(
            reference.canonical_text({"b": 1, "a": 2}), '{"a":2,"b":1}')

    def test_negative_zero_is_normalized(self) -> None:
        self.assertEqual(reference.canonical_text({"v": -0.0}), '{"v":0.0}')


class IdentityTests(unittest.TestCase):
    def test_identity_is_linked_row_only(self) -> None:
        identity = reference.task_row_identity()
        self.assertIs(identity["whole_file_hashed"], False)
        self.assertEqual(identity["source"],
                         "audio-benchmark-platform/plan/swarm/TASKS.json")
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "feasibility")
        self.assertEqual(
            identity["stable_sha256"],
            reference.sha256(reference.canonical_bytes(identity["stable_fields"])))

    def test_mutable_fields_are_excluded(self) -> None:
        identity = reference.task_row_identity()
        for field in ("owner", "status", "review", "handoff", "dispatch_priority"):
            self.assertNotIn(field, identity["stable_fields"])
            self.assertIn(field, identity["excluded_mutable_fields"])

    def test_no_tasks_json_pin(self) -> None:
        labels = set(reference.SOURCE_PINS) | set(reference.BOUNDARY_PINS)
        self.assertFalse(any(label.endswith("TASKS.json") for label in labels))

    def test_claim_pins_match_contract(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["claim"]["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(identity["claim"]["branch"], reference.BRANCH)
        self.assertEqual(identity["claim"]["reviewer"], reference.REVIEWER)


class AuditTests(unittest.TestCase):
    def test_audit_is_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertIs(audit["any_present"], False)
        self.assertIs(audit["implementation_present"], False)
        self.assertIs(audit["weights_present"], False)
        self.assertIs(audit["runtime_present"], False)
        self.assertIs(audit["cohort_present"], False)
        self.assertIs(audit["rights_present"], False)

    def test_audit_is_deterministic(self) -> None:
        self.assertEqual(reference.audit_assets(), reference.audit_assets())

    def test_audit_paths_are_fixed_workspace_relative(self) -> None:
        for name, path in reference.AUDIT_PATHS:
            self.assertTrue(name)
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("..", Path(path).parts)


class SurrogateTests(unittest.TestCase):
    def test_trace_is_deterministic(self) -> None:
        first = reference.surrogate_trace()
        second = reference.surrogate_trace()
        self.assertEqual(first, second)
        self.assertEqual(len(first), reference.SURROGATE_TOTAL_FRAMES)
        self.assertTrue(all(0 <= value <= 1000 for value in first))

    def test_notch_level_is_present(self) -> None:
        levels = reference.surrogate_trace()
        self.assertEqual(levels[reference.NOTCH_START_FRAME],
                         reference.NOTCH_LEVEL)
        self.assertEqual(levels[reference.NOTCH_END_FRAME - 1],
                         reference.NOTCH_LEVEL)

    def test_labels_cover_every_frame(self) -> None:
        labels, conditions = reference.surrogate_labels()
        self.assertEqual(len(labels), reference.SURROGATE_TOTAL_FRAMES)
        self.assertEqual(len(conditions), reference.SURROGATE_TOTAL_FRAMES)
        self.assertEqual(sum(1 for label in labels if label is None), 60)

    def test_causal_is_zero_lookahead(self) -> None:
        levels = reference.surrogate_trace()
        decisions = reference.causal_decisions(levels)
        self.assertEqual(len(decisions), len(levels))
        self.assertTrue(all(isinstance(item, bool) for item in decisions))

    def test_offline_has_declared_lookahead(self) -> None:
        self.assertEqual(reference.OFFLINE_HALF_WINDOW_FRAMES, 5)
        self.assertEqual(reference.OFFLINE_WINDOW_FRAMES, 11)

    def test_offline_bridges_notch_and_causal_splits(self) -> None:
        levels = reference.surrogate_trace()
        causal = reference.causal_decisions(levels)
        offline = reference.offline_decisions(levels)
        notch = range(reference.NOTCH_START_FRAME, reference.NOTCH_END_FRAME)
        self.assertTrue(any(causal[index] is False for index in notch))
        self.assertTrue(all(offline[index] is True for index in notch))

    def test_causal_and_offline_differ(self) -> None:
        levels = reference.surrogate_trace()
        self.assertNotEqual(reference.causal_decisions(levels),
                            reference.offline_decisions(levels))

    def test_bad_levels_rejected(self) -> None:
        for payload in ([0] * 799, [0] * 799 + [math.nan],
                        [0] * 799 + [1001], [True] * 800, "levels"):
            with self.assertRaises(reference.Reject):
                reference.causal_decisions(payload)
            with self.assertRaises(reference.Reject):
                reference.offline_decisions(payload)


class ScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.labels = [True, True, False, False, None]
        self.conditions = ["speech", "speech", "idle", "idle", "unknown"]

    def test_exact_counts_and_rates(self) -> None:
        metrics = reference.score_frames(
            [True, False, True, False, True], self.labels, self.conditions)
        self.assertEqual(metrics["counts_frames"],
                         {"tp": 1, "fn": 1, "fp": 1, "tn": 1, "unknown": 1})
        self.assertEqual(metrics["miss_rate_fraction"], "1/2")
        self.assertEqual(metrics["false_alarm_rate_fraction"], "1/2")
        self.assertEqual(metrics["counts_samples"]["tp"], 160)

    def test_unknown_is_never_nonspeech(self) -> None:
        metrics = reference.score_frames(
            [False] * 5, self.labels, self.conditions)
        self.assertEqual(metrics["counts_frames"]["unknown"], 1)
        self.assertEqual(metrics["counts_frames"]["tn"], 2)
        self.assertEqual(metrics["counts_frames"]["fn"], 2)

    def test_stratified_counts(self) -> None:
        metrics = reference.score_frames(
            [True, False, True, False, True], self.labels, self.conditions)
        self.assertEqual(metrics["stratified"]["speech"]["tp"], 1)
        self.assertEqual(metrics["stratified"]["speech"]["fn"], 1)
        self.assertEqual(metrics["stratified"]["idle"]["fp"], 1)
        self.assertEqual(metrics["stratified"]["unknown"]["unknown"], 1)

    def test_invalid_decisions_rejected(self) -> None:
        for decision in (1, 0, "True", None):
            with self.assertRaises(reference.Reject):
                reference.score_frames(
                    [decision] * 5, self.labels, self.conditions)

    def test_invalid_labels_rejected(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.score_frames(
                [True] * 5, [1] * 5, self.conditions)

    def test_zero_denominators_are_zero_fractions(self) -> None:
        metrics = reference.score_frames(
            [True, True], [True, True], ["speech", "speech"])
        self.assertEqual(metrics["false_alarm_rate_fraction"], "0")

    def test_always_speech_and_nonspeech_controls(self) -> None:
        control = reference.build_surrogate_control()
        always_speech = control["controls"]["always_speech"]["counts_frames"]
        always_nonspeech = control["controls"]["always_nonspeech"]["counts_frames"]
        self.assertEqual(always_speech["fn"], 0)
        self.assertEqual(always_speech["fp"], 260)
        self.assertEqual(always_nonspeech["tp"], 0)
        self.assertEqual(always_nonspeech["fn"], 480)


class BoundaryTests(unittest.TestCase):
    def test_pairing_is_one_to_one_max_overlap(self) -> None:
        truth = [{"start_frame": 10, "end_frame": 20}]
        hypothesis = [{"start_frame": 12, "end_frame": 18},
                      {"start_frame": 19, "end_frame": 25}]
        paired = reference._pair_events(truth, hypothesis)
        self.assertEqual(paired["unmatched_truth_runs"], 0)
        self.assertEqual(paired["unmatched_hypothesis_runs"], 1)
        self.assertEqual(paired["matched"][0]["onset_error_samples"], 320)
        self.assertEqual(paired["matched"][0]["offset_error_samples"], -320)

    def test_control_boundary_separates_paths(self) -> None:
        control = reference.build_surrogate_control()
        causal = control["paths"]["framewise_causal"]["boundary"]
        offline = control["paths"]["bidirectional_offline"]["boundary"]
        self.assertEqual(causal["unmatched_truth_runs"], 0)
        self.assertGreaterEqual(causal["unmatched_hypothesis_runs"], 1)
        self.assertEqual(offline["unmatched_truth_runs"], 0)
        self.assertEqual(offline["unmatched_hypothesis_runs"], 0)
        self.assertEqual(offline["onset_median_samples"], 0)

    def test_p90_absolute_value(self) -> None:
        self.assertEqual(reference._p90_abs([0, 10, -20]), 20)
        self.assertIsNone(reference._p90_abs([]))


class ControlTests(unittest.TestCase):
    def test_control_is_non_qualifying(self) -> None:
        control = reference.build_surrogate_control()
        self.assertIs(control["surrogate"], True)
        self.assertIs(control["model_executed"], False)
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(control["label"],
                         "synthetic_two_path_control_not_cnn_bilstm")
        self.assertIs(control["paths"]["bidirectional_offline"]["bidirectional"],
                      True)
        self.assertIs(
            control["paths"]["framewise_causal"]["bidirectional"], False)

    def test_availability_is_separated(self) -> None:
        availability = reference.build_surrogate_control()["availability"]
        self.assertIs(availability["separation_declared"], True)
        self.assertIs(availability["framewise_available"], True)
        self.assertIs(availability["offline_available"], False)
        self.assertIs(availability["offline_streaming_claim"], False)
        self.assertEqual(availability["causal_lookahead_samples"], 0)
        self.assertEqual(availability["offline_lookahead_samples"], 800)
        self.assertEqual(availability["offline_lookahead_ns"], 50_000_000)

    def test_offline_metrics_do_not_improve_qualification(self) -> None:
        control = reference.build_surrogate_control()
        for path in control["paths"].values():
            self.assertEqual(path["qualification_effect"], "none")


class AdmissionTests(unittest.TestCase):
    def test_positive_schema_control_is_accepted_but_not_qualified(self) -> None:
        summary = reference.run_admission_controls()["positive_control"]
        self.assertIs(summary["accepted"], True)
        self.assertIs(summary["qualifies"], False)
        self.assertIs(summary["executed"], False)
        self.assertIs(summary["upstream_identity_verified"], False)
        self.assertEqual(summary["label"],
                         "synthetic_schema_control_not_evidence")

    def test_adverse_controls_all_rejected(self) -> None:
        result = reference.run_admission_controls()
        self.assertEqual(result["adverse_count"], 51)
        self.assertIs(result["adverse_all_rejected"], True)
        self.assertTrue(all(item["result"] == "rejected"
                            for item in result["adverse"]))
        self.assertEqual(len({item["case"] for item in result["adverse"]}),
                         result["adverse_count"])

    def test_bidirectional_requires_lookahead(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = reference._synthetic_admission_tree(Path(raw))
            broken = copy.deepcopy(base)
            broken["lookahead_frames"] = 0
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(broken)

    def test_framewise_requires_zero_lookahead(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = reference._synthetic_admission_tree(Path(raw))
            broken = copy.deepcopy(base)
            broken["bidirectional"] = False
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(broken)

    def test_framewise_manifest_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = reference._synthetic_admission_tree(Path(raw))
            framewise = copy.deepcopy(base)
            framewise["bidirectional"] = False
            framewise["lookahead_frames"] = 0
            framewise["offline_context_frames"] = 0
            result = reference.validate_caller_manifest(framewise)
            self.assertIs(result["accepted"], True)
            self.assertIs(result["qualifies"], False)
            self.assertIs(result["separation"]["framewise_available"], True)
            self.assertIs(result["separation"]["streaming_claim_allowed"], True)

    def test_manifest_claims_qualified_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = reference._synthetic_admission_tree(Path(raw))
            broken = copy.deepcopy(base)
            broken["claims_qualified"] = True
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(broken)

    def test_manifest_wrong_hash_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = reference._synthetic_admission_tree(Path(raw))
            broken = copy.deepcopy(base)
            broken["weights_sha256"] = "0" * 64
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(broken)


class ReportTests(unittest.TestCase):
    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_report(reference.build_report())
        second = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)

    def test_report_and_contract_are_non_qualifying(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIs(report["qualification"]["candidate_qualified"], False)
        self.assertEqual(report["qualification"]["blocked_gate_count"], 8)
        self.assertEqual(len(report["qualification"]["blocked_gate_ids"]), 8)
        self.assertIsNone(report["candidate_metrics"])
        self.assertEqual(report["analysis_profile"]["satisfied_for_qualification"],
                         [])

    def test_all_gates_blocked(self) -> None:
        report = reference.build_report()
        self.assertEqual([gate["id"] for gate in report["gates"]],
                         [f"RG-0{index}" for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["gates"]))
        self.assertEqual(len(report["exact_blockers"]), 8)

    def test_committed_report_matches_build(self) -> None:
        text, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(
            (reference.HERE / "report.json").read_text(encoding="utf-8"), text)
        self.assertEqual(
            (reference.HERE / "report.json.sha256").read_text(encoding="utf-8"),
            digest + "\n")

    def test_committed_contract_matches_build(self) -> None:
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        self.assertEqual(
            (reference.HERE / "contract.json").read_text(encoding="utf-8"),
            reference.canonical_text(contract) + "\n")

    def test_contract_identity_and_pins(self) -> None:
        report = reference.build_report()
        _, digest = reference.canonical_report(report)
        contract = reference.build_contract(report, digest)
        self.assertEqual(contract["task_row_identity"],
                         report["task_row_identity"])
        self.assertEqual(contract["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(contract["boundary_pins"], reference.BOUNDARY_PINS)
        self.assertEqual(contract["reproduction"]["cold_start_regenerations"], 3)
        self.assertEqual(contract["qualification"]["status"],
                         "not_qualified")


if __name__ == "__main__":
    unittest.main()
