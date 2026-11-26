# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the SDK-LLVC blocker evidence package."""

from __future__ import annotations

import json
import math
import unittest

import reference


def valid_request() -> dict:
    return {
        "candidate": "llvc",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "samples": [0.0] * 160,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
        "target_condition": "builtin_any_to_one",
    }


class StrictJsonTests(unittest.TestCase):
    def test_valid_object(self) -> None:
        self.assertEqual(reference.strict_json_loads('{"a":1}'), {"a": 1})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}',
                     '{"a":-Infinity}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)

    def test_trailing_and_syntax_rejected(self) -> None:
        for text in ('{"a":1} extra', '{"a":}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)


class RequestValidationTests(unittest.TestCase):
    def test_valid_request_accepted(self) -> None:
        validated = reference.validate_request(valid_request())
        self.assertEqual(validated["candidate"], "llvc")
        self.assertEqual(validated["target_condition"],
                         "builtin_any_to_one")
        self.assertEqual(len(validated["samples"]), 160)

    def test_unknown_and_missing_fields_rejected(self) -> None:
        request = valid_request()
        request["extra"] = True
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)
        request = valid_request()
        del request["epoch"]
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)

    def test_nonfinite_and_out_of_range_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            request = valid_request()
            request["samples"][3] = value
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)
        request = valid_request()
        request["samples"][0] = 4.5
        with self.assertRaises(reference.InputError):
            reference.validate_request(request)

    def test_bool_and_string_samples_rejected(self) -> None:
        for value in (True, "0.0", None):
            request = valid_request()
            request["samples"][0] = value
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_geometry_and_lifecycle_rejected(self) -> None:
        cases = (
            ("sample_rate_hz", 48000),
            ("channels", 2),
            ("frame_samples", 320),
            ("epoch", -1),
            ("first_input_sample", -160),
            ("lifecycle", "drained"),
            ("execution_mode", 4),
            ("target_condition", "p360"),
            ("candidate", "llvc2"),
        )
        for key, value in cases:
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=key):
                reference.validate_request(request)

    def test_short_sample_list_rejected(self) -> None:
        request = valid_request()
        request["samples"] = [0.0] * 159
        with self.assertRaises(reference.InputError):
            reference.validate_request(request)

    def test_adverse_cases_all_rejected(self) -> None:
        data = reference._adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertGreaterEqual(data["case_count"], 20)
        self.assertTrue(all(not case["accepted"] for case in data["cases"]))

    def test_valid_request_fails_closed_without_weights(self) -> None:
        with self.assertRaises(reference.WeightsAbsent) as context:
            reference.probe_candidate(valid_request())
        self.assertEqual(context.exception.code, "WEIGHTS_ABSENT")
        self.assertIn("WEIGHTS_ABSENT", str(context.exception))


class ProbeTests(unittest.TestCase):
    def test_source_is_present_and_exactly_pinned(self) -> None:
        probe = reference.source_probe()
        self.assertTrue(probe["present"])
        self.assertEqual(probe["status"], "present_pinned")
        self.assertEqual(probe["revision"], reference.SOURCE_REVISION)
        self.assertEqual(probe["tree_digest"], reference.SOURCE_TREE_DIGEST)
        self.assertEqual(probe["file_count"], reference.SOURCE_FILE_COUNT)

    def test_weights_absent(self) -> None:
        probe = reference.weights_probe()
        self.assertFalse(probe["present"])
        self.assertEqual(probe["status"], "blocked_weights_absent")
        self.assertIsNone(probe["sha256"])
        self.assertEqual(probe["found"], [])

    def test_runtime_unpinned(self) -> None:
        probe = reference.runtime_probe()
        self.assertFalse(probe["pinned"])
        self.assertEqual(probe["status"], "blocked_runtime_unpinned")
        self.assertFalse(probe["importable_modules"]["torch"])

    def test_geometry_is_deterministic_and_not_measured(self) -> None:
        geometry = reference.geometry()
        self.assertEqual(geometry["chunk_samples"], 208)
        self.assertEqual(geometry["chunk_ms"], 13.0)
        self.assertEqual(geometry["lookahead_samples"], 32)
        self.assertEqual(geometry["algorithmic_latency_samples"], 240)
        self.assertEqual(geometry["algorithmic_latency_ms"], 15.0)
        self.assertEqual(geometry["chunk_count"], 743)
        self.assertEqual(geometry["padded_samples"], 154544)
        self.assertFalse(geometry["measured_here"])
        self.assertFalse(geometry["candidate_output"])
        self.assertAlmostEqual(geometry["source_duration_seconds"], 9.6550625)

    def test_source_reported_values_are_separated(self) -> None:
        geometry = reference.geometry()
        self.assertEqual(geometry["source_reported"]["rtf"], 0.123)
        self.assertEqual(geometry["source_reported"]["e2e_latency_ms"], 120.785)
        derived = geometry["derived_from_source_reported_rtf"]
        self.assertIn("not a local measurement", derived["note"])
        self.assertGreater(derived["deadline_miss_ratio"], 9.0)

    def test_historical_evidence_does_not_qualify(self) -> None:
        history = reference.historical_evidence()
        self.assertFalse(history["reproduced_here"])
        self.assertFalse(history["qualifies_candidate"])
        self.assertTrue(history["output_digest_matches_pin"])
        self.assertEqual(history["identity_similarity"], "not_scored")
        self.assertEqual(history["naturalness"], "not_scored")
        self.assertEqual(history["utterance_count"], 1)

    def test_stimulus_identity_is_bit_exact(self) -> None:
        probe = reference.stimulus_probe()
        self.assertFalse(probe["candidate_processing"])
        for block in probe["identity_control"].values():
            self.assertTrue(block["byte_identical"])
        for metrics in probe["stimuli"].values():
            self.assertEqual(metrics["nonfinite_count"], 0)
            self.assertLessEqual(metrics["peak_abs"],
                                 reference.MAX_ABS_STIMULUS)


