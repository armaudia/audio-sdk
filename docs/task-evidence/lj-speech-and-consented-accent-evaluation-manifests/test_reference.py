# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the LJ Speech / consented accent evidence package."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import reference

HERE = Path(__file__).resolve().parent


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _disk_manifest(root: Path) -> dict:
    manifest = copy.deepcopy(reference._synthetic_manifest())
    files = dict(reference._synthetic_files())
    file_names = {
        "source_path": "source_lj001_0001.wav",
        "target_path": "target_p360.flac",
        "consent_record_path": "consent.json",
        "terms_record_path": "terms.json",
        "cohort_record_path": "cohort.json",
        "scoring_plan_path": "scoring-plan.json",
        "approval_record_path": "approval.json",
    }
    for field, name in file_names.items():
        payload = files[f"{reference.SYNTHETIC_ROOT}/{name}"]
        (root / name).write_bytes(payload)
        manifest[field] = str(root / name)
        manifest[field.replace("_path", "_sha256")] = _sha(payload)
    for entry in manifest["accent_entries"]:
        name = Path(entry["path"]).name
        payload = files[f"{reference.SYNTHETIC_ROOT}/{name}"]
        (root / name).write_bytes(payload)
        entry["path"] = str(root / name)
        entry["sha256"] = _sha(payload)
    return manifest


