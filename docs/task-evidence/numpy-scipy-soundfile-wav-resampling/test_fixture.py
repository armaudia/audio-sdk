# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the offline WAV/resampling tooling fixture.

Run with the pinned interpreter:

    PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python -m unittest -v test_fixture.py

No skips and no network: the pinned libraries are required to be installed.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import tempfile
import unittest
from pathlib import Path

import numpy as np

import fixture as fx

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
SITE_PACKAGES = Path(os.environ.get(
    "PY312_SITE_PACKAGES",
    "/Users/htsakanyan/.pyenv/versions/3.12.16/lib/python3.12/site-packages"))
REPORT = HERE / "report.json"
MEASUREMENTS = HERE / "runtime-measurements.json"
PINS = HERE / "SOURCES.sha256"
REPORT_SHA = HERE / "report.json.sha256"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
BINARY_SUFFIXES = (".wav", ".flac", ".so", ".dylib", ".dll", ".pyc")


def strict_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"),
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError("nonfinite JSON " + value)))


class PinTests(unittest.TestCase):
    def test_01_source_pins_hash_to_recorded_bytes(self) -> None:
        for pin in fx.SOURCE_PINS:
            with self.subTest(path=pin["path"]):
                root = SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT
                path = root / pin["path"]
                self.assertTrue(path.is_file(), f"missing {path}")
                self.assertEqual(fx.file_digest(path), pin["sha256"])

    def test_02_library_pin_files_hash_to_installed_bytes(self) -> None:
        for pin in fx.LIBRARY_PIN_FILES:
            with self.subTest(path=pin["path"]):
                path = SITE_PACKAGES / pin["path"]
                self.assertTrue(path.is_file(), f"missing {path}")
                self.assertEqual(fx.file_digest(path), pin["sha256"])

    def test_03_artifact_pins_match_code_files(self) -> None:
        for pin in fx.artifact_pins():
            with self.subTest(path=pin["path"]):
                self.assertEqual(fx.file_digest(HERE / pin["path"]),
                                 pin["sha256"])

    def test_04_sha256_manifest_covers_every_pin(self) -> None:
        lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
                 if line and not line.startswith("#")]
        expected = (len(fx.SOURCE_PINS) + len(fx.LIBRARY_PIN_FILES)
                    + len(fx.ALL_ARTIFACTS) - 1)
        self.assertEqual(len(lines), expected)
        for line in lines:
            digest, raw_path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            if raw_path.startswith("source:"):
                path = SOURCE_ROOT / raw_path.split(":", 1)[1]
            elif raw_path.startswith("py312:"):
                path = SITE_PACKAGES / raw_path.split(":", 1)[1]
            else:
                path = SDK_ROOT / raw_path
            self.assertTrue(path.is_file(), f"missing {path}")
            self.assertEqual(fx.file_digest(path), digest)
        for name in fx.ALL_ARTIFACTS:
            if name != "SOURCES.sha256":
                self.assertIn(f"docs/task-evidence/{fx.SLUG}/{name}",
                              PINS.read_text(encoding="utf-8"))

    def test_05_spdx_headers_and_no_trailing_whitespace(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                head = "\n".join(text.splitlines()[:4])
                self.assertIn(SPDX_LICENSE_LINE, head)
                self.assertIn(SPDX_COPYRIGHT_LINE, head)
                self.assertFalse(any(line != line.rstrip()
                                     for line in text.splitlines()))

    def test_06_report_sha256_matches_committed_report(self) -> None:
        self.assertEqual(REPORT_SHA.read_text(encoding="utf-8").strip(),
                         fx.file_digest(REPORT))


class DeterminismTests(unittest.TestCase):
    def test_07_report_is_byte_identical(self) -> None:
        self.assertEqual(fx.canonical_report_bytes(fx.build_report()),
                         REPORT.read_bytes())

    def test_08_signals_are_repeatable_and_frozen(self) -> None:
        first = fx.build_signals()
        second = fx.build_signals()
        self.assertEqual(set(first), {row[0] for row in fx.SIGNAL_SPECS})
        for name in first:
            self.assertEqual(fx.array_digest(first[name]),
                             fx.array_digest(second[name]))
            self.assertEqual(fx.array_digest(first[name]),
                             strict_json(REPORT)["synthetic_runtime"]["signals"][name]["digest"])

    def test_09_fixture_spec_digest_matches(self) -> None:
        report = strict_json(REPORT)
        spec = {
            "contract": fx.CONTRACT_ID,
            "schema": fx.SCHEMA_ID,
            "task_id": fx.TASK_ID,
            "base_commit": fx.BASE_COMMIT,
            "profile": "Tool",
            "sdk_boundary": {"sample_rate_hz": fx.SDK_SAMPLE_RATE_HZ,
                             "channels": fx.SDK_CHANNELS,
                             "sample_format": fx.SDK_SAMPLE_FORMAT,
                             "frame_samples": fx.SDK_FRAME_SAMPLES},
            "base_rate_hz": fx.BASE_RATE_HZ,
            "target_rates_hz": list(fx.TARGET_RATES_HZ),
            "signal_specs": [list(row) for row in fx.SIGNAL_SPECS],
            "library_versions": dict(fx.LIB_VERSIONS),
            "libsndfile_version": fx.LIBSNDFILE_VERSION,
            "source_pins": {pin["path"]: pin["sha256"] for pin in fx.SOURCE_PINS},
            "library_pin_files": {pin["path"]: pin["sha256"]
                                  for pin in fx.LIBRARY_PIN_FILES},
            "artifact_pins": {pin["path"]: pin["sha256"] for pin in fx.artifact_pins()},
        }
        self.assertEqual(fx.object_digest(spec), report["fixture_digest"])

    def test_10_json_is_strict_and_finite(self) -> None:
        report = strict_json(REPORT)
        measurements = strict_json(MEASUREMENTS)
        self.assertEqual(report["base_commit"], fx.BASE_COMMIT)
        self.assertEqual(measurements["base_commit"], fx.BASE_COMMIT)
        self.assertEqual(report["task_id"], fx.TASK_ID)
        self.assertEqual(measurements["task_id"], fx.TASK_ID)


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)
        cls.measurements = strict_json(MEASUREMENTS)

    def test_11_profile_and_status(self) -> None:
        self.assertEqual(self.report["profile"], "Tool")
        self.assertEqual(self.report["candidate_status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_12_sdk_boundary_stays_unchanged(self) -> None:
        boundary = self.report["boundary"]
        self.assertEqual(boundary["sdk_public_boundary"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "f32", "frame_samples": 160})
        self.assertFalse(boundary["registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertEqual(boundary["descriptor_settings"], {})
        self.assertTrue(self.report["scope"]["no_public_api_change"])

    def test_13_tooling_is_outside_sdk_runtime_timing(self) -> None:
        self.assertFalse(self.report["boundary"]["included_in_sdk_runtime_timing"])
        self.assertTrue(self.report["scope"]["no_sdk_runtime_timing"])
        self.assertIn("NEVER included in SDK runtime timing",
                      self.report["scope"]["boundary_statement"])
        self.assertTrue(self.report["flags"]["sdk_runtime_timing_excluded"])

    def test_14_optional_selection_is_pinned(self) -> None:
        probe = fx.probe_optional_selection()
        self.assertEqual(probe["overall_status"], "ok")
        for name, version in fx.LIB_VERSIONS.items():
            self.assertEqual(probe["entries"][name]["version"], version)
            self.assertEqual(importlib.metadata.version(name), version)
        self.assertEqual(probe["python_pin"], fx.PYTHON_VERSION)

    def test_15_missing_optional_selection_never_substitutes(self) -> None:
        for name in ("numpy", "scipy", "soundfile"):
            probe = fx.probe_optional_selection(blocked=(name,))
            self.assertEqual(probe["overall_status"], "missing_optional_selection")
            self.assertFalse(probe["entries"][name]["available"])
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "blocked.wav"
            signal = np.array([[0.1, -0.2]], dtype=np.float32)
            with fx.importer_override(fx.blocking_importer("soundfile")):
                with self.assertRaises(ImportError):
                    fx.write(target, signal, 16000)
            self.assertFalse(target.exists())
        missing = self.report["failure_cases"]["cases"]["missing_optional_selection"]
        self.assertEqual(missing["numpy_probe_status"], "missing_optional_selection")
        self.assertTrue(missing["no_fallback_written"])
        for key in ("numpy_write", "soundfile_read", "soundfile_write",
                    "scipy_resample"):
            self.assertEqual(missing[key]["status"], "rejected")
            self.assertEqual(missing[key]["exception"], "ImportError")

    def test_16_float_wav_roundtrip_is_bit_exact(self) -> None:
        cases = self.report["synthetic_runtime"]["one_typical_use_wav_float_roundtrip"]
        self.assertEqual(set(cases), set(fx.ROUNDTRIP_SIGNALS))
        for case in cases.values():
            self.assertEqual(case["status"], "ok")
            self.assertTrue(case["bit_exact"])
            self.assertEqual(case["input_digest"], case["output_digest"])
            self.assertEqual(case["sample_rate_hz"], 16000)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "rt.wav"
            source = fx.build_signals()["stereo_1600"]
            fx.write(target, source, 16000)
            decoded, rate = fx.read(target, rate=16000, channels=2)
            self.assertTrue(np.array_equal(source, decoded))
            self.assertEqual(rate, 16000)

    def test_17_pcm16_format_edge_is_quantised(self) -> None:
        case = self.report["synthetic_runtime"]["format_edge_pcm16_read"]
        self.assertEqual(case["subtype"], "PCM_16")
        self.assertTrue(case["differs_from_float_roundtrip"])
        self.assertGreater(case["max_abs_quantisation_error"], 0.0)
        self.assertLess(case["max_abs_quantisation_error"], 0.001)

    def test_18_resample_matrix_counts_and_finite(self) -> None:
        cases = self.report["synthetic_runtime"]["resampling"]
        self.assertEqual(len(cases), len(fx.RESAMPLE_SIGNALS)
                         * len(fx.TARGET_RATES_HZ))
        for key, case in cases.items():
            with self.subTest(case=key):
                self.assertTrue(case["count_matches"])
                self.assertTrue(case["finite"])
                self.assertEqual(case["expected_frames"], case["actual_frames"])
                self.assertEqual(len(case["first_values"]),
                                 min(8, case["actual_frames"]))
        self.assertTrue(self.report["flags"]["all_resample_counts_match"])
        self.assertTrue(self.report["flags"]["all_resample_outputs_finite"])

    def test_19_identity_and_downsample_lengths(self) -> None:
        cases = self.report["synthetic_runtime"]["resampling"]
        identity = cases["sine_1k_1600_mono__16000_to_16000"]
        self.assertEqual(identity["up"], 1)
        self.assertEqual(identity["down"], 1)
        self.assertEqual(identity["actual_frames"], 1600)
        source = fx.build_signals()["sine_1k_1600_mono"]
        self.assertTrue(np.array_equal(fx.resample(source, 16000, 16000), source))
        half = cases["sine_1k_1600_mono__16000_to_8000"]
        self.assertEqual(half["actual_frames"], 800)
        third = cases["sine_1k_1600_mono__16000_to_48000"]
        self.assertEqual((third["up"], third["down"], third["actual_frames"]),
                         (3, 1, 4800))
        odd = cases["sine_1k_1600_mono__16000_to_44100"]
        self.assertEqual((odd["up"], odd["down"]), (441, 160))
        self.assertEqual(odd["actual_frames"], 4410)

    def test_20_pcm16_clipping_and_nonfinite(self) -> None:
        pcm = self.report["synthetic_runtime"]["pcm16"]
        self.assertEqual(pcm["clipped_count"], 2)
        self.assertEqual(pcm["values"], [[-32768, -16384], [16384, 32767]])
        self.assertEqual(pcm["nonfinite_rejected"], "rejected")
        self.assertEqual(pcm["write_dtype_f32"], "float32")

    def test_21_prepare_and_chunks(self) -> None:
        case = self.report["synthetic_runtime"]["prepare_and_chunks"]
        self.assertEqual(case["output_rate_hz"], 48000)
        self.assertEqual(case["prepared_frames"], 960)
        self.assertGreater(len(case["output_digest"]), 32)
        self.assertEqual(case["crop_rejected_without_end"], "rejected")
        self.assertTrue(case["chunk_covers_all_samples"])
        self.assertEqual(case["chunk_invalid_schedule"], "rejected")

    def test_22_malformed_wav_inputs_rejected(self) -> None:
        cases = self.report["failure_cases"]["cases"]
        for name in ("git_lfs_pointer", "empty_file", "truncated_riff_header",
                     "non_wav_bytes", "missing_file"):
            self.assertEqual(cases[name]["status"], "rejected", name)
        self.assertEqual(cases["git_lfs_pointer"]["exception"], "ValueError")
        self.assertTrue(self.report["flags"]["malformed_inputs_rejected"])

    def test_23_rate_channel_shape_and_limit_edges(self) -> None:
        cases = self.report["failure_cases"]["cases"]
        for name in ("unexpected_sample_rate", "unexpected_channel_count",
                     "write_nonfinite", "write_1d", "write_rate_zero",
                     "resample_1d", "resample_rate_zero",
                     "sample_interval_invalid", "chunk_invalid"):
            self.assertEqual(cases[name]["status"], "rejected", name)
        self.assertEqual(cases["unexpected_sample_rate"]["exception"], "ValueError")
        self.assertEqual(cases["unexpected_channel_count"]["exception"], "ValueError")
        self.assertTrue(self.report["flags"]["edge_inputs_rejected"])

    def test_24_caller_owned_inputs_are_isolated(self) -> None:
        caller = self.report["failure_cases"]["caller_owned"]
        for key, value in caller.items():
            self.assertTrue(value, key)
        source = fx.build_signals()["sine_1k_1600_mono"].copy()
        before = fx.array_digest(source)
        output = fx.resample(source, 16000, 48000)
        output[0, 0] = -99.0
        self.assertEqual(fx.array_digest(source), before)
        self.assertFalse(np.shares_memory(source, output))

    def test_25_flags_and_counts_are_complete(self) -> None:
        flags = self.report["flags"]
        for name, value in flags.items():
            self.assertTrue(value, name)
        counts = self.report["counts"]
        self.assertEqual(counts["signals"], len(fx.SIGNAL_SPECS))
        self.assertEqual(counts["wav_float_roundtrips"], len(fx.ROUNDTRIP_SIGNALS))
        self.assertEqual(counts["resampling_cases"],
                         len(fx.RESAMPLE_SIGNALS) * len(fx.TARGET_RATES_HZ))
        self.assertEqual(counts["malformed_input_cases"], 5)
        self.assertEqual(counts["source_pins"], len(fx.SOURCE_PINS))
        self.assertEqual(counts["library_pin_files"], len(fx.LIBRARY_PIN_FILES))

    def test_26_blockers_gates_and_evidence_classes(self) -> None:
        blockers = {item["id"]: item for item in self.report["blockers"]}
        self.assertEqual(set(blockers), {"sdk_runtime_timing",
                                         "real_audio_and_quality",
                                         "provider_intake"})
        for item in blockers.values():
            self.assertEqual(item["status"], "blocked")
            self.assertTrue(item["reason"])
            self.assertTrue(item["reopen"])
        gates = {item["id"]: item["status"] for item in self.report["gates"]}
        self.assertEqual(gates["sdk_runtime_timing"], "blocked")
        self.assertEqual(gates["clean_checkout_and_pins"], "pass")
        classes = self.report["evidence_classes"]
        self.assertEqual(classes["real_audio_rights_qualified"], "none")
        self.assertEqual(classes["sdk_runtime_or_device"], "none")

    def test_27_no_missing_result_qualifies_candidate(self) -> None:
        damaged = dict(self.report)
        damaged["flags"] = dict(self.report["flags"])
        damaged["flags"]["all_resample_outputs_finite"] = False
        self.assertEqual(fx.qualification_state(damaged), "not_qualified")
        with self.assertRaises(ValueError):
            fx.qualification_state({
                **damaged, "no_missing_result_qualifies_candidate": False})

    def test_28_build_runtime_and_workload_are_separate(self) -> None:
        build = self.report["compile_build"]
        self.assertEqual(build["status"], "verified_installed_packages")
        self.assertFalse(build["compilation_performed"])
        self.assertEqual(len(build["libraries"]), 3)
        self.assertEqual(len(build["pinned_library_files"]),
                         len(fx.LIBRARY_PIN_FILES))
        self.assertIn("resampling", self.report["synthetic_runtime"])
        self.assertIn("failure_cases", self.report)
        self.assertTrue(self.measurements["non_deterministic"])
        self.assertTrue(self.measurements["unpaced"])

    def test_29_measurements_are_non_qualifying(self) -> None:
        self.assertEqual(self.measurements["qualification_status"], "blocked")
        self.assertIsNone(self.measurements["deadline_ns"])
        self.assertFalse(self.measurements["included_in_sdk_runtime_timing"])
        self.assertGreater(self.measurements["reads"]["repeats"], 0)
        self.assertGreater(self.measurements["resampling"]["repeats"], 0)

    def test_30_no_generated_binaries_in_evidence_dir(self) -> None:
        for path in HERE.iterdir():
            if path.is_file():
                self.assertNotIn(path.suffix.lower(), BINARY_SUFFIXES,
                                 path.name)


if __name__ == "__main__":
    unittest.main()
