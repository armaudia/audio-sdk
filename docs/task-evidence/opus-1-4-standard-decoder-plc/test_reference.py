# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the synthetic decoder-PLC-style reference fixture.

Run with the pinned Python 3.12 scorer environment:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
"""
from __future__ import annotations

import builtins
import hashlib
import importlib.metadata
import inspect
import json
import math
import os
import pathlib
import unittest
from pathlib import Path

import reference as fx

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
REPORT = HERE / "report.json"
REPORT_DIGEST = HERE / "report.json.sha256"
MEASUREMENTS = HERE / "runtime-measurements.json"
PINS = HERE / "SOURCES.sha256"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def pinned_scorer_available() -> bool:
    try:
        import numpy
        import pystoi  # noqa: F401
        return (importlib.metadata.version("pystoi") == "0.4.1"
                and numpy.__version__ == "2.5.4")
    except Exception:
        return False


def strict_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"),
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError("nonfinite JSON " + value)))


class PinTests(unittest.TestCase):
    def test_01_source_pins_hash_to_recorded_bytes(self) -> None:
        for pin in fx.SOURCE_PINS:
            with self.subTest(path=pin["path"]):
                root = SOURCE_ROOT if pin["root"] == "source" else SDK_ROOT
                path = root / pin["path"]
                self.assertTrue(path.is_file(), f"missing {path}")
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 pin["sha256"])

    def test_02_scorer_pin_matches_installed_module(self) -> None:
        pin = next(p for p in fx.SCORER_PINS if p["id"] == "pystoi")
        import numpy
        from pystoi import stoi
        self.assertEqual(importlib.metadata.version("pystoi"), pin["version"])
        self.assertEqual(numpy.__version__, "2.5.4")
        module = pathlib.Path(inspect.getfile(stoi))
        self.assertEqual(hashlib.sha256(module.read_bytes()).hexdigest(),
                         pin["sha256"])

    def test_03_artifact_pins_match_committed_task_files(self) -> None:
        for pin in fx.artifact_pins():
            with self.subTest(path=pin["path"]):
                self.assertEqual(hashlib.sha256(
                    (HERE / pin["path"]).read_bytes()).hexdigest(),
                    pin["sha256"])

    def test_04_sha256_manifest_covers_every_pinned_byte(self) -> None:
        lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
                 if line and not line.startswith("#")]
        expected = len(fx.SOURCE_PINS) + len(fx.artifact_pins()) + 4
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
        self.assertIn("docs/task-evidence/opus-1-4-standard-decoder-plc/report.json", text)
        self.assertIn("docs/task-evidence/opus-1-4-standard-decoder-plc/README.md", text)
        self.assertIn("docs/task-evidence/opus-1-4-standard-decoder-plc/report.json.sha256", text)
        self.assertIn("source:adapters/opus-plc/adapter.json", text)

    def test_05_spdx_headers_present_in_new_python_files(self) -> None:
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            with self.subTest(path=name):
                head = "\n".join((HERE / name).read_text(
                    encoding="utf-8").splitlines()[:4])
                self.assertIn(SPDX_LICENSE_LINE, head)
                self.assertIn(SPDX_COPYRIGHT_LINE, head)

    def test_06_report_digest_file_matches_committed_report(self) -> None:
        self.assertEqual(REPORT_DIGEST.read_text(encoding="utf-8").strip(),
                         hashlib.sha256(REPORT.read_bytes()).hexdigest())


class DeterminismTests(unittest.TestCase):
    def test_07_generated_report_is_byte_identical(self) -> None:
        self.assertTrue(pinned_scorer_available())
        self.assertEqual(fx.canonical_report_bytes(fx.build_report()),
                         REPORT.read_bytes())

    def test_08_clean_digest_and_stream_are_repeatable(self) -> None:
        clean = fx.clean_speech()
        digest = fx.tensor_digest(clean)
        self.assertEqual(digest, fx.tensor_digest(fx.clean_speech()))
        self.assertEqual(digest, strict_json(REPORT)["cohort"]["clean_digest"])
        frames = fx.form_packet_stream(clean, fx.ERASURE_PLAN)
        outputs = []
        for _ in range(2):
            results, _ = fx.run_stream(frames, method=fx.METHOD_PLC)
            outputs.append(fx.tensor_digest(fx.reconstruct(results, len(clean))))
        self.assertEqual(outputs[0], outputs[1])

    def test_09_fixture_spec_digest_matches(self) -> None:
        report = strict_json(REPORT)
        spec = {
            "contract": fx.CONTRACT_ID,
            "schema": fx.SCHEMA_ID,
            "sample_rate_hz": fx.SAMPLE_RATE_HZ,
            "channels": fx.CHANNELS,
            "sample_format": "f32",
            "frame_samples": fx.FRAME_SAMPLES,
            "buffering_frames": fx.BUFFERING_FRAMES,
            "buffering_delay_samples": fx.BUFFERING_DELAY_SAMPLES,
            "max_burst_frames": fx.MAX_BURST_FRAMES,
            "max_drain_calls": fx.MAX_DRAIN_CALLS,
            "scored_frames": fx.SCORED_FRAMES,
            "seed": fx.SEED_SPEECH,
            "regions": [list(region) for region in fx.REGIONS],
            "erasure_plan": list(fx.ERASURE_PLAN),
            "strata": fx.STRATA,
            "decay_gains_by_burst_frame": list(fx.DECAY_GAINS),
            "pitch_lag_range_samples": [fx.PITCH_LAG_MIN, fx.PITCH_LAG_MAX],
            "final_partial_samples": fx.FINAL_PARTIAL_SAMPLES,
            "source_pins": {pin["path"]: pin["sha256"] for pin in fx.SOURCE_PINS},
            "scorer_pins": [dict(pin) for pin in fx.SCORER_PINS],
            "artifact_pins": {pin["path"]: pin["sha256"] for pin in fx.artifact_pins()},
            "base_commit": fx.BASE_COMMIT,
        }
        self.assertEqual(fx.object_digest(spec), report["fixture_digest"])

    def test_10_json_reports_are_strict_and_finite(self) -> None:
        for path in (REPORT, MEASUREMENTS):
            data = strict_json(path)
            self.assertIsInstance(data, dict)
            self.assertEqual(data["base_commit"], fx.BASE_COMMIT)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_11_profile_status_and_v0_geometry(self) -> None:
        self.assertEqual(self.report["profile"], "Enhancement")
        self.assertEqual(self.report["supporting_profile"], "Restoration")
        self.assertEqual(self.report["candidate_status"],
                         "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        fmt = self.report["format"]
        self.assertEqual((fmt["sample_rate_hz"], fmt["channels"],
                          fmt["sample_format"], fmt["frame_samples"]),
                         (16000, 1, "f32", 160))
        boundary = self.report["boundary"]
        self.assertFalse(boundary["registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertEqual(boundary["descriptor_settings"], {})

    def test_12_control_roles_and_optional_selection(self) -> None:
        algorithm = self.report["algorithm"]
        self.assertEqual(algorithm["identity_control"], fx.IDENTITY_CONTROL)
        self.assertEqual(algorithm["degraded_noisy_control"], fx.DEGRADED_NOISY_CONTROL)
        self.assertEqual(algorithm["task_matched_baseline"], fx.TASK_MATCHED_BASELINE)
        self.assertEqual(algorithm["additional_controls"], ["hold_control"])
        self.assertEqual(algorithm["intrinsic_delay_samples"], 0)
        self.assertEqual(set(self.report["conditions"]), set(fx.CONDITIONS))

    def test_13_cohort_counts_and_erasure_plan(self) -> None:
        cohort = self.report["cohort"]
        self.assertEqual((cohort["frames"], cohort["samples"],
                          cohort["duration_seconds"]), (250, 40000, 2.5))
        self.assertEqual(cohort["erased_frames"], list(fx.ERASURE_PLAN))
        self.assertEqual(cohort["erased_frame_count"], len(fx.ERASURE_PLAN))
        self.assertEqual(cohort["erased_sample_count"],
                         len(fx.ERASURE_PLAN) * fx.FRAME_SAMPLES)
        for name, condition in self.report["conditions"].items():
            self.assertEqual(condition["counts"]["produced_frames"], 255)
            self.assertEqual(condition["counts"]["startup_padding_frames"], 5)
            self.assertEqual(condition["input"]["samples"], 40000)
            self.assertEqual(condition["output"]["samples"], 40000)
            self.assertEqual(condition["counts"]["concealed_frames"],
                             0 if name == fx.IDENTITY_CONTROL else len(fx.ERASURE_PLAN))

    def test_14_paired_scores_controls_and_peak_bounds(self) -> None:
        conditions = self.report["conditions"]
        self.assertTrue(self.report["all_metrics_available"])
        self.assertTrue(self.report["all_outputs_finite"])
        for condition in conditions.values():
            self.assertTrue(condition["all_metrics_available"])
            self.assertTrue(condition["output"]["finite"])
            self.assertEqual(condition["output"]["nonfinite_count"], 0)
            self.assertEqual(condition["output"]["at_or_above_one_count"], 0)
            self.assertLess(condition["output"]["peak_abs"], 1.0)
            self.assertTrue(condition["clean_preservation"]["valid_samples_bit_identical"])
            self.assertEqual(condition["clean_preservation"]["valid_sample_mismatches"], 0)
        identity = conditions[fx.IDENTITY_CONTROL]
        self.assertIsNone(identity["si_sdr_db"]["condition"])
        self.assertIn("exact_reconstruction", identity["si_sdr_db"]["invalid_reasons"])
        self.assertEqual(identity["stoi"]["condition"], 1.0)
        for name in fx.CONDITIONS[1:]:
            condition = conditions[name]
            self.assertIsNotNone(condition["si_sdr_db"]["condition"])
            self.assertIsNotNone(condition["stoi"]["condition"])
            self.assertIsNone(condition["si_sdr_db"]["paired_delta_vs_identity"])
            self.assertIn("exact_reconstruction",
                          condition["si_sdr_db"]["invalid_reasons"])
            self.assertEqual(condition["stoi"]["paired_delta_vs_identity"],
                             round(condition["stoi"]["condition"]
                                   - condition["stoi"]["identity_clean"], 6))
        for control in fx.CONTROL_CONDITIONS:
            comparison = self.report["comparisons"][control]
            for key in ("candidate_minus_control_si_sdr_db",
                        "candidate_minus_control_stoi",
                        "candidate_minus_control_concealed_rmse"):
                self.assertIsNotNone(comparison[key])
            self.assertEqual(set(comparison["per_stratum_concealed_rmse_delta"]),
                             set(fx.STRATA))
        self.assertIsInstance(self.report["regressions"], list)

    def test_15_strata_content_classes_and_boundaries(self) -> None:
        self.assertTrue(self.report["strata_complete"])
        by_burst = self.report["erasure_stratification"]["by_burst_length"]
        self.assertEqual(set(by_burst), set(fx.STRATA))
        covered = [frame for stratum in by_burst.values()
                   for frame in stratum["erased_frames"]]
        self.assertEqual(sorted(covered), list(fx.ERASURE_PLAN))
        for stratum in by_burst.values():
            self.assertEqual(set(stratum["per_condition_rmse"]), set(fx.CONDITIONS))
        content = self.report["erasure_stratification"]["by_content_and_boundary"]
        self.assertEqual(set(content["by_content_class"]),
                         {"voiced", "unvoiced", "silence"})
        self.assertEqual(set(content["onset_offset"]), {"onset", "offset"})
        self.assertEqual(len(content["per_erased_frame"]), len(fx.ERASURE_PLAN))
        self.assertTrue(self.report["erasure_stratification"][
            "identity_is_exact_on_erased_intervals"])

    def test_16_decoded_intervals_duration_and_alignment(self) -> None:
        intervals = self.report["decoded_intervals"][fx.CANDIDATE_CONDITION]
        conceal_frames = sum(run["frames"] for run in intervals["runs"]
                             if run["kind"] == fx.KIND_CONCEAL)
        self.assertEqual(conceal_frames, len(fx.ERASURE_PLAN))
        self.assertEqual(intervals["decoded_samples"], 40000)
        self.assertEqual(intervals["decoded_duration_s"], 2.5)
        self.assertEqual(intervals["valid_content_samples"],
                         40000 - len(fx.ERASURE_PLAN) * fx.FRAME_SAMPLES)
        self.assertEqual(intervals["invalid_zero_length_frames"], 0)
        availability = self.report["availability"][fx.CANDIDATE_CONDITION]
        self.assertEqual(availability["buffering_delay_samples"], 800)
        self.assertEqual(availability["first_valid_output_call_index"], 5)
        self.assertTrue(self.report["alignment_pass"])
        alignment = self.report["alignment"]
        self.assertEqual(alignment["measured_raw_peak_index"], 4800)
        self.assertEqual(alignment["expected_raw_peak_index"], 4800)
        self.assertEqual(alignment["measured_content_lag_samples"], 0)
        self.assertEqual(alignment["candidate_intrinsic_delay_samples"], 0)
        self.assertTrue(alignment["source_mapping_checks"])

    def test_17_final_partial_window(self) -> None:
        self.assertTrue(self.report["partial_window_pass"])
        partial = self.report["final_partial_window"]
        self.assertEqual(partial["source_samples"], 8 * 160 + 37)
        self.assertEqual(partial["last_frame_valid_count"], 37)
        self.assertTrue(partial["last_frame_flagged_final"])
        self.assertEqual(partial["clean_preservation_valid_mismatches"], 0)
        self.assertEqual(partial["produced_frames"][fx.CANDIDATE_CONDITION], 14)
        for name, value in partial["per_condition_rmse_over_partial_window"].items():
            self.assertIsNotNone(value)
            self.assertGreaterEqual(value, 0.0)

    def test_18_adverse_controls_complete(self) -> None:
        self.assertTrue(self.report["controls_all_pass"])
        adverse = self.report["adverse"]
        for name in ("missing_frame", "wrong_frame_shape", "short_frame",
                     "zero_length_frame", "nonfinite_input", "stale_epoch",
                     "future_packet", "bad_padding", "invalid_reset_epoch",
                     "duplicate_packet", "out_of_order_packet", "order_recovery",
                     "closed_rejects_further_process", "process_after_final",
                     "erase_burst_length", "erase_boundary",
                     "concealment_zero_valid_output", "final_short_frame"):
            self.assertIn(name, adverse)
        self.assertEqual(adverse["stale_epoch"]["status"], "rejected_stale_epoch")
        self.assertEqual(adverse["future_packet"]["status"], "rejected_future_packet")
        self.assertEqual(adverse["nonfinite_input"]["status"], "rejected_nonfinite")
        self.assertEqual(adverse["bad_padding"]["status"], "rejected_bad_padding")
        self.assertEqual(adverse["erase_burst_length"]["over_max_status"],
                         "rejected_burst_length")
        self.assertEqual(adverse["concealment_zero_valid_output"]["concealment_flags"],
                         [fx.FLAG_CONCEALMENT])
        self.assertEqual(adverse["final_short_frame"]["samples"], 37)

    def test_19_state_reset_and_session_independence(self) -> None:
        self.assertTrue(self.report["state_pass"])
        for name, value in self.report["state"].items():
            self.assertTrue(value, name)
        boundary = self.report["adverse"]["erase_boundary"]
        self.assertEqual(boundary["leading_erasure_status"], "ok")
        self.assertEqual(boundary["leading_zero_valued_fallback_frames"], 1)
        self.assertEqual(boundary["trailing_fallback_frames"], 2)
        self.assertEqual(boundary["boundary_burst_concealed"], 4)

    def test_20_no_missing_result_can_qualify_candidate(self) -> None:
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        damaged = dict(self.report)
        damaged["conditions"] = dict(self.report["conditions"])
        first = next(iter(damaged["conditions"]))
        damaged["conditions"][first] = dict(damaged["conditions"][first])
        damaged["conditions"][first]["all_metrics_available"] = False
        self.assertEqual(fx.qualification_state(damaged), "not_qualified")
        with self.assertRaises(ValueError):
            fx.qualification_state({**damaged,
                                    "no_missing_result_qualifies_candidate": False})

    def test_21_blockers_and_evidence_classes(self) -> None:
        blocked = {item["id"] for item in self.report["blockers"]}
        self.assertEqual(blocked, {
            "real_clean_reference", "authorized_listening_wer_stoi",
            "codec_network_fec_trace", "opus_runtime_rights",
            "target_runtime_timing", "provider_intake"})
        for item in self.report["blockers"]:
            self.assertEqual(item["status"], "blocked")
            self.assertTrue(item["reason"])
            self.assertTrue(item["reopen"])
        classes = self.report["evidence_classes"]
        self.assertEqual(classes["unpaired_predictive_or_listening"], "none")
        self.assertEqual(classes["real_audio_rights_qualified"], "none")

    def test_22_timing_pointer_is_non_qualifying(self) -> None:
        pointer = self.report["timing_pointer"]
        self.assertTrue(pointer["non_deterministic"])
        self.assertEqual(pointer["qualification_status"], "blocked")
        self.assertEqual(pointer["pacing"], "unpaced")
        self.assertIsNone(pointer["deadline_ns"])
        measurements = strict_json(MEASUREMENTS)
        self.assertTrue(measurements["non_deterministic"])
        self.assertEqual(measurements["qualification_status"], "blocked")
        self.assertIsNone(measurements["deadline_ns"])
        self.assertEqual(set(measurements["per_condition"]), set(fx.CONDITIONS))

    def test_23_opus_provenance_is_context_only(self) -> None:
        provenance = self.report["opus_provenance"]
        self.assertFalse(provenance["claims_made"])
        self.assertFalse(provenance["documented_binary"]["used_by_fixture"])
        self.assertFalse(provenance["documented_binary"]["present_in_this_workspace"])
        self.assertFalse(provenance["source_reported_scores_pooled"])
        self.assertEqual(provenance["external_cli_tools_found"], [])
        self.assertIn("libopus 1.4", provenance["documented_binary"]["documented_version"])
        self.assertIn("source:adapters/opus-plc/adapter.json",
                      PINS.read_text(encoding="utf-8"))


class BoundaryTests(unittest.TestCase):
    def test_24_missing_scorer_is_never_substituted(self) -> None:
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

    def test_25_invalid_inputs_have_no_score(self) -> None:
        self.assertEqual(fx.si_sdr_db(None, (0.0, 1.0))[1],
                         "missing_reference_or_output")
        self.assertEqual(fx.stoi_score((0.1,), (0.1, 0.2))[1], "invalid_input")
        self.assertEqual(fx.si_sdr_db((0.0, 0.0), (0.1, 0.2))[1], "zero_reference")

    def test_26_invalid_frames_do_not_change_state(self) -> None:
        session = fx.DecoderPlcSession(fx.PlcConfig(epoch=3))
        baseline = {k: v for k, v in session.stats.items()
                    if not k.startswith("rejected_")}
        bad_frames = (
            None,
            {"first_input_sample": 0, "samples": ((0.0,),) * fx.FRAME_SAMPLES},
            {"first_input_sample": 0, "samples": (0.0,) * (fx.FRAME_SAMPLES - 1)},
            {"first_input_sample": 0, "samples": (), "valid_count": 0},
            {"first_input_sample": 0, "samples": (float("inf"),) * fx.FRAME_SAMPLES},
            {**fx.form_packet_stream(fx.clean_speech(fx.FRAME_SAMPLES))[0],
             "epoch": 2},
            {**fx.form_packet_stream(fx.clean_speech(fx.FRAME_SAMPLES))[0],
             "first_input_sample": 160},
        )
        for frame in bad_frames:
            self.assertNotEqual(session.process(frame).status, "ok")
        self.assertEqual({k: v for k, v in session.stats.items()
                          if not k.startswith("rejected_")}, baseline)
        session.close()

    def test_27_plc_concealment_is_causal_zero_valid_and_finite(self) -> None:
        clean = fx.clean_speech(fx.FRAME_SAMPLES * 6)
        frames = fx.form_packet_stream(clean, (2,))
        results, _ = fx.run_stream(frames, method=fx.METHOD_PLC)
        concealed = [r for r in results if r.is_concealment]
        self.assertEqual(len(concealed), 1)
        self.assertEqual(concealed[0].flags, fx.FLAG_CONCEALMENT)
        self.assertEqual(concealed[0].valid_count, 0)
        self.assertEqual(len(concealed[0].samples), fx.FRAME_SAMPLES)
        self.assertNotEqual(concealed[0].samples, (0.0,) * fx.FRAME_SAMPLES)
        self.assertNotEqual(concealed[0].samples, clean[2 * fx.FRAME_SAMPLES:
                                                       3 * fx.FRAME_SAMPLES])
        self.assertTrue(all(math.isfinite(v) for v in concealed[0].samples))
        self.assertEqual(sum(r.valid_count for r in results),
                         len(clean) - fx.FRAME_SAMPLES)

    def test_28_burst_decay_is_fixed_and_bounded(self) -> None:
        self.assertEqual(len(fx.DECAY_GAINS), fx.MAX_BURST_FRAMES)
        self.assertTrue(all(0.0 < gain <= 1.0 for gain in fx.DECAY_GAINS))
        self.assertTrue(all(left > right for left, right
                            in zip(fx.DECAY_GAINS, fx.DECAY_GAINS[1:])))
        session = fx.DecoderPlcSession(method=fx.METHOD_PLC)
        frames = fx.form_packet_stream(fx.clean_speech(fx.FRAME_SAMPLES * 20),
                                       (5, 6, 7, 8))
        for frame in frames:
            result = session.process(dict(frame))
            self.assertEqual(result.status, "ok")
        session.drain()
        self.assertEqual(session.stats["plc_frames"], fx.MAX_BURST_FRAMES)
        self.assertEqual(session.consecutive_erased, 0)
        session.close()

    def test_29_pitch_estimator_is_deterministic_and_in_range(self) -> None:
        voiced = fx.clean_speech()[10 * fx.FRAME_SAMPLES:11 * fx.FRAME_SAMPLES]
        lag = fx.estimate_pitch_lag(voiced)
        self.assertIsNotNone(lag)
        self.assertIn(lag, range(fx.PITCH_LAG_MIN, fx.PITCH_LAG_MAX + 1))
        self.assertEqual(lag, fx.estimate_pitch_lag(voiced))
        self.assertIsNone(fx.estimate_pitch_lag((0.0,) * fx.FRAME_SAMPLES))

    def test_30_burst_cap_and_order_recovery(self) -> None:
        session = fx.DecoderPlcSession(fx.PlcConfig(epoch=1))
        for index in range(fx.MAX_BURST_FRAMES):
            result = session.process({
                "first_input_sample": index * fx.FRAME_SAMPLES,
                "present": False, "samples": (0.0,) * fx.FRAME_SAMPLES,
                "valid_count": 0})
            self.assertEqual(result.status, "ok")
        before = session.stats["accepted_valid_samples"]
        overflow = session.process({
            "first_input_sample": fx.MAX_BURST_FRAMES * fx.FRAME_SAMPLES,
            "present": False, "samples": (0.0,) * fx.FRAME_SAMPLES,
            "valid_count": 0})
        self.assertEqual(overflow.status, "rejected_burst_length")
        self.assertEqual(session.stats["accepted_valid_samples"], before)
        source = dict(fx.form_packet_stream(
            fx.clean_speech(fx.FRAME_SAMPLES * 6))[5])
        source["first_input_sample"] = fx.MAX_BURST_FRAMES * fx.FRAME_SAMPLES
        recovered = session.process(source)
        self.assertEqual(recovered.status, "ok")
        self.assertEqual(session.consecutive_erased, 0)
        session.close()


if __name__ == "__main__":
    unittest.main()
