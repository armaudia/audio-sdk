# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Standard-library acceptance suite for the task-local rate evidence package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import check_licensing
import fixture
import reference
import run
import scorer

HERE = Path(__file__).resolve().parent
LICENSE_LINE = "SPDX" "-License-Identifier:"
ALL_FILES = (
    "README.md", "SOURCES.sha256", "contract.json", "adapter.json",
    "provider.json", "reference.py", "scorer.py", "fixture.py", "run.py",
    "verify.py", "check_licensing.py", "test_reference.py", "report.json",
    "report.json.sha256",
)


def request_ref(identifier: str) -> dict:
    return {"kind": "synthetic", "id": identifier, "revision": 1}


def run_request(config: dict, **extra) -> dict:
    payload = {
        "protocol_version": 1,
        "operation": "run",
        "candidate_ref": request_ref("libsamplerate-reference"),
        "adapter_ref": request_ref("libsamplerate-adapter"),
        "configuration": config,
        "attempt_id": "unit-test",
        "ratio": 1.25,
        "samples": None,
    }
    payload.update(extra)
    return payload


class FileAndManifestTests(unittest.TestCase):
    def test_01_all_files_present(self):
        for name in ALL_FILES:
            self.assertTrue((HERE / name).is_file(), name)

    def test_02_spdx_headers(self):
        for name in ALL_FILES:
            if name.endswith((".py", ".md")):
                head = (HERE / name).read_text(encoding="utf-8")[:400]
                self.assertIn("SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes", head)
                self.assertIn("SPDX" "-License-Identifier: Apache-2.0", head)

    def test_03_no_full_license_token_in_python_body(self):
        for path in sorted(HERE.glob("*.py")):
            body = "\n".join(path.read_text(encoding="utf-8").splitlines()[2:])
            self.assertNotIn(LICENSE_LINE, body, path.name)

    def test_04_strict_json_loads(self):
        for name in ("report.json", "contract.json", "adapter.json", "provider.json"):
            payload = json.loads((HERE / name).read_text(encoding="utf-8"),
                                 parse_constant=lambda token: (_ for _ in ()).throw(
                                     ValueError(token)))
            self.assertIsInstance(payload, dict, name)

    def test_05_canonical_report_has_trailing_newline(self):
        payload = (HERE / "report.json").read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        canonical = reference.canonical_report(reference.build_report())[0]
        self.assertEqual(payload, (canonical + "\n").encode("utf-8"))

    def test_06_sidecar_matches_file_bytes(self):
        digest = scorer.sha256_bytes((HERE / "report.json").read_bytes())
        self.assertEqual((HERE / "report.json.sha256").read_text().strip(), digest)

    def test_07_licensing_clean(self):
        result = check_licensing.check()
        self.assertEqual(result["status"], "ok", result["problems"])
        self.assertFalse(result["upstream_license_present"])

    def test_08_sources_manifest_covers_artifacts(self):
        text = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        names = [line.split("  ", 1)[1] for line in text.splitlines()
                 if line and not line.startswith("#")]
        for name in set(run.SOURCE_ARTIFACT_NAMES) | {"contract.json"}:
            self.assertIn(reference.TASK_PREFIX + name, names)
        for path in reference.SOURCE_PINS:
            self.assertIn("source:" + path, names)

    def test_09_contract_is_defer_proposal_only(self):
        contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], "proposal_only_not_qualified")
        self.assertEqual(contract["contract_version"], "0.1")
        self.assertEqual(len(contract["release_gates"]), 8)
        self.assertFalse(contract["qualification"]["upstream_parity"])

    def test_10_adapter_and_provider_are_disabled(self):
        adapter = json.loads((HERE / "adapter.json").read_text(encoding="utf-8"))
        provider = json.loads((HERE / "provider.json").read_text(encoding="utf-8"))
        self.assertFalse(adapter["registered"])
        self.assertFalse(adapter["default_enabled"])
        self.assertFalse(adapter["upstream_libsamplerate_used"])
        self.assertFalse(provider["registered"])
        self.assertFalse(provider["enabled_by_default"])
        self.assertTrue(provider["opt_in_required"])
        self.assertFalse(provider["upstream_source_present"])
        self.assertEqual(provider["required_assets"], [])


