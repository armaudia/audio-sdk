# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest suite for the task-local synthetic room evidence."""

from __future__ import annotations

import json
import math
import pathlib
import unittest

import check_licensing
import crosscheck
import fixture
import reference
import run as cli
import scorer
import verify

TASK = pathlib.Path(__file__).resolve().parent
CONDITION = "overlap"


class FixtureTests(unittest.TestCase):
    def test_pins_are_exact(self):
        self.assertEqual(len(fixture.SOURCE_PINS), 7)
        for name, expected in fixture.SOURCE_PINS.items():
            self.assertEqual(fixture.sha256_file(fixture.resolve_pin_path(name)), expected)

    def test_board_snapshot_is_recorded(self):
        # The board is mutable provenance, never a gate.  Its digest at read
        # time stays frozen while the live file is allowed to advance.
        self.assertTrue(fixture.resolve_pin_path(fixture.MUTABLE_BOARD).is_file())
        self.assertEqual(len(fixture.MUTABLE_BOARD_SHA256_AT_READ), 64)
        report = reference.build_report()
        self.assertEqual(report["sources"]["mutable_board"]["sha256_at_read"],
                         fixture.MUTABLE_BOARD_SHA256_AT_READ)
        self.assertIs(report["sources"]["mutable_board"]["gate"], False)
        self.assertEqual(report["sources"]["mutable_board"]["path"],
                         fixture.MUTABLE_BOARD)
        self.assertEqual(
            json.load((TASK / "contract.json").open(encoding="utf-8"))["mutable_provenance"]["sha256_at_read"],
            fixture.MUTABLE_BOARD_SHA256_AT_READ)

    def test_stream_shape(self):
        for condition in fixture.CONDITIONS:
            data = fixture.build_stream(condition)
            self.assertEqual(len(data["microphone"]), fixture.TOTAL_SAMPLES)
            self.assertEqual(len(data["near"]), fixture.TOTAL_SAMPLES)
            self.assertEqual(len(data["render"]), fixture.TOTAL_SAMPLES)
            self.assertEqual(fixture.TOTAL_SAMPLES % fixture.FRAME_SAMPLES, 0)

    def test_all_fixture_samples_are_finite_and_bounded(self):
        for condition in fixture.CONDITIONS:
            data = fixture.build_stream(condition)
            for key in ("microphone", "near", "render", "capture_noise"):
                for value in data[key]:
                    self.assertTrue(math.isfinite(value))
                    self.assertLess(abs(value), fixture.f32(4.0))

    def test_fixture_is_byte_deterministic(self):
        first = fixture.build_stream(CONDITION)
        second = fixture.build_stream(CONDITION)
        for key in ("microphone", "reference", "near", "render"):
            self.assertEqual(first[key], second[key])
        self.assertEqual(fixture.FIXTURE_SPEC_DIGEST,
                         fixture.sha256_bytes(fixture.canonical_bytes(fixture.stream_spec())))

    def test_segment_table_has_no_gaps(self):
        for index in range(fixture.TOTAL_SAMPLES):
            self.assertIn("path", fixture.segment_for_sample(index))

    def test_path_change_is_frozen(self):
        self.assertEqual(fixture.path_for_sample(fixture.PATH_CHANGE_SAMPLE - 1), fixture.PATH_A)
        self.assertEqual(fixture.path_for_sample(fixture.PATH_CHANGE_SAMPLE), fixture.PATH_B)

    def test_delayed_render_never_uses_future(self):
        data = fixture.build_stream("delayed_render")
        self.assertEqual(data["reference"][:fixture.DELAYED_RENDER_SAMPLES],
                         tuple([0.0] * fixture.DELAYED_RENDER_SAMPLES))
        self.assertEqual(data["reference"][fixture.DELAYED_RENDER_SAMPLES],
                         data["render"][0])

    def test_shift_rejects_negative_delay(self):
        with self.assertRaises(ValueError):
            fixture.shift_signal((1.0, 2.0), -1)

    def test_stimuli_are_frozen(self):
        impulse = fixture.stimulus("impulse")
        self.assertEqual(impulse["microphone"][1600], 0.5)
        self.assertEqual(max(abs(value) for value in fixture.stimulus("silence")["microphone"]), 0.0)
        self.assertEqual(fixture.stimulus("step")["microphone"][1599], 0.0)

    def test_f32_rounding_is_stable(self):
        value = fixture.f32(0.1)
        self.assertEqual(value, fixture.f32(value))