class JsonAndCanonicalTests(unittest.TestCase):
    def test_canonical_json_rejects_nonfinite(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.canonical_bytes({"value": math.nan})

    def test_strict_json_rejects_duplicate_key(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_rejects_infinity_constant(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads('{"a":Infinity}')

    def test_strict_json_requires_object(self) -> None:
        with self.assertRaises(reference.Reject):
            reference.strict_loads("[1,2]")

    def test_canonical_normalizes_negative_zero(self) -> None:
        self.assertEqual(
            reference.canonical_bytes({"z": -0.0}), b'{"z":0.0}')


class WorkspaceAuditTests(unittest.TestCase):
    def test_five_clips_are_present_and_pinned(self) -> None:
        audit = reference.audit_workspace()
        self.assertEqual(audit["observed_clip_count"], 5)
        self.assertEqual(audit["admitted_clip_count"], 0)
        for artifact in audit["observed_artifacts"]:
            self.assertTrue(artifact["present"], artifact["id"])
            self.assertTrue(artifact["pin_matches"], artifact["id"])
            self.assertFalse(artifact["admitted"], artifact["id"])
            self.assertEqual(artifact["consent_status"], "absent")

    def test_declared_hashes_match_where_published(self) -> None:
        audit = reference.audit_workspace()
        declared = {item["id"]: item["declared_matches"]
                    for item in audit["observed_artifacts"]}
        self.assertTrue(declared["ljspeech_lj001_0001"])
        self.assertTrue(declared["rtvc_p360_target"])
        self.assertIsNone(declared["l2_arabic_aba_a0046"])
        self.assertIsNone(declared["l2_hindi_rrbi_a0391"])
        self.assertIsNone(declared["l2_korean_hjk_a0103"])

    def test_accent_group_mapping_matches_pinned_readme(self) -> None:
        audit = reference.audit_workspace()
        mapping = {
            item["speaker_id"]: item["l1_accent_group"]
            for item in audit["observed_artifacts"]
            if item["role"] == "accent_source"
        }
        self.assertEqual(mapping, {
            "ABA": "arabic", "RRBI": "hindi", "HJK": "korean"})

    def test_accent_clip_set_is_exact(self) -> None:
        audit = reference.audit_workspace()
        self.assertEqual(audit["accent_clip_names"], [
            "ABA_arctic_a0046.wav",
            "HJK_arctic_a0103.wav",
            "RRBI_arctic_a0391.wav",
        ])

    def test_reserved_manifests_and_rights_are_absent(self) -> None:
        audit = reference.audit_workspace()
        self.assertEqual(audit["reserved_present_paths"], [])
        self.assertFalse(audit["source_manifest_present"])
        self.assertFalse(audit["accent_manifest_present"])
        self.assertFalse(audit["target_manifest_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["consent_record_present"])
        self.assertFalse(audit["terms_record_present"])
        self.assertFalse(audit["scoring_plan_present"])
        self.assertFalse(audit["approval_record_present"])

    def test_audit_never_decodes_or_copies_audio(self) -> None:
        audit = reference.audit_workspace()
        self.assertFalse(audit["audio_decoded"])
        self.assertFalse(audit["audio_copied"])
        self.assertFalse(audit["network_used"])


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(
            identity["stable_fields"]["component"], reference.COMPONENT)
        self.assertEqual(
            identity["stable_fields"]["mode"], "research-control")
        self.assertFalse(identity["whole_file_hashed"])
        self.assertEqual(
            identity["claim"]["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(identity["claim"]["branch"], reference.BRANCH)
        expected = _sha(reference.canonical_bytes(identity["stable_fields"]))
        self.assertEqual(identity["stable_sha256"], expected)

    def test_mutable_fields_excluded(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(set(identity["excluded_mutable_fields"]),
                         set(reference.MUTABLE_TASK_FIELDS))
        for field in reference.MUTABLE_TASK_FIELDS:
            self.assertNotIn(field, identity["stable_fields"])

    def test_commit_is_full_hex(self) -> None:
        self.assertRegex(reference.BASE_COMMIT, r"^[0-9a-f]{40}$")


class SyntheticManifestTests(unittest.TestCase):
    def test_valid_manifest_is_structural_only(self) -> None:
        result = reference.validate_synthetic_manifest()
        self.assertTrue(result["accepted"])
        self.assertFalse(result["admitted_for_evaluation"])
        self.assertFalse(result["accepted_for_qualification"])
        self.assertFalse(result["consent_verified"])
        self.assertFalse(result["rights_approved"])
        self.assertFalse(result["reviewer_approved"])
        self.assertFalse(result["audio_decoded"])
        self.assertEqual(result["qualification_effect"], "none")
        self.assertEqual(result["accent_group_counts"], {
            "arabic": 1, "hindi": 1, "korean": 1})
        self.assertEqual(result["files_checked"], 10)

    def test_valid_manifest_projection_is_deterministic(self) -> None:
        first = reference.validate_synthetic_manifest()
        second = reference.validate_synthetic_manifest()
        self.assertEqual(first["manifest_projection_sha256"],
                         second["manifest_projection_sha256"])

    def test_caller_manifest_accepts_present_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _disk_manifest(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["admitted_for_evaluation"])
        self.assertEqual(result["accent_entry_count"], 3)

    def test_caller_manifest_rejects_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _disk_manifest(Path(raw))
            Path(manifest["target_path"]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_caller_manifest_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _disk_manifest(Path(raw))
            Path(manifest["source_path"]).write_bytes(b"tampered")
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_caller_manifest_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _disk_manifest(Path(raw))
            manifest["source_path"] = "relative.wav"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_all_adverse_cases_are_invoked_and_rejected(self) -> None:
        results = reference.run_adverse_controls()
        self.assertEqual(len(results), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual([item["case"] for item in results],
                         list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(item["result"] == "rejected" for item in results))


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.control = reference.build_control()

    def test_control_is_labelled_synthetic(self) -> None:
        control = self.control
        self.assertEqual(control["control_id"], reference.CONTROL_ID)
        self.assertFalse(control["model_executed"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertTrue(control["synthetic_fixture_is_not_a_real_manifest"])
        self.assertTrue(
            control["declared_ids_are_task_ids_not_provenance"])
        self.assertFalse(control["real_data_admitted"])

    def test_valid_invalid_missing_nonfinite_cases(self) -> None:
        control = self.control
        self.assertEqual(control["valid_case"]["result"], "accepted")
        self.assertFalse(
            control["valid_case"]["admitted_for_evaluation"])
        self.assertFalse(
            control["valid_case"]["accepted_for_qualification"])
        self.assertEqual(control["invalid_case"]["result"], "rejected")
        self.assertEqual(control["missing_case"]["result"], "rejected")
        self.assertEqual(control["nonfinite_case"]["result"], "rejected")

    def test_aggregation_separates_classes_and_records_failures(self) -> None:
        aggregation = self.control["aggregation"]
        self.assertFalse(aggregation["pooled_across_evidence_classes"])
        self.assertEqual(aggregation["record_count"], 4)
        self.assertEqual(aggregation["by_evidence_class"], {
            "paired": 0, "unpaired": 0, "synthetic": 4, "human": 0,
            "source_reported": 0})
        self.assertEqual(aggregation["by_l1_accent_group"], {
            "arabic": 2, "hindi": 1, "korean": 1})
        self.assertEqual(aggregation["failed_entry_ids"], [
            "synthetic_missing_consent_failure"])
        self.assertEqual(aggregation["measured_entry_ids"], [])
        self.assertEqual(len(aggregation["not_measured_entry_ids"]), 3)

    def test_aggregation_rejects_nonfinite_measured_value(self) -> None:
        records = [{
            "entry_id": "synthetic_nan",
            "l1_accent_group": "arabic",
            "evidence_class": "synthetic",
            "status": "measured",
            "value": math.nan,
            "reason": "",
        }]
        with self.assertRaises(reference.Reject):
            reference.aggregate_evidence(records)

    def test_aggregation_rejects_duplicate_and_bad_class(self) -> None:
        good = {
            "entry_id": "synthetic_one",
            "l1_accent_group": "arabic",
            "evidence_class": "synthetic",
            "status": "not_measured",
            "value": None,
            "reason": "",
        }
        with self.assertRaises(reference.Reject):
            reference.aggregate_evidence([good, dict(good)])
        bad = dict(good, evidence_class="source_reported_claim")
        with self.assertRaises(reference.Reject):
            reference.aggregate_evidence([bad])
        failed_without_reason = dict(
            good, entry_id="synthetic_two", status="failed")
        with self.assertRaises(reference.Reject):
            reference.aggregate_evidence([failed_without_reason])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = json.loads((HERE / "contract.json").read_text())

    def test_top_level_decision(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["mode"], "research-control")
        self.assertEqual(report["profile"], "evidence")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertIsNone(report["candidate_metrics"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertEqual(
            [gate["id"] for gate in gates],
            [gate for gate, _ in reference.GATE_REQUIREMENTS])

    def test_eight_exact_blockers(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 8)
        self.assertTrue(all(item["state"] == "absent" for item in blockers))
        ids = [item["id"] for item in blockers]
        self.assertIn("per_speaker_consent_absent", ids)
        self.assertIn("target_reference_provenance_absent", ids)
        self.assertIn("accent_group_manifest_absent", ids)

    def test_qualification_blocked(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(
            qualification["no_missing_result_qualifies_candidate"])
        self.assertEqual(qualification["blocked_gate_count"], 8)

    def test_boundary_is_closed(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "production_callback_registered",
                    "descriptor_registry_change", "shared_build_or_ci_change",
                    "installed_v0_behavior_change",
                    "audio_copied_into_package", "manifests_fabricated",
                    "consent_claimed", "rights_approved", "adapter_code_added",
                    "adapter_json_added", "downloads_performed",
                    "network_used", "processor_exposure", "ci_change"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_is_closed(self) -> None:
        scope = self.report["scope"]
        for key in ("benchmark_claim", "consent_record_present",
                    "device_timing", "listening", "manifest_admitted",
                    "model_executed", "network_used", "real_audio_copied",
                    "real_audio_decoded", "real_corpus_ingested",
                    "real_corpus_scored", "release_claim", "runtime_invoked",
                    "weights_downloaded", "weights_loaded"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["task_local_only"], True)
        self.assertIs(scope["clip_bytes_hashed_for_pin"], True)

    def test_requirements_have_no_fabricated_hash(self) -> None:
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertEqual(len(requirements), 8)
        for item in requirements.values():
            self.assertIsNone(item["sha256"])
            self.assertEqual(item["status"], "absent")

    def test_observed_artifacts_are_not_admitted(self) -> None:
        artifacts = self.report["observed_artifacts"]
        self.assertEqual(len(artifacts), 5)
        self.assertTrue(all(item["present"] for item in artifacts))
        self.assertTrue(all(item["pin_matches"] for item in artifacts))
        self.assertTrue(all(not item["admitted"] for item in artifacts))
        self.assertTrue(all(item["consent_status"] == "absent"
                            for item in artifacts))

    def test_evidence_profile_has_no_satisfied_item(self) -> None:
        profile = self.report["evidence_profile"]
        self.assertEqual(profile["name"], "evidence")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_measurements"])
        self.assertIsNone(profile["scorer_pin"])
        self.assertIsNone(profile["cohort_pin"])
        self.assertIsNone(profile["aggregation_plan"])
        self.assertTrue(all(item["qualification_effect"] == "none"
                            for item in profile["required_items"]))
        self.assertTrue(all(not item["satisfied_for_qualification"]
                            for item in profile["required_items"]))

    def test_audit_is_not_qualified(self) -> None:
        audit = self.report["asset_audit"]
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["audit_result"],
                         "observed_unmanifested_unconsented")
        self.assertEqual(audit["admitted_clip_count"], 0)
        self.assertFalse(audit["consent_present"])
        self.assertFalse(audit["terms_present"])
        self.assertFalse(audit["approval_present"])

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_source_reported_context_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"], "source_reported_not_measured_here")
        self.assertIn("not yet confirmed",
                      context["target_reference_status"])
        self.assertIn("CC BY-NC 4.0", context["accent_status"])

    def test_missing_artifacts_recorded(self) -> None:
        self.assertEqual(self.report["missing_historical_artifacts"],
                         list(reference.RESERVED_ABSENT_PATHS))

    def test_report_is_deterministic(self) -> None:
        first = reference.canonical_report_bytes(reference.build_report())
        second = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)

    def test_on_disk_report_matches_generator(self) -> None:
        expected = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual((HERE / "report.json").read_bytes(), expected)

    def test_sidecar_matches_report(self) -> None:
        expected = reference.canonical_report_bytes(reference.build_report())
        digest = _sha(expected)
        sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8")
        self.assertEqual(sidecar, f"{digest}  report.json\n")

    def test_contract_matches_report(self) -> None:
        contract = self.contract
        report = self.report
        self.assertEqual(contract["task"], report["task_id"])
        self.assertEqual(contract["decision"], report["decision"])
        self.assertEqual(contract["status"], report["status"])
        self.assertEqual(contract["mode"], report["mode"])
        self.assertEqual(contract["profile"], report["profile"])
        self.assertEqual(contract["source_pins"], report["source_pins"])
        self.assertEqual(contract["boundary_pins"], report["boundary_pins"])
        self.assertEqual(
            [gate["id"] for gate in contract["gates"]],
            [gate["id"] for gate in report["gates"]])
        self.assertEqual(
            [item["id"] for item in contract["exact_blockers"]],
            [item["id"] for item in report["exact_blockers"]])
        self.assertEqual(
            contract["task_row_identity"]["stable_sha256"],
            report["task_row_identity"]["stable_sha256"])
        self.assertEqual(contract["qualification"]["blocked_gate_count"], 8)

    def test_sources_manifest_has_no_tasks_json(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line and not line.startswith("#"):
                self.assertNotIn("TASKS.json", line)


if __name__ == "__main__":
    unittest.main()
