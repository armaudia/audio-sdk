# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance tests for the DAC-SE1 evidence bundle."""

from __future__ import annotations

import copy
import hashlib
import unittest
from pathlib import Path

import reference
import run

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

    def test_trailing_data_rejected(self):
        with self.assertRaises(ValueError):
            reference.loads_strict('{"a":1} trailing')

    def test_canonical_is_sorted_compact_and_newline_terminated(self):
        text = reference.canonical_text({"b": 1, "a": [2, 3]})
        self.assertEqual(text, '{"a":[2,3],"b":1}\n')
        self.assertNotIn(" ", text)


class PinAndIdentityTests(unittest.TestCase):
    def test_source_pins_match(self):
        rows = reference.pin_rows(reference.SOURCE_PINS, reference.AUDIO_ROOT)
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_boundary_pins_match(self):
        rows = reference.pin_rows(reference.BOUNDARY_PINS,
                                  reference.WORKTREE)
        self.assertEqual(len(rows), 18)
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

    def test_board_row_digest_is_stable(self):
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        expected = hashlib.sha256(reference.canonical_bytes(row)).hexdigest()
        self.assertEqual(reference.board_row_digest(row), expected)

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
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(not row["present"] for row in rows))

    def test_absence_summary_totals(self):
        summary = reference.absence_summary(
            reference.absence_probes(reference.AUDIO_ROOT),
            reference.worktree_absence_probes(),
            reference.home_absence_probes())
        self.assertEqual(summary["probe_count"], 28)
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


class EvidencePresenceTests(unittest.TestCase):
    def test_inventory_record_is_pinned_and_consistent(self):
        record = reference.inventory_record()
        self.assertEqual(record["id"], reference.COMPONENT_ID)
        self.assertEqual(record["name"], reference.TASK_TITLE)
        self.assertEqual(record["area"], "Enhancement")
        self.assertEqual(record["disposition"], "sdk-model")
        self.assertEqual(record["verification_profile"], "enhancement")
        self.assertEqual(record["task"], reference.TASK)
        self.assertEqual(record["evidence_line"], 68)
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
                    "weights_identified", "tokenizer_toolchain_present",
                    "input_media_present",
                    "exact_source_runtime_weights_conjunction_present",
                    "runtime_imported", "weights_loaded", "model_executed",
                    "audio_read", "network_used"):
            self.assertFalse(presence[key])

    def test_checkpoint_scope_has_no_identity(self):
        presence = reference.checkpoint_presence()
        self.assertEqual(presence["row_count"], 3)
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
            self.assertFalse(row["identity_verified"])

    def test_source_reported_identity_is_not_verified(self):
        identity = reference.SOURCE_REPORTED_IDENTITY
        self.assertEqual(identity["declared_code_license"], "MIT")
        self.assertEqual(identity["declared_checkpoint_license"], "MIT")
        self.assertEqual(identity["declared_released_checkpoint_size"],
                         "1.84 GB")
        self.assertEqual(identity["published_device"], "cuda")
        self.assertFalse(identity["cpu_only_worker_runnable_as_published"])
        self.assertFalse(identity["immutable_revision_recorded"])
        self.assertFalse(identity["license_text_staged"])
        self.assertFalse(identity["checkpoint_identity_recorded"])
        self.assertFalse(identity["tokenizer_toolchain_identified"])
        self.assertTrue(identity["source_reported_only"])
        self.assertFalse(identity["verified"])

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

    def test_rejection_groups_cover_missing_invalid_nonfinite(self):
        groups = {case["group"] for case in reference.admission_cases()}
        for group in ("document", "structure", "model", "runtime", "command",
                      "assets", "input", "output", "rights", "controls",
                      "nonfinite"):
            self.assertIn(group, groups)

    def test_missing_and_nonfinite_codes_present(self):
        codes = {case["code"] for case in reference.admission_cases()}
        self.assertIn("manifest_missing_field:runtime", codes)
        self.assertIn("output_peak_nonfinite", codes)
        self.assertIn("input_peak_nonfinite", codes)
        self.assertIn("assets[0]_present_at_review_wrong_value", codes)

    def test_admission_summary(self):
        admission = reference.build_admission()
        summary = admission["summary"]
        self.assertEqual(summary["case_count"], 90)
        self.assertEqual(summary["rejected_count"], 90)
        self.assertEqual(summary["accepted_schema_controls"], 1)
        self.assertEqual(summary["qualifying_results"], 0)
        self.assertFalse(summary["runtime_invoked"])
        control = admission["control"]
        self.assertTrue(control["accepted"])
        self.assertFalse(control["qualifies"])
        self.assertEqual(control["label"],
                         "synthetic_schema_control_not_evidence")


