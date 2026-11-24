# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the task-local granular-TSM fixture.

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
            self.assertTrue((AUDIO_ROOT / relative).is_file(), relative)
            self.assertEqual(row["sha256"], row["actual"], relative)

    def test_boundary_pins_are_verified(self):
        for relative, row in self.report["boundary_pins"].items():
            self.assertTrue(row["verified"], relative)
            self.assertEqual(row["sha256"], row["actual"], relative)

    def test_required_sections_are_present(self):
        for key in ("stimuli", "variants", "parameter_grid", "frequency_scale",
                    "transient_proxy", "rate_updates", "drift_rebuffer",
                    "energy_normalization", "streaming", "final_partial",
                    "c_boundary_expected", "rate_profile_gaps", "blockers"):
            self.assertTrue(self.report[key], key)
        self.assertEqual(self.report["status"], "synthetic-fixture-only")
        self.assertTrue(self.report["scope"]["fixture_only"])
        self.assertFalse(self.report["scope"]["playback_actuator"])
        self.assertFalse(self.report["scope"]["public_surface_changed"])
        self.assertFalse(self.report["scope"]["installed_behavior_changed"])
        self.assertTrue(self.report["qualification"]["all_required_results_present"])
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_stimuli_are_finite_and_bounded(self):
        for name, row in self.report["stimuli"].items():
            self.assertEqual(row["nonfinite_count"], 0, name)
            self.assertEqual(row["clipping_count"], 0, name)
            self.assertLessEqual(row["peak_abs"], 1.0, name)
            self.assertEqual(row["samples"], reference.STIMULUS_LENGTH, name)

    def test_all_variants_are_scored_finite_and_bounded(self):
        labels = {
            "identity_1x_control",
            "fixed_rate_density1_baseline",
            "granular_density2_candidate",
            "granular_density1_control",
            "unsmoothed_rate_step_adverse",
            "varispeed_control",
        }
        for name, rows in self.report["variants"].items():
            self.assertEqual(set(rows), labels, name)
            for label, row in rows.items():
                self.assertIn(row["status"],
                              ("control", "adverse_control", "scored"),
                              name + "/" + label)
                self.assertEqual(row["nonfinite_count"], 0, name + "/" + label)
                self.assertEqual(row["clipping_count"], 0, name + "/" + label)
                self.assertLessEqual(row["peak_abs"], 1.0, name + "/" + label)
                self.assertEqual(len(row["digest"]), 64, name + "/" + label)

    def test_identity_control_is_bit_exact(self):
        stimuli = self.report["stimuli"]
        for name, rows in self.report["variants"].items():
            self.assertEqual(rows["identity_1x_control"]["digest"],
                             stimuli[name]["digest"], name)
            self.assertEqual(rows["identity_1x_control"]["effective_rate"], 1.0)

    def test_fixed_rate_control_is_shorter_than_identity(self):
        for name, rows in self.report["variants"].items():
            if name == "silence":
                continue
            self.assertLess(rows["fixed_rate_density1_baseline"]["samples"],
                            rows["identity_1x_control"]["samples"], name)

    def test_candidate_duration_mapping_is_in_range(self):
        for name, rows in self.report["variants"].items():
            if name == "silence":
                continue
            identity = rows["identity_1x_control"]["samples"]
            candidate = rows["granular_density2_candidate"]["samples"]
            self.assertLess(candidate, identity, name)
            self.assertGreater(candidate, identity // 2, name)
            density1 = rows["granular_density1_control"]["samples"]
            self.assertLess(density1, identity, name)

    def test_source_maps_are_monotonic_and_bounded(self):
        for name, rows in self.report["variants"].items():
            row = rows["granular_density2_candidate"]["source_map"]
            self.assertTrue(row["monotonic"], name)
            self.assertEqual(row["monotonic_violations"], 0, name)
            self.assertLessEqual(row["max_source_repeat"], reference.OVERLAP_SAMPLES,
                                 name)

    def test_candidate_baseline_and_control_are_distinct(self):
        for name, rows in self.report["variants"].items():
            digests = {rows[label]["digest"] for label in
                       ("identity_1x_control", "fixed_rate_density1_baseline",
                        "granular_density2_candidate")}
            self.assertEqual(len(digests), 3, name)

    def test_frequency_scale_is_recorded_and_pitch_preserved(self):
        rows = self.report["frequency_scale"]["rows"]
        for label in ("identity_1x_control", "granular_density2_candidate",
                      "granular_density1_control"):
            self.assertTrue(rows[label]["pitch_preserved"], label)
            self.assertTrue(rows[label]["matches_expected_model"], label)
            self.assertLessEqual(rows[label]["absolute_error"], 0.03, label)
        fixed = rows["fixed_rate_density1_baseline"]
        self.assertEqual(fixed["status"], "scored")
        self.assertLess(fixed["absolute_error"], 0.05)
        self.assertEqual(self.report["frequency_scale"]["analysis"],
                         {"start": 512, "count": 2048})

    def test_varispeed_adverse_control_changes_frequency(self):
        row = self.report["frequency_scale"]["rows"]["varispeed_control"]
        self.assertFalse(row["pitch_preserved"])
        self.assertGreater(row["frequency_ratio"], 1.15)
        self.assertTrue(row["matches_expected_model"])

    def test_transient_proxy_is_explicit_and_not_an_audibility_claim(self):
        rows = self.report["transient_proxy"]["rows"]
        self.assertEqual(set(rows), {"tonal", "speech_like", "music_like"})
        for name, row in rows.items():
            self.assertEqual(row["status"], "scored", name)
            self.assertFalse(row["audibility_measured"], name)
            self.assertTrue(row["proxy_only"], name)
            self.assertGreater(row["source_peak_abs"], 0.0, name)
            for variant in ("candidate", "fixed_rate_density1_baseline",
                            "varispeed_control"):
                self.assertEqual(row[variant]["status"], "ok", name + "/" + variant)
                self.assertGreater(row[variant]["local_peak_abs"], 0.0,
                                   name + "/" + variant)
                self.assertFalse(row[variant]["audibility_measured"])

    def test_parameter_grid_covers_grain_overlap_density(self):
        grid = self.report["parameter_grid"]
        rows = grid["rows"]
        self.assertEqual(len(rows), len(reference.ALLOWED_GRAIN_SAMPLES) *
                         len(reference.ALLOWED_OVERLAP_RATIOS) *
                         len(reference.ALLOWED_DENSITIES))
        for key, row in rows.items():
            self.assertEqual(row["status"], "scored", key)
            self.assertTrue(row["finite"], key)
            self.assertLessEqual(row["peak_abs"], 1.0, key)
            self.assertGreater(row["window_sum_min"], 0.0, key)
            self.assertGreater(row["synth_hop_samples"], 0, key)
            self.assertEqual(row["analysis_hop_samples"] % row["density"], 0, key)
            self.assertTrue(row["source_map"]["monotonic"], key)
            self.assertGreater(row["output_samples"], 0, key)

    def test_parameter_grid_invalid_cases_fail_closed(self):
        invalid = self.report["parameter_grid"]["invalid_cases"]
        self.assertGreaterEqual(len(invalid), 8)
        for label, row in invalid.items():
            self.assertEqual(row["status"], "rejected", label)
            self.assertIsNotNone(row["code"], label)
            self.assertNotEqual(row["code"], "incorrectly_accepted", label)
        self.assertEqual(invalid["missing_density"]["code"], "missing_parameter_set")
        self.assertEqual(invalid["invalid_grain_size"]["code"], "invalid_grain_size")
        self.assertEqual(invalid["invalid_overlap"]["code"], "invalid_overlap")
        self.assertEqual(invalid["nonfinite_rate"]["code"], "nonfinite_rate")

    def test_rate_update_boundaries_are_all_observed(self):
        updates = self.report["rate_updates"]
        self.assertEqual(updates["boundaries"], [3600, 7200, 10000])
        for name, row in updates["rows"].items():
            self.assertEqual(set(row["boundaries"]), {"3600", "7200", "10000"}, name)
            for variants in row["boundaries"].values():
                self.assertTrue(all(variant["status"] == "ok"
                                    for variant in variants.values()),
                                name)
            source_map = row["source_maps"]["granular_density2_candidate"]
            self.assertTrue(source_map["monotonic"], name)
            self.assertLessEqual(source_map["max_source_repeat"],
                                 reference.OVERLAP_SAMPLES, name)

    def test_smooth_rate_envelope_and_adverse_step_are_recorded(self):
        smooth = self.report["rate_updates"]["smoothness"]
        candidate = smooth["granular_density2_candidate"]
        adverse = smooth["unsmoothed_rate_step_adverse"]
        self.assertTrue(candidate["within_configured_slew"])
        self.assertLessEqual(candidate["observed_max_step"],
                             reference.MAX_RATE_STEP + 1e-12)
        self.assertGreater(candidate["rate_updates"], 0)
        self.assertFalse(adverse["slewed"])
        self.assertFalse(adverse["within_configured_slew"])
        self.assertGreater(adverse["observed_max_step"], candidate["observed_max_step"])

        adverse_worse = 0
        for row in self.report["rate_updates"]["rows"].values():
            for variants in row["boundaries"].values():
                candidate_ratio = variants["granular_density2_candidate"][
                    "ratio_to_clip_p99"]
                adverse_ratio = variants["unsmoothed_rate_step_adverse"][
                    "ratio_to_clip_p99"]
                if adverse_ratio > candidate_ratio:
                    adverse_worse += 1
        self.assertGreater(adverse_worse, 0)

    def test_drift_and_rebuffer_case_is_scored(self):
        row = self.report["drift_rebuffer"]
        self.assertEqual(row["status"], "ok")
        self.assertGreater(row["expected_output_samples"], 0)
        self.assertLess(abs(row["relative_duration_error"]), 0.06)
        self.assertLessEqual(row["source_map"]["max_source_repeat"],
                             reference.OVERLAP_SAMPLES)
        self.assertNotEqual(row["candidate_digest"], row["identity_digest"])

    def test_overlap_add_normalization_is_effective(self):
        row = self.report["energy_normalization"]
        self.assertEqual(row["status"], "ok")
        self.assertTrue(row["normalized_closer_to_reference"])
        self.assertGreater(row["normalized_ratio"], 0.0)
        self.assertGreater(row["unnormalized_ratio"], row["normalized_ratio"])

    def test_chunking_and_reset_are_deterministic(self):
        streaming = self.report["streaming"]
        chunking = streaming["chunking_equivalence"]
        self.assertEqual(chunking["status"], "bit_exact_chunking")
        self.assertTrue(chunking["equal"])
        self.assertEqual(len(chunking["whole_digest"]), 64)
        self.assertEqual(len(chunking["chunked_digest"]), 64)
        self.assertTrue(streaming["reset_replay"]["replay_matches"])
        self.assertTrue(streaming["reset_replay"]["source_offset_respected"])
        self.assertTrue(streaming["session_independence"]["independent"])

    def test_frame_and_config_rejections_fail_closed(self):
        for label, row in self.report["streaming"]["frame_rejections"].items():
            self.assertEqual(row["status"], "rejected", label)
            self.assertIsNotNone(row["code"], label)
            self.assertTrue(row["state_unchanged"], label)
        self.assertEqual(
            self.report["streaming"]["frame_rejections"]["nonfinite_input"]["code"],
            "nonfinite_input")
        self.assertEqual(
            self.report["streaming"]["frame_rejections"]["out_of_range"]["code"],
            "out_of_range")
        for label, row in self.report["streaming"]["config_rejections"].items():
            self.assertEqual(row["status"], "rejected", label)
            self.assertNotEqual(row["code"], "incorrectly_accepted", label)

    def test_final_partial_window_is_explicit(self):
        row = self.report["final_partial"]
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["final_input_valid_count"], 137)
        self.assertTrue(row["output_finite"])
        self.assertGreater(row["content_output_samples"], 0)
        self.assertGreater(row["target_final_output_samples"], 0)
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
        self.assertGreater(expected["drain_non_content_samples"], 0)
        self.assertEqual(expected["provider_source_digest"],
                         reference.sha256_file(
                             TASK_DIR / "provider" / "granular_tsm_provider.c"))
        self.assertEqual(expected["config_digest"],
                         reference.sha256_file(
                             TASK_DIR / "provider" / "config" / "config.json"))

    def test_generated_header_matches_report(self):
        text = HEADER_FILE.read_text(encoding="utf-8")
        expected = self.report["c_boundary_expected"]
        self.assertIn('SPDX' '-License-Identifier: Apache-2.0', text)
        self.assertIn('#define GRANULAR_EXPECTED_CONTENT_DIGEST "' +
                      expected["content_digest"] + '"', text)
        self.assertIn('#define GRANULAR_EXPECTED_CONTENT_SAMPLES ' +
                      str(expected["content_samples"]), text)
        self.assertIn('#define GRANULAR_EXPECTED_FRAME_COUNT ' +
                      str(expected["frames"]), text)
        self.assertEqual(generator.header_text(expected), text)

    def test_unmeasured_rate_profile_items_are_blocked_not_promoted(self):
        gaps = self.report["rate_profile_gaps"]
        self.assertEqual(gaps["playback_buffering"]["status"], "not_measured")
        self.assertEqual(gaps["unfamiliar_speech_preservation"]["status"],
                         "not_measured")
        self.assertEqual(gaps["music"]["status"], "synthetic_surrogate_only")
        self.assertEqual(gaps["transient_audibility"]["status"], "proxy_only")
        for label, row in gaps.items():
            self.assertTrue(row["reason"], label)
            self.assertIn(row["blocker"], {"BLK-01", "BLK-02", "BLK-03"}, label)
        self.assertEqual(self.report["qualification"]["candidate_status"],
                         "synthetic-reference-only")
        self.assertEqual(self.report["qualification"]["boundary_status"],
                         "conditional-blocked")
        self.assertEqual(self.report["qualification"]["unmeasured_rate_profile_items"],
                         "recorded_as_blocked")

    def test_blockers_and_reopening_are_explicit(self):
        blockers = {row["id"]: row for row in self.report["blockers"]}
        self.assertEqual(set(blockers),
                         {"BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05"})
        for row in blockers.values():
            self.assertTrue(row["blocker"])
            self.assertTrue(row["scope"])
            self.assertTrue(row["reopen"])
        self.assertIn("0.95", blockers["BLK-01"]["scope"])
        self.assertIn("playback-buffering", blockers["BLK-02"]["scope"])

    def test_clean_checkout_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory(
                prefix="granular-tsm-clean-",
                dir="/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode") as root:
            # Mirror the real relative layout so the pinned source and boundary
            # files resolve exactly as they do in the worktree.
            isolated_task = (Path(root) / "audioml" / "worktrees" / "audio-sdk" /
                             "SDK-GRANULAR-TSM" / "docs" / "task-evidence" /
                             "granular-tsm")
            isolated_worktree = isolated_task.parents[2]
            isolated_audio_root = isolated_worktree.parents[2]
            isolated_task.mkdir(parents=True)
            for name in ("reference.py", "run.py"):
                shutil.copy2(TASK_DIR / name, isolated_task / name)
            (isolated_task / "provider" / "config").mkdir(parents=True)
            shutil.copy2(TASK_DIR / "provider" / "granular_tsm_provider.c",
                         isolated_task / "provider" / "granular_tsm_provider.c")
            shutil.copy2(TASK_DIR / "provider" / "config" / "config.json",
                         isolated_task / "provider" / "config" / "config.json")
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
                                       capture_output=True, text=True, timeout=300)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual((isolated_task / "report.json").read_bytes(),
                             REPORT_FILE.read_bytes())
            self.assertEqual((isolated_task / "report.json.sha256").read_bytes(),
                             SIDECAR_FILE.read_bytes())
            self.assertEqual((isolated_task / "provider" / "expected_vectors.h").read_bytes(),
                             HEADER_FILE.read_bytes())

    def test_report_pins_match_task_declared_evidence(self):
        self.assertIn("cpp-library/pipeline-validation/playback-speed-candidates.md",
                      self.report["source_pins"])
        self.assertIn("audio-benchmark-platform/plan/swarm/VERIFICATION.md",
                      self.report["source_pins"])

    def test_no_missing_metrics_are_promoted(self):
        for name, rows in self.report["variants"].items():
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
        self.assertEqual(contract["qualification"]["python_tests"], 39)


