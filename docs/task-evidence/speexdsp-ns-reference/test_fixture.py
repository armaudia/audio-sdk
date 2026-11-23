# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the installed speex.ns.v0 reference fixture."""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import unittest
from pathlib import Path

import fixture as fx

HERE = Path(__file__).resolve().parent
CONFORMANCE = HERE / "conformance-report.json"
REPORT = HERE / "report.json"
MEASUREMENTS = HERE / "runtime-measurements.json"
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))


@unittest.skipUnless(os.environ.get("AUDIO_SDK_LIBRARY") and os.environ.get("AUDIO_SDK_EXPECTED_BUILD_ID"),
                     "installed SDK environment is not configured")
class InstalledReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binding = fx.load_binding()
        cls.report, cls.measurements = fx.collect(cls.binding, CONFORMANCE)
        cls.stored = json.loads(REPORT.read_text())
        cls.stored_measurements = json.loads(MEASUREMENTS.read_text())

    def test_01_stimuli_are_deterministic(self) -> None:
        a = fx.clean_speech(3200) + fx.noise(3200)
        b = fx.clean_speech(3200) + fx.noise(3200)
        self.assertEqual(a, b)
        self.assertEqual(hashlib.sha256(repr(a).encode()).hexdigest(),
                         hashlib.sha256(repr(b).encode()).hexdigest())

    def test_02_si_sdr_analytic_and_invalid(self) -> None:
        ref = [0.0, 1.0, 0.0, -1.0]
        self.assertEqual(fx.si_sdr_db(ref, ref)[1], "exact_reconstruction")
        self.assertEqual(fx.si_sdr_db(ref, [0.5 * v for v in ref])[1],
                         "exact_reconstruction")
        # Zero-mean fit: target energy 2, residual energy 3/4.
        value, reason = fx.si_sdr_db([1.0, 0.0, -1.0, 0.0], [1.0, 1.0, -1.0, 0.0])
        self.assertIsNone(reason)
        self.assertAlmostEqual(value, round(10 * math.log10(8.0 / 3.0), 6))
        self.assertEqual(fx.si_sdr_db(None, ref), (None, "missing_reference_or_output"))
        self.assertEqual(fx.si_sdr_db(ref, ref[:-1]), (None, "length_mismatch"))
        self.assertEqual(fx.si_sdr_db([0.0] * 4, ref), (None, "zero_reference"))

    def test_03_alignment_is_measured_not_declared(self) -> None:
        self.assertEqual(self.report["alignment"]["declared_buffering_samples"], 160)
        self.assertEqual(self.report["alignment"]["declared_first_source_sample"], -160)
        self.assertEqual(self.report["alignment"]["measured_impulse_index"], 4000)
        self.assertEqual(self.report["alignment"]["measured_content_lag_samples"], 0)
        self.assertEqual(self.report["alignment"]["valid_output_samples"], 32000)

    def test_04_conformance_baseline_is_green(self) -> None:
        self.assertEqual(self.report["conformance"]["result"], "pass")
        self.assertEqual(self.report["conformance"]["pass"], 40)
        self.assertEqual(self.report["conformance"]["fail"], 0)
        self.assertEqual(self.report["conformance"]["skip"], 0)
        self.assertTrue(self.report["all_conformance_pass"])

    def test_05_invalid_missing_nonfinite_controls(self) -> None:
        controls = self.report["controls"]
        self.assertEqual(set(c["status"] for c in controls.values()), {"pass"})
        self.assertTrue(controls["nonfinite_input_rejected"]["state_unchanged_after_rejection"])
        self.assertEqual(controls["missing_reference"]["reason"], "missing_reference_or_output")
        self.assertEqual(controls["truncated_output"]["reason"], "length_mismatch")
        self.assertEqual(controls["invalid_config_conformance"]["count"], 10)

    def test_06_state_and_finite_outputs(self) -> None:
        self.assertTrue(self.report["all_state_pass"])
        for value in self.report["state"].values():
            self.assertTrue(value)
        self.assertTrue(self.report["all_outputs_finite"])
        for item in self.report["conditions"].values():
            self.assertTrue(item["output"]["finite"])
            self.assertLessEqual(item["output"]["peak_abs"], 1.0)

    def test_07_paired_metrics_and_preservation(self) -> None:
        conditions = self.report["conditions"]
        noisy = conditions["noisy_snr10"]
        self.assertGreater(noisy["si_sdr_db"]["paired_delta"], 0.0)
        self.assertIsNotNone(noisy["stoi"]["provider"])
        self.assertIsInstance(noisy["stoi"]["paired_delta"], float)
        self.assertLess(conditions["clean_only"]["stoi"]["paired_delta"], 0.0)
        self.assertLess(conditions["clean_only"]["preservation"]["rms_gain_ratio"], 1.0)
        self.assertEqual(conditions["silence"]["si_sdr_db"]["provider"], None)
        self.assertEqual(conditions["clean_only"]["si_sdr_db"]["invalid_reasons"],
                         ["exact_reconstruction"])

    def test_08_report_is_canonical_and_reproducible(self) -> None:
        self.assertEqual(fx.canonical_bytes(self.report), REPORT.read_bytes())
        self.assertEqual(self.measurements["schema_id"], self.stored_measurements["schema_id"])
        self.assertEqual(self.measurements["installed_identity"],
                         self.stored_measurements["installed_identity"])
        self.assertEqual(self.stored["schema_id"], fx.SCHEMA)
        self.assertEqual(self.stored["installed_identity"]["base_commit"], fx.BASE_COMMIT)
        self.assertEqual(len(self.stored["source_pins"]), 7)
        self.assertEqual(self.stored["conformance"]["report_sha256"],
                         hashlib.sha256(CONFORMANCE.read_bytes()).hexdigest())
        self.assertEqual(self.report["controls"], self.stored["controls"])
        self.assertEqual(self.report["conditions"], self.stored["conditions"])

    def test_09_source_pins_match_files(self) -> None:
        sdk_copy = SOURCE_ROOT / "audio-benchmark-platform/audio-sdk/core/providers/speex/speex_provider.c"
        if sdk_copy.is_file():
            dig = hashlib.sha256(sdk_copy.read_bytes()).hexdigest()
            pinned = next(p["sha256"] for p in self.report["source_pins"]
                          if p["path"].endswith("core/providers/speex/speex_provider.c"))
            self.assertEqual(dig, pinned)
        for pin in self.report["source_pins"]:
            path = SOURCE_ROOT / pin["path"]
            if not path.is_file():
                self.skipTest(f"source pin not available locally: {path}")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin["sha256"])

    def test_10_stoi_scorer_is_pinned_or_explicitly_skipped(self) -> None:
        reasons = [r for c in self.report["conditions"].values()
                   for r in c["stoi"]["invalid_reasons"]]
        self.assertEqual(set(reasons), set())
        self.assertEqual(self.measurements["platform"]["pystoi"], "0.4.1")
        self.assertEqual(self.measurements["platform"]["numpy"], "2.5.4")
        self.assertIsNone(fx.stoi_score([0.0] * 1600, [0.0] * 1600)[0])
        self.assertEqual(fx.stoi_score(None, [0.0] * 1600), (None, "missing_reference_or_output"))

    def test_11_measurement_envelope_is_explicit(self) -> None:
        self.assertTrue(self.measurements["non_deterministic"])
        self.assertIsNone(self.measurements["deadline_ns"])
        self.assertEqual(self.measurements["pacing"], "unpaced")
        self.assertEqual(len(self.measurements["per_condition"]), 5)
        for item in self.measurements["per_condition"].values():
            self.assertGreaterEqual(item["first_valid_output_s"], 0.0)
            self.assertGreater(item["process_duration_ms"]["max"], 0.0)
            self.assertIsInstance(item["maxrss_delta_bytes"], int)


if __name__ == "__main__":
    unittest.main(verbosity=2)
