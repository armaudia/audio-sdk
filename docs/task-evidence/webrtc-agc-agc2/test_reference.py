# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic standard-library acceptance tests for SDK-WEBRTC-AGC-AGC2."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import reference

HERE = Path(__file__).resolve().parent
REPORT = reference.build_report()
REPORT_BYTES = reference.report_bytes()


def artifact(name: str) -> Path:
    return HERE / name


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _finite_json(value):
    if isinstance(value, float):
        return value == value and value not in (float("inf"), float("-inf"))
    if isinstance(value, dict):
        return all(_finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(_finite_json(item) for item in value)
    return True


class InvariantTests(unittest.TestCase):
    def test_identity_status_and_decision(self) -> None:
        self.assertEqual(REPORT["task"], "SDK-WEBRTC-AGC-AGC2")
        self.assertEqual(REPORT["component"], "webrtc-agc-agc2")
        self.assertEqual(REPORT["decision"], "DEFER")
        self.assertEqual(REPORT["status"], "proposal_only_not_qualified")
        self.assertEqual(REPORT["qualification_status"], "not_qualified")
        self.assertEqual(REPORT["qualification"]["status"], "not_qualified")
        self.assertEqual(REPORT["qualification"]["readiness"], "incomplete")
        self.assertFalse(REPORT["qualification"]["candidate_qualified"])
        self.assertFalse(REPORT["qualification"]["upstream_parity"])
        self.assertFalse(REPORT["qualification"]["all_required_results_present"])

    def test_all_eight_release_gates_blocked(self) -> None:
        gates = REPORT["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-0" + str(number) for number in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["reason"] and gate["reopen"] for gate in gates))
        self.assertEqual(REPORT["remaining_gates"], REPORT["gates"])

    def test_upstream_blocker_is_explicit_not_fabricated(self) -> None:
        blocker = REPORT["upstream_blocker"]
        self.assertEqual(blocker["status"], "blocked_upstream_absent")
        self.assertIsNone(blocker["pinned_revision"])
        self.assertIsNone(blocker["source_digest"])
        self.assertIsNone(blocker["runtime_digest"])
        self.assertTrue(blocker["no_upstream_parity_claim"])
        self.assertIn("Apache-2.0", blocker["expected_license"])
        self.assertIn("rights_requirement", blocker)
        self.assertIn("required_runtime", blocker)
        for revision in blocker["documented_reference_revisions"]:
            self.assertFalse(revision["verified_locally"])
            self.assertEqual(len(revision["revision"]), 40)

    def test_installed_v0_boundary_is_unchanged(self) -> None:
        boundary = REPORT["boundary"]
        self.assertEqual(boundary["format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "float32", "frame_samples": 160,
        })
        self.assertTrue(boundary["installed_v0_unchanged"])
        for key in ("public_api_abi_changed", "provider_registered",
                    "descriptor_registration", "enabled_by_default",
                    "registry_changed", "shared_cmake_changed", "ci_changed",
                    "board_or_handoff_changed", "real_corpus_or_weights",
                    "benchmark_claim", "release_claim"):
            self.assertFalse(boundary[key], key)

    def test_reference_is_not_candidate_processing(self) -> None:
        block = REPORT["reference"]
        self.assertFalse(block["real_webrtc_source_or_binary"])
        self.assertFalse(block["upstream_parity"])
        self.assertFalse(block["downloads"])
        self.assertFalse(block["model_weights"])
        self.assertFalse(block["candidate_processing"])
        self.assertTrue(block["synthetic_only"])
        self.assertTrue(block["deterministic"])

    def test_profile_mapping_is_blocked_or_partial(self) -> None:
        for key, value in REPORT["profile_mapping"].items():
            self.assertTrue(
                value.startswith("blocked_") or
                value.startswith("partial_") or
                value.startswith("characterised_") or
                value.startswith("unresolved_"), key)

    def test_local_harness_checks_are_true(self) -> None:
        self.assertTrue(all(REPORT["local_harness_checks"].values()))
        self.assertTrue(REPORT["local_harness_checks"][
            "absence_probe_complete"])