class AlgorithmTests(unittest.TestCase):
    def test_density_changes_output_and_window_overlap(self):
        values = reference.analytic_stimulus("tonal")[:4096]
        dense = reference.run_tsm(values, schedule=reference.FIXED_SCHEDULE,
                                  parameters=reference.DEFAULT_SETTINGS)[0]
        sparse = reference.run_tsm(values, schedule=reference.FIXED_SCHEDULE,
                                   parameters=reference.DENSITY1_SETTINGS)[0]
        self.assertNotEqual(reference.tensor_digest(dense),
                            reference.tensor_digest(sparse))
        self.assertLess(reference.SYNTH_HOP, reference.ANALYSIS_HOP)

    def test_grain_size_and_overlap_change_duration_and_grid(self):
        small = reference.validate_parameters({"grain_samples": 256,
                                               "overlap_samples": 192,
                                               "density": 2})
        large = reference.validate_parameters({"grain_samples": 512,
                                               "overlap_samples": 384,
                                               "density": 2})
        self.assertEqual(small["synth_hop_samples"], 32)
        self.assertEqual(large["synth_hop_samples"], 64)
        values = reference.analytic_stimulus("tonal")[:4096]
        a = reference.run_tsm(values, schedule=reference.FIXED_SCHEDULE,
                              parameters={"grain_samples": 256,
                                          "overlap_samples": 192,
                                          "density": 2})[0]
        b = reference.run_tsm(values, schedule=reference.FIXED_SCHEDULE,
                              parameters={"grain_samples": 512,
                                          "overlap_samples": 384,
                                          "density": 2})[0]
        self.assertEqual(len(a), len(b))
        self.assertNotEqual(reference.tensor_digest(a), reference.tensor_digest(b))

    def test_varispeed_length_matches_rate(self):
        values = reference.analytic_stimulus("tonal")[:4096]
        output, _ = reference.varispeed_run(values, 1.25)
        self.assertEqual(len(output), reference.round_half_away(len(values) / 1.25))

    def test_schedule_and_parameter_validation_reject_bad_values(self):
        for schedule in (None, (), ((0, 2.0),), ((0, 1.0), (0, 1.25))):
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_schedule(schedule)
        for params in (None, {"grain_samples": 512, "overlap_samples": 384},
                       {"grain_samples": 0, "overlap_samples": 0, "density": 2},
                       {"grain_samples": 512, "overlap_samples": 512, "density": 2},
                       {"grain_samples": 512, "overlap_samples": 384, "density": 0}):
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_parameters(params)

    def test_energy_and_finite_helpers_are_deterministic(self):
        values = [0.0, 0.25, -0.5, 0.125]
        self.assertEqual(reference.finite_stats(values)["nonfinite_count"], 0)
        self.assertAlmostEqual(reference.finite_stats(values)["peak_abs"], 0.5)
        self.assertEqual(reference.tensor_digest(values), reference.tensor_digest(values))
        self.assertNotEqual(reference.tensor_digest(values),
                            reference.tensor_digest(values + [0.0]))
        self.assertTrue(math.isfinite(reference.MAX_RATE_STEP))

    def test_reset_to_new_source_origin_is_exact(self):
        values = reference.analytic_stimulus("c_vector")[:2048]
        first = reference.run_tsm(values, schedule=reference.DYNAMIC_SCHEDULE,
                                  first_input_sample=0)
        replay = reference.run_tsm(values, schedule=reference.DYNAMIC_SCHEDULE,
                                   first_input_sample=9000)
        self.assertEqual(first[0], replay[0])
        self.assertEqual(replay[1][0] - first[1][0], 9000)

    def test_nonfinite_and_missing_results_never_score(self):
        values = reference.analytic_stimulus("tonal")[:2048]
        with self.assertRaises(reference.ReferenceRejection):
            reference.run_tsm(values + [math.nan] + values,
                              schedule=reference.FIXED_SCHEDULE)
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_config({**reference.DEFAULT_CONFIG,
                                       "settings": {"density": 2,
                                                    "grain_samples": 512}})
        self.assertFalse(reference.build_report()["qualification"]["missing_result_promoted"])


if __name__ == "__main__":
    unittest.main()
