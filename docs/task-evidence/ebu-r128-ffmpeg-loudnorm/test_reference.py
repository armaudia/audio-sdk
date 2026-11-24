# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local tests for the R128 target reference fixture."""
from __future__ import annotations

import hashlib
import json
import math
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference as ref  # noqa: E402 - local task module

HERE = Path(__file__).resolve().parent
SOURCE_ROOT = Path("/Users/htsakanyan/workspace/audio/audioml")
SDK_ROOT = HERE.parents[2]


class DeterminismTests(unittest.TestCase):
    def test_generator_is_repeatable(self) -> None:
        first = ref.speech_signal()
        second = ref.speech_signal()
        self.assertEqual(first, second)
        self.assertEqual(ref.tensor_digest(first), ref.tensor_digest(second))

    def test_independent_seeds_differ(self) -> None:
        self.assertNotEqual(ref.tensor_digest(ref.speech_signal(seed=1)),
                            ref.tensor_digest(ref.speech_signal(seed=2)))

    def test_f32_tensor_digest_is_exact(self) -> None:
        digest = ref.tensor_digest((1.0, -1.0, 0.5))
        expected = hashlib.sha256(
            bytes.fromhex("0000803f000080bf0000003f")).hexdigest()
        self.assertEqual(digest, expected)

    def test_canonical_bytes_are_stable(self) -> None:
        value = {"b": 1, "a": [2.0, 3.0]}
        self.assertEqual(ref.canonical_bytes(value),
                         b'{"a":[2.0,3.0],"b":1}')

    def test_lcg_is_version_stable(self) -> None:
        rng = ref.LCG(ref.SEED)
        values = tuple(rng.uniform() for _ in range(4))
        expected = (-0.03229897329583764, 0.023610691539943218,
                    -0.9415285303257406, 0.6951954923570156)
        self.assertEqual(values, expected)


