# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local tests for the DNSMOS P.835 / DNSMOS-C DEFER package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import struct
import tempfile
import unittest

import reference

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]


class PinTests(unittest.TestCase):
    def test_source_pins_are_exact(self) -> None:
        for name, expected in reference.SOURCE_PINS.items():
            self.assertEqual(reference.digest_file(WORKSPACE / name), expected, name)

    def test_boundary_pins_are_exact(self) -> None:
        for name, expected in reference.BOUNDARY_PINS.items():
            self.assertEqual(reference.digest_file(WORKTREE / name), expected, name)

    def test_sibling_pins_are_exact(self) -> None:
        for name, expected in reference.SIBLING_PINS.items():
            self.assertEqual(reference.digest_file(WORKTREE / name), expected, name)

    def test_documentation_audit_tokens(self) -> None:
        audit = reference.scorer_documentation_audit()
        self.assertTrue(audit["p835_script"]["all_tokens_present"])
        self.assertTrue(audit["dnsmos_c_report"]["all_tokens_present"])
        self.assertFalse(audit["reproduces_scores"])
        self.assertFalse(audit["qualifies"])

    def test_task_row_identity(self) -> None:
        self.assertEqual(reference.TASK_ROW_IDENTITY["id"],
                         "SDK-DNSMOS-P-835-AND-DNSMOS-C")
        self.assertEqual(reference.TASK_ROW_IDENTITY["component"],
                         "dnsmos-p-835-and-dnsmos-c")
        self.assertEqual(reference.TASK_ROW_IDENTITY["mode"], "research-control")
        self.assertEqual(reference.TASK_ROW_IDENTITY["base_commit"],
                         reference.BASE_COMMIT)
        self.assertEqual(reference.TASK_ROW_IDENTITY["branch"],
                         reference.BRANCH)

    def test_mutable_board_is_not_gated(self) -> None:
        self.assertFalse(reference.MUTABLE_PROVENANCE["hashed"])
        self.assertFalse(reference.MUTABLE_PROVENANCE["gate"])

    def test_scope_is_synthetic_and_local(self) -> None:
        self.assertTrue(reference.SCOPE["task_local_only"])
        self.assertTrue(reference.SCOPE["synthetic_only"])
        self.assertTrue(
            reference.SCOPE["predicted_scores_kept_separate_from_subjective_mos"])
        for key in ("real_p835_weights", "real_p835_scorer",
                    "real_dnsmos_c_checkpoint", "real_dnsmos_c_source",
                    "model_runtime_executed", "weights_or_assets",
                    "real_speech_or_corpus", "downloads", "device_timing",
                    "listening", "benchmark_claim", "release_claim"):
            self.assertFalse(reference.SCOPE[key], key)

    def test_public_surface_is_unchanged(self) -> None:
        for key, value in reference.PUBLIC_SURFACE.items():
            self.assertFalse(value, key)

    def test_exactly_eight_blocked_gates(self) -> None:
        self.assertEqual(len(reference.RELEASE_GATES), 8)
        for gate in reference.RELEASE_GATES:
            self.assertEqual(gate["status"], "blocked")
            self.assertIs(gate["qualifies"], False)
            self.assertIsNone(gate["evidence"])

    def test_required_artifacts_are_absent(self) -> None:
        for item in reference.REQUIRED_ARTIFACTS:
            self.assertFalse(item["present"], item["id"])
            self.assertTrue(item["rights_requirement"])


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError) as caught:
            reference.parse_strict_json_text('{"a":1,"a":2}')
        self.assertIn("duplicate_json_key", str(caught.exception))

    def test_nan_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text('{"a":NaN}')

    def test_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text('{"a":Infinity}')

    def test_top_level_array_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text("[1]")

    def test_empty_document_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_strict_json_text("  ")

    def test_valid_document(self) -> None:
        self.assertEqual(reference.parse_strict_json_text('{"a": 1}'), {"a": 1})


