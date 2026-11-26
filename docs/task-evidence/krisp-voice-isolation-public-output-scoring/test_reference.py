# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance tests for the Krisp public-output scoring package.

Standard library only, no network, no skipped cases and no real audio, weight,
checkpoint, runtime, corpus or score.  Every failure is an explicit rejection;
nothing here qualifies the component.
"""

from __future__ import annotations

import hashlib
import json
import math
import unittest

import reference


class StrictJsonTests(unittest.TestCase):
    def test_valid_document_accepted(self) -> None:
        self.assertEqual(reference.parse_strict_json_text('{"a":1}'), {"a": 1})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate_json_key:a"):
            reference.parse_strict_json_text('{"a":1,"a":2}')

    def test_nan_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non_json_constant:NaN"):
            reference.parse_strict_json_text('{"a":NaN}')

    def test_infinity_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non_json_constant:Infinity"):
            reference.parse_strict_json_text('{"a":Infinity}')

    def test_top_level_list_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "top_level_document_must_be_object"):
            reference.parse_strict_json_text("[1,2]")

    def test_empty_document_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "empty_document"):
            reference.parse_strict_json_text("   ")

    def test_bom_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "utf8_bom_rejected"):
            reference.parse_strict_json_text("\ufeff{}")

    def test_malformed_maps_to_invalid_json(self) -> None:
        self.assertEqual(reference.strict_error_code('{"a":'), "invalid_json")

    def test_canonical_bytes_are_sorted_and_compact(self) -> None:
        self.assertEqual(
            reference.canonical_bytes({"b": 1, "a": 2}), b'{"a":2,"b":1}'
        )

    def test_canonical_bytes_reject_nan(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"a": float("nan")})


class SegmentTests(unittest.TestCase):
    def test_below_one_second_dropped(self) -> None:
        plan = reference.dnsmos_c_segment_plan(999, "primary")
        self.assertTrue(plan["dropped"])
        self.assertEqual(plan["window_count"], 0)

    def test_exact_one_second_repeated_ten_times(self) -> None:
        plan = reference.dnsmos_c_segment_plan(1000, "mix")
        self.assertTrue(plan["repeated"])
        self.assertEqual(plan["repeat_count"], 10)

    def test_four_seconds_tiled(self) -> None:
        plan = reference.dnsmos_c_segment_plan(4000, "primary")
        self.assertEqual(plan["repeat_count"], 3)
        self.assertEqual(plan["tiling_truncated_ms"], 2000)

    def test_ten_seconds_single_window(self) -> None:
        plan = reference.dnsmos_c_segment_plan(10000, "mix")
        self.assertEqual(plan["window_count"], 1)
        self.assertFalse(plan["end_aligned_tail"])

    def test_twelve_seconds_has_tail(self) -> None:
        plan = reference.dnsmos_c_segment_plan(12345, "primary")
        self.assertEqual(plan["window_count"], 2)
        self.assertTrue(plan["end_aligned_tail"])
        self.assertEqual(plan["windows"][-1]["start_ms"], 2345)

    def test_twenty_seconds_three_windows(self) -> None:
        plan = reference.dnsmos_c_segment_plan(20000, "primary")
        self.assertEqual(plan["window_count"], 3)
        self.assertFalse(plan["end_aligned_tail"])

    def test_unknown_kind_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported_segment_kind"):
            reference.dnsmos_c_segment_plan(10000, "studio")

    def test_nonpositive_duration_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires_positive_ms"):
            reference.dnsmos_c_segment_plan(0, "primary")

    def test_duration_bound_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duration_exceeds_bound"):
            reference.dnsmos_c_segment_plan(
                reference.DNSC_MAX_DURATION_MS + 1, "primary")

    def test_plan_aggregates_windows(self) -> None:
        plan = reference.dnsmos_c_plan([
            {"kind": "primary", "duration_ms": 999},
            {"kind": "mix", "duration_ms": 10000},
        ])
        self.assertEqual(plan["dropped_segment_count"], 1)
        self.assertEqual(plan["scored_segment_count"], 1)
        self.assertEqual(plan["window_count"], 1)


class AggregationTests(unittest.TestCase):
    def test_equal_weight_average(self) -> None:
        self.assertEqual(
            reference.equal_weight_average(
                {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0}),
            3.5,
        )

    def test_equal_weight_is_order_invariant(self) -> None:
        first = reference.equal_weight_average(
            {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0})
        second = reference.equal_weight_average(
            {"phone_calls": 4.0, "work": 3.0, "call_center": 3.5})
        self.assertEqual(first, second)

    def test_bool_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_number"):
            reference.equal_weight_average(
                {"work": True, "call_center": 3.5, "phone_calls": 4.0})

    def test_nan_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_number"):
            reference.equal_weight_average(
                {"work": float("nan"), "call_center": 3.5, "phone_calls": 4.0})

    def test_missing_scenario_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly_three_declared"):
            reference.equal_weight_average({"work": 3.0, "call_center": 3.5})

    def test_extra_scenario_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly_three_declared"):
            reference.equal_weight_average(
                {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0,
                 "studio": 2.0})

    def test_out_of_scale_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_number"):
            reference.equal_weight_average(
                {"work": 3.0, "call_center": 3.5, "phone_calls": 9.0})


class MetricTests(unittest.TestCase):
    def test_valid_metric_accepted_as_prediction(self) -> None:
        result = reference.validate_metric_value(3.815)
        self.assertTrue(result["is_prediction"])
        self.assertFalse(result["is_human_rating"])
        self.assertFalse(result["qualifies"])

    def test_bool_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_number"):
            reference.validate_metric_value(True)

    def test_text_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_number"):
            reference.validate_metric_value("3.5")

    def test_nan_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_number"):
            reference.validate_metric_value(float("nan"))

    def test_below_scale_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_number"):
            reference.validate_metric_value(0.99)

    def test_above_scale_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_number"):
            reference.validate_metric_value(5.01)


class CohortTests(unittest.TestCase):
    def test_valid_manifest_metadata_only(self) -> None:
        result = reference.validate_cohort_manifest(reference._cohort_template())
        self.assertTrue(result["accepted_metadata"])
        self.assertFalse(result["admitted_for_scoring"])
        self.assertFalse(result["qualifies"])

    def test_unknown_license_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cc_by_nc_4_0"):
            reference.validate_cohort_manifest(
                reference._cohort_with(license="NOASSERTION"))

    def test_rights_not_cleared_rejected(self) -> None:
        value = reference._cohort_template()
        value["items"][3] = dict(value["items"][3], rights_cleared=False)
        with self.assertRaisesRegex(ValueError, "rights_not_cleared"):
            reference.validate_cohort_manifest(value)

    def test_item_sum_mismatch_rejected(self) -> None:
        value = reference._cohort_template()
        value["items"][7] = dict(value["items"][7], bytes=1)
        with self.assertRaisesRegex(ValueError, "do_not_sum_to_total"):
            reference.validate_cohort_manifest(value)

    def test_duplicate_id_rejected(self) -> None:
        value = reference._cohort_template()
        value["items"][9] = dict(value["items"][9],
                                 id=value["items"][8]["id"])
        with self.assertRaisesRegex(ValueError, "duplicate_item_id"):
            reference.validate_cohort_manifest(value)

    def test_wrong_revision_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "40_hex"):
            reference.validate_cohort_manifest(
                reference._cohort_with(processed_revision="A" * 40))

    def test_wrong_item_count_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must_be_265"):
            reference.validate_cohort_manifest(
                reference._cohort_with(item_count=264))


class ScorerTests(unittest.TestCase):
    def test_valid_manifest_not_admitted_for_execution(self) -> None:
        result = reference.validate_scorer_manifest(reference._scorer_template())
        self.assertTrue(result["accepted_metadata"])
        self.assertFalse(result["admitted_for_execution"])
        self.assertFalse(result["qualifies"])

    def test_unknown_metric_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown_metric"):
            reference.validate_scorer_manifest(
                reference._scorer_with(metric="dnsmos_p835"))

    def test_bad_checkpoint_digest_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "checkpoint_sha256"):
            reference.validate_scorer_manifest(reference._scorer_with(
                checkpoint=dict(reference._scorer_template()["checkpoint"],
                                sha256="AB")))

    def test_wrong_checkpoint_name_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "model_best_pt"):
            reference.validate_scorer_manifest(reference._scorer_with(
                checkpoint=dict(reference._scorer_template()["checkpoint"],
                                name="sig.onnx")))

    def test_unknown_license_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "identified_terms"):
            reference.validate_scorer_manifest(
                reference._scorer_with(license="unknown"))

    def test_runtime_license_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "runtime_license"):
            reference.validate_scorer_manifest(reference._scorer_with(
                runtime={"name": "torch", "version": "2.1.0",
                         "license_id": "NOASSERTION"}))


class WerTests(unittest.TestCase):
    def test_valid_record_stays_unmeasured(self) -> None:
        result = reference.validate_wer_record(reference._wer_template())
        self.assertTrue(result["accepted_metadata"])
        self.assertFalse(result["measured_here"])
        self.assertFalse(result["merged_with_dnsmos_c"])

    def test_config_count_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "must_be_11"):
            reference.validate_wer_record(
                reference._wer_with(config_count=10))

    def test_library_column_must_stay_null(self) -> None:
        with self.assertRaisesRegex(ValueError, "stay_unmeasured"):
            reference.validate_wer_record(
                reference._wer_with(library_percent=5.0))

    def test_nan_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_percent"):
            reference.validate_wer_record(
                reference._wer_with(raw_percent=float("nan")))

    def test_out_of_range_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite_percent"):
            reference.validate_wer_record(
                reference._wer_with(processed_percent=101.0))


class ReportTests(unittest.TestCase):
    def test_decision_and_status(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertEqual(report["completeness"], "incomplete")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertFalse(report["qualification"]["qualifies"])

    def test_task_row_identity(self) -> None:
        self.assertEqual(reference.TASK_ROW_IDENTITY["id"], reference.TASK_ID)
        self.assertEqual(reference.TASK_ROW_IDENTITY["component"],
                         reference.COMPONENT)

    def test_eight_blocked_release_gates(self) -> None:
        report = reference.build_report()
        self.assertEqual(len(report["release_gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["release_gates"]))
        self.assertTrue(all(gate["qualifies"] is False
                            for gate in report["release_gates"]))

    def test_public_surface_unchanged(self) -> None:
        self.assertTrue(all(value is False
                            for value in reference.PUBLIC_SURFACE.values()))

    def test_real_score_slots_are_null(self) -> None:
        report = reference.build_report()
        self.assertTrue(all(value is None
                            for value in report["scorer"]["score_slots"].values()))
        self.assertTrue(all(value is None
                            for row in report["runs"]
                            for value in row["scores"].values()))

    def test_documented_scores_are_source_reported_not_reproduced(self) -> None:
        scores = reference.documented_scores()
        self.assertFalse(scores["reproduced_here"])
        self.assertFalse(scores["is_human_rating"])
        self.assertFalse(scores["is_mos"])
        self.assertEqual(scores["labels"], "source_reported_predicted_dnsmos_c")

    def test_wer_is_unrun_and_separate(self) -> None:
        wer = reference.wer_record()
        self.assertFalse(wer["measured_here"])
        self.assertFalse(wer["merged_with_dnsmos_c"])
        self.assertIsNone(wer["audio_enhance_percent"])

    def test_aggregation_recomputation_matches_three_decimals(self) -> None:
        for condition, expected in reference.DOCUMENTED_SCORES.items():
            recomputed = reference.equal_weight_average(
                {name: expected[name] for name in reference.SCENARIOS})
            self.assertEqual(round(recomputed, 3),
                             expected["scenario_average"], condition)

    def test_adverse_cases_all_rejected(self) -> None:
        rows = reference.adverse_results()
        self.assertGreaterEqual(len(rows), 45)
        self.assertTrue(reference._check_all_rejected(rows))
        self.assertTrue(all(row["qualifies"] is False for row in rows))

    def test_missing_cases_all_blocked(self) -> None:
        rows = reference.missing_results()
        self.assertGreaterEqual(len(rows), 12)
        self.assertTrue(all(row["status"] == "blocked" and row["scores"] is None
                            for row in rows))

    def test_every_probe_is_absent(self) -> None:
        self.assertTrue(all(row["present"] is False
                            for row in reference.absence_probes()))
        self.assertTrue(reference.artifact_assessment()["all_required_absent"])

    def test_evidence_profile_is_non_qualifying(self) -> None:
        profile = reference.acceptance_profile()
        self.assertEqual(profile["profile"], "evidence")
        self.assertFalse(profile["all_qualify"])
        self.assertTrue(all(item["qualifies"] is False
                            for item in profile["items"]))

    def test_rendered_report_is_byte_identical_three_times(self) -> None:
        payloads = [reference.render_report()[0] for _ in range(3)]
        self.assertEqual(len(set(payloads)), 1)
        digest = hashlib.sha256(payloads[0]).hexdigest()
        self.assertEqual(reference.render_report()[1], digest)

    def test_report_digest_is_stable(self) -> None:
        first = reference.render_report()
        second = reference.render_report()
        self.assertEqual(first, second)

    def test_canonical_report_has_single_trailing_newline(self) -> None:
        payload, _, _ = reference.render_report()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))

    def test_fixture_contains_no_audio(self) -> None:
        fixture = reference.fixture_payload()
        self.assertFalse(fixture["contains_audio"])
        self.assertFalse(fixture["scored"])

    def test_contract_is_task_local_and_defer(self) -> None:
        contract = reference.contract_payload({"x": "y"})
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["profile"], "evidence")
        self.assertFalse(contract["scope"]["downloads"])
        self.assertFalse(contract["public_surface"]["provider_registration"])

    def test_no_finite_real_values_are_present_as_scores(self) -> None:
        report = reference.build_report()
        self.assertIsNone(report["cohort"]["scenario_item_counts"]["work"])
        self.assertIsNone(report["scorer"]["checkpoint_sha256"])
        self.assertIsNone(report["scorer"]["source_revision"])


if __name__ == "__main__":
    unittest.main()
