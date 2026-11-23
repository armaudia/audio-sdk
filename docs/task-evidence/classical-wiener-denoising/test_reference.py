# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the task-local classical Wiener reference.

Run from this directory with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v`.
No external packages, downloads, WAV files, SDK runtime or bench artifacts are
needed. The one full report rebuild is intentionally explicit.
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


def request(operation: str, control: str = "wiener", *, stimulus: str = "mild",
            samples=None, attempt: str = "attempt-1"):
    common = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": {"kind": "reference", "id": "wiener", "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": adapter.ADAPTER_ID, "revision": 1},
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
                         "b395b08417212cdf07988c359dde424e9ee011d5d961adfda0d668b8251be8b0")
        self.assertEqual(sha256_file(SIDECAR_FILE),
                         "5e1b45c9c5570ac7a0c742544036a2134197151e621bcd53065c8c25be3e56ca")

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
        specs = {
            "mild": (0.05, 7101),
            "hard": (0.12, 7102),
        }
        clean_digest = reference.tensor_digest(reference.clean_reference())
        for name, (amplitude, seed) in specs.items():
            recorded = self.report["conditions"][name]["fixture_digests"]
            self.assertEqual(clean_digest, recorded["clean_digest"])
            self.assertEqual(reference.tensor_digest(
                reference.noisy_mixture(amplitude, seed)), recorded["noisy_digest"])

    def test_all_required_variants_are_scored(self):
        for name, condition in self.report["conditions"].items():
            variants = condition["variants"]
            self.assertEqual(
                set(variants),
                {"noisy_identity_control", "spectral_subtraction_baseline",
                 "wiener_candidate"},
                name)
            for label, row in variants.items():
                self.assertEqual(row["status"], "scored", name + "/" + label)
                self.assertFalse(row["excluded_from_qualification"])
                self.assertIsNotNone(row["metrics"])
            noisy = variants["noisy_identity_control"]["metrics"]
            self.assertEqual(noisy["delta_si_sdr_db"], 0.0)
            self.assertEqual(noisy["delta_stoi"], 0.0)
            for label in ("spectral_subtraction_baseline", "wiener_candidate"):
                metrics = variants[label]["metrics"]
                self.assertGreater(metrics["delta_si_sdr_db"], 0.0, name + "/" + label)
                self.assertGreater(metrics["delta_stoi"], 0.0, name + "/" + label)
            self.assertTrue(condition["identity_is_bit_exact_to_noisy"])

    def test_task_matched_baseline_is_distinct_and_visible(self):
        for condition in self.report["conditions"].values():
            variants = condition["variants"]
            digests = {label: row["output_digest"] for label, row in variants.items()}
            self.assertEqual(len(set(digests.values())), 3)
            baseline = variants["spectral_subtraction_baseline"]["metrics"]
            candidate = variants["wiener_candidate"]["metrics"]
            self.assertIsNotNone(baseline["delta_si_sdr_db"])
            self.assertIsNotNone(candidate["delta_si_sdr_db"])
            self.assertLess(candidate["si_sdr_db"], baseline["si_sdr_db"])

    def test_clean_speech_preservation_is_explicit(self):
        preservation = self.report["clean_speech_preservation"]
        self.assertEqual(
            set(preservation),
            {"identity", "spectral_subtraction", "wiener"})
        identity = preservation["identity"]
        self.assertEqual(identity["status"], "control_exact")
        self.assertTrue(identity["identity_is_bit_exact"])
        self.assertEqual(identity["stoi"], 1.0)
        self.assertTrue(identity["excluded_from_qualification"])
        for mode in ("spectral_subtraction", "wiener"):
            row = preservation[mode]
            self.assertEqual(row["status"], "scored")
            self.assertEqual(row["metrics"]["stoi"], 1.0)
            self.assertFalse(row["excluded_from_qualification"])

    def test_peaks_and_invalid_outputs_are_bounded(self):
        all_rows = []
        for condition in self.report["conditions"].values():
            all_rows.extend(condition["variants"].values())
        all_rows.extend(self.report["clean_speech_preservation"].values())
        for row in all_rows:
            self.assertLessEqual(row["peak_abs"], 1.0)
            self.assertEqual(row["nonfinite_count"], 0)
            self.assertEqual(row["clipping_count"], 0)
            self.assertEqual(len(row["output_digest"]), 64)

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
        partial = alignment["partial_final_frame"]
        self.assertEqual(partial["status"], "ok")
        self.assertTrue(partial["equal_duration"])
        self.assertEqual(partial["output_samples"], partial["input_samples"])

    def test_adverse_controls_fail_closed(self):
        frame = self.report["adverse"]["frame_rejections"]
        self.assertEqual(frame["nonfinite"], "rejected_nonfinite")
        self.assertEqual(frame["wrong_shape"], "rejected_tensor")
        self.assertEqual(frame["out_of_range"], "rejected_invalid")
        self.assertEqual(frame["stale_epoch"], "rejected_epoch")
        self.assertEqual(frame["stale_position"], "rejected_position")
        self.assertTrue(frame["dsp_state_unchanged"])
        self.assertEqual(frame["invalid_count_delta"], 5)
        for row in self.report["adverse"]["config_rejections"].values():
            self.assertNotEqual(row["status"], "ok")
            self.assertFalse(row["controller_created"])
        missing = self.report["adverse"]["missing_reference"]
        self.assertEqual(missing["status"], "blocked")
        self.assertEqual(missing["reason"], "missing_reference")
        self.assertIsNone(missing["metrics"])
        self.assertTrue(missing["excluded_from_qualification"])
        self.assertTrue(self.report["qualification"]["all_required_results_present"])

    def test_scorer_crosscheck_vectors_are_pinned(self):
        vectors = json.loads(CROSSCHECK_FILE.read_text(encoding="utf-8"))
        self.assertEqual(sha256_file(CROSSCHECK_FILE),
                         "bb79854862b2cb8eb0d5be341e3e7c68bc369a8bae96113c06cd16e11b21c80a")
        scorer_section = self.report["scorer"]
        self.assertEqual(scorer_section["crosscheck_vectors_digest"],
                         reference.object_digest(vectors))
        self.assertEqual(scorer_section["crosscheck_vectors"], vectors)
        self.assertLess(scorer_section["pystoi_crosscheck_max_abs_delta"], 1e-12)
        self.assertLess(scorer_section["si_sdr_numpy_crosscheck_max_abs_delta"], 1e-12)
        expected = {
            name + "_wiener":
                condition["variants"]["wiener_candidate"]["output_digest"]
            for name, condition in self.report["conditions"].items()
        }
        expected.update({
            name + "_spectral_subtraction":
                condition["variants"]["spectral_subtraction_baseline"]["output_digest"]
            for name, condition in self.report["conditions"].items()
        })
        for vector in vectors:
            self.assertEqual(vector["estimate_digest"], expected[vector["name"]])


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
              if key != "gain_floor"}, reference.Status.REJECTED_MISSING),
            (reference.config_with(unknown=1), reference.Status.REJECTED_INVALID),
            (reference.config_with(gain_floor=float("inf")),
             reference.Status.REJECTED_NONFINITE),
            (reference.config_with(mode="bogus"), reference.Status.REJECTED_INVALID),
            (reference.config_with(noise_frames="10"), reference.Status.REJECTED_INVALID),
        ]
        for config, expected in cases:
            status, controller = reference.WienerController.create(config)
            self.assertEqual(status, expected)
            self.assertIsNone(controller)
        self.assertEqual(reference.DEFAULT_CONFIG["mode"], "wiener")
        self.assertEqual(len(reference.DEFAULT_CONFIG), len(reference.REQUIRED_KEYS))

    def test_identity_is_bit_exact_and_wiener_is_causal(self):
        samples = reference.noisy_mixture(0.05, 7101)[:reference.FRAME_SAMPLES * 40]
        identity = reference._run("identity", samples)
        self.assertEqual(reference.tensor_digest(identity),
                         reference.tensor_digest(samples))
        controller = reference.WienerController(reference.DEFAULT_CONFIG)
        seen = []
        for start in range(0, len(samples), reference.FRAME_SAMPLES):
            frame = samples[start:start + reference.FRAME_SAMPLES]
            result = controller.process(frame, epoch=1, first_input_sample=start)
            self.assertEqual(result.status, reference.Status.OK)
            self.assertEqual(result.source_first_sample, start)
            seen.append(result.samples)
        self.assertEqual(
            reference.tensor_digest([value for frame in seen for value in frame]),
            reference.tensor_digest(reference._run("wiener", samples)))

    def test_rejections_preserve_dsp_state(self):
        controller = reference.WienerController(reference.DEFAULT_CONFIG)
        valid = (0.01,) * reference.FRAME_SAMPLES
        self.assertEqual(controller.process(valid).status, reference.Status.OK)
        before = controller.state.dsp_digest()
        cases = [
            controller.process((math.nan,) * reference.FRAME_SAMPLES),
            controller.process((0.0,) * (reference.FRAME_SAMPLES - 1)),
            controller.process((9.0,) * reference.FRAME_SAMPLES),
            controller.process(valid, epoch=99),
            controller.process(valid, first_input_sample=123456),
        ]
        self.assertEqual(
            [result.status.value for result in cases],
            ["rejected_nonfinite", "rejected_tensor", "rejected_invalid",
             "rejected_epoch", "rejected_position"])
        self.assertEqual(controller.state.dsp_digest(), before)
        self.assertEqual(controller.state.invalid_count, 5)
        self.assertEqual(controller.process(valid).status, reference.Status.OK)

    def test_reset_epoch_and_position(self):
        controller = reference.WienerController(reference.DEFAULT_CONFIG)
        self.assertEqual(controller.reset(1, 0), reference.Status.REJECTED_EPOCH)
        self.assertEqual(controller.reset(3, 9000), reference.Status.OK)
        self.assertEqual(controller.state.epoch, 3)
        self.assertEqual(controller.state.output_start, 9000)
        self.assertEqual(
            controller.process((0.0,) * reference.FRAME_SAMPLES,
                               first_input_sample=0).status,
            reference.Status.REJECTED_POSITION)
        self.assertEqual(
            controller.process((0.0,) * reference.FRAME_SAMPLES,
                               epoch=2, first_input_sample=9000).status,
            reference.Status.REJECTED_EPOCH)

    def test_partial_final_frame_keeps_duration(self):
        samples = reference.synthetic_speech(frames=12) + (0.11, 0.12, 0.13)
        padded = samples + (0.0,) * (reference.FRAME_SAMPLES - len(samples) %
                                     reference.FRAME_SAMPLES)
        status, output = reference.WienerController(
            reference.DEFAULT_CONFIG).process_stream(padded)
        self.assertEqual(status, reference.Status.OK)
        self.assertEqual(len(output), len(padded))
        self.assertEqual(len(output[:len(samples)]), len(samples))


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
        self.assertIn("unregistered", result["registration"])

    def test_run_returns_canonical_finite_result(self):
        payload = json.dumps(request("run", "wiener", samples=None))
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
                         len(reference.noisy_mixture(0.05, 7101)))
        self.assertEqual(result["output"]["nonfinite_count"], 0)
        self.assertEqual(raw.count("\n"), 1)

    def test_malformed_requests_are_rejected(self):
        bad_payloads = [
            '{"operation":NaN}',
            '{"protocol_version":1,"protocol_version":1}',
            json.dumps({"protocol_version": 1, "operation": "inspect"}),
            json.dumps(request("inspect") | {"extra": 1}),
            json.dumps(request("run", "bogus", samples=None)),
            json.dumps(request("run", samples=[0.0, 1.0])),
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
