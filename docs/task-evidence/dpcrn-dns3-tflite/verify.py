# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-DPCRN-DNS3-TFLITE blocker package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins or
digests, README digest/gate drift, invalid/missing/nonfinite case acceptance,
an admitted artifact that does not exist, an unpinned task file, license gaps,
out-of-scope worktree changes, a foreign interpreter, a mutable-board pin, a
caller-artifact gate that is not blocked, or a dirty ``git diff --check``.
Never writes.
"""

from __future__ import annotations

import csv
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
LICENSE_SIDECARS = (
    "contract.json.license", "report.json.license",
    "report.json.sha256.license", "SOURCES.sha256.license",
)
REQUIRED_REPORT_KEYS = {
    "schema_id", "task_id", "title", "component_id", "reference_family",
    "task_mode", "base_commit", "branch", "profile", "status", "evidence_status",
    "qualification_status", "decision", "defer_before",
    "no_missing_result_qualifies_candidate", "qualification", "task_identity",
    "scope", "boundary", "format", "model_geometry", "artifact_requirement",
    "asset_boundary", "public_boundary", "source_pins", "boundary_pins",
    "artifact_pins", "contract_sha256", "acceptance_profile", "conditions",
    "controls", "identity_reconstruction", "adverse", "regressions",
    "locator_evidence", "related_models_not_pooled", "independent_timing_evidence",
    "prior_pilot_provenance", "readiness", "rights_gap", "licensing_analysis",
    "model_provenance", "caller_supplied_artifact_gate", "surrogate_parameters",
    "surrogate_limitations", "scorer", "missing_evidence", "negative_claims",
    "evidence_classes", "exact_blockers", "gates", "repeatability",
}
ACCEPTANCE_CASES = {
    "identity_noisy_control", "established_task_matched_baseline",
    "paired_si_sdr_stoi", "clean_speech_preservation",
    "peaks_and_invalid_outputs", "unpaired_speech",
    "alignment_state_memory_timing", "quantized_edge_runtime",
}


def _strict_json(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.strict_json(path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + label + ":" + str(error))
        return {}
    if not isinstance(payload, dict):
        errors.append("json_root_not_object:" + label)
        return {}
    return payload


def check_interpreter(errors: List[str]) -> None:
    if not reference.interpreter_is_pinned():
        errors.append("interpreter_not_pinned:" + sys.version.split()[0])


def check_pins(errors: List[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    try:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_pin_rejection:" + str(error))
        return 0
    local = {f"{reference.TASK_REL}/{path.name}" for path in HERE.iterdir()
             if path.is_file() and path.name != "SOURCES.sha256"}
    expected = set(reference.SOURCE_PINS) | set(reference.BOUNDARY_PINS) | local
    if {raw for _, raw in pins} != expected:
        errors.append("pin_manifest_key_set_mismatch")
    for digest, raw in pins:
        path = reference.pin_path(raw)
        if not path.is_file():
            errors.append("pin_target_missing:" + raw)
        elif reference.sha256(path.read_bytes()) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    for line in PINS.read_text(encoding="ascii").splitlines():
        if line and not line.startswith("#") and re.search(r"(?:^|/)TASKS\.json$", line):
            errors.append("mutable_task_board_pinned")
            break
    try:
        generated = reference.sources_bytes()
    except OSError as error:
        errors.append("sources_generation_failed:" + str(error))
        return len(pins)
    if PINS.read_bytes() != generated:
        errors.append("SOURCES.sha256_not_deterministic_bytes")
    return len(pins)


def check_json(errors: List[str]) -> Dict[str, Dict[str, Any]]:
    payloads = {
        "report": _strict_json(REPORT, errors, "report"),
        "contract": _strict_json(CONTRACT, errors, "contract"),
    }
    if not all(payloads.values()):
        return payloads
    if CONTRACT.read_bytes() != reference.contract_bytes():
        errors.append("contract_not_canonical_bytes")
    report = payloads["report"]
    missing = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing:
        errors.append("report_missing_keys:" + ",".join(missing))
        return payloads
    if REPORT.read_bytes() != reference.canonical_report_bytes(report):
        errors.append("report_not_canonical_bytes")
    for path in (REPORT, CONTRACT):
        if reference.contains_negative_zero(path.read_bytes()):
            errors.append("negative_zero_in_artifact:" + path.name)
    expected_sidecar = f"{reference.sha256(REPORT.read_bytes())}  report.json\n"
    if not SIDECAR.is_file() or SIDECAR.read_text(encoding="ascii") != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    return payloads


def check_content(errors: List[str], payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]

    if report["base_commit"] != reference.BASE_COMMIT:
        errors.append("base_commit_mismatch")
    if report["branch"] != reference.BRANCH or contract.get("branch") != reference.BRANCH:
        errors.append("branch_mismatch")
    if report["profile"] != reference.PROFILE or contract.get("verification_profile") != reference.PROFILE:
        errors.append("enhancement_profile_not_applied")
    if report.get("task_mode") != reference.TASK_MODE or contract.get("task_mode") != reference.TASK_MODE:
        errors.append("task_mode_not_feasibility")
    for key, expected in (
            ("status", reference.STATUS),
            ("evidence_status", "incomplete"),
            ("qualification_status", reference.QUALIFICATION_STATUS),
            ("decision", reference.DECISION),
            ("defer_before", reference.DEFER_BEFORE)):
        if report.get(key) != expected:
            errors.append("disposition_mismatch:" + key)
    if contract.get("decision") != reference.DECISION:
        errors.append("contract_decision_mismatch")
    if contract.get("evidence_status") != "incomplete":
        errors.append("contract_evidence_status_mismatch")
    if contract.get("qualification_status") != reference.QUALIFICATION_STATUS:
        errors.append("contract_qualification_status_mismatch")
    if contract.get("status") != reference.STATUS:
        errors.append("contract_status_mismatch")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")
    if report["qualification"] != reference.qualification():
        errors.append("qualification_mismatch")
    if contract.get("qualification") != reference.qualification():
        errors.append("contract_qualification_mismatch")

    if report["task_identity"] != {
            "row_projection": reference.TASK_ROW_PROJECTION,
            "row_projection_sha256": reference.TASK_ROW_PROJECTION_SHA256,
            "board_policy": reference.TASK_BOARD_POLICY}:
        errors.append("task_identity_mismatch")
    if report["task_identity"]["board_policy"]["full_tasks_json_pinned"] is not False:
        errors.append("task_board_claimed_pinned")

    for key in ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "shared_cmakelists_change",
                "shared_build_or_ci_change", "installed_v0_behavior_change",
                "processor_exposure", "realtime_streaming_exposed", "ci_change",
                "task_board_or_handoff_write"):
        if report["boundary"].get(key) is not False:
            errors.append("boundary_not_false:" + key)
    if report["boundary"].get("descriptor_settings") != {}:
        errors.append("descriptor_settings_not_empty")
    if report["boundary"].get("installed_v0_geometry_preserved") is not True:
        errors.append("installed_v0_geometry_not_preserved")

    for key, value in (
            ("sample_rate_hz", 16000), ("channels", 1), ("sample_format", "f32"),
            ("frame_samples", 160), ("hop_samples", 160),
            ("content_delay_samples", 0),
            ("installed_v0_geometry_preserved", True),
            ("sdk_callback_invoked", False)):
        if report["format"].get(key) != value:
            errors.append("format_mismatch:" + key)

    geometry = report["model_geometry"]
    for key, value in (
            ("sample_rate_hz", 16000), ("channels", 1), ("sample_format", "f32"),
            ("processing_mode", "offline_whole_utterance"),
            ("n_fft", 512), ("window_samples", 512), ("hop_samples", 256),
            ("hop_ms", 16.0), ("stft_bins", 257),
            ("stft_centered", True), ("stft_padding_samples", 256),
            ("surrogate_frequency_chunks", 16),
            ("istft_length", "input_sample_count"),
            ("output_samples", "input_sample_count"),
            ("source_time_mapping", "identity"),
            ("content_delay_samples", 0), ("content_delay_ms", 0.0),
            ("streaming_state", "none_offline_whole_utterance"),
            ("exact_artifact_geometry_verified", False),
            ("exact_artifact_stream_delay_samples", None),
            ("real_time_causal", False), ("measured_timing", False)):
        if geometry.get(key) != value:
            errors.append("geometry_mismatch:" + key)

    requirement = report["artifact_requirement"]
    if requirement.get("status") != "unresolved":
        errors.append("artifact_requirement_not_unresolved")
    if requirement.get("locator_status") != reference.LOCATOR_STATUS:
        errors.append("artifact_locator_status_mismatch")
    if set(requirement.get("unresolved_fields", [])) != set(
            reference.ARTIFACT_REQUIREMENT["unresolved_fields"]):
        errors.append("artifact_unresolved_fields_changed")
    if contract.get("artifact_requirement") != reference.ARTIFACT_REQUIREMENT:
        errors.append("contract_artifact_requirement_mismatch")

    assets = report["asset_boundary"]
    if assets.get("expected_files") != []:
        errors.append("fabricated_asset_file_list")
    for key in ("admitted_artifact_descriptor_exists", "asset_present",
                "asset_loaded_or_hashed", "asset_rights_verified",
                "runtime_available", "tflite_invoked",
                "silent_fallback_to_surrogate"):
        if assets.get(key) is not False:
            errors.append("asset_boundary_not_false:" + key)
    for key in ("source_commit", "artifact_path", "artifact_sha256", "artifact_bytes"):
        if assets.get(key) is not None:
            errors.append("asset_boundary_claims_pin:" + key)
    if assets.get("real_path_status") != "rejected_unpinned_artifact":
        errors.append("real_path_not_unpinned_artifact")

    if report["source_pins"] != reference.SOURCE_PINS:
        errors.append("report_source_pins_mismatch")
    expected_contract_sources = {path.split(":", 1)[1]: digest
                                 for path, digest in reference.SOURCE_PINS.items()}
    if contract.get("source_pins") != expected_contract_sources:
        errors.append("contract_source_pins_mismatch")
    if report["boundary_pins"] != reference.BOUNDARY_PINS:
        errors.append("report_boundary_pins_mismatch")
    if contract.get("boundary_pins") != reference.BOUNDARY_PINS:
        errors.append("contract_boundary_pins_mismatch")
    if report["artifact_pins"] != reference.report_artifact_pins():
        errors.append("report_artifact_pins_stale")
    if contract.get("artifact_pins") != reference.base_artifact_pins():
        errors.append("contract_artifact_pins_stale")
    if report["contract_sha256"] != reference.sha256(reference.contract_bytes()):
        errors.append("contract_digest_mismatch")

    reference_section = contract.get("reference", {})
    if reference_section.get("registered_in_bench") is not False:
        errors.append("contract_reference_registered")
    if reference_section.get("default_enabled") is not False:
        errors.append("contract_reference_default")
    if reference_section.get("model_weights") is not False:
        errors.append("contract_reference_weights")
    if reference_section.get("tflite_invoked") is not False:
        errors.append("contract_reference_tflite")
    if reference_section.get("tensorflow_invoked") is not False:
        errors.append("contract_reference_tensorflow")

    if report["model_provenance"] != reference.model_provenance():
        errors.append("model_provenance_mismatch")
    if contract.get("model_provenance") != reference.model_provenance():
        errors.append("contract_model_provenance_mismatch")
    provenance = report["model_provenance"]
    if provenance["upstream_repository"] != reference.UPSTREAM_REPOSITORY:
        errors.append("upstream_repository_mismatch")
    for key in ("upstream_commit", "upstream_license", "upstream_license_pin"):
        if provenance.get(key) is not None:
            errors.append("provenance_claims_pin:" + key)
    if provenance["locator_status"] != reference.LOCATOR_STATUS:
        errors.append("locator_status_mismatch")
    for section in ("artifact", "checkpoint"):
        item = provenance[section]
        for key in ("path", "bytes", "sha256", "license_terms"):
            if item.get(key) is not None:
                errors.append("provenance_" + section + "_claims_pin:" + key)
        if item["present_in_sdk_worktree"] is not False:
            errors.append("provenance_scope_claim_invalid:" + section)
        if item["present_in_research_checkout"] is not False:
            errors.append("provenance_research_claim_invalid:" + section)
        if item["loaded_or_executed"] is not False:
            errors.append("provenance_executed_claim_invalid:" + section)
    if provenance["runtime"]["installed_in_sdk_worktree"] is not False:
        errors.append("runtime_installed_claim_invalid")
    if provenance["runtime"]["tflite_importable_in_evidence_interpreter"] is not False:
        errors.append("tflite_import_claim_invalid")

    licensing = report["licensing_analysis"]
    if licensing != reference.LICENSING_ANALYSIS:
        errors.append("licensing_analysis_mismatch")
    if contract.get("licensing_analysis") != reference.LICENSING_ANALYSIS:
        errors.append("contract_licensing_analysis_mismatch")
    for key in ("checkpoint_specific_terms_recorded",
                "checkpoint_license_text_present_in_ledger",
                "tflite_conversion_terms_recorded",
                "training_data_provenance_established",
                "training_eval_overlap_assessed",
                "runtime_redistribution_terms_established",
                "redistribution_clearance", "product_use_clearance",
                "legal_review_completed",
                "asset_copied_vendored_built_or_downloaded"):
        if licensing.get(key) is not False:
            errors.append("rights_claimed:" + key)
    if licensing.get("upstream_code_license") is not None:
        errors.append("code_license_claimed")
    if licensing.get("blocked_gate") != "weight_runtime_and_training_data_rights_cleared":
        errors.append("licensing_gate_mismatch")
    rights = report["rights_gap"]
    if rights.get("blocked") is not True:
        errors.append("rights_gap_not_blocked")
    for key in ("exact_upstream_source_verified", "model_weight_terms_verified",
                "training_data_provenance_verified",
                "tflite_redistribution_terms_verified"):
        if rights.get(key) is not False:
            errors.append("rights_gap_claims_verified:" + key)

    gate = report["caller_supplied_artifact_gate"]
    if gate.get("status") != "blocked":
        errors.append("artifact_gate_not_blocked")
    for key in ("admitted_artifact_descriptor_exists",
                "asset_present_in_sdk_worktree",
                "asset_present_in_research_checkout",
                "asset_loaded_or_hashed_by_package",
                "runtime_available", "tflite_invoked", "tensorflow_invoked",
                "inference_executed", "silent_fallback_to_surrogate"):
        if gate.get(key) is not False:
            errors.append("artifact_gate_claim_invalid:" + key)
    for key in ("pinned_source_commit", "pinned_artifact_path",
                "pinned_artifact_bytes", "pinned_artifact_sha256", "pinned_license"):
        if gate.get(key) is not None:
            errors.append("artifact_gate_claims_pin:" + key)
    if gate.get("real_path_status") != "rejected_unpinned_artifact":
        errors.append("artifact_gate_real_path_status_mismatch")
    if gate.get("positive_control") is not None:
        errors.append("artifact_gate_fabricated_positive_control")
    if gate.get("positive_control_status") != "unavailable_no_canonical_pins":
        errors.append("artifact_gate_positive_control_status_mismatch")
    if gate["validation_asset_absent"].get("reason") != "blocked_asset_absent":
        errors.append("artifact_gate_absence_not_detected")
    if gate["validation_runtime_unavailable"].get("reason") != "blocked_runtime_unavailable":
        errors.append("artifact_gate_runtime_not_detected")
    if gate["validation_fabricated_pins"].get("reason") != "blocked_unpinned_artifact":
        errors.append("artifact_gate_fabricated_pins_accepted")

    readiness = report["readiness"]
    if readiness.get("conclusion") != "not_ready":
        errors.append("readiness_not_not_ready")
    if readiness.get("decision") != reference.DECISION:
        errors.append("readiness_decision_mismatch")
    if readiness.get("defer_before") != reference.DEFER_BEFORE:
        errors.append("readiness_defer_mismatch")
    for key in ("artifact_available", "exact_artifact_identity_pinned",
                "runtime_available", "rights_cleared"):
        if readiness.get(key) is not False:
            errors.append("readiness_claims_available:" + key)
    for key in ("synthetic_surrogate_only", "no_missing_result_qualifies_candidate"):
        if readiness.get(key) is not True:
            errors.append("readiness_missing_disclosure:" + key)
    for key in ("exact_external_blocker", "reopen_condition"):
        value = readiness.get(key)
        if not isinstance(value, str) or len(value.split()) < 12:
            errors.append("readiness_statement_too_short:" + key)

    acceptance = report["acceptance_profile"]
    if acceptance.get("profile") != reference.PROFILE:
        errors.append("acceptance_profile_not_enhancement")
    if set(acceptance.get("mapped_cases", {})) != ACCEPTANCE_CASES:
        errors.append("acceptance_cases_changed")
    if acceptance["mapped_cases"]["unpaired_speech"]["status"] != "not_run":
        errors.append("unpaired_speech_claimed")
    if acceptance["mapped_cases"]["quantized_edge_runtime"]["status"] != "not_run":
        errors.append("quantized_edge_runtime_claimed")
    if acceptance["mapped_cases"]["alignment_state_memory_timing"]["status"] != "partial_analytical":
        errors.append("timing_claim_not_partial")
    if contract.get("acceptance_profile") != acceptance:
        errors.append("contract_acceptance_profile_mismatch")

    if set(report["conditions"]) != set(reference.CONDITIONS):
        errors.append("condition_set_mismatch")
    for name, case in report["conditions"].items():
        prefix = "condition:" + name
        if name == "silence":
            if case["status"] != "excluded_no_reference":
                errors.append("silence_not_excluded")
            if case["candidate_metrics"]["si_sdr_db"] is not None:
                errors.append("silence_has_si_sdr")
            continue
        if case["status"] != "measured_synthetic":
            errors.append("condition_not_measured:" + prefix)
        run = case["offline_run"]
        if run["status"] != "ok" or run["rejections"] != 0:
            errors.append("frozen_signal_rejected:" + prefix)
        if run["samples"] != case["samples"]:
            errors.append("output_length_mismatch:" + prefix)
        if run["frames"] != reference.frame_count(case["samples"]):
            errors.append("frame_count_mismatch:" + prefix)
        if run["delay_compensation_samples"] != 0:
            errors.append("offline_delay_not_zero:" + prefix)
        if run["exact_artifact_geometry_verified"] is not False:
            errors.append("exact_geometry_claimed:" + prefix)
        if case["candidate_metrics"]["nonfinite_count"] != 0:
            errors.append("nonfinite_output:" + prefix)
        if case["candidate_metrics"]["status"] != "measured_synthetic":
            errors.append("candidate_not_measured:" + prefix)
        if case["alignment"]["exact_artifact_delay_samples"] is not None:
            errors.append("exact_delay_claimed:" + prefix)

    controls = report["controls"]
    if controls.get("all_present") is not True:
        errors.append("controls_not_present")
    if controls["identity"].get("name") != "identity_no_processing":
        errors.append("identity_control_missing")
    if controls["named_baseline"].get("name") != "noisy_input_no_processing":
        errors.append("named_baseline_missing")
    for name in ("identity", "named_baseline", "candidate"):
        if controls[name]["metrics"].get("status") != "measured_synthetic":
            errors.append("control_not_measured:" + name)
    if controls["clean_speech_preservation"]["metrics"].get("status") != "measured_synthetic":
        errors.append("clean_preservation_not_measured")

    recomputed = reference.identity_reconstruction()
    if recomputed.get("reconstruction_exact") is not True:
        errors.append("identity_reconstruction_not_exact")
    if report["identity_reconstruction"] != recomputed:
        errors.append("identity_reconstruction_stale")
    if report["regressions"] != reference.regressions(report["conditions"]):
        errors.append("regressions_stale")

    adverse = report["adverse"]
    if adverse.get("all_rejected") is not True:
        errors.append("adverse_all_rejected_false")
    if adverse.get("all_outputs_finite") is not True:
        errors.append("adverse_outputs_nonfinite")
    for section in ("config_rejections", "signal_rejections"):
        for name, value in adverse[section].items():
            if not value["status"].startswith("rejected") or value["output_created"]:
                errors.append("adverse_not_rejected:" + section + ":" + name)
    if adverse["config_rejections"]["real_mode_without_pins"]["status"] != "rejected_unpinned_artifact":
        errors.append("real_mode_not_unpinned_artifact")
    for name, value in adverse["asset_gate"].items():
        if value["status"] != "blocked":
            errors.append("artifact_gate_case_not_blocked:" + name)
        if value["artifact_opened"] is not False:
            errors.append("artifact_gate_case_opened_artifact:" + name)
        if value["download_attempted"] is not False:
            errors.append("artifact_gate_case_attempted_download:" + name)
    for name in ("missing_files", "bad_hash_format", "bad_size",
                 "duplicate_file", "path_traversal", "malformed_not_dict",
                 "missing_key", "wrong_repository", "wrong_geometry",
                 "wrong_runtime"):
        if adverse["asset_gate"][name]["reason"] != "blocked_invalid_request" and \
                adverse["asset_gate"][name]["reason"] not in {
                    "blocked_duplicate_file", "blocked_wrong_repository",
                    "blocked_wrong_geometry", "blocked_runtime_unavailable"}:
            errors.append("artifact_gate_reason_unexpected:" + name)
    if adverse["asset_gate"]["fabricated_pins"]["reason"] != "blocked_unpinned_artifact":
        errors.append("artifact_gate_fabricated_case_accepted")
    if adverse.get("asset_gate_control") is not None:
        errors.append("adverse_fabricated_control")
    if adverse["valid_signal"].get("status") != "ok":
        errors.append("valid_signal_not_ok")

    prior = report["prior_pilot_provenance"]
    if prior.get("used_for_qualification") is not False or prior.get("measured_here") is not False:
        errors.append("prior_pilot_used_for_qualification")
    if prior.get("status") != "not_available" or prior.get("reported") != {}:
        errors.append("prior_pilot_not_labeled_absent")
    timing = report["independent_timing_evidence"]
    if (timing.get("used_for_qualification") is not False
            or timing.get("measured_here") is not False
            or timing.get("target_device") is not False
            or timing.get("reported") != {}):
        errors.append("timing_evidence_claimed_qualifying")
    related = report["related_models_not_pooled"]
    if related.get("metrics_used_for_qualification") is not False:
        errors.append("related_models_used_for_qualification")
    if report["locator_evidence"] != reference.LOCATOR_EVIDENCE:
        errors.append("locator_evidence_mismatch")
    if contract.get("locator_evidence") != reference.LOCATOR_EVIDENCE:
        errors.append("contract_locator_evidence_mismatch")

    for key, value in report["negative_claims"].items():
        if value is not False:
            errors.append("prohibited_claim:" + key)
    for key, value in report["scope"].items():
        if value is not False:
            errors.append("scope_claim:" + key)
    if report["scorer"].get("scorer_id") != reference.SCORER_ID:
        errors.append("scorer_id_mismatch")
    if report["scorer"].get("used_as_oracle") is not False:
        errors.append("scorer_used_as_oracle")
    if len(report["surrogate_limitations"]) != len(reference.SURROGATE_LIMITATIONS):
        errors.append("surrogate_limitations_changed")
    if len(report["missing_evidence"]) != len(reference.MISSING_EVIDENCE):
        errors.append("missing_evidence_changed")
    if report["exact_blockers"] != reference.EXACT_BLOCKERS:
        errors.append("exact_blockers_mismatch")
    if contract.get("exact_blockers") != reference.EXACT_BLOCKERS:
        errors.append("contract_exact_blockers_mismatch")

    if len(report["gates"]) != 8:
        errors.append("gate_count_not_eight")
    if [item["name"] for item in report["gates"]] != list(reference.GATE_NAMES):
        errors.append("report_gate_order_mismatch")
    if contract.get("gates") != reference.gates():
        errors.append("contract_gate_mismatch")
    for item in report["gates"]:
        if item["status"] != "blocked" or not item["reopen_condition"]:
            errors.append("gate_not_blocked:" + item["name"])

    repeat = report["repeatability"]
    expected_repeat = reference.repeatability()
    if (repeat != expected_repeat or repeat["count"] != 3
            or repeat["byte_identical"] is not True
            or len(set(repeat["digests"])) != 1):
        errors.append("repeatability_failed")

    if contract.get("task_identity") != report["task_identity"]:
        errors.append("contract_task_identity_mismatch")
    if contract.get("readiness") != readiness:
        errors.append("contract_readiness_mismatch")
    if contract.get("rights_gap") != report["rights_gap"]:
        errors.append("contract_rights_gap_mismatch")
    if contract.get("related_models_not_pooled") != related:
        errors.append("contract_related_models_mismatch")
    if contract.get("surrogate_parameters") != report["surrogate_parameters"]:
        errors.append("contract_surrogate_parameters_mismatch")


def check_task_identity(errors: List[str]) -> None:
    path = reference.SOURCE_ROOT / "audio-benchmark-platform/plan/INVENTORY.json"
    try:
        inventory = reference.strict_json(path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("inventory_unreadable:" + str(error))
        return
    components = [item for item in inventory.get("components", [])
                  if item.get("id") == reference.COMPONENT_ID]
    if len(components) != 1:
        errors.append("inventory_component_mismatch")
        return
    component = components[0]
    evidence = component.get("evidence", [])
    if not evidence:
        errors.append("inventory_evidence_missing")
        return
    projection = {
        "task_id": component.get("task"),
        "component_id": component.get("id"),
        "name": component.get("name"),
        "repository": component.get("repository"),
        "verification_profile": component.get("verification_profile"),
        "disposition": component.get("disposition"),
        "evidence_status": component.get("evidence_status"),
        "evidence_path": evidence[0].get("path"),
        "evidence_line": evidence[0].get("line"),
    }
    if projection != reference.TASK_ROW_PROJECTION:
        errors.append("inventory_row_projection_mismatch")
    if evidence[0].get("record_name") != reference.CENSUS_RECORD_NAME:
        errors.append("inventory_record_name_mismatch")
    digest = reference.sha256(reference.canonical_bytes(projection))
    if digest != reference.TASK_ROW_PROJECTION_SHA256:
        errors.append("task_row_projection_sha_mismatch")


def check_candidate_accounting(errors: List[str]) -> None:
    path = reference.SOURCE_ROOT / reference.ACCOUNTING_PATH
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error) as error:
        errors.append("candidate_accounting_unreadable:" + str(error))
        return
    matches = [row for row in rows if row.get("id") == "candidate-dpcrn-dns3"]
    if len(matches) != 1:
        errors.append("candidate_accounting_row_mismatch")
        return
    row = matches[0]
    if row.get("eligibility") != "blocked":
        errors.append("candidate_accounting_not_blocked")
    if row.get("weights") != reference.LOCATOR_STATUS:
        errors.append("candidate_accounting_locator_mismatch")
    reason = row.get("reason", "")
    for token in ("pin/hash", "checkpoint licensing", "TensorFlow 1.x", "TFLite"):
        if token not in reason:
            errors.append("candidate_accounting_reason_missing:" + token)


def check_asset_ledger_and_pilot(errors: List[str]) -> None:
    ledger_path = reference.SOURCE_ROOT / "research/noise_suppression_assets_20261027.json"
    try:
        ledger = reference.strict_json(ledger_path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("asset_ledger_unreadable:" + str(error))
        return
    for candidate in ledger.get("candidates", []):
        identifier = str(candidate.get("id", "")).lower()
        if "dpcrn-dns3" in identifier or "dpcrn_dns3" in identifier:
            errors.append("asset_ledger_has_unexpected_dpcrn_dns3_entry")
        for artifact in candidate.get("artifacts", []):
            if "dpcrn_dns3" in str(artifact.get("path", "")).lower():
                errors.append("asset_ledger_has_unexpected_dpcrn_dns3_artifact")
    pilot_path = reference.SOURCE_ROOT / "research/noise_suppression_pilot_20261027.md"
    try:
        pilot = pilot_path.read_text(encoding="utf-8").lower()
    except OSError as error:
        errors.append("pilot_unreadable:" + str(error))
        return
    for token in ("dpcrn_dns3", "dpcrn dns3", "dpcrn-dns3"):
        if token in pilot:
            errors.append("pilot_has_unexpected_dpcrn_dns3_row:" + token)


def check_runtime_absence(errors: List[str]) -> None:
    for module in ("tensorflow", "tflite_runtime", "ai_edge_litert"):
        if importlib.util.find_spec(module) is not None:
            errors.append("runtime_unexpectedly_installed:" + module)


def check_scorer(errors: List[str]) -> None:
    prior = SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/scorer.py"
    if not prior.is_file():
        errors.append("prior_scorer_missing")
        return
    expected = prior.read_text(encoding="utf-8").replace(
        'SCORER_ID = "audio-sdk/online-multichannel-wpe-scoring/0.1"',
        f'SCORER_ID = "{reference.SCORER_ID}"')
    if (HERE / "scorer.py").read_text(encoding="utf-8") != expected:
        errors.append("scorer_not_byte_identical_apart_from_id")
    vectors = SDK_ROOT / "docs/task-evidence/online-multichannel-wpe/crosscheck_vectors.json"
    if not vectors.is_file():
        errors.append("crosscheck_vectors_missing")
        return
    try:
        payload = reference.strict_loads(vectors.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("crosscheck_vectors_unreadable:" + str(error))
        return
    if not isinstance(payload, list) or len(payload) != 6:
        errors.append("crosscheck_vectors_changed")


def check_strict_rejections(errors: List[str]) -> None:
    for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
                 '{"a":-Infinity}'):
        try:
            reference.strict_loads(text)
            errors.append("strict_json_accepted:" + repr(text))
        except ValueError:
            pass
    for text in (
            "not-a-line",
            "a" * 64 + "  ../escape",
            "a" * 64 + "  docs/task-evidence/dpcrn-dns3-tflite/unknown",
            "\n".join(["0" * 64 + "  CONTRACTS.md", "0" * 64 + "  CONTRACTS.md"]),
            "Z" * 64 + "  CONTRACTS.md"):
        try:
            reference.parse_pin_lines(text)
            errors.append("strict_pin_parser_accepted:" + repr(text))
        except ValueError:
            pass
    request = reference._asset_request()
    admitted = reference.validate_asset_request(
        request, asset_present=True, runtime_available=True)
    if admitted.get("status") != "blocked" or admitted.get("reason") != "blocked_unpinned_artifact":
        errors.append("fabricated_artifact_request_accepted")
    if admitted.get("artifact_opened") is not False:
        errors.append("fabricated_artifact_request_opened")


def check_readme(errors: List[str]) -> None:
    path = HERE / "README.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append("readme_unreadable:" + str(error))
        return
    try:
        rows = reference.readme_artifact_digests(text)
    except ValueError as error:
        errors.append("readme_digest_table_invalid:" + str(error))
    else:
        if set(rows) != set(reference.README_ARTIFACT_FILES):
            errors.append("readme_digest_table_files_mismatch")
        for name in reference.README_ARTIFACT_FILES:
            target = HERE / name
            if not target.is_file():
                errors.append("readme_digest_target_missing:" + name)
            elif rows.get(name) != reference.sha256(target.read_bytes()):
                errors.append("readme_digest_stale:" + name)
    try:
        items = reference.readme_gate_items(text)
    except ValueError as error:
        errors.append("readme_gate_list_invalid:" + str(error))
    else:
        if len(items) != 8:
            errors.append("readme_gate_count_mismatch:" + str(len(items)))
            return
        for name, item in zip(reference.GATE_NAMES, items):
            if not re.match(r"^\d+\. `" + re.escape(name) + r"`", item):
                errors.append("readme_gate_name_mismatch:" + name)
    lowered = text.lower()
    for token in ("decision=defer", "not_qualified", "incomplete",
                  "do not fabricate", "do not download", "tasks.json"):
        if token not in lowered:
            errors.append("readme_missing_disclosure:" + token)


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if reference.SPDX_LICENSE_LINE not in head or reference.SPDX_COPYRIGHT_LINE not in head:
            errors.append("missing_python_spdx:" + path.name)
    readme = HERE / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    if (f"<!-- {reference.SPDX_COPYRIGHT_LINE} -->" not in text
            or f"<!-- {reference.SPDX_LICENSE_LINE} -->" not in text):
        errors.append("README_spdx_missing")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        sidecar = path.read_text(encoding="utf-8") if path.is_file() else ""
        if sidecar != reference.LICENSE_TEXT:
            errors.append("license_sidecar_mismatch:" + name)
    reuse_path = SDK_ROOT / "REUSE.toml"
    reuse = reuse_path.read_text(encoding="utf-8") if reuse_path.is_file() else ""
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE_docs_coverage_missing")


def check_scope(errors: List[str]) -> int:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return 0
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            changed.append(path)
            if not path.startswith(reference.TASK_REL + "/"):
                errors.append("out_of_scope_change:" + path)
    diff = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"],
                          capture_output=True, text=True, check=False)
    if diff.returncode != 0:
        errors.append("git_diff_check_failed:" + diff.stdout.strip())
    pinned = {f"{reference.TASK_REL}/{path.name}" for path in HERE.iterdir()
              if path.is_file() and path.name != "SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if (path.is_file() and path.name != "SOURCES.sha256"
                and f"{reference.TASK_REL}/{path.name}" not in pinned):
            errors.append("unpinned_task_file:" + path.name)
    return len(changed)


def check_reproduction(errors: List[str]) -> bool:
    code = ("import sys; sys.path.insert(0, " + repr(str(HERE)) + "); "
            "import reference; sys.stdout.write(reference.sha256("
            "reference.canonical_report_bytes(reference.build_report())))")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    digests: List[str] = []
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                capture_output=True, text=True, check=False)
        if result.returncode != 0:
            errors.append("cold_start_regeneration_failed:" + result.stderr.strip())
            return False
        digests.append(result.stdout.strip())
    if len(set(digests)) != 1:
        errors.append("three_cold_start_regenerations_not_identical")
        return False
    if digests[0] != reference.sha256(REPORT.read_bytes()):
        errors.append("cold_start_digest_differs_from_report")
        return False
    return True


def main() -> int:
    errors: List[str] = []
    check_interpreter(errors)
    pins = check_pins(errors)
    payloads = check_json(errors)
    if len(payloads) == 2 and all(payloads.values()):
        check_content(errors, payloads)
    check_task_identity(errors)
    check_candidate_accounting(errors)
    check_asset_ledger_and_pilot(errors)
    check_runtime_absence(errors)
    check_scorer(errors)
    check_strict_rejections(errors)
    check_readme(errors)
    check_licensing(errors)
    reproduced = check_reproduction(errors)
    changed = check_scope(errors)
    digest = reference.sha256(REPORT.read_bytes()) if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"pins_ok=0 report_sha256={digest} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} json_ok=2 interpreter=3.12.16 "
          f"task_identity_ok=1 candidate_accounting_ok=1 asset_ledger_ok=1 "
          f"runtime_absence_ok=1 strict_rejections_ok=1 readme_ok=1 "
          f"reproduction_ok={3 if reproduced else 0} "
          f"licensing_ok=1 scope_ok=1 changed_files={changed} "
          f"profile=enhancement status={reference.STATUS} "
          f"qualification={reference.QUALIFICATION_STATUS} decision={reference.DECISION} "
          f"gates=8/8_blocked report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
