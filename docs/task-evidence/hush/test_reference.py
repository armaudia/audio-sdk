# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local SDK-HUSH evidence package."""

from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
READINESS = HERE / "readiness.json"
ADAPTER = HERE / "adapter.json"
README = HERE / "README.md"


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.strict_loads(REPORT.read_text(encoding="utf-8"))
        cls.contract = reference.strict_loads(CONTRACT.read_text(encoding="utf-8"))
        cls.readiness = reference.strict_loads(READINESS.read_text(encoding="utf-8"))
        cls.adapter = reference.strict_loads(ADAPTER.read_text(encoding="utf-8"))
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_bytes(), f"{digest}  report.json\n".encode("ascii"))

    def test_03_report_is_canonical_strict_json(self) -> None:
        self.assertEqual(REPORT.read_bytes(),
                         reference.canonical_report_bytes(self.report))
        self.assertFalse(reference.has_negative_zero(self.report))

    def test_04_disposition_is_defer_incomplete_not_qualified(self) -> None:
        for key, expected in (
                ("status", "proposal_only_synthetic_incomplete"),
                ("evidence_status", "incomplete"),
                ("qualification_status", "not_qualified"),
                ("decision", "DEFER"),
                ("defer_before", "opt_in_adapter_exposure")):
            self.assertEqual(self.report[key], expected, key)
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_05_spatial_profile_is_applied(self) -> None:
        self.assertEqual(self.report["profile"], "spatial")
        self.assertEqual(self.contract["profile"], "spatial")
        self.assertEqual(self.contract["acceptance_profile"]["name"], "spatial")
        self.assertEqual(self.report["spatial_geometry"],
                         reference.SPATIAL_GEOMETRY)
        for key in ("layout", "source_condition", "target_condition",
                    "reference_condition", "interferer_condition",
                    "room_condition", "permissions"):
            self.assertTrue(self.report["spatial_geometry"][key], key)

    def test_06_boundary_is_opt_in_unregistered_and_unchanged(self) -> None:
        keys = ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "shared_cmakelists_change",
                "installed_v0_behavior_change", "processor_exposure", "ci_change")
        for key in keys:
            self.assertIs(self.report["boundary"][key], False, key)
            self.assertIs(self.contract["boundary"][key], False, key)
        self.assertEqual(self.report["boundary"]["descriptor_settings"], {})

    def test_07_public_and_asset_geometry_pinned(self) -> None:
        fmt = self.report["format"]
        self.assertEqual(fmt["public_sample_rate_hz"], 16000)
        self.assertEqual(fmt["public_channels"], 1)
        self.assertEqual(fmt["public_sample_format"], "f32")
        self.assertEqual(fmt["public_frame_samples"], 160)
        self.assertEqual(fmt["asset_sample_rate_hz"], 16000)
        self.assertEqual(fmt["asset_channels"], 1)
        self.assertEqual(fmt["asset_frame_samples"], 160)
        self.assertEqual(fmt["asset_frame_duration_ms"], 10)
        self.assertTrue(fmt["asset_is_native_16k"])
        self.assertFalse(fmt["resampling_required"])
        self.assertEqual(fmt["atten_limit_db"], 100.0)
        self.assertEqual(fmt["window_samples"], 32000)
        self.assertEqual(fmt["window_frames"], 200)
        self.assertFalse(fmt["sdk_callback_invoked"])

    def test_08_caller_supplied_asset_contract_is_exact(self) -> None:
        contract = self.report["caller_supplied_asset_contract"]
        self.assertEqual(contract, reference.CALLER_ASSET_CONTRACT)
        self.assertEqual(set(contract["required_fields"]),
                         reference.REQUIRED_ASSET_FIELDS)
        self.assertEqual(contract["pinned_values"]["sample_rate_hz"], 16000)
        self.assertEqual(contract["pinned_values"]["frame_samples"], 160)
        self.assertEqual(contract["pinned_values"]["atten_limit_db"], 100.0)
        self.assertEqual(contract["pinned_values"]["source_commit"],
                         reference.UPSTREAM_COMMIT)
        self.assertFalse(contract["asset_is_vendored"])

    def test_09_asset_is_absent_and_not_loaded(self) -> None:
        resolution = self.report["asset_resolution"]
        for key in ("requested", "manifest_present",
                    "library_present_in_sdk_worktree",
                    "model_bundle_present_in_sdk_worktree",
                    "runtime_library_present_in_sdk_worktree",
                    "verified", "loaded", "executed"):
            self.assertIs(resolution[key], False, key)
        self.assertTrue(resolution["surrogate_used"])
        self.assertTrue(resolution["model_bundle_present_in_external_checkout"])
        self.assertTrue(resolution["runtime_library_present_in_external_checkout"])
        for expected in (reference.EXPECTED_CALLER_RUNTIME_PATH,
                         reference.EXPECTED_CALLER_MODEL_PATH):
            self.assertFalse((SDK_ROOT / expected).exists(), expected)

    def test_10_surrogate_is_not_hush(self) -> None:
        surrogate = self.report["surrogate"]
        self.assertEqual(surrogate["identity"],
                         "hush-boundary-surrogate-v0")
        for key in ("is_hush", "is_neural_network", "onnx_graph",
                    "deepfilternet_blocks", "weights", "checkpoint",
                    "model_bundle", "enrollment_input", "quality_claim"):
            self.assertIs(surrogate[key], False, key)
        self.assertEqual(surrogate["delay_modeled_samples"], 160)
        self.assertEqual(surrogate["delay_compensated_samples"], 160)
        self.assertEqual(surrogate["atten_limit_db"], 100.0)

    def test_11_all_conditions_present_and_outputs_finite(self) -> None:
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for name, condition in self.report["conditions"].items():
            self.assertEqual(condition["input"]["samples"], 32000, name)
            self.assertEqual(condition["output"]["samples"], 32000, name)
            self.assertTrue(condition["input"]["finite"], name)
            self.assertTrue(condition["output"]["finite"], name)
            self.assertEqual(condition["output"]["clipped_or_nonfinite"], 0, name)
            self.assertEqual(condition["input"]["clipped_or_nonfinite"], 0, name)
            self.assertEqual(condition["surrogate_gate"]["frame_count"], 200, name)
            self.assertTrue(condition["surrogate_gate"]["delay_compensated"], name)
            self.assertEqual(condition["surrogate_gate"]["attenuation_floor"],
                             reference.GATE_FLOOR, name)

    def test_12_paired_metric_deltas_are_consistent(self) -> None:
        for name, condition in self.report["conditions"].items():
            for metric_name in ("si_sdr_db", "stoi"):
                metric = condition[metric_name]
                identity = metric["identity_noisy"]
                provider = metric["provider_surrogate"]
                delta = metric["paired_delta"]
                if identity is not None and provider is not None:
                    self.assertIsNotNone(delta, (name, metric_name))
                    self.assertAlmostEqual(delta, provider - identity, places=6)
                else:
                    self.assertIsNone(delta, (name, metric_name))

    def test_13_three_sir_strata_are_measured(self) -> None:
        for name, sir in (("mixture_sir12", 12), ("mixture_sir18", 18),
                          ("mixture_sir24", 24)):
            condition = self.report["conditions"][name]
            self.assertEqual(condition["interferer_sir_db"], sir, name)
            projection = condition["projection"]
            self.assertEqual(projection["status"], "measured", name)
            for key in ("target_retention", "interferer_leakage_retention",
                        "target_to_interferer_ratio_gain_db",
                        "target_projection_snr_db",
                        "identity_target_projection_snr_db",
                        "target_projection_snr_delta_db"):
                self.assertIsNotNone(projection[key], (name, key))
            self.assertAlmostEqual(
                projection["target_projection_snr_delta_db"],
                projection["target_projection_snr_db"] -
                projection["identity_target_projection_snr_db"], places=5)
        self.assertEqual([row["condition"] for row in self.report["stratification"]],
                         list(reference.STRATUM_CONDITIONS))
        for row in self.report["stratification"]:
            self.assertFalse(row["held_out"])
            self.assertFalse(row["independent_items"])

    def test_14_non_strata_are_not_scored_for_leakage(self) -> None:
        for name in ("target_only", "interferer_only", "silence"):
            projection = self.report["conditions"][name]["projection"]
            self.assertEqual(projection["status"], "not_applicable", name)
            self.assertIsNone(
                projection["target_to_interferer_ratio_gain_db"], name)
            self.assertIsNone(
                self.report["conditions"][name]["interferer_sir_db"], name)

    def test_15_zero_reference_is_explicit_not_scored(self) -> None:
        self.assertEqual(
            self.report["conditions"]["target_only"]["si_sdr_db"][
                "identity_invalid_reason"], "zero_error_identity_exact")
        self.assertEqual(
            self.report["conditions"]["interferer_only"]["si_sdr_db"][
                "identity_invalid_reason"], "zero_reference_energy")
        self.assertEqual(
            self.report["conditions"]["silence"]["stoi"][
                "identity_invalid_reason"], "zero_reference")
        self.assertIsNone(
            self.report["conditions"]["silence"]["si_sdr_db"]["paired_delta"])

    def test_16_target_damage_and_leakage_are_consistent(self) -> None:
        conditions = self.report["conditions"]
        self.assertEqual(self.report["target_damage"],
                         reference._target_damage(conditions))
        self.assertEqual(self.report["leakage"],
                         reference._leakage(conditions))
        self.assertEqual(self.report["regressions"],
                         reference._regressions(conditions))
        self.assertEqual(self.report["comparison"]["regression_count"],
                         len(self.report["regressions"]))

    def test_17_channel_and_room_limits_are_declared(self) -> None:
        channel = self.report["channel_and_room"]
        for key in ("channel_loss_evaluated", "multichannel_evaluated",
                    "room_model", "rir_used", "movement_evaluated",
                    "reference_change_evaluated"):
            self.assertIs(channel[key], False, key)
        self.assertEqual(channel["channels"], 1)
        labels = self.report["held_out_labels"]
        for key in ("present", "speaker_identity_labels", "room_labels",
                    "independent_items"):
            self.assertIs(labels[key], False, key)

    def test_18_alignment_models_and_compensates_160_samples(self) -> None:
        alignment = self.report["alignment"]
        self.assertEqual(alignment["expected_impulse_index"], 4000)
        self.assertEqual(alignment["uncompensated_impulse_index"], 4160)
        self.assertEqual(alignment["compensated_impulse_index"], 4000)
        self.assertEqual(alignment["measured_content_lag_samples"], 0)
        self.assertEqual(alignment["modeled_frame_delay_samples"], 160)
        self.assertEqual(alignment["modeled_frame_delay_ms"], 10)
        self.assertEqual(alignment["upstream_algorithmic_latency_samples"], 320)
        self.assertEqual(alignment["upstream_algorithmic_latency_ms"], 20)
        self.assertTrue(alignment["delay_compensation_applied"])
        self.assertFalse(alignment["sdk_callback_invoked"])

    def test_19_state_controls_pass(self) -> None:
        for key, value in self.report["state"].items():
            self.assertTrue(value, key)
        self.assertTrue(self.report["state"]["zero_attenuation_is_identity"])

    def test_20_caller_asset_controls_fail_closed(self) -> None:
        controls = self.report["controls"]["caller_asset"]
        self.assertTrue(controls["all_present"])
        self.assertTrue(controls["all_fail_closed"])
        self.assertEqual(controls["valid_manifest"],
                         {"status": "validated", "verified": True,
                          "loaded": False, "executed": False})
        for name in ("missing_manifest", "absent_file", "library_hash_mismatch",
                     "model_hash_mismatch", "wrong_source_commit",
                     "wrong_sample_rate", "wrong_channels", "wrong_frame_size",
                     "wrong_atten_limit", "relative_path", "extra_field"):
            self.assertEqual(controls[name]["status"], "rejected", name)

    def test_21_frame_controls_fail_closed(self) -> None:
        controls = self.report["controls"]["frame"]
        self.assertTrue(controls["all_present"])
        self.assertTrue(controls["all_fail_closed"])
        for name in ("short_input", "two_dimensional_input", "nonfinite_input",
                     "truncated_output", "atten_above_limit",
                     "atten_below_limit"):
            self.assertEqual(controls[name]["status"], "rejected", name)
        self.assertEqual(controls["missing_reference"]["status"], "invalid")
        self.assertEqual(controls["silence_output"]["status"], "pass")
        self.assertTrue(controls["state_unchanged_after_rejection"])

    def test_22_adverse_matches_controls(self) -> None:
        adverse = self.report["adverse"]
        self.assertTrue(adverse["all_rejected"])
        self.assertTrue(adverse["all_invalid_cases_rejected"])
        self.assertTrue(adverse["valid_manifest_control_present"])
        self.assertEqual(adverse["config_rejections"],
                         self.report["controls"]["caller_asset"])
        self.assertEqual(adverse["frame_rejections"],
                         self.report["controls"]["frame"])

    def test_23_source_pins_match_files(self) -> None:
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.contract["source_pins"], reference.SOURCE_PINS)
        for path, digest in reference.SOURCE_PINS.items():
            actual = hashlib.sha256(
                (reference.SOURCE_ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)

    def test_24_asset_pins_match_files(self) -> None:
        self.assertEqual(self.report["asset_pins"], reference.ASSET_PINS)
        for path, digest in reference.ASSET_PINS.items():
            actual = hashlib.sha256(
                (reference.SOURCE_ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)
        self.assertEqual(
            reference.ASSET_PINS[reference.MODEL_BUNDLE_PATH],
            reference.MODEL_BUNDLE_SHA256)

    def test_25_boundary_pins_match_worktree(self) -> None:
        self.assertEqual(self.report["boundary_pins"], reference.BOUNDARY_PINS)
        for path, digest in reference.BOUNDARY_PINS.items():
            actual = hashlib.sha256((SDK_ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)

    def test_26_readme_digest_table_matches_pins_and_files(self) -> None:
        rows = dict(reference.readme_pin_rows())
        external = {**reference.SOURCE_PINS, **reference.ASSET_PINS}
        self.assertEqual(set(rows), set(external))
        for path, digest in rows.items():
            self.assertEqual(digest, external[path], path)
            target = reference.qualify_pin_path(path)
            self.assertTrue(target.is_file(), path)
            self.assertEqual(
                hashlib.sha256(target.read_bytes()).hexdigest(), digest, path)

    def test_27_contract_digest_matches(self) -> None:
        self.assertEqual(CONTRACT.read_bytes(), reference.contract_bytes())
        self.assertEqual(self.report["contract_sha256"],
                         hashlib.sha256(CONTRACT.read_bytes()).hexdigest())
        self.assertEqual(self.readiness["contract_sha256"],
                         hashlib.sha256(CONTRACT.read_bytes()).hexdigest())

    def test_28_readiness_is_strict_and_blocked(self) -> None:
        self.assertEqual(READINESS.read_bytes(), reference.readiness_bytes())
        self.assertEqual(self.readiness["report_sha256"],
                         hashlib.sha256(REPORT.read_bytes()).hexdigest())
        for key in ("ready_for_opt_in_adapter", "ready_for_provider_registration",
                    "ready_for_release", "quality_pass",
                    "spatial_acceptance_cleared"):
            self.assertIs(self.readiness[key], False, key)
        self.assertEqual(self.readiness["blocked_gates"],
                         [name for name, _ in reference.GATE_DEFINITIONS])
        self.assertEqual(self.readiness["exact_blocker"],
                         reference.EXACT_BLOCKERS[0])
        self.assertEqual(self.readiness["external_asset"]["expected_runtime_sha256"],
                         reference.ASSET_PINS[reference.RUNTIME_DYLIB_PATH])

    def test_29_adapter_is_task_local_and_not_implemented(self) -> None:
        self.assertEqual(ADAPTER.read_bytes(), reference.adapter_bytes())
        self.assertEqual(self.adapter["task_id"], reference.TASK)
        self.assertTrue(self.adapter["task_local"])
        for key in ("implemented", "registered", "enabled_by_default",
                    "default_selected", "public_api_abi_change",
                    "provider_registration", "descriptor_registry_change",
                    "installed_v0_behavior_change", "asset_present",
                    "enrollment_input"):
            self.assertIs(self.adapter[key], False, key)
        self.assertTrue(self.adapter["caller_supplied_asset_required"])
        self.assertEqual(self.adapter["activation"], "deferred_until_gates_clear")
        self.assertIsNone(self.adapter["entrypoint"])
        self.assertEqual(self.adapter["tasks"], ["SPK-01"])

    def test_30_all_gates_blocked_with_reopen_conditions(self) -> None:
        self.assertEqual(len(self.report["gates"]),
                         len(reference.GATE_DEFINITIONS))
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen_condition"])
        self.assertEqual(self.report["exact_blockers"],
                         reference.EXACT_BLOCKERS)
        self.assertEqual(self.report["missing_evidence"],
                         reference.MISSING_EVIDENCE)
        self.assertEqual(self.report["reopening_conditions"],
                         reference.REOPENING_CONDITIONS)

    def test_31_repeatability_is_three_identical_cold_starts(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)
        self.assertEqual(repeat["digests"][0],
                         hashlib.sha256(reference.canonical_bytes({
                             key: value for key, value in self.report.items()
                             if key != "repeatability"})).hexdigest())

    def test_32_source_reported_values_are_provenance_only(self) -> None:
        source = self.report["source_reported"]
        self.assertEqual(source["status"], "source_reported_not_reproduced")
        self.assertFalse(source["used_for_qualification"])
        self.assertTrue(source["findings"])
        self.assertFalse(self.report["comparison"][
            "source_reported_hush_pilot_used_for_qualification"])

    def test_33_licensing_rights_remain_blocked(self) -> None:
        licensing = self.report["licensing_analysis"]
        for key in ("model_bundle_redistribution_clearance",
                    "runtime_binary_redistribution_clearance",
                    "product_use_clearance",
                    "training_data_provenance_established",
                    "legal_review_completed",
                    "asset_copied_vendored_built_or_downloaded"):
            self.assertIs(licensing[key], False, key)
        self.assertEqual(licensing["blocked_gate"],
                         "model_bundle_and_runtime_rights")
        self.assertEqual(licensing["upstream_license_sha256"],
                         reference.ASSET_PINS[reference.UPSTREAM_LICENSE_PATH])

    def test_34_strict_parsers_reject_bad_inputs(self) -> None:
        result = reference.strict_rejection_examples()
        self.assertEqual(result["bad_json_rejected"], result["bad_json_total"])
        self.assertEqual(result["bad_pins_rejected"], result["bad_pins_total"])

    def test_35_sources_manifest_is_complete_and_deterministic(self) -> None:
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
        self.assertEqual({raw for _, raw in pins},
                         reference.allowed_pin_keys())
        self.assertEqual(len(pins), len(reference.allowed_pin_keys()))

    def test_36_base_commit_and_branch_are_pinned(self) -> None:
        self.assertEqual(self.report["base_commit"],
                         "d5b11912cd09e87296cd9d4654f1917c9cb94258")
        self.assertEqual(self.report["branch"], "swarm/SDK-HUSH")

    def test_37_upstream_identity_and_absence(self) -> None:
        identity = reference.upstream_git_identity()
        self.assertEqual(identity["normalized_remote"],
                         reference.UPSTREAM_REPOSITORY)
        self.assertEqual(identity["commit"], reference.UPSTREAM_COMMIT)
        self.assertTrue(identity["pinned_commit_present"])
        self.assertEqual(reference.vendored_binary_files(), [])

    def test_38_no_prohibited_spatial_real_model_audio_or_release_claim(self) -> None:
        for key, value in self.report["negative_claims"].items():
            self.assertIs(value, False, key)
        for key in ("caller_supplied_asset_present", "hush_source_executed",
                    "hush_runtime_executed", "hush_model_loaded",
                    "model_weights_downloaded", "model_weights_loaded",
                    "real_audio", "real_labels", "room_measurement",
                    "enrollment_prompt", "network_used", "device_timing",
                    "listening_result", "benchmark_claim", "release_claim",
                    "registered_provider"):
            self.assertIs(self.report["scope"][key], False, key)
        for key in ("measured", "device_timing", "paced"):
            self.assertIs(self.report["timing"][key], False, key)
        self.assertEqual(self.readiness["evidence_status"], "incomplete")


if __name__ == "__main__":
    unittest.main(verbosity=2)