class EngineTests(unittest.TestCase):
    def test_initial_state_is_zero(self):
        engine = reference.Aec3Lite()
        self.assertEqual(engine.weight_l1(), 0.0)
        self.assertEqual(engine.frames, 0)
        self.assertEqual(engine.last_ratio, 1.0)

    def test_frame_length_is_enforced(self):
        engine = reference.Aec3Lite()
        with self.assertRaises(ValueError):
            engine.process_frame((0.0,) * 8, (0.0,) * fixture.FRAME_SAMPLES)

    def test_reference_length_is_enforced(self):
        engine = reference.Aec3Lite()
        with self.assertRaises(ValueError):
            engine.process_frame((0.0,) * fixture.FRAME_SAMPLES, (0.0,) * 8)

    def test_nonfinite_microphone_rejected(self):
        engine = reference.Aec3Lite()
        mic = tuple([float("nan")] + [0.0] * (fixture.FRAME_SAMPLES - 1))
        with self.assertRaises(ValueError):
            engine.process_frame(mic, (0.0,) * fixture.FRAME_SAMPLES)

    def test_out_of_range_microphone_rejected(self):
        engine = reference.Aec3Lite()
        mic = tuple([9.0] + [0.0] * (fixture.FRAME_SAMPLES - 1))
        with self.assertRaises(ValueError):
            engine.process_frame(mic, (0.0,) * fixture.FRAME_SAMPLES)

    def test_nonfinite_reference_rejected(self):
        engine = reference.Aec3Lite()
        ref = tuple([float("inf")] + [0.0] * (fixture.FRAME_SAMPLES - 1))
        with self.assertRaises(ValueError):
            engine.process_frame((0.0,) * fixture.FRAME_SAMPLES, ref)

    def test_no_reference_is_exact_passthrough(self):
        data = fixture.build_stream(CONDITION)
        result = reference.run_stream(data, mode="no_reference_passthrough")
        self.assertEqual(result["output"], data["microphone"])
        self.assertEqual(result["adapted_frames"], 0)
        self.assertEqual(result["no_reference_frames"], fixture.TOTAL_FRAMES)

    def test_adaptation_reduces_echo(self):
        output = reference.run_stream(fixture.build_stream("echo_only"))["output"]
        before = scorer.energy(fixture.build_stream("echo_only")["microphone"], 3200, 6080)
        after = scorer.energy(output, 3200, 6080)
        self.assertGreater(scorer.db(before / after), 20.0)

    def test_near_only_case_has_no_adaptation(self):
        result = reference.run_stream(fixture.build_stream("near_only"))
        self.assertEqual(result["adapted_frames"], 0)
        self.assertEqual(result["failures"], 0)

    def test_overlap_case_adapts_and_fails_no_frames(self):
        result = reference.run_stream(fixture.build_stream(CONDITION))
        self.assertGreater(result["adapted_frames"], 100)
        self.assertEqual(result["failures"], 0)

    def test_adaptive_output_is_finite(self):
        for condition in fixture.CONDITIONS:
            result = reference.run_stream(fixture.build_stream(condition))
            self.assertEqual(result["failures"], 0)
            self.assertTrue(all(math.isfinite(value) for value in result["output"]))

    def test_reset_requires_newer_epoch(self):
        engine = reference.Aec3Lite()
        with self.assertRaises(ValueError):
            engine.reset(1, 0)
        with self.assertRaises(ValueError):
            engine.reset(2, -1)
        engine.reset(2, 16000)
        self.assertEqual(engine.epoch, 2)
        self.assertEqual(engine.reset_count, 1)

    def test_reset_clears_weights_and_history(self):
        engine = reference.Aec3Lite()
        data = fixture.build_stream(CONDITION)
        for index in range(20):
            engine.process_frame(
                tuple(data["microphone"][index * 160:(index + 1) * 160]),
                tuple(data["reference"][index * 160:(index + 1) * 160]))
        self.assertGreater(engine.weight_l1(), 0.0)
        engine.reset(2, 20 * 160)
        self.assertEqual(engine.weight_l1(), 0.0)
        self.assertEqual(engine.frames, 0)
        self.assertEqual(engine.history, [0.0] * reference.FILTER_TAPS)

    def test_forced_nonfinite_weight_is_safety_reset(self):
        engine = reference.Aec3Lite()
        data = fixture.build_stream(CONDITION)
        frame = tuple(data["microphone"][:160])
        ref = tuple(data["reference"][:160])
        engine.main[0] = float("nan")
        result = engine.process_frame(frame, ref)
        self.assertEqual(engine.safety_resets, 1)
        self.assertTrue(all(math.isfinite(value) for value in result["samples"]))

    def test_causality_first_nonzero_is_input_sample(self):
        causality = reference.causality_payload()
        self.assertEqual(causality["impulse_first_nonzero_sample"], 1600)
        self.assertEqual(causality["step_first_nonzero_sample"], 1600)
        self.assertEqual(causality["silence_peak_abs"], 0.0)
        self.assertFalse(causality["future_frame_reads"])

    def test_chunked_and_single_digest_identity(self):
        causality = reference.causality_payload()
        values = list(causality["chunk_identity"].values())
        self.assertEqual(len(set(values)), 1)

    def test_chunk_size_must_be_frame_aligned(self):
        with self.assertRaises(ValueError):
            reference.run_stream(fixture.build_stream(CONDITION), chunk_samples=17)

    def test_run_stream_rejects_unknown_mode(self):
        with self.assertRaises(ValueError):
            reference.run_stream(fixture.build_stream(CONDITION), mode="bogus")


