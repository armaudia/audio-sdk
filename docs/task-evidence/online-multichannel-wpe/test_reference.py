# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local online multichannel WPE reference.

Run from this directory with
``PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py``.
No external packages, downloads, WAV files, model weights, SDK runtime or Bench
artifacts are needed. The full report rebuild is the only slow test; every
other check uses the frozen committed evidence and short deterministic probes.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import fixture
import reference
import run as adapter
import scorer

TASK_DIR = Path(__file__).resolve().parent
WORKTREE = fixture.SDK_ROOT
AUDIO_ROOT = fixture.SOURCE_ROOT
REPORT_FILE = fixture.REPORT_FILE
SIDECAR_FILE = fixture.SIDECAR_FILE
PINS_FILE = fixture.PINS_FILE
CROSSCHECK_FILE = fixture.CROSSCHECK_FILE
REPORT_SHA256 = "df76b6e78ab86bc21609d3a93d53bc175b9281962396cc3bf1acf8ea2d994e6f"
SIDECAR_SHA256 = "527844b13d2475539f95fbb4517880e4aa2ccfa8232610ee087c8bac7b28735e"
SOURCES_SHA256 = "981ca427d3177d8a08a395ecbfd33955daabafaec1ee12ba7c92441f46319dae"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request(operation: str, control: str = "online_mc_wpe", *, stimulus: str = "short_rt60",
            samples=None, attempt: str = "attempt-1", enabled: bool = True):
    common = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": {"kind": "reference", "id": "online-multichannel-wpe", "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": adapter.IDENTITY, "revision": 1},
        "configuration": {"control": control, "provider_enabled": enabled},
    }
    if operation == "inspect":
        return common
    common.update({"attempt_id": attempt, "stimulus_id": stimulus, "samples": samples})
    return common


