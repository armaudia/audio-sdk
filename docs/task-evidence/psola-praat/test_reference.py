# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the task-local PSOLA/Praat fixture.

Run from this directory with:
  PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
No external package, corpus, model, SDK build or network access is needed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import reference
import run as generator

TASK_DIR = Path(__file__).resolve().parent
WORKTREE = TASK_DIR.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]
REPORT_FILE = TASK_DIR / "report.json"
SIDECAR_FILE = TASK_DIR / "report.json.sha256"
HEADER_FILE = TASK_DIR / "provider" / "expected_vectors.h"
TEMP_ROOT = "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode"


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
        cls.sidecar = SIDECAR_FILE.read_text(encoding="ascii").strip()

    def test_committed_report_is_canonical_and_digest_matches(self):
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(REPORT_FILE.read_bytes(), (text + "\n").encode("utf-8"))
        self.assertEqual(self.sidecar, digest)
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, reference.sha256_bytes(text.encode("utf-8")))

    def test_report_regeneration_is_byte_identical(self):
        text, digest = reference.canonical_report(reference.build_report())
        self.assertEqual((text + "\n").encode("utf-8"), REPORT_FILE.read_bytes())
        self.assertEqual(digest, self.sidecar)

    def test_source_pins_are_verified(self):
        for relative, row in self.report["source_pins"].items():
            self.assertTrue(row["verified"], relative)
            self.assertEqual((AUDIO_ROOT / relative).is_file(), True, relative)
            self.assertEqual(row["sha256"], row["actual"], relative)

    def test_boundary_pins_are_verified(self):
        for relative, row in self.report["boundary_pins"].items():
            self.assertTrue(row["verified"], relative)
            self.assertEqual(row["sha256"], row["actual"], relative)

    def test_declared_evidence_paths_are_pinned(self):
        for relative in ("research/tsm-followup-20261101/README.md",
                         "REALTIME_COMPONENT_CANDIDATES.md",
                         "audio-benchmark-platform/plan/swarm/VERIFICATION.md"):
            self.assertIn(relative, self.report["source_pins"])

    def test_required_sections_are_present_and_fixture_only(self):
        for key in ("stimuli", "pitch_marking", "variants", "frequency_scale",
                    "overlap_add", "rate_updates", "drift_rebuffer",
                    "slow_r_whole_clip", "transient_proxy", "streaming",
                    "final_partial", "playback_buffering", "c_boundary_expected",
                    "blockers"):
            self.assertTrue(self.report[key], key)
        self.assertEqual(self.report["status"], "synthetic-fixture-only")
        self.assertTrue(self.report["scope"]["fixture_only"])
        self.assertFalse(self.report["scope"]["playback_actuator"])
        self.assertFalse(self.report["scope"]["real_speech_or_music"])
        self.assertFalse(self.report["scope"]["listening_or_release_claim"])
        self.assertTrue(self.report["qualification"]["all_required_results_present"])
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_stimuli_are_finite_bounded_and_include_all_cases(self):
        expected = {"silence", "tonal", "speech_like", "unfamiliar_speech",
                    "music_like", "c_vector"}
        self.assertEqual(set(self.report["stimuli"]), expected)
        for name, row in self.report["stimuli"].items():
            self.assertEqual(row["nonfinite_count"], 0, name)
            self.assertEqual(row["clipping_count"], 0, name)
            self.assertLessEqual(row["peak_abs"], 1.0, name)
            self.assertEqual(row["samples"], reference.STIMULUS_LENGTH, name)

    def test_pitch_marks_cover_all_voiced_stimuli(self):
        rows = self.report["pitch_marking"]["rows"]
        self.assertEqual(rows["silence"]["status"], "no_pitch_marks")
        self.assertEqual(rows["silence"]["mark_count"], 0)
        for name in ("tonal", "speech_like", "unfamiliar_speech", "music_like", "c_vector"):
            row = rows[name]
            self.assertEqual(row["status"], "scored", name)
            self.assertGreater(row["mark_count"], 50, name)
            self.assertTrue(row["min_gap_ok"], name)
            self.assertTrue(row["max_gap_ok"], name)
            self.assertGreaterEqual(row["min_period_samples"], reference.MIN_PERIOD, name)
            self.assertLessEqual(row["max_period_samples"], 2 * reference.HALF_WINDOW, name)
        self.assertLess(abs(rows["tonal"]["estimated_f0_hz"] - 220.0), 5.0)
        self.assertLess(abs(rows["music_like"]["estimated_f0_hz"] - 160.0), 5.0)
        self.assertLess(abs(rows["c_vector"]["estimated_f0_hz"] - 166.667), 5.0)

    def test_all_voiced_variants_are_finite_and_bounded(self):
        labels = {"identity_1x_control", "fixed_rate_psola",
                  "dynamic_rate_psola", "varispeed_adverse"}
        for name, rows in self.report["variants"].items():
            if name == "silence":
                self.assertEqual(set(rows), {"unvoiced_fallback"})
                self.assertEqual(rows["unvoiced_fallback"]["status"], "no_pitch_marks")
                self.assertEqual(rows["unvoiced_fallback"]["output_samples"], 0)
                continue
            self.assertEqual(set(rows), labels, name)
            for label, row in rows.items():
                self.assertIn(row["status"], ("control", "candidate", "scored",
                                              "adverse_control"), name + "/" + label)
                self.assertEqual(row["nonfinite_count"], 0, name + "/" + label)
                self.assertEqual(row["clipping_count"], 0, name + "/" + label)
                self.assertLessEqual(row["peak_abs"], 1.0, name + "/" + label)
                self.assertEqual(len(row["digest"]), 64, name + "/" + label)

    def test_identity_control_and_candidate_are_distinct(self):
        for name, rows in self.report["variants"].items():
            if name == "silence":
                continue
            identity = rows["identity_1x_control"]
            self.assertEqual(identity["effective_rate"], 1.0)
            self.assertEqual(identity["digest"], self.report["stimuli"][name]["digest"])
            digests = {rows[label]["digest"] for label in
                       ("identity_1x_control", "fixed_rate_psola", "dynamic_rate_psola")}
            self.assertEqual(len(digests), 3, name)

    def test_fixed_rate_duration_and_rate_are_bounded(self):
        for name, rows in self.report["variants"].items():
            if name == "silence":
                continue
            fixed = rows["fixed_rate_psola"]
            self.assertLess(abs(fixed["duration_error_samples"]),
                            0.02 * fixed["source_samples"], name)
            self.assertGreater(fixed["effective_rate"], 1.20, name)
            self.assertLess(fixed["effective_rate"], 1.30, name)
            self.assertEqual(fixed["uncovered_samples"], 0, name)

    def test_dynamic_candidate_mapping_is_bounded(self):
        for name, rows in self.report["variants"].items():
            if name == "silence":
                continue
            candidate = rows["dynamic_rate_psola"]
            self.assertGreater(candidate["effective_rate"], 1.0, name)
            self.assertLess(candidate["effective_rate"], 1.25, name)
            self.assertLess(candidate["samples"], candidate["source_samples"], name)
            source_map = candidate["source_map"]
            self.assertEqual(source_map["unmapped_samples"], 0, name)
            self.assertLessEqual(source_map["max_source_repeat"], 2 * reference.HALF_WINDOW,
                                 name)
            self.assertLessEqual(source_map["monotonic_violations"], 4, name)

    def test_pitch_is_preserved_and_adverse_controls_are_recorded(self):
        rows = self.report["frequency_scale"]["rows"]
        for label in ("identity_1x_control", "fixed_rate_psola"):
            self.assertTrue(rows[label]["pitch_preserved"], label)
            self.assertTrue(rows[label]["matches_expected_model"], label)
            self.assertLessEqual(rows[label]["absolute_error"], 0.06, label)
        adverse = rows["varispeed_adverse"]
        self.assertFalse(adverse["pitch_preserved"])
        self.assertTrue(adverse["matches_expected_model"])
        self.assertGreater(adverse["frequency_ratio"], 1.15)
        mismatch = rows["mismarked_adverse"]
        self.assertFalse(mismatch["pitch_preserved"])
        self.assertGreater(mismatch["frequency_ratio"], 1.8)
        self.assertLess(mismatch["mean_period_samples"], reference.MIN_PERIOD)

    def test_overlap_add_manipulation_is_explicit(self):
        row = self.report["overlap_add"]
        self.assertEqual(row["status"], "ok")
        self.assertTrue(row["normalized_closer_to_reference"])
        self.assertGreater(row["candidate_denominator_min"], 0.0)
        self.assertEqual(row["candidate_uncovered_samples"], 0)
        adverse = row["excision_adverse"]
        self.assertEqual(adverse["status"], "adverse_control")
        self.assertGreater(adverse["uncovered_samples"], 0)
        self.assertEqual(len(adverse["digest"]), 64)

    def test_rate_boundaries_and_applied_updates_are_recorded(self):
        for name, row in self.report["rate_updates"]["rows"].items():
            self.assertEqual(set(row["boundaries"]), {"4800", "8000", "11200"}, name)
            for boundary, variants in row["boundaries"].items():
                self.assertTrue(all(variant["status"] == "ok"
                                    for variant in variants.values()),
                                name + "/" + boundary)
        applied = self.report["rate_updates"]["applied_updates"]
        self.assertGreaterEqual(len(applied), 3)
        self.assertEqual({update["target_rate"] for update in applied},
                         {1.25, 1.0, 1.5})
        for update in applied:
            self.assertGreaterEqual(update["source_sample"], 0)
            self.assertGreater(update["applied_rate"], reference.RATE_MIN)
            self.assertLessEqual(update["applied_rate"], reference.RATE_MAX)
            self.assertTrue(update["slewed"])

    def test_unsmoothed_rate_step_is_recorded_as_adverse(self):
        adverse_worse = 0
        for row in self.report["rate_updates"]["rows"].values():
            for boundary in row["boundaries"].values():
                candidate = boundary["dynamic_rate_psola"]["ratio_to_clip_p99"]
                adverse = boundary["unsmoothed_psola_adverse"]["ratio_to_clip_p99"]
                if adverse > candidate:
                    adverse_worse += 1
        self.assertGreater(adverse_worse, 0)

    def test_drift_rebuffer_is_scored(self):
        row = self.report["drift_rebuffer"]
        self.assertEqual(row["status"], "ok")
        self.assertGreater(row["expected_output_samples"], 0)
        self.assertLess(abs(row["relative_duration_error"]), 0.02)
        self.assertNotEqual(row["candidate_digest"], row["identity_digest"])
        self.assertLessEqual(row["source_map"]["monotonic_violations"], 4)

    def test_slow_rate_is_whole_clip_fixture_only(self):
        row = self.report["slow_r_whole_clip"]
        self.assertEqual(row["status"], "ok")
        self.assertTrue(row["output_longer_than_input"])
        self.assertGreater(row["effective_rate"], 0.94)
        self.assertLess(row["effective_rate"], 0.96)
        self.assertEqual(row["boundary_status"], "whole_clip_fixture_only")
        self.assertIn("v0 process call cannot emit", row["interpretation"])

    def test_transient_proxy_has_no_listening_claim(self):
        rows = self.report["transient_proxy"]["rows"]
        self.assertEqual(set(rows), {"speech_like", "unfamiliar_speech", "music_like"})
        for row in rows.values():
            self.assertEqual(row["status"], "ok")
            self.assertGreater(row["clip_p99_adjacent_delta"], 0.0)
            self.assertIn("No listening", row["note"])

    def test_streaming_chunking_and_reset_are_deterministic(self):
        streaming = self.report["streaming"]
        chunking = streaming["chunking_equivalence"]
        self.assertEqual(chunking["status"], "expected_lookahead_difference")
        self.assertFalse(chunking["equal"])
        self.assertEqual(len(chunking["whole_digest"]), 64)
        self.assertEqual(len(chunking["chunked_digest"]), 64)
        self.assertTrue(streaming["reset_replay"]["replay_matches"])
        self.assertEqual(streaming["reset_replay"]["replay_first_input_sample"], 50000)
        self.assertTrue(streaming["session_independence"]["independent"])

    def test_invalid_missing_and_nonfinite_cases_fail_closed(self):
        streaming = self.report["streaming"]
        expected_codes = {
            "nonfinite_input": "nonfinite_input",
            "out_of_range": "out_of_range",
            "wrong_shape": "wrong_shape",
            "wrong_position": "wrong_position",
            "stale_epoch": "stale_epoch",
            "process_after_final": "process_after_final",
        }
        self.assertEqual(set(streaming["frame_rejections"]), set(expected_codes))
        for label, row in streaming["frame_rejections"].items():
            self.assertEqual(row["status"], "rejected", label)
            self.assertEqual(row["code"], expected_codes[label], label)
            self.assertTrue(row["state_unchanged"], label)
        for label, row in streaming["config_rejections"].items():
            self.assertEqual(row["status"], "rejected", label)
            self.assertNotEqual(row["code"], "incorrectly_accepted", label)
        self.assertEqual(streaming["drain_before_final"]["code"], "missing_final_input")
        self.assertEqual(streaming["flush_before_final"]["code"], "missing_final_input")

    def test_final_partial_window_is_explicit(self):
        row = self.report["final_partial"]
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["final_input_valid_count"], 137)
        self.assertEqual(row["full_frames"], 77)
        self.assertTrue(row["output_finite"])
        self.assertGreater(row["content_output_samples"], 0)
        self.assertLessEqual(row["output_peak_abs"], 1.0)
        self.assertEqual(len(row["output_digest"]), 64)

    def test_c_expected_vectors_are_pinned(self):
        expected = self.report["c_boundary_expected"]
        self.assertEqual(expected["status"], "expected_from_python_model")
        self.assertEqual(len(expected["content_digest"]), 64)
        self.assertEqual(expected["frames"], 78)
        self.assertEqual(len(expected["valid_counts"]), 78)
        self.assertTrue(any(count == 0 for count in expected["valid_counts"]))
        self.assertLess(expected["valid_counts"][-1], 137)
        self.assertEqual(expected["rejections"], [])
        self.assertEqual(expected["provider_source_digest"],
                         reference.sha256_file(TASK_DIR / "provider" / "psola_praat_provider.c"))
        self.assertEqual(expected["config_digest"],
                         reference.sha256_file(TASK_DIR / "provider" / "config" / "config.json"))

    def test_generated_header_matches_report_and_has_spdx(self):
        text = HEADER_FILE.read_text(encoding="utf-8")
        expected = self.report["c_boundary_expected"]
        self.assertIn('#define EXPECTED_CONTENT_DIGEST "' + expected["content_digest"] + '"', text)
        self.assertIn('#define EXPECTED_CONTENT_SAMPLES ' + str(expected["content_samples"]), text)
        self.assertIn('#define EXPECTED_FRAME_COUNT ' + str(expected["frames"]), text)
        self.assertIn(" * SPDX" + "-License-Identifier: Apache-2.0", text)
        self.assertEqual(text, generator.header_text(expected))

    def test_blockers_and_reopening_are_explicit(self):
        blockers = {row["id"]: row for row in self.report["blockers"]}
        self.assertEqual(set(blockers), {"BLK-01", "BLK-02", "BLK-03", "BLK-04"})
        for row in blockers.values():
            self.assertTrue(row["blocker"])
            self.assertTrue(row["scope"])
            self.assertTrue(row["reopen"])
        self.assertIn("0.95", blockers["BLK-01"]["scope"])

    def test_clean_checkout_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory(prefix="psola-praat-clean-", dir=TEMP_ROOT) as root:
            isolated_task = (Path(root) / "audioml" / "worktrees" / "audio-sdk" /
                             "SDK-PSOLA-PRAAT" / "docs" / "task-evidence" / "psola-praat")
            isolated_worktree = isolated_task.parents[2]
            isolated_audio_root = isolated_worktree.parents[2]
            isolated_task.mkdir(parents=True)
            for name in ("reference.py", "run.py"):
                shutil.copy2(TASK_DIR / name, isolated_task / name)
            (isolated_task / "provider" / "config").mkdir(parents=True)
            for relative in ("provider/psola_praat_provider.c", "provider/config/config.json"):
                target = isolated_task / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(TASK_DIR / relative, target)
            for relative in reference.SOURCE_PINS:
                target = isolated_audio_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(AUDIO_ROOT / relative, target)
            for relative in reference.BOUNDARY_PINS:
                target = isolated_worktree / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(WORKTREE / relative, target)
            environment = {
                "PATH": "/usr/bin:/bin:/usr/local/bin",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            command = [sys.executable, str(isolated_task / "run.py"), "--report",
                       "--install-location", str(TASK_DIR)]
            completed = subprocess.run(command, cwd=isolated_task, env=environment,
                                       capture_output=True, text=True, timeout=600)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual((isolated_task / "report.json").read_bytes(), REPORT_FILE.read_bytes())
            self.assertEqual((isolated_task / "report.json.sha256").read_bytes(),
                             SIDECAR_FILE.read_bytes())

    def test_no_missing_metrics_are_promoted(self):
        self.assertEqual(self.report["qualification"]["candidate_status"],
                         "synthetic-reference-only")
        self.assertEqual(self.report["qualification"]["boundary_status"],
                         "conditional-blocked")
        for name, rows in self.report["variants"].items():
            if name == "silence":
                continue
            for label, row in rows.items():
                if label != "identity_1x_control":
                    self.assertIsInstance(row["effective_rate"], (int, float))
                    self.assertGreater(row["effective_rate"], 0.0)

    def test_sources_and_contract_pins_are_consistent(self):
        lines = (TASK_DIR / "SOURCES.sha256").read_text(encoding="ascii").splitlines()
        pinned = {}
        for line in lines:
            digest, name = line.split(None, 1)
            pinned[name.strip()] = digest
        self.assertNotIn("SOURCES.sha256", pinned)
        actual = {}
        for path in TASK_DIR.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if path.name == "SOURCES.sha256":
                continue
            actual[path.relative_to(TASK_DIR).as_posix()] = reference.sha256_file(path)
        self.assertEqual(set(pinned), set(actual))
        for name, digest in actual.items():
            self.assertEqual(pinned[name], digest, name)

        contract = json.loads((TASK_DIR / "contract.json").read_text(encoding="utf-8"))
        _, canonical = reference.canonical_report(self.report)
        record = contract["canonical_report"]
        self.assertEqual(record["canonical_digest"], canonical)
        self.assertEqual(record["file_sha256"], reference.sha256_file(REPORT_FILE))
        self.assertEqual(record["content_digest"],
                         self.report["c_boundary_expected"]["content_digest"])
        self.assertEqual(contract["source_pins"], self.report["source_pins"])
        self.assertEqual(contract["boundary_pins"], self.report["boundary_pins"])


class AlgorithmTests(unittest.TestCase):
    def test_pitch_marking_is_deterministic(self):
        values = reference.analytic_stimulus("c_vector")[:4096]
        first = reference.pitch_marks(values)
        self.assertEqual(first, reference.pitch_marks(values))
        self.assertEqual(first[:5], (96, 192, 288, 384, 480))
        self.assertEqual(reference.pitch_marks([0.0] * 4096), ())
        tonal = reference.analytic_stimulus("tonal")[:4096]
        self.assertNotEqual(reference.pitch_marks(tonal),
                            reference.pitch_marks(tonal, min_period=8))

    def test_synthesis_normalization_changes_output(self):
        values = reference.analytic_stimulus("tonal")[:4096]
        normalized = reference.synthesize(values, reference.FIXED_SCHEDULE, normalize=True)[0]
        raw = reference.synthesize(values, reference.FIXED_SCHEDULE, normalize=False)[0]
        self.assertNotEqual(reference.tensor_digest(normalized), reference.tensor_digest(raw))

    def test_rate_schedule_validation_rejects_bad_values(self):
        for schedule in (None, (), ((0, 2.0),), ((0, 1.0), (0, 1.25)),
                         ((0, math.nan),)):
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_schedule(schedule)

    def test_config_validation_rejects_bad_values(self):
        for config in (None, {**reference.DEFAULT_CONFIG, "unknown": 1},
                       {**reference.DEFAULT_CONFIG, "provider_id": "wrong"}):
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_config(config)

    def test_reset_to_new_source_origin_is_exact(self):
        values = reference.analytic_stimulus("c_vector")[:4 * reference.FRAME_SAMPLES]
        first = reference.synthesize(values, reference.FIXED_SCHEDULE)[0]
        replay = reference.synthesize(values, reference.FIXED_SCHEDULE)[0]
        stream = reference.PsolaStream(reference.FIXED_SCHEDULE, first_input_sample=9000,
                                       epoch=4)
        for start in range(0, len(values), reference.FRAME_SAMPLES):
            stream.push(values[start:start + reference.FRAME_SAMPLES],
                        reference.FRAME_SAMPLES, 9000 + start, epoch=4)
        self.assertEqual(first, replay)
        self.assertEqual(stream.input_position, 9000 + len(values) // reference.FRAME_SAMPLES *
                         reference.FRAME_SAMPLES)

    def test_varispeed_length_matches_rate(self):
        values = reference.analytic_stimulus("tonal")[:4096]
        output, _ = reference.varispeed_run(values, 1.25)
        self.assertEqual(len(output), reference.round_half_away(len(values) / 1.25))


if __name__ == "__main__":
    unittest.main()
