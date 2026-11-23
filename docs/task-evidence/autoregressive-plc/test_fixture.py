# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the synthetic autoregressive PLC fixture.

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
CONDITIONS = ("identity_clean", "zero_fill_noisy_control",
              "linear_interpolation_baseline", "autoregressive_plc")


def pinned_scorer_available() -> bool:
    try:
        import numpy  # noqa: F401
        import pystoi  # noqa: F401
        import importlib.metadata
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
        self.assertEqual(hashlib.sha256(module.read_bytes()).hexdigest(), pin["sha256"])

    def test_03_baseline_pin_matches_pinned_git_blob(self) -> None:
        pin = fx.BASELINE_PIN if hasattr(fx, "BASELINE_PIN") else {
            "commit": fx.BASELINE_COMMIT,
            "path": fx.BASELINE_PATH,
            "sha256": fx.BASELINE_SHA256,
        }
        try:
            raw = subprocess.run(
                ["git", "-C", str(SDK_ROOT), "show",
                 f"{pin['commit']}:{pin['path']}"],
                check=True, capture_output=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("baseline git blob unavailable in this checkout")
        self.assertEqual(hashlib.sha256(raw).hexdigest(), pin["sha256"])


class DeterminismTests(unittest.TestCase):
    def test_04_generated_report_is_byte_identical(self) -> None:
        if not pinned_scorer_available():
            self.skipTest("pinned scorer not installed")
        self.assertEqual(fx.canonical_report_bytes(fx.build_report()),
                         REPORT.read_bytes())

    def test_05_clean_reference_digest_is_stable(self) -> None:
        digest = fx.tensor_digest(fx.clean_speech())
        self.assertEqual(digest, json.loads(REPORT.read_text())["cohort"]["clean_digest"])
        self.assertEqual(fx.tensor_digest(fx.clean_speech()), digest)

    def test_06_stream_is_repeatable(self) -> None:
        frames = fx.form_packet_stream(fx.clean_speech(), fx.ERASURE_PLAN,
                                       method="ar")
        digests = []
        for _ in range(2):
            results, _ = fx.run_stream(frames)
            digests.append(fx.tensor_digest(
                fx.reconstruct(results, fx.SCORED_SAMPLES)))
        self.assertEqual(digests[0], digests[1])

    def test_07_fixture_spec_digest_matches(self) -> None:
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
            "ar_order": fx.AR_ORDER,
            "ar_context_samples": fx.AR_CONTEXT_SAMPLES,
            "ar_ridge_relative": fx.AR_RIDGE_RELATIVE,
            "ar_ridge_absolute": fx.AR_RIDGE_ABSOLUTE,
            "ar_bound_factor": fx.AR_BOUND_FACTOR,
            "ar_output_clamp": fx.AR_OUTPUT_CLAMP,
            "scored_frames": fx.SCORED_FRAMES,
            "erasure_plan": list(fx.ERASURE_PLAN),
            "strata": fx.STRATA,
            "adversarial_erasures": fx.ADVERSARIAL_ERASURES,
            "seeds": {"speech": fx.SEED_SPEECH, "noise": fx.SEED_NOISE},
            "source_pins": {p["path"]: p["sha256"] for p in fx.SOURCE_PINS},
            "scorer_pins": [dict(p) for p in fx.SCORER_PINS],
            "baseline_pin": {
                "commit": fx.BASELINE_COMMIT,
                "path": fx.BASELINE_PATH,
                "sha256": fx.BASELINE_SHA256,
            },
            "base_commit": fx.BASE_COMMIT,
        }
        self.assertEqual(fx.object_digest(spec), report["fixture_digest"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text())

    def test_08_profile_status_and_v0_geometry(self) -> None:
        self.assertEqual(self.report["profile"], "Enhancement")
        self.assertEqual(self.report["candidate_status"],
                         "proposal_only_synthetic_incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        fmt = self.report["format"]
        self.assertEqual((fmt["sample_rate_hz"], fmt["channels"],
                          fmt["sample_format"], fmt["frame_samples"]),
                         (16000, 1, "f32", 160))

    def test_09_counts_and_cohort(self) -> None:
        cohort = self.report["cohort"]
        self.assertEqual(cohort["frames"], 250)
        self.assertEqual(cohort["samples"], 40000)
        self.assertEqual(cohort["duration_seconds"], 2.5)
        self.assertEqual(cohort["erased_frame_count"], 9)
        self.assertEqual(cohort["erased_sample_count"], 1440)
        self.assertEqual(set(self.report["conditions"]), set(CONDITIONS))
        for name, condition in self.report["conditions"].items():
            self.assertEqual(condition["counts"]["produced_frames"], 255)
            self.assertEqual(condition["input"]["samples"], 40000)
            self.assertEqual(condition["output"]["samples"], 40000)
            self.assertEqual(condition["counts"]["concealed_frames"],
                             0 if name == "identity_clean" else 9)

    def test_10_all_metrics_available_and_outputs_valid(self) -> None:
        self.assertTrue(self.report["all_metrics_available"])
        self.assertTrue(self.report["all_outputs_finite"])
        for condition in self.report["conditions"].values():
            self.assertTrue(condition["all_metrics_available"])
            self.assertTrue(condition["output"]["finite"])
            self.assertEqual(condition["output"]["nonfinite_count"], 0)
            self.assertEqual(condition["output"]["at_or_above_one_count"], 0)
            self.assertLess(condition["output"]["peak_abs"], 1.0)
            self.assertTrue(condition["clean_preservation"]["valid_samples_bit_identical"])
            self.assertEqual(condition["clean_preservation"]["valid_sample_mismatches"], 0)

    def test_11_identity_and_paired_controls(self) -> None:
        identity = self.report["conditions"]["identity_clean"]
        self.assertIsNone(identity["si_sdr_db"]["candidate"])
        self.assertIn("exact_reconstruction", identity["si_sdr_db"]["invalid_reasons"])
        self.assertEqual(identity["stoi"]["candidate"], 1.0)
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

    def test_12_established_baselines_and_candidate(self) -> None:
        conditions = self.report["conditions"]
        zero = conditions["zero_fill_noisy_control"]
        linear = conditions["linear_interpolation_baseline"]
        ar = conditions["autoregressive_plc"]
        self.assertGreater(linear["si_sdr_db"]["candidate"],
                           zero["si_sdr_db"]["candidate"])
        self.assertGreater(ar["si_sdr_db"]["candidate"],
                           zero["si_sdr_db"]["candidate"])
        self.assertLess(ar["lost_region"]["concealed_rmse"],
                        zero["lost_region"]["concealed_rmse"])
        self.assertIsNotNone(ar["stoi"]["candidate"])
        self.assertTrue(all(conditions[name]["clean_preservation"]["valid_samples_bit_identical"]
                            for name in CONDITIONS))

    def test_13_erasure_stratification_complete(self) -> None:
        strata = self.report["erasure_stratification"]["strata"]
        self.assertEqual(set(strata), set(fx.STRATA))
        covered = [frame for stratum in strata.values()
                   for frame in stratum["erased_frames"]]
        self.assertEqual(sorted(covered), list(fx.ERASURE_PLAN))
        for name, stratum in strata.items():
            self.assertEqual(stratum["erased_samples"],
                             len(stratum["erased_frames"]) * fx.FRAME_SAMPLES)
            self.assertEqual(set(stratum["per_condition_rmse"]), set(CONDITIONS))
            for condition in stratum["per_frame_rmse"].values():
                self.assertEqual(set(condition),
                                 {str(f) for f in stratum["erased_frames"]})
            self.assertEqual(stratum["per_condition_rmse"]["identity_clean"], 0.0)
        self.assertTrue(self.report["erasure_stratification"][
            "identity_is_exact_on_erased_intervals"])
        self.assertEqual(self.report["erasure_stratification"]["all_erased_samples"],
                         1440)

    def test_14_decoded_intervals_and_duration(self) -> None:
        intervals = self.report["decoded_intervals"]["autoregressive_plc"]
        conceal_frames = sum(run["frames"] for run in intervals["runs"]
                             if run["kind"] == fx.KIND_CONCEAL)
        self.assertEqual(conceal_frames, 9)
        self.assertTrue(all(run["flags"] == [fx.FLAG_CONCEALMENT]
                            for run in intervals["runs"]
                            if run["kind"] == fx.KIND_CONCEAL))
        self.assertEqual(intervals["decoded_samples"], 40000)
        self.assertEqual(intervals["decoded_duration_s"], 2.5)
        self.assertEqual(intervals["valid_content_samples"], 38560)
        self.assertEqual(intervals["concealed_frames"], 9)
        self.assertEqual(intervals["invalid_zero_length_frames"], 0)
        availability = self.report["availability"]["autoregressive_plc"]
        self.assertEqual(availability["buffering_delay_samples"], 800)
        self.assertEqual(availability["first_valid_output_call_index"], 5)

    def test_15_alignment_state_and_memory(self) -> None:
        self.assertTrue(self.report["alignment_pass"])
        self.assertEqual(self.report["alignment"]["measured_content_lag_samples"], 0)
        self.assertTrue(self.report["alignment"]["source_mapping_checks"])
        self.assertEqual(self.report["alignment"]["ar_algorithm_intrinsic_delay_samples"], 0)
        self.assertTrue(self.report["state_pass"])
        self.assertTrue(all(self.report["state"].values()))
        observations = self.report["state_observations"]
        self.assertEqual(observations["ar_history_samples_after_250_frames"], 128)
        self.assertEqual(observations["max_queue_depth_during_process"], 5)

    def test_16_adverse_controls_complete(self) -> None:
        self.assertTrue(self.report["controls_all_pass"])
        adverse = self.report["adverse"]
        for name in ("missing_frame", "wrong_frame_shape", "short_frame",
                     "zero_length_frame", "nonfinite_input", "stale_epoch",
                     "invalid_epoch", "duplicate_packet", "out_of_order_packet",
                     "erase_burst_length", "erase_boundary",
                     "concealment_zero_valid_output", "final_short_frame"):
            self.assertIn(name, adverse)
        self.assertEqual(adverse["final_short_frame"]["samples"], 37)
        self.assertEqual(adverse["erase_burst_length"]["over_max_status"],
                         "rejected_burst_length")
        self.assertEqual(adverse["concealment_zero_valid_output"]["valid_content_samples"],
                         39 * fx.FRAME_SAMPLES)
        self.assertEqual(adverse["erase_boundary"]["trailing_unresolved_frames"], 2)

    def test_17_ar_specific_controls(self) -> None:
        ar = self.report["adverse"]["ar_state_and_output"]
        stats = ar["per_condition"]["autoregressive_plc"]
        self.assertEqual(stats["ar_synth_frames"], 9)
        self.assertEqual(stats["ar_solver_fallback_frames"], 0)
        self.assertEqual(stats["concealed_frames"], 9)
        self.assertTrue(ar["finite_clamped_output"])
        boundary = self.report["adverse"]["erase_boundary"]
        self.assertEqual(boundary["leading_ar_synth_frames"], 0)
        self.assertEqual(boundary["leading_ar_fallback_frames"], 1)
        self.assertTrue(boundary["leading_zero_fill_fallback_explicit"])

    def test_18_blockers_and_evidence_classes(self) -> None:
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

    def test_19_runtime_measurements_are_pointer_only(self) -> None:
        measurements = json.loads(MEASUREMENTS.read_text())
        self.assertTrue(measurements["non_deterministic"])
        self.assertEqual(measurements["qualification_status"], "blocked")
        self.assertIsNone(measurements["deadline_ns"])
        self.assertEqual(measurements["base_commit"], fx.BASE_COMMIT)
        self.assertEqual(set(measurements["per_condition"]), set(CONDITIONS))


class BoundaryTests(unittest.TestCase):
    def test_20_missing_scorer_is_never_substituted(self) -> None:
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

    def test_21_invalid_inputs_have_no_score(self) -> None:
        self.assertEqual(fx.si_sdr_db(None, (0.0, 1.0))[1],
                         "missing_reference_or_output")
        self.assertEqual(fx.stoi_score((0.1,), (0.1, 0.2))[1], "invalid_input")
        self.assertEqual(fx.si_sdr_db((0.0, 0.0), (0.1, 0.2))[1], "zero_reference")

    def test_22_invalid_frames_are_rejected_before_state_change(self) -> None:
        session = fx.AutoRegressivePlcSession(fx.PlcConfig(epoch=3))
        baseline = {k: v for k, v in session.stats.items()
                    if not k.startswith("rejected_")}
        bad_frames = (
            None,
            {"first_input_sample": 0, "samples": ((0.0,),) * fx.FRAME_SAMPLES},
            {"first_input_sample": 0, "samples": (0.0,) * (fx.FRAME_SAMPLES - 1)},
            {"first_input_sample": 0, "samples": (), "valid_count": 0},
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

    def test_23_ar_solver_is_bounded_and_falls_back(self) -> None:
        coeff = fx.solve_toeplitz((4.0, 2.0, 1.0, 0.5), 3, 1e-5)
        self.assertIsNotNone(coeff)
        self.assertTrue(all(isinstance(v, float) and abs(v) < 1e3 for v in coeff))
        self.assertIsNone(fx.solve_toeplitz((0.0, 0.0, 0.0), 2, 0.0))
        session = fx.AutoRegressivePlcSession()
        zeros = session._ar_synthesize(fx.FRAME_SAMPLES)
        self.assertEqual(zeros, (0.0,) * fx.FRAME_SAMPLES)
        self.assertEqual(session.stats["ar_solver_fallback_frames"], 1)

    def test_24_frame_after_max_burst_is_accepted(self) -> None:
        session = fx.AutoRegressivePlcSession(fx.PlcConfig(epoch=1))
        for index in range(fx.MAX_BURST_FRAMES):
            result = session.process({
                "first_input_sample": index * fx.FRAME_SAMPLES,
                "present": False,
                "samples": (0.0,) * fx.FRAME_SAMPLES,
                "valid_count": 0,
                "method": "ar",
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


if __name__ == "__main__":
    unittest.main()
