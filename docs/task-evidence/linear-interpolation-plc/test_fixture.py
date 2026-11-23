# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the synthetic linear-interpolation PLC fixture.

Run with the pinned Python 3.12 scorer environment from README.md:

    /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python -m unittest -v test_fixture.py
"""
from __future__ import annotations

import builtins
import hashlib
import json
import os
import unittest
from pathlib import Path

import fixture as fx

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
REPORT = HERE / "report.json"
MEASUREMENTS = HERE / "runtime-measurements.json"


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
                path = (SDK_ROOT / pin["path"] if pin["path"].startswith("api/")
                        else SOURCE_ROOT / pin["path"])
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(digest, pin["sha256"])

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


class DeterminismTests(unittest.TestCase):
    def test_03_generated_report_is_byte_identical(self) -> None:
        if not pinned_scorer_available():
            self.skipTest("pinned scorer not installed")
        generated = fx.canonical_report_bytes(fx.build_report())
        self.assertEqual(generated, REPORT.read_bytes())

    def test_04_clean_reference_digest_is_stable(self) -> None:
        digest = fx.tensor_digest(fx.clean_speech())
        self.assertEqual(digest, json.loads(REPORT.read_text())["cohort"]["clean_digest"])
        self.assertEqual(fx.tensor_digest(fx.clean_speech()), digest)

    def test_05_stream_is_repeatable(self) -> None:
        frames = fx.form_packet_stream(fx.clean_speech(), fx.ERASURE_PLAN)
        waves = []
        for _ in range(2):
            results, _ = fx.run_stream(frames)
            waves.append(fx.tensor_digest(fx.reconstruct(results, fx.SCORED_SAMPLES)))
        self.assertEqual(waves[0], waves[1])

    def test_06_fixture_spec_digest_matches(self) -> None:
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
            "scored_frames": fx.SCORED_FRAMES,
            "erasure_plan": list(fx.ERASURE_PLAN),
            "adversarial_erasures": fx.ADVERSARIAL_ERASURES,
            "seeds": {"speech": fx.SEED_SPEECH, "noise": fx.SEED_NOISE},
            "source_pins": {p["path"]: p["sha256"] for p in fx.SOURCE_PINS},
            "scorer_pins": [dict(p) for p in fx.SCORER_PINS],
            "base_commit": fx.BASE_COMMIT,
        }
        self.assertEqual(fx.object_digest(spec), report["fixture_digest"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text())

    def test_07_profile_and_status_are_proposal_only(self) -> None:
        self.assertEqual(self.report["profile"], "Enhancement")
        self.assertEqual(self.report["candidate_status"],
                         "proposal_only_synthetic_incomplete")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_08_counts_and_cohort(self) -> None:
        cohort = self.report["cohort"]
        self.assertEqual(cohort["frames"], 250)
        self.assertEqual(cohort["samples"], 40000)
        self.assertEqual(cohort["erased_frame_count"], 9)
        self.assertEqual(cohort["erased_sample_count"], 1440)
        for condition in self.report["conditions"].values():
            self.assertEqual(condition["counts"]["produced_frames"], 255)
            self.assertEqual(condition["input"]["samples"], 40000)
            self.assertEqual(condition["output"]["samples"], 40000)

    def test_09_alignment_state_and_controls_pass(self) -> None:
        self.assertTrue(self.report["alignment_pass"])
        self.assertEqual(self.report["alignment"]["measured_content_lag_samples"], 0)
        self.assertTrue(self.report["alignment"]["source_mapping_checks"])
        self.assertTrue(self.report["state_pass"])
        self.assertTrue(all(self.report["state"].values()))
        self.assertTrue(self.report["controls_all_pass"])
        for name in ("missing_frame", "short_frame", "nonfinite_input",
                     "wrong_frame_shape", "stale_epoch", "duplicate_packet",
                     "out_of_order_packet", "erase_burst_length", "erase_boundary",
                     "concealment_zero_valid_output", "final_short_frame"):
            self.assertIn(name, self.report["adverse"])

    def test_10_paired_metrics_and_baseline(self) -> None:
        conditions = self.report["conditions"]
        linear = conditions["linear_interpolation"]
        zero = conditions["zero_fill_baseline"]
        self.assertTrue(self.report["all_metrics_available"])
        self.assertGreater(linear["si_sdr_db"]["candidate"],
                           zero["si_sdr_db"]["candidate"])
        self.assertEqual(linear["si_sdr_db"]["paired_delta"],
                         round(linear["si_sdr_db"]["candidate"]
                               - linear["si_sdr_db"]["identity_noisy"], 6))
        self.assertLess(linear["lost_region"]["concealed_rmse"],
                        zero["lost_region"]["concealed_rmse"])
        self.assertIsNotNone(linear["stoi"]["candidate"])
        self.assertIsNotNone(linear["stoi"]["identity_noisy"])

    def test_11_outputs_are_finite_and_in_range(self) -> None:
        self.assertTrue(self.report["all_outputs_finite"])
        for condition in self.report["conditions"].values():
            self.assertTrue(condition["output"]["finite"])
            self.assertEqual(condition["output"]["nonfinite_count"], 0)
            self.assertEqual(condition["output"]["at_or_above_one_count"], 0)
            self.assertLess(condition["output"]["peak_abs"], 1.0)

    def test_12_blockers_and_evidence_classes(self) -> None:
        blocked = {b["id"] for b in self.report["blockers"]}
        self.assertEqual(blocked, {
            "real_clean_reference", "authorized_listening",
            "target_runtime_timing", "codec_network_pipeline"})
        self.assertTrue(all(b["status"] == "blocked" for b in self.report["blockers"]))
        classes = self.report["evidence_classes"]
        self.assertEqual(classes["unpaired_predictive_or_listening"], "none")
        self.assertEqual(classes["real_audio_rights_qualified"], "none")

    def test_13_runtime_measurements_are_pointer_only(self) -> None:
        measurements = json.loads(MEASUREMENTS.read_text())
        self.assertTrue(measurements["non_deterministic"])
        self.assertEqual(measurements["qualification_status"], "blocked")
        self.assertIsNone(measurements["deadline_ns"])
        self.assertEqual(measurements["base_commit"], fx.BASE_COMMIT)
        self.assertEqual(set(measurements["per_condition"]),
                         set(self.report["conditions"]))


class BoundaryTests(unittest.TestCase):
    def test_14_missing_scorer_is_never_substituted(self) -> None:
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

    def test_15_invalid_inputs_have_no_score(self) -> None:
        self.assertEqual(fx.si_sdr_db(None, (0.0, 1.0))[1],
                         "missing_reference_or_output")
        self.assertEqual(fx.stoi_score((0.1,), (0.1, 0.2))[1], "invalid_input")
        self.assertEqual(fx.si_sdr_db((0.0, 0.0), (0.1, 0.2))[1], "zero_reference")

    def test_16_invalid_frames_are_rejected_before_state_change(self) -> None:
        session = fx.LinearPlcSession(fx.PlcConfig(epoch=3))
        baseline = {k: v for k, v in session.stats.items()
                    if not k.startswith("rejected_")}
        bad_frames = (
            None,
            {"first_input_sample": 0, "samples": ((0.0,),) * fx.FRAME_SAMPLES},
            {"first_input_sample": 0, "samples": (0.0,) * (fx.FRAME_SAMPLES - 1)},
            {"first_input_sample": 0, "samples": (float("inf"),) * fx.FRAME_SAMPLES},
            {**fx.form_packet_stream(fx.clean_speech(320))[0], "epoch": 2},
        )
        for frame in bad_frames:
            result = session.process(frame)
            self.assertNotEqual(result.status, "ok")
        after = {k: v for k, v in session.stats.items()
                 if not k.startswith("rejected_")}
        self.assertEqual(after, baseline)


if __name__ == "__main__":
    unittest.main()
