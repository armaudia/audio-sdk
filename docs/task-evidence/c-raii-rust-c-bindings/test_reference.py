# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the task-local synthetic C/Rust binding evidence model."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import check_licensing
import fixture
import reference
import run
import scorer

ROOT = Path(__file__).resolve().parent


class FixtureTests(unittest.TestCase):
    def test_coefficient_count(self):
        self.assertEqual(len(fixture.coefficients()), 160)

    def test_coefficient_range(self):
        for value in fixture.coefficients():
            self.assertGreaterEqual(value, -8192)
            self.assertLessEqual(value, 8191)

    def test_coefficients_are_deterministic(self):
        self.assertEqual(fixture.coefficients(), fixture.coefficients())

    def test_sample_count_and_finite(self):
        samples = fixture.samples()
        self.assertEqual(len(samples), 160)
        self.assertTrue(all(abs(value) <= 1.0 for value in samples))

    def test_samples_match_coefficients(self):
        for coefficient, sample in zip(fixture.coefficients(), fixture.samples()):
            self.assertEqual(sample, coefficient / 8192.0)

    def test_fnv_known_vector(self):
        self.assertEqual(f"{fixture.fnv1a64(b''):016x}", "cbf29ce484222325")

    def test_input_digest_is_16_hex(self):
        digest = fixture.input_digest()
        self.assertEqual(len(digest), 16)
        self.assertEqual(digest, digest.lower())
        int(digest, 16)

    def test_case_count(self):
        self.assertEqual(len(fixture.cases()), 11)

    def test_case_ids_unique(self):
        ids = [row["case_id"] for row in fixture.cases()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_case_kinds_covered(self):
        kinds = {row["kind"] for row in fixture.cases()}
        self.assertTrue({"valid", "malformed", "missing_optional", "invalid", "nonfinite"} <= kinds)

    def test_all_cases_share_input_digest(self):
        digests = {row["input_digest"] for row in fixture.cases()}
        self.assertEqual(digests, {fixture.input_digest()})

    def test_fixture_pins(self):
        pins = fixture.fixture_pins()
        self.assertEqual(pins["frame_samples"], 160)
        self.assertEqual(pins["sample_rate_hz"], 16000)
        self.assertEqual(pins["channels"], 1)
        self.assertEqual(pins["case_count"], 11)


class StrictJsonTests(unittest.TestCase):
    def _write(self, text):
        handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        return Path(handle.name)

    def test_valid_object(self):
        path = self._write('{"a": 1}')
        self.assertEqual(reference.read_strict_json(path), {"a": 1})

    def test_duplicate_key_rejected(self):
        path = self._write('{"a": 1, "a": 2}')
        with self.assertRaises(ValueError):
            reference.read_strict_json(path)

    def test_nan_rejected(self):
        path = self._write('{"a": NaN}')
        with self.assertRaises(ValueError):
            reference.read_strict_json(path)

    def test_array_root_rejected(self):
        path = self._write('[1, 2]')
        with self.assertRaises(ValueError):
            reference.read_strict_json(path)

    def test_canonical_is_sorted_and_compact(self):
        text, digest = reference.canonical_json({"b": 2, "a": 1})
        self.assertEqual(text, '{"a":1,"b":2}')
        self.assertEqual(digest, hashlib.sha256(text.encode("utf-8")).hexdigest())

    def test_repository_json_files_are_strict(self):
        for name in ("contract.json", "adapter.json", "provider.json",
                     "crosscheck.json", "c_boundary/harness_output.json", "report.json"):
            self.assertIsInstance(reference.read_strict_json(ROOT / name), dict, name)


class ModelTests(unittest.TestCase):
    def test_model_case_count(self):
        self.assertEqual(len(reference.model_cases()), 11)

    def test_model_events_start_and_end(self):
        for row in reference.model_cases():
            self.assertEqual(row["events"][0], "registry_create:OK")
            self.assertEqual(row["events"][-1], "registry_close_double:OK")

    def test_no_process_event_on_create_failure(self):
        for row in reference.model_cases():
            if row["expected_create_status"] != "OK":
                self.assertIsNone(row["expected_process_status"])
                self.assertFalse(any(event.startswith("process:") for event in row["events"]))

    def test_model_digest_is_stable(self):
        self.assertEqual(reference.model_digest(), reference.model_digest())
        self.assertEqual(len(reference.model_digest()), 16)

    def test_status_codes(self):
        self.assertEqual(reference.STATUS_CODES["OK"], 0)
        self.assertEqual(reference.STATUS_CODES["INVALID_ARGUMENT"], 1)
        self.assertEqual(reference.STATUS_CODES["UNSUPPORTED"], 2)

    def test_pins_match_files(self):
        for pin in reference.PINS:
            path = reference.pin_paths()[pin["id"]]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin["sha256"], pin["id"])

    def test_generated_header_contract_values(self):
        text = reference.generated_header()
        self.assertIn("AS_RAII_EVIDENCE_CASE_COUNT 11u", text)
        self.assertIn("AS_RAII_EVIDENCE_FRAME_SAMPLES 160u", text)
        self.assertIn(fixture.input_digest().upper(), text)
        self.assertIn("SPDX" "-License-Identifier: Apache-2.0", text)

    def test_generated_header_file_matches(self):
        self.assertEqual((ROOT / "c_boundary/raii_model.h").read_text(encoding="utf-8"),
                         reference.generated_header())


