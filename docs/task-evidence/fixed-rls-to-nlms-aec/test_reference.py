# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest coverage for the fixed RLS-to-NLMS reference."""

from __future__ import annotations

import hashlib
import pathlib
import unittest

import check_licensing
import crosscheck
import reference
import run as adapter

ROOT = pathlib.Path(__file__).resolve().parent
FRAME = reference.FRAME_SAMPLES


class ReportFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()


class ConfigAndAdverseTests(ReportFixture):
    def test_01_config_validation(self):
        for kwargs in ({"filter_taps": 0}, {"filter_taps": 1.5},
                       {"rls_lambda": 1.0}, {"rls_lambda": float("inf")},
                       {"handoff_sample": -1}, {"nlms_step": 0.0},
                       {"epsilon": -1e-9}, {"max_abs_input": 0},
                       {"weight_l1_limit": 0}, {"variant": "unknown"}):
            with self.assertRaises(reference.ConfigError):
                reference.HybridConfig(**kwargs)
        self.assertEqual(reference.HybridConfig().filter_taps,
                         reference.FILTER_TAPS)

    def test_02_invalid_frame_rejections_leave_state_unchanged(self):
        engine = reference.FixedHandoffAec()
        frame = (0.1,) * FRAME
        ref = (0.05,) * FRAME
        engine.process(frame, ref)
        before = engine.state_digest()
        statuses = [
            engine.process((float("nan"),) * FRAME, ref).status,
            engine.process((float("inf"),) * FRAME, ref).status,
            engine.process((5.0,) * FRAME, ref).status,
            engine.process((0.1,) * 8, ref).status,
            engine.process(frame, (float("nan"),) * FRAME).status,
            engine.process(frame, (0.05,) * 8).status,
            engine.process(frame, ref, epoch=2).status,
            engine.process(frame, ref, first_sample=161).status,
        ]
        self.assertTrue(all(status.startswith("rejected") for status in statuses))
        self.assertEqual(engine.state_digest(), before)
        self.assertEqual(engine.invalid_count, 8)

    def test_03_missing_reference_passthrough_is_not_adaptive(self):
        engine = reference.FixedHandoffAec()
        frame = tuple(0.1 * value / 10.0 for value in range(FRAME))
        result = engine.process(frame, None)
        self.assertEqual(result.status, "no_reference_passthrough")
        self.assertEqual(result.samples, frame)
        self.assertEqual(engine.reference_frames, 0)
        self.assertEqual(engine.no_reference_frames, 1)
        self.assertEqual(engine.weight_l1(), 0.0)

    def test_04_reset_drain_and_partial_frame(self):
        engine = reference.FixedHandoffAec()
        self.assertIsNone(engine.reset(9, 320))
        self.assertEqual((engine.epoch, engine.next_sample), (9, 320))
        self.assertTrue(engine.process((0.1,) * FRAME, (0.05,) * FRAME,
                                       epoch=8).status.startswith("rejected"))
        result = engine.process((0.1,) * 37, (0.05,) * 37, final=True,
                                first_sample=320)
        self.assertEqual(len(result.samples), 37)
        self.assertEqual(engine.next_sample, 357)
        state_before = engine.state_digest()
        drain = engine.drain()
        self.assertEqual(drain.status, "end_of_stream")
        self.assertEqual(drain.samples, ())
        self.assertEqual(engine.state_digest(), state_before)
        with self.assertRaises(reference.ConfigError):
            engine.reset(8, 0)

    def test_05_infinite_state_is_contained(self):
        self.assertTrue(self.report["state"]["safety_guard_status"].startswith("ok"))
        self.assertTrue(self.report["state"]["safety_guard_output_finite"])
        self.assertTrue(self.report["state"]["safety_guard_handoff"])
        self.assertTrue(self.report["state"]["safety_guard_weights_finite"])
        self.assertTrue(self.report["adverse"]["state_unchanged_after_invalid"])
        self.assertTrue(self.report["adverse"]["no_reference_weights_unchanged"])

    def test_06_independent_sessions_and_determinism(self):
        self.assertTrue(self.report["state"]["deterministic_output_digest"])
        self.assertTrue(self.report["state"]["deterministic_state_digest"])
        mic, ref = self.report, None  # state assertions come from the pinned report
        data = reference.fixture("delay_change")
        engine_a = reference.FixedHandoffAec()
        engine_b = reference.FixedHandoffAec()
        for start in range(0, 20 * FRAME, FRAME):
            engine_a.process(data["microphone"][start:start + FRAME],
                             data["reference"][start:start + FRAME])
            engine_b.process(data["microphone"][start:start + FRAME],
                             data["reference"][start:start + FRAME])
        self.assertEqual(engine_a.state_digest(), engine_b.state_digest())
        engine_c = reference.FixedHandoffAec()
        engine_c.process((0.3,) * FRAME, (0.2,) * FRAME)
        self.assertNotEqual(engine_a.state_digest(), engine_c.state_digest())

    def test_07_frame_and_sample_paths_agree(self):
        self.assertTrue(self.report["state"]["framewise_equals_samplewise"])
        self.assertTrue(self.report["state"]["framewise_equals_samplewise_state"])


