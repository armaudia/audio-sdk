# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only tests for the WavLM Base+ ridge DEFER package."""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def _write(self, text: str) -> Path:
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        return Path(handle.name)

    def test_canonical_bytes_sorted_compact_terminal_newline(self) -> None:
        payload = reference.canonical_bytes({"b": 1, "a": [True, None]})
        self.assertEqual(payload, b'{"a":[true,null],"b":1}\n')
        self.assertTrue(payload.endswith(b"\n"))

    def test_float_rejected_everywhere(self) -> None:
        with self.assertRaisesRegex(ValueError, "float_not_allowed"):
            reference.canonical_bytes({"x": 1.0})

    def test_duplicate_keys_rejected(self) -> None:
        path = self._write('{"a":1,"a":2}')
        try:
            with self.assertRaisesRegex(ValueError, "json_duplicate_key"):
                reference.read_strict_json(path)
        finally:
            path.unlink()

    def test_nonfinite_constants_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            path = self._write('{"a":' + token + "}")
            try:
                with self.assertRaisesRegex(ValueError, "json_nonfinite"):
                    reference.read_strict_json(path)
            finally:
                path.unlink()

    def test_malformed_and_nonexact_numbers_rejected(self) -> None:
        path = self._write('{"a":1.5}')
        try:
            with self.assertRaisesRegex(ValueError, "float_not_allowed"):
                reference.read_strict_json(path)
        finally:
            path.unlink()