class ConfigurationTests(unittest.TestCase):
    def test_11_ratio_terms_exact(self):
        for ratio, expected in ((0.5, (1, 2)), (0.75, (3, 4)), (1.0, (1, 1)),
                                (1.25, (5, 4)), (1.5, (3, 2)), (2.0, (2, 1))):
            self.assertEqual(reference.ratio_terms(ratio)[:2], expected)

    def test_12_ratio_bounds_inclusive(self):
        self.assertEqual(reference.ratio_terms(0.25)[2], 0.25)
        self.assertEqual(reference.ratio_terms(4.0)[2], 4.0)

    def test_13_ratio_out_of_bounds_rejected(self):
        for value in (0.24, 4.01, 0.0, -1.0, 100):
            with self.assertRaises(reference.ConfigError):
                reference.ratio_terms(value)

    def test_14_nonfinite_ratio_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(reference.ConfigError):
                reference.ratio_terms(value)

    def test_15_non_numeric_ratio_rejected(self):
        for value in (True, "1.25", None, [1.25]):
            with self.assertRaises(reference.ConfigError):
                reference.ratio_terms(value)

    def test_16_inexact_rational_rejected(self):
        with self.assertRaises(reference.ConfigError):
            reference.ratio_terms(1.3333333333333333)

    def test_17_unknown_config_keys_rejected(self):
        with self.assertRaises(reference.ConfigError):
            reference.validate_config({"half_width": 12, "unexpected": 1})

    def test_18_wrong_grid_rejected(self):
        with self.assertRaises(reference.ConfigError):
            reference.validate_config({"sample_rate_hz": 48000})
        with self.assertRaises(reference.ConfigError):
            reference.validate_config({"frame_samples": 320})

    def test_19_invalid_config_types_rejected(self):
        for value in ({"half_width": 0}, {"half_width": True},
                      {"min_ratio": float("nan")}, {"max_ratio": "2"},
                      {"half_width": 3.5}):
            with self.assertRaises(reference.ConfigError):
                reference.validate_config(value)

    def test_20_expected_length_rounds_half_up(self):
        self.assertEqual(reference.expected_output_samples(12737, 1.25), 15921)
        self.assertEqual(reference.expected_output_samples(3, 0.5), 2)
        self.assertEqual(reference.expected_output_samples(1, 0.5), 1)
        self.assertEqual(reference.expected_output_samples(160, 1.0), 160)


class DurationAndMappingTests(unittest.TestCase):
    def test_21_duration_exact_for_every_ratio(self):
        for length in (1, 5, 160, 12737):
            for ratio in reference.RATES:
                result = reference.resample((0.1,) * length, ratio)
                self.assertEqual(len(result["samples"]),
                                 reference.expected_output_samples(length, ratio),
                                 (length, ratio))
                self.assertTrue(result["samples"])

    def test_22_mapping_starts_at_zero_and_is_monotonic(self):
        result = reference.resample(reference.synthetic_speech(4000), 1.5)
        self.assertEqual(result["mapping"][0], 0)
        self.assertTrue(result["map_monotonic"])
        self.assertTrue(result["source_interval_union_covers_all"])

    def test_23_mapping_partitions_every_source_sample(self):
        for ratio in reference.RATES:
            result = reference.resample(reference.synthetic_speech(2000), ratio)
            mapping = list(result["mapping"]) + [len(reference.synthetic_speech(2000))]
            covered = 0
            for left, right in zip(mapping, mapping[1:]):
                self.assertLessEqual(left, right)
                covered += max(0, right - left)
            self.assertEqual(covered, 2000, ratio)

    def test_24_identity_is_bit_exact(self):
        signal = reference.tonal(512)
        result = reference.resample(signal, 1.0)
        self.assertTrue(result["identity_fast_path"])
        self.assertEqual(result["samples"], signal)
        self.assertEqual(result["edge_exclusion_start"], 0)
        self.assertEqual(result["edge_exclusion_end"], 0)
        self.assertEqual(result["valid_count"], 512)

    def test_25_edge_exclusions_are_declared(self):
        for ratio in (0.5, 1.25, 2.0):
            result = reference.resample(reference.tonal(6400), ratio)
            self.assertGreater(result["edge_exclusion_start"], 0, ratio)
            self.assertGreater(result["edge_exclusion_end"], 0, ratio)
            self.assertEqual(result["valid_count"],
                             len(result["samples"])
                             - result["edge_exclusion_start"]
                             - result["edge_exclusion_end"])

    def test_26_silence_stays_exactly_zero(self):
        for ratio in reference.RATES:
            result = reference.resample(reference.silence(1000), ratio)
            self.assertEqual(scorer.peak_abs(result["samples"]), 0.0, ratio)

    def test_27_short_input_is_finite(self):
        for ratio in reference.RATES:
            result = reference.resample((0.3, -0.2, 0.1), ratio)
            self.assertEqual(result["nonfinite_count"], 0)
            self.assertEqual(len(result["samples"]),
                             reference.expected_output_samples(3, ratio))

    def test_28_source_pitch_preserved_at_output_rate(self):
        signal = reference.tonal(6400)
        for ratio, rate in ((0.5, 8000.0), (1.0, 16000.0), (2.0, 32000.0)):
            result = reference.resample(signal, ratio)
            measured = scorer.dominant_hz(result["samples"], rate)
            self.assertAlmostEqual(measured["dominant_hz"], 220.0, delta=1.0, msg=ratio)

    def test_29_second_call_path_is_byte_identical(self):
        signal = reference.tonal(3200)
        for ratio in reference.RATES:
            case = reference.crosscheck_resample(signal, ratio)
            self.assertTrue(case["byte_identical"], ratio)
            self.assertEqual(case["primary_digest"], case["alternative_digest"])

    def test_30_playback_metrics_are_varispeed(self):
        metrics = reference.playback_metrics(6400, 3200, 0.5)
        self.assertTrue(metrics["render_duration_exact"])
        self.assertEqual(metrics["playback_speed_factor"], 2.0)
        self.assertEqual(metrics["playback_pitch_factor"], 2.0)