def stereo_probe(frames: int = 6):
    pair = reference.causal_probe_pair()
    return [list(pair[0][:frames * reference.FRAME_SAMPLES]),
            list(pair[1][:frames * reference.FRAME_SAMPLES])]


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT_FILE.read_text(encoding="utf-8"))
        cls.sidecar = SIDECAR_FILE.read_text(encoding="ascii").strip()

    def test_committed_report_is_canonical_and_digest_matches(self):
        text, digest = reference.canonical_report(self.report)
        self.assertEqual(REPORT_FILE.read_bytes(), text.encode("utf-8") + b"\n")
        self.assertEqual(self.sidecar, digest)
        self.assertEqual(sha256_file(REPORT_FILE), REPORT_SHA256)
        self.assertEqual(sha256_file(SIDECAR_FILE), SIDECAR_SHA256)

    def test_report_regeneration_is_byte_identical(self):
        text, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(text.encode("utf-8") + b"\n", REPORT_FILE.read_bytes())
        self.assertEqual(digest, self.sidecar)

    def test_sources_file_is_deterministic(self):
        self.assertEqual(PINS_FILE.read_bytes(), reference.sources_bytes())
        self.assertEqual(sha256_file(PINS_FILE), SOURCES_SHA256)

    def test_pinned_sources_boundaries_and_artifacts_are_unchanged(self):
        for relative, expected in reference.SOURCE_PINS.items():
            path = AUDIO_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(sha256_file(path), expected, relative)
        for relative, expected in reference.BOUNDARY_PINS.items():
            path = WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(sha256_file(path), expected, relative)
        for relative, expected in reference.ARTIFACT_PINS.items():
            path = WORKTREE / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(sha256_file(path), expected, relative)

    def test_fixture_digests_are_reproducible(self):
        digests = fixture.frozen_digests()
        self.assertEqual(digests["clean_source"],
                         self.report["conditions"]["short_rt60"]["source_digest"])
        for name, condition in self.report["conditions"].items():
            spec = reference.ROOM_SPECS[name]
            first, second = reference.synthetic_rir_pair(spec)
            self.assertEqual(digests[name + "_rir_mic0"], condition["rir_mic0_digest"])
            self.assertEqual(digests[name + "_rir_mic1"], condition["rir_mic1_digest"])
            self.assertEqual(reference.tensor_digest(first), condition["rir_mic0_digest"])
            self.assertEqual(reference.tensor_digest(second), condition["rir_mic1_digest"])
            self.assertEqual(condition["rir_samples"], len(first))

    def test_all_condition_variants_are_scored(self):
        expected = {"identity_control", "online_mc_wpe_candidate",
                    "noisy_identity_control", "online_mc_wpe_on_noisy"}
        for name, condition in self.report["conditions"].items():
            variants = condition["variants"]
            self.assertEqual(set(variants), expected, name)
            for label, row in variants.items():
                self.assertEqual(row["status"], "scored", name + "/" + label)
                self.assertFalse(row["excluded_from_qualification"])
                self.assertIsNotNone(row["metrics"])
            for label in ("identity_control", "noisy_identity_control"):
                metrics = variants[label]["metrics"]
                self.assertEqual(metrics["delta_si_sdr_db"], 0.0)
                self.assertEqual(metrics["delta_stoi"], 0.0)
            self.assertEqual(len({row["output_digest"] for row in variants.values()}), 4)

    def test_echo_only_variants_and_late_tail_proxy_are_present(self):
        for name, condition in self.report["conditions"].items():
            echo = condition["echo_only"]
            self.assertEqual({row["status"] for row in echo["variants"].values()}, {"scored"})
            self.assertEqual(echo["late_tail_proxy"]["status"], "ok", name)
            self.assertIn("not a measured echo attenuation", echo["late_tail_proxy"]["label"])
            self.assertIsNotNone(echo["late_tail_proxy"]["late_energy_reduction_db"])

    def test_identity_controls_are_bit_exact(self):
        for condition in self.report["conditions"].values():
            variants = condition["variants"]
            self.assertTrue(condition["identity_is_bit_exact"])
            self.assertEqual(variants["identity_control"]["output_digest"],
                             condition["identity_input_digest"])
            self.assertEqual(variants["noisy_identity_control"]["output_digest"],
                             condition["noisy_input_digest"])
            self.assertNotEqual(variants["online_mc_wpe_candidate"]["output_digest"],
                                condition["identity_input_digest"])
            self.assertNotEqual(variants["online_mc_wpe_on_noisy"]["output_digest"],
                                condition["noisy_input_digest"])

    def test_candidate_is_not_presented_as_universal_improvement(self):
        si_deltas = [condition["variants"]["online_mc_wpe_candidate"]["metrics"][
            "delta_si_sdr_db"] for condition in self.report["conditions"].values()]
        stoi_deltas = [condition["variants"]["online_mc_wpe_candidate"]["metrics"][
            "delta_stoi"] for condition in self.report["conditions"].values()]
        self.assertEqual(len(si_deltas), 3)
        self.assertTrue(all(delta < 0.0 for delta in si_deltas), si_deltas)
        self.assertTrue(any(delta > 0.0 for delta in stoi_deltas))
        self.assertTrue(any(delta < 0.0 for delta in stoi_deltas))
        self.assertEqual(
            {condition["rt60_ms"] for condition in self.report["conditions"].values()},
            {250, 550, 900})

    def test_unaligned_scores_are_recorded_separately(self):
        for condition in self.report["conditions"].values():
            for label in ("online_mc_wpe_candidate", "online_mc_wpe_on_noisy"):
                aligned = condition["variants"][label]["metrics"]
                unaligned = condition["variants"][label]["unaligned"]
                self.assertEqual(aligned["alignment_delay_samples"], 480)
                self.assertEqual(unaligned["alignment_delay_samples"], 0)
                self.assertNotEqual(aligned["si_sdr_db"], unaligned["si_sdr_db"])

    def test_spectral_tilt_is_present_for_every_condition(self):
        for name, condition in self.report["conditions"].items():
            tilt = condition["spectral_tilt"]
            self.assertEqual(set(tilt),
                             {"early_target", "identity_control", "online_mc_wpe_candidate"}, name)
            for label, row in tilt.items():
                self.assertEqual(row["status"], "ok", name + "/" + label)
                self.assertLess(row["mid_over_low_db"], 0.0)
                self.assertLess(row["high_over_low_db"], 0.0)
            self.assertIn("mid_minus_target_db", tilt["identity_control"])
            self.assertIn("high_minus_target_db", tilt["online_mc_wpe_candidate"])

    def test_special_conditions_are_scored(self):
        for name, special in self.report["special_conditions"].items():
            for label, row in special["variants"].items():
                self.assertIn(row["status"], ("scored", "control_exact"), name + "/" + label)
                self.assertIsNotNone(row["metrics"])
        self.assertEqual(set(self.report["special_conditions"]),
                         {"movement_long", "overlap_long", "near_end_only"})

    def test_near_end_damage_is_explicit(self):
        near = self.report["special_conditions"]["near_end_only"]["near_end_damage"]
        self.assertTrue(near["identity_is_bit_exact"])
        self.assertIsNone(near["delta_si_sdr_db"])
        self.assertIsNotNone(near["delta_stoi"])
        self.assertIn("identity_si_sdr_undefined", near["delta_reason"])
        self.assertIsNotNone(near["candidate_si_sdr_db"])

    def test_clean_near_end_preservation_is_explicit(self):
        preservation = self.report["clean_near_end_preservation"]
        self.assertEqual(set(preservation), {"identity_control", "online_mc_wpe_candidate"})
        identity = preservation["identity_control"]
        self.assertEqual(identity["status"], "control_exact")
        self.assertTrue(identity["identity_is_bit_exact"])
        self.assertTrue(identity["excluded_from_qualification"])
        candidate = preservation["online_mc_wpe_candidate"]
        self.assertEqual(candidate["status"], "scored")
        self.assertFalse(candidate["identity_is_bit_exact"])
        self.assertFalse(candidate["excluded_from_qualification"])

    def test_peaks_nonfinite_and_clipping_are_bounded(self):
        rows = []
        for condition in self.report["conditions"].values():
            rows.extend(condition["variants"].values())
            rows.extend(condition["echo_only"]["variants"].values())
        for special in self.report["special_conditions"].values():
            rows.extend(special["variants"].values())
        rows.extend(self.report["clean_near_end_preservation"].values())
        for row in rows:
            self.assertLessEqual(row["peak_abs"], 1.0)
            self.assertEqual(row["nonfinite_count"], 0)
            self.assertEqual(row["clipping_count"], 0)
            self.assertEqual(len(row["output_digest"]), 64)

    def test_alignment_delay_and_flush_policy_are_explicit(self):
        fmt = self.report["format"]
        self.assertEqual(fmt["content_delay_samples"], 480)
        self.assertEqual(fmt["content_delay_ms"], 30.0)
        self.assertEqual(fmt["flush_frames"], 3)
        self.assertEqual(fmt["predictor_history_ms_min"], 80.0)
        self.assertEqual(fmt["predictor_history_ms_max"], 100.0)
        self.assertEqual(fmt["processing_mode"], "causal_frame_streaming")
        self.assertIn("three final zero frames", fmt["note"])
        align = self.report["alignment_and_state"]
        self.assertEqual(align["impulse"]["status"], "ok")
        self.assertEqual(align["impulse"]["peak_index"], 480)
        self.assertEqual(align["impulse"]["content_delay_samples"], 480)
        self.assertEqual(align["silence"]["status"], "ok")
        self.assertEqual(align["silence"]["peak_abs"], 0.0)

    def test_channel1_influence_is_real(self):
        influence = self.report["alignment_and_state"]["channel1_influence"]
        self.assertTrue(influence["channel1_changes_output"])
        self.assertNotEqual(influence["output_with_silent_channel1"],
                            influence["output_with_active_channel1"])
        self.assertEqual(len(influence["channel0_digest"]), 64)
        c1_only = self.report["alignment_and_state"]["channel1_only_impulse"]
        self.assertIn("non-injecting behavior", c1_only["note"])

    def test_chunking_and_partial_frame_keep_exact_bytes(self):
        align = self.report["alignment_and_state"]
        self.assertTrue(align["duration"]["equal"])
        self.assertTrue(align["chunking_equivalence"]["equal"])
        self.assertEqual(align["chunking_equivalence"]["stream_digest"],
                         align["chunking_equivalence"]["chunked_digest"])
        partial = align["partial_final_frame"]
        self.assertTrue(partial["equal_duration"])
        self.assertEqual(partial["output_samples"], partial["input_samples"])
        self.assertEqual(partial["chunk_sizes"][-1], 37)

    def test_reset_session_and_causality_controls(self):
        align = self.report["alignment_and_state"]
        self.assertTrue(align["session_independence"]["independent"])
        self.assertEqual(align["reset"]["status"], "ok")
        self.assertTrue(align["reset"]["replay_matches_original"])
        self.assertEqual(align["reset"]["stale_epoch_status"], "rejected_epoch")
        self.assertEqual(align["reset"]["stale_position_status"], "rejected_position")
        causality = align["causality_probe"]
        self.assertTrue(causality["prefix_byte_identical"])
        self.assertTrue(causality["future_frame_differs"])
        self.assertEqual(causality["emitted_frames_compared_before_divergence"], 8)
        self.assertEqual(causality["divergent_input_frame_index"], 8)
        self.assertIsNotNone(causality["first_divergent_later_frame"])
        self.assertEqual(causality["divergent_channel"], 1)

    def test_adverse_controls_fail_closed(self):
        frame = self.report["adverse"]["frame_rejections"]
        self.assertEqual(frame["nonfinite_channel0"], "rejected_nonfinite")
        self.assertEqual(frame["nonfinite_channel1"], "rejected_nonfinite")
        self.assertEqual(frame["missing_channel"], "rejected_missing_channel")
        self.assertEqual(frame["delayed_channel"], "rejected_delayed_channel")
        self.assertEqual(frame["stale_session"], "rejected_session")
        self.assertEqual(frame["wrong_shape"], "rejected_tensor")
        self.assertEqual(frame["out_of_range"], "rejected_invalid")
        self.assertEqual(frame["stale_epoch"], "rejected_epoch")
        self.assertEqual(frame["stale_position"], "rejected_position")
        self.assertTrue(frame["dsp_state_unchanged"])
        self.assertEqual(frame["invalid_count_delta"], 9)
        self.assertEqual(frame["finished_reuse"], "rejected_session")
        self.assertEqual(frame["process_after_finish"], "rejected_session")
        for row in self.report["adverse"]["config_rejections"].values():
            self.assertNotEqual(row["status"], "ok")
            self.assertFalse(row["controller_created"])

    def test_no_reference_is_blocked_not_qualified(self):
        missing = self.report["adverse"]["missing_reference"]
        self.assertEqual(missing["status"], "blocked")
        self.assertEqual(missing["reason"], "missing_reference")
        self.assertIsNone(missing["metrics"])
        self.assertTrue(missing["excluded_from_qualification"])
        self.assertTrue(self.report["qualification"]["all_required_results_present"])
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")

    def test_room_profile_structure_is_applied(self):
        profile = self.report["room_profile"]
        self.assertEqual(profile["profile"], "room")
        self.assertEqual(set(profile["mapped_cases"]),
                         {"echo_only", "near_end_only", "overlap", "no_reference"})
        self.assertIn("delayed_or_missing_render", profile["not_applicable"])
        self.assertEqual(profile["frozen"]["rate_hz"], 16000)
        self.assertEqual(profile["frozen"]["input_channels"], 2)
        self.assertEqual(profile["frozen"]["output_channels"], 1)
        self.assertEqual(profile["frozen"]["frame_samples"], 160)
        self.assertEqual(profile["frozen"]["content_delay_samples"], 480)
        self.assertIn("reset_schedule", profile["frozen"])
        for label in ("alignment", "echo_attenuation_proxy", "near_end_damage",
                      "nonfinite_failures", "reset_behavior", "delayed_missing_channel"):
            self.assertIn(label, profile["reported"])

    def test_three_byte_identical_repeats_are_pinned(self):
        repeats = self.report["repeatability"]
        self.assertEqual(repeats["runs"], 3)
        self.assertTrue(repeats["byte_identical"])
        self.assertEqual(len(set(repeats["output_digests"])), 1)
        observed = fixture.repeat_probe()
        self.assertEqual(observed["input_digests"], repeats["input_digests"])
        self.assertEqual(observed["output_digests"], repeats["output_digests"])

    def test_scorer_crosscheck_vectors_are_inherited_not_online_oracle(self):
        vectors = json.loads(CROSSCHECK_FILE.read_text(encoding="utf-8"))
        section = self.report["scorer"]
        self.assertEqual(sha256_file(CROSSCHECK_FILE),
                         reference.ARTIFACT_PINS[
                             "docs/task-evidence/offline-mono-wpe/crosscheck_vectors.json"])
        self.assertEqual(section["crosscheck_vectors_file_sha256"], sha256_file(CROSSCHECK_FILE))
        self.assertEqual(section["crosscheck_vectors_digest"], reference.object_digest(vectors))
        self.assertEqual(section["crosscheck_vectors"], vectors)
        self.assertLess(section["pystoi_crosscheck_max_abs_delta"], 1e-12)
        self.assertLess(section["si_sdr_numpy_crosscheck_max_abs_delta"], 1e-12)
        self.assertTrue(all("online" not in vector["name"] for vector in vectors))
        self.assertIn("not multichannel online candidate results",
                      section["crosscheck_vectors_origin"])
        self.assertEqual(section["scorer_id"], scorer.SCORER_ID)

    def test_offline_control_is_not_an_online_oracle(self):
        control = self.report["noncausal_upper_bound_control"]
        self.assertFalse(control["usable_for_realtime_qualification"])
        self.assertFalse(control["used_as_candidate_oracle"])
        self.assertEqual(control["source_sha256"], reference.ARTIFACT_PINS[
            "docs/task-evidence/offline-mono-wpe/report.json"])
        self.assertEqual(len(self.report["causal_vs_noncausal_comparison"]), 3)
        for name, row in self.report["causal_vs_noncausal_comparison"].items():
            self.assertIn("not a like-for-like realtime result", row["note"])
            self.assertIn(name, control["conditions"])

    def test_provider_stays_opt_in_unregistered_and_disabled(self):
        provider = self.report["provider"]
        self.assertFalse(provider["default_enabled"])
        self.assertTrue(provider["opt_in_required"])
        self.assertFalse(provider["registered"])
        self.assertFalse(provider["c_abi_or_sdk_default_change"])
        self.assertFalse(provider["c_boundary_included"])
        self.assertEqual(provider["descriptor_settings"], {})
        probe = provider["off_on_probe"]
        self.assertTrue(probe["off_is_bit_exact_mic0_passthrough"])
        self.assertTrue(probe["on_differs_from_off"])
        self.assertFalse(self.report["format"]["realtime_v0_provider"])
        self.assertIn("no real room", self.report["scope"])
        self.assertIn("no release qualification", self.report["scope"])

    def test_status_and_defer_are_explicit(self):
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["defer_before"], "processor_exposure")
        self.assertTrue(self.report["qualification"]["no_missing_result_may_qualify"])
        self.assertEqual(self.report["qualification"]["decision"], "DEFER")


