# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance tests for the CoF denoising evidence bundle."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            reference.loads_strict('{"a":1,"a":2}')

    def test_nan_constant_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonfinite_json_constant"):
            reference.loads_strict('{"a":NaN}')

    def test_infinity_constant_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonfinite_json_constant"):
            reference.loads_strict('{"a":Infinity}')

    def test_root_array_rejected(self):
        with self.assertRaisesRegex(ValueError, "json_root_not_object"):
            reference.loads_strict("[]")

    def test_byte_order_mark_rejected(self):
        with self.assertRaisesRegex(ValueError, "json_byte_order_mark"):
            reference.loads_strict('\ufeff{"a":1}')

    def test_canonical_is_sorted_compact_and_newline_terminated(self):
        text = reference.canonical_text({"b": 1, "a": [2, 3]})
        self.assertEqual(text, '{"a":[2,3],"b":1}\n')
        self.assertNotIn(" ", text)


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_match(self):
        rows = reference.pin_rows(reference.SOURCE_PINS, reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.SOURCE_PINS))
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_boundary_pins_match(self):
        rows = reference.pin_rows(reference.BOUNDARY_PINS,
                                  reference.WORKTREE)
        self.assertEqual(len(rows), len(reference.BOUNDARY_PINS))
        self.assertEqual(len(rows), 13)
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_board_projection_has_only_stable_fields(self):
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(tuple(sorted(row)), tuple(sorted(
            reference.BOARD_ROW_FIELDS)))
        self.assertEqual(row["id"], reference.TASK)
        self.assertEqual(row["component"], reference.COMPONENT_ID)
        self.assertEqual(row["mode"], "feasibility")
        for mutable in ("status", "owner", "claim", "review", "handoff",
                        "blocked_reason", "dispatch_priority"):
            self.assertNotIn(mutable, row)

    def test_board_row_digest_ignores_mutable_fields(self):
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        expected = hashlib.sha256(reference.canonical_bytes(row)).hexdigest()
        self.assertEqual(reference.board_row_digest(row), expected)
        mutated = dict(row)
        mutated["status"] = "done"
        mutated["owner"] = "someone-else"
        self.assertEqual(reference.board_row_digest(
            reference.board_row_projection(
                reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)),
            expected)

    def test_linked_rows_are_declared_dependencies(self):
        rows = reference.linked_rows()
        self.assertEqual([row["id"] for row in rows],
                         list(reference.LINKED_ROW_IDS))
        self.assertEqual(rows[0]["depends_on"],
                         ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE",
                          "SDK-FND-PROVIDER"])

    def test_board_file_is_not_a_pin(self):
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.SOURCE_PINS)
        self.assertNotIn(reference.BOARD_TASK_ROW, reference.BOUNDARY_PINS)


class AbsenceTests(unittest.TestCase):
    def test_workspace_probes_absent(self):
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_worktree_probes_absent(self):
        rows = reference.worktree_absence_probes()
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_home_probes_absent(self):
        rows = reference.home_absence_probes()
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_absence_summary_totals(self):
        summary = reference.absence_summary(
            reference.absence_probes(reference.AUDIO_ROOT),
            reference.worktree_absence_probes(),
            reference.home_absence_probes())
        self.assertEqual(summary["probe_count"], 27)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])
        for key in ("download_attempted", "network_used",
                    "recursive_workspace_walk", "source_or_runtime_imported",
                    "weights_loaded", "model_executed", "audio_read"):
            self.assertFalse(summary[key])

    def test_runtime_modules_are_absent(self):
        readiness = reference.runtime_readiness()
        self.assertFalse(readiness["importable"])
        self.assertFalse(readiness["module_spec_found"])
        self.assertTrue(readiness["blocked"])
        self.assertFalse(readiness["runtime_imported"])
        self.assertIsNone(readiness["recorded_runtime"])
        self.assertFalse(readiness["runtime_versions_recorded"])
        self.assertEqual(readiness["exact_error"],
                         "ModuleNotFoundError: No module named 'torch'")
        self.assertEqual(len(readiness["modules"]),
                         len(reference.RUNTIME_MODULES))
        self.assertTrue(all(not row["module_spec_found"]
                            for row in readiness["modules"]))

    def test_runtime_interpreter_matches_pinned_verifier(self):
        if reference.platform.python_version() == \
                reference.REQUIRED_INTERPRETER:
            self.assertTrue(reference.runtime_readiness()
                            ["interpreter_matches"])


