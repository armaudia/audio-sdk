# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the synthetic bridge-descriptor evidence harness."""

from __future__ import annotations

import unittest

import check_licensing
import fixture
import reference


class DescriptorAndFixtureTests(unittest.TestCase):
    def test_package_json_files_are_strict(self):
        for name in ("contract.json", "adapter.json", "provider.json", "report.json"):
            value = reference.load_package_json(name)
            self.assertIsInstance(value, dict)

    def test_at_least_33_fixture_cases(self):
        self.assertGreaterEqual(len(fixture.fixture_ids()), 33)

    def test_fixture_ids_are_unique_and_ordered(self):
        ids = fixture.fixture_ids()
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, tuple(fixture._all_cases().keys()))

    def test_fixture_build_is_independent(self):
        first = fixture.build_fixture("valid_with_optional")
        first["request"]["request_id"] = "mutated"
        second = fixture.build_fixture("valid_with_optional")
        self.assertEqual(second["request"]["request_id"], "req-0001")

    def test_pseudo_bytes_are_deterministic(self):
        self.assertEqual(fixture.pseudo_bytes(11, 257), fixture.pseudo_bytes(11, 257))
        self.assertNotEqual(fixture.pseudo_bytes(11, 64), fixture.pseudo_bytes(12, 64))
        self.assertEqual(len(fixture.pseudo_bytes(7, 33)), 33)

    def test_synthetic_asset_identity_is_stable(self):
        first = fixture.synthetic_asset()
        second = fixture.synthetic_asset()
        self.assertEqual(first, second)
        self.assertEqual(first["byte_count"], 64)
        self.assertEqual(len(first["sha256"]), 64)

    def test_strict_json_rejects_duplicate_key(self):
        with self.assertRaises(reference.Reject) as caught:
            reference.strict_loads('{"a": 1, "a": 2}')
        self.assertEqual(caught.exception.reason, "strict_json_duplicate_key")

    def test_strict_json_rejects_nan_constant(self):
        with self.assertRaises(reference.Reject) as caught:
            reference.strict_loads('{"a": NaN}')
        self.assertEqual(caught.exception.reason, "strict_json_nonfinite")

    def test_strict_json_rejects_non_object_root(self):
        with self.assertRaises(reference.Reject) as caught:
            reference.strict_loads("[1,2,3]")
        self.assertEqual(caught.exception.reason, "strict_json_non_object")

    def test_strict_json_rejects_trailing_text(self):
        with self.assertRaises(reference.Reject) as caught:
            reference.strict_loads('{"a": 1} trailing')
        self.assertEqual(caught.exception.reason, "strict_json_invalid")

    def test_canonical_bytes_are_key_order_independent(self):
        left = reference.canonical_bytes({"a": 1, "b": 2})
        right = reference.canonical_bytes({"b": 2, "a": 1})
        self.assertEqual(left, right)
        self.assertEqual(left, b'{"a":1,"b":2}')

    def test_canonical_bytes_reject_nonfinite(self):
        with self.assertRaises(reference.Reject) as caught:
            reference.canonical_bytes({"a": float("inf")})
        self.assertEqual(caught.exception.reason, "nonfinite_value")

    def test_fixture_digest_is_stable(self):
        item = fixture.build_fixture("valid_with_optional")
        self.assertEqual(reference.fixture_digest(item),
                         reference.fixture_digest(fixture.build_fixture("valid_with_optional")))

    def test_base_descriptor_validates(self):
        self.assertEqual(len(reference.validate_descriptor(fixture.base_descriptor())), 64)

    def test_base_request_without_selection_is_omitted(self):
        status = reference.validate_request(fixture.base_request(with_selection=False),
                                            fixture.base_descriptor())
        self.assertEqual(status, "ok_omitted")


