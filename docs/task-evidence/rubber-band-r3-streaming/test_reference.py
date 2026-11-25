# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the task-local rubber-band R3 evidence."""

from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import fixture
import reference
import scorer

TASK_DIR = Path(__file__).resolve().parent
REPORT_FILE = TASK_DIR / "report.json"
SIDECAR_FILE = TASK_DIR / "report.json.sha256"
HEADER_FILE = TASK_DIR / "provider" / "expected_vectors.h"


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
        cls.sidecar = SIDECAR_FILE.read_text(encoding="ascii").strip()

    def test_report_is_strict_canonical_and_sidecar_matches(self):
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(REPORT_FILE.read_bytes(), (text + "\n").encode("utf-8"))
        self.assertEqual(self.sidecar, digest)
        self.assertEqual(len(digest), 64)

    def test_report_regeneration_is_byte_identical(self):
        text, digest = reference.canonical_report(scorer.build_report())
        self.assertEqual((text + "\n").encode("utf-8"), REPORT_FILE.read_bytes())
        self.assertEqual(digest, self.sidecar)

    def test_report_status_and_qualification(self):
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["disposition"], "incomplete")
        q = self.report["qualification"]
        self.assertEqual(q["decision"], "DEFER")
        self.assertEqual(q["processor_exposure"], "deferred")
        self.assertFalse(q["candidate_qualified"])
        self.assertFalse(q["missing_result_promoted"])
        self.assertTrue(q["all_required_results_present"])
        tool = self.report["tool_profile"]
        self.assertTrue(tool["environment_independent"])
        for key in ("install_location", "runner_python", "runner_platform"):
            self.assertNotIn(key, tool)

    def test_scope_flags(self):
        scope = self.report["scope"]
        self.assertTrue(scope["task_local_only"])
        for key in ("public_surface_changed", "installed_behavior_changed",
                    "descriptor_or_registry_changed", "shared_cmake_changed",
                    "board_or_handoff_changed", "real_rubber_band_source_or_binary",
                    "model_weights", "licensed_runtime", "real_corpus",
                    "playback_device", "listening_or_release_claim"):
            self.assertFalse(scope[key], key)

    def test_source_and_boundary_pins_verified(self):
        for section in ("source_pins", "boundary_pins"):
            for relative, row in self.report[section].items():
                self.assertTrue(row["verified"], relative)
                self.assertEqual(row["sha256"], row["actual"], relative)
                self.assertTrue((TASK_DIR / relative).is_file(), relative)

    def test_frozen_fixtures_verified(self):
        for name, row in self.report["frozen_fixtures"].items():
            self.assertTrue(row["verified"], name)
            self.assertEqual(row["sha256"], row["actual"], name)

    def test_required_sections_present(self):
        for key in ("stimuli", "variants", "parameter_grid", "frequency_scale",
                    "transient_proxy", "rate_updates", "streaming",
                    "final_partial", "c_boundary_expected", "rate_profile",
                    "invalid_and_adverse", "blockers", "release_gates"):
            self.assertTrue(self.report[key], key)

    def test_stimuli_finite_and_bounded(self):
        for name, row in self.report["stimuli"].items():
            self.assertEqual(row["nonfinite_count"], 0, name)
            self.assertEqual(row["clipping_count"], 0, name)
            self.assertLessEqual(row["peak_abs"], 1.0, name)
            self.assertEqual(row["samples"], reference.STIMULUS_LENGTH, name)

    def test_all_variants_present_and_finite(self):
        labels = set(fixture.FIXTURE_CASE_IDS)
        for name, rows in self.report["variants"].items():
            self.assertEqual(set(rows), labels, name)
            for label, row in rows.items():
                self.assertEqual(row["nonfinite_count"], 0, name + label)
                self.assertEqual(row["clipping_count"], 0, name + label)
                self.assertLessEqual(row["peak_abs"], 1.0, name + label)
                self.assertFalse(row["qualifies"])

    def test_identity_control_has_deterministic_shortfall(self):
        for name, rows in self.report["variants"].items():
            row = rows["identity_1x_control"]
            self.assertEqual(row["duration_error_samples"], -41.0, name)
            self.assertFalse(self.report["rate_profile"]["one_x_and_rate_changes"][
                "identity_digest_equals_input"])

    def test_duration_gate_is_recorded_as_failed(self):
        duration = self.report["rate_profile"]["duration"]
        self.assertFalse(duration["one_ms_per_second_gate_pass"])
        self.assertEqual(set(duration["failing_cases"]),
                         {"silence", "tonal", "speech_like", "music_like"})
        self.assertFalse(self.report["qualification"]["duration_gate_pass"])

    def test_frequency_proxy_rows(self):
        scale = self.report["frequency_scale"]
        rows = scale["rows"]
        self.assertEqual(scale["input_sampling"], "mapped_from_output_after_stretch")
        for label in ("identity_1x_control", "candidate_dynamic_wsola_ola",
                      "alignment_disabled_control"):
            self.assertTrue(rows[label]["pitch_preserved"], label)
            self.assertLessEqual(rows[label]["absolute_error"], 0.03, label)
        self.assertFalse(rows["varispeed_adverse"]["pitch_preserved"])
        self.assertGreater(rows["varispeed_adverse"]["frequency_ratio"], 1.15)
        self.assertGreater(rows["varispeed_adverse"]["mapped_source_interval"][0],
                           scale["analysis"]["start"])

    def test_transient_proxy_is_not_audibility(self):
        rows = self.report["transient_proxy"]["rows"]
        self.assertEqual(set(rows), {"tonal", "speech_like", "music_like"})
        for name, row in rows.items():
            self.assertTrue(row["proxy_only"], name)
            self.assertFalse(row["audibility_measured"], name)
            for key in ("candidate", "alignment_disabled_control", "varispeed_adverse"):
                self.assertEqual(row[key]["status"], "ok", name + key)

    def test_parameter_grid_and_invalid_subset(self):
        grid = self.report["parameter_grid"]
        self.assertEqual(len(grid["rows"]),
                         len(reference.ALLOWED_GRAIN_SAMPLES) *
                         len(reference.ALLOWED_OVERLAP_RATIOS) *
                         len(reference.ALLOWED_DENSITIES))
        for key, row in grid["rows"].items():
            self.assertEqual(row["nonfinite_count"], 0, key)
            self.assertLessEqual(row["peak_abs"], 1.0, key)
            self.assertGreater(row["window_sum_min"], 0.0, key)
        invalid = grid["invalid_cases"]
        for label in ("missing_parameter_set", "invalid_grain_size", "invalid_overlap",
                      "invalid_density_zero", "invalid_density_divisor",
                      "missing_rate_selection", "nonfinite_rate", "nan_rate",
                      "rate_out_of_range", "nonfinite_input", "missing_valid_input"):
            self.assertEqual(invalid[label]["status"], "rejected", label)

    def test_rate_update_boundaries_and_smoothness(self):
        updates = self.report["rate_updates"]
        self.assertEqual(updates["boundaries"], [3200, 6400, 9600])
        cand = updates["smoothness"]["candidate_dynamic_wsola_ola"]
        adv = updates["smoothness"]["unsmoothed_step_adverse"]
        self.assertLessEqual(cand["observed_max_step"], reference.MAX_RATE_STEP + 1e-12)
        self.assertGreater(adv["observed_max_step"], reference.MAX_RATE_STEP)
        for name, row in updates["rows"].items():
            for boundary in ("3200", "6400", "9600"):
                self.assertEqual(row[boundary]["candidate_dynamic_wsola_ola"]["status"], "ok", name)

    def test_streaming_chunking_reset_and_rejections(self):
        streaming = self.report["streaming"]
        self.assertTrue(streaming["one_output_frame_per_input_frame"])
        self.assertTrue(streaming["chunking"]["byte_identical"])
        self.assertTrue(streaming["reset_replay"]["state_replay_identical"])
        self.assertTrue(streaming["reset_replay"]["source_offset_respected"])
        self.assertTrue(streaming["session_independence"]["different_digest"])
        for label in ("nonfinite_input", "missing_valid_input", "wrong_shape",
                      "wrong_position", "process_after_final", "out_of_range"):
            self.assertEqual(streaming["frame_rejections"][label]["status"], "rejected", label)

    def test_final_partial_and_c_boundary(self):
        final = self.report["final_partial"]
        self.assertEqual(final["final_input_frame_start"],
                         (reference.STIMULUS_LENGTH // reference.FRAME_SAMPLES) *
                         reference.FRAME_SAMPLES)
        self.assertEqual(final["final_input_valid_count"],
                         reference.STIMULUS_LENGTH % reference.FRAME_SAMPLES)
        self.assertTrue(final["final_source_offset_ok"])
        tail = reference.analytic_stimulus("speech_like")[
            final["final_input_frame_start"]:]
        self.assertEqual(final["final_input_digest"],
                         reference.tensor_digest(tail))
        self.assertEqual(final["nonfinite_count"], 0)
        c = self.report["c_boundary_expected"]
        self.assertEqual(c["content_digest"], "5717e525060b71b3c72360f2d53111fc1a9a2f6d833a3f005fbcdc0df20fd569")
        self.assertEqual(c["content_samples"], 10294)
        self.assertEqual(c["frames"], 78)
        self.assertEqual(c["first_output_frame"], 3)
        self.assertEqual(c["first_output_input_frame_start"], 480)
        self.assertEqual(c["model_undelivered_fifo_samples"], 970)
        self.assertEqual(c["parity_scope"], "process_bytes_and_frame_shape_only")
        self.assertEqual(c["v0_source_mapping"], "unsupported")
        self.assertEqual(c["v0_tail_drain"], "unsupported")
        self.assertNotIn("drain_non_content_samples", c)
        self.assertNotIn("first_output_source_samples", c)
        self.assertEqual(len(c["valid_counts"]), 78)

    def test_header_matches_expected(self):
        header = HEADER_FILE.read_text(encoding="utf-8")
        expected = self.report["c_boundary_expected"]
        for token in (expected["content_digest"], str(expected["content_samples"]),
                      str(expected["frames"]), str(expected["first_output_frame"])):
            self.assertIn(token, header)
        self.assertNotIn("RB3_EXPECTED_DRAIN_NON_CONTENT_SAMPLES", header)
        self.assertIn("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes", header)
        self.assertIn("SPDX" "-License-Identifier: Apache-2.0", header)

    def test_invalid_and_adverse_cases(self):
        invalid = self.report["invalid_and_adverse"]
        self.assertGreaterEqual(len(invalid), 16)
        for label, row in invalid.items():
            self.assertEqual(row["status"], "rejected", label)
            self.assertFalse(row["candidate_qualified"], label)

    def test_rate_profile_speech_music_silence_and_policy(self):
        profile = self.report["rate_profile"]
        self.assertEqual(profile["unfamiliar_speech"]["status"], "synthetic_formant_surrogate_only")
        self.assertFalse(profile["unfamiliar_speech"]["real_speech"])
        self.assertEqual(profile["music"]["status"], "synthetic_chord_and_beat_surrogate_only")
        self.assertFalse(profile["music"]["recording"])
        self.assertEqual(profile["silence"]["status"], "synthetic_zero_stimulus")
        self.assertTrue(profile["silence"]["finite_output"])
        self.assertTrue(profile["pause_filler_decisions"]["all_policy_rows_ok"])
        self.assertTrue(profile["pause_filler_decisions"]["all_rate_decisions_at_source_timestamps"])
        self.assertFalse(profile["speech_preservation"]["intelligibility_or_listening_measured"])

    def test_drift_rebuffer_and_playback_buffering(self):
        profile = self.report["rate_profile"]
        drift = profile["drift"]
        self.assertEqual(drift["case"], "drift_control")
        self.assertEqual(drift["observed_output_samples"],
                         self.report["variants"]["speech_like"]["drift_control"][
                             "output_samples"])
        self.assertNotEqual(drift["observed_output_samples"],
                            self.report["variants"]["speech_like"][
                                "candidate_dynamic_wsola_ola"]["output_samples"])
        rebuffer = profile["rebuffer"]
        trace = rebuffer["trace"]
        self.assertEqual(rebuffer["case"], "rebuffer_control_with_input_gap")
        self.assertGreater(len(trace["gap_rows"]), 0)
        self.assertTrue(all(trace["rows"][index]["input_frame_start"] is None
                            for index in trace["gap_rows"]))
        self.assertGreater(trace["gap_delivered_samples"], 0)
        self.assertGreater(trace["refill_first_delivered"], 0)
        self.assertFalse(rebuffer["target_device_recovery_measured"])
        pb = profile["playback_buffering"]
        self.assertTrue(pb["one_output_frame_per_input_frame"])
        self.assertEqual(pb["alignment_lookahead_samples"], 0)
        self.assertEqual(pb["v0_source_mapping"], "unsupported")
        self.assertEqual(pb["v0_tail_drain"], "unsupported")
        self.assertIn("model_undelivered_fifo_samples", pb)
        self.assertNotIn("drain_non_content_samples", pb)
        self.assertFalse(pb["target_device_buffer_occupancy_measured"])
        self.assertFalse(pb["fill_flush_or_deadline_measured"])

    def test_contract_adapter_provider_json_are_strict(self):
        for name in ("contract.json", "adapter.json", "provider.json"):
            obj = fixture.strict_load(TASK_DIR / name)
            self.assertIsInstance(obj, dict, name)

    def test_source_pins_match_reference(self):
        for section, recomputed in (
                ("source_pins", fixture.verify_source_pins()),
                ("boundary_pins", fixture.verify_boundary_pins())):
            self.assertEqual(self.report[section], recomputed, section)
            for relative, expected in getattr(reference, section.upper()).items():
                actual = reference.sha256_file(TASK_DIR / relative)
                self.assertEqual(actual, expected, relative)

    def test_invalid_cases_function_returns_rejections(self):
        cases = reference.invalid_cases()
        for label in ("missing_parameter_set", "invalid_grain_size", "invalid_overlap",
                      "invalid_density_zero", "missing_rate_selection", "nonfinite_rate",
                      "nan_rate", "rate_out_of_range", "invalid_config", "nonfinite_input",
                      "missing_valid_input", "wrong_shape", "wrong_position",
                      "process_after_final", "out_of_range", "missing_final_input"):
            self.assertEqual(cases[label]["status"], "rejected", label)
            self.assertIsNotNone(cases[label]["code"], label)
        self.assertFalse(any(row["status"] == "unexpected_acceptance"
                             for row in cases.values()))
        self.assertEqual(self.report["invalid_and_adverse"], cases)

    def test_state_invariant_on_rejection(self):
        stream = reference.StreamTSM(reference.DYNAMIC_SCHEDULE)
        stream.push([0.0] * reference.FRAME_SAMPLES, reference.FRAME_SAMPLES)
        before = stream.state_digest()
        with self.assertRaises(reference.ReferenceRejection):
            stream.push([math.nan] + [0.0] * (reference.FRAME_SAMPLES - 1), reference.FRAME_SAMPLES)
        self.assertEqual(stream.state_digest(), before)

    def test_chunked_and_whole_are_identical(self):
        values = reference.analytic_stimulus("speech_like")
        whole, _, _ = reference.run_tsm(values, schedule=reference.DYNAMIC_SCHEDULE,
                                        chunk_size=len(values) + reference.FRAME_SAMPLES)
        chunked, _, _ = reference.run_tsm(values, schedule=reference.DYNAMIC_SCHEDULE)
        self.assertEqual(reference.tensor_digest(whole), reference.tensor_digest(chunked))

    def test_reset_replay_identical(self):
        a = reference.StreamTSM(reference.DYNAMIC_SCHEDULE, first_input_sample=50000)
        b = reference.StreamTSM(reference.DYNAMIC_SCHEDULE, first_input_sample=50000)
        for _ in range(5):
            a.push([0.0] * reference.FRAME_SAMPLES, reference.FRAME_SAMPLES)
            b.push([0.0] * reference.FRAME_SAMPLES, reference.FRAME_SAMPLES)
        self.assertEqual(a.state_digest(), b.state_digest())

    def test_parameter_grid_api(self):
        for grain in reference.ALLOWED_GRAIN_SAMPLES:
            for ratio in reference.ALLOWED_OVERLAP_RATIOS:
                overlap = reference.round_half_away(grain * ratio)
                for density in reference.ALLOWED_DENSITIES:
                    params = reference.validate_parameters({
                        "grain_samples": grain, "overlap_samples": overlap, "density": density})
                    self.assertGreater(params["synth_hop_samples"], 0)

    def test_run_py_generates_clean_checkout_outputs(self):
        with tempfile.TemporaryDirectory(prefix="rb3-") as tmp:
            root = Path(tmp)
            for path in TASK_DIR.rglob("*"):
                rel = path.relative_to(TASK_DIR)
                dest = root / rel
                if path.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dest)
            subprocess.run([sys.executable, "run.py", "--report"], cwd=root, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            subprocess.run([sys.executable, "run.py", "--sources"], cwd=root, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            sidecar = (root / "report.json.sha256").read_text(encoding="ascii").strip()
            self.assertEqual(reference.canonical_report(report)[1], sidecar)
            self.assertTrue((root / "SOURCES.sha256").is_file())

    def test_sources_manifest_matches_tree(self):
        manifest = fixture.read_sources_manifest()
        expected = {}
        for path in sorted(TASK_DIR.rglob("*")):
            rel = path.relative_to(TASK_DIR).as_posix()
            if rel == "SOURCES.sha256" or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path.is_file():
                expected[rel] = reference.sha256_file(path)
        self.assertEqual(manifest, expected)

    def test_board_snapshot_is_mutable_provenance(self):
        board = self.report["board_snapshot"]
        self.assertTrue(board["mutable"])
        self.assertIn("provenance", board["note"].lower())
        self.assertEqual(board["sha256_at_read"], reference.BOARD_SHA256_AT_READ)
        self.assertNotIn("actual", board)

    def test_release_gates_and_blockers_present(self):
        self.assertGreaterEqual(len(self.report["release_gates"]), 5)
        self.assertGreaterEqual(len(self.report["blockers"]), 5)
        ids = {b["id"] for b in self.report["blockers"]}
        self.assertEqual(ids, {"BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05"})


if __name__ == "__main__":
    unittest.main()
