# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Unit and evidence-bundle tests for the proposal-only synthetic NS package."""

from __future__ import annotations

import math
import os
from pathlib import Path
import subprocess
import sys
import unittest

import check_licensing
import fixture
import reference
import run
import scorer
import verify

ROOT = Path(__file__).resolve().parent


class FixtureTests(unittest.TestCase):
    def test_fixture_deterministic(self):
        first, first_pins = fixture.cohort()
        second, second_pins = fixture.cohort()
        self.assertEqual(first_pins, second_pins)
        for left, right in zip(first, second):
            self.assertEqual(left["digests"], right["digests"])

    def test_fixture_digests_are_64_hex(self):
        _, pins = fixture.cohort()
        self.assertEqual(set(pins), {"clean", "mild-snr+6.noisy", "mild-snr+6.noise",
                                     "hard-snr-3.noisy", "hard-snr-3.noise"})
        for value in pins.values():
            self.assertEqual(len(value), 64)
            self.assertTrue(all(character in "0123456789abcdef" for character in value))

    def test_fixture_lengths_and_frame_grid(self):
        items, _ = fixture.cohort()
        for item in items:
            self.assertEqual(len(item["clean"]), fixture.SAMPLES)
            self.assertEqual(len(item["noisy"]), fixture.SAMPLES)
            self.assertEqual(len(fixture.frame_view(item["noisy"])), fixture.SAMPLES // fixture.FRAME_SAMPLES)

    def test_fixture_finite(self):
        items, _ = fixture.cohort()
        for item in items:
            self.assertTrue(all(math.isfinite(value) for value in item["clean"] + item["noisy"] + item["noise"]))

    def test_calibration_prefix_is_silent_in_clean(self):
        items, _ = fixture.cohort()
        self.assertEqual(items[0]["clean"][:fixture.NOISE_PREFIX_SAMPLES],
                         [0.0] * fixture.NOISE_PREFIX_SAMPLES)

    def test_conditions_differ(self):
        items, _ = fixture.cohort()
        self.assertNotEqual(items[0]["digests"]["noisy"], items[1]["digests"]["noisy"])
        self.assertNotEqual(items[0]["snr_db"], items[1]["snr_db"])

    def test_frame_view_rejects_partial(self):
        with self.assertRaises(ValueError):
            fixture.frame_view([0.0] * (fixture.FRAME_SAMPLES + 1))

    def test_unpaired_item_has_no_reference(self):
        item = fixture.unpaired()
        self.assertFalse(item["has_clean_reference"])
        self.assertEqual(len(item["noisy"]), fixture.SAMPLES)
        self.assertEqual(len(item["digest"]), 64)


class ScorerTests(unittest.TestCase):
    def setUp(self):
        self.clean = [0.0, 0.7, -0.4, 0.2, 0.0, -0.9, 0.35, 0.1] * 100

    def test_si_sdr_scale_invariant(self):
        score, reason = scorer.si_sdr(self.clean, [0.3 * value for value in self.clean])
        self.assertIsNone(reason)
        self.assertGreater(score, 300.0)

    def test_si_sdr_identity_is_undefined(self):
        score, reason = scorer.si_sdr(self.clean, self.clean)
        self.assertIsNone(score)
        self.assertEqual(reason, "perfect_reconstruction")

    def test_si_sdr_noisy_lower_than_clean(self):
        noisy = [value + 0.05 * math.sin(index) for index, value in enumerate(self.clean)]
        clean_score, _ = scorer.si_sdr(self.clean, self.clean)
        noisy_score, _ = scorer.si_sdr(self.clean, noisy)
        self.assertIsNone(clean_score)
        self.assertIsNotNone(noisy_score)

    def test_si_sdr_rejects_nonfinite(self):
        bad = list(self.clean)
        bad[3] = float("inf")
        self.assertEqual(scorer.si_sdr(self.clean, bad), (None, "invalid_input"))

    def test_si_sdr_rejects_length_mismatch(self):
        self.assertEqual(scorer.si_sdr(self.clean, self.clean[:-1]), (None, "invalid_input"))

    def test_si_sdr_rejects_zero_reference(self):
        self.assertEqual(scorer.si_sdr([0.0] * 64, [1.0] * 64), (None, "zero_reference_energy"))

    def test_si_sdr_improvement_uses_paired_noisy(self):
        noisy = [value + 0.1 * math.cos(index) for index, value in enumerate(self.clean)]
        delta, reason = scorer.si_sdr_improvement(self.clean, self.clean, noisy)
        self.assertIsNotNone(reason)
        self.assertIsNone(delta)

    def test_stoi_style_identity(self):
        score, reason = scorer.stoi_style(self.clean, self.clean)
        self.assertIsNone(reason)
        self.assertEqual(score, 1.0)

    def test_stoi_style_noise_degrades(self):
        item = fixture.cohort()[0][0]
        clean_score, _ = scorer.stoi_style(item["clean"], item["clean"])
        noisy_score, noisy_reason = scorer.stoi_style(item["clean"], item["noisy"])
        self.assertIsNone(noisy_reason)
        self.assertLess(noisy_score, clean_score)

    def test_stoi_style_deterministic(self):
        first, _ = scorer.stoi_style(self.clean, [0.8 * value for value in self.clean])
        second, _ = scorer.stoi_style(self.clean, [0.8 * value for value in self.clean])
        self.assertEqual(first, second)

    def test_stoi_style_rejects_invalid(self):
        self.assertEqual(scorer.stoi_style(self.clean, [float("nan")] * len(self.clean)),
                         (None, "invalid_input"))

    def test_stoi_style_rejects_zero_reference(self):
        self.assertEqual(scorer.stoi_style([0.0] * 1024, [1.0] * 1024),
                         (None, "zero_reference_energy"))

    def test_stoi_style_rejects_short_input(self):
        self.assertEqual(scorer.stoi_style([1.0] * 32, [1.0] * 32), (None, "too_short"))


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items, cls.pins = fixture.cohort()

    def frame(self, item_index=0, position=0):
        return fixture.frame_view(self.items[item_index]["noisy"])[position]

    def test_default_config_frozen(self):
        config = reference.validate_config()
        self.assertEqual(config["fft_size"], reference.FFT_SIZE)
        self.assertEqual(config["noise_calibration_frames"], 10)

    def test_config_rejects_unknown_key(self):
        with self.assertRaises(reference.ReferenceError):
            reference.validate_config({"fft_size": 256})

    def test_config_rejects_range(self):
        config = dict(reference.DEFAULT_CONFIG, decision_alpha=1.5)
        with self.assertRaises(reference.ReferenceError):
            reference.validate_config(config)

    def test_reset_returns_epoch(self):
        session = reference.Session()
        self.assertEqual(session.reset(4)["epoch"], 4)
        self.assertEqual(session.position, 0)

    def test_reset_rejects_invalid_epoch(self):
        with self.assertRaises(reference.ReferenceError):
            reference.Session().reset(0)

    def test_framewise_equals_stream(self):
        samples = self.items[0]["noisy"]
        stream = reference.render(reference.CANDIDATE_VARIANT, samples)
        session = reference.Session()
        collected = []
        for position, frame in enumerate(fixture.frame_view(samples)):
            result = session.process_frame(frame, 1, position, reference.CANDIDATE_VARIANT)
            self.assertEqual(result["status"], "ok")
            collected.extend(result["samples"])
        self.assertEqual(stream["digest"], reference.digest_values(collected))

    def test_identity_control_bit_exact(self):
        samples = self.items[0]["noisy"]
        rendered = reference.render(reference.CONTROL_VARIANT, samples)
        self.assertEqual(rendered["digest"], reference.digest_values(samples))

    def test_candidate_output_finite(self):
        rendered = reference.render(reference.CANDIDATE_VARIANT, self.items[0]["noisy"])
        self.assertEqual(rendered["status"], "ok")
        self.assertTrue(rendered["finite"])

    def test_candidate_improves_si_sdr_mild(self):
        item = self.items[0]
        rendered = reference.render(reference.CANDIDATE_VARIANT, item["noisy"])
        scored = reference.score_variant(item["clean"], item["noisy"], rendered)
        self.assertEqual(scored["status"], "scored")
        self.assertGreater(scored["metrics"]["delta_si_sdr_db"], 0.0)

    def test_candidate_improves_si_sdr_hard(self):
        item = self.items[1]
        rendered = reference.render(reference.CANDIDATE_VARIANT, item["noisy"])
        scored = reference.score_variant(item["clean"], item["noisy"], rendered)
        self.assertEqual(scored["status"], "scored")
        self.assertGreater(scored["metrics"]["delta_si_sdr_db"], 0.0)

    def test_candidate_stoi_delta_reported_with_sign(self):
        for item in self.items:
            rendered = reference.render(reference.CANDIDATE_VARIANT, item["noisy"])
            scored = reference.score_variant(item["clean"], item["noisy"], rendered)
            self.assertIsInstance(scored["metrics"]["delta_stoi_style"], float)
            self.assertTrue(math.isfinite(scored["metrics"]["delta_stoi_style"]))

    def test_adverse_results_are_retained(self):
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertTrue(report["adverse_results"])
        self.assertTrue(all(row["classification"].startswith("adverse") for row in report["adverse_results"]))

    def test_baseline_is_scored(self):
        item = self.items[0]
        rendered = reference.render(reference.BASELINE_VARIANT, item["noisy"])
        scored = reference.score_variant(item["clean"], item["noisy"], rendered)
        self.assertEqual(scored["status"], "scored")
        self.assertIsNotNone(scored["metrics"]["delta_stoi_style"])

    def test_clean_preservation_finite(self):
        clean = self.items[0]["clean"]
        for variant in reference.PROCESS_VARIANTS:
            rendered = reference.render(variant, clean)
            self.assertEqual(rendered["status"], "ok")
            self.assertTrue(rendered["finite"])

    def test_level_ablation_is_ordered(self):
        item = self.items[0]
        attenuations = {}
        for variant in ("webrtc_ns_l1", reference.CANDIDATE_VARIANT, "webrtc_ns_l3"):
            rendered = reference.render(variant, item["noisy"])
            attenuations[variant] = reference.noise_prefix_attenuation(item["noisy"], rendered["samples"])
        self.assertGreater(attenuations["webrtc_ns_l1"], attenuations[reference.CANDIDATE_VARIANT])
        self.assertGreater(attenuations[reference.CANDIDATE_VARIANT], attenuations["webrtc_ns_l3"])

    def test_output_peaks_below_clipping(self):
        for item in self.items:
            for variant in reference.PROCESS_VARIANTS:
                rendered = reference.render(variant, item["noisy"])
                self.assertLess(rendered["peak"], 1.0)

    def test_zero_added_delay_impulse(self):
        impulse = [0.0] * 320
        impulse[0] = 0.5
        rendered = reference.render(reference.CANDIDATE_VARIANT, impulse)
        peak_index = max(range(len(rendered["samples"])), key=lambda index: abs(rendered["samples"][index]))
        self.assertEqual(peak_index, 0)

    def test_silence_stays_silent(self):
        rendered = reference.render(reference.CANDIDATE_VARIANT, [0.0] * 320)
        self.assertEqual(rendered["peak"], 0.0)

    def test_independent_sessions(self):
        first = reference.render(reference.CANDIDATE_VARIANT, self.items[0]["noisy"])
        second = reference.render(reference.CANDIDATE_VARIANT, self.items[1]["noisy"])
        self.assertNotEqual(first["digest"], second["digest"])

    def test_reset_replays(self):
        samples = self.items[0]["noisy"][:3 * fixture.FRAME_SAMPLES]
        first = reference.render(reference.CANDIDATE_VARIANT, samples, epoch=9)
        session = reference.Session(epoch=9)
        collected = []
        for position, frame in enumerate(fixture.frame_view(samples)):
            result = session.process_frame(frame, 9, position, reference.CANDIDATE_VARIANT)
            collected.extend(result["samples"])
        self.assertEqual(first["digest"], reference.digest_values(collected))

    def test_reject_wrong_shape(self):
        result = reference.Session().process_frame([0.0] * 159, 1, 0)
        self.assertEqual(result["status"], "rejected_shape")

    def test_reject_nonfinite_input(self):
        result = reference.Session().process_frame([float("nan")] + [0.0] * 159, 1, 0)
        self.assertEqual(result["status"], "rejected_nonfinite")

    def test_reject_wrong_type(self):
        result = reference.Session().process_frame(["x"] + [0.0] * 159, 1, 0)
        self.assertEqual(result["status"], "rejected_type")

    def test_reject_out_of_range(self):
        result = reference.Session().process_frame([9.0] + [0.0] * 159, 1, 0)
        self.assertEqual(result["status"], "rejected_range")

    def test_reject_stale_epoch(self):
        result = reference.Session().process_frame([0.0] * 160, 2, 0)
        self.assertEqual(result["status"], "rejected_epoch")

    def test_reject_stale_position(self):
        result = reference.Session().process_frame([0.0] * 160, 1, 3)
        self.assertEqual(result["status"], "rejected_position")

    def test_reject_unknown_variant(self):
        result = reference.Session().process_frame([0.0] * 160, 1, 0, "webrtc_runtime")
        self.assertEqual(result["status"], "rejected_variant")

    def test_reject_closed_session(self):
        session = reference.Session()
        session.close()
        self.assertEqual(session.process_frame([0.0] * 160, 1, 0)["status"], "rejected_closed")

    def test_rejections_do_not_mutate_state(self):
        session = reference.Session()
        for _ in range(5):
            session.process_frame([0.0] * 159, 1, 0)
        self.assertEqual(session.position, 0)
        self.assertEqual(session.invalid_count, 5)
        self.assertEqual(session.noise_psd, [0.0] * reference.FFT_BINS)

    def test_invalid_output_is_rejected_and_unscored(self):
        session = reference.Session()
        session.inject_nonfinite = True
        result = session.process_frame([0.01] * 160, 1, 0)
        self.assertEqual(result["status"], "invalid_output_nonfinite")
        scored = reference.score_variant([0.01] * 160, [0.01] * 160, result)
        self.assertEqual(scored["status"], "invalid_output")
        self.assertIsNone(scored["metrics"])

    def test_missing_input_blocked(self):
        rendered = reference.render(reference.CANDIDATE_VARIANT, None)
        self.assertEqual(rendered["status"], "blocked")
        scored = reference.score_variant([0.0], [0.0], rendered)
        self.assertEqual(scored["status"], "blocked")

    def test_missing_reference_blocked(self):
        scored = reference.score_variant(None, [0.0] * 160, {"status": "ok"})
        self.assertEqual(scored["status"], "blocked")
        self.assertIsNone(scored["metrics"])

    def test_drain_is_empty(self):
        self.assertEqual(reference.Session().drain()["frames"], 0)

    def test_memory_is_analytic(self):
        self.assertEqual(reference.Session().memory_floats, 3 * reference.FFT_BINS + 2)


class AdapterAndReportTests(unittest.TestCase):
    def test_adapter_inspect_is_dev_only(self):
        request = {
            "protocol_version": 1,
            "operation": "inspect",
            "candidate_ref": {"kind": "synthetic-candidate", "id": "webrtc-apm-ns-synthetic-v1", "revision": 1},
            "adapter_ref": {"kind": "developer-adapter", "id": run.IDENTITY, "revision": 1},
            "configuration": {"profile": reference.TASK_ID},
        }
        result = run.inspect(request)
        self.assertFalse(result["expose_as_processor"])
        self.assertEqual(result["promotion"], "DEFER")

    def test_adapter_rejects_invalid_request(self):
        with self.assertRaises(run.RequestError):
            run.validate_request({"protocol_version": 2}, "inspect")

    def test_bundle_validation_explicit(self):
        validation = run.bundle_validation()
        self.assertTrue(validation["all_explicit"])
        self.assertTrue(all(validation["checks"].values()))

    def test_report_is_strict_json(self):
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertEqual(report["task"], reference.TASK_ID)

    def test_report_canonical_bytes(self):
        report = reference.read_strict_json(ROOT / "report.json")
        text, digest = reference.canonical_report(report)
        self.assertEqual((ROOT / "report.json").read_bytes(), text.encode("utf-8") + b"\n")
        self.assertEqual((ROOT / "report.json.sha256").read_text(encoding="ascii").strip(), digest)

    def test_report_status_defer(self):
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertEqual(report["status"], "proposal_only_not_qualified")
        self.assertEqual(report["completeness"], "incomplete")
        self.assertEqual(report["decision"]["disposition"], "DEFER")
        self.assertTrue(all(gate["status"] == "not_met" for gate in report["gates"]))

    def test_report_all_paired_results_scored(self):
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertEqual(len(report["paired_results"]), 2 * len(reference.PROCESS_VARIANTS))
        self.assertTrue(all(row["status"] == "scored" for row in report["paired_results"]))

    def test_report_fixture_pins(self):
        report = reference.read_strict_json(ROOT / "report.json")
        _, pins = fixture.cohort()
        self.assertEqual(report["fixture"]["digests"], pins)

    def test_report_artifact_pins(self):
        report = reference.read_strict_json(ROOT / "report.json")
        for name, digest in report["artifact_pins"].items():
            self.assertEqual(reference.digest_file(ROOT / name), digest)

    def test_sources_manifest_matches_file(self):
        self.assertEqual((ROOT / "SOURCES.sha256").read_text(encoding="utf-8"), run.source_manifest())

    def test_report_regeneration_byte_identical(self):
        original = (ROOT / "report.json").read_bytes()
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, "run.py", "--report"], cwd=ROOT, env=environment,
                                capture_output=True, text=True, check=True)
        self.assertEqual(len(result.stdout.strip()), 64)
        self.assertEqual((ROOT / "report.json").read_bytes(), original)

    def test_unpaired_screen_is_separate(self):
        report = reference.read_strict_json(ROOT / "report.json")
        screen = report["unpaired_predictive_screen"]
        self.assertFalse(screen["has_clean_reference"])
        self.assertFalse(screen["human_listening"])
        self.assertFalse(screen["qualifies_candidate"])

    def test_contract_adapter_provider_consistency(self):
        contract = reference.read_strict_json(ROOT / "contract.json")
        adapter = reference.read_strict_json(ROOT / "adapter.json")
        provider = reference.read_strict_json(ROOT / "provider.json")
        self.assertEqual(contract["status"], "proposal_only_not_qualified")
        self.assertFalse(contract["public_surface_change"])
        self.assertTrue(adapter["registration"]["unregistered"])
        self.assertFalse(provider["registered"])
        self.assertFalse(provider["enabled_by_default"])

    def test_no_public_surface_change_in_scope(self):
        report = reference.read_strict_json(ROOT / "report.json")
        self.assertFalse(report["scope"]["public_api_abi_descriptor_registry_defaults_changed"])
        self.assertFalse(report["scope"]["installed_behavior"].startswith("changed"))

    def test_licensing_script_green(self):
        self.assertEqual(check_licensing.main(), 0)

    def test_verify_script_green(self):
        self.assertEqual(verify.main(), 0)


if __name__ == "__main__":
    unittest.main()