class ScorerTests(unittest.TestCase):
    def test_success_invariants(self):
        result = {"process_status": "OK", "result": {
            "status": 0, "consumed_count": 160, "produced_count": 160,
            "valid_offset": 0, "valid_count": 160, "flags": 0}}
        self.assertTrue(all(scorer.result_invariants(result).values()))

    def test_failure_result_must_be_absent(self):
        self.assertEqual(scorer.result_invariants(
            {"process_status": "INVALID_ARGUMENT", "result": None}),
            {"result_absent_on_failure": True})

    def test_failure_with_result_rejected(self):
        self.assertFalse(scorer.result_invariants(
            {"process_status": "INVALID_ARGUMENT", "result": {"status": 0}})["result_absent_on_failure"])

    def test_success_missing_result_rejected(self):
        self.assertFalse(all(scorer.result_invariants({"process_status": "OK"}).values()))

    def test_out_of_range_produced_rejected(self):
        result = {"process_status": "OK", "result": {
            "status": 0, "consumed_count": 160, "produced_count": 161,
            "valid_offset": 0, "valid_count": 0, "flags": 0}}
        self.assertFalse(scorer.result_invariants(result)["produced_within_frame"])

    def test_invalid_valid_window_rejected(self):
        result = {"process_status": "OK", "result": {
            "status": 0, "consumed_count": 160, "produced_count": 160,
            "valid_offset": 159, "valid_count": 2, "flags": 0}}
        self.assertFalse(scorer.result_invariants(result)["valid_window_within_output"])

    def test_score_case_pass(self):
        expected = reference.model_cases()[0]
        observed = json.loads((ROOT / "c_boundary/harness_output.json").read_text())["cases"][0]
        self.assertTrue(scorer.score_case(expected, observed)["passed"])

    def test_score_case_detects_mutation(self):
        expected = reference.model_cases()[0]
        observed = dict(expected)
        observed["input_digest"] = "0" * 16
        self.assertFalse(scorer.score_case(expected, observed)["passed"])

    def test_score_all_count_mismatch(self):
        outcome = scorer.score_all(reference.model_cases(), [])
        self.assertFalse(outcome["passed"])
        self.assertEqual(outcome["reason"], "case_count_mismatch")

    def test_crosscheck_all_pass(self):
        observed = json.loads((ROOT / "c_boundary/harness_output.json").read_text())["cases"]
        summary = scorer.summary(scorer.score_all(reference.model_cases(), observed))
        self.assertTrue(summary["passed"])
        self.assertEqual(summary["passed_count"], 11)
        self.assertEqual(summary["failed_cases"], [])