class ScorerTests(unittest.TestCase):
    def test_si_sdr_degenerate_cases_have_explicit_reasons(self):
        self.assertEqual(scorer.si_sdr([0.0, 0.0], [1.0, 2.0]),
                         (None, "zero_reference_energy"))
        signal = [0.1, -0.2, 0.3]
        self.assertEqual(scorer.si_sdr(signal, signal),
                         (None, "perfect_reconstruction"))
        self.assertEqual(scorer.si_sdr([1.0, 2.0], [1.0]),
                         (None, "invalid_input"))
        self.assertEqual(scorer.si_sdr([1.0, 2.0], [1.0, math.nan]),
                         (None, "invalid_input"))

    def test_stoi_identity_and_invalid_rates(self):
        short = reference.synthetic_speech(frames=50)
        value, reason = scorer.stoi(short, short)
        self.assertIsNone(reason)
        self.assertAlmostEqual(value, 1.0, places=12)
        self.assertEqual(scorer.stoi(short, short, rate=8000),
                         (None, "unsupported_rate"))
        self.assertEqual(scorer.stoi([0.0] * len(short), short),
                         (None, "insufficient_active_speech"))

    def test_scorer_identity_differs_from_prior_artifact(self):
        self.assertEqual(scorer.SCORER_ID, "audio-sdk/online-multichannel-wpe-scoring/0.1")
        self.assertNotEqual(scorer.SCORER_ID, "audio-sdk/offline-mono-wpe-scoring/0.1")


