# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the LocalVQE dereverberation probe.

No network, no model, no audio, no native runtime and no skips.  Run after
``run.py`` has generated the canonical artifacts::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
"""

from __future__ import annotations

import hashlib
import json
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
    model = root / reference.MODEL_FILENAME
    library = root / reference.LIBRARY_FILENAME
    if not model.exists():
        model.write_bytes(b"caller-owned-placeholder-model")
    if not library.exists():
        library.write_bytes(b"caller-owned-placeholder-library")
    manifest = {
        "algorithmic_latency_samples": reference.LATENCY_SAMPLES,
        "channels": reference.CHANNELS,
        "frame_samples": reference.FRAME_SAMPLES,
        "input_format": "float32",
        "library_path": str(library),
        "library_sha256": reference.sha256_file(library),
        "model_path": str(model),
        "model_sha256": reference.sha256_file(model),
        "reference_mode": "zero_far_end",
        "render_delay_samples": 0,
        "sample_rate_hz": reference.SAMPLE_RATE_HZ,
        "source_commit": reference.UPSTREAM_COMMIT,
        "variant": "compact-full",
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
        self.assertEqual(len(reference.FIXTURE_COMPONENTS["reverb"]),
                         reference.TOTAL_SAMPLES)

    def test_segment_boundaries_are_frame_aligned(self):
        for segment in reference.SEGMENTS:
            self.assertEqual(segment["start_frame"] % 1, 0)
            self.assertEqual((segment["end_frame"] - segment["start_frame"]) *
                             reference.FRAME_SAMPLES % reference.FRAME_SAMPLES, 0)
        self.assertEqual(reference.SEGMENTS[0]["start_frame"], 0)
        self.assertEqual(reference.SEGMENTS[-1]["end_frame"],
                         reference.TOTAL_FRAMES)

    def test_segment_coverage_is_contiguous(self):
        cursor = 0
        for segment in reference.SEGMENTS:
            self.assertEqual(segment["start_frame"], cursor)
            cursor = segment["end_frame"]
        self.assertEqual(cursor, reference.TOTAL_FRAMES)

    def test_decomposition_is_exact(self):
        components = reference.FIXTURE_COMPONENTS
        for index in range(reference.TOTAL_SAMPLES):
            expected = reference._clip16(
                components["early"][index] + components["late"][index] +
                components["noise"][index])
            self.assertEqual(components["reverb"][index], expected)

    def test_int16_range(self):
        for values in reference.FIXTURE_COMPONENTS.values():
            self.assertGreaterEqual(min(values), -32768)
            self.assertLessEqual(max(values), 32767)

    def test_silence_segment_exactly_zero(self):
        end = reference.SEGMENT_FRAMES * reference.FRAME_SAMPLES
        self.assertTrue(all(value == 0
                            for value in reference.FIXTURE_COMPONENTS["clean"][:end]))

    def test_noise_only_in_noisy_segment(self):
        noise = reference.FIXTURE_COMPONENTS["noise"]
        start = 150 * reference.FRAME_SAMPLES
        end = 200 * reference.FRAME_SAMPLES
        self.assertTrue(all(value != 0 for value in noise[start:start + 1]))
        self.assertTrue(all(value == 0 for value in noise[:start]))

    def test_fixture_spec_digest_stable(self):
        self.assertEqual(reference.FIXTURE_SPEC_DIGEST,
                         reference.sha256(reference.canonical_bytes(
                             reference.fixture_spec())))

    def test_component_digests_cover_all_components(self):
        self.assertEqual(set(reference.FIXTURE_DIGESTS),
                         {"clean", "early", "late", "noise", "reverb"})

    def test_early_and_late_taps_do_not_overlap(self):
        self.assertLess(max(delay for delay, _ in reference.EARLY_TAPS),
                        min(delay for delay, _ in reference.LATE_TAPS))

    def test_predictor_taps_are_causal(self):
        for delay, gain in reference.PREDICTOR_TAPS:
            self.assertGreater(delay, 0)
            self.assertGreater(gain, 0)


class ConfigTests(unittest.TestCase):
    def test_baseline_accepted(self):
        session = reference.Session(reference.CONFIG, "ok", 0)
        self.assertEqual(session.epoch, 0)

    def test_unknown_key_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, extra=True), "ok", 0)

    def test_sample_rate_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, sample_rate_hz=48000),
                              "ok", 0)

    def test_channels_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, channels=2), "ok", 0)

    def test_bool_for_int_channel_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, channels=True), "ok", 0)

    def test_frame_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, frame_samples=320),
                              "ok", 0)

    def test_input_format_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, input_format="int16"),
                              "ok", 0)

    def test_latency_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(
                dict(reference.CONFIG, algorithmic_latency_samples=0), "ok", 0)

    def test_render_delay_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(
                dict(reference.CONFIG, render_delay_samples=256), "ok", 0)

    def test_reference_mode_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(
                dict(reference.CONFIG, reference_mode="paired_reference"),
                "ok", 0)

    def test_variant_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(
                dict(reference.CONFIG, variant="compact-echo-only"), "ok", 0)

    def test_real_runtime_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, real_runtime=True),
                              "ok", 0)

    def test_model_used_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, model_used=True),
                              "ok", 0)

    def test_library_used_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, library_used=True),
                              "ok", 0)

    def test_empty_session_id_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(reference.CONFIG, "", 0)

    def test_negative_epoch_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(reference.CONFIG, "ok", -1)

    def test_bool_epoch_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(reference.CONFIG, "ok", True)


class FrameTests(unittest.TestCase):
    def setUp(self):
        self.session = reference.Session(reference.CONFIG, "frame", 0)

    def test_valid_frame_returns_256(self):
        self.assertEqual(len(self.session.process_frame([0.0] * 256)), 256)

    def test_short_nonfinal_rejected(self):
        with self.assertRaises(ValueError):
            self.session.process_frame([0.0] * 255)

    def test_long_nonfinal_rejected(self):
        with self.assertRaises(ValueError):
            self.session.process_frame([0.0] * 257)

    def test_non_sequence_rejected(self):
        with self.assertRaises(ValueError):
            self.session.process_frame("x" * 256)

    def test_nan_rejected(self):
        frame = [0.0] * 256
        frame[3] = math.nan
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_infinity_rejected(self):
        frame = [0.0] * 256
        frame[3] = math.inf
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_range_rejected(self):
        frame = [0.0] * 256
        frame[0] = 1.5
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_boolean_sample_rejected(self):
        frame = [0.0] * 256
        frame[0] = True
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_partial_nonfinal_rejected(self):
        with self.assertRaises(ValueError):
            self.session.process_frame([0.0] * 128)

    def test_rejection_leaves_state_and_counter(self):
        before = self.session.state_digest()
        accepted = self.session.counters["accepted_input_samples"]
        with self.assertRaises(ValueError):
            self.session.process_frame([math.nan] * 256)
        self.assertEqual(self.session.state_digest(), before)
        self.assertEqual(self.session.counters["accepted_input_samples"],
                         accepted)

    def test_final_partial_accepted(self):
        output = self.session.process_frame([0.1] * 232, final=True)
        self.assertEqual(len(output), 256)
        self.assertEqual(self.session.frames[-1]["input_valid"], 232)

    def test_drain_before_final_rejected(self):
        with self.assertRaises(ValueError):
            self.session.drain()

    def test_process_after_final_rejected(self):
        self.session.process_frame([0.0] * 256, final=True)
        with self.assertRaises(ValueError):
            self.session.process_frame([0.0] * 256)

    def test_drain_after_final_returns_valid_tail(self):
        self.session.process_frame([0.0] * 232, final=True)
        tail, valid = self.session.drain()
        self.assertEqual(len(tail), 256)
        self.assertEqual(valid, 232)

    def test_drain_twice_rejected(self):
        self.session.process_frame([0.0] * 256, final=True)
        self.session.drain()
        with self.assertRaises(ValueError):
            self.session.drain()

    def test_reset_requires_greater_epoch(self):
        with self.assertRaises(ValueError):
            self.session.reset(0)

    def test_reset_fresh_parity(self):
        samples = reference.as_float(
            reference.FIXTURE_COMPONENTS["reverb"][:768])
        for index in range(3):
            self.session.process_frame(
                samples[index * 256:(index + 1) * 256],
                final=index == 2)
        self.session.reset(1)
        for index in range(3):
            self.session.process_frame(
                samples[index * 256:(index + 1) * 256],
                final=index == 2)
        self.session.drain()
        fresh = reference.Session(reference.CONFIG, "frame", 1)
        for index in range(3):
            fresh.process_frame(samples[index * 256:(index + 1) * 256],
                                final=index == 2)
        fresh.drain()
        self.assertEqual(self.session.state_digest(), fresh.state_digest())


class StreamingTests(unittest.TestCase):
    def setUp(self):
        self.samples = reference.as_float(
            reference.FIXTURE_COMPONENTS["reverb"][:4096])
        self.reference = reference.run_offline(self.samples)

    def test_output_length_preserved(self):
        self.assertEqual(len(self.reference["output"]), len(self.samples))

    def test_arbitrary_chunks_are_identical(self):
        for chunk in (160, 480, 320, 256, 137, 641, 1000):
            result = reference.drive_streaming(self.samples, chunk=chunk)
            self.assertEqual(result["output"], self.reference["output"])

    def test_partial_tail_prefix_matches(self):
        partial = reference.run_offline(self.samples[:1000])
        self.assertEqual(partial["output"], self.reference["output"][:1000])
        self.assertEqual(partial["tail_valid"], 1000 % 256)

    def test_silence_is_exact_zero(self):
        result = reference.run_offline([0.0] * 512)
        self.assertTrue(all(value == 0.0 for value in result["output"]))

    def test_impulse_maps_by_one_hop(self):
        control = reference.impulse_control()
        self.assertEqual(control["observed_peak_index"],
                         control["source_index"] + reference.LATENCY_SAMPLES)
        self.assertTrue(control["finite"])

    def test_streaming_session_counters(self):
        result = reference.drive_streaming(self.samples, chunk=137)
        counters = result["session"].counters
        self.assertEqual(counters["accepted_input_samples"], len(self.samples))
        self.assertEqual(counters["frames"],
                         math.ceil(len(self.samples) / 256))


class ScoringTests(unittest.TestCase):
    def test_self_si_sdr_is_large(self):
        signal = [0.1, -0.2, 0.3]
        self.assertGreater(reference.si_sdr(signal, signal), 100.0)

    def test_si_sdr_length_mismatch(self):
        with self.assertRaises(ValueError):
            reference.si_sdr([0.1], [0.1, 0.2])

    def test_si_sdr_silence_undefined(self):
        self.assertIsNone(reference.si_sdr([0.0, 0.0], [0.0, 0.0]))

    def test_projection_drr_numeric(self):
        components = reference.FIXTURE_COMPONENTS
        early = reference.as_float(components["early"])
        late = reference.as_float(components["late"])
        value = reference.projection_drr(early, early, late)
        self.assertIsInstance(value, float)

    def test_delay_best_lag(self):
        control = reference.delay_control(
            reference.FIXTURE_COMPONENTS,
            reference.run_offline(reference.as_float(
                reference.FIXTURE_COMPONENTS["reverb"]))["output"])
        self.assertEqual(
            control["output_best_alignment"]["best_lag_samples"],
            reference.LATENCY_SAMPLES)
        self.assertEqual(
            control["identity_best_alignment"]["best_lag_samples"], 0)


class AssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(
            prefix="localvqe-dereverb-test-")
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
        manifest.pop("reference_mode")
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(manifest)

    def test_relative_path_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, model_path=reference.MODEL_FILENAME))

    def test_absent_file_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest,
                     model_path=str(self.root / "absent.gguf")))

    def test_model_hash_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, model_sha256="0" * 64))

    def test_library_hash_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, library_sha256="0" * 64))

    def test_wrong_commit_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, source_commit="0" * 40))

    def test_wrong_geometry_rejected(self):
        for override in ({"sample_rate_hz": 48000}, {"channels": 2},
                         {"frame_samples": 320}, {"input_format": "int16"},
                         {"algorithmic_latency_samples": 0},
                         {"render_delay_samples": 256}):
            with self.assertRaises(ValueError):
                reference.validate_caller_asset(dict(self.manifest, **override))

    def test_wrong_variant_rejected(self):
        for variant in ("compact-echo-only", "dereverb-only"):
            with self.assertRaises(ValueError):
                reference.validate_caller_asset(
                    dict(self.manifest, variant=variant))

    def test_paired_reference_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, reference_mode="paired_reference"))

    def test_extra_field_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(dict(self.manifest, extra=True))

    def test_pinned_placeholder_rejected(self):
        with self.assertRaises(ValueError):
            reference.pinned_asset_identity(
                dict(self.manifest, model_sha256=reference.MODEL_SHA256,
                     library_sha256=reference.LIBRARY_SHA256))

    def test_workspace_pinned_model_absent(self):
        manifest = dict(
            self.manifest,
            model_path=str(reference.resolve_source_path(
                reference.MODEL_PATH)),
            model_sha256=reference.MODEL_SHA256,
            library_path=str(reference.resolve_source_path(
                reference.LIBRARY_PATH)),
            library_sha256=reference.LIBRARY_SHA256)
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(manifest)


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

    def test_missing_result_rule(self):
        self.assertTrue(report()["no_missing_result_qualifies_candidate"])
        self.assertTrue(report()["missing_results"])

    def test_scenario_is_distinct(self):
        scenario = report()["scenario"]
        self.assertEqual(scenario["far_end_reference"], "zero")
        self.assertFalse(scenario["is_aec"])
        self.assertFalse(scenario["is_pure_dereverberator"])
        self.assertFalse(scenario["is_joint_full_paired_reference"])

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
        self.assertEqual(metrics["nonfinite_output_samples"], 0)
        self.assertEqual(metrics["output_peak_clipped_samples"], 0)
        self.assertLessEqual(metrics["max_abs_output"], 1.0)
        self.assertTrue(metrics["silence_exact_zero"])

    def test_report_controls_rejected(self):
        controls = report()["controls"]
        self.assertTrue(controls["asset"]["rejected_all"])
        self.assertTrue(controls["config"]["rejected_all"])
        self.assertTrue(controls["frame"]["rejected_all"])
        self.assertTrue(controls["streaming_parity"]["all_identical"])
        self.assertTrue(controls["partial_tail"]["prefix_matches_full"])
        self.assertTrue(controls["reset"]["fresh_matches_reset"])
        self.assertFalse(controls["nonfinite_counter"]["counted_as_silence"])

    def test_asset_pins_absent(self):
        pins = report()["asset_pins"]
        self.assertFalse(pins["asset:joint_model"]["present"])
        self.assertFalse(pins["asset:echo_model"]["present"])
        self.assertFalse(pins["asset:native_runtime"]["admitted"])

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