class EvidencePresenceTests(unittest.TestCase):
    def test_inventory_record_is_pinned_and_consistent(self):
        record = reference.inventory_record()
        self.assertEqual(record["id"], reference.COMPONENT_ID)
        self.assertEqual(record["name"], reference.TASK_TITLE)
        self.assertEqual(record["area"], "Enhancement")
        self.assertEqual(record["disposition"], "sdk-model")
        self.assertEqual(record["verification_profile"], "enhancement")
        self.assertEqual(record["task"], reference.TASK)
        self.assertEqual(record["evidence_line"], 62)
        self.assertTrue(record["verified"])

    def test_evidence_snippets_are_present(self):
        rows = reference.evidence_snippet_check()
        self.assertEqual(set(rows), set(reference.EVIDENCE_SNIPPETS))
        for row in rows.values():
            self.assertTrue(row["verified"])
            self.assertEqual(row["snippets_required"],
                             row["snippets_found"])

    def test_evidence_presence_never_claims_assets(self):
        presence = reference.evidence_presence()
        self.assertTrue(presence["evidence_register_present"])
        self.assertTrue(presence["inventory_record_present"])
        self.assertTrue(presence["census_source_present"])
        for key in ("source_present", "source_identity_recorded",
                    "runtime_present", "runtime_pinned", "weights_present",
                    "weights_identified", "input_media_present",
                    "exact_source_runtime_weights_conjunction_present",
                    "runtime_imported", "weights_loaded", "model_executed",
                    "audio_read", "network_used"):
            self.assertFalse(presence[key])

    def test_checkpoint_scope_has_no_identity(self):
        presence = reference.checkpoint_presence()
        self.assertEqual(presence["row_count"], 4)
        self.assertFalse(presence["artifact_count_asserted"])
        for key in ("file_names_recorded", "revisions_recorded",
                    "byte_counts_recorded", "sha256_values_recorded",
                    "any_checkpoint_present"):
            self.assertFalse(presence[key])
        for row in presence["rows"]:
            self.assertIsNone(row["file_names"])
            self.assertIsNone(row["revision"])
            self.assertIsNone(row["byte_count"])
            self.assertIsNone(row["sha256"])
            self.assertFalse(row["present"])
            self.assertFalse(row["formulation_files_mapped"])

    def test_enhancement_profile_row_is_pinned(self):
        row = reference.profile_row_check()
        self.assertEqual(row["profile"], "enhancement")
        self.assertEqual(row["label"], "Enhancement")
        self.assertTrue(row["verified"])
        self.assertEqual(row["required_phrases"], 5)
        self.assertEqual(row["phrases_found"], 5)


