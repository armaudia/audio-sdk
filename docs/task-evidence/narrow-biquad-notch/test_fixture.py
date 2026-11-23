"""Unit tests for the deterministic narrow biquad notch fixture."""

import hashlib
import json
import math
import unittest
from pathlib import Path

import fixture

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
AUDIOML_ROOT = REPO_ROOT.parents[2]

CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
REPORT_ON_DISK = (HERE / "report.json").read_text(encoding="utf-8")

REPORT_DIGEST = "c80db3087434ed0e8d5755b037e052ff3dfa5ae03d582f858ba76526253e99dd"
FIXTURE_DIGEST = "b98e9b2a711dce687ec62002eb72487df871b7ce10aaaa2864d831258327fb22"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report() -> dict:
    return json.loads(REPORT_ON_DISK)


class NarrowNotchFixtureTest(unittest.TestCase):
    def test_pins_and_fixed_v0_format(self):
        self.assertEqual(fixture.CONTRACT_ID, CONTRACT["schema_id"])
        self.assertEqual(fixture.SAMPLE_RATE_HZ, 16000)
        self.assertEqual(fixture.FRAME_SAMPLES, 160)
        self.assertEqual(len(fixture.SWEEP_FREQUENCIES_HZ), 78)
        self.assertEqual(fixture.SOURCE_PINS, CONTRACT["source_pins"])
        self.assertEqual(fixture.BOUNDARY_PINS, CONTRACT["boundary_pins"])
        self.assertEqual(fixture.DEFAULT_CONFIG, CONTRACT["reference_controls"])
        self.assertEqual(CONTRACT["format"], {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "f32", "frame_samples": 160})

    def test_external_source_pins_match_exact_bytes(self):
        pins = [(AUDIOML_ROOT / path, digest)
                for path, digest in fixture.SOURCE_PINS.items()]
        pins.extend((REPO_ROOT / path, digest)
                    for path, digest in fixture.BOUNDARY_PINS.items())
        self.assertEqual(len(pins), 6)
        for source, digest in pins:
            self.assertTrue(source.is_file(), str(source))
            self.assertEqual(sha256_file(source), digest, str(source))

    def test_local_artifact_pins(self):
        for relative_path, digest in CONTRACT["artifact_pins"].items():
            path = HERE / relative_path
            self.assertTrue(path.is_file(), relative_path)
            self.assertEqual(sha256_file(path), digest, relative_path)

    def test_explicit_control_validation(self):
        self.assertEqual(fixture.validate_config(None), fixture.Status.REJECTED_MISSING)
        missing = fixture.config_with()
        del missing["frequency_hz"]
        self.assertEqual(fixture.validate_config(missing), fixture.Status.REJECTED_MISSING)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            frequency_hz=float("nan"))), fixture.Status.REJECTED_NONFINITE)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            bandwidth_hz=float("inf"))), fixture.Status.REJECTED_NONFINITE)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            frequency_hz=8100.0)), fixture.Status.REJECTED_INVALID)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            bandwidth_hz=0.0)), fixture.Status.REJECTED_INVALID)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            q=0.0)), fixture.Status.REJECTED_INVALID)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            q=float("nan"))), fixture.Status.REJECTED_NONFINITE)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            q=float("inf"))), fixture.Status.REJECTED_NONFINITE)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            q=5.0)), fixture.Status.REJECTED_INVALID)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            frequency_hz="1000")), fixture.Status.REJECTED_INVALID)
        self.assertEqual(fixture.validate_config(fixture.config_with(
            unexpected=1)), fixture.Status.REJECTED_INVALID)
        status, instance = fixture.NotchSession.create(None)
        self.assertEqual(status, fixture.Status.REJECTED_MISSING)
        self.assertIsNone(instance)

    def test_coefficient_design_and_analytic_response(self):
        coefficients = fixture.design_coefficients(1000.0, 100.0)
        self.assertAlmostEqual(fixture.effective_q(fixture.config_with()), 10.0)
        self.assertLess(fixture.analytic_gain(coefficients, 1000.0), 1e-9)
        self.assertAlmostEqual(fixture.analytic_gain(coefficients, 1500.0),
                               0.9934484, places=6)
        for arguments in ((float("nan"), 100.0, None), (1000.0, 0.0, None),
                          (1000.0, 100.0, float("nan")), (1000.0, 100.0, 0.0)):
            with self.assertRaises(ValueError):
                fixture.design_coefficients(*arguments)

    def test_silence_impulse_step_and_chirp(self):
        results = report()["results"]
        silence = results["silence"]
        self.assertEqual(silence["status"], "ok")
        self.assertEqual(silence["peak_abs_output"], 0.0)
        self.assertEqual(silence["output_digest"],
                         "c65206769723a13afe80c0d925531639ceef9c2eb97eee3b1b542739ec40597f")
        impulse = results["impulse"]
        self.assertEqual(impulse["status"], "ok")
        self.assertEqual(impulse["peak_index"], 0)
        self.assertAlmostEqual(impulse["peak_abs_output"], 0.490613, places=6)
        self.assertEqual(impulse["output_digest"],
                         "2cf94e6dfec4b128902b92aa5b2464275ef3f0afe4dd6a237a8ad50c8032ae88")
        step = results["step"]
        self.assertEqual(step["status"], "ok")
        self.assertGreaterEqual(step["crossing_samples"], 0)
        self.assertEqual(step["steady_state_mean"], 0.25)
        self.assertEqual(step["output_digest"],
                         "adcb7d0bba8ed970102fdaab0ac9f9e3f8c5494a956826120c118be5b2dd5d18")
        chirp = results["chirp"]
        self.assertEqual(chirp["status"], "ok")
        self.assertEqual(chirp["frames"], 40)
        self.assertTrue(chirp["finite"])
        self.assertEqual(chirp["output_digest"],
                         "310a53b82515af9905bcd705ea787e13abfdb8848c1b08f1c5266963571ff9c3")

    def test_frequency_sweep_matches_analytic_response(self):
        sweep = report()["results"]["frequency_sweep"]
        self.assertEqual(sweep["frames_per_frequency"], 12)
        self.assertEqual(len(sweep["rows"]), 78)
        self.assertLess(sweep["max_gain_error_db"], 0.1)
        self.assertLess(sweep["center_measured_gain"], 0.02)
        self.assertLessEqual(sweep["min_gain"], 0.02)
        self.assertLessEqual(sweep["max_gain"], 1.01)
        self.assertTrue(all(row["gain_error_db"] < 0.1 for row in sweep["rows"]
                            if row["analytic_gain"] >= 0.01))
        self.assertEqual(sweep["output_digest"],
                         "dad78e813f4d8243c83aa7d724cd1ef95b814b91874df4700be9c511398f8aba")

    def test_explicit_frequency_and_bandwidth_controls(self):
        controls = report()["results"]["center_bandwidth_controls"]
        rows = controls["rows"]
        self.assertEqual(len(rows), 4)
        self.assertEqual([(row["frequency_hz"], row["bandwidth_hz"]) for row in rows],
                         [(1000.0, 100.0), (120.0, 12.0), (250.0, 25.0), (4000.0, 400.0)])
        for row in rows:
            self.assertEqual(row["status"], "ok")
            self.assertEqual(row["skirt_status"], "ok")
            self.assertEqual(row["quality"], 10.0)
            self.assertLess(row["center_measured_gain"], 0.02)
            self.assertGreater(row["skirt_measured_gain"], 0.95)
            self.assertLess(abs(row["skirt_measured_gain"] - row["skirt_analytic_gain"]), 0.02)
        self.assertEqual(controls["output_digest"],
                         "9e4717705c800e3e112f34d44a7d57c65aed84cdc7b9e7996e1479d2a3dbebb2")

    def test_attack_release_and_state_transitions(self):
        result = report()["results"]["attack_release"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["probe_frequency_hz"], 700.0)
        self.assertEqual(result["attack_frames"], 0)
        self.assertIsNotNone(result["release_frames"])
        self.assertLessEqual(result["release_frames"], 20)
        self.assertEqual(result["output_digest"],
                         "2af71f440d76c78e9dac2bd3a0fe6e5494e281b944d1f35b0a4c5af6c9c486ab")

    def test_clean_speech_proxy_impact(self):
        clean = report()["results"]["clean_speech"]
        self.assertEqual(clean["status"], "ok")
        self.assertEqual(clean["bypass_status"], "ok")
        self.assertEqual(clean["frames"], 300)
        self.assertLess(abs(clean["rms_delta_db"]), 0.5)
        self.assertGreater(clean["envelope_correlation"], 0.99)
        self.assertIn("synthetic", clean["qualification"])
        self.assertEqual(clean["output_digest"],
                         "4e9ba0d5abe102f245c241c134c83bc45e1288c4d116a187051651d91dd450c1")
        self.assertEqual(clean["bypass_output_digest"],
                         "708c2d61cb22b615db564c01b13fb30e6478b67cd34172a7fa96354f6ad12648")

    def test_tone_rejection_in_speech(self):
        result = report()["results"]["tone_in_speech"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["injected_frequency_hz"], 1000)
        self.assertEqual(result["injected_frames"], 100)
        self.assertGreater(result["tone_reduction_db"], 15.0)
        self.assertEqual(result["output_digest"],
                         "85f7adbf5d07ee8f96ccaffa01db2d73a105126460a97e2fa3d358f7b366fa48")

    def test_load_control_is_counted_not_timed(self):
        result = report()["results"]["load_control"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["frames"], 2000)
        self.assertEqual(result["samples"], 320000)
        self.assertTrue(result["finite"])
        self.assertIn("none", result["timing_claim"])
        self.assertEqual(result["output_digest"],
                         "275f77fc62e3df16590f0ec5571c47ac7e93dfe70c77a9b5a371bf6d13fe7ded")

    def test_nonlinear_loop_interaction_controls(self):
        loops = report()["results"]["loop_nonlinear"]
        self.assertEqual(sorted(loops), ["1.05", "1.15", "1.3"])
        expected_digests = {
            ("1.05", "bypass"): "331f33106ec3dba77cc28706c2915ade192d03c23f87bbc22ea307f01f8d4a52",
            ("1.05", "notch"): "301996f23e96cf7938bfea317c880d2b75a5b9c09bde3e3c9d15addd52ce6ae0",
            ("1.05", "notch_plus_saturation"):
                "2ef37ba3111cdc51856932e97c713b57cb8b75eb4e3b67cb80226b107404fbb8",
            ("1.15", "bypass"): "8e9960af7f8b0cdaebe4aa59709010498d52274438596db1b4d94e408f1e290d",
            ("1.15", "notch"): "d2ce2591b685ac2b7e530a9b42d98bf2e0992b46a0ab44f803798861c04991f2",
            ("1.15", "notch_plus_saturation"):
                "2f16859f37e6269cd9309611b476921ffdb17338bb63f2d8e6eaf2ea3e13c0b2",
            ("1.3", "bypass"): "4e2ed2763259c1e423116e9e4dd9e4e9b2d05f2adb4bfdea7157f8fa1ab3d85d",
            ("1.3", "notch"): "f16c4bf4f0ad3be25471589e8315c299b820264725ae76e14569f4faf2bb2e0c",
            ("1.3", "notch_plus_saturation"):
                "fd7e8d9ea5f991a6cc528b862f37dcff7a8f996ded29327fea1ee371b6ae2ab2",
        }
        for gain, conditions in loops.items():
            self.assertEqual(sorted(conditions),
                             ["bypass", "notch", "notch_plus_saturation"])
            for name, result in conditions.items():
                self.assertEqual(result["nonfinite_frames"], 0, f"{gain}/{name}")
                self.assertEqual(result["output_digest"], expected_digests[(gain, name)])
            saturated = conditions["notch_plus_saturation"]
            self.assertLess(saturated["peak_abs_output"], 1.0, gain)
            self.assertEqual(saturated["rejected_frames"], 0, gain)
        self.assertLess(loops["1.05"]["notch"]["tail_db_relative_to_program"], -20.0)
        self.assertGreater(loops["1.15"]["bypass"]["tail_db_relative_to_program"], 20.0)

    def test_long_silence_and_impulse_train_stability(self):
        result = report()["results"]["long_stability"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["silence_frames"], 1000)
        self.assertEqual(result["impulse_train_frames"], 120)
        self.assertEqual(result["frames"], 1320)
        self.assertTrue(result["all_finite"])
        self.assertLess(result["peak_abs_output"], 1.0)
        self.assertLess(result["tail_rms"], 1e-6)
        self.assertEqual(result["frames_rejected"], 0)
        self.assertEqual(result["output_digest"],
                         "a9df5f0b3d5e8c618e04e0586eadf35e343e6aa340c8eea8a130dadaf56c693a")

    def test_state_isolation_across_sessions(self):
        result = report()["results"]["state_isolation"]
        self.assertTrue(result["distinct_states"])
        self.assertTrue(result["distinct_outputs"])
        self.assertEqual(result["reset_status"], "ok")
        self.assertTrue(result["reset_output_matches_fresh"])
        self.assertTrue(result["session_b_state_unchanged"])
        self.assertEqual(len(result["digest_a"]), 64)
        self.assertEqual(len(result["digest_b"]), 64)
        self.assertNotEqual(result["digest_a"], result["digest_b"])

    def test_stale_epoch_and_position_are_rejected(self):
        result = report()["results"]["epoch_and_position"]
        self.assertEqual(result["stale_epoch_status"], "rejected_epoch")
        self.assertEqual(result["stale_position_status"], "rejected_position")
        self.assertEqual(result["valid_epoch_status"], "ok")
        self.assertTrue(result["state_unchanged_after_rejects"])
        self.assertEqual(result["frames_processed"], 2)
        self.assertEqual(result["digest"],
                         "e233eab41591f71f825090cf6f2f075a1f165ee3ec681a9ec3ee1fbf7852a472")

    def test_adverse_controls_and_fail_closed_state(self):
        result = report()["results"]["adverse"]
        expected = {
            "nan_frequency": "rejected_nonfinite",
            "inf_frequency": "rejected_nonfinite",
            "nan_bandwidth": "rejected_nonfinite",
            "zero_bandwidth": "rejected_invalid",
            "zero_q": "rejected_invalid",
            "nan_q": "rejected_nonfinite",
            "inf_q": "rejected_nonfinite",
            "mismatched_q": "rejected_invalid",
            "high_frequency": "rejected_invalid",
            "bandwidth_above_frequency": "rejected_invalid",
            "missing_frequency": "rejected_missing",
            "wrong_type": "rejected_invalid",
        }
        self.assertEqual(result["config_statuses"], expected)
        self.assertEqual(result["coefficient_statuses"], {
            "nan_frequency": "rejected", "zero_bandwidth": "rejected",
            "nan_q": "rejected", "zero_q": "rejected"})
        self.assertEqual(result["nan_frame_status"], "rejected_nonfinite")
        self.assertEqual(result["inf_frame_status"], "rejected_nonfinite")
        self.assertEqual(result["short_frame_status"], "rejected_tensor")
        self.assertEqual(result["long_frame_status"], "rejected_tensor")
        self.assertEqual(result["out_of_range_frame_status"], "rejected_invalid")
        self.assertTrue(result["state_unchanged"])
        self.assertEqual(result["frames_processed"], 5)

    def test_lifecycle_transitions(self):
        result = report()["results"]["lifecycle"]
        self.assertEqual(result["close_status"], "ok")
        self.assertEqual(result["double_close_status"], "closed")
        self.assertEqual(result["process_after_close"], "closed")
        self.assertEqual(result["reset_after_close"], "closed")
        self.assertTrue(any("created@epoch" in item for item in result["transitions"]))
        self.assertIn("closed", result["transitions"])

    def test_no_missing_result_and_incomplete_qualification(self):
        data = report()
        required = {
            "silence", "impulse", "step", "chirp", "frequency_sweep",
            "center_bandwidth_controls", "attack_release", "clean_speech",
            "tone_in_speech", "load_control", "loop_nonlinear", "long_stability",
            "state_isolation", "epoch_and_position", "adverse", "lifecycle",
        }
        self.assertEqual(set(data["results"]), required)
        self.assertTrue(all(value is not None for value in data["results"].values()))
        self.assertEqual(data["counts"]["conditions"], len(required))
        self.assertEqual(data["status"], "proposal-only-synthetic")
        self.assertEqual(data["qualification"]["status"], "incomplete")
        for gate in ("real_speech", "listening", "nonlinear_interaction",
                     "device", "release"):
            self.assertIn(gate, data["qualification"])
            self.assertIn(data["qualification"][gate]["status"],
                          {"blocked", "incomplete"})
            self.assertTrue(data["qualification"][gate]["reason"])
        self.assertEqual(len(data["blockers"]), 3)
        self.assertNotIn("installed", data["qualification"]["release"]["status"])

    def test_optional_scope_is_declared(self):
        self.assertEqual(CONTRACT["status"], "optional-task-local-reference")
        self.assertTrue(any("task-local" in item.lower() for item in CONTRACT["invariants"]))
        self.assertEqual(CONTRACT["public_boundary"]["registration"],
                         "explicit caller-side registration only; no installed registry entry")
        self.assertEqual(CONTRACT["provider"]["required_assets"], [])
        self.assertEqual(CONTRACT["provider"]["buffering_delay_samples"], 0)

    def test_canonical_report_and_byte_identical_regeneration(self):
        generated = fixture.build_report()
        text, digest = fixture.canonical_report(generated)
        self.assertEqual(text, REPORT_ON_DISK)
        self.assertEqual(digest, REPORT_DIGEST)
        self.assertEqual(generated["fixture_digest"], FIXTURE_DIGEST)
        self.assertEqual(sha256_file(HERE / "report.json"), REPORT_DIGEST)


if __name__ == "__main__":
    unittest.main()