class RequestTests(unittest.TestCase):
    def test_make_request_shapes(self):
        self.assertIn("case_id", run.make_request("run", "valid_full_frame"))
        self.assertNotIn("case_id", run.make_request("inspect"))

    def test_inspect_result(self):
        result = run.inspect(run.make_request("inspect"))
        self.assertEqual(result["operation"], "inspect")
        self.assertFalse(result["expose_as_processor"])

    def test_run_result(self):
        result = run.run_case(run.make_request("run", "valid_full_frame"))
        self.assertEqual(result["case"]["case_id"], "valid_full_frame")
        self.assertEqual(result["status"], "contract_model_only")

    def test_validate_result(self):
        result = run.validate(run.make_request("validate"))
        self.assertTrue(result["passed"])
        self.assertEqual(result["case_count"], 11)

    def test_request_must_be_object(self):
        with self.assertRaises(run.RequestError):
            run.inspect([])

    def test_request_extra_field_rejected(self):
        request = run.make_request("inspect")
        request["unexpected"] = 1
        with self.assertRaises(run.RequestError):
            run.inspect(request)

    def test_request_missing_case_id_rejected(self):
        request = run.make_request("run", "valid_full_frame")
        del request["case_id"]
        with self.assertRaises(run.RequestError):
            run.run_case(request)

    def test_unknown_case_rejected(self):
        with self.assertRaises(run.RequestError):
            run.run_case(run.make_request("run", "does_not_exist"))

    def test_bad_ref_rejected(self):
        request = run.make_request("inspect")
        request["candidate_ref"]["revision"] = 0
        with self.assertRaises(run.RequestError):
            run.inspect(request)

    def test_bad_configuration_rejected(self):
        request = run.make_request("inspect")
        request["configuration"] = {"profile": "production"}
        with self.assertRaises(run.RequestError):
            run.inspect(request)

    def test_dispatch_unknown_operation(self):
        with self.assertRaises(run.RequestError):
            run.dispatch({"operation": "promote"})

    def test_bundle_validation(self):
        checks = run.bundle_validation()["checks"]
        self.assertTrue(all(checks.values()))


class PackageTests(unittest.TestCase):
    def test_report_decision_is_deferred(self):
        report = reference.read_strict_json(ROOT / "report.json")
        decision = report["decision"]
        self.assertFalse(decision["expose_as_processor"])
        self.assertFalse(decision["registered"])
        self.assertFalse(decision["default_enabled"])
        self.assertEqual(decision["production_exposure"], "DEFER")

    def test_report_status(self):
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertTrue(report["decision"]["incomplete"])

    def test_installed_v0_unchanged(self):
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertEqual(report["installed_v0"]["frame_samples"], 160)
        self.assertFalse(report["installed_v0"]["changed"])

    def test_no_public_surface_change(self):
        boundary = reference.read_strict_json(ROOT / "contract.json")["public_boundary"]
        boolean_fields = ("api_abi_changed", "headers_changed",
                          "descriptor_registry_changed", "provider_registration_changed",
                          "cmake_target_added")
        self.assertTrue(all(boundary[name] is False for name in boolean_fields))

    def test_provider_not_added(self):
        provider = reference.read_strict_json(ROOT / "provider.json")
        self.assertFalse(provider["provider_added"])
        self.assertFalse(provider["registration_call_added"])

    def test_c_boundary_default_off(self):
        adapter = reference.read_strict_json(ROOT / "adapter.json")
        self.assertEqual(adapter["c_boundary"]["default"], "OFF")

    def test_build_evidence_recorded(self):
        build = reference.read_strict_json(ROOT / "report.json")["build_evidence"]
        self.assertEqual(build["sdk_native_build_install_ctest"], "11/11")

    def test_rust_build_deferred(self):
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertEqual(report["tool"]["rust"]["native_build"], "DEFER")

    def test_sources_manifest_shape(self):
        lines = (ROOT / "SOURCES.sha256").read_text(encoding="ascii").splitlines()
        self.assertTrue(any(line.startswith("PIN  ") for line in lines))
        self.assertTrue(any(line.endswith("  run.py") for line in lines))

    def test_licensing_check(self):
        self.assertEqual(check_licensing.check()["status"], "ok")

    def test_report_bytes_are_canonical(self):
        report = reference.read_strict_json(ROOT / "report.json")
        text, digest = reference.canonical_report(report)
        self.assertEqual((ROOT / "report.json").read_bytes(), text.encode("utf-8") + b"\n")
        self.assertEqual((ROOT / "report.json.sha256").read_text(encoding="ascii"), digest + "\n")


if __name__ == "__main__":
    unittest.main()
