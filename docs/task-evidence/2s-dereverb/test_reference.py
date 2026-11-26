# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the 2S-Dereverb blocker package.

No network, no source import, no checkpoint, no runtime, no real audio and no
skips.  Run after ``run.py`` so the generated artifacts exist::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py
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
    source = root / "source.txt"
    stage1 = root / "stage1.ckpt"
    stage2 = root / "stage2.ckpt"
    runtime = root / "runtime.bin"
    for path, payload in (
            (source, b"caller-owned-placeholder-source"),
            (stage1, b"caller-owned-placeholder-stage1"),
            (stage2, b"caller-owned-placeholder-stage2"),
            (runtime, b"caller-owned-placeholder-runtime")):
        if not path.exists():
            path.write_bytes(payload)
    manifest = {
        "algorithmic_latency_samples": reference.LATENCY_SAMPLES,
        "channels": reference.CHANNELS,
        "frame_samples": reference.FRAME_SAMPLES,
        "input_format": "float32",
        "reference_channel": 0,
        "runtime_path": str(runtime),
        "runtime_sha256": reference.sha256_file(runtime),
        "sample_rate_hz": reference.SAMPLE_RATE_HZ,
        "source_commit": "a" * 40,
        "source_path": str(source),
        "stage1_checkpoint_path": str(stage1),
        "stage1_checkpoint_sha256": reference.sha256_file(stage1),
        "stage1_id": "stage1_multichannel_wpe",
        "stage2_channels": 1,
        "stage2_checkpoint_path": str(stage2),
        "stage2_checkpoint_sha256": reference.sha256_file(stage2),
        "stage2_id": "stage2_nonlinear_postfilter",
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
    def test_three_channels(self):
        self.assertEqual(len(reference.FIXTURE_COMPONENTS["reverb"]),
                         reference.CHANNELS)

    def test_total_samples_per_channel(self):
        for channel in reference.FIXTURE_COMPONENTS["reverb"]:
            self.assertEqual(len(channel), reference.TOTAL_SAMPLES)

    def test_segment_boundaries_are_frame_aligned(self):
        for segment in reference.SEGMENTS:
            self.assertEqual(
                (segment["end_frame"] - segment["start_frame"]) *
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

    def test_decomposition_is_exact_per_channel(self):
        components = reference.FIXTURE_COMPONENTS
        for channel in range(reference.CHANNELS):
            for index in range(reference.TOTAL_SAMPLES):
                expected = reference._clip16(
                    components["early"][channel][index] +
                    components["late"][channel][index] +
                    components["noise"][channel][index])
                self.assertEqual(components["reverb"][channel][index],
                                 expected)

    def test_int16_range_all_channels(self):
        for name in ("clean", "early", "late", "noise", "reverb"):
            value = reference.FIXTURE_COMPONENTS[name]
            channels = value if name != "clean" else [value]
            for channel in channels:
                self.assertGreaterEqual(min(channel), -32768)
                self.assertLessEqual(max(channel), 32767)

    def test_silence_segment_exactly_zero(self):
        end = reference.SEGMENT_FRAMES * reference.FRAME_SAMPLES
        for channel in reference.FIXTURE_COMPONENTS["reverb"]:
            self.assertTrue(all(value == 0 for value in channel[:end]))

    def test_noise_only_in_noisy_segment(self):
        noise = reference.FIXTURE_COMPONENTS["noise"][0]
        start = 150 * reference.FRAME_SAMPLES
        end = 200 * reference.FRAME_SAMPLES
        self.assertTrue(any(value != 0 for value in noise[start:end]))
        self.assertTrue(all(value == 0 for value in noise[:start]))

    def test_fixture_spec_digest_stable(self):
        self.assertEqual(reference.FIXTURE_SPEC_DIGEST,
                         reference.sha256(reference.canonical_bytes(
                             reference.fixture_spec())))

    def test_component_digests_cover_all_components(self):
        self.assertEqual(set(reference.FIXTURE_DIGESTS),
                         {"clean", "early", "late", "noise", "reverb"})

    def test_early_before_late_per_channel(self):
        for channel in range(reference.CHANNELS):
            self.assertLess(
                max(delay for delay, _ in
                    reference.EARLY_TAPS_BY_CHANNEL[channel]),
                min(delay for delay, _ in
                    reference.LATE_TAPS_BY_CHANNEL[channel]))
            self.assertLessEqual(
                reference.EARLY_WINDOW_SAMPLES,
                min(delay for delay, _ in
                    reference.LATE_TAPS_BY_CHANNEL[channel]))

    def test_predictor_taps_are_causal(self):
        for taps in reference.PREDICTOR_TAPS_BY_CHANNEL:
            for delay, gain in taps:
                self.assertGreater(delay, 0)
                self.assertGreater(gain, 0)

    def test_channels_differ(self):
        reverb = reference.FIXTURE_COMPONENTS["reverb"]
        self.assertNotEqual(reverb[0], reverb[1])
        self.assertNotEqual(reverb[1], reverb[2])


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

    def test_mono_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, channels=1), "ok", 0)

    def test_two_channels_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, channels=2), "ok", 0)

    def test_bool_for_channel_rejected(self):
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

    def test_negative_latency_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(
                dict(reference.CONFIG, algorithmic_latency_samples=-1), "ok", 0)

    def test_multichannel_flag_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, multichannel=False),
                              "ok", 0)

    def test_reference_channel_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, reference_channel=3),
                              "ok", 0)

    def test_stage1_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, stage1="mono_wpe"),
                              "ok", 0)

    def test_stage2_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, stage2="linear_filter"),
                              "ok", 0)

    def test_real_runtime_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, real_runtime=True),
                              "ok", 0)

    def test_model_used_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, model_used=True),
                              "ok", 0)

    def test_surrogate_false_rejected(self):
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG, surrogate=False), "ok", 0)

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
        self.good = [[0.0] * reference.FRAME_SAMPLES
                     for _ in range(reference.CHANNELS)]

    def test_valid_frame_returns_256(self):
        self.assertEqual(len(self.session.process_frame(self.good)),
                         reference.FRAME_SAMPLES)

    def test_mono_rejected(self):
        with self.assertRaises(ValueError):
            self.session.process_frame([self.good[0]])

    def test_two_channels_rejected(self):
        with self.assertRaises(ValueError):
            self.session.process_frame(self.good[:2])

    def test_four_channels_rejected(self):
        with self.assertRaises(ValueError):
            self.session.process_frame(self.good + [list(self.good[0])])

    def test_ragged_rejected(self):
        frame = [list(item) for item in self.good]
        frame[2] = frame[2][:-1]
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_short_nonfinal_rejected(self):
        frame = [[0.0] * (reference.FRAME_SAMPLES - 1)
                 for _ in range(reference.CHANNELS)]
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_long_nonfinal_rejected(self):
        frame = [[0.0] * (reference.FRAME_SAMPLES + 1)
                 for _ in range(reference.CHANNELS)]
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_string_outer_rejected(self):
        with self.assertRaises(ValueError):
            self.session.process_frame("x" * reference.FRAME_SAMPLES)

    def test_string_channel_rejected(self):
        frame = [list(item) for item in self.good]
        frame[1] = "x" * reference.FRAME_SAMPLES
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_nan_rejected(self):
        frame = [list(item) for item in self.good]
        frame[0][3] = math.nan
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_infinity_rejected(self):
        frame = [list(item) for item in self.good]
        frame[1][3] = math.inf
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_negative_infinity_rejected(self):
        frame = [list(item) for item in self.good]
        frame[2][3] = -math.inf
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_range_rejected(self):
        frame = [list(item) for item in self.good]
        frame[0][0] = 1.5
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_boolean_sample_rejected(self):
        frame = [list(item) for item in self.good]
        frame[1][0] = True
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_nested_sample_rejected(self):
        frame = [list(item) for item in self.good]
        frame[0][0] = [0.0]
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_none_sample_rejected(self):
        frame = [list(item) for item in self.good]
        frame[2][0] = None
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)

    def test_partial_nonfinal_rejected(self):
        with self.assertRaises(ValueError):
            self.session.process_frame(
                [[0.0] * 128 for _ in range(reference.CHANNELS)])

    def test_rejection_leaves_state_and_counter(self):
        before = self.session.state_digest()
        accepted = self.session.counters["accepted_input_samples"]
        frame = [list(item) for item in self.good]
        frame[1][9] = math.nan
        with self.assertRaises(ValueError):
            self.session.process_frame(frame)
        self.assertEqual(self.session.state_digest(), before)
        self.assertEqual(self.session.counters["accepted_input_samples"],
                         accepted)

    def test_final_partial_accepted(self):
        frame = [[0.1] * 232 for _ in range(reference.CHANNELS)]
        output = self.session.process_frame(frame, final=True)
        self.assertEqual(len(output), reference.FRAME_SAMPLES)
        self.assertEqual(self.session.frames[-1]["input_valid"], 232)

    def test_drain_before_final_rejected(self):
        with self.assertRaises(ValueError):
            self.session.drain()

    def test_process_after_final_rejected(self):
        self.session.process_frame(self.good, final=True)
        with self.assertRaises(ValueError):
            self.session.process_frame(self.good)

    def test_drain_after_final_returns_valid_tail(self):
        self.session.process_frame(
            [[0.0] * 232 for _ in range(reference.CHANNELS)], final=True)
        tail, valid = self.session.drain()
        self.assertEqual(len(tail), reference.FRAME_SAMPLES)
        self.assertEqual(valid, 232)

    def test_drain_twice_rejected(self):
        self.session.process_frame(self.good, final=True)
        self.session.drain()
        with self.assertRaises(ValueError):
            self.session.drain()

    def test_reset_requires_greater_epoch(self):
        with self.assertRaises(ValueError):
            self.session.reset(0)

    def test_reset_fresh_parity(self):
        samples = reference.as_float_channels(
            reference.FIXTURE_COMPONENTS["reverb"])
        window = [channel[:reference.FRAME_SAMPLES * 3]
                  for channel in samples]
        for index in range(3):
            self.session.process_frame(
                [channel[index * reference.FRAME_SAMPLES:
                         (index + 1) * reference.FRAME_SAMPLES]
                 for channel in window], final=index == 2)
        self.session.reset(1)
        for index in range(3):
            self.session.process_frame(
                [channel[index * reference.FRAME_SAMPLES:
                         (index + 1) * reference.FRAME_SAMPLES]
                 for channel in window], final=index == 2)
        self.session.drain()
        fresh = reference.Session(reference.CONFIG, "frame", 1)
        for index in range(3):
            fresh.process_frame(
                [channel[index * reference.FRAME_SAMPLES:
                         (index + 1) * reference.FRAME_SAMPLES]
                 for channel in window], final=index == 2)
        fresh.drain()
        self.assertEqual(self.session.state_digest(), fresh.state_digest())


