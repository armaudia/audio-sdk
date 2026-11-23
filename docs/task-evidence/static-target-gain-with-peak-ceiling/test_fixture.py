"""Deterministic unittest coverage for the static-target-gain DSP fixture.

Run from the worktree root with:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s docs/task-evidence/static-target-gain-with-peak-ceiling -p 'test_*.py' -v

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
    "near_silence_below": (1600, "8eb1df611ee5e23af430e9355790e6a850e07e4be042a19ddd7bf6d8a6dac500"),
    "near_silence_above": (1600, "9c1ab65d3aebaa7e04a9a25ca0fd86cb009f68a2214231014fa1111c6d563f54"),
    "fixed_tone": (3200, "865188a0714e78e2f003d4cf2f925151e60df86a1e5b02c32cbe455243857bbe"),
    "clean_speech_like": (6400, "cc6b89814daed3e6531ab57c26d3f65d2e9c3f970825e3d6be8a1eb254734922"),
    "gain_step_speech": (6400, "1f4e6f9290681bd842bc0729331b268786dd0a6f23a95993ae20462d3f1b2e32"),
    "overshoot": (3200, "a6e134c5bdb924697ae389d3406af99e05027017489436618e0435a819d93958"),
    "nonfinite": (320, "5bf1d6d5a1d44e5073f5f55a89fbe3f8f5364c9768039388afe54447659b7191"),
}
EXPECTED_CASE_DIGESTS = {
    "sweep": "925120721e0c1f04f6e8f47585a2f25f9b9075ec69761f8ed914d1c9498148cc",
    "steps": "fdd8a1ab4440d9a10a7760d60d39b6f46759a1da0db2015a9af118656349b414",
    "impulse": "5526b219130f9627513724a1db316a7a86249244acce13925ab6c4b383793186",
    "silence": "56a43ef88ddfcd0f56f7dd973312c0e73d62f59655c01d7b4e59aaa3be8b3fb6",
    "near_silence_below": "56a43ef88ddfcd0f56f7dd973312c0e73d62f59655c01d7b4e59aaa3be8b3fb6",
    "near_silence_above": "a8fa36d7b85a4e80743174a5aab6ea32194ce6583d7c0a44ef1ba05e34323a71",
    "fixed_tone": "5e0af5553a53dde36d8a48febe9650c6b4d8f2d228850890d37f1300b8c07ba6",
    "clean_speech_like": "f1858f2a273626dc43768a18e18b6445a438087688ec51646ebf78722583581d",
    "gain_step_speech": "5ce9932982706c6d66afc4f81b63204f0de2bddb29c66490a4546d770acf2fa7",
    "overshoot": "cd68e309486e8e314ed58a337ad8108f28ae614d0c4bbd007ac40a8fed6ebcfb",
    "nonfinite": "d17beff5043ad1e8e05f2cbe9d233b7316869c6107cef9f5c8bb162e8df8e703",
}
REPORT_SHA256 = "09500a0414822caef99d1146157b293eea9ebab70e9cf03b2d665c15cea0a3eb"
SPEC_SHA256 = "f386dc8af6ba90958000e370506845ca40ca659ad14ddd4bb2160a20fab70ecb"
ADAPTER_SHA256 = "ee150e7a226ce9ed42fe4216ed227ba9090f35856b8a9db77874cb8b5d571b7d"
CONTRACT_SHA256 = "8ef8c547365382bd863a06825155bd0f403a69ec040c7180810df2d50faa04ea"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class StaticTargetGainFixtureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        cls.spec = run.fixture()

    def test_source_pins(self):
        pins = self.spec["source_pins"]
        self.assertEqual(len(pins), 9)
        for relative_path, expected in pins.items():
            source = AUDIOML_ROOT / relative_path
            self.assertTrue(source.is_file(), "missing pinned source: " + relative_path)
            self.assertEqual(digest(source), expected, relative_path)

    def test_fixture_and_report_files_are_canonical(self):
        self.assertEqual(digest(FIXTURES / "stimuli.json"), SPEC_SHA256)
        self.assertEqual(generate.canonical_bytes(generate.build_spec()),
                         (FIXTURES / "stimuli.json").read_bytes())
        self.assertEqual(digest(ADAPTER_PATH), ADAPTER_SHA256)
        self.assertEqual(digest(CONTRACT_PATH), CONTRACT_SHA256)
        self.assertEqual(digest(REPORT_PATH), REPORT_SHA256)
        self.assertEqual(report.canonical_bytes(report.build_report()),
                         REPORT_PATH.read_bytes())

    def test_contract_is_proposal_only_and_task_local(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        adapter = json.loads(ADAPTER_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "proposal-only")
        self.assertEqual(contract["task"], "SDK-STATIC-TARGET-GAIN-WITH-PEAK-CEILING")
        self.assertEqual(adapter["registration"], "unregistered-developer-only")
        self.assertEqual(adapter["protocol_version"], 1)
        self.assertEqual(contract["format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "f32", "frame_samples": 160})
        self.assertIn("No missing result qualifies", " ".join(contract["invariants"]))

    def test_inspect_reports_supported_controls(self):
        result = run.inspect(report.request(
            "inspect", None, dict(report.DEFAULT_TARGET), "unittest-inspect"))
        self.assertEqual(result["identity"], "static-target-gain-reference-v1")
        self.assertEqual(result["supported_controls"], [
            "identity", "static_target_gain_reference", "fixed_gain_reference"])
        self.assertEqual(result["supported_formats"], ["mono 16 kHz float32, 160-sample frames"])
        self.assertEqual(result["supported_modes"], ["offline", "frame_sequence"])

    def test_all_stimuli_are_deterministic_and_frame_aligned(self):
        self.assertEqual(set(EXPECTED_STIMULI), set(self.spec["stimuli"]))
        for stimulus_id, (length, expected_digest) in EXPECTED_STIMULI.items():
            samples = run.generate(stimulus_id)
            self.assertEqual(len(samples), length, stimulus_id)
            self.assertEqual(length % reference.FRAME_SAMPLES, 0, stimulus_id)
            self.assertEqual(reference.digest_samples(samples), expected_digest, stimulus_id)

    def test_report_counts_and_case_digests(self):
        self.assertEqual(self.document["counts"], {
            "stimuli": 11, "cases": 11, "source_pins": 9,
            "control_rejection_probes": 17, "frame_shape_probes": 2,
            "epoch_session_probes": 4, "level_sweep_points": 9,
            "target_sweep_points": 5, "ceiling_sweep_points": 6,
            "interaction_configurations": 6, "blockers": 5})
        self.assertEqual(set(EXPECTED_CASE_DIGESTS), set(self.document["cases"]))
        for case_id, expected_digest in EXPECTED_CASE_DIGESTS.items():
            self.assertEqual(self.document["cases"][case_id]["output_sha256"],
                             expected_digest, case_id)

    def test_exact_gain_arithmetic_and_target_rms(self):
        case = self.document["cases"]["fixed_tone"]
        self.assertAlmostEqual(case["output_rms_db"], report.DEFAULT_TARGET["target_dbfs"],
                               places=6)
        self.assertAlmostEqual(case["gain_db_plan"],
                               case["desired_gain_db_unbounded"], places=9)
        self.assertAlmostEqual(case["gain_db_plan"],
                               report.expected_gain_db(run.generate("fixed_tone"),
                                                       report.DEFAULT_TARGET), places=9)
        gain_linear = report.reference.dbfs_to_linear(case["gain_db_plan"])
        self.assertAlmostEqual(gain_linear, 10.0 ** (case["gain_db_plan"] / 20.0), places=12)
        for row in self.document["comparisons"]["level_sweep"]["rows"]:
            self.assertAlmostEqual(row["gain_db"], row["gain_db_expected"], places=6)
        rows = {row["level_db"]: row
                for row in self.document["comparisons"]["level_sweep"]["rows"]}
        self.assertEqual(rows[-42.0]["gain_db"], 18.0)
        self.assertEqual(rows[0.0]["gain_db"], -18.0)
        self.assertAlmostEqual(rows[-36.0]["output_rms_db"], -24.0, places=6)

    def test_target_and_ceiling_sweeps(self):
        targets = {row["target_dbfs"]: row
                   for row in self.document["comparisons"]["target_sweep"]["rows"]}
        self.assertEqual(targets[-60.0]["gain_db"], -18.0)
        self.assertEqual(targets[-6.0]["gain_db"], 18.0)
        self.assertAlmostEqual(targets[-24.0]["output_rms_db"], -24.0, places=6)
        for row in self.document["comparisons"]["ceiling_sweep"]["rows"]:
            self.assertLessEqual(row["peak_output"], row["ceiling"] + 1e-7)
            self.assertGreaterEqual(row["headroom"], -1e-7)
        impulse_rows = [row for row in self.document["comparisons"]["ceiling_sweep"]["rows"]
                        if row["stimulus_id"] == "impulse"]
        self.assertEqual(len(impulse_rows), 3)
        self.assertTrue(all(row["clipped_samples"] > 0 for row in impulse_rows))

    def test_silence_and_near_silence_handling(self):
        cases = self.document["cases"]
        silence = self.document["adverse_and_skipped"]["silence_and_near_silence"]
        self.assertEqual(silence["status"], "observed")
        for case_id in ("silence", "near_silence_below"):
            self.assertTrue(cases[case_id]["silence_bypass"])
            self.assertEqual(cases[case_id]["peak_output"], 0.0)
            self.assertEqual(cases[case_id]["gain_db_plan"], 0.0)
        above = cases["near_silence_above"]
        self.assertFalse(above["silence_bypass"])
        self.assertEqual(above["gain_db_plan"], 18.0)
        self.assertGreater(above["peak_output"], 0.0)
        self.assertLessEqual(above["peak_output"], report.CEILING + 1e-7)
        self.assertIn("not gated", silence["note"])

    def test_nonfinite_input_is_observed_and_bounded(self):
        case = self.document["cases"]["nonfinite"]
        adverse = self.document["adverse_and_skipped"]["nonfinite_input"]
        self.assertEqual(adverse["status"], "adverse_numerical_observed")
        self.assertEqual(case["nonfinite_input_count"], 2)
        self.assertEqual(case["nonfinite_output_count"], 0)
        self.assertEqual(case["finite_output_count"], case["sample_count"])
        self.assertGreater(case["clipped_samples"], 0)
        self.assertAlmostEqual(case["peak_output"], report.CEILING, delta=1e-7)
        result = run.run(report.request(
            "run", "nonfinite", dict(report.DEFAULT_TARGET), "unittest-nonfinite"))
        self.assertIn("samples", result["output"])
        self.assertTrue(all(math.isfinite(value) for value in result["output"]["samples"]))
        self.assertEqual(result["errors"], [])

    def test_sweep_response_and_zero_delay(self):
        response = self.document["comparisons"]["response"]
        self.assertEqual(len(response["bands"]), 8)
        ratios = [band["rms_ratio_db"] for band in response["bands"]]
        self.assertLess(max(ratios) - min(ratios), 1e-6)
        delay = self.document["comparisons"]["delay"]
        self.assertEqual(delay["content_delay_samples"], 0)
        self.assertEqual(delay["lookahead_samples"], 0)
        self.assertEqual(delay["input_peak_sample"], 17)
        self.assertEqual(delay["output_peak_sample"], 17)

    def test_control_rejections(self):
        rejections = self.document["adverse_and_skipped"]["control_rejections"]
        self.assertEqual(len(rejections), 17)
        self.assertTrue(all(item["status"] == "rejected" for item in rejections.values()))
        for name in ("missing_target_dbfs", "missing_silence_floor_dbfs",
                     "inverted_gain_bounds", "nonfinite_target", "infinite_ceiling",
                     "json_nan_constant", "control_mismatch"):
            self.assertEqual(rejections[name]["status"], "rejected", name)

    def test_structural_control_and_frame_shape_rejections(self):
        shapes = self.document["adverse_and_skipped"]["frame_shape"]
        self.assertEqual(shapes["boundary_short_frame"]["status"], "rejected")
        self.assertEqual(shapes["reference_short_frame"]["status"], "rejected")
        with self.assertRaises(run.RequestError):
            run.run(report.request(
                "run", "caller_sequence", dict(report.DEFAULT_TARGET), "unittest-shape",
                stimulus_samples=[0.0] * 159))
        processor = reference.StaticTargetGain(dict(report.DEFAULT_TARGET))
        with self.assertRaises(ValueError):
            processor.process_frame([0.0] * 161, processor.plan([0.0] * 161))

    def test_stale_epoch_is_rejected_before_state_changes(self):
        samples = run.generate("fixed_tone")[:320]
        first, second = samples[:160], samples[160:]
        session = "unittest-stale"
        initial = run.run(report.request("run", "caller_sequence",
                                         dict(report.DEFAULT_TARGET), session,
                                         epoch=4, stimulus_samples=first))
        before = initial["session_state"]["buffer_samples_sha256"]
        with self.assertRaises(run.RequestError) as caught:
            run.run(report.request("run", "caller_sequence", dict(report.DEFAULT_TARGET),
                                   session, epoch=3, stimulus_samples=second))
        self.assertEqual(str(caught.exception), "stale_epoch")
        after_stale = run.SESSIONS[(session, "static_target_gain_reference",
                                    run._config_digest(report.DEFAULT_TARGET))]
        self.assertEqual(reference.digest_samples(after_stale["samples"]), before)
        valid = run.run(report.request("run", "caller_sequence", dict(report.DEFAULT_TARGET),
                                       session, epoch=4, continue_session=True,
                                       stimulus_samples=second))
        self.assertEqual(valid["session_state"]["buffer_samples_sha256"],
                         reference.digest_samples(samples))

    def test_session_replay_and_no_leakage(self):
        control = self.document["adverse_and_skipped"]["epoch_and_sessions"][
            "state_leakage_across_sessions"]
        self.assertEqual(control["status"], "observed")
        self.assertEqual(control["split_second_segment_sha256"],
                         control["expected_second_segment_sha256"])
        self.assertEqual(control["resumed_second_segment_sha256"],
                         control["expected_second_segment_sha256"])
        samples = run.generate("fixed_tone")
        one_shot = report.call_sequence(samples, dict(report.DEFAULT_TARGET),
                                        "unittest-replay-once")
        first = report.call_sequence(samples[:1600], dict(report.DEFAULT_TARGET),
                                     "unittest-replay-split")
        report.call_sequence(run.generate("steps"), dict(report.DEFAULT_TARGET),
                             "unittest-replay-other")
        second = report.call_sequence(samples[1600:], dict(report.DEFAULT_TARGET),
                                      "unittest-replay-split", continue_session=True)
        self.assertEqual(second["output"]["samples_sha256"],
                         reference.digest_samples(one_shot["output"]["samples"][1600:]))
        self.assertEqual(len(first["output"]["samples"]), 1600)
        transition = self.document["adverse_and_skipped"]["epoch_and_sessions"]["epoch_advance"]
        self.assertEqual(transition["status"], "observed")
        self.assertEqual(transition["transition"]["buffer"], "cleared")

    def test_reset_frames_change_static_segments(self):
        transitions = self.document["comparisons"]["state_transitions"]
        self.assertTrue(transitions["distinct"])
        self.assertEqual(transitions["with_reset"]["reset_count"], 1)
        self.assertEqual(transitions["without_reset"]["reset_count"], 0)
        self.assertEqual(len(transitions["with_reset"]["segments"]), 2)
        self.assertEqual(len(transitions["without_reset"]["segments"]), 1)
        with_plans = transitions["with_reset"]["segments"]
        self.assertNotEqual(with_plans[0]["gain_db"], with_plans[1]["gain_db"])

    def test_interacting_nonlinear_controls_are_static_chains(self):
        interactions = self.document["comparisons"]["interacting_nonlinear"]
        self.assertTrue(interactions["all_present"])
        self.assertEqual(interactions["configuration_count"], 6)
        self.assertGreaterEqual(interactions["distinct_output_count"], 4)
        self.assertTrue(interactions["identity_transparent"])
        for name in ("target_only", "fixed_only", "target_then_fixed",
                     "fixed_then_target", "low_ceiling_target_then_target",
                     "identity_then_target"):
            self.assertEqual(len(interactions[name]["output_sha256"]), 64, name)
        self.assertIn("native chain", interactions["note"])

    def test_energy_matched_and_identity_controls_are_synthetic_only(self):
        load = self.document["comparisons"]["load_and_energy_matched_control"]
        self.assertAlmostEqual(load["windowed_rms_abs_error_db_energy_matched"],
                               0.0, places=6)
        self.assertGreater(load["windowed_rms_abs_error_db_identity"], 4.0)
        self.assertGreater(load["windowed_rms_abs_error_db_target"],
                           load["windowed_rms_abs_error_db_identity"])
        for key in ("envelope_correlation_clean_vs_stepped_input",
                    "envelope_correlation_clean_vs_target_output",
                    "envelope_correlation_clean_vs_identity"):
            self.assertTrue(math.isfinite(load[key]), key)
        self.assertIn("Not STOI", load["note"])

    def test_status_and_blockers_are_explicit(self):
        self.assertEqual(self.document["status"], "proposal_only_synthetic")
        self.assertEqual(self.document["qualification_status"], "incomplete")
        self.assertEqual(self.document["baseline_comparison"]["status"], "not_qualified")
        self.assertIn("No missing", self.document["missing_result_policy"])
        statuses = {item["id"]: item["status"] for item in self.document["blockers"]}
        self.assertEqual(len(statuses), 5)
        for key in ("real_speech_qualification", "listening_and_loudness_standard",
                    "native_provider_and_baseline", "target_device_and_deadline",
                    "pause_noise_and_interaction_realtime"):
            self.assertEqual(statuses[key], "blocked", key)
            self.assertTrue(self.document["blockers"][
                next(index for index, item in enumerate(self.document["blockers"])
                     if item["id"] == key)]["reopening_condition"])

    def test_cli_inspect_and_run_roundtrip(self):
        with tempfile.TemporaryDirectory() as scratch:
            request_path = Path(scratch) / "request.json"
            result_path = Path(scratch) / "result.json"
            request = report.request("inspect", None, dict(report.DEFAULT_TARGET),
                                     "unittest-cli")
            request_path.write_text(json.dumps(request) + "\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(HERE / "run.py"), "--request", str(request_path),
                 "--result", str(result_path)],
                cwd=HERE, capture_output=True, text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(result["operation"], "inspect")
            self.assertEqual(result["identity"], "static-target-gain-reference-v1")

    def test_report_cli_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as scratch:
            target = Path(scratch) / "report.json"
            with target.open("wb") as output:
                completed = subprocess.run(
                    [sys.executable, str(HERE / "report.py")], cwd=HERE,
                    stdout=output, stderr=subprocess.PIPE,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
            self.assertEqual(completed.returncode, 0, completed.stderr.decode())
            self.assertEqual(target.read_bytes(), REPORT_PATH.read_bytes())


if __name__ == "__main__":
    unittest.main()
