# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest suite for the dynamic-int8 wav2vec2-base package.

No network, model, weight, runtime, audio, transcript, syllable label,
listening session or device measurement is used. No test is skipped.
"""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}',
                     '{"a":-Infinity}'):
            with self.assertRaises(ValueError):
                reference.loads_strict(text)

    def test_non_object_root_rejected(self) -> None:
        for text in ("[]", "1", "null", '"x"'):
            with self.assertRaises(ValueError):
                reference.loads_strict(text)

    def test_byte_order_mark_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.loads_strict('\ufeff{"a":1}')

    def test_canonical_bytes_are_sorted_and_newline_terminated(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": [True, "x"]})
        self.assertEqual(payload, b'{"a":[true,"x"],"b":1}\n')

    def test_object_digest_is_stable(self) -> None:
        document = {"b": [1, 2], "a": "x"}
        self.assertEqual(reference.object_digest(document),
                         reference.object_digest({"a": "x", "b": [1, 2]}))

    def test_decimal_string_rejects_nonfinite(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                reference._decimal_string(value)

    def test_decimal_string_has_no_negative_zero(self) -> None:
        self.assertEqual(reference._decimal_string(-0.0), "0")


class PinAndBoundaryTests(unittest.TestCase):
    def test_source_pins_verify(self) -> None:
        rows = reference.pin_rows(reference.SOURCE_PINS, reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.SOURCE_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_boundary_pins_verify(self) -> None:
        rows = reference.pin_rows(reference.BOUNDARY_PINS, reference.WORKTREE)
        self.assertEqual(len(rows), len(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_board_projection_has_only_stable_fields(self) -> None:
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(tuple(row), reference.BOARD_ROW_FIELDS)
        self.assertEqual(row["id"], reference.TASK)
        for field in ("status", "owner", "claim", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertNotIn(field, row)

    def test_linked_row_digest_is_stable(self) -> None:
        first = reference.linked_rows_digest()
        second = reference.linked_rows_digest(reference.linked_rows())
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")

    def test_linked_rows_include_dependencies(self) -> None:
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))

    def test_absence_probes_are_all_absent(self) -> None:
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_home_absence_probes_are_all_absent(self) -> None:
        rows = reference.home_absence_probes()
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_present_probe_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "data/models/speech-rate-encoders"
            target.mkdir(parents=True)
            with self.assertRaises(ValueError):
                reference.absence_probes(
                    root, ("data/models/speech-rate-encoders",))

    def test_absence_summary_counts(self) -> None:
        summary = reference.absence_summary(
            reference.absence_probes(reference.AUDIO_ROOT),
            reference.home_absence_probes())
        self.assertEqual(summary["probe_count"], 20)
        self.assertEqual(summary["workspace_probe_count"], 16)
        self.assertEqual(summary["home_probe_count"], 4)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])

    def test_absence_summary_never_claims_use(self) -> None:
        summary = reference.absence_summary([], [])
        for key in ("download_attempted", "network_used",
                    "recursive_workspace_walk", "source_or_runtime_imported",
                    "weights_loaded", "model_executed", "audio_read"):
            self.assertIs(summary[key], False)


class ArtifactAndGateTests(unittest.TestCase):
    def test_artifacts_have_one_present_and_six_blocked(self) -> None:
        rows = reference.REQUIRED_ARTIFACTS
        self.assertEqual(len(rows), 7)
        self.assertTrue(rows[0]["present"])
        self.assertTrue(rows[0]["verified"])
        self.assertFalse(rows[0]["blocked"])
        for row in rows[1:]:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])

    def test_eight_gates_are_blocked(self) -> None:
        contract = reference.build_contract()
        gates = contract["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual([gate["id"] for gate in gates],
                         [f"RG-{index:02d}" for index in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])

    def test_six_blockers_are_open(self) -> None:
        blockers = reference.build_contract()["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertTrue(blocker["required_action"])

    def test_rate_profile_rows_are_blocked(self) -> None:
        rows = reference.build_contract()["rate_profile_requirements"]
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["status"] == "blocked" for row in rows))

    def test_quality_and_timing_rows_have_no_values(self) -> None:
        contract = reference.build_contract()
        for section in ("quality_outcomes", "timing_requirements"):
            rows = contract[section]
            self.assertEqual(len(rows), 4)
            for row in rows:
                self.assertEqual(row["status"], "blocked")
                self.assertIsNone(row["value"])

    def test_qualification_never_claims(self) -> None:
        qualification = reference.build_contract()["qualification"]
        self.assertTrue(qualification["not_qualified"])
        self.assertTrue(qualification["all_release_gates_blocked"])
        for key in ("real_result_present", "weights_present",
                    "runtime_present", "quantized_artifact_present",
                    "fp32_int8_result", "accuracy_result",
                    "embedding_fidelity_result", "device_timing_result",
                    "rate_profile_result", "listening_result",
                    "benchmark_result", "release_claim",
                    "missing_result_promoted"):
            self.assertFalse(qualification[key])

    def test_exact_model_is_absent_and_not_downloaded(self) -> None:
        model = reference.build_contract()["exact_model"]
        self.assertEqual(model["revision"], reference.UPSTREAM_REVISION)
        self.assertEqual(model["weight_sha256"],
                         reference.MODEL_WEIGHT_SHA256)
        self.assertFalse(model["locally_present"])
        self.assertFalse(model["downloaded_or_reconstructed"])
        self.assertFalse(model["files_documented_locally_verified"])

    def test_recipe_is_provenance_only(self) -> None:
        recipe = reference.recipe_provenance()
        self.assertEqual(recipe["engine"], "qnnpack")
        self.assertEqual(recipe["dtype"], "qint8")
        self.assertEqual(recipe["module_types"], ["torch.nn.Linear"])
        self.assertTrue(recipe["quantized_linear_weights"])
        self.assertFalse(recipe["executed_here"])
        self.assertFalse(recipe["saved_quantized_state_dict"])
        self.assertEqual(recipe["recipe_snippets_present"],
                         recipe["recipe_snippets_required"])

    def test_documented_metrics_are_not_reproduced(self) -> None:
        metrics = reference.documented_metrics()
        self.assertFalse(metrics["reproduced_here"])
        self.assertFalse(metrics["used_for_evidence"])
        self.assertFalse(metrics["qualifies"])
        self.assertEqual(metrics["revision"], reference.UPSTREAM_REVISION)
        self.assertEqual(metrics["weight_bytes"],
                         str(reference.MODEL_WEIGHT_BYTES))
        self.assertEqual(metrics["runtime_torch"], "2.2.2")
        self.assertEqual(metrics["runtime_transformers"], "4.40.2")
        self.assertEqual(metrics["nonnegative_mae_syllables_per_second"],
                         "0.6867313226062639")
        self.assertEqual(metrics["median_fp32_int8_embedding_cosine"],
                         "0.9761238098144531")

    def test_source_presence_never_uses_assets(self) -> None:
        presence = reference.source_presence()
        self.assertFalse(presence["exact_weights_present"])
        self.assertFalse(presence["exact_runtime_present"])
        self.assertFalse(presence["quantized_engine_artifact_present"])
        self.assertFalse(
            presence["exact_source_weights_runtime_conjunction_present"])
        for key in ("weights_used", "runtime_imported", "audio_read",
                    "model_executed"):
            self.assertFalse(presence[key])
        self.assertEqual(len(presence["derived_artifacts"]), 4)


class AdmissionTests(unittest.TestCase):
    def test_control_is_accepted_and_not_qualified(self) -> None:
        manifest = reference.control_manifest()
        before = copy.deepcopy(manifest)
        reference.validate_manifest(manifest)
        self.assertEqual(manifest, before)
        admission = reference.build_admission()
        self.assertTrue(admission["control"]["accepted"])
        self.assertFalse(admission["control"]["qualifies"])
        self.assertEqual(admission["control"]["label"],
                         "synthetic_schema_control_not_evidence")

    def test_non_object_manifest_rejected(self) -> None:
        for value in ([], 1, None, "x"):
            with self.assertRaises(ValueError):
                reference.validate_manifest(value)  # type: ignore[arg-type]

    def test_every_admission_mutation_is_rejected(self) -> None:
        cases = reference.admission_cases()
        self.assertGreaterEqual(len(cases), 70)
        for case in cases:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])

    def test_missing_weight_rejected(self) -> None:
        manifest = reference.control_manifest()
        del manifest["weights"]["files"]["model.safetensors"]
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_wrong_weight_digest_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["weights"]["files"]["model.safetensors"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_wrong_weight_size_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["weights"]["files"]["model.safetensors"]["byte_count"] = 1
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_nonfinite_rate_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            manifest = reference.control_manifest()
            manifest["audio"][0]["reference_rate_sps"] = value
            with self.assertRaises(ValueError):
                reference.validate_manifest(manifest)

    def test_wrong_runtime_rejected(self) -> None:
        for field, value in (("python", "3.12.16"), ("torch", "2.4.0"),
                             ("transformers", "4.44.0"), ("device", "cuda")):
            manifest = reference.control_manifest()
            manifest["runtime"][field] = value
            with self.assertRaises(ValueError):
                reference.validate_manifest(manifest)

    def test_human_nuclei_claim_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["labels"]["human_syllable_nuclei"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_duplicate_audio_id_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["audio"][1]["id"] = manifest["audio"][0]["id"]
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_relative_audio_path_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["audio"][0]["path"] = "relative.wav"
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_wrong_window_span_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["audio"][0]["end_s"] = 3.0
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_quantization_plan_mismatch_rejected(self) -> None:
        for field, value in (("scheme", "static"), ("dtype", "float16"),
                             ("backend", "fbgemm"),
                             ("modules", ["torch.nn.Conv1d"]),
                             ("reduce_range", True)):
            manifest = reference.control_manifest()
            manifest["quantization"][field] = value
            with self.assertRaises(ValueError):
                reference.validate_manifest(manifest)

    def test_nonfinite_outcome_rejected(self) -> None:
        for field in ("mae_syllables_per_second",
                      "rmse_syllables_per_second",
                      "median_fp32_int8_cosine", "p95_encoder_ms"):
            manifest = reference.control_manifest()
            manifest["outcomes"][field] = float("inf")
            with self.assertRaises(ValueError):
                reference.validate_manifest(manifest)

    def test_out_of_range_cosine_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["outcomes"]["median_fp32_int8_cosine"] = 1.01
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_qualified_claim_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["rights"]["claims_qualified"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_boolean_as_integer_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["weights"]["files"]["model.safetensors"]["byte_count"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_extra_top_level_field_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["extra"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)

    def test_missing_control_rejected(self) -> None:
        manifest = reference.control_manifest()
        manifest["controls"].pop()
        with self.assertRaises(ValueError):
            reference.validate_manifest(manifest)


class ReportTests(unittest.TestCase):
    def test_report_shape_and_decision(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["schema_id"], reference.REPORT_SCHEMA_ID)

    def test_report_has_no_floats(self) -> None:
        reference._no_floats(reference.build_report())

    def test_report_contract_digest_matches(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report()
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))

    def test_report_is_byte_stable(self) -> None:
        first, first_digest = reference.canonical_report(
            reference.build_report())
        second, second_digest = reference.canonical_report(
            reference.build_report())
        self.assertEqual(first, second)
        self.assertEqual(first_digest, second_digest)

    def test_committed_report_matches_generated(self) -> None:
        generated, digest = reference.canonical_report(
            reference.build_report())
        committed = (HERE / "report.json").read_text(encoding="utf-8")
        self.assertEqual(committed, generated)
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            f"{digest}  report.json\n")
        self.assertEqual(digest,
                         hashlib.sha256(committed.encode()).hexdigest())

    def test_committed_contract_matches_generated(self) -> None:
        generated = reference.canonical_bytes(reference.build_contract())
        self.assertEqual((HERE / "contract.json").read_bytes(), generated)

    def test_report_sections_match_contract(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report()
        self.assertEqual(report["gates"], contract["release_gates"])
        self.assertEqual(report["exact_blockers"],
                         contract["exact_blockers"])
        self.assertEqual(report["required_artifacts"],
                         contract["required_artifacts"])
        self.assertEqual(report["rate_profile"]["rows"],
                         contract["rate_profile_requirements"])
        self.assertEqual(report["quality_outcomes"]["rows"],
                         contract["quality_outcomes"])
        self.assertEqual(report["timing"]["rows"],
                         contract["timing_requirements"])

    def test_admission_summary_is_derived(self) -> None:
        admission = reference.build_report()["admission"]
        cases = admission["cases"]
        self.assertEqual(admission["summary"]["case_count"], len(cases))
        self.assertEqual(admission["summary"]["rejected_count"],
                         sum(1 for case in cases
                             if case["status"] == "rejected"))
        self.assertEqual(admission["summary"]["qualifying_results"], 0)

    def test_board_mutable_fields_absent_from_report(self) -> None:
        text = reference.canonical_text(reference.build_report())
        for field in ('"dispatch_priority"', '"blocked_reason"',
                      '"owner"', '"handoff"'):
            self.assertNotIn(field, text)

    def test_profile_phrases_exist_in_source(self) -> None:
        path = (reference.AUDIO_ROOT /
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
        text = path.read_text(encoding="utf-8")
        rows = [line for line in text.splitlines()
                if line.startswith("| Rate |")]
        self.assertEqual(len(rows), 1)
        for phrase in reference.PROFILE_PHRASES:
            self.assertIn(phrase, rows[0])

    def test_contract_validation(self) -> None:
        reference.validate_contract(reference.build_contract())

    def test_contract_validation_rejects_open_gate(self) -> None:
        contract = reference.build_contract()
        contract["release_gates"][0]["status"] = "open"
        with self.assertRaises(ValueError):
            reference.validate_contract(contract)

    def test_contract_validation_rejects_wrong_gate_count(self) -> None:
        contract = reference.build_contract()
        contract["release_gates"].pop()
        with self.assertRaises(ValueError):
            reference.validate_contract(contract)

    def test_json_round_trip_of_committed_report(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        parsed = json.loads(payload, parse_constant=reference._reject_constant)
        self.assertEqual(reference.canonical_bytes(parsed), payload)


if __name__ == "__main__":
    unittest.main()
