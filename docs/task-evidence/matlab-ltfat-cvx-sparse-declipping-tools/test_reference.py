# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the MATLAB/LTFAT/CVX tools blocker package."""

from __future__ import annotations

import hashlib
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
    matlab = root / "matlab"
    ltfat = root / "ltfat"
    cvx = root / "cvx"
    for directory in (source, matlab, ltfat, cvx):
        directory.mkdir(parents=True, exist_ok=True)
    files = {
        "config_path": b'{"threshold": 0.35, "alias": "toolbox"}\n',
        "license_record_path": b"license-record",
        "rights_record_path": b"rights-record",
        "reference_experiment_path": b'{"expected": "fixture"}',
        "cohort_manifest_path": b'{"cohort": "fixture"}',
        "parity_vector_path": b'{"parity": "fixture"}',
        "output_use_grant_path": b'{"grant": "fixture"}',
    }
    manifest = {
        "source_checkout_path": str(source),
        "source_revision": "a" * 40,
        "matlab_runtime_path": str(matlab),
        "matlab_version": "R2024a",
        "ltfat_path": str(ltfat),
        "ltfat_revision": "b" * 40,
        "cvx_path": str(cvx),
        "cvx_revision": "c" * 40,
        "tool_version": "0.0.0",
        "tool_install_path": str(source),
        "sample_rate_hz": reference.CONTROL_SAMPLE_RATE_HZ,
        "channels": reference.CHANNELS,
        "block_samples": 1600,
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
        self.assertEqual(reference.canonical_bytes({"z": -0.0}),
                         b'{"z":0.0}')

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

    def test_no_license_or_runtime(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["license_file_present"])
        self.assertEqual(audit["license_files"], [])
        self.assertFalse(audit["complete_runtime_present"])
        self.assertFalse(audit["matlab_env_present"])
        self.assertFalse(audit["matlab_env_manifest_present"])

    def test_no_experiment_rights_or_cohort(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["reference_experiment_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])
        self.assertFalse(audit["output_use_grant_present"])

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
        self.assertEqual(config["control_source_samples"], 16000)


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(identity["stable_fields"]["component"],
                         reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "external-adapter")
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

    def test_commits_are_full_hex_and_no_fake_revision(self) -> None:
        self.assertRegex(reference.BASE_COMMIT, r"^[0-9a-f]{40}$")
        self.assertIsNone(reference.UPSTREAM_REVISION)
        self.assertIsNone(reference.REPORTED_LICENSE)


class PcmAndClipTests(unittest.TestCase):
    def test_synthetic_pcm_is_deterministic(self) -> None:
        self.assertEqual(reference.synthetic_clean_pcm(),
                         reference.synthetic_clean_pcm())
        self.assertEqual(len(reference.synthetic_clean_pcm()),
                         reference.CONTROL_SOURCE_SAMPLES)

    def test_synthetic_pcm_is_finite_bounded_and_binary32(self) -> None:
        source = reference.validate_pcm(reference.synthetic_clean_pcm())
        self.assertTrue(all(math.isfinite(value) for value in source))
        self.assertLessEqual(max(abs(v) for v in source), 0.90)
        self.assertTrue(all(reference._f32(value) == value for value in source))

    def test_pcm_summary_is_deterministic(self) -> None:
        signal = reference.synthetic_clean_pcm()
        first = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        second = reference.pcm_summary(signal, reference.CONTROL_SAMPLE_RATE_HZ)
        self.assertEqual(first, second)
        self.assertEqual(first["duration_s"], "1")
        self.assertEqual(first["channels"], 1)
        self.assertEqual(first["samples"], 16000)

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

    def test_threshold_is_strictly_between_zero_and_one(self) -> None:
        self.assertEqual(reference.validate_threshold(0.35),
                         reference._f32(0.35))
        for bad in (0, 1, -0.1, 1.1, math.nan, math.inf, -math.inf,
                    True, "0.35"):
            with self.assertRaises(reference.Reject):
                reference.validate_threshold(bad)

    def test_clipping_is_exact_and_preserves_unmasked_samples(self) -> None:
        clean = reference.synthetic_clean_pcm()
        clipped, threshold, mask = reference.clipping_mask(clean, 0.35)
        self.assertEqual(threshold, reference._f32(0.35))
        self.assertEqual(len(clipped), len(clean))
        for index, flag in enumerate(mask):
            if flag:
                self.assertEqual(abs(clipped[index]), threshold)
                self.assertGreater(abs(clean[index]), threshold)
            else:
                self.assertEqual(clipped[index], clean[index])
                self.assertLessEqual(abs(clean[index]), threshold)

    def test_accounting_occupancy_and_intervals_are_exact(self) -> None:
        clean = reference.synthetic_clean_pcm()
        accounting = reference.clipping_accounting(clean, 0.35)
        self.assertTrue(accounting["exact_mask"])
        self.assertTrue(accounting["unmasked_preserved"])
        self.assertTrue(accounting["duration_conserved"])
        self.assertEqual(accounting["duration_ratio"], "1")
        self.assertEqual(accounting["duration_s"], "1")
        self.assertEqual(accounting["input_samples"], 16000)
        self.assertEqual(accounting["output_samples"], 16000)
        self.assertGreater(accounting["masked_samples"], 0)
        self.assertEqual(
            accounting["masked_samples"] + accounting["unmasked_samples"],
            accounting["input_samples"])
        self.assertEqual(sum(item["duration_samples"]
                             for item in accounting["mask_intervals"]),
                         accounting["masked_samples"])
        self.assertFalse(accounting["reconstruction_performed"])
        self.assertFalse(accounting["c_omp_executed"])
        self.assertFalse(accounting["candidate_output"])
        self.assertIsNone(accounting["quality_metrics"])
        self.assertEqual(accounting["qualification_effect"], "none")

    def test_quiet_control_has_no_clipped_sample(self) -> None:
        quiet = reference.synthetic_clean_pcm(reference.QUIET_SCALE)
        accounting = reference.clipping_accounting(quiet,
                                                   reference.QUIET_THRESHOLD)
        self.assertEqual(accounting["masked_samples"], 0)
        self.assertEqual(accounting["mask_intervals"], [])
        self.assertEqual(accounting["clipped_pcm_sha256"],
                         accounting["clean_pcm_sha256"])

    def test_threshold_055_has_lower_occupancy_than_035(self) -> None:
        clean = reference.synthetic_clean_pcm()
        low = reference.clipping_accounting(clean, 0.35)
        high = reference.clipping_accounting(clean, 0.55)
        self.assertGreater(low["masked_samples"], high["masked_samples"])

    def test_config_is_closed_and_strict(self) -> None:
        good = {"threshold": 0.35, "sample_rate_hz": 16000, "channels": 1}
        self.assertEqual(reference.validate_clip_config(good)["threshold"],
                         reference._f32(0.35))
        for bad in (
            [],
            {"threshold": 0.35, "sample_rate_hz": 16000},
            {**good, "extra": 1},
            {**good, "sample_rate_hz": 8000},
            {**good, "channels": 2},
            {**good, "threshold": 0},
        ):
            with self.assertRaises(reference.Reject):
                reference.validate_clip_config(bad)


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
        self.assertEqual(result["directories_checked"],
                         len(reference.CALLER_DIR_FIELDS))
        self.assertEqual(result["tool_version"], "0.0.0")
        self.assertFalse(result["toolbox_executed"])
        self.assertFalse(result["c_omp_executed"])
        self.assertFalse(result["sparse_recovery_performed"])

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["reference_experiment_path"]).unlink()
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
            Path(manifest["matlab_runtime_path"]).rmdir()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["config_path"] = "config.json"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_bad_revisions(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = _manifest_fixture(Path(raw))
            for field in ("source_revision", "ltfat_revision", "cvx_revision"):
                manifest = dict(base)
                manifest[field] = "short"
                with self.assertRaises(reference.Reject):
                    reference.validate_caller_manifest(manifest)
                manifest = dict(base)
                manifest[field] = "g" * 40
                with self.assertRaises(reference.Reject):
                    reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_bad_variant_and_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = _manifest_fixture(Path(raw))
            for field, value in (
                ("variant", "incremental_streaming"),
                ("matlab_version", ""),
                ("tool_version", "  "),
                ("sample_rate_hz", 48000),
                ("channels", 2),
                ("block_samples", 0),
                ("block_samples", 1001),
                ("block_samples", 65536 + 160),
            ):
                manifest = dict(base)
                manifest[field] = value
                with self.assertRaises(reference.Reject):
                    reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_extra_or_missing_field(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = _manifest_fixture(Path(raw))
            extra = dict(base, unexpected=1)
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(extra)
            missing = dict(base)
            missing.pop("config_sha256")
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(missing)


class AdverseControlTests(unittest.TestCase):
    def test_all_adverse_cases_are_invoked_and_rejected(self) -> None:
        results = reference.run_adverse_controls()
        self.assertEqual(len(results), len(reference.ADVERSE_CASE_IDS))
        self.assertEqual([item["case"] for item in results],
                         list(reference.ADVERSE_CASE_IDS))
        self.assertTrue(all(item["result"] == "rejected" for item in results))

    def test_control_is_labelled_synthetic_and_not_candidate(self) -> None:
        control = reference.build_control()
        self.assertEqual(control["plan_source"],
                         reference.CONTROL_PLAN_PROVENANCE)
        self.assertFalse(control["toolbox_executed"])
        self.assertFalse(control["c_omp_executed"])
        self.assertFalse(control["matlab_invoked"])
        self.assertFalse(control["ltfat_loaded"])
        self.assertFalse(control["cvx_loaded"])
        self.assertEqual(control["executor"], "absent")
        self.assertEqual(control["qualification_effect"], "none")
        self.assertFalse(control["geometry"]["performs_sparse_recovery"])
        self.assertFalse(control["geometry"]["task_geometry_asserted"])
        provenance = control["tool_provenance"]
        self.assertIsNone(provenance["tool_version"])
        self.assertIsNone(provenance["install_location"])
        self.assertIsNone(provenance["upstream_revision"])
        self.assertFalse(provenance["clean_checkout_or_package_verified"])
        self.assertFalse(provenance["typical_use_run"])

    def test_all_acceptance_outcomes_are_unmeasured(self) -> None:
        control = reference.build_control()
        self.assertEqual(len(control["acceptance_outcomes"]), 8)
        self.assertTrue(all(item["measured"] is False
                            and item["value"] is None
                            for item in control["acceptance_outcomes"]))

    def test_three_cases_are_accounting_only(self) -> None:
        control = reference.build_control()
        self.assertEqual([item["id"] for item in control["cases"]],
                         ["clipped_0_35", "clipped_0_55",
                          "quiet_no_clip_0_55"])
        self.assertTrue(all(item["candidate_output"] is False
                            for item in control["cases"]))
        self.assertTrue(all(item["accounting"]["candidate_output"] is False
                            for item in control["cases"]))


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = reference.build_contract()

    def test_top_level_decision(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["mode"], "external-adapter")
        self.assertEqual(report["profile"], "tool")
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
        self.assertIn("toolbox_source_checkout_absent", ids)
        self.assertIn("matlab_runtime_absent", ids)
        self.assertIn("ltfat_runtime_absent", ids)
        self.assertIn("cvx_optional_solver_absent", ids)
        self.assertIn("documented_tool_use_absent", ids)
        self.assertIn("vendor_terms_and_rights_unverified", ids)
        self.assertIn("isolated_adapter_and_parity_absent", ids)

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
                    "weights_vendored", "network_used", "adapter_json_added",
                    "matlab_dependency_added", "toolbox_vendored",
                    "processor_exposure"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_is_closed(self) -> None:
        scope = self.report["scope"]
        for key in ("real_audio", "real_corpus", "c_omp_executed",
                    "matlab_invoked", "ltfat_loaded", "cvx_loaded",
                    "sparse_recovery_performed", "declipping_output_produced",
                    "quality_metrics_computed", "runtime_invoked",
                    "vendor_runtime_invoked", "toolbox_executed",
                    "tool_use_run", "clean_install_verified",
                    "adapter_prototype_created", "vendor_output_scored",
                    "workload_measured", "network_used",
                    "device_timing", "listening",
                    "public_benchmark", "release_claim"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["task_local_only"], True)

    def test_no_fabricated_identity(self) -> None:
        upstream = self.report["upstream_identity"]
        self.assertIsNone(upstream["revision"])
        self.assertIsNone(upstream["reported_license"])
        self.assertFalse(upstream["revision_pin_available"])
        self.assertEqual(upstream["geometry_status"], "unestablished")
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertIsNone(requirements["upstream_revision"]["sha256"])
        self.assertIsNone(requirements["source_checkout"]["revision"])
        self.assertIsNone(requirements["documented_tool_use"]["sha256"])
        self.assertTrue(requirements["cvx_optional_solver"]["optional"])
        self.assertTrue(
            requirements["cvx_optional_solver"]["required_for_c_omp_comparison"])
        self.assertEqual(
            upstream["reported_optional_cvx_path"],
            reference.REPORTED_OPTIONAL_CVX_PATH)

    def test_runtime_is_absent(self) -> None:
        runtime = self.report["runtime_requirements"]
        self.assertFalse(runtime["complete_runtime_present"])
        self.assertFalse(runtime["matlab"]["present"])
        self.assertFalse(runtime["matlab"]["licensed"])
        self.assertFalse(runtime["matlab"]["install_present"])
        self.assertIsNone(runtime["matlab"]["version"])
        self.assertFalse(runtime["ltfat"]["present"])
        self.assertFalse(runtime["ltfat"]["manifest_present"])
        self.assertFalse(runtime["cvx"]["present"])
        self.assertFalse(runtime["cvx"]["manifest_present"])
        self.assertTrue(runtime["cvx"]["optional_selection"])

    def test_tool_profile_has_no_satisfied_item(self) -> None:
        profile = self.report["tool_profile"]
        self.assertEqual(profile["name"], "tool")
        self.assertEqual(profile["satisfied_for_qualification"], [])
        self.assertIsNone(profile["measured_workload_metrics"])
        self.assertEqual(len(profile["required_items"]),
                         len(reference.TOOL_REQUIREMENTS))
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
        self.assertFalse(audit["complete_runtime_present"])
        self.assertFalse(audit["reference_experiment_present"])
        self.assertFalse(audit["rights_record_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["parity_manifest_present"])
        self.assertFalse(audit["adapter_prototype_present"])
        self.assertFalse(audit["matlab_install_present"])
        self.assertFalse(audit["ltfat_manifest_present"])
        self.assertFalse(audit["cvx_manifest_present"])
        self.assertTrue(audit["all_absence_probes_absent"])

    def test_vendor_boundary_is_documented_not_bridged(self) -> None:
        boundary = self.report["external_adapter_boundary"]
        self.assertEqual(
            boundary["boundary"],
            "vendor_documented_external_tool_no_adapter_built")
        self.assertFalse(boundary["allowed_access_documented"])
        self.assertFalse(boundary["local_runtime_present"])
        self.assertFalse(boundary["vendor_output_scoring_present"])
        self.assertFalse(boundary["vendor_claim_present"])
        self.assertFalse(boundary["adapter_prototype_created"])
        self.assertTrue(boundary["fallback_requires_no_licensed_asset"])
        self.assertEqual(boundary["separation"]["compile_or_build_evidence"],
                         "absent")
        self.assertEqual(boundary["separation"]["measured_workload_support"],
                         "absent")
        self.assertEqual(boundary["separation"]["synthetic_runtime_evidence"],
                         "structural_accounting_only")
        self.assertFalse(boundary["matlab_dependency_added"])
        self.assertFalse(boundary["toolbox_vendored"])
        self.assertFalse(boundary["network_used"])

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_source_reported_context_has_no_c_omp_result(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"], "source_reported_not_measured_here")
        self.assertFalse(context["source_reported_numeric_result"])
        self.assertFalse(context["pilot_c_omp_row_present"])
        self.assertIsNone(context["reported_license"])
        self.assertIsNone(context["source_reported_revision"])
        self.assertEqual(context["reported_dependencies"],
                         ["MATLAB", "LTFAT", "CVX"])
        self.assertEqual(context["inventory_disposition"], "external-adapter")
        self.assertEqual(context["reported_optional_cvx_path"],
                         reference.REPORTED_OPTIONAL_CVX_PATH)
        self.assertEqual(len(context["sibling_context_not_attributed"]), 6)
        self.assertIn("no toolbox or C-OMP method row",
                      " ".join(context["sibling_context_not_attributed"]))

    def test_missing_artifacts_recorded(self) -> None:
        for path in (reference.MISSING_SOURCE_PATH,
                     reference.MATLAB_ENV_PATH,
                     reference.MATLAB_ENV_MANIFEST_PATH,
                     reference.MATLAB_INSTALL_PATH,
                     reference.LTFAT_PATH,
                     reference.LTFAT_MANIFEST_PATH,
                     reference.CVX_PATH,
                     reference.CVX_MANIFEST_PATH,
                     reference.REFERENCE_EXPERIMENT_PATH,
                     reference.RIGHTS_RECORD_PATH,
                     reference.COHORT_MANIFEST_PATH,
                     reference.PARITY_MANIFEST_PATH,
                     reference.OUTPUT_USE_GRANT_PATH,
                     reference.ADAPTER_PROTOTYPE_PATH):
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
        self.assertEqual(contract["external_adapter_boundary"],
                         report["external_adapter_boundary"])
        self.assertEqual(len(contract["tool_profile_requirements"]),
                         len(reference.TOOL_REQUIREMENTS))

    def test_sources_manifest_has_no_tasks_json(self) -> None:
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line and not line.startswith("#"):
                self.assertNotIn("TASKS.json", line)


if __name__ == "__main__":
    unittest.main()
