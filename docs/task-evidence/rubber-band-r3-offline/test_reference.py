# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for task-local synthetic offline TSM evidence."""

from __future__ import annotations

from pathlib import Path
import unittest

import check_licensing
import fixture
import reference
import run as runner
import scorer
import verify

TASK_DIR = Path(__file__).resolve().parent
REPORT = reference.build_report()
STIMULI = fixture.build_stimuli()
CASES = REPORT["cases"]


class PinTests(unittest.TestCase):
    def test_source_pins_verified(self):
        pins = fixture.verify_source_pins()
        self.assertTrue(all(item["verified"] for item in pins.values()))

    def test_boundary_pins_verified(self):
        pins = fixture.verify_boundary_pins()
        self.assertTrue(all(item["verified"] for item in pins.values()))

    def test_board_snapshot_is_mutable_provenance(self):
        self.assertTrue(fixture.BOARD_SNAPSHOT["mutable"])
        self.assertFalse(fixture.BOARD_SNAPSHOT["qualifies"])

    def test_sources_manifest_matches_files(self):
        lines = (TASK_DIR / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines, runner.source_manifest_lines())

    def test_contract_and_descriptors_are_strict_json(self):
        for name in ("contract.json", "adapter.json", "provider.json", "report.json"):
            data = verify.strict_json(TASK_DIR / name)
            self.assertIsInstance(data, dict)


class FixtureTests(unittest.TestCase):
    def test_fixture_digest_stable(self):
        self.assertEqual(fixture.fixture_digest(), fixture.digest_value(fixture.fixture_recipe()))

    def test_stimuli_are_reproducible(self):
        again = fixture.build_stimuli()
        for name, samples in STIMULI.items():
            self.assertEqual(fixture.digest_value(samples), fixture.digest_value(again[name]))

    def test_silence_is_exact_zeros(self):
        self.assertEqual(set(STIMULI["silence"]), {0.0})

    def test_click_starts_frozen(self):
        self.assertEqual(list(fixture.CLICK_STARTS), [2400, 6400, 10400, 14400])

    def test_final_partial_is_not_frame_aligned(self):
        source_remainder = len(STIMULI["final_partial"]) % fixture.FRAME_SAMPLES
        self.assertNotEqual(source_remainder, 0)
        case = CASES["final_partial_window"]
        target = case["duration"]["target_output_samples"]
        self.assertEqual(case["playback_buffering"]["final_partial_window_valid_samples"],
                         target % fixture.FRAME_SAMPLES)

    def test_labels_use_source_timestamps(self):
        for entry in fixture.DECISION_LABELS["speech_unfamiliar"]:
            self.assertLess(entry["source_start"], entry["source_end"])
            self.assertEqual(entry["source_start"] * fixture.NS_PER_SAMPLE,
                             entry["source_start"] * 62500)