class BoundaryTests(unittest.TestCase):
    def test_public_geometry_constants(self) -> None:
        self.assertEqual(ref.SAMPLE_RATE_HZ, 16000)
        self.assertEqual(ref.CHANNELS, 1)
        self.assertEqual(ref.SAMPLE_FORMAT, "f32")
        self.assertEqual(ref.FRAME_SAMPLES, 160)

    def test_frame_padding_and_flags(self) -> None:
        frames = ref.form_frames((0.1,) * (2 * 160 + 37))
        self.assertEqual(len(frames), 3)
        self.assertEqual(frames[-1]["valid_count"], 37)
        self.assertEqual(frames[-1]["flags"], ref.FLAG_FINAL_PADDING)
        self.assertEqual(frames[-1]["samples"][37:], (0.0,) * 123)
        self.assertEqual(frames[0]["flags"], 0)

    def test_process_conserves_samples_and_maps_source(self) -> None:
        wave = ref.tone(1000.0, 0.05, samples=3 * 160)
        plan = ref.solve_gain(ref.analyze(wave))
        output, results, stats = ref.apply_plan(wave, plan)
        self.assertEqual(len(output), len(wave))
        self.assertEqual(stats["accepted_frames"], 3)
        self.assertEqual(stats["produced_frames"], 3)
        self.assertEqual(stats["rejected_closed"], 0)
        self.assertTrue(all(result.source_first_sample == index * 160
                            and result.produced_count == 160
                            and result.valid_offset == 0
                            for index, result in enumerate(results)))

    def test_invalid_frames_do_not_change_state(self) -> None:
        adapter = ref.LoudnormFrameAdapter(1.0)
        frames = ref.form_frames(ref.tone(1000.0, 0.05, samples=320))
        baseline = {key: value for key, value in adapter.stats.items()
                    if not key.startswith("rejected_")}
        invalid = {
            "missing", "wrong_shape", "short", "nonfinite", "bad_padding",
            "stale_epoch",
        }
        probes = {
            "missing": None,
            "wrong_shape": {"first_input_sample": 0,
                            "samples": ((0.0,),) * 160},
            "short": {"first_input_sample": 0,
                      "samples": (0.0,) * 159},
            "nonfinite": {"first_input_sample": 0,
                          "samples": (float("inf"),) * 160},
            "bad_padding": {**frames[0], "valid_count": 10, "final": True,
                            "samples": (0.1,) * 10 + (0.2,) * 150},
            "stale_epoch": {**frames[0], "epoch": 42},
        }
        for name, frame in probes.items():
            status = adapter.process(frame).status
            self.assertTrue(status.startswith("rejected_"), name)
            self.assertIn(name, invalid)
        self.assertEqual({key: value for key, value in adapter.stats.items()
                          if not key.startswith("rejected_")}, baseline)
        self.assertEqual(adapter.process(frames[0]).status, "ok")
        adapter.close()

    def test_epoch_order_and_close(self) -> None:
        adapter = ref.LoudnormFrameAdapter(1.0)
        frames = ref.form_frames(ref.tone(1000.0, 0.05, samples=480))
        self.assertEqual(adapter.process(frames[0]).status, "ok")
        self.assertEqual(adapter.process(frames[0]).status,
                         "rejected_duplicate")
        self.assertEqual(adapter.process({**frames[2],
                                          "first_input_sample": 320}).status,
                         "rejected_future_packet")
        self.assertEqual(adapter.process(frames[1]).status, "ok")
        self.assertEqual(adapter.process(frames[0]).status,
                         "rejected_out_of_order")
        adapter.close()
        self.assertEqual(adapter.process(frames[2]).status,
                         "rejected_closed")
        self.assertEqual(adapter.drain()[0].status, "rejected_closed")

    def test_reset_is_bit_identical_to_fresh_session(self) -> None:
        frames = ref.form_frames(ref.tone(1000.0, 0.05, samples=8 * 160))
        adapter = ref.LoudnormFrameAdapter(1.25)
        for frame in frames:
            self.assertEqual(adapter.process(frame).status, "ok")
        self.assertEqual(adapter.reset(2, 0).status, "ok")
        self.assertEqual(adapter.process({**frames[0], "epoch": 1}).status,
                         "rejected_stale_epoch")
        reset_outputs = [adapter.process({**frame, "epoch": 2}).samples
                         for frame in frames]
        fresh = ref.LoudnormFrameAdapter(1.25, epoch=2)
        fresh_outputs = [fresh.process({**frame, "epoch": 2}).samples
                         for frame in frames]
        self.assertEqual(reset_outputs, fresh_outputs)
        adapter.close()
        fresh.close()

    def test_sessions_are_independent(self) -> None:
        wave = ref.tone(1000.0, 0.05, samples=3 * 160)
        first, _, first_stats = ref.apply_plan(wave, ref.GainPlan(1.0, "c", None, None, "n"))
        second, _, second_stats = ref.apply_plan(
            wave, ref.GainPlan(0.5, "c", None, None, "n"))
        self.assertNotEqual(first, second)
        self.assertEqual(first_stats["produced_frames"], 3)
        self.assertEqual(second_stats["produced_frames"], 3)


