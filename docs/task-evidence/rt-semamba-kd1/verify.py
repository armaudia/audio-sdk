# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-RT-SEMAMBA-KD1 evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins,
stale digests, a stale README source or artifact digest table, invalid/missing/
nonfinite case acceptance, unpinned or vendored files, license gaps,
out-of-scope worktree changes, whitespace damage or a dirty diff check. Never
writes.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
READINESS = HERE / "readiness.json"
ADAPTER = HERE / "adapter.json"
README = HERE / "README.md"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "adapter.json.license",
    "contract.json.license",
    "readiness.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "requirements.lock.license",
)
REQUIRED_REPORT_KEYS = {
    "schema_id", "task_id", "title", "component_id", "base_commit", "branch",
    "profile", "status", "evidence_status", "qualification_status", "decision",
    "defer_before", "no_missing_result_qualifies_candidate", "scope",
    "negative_claims", "boundary", "format", "enhancement_boundary",
    "enhancement_profile", "caller_supplied_asset_contract",
    "asset_resolution", "surrogate", "stimuli", "timestamp_calibration",
    "conditions", "stratification", "clean_preservation", "peaks_and_invalid",
    "alignment", "state", "controls", "adverse", "comparison", "regressions",
    "timing", "memory", "source_reported", "model_provenance",
    "licensing_analysis", "source_pins", "asset_pins", "boundary_pins",
    "gates", "exact_blockers", "missing_evidence", "reopening_conditions",
    "evidence_classes", "contract_sha256", "repeatability",
}
REQUIRED_READINESS_KEYS = {
    "schema_id", "task_id", "title", "profile", "decision", "evidence_status",
    "qualification_status", "defer_before", "ready_for_opt_in_adapter",
    "ready_for_provider_registration", "ready_for_release", "quality_pass",
    "enhancement_acceptance_cleared", "report_sha256", "contract_sha256",
    "blocked_gates", "exact_blocker", "reopen_condition", "external_asset",
    "scope", "negative_claims",
}
REQUIRED_ADAPTER_KEYS = {
    "schema_id", "task_id", "task_local", "implemented", "registered",
    "enabled_by_default", "default_selected", "descriptor_settings",
    "public_api_abi_change", "provider_registration",
    "descriptor_registry_change", "installed_v0_behavior_change",
    "shared_build_or_ci_change", "input_kind", "output_kinds", "tasks",
    "modes", "weights", "caller_supplied_asset_required", "asset_present",
    "streaming_supported", "activation", "entrypoint", "note",
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".lock", ".license", ".txt"}
BINARY_SUFFIXES = (
    ".dylib", ".so", ".dll", ".onnx", ".tar", ".gz", ".ckpt", ".pt",
    ".pth", ".safetensors", ".wav", ".flac", ".mp3",
)


def _strict_json(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + label + ":" + str(error))
        return {}
    if not isinstance(payload, dict):
        errors.append("json_root_not_object:" + label)
        return {}
    return payload