class P835WindowTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(reference.P835_WINDOW_SAMPLES, 144160)
        self.assertEqual(reference.P835_HOP_SAMPLES, 16000)
        self.assertEqual(reference.P835_INPUT_LENGTH_S, 9.01)

    def test_exact_window_is_one_hop(self) -> None:
        plan = reference.p835_window_plan(144160)
        self.assertEqual(plan["doublings"], 0)
        self.assertEqual(plan["num_hops"], 1)
        self.assertEqual(plan["windows"][0]["start"], 0)
        self.assertEqual(plan["windows"][0]["end"], 144160)
        self.assertEqual(plan["windows"][0]["original_samples"], 144160)
        self.assertEqual(plan["uncovered_samples"], 0)

    def test_short_buffer_doubling(self) -> None:
        plan = reference.p835_window_plan(12000)
        self.assertEqual(plan["doublings"], 4)
        self.assertEqual(plan["padded_samples"], 192000)
        self.assertEqual(plan["num_hops"], 3)
        self.assertEqual(plan["windows"][0]["original_samples"], 12000)
        self.assertEqual(plan["windows"][0]["repeated_samples"], 132160)
        self.assertEqual(plan["windows"][1]["original_samples"], 0)

    def test_one_sample_over_leaves_uncovered_sample(self) -> None:
        plan = reference.p835_window_plan(144161)
        self.assertEqual(plan["num_hops"], 1)
        self.assertEqual(plan["uncovered_samples"], 1)

    def test_single_sample_doubling_count(self) -> None:
        plan = reference.p835_window_plan(1)
        self.assertEqual(plan["doublings"], 18)
        self.assertEqual(plan["padded_samples"], 262144)
        self.assertEqual(plan["num_hops"], 7)
        self.assertEqual(plan["windows"][0]["original_samples"], 1)

    def test_windows_are_contiguous_slices(self) -> None:
        plan = reference.p835_window_plan(300000)
        for window in plan["windows"]:
            self.assertEqual(window["samples"], reference.P835_WINDOW_SAMPLES)
            self.assertEqual(window["original_samples"]
                             + window["repeated_samples"], window["samples"])
        starts = [window["start"] for window in plan["windows"]]
        self.assertEqual(starts, [index * 16000
                                  for index in range(plan["num_hops"])])

    def test_rejects_invalid_inputs(self) -> None:
        for value in (True, 1.5, 0, -1, "1", None):
            with self.assertRaises(reference.ReferenceError):
                reference.p835_window_plan(value)
        with self.assertRaises(reference.ReferenceError):
            reference.p835_window_plan(reference.MAX_INPUT_SAMPLES + 1)

    def test_plan_is_not_scored(self) -> None:
        plan = reference.p835_window_plan(12000)
        self.assertIs(plan["scored"], False)
        self.assertIs(plan["qualifies"], False)