class ControllerTests(unittest.TestCase):
    def test_config_validation_matrix(self):
        cases = [
            (None, reference.Status.REJECTED_MISSING),
            ({key: value for key, value in reference.DEFAULT_CONFIG.items()
              if key != "taps"}, reference.Status.REJECTED_MISSING),
            (reference.config_with(unknown=1), reference.Status.REJECTED_INVALID),
            (reference.config_with(forgetting=float("inf")), reference.Status.REJECTED_NONFINITE),
            (reference.config_with(wpe_delay_frames="8"), reference.Status.REJECTED_INVALID),
            (reference.config_with(taps=0), reference.Status.REJECTED_INVALID),
            (reference.config_with(input_channels=1), reference.Status.REJECTED_INVALID),
            (reference.config_with(fft_size=512, hop_size=512), reference.Status.REJECTED_INVALID),
            (reference.config_with(prediction_energy_cap=2.0), reference.Status.REJECTED_INVALID),
        ]
        for config, expected in cases:
            with self.subTest(config=config):
                status, controller = reference.OnlineController.create(config)
                self.assertEqual(status, expected)
                self.assertIsNone(controller)

    def test_none_config_is_rejected_and_default_constructor_works(self):
        status, controller = reference.OnlineController.create(None)
        self.assertEqual(status, reference.Status.REJECTED_MISSING)
        self.assertIsNone(controller)
        default_controller = reference.OnlineController()
        self.assertEqual(default_controller.config["input_channels"], 2)

    def test_frame_shape_and_channel_state_rejections(self):
        controller = reference.OnlineController()
        good = ((0.01,) * reference.FRAME_SAMPLES,) * 2
        self.assertEqual(controller.process(good).status, reference.Status.OK)
        before = controller.dsp_digest()
        results = [
            controller.process((good[0], None)),
            controller.process(good, channel_positions=(0, reference.FRAME_SAMPLES)),
            controller.process((good[0], (0.0,) * (reference.FRAME_SAMPLES + 1))),
        ]
        self.assertEqual([row.status for row in results], [
            reference.Status.REJECTED_MISSING_CHANNEL,
            reference.Status.REJECTED_DELAYED_CHANNEL,
            reference.Status.REJECTED_TENSOR])
        self.assertEqual(controller.dsp_digest(), before)
        self.assertEqual(controller.state.invalid_count, 3)

    def test_nonfinite_in_either_channel_is_rejected(self):
        controller = reference.OnlineController()
        good = (0.01,) * reference.FRAME_SAMPLES
        first = controller.process(((math.nan,) * reference.FRAME_SAMPLES, good))
        second = controller.process((good, (float("inf"),) * reference.FRAME_SAMPLES))
        self.assertEqual(first.status, reference.Status.REJECTED_NONFINITE)
        self.assertEqual(second.status, reference.Status.REJECTED_NONFINITE)
        self.assertEqual(controller.state.invalid_count, 2)

    def test_out_of_range_is_rejected_without_state_change(self):
        controller = reference.OnlineController()
        controller.process(((0.01,) * reference.FRAME_SAMPLES,) * 2)
        before = controller.dsp_digest()
        result = controller.process(((9.0,) * reference.FRAME_SAMPLES,
                                     (0.01,) * reference.FRAME_SAMPLES))
        self.assertEqual(result.status, reference.Status.REJECTED_INVALID)
        self.assertEqual(controller.dsp_digest(), before)

    def test_stale_session_epoch_and_position_are_rejected(self):
        controller = reference.OnlineController()
        good = ((0.01,) * reference.FRAME_SAMPLES,) * 2
        self.assertEqual(controller.process(good, session=2).status,
                         reference.Status.REJECTED_SESSION)
        self.assertEqual(controller.process(good, epoch=99).status,
                         reference.Status.REJECTED_EPOCH)
        self.assertEqual(controller.process(good, first_input_sample=123456).status,
                         reference.Status.REJECTED_POSITION)

    def test_close_and_finish_reuse_are_rejected(self):
        controller = reference.OnlineController()
        controller.close()
        self.assertEqual(controller.process(
            ((0.01,) * reference.FRAME_SAMPLES,) * 2).status, reference.Status.CLOSED)
        fresh = reference.OnlineController()
        self.assertEqual(fresh.finish().status, reference.Status.OK)
        self.assertEqual(fresh.finish().status, reference.Status.REJECTED_SESSION)

    def test_content_delay_and_partial_final_frame(self):
        status, output = reference.process_whole_clip(reference.impulse_pair())
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(reference.impulse_peak_index(output), 480)
        status, silence = reference.process_whole_clip(reference.silence_pair())
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(max(abs(value) for value in silence), 0.0)
        pair = reference.two_channel_convolve(reference.clean_source(), reference.synthetic_rir_pair(
            reference.ROOM_SPECS["short_rt60"]))[:2]
        partial = tuple(channel[:reference.FRAME_SAMPLES * 4 + 37] for channel in pair)
        status, output = reference.process_whole_clip(
            partial, chunks=[reference.FRAME_SAMPLES] * 4 + [37])
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(len(output), len(partial[0]))

    def test_chunking_matches_single_stream_bit_exactly(self):
        pair = reference.causal_probe_pair()
        schedule = [reference.FRAME_SAMPLES] * (len(pair[0]) // reference.FRAME_SAMPLES)
        remainder = len(pair[0]) - sum(schedule)
        if remainder:
            schedule.append(remainder)
        status_a, output_a = reference.process_whole_clip(pair)
        status_b, output_b = reference.process_whole_clip(pair, chunks=schedule)
        self.assertEqual(status_a, reference.Status.OK)
        self.assertEqual(status_b, reference.Status.OK)
        self.assertEqual(reference.tensor_digest(output_a),
                         reference.tensor_digest(output_b))

    def test_mismatched_channel_lengths_are_rejected(self):
        status, output = reference.process_whole_clip(
            ((0.0,) * reference.FRAME_SAMPLES, (0.0,) * (reference.FRAME_SAMPLES - 1)))
        self.assertEqual(status, reference.Status.REJECTED_TENSOR)
        self.assertEqual(output, ())

    def test_reset_replay_and_stale_state(self):
        pair = reference.two_channel_convolve(reference.clean_source(), reference.synthetic_rir_pair(
            reference.ROOM_SPECS["short_rt60"]))[:2]
        clip = tuple(channel[:reference.FRAME_SAMPLES * 12] for channel in pair)
        controller = reference.OnlineController()
        for start in range(0, len(clip[0]), reference.FRAME_SAMPLES):
            result = controller.process(tuple(
                channel[start:start + reference.FRAME_SAMPLES] for channel in clip))
            self.assertEqual(result.status, reference.Status.OK)
        self.assertEqual(controller.reset(reference.RESET_SCHEDULE["initial_epoch"], 9000),
                         reference.Status.REJECTED_EPOCH)
        self.assertEqual(controller.reset(reference.RESET_SCHEDULE["reset_epoch"], 9000),
                         reference.Status.OK)
        emitted = []
        for start in range(0, len(clip[0]), reference.FRAME_SAMPLES):
            result = controller.process(
                tuple(channel[start:start + reference.FRAME_SAMPLES] for channel in clip),
                epoch=reference.RESET_SCHEDULE["reset_epoch"],
                first_input_sample=(9000 + start if start == 0 else None),
                final=start + reference.FRAME_SAMPLES == len(clip[0]))
            self.assertEqual(result.status, reference.Status.OK)
            emitted.extend(result.samples)
        final = controller.finish(epoch=reference.RESET_SCHEDULE["reset_epoch"])
        emitted.extend(final.samples)
        _, expected = reference.process_whole_clip(clip)
        self.assertEqual(reference.tensor_digest(tuple(emitted[:len(clip[0])])),
                         reference.tensor_digest(expected))

    def test_three_fresh_controllers_are_byte_identical(self):
        digests = [reference.tensor_digest(reference._run_candidate(reference.causal_probe_pair()))
                   for _ in range(3)]
        self.assertEqual(len(set(digests)), 1)


class AdapterTests(unittest.TestCase):
    def test_inspect_reports_task_local_boundary(self):
        payload = json.dumps(request("inspect"))
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(payload, encoding="utf-8")
            result = adapter.process_file(request_path, result_path)
        self.assertEqual(result["identity"], adapter.IDENTITY)
        self.assertEqual(result["supported_controls"], list(adapter.CONTROLS))
        self.assertEqual(result["supported_modes"], ["causal_frame_streaming"])
        self.assertEqual(result["content_delay_samples"], 480)
        self.assertEqual(result["input_channels"], 2)
        self.assertEqual(result["output_channels"], 1)
        self.assertFalse(result["default_enabled"])
        self.assertFalse(result["realtime_v0_provider"])
        self.assertIn("unregistered", result["registration"])
        self.assertIn("not used", result["public_c_boundary"])

    def test_run_returns_canonical_finite_result(self):
        samples = stereo_probe()
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(json.dumps(request(
                "run", samples=samples, stimulus="custom")), encoding="utf-8")
            result = adapter.process_file(request_path, result_path)
            raw = result_path.read_text(encoding="utf-8")
        self.assertEqual(raw, adapter.canonical_bytes(result).decode("utf-8") + "\n")
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["output"]["sample_count"], len(samples[0]))
        self.assertEqual(result["output"]["nonfinite_count"], 0)
        self.assertEqual(result["output"]["frames_consumed"], 6)
        self.assertEqual(result["output"]["byte_count"], 4 * len(samples[0]))

    def test_identity_control_is_bit_exact(self):
        samples = stereo_probe()
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(json.dumps(request(
                "run", "identity", samples=samples, stimulus="custom")), encoding="utf-8")
            result = adapter.process_file(request_path, result_path)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["output"]["samples_sha256"],
                         reference.tensor_digest(samples[0]))

    def test_provider_off_is_identity_and_on_uses_causal_wpe(self):
        samples = stereo_probe()
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(json.dumps(request(
                "run", samples=samples, stimulus="custom", enabled=False)), encoding="utf-8")
            off = adapter.process_file(request_path, result_path)
            request_path.write_text(json.dumps(request(
                "run", samples=samples, stimulus="custom", enabled=True)), encoding="utf-8")
            on = adapter.process_file(request_path, result_path)
        self.assertEqual(off["applied_control"], "identity_provider_off")
        self.assertEqual(off["output"]["samples_sha256"],
                         reference.tensor_digest(samples[0]))
        self.assertEqual(on["applied_control"], "online_mc_wpe")
        self.assertNotEqual(on["output"]["samples_sha256"],
                            off["output"]["samples_sha256"])
        self.assertEqual(on["output"]["nonfinite_count"], 0)

    def test_fixture_stimulus_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(json.dumps(request(
                "run", stimulus="short_rt60", samples=None)), encoding="utf-8")
            result = adapter.process_file(request_path, result_path)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["stimulus_id"], "short_rt60")
        expected_samples = (reference.SPEECH_FRAMES + reference.SILENCE_FRAMES) \
            * reference.FRAME_SAMPLES
        self.assertEqual(result["output"]["sample_count"], expected_samples)
        self.assertEqual(result["output"]["nonfinite_count"], 0)

    def test_malformed_requests_are_rejected(self):
        bad_payloads = [
            '{"operation":NaN}',
            '{"protocol_version":1,"protocol_version":1}',
            json.dumps({"protocol_version": 1, "operation": "inspect"}),
            json.dumps(request("inspect") | {"extra": 1}),
            json.dumps(request("run", "bogus", samples=None)),
            json.dumps(request("run", samples=[])),
            json.dumps(request("run", samples=[[0.0] * (reference.MAX_CHUNK_SAMPLES + 1)] * 2)),
            json.dumps(request("run", stimulus="unknown", samples=None)),
            json.dumps(request("run", samples=[list(range(reference.FRAME_SAMPLES)), [0.0]])),
        ]
        for payload in bad_payloads:
            with self.subTest(payload=payload[:60]):
                with tempfile.TemporaryDirectory() as directory:
                    request_path = Path(directory) / "request.json"
                    result_path = Path(directory) / "result.json"
                    request_path.write_text(payload, encoding="utf-8")
                    with self.assertRaises(adapter.RequestError):
                        adapter.process_file(request_path, result_path)


if __name__ == "__main__":
    unittest.main()