class BoardIdentityTests(unittest.TestCase):
    def test_stable_projection_only(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertEqual(digest, REPORT["board_link_projection_sha256"])
        for row in links:
            self.assertEqual(set(row), set(reference.LINK_FIELDS))
            for mutable in ("status", "owner", "history", "review", "handoff"):
                self.assertNotIn(mutable, row)

    def test_full_board_digest_never_enters_canonical_bytes(self) -> None:
        board = reference.BOARD_PATH.read_bytes()
        full_digest = sha256_bytes(board)
        for payload in (REPORT_BYTES, (HERE / "contract.json").read_bytes()
                        if (HERE / "contract.json").is_file() else b"",
                        (HERE / "SOURCES.sha256").read_bytes()
                        if (HERE / "SOURCES.sha256").is_file() else b""):
            self.assertNotIn(full_digest.encode("ascii"), payload)
            self.assertNotIn(b"plan/swarm/TASKS.json", payload)

    def test_mutable_fields_are_documented_as_excluded(self) -> None:
        excluded = REPORT["board_mutable_fields_excluded"]
        for name in ("status", "owner", "history", "review", "handoff"):
            self.assertIn(name, excluded)


class RequestValidationTests(unittest.TestCase):
    def _base(self):
        return {
            "candidate": "webrtc_agc2",
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "samples": [0.0] * 160,
            "epoch": 0,
            "first_input_sample": 0,
            "lifecycle": "prepared",
            "execution_mode": 1,
        }

    def test_valid_request_normalizes(self) -> None:
        value = reference.validate_request(self._base())
        self.assertEqual(value["candidate"], "webrtc_agc2")
        self.assertEqual(value["frame_samples"], 160)
        self.assertEqual(len(value["samples"]), 160)

    def test_both_candidates_fail_closed_as_upstream_absent(self) -> None:
        for candidate in reference.CANDIDATES:
            request = self._base()
            request["candidate"] = candidate
            with self.assertRaises(reference.UpstreamAbsent) as context:
                reference.probe_candidate(request)
            self.assertEqual(context.exception.code, "UPSTREAM_ABSENT")

    def test_unknown_and_missing_fields_rejected(self) -> None:
        request = self._base()
        request["extra"] = 1
        with self.assertRaises(reference.ConfigError) as context:
            reference.validate_request(request)
        self.assertEqual(context.exception.code, "UNKNOWN_FIELD")
        request = self._base()
        del request["epoch"]
        with self.assertRaises(reference.ConfigError) as context:
            reference.validate_request(request)
        self.assertEqual(context.exception.code, "MISSING_FIELD")

    def test_unknown_candidate_rejected(self) -> None:
        request = self._base()
        request["candidate"] = "webrtc_agc3"
        with self.assertRaises(reference.ConfigError) as context:
            reference.validate_request(request)
        self.assertEqual(context.exception.code, "UNKNOWN_CANDIDATE")

    def test_wrong_geometry_rejected(self) -> None:
        for key, value, code in (
                ("sample_rate_hz", 48000, "WRONG_RATE"),
                ("channels", 2, "WRONG_CHANNELS"),
                ("frame_samples", 320, "WRONG_FRAME")):
            request = self._base()
            request[key] = value
            with self.assertRaises(reference.ConfigError) as context:
                reference.validate_request(request)
            self.assertEqual(context.exception.code, code)

    def test_wrong_sample_count_rejected(self) -> None:
        request = self._base()
        request["samples"] = [0.0] * 159
        with self.assertRaises(reference.InputError) as context:
            reference.validate_request(request)
        self.assertEqual(context.exception.code, "WRONG_SAMPLE_COUNT")

    def test_nonfinite_and_out_of_range_rejected(self) -> None:
        for value, code in ((float("nan"), "NONFINITE"),
                            (float("inf"), "NONFINITE"),
                            (float("-inf"), "NONFINITE"),
                            (4.5, "OUT_OF_RANGE"),
                            (-4.5, "OUT_OF_RANGE")):
            request = self._base()
            request["samples"][7] = value
            with self.assertRaises(reference.InputError) as context:
                reference.validate_request(request)
            self.assertEqual(context.exception.code, code)

    def test_invalid_sample_types_rejected(self) -> None:
        for value in (True, "0.1", None, [0.1], object()):
            request = self._base()
            request["samples"][3] = value
            with self.assertRaises(reference.InputError) as context:
                reference.validate_request(request)
            self.assertEqual(context.exception.code, "INVALID_SAMPLE_TYPE")

    def test_invalid_lifecycle_epoch_position_and_mode_rejected(self) -> None:
        for key, value, code in (
                ("epoch", -1, "INVALID_EPOCH"),
                ("epoch", True, "INVALID_EPOCH"),
                ("first_input_sample", -160, "INVALID_POSITION"),
                ("lifecycle", "closed", "INVALID_LIFECYCLE"),
                ("lifecycle", "drained", "INVALID_LIFECYCLE"),
                ("execution_mode", 4, "INVALID_MODE"),
                ("execution_mode", True, "INVALID_MODE")):
            request = self._base()
            request[key] = value
            with self.assertRaises(reference.ConfigError) as context:
                reference.validate_request(request)
            self.assertEqual(context.exception.code, code)

    def test_non_object_request_rejected(self) -> None:
        for value in (None, [], "request", 1):
            with self.assertRaises(reference.InputError) as context:
                reference.validate_request(value)
            self.assertEqual(context.exception.code, "INVALID_REQUEST")


class JsonTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate_and_nonfinite(self) -> None:
        for payload in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
                        '{"a":-Infinity}', '{"a":1} extra', '{"a":}'):
            with self.assertRaises(reference.JsonError):
                reference.strict_json_loads(payload)

    def test_strict_json_accepts_clean_object(self) -> None:
        self.assertEqual(reference.strict_json_loads('{"a":1}'), {"a": 1})

    def test_canonical_bytes_are_stable(self) -> None:
        value = {"b": [3, 2, 1], "a": {"d": 4, "c": 5}}
        first = reference.canonical_bytes(value)
        second = reference.canonical_bytes(value)
        self.assertEqual(first, second)
        self.assertEqual(first, b'{"a":{"c":5,"d":4},"b":[3,2,1]}')

    def test_canonical_bytes_reject_nonfinite(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"a": float("nan")})

    def test_report_is_finite_json(self) -> None:
        self.assertTrue(_finite_json(REPORT))


