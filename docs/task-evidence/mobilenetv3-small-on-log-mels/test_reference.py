# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest suite for the MobileNetV3-small evidence package.

No network, model, checkpoint, runtime, audio, transcript, syllable label,
feature cache, listening session or device measurement is used. No test is
skipped.
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
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
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

    def test_floats_rejected_from_canonical_output(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"value": 1.5})
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"value": [float("nan")]})

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
            target = root / "data/models/mobilenetv3-small-on-log-mels"
            target.mkdir(parents=True)
            with self.assertRaises(ValueError):
                reference.absence_probes(
                    root, ("data/models/mobilenetv3-small-on-log-mels",))

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
    def test_artifacts_have_one_present_and_seven_blocked(self) -> None:
        rows = reference.required_artifacts()
        self.assertEqual(len(rows), 8)
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
            self.assertEqual(gate["linked_row"],
                             reference.board_row_projection())

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
        for key in ("weights_present", "checkpoint_present",
                    "feature_cache_present", "runtime_present",
                    "real_result_present", "cv_result",
                    "rate_profile_result", "device_timing_result",
                    "listening_result", "benchmark_result", "release_claim",
                    "missing_result_promoted"):
            self.assertIs(qualification[key], False)


class FrontendReferenceTests(unittest.TestCase):
    def test_geometry_is_exact(self) -> None:
        geometry = reference.frontend_geometry()
        self.assertEqual(geometry["window_samples"], 64000)
        self.assertEqual(geometry["padded_samples"], 64400)
        self.assertEqual(geometry["frames"], 401)
        self.assertEqual(geometry["fft_bins"], 201)
        self.assertEqual(geometry["values_per_window"], 1536)
        self.assertEqual(geometry["cohort_values"], 322560)
        self.assertEqual(geometry["n_fft_ms"], 25)
        self.assertEqual(geometry["hop_ms"], 10)

    def test_resize_axis_is_mass_conserving(self) -> None:
        rows = reference.resize_axis(401, 64)
        self.assertEqual(len(rows), 64)
        for lower, upper, weight_lower, weight_upper in rows:
            self.assertLessEqual(0, lower)
            self.assertLessEqual(lower, upper)
            self.assertLess(upper, 401)
            self.assertEqual(weight_lower + weight_upper, 1)
            self.assertGreaterEqual(weight_lower, 0)
            self.assertGreaterEqual(weight_upper, 0)

    def test_resize_height_axis_is_identity(self) -> None:
        rows = reference.resize_axis(24, 24)
        self.assertEqual(len(rows), 24)
        self.assertTrue(all(lower == dst and weight_lower == 1
                            and weight_upper == 0
                            for dst, (lower, _, weight_lower, weight_upper)
                            in enumerate(rows)))

    def test_resize_rejects_adverse_arguments(self) -> None:
        for args in ((0, 64), (401, 0), (-1, 64), (401.0, 64), (True, 64)):
            with self.assertRaises(ValueError):
                reference.resize_axis(*args)

    def test_resize_summary_is_stable(self) -> None:
        first = reference.resize_summary()
        second = reference.resize_summary()
        self.assertEqual(first, second)
        self.assertEqual(first["cell_count"], 1536)
        self.assertEqual(first["weight_sum_per_axis_row"], "1")
        self.assertEqual(first["width_source_min"], "2.6328125")
        self.assertEqual(first["width_source_max"], "397.3671875")
        self.assertRegex(first["cell_grid_sha256"], r"^[0-9a-f]{64}$")

    def test_frontend_reference_never_claims_execution(self) -> None:
        frontend = reference.frontend_reference()
        self.assertTrue(frontend["all_checks_pass"])
        self.assertIs(frontend["executed_here"], False)
        self.assertIs(frontend["is_feature_reproduction"], False)
        self.assertIs(frontend["feature_cache_present"], False)
        self.assertIs(frontend["frontend_runtime_pinned"], False)


class ProvenanceTests(unittest.TestCase):
    def test_architecture_recipe_checks_pass(self) -> None:
        recipe = reference.architecture_recipe()
        self.assertTrue(recipe["all_checks_pass"])
        self.assertIs(recipe["pretrained_weights_used"], False)
        self.assertIs(recipe["checkpoint_present"], False)
        self.assertIs(recipe["executed_here"], False)

    def test_documented_metrics_are_provenance_only(self) -> None:
        metrics = reference.documented_metrics()
        self.assertTrue(metrics["provenance_only"])
        self.assertFalse(metrics["reproduced_here"])
        self.assertFalse(metrics["used_for_evidence"])
        self.assertFalse(metrics["qualifies"])
        self.assertEqual(metrics["cv_recorded"]["mae"],
                         "2.7566285133361816")
        self.assertEqual(metrics["cv_recorded"]["baseline_mae"],
                         "1.1604056358337402")
        self.assertEqual(metrics["model_recorded"]["parameter_count"],
                         1518593)

    def test_checkpoint_contradiction_is_recorded(self) -> None:
        checkpoint = reference.documented_checkpoint()
        self.assertTrue(checkpoint["documented_in_report"])
        self.assertFalse(checkpoint["present"])
        self.assertTrue(checkpoint["contradiction"])
        self.assertFalse(checkpoint["all_five_fold_checkpoints_present"])

    def test_source_presence_is_fail_closed(self) -> None:
        presence = reference.source_presence()
        self.assertTrue(presence["research_scripts_present"])
        self.assertFalse(presence["documented_checkpoint_present"])
        self.assertFalse(presence["feature_cache_present"])
        self.assertFalse(presence["runtime_present"])
        self.assertFalse(
            presence["exact_source_weights_runtime_conjunction_present"])
        for key in ("weights_used", "runtime_imported", "audio_read",
                    "model_executed"):
            self.assertIs(presence[key], False)


