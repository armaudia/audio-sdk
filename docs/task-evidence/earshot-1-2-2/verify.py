# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-EARSHOT-1-2-2 evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins,
stale digests, invalid/missing/nonfinite case acceptance, README digest-table
drift, unpinned files, license gaps, out-of-scope worktree changes, whitespace
damage or a dirty diff check. Never writes.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

sys.dont_write_bytecode = True

import fixture  # noqa: E402
import reference  # noqa: E402

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
REQUIRED_REPORT_KEYS = reference.REPORT_KEYS
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


def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label)


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
            path = fixture.resolve_source_path(raw.split(":", 1)[1])
        else:
            path = SDK_ROOT / raw
        if not path.is_file():
            errors.append("pin_target_missing:" + raw)
        elif fixture.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("SOURCES.sha256_not_deterministic_bytes")
    return len(pins)


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
    if REPORT.read_bytes() != reference.canonical_report_bytes(
            payloads["report"]):
        errors.append("report_not_canonical_bytes")
    if REPORT.read_bytes() != reference.canonical_report_bytes():
        errors.append("report_not_regenerated_bytes")
    if READINESS.read_bytes() != reference.readiness_bytes():
        errors.append("readiness_not_canonical_bytes")
    if ADAPTER.read_bytes() != reference.adapter_bytes():
        errors.append("adapter_not_canonical_bytes")
    report_digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
    expected_sidecar = f"{report_digest}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    if payloads["report"].get("contract_sha256") != hashlib.sha256(
            CONTRACT.read_bytes()).hexdigest():
        errors.append("report_contract_digest_mismatch")
    if payloads["readiness"].get("report_sha256") != report_digest:
        errors.append("readiness_report_digest_mismatch")
    if payloads["readiness"].get("contract_sha256") != hashlib.sha256(
            CONTRACT.read_bytes()).hexdigest():
        errors.append("readiness_contract_digest_mismatch")
    for name, payload in payloads.items():
        if reference.has_negative_zero(payload):
            errors.append("negative_zero_in_artifact:" + name)
    return payloads


