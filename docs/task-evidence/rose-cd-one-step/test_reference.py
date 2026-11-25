# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Acceptance suite for the task-local SDK-ROSE-CD-ONE-STEP evidence package."""

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

    def test_05_boundary_is_opt_in_unregistered_and_unchanged(self) -> None:
        keys = ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "shared_cmakelists_change",
                "installed_v0_behavior_change", "processor_exposure", "ci_change")
        for key in keys:
            self.assertIs(self.report["boundary"][key], False, key)
            self.assertIs(self.contract["boundary"][key], False, key)
        self.assertEqual(self.report["boundary"]["descriptor_settings"], {})

    def test_06_public_and_asset_geometry_pinned(self) -> None:
        fmt = self.report["format"]
        self.assertEqual(fmt["public_sample_rate_hz"], 16000)
        self.assertEqual(fmt["public_channels"], 1)
        self.assertEqual(fmt["public_sample_format"], "f32")
        self.assertEqual(fmt["public_frame_samples"], 160)
        self.assertEqual(fmt["public_frame_duration_ms"], 10)
        self.assertEqual(fmt["asset_sample_rate_hz"], 16000)
        self.assertEqual(fmt["asset_channels"], 1)
        self.assertEqual(fmt["asset_minimum_samples"], 8064)
        self.assertEqual(fmt["asset_stft_n_fft"], 510)
        self.assertEqual(fmt["asset_stft_hop_samples"], 128)
        self.assertTrue(fmt["asset_stft_center"])
        self.assertEqual(fmt["asset_stft_reflection_pad_multiple_frames"], 64)
        self.assertEqual(fmt["window_samples"], 32000)
        self.assertEqual(fmt["window_frames"], 200)
        self.assertFalse(fmt["sdk_callback_invoked"])

    def test_07_caller_supplied_asset_contract_is_exact(self) -> None:
        contract = self.report["caller_supplied_asset_contract"]
        self.assertEqual(contract, reference.CALLER_ASSET_CONTRACT)
        self.assertEqual(set(contract["required_fields"]),
                         reference.REQUIRED_ASSET_FIELDS)
        pinned = contract["pinned_values"]
        self.assertEqual(pinned["sample_rate_hz"], 16000)
        self.assertEqual(pinned["channels"], 1)
        self.assertEqual(pinned["source_revision"], reference.UPSTREAM_COMMIT)
        self.assertEqual(pinned["checkpoint_revision"], reference.HF_REVISION)
        self.assertEqual(pinned["checkpoint_sha256"], reference.CHECKPOINT_SHA256)
        self.assertEqual(pinned["sampler_type"], "stochastic")
        self.assertEqual(pinned["steps"], 1)
        self.assertEqual(pinned["snr"], 0.5)
        self.assertFalse(contract["asset_is_vendored"])

    def test_08_asset_is_absent_and_not_loaded(self) -> None:
        resolution = self.report["asset_resolution"]
        for key in ("requested", "manifest_present",
                    "checkpoint_present_in_sdk_worktree",
                    "checkpoint_present_in_external_checkout",
                    "source_checkout_present_in_sdk_worktree",
                    "runtime_environment_present", "verified", "loaded",
                    "executed"):
            self.assertIs(resolution[key], False, key)
        self.assertTrue(resolution["surrogate_used"])
        self.assertTrue(resolution["source_checkout_present_in_external_checkout"])
        self.assertFalse((reference.SOURCE_ROOT /
                          reference.CHECKPOINT_LEDGER_PATH).exists())
        self.assertFalse((SDK_ROOT /
                          reference.EXPECTED_CALLER_CHECKPOINT_PATH).exists())

    def test_09_surrogate_is_not_rose_cd(self) -> None:
        surrogate = self.report["surrogate"]
        self.assertEqual(surrogate["identity"],
                         "rose-cd-one-step-boundary-surrogate-v0")
        for key in ("is_rose_cd", "is_neural_network", "pytorch_used", "weights",
                    "checkpoint", "stft_model", "diffusion_sampler",
                    "quality_claim"):
            self.assertIs(surrogate[key], False, key)
        self.assertEqual(surrogate["delay_modeled_samples"], 0)
        self.assertEqual(surrogate["delay_compensated_samples"], 0)

    def test_10_all_conditions_present_and_outputs_finite(self) -> None:
        self.assertEqual(set(self.report["conditions"]), set(reference.CONDITIONS))
        for name, condition in self.report["conditions"].items():
            self.assertEqual(condition["input"]["samples"], 32000, name)
            self.assertEqual(condition["output"]["samples"], 32000, name)
            self.assertTrue(condition["input"]["finite"], name)
            self.assertTrue(condition["output"]["finite"], name)
            self.assertEqual(condition["output"]["clipped_or_nonfinite"], 0, name)
            self.assertEqual(condition["input"]["clipped_or_nonfinite"], 0, name)
            gate = condition["surrogate_gate"]
            self.assertEqual(gate["frame_count"], 200, name)
            self.assertEqual(gate["stft_frames"], 251, name)
            self.assertEqual(gate["reflection_pad_frames"], 5, name)
            self.assertTrue(gate["delay_compensated"], name)

    def test_11_paired_metric_deltas_are_consistent(self) -> None:
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

    def test_12_zero_reference_is_explicit_not_scored(self) -> None:
        self.assertEqual(
            self.report["conditions"]["noise_only"]["si_sdr_db"][
                "identity_invalid_reason"], "zero_reference_energy")
        self.assertEqual(
            self.report["conditions"]["noise_only"]["stoi"][
                "identity_invalid_reason"], "zero_reference")
        self.assertEqual(
            self.report["conditions"]["silence"]["stoi"][
                "identity_invalid_reason"], "zero_reference")
        self.assertIsNone(
            self.report["conditions"]["silence"]["si_sdr_db"]["paired_delta"])

    def test_13_alignment_is_exact_zero_delay(self) -> None:
        alignment = self.report["alignment"]
        self.assertEqual(alignment["expected_impulse_index"], 4000)
        self.assertEqual(alignment["uncompensated_impulse_index"], 4000)
        self.assertEqual(alignment["compensated_impulse_index"], 4000)
        self.assertEqual(alignment["measured_content_lag_samples"], 0)
        self.assertEqual(alignment["modeled_delay_samples"], 0)
        self.assertEqual(alignment["stft_frames"], 251)
        self.assertEqual(alignment["reflection_pad_frames"], 5)
        self.assertTrue(alignment["delay_compensation_applied"])
        self.assertFalse(alignment["sdk_callback_invoked"])

    def test_14_state_controls_pass(self) -> None:
        for key, value in self.report["state"].items():
            self.assertTrue(value, key)

    def test_15_caller_asset_controls_fail_closed(self) -> None:
        controls = self.report["controls"]["caller_asset"]
        self.assertTrue(controls["all_present"])
        self.assertTrue(controls["all_fail_closed"])
        self.assertEqual(controls["valid_manifest"],
                         {"status": "validated", "verified": True,
                          "loaded": False, "executed": False})
        for name in ("missing_manifest", "absent_checkpoint", "hash_mismatch",
                     "wrong_source_revision", "wrong_checkpoint_revision",
                     "wrong_sample_rate", "wrong_channels", "wrong_sampler_type",
                     "wrong_steps", "wrong_snr", "relative_path", "extra_field",
                     "missing_source_marker"):
            self.assertEqual(controls[name]["status"], "rejected", name)

    def test_16_frame_controls_fail_closed(self) -> None:
        controls = self.report["controls"]["frame"]
        self.assertTrue(controls["all_present"])
        self.assertTrue(controls["all_fail_closed"])
        for name in ("short_input", "two_dimensional_input", "nonfinite_input",
                     "out_of_range_input", "truncated_output",
                     "finish_called_twice"):
            self.assertEqual(controls[name]["status"], "rejected", name)
        self.assertEqual(controls["missing_reference"]["status"], "invalid")
        self.assertEqual(controls["silence_output"]["status"], "pass")
        self.assertTrue(controls["state_unchanged_after_rejection"])

    def test_17_adverse_matches_controls(self) -> None:
        adverse = self.report["adverse"]
        self.assertTrue(adverse["all_rejected"])
        self.assertTrue(adverse["all_invalid_cases_rejected"])
        self.assertTrue(adverse["valid_manifest_control_present"])
        self.assertEqual(adverse["config_rejections"],
                         self.report["controls"]["caller_asset"])
        self.assertEqual(adverse["frame_rejections"],
                         self.report["controls"]["frame"])

    def test_18_source_pins_match_files(self) -> None:
        self.assertEqual(self.report["source_pins"], reference.SOURCE_PINS)
        self.assertEqual(self.contract["source_pins"], reference.SOURCE_PINS)
        for path, digest in reference.SOURCE_PINS.items():
            actual = hashlib.sha256((reference.SOURCE_ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)

    def test_19_asset_pins_match_files(self) -> None:
        self.assertEqual(self.report["asset_pins"], reference.ASSET_PINS)
        for path, digest in reference.ASSET_PINS.items():
            actual = hashlib.sha256((reference.SOURCE_ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)

    def test_20_boundary_pins_match_worktree(self) -> None:
        self.assertEqual(self.report["boundary_pins"], reference.BOUNDARY_PINS)
        for path, digest in reference.BOUNDARY_PINS.items():
            actual = hashlib.sha256((SDK_ROOT / path).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path)

    def test_21_contract_digest_matches(self) -> None:
        self.assertEqual(CONTRACT.read_bytes(), reference.contract_bytes())
        self.assertEqual(self.report["contract_sha256"],
                         hashlib.sha256(CONTRACT.read_bytes()).hexdigest())
        self.assertEqual(self.readiness["contract_sha256"],
                         hashlib.sha256(CONTRACT.read_bytes()).hexdigest())

    def test_22_readiness_is_strict_and_blocked(self) -> None:
        self.assertEqual(READINESS.read_bytes(), reference.readiness_bytes())
        self.assertEqual(self.readiness["report_sha256"],
                         hashlib.sha256(REPORT.read_bytes()).hexdigest())
        for key in ("ready_for_opt_in_adapter", "ready_for_provider_registration",
                    "ready_for_release", "quality_pass"):
            self.assertIs(self.readiness[key], False, key)
        self.assertEqual(self.readiness["blocked_gates"],
                         [name for name, _ in reference.GATE_DEFINITIONS])
        self.assertEqual(self.readiness["exact_blocker"],
                         reference.EXACT_BLOCKERS[0])
        external = self.readiness["external_asset"]
        self.assertTrue(external["required"])
        for key in ("present", "loaded", "executed",
                    "runtime_environment_present"):
            self.assertIs(external[key], False, key)
        self.assertEqual(external["expected_checkpoint_sha256"],
                         reference.CHECKPOINT_SHA256)
        self.assertEqual(external["expected_checkpoint_bytes"],
                         reference.CHECKPOINT_BYTES)

    def test_23_adapter_is_task_local_and_not_implemented(self) -> None:
        self.assertEqual(ADAPTER.read_bytes(), reference.adapter_bytes())
        self.assertEqual(self.adapter["task_id"], reference.TASK)
        self.assertTrue(self.adapter["task_local"])
        for key in ("implemented", "registered", "enabled_by_default",
                    "default_selected", "public_api_abi_change",
                    "provider_registration", "descriptor_registry_change",
                    "installed_v0_behavior_change", "asset_present"):
            self.assertIs(self.adapter[key], False, key)
        self.assertTrue(self.adapter["caller_supplied_asset_required"])
        self.assertEqual(self.adapter["activation"], "deferred_until_gates_clear")
        self.assertIsNone(self.adapter["entrypoint"])

    def test_24_all_gates_blocked_with_reopen_conditions(self) -> None:
        self.assertEqual(len(self.report["gates"]),
                         len(reference.GATE_DEFINITIONS))
        self.assertEqual(len(self.report["gates"]), 10)
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen_condition"])
        self.assertEqual(self.report["exact_blockers"],
                         reference.EXACT_BLOCKERS)
        self.assertEqual(self.report["missing_evidence"],
                         reference.MISSING_EVIDENCE)
        self.assertEqual(self.report["reopening_conditions"],
                         reference.REOPENING_CONDITIONS)

    def test_25_repeatability_is_three_identical_cold_starts(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)
        self.assertEqual(repeat["digests"][0],
                         hashlib.sha256(reference.canonical_bytes({
                             key: value for key, value in self.report.items()
                             if key != "repeatability"})).hexdigest())

    def test_26_source_reported_values_are_provenance_only(self) -> None:
        source = self.report["source_reported"]
        self.assertEqual(source["status"], "source_reported_not_reproduced")
        self.assertFalse(source["used_for_qualification"])
        self.assertTrue(source["findings"])
        self.assertTrue(source["unavailable"])

    def test_27_licensing_rights_remain_blocked(self) -> None:
        licensing = self.report["licensing_analysis"]
        for key in ("checkpoint_redistribution_clearance",
                    "product_use_clearance",
                    "training_data_provenance_established",
                    "legal_review_completed",
                    "asset_copied_vendored_built_or_downloaded"):
            self.assertIs(licensing[key], False, key)
        self.assertEqual(licensing["blocked_gate"],
                         "checkpoint_and_runtime_rights")
        self.assertEqual(licensing["upstream_license_sha256"],
                         reference.ASSET_PINS[reference.UPSTREAM_LICENSE_PATH])

    def test_28_strict_parsers_reject_bad_inputs(self) -> None:
        result = reference.strict_rejection_examples()
        self.assertEqual(result["bad_json_rejected"], result["bad_json_total"])
        self.assertEqual(result["bad_pins_rejected"], result["bad_pins_total"])

    def test_29_sources_manifest_is_complete_and_deterministic(self) -> None:
        self.assertEqual(PINS.read_bytes(), reference.sources_bytes())
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
        self.assertEqual({raw for _, raw in pins}, reference.allowed_pin_keys())
        self.assertEqual(len(pins), len(reference.allowed_pin_keys()))

    def test_30_base_commit_and_branch_are_pinned(self) -> None:
        self.assertEqual(self.report["base_commit"],
                         "871201c187c42291410245344aacee5c80051b48")
        self.assertEqual(self.report["branch"],
                         "swarm/SDK-ROSE-CD-ONE-STEP")

    def test_31_upstream_identity_and_checkpoint_absence(self) -> None:
        identity = reference.upstream_git_identity()
        self.assertEqual(identity["normalized_remote"],
                         reference.UPSTREAM_REPOSITORY)
        self.assertEqual(identity["commit"], reference.UPSTREAM_COMMIT)
        self.assertTrue(identity["pinned_commit_present"])
        self.assertFalse((reference.SOURCE_ROOT /
                          reference.CHECKPOINT_LEDGER_PATH).exists())

    def test_32_no_prohibited_real_model_audio_device_or_release_claim(self) -> None:
        for key, value in self.report["negative_claims"].items():
            self.assertIs(value, False, key)
        for key in ("caller_supplied_asset_present", "rose_cd_source_executed",
                    "rose_cd_runtime_executed", "rose_cd_checkpoint_loaded",
                    "model_weights_downloaded", "model_weights_loaded",
                    "real_audio", "real_labels", "network_used", "device_timing",
                    "listening_result", "benchmark_claim", "release_claim",
                    "registered_provider"):
            self.assertIs(self.report["scope"][key], False, key)

    def test_33_enhancement_profile_is_explicitly_mapped(self) -> None:
        profile = self.report["enhancement_profile"]
        self.assertEqual(profile["name"], "enhancement")
        self.assertEqual(profile["identity_noisy_control"],
                         "present: unprocessed input is the baseline")
        self.assertEqual(profile["paired_metrics"],
                         {"si_sdr": "synthetic_only", "stoi": "synthetic_only",
                          "snr": "synthetic_only"})
        self.assertEqual(profile["clean_speech_preservation"], "synthetic_only")
        self.assertEqual(profile["task_matched_baseline"], "not_reproduced")
        self.assertEqual(profile["content_availability_timing"],
                         "blocked_unmeasured")
        self.assertEqual(profile["listening"], "not_run")
        for key in ("real_audio", "real_clean_references", "device_timing",
                    "memory_measured", "quality_claim"):
            self.assertIs(profile[key], False, key)

    def test_34_offline_whole_clip_boundary_and_chunk_independence(self) -> None:
        signal = reference.stimuli()["noisy_snr10"]
        reference_output, _ = reference.process_reference(signal)
        sizes = (1, 7, 80, 159, 160, 161, 320, 1280, 32000)
        for size in sizes:
            chunks = [size] * (signal.size // size)
            if signal.size % size:
                chunks.append(signal.size % size)
            output, _ = reference.process_reference(signal, chunk_sizes=chunks)
            self.assertEqual(reference._f32_sha256(output),
                             reference._f32_sha256(reference_output), size)
        self.assertTrue(self.report["state"]["output_independent_of_chunking"])

    def test_35_minimum_stft_frame_boundary_and_padding(self) -> None:
        self.assertEqual(reference.MIN_ASSET_SAMPLES, 8064)
        self.assertEqual(reference._stft_frame_count(8064), 64)
        self.assertEqual(reference._reflection_pad_frames(8064), 0)
        self.assertEqual(reference._stft_frame_count(32000), 251)
        self.assertEqual(reference._reflection_pad_frames(32000), 5)
        model = reference.Surrogate()
        signal = reference.stimuli()["clean"][:reference.MIN_ASSET_SAMPLES]
        output, info = model.process(signal)
        self.assertEqual(output.size, reference.MIN_ASSET_SAMPLES)
        self.assertEqual(info["stft_frames"], 64)
        self.assertEqual(info["reflection_pad_frames"], 0)

    def test_36_peak_normalization_round_trip_preserves_clean_input(self) -> None:
        clean = reference.stimuli()["clean_only"]
        output, info = reference.process_reference(clean)
        self.assertEqual(reference._f32_sha256(output),
                         reference._f32_sha256(clean))
        self.assertEqual(info["norm_factor"], 0.5)
        self.assertEqual(info["nfe"], 1)

    def test_37_silence_is_exact_zero_without_model_evaluation(self) -> None:
        zeros = reference.stimuli()["silence"]
        output, info = reference.process_reference(zeros)
        self.assertEqual(float(abs(output).max()), 0.0)
        self.assertEqual(info["nfe"], 0)
        self.assertEqual(info["norm_factor"], 0.0)

    def test_38_readme_digest_table_covers_external_pins(self) -> None:
        rows = reference.readme_pin_rows()
        self.assertTrue(rows)
        seen = dict(rows)
        self.assertEqual(len(seen), len(rows))
        external = {**reference.SOURCE_PINS, **reference.ASSET_PINS}
        self.assertEqual(set(seen), set(external))
        for path, digest in external.items():
            target = reference.qualify_pin_path(path)
            self.assertTrue(target.is_file(), path)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),
                             digest, path)
            self.assertEqual(seen[path], digest, path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
