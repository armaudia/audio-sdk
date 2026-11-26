# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic acceptance suite for the SDK-UL-UNAS-DNS3 package."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402


class ReportIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_disposition_is_defer_not_qualified(self):
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertFalse(self.report["qualification"]["qualifies"])

    def test_eight_blocked_release_gates(self):
        gates = self.report["release_gates"]
        self.assertEqual([row["id"] for row in gates], [f"RG-{index:02d}" for index in range(1, 9)])
        self.assertTrue(all(row["status"] == "blocked" for row in gates))

    def test_enhancement_profile_items(self):
        profile = self.report["acceptance_profile"]
        self.assertEqual(profile["profile"], "enhancement")
        self.assertEqual(len(profile["required_items"]), 12)
        statuses = {row["status"] for row in profile["required_items"].values()}
        self.assertTrue(statuses.issubset({"synthetic_only", "blocked"}))
        blocked = sorted(name for name, row in profile["required_items"].items() if row["status"] == "blocked")
        self.assertEqual(self.report["profile_blockers"], blocked)
        self.assertIn("paired_stoi", blocked)
        self.assertIn("task_matched_baseline", blocked)

    def test_candidate_geometry_not_fabricated(self):
        candidate = self.report["candidate"]
        self.assertEqual(candidate["reported_input_sample_rate_hz"], 16000)
        self.assertIsNone(candidate["reported_hop_samples"])
        self.assertIsNone(candidate["reported_frame_samples"])
        self.assertIsNone(candidate["reported_channels"])
        self.assertIsNone(candidate["reported_algorithmic_latency_samples"])
        self.assertIsNone(candidate["reported_parameter_count"])
        self.assertFalse(candidate["geometry_documented"])
        self.assertFalse(candidate["configuration_verified"])
        self.assertFalse(candidate["checkpoint_lineage_verified"])
        self.assertFalse(candidate["source_present"])
        self.assertFalse(candidate["weights_present"])
        self.assertFalse(candidate["runtime_present"])
        self.assertFalse(candidate["exact_numeric_output_present"])

    def test_all_boundary_and_scope_flags(self):
        self.assertTrue(all(value is False for value in self.report["boundary"].values()))
        scope = self.report["scope"]
        self.assertTrue(scope["synthetic_only"])
        self.assertTrue(scope["task_local_only"])
        for key, value in scope.items():
            if key not in {"synthetic_only", "task_local_only"}:
                self.assertIs(value, False, key)

    def test_no_result_promoted(self):
        self.assertTrue(self.report["adverse_all_rejected"])
        for case in self.report["adverse_rejections"]:
            self.assertEqual(case["status"], "rejected")
            self.assertEqual(case["expected_code"], case["observed_code"])
            self.assertTrue(case["state_unchanged"])
        for section in ("paired_metrics", "clean_preservation", "peaks_and_invalid",
                        "pause_attenuation", "stoi", "baseline", "alignment",
                        "streaming", "reset", "final_partial", "state_and_memory",
                        "runtime_timing", "nonfinite"):
            self.assertIs(self.report[section]["qualifies"], False, section)
        self.assertFalse(self.report["qualification"]["missing_result_promoted"])

    def test_stoi_and_baseline_blocked(self):
        self.assertEqual(self.report["stoi"]["status"], "blocked")
        self.assertIsNone(self.report["stoi"]["value_millis"])
        self.assertEqual(self.report["baseline"]["status"], "blocked")
        self.assertIsNone(self.report["baseline"]["baseline_id"])

    def test_six_exact_blockers(self):
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(blockers), 6)
        identifiers = {row["id"] for row in blockers}
        self.assertIn("pinned_ul_unas_source_weights_runtime_absent", identifiers)
        self.assertIn("streaming_geometry_and_reproducible_backend_unverified", identifiers)
        self.assertIn("timing_and_independent_review_absent", identifiers)


class MetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = reference.build_report()

    def test_paired_metrics_exact(self):
        paired = self.report["paired_metrics"]
        self.assertEqual(len(paired["regions"]), 3)
        for region in paired["regions"]:
            self.assertIs(region["qualifies"], False)
            self.assertEqual(region["surrogate_si_sdr_millidb"],
                             region["identity_si_sdr_millidb"] + region["delta_si_sdr_millidb"])
        self.assertTrue(paired["no_noisy_region_degraded"])
        self.assertEqual(paired["min_delta_si_sdr_millidb"],
                         min(row["delta_si_sdr_millidb"] for row in paired["regions"]))

    def test_si_sdr_scale_invariant(self):
        clean = [0, 1000, -2000, 3000, 0, -1000]
        self.assertEqual(reference.si_sdr_millidb(clean, clean, 0, 6), reference.MAX_MILLIDB)
        scaled = [value * 3 for value in clean]
        self.assertEqual(reference.si_sdr_millidb(clean, scaled, 0, 6), reference.MAX_MILLIDB)
        silent = [0, 0, 0, 0, 0, 0]
        self.assertEqual(reference.si_sdr_millidb(silent, scaled, 0, 6), reference.MIN_MILLIDB)

    def test_clean_preservation(self):
        clean = self.report["clean_preservation"]
        self.assertEqual(len(clean["regions"]), 2)
        for region in clean["regions"]:
            self.assertIs(region["qualifies"], False)
            self.assertGreater(region["si_sdr_millidb"], 30000)
            self.assertLess(abs(region["level_change_millidb"]), 500)
            self.assertLess(region["peak_milli"], 1000)
        self.assertEqual(clean["nonfinite_output_count"], 0)

    def test_peaks_pause_alignment(self):
        peaks = self.report["peaks_and_invalid"]
        self.assertLess(peaks["max_peak_milli"], peaks["peak_bound_milli"])
        self.assertEqual(peaks["clipped_samples"], 0)
        self.assertEqual(peaks["invalid_output_count"], 0)
        self.assertGreater(self.report["pause_attenuation"]["noise_attenuation_millidb"], 0)
        alignment = self.report["alignment"]
        self.assertEqual(alignment["surrogate_content_delay_samples"], 0)
        self.assertEqual(alignment["best_shift_samples"], 0)
        self.assertTrue(alignment["zero_shift_best"])

    def test_streaming_reset_partial(self):
        streaming = self.report["streaming"]
        self.assertTrue(streaming["all_match"])
        self.assertEqual(streaming["accepted_samples"], 12000)
        self.assertEqual(sum(streaming["chunks"]), 12000)
        self.assertFalse(streaming["scheduler_measured"])
        self.assertTrue(self.report["reset"]["matches_fresh"])
        self.assertEqual(self.report["reset"]["epoch"], 2)
        partial = self.report["final_partial"]
        self.assertEqual(partial["valid_count"], 137)
        self.assertEqual(partial["output_samples"], 160)
        self.assertEqual(partial["advanced_samples"], 137)
        self.assertTrue(partial["padding_zero"])
        self.assertTrue(partial["tail_zero"])


class StrictInputTests(unittest.TestCase):
    def test_strict_json_rejects_duplicate_and_nonfinite(self):
        for text, code in (('{"a":1,"a":2}', "duplicate_json_key:a"),
                           ('{"a":NaN}', "nonfinite_json_constant:NaN"),
                           ('{"a":Infinity}', "nonfinite_json_constant:Infinity")):
            with self.assertRaisesRegex(ValueError, code):
                reference.load_strict_json_text(text)
        with self.assertRaises(ValueError):
            reference.load_strict_json_text("[1,2,3]")

    def test_frame_and_reset_rejections_keep_state(self):
        surrogate = reference.BlockEnergyGateSurrogate(epoch=1)
        frame = [0.0] * 160
        surrogate.process_frame(frame)
        before = surrogate.state_digest
        with self.assertRaises(reference.ReferenceRejection) as ctx:
            surrogate.process_frame([float("nan")] + frame[1:])
        self.assertEqual(ctx.exception.code, "nonfinite_input:input")
        self.assertEqual(surrogate.state_digest, before)
        with self.assertRaises(reference.ReferenceRejection) as ctx:
            surrogate.reset(1, 0)
        self.assertEqual(ctx.exception.code, "invalid_epoch")
        self.assertEqual(surrogate.state_digest, before)

    def test_caller_manifest_validation(self):
        manifest = reference._base_manifest()
        result = reference.validate_caller_manifest(manifest)
        self.assertTrue(result["validated"])
        self.assertFalse(result["loaded"])
        self.assertFalse(result["executed"])
        with self.assertRaises(reference.ReferenceRejection) as ctx:
            reference.validate_caller_manifest({**manifest, "sample_rate_hz": 8000})
        self.assertEqual(ctx.exception.code, "unsupported_sample_rate")


class DeterminismTests(unittest.TestCase):
    def test_report_is_byte_identical(self):
        reports = [reference.canonical_report(reference.build_report())[0] for _ in range(3)]
        self.assertEqual(reports[0], reports[1])
        self.assertEqual(reports[1], reports[2])

    def test_source_pins_present(self):
        for path, expected in reference.SOURCE_PINS.items():
            full = reference.SOURCE_ROOT / path
            self.assertTrue(full.is_file(), path)
            self.assertEqual(reference.file_digest(full), expected, path)
        for path, expected in reference.BOUNDARY_PINS.items():
            full = reference.SDK_ROOT / path
            self.assertTrue(full.is_file(), path)
            self.assertEqual(reference.file_digest(full), expected, path)

    def test_scope_base_fails_closed_when_missing(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            repo.mkdir()
            # no git repo => missing refs
            self.assertIsNone(reference.scope_base(repo))


if __name__ == "__main__":
    unittest.main()