class ValidationTests(unittest.TestCase):
    def test_reject_nonfinite(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_samples([0.0, float("nan")], "bad")

    def test_reject_infinite(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_samples([0.0, float("inf")], "bad")

    def test_reject_empty(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_samples([], "bad")

    def test_reject_out_of_range(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_samples([2.0], "bad")

    def test_reject_missing_schedule(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_schedule([])

    def test_reject_nonfinite_rate(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_schedule([(0, float("nan"))])

    def test_reject_zero_rate(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_schedule([(0, 0.0)])

    def test_reject_oversized_rate(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_schedule([(0, 3.0)])

    def test_reject_nonmonotone_schedule(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_schedule([(0, 1.0), (0, 1.1)])

    def test_reject_schedule_without_origin(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_schedule([(160, 1.0)])

    def test_unknown_case_is_rejected(self):
        with self.assertRaises(reference.ReferenceError):
            reference.run_case("not_registered", STIMULI)


class EngineTests(unittest.TestCase):
    def test_prefix_monotone(self):
        prefix = reference.build_prefix(1600, [(0, 1.25)])
        values = [prefix[i + 1] - prefix[i] for i in range(len(prefix) - 1)]
        self.assertTrue(all(value > 0 for value in values))
        self.assertAlmostEqual(prefix[-1], 1280.0, places=6)

    def test_prefix_rate_change(self):
        prefix = reference.build_prefix(1600, [(0, 1.0), (800, 2.0)], ramp=0)
        self.assertAlmostEqual(prefix[800], 800.0, places=6)
        self.assertAlmostEqual(prefix[1600], 1200.0, places=6)

    def test_rate_at_ramp(self):
        schedule = [(0, 1.0), (800, 1.5)]
        self.assertAlmostEqual(reference.rate_at(0, schedule, 100), 1.0)
        self.assertAlmostEqual(reference.rate_at(850, schedule, 100), 1.25)
        self.assertAlmostEqual(reference.rate_at(900, schedule, 100), 1.5)

    def test_identity_is_bit_exact(self):
        source = STIMULI["tonal"]
        output, records = reference.identity_reference(source)
        self.assertEqual(output, source)
        self.assertTrue(records)

    def test_ola_has_exact_target_length(self):
        for name in ("speed_up_125", "speed_down_080", "drift_case"):
            self.assertEqual(CASES[name]["duration"]["error_samples"], 0)

    def test_ola_output_finite_and_bounded(self):
        for case in CASES.values():
            self.assertEqual(case["signal"]["nonfinite"], 0)
            self.assertLessEqual(case["signal"]["peak"], 1.0)

    def test_ola_mapping_monotone(self):
        for case in CASES.values():
            self.assertTrue(case["mapping"]["output_centers_monotone"])
            self.assertTrue(case["mapping"]["output_centers_within_target"])

    def test_wsola_shift_used(self):
        case = CASES["speed_up_125"]
        shifts = [record["wsola_shift"] for record in case["mapping_records"]]
        self.assertTrue(any(shift != 0 for shift in shifts))

    def test_terminal_window_covers_late_gap(self):
        # Synthetic prefix with a long tail gap forces the terminal OLA window
        # path without changing any frozen report fixture.
        source = STIMULI["tonal"][:1600]
        prefix = [min(float(index) * 0.5, 200.0) for index in range(len(source) + 1)]
        output, records = reference.ola_wsola(source, prefix, 800)
        self.assertEqual(len(output), 800)
        terminal = [record for record in records if record["terminal_repeat"]]
        self.assertEqual(len(terminal), 1)
        self.assertTrue(all(not record["terminal_repeat"] for record in
                            reference.ola_wsola(source, [float(i) for i in range(len(source) + 1)],
                                                1600)[1]))


class RateProfileTests(unittest.TestCase):
    def test_identity_pitch_preserved(self):
        pitch = CASES["identity_1x"]["pitch_proxy"]
        self.assertTrue(pitch["pitch_preserved_proxy"])

    def test_ola_pitch_preserved_on_tone(self):
        pitch = CASES["tonal_pitch_case"]["pitch_proxy"]
        self.assertAlmostEqual(pitch["octave_normalized_scale"], 1.0, delta=0.08)

    def test_varispeed_changes_pitch_adversely(self):
        pitch = CASES["varispeed_adverse"]["pitch_proxy"]
        self.assertGreater(pitch["scale"], 1.2)
        self.assertFalse(pitch["pitch_preserved_proxy"])

    def test_silence_pitch_withheld(self):
        pitch = CASES["silence_case"]["pitch_proxy"]
        self.assertFalse(pitch["applicable"])
        self.assertTrue(pitch["missing"])

    def test_transient_proxy_reports_clicks(self):
        comparison = CASES["transient_case"]["transient_proxy_comparison"]
        self.assertEqual(len(comparison["candidate"]["clicks"]), len(fixture.CLICK_STARTS))
        self.assertGreater(comparison["candidate"]["mean_peak_to_local_rms"], 1.0)

    def test_transient_smearing_regression_is_visible(self):
        comparison = CASES["transient_case"]["transient_proxy_comparison"]
        self.assertGreater(comparison["candidate_max_width"], comparison["identity_max_width"])

    def test_unsmoothed_step_is_adverse(self):
        case = CASES["rate_step_unsmoothed_adverse"]
        self.assertTrue(case["adverse_control"])
        self.assertFalse(case["candidate_qualified"])
        self.assertEqual(case["ramp_samples"], 0)

    def test_speech_preservation_entries(self):
        preservation = CASES["source_timestamp_policy"]["speech_preservation"]
        self.assertGreaterEqual(preservation["speech_intervals"], 2)
        self.assertTrue(all(item["source_timestamped"] for item in preservation["entries"]))

    def test_rate_decisions_tied_to_source_labels(self):
        case = CASES["source_timestamp_policy"]
        starts = {change["source_sample"] for change in case["rate_bounds"]["changes"]}
        label_starts = {item["source_start"] for item in
                        fixture.DECISION_LABELS["speech_unfamiliar"]}
        self.assertTrue(label_starts.issubset(starts))
        self.assertTrue(all(change["source_ns"] == change["source_sample"] * 62500
                            for change in case["rate_bounds"]["changes"]))

    def test_rebuffer_is_source_timestamped(self):
        rebuffer = CASES["rebuffer_case"]["playback_buffering"]["rebuffer"]
        self.assertEqual(rebuffer["source_sample"], 6400)
        self.assertEqual(rebuffer["source_ns"], 6400 * 62500)
        self.assertTrue(rebuffer["decision_tied_to_source_timestamp"])

    def test_rebuffer_withheld_when_missing(self):
        self.assertIsNone(CASES["speed_up_125"]["playback_buffering"]["rebuffer"])

    def test_drift_changes_schedule(self):
        case = CASES["drift_case"]
        self.assertEqual(len(case["schedule"]), 4)
        self.assertEqual(case["duration"]["error_samples"], 0)

    def test_buffering_checkpoints_monotone(self):
        checkpoints = CASES["rebuffer_case"]["playback_buffering"]["checkpoints"]
        values = [item["ideal_output_samples"] for item in checkpoints]
        self.assertEqual(values, sorted(values))
        frames = [item["full_output_frames"] for item in checkpoints]
        self.assertEqual(frames, sorted(frames))

    def test_no_device_claim(self):
        self.assertFalse(REPORT["method"]["device_or_listening_claim"])
        self.assertFalse(
            CASES["identity_1x"]["playback_buffering"]["qualifies_device_claim"]
        )


class ReportTests(unittest.TestCase):
    def test_canonical_bytes(self):
        canonical = fixture.canonical_bytes(REPORT)
        self.assertEqual((TASK_DIR / "report.json").read_bytes(), canonical + b"\n")

    def test_sidecar_digest(self):
        sidecar = (TASK_DIR / "report.json.sha256").read_text(encoding="ascii").strip()
        self.assertEqual(sidecar, fixture.sha256_bytes(fixture.canonical_bytes(REPORT)))

    def test_three_cold_digests_identical(self):
        digests = [reference.cold_core_digest() for _ in range(3)]
        self.assertEqual(len(set(digests)), 1)
        self.assertEqual(digests[0], REPORT["crosscheck"]["canonical_core_digest"])

    def test_decision_is_defer(self):
        self.assertEqual(REPORT["status"], "proposal_only_not_qualified")
        self.assertEqual(REPORT["decision"], "DEFER")
        self.assertEqual(REPORT["processor_exposure"], "none")

    def test_adverse_never_qualifies(self):
        for name, case in CASES.items():
            if case["adverse_control"]:
                self.assertFalse(case["candidate_qualified"], name)

    def test_incomplete_never_qualifies(self):
        for name, case in CASES.items():
            if not case["all_required_results_present"]:
                self.assertFalse(case["candidate_qualified"], name)

    def test_invalid_rows_present_and_nonqualifying(self):
        rows = REPORT["invalid_and_missing_cases"]
        self.assertGreaterEqual(len(rows), 12)
        self.assertTrue(all(not row["candidate_qualified"] for row in rows))
        self.assertTrue(all(not row["missing_result_promoted"] for row in rows))

    def test_no_release_claim(self):
        self.assertTrue(REPORT["qualification"]["no_release_claim"])
        self.assertTrue(REPORT["qualification"]["no_missing_result_may_qualify"])


class ScopeAndLicensingTests(unittest.TestCase):
    def test_spdx_headers(self):
        self.assertEqual(verify.check_spdx(), [])

    def test_licensing_audit(self):
        self.assertEqual(check_licensing.audit(), [])

    def test_no_c_or_cmake_boundary(self):
        paths = [path.name for path in TASK_DIR.rglob("*") if path.is_file()]
        self.assertNotIn("CMakeLists.txt", paths)
        self.assertFalse(any(name.endswith(".c") or name.endswith(".h") for name in paths))

    def test_installed_v0_unchanged(self):
        self.assertTrue(REPORT["installed_v0_unchanged"])
        self.assertEqual(verify.strict_json(TASK_DIR / "adapter.json")["frame_samples"], 160)


if __name__ == "__main__":
    unittest.main(verbosity=2)
