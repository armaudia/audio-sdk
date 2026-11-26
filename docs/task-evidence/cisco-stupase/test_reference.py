# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Standard-library tests for the SDK-CISCO-STUPASE evidence package."""

from __future__ import annotations

import hashlib
import json
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


class CanonicalSerializationTests(unittest.TestCase):
    def test_pinned_python(self) -> None:
        self.assertEqual(sys.version_info[:3], (3, 12, 16))

    def test_canonical_bytes_are_sorted_and_compact(self) -> None:
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": 2}),
                         b'{"a":2,"b":1}')

    def test_canonical_bytes_reject_nonfinite(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                reference.canonical_bytes({"x": value})

    def test_negative_zero_is_normalized(self) -> None:
        self.assertEqual(reference.canonical_bytes({"x": -0.0}), b'{"x":0.0}')


class PinTests(unittest.TestCase):
    def test_source_pins_exist_and_match(self) -> None:
        for raw, digest in reference.SOURCE_PINS.items():
            path = reference.SOURCE_ROOT / raw
            self.assertTrue(path.is_file(), raw)
            self.assertEqual(reference.sha256_file(path), digest, raw)

    def test_boundary_pins_exist_and_match(self) -> None:
        for raw, digest in reference.BOUNDARY_PINS.items():
            path = reference.SDK_ROOT / raw
            self.assertTrue(path.is_file(), raw)
            self.assertEqual(reference.sha256_file(path), digest, raw)

    def test_readme_pin_rows_match_source_pins(self) -> None:
        rows = reference.readme_pin_rows()
        seen = dict(rows)
        self.assertEqual(len(rows), len(seen))
        self.assertEqual(set(seen), set(reference.SOURCE_PINS))
        for raw, digest in reference.SOURCE_PINS.items():
            self.assertEqual(seen[raw], digest, raw)
            target = reference.qualify_pin_path(raw)
            self.assertEqual(reference.sha256_file(target), digest, raw)

    def test_qualify_pin_path_rejects_escape(self) -> None:
        for bad in ("", "/etc/passwd", "a/../b", "a\\b"):
            with self.assertRaises(ValueError):
                reference.qualify_pin_path(bad)


class AdmissionTests(unittest.TestCase):
    def test_valid_synthetic_schema(self) -> None:
        result = reference.validate_asset_bundle(
            reference.synthetic_bundle(), allow_synthetic=True)
        self.assertTrue(result["accepted"], result)
        self.assertIsNone(result["code"])

    def test_synthetic_bundle_is_not_admitted_without_bytes(self) -> None:
        result = reference.admit_asset_bundle(
            reference.synthetic_bundle(), bytes_present=False, allow_synthetic=True)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["admitted"])
        self.assertEqual(result["reason"],
                         "asset_bytes_not_supplied_in_this_worktree")
        self.assertFalse(result["qualifies"])

    def test_synthetic_present_control_admits_but_does_not_qualify(self) -> None:
        result = reference.admit_asset_bundle(
            reference.synthetic_bundle(), bytes_present=True, allow_synthetic=True)
        self.assertTrue(result["admitted"])
        self.assertFalse(result["qualifies"])
        self.assertFalse(result["bytes_read"])

    def test_admission_control_all_codes_match(self) -> None:
        control = reference.admission_control()
        summary = control["summary"]
        self.assertEqual(summary["case_count"], 54)
        self.assertEqual(summary["rejected_count"], 54)
        self.assertTrue(summary["all_rejected"])
        self.assertTrue(summary["all_codes_match"])
        self.assertFalse(summary["state_advanced_on_rejection"])
        self.assertFalse(summary["candidate_admitted"])
        self.assertFalse(summary["qualifies"])
        for case in control["cases"]:
            self.assertEqual(case["expected_code"], case["observed_code"], case["id"])
            self.assertEqual(case["status"], "rejected", case["id"])
            self.assertFalse(case["qualifies"])

    def test_exact_identity_rejections(self) -> None:
        cases = {case["id"]: case for case in reference.admission_control()["cases"]}
        self.assertEqual(cases["M51"]["observed_code"], "checkpoint_identity_mismatch")
        self.assertEqual(cases["M52"]["observed_code"], "checkpoint_size_mismatch")
        self.assertEqual(cases["M53"]["observed_code"], "invalid_hub_revision")
        self.assertEqual(cases["M54"]["observed_code"], "invalid_source_commit")

    def test_candidate_admission_is_absent(self) -> None:
        admission = reference.admission_control()
        candidate = admission["candidate_admission"]
        self.assertFalse(candidate["accepted"])
        self.assertFalse(candidate["admitted"])
        self.assertEqual(candidate["reason"], "asset_bundle_not_supplied")
        self.assertFalse(candidate["qualifies"])