class PostprocessTests(unittest.TestCase):
    def test_standard_mapping_literals(self) -> None:
        mapped = reference.p835_postprocess(2.5, 3.0, 2.8)["mapped"]
        self.assertAlmostEqual(mapped["SIG"], 2.53251285, places=9)
        self.assertAlmostEqual(mapped["BAK"], 3.24640004, places=9)
        self.assertAlmostEqual(mapped["OVL"], 2.6388498668, places=9)

    def test_personalized_mapping_differs(self) -> None:
        standard = reference.p835_postprocess(2.5, 3.0, 2.8)
        personalized = reference.p835_postprocess(
            2.5, 3.0, 2.8, personalized=True)
        self.assertEqual(standard["variant"], "standard")
        self.assertEqual(personalized["variant"], "personalized")
        self.assertNotEqual(standard["mapped"], personalized["mapped"])

    def test_mapping_is_not_a_score(self) -> None:
        result = reference.p835_postprocess(2.5, 3.0, 2.8)
        self.assertFalse(result["is_model_output"])
        self.assertFalse(result["is_mos"])
        self.assertFalse(result["is_human_rating"])
        self.assertFalse(result["qualifies"])

    def test_rejects_nonfinite_and_out_of_range(self) -> None:
        for args in ((float("nan"), 3.0, 2.8),
                     (2.5, float("inf"), 2.8),
                     (9.0, 3.0, 2.8),
                     (2.5, -0.1, 2.8),
                     (True, 3.0, 2.8),
                     ("2.5", 3.0, 2.8)):
            with self.assertRaises(reference.ReferenceError):
                reference.p835_postprocess(*args)

    def test_rejects_bad_variant(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.p835_postprocess(2.5, 3.0, 2.8, personalized="yes")

    def test_coefficients_are_documented_shape(self) -> None:
        self.assertEqual(len(reference.P835_POLYFIT["standard"]["SIG"]), 3)
        self.assertEqual(len(reference.P835_POLYFIT["personalized"]["SIG"]), 4)


class DnsmosCSegmentTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(reference.DNSC_SEGMENT_KINDS, ("primary", "mix"))
        self.assertEqual(reference.DNSC_MIN_SEGMENT_MS, 1000)
        self.assertEqual(reference.DNSC_WINDOW_MS, 10000)
        self.assertEqual(reference.DNSC_HOP_MS, 5000)

    def test_sub_one_second_dropped(self) -> None:
        plan = reference.dnsmos_c_segment_plan(999, "primary")
        self.assertTrue(plan["dropped"])
        self.assertEqual(plan["drop_reason"], "segment_shorter_than_1s")
        self.assertEqual(plan["window_count"], 0)

    def test_one_second_repeated_ten_times(self) -> None:
        plan = reference.dnsmos_c_segment_plan(1000, "mix")
        self.assertFalse(plan["dropped"])
        self.assertTrue(plan["repeated"])
        self.assertEqual(plan["repeat_count"], 10)
        self.assertEqual(plan["tiling_truncated_ms"], 0)
        self.assertEqual(plan["window_count"], 1)

    def test_four_seconds_repeated_and_truncated(self) -> None:
        plan = reference.dnsmos_c_segment_plan(4000, "primary")
        self.assertEqual(plan["repeat_count"], 3)
        self.assertEqual(plan["tiled_ms"], 12000)
        self.assertEqual(plan["tiling_truncated_ms"], 2000)

    def test_ten_seconds_single_window(self) -> None:
        plan = reference.dnsmos_c_segment_plan(10000, "mix")
        self.assertFalse(plan["repeated"])
        self.assertEqual(plan["window_count"], 1)
        self.assertFalse(plan["end_aligned_tail"])

    def test_long_segment_gets_end_aligned_tail(self) -> None:
        plan = reference.dnsmos_c_segment_plan(12345, "primary")
        self.assertEqual(plan["window_count"], 2)
        self.assertTrue(plan["end_aligned_tail"])
        self.assertEqual(plan["windows"][-1]["start_ms"], 2345)
        self.assertEqual(plan["windows"][-1]["end_ms"], 12345)

    def test_exact_hop_multiple_has_no_tail(self) -> None:
        plan = reference.dnsmos_c_segment_plan(15000, "mix")
        self.assertEqual(plan["window_count"], 2)
        self.assertFalse(plan["end_aligned_tail"])
        self.assertEqual(plan["windows"][-1]["start_ms"], 5000)

    def test_interval_union(self) -> None:
        self.assertEqual(
            reference._interval_union_ms([(0, 10), (5, 15), (20, 30)]), 25)

    def test_rejects_invalid_segments(self) -> None:
        for duration in (True, 1000.5, 0, -1, None):
            with self.assertRaises(reference.ReferenceError):
                reference.dnsmos_c_segment_plan(duration)
        with self.assertRaises(reference.ReferenceError):
            reference.dnsmos_c_segment_plan(
                reference.DNSC_MAX_DURATION_MS + 1)
        with self.assertRaises(reference.ReferenceError):
            reference.dnsmos_c_segment_plan(1000, "other")

    def test_plan_builder_counts(self) -> None:
        plan = reference.dnsmos_c_plan(reference.DNSC_FIXTURE_SEGMENTS)
        self.assertEqual(plan["segment_count"], 6)
        self.assertEqual(plan["dropped_segment_count"], 1)
        self.assertEqual(plan["scored_segment_count"], 5)
        self.assertEqual(plan["window_count"], 7)
        self.assertIs(plan["qualifies"], False)

    def test_plan_rejects_bad_lists(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.dnsmos_c_plan([])
        with self.assertRaises(reference.ReferenceError):
            reference.dnsmos_c_plan(["primary"])
        with self.assertRaises(reference.ReferenceError):
            reference.dnsmos_c_plan(
                [{"kind": "primary", "duration_ms": 1000, "extra": 1}])


class AggregationTests(unittest.TestCase):
    def test_exact_mean(self) -> None:
        self.assertEqual(reference.exact_mean([3.0, 4.25, 3.5, 4.75]), 3.875)

    def test_mean_is_order_invariant(self) -> None:
        self.assertEqual(reference.exact_mean([3.0, 4.25, 3.5, 4.75]),
                         reference.exact_mean([4.75, 3.5, 4.25, 3.0]))

    def test_scenario_average_equal_weight(self) -> None:
        self.assertEqual(
            reference.scenario_average(
                {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0}),
            3.5)

    def test_rejects_bad_aggregation(self) -> None:
        for values in ([], [float("nan")], [float("inf")], ["3"], [True]):
            with self.assertRaises(reference.ReferenceError):
                reference.exact_mean(values)
        for mapping in ({}, {"a": 3.0}, {"a": 3.0, "b": 4.0},
                        {"a": 3.0, "b": 4.0, "c": float("nan")}):
            with self.assertRaises(reference.ReferenceError):
                reference.scenario_average(mapping)

    def test_aggregation_is_not_a_score(self) -> None:
        self.assertIs(reference.aggregation_reference()["is_a_score"], False)


class ManifestTests(unittest.TestCase):
    def test_valid_p835_manifest_shape_is_not_admitted(self) -> None:
        result = reference.validate_scorer_manifest(
            reference._manifest_template("dnsmos_p835"))
        self.assertTrue(result["accepted"])
        self.assertFalse(result["admitted_for_execution"])
        self.assertFalse(result["qualifies"])

    def test_valid_dnsmos_c_manifest_shape_is_not_admitted(self) -> None:
        result = reference.validate_scorer_manifest(
            reference._manifest_template("dnsmos_c"))
        self.assertTrue(result["accepted"])
        self.assertFalse(result["admitted_for_execution"])

    def test_manifest_rejections(self) -> None:
        cases = [
            reference._manifest_with(metric="dnsmos_p808"),
            reference._manifest_with(sample_rate_hz=48000),
            reference._manifest_with(channels=2),
            reference._manifest_with(license="unknown"),
            reference._manifest_with(source_revision="main"),
            reference._manifest_with(extra="field"),
        ]
        for manifest in cases:
            with self.assertRaises(reference.ReferenceError):
                reference.validate_scorer_manifest(manifest)

    def test_manifest_model_rejections(self) -> None:
        base = reference._manifest_template("dnsmos_p835")["models"]
        bad_sha = [dict(base[0], sha256="ABCDEF"), base[1]]
        zero_bytes = [dict(base[0], bytes=0), base[1]]
        duplicate = [base[0], dict(base[0])]
        traversal = [dict(base[0], name="../sig.onnx"), base[1]]
        wrong_set = [dict(base[0], name="model_v8.onnx"), base[1]]
        for models in (bad_sha, zero_bytes, duplicate, traversal, wrong_set):
            with self.assertRaises(reference.ReferenceError):
                reference.validate_scorer_manifest(
                    reference._manifest_with(models=models))

    def test_manifest_requires_exact_field_set(self) -> None:
        manifest = reference._manifest_template()
        del manifest["license"]
        with self.assertRaises(reference.ReferenceError):
            reference.validate_scorer_manifest(manifest)


class AdmissionTests(unittest.TestCase):
    def test_exact_pinned_pair_is_identity_only(self) -> None:
        result = reference.classify_observed_artifact(
            "sig.onnx", "dnsmos_p835", reference.P835_MODELS["sig.onnx"])
        self.assertTrue(result["identity_accepted"])
        self.assertFalse(result["admitted_for_execution"])
        self.assertFalse(result["qualifies"])

    def test_p808_copy_is_not_p835(self) -> None:
        with self.assertRaises(reference.ReferenceError) as caught:
            reference.classify_observed_artifact(
                "model_v8.onnx", "dnsmos_p835", "0" * 64)
        self.assertEqual(str(caught.exception), "wrong_model_identity")

    def test_combined_p835_copy_is_not_a_split_model(self) -> None:
        with self.assertRaises(reference.ReferenceError) as caught:
            reference.classify_observed_artifact(
                "sig_bak_ovr.onnx", "dnsmos_p835", "0" * 64)
        self.assertEqual(str(caught.exception), "wrong_model_identity")

    def test_wrong_digest_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceError) as caught:
            reference.classify_observed_artifact(
                "sig.onnx", "dnsmos_p835", "0" * 64)
        self.assertEqual(str(caught.exception), "wrong_model_digest")

    def test_unknown_metric_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceError) as caught:
            reference.classify_observed_artifact(
                "sig.onnx", "dnsmos_p806", reference.P835_MODELS["sig.onnx"])
        self.assertEqual(str(caught.exception), "unknown_metric")