class StimulusTests(unittest.TestCase):
    def test_silence_is_exact_zero(self) -> None:
        metrics = reference.stimulus_metrics("silence", reference.silence(320))
        self.assertEqual(metrics["peak_abs"], 0.0)
        self.assertEqual(metrics["rms"], 0.0)
        self.assertEqual(metrics["nonfinite_count"], 0)

    def test_impulse_position_and_peak(self) -> None:
        samples = reference.impulse(1600, 800, 0.5)
        self.assertEqual(samples[800], 0.5)
        self.assertEqual(reference.peak_abs(samples), 0.5)
        self.assertEqual(sum(1 for value in samples if value != 0.0), 1)

    def test_step_geometry(self) -> None:
        samples = reference.step(1600, 800, 0.25)
        self.assertTrue(all(value == 0.0 for value in samples[:800]))
        self.assertTrue(all(value == 0.25 for value in samples[800:]))

    def test_sweep_is_finite_and_bounded(self) -> None:
        samples = reference.sweep(1600, 200.0, 3000.0, 0.3)
        metrics = reference.stimulus_metrics("sweep", samples)
        self.assertEqual(metrics["sample_count"], 1600)
        self.assertEqual(metrics["nonfinite_count"], 0)
        self.assertLessEqual(metrics["peak_abs"], 0.300000001)

    def test_speech_like_has_voiced_pause_contrast(self) -> None:
        samples = reference.speech_like(3200)
        contrast = reference.speech_contrast(samples)
        self.assertGreater(contrast["voiced_to_pause_db"], 10.0)
        self.assertGreater(contrast["voiced_rms"], contrast["pause_rms"])

    def test_stimulus_digests_are_deterministic(self) -> None:
        for name, generator in reference.STIMULUS_GENERATORS.items():
            first = reference.tensor_digest(generator())
            second = reference.tensor_digest(generator())
            self.assertEqual(first, second, name)

    def test_nonfinite_stimulus_rejected(self) -> None:
        with self.assertRaises(reference.InputError) as context:
            reference.stimulus_metrics("bad", [0.0, float("nan")])
        self.assertEqual(context.exception.code, "NONFINITE")

    def test_out_of_range_stimulus_rejected(self) -> None:
        with self.assertRaises(reference.InputError) as context:
            reference.stimulus_metrics("bad", [0.0, 3.0])
        self.assertEqual(context.exception.code, "OUT_OF_RANGE")


