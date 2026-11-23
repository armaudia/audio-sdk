# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the task-local offline mono WPE reference.

Run from this directory with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v`.
No external packages, downloads, WAV files, SDK runtime or bench artifacts are
needed. The full report rebuild is intentionally explicit.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import reference
import run as adapter
import scorer

TASK_DIR = Path(__file__).resolve().parent
WORKTREE = TASK_DIR.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]
REPORT_FILE = TASK_DIR / "report.json"
SIDECAR_FILE = TASK_DIR / "report.json.sha256"
CROSSCHECK_FILE = TASK_DIR / "crosscheck_vectors.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request(operation: str, control: str = "offline_wpe", *, stimulus: str = "short_rt60",
            samples=None, attempt: str = "attempt-1"):
    common = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": {"kind": "reference", "id": "offline-mono-wpe", "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": adapter.IDENTITY, "revision": 1},
        "configuration": {"control": control},
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
        self.assertEqual(sha256_file(REPORT_FILE),
                         "2b9be2488c4b0f82f417abd3e131c840729856937ed8239f2645beeaa30d7e61")
        self.assertEqual(sha256_file(SIDECAR_FILE),
                         "1b7a5e1af8efd625003c386c8fadb79b171c2d0f0e05d830f6cbbf9bbd2a4d88")

    def test_report_regeneration_is_byte_identical(self):
        text, digest = reference.canonical_report(reference.build_report())
        self.assertEqual(text.encode("utf-8") + b"\n", REPORT_FILE.read_bytes())
        self.assertEqual(digest, self.sidecar)

    def test_pinned_sources_and_boundary_headers_are_unchanged(self):
        for relative, expected in reference.SOURCE_PINS.items():
            path = AUDIO_ROOT / relative
            if not path.exists():
                self.skipTest("source evidence unavailable: " + relative)
            self.assertEqual(sha256_file(path), expected, relative)
        for relative, expected in reference.BOUNDARY_PINS.items():
            path = WORKTREE / relative
            self.assertTrue(path.exists(), relative)
            self.assertEqual(sha256_file(path), expected, relative)

    def test_fixture_digests_are_reproducible(self):
        source_digest = reference.tensor_digest(reference.clean_source())
        self.assertEqual(self.report["fixture_digest"],
                         "fb2aeb11e2afd5eb1634f506a680867d0b5ca43624718b9e78b73b0e44e647dd")
        for name, condition in self.report["conditions"].items():
            spec = reference.ROOM_SPECS[name]
            rir = reference.synthetic_rir(spec["rt60_ms"], spec["dr_db"], spec["seed"])
            self.assertEqual(source_digest, condition["source_digest"])
            self.assertEqual(reference.tensor_digest(rir), condition["rir_digest"])
            self.assertEqual(condition["rir_samples"], len(rir))

    def test_all_required_variants_are_scored(self):
        expected = {"identity_control", "wpe_candidate",
                    "noisy_identity_control", "wpe_on_noisy"}
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
            self.assertIn(condition["configured_direct_to_diffuse_db"], (12.0, 6.0, 0.0))

    def test_wpe_result_is_not_presented_as_universal_improvement(self):
        beats = [condition["wpe_beats_identity_si_sdr"]
                 for condition in self.report["conditions"].values()]
        self.assertIn(True, beats)
        self.assertIn(False, beats)
        self.assertEqual(
            {condition["rt60_ms"] for condition in self.report["conditions"].values()},
            {250, 550, 900})

    def test_clean_source_preservation_is_explicit(self):
        preservation = self.report["clean_source_preservation"]
        self.assertEqual(set(preservation), {"identity_control", "wpe_candidate"})
        identity = preservation["identity_control"]
        self.assertEqual(identity["status"], "control_exact")
        self.assertTrue(identity["identity_is_bit_exact"])
        self.assertEqual(identity["stoi"], 1.0)
        self.assertTrue(identity["excluded_from_qualification"])
        wpe = preservation["wpe_candidate"]
        self.assertEqual(wpe["status"], "scored")
        self.assertFalse(wpe["identity_is_bit_exact"])
        self.assertFalse(wpe["excluded_from_qualification"])

    def test_peaks_and_invalid_outputs_are_bounded(self):
        all_rows = []
        for condition in self.report["conditions"].values():
            all_rows.extend(condition["variants"].values())
        all_rows.extend(self.report["clean_source_preservation"].values())
        for row in all_rows:
            self.assertLessEqual(row["peak_abs"], 1.0)
            self.assertEqual(row["nonfinite_count"], 0)
            self.assertEqual(row["clipping_count"], 0)
            self.assertEqual(len(row["output_digest"]), 64)

    def test_spectral_tilt_is_present_for_every_condition(self):
        for name, condition in self.report["conditions"].items():
            tilt = condition["spectral_tilt"]
            self.assertEqual(set(tilt),
                             {"early_target", "identity_control", "wpe_candidate"}, name)
            for label, row in tilt.items():
                self.assertEqual(row["status"], "ok", name + "/" + label)
                self.assertLess(row["mid_over_low_db"], 0.0)
                self.assertLess(row["high_over_low_db"], 0.0)
            self.assertIn("mid_minus_target_db", tilt["identity_control"])
            self.assertIn("high_minus_target_db", tilt["wpe_candidate"])

    def test_alignment_state_and_duration_semantics(self):
        alignment = self.report["alignment_and_state"]
        self.assertEqual(alignment["impulse"]["status"], "ok")
        self.assertEqual(alignment["impulse"]["peak_index"], 0)
        self.assertEqual(alignment["impulse"]["content_delay_samples"], 0)
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
        self.assertEqual(partial["status"], "ok")
        self.assertTrue(partial["equal_duration"])
        self.assertEqual(partial["output_samples"], partial["input_samples"])

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
        self.assertEqual(frame["finalize_status"], "ok")
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
        self.assertEqual(self.report["qualification"]["status"], "synthetic_reference_only")

    def test_scorer_crosscheck_vectors_are_pinned(self):
        self.assertEqual(sha256_file(CROSSCHECK_FILE),
                         "7bdd131858306648b4f24b1544a6afb4da2660b3f2d3edcdfb3b715e574a18a2")
        vectors = json.loads(CROSSCHECK_FILE.read_text(encoding="utf-8"))
        scorer_section = self.report["scorer"]
        self.assertEqual(scorer_section["crosscheck_vectors_digest"],
                         reference.object_digest(vectors))
        self.assertEqual(scorer_section["crosscheck_vectors"], vectors)
        self.assertLess(scorer_section["pystoi_crosscheck_max_abs_delta"], 1e-12)
        self.assertLess(scorer_section["si_sdr_numpy_crosscheck_max_abs_delta"], 1e-12)
        expected = {
            name + "_" + label: row["output_digest"]
            for name, condition in self.report["conditions"].items()
            for label, row in condition["variants"].items()
            if label in ("wpe_candidate", "wpe_on_noisy")
        }
        self.assertEqual(len(vectors), 6)
        for vector in vectors:
            self.assertEqual(vector["estimate_digest"], expected[vector["name"]])

    def test_offline_whole_clip_is_explicitly_outside_realtime_v0(self):
        self.assertFalse(self.report["format"]["realtime_v0_provider"])
        self.assertEqual(self.report["format"]["processing_mode"], "offline_whole_clip_only")
        self.assertEqual(self.report["format"]["frame_samples"], 160)
        self.assertEqual(self.report["format"]["sample_rate_hz"], 16000)
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

    def test_scaled_signal_si_sdr_is_invariant(self):
        signal = [0.12 * math.sin(index * 0.3) for index in range(256)]
        scaled = [0.37 * value for value in signal]
        first, reason = scorer.si_sdr(signal, scaled)
        self.assertIsNone(reason)
        self.assertGreater(first, 300.0)

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
            (reference.config_with(regularization=float("inf")),
             reference.Status.REJECTED_NONFINITE),
            (reference.config_with(delay="8"), reference.Status.REJECTED_INVALID),
            (reference.config_with(taps=0), reference.Status.REJECTED_INVALID),
            (reference.config_with(hop_size=512), reference.Status.REJECTED_INVALID),
        ]
        for config, expected in cases:
            status, controller = reference.OfflineController.create(config)
            self.assertEqual(status, expected)
            self.assertIsNone(controller)
        self.assertEqual(reference.DEFAULT_CONFIG["fft_size"], 512)
        self.assertEqual(reference.DEFAULT_CONFIG["hop_size"], 128)
        self.assertEqual(reference.DEFAULT_CONFIG["taps"], 5)
        self.assertEqual(reference.DEFAULT_CONFIG["delay"], 8)
        self.assertEqual(len(reference.DEFAULT_CONFIG), len(reference.REQUIRED_KEYS))

    def test_finish_is_whole_clip_and_no_partial_output_is_emitted(self):
        samples = reference.impulse(frames=12)
        controller = reference.OfflineController()
        for start in range(0, len(samples), reference.CHUNK_SAMPLES):
            result = controller.process(samples[start:start + reference.CHUNK_SAMPLES])
            self.assertEqual(result.status, reference.Status.OK)
            self.assertEqual(result.samples, ())
        final = controller.finish()
        self.assertEqual(final.status, reference.Status.OK)
        self.assertEqual(len(final.samples), len(samples))
        self.assertEqual(final.source_first_sample, 0)

    def test_chunking_matches_single_buffer_bit_exactly(self):
        samples = reference.synthetic_speech(frames=20)
        schedule = [reference.CHUNK_SAMPLES] * (len(samples) // reference.CHUNK_SAMPLES)
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
        controller = reference.OfflineController()
        valid = (0.01,) * reference.STATE_CHUNK_SAMPLES
        self.assertEqual(controller.process(valid).status, reference.Status.OK)
        before = controller.state.dsp_digest()
        cases = [
            controller.process((math.nan,) * reference.CHUNK_SAMPLES),
            controller.process((0.0,) * (reference.MAX_CHUNK_SAMPLES + 1)),
            controller.process((9.0,) * reference.CHUNK_SAMPLES),
            controller.process(valid, epoch=99),
            controller.process(valid, first_input_sample=123456),
            controller.process(valid, session=2),
        ]
        self.assertEqual([result.status.value for result in cases],
                         ["rejected_nonfinite", "rejected_tensor", "rejected_invalid",
                          "rejected_epoch", "rejected_position", "rejected_session"])
        self.assertEqual(controller.state.dsp_digest(), before)
        self.assertEqual(controller.state.invalid_count, 6)

    def test_reset_epoch_and_position(self):
        controller = reference.OfflineController()
        self.assertEqual(controller.reset(1, 0), reference.Status.REJECTED_EPOCH)
        self.assertEqual(controller.reset(3, 9000), reference.Status.OK)
        self.assertEqual(controller.state.epoch, 3)
        self.assertEqual(controller.state.first_input_sample, 9000)
        self.assertEqual(
            controller.process((0.0,) * reference.STATE_CHUNK_SAMPLES,
                               first_input_sample=0).status,
            reference.Status.REJECTED_POSITION)
        self.assertEqual(
            controller.process((0.0,) * reference.STATE_CHUNK_SAMPLES,
                               epoch=2, first_input_sample=9000).status,
            reference.Status.REJECTED_EPOCH)
        samples = reference.synthetic_speech(frames=16)
        self.assertEqual(controller.process(samples, epoch=3,
                                            first_input_sample=9000).status,
                         reference.Status.OK)
        self.assertEqual(controller.finish(epoch=3).status, reference.Status.OK)
        self.assertEqual(controller.process(valid_sample()).status,
                         reference.Status.REJECTED_SESSION)

    def test_partial_final_frame_keeps_duration(self):
        samples = reference.synthetic_speech(frames=12) + (0.11, 0.12, 0.13)
        schedule = [reference.CHUNK_SAMPLES]
        schedule.append(len(samples) - sum(schedule))
        status, output = reference.process_whole_clip(samples, chunks=schedule)
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(len(output), len(samples))

    def test_impulse_peak_and_silence_are_zero_delay(self):
        samples = reference.impulse(frames=12)
        status, output = reference.process_whole_clip(samples)
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(max(range(len(output)), key=lambda i: abs(output[i])), 0)
        status, output = reference.process_whole_clip(reference.silence(frames=40))
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(max(abs(value) for value in output), 0.0)


def valid_sample():
    return (0.01,) * reference.CHUNK_SAMPLES


class AdapterTests(unittest.TestCase):
    def test_inspect_reports_task_local_boundary(self):
        payload = json.dumps(request("inspect"))
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(payload, encoding="utf-8")
            result = adapter.process_file(request_path, result_path)
        self.assertEqual(result["operation"], "inspect")
        self.assertEqual(result["identity"], adapter.IDENTITY)
        self.assertEqual(result["supported_controls"], list(adapter.CONTROLS))
        self.assertEqual(result["supported_modes"], ["offline_whole_clip"])
        self.assertFalse(result["realtime_v0_provider"])
        self.assertIn("unregistered", result["registration"])
        self.assertIn("not used", result["public_c_boundary"])

    def test_run_returns_canonical_finite_result(self):
        payload = json.dumps(request("run", "offline_wpe", samples=None))
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(payload, encoding="utf-8")
            result = adapter.process_file(request_path, result_path)
            raw = result_path.read_text(encoding="utf-8")
        self.assertEqual(raw, adapter.canonical_bytes(result).decode("utf-8") + "\n")
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["output"]["sample_count"],
                         len(reference.clean_source()))
        self.assertEqual(result["output"]["nonfinite_count"], 0)
        self.assertEqual(raw.count("\n"), 1)

    def test_identity_control_is_bit_exact(self):
        payload = json.dumps(request("run", "identity", stimulus="clean", samples=None))
        with tempfile.TemporaryDirectory() as directory:
            request_path = Path(directory) / "request.json"
            result_path = Path(directory) / "result.json"
            request_path.write_text(payload, encoding="utf-8")
            result = adapter.process_file(request_path, result_path)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["output"]["samples_sha256"],
                         reference.tensor_digest(reference.clean_source()))

    def test_malformed_requests_are_rejected(self):
        bad_payloads = [
            '{"operation":NaN}',
            '{"protocol_version":1,"protocol_version":1}',
            json.dumps({"protocol_version": 1, "operation": "inspect"}),
            json.dumps(request("inspect") | {"extra": 1}),
            json.dumps(request("run", "bogus", samples=None)),
            json.dumps(request("run", samples=[])),
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
