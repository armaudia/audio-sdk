# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local online mono WPE reference.

Run from this directory with ``PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v``.
No external packages, downloads, WAV files, SDK runtime or Bench artifacts are
needed. The full report rebuild is intentionally explicit and is the only slow
test; every other check uses the frozen committed evidence.
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
CROSSCHECK_FILE = fixture.CROSSCHECK_FILE
REPORT_SHA256 = "77d5268a5b4e5c798fcbae5ef0d23dcf6008ed3534523d15fb21806fbb36fdd4"
SIDECAR_SHA256 = "efd6cd4a7ecbdd371ce1e6b2051fd6abd98a353f705ed58e78b7d9789fbf79ba"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request(operation: str, control: str = "online_wpe", *, stimulus: str = "short_rt60",
            samples=None, attempt: str = "attempt-1", enabled: bool = True):
    common = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": {"kind": "reference", "id": "online-mono-wpe", "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": adapter.IDENTITY, "revision": 1},
        "configuration": {"control": control, "provider_enabled": enabled},
    }
    if operation == "inspect":
        return common
    common.update({"attempt_id": attempt, "stimulus_id": stimulus, "samples": samples})
    return common


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

    def test_pinned_sources_and_boundary_headers_are_unchanged(self):
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
            rir = reference.synthetic_rir(spec["rt60_ms"], spec["dr_db"], spec["seed"])
            self.assertEqual(digests[name + "_rir"], condition["rir_digest"])
            self.assertEqual(reference.tensor_digest(rir), condition["rir_digest"])
            self.assertEqual(condition["rir_samples"], len(rir))

    def test_all_required_variants_are_scored(self):
        expected = {"identity_control", "online_wpe_candidate",
                    "noisy_identity_control", "online_wpe_on_noisy"}
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
            self.assertTrue(condition["identity_is_bit_exact"])

    def test_identity_input_is_bit_exact_and_candidate_differs(self):
        for condition in self.report["conditions"].values():
            variants = condition["variants"]
            self.assertEqual(variants["identity_control"]["output_digest"],
                             condition["identity_input_digest"])
            self.assertEqual(variants["noisy_identity_control"]["output_digest"],
                             condition["noisy_input_digest"])
            self.assertNotEqual(variants["online_wpe_candidate"]["output_digest"],
                                condition["identity_input_digest"])

    def test_candidate_is_not_presented_as_universal_improvement(self):
        beats = [condition["candidate_beats_identity_si_sdr"]
                 for condition in self.report["conditions"].values()]
        self.assertEqual(len(beats), 3)
        self.assertTrue(any(beats), "expected at least one measured gain")
        self.assertFalse(all(beats), "expected at least one measured regression")
        self.assertEqual(
            {condition["rt60_ms"] for condition in self.report["conditions"].values()},
            {250, 550, 900})

    def test_clean_near_end_preservation_is_explicit(self):
        preservation = self.report["clean_near_end_preservation"]
        self.assertEqual(set(preservation), {"identity_control", "online_wpe_candidate"})
        identity = preservation["identity_control"]
        self.assertEqual(identity["status"], "control_exact")
        self.assertTrue(identity["identity_is_bit_exact"])
        self.assertEqual(identity["stoi"], 1.0)
        self.assertTrue(identity["excluded_from_qualification"])
        candidate = preservation["online_wpe_candidate"]
        self.assertEqual(candidate["status"], "scored")
        self.assertFalse(candidate["identity_is_bit_exact"])
        self.assertFalse(candidate["excluded_from_qualification"])

    def test_peaks_and_invalid_outputs_are_bounded(self):
        rows = []
        for condition in self.report["conditions"].values():
            rows.extend(condition["variants"].values())
        for special in self.report["special_conditions"].values():
            rows.extend(special["variants"].values())
        rows.extend(self.report["clean_near_end_preservation"].values())
        for row in rows:
            self.assertLessEqual(row["peak_abs"], 1.0)
            self.assertEqual(row["nonfinite_count"], 0)
            self.assertEqual(row["clipping_count"], 0)
            self.assertEqual(len(row["output_digest"]), 64)

    def test_spectral_tilt_is_present_for_every_condition(self):
        for name, condition in self.report["conditions"].items():
            tilt = condition["spectral_tilt"]
            self.assertEqual(set(tilt),
                             {"early_target", "identity_control", "online_wpe_candidate"}, name)
            for label, row in tilt.items():
                self.assertEqual(row["status"], "ok", name + "/" + label)
                self.assertLess(row["mid_over_low_db"], 0.0)
                self.assertLess(row["high_over_low_db"], 0.0)
            self.assertIn("mid_minus_target_db", tilt["identity_control"])
            self.assertIn("high_minus_target_db", tilt["online_wpe_candidate"])

    def test_alignment_state_duration_and_causality(self):
        alignment = self.report["alignment_and_state"]
        self.assertEqual(alignment["impulse"]["status"], "ok")
        self.assertEqual(alignment["impulse"]["peak_index"], 480)
        self.assertEqual(alignment["impulse"]["content_delay_samples"], 480)
        self.assertEqual(alignment["silence"]["status"], "ok")
        self.assertEqual(alignment["silence"]["peak_abs"], 0.0)
        self.assertTrue(alignment["duration"]["equal"])
        self.assertTrue(alignment["chunking_equivalence"]["equal"])
        self.assertTrue(alignment["session_independence"]["independent"])
        self.assertEqual(alignment["reset"]["status"], "ok")
        self.assertTrue(alignment["reset"]["replay_matches_original"])
        self.assertEqual(alignment["reset"]["stale_epoch_status"], "rejected_epoch")
        self.assertEqual(alignment["reset"]["stale_position_status"], "rejected_position")
        partial = alignment["partial_final_frame"]
        self.assertTrue(partial["equal_duration"])
        self.assertEqual(partial["output_samples"], partial["input_samples"])
        causality = alignment["causality_probe"]
        self.assertTrue(causality["prefix_byte_identical"])
        self.assertTrue(causality["future_frame_differs"])
        self.assertEqual(causality["emitted_frames_compared"], 8)

    def test_room_profile_structure_is_applied(self):
        profile = self.report["room_profile"]
        self.assertEqual(profile["profile"], "room")
        self.assertEqual(set(profile["mapped_cases"]),
                         {"echo_only", "near_end_only", "overlap", "no_reference"})
        self.assertIn("delayed_or_missing_render", profile["not_applicable"])
        self.assertEqual(profile["frozen"]["rate_hz"], 16000)
        self.assertEqual(profile["frozen"]["frame_samples"], 160)
        self.assertIn("reset_schedule", profile["frozen"])

    def test_three_byte_identical_repeats_are_pinned(self):
        repeats = self.report["repeatability"]
        self.assertEqual(repeats["runs"], 3)
        self.assertTrue(repeats["byte_identical"])
        self.assertEqual(len(set(repeats["output_digests"])), 1)
        observed = fixture.repeat_probe()
        self.assertEqual(observed["input_digest"], repeats["input_digest"])
        self.assertEqual(observed["output_digests"], repeats["output_digests"])

    def test_adverse_controls_fail_closed(self):
        frame = self.report["adverse"]["frame_rejections"]
        self.assertEqual(frame["nonfinite"], "rejected_nonfinite")
        self.assertEqual(frame["stale_session"], "rejected_session")
        self.assertEqual(frame["wrong_shape"], "rejected_tensor")
        self.assertEqual(frame["out_of_range"], "rejected_invalid")
        self.assertEqual(frame["stale_epoch"], "rejected_epoch")
        self.assertEqual(frame["stale_position"], "rejected_position")
        self.assertTrue(frame["dsp_state_unchanged"])
        self.assertEqual(frame["invalid_count_delta"], 6)
        self.assertEqual(frame["finished_reuse"], "rejected_session")
        self.assertEqual(frame["process_after_finish"], "rejected_session")
        for row in self.report["adverse"]["config_rejections"].values():
            self.assertNotEqual(row["status"], "ok")
            self.assertFalse(row["controller_created"])
        missing = self.report["adverse"]["missing_reference"]
        self.assertEqual(missing["status"], "blocked")
        self.assertEqual(missing["reason"], "missing_reference")
        self.assertIsNone(missing["metrics"])
        self.assertTrue(missing["excluded_from_qualification"])
        self.assertTrue(self.report["qualification"]["all_required_results_present"])
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")

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
        self.assertIn("not online candidate results", section["crosscheck_vectors_origin"])

    def test_offline_control_is_not_an_online_oracle(self):
        control = self.report["noncausal_upper_bound_control"]
        self.assertFalse(control["usable_for_realtime_qualification"])
        self.assertFalse(control["used_as_candidate_oracle"])
        self.assertEqual(control["source_sha256"], reference.ARTIFACT_PINS[
            "docs/task-evidence/offline-mono-wpe/report.json"])
        self.assertEqual(len(self.report["causal_vs_noncausal_comparison"]), 3)

    def test_provider_stays_opt_in_unregistered_and_disabled(self):
        provider = self.report["provider"]
        self.assertFalse(provider["default_enabled"])
        self.assertTrue(provider["opt_in_required"])
        self.assertFalse(provider["registered"])
        self.assertFalse(provider["c_abi_or_sdk_default_change"])
        self.assertEqual(provider["descriptor_settings"], {})
        probe = provider["off_on_probe"]
        self.assertTrue(probe["off_is_bit_exact_identity"])
        self.assertTrue(probe["on_differs_from_off"])
        self.assertFalse(self.report["format"]["realtime_v0_provider"])
        self.assertIn("no real room", self.report["scope"])
        self.assertIn("no release qualification", self.report["scope"])


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


