# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local deterministic tests for the synthetic rate-change reference."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

import fixture
import reference
import run as cli
import scorer

TASK_DIR = Path(__file__).resolve().parent


class PinTest(unittest.TestCase):
    def test_source_pins_exact(self) -> None:
        self.assertEqual(fixture.verify_source_pins(), fixture.SOURCE_PINS)

    def test_mutable_board_is_provenance_only(self) -> None:
        path = fixture.resolve_pin_path(fixture.MUTABLE_BOARD)
        self.assertTrue(path.is_file())
        provenance = reference.build_report()["mutable_provenance"]
        self.assertEqual(provenance["path"], fixture.MUTABLE_BOARD)
        self.assertEqual(provenance["sha256_at_read"], fixture.MUTABLE_BOARD_SHA256_AT_READ)
        self.assertFalse(provenance["gate"])
        result = subprocess.run([sys.executable, "run.py", "--sources"], cwd=TASK_DIR,
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        sources = json.loads(result.stdout)
        self.assertFalse(sources["mutable_provenance"]["gate"])
        self.assertNotIn("sha256_now", sources["mutable_provenance"])

    def test_boundary_pins_in_contract(self) -> None:
        contract = json.loads((TASK_DIR / "contract.json").read_text(encoding="utf-8"))
        for key in fixture.SOURCE_PINS:
            self.assertEqual(contract["source_pins"][key], fixture.SOURCE_PINS[key])


class FixtureTest(unittest.TestCase):
    def test_eight_scenarios(self) -> None:
        self.assertEqual(len(fixture.SCENARIOS), 8)

    def test_segments_cover_source(self) -> None:
        for scenario in fixture.SCENARIOS:
            previous = 0
            for segment in scenario["segments"]:
                self.assertEqual(segment["start"], previous)
                self.assertGreater(segment["end"], segment["start"])
                previous = segment["end"]
            self.assertEqual(previous, scenario["length"])

    def test_chunk_schedules_cover(self) -> None:
        for scenario in fixture.SCENARIOS:
            for schedule in fixture.CHUNK_SCHEDULE_NAMES:
                sizes = fixture.chunk_sizes(scenario, schedule)
                self.assertEqual(sum(sizes), scenario["length"])
                self.assertTrue(all(size > 0 for size in sizes))

    def test_deterministic_samples_digest(self) -> None:
        first = fixture.samples_digest(fixture.scenario_by_name("identity_1x_speech")["samples"])
        second = fixture.samples_digest(fixture.scenario_by_name("identity_1x_speech")["samples"])
        self.assertEqual(first, second)


class ReferenceTest(unittest.TestCase):
    def test_target_length_identity(self) -> None:
        scenario = fixture.scenario_by_name("identity_1x_speech")
        self.assertEqual(reference.target_output_length(((0, 1, 1),), scenario["length"]),
                         scenario["length"])

    def test_rate_at_schedule(self) -> None:
        schedule = reference.validate_schedule([[0, 1, 1], [3200, 5, 4], [4800, 4, 5]])
        self.assertEqual(reference.rate_at(schedule, 0), (1, 1))
        self.assertEqual(reference.rate_at(schedule, 3199), (1, 1))
        self.assertEqual(reference.rate_at(schedule, 3200), (5, 4))
        self.assertEqual(reference.rate_at(schedule, 4800), (4, 5))

    def test_output_position_exact(self) -> None:
        schedule = reference.validate_schedule([[0, 1, 1], [3200, 5, 4]])
        self.assertEqual(reference.output_position_at(schedule, 3200), 3200)
        self.assertEqual(reference.output_position_at(schedule, 3205), 3204)
        self.assertEqual(reference.round_fraction(reference.output_position_at(schedule, 6400)), 5760)

    def test_chunk_identity_all_scenarios(self) -> None:
        for scenario in fixture.SCENARIOS:
            digests = [reference.run_scenario(scenario, schedule)["sample_digest"]
                       for schedule in fixture.CHUNK_SCHEDULE_NAMES]
            self.assertEqual(len(set(digests)), 1, scenario["name"])

    def test_metadata_identity_all_scenarios(self) -> None:
        for scenario in fixture.SCENARIOS:
            digests = [reference.run_scenario(scenario, schedule)["metadata_digest"]
                       for schedule in fixture.CHUNK_SCHEDULE_NAMES]
            self.assertEqual(len(set(digests)), 1, scenario["name"])

    def test_reset_replay_matches_baseline(self) -> None:
        cross = reference.crosscheck_payload()
        self.assertTrue(cross["reset_replay"]["matches_baseline"])
        self.assertTrue(cross["reset_replay"]["stale_epoch_rejected"])

    def test_invalid_controls(self) -> None:
        controls = reference.invalid_controls()
        self.assertGreaterEqual(len(controls), 12)
        self.assertTrue(all(item["rejected"] for item in controls))

    def test_rejects_gap_overlap_epoch(self) -> None:
        session = reference.RateChange([[0, 1, 1]])
        self.assertEqual(session.feed([1, 2, 3], 10), [])
        self.assertEqual(session.rejected[-1]["reason"], "source_gap_or_overlap")
        session.feed([1, 2, 3], 0)
        self.assertEqual(session.feed([4, 5], 1), [])
        self.assertEqual(session.rejected[-1]["reason"], "source_gap_or_overlap")
        self.assertEqual(session.feed([4, 5], 3, epoch=9), [])
        self.assertEqual(session.rejected[-1]["reason"], "stale_or_wrong_epoch")

    def test_no_mutation_after_rejection(self) -> None:
        scenario = fixture.scenario_by_name("identity_1x_speech")
        session = reference.RateChange(scenario["rate_schedule"])
        session.feed(list(scenario["samples"][:320]), 0)
        before = session.output_samples()
        session.feed([0], 9999)
        session.feed([0.5], 320)  # type: ignore[list-item]
        self.assertEqual(session.output_samples(), before)

    def test_drain_idempotent(self) -> None:
        scenario = fixture.scenario_by_name("drift_partial_tail")
        session = reference.RateChange(scenario["rate_schedule"])
        session.feed(list(scenario["samples"]), 0)
        first = session.drain()
        second = session.drain()
        self.assertTrue(first)
        self.assertEqual(second, [])

    def test_1x_exact_speech(self) -> None:
        scenario = fixture.scenario_by_name("identity_1x_speech")
        result = reference.run_scenario(scenario, "sdk_frames")
        for segment in scenario["segments"]:
            if segment["kind"].startswith("speech"):
                start, end = segment["start"], segment["end"]
                self.assertEqual(list(result["samples"][start:end]),
                                 list(scenario["samples"][start:end]))


class ScorerTest(unittest.TestCase):
    def test_profile_checklist_true(self) -> None:
        report = reference.build_report()
        profile = report["profile_checklist"]
        for key, value in profile.items():
            if key in ("profile", "scorer_sha256"):
                continue
            if key == "missing_result_promoted":
                self.assertFalse(value)
                continue
            self.assertTrue(value, key)

    def test_duration_errors_zero(self) -> None:
        report = reference.build_report()
        for scenario in report["scenarios"]:
            self.assertEqual(scenario["duration_error_samples"], 0, scenario["name"])

    def test_rebuffer_has_underruns(self) -> None:
        report = reference.build_report()
        row = next(item for item in report["scenarios"] if item["name"] == "rebuffer_step")
        self.assertGreater(row["playback_buffering"]["underrun_ticks"], 0)

    def test_drift_partial_has_partial(self) -> None:
        report = reference.build_report()
        row = next(item for item in report["scenarios"] if item["name"] == "drift_partial_tail")
        self.assertTrue(row["final_partial_window"]["has_partial_input_window"])
        self.assertGreater(row["final_partial_window"]["partial_analysis_frames"], 0)

    def test_no_deleted_speech(self) -> None:
        report = reference.build_report()
        for scenario in report["scenarios"]:
            self.assertTrue(scenario["speech_preservation"]["no_deleted_speech"])

    def test_pause_filler_honored(self) -> None:
        report = reference.build_report()
        for scenario in report["scenarios"]:
            self.assertTrue(scenario["pause_filler_policy"]["source_timestamps_honored"])

    def test_mapping_monotonic_and_bounded(self) -> None:
        report = reference.build_report()
        for scenario in report["scenarios"]:
            mapping = scenario["source_output_mapping"]
            self.assertTrue(mapping["frame_source_starts_monotonic"])
            self.assertTrue(mapping["frame_source_intervals_in_bounds"])

    def test_transient_proxy_present(self) -> None:
        report = reference.build_report()
        for scenario in report["scenarios"]:
            self.assertTrue(scenario["transient_audibility_proxy"]["events"])

    def test_pitch_proxy_present(self) -> None:
        report = reference.build_report()
        for scenario in report["scenarios"]:
            self.assertTrue(scenario["pitch_preservation_proxy"]["windows"])

    def test_crosscheck_identical(self) -> None:
        cross = reference.crosscheck_payload()
        self.assertTrue(cross["all_chunk_identical"])


class ReportTest(unittest.TestCase):
    def test_report_keys(self) -> None:
        report = reference.build_report()
        self.assertEqual(set(report), reference.REPORT_KEYS)

    def test_canonical_report_stable(self) -> None:
        a, da = reference.canonical_report(reference.build_report())
        b, db = reference.canonical_report(reference.build_report())
        self.assertEqual(a, b)
        self.assertEqual(da, db)

    def test_report_disposition(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertEqual(report["qualification_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertFalse(report["processor_exposure"])
        self.assertFalse(report["public_surface_changed"])
        self.assertFalse(report["installed_v0_changed"])

    def test_no_literal_spdx_token_in_python_strings(self) -> None:
        token = "SPDX" + "-License-Identifier:"
        for path in TASK_DIR.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertEqual(text.count(token), 1, path.name)

    def test_json_files_parse_strictly(self) -> None:
        for path in TASK_DIR.glob("*.json"):
            raw = path.read_text(encoding="utf-8")
            parsed = json.loads(raw)
            self.assertIsInstance(parsed, dict)
            self.assertEqual(parsed["SPDX-FileCopyrightText"],
                             "2026 Tsakanyan Hovhannes")
            self.assertEqual(parsed["SPDX-License-Identifier"], "Apache-2.0")
            remaining = raw
            for key, value in (("SPDX-FileCopyrightText", "2026 Tsakanyan Hovhannes"),
                               ("SPDX-License-Identifier", "Apache-2.0")):
                remaining = remaining.replace(f'"{key}": "{value}"', "")
                remaining = remaining.replace(f'"{key}":"{value}"', "")
            self.assertNotIn('"SPDX-FileCopyrightText"', remaining)
            self.assertNotIn('"SPDX-License-Identifier"', remaining)

    def test_source_pins_in_report(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["source_pins"], fixture.SOURCE_PINS)

    def test_licensing_absent(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["licensing"]["ffmpeg_binary_or_source"], "absent")
        self.assertEqual(report["licensing"]["download_or_install"], "none")

    def test_ffmpeg_context_explicit(self) -> None:
        report = reference.build_report()
        ctx = report["ffmpeg_context"]
        self.assertTrue(ctx["blocked_context"])
        self.assertFalse(ctx["hidden_assumption"])
        self.assertFalse(ctx["binary_invoked"])


class CliTest(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "run.py", *args], cwd=TASK_DIR,
                              capture_output=True, text=True, check=False)

    def test_crosscheck_cli(self) -> None:
        result = self.run_cli("--crosscheck")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["all_chunk_identical"])

    def test_sources_cli(self) -> None:
        result = self.run_cli("--sources")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("sources_sha256", payload)

    def test_report_cli_writes(self) -> None:
        result = self.run_cli("--report")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("byte_identical=true", result.stdout)
        self.assertTrue((TASK_DIR / "report.json").is_file())
        self.assertTrue((TASK_DIR / "report.json.sha256").is_file())


if __name__ == "__main__":
    unittest.main()
