#!/usr/bin/env python3
"""Unittest suite for the task-local Block-NLMS AFC DSP reference."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import afc_reference as afc

TASK = Path(__file__).resolve().parents[1]
WORKSPACE = TASK.parents[5]
REPORT = TASK / "evidence" / "report.json"
REQUIRED = (
    "echo_return_loss", "convergence", "tracking", "double_talk",
    "reference_latency", "frequency_sweep", "chirp_sweep", "impulse",
    "silence", "step", "clean_speech", "gain_before_feedback",
    "adverse_loop", "headroom_and_nonlinearity", "numerical_behaviour",
    "state_transitions", "load_proxy",
)


def check_no_missing(value: object, path: str = "report") -> None:
    if value is None:
        raise AssertionError("missing result: %s" % path)
    if isinstance(value, float):
        assert value == value and abs(value) != float("inf"), path
    elif isinstance(value, dict):
        for key, item in value.items():
            check_no_missing(item, "%s.%s" % (path, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_no_missing(item, "%s[%d]" % (path, index))


class BlockNlmsAfcTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.results = cls.report["results"]

    def test_fixtures_are_byte_identical(self) -> None:
        subprocess.run(["python3", str(TASK / "tools" / "generate_fixtures.py"),
                        "--check"], check=True, capture_output=True)

    def test_report_regeneration_is_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            subprocess.run([
                "python3", str(TASK / "tools" / "evaluate.py"),
                "--fixtures", str(TASK / "fixtures"),
                "--sources-sha", str(TASK / "SOURCES.sha256"),
                "--fixture-manifest", str(TASK / "fixtures" / "FIXTURES.sha256"),
                "--output", str(output),
            ], check=True, capture_output=True)
            self.assertEqual(REPORT.read_bytes(), output.read_bytes())

    def test_all_sections_present_with_no_missing_results(self) -> None:
        for name in REQUIRED:
            self.assertIn(name, self.results)
        check_no_missing(self.report)
        for gate in self.report["gates"].values():
            self.assertTrue(gate["evidence_present"])
            self.assertIn(gate["result"], ("passed", "not_performed"))

    def test_external_source_pins_match(self) -> None:
        for name, expected in afc.SOURCE_PINS.items():
            actual = hashlib.sha256((WORKSPACE / name).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, name)

    def test_reference_is_required_and_fail_closed(self) -> None:
        status, controller = afc.AfcController.create(afc.config_with(), None)
        self.assertEqual(status, afc.Status.REJECTED_MISSING)
        self.assertIsNone(controller)
        status, _ = afc.AfcController.create(
            afc.config_with(), (float("nan"),) * afc.ASSET_PREFIX)
        self.assertEqual(status, afc.Status.REJECTED_NONFINITE)
        self.assertEqual(self.results["numerical_behaviour"]["create_statuses"][
            "missing_reference"], "rejected_missing")

    def test_zero_buffering_and_waveform_controls(self) -> None:
        self.assertEqual(self.results["impulse"]["added_delay_samples"], 0)
        self.assertEqual(self.results["step"]["added_delay_samples"], 0)
        self.assertEqual(self.results["silence"]["peak_abs_output"], 0.0)
        self.assertEqual(self.results["load_proxy"]["buffering_delay_samples"], 0)

    def test_block_nlms_adaptation_and_tracking(self) -> None:
        erle = self.results["echo_return_loss"]
        self.assertGreater(erle["erle_db_steady_frames_80_159"],
                           erle["erle_db_early_frames_0_19"])
        self.assertGreater(erle["erle_db_steady_frames_80_159"], 3.0)
        self.assertIsInstance(
            self.results["convergence"]["frames_to_6db_trailing_mean"], int)
        self.assertIsInstance(
            self.results["tracking"]["frames_to_recover_within_3db"], int)

    def test_latency_and_double_talk_evidence(self) -> None:
        latency = self.results["reference_latency"]
        self.assertEqual(latency["best_causal_lag_samples"], 0)
        self.assertEqual(len(latency["causal_closed_loop_lag_sweep"]), 4)
        self.assertEqual(len(latency["offline_adaptation_lag_sweep"]), 5)
        self.assertGreater(len(latency["offline_adaptation_leading_reference_sweep"]), 0)
        self.assertFalse(latency["leading_reference_is_causal"])
        self.assertGreater(self.results["double_talk"]["double_talk_frames"], 0)

    def test_gain_before_feedback_is_separate_from_erle(self) -> None:
        gain = self.results["gain_before_feedback"]
        self.assertEqual(gain["status"], "ok")
        self.assertGreater(gain["max_stable_loop_gain"]["identity"], 0.0)
        self.assertGreaterEqual(gain["max_stable_loop_gain"]["afc_margin"],
                                gain["max_stable_loop_gain"]["identity"])
        self.assertEqual(gain["measurement_class"],
                         "attenuation_and_stability_not_adaptation_quality")
        self.assertIn("reference_adaptation_sections",
                      self.report["measurement_separation"])


if __name__ == "__main__":
    unittest.main()