class PinAndPresenceTests(unittest.TestCase):
    def test_source_pins_verify(self) -> None:
        source, boundary = reference.verify_pins()
        self.assertEqual(set(source), set(reference.SOURCE_PINS))
        self.assertEqual(set(boundary), set(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"] for row in source.values()))
        self.assertTrue(all(row["verified"] for row in boundary.values()))

    def test_mutable_board_is_not_pinned(self) -> None:
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)

    def test_board_projection_has_only_stable_fields(self) -> None:
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(tuple(sorted(projection)),
                         tuple(sorted(reference.BOARD_ROW_FIELDS)))
        self.assertEqual(projection["id"], reference.TASK)
        self.assertEqual(projection["component"], reference.COMPONENT_ID)
        for excluded in ("status", "owner", "claim", "review", "handoff",
                         "blocked_reason"):
            self.assertNotIn(excluded, projection)

    def test_board_projection_digest(self) -> None:
        projection = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(reference.board_row_digest(projection),
                         hashlib.sha256(
                             reference.canonical_bytes(projection)).hexdigest())

    def test_documented_model_identity_and_tree(self) -> None:
        self.assertEqual(reference.MODEL_REPO_ID, "microsoft/wavlm-base-plus")
        self.assertEqual(len(reference.MODEL_REVISION), 40)
        self.assertEqual(len(reference.MODEL_FILES), 4)
        self.assertEqual(reference.MODEL_FILE_BYTES["pytorch_model.bin"],
                         377617425)
        self.assertEqual(reference.MODEL_TREE_SHA256,
                         reference._tree_digest(reference.MODEL_FILES))

    def test_weights_runtime_and_license_are_absent(self) -> None:
        presence = reference.source_presence()
        self.assertFalse(presence["weights_present"])
        self.assertFalse(presence["hf_cache_present"])
        self.assertFalse(presence["upstream_source_checkout_present"])
        self.assertFalse(presence["runtime_torch_present"])
        self.assertFalse(presence["runtime_transformers_present"])
        self.assertFalse(presence["runtime_present"])
        self.assertFalse(presence["license_present"])
        self.assertFalse(
            presence["exact_licensed_source_weights_runtime_present"])
        self.assertFalse(presence["admitted"])
        self.assertFalse(presence["weights_used"])
        self.assertFalse(presence["runtime_imported"])
        self.assertFalse(presence["model_executed"])
        self.assertFalse(presence["download_attempted"])
        self.assertFalse(presence["network_used"])

    def test_source_record_has_no_license_value(self) -> None:
        findings = reference.license_marker_probe()
        self.assertEqual(findings["model_license_marker_files"], [])
        self.assertIsNone(findings["source_record_license_value"])
        self.assertFalse(findings["source_record_license_present"])
        self.assertFalse(findings["redistribution_approved"])
        self.assertFalse(findings["commercial_use_approved"])
        self.assertFalse(findings["output_use_defined"])
        self.assertFalse(findings["qualifies"])

    def test_source_pins_include_provenance_and_plan_inputs(self) -> None:
        self.assertIn(reference.RUN_PREFIX + "/wavlm-base-plus_source.json",
                      reference.SOURCE_PINS)
        self.assertIn(
            reference.RUN_PREFIX + "/wavlm-base-plus_fp32_embeddings.npz",
            reference.SOURCE_PINS)
        self.assertIn("audio-benchmark-platform/plan/INVENTORY.json",
                      reference.SOURCE_PINS)


class RidgeArithmeticTests(unittest.TestCase):
    def test_control_is_synthetic_and_never_qualifies(self) -> None:
        control = reference.ridge_control()
        self.assertEqual(
            control["evidence_class"],
            "synthetic_ridge_arithmetic_control_not_evidence")
        self.assertFalse(control["qualifies"])
        self.assertEqual(control["qualifying_results"], 0)
        self.assertEqual(control["alpha"], "10/1")
        self.assertEqual(control["calibration_count"], 18)
        self.assertEqual(control["evaluation_count"], 6)
        self.assertEqual(control["feature_dim"], 4)
        self.assertTrue(control["labels_are_synthetic"])
        for key in ("audio_read", "weights_loaded", "model_executed",
                    "runtime_imported", "network_used"):
            self.assertFalse(control[key], key)

    def test_control_metrics_are_exact_decimal_strings(self) -> None:
        control = reference.ridge_control()
        for group in ("raw_metrics", "nonnegative_clipped",
                      "constant_calibration_mean_baseline"):
            metrics = (control[group]["metrics"] if group != "raw_metrics"
                       else control[group])
            for key, value in metrics.items():
                if key == "pearson_r_squared" and value == "undefined":
                    continue
                self.assertIsInstance(value, str, key)
                self.assertRegex(value, r"^-?(0|[1-9][0-9]*)\.[0-9]{9}$")
        for value in control["predictions_syllables_per_second"]:
            self.assertRegex(value, r"^-?(0|[1-9][0-9]*)\.[0-9]{9}$")
        self.assertEqual(len(control["weights"]), 4)
        self.assertEqual(
            control["nonnegative_clipped"]["negative_prediction_count"], 0)

    def test_ridge_beats_constant_mean_control(self) -> None:
        control = reference.ridge_control()
        ridge = Fraction(
            control["nonnegative_clipped"]["metrics"]
            ["mae_syllables_per_second"])
        baseline = Fraction(
            control["constant_calibration_mean_baseline"]["metrics"]
            ["mae_syllables_per_second"])
        self.assertLess(ridge, baseline)

    def test_ridge_metrics_and_baseline_match_exact_rebuild(self) -> None:
        control = reference.ridge_control()
        text, digest = reference.canonical_report(control)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(hashlib.sha256(text.encode("ascii")).hexdigest(),
                         digest)
        self.assertEqual(control, reference.ridge_control())

    def test_fit_rejects_nonexact_and_invalid_inputs(self) -> None:
        rows = reference._synthetic_rows()
        bad_float = [dict(row) for row in rows]
        bad_float[0] = dict(bad_float[0])
        bad_float[0]["features"] = [0.5, 1.0, 2.0, 3.0]
        with self.assertRaisesRegex(ValueError, "ridge_feature_not_exact"):
            reference.fit_ridge(bad_float, Fraction(10))
        bad_label = [dict(row) for row in rows]
        bad_label[0] = dict(bad_label[0])
        bad_label[0]["label"] = Fraction(0)
        with self.assertRaisesRegex(ValueError, "ridge_label"):
            reference.fit_ridge(bad_label, Fraction(10))
        with self.assertRaisesRegex(ValueError, "ridge_alpha"):
            reference.fit_ridge(rows, Fraction(0))
        with self.assertRaisesRegex(ValueError, "ridge_rows"):
            reference.fit_ridge([], Fraction(10))
        with self.assertRaisesRegex(ValueError, "ridge_dimension"):
            reference.fit_ridge(rows[:1] + [{
                "features": [Fraction(1)], "label": Fraction(1)}],
                Fraction(10))

    def test_predict_rejects_wrong_dimension(self) -> None:
        head = reference.fit_ridge(reference._synthetic_rows()[:18],
                                   Fraction(10))
        with self.assertRaisesRegex(ValueError, "predict_dimension"):
            reference.predict_ridge(head, [Fraction(1)])
        with self.assertRaisesRegex(ValueError, "predict_feature_not_exact"):
            reference.predict_ridge(head, [Fraction(1)] * 3 + [1.0])


class ManifestAdmissionTests(unittest.TestCase):
    def test_schema_control_is_admitted_but_never_qualifies(self) -> None:
        result = reference.validate_manifest(reference._base_manifest())
        self.assertTrue(result["admitted"])
        self.assertFalse(result["qualifies"])
        self.assertEqual(result["evidence_class"],
                         "synthetic_schema_control_not_evidence")
        self.assertEqual(result["window_count"],
                         reference.TOTAL_MANIFEST_WINDOWS)
        self.assertEqual(result["feature_dim"], 4)

    def test_all_adverse_controls_are_rejected_with_exact_code(self) -> None:
        admission = reference.admission_controls()
        self.assertEqual(admission["summary"]["rejected_count"],
                         admission["summary"]["case_count"])
        self.assertTrue(admission["summary"]["all_rejected"])
        self.assertTrue(admission["summary"]["all_codes_match"])
        self.assertEqual(admission["summary"]["qualifying_results"], 0)
        self.assertTrue(admission["control"]["accepted"])
        self.assertFalse(admission["control"]["qualifies"])
        for case in admission["cases"]:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertEqual(case["code"], case["expected_code"], case["id"])
            self.assertTrue(case["state_unchanged"], case["id"])
            self.assertFalse(case["qualifies"], case["id"])

    def test_missing_and_unknown_fields_rejected(self) -> None:
        manifest = reference._base_manifest()
        del manifest["rights"]
        with self.assertRaisesRegex(ValueError, "manifest_fields"):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["extra"] = True
        with self.assertRaisesRegex(ValueError, "manifest_fields"):
            reference.validate_manifest(manifest)

    def test_nonfinite_values_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["outcomes"]["nonfinite_count"] = 1
        with self.assertRaisesRegex(ValueError, "outcome_nonfinite"):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["windows"][0]["features"][0] = "NaN"
        with self.assertRaisesRegex(ValueError, "window_feature_malformed"):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["windows"][0]["features"][0] = "Infinity"
        with self.assertRaisesRegex(ValueError, "window_feature_malformed"):
            reference.validate_manifest(manifest)

    def test_float_and_real_number_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["runtime"]["threads"] = 1.0
        with self.assertRaisesRegex(ValueError, "runtime_threads_not_int"):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["windows"][0]["features"][0] = 0.5
        with self.assertRaisesRegex(ValueError, "window_feature_not_string"):
            reference.validate_manifest(manifest)

    def test_self_qualified_outcome_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["outcomes"]["qualified"] = True
        with self.assertRaisesRegex(ValueError, "outcome_self_qualified"):
            reference.validate_manifest(manifest)

    def test_license_placeholders_rejected(self) -> None:
        for value in (None, "", "UNKNOWN", "NONE", "NOASSERTION"):
            manifest = reference._base_manifest()
            manifest["source"]["license_id"] = value
            with self.assertRaisesRegex(ValueError, "source_license_id"):
                reference.validate_manifest(manifest)

    def test_window_geometry_rejected(self) -> None:
        manifest = reference._base_manifest()
        manifest["windows"][1]["start_sample"] = 64001
        with self.assertRaisesRegex(ValueError, "window_start_misaligned"):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["windows"][1]["start_sample"] = 64160
        with self.assertRaisesRegex(ValueError, "window_contiguous"):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["windows"][0]["end_sample"] = 63999
        with self.assertRaisesRegex(ValueError, "window_end_misaligned"):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["windows"][1]["end_sample"] = 128160
        with self.assertRaisesRegex(ValueError, "window_length"):
            reference.validate_manifest(manifest)

    def test_rights_flags_must_all_be_true(self) -> None:
        for field in reference.RIGHTS_FIELDS:
            manifest = reference._base_manifest()
            manifest["rights"][field] = False
            with self.assertRaisesRegex(ValueError, "rights_" + field):
                reference.validate_manifest(manifest)

    def test_weight_set_must_be_exact(self) -> None:
        manifest = reference._base_manifest()
        manifest["weights"]["files"][0]["name"] = "extra.bin"
        with self.assertRaisesRegex(ValueError, "weight_name"):
            reference.validate_manifest(manifest)
        manifest = reference._base_manifest()
        manifest["weights"]["files"][2]["name"] = "model.safetensors"
        with self.assertRaisesRegex(ValueError, "weights_required_name"):
            reference.validate_manifest(manifest)

    def test_runtime_pins_are_exact(self) -> None:
        for field, value, code in (
                ("python", "3.9", "runtime_python"),
                ("torch", "2.3.0", "runtime_torch"),
                ("transformers", "4.41.0", "runtime_transformers"),
                ("device", "cuda", "runtime_device"),
                ("deterministic", False, "runtime_deterministic"),
                ("offline", False, "runtime_offline")):
            manifest = reference._base_manifest()
            manifest["runtime"][field] = value
            with self.assertRaisesRegex(ValueError, code):
                reference.validate_manifest(manifest)

    def test_admission_never_invokes_runtime_or_reads_audio(self) -> None:
        summary = reference.admission_controls()["summary"]
        for field in ("runtime_invoked", "audio_read", "weights_loaded",
                      "model_executed", "network_used",
                      "state_advanced_on_rejection"):
            self.assertFalse(summary[field], field)


class ContractReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = reference.build_contract()
        cls.report = reference.build_report()

    def test_contract_disposition(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["status"], "incomplete")
        self.assertEqual(self.contract["qualification_status"],
                         "not_qualified")
        self.assertTrue(self.contract["proposal_only"])
        self.assertFalse(self.contract["board_file_pinned"])
        reference.validate_contract(self.contract)

    def test_report_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["qualification"]["qualifying_results"], 0)
        self.assertFalse(report["qualification"]["weights_present"])
        self.assertFalse(report["qualification"]["license_present"])
        self.assertFalse(report["qualification"]["real_result_present"])

    def test_eight_blocked_release_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        for index, gate in enumerate(gates, start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"],
                             self.report["linked_row_identity"]["projection"])

    def test_six_open_blockers(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        artifact_ids = {row["id"] for row in self.report["required_artifacts"]}
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertIn("missing", blocker)
            self.assertTrue(blocker["required_action"])

    def test_artifacts_are_pinned_or_absent_and_blocked(self) -> None:
        artifacts = {row["id"]: row for row in
                     self.report["required_artifacts"]}
        self.assertEqual(len(artifacts), 10)
        present = artifacts["A01"]
        self.assertTrue(present["present"])
        self.assertTrue(present["verified"])
        self.assertFalse(present["licensed"])
        self.assertFalse(present["admitted"])
        self.assertTrue(present["blocked"])
        for artifact_id in ("A02", "A03", "A04", "A05", "A06", "A07",
                            "A08", "A09", "A10"):
            row = artifacts[artifact_id]
            self.assertFalse(row["present"], artifact_id)
            self.assertFalse(row["admitted"], artifact_id)
            self.assertTrue(row["blocked"], artifact_id)
            self.assertIsNone(row["sha256"], artifact_id)

    def test_exact_model_is_documented_not_present(self) -> None:
        model = self.report["exact_model"]
        self.assertEqual(model["repo_id"], reference.MODEL_REPO_ID)
        self.assertEqual(model["revision"], reference.MODEL_REVISION)
        self.assertIsNone(model["license"])
        self.assertFalse(model["locally_present"])
        self.assertFalse(model["downloaded_or_reconstructed"])
        self.assertFalse(model["files_documented_locally_verified"])
        self.assertEqual(model["weight_bytes"], 377617425)
        self.assertEqual(set(model["files"]),
                         {"README.md", "config.json",
                          "preprocessor_config.json", "pytorch_model.bin"})

    def test_documented_context_is_not_reproduced(self) -> None:
        context = self.report["observed_provenance"]["documented_context"]
        self.assertFalse(context["reproduced_here"])
        self.assertFalse(context["weights_used_here"])
        self.assertFalse(context["runtime_imported_here"])
        self.assertFalse(context["audio_read_here"])
        self.assertEqual(context["reported"]["rate_mae_syllables_per_second"],
                         "0.609")
        self.assertEqual(context["reported"]["meeting_count"], 1)

    def test_eight_rate_requirements_and_outcomes_are_blocked(self) -> None:
        rows = self.report["rate_profile"]["rows"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(row["status"], "blocked")
            self.assertFalse(row["qualifies"])
        outcomes = self.report["rate_outcomes"]["rows"]
        self.assertEqual(len(outcomes), 8)
        for row in outcomes:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])
            self.assertFalse(row["qualifies"])

    def test_required_results_never_promote(self) -> None:
        results = self.report["required_results"]
        self.assertTrue(results["no_result_qualifies"])
        for key, value in results.items():
            if key != "no_result_qualifies":
                self.assertFalse(value, key)

    def test_report_is_canonical_and_float_free(self) -> None:
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(hashlib.sha256(text.encode("ascii")).hexdigest(),
                         digest)
        self.assertTrue(text.endswith("\n"))
        reference._no_floats(self.report)

    def test_contract_digest_matches(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         reference.object_digest(self.contract))

    def test_linked_row_identity_projection(self) -> None:
        identity = self.report["linked_row_identity"]
        self.assertEqual(identity["projection"],
                         reference.board_row_projection(
                             reference.AUDIO_ROOT /
                             reference.BOARD_TASK_ROW))
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["linked_rows"],
                         [dict(row) for row in reference.LINKED_ROWS])

    def test_scope_flags_are_all_negative(self) -> None:
        scope = self.report["scope"]
        for key, value in scope.items():
            if key in ("task_local_only", "directory"):
                continue
            self.assertFalse(value, key)

    def test_no_forbidden_artifacts_in_package(self) -> None:
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(),
                             reference.FORBIDDEN_SUFFIXES, path.name)
            self.assertFalse(path.is_symlink(), path.name)
            self.assertNotIn(path.name,
                             {"LICENSE", "LICENSE.txt", "COPYING", "NOTICE"})


class RegenerationTests(unittest.TestCase):
    def test_committed_sources_manifest_verifies(self) -> None:
        path = HERE / "SOURCES.sha256"
        self.assertTrue(path.is_file())
        reference.verify_sources_manifest(path.read_bytes())
        self.assertEqual(path.read_bytes(), run.sources_bytes())

    def test_committed_report_matches_build(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        text, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(payload, text.encode("ascii"))
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), digest + "  report.json\n")


if __name__ == "__main__":
    unittest.main()