class ReportTests(unittest.TestCase):
    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_bytes(reference.build_report_core())
        second = reference.canonical_bytes(reference.build_report_core())
        self.assertEqual(first, second)

    def test_report_has_no_nonfinite_json(self) -> None:
        payload = reference.canonical_bytes(reference.build_report_core())

        def reject_constant(value: str) -> None:
            raise AssertionError("nonfinite JSON constant: " + value)

        json.loads(payload, parse_constant=reject_constant)

    def test_all_score_slots_are_null(self) -> None:
        report = reference.build_report_core()
        for scorer in report["scorers"]:
            self.assertTrue(all(value is None
                                for value in scorer["score_slots"].values()))
        for run in report["runs"]:
            self.assertTrue(all(value is None for value in run["scores"].values()))

    def test_every_result_is_non_qualifying(self) -> None:
        report = reference.build_report_core()

        def walk(value: object) -> None:
            if isinstance(value, dict):
                if "qualifies" in value:
                    self.assertIs(value["qualifies"], False)
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(report)

    def test_eight_blocked_gates_in_report(self) -> None:
        report = reference.build_report_core()
        self.assertEqual(len(report["release_gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["release_gates"]))

    def test_adverse_results_all_rejected(self) -> None:
        rows = reference.adverse_results()
        self.assertGreaterEqual(len(rows), 50)
        self.assertTrue(all(row["rejected"] for row in rows))
        self.assertTrue(all(row["state_unchanged"] for row in rows))

    def test_missing_results_are_blocked(self) -> None:
        rows = reference.missing_results()
        self.assertGreaterEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["scores"])
            self.assertIs(row["qualifies"], False)

    def test_failure_controls_all_true(self) -> None:
        controls = reference.failure_controls()
        self.assertTrue(controls["all_explicit"])
        self.assertTrue(all(controls["checks"].values()))
        self.assertEqual(controls["rejected_count"],
                         len(reference.adverse_results()))

    def test_observed_provenance_is_not_reproduced(self) -> None:
        provenance = reference.observed_provenance()
        self.assertFalse(provenance["reproduced_here"])
        for item in provenance["documented_context"]:
            self.assertFalse(item["reproduced_here"])
            self.assertFalse(item["is_human_rating"])
            self.assertFalse(item["is_mos"])

    def test_artifact_assessment_is_explicit_blocker(self) -> None:
        assessment = reference.artifact_assessment()
        self.assertTrue(assessment["all_required_absent"])
        self.assertFalse(assessment["crosscheck"]["admitted"])
        self.assertFalse(assessment["substitution"]["performed"])
        self.assertTrue(assessment["conclusion"].startswith("BLOCKED:"))

    def test_regeneration_reports_three_identical_digests(self) -> None:
        payload, digest, core_digest = reference.render_report()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertEqual(len(digest), 64)
        report = json.loads(payload)
        self.assertEqual(report["regeneration"]["canonical_digests"],
                         [core_digest] * 3)
        self.assertTrue(report["regeneration"]["byte_identical"])

    def test_ranking_is_withheld(self) -> None:
        ranking = reference.build_report_core()["ranking"]
        self.assertEqual(ranking["order"], "not_ranked")
        self.assertIsNone(ranking["recommendation"])
        self.assertIs(ranking["qualifies"], False)

    def test_separation_from_siblings(self) -> None:
        separation = reference.separation_from_siblings()
        self.assertFalse(separation["reused_source_fixtures_metrics_or_results"])
        self.assertTrue(all(not package["reused"]
                            for package in separation["packages"]))

    def test_fixture_digest_is_float32_stable(self) -> None:
        values = reference.p835_fixture_values()
        self.assertEqual(reference.digest_float32(values),
                         reference.digest_float32(list(values)))
        self.assertEqual(len(values), reference.P835_FIXTURE_SAMPLES)

    def test_fixture_is_not_speech(self) -> None:
        fixture = reference.fixture_payload()
        self.assertFalse(fixture["p835"]["is_speech"])
        self.assertFalse(fixture["dnsmos_c"]["is_speech"])


class FileTests(unittest.TestCase):
    def test_read_strict_json_rejects_duplicate_key_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as handle:
            handle.write('{"a":1,"a":2}')
            name = handle.name
        try:
            with self.assertRaises(ValueError):
                reference.read_strict_json(Path(name))
        finally:
            Path(name).unlink()

    def test_read_strict_json_accepts_clean_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as handle:
            handle.write('{"a":1}')
            name = handle.name
        try:
            self.assertEqual(reference.read_strict_json(Path(name)), {"a": 1})
        finally:
            Path(name).unlink()

    def test_committed_report_parses_strictly(self) -> None:
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertEqual(report["decision"], "DEFER")

    def test_committed_contract_parses_strictly(self) -> None:
        contract = reference.read_strict_json(ROOT / "contract.json")
        self.assertEqual(contract["decision"], "DEFER")

    def test_report_sidecar_matches_bytes(self) -> None:
        import hashlib

        digest = hashlib.sha256((ROOT / "report.json").read_bytes()).hexdigest()
        self.assertEqual(
            (ROOT / "report.json.sha256").read_text(encoding="ascii").strip(),
            digest)


if __name__ == "__main__":
    unittest.main()
