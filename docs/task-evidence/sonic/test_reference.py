# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Standard-library acceptance suite for the synthetic Sonic evidence package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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
        "candidate_ref": request_ref("sonic-reference"),
        "adapter_ref": request_ref("sonic-adapter"),
        "configuration": config,
        "attempt_id": "unit-test",
        "rate": 1.25,
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

    def test_07_source_pins_present(self):
        sdk_root = HERE.parents[2]
        source_root = sdk_root.parents[2]
        for path in reference.SOURCE_PINS:
            target = (Path(source_root) / path if path.startswith(("cpp-library", "REALTIME", "audio-benchmark"))
                      else sdk_root / path)
            self.assertTrue(target.is_file(), path)

    def test_08_boundary_pins_match_headers(self):
        sdk_root = HERE.parents[2]
        for path, digest in reference.BOUNDARY_PINS.items():
            self.assertEqual(scorer.sha256_bytes((sdk_root / path).read_bytes()), digest)

    def test_09_artifact_pins_match(self):
        for name, digest in reference.artifact_pins().items():
            self.assertEqual(scorer.sha256_bytes((HERE / name).read_bytes()), digest, name)

    def test_10_sources_manifest_covers_all_files(self):
        lines = [line for line in (HERE / "SOURCES.sha256").read_text().splitlines()
                 if line and not line.startswith("#")]
        self.assertEqual(len(lines), len(reference.SOURCE_PINS)
                         + len(reference.BOUNDARY_PINS)
                         + len(run.SOURCE_ARTIFACT_NAMES) + 1)
        self.assertTrue(all(len(line.split("  ", 1)) == 2 for line in lines))