class ScorerTests(unittest.TestCase):
    def test_erle_is_nonnegative_for_attenuation(self):
        data = fixture.build_stream("echo_only")
        output = reference.run_stream(data)["output"]
        self.assertGreater(scorer.erle(data["microphone"], output), 20.0)

    def test_erle_identity_is_zero_db(self):
        data = fixture.build_stream("echo_only")
        self.assertAlmostEqual(
            scorer.erle(data["microphone"], data["microphone"]), 0.0, places=6)

    def test_near_snr_uses_synthetic_ground_truth(self):
        data = fixture.build_stream("near_only")
        output = reference.run_stream(data)["output"]
        self.assertGreater(scorer.near_snr(data["near"], output, "near_only_early"), 20.0)

    def test_alignment_measures_fixture_lag(self):
        data = fixture.build_stream("echo_only")
        self.assertEqual(scorer.alignment_lag(data["render"], data["microphone"]), 18)

    def test_delayed_render_alignment_is_zero_on_fed_reference(self):
        data = fixture.build_stream("delayed_render")
        self.assertEqual(scorer.alignment_lag(data["reference"], data["microphone"]), 0)
        self.assertEqual(scorer.alignment_lag(data["render"], data["microphone"]), 18)

    def test_scorer_rejects_invalid_window(self):
        with self.assertRaises(ValueError):
            scorer.energy((0.0, 1.0), 0, 5)

    def test_digest_is_order_sensitive(self):
        self.assertNotEqual(scorer.digest((1.0, 2.0)), scorer.digest((2.0, 1.0)))

    def test_nonfinite_count(self):
        self.assertEqual(scorer.finite_count((1.0, float("nan"), 2.0)), 2)

    def test_db_floor(self):
        self.assertLess(scorer.db(0.0), -190.0)