class FixtureAndHandoffTests(ReportFixture):
    def test_08_fixture_is_deterministic(self):
        first = reference.fixture("double_talk")
        second = reference.fixture("double_talk")
        for key in ("microphone", "reference", "echo", "near", "playback"):
            self.assertEqual(reference.tensor_digest(first[key]),
                             reference.tensor_digest(second[key]))

    def test_09_explicit_reference_latency_measured(self):
        alignment = self.report["alignment"]
        self.assertEqual(alignment["measured_lag_samples"],
                         alignment["intended_primary_tap_delay_samples"])
        self.assertEqual(alignment["alignment_error_samples"], 0)
        self.assertEqual(alignment["delayed_render_misalignment_samples"],
                         reference.DELAYED_RENDER_SAMPLES)
        self.assertEqual(alignment["algorithmic_delay_samples"], 0)

    def test_10_fixture_digests_present(self):
        for name, digests in self.report["fixture_digests"].items():
            self.assertEqual(len(digests["microphone"]), 64)
            if name == "legacy_zero_reference_extension":
                self.assertIn("reference", digests)
                continue
            self.assertIn("playback", digests)
            self.assertIn("near", digests)
        self.assertEqual(self.report["fixture_digests"]
                         ["legacy_zero_reference_extension"]["samples"],
                         reference.LEGACY_SAMPLES)

    def test_11_impulse_step_and_silence(self):
        dsp = self.report["dsp_controls"]
        self.assertEqual(dsp["impulse"]["detail"]["peak_sample_index"],
                         reference.PATH_A[0][0] + 10 * FRAME)
        self.assertEqual(dsp["step"]["detail"]["first_nonzero_sample_index"],
                         dsp["step"]["detail"]["expected_sample_index"])
        self.assertEqual(dsp["silence"]["detail"]["peak_abs"], 0.0)
        self.assertEqual(dsp["silence"]["detail"]["nonzero_count"], 0)

    def test_12_handoff_is_fixed_and_frame_aligned(self):
        handoff = self.report["handoff"]
        self.assertTrue(handoff["frame_aligned"])
        self.assertEqual(handoff["candidate_handoff_samples"], [reference.HANDOFF_SAMPLE] * 4)
        self.assertEqual(handoff["candidate_handoff_reasons"], ["scheduled"] * 4)
        self.assertTrue(handoff["weights_and_history_copied"])
        self.assertTrue(handoff["rls_covariance_drained_at_handoff"])

    def test_13_rls_phase_precedes_nlms_phase(self):
        data = reference.fixture("single_talk")
        run = reference.run_stream(data)
        self.assertIsNotNone(run["handoff_sample"])
        self.assertEqual(run["handoff_sample"], reference.HANDOFF_SAMPLE)
        self.assertEqual(run["phase"], "nlms")
        self.assertGreater(run["rls_frames"], 0)
        self.assertGreater(run["nlms_frames"], 0)
        self.assertEqual(run["safety_handoffs"], 0)


