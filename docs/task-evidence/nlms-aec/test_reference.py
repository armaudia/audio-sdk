# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest coverage for the task-local NLMS AEC reference."""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
import unittest

import reference
import run as adapter

ROOT = pathlib.Path(__file__).resolve().parent
FRAME = reference.FRAME_SAMPLES


class ReportFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def mic_ref(self, name="double_talk"):
        data = reference.fixture(name)
        return data["microphone"], data["reference"]


class ConfigAndAdverseTests(ReportFixture):
    def test_01_config_validation(self):
        for kwargs in ({"filter_taps": 0}, {"filter_taps": 1.5},
                       {"step_size": 0.0}, {"step_size": float("inf")},
                       {"epsilon": -1e-9}, {"max_abs_input": 0},
                       {"double_talk_threshold": 2.0},
                       {"double_talk_hold": 1}):
            with self.assertRaises(reference.ConfigError):
                reference.NlmsConfig(**kwargs)
        config = reference.NlmsConfig()
        self.assertEqual(config.as_dict()["filter_taps"], reference.FILTER_TAPS)

    def test_02_invalid_frame_rejections_leave_state_unchanged(self):
        engine = reference.NlmsAec()
        frame = (0.1,) * FRAME
        ref = (0.05,) * FRAME
        engine.process(frame, ref)
        before = engine.state_digest()
        invalid = [
            engine.process((float("nan"),) * FRAME, ref).status,
            engine.process((float("inf"),) * FRAME, ref).status,
            engine.process((5.0,) * FRAME, ref).status,
            engine.process((0.1,) * 8, ref).status,
            engine.process(frame, (float("nan"),) * FRAME).status,
            engine.process(frame, (0.05,) * 8).status,
            engine.process(frame, ref, epoch=2).status,
            engine.process(frame, ref, first_sample=161).status,
        ]
        self.assertTrue(all(status.startswith("rejected") for status in invalid))
        self.assertEqual(engine.state_digest(), before)
        self.assertEqual(engine.invalid_count, 8)

    def test_03_missing_reference_passthrough_is_not_adaptive(self):
        engine = reference.NlmsAec()
        frame = tuple(0.1 * math.sin(i / 7.0) for i in range(FRAME))
        result = engine.process(frame, None)
        self.assertEqual(result.status, "no_reference_passthrough")
        self.assertEqual(result.samples, frame)
        self.assertEqual(engine.state_digest(),
                         hashlib.sha256(b"\x00" * 8 * reference.FILTER_TAPS).hexdigest())
        self.assertEqual(engine.reference_frames, 0)
        self.assertEqual(engine.no_reference_frames, 1)

    def test_04_reset_epoch_and_partial_final_frame(self):
        engine = reference.NlmsAec()
        self.assertEqual(engine.reset(9, 320), None)
        self.assertEqual(engine.epoch, 9)
        self.assertEqual(engine.next_sample, 320)
        self.assertTrue(engine.process((0.1,) * FRAME, (0.05,) * FRAME,
                                       epoch=8).status.startswith("rejected"))
        result = engine.process((0.1,) * 37, (0.05,) * 37, final=True,
                                first_sample=320)
        self.assertEqual(len(result.samples), 37)
        self.assertEqual(engine.next_sample, 357)
        with self.assertRaises(reference.ConfigError):
            engine.reset(8, 0)

    def test_05_independent_sessions_and_determinism(self):
        mic, ref = self.mic_ref("delay_change")
        engine_a = reference.NlmsAec()
        engine_b = reference.NlmsAec()
        for start in range(0, 20 * FRAME, FRAME):
            engine_a.process(mic[start:start + FRAME], ref[start:start + FRAME])
            engine_b.process(mic[start:start + FRAME], ref[start:start + FRAME])
        self.assertEqual(engine_a.state_digest(), engine_b.state_digest())
        engine_c = reference.NlmsAec()
        engine_c.process((0.3,) * FRAME, (0.2,) * FRAME)
        self.assertNotEqual(engine_a.state_digest(), engine_c.state_digest())

    def test_06_frame_and_sample_paths_agree(self):
        self.assertTrue(self.report["state"]["framewise_equals_samplewise"])
        self.assertTrue(self.report["state"]["framewise_equals_samplewise_state"])
        self.assertTrue(self.report["state"]["deterministic_output_digest"])
        self.assertTrue(self.report["state"]["deterministic_state_digest"])


