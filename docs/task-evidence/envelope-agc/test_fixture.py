"""Deterministic unittest coverage for the envelope-AGC DSP fixture.

Run from this directory with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py

All checks are offline, stdlib-only and task-local. No real audio, model,
device, download or installed-provider build is used.
"""

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import generate
import reference
import report
import run

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
REPORT_PATH = FIXTURES / "report.json"
ADAPTER_PATH = HERE / "adapter.json"
CONTRACT_PATH = HERE / "contract.json"
AUDIOML_ROOT = Path(os.environ.get(
    "AUDIOML_ROOT", str(HERE.parents[5]))).resolve()

EXPECTED_STIMULI = {
    "sweep": (4000, "11b87f0a08f353493f0c00c19df283fa77b736c92a0cab31029e2e7c1f6f71d6"),
    "steps": (4000, "df4d9223a379d1cf071b8034cac669d6d99ea20e9d089aa9ee11beaab3d21eb8"),
    "impulse": (3200, "a53de14748214fd307fd5b0990fc73b56e95b9a8ae4fde496528c298c3883f15"),
    "silence": (1600, "56a43ef88ddfcd0f56f7dd973312c0e73d62f59655c01d7b4e59aaa3be8b3fb6"),
    "fixed_tone": (3200, "865188a0714e78e2f003d4cf2f925151e60df86a1e5b02c32cbe455243857bbe"),
    "clean_speech_like": (6400, "cc6b89814daed3e6531ab57c26d3f65d2e9c3f970825e3d6be8a1eb254734922"),
    "gain_step_speech": (6400, "1f4e6f9290681bd842bc0729331b268786dd0a6f23a95993ae20462d3f1b2e32"),
    "overshoot": (3200, "a6e134c5bdb924697ae389d3406af99e05027017489436618e0435a819d93958"),
    "nonfinite": (320, "5bf1d6d5a1d44e5073f5f55a89fbe3f8f5364c9768039388afe54447659b7191"),
}
EXPECTED_CASE_DIGESTS = {
    "sweep": "78ce3d92568561aa9ab435f58a65773ea3c2e325699bca1e0ceb361b03ccf4e5",
    "steps": "6ae32253c78e42e685024d258606fc02432f77f3398d5d2746909d756376b679",
    "impulse": "01ebea564a4c9bdb6e694ecb45253d87866bf489b77b8060c9602b3c8dc52056",
    "silence": "56a43ef88ddfcd0f56f7dd973312c0e73d62f59655c01d7b4e59aaa3be8b3fb6",
    "fixed_tone": "813a02753d6195cbe2d71fa356332b9675631d9ac611193f31066c8373faeec5",
    "clean_speech_like": "e7e7304120ef94ec33bb160482f2d53aacc262d50b048d7684633f87698fe51c",
    "gain_step_speech": "9d016f05e1c967a63d7eb5f0bec0ac7550146191183cced1bc67dd11c58aea1d",
    "overshoot": "5ff46b7bd3e74f01d286102b7f7a7c730f08a1ca2a864dbf8e399a93946052e8",
    "nonfinite": "2377c6f55e3002bbc4746f8b30826caa0d9c3cf7f9a73e0999f51fc606458b9e",
    "sweep_ceiling_minus_6": "78ce3d92568561aa9ab435f58a65773ea3c2e325699bca1e0ceb361b03ccf4e5",
    "impulse_fast_attack": "74170dc09a45ae849c4dc188c9e39f2ee714735b3564896e7ddf6939f10418a6",
    "impulse_slow_release": "2a02e449bd0a485fb146689bc7e941995791b0f066295f689e98842041a42e02",
}
REPORT_SHA256 = "f4bdf1862c75ed89cb1ca8c3bc8ee21aeb7831495410a210d4ca6d3e81950fe3"
SPEC_SHA256 = "12e3377935d0c0ba0ba489c559466c510e48903ce0a6515e1e59926a46aeb5e4"
ADAPTER_SHA256 = "7258da7eaf20ece3d257d10f90a658f9ef8b0abc3a6ba6a7c4d96a8f75737250"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class EnvelopeAGCFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.spec = run.fixture()

    def test_source_pins(self):
        pins = self.spec["source_pins"]
        self.assertEqual(len(pins), 10)
        for relative_path, expected in pins.items():
            source = AUDIOML_ROOT / relative_path
            self.assertTrue(source.is_file(), "missing pinned source: " + relative_path)
            self.assertEqual(digest(source), expected, relative_path)

    def test_fixture_and_report_files_are_canonical(self):
        self.assertEqual(digest(FIXTURES / "stimuli.json"), SPEC_SHA256)
        self.assertEqual(generate.canonical_bytes(generate.build_spec()),
                         (FIXTURES / "stimuli.json").read_bytes())
        self.assertEqual(digest(ADAPTER_PATH), ADAPTER_SHA256)
        self.assertEqual(digest(REPORT_PATH), REPORT_SHA256)
        self.assertEqual(report.canonical_bytes(report.build_report()), REPORT_PATH.read_bytes())

    def test_contract_is_proposal_only_and_task_local(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        adapter = json.loads(ADAPTER_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "proposal-only")
        self.assertEqual(contract["task"], "SDK-ENVELOPE-AGC")
        self.assertEqual(adapter["registration"], "unregistered-developer-only")
        self.assertEqual(adapter["protocol_version"], 1)
        self.assertEqual(contract["format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "f32", "frame_samples": 160})

    def test_inspect_reports_supported_controls(self):
        result = run.inspect(report.request("inspect", None, dict(report.DEFAULT_AGC), "unittest-inspect"))
        self.assertEqual(result["identity"], "envelope-agc-reference-v1")
        self.assertEqual(result["supported_controls"], [
            "identity", "envelope_agc_reference", "static_gain_reference",
            "peak_limiter_reference", "compressor_reference"])
        self.assertEqual(result["supported_formats"], ["mono 16 kHz float32, 160-sample frames"])

    def test_all_stimuli_are_deterministic_and_frame_aligned(self):
        self.assertEqual(set(EXPECTED_STIMULI), set(self.spec["stimuli"]))
        for stimulus_id, (length, expected_digest) in EXPECTED_STIMULI.items():
            samples = run.generate(stimulus_id)
            self.assertEqual(len(samples), length, stimulus_id)
            self.assertEqual(length % reference.FRAME_SAMPLES, 0, stimulus_id)
            self.assertEqual(reference.digest_samples(samples), expected_digest, stimulus_id)

    def test_report_counts_and_case_digests(self):
        self.assertEqual(self.document["counts"], {
            "stimuli": 9, "cases": 12, "source_pins": 10,
            "control_rejection_probes": 16, "frame_shape_probes": 2,
            "epoch_session_probes": 4, "interaction_configurations": 7,
            "blockers": 5})
        self.assertEqual(set(EXPECTED_CASE_DIGESTS), set(self.document["cases"]))
        for case_id, expected_digest in EXPECTED_CASE_DIGESTS.items():
            self.assertEqual(self.document["cases"][case_id]["output_sha256"],
                             expected_digest, case_id)

    def test_gain_and_headroom(self):
        case = self.document["cases"]["fixed_tone"]
        self.assertAlmostEqual(case["steady_state_rms_db"], -24.0, delta=3.0)
        self.assertLessEqual(case["peak_output"], report.CEILING + 1e-7)
        self.assertGreaterEqual(case["headroom"], -1e-7)
        self.assertEqual(case["nonfinite_output_count"], 0)
        lower_ceiling = self.document["cases"]["sweep_ceiling_minus_6"]
        self.assertEqual(lower_ceiling["output_sha256"],
                         self.document["cases"]["sweep"]["output_sha256"])
        self.assertEqual(lower_ceiling["clipped_samples"], 0)

    def test_sweep_response_bands_and_zero_delay(self):
        response = self.document["comparisons"]["response"]
        self.assertEqual(len(response["bands"]), 8)
        self.assertTrue(all(band["input_rms_db"] > -100.0 for band in response["bands"]))
        delay = self.document["comparisons"]["delay"]
        self.assertEqual(delay["content_delay_samples"], 0)
        self.assertEqual(delay["lookahead_samples"], 0)
        self.assertEqual(delay["input_peak_sample"], 17)

    def test_steps_and_attack_release(self):
        steps = self.document["cases"]["steps"]
        self.assertGreater(steps["clipped_samples"], 0)
        self.assertLess(steps["gain_db_min"], steps["gain_db_max"] - 3.0)
        overshoot = self.document["cases"]["overshoot"]
        attack = overshoot["attack_release"]
        self.assertEqual(attack["release_status"], "not_reached_within_fixture")
        self.assertIsNotNone(attack["attack_sample"])
        self.assertGreaterEqual(attack["attack_sample"], 1600)
        self.assertLess(attack["attack_sample"], 2400)
        self.assertEqual(self.document["adverse_and_skipped"]["unreached_recovery"]["status"],
                         "not_reached_within_fixture")

    def test_silence_handling(self):
        silence = self.document["cases"]["silence"]
        self.assertEqual(silence["peak_output"], 0.0)
        self.assertEqual(silence["clipped_samples"], 0)
        self.assertEqual(silence["nonfinite_output_count"], 0)
        self.assertEqual(silence["gain_db_final"], 18.0)
        self.assertEqual(self.document["adverse_and_skipped"]["silence_handling"]["status"],
                         "observed")

    def test_nonfinite_input_is_observed_and_bounded(self):
        case = self.document["cases"]["nonfinite"]
        self.assertEqual(case["nonfinite_input_count"], 2)
        self.assertEqual(case["nonfinite_output_count"], 0)
        self.assertEqual(case["finite_output_count"], case["sample_count"])
        result = run.run(report.request(
            "run", "nonfinite", dict(report.DEFAULT_AGC), "unittest-nonfinite"))
        self.assertIn("samples", result["output"])
        self.assertTrue(all(math.isfinite(value) for value in result["output"]["samples"]))
        self.assertAlmostEqual(result["output"]["peak_abs"], report.CEILING, delta=1e-7)
        self.assertEqual(result["errors"], [])

    def test_invalid_attack_release_target_and_ceiling_controls(self):
        rejections = self.document["adverse_and_skipped"]["control_rejections"]
        for name in ("attack_zero", "attack_over_range", "release_zero", "release_over_range",
                     "target_below_range", "target_positive", "ceiling_positive",
                     "ceiling_below_range", "nonfinite_target", "infinite_release"):
            self.assertEqual(rejections[name]["status"], "rejected", name)
        self.assertTrue(all(item["status"] == "rejected" for item in rejections.values()))

    def test_structural_control_and_frame_shape_rejections(self):
        rejections = self.document["adverse_and_skipped"]["control_rejections"]
        for name in ("missing_target_dbfs", "unknown_control_key", "boolean_attack",
                     "string_release", "inverted_gain_bounds", "json_nan_constant"):
            self.assertEqual(rejections[name]["status"], "rejected", name)
        shapes = self.document["adverse_and_skipped"]["frame_shape"]
        self.assertEqual(shapes["boundary_short_frame"]["status"], "rejected")
        self.assertEqual(shapes["reference_short_frame"]["status"], "rejected")
        with self.assertRaises(run.RequestError):
            run.run(report.request(
                "run", "caller_sequence", dict(report.DEFAULT_AGC), "unittest-shape",
                stimulus_samples=[0.0] * 159))
        with self.assertRaises(ValueError):
            reference.EnvelopeAGC(report.DEFAULT_AGC).process([0.0] * 161)

    def test_stale_epoch_is_rejected_before_state_changes(self):
        epoch = self.document["adverse_and_skipped"]["epoch_and_sessions"]["stale_epoch"]
        self.assertEqual(epoch["status"], "rejected")
        self.assertEqual(epoch["reason"], "stale_epoch")
        self.assertTrue(epoch["state_unchanged_digest_match"])
        session = "unittest-stale"
        first = run.generate("fixed_tone")[:160]
        run.run(report.request("run", "caller_sequence", dict(report.DEFAULT_AGC), session,
                               epoch=4, stimulus_samples=first))
        with self.assertRaises(run.RequestError) as caught:
            run.run(report.request("run", "caller_sequence", dict(report.DEFAULT_AGC), session,
                                   epoch=3, stimulus_samples=first))
        self.assertEqual(str(caught.exception), "stale_epoch")

    def test_state_does_not_leak_across_sessions(self):
        control = self.document["adverse_and_skipped"]["epoch_and_sessions"][
            "state_leakage_across_sessions"]
        self.assertEqual(control["status"], "observed")
        self.assertEqual(control["one_shot_sha256"], control["rejoined_sha256"])
        samples = run.generate("impulse")
        session_a = "unittest-leak-a"
        session_b = "unittest-leak-b"
        a1 = run.run(report.request("run", "caller_sequence", dict(report.DEFAULT_AGC),
                                    session_a, stimulus_samples=samples[:1600]))
        run.run(report.request("run", "caller_sequence", dict(report.DEFAULT_AGC),
                               session_b, stimulus_samples=samples))
        a2 = run.run(report.request("run", "caller_sequence", dict(report.DEFAULT_AGC),
                                    session_a, epoch=1, continue_session=True,
                                    stimulus_samples=samples[1600:]))
        self.assertEqual(
            reference.digest_samples(a1["output"]["samples"] + a2["output"]["samples"]),
            reference.digest_samples(run.run(report.request(
                "run", "caller_sequence", dict(report.DEFAULT_AGC), "unittest-leak-once",
                stimulus_samples=samples))["output"]["samples"]))

    def test_reset_frames_change_state_transitions(self):
        transitions = self.document["comparisons"]["state_transitions"]
        self.assertTrue(transitions["distinct"])
        self.assertEqual(transitions["with_reset"]["reset_count"], 1)
        self.assertEqual(transitions["without_reset"]["reset_count"], 0)

    def test_peak_overshoot_is_bounded_by_ceiling(self):
        overshoot = self.document["adverse_and_skipped"]["peak_overshoot"]
        self.assertEqual(overshoot["status"], "observed")
        self.assertGreater(overshoot["clipped_samples"], 0)
        self.assertLessEqual(overshoot["peak_output"], report.CEILING + 1e-7)

    def test_interacting_limiter_and_compressor_configurations(self):
        interactions = self.document["comparisons"]["interacting_nonlinear"]
        self.assertTrue(interactions["all_present"])
        self.assertEqual(interactions["configuration_count"], 7)
        self.assertGreaterEqual(interactions["distinct_output_count"], 5)
        for name in ("agc_only", "limiter_only", "compressor_only", "agc_then_limiter",
                     "agc_then_compressor", "limiter_then_agc", "compressor_then_agc"):
            self.assertEqual(len(interactions[name]["output_sha256"]), 64, name)
        self.assertEqual(interactions["agc_then_limiter"]["output_sha256"],
                         interactions["agc_only"]["output_sha256"])
        self.assertIn("No native", interactions["note"])

    def test_load_specific_control_is_reported_without_quality_claim(self):
        load = self.document["comparisons"]["load_and_gain_step_control"]
        for key in ("windowed_rms_abs_error_db_agc", "windowed_rms_abs_error_db_identity",
                    "windowed_rms_abs_error_db_static_gain",
                    "envelope_correlation_clean_vs_stepped_input",
                    "envelope_correlation_clean_vs_agc_output"):
            self.assertIsInstance(load[key], float, key)
            self.assertTrue(math.isfinite(load[key]), key)
        self.assertIn("Not STOI", load["note"])

    def test_status_and_blockers_are_explicit(self):
        self.assertEqual(self.document["status"], "proposal_only_synthetic")
        self.assertEqual(self.document["qualification_status"], "incomplete")
        self.assertEqual(len(self.document["blockers"]), 5)
        statuses = {item["id"]: item["status"] for item in self.document["blockers"]}
        for key in ("real_speech_qualification", "listening_and_stoi",
                    "native_provider_and_baseline", "target_device_and_deadline",
                    "nonlinear_interaction_realtime"):
            self.assertEqual(statuses[key], "blocked", key)
        self.assertEqual(self.document["baseline_comparison"]["status"], "not_qualified")

    def test_cli_inspect_and_run_roundtrip(self):
        with tempfile.TemporaryDirectory() as scratch:
            request_path = Path(scratch) / "request.json"
            result_path = Path(scratch) / "result.json"
            request = report.request("inspect", None, dict(report.DEFAULT_AGC), "unittest-cli")
            request_path.write_text(json.dumps(request) + "\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(HERE / "run.py"), "--request", str(request_path),
                 "--result", str(result_path)],
                cwd=HERE, capture_output=True, text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(result["operation"], "inspect")
            self.assertEqual(result["identity"], "envelope-agc-reference-v1")


if __name__ == "__main__":
    unittest.main()
