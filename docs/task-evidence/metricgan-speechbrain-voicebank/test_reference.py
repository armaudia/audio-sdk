# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance tests for the task-local MetricGAN+ SpeechBrain VoiceBank reference."""

from __future__ import annotations

import functools
import hashlib
import json
import math
import unittest
from pathlib import Path

import reference
import run as cli

HERE = Path(__file__).resolve().parent


@functools.lru_cache(maxsize=1)
def report() -> dict:
    return reference.build_report()


class BoundaryTests(unittest.TestCase):
    def test_v0_geometry_preserved(self) -> None:
        self.assertEqual(report()["format"], reference.FORMAT)
        self.assertEqual(report()["format"]["frame_samples"], 160)
        self.assertEqual(report()["format"]["sample_rate_hz"], 16000)
        self.assertEqual(report()["format"]["channels"], 1)
        self.assertEqual(report()["format"]["sample_format"], "f32")

    def test_boundary_flags_all_false(self) -> None:
        boundary = report()["boundary"]
        self.assertFalse(boundary["registered"])
        self.assertFalse(boundary["enabled_by_default"])
        self.assertFalse(boundary["default_selected"])
        self.assertFalse(boundary["public_api_abi_change"])
        self.assertFalse(boundary["provider_registration"])
        self.assertFalse(boundary["processor_exposure"])
        self.assertFalse(boundary["shared_build_or_ci_change"])
        self.assertEqual(boundary["descriptor_settings"], {})
        self.assertTrue(boundary["installed_v0_geometry_preserved"])

    def test_disposition_is_defer_incomplete_not_qualified(self) -> None:
        self.assertEqual(report()["decision"], "DEFER")
        self.assertEqual(report()["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(report()["evidence_status"], "incomplete")
        self.assertEqual(report()["qualification_status"], "not_qualified")
        self.assertFalse(report()["readiness"]["qualifies"])
        self.assertFalse(report()["readiness"]["missing_result_promoted"])

    def test_no_real_world_claim(self) -> None:
        self.assertTrue(all(value is False for value in report()["claims"].values()))
        self.assertTrue(all(value is False for value in report()["scope"].values()
                            if isinstance(value, bool) and value is not True))
        self.assertFalse(report()["extra"]["live_default"])
        self.assertFalse(report()["extra"]["task_board_handoff_written"])

    def test_every_gate_is_blocked(self) -> None:
        gates = report()["gates"]
        self.assertGreaterEqual(len(gates), 11)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["blocked_by"])
            self.assertTrue(gate["reopen_condition"])


class FixtureTests(unittest.TestCase):
    def test_conditions_are_frozen_and_deterministic(self) -> None:
        first = reference.fixture("voiced_steady")
        second = reference.fixture("voiced_steady")
        self.assertEqual(first["meta"], second["meta"])
        self.assertEqual(len(first["clean"]), reference.SAMPLES)
        self.assertEqual(len(first["noisy"]), reference.SAMPLES)
        self.assertEqual(set(report()["conditions"]), set(reference.CONDITIONS))

    def test_fixture_pair_has_expected_snr(self) -> None:
        frozen = reference.fixture("voiced_steady")
        measured, reason = reference.direct_snr_db(frozen["clean"], frozen["noisy"])
        self.assertIsNone(reason)
        self.assertAlmostEqual(measured, 5.0, delta=0.05)

    def test_silence_control_is_degenerate_not_scored(self) -> None:
        metrics = report()["conditions"]["silence_control"]["input_metrics"]
        self.assertIsNone(metrics["stoi"])
        self.assertIsNone(metrics["si_sdr_db"])
        self.assertEqual(metrics["stoi_status"], "insufficient_active_speech")
        self.assertTrue(report()["adverse"]["validity"]["silence_degenerate"])

    def test_stoi_scorer_identity_and_monotonicity(self) -> None:
        clean = reference.fixture("voiced_steady")["clean"]
        value, reason = reference.scorer.stoi(clean, clean, reference.SAMPLE_RATE)
        self.assertIsNone(reason)
        self.assertAlmostEqual(value, 1.0, places=9)
        scores = []
        for snr in (20.0, 6.0, 0.0):
            noisy = [c + 0.05 * math.sin(2 * math.pi * 997 * index / len(clean)) *
                     (10 ** ((6.0 - snr) / 20.0))
                     for index, c in enumerate(clean)]
            score, reason = reference.scorer.stoi(clean, noisy, reference.SAMPLE_RATE)
            self.assertIsNone(reason)
            scores.append(score)
        self.assertGreater(scores[0], scores[1])
        self.assertGreater(scores[1], scores[2])


class SurrogateTests(unittest.TestCase):
    def test_identity_variant_is_exact_passthrough(self) -> None:
        frozen = reference.fixture("voiced_modulated")
        self.assertEqual(reference.apply_variant("identity_noisy", frozen["noisy"]),
                         frozen["noisy"])
        entry = report()["conditions"]["voiced_modulated"]["variants"]["identity_noisy"]
        self.assertEqual(entry["delta_vs_identity_noisy"]["stoi"], 0.0)
        self.assertEqual(entry["delta_vs_identity_noisy"]["direct_snr_db"], 0.0)

    def test_peak_normalizers_reach_unit_peak(self) -> None:
        for condition in reference.SCORED_CONDITIONS:
            noisy = reference.fixture(condition)["noisy"]
            for variant in ("level_only_peak_normalized", "peak_normalized_mask"):
                output = reference.apply_variant(variant, noisy)
                self.assertAlmostEqual(max(abs(value) for value in output), 1.0, places=9)

    def test_level_only_normalization_is_content_preserving(self) -> None:
        for condition in reference.SCORED_CONDITIONS:
            delta = report()["conditions"][condition]["variants"][
                "level_only_peak_normalized"]["delta_vs_identity_noisy"]
            self.assertEqual(delta["si_sdr_db"], 0.0)
            self.assertEqual(delta["stoi"], 0.0)
        findings = report()["enhancement_profile"]["mechanism_findings"]
        self.assertLess(findings["unit_peak_normalization_pattern"]
                        ["peak_only_mean_delta_snr_db"], -5.0)

    def test_rms_match_changes_level_only(self) -> None:
        findings = report()["enhancement_profile"]["mechanism_findings"]
        self.assertEqual(findings["rms_match_recovers_level_not_content"]
                         ["max_abs_si_sdr_change_db"], 0.0)
        self.assertEqual(findings["rms_match_recovers_level_not_content"]
                         ["max_abs_stoi_change"], 0.0)
        self.assertGreater(
            findings["rms_match_recovers_level_not_content"]["rms_matched_mean_delta_snr_db"],
            findings["rms_match_recovers_level_not_content"]["candidate_mean_delta_snr_db"])

    def test_outputs_are_finite_same_length_and_accounted(self) -> None:
        for condition, variants in report()["conditions"].items():
            for name, entry in variants["variants"].items():
                metrics = entry["metrics"]
                self.assertTrue(metrics["finite"], (condition, name))
                self.assertEqual(metrics["samples"], reference.SAMPLES)
                if metrics["stoi"] is None:
                    self.assertIsNotNone(metrics["stoi_status"])
                else:
                    self.assertTrue(0.0 <= metrics["stoi"] <= 1.0)
        peaks = report()["enhancement_profile"]["peaks_and_invalid_outputs"]
        self.assertEqual(peaks["invalid_outputs"], 0)
        self.assertGreaterEqual(peaks["clipped_outputs"], 0)

    def test_clean_preservation_is_measured_for_declared_variants(self) -> None:
        preservation = report()["clean_preservation"]
        self.assertEqual(set(preservation), set(reference.SCORED_CONDITIONS))
        for condition, entry in preservation.items():
            self.assertEqual(set(entry["variants"]),
                             set(reference.CLEAN_PRESERVATION_VARIANTS))
            for variant, result in entry["variants"].items():
                if result["metrics"]["stoi"] is not None:
                    self.assertTrue(0.0 <= result["metrics"]["stoi"] <= 1.0,
                                    (condition, variant))


class AdverseTests(unittest.TestCase):
    def test_configuration_fails_closed(self) -> None:
        cases = report()["adverse"]["config_rejections"]
        for name, case in cases.items():
            self.assertTrue(case["status"].startswith("rejected_"), name)
            self.assertFalse(case["controller_created"], name)

    def test_frame_and_lifecycle_fail_closed(self) -> None:
        adverse = report()["adverse"]
        for name in ("empty", "nonfinite", "wrong_rate", "stereo", "oversize"):
            self.assertTrue(adverse["frame_rejections"][name].startswith("rejected_"), name)
        self.assertTrue(adverse["frame_rejections"]["dsp_state_unchanged"])
        self.assertEqual(adverse["lifecycle"]["finish_then_process"], "rejected_session")
        self.assertEqual(adverse["lifecycle"]["close_then_process"], "rejected_session")
        validity = adverse["validity"]
        self.assertTrue(validity["invalid_excluded"])
        self.assertTrue(validity["missing_result_not_promoted"])
        self.assertTrue(validity["clipped_input_recorded"])

    def test_silence_passes_through_without_fake_metrics(self) -> None:
        harness = reference.ReferenceHarness(
            {"variant": "peak_normalized_mask", "gain_floor": reference.MASK_GAIN_FLOOR,
             "noise_fraction": reference.MASK_NOISE_FRACTION})
        output = harness.process([0.0] * 1024)
        self.assertTrue(all(value == 0.0 for value in output))

    def test_caller_asset_boundary_never_loads(self) -> None:
        probe = report()["caller_asset_boundary"]["probe"]
        self.assertEqual(probe["absent"]["status"], "asset_unavailable")
        self.assertEqual(probe["identity_undeclared"]["status"], "asset_identity_undeclared")
        self.assertEqual(probe["digest_mismatch"]["status"], "asset_digest_mismatch")
        self.assertEqual(probe["load_requested"]["status"],
                         "asset_load_not_permitted_in_task")
        self.assertEqual(probe["declared_but_unverified"]["status"],
                         "descriptor_accepted_no_bytes_read")
        for outcome in probe.values():
            self.assertFalse(outcome["loaded"])
            self.assertFalse(outcome["executed"])
        boundary = report()["caller_asset_boundary"]
        self.assertFalse(boundary["loaded"])
        self.assertFalse(boundary["executed"])
        self.assertTrue(boundary["surrogate_substituted"])
        self.assertFalse(boundary["runtime_identity"]["installed_in_this_worktree"])
        self.assertFalse(boundary["corpus_identity"]["download_attempted"])


class ProvenanceTests(unittest.TestCase):
    def test_historical_numbers_are_quarantined(self) -> None:
        provenance = report()["historical_provenance"]
        self.assertTrue(provenance["status"].startswith("recorded_provenance_only"))
        self.assertEqual(provenance["recorded_dns_pilot"]["mean_delta_si_sdr_db"], -3.538)
        self.assertEqual(provenance["recorded_dns_pilot"]["mean_delta_snr_db"], -10.505)
        self.assertEqual(provenance["upstream_model_card_claim"]["voicebank_test_pesq"], 3.15)
        self.assertIn("not_reproduced", provenance["upstream_model_card_claim"]["status"])

    def test_external_blockers_name_exact_requirements(self) -> None:
        readiness = report()["readiness"]
        identifiers = {blocker["id"] for blocker in readiness["external_blockers"]}
        self.assertEqual(identifiers, {
            "checkpoint_assets_absent", "pinned_runtime_absent",
            "corpus_provenance_uncleared", "recorded_quality_result_negative",
            "installed_adapter_not_implemented"})
        text = json.dumps(readiness)
        for token in ("VoiceBank", "CC BY 4.0", "ODC-By", "SHA-256", "SpeechBrain"):
            self.assertIn(token, text)
        self.assertFalse(readiness["asset_availability"]["checkpoint_bytes_present"])

    def test_asset_identity_matches_pinned_evidence(self) -> None:
        asset = report()["caller_asset_boundary"]["asset_identity"]
        self.assertEqual(asset["checkpoint_sha256"], reference.CHECKPOINT_SHA256)
        self.assertEqual(asset["model_repo_revision"], reference.MODEL_REPO_REVISION)
        self.assertEqual(asset["config_sha256"], reference.CONFIG_SHA256)
        self.assertEqual(asset["model_card_license"], "Apache-2.0")
        self.assertIn("bytes_absent_not_verified", asset["verification"])


class ReproductionTests(unittest.TestCase):
    def test_report_is_canonical_and_repeatable(self) -> None:
        payload = reference.canonical_report_bytes(report())
        self.assertTrue(payload.endswith(b"\n"))
        parsed = json.loads(payload.decode("utf-8"))

        def has_negative_zero(value) -> bool:
            if isinstance(value, float):
                return value == 0.0 and math.copysign(1.0, value) < 0.0
            if isinstance(value, dict):
                return any(has_negative_zero(item) for item in value.values())
            if isinstance(value, list):
                return any(has_negative_zero(item) for item in value)
            return False

        self.assertFalse(has_negative_zero(parsed))
        again = reference.canonical_report_bytes(reference.build_report())
        self.assertEqual(hashlib.sha256(payload).hexdigest(),
                         hashlib.sha256(again).hexdigest())

    def test_on_disk_report_matches_regeneration(self) -> None:
        payload = (HERE / "report.json").read_bytes()
        self.assertEqual(payload, reference.canonical_report_bytes(report()))
        sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
        self.assertEqual(sidecar, hashlib.sha256(payload).hexdigest() + "  report.json")

    def test_sources_manifest_pins_every_local_artifact(self) -> None:
        manifest = cli.manifest_bytes()
        self.assertEqual(manifest, (HERE / "SOURCES.sha256").read_bytes())
        lines = manifest.decode("utf-8").splitlines()[1:]
        pinned = {line.split("  ", 1)[1] for line in lines}
        prefix = f"worktree:docs/task-evidence/{reference.SLUG}/"
        for name in reference.LOCAL_FILES:
            self.assertIn(prefix + name, pinned)
        self.assertNotIn(prefix + "SOURCES.sha256", pinned)
        self.assertEqual(len(pinned),
                         len(reference.SOURCE_PIN_PATHS) + len(reference.BOUNDARY_PIN_PATHS)
                         + len(reference.LOCAL_FILES))


if __name__ == "__main__":
    unittest.main()
