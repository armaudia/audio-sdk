# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance tests for the task-local evidence package."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            reference.load_strict_json_text('{"a":1,"a":2}')

    def test_nonfinite_constants_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaisesRegex(ValueError, "nonfinite_json_constant"):
                reference.load_strict_json_text('{"a":' + token + "}")

    def test_malformed_and_nonobject_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid_json"):
            reference.load_strict_json_text('{"a":')
        with self.assertRaisesRegex(ValueError, "json_not_object"):
            reference.load_strict_json_text("[1,2,3]")


class ConfigAndFixtureTests(unittest.TestCase):
    def test_valid_config(self) -> None:
        config = {
            "sample_rate_hz": 16000, "channels": 1, "frame_samples": 160,
            "sample_format": "float32", "clock_ppm": 0, "resampling": "none",
            "algorithmic_latency_samples": 0, "precision": "float32",
        }
        self.assertEqual(reference.validate_config(config), config)

    def test_config_rejects_nonfinite_and_bool(self) -> None:
        base = {
            "sample_rate_hz": 16000, "channels": 1, "frame_samples": 160,
            "sample_format": "float32", "clock_ppm": 0, "resampling": "none",
            "algorithmic_latency_samples": 0, "precision": "float32",
        }
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_config({**base, "sample_rate_hz": True})
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_config({**base, "precision": "fp16"})

    def test_fixture_is_deterministic_and_bounded(self) -> None:
        first = reference.build_fixture()
        second = reference.build_fixture()
        self.assertEqual(first, second)
        self.assertEqual(len(first["clean"]), reference.FIXTURE_LENGTH)
        self.assertEqual(len(first["noise"]), reference.FIXTURE_LENGTH)
        self.assertEqual(len(first["noisy"]), reference.FIXTURE_LENGTH)
        self.assertTrue(all(value == 0 for value in
                            first["clean"][reference.ACTIVE_END:]))
        self.assertTrue(any(value != 0 for value in
                            first["noise"][reference.ACTIVE_END:]))
        self.assertTrue(all(abs(value) <= 32768 for value in first["noisy"]))

    def test_fixture_validation_rejects_bad_geometry(self) -> None:
        spec = reference.fixture_spec()
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture({**spec, "length_samples": 7999})
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_fixture(
                {**spec, "segments": spec["segments"][:-1]})


class SurrogateTests(unittest.TestCase):
    def test_metrics_improve_and_are_finite(self) -> None:
        run = reference.enhancement_run()
        self.assertGreater(run["delta_si_sdr_millidb"], 0)
        self.assertGreater(run["delta_snr_millidb"], 0)
        self.assertEqual(run["output_metrics"]["nonfinite_output_count"], 0)
        self.assertLess(run["output_metrics"]["peak_milli"], 1000)
        self.assertGreater(run["envelope_correlation_millipoints"], 0)
        self.assertLessEqual(run["envelope_correlation_millipoints"], 1000)

    def test_streaming_is_block_invariant(self) -> None:
        run = reference.enhancement_run()
        check = reference.streaming_check(run)
        self.assertTrue(check["all_match"])
        self.assertEqual(check["offline_state_digest"],
                         check["streamed_state_digest"])
        self.assertEqual(sum(check["chunks"]), reference.FIXTURE_LENGTH)

    def test_reset_matches_fresh_session(self) -> None:
        check = reference.reset_check()
        self.assertTrue(check["matches_fresh"])
        self.assertEqual(check["epoch"], 2)

    def test_final_partial_frame(self) -> None:
        check = reference.final_partial_check()
        self.assertEqual(check["valid_count"], reference.FINAL_PARTIAL_VALID)
        self.assertEqual(check["advanced_samples"],
                         reference.FINAL_PARTIAL_VALID)
        self.assertTrue(check["tail_zero"])
        self.assertEqual(check["nonfinite_output_count"], 0)


