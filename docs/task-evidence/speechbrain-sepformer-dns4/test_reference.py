# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance tests for the SepFormer DNS4 readiness bundle."""

from __future__ import annotations

import copy
import hashlib
import math
import unittest
from decimal import Decimal
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
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_boundary_pins_match(self):
        rows = reference.pin_rows(reference.BOUNDARY_PINS, reference.WORKTREE)
        self.assertEqual(len(rows), len(reference.BOUNDARY_PINS))
        self.assertTrue(all(row["verified"] for row in rows.values()))

    def test_board_projection_has_only_stable_fields(self):
        row = reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
        self.assertEqual(tuple(sorted(row)), tuple(sorted(
            reference.BOARD_ROW_FIELDS)))
        self.assertEqual(row["id"], reference.TASK)
        self.assertEqual(row["component"], reference.COMPONENT_ID)
        for mutable in ("status", "owner", "claim", "review", "handoff",
                        "blocked_reason", "dispatch_priority"):
            self.assertNotIn(mutable, row)

    def test_board_row_digest_is_projection_digest(self):
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
                          "SDK-FND-NN", "SDK-FND-PROVIDER"])

    def test_checkpoint_pins_match_the_recorded_lock(self):
        lock = reference.read_strict_json(
            reference.AUDIO_ROOT /
            "research/voice-enhancement-20261101/agent-sepformer-eval/"
            "adapter.lock.json")
        self.assertEqual(lock["model"], reference.MODEL_ID)
        self.assertEqual(lock["revision"], reference.MODEL_REVISION)
        self.assertEqual(lock["license"], reference.MODEL_LICENSE)
        self.assertEqual(lock["files_sha256"], reference.CHECKPOINT_FILES)

    def test_adapter_descriptor_matches_identity(self):
        descriptor = reference.read_strict_json(
            reference.AUDIO_ROOT /
            "research/voice-enhancement-20261101/agent-sepformer-eval/"
            "adapter.json")
        self.assertEqual(descriptor["identity"],
                         "SpeechBrain-1.0.3-SepFormer-DNS4")
        self.assertEqual(descriptor["modes"], ["offline"])
        self.assertEqual(descriptor["tasks"], ["CLN-01"])


class AbsenceAndReadinessTests(unittest.TestCase):
    def test_workspace_probes_are_absent(self):
        rows = reference.absence_probes(reference.AUDIO_ROOT)
        self.assertEqual(len(rows), len(reference.ABSENCE_PROBES))
        self.assertTrue(all(not row["present"] for row in rows))

    def test_worktree_and_home_probes_are_absent(self):
        worktree = reference.worktree_absence_probes()
        home = reference.home_absence_probes()
        self.assertEqual(len(worktree), len(reference.WORKTREE_ABSENCE_PROBES))
        self.assertEqual(len(home), len(reference.HOME_ABSENCE_PROBES))
        self.assertTrue(all(not row["present"] for row in worktree + home))

    def test_present_probe_fails_closed(self):
        with self.assertRaisesRegex(ValueError,
                                    "artifact_present_reopen_required"):
            reference.absence_probes(reference.AUDIO_ROOT,
                                     probes=("research",))

    def test_absence_summary_counts(self):
        summary = reference.absence_summary(
            reference.absence_probes(reference.AUDIO_ROOT),
            reference.worktree_absence_probes(),
            reference.home_absence_probes())
        self.assertEqual(summary["probe_count"], 19)
        self.assertEqual(summary["workspace_probe_count"], 12)
        self.assertEqual(summary["worktree_probe_count"], 3)
        self.assertEqual(summary["home_probe_count"], 4)
        self.assertEqual(summary["present_count"], 0)
        self.assertTrue(summary["all_probes_absent"])

    def test_runtime_readiness_is_blocked_without_importing(self):
        readiness = reference.runtime_readiness()
        self.assertTrue(readiness["blocked"])
        self.assertFalse(readiness["importable"])
        self.assertFalse(readiness["module_spec_found"])
        self.assertFalse(readiness["runtime_imported"])
        self.assertEqual(readiness["found_modules"], [])
        self.assertEqual(readiness["exact_error"],
                         "ModuleNotFoundError: No module named 'torch'")

    def test_source_presence_keeps_conjunction_false(self):
        presence = reference.source_presence()
        self.assertTrue(presence["research_reports_present"])
        self.assertTrue(presence["checkpoint_lock_present"])
        self.assertTrue(presence["recorded_result_rows_present"])
        self.assertTrue(presence["scorer_source_present"])
        self.assertFalse(
            presence["exact_source_runtime_weights_conjunction_present"])
        for key in ("runtime_present", "weights_present", "corpus_present",
                    "outputs_present", "runtime_imported", "weights_loaded",
                    "model_executed", "audio_read", "network_used"):
            self.assertFalse(presence[key], key)