class FixtureAndAlignmentTests(ReportFixture):
    def test_07_fixture_is_deterministic(self):
        first = reference.fixture("double_talk")
        second = reference.fixture("double_talk")
        for key in ("microphone", "reference", "echo", "near", "playback"):
            self.assertEqual(reference.tensor_digest(first[key]),
                             reference.tensor_digest(second[key]))

    def test_08_explicit_reference_latency_measured(self):
        alignment = self.report["alignment"]
        self.assertEqual(alignment["measured_lag_samples"],
                         alignment["intended_primary_tap_delay_samples"])
        self.assertEqual(alignment["alignment_error_samples"], 0)
        self.assertEqual(alignment["delayed_render_misalignment_samples"],
                         reference.DELAYED_RENDER_SAMPLES)
        self.assertEqual(alignment["algorithmic_delay_samples"], 0)

    def test_09_fixture_digests_present(self):
        for name, digests in self.report["fixture_digests"].items():
            self.assertEqual(len(digests["microphone"]), 64)
            self.assertIsNotNone(digests["playback"])
            self.assertIsNotNone(digests["echo"])

    def test_10_impulse_step_and_silence(self):
        dsp = self.report["dsp_controls"]
        self.assertEqual(dsp["impulse"]["detail"]["peak_sample_index"],
                         reference.PATH_A[0][0] + 10 * FRAME)
        self.assertEqual(dsp["step"]["detail"]["first_nonzero_sample_index"],
                         dsp["step"]["detail"]["expected_sample_index"])
        self.assertEqual(dsp["silence"]["detail"]["peak_abs"], 0.0)
        self.assertEqual(dsp["silence"]["detail"]["nonzero_count"], 0)

    def test_11_analytic_stimuli_are_zero_delay(self):
        for name in ("impulse", "step", "silence"):
            data = reference.stimulus(name)
            self.assertEqual(len(data["microphone"]), reference.TOTAL_SAMPLES)
            self.assertEqual(data["reference_mode"], "explicit_playback")