class ReportTests(unittest.TestCase):
    def test_report_is_canonical_finite_and_stable(self) -> None:
        first = reference.report_bytes()
        second = reference.report_bytes()
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertFalse(first.endswith(b"\n\n"))
        report = reference.strict_json_loads(first.decode("utf-8"))
        self.assertEqual(reference.canonical_bytes(report) + b"\n", first)
        self.assertTrue(reference.finite_json(report))

    def test_decision_and_qualification(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["qualification"]["status"], "not_qualified")
        self.assertEqual(report["qualification"]["readiness"], "incomplete")
        self.assertTrue(report["qualification"]["proposal_only"])
        self.assertFalse(report["qualification"]["candidate_qualified"])
        self.assertFalse(report["qualification"]["upstream_parity"])

    def test_eight_release_gates_blocked(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["remaining_gates"], reference_gate_ids())
        self.assertEqual(report["gates"], reference_gate_ids())
        self.assertEqual(len(report["release_gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["release_gates"]))
        self.assertTrue(all(gate["reason"] and gate["reopen"]
                            for gate in report["release_gates"]))

    def test_candidate_and_required_results_do_not_qualify(self) -> None:
        report = reference.build_report()
        candidate = report["candidates"]["llvc"]
        self.assertIsNone(candidate["metrics"])
        self.assertFalse(candidate["qualifies_candidate"])
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        for value in report["required_results"].values():
            self.assertNotIn(value, ("passed", "qualified", "measured"))

    def test_boundary_is_closed(self) -> None:
        boundary = reference.build_report()["boundary"]
        for key in (
            "benchmark_claim", "board_or_handoff_changed", "ci_changed",
            "descriptor_default_changed", "descriptor_registration",
            "enabled_by_default", "provider_registered",
            "public_api_abi_changed", "real_corpus_or_weights",
            "release_claim", "shared_cmake_changed",
        ):
            self.assertFalse(boundary[key], key)
        self.assertTrue(boundary["installed_v0_unchanged"])
        self.assertEqual(boundary["format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "float32", "frame_samples": 160,
        })

    def test_voice_profile_mapping_is_blocked_or_source_reported(self) -> None:
        mapping = reference.voice_profile_mapping()
        self.assertEqual(mapping["identity_and_similarity"],
                         "blocked_not_scored")
        self.assertEqual(mapping["naturalness"], "blocked_no_listening_or_mos")
        self.assertEqual(mapping["candidate_output"],
                         "blocked_weights_and_runtime_absent")
        self.assertIn("source_reported",
                      mapping["text_and_semantic_content"])

    def test_board_projection_is_stable_only(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertEqual(digest,
                         reference.sha256_bytes(
                             reference.canonical_bytes(links)))
        self.assertNotIn(
            "audio-benchmark-platform/plan/swarm/TASKS.json",
            reference.SOURCE_PINS)

    def test_missing_result_never_qualifies(self) -> None:
        missing = reference.missing_result("fixture")
        self.assertEqual(missing["status"], "blocked")
        self.assertIsNone(missing["metrics"])
        self.assertFalse(missing["qualifies_candidate"])


def reference_gate_ids() -> list:
    return ["RG-0" + str(number) for number in range(1, 9)]


if __name__ == "__main__":
    unittest.main()
