# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local AccentCL evidence package."""

from __future__ import annotations

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


def _manifest_fixture(root: Path) -> dict:
    runtime = root / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    checkpoint_paths = []
    checkpoint_shas = []
    for index in range(reference.CLASS_COUNT):
        path = root / f"class-{index}.pt"
        data = f"checkpoint-{index}".encode("utf-8")
        path.write_bytes(data)
        checkpoint_paths.append(str(path))
        checkpoint_shas.append(_sha(data))
    files = {
        "whisper_weights_path": b"whisper-large-v3-weights",
        "whisper_config_path": b'{"model":"whisper-large-v3"}',
        "label_map_path": b'["synthetic_class_0","synthetic_class_1"]',
        "runtime_lock_path": b"torch==0.0.0\n",
        "license_record_path": b"license-record",
        "consent_record_path": b"consent-record",
        "cohort_manifest_path": b'{"cohort":"frozen"}',
    }
    manifest = {
        "source_revision": "b" * 40,
        "variant": reference.VARIANT,
        "sample_rate_input_hz": reference.INPUT_SAMPLE_RATE_HZ,
        "channels": reference.CHANNELS,
        "class_count": reference.CLASS_COUNT,
        "whisper_model": reference.WHISPER_MODEL_NAME,
        "checkpoint_paths": checkpoint_paths,
        "checkpoint_sha256s": checkpoint_shas,
        "runtime_path": str(runtime),
    }
    for field, data in files.items():
        path = root / (field.replace("_path", "") + ".bin")
        path.write_bytes(data)
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = _sha(data)
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


