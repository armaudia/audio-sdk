# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance checks for the advisory-probability fixture.

Run from this directory with:
  PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
No external package, corpus, model, SDK build or network access is needed.
"""

from __future__ import annotations

import json
from pathlib import Path
import struct
import subprocess
import unittest

import reference

TASK_DIR = Path(__file__).resolve().parent
WORKTREE = TASK_DIR.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]
REPORT_FILE = TASK_DIR / "report.json"
SIDECAR_FILE = TASK_DIR / "report.json.sha256"
HEADER_FILE = TASK_DIR / "provider" / "expected_vectors.h"
CONTRACT_FILE = TASK_DIR / "contract.json"
SOURCES_FILE = TASK_DIR / "SOURCES.sha256"
SCHEMA_FILE = TASK_DIR / "report.schema.json"
CONFIG_SCHEMA_FILE = TASK_DIR / "provider" / "config" / "config.schema.json"

EVENT_KEYS = {
    "schema_id", "sequence", "hop", "producer_id", "tap_id", "epoch",
    "source_first_sample", "source_end_sample", "value_milli", "value",
    "validity", "available_monotonic_ns", "clock_id", "config_digest",
}


class AdvisoryEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
        cls.sidecar = SIDECAR_FILE.read_text(encoding="ascii").strip()
        cls.contract = json.loads(CONTRACT_FILE.read_text(encoding="utf-8"))
        cls.config_digest = cls.report["c_boundary_expected"]["config_digest"]

    def test_committed_report_is_canonical_and_digest_matches(self):
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(REPORT_FILE.read_bytes(), (text + "\n").encode("utf-8"))
        self.assertEqual(self.sidecar, digest)
        self.assertEqual(len(digest), 64)

    def test_report_regeneration_is_byte_identical(self):
        text, digest = reference.canonical_report(reference.build_report())
        self.assertEqual((text + "\n").encode("utf-8"), REPORT_FILE.read_bytes())
        self.assertEqual(digest, self.sidecar)

    def test_source_and_boundary_pins_are_verified(self):
        for relative, row in self.report["source_pins"].items():
            self.assertTrue((AUDIO_ROOT / relative).is_file(), relative)
            self.assertTrue(row["verified"], relative)
            self.assertEqual(row["sha256"], row["actual"], relative)
            self.assertEqual(row["sha256"], reference.sha256_hex(
                (AUDIO_ROOT / relative).read_bytes()), relative)
        for relative, row in self.report["boundary_pins"].items():
            self.assertTrue((WORKTREE / relative).is_file(), relative)
            self.assertTrue(row["verified"], relative)
            self.assertEqual(row["sha256"], row["actual"], relative)

    def test_required_sections_and_profile_are_present(self):
        for key in (
            "scope", "provider", "public_boundary", "source_pins",
            "boundary_pins", "stimuli", "conditions", "analysis", "controls",
            "state", "acceptance_profile", "c_boundary_expected",
            "qualification", "historical_source_reported", "release_gates",
            "non_claims",
        ):
            self.assertTrue(self.report[key], key)
        self.assertEqual(self.report["status"], "synthetic-fixture-only")
        self.assertEqual(self.report["profile"], "Analysis")
        self.assertEqual(self.report["base_commit"],
                         "941cabfc39f7e33f01881b6e50e3a1e49e7eb9ce")
        self.assertEqual(self.report["branch"],
                         "swarm/SDK-SPEEX-NS-ADVISORY-PROBABILITY")
        self.assertTrue(self.report["qualification"]["all_required_results_present"])
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_scope_forbids_control_and_release_claims(self):
        scope = self.report["scope"]
        self.assertTrue(scope["fixture_only"])
        self.assertTrue(scope["synthetic_only"])
        for key, value in scope.items():
            if key not in ("fixture_only", "synthetic_only"):
                self.assertFalse(value, key)
        self.assertFalse(scope["advisory_probability_is_control_signal"])
        self.assertFalse(scope["held_out_validation_of_combined_settings"])
        self.assertFalse(scope["tiny16_comparison"])
        self.assertTrue(any("No upstream SpeexDSP" in text
                            for text in self.report["non_claims"]))

    def test_non_gating_wiring(self):
        row = self.report["controls"]["no_gating_wiring"]
        self.assertEqual(row["status"], "pass")
        observed = row["observed"]
        self.assertFalse(observed["advisory_is_control_signal"])
        self.assertFalse(observed["registry_entry_installed"])
        self.assertFalse(observed["default_provider"])
        self.assertEqual(observed["public_surface_id_mentions"], 0)
        self.assertTrue(observed["opt_in_gate_default_off"])
        cmake_text = (TASK_DIR / "provider" / "CMakeLists.txt").read_text(
            encoding="utf-8")
        self.assertIn("option(AS_ENABLE_SPEEX_NS_ADVISORY_PROBABILITY", cmake_text)
        self.assertIn("advisory probability reference\" OFF)", cmake_text)
        self.assertEqual(reference.public_surface_id_mentions(), 0)

    def test_identity_pcm_and_three_byte_identical_repeats(self):
        conditions = self.report["conditions"]
        stimuli = self.report["stimuli"]
        self.assertEqual(set(conditions), set(stimuli))
        for name, row in conditions.items():
            self.assertTrue(row["byte_identical_repeats"], name)
            self.assertEqual(len(row["repeats"]), reference.REPEATS, name)
            self.assertEqual(row["pcm_digest"], stimuli[name]["digest"], name)
            self.assertEqual(row["pcm_bytes"], 64000, name)
            first = row["repeats"][0]
            for repeat in row["repeats"]:
                self.assertEqual(repeat, first, name)
                self.assertEqual(repeat["pcm_digest"], row["pcm_digest"], name)

    def test_stimuli_are_bounded_and_deterministic(self):
        for name in ("primary", "silence", "impulse", "loud_noise_only"):
            row = self.report["stimuli"][name]
            source = (reference.noise_q15(0x4C4F5544, reference.STIMULUS_LENGTH, 8000)
                      if name == "loud_noise_only"
                      else reference.build_stimulus(name))
            self.assertEqual(row["samples"], reference.STIMULUS_LENGTH, name)
            self.assertEqual(row["peak_q15"],
                             max(abs(value) for value in source), name)
            self.assertLessEqual(row["peak_q15"], 20000, name)
            self.assertEqual(len(row["digest"]), 64, name)
        self.assertEqual(reference.build_stimulus("silence"),
                         [0] * reference.STIMULUS_LENGTH)

    def test_event_schema_timestamps_and_intervals(self):
        result = reference.run_reference(reference.build_stimulus("primary"),
                                         config_digest=self.config_digest)
        hop0 = [event for event in result["events"] if event["hop"] == 0]
        hop1 = [event for event in result["events"] if event["hop"] == 1]
        self.assertEqual(len(hop0), 50)
        self.assertEqual(len(hop1), 50)
        for event in result["events"]:
            self.assertEqual(set(event), EVENT_KEYS)
            self.assertEqual(event["schema_id"],
                             "audio-sdk/speex-ns-advisory-analysis/0.1")
            self.assertEqual(event["producer_id"], reference.PROVIDER_ID)
            self.assertEqual(event["validity"], "known")
            self.assertEqual(event["epoch"], 1)
            self.assertEqual(event["config_digest"], self.config_digest)
            self.assertGreater(event["available_monotonic_ns"], 0)
        intervals = [(event["source_first_sample"], event["source_end_sample"])
                     for event in hop0]
        self.assertEqual(intervals,
                         [(index * reference.WINDOW,
                           (index + 1) * reference.WINDOW)
                          for index in range(50)])
        for left, right in zip(hop0, hop1):
            self.assertEqual(left["source_first_sample"], right["source_first_sample"])
            self.assertEqual(left["source_end_sample"], right["source_end_sample"])
            self.assertEqual(left["value_milli"], right["value_milli"])
            self.assertEqual(right["available_monotonic_ns"] -
                             left["available_monotonic_ns"],
                             reference.FRAME * reference.NS_PER_SAMPLE)

    def test_probability_values_are_bounded_milli(self):
        result = reference.run_reference(reference.build_stimulus("primary"),
                                         config_digest=self.config_digest)
        for event in result["events"]:
            self.assertGreaterEqual(event["value_milli"], 0)
            self.assertLessEqual(event["value_milli"], 1000)
            self.assertEqual(event["value"], event["value_milli"] / 1000.0)
        values = [event["value_milli"] for event in result["events"]
                  if event["hop"] == 0]
        self.assertEqual(sum(value > 0 for value in values), 10)

    def test_confusion_and_strata_are_consistent(self):
        analysis = self.report["analysis"]
        counts = analysis["confusion_samples"]
        self.assertEqual(counts["TP"] + counts["FN"], 3200)
        self.assertEqual(counts["FP"] + counts["TN"], 12800)
        self.assertAlmostEqual(analysis["speech_miss_rate"],
                               counts["FN"] / 3200.0)
        self.assertAlmostEqual(analysis["false_alarm_rate"],
                               counts["FP"] / 12800.0)
        for field in ("TP", "FN", "FP", "TN"):
            self.assertEqual(sum(row[field] for row in analysis["strata"].values()),
                             counts[field], field)
        for name, row in analysis["strata"].items():
            self.assertEqual(sum(row["decision_samples"].values()), row["samples"], name)

    def test_onset_offset_and_detection_intervals(self):
        strata = self.report["analysis"]["strata"]
        self.assertEqual(strata["active_speech"]["detected_interval"], [3200, 4800])
        self.assertEqual(strata["active_speech"]["onset_delay_samples"], 0)
        self.assertEqual(strata["active_speech"]["offset_delay_samples"], 0)
        quiet = strata["quiet_speech"]
        self.assertIsNone(quiet["detected_interval"])
        self.assertIsNone(quiet["onset_delay_samples"])
        self.assertEqual(quiet["FN"], 1600)
        noise = strata["loud_idle_noise"]
        self.assertEqual(noise["detected_interval"], [4800, 6400])
        self.assertEqual(noise["FP"], 1600)
        for name in ("quiet_idle_1", "quiet_idle_tail"):
            self.assertIsNone(strata[name]["detected_interval"])
            self.assertEqual(strata[name]["FP"], 0)

    def test_invalid_validity_is_not_nonspeech(self):
        invalid = reference.event_dict(1, 0, 1, 0, reference.WINDOW, 0, "invalid",
                                       reference.ORIGIN_NS +
                                       reference.WINDOW * reference.NS_PER_SAMPLE)
        invalid["config_digest"] = self.config_digest
        labels = reference.decoded_labels([invalid], reference.WINDOW)
        self.assertEqual(set(labels), {"nonspeech"})
        scored = [event for event in [invalid] if event["validity"] == "known"]
        self.assertEqual(scored, [])
        row = self.report["controls"]["invalid_event_not_nonspeech"]
        self.assertEqual(row["status"], "pass")
        self.assertFalse(row["observed"]["in_scoring_denominator"])
        self.assertFalse(row["observed"]["relabelled_nonspeech"])

    def test_dropped_events_record_explicit_gaps(self):
        result = reference.run_reference(reference.build_stimulus("primary"),
                                         config_digest=self.config_digest)
        hop0 = [event for event in result["events"] if event["hop"] == 0]
        dropped = {1, 3}
        kept = [event for event in hop0 if event["sequence"] not in dropped]
        gaps = [[kept[index - 1]["source_end_sample"],
                 kept[index]["source_first_sample"]]
                for index in range(1, len(kept))
                if kept[index]["source_first_sample"] !=
                kept[index - 1]["source_end_sample"]]
        row = self.report["controls"]["dropped_events_explicit"]
        self.assertEqual(row["status"], "pass")
        self.assertEqual(row["observed"]["gaps"], gaps)
        self.assertEqual(row["observed"]["dropped_sequences"], [1, 3])
        self.assertEqual(row["observed"]["fabricated_events"], 0)

    def test_stale_and_post_reset_events_are_filtered(self):
        stale = reference.event_dict(999, 0, 0, 0, reference.WINDOW, 0, "known",
                                     reference.ORIGIN_NS +
                                     reference.WINDOW * reference.NS_PER_SAMPLE)
        stale["config_digest"] = self.config_digest
        result = reference.run_reference(reference.build_stimulus("primary"),
                                         config_digest=self.config_digest)
        self.assertNotIn(stale, result["events"])
        self.assertEqual({event["epoch"] for event in result["events"]}, {1})
        reset = reference.run_reference(reference.build_stimulus("primary"),
                                        epoch=2, config_digest=self.config_digest)
        self.assertEqual({event["epoch"] for event in reset["events"]}, {2})
        for name in ("stale_epoch_rejected", "old_event_after_reset_rejected"):
            self.assertEqual(self.report["controls"][name]["status"], "pass")

    def test_controls_and_state_checks_pass(self):
        self.assertTrue(self.report["all_controls_pass"])
        self.assertTrue(self.report["all_state_pass"])
        for name, row in self.report["controls"].items():
            self.assertEqual(row["status"], "pass", name)
            self.assertTrue(row["expected"], name)
            self.assertTrue(row["observed"], name)
        for name, value in self.report["state"].items():
            self.assertTrue(value, name)

    def test_config_and_provider_source_digests_match_files(self):
        expected = self.report["c_boundary_expected"]
        self.assertEqual(reference.file_digest("provider/config/config.json"),
                         expected["config_digest"])
        self.assertEqual(reference.file_digest("provider/speex_ns_advisory_provider.c"),
                         expected["provider_source_digest"])
        self.assertEqual(self.report["provider"]["config_digest"],
                         expected["config_digest"])
        self.assertEqual(self.report["provider"]["source_digest"],
                         expected["provider_source_digest"])

    def test_generated_header_matches_report(self):
        text = HEADER_FILE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: Apache-2.0", text)
        expected = self.report["c_boundary_expected"]
        for name in ("pcm_digest", "event_hop0_digest", "event_hop1_digest",
                     "event_hop0_binary_digest", "event_hop1_binary_digest",
                     "provider_source_digest", "config_digest"):
            self.assertIn(expected[name], text, name)
        self.assertIn("#define EXPECTED_STIMULUS_LENGTH 16000u", text)
        self.assertIn("#define EXPECTED_EVENT_COUNT 100u", text)
        self.assertIn("#define EXPECTED_REPEATS 3u", text)

    def test_python_test_count_is_pinned(self):
        methods = [name for name in dir(self) if name.startswith("test_")]
        self.assertEqual(len(methods), reference.PYTHON_TESTS)
        self.assertEqual(self.report["qualification"]["python_tests"], 24)
        self.assertEqual(self.contract["qualification"]["python_tests"], 24)

    def test_no_installed_surface_changes_in_git_diff(self):
        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"], cwd=WORKTREE,
            capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(diff, "")
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=WORKTREE,
            capture_output=True, text=True, check=True).stdout.strip()
        prefix = "docs/task-evidence/speex-ns-advisory-probability/"
        for line in status.splitlines():
            path = line[3:].strip().strip('"')
            self.assertTrue(path.startswith(prefix), path)

    def test_contract_and_sources_pins_match_files(self):
        pins = self.contract["artifact_pins"]
        self.assertNotIn("contract.json", pins)
        self.assertNotIn("SOURCES.sha256", pins)
        for relative, digest in pins.items():
            self.assertEqual(reference.file_digest(relative), digest, relative)
        rows = {}
        for line in SOURCES_FILE.read_text(encoding="ascii").splitlines():
            digest, relative = line.split("  ", 1)
            rows[relative] = digest
        self.assertEqual(set(rows), {
            path.relative_to(TASK_DIR).as_posix()
            for path in TASK_DIR.rglob("*")
            if path.is_file() and path.name != "SOURCES.sha256"
            and "__pycache__" not in path.parts
        })
        for relative, digest in rows.items():
            self.assertEqual(reference.file_digest(relative), digest, relative)

    def test_report_schema_structure_is_strict(self):
        schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], self.report["schema_id"])
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(self.report))
        self.assertEqual(set(schema["$defs"]["control"]["required"]),
                         {"expected", "status", "observed"})
        self.assertEqual(schema["$defs"]["qualification"]["properties"][
            "python_tests"]["const"], reference.PYTHON_TESTS)

    def test_provider_config_schema_structure_is_strict(self):
        schema = json.loads(CONFIG_SCHEMA_FILE.read_text(encoding="utf-8"))
        config = json.loads((TASK_DIR / "provider" / "config" /
                             "config.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "audio-sdk/speex-ns-advisory-probability-config/0.1")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(config))
        self.assertEqual(schema["properties"]["provider_id"]["const"],
                         reference.PROVIDER_ID)

    def test_integer_only_parity_has_no_float_tolerance(self):
        samples = reference.build_stimulus("primary")
        self.assertTrue(all(isinstance(value, int) for value in samples))
        self.assertTrue(all(-32768 <= value <= 32767 for value in samples))
        packed = reference.f32_bytes(
            [reference.q15_to_f32(value) for value in samples[:64]])
        self.assertEqual(len(packed), 256)
        for index, value in enumerate(samples[:64]):
            self.assertEqual(struct.unpack("<f", packed[index * 4:index * 4 + 4])[0],
                             reference.q15_to_f32(value))
        result = reference.run_reference(samples, config_digest=self.config_digest)
        hop0 = [event for event in result["events"] if event["hop"] == 0]
        self.assertEqual(reference.event_binary_digest(hop0),
                         self.report["c_boundary_expected"]["event_hop0_binary_digest"])


if __name__ == "__main__":
    unittest.main()