class SignalProxyTests(unittest.TestCase):
    def test_31_anti_alias_beats_naive_decimation(self):
        report = reference.build_report()
        alias = report["alias_suppression"]
        self.assertLess(alias["filtered_suppression_db"],
                        alias["naive_suppression_db"] - 20.0)
        self.assertLess(alias["filtered_suppression_db"], -40.0)

    def test_32_image_rejection_beats_naive_interpolation(self):
        report = reference.build_report()
        image = report["image_rejection"]
        self.assertLess(image["filtered_suppression_db"],
                        image["naive_suppression_db"] - 20.0)
        self.assertLess(image["filtered_suppression_db"], -40.0)

    def test_33_transient_timing_within_two_samples(self):
        report = reference.build_report()
        for ratio, case in report["transient_proxies"].items():
            for event in case["events"]:
                self.assertIsNotNone(event["peak_ratio"], ratio)
                self.assertLessEqual(abs(event["timing_error_samples"]), 2, ratio)
                self.assertGreater(event["peak_ratio"], 0.5, ratio)

    def test_34_drift_control_is_nonzero(self):
        control = reference.float_accumulator_drift(reference.drift_signal(), 1.25)
        self.assertGreater(control["max_position_error_samples"], 0.0)
        self.assertEqual(control["reference_position_error_samples"], 0.0)

    def test_35_rebuffer_stall_refill_resume(self):
        produced = [160, 160, 0, 0, 0, 0, 320, 320, 160]
        consumed = [160] * 9
        trace = scorer.rebuffer_trace(produced, consumed, prefill=480, capacity=960)
        self.assertTrue(trace["stall"])
        self.assertTrue(trace["stall_refill_resume_observed"])
        self.assertGreaterEqual(trace["underrun_ticks"], 1)
        self.assertEqual(trace["overflow_ticks"], 0)

    def test_36_fifo_rejects_bad_geometry(self):
        with self.assertRaises(scorer.ScorerError):
            scorer.fifo_occupancy([1], [1], prefill=-1, capacity=4)
        with self.assertRaises(scorer.ScorerError):
            scorer.fifo_occupancy([1], [1], prefill=5, capacity=4)

    def test_37_final_partial_window_is_exact(self):
        report = reference.build_report()
        case = report["final_partial_window"]
        self.assertEqual(case["source_samples"], 12737)
        self.assertEqual(case["output_samples"], 15921)
        self.assertEqual(case["target_samples"], 15921)
        self.assertEqual(case["final_frame_valid_samples"], 81)
        self.assertEqual(case["nonfinite_count"], 0)

    def test_38_envelope_ratio_near_unity(self):
        report = reference.build_report()
        for span in report["speech_preservation"]["envelope_proxy"]["spans"]:
            self.assertIsNotNone(span["ratio"])
            self.assertAlmostEqual(span["ratio"], 1.0, delta=0.05)