class ReportAndCLITests(unittest.TestCase):
    def test_report_keys(self):
        self.assertEqual(set(reference.build_report()), reference.REPORT_KEYS)

    def test_report_is_canonical_and_byte_identical(self):
        first, digest = reference.canonical_report(reference.build_report())
        second, digest_two = reference.canonical_report(reference.build_report())
        self.assertEqual(first, second)
        self.assertEqual(digest, digest_two)
        self.assertEqual((TASK / "report.json").read_bytes(), first.encode("utf-8"))
        self.assertEqual((TASK / "report.json.sha256").read_text().strip(), digest)

    def test_room_profile_complete(self):
        profile = reference.build_report()["acceptance_profile"]
        self.assertEqual(profile["profile"], "room")
        for key, value in profile.items():
            if key != "profile":
                self.assertTrue(value, key)

    def test_all_runs_are_nonqualifying(self):
        report = reference.build_report()
        for name, run in report["runs"].items():
            self.assertFalse(run["qualifies"], name)
        for name, control in report["controls"].items():
            self.assertFalse(control["qualifies"], name)

    def test_adverse_statuses(self):
        report = reference.build_report()
        self.assertEqual(report["runs"]["no_reference"]["status"], "blocked_no_reference")
        self.assertEqual(report["runs"]["delayed_render"]["status"], "misaligned_reference")
        self.assertEqual(report["runs"]["reference_dropout"]["status"], "partial_reference")

    def test_no_reference_control_withholds(self):
        control = reference.build_report()["controls"]["no_reference_passthrough"]
        self.assertEqual(control["no_reference_frames"], fixture.TOTAL_FRAMES)

    def test_identity_and_fixed_controls(self):
        report = reference.build_report()
        self.assertAlmostEqual(report["controls"]["identity"]["metrics"]["erle_early_db"], 0.0, 2)
        self.assertAlmostEqual(report["controls"]["fixed_attenuation"]["metrics"]["erle_early_db"],
                               6.0206, 3)

    def test_failure_controls_recorded(self):
        failures = reference.build_report()["failures"]
        self.assertEqual(failures["rejected_count"], 5)
        self.assertEqual(failures["dropout_frames_withheld"], 20)
        self.assertEqual(failures["forced_nonfinite_weight_safety_resets"], 1)

    def test_crosscheck_payload_is_repeatable(self):
        first = reference.crosscheck_payload()
        second = reference.crosscheck_payload()
        self.assertEqual(first, second)
        self.assertEqual(len(first["output_sha256_per_frame"]), 4)

    def test_generated_header_is_byte_identical(self):
        existing = (TASK / "provider" / "crosscheck_vectors.h").read_text(encoding="ascii")
        self.assertEqual(crosscheck.generate(), existing)

    def test_sources_cli_is_deterministic(self):
        self.assertEqual(cli.sources_payload(), cli.sources_payload())
        self.assertEqual(cli.crosscheck_payload(), cli.crosscheck_payload())
        self.assertEqual(cli.inspect_payload()["decision"], "DEFER")

    def test_manifest_is_complete(self):
        manifest = cli.read_manifest()
        self.assertNotIn("SOURCES.sha256", manifest)
        for name, expected in manifest.items():
            self.assertEqual(fixture.sha256_file(TASK / name), expected)

    def test_strict_json_files(self):
        for name in ("contract.json", "adapter.json", "provider.json", "report.json"):
            verify.strict_json(TASK / name)

    def test_report_sidecar_matches_file(self):
        raw = (TASK / "report.json").read_bytes()
        self.assertEqual((TASK / "report.json.sha256").read_text().strip(),
                         fixture.sha256_bytes(raw))

    def test_license_check_is_green(self):
        self.assertEqual(check_licensing.check()["status"], "ok")

    def test_disposition_is_defer(self):
        report = reference.build_report()
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertEqual(report["qualification_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertFalse(report["public_surface_changed"])
        self.assertFalse(report["installed_v0_changed"])

    def test_no_literal_spdx_token_in_json_values(self):
        token = "SPDX" + "-License-Identifier:"
        for name in ("contract.json", "adapter.json", "provider.json", "report.json"):
            self.assertNotIn(token, (TASK / name).read_text(encoding="utf-8"))

    def test_signal_model_and_metric_definitions_are_explicit(self):
        spec = reference.build_report()["fixture_spec"]
        model = spec["signal_model"]
        for key in ("far_end", "near_end", "capture_noise", "microphone",
                    "echo_path", "double_talk", "reference_sidechain"):
            self.assertTrue(model[key], key)
        self.assertIn("microphone", model["microphone"])
        self.assertIn("never supplied", model["near_end"])
        for key in ("erle_proxy", "near_snr", "alignment", "matched_controls"):
            self.assertTrue(spec["metrics"][key], key)

    def test_real_runtime_gap_is_explicit_and_blocked(self):
        algorithm = reference.build_report()["algorithm"]
        self.assertIs(algorithm["real_webrtc_source_or_weights"], False)
        self.assertIs(algorithm["real_webrtc_runtime"], False)
        self.assertIs(algorithm["real_webrtc_model_or_weights"], False)
        self.assertIn("BLOCKED", algorithm["provenance_gap"])
        self.assertEqual(reference.build_report()["decision"], "DEFER")

    def test_reset_replay_is_byte_and_state_identical(self):
        replay = reference.build_report()["failures"]["reset_replay"]
        self.assertEqual(replay["frames"], 20)
        self.assertEqual(replay["start_sample"], 100 * fixture.FRAME_SAMPLES)
        self.assertTrue(replay["byte_identical"])
        self.assertTrue(replay["state_digest_identical"])
        self.assertEqual(replay["continued_output_sha256"],
                         replay["fresh_output_sha256"])
        self.assertEqual(replay["continued_state_digest"],
                         replay["fresh_state_digest"])
        self.assertEqual(replay["invalid_reset_rejections"],
                         ["stale_or_invalid_epoch", "invalid_first_sample"])

    def test_echo_proxy_beats_matched_controls(self):
        report = reference.build_report()
        adaptive = report["runs"]["echo_only"]["metrics"]["erle_early_db"]
        identity = report["controls"]["identity"]["metrics"]["erle_early_db"]
        fixed = report["controls"]["fixed_attenuation"]["metrics"]["erle_early_db"]
        self.assertGreater(adaptive, identity + 20.0)
        self.assertGreater(adaptive, fixed + 20.0)
        overlap = report["runs"]["overlap"]["metrics"]["near_snr_overlap_db"]
        self.assertGreater(overlap,
                           report["controls"]["identity"]["metrics"]["near_snr_overlap_db"])

    def test_alignment_records_direct_tap_and_composite_measure(self):
        failures = reference.build_report()["failures"]
        self.assertEqual(failures["alignment_direct_path_tap_samples"], 12)
        self.assertIsInstance(failures["alignment_early_measured_samples"], int)
        self.assertGreaterEqual(failures["alignment_early_measured_samples"], 0)
        self.assertIn("not a device", failures["alignment_measurement"])

    def test_verify_accepts_the_frozen_evidence_package(self):
        report = reference.build_report()
        verify.check_report(report)
        verify.check_contract(verify.strict_json(TASK / "contract.json"),
                              verify.strict_json(TASK / "adapter.json"),
                              verify.strict_json(TASK / "provider.json"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
