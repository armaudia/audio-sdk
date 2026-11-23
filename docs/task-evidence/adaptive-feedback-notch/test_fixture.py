import hashlib
import json
import unittest
from pathlib import Path

import fixture

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
AUDIOML_ROOT = REPO_ROOT.parents[2]

CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
REPORT_ON_DISK = (HERE / "report.json").read_text(encoding="utf-8")

REPORT_DIGEST = "7ac0a069736bd8d14212c3cbbcc288a632524d75a95b3f1afd9e73572118ff73"
FIXTURE_DIGEST = "0779923ef1160b64a0f3da9354c145e7108a9b7720a13136aff7b28d36da844d"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report() -> dict:
    return json.loads(REPORT_ON_DISK)


class AdaptiveNotchFixtureTest(unittest.TestCase):
    def test_source_pins_and_v0_format(self):
        self.assertEqual(fixture.CONTRACT_ID, CONTRACT["schema_id"])
        self.assertEqual(fixture.SAMPLE_RATE_HZ, 16000)
        self.assertEqual(fixture.FRAME_SAMPLES, 160)
        self.assertEqual(len(fixture.FREQUENCIES_HZ), 39)
        self.assertEqual(fixture.FREQUENCIES_HZ[0], 200)
        self.assertEqual(fixture.FREQUENCIES_HZ[-1], 4000)
        self.assertEqual(fixture.SOURCE_PINS, CONTRACT["source_pins"])
        self.assertEqual(fixture.BOUNDARY_PINS, CONTRACT["boundary_pins"])
        self.assertEqual(fixture.BOARD_SNAPSHOT, CONTRACT["board_snapshot"])
        self.assertEqual(fixture.DEFAULT_CONFIG, CONTRACT["reference_controls"])

    def test_pinned_source_files_when_present(self):
        pins = [(AUDIOML_ROOT / path, digest)
                for path, digest in fixture.SOURCE_PINS.items()]
        pins.extend((REPO_ROOT / path, digest)
                    for path, digest in fixture.BOUNDARY_PINS.items())
        for source, digest in pins:
            if not source.exists():
                self.skipTest(f"external source not present here: {source}")
            self.assertEqual(sha256_file(source), digest, str(source))

    def test_board_snapshot_is_not_a_qualification_gate(self):
        self.assertTrue(CONTRACT["board_snapshot"]["mutable"])
        self.assertEqual(len(CONTRACT["board_snapshot"]["sha256_at_read"]), 64)
        self.assertNotIn(CONTRACT["board_snapshot"]["path"], CONTRACT["source_pins"])

    def test_pinned_local_artifacts(self):
        for relative_path, digest in CONTRACT["artifact_pins"].items():
            path = HERE / relative_path
            self.assertTrue(path.exists(), relative_path)
            self.assertEqual(sha256_file(path), digest, relative_path)

    def test_config_validation_missing_invalid_and_nonfinite(self):
        status = fixture.validate_config(None)
        self.assertEqual(status, fixture.Status.REJECTED_MISSING)
        missing = fixture.config_with()
        del missing["q"]
        self.assertEqual(fixture.validate_config(missing), fixture.Status.REJECTED_MISSING)
        self.assertEqual(fixture.validate_config(fixture.config_with(q=float("nan"))),
                         fixture.Status.REJECTED_NONFINITE)
        self.assertEqual(fixture.validate_config(fixture.config_with(q=float("inf"))),
                         fixture.Status.REJECTED_NONFINITE)
        self.assertEqual(fixture.validate_config(fixture.config_with(q=1.0)),
                         fixture.Status.REJECTED_INVALID)
        bad_type = fixture.config_with(persistence_frames="4")
        self.assertEqual(fixture.validate_config(bad_type), fixture.Status.REJECTED_INVALID)
        unknown = fixture.config_with(unexpected=1)
        self.assertEqual(fixture.validate_config(unknown), fixture.Status.REJECTED_INVALID)
        status, instance = fixture.AdaptiveNotchController.create(None)
        self.assertEqual(status, fixture.Status.REJECTED_MISSING)
        self.assertIsNone(instance)

    def test_silence_and_impulse_delay(self):
        results = report()["results"]
        silence = results["silence"]
        self.assertEqual(silence["status"], "ok")
        self.assertEqual(silence["activations"], 0)
        self.assertEqual(silence["peak_abs_output"], 0.0)
        self.assertEqual(silence["output_digest"],
                         "c65206769723a13afe80c0d925531639ceef9c2eb97eee3b1b542739ec40597f")
        impulse = results["impulse"]
        self.assertEqual(impulse["status"], "ok")
        self.assertEqual(impulse["peak_index"], 0)
        self.assertEqual(impulse["peak_abs_output"], 0.5)
        self.assertEqual(impulse["output_digest"],
                         "ce07c8c9dc23807c039f14a4adf42e25aa2f5c5998ad8b627bd8a3b67ebc7468")

    def test_step_response_and_headroom(self):
        step = report()["results"]["step"]
        self.assertEqual(step["status"], "ok")
        self.assertEqual(step["crossing_samples"], 0)
        self.assertEqual(step["peak_abs_output"], 0.25)
        self.assertEqual(step["output_digest"],
                         "5f79d1e49ae19f9e73ab04866e258a3c5798429263d1c33d9af248da5a476cca")

    def test_sweep_response(self):
        sweep = report()["results"]["sweep"]
        self.assertEqual(sweep["frames_per_frequency"], 12)
        self.assertEqual(sweep["activated_frequencies"], 39)
        self.assertEqual(len(sweep["per_frequency"]), 39)
        self.assertLess(sweep["min_gain"], 0.2)
        self.assertLess(sweep["max_gain"], 0.2)
        self.assertTrue(all(item["activated"] for item in sweep["per_frequency"]))
        self.assertEqual(sweep["output_digest"],
                         "1f1d4df671abb4811a54d88360836f3d535906729819305bde3626dc3d7288c0")

    def test_attack_release_and_state_transitions(self):
        result = report()["results"]["attack_release"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["attack_frames"], 3)
        self.assertEqual(result["release_frames"], 23)
        self.assertEqual(result["activations"], 1)
        self.assertEqual(result["releases"], 1)
        self.assertEqual(result["transitions"],
                         ["idle->active@23:1000", "active->idle@143:1000"])
        self.assertEqual(result["output_digest"],
                         "a8ec5914d8354b5cd594d993002ba3ba45592a96ee4fb0dc51fd20952735502b")

    def test_false_notch_activations_on_speech(self):
        results = report()["results"]
        clean = results["clean_speech"]
        self.assertEqual(clean["status"], "ok")
        self.assertEqual(clean["frames"], 300)
        self.assertEqual(clean["false_activations"], 0)
        self.assertEqual(clean["false_activation_rate_per_minute"], 0.0)
        self.assertEqual(clean["gain_margin_activations"], 0)
        self.assertEqual(clean["output_digest"],
                         "76587b604530a569eeb771a57ac5367567b2eeecdbf735d5f8a29d57ce0f77cf")
        tonal = results["tonal_vowel_stress"]
        self.assertEqual(tonal["status"], "ok")
        self.assertEqual(tonal["false_activations"], 3)
        self.assertEqual(tonal["false_activation_rate_per_minute"], 6.0)
        self.assertEqual(tonal["output_digest"],
                         "ee10d8160a2221d0f3eda7edb002e8e33ea8891a91c49f00bd8c68a0e52ac054")

    def test_tone_artifact_rate_control(self):
        result = report()["results"]["tone_artifacts"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["activations_in_tone_region"], 1)
        self.assertEqual(result["false_activations_clean_region"], 0)
        self.assertAlmostEqual(result["tone_absolute_db_reduction"], 12.693, places=3)
        self.assertGreater(result["tone_to_total_db_before"],
                           result["tone_to_total_db_after"])
        self.assertEqual(result["clean_region_tone_db_before"],
                         result["clean_region_tone_db_after"])
        self.assertEqual(result["output_digest"],
                         "677b33fe46dbfd729789645f144ac90931caa93a23c9b33ca2d8e409d2ac8add")

    def test_loop_stability_controls(self):
        loops = report()["results"]["loop_stability"]
        self.assertEqual(sorted(loops), ["1.05", "1.15", "1.3"])
        for gain, conditions in loops.items():
            self.assertGreater(conditions["identity"]["tail_db_relative_to_program"], 20.0,
                               gain)
            self.assertEqual(conditions["identity"]["activations"], 0)
            self.assertLess(conditions["fixed_margin"]["tail_db_relative_to_program"], -20.0,
                            gain)
            self.assertEqual(conditions["fixed_margin"]["rejected_frames"], 0, gain)
            saturated = conditions["notch_plus_saturation"]
            self.assertLess(saturated["tail_db_relative_to_program"], -100.0, gain)
            self.assertEqual(saturated["rejected_frames"], 0, gain)
            self.assertEqual(saturated["nonfinite_frames"], 0, gain)
            self.assertGreater(saturated["activations"], 0, gain)
            self.assertLess(saturated["peak_abs_output"], 0.8, gain)
        self.assertEqual(loops["1.05"]["notch_only"]["rejected_frames"], 20)
        self.assertEqual(loops["1.3"]["notch_plus_margin"]["rejected_frames"], 42)
        for gain, conditions in loops.items():
            for name, result in conditions.items():
                self.assertEqual(result["nonfinite_frames"], 0, f"{gain}/{name}")

    def test_invalid_frames_leave_state_unchanged(self):
        controller = fixture.AdaptiveNotchController(fixture.config_with())
        controller.process_stream(fixture.tone(10))
        before = controller.state.digest()
        self.assertEqual(controller.process((float("nan"),) * fixture.FRAME_SAMPLES).status,
                         fixture.Status.REJECTED_NONFINITE)
        self.assertEqual(controller.state.digest(), before)
        self.assertEqual(controller.process((9.0,) * fixture.FRAME_SAMPLES).status,
                         fixture.Status.REJECTED_INVALID)
        self.assertEqual(controller.process((0.0,) * 159).status,
                         fixture.Status.REJECTED_TENSOR)
        invalid = report()["results"]["invalid_controls"]
        self.assertEqual(invalid["nonfinite_status"], "rejected_nonfinite")
        self.assertEqual(invalid["out_of_range_status"], "rejected_invalid")
        self.assertEqual(invalid["short_frame_status"], "rejected_tensor")
        self.assertTrue(invalid["state_unchanged"])

    def test_reset_and_close_are_explicit(self):
        controller = fixture.AdaptiveNotchController(fixture.config_with())
        controller.process_stream(fixture.tone(10))
        self.assertGreater(controller.state.activation_count, 0)
        self.assertEqual(controller.reset(), fixture.Status.OK)
        self.assertEqual(controller.state.activation_count, 0)
        self.assertEqual(controller.state.digest(), fixture.ControllerState().digest())
        controller.close()
        controller.close()
        result = controller.process((0.0,) * fixture.FRAME_SAMPLES)
        self.assertEqual(result.status, fixture.Status.CLOSED)
        self.assertEqual(controller.reset(), fixture.Status.CLOSED)

    def test_canonical_report_and_fixture_digests(self):
        generated = fixture.build_report()
        text, digest = fixture.canonical_report(generated)
        self.assertEqual(text, REPORT_ON_DISK)
        self.assertEqual(digest, REPORT_DIGEST)
        self.assertEqual(generated["fixture_digest"], FIXTURE_DIGEST)
        self.assertEqual(sha256_file(HERE / "report.json"), REPORT_DIGEST)


if __name__ == "__main__":
    unittest.main()
