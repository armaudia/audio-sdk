# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-LOCALVQE-COMPACT-ECHO-ONLY package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 SOURCE_ROOT=<workspace> python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins,
stale digests, invalid/missing/nonfinite case acceptance, README digest-table
drift, unpinned files, license gaps, out-of-scope worktree changes, a hashed
mutable board file, whitespace damage or a dirty diff check. Never writes.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
README = HERE / "README.md"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".license"}
GATE_NAMES = {
    "exact_echo_asset_identity",
    "model_and_runtime_rights",
    "exact_runtime_reproduction",
    "streaming_boundary_and_one_hop_latency",
    "rights_cleared_paired_reference_cohort",
    "room_echo_near_overlap_no_reference_acceptance",
    "target_runtime_timing_memory",
    "provider_intake_and_default_selection",
}
FORBIDDEN_TOKENS = (
    "import " + "requests",
    "import " + "urllib",
    "import " + "socket",
    "url" + "open",
    "url" + "retrieve",
    "pip " + "install",
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
            path = reference.resolve_source_path(raw.split(":", 1)[1])
        else:
            path = SDK_ROOT / raw
        if not path.is_file():
            errors.append("pin_target_missing:" + raw)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("SOURCES.sha256_not_deterministic_bytes")
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line.startswith("#") and "TASKS.json" in line:
            errors.append("mutable_board_file_is_pinned")
    return len(pins)


def check_json(errors: List[str]) -> Dict[str, Dict[str, Any]]:
    payloads = {
        "contract": _strict_json(CONTRACT, errors, "contract"),
        "report": _strict_json(REPORT, errors, "report"),
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
    digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
    expected_sidecar = f"{digest}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    if payloads["report"].get("contract_sha256") != hashlib.sha256(
            CONTRACT.read_bytes()).hexdigest():
        errors.append("report_contract_digest_mismatch")
    for name, payload in payloads.items():
        if reference.has_negative_zero(payload):
            errors.append("negative_zero_in_artifact:" + name)
    return payloads


def check_content(errors: List[str],
                  payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]
    _eq(errors, "report_key_set_mismatch", set(report),
        reference.REPORT_KEYS)

    _eq(errors, "base_commit_mismatch", report.get("base_commit"),
        reference.BASE_COMMIT)
    _eq(errors, "branch_mismatch", report.get("branch"), reference.BRANCH)
    _eq(errors, "profile_not_applied", report.get("profile"),
        reference.PROFILE)
    _eq(errors, "contract_profile_not_applied", contract.get("profile"),
        reference.PROFILE)
    for key, expected in (
            ("task_id", reference.TASK),
            ("component_id", reference.COMPONENT),
            ("status", reference.STATUS),
            ("evidence_status", reference.EVIDENCE_STATUS),
            ("qualification_status", reference.QUALIFICATION),
            ("decision", reference.DECISION),
            ("defer_before", reference.DEFER_BEFORE)):
        _eq(errors, "disposition_mismatch:" + key, report.get(key), expected)
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")
    qualification = report.get("qualification", {})
    _eq(errors, "qualification_status_mismatch",
        qualification.get("status"), "not_qualified")
    if qualification.get("qualified") is not False:
        errors.append("qualified_claimed")
    if qualification.get("missing_result_may_qualify") is not False:
        errors.append("missing_result_may_qualify")

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

    _eq(errors, "contract_format_mismatch", contract.get("format"),
        reference.FORMAT)
    _eq(errors, "contract_boundary_mismatch", contract.get("boundary"),
        reference.BOUNDARY)
    _eq(errors, "contract_scope_mismatch", contract.get("scope"),
        reference.SCOPE)
    fmt = report["format"]
    for key, value in reference.FORMAT.items():
        _eq(errors, "format_mismatch:" + key, fmt.get(key), value)
    for key in ("sdk_v0_geometry_preserved",
                "echo_only_retains_noise_and_room"):
        if fmt.get(key) is not True:
            errors.append("format_true_missing:" + key)
    for key in ("sdk_callback_invoked",
                "frame_cadence_parity_with_real_runtime_claimed",
                "noise_suppression_stage", "dereverberation_stage"):
        if fmt.get(key) is not False:
            errors.append("format_claim:" + key)
    _eq(errors, "joint_tasks_mismatch", fmt.get("joint_tasks"), ["aec"])

    for key in ("task_local_only", "synthetic_boundary_surrogate_only",
                "caller_supplied_asset_contract_modeled",
                "paired_reference_boundary_modeled",
                "source_checkout_present", "runtime_library_present"):
        if report["scope"].get(key) is not True:
            errors.append("scope_true_missing:" + key)
    for key in ("caller_supplied_asset_present", "localvqe_source_executed",
                "localvqe_runtime_executed", "localvqe_library_loaded",
                "localvqe_model_loaded", "model_weights_downloaded",
                "model_weights_loaded", "real_audio", "real_labels",
                "network_used", "device_timing", "listening_result",
                "benchmark_claim", "release_claim", "registered_provider"):
        if report["scope"].get(key) is not False:
            errors.append("scope_claim:" + key)
    for key, value in report["negative_claims"].items():
        if value is not False:
            errors.append("prohibited_claim:" + key)

    _eq(errors, "caller_asset_contract_mismatch",
        report["caller_supplied_asset_contract"],
        reference.CALLER_ASSET_CONTRACT)
    _eq(errors, "contract_caller_asset_contract_mismatch",
        contract["caller_supplied_asset_contract"],
        reference.CALLER_ASSET_CONTRACT)
    if report["caller_supplied_asset_contract"].get(
            "requires_far_end_reference") is not True:
        errors.append("caller_asset_far_end_reference_missing")
    _eq(errors, "pinned_variant_mismatch",
        report["caller_supplied_asset_contract"]["pinned_values"]["variant"],
        "compact-echo-only")

    resolution = report["asset_resolution"]
    for key in ("requested", "manifest_present", "model_present",
                "full_model_present", "environment_present",
                "runtime_library_loaded", "verified", "loaded", "executed",
                "imported", "weights_embedded"):
        if resolution.get(key) is not False:
            errors.append("asset_resolution_claim:" + key)
    for key in ("source_checkout_present", "runtime_library_present",
                "runtime_library_identity_verified", "surrogate_used",
                "separate_model_archive_required",
                "requires_far_end_reference"):
        if resolution.get(key) is not True:
            errors.append("asset_resolution_true_missing:" + key)
    _eq(errors, "expected_model_path_mismatch",
        resolution.get("expected_model_path"), reference.ECHO_MODEL_PATH)
    _eq(errors, "expected_model_digest_mismatch",
        resolution.get("expected_model_sha256"),
        reference.ECHO_MODEL_SHA256)
    _eq(errors, "expected_full_model_path_mismatch",
        resolution.get("expected_full_model_path"),
        reference.FULL_MODEL_PATH)
    _eq(errors, "expected_full_model_digest_mismatch",
        resolution.get("expected_full_model_sha256"),
        reference.FULL_MODEL_SHA256)
    _eq(errors, "expected_library_path_mismatch",
        resolution.get("expected_library_path"), reference.LIBRARY_PATH)
    _eq(errors, "expected_library_digest_mismatch",
        resolution.get("expected_library_sha256"), reference.LIBRARY_SHA256)

    surrogate = report["surrogate"]
    for key in ("is_localvqe", "is_neural_network", "weights", "checkpoint",
                "model_archive", "quality_claim", "adaptive",
                "noise_suppression_stage", "dereverberation_stage"):
        if surrogate.get(key) is not False:
            errors.append("surrogate_claim:" + key)
    _eq(errors, "surrogate_identity_mismatch", surrogate.get("identity"),
        "localvqe-compact-echo-only-boundary-surrogate-v1")
    _eq(errors, "surrogate_frame_mismatch", surrogate.get("frame_samples"),
        256)
    _eq(errors, "surrogate_latency_mismatch",
        surrogate.get("algorithmic_latency_samples"), 256)
    if surrogate.get("deterministic") is not True \
            or surrogate.get("pure_synthetic") is not True:
        errors.append("surrogate_not_deterministic_synthetic")

    fixture_block = report["fixture"]
    _eq(errors, "fixture_spec_digest_mismatch",
        fixture_block.get("fixture_spec_sha256"),
        reference.FIXTURE_SPEC_DIGEST)
    _eq(errors, "fixture_stream_digest_mismatch",
        fixture_block.get("stream_sha256"), reference.stream_digest())
    _eq(errors, "fixture_samples_mismatch",
        fixture_block.get("stream_samples"), reference.TOTAL_SAMPLES)
    _eq(errors, "fixture_frames_mismatch",
        fixture_block.get("stream_frames"), reference.TOTAL_FRAMES)
    segment_ids = {segment["id"] for segment in reference.SEGMENTS}
    _eq(errors, "fixture_segment_set_mismatch",
        {segment["id"] for segment in fixture_block["segments"]},
        segment_ids)
    _eq(errors, "strata_set_mismatch", set(report["strata"]), segment_ids)
    for name, row in report["strata"].items():
        segment = next(segment for segment in reference.SEGMENTS
                       if segment["id"] == name)
        _eq(errors, "stratum_interval_mismatch:" + name,
            [row["start_sample"], row["end_sample"]],
            [segment["start"], segment["end"]])
        _eq(errors, "stratum_samples_mismatch:" + name, row["samples"],
            segment["end"] - segment["start"])
        _eq(errors, "stratum_nonfinite:" + name,
            row["nonfinite_output_samples"], 0)
        if "echo_only" in segment["roles"]:
            if not isinstance(row.get("echo_erle_db"), float):
                errors.append("stratum_echo_erle_missing:" + name)
            _eq(errors, "stratum_identity_erle:" + name,
                row.get("identity_echo_erle_db"), 0.0)
        if any(role in segment["roles"]
               for role in ("near_only", "overlap")):
            for key in ("near_snr_db", "near_si_sdr_db",
                        "identity_near_snr_db", "identity_near_si_sdr_db",
                        "near_rms_ratio"):
                if not isinstance(row.get(key), float):
                    errors.append(
                        "stratum_near_metric_missing:" + name + ":" + key)
            if "near_only" in segment["roles"]:
                if row["near_snr_db"] != row["identity_near_snr_db"]:
                    errors.append("near_only_not_identity:" + name)

    echo = report["echo"]
    _eq(errors, "echo_identity_erle_mismatch", echo.get("identity_erle_db"),
        0.0)
    if echo["pooled_pre_movement"]["erle_db"] is None:
        errors.append("pre_movement_erle_missing")
    if echo["pooled_post_movement"]["erle_db"] is None:
        errors.append("post_movement_erle_missing")
    if echo["movement_drop_db"] is None or echo["movement_drop_db"] <= 0:
        errors.append("movement_drop_not_positive")
    if echo["pooled_pre_movement"]["erle_db"] <= \
            echo["pooled_post_movement"]["erle_db"]:
        errors.append("movement_pre_not_better_than_post")

    near = report["near_end"]
    if near["pooled_near"]["near_snr_db"] is None \
            or near["pooled_overlap"]["near_snr_db"] is None:
        errors.append("near_end_metric_missing")
    if near["pooled_overlap"]["near_snr_db"] <= \
            near["pooled_overlap"]["identity_near_snr_db"]:
        errors.append("overlap_not_better_than_identity")
    if near["alignment_gain_db"] is None or near["alignment_gain_db"] <= 0:
        errors.append("alignment_gain_not_positive")
    if near["overlap_unaligned_snr_db"] >= near["overlap_aligned_snr_db"]:
        errors.append("unaligned_not_worse")

    peaks = report["peaks"]
    _eq(errors, "clipped_samples_mismatch", peaks.get("clipped_samples"), 0)
    _eq(errors, "nonfinite_outputs_mismatch",
        peaks.get("nonfinite_output_samples"), 0)
    if peaks.get("within_unit_range") is not True:
        errors.append("output_not_within_unit_range")
    if peaks.get("limiter_used") is not False:
        errors.append("limiter_claim")

    alignment = report["alignment"]
    for key, value in (
            ("declared_content_delay_samples", 256),
            ("declared_content_delay_ms", 16),
            ("one_hop_latency_modeled", True),
            ("first_output_hop_is_delay", True),
            ("delay_compensation_applied_for_scoring", True),
            ("source_interval_mapping", "identity"),
            ("measured", False)):
        _eq(errors, "alignment_mismatch:" + key, alignment.get(key), value)

    for key, value in report["state"].items():
        if value is not True:
            errors.append("state_control_failed:" + key)

    controls = report["controls"]
    caller_asset = controls["caller_asset"]
    if caller_asset.get("all_present") is not True \
            or caller_asset.get("all_fail_closed") is not True:
        errors.append("caller_asset_controls_incomplete")
    _eq(errors, "valid_manifest_scope_wrong",
        caller_asset["valid_manifest"],
        {"status": "validated", "verified": True, "loaded": False,
         "executed": False, "imported": False})
    for name in ("workspace_pinned_asset", "pinned_placeholder",
                 "missing_manifest", "absent_file", "relative_path",
                 "hash_mismatch", "wrong_source_commit", "wrong_sample_rate",
                 "wrong_channels", "wrong_frame_size", "wrong_input_format",
                 "wrong_variant", "wrong_render_delay",
                 "wrong_algorithmic_latency", "unexpected_field"):
        if caller_asset[name].get("status") != "rejected":
            errors.append("caller_asset_not_rejected:" + name)

    frame = controls["frame"]
    if frame.get("all_present") is not True \
            or frame.get("all_fail_closed") is not True:
        errors.append("frame_controls_incomplete")
    for name, case in frame["cases"].items():
        if case.get("status") != "rejected" \
                or case.get("state_unchanged") is not True:
            errors.append("frame_control_failed:" + name)
    _eq(errors, "final_partial_end_mismatch",
        frame.get("final_partial_end_sample"), 384)
    _eq(errors, "final_partial_padded_mismatch",
        frame.get("final_partial_padded_samples"), 128)
    _eq(errors, "final_partial_valid_mismatch",
        frame.get("final_partial_valid_samples"), 128)
    if frame.get("state_unchanged_after_rejections") is not True:
        errors.append("frame_state_changed_after_rejection")

    for name in ("sample_rate_hz", "channels", "sample_format",
                 "frame_samples", "variant", "algorithmic_latency_samples",
                 "render_delay_samples", "real_runtime",
                 "model_or_library_used", "missing_session_id",
                 "negative_epoch", "bool_epoch"):
        if controls["config_adverse"][name].get("status") != "rejected":
            errors.append("config_control_not_rejected:" + name)

    reset = controls["reset"]
    for key in ("independent_sessions_uncoupled",
                "reset_matches_fresh_digest", "epoch_propagated"):
        if reset.get(key) is not True:
            errors.append("reset_control_failed:" + key)
    _eq(errors, "reset_output_digest_mismatch",
        reset.get("output_digest"), reset.get("fresh_output_digest"))

    parity = controls["streaming_parity"]
    if parity.get("events_identical") is not True \
            or parity.get("fresh_session_identical") is not True:
        errors.append("streaming_parity_failed")
    _eq(errors, "streaming_digest_mismatch",
        parity.get("offline_digest"), parity.get("streaming_digest"))
    _eq(errors, "streaming_sample_count_mismatch",
        parity.get("offline_samples"), reference.TOTAL_SAMPLES)

    render = controls["delay_and_render"]
    if render.get("delayed_render_is_failure") is not True:
        errors.append("delayed_render_failure_not_recorded")
    if render.get("missing_render_is_failure") is not True:
        errors.append("missing_render_failure_not_recorded")
    if render.get("no_reference_is_misuse_not_a_pass") is not True:
        errors.append("no_reference_misuse_not_labeled")
    if render.get("all_failures_recorded") is not True:
        errors.append("failure_controls_not_recorded")
    if render["delayed_render_collapse_db"] is None \
            or render["delayed_render_collapse_db"] <= 3.0:
        errors.append("delayed_render_collapse_too_small")
    if render["missing_render_collapse_db"] is None \
            or render["missing_render_collapse_db"] <= 6.0:
        errors.append("missing_render_collapse_too_small")

    availability = controls["availability"]
    _eq(errors, "availability_output_samples_mismatch",
        availability.get("output_samples"), reference.TOTAL_SAMPLES)
    _eq(errors, "availability_valid_samples_mismatch",
        availability.get("valid_aligned_samples"),
        reference.TOTAL_SAMPLES - reference.ALGORITHMIC_LATENCY_SAMPLES)
    _eq(errors, "availability_tail_mismatch",
        availability.get("unavailable_tail_samples"),
        reference.ALGORITHMIC_LATENCY_SAMPLES)
    if availability.get("first_hop_is_delay") is not True \
            or availability.get("tail_is_not_scored") is not True:
        errors.append("availability_control_mismatch")

    adverse = report["adverse"]
    for key in ("all_rejected", "all_invalid_cases_rejected",
                "caller_asset_fail_closed", "frame_fail_closed",
                "render_fail_closed"):
        if adverse.get(key) is not True:
            errors.append("adverse_false:" + key)
    _eq(errors, "adverse_config_mismatch",
        adverse.get("config_rejections"), controls["config_adverse"])
    _eq(errors, "adverse_frame_mismatch",
        adverse.get("frame_rejections"), frame["cases"])

    comparison = report["comparison"]
    for key in ("established_task_matched_baseline_reproduced",
                "source_reported_used_for_qualification", "quality_pass"):
        if comparison.get(key) is not False:
            errors.append("comparison_claim:" + key)
    if comparison.get("identity_control_reproduced") is not True:
        errors.append("identity_control_not_reproduced")
    _eq(errors, "regression_count_mismatch",
        comparison.get("regression_count"), len(report["regressions"]))

    timing = report["timing"]
    if timing.get("measured") is not False or \
            timing.get("device_timing") is not False:
        errors.append("timing_claim")
    if timing.get("source_reported_rtf_used_for_qualification") is not False:
        errors.append("source_reported_rtf_used_for_qualification")
    _eq(errors, "declared_delay_samples_mismatch",
        timing.get("declared_content_delay_samples"), 256)
    _eq(errors, "declared_delay_ms_mismatch",
        timing.get("declared_content_delay_ms"), 16)

    _eq(errors, "source_reported_mismatch", report["source_reported"],
        reference.SOURCE_REPORTED)
    if report["source_reported"].get("status") != \
            "source_reported_not_reproduced":
        errors.append("source_reported_not_labeled")
    if report["source_reported"].get("used_for_qualification") is not False:
        errors.append("source_reported_used_for_qualification")

    _eq(errors, "model_provenance_mismatch", report["model_provenance"],
        reference.MODEL_PROVENANCE)
    _eq(errors, "contract_model_provenance_mismatch",
        contract["model_provenance"], reference.MODEL_PROVENANCE)
    provenance = report["model_provenance"]
    _eq(errors, "upstream_commit_mismatch",
        provenance.get("upstream_commit"), reference.UPSTREAM_COMMIT)
    _eq(errors, "upstream_license_mismatch",
        provenance.get("upstream_license"), reference.UPSTREAM_LICENSE)
    _eq(errors, "upstream_repository_mismatch",
        provenance.get("upstream_repository"), reference.UPSTREAM_REPOSITORY)
    model = provenance["model"]
    for key in ("present_in_sdk_worktree", "present_in_research_workspace",
                "downloaded_by_this_package", "copied_or_vendored",
                "loaded_or_executed"):
        if model.get(key) is not False:
            errors.append("model_scope_claim:" + key)
    _eq(errors, "model_digest_mismatch", model.get("sha256"),
        reference.ECHO_MODEL_SHA256)
    _eq(errors, "model_path_mismatch", model.get("expected_path"),
        reference.ECHO_MODEL_PATH)
    full = provenance["full_enhancement_sibling"]
    for key in ("present_in_research_workspace", "downloaded_by_this_package",
                "copied_or_vendored", "loaded_or_executed"):
        if full.get(key) is not False:
            errors.append("full_model_scope_claim:" + key)
    _eq(errors, "full_model_digest_mismatch", full.get("sha256"),
        reference.FULL_MODEL_SHA256)
    source = provenance["source_checkout"]
    if source.get("present") is not True:
        errors.append("source_checkout_not_present")
    _eq(errors, "source_revision_mismatch", source.get("revision"),
        reference.UPSTREAM_COMMIT)
    _eq(errors, "source_license_digest_mismatch",
        source.get("license_sha256"), reference.SOURCE_LICENSE_SHA256)
    if source.get("executed") is not False:
        errors.append("source_execution_claim")
    library = provenance["native_library"]
    if library.get("present") is not True:
        errors.append("library_not_present")
    _eq(errors, "library_digest_mismatch", library.get("sha256"),
        reference.LIBRARY_SHA256)
    if library.get("sha256_matches_pin") is not True:
        errors.append("library_hash_not_matched")
    for key in ("loaded", "executed", "build_provenance_verified"):
        if library.get(key) is not False:
            errors.append("library_scope_claim:" + key)
    runtime = provenance["runtime_environment"]
    for key in ("present", "built_by_this_package", "used_by_this_package"):
        if runtime.get(key) is not False:
            errors.append("runtime_environment_claim:" + key)
    public_adapter = provenance["public_adapter"]
    if public_adapter.get("present_in_research_workspace") is not True:
        errors.append("public_adapter_research_presence_missing")
    if public_adapter.get("present_in_sdk_worktree") is not False:
        errors.append("public_adapter_sdk_presence_claim")
    if public_adapter.get("executed_by_this_package") is not False:
        errors.append("public_adapter_execution_claim")

    _eq(errors, "licensing_analysis_mismatch", report["licensing_analysis"],
        reference.LICENSING_ANALYSIS)
    licensing = report["licensing_analysis"]
    for key in ("standalone_license_file_in_model_archive",
                "model_redistribution_clearance", "product_use_clearance",
                "training_data_provenance_established",
                "legal_review_completed",
                "asset_copied_vendored_built_or_downloaded"):
        if licensing.get(key) is not False:
            errors.append("licensing_rights_claimed:" + key)
    _eq(errors, "licensing_gate_mismatch", licensing.get("blocked_gate"),
        "model_and_runtime_rights")

    _eq(errors, "source_probe_mismatch", report["source_probe"],
        reference.source_probe_payload())
    if contract.get("source_probe") != report["source_probe"]:
        errors.append("contract_source_probe_mismatch")

    _eq(errors, "report_source_pins_mismatch", report["source_pins"],
        reference.SOURCE_PINS)
    _eq(errors, "report_asset_pins_mismatch", report["asset_pins"],
        reference.EXTERNAL_ASSET_PINS)
    _eq(errors, "report_runtime_asset_pin_mismatch",
        report["runtime_asset_pin"], reference.EXTERNAL_RUNTIME_PINS)
    _eq(errors, "report_boundary_pins_mismatch", report["boundary_pins"],
        reference.BOUNDARY_PINS)
    _eq(errors, "contract_source_pins_mismatch", contract["source_pins"],
        reference.SOURCE_PINS)
    _eq(errors, "contract_asset_pins_mismatch", contract["asset_pins"],
        reference.EXTERNAL_ASSET_PINS)
    _eq(errors, "contract_runtime_asset_pin_mismatch",
        contract["runtime_asset_pin"], reference.EXTERNAL_RUNTIME_PINS)
    _eq(errors, "contract_boundary_pins_mismatch",
        contract["boundary_pins"], reference.BOUNDARY_PINS)

    _eq(errors, "exact_blockers_mismatch", report["exact_blockers"],
        reference.EXACT_BLOCKERS)
    _eq(errors, "missing_evidence_mismatch", report["missing_evidence"],
        reference.MISSING_EVIDENCE)
    _eq(errors, "reopening_conditions_mismatch",
        report["reopening_conditions"], reference.REOPENING_CONDITIONS)
    _eq(errors, "contract_exact_blockers_mismatch",
        contract["exact_blockers"], reference.EXACT_BLOCKERS)
    _eq(errors, "release_gate_count_mismatch",
        report.get("release_gate_count"), 8)
    _eq(errors, "contract_release_gate_count_mismatch",
        contract.get("release_gate_count"), 8)
    gates = report["release_gates"]
    if len(gates) != 8:
        errors.append("release_gate_count_is_not_eight")
    if {gate.get("name") for gate in gates} != GATE_NAMES:
        errors.append("release_gate_names_drift")
    for gate in gates:
        if gate.get("status") != "blocked":
            errors.append("gate_not_blocked:" + str(gate.get("name")))
        if not gate.get("evidence") or not gate.get("reopen_condition"):
            errors.append("gate_missing_evidence_or_reopen:"
                          + str(gate.get("name")))
    if contract.get("release_gates") != gates:
        errors.append("contract_release_gates_mismatch")

    profile = report["acceptance_profile"]
    if profile.get("profile") != reference.PROFILE:
        errors.append("acceptance_profile_not_room")
    for item in reference.ACCEPTANCE_PROFILE_ITEMS:
        if profile.get(item) is not True:
            errors.append("acceptance_profile_item_missing:" + item)
    if not profile.get("not_applicable"):
        errors.append("acceptance_profile_not_applicable_empty")
    _eq(errors, "reference_pin_mismatch",
        profile.get("reference_sha256"),
        reference.sha256_file(HERE / "reference.py"))

    if report.get("tool_provenance") != {
            "language": "python", "language_version": "3.12",
            "standard_library_only": True, "third_party_dependencies": [],
            "network_used": False, "bytecode_written": False}:
        errors.append("tool_provenance_mismatch")

    repeat = report["repeatability"]
    if (repeat.get("count") != 3 or repeat.get("byte_identical") is not True
            or len(set(repeat.get("digests", []))) != 1):
        errors.append("cold_start_repeatability_failed")
    core = {key: value for key, value in report.items()
            if key != "repeatability"}
    _eq(errors, "repeatability_digest_mismatch", repeat.get("digests"),
        [hashlib.sha256(reference.canonical_bytes(core)).hexdigest()] * 3)

    identity = report["task_identity"]
    _eq(errors, "task_identity_contract_mismatch",
        contract.get("task_identity"), identity)
    _eq(errors, "task_identity_id_mismatch", identity.get("id"),
        reference.TASK)
    if identity.get("mutable_full_board_hashed_or_pinned") is not False:
        errors.append("mutable_board_hashed_claim")
    row = reference.board_row()
    stable = {
        "id": row.get("id"),
        "component": row.get("component"),
        "repository": row.get("repository"),
        "claim_branch": (row.get("claim") or {}).get("branch"),
    }
    _eq(errors, "board_stable_field_digest_mismatch",
        identity.get("stable_field_digest"),
        reference.sha256(reference.canonical_bytes(stable)))
    _eq(errors, "board_component_mismatch", stable["component"],
        reference.COMPONENT)
    _eq(errors, "board_branch_mismatch", stable["claim_branch"],
        reference.BRANCH)

    contract_report_equivalents = (
        "task", "title", "component", "repository", "branch", "base_commit",
        "profile", "status", "evidence_status", "qualification_status",
        "decision", "defer_before", "qualification", "task_identity",
        "boundary", "format", "caller_supplied_asset_contract",
        "model_provenance", "licensing_analysis", "source_pins", "asset_pins",
        "runtime_asset_pin", "boundary_pins", "exact_blockers",
        "missing_evidence", "reopening_conditions", "scope")
    for key in contract_report_equivalents:
        report_key = "task_id" if key == "task" else (
            "component_id" if key == "component" else key)
        _eq(errors, "contract_report_mismatch:" + key,
            contract.get(key), report.get(report_key))


def check_external_asset_boundary(errors: List[str]) -> None:
    workspace = reference.workspace_root()
    for key, path in (
            ("echo_model", reference.ECHO_MODEL_PATH),
            ("full_model", reference.FULL_MODEL_PATH)):
        if (workspace / path).exists():
            errors.append("external_" + key
                          + "_present_but_report_says_absent")
    environment = workspace / reference.RUNTIME_ENV_PATH
    if environment.exists():
        errors.append("external_environment_present_but_report_says_absent")
    library = workspace / reference.LIBRARY_PATH
    if not library.is_file():
        errors.append("external_runtime_library_missing")
    elif reference.sha256_file(library) != reference.LIBRARY_SHA256:
        errors.append("external_runtime_library_digest_mismatch")
    checkout = workspace / reference.SOURCE_CHECKOUT_PATH
    if not checkout.is_dir():
        errors.append("external_source_checkout_missing")
    license_path = workspace / reference.SOURCE_LICENSE_PATH
    if not license_path.is_file():
        errors.append("external_source_license_missing")
    elif reference.sha256_file(license_path) != reference.SOURCE_LICENSE_SHA256:
        errors.append("external_source_license_digest_mismatch")
    adapter = reference.SDK_ROOT / "adapters/localvqe-aec"
    if adapter.exists():
        errors.append("localvqe_adapter_present_in_sdk_worktree")


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
        head = "\n".join(
            path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    text = README.read_text(encoding="utf-8")
    if f"<!-- {SPDX_COPYRIGHT} -->" not in text or \
            f"<!-- {SPDX_LICENSE} -->" not in text:
        errors.append("missing_markdown_spdx:README.md")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        sidecar = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in sidecar or SPDX_COPYRIGHT not in sidecar:
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
            errors.append(
                "git_" + "_".join(args).replace("-", "") + "_failed")
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
                    errors.append(
                        f"trailing_whitespace:{path.name}:{number}")
                    break
    return len(changed)


def check_source_text(errors: List[str]) -> None:
    text = (HERE / "reference.py").read_text(encoding="utf-8")
    for token in FORBIDDEN_TOKENS:
        if token in text:
            errors.append("forbidden_network_token:" + token)
    for line in (HERE / "SOURCES.sha256").read_text(
            encoding="ascii").splitlines():
        if not line.startswith("#") and "TASKS.json" in line:
            errors.append("mutable_board_file_is_pinned")


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
    check_external_asset_boundary(errors)
    readme_rows = check_readme(errors)
    strict_count = check_strict_rejections(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    check_source_text(errors)
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
        f"PASS pins={pins} json_ok=2 readme_rows={readme_rows} "
        f"strict_rejections_ok={strict_count} reproduction_ok=1 "
        f"licensing_ok=1 scope_ok=1 tests={tests} changed_files={changed} "
        f"profile={reference.PROFILE} status={reference.STATUS} "
        f"qualification={reference.QUALIFICATION} decision={reference.DECISION} "
        f"gates=8 report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
