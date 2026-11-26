# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit tests for the LLVC audio-I/O compatibility package."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
import unittest

import reference


def valid_request() -> dict:
    return {
        "tool": reference.TOOL_ID,
        "operation": "load",
        "python_version": "3.11.5",
        "torch_version": "2.15.0",
        "torchaudio_version": "2.11.1",
        "soundfile_version": "0.12.1",
        "torchcodec_status": reference.TORCHCODEC_STATUS,
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "samples": [0.0] * 160,
        "dtype": "float32",
        "source": "caller_owned",
        "lifecycle": "prepared",
    }


class StrictJsonTests(unittest.TestCase):
    def test_valid_object(self) -> None:
        self.assertEqual(reference.strict_json_loads('{"a":1}'), {"a": 1})

    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.JsonError):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_nan_and_infinity_rejected(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)

    def test_trailing_and_syntax_rejected(self) -> None:
        for text in ('{"a":1} extra', '{"a":}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(text)


class RequestValidationTests(unittest.TestCase):
    def test_valid_request_accepted(self) -> None:
        validated = reference.validate_request(valid_request())
        self.assertEqual(validated["tool"], reference.TOOL_ID)
        self.assertEqual(validated["torchaudio_version"], "2.11.1")
        self.assertEqual(validated["torchcodec_status"],
                         reference.TORCHCODEC_STATUS)
        self.assertEqual(len(validated["samples"]), 160)

    def test_unknown_and_missing_fields_rejected(self) -> None:
        request = valid_request()
        request["extra"] = True
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)
        request = valid_request()
        del request["torchcodec_status"]
        with self.assertRaises(reference.ConfigError):
            reference.validate_request(request)

    def test_unsupported_pins_rejected(self) -> None:
        cases = (
            ("python_version", "3.12.16"),
            ("torch_version", "2.14.1"),
            ("torchaudio_version", "2.11.0"),
            ("soundfile_version", "0.14.0"),
            ("torchcodec_status", "present"),
            ("dtype", "float64"),
            ("source", "downloaded"),
            ("tool", "llvc_runtime"),
            ("operation", "stream"),
        )
        for key, value in cases:
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=key):
                reference.validate_request(request)

    def test_nonfinite_and_out_of_range_rejected(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            request = valid_request()
            request["samples"][3] = value
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)
        request = valid_request()
        request["samples"][0] = 1.5
        with self.assertRaises(reference.InputError):
            reference.validate_request(request)

    def test_bool_and_string_samples_rejected(self) -> None:
        for value in (True, "0.0", None):
            request = valid_request()
            request["samples"][0] = value
            with self.assertRaises(reference.InputError):
                reference.validate_request(request)

    def test_geometry_and_lifecycle_rejected(self) -> None:
        for key, value in (
            ("sample_rate_hz", 48000),
            ("channels", 2),
            ("frame_samples", 320),
            ("lifecycle", "closed"),
        ):
            request = valid_request()
            request[key] = value
            with self.assertRaises(reference.EvidenceError, msg=key):
                reference.validate_request(request)

    def test_short_samples_rejected(self) -> None:
        request = valid_request()
        request["samples"] = [0.0] * 159
        with self.assertRaises(reference.InputError):
            reference.validate_request(request)

    def test_valid_request_fails_closed_without_runtime(self) -> None:
        with self.assertRaises(reference.RuntimeAbsent) as context:
            reference.probe_candidate(valid_request())
        self.assertEqual(context.exception.code, "RUNTIME_ABSENT")
        self.assertIn("RUNTIME_ABSENT", str(context.exception))

    def test_adverse_requests_all_rejected(self) -> None:
        data = reference._adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertGreaterEqual(data["case_count"], 22)
        self.assertTrue(all(not case["accepted"] for case in data["cases"]))

    def test_adverse_json_all_rejected(self) -> None:
        data = reference._json_adverse_cases()
        self.assertTrue(data["all_rejected"])
        self.assertEqual(data["accepted_count"], 0)
        self.assertIsNone(data["metrics"])
        self.assertEqual(data["case_count"], 6)


