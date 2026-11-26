# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local Krisp VI 2.5 evidence package."""

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
    runtime = root / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    files = {
        "config_path": b"voice_isolation: 2.5\ndefault: true\n",
        "corpus_manifest_path": b"corpus-files",
        "dnsmos_checkpoint_path": b"nisqa-checkpoint",
        "dnsmos_environment_lock_path": b"torch==0.0.0\n",
        "processed_outputs_manifest_path": b"outputs-files",
        "redistribution_approval_path": b"redistribution-approval",
        "rights_record_path": b"rights-record",
        "vendor_license_path": b"vendor-license",
        "vendor_runtime_lock_path": b"vendor-runtime-lock",
    }
    manifest = {
        "channels": reference.COMPARISON_CHANNELS,
        "platform": "macos-arm64",
        "sample_rate_hz": reference.REQUIRED_SAMPLE_RATE_HZ,
        "scope": reference.CALLER_SCOPE,
        "variant": reference.CALLER_VARIANT,
        "vendor_entitlement_id": "krisp-entitlement-0001",
        "vendor_runtime_path": str(runtime),
        "vendor_runtime_version": "2.5.0",
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


class SourceAuditTests(unittest.TestCase):
    def test_vendor_runtime_is_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["vendor_runtime_present"])
        self.assertIsNone(audit["vendor_runtime_version"])
        self.assertFalse(audit["vendor_runtime_pin_available"])

    def test_no_license_scorer_or_data(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["vendor_license_present"])
        self.assertEqual(audit["vendor_license_files"], [])
        self.assertFalse(audit["scorer_present"])
        self.assertFalse(audit["scorer_env_present"])
        self.assertFalse(audit["scorer_lock_present"])
        self.assertFalse(audit["corpus_present"])
        self.assertFalse(audit["processed_outputs_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["comparison_manifest_present"])
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

    def test_geometry_is_recorded_for_scoring_only(self) -> None:
        config = reference.audit_assets()["requested_config"]
        self.assertEqual(config["comparison_geometry"]["status"],
                         "recorded_for_scoring_only")
        self.assertEqual(config["vendor_runtime_geometry_status"],
                         "unestablished")
        self.assertEqual(config["corpus_revision"],
                         reference.CORPUS_REVISION)
        self.assertEqual(config["processed_revision"],
                         reference.PROCESSED_REVISION)
        self.assertIsNone(config["vendor_runtime_version"])


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"],
                         "external-adapter")
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
        self.assertRegex(reference.CORPUS_REVISION, r"^[0-9a-f]{40}$")
        self.assertRegex(reference.PROCESSED_REVISION, r"^[0-9a-f]{40}$")
        self.assertIsNone(reference.VENDOR_RUNTIME_VERSION)


class PcmTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        first = reference.synthetic_source_pcm()
        second = reference.synthetic_source_pcm()
        self.assertEqual(first, second)
        self.assertEqual(len(first), reference.CONTROL_SOURCE_SAMPLES)
        self.assertEqual(len(reference.synthetic_output_pcm()),
                         reference.CONTROL_OUTPUT_SAMPLES)

    def test_synthetic_pcm_is_finite_and_bounded(self) -> None:
        source = reference.validate_pcm(
            reference.synthetic_source_pcm(),
            reference.CONTROL_SAMPLE_RATE_HZ)
        output = reference.validate_pcm(
            reference.synthetic_output_pcm(),
            reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertTrue(all(math.isfinite(value) for value in source))
        self.assertTrue(all(math.isfinite(value) for value in output))
        self.assertLessEqual(max(abs(v) for v in source), 1.0)
        self.assertLessEqual(max(abs(v) for v in output), 1.0)

    def test_pcm_summary_is_deterministic(self) -> None:
        signal = reference.synthetic_source_pcm()
        first = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        second = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertEqual(first, second)
        self.assertEqual(first["duration_s"], "3")
        self.assertEqual(first["channels"], 1)

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

    def test_duration_accounting_exact(self) -> None:
        result = reference.duration_accounting(
            reference.CONTROL_SOURCE_SAMPLES, reference.CONTROL_OUTPUT_SAMPLES)
        self.assertEqual(result["source_duration_s"], "3")
        self.assertEqual(result["output_duration_s"], "2")
        self.assertEqual(result["duration_ratio"], "2/3")

    def test_duration_accounting_rejects_bad_counts(self) -> None:
        for value in (0, -1, True, 1.5, "4"):
            with self.assertRaises(reference.Reject):
                reference.duration_accounting(value, 1)
            with self.assertRaises(reference.Reject):
                reference.duration_accounting(1, value)

    def test_alignment_is_offline(self) -> None:
        alignment = reference.alignment_accounting(32000)
        self.assertEqual(alignment["mode"], "offline_whole_utterance")
        self.assertFalse(alignment["streaming_supported"])
        self.assertTrue(alignment["whole_clip_required"])
        self.assertEqual(alignment["tail_samples"], 32000)


class ScoringTests(unittest.TestCase):
    def test_scenario_balanced_mean_is_exact(self) -> None:
        result = reference.scenario_balanced_mean(
            {name: list(values)
             for name, values in reference.SYNTHETIC_SCENARIO_SCORES.items()})
        self.assertEqual(result["overall"]["mean"], "11/3")
        self.assertEqual(result["scenarios"]["work"]["mean"], "11/3")
        self.assertEqual(result["scenarios"]["call_center"]["mean"], "13/3")
        self.assertEqual(result["scenarios"]["phone_calls"]["mean"], "3")
        self.assertEqual(result["aggregation"],
                         "unweighted_mean_of_three_scenario_means")
        self.assertEqual(result["label"],
                         reference.CONTROL_PLAN_PROVENANCE)
        self.assertEqual(result["qualification_effect"], "none")

    def test_scenario_balanced_mean_rejects_invalid(self) -> None:
        good = {name: list(values)
                for name, values in reference.SYNTHETIC_SCENARIO_SCORES.items()}
        cases = [
            lambda: reference.scenario_balanced_mean([]),
            lambda: reference.scenario_balanced_mean(
                {key: value for key, value in good.items()
                 if key != "work"}),
            lambda: reference.scenario_balanced_mean(
                dict(good, music=["4"])),
            lambda: reference.scenario_balanced_mean(dict(good, work=[])),
            lambda: reference.scenario_balanced_mean(
                dict(good, work=[math.nan])),
            lambda: reference.scenario_balanced_mean(
                dict(good, work=[math.inf])),
            lambda: reference.scenario_balanced_mean(
                dict(good, work=[-math.inf])),
            lambda: reference.scenario_balanced_mean(
                dict(good, work=[5.5])),
            lambda: reference.scenario_balanced_mean(
                dict(good, work=[0.5])),
            lambda: reference.scenario_balanced_mean(
                dict(good, work=[True])),
            lambda: reference.scenario_balanced_mean(
                dict(good, work=["great"])),
        ]
        for action in cases:
            with self.assertRaises(reference.Reject):
                action()

    def test_scenario_weights_are_equal(self) -> None:
        result = reference.scenario_balanced_mean({
            "work": ["5"],
            "call_center": ["1", "1", "1"],
            "phone_calls": ["3"],
        })
        self.assertEqual(result["overall"]["mean"], "3")
        self.assertEqual(result["scenarios"]["call_center"]["count"], 3)


class ManifestTests(unittest.TestCase):
    def test_manifest_accepts_complete_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["vendor_runtime_version"], "2.5.0")
        self.assertFalse(result["runtime_version_pin_available"])
        self.assertEqual(result["scope"], reference.CALLER_SCOPE)
        self.assertEqual(result["files_checked"],
                         len(reference.CALLER_FILE_PAIRS))
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["vendor_runtime_imported"])
        self.assertFalse(result["scorer_executed"])

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["vendor_license_path"]).unlink()
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
            Path(manifest["vendor_runtime_path"]).rmdir()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["config_path"] = "config.json"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_bad_version(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["vendor_runtime_version"] = "2.5"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_streaming_variant(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["variant"] = "incremental_streaming"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_scope(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["scope"] = "vendor_runtime_adapter"
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
            manifest["sample_rate_hz"] = 4000
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_noncomparison_rate(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["sample_rate_hz"] = 48000
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_empty_entitlement(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["vendor_entitlement_id"] = ""
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_bad_platform(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["platform"] = "macOS ARM64"
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
        self.assertEqual(control["scorer"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertEqual(control["duration"]["duration_ratio"], "2/3")
        self.assertFalse(control["alignment"]["streaming_supported"])
        self.assertFalse(control["geometry"]["vendor_runtime_geometry_asserted"])
        self.assertEqual(control["geometry"]["vendor_scope"],
                         reference.VENDOR_OUTPUT_SCOPING)
        self.assertEqual(control["synthetic_scoring"]["overall"]["mean"],
                         "11/3")

    def test_acceptance_outcomes_are_all_unmeasured(self) -> None:
        control = reference.build_control()
        self.assertEqual(len(control["acceptance_outcomes"]), 5)
        self.assertTrue(all(item["measured"] is False
                            and item["value"] is None
                            for item in control["acceptance_outcomes"]))

    def test_positive_structure_control_is_labelled(self) -> None:
        control = reference.build_control()
        positive = control["accepted_control"]
        self.assertTrue(positive["accepted"])
        self.assertEqual(positive["id"],
                         "synthetic_structure_only_manifest")
        self.assertFalse(positive["model_executed"])
        self.assertFalse(positive["vendor_runtime_imported"])
        self.assertFalse(positive["scorer_executed"])
        self.assertEqual(positive["qualification_effect"], "none")
        self.assertEqual(positive["scope"], reference.CALLER_SCOPE)
        self.assertEqual(positive["variant"], reference.CALLER_VARIANT)


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
        self.assertEqual(report["profile"], "external")
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

    def test_exact_blockers(self) -> None:
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), len(reference.EXACT_BLOCKERS))
        self.assertEqual([item["id"] for item in blockers],
                         [item["id"] for item in reference.EXACT_BLOCKERS])
        self.assertTrue(all(item["state"] == "absent" for item in blockers))
        ids = [item["id"] for item in blockers]
        for expected in ("vendor_runtime_absent",
                         "vendor_license_and_terms_unverified",
                         "vendor_sdk_abi_undocumented",
                         "dnsmos_c_scorer_absent",
                         "dnsmos_c_runtime_absent",
                         "source_corpus_absent",
                         "processed_vendor_outputs_absent",
                         "corpus_and_output_rights_uncleared",
                         "comparison_manifest_and_parity_absent",
                         "wer_ensemble_unavailable"):
            self.assertIn(expected, ids)

    def test_qualification_blocked(self) -> None:
        qualification = self.report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertFalse(qualification["candidate_qualified"])
        self.assertTrue(qualification["no_missing_result_qualifies_candidate"])
        self.assertEqual(qualification["blocked_gate_count"], 8)
        self.assertEqual(qualification["blocked_gate_ids"],
                         [gate["id"] for gate in self.report["gates"]])

    def test_boundary_is_closed(self) -> None:
        boundary = self.report["boundary"]
        for key in ("registered", "enabled_by_default", "default_selected",
                    "public_api_abi_change", "provider_registration",
                    "production_callback_registered", "descriptor_registry_change",
                    "shared_build_or_ci_change", "installed_v0_behavior_change",
                    "asset_bundled", "weights_vendored", "sdk_callback_invoked",
                    "network_used", "vendor_runtime_linked",
                    "vendor_outputs_bundled"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_is_closed(self) -> None:
        scope = self.report["scope"]
        for key in ("real_audio", "real_corpus", "real_vendor_outputs",
                    "real_vendor_runtime", "model_executed", "scorer_executed",
                    "weights_loaded", "weights_downloaded", "runtime_invoked",
                    "vendor_runtime_invoked", "network_used", "device_timing",
                    "listening", "public_benchmark", "release_claim"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["task_local_only"], True)

    def test_no_fabricated_identity(self) -> None:
        upstream = self.report["upstream_identity"]
        self.assertEqual(upstream["benchmark_url"], reference.BENCHMARK_URL)
        self.assertIsNone(upstream["vendor_runtime_version"])
        self.assertFalse(upstream["vendor_runtime_pin_available"])
        self.assertFalse(upstream["vendor_runtime_present"])
        self.assertFalse(upstream["vendor_source_checkout_available"])
        self.assertEqual(upstream["vendor_scope"],
                         reference.VENDOR_OUTPUT_SCOPING)
        self.assertEqual(upstream["corpus_revision"],
                         reference.CORPUS_REVISION)
        self.assertEqual(upstream["processed_outputs_revision"],
                         reference.PROCESSED_REVISION)
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertIsNone(requirements["vendor_runtime"]["build_sha256"])
        self.assertIsNone(requirements["vendor_runtime"]["version"])
        self.assertIsNone(requirements["dnsmos_c_scorer"]["checkpoint_sha256"])
        self.assertIsNone(requirements["dnsmos_c_runtime"]["lock_sha256"])
        self.assertIsNone(requirements["comparison_manifest"]["sha256"])
        self.assertFalse(requirements["source_corpus"]["local_copy_present"])
        self.assertFalse(
            requirements["processed_vendor_outputs"]["local_copy_present"])
        self.assertEqual(requirements["source_corpus"]["recorded_revision"],
                         reference.CORPUS_REVISION)
        self.assertEqual(
            requirements["processed_vendor_outputs"]["recorded_bytes"],
            reference.PROCESSED_BYTES)

    def test_external_profile_has_no_satisfied_item(self) -> None:
        profile = self.report["external_profile"]
        self.assertEqual(profile["name"], "external")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["real_external_metrics"])
        self.assertTrue(all(item["qualification_effect"] == "none"
                            for item in profile["required_items"]))
        self.assertEqual(len(profile["required_items"]),
                         len(reference.EXTERNAL_REQUIREMENTS))
        separation = profile["separation"]
        self.assertEqual(separation["local_vendor_runtime"], "absent")
        self.assertEqual(separation["vendor_output_scoring"], "not_run")
        self.assertEqual(separation["vendor_claim"],
                         "source_reported_only")

    def test_audit_is_absent_and_not_qualified(self) -> None:
        audit = self.report["asset_audit"]
        self.assertFalse(audit["qualified"])
        self.assertEqual(audit["audit_result"], "absent")
        self.assertFalse(audit["vendor_runtime_present"])
        self.assertFalse(audit["vendor_license_present"])
        self.assertFalse(audit["scorer_present"])
        self.assertFalse(audit["corpus_present"])
        self.assertFalse(audit["processed_outputs_present"])
        self.assertTrue(audit["all_absence_probes_absent"])

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_source_reported_context_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"],
                         "source_reported_not_reproduced_here")
        self.assertEqual(context["benchmark_url"],
                         reference.BENCHMARK_URL)
        self.assertEqual(context["corpus"]["revision"],
                         reference.CORPUS_REVISION)
        self.assertEqual(context["corpus"]["license"],
                         reference.CORPUS_LICENSE)
        self.assertEqual(context["processed_outputs"]["revision"],
                         reference.PROCESSED_REVISION)
        self.assertEqual(context["processed_outputs"]["bytes"],
                         reference.PROCESSED_BYTES)
        self.assertEqual(context["vendor_published_dnsmos_c"]["label"],
                         "vendor_published_not_reproduced_here")
        self.assertEqual(context["vendor_published_wer"]["engine_count"],
                         reference.WER_ENGINE_COUNT)
        self.assertIsNone(
            context["vendor_published_wer"]["local_audio_enhance_wer"])
        self.assertEqual(
            len(context["sibling_context_not_attributed"]), 4)

    def test_missing_artifacts_recorded(self) -> None:
        for path in (reference.MISSING_RUNTIME_PATH,
                     reference.MISSING_LICENSE_PATH,
                     reference.MISSING_SCORER_PATH,
                     reference.MISSING_SCORER_ENV_PATH,
                     reference.MISSING_SCORER_LOCK_PATH,
                     reference.MISSING_CORPUS_PATH,
                     reference.MISSING_OUTPUTS_PATH,
                     reference.MISSING_COMPARISON_PATH,
                     reference.MISSING_PARITY_PATH,
                     reference.MISSING_RIGHTS_PATH):
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
