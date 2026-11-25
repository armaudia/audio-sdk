# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Checks for the opt-in native Bungee Basic reference evidence."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import run_native
import synthetic

HERE = Path(__file__).resolve().parent


class NativeReferenceTests(unittest.TestCase):
    def test_stimulus_is_deterministic_and_finite(self):
        samples = synthetic.stimulus()
        self.assertEqual(len(samples), synthetic.LENGTH)
        self.assertTrue(all(synthetic.local_contrast(samples, marker) > 0.5
                            for marker in synthetic.MARKERS))
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "input.wav"
            synthetic.write_wav(path, samples)
            expected = json.loads((HERE / "native_report.json").read_text())[
                "stimulus"]["sha256"]
            self.assertEqual(synthetic.sha256(path), expected)
            self.assertEqual(synthetic.read_wav(path), samples)

    def test_target_clock_is_exact_across_rate_changes(self):
        schedule = synthetic.RATE_CHANGES
        self.assertEqual(synthetic.target_at(schedule, 4_800), 4_800)
        self.assertEqual(synthetic.target_at(schedule, 9_600), 10_800)
        self.assertEqual(synthetic.target_at(schedule, 12_960), 13_488)
        self.assertEqual(synthetic.target_at(schedule, synthetic.LENGTH), 16_531)
        self.assertEqual(sum(synthetic.chunk_sizes(synthetic.LENGTH)), synthetic.LENGTH)

    def test_transient_probe_uses_native_mapping(self):
        samples = synthetic.stimulus()
        mapping = [{"source": [0, synthetic.LENGTH], "speed": 1.0,
                    "output": [0, synthetic.LENGTH], "native_source_begin": 0.0,
                    "native_source_end": float(synthetic.LENGTH),
                    "latency_input_frames": 0.0}]
        probe = synthetic.impulse_probe(samples, samples, mapping)
        self.assertTrue(probe["all_markers_located"])
        self.assertTrue(all(item["position_error_samples"] == 0
                            for item in probe["marker_positions"]))
        self.assertEqual(probe["audibility"], "not_measured")

    def test_pitch_proxy_separates_native_from_pitch_changing_control(self):
        tone = [synthetic.triangle(index) for index in range(16_000)]
        self.assertEqual(synthetic.pitch_proxy(tone, 2_000, 3_800)["best_lag_samples"], 40)
        control = synthetic.matched_linear_control(tone, ((0, "1.25"),))
        self.assertEqual(synthetic.pitch_proxy(control, 2_000, 3_800)["best_lag_samples"], 32)

    def test_report_has_required_native_invariants(self):
        raw = (HERE / "native_report.json").read_bytes()
        report = json.loads(raw, parse_constant=lambda value: self.fail(value))
        self.assertEqual(run_native.canonical_bytes(report), raw)
        self.assertEqual((HERE / "native_report.json.sha256").read_text().strip(),
                         hashlib.sha256(raw).hexdigest() + "  native_report.json")
        self.assertEqual(report["status"], "native_reference_proven_not_qualified")
        self.assertFalse(report["candidate_qualified"])
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        self.assertEqual(report["base_commit"], "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d")
        self.assertFalse(report["rights"]["vendor_source_or_binary_in_sdk_git"])
        self.assertFalse(report["source"]["vendor_files_modified"])

        cases = report["cases"]
        self.assertEqual(len(cases), 6)
        for case in cases.values():
            native = case["native_bungee"]
            self.assertEqual(native["duration"]["error_frames"], 0)
            self.assertTrue(native["finite_output"]["finite"])
            self.assertTrue(native["impulse_proxy"]["all_markers_located"])
            self.assertTrue(native["source_mapping"]["source_intervals_contiguous"])
            self.assertTrue(native["source_mapping"]["output_intervals_contiguous"])
            self.assertTrue(native["source_mapping"]["native_positions_finite"])
            self.assertEqual(native["pitch_proxy"]["output_over_source"], 1.0)
            self.assertEqual(case["input_sha256"], report["stimulus"]["sha256"])
            self.assertTrue(native["native"]["drain"]["finite"])
        self.assertLess(cases["slower_0p8"]["matched_synthetic_control"]
                        ["pitch_proxy"]["control_over_source"], 1.0)
        self.assertGreater(cases["faster_1p25"]["matched_synthetic_control"]
                           ["pitch_proxy"]["control_over_source"], 1.0)
        self.assertGreater(cases["faster_1p5"]["matched_synthetic_control"]
                           ["pitch_proxy"]["control_over_source"], 1.0)
        self.assertEqual(cases["bounded_zero_tail"]["native_bungee"]
                         ["native"]["drain"]["samples"], 64)
        self.assertTrue(report["granular_flush"]["is_flushed"])
        self.assertTrue(report["granular_flush"]["bounded_by_grains"])
        self.assertTrue(report["granular_flush"]["finite_output"])

    def test_source_pin_check_fails_closed(self):
        with tempfile.TemporaryDirectory() as scratch:
            with self.assertRaises(RuntimeError):
                run_native.check_source(Path(scratch))


if __name__ == "__main__":
    unittest.main()
