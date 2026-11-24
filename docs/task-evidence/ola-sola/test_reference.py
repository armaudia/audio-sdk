# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the task-local OLA/SOLA fixture.

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
            self.assertEqual((AUDIO_ROOT / relative).is_file(), True, relative)
            self.assertEqual(row["sha256"], row["actual"], relative)

    def test_boundary_pins_are_verified(self):
        for relative, row in self.report["boundary_pins"].items():
            self.assertTrue(row["verified"], relative)
            self.assertEqual(row["sha256"], row["actual"], relative)

    def test_required_sections_are_present(self):
        for key in ("stimuli", "variants", "frequency_scale", "rate_updates",
                    "drift_rebuffer", "energy_normalization", "streaming",
                    "final_partial", "c_boundary_expected", "blockers"):
            self.assertTrue(self.report[key], key)
        self.assertEqual(self.report["status"], "synthetic-fixture-only")
        self.assertTrue(self.report["scope"]["fixture_only"])
        self.assertFalse(self.report["scope"]["playback_actuator"])
        self.assertTrue(self.report["qualification"]["all_required_results_present"])
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_stimuli_are_finite_and_bounded(self):
        for name, row in self.report["stimuli"].items():
            self.assertEqual(row["nonfinite_count"], 0, name)
            self.assertEqual(row["clipping_count"], 0, name)
            self.assertLessEqual(row["peak_abs"], 1.0, name)
            self.assertEqual(row["samples"], reference.STIMULUS_LENGTH, name)

    def test_all_variants_are_scored_finite_and_bounded(self):
        labels = {"identity_1x_control", "fixed_rate_ola_baseline",
                  "ola_candidate", "sola_candidate", "varispeed_control"}
        for name, rows in self.report["variants"].items():
            self.assertEqual(set(rows), labels, name)
            for label, row in rows.items():
                self.assertEqual(row["status"] in ("control", "adverse_control", "scored"), True,
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

    def test_fixed_rate_baseline_is_shorter_than_identity(self):
        for name, rows in self.report["variants"].items():
            if name == "silence":
                continue
            identity = rows["identity_1x_control"]["samples"]
            baseline = rows["fixed_rate_ola_baseline"]["samples"]
            self.assertLess(baseline, identity, name)

    def test_dynamic_candidate_duration_mapping_is_in_range(self):
        for name, rows in self.report["variants"].items():
            if name == "silence":
                continue
            identity = rows["identity_1x_control"]["samples"]
            candidate = rows["sola_candidate"]["samples"]
            self.assertLess(candidate, identity, name)
            self.assertGreater(candidate, identity // 2, name)

    def test_source_maps_have_bounded_repeats(self):
        for name, rows in self.report["variants"].items():
            row = rows["sola_candidate"]["source_map"]
            self.assertLessEqual(row["max_source_repeat"], reference.OVERLAP, name)
            self.assertLessEqual(row["max_source_step"],
                                 reference.HOP + reference.SEARCH, name)

    def test_candidate_baseline_and_control_are_distinct(self):
        for name, rows in self.report["variants"].items():
            digests = {rows[label]["digest"] for label in
                       ("identity_1x_control", "fixed_rate_ola_baseline", "sola_candidate")}
            self.assertEqual(len(digests), 3, name)

    def test_frequency_scale_is_preserved_by_candidate(self):
        rows = self.report["frequency_scale"]["rows"]
        for label in ("identity_1x_control", "sola_candidate"):
            self.assertTrue(rows[label]["pitch_preserved"], label)
            self.assertTrue(rows[label]["matches_expected_model"], label)
            self.assertLessEqual(rows[label]["absolute_error"], 0.03, label)
        # Fixed-rate OLA has no alignment search and is allowed to show pitch
        # modulation; the measured drift remains part of the baseline record.
        self.assertEqual(rows["fixed_rate_ola_baseline"]["status"], "scored")
        self.assertLess(rows["fixed_rate_ola_baseline"]["absolute_error"], 0.05)

    def test_varispeed_adverse_control_changes_frequency(self):
        row = self.report["frequency_scale"]["rows"]["varispeed_control"]
        self.assertFalse(row["pitch_preserved"])
        self.assertGreater(row["frequency_ratio"], 1.15)
        self.assertTrue(row["matches_expected_model"])

    def test_rate_update_boundaries_are_all_observed(self):
        for name, row in self.report["rate_updates"]["rows"].items():
            self.assertEqual(set(row["boundaries"]), {"4800", "8000", "11200"}, name)
            for boundary, variants in row["boundaries"].items():
                self.assertTrue(all(variant["status"] == "ok"
                                    for variant in variants.values()),
                                name + "/" + boundary)
                source_map = row["source_maps"]["sola_candidate"]
                self.assertLessEqual(source_map["max_source_repeat"],
                                     reference.OVERLAP, name)

    def test_unsmoothed_rate_step_is_recorded_adverse_control(self):
        rows = self.report["rate_updates"]["rows"]
        candidate_worse = 0
        adverse_worse = 0
        for row in rows.values():
            for boundary in row["boundaries"].values():
                candidate = boundary["sola_candidate"]["ratio_to_clip_p99"]
                adverse = boundary["unsmoothed_sola_adverse"]["ratio_to_clip_p99"]
                if candidate > adverse:
                    candidate_worse += 1
                if adverse > candidate:
                    adverse_worse += 1
        self.assertGreater(adverse_worse, 0)

    def test_drift_and_rebuffer_case_is_scored(self):
        row = self.report["drift_rebuffer"]
        self.assertEqual(row["status"], "ok")
        self.assertGreater(row["expected_output_samples"], 0)
        self.assertLess(abs(row["relative_duration_error"]), 0.06)
        self.assertLessEqual(row["source_map"]["max_source_repeat"], reference.OVERLAP)
        self.assertNotEqual(row["candidate_digest"], row["identity_digest"])

    def test_overlap_add_normalization_is_effective(self):
        row = self.report["energy_normalization"]
        self.assertEqual(row["status"], "ok")
        self.assertTrue(row["normalized_closer_to_reference"])
        self.assertGreater(row["window_sum_min"], 0.0)
        self.assertLess(row["window_sum_max"], 2.0)

    def test_chunking_and_reset_are_deterministic(self):
        streaming = self.report["streaming"]
        chunking = streaming["chunking_equivalence"]
        self.assertEqual(chunking["status"], "expected_lookahead_difference")
        self.assertFalse(chunking["equal"])
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
        for label, row in self.report["streaming"]["config_rejections"].items():
            self.assertEqual(row["status"], "rejected", label)
            self.assertNotEqual(row["code"], "incorrectly_accepted", label)

    def test_final_partial_window_is_explicit(self):
        row = self.report["final_partial"]
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["final_input_valid_count"], 137)
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
                         reference.sha256_file(TASK_DIR / "provider" / "ola_sola_provider.c"))
        self.assertEqual(expected["config_digest"],
                         reference.sha256_file(TASK_DIR / "provider" / "config" / "config.json"))

    def test_generated_header_matches_report(self):
        text = HEADER_FILE.read_text(encoding="utf-8")
        expected = self.report["c_boundary_expected"]
        self.assertIn('#define EXPECTED_CONTENT_DIGEST "' + expected["content_digest"] + '"', text)
        self.assertIn('#define EXPECTED_CONTENT_SAMPLES ' + str(expected["content_samples"]), text)
        self.assertIn('#define EXPECTED_FRAME_COUNT ' + str(expected["frames"]), text)

    def test_blockers_and_reopening_are_explicit(self):
        blockers = {row["id"]: row for row in self.report["blockers"]}
        self.assertEqual(set(blockers), {"BLK-01", "BLK-02", "BLK-03", "BLK-04"})
        for row in blockers.values():
            self.assertTrue(row["blocker"])
            self.assertTrue(row["scope"])
            self.assertTrue(row["reopen"])
        self.assertIn("0.95", blockers["BLK-01"]["scope"])

    def test_clean_checkout_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory(
                prefix="ola-sola-clean-",
                dir="/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode") as root:
            # Mirror the real relative layout so the pinned source and boundary
            # files resolve exactly as they do in the worktree.
            isolated_task = (Path(root) / "audioml" / "worktrees" / "audio-sdk" /
                             "SDK-OLA-SOLA" / "docs" / "task-evidence" / "ola-sola")
            isolated_worktree = isolated_task.parents[2]
            isolated_audio_root = isolated_worktree.parents[2]
            isolated_task.mkdir(parents=True)
            for name in ("reference.py", "run.py"):
                shutil.copy2(TASK_DIR / name, isolated_task / name)
            (isolated_task / "provider" / "config").mkdir(parents=True)
            shutil.copy2(TASK_DIR / "provider" / "ola_sola_provider.c",
                         isolated_task / "provider" / "ola_sola_provider.c")
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
            regenerated = (isolated_task / "report.json").read_bytes()
            self.assertEqual(regenerated, REPORT_FILE.read_bytes())
            self.assertEqual((isolated_task / "report.json.sha256").read_bytes(),
                             SIDECAR_FILE.read_bytes())

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
        self.assertEqual(self.report["qualification"]["candidate_status"],
                         "synthetic-reference-only")
        self.assertEqual(self.report["qualification"]["boundary_status"],
                         "conditional-blocked")

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
    def test_ola_and_sola_differ(self):
        values = reference.analytic_stimulus("tonal")[:4096]
        ola = reference.run_tsm(values, algorithm="ola", schedule=reference.DYNAMIC_SCHEDULE)[0]
        sola = reference.run_tsm(values, algorithm="sola", schedule=reference.DYNAMIC_SCHEDULE)[0]
        self.assertNotEqual(reference.tensor_digest(ola), reference.tensor_digest(sola))

    def test_varispeed_length_matches_rate(self):
        values = reference.analytic_stimulus("tonal")[:4096]
        output, _ = reference.varispeed_run(values, 1.25)
        self.assertEqual(len(output), reference.round_half_away(len(values) / 1.25))

    def test_schedule_validation_rejects_bad_values(self):
        for schedule in (None, (), ((0, 2.0),), ((0, 1.0), (0, 1.25))):
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_schedule(schedule)

    def test_energy_and_finite_helpers_are_deterministic(self):
        values = [0.0, 0.25, -0.5, 0.125]
        self.assertEqual(reference.finite_stats(values)["nonfinite_count"], 0)
        self.assertAlmostEqual(reference.finite_stats(values)["peak_abs"], 0.5)
        self.assertEqual(reference.tensor_digest(values), reference.tensor_digest(values))
        self.assertNotEqual(reference.tensor_digest(values),
                            reference.tensor_digest(values + [0.0]))

    def test_reset_to_new_source_origin_is_exact(self):
        values = reference.analytic_stimulus("c_vector")[:2048]
        first = reference.run_tsm(values, algorithm="sola",
                                  schedule=reference.DYNAMIC_SCHEDULE,
                                  first_input_sample=0)
        replay = reference.run_tsm(values, algorithm="sola",
                                   schedule=reference.DYNAMIC_SCHEDULE,
                                   first_input_sample=9000)
        self.assertEqual(first[0], replay[0])
        self.assertEqual(replay[1][0] - first[1][0], 9000)


if __name__ == "__main__":
    unittest.main()
