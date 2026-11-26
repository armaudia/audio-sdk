# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local Krisp NC/BVC evidence package."""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest

import reference

HERE = Path(__file__).resolve().parent


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest_fixture(root: Path) -> dict:
    install_root = root / "sdk"
    install_root.mkdir(parents=True, exist_ok=True)
    files = {
        "config_path": b'{"models":["noise_cancellation"]}\n',
        "entitlement_path": b"krisp-entitlement",
        "license_record_path": b"krisp-license-record",
        "model_bundle_path": b"krisp-model-bundle",
        "runtime_lock_path": b"krisp-sdk==0.0.0\n",
        "vendor_terms_path": b"krisp-vendor-terms",
    }
    manifest = {
        "background_voice_cancellation_enabled": True,
        "channels": reference.CHANNELS,
        "entitlement_approved": True,
        "entitlement_id": "eval-0001",
        "install_root": str(install_root),
        "noise_cancellation_enabled": True,
        "other_features_disabled": True,
        "platform": "macos-arm64",
        "product": reference.CALLER_PRODUCT,
        "release_version": "0.0.0",
        "sample_rate_hz": reference.CONTROL_SAMPLE_RATE_HZ,
        "scope": reference.CALLER_SCOPE,
        "telemetry_disclosure": True,
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
        self.assertEqual(reference.fraction_text(Fraction(2, 3)), "2/3")
        self.assertEqual(reference.fraction_text(Fraction(6, 3)), "2")


class AuditTests(unittest.TestCase):
    def test_sdk_and_assets_are_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["sdk_present"])
        self.assertFalse(audit["model_bundle_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])
        self.assertFalse(audit["license_record_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["vendor_output_present"])
        self.assertFalse(audit["results_present"])

    def test_absence_probes_are_all_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertEqual(len(audit["absence_probes"]),
                         len(reference.ABSENCE_PROBES))
        self.assertEqual(
            [item["probe"] for item in audit["absence_probes"]],
            list(reference.ABSENCE_PROBES))
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertTrue(all(item["present"] is False
                            for item in audit["absence_probes"]))
        self.assertEqual(len(reference.ABSENCE_PROBES), 22)

    def test_asset_register_has_no_krisp_entry(self) -> None:
        register = reference.audit_assets()["asset_register"]
        self.assertTrue(register["present"])
        self.assertEqual(register["candidate_count"], 20)
        self.assertFalse(register["krisp_entry_present"])
        self.assertEqual(register["entries_matching_krisp"], 0)
        self.assertRegex(register["candidate_ids_sha256"], r"^[0-9a-f]{64}$")

    def test_geometry_is_unestablished(self) -> None:
        config = reference.audit_assets()["requested_config"]
        self.assertEqual(config["geometry_status"], "unestablished")
        self.assertEqual(config["task_scope"], reference.TASK_SCOPE)
        self.assertEqual(config["profile"], "enhancement")
        self.assertIsNone(config["release_pin"])

    def test_enhancement_profile_row(self) -> None:
        row = reference._profile_row()
        self.assertEqual(row["row_count"], 1)
        self.assertTrue(row["all_phrases_present"])
        self.assertIn("| Enhancement |", row["row"])


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "external-adapter")
        self.assertFalse(identity["whole_file_hashed"])
        self.assertEqual(identity["gating"], "stable_identity_only")
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
        self.assertIsNone(reference.VENDOR_DOCUMENTATION_LOCATOR)


class PcmTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        first = reference.synthetic_noisy_pcm()
        second = reference.synthetic_noisy_pcm()
        self.assertEqual(first, second)
        self.assertEqual(len(first), reference.CONTROL_SOURCE_SAMPLES)
        self.assertEqual(len(reference.synthetic_clean_pcm()),
                         reference.CONTROL_SOURCE_SAMPLES)

    def test_synthetic_pcm_is_finite_and_bounded(self) -> None:
        noisy = reference.validate_pcm(
            reference.synthetic_noisy_pcm(),
            reference.CONTROL_SAMPLE_RATE_HZ)
        clean = reference.validate_pcm(
            reference.synthetic_clean_pcm(),
            reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertTrue(all(math.isfinite(value) for value in noisy))
        self.assertTrue(all(math.isfinite(value) for value in clean))
        self.assertLessEqual(max(abs(v) for v in noisy), 1.0)
        self.assertLessEqual(max(abs(v) for v in clean), 1.0)

    def test_identity_and_scaled_controls_exact(self) -> None:
        noisy = reference.synthetic_noisy_pcm()
        identity = reference.identity_control(noisy)
        scaled = reference.scaled_control(noisy)
        self.assertEqual(identity, list(noisy))
        self.assertEqual(scaled, [0.5 * value for value in noisy])
        self.assertEqual(
            reference.energy_accounting(noisy, identity)[
                "output_to_noisy_energy_ratio"], "1")
        self.assertEqual(
            reference.energy_accounting(noisy, scaled)[
                "output_to_noisy_energy_ratio"], "1/4")

    def test_pcm_summary_is_deterministic(self) -> None:
        signal = reference.synthetic_noisy_pcm()
        first = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        second = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertEqual(first, second)
        self.assertEqual(first["duration_s"], "2")
        self.assertEqual(first["channels"], 1)
        self.assertEqual(first["nonfinite_samples"], 0)

    def test_validate_pcm_accepts_integers(self) -> None:
        self.assertEqual(reference.validate_pcm([0, 0.5, -1]),
                         [0.0, 0.5, -1.0])

    def test_validate_pcm_rejects_invalid(self) -> None:
        cases = [
            lambda: reference.validate_pcm([]),
            lambda: reference.validate_pcm(b"ab"),
            lambda: reference.validate_pcm(None),
            lambda: reference.validate_pcm([0.0], 8000),
            lambda: reference.validate_pcm(
                [0.0], reference.CONTROL_SAMPLE_RATE_HZ, 2),
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

    def test_frame_accounting_exact(self) -> None:
        result = reference.frame_accounting(
            reference.CONTROL_SOURCE_SAMPLES, reference.CONTROL_OUTPUT_SAMPLES)
        self.assertEqual(result["frame_samples"], 160)
        self.assertEqual(result["hop_samples"], 160)
        self.assertEqual(result["frame_count"], 200)
        self.assertEqual(result["content_delay_samples"], 0)
        self.assertTrue(result["sample_conservation"])
        self.assertFalse(result["vendor_timing_measured"])
        self.assertFalse(result["device_timing_measured"])

    def test_frame_accounting_rejects_bad_counts(self) -> None:
        for value in (0, -1, True, 1.5, "4"):
            with self.assertRaises(reference.Reject):
                reference.frame_accounting(value, 320)
        with self.assertRaises(reference.Reject):
            reference.frame_accounting(321, 321)
        with self.assertRaises(reference.Reject):
            reference.frame_accounting(320, 480)


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_complete_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["product"], reference.CALLER_PRODUCT)
        self.assertEqual(result["scope"], reference.CALLER_SCOPE)
        self.assertEqual(result["models"], [
            "noise_cancellation", "background_voice_cancellation"])
        self.assertEqual(result["files_checked"],
                         len(reference.CALLER_FILE_PAIRS))
        self.assertFalse(result["vendor_sdk_imported"])
        self.assertFalse(result["vendor_runtime_executed"])
        self.assertFalse(result["model_executed"])

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["model_bundle_path"]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["config_path"]).write_bytes(b"tampered")
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_missing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["install_root"]).rmdir()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["config_path"] = "config.json"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_short_or_nonhex_release(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["release_version"] = "1.0"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
            manifest["release_version"] = "1.0.x"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_unapproved_entitlement(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["entitlement_approved"] = False
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_scope(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["scope"] = "unlicensed_benchmark"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_float_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["channels"] = 1.0
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_out_of_range_rate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["sample_rate_hz"] = 44100
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_disabled_isolation(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["other_features_disabled"] = False
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
            manifest = _manifest_fixture(Path(raw))
            manifest["noise_cancellation_enabled"] = False
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
        self.assertFalse(control["vendor_runtime_executed"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(
            control["identity_energy"]["output_to_noisy_energy_ratio"], "1")
        self.assertEqual(
            control["scaled_energy"]["output_to_noisy_energy_ratio"], "1/4")
        self.assertFalse(control["geometry"]["krisp_geometry_asserted"])
        self.assertEqual(control["geometry"]["task_scope"],
                         reference.TASK_SCOPE)

    def test_acceptance_outcomes_are_all_unmeasured(self) -> None:
        control = reference.build_control()
        self.assertEqual(len(control["acceptance_outcomes"]), 8)
        self.assertTrue(all(item["measured"] is False
                            and item["value"] is None
                            for item in control["acceptance_outcomes"]))

    def test_positive_structure_control_is_labelled(self) -> None:
        control = reference.build_control()
        positive = control["accepted_control"]
        self.assertTrue(positive["accepted"])
        self.assertEqual(positive["id"],
                         "synthetic_structure_only_licensed_manifest")
        self.assertFalse(positive["vendor_sdk_imported"])
        self.assertFalse(positive["vendor_runtime_executed"])
        self.assertEqual(positive["qualification_effect"], "none")
        self.assertEqual(positive["scope"], reference.CALLER_SCOPE)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = json.loads((HERE / "contract.json").read_text())

    def test_top_level_decision(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["mode"], "external-adapter")
        self.assertEqual(report["profile"], "enhancement")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertTrue(report["proposal_only"])
        self.assertTrue(report["incomplete"])
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
        self.assertEqual(self.report["remaining_gates"],
                         [gate["id"] for gate in gates])

    def test_exact_blockers_and_artifacts(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), len(reference.EXACT_BLOCKERS))
        self.assertEqual([item["id"] for item in blockers],
                         [item["id"] for item in reference.EXACT_BLOCKERS])
        self.assertTrue(all(item["state"] == "absent" for item in blockers))
        artifacts = self.report["required_artifacts"]
        self.assertEqual(len(artifacts), 8)
        self.assertTrue(all(item["present"] is False
                            and item["verified"] is False
                            and item["blocked"] is True
                            and item["sha256"] is None
                            and item["bytes"] is None
                            for item in artifacts))

    def test_qualification_blocked(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(qualification["no_missing_result_qualifies_candidate"])
        self.assertEqual(qualification["blocked_gate_count"], 8)
        self.assertEqual(qualification["blocked_gate_ids"],
                         [gate["id"] for gate in self.report["gates"]])
        self.assertEqual(qualification["decision"], "DEFER")

    def test_boundary_is_closed(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "production_callback_registered", "descriptor_registry_change",
                    "shared_build_or_ci_change", "installed_v0_behavior_change",
                    "asset_bundled", "weights_vendored", "sdk_callback_invoked",
                    "network_used", "adapter_added", "vendor_sdk_imported",
                    "vendor_sdk_linked"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_is_closed(self) -> None:
        scope = self.report["scope"]
        for key in ("real_audio", "real_corpus", "real_krisp_runtime",
                    "model_executed", "weights_loaded", "weights_downloaded",
                    "runtime_invoked", "vendor_runtime_executed",
                    "vendor_sdk_imported", "vendor_output_read",
                    "network_used", "device_timing", "listening",
                    "benchmark_claim", "public_benchmark", "release_claim",
                    "peer_evidence_inherited", "processed_data_present"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["task_local_only"], True)

    def test_no_fabricated_vendor_identity(self) -> None:
        vendor = self.report["vendor_identity"]
        self.assertEqual(vendor["vendor"], "Krisp")
        self.assertIsNone(vendor["release_version"])
        self.assertIsNone(vendor["abi_version"])
        self.assertIsNone(vendor["artifact_sha256"])
        self.assertEqual(vendor["model_families_verified"], [])
        self.assertFalse(vendor["entitlement_approved"])
        self.assertFalse(vendor["runtime_present"])
        self.assertFalse(vendor["vendor_output_present"])
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertIsNone(requirements["exact_release_and_platform_sdk"]["sha256"])
        self.assertIsNone(requirements["model_bundle"]["sha256"])
        self.assertIsNone(requirements["runtime_lock"]["sha256"])
        self.assertIsNone(requirements["vendor_entitlement"]["sha256"])
        self.assertIsNone(
            requirements["exact_release_and_platform_sdk"]["revision"])

    def test_enhancement_profile_has_no_satisfied_item(self) -> None:
        profile = self.report["enhancement_profile"]
        self.assertEqual(profile["name"], "enhancement")
        self.assertTrue(profile["source_check"]["all_phrases_present"])
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_model_metrics"])
        self.assertTrue(all(item["qualification_effect"] == "none"
                            for item in profile["required_items"]))
        self.assertEqual(len(profile["required_items"]),
                         len(reference.ENHANCEMENT_REQUIREMENTS))

    def test_audit_is_absent_and_not_qualified(self) -> None:
        audit = self.report["asset_audit"]
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["audit_result"], "absent")
        self.assertFalse(audit["sdk_present"])
        self.assertFalse(audit["model_bundle_present"])
        self.assertFalse(audit["vendor_output_present"])
        self.assertTrue(audit["all_absence_probes_absent"])
        self.assertFalse(self.report["asset_registry"]["krisp_entry_present"])

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_source_reported_context_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"], "source_reported_not_measured_here")
        self.assertEqual(context["report_line"], 78)
        self.assertEqual(context["source"],
                         "research/noise_suppression_candidate_census.md")
        self.assertEqual(len(context["sibling_context_not_attributed"]), 3)
        self.assertEqual(
            context["reported_capabilities"]["model_family_count"], 2)

    def test_peer_and_sibling_evidence_not_inherited(self) -> None:
        self.assertEqual(self.report["merged_sibling_krisp_packages"], [])
        peers = self.report["peer_evidence"]
        self.assertTrue(peers)
        self.assertTrue(all(item["inherited_metrics"] is False
                            for item in peers))

    def test_missing_artifacts_recorded(self) -> None:
        for path in (reference.MISSING_SDK_PATH,
                     reference.MISSING_MODEL_BUNDLE_PATH,
                     reference.RUNTIME_ENV_PATH,
                     reference.RUNTIME_LOCK_PATH,
                     reference.RIGHTS_RECORD_PATH,
                     reference.COHORT_MANIFEST_PATH,
                     reference.VENDOR_OUTPUT_PATH,
                     reference.RESULTS_PATH):
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