class RecordedProvenanceTests(unittest.TestCase):
    def test_recorded_arithmetic_agrees(self):
        provenance = reference.recorded_provenance()
        self.assertTrue(provenance["all_agree"])
        self.assertTrue(provenance["rtf_definition_consistent"])
        self.assertTrue(provenance["clean_rtf_definition_consistent"])
        self.assertTrue(provenance["clean_identity_stoi_consistent"])
        self.assertFalse(provenance["reproduced_here"])
        self.assertFalse(provenance["qualifies"])

    def test_recorded_identity_is_the_frozen_protocol(self):
        identity = reference.recorded_provenance()["identity"]
        self.assertTrue(identity["ids_match_recorded_set"])
        self.assertTrue(identity["clean_ids_match_recorded_set"])
        self.assertTrue(identity["matched_ids_match_recorded_set"])
        self.assertEqual(identity["row_count"], 30)
        self.assertEqual(identity["unique_output_hashes"], 30)
        self.assertTrue(identity["all_rows_ten_seconds"])
        self.assertEqual(identity["revision"], reference.MODEL_REVISION)

    def test_recorded_protocol_arithmetic(self):
        protocol = reference.PROTOCOL_RECORDED
        self.assertEqual(
            protocol["pair_count"] * protocol["sample_count_per_item"],
            protocol["total_samples"])
        self.assertEqual(
            Decimal(protocol["pair_count"]) *
            Decimal(protocol["item_seconds"]),
            Decimal(protocol["total_seconds"]))
        self.assertEqual(len(set(protocol["expected_sample_ids"])),
                         protocol["pair_count"])

    def test_quantized_agreement_detects_drift(self):
        self.assertTrue(reference._agrees("0.1234564", "0.1234561"))
        self.assertFalse(reference._agrees("0.123456", "0.123457"))

    def test_provenance_reports_no_model_use(self):
        provenance = reference.recorded_provenance()
        self.assertFalse(provenance["model_executed"])
        self.assertFalse(provenance["weights_loaded"])
        self.assertFalse(provenance["audio_read"])
        self.assertFalse(provenance["network_used"])
        self.assertFalse(provenance["used_for_evidence"])


class EnvelopeTests(unittest.TestCase):
    def test_identity_variant_is_exact_and_unchanged(self):
        identity = reference._envelope_variant("identity")
        self.assertTrue(identity["identity_exact"])
        self.assertFalse(identity["changed"])
        self.assertTrue(identity["replay_identical"])
        self.assertTrue(identity["reset_replay_identical"])
        self.assertTrue(identity["length_preserving"])
        self.assertTrue(identity["finite_output"])
        self.assertEqual(identity["output_peak"], "0.78125")

    def test_unit_peak_variant_changes_level_only(self):
        unit_peak = reference._envelope_variant("unit_peak")
        self.assertFalse(unit_peak["identity_exact"])
        self.assertTrue(unit_peak["changed"])
        self.assertTrue(unit_peak["length_preserving"])
        self.assertTrue(unit_peak["peak_within_unit"])
        self.assertEqual(unit_peak["output_peak"], "1.0")
        self.assertTrue(unit_peak["replay_identical"])

    def test_envelope_rejections_do_not_advance_state(self):
        cases = reference.envelope_cases()
        self.assertEqual(len(cases), 18)
        for case in cases:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertEqual(case["calls_after_rejection"], 0, case["id"])
            self.assertTrue(case["state_unchanged"], case["id"])
            self.assertTrue(case["code"], case["id"])
            self.assertFalse(case["qualifies"], case["id"])

    def test_envelope_lifecycle_closes_and_rejects(self):
        probe = reference.synthetic_envelope_probe()
        lifecycle = probe["lifecycle"]
        self.assertEqual(lifecycle["status"], "rejected")
        self.assertEqual(lifecycle["code"], "enhancer_closed")
        self.assertFalse(lifecycle["qualifies"])
        self.assertEqual(probe["summary"]["case_count"], 18)
        self.assertEqual(probe["summary"]["rejected_count"], 18)

    def test_nonfinite_envelope_input_is_rejected(self):
        cases = {case["id"]: case for case in reference.envelope_cases()}
        self.assertEqual(cases["EV-13"]["code"], "input_nonfinite")

    def test_envelope_probe_claims_no_runtime_or_model(self):
        probe = reference.synthetic_envelope_probe()
        for key in ("runtime_invoked", "weights_loaded", "model_executed",
                    "audio_read", "network_used"):
            self.assertFalse(probe["summary"][key], key)
            self.assertFalse(probe["typical_api_use"][key], key)
        self.assertFalse(probe["qualifies"])


