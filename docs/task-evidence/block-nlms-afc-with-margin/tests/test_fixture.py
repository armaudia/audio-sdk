"""Determinism, separation and failure-closed checks for the AFC reference.

Run from this task directory:
    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import hashlib
import math
import struct
import unittest
from pathlib import Path

import fixture as f


class ContractTests(unittest.TestCase):
    def test_v0_format_is_fixed(self) -> None:
        self.assertEqual(f.SAMPLE_RATE_HZ, 16000)
        self.assertEqual(f.CHANNELS, 1)
        self.assertEqual(f.FRAME_SAMPLES, 160)
        self.assertEqual(f.SAMPLE_FORMAT, "f32")

    def test_source_pins_are_exact(self) -> None:
        self.assertEqual(len(f.SOURCE_PINS), 2)
        for value in f.SOURCE_PINS.values():
            self.assertEqual(len(value), 64)
            self.assertTrue(all(c in "0123456789abcdef" for c in value))
        self.assertTrue(f.BOARD_SNAPSHOT["mutable"])

    def test_config_is_fail_closed(self) -> None:
        self.assertEqual(f.validate_config(f.DEFAULT_CONFIG), f.Status.OK)
        self.assertEqual(f.validate_config(None), f.Status.REJECTED_MISSING)
        self.assertEqual(f.validate_config("bad"), f.Status.REJECTED_INVALID)
        missing = dict(f.DEFAULT_CONFIG)
        del missing["mu"]
        self.assertEqual(f.validate_config(missing), f.Status.REJECTED_MISSING)
        self.assertEqual(f.validate_config(f.config_with(mu=float("nan"))),
                         f.Status.REJECTED_NONFINITE)
        self.assertEqual(f.validate_config(f.config_with(mu=2.0)),
                         f.Status.REJECTED_INVALID)
        self.assertEqual(f.validate_config(f.config_with(taps=32)),
                         f.Status.REJECTED_INVALID)
        self.assertEqual(f.validate_config(f.config_with(profile="lol")),
                         f.Status.REJECTED_INVALID)

    def test_frame_is_fail_closed(self) -> None:
        good = {"count": 160, "valid": 160, "samples": [0.0] * 160,
                "flags": 0, "epoch": 1, "position": 0}
        self.assertEqual(f.validate_frame(good), f.Status.OK)
        self.assertEqual(f.validate_frame(None), f.Status.REJECTED_MISSING)
        self.assertEqual(
            f.validate_frame(dict(good, count=159)), f.Status.REJECTED_TENSOR)
        self.assertEqual(
            f.validate_frame(dict(good, samples=[float("nan")] + [0.0] * 159)),
            f.Status.REJECTED_NONFINITE)
        self.assertEqual(
            f.validate_frame(dict(good, samples=[9.0] + [0.0] * 159)),
            f.Status.REJECTED_INVALID)
        self.assertEqual(f.validate_frame(dict(good, epoch=0)),
                         f.Status.REJECTED_EPOCH)
        self.assertEqual(f.validate_frame(dict(good, position=160)),
                         f.Status.REJECTED_POSITION)


class DeterminismTests(unittest.TestCase):
    def test_fixtures_are_deterministic(self) -> None:
        first = f.fixture_digests()
        f.synthetic_fixtures.cache_clear()
        self.assertEqual(f.fixture_digests(), first)

    def test_report_is_byte_identical(self) -> None:
        left, left_digest = f.canonical_report(f.build_report())
        right, right_digest = f.canonical_report(f.build_report())
        self.assertEqual(left, right)
        self.assertEqual(left_digest, right_digest)
        self.assertFalse(left.endswith("\n"))

    def test_tensor_digest_uses_little_endian_f32(self) -> None:
        self.assertEqual(f.tensor_digest([1.0]),
                         hashlib.sha256(struct.pack("<f", 1.0)).hexdigest())

    def test_binary_fixtures_match_pinned_manifest(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = (root / "fixtures" / "FIXTURES.sha256").read_text().splitlines()
        digests = f.fixture_digests()
        self.assertEqual(len(manifest), len(digests))
        for line in manifest:
            digest, name = line.split("  ", 1)
            self.assertEqual(digest, digests[name])
            data = (root / "fixtures" / name).read_bytes()
            self.assertEqual(len(data) % 4, 0)
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest)


class MeasurementTests(unittest.TestCase):
    def test_all_sections_present(self) -> None:
        results = f.build_report()["results"]
        self.assertEqual(results["completeness"]["missing_sections"], [])
        self.assertTrue(results["completeness"]["all_sections_measured"])
        self.assertFalse(results["completeness"]["missing_results_qualify_candidate"])

    def test_open_loop_is_causal(self) -> None:
        geometry = f.measure_geometry()
        self.assertEqual(geometry["added_delay_samples"], 0)
        self.assertEqual(geometry["buffering_delay_samples"], 0)
        self.assertEqual(geometry["impulse_peak_index"], 0)
        self.assertEqual(geometry["silence_peak_abs"], 0.0)

    def test_adaptive_reference_converges_and_tracks(self) -> None:
        convergence = f.measure_convergence()
        tracking = f.measure_tracking()
        self.assertIsNotNone(convergence["frames_to_threshold"])
        self.assertGreater(convergence["final_erle_db"], 12.0)
        self.assertIsNotNone(tracking["frames_to_retrack"])
        self.assertGreater(tracking["post_change_mean_erle_db"], 12.0)
        self.assertLess(tracking["final_misalignment_db"], 0.0)

    def test_latency_alignment_is_selected(self) -> None:
        latency = f.measure_reference_latency()
        self.assertEqual(latency["best_offset_samples"], 0)
        self.assertGreater(latency["aligned_erle_db"], 12.0)

    def test_reference_and_fixed_groups_are_separate(self) -> None:
        report = f.build_report()
        self.assertIn("reference_adaptation", report["results"])
        self.assertIn("fixed_attenuation", report["results"])
        self.assertNotIn("erle_db", report["results"]["fixed_attenuation"])
        self.assertNotIn("gain_margin", report["results"]["reference_adaptation"])

    def test_fixed_gain_is_level_only_and_bounded(self) -> None:
        fixed = f.measure_fixed_attenuation()
        margin = fixed["gain_margin"]
        self.assertAlmostEqual(margin["adaptive_margin_db"], -3.0)
        self.assertAlmostEqual(margin["fixed_attenuation_db"], -5.0)
        self.assertAlmostEqual(margin["adaptive_measured_linear_gain"],
                               margin["adaptive_configured_linear_gain"],
                               places=10)
        self.assertAlmostEqual(margin["fixed_measured_linear_gain"],
                               margin["fixed_configured_linear_gain"],
                               places=10)
        self.assertTrue(fixed["control_is_level_only"])
        self.assertEqual(fixed["headroom_and_nonlinearity"]["nonfinite_samples"], 0)

    def test_closed_loop_afc_margin_beats_afc_only_in_all_cases(self) -> None:
        matrix = f.measure_closed_loop()
        for name, controls in matrix.items():
            with self.subTest(case=name):
                adaptive = controls["afc_plus_margin"]
                plain = controls["afc_only"]
                self.assertEqual(adaptive["control_family"], "adaptive_reference")
                self.assertEqual(controls["fixed_gain"]["control_family"],
                                 "fixed_attenuation")
                self.assertLess(adaptive["tail_db_relative_to_program"],
                                plain["tail_db_relative_to_program"])
                self.assertEqual(adaptive["rejected_frames"], 0)
                self.assertEqual(adaptive["nonfinite_frames"], 0)

    def test_numerical_and_state_controls(self) -> None:
        adverse = f.measure_adverse_controls()
        self.assertTrue(adverse["state_unchanged_on_rejection"])
        self.assertTrue(adverse["reset_matches_fresh"])
        self.assertTrue(adverse["independent_sessions_match"])
        self.assertEqual(adverse["closed_session_status"], "closed")


if __name__ == "__main__":
    unittest.main()