def check_content(errors: List[str],
                  payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]
    readiness = payloads["readiness"]
    adapter = payloads["adapter"]

    _eq(errors, "report_key_set_mismatch", set(report), REQUIRED_REPORT_KEYS)
    for key in sorted(REQUIRED_READINESS_KEYS - set(readiness)):
        errors.append("readiness_missing_keys:" + key)
    for key in sorted(REQUIRED_ADAPTER_KEYS - set(adapter)):
        errors.append("adapter_missing_keys:" + key)

    _eq(errors, "base_commit_mismatch", report.get("base_commit"),
        reference.BASE_COMMIT)
    _eq(errors, "branch_mismatch", report.get("branch"), reference.BRANCH)
    _eq(errors, "profile_not_applied", report.get("profile"), reference.PROFILE)
    _eq(errors, "contract_profile_not_applied", contract.get("profile"),
        reference.PROFILE)
    for key, expected in (
            ("task_id", reference.TASK),
            ("status", reference.STATUS),
            ("evidence_status", reference.EVIDENCE_STATUS),
            ("qualification_status", reference.QUALIFICATION),
            ("decision", reference.DECISION),
            ("defer_before", reference.DEFER_BEFORE)):
        _eq(errors, "disposition_mismatch:" + key, report.get(key), expected)
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")

    boundary_false = (
        "registered", "enabled_by_default", "default_selected",
        "public_api_abi_change", "provider_registration",
        "descriptor_registry_change", "shared_cmakelists_change",
        "installed_v0_behavior_change", "processor_exposure", "ci_change",
    )
    for key in boundary_false:
        if report["boundary"].get(key) is not False \
                or contract["boundary"].get(key) is not False:
            errors.append("boundary_not_false:" + key)
    _eq(errors, "descriptor_settings_not_empty",
        report["boundary"].get("descriptor_settings"), {})

    fmt = report["format"]
    for key, value in (
            ("sdk_v0_sample_rate_hz", 16000), ("sdk_v0_channels", 1),
            ("sdk_v0_sample_format", "f32"), ("sdk_v0_frame_samples", 160),
            ("asset_sample_rate_hz", 16000), ("asset_channels", 1),
            ("asset_sample_format", "float32"), ("asset_frame_samples", 256),
            ("asset_frame_duration_ms", 16), ("decision_threshold", 0.5),
            ("window_samples", 32000), ("window_frames", 125),
            ("sdk_v0_geometry_preserved", True), ("sdk_callback_invoked", False),
            ("frame_cadence_parity_with_real_runtime_claimed", False)):
        _eq(errors, "format_mismatch:" + key, fmt.get(key), value)
    _eq(errors, "contract_format_mismatch", contract.get("format"),
        reference.FORMAT)
    _eq(errors, "contract_boundary_mismatch", contract.get("boundary"),
        reference.BOUNDARY)
    _eq(errors, "contract_scope_mismatch", contract.get("scope"),
        reference.SCOPE)

    for key in ("task_local_only", "synthetic_boundary_surrogate_only",
                "caller_supplied_asset_contract_modeled"):
        if report["scope"].get(key) is not True:
            errors.append("scope_true_missing:" + key)
    for key in ("caller_supplied_asset_present", "earshot_source_executed",
                "earshot_runtime_executed", "earshot_wheel_imported",
                "wheel_downloaded", "wheel_loaded", "model_weights_loaded",
                "real_audio", "real_labels", "network_used", "device_timing",
                "listening_result", "benchmark_claim", "release_claim",
                "registered_provider"):
        if report["scope"].get(key) is not False:
            errors.append("scope_claim:" + key)
    for key, value in report["negative_claims"].items():
        if value is not False:
            errors.append("prohibited_claim:" + key)

    _eq(errors, "caller_asset_contract_mismatch",
        report["caller_supplied_asset_contract"], reference.CALLER_ASSET_CONTRACT)
    _eq(errors, "contract_caller_asset_contract_mismatch",
        contract["caller_supplied_asset_contract"], reference.CALLER_ASSET_CONTRACT)

    resolution = report["asset_resolution"]
    for key in ("requested", "manifest_present", "wheel_present_in_sdk_worktree",
                "wheel_present_in_research_workspace", "environment_present",
                "source_archive_present", "runtime_library_present", "verified",
                "loaded", "executed", "imported"):
        if resolution.get(key) is not False:
            errors.append("asset_resolution_claim:" + key)
    if resolution.get("surrogate_used") is not True:
        errors.append("surrogate_not_used")
    if resolution.get("weights_embedded_in_wheel") is not True:
        errors.append("embedded_weights_not_declared")
    _eq(errors, "expected_wheel_path_mismatch",
        resolution.get("expected_wheel_path"), reference.WHEEL_PATH)
    _eq(errors, "expected_wheel_digest_mismatch",
        resolution.get("expected_wheel_sha256"), reference.WHEEL_SHA256)

    surrogate = report["surrogate"]
    for key in ("is_earshot", "is_neural_network", "weights", "checkpoint",
                "model_archive", "quality_claim"):
        if surrogate.get(key) is not False:
            errors.append("surrogate_claim:" + key)
    _eq(errors, "surrogate_identity_mismatch", surrogate.get("identity"),
        "earshot-1-2-2-boundary-surrogate-v1")
    _eq(errors, "surrogate_frame_mismatch", surrogate.get("frame_samples"), 256)
    _eq(errors, "surrogate_threshold_mismatch",
        surrogate.get("decision_threshold"), 0.5)
    if surrogate.get("deterministic") is not True \
            or surrogate.get("pure_synthetic") is not True:
        errors.append("surrogate_not_deterministic_synthetic")

    totals = fixture.truth_totals()
    _eq(errors, "strata_set_mismatch", set(report["strata"]),
        {segment["id"] for segment in fixture.SEGMENTS})
    for name, row in report["strata"].items():
        segment = next(segment for segment in fixture.SEGMENTS
                       if segment["id"] == name)
        _eq(errors, "stratum_interval_mismatch:" + name,
            [row["start_sample"], row["end_sample"]],
            [segment["start"], segment["end"]])
        _eq(errors, "stratum_truth_mismatch:" + name, row["truth"],
            segment["truth"])
        _eq(errors, "stratum_samples_mismatch:" + name, row["samples"],
            segment["end"] - segment["start"])
    _eq(errors, "unknown_was_scored", report["strata"]["unknown-tail"]["scored"],
        False)

    detections = report["detections"]
    overall = detections["overall"]
    _eq(errors, "detection_sum_mismatch", sum(overall.values()),
        detections["speech_samples"] + detections["nonspeech_samples"])
    _eq(errors, "speech_denominator_mismatch", overall["TP"] + overall["FN"],
        totals["speech"])
    _eq(errors, "nonspeech_denominator_mismatch", overall["FP"] + overall["TN"],
        totals["nonspeech"])
    _eq(errors, "unknown_excluded_mismatch",
        detections["unknown_excluded_samples"], totals["unknown"])
    _eq(errors, "invalid_excluded_mismatch",
        detections["invalid_excluded_samples"], 0)
    if abs(detections["speech_miss_rate"]
           - overall["FN"] / totals["speech"]) > 1e-12:
        errors.append("speech_miss_rate_mismatch")
    if abs(detections["false_alarm_rate"]
           - overall["FP"] / totals["nonspeech"]) > 1e-12:
        errors.append("false_alarm_rate_mismatch")
    _eq(errors, "frame_resolution_mismatch",
        detections["frame_resolution_samples"], 256)
    _eq(errors, "stratified_quiet_a_fn_mismatch",
        report["strata"]["quiet-a"]["FN"], 1536)
    _eq(errors, "stratified_quiet_b_fn_mismatch",
        report["strata"]["quiet-b"]["FN"], 3328)
    _eq(errors, "stratified_noise_burst_fp_mismatch",
        report["strata"]["noise-burst"]["FP"], 1280)
    _eq(errors, "stratified_active_fn_mismatch",
        report["strata"]["active-a"]["FN"], 0)

    probabilities = report["probabilities"]
    for key in ("brier_score", "log_loss", "mean_probability",
                "min_probability", "max_probability"):
        value = probabilities.get(key)
        if not isinstance(value, (int, float)) or not isinstance(value, float):
            errors.append("probability_metric_not_float:" + key)
        elif not (-1e-12 <= float(value) < 1e9):
            errors.append("probability_metric_out_of_range:" + key)
    _eq(errors, "known_event_count_mismatch",
        probabilities.get("known_events"), 112)
    _eq(errors, "unknown_event_count_mismatch",
        probabilities.get("unknown_events"), 13)
    _eq(errors, "scored_sample_count_mismatch",
        probabilities.get("scored_samples"), totals["speech"] + totals["nonspeech"])
    bins = probabilities.get("calibration_bins", [])
    _eq(errors, "calibration_bin_count_mismatch", len(bins), 5)
    if sum(item.get("events", 0) for item in bins) != 112:
        errors.append("calibration_event_sum_mismatch")
    if sum(item.get("samples", 0) for item in bins) != \
            totals["speech"] + totals["nonspeech"]:
        errors.append("calibration_sample_sum_mismatch")

    boundaries = report["boundaries"]
    _eq(errors, "truth_runs_mismatch", boundaries["truth_runs"],
        [[2048, 6144], [8192, 16128], [18688, 22016]])
    _eq(errors, "detected_runs_mismatch", boundaries["detected_runs"],
        [[3584, 6144], [8192, 16128], [17408, 18688]])
    _eq(errors, "matched_boundary_count_mismatch",
        boundaries["matched_count"], 2)
    _eq(errors, "quiet_a_onset_delay_mismatch",
        boundaries["matches"][0]["onset_delay_samples"], 1536)
    _eq(errors, "quiet_a_offset_delay_mismatch",
        boundaries["matches"][0]["offset_delay_samples"], 0)
    _eq(errors, "active_a_onset_delay_mismatch",
        boundaries["matches"][1]["onset_delay_samples"], 0)
    _eq(errors, "missed_truth_runs_mismatch",
        boundaries["missed_truth_runs"], [[18688, 22016]])
    _eq(errors, "false_detected_runs_mismatch",
        boundaries["false_detected_runs"], [[17408, 18688]])
    _eq(errors, "boundary_tolerance_mismatch",
        boundaries["tolerance_samples"], 0)

    baselines = report["baselines"]
    _eq(errors, "always_speech_baseline_mismatch",
        baselines["always_speech"],
        {"TP": totals["speech"], "FN": 0, "FP": totals["nonspeech"], "TN": 0,
         "speech_miss_rate": 0.0, "false_alarm_rate": 1.0})
    _eq(errors, "always_nonspeech_baseline_mismatch",
        baselines["always_nonspeech"],
        {"TP": 0, "FN": totals["speech"], "FP": 0, "TN": totals["nonspeech"],
         "speech_miss_rate": 1.0, "false_alarm_rate": 0.0})
    if baselines.get("diagnostic_only") is not True \
            or baselines.get("used_for_qualification") is not False:
        errors.append("baseline_scope_claim")

    alignment = report["alignment"]
    for key, value in (
            ("frame_grid_exact", True), ("frame_samples", 256),
            ("frame_duration_ms", 16), ("declared_analysis_delay_samples", 0),
            ("matched_boundary_count", 2),
            ("source_interval_mapping", "identity"), ("measured", False)):
        _eq(errors, "alignment_mismatch:" + key, alignment.get(key), value)

    for key, value in report["state"].items():
        if value is not True:
            errors.append("state_control_failed:" + key)

    controls = report["controls"]
    caller_asset = controls["caller_asset"]
    if caller_asset.get("all_present") is not True \
            or caller_asset.get("all_fail_closed") is not True:
        errors.append("caller_asset_controls_incomplete")
    _eq(errors, "valid_manifest_scope_wrong", caller_asset["valid_manifest"],
        {"status": "validated", "verified": True, "loaded": False,
         "executed": False, "imported": False})
    for name in ("missing_manifest", "absent_file", "relative_path",
                 "hash_mismatch", "wrong_source_commit", "wrong_sample_rate",
                 "wrong_channels", "wrong_frame_size", "wrong_threshold",
                 "wrong_input_format", "unexpected_field"):
        if caller_asset[name].get("status") != "rejected":
            errors.append("caller_asset_not_rejected:" + name)

    frame = controls["frame"]
    if frame.get("all_present") is not True \
            or frame.get("all_fail_closed") is not True:
        errors.append("frame_controls_incomplete")
    for name, case in frame["cases"].items():
        if case.get("reason") != case.get("expected") \
                or case.get("state_unchanged") is not True:
            errors.append("frame_control_failed:" + name)
    _eq(errors, "final_partial_end_mismatch",
        frame.get("final_partial_end_sample"), 384)
    _eq(errors, "final_partial_padded_mismatch",
        frame.get("final_partial_padded_samples"), 128)
    if frame.get("state_unchanged_after_rejections") is not True:
        errors.append("frame_state_changed_after_rejection")

    bus = controls["event_bus"]
    _eq(errors, "event_bus_dropped_mismatch", bus.get("dropped_sequences"),
        [2, 5, 17])
    _eq(errors, "event_bus_gaps_mismatch", bus.get("gaps"),
        [[2, 2], [5, 5], [17, 17]])
    _eq(errors, "event_bus_fabricated_mismatch", bus.get("fabricated_events"), 0)
    if bus.get("all_rejected_without_state_change") is not True:
        errors.append("event_bus_rejection_state_changed")
    for name, case in bus.get("adverse_cases", {}).items():
        if case.get("state_unchanged") is not True or case.get("accepted") is not False:
            errors.append("event_bus_case_not_rejected:" + name)

    parity = controls["streaming_parity"]
    if parity.get("events_identical") is not True \
            or parity.get("fresh_session_identical") is not True:
        errors.append("streaming_parity_failed")
    _eq(errors, "streaming_digest_mismatch",
        parity.get("offline_digest"), parity.get("streaming_digest"))
    _eq(errors, "streaming_event_count_mismatch",
        parity.get("offline_events"), 125)

    partial = controls["partial_tail"]
    for key, value in (
            ("stream_samples", 384), ("full_frames", 1),
            ("final_valid_samples", 128), ("final_padded_samples", 128),
            ("final_end_sample", 384), ("frame_interval_clipped_to_real_samples", True),
            ("inference_frame_zero_padded", True)):
        _eq(errors, "partial_tail_mismatch:" + key, partial.get(key), value)

    cross = controls["cross_hop"]
    _eq(errors, "cross_hop_frames_mismatch", cross.get("frames"),
        [[0, 106], [1, 74]])
    _eq(errors, "cross_hop_overlap_mismatch", cross.get("overlap_samples"), 180)
    _eq(errors, "cross_hop_truth_hops_mismatch", cross.get("truth_hops"), 16)

    intervals = controls["interval_and_availability"]
    for key, value in (
            ("frame_boundaries_exact", True),
            ("known_availability_strictly_increasing", True),
            ("unknown_events_have_no_availability", True),
            ("measured", False),
            ("probability_events_cover_samples", [0, 32000])):
        _eq(errors, "interval_control_mismatch:" + key, intervals.get(key), value)

    for name in ("sample_rate_hz", "channels", "sample_format", "frame_samples",
                 "decision_threshold", "real_runtime",
                 "wheel_or_licensed_runtime_used", "missing_session_id"):
        if controls["config_adverse"][name].get("status") != "rejected":
            errors.append("config_control_not_rejected:" + name)

    invalid = controls["invalid_vs_nonspeech"]
    if invalid.get("unknown_event_admitted") is not True \
            or invalid.get("invalid_counted_as_nonspeech") is not False \
            or invalid.get("false_positives") != 0:
        errors.append("invalid_vs_nonspeech_control_mismatch")
    for name, case in invalid.get("rejected_cases", {}).items():
        if case.get("status") != "rejected":
            errors.append("invalid_vs_nonspeech_not_rejected:" + name)

    adverse = report["adverse"]
    for key in ("all_rejected", "all_invalid_cases_rejected",
                "caller_asset_fail_closed", "frame_fail_closed",
                "event_bus_fail_closed"):
        if adverse.get(key) is not True:
            errors.append("adverse_false:" + key)
    _eq(errors, "adverse_config_mismatch", adverse.get("config_rejections"),
        controls["config_adverse"])
    _eq(errors, "adverse_frame_mismatch", adverse.get("frame_rejections"),
        frame["cases"])

    comparison = report["comparison"]
    for key in ("established_task_matched_baseline_reproduced",
                "source_reported_used_for_qualification", "quality_pass"):
        if comparison.get(key) is not False:
            errors.append("comparison_claim:" + key)
    _eq(errors, "regression_count_mismatch", comparison.get("regression_count"),
        len(report["regressions"]))

    timing = report["timing"]
    if timing.get("measured") is not False or timing.get("device_timing") is not False:
        errors.append("timing_claim")
    if timing.get("source_reported_cost_used_for_qualification") is not False:
        errors.append("source_reported_cost_used_for_qualification")
    _eq(errors, "source_reported_cost_mismatch",
        timing.get("source_reported_cost_us_per_20ms_frame"), 13.41)

    _eq(errors, "source_reported_mismatch", report["source_reported"],
        reference.SOURCE_REPORTED)
    if report["source_reported"].get("status") != "source_reported_not_reproduced":
        errors.append("source_reported_not_labeled")

    _eq(errors, "model_provenance_mismatch", report["model_provenance"],
        reference.MODEL_PROVENANCE)
    _eq(errors, "contract_model_provenance_mismatch",
        contract["model_provenance"], reference.MODEL_PROVENANCE)
    provenance = report["model_provenance"]
    _eq(errors, "upstream_commit_mismatch", provenance.get("upstream_commit"),
        reference.UPSTREAM_COMMIT)
    _eq(errors, "upstream_license_mismatch", provenance.get("upstream_license"),
        reference.UPSTREAM_LICENSE)
    _eq(errors, "upstream_repository_mismatch",
        provenance.get("upstream_repository"), reference.UPSTREAM_REPOSITORY)
    wheel = provenance.get("wheel", {})
    for key in ("present_in_sdk_worktree", "present_in_research_workspace",
                "verified", "downloaded_by_this_package", "copied_or_vendored",
                "imported_or_executed"):
        if wheel.get(key) is not False:
            errors.append("wheel_scope_claim:" + key)
    _eq(errors, "wheel_digest_mismatch", wheel.get("sha256"),
        reference.WHEEL_SHA256)
    _eq(errors, "wheel_path_mismatch", wheel.get("expected_path"),
        reference.WHEEL_PATH)
    _eq(errors, "wheel_weights_mismatch", wheel.get("weights"),
        "embedded-in-wheel")
    runtime = provenance.get("runtime_environment", {})
    for key in ("present", "built_by_this_package", "used_by_this_package"):
        if runtime.get(key) is not False:
            errors.append("runtime_environment_claim:" + key)
    public_adapter = provenance.get("public_adapter", {})
    if public_adapter.get("present_in_research_workspace") is not True:
        errors.append("public_adapter_research_presence_missing")
    if public_adapter.get("present_in_sdk_worktree") is not False:
        errors.append("public_adapter_sdk_presence_claim")
    if public_adapter.get("executed_by_this_package") is not False:
        errors.append("public_adapter_execution_claim")

    _eq(errors, "licensing_analysis_mismatch", report["licensing_analysis"],
        reference.LICENSING_ANALYSIS)
    licensing = report["licensing_analysis"]
    for key in ("standalone_license_file_in_wheel",
                "source_archive_redistribution_clearance",
                "wheel_redistribution_clearance", "product_use_clearance",
                "training_data_provenance_established", "legal_review_completed",
                "asset_copied_vendored_built_or_downloaded"):
        if licensing.get(key) is not False:
            errors.append("licensing_rights_claimed:" + key)
    _eq(errors, "licensing_gate_mismatch", licensing.get("blocked_gate"),
        "wheel_and_embedded_weight_rights")

    _eq(errors, "report_source_pins_mismatch", report["source_pins"],
        fixture.SOURCE_PINS)
    _eq(errors, "report_asset_pins_mismatch", report["asset_pins"],
        fixture.EXTERNAL_ASSET_PINS)
    _eq(errors, "report_boundary_pins_mismatch", report["boundary_pins"],
        fixture.BOUNDARY_PINS)
    _eq(errors, "contract_source_pins_mismatch", contract["source_pins"],
        fixture.SOURCE_PINS)
    _eq(errors, "contract_asset_pins_mismatch", contract["asset_pins"],
        fixture.EXTERNAL_ASSET_PINS)
    _eq(errors, "contract_boundary_pins_mismatch", contract["boundary_pins"],
        fixture.BOUNDARY_PINS)

    _eq(errors, "exact_blockers_mismatch", report["exact_blockers"],
        reference.EXACT_BLOCKERS)
    _eq(errors, "missing_evidence_mismatch", report["missing_evidence"],
        reference.MISSING_EVIDENCE)
    _eq(errors, "reopening_conditions_mismatch",
        report["reopening_conditions"], reference.REOPENING_CONDITIONS)
    _eq(errors, "contract_exact_blockers_mismatch",
        contract["exact_blockers"], reference.EXACT_BLOCKERS)
    _eq(errors, "gate_count_changed", len(report["gates"]),
        len(reference.GATE_DEFINITIONS))
    for gate in report["gates"]:
        if gate.get("status") != "blocked" or not gate.get("reopen_condition"):
            errors.append("gate_not_blocked:" + str(gate.get("name")))

    profile = report["acceptance_profile"]
    if profile.get("profile") != reference.PROFILE:
        errors.append("acceptance_profile_not_analysis")
    for item in reference.ACCEPTANCE_PROFILE_ITEMS:
        if profile.get(item) is not True:
            errors.append("acceptance_profile_item_missing:" + item)
    _eq(errors, "scorer_pin_mismatch", profile.get("scorer_sha256"),
        fixture.sha256_file(HERE / "scorer.py"))
    _eq(errors, "fixture_pin_mismatch", profile.get("fixture_sha256"),
        fixture.sha256_file(HERE / "fixture.py"))

    repeat = report["repeatability"]
    if (repeat.get("count") != 3 or repeat.get("byte_identical") is not True
            or len(set(repeat.get("digests", []))) != 1):
        errors.append("cold_start_repeatability_failed")
    core = {key: value for key, value in report.items() if key != "repeatability"}
    _eq(errors, "repeatability_digest_mismatch", repeat.get("digests"),
        [hashlib.sha256(reference.canonical_bytes(core)).hexdigest()] * 3)

    _eq(errors, "readiness_decision_mismatch", readiness.get("decision"),
        reference.DECISION)
    _eq(errors, "readiness_evidence_status_mismatch",
        readiness.get("evidence_status"), reference.EVIDENCE_STATUS)
    _eq(errors, "readiness_qualification_mismatch",
        readiness.get("qualification_status"), reference.QUALIFICATION)
    for key in ("ready_for_opt_in_adapter", "ready_for_provider_registration",
                "ready_for_release", "quality_pass"):
        if readiness.get(key) is not False:
            errors.append("readiness_claim:" + key)
    _eq(errors, "readiness_blocked_gates_mismatch",
        readiness.get("blocked_gates"),
        [name for name, _ in reference.GATE_DEFINITIONS])
    _eq(errors, "readiness_exact_blocker_mismatch",
        readiness.get("exact_blocker"), reference.EXACT_BLOCKERS[0])
    _eq(errors, "readiness_reopen_condition_mismatch",
        readiness.get("reopen_condition"), reference.REOPENING_CONDITIONS[0])
    external = readiness.get("external_asset", {})
    if external.get("required") is not True:
        errors.append("readiness_external_asset_required_missing")
    if external.get("weights_embedded_in_wheel") is not True:
        errors.append("readiness_embedded_weights_missing")
    for key in ("present", "loaded", "executed", "imported"):
        if external.get(key) is not False:
            errors.append("readiness_external_asset_claim:" + key)
    _eq(errors, "readiness_scope_mismatch", readiness.get("scope"),
        reference.SCOPE)
    _eq(errors, "readiness_negative_claims_mismatch",
        readiness.get("negative_claims"), reference.NEGATIVE_CLAIMS)

    _eq(errors, "adapter_task_mismatch", adapter.get("task_id"), reference.TASK)
    if adapter.get("task_local") is not True:
        errors.append("adapter_not_task_local")
    for key in ("implemented", "registered", "enabled_by_default",
                "default_selected", "public_api_abi_change",
                "provider_registration", "descriptor_registry_change",
                "installed_v0_behavior_change", "asset_present"):
        if adapter.get(key) is not False:
            errors.append("adapter_claim:" + key)
    _eq(errors, "adapter_descriptor_settings_not_empty",
        adapter.get("descriptor_settings"), {})
    if adapter.get("caller_supplied_asset_required") is not True:
        errors.append("adapter_asset_requirement_missing")
    _eq(errors, "adapter_activation_not_deferred", adapter.get("activation"),
        "deferred_until_gates_clear")
    if adapter.get("entrypoint") is not None:
        errors.append("adapter_entrypoint_should_be_null")
    _eq(errors, "adapter_output_kinds_mismatch", adapter.get("output_kinds"),
        ["annotation"])
    _eq(errors, "adapter_tasks_mismatch", adapter.get("tasks"), ["DET-01"])