class DspTests(unittest.TestCase):
    def test_k_weighting_is_finite_and_high_shelf_boosts(self) -> None:
        low = ref.k_weight(ref.tone(100.0, 0.05))
        high = ref.k_weight(ref.tone(6000.0, 0.05))
        self.assertEqual(len(low), ref.SAMPLE_RATE_HZ)
        self.assertTrue(all(math.isfinite(value) for value in low + high))
        low_power = sum(value * value for value in low)
        high_power = sum(value * value for value in high)
        self.assertGreater(high_power / low_power, 2.0)

    def test_true_peak_intersample_overshoot(self) -> None:
        wave = (0.0, 0.4, 0.4, 0.0) + (0.0,) * 16
        analysis = ref.analyze(wave)
        self.assertEqual(analysis["sample_peak_abs"], 0.4)
        self.assertGreater(analysis["true_peak_abs"], 0.4)
        overshoot = ref.dbfs(analysis["true_peak_abs"] / 0.4)
        self.assertIsNotNone(overshoot)
        self.assertGreater(float(overshoot), 0.5)

    def test_silence_loudness_undefined_and_gain_identity(self) -> None:
        result = ref.run_condition(ref.silence_signal(1600), "candidate")
        self.assertIsNone(result["input_analysis"]["lufs"])
        self.assertEqual(result["plan"]["mode"], "identity_no_gate")
        self.assertEqual(result["plan"]["gain"], 1.0)
        self.assertEqual(result["output_analysis"]["sample_peak_abs"], 0.0)
        self.assertTrue(result["finite_output"])

    def test_nonfinite_analysis_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ref.analyze((float("nan"),) * 160)

    def test_linear_gain_hits_target_without_peak_cap(self) -> None:
        result = ref.run_condition(ref.tone(1000.0, 0.05), "candidate")
        self.assertEqual(result["plan"]["mode"], "linear_loudness")
        self.assertIsNotNone(result["target_error_lu"])
        self.assertLess(abs(float(result["target_error_lu"])), 1e-6)
        self.assertGreaterEqual(float(result["true_peak_headroom_db"]), 0.0)
        self.assertLess(abs(float(result["gain_error_db"])), 1e-3)

    def test_impulse_peak_cap_and_zero_delay(self) -> None:
        wave = ref.impulse_signal()
        result = ref.run_condition(wave, "candidate")
        self.assertEqual(result["plan"]["mode"], "true_peak_limited")
        self.assertEqual(result["output_analysis"]["true_peak_dbtp"], -1.0)
        self.assertLess(float(result["target_error_lu"]), -1.0)
        self.assertEqual(ref.peak_index(wave), 4000)
        self.assertEqual(ref.peak_index(result["output_samples"]), 4000)
        self.assertEqual(result["buffering_delay_samples"], 0)

    def test_sweep_response_is_flat(self) -> None:
        errors = []
        for frequency in ref.FREQUENCIES_HZ:
            result = ref.run_condition(ref.tone(frequency), "candidate")
            self.assertEqual(result["plan"]["mode"], "linear_loudness")
            errors.append(abs(float(result["gain_error_db"])))
        self.assertLess(max(errors), 1e-3)

    def test_chirp_and_steps_keep_static_gain(self) -> None:
        for wave in (ref.sweep_signal(), ref.step_signal()):
            result = ref.run_condition(wave, "candidate")
            self.assertEqual(result["source_mapping_ok"], True)
            self.assertLess(abs(float(result["gain_error_db"])), 1e-3)
            self.assertTrue(result["finite_output"])

    def test_near_silence_gain_cap_is_explicit(self) -> None:
        result = ref.run_condition(ref.tone(1000.0, 0.001), "candidate")
        self.assertEqual(result["plan"]["mode"], "max_gain_limited")
        self.assertEqual(result["plan"]["limiting_factor"], "gain_safety_cap")
        self.assertEqual(result["plan"]["gain"], ref.MAX_GAIN)
        self.assertLess(float(result["target_error_lu"]), -1.0)

    def test_full_scale_tone_does_not_clip(self) -> None:
        result = ref.run_condition(ref.tone(1000.0, 0.9), "candidate")
        self.assertEqual(result["at_or_above_one_count"], 0)
        self.assertTrue(result["finite_output"])
        self.assertGreaterEqual(float(result["true_peak_headroom_db"]), 0.0)

    def test_sparse_intersample_ceiling_binds(self) -> None:
        result = ref.run_condition(ref.sparse_intersample_signal(),
                                   "candidate")
        self.assertEqual(result["plan"]["mode"], "true_peak_limited")
        self.assertEqual(result["output_analysis"]["true_peak_dbtp"], -1.0)
        self.assertLess(float(result["target_error_lu"]), -1.0)

    def test_lra_estimate_requires_ten_blocks(self) -> None:
        short = ref.analyze(ref.tone(1000.0, samples=8 * ref.HOP_SAMPLES
                                     + ref.BLOCK_SAMPLES - 1))
        self.assertIsNone(short["lra_estimate"])
        self.assertEqual(short["lra_reason"], "insufficient_gated_blocks")
        long = ref.analyze(ref.tone(1000.0, samples=20 * ref.HOP_SAMPLES
                                    + ref.BLOCK_SAMPLES))
        self.assertIsNotNone(long["lra_estimate"])

    def test_final_partial_window_is_conserved(self) -> None:
        wave = ref.speech_signal()[:8 * 160 + ref.FINAL_PARTIAL_SAMPLES]
        result = ref.run_condition(wave, "candidate")
        self.assertEqual(result["counts"]["source_samples"], 1317)
        self.assertEqual(result["counts"]["valid_samples"], 1317)
        self.assertEqual(result["counts"]["frames"], 9)
        self.assertTrue(result["source_mapping_ok"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = ref.build_report()

    def test_report_shape_and_status(self) -> None:
        self.assertEqual(self.report["profile"], "DSP")
        self.assertEqual(self.report["base_commit"], ref.BASE_COMMIT)
        self.assertEqual(self.report["candidate_status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        for key in ("conditions", "sweeps", "steps", "impulse", "silence",
                    "control", "headroom_and_true_peak", "delay", "state",
                    "regressions", "gates", "blockers"):
            self.assertIn(key, self.report)

    def test_boundary_is_optional_and_unregistered(self) -> None:
        boundary = self.report["boundary"]
        self.assertFalse(boundary["registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_ffmpeg_provenance_is_blocked(self) -> None:
        provenance = self.report["ffmpeg_provenance"]
        self.assertEqual(provenance["status"], "blocked")
        self.assertEqual(provenance["synthetic_loudnorm_invocation"]["status"],
                         "not_run")
        historical = provenance["historical_ffmpeg_provenance"]
        self.assertEqual(historical["version"], "7.1")
        self.assertEqual(historical["license"], "GPL-2.0-or-later")
        self.assertIsNone(historical["build_configuration"])
        self.assertTrue(all(not provenance["binary_handling"][key]
                            for key in ("vendored", "downloaded", "shipped",
                                        "wrapped")))

    def test_no_binary_or_licensed_media_in_task_dir(self) -> None:
        forbidden = {path.name.lower() for path in HERE.iterdir()
                     if path.suffix.lower() in (".wav", ".bin", ".exe",
                                                ".dylib", ".so", ".dll")}
        self.assertEqual(forbidden, set())
        self.assertFalse(any(path.name.startswith("ffmpeg")
                             for path in HERE.iterdir()))

    def test_source_pins_match_bytes(self) -> None:
        for pin in ref.SOURCE_PINS:
            root = SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT
            path = root / pin["path"]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, pin["sha256"], pin["path"])

    def test_report_is_byte_reproducible(self) -> None:
        self.assertEqual(ref.canonical_report_bytes(ref.build_report()),
                         ref.canonical_report_bytes(ref.build_report()))

    def test_committed_report_matches_generator_and_digest(self) -> None:
        report_bytes = (HERE / "report.json").read_bytes()
        self.assertEqual(report_bytes,
                         ref.canonical_report_bytes(self.report))
        recorded = (HERE / "report.json.sha256").read_text().strip()
        self.assertEqual(recorded,
                         hashlib.sha256(report_bytes).hexdigest())

    def test_regressions_are_recorded_verbatim(self) -> None:
        names = {(item["condition"], item["metric"])
                 for item in self.report["regressions"]}
        self.assertIn(("impulse", "target_error_lu"), names)
        self.assertIn(("sparse_intersample_ceiling", "target_error_lu"), names)
        self.assertIn(("all_conditions", "lra_target"), names)
        self.assertIn(("all_conditions", "dynamic_mode"), names)

    def test_counts_and_finite_outputs(self) -> None:
        self.assertTrue(self.report["all_outputs_finite"])
        self.assertTrue(self.report["all_valid_frames_conserved"])
        for condition in self.report["conditions"].values():
            self.assertEqual(condition["counts"]["source_samples"],
                             ref.SCORED_SAMPLES)
            self.assertEqual(condition["counts"]["valid_samples"],
                             ref.SCORED_SAMPLES)
            self.assertEqual(condition["counts"]["rejections"], 0)

    def test_gate_statuses(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(gates["local_external_tool"]["status"], "blocked")
        self.assertEqual(gates["independent_ebu_meter"]["status"], "blocked")
        self.assertEqual(gates["public_frame_boundary"]["status"], "pass")
        self.assertEqual(gates["dsp_profile_synthetic"]["status"], "pass")
        self.assertEqual(gates["gpl_binary_exclusion"]["status"], "pass")
        self.assertTrue(all("reopen" in value for value in gates.values()))

    def test_strict_json_serialization(self) -> None:
        encoded = ref.canonical_report_bytes(self.report)
        decoded = json.loads(encoded, parse_constant=lambda value: (
            (_ for _ in ()).throw(ValueError(value))))
        self.assertEqual(decoded["schema_id"], ref.SCHEMA_ID)


if __name__ == "__main__":
    unittest.main()
