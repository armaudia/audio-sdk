# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the synthetic pitch-period repeat PLC fixture.

Run with the pinned Python 3.12 scorer environment from README.md:

    /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python -m unittest -v test_fixture.py
"""
from __future__ import annotations

import builtins
import hashlib
import json
import os
import subprocess
import unittest
from pathlib import Path

import fixture as fx

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
REPORT = HERE / "report.json"
MEASUREMENTS = HERE / "runtime-measurements.json"
CONDITIONS = (
    "identity_clean", "zero_fill_noisy_control",
    "linear_interpolation_baseline", "autoregressive_baseline",
    "pitch_period_repeat",
)


def pinned_scorer_available() -> bool:
    try:
        import importlib.metadata
        import numpy  # noqa: F401
        import pystoi  # noqa: F401
        return (importlib.metadata.version("pystoi") == "0.4.1"
                and numpy.__version__ == "2.5.4")
    except Exception:
        return False


class SourcePinTests(unittest.TestCase):
    def test_01_source_pins_hash_to_recorded_values(self) -> None:
        for pin in fx.SOURCE_PINS:
            with self.subTest(path=pin["path"]):
                base = SDK_ROOT if pin["path"].startswith("api/") else SOURCE_ROOT
                path = base / pin["path"]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 pin["sha256"])

    def test_02_scorer_pin_matches_installed_pystoi(self) -> None:
        pin = next(p for p in fx.SCORER_PINS if p["id"] == "pystoi")
        import importlib.metadata
        import inspect
        import numpy
        from pystoi import stoi
        self.assertEqual(importlib.metadata.version("pystoi"), pin["version"])
        self.assertEqual(numpy.__version__, "2.5.4")
        module = Path(inspect.getfile(stoi))
        self.assertEqual(hashlib.sha256(module.read_bytes()).hexdigest(),
                         pin["sha256"])

    def test_03_baseline_pins_match_pinned_git_blobs(self) -> None:
        for pin in fx.BASELINE_PINS:
            with self.subTest(baseline=pin["id"]):
                try:
                    raw = subprocess.run(
                        ["git", "-C", str(SDK_ROOT), "show",
                         f"{pin['commit']}:{pin['path']}"],
                        check=True, capture_output=True).stdout
                except (OSError, subprocess.CalledProcessError):
                    self.skipTest("baseline git blob unavailable in this checkout")
                self.assertEqual(hashlib.sha256(raw).hexdigest(), pin["sha256"])

    def test_04_pinned_base_commit_is_reachable_from_head(self) -> None:
        result = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "merge-base", "--is-ancestor",
             fx.BASE_COMMIT, "HEAD"], capture_output=True)
        self.assertEqual(result.returncode, 0)


class DeterminismTests(unittest.TestCase):
    def test_05_generated_report_is_byte_identical(self) -> None:
        if not pinned_scorer_available():
            self.skipTest("pinned scorer not installed")
        self.assertEqual(fx.canonical_report_bytes(fx.build_report()),
                         REPORT.read_bytes())

    def test_06_clean_reference_digest_is_stable(self) -> None:
        digest = fx.tensor_digest(fx.clean_speech())
        self.assertEqual(digest, json.loads(REPORT.read_text())["cohort"]["clean_digest"])
        self.assertEqual(fx.tensor_digest(fx.clean_speech()), digest)

    def test_07_stream_is_repeatable(self) -> None:
        frames = fx.form_packet_stream(fx.clean_speech(), fx.ERASURE_PLAN,
                                       method="pitch")
        digests = []
        for _ in range(2):
            results, _ = fx.run_stream(frames)
            digests.append(fx.tensor_digest(
                fx.reconstruct(results, fx.SCORED_SAMPLES)))
        self.assertEqual(digests[0], digests[1])

    def test_08_pitch_material_and_estimates_are_repeatable(self) -> None:
        for spec in fx.PITCH_PROBES:
            with self.subTest(probe=spec["name"]):
                material = fx.pitch_probe_material(spec)
                self.assertEqual(fx.tensor_digest(material),
                                 fx.tensor_digest(fx.pitch_probe_material(spec)))
                self.assertEqual(fx.estimate_pitch(material),
                                 fx.estimate_pitch(material))

    def test_09_fixture_spec_digest_matches(self) -> None:
        report = json.loads(REPORT.read_text())
        spec = {
            "contract": fx.CONTRACT_ID,
            "schema": fx.SCHEMA_ID,
            "sample_rate_hz": fx.SAMPLE_RATE_HZ,
            "frame_samples": fx.FRAME_SAMPLES,
            "buffering_frames": fx.BUFFERING_FRAMES,
            "buffering_delay_samples": fx.BUFFERING_DELAY_SAMPLES,
            "max_burst_frames": fx.MAX_BURST_FRAMES,
            "max_drain_calls": fx.MAX_DRAIN_CALLS,
            "pitch_min_lag": fx.PITCH_MIN_LAG,
            "pitch_max_lag": fx.PITCH_MAX_LAG,
            "pitch_window_samples": fx.PITCH_WINDOW_SAMPLES,
            "pitch_voice_threshold": fx.PITCH_VOICE_THRESHOLD,
            "pitch_energy_threshold": fx.PITCH_ENERGY_THRESHOLD,
            "pitch_repeat_gain": fx.PITCH_REPEAT_GAIN,
            "pitch_burst_decay": fx.PITCH_BURST_DECAY,
            "pitch_min_gain": fx.PITCH_MIN_GAIN,
            "pitch_output_clamp": fx.PITCH_OUTPUT_CLAMP,
            "ar_order": fx.AR_ORDER,
            "ar_context_samples": fx.AR_CONTEXT_SAMPLES,
            "ar_ridge_relative": fx.AR_RIDGE_RELATIVE,
            "ar_ridge_absolute": fx.AR_RIDGE_ABSOLUTE,
            "ar_bound_factor": fx.AR_BOUND_FACTOR,
            "scored_frames": fx.SCORED_FRAMES,
            "pitch_schedule": [list(item) for item in fx.PITCH_SCHEDULE],
            "erasure_plan": list(fx.ERASURE_PLAN),
            "strata": fx.STRATA,
            "adversarial_erasures": fx.ADVERSARIAL_ERASURES,
            "pitch_probes": [dict(item) for item in fx.PITCH_PROBES],
            "seeds": {"speech": fx.SEED_SPEECH, "noise": fx.SEED_NOISE,
                      "probe": fx.SEED_PROBE},
            "source_pins": {p["path"]: p["sha256"] for p in fx.SOURCE_PINS},
            "scorer_pins": [dict(p) for p in fx.SCORER_PINS],
            "baseline_pins": [dict(p) for p in fx.BASELINE_PINS],
            "base_commit": fx.BASE_COMMIT,
        }
        self.assertEqual(fx.object_digest(spec), report["fixture_digest"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text())

    def test_10_profile_status_and_v0_geometry(self) -> None:
        self.assertEqual(self.report["profile"], "Enhancement")
        self.assertEqual(self.report["candidate_status"],
                         "proposal_only_synthetic_incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        fmt = self.report["format"]
        self.assertEqual((fmt["sample_rate_hz"], fmt["channels"],
                          fmt["sample_format"], fmt["frame_samples"]),
                         (16000, 1, "f32", 160))
        self.assertFalse(self.report["boundary"]["public_abi_changed"])
        self.assertFalse(self.report["boundary"]["installed_default_changed"])

    def test_11_counts_and_cohort(self) -> None:
        cohort = self.report["cohort"]
        self.assertEqual(cohort["frames"], 250)
        self.assertEqual(cohort["samples"], 40000)
        self.assertEqual(cohort["duration_seconds"], 2.5)
        self.assertEqual(cohort["erased_frame_count"], 11)
        self.assertEqual(cohort["erased_sample_count"], 1760)
        self.assertEqual(set(self.report["conditions"]), set(CONDITIONS))
        for name, condition in self.report["conditions"].items():
            self.assertEqual(condition["counts"]["produced_frames"], 255)
            self.assertEqual(condition["input"]["samples"], 40000)
            self.assertEqual(condition["output"]["samples"], 40000)
            self.assertEqual(condition["counts"]["concealed_frames"],
                             0 if name == "identity_clean" else 11)

    def test_12_all_metrics_available_and_outputs_valid(self) -> None:
        self.assertTrue(self.report["all_metrics_available"])
        self.assertTrue(self.report["all_outputs_finite"])
        self.assertTrue(self.report["overall_synthetic_pass"])
        for condition in self.report["conditions"].values():
            self.assertTrue(condition["all_metrics_available"])
            self.assertTrue(condition["output"]["finite"])
            self.assertEqual(condition["output"]["nonfinite_count"], 0)
            self.assertEqual(condition["output"]["at_or_above_one_count"], 0)
            self.assertLess(condition["output"]["peak_abs"], 1.0)
            self.assertTrue(condition["clean_preservation"]["valid_samples_bit_identical"])
            self.assertEqual(condition["clean_preservation"]["valid_sample_mismatches"], 0)
            if condition["counts"]["concealed_frames"]:
                self.assertIsNotNone(condition["lost_region"]["concealed_rmse"])
            else:
                self.assertIsNone(condition["lost_region"]["concealed_rmse"])

    def test_13_identity_and_paired_controls(self) -> None:
        identity = self.report["conditions"]["identity_clean"]
        self.assertIsNone(identity["si_sdr_db"]["candidate"])
        self.assertIn("exact_reconstruction", identity["si_sdr_db"]["invalid_reasons"])
        self.assertEqual(identity["stoi"]["candidate"], 1.0)
        self.assertIsNone(identity["lost_region"]["concealed_rmse"])
        for name in CONDITIONS[1:]:
            condition = self.report["conditions"][name]
            self.assertIsNotNone(condition["si_sdr_db"]["candidate"])
            self.assertIsNotNone(condition["stoi"]["candidate"])
            self.assertEqual(condition["si_sdr_db"]["paired_delta"],
                             round(condition["si_sdr_db"]["candidate"]
                                   - condition["si_sdr_db"]["identity_noisy"], 6))
            self.assertEqual(condition["stoi"]["paired_delta"],
                             round(condition["stoi"]["candidate"]
                                   - condition["stoi"]["identity_noisy"], 6))

    def test_14_established_baselines_and_candidate(self) -> None:
        conditions = self.report["conditions"]
        zero = conditions["zero_fill_noisy_control"]
        linear = conditions["linear_interpolation_baseline"]
        ar = conditions["autoregressive_baseline"]
        pitch = conditions["pitch_period_repeat"]
        # On this synthetic signal the linear baseline is below zero-fill on
        # SI-SDR; report that measured result rather than asserting a win.
        self.assertIsNotNone(linear["si_sdr_db"]["candidate"])
        self.assertGreater(ar["si_sdr_db"]["candidate"],
                           zero["si_sdr_db"]["candidate"])
        self.assertGreater(pitch["si_sdr_db"]["candidate"],
                           zero["si_sdr_db"]["candidate"])
        self.assertLess(pitch["lost_region"]["concealed_rmse"],
                        zero["lost_region"]["concealed_rmse"])
        self.assertLess(pitch["lost_region"]["concealed_rmse"],
                        linear["lost_region"]["concealed_rmse"])
        self.assertIsNotNone(pitch["stoi"]["candidate"])
        self.assertTrue(all(conditions[name]["clean_preservation"]["valid_samples_bit_identical"]
                            for name in CONDITIONS))

    def test_15_pitch_estimation_evidence_complete(self) -> None:
        pitch = self.report["pitch_estimation"]
        self.assertTrue(pitch["pass"])
        self.assertTrue(pitch["probes"]["pass"])
        self.assertEqual({case["kind"] for case in pitch["probes"]["cases"]},
                         {"voiced", "unvoiced", "silence"})
        for case in pitch["probes"]["cases"]:
            self.assertTrue(case["pass"])
            self.assertEqual(case["material_digest"], fx.tensor_digest(
                fx.pitch_probe_material(next(p for p in fx.PITCH_PROBES
                                             if p["name"] == case["name"]))))
        self.assertEqual(len(pitch["decision_alignment"]), 11)
        self.assertTrue(pitch["decision_alignment_pass"])
        for item in pitch["decision_alignment"]:
            if item["region"] == "voiced":
                self.assertTrue(item["estimated_voiced"])
            else:
                self.assertFalse(item["estimated_voiced"])

    def test_16_erasure_stratification_complete(self) -> None:
        strata = self.report["erasure_stratification"]["strata"]
        self.assertEqual(set(strata), set(fx.STRATA))
        covered = [frame for stratum in strata.values()
                   for frame in stratum["erased_frames"]]
        self.assertEqual(sorted(covered), list(fx.ERASURE_PLAN))
        for name, stratum in strata.items():
            self.assertEqual(stratum["erased_samples"],
                             len(stratum["erased_frames"]) * fx.FRAME_SAMPLES)
            self.assertEqual(set(stratum["per_condition_rmse"]), set(CONDITIONS))
            self.assertEqual(set(stratum["regions"]),
                             {fx.region_for_frame(f)
                              for f in stratum["erased_frames"]})
            for condition in stratum["per_frame_rmse"].values():
                self.assertEqual(set(condition),
                                 {str(f) for f in stratum["erased_frames"]})
            self.assertEqual(stratum["per_condition_rmse"]["identity_clean"], 0.0)
            self.assertEqual(len(stratum["candidate_pitch_decisions"]),
                             len(stratum["erased_frames"]))
        self.assertTrue(self.report["erasure_stratification"][
            "identity_is_exact_on_erased_intervals"])
        self.assertEqual(self.report["erasure_stratification"]["all_erased_samples"],
                         1760)
        voiced = strata["voiced_four_frame_burst"]["per_condition_rmse"]
        self.assertLess(voiced["pitch_period_repeat"], voiced["zero_fill_noisy_control"])

    def test_17_decoded_intervals_and_duration(self) -> None:
        intervals = self.report["decoded_intervals"]["pitch_period_repeat"]
        conceal_frames = sum(run["frames"] for run in intervals["runs"]
                             if run["kind"] == fx.KIND_CONCEAL)
        self.assertEqual(conceal_frames, 11)
        self.assertTrue(all(run["flags"] == [fx.FLAG_CONCEALMENT]
                            for run in intervals["runs"]
                            if run["kind"] == fx.KIND_CONCEAL))
        self.assertEqual(intervals["decoded_samples"], 40000)
        self.assertEqual(intervals["decoded_duration_s"], 2.5)
        self.assertEqual(intervals["valid_content_samples"], 40000 - 1760)
        self.assertEqual(intervals["concealed_frames"], 11)
        self.assertEqual(intervals["invalid_zero_length_frames"], 0)
        availability = self.report["availability"]["pitch_period_repeat"]
        self.assertEqual(availability["buffering_delay_samples"], 800)
        self.assertEqual(availability["first_valid_output_call_index"], 5)

    def test_18_alignment_state_and_memory(self) -> None:
        self.assertTrue(self.report["alignment_pass"])
        self.assertEqual(self.report["alignment"]["measured_content_lag_samples"], 0)
        self.assertEqual(self.report["alignment"]["measured_raw_peak_index"], 4800)
        self.assertEqual(self.report["alignment"]["pitch_algorithm_intrinsic_delay_samples"], 0)
        self.assertTrue(self.report["alignment"]["source_mapping_checks"])
        self.assertTrue(self.report["state_pass"])
        self.assertTrue(all(self.report["state"].values()))
        observations = self.report["state_observations"]
        self.assertEqual(observations["pitch_history_samples_after_250_frames"], 480)
        self.assertEqual(observations["max_queue_depth_during_process"], 5)
        self.assertEqual(observations["queue_depth_after_drain"], 0)

    def test_19_adverse_controls_complete(self) -> None:
        self.assertTrue(self.report["controls_all_pass"])
        adverse = self.report["adverse"]
        state_controls = ("missing_frame", "wrong_frame_shape", "short_frame",
                          "zero_length_frame", "nonfinite_input", "infinite_input",
                          "stale_epoch", "invalid_epoch", "duplicate_packet",
                          "out_of_order_packet")
        for name in state_controls:
            self.assertIn(name, adverse)
            self.assertTrue(adverse[name]["state_unchanged"])
        for name in ("order_recovery", "concealment_zero_valid_output",
                     "final_short_frame", "pitch_state_and_output",
                     "erase_burst_length", "erase_boundary"):
            self.assertIn(name, adverse)
        self.assertTrue(adverse["erase_burst_length"]["over_max_state_unchanged"])
        self.assertTrue(adverse["erase_burst_length"]["over_max_accepted"])
        self.assertTrue(adverse["erase_boundary"]["leading_zero_valid_output"])
        self.assertEqual(adverse["final_short_frame"]["samples"], 37)
        self.assertEqual(adverse["erase_burst_length"]["over_max_status"],
                         "rejected_burst_length")
        self.assertEqual(adverse["concealment_zero_valid_output"]["valid_content_samples"],
                         39 * fx.FRAME_SAMPLES)
        self.assertEqual(adverse["erase_boundary"]["trailing_unresolved_frames"], 2)

    def test_20_pitch_specific_state_and_output(self) -> None:
        pitch = self.report["adverse"]["pitch_state_and_output"]
        stats = pitch["per_condition"]["pitch_period_repeat"]
        self.assertEqual(stats["pitch_est_calls"], 11)
        self.assertEqual(stats["pitch_voiced_frames"], 9)
        self.assertEqual(stats["pitch_fallback_frames"], 2)
        self.assertEqual(stats["pitch_repeated_samples"], 9 * fx.FRAME_SAMPLES)
        self.assertEqual(stats["concealed_frames"], 11)
        self.assertTrue(pitch["finite_bounded_output"])
        self.assertTrue(all(self.report["adverse"]["pitch_state_and_output"][
            "per_condition"][name]["pitch_est_calls"] == 0
            for name in CONDITIONS[:-1]))
        boundary = self.report["adverse"]["erase_boundary"]
        self.assertEqual(boundary["leading_pitch_voiced_frames"], 0)
        self.assertEqual(boundary["leading_pitch_fallback_frames"], 1)
        self.assertTrue(boundary["leading_zero_fill_fallback_explicit"])

    def test_21_blockers_and_evidence_classes(self) -> None:
        blocked = {b["id"] for b in self.report["blockers"]}
        self.assertEqual(blocked, {
            "real_clean_reference", "authorized_listening",
            "target_runtime_timing", "codec_network_pipeline",
            "generative_plc_assets"})
        self.assertTrue(all(b["status"] == "blocked" and b["reopen"]
                            for b in self.report["blockers"]))
        classes = self.report["evidence_classes"]
        self.assertEqual(classes["unpaired_predictive_or_listening"], "none")
        self.assertEqual(classes["real_audio_rights_qualified"], "none")

    def test_22_runtime_measurements_are_pointer_only(self) -> None:
        measurements = json.loads(MEASUREMENTS.read_text())
        self.assertTrue(measurements["non_deterministic"])
        self.assertEqual(measurements["qualification_status"], "blocked")
        self.assertIsNone(measurements["deadline_ns"])
        self.assertEqual(measurements["base_commit"], fx.BASE_COMMIT)
        self.assertEqual(set(measurements["per_condition"]), set(CONDITIONS))


class BoundaryTests(unittest.TestCase):
    def test_23_missing_scorer_is_never_substituted(self) -> None:
        real_import = builtins.__import__

        def blocked_import(name, *args, **kwargs):
            if name == "pystoi" or name.startswith("pystoi."):
                raise ImportError("blocked for test")
            return real_import(name, *args, **kwargs)

        builtins.__import__ = blocked_import
        try:
            value, reason = fx.stoi_score((0.1, 0.2), (0.1, 0.2))
        finally:
            builtins.__import__ = real_import
        self.assertIsNone(value)
        self.assertEqual(reason, "missing_pinned_scorer")

    def test_24_invalid_inputs_have_no_score(self) -> None:
        self.assertEqual(fx.si_sdr_db(None, (0.0, 1.0))[1],
                         "missing_reference_or_output")
        self.assertEqual(fx.stoi_score((0.1,), (0.1, 0.2))[1], "invalid_input")
        self.assertEqual(fx.si_sdr_db((0.0, 0.0), (0.1, 0.2))[1], "zero_reference")

    def test_25_invalid_frames_are_rejected_before_state_change(self) -> None:
        session = fx.PitchRepeatPlcSession(fx.PlcConfig(epoch=3))
        baseline = {k: v for k, v in session.stats.items()
                    if not k.startswith("rejected_")}
        bad_frames = (
            None,
            {"first_input_sample": 0, "samples": ((0.0,),) * fx.FRAME_SAMPLES},
            {"first_input_sample": 0, "samples": (0.0,) * (fx.FRAME_SAMPLES - 1)},
            {"first_input_sample": 0, "samples": (), "valid_count": 0},
            {"first_input_sample": 0,
             "samples": (float("nan"),) * fx.FRAME_SAMPLES},
            {"first_input_sample": 0,
             "samples": (float("inf"),) * fx.FRAME_SAMPLES},
            {**fx.form_packet_stream(fx.clean_speech(320))[0], "epoch": 2},
        )
        for frame in bad_frames:
            result = session.process(frame)
            self.assertNotEqual(result.status, "ok")
        after = {k: v for k, v in session.stats.items()
                 if not k.startswith("rejected_")}
        self.assertEqual(after, baseline)
        self.assertEqual(session.history, [])
        session.close()

    def test_26_silence_and_unvoiced_fall_back_to_zero_fill(self) -> None:
        session = fx.PitchRepeatPlcSession()
        for frame in fx.form_packet_stream(fx.clean_speech(), fx.ERASURE_PLAN,
                                           method="pitch"):
            self.assertEqual(session.process(dict(frame)).status, "ok")
        session.drain()
        decisions = {item["frame"]: item for item in session.pitch_decisions}
        for frame in (150, 190):
            self.assertFalse(decisions[frame]["voiced"])
            self.assertEqual(decisions[frame]["period"], None)
        self.assertEqual(session.stats["pitch_fallback_frames"], 2)
        self.assertEqual(session.stats["pitch_repeated_samples"],
                         9 * fx.FRAME_SAMPLES)
        session.close()

    def test_27_estimator_rejects_short_silence_and_noise(self) -> None:
        self.assertEqual(fx.estimate_pitch((0.1,) * 160).reason,
                         "insufficient_context")
        self.assertEqual(fx.estimate_pitch((0.0,) * 480).reason, "silence")
        self.assertIsNone(fx.estimate_pitch(
            fx.unvoiced_chunk(480, fx.SEED_PROBE)).period)

    def test_28_leading_erasure_uses_explicit_zero_fill_fallback(self) -> None:
        session = fx.PitchRepeatPlcSession()
        result = session.process({
            "first_input_sample": 0,
            "present": False,
            "samples": (0.0,) * fx.FRAME_SAMPLES,
            "valid_count": 0,
            "method": "pitch",
        })
        self.assertEqual(result.status, "ok")
        drained = session.drain()
        conceal = [item for item in drained if item.is_concealment]
        self.assertTrue(conceal)
        self.assertTrue(all(item.valid_count == 0 for item in conceal))
        self.assertEqual(session.stats["pitch_fallback_frames"], 1)
        self.assertEqual(session.pitch_decisions[0]["reason"], "insufficient_context")
        session.close()

    def test_29_frame_after_max_burst_is_accepted(self) -> None:
        session = fx.PitchRepeatPlcSession(fx.PlcConfig(epoch=1))
        for index in range(fx.MAX_BURST_FRAMES):
            result = session.process({
                "first_input_sample": index * fx.FRAME_SAMPLES,
                "present": False,
                "samples": (0.0,) * fx.FRAME_SAMPLES,
                "valid_count": 0,
                "method": "pitch",
            })
            self.assertEqual(result.status, "ok")
        source = dict(fx.form_packet_stream(
            fx.clean_speech(fx.FRAME_SAMPLES * 6))[5])
        source["first_input_sample"] = fx.MAX_BURST_FRAMES * fx.FRAME_SAMPLES
        before = session.stats["accepted_valid_samples"]
        recovered = session.process(dict(source))
        self.assertEqual(recovered.status, "ok")
        self.assertEqual(session.stats["accepted_valid_samples"] - before,
                         fx.FRAME_SAMPLES)
        self.assertEqual(session.consecutive_erased, 0)
        session.close()

    def test_30_final_partial_frame_carries_padding_flag(self) -> None:
        frames = fx.form_packet_stream(fx.clean_speech(fx.FRAME_SAMPLES * 8 + 37))
        session = fx.PitchRepeatPlcSession()
        results = [session.process(dict(frame)) for frame in frames]
        results.extend(session.drain())
        final = results[-1]
        self.assertEqual(final.status, "ok")
        self.assertEqual(final.valid_count, 37)
        self.assertTrue(final.flags & fx.FLAG_FINAL_PADDING)
        self.assertEqual(sum(r.valid_count for r in results), 8 * fx.FRAME_SAMPLES + 37)
        session.close()

    def test_31_config_rejects_out_of_range_tuning(self) -> None:
        with self.assertRaises(ValueError):
            fx.PitchRepeatPlcSession(fx.PlcConfig(pitch_min_lag=39))
        with self.assertRaises(ValueError):
            fx.PitchRepeatPlcSession(fx.PlcConfig(pitch_repeat_gain=0.5))
        with self.assertRaises(ValueError):
            fx.PitchRepeatPlcSession(fx.PlcConfig(max_burst_frames=5))


if __name__ == "__main__":
    unittest.main()