class MetricTests(ReportFixture):
    def test_12_single_talk_convergence(self):
        metrics = self.report["runs"]["single_talk"]["metrics"]
        self.assertGreater(metrics["single_talk_erle_db"], 20.0)
        self.assertLess(metrics["early_single_talk_erle_db"],
                        metrics["single_talk_erle_db"])
        self.assertLess(metrics["peak_abs"], 1.0)
        self.assertEqual(metrics["nonfinite_count"], 0)
        self.assertIsNone(metrics["double_talk_near_snr_db"])

    def test_13_double_talk_preserves_near_end(self):
        adaptive = self.report["runs"]["double_talk"]["metrics"]
        fixed = self.report["controls"]["fixed_attenuation_double_talk"]["metrics"]
        identity = self.report["controls"]["identity_double_talk"]["metrics"]
        self.assertGreater(adaptive["double_talk_near_snr_db"], 8.0)
        self.assertGreater(adaptive["double_talk_near_snr_db"],
                           fixed["double_talk_near_snr_db"])
        self.assertGreater(adaptive["double_talk_near_snr_db"],
                           identity["double_talk_near_snr_db"])

    def test_14_fixed_attenuation_separate_from_adaptive(self):
        self.assertTrue(self.report["fixed_attenuation_separate_from_adaptive"])
        for name in ("single_talk", "double_talk", "delay_change"):
            fixed = self.report["controls"]["fixed_attenuation_" + name]
            adaptive = self.report["runs"][name]
            self.assertFalse(fixed["qualifies"])
            self.assertEqual(fixed["variant"], "fixed_attenuation")
            self.assertNotEqual(fixed["output_digest"], adaptive["output_digest"])
            self.assertEqual(fixed["variant"], "fixed_attenuation")

    def test_15_echo_return_loss_and_gain_margin(self):
        adaptive = self.report["runs"]["single_talk"]["metrics"]
        fixed = self.report["controls"]["fixed_attenuation_single_talk"]["metrics"]
        self.assertEqual(adaptive["echo_return_loss_db"],
                         adaptive["single_talk_erle_db"])
        self.assertGreater(adaptive["gain_before_feedback_db"], 20.0)
        self.assertGreater(adaptive["gain_before_feedback_db"],
                           fixed["gain_before_feedback_db"])
        self.assertAlmostEqual(fixed["single_talk_erle_db"], 6.0206, places=3)

    def test_16_delay_change_and_reconvergence(self):
        metrics = self.report["runs"]["delay_change"]["metrics"]
        self.assertGreater(metrics["pre_change_erle_db"], 20.0)
        self.assertLess(metrics["post_change_early_erle_db"],
                        metrics["pre_change_erle_db"])
        self.assertGreater(metrics["post_change_late_erle_db"],
                           metrics["post_change_early_erle_db"])
        self.assertGreater(metrics["reconvergence_delta_db"], 1.0)
        self.assertLess(metrics["gain_before_feedback_db"],
                        self.report["runs"]["single_talk"]["metrics"]["gain_before_feedback_db"])

    def test_17_near_only_and_clean_speech_like(self):
        near_only = self.report["runs"]["near_only"]["metrics"]
        clean = self.report["dsp_controls"]["clean_speech_like_near_only"]
        self.assertGreater(near_only["double_talk_near_snr_db"], 20.0)
        self.assertGreater(clean["near_snr_db"], 20.0)
        self.assertEqual(clean["status"], "ok")

    def test_18_misaligned_delayed_and_dropout_do_not_qualify(self):
        for name, status in (("delayed_render", "misaligned_reference"),
                             ("reference_dropout", "partial_reference")):
            record = self.report["runs"][name]
            self.assertEqual(record["status"], status)
            self.assertFalse(record["qualifies"])
            self.assertIsNotNone(record["metrics"])
        missing = self.report["runs"]["missing_reference"]
        self.assertEqual(missing["status"], "blocked_no_reference")
        self.assertIsNone(missing["metrics"])
        self.assertFalse(missing["qualifies"])
        self.assertEqual(missing["no_reference_frames"],
                         reference.TOTAL_SAMPLES // FRAME)

    def test_19_no_missing_result_qualifies(self):
        for name, record in self.report["runs"].items():
            if record["qualifies"]:
                self.assertEqual(record["status"], "ok")
                self.assertIsInstance(record["metrics"], dict)
                self.assertIsNotNone(record["metrics"])

    def test_20_numerical_and_output_bounds(self):
        for name, record in {**self.report["runs"],
                             **self.report["controls"]}.items():
            metrics = record.get("metrics")
            if metrics is None:
                continue
            self.assertEqual(metrics["nonfinite_count"], 0)
            self.assertLessEqual(metrics["peak_abs"], 4.0)
            self.assertEqual(metrics["output_samples"], reference.TOTAL_SAMPLES)


class AdapterTests(ReportFixture):
    def _base_request(self, operation="inspect"):
        request = {
            "protocol_version": 1,
            "operation": operation,
            "candidate_ref": {"kind": "local", "id": "nlms-aec", "revision": 1},
            "adapter_ref": {"kind": "local", "id": "adapter", "revision": 1},
            "configuration": {"control": "nlms_adaptive"},
        }
        if operation == "run":
            request.update({"attempt_id": "attempt-1", "stimulus_id": "double_talk",
                            "samples": None, "reference_samples": None,
                            "reference_mode": "explicit"})
        return request

    def test_21_inspect_discloses_boundary(self):
        result = adapter.inspect(self._base_request())
        self.assertEqual(result["identity"], adapter.IDENTITY)
        self.assertIn("paired_render_reference", result["supported_modes"])
        self.assertEqual(result["algorithmic_delay_samples"], 0)

    def test_22_run_with_explicit_reference(self):
        result = adapter.run(self._base_request("run"))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"]["sample_rate_hz"], 16000)
        self.assertEqual(result["output"]["nonfinite_count"], 0)
        self.assertEqual(result["metrics"], None)
        self.assertFalse(result["qualifies"])

    def test_23_run_with_withheld_reference_is_blocked(self):
        request = self._base_request("run")
        request["reference_mode"] = "withheld"
        result = adapter.run(request)
        self.assertEqual(result["status"], "blocked_no_reference")
        self.assertEqual(result["metrics"], None)
        self.assertFalse(result["qualifies"])
        self.assertEqual(sum(result["output"]["frame_statuses"].values()),
                         reference.TOTAL_SAMPLES // FRAME)

    def test_24_request_validation(self):
        request = self._base_request("run")
        request["reference_mode"] = "unknown"
        with self.assertRaises(adapter.RequestError):
            adapter.run(request)
        request = self._base_request("run")
        request["configuration"] = {"control": "unknown"}
        with self.assertRaises(adapter.RequestError):
            adapter.run(request)
        request = self._base_request("run")
        request["samples"] = [float("nan")] * FRAME
        with self.assertRaises(adapter.RequestError):
            adapter.run(request)
        request = self._base_request("run")
        request["samples"] = [0.1] * FRAME
        request["reference_samples"] = [0.1] * (2 * FRAME)
        with self.assertRaises(adapter.RequestError):
            adapter.run(request)

    def test_25_report_regeneration_is_byte_identical(self):
        current = (ROOT / "report.json").read_bytes()
        rebuilt, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(current, (rebuilt + "\n").encode("utf-8"))
        self.assertEqual((ROOT / "report.json.sha256").read_text(encoding="ascii").strip(),
                         digest)

    def test_26_source_pins_match_files(self):
        workspace = ROOT.parents[5]
        worktree = ROOT.parents[2]
        for path, expected in self.report["source_pins"].items():
            source = workspace / path
            if not source.is_file():
                source = worktree / path
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                             expected, path)

    def test_27_board_snapshot_is_provenance_only(self):
        self.assertTrue(self.report["board_snapshot"]["mutable"])
        self.assertNotIn("board_snapshot", self.report["runs"])


if __name__ == "__main__":
    unittest.main()
