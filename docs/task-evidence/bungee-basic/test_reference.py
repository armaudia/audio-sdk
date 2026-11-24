# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Behavior and reproducibility checks for the rate reference."""

import hashlib
import subprocess
import sys
import unittest
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

import reference as ref

HERE = Path(__file__).resolve().parent


class RateTests(unittest.TestCase):
    def test_identity_preserves_content_and_partial_tail(self):
        samples = [1.0, -1.0, 0.0] * 54
        spans, exact = ref.rate_map(len(samples), [(0, "1")])
        self.assertEqual(ref.linear_control(samples, spans), samples)
        self.assertEqual(exact, len(samples))
        self.assertEqual(ref.observe(samples, [(0, "1")])["final_partial_source_samples"], 2)

    def test_duration_and_mapping_do_not_accumulate_rounding_drift(self):
        schedule = [(160 * i, "1.5") for i in range(100)]
        spans, exact = ref.rate_map(16_003, schedule)
        self.assertEqual(exact, Fraction(32_006, 3))
        for previous, following in pairwise(spans):
            self.assertEqual(previous["source"][1], following["source"][0])
            self.assertEqual(previous["output"][1], following["output"][0])
        self.assertEqual(spans[-1]["source"][1], 16_003)
        self.assertEqual(spans[-1]["output"][1], round(exact))
        self.assertNotEqual(round(exact), 99 * round(Fraction(320, 3))
                            + round(Fraction(326, 3)))

    def test_reject_invalid_rate_changes(self):
        for schedule in ([], [(160, "1")], [(0, "0")], [(0, "1"), (1, "2.5")],
                         [(0, "1"), (0, "1")], [(0, "1"), (320, "1")]):
            with self.subTest(schedule=schedule), self.assertRaises(ValueError):
                ref.rate_map(320, schedule)

    def test_reject_nonfinite(self):
        spans, _ = ref.rate_map(1, [(0, "1")])
        with self.assertRaises(ValueError):
            ref.linear_control([float("nan")], spans)

    def test_controls_disclose_pitch_change_and_unmeasured_audibility(self):
        report = ref.build_report()
        cases = report["controls"]["linear_pitch_changing"]
        self.assertTrue(cases["1"]["identity"])
        self.assertLess(cases["0.5"]["output_pitch_proxy_hz"], 400)
        self.assertGreater(cases["2.5"]["output_pitch_proxy_hz"], 400)
        self.assertEqual(len(report["regressions"]), 5)
        self.assertEqual(report["controls"]["silence"]["peak_abs"], 0)
        impulse = report["controls"]["impulse"]["impulse"]
        self.assertEqual(impulse["output_peak_sample"], 320)
        self.assertEqual(impulse["audibility"], "not_measured")
        self.assertEqual(report["controls"]["buffer_simulation"]["rebuffer_samples"], 160)
        self.assertFalse(report["native_bungee"]["invoked"])

    def test_three_cold_starts_match_report_and_sidecar(self):
        expected = (HERE / "report.json").read_bytes()
        command = [sys.executable, "-B", "-c",
                   "import sys, reference as r; "
                   "sys.stdout.buffer.write(r.canonical_report_bytes(r.build_report()))"]
        for _ in range(3):
            self.assertEqual(subprocess.check_output(command, cwd=HERE), expected)
        self.assertEqual((HERE / "report.json.sha256").read_text(),
                         hashlib.sha256(expected).hexdigest() + "  report.json\n")