class ValidationTests(unittest.TestCase):
    def decision(self, case_id):
        return reference.evaluate_case(fixture.build_fixture(case_id))

    def assert_reason(self, case_id, reason):
        decision = self.decision(case_id)
        self.assertEqual(decision["actual_status"], "rejected", decision)
        self.assertEqual(decision["actual_reason"], reason, decision)
        self.assertFalse(decision["qualified"])

    def test_valid_with_optional(self):
        decision = self.decision("valid_with_optional")
        self.assertEqual((decision["actual_status"], decision["actual_reason"]),
                         ("ok", "valid_synthetic_fixture"))

    def test_valid_without_optional(self):
        decision = self.decision("valid_without_optional")
        self.assertEqual((decision["actual_status"], decision["actual_reason"]),
                         ("ok_omitted", "optional_selection_omitted"))

    def test_unsupported_protocol(self):
        self.assert_reason("unsupported_protocol", "unsupported_protocol")

    def test_duplicate_json_key(self):
        self.assert_reason("duplicate_json_key", "strict_json_duplicate_key")

    def test_nonfinite_json_constant(self):
        self.assert_reason("nonfinite_json_constant", "strict_json_nonfinite")

    def test_nonfinite_frame_value(self):
        self.assert_reason("nonfinite_frame_value", "nonfinite_value")

    def test_asset_sha_mismatch(self):
        self.assert_reason("asset_sha_mismatch", "asset_hash_mismatch")

    def test_asset_byte_count_mismatch(self):
        self.assert_reason("asset_byte_count_mismatch", "asset_byte_count_mismatch")

    def test_duplicate_asset_id(self):
        self.assert_reason("duplicate_asset_id", "duplicate_asset_id")

    def test_asset_path_escape(self):
        self.assert_reason("asset_path_escape", "asset_location_not_granted")

    def test_asset_missing_rights_ref(self):
        self.assert_reason("asset_missing_rights_ref", "asset_rights_ref_missing")

    def test_input_manifest_in_attempt_dir(self):
        self.assert_reason("input_manifest_in_attempt_dir", "input_manifest_inside_attempt_dir")

    def test_writable_root_escape(self):
        self.assert_reason("writable_root_escape", "writable_root_escape")

    def test_read_grant_missing(self):
        self.assert_reason("read_grant_missing", "read_grant_missing")

    def test_network_allowed(self):
        self.assert_reason("network_allowed", "network_not_denied")

    def test_downloads_allowed(self):
        self.assert_reason("downloads_allowed", "downloads_not_denied")

    def test_nested_sandbox_allowed(self):
        self.assert_reason("nested_sandbox_allowed", "nested_policy_not_fail_closed")

    def test_production_callback_declared(self):
        self.assert_reason("production_callback_declared", "production_callback_not_none")

    def test_wrong_frame_samples(self):
        self.assert_reason("wrong_frame_samples", "frame_samples_mismatch")

    def test_wrong_sample_rate(self):
        self.assert_reason("wrong_sample_rate", "sample_rate_mismatch")

    def test_empty_request_id(self):
        self.assert_reason("empty_request_id", "request_id_invalid")

    def test_inline_callback_mode(self):
        self.assert_reason("inline_callback_mode", "execution_mode_unsupported")

    def test_stale_descriptor_digest(self):
        self.assert_reason("stale_descriptor_digest", "descriptor_digest_mismatch")

    def test_download_requested(self):
        self.assert_reason("download_requested", "download_requested")

    def test_null_optional_selection(self):
        self.assert_reason("null_optional_selection", "optional_selection_null")

    def test_unknown_optional_selection(self):
        self.assert_reason("unknown_optional_selection", "optional_selection_unknown")

    def test_missing_result_is_incomplete(self):
        decision = self.decision("missing_result")
        self.assertEqual((decision["actual_status"], decision["actual_reason"]),
                         ("incomplete", "result_missing"))
        self.assertFalse(decision["qualified"])

    def test_result_missing_status(self):
        self.assert_reason("result_missing_status", "result_field_missing")

    def test_result_manifest_digest_invalid(self):
        self.assert_reason("result_manifest_digest_invalid", "result_digest_mismatch")

    def test_result_asset_unknown(self):
        self.assert_reason("result_asset_unknown", "result_asset_unknown")

    def test_nonfinite_result_metric(self):
        self.assert_reason("nonfinite_result_metric", "nonfinite_value")

    def test_malformed_result_manifest(self):
        self.assert_reason("malformed_result_manifest", "result_field_missing")

    def test_blocked_nested_sandbox(self):
        decision = self.decision("blocked_nested_sandbox")
        self.assertEqual((decision["actual_status"], decision["actual_reason"]),
                         ("blocked", "nested_sandbox_denied"))
        self.assertFalse(decision["qualified"])


