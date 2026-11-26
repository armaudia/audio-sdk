# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local Krisp Accent Conversion evidence package."""

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
    manifest = {
        "vendor_sdk_version": "9.9.9-test",
        "vendor_release_id": "test-release-1",
        "input_sample_rate_hz": reference.INPUT_SAMPLE_RATE_HZ,
        "input_channels": reference.CHANNELS,
        "frame_samples": reference.SDK_FRAME_SAMPLES,
        "sample_format": reference.SAMPLE_FORMAT,
        "variant": reference.VARIANT,
        "runtime_platform": reference.ALLOWED_RUNTIME_PLATFORMS[0],
    }
    for index, (path_field, sha_field) in enumerate(
            reference.CALLER_FILE_PAIRS):
        path = root / f"asset-{index}.bin"
        data = f"asset-{index}-payload".encode("utf-8")
        path.write_bytes(data)
        manifest[path_field] = str(path)
        manifest[sha_field] = _sha(data)
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


class VendorAuditTests(unittest.TestCase):
    def test_vendor_sdk_is_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["vendor_sdk_root_present"])
        self.assertEqual(audit["vendor_sdk_file_count"], 0)
        self.assertEqual(audit["vendor_sdk_files_found"], [])

    def test_model_bundle_is_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["model_bundle_dir_present"])
        self.assertEqual(audit["model_bundle_file_count"], 0)
        self.assertEqual(audit["model_bundle_files_found"], [])

    def test_vendor_identity_is_not_invented(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["release_id_known"])
        self.assertIsNone(reference.VENDOR_RELEASE_ID)

    def test_rights_and_runtime_are_absent(self) -> None:
        audit = reference.audit_assets()
        self.assertFalse(audit["license_record_present"])
        self.assertFalse(audit["entitlement_record_present"])
        self.assertFalse(audit["consent_record_present"])
        self.assertFalse(audit["direction_map_present"])
        self.assertFalse(audit["cohort_manifest_present"])
        self.assertFalse(audit["target_reference_present"])
        self.assertFalse(audit["runtime_env_present"])
        self.assertFalse(audit["runtime_lock_present"])

    def test_research_clips_are_not_evaluation_evidence(self) -> None:
        audit = reference.audit_assets()
        self.assertEqual(audit["research_demo_audio_clip_count"], 3)
        self.assertNotIn("evaluation_clip_count", audit)

    def test_requested_geometry(self) -> None:
        config = reference.audit_assets()["requested_config"]
        self.assertEqual(config["input_sample_rate_hz"], 16000)
        self.assertEqual(config["input_channels"], 1)
        self.assertEqual(config["frame_samples"], 160)
        self.assertEqual(config["sample_format"], "f32")
        self.assertEqual(config["variant"], reference.VARIANT)


class TaskIdentityTests(unittest.TestCase):
    def test_identity_matches_live_board(self) -> None:
        identity = reference.task_row_identity()
        self.assertEqual(identity["stable_fields"]["id"], reference.TASK)
        self.assertEqual(
            identity["stable_fields"]["component"], reference.COMPONENT)
        self.assertEqual(identity["stable_fields"]["mode"], "external-adapter")
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
        self.assertIsNone(reference.VENDOR_RELEASE_ID)