class StreamingTests(unittest.TestCase):
    def setUp(self):
        self.samples = reference.as_float_channels(
            reference.FIXTURE_COMPONENTS["reverb"])
        self.reference = reference.run_offline(self.samples)

    def test_output_length_preserved(self):
        self.assertEqual(len(self.reference["output"]),
                         len(self.samples[0]))

    def test_arbitrary_chunks_are_identical(self):
        for chunk in (160, 480, 320, 256, 137, 641, 1000):
            result = reference.drive_streaming(self.samples, chunk=chunk)
            self.assertEqual(result["output"], self.reference["output"])

    def test_partial_tail_prefix_matches(self):
        partial = reference.run_offline(
            [channel[:1000] for channel in self.samples])
        self.assertEqual(partial["output"], self.reference["output"][:1000])
        self.assertEqual(partial["tail_valid"], 1000 % reference.FRAME_SAMPLES)

    def test_silence_is_exact_zero(self):
        result = reference.run_offline(
            [[0.0] * 512 for _ in range(reference.CHANNELS)])
        self.assertTrue(all(value == 0.0 for value in result["output"]))

    def test_impulse_maps_by_one_hop(self):
        control = reference.impulse_control()
        self.assertEqual(control["observed_peak_index"],
                         control["source_index"] + reference.LATENCY_SAMPLES)
        self.assertTrue(control["finite"])

    def test_impulse_reduced_by_nonlinear_stage(self):
        control = reference.impulse_control()
        self.assertTrue(control["nonlinear_peak_reduced"])
        self.assertLess(abs(control["peak_value"]), 0.5)

    def test_streaming_session_counters(self):
        result = reference.drive_streaming(self.samples, chunk=137)
        counters = result["session"].counters
        self.assertEqual(counters["accepted_input_samples"],
                         len(self.samples[0]))
        self.assertEqual(counters["frames"],
                         math.ceil(len(self.samples[0]) /
                                   reference.FRAME_SAMPLES))

    def test_other_channels_change_output(self):
        control = reference.multichannel_control()
        self.assertTrue(control["other_channels_change_output"])

    def test_mono_stream_rejected(self):
        with self.assertRaises(ValueError):
            reference.run_offline([[0.0] * 512])

    def test_ragged_stream_rejected(self):
        with self.assertRaises(ValueError):
            reference.run_offline([[0.0] * 512, [0.0] * 511, [0.0] * 512])


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="2s-dereverb-test-")
        cls.root = Path(cls.temp.name)
        cls.manifest = asset_manifest(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_generic_manifest_accepted_without_execution(self):
        result = reference.validate_caller_asset(self.manifest)
        self.assertTrue(result["accepted"])
        self.assertTrue(result["multichannel"])
        self.assertTrue(result["stage2_single_channel"])
        self.assertFalse(result["loaded"])
        self.assertFalse(result["executed"])
        self.assertFalse(result["imported"])
        self.assertFalse(result["pinned_asset"])

    def test_asset_controls_reject_all(self):
        self.assertTrue(reference._asset_controls()["rejected_all"])

    def test_pinned_identity_rejected(self):
        with self.assertRaises(ValueError):
            reference.pinned_asset_identity(self.manifest)

    def test_config_controls_reject_all(self):
        self.assertTrue(reference.config_adverse_control()["rejected_all"])

    def test_frame_controls_reject_all(self):
        self.assertTrue(reference.frame_adverse_control()["rejected_all"])

    def test_nonfinite_not_counted_as_silence(self):
        control = reference.nonfinite_counter_control()
        self.assertFalse(control["counted_as_silence"])
        self.assertTrue(control["accepted_counter_unchanged"])
        self.assertTrue(control["state_digest_unchanged"])

    def test_delay_control_matches(self):
        self.assertTrue(reference.delay_control(
            reference.impulse_control())["matches"])

    def test_reset_control_matches(self):
        control = reference.reset_control(reference.FIXTURE_COMPONENTS)
        self.assertTrue(control["fresh_matches_reset"])
        self.assertTrue(control["higher_epoch_accepted"])
        self.assertTrue(control["stale_digest_unchanged"])

    def test_partial_tail_control(self):
        control = reference.partial_tail_control(reference.FIXTURE_COMPONENTS)
        self.assertEqual(control["tail_valid"], 232)
        self.assertTrue(control["length_preserved"])
        self.assertTrue(control["prefix_matches_full"])

    def test_silence_control(self):
        control = reference.silence_control()
        self.assertTrue(control["exact_zero"])
        self.assertTrue(control["finite"])

    def test_multichannel_control(self):
        control = reference.multichannel_control()
        self.assertTrue(control["mono_rejected"])
        self.assertTrue(control["other_channels_change_output"])
        self.assertTrue(control["finite"])

    def test_streaming_parity_control(self):
        control = reference.streaming_parity_control(
            reference.FIXTURE_COMPONENTS)
        self.assertTrue(control["all_identical"])


class AssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="2s-dereverb-asset-")
        cls.root = Path(cls.temp.name)
        cls.manifest = asset_manifest(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_missing_field_rejected(self):
        manifest = dict(self.manifest)
        manifest.pop("stage2_id")
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(manifest)

    def test_relative_path_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, source_path="source.txt"))

    def test_absent_file_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, source_path=str(self.root / "absent")))

    def test_stage1_hash_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, stage1_checkpoint_sha256="0" * 64))

    def test_stage2_hash_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, stage2_checkpoint_sha256="0" * 64))

    def test_runtime_hash_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, runtime_sha256="0" * 64))

    def test_short_commit_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(
                dict(self.manifest, source_commit="0" * 39))

    def test_wrong_geometry_rejected(self):
        for override in (
                {"sample_rate_hz": 0},
                {"frame_samples": 0},
                {"algorithmic_latency_samples": -1},
                {"channels": 1},
                {"reference_channel": 3},
                {"input_format": "int16"},
                {"stage1_id": "mono_wpe"},
                {"stage2_id": "linear"},
                {"stage2_channels": 2}):
            with self.assertRaises(ValueError):
                reference.validate_caller_asset(
                    dict(self.manifest, **override))

    def test_bool_geometry_rejected(self):
        for override in ({"channels": True}, {"sample_rate_hz": True}):
            with self.assertRaises(ValueError):
                reference.validate_caller_asset(
                    dict(self.manifest, **override))

    def test_extra_field_rejected(self):
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(dict(self.manifest, extra=True))

    def test_pinned_placeholder_rejected(self):
        with self.assertRaises(ValueError):
            reference.pinned_asset_identity(self.manifest)

    def test_workspace_pinned_path_absent(self):
        manifest = dict(
            self.manifest,
            source_path=str(reference.resolve_source_path(
                reference.SOURCE_CHECKOUT_PATH)))
        with self.assertRaises(ValueError):
            reference.validate_caller_asset(manifest)


