# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic tests for the synthetic FFmpeg-afftdn evidence package."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

import fixture
import reference
import run as cli
import scorer

TASK = Path(__file__).resolve().parent
SPDX_TAG = "SPDX" "-License-Identifier:"


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.items = [reference._item_result(item_id) for item_id in fixture.item_ids()]

    def item(self, item_id: str) -> dict:
        return next(item for item in self.items if item["id"] == item_id)

    def test_fixture_digest_stable(self) -> None:
        self.assertEqual(fixture.fixture_digest(), fixture.fixture_digest())
        self.assertEqual(len(fixture.fixture_digest()), 64)

    def test_source_pin_count(self) -> None:
        self.assertEqual(len(fixture.SOURCE_PINS), 14)

    def test_item_ids_frozen(self) -> None:
        self.assertEqual(fixture.item_ids(), ("case-quiet", "case-loud", "case-hum", "case-burst"))

    def test_synthesis_deterministic(self) -> None:
        a = fixture.synthesize("case-quiet")
        b = fixture.synthesize("case-quiet")
        self.assertEqual(a["clean"], b["clean"])
        self.assertEqual(a["noisy"], b["noisy"])

    def test_calibration_span_noise_only(self) -> None:
        for item_id in fixture.item_ids():
            data = fixture.synthesize(item_id)
            for index in range(fixture.CALIBRATION_END):
                self.assertEqual(data["clean_ints"][index], 0)

    def test_clean_speech_nonzero(self) -> None:
        for item_id in fixture.item_ids():
            data = fixture.synthesize(item_id)
            self.assertGreater(max(abs(value) for value in data["clean"]), 0.1)

    def test_noise_profile_deterministic(self) -> None:
        noisy = fixture.synthesize("case-loud")["noisy"]
        self.assertEqual(reference.noise_profile(noisy), reference.noise_profile(noisy))

    def test_denoise_deterministic(self) -> None:
        noisy = fixture.synthesize("case-hum")["noisy"]
        profile = reference.noise_profile(noisy)
        self.assertEqual(reference.denoise(noisy, profile), reference.denoise(noisy, profile))

    def test_gain_one_is_identity(self) -> None:
        noisy = fixture.synthesize("case-quiet")["noisy"]
        profile = tuple(0.0 for _ in range(reference.BIN_COUNT))
        out = reference.denoise(noisy, profile, exponent=1.0, floor=1.0, release=1.0)
        # Hann window edge sample can be clamped by the safety guard; interior
        # must be near-identical.
        for a, b in zip(out[1:], noisy[1:]):
            self.assertAlmostEqual(a, b, delta=1e-6)

    def test_afftdn_improves_over_noisy(self) -> None:
        for item in self.items:
            noisy = item["scores"]["noisy_identity_control"]["sisdr_db"]
            restored = item["scores"]["synthetic_afftdn_reference"]["sisdr_db"]
            self.assertGreater(restored, noisy)

    def test_afftdn_improves_over_fixed_gain_baseline(self) -> None:
        for item in self.items:
            base = item["scores"]["synthetic_fixed_gain_baseline"]["sisdr_db"]
            restored = item["scores"]["synthetic_afftdn_reference"]["sisdr_db"]
            self.assertGreater(restored, base)

    def test_clean_speech_preservation(self) -> None:
        for item in self.items:
            preserved = item["scores"]["clean_speech_preservation"]["sisdr_db"]
            self.assertGreaterEqual(preserved, 20.0)

    def test_peaks_bounded(self) -> None:
        for item in self.items:
            for name in ("synthetic_afftdn_reference", "clean_speech_preservation"):
                score = item["scores"][name]
                self.assertLessEqual(score["peak"], 1.0)
                self.assertTrue(score["all_finite"])
                self.assertTrue(score["valid"])

    def test_stoi_style_range(self) -> None:
        for item in self.items:
            for name in item["scores"]:
                score = item["scores"][name]["stoi_style"]["score"]
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

    def test_stoi_style_method_labeled(self) -> None:
        for item in self.items:
            method = item["scores"]["synthetic_afftdn_reference"]["stoi_style"]["method"]
            self.assertEqual(method, "nonstandard_band_cosine_surrogate_not_stoi")

    def test_invalid_output_rejected(self) -> None:
        for item in self.items:
            control = item["invalid_output_control"]
            self.assertFalse(control["accepted"])
            self.assertFalse(control["missing_result_promoted"])

    def test_missing_result_not_promoted(self) -> None:
        report = reference.build_report()
        self.assertTrue(report["no_missing_result_promoted"])
        self.assertFalse(report["failure_controls"]["missing_result_promoted"])

    def test_frame_processor_accepts_full_stream(self) -> None:
        data = fixture.synthesize("case-quiet")
        restored = reference.denoise(data["noisy"], reference.noise_profile(data["noisy"]))
        proc = reference.FrameProcessor(restored, reference.noise_profile(data["noisy"]))
        for seq in range(fixture.frame_count()):
            frame = tuple(data["noisy"][seq * 160:(seq + 1) * 160])
            result = proc.process(frame, 7, seq, final=seq == fixture.frame_count() - 1)
            self.assertEqual(len(result["frame"]), 160)
        self.assertTrue(proc.closed)

    def test_frame_processor_rejects_bad_epoch(self) -> None:
        data = fixture.synthesize("case-quiet")
        restored = reference.denoise(data["noisy"], reference.noise_profile(data["noisy"]))
        proc = reference.FrameProcessor(restored, reference.noise_profile(data["noisy"]))
        with self.assertRaises(ValueError):
            proc.process(tuple(data["noisy"][:160]), 8, 0)

    def test_frame_processor_rejects_wrong_length(self) -> None:
        data = fixture.synthesize("case-quiet")
        restored = reference.denoise(data["noisy"], reference.noise_profile(data["noisy"]))
        proc = reference.FrameProcessor(restored, reference.noise_profile(data["noisy"]))
        with self.assertRaises(ValueError):
            proc.process(tuple(data["noisy"][:159]), 7, 0)

    def test_frame_processor_rejects_nonfinite(self) -> None:
        data = fixture.synthesize("case-quiet")
        restored = reference.denoise(data["noisy"], reference.noise_profile(data["noisy"]))
        proc = reference.FrameProcessor(restored, reference.noise_profile(data["noisy"]))
        bad = tuple(float("nan") if i == 0 else value for i, value in enumerate(data["noisy"][:160]))
        with self.assertRaises(ValueError):
            proc.process(bad, 7, 0)

    def test_frame_processor_rejects_duplicate_sequence(self) -> None:
        data = fixture.synthesize("case-quiet")
        restored = reference.denoise(data["noisy"], reference.noise_profile(data["noisy"]))
        proc = reference.FrameProcessor(restored, reference.noise_profile(data["noisy"]))
        frame = tuple(data["noisy"][:160])
        proc.process(frame, 7, 0)
        with self.assertRaises(ValueError):
            proc.process(frame, 7, 0)

    def test_frame_processor_reset_changes_digest(self) -> None:
        data = fixture.synthesize("case-quiet")
        restored = reference.denoise(data["noisy"], reference.noise_profile(data["noisy"]))
        proc = reference.FrameProcessor(restored, reference.noise_profile(data["noisy"]))
        proc.process(tuple(data["noisy"][:160]), 7, 0)
        before = proc.digest()
        proc.reset(9)
        self.assertNotEqual(before, proc.digest())

    def test_report_canonical(self) -> None:
        text, digest = reference.canonical_report(reference.build_report())
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(len(digest), 64)
        json.loads(text)

    def test_report_repeats_identical(self) -> None:
        digests = [reference.canonical_report(reference.build_report())[1] for _ in range(3)]
        self.assertEqual(len(set(digests)), 1)

    def test_report_disposition(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertEqual(report["qualification_status"], "incomplete")
        self.assertEqual(report["decision"], "DEFER")
        self.assertFalse(report["processor_exposure"])
        self.assertFalse(report["public_surface_changed"])
        self.assertFalse(report["installed_v0_changed"])
        self.assertFalse(report["ffmpeg_available"])
        self.assertFalse(report["numeric_ffmpeg_parity_claimed"])
        self.assertFalse(report["human_listening_used"])
        self.assertFalse(report["target_device_measured"])

    def test_unpaired_proxy_labeled(self) -> None:
        report = reference.build_report()
        proxy = report["unpaired_predictive_proxy"]
        self.assertEqual(proxy["label"], "predictive_proxy_not_quality_not_listening")
        self.assertFalse(proxy["items"][0]["human_listening"])
        self.assertFalse(proxy["items"][0]["clean_reference_available"])

    def test_acceptance_profile_complete(self) -> None:
        report = reference.build_report()
        profile = report["acceptance_profile"]
        self.assertEqual(profile["profile"], "enhancement")
        for key in ("identity_noisy_control", "documented_synthetic_baseline", "paired_si_sdr",
                    "paired_stoi_style", "clean_speech_preservation", "peaks_checked",
                    "invalid_outputs_rejected", "unpaired_predictive_proxy_separately_labeled",
                    "alignment_and_state_declared", "unpaced_synthetic_timing_labeled",
                    "no_authoritative_ns_baseline_claim", "no_human_listening",
                    "no_target_device_measurement"):
            self.assertTrue(profile[key], key)

    def test_crosscheck_is_not_parity(self) -> None:
        payload = reference.crosscheck_payload()
        self.assertFalse(payload["numeric_ffmpeg_parity"])
        self.assertEqual(payload["kind"], "deterministic_replay_not_external_tool")

    def test_cli_sources(self) -> None:
        payload = cli.sources_payload()
        self.assertIn("sources", payload)
        self.assertIn("local_artifacts", payload)
        self.assertEqual(payload["counts"]["sources"], len(fixture.SOURCE_PINS))

    def test_spdx_headers_present(self) -> None:
        for path in TASK.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# SPDX-FileCopyrightText:"))
            self.assertIn("# " + SPDX_TAG + " Apache-2.0", text.splitlines()[1])

    def test_no_literal_spdx_in_python_strings(self) -> None:
        literal = "SPDX" + "-License-Identifier"
        for path in TASK.glob("*.py"):
            lines = path.read_text(encoding="utf-8").splitlines()
            body = "\n".join(lines[2:])
            self.assertNotIn(literal, body, path.name)

    def test_json_escaped_license_key(self) -> None:
        for path in TASK.glob("*.json"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("SPDX\\u002dLicense-Identifier", text, path.name)

    def test_timing_not_measured(self) -> None:
        report = reference.build_report()
        self.assertFalse(report["timing"]["paced_or_measured"])
        self.assertIsNone(report["timing"]["measured_seconds"])
        self.assertIsNone(report["timing"]["target_device"])

    def test_alignment_declared(self) -> None:
        report = reference.build_report()
        self.assertEqual(report["alignment_and_state"]["lookahead_samples"], 96)
        self.assertFalse(report["alignment_and_state"]["causal_streaming_claim"])


if __name__ == "__main__":
    unittest.main()