class AdmissionTests(unittest.TestCase):
    def test_control_manifest_is_admitted_without_mutation(self):
        manifest = reference.control_manifest()
        before = copy.deepcopy(manifest)
        reference.validate_manifest(manifest)
        self.assertEqual(manifest, before)

    def test_admission_rejections_do_not_advance_state(self):
        cases = reference.admission_cases()
        self.assertEqual(len(cases), 95)
        for case in cases:
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertTrue(case["code"], case["id"])
            self.assertTrue(case["state_unchanged"], case["id"])
            self.assertFalse(case["qualifies"], case["id"])

    def test_admission_groups_are_covered(self):
        groups = {case["group"] for case in reference.admission_cases()}
        self.assertEqual(groups, {
            "document", "structure", "model", "runtime", "assets", "corpus",
            "outputs", "metrics", "controls", "rights", "nonfinite"})

    def test_admission_build_has_one_nonqualifying_control(self):
        admission = reference.build_admission()
        self.assertTrue(admission["control"]["accepted"])
        self.assertFalse(admission["control"]["qualifies"])
        self.assertEqual(admission["control"]["label"],
                         "synthetic_schema_control_not_evidence")
        self.assertEqual(admission["summary"]["case_count"], 95)
        self.assertEqual(admission["summary"]["rejected_count"], 95)
        self.assertEqual(admission["summary"]["qualifying_results"], 0)

    def test_nonfinite_and_missing_metrics_rejected(self):
        cases = {case["id"]: case for case in reference.admission_cases()}
        self.assertEqual(cases["NF-01"]["code"],
                         "decimal_invalid:outputs.peak_max")
        self.assertEqual(cases["NF-02"]["code"],
                         "decimal_invalid:metrics.si_sdr_delta_db_mean")
        self.assertEqual(cases["ME-12"]["code"],
                         "decimal_invalid:metrics.stoi_delta_mean")
        self.assertEqual(cases["MD-02"]["code"], "model_revision_invalid")

    def test_claims_qualified_true_is_rejected(self):
        manifest = reference.control_manifest()
        manifest["rights"]["claims_qualified"] = True
        with self.assertRaisesRegex(reference.AdmissionError,
                                    "claims_qualified"):
            reference.validate_manifest(manifest)

    def test_asset_digest_must_match_the_pinned_lock(self):
        manifest = reference.control_manifest()
        manifest["assets"][0]["sha256"] = "1" * 64
        with self.assertRaisesRegex(reference.AdmissionError,
                                    "asset_digest_mismatch"):
            reference.validate_manifest(manifest)

    def test_speechbrain_wheel_digest_is_pinned(self):
        manifest = reference.control_manifest()
        manifest["runtime"]["wheel_digests"]["speechbrain"] = "f" * 64
        with self.assertRaisesRegex(reference.AdmissionError,
                                    "speechbrain_wheel_digest_mismatch"):
            reference.validate_manifest(manifest)

    def test_extra_field_is_rejected(self):
        manifest = reference.control_manifest()
        manifest["extra"] = 1
        with self.assertRaisesRegex(reference.AdmissionError,
                                    "field_set_invalid:root"):
            reference.validate_manifest(manifest)


