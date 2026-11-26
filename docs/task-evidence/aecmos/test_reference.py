# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local tests for the AECMOS input-contract DEFER package."""

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

    def test_adapter_contract_audit(self) -> None:
        audit = reference.adapter_contract_audit()
        self.assertTrue(audit["all_tokens_present"])
        self.assertTrue(audit["hash_matches_source_pin"])
        self.assertFalse(audit["reproduces_feature_values"])
        self.assertFalse(audit["qualifies"])

    def test_task_row_identity(self) -> None:
        self.assertEqual(reference.TASK_ROW_IDENTITY["id"], "SDK-AECMOS")
        self.assertEqual(reference.TASK_ROW_IDENTITY["component"], "aecmos")
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
        for key in ("real_aecmos_weights", "real_aecmos_source",
                    "model_runtime_executed", "weights_or_assets",
                    "real_speech_or_corpus", "downloads", "device_timing",
                    "listening", "benchmark_claim", "release_claim"):
            self.assertIs(reference.SCOPE[key], False, key)

    def test_public_surface_is_unchanged(self) -> None:
        self.assertTrue(reference.PUBLIC_SURFACE)
        for key, value in reference.PUBLIC_SURFACE.items():
            self.assertIs(value, False, key)


class ContractGeometryTests(unittest.TestCase):
    def test_exact_geometry_constants(self) -> None:
        contract = reference.input_contract()
        self.assertEqual(contract["sample_rate_hz"], 16000)
        self.assertEqual(contract["n_fft"], 513)
        self.assertEqual(contract["hop_length"], 256)
        self.assertEqual(contract["n_mels"], 160)
        self.assertEqual(contract["fft_bins"], 257)
        self.assertEqual(contract["max_samples"], 320000)
        self.assertEqual(contract["scenario_marker_frames"], 20)
        self.assertEqual(contract["scenario_terminator_frames"], 20)
        self.assertEqual(contract["state_shape"], [4, 1, 64])

    def test_stream_and_output_order(self) -> None:
        contract = reference.input_contract()
        self.assertEqual(contract["stream_order"],
                         ["lpb", "microphone", "enhanced"])
        self.assertEqual(contract["output_names"],
                         ["aecmos_echo", "aecmos_degradation"])
        self.assertEqual(contract["talk_types"], ["st", "nst", "dt"])

    def test_no_score_is_claimed_reproduced(self) -> None:
        contract = reference.input_contract()
        self.assertFalse(contract["mel_implementation_reproduced"])
        self.assertFalse(contract["feature_values_reproduced"])
        self.assertFalse(contract["scores_reproduced"])
        self.assertFalse(contract["qualifies"])

    def test_frame_count_rule(self) -> None:
        self.assertEqual(reference.feature_frame_count(19200),
                         1 + (19200 - 1) // 256)
        self.assertEqual(reference.feature_frame_count(320000), 1250)
        self.assertEqual(reference.feature_frame_count(160), 1)
        self.assertEqual(reference.feature_frame_count(256), 1)
        self.assertEqual(reference.feature_frame_count(257), 2)

    def test_frame_count_rejects_bad_input(self) -> None:
        for value in (0, -1, True, 1.5, "1"):
            with self.assertRaises(reference.ReferenceError):
                reference.feature_frame_count(value)

    def test_length_policy(self) -> None:
        self.assertEqual(reference.length_policy(10), (10, False))
        self.assertEqual(reference.length_policy(320000), (320000, False))
        self.assertEqual(reference.length_policy(320001), (320000, True))
        self.assertEqual(reference.length_policy(999999), (320000, True))

    def test_length_policy_rejects_bad_input(self) -> None:
        for value in (0, -5, False, 2.5):
            with self.assertRaises(reference.ReferenceError):
                reference.length_policy(value)

    def test_marker_values_match_adapter(self) -> None:
        self.assertEqual(reference.scenario_marker("st"),
                         {"lpb": 1.0, "microphone": 0.0, "enhanced": 1.0})
        self.assertEqual(reference.scenario_marker("nst"),
                         {"lpb": 0.0, "microphone": 1.0, "enhanced": 1.0})
        self.assertEqual(reference.scenario_marker("dt"),
                         {"lpb": 1.0, "microphone": 1.0, "enhanced": 1.0})

    def test_invalid_talk_type_rejected(self) -> None:
        for value in ("ST", "", "single", None, 1):
            with self.assertRaises(reference.ReferenceError):
                reference.scenario_marker(value)


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.good = [0.01, -0.02, 0.03, 0.0]

    def test_accepts_valid_triplet(self) -> None:
        result = reference.validate_triplet(self.good, self.good, self.good, "dt")
        self.assertEqual(result["kept_samples"], 4)
        self.assertFalse(result["truncated"])
        self.assertTrue(result["finite"])

    def test_truncates_over_20s(self) -> None:
        big = [0.0] * (reference.MAX_SAMPLES + 3)
        result = reference.validate_triplet(big, big, big, "st")
        self.assertEqual(result["kept_samples"], reference.MAX_SAMPLES)
        self.assertTrue(result["truncated"])

    def test_rejects_missing_stream(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.validate_triplet(None, self.good, self.good, "dt")

    def test_rejects_empty_stream(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.validate_triplet([], self.good, self.good, "dt")

    def test_rejects_unequal_lengths(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.validate_triplet(self.good, self.good + [0.0],
                                       self.good, "dt")

    def test_rejects_bool_sample(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.validate_triplet([True], [0.0], [0.0], "dt")

    def test_rejects_nonfinite_sample(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(reference.ReferenceError):
                reference.validate_triplet([value], [0.0], [0.0], "dt")

    def test_rejects_out_of_bounds_sample(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.validate_triplet([reference.MAX_ABS_INPUT + 0.5],
                                       [0.0], [0.0], "dt")

    def test_rejects_string_stream(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.validate_triplet("abcd", self.good, self.good, "dt")

    def test_rejects_invalid_talk_type(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.validate_triplet(self.good, self.good, self.good, "dtx")


class FixtureTests(unittest.TestCase):
    def test_geometry(self) -> None:
        fixture = reference.fixture_payload()
        self.assertEqual(fixture["samples"], reference.FIXTURE_SAMPLES)
        self.assertEqual(fixture["sample_rate_hz"], 16000)
        self.assertEqual(fixture["stream_order"],
                         ["lpb", "microphone", "enhanced"])

    def test_deterministic(self) -> None:
        first = reference.build_streams("paired")
        second = reference.build_streams("paired")
        for name in reference.STREAM_ORDER:
            self.assertEqual(reference.digest_float32(first[name]),
                             reference.digest_float32(second[name]))

    def test_conditions_differ(self) -> None:
        paired = reference.geometry_payload("paired", "dt")
        plain = reference.build_streams("paired")
        silence = reference.build_streams("silence")
        self.assertNotEqual(reference.digest_float32(plain["lpb"]),
                            reference.digest_float32(silence["lpb"]))
        self.assertEqual(paired["scores"],
                         {"aecmos_echo": None, "aecmos_degradation": None})

    def test_no_reference_is_zero(self) -> None:
        streams = reference.build_streams("no_reference")
        self.assertEqual(set(streams["lpb"]), {0.0})

    def test_dropout_bounds(self) -> None:
        streams = reference.build_streams("reference_dropout")
        start = reference.DROPOUT_START_FRAME * reference.FRAME_SAMPLES
        end = reference.DROPOUT_END_FRAME * reference.FRAME_SAMPLES
        self.assertEqual(set(streams["lpb"][start:end]), {0.0})
        self.assertNotEqual(set(streams["lpb"][:start]), {0.0})

    def test_delayed_enhanced_is_shifted(self) -> None:
        paired = reference.build_streams("paired")["enhanced"]
        delayed = reference.build_streams("delayed_enhanced")["enhanced"]
        shift = reference.DELAYED_ENHANCED_SAMPLES
        self.assertEqual(delayed[:shift], [0.0] * shift)
        self.assertEqual(delayed[shift:], paired[:-shift])

    def test_swapped_streams(self) -> None:
        paired = reference.build_streams("paired")
        swapped = reference.build_streams("swapped_streams")
        self.assertEqual(swapped["lpb"], paired["microphone"])
        self.assertEqual(swapped["microphone"], paired["lpb"])

    def test_unknown_condition_rejected(self) -> None:
        with self.assertRaises(reference.ReferenceError):
            reference.build_streams("bogus")


class GeometryRunTests(unittest.TestCase):
    def test_three_talk_types(self) -> None:
        runs = reference.talk_type_runs()
        self.assertEqual([row["talk_type"] for row in runs], ["st", "nst", "dt"])
        self.assertEqual(len({row["triplet_digest"] for row in runs}), 1)

    def test_feature_shape_and_counts(self) -> None:
        for row in reference.talk_type_runs():
            base = row["frame_count_before_marker"]
            self.assertEqual(base, reference.feature_frame_count(row["kept_samples"]))
            self.assertEqual(row["feature_frames"], base + 40)
            self.assertEqual(row["feature_shape"],
                             [3, base + 40, reference.N_MELS])
            self.assertEqual(row["marker_end_frame"], base + 19)
            self.assertEqual(row["terminator_start_frame"], base + 20)
            self.assertEqual(row["terminator_end_frame"], base + 39)

    def test_all_scores_are_null(self) -> None:
        rows = reference.talk_type_runs() + list(reference.control_runs().values())
        for row in rows:
            self.assertEqual(row["scores"],
                             {"aecmos_echo": None, "aecmos_degradation": None})
            self.assertFalse(row["scores_are_aecmos_predictions"])
            self.assertFalse(row["scores_are_human_ratings"])
            self.assertFalse(row["qualifies"])

    def test_status_is_never_scored(self) -> None:
        rows = reference.talk_type_runs() + list(reference.control_runs().values())
        for row in rows:
            self.assertNotIn("ok", row["status"])
            self.assertTrue(row["status"].endswith("_not_scored"),
                            row["status"])

    def test_diagnostics_are_finite(self) -> None:
        for row in reference.talk_type_runs():
            for name in reference.STREAM_ORDER:
                stats = row["diagnostics"][name]
                self.assertTrue(math.isfinite(stats["rms"]))
                self.assertTrue(math.isfinite(stats["peak_abs"]))
                self.assertLessEqual(stats["peak_abs"], reference.MAX_ABS_INPUT)


class ControlTests(unittest.TestCase):
    def test_control_set(self) -> None:
        controls = reference.control_runs()
        self.assertEqual(
            set(controls),
            {"paired_reference", "swapped_streams", "no_reference",
             "reference_dropout", "delayed_enhanced", "silence"})

    def test_statuses(self) -> None:
        controls = reference.control_runs()
        self.assertEqual(controls["swapped_streams"]["status"],
                         "stream_order_control_not_scored")
        self.assertEqual(controls["no_reference"]["status"],
                         "no_reference_input_not_scored")
        self.assertEqual(controls["reference_dropout"]["status"],
                         "partial_reference_not_scored")
        self.assertEqual(controls["delayed_enhanced"]["status"],
                         "misaligned_enhanced_not_scored")
        self.assertEqual(controls["silence"]["status"],
                         "degenerate_silence_not_scored")

    def test_controls_are_distinct(self) -> None:
        controls = reference.control_runs()
        digests = {row["triplet_digest"] for row in controls.values()}
        self.assertEqual(len(digests), len(controls))

    def test_truncation_control(self) -> None:
        control = reference.truncation_control()
        self.assertTrue(control["kept_equals_max"])
        self.assertTrue(control["truncated"])
        self.assertEqual(control["frames_after_truncation"], 1250)
        self.assertFalse(control["qualifies"])


class FailureControlTests(unittest.TestCase):
    def test_all_checks_pass(self) -> None:
        controls = reference.failure_controls()
        self.assertTrue(controls["all_explicit"])
        for name, value in controls["checks"].items():
            self.assertTrue(value, name)

    def test_rejection_floor(self) -> None:
        controls = reference.failure_controls()
        self.assertGreaterEqual(controls["rejected_count"], 10)
        self.assertGreaterEqual(controls["blocked_count"], 8)


class JsonTests(unittest.TestCase):
    def write(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                             encoding="utf-8")
        handle.write(text)
        handle.close()
        return Path(handle.name)

    def test_strict_json_rejects_nan(self) -> None:
        path = self.write('{"a": NaN}')
        try:
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
        finally:
            path.unlink()

    def test_strict_json_rejects_duplicate_keys(self) -> None:
        path = self.write('{"a": 1, "a": 2}')
        try:
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
        finally:
            path.unlink()

    def test_strict_json_rejects_non_object(self) -> None:
        path = self.write("[1, 2]")
        try:
            with self.assertRaises(ValueError):
                reference.read_strict_json(path)
        finally:
            path.unlink()

    def test_canonical_bytes_reject_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"a": float("inf")})


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_report_key_set(self) -> None:
        self.assertEqual(set(self.report), reference.REPORT_KEYS)

    def test_decision_and_status(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["completeness"], "incomplete")
        self.assertEqual(self.report["profile"], "evidence")

    def test_qualification_is_not_qualified(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["qualifies"])
        self.assertTrue(qualification["incomplete"])
        self.assertFalse(qualification["missing_result_promoted"])

    def test_eight_release_gates_all_blocked(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertIsNone(gate["evidence"])
            self.assertFalse(gate["qualifies"])

    def test_required_artifacts_absent(self) -> None:
        for artifact in reference.REQUIRED_ARTIFACTS:
            self.assertFalse(artifact["present"], artifact["id"])

    def test_runs_are_three_talk_types(self) -> None:
        self.assertEqual([row["talk_type"] for row in self.report["runs"]],
                         ["st", "nst", "dt"])
        for row in self.report["runs"]:
            self.assertFalse(row["qualifies"])

    def test_controls_cover_evidence_cases(self) -> None:
        self.assertEqual(
            set(self.report["controls"]),
            {"paired_reference", "swapped_streams", "no_reference",
             "reference_dropout", "delayed_enhanced", "silence"})

    def test_adverse_results_retained(self) -> None:
        rows = self.report["adverse_results"]
        self.assertGreaterEqual(len(rows), 6)
        self.assertTrue(any(row["result_id"] == "over_20s_truncation"
                            for row in rows))
        for row in rows:
            self.assertFalse(row["qualifies"])

    def test_missing_results_not_promoted(self) -> None:
        rows = self.report["missing_results"]
        self.assertTrue(rows)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["scores"])
            self.assertFalse(row["qualifies"])

    def test_failure_controls(self) -> None:
        controls = self.report["failure_controls"]
        self.assertTrue(controls["all_explicit"])
        self.assertGreaterEqual(controls["rejected_count"], 10)

    def test_acceptance_profile_all_nonqualifying(self) -> None:
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "evidence")
        self.assertFalse(profile["all_qualify"])
        self.assertFalse(profile["qualifies"])
        self.assertTrue(profile["items"])
        allowed = {"synthetic_control_only", "synthetic_geometry_only",
                   "proposal_only", "blocked"}
        for item in profile["items"]:
            self.assertIn(item["status"], allowed)
            self.assertFalse(item["qualifies"])

    def test_observed_provenance_is_not_reproduced(self) -> None:
        provenance = self.report["observed_provenance"]
        self.assertFalse(provenance["reproduced_here"])
        for item in provenance["documented_context"]:
            self.assertFalse(item["reproduced_here"])
            self.assertFalse(item["is_human_rating"])

    def test_artifact_assessment_blocked(self) -> None:
        assessment = self.report["artifact_assessment"]
        self.assertTrue(assessment["all_required_absent"])
        self.assertFalse(assessment["runtime_presence"]["present"])
        self.assertFalse(assessment["weights_presence"]["present"])
        self.assertFalse(assessment["corpus_presence"]["present"])
        self.assertFalse(assessment["package_assets"]["present"])
        self.assertTrue(assessment["conclusion"].startswith("BLOCKED:"))

    def test_ranking_is_not_a_recommendation(self) -> None:
        ranking = self.report["ranking"]
        self.assertEqual(ranking["order"], "not_ranked")
        self.assertIsNone(ranking["recommendation"])
        self.assertFalse(ranking["qualifies"])

    def test_no_qualifying_true_anywhere(self) -> None:
        def walk(value) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == "qualifies":
                        self.assertIs(item, False)
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
        walk(self.report)

    def test_regeneration_is_three_identical(self) -> None:
        regeneration = self.report["regeneration"]
        self.assertEqual(regeneration["runs"], 3)
        self.assertTrue(regeneration["byte_identical"])
        self.assertEqual(len(set(regeneration["canonical_digests"])), 1)

    def test_canonical_report_is_deterministic(self) -> None:
        text, digest = reference.canonical_report(self.report)
        second_text, second_digest = reference.canonical_report(
            reference.build_report())
        self.assertEqual(text, second_text)
        self.assertEqual(digest, second_digest)


if __name__ == "__main__":
    unittest.main()