class FrameAndDirectionTests(unittest.TestCase):
    def test_synthetic_frame_is_bounded(self) -> None:
        frame = reference.synthetic_frame(0)
        self.assertEqual(len(frame), 160)
        self.assertTrue(all(math.isfinite(value) for value in frame))
        self.assertTrue(all(-1.0 <= value <= 1.0 for value in frame))

    def test_synthetic_frame_is_deterministic(self) -> None:
        self.assertEqual(reference.synthetic_frame(3),
                         reference.synthetic_frame(3))
        self.assertNotEqual(reference.synthetic_frame(0),
                            reference.synthetic_frame(1))

    def test_passthrough_never_claims_conversion(self) -> None:
        record = reference.passthrough_frame(reference.synthetic_frame(0))
        self.assertEqual(record["consumed_count"], 160)
        self.assertEqual(record["produced_count"], 160)
        self.assertEqual(record["valid_count"], 160)
        self.assertFalse(record["transform_applied"])
        self.assertFalse(record["converted_speech"])

    def test_validate_frame_rejects_invalid(self) -> None:
        good = reference.synthetic_frame(0)
        cases = [
            lambda: reference.validate_frame(good[:159]),
            lambda: reference.validate_frame(good + [0.0]),
            lambda: reference.validate_frame(b"0" * 160),
            lambda: reference.validate_frame(None),
            lambda: reference.validate_frame([math.nan] + good[1:]),
            lambda: reference.validate_frame([math.inf] + good[1:]),
            lambda: reference.validate_frame([-math.inf] + good[1:]),
            lambda: reference.validate_frame([1.5] + good[1:]),
            lambda: reference.validate_frame([-1.5] + good[1:]),
            lambda: reference.validate_frame([True] + good[1:]),
            lambda: reference.validate_frame(["0.0"] + good[1:]),
        ]
        for action in cases:
            with self.assertRaises(reference.Reject):
                action()

    def test_direction_set_is_closed_and_placeholder(self) -> None:
        for pair in reference.SYNTHETIC_DIRECTIONS:
            self.assertEqual(reference.validate_direction(list(pair)), pair)
            self.assertTrue(all(part.startswith("synthetic_accent_")
                                for part in pair))

    def test_validate_direction_rejects_invalid(self) -> None:
        good = reference.SYNTHETIC_DIRECTIONS[0]
        cases = [
            lambda: reference.validate_direction("a->b"),
            lambda: reference.validate_direction([good[0]]),
            lambda: reference.validate_direction([good[0], good[1], "x"]),
            lambda: reference.validate_direction([good[0], good[0]]),
            lambda: reference.validate_direction([good[0], "vendor_accent_z"]),
            lambda: reference.validate_direction([good[0], "accent\u00e9"]),
            lambda: reference.validate_direction([good[0], 7]),
        ]
        for action in cases:
            with self.assertRaises(reference.Reject):
                action()


