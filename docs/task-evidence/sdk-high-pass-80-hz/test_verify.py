"""Unit tests for the installed high-pass control fixture.

Run from the task directory with:
  PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_verify.py

The regeneration test needs AUDIO_SDK_PREFIX and AUDIO_SDK_HARNESS pointing at
the installed package and compiled harness. It is reported as skipped when
those are absent; the committed report/capture are still checked below.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify  # noqa: E402

REPORT_PATH = HERE / "report.json"
CAPTURE_PATH = HERE / "installed-capture.json"

PINNED_DIGESTS = {
    "harness.c": "1ccf81bb7f6542cc00dfd9764029c2030712b0836d0a7410c42c352aac057e8d",
    "stimuli.json": "ce82b8d0241a324ede247441356a1f83e9c270eadf3315916e2b95b636f6d142",
    "verify.py": "b40d4a1e99c55d04b3a880ee4b9870a7603c4c186c3094e03a2985a5187a77ea",
    "report.json": "741babd8aff0e886f10041002213c5556b3a8b11bc69d2028a25c118ffd00d5b",
    "installed-capture.json": "5d4b849cfef3e71c68fb20a010a26fcfbe93251111ef5582e7e3de25dd5d6e90",
}
TASK_PROFILE_DIGEST = "5eea8b61fa70c0e3669ceb878aefc96e9005204f97f1970879583bc710689e80"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.capture = json.loads(CAPTURE_PATH.read_text(encoding="utf-8"))
        cls.stimuli = json.loads((HERE / "stimuli.json").read_text(encoding="utf-8"))

    def test_source_and_fixture_pins(self) -> None:
        for name, expected in PINNED_DIGESTS.items():
            self.assertEqual(sha256(HERE / name), expected, name)
        for label, (path, expected, _summary) in verify.SOURCE_PINS.items():
            self.assertEqual(sha256(path), expected, label)
        self.assertEqual(sha256(verify.TASKS_PATH), TASK_PROFILE_DIGEST)
        self.assertEqual(self.report["task_profile_sha256"], TASK_PROFILE_DIGEST)

    def test_canonical_report_bytes(self) -> None:
        self.assertEqual(REPORT_PATH.read_bytes(), verify.canonical_bytes(self.report))
        self.assertEqual(CAPTURE_PATH.read_bytes(), verify.canonical_bytes(self.capture))
        self.assertEqual(self.report["installed_capture_sha256"], sha256(CAPTURE_PATH))

    def test_fixed_v0_and_scope(self) -> None:
        fixed = self.stimuli["fixed_v0"]
        self.assertEqual(fixed["sample_rate_hz"], 16000)
        self.assertEqual(fixed["channels"], 1)
        self.assertEqual(fixed["frame_samples"], 160)
        self.assertEqual(fixed["cutoff_hz"], 80)
        self.assertEqual(self.report["fixed_v0"], fixed)
        self.assertEqual(self.report["mode"], "reference-verification")
        self.assertEqual(self.report["acceptance_profile"], "DSP")
        self.assertEqual(self.report["base_commit"], verify.BASE_COMMIT)
        self.assertEqual(self.report["branch"], verify.BRANCH)
        self.assertEqual(self.report["provider_id"], "dsp.highpass80.v0")

    def test_all_checks_pass_and_counts_match(self) -> None:
        checks = self.report["checks"]
        failures = [row["id"] for row in checks if row["status"] != "pass"]
        self.assertEqual(failures, [])
        counts = self.report["counts"]
        self.assertEqual(counts["checks"], len(checks))
        self.assertEqual(counts["checks_passed"], len(checks))
        self.assertEqual(counts["checks_failed"], 0)
        self.assertEqual(counts["controls"], 20)
        self.assertEqual(counts["scenarios"], 25)
        self.assertEqual(counts["frames"], 2376)
        self.assertEqual(counts["samples"], 380160)
        self.assertEqual(len(self.capture["scenarios"]), counts["scenarios"])

    def test_installed_conformance_and_build_identity(self) -> None:
        installed = self.report["installed"]
        self.assertEqual(installed["provider_id"], "dsp.highpass80.v0")
        self.assertEqual(installed["conformance_result"], "pass")
        self.assertEqual(installed["conformance_checks"], 40)
        self.assertEqual(installed["conformance_checks_passed"], 40)
        self.assertTrue(installed["build_id"].startswith("audio-sdk/0.1.0+sha256:"))
        self.assertEqual(len(installed["descriptor_digest"]), 64)

    def test_dsp_measurements(self) -> None:
        sweep = self.report["measurements"]["tone_sweep"]
        self.assertEqual(len(sweep), 13)
        self.assertAlmostEqual(sweep["80"]["analytic_gain"], 2 ** -0.5, delta=1e-3)
        self.assertLess(sweep["20"]["measured_gain"], 0.1)
        self.assertGreater(sweep["1000"]["measured_gain"], 0.99)
        impulse = self.report["measurements"]["impulse"]
        self.assertEqual(impulse["measured_content_delay_samples"], 0)
        self.assertAlmostEqual(impulse["first_sample"], impulse["analytic_first_sample"], delta=2e-5)
        self.assertEqual(self.report["measurements"]["steps"]["step_pos"]["settled_mean_abs_last_32"] < 0.02, True)
        self.assertTrue(all(value == 0.0 for value in self.capture["scenarios"]["silence"]["output_samples"]))
        headroom = self.report["measurements"]["headroom"]
        self.assertLess(headroom["steady_state_output_peak"], 1.000001)
        self.assertTrue(math.isfinite(headroom["startup_transient_peak"]))
        self.assertGreater(headroom["startup_transient_peak"], headroom["steady_state_output_peak"])

    def test_speech_and_rumble_controls(self) -> None:
        speech = self.report["measurements"]["speech_proxy"]
        self.assertTrue(speech["not_stoi_or_real_speech"])
        self.assertGreater(speech["envelope_correlation"], 0.95)
        self.assertLess(abs(speech["speech_band_gain_db"] - speech["analytic_band_gain_db"]), 1.0)
        rumble = self.report["measurements"]["rumble_control"]
        self.assertGreater(rumble["rumble_attenuation_db"], 20.0)
        self.assertLess(abs(rumble["speech_band_gain_db"] - speech["analytic_band_gain_db"]), 1.0)

    def test_state_transitions_and_independent_sessions(self) -> None:
        transitions = self.report["measurements"]["state_transitions"]
        self.assertEqual(transitions["final_partial_valid_count"], 37)
        self.assertEqual(transitions["final_partial_source_first"], 320)
        self.assertEqual(transitions["reset_status"], "ok")
        self.assertEqual(transitions["end_of_stream_events"], 2)
        self.assertEqual(transitions["partial_epoch_stats"]["final_padding_samples"], "123")
        self.assertEqual(transitions["post_reset_epoch_stats"]["final_padding_samples"], "0")
        self.assertEqual(transitions["partial_epoch_stats"]["accepted_valid_samples"], "357")
        self.assertEqual(transitions["partial_epoch_stats"]["delivered_valid_samples"], "357")
        self.assertTrue(self.report["measurements"]["independent_sessions"]["bit_identical_to_standalone"])

    def test_invalid_missing_nonfinite_controls(self) -> None:
        rows = self.report["controls"]
        self.assertEqual(len(rows), 20)
        self.assertTrue(all(row["status"] == "pass" for row in rows.values()))
        for name in ("nonfinite_nan", "nonfinite_inf"):
            self.assertTrue(rows[name]["all_output_finite"])
            self.assertEqual(rows[name]["observed"]["status"], "invalid_argument")
        self.assertEqual(rows["process_bad_position"]["observed"]["reset_status"], 6)
        self.assertEqual(rows["recover_after_bad_position"]["observed"]["recovered_status"], 0)
        self.assertAlmostEqual(rows["recover_after_bad_position"]["first_sample_after_reset"],
                               0.25 * verify.design(self.stimuli)[0], delta=2e-5)

    def test_adverse_and_boundary_disclosure(self) -> None:
        adverse = "\n".join(self.report["adverse_cases"])
        for phrase in ("Nonfinite", "not_ready", "no deadline", "not STOI",
                       "Fixed 80 Hz", "No clipping"):
            self.assertIn(phrase, adverse)
        limitations = "\n".join(self.report["limitations"])
        self.assertIn("audio-bench bundle", limitations)
        self.assertIn("public API", limitations)

    def test_analytic_reference(self) -> None:
        coeffs = verify.design(self.stimuli)
        self.assertAlmostEqual(coeffs[0], 0.9780304792065596, delta=1e-12)
        self.assertAlmostEqual(verify.magnitude_response(80, self.stimuli, coeffs), 2 ** -0.5, delta=1e-6)
        self.assertLess(verify.magnitude_response(20, self.stimuli, coeffs), 0.07)
        self.assertGreater(verify.magnitude_response(1000, self.stimuli, coeffs), 0.9999)

    @unittest.skipUnless(os.environ.get("AUDIO_SDK_PREFIX") and os.environ.get("AUDIO_SDK_HARNESS"),
                         "installed SDK prefix and harness not provided")
    def test_regeneration_is_deterministic(self) -> None:
        prefix = pathlib.Path(os.environ["AUDIO_SDK_PREFIX"]).resolve()
        harness = pathlib.Path(os.environ["AUDIO_SDK_HARNESS"]).resolve()
        with tempfile.TemporaryDirectory(prefix="sdk-highpass-test-") as scratch:
            outputs = []
            for index in range(2):
                report_path = pathlib.Path(scratch) / f"report-{index}.json"
                capture_path = pathlib.Path(scratch) / f"capture-{index}.json"
                completed = subprocess.run(
                    [sys.executable, str(HERE / "verify.py"), "--prefix", str(prefix),
                     "--harness", str(harness), "--output", str(report_path),
                     "--capture-output", str(capture_path)],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                outputs.append((report_path.read_bytes(), capture_path.read_bytes()))
            self.assertEqual(outputs[0][0], outputs[1][0])
            self.assertEqual(outputs[0][1], outputs[1][1])
            if verify.design(self.stimuli):
                regenerated = json.loads(outputs[0][0])
                if regenerated["installed"]["build_id"] == self.report["installed"]["build_id"]:
                    self.assertEqual(outputs[0][0], REPORT_PATH.read_bytes())
                    self.assertEqual(outputs[0][1], CAPTURE_PATH.read_bytes())


if __name__ == "__main__":
    unittest.main()