class RejectionTests(unittest.TestCase):
    def test_39_nonfinite_samples_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(scorer.ScorerError):
                scorer.validate_vector([0.1, value])

    def test_40_out_of_range_samples_rejected(self):
        with self.assertRaises(scorer.ScorerError):
            scorer.validate_vector([4.5])

    def test_41_wrong_sample_types_rejected(self):
        for value in (True, "0.5", None, [0.5]):
            with self.assertRaises(scorer.ScorerError):
                scorer.validate_vector([value])

    def test_42_empty_vector_rejected(self):
        with self.assertRaises(scorer.ScorerError):
            scorer.validate_vector([])

    def test_43_nonfinite_goertzel_input_rejected(self):
        with self.assertRaises(scorer.ScorerError):
            scorer.goertzel_amplitude([0.1], 100.0, 100.0)

    def test_44_goertzel_rejects_nyquist_bin(self):
        with self.assertRaises(scorer.ScorerError):
            scorer.goertzel_amplitude([0.0] * 64, 8000.0, 16000.0)

    def test_45_digest_rejects_nonfinite(self):
        with self.assertRaises(scorer.ScorerError):
            scorer.tensor_digest([0.0, float("nan")])

    def test_46_duration_rejects_nonfinite_ratio(self):
        with self.assertRaises(ValueError):
            scorer.duration_metrics(10, 10, float("nan"))