class SourceAuditTests(unittest.TestCase):
    def test_accentcl_source_is_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["source_checkout_present"])
        self.assertIsNone(audit["source_revision"])
        self.assertFalse(audit["source_revision_pinned"])

    def test_no_source_pins_are_invented(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["source_file_pins_defined"])
        self.assertEqual(audit["source_files_checked"], 0)
        self.assertFalse(audit["source_file_pins_match"])

    def test_asset_set_is_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["license_file_present"])
        self.assertFalse(audit["checkpoint_dir_present"])
        self.assertEqual(audit["checkpoint_file_count"], 0)
        self.assertFalse(audit["all_checkpoints_present"])
        self.assertFalse(audit["whisper_cache_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["label_map_present"])

    def test_research_clips_are_not_evaluation_evidence(self) -> None:
        audit = reference.audit_assets()
        self.assertEqual(audit["research_demo_audio_clip_count"], 3)
        self.assertNotIn("evaluation_clip_count", audit)

    def test_requested_geometry(self) -> None:
        config = reference.audit_assets()["requested_config"]
        self.assertEqual(config["input_sample_rate_hz"], 16000)
        self.assertEqual(config["channels"], 1)
        self.assertEqual(config["class_count"], 7)
        self.assertEqual(config["backbone"], "Whisper-Large-v3")
        self.assertEqual(config["variant"], "offline_whole_utterance")


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(
            identity["stable_fields"]["component"], reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "feasibility")
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

    def test_commits_are_full_hex(self) -> None:
        self.assertRegex(reference.BASE_COMMIT, r"^[0-9a-f]{40}$")
        self.assertIsNone(reference.ACCENTCL_COMMIT)


class LabelAndScoreTests(unittest.TestCase):
    def test_synthetic_labels_are_placeholders(self) -> None:
        labels = list(reference.SYNTHETIC_LABELS)
        self.assertEqual(len(labels), 7)
        self.assertEqual(labels, list(reference.validate_label_set(labels)))
        self.assertTrue(all(label.startswith("synthetic_class_")
                            for label in labels))

    def test_label_digest_is_deterministic(self) -> None:
        first = reference.label_map_digest(list(reference.SYNTHETIC_LABELS))
        second = reference.label_map_digest(list(reference.SYNTHETIC_LABELS))
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")

    def test_synthetic_scores_are_normalized(self) -> None:
        scores = reference.synthetic_scores()
        self.assertEqual(len(scores), 7)
        self.assertAlmostEqual(math.fsum(scores), 1.0, places=12)
        self.assertTrue(all(math.isfinite(value) for value in scores))
        self.assertTrue(all(0.0 <= value <= 1.0 for value in scores))

    def test_argmax_is_deterministic(self) -> None:
        self.assertEqual(reference.argmax_index(reference.synthetic_scores()), 0)
        record = reference.classification_record(reference.synthetic_scores())
        self.assertEqual(record["class_index"], 0)
        self.assertEqual(record["class_label"], "synthetic_class_0")
        self.assertFalse(record["tie"])

    def test_tie_uses_lowest_index(self) -> None:
        record = reference.classification_record(reference.tie_scores())
        self.assertTrue(record["tie"])
        self.assertEqual(record["class_index"], 0)
        self.assertEqual(record["tie_indices"], [0, 1])
        self.assertEqual(record["tie_rule"], "lowest_index_wins")

    def test_validate_scores_rejects_invalid(self) -> None:
        cases = [
            lambda: reference.validate_class_scores([]),
            lambda: reference.validate_class_scores(b"1234567"),
            lambda: reference.validate_class_scores(None),
            lambda: reference.validate_class_scores([0.5] * 6),
            lambda: reference.validate_class_scores([0.5] * 8),
            lambda: reference.validate_class_scores(
                [0.5, 0.5, math.nan, 0, 0, 0, 0]),
            lambda: reference.validate_class_scores(
                [0.5, 0.5, math.inf, 0, 0, 0, 0]),
            lambda: reference.validate_class_scores(
                [0.5, 0.5, -math.inf, 0, 0, 0, 0]),
            lambda: reference.validate_class_scores(
                [0.5, 0.5, 1.5, 0, 0, 0, 0]),
            lambda: reference.validate_class_scores(
                [0.5, 0.5, -0.5, 0.5, 0, 0, 0]),
            lambda: reference.validate_class_scores(
                [0.5, 0.5, True, 0, 0, 0, 0]),
            lambda: reference.validate_class_scores(
                [0.5, 0.5, "0", 0, 0, 0, 0]),
            lambda: reference.validate_class_scores([0.5] * 7),
        ]
        for action in cases:
            with self.assertRaises(reference.Reject):
                action()

    def test_validate_labels_rejects_invalid(self) -> None:
        good = list(reference.SYNTHETIC_LABELS)
        cases = [
            lambda: reference.validate_label_set([]),
            lambda: reference.validate_label_set(good[:6]),
            lambda: reference.validate_label_set(good + ["x"]),
            lambda: reference.validate_label_set(
                ["a", "b", "c", "d", "e", "f", ""]),
            lambda: reference.validate_label_set(
                ["a", "a", "b", "c", "d", "e", "f"]),
            lambda: reference.validate_label_set(
                ["a", "b", "c", "d", "e", "f", "class\u00e9"]),
            lambda: reference.validate_label_set(
                ["a", "b", "c", "d", "e", "f", 7]),
        ]
        for action in cases:
            with self.assertRaises(reference.Reject):
                action()


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_complete_shape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["accepted_for_qualification"])
        self.assertFalse(result["revision_pinned"])
        self.assertFalse(result["model_executed"])
        self.assertEqual(result["class_count"], 7)
        self.assertEqual(result["checkpoints_checked"], 7)
        self.assertEqual(result["qualification_effect"], "none")

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["checkpoint_paths"][3]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["whisper_weights_path"]).write_bytes(b"tampered")
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["runtime_path"]).rmdir()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["label_map_path"] = "labels.json"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_unpinned_revision_shape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["source_revision"] = "not-a-commit"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_streaming_variant(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["variant"] = "incremental_streaming"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_float_class_count(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["class_count"] = 7.0
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_duplicate_checkpoints(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["checkpoint_paths"][1] = manifest["checkpoint_paths"][0]
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)


class AdverseControlTests(unittest.TestCase):
    def test_all_adverse_cases_are_invoked_and_rejected(self) -> None:
        results = reference.run_adverse_controls()
        self.assertEqual(len(results), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual([item["case"] for item in results],
                         list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(item["result"] == "rejected" for item in results))

    def test_control_is_labelled_synthetic(self) -> None:
        control = reference.build_control()
        self.assertEqual(control["plan_source"],
                         reference.CONTROL_PLAN_PROVENANCE)
        self.assertFalse(control["model_executed"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertTrue(control["synthetic_label_set_is_placeholder"])
        self.assertFalse(control["upstream_label_names_available"])
        self.assertEqual(control["class_count"], 7)

    def test_acceptance_outcomes_are_all_unmeasured(self) -> None:
        control = reference.build_control()
        self.assertEqual(len(control["acceptance_outcomes"]), 6)
        self.assertTrue(all(item["measured"] is False
                            and item["value"] is None
                            for item in control["acceptance_outcomes"]))


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = json.loads((HERE / "contract.json").read_text())

    def test_top_level_decision(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["mode"], "feasibility")
        self.assertEqual(report["profile"], "voice")
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
        self.assertIn("source_license_absent",
                      [item["id"] for item in blockers])

    def test_qualification_blocked(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(qualification["no_missing_result_qualifies_candidate"])
        self.assertEqual(qualification["blocked_gate_count"], 8)

    def test_boundary_is_closed(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "production_callback_registered", "descriptor_registry_change",
                    "shared_build_or_ci_change", "installed_v0_behavior_change",
                    "asset_bundled", "weights_vendored", "sdk_callback_invoked",
                    "network_used"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_is_closed(self) -> None:
        scope = self.report["scope"]
        for key in ("real_audio", "real_corpus", "real_accentcl_model",
                    "model_executed", "weights_loaded", "weights_downloaded",
                    "runtime_invoked", "vendor_runtime_invoked", "network_used",
                    "device_timing", "listening", "public_benchmark",
                    "release_claim"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["task_local_only"], True)

    def test_requirements_have_no_fabricated_hash(self) -> None:
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertIsNone(requirements["accentcl_source_checkout"]["sha256"])
        self.assertIsNone(requirements["seven_class_checkpoints"]["sha256"])
        self.assertIsNone(requirements["whisper_large_v3_backbone"]["sha256"])
        self.assertIsNone(requirements["exact_runtime"]["runtime_lock_sha256"])

    def test_voice_profile_has_no_satisfied_item(self) -> None:
        profile = self.report["voice_profile"]
        self.assertEqual(profile["name"], "voice")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_model_metrics"])
        self.assertTrue(all(item["qualification_effect"] == "none"
                            for item in profile["required_items"]))

    def test_audit_is_not_qualified(self) -> None:
        audit = self.report["asset_audit"]
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["audit_result"], "absent")
        self.assertFalse(audit["source_present"])
        self.assertFalse(audit["license_present"])
        self.assertFalse(audit["all_checkpoints_present"])
        self.assertFalse(audit["whisper_cache_present"])
        self.assertFalse(audit["label_map_present"])

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_source_reported_context_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"], "source_reported_not_measured_here")
        self.assertEqual(context["reported_status"], "Not run")
        self.assertEqual(context["reported_class_count"], 7)

    def test_missing_artifacts_recorded(self) -> None:
        for path in (reference.MISSING_CHECKPOINT_PATH,
                     reference.RUNTIME_LOCK_PATH,
                     reference.LABEL_MAP_PATH,
                     reference.COHORT_MANIFEST_PATH,
                     reference.RIGHTS_RECORD_PATH):
            self.assertIn(path, self.report["missing_historical_artifacts"])

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