class MetricAndSafetyTests(ReportFixture):
    def test_14_single_talk_convergence(self):
        metrics = self.report["runs"]["single_talk"]["metrics"]
        attenuation = metrics["echo_attenuation"]
        self.assertGreater(attenuation["single_talk_erle_db"], 20.0)
        self.assertGreater(attenuation["early_single_talk_erle_db"], 20.0)
        self.assertEqual(attenuation["nonfinite_count"], 0)
        self.assertLess(attenuation["peak_abs"], 1.0)
        self.assertIsNone(metrics["near_end_preservation"]["double_talk_near_snr_db"])

    def test_15_far_end_only_erle_separate_from_double_talk(self):
        for record in self.report["runs"].values():
            metrics = record["metrics"]
            if metrics is None:
                continue
            self.assertTrue(metrics["far_end_only_erle_excludes_double_talk"])
            self.assertEqual(metrics["echo_attenuation"]
                             ["valid_far_end_only_window_samples"],
                             [reference.SEGMENTS["single_metric_start"],
                              reference.SEGMENTS["single_end"]])
            self.assertNotIn("double_talk_erle_db", metrics["echo_attenuation"])

    def test_16_double_talk_preservation_is_separate(self):
        adaptive = self.report["runs"]["double_talk"]["metrics"]
        near = adaptive["near_end_preservation"]["double_talk_near_snr_db"]
        fixed = self.report["controls"]["fixed_attenuation_double_talk"]["metrics"]
        identity = self.report["controls"]["identity_double_talk"]["metrics"]
        self.assertGreater(near, 20.0)
        self.assertGreater(near, fixed["near_end_preservation"]["double_talk_near_snr_db"])
        self.assertGreater(near, identity["near_end_preservation"]["double_talk_near_snr_db"])

    def test_17_controls_are_separate_and_never_qualify(self):
        self.assertTrue(self.report["fixed_attenuation_separate_from_adaptive"])
        for name, record in self.report["controls"].items():
            self.assertFalse(record["qualifies"])
            self.assertIn(name.split("_")[0],
                          ("rls", "nlms", "identity", "fixed"))
        fixed = self.report["controls"]["fixed_attenuation_single_talk"]["metrics"]
        self.assertAlmostEqual(fixed["echo_attenuation"]["single_talk_erle_db"],
                               6.0206, places=3)

    def test_18_delay_change_reconvergence(self):
        metrics = self.report["runs"]["delay_change"]["metrics"]["echo_attenuation"]
        self.assertGreater(metrics["pre_change_erle_db"], 20.0)
        self.assertLess(metrics["post_change_early_erle_db"],
                        metrics["pre_change_erle_db"])
        self.assertGreater(metrics["post_change_late_erle_db"],
                           metrics["post_change_early_erle_db"])
        self.assertGreater(metrics["reconvergence_delta_db"], 1.0)
        self.assertLess(metrics["gain_before_feedback_db"],
                        self.report["runs"]["single_talk"]["metrics"]
                        ["echo_attenuation"]["gain_before_feedback_db"])

    def test_19_legacy_rls_nonfinite_is_reproduced(self):
        legacy = self.report["legacy_rls_only"]
        self.assertEqual(legacy["status"], "historical_failure_reproduced")
        self.assertTrue(legacy["overflow_within_fixture"])
        self.assertGreater(legacy["first_nonfinite_sample"], 0)
        self.assertLess(legacy["first_nonfinite_sample"], legacy["samples"])
        self.assertLess(legacy["max_relative_error_vs_closed_form"], 1e-12)
        self.assertFalse(legacy["qualifies"])

    def test_20_candidate_prevents_legacy_failure(self):
        safety = self.report["near_only_zero_reference_safety"]
        self.assertEqual(safety["status"], "ok_synthetic")
        self.assertEqual(safety["samples"], reference.LEGACY_SAMPLES)
        self.assertEqual(safety["nonfinite_count"], 0)
        self.assertTrue(safety["weights_bounded"])
        self.assertLessEqual(safety["max_weight_l1"], safety["weight_l1_limit"])
        self.assertEqual(safety["safety_handoffs"], 0)
        self.assertEqual(safety["handoff_sample"], reference.HANDOFF_SAMPLE)
        self.assertEqual(safety["handoff_reason"], "scheduled")

    def test_21_delayed_dropout_missing_do_not_qualify(self):
        for name, status in (("delayed_render", "misaligned_reference"),
                             ("reference_dropout", "partial_reference")):
            record = self.report["runs"][name]
            self.assertEqual(record["status"], status)
            self.assertIsNotNone(record["metrics"])
            self.assertFalse(record["qualifies"])
        missing = self.report["runs"]["missing_reference"]
        self.assertEqual(missing["status"], "blocked_no_reference")
        self.assertIsNone(missing["metrics"])
        self.assertFalse(missing["qualifies"])
        self.assertEqual(missing["no_reference_frames"],
                         reference.TOTAL_SAMPLES // FRAME)

    def test_22_no_missing_result_may_qualify(self):
        self.assertTrue(self.report["no_missing_result_may_qualify"])
        self.assertEqual(self.report["qualification"], "not_qualified")
        self.assertEqual(self.report["status"], "proposal_only")
        self.assertEqual(self.report["completeness"], "incomplete")
        for record in list(self.report["runs"].values()) + list(self.report["controls"].values()):
            if record["metrics"] is None:
                self.assertFalse(record["qualifies"])
            if record["qualifies"]:
                self.assertIsNotNone(record["metrics"])

    def test_23_bounded_weights_and_finite_outputs(self):
        for record in list(self.report["runs"].values()) + list(self.report["controls"].values()):
            metrics = record["metrics"]
            if metrics is None:
                continue
            attenuation = metrics["echo_attenuation"]
            self.assertEqual(attenuation["nonfinite_count"], 0)
            self.assertLessEqual(attenuation["peak_abs"], reference.MAX_ABS_INPUT)
            self.assertTrue(attenuation["weights_bounded"])
            self.assertLessEqual(attenuation["max_weight_l1"],
                                 attenuation["weight_l1_limit"])

    def test_24_regressions_are_reported(self):
        self.assertEqual(len(self.report["regressions"]), 4)
        self.assertTrue(any(item["value_db"] < 0.0
                            for item in self.report["regressions"]))
        self.assertTrue(any("rls_only_frozen" in item["comparison"]
                            for item in self.report["regressions"]))


class AdapterAndReproducibilityTests(ReportFixture):
    def _base_request(self, operation="inspect"):
        request = {
            "protocol_version": 1,
            "operation": operation,
            "candidate_ref": {"kind": "local", "id": "fixed-rls-to-nlms-aec",
                              "revision": 1},
            "adapter_ref": {"kind": "local", "id": "adapter", "revision": 1},
            "configuration": {"control": "hybrid"},
        }
        if operation == "run":
            request.update({"attempt_id": "attempt-1", "stimulus_id": "double_talk",
                            "samples": None, "reference_samples": None,
                            "reference_mode": "explicit"})
        return request

    def test_25_inspect_discloses_boundary(self):
        result = adapter.inspect(self._base_request())
        self.assertEqual(result["identity"], adapter.IDENTITY)
        self.assertEqual(result["handoff_sample"], reference.HANDOFF_SAMPLE)
        self.assertIn("fixed_rls_to_nlms_handoff", result["supported_modes"])
        self.assertEqual(result["algorithmic_delay_samples"], 0)

    def test_26_run_with_explicit_reference(self):
        result = adapter.run(self._base_request("run"))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"]["sample_rate_hz"], 16000)
        self.assertEqual(result["output"]["nonfinite_count"], 0)
        self.assertEqual(result["output"]["handoff_sample"], reference.HANDOFF_SAMPLE)
        self.assertIsNone(result["metrics"])
        self.assertFalse(result["qualifies"])

    def test_27_withheld_reference_is_blocked(self):
        request = self._base_request("run")
        request["reference_mode"] = "withheld"
        result = adapter.run(request)
        self.assertEqual(result["status"], "blocked_no_reference")
        self.assertIsNone(result["metrics"])
        self.assertFalse(result["qualifies"])

    def test_28_request_validation(self):
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

    def test_29_report_regeneration_is_byte_identical(self):
        current = (ROOT / "report.json").read_bytes()
        rebuilt, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(current, (rebuilt + "\n").encode("utf-8"))
        self.assertEqual((ROOT / "report.json.sha256").read_text(
            encoding="ascii").strip(), digest)

    def test_30_sources_regeneration_is_byte_identical(self):
        current = (ROOT / "SOURCES.sha256").read_bytes()
        adapter.generate_sources()
        self.assertEqual((ROOT / "SOURCES.sha256").read_bytes(), current)

    def test_31_crosscheck_regeneration_is_byte_identical(self):
        current = (ROOT / "provider" / "crosscheck_vectors.h").read_bytes()
        self.assertEqual(crosscheck.generate().encode("ascii"), current)

    def test_32_source_pins_match_files(self):
        workspace = ROOT.parents[5]
        worktree = ROOT.parents[2]
        for mapping in (self.report["source_pins"], self.report["boundary_pins"]):
            for path, expected in mapping.items():
                source = workspace / path
                if not source.is_file():
                    source = worktree / path
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                                 expected, path)

    def test_33_board_snapshot_is_provenance_only(self):
        self.assertTrue(self.report["board_snapshot"]["mutable"])
        self.assertNotIn("board_snapshot", self.report["runs"])

    def test_34_licensing_check_passes(self):
        result = check_licensing.check()
        self.assertEqual(result["status"], "ok", result["problems"])


if __name__ == "__main__":
    unittest.main()