class ControlTests(unittest.TestCase):
    def test_frame_control(self) -> None:
        control = reference.frame_control()
        self.assertEqual(control["summary"]["case_count"], 12)
        self.assertEqual(control["summary"]["accepted_count"], 1)
        self.assertEqual(control["summary"]["rejected_count"], 11)
        self.assertTrue(control["summary"]["all_codes_match"])
        self.assertFalse(control["summary"]["qualifies"])
        self.assertFalse(control["summary"]["audio_read"])

    def test_frame_validator(self) -> None:
        self.assertIsNone(reference.validate_frame([0.0] * reference.FRAME_SAMPLES))
        self.assertEqual(reference.validate_frame([0.0] * 159),
                         "wrong_frame_length")
        self.assertEqual(reference.validate_frame([0.0] * 159 + [1.1]),
                         "sample_out_of_range")
        self.assertEqual(reference.validate_frame([0.0] * 159 + [True]),
                         "sample_not_number")

    def test_mel_geometry(self) -> None:
        control = reference.mel_geometry_control()
        self.assertEqual(reference.mel_frames(16000), 51)
        self.assertEqual(reference.mel_frames(32000), 101)
        self.assertEqual(reference.mel_frames(0), 1)
        self.assertTrue(control["summary"]["all_checks_pass"])
        self.assertEqual(control["summary"]["checks_passed"], 7)
        self.assertFalse(control["qualifies"])
        self.assertFalse(control["measured"])

    def test_scoring_control(self) -> None:
        control = reference.scoring_control()
        self.assertTrue(control["summary"]["identity_exact"])
        self.assertIsInstance(control["identity_control"]["si_sdr_db"], str)
        self.assertIsInstance(control["identity_control"]["snr_db"], str)
        self.assertTrue(control["gain_half_control"]["si_sdr_scale_invariant"])
        self.assertNotEqual(control["gain_half_control"]["snr_delta_db"], 0.0)
        self.assertEqual(control["silence_control"]["snr_db"], 0.0)
        self.assertIsInstance(control["silence_control"]["si_sdr_db"], str)
        self.assertTrue(control["all_values_finite_or_explicitly_undefined"])
        self.assertIsInstance(control["stoi"], str)
        self.assertFalse(control["qualifies"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_report_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["status"], "proposal_only_incomplete")
        self.assertEqual(report["evidence_status"], "incomplete")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertEqual(report["profile"], "enhancement")
        self.assertTrue(report["proposal_only"])
        self.assertTrue(report["no_missing_result_qualifies_candidate"])

    def test_report_gates_and_blockers(self) -> None:
        gates = self.report["gates"]
        blockers = self.report["exact_blockers"]
        self.assertEqual(len(gates), 10)
        self.assertEqual(len(blockers), 8)
        self.assertEqual(len({gate["id"] for gate in gates}), 10)
        self.assertEqual(len({blocker["id"] for blocker in blockers}), 8)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertFalse(gate["qualifies"])
            self.assertTrue(gate["reopen"])
        for blocker in blockers:
            self.assertEqual(blocker["status"], "open")
            self.assertFalse(blocker["qualifies"])
            self.assertTrue(blocker["reopen"])
        self.assertEqual(self.report["qualification"]["qualifying_results"], 0)

    def test_report_assets(self) -> None:
        boundary = self.report["asset_boundary"]
        self.assertEqual(boundary["source_commit"], reference.SOURCE_COMMIT)
        self.assertEqual(boundary["hub_revision"], reference.HUB_REVISION)
        self.assertEqual(boundary["asset_count"], 3)
        self.assertEqual(boundary["checkpoint_total_bytes"],
                         reference.TOTAL_CHECKPOINT_BYTES)
        self.assertEqual(len(boundary["assets"]), 3)
        for asset, expected in zip(boundary["assets"], reference.EXTERNAL_ASSETS):
            self.assertEqual(asset["id"], expected["id"])
            self.assertEqual(asset["path"], expected["path"])
            self.assertEqual(asset["byte_count"], expected["byte_count"])
            self.assertEqual(asset["sha256"], expected["sha256"])
            self.assertFalse(asset["present_locally"])
            self.assertFalse(asset["admitted"])
            self.assertFalse(asset["bytes_read"])
            self.assertFalse(asset["qualifies"])
        self.assertFalse(boundary["weights_downloaded"])
        self.assertFalse(boundary["asset_bytes_read"])
        self.assertFalse(boundary["candidate_admission"]["admitted"])

    def test_report_scope(self) -> None:
        scope = self.report["scope"]
        false_keys = (
            "benchmark_claim", "benchmark_run", "default_selected",
            "descriptor_registry_change", "device_timing_measured",
            "download_attempted", "audio_played", "audio_read",
            "installed_v0_behavior_change", "license_key_used",
            "listening_conducted", "network_used_by_package",
            "provider_registration", "public_api_abi_change",
            "release_claim", "render_produced", "shared_build_or_ci_change",
            "vendor_runtime_imported", "vendor_runtime_invoked",
            "vendor_sdk_copied", "weights_downloaded", "asset_bytes_read",
        )
        for key in false_keys:
            self.assertFalse(scope[key], key)
        self.assertTrue(scope["network_used_for_metadata"])
        self.assertTrue(scope["task_local_only"])

    def test_report_geometry(self) -> None:
        geometry = self.report["task_geometry"]
        self.assertEqual(geometry["sample_rate_hz"], 16000)
        self.assertEqual(geometry["channels"], 1)
        self.assertEqual(geometry["sample_format"], "f32")
        self.assertEqual(geometry["mel"]["n_mels"], 100)
        self.assertEqual(geometry["mel"]["n_fft"], 1280)
        self.assertEqual(geometry["mel"]["hop_length"], 320)
        self.assertEqual(geometry["mel"]["win_length"], 1280)
        self.assertEqual(geometry["cfm"]["default_steps"], 8)
        self.assertEqual(geometry["cfm"]["default_cfg_strength"], 0.5)
        self.assertEqual(geometry["cfm"]["default_sway_sampling_coef"], -1.0)
        self.assertEqual(geometry["content_alignment"]["content_lag_samples"], 0)
        self.assertFalse(geometry["peak_policy"]["consistent"])
        self.assertFalse(geometry["qualifies"])

    def test_report_enhancement_rows(self) -> None:
        profile = self.report["enhancement_profile"]
        self.assertEqual(len(profile["rows"]), 10)
        for row in profile["rows"]:
            self.assertFalse(row["qualifies"], row["id"])
        self.assertEqual(profile["qualifying_results"], 0)
        self.assertFalse(profile["qualifies"])
        self.assertFalse(profile["clean_references_present"])
        self.assertFalse(profile["listening_conducted"])

    def test_report_repeatability(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)
        self.assertEqual(reference.canonical_report_bytes(),
                         reference.canonical_report_bytes())

    def test_report_pin_sets(self) -> None:
        self.assertEqual(set(self.report["source_pin_paths"]),
                         set(reference.SOURCE_PINS))
        self.assertEqual(set(self.report["boundary_pin_paths"]),
                         set(reference.BOUNDARY_PINS))
        self.assertEqual(set(self.report["local_file_names"]),
                         set(reference.LOCAL_FILES))

    def test_linked_row(self) -> None:
        self.assertEqual(self.report["linked_row"], reference.linked_row())
        self.assertEqual(self.report["linked_row_sha256"],
                         reference.linked_row_digest())
        self.assertEqual(self.report["linked_row"]["id"], reference.TASK)

    def test_inventory_component(self) -> None:
        component = reference.inventory_component()
        self.assertEqual(component, reference.INVENTORY_COMPONENT)

    def test_no_negative_zero(self) -> None:
        self.assertFalse(reference.has_negative_zero(self.report))


class DocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = reference.build_contract()
        cls.readiness = reference.build_readiness()
        cls.adapter = reference.build_adapter()

    def test_contract_invariants(self) -> None:
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.contract["profile"], "enhancement")
        self.assertEqual(self.contract["base_commit"], reference.BASE_COMMIT)
        self.assertEqual(len(self.contract["gates"]), 10)
        self.assertEqual(len(self.contract["exact_blockers"]), 8)
        self.assertTrue(all(self.contract["invariants"].values()))
        self.assertIsNone(self.contract["report_sha256"])
        self.assertEqual(self.contract["artifact_pins"], {})

    def test_readiness(self) -> None:
        self.assertEqual(self.readiness["decision"], "DEFER")
        self.assertEqual(self.readiness["status"], "blocked")
        self.assertEqual(self.readiness["qualification_status"], "not_qualified")
        self.assertTrue(self.readiness["proposal_only"])
        self.assertFalse(self.readiness["qualified"])
        self.assertEqual(self.readiness["admitted_asset_count"], 0)
        self.assertEqual(self.readiness["qualifying_results"], 0)
        self.assertEqual(len(self.readiness["external_blockers"]), 8)
        self.assertEqual(len(self.readiness["gates"]), 10)
        self.assertFalse(self.readiness["weights_downloaded"])

    def test_adapter_is_off(self) -> None:
        self.assertTrue(self.adapter["proposal_only"])
        self.assertFalse(self.adapter["implemented"])
        self.assertFalse(self.adapter["registered"])
        self.assertFalse(self.adapter["provider_registration"])
        self.assertFalse(self.adapter["enabled_by_default"])
        self.assertFalse(self.adapter["default_selected"])
        self.assertFalse(self.adapter["qualifies"])

    def test_local_files_exist(self) -> None:
        for name in reference.LOCAL_FILES:
            path = HERE / name
            self.assertTrue(path.is_file(), name)
            self.assertFalse(path.is_symlink(), name)

    def test_non_claims_cover_asset_and_release(self) -> None:
        text = "\n".join(self.report["non_claims"])
        for token in ("checkpoint", "runtime", "rights", "benchmark", "release"):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