class AdmissionTests(unittest.TestCase):
    def test_control_manifest_is_accepted_without_mutation(self):
        manifest = reference.control_manifest()
        before = copy.deepcopy(manifest)
        reference.validate_manifest(manifest)
        self.assertEqual(manifest, before)

    def test_all_rejection_cases_reject(self):
        cases = reference.admission_cases()
        self.assertEqual(len(cases), 90)
        self.assertEqual(len({case["id"] for case in cases}), 90)
        for case in cases:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertTrue(case["code"])

    def test_representative_rejection_codes(self):
        codes = {case["id"]: case["code"]
                 for case in reference.admission_cases()}
        self.assertEqual(codes["DOC-01"], "duplicate_json_key")
        self.assertEqual(codes["DOC-02"], "nonfinite_json_constant")
        self.assertEqual(codes["MD-05"], "model_formulation_not_allowed")
        self.assertEqual(codes["MD-14"], "model_padding_profile_not_text")
        self.assertEqual(codes["RT-01"], "runtime_python_invalid")
        self.assertEqual(codes["AS-05"], "assets[0]_sha256_not_sha256")
        self.assertEqual(codes["RI-01"],
                         "rights_claims_qualified_wrong_value")
        self.assertEqual(codes["NF-01"], "output_peak_nonfinite")

    def test_admission_summary_never_qualifies(self):
        admission = reference.build_admission()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], 90)
        self.assertEqual(summary["rejected_count"], 90)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertEqual(admission["control"]["label"],
                         "synthetic_schema_control_not_evidence")
        self.assertFalse(admission["control"]["qualifies"])

    def test_missing_invalid_and_nonfinite_rejected(self):
        for mutate, pattern in (
                (lambda row: row["model"].pop("stage"),
                 "model_missing_field"),
                (lambda row: row["runtime"].update(device="tpu"),
                 "runtime_device_not_allowed"),
                (lambda row: row["command"].update(network="allowed"),
                 "command_network"),
                (lambda row: row["assets"][0].update(sha256="x"),
                 r"assets\[0\]_sha256_not_sha256"),
                (lambda row: row["output"].update(peak=float("nan")),
                 "output_peak_nonfinite"),
                (lambda row: row["rights"].update(claims_qualified=True),
                 "rights_claims_qualified_wrong_value")):
            manifest = reference.control_manifest()
            mutate(manifest)
            with self.assertRaisesRegex(reference.AdmissionError, pattern):
                reference.validate_manifest(manifest)

    def test_unknown_model_and_stage_rejected(self):
        for formulation in ("gan", "waveform", ""):
            manifest = reference.control_manifest()
            manifest["model"]["formulation"] = formulation
            with self.assertRaises(reference.AdmissionError):
                reference.validate_manifest(manifest)
        manifest = reference.control_manifest()
        manifest["model"]["stage"] = "fine_tuned"
        with self.assertRaisesRegex(reference.AdmissionError, "stage"):
            reference.validate_manifest(manifest)


class EnvelopeTests(unittest.TestCase):
    def test_request_validation_returns_exact_payload(self):
        request = reference.protocol_request()
        payload = reference.validate_protocol_request(request)
        self.assertEqual(payload, reference.frame_bytes(
            reference.synthetic_frame()))
        self.assertEqual(len(payload), reference.FRAME_BYTES)

    def test_typical_use_is_identity_replay_and_reset(self):
        probe = reference.synthetic_envelope_probe()
        use = probe["typical_api_use"]
        self.assertEqual(use["status"], "synthetic_pass")
        self.assertTrue(use["identity_exact"])
        self.assertTrue(use["replay_identical"])
        self.assertTrue(use["reset_replay_identical"])
        self.assertTrue(use["close_idempotent"])
        self.assertTrue(use["run_after_close_rejected"])
        self.assertFalse(use["timing_measured"])
        self.assertFalse(use["runtime_invoked"])
        self.assertFalse(use["weights_loaded"])
        self.assertFalse(use["model_executed"])
        self.assertFalse(use["audio_read"])
        self.assertFalse(use["qualifies"])
        self.assertEqual(use["output_peak"], "0.78125")

    def test_all_envelope_cases_reject_without_advancing(self):
        cases = reference.envelope_cases()
        self.assertEqual(len(cases), 20)
        self.assertEqual(len({case["id"] for case in cases}), 20)
        for case in cases:
            self.assertEqual(case["status"], "rejected")
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
            self.assertEqual(case["calls_after_rejection"], 0)
            self.assertTrue(case["code"])

    def test_nonfinite_payload_and_bad_hex_rejected(self):
        codes = {case["id"]: case["code"]
                 for case in reference.envelope_cases()}
        self.assertEqual(codes["EV-16"], "payload_nonfinite")
        self.assertEqual(codes["EV-19"], "payload_hex_invalid")

    def test_lifecycle_after_close_rejected(self):
        probe = reference.synthetic_envelope_probe()
        self.assertEqual(probe["lifecycle"]["status"], "rejected")
        self.assertEqual(probe["lifecycle"]["code"], "adapter_closed")
        self.assertFalse(probe["lifecycle"]["qualifies"])
        self.assertEqual(probe["summary"]["case_count"], 20)
        self.assertEqual(probe["summary"]["rejected_count"], 20)
        self.assertEqual(probe["summary"]["accepted_schema_controls"], 1)
        self.assertEqual(probe["summary"]["qualifying_results"], 0)


