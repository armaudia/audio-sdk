# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-ROSE-CD-ONE-STEP evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins,
stale digests, a stale README digest table, invalid/missing/nonfinite case
acceptance, unpinned or vendored files, license gaps, out-of-scope worktree
changes, whitespace damage or a dirty diff check. Never writes.
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
    "negative_claims", "boundary", "format", "caller_supplied_asset_contract",
    "asset_resolution", "surrogate", "enhancement_profile", "availability",
    "conditions", "alignment", "state", "controls", "adverse", "comparison",
    "regressions", "timing", "source_reported", "model_provenance",
    "licensing_analysis", "source_pins", "asset_pins", "boundary_pins", "gates",
    "exact_blockers", "missing_evidence", "reopening_conditions",
    "evidence_classes", "contract_sha256", "repeatability",
}
REQUIRED_READINESS_KEYS = {
    "schema_id", "task_id", "title", "profile", "decision", "evidence_status",
    "qualification_status", "defer_before", "ready_for_opt_in_adapter",
    "ready_for_provider_registration", "ready_for_release", "quality_pass",
    "report_sha256", "contract_sha256", "blocked_gates", "exact_blocker",
    "reopen_condition", "external_asset", "scope", "negative_claims",
}
REQUIRED_ADAPTER_KEYS = {
    "schema_id", "task_id", "task_local", "implemented", "registered",
    "enabled_by_default", "default_selected", "descriptor_settings",
    "public_api_abi_change", "provider_registration",
    "descriptor_registry_change", "installed_v0_behavior_change", "input_kind",
    "output_kinds", "tasks", "modes", "weights",
    "caller_supplied_asset_required", "asset_present", "activation",
    "entrypoint", "note",
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


def check_readme_digest_table(errors: List[str]) -> int:
    if not README.is_file():
        errors.append("README.md missing")
        return 0
    try:
        rows = reference.readme_pin_rows()
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_table_unreadable:" + str(error))
        return 0
    if not rows:
        errors.append("readme_digest_table_missing")
        return 0
    seen: Dict[str, str] = {}
    for path, digest in rows:
        if path in seen:
            errors.append("readme_duplicate_row:" + path)
            continue
        seen[path] = digest
        if path.startswith(reference.TASK_PREFIX):
            errors.append("readme_row_for_local_artifact:" + path)
            continue
        try:
            target = reference.qualify_pin_path(path)
        except ValueError as error:
            errors.append("readme_row_path_invalid:" + str(error))
            continue
        if not target.is_file():
            errors.append("readme_row_target_missing:" + path)
        elif reference.sha256(target.read_bytes()) != digest:
            errors.append("readme_row_digest_stale:" + path)
    external = {**reference.SOURCE_PINS, **reference.ASSET_PINS}
    for path in sorted(set(external) - set(seen)):
        errors.append("readme_row_missing:" + path)
    for path in sorted(set(seen) - set(external)):
        errors.append("readme_row_unexpected:" + path)
    for path, digest in external.items():
        if seen.get(path) not in (None, digest):
            errors.append("readme_row_pin_disagreement:" + path)
    return len(rows)


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
    if report["profile"] != reference.PROFILE or contract.get("profile") != reference.PROFILE:
        errors.append("profile_not_applied")
    if report["component_id"] != "rose-cd-one-step":
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
        if report["boundary"].get(key) is not False or contract["boundary"].get(key) is not False:
            errors.append("boundary_not_false:" + key)
    if report["boundary"].get("descriptor_settings") != {}:
        errors.append("descriptor_settings_not_empty")
    fmt = report["format"]
    for key, value in (
            ("public_sample_rate_hz", 16000), ("public_channels", 1),
            ("public_sample_format", "f32"), ("public_frame_samples", 160),
            ("public_frame_duration_ms", 10), ("asset_sample_rate_hz", 16000),
            ("asset_channels", 1), ("asset_minimum_samples", 8064),
            ("asset_stft_n_fft", 510), ("asset_stft_hop_samples", 128),
            ("asset_stft_center", True),
            ("asset_stft_reflection_pad_multiple_frames", 64),
            ("window_samples", 32000), ("window_frames", 200),
            ("public_v0_geometry_preserved", True), ("sdk_callback_invoked", False)):
        if fmt.get(key) != value:
            errors.append("format_mismatch:" + key)
    for key in ("task_local_only", "synthetic_boundary_surrogate_only",
                "caller_supplied_asset_contract_modeled"):
        if report["scope"].get(key) is not True:
            errors.append("scope_true_missing:" + key)
    for key in ("caller_supplied_asset_present", "rose_cd_source_executed",
                "rose_cd_runtime_executed", "rose_cd_checkpoint_loaded",
                "model_weights_downloaded", "model_weights_loaded", "real_audio",
                "real_labels", "network_used", "device_timing", "listening_result",
                "benchmark_claim", "release_claim", "registered_provider"):
        if report["scope"].get(key) is not False:
            errors.append("scope_claim:" + key)
    for key, value in report["negative_claims"].items():
        if value is not False:
            errors.append("prohibited_claim:" + key)
    asset_contract = report["caller_supplied_asset_contract"]
    if asset_contract != reference.CALLER_ASSET_CONTRACT:
        errors.append("caller_asset_contract_mismatch")
    if set(asset_contract.get("required_fields", [])) != reference.REQUIRED_ASSET_FIELDS:
        errors.append("caller_asset_fields_mismatch")
    resolution = report["asset_resolution"]
    for key in ("requested", "manifest_present",
                "checkpoint_present_in_sdk_worktree",
                "checkpoint_present_in_external_checkout",
                "source_checkout_present_in_sdk_worktree",
                "runtime_environment_present", "verified", "loaded", "executed"):
        if resolution.get(key) is not False:
            errors.append("asset_resolution_claim:" + key)
    if resolution.get("surrogate_used") is not True:
        errors.append("surrogate_not_used")
    if resolution.get("source_checkout_present_in_external_checkout") is not True:
        errors.append("external_source_claim")
    surrogate = report["surrogate"]
    for key in ("is_rose_cd", "is_neural_network", "pytorch_used", "weights",
                "checkpoint", "stft_model", "diffusion_sampler", "quality_claim"):
        if surrogate.get(key) is not False:
            errors.append("surrogate_claim:" + key)
    if surrogate.get("identity") != "rose-cd-one-step-boundary-surrogate-v0":
        errors.append("surrogate_identity_mismatch")
    if surrogate.get("minimum_asset_samples") != reference.MIN_ASSET_SAMPLES:
        errors.append("surrogate_minimum_samples_mismatch")
    if surrogate.get("stft_n_fft") != reference.STFT_N_FFT:
        errors.append("surrogate_stft_n_fft_mismatch")
    if surrogate.get("stft_hop_samples") != reference.STFT_HOP:
        errors.append("surrogate_stft_hop_mismatch")
    if surrogate.get("reflection_pad_multiple_frames") != reference.STFT_PAD_FRAMES:
        errors.append("surrogate_stft_pad_mismatch")
    if surrogate.get("delay_modeled_samples") != 0 or \
            surrogate.get("delay_compensated_samples") != 0:
        errors.append("surrogate_delay_mismatch")
    enhancement = report["enhancement_profile"]
    for key, value in (
            ("name", "enhancement"),
            ("identity_noisy_control", "present: unprocessed input is the baseline"),
            ("task_matched_baseline", "not_reproduced"),
            ("unpaired_predictive_screen_or_listening", "not_run"),
            ("alignment", "modeled_offline_whole_clip_zero_delay"),
            ("state_and_memory", "synthetic_state_only"),
            ("content_availability_timing", "blocked_unmeasured"),
            ("listening", "not_run"),
            ("real_audio", False), ("real_clean_references", False),
            ("device_timing", False), ("memory_measured", False),
            ("quality_claim", False)):
        if enhancement.get(key) != value:
            errors.append("enhancement_profile_mismatch:" + key)
    conditions = report["conditions"]
    if set(conditions) != set(reference.CONDITIONS):
        errors.append("condition_set_mismatch")
    for name, condition in conditions.items():
        if condition["input"]["samples"] != reference.WINDOW_SAMPLES:
            errors.append("input_samples_wrong:" + name)
        if condition["output"]["samples"] != reference.WINDOW_SAMPLES:
            errors.append("output_samples_wrong:" + name)
        if condition["input"]["finite"] is not True or condition["output"]["finite"] is not True:
            errors.append("nonfinite_condition:" + name)
        if condition["output"]["clipped_or_nonfinite"] != 0:
            errors.append("output_clipped_or_nonfinite:" + name)
        if condition["input"]["clipped_or_nonfinite"] != 0:
            errors.append("guarded_input_clipped:" + name)
        for metric_name in ("si_sdr_db", "stoi"):
            metric = condition[metric_name]
            identity = metric["identity_noisy"]
            provider = metric["provider_surrogate"]
            delta = metric["paired_delta"]
            if identity is not None and provider is not None:
                if delta is None or abs(delta - (provider - identity)) > 1e-6:
                    errors.append("paired_delta_wrong:" + name + ":" + metric_name)
            elif delta is not None:
                errors.append("paired_delta_without_both:" + name + ":" + metric_name)
        gate = condition["surrogate_gate"]
        if gate["frame_count"] != reference.WINDOW_FRAMES:
            errors.append("gate_frame_count_wrong:" + name)
        if gate["stft_frames"] != reference._stft_frame_count(reference.WINDOW_SAMPLES):
            errors.append("gate_stft_frames_wrong:" + name)
        if gate["reflection_pad_frames"] != \
                reference._reflection_pad_frames(reference.WINDOW_SAMPLES):
            errors.append("gate_reflection_pad_wrong:" + name)
        if gate["delay_compensated"] is not True:
            errors.append("gate_not_compensated:" + name)
        if gate["nfe"] not in (0, 1):
            errors.append("gate_nfe_invalid:" + name)
    if conditions["noisy_snr10"]["si_sdr_db"]["paired_delta"] is None:
        errors.append("snr10_metric_missing")
    if conditions["noise_only"]["si_sdr_db"]["identity_invalid_reason"] != \
            "zero_reference_energy":
        errors.append("noise_only_not_zero_reference")
    if conditions["silence"]["stoi"]["identity_invalid_reason"] != "zero_reference":
        errors.append("silence_not_zero_reference")
    if report["regressions"] != reference._regressions(conditions):
        errors.append("regressions_mismatch")
    if report["comparison"].get("regression_count") != len(report["regressions"]):
        errors.append("regression_count_mismatch")
    alignment = report["alignment"]
    for key, value in (
            ("expected_impulse_index", 4000),
            ("uncompensated_impulse_index", 4000),
            ("compensated_impulse_index", 4000),
            ("measured_content_lag_samples", 0),
            ("modeled_delay_samples", 0),
            ("modeled_delay_ms", 0),
            ("delay_compensation_applied", True),
            ("valid_output_samples", 32000),
            ("sdk_callback_invoked", False)):
        if alignment.get(key) != value:
            errors.append("alignment_mismatch:" + key)
    if alignment.get("stft_frames") != reference._stft_frame_count(32000):
        errors.append("alignment_stft_frames_mismatch")
    if alignment.get("reflection_pad_frames") != \
            reference._reflection_pad_frames(32000):
        errors.append("alignment_reflection_pad_mismatch")
    for key, value in report["state"].items():
        if value is not True:
            errors.append("state_control_failed:" + key)
    caller_asset = report["controls"]["caller_asset"]
    frame_control = report["controls"]["frame"]
    if caller_asset.get("all_present") is not True or caller_asset.get("all_fail_closed") is not True:
        errors.append("caller_asset_controls_incomplete")
    if caller_asset["valid_manifest"] != {
            "status": "validated", "verified": True, "loaded": False, "executed": False}:
        errors.append("valid_manifest_scope_wrong")
    for name in ("missing_manifest", "absent_checkpoint", "hash_mismatch",
                 "wrong_source_revision", "wrong_checkpoint_revision",
                 "wrong_sample_rate", "wrong_channels", "wrong_sampler_type",
                 "wrong_steps", "wrong_snr", "relative_path", "extra_field",
                 "missing_source_marker"):
        if caller_asset[name].get("status") != "rejected":
            errors.append("caller_asset_not_rejected:" + name)
    if frame_control.get("all_present") is not True or frame_control.get("all_fail_closed") is not True:
        errors.append("frame_controls_incomplete")
    for name in ("short_input", "two_dimensional_input", "nonfinite_input",
                 "out_of_range_input", "truncated_output", "finish_called_twice"):
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
    for key in ("established_task_matched_baseline_reproduced",
                "source_reported_rose_cd_pilot_used_for_qualification",
                "quality_pass"):
        if comparison.get(key) is not False:
            errors.append("comparison_claim:" + key)
    if comparison.get("raw_and_rms_matched_configurations_separated") is not True:
        errors.append("raw_rms_separation_missing")
    timing = report["timing"]
    for key in ("measured", "device_timing", "paced"):
        if timing.get(key) is not False:
            errors.append("timing_claim:" + key)
    source_reported = report["source_reported"]
    if source_reported.get("status") != "source_reported_not_reproduced":
        errors.append("source_reported_not_labeled")
    if source_reported.get("used_for_qualification") is not False:
        errors.append("source_reported_used_for_qualification")
    if not source_reported.get("findings") or not source_reported.get("unavailable"):
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
    for key in ("present_in_external_checkout", "present_in_sdk_worktree",
                "downloaded_by_this_package", "copied_or_vendored",
                "loaded_or_executed"):
        if checkpoint.get(key) is not False:
            errors.append("checkpoint_scope:" + key)
    card = provenance.get("model_card", {})
    if card.get("repository") != reference.HF_REPOSITORY:
        errors.append("model_card_repository_mismatch")
    if card.get("declared_revision") != reference.HF_REVISION:
        errors.append("model_card_revision_mismatch")
    if card.get("artifact_accessed_by_this_package") is not False:
        errors.append("model_card_access_claim")
    public_adapter = provenance.get("public_adapter", {})
    if public_adapter.get("present_in_research_workspace") is not True:
        errors.append("public_adapter_research_presence_missing")
    if public_adapter.get("present_in_sdk_worktree") is not False:
        errors.append("public_adapter_sdk_presence_claim")
    if public_adapter.get("executed_by_this_package") is not False:
        errors.append("public_adapter_execution_claim")
    licensing = report["licensing_analysis"]
    for key in ("checkpoint_redistribution_clearance", "product_use_clearance",
                "training_data_provenance_established", "legal_review_completed",
                "asset_copied_vendored_built_or_downloaded"):
        if licensing.get(key) is not False:
            errors.append("licensing_rights_claimed:" + key)
    if licensing.get("blocked_gate") != "checkpoint_and_runtime_rights":
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
    expected_repeat = reference.build_report()["repeatability"]
    if repeat != expected_repeat:
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
                "ready_for_release", "quality_pass"):
        if readiness.get(key) is not False:
            errors.append("readiness_claim:" + key)
    if readiness.get("blocked_gates") != [name for name, _ in reference.GATE_DEFINITIONS]:
        errors.append("readiness_blocked_gates_mismatch")
    if readiness.get("exact_blocker") != reference.EXACT_BLOCKERS[0]:
        errors.append("readiness_exact_blocker_mismatch")
    if readiness.get("reopen_condition") != reference.REOPENING_CONDITIONS[0]:
        errors.append("readiness_reopen_condition_mismatch")
    external = readiness.get("external_asset", {})
    if external.get("required") is not True:
        errors.append("readiness_external_asset_required_missing")
    for key in ("present", "loaded", "executed", "runtime_environment_present"):
        if external.get(key) is not False:
            errors.append("readiness_external_asset_claim:" + key)
    if external.get("expected_checkpoint_sha256") != reference.CHECKPOINT_SHA256:
        errors.append("readiness_checkpoint_digest_mismatch")
    if external.get("expected_checkpoint_bytes") != reference.CHECKPOINT_BYTES:
        errors.append("readiness_checkpoint_bytes_mismatch")
    if adapter.get("task_id") != reference.TASK or adapter.get("task_local") is not True:
        errors.append("adapter_not_task_local")
    for key in ("implemented", "registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "installed_v0_behavior_change",
                "asset_present"):
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
    for path, digest in {**reference.SOURCE_PINS, **reference.ASSET_PINS}.items():
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
    if not (reference.SOURCE_ROOT / reference.UPSTREAM_SNAPSHOT).is_dir():
        errors.append("external_source_checkout_missing")
    for candidate in (
            reference.SOURCE_ROOT / reference.CHECKPOINT_LEDGER_PATH,
            SDK_ROOT / reference.EXPECTED_CALLER_CHECKPOINT_PATH):
        if candidate.exists():
            errors.append("checkpoint_present_but_report_says_absent:" + str(candidate))
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and path.suffix.lower() in BINARY_SUFFIXES:
            errors.append("binary_file_in_task_dir:" + path.name)
    try:
        identity = reference.upstream_git_identity()
    except (OSError, ValueError) as error:
        errors.append("upstream_identity_failed:" + str(error))
    else:
        if identity["normalized_remote"] != reference.UPSTREAM_REPOSITORY:
            errors.append("upstream_remote_mismatch:" + identity["normalized_remote"])
        if identity["commit"] != reference.UPSTREAM_COMMIT:
            errors.append("upstream_commit_mismatch:" + identity["commit"])
        if identity["pinned_commit_present"] is not True:
            errors.append("upstream_pinned_commit_absent")


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
            text = sidecar.read_text(encoding="utf-8") if sidecar.is_file() else ""
            if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
                errors.append("missing_artifact_sidecar:" + path.name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
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
    diff = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"],
                          capture_output=True, text=True, check=False)
    if diff.returncode != 0:
        errors.append("git_diff_check_failed:" + diff.stdout.strip())
    pinned = {reference.TASK_PREFIX + name for name in reference.LOCAL_PIN_PATHS}
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
            for number, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
                if line.rstrip() != line:
                    errors.append(f"trailing_whitespace:{path.name}:{number}")
                    break
    return len(changed)


def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    readme_rows = check_readme_digest_table(errors)
    payloads = check_json(errors)
    if all(payloads.values()):
        check_content(errors, payloads)
    check_source_files(errors)
    strict_count = check_strict_rejections(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digest = reference.sha256(REPORT.read_bytes()) if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        pin_failures = [error for error in errors if (
            error.startswith(("strict_pin", "pin_", "pinned_", "SOURCES",
                              "incomplete_pin", "readme_row", "readme_digest",
                              "readme_table", "readme_duplicate")))]
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