class AdapterProtocolTests(unittest.TestCase):
    def test_47_provider_off_is_identity(self):
        result = run.run(run_request({"provider_enabled": False,
                                      "stimulus_id": "tonal_220hz"}))
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["applied_control"], "identity_provider_off")
        metrics = result["metrics"]
        self.assertEqual(metrics["source_digest"], metrics["output_digest"])
        self.assertEqual(metrics["source_samples"], metrics["output_samples"])

    def test_48_provider_on_is_deterministic(self):
        payload = run_request({"provider_enabled": True, "stimulus_id": "speech_like"})
        first = run.run(payload)
        second = run.run(payload)
        self.assertEqual(first["metrics"]["output_digest"],
                         second["metrics"]["output_digest"])
        self.assertEqual(first["metrics"]["output_samples"], 16000)
        self.assertTrue(first["metrics"]["duration"]["exact"])

    def test_49_caller_samples_respected(self):
        payload = run_request({"provider_enabled": True, "stimulus_id": None},
                              samples=[0.0, 0.0, 0.0, 0.0], ratio=2.0)
        result = run.run(payload)
        self.assertEqual(result["stimulus"], "caller_supplied")
        self.assertEqual(result["metrics"]["output_samples"], 8)

    def test_50_missing_stimulus_blocked(self):
        with self.assertRaises(run.RequestError):
            run.run(run_request({"provider_enabled": True, "stimulus_id": None}))

    def test_51_unknown_stimulus_rejected(self):
        with self.assertRaises(run.RequestError):
            run.run(run_request({"provider_enabled": True, "stimulus_id": "not-a-fixture"}))

    def test_52_bad_protocol_version_rejected(self):
        for value in (True, "1", 1.0, 2, None):
            payload = run_request({"provider_enabled": True, "stimulus_id": "silence"})
            payload["protocol_version"] = value
            with self.assertRaises(run.RequestError):
                run.run(payload)

    def test_53_bad_ratio_json_rejected(self):
        for value in (True, "1.25", None, 0.1, 9.0):
            payload = run_request({"provider_enabled": True, "stimulus_id": "silence"},
                                  ratio=value)
            with self.assertRaises((run.RequestError, reference.ConfigError)):
                run.run(payload)

    def test_54_bad_samples_json_rejected(self):
        for value in (True, "0.1", 3, [True], [float("nan")], [5.0]):
            payload = run_request({"provider_enabled": True, "stimulus_id": None},
                                  samples=value)
            with self.assertRaises((run.RequestError, scorer.ScorerError)):
                run.run(payload)

    def test_55_bad_refs_and_attempt_rejected(self):
        payload = run_request({"provider_enabled": True, "stimulus_id": "silence"})
        payload["candidate_ref"] = {"kind": "synthetic", "id": "", "revision": 1}
        with self.assertRaises(run.RequestError):
            run.run(payload)
        payload = run_request({"provider_enabled": True, "stimulus_id": "silence"})
        payload["attempt_id"] = 7
        with self.assertRaises(run.RequestError):
            run.run(payload)

    def test_56_inspect_is_read_only(self):
        payload = run_request({"provider_enabled": False, "stimulus_id": None})
        payload.pop("attempt_id")
        payload.pop("ratio")
        payload.pop("samples")
        payload["operation"] = "inspect"
        result = run.inspect(payload)
        self.assertEqual(result["operation"], "inspect")
        self.assertFalse(result["registered"])
        self.assertFalse(result["upstream_libsamplerate_present"])

    def test_57_file_round_trip_is_canonical(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(json.dumps(
                run_request({"provider_enabled": True, "stimulus_id": "silence"})),
                encoding="utf-8")
            run.process_file(request_path, result_path)
            payload = result_path.read_bytes()
            self.assertTrue(payload.endswith(b"\n"))
            parsed = json.loads(payload)
            self.assertEqual(payload, run.canonical_bytes(parsed) + b"\n")

    def test_58_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            request_path.write_text('{"protocol_version":1,"protocol_version":1}',
                                    encoding="utf-8")
            with self.assertRaises(run.RequestError):
                run.strict_load(request_path)

    def test_59_nonfinite_json_constant_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            request_path.write_text('{"ratio":NaN}', encoding="utf-8")
            with self.assertRaises(run.RequestError):
                run.strict_load(request_path)


class ReportSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.report = reference.build_report()

    def test_60_report_is_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"], "incomplete")
        self.assertFalse(self.report["qualification"]["candidate_qualified"])
        self.assertFalse(self.report["qualification"]["upstream_parity"])

    def test_61_eight_blocked_release_gates(self):
        gates = self.report["gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         ["RG-0" + str(index) for index in range(1, 9)])
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reason"])
            self.assertTrue(gate["reopen"])

    def test_62_every_required_results_is_present(self):
        required = self.report["required_results"]
        self.assertTrue(required)
        self.assertTrue(all(required.values()), required)
        self.assertTrue(self.report["qualification"]["all_required_results_present"])

    def test_63_upstream_blocker_is_exact(self):
        blocker = self.report["upstream_blocker"]
        self.assertEqual(blocker["status"], "blocked_upstream_absent")
        self.assertEqual(blocker["expected_license"], "BSD-2-Clause")
        self.assertIsNone(blocker["pinned_revision"])
        self.assertIsNone(blocker["source_digest"])
        self.assertIn("include/samplerate.h", blocker["required_files"])
        self.assertTrue(blocker["no_upstream_parity_claim"])
        self.assertEqual(len(blocker["not_attempted"]), 3)

    def test_64_board_links_project_identity_only(self):
        rows = self.report["board_links"]
        self.assertIn({"task_id": "SDK-LIBSAMPLERATE", "title": "libsamplerate",
                       "mode": "feasibility"}, rows)
        for row in rows:
            self.assertEqual(set(row), {"task_id", "title", "mode"})
        projected = scorer.sha256_bytes(json.dumps(
            rows, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        self.assertEqual(projected, self.report["board_link_projection_sha256"])
        self.assertTrue(self.report["board_snapshot"]["mutable"])

    def test_65_boundary_invariants_hold(self):
        boundary = self.report["boundary"]
        self.assertTrue(boundary["installed_v0_unchanged"])
        self.assertTrue(boundary["opt_in_required"])
        for key in ("public_api_abi_changed", "registry_changed",
                    "descriptor_registration", "enabled_by_default",
                    "provider_registered", "release_claim", "benchmark_claim"):
            self.assertFalse(boundary[key], key)

    def test_66_adverse_controls_have_no_metrics(self):
        adverse = self.report["adverse"]
        for key in ("nonfinite_input", "out_of_range_input", "missing_result"):
            self.assertIsNone(adverse[key]["metrics"], key)

    def test_67_fixture_digest_matches_generators(self):
        self.assertEqual(self.report["fixture_digest"], reference.fixture_digest())
        self.assertEqual(set(self.report["fixtures"]), set(reference.FIXTURE_GENERATORS))

    def test_68_report_is_byte_reproducible(self):
        first = fixture.canonical_report_bytes(self.report)
        second = fixture.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)


class VerifyTests(unittest.TestCase):
    def test_69_verify_script_passes(self):
        completed = subprocess.run(
            [sys.executable, "verify.py"], cwd=str(HERE),
            capture_output=True, text=True, timeout=600,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"})
        self.assertEqual(completed.returncode, 0,
                         completed.stdout + completed.stderr)
        self.assertIn("reproduction_ok=1", completed.stdout)

    def test_70_math_helpers_agree(self):
        self.assertEqual(scorer.r6(1.23456789), 1.234568)
        values = [0.25, -0.5, 0.0]
        self.assertEqual(scorer.peak_abs(values), 0.5)
        self.assertEqual(scorer.nonfinite_count([0.0, 1.0]), 0)
        self.assertEqual(scorer.finite_count([0.0, 1.0]), 2)
        self.assertTrue(math.isfinite(scorer.rms(values)))


if __name__ == "__main__":
    unittest.main()
