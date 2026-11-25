# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-GTCRN-DNS3-OFFLINE evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins or
digests, README digest/gate drift, invalid/missing/nonfinite case acceptance,
an unpinned task file, license gaps, out-of-scope worktree changes, a foreign
interpreter, a caller-supplied-asset gate that is not blocked, or a dirty
``git diff --check``. Never writes.
"""

from __future__ import annotations

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
ADAPTER = HERE / "adapter.json"
PROVIDER = HERE / "provider.json"
ASSET = HERE / "asset.json"
LICENSE_SIDECARS = (
    "contract.json.license", "adapter.json.license", "provider.json.license",
    "asset.json.license", "report.json.license", "report.json.sha256.license",
    "SOURCES.sha256.license",
)
REQUIRED_REPORT_KEYS = {
    "schema_id", "task_id", "title", "component_id", "reference_family",
    "base_commit", "branch", "profile", "status", "evidence_status",
    "qualification_status", "decision", "defer_before",
    "no_missing_result_qualifies_candidate", "scope", "boundary", "format",
    "model_geometry", "asset_boundary", "public_boundary", "source_pins",
    "boundary_pins", "asset_pins", "artifact_pins", "contract_sha256",
    "acceptance_profile", "conditions", "controls", "identity_reconstruction",
    "adverse", "regressions", "independent_timing_evidence",
    "prior_pilot_provenance", "readiness", "rights_gap", "licensing_analysis",
    "model_provenance", "caller_supplied_asset_gate", "surrogate_limitations",
    "scorer", "missing_evidence", "negative_claims", "evidence_classes",
    "exact_blockers", "gates", "repeatability",
}
ACCEPTANCE_CASES = {
    "identity_noisy_control", "established_task_matched_baseline",
    "paired_si_sdr_stoi", "clean_speech_preservation",
    "peaks_and_invalid_outputs", "unpaired_speech",
    "alignment_state_memory_timing",
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
        "adapter": _strict_json(ADAPTER, errors, "adapter"),
        "provider": _strict_json(PROVIDER, errors, "provider"),
        "asset": _strict_json(ASSET, errors, "asset"),
    }
    if not all(payloads.values()):
        return payloads
    if CONTRACT.read_bytes() != reference.contract_bytes():
        errors.append("contract_not_canonical_bytes")
    for name in ("adapter", "provider", "asset"):
        expected = reference.canonical_bytes(payloads[name]) + b"\n"
        if (HERE / (name + ".json")).read_bytes() != expected:
            errors.append(name + "_not_canonical_bytes")
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
    adapter = payloads["adapter"]
    provider = payloads["provider"]
    asset = payloads["asset"]

    if report["base_commit"] != reference.BASE_COMMIT:
        errors.append("base_commit_mismatch")
    if report["branch"] != reference.BRANCH or contract.get("branch") != reference.BRANCH:
        errors.append("branch_mismatch")
    if report["profile"] != reference.PROFILE or contract.get("verification_profile") != reference.PROFILE:
        errors.append("enhancement_profile_not_applied")
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
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")

    for key in ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "shared_cmakelists_change",
                "installed_v0_behavior_change", "processor_exposure", "ci_change"):
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
            ("istft_length", "input_sample_count"),
            ("output_samples", "input_sample_count"),
            ("source_time_mapping", "identity"),
            ("content_delay_samples", 0), ("content_delay_ms", 0.0),
            ("streaming_state", "none_offline_whole_utterance"),
            ("real_time_causal", False), ("measured_timing", False)):
        if geometry.get(key) != value:
            errors.append("geometry_mismatch:" + key)

    assets = report["asset_boundary"]
    if assets.get("asset_present") is not False:
        errors.append("asset_claimed_present")
    for key in ("asset_loaded_or_hashed", "asset_rights_verified", "runtime_available",
                "torch_invoked", "silent_fallback_to_surrogate"):
        if assets.get(key) is not False:
            errors.append("asset_boundary_not_false:" + key)
    if assets.get("real_path_status") != "rejected_asset_unavailable":
        errors.append("real_path_not_asset_unavailable")
    if assets.get("expected_files") != [dict(item) for item in reference.EXPECTED_ASSET_FILES]:
        errors.append("asset_expected_files_mismatch")
    if asset.get("asset_present") is not False:
        errors.append("asset_json_claims_present")
    if asset.get("license") != "unverified_absent":
        errors.append("asset_license_claimed")
    if asset.get("silent_fallback_to_surrogate") is not False:
        errors.append("asset_json_permits_fallback")
    if asset.get("assets") != [dict(item) for item in reference.EXPECTED_ASSET_FILES]:
        errors.append("asset_json_pins_mismatch")
    if asset.get("runtime") != reference.EXPECTED_RUNTIME:
        errors.append("asset_json_runtime_mismatch")
    if report["asset_pins"] != reference.ASSET_PINS or contract.get("asset_pins") != reference.ASSET_PINS:
        errors.append("asset_pins_mismatch")

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

    if adapter.get("source_sha256") != reference.SOURCE_PINS[
            "source:adapters/gtcrn/run.py"]:
        errors.append("adapter_source_identity_mismatch")
    if adapter.get("registered") is not False or adapter.get("default_enabled") is not False:
        errors.append("adapter_not_opt_in")
    for key, value in (("n_fft", 512), ("window_samples", 512), ("hop_samples", 256),
                       ("content_delay_samples", 0), ("input_kind", "waveform_utterance"),
                       ("output_kind", "waveform_utterance")):
        if adapter.get(key) != value:
            errors.append("adapter_boundary_mismatch:" + key)
    if provider.get("registered") is not False or provider.get("default_enabled") is not False:
        errors.append("provider_not_opt_in")
    if provider.get("descriptor_settings") != {}:
        errors.append("provider_descriptor_settings_not_empty")
    if provider.get("public_api_abi_changed") is not False:
        errors.append("provider_claims_abi_change")
    if provider.get("torch_runtime_invoked") is not False:
        errors.append("provider_claims_torch_runtime")

    if report["model_provenance"] != reference.model_provenance():
        errors.append("model_provenance_mismatch")
    if contract.get("model_provenance") != reference.model_provenance():
        errors.append("contract_model_provenance_mismatch")
    provenance = report["model_provenance"]
    if provenance["upstream_commit"] != reference.UPSTREAM_COMMIT:
        errors.append("upstream_commit_mismatch")
    if provenance["upstream_repository"] != reference.UPSTREAM_REPOSITORY:
        errors.append("upstream_repository_mismatch")
    if provenance["upstream_license"] != reference.UPSTREAM_LICENSE:
        errors.append("upstream_license_mismatch")
    for section in ("source_file", "checkpoint"):
        item = provenance[section]
        if (item["present_in_sdk_worktree"] is not False
                or item["present_in_research_checkout"] is not True
                or item["loaded_or_executed"] is not False):
            errors.append("provenance_scope_claim_invalid:" + section)
    if provenance["runtime_lock"]["installed_in_sdk_worktree"] is not False:
        errors.append("runtime_installed_claim_invalid")

    licensing = report["licensing_analysis"]
    if licensing != reference.LICENSING_ANALYSIS:
        errors.append("licensing_analysis_mismatch")
    if contract.get("licensing_analysis") != reference.LICENSING_ANALYSIS:
        errors.append("contract_licensing_analysis_mismatch")
    for key in ("checkpoint_specific_terms_recorded",
                "checkpoint_license_text_present_in_ledger",
                "training_data_provenance_established",
                "training_eval_overlap_assessed",
                "runtime_redistribution_terms_established",
                "redistribution_clearance", "product_use_clearance",
                "legal_review_completed",
                "asset_copied_vendored_built_or_downloaded"):
        if licensing.get(key) is not False:
            errors.append("rights_claimed:" + key)
    if licensing.get("blocked_gate") != "weight_and_runtime_rights_cleared":
        errors.append("licensing_gate_mismatch")
    rights = report["rights_gap"]
    if rights.get("blocked") is not True:
        errors.append("rights_gap_not_blocked")
    for key in ("model_weight_terms_verified", "training_data_provenance_verified",
                "torch_redistribution_terms_verified"):
        if rights.get(key) is not False:
            errors.append("rights_gap_claims_verified:" + key)

    gate = report["caller_supplied_asset_gate"]
    if gate.get("status") != "blocked":
        errors.append("asset_gate_not_blocked")
    for key in ("asset_present_in_sdk_worktree", "asset_loaded_or_hashed_by_package",
                "runtime_available", "torch_importable_in_evidence_interpreter",
                "inference_executed"):
        if gate.get(key) is not False:
            errors.append("asset_gate_claim_invalid:" + key)
    if gate.get("real_path_status") != "rejected_asset_unavailable":
        errors.append("asset_gate_real_path_status_mismatch")
    if gate["validation_asset_absent"].get("reason") != "blocked_asset_absent":
        errors.append("asset_gate_absence_not_detected")
    if gate["validation_runtime_unavailable"].get("reason") != "blocked_runtime_unavailable":
        errors.append("asset_gate_runtime_not_detected")
    if gate["positive_control"].get("status") != "ready_for_caller_execution":
        errors.append("asset_gate_positive_control_failed")
    for name in ("validation_asset_absent", "validation_runtime_unavailable", "positive_control"):
        if gate[name].get("inference_executed") is not False:
            errors.append("asset_gate_executed_inference:" + name)

    readiness = report["readiness"]
    if readiness.get("conclusion") != "not_ready":
        errors.append("readiness_not_not_ready")
    if readiness.get("decision") != reference.DECISION:
        errors.append("readiness_decision_mismatch")
    if readiness.get("defer_before") != reference.DEFER_BEFORE:
        errors.append("readiness_defer_mismatch")
    for key in ("asset_available", "runtime_available", "rights_cleared"):
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
    if acceptance["mapped_cases"]["alignment_state_memory_timing"]["status"] != "partial_analytical":
        errors.append("timing_claim_not_partial")

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
        if case["candidate_metrics"]["nonfinite_count"] != 0:
            errors.append("nonfinite_output:" + prefix)
        if case["candidate_metrics"]["status"] != "measured_synthetic":
            errors.append("candidate_not_measured:" + prefix)

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
    if adverse["config_rejections"]["real_mode_without_asset"]["status"] != "rejected_asset_unavailable":
        errors.append("real_mode_not_asset_unavailable")
    for name, value in adverse["asset_gate"].items():
        if value["status"] != "blocked":
            errors.append("asset_gate_case_not_blocked:" + name)
    if adverse["asset_gate"]["hash_mismatch"]["reason"] != "blocked_hash_mismatch":
        errors.append("asset_gate_hash_mismatch_not_detected")
    if adverse["asset_gate"]["size_mismatch"]["reason"] != "blocked_size_mismatch":
        errors.append("asset_gate_size_mismatch_not_detected")
    if adverse["asset_gate"]["runtime_unavailable"]["reason"] != "blocked_runtime_unavailable":
        errors.append("asset_gate_runtime_not_detected")
    if adverse["asset_gate_control"].get("status") != "ready_for_caller_execution":
        errors.append("asset_gate_control_not_ready")
    if adverse["valid_signal"].get("status") != "ok":
        errors.append("valid_signal_not_ok")

    prior = report["prior_pilot_provenance"]
    if prior.get("used_for_qualification") is not False or prior.get("measured_here") is not False:
        errors.append("prior_pilot_used_for_qualification")
    if prior.get("status") != "source_reported_not_reproduced":
        errors.append("prior_pilot_not_labeled")
    reported = prior["reported"]
    if reported["median_snr_gain_db"] != 5.381 or reported["median_stoi"] != 0.9484:
        errors.append("prior_pilot_values_changed")
    timing = report["independent_timing_evidence"]
    if (timing.get("used_for_qualification") is not False
            or timing.get("measured_here") is not False
            or timing.get("target_device") is not False):
        errors.append("timing_evidence_claimed_qualifying")

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

    if len(report["gates"]) != len(reference.GATE_NAMES):
        errors.append("gate_count_changed")
    if [item["name"] for item in report["gates"]] != list(reference.GATE_NAMES):
        errors.append("report_gate_order_mismatch")
    if contract.get("gates") != list(reference.GATE_NAMES):
        errors.append("contract_gate_order_mismatch")
    for item in report["gates"]:
        if item["status"] != "blocked" or not item["reopen_condition"]:
            errors.append("gate_not_blocked:" + item["name"])

    repeat = report["repeatability"]
    expected_repeat = reference.repeatability()
    if (repeat != expected_repeat or repeat["count"] != 3
            or repeat["byte_identical"] is not True
            or len(set(repeat["digests"])) != 1):
        errors.append("repeatability_failed")


def check_asset_ledger(errors: List[str]) -> None:
    ledger_path = reference.SOURCE_ROOT / "research/noise_suppression_assets_20261027.json"
    try:
        ledger = reference.strict_json(ledger_path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("asset_ledger_unreadable:" + str(error))
        return
    candidates = [item for item in ledger.get("candidates", [])
                  if item.get("id") == "GTCRN-DNS3"]
    if len(candidates) != 1:
        errors.append("asset_ledger_candidate_mismatch")
        return
    candidate = candidates[0]
    if candidate.get("source") != reference.UPSTREAM_REPOSITORY:
        errors.append("asset_ledger_source_mismatch")
    if candidate.get("source_revision") != reference.UPSTREAM_COMMIT:
        errors.append("asset_ledger_revision_mismatch")
    if candidate.get("code_license") != "MIT (upstream repository)":
        errors.append("asset_ledger_code_license_mismatch")
    if "model_license" in candidate or "model_terms" in candidate:
        errors.append("asset_ledger_unexpected_model_terms")
    artifacts = {item.get("path"): item for item in candidate.get("artifacts", [])}
    for expected in reference.EXPECTED_ASSET_FILES:
        path = f"{reference.UPSTREAM_SNAPSHOT}/{expected['path']}"
        actual = artifacts.get(path)
        if actual is None:
            errors.append("asset_ledger_artifact_missing:" + path)
            continue
        if actual.get("bytes") != expected["bytes"]:
            errors.append("asset_ledger_size_mismatch:" + path)
        if actual.get("sha256") != expected["sha256"]:
            errors.append("asset_ledger_hash_mismatch:" + path)


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


def _normalize_remote(url: str) -> str:
    value = url.strip()
    if value.startswith("git@"):
        value = "https://" + value.split("@", 1)[1].replace(":", "/", 1)
    if value.endswith("/"):
        value = value[:-1]
    if value.endswith(".git"):
        value = value[:-4]
    return value


def check_upstream_identity(errors: List[str]) -> None:
    checkout = reference.SOURCE_ROOT / reference.UPSTREAM_SNAPSHOT
    try:
        remote = subprocess.run(
            ["git", "-C", str(checkout), "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True).stdout.strip()
        commit = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()
        present = subprocess.run(
            ["git", "-C", str(checkout), "cat-file", "-e",
             reference.UPSTREAM_COMMIT + "^{commit}"],
            capture_output=True, text=True, check=False)
    except (OSError, subprocess.CalledProcessError) as error:
        errors.append("upstream_identity_failed:" + str(error))
        return
    if _normalize_remote(remote) != _normalize_remote(reference.UPSTREAM_REPOSITORY):
        errors.append("upstream_remote_mismatch:" + remote)
    if commit != reference.UPSTREAM_COMMIT:
        errors.append("upstream_checkout_commit_mismatch:" + commit)
    if present.returncode != 0:
        errors.append("upstream_pinned_commit_absent")


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
            "a" * 64 + "  docs/task-evidence/gtcrn-dns3-offline/unknown",
            "\n".join(["0" * 64 + "  CONTRACTS.md", "0" * 64 + "  CONTRACTS.md"]),
            "Z" * 64 + "  CONTRACTS.md"):
        try:
            reference.parse_pin_lines(text)
            errors.append("strict_pin_parser_accepted:" + repr(text))
        except ValueError:
            pass


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
        if len(items) != len(reference.GATE_NAMES):
            errors.append("readme_gate_count_mismatch:" + str(len(items)))
            return
        for name, item in zip(reference.GATE_NAMES, items):
            if not re.match(r"^\d+\. `" + re.escape(name) + r"`", item):
                errors.append("readme_gate_name_mismatch:" + name)


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
    if len(payloads) == 5 and all(payloads.values()):
        check_content(errors, payloads)
    check_asset_ledger(errors)
    check_scorer(errors)
    check_upstream_identity(errors)
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
    print(f"PASS pins={pins} json_ok=5 interpreter=3.12.16 upstream_identity_ok=1 "
          f"asset_ledger_ok=1 strict_rejections_ok=10 readme_ok=1 "
          f"reproduction_ok={3 if reproduced else 0} "
          f"licensing_ok=1 scope_ok=1 changed_files={changed} "
          f"profile=enhancement status={reference.STATUS} "
          f"qualification={reference.QUALIFICATION_STATUS} decision={reference.DECISION} "
          f"report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
