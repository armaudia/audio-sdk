# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest suite for the WavLM acoustic disfluency package.

No network, model, weight, runtime, audio, transcript, frame label, listening
session or device measurement is used. No test is skipped.
"""

from __future__ import annotations

import copy
import hashlib
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

    def test_repository_head_matches_declared_commit(self) -> None:
        repository = (reference.AUDIO_ROOT /
                      "data/checkouts/disfluency_detection_from_audio")
        head = reference.repository_head(repository)
        self.assertEqual(head, reference.UPSTREAM_COMMIT)
        self.assertRegex(head, r"^[0-9a-f]{40}$")

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
        self.assertEqual(len(rows), 15)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_home_absence_probes_are_all_absent(self) -> None:
        rows = reference.home_absence_probes()
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_present_probe_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "data/models/disfluency"
            target.mkdir(parents=True)
            with self.assertRaises(ValueError):
                reference.absence_probes(root, ("data/models/disfluency",))

    def test_absence_summary_counts(self) -> None:
        summary = reference.absence_summary(
            reference.absence_probes(reference.AUDIO_ROOT),
            reference.home_absence_probes())
        self.assertEqual(summary["probe_count"], 19)
        self.assertEqual(summary["workspace_probe_count"], 15)
        self.assertEqual(summary["home_probe_count"], 4)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])

    def test_absence_summary_never_claims_use(self) -> None:
        summary = reference.absence_summary([], [])
        for key in ("download_attempted", "network_used",
                    "recursive_workspace_walk", "source_or_runtime_imported",
                    "weights_loaded", "model_executed", "audio_read"):
            self.assertIs(summary[key], False)

    def test_source_inventory_declares_no_license(self) -> None:
        inventory = reference.source_inventory()
        self.assertEqual(inventory["head_commit"], reference.UPSTREAM_COMMIT)
        self.assertTrue(inventory["head_matches"])
        self.assertIsNone(inventory["license"])
        self.assertEqual(inventory["license_status"], "not_declared")
        self.assertEqual(inventory["license_files_present"], [])
        self.assertFalse(inventory["license_declared_in_readme"])
        self.assertFalse(inventory["terms_reviewed"])
        self.assertEqual(inventory["model_definition"]["labels"],
                         list(reference.LABELS))

    def test_smoke_runner_provenance(self) -> None:
        provenance = reference.smoke_runner_provenance()
        self.assertEqual(provenance["snippets_present"], 6)
        self.assertEqual(provenance["config_revision"],
                         reference.SMOKE_CONFIG_REVISION)
        self.assertIsNone(provenance["config_license"])
        self.assertIs(provenance["executed_here"], False)
        self.assertIs(provenance["downloaded"], False)


class ArtifactAndGateTests(unittest.TestCase):
    def test_artifacts_include_unlicensed_source_and_six_blocked(self) -> None:
        rows = reference.REQUIRED_ARTIFACTS
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0]["id"], "ART-01")
        self.assertTrue(rows[0]["present"])
        self.assertFalse(rows[0]["blocked"])
        self.assertEqual(rows[1]["id"], "ART-02")
        self.assertTrue(rows[1]["present"])
        self.assertTrue(rows[1]["blocked"])
        for row in rows[2:]:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])

    def test_eight_gates_are_blocked(self) -> None:
        self.assertEqual(len(reference.RELEASE_GATES), 8)
        for index, gate in enumerate(reference.RELEASE_GATES, start=1):
            self.assertEqual(gate["id"], f"RG-{index:02d}")
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen_condition"])

    def test_six_blockers_are_open(self) -> None:
        self.assertEqual(len(reference.EXACT_BLOCKERS), 6)
        artifact_ids = {row["id"] for row in reference.REQUIRED_ARTIFACTS}
        gate_ids = {row["id"] for row in reference.RELEASE_GATES}
        for blocker in reference.EXACT_BLOCKERS:
            self.assertEqual(blocker["status"], "open")
            self.assertIs(blocker["qualifies"], False)
            self.assertIn(blocker["artifact_id"], artifact_ids)
            self.assertTrue(blocker["required_action"])
            for gate in blocker["linked_gates"]:
                self.assertIn(gate, gate_ids)

    def test_rate_profile_rows_are_blocked(self) -> None:
        self.assertEqual(len(reference.RATE_PROFILE_ROWS), 8)
        for row in reference.RATE_PROFILE_ROWS:
            self.assertEqual(row["status"], "blocked")

    def test_quality_and_timing_rows_have_no_values(self) -> None:
        self.assertEqual(len(reference.QUALITY_ROWS), 4)
        self.assertEqual(len(reference.TIMING_ROWS), 4)
        for row in reference.QUALITY_ROWS + reference.TIMING_ROWS:
            self.assertEqual(row["status"], "blocked")
            self.assertIsNone(row["value"])

    def test_qualification_never_claims(self) -> None:
        contract = reference.build_contract()
        qualification = contract["qualification"]
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")
        self.assertIs(contract["proposal_only"], True)
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertIs(qualification["not_qualified"], True)
        self.assertIs(qualification["all_release_gates_blocked"], True)
        for key in ("real_result_present", "weights_present",
                    "backbone_present", "runtime_present",
                    "frame_labels_present", "accuracy_result",
                    "detection_quality_result", "onset_delay_result",
                    "device_timing_result", "rate_profile_result",
                    "listening_result", "benchmark_result", "release_claim",
                    "missing_result_promoted", "source_licensed"):
            self.assertIs(qualification[key], False, key)

    def test_exact_model_is_absent_and_not_downloaded(self) -> None:
        model = reference.build_contract()["exact_model"]
        checkpoint = model["checkpoint"]
        self.assertFalse(checkpoint["locally_present"])
        self.assertFalse(checkpoint["downloaded_or_reconstructed"])
        self.assertEqual(checkpoint["byte_count"],
                         str(reference.CHECKPOINT_BYTES))
        self.assertEqual(checkpoint["sha256"], reference.CHECKPOINT_SHA256)
        self.assertFalse(model["backbone"]["config_present"])
        self.assertFalse(model["backbone"]["weights_present"])
        self.assertIsNone(model["backbone"]["smoke_config_license"])
        self.assertFalse(model["locally_present"])

    def test_documented_smoke_is_provenance_only(self) -> None:
        smoke = reference.documented_smoke()
        self.assertEqual(smoke["frame_count"], 199)
        self.assertEqual(smoke["cpu_model_only_ms"],
                         reference.CPU_MODEL_ONLY_MS)
        self.assertEqual(smoke["positive_frame_count_per_label"],
                         reference.POSITIVE_FRAMES)
        self.assertIs(smoke["provenance_only"], True)
        for key in ("reproduced_here", "used_for_evidence", "qualifies"):
            self.assertIs(smoke[key], False)

    def test_source_presence_never_uses_assets(self) -> None:
        presence = reference.source_presence()
        self.assertIs(presence["upstream_repository_present"], True)
        self.assertIs(presence["upstream_license_present"], False)
        self.assertIs(presence["checkpoint_present"], False)
        self.assertIs(presence["backbone_config_present"], False)
        self.assertIs(presence["runtime_present"], False)
        self.assertIs(
            presence["exact_source_weights_runtime_licensed_conjunction_present"],
            False)
        self.assertIs(
            presence["audio_clip_recorded_in_research_bundle"], True)
        for key in ("weights_used", "runtime_imported", "audio_read",
                    "model_executed", "downloaded_or_reconstructed"):
            self.assertIs(presence[key], False)


class AdmissionTests(unittest.TestCase):
    def test_control_is_accepted_and_not_qualified(self) -> None:
        control = reference.control_manifest()
        reference.validate_manifest(control)
        self.assertIs(control["rights"]["claims_qualified"], False)
        self.assertEqual(control["labels"]["names"], list(reference.LABELS))

    def test_non_object_manifest_rejected(self) -> None:
        for value in ([], 1, None, "x"):
            with self.assertRaises(ValueError):
                reference.validate_manifest(value)

    def test_every_admission_mutation_is_rejected(self) -> None:
        control = reference.control_manifest()
        for case_id, _description, mutate in reference._mutation_cases():
            candidate = copy.deepcopy(control)
            if case_id == "ADM-01":
                candidate = []
            else:
                mutate(candidate)
            with self.assertRaises(ValueError, msg=case_id):
                reference.validate_manifest(candidate)

    def test_missing_weight_rejected(self) -> None:
        control = reference.control_manifest()
        control["weights"].pop("file")
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_wrong_weight_digest_rejected(self) -> None:
        control = reference.control_manifest()
        control["weights"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_wrong_weight_size_rejected(self) -> None:
        control = reference.control_manifest()
        control["weights"]["byte_count"] = reference.CHECKPOINT_BYTES + 1
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_unlicensed_source_rejected(self) -> None:
        control = reference.control_manifest()
        control["source"]["license_id"] = "none"
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_nonfinite_audio_start_rejected(self) -> None:
        control = reference.control_manifest()
        control["audio"][0]["start_s"] = float("nan")
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_wrong_runtime_rejected(self) -> None:
        control = reference.control_manifest()
        control["runtime"]["torch"] = "1.12.1"
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_human_label_claim_rejected(self) -> None:
        control = reference.control_manifest()
        control["labels"]["human_verified"] = False
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_duplicate_audio_id_rejected(self) -> None:
        control = reference.control_manifest()
        control["audio"][1]["id"] = control["audio"][0]["id"]
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_relative_audio_path_rejected(self) -> None:
        control = reference.control_manifest()
        control["audio"][0]["path"] = "relative.wav"
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_wrong_window_span_rejected(self) -> None:
        control = reference.control_manifest()
        control["audio"][0]["end_s"] = 3.0
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_nonfinite_outcome_rejected(self) -> None:
        control = reference.control_manifest()
        control["outcomes"]["per_label"][0]["precision"] = float("inf")
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_out_of_range_f1_rejected(self) -> None:
        control = reference.control_manifest()
        control["outcomes"]["per_label"][0]["f1"] = 2
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_qualified_claim_rejected(self) -> None:
        control = reference.control_manifest()
        control["rights"]["claims_qualified"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_boolean_as_integer_rejected(self) -> None:
        control = reference.control_manifest()
        control["outcomes"]["frame_count"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_extra_top_level_field_rejected(self) -> None:
        control = reference.control_manifest()
        control["unexpected"] = True
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_missing_control_rejected(self) -> None:
        control = reference.control_manifest()
        control["controls"].pop()
        with self.assertRaises(ValueError):
            reference.validate_manifest(control)

    def test_admission_summary_is_derived(self) -> None:
        admission = reference.build_admission()
        cases = reference.admission_cases()
        self.assertEqual(admission["cases"], cases)
        self.assertEqual(len(cases), 77)
        self.assertEqual(admission["summary"]["case_count"], len(cases))
        self.assertEqual(admission["summary"]["rejected_count"], len(cases))
        self.assertEqual(admission["summary"]["accepted_schema_controls"], 1)
        self.assertEqual(admission["summary"]["qualifying_results"], 0)
        self.assertIs(admission["control"]["qualifies"], False)
        self.assertIs(admission["control"]["accepted"], True)


class ReportTests(unittest.TestCase):
    def test_report_shape_and_decision(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["schema_id"], reference.REPORT_SCHEMA_ID)
        self.assertEqual(report["task"], reference.TASK)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIs(report["proposal_only"], True)

    def test_report_has_no_floats(self) -> None:
        reference._no_floats(reference.build_report())

    def test_report_contract_digest_matches(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report()
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))

    def test_report_is_byte_stable(self) -> None:
        first = reference.canonical_bytes(reference.build_report())
        second = reference.canonical_bytes(reference.build_report())
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))

    def test_committed_report_matches_generated(self) -> None:
        path = HERE / "report.json"
        self.assertTrue(path.is_file())
        committed = path.read_bytes()
        generated = reference.canonical_bytes(reference.build_report())
        self.assertEqual(committed, generated)
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar,
                         f"{hashlib.sha256(committed).hexdigest()}  "
                         "report.json\n")

    def test_committed_contract_matches_generated(self) -> None:
        path = HERE / "contract.json"
        self.assertTrue(path.is_file())
        self.assertEqual(path.read_bytes(),
                         reference.canonical_bytes(
                             reference.build_contract()))

    def test_report_sections_match_contract(self) -> None:
        contract = reference.build_contract()
        report = reference.build_report()
        self.assertEqual(report["qualification"], contract["qualification"])
        self.assertEqual(report["required_artifacts"],
                         contract["required_artifacts"])
        self.assertEqual(report["exact_blockers"],
                         contract["exact_blockers"])
        self.assertEqual(report["gates"], contract["release_gates"])
        self.assertEqual(report["rate_profile"]["rows"],
                         contract["rate_profile_requirements"])
        self.assertEqual(report["quality_outcomes"]["rows"],
                         contract["quality_outcomes"])
        self.assertEqual(report["timing"]["rows"],
                         contract["timing_requirements"])
        self.assertEqual(report["exact_source"], contract["exact_source"])
        self.assertEqual(report["exact_model"], contract["exact_model"])

    def test_board_mutable_fields_absent_from_boundary(self) -> None:
        report = reference.build_report()
        projection = report["linked_row_identity"]["projection"]
        for field in ("status", "owner", "claim", "review", "handoff",
                      "blocked_reason", "dispatch_priority"):
            self.assertNotIn(field, projection)
        self.assertIs(report["linked_row_identity"]["board_file_pinned"], False)
        self.assertIs(
            report["linked_row_identity"]["board_status_gates_anything"], False)
        self.assertEqual(report["linked_row_identity"]["gating"],
                         "stable_identity_only")

    def test_report_absence_summary(self) -> None:
        summary = reference.build_report()["absence_evidence"]["summary"]
        self.assertEqual(summary["probe_count"], 19)
        self.assertEqual(summary["present_count"], 0)
        self.assertIs(summary["all_probes_absent"], True)
        self.assertIs(summary["audio_read"], False)

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
        contract = copy.deepcopy(reference.build_contract())
        contract["release_gates"][0]["status"] = "open"
        with self.assertRaises(ValueError):
            reference.validate_contract(contract)

    def test_contract_validation_rejects_wrong_gate_count(self) -> None:
        contract = copy.deepcopy(reference.build_contract())
        contract["release_gates"].pop()
        with self.assertRaises(ValueError):
            reference.validate_contract(contract)

    def test_contract_validation_rejects_licensed_source(self) -> None:
        contract = copy.deepcopy(reference.build_contract())
        contract["qualification"]["source_licensed"] = True
        with self.assertRaises(ValueError):
            reference.validate_contract(contract)

    def test_json_round_trip_of_committed_report(self) -> None:
        text = (HERE / "report.json").read_text(encoding="utf-8")
        parsed = reference.loads_strict(text)
        self.assertEqual(parsed, reference.build_report())


if __name__ == "__main__":
    unittest.main()