def check_external_asset_absence(errors: List[str]) -> None:
    wheel = fixture.workspace_root() / reference.WHEEL_PATH
    if wheel.exists():
        errors.append("external_wheel_present_but_report_says_absent")
    environment = fixture.workspace_root() / reference.RUNTIME_ENV_PATH
    if environment.exists():
        errors.append("external_environment_present_but_report_says_absent")
    adapter = fixture.SDK_ROOT / "adapters/earshot-vad"
    if adapter.exists():
        errors.append("earshot_adapter_present_in_sdk_worktree")


def check_readme(errors: List[str]) -> int:
    try:
        counts = reference.verify_readme_digests(
            README.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return 0
    expected = reference.expected_readme_keys()
    for name in reference.README_SECTIONS:
        if counts.get(name) != len(expected[name]):
            errors.append("readme_section_count_mismatch:" + name)
    return sum(counts.values())


def check_strict_rejections(errors: List[str]) -> int:
    result = reference.strict_rejection_examples()
    for key, total in (("bad_json", "bad_json_total"),
                       ("bad_pins", "bad_pins_total"),
                       ("bad_readme", "bad_readme_total")):
        if result[key + "_rejected"] != result[total]:
            errors.append("strict_parser_accepted_bad_" + key)
    return (result["bad_json_rejected"] + result["bad_pins_rejected"]
            + result["bad_readme_rejected"])


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
    for args in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *args],
                              capture_output=True, text=True, check=False)
        if diff.returncode != 0:
            errors.append("git_" + "_".join(args).replace("-", "") + "_failed")
    expected_files = set(reference.LOCAL_PIN_PATHS) | {"SOURCES.sha256"}
    actual_files = {path.name for path in HERE.iterdir() if path.is_file()}
    if actual_files != expected_files:
        for name in sorted(actual_files - expected_files):
            errors.append("unpinned_task_file:" + name)
        for name in sorted(expected_files - actual_files):
            errors.append("pinned_task_file_missing:" + name)
    for path in sorted(HERE.iterdir()):
        if path.is_dir():
            errors.append("unexpected_subdirectory:" + path.name)
    if any(HERE.rglob("__pycache__")) or any(HERE.rglob("*.pyc")):
        errors.append("bytecode_cache_present")
    for path in sorted(HERE.glob("*")):
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            data = path.read_bytes()
            if b"\r" in data:
                errors.append("crlf_in_text_file:" + path.name)
            for number, line in enumerate(
                    data.decode("utf-8", "replace").splitlines(), 1):
                if line.rstrip() != line:
                    errors.append(f"trailing_whitespace:{path.name}:{number}")
                    break
    return len(changed)


def check_tests(errors: List[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = sum(1 for line in text.splitlines()
                if line.startswith("    def test_"))
    if count < 40:
        errors.append("fewer_than_40_reference_tests:" + str(count))
    return count


def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    payloads = check_json(errors)
    if all(payloads.values()):
        check_content(errors, payloads)
    check_external_asset_absence(errors)
    readme_rows = check_readme(errors)
    strict_count = check_strict_rejections(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    tests = check_tests(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"pins={pins} json_ok={all(payloads.values())} "
              f"readme_rows={readme_rows} strict_rejections={strict_count} "
              f"report_sha256={digest} failures={len(errors)}")
        return 1
    print(
        f"PASS pins={pins} json_ok=4 readme_rows={readme_rows} "
        f"strict_rejections_ok={strict_count} reproduction_ok=1 licensing_ok=1 "
        f"scope_ok=1 tests={tests} changed_files={changed} "
        f"profile={reference.PROFILE} status={reference.STATUS} "
        f"qualification={reference.QUALIFICATION} decision={reference.DECISION} "
        f"report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