class ConfigAndFixtureTests(unittest.TestCase):
    def test_11_default_config(self):
        config = reference.validate_config()
        self.assertEqual(config.sample_rate_hz, 16000)
        self.assertEqual(config.frame_samples, 160)

    def test_12_config_rejects_wrong_rate(self):
        with self.assertRaises(reference.ConfigError):
            reference.validate_config({**reference.DEFAULT_CONFIG.__dict__,
                                       "sample_rate_hz": 48000})

    def test_13_config_rejects_nonfinite(self):
        with self.assertRaises(reference.ConfigError):
            reference.validate_config({**reference.DEFAULT_CONFIG.__dict__,
                                       "max_rate": math.inf})

    def test_14_config_rejects_unknown_keys(self):
        with self.assertRaises(reference.ConfigError):
            reference.validate_config({"sample_rate_hz": 16000})

    def test_15_validate_rate_range_and_types(self):
        self.assertEqual(reference.validate_rate(1.25), 1.25)
        for value in (0.0, 2.01, math.nan, True, False, "1.25", None, [1.25]):
            with self.assertRaises(reference.ConfigError):
                reference.validate_rate(value)

    def test_16_fixture_determinism(self):
        first = reference.synthetic_speech()
        second = reference.synthetic_speech()
        self.assertEqual(scorer.tensor_digest(first), scorer.tensor_digest(second))

    def test_17_fixture_variety(self):
        digests = {name: scorer.tensor_digest(generator())
                   for name, generator in reference.fixture_generators().items()}
        self.assertEqual(len(digests), 8)
        self.assertEqual(len(set(digests.values())), 8)

    def test_18_estimate_period_tonal(self):
        period = reference.estimate_period(reference.tonal(), 0)
        self.assertTrue(65 <= period <= 80)

    def test_19_fixture_digest_matches_report(self):
        report = json.loads((HERE / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["fixture_digest"], reference.fixture_digest())


class EngineTests(unittest.TestCase):
    def test_20_duration_exact_at_all_rates(self):
        signal = reference.synthetic_speech()
        for rate in reference.RATES:
            result = reference.stretch(signal, rate)
            self.assertEqual(len(result["samples"]), int(round(len(signal) / rate)))

    def test_21_outputs_finite_and_bounded(self):
        for name in ("speech_like", "music_like", "tonal_220hz", "silence"):
            signal = reference.fixture_generators()[name]()
            for rate in reference.RATES:
                result = reference.stretch(signal, rate)
                self.assertEqual(scorer.nonfinite_count(result["samples"]), 0)
                self.assertLess(scorer.peak_abs(result["samples"]), 1.0)

    def test_22_identity_preserves_frequency_proxy(self):
        signal = reference.tonal()
        metrics = reference.pitch_metrics(signal, reference.stretch(signal, 1.0)["samples"])
        self.assertEqual(metrics["ratio"], 1.0)

    def test_23_identity_speech_rms_close(self):
        signal = reference.synthetic_speech()
        output = reference.stretch(signal, 1.0)["samples"]
        ratio = scorer.rms(output) / scorer.rms(signal)
        self.assertTrue(0.8 < ratio < 1.2, ratio)

    def test_24_silence_stays_zero(self):
        result = reference.stretch(reference.silence(), 1.5)
        self.assertEqual(scorer.peak_abs(result["samples"]), 0.0)

    def test_25_pitch_proxy_preserved_at_rate_changes(self):
        signal = reference.tonal()
        for rate in (0.75, 1.25, 1.5):
            ratio = reference.pitch_metrics(
                signal, reference.stretch(signal, rate)["samples"])["ratio"]
            self.assertTrue(0.95 < ratio < 1.05, (rate, ratio))

    def test_26_varispeed_adverse_control_shifts_pitch(self):
        signal = reference.tonal()
        adverse = reference.varispeed(signal, 1.25)
        ratio = reference.pitch_metrics(signal, adverse["samples"])["ratio"]
        self.assertTrue(1.2 < ratio < 1.3, ratio)

    def test_27_mapping_monotonic_and_in_range(self):
        signal = reference.synthetic_speech()
        result = reference.stretch(signal, 1.25)
        mapping = result["mapping"]
        self.assertTrue(all(left <= right for left, right in zip(mapping, mapping[1:])))
        self.assertLessEqual(max(mapping), len(signal) - 1)

    def test_28_sampled_mapping_shape(self):
        result = reference.stretch(reference.synthetic_speech(), 1.25)
        sampled = reference._sampled_mapping(result["mapping"])
        self.assertEqual(len(sampled), 5)
        self.assertEqual(sampled[0]["source_sample"], 0)

    def test_29_crosscheck_renderers_byte_identical(self):
        signal = reference.tonal()
        for rate in reference.RATES:
            case = reference.crosscheck_stretch(signal, rate)
            self.assertTrue(case["byte_identical"], rate)
            self.assertEqual(case["independent_digest"], case["primary_digest"])

    def test_30_final_partial_window(self):
        signal = reference.partial_signal()
        result = reference.stretch(signal, 1.25)
        self.assertEqual(len(result["samples"]), int(round(len(signal) / 1.25)))
        self.assertNotEqual(len(result["samples"]) % 160, 0)
        self.assertGreater(len(result["samples"]), 0)
        self.assertEqual(scorer.nonfinite_count(result["samples"]), 0)


class ProfileAndAdverseTests(unittest.TestCase):
    def test_31_policy_duration_exact(self):
        result = reference.profile_stretch(reference.synthetic_speech(),
                                           reference.SPEECH_POLICY_ANCHORS)
        self.assertEqual(len(result["samples"]), 12800)
        self.assertEqual(len(result["samples"]), result["expected_output_samples"])

    def test_32_policy_anchors_are_source_timestamps(self):
        result = reference.profile_stretch(reference.synthetic_speech(),
                                           reference.SPEECH_POLICY_ANCHORS)
        self.assertEqual(result["anchors"], list(reference.SPEECH_POLICY_ANCHORS))
        self.assertEqual(result["boundaries"], [2400, 3200, 5600, 6400, 8800, 9600, 12000])
        self.assertTrue(all(rate in (0.9, 1.5) for rate in result["block_rates"]))

    def test_33_speech_envelope_proxy_measured(self):
        signal = reference.synthetic_speech()
        result = reference.profile_stretch(signal, reference.SPEECH_POLICY_ANCHORS)
        spans = [(start, end) for start, end, label in reference.SPEECH_SPANS
                 if label == "voiced"]
        metrics = scorer.envelope_proxy(signal, result["samples"], result["mapping"], spans)
        self.assertEqual(len(metrics["spans"]), 4)
        self.assertTrue(all(row["mapped_output_samples"] > 0 for row in metrics["spans"]))

    def test_34_dynamic_buffer_no_underrun(self):
        result = reference.profile_stretch(reference.synthetic_speech(),
                                           reference.DYNAMIC_ANCHORS)
        self.assertEqual(result["final_output_samples"], result["expected_output_samples"])
        self.assertEqual(result["buffer"]["underrun_blocks"], 0)

    def test_35_drift_duration_exact(self):
        result = reference.profile_stretch(reference.drift_signal(),
                                           reference.DRIFT_ANCHORS)
        self.assertEqual(result["final_output_samples"], 9600)
        self.assertEqual(result["final_output_samples"], result["expected_output_samples"])

    def test_36_rebuffer_stalls_refills_resumes_and_drains(self):
        report = run.strict_load(HERE / "report.json")
        result = report["drift_and_rebuffer"]["rebuffer"]
        self.assertEqual(result["output_samples"], 9600)
        self.assertTrue(result["duration_exact"])
        fifo = result["synthetic_fifo"]
        self.assertTrue(fifo["stall_refill_resume_observed"])
        self.assertEqual(fifo["refill_threshold_samples"], 320)
        ticks = fifo["ticks"]
        events = [row["event"] for row in ticks]
        self.assertEqual(events[:6],
                         ["play", "play", "stall", "waiting", "refill", "resume"])
        self.assertLess(events.index("stall"), events.index("refill"))
        self.assertLess(events.index("refill"), events.index("resume"))
        self.assertEqual([row["arrived_samples"] for row in ticks[:6]],
                         [0, 0, 0, 0, 160, 160])
        self.assertEqual([row["played_samples"] for row in ticks[:6]],
                         [160, 160, 0, 0, 0, 160])
        queued = fifo["prefill_samples"]
        for row in ticks:
            queued += row["arrived_samples"] - row["played_samples"]
            self.assertGreaterEqual(queued, 0)
            self.assertEqual(row["queued_samples"], queued)
        self.assertEqual(queued, 0)
        self.assertEqual(sum(row["played_samples"] for row in ticks), result["output_samples"])
        self.assertEqual(fifo["played_samples"], result["output_samples"])

    def test_37_transient_proxy_uses_renderer_source_to_output_map(self):
        signal = reference.transient_train()
        result = reference.stretch(signal, 1.25)
        mapping = result["mapping"]
        metrics = scorer.transient_proxy(signal, result["samples"], 1.25,
                                         reference.TRANSIENT_POSITIONS, mapping)
        self.assertEqual(len(metrics["events"]), 4)
        self.assertIsNotNone(metrics["median_peak_retention"])
        for event in metrics["events"]:
            source = event["source_sample"]
            expected = event["expected_output_sample"]
            self.assertTrue(mapping[expected - 1] < source)
            self.assertGreaterEqual(mapping[expected], source)
            self.assertEqual(event["mapped_source_sample"], mapping[expected])
            self.assertLessEqual(abs(event["timing_error_samples"]), 48)
        self.assertTrue(any(event["expected_output_sample"]
                            != event["caller_clock_estimate"]
                            for event in metrics["events"]))
        report = run.strict_load(HERE / "report.json")
        self.assertEqual(report["transient_proxies"]["1.25"], metrics)

    def test_38_boundary_comparison_uses_each_renders_output_positions(self):
        report = run.strict_load(HERE / "report.json")
        profile = report["dynamic_profile"]
        signal = reference.synthetic_speech()
        for smooth, key, map_key, expected in (
            (False, "boundary_jump_unsmoothed",
             "rate_step_source_to_output", [4800, 7360, 10560]),
            (True, "boundary_jump_smoothed_control",
             "smoothed_rate_step_source_to_output", [4800, 7843, 10900]),
        ):
            rendered = reference.profile_stretch(signal, reference.DYNAMIC_ANCHORS, smooth=smooth)
            block_starts = {row["source_start"]: row["output_start"] for row in rendered["blocks"]}
            source_anchors = [pos for pos, _rate in reference.DYNAMIC_ANCHORS[1:]]
            self.assertEqual([block_starts[pos] for pos in source_anchors], expected)
            self.assertEqual([row["source_sample"] for row in profile[map_key]],
                             source_anchors)
            self.assertEqual([row["output_sample"] for row in profile[map_key]],
                             expected)
            self.assertEqual(profile[key], scorer.boundary_jump_ratio(rendered["samples"], expected))
        comparison = next(entry for entry in report["regressions"]
                          if entry["entry_id"] == "rate_step_boundary_comparison")
        self.assertEqual(comparison["observed"], {"abrupt": 5.312563, "smoothed": 6.061116})
        self.assertTrue(comparison["excluded_from_qualification"])

    def test_39_nonfinite_input_rejected(self):
        with self.assertRaises(scorer.ScorerError):
            reference.stretch((0.0, math.nan), 1.0)

    def test_40_out_of_range_input_rejected(self):
        with self.assertRaises(scorer.ScorerError):
            reference.stretch((0.0, 9.0), 1.0)

    def test_41_missing_fixture_blocked(self):
        payload = run_request({"provider_enabled": True, "stimulus_id": "not-a-fixture"})
        with self.assertRaises(run.RequestError):
            run.run(payload)

    def test_42_adapter_off_is_identity(self):
        payload = run_request({"provider_enabled": False, "stimulus_id": "tonal_220hz"})
        result = run.run(payload)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["applied_control"], "identity_provider_off")
        self.assertEqual(result["metrics"]["source_digest"],
                         result["metrics"]["output_digest"])

    def test_43_adapter_on_runs_synthetic_reference(self):
        payload = run_request({"provider_enabled": True, "stimulus_id": "tonal_220hz"},
                              rate=1.25)
        result = run.run(payload)
        self.assertEqual(result["status"], "complete")
        self.assertTrue(result["metrics"]["duration"]["exact"])
        self.assertIn("synthetic", result["disclosure"])

    def test_44_report_status_and_gates(self):
        report = json.loads((HERE / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["qualification"]["decision"], "DEFER")
        self.assertEqual(report["qualification"]["readiness"], "incomplete")
        self.assertTrue(all(report["qualification"]["required_results"].values()))
        self.assertTrue(all(gate["status"] == "blocked" for gate in report["gates"]))

    def test_45_manifests_are_opt_in_and_unregistered(self):
        adapter = json.loads((HERE / "adapter.json").read_text(encoding="utf-8"))
        provider = json.loads((HERE / "provider.json").read_text(encoding="utf-8"))
        self.assertFalse(adapter["registered"])
        self.assertFalse(adapter["default_enabled"])
        self.assertFalse(provider["registered"])
        self.assertFalse(provider["enabled_by_default"])
        self.assertTrue(provider["opt_in_required"])

    def test_46_readme_discloses_scope(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        for phrase in ("proposal_only_not_qualified", "DEFER", "synthetic",
                       "no listening", "16 kHz", "160-sample"):
            self.assertIn(phrase, text.lower() if phrase.islower() else text)

    def test_47_three_cold_starts_byte_identical(self):
        probe = fixture.repeat_probe()
        self.assertEqual(probe["runs"], 3)
        self.assertTrue(probe["byte_identical"])

    def test_48_cli_rejects_non_numeric_fields_without_writing_result(self):
        with tempfile.TemporaryDirectory() as temp:
            request = Path(temp) / "request.json"
            result = Path(temp) / "result.json"
            command = [sys.executable, str(HERE / "run.py"),
                       "--request", str(request), "--result", str(result)]
            for provider_enabled in (False, True):
                base = run_request({"provider_enabled": provider_enabled, "stimulus_id": None},
                                   rate=1, samples=[0, 0.25])
                invalid = [
                    ("protocol_version", (True, "1", 1.0, 2),
                     "invalid_protocol_or_operation"),
                    ("rate", (True, "1.25", None), "rate_wrong_type"),
                    ("rate", (10**400,), "rate_out_of_range"),
                    ("samples", ([True], ["0.25"], [None]),
                     "invalid_samples_type"),
                    ("samples", ([10**400],), "out_of_range_samples"),
                    ("candidate_ref", (
                        {**request_ref("sonic-reference"), "revision": True},
                        {**request_ref("sonic-reference"), "revision": "1"},
                        {**request_ref("sonic-reference"), "revision": 1.0},
                        {**request_ref("sonic-reference"), "revision": 0},
                    ), "invalid_candidate_ref"),
                    ("configuration", (
                        {**base["configuration"], "provider_enabled": "true"},
                        {**base["configuration"], "provider_enabled": 1},
                    ), "invalid_provider_switch"),
                    ("configuration", (
                        {**base["configuration"], "stimulus_id": 1},
                        {**base["configuration"], "stimulus_id": True},
                    ), "unknown_stimulus"),
                    ("attempt_id", (1, True), "invalid_attempt_id"),
                ]
                for field, values, error in invalid:
                    for value in values:
                        with self.subTest(enabled=provider_enabled, field=field, value=value):
                            request.write_text(json.dumps({**base, field: value}), encoding="utf-8")
                            completed = subprocess.run(command, capture_output=True, text=True)
                            self.assertEqual(completed.returncode, 2, completed.stderr)
                            self.assertEqual(completed.stderr.strip(), error)
                            self.assertFalse(result.exists())
                request.write_text(json.dumps(base), encoding="utf-8")
                subprocess.run(command, check=True)
                self.assertEqual(run.strict_load(result)["status"], "complete")
                result.unlink()
            inspect = {key: base[key] for key in run.COMMON_FIELDS}
            inspect.update(operation="inspect", protocol_version=True)
            request.write_text(json.dumps(inspect), encoding="utf-8")
            completed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stderr.strip(), "invalid_protocol_or_operation")
            self.assertFalse(result.exists())

    def test_49_scorer_rejects_non_numeric_samples_and_nonmonotonic_map(self):
        for value in (True, False, "0.25", None, [0.25]):
            with self.subTest(value=value):
                with self.assertRaises(scorer.ScorerError):
                    scorer.validate_vector([0.0, value])
        with self.assertRaises(scorer.ScorerError):
            scorer.transient_proxy((0.0, 1.0), (0.0, 1.0), 1.0, (0,), (1, 0))
        report = run.strict_load(HERE / "report.json")
        adverse = report["adverse"]["invalid_json_numeric_fields"]
        self.assertEqual(adverse["status"], "rejected_closed")
        self.assertTrue(adverse["cases"])


if __name__ == "__main__":
    unittest.main()
