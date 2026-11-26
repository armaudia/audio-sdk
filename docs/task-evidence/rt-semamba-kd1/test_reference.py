# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local SDK-RT-SEMAMBA-KD1 evidence package."""

from __future__ import annotations

import hashlib
from pathlib import Path
import unittest

import numpy as np

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
        cls.contract = reference.strict_loads(
            CONTRACT.read_text(encoding="utf-8"))
        cls.readiness = reference.strict_loads(
            READINESS.read_text(encoding="utf-8"))
        cls.adapter = reference.strict_loads(
            ADAPTER.read_text(encoding="utf-8"))
        cls.generated = reference.canonical_report_bytes(reference.build_report())

    def test_01_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(self.generated, REPORT.read_bytes())

    def test_02_sidecar_matches_report(self) -> None:
        digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_bytes(),
                         f"{digest}  report.json\n".encode("ascii"))

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

    def test_05_enhancement_profile_is_applied(self) -> None:
        self.assertEqual(self.report["profile"], "enhancement")
        self.assertEqual(self.contract["profile"], "enhancement")
        self.assertEqual(self.contract["acceptance_profile"]["name"],
                         "enhancement")
        profile = self.report["enhancement_profile"]
        self.assertTrue(profile["identity_noisy_control"])
        self.assertTrue(profile["peak_and_invalid_output_check"])
        self.assertFalse(profile["established_task_matched_baseline_reproduced"])
        self.assertFalse(profile["real_cohort_scored"])
        self.assertEqual(profile["independent_listening"], "not_run")

    def test_06_boundary_is_opt_in_unregistered_and_unchanged(self) -> None:
        keys = ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "shared_cmakelists_change",
                "installed_v0_behavior_change", "processor_exposure",
                "ci_change")
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
        self.assertEqual(fmt["public_frame_duration_ms"], 10)
        self.assertEqual(fmt["asset_sample_rate_hz"], 16000)
        self.assertEqual(fmt["asset_channels"], 1)
        self.assertEqual(fmt["asset_window_samples"], 400)
        self.assertEqual(fmt["asset_window_duration_ms"], 25)
        self.assertEqual(fmt["asset_hop_samples"], 100)
        self.assertEqual(fmt["asset_chunk_samples"], 1600)
        self.assertTrue(fmt["asset_is_native_16k"])
        self.assertFalse(fmt["resampling_required"])
        self.assertEqual(fmt["clip_samples"], 32000)
        self.assertFalse(fmt["sdk_callback_invoked"])

    def test_08_enhancement_boundary_matches_upstream_contract(self) -> None:
        eb = self.report["enhancement_boundary"]
        self.assertEqual(eb["stft_window_samples"], 400)
        self.assertEqual(eb["stft_hop_samples"], 100)
        self.assertIs(eb["stft_center"], False)
        self.assertEqual(eb["algorithmic_latency_samples"], 400)
        self.assertEqual(eb["algorithmic_latency_ms"], 25)
        self.assertTrue(eb["upstream_streaming_capable"])
        self.assertFalse(eb["streaming_path_evaluated"])
        self.assertEqual(eb["parameter_count"], 1050000)
        self.assertTrue(eb["vctk_demand_training_and_evaluation"])

    def test_09_caller_supplied_asset_contract_is_exact(self) -> None:
        contract = self.report["caller_supplied_asset_contract"]
        self.assertEqual(contract, reference.CALLER_ASSET_CONTRACT)
        self.assertEqual(set(contract["required_fields"]),
                         reference.REQUIRED_ASSET_FIELDS)
        self.assertEqual(contract["pinned_values"]["sample_rate_hz"], 16000)
        self.assertEqual(contract["pinned_values"]["window_samples"], 400)
        self.assertEqual(contract["pinned_values"]["hop_samples"], 100)
        self.assertEqual(contract["pinned_values"]["source_revision"],
                         reference.UPSTREAM_COMMIT)
        self.assertFalse(contract["asset_is_vendored"])

    def test_10_asset_is_absent_and_not_loaded(self) -> None:
        resolution = self.report["asset_resolution"]
        for key in ("requested", "manifest_present",
                    "checkpoint_present_in_sdk_worktree",
                    "config_present_in_sdk_worktree",
                    "source_tree_present_in_sdk_worktree",
                    "runtime_installed_in_sdk_worktree", "verified", "loaded",
                    "executed"):
            self.assertIs(resolution[key], False, key)
        self.assertTrue(resolution["surrogate_used"])
        self.assertTrue(resolution["checkpoint_present_in_external_checkout"])
        self.assertTrue(resolution["config_present_in_external_checkout"])
        for expected in (reference.EXPECTED_CALLER_CHECKPOINT_PATH,
                         reference.EXPECTED_CALLER_CONFIG_PATH):
            self.assertFalse((SDK_ROOT / expected).exists(), expected)

    def test_11_surrogate_is_not_rt_semamba(self) -> None:
        surrogate = self.report["surrogate"]
        self.assertEqual(surrogate["identity"],
                         "rt-semamba-kd1-boundary-surrogate-v0")
        for key in ("is_rt_semamba", "is_neural_network", "ctf_mamba_blocks",
                    "ssm_state", "checkpoint", "weights", "pytorch",
                    "quality_claim"):
            self.assertIs(surrogate[key], False, key)
        self.assertEqual(surrogate["window_samples"], 400)
        self.assertEqual(surrogate["hop_samples"], 100)
        self.assertEqual(surrogate["delay_modeled_samples"], 400)

    def test_12_stimuli_are_synthetic_and_deterministic(self) -> None:
        first = reference.stimuli()
        second = reference.stimuli()
        self.assertIs(first, second)
        stimuli = self.report["stimuli"]
        self.assertFalse(stimuli["real_audio"])
        self.assertFalse(stimuli["room_model"])
        self.assertEqual(stimuli["snr_db_strata"], [20, 10, 0])
        self.assertEqual(stimuli["clip_samples"], 32000)
        for name in reference.CONDITIONS:
            signal = first["signals"][name]
            self.assertEqual(signal.dtype, np.float32)
            self.assertEqual(signal.size, 32000)
            self.assertTrue(np.isfinite(signal).all())
        self.assertFalse(np.array_equal(first["signals"]["idle_noise"],
                                        first["signals"]["silence"]))
        self.assertFalse(np.array_equal(first["signals"]["noisy_snr20"],
                                        first["signals"]["noisy_snr10"]))

    def test_13_conditions_cover_all_cases_with_exact_lengths(self) -> None:
        conditions = self.report["conditions"]
        self.assertEqual(set(conditions), set(reference.CONDITIONS))
        for name, condition in conditions.items():
            self.assertEqual(condition["input"]["samples"], 32000, name)
            self.assertEqual(condition["output"]["samples"], 32000, name)
            self.assertTrue(condition["input"]["finite"], name)
            self.assertTrue(condition["output"]["finite"], name)
            self.assertEqual(condition["output"]["clipped_or_nonfinite"], 0,
                             name)
            self.assertEqual(condition["surrogate_mask"]["frame_count"], 325,
                             name)
            self.assertTrue(condition["surrogate_mask"]["delay_compensated"],
                            name)

    def test_14_paired_deltas_are_arithmetic(self) -> None:
        for name, condition in self.report["conditions"].items():
            for metric_name in ("snr_db", "si_sdr_db", "stoi"):
                metric = condition[metric_name]
                identity = metric["identity_noisy"]
                provider = metric["provider_surrogate"]
                delta = metric["paired_delta"]
                if identity is None or provider is None:
                    self.assertIsNone(delta, (name, metric_name))
                else:
                    self.assertAlmostEqual(
                        delta, provider - identity, places=5,
                        msg=(name, metric_name))

    def test_15_strata_have_paired_metrics(self) -> None:
        for name in reference.STRATUM_CONDITIONS:
            condition = self.report["conditions"][name]
            for metric_name in ("snr_db", "si_sdr_db", "stoi"):
                self.assertIsNotNone(
                    condition[metric_name]["identity_noisy"], (name, metric_name))
                self.assertIsNotNone(
                    condition[metric_name]["provider_surrogate"],
                    (name, metric_name))
                self.assertIsNotNone(condition[metric_name]["paired_delta"],
                                     (name, metric_name))

    def test_16_clean_control_is_exact_passthrough(self) -> None:
        clean = self.report["conditions"]["clean_control"]
        self.assertEqual(clean["input"]["waveform_sha256"],
                         clean["output"]["waveform_sha256"])
        self.assertEqual(clean["si_sdr_db"]["provider_invalid_reason"],
                         "zero_error_identity_exact")
        self.assertEqual(clean["stoi"]["provider_surrogate"], 1.0)
        preservation = self.report["clean_preservation"]
        self.assertTrue(preservation["bit_exact_passthrough"])
        self.assertEqual(preservation["rms_change_db"], 0.0)

    def test_17_zero_reference_controls_are_never_scored(self) -> None:
        for name in ("idle_noise", "silence"):
            condition = self.report["conditions"][name]
            self.assertEqual(condition["reference"], "none")
            for metric_name in ("snr_db", "si_sdr_db", "stoi"):
                self.assertIsNone(condition[metric_name]["identity_noisy"],
                                  (name, metric_name))
                self.assertIsNone(condition[metric_name]["provider_surrogate"],
                                  (name, metric_name))
                self.assertIsNone(condition[metric_name]["paired_delta"],
                                  (name, metric_name))

    def test_18_peaks_and_invalid_accounting_is_consistent(self) -> None:
        peaks = self.report["peaks_and_invalid"]
        self.assertTrue(peaks["all_outputs_finite"])
        self.assertTrue(peaks["all_outputs_same_length"])
        self.assertEqual(peaks["total_clipped_or_nonfinite"], 0)
        self.assertEqual(set(peaks["per_condition"]), set(reference.CONDITIONS))

    def test_19_alignment_models_and_compensates_one_window(self) -> None:
        alignment = self.report["alignment"]
        self.assertEqual(alignment["expected_impulse_index"], 4000)
        self.assertEqual(alignment["uncompensated_impulse_index"], 4400)
        self.assertEqual(alignment["compensated_impulse_index"], 4000)
        self.assertEqual(alignment["measured_content_lag_samples"], 0)
        self.assertEqual(alignment["modeled_window_delay_samples"], 400)
        self.assertEqual(alignment["algorithmic_latency_ms"], 25)

    def test_20_state_controls_pass(self) -> None:
        for key, value in self.report["state"].items():
            self.assertIs(value, True, key)

    def test_21_caller_asset_controls_fail_closed(self) -> None:
        controls = self.report["controls"]["caller_asset"]
        self.assertTrue(controls["all_present"])
        self.assertTrue(controls["all_fail_closed"])
        self.assertEqual(controls["valid_manifest"], {
            "status": "validated", "verified": True, "loaded": False,
            "executed": False})
        for name in ("missing_manifest", "absent_file",
                     "checkpoint_hash_mismatch", "config_hash_mismatch",
                     "wrong_source_revision", "wrong_sample_rate",
                     "wrong_channels", "wrong_window_samples",
                     "wrong_hop_samples", "wrong_algorithm_latency",
                     "relative_path", "extra_field"):
            self.assertEqual(controls[name]["status"], "rejected", name)

    def test_22_frame_controls_fail_closed(self) -> None:
        controls = self.report["controls"]["frame"]
        self.assertTrue(controls["all_present"])
        self.assertTrue(controls["all_fail_closed"])
        for name in ("short_input", "two_dimensional_input", "nonfinite_input",
                     "truncated_output", "wrong_sample_rate", "wrong_channels",
                     "wrong_window_samples", "wrong_hop_samples"):
            self.assertEqual(controls[name]["status"], "rejected", name)
        self.assertEqual(controls["missing_reference"]["status"], "invalid")
        self.assertEqual(controls["silence_output"]["status"], "pass")
        self.assertTrue(controls["state_unchanged_after_rejection"])

    def test_23_adverse_summary_matches_controls(self) -> None:
        adverse = self.report["adverse"]
        controls = self.report["controls"]
        self.assertTrue(adverse["all_rejected"])
        self.assertTrue(adverse["all_invalid_cases_rejected"])
        self.assertEqual(adverse["config_rejections"],
                         controls["caller_asset"])
        self.assertEqual(adverse["frame_rejections"], controls["frame"])

    def test_24_quality_pass_is_not_claimed(self) -> None:
        comparison = self.report["comparison"]
        self.assertFalse(comparison["quality_pass"])
        self.assertFalse(
            comparison["established_task_matched_baseline_reproduced"])
        self.assertFalse(comparison[
            "source_reported_candidate_screen_used_for_qualification"])
        self.assertEqual(comparison["regression_count"],
                         len(self.report["regressions"]))

    def test_25_source_reported_is_provenance_only(self) -> None:
        source = self.report["source_reported"]
        self.assertEqual(source["status"], "source_reported_not_reproduced")
        self.assertFalse(source["used_for_qualification"])
        self.assertTrue(source["findings"])
        fixtures = {finding["fixture"] for finding in source["findings"]}
        self.assertIn("dns_crop_screen_30", fixtures)
        self.assertIn("upstream_vctk_demand", fixtures)

    def test_26_model_provenance_pins_exact_artifacts(self) -> None:
        provenance = self.report["model_provenance"]
        self.assertEqual(provenance["upstream_commit"],
                         "0c9e8c7c42caadd7badb6cc145c8af93f760863c")
        self.assertEqual(provenance["checkpoint"]["sha256"],
                         reference.CHECKPOINT_SHA256)
        self.assertEqual(provenance["checkpoint"]["bytes"], 4235024)
        self.assertEqual(provenance["config"]["sha256"],
                         reference.CONFIG_SHA256)
        self.assertFalse(provenance["unused_teacher_checkpoint"]["used"])
        self.assertFalse(provenance["runtime"]["loaded_or_executed"])

    def test_27_licensing_does_not_claim_clearance(self) -> None:
        licensing = self.report["licensing_analysis"]
        for key in ("checkpoint_redistribution_clearance",
                    "runtime_redistribution_clearance",
                    "product_use_clearance",
                    "training_data_provenance_established",
                    "legal_review_completed",
                    "asset_copied_vendored_built_or_downloaded"):
            self.assertIs(licensing[key], False, key)
        self.assertEqual(licensing["blocked_gate"],
                         "artifact_and_runtime_rights")

    def test_28_all_gates_are_blocked_with_reopen_conditions(self) -> None:
        gates = self.report["gates"]
        self.assertEqual(len(gates), len(reference.GATE_DEFINITIONS))
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen_condition"])

    def test_29_exact_blockers_and_reopen_conditions_are_recorded(self) -> None:
        self.assertEqual(self.report["exact_blockers"],
                         reference.EXACT_BLOCKERS)
        self.assertEqual(self.report["reopening_conditions"],
                         reference.REOPENING_CONDITIONS)
        self.assertEqual(self.report["missing_evidence"],
                         reference.MISSING_EVIDENCE)

    def test_30_contract_pins_and_digest_are_consistent(self) -> None:
        self.assertEqual(self.report["contract_sha256"],
                         hashlib.sha256(CONTRACT.read_bytes()).hexdigest())
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.report["asset_pins"], reference.ASSET_PINS)
        self.assertEqual(self.report["boundary_pins"],
                         reference.BOUNDARY_PINS)
        self.assertEqual(CONTRACT.read_bytes(), reference.contract_bytes())

    def test_31_sources_manifest_is_complete_and_deterministic(self) -> None:
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
        self.assertEqual(len(pins), len(reference.allowed_pin_keys()))
        for digest, raw in pins:
            if raw.startswith("source:"):
                target = reference.SOURCE_ROOT / raw.split(":", 1)[1]
            else:
                target = SDK_ROOT / raw
            self.assertTrue(target.is_file(), raw)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),
                             digest, raw)

    def test_32_readme_source_table_matches_pins(self) -> None:
        rows = dict(reference.readme_source_rows())
        external = {**reference.SOURCE_PINS, **reference.ASSET_PINS}
        self.assertEqual(rows, external)

    def test_33_readme_artifact_table_matches_files(self) -> None:
        rows = {name: (digest, size)
                for name, digest, size in reference.readme_artifact_rows()}
        self.assertEqual(set(rows), set(reference.ARTIFACT_TABLE_PATHS))
        for name, (digest, size) in rows.items():
            data = (HERE / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest, name)
            self.assertEqual(len(data), size, name)

    def test_34_repeatability_is_byte_identical(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_35_readiness_is_strictly_blocked(self) -> None:
        for key in ("ready_for_opt_in_adapter",
                    "ready_for_provider_registration", "ready_for_release",
                    "quality_pass", "enhancement_acceptance_cleared"):
            self.assertIs(self.readiness[key], False, key)
        self.assertEqual(self.readiness["decision"], "DEFER")
        self.assertEqual(self.readiness["blocked_gates"],
                         [name for name, _ in reference.GATE_DEFINITIONS])
        self.assertEqual(self.readiness["exact_blocker"],
                         reference.EXACT_BLOCKERS[0])
        self.assertEqual(self.readiness["report_sha256"],
                         hashlib.sha256(REPORT.read_bytes()).hexdigest())

    def test_36_adapter_is_proposal_only(self) -> None:
        for key in ("implemented", "registered", "enabled_by_default",
                    "default_selected", "public_api_abi_change",
                    "provider_registration", "descriptor_registry_change",
                    "installed_v0_behavior_change", "shared_build_or_ci_change",
                    "asset_present", "streaming_supported"):
            self.assertIs(self.adapter[key], False, key)
        self.assertIsNone(self.adapter["entrypoint"])
        self.assertEqual(self.adapter["activation"],
                         "deferred_until_gates_clear")
        self.assertEqual(self.adapter["modes"], ["offline"])

    def test_37_no_binary_or_vendored_asset(self) -> None:
        self.assertEqual(reference.vendored_binary_files(), [])
        for path in HERE.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.suffix.lower(),
                                 (".pth", ".onnx", ".wav", ".dylib", ".so",
                                  ".dll", ".ckpt"), path.name)

    def test_38_strict_parsers_reject_bad_input(self) -> None:
        result = reference.strict_rejection_examples()
        self.assertEqual(result["bad_json_rejected"],
                         result["bad_json_total"])
        self.assertEqual(result["bad_pins_rejected"],
                         result["bad_pins_total"])

    def test_39_upstream_identity_matches_pins(self) -> None:
        identity = reference.upstream_git_identity()
        self.assertEqual(identity["normalized_remote"],
                         reference.UPSTREAM_REPOSITORY)
        self.assertEqual(identity["commit"], reference.UPSTREAM_COMMIT)
        self.assertTrue(identity["pinned_commit_present"])

    def test_40_surrogate_config_and_inputs_fail_closed(self) -> None:
        zeros = np.zeros(reference.CLIP_SAMPLES, dtype=np.float32)
        with self.assertRaises(ValueError):
            reference.Surrogate(sample_rate_hz=48000).process(zeros)
        with self.assertRaises(ValueError):
            reference.Surrogate(channels=2).process(zeros)
        with self.assertRaises(ValueError):
            reference.Surrogate(window_samples=320).process(zeros)
        with self.assertRaises(ValueError):
            reference.Surrogate(hop_samples=160).process(zeros)
        with self.assertRaises(ValueError):
            reference.Surrogate().process(zeros[:-1])
        with self.assertRaises(ValueError):
            reference.Surrogate().process(zeros.reshape(-1, 1))

    def test_41_bypass_and_reset_semantics(self) -> None:
        signal = reference.stimuli()["signals"]["noisy_snr10"]
        bypass, _ = reference.Surrogate(bypass=True).process(signal)
        self.assertTrue(np.array_equal(bypass, signal.astype(np.float64)))
        model = reference.Surrogate()
        first, _ = model.process(signal)
        second, _ = model.process(signal)
        self.assertTrue(np.array_equal(first, second))
        model.reset(epoch=2)
        third, _ = model.process(signal)
        self.assertTrue(np.array_equal(first, third))
        self.assertEqual(model.epoch, 2)

    def test_42_licensing_sidecars_are_present(self) -> None:
        for name in ("SOURCES.sha256.license", "adapter.json.license",
                     "contract.json.license", "readiness.json.license",
                     "report.json.license", "report.json.sha256.license",
                     "requirements.lock.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn("SPDX" "-License-Identifier: Apache-2.0", text, name)
            self.assertIn("SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes",
                          text, name)

    def test_43_readme_is_digest_table_documented(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn(reference.SOURCE_TABLE_START, text)
        self.assertIn(reference.ARTIFACT_TABLE_START, text)
        self.assertIn("Exact external blocker", text)


if __name__ == "__main__":
    unittest.main()