class IntervalTests(unittest.TestCase):
    def test_contract_example_320_with_delay_160(self) -> None:
        plan = reference.plan_intervals(320, 160)
        coverage = reference.interval_coverage(plan, 320)
        self.assertTrue(coverage["exact_union_match"])
        self.assertEqual(plan[0]["valid_count"], 0)
        self.assertEqual(plan[0]["valid_offset"], 160)
        self.assertEqual(plan[-1]["kind"], "drain")
        self.assertEqual(plan[-1]["valid_count"], 160)

    def test_partial_final_frame(self) -> None:
        plan = reference.plan_intervals(165, 160)
        coverage = reference.interval_coverage(plan, 165)
        self.assertTrue(coverage["exact_union_match"])
        self.assertEqual(plan[-1]["valid_count"], 5)

    def test_delay_not_divisible_by_frame(self) -> None:
        for accepted in (1, 159, 161, 485, 1000):
            for delay in (0, 17, 160, 1234):
                plan = reference.plan_intervals(accepted, delay)
                coverage = reference.interval_coverage(plan, accepted)
                self.assertTrue(coverage["exact_union_match"],
                                (accepted, delay))

    def test_empty_stream_drains_immediately(self) -> None:
        self.assertEqual(reference.plan_intervals(0, 0), [])

    def test_validate_interval_rejects_invalid(self) -> None:
        cases = [
            lambda: reference.plan_intervals(-1, 0),
            lambda: reference.plan_intervals(True, 0),
            lambda: reference.plan_intervals(160, -1),
            lambda: reference.plan_intervals(
                160, reference.MAX_BUFFERING_DELAY_SAMPLES + 1),
            lambda: reference.plan_intervals(160, 160.0),
            lambda: reference.plan_intervals(160, math.nan),
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
        self.assertFalse(result["vendor_release_approved"])
        self.assertFalse(result["entitlement_approved"])
        self.assertFalse(result["revision_pinned"])
        self.assertFalse(result["model_executed"])
        self.assertFalse(result["vendor_sdk_linked"])
        self.assertEqual(result["frame_samples"], 160)
        self.assertEqual(result["files_checked"],
                         len(reference.CALLER_FILE_PAIRS))
        self.assertEqual(result["qualification_effect"], "none")

    def test_manifest_rejects_missing_asset(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["model_bundle_path"]).unlink()
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            Path(manifest["runtime_library_path"]).write_bytes(b"tampered")
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["direction_map_path"] = "directions.json"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_unpinned_release_shape(self) -> None:
        for value in ("", "x", "bad release", "release/1"):
            with tempfile.TemporaryDirectory() as raw:
                manifest = _manifest_fixture(Path(raw))
                manifest["vendor_release_id"] = value
                with self.assertRaises(reference.Reject):
                    reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_wrong_geometry(self) -> None:
        for field, value in (("input_sample_rate_hz", 22050),
                             ("input_channels", 2),
                             ("frame_samples", 80),
                             ("sample_format", "s16"),
                             ("variant", "vendor_native_stream"),
                             ("runtime_platform", "plan9-mips")):
            with tempfile.TemporaryDirectory() as raw:
                manifest = _manifest_fixture(Path(raw))
                manifest[field] = value
                with self.assertRaises(reference.Reject):
                    reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_duplicate_paths(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["target_reference_path"] = manifest["cohort_manifest_path"]
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)

    def test_manifest_rejects_unknown_and_missing_fields(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest["extra"] = "x"
            with self.assertRaises(reference.Reject):
                reference.validate_caller_manifest(manifest)
        with tempfile.TemporaryDirectory() as raw:
            manifest = _manifest_fixture(Path(raw))
            manifest.pop("consent_record_sha256")
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
        self.assertTrue(control["synthetic_direction_set_is_placeholder"])
        self.assertFalse(control["vendor_direction_names_available"])

    def test_control_is_not_conversion(self) -> None:
        control = reference.build_control()
        self.assertFalse(control["passthrough"]["transform_applied"])
        self.assertFalse(control["passthrough"]["converted_speech"])
        frames = [reference.synthetic_frame(0), reference.synthetic_frame(1)]
        expected = reference.sha256(reference.canonical_bytes(
            [[f"{value:.6f}" for value in frame] for frame in frames]))
        self.assertEqual(control["passthrough"]["input_sha256"], expected)
        self.assertEqual(len(control["passthrough"]["records"]), 2)
        for frame, record in zip(frames, control["passthrough"]["records"]):
            self.assertEqual(
                record["output_sha256"],
                reference.sha256(reference.canonical_bytes(
                    [f"{value:.6f}" for value in frame])))

    def test_control_coverage_is_exact(self) -> None:
        control = reference.build_control()
        self.assertTrue(control["coverage"]["exact_union_match"])
        self.assertFalse(control["coverage"]["duplicates"])
        self.assertEqual(control["coverage"]["expected_samples"],
                         reference.ACCEPTED_TOTAL_SAMPLES)

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
        self.assertEqual(report["mode"], "external-adapter")
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
        self.assertIn("entitlement_and_terms_absent",
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
                    "asset_bundled", "model_weights_vendored",
                    "vendor_sdk_vendored", "vendor_sdk_linked",
                    "entitlement_token_handled", "adapter_code_added",
                    "sdk_callback_invoked", "network_used"):
            self.assertIs(boundary[key], False, key)
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_scope_is_closed(self) -> None:
        scope = self.report["scope"]
        for key in ("real_audio", "real_corpus", "real_krisp_model",
                    "model_executed", "weights_loaded", "weights_downloaded",
                    "runtime_invoked", "vendor_runtime_invoked",
                    "vendor_sdk_linked", "entitlement_used", "network_used",
                    "device_timing", "listening", "public_benchmark",
                    "release_claim"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["task_local_only"], True)

    def test_requirements_have_no_fabricated_hash(self) -> None:
        requirements = {item["id"]: item
                        for item in self.report["asset_requirements"]}
        self.assertIsNone(requirements["vendor_sdk_package"]["sha256"])
        self.assertIsNone(requirements["model_bundle"]["sha256"])
        self.assertIsNone(requirements["exact_runtime"]["runtime_lock_sha256"])
        self.assertIsNone(requirements["entitlement_record"]["sha256"])

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
        self.assertFalse(audit["vendor_sdk_present"])
        self.assertFalse(audit["model_bundle_present"])
        self.assertFalse(audit["license_present"])
        self.assertFalse(audit["entitlement_present"])
        self.assertFalse(audit["direction_map_present"])

    def test_no_whole_file_tasks_hash(self) -> None:
        encoded = reference.canonical_bytes(self.report).decode("utf-8")
        self.assertNotIn('TASKS.json": "', encoded)
        self.assertFalse(self.report["task_row_identity"]["whole_file_hashed"])

    def test_source_reported_context_labelled(self) -> None:
        context = self.report["source_reported_context"]
        self.assertEqual(context["label"], "source_reported_not_measured_here")
        self.assertIn("not locally downloadable", context["reported_status"])
        self.assertEqual(context["reported_latency_approx_ms"], 180)

    def test_missing_artifacts_recorded(self) -> None:
        for path in (reference.VENDOR_SDK_ROOT_PATH + "/",
                     reference.MODEL_BUNDLE_PATH + "/",
                     reference.RUNTIME_LOCK_PATH,
                     reference.LICENSE_RECORD_PATH,
                     reference.ENTITLEMENT_RECORD_PATH,
                     reference.DIRECTION_MAP_PATH,
                     reference.COHORT_MANIFEST_PATH,
                     reference.TARGET_REFERENCE_PATH):
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
