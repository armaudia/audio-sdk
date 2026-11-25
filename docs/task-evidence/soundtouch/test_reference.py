# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the task-local stretch fixture.

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

import check_licensing
import fixture
import reference
import run as generator
import scorer

TASK_DIR = Path(__file__).resolve().parent
WORKTREE = TASK_DIR.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]
REPORT_FILE = TASK_DIR / "report.json"
SIDECAR_FILE = TASK_DIR / "report.json.sha256"
HEADER_FILE = TASK_DIR / "provider" / "expected_vectors.h"

VARIANT_LABELS = {
    "identity_1x_control",
    "fixed_1_25_reference",
    "slow_0_75_reference",
    "dynamic_rate_candidate",
    "varispeed_adverse_control",
}


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

    def test_report_regeneration_is_byte_identical(self):
        text, digest = reference.canonical_report(generator.build_report())
        self.assertEqual((text + "\n").encode("utf-8"), REPORT_FILE.read_bytes())
        self.assertEqual(digest, self.sidecar)
        for _ in range(3):
            repeated, _ = reference.canonical_report(generator.build_report())
            self.assertEqual((repeated + "\n").encode("utf-8"), REPORT_FILE.read_bytes())

    def test_source_and_boundary_pins_are_verified(self):
        for relative, row in self.report["source_pins"].items():
            self.assertTrue(row["verified"], relative)
            self.assertEqual((AUDIO_ROOT / relative).is_file(), True, relative)
            self.assertEqual(row["sha256"], row["actual"], relative)
        for relative, row in self.report["boundary_pins"].items():
            self.assertTrue(row["verified"], relative)
            self.assertEqual((WORKTREE / relative).is_file(), True, relative)
            self.assertEqual(row["sha256"], row["actual"], relative)

    def test_required_sections_and_profile_are_present(self):
        for key in ("stimuli", "duration_mapping", "variants", "transient_behavior",
                    "steady_state", "rate_updates", "pause_policy", "drift_rebuffer",
                    "streaming", "final_partial", "c_boundary_expected",
                    "acceptance_profile", "blockers", "fixture", "profile_scoring",
                    "remaining_gates", "decision", "installed_v0"):
            self.assertTrue(self.report[key], key)
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["decision"]["status"], "incomplete")
        self.assertEqual(self.report["decision"]["production_exposure"], "DEFER")
        self.assertEqual(self.report["acceptance_profile"]["profile"], "Rate")
        self.assertTrue(self.report["scope"]["fixture_only"])
        self.assertFalse(self.report["scope"]["playback_actuator"])
        self.assertTrue(self.report["qualification"]["all_required_results_present"])
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])
        self.assertTrue(self.report["profile_scoring"]["passed"])

    def test_stimuli_are_finite_and_bounded(self):
        for name, row in self.report["stimuli"].items():
            expected_length = (reference.PAUSE_POLICY_LENGTH if name == "pause_policy"
                               else reference.STIMULUS_LENGTH)
            self.assertEqual(row["nonfinite_count"], 0, name)
            self.assertEqual(row["clipping_count"], 0, name)
            self.assertLessEqual(row["peak_abs"], 1.0, name)
            self.assertEqual(row["samples"], expected_length, name)

    def test_rate_is_clamped_by_validation(self):
        self.assertEqual(self.report["contract"]["rate_min"], 0.75)
        self.assertEqual(self.report["contract"]["rate_max"], 1.5)
        self.assertEqual(self.report["acceptance_profile"]["clamp"], [0.75, 1.5])
        for name, rows in self.report["duration_mapping"].items():
            for rate, row in rows.items():
                self.assertGreaterEqual(float(rate), 0.75, name + "/" + rate)
                self.assertLessEqual(float(rate), 1.5, name + "/" + rate)

    def test_all_variants_are_scored_finite_and_bounded(self):
        for name, rows in self.report["variants"].items():
            self.assertEqual(set(rows), VARIANT_LABELS, name)
            for label, row in rows.items():
                self.assertIn(row["status"], ("control", "adverse_control", "scored"))
                self.assertEqual(row["nonfinite_count"], 0, name + "/" + label)
                self.assertEqual(row["clipping_count"], 0, name + "/" + label)
                self.assertLessEqual(row["peak_abs"], 1.0, name + "/" + label)
                self.assertEqual(len(row["digest"]), 64, name + "/" + label)

    def test_identity_control_is_bit_exact(self):
        stimuli = self.report["stimuli"]
        for name, rows in self.report["variants"].items():
            row = rows["identity_1x_control"]
            self.assertEqual(row["digest"], stimuli[name]["digest"], name)
            self.assertEqual(row["effective_rate"], 1.0)
            self.assertEqual(row["duration_error_samples"], 0)

    def test_rate_direction_and_duration_mapping(self):
        for name, rows in self.report["variants"].items():
            if name == "silence":
                continue
            identity = rows["identity_1x_control"]["samples"]
            fast = rows["fixed_1_25_reference"]["samples"]
            slow = rows["slow_0_75_reference"]["samples"]
            dynamic = rows["dynamic_rate_candidate"]["samples"]
            self.assertLess(fast, identity, name)
            self.assertGreater(slow, identity, name)
            self.assertLess(dynamic, identity, name)
            self.assertGreater(dynamic, fast, name)
        for name, rows in self.report["duration_mapping"].items():
            for rate, row in rows.items():
                self.assertEqual(row["duration_error_samples"], 0,
                                 name + "/" + rate)
                self.assertEqual(row["observed_output_samples"],
                                 row["expected_output_samples"])
                self.assertEqual(row["nonfinite_count"], 0)
                self.assertEqual(row["clipping_count"], 0)
                # Output length is rounded to whole samples by the caller clock.
                self.assertAlmostEqual(row["effective_rate"], float(rate),
                                       delta=1e-4, msg=name + "/" + rate)

    def test_source_maps_are_block_monotonic_with_bounded_overlap(self):
        for name, rows in self.report["variants"].items():
            for label, row in rows.items():
                source_map = row["source_map"]
                self.assertTrue(source_map["monotonic"], name + "/" + label)
                self.assertTrue(source_map["segment_starts_monotonic"])
                self.assertEqual(source_map["monotonic_violations"], 0)
                self.assertLessEqual(source_map["max_source_repeat"],
                                     reference.OVERLAP, name + "/" + label)
                self.assertLessEqual(source_map["max_source_step"],
                                     reference.HOP + reference.SEARCH,
                                     name + "/" + label)

    def test_candidate_baseline_and_controls_are_distinct(self):
        for name, rows in self.report["variants"].items():
            digests = {rows[label]["digest"] for label in VARIANT_LABELS}
            expected = 4 if name == "silence" else 5
            self.assertGreaterEqual(len(digests), expected, name)

    def test_frequency_scale_is_preserved_by_reference(self):
        rows = self.report["steady_state"]["frequency_scale"]["rows"]
        for label in ("identity_1x_control", "fixed_1_25_reference",
                      "dynamic_rate_candidate"):
            self.assertTrue(rows[label]["pitch_preserved"], label)
            self.assertTrue(rows[label]["matches_expected_model"], label)
            self.assertLessEqual(rows[label]["absolute_error"], 0.03, label)

    def test_varispeed_adverse_control_changes_frequency(self):
        row = self.report["steady_state"]["frequency_scale"][
            "rows"]["varispeed_adverse_control"]
        self.assertFalse(row["pitch_preserved"])
        self.assertGreater(row["frequency_ratio"], 1.15)
        self.assertTrue(row["matches_expected_model"])

    def test_energy_normalization_is_effective(self):
        row = self.report["steady_state"]["energy_normalization"]
        self.assertEqual(row["status"], "ok")
        self.assertTrue(row["normalized_closer_to_reference"])
        self.assertGreater(row["window_sum_min"], 0.0)
        self.assertGreater(row["unnormalized_ratio"], row["normalized_ratio"])

    def test_transient_events_are_scored_and_preserved(self):
        rows = self.report["transient_behavior"]["transients"]
        self.assertEqual(set(rows), {"tonal", "speech_like", "music_like"})
        for name, row in rows.items():
            self.assertEqual(row["status"], "ok", name)
            self.assertTrue(row["transient_events"], name)
            self.assertIn("proxy", row["note"].lower())
            for event in row["transient_events"]:
                self.assertEqual(event["status"], "scored", name)
                self.assertGreater(event["output_peak_amplitude"], 0.0)
                self.assertGreater(event["amplitude_retention"], 0.0)
                self.assertLessEqual(event["source_timing_error_samples"],
                                     reference.SEGMENT, name)

    def test_rate_change_boundaries_and_unsmoothed_control(self):
        boundaries = self.report["transient_behavior"]["rate_change_boundaries"]
        self.assertEqual(set(boundaries), {"4800", "8000", "11200"})
        for row in boundaries.values():
            for variant in row.values():
                self.assertEqual(variant["status"], "ok")
        smoothed = self.report["rate_updates"]["rows"]
        adverse_worse = 0
        for row in smoothed.values():
            self.assertEqual(set(row["boundaries"]), {"4800", "8000", "11200"})
            for boundary in row["boundaries"].values():
                candidate = boundary["dynamic_rate_candidate"]["ratio_to_clip_p99"]
                adverse = boundary["unsmoothed_adverse"]["ratio_to_clip_p99"]
                if adverse > candidate:
                    adverse_worse += 1
        self.assertGreater(adverse_worse, 0)

    def test_source_anchored_pause_policy_has_duration_identity(self):
        row = self.report["pause_policy"]
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["input_samples"], reference.PAUSE_POLICY_LENGTH)
        self.assertEqual(row["voiced_source_samples"], 9600)
        self.assertEqual(row["pause_source_samples"], 3200)
        self.assertEqual(row["duration_error_samples"], 0)
        self.assertEqual(row["observed_output_samples"],
                         row["expected_output_samples"])
        self.assertEqual(row["nonfinite_count"], 0)
        self.assertEqual(row["clipping_count"], 0)
        self.assertTrue(row["source_map"]["segment_starts_monotonic"])
        self.assertEqual(len(row["boundaries"]), 7)
        self.assertTrue(all(boundary["transition"]["status"] == "ok"
                            for boundary in row["boundaries"]))
        self.assertGreaterEqual(len(row["rate_updates"]), len(row["boundaries"]))
        targets = {update["target_rate"] for update in row["rate_updates"]}
        self.assertEqual(targets, {rate for _, rate in row["schedule"]})
        for start, rate in row["schedule"]:
            self.assertGreaterEqual(rate, 0.75)
            self.assertLessEqual(rate, 1.5)

    def test_drift_and_rebuffer_are_scored_with_exact_duration(self):
        for name, row in self.report["drift_rebuffer"].items():
            self.assertEqual(row["status"], "scored", name)
            self.assertEqual(row["duration_error_samples"], 0, name)
            self.assertEqual(row["observed_output_samples"],
                             row["expected_output_samples"])
            self.assertNotEqual(row["candidate_digest"], row["identity_digest"])
            self.assertTrue(row["source_map"]["segment_starts_monotonic"])

    def test_streaming_chunking_and_reset_are_deterministic(self):
        streaming = self.report["streaming"]
        chunking = streaming["chunking_equivalence"]
        self.assertEqual(chunking["status"], "expected_lookahead_difference")
        self.assertFalse(chunking["equal"])
        self.assertEqual(len(chunking["whole_digest"]), 64)
        self.assertEqual(len(chunking["chunked_digest"]), 64)
        self.assertEqual(chunking["chunked_observed_output_samples"],
                         chunking["chunked_target_output_samples"])
        self.assertEqual(chunking["chunked_underrun_samples"], 0)
        replay = streaming["reset_replay"]
        self.assertTrue(replay["replay_matches"])
        self.assertTrue(replay["source_offset_respected"])
        self.assertTrue(streaming["session_independence"]["independent"])

    def test_frame_and_config_rejections_fail_closed(self):
        for label, row in self.report["streaming"]["frame_rejections"].items():
            self.assertEqual(row["status"], "rejected", label)
            self.assertIsNotNone(row["code"], label)
            self.assertTrue(row["state_unchanged"], label)
        for label, row in self.report["streaming"]["config_rejections"].items():
            self.assertEqual(row["status"], "rejected", label)
            self.assertIsNotNone(row["code"], label)
        self.assertEqual(set(self.report["streaming"]["frame_rejections"]), {
            "nonfinite_input", "out_of_range_input", "wrong_shape",
            "wrong_position", "wrong_epoch", "process_after_final",
            "drain_before_final",
        })
        self.assertEqual(set(self.report["streaming"]["config_rejections"]), {
            "missing_rate_selection", "invalid_config",
            "rate_out_of_range", "nonfinite_rate",
        })

    def test_final_partial_window_is_explicit(self):
        row = self.report["final_partial"]
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["final_input_valid_count"], 137)
        self.assertEqual(row["content_output_samples"],
                         row["target_output_samples"])
        self.assertGreater(row["drain_non_content_samples"], 0)
        self.assertTrue(row["output_finite"])
        self.assertLessEqual(row["output_peak_abs"], 1.0)
        self.assertEqual(row["output_clipping_count"], 0)
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
        self.assertEqual(expected["offsets"], [0] * 78)
        self.assertEqual(expected["flags"], [0] * 78)
        self.assertEqual(expected["provider_source_digest"],
                         reference.sha256_file(
                             TASK_DIR / "provider" / "soundtouch_reference_provider.c"))
        self.assertEqual(expected["config_digest"],
                         reference.sha256_file(
                             TASK_DIR / "provider" / "config" / "config.json"))

    def test_generated_header_matches_report_and_has_valid_spdx(self):
        text = HEADER_FILE.read_text(encoding="utf-8")
        expected = self.report["c_boundary_expected"]
        self.assertIn('#define EXPECTED_CONTENT_DIGEST "'
                      + expected["content_digest"] + '"', text)
        self.assertIn('#define EXPECTED_CONTENT_SAMPLES '
                      + str(expected["content_samples"]), text)
        self.assertIn('#define EXPECTED_FRAME_COUNT '
                      + str(expected["frames"]), text)
        self.assertIn(" * SPDX" + "-License-Identifier: Apache-2.0", text)
        self.assertNotIn(".replace(", text)

    def test_blockers_and_reopening_are_explicit(self):
        blockers = {row["id"]: row for row in self.report["blockers"]}
        self.assertEqual(set(blockers),
                         {"BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05", "BLK-06"})
        for row in blockers.values():
            self.assertTrue(row["blocker"])
            self.assertTrue(row["scope"])
            self.assertTrue(row["reopen"])
        self.assertIn("160", blockers["BLK-01"]["blocker"])
        self.assertIn("unregistered", blockers["BLK-05"]["blocker"].lower())

    def test_sources_and_contract_pins_are_consistent(self):
        lines = (TASK_DIR / "SOURCES.sha256").read_text(encoding="ascii").splitlines()
        pinned = {}
        for line in lines:
            if line.startswith("PIN  "):
                continue
            digest, name = line.split("  ", 1)
            pinned[name] = digest
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
        contract_pins = {row["id"]: row["sha256"] for row in contract["pins"]}
        expected_pins = {**reference.SOURCE_PINS, **reference.BOUNDARY_PINS}
        expected_pins = {("audio-sdk/" + key if key in reference.BOUNDARY_PINS else key): sha
                         for key, sha in expected_pins.items()}
        self.assertEqual(expected_pins, {k: v for k, v in contract_pins.items()
                                         if k in expected_pins})
        for relative, sha in reference.SOURCE_PINS.items():
            self.assertEqual(contract_pins[relative], sha)
        for relative, sha in reference.BOUNDARY_PINS.items():
            self.assertEqual(contract_pins["audio-sdk/" + relative], sha)
        self.assertEqual(contract["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(contract["status"], "proposal_only_not_qualified")
        self.assertEqual(contract["decision"]["production_exposure"], "DEFER")
        self.assertFalse(contract["exact_scope"]["installed_v0_changed"])

    def test_clean_checkout_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory(
                prefix="soundtouch-clean-",
                dir="/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode") as root:
            isolated_task = (Path(root) / "audioml" / "worktrees" / "audio-sdk" /
                             "SDK-SOUNDTOUCH" / "docs" /
                             "task-evidence" / "soundtouch")
            isolated_worktree = isolated_task.parents[2]
            isolated_audio_root = isolated_worktree.parents[2]
            isolated_task.mkdir(parents=True)
            for name in ("reference.py", "run.py", "fixture.py", "scorer.py"):
                shutil.copy2(TASK_DIR / name, isolated_task / name)
            (isolated_task / "provider" / "config").mkdir(parents=True)
            for name in ("soundtouch_reference_provider.c", "expected_vectors.h"):
                shutil.copy2(TASK_DIR / "provider" / name,
                             isolated_task / "provider" / name)
            for name in ("config.json", "descriptor.h.in"):
                shutil.copy2(TASK_DIR / "provider" / "config" / name,
                             isolated_task / "provider" / "config" / name)
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


class AlgorithmTests(unittest.TestCase):
    def test_schedule_validation_rejects_bad_values(self):
        for schedule in (None, (), ((0, 2.0),), ((0, 0.5),),
                         ((0, 1.0), (0, 1.25)), ((0, math.nan),),
                         ((0, 1.0), (100, 1.25), (50, 1.5))):
            with self.assertRaises(reference.ReferenceRejection):
                reference.validate_schedule(schedule)

    def test_config_validation_rejects_unknown_keys_and_ids(self):
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_config({**reference.DEFAULT_CONFIG, "extra": 1})
        with self.assertRaises(reference.ReferenceRejection):
            reference.validate_config({**reference.DEFAULT_CONFIG,
                                       "provider_id": "rate.other.v0"})

    def test_varispeed_length_matches_rate(self):
        values = reference.analytic_stimulus("tonal")[:4096]
        output, sources = reference.varispeed_run(values, 1.25)
        self.assertEqual(len(output), reference.llround(len(values) / 1.25))
        self.assertEqual(len(sources), len(output))
        self.assertTrue(reference.source_map_stats(sources)["monotonic"])

    def test_whole_clip_and_streaming_are_deterministic(self):
        values = reference.analytic_stimulus("c_vector")[:2048]
        first = reference.run_tsm(values, chunk_size=0)
        replay = reference.run_tsm(values, chunk_size=0,
                                   first_input_sample=9000)
        self.assertEqual(first[0], replay[0])
        self.assertEqual([source - 9000 for source in replay[1]], first[1])
        self.assertEqual(first[2].segments, replay[2].segments)

    def test_llround_matches_half_away_from_zero(self):
        self.assertEqual(reference.llround(1.5), 2)
        self.assertEqual(reference.llround(-1.5), -2)
        self.assertEqual(reference.llround(1.4), 1)
        self.assertEqual(reference.llround(-1.4), -1)

    def test_finite_and_tensor_helpers_are_deterministic(self):
        values = [0.0, 0.25, -0.5, 0.125]
        self.assertEqual(reference.finite_stats(values)["nonfinite_count"], 0)
        self.assertAlmostEqual(reference.finite_stats(values)["peak_abs"], 0.5)
        self.assertEqual(reference.tensor_digest(values),
                         reference.tensor_digest(values))
        self.assertNotEqual(reference.tensor_digest(values),
                            reference.tensor_digest(values + [0.0]))


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
        cls.catalog = fixture.catalog()
        cls.crosscheck = json.loads((TASK_DIR / "crosscheck.json").read_text(encoding="utf-8"))

    def test_fixture_catalog_is_pinned_and_exhaustive(self):
        self.assertEqual(self.report["fixture"], self.catalog)
        self.assertEqual(self.catalog["stimulus_names"], list(fixture.STIMULI))
        self.assertEqual(self.catalog["c_vector_length"], reference.STIMULUS_LENGTH)
        self.assertEqual(len(self.catalog["profile_dimensions"]), 10)
        self.assertFalse(self.catalog["real_assets"])
        self.assertFalse(self.catalog["missing_result_promoted"])

    def test_all_invalid_missing_and_adverse_cases_are_declared(self):
        case_ids = {row["case_id"] for row in self.catalog["cases"]}
        for expected in ("nonfinite_input", "out_of_range_input", "wrong_shape",
                         "wrong_position", "wrong_epoch", "process_after_final",
                         "drain_before_final", "missing_rate_selection",
                         "invalid_config", "rate_out_of_range", "nonfinite_rate",
                         "varispeed_adverse_control", "unsmoothed_rate_step",
                         "silence", "identity_1x_control"):
            self.assertIn(expected, case_ids)
        categories = {row["case_id"]: row["category"] for row in self.catalog["cases"]}
        self.assertEqual(categories["nonfinite_input"], "invalid")
        self.assertEqual(categories["drain_before_final"], "missing")
        self.assertEqual(categories["varispeed_adverse_control"], "adverse")

    def test_scorer_rejects_missing_or_invalid_results(self):
        valid = scorer.score_profile(self.report, self.catalog)
        self.assertTrue(valid["passed"])
        self.assertEqual(valid["status"],
                         "all-required-synthetic-results-present-not-qualified")
        incomplete = json.loads(json.dumps(self.report))
        incomplete["steady_state"]["frequency_scale"]["rows"] = {}
        failed = scorer.score_profile(incomplete, self.catalog)
        self.assertFalse(failed["passed"])
        self.assertIn("pitch", failed["failed_checks"])
        adverse = scorer.score_validity({"samples": 10, "nonfinite_count": 1,
                                         "clipping_count": 0, "peak_abs": 0.5})
        self.assertEqual(adverse["status"], "invalid")
        duration = scorer.score_duration({"expected_output_samples": 10,
                                          "observed_output_samples": 9,
                                          "duration_error_samples": -1,
                                          "nonfinite_count": 0, "clipping_count": 0})
        self.assertEqual(duration["status"], "missing_or_invalid")

    def test_crosscheck_is_canonical_and_consumer_results_are_recorded(self):
        consumer = json.loads((TASK_DIR / "provider" / "consumer_result.json").read_text(
            encoding="utf-8"))
        text, digest = reference.canonical_report(self.crosscheck)
        self.assertEqual((TASK_DIR / "crosscheck.json").read_bytes(),
                         (text + "\n").encode("utf-8"))
        self.assertEqual((TASK_DIR / "crosscheck.json.sha256").read_text(
            encoding="ascii").strip(), digest)
        self.assertEqual(self.crosscheck["consumer_result_sha256"],
                         reference.sha256_file(TASK_DIR / "provider" / "consumer_result.json"))
        self.assertEqual((consumer["sdk_ctest"], consumer["consumer_off"],
                          consumer["consumer_on"]), ("11/11", "1/1", "1/1"))
        expected = self.report["c_boundary_expected"]
        self.assertEqual(self.crosscheck["expected_content_digest"],
                         expected["content_digest"])
        self.assertEqual(self.crosscheck["expected_final_valid_count"],
                         expected["valid_counts"][-1])
        self.assertEqual(self.crosscheck["decision"]["production_exposure"], "DEFER")

    def test_scope_declarations_are_consistent_across_manifests(self):
        contract = json.loads((TASK_DIR / "contract.json").read_text(encoding="utf-8"))
        adapter = json.loads((TASK_DIR / "adapter.json").read_text(encoding="utf-8"))
        provider = json.loads((TASK_DIR / "provider.json").read_text(encoding="utf-8"))
        for manifest in (contract, adapter, provider):
            self.assertEqual(manifest["spdx"]["SPDX-License-Identifier"], "Apache-2.0")
        self.assertEqual(contract["status"], "proposal_only_not_qualified")
        self.assertEqual(contract["decision"]["status"], "incomplete")
        self.assertEqual(contract["decision"]["production_exposure"], "DEFER")
        self.assertFalse(provider["provider_added"])
        self.assertFalse(provider["descriptor_added_to_sdk"])
        self.assertFalse(adapter["registration"]["default_enabled"])
        self.assertEqual(adapter["c_boundary"]["default"], "OFF")
        cmake = (TASK_DIR / "provider" / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("AS_ENABLE_SOUNDTOUCH_REFERENCE", cmake)
        self.assertIn(" OFF)", cmake)

    def test_licensing_check_is_clean(self):
        result = check_licensing.check()
        self.assertEqual(result["status"], "ok", result["problems"])
        self.assertGreaterEqual(result["explicit_spdx_files"], 13)

    def test_verify_script_is_green(self):
        environment = {"PATH": "/usr/bin:/bin:/usr/local/bin",
                       "PYTHONDONTWRITEBYTECODE": "1"}
        completed = subprocess.run([sys.executable, "verify.py"], cwd=TASK_DIR,
                                   env=environment, capture_output=True, text=True,
                                   timeout=300)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(completed.stdout.startswith("PASS "))

    def test_sources_manifest_is_byte_repeatable(self):
        manifest = (TASK_DIR / "SOURCES.sha256").read_text(encoding="ascii")
        for _ in range(3):
            self.assertEqual(generator.sources_text(), manifest)


if __name__ == "__main__":
    unittest.main()
