# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the ROSE-CD RMS-matched evidence package.

No network, no checkpoint, no real audio, no neural runtime and no skips.  Run
after ``run.py`` has generated the canonical artifacts::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
"""

from __future__ import annotations

import hashlib
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
REPORT_CACHE = None


def report() -> dict:
    global REPORT_CACHE
    if REPORT_CACHE is None:
        REPORT_CACHE = reference.build_report()
    return REPORT_CACHE


def asset_manifest(root: Path, **overrides):
    checkpoint = root / reference.CHECKPOINT_FILENAME
    if not checkpoint.exists():
        checkpoint.write_bytes(b"caller-owned-placeholder-checkpoint")
    source = root / "ROSE-CD"
    if not source.exists():
        source.mkdir()
        for marker in reference.SOURCE_MARKERS:
            target = source / marker
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"marker")
    manifest = {
        "channels": reference.CHANNELS,
        "checkpoint_path": str(checkpoint),
        "checkpoint_revision": reference.CHECKPOINT_REVISION,
        "checkpoint_sha256": reference.sha256_file(checkpoint),
        "frame_samples": reference.FRAME_SAMPLES,
        "peak_policy": "unpinned",
        "rms_match_reference": "noisy_input",
        "rms_match_scope": "whole_clip",
        "sample_rate_hz": reference.SAMPLE_RATE_HZ,
        "source_dir": str(source),
        "source_revision": reference.UPSTREAM_COMMIT,
        "variant": "one-step-rms-matched",
    }
    manifest.update(overrides)
    return manifest


class CanonicalJsonTests(unittest.TestCase):
    def test_canonical_bytes_sorted_and_newline(self):
        data = reference.canonical_bytes({"b": 1, "a": 2})
        self.assertTrue(data.endswith(b"\n"))
        self.assertLess(data.index(b'"a"'), data.index(b'"b"'))

    def test_strict_loads_accepts_object(self):
        self.assertEqual(reference.strict_loads('{"a": 1}'), {"a": 1})

    def test_strict_loads_rejects_duplicate_key(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1, "a": 2}')

    def test_strict_loads_rejects_nan(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": NaN}')

    def test_strict_loads_rejects_infinity(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": Infinity}')

    def test_strict_loads_rejects_non_object(self):
        with self.assertRaises(ValueError):
            reference.strict_loads("[1, 2]")

    def test_strict_loads_rejects_trailing_text(self):
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a": 1} trailing')

    def test_negative_zero_detection(self):
        self.assertTrue(reference.has_negative_zero({"a": -0.0}))
        self.assertFalse(reference.has_negative_zero({"a": 0.0}))

    def test_metric_normalises_zero(self):
        self.assertEqual(reference._metric(-0.0), 0.0)
        self.assertEqual(reference._metric(1.234567890123), 1.23456789)

    def test_metric_rejects_nonfinite(self):
        with self.assertRaises(ValueError):
            reference._metric(math.inf)


class FixtureTests(unittest.TestCase):
    def test_total_samples(self):
        self.assertEqual(len(reference.FIXTURE_COMPONENTS["noisy"]),
                         reference.TOTAL_SAMPLES)

    def test_segment_coverage_is_contiguous(self):
        cursor = 0
        for segment in reference.SEGMENTS:
            self.assertEqual(segment["start_frame"], cursor)
            cursor = segment["end_frame"]
        self.assertEqual(cursor, reference.TOTAL_FRAMES)

    def test_noisy_decomposition_is_exact(self):
        components = reference.FIXTURE_COMPONENTS
        for index in range(reference.TOTAL_SAMPLES):
            expected = reference._clip16(
                components["clean"][index] + components["noise"][index])
            self.assertEqual(components["noisy"][index], expected)

    def test_int16_range(self):
        for values in reference.FIXTURE_COMPONENTS.values():
            self.assertGreaterEqual(min(values), -32768)
            self.assertLessEqual(max(values), 32767)

    def test_silence_segment_exactly_zero(self):
        end = 25 * reference.FRAME_SAMPLES
        self.assertTrue(all(value == 0
                            for value in reference.FIXTURE_COMPONENTS["clean"][:end]))
        self.assertTrue(all(value == 0
                            for value in reference.FIXTURE_COMPONENTS["noise"][:end]))

    def test_clean_has_headroom(self):
        peak = max(abs(value)
                   for value in reference.as_float(
                       reference.FIXTURE_COMPONENTS["noisy"]))
        self.assertLess(peak, 1.0)

    def test_fixture_spec_digest_stable(self):
        self.assertEqual(reference.FIXTURE_SPEC_DIGEST,
                         reference.sha256(reference.canonical_bytes(
                             reference.fixture_spec())))

    def test_component_digests_cover_all_components(self):
        self.assertEqual(set(reference.FIXTURE_DIGESTS),
                         {"clean", "noise", "noisy"})

    def test_fixture_is_byte_stable(self):
        self.assertEqual(reference.component_digests(reference.build_fixture()),
                         reference.FIXTURE_DIGESTS)


class ConfigTests(unittest.TestCase):
    def test_baseline_accepted(self):
        reference.validate_config(reference.CONFIG)

    def test_unknown_key_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(dict(reference.CONFIG, extra=True))

    def test_sample_rate_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(
                dict(reference.CONFIG, sample_rate_hz=48000))

    def test_channels_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(dict(reference.CONFIG, channels=2))

    def test_frame_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(
                dict(reference.CONFIG, frame_samples=256))

    def test_streaming_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(
                dict(reference.CONFIG, execution="streaming"))

    def test_frame_scope_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(
                dict(reference.CONFIG, rms_match_scope="frame"))

    def test_clean_reference_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(
                dict(reference.CONFIG, rms_match_reference="clean_input"))

    def test_raw_variant_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(dict(reference.CONFIG, variant="one-step"))

    def test_real_runtime_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(dict(reference.CONFIG, real_runtime=True))

    def test_model_used_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(dict(reference.CONFIG, model_used=True))

    def test_non_object_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config([])

    def test_bool_for_int_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_config(dict(reference.CONFIG, channels=True))


class ClipValidationTests(unittest.TestCase):
    def test_valid_clip_accepted(self):
        self.assertEqual(reference.validate_clip([0.0, 0.5, -0.5]),
                         [0.0, 0.5, -0.5])

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_clip([])

    def test_non_sequence_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_clip("samples")

    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_clip([0.0, math.nan])

    def test_infinity_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_clip([0.0, math.inf])

    def test_boolean_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_clip([0.0, True])

    def test_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_clip([0.0, 1.5])

    def test_rejection_does_not_mutate_input(self):
        values = [0.0, 0.25]
        reference.validate_clip(values)
        self.assertEqual(values, [0.0, 0.25])


class RmsMatchTests(unittest.TestCase):
    def setUp(self):
        self.reference = [0.1, -0.2, 0.3, -0.4]
        self.enhanced = [0.05, -0.1, 0.15, -0.2]

    def test_output_length_matches(self):
        result = reference.rms_match(self.enhanced, self.reference)
        self.assertEqual(len(result["matched"]), len(self.reference))

    def test_gain_is_rms_ratio(self):
        result = reference.rms_match(self.enhanced, self.reference)
        self.assertEqual(result["gain"], reference.rms(self.reference) /
                         reference.rms(self.enhanced))

    def test_matched_rms_equals_reference_rms(self):
        result = reference.rms_match(self.enhanced, self.reference)
        self.assertAlmostEqual(reference.rms(result["matched"]),
                               reference.rms(self.reference), places=15)

    def test_output_is_positive_scale_of_input(self):
        result = reference.rms_match(self.enhanced, self.reference)
        gain = result["gain"]
        for original, matched in zip(self.enhanced, result["matched"]):
            self.assertEqual(matched, gain * original)

    def test_zero_reference_returns_exact_zeros(self):
        result = reference.rms_match(self.enhanced, [0.0] * 4)
        self.assertFalse(result["defined"])
        self.assertIsNone(result["gain"])
        self.assertTrue(all(value == 0.0 for value in result["matched"]))

    def test_zero_enhanced_rejected(self):
        with self.assertRaises(ValueError):
            reference.rms_match([0.0] * 4, self.reference)

    def test_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            reference.rms_match(self.enhanced[:3], self.reference)

    def test_nonfinite_enhanced_rejected(self):
        bad = list(self.enhanced)
        bad[1] = math.nan
        with self.assertRaises(ValueError):
            reference.rms_match(bad, self.reference)

    def test_nonfinite_reference_rejected(self):
        bad = list(self.reference)
        bad[1] = math.inf
        with self.assertRaises(ValueError):
            reference.rms_match(self.enhanced, bad)

    def test_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            reference.rms_match([0.0, 2.0], [0.0, 0.1])

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            reference.rms_match([], [])

    def test_correlation_is_one(self):
        result = reference.rms_match(self.enhanced, self.reference)
        self.assertAlmostEqual(
            reference.correlation(result["matched"], self.enhanced), 1.0,
            places=15)

    def test_si_sdr_invariant_under_positive_gain(self):
        result = reference.rms_match(self.enhanced, self.reference)
        self.assertAlmostEqual(
            reference.si_sdr(result["matched"], self.reference),
            reference.si_sdr(self.enhanced, self.reference), places=12)


class SurrogateTests(unittest.TestCase):
    def setUp(self):
        self.noisy = reference.as_float(reference.FIXTURE_COMPONENTS["noisy"])

    def test_output_length_preserved(self):
        result = reference.surrogate_enhance(self.noisy)
        self.assertEqual(len(result["output"]), len(self.noisy))

    def test_noise_floor_positive(self):
        result = reference.surrogate_enhance(self.noisy)
        self.assertGreater(result["noise_floor_rms"], 0.0)

    def test_frame_gain_count(self):
        result = reference.surrogate_enhance(self.noisy)
        self.assertEqual(len(result["frame_gains"]),
                         reference.TOTAL_FRAMES)

    def test_silence_gain_is_zero(self):
        result = reference.surrogate_enhance([0.0] * 640)
        self.assertTrue(all(gain == 0.0 for gain in result["frame_gains"]))

    def test_surrogate_output_finite(self):
        result = reference.surrogate_enhance(self.noisy)
        self.assertTrue(all(math.isfinite(value) for value in result["output"]))

    def test_process_offline_reports_undefined_gain_for_silence(self):
        result = reference.process_offline([0.0] * 640)
        self.assertFalse(result["matched_defined"])
        self.assertIsNone(result["gain"])


class MetricsTests(unittest.TestCase):
    def test_self_si_sdr_is_large(self):
        signal = [0.1, -0.2, 0.3]
        self.assertGreater(reference.si_sdr(signal, signal), 100.0)

    def test_si_sdr_length_mismatch(self):
        with self.assertRaises(ValueError):
            reference.si_sdr([0.1], [0.1, 0.2])

    def test_si_sdr_silence_undefined(self):
        self.assertIsNone(reference.si_sdr([0.0, 0.0], [0.0, 0.0]))

    def test_snr_identical_signals(self):
        signal = [0.1, -0.2, 0.3]
        self.assertEqual(reference.snr_db(signal, signal), 120.0)

    def test_correlation_anticorrelated(self):
        self.assertAlmostEqual(reference.correlation([1.0, 2.0],
                                                     [-1.0, -2.0]), -1.0)

    def test_peak_and_clipped(self):
        self.assertEqual(reference.peak([-0.5, 0.9]), 0.9)
        self.assertEqual(reference.clipped_count([-0.5, 0.9]), 0)

    def test_nonfinite_count(self):
        self.assertEqual(reference.nonfinite_count([0.0, math.nan]), 1)


class AssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(
            prefix="rose-cd-rms-test-")
        cls.root = Path(cls.temp.name)
        cls.manifest = asset_manifest(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_generic_manifest_accepted_without_execution(self):
        result = reference.validate_caller_asset(self.manifest)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["loaded"])
        self.assertFalse(result["executed"])
        self.assertFalse(result["imported"])
        self.assertFalse(result["pinned_model"])

    def test_missing_field_rejected(self):
        manifest = dict(self.manifest)
        manifest.pop("peak_policy")
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(manifest)

    def test_extra_field_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(dict(self.manifest, extra=True))

    def test_relative_checkpoint_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest,
                     checkpoint_path=reference.CHECKPOINT_FILENAME))

    def test_relative_source_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest,
                     source_dir=reference.SOURCE_CHECKOUT_PATH))

    def test_absent_checkpoint_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest,
                     checkpoint_path=str(self.root / "absent.ckpt")))

    def test_checkpoint_hash_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, checkpoint_sha256="0" * 64))

    def test_wrong_source_revision_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, source_revision="0" * 40))

    def test_wrong_checkpoint_revision_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, checkpoint_revision="0" * 40))

    def test_wrong_geometry_rejected(self):
        for override in ({"sample_rate_hz": 48000}, {"channels": 2},
                         {"frame_samples": 256}):
            with self.assertRaises(ValueError):
                reference.validate_caller_asset(
                    dict(self.manifest, **override))

    def test_raw_variant_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, variant="one-step"))

    def test_streaming_scope_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, rms_match_scope="streaming"))

    def test_clean_reference_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, rms_match_reference="clean_input"))

    def test_guessed_peak_policy_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, peak_policy="clip_to_unity"))

    def test_pinned_placeholder_rejected(self):
        with self.assertRaises(ValueError):
            reference.pinned_asset_identity(
                dict(self.manifest,
                     checkpoint_sha256=reference.CHECKPOINT_SHA256))

    def test_workspace_checkpoint_absent(self):
        path = reference.resolve_source_path(reference.CHECKPOINT_PATH)
        self.assertFalse(path.is_file())


class ReportTests(unittest.TestCase):
    def test_disposition(self):
        self.assertEqual(report()["decision"], "DEFER")
        self.assertEqual(report()["evidence_status"], "incomplete")
        self.assertEqual(report()["qualification_status"], "not_qualified")
        self.assertEqual(report()["status"], reference.STATUS)

    def test_eight_blocked_gates(self):
        gates = report()["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))

    def test_four_exact_blockers(self):
        self.assertEqual(len(report()["exact_blockers"]), 4)

    def test_missing_result_rule(self):
        self.assertTrue(report()["no_missing_result_qualifies_candidate"])
        self.assertTrue(report()["missing_results"])

    def test_contract_digest(self):
        self.assertEqual(report()["contract_sha256"],
                         hashlib.sha256(reference.contract_bytes()).hexdigest())

    def test_no_negative_zero(self):
        self.assertFalse(reference.has_negative_zero(report()))

    def test_cold_start_deterministic(self):
        first = reference.canonical_report_bytes(reference.build_report())
        second = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(first, second)

    def test_canonical_report_roundtrip(self):
        payload = reference.strict_loads(
            reference.canonical_report_bytes(report()).decode("utf-8"))
        self.assertEqual(payload, report())

    def test_report_metrics_finite_and_bounded(self):
        metrics = report()["metrics"]
        self.assertEqual(metrics["raw_surrogate"]["nonfinite_samples"], 0)
        self.assertEqual(metrics["rms_matched_surrogate"]["nonfinite_samples"], 0)
        self.assertEqual(metrics["rms_matched_surrogate"]["clipped_samples"], 0)
        self.assertLessEqual(metrics["max_abs_output"], 1.0)
        self.assertEqual(metrics["si_sdr_delta_matched_minus_raw_db"], 0.0)

    def test_controls_rejected(self):
        controls = report()["controls"]
        self.assertTrue(controls["asset"]["rejected_all"])
        self.assertTrue(controls["config"]["rejected_all"])
        self.assertTrue(controls["shape"]["clip_rejected_all"])
        self.assertTrue(controls["shape"]["rms_match_rejected_all"])
        self.assertTrue(controls["silence"]["exact_zero"])
        self.assertFalse(controls["silence"]["gain_defined"])

    def test_matching_invariants(self):
        invariance = report()["controls"]["invariance"]
        self.assertTrue(invariance["matched_rms_equals_noisy_rms"])
        self.assertTrue(invariance["si_sdr_invariant"])
        self.assertTrue(invariance["gain_matches_rms_ratio"])
        self.assertEqual(invariance["correlation_matched_raw"], 1.0)

    def test_injected_scale_control(self):
        control = report()["controls"]["scale_restoration"]
        self.assertTrue(control["restored_rms_equals_noisy_rms"])
        self.assertTrue(control["si_sdr_preserved"])
        expected = (-control["attenuation_gain_db"] +
                    20.0 * math.log10(report()["rms_match"]["gain"]))
        self.assertAlmostEqual(control["applied_gain_db"], expected, places=6)

    def test_whole_clip_only(self):
        scope = report()["controls"]["whole_clip_scope"]
        self.assertTrue(scope["whole_clip_only"])
        self.assertFalse(scope["streaming_capable"])
        self.assertFalse(scope["prefix_matches_full"])

    def test_determinism_control(self):
        determinism = report()["controls"]["determinism"]
        self.assertTrue(determinism["identical"])
        self.assertEqual(determinism["runs"], 3)

    def test_asset_pins_absent(self):
        pins = report()["asset_pins"]
        self.assertFalse(pins["asset:checkpoint"]["present"])
        self.assertFalse(pins["asset:checkpoint"]["loaded"])
        self.assertFalse(pins["asset:runtime"]["present"])
        self.assertFalse(pins["asset:runtime"]["admitted"])

    def test_boundary_flags_false(self):
        self.assertTrue(all(value is False
                            for value in report()["boundary"].values()
                            if isinstance(value, bool)))

    def test_board_row_stable_identity(self):
        board = report()["board_row"]
        self.assertFalse(board["full_tasks_json_hashed"])
        self.assertEqual(reference.board_row_digest(),
                         reference.BOARD_ROW_STABLE_SHA256)


class ManifestTests(unittest.TestCase):
    def test_contract_local_files(self):
        self.assertEqual(reference.contract_payload()["local_files"],
                         sorted(reference.LOCAL_FILES))

    def test_expected_dir_files(self):
        self.assertEqual(reference.EXPECTED_DIR_FILES,
                         set(reference.LOCAL_FILES) | {"SOURCES.sha256"})

    def test_sources_manifest_covers_local_files(self):
        text = reference.sources_bytes().decode("ascii")
        rows = reference.parse_pin_lines(text)
        paths = {path for _, path in rows}
        for name in reference.LOCAL_FILES:
            self.assertIn(reference.TASK_PREFIX + name, paths)
        self.assertNotIn(reference.TASK_PREFIX + "SOURCES.sha256", paths)

    def test_pin_manifest_has_no_duplicates(self):
        rows = reference.parse_pin_lines(
            reference.sources_bytes().decode("ascii"))
        self.assertEqual(len(rows), len({path for _, path in rows}))

    def test_pin_parser_rejects_malformed(self):
        for text in ("not-a-pin", "0" * 63 + "  source:x",
                     "0" * 64 + "  other:x"):
            with self.assertRaises(ValueError):
                reference.parse_pin_lines(text)

    def test_readme_table_update_idempotent(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        once = reference.update_readme_artifact_table(text)
        twice = reference.update_readme_artifact_table(once)
        self.assertEqual(once, twice)

    def test_readme_tables_verify(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        text = reference.update_readme_artifact_table(text)
        counts = reference.verify_readme_digests(text)
        self.assertEqual(set(counts), set(reference.README_SECTIONS))

    def test_strict_rejection_examples(self):
        result = reference.strict_rejection_examples()
        self.assertEqual(result["bad_json_rejected"], result["bad_json_total"])
        self.assertEqual(result["bad_pins_rejected"], result["bad_pins_total"])
        self.assertEqual(result["bad_readme_rejected"],
                         result["bad_readme_total"])

    def test_source_pin_identity(self):
        for name, digest in reference.SOURCE_PINS.items():
            path = reference.resolve_source_path(name)
            self.assertTrue(path.is_file(), name)
            self.assertEqual(reference.sha256_file(path), digest, name)

    def test_boundary_pin_identity(self):
        for name, digest in reference.BOUNDARY_PINS.items():
            path = reference.SDK_ROOT / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(reference.sha256_file(path), digest, name)


if __name__ == "__main__":
    unittest.main()
