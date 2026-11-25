# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest suite for the task-local inverse-EQ evidence."""

from __future__ import annotations

from itertools import islice
import math
from pathlib import Path
import tempfile
import unittest

import check_licensing
import fixture
import reference
import run
import scorer

ROOT = Path(__file__).resolve().parent
REPORT = scorer.read_strict_json(ROOT / "report.json")
CONTRACT = scorer.read_strict_json(ROOT / "contract.json")
ADAPTER = scorer.read_strict_json(ROOT / "adapter.json")
PROVIDER = scorer.read_strict_json(ROOT / "provider.json")
COHORT = fixture.cohort()
MODEL = reference.learned_model()
RESPONSE_FIXTURE = reference.response_fixture()
ILL = reference.ill_conditioned_case(MODEL["weights"])


def request(operation: str, control: str = "learned_inverse", samples=None,
            stimulus_id: str = "impulse") -> dict:
    common = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": {"kind": "task-local", "id": "learned-inverse-eq", "revision": 1},
        "adapter_ref": {"kind": "task-local", "id": "learned-inverse-eq", "revision": 1},
        "configuration": {"control": control},
    }
    if operation == "run":
        common.update({"attempt_id": "a1", "stimulus_id": stimulus_id, "samples": samples})
    return common


class FrozenFixtureTests(unittest.TestCase):
    def test_01_lcg_is_reproducible(self):
        first = list(islice(reference.lcg(12345), 8))
        second = list(islice(reference.lcg(12345), 8))
        self.assertEqual(first, second)
        self.assertNotEqual(first[0], next(reference.lcg(12346)))

    def test_02_forward_gains_are_frozen(self):
        self.assertEqual(reference.FORWARD_GAINS_DB, (-6.0, 4.0, -3.0, 5.0, -4.0, 3.0))

    def test_03_fixture_digest_is_pinned(self):
        self.assertEqual(RESPONSE_FIXTURE["sha256"],
                         "3226c4224ac33e0a88c0ab9db732d9e6c2c055fba1f95e20c75f2ba21a30389f")
        self.assertEqual(RESPONSE_FIXTURE["seed"], reference.FIXTURE_SEED)

    def test_04_training_row_count(self):
        self.assertEqual(len(RESPONSE_FIXTURE["training_rows"]), 12)
        self.assertEqual(RESPONSE_FIXTURE["training_rows"][0]["coefficients_db"],
                         list(reference.FORWARD_GAINS_DB))

    def test_05_coefficients_are_finite_and_stable(self):
        for stages in (reference.FORWARD_COEFFICIENTS,
                       reference.cascade_coefficients(MODEL["estimated_inverse_gains_db"])):
            for b0, b1, b2, a1, a2 in stages:
                self.assertTrue(all(math.isfinite(v) for v in (b0, b1, b2, a1, a2)))
                self.assertLess(abs(a2), 1.0)

    def test_06_coefficient_digest_is_stable(self):
        other = reference.learned_model()
        self.assertEqual(MODEL["coefficients_digest"], other["coefficients_digest"])
        self.assertEqual(len(MODEL["coefficients_digest"]), 64)

    def test_07_learned_gains_recover_frozen_inverse(self):
        self.assertLess(MODEL["max_abs_gain_error_db"], 0.1)
        self.assertEqual(len(MODEL["estimated_inverse_gains_db"]), 6)

    def test_08_training_residual_is_small(self):
        self.assertLess(MODEL["training_rmse_db"], 0.05)

    def test_09_response_error_improves_over_controls(self):
        response = REPORT["frozen_coefficients_and_responses"]["response_rmse_db"]
        self.assertLess(response["learned_inverse"], response["identity"])
        self.assertLess(response["learned_inverse"], response["fixed_eq"])
        probes = reference.PROBE_FREQUENCIES_HZ
        forward = reference.cascade_response_db(reference.FORWARD_COEFFICIENTS, probes)
        correction = reference.cascade_response_db(reference.cascade_coefficients(
            MODEL["estimated_inverse_gains_db"]), probes)
        corrected = [a + b for a, b in zip(forward, correction)]
        direct = scorer.response_rmse_db(corrected, [0.0] * len(probes))
        self.assertLess(abs(direct - response["learned_inverse"]), 1e-8)

    def test_10_analytic_response_matches_filtered_sine(self):
        stages = reference.cascade_coefficients((3.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        frequency = 250.0
        length = reference.FRAME_SAMPLES * 40
        sine = tuple(0.2 * math.sin(2.0 * math.pi * frequency * index
                                    / reference.SAMPLE_RATE_HZ) for index in range(length))
        output = reference.apply_cascade(sine, stages)
        measured = scorer.safe_db(scorer.rms(output[reference.FRAME_SAMPLES:])
                                  / scorer.rms(sine[reference.FRAME_SAMPLES:]))
        analytic = reference.cascade_response_db(stages, (frequency,))[0]
        self.assertLess(abs(measured - analytic), 0.15)


class ControllerTests(unittest.TestCase):
    def test_11_identity_is_bit_exact(self):
        stimulus = COHORT["clean_speech"]
        self.assertEqual(reference.stream(stimulus, "identity")["output"], stimulus)

    def test_12_fixed_eq_matches_forward_cascade(self):
        stimulus = COHORT["clean_speech_perturbed"]
        streamed = reference.stream(stimulus, "fixed_eq")["output"]
        direct = reference.apply_cascade(stimulus, reference.FORWARD_COEFFICIENTS)
        self.assertEqual(streamed, direct)

    def test_13_zero_added_delay(self):
        stimulus = COHORT["impulse"]
        output = reference.stream(stimulus, "learned_inverse",
                                  gains_db=MODEL["estimated_inverse_gains_db"])["output"]
        self.assertEqual(scorer.delay_samples(stimulus, output), 0)

    def test_14_silence_stays_silent(self):
        output = reference.stream(COHORT["silence"], "learned_inverse",
                                  gains_db=MODEL["estimated_inverse_gains_db"])["output"]
        self.assertEqual(scorer.peak(output), 0.0)
        self.assertTrue(all(math.isfinite(value) for value in output))

    def test_15_framewise_equals_whole_call(self):
        stimulus = COHORT["sweep_clean"]
        streamed = reference.stream(stimulus, "learned_inverse",
                                    gains_db=MODEL["estimated_inverse_gains_db"])["output"]
        direct = reference.apply_cascade(stimulus, reference.cascade_coefficients(
            MODEL["estimated_inverse_gains_db"]))
        self.assertEqual(streamed, direct)

    def test_16_partial_final_frame_keeps_length(self):
        result = reference.Controller("learned_inverse").process((0.1,) * 37, final=True)
        self.assertEqual(result.status, "ok")
        self.assertEqual(len(result.samples), 37)

    def test_17_missing_frame_rejected(self):
        controller = reference.Controller("learned_inverse")
        before = controller.dsp_state_digest()
        result = controller.process(None)
        self.assertEqual(result.error, "missing_frame")
        self.assertEqual(controller.dsp_state_digest(), before)

    def test_18_wrong_shape_rejected(self):
        controller = reference.Controller("learned_inverse")
        self.assertEqual(controller.process((0.0,) * 12).error, "partial_frame_without_final")
        self.assertEqual(controller.process((0.0,) * (reference.FRAME_SAMPLES - 1)).error,
                         "partial_frame_without_final")
        self.assertEqual(controller.process((0.0,) * (reference.FRAME_SAMPLES + 1)).error,
                         "invalid_frame_length")

    def test_19_nonfinite_rejected(self):
        controller = reference.Controller("learned_inverse")
        frame = (float("nan"),) + (0.0,) * (reference.FRAME_SAMPLES - 1)
        self.assertEqual(controller.process(frame).error, "nonfinite_input")
        self.assertEqual(controller.invalid_count, 1)

    def test_20_out_of_range_rejected(self):
        controller = reference.Controller("learned_inverse")
        self.assertEqual(controller.process((3.0,) + (0.0,) * 159).error,
                         "out_of_range_input")

    def test_21_stale_epoch_rejected(self):
        controller = reference.Controller("learned_inverse", epoch=2)
        frame = (0.1,) * reference.FRAME_SAMPLES
        self.assertEqual(controller.process(frame, epoch=3).error, "stale_epoch")

    def test_22_stale_position_rejected(self):
        controller = reference.Controller("learned_inverse", position=8)
        frame = (0.1,) * reference.FRAME_SAMPLES
        self.assertEqual(controller.process(frame, position=9).error, "stale_position")

    def test_23_reset_replays_exactly(self):
        frame = COHORT["impulse"][:reference.FRAME_SAMPLES]
        first = reference.Controller("learned_inverse")
        second = reference.Controller("learned_inverse")
        for _ in range(4):
            first.process(frame)
        for _ in range(4):
            second.process(frame)
        self.assertEqual(first.state_digest(), second.state_digest())
        first.reset(1)
        second.reset(1)
        for _ in range(4):
            first.process(frame, epoch=1)
            second.process(frame, epoch=1)
        self.assertEqual(first.state_digest(), second.state_digest())

    def test_24_non_monotonic_reset_rejected(self):
        controller = reference.Controller("learned_inverse")
        controller.process((0.1,) * reference.FRAME_SAMPLES)
        with self.assertRaises(ValueError):
            controller.reset(0)

    def test_25_clipped_input_is_explicit(self):
        stimulus = COHORT["clipped_input"]
        self.assertGreater(scorer.peak(stimulus), 1.0)
        result = reference.stream(stimulus, "learned_inverse",
                                  gains_db=MODEL["estimated_inverse_gains_db"])
        self.assertEqual(result["status"], "complete")
        self.assertTrue(scorer.is_finite(result["output"]))


class ReportTests(unittest.TestCase):
    def test_26_status_is_proposal_only(self):
        self.assertEqual(REPORT["status"], "proposal_only_not_qualified")
        self.assertEqual(REPORT["qualification"], "incomplete")

    def test_27_decision_defers_exposure(self):
        self.assertEqual(REPORT["decision"], CONTRACT["decision"])
        for key in ("expose_as_processor", "registered", "default_enabled",
                    "public_api_abi_change", "descriptor_registry_change", "release_claim"):
            self.assertIs(REPORT["decision"][key], False)
        self.assertEqual(PROVIDER["exposure_decision"], "deferred")

    def test_28_all_comparisons_finite_and_nonqualifying(self):
        for name, rows in REPORT["comparisons"].items():
            for mode, row in rows.items():
                self.assertEqual(row["status"], "complete", (name, mode))
                self.assertTrue(row["finite"], (name, mode))
                self.assertIs(row["qualifies"], False, (name, mode))

    def test_29_identity_is_bit_exact_in_report(self):
        self.assertTrue(REPORT["controls"]["identity_is_bit_exact"])

    def test_30_report_regeneration_is_byte_identical(self):
        text, digest = reference.canonical_report(run.report_with_pins())
        self.assertEqual(text.encode("utf-8") + b"\n", (ROOT / "report.json").read_bytes())
        self.assertEqual((ROOT / "report.json.sha256").read_text(encoding="ascii"),
                         digest + "\n")

    def test_31_crosscheck_regeneration_is_byte_identical(self):
        rendered = scorer.canonical_text(reference.crosscheck_vectors()) + "\n"
        self.assertEqual(rendered, (ROOT / "crosscheck_vectors.json").read_text(encoding="utf-8"))

    def test_32_sources_manifest_matches_tree(self):
        expected = []
        for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
            if not path.is_file() or "__pycache__" in path.parts or path.name == "SOURCES.sha256":
                continue
            expected.append(scorer.digest_bytes(path.read_bytes()) + "  "
                            + path.relative_to(ROOT).as_posix() + "\n")
        self.assertEqual("".join(expected), (ROOT / "SOURCES.sha256").read_text(encoding="utf-8"))

    def test_33_fixture_spec_digest_pinned(self):
        spec = fixture.fixture_spec()
        self.assertEqual(spec["sha256"], REPORT["fixture"]["sha256"])
        self.assertEqual(len(spec["signals"]),
                         1 + 2 * len(fixture.COMPARISON_CONDITIONS) + len(fixture.DSP_CONDITIONS))

    def test_34_ill_condition_is_explicit(self):
        condition = REPORT["dsp_profile"]["ill_conditioned_inverse"]
        self.assertGreater(condition["condition"]["condition_estimate"], 1e6)
        self.assertIs(condition["qualifies"], False)

    def test_35_out_of_band_amplification_is_explicit(self):
        adverse = REPORT["dsp_profile"]["adverse_out_of_band_amplification"]
        self.assertGreater(adverse["ill_conditioned_amplification_db"],
                           adverse["nominal_amplification_db"] + 6.0)
        self.assertIs(adverse["qualifies"], False)

    def test_36_nonlinear_ablation_recorded(self):
        nonlinear = REPORT["dsp_profile"]["nonlinear_and_state_interaction"]
        self.assertEqual(set(nonlinear["ablations"]), {
            "no_learned_inverse", "no_level_tone_control", "full_chain"})
        self.assertIs(nonlinear["qualifies"], False)
        self.assertEqual(nonlinear["nonfinite_count"], 0)

    def test_37_level_tone_attack_and_release_recorded(self):
        nonlinear = REPORT["dsp_profile"]["nonlinear_and_state_interaction"]
        self.assertGreater(nonlinear["gain_trace_peak"], nonlinear["gain_trace_min"])
        self.assertGreater(nonlinear["release_frames_after_peak"], 0)
        self.assertGreaterEqual(nonlinear["attack_peak_frame"], 0)

    def test_38_invalid_controls_do_not_change_dsp_state(self):
        controls = REPORT["controls"]["invalid_and_missing"]
        self.assertEqual(len(controls), 7)
        for row in controls.values():
            self.assertEqual(row["status"], "rejected")
            self.assertTrue(row["dsp_state_unchanged"])
            self.assertEqual(row["invalid_count_delta"], 1)

    def test_39_source_and_boundary_pins_match(self):
        self.assertEqual(CONTRACT["source_pins"], REPORT["source_pins"])
        self.assertEqual(CONTRACT["boundary_pins"], REPORT["boundary_pins"])

    def test_40_strict_json_rejects_duplicates_and_nan(self):
        with tempfile.TemporaryDirectory() as directory:
            duplicate = Path(directory) / "duplicate.json"
            duplicate.write_text('{"a":1,"a":2}\n', encoding="utf-8")
            with self.assertRaises(scorer.StrictJSONError):
                scorer.read_strict_json(duplicate)
            nonfinite = Path(directory) / "nonfinite.json"
            nonfinite.write_text('{"a":NaN}\n', encoding="utf-8")
            with self.assertRaises(scorer.StrictJSONError):
                scorer.read_strict_json(nonfinite)

    def test_41_adapter_inspect_is_valid(self):
        result = run.inspect(request("inspect"))
        self.assertEqual(result["identity"], ADAPTER["identity"])
        self.assertEqual(result["supported_controls"], ADAPTER["controls"])

    def test_42_adapter_run_is_complete(self):
        result = run.run(request("run"))
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["output"]["channels"], 1)
        self.assertEqual(result["output"]["sample_rate_hz"], 16000)

    def test_43_adapter_rejects_bad_control_and_extra_field(self):
        with self.assertRaises(run.RequestError):
            run.inspect(request("inspect", control="unknown"))
        broken = request("inspect")
        broken["extra"] = 1
        with self.assertRaises(run.RequestError):
            run.inspect(broken)

    def test_44_no_missing_result_qualifies(self):
        self.assertTrue(REPORT["controls"]["no_missing_result_qualifies"])
        self.assertTrue(REPORT["scope"]["external_model_or_weights"] is False)
        self.assertTrue(REPORT["scope"]["real_speech_or_listening"] is False)

    def test_45_licensing_check_is_green(self):
        self.assertEqual(check_licensing.check()["status"], "ok")

    def test_46_crosscheck_pin_matches_report(self):
        vectors = scorer.read_strict_json(ROOT / "crosscheck_vectors.json")
        self.assertEqual(vectors["sha256"], REPORT["crosscheck"]["content_digest"])
        self.assertEqual(REPORT["crosscheck"]["file_sha256_at_build"],
                         scorer.digest_bytes((ROOT / "crosscheck_vectors.json").read_bytes()))

    def test_47_gain_error_smaller_than_controls(self):
        for rows in REPORT["comparisons"].values():
            learned = abs(rows["learned_inverse"]["gain_error_db"])
            self.assertLess(learned, abs(rows["identity"]["gain_error_db"]) + 0.1)
            self.assertLess(learned, abs(rows["fixed_eq"]["gain_error_db"]) + 0.1)

    def test_48_dsp_conditions_covered(self):
        names = set(REPORT["dsp_profile"]["conditions"])
        self.assertEqual(names, set(fixture.DSP_CONDITIONS))
        for row in REPORT["dsp_profile"]["conditions"].values():
            self.assertTrue(row["output_finite"])
            self.assertEqual(row["nonfinite_count"], 0)


if __name__ == "__main__":
    unittest.main()