class AdverseTests(unittest.TestCase):
    def test_all_adverse_cases_rejected_with_state_unchanged(self) -> None:
        cases = reference.adverse_rejections()
        self.assertGreaterEqual(len(cases), 40)
        for case in cases:
            self.assertEqual(case["status"], "rejected", case["case_id"])
            self.assertIs(case["state_unchanged"], True, case["case_id"])
        codes = {case["code"] for case in cases}
        for required in ("duplicate_json_key:a",
                         "nonfinite_json_constant:NaN",
                         "nonfinite_input:input", "padding_not_zero:input",
                         "unsupported_delegate", "unsupported_precision"):
            self.assertIn(required, codes)

    def test_caller_manifest_validates_without_loading(self) -> None:
        manifest = {
            "android_target": "example/Android/arm64-v8a",
            "candidate": "cmgan-litert-community-port",
            "channels": 1,
            "delegate": "npu",
            "frame_samples": 160,
            "input_format": "float32",
            "model_byte_count": 1024,
            "model_path": "/caller/cmgan-litert/model.tflite",
            "model_sha256": "0" * 64,
            "precision": "fp16",
            "runtime_path": "/caller/litert/liblitert.so",
            "runtime_sha256": "3" * 64,
            "runtime_version": "caller-supplied",
            "sample_rate_hz": 16000,
            "source_revision": "1" * 40,
            "source_sha256": "2" * 64,
            "source_url": reference.CANDIDATE_CARD_URL,
        }
        result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["validated"])
        self.assertFalse(result["loaded"])
        self.assertFalse(result["executed"])
        self.assertFalse(result["imported"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_scope_and_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["task"], reference.TASK_ID)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["status"], "proposal_only_synthetic_incomplete")
        self.assertFalse(report["qualification"]["qualifies"])
        self.assertFalse(report["qualification"]["missing_result_promoted"])
        self.assertFalse(report["reference"]["source_present"])
        self.assertFalse(report["reference"]["weights_present"])
        self.assertFalse(report["reference"]["runtime_present"])
        self.assertFalse(report["candidate"]["conversion_parity_verified"])
        self.assertEqual(report["stoi"]["status"], "blocked_not_measured")

    def test_eight_release_gates_blocked(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-0" + str(index) for index in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_profile_items_are_not_promoted(self) -> None:
        items = self.report["acceptance_profile"]["required_items"]
        self.assertGreaterEqual(len(items), 10)
        for name, item in items.items():
            self.assertIn(item["status"],
                          {"synthetic_only", "blocked", "blocked_unmeasured"},
                          name)
        self.assertIn("task_matched_baseline", self.report["profile_blockers"])
        self.assertIn("stoi", self.report["profile_blockers"])
        self.assertIn("heldout_qualification",
                      self.report["profile_blockers"])

    def test_adverse_and_negative_claims(self) -> None:
        self.assertTrue(self.report["adverse_all_rejected"])
        self.assertTrue(self.report["negative_claims"])
        self.assertTrue(all(isinstance(claim, str)
                            for claim in self.report["negative_claims"]))
        boundary = self.report["boundary"]
        self.assertTrue(boundary)
        self.assertTrue(all(value is False for value in boundary.values()))

    def test_board_identity_is_stable_fields_only(self) -> None:
        row = self.report["board_row"]
        self.assertEqual(row["stable_sha256"],
                         reference.BOARD_ROW_STABLE_SHA256)
        self.assertFalse(row["full_tasks_json_hashed"])
        self.assertEqual(row["stable_fields"]["id"], reference.TASK_ID)

    def test_report_is_byte_identical_three_times(self) -> None:
        payloads = [reference.canonical_report(reference.build_report())[0]
                    for _ in range(3)]
        self.assertEqual(len(set(payloads)), 1)

    def test_canonical_json_has_no_nan(self) -> None:
        text = reference.canonical_text(self.report)
        self.assertEqual(reference.load_strict_json_text(text), self.report)
        for value in self.report["adverse_rejections"]:
            self.assertFalse(isinstance(value, float))
        self.assertTrue(all(
            not isinstance(item, float) or math.isfinite(item)
            for item in self.report.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