class ReportTests(unittest.TestCase):
    def test_disposition(self):
        self.assertEqual(report()["decision"], "DEFER")
        self.assertEqual(report()["evidence_status"], "incomplete")
        self.assertEqual(report()["qualification_status"], "not_qualified")
        self.assertEqual(report()["qualification"]["status"],
                         "not_qualified")
        self.assertEqual(report()["status"], reference.STATUS)

    def test_proposal_only(self):
        self.assertTrue(report()["proposal_only"])

    def test_eight_blocked_gates(self):
        gates = report()["gates"]
        self.assertEqual(len(gates), 8)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["qualifies"] is False for gate in gates))

    def test_missing_result_rule(self):
        self.assertTrue(report()["no_missing_result_qualifies_candidate"])
        self.assertTrue(report()["missing_results"])

    def test_scenario_is_multichannel_room(self):
        scenario = report()["scenario"]
        self.assertFalse(scenario["is_aec"])
        self.assertFalse(scenario["is_mono_baseline"])
        self.assertFalse(scenario["upstream_geometry_verified"])
        self.assertEqual(scenario["channels_required"], ">=2")

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
        self.assertFalse(metrics["candidate_result"])
        self.assertTrue(metrics["surrogate_only"])
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
        for key in pins:
            self.assertFalse(pins[key]["present"])
            self.assertFalse(pins[key]["loaded"])
            self.assertFalse(pins[key]["executed"])

    def test_upstream_identity_not_fabricated(self):
        upstream = report()["upstream"]
        self.assertIsNone(upstream["commit"])
        self.assertIsNone(upstream["license"])
        self.assertIsNone(upstream["checkpoint_identity"])
        self.assertFalse(upstream["source_present"])

    def test_boundary_flags_false(self):
        self.assertTrue(all(value is False
                            for value in report()["boundary"].values()
                            if isinstance(value, bool)))

    def test_scope_flags_false(self):
        scope = report()["scope"]
        self.assertTrue(scope["task_local_only"])
        flags = [value for name, value in scope.items()
                 if isinstance(value, bool) and name != "task_local_only"]
        self.assertTrue(all(value is False for value in flags))

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
