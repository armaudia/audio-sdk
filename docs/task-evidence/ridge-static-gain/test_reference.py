# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the synthetic static-gain held-out fixture.

Run with the pinned Python 3.12 scorer environment:

    PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import reference as fx

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
REPORT = HERE / "report.json"
DIGEST = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
PY_FILES = ("reference.py", "run.py", "test_reference.py", "verify.py")
PY312 = "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12"


def strict_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"),
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError("nonfinite JSON " + value)))


class PinTests(unittest.TestCase):
    def test_01_source_pins_match_recorded_bytes(self) -> None:
        for pin in fx.SOURCE_PINS:
            with self.subTest(path=pin["path"]):
                root = SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT
                path = root / pin["path"]
                self.assertTrue(path.is_file(), f"missing {path}")
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 pin["sha256"])

    def test_02_research_digest_is_exact(self) -> None:
        pin = next(p for p in fx.SOURCE_PINS
                   if p["path"] == "research/level_tone_control_20261028.md")
        path = SOURCE_ROOT / pin["path"]
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44")

    def test_03_artifact_pins_match_task_files(self) -> None:
        for pin in fx.artifact_pins():
            with self.subTest(path=pin["path"]):
                self.assertEqual(hashlib.sha256(
                    (HERE / pin["path"]).read_bytes()).hexdigest(),
                    pin["sha256"])

    def test_04_manifest_covers_all_pins(self) -> None:
        lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
                 if line and not line.startswith("#")]
        expected = len(fx.SOURCE_PINS) + len(fx.artifact_pins()) + 3
        self.assertEqual(len(lines), expected)
        for line in lines:
            digest, raw_path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            root = SOURCE_ROOT if raw_path.startswith("source:") else SDK_ROOT
            relative = raw_path.split(":", 1)[1] if ":" in raw_path else raw_path
            path = root / relative
            self.assertTrue(path.is_file(), f"missing {path}")
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
        text = PINS.read_text(encoding="utf-8")
        self.assertIn("docs/task-evidence/ridge-static-gain/report.json", text)
        self.assertIn("docs/task-evidence/ridge-static-gain/report.json.sha256", text)
        self.assertIn("docs/task-evidence/ridge-static-gain/README.md", text)

    def test_05_spdx_headers_on_every_new_python_file(self) -> None:
        for name in PY_FILES:
            with self.subTest(path=name):
                head = "\n".join((HERE / name).read_text(
                    encoding="utf-8").splitlines()[:4])
                self.assertIn(SPDX_LICENSE_LINE, head)
                self.assertIn(SPDX_COPYRIGHT_LINE, head)

    def test_06_digest_file_matches_report_bytes(self) -> None:
        digest, name = DIGEST.read_text(encoding="ascii").strip().split("  ", 1)
        self.assertEqual(name, "report.json")
        self.assertEqual(digest, hashlib.sha256(REPORT.read_bytes()).hexdigest())


