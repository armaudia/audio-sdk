# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local breath-detector-removal package."""

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
    source = root / "source"
    runtime = root / "runtime"
    source.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    files = {
        "detector_weights_path": b"breath-weights",
        "config_path": b"sample_rate_hz: 16000\n",
        "calibration_path": b"calibration: frozen\n",
        "runtime_lock_path": b"numpy==0.0.0\n",
        "license_record_path": b"license-record",
        "rights_record_path": b"rights-record",
        "breath_policy_path": b'{"preserve": ["expressive"]}',
        "event_label_manifest_path": b'{"events": []}',
        "cohort_manifest_path": b'{"cohort": "fixture"}',
        "parity_vector_path": b'{"parity": "fixture"}',
        "output_use_grant_path": b'{"grant": "fixture"}',
    }
    manifest = {
        "detector_source_path": str(source),
        "runtime_path": str(runtime),
        "sample_rate_hz": reference.CONTROL_SAMPLE_RATE_HZ,
        "channels": reference.CHANNELS,
        "frame_samples": reference.SDK_FRAME_SAMPLES,
        "source_revision": "a" * 40,
        "variant": reference.CALLER_VARIANT,
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
        payload = reference.canonical_bytes({"z": -0.0})
        self.assertEqual(payload, b'{"z":0.0}')

    def test_fraction_text(self) -> None:
        from fractions import Fraction
        self.assertEqual(reference.fraction_text(Fraction(2, 3)), "2/3")
        self.assertEqual(reference.fraction_text(Fraction(6, 3)), "2")


class SourceAuditTests(unittest.TestCase):
    def test_source_checkout_is_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["source_checkout_present"])
        self.assertIsNone(audit["source_revision"])
        self.assertFalse(audit["source_revision_pin_available"])
        self.assertFalse(audit["source_revision_matches"])

    def test_no_license_weights_or_runtime(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["license_file_present"])
        self.assertEqual(audit["license_files"], [])
        self.assertFalse(audit["weights_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])

    def test_no_policy_labels_rights_or_cohort(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["output_use_grant_present"])
        self.assertFalse(audit["breath_policy_present"])
        self.assertFalse(audit["natural_breath_labels_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])

    def test_absence_probes_are_all_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertEqual(len(audit["absence_probes"]),
                         len(reference.ABSENCE_PROBES))
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertEqual(
            [item["path"] for item in audit["absence_probes"]],
            list(reference.ABSENCE_PROBES))
        self.assertTrue(all(item["exists"] is False
                            for item in audit["absence_probes"]))

    def test_geometry_is_unestablished(self) -> None:
        config = reference.audit_assets()["requested_config"]
        self.assertEqual(config["geometry_status"], "unestablished")
        self.assertIsNone(config["upstream_revision"])
        self.assertFalse(config["pinned_candidate_source"])
        self.assertEqual(config["control_sample_rate_hz"], 16000)
        self.assertEqual(config["control_frame_samples"], 160)


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "feasibility")
        self.assertFalse(identity["whole_file_hashed"])
        self.assertEqual(identity["claim"]["base_commit"],
                         reference.BASE_COMMIT)
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
        self.assertIsNone(reference.UPSTREAM_REVISION)
        self.assertIsNone(reference.UPSTREAM_PROJECT_URL)
        self.assertIsNone(reference.UPSTREAM_REPO_URL)


class PcmTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        first = reference.synthetic_input_pcm()
        second = reference.synthetic_input_pcm()
        self.assertEqual(first, second)
        self.assertEqual(len(first), reference.CONTROL_SOURCE_SAMPLES)

    def test_synthetic_pcm_is_finite_and_bounded(self) -> None:
        source = reference.validate_pcm(reference.synthetic_input_pcm())
        self.assertTrue(all(math.isfinite(value) for value in source))
        self.assertLessEqual(max(abs(v) for v in source), 1.0)

    def test_pcm_summary_is_deterministic(self) -> None:
        signal = reference.synthetic_input_pcm()
        first = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        second = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertEqual(first, second)
        self.assertEqual(first["duration_s"], "3")
        self.assertEqual(first["channels"], 1)
        self.assertEqual(first["samples"], 48000)

    def test_validate_pcm_accepts_integers(self) -> None:
        self.assertEqual(reference.validate_pcm([0, 0.5, -1]), [0.0, 0.5, -1.0])

    def test_validate_pcm_rejects_invalid(self) -> None:
        cases = [
            lambda: reference.validate_pcm([]),
            lambda: reference.validate_pcm(b"ab"),
            lambda: reference.validate_pcm(None),
            lambda: reference.validate_pcm([0.0], 8000),
            lambda: reference.validate_pcm([0.0], 16000, 2),
            lambda: reference.validate_pcm([math.nan]),
            lambda: reference.validate_pcm([math.inf]),
            lambda: reference.validate_pcm([-math.inf]),
            lambda: reference.validate_pcm([1.5]),
            lambda: reference.validate_pcm([True]),
            lambda: reference.validate_pcm(["0.1"]),
        ]
        for action in cases:
            with self.assertRaises(reference.Reject):
                action()


class IntervalTests(unittest.TestCase):
    def test_fixture_intervals_validate(self) -> None:
        checked = reference.validate_breath_intervals(
            [dict(item) for item in reference.SYNTHETIC_BREATH_INTERVALS],
            reference.CONTROL_SOURCE_SAMPLES)
        self.assertEqual(len(checked), 5)
        self.assertEqual(sum(1 for item in checked
                             if item["label"] == "breath_removable"), 3)
        self.assertEqual(sum(1 for item in checked
                             if item["label"] == "breath_preserve"), 2)

    def test_accounting_counts_and_separation(self) -> None:
        accounting = reference.breath_interval_accounting(
            reference.synthetic_input_pcm(),
            [dict(item) for item in reference.SYNTHETIC_BREATH_INTERVALS])
        self.assertEqual(accounting["removable_breath_samples"], 4800)
        self.assertEqual(accounting["preserved_breath_samples"], 3200)
        self.assertEqual(accounting["breath_samples"], 8000)
        self.assertEqual(accounting["non_breath_samples"], 40000)
        self.assertEqual(accounting["duration_s"], "3")
        self.assertEqual(accounting["output_duration_s"], "3")
        self.assertEqual(accounting["duration_ratio"], "1")
        self.assertTrue(accounting["duration_conserved"])
        self.assertEqual(accounting["changed_samples_outside_removable"], 0)
        self.assertEqual(accounting["changed_samples_in_preserved_breath"], 0)
        self.assertEqual(
            accounting["changed_samples"]
            + accounting["already_zero_removable_samples"],
            accounting["removable_breath_samples"])

    def test_ledger_timestamps_are_exact(self) -> None:
        accounting = reference.breath_interval_accounting(
            reference.synthetic_input_pcm(),
            [dict(item) for item in reference.SYNTHETIC_BREATH_INTERVALS])
        first = accounting["interval_ledger"][0]
        self.assertEqual(first["start_ns"], "200000000")
        self.assertEqual(first["end_ns"], "300000000")
        self.assertEqual(first["duration_ns"], "100000000")
        self.assertEqual(first["duration_s"], "1/10")
        self.assertEqual(first["decision"], "gate_to_zero")
        self.assertTrue(accounting["decision_timestamps_tied_to_source"])

    def test_gate_only_changes_removable_samples(self) -> None:
        source = reference.synthetic_input_pcm()
        intervals = [dict(item) for item in reference.SYNTHETIC_BREATH_INTERVALS]
        gated = reference.synthetic_gated_output_pcm(source, intervals)
        removable = set()
        for item in intervals:
            if item["label"] == "breath_removable":
                removable.update(range(item["start"], item["end"]))
        for index, (before, after) in enumerate(zip(source, gated)):
            if index in removable:
                self.assertEqual(after, 0.0)
            else:
                self.assertEqual(after, before)

    def test_control_is_not_candidate_output(self) -> None:
        accounting = reference.breath_interval_accounting(
            reference.synthetic_input_pcm(),
            [dict(item) for item in reference.SYNTHETIC_BREATH_INTERVALS])
        self.assertFalse(accounting["detector_executed"])
        self.assertFalse(accounting["performs_breath_detection"])
        self.assertFalse(accounting["performs_model_inference"])
        self.assertTrue(accounting["uses_oracle_labels"])
        self.assertFalse(accounting["is_candidate_removal_output"])
        self.assertEqual(accounting["qualification_effect"], "none")

    def test_interval_validation_rejects_bad_shapes(self) -> None:
        total = reference.CONTROL_SOURCE_SAMPLES
        cases = [
            lambda: reference.validate_breath_intervals([], total),
            lambda: reference.validate_breath_intervals(None, total),
            lambda: reference.validate_breath_intervals(b"ab", total),
            lambda: reference.validate_breath_intervals([1], total),
            lambda: reference.validate_breath_intervals(
                [{"start": 0, "end": 1}], total),
            lambda: reference.validate_breath_intervals(
                [{"start": 0, "end": 1, "label": "x", "extra": 1}], total),
            lambda: reference.validate_breath_intervals(
                [{"start": True, "end": 1, "label": "breath_removable"}],
                total),
            lambda: reference.validate_breath_intervals(
                [{"start": 0.0, "end": 1, "label": "breath_removable"}],
                total),
            lambda: reference.validate_breath_intervals(
                [{"start": -1, "end": 1, "label": "breath_removable"}],
                total),
            lambda: reference.validate_breath_intervals(
                [{"start": 1, "end": 1, "label": "breath_removable"}],
                total),
            lambda: reference.validate_breath_intervals(
                [{"start": 2, "end": 1, "label": "breath_removable"}],
                total),
            lambda: reference.validate_breath_intervals(
                [{"start": 0, "end": total + 1,
                  "label": "breath_removable"}], total),
            lambda: reference.validate_breath_intervals(
                [{"start": 0, "end": 10, "label": "breath_removable"},
                 {"start": 5, "end": 15, "label": "breath_preserve"}], total),
            lambda: reference.validate_breath_intervals(
                [{"start": 20, "end": 30, "label": "breath_removable"},
                 {"start": 0, "end": 10, "label": "breath_preserve"}], total),
            lambda: reference.validate_breath_intervals(
                [{"start": 0, "end": 1, "label": "click"}], total),
        ]
        for action in cases:
            with self.assertRaises(reference.Reject):
                action()


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_complete_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["source_revision"], "a" * 40)
        self.assertFalse(result["revision_pin_available"])
        self.assertEqual(result["files_checked"],
                         len(reference.CALLER_FILE_PAIRS))
        self.assertTrue(result["breath_policy_checked"])
        self.assertTrue(result["natural_event_labels_checked"])
        self.assertTrue(result["output_use_grant_checked"])
        self.assertFalse(result["detector_executed"])

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["event_label_manifest_path"]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["detector_weights_path"]).write_bytes(b"tampered")
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
            manifest["config_path"] = "config.json"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_short_or_nonhex_revision(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["source_revision"] = "7dae8a2"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
            manifest["source_revision"] = "g" * 40
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_variant(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["variant"] = "offline_batch_removal"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_float_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["sample_rate_hz"] = 16000.0
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["sample_rate_hz"] = 48000
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
            manifest = _manifest_fixture(Path(raw))
            manifest["channels"] = 2
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
            manifest = _manifest_fixture(Path(raw))
            manifest["frame_samples"] = 512
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
        self.assertFalse(control["detector_executed"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(control["accounting"]["duration_ratio"], "1")
        self.assertFalse(control["geometry"]["performs_breath_detection"])
        self.assertFalse(control["geometry"]["task_geometry_asserted"])
        self.assertTrue(control["geometry"]["uses_oracle_labels"])

    def test_acceptance_outcomes_are_all_unmeasured(self) -> None:
        control = reference.build_control()
        self.assertEqual(len(control["acceptance_outcomes"]), 8)
        self.assertTrue(all(item["measured"] is False
                            and item["value"] is None
                            for item in control["acceptance_outcomes"]))

    def test_rate_profile_controls_are_structural_only(self) -> None:
        controls = reference.build_control()["rate_profile_controls"]
        self.assertTrue(controls["duration_conserved"])
        self.assertFalse(controls["playback_rate_cases_measured"])
        self.assertFalse(controls["pitch_measured"])
        self.assertFalse(controls["transient_audibility_measured"])
        self.assertFalse(controls["speech_preservation_measured"])
        self.assertFalse(controls["device_buffering_measured"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = reference.build_contract()

    def test_top_level_decision(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["mode"], "feasibility")
        self.assertEqual(report["profile"], "rate")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertTrue(report["proposal_only"])
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
        self.assertIn("breath_candidate_source_absent", ids)
        self.assertIn("breath_detector_weights_absent", ids)
        self.assertIn("natural_breath_labels_absent", ids)
        self.assertIn("rights_and_consent_uncleared", ids)

    def test_qualification_blocked(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(qualification["no_missing_result_qualifies_candidate"])
        self.assertEqual(qualification["blocked_gate_count"], 8)

    def test_boundary_is_closed(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "abi_change",
                    "provider_registration", "production_callback_registered",
                    "descriptor_registry_change", "shared_build_or_ci_change",
                    "installed_v0_behavior_change", "asset_bundled",
                    "weights_vendored", "model_loaded", "sdk_callback_invoked",
                    "network_used"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_is_closed(self) -> None:
        scope = self.report["scope"]
        for key in ("real_audio", "real_corpus", "real_breath_labels",
                    "model_executed", "detector_executed",
                    "detector_weights_loaded", "weights_downloaded",
                    "runtime_invoked", "vendor_runtime_invoked", "network_used",
                    "device_timing", "listening", "public_benchmark",
                    "release_claim", "breath_detection_performed",
                    "acoustic_removal_reference_produced"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["task_local_only"], True)

    def test_no_fabricated_identity(self) -> None:
        upstream = self.report["upstream_identity"]
        self.assertIsNone(upstream["revision"])
        self.assertIsNone(upstream["project_url"])
        self.assertIsNone(upstream["repository_url"])
        self.assertFalse(upstream["revision_pin_available"])
        self.assertEqual(upstream["geometry_status"], "unestablished")
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertIsNone(requirements["detector_weights"]["sha256"])
        self.assertIsNone(requirements["upstream_revision"]["sha256"])
        self.assertIsNone(requirements["source_checkout"]["revision"])
        self.assertIsNone(
            requirements["exact_runtime"]["runtime_lock_sha256"])

    def test_rate_profile_has_no_satisfied_item(self) -> None:
        profile = self.report["rate_profile"]
        self.assertEqual(profile["name"], "rate")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_model_metrics"])
        self.assertEqual(len(profile["required_items"]),
                         len(reference.RATE_REQUIREMENTS))
        self.assertTrue(all(item["qualification_effect"] == "none"
                            for item in profile["required_items"]))
        self.assertTrue(all(item["satisfied_for_qualification"] is False
                            for item in profile["required_items"]))

    def test_audit_is_absent_and_not_qualified(self) -> None:
        audit = self.report["asset_audit"]
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["audit_result"], "absent")
        self.assertFalse(audit["source_present"])
        self.assertFalse(audit["license_present"])
        self.assertFalse(audit["weights_present"])
        self.assertFalse(audit["breath_policy_present"])
        self.assertFalse(audit["natural_breath_labels_present"])
        self.assertFalse(audit["output_use_grant_present"])
        self.assertTrue(audit["all_absence_probes_absent"])

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_source_reported_context_is_adjacent_only(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"],
                         "adjacent_sibling_reported_not_measured_here")
        self.assertEqual(context["candidate_matrix_record"], 38)
        self.assertEqual(context["record_status"], "partially evaluated")
        self.assertFalse(context["breath_specific_result_present"])
        self.assertFalse(context["pinned_candidate_source_present"])
        self.assertIsNone(context["project_url"])
        self.assertIsNone(context["repository_url"])
        self.assertEqual(len(context["sibling_context_not_attributed"]), 5)
        self.assertIn("breaths remain untested",
                      " ".join(context["sibling_context_not_attributed"]))

    def test_missing_artifacts_recorded(self) -> None:
        for path in (reference.MISSING_SOURCE_PATH,
                     reference.MISSING_WEIGHTS_PATH,
                     reference.MISSING_POLICY_PATH,
                     reference.MISSING_LABELS_PATH,
                     reference.RUNTIME_ENV_PATH,
                     reference.RUNTIME_LOCK_PATH,
                     reference.RIGHTS_RECORD_PATH,
                     reference.OUTPUT_USE_GRANT_PATH,
                     reference.COHORT_MANIFEST_PATH,
                     reference.PARITY_MANIFEST_PATH):
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

    def test_on_disk_contract_matches_generator(self) -> None:
        self.assertEqual((HERE / "contract.json").read_bytes(),
                         reference.canonical_contract_bytes())

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
        self.assertEqual(len(contract["rate_profile_requirements"]),
                         len(reference.RATE_REQUIREMENTS))

    def test_sources_manifest_has_no_tasks_json(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line and not line.startswith("#"):
                self.assertNotIn("TASKS.json", line)


if __name__ == "__main__":
    unittest.main()