class EnvelopeTests(unittest.TestCase):
    def test_envelope_is_exact_identity_copy(self):
        envelope = reference.synthetic_envelope_probe()
        use = envelope["typical_api_use"]
        self.assertTrue(use["identity_exact"])
        self.assertTrue(use["replay_identical"])
        self.assertTrue(use["reset_replay_identical"])
        self.assertTrue(use["run_after_close_rejected"])
        self.assertEqual(use["output_peak"], "0.78125")
        self.assertFalse(use["qualifies"])
        self.assertFalse(use["runtime_invoked"])

    def test_envelope_rejections(self):
        envelope = reference.synthetic_envelope_probe()
        self.assertEqual(len(envelope["cases"]), 20)
        for case in envelope["cases"]:
            self.assertEqual(case["status"], "rejected")
            self.assertEqual(case["calls_after_rejection"], 0)
            self.assertFalse(case["qualifies"])
            self.assertTrue(case["state_unchanged"])
        self.assertEqual(envelope["summary"]["rejected_count"], 20)
        self.assertEqual(envelope["summary"]["qualifying_results"], 0)

    def test_envelope_lifecycle_rejects_after_close(self):
        envelope = reference.synthetic_envelope_probe()
        self.assertEqual(envelope["lifecycle"]["status"], "rejected")
        self.assertEqual(envelope["lifecycle"]["code"], "adapter_closed")
        self.assertFalse(envelope["lifecycle"]["qualifies"])

    def test_nonfinite_payload_rejected(self):
        codes = {case["code"] for case in reference.synthetic_envelope_probe()
                 ["cases"]}
        self.assertIn("payload_nonfinite", codes)


class ContractReportTests(unittest.TestCase):
    def test_contract_is_defer_incomplete_not_qualified(self):
        contract = reference.build_contract()
        reference.validate_contract(contract)
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "incomplete")
        self.assertTrue(contract["proposal_only"])
        self.assertEqual(contract["qualification_status"],
                         "not_qualified")

    def test_eight_blocked_release_gates(self):
        contract = reference.build_contract()
        self.assertEqual(len(contract["release_gates"]), 8)
        for index, gate in enumerate(contract["release_gates"], start=1):
            self.assertEqual(gate["id"], "RG-%02d" % index)
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])

    def test_seven_artifacts_one_present_six_blocked(self):
        contract = reference.build_contract()
        artifacts = contract["required_artifacts"]
        self.assertEqual(len(artifacts), 7)
        self.assertTrue(artifacts[0]["present"])
        self.assertTrue(artifacts[0]["verified"])
        for artifact in artifacts[1:]:
            self.assertFalse(artifact["present"])
            self.assertFalse(artifact["verified"])
            self.assertTrue(artifact["blocked"])

    def test_six_open_blockers(self):
        contract = reference.build_contract()
        self.assertEqual(len(contract["exact_blockers"]), 6)
        for blocker in contract["exact_blockers"]:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertTrue(blocker["required_action"])

    def test_enhancement_rows_and_no_real_result(self):
        contract = reference.build_contract()
        rows = contract["enhancement_profile"]["requirement_rows"]
        self.assertEqual(len(rows), 7)
        self.assertEqual(sum(1 for row in rows
                             if row["status"] == "blocked"), 6)
        self.assertEqual(sum(1 for row in rows
                             if row["status"] == "documented"), 1)
        self.assertFalse(contract["enhancement_profile"]
                         ["profile_satisfied"])
        self.assertEqual(contract["enhancement_profile"]["real_results"], 0)

    def test_report_has_no_floats_and_is_canonical(self):
        report = reference.build_report()
        reference._no_floats(report)
        text, digest = reference.canonical_report(report)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(),
                         digest)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(report["proposal_only"])

    def test_report_qualification_flags(self):
        report = reference.build_report()
        qualification = report["qualification"]
        self.assertTrue(qualification["not_qualified"])
        self.assertTrue(qualification["all_release_gates_blocked"])
        for key in ("real_result_present", "source_present",
                    "source_identity_recorded", "runtime_present",
                    "runtime_pinned", "weights_present", "weights_identified",
                    "tokenizer_toolchain_present", "input_media_present",
                    "implementation_present", "reference_execution_result",
                    "output_validity_result", "enhancement_profile_result",
                    "device_timing_result", "listening_result",
                    "benchmark_result", "release_claim",
                    "missing_result_promoted"):
            self.assertFalse(qualification[key])

    def test_report_scope_has_no_shared_change(self):
        scope = reference.build_report()["scope"]
        for key in ("provider_registered", "reference_implemented",
                    "reference_executed", "public_abi_changed",
                    "installed_v0_changed", "registry_or_default_changed",
                    "shared_build_or_ci_changed", "real_assets_used",
                    "network_used", "listening_performed",
                    "device_timing_measured", "benchmark_run",
                    "release_claim"):
            self.assertFalse(scope[key])
        self.assertTrue(scope["task_local_only"])


class CommittedArtifactTests(unittest.TestCase):
    def test_committed_report_matches_regeneration(self):
        report = reference.read_strict_json(HERE / "report.json")
        self.assertEqual(reference.canonical_bytes(report),
                         reference.canonical_bytes(reference.build_report()))

    def test_committed_contract_matches_regeneration(self):
        contract = reference.read_strict_json(HERE / "contract.json")
        self.assertEqual(reference.canonical_bytes(contract),
                         reference.canonical_bytes(reference.build_contract()))

    def test_sidecar_digest_matches_report(self):
        digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
        self.assertEqual((HERE / "report.json.sha256").read_text(
            encoding="ascii"), f"{digest}  report.json\n")

    def test_sources_manifest_matches(self):
        self.assertEqual((HERE / "SOURCES.sha256").read_bytes(),
                         run.sources_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