def check_pins(errors: List[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    try:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_pin_rejection:" + str(error))
        return 0
    expected = reference.allowed_pin_keys()
    if len(pins) != len(expected):
        errors.append("incomplete_pin_manifest")
    for digest, raw in pins:
        if raw.startswith("source:"):
            path = reference.SOURCE_ROOT / raw.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw
        if not path.is_file():
            errors.append("pin_target_missing:" + raw)
        elif reference.sha256(path.read_bytes()) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("SOURCES.sha256_not_deterministic_bytes")
    return len(pins)


def check_readme_digest_tables(errors: List[str]) -> int:
    if not README.is_file():
        errors.append("README.md missing")
        return 0
    try:
        source_rows = reference.readme_source_rows()
        artifact_rows = reference.readme_artifact_rows()
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_table_unreadable:" + str(error))
        return 0
    if not source_rows:
        errors.append("readme_source_digest_table_missing")
    if not artifact_rows:
        errors.append("readme_artifact_digest_table_missing")
    seen_sources: Dict[str, str] = {}
    for path, digest in source_rows:
        if path in seen_sources:
            errors.append("readme_duplicate_source_row:" + path)
            continue
        seen_sources[path] = digest
        try:
            target = reference.qualify_pin_path(path)
        except ValueError as error:
            errors.append("readme_source_row_path_invalid:" + str(error))
            continue
        if not target.is_file():
            errors.append("readme_source_row_target_missing:" + path)
        elif reference.sha256(target.read_bytes()) != digest:
            errors.append("readme_source_row_digest_stale:" + path)
    external = {**reference.SOURCE_PINS, **reference.ASSET_PINS}
    for path in sorted(set(external) - set(seen_sources)):
        errors.append("readme_source_row_missing:" + path)
    for path in sorted(set(seen_sources) - set(external)):
        errors.append("readme_source_row_unexpected:" + path)
    for path, digest in external.items():
        if seen_sources.get(path) not in (None, digest):
            errors.append("readme_source_row_pin_disagreement:" + path)
    seen_artifacts: Dict[str, str] = {}
    for name, digest, size in artifact_rows:
        if name in seen_artifacts:
            errors.append("readme_duplicate_artifact_row:" + name)
            continue
        seen_artifacts[name] = digest
        if "/" in name or name.startswith(".."):
            errors.append("readme_artifact_row_path_invalid:" + name)
            continue
        target = HERE / name
        if not target.is_file():
            errors.append("readme_artifact_row_target_missing:" + name)
            continue
        data = target.read_bytes()
        if reference.sha256(data) != digest:
            errors.append("readme_artifact_row_digest_stale:" + name)
        if len(data) != size:
            errors.append("readme_artifact_row_bytes_stale:" + name)
    expected_artifacts = set(reference.ARTIFACT_TABLE_PATHS)
    for name in sorted(expected_artifacts - set(seen_artifacts)):
        errors.append("readme_artifact_row_missing:" + name)
    for name in sorted(set(seen_artifacts) - expected_artifacts):
        errors.append("readme_artifact_row_unexpected:" + name)
    return len(source_rows) + len(artifact_rows)


def check_json(errors: List[str]) -> Dict[str, Dict[str, Any]]:
    payloads = {
        "contract": _strict_json(CONTRACT, errors, "contract"),
        "report": _strict_json(REPORT, errors, "report"),
        "readiness": _strict_json(READINESS, errors, "readiness"),
        "adapter": _strict_json(ADAPTER, errors, "adapter"),
    }
    if not all(payloads.values()):
        return payloads
    if CONTRACT.read_bytes() != reference.contract_bytes():
        errors.append("contract_not_canonical_bytes")
    if REPORT.read_bytes() != reference.canonical_report_bytes(payloads["report"]):
        errors.append("report_not_canonical_bytes")
    if READINESS.read_bytes() != reference.readiness_bytes():
        errors.append("readiness_not_canonical_bytes")
    if ADAPTER.read_bytes() != reference.adapter_bytes():
        errors.append("adapter_not_canonical_bytes")
    report_digest = reference.sha256(REPORT.read_bytes())
    expected_sidecar = f"{report_digest}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    if payloads["report"].get("contract_sha256") != reference.sha256(
            CONTRACT.read_bytes()):
        errors.append("report_contract_digest_mismatch")
    if payloads["readiness"].get("report_sha256") != report_digest:
        errors.append("readiness_report_digest_mismatch")
    if payloads["readiness"].get("contract_sha256") != reference.sha256(
            CONTRACT.read_bytes()):
        errors.append("readiness_contract_digest_mismatch")
    for name, payload in payloads.items():
        if reference.has_negative_zero(payload):
            errors.append("negative_zero_in_artifact:" + name)
    return payloads


def check_content(errors: List[str], payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]
    readiness = payloads["readiness"]
    adapter = payloads["adapter"]
    missing = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing:
        errors.append("report_missing_keys:" + ",".join(missing))
        return
    missing = sorted(REQUIRED_READINESS_KEYS - set(readiness))
    if missing:
        errors.append("readiness_missing_keys:" + ",".join(missing))
    missing = sorted(REQUIRED_ADAPTER_KEYS - set(adapter))
    if missing:
        errors.append("adapter_missing_keys:" + ",".join(missing))
    if report["base_commit"] != reference.BASE_COMMIT:
        errors.append("base_commit_mismatch")
    if report["branch"] != reference.BRANCH:
        errors.append("branch_mismatch")
    if report["profile"] != reference.PROFILE or \
            contract.get("profile") != reference.PROFILE:
        errors.append("profile_not_applied")
    if report["component_id"] != reference.SLUG:
        errors.append("component_id_mismatch")
    for key, expected in (
            ("task_id", reference.TASK),
            ("status", reference.STATUS),
            ("evidence_status", reference.EVIDENCE_STATUS),
            ("qualification_status", reference.QUALIFICATION),
            ("decision", reference.DECISION),
            ("defer_before", reference.DEFER_BEFORE)):
        if report.get(key) != expected:
            errors.append("disposition_mismatch:" + key)
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")
    boundary_false = (
        "registered", "enabled_by_default", "default_selected",
        "public_api_abi_change", "provider_registration",
        "descriptor_registry_change", "shared_cmakelists_change",
        "installed_v0_behavior_change", "processor_exposure", "ci_change",
    )
    for key in boundary_false:
        if report["boundary"].get(key) is not False or \
                contract["boundary"].get(key) is not False:
            errors.append("boundary_not_false:" + key)
    if report["boundary"].get("descriptor_settings") != {}:
        errors.append("descriptor_settings_not_empty")
    fmt = report["format"]
    for key, value in (
            ("public_sample_rate_hz", 16000), ("public_channels", 1),
            ("public_sample_format", "f32"), ("public_frame_samples", 160),
            ("public_frame_duration_ms", 10),
            ("asset_sample_rate_hz", 16000), ("asset_channels", 1),
            ("asset_window_samples", 400), ("asset_window_duration_ms", 25),
            ("asset_hop_samples", 100), ("asset_hop_duration_ms", 6.25),
            ("asset_chunk_samples", 1600), ("asset_chunk_duration_ms", 100),
            ("asset_is_native_16k", True), ("resampling_required", False),
            ("clip_samples", 32000), ("clip_duration_ms", 2000),
            ("public_v0_geometry_preserved", True),
            ("sdk_callback_invoked", False)):
        if fmt.get(key) != value:
            errors.append("format_mismatch:" + key)
    eb = report["enhancement_boundary"]
    for key, value in (
            ("upstream_streaming_capable", True),
            ("streaming_path_evaluated", False),
            ("stft_window_samples", 400), ("stft_hop_samples", 100),
            ("stft_center", False),
            ("algorithmic_latency_samples", 400),
            ("algorithmic_latency_ms", 25),
            ("realtime_chunk_samples", 1600), ("realtime_chunk_ms", 100),
            ("parameter_count", 1050000),
            ("parameter_count_is_source_reported", True),
            ("vctk_demand_training_and_evaluation", True),
            ("adapter_device", "cpu"), ("adapter_rejects_non_cpu", True),
            ("mps_available_on_research_host", False),
            ("cuda_available_on_research_host", False)):
        if eb.get(key) != value:
            errors.append("enhancement_boundary_mismatch:" + key)
    profile = report["enhancement_profile"]
    if profile.get("identity_noisy_control") is not True or \
            profile.get("peak_and_invalid_output_check") is not True:
        errors.append("enhancement_profile_controls_missing")
    for key in ("paired_si_sdr", "paired_stoi", "clean_speech_preservation"):
        if profile.get(key) in (None, "", "real", "measured"):
            errors.append("enhancement_profile_overclaim:" + key)
    for key in ("established_task_matched_baseline_reproduced",
                "real_cohort_scored"):
        if profile.get(key) is not False:
            errors.append("enhancement_profile_claim:" + key)
    for key in ("independent_listening", "memory",
                "content_availability_timing", "target_runtime"):
        if profile.get(key) == "measured":
            errors.append("enhancement_profile_unmeasured_claim:" + key)
    for key in ("task_local_only", "synthetic_boundary_surrogate_only",
                "caller_supplied_asset_contract_modeled"):
        if report["scope"].get(key) is not True:
            errors.append("scope_true_missing:" + key)
    for key in ("caller_supplied_asset_present", "rt_semamba_source_executed",
                "rt_semamba_runtime_executed", "rt_semamba_checkpoint_loaded",
                "pytorch_imported", "mamba_package_imported",
                "model_weights_downloaded", "model_weights_loaded",
                "real_audio", "real_labels", "network_used", "device_timing",
                "listening_result", "benchmark_claim", "release_claim",
                "registered_provider"):
        if report["scope"].get(key) is not False:
            errors.append("scope_claim:" + key)
    for key, value in report["negative_claims"].items():
        if value is not False:
            errors.append("prohibited_claim:" + key)
    for name, expected in (
            ("real_audio_used", False),
            ("real_speaker_labels_used", False),
            ("listening_performed", False),
            ("device_timing_measured", False),
            ("streaming_behavior_verified", False),
            ("quality_pass", False),
            ("exact_rt_semamba_reproduction_claimed", False)):
        if report["negative_claims"].get(name) is not expected:
            errors.append("prohibited_claim:" + name)
    asset_contract = report["caller_supplied_asset_contract"]
    if asset_contract != reference.CALLER_ASSET_CONTRACT:
        errors.append("caller_asset_contract_mismatch")
    if set(asset_contract.get("required_fields", [])) != \
            reference.REQUIRED_ASSET_FIELDS:
        errors.append("caller_asset_fields_mismatch")
    resolution = report["asset_resolution"]
    for key in ("requested", "manifest_present",
                "checkpoint_present_in_sdk_worktree",
                "config_present_in_sdk_worktree",
                "source_tree_present_in_sdk_worktree",
                "runtime_installed_in_sdk_worktree", "verified", "loaded",
                "executed"):
        if resolution.get(key) is not False:
            errors.append("asset_resolution_claim:" + key)
    if resolution.get("surrogate_used") is not True:
        errors.append("surrogate_not_used")
    for key in ("checkpoint_present_in_external_checkout",
                "config_present_in_external_checkout",
                "source_tree_present_in_external_checkout"):
        if resolution.get(key) is not True:
            errors.append("external_asset_claim:" + key)
    surrogate = report["surrogate"]
    for key in ("is_rt_semamba", "is_neural_network", "ctf_mamba_blocks",
                "ssm_state", "checkpoint", "weights", "pytorch",
                "quality_claim"):
        if surrogate.get(key) is not False:
            errors.append("surrogate_claim:" + key)
    if surrogate.get("identity") != "rt-semamba-kd1-boundary-surrogate-v0":
        errors.append("surrogate_identity_mismatch")
    for key, value in (
            ("window_samples", 400), ("hop_samples", 100),
            ("noise_estimate_frames", 5), ("noise_attack_beta", 1.5),
            ("gate_floor", 0.2), ("delay_modeled_samples", 400),
            ("delay_compensated_samples", 400), ("peak_guard", 0.95),
            ("deterministic", True), ("pure_synthetic", True)):
        if surrogate.get(key) != value:
            errors.append("surrogate_config_mismatch:" + key)
    stimuli = report["stimuli"]
    if stimuli.get("snr_db_strata") != list(reference.SNR_DB_STRATA):
        errors.append("stimuli_strata_mismatch")
    for key in ("real_audio", "room_model"):
        if stimuli.get(key) is not False:
            errors.append("stimuli_claim:" + key)
    if stimuli.get("peak_guard") != reference.PEAK_GUARD:
        errors.append("stimuli_peak_guard_mismatch")
    if stimuli.get("clip_samples") != reference.CLIP_SAMPLES:
        errors.append("stimuli_clip_mismatch")
    calibration = report["timestamp_calibration"]
    if calibration.get("clock_id") != reference.CLOCK_ID:
        errors.append("clock_id_mismatch")
    if calibration.get("ns_per_sample") != reference.NS_PER_SAMPLE:
        errors.append("clock_rate_mismatch")
    if calibration.get("measured") is not False:
        errors.append("clock_measured_claim")
    if calibration.get("monotonic_nondecreasing") is not True:
        errors.append("clock_not_monotonic")
    conditions = report["conditions"]
    if set(conditions) != set(reference.CONDITIONS):
        errors.append("condition_set_mismatch")
    expected_frames = 1 + (reference.CLIP_SAMPLES +
                           2 * reference.ASSET_WINDOW_SAMPLES -
                           reference.ASSET_WINDOW_SAMPLES) // \
        reference.ASSET_HOP_SAMPLES
    for name, condition in conditions.items():
        if condition["input"]["samples"] != reference.CLIP_SAMPLES:
            errors.append("input_samples_wrong:" + name)
        if condition["output"]["samples"] != reference.CLIP_SAMPLES:
            errors.append("output_samples_wrong:" + name)
        if condition["input"]["finite"] is not True or \
                condition["output"]["finite"] is not True:
            errors.append("nonfinite_condition:" + name)
        if condition["output"]["clipped_or_nonfinite"] != 0:
            errors.append("output_clipped_or_nonfinite:" + name)
        if condition["input"]["clipped_or_nonfinite"] != 0:
            errors.append("guarded_input_clipped:" + name)
        for metric_name in ("snr_db", "si_sdr_db", "stoi"):
            metric = condition[metric_name]
            identity = metric["identity_noisy"]
            provider = metric["provider_surrogate"]
            delta = metric["paired_delta"]
            if identity is not None and provider is not None:
                if delta is None or abs(delta - (provider - identity)) > 1e-6:
                    errors.append("paired_delta_wrong:" + name + ":" + metric_name)
            elif delta is not None:
                errors.append("paired_delta_without_both:" + name + ":" +
                              metric_name)
        if condition["surrogate_mask"]["frame_count"] != expected_frames:
            errors.append("mask_frame_count_wrong:" + name)
        if condition["surrogate_mask"]["delay_compensated"] is not True:
            errors.append("mask_not_compensated:" + name)
        if name in reference.STRATUM_CONDITIONS:
            for metric_name in ("snr_db", "si_sdr_db", "stoi"):
                if condition[metric_name]["identity_noisy"] is None or \
                        condition[metric_name]["provider_surrogate"] is None or \
                        condition[metric_name]["paired_delta"] is None:
                    errors.append("stratum_metric_missing:" + name + ":" +
                                  metric_name)
        else:
            if condition["reference"] != "none" and name != "clean_control":
                errors.append("non_stratum_reference_unexpected:" + name)
            if name in ("idle_noise", "silence"):
                for metric_name in ("snr_db", "si_sdr_db", "stoi"):
                    if condition[metric_name]["identity_noisy"] is not None or \
                            condition[metric_name]["provider_surrogate"] is not None:
                        errors.append("zero_reference_scored:" + name + ":" +
                                      metric_name)
    clean = conditions["clean_control"]
    if clean["input"]["waveform_sha256"] != clean["output"]["waveform_sha256"]:
        errors.append("clean_control_not_exact")
    if clean["si_sdr_db"]["provider_invalid_reason"] != \
            "zero_error_identity_exact":
        errors.append("clean_control_si_sdr_not_exact")
    if clean["stoi"]["provider_surrogate"] != 1.0:
        errors.append("clean_control_stoi_not_one")
    if conditions["idle_noise"]["stoi"]["provider_invalid_reason"] != \
            "missing_reference_or_output":
        errors.append("idle_noise_not_zero_reference")
    if conditions["silence"]["snr_db"]["provider_invalid_reason"] != \
            "missing_reference_or_output":
        errors.append("silence_not_zero_reference")
    if conditions["noisy_snr20"]["surrogate_mask"]["noise_estimate"] is None:
        errors.append("noise_estimate_missing")
    if report["stratification"] != [
            {"condition": name,
             "snr_db": conditions[name]["snr_db"]["identity_noisy"],
             "source_pair_count": 1,
             "independent_items": False,
             "held_out": False}
            for name in reference.STRATUM_CONDITIONS]:
        errors.append("stratification_mismatch")
    if report["clean_preservation"] != reference._clean_preservation(conditions):
        errors.append("clean_preservation_mismatch")
    if report["peaks_and_invalid"] != reference._peaks(conditions):
        errors.append("peaks_mismatch")
    if report["peaks_and_invalid"].get("all_outputs_finite") is not True or \
            report["peaks_and_invalid"].get("total_clipped_or_nonfinite") != 0:
        errors.append("peaks_invalid")
    alignment = report["alignment"]
    for key, value in (
            ("expected_impulse_index", 4000),
            ("uncompensated_impulse_index", 4400),
            ("compensated_impulse_index", 4000),
            ("measured_content_lag_samples", 0),
            ("modeled_window_delay_samples", 400),
            ("modeled_window_delay_ms", 25),
            ("algorithmic_latency_samples", 400),
            ("algorithmic_latency_ms", 25),
            ("delay_compensation_applied", True),
            ("valid_output_samples", 32000),
            ("sdk_callback_invoked", False)):
        if alignment.get(key) != value:
            errors.append("alignment_mismatch:" + key)
    for key, value in report["state"].items():
        if value is not True:
            errors.append("state_control_failed:" + key)
    for key in ("identity", "clean_control", "idle_noise", "silence"):
        if report["controls"].get(key, {}).get("status") != "present":
            errors.append("control_missing:" + key)
    caller_asset = report["controls"]["caller_asset"]
    frame_control = report["controls"]["frame"]
    if caller_asset.get("all_present") is not True or \
            caller_asset.get("all_fail_closed") is not True:
        errors.append("caller_asset_controls_incomplete")
    if caller_asset["valid_manifest"] != {
            "status": "validated", "verified": True, "loaded": False,
            "executed": False}:
        errors.append("valid_manifest_scope_wrong")
    for name in ("missing_manifest", "absent_file", "checkpoint_hash_mismatch",
                 "config_hash_mismatch", "wrong_source_revision",
                 "wrong_sample_rate", "wrong_channels", "wrong_window_samples",
                 "wrong_hop_samples", "wrong_algorithm_latency",
                 "relative_path", "extra_field"):
        if caller_asset[name].get("status") != "rejected":
            errors.append("caller_asset_not_rejected:" + name)
    if frame_control.get("all_present") is not True or \
            frame_control.get("all_fail_closed") is not True:
        errors.append("frame_controls_incomplete")
    for name in ("short_input", "two_dimensional_input", "nonfinite_input",
                 "truncated_output", "wrong_sample_rate", "wrong_channels",
                 "wrong_window_samples", "wrong_hop_samples"):
        if frame_control[name].get("status") != "rejected":
            errors.append("frame_control_not_rejected:" + name)
    if frame_control["missing_reference"].get("status") != "invalid":
        errors.append("missing_reference_not_invalid")
    if frame_control["silence_output"].get("status") != "pass":
        errors.append("silence_output_not_pass")
    if frame_control.get("state_unchanged_after_rejection") is not True:
        errors.append("state_changed_after_rejection")
    adverse = report["adverse"]
    if adverse.get("all_rejected") is not True:
        errors.append("adverse_all_rejected_false")
    if adverse.get("all_invalid_cases_rejected") is not True:
        errors.append("adverse_invalid_cases_not_rejected")
    if adverse.get("valid_manifest_control_present") is not True:
        errors.append("adverse_valid_manifest_control_missing")
    if adverse.get("config_rejections") != caller_asset:
        errors.append("adverse_config_mismatch")
    if adverse.get("frame_rejections") != frame_control:
        errors.append("adverse_frame_mismatch")
    comparison = report["comparison"]
    if comparison.get("quality_pass") is not False:
        errors.append("quality_pass_claimed")
    if comparison.get("established_task_matched_baseline_reproduced") is not False:
        errors.append("baseline_reproduction_claimed")
    if comparison.get(
            "source_reported_candidate_screen_used_for_qualification") is not False:
        errors.append("source_reported_used_for_qualification")
    if comparison.get("regression_count") != len(report["regressions"]):
        errors.append("regression_count_mismatch")
    if report["regressions"] != reference._regressions(conditions):
        errors.append("regressions_mismatch")
    timing = report["timing"]
    for key in ("measured", "device_timing", "paced"):
        if timing.get(key) is not False:
            errors.append("timing_claim:" + key)
    if timing.get("modeled_algorithm_latency_samples") != 400 or \
            timing.get("modeled_algorithm_latency_ms") != 25:
        errors.append("timing_latency_mismatch")
    memory = report["memory"]
    if memory.get("measured") is not False or \
            memory.get("device_memory_measured") is not False:
        errors.append("memory_claim")
    if memory.get("source_reported_process_peak_rss_bytes") != 3219685376:
        errors.append("memory_source_value_mismatch")
    source_reported = report["source_reported"]
    if source_reported.get("status") != "source_reported_not_reproduced":
        errors.append("source_reported_not_labeled")
    if source_reported.get("used_for_qualification") is not False:
        errors.append("source_reported_used_for_qualification")
    if not source_reported.get("findings"):
        errors.append("source_reported_findings_missing")
    provenance = report["model_provenance"]
    if provenance.get("upstream_commit") != reference.UPSTREAM_COMMIT:
        errors.append("upstream_commit_mismatch")
    if provenance.get("upstream_license") != reference.UPSTREAM_LICENSE:
        errors.append("upstream_license_mismatch")
    if provenance.get("upstream_repository") != reference.UPSTREAM_REPOSITORY:
        errors.append("upstream_repository_mismatch")
    checkpoint = provenance.get("checkpoint", {})
    if checkpoint.get("sha256") != reference.CHECKPOINT_SHA256:
        errors.append("checkpoint_digest_mismatch")
    if checkpoint.get("bytes") != reference.CHECKPOINT_BYTES:
        errors.append("checkpoint_bytes_mismatch")
    if checkpoint.get("present_in_sdk_worktree") is not False:
        errors.append("checkpoint_present_claim")
    for key in ("downloaded_by_this_package", "copied_or_vendored",
                "loaded_or_executed"):
        if checkpoint.get(key) is not False:
            errors.append("checkpoint_scope:" + key)
    config = provenance.get("config", {})
    if config.get("sha256") != reference.CONFIG_SHA256:
        errors.append("config_digest_mismatch")
    if config.get("present_in_sdk_worktree") is not False:
        errors.append("config_present_claim")
    unused = provenance.get("unused_teacher_checkpoint", {})
    if unused.get("used") is not False:
        errors.append("teacher_checkpoint_claimed")
    runtime = provenance.get("runtime", {})
    if runtime.get("runtime_installed_in_sdk_worktree") is not False or \
            runtime.get("loaded_or_executed") is not False:
        errors.append("runtime_scope_claim")
    public_adapter = provenance.get("public_adapter", {})
    if public_adapter.get("present_in_research_workspace") is not True:
        errors.append("public_adapter_research_presence_missing")
    if public_adapter.get("present_in_sdk_worktree") is not False:
        errors.append("public_adapter_sdk_presence_claim")
    if public_adapter.get("executed_by_this_package") is not False:
        errors.append("public_adapter_execution_claim")
    licensing = report["licensing_analysis"]
    for key in ("checkpoint_redistribution_clearance",
                "runtime_redistribution_clearance", "product_use_clearance",
                "training_data_provenance_established", "legal_review_completed",
                "asset_copied_vendored_built_or_downloaded"):
        if licensing.get(key) is not False:
            errors.append("licensing_rights_claimed:" + key)
    if licensing.get("blocked_gate") != "artifact_and_runtime_rights":
        errors.append("licensing_gate_mismatch")
    if licensing.get("upstream_license_sha256") != reference.ASSET_PINS[
            reference.UPSTREAM_LICENSE_PATH]:
        errors.append("licensing_license_pin_mismatch")
    if report["source_pins"] != reference.SOURCE_PINS:
        errors.append("report_source_pins_mismatch")
    if report["asset_pins"] != reference.ASSET_PINS:
        errors.append("report_asset_pins_mismatch")
    if report["boundary_pins"] != reference.BOUNDARY_PINS:
        errors.append("report_boundary_pins_mismatch")
    if contract.get("source_pins") != reference.SOURCE_PINS:
        errors.append("contract_source_pins_mismatch")
    if contract.get("asset_pins") != reference.ASSET_PINS:
        errors.append("contract_asset_pins_mismatch")
    if contract.get("boundary_pins") != reference.BOUNDARY_PINS:
        errors.append("contract_boundary_pins_mismatch")
    if contract.get("enhancement_boundary") != reference.ENHANCEMENT_BOUNDARY:
        errors.append("contract_enhancement_boundary_mismatch")
    if report["exact_blockers"] != reference.EXACT_BLOCKERS:
        errors.append("exact_blockers_mismatch")
    if report["missing_evidence"] != reference.MISSING_EVIDENCE:
        errors.append("missing_evidence_mismatch")
    if report["reopening_conditions"] != reference.REOPENING_CONDITIONS:
        errors.append("reopening_conditions_mismatch")
    if len(report["gates"]) != len(reference.GATE_DEFINITIONS):
        errors.append("gate_count_changed")
    for gate in report["gates"]:
        if gate.get("status") != "blocked" or not gate.get("reopen_condition"):
            errors.append("gate_not_blocked:" + str(gate.get("name")))
    classes = report["evidence_classes"]
    if classes.get("independent_listening") != "none" or \
            classes.get("target_runtime") != "none":
        errors.append("evidence_class_overclaim")
    repeat = report["repeatability"]
    if repeat != reference.build_report()["repeatability"]:
        errors.append("repeatability_mismatch")
    if (repeat.get("count") != 3 or repeat.get("byte_identical") is not True
            or len(set(repeat.get("digests", []))) != 1):
        errors.append("cold_start_repeatability_failed")
    if readiness.get("decision") != reference.DECISION:
        errors.append("readiness_decision_mismatch")
    if readiness.get("evidence_status") != reference.EVIDENCE_STATUS:
        errors.append("readiness_evidence_status_mismatch")
    if readiness.get("qualification_status") != reference.QUALIFICATION:
        errors.append("readiness_qualification_mismatch")
    if readiness.get("profile") != reference.PROFILE:
        errors.append("readiness_profile_mismatch")
    for key in ("ready_for_opt_in_adapter", "ready_for_provider_registration",
                "ready_for_release", "quality_pass",
                "enhancement_acceptance_cleared"):
        if readiness.get(key) is not False:
            errors.append("readiness_claim:" + key)
    if readiness.get("blocked_gates") != [
            name for name, _ in reference.GATE_DEFINITIONS]:
        errors.append("readiness_blocked_gates_mismatch")
    if readiness.get("exact_blocker") != reference.EXACT_BLOCKERS[0]:
        errors.append("readiness_exact_blocker_mismatch")
    if readiness.get("reopen_condition") != reference.REOPENING_CONDITIONS[0]:
        errors.append("readiness_reopen_condition_mismatch")
    external = readiness.get("external_asset", {})
    if external.get("required") is not True:
        errors.append("readiness_external_asset_required_missing")
    for key in ("present", "loaded", "executed", "runtime_installed"):
        if external.get(key) is not False:
            errors.append("readiness_external_asset_claim:" + key)
    if external.get("expected_checkpoint_sha256") != \
            reference.CHECKPOINT_SHA256:
        errors.append("readiness_checkpoint_digest_mismatch")
    if external.get("expected_config_sha256") != reference.CONFIG_SHA256:
        errors.append("readiness_config_digest_mismatch")
    if adapter.get("task_id") != reference.TASK or \
            adapter.get("task_local") is not True:
        errors.append("adapter_not_task_local")
    for key in ("implemented", "registered", "enabled_by_default",
                "default_selected", "public_api_abi_change",
                "provider_registration", "descriptor_registry_change",
                "installed_v0_behavior_change", "shared_build_or_ci_change",
                "asset_present", "streaming_supported"):
        if adapter.get(key) is not False:
            errors.append("adapter_claim:" + key)
    if adapter.get("descriptor_settings") != {}:
        errors.append("adapter_descriptor_settings_not_empty")
    if adapter.get("caller_supplied_asset_required") is not True:
        errors.append("adapter_asset_requirement_missing")
    if adapter.get("activation") != "deferred_until_gates_clear":
        errors.append("adapter_activation_not_deferred")
    if adapter.get("entrypoint") is not None:
        errors.append("adapter_entrypoint_should_be_null")


def check_source_files(errors: List[str]) -> None:
    for path, digest in {**reference.SOURCE_PINS,
                         **reference.ASSET_PINS}.items():
        target = reference.SOURCE_ROOT / path
        if not target.is_file():
            errors.append("source_pin_missing:" + path)
        elif reference.sha256(target.read_bytes()) != digest:
            errors.append("source_pin_changed:" + path)
    for path, digest in reference.BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file():
            errors.append("boundary_pin_missing:" + path)
        elif reference.sha256(target.read_bytes()) != digest:
            errors.append("boundary_pin_changed:" + path)
    for expected in (reference.EXPECTED_CALLER_CHECKPOINT_PATH,
                     reference.EXPECTED_CALLER_CONFIG_PATH):
        if (SDK_ROOT / expected).exists():
            errors.append("caller_asset_present_but_report_says_absent:" +
                          expected)
    try:
        identity = reference.upstream_git_identity()
    except (OSError, ValueError) as error:
        errors.append("upstream_identity_failed:" + str(error))
    else:
        if identity["normalized_remote"] != reference.UPSTREAM_REPOSITORY:
            errors.append("upstream_remote_mismatch:" +
                          identity["normalized_remote"])
        if identity["commit"] != reference.UPSTREAM_COMMIT:
            errors.append("upstream_commit_mismatch:" + identity["commit"])
        if identity["pinned_commit_present"] is not True:
            errors.append("upstream_pinned_commit_absent")
    vendored = reference.vendored_binary_files()
    if vendored:
        errors.append("vendored_asset_file:" + ",".join(vendored))
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and path.suffix.lower() in BINARY_SUFFIXES:
            errors.append("binary_file_in_task_dir:" + path.name)


def check_strict_rejections(errors: List[str]) -> int:
    result = reference.strict_rejection_examples()
    if result["bad_json_rejected"] != result["bad_json_total"]:
        errors.append("strict_json_accepted_bad_input")
    if result["bad_pins_rejected"] != result["bad_pins_total"]:
        errors.append("strict_pin_parser_accepted_bad_input")
    return result["bad_json_rejected"] + result["bad_pins_rejected"]


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in ("README.md", "LICENSES.md"):
        text = (HERE / name).read_text(encoding="utf-8")
        if f"<!-- {SPDX_COPYRIGHT} -->" not in text or \
                f"<!-- {SPDX_LICENSE} -->" not in text:
            errors.append("missing_markdown_spdx:" + name)
    for name in LICENSE_SIDECARS:
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for path in sorted(HERE.glob("*")):
        if path.is_file() and path.name.endswith(".license"):
            continue
        if path.suffix in (".json", ".sha256", ".lock", ".txt"):
            sidecar = HERE / (path.name + ".license")
            text = sidecar.read_text(encoding="utf-8") if sidecar.is_file() \
                else ""
            if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
                errors.append("missing_artifact_sidecar:" + path.name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or \
            'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE_docs_coverage_missing")


def check_scope(errors: List[str]) -> int:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return 0
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    diff = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "diff", "--check"],
        capture_output=True, text=True, check=False)
    if diff.returncode != 0:
        errors.append("git_diff_check_failed:" + diff.stdout.strip())
    pinned = {reference.TASK_PREFIX + name
              for name in reference.LOCAL_PIN_PATHS}
    pinned.add(reference.TASK_PREFIX + "SOURCES.sha256")
    for path in sorted(HERE.iterdir()):
        if path.is_file() and reference.TASK_PREFIX + path.name not in pinned:
            errors.append("unpinned_task_file:" + path.name)
        if path.is_dir():
            errors.append("unexpected_subdirectory:" + path.name)
    for path in sorted(HERE.glob("*")):
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            data = path.read_bytes()
            if b"\r" in data:
                errors.append("crlf_in_text_file:" + path.name)
            for number, line in enumerate(
                    data.decode("utf-8", "replace").splitlines(), 1):
                if line.rstrip() != line:
                    errors.append(
                        f"trailing_whitespace:{path.name}:{number}")
                    break
    return len(changed)


