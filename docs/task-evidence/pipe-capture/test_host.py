# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Offline acceptance tests for the frozen SDK-PIPE-CAPTURE fixture."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import generate_report
import host

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]

RECIPE_FILE_DIGEST = "08d5e1fa42327f1830e623c27ccb5ef0b03d40ca84cc7613342d1e3fa8cf8141"
FIXTURES_FILE_DIGEST = "23b4d9e589239a8662d28e3c8dbc11371d22ebcbcc4de80d37217936dcc49e30"
REPORT_FILE_DIGEST = "30734c321a8150cc2adea332e3b2c8daeeea24eb64b733fdfc0d0efd00609a37"
RECIPE_DIGEST = "1766bbc2ff55037fb0502f221cbf6ece429759a4031cd042e3a9356115345f67"
FIXTURES_DIGEST = "1dfc172da444dce16b30056738e76e700ecd0640ff12a4b9cf162e87b4181868"
REPEAT_DIGEST = "3c5d380168a7ed221307c383e0513e24c2b830db9de207a7327fcee685bdd8f6"
MAIN_VARIANTS = ["identity", "highpass_only", "ns_only", "limiter_only",
                 "basic_chain", "voice_focus"]


class PipeCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.recipe = host.load_json("recipe.json")
        cls.fixtures = host.load_json("fixtures.json")
        cls.report = json.loads((HERE / "report.json").read_text(encoding="ascii"))

    def test_01_frozen_file_and_canonical_digests(self) -> None:
        self.assertEqual(host.sha256((HERE / "recipe.json").read_bytes()), RECIPE_FILE_DIGEST)
        self.assertEqual(host.sha256((HERE / "fixtures.json").read_bytes()), FIXTURES_FILE_DIGEST)
        self.assertEqual(host.sha256((HERE / "report.json").read_bytes()), REPORT_FILE_DIGEST)
        self.assertEqual(self.report["recipe_digest"], RECIPE_DIGEST)
        self.assertEqual(self.report["fixtures_digest"], FIXTURES_DIGEST)
        self.assertEqual(host.canonical_digest(self.recipe), RECIPE_DIGEST)
        self.assertEqual(host.canonical_digest(self.fixtures), FIXTURES_DIGEST)

    def test_02_report_sidecar_matches_report(self) -> None:
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{REPORT_FILE_DIGEST}  report.json\n")

    def test_03_three_byte_identical_report_regenerations(self) -> None:
        generated: list[bytes] = []
        with tempfile.TemporaryDirectory() as scratch:
            for _ in range(3):
                target = generate_report.write_report(Path(scratch))
                generated.append(target.read_bytes())
        self.assertEqual(len(generated), 3)
        self.assertTrue(all(item == generated[0] for item in generated))
        self.assertEqual(generated[0], (HERE / "report.json").read_bytes())

    def test_04_report_internal_repeat_record_is_exact(self) -> None:
        repeat = self.report["repeat_runs"]
        self.assertEqual(repeat["three_repeats"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(repeat["canonical_digests"], [REPEAT_DIGEST] * 3)

    def test_05_source_pins_match_declared_digests(self) -> None:
        pins = host.check_pins(self.fixtures)
        self.assertEqual(len(pins), 7)
        self.assertTrue(all(pin["verified"] for pin in pins), pins)
        self.assertEqual([pin["path"] for pin in pins],
                         [pin["path"] for pin in self.report["source_pins"]])

    def test_06_dependency_lock_is_exact(self) -> None:
        pin = host.check_dependency_pin(self.fixtures)
        self.assertTrue(pin["verified"])
        self.assertTrue(pin["native_library_pin_verified"])
        self.assertEqual(pin["name"], "SpeexDSP")
        self.assertEqual(pin["version"], "1.2.1")
        self.assertEqual(pin["revision"], "7a158783df74efe7c2d1c6ee8363c1e695c71226")
        self.assertEqual(pin["source"], "vendored:third_party/speexdsp")
        self.assertFalse(pin["network_fetch_required"])

    def test_07_default_off_additive_recipe(self) -> None:
        valid, reason = host.validate_recipe(self.recipe)
        self.assertTrue(valid, reason)
        self.assertFalse(self.recipe["activation"]["default_enabled"])
        self.assertTrue(self.recipe["activation"]["opt_in_only"])
        self.assertEqual(self.recipe["activation"]["build_targets_added"], [])
        self.assertEqual(self.recipe["activation"]["shared_sources_modified"], [])
        self.assertFalse(self.recipe["transport"]["automatic_retry"])
        self.assertFalse(self.recipe["transport"]["hot_swap"])

    def test_08_recipe_rejects_default_enabled(self) -> None:
        changed = json.loads(json.dumps(self.recipe))
        changed["activation"]["default_enabled"] = True
        valid, reason = host.validate_recipe(changed)
        self.assertFalse(valid)
        self.assertEqual(reason, "default_enabled")

    def test_09_recipe_rejects_analysis_node_in_audio_path(self) -> None:
        changed = json.loads(json.dumps(self.recipe))
        variant = changed["variants"]["voice_focus"]
        variant["audio_path"] = variant["audio_path"] + ["advisory_rms"]
        valid, reason = host.validate_recipe(changed)
        self.assertFalse(valid)
        self.assertTrue(reason.startswith("voice_focus:"))

    def test_10_identity_output_is_bit_exact(self) -> None:
        comparisons = self.report["comparisons"]
        self.assertTrue(comparisons["identity_output_equals_noisy_input"])

    def test_11_exact_valid_audio_conservation_for_all_variants(self) -> None:
        self.assertTrue(self.report["exact_valid_audio_conservation"])
        for name in MAIN_VARIANTS:
            accounting = self.report["variants"][name]["conservation"]
            self.assertEqual(accounting["accepted_samples"], accounting["delivered_valid_samples"])
            self.assertEqual(accounting["missing_samples"], 0)
            self.assertEqual(accounting["duplicate_samples"], 0)
            self.assertEqual(accounting["source_interval"], [0, accounting["accepted_samples"]])

    def test_12_individual_stages_and_chain_are_distinct(self) -> None:
        digests = {name: self.report["variants"][name]["paired_output_digest"]
                   for name in MAIN_VARIANTS}
        # The paired stimulus stays below the limiter ceiling, so the pinned
        # copy fast path makes identity and limiter-only bit-identical there.
        # The clipping stimulus below distinguishes them; base and voice-focus
        # are intentionally identical because the tap is read-only.
        self.assertEqual(len(set(digests.values())), 4)
        self.assertNotEqual(digests["identity"], digests["highpass_only"])
        self.assertNotEqual(digests["identity"], digests["ns_only"])
        self.assertEqual(digests["identity"], digests["limiter_only"])
        self.assertNotEqual(
            self.report["variants"]["identity"]["clipping_output"]["f32_digest"],
            self.report["variants"]["limiter_only"]["clipping_output"]["f32_digest"])

    def test_13_base_chain_without_tap_is_bit_identical_to_voice_focus(self) -> None:
        comparisons = self.report["comparisons"]
        self.assertTrue(comparisons["basic_and_voice_focus_audio_bit_identical"])
        self.assertEqual(comparisons["tap_events_basic"], 0)
        self.assertGreater(comparisons["tap_events_voice_focus"], 0)
        self.assertTrue(comparisons["tap_read_only"])

    def test_14_tap_is_not_in_audio_path(self) -> None:
        variant = self.recipe["variants"]["voice_focus"]
        tap_ids = [node["id"] for node in variant["nodes"] if node["role"] == "analysis"]
        self.assertEqual(tap_ids, ["advisory_rms"])
        self.assertFalse(any(node_id in variant["audio_path"] for node_id in tap_ids))
        self.assertFalse(self.report["comparisons"]["analysis_tap_in_audio_path"])

    def test_15_measured_delay_separates_content_and_availability(self) -> None:
        delay = self.report["measured_delay"]
        self.assertEqual(delay["identity"]["measured_raw_offset_samples"], 0)
        self.assertEqual(delay["identity"]["measured_content_lag_after_alignment"], 0)
        self.assertEqual(delay["basic_chain"]["declared_buffering_samples"], 160)
        self.assertEqual(delay["basic_chain"]["startup_padding_samples"], 160)
        self.assertEqual(delay["basic_chain"]["measured_raw_offset_samples"], 160)
        self.assertEqual(delay["basic_chain"]["measured_content_lag_after_alignment"], 0)
        self.assertEqual(delay["basic_chain"]["valid_output_samples"], 6400)

    def test_16_backend_failure_bypasses_on_next_epoch(self) -> None:
        bypass = self.report["failure_bypass"]
        self.assertEqual(bypass["failure"]["reason"], "explicit_backend_failure")
        self.assertEqual(bypass["failed_epoch"], 7)
        self.assertEqual(bypass["bypass_epoch"], 8)
        self.assertFalse(bypass["automatic_retry"])
        self.assertEqual(bypass["operator_selected_bypass_recipe"], "bypass")
        self.assertEqual(bypass["pre_failure_drained_valid_samples"], 320)
        self.assertEqual(bypass["bypass_accepted_samples"], 480)
        self.assertEqual(bypass["combined"]["missing_samples"], 0)
        self.assertEqual(bypass["combined"]["duplicate_samples"], 0)
        self.assertEqual(bypass["combined"]["accepted_samples"], 800)

    def test_17_timeout_clock_and_frame_controls(self) -> None:
        controls = self.report["controls"]
        self.assertTrue(controls["all_expected"])
        self.assertEqual(controls["normal_submission_status"], "ok")
        self.assertEqual(controls["observations"], {
            "timeout_exceeded": "rejected_timeout",
            "nonmonotonic_clock": "rejected_bad_clock",
            "stale_epoch": "rejected_stale_epoch",
            "nonfinite_input": "rejected_nonfinite_input",
            "bad_final_padding": "rejected_bad_padding",
        })

    def test_18_paired_scores_are_present_without_stoi_claim(self) -> None:
        for name in MAIN_VARIANTS:
            paired = self.report["variants"][name]["paired"]
            self.assertIn("si_sdr_db", paired)
            self.assertIn("identity_noisy", paired["si_sdr_db"])
            self.assertIn("variant_output", paired["si_sdr_db"])
            self.assertIn("rms_gain_ratio", paired["preservation"])
            self.assertTrue(paired["output"]["finite"])
            self.assertEqual(paired["stoi"]["status"], "blocked_missing_pinned_scorer")
            self.assertIsNone(paired["stoi"]["value"])

    def test_19_clipped_counts_are_recorded(self) -> None:
        identity = self.report["variants"]["identity"]
        limiter = self.report["variants"]["limiter_only"]
        self.assertGreater(identity["clipping_input"]["clipped_or_nonfinite"], 0)
        self.assertEqual(limiter["clipping_output"]["clipped_or_nonfinite"], 0)
        self.assertGreater(limiter["clipping_output"]["at_or_above_ceiling"], 0)

    def test_20_no_public_claim_or_excluded_evidence(self) -> None:
        self.assertEqual(self.report["claim"], "none")
        self.assertEqual(self.report["status"], "proposal_only_synthetic_incomplete")
        excluded = {item["item"]: item["status"] for item in self.report["non_claims"]}
        self.assertEqual(excluded["Tiny16 model parity"], "excluded")
        self.assertEqual(excluded["Real audio, devices, paced workload, listening and release qualification"],
                         "excluded")

    def test_21_change_scope_is_task_local(self) -> None:
        scope = self.report["change_scope"]
        self.assertTrue(scope["task_local_files_only"])
        self.assertEqual(scope["cmake_ci_edits"], 0)
        self.assertEqual(scope["abi_or_default_changes"], 0)
        self.assertEqual(scope["provider_substitutions"], [])
        self.assertEqual(scope["tolerance_widening"], [])
        self.assertEqual(scope["external_assets"], 0)
        protected = ["CMakeLists.txt", ".github/workflows/ci.yml", "core/providers",
                     "deps/lock.json", "deps/speexdsp-files.sha256", "api", "include"]
        diff = subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", *protected],
                              cwd=WORKTREE, capture_output=True, text=True, check=False)
        self.assertEqual(diff.returncode, 0, diff.stdout + diff.stderr)

    def test_22_all_report_checks_pass(self) -> None:
        self.assertTrue(self.report["all_checks_pass"])
        self.assertEqual(host.build_report(), self.report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