class ReportAndBoundaryTests(unittest.TestCase):
    def test_all_fixture_outcomes_match_expectations(self):
        report = reference.build_report()
        for decision in report["cases"]:
            self.assertEqual(decision["actual_status"], decision["expected_status"], decision["case_id"])
            self.assertEqual(decision["actual_reason"], decision["expected_reason"], decision["case_id"])

    def test_no_case_ever_qualifies(self):
        report = reference.build_report()
        self.assertTrue(all(not decision["qualified"] for decision in report["cases"]))
        self.assertEqual(report["summary"]["qualified_candidates"], 0)

    def test_report_schema_and_proposal_status(self):
        report = reference.build_report()
        self.assertEqual(report["schema_id"], reference.REPORT_SCHEMA)
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertEqual(report["boundary"]["release_gate"], "DEFER")

    def test_report_has_no_draft_schema_keys(self):
        report = reference.build_report()
        for key in ("framing", "gates", "qualification_status"):
            self.assertNotIn(key, report)
            self.assertNotIn(key, reference.load_package_json(reference.CONTRACT))

    def test_report_all_checks_green(self):
        report = reference.build_report()
        self.assertTrue(report["summary"]["all_checks_green"], report["checks"])

    def test_report_digest_matches_content(self):
        report = reference.build_report()
        supplied = report.pop("canonical_report_digest")
        self.assertEqual(supplied, reference.canonical_digest(report))

    def test_report_bytes_are_deterministic(self):
        self.assertEqual(reference.report_bytes(), reference.report_bytes(reference.build_report()))

    def test_committed_report_matches_model(self):
        self.assertEqual((reference.ROOT / reference.REPORT).read_bytes(), reference.report_bytes())

    def test_sidecar_matches_report_bytes(self):
        data = (reference.ROOT / reference.REPORT).read_bytes()
        self.assertEqual(reference.read_sidecar(), reference.sha256_bytes(data))
        self.assertEqual((reference.ROOT / reference.SIDECAR).read_bytes(),
                         reference.sidecar_bytes(data))

    def test_source_pins_recorded(self):
        report = reference.build_report()
        pins = report["source_pins"]
        self.assertEqual(pins["adapters_readme"]["sha256"],
                         "24d8915f0ff59ee026ef86b396f64f1b3e68d3a5678f98a353273b712f09e1ee")
        self.assertIn("board_snapshot", pins)
        self.assertIn("verification_profile", pins)
        self.assertIn("public_provider_header", pins)
        self.assertIn("public_session_header", pins)

    def test_sources_check_is_green(self):
        result = reference.check_sources()
        self.assertEqual(result["status"], "ok", result["problems"])
        self.assertEqual(result["adapters_readme_sha256"],
                         "24d8915f0ff59ee026ef86b396f64f1b3e68d3a5678f98a353273b712f09e1ee")

    def test_spdx_and_reuse_check_is_green(self):
        result = check_licensing.check()
        self.assertEqual(result["status"], "ok", result["problems"])

    def test_provider_is_unregistered_and_unlinked(self):
        provider = fixture.load_json("provider.json")
        self.assertEqual(provider["registration"], "unregistered")
        self.assertFalse(provider["linked"])
        self.assertFalse(provider["opt_in"])
        self.assertEqual(provider["production_callback"], "none")
        self.assertFalse(provider["fixture_contract"]["benchmark_submission_claimed"])

    def test_adapter_descriptor_is_evidence_only(self):
        descriptor = fixture.base_descriptor()
        self.assertEqual(descriptor["kind"], "evidence_only_bridge_descriptor")
        self.assertFalse(descriptor["entrypoint_invoked"])
        self.assertEqual(descriptor["production_callback"], "none")

    def test_measured_workload_support_is_unclaimed(self):
        report = reference.build_report()
        self.assertEqual(report["evidence_separation"]["measured_workload_support"]["status"],
                         "unclaimed")
        self.assertEqual(report["evidence_separation"]["synthetic_runtime"]["external_runner_invoked"],
                         False)

    def test_compile_build_evidence_is_separate(self):
        report = reference.build_report()
        build = report["evidence_separation"]["compile_build"]
        self.assertEqual((build["ctest_passed"], build["ctest_total"]), (11, 11))
        self.assertEqual(build["consumer_opt_in_boundary"],
                         "not_included_no_c_boundary_added")


if __name__ == "__main__":
    unittest.main()