class ProbeTests(unittest.TestCase):
    def test_runtime_is_absent_and_unpinned(self) -> None:
        probe = reference.runtime_readiness()
        self.assertTrue(probe["blocked"])
        self.assertFalse(probe["exact_runtime_present"])
        self.assertFalse(probe["pinned"])
        self.assertEqual(probe["status"], "blocked_runtime_absent_unpinned")
        self.assertFalse(probe["runtime_imported"])
        availability = probe["package_availability_any_interpreter"]
        self.assertFalse(availability["torchaudio"])
        self.assertFalse(availability["torchcodec"])
        self.assertFalse((reference.EVAL_ROOT / ".venv-eval").exists())

    def test_partial_installations_are_not_qualified(self) -> None:
        probe = reference.runtime_readiness()
        for row in probe["partial_installations"]:
            self.assertFalse(row["qualified"], row["dist_info"])

    def test_exact_runtime_absence_paths(self) -> None:
        probe = reference.absence_probe()
        self.assertTrue(probe["all_exact_runtime_artifacts_absent"])
        self.assertEqual(probe["exact_runtime_artifacts_found"], [])

    def test_shim_source_is_pinned_and_checks_pass(self) -> None:
        probe = reference.shim_source_probe()
        self.assertEqual(probe["status"], "pinned_source_checks_pass")
        self.assertEqual(probe["wrapper_sha256"],
                         reference.SOURCE_PINS[reference.SHIM_WRAPPER_PATH])
        self.assertEqual(len(probe["checks"]), 4)
        self.assertEqual(len(probe["upstream_checks"]), 3)
        self.assertTrue(all(item["present"] for item in probe["checks"]))
        self.assertTrue(all(item["present"]
                            for item in probe["upstream_checks"]))
        self.assertFalse(probe["executed"])

    def test_source_pins_match_bytes(self) -> None:
        for path, digest in reference.SOURCE_PINS.items():
            target = reference.WORKSPACE / path
            self.assertTrue(target.is_file(), path)
            self.assertEqual(reference.sha256_file(target), digest, path)

    def test_boundary_pins_match_bytes(self) -> None:
        for path, digest in reference.BOUNDARY_PINS.items():
            target = reference.SDK_ROOT / path
            self.assertTrue(target.is_file(), path)
            self.assertEqual(reference.sha256_file(target), digest, path)

    def test_timing_is_arithmetic_not_measurement(self) -> None:
        timing = reference.historical_timing()
        self.assertEqual(timing["chunk_samples"], 208)
        self.assertEqual(timing["chunk_ms"], 13.0)
        self.assertEqual(timing["lookahead_samples"], 32)
        self.assertEqual(timing["algorithmic_latency_samples"], 240)
        self.assertEqual(timing["algorithmic_latency_ms"], 15.0)
        self.assertEqual(timing["chunk_count"], 743)
        self.assertFalse(timing["measured_here"])
        self.assertFalse(timing["reproduced_here"])
        self.assertFalse(timing["shim_overhead_measured"])
        self.assertEqual(timing["source_reported"]["rtf"], 0.123)
        self.assertEqual(timing["source_reported"]["e2e_latency_ms"], 120.785)
        self.assertIn("not a local measurement",
                      timing["derived_from_source_reported_rtf"]["note"])
        self.assertGreater(
            timing["derived_from_source_reported_rtf"]["deadline_miss_ratio"],
            9.0)