class DeterminismTests(unittest.TestCase):
    def test_07_report_is_byte_reproducible(self) -> None:
        self.assertEqual(fx.canonical_report_bytes(fx.build_report()),
                         REPORT.read_bytes())

    def test_08_generation_repeats_exactly(self) -> None:
        self.assertEqual(fx.tensor_digest(fx.make_clip(199)),
                         fx.tensor_digest(fx.make_clip(199)))
        self.assertEqual(fx.tensor_digest(fx.perturb(fx.make_clip(199), 199)[0]),
                         fx.tensor_digest(fx.perturb(fx.make_clip(199), 199)[0]))
        expected = fx.tensor_digest(fx.perturb(fx.make_clip(199), 199)[0])
        report = strict_json(REPORT)
        actual = next(item["input_digest"]
                      for item in report["held_out"]["per_clip"]
                      if item["clip_index"] == 199)
        self.assertEqual(expected, actual)

    def test_09_fixture_spec_digest_matches(self) -> None:
        report = strict_json(REPORT)
        spec = {
            "contract": fx.CONTRACT_ID,
            "schema": fx.SCHEMA_ID,
            "sample_rate_hz": fx.SAMPLE_RATE_HZ,
            "channels": fx.CHANNELS,
            "sample_format": fx.SAMPLE_FORMAT,
            "frame_samples": fx.FRAME_SAMPLES,
            "buffering_delay_samples": fx.BUFFERING_DELAY_SAMPLES,
            "target_rms_db": fx.TARGET_RMS_DB,
            "peak_ceiling": fx.PEAK_CEILING,
            "max_gain": fx.MAX_GAIN,
            "ridge_lambda": fx.RIDGE_LAMBDA,
            "train_clips": fx.TRAIN_CLIPS,
            "held_out_clips": fx.HELD_OUT_CLIPS,
            "clip_samples": fx.CLIP_SAMPLES,
            "seed": fx.SEED_CORPUS,
            "perturbation_db_range": [fx.PERTURBATION_DB_MIN,
                                      fx.PERTURBATION_DB_MAX],
            "source_pins": {pin["path"]: pin["sha256"]
                            for pin in fx.SOURCE_PINS},
            "artifact_pins": {pin["path"]: pin["sha256"]
                              for pin in fx.artifact_pins()},
            "base_commit": fx.BASE_COMMIT,
        }
        self.assertEqual(fx.object_digest(spec), report["fixture_digest"])

    def test_10_run_script_regenerates_byte_identically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "report.json"
            result = subprocess.run(
                [PY312, str(HERE / "run.py"), str(target)],
                cwd=str(HERE), capture_output=True, text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=True)
            self.assertEqual(target.read_bytes(), REPORT.read_bytes())
            self.assertIn(f"report_sha256={hashlib.sha256(REPORT.read_bytes()).hexdigest()}",
                          result.stdout)
            self.assertEqual((target.with_name("report.json.sha256")).read_bytes(),
                             DIGEST.read_bytes())


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_11_profile_status_boundary_and_v0_geometry(self) -> None:
        report = self.report
        self.assertEqual(report["profile"], "DSP")
        self.assertEqual(report["candidate_status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["no_missing_result_qualifies_candidate"])
        fmt = report["format"]
        self.assertEqual((fmt["sample_rate_hz"], fmt["channels"],
                          fmt["sample_format"], fmt["frame_samples"]),
                         (16000, 1, "f32", 160))
        self.assertEqual(fmt["buffering_delay_samples"], 0)
        boundary = report["boundary"]
        self.assertFalse(boundary["registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertFalse(boundary["default_selected"])
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_12_no_default_strategy_is_advertised(self) -> None:
        report = self.report
        for key in ("default_strategy", "selected_strategy", "recommended_strategy"):
            self.assertNotIn(key, report)
            self.assertNotIn(key, report["strategy_settings"])
        self.assertEqual(set(report["held_out"]["aggregates"]), set(fx.STRATEGIES))

    def test_13_split_is_disjoint_and_frozen(self) -> None:
        split = self.report["split"]
        self.assertEqual((split["train_clips"], split["held_out_clips"]),
                         (fx.TRAIN_CLIPS, fx.HELD_OUT_CLIPS))
        self.assertEqual(split["overlap"], 0)
        self.assertEqual(split["train_indices"], [0, fx.TRAIN_CLIPS - 1])
        self.assertEqual(split["held_out_indices"],
                         [fx.TRAIN_CLIPS, fx.TRAIN_CLIPS + fx.HELD_OUT_CLIPS - 1])
        items = self.report["held_out"]["per_clip"]
        self.assertEqual([item["clip_index"] for item in items],
                         list(range(fx.TRAIN_CLIPS,
                                    fx.TRAIN_CLIPS + fx.HELD_OUT_CLIPS)))

    def test_14_ridge_fit_is_finite_and_train_only(self) -> None:
        model = self.report["ridge_fit"]
        self.assertEqual(model["lambda"], fx.RIDGE_LAMBDA)
        self.assertEqual(model["train_items"], fx.TRAIN_CLIPS)
        self.assertEqual(model["feature"], "log10(measured clip RMS)")
        self.assertTrue(all(math.isfinite(model[key])
                            for key in ("slope", "intercept", "mean_x", "mean_y")))
        self.assertEqual(len(model["train_feature_digest"]), 64)
        self.assertEqual(len(model["train_label_digest"]), 64)

    def test_15_held_out_aggregates_and_ceiling_behavior(self) -> None:
        agg = self.report["held_out"]["aggregates"]
        self.assertLess(agg[fx.STRATEGY_TARGET]["mean_abs_rms_error_db"],
                        agg[fx.STRATEGY_NO_GAIN]["mean_abs_rms_error_db"])
        for strategy in (fx.STRATEGY_TARGET, fx.STRATEGY_RIDGE,
                         fx.STRATEGY_ENVELOPE):
            self.assertEqual(agg[strategy]["nonfinite_samples"], 0)
            self.assertLessEqual(agg[strategy]["max_peak"], fx.PEAK_CEILING + 1e-6)
            self.assertEqual(agg[strategy]["clipped_samples"], 0)
        self.assertTrue(agg[fx.STRATEGY_NO_GAIN]["clipped_samples"] >= 0)
        self.assertTrue(all(item["all_finite"] for item in agg.values()))

    def test_16_comparisons_are_paired_and_honest(self) -> None:
        comparisons = self.report["held_out"]["comparisons"]
        self.assertEqual(set(comparisons), {
            "ridge_minus_target_rms", "no_gain_minus_target_rms",
            "envelope_agc_minus_target_rms"})
        for name, comparison in comparisons.items():
            self.assertEqual(len(comparison["per_clip_delta_db"]),
                             fx.HELD_OUT_CLIPS)
            self.assertEqual(comparison["worse_clips"]
                             + comparison["no_worse_clips"], fx.HELD_OUT_CLIPS)
            self.assertTrue(math.isfinite(comparison["mean_abs_error_delta_db"]))
        self.assertGreater(comparisons["no_gain_minus_target_rms"]["worse_clips"], 0)

    def test_17_regressions_recorded_verbatim(self) -> None:
        regressions = self.report["held_out"]["regressions"]
        self.assertIsInstance(regressions, list)
        self.assertGreater(len(regressions), 0)
        for item in regressions:
            self.assertIn("strategy", item)
            self.assertIn("compared_with", item)
            self.assertIn("clip_index", item)
            self.assertIn("metric", item)
            self.assertTrue(math.isfinite(item["delta"]))
            self.assertTrue(item["interpretation"])
        self.assertTrue(any(item["strategy"] == fx.STRATEGY_TARGET
                            and item["compared_with"] == "uncapped_target"
                            for item in regressions))

    def test_18_evidence_classes_pinned_context_only(self) -> None:
        classes = self.report["evidence_classes"]
        self.assertEqual(classes["real_audio_rights_qualified"], "none")
        self.assertEqual(classes["unpaired_predictive_or_listening"], "none")
        self.assertIn("context only", classes["source_reported_context"])


class DspProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)
        cls.probes = cls.report["dsp_probes"]

    def test_19_sweep_gain_response_is_flat(self) -> None:
        sweep = self.probes["sweep"]
        self.assertEqual(len(sweep["band_gain_ratios"]), 10)
        self.assertLessEqual(sweep["response_flatness_db"], 1e-4)
        self.assertEqual(sweep["frames"], 200)
        self.assertEqual(sweep["cap_engaged_frames"], 0)

    def test_20_steps_static_gain_does_not_track(self) -> None:
        steps = self.probes["steps"]
        self.assertEqual(steps["static_gain_unique_values"], 1)
        self.assertEqual(len(steps["per_step_input_rms_db"]), 8)
        self.assertGreater(steps["envelope_control_unique_gain_values"], 1)
        self.assertLess(steps["per_step_input_rms_db"][0],
                        steps["per_step_input_rms_db"][5])

    def test_21_impulse_delay_and_mapping(self) -> None:
        impulse = self.probes["impulse"]
        self.assertEqual(impulse["source_peak_index"], 4000)
        self.assertEqual(impulse["measured_output_peak_index"], 4000)
        self.assertEqual(impulse["measured_content_delay_samples"], 0)
        self.assertEqual(impulse["declared_buffering_delay_samples"], 0)
        self.assertEqual(impulse["nonzero_output_samples"], 1)
        self.assertTrue(impulse["source_mapping_checks"])

    def test_22_silence_fallback_and_headroom(self) -> None:
        silence = self.probes["silence"]
        self.assertEqual(silence["fallback_gain"], 1.0)
        self.assertEqual(silence["output_peak"], 0.0)
        self.assertEqual(silence["headroom_linear"], fx.PEAK_CEILING)
        self.assertEqual(silence["nonfinite_count"], 0)

    def test_23_synthetic_speech_static_gain_and_no_gating(self) -> None:
        speech = self.probes["synthetic_speech"]
        self.assertEqual(speech["unique_gain_values"], 1)
        self.assertEqual(len(speech["per_region"]), 20)
        self.assertTrue({row["region"] for row in speech["per_region"]}
                        >= {"voiced", "unvoiced", "pause_floor"})
        self.assertIn("SNR is unchanged", speech["noise_floor_note"])
        control = self.probes["no_gain_control"]
        self.assertTrue(control["bit_identical_to_input"])
        self.assertEqual(control["gain"], 1.0)
        self.assertEqual(control["unique_gain_values"], 1)

    def test_24_headroom_peak_cap_not_hard_clipping(self) -> None:
        headroom = self.probes["headroom_peak"]
        self.assertTrue(headroom["cap_engaged"])
        self.assertGreater(headroom["input_peak"], fx.PEAK_CEILING)
        self.assertLess(headroom["raw_gain"], 1000.0)
        self.assertLessEqual(headroom["output_peak"], fx.PEAK_CEILING + 1e-6)
        self.assertEqual(headroom["output_at_or_above_one_count"], 0)
        self.assertGreaterEqual(headroom["headroom_linear"], -1e-6)

    def test_25_interacting_nonlinearity_state_control(self) -> None:
        interacting = self.probes["interacting_nonlinearity"]
        self.assertGreater(interacting["unique_gain_values"], 1)
        self.assertEqual(len(interacting["first_40_gain_trace"]), 40)
        self.assertTrue(all(math.isfinite(v)
                            for v in interacting["first_40_gain_trace"]))
        self.assertIn("Smoothing and ceiling interact",
                      interacting["note"])

    def test_26_final_partial_window(self) -> None:
        partial = self.report["final_partial_window"]
        self.assertEqual(partial["source_samples"], 7 * fx.FRAME_SAMPLES + 37)
        self.assertEqual(partial["final_frame_valid_count"], 37)
        self.assertTrue(partial["final_frame_flagged_final"])
        self.assertEqual(partial["result_flags"], [fx.FLAG_FINAL_PADDING])
        self.assertEqual(partial["valid_content_samples"], 1157)
        self.assertEqual(partial["produced_frames"], 8)
        self.assertTrue(partial["padding_bits_identical"])


class ValidityStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_27_adverse_frames_rejected_without_state_change(self) -> None:
        adverse = self.report["adverse"]
        for name in ("missing_frame", "wrong_frame_shape", "short_frame",
                     "zero_length_frame", "nonfinite_input", "stale_epoch",
                     "future_packet", "bad_padding", "duplicate_packet",
                     "out_of_order_packet", "process_after_final",
                     "closed_rejects_process", "invalid_gain_rejected"):
            self.assertIn(name, adverse)
            self.assertTrue(adverse[name]["state_unchanged"], name)
        self.assertEqual(adverse["nonfinite_input"]["status"],
                         "rejected_nonfinite")
        self.assertEqual(adverse["stale_epoch"]["status"],
                         "rejected_stale_epoch")
        self.assertEqual(adverse["future_packet"]["status"],
                         "rejected_future_packet")
        self.assertTrue(self.report["controls_complete"])

    def test_28_state_transitions_and_isolation(self) -> None:
        state = self.report["state"]
        self.assertTrue(all(state.values()))
        self.assertTrue(state["separate_sessions_uncoupled"])
        self.assertTrue(state["reset_accepted"])
        self.assertTrue(state["stale_epoch_after_reset_rejected"])
        self.assertTrue(state["reset_bit_identical_to_fresh_epoch2"])
        self.assertTrue(state["static_gain_invariant_across_frames"])
        self.assertTrue(state["envelope_state_changes_within_stream"])

    def test_29_qualification_gate_cannot_be_disabled(self) -> None:
        report = self.report
        self.assertTrue(all(block["status"] == "blocked"
                            for block in report["blockers"]))
        self.assertEqual(fx.qualification_state(report), "not_qualified")
        damaged = dict(report)
        damaged["held_out"] = dict(report["held_out"])
        damaged["held_out"]["per_clip"] = list(report["held_out"]["per_clip"])
        broken = dict(damaged["held_out"]["per_clip"][0])
        broken["finite"] = dict(broken["finite"])
        broken["finite"][fx.STRATEGY_TARGET] = False
        damaged["held_out"]["per_clip"][0] = broken
        with self.assertRaises(ValueError):
            fx.qualification_state({**damaged,
                                    "no_missing_result_qualifies_candidate": False})

    def test_30_gate_ids_and_reopen_conditions(self) -> None:
        blocked = {item["id"] for item in self.report["blockers"]}
        self.assertEqual(blocked, {
            "real_speech_benchmark", "blinded_listening_quality",
            "pinned_external_controls", "target_runtime_deadline",
            "provider_intake", "default_selection"})
        for item in self.report["blockers"]:
            self.assertTrue(item["reason"])
            self.assertTrue(item["reopen"])


if __name__ == "__main__":
    unittest.main()