class ReportTests(unittest.TestCase):
    def test_absence_probe_finds_no_upstream(self) -> None:
        probe = REPORT["absence_probe"]
        self.assertEqual(probe["status"], "blocked_upstream_absent")
        self.assertFalse(probe["present"])
        self.assertEqual(probe["match_count"], 0)
        self.assertEqual(probe["found_count"], 0)
        self.assertFalse(probe["scan_truncated"])
        self.assertIn("sdk", probe["roots_scanned"])

    def test_candidates_are_blocked_without_metrics(self) -> None:
        for name, block in REPORT["candidates"].items():
            self.assertEqual(block["status"], "blocked_upstream_absent", name)
            self.assertIsNone(block["metrics"], name)
            self.assertFalse(block["qualifies_candidate"], name)
            self.assertEqual(block["apm_mode_ownership"], "unresolved", name)

    def test_separate_dsp_agc_comparison_is_blocked(self) -> None:
        block = REPORT["separate_dsp_agc_comparison"]
        self.assertEqual(block["status"], "blocked_upstream_absent")
        self.assertIsNone(block["candidate_metrics"])
        self.assertIsNone(block["control_metrics"])
        self.assertFalse(block["qualifies_candidate"])

    def test_apm_mode_ownership_is_unresolved(self) -> None:
        block = REPORT["apm_mode_ownership"]
        self.assertEqual(block["status"], "unresolved")
        self.assertIsNone(block["owner"])
        self.assertEqual(block["declared_modes"], [])
        self.assertFalse(block["qualifies_candidate"])
        for value in block["execution_modes"].values():
            self.assertEqual(value, "unresolved")

    def test_required_candidate_results_are_not_met(self) -> None:
        results = REPORT["required_results"]
        self.assertTrue(results)
        self.assertTrue(all(value in ("blocked_upstream_absent",
                                      "partial_local_harness_only")
                            for value in results.values()))
        self.assertEqual(results["numerical_and_nonfinite"],
                         "partial_local_harness_only")

    def test_adverse_cases_fail_closed(self) -> None:
        for key in ("invalid_config_and_input", "invalid_json_numeric_fields"):
            block = REPORT["adverse"][key]
            self.assertTrue(block["all_rejected"], key)
            self.assertEqual(block["accepted_count"], 0)
            self.assertIsNone(block["metrics"])
            for case in block["cases"]:
                self.assertFalse(case["accepted"], case)
                self.assertNotEqual(case["error"], "NOT_REJECTED")

    def test_missing_result_is_blocked_without_metrics(self) -> None:
        missing = REPORT["adverse"]["missing_result"]
        self.assertEqual(missing["status"], "blocked")
        self.assertIsNone(missing["metrics"])
        self.assertFalse(missing["qualifies_candidate"])

    def test_stimulus_probe_is_not_candidate_processing(self) -> None:
        probe = REPORT["stimulus_probe"]
        self.assertFalse(probe["candidate_processing"])
        self.assertTrue(all(block["byte_identical"]
                            for block in probe["identity_control"].values()))
        self.assertGreater(probe["speech_contrast"]["voiced_to_pause_db"], 10.0)

    def test_report_bytes_have_one_trailing_newline(self) -> None:
        self.assertTrue(REPORT_BYTES.endswith(b"\n"))
        self.assertFalse(REPORT_BYTES.endswith(b"\n\n"))
        self.assertNotIn(b"NaN", REPORT_BYTES)
        self.assertNotIn(b"Infinity", REPORT_BYTES)

    def test_report_value_and_bytes_agree(self) -> None:
        value = reference.strict_json_loads(REPORT_BYTES.decode("utf-8"))
        self.assertEqual(reference.canonical_bytes(value) + b"\n", REPORT_BYTES)

    def test_artifact_pins_match_files(self) -> None:
        for name, digest in REPORT["artifact_pins"].items():
            self.assertTrue(artifact(name).is_file(), name)
            self.assertEqual(sha256_file(artifact(name)), digest, name)

    def test_source_and_boundary_pins_match(self) -> None:
        for path, digest in REPORT["source_pins"].items():
            self.assertEqual(sha256_file(reference.WORKSPACE / path), digest,
                             path)
        for path, digest in REPORT["boundary_pins"].items():
            self.assertEqual(sha256_file(reference.SDK_ROOT / path), digest,
                             path)

    def test_no_forbidden_upstream_artifact_in_package(self) -> None:
        forbidden_suffixes = {".wav", ".flac", ".mp3", ".ogg", ".opus",
                              ".onnx", ".pt", ".bin", ".so", ".dylib", ".a",
                              ".o", ".zip", ".tar", ".gz", ".whl"}
        for path in sorted(HERE.rglob("*")):
            if not path.is_file():
                continue
            lower = path.name.lower()
            self.assertNotIn(lower, reference.EXACT_UPSTREAM_NAMES, str(path))
            self.assertNotIn(path.suffix.lower(), forbidden_suffixes, str(path))

    def test_run_stdout_report_matches_committed_bytes(self) -> None:
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        process = subprocess.run(
            [sys.executable, str(HERE / "run.py"), "--stdout-report"],
            cwd=str(HERE), capture_output=True, env=environment, check=False)
        self.assertEqual(process.returncode, 0, process.stderr.decode())
        self.assertEqual(process.stdout, REPORT_BYTES)

    def test_contract_matches_report(self) -> None:
        contract = reference.strict_json_loads(
            (HERE / "contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["task"], "SDK-WEBRTC-AGC-AGC2")
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_not_qualified")
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(contract["canonical_report"]["file_sha256"],
                         sha256_bytes(REPORT_BYTES))
        self.assertEqual(contract["board_link_projection_sha256"],
                         REPORT["board_link_projection_sha256"])
        self.assertEqual([gate["id"] for gate in contract["release_gates"]],
                         ["RG-0" + str(number) for number in range(1, 9)])
        self.assertTrue(all(gate["status"] == "blocked"
                            for gate in contract["release_gates"]))
        for name, digest in contract["artifact_pins"].items():
            self.assertEqual(sha256_file(HERE / name), digest, name)


if __name__ == "__main__":
    unittest.main()