def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    readme_rows = check_readme_digest_tables(errors)
    payloads = check_json(errors)
    if all(payloads.values()):
        check_content(errors, payloads)
    check_source_files(errors)
    strict_count = check_strict_rejections(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digest = reference.sha256(REPORT.read_bytes()) \
        if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        pin_failures = [error for error in errors if (
            error.startswith(("strict_pin", "pin_", "pinned_", "SOURCES",
                              "incomplete_pin", "readme_")))]
        json_failures = [error for error in errors if (
            error.startswith("strict_json")
            or error.endswith("canonical_bytes")
            or error.endswith("sidecar_stale")
            or error.endswith("digest_mismatch")
            or error.startswith("report_missing_keys")
            or error == "negative_zero_in_artifact")]
        print(f"pins_ok={pins == len(reference.allowed_pin_keys()) and not pin_failures} "
              f"readme_rows={readme_rows} json_ok={not json_failures} "
              f"report_sha256={digest} failures={len(errors)}")
        return 1
    print(
        f"PASS pins={pins} readme_digest_rows={readme_rows} json_ok=4 "
        f"strict_rejections_ok={strict_count} reproduction_ok=3 licensing_ok=1 "
        f"scope_ok=1 changed_files={changed} profile={reference.PROFILE} "
        f"status={reference.STATUS} qualification={reference.QUALIFICATION} "
        f"decision={reference.DECISION} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