class WavContractTests(unittest.TestCase):
    def test_model_cases_are_exact_and_stable(self) -> None:
        probe = reference.wav_contract_probe()
        self.assertFalse(probe["real_soundfile_used"])
        self.assertFalse(probe["real_torchaudio_used"])
        self.assertFalse(probe["candidate_processing"])
        self.assertEqual(len(probe["cases"]), 5)
        self.assertTrue(probe["all_sample_counts_exact"])
        self.assertTrue(probe["all_channel_orientations_ok"])
        self.assertTrue(probe["all_roundtrips_byte_identical"])
        self.assertTrue(probe["all_quantization_within_bound"])
        self.assertTrue(probe["all_rejections_closed"])

    def test_stereo_orientation_is_channels_first(self) -> None:
        probe = reference.wav_contract_probe()
        stereo = [case for case in probe["cases"] if case["name"] == "stereo"]
        self.assertEqual(len(stereo), 1)
        self.assertEqual(stereo[0]["channel_count"], 2)
        self.assertTrue(stereo[0]["channel_orientation_ok"])
        self.assertTrue(stereo[0]["roundtrip_byte_identical"])

    def test_full_scale_clipping_is_reported(self) -> None:
        probe = reference.wav_contract_probe()
        full_scale = [case for case in probe["cases"]
                      if case["name"] == "full_scale"][0]
        self.assertGreater(full_scale["clipped_count"], 0)

    def test_malformed_wav_rejected(self) -> None:
        probe = reference.wav_contract_probe()
        rejections = probe["rejections"]
        self.assertTrue(rejections["all_rejected"])
        self.assertEqual(rejections["accepted_count"], 0)
        self.assertGreaterEqual(rejections["case_count"], 12)
        for case in rejections["cases"]:
            self.assertFalse(case["accepted"], case["id"])

    def test_identity_control_is_bit_exact(self) -> None:
        control = reference.wav_contract_probe()["identity_control"]
        self.assertTrue(control["encode_byte_identical"])
        self.assertTrue(control["decode_digest_identical"])

    def test_nonfinite_write_rejected(self) -> None:
        for value in (float("nan"), float("inf")):
            with self.assertRaises(reference.WavContractError):
                reference.encode_wav_pcm16(((value,),), 16000)

    def test_decode_is_deterministic(self) -> None:
        payload, _ = reference.encode_wav_pcm16(
            ((0.0, 0.25, -0.25),), 16000)
        first = reference.decode_wav_float32(payload)
        second = reference.decode_wav_float32(payload)
        self.assertEqual(first, second)
        self.assertEqual(first["channels"], 1)
        self.assertEqual(first["sample_count"], 3)


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
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["proposal_only"])
        self.assertEqual(report["profile"], "tool")
        self.assertEqual(report["profile_label"], "Tool")
        qualification = report["qualification"]
        self.assertEqual(qualification["status"], "not_qualified")
        self.assertEqual(qualification["readiness"], "incomplete")
        self.assertTrue(qualification["proposal_only"])
        self.assertFalse(qualification["candidate_qualified"])
        self.assertFalse(qualification["shim_executed"])
        self.assertFalse(qualification["tool_profile_result"])
        self.assertFalse(qualification["release_claim"])

    def test_eight_release_gates_blocked(self) -> None:
        report = reference.build_report()
        gate_ids = ["RG-0" + str(number) for number in range(1, 9)]
        self.assertEqual(report["gates"], gate_ids)
        self.assertEqual(report["remaining_gates"], gate_ids)
        self.assertEqual(len(report["release_gates"]), 8)
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in report["release_gates"]))
        self.assertTrue(all(gate["statement"] and gate["reopen_condition"]
                            for gate in report["release_gates"]))
        self.assertTrue(all(gate["qualifies"] is False
                            for gate in report["release_gates"]))
        self.assertTrue(
            report["qualification"]["all_release_gates_blocked"])

    def test_no_result_qualifies(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["counts"]["qualifying_results"], 0)
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        self.assertFalse(report["tool_profile"]["satisfied"])
        for value in report["required_results"].values():
            self.assertNotIn(value, ("passed", "qualified", "measured"))
        for row in report["tool_profile"]["requirements"]:
            self.assertIn(row["status"],
                          ("blocked", "not_run", "synthetic_pass"))
        for row in report["exact_blockers"]:
            self.assertFalse(row["qualifies"])

    def test_missing_result_never_qualifies(self) -> None:
        missing = reference.missing_result("fixture")
        self.assertEqual(missing["status"], "blocked")
        self.assertIsNone(missing["metrics"])
        self.assertFalse(missing["qualifies_candidate"])

    def test_boundary_and_scope_are_closed(self) -> None:
        report = reference.build_report()
        scope = report["scope"]
        for key in (
            "runtime_installed", "runtime_imported", "runtime_executed",
            "shim_executed", "network_used", "real_assets_used",
            "real_corpus_used", "provider_registered", "public_abi_changed",
            "registry_or_default_changed", "shared_build_or_ci_changed",
            "benchmark_run", "device_timing_measured", "listening_performed",
            "release_claim",
        ):
            self.assertFalse(scope[key], key)
        self.assertTrue(scope["task_local_only"])
        boundary = report["boundary"]
        self.assertTrue(boundary["linked_row_identity_only"])
        self.assertFalse(boundary["board_file_pinned"])
        self.assertFalse(boundary["mutable_board_fields_gate"])
        self.assertEqual(report["public_v0_geometry"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "float32", "frame_samples": 160,
            "changed": False,
        })

    def test_board_projection_is_stable_only(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertEqual(digest, reference.sha256_bytes(
            reference.canonical_bytes(links)))
        self.assertNotIn(
            "audio-benchmark-platform/plan/swarm/TASKS.json",
            reference.SOURCE_PINS)
        self.assertNotIn("audio-benchmark-platform/plan/swarm/TASKS.json",
                         reference.BOUNDARY_PINS)

    def test_artifact_pins_match_files(self) -> None:
        pins = reference.artifact_pins()
        self.assertEqual(set(pins), set(reference.SOURCE_ARTIFACT_FILES))
        for name, digest in pins.items():
            path = reference.HERE / name
            self.assertEqual(reference.sha256_file(path), digest, name)

    def test_upstream_blocker_is_explicit(self) -> None:
        blocker = reference.UPSTREAM_BLOCKER
        self.assertEqual(blocker["status"],
                         "blocked_runtime_absent_and_unpinned")
        self.assertIsNone(blocker["runtime_digest"])
        self.assertTrue(blocker["no_upstream_parity_claim"])
        self.assertIsNone(blocker["missing"]["torchcodec"]["version"])
        self.assertIsNone(blocker["missing"]["torchcodec"]["sha256"])
        self.assertIsNone(blocker["missing"]["torchaudio"]["sha256"])
        self.assertIsNone(blocker["missing"]["soundfile"]["sha256"])
        self.assertIn("consent", blocker["rights_requirement"].lower())


if __name__ == "__main__":
    unittest.main()