class ContractReportTests(unittest.TestCase):
    def test_contract_shape_and_gates(self):
        contract = reference.build_contract()
        reference.validate_contract(contract)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")
        self.assertTrue(contract["proposal_only"])
        self.assertEqual(contract["qualification_status"], "not_qualified")
        self.assertEqual(len(contract["release_gates"]), 8)
        for index, gate in enumerate(contract["release_gates"], start=1):
            self.assertEqual(gate["id"], "RG-%02d" % index)
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])

    def test_contract_artifacts_and_blockers(self):
        contract = reference.build_contract()
        artifacts = contract["required_artifacts"]
        self.assertEqual(len(artifacts), 7)
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        for row in artifacts[1:]:
            self.assertFalse(row["present"])
            self.assertFalse(row["verified"])
            self.assertTrue(row["blocked"])
            self.assertIsNone(row["sha256"])
        blockers = contract["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertTrue(blocker["required_action"])

    def test_contract_scope_is_task_local(self):
        contract = reference.build_contract()
        self.assertTrue(contract["scope"]["task_local_only"])
        for key in ("provider_registered", "reference_implemented",
                    "reference_executed", "public_abi_changed",
                    "installed_v0_changed", "registry_or_default_changed",
                    "shared_build_or_ci_changed", "real_assets_used",
                    "network_used", "listening_performed",
                    "device_timing_measured", "benchmark_run",
                    "release_claim"):
            self.assertFalse(contract["scope"][key])

    def test_qualification_never_promotes_missing_results(self):
        qualification = reference.qualification()
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertTrue(qualification["not_qualified"])
        self.assertTrue(qualification["all_release_gates_blocked"])
        self.assertFalse(qualification["missing_result_promoted"])
        self.assertFalse(qualification["release_claim"])
        for key in ("source_present", "source_identity_recorded",
                    "runtime_present", "runtime_pinned", "weights_present",
                    "weights_identified", "input_media_present",
                    "implementation_present", "reference_execution_result",
                    "output_validity_result", "enhancement_profile_result",
                    "device_timing_result", "listening_result",
                    "benchmark_result"):
            self.assertFalse(qualification[key])

    def test_report_is_canonical_and_float_free(self):
        report = reference.build_report()
        text, digest = reference.canonical_report(report)
        self.assertEqual(text, reference.canonical_text(report))
        self.assertEqual(digest, hashlib.sha256(
            text.encode("utf-8")).hexdigest())
        reference._no_floats(report)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["qualification_status"], "not_qualified")

    def test_report_evidence_and_profile_counts(self):
        report = reference.build_report()
        self.assertEqual(report["absence_evidence"]["summary"]["probe_count"],
                         27)
        self.assertEqual(
            report["enhancement_profile"]["row_summary"]["real_result_count"],
            0)
        self.assertFalse(
            report["enhancement_profile"]["row_summary"]["profile_satisfied"])
        self.assertEqual(report["admission"]["summary"]["rejected_count"], 90)
        self.assertEqual(
            report["protocol_envelope"]["summary"]["rejected_count"], 20)
        self.assertEqual(report["mode_platform"]["modes_measured"], [])
        self.assertFalse(
            report["mode_platform"]["device_timing_measured"])
        self.assertFalse(report["mode_platform"]["listening_performed"])

    def test_report_does_not_copy_mutable_board_fields(self):
        report = reference.build_report()
        identity = report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(tuple(sorted(identity["projection"])),
                         tuple(sorted(reference.BOARD_ROW_FIELDS)))


if __name__ == "__main__":
    unittest.main()