class AdmissionTests(unittest.TestCase):
    def test_control_is_accepted_but_never_qualified(self) -> None:
        control = reference.admission_control()
        self.assertTrue(control["accepted"])
        self.assertFalse(control["qualifies"])
        self.assertTrue(control["synthetic_schema_control_not_evidence"])
        self.assertEqual(control["audio_window_count"], 210)
        self.assertEqual(control["meeting_count"], 2)
        self.assertEqual(control["checkpoint_count"], 5)
        self.assertFalse(control["state_advanced"])
        self.assertFalse(control["runtime_invoked"])
        self.assertFalse(control["audio_read"])
        self.assertFalse(control["weights_loaded"])
        self.assertFalse(control["model_executed"])
        self.assertFalse(control["network_used"])

    def test_all_adverse_cases_are_rejected(self) -> None:
        cases = reference.admission_cases()
        self.assertGreaterEqual(len(cases), 30)
        self.assertTrue(all(case["status"] == "rejected" for case in cases))
        self.assertTrue(all(case["qualifies"] is False for case in cases))
        self.assertTrue(all(case["state_unchanged"] for case in cases))
        self.assertTrue(all(case["code"] for case in cases))
        identifiers = [case["id"] for case in cases]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_specific_adverse_codes(self) -> None:
        codes = {case["mutation"]: case["code"]
                 for case in reference.admission_cases()}
        self.assertEqual(codes["architecture_pretrained"],
                         "architecture_pretrained")
        self.assertEqual(codes["runtime_version:torch"],
                         "runtime_version:torch")
        self.assertEqual(codes["audio_span"], "audio_span")
        self.assertEqual(codes["outcome_nonfinite:mae_syllables_per_second"],
                         "outcome_nonfinite:mae_syllables_per_second")
        self.assertEqual(codes["rights_claims_qualified"],
                         "rights_claims_qualified")

    def test_document_with_nan_outcome_is_rejected(self) -> None:
        document = reference._synthetic_control()
        document["outcomes"]["mae_syllables_per_second"] = float("nan")
        result = reference.admit(document)
        self.assertFalse(result["accepted"])
        self.assertFalse(result["state_advanced"])

    def test_document_with_boolean_number_is_rejected(self) -> None:
        document = reference._synthetic_control()
        document["audio"][0]["active_s"] = True
        result = reference.admit(document)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["code"], "audio_number:active_s")

    def test_missing_control_is_rejected(self) -> None:
        document = reference._synthetic_control()
        document["controls"].pop()
        self.assertEqual(reference.admit(document)["code"], "controls")

    def test_extra_field_is_rejected(self) -> None:
        document = reference._synthetic_control()
        document["extra"] = 1
        self.assertEqual(reference.admit(document)["code"],
                         "admission_fields")

    def test_duplicate_checkpoint_is_rejected(self) -> None:
        document = reference._synthetic_control()
        document["checkpoints"][1]["sha256"] = \
            document["checkpoints"][0]["sha256"]
        self.assertEqual(reference.admit(document)["code"],
                         "checkpoint_duplicate")


class ReportTests(unittest.TestCase):
    def test_report_is_deterministic(self) -> None:
        first = reference.build_report()
        second = reference.build_report()
        self.assertEqual(reference.object_digest(first),
                         reference.object_digest(second))
        self.assertEqual(reference.canonical_report(first),
                         reference.canonical_report(second))

    def test_report_has_no_floats_and_is_canonical(self) -> None:
        report = reference.build_report()
        reference._no_floats(report)
        payload = reference.canonical_bytes(report)
        self.assertTrue(payload.endswith(b"\n"))
        self.assertEqual(payload, reference.canonical_bytes(
            json.loads(payload.decode("ascii"))))

    def test_report_identity_and_status(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(len(report["gates"]), 8)
        self.assertEqual(len(report["exact_blockers"]), 6)
        self.assertEqual(len(report["required_artifacts"]), 8)

    def test_contract_digest_matches_report(self) -> None:
        report = reference.build_report()
        contract = reference.build_contract()
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))
        reference.validate_contract(contract)

    def test_report_copies_contract_sections(self) -> None:
        report = reference.build_report()
        contract = reference.build_contract()
        for key in ("disposition", "qualification", "scope", "boundary",
                    "public_v0_geometry", "exact_model", "frontend_contract",
                    "runtime_recorded", "training_recipe_recorded",
                    "required_results", "non_claims"):
            self.assertEqual(report[key], contract[key])
        self.assertEqual(report["gates"], contract["release_gates"])
        self.assertEqual(report["exact_blockers"], contract["exact_blockers"])
        self.assertEqual(report["required_artifacts"],
                         contract["required_artifacts"])


if __name__ == "__main__":
    unittest.main()