class ControllerTests(unittest.TestCase):
    def test_config_validation(self):
        cases = [
            (None, reference.Status.REJECTED_MISSING),
            ({key: value for key, value in reference.DEFAULT_CONFIG.items()
              if key != "taps"}, reference.Status.REJECTED_MISSING),
            (reference.config_with(unknown=1), reference.Status.REJECTED_INVALID),
            (reference.config_with(forgetting=float("inf")), reference.Status.REJECTED_NONFINITE),
            (reference.config_with(wpe_delay_frames="8"), reference.Status.REJECTED_INVALID),
            (reference.config_with(taps=0), reference.Status.REJECTED_INVALID),
            (reference.config_with(fft_size=512, hop_size=512), reference.Status.REJECTED_INVALID),
        ]
        for config, expected in cases:
            status, controller = reference.OnlineController.create(config)
            self.assertEqual(status, expected)
            self.assertIsNone(controller)

    def test_content_delay_and_partial_final_frame(self):
        samples = reference.impulse(frames=12)
        status, output = reference.process_whole_clip(samples)
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(max(range(len(output)), key=lambda i: abs(output[i])), 480)
        status, silence = reference.process_whole_clip(reference.silence(frames=40))
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(max(abs(value) for value in silence), 0.0)
        partial = samples[:reference.FRAME_SAMPLES * 4 + 37]
        status, output = reference.process_whole_clip(
            partial, chunks=[reference.FRAME_SAMPLES] * 4 + [37])
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(len(output), len(partial))

    def test_chunking_matches_single_stream_bit_exactly(self):
        samples = reference.synthetic_speech(frames=20)
        schedule = [reference.FRAME_SAMPLES] * (len(samples) // reference.FRAME_SAMPLES)
        remainder = len(samples) - sum(schedule)
        if remainder:
            schedule.append(remainder)
        status_a, output_a = reference.process_whole_clip(samples)
        status_b, output_b = reference.process_whole_clip(samples, chunks=schedule)
        self.assertEqual(status_a, reference.Status.OK)
        self.assertEqual(status_b, reference.Status.OK)
        self.assertEqual(reference.tensor_digest(output_a),
                         reference.tensor_digest(output_b))

    def test_rejections_preserve_dsp_state(self):
        controller = reference.OnlineController()
        valid = (0.01,) * reference.FRAME_SAMPLES
        self.assertEqual(controller.process(valid).status, reference.Status.OK)
        before = controller.dsp_digest()
        cases = [
            controller.process((math.nan,) * reference.FRAME_SAMPLES),
            controller.process((0.0,) * (reference.FRAME_SAMPLES + 1)),
            controller.process((9.0,) * reference.FRAME_SAMPLES),
            controller.process(valid, epoch=99),
            controller.process(valid, first_input_sample=123456),
            controller.process(valid, session=2),
        ]
        self.assertEqual([result.status.value for result in cases],
                         ["rejected_nonfinite", "rejected_tensor", "rejected_invalid",
                          "rejected_epoch", "rejected_position", "rejected_session"])
        self.assertEqual(controller.dsp_digest(), before)
        self.assertEqual(controller.state.invalid_count, 6)

    def test_reset_replay_and_stale_state(self):
        samples = reference.synthetic_speech(frames=12)
        controller = reference.OnlineController()
        for start in range(0, len(samples), reference.FRAME_SAMPLES):
            self.assertEqual(controller.process(
                samples[start:start + reference.FRAME_SAMPLES]).status, reference.Status.OK)
        self.assertEqual(controller.reset(1, 9000), reference.Status.REJECTED_EPOCH)
        self.assertEqual(controller.reset(3, 9000), reference.Status.OK)
        self.assertEqual(controller.state.epoch, 3)
        emitted: list = []
        final = reference.Status.OK
        for start in range(0, len(samples), reference.FRAME_SAMPLES):
            result = controller.process(
                samples[start:start + reference.FRAME_SAMPLES], epoch=3,
                first_input_sample=(9000 + start if start == 0 else None),
                final=start + reference.FRAME_SAMPLES == len(samples))
            self.assertEqual(result.status, reference.Status.OK)
            emitted.extend(result.samples)
        replay = controller.finish(epoch=3)
        self.assertEqual(replay.status, reference.Status.OK)
        emitted.extend(replay.samples)
        _, expected = reference.process_whole_clip(samples)
        self.assertEqual(reference.tensor_digest(tuple(emitted[:len(samples)])),
                         reference.tensor_digest(expected))
        self.assertEqual(controller.process(valid_sample()).status,
                         reference.Status.REJECTED_SESSION)


def valid_sample():
    return (0.01,) * reference.FRAME_SAMPLES


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
        self.assertFalse(result["default_enabled"])
        self.assertFalse(result["realtime_v0_provider"])
        self.assertIn("unregistered", result["registration"])
        self.assertIn("not used", result["public_c_boundary"])

    def test_run_returns_canonical_finite_result(self):
        samples = [0.01 * math.sin(index * 0.4) for index in range(reference.FRAME_SAMPLES * 6)]
        payload = json.dumps(request("run", "online_wpe", samples=samples, stimulus="custom"))
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(payload, encoding="utf-8")
            result = adapter.process_file(request_path, result_path)
            raw = result_path.read_text(encoding="utf-8")
        self.assertEqual(raw, adapter.canonical_bytes(result).decode("utf-8") + "\n")
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["output"]["sample_count"], len(samples))
        self.assertEqual(result["output"]["nonfinite_count"], 0)
        self.assertEqual(result["output"]["frames_consumed"], 6)
        self.assertEqual(raw.count("\n"), 1)

    def test_identity_control_is_bit_exact(self):
        samples = reference.causal_probe_signal()
        payload = json.dumps(request("run", "identity", samples=list(samples), stimulus="custom"))
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(payload, encoding="utf-8")
            result = adapter.process_file(request_path, result_path)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["output"]["samples_sha256"],
                         reference.tensor_digest(samples))

    def test_provider_off_is_identity_and_on_uses_causal_wpe(self):
        samples = reference.causal_probe_signal()
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(json.dumps(request(
                "run", "online_wpe", samples=list(samples), stimulus="custom", enabled=False)),
                encoding="utf-8")
            off = adapter.process_file(request_path, result_path)
            request_path.write_text(json.dumps(request(
                "run", "online_wpe", samples=list(samples), stimulus="custom", enabled=True)),
                encoding="utf-8")
            on = adapter.process_file(request_path, result_path)
        self.assertEqual(off["applied_control"], "identity_provider_off")
        self.assertEqual(off["output"]["samples_sha256"], reference.tensor_digest(samples))
        self.assertEqual(on["applied_control"], "online_wpe")
        self.assertNotEqual(on["output"]["samples_sha256"],
                            off["output"]["samples_sha256"])
        self.assertEqual(on["output"]["nonfinite_count"], 0)

    def test_malformed_requests_are_rejected(self):
        bad_payloads = [
            '{"operation":NaN}',
            '{"protocol_version":1,"protocol_version":1}',
            json.dumps({"protocol_version": 1, "operation": "inspect"}),
            json.dumps(request("inspect") | {"extra": 1}),
            json.dumps(request("run", "bogus", samples=None)),
            json.dumps(request("run", samples=[])),
            json.dumps(request("run", samples=[0.0] * (reference.MAX_CHUNK_SAMPLES + 1))),
            json.dumps(request("run", stimulus="unknown", samples=None)),
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