class ContractReportTests(unittest.TestCase):
    def test_contract_validates(self):
        reference.validate_contract(reference.build_contract())

    def test_eight_blocked_gates(self):
        contract = reference.build_contract()
        gates = contract["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-%02d" % index for index in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen_condition"])
            self.assertEqual(gate["linked_row"], contract["boundary"][
                "linked_row"])

    def test_seven_open_blockers_map_to_artifacts(self):
        contract = reference.build_contract()
        artifacts = {row["id"] for row in contract["required_artifacts"]}
        gates = {row["id"] for row in contract["release_gates"]}
        self.assertEqual(len(contract["exact_blockers"]), 7)
        for blocker in contract["exact_blockers"]:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertIn(blocker["artifact_id"], artifacts)
            self.assertTrue(set(blocker["linked_gates"]) <= gates)

    def test_artifact_presence_is_bounded(self):
        artifacts = reference.build_contract()["required_artifacts"]
        self.assertEqual(len(artifacts), 8)
        self.assertTrue(artifacts[0]["present"])
        self.assertFalse(artifacts[0]["blocked"])
        for artifact in artifacts[1:]:
            self.assertFalse(artifact["present"])
            self.assertTrue(artifact["blocked"])
            self.assertIsNone(artifact["sha256"])

    def test_enhancement_profile_is_fully_blocked(self):
        report = reference.build_report()
        profile = report["enhancement_profile"]
        self.assertEqual(profile["summary"]["requirement_count"], 8)
        self.assertEqual(profile["summary"]["blocked_count"], 8)
        self.assertFalse(profile["summary"]["profile_satisfied"])
        self.assertFalse(profile["summary"]["values_inferred"])

    def test_qualification_flags(self):
        qualification = reference.build_contract()["qualification"]
        for key in ("not_qualified", "all_release_gates_blocked"):
            self.assertTrue(qualification[key], key)
        for key in ("real_result_present", "runtime_present", "weights_present",
                    "corpus_present", "outputs_present",
                    "reproduced_inference_result",
                    "enhancement_profile_result", "alignment_state_result",
                    "timing_result", "listening_result", "benchmark_result",
                    "release_claim", "missing_result_promoted"):
            self.assertFalse(qualification[key], key)

    def test_report_is_canonical_and_float_free(self):
        report = reference.build_report()
        reference._no_floats(report)
        text, digest = reference.canonical_report(report)
        self.assertEqual(text, reference.canonical_text(report))
        self.assertEqual(digest, hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(reference.build_report(), report)

    def test_report_carries_contract_digest_and_identity(self):
        contract = reference.build_contract()
        report = reference.build_report()
        self.assertEqual(report["contract_sha256"],
                         reference.object_digest(contract))
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "incomplete")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["profile"], "enhancement")

    def test_historical_run_is_provenance_only(self):
        historical = reference.build_report()["historical_execution"]
        self.assertTrue(historical["provenance_only"])
        self.assertFalse(historical["reproduced_here"])
        self.assertFalse(historical["used_for_evidence"])
        self.assertFalse(historical["qualifies"])
        run = historical["run"]
        self.assertFalse(run["listening_result"])
        self.assertFalse(run["device_timing_result"])
        self.assertFalse(run["streaming_supported"])
        self.assertEqual(run["provenance_only"], True)

    def test_linked_row_identity_is_not_the_board_file(self):
        report = reference.build_report()
        identity = report["linked_row_identity"]
        self.assertEqual(identity["gating"], "stable_identity_only")
        self.assertFalse(identity["board_file_pinned"])
        self.assertFalse(identity["board_status_gates_anything"])
        self.assertEqual(identity["linked_rows_sha256"],
                         reference.linked_rows_digest())

    def test_no_forbidden_artifacts_in_package(self):
        forbidden = {".ckpt", ".pt", ".pth", ".onnx", ".wav", ".flac",
                     ".safetensors", ".bin", ".so", ".dylib", ".pyc"}
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(), forbidden, path.name)
            self.assertFalse(path.is_symlink(), path.name)

    def test_decimal_helper_rejects_nonfinite(self):
        with self.assertRaisesRegex(ValueError, "nonfinite_decimal"):
            reference._decimal_string(math.inf)


if __name__ == "__main__":
    unittest.main()
