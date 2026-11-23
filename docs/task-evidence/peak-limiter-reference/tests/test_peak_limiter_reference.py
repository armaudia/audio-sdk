"""Deterministic checks for the opt-in peak-limiter reference evidence."""

import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import report  # noqa: E402
import run  # noqa: E402

REPORT_PATH = HERE / "fixtures/report.json"
AUDIOML_ROOT = Path(os.environ.get("AUDIOML_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))


class PeakLimiterReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report_bytes = REPORT_PATH.read_bytes()
        cls.document = json.loads(cls.report_bytes)
        cls.regenerated = json.dumps(report.build_report(), sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode("ascii") + b"\n"

    def test_report_is_canonical_and_repeatable(self):
        self.assertEqual(self.report_bytes, self.regenerated)
        self.assertTrue(self.report_bytes.endswith(b"\n"))
        self.assertEqual(self.document["protocol"], "sdk.peak-limiter-reference.dsp.v1")
        self.assertEqual(self.document["evidence_kind"], "synthetic_developer_only")

    def test_source_pins(self):
        pins = self.document["adapter"]["source_pins"]
        self.assertEqual(len(pins), 5)
        self.assertTrue(self.document["task_board"]["mutable"])
        missing = []
        for relative, digest in pins.items():
            path = AUDIOML_ROOT / relative
            if not path.is_file():
                missing.append(relative)
                continue
            self.assertEqual(report.sha256_path(path), digest, relative)
        self.assertEqual(missing, [], "required pinned source files are missing")

    def test_fixture_and_adapter_digests(self):
        self.assertEqual(self.document["fixture_sha256"], report.sha256_path(report.FIXTURE_PATH))
        self.assertEqual(self.document["adapter"]["descriptor_sha256"],
                         report.sha256_path(report.ADAPTER_PATH))

    def test_geometry(self):
        geometry = self.document["geometry"]
        self.assertEqual(geometry, {"sample_rate_hz": 16000, "frame_samples": 160,
                                    "sample_format": "f32", "channels": 1})
        self.assertAlmostEqual(self.document["release_coefficient"],
                               1.0 - math.exp(-1000.0 / (50.0 * 16000.0)), places=15)

    def test_peak_protection(self):
        cases = self.document["cases"]
        for name in ("sweep", "steps", "impulse", "clean_speech_like"):
            case = cases[name]
            self.assertLessEqual(case["peak_out"], 0.98 + 2e-8, name)
            self.assertIsNotNone(case["first_modified_sample"], name)
        self.assertGreater(cases["sweep"]["peak_in"], 1.5)
        self.assertAlmostEqual(cases["sweep_ceiling_0_5"]["peak_out"], 0.5, places=6)
        self.assertEqual(cases["silence"]["peak_out"], 0.0)

    def test_headroom_explains_float32_rounding(self):
        headroom = self.document["comparisons"]["peak_protection"]["headroom_sweep"]
        self.assertGreaterEqual(headroom, -1e-7)
        self.assertLess(abs(headroom), 1e-6)
        self.assertIn("f32(0.98)", self.document["comparisons"]["peak_protection"]["headroom_note"])

    def test_transparency_is_bit_exact_when_gain_is_unity(self):
        transparency = self.document["comparisons"]["transparency"]
        self.assertTrue(transparency["bit_exact"])
        self.assertEqual(transparency["identity_output_sha256"],
                         transparency["reference_output_sha256"])
        self.assertEqual(transparency["engaged_frames"], 0)
        self.assertEqual(transparency["fast_path_frames"], 2)

    def test_zero_content_delay_and_no_lookahead(self):
        delay = self.document["comparisons"]["delay"]
        self.assertEqual(delay["content_delay_samples"], 0)
        self.assertEqual(delay["lookahead_samples"], 0)
        self.assertEqual(delay["input_peak_sample"], delay["output_peak_sample"])
        self.assertEqual(self.document["cases"]["impulse"]["first_modified_sample"], 17)

    def test_attack_and_release(self):
        recovery = self.document["comparisons"]["recovery"]
        fast = recovery["fast_release_ms_1"]["recovery_sample_exact"]
        nominal = self.document["cases"]["impulse"]["recovery_sample_exact"]
        slow = recovery["slow_release_ms_5000"]["recovery_sample_exact"]
        self.assertIsNotNone(fast)
        self.assertIsNotNone(nominal)
        self.assertLess(fast, nominal)
        self.assertIsNone(slow)
        self.assertEqual(self.document["adverse_and_skipped"]["unreached_recovery"]["status"],
                         "not_reached_within_fixture")

    def test_state_transitions_and_reset(self):
        transitions = self.document["comparisons"]["state_transitions"]
        reset = transitions["with_reset"]
        retained = transitions["without_reset"]
        self.assertEqual(reset["reset_count"], 1)
        self.assertEqual(reset["gain_final"], 1.0)
        self.assertGreater(reset["fast_path_frames"], retained["fast_path_frames"])
        self.assertLess(reset["engaged_frames"], retained["engaged_frames"])
        self.assertEqual(reset["input_sha256"], retained["input_sha256"])
        self.assertNotEqual(reset["output_sha256"], retained["output_sha256"])

    def test_interacting_nonlinear_configurations(self):
        interactions = self.document["comparisons"]["interacting_nonlinear"]
        self.assertLessEqual(interactions["clip_then_limiter"]["peak_out"], 0.5 + 2e-8)
        self.assertLess(interactions["clip_then_limiter"]["preprocessed_sha256"], "g")
        self.assertGreater(interactions["limiter_then_clip"]["limiter_engaged_frames"], 0)
        cascade = interactions["cascaded_limiters"]
        self.assertLessEqual(cascade["second"]["frames"][-1]["gain"], 1.0)
        self.assertEqual(cascade["first"]["output_sha256"],
                         cascade["first_output_sha256"])

    def test_intelligibility_and_load_controls(self):
        proxy = self.document["comparisons"]["intelligibility_load_control"]
        self.assertGreater(proxy["envelope_correlation_reference"],
                           proxy["envelope_correlation_degraded_anchor"])
        self.assertIn("not STOI", proxy["note"])
        load = self.document["cases"]["load_control"]
        self.assertEqual(load["engaged_frames"], 0)
        self.assertEqual(load["fast_path_frames"], 20)
        self.assertEqual(load["nonfinite_output_count"], 0)

    def test_control_rejections(self):
        rejected = self.document["adverse_and_skipped"]["control_rejections"]
        self.assertEqual(len(rejected), 9)
        for name, outcome in rejected.items():
            self.assertEqual(outcome["status"], "rejected", name)
            self.assertTrue(outcome["reason"], name)
        self.assertIn("missing_control", rejected["missing_controls"]["reason"])
        self.assertIn("nonfinite", rejected["nonfinite_release_string"]["reason"])
        self.assertIn("nonfinite_json_constant", rejected["json_nan_constant"]["reason"])

    def test_nonfinite_input_is_retained_as_adverse_numerical(self):
        adverse = self.document["adverse_and_skipped"]["nonfinite_input"]
        self.assertEqual(adverse["status"], "adverse_numerical_observed")
        self.assertEqual(adverse["input_nonfinite"], 2)
        self.assertEqual(adverse["output_nonfinite"], 0)
        self.assertEqual(self.document["cases"]["nonfinite"]["sample_count"], 320)

    def test_no_baseline_parity_claim(self):
        self.assertEqual(self.document["baseline_comparison"]["status"], "not_run")
        self.assertEqual(self.document["adverse_and_skipped"]["missing_baseline"]["status"],
                         "not_run")

    def test_adapter_cli_inspect_and_run(self):
        with tempfile.TemporaryDirectory() as scratch:
            scratch = Path(scratch)
            request = report.request("inspect", None, dict(report.DEFAULT), "inspect-cli")
            req_path = scratch / "inspect.json"
            req_path.write_text(json.dumps(request, sort_keys=True) + "\n", encoding="ascii")
            result_path = scratch / "inspect-result.json"
            code = subprocess.call([sys.executable, str(HERE / "run.py"),
                                    "--request", str(req_path), "--result", str(result_path)])
            self.assertEqual(code, 0)
            inspected = json.loads(result_path.read_text(encoding="ascii"))
            self.assertEqual(inspected["identity"], "peak-limiter-reference-v1")
            self.assertIn("unregistered", inspected["registration"])

            run_request = report.request("run", "impulse", dict(report.DEFAULT), "run-cli")
            req_path.write_text(json.dumps(run_request, sort_keys=True) + "\n", encoding="ascii")
            code = subprocess.call([sys.executable, str(HERE / "run.py"),
                                    "--request", str(req_path), "--result", str(result_path)])
            self.assertEqual(code, 0)
            produced = json.loads(result_path.read_text(encoding="ascii"))
            self.assertEqual(produced["output"]["samples_sha256"],
                             self.document["cases"]["impulse"]["output_sha256"])

    def test_adapter_cli_rejects_nonfinite_json_constant(self):
        with tempfile.TemporaryDirectory() as scratch:
            scratch = Path(scratch)
            request = report.request("run", "subceiling", dict(report.DEFAULT), "bad-cli")
            text = json.dumps(request, sort_keys=True).replace('"release_ms": 50.0',
                                                                '"release_ms": NaN')
            self.assertIn("NaN", text)
            req_path = scratch / "bad.json"
            req_path.write_text(text, encoding="ascii")
            code = subprocess.call([sys.executable, str(HERE / "run.py"),
                                    "--request", str(req_path),
                                    "--result", str(scratch / "bad-result.json")])
            self.assertEqual(code, 2)
            self.assertFalse((scratch / "bad-result.json").exists())

    def test_reference_rejects_invalid_controls_directly(self):
        for config, reason in (
                ({"ceiling": 0.0, "release_ms": 50.0}, "ceiling_out_of_range"),
                ({"ceiling": 0.98, "release_ms": 6000.0}, "release_out_of_range"),
                ({"ceiling": math.nan, "release_ms": 50.0}, "nonfinite_control:ceiling"),
                ({"ceiling": 0.98}, "missing_control:release_ms"),
                ({"ceiling": 0.98, "release_ms": 50.0, "x": 1}, "unknown_control:x")):
            with self.subTest(config=config):
                with self.assertRaises(reference.ControlError) as context:
                    reference.validate_controls(config)
                self.assertEqual(str(context.exception), reason)


if __name__ == "__main__":
    unittest.main(verbosity=2)
