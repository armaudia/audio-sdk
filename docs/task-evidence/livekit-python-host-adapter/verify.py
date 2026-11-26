#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local LiveKit host package.

The original directory is never written. Regeneration runs in three independent
scratch trees with fresh interpreter processes and symlinks to the pinned,
read-only source and boundary files. The branch scope gate resolves the newest
merge-base against an available PR base ref and fails closed.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"
TASK_PREFIX = reference.TASK_PREFIX
# Concatenated so this literal never contains a contiguous SPDX token.
SPDX_LICENSE = "SPDX-License-" + "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
    ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus", ".pcap", ".pcapng",
    ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wasm", ".wav", ".weights",
    ".whl",
}
GATE_IDS = ("RG-01", "RG-02", "RG-03", "RG-04", "RG-05", "RG-06", "RG-07",
            "RG-08")
BLOCKER_IDS = ("BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05", "BLK-06",
               "BLK-07", "BLK-08")


def sdk_root() -> Path:
    override = os.environ.get("SDK_ROOT")
    if override and (Path(override) / "REUSE.toml").is_file():
        return Path(override)
    cursor = HERE
    while cursor != cursor.parent:
        if (cursor / "REUSE.toml").is_file() and (cursor / "LICENSES").is_dir():
            return cursor
        cursor = cursor.parent
    return HERE.parents[2]


SDK = sdk_root()
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT",
                                  str(reference.SOURCE_ROOT))).resolve()


def _expect(condition: bool, message: str, errors: list[str]) -> bool:
    if not condition:
        errors.append(message)
    return bool(condition)


def check_profile_source(errors: list[str]) -> None:
    try:
        source = reference.profile_source()
    except (OSError, ValueError) as error:
        errors.append("profile_source_failed:" + str(error))
        return
    if source["profile"] != "Tool" or source["key"] != "tool":
        errors.append("profile_source_not_tool")
    if not source["row"].startswith("| Tool |"):
        errors.append("profile_row_not_tool")


def check_pins(errors: list[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    text = PINS.read_text(encoding="ascii")
    try:
        rows = reference.parse_pin_lines(text)
    except ValueError as error:
        errors.append(str(error))
        return 0
    expected = reference.allowed_pin_keys()
    seen: set[str] = set()
    verified = 0
    for digest, path in rows:
        if path in seen:
            errors.append("duplicate_pin:" + path)
            continue
        seen.add(path)
        if path not in expected:
            errors.append("unexpected_pin:" + path)
            continue
        root = (SOURCE_ROOT if path.startswith("source:")
                else SDK if path.startswith("sdk:") else HERE)
        relative = (path[len("source:"):] if path.startswith("source:")
                    else path[len("sdk:"):] if path.startswith("sdk:")
                    else path[len(TASK_PREFIX):])
        target = root / relative
        if not target.is_file():
            errors.append("pin_target_missing:" + path)
            continue
        if reference.sha256_file(target) != digest:
            errors.append("pin_mismatch:" + path)
            continue
        verified += 1
    for path in sorted(expected - seen):
        errors.append("missing_pin:" + path)
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return verified


def _check_common(document: dict | None, label: str,
                  errors: list[str]) -> bool:
    if document is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, label + ":" + message, errors) and ok

    expect(document.get("task") == reference.TASK, "task mismatch")
    expect(document.get("task_id") == reference.TASK, "task_id mismatch")
    expect(document.get("component") == reference.COMPONENT,
           "component mismatch")
    expect(document.get("repository") == reference.REPOSITORY,
           "repository mismatch")
    expect(document.get("mode") == reference.MODE, "mode mismatch")
    expect(document.get("profile") == reference.PROFILE, "profile mismatch")
    expect(document.get("status") == reference.STATUS, "status mismatch")
    expect(document.get("evidence_status") == reference.EVIDENCE_STATUS,
           "evidence_status mismatch")
    expect(document.get("decision") == reference.DECISION,
           "decision mismatch")
    expect(document.get("defer_before") == reference.DEFER_BEFORE,
           "defer_before mismatch")
    expect(document.get("qualification_status")
           == reference.QUALIFICATION_STATUS, "qualification mismatch")
    expect(document.get("base_commit") == reference.BASE_COMMIT,
           "base commit mismatch")
    expect(document.get("branch") == reference.BRANCH, "branch mismatch")
    expect(document.get("worktree") == reference.CLAIM_WORKTREE,
           "worktree mismatch")
    expect(document.get("reviewer") == reference.REVIEWER, "reviewer mismatch")
    expect(document.get("write_scope") == reference.WRITE_SCOPE,
           "write scope mismatch")
    expect(document.get("proposal_only") is True, "proposal_only missing")
    expect(document.get("incomplete") is True, "incomplete missing")
    expect(document.get("source_pins") == reference.SOURCE_PINS,
           "source pins differ")
    expect(document.get("boundary_pins") == reference.BOUNDARY_PINS,
           "boundary pins differ")
    expect(document.get("public_v0_geometry")
           == reference.PUBLIC_V0_GEOMETRY, "public v0 geometry changed")
    boundary = document.get("boundary", {})
    for key in ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "shared_build_or_ci_change",
                "installed_v0_behavior_change", "adapter_json_added",
                "provider_json_added", "network_used",
                "host_package_vendored", "wheel_committed",
                "audio_committed"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    expect(boundary.get("descriptor_settings") == {},
           "descriptor settings are not empty")
    scope = document.get("scope", {})
    for key in ("host_package_installed", "host_package_imported",
                "host_package_executed", "sdk_library_loaded",
                "sdk_callback_invoked", "real_audio", "real_corpus",
                "real_speech", "network_used", "download_attempted",
                "package_install_attempted", "audio_read", "device_timing",
                "listening", "public_benchmark", "benchmark_claim",
                "latency_claim", "release_claim"):
        expect(scope.get(key) is False, "scope flag not false: " + key)
    expect(scope.get("task_local_only") is True,
           "task_local_only is not true")
    gates = document.get("gates", [])
    expect([gate.get("id") for gate in gates] == list(GATE_IDS),
           "gate IDs or order mismatch")
    expect(all(gate.get("status") == "blocked" for gate in gates),
           "a gate is not blocked")
    blockers = document.get("exact_blockers", [])
    expect([item.get("id") for item in blockers] == list(BLOCKER_IDS),
           "blocker IDs or order mismatch")
    expect(all(item.get("state") == "open" for item in blockers),
           "a blocker is not open")
    expect(document.get("qualification", {}).get("status")
           == reference.QUALIFICATION_STATUS, "nested qualification mismatch")
    expect(document.get("qualification", {}).get("candidate_qualified")
           is False, "candidate appears qualified")
    expect(document.get("qualification", {}).get(
        "no_missing_result_qualifies_candidate") is True,
        "missing-result guard missing")
    expect(document.get("qualification", {}).get("blocked_gate_count") == 8,
           "blocked gate count is not eight")
    expect(document.get("qualification", {}).get("blocked_gate_ids")
           == list(GATE_IDS), "blocked gate IDs differ")
    host = document.get("host_source", {})
    expect(host.get("host_package_pair_pinned") is False,
           "host package pair claimed pinned")
    expect(host.get("host_package_version") is None,
           "fabricated host version")
    expect(host.get("host_package_sha256") is None,
           "fabricated host digest")
    expect(host.get("host_package_imported") is False,
           "host package claimed imported")
    expect(host.get("host_geometry_status") == reference.HOST_GEOMETRY_STATUS,
           "host geometry status mismatch")
    expect(host.get("host_api_status") == reference.HOST_API_STATUS,
           "host API status mismatch")
    expect(host.get("host_license_status") == reference.HOST_LICENSE_STATUS,
           "host license status mismatch")
    expect(host.get("sdk_library_loaded") is False,
           "SDK library claimed loaded")
    geometry = document.get("geometry", {})
    expect(geometry.get("host_geometry_status")
           == reference.HOST_GEOMETRY_STATUS, "geometry status mismatch")
    expect(geometry.get("host_geometry_asserted") is False,
           "host geometry is asserted")
    expect(geometry.get("livekit_execution") is False,
           "LiveKit execution claimed")
    for key in ("livekit_frame_size_verified",
                "livekit_sample_rate_verified",
                "livekit_sample_format_verified",
                "livekit_channel_count_verified",
                "livekit_pacing_verified",
                "event_loop_wait_verified"):
        expect(geometry.get(key) is False, "geometry claim: " + key)
    expect(geometry.get("sdk_geometry_source_verified") is True,
           "SDK geometry source not verified")
    expect(geometry.get("sdk_sample_rate_hz") == 16000,
           "SDK sample rate changed")
    expect(geometry.get("sdk_channels") == 1, "SDK channels changed")
    expect(geometry.get("sdk_frame_samples") == 160,
           "SDK frame size changed")
    expect(geometry.get("host_shift_samples") == 480,
           "host shift changed")
    expect(geometry.get("startup_invalid_frames") == 3,
           "startup invalid frames changed")
    expect(geometry.get("wrong_lengths_rejected") == [161, 320, 800],
           "wrong length vectors changed")
    feasibility = document.get("feasibility_verification", {})
    expect(feasibility.get("runnable_source", {}).get("status") == "absent",
           "runnable source is not recorded absent")
    expect(feasibility.get("exact_assets", {}).get("status") == "absent",
           "exact assets are not recorded absent")
    expect(feasibility.get("permitted_scope", {}).get("status")
           == "task_local_evidence_only", "permitted scope mismatch")
    expect(feasibility.get("permitted_scope", {}).get("write_scope")
           == TASK_PREFIX, "permitted scope write prefix mismatch")
    expect(feasibility.get("host_adapter_geometry", {}).get("sdk_status")
           == "source_verified", "SDK geometry source not verified")
    expect(feasibility.get("host_adapter_geometry", {}).get("host_status")
           == reference.HOST_GEOMETRY_STATUS, "host geometry mismatch")
    expect(feasibility.get("host_adapter_geometry", {}).get(
        "livekit_execution") is False, "feasibility geometry claims execution")
    expect(feasibility.get("matched_evidence", {}).get("status") == "absent",
           "matched evidence is not recorded absent")
    expect(feasibility.get("matched_evidence", {}).get("measured_workload")
           is False, "matched evidence claims workload")
    expect(feasibility.get("conclusion") == "defer_external_blocker",
           "feasibility conclusion mismatch")
    identity = document.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False,
           "task identity claims a whole-file hash")
    expect(identity.get("source") == reference.BOARD_TASK_ROW,
           "task identity source mismatch")
    expect(set(identity.get("excluded_mutable_fields", []))
           == set(reference.MUTABLE_FIELDS_EXCLUDED),
           "mutable field exclusion mismatch")
    return ok


def check_report(errors: list[str]) -> bool:
    if not REPORT.is_file():
        errors.append("report.json missing")
        return False
    try:
        report = reference.read_strict_json(REPORT)
    except (OSError, ValueError) as error:
        errors.append("report_strict_json_failed:" + str(error))
        return False
    ok = _check_common(report, "report", errors)
    try:
        reference.assert_no_float(report)
    except ValueError as error:
        errors.append("report:" + str(error))
        ok = False

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, "report:" + message, errors) and ok

    qualification = report.get("qualification", {})
    expect(isinstance(qualification.get("reason"), str)
           and bool(qualification["reason"].strip()),
           "qualification reason missing")
    disposition = report.get("disposition", {})
    expect(disposition.get("decision") == "DEFER", "disposition decision")
    expect(disposition.get("status") == "incomplete", "disposition status")
    expect(disposition.get("missing_result_qualifies") is False,
           "disposition missing-result guard")
    expect(disposition.get("default_enabled") is False,
           "disposition default")
    expect(disposition.get("expose_as_host_adapter") is False,
           "disposition host adapter exposure")
    profile = report.get("tool_profile", {})
    expect(profile.get("name") == "tool", "tool profile name")
    expect(profile.get("satisfied_for_qualification") == [],
           "tool profile claims a satisfied item")
    expect(profile.get("measured_workload_result") is None,
           "tool profile has a measured workload")
    expect(len(profile.get("required_items", []))
           == len(reference.TOOL_REQUIREMENTS), "tool requirement count")
    expect(all(item.get("satisfied_for_qualification") is False
               and item.get("qualification_effect") == "none"
               for item in profile.get("required_items", [])),
           "a tool item has qualification effect")
    protocol = report.get("reference_protocol", {})
    expect(protocol.get("host_package_loaded") is False,
           "reference protocol loads a host package")
    expect(protocol.get("sdk_library_loaded") is False,
           "reference protocol loads the SDK")
    expect(protocol.get("real_audio_used") is False,
           "reference protocol uses audio")
    expect(protocol.get("executor") == "absent",
           "reference protocol executor")
    expect(protocol.get("plan_source") == reference.CONTROL_PLAN_PROVENANCE,
           "plan source is not the labelled control")
    expect(protocol.get("qualification_effect") == "none",
           "reference protocol has qualification effect")
    expect(protocol.get("geometry", {}).get("livekit_geometry_asserted")
           is False, "reference protocol asserts LiveKit geometry")
    expect(protocol.get("conversion", {}).get("sdk_output_samples") == 160,
           "conversion output is not 160")
    expect(protocol.get("conversion", {}).get("nonfinite_output_count") == 0,
           "conversion produced nonfinite samples")
    expect(protocol.get("conversion", {}).get("float_values_retained_in_report")
           is False, "conversion retains floats")
    expect(protocol.get("required_rejected_lengths_all_rejected") is True,
           "wrong lengths are not all rejected")
    expect(all(row.get("exact") is True for row in protocol.get("packing", [])),
           "packing control is not exact")
    expect(all(row.get("drift_samples", 0) == 0
               for row in protocol.get("packing", [])),
           "packing drifts")
    expect(all(row.get("drift_samples", 0) == 0
               for row in protocol.get("shift_models", [])),
           "shift model drifts")
    expect(all(item.get("measured") is False
               for item in protocol.get("shift_models", [])),
           "a shift model claims measurement")
    expect(all(row.get("verified") is False
               for row in protocol.get("policy_checks", [])),
           "a policy check claims verification")
    expect(all(item.get("measured") is False
               for item in protocol.get("acceptance_outcomes", [])),
           "an acceptance outcome claims a measurement")
    controls = report.get("controls", {})
    expect(controls.get("adverse_all_rejected") is True,
           "adverse controls are not all rejected")
    expect(controls.get("adverse_case_count")
           == len(reference.ADVERSE_CASE_IDS), "adverse case count")
    expect(controls.get("nonfinite_rejected") is True,
           "nonfinite control missing")
    expect(controls.get("wrong_lengths_rejected") is True,
           "wrong-length control missing")
    expect(controls.get("missing_asset_rejected_before_processing") is True,
           "missing-asset control missing")
    expect(controls.get("missing_result_never_qualifies") is True,
           "missing-result control missing")
    expect(controls.get("scope_mismatch_rejected") is True,
           "scope mismatch control missing")
    expect(controls.get("variant_mismatch_rejected") is True,
           "variant mismatch control missing")
    expect(controls.get("python_version_mismatch_rejected") is True,
           "python version control missing")
    expect(controls.get("host_geometry_mismatch_rejected") is True,
           "host geometry control missing")
    expect(controls.get("provider_delay_mismatch_rejected") is True,
           "provider delay control missing")
    expect(controls.get("rights_acknowledgement_required") is True,
           "rights acknowledgement control missing")
    expect(controls.get("validator_accepts_well_formed_manifest") is True,
           "positive manifest control missing")
    expect(controls.get("absence_probes_all_absent") is True,
           "absence probes are not all absent")
    expect(controls.get("host_modules_all_absent") is True,
           "host modules are present")
    expect(controls.get("host_package_never_imported") is True,
           "host package import control missing")
    expect(controls.get("sdk_library_never_loaded") is True,
           "SDK library control missing")
    expect(controls.get("audio_never_read") is True,
           "audio control missing")
    adverse = controls.get("adverse", [])
    expect(len(adverse) == len(reference.ADVERSE_CASE_IDS),
           "adverse control count")
    expect(all(item.get("result") == "rejected" for item in adverse),
           "an adverse control was accepted")
    audit = report.get("asset_audit", {})
    expect(audit.get("qualified") is False, "asset audit claims qualification")
    expect(audit.get("audit_result") == "absent", "asset audit result")
    expect(audit.get("host", {}).get("present") is False,
           "asset audit claims a host package")
    expect(audit.get("host", {}).get("host_package_pair_pinned") is False,
           "asset audit claims a host pin")
    expect(audit.get("sdk_build", {}).get("installed_wheel_present") is False,
           "asset audit claims an installed wheel")
    expect(audit.get("sdk_build", {}).get("native_library_present") is False,
           "asset audit claims a native library")
    expect(audit.get("rights", {}).get("rights_cleared_audio_present")
           is False, "asset audit claims rights-cleared audio")
    expect(audit.get("absence", {}).get("all_probes_absent") is True,
           "absence summary is not absent")
    expect(audit.get("module_absence", {}).get("all_modules_absent") is True,
           "module absence summary is not absent")
    expect(audit.get("runtime", {}).get("pinned_python_match") is True,
           "pinned Python is not the reproduction interpreter")
    expect(len(report.get("absence_probes", []))
           == len(reference.ABSENCE_PROBE_PATHS), "absence probe count")
    expect(len(report.get("module_probes", []))
           == len(reference.MODULE_PROBES), "module probe count")
    requirements = {item.get("id"): item
                    for item in report.get("asset_requirements", [])}
    expected_requirements = {
        "pinned_livekit_host_package_pair", "installed_sdk_python_binding",
        "host_api_and_geometry_record", "rights_cleared_host_audio",
        "host_adapter_evidence", "tool_acceptance_evidence",
        "independent_review"}
    expect(set(requirements) == expected_requirements,
           "asset requirement IDs differ")
    for key in expected_requirements:
        expect(requirements.get(key, {}).get("status") == "absent",
               "asset requirement not absent: " + key)
    contract_data = report.get("caller_asset_contract", {})
    expect(contract_data.get("absent_behavior")
           == "reject_before_processing", "caller absent behavior")
    expect(contract_data.get("asset_is_vendored") is False,
           "caller asset is vendored")
    expect(contract_data.get("required_variant") == reference.CALLER_VARIANT,
           "caller variant")
    expect(contract_data.get("required_scope") == reference.CALLER_SCOPE,
           "caller scope")
    expect(contract_data.get("required_python_version")
           == reference.PINNED_PYTHON, "caller python version")
    expect(contract_data.get("required_host_shift_samples") == 480,
           "caller host shift")
    expect(contract_data.get("required_sdk_contract_version") == "0.1",
           "caller SDK contract")
    expect(contract_data.get("required_rights_cleared_audio_acknowledged")
           is True, "caller rights acknowledgement not required")
    expect(report.get("candidate_metrics") is None,
           "candidate_metrics is not null")
    expect(report.get("source_reported_context", {}).get("label")
           == "source_reported_not_measured_here",
           "source-reported context not labelled")
    matrix = report.get("acceptance_matrix_evidence", {})
    expect(matrix.get("sha256") == reference.SOURCE_PINS[
        reference.ACCEPTANCE_SOURCE_REL], "acceptance matrix pin mismatch")
    expect("No pinned/tested LiveKit host package pair"
           in matrix.get("s09_row", ""), "acceptance matrix S09 row missing")
    expect("S09 blocked" in matrix.get("st11_row", ""),
           "acceptance matrix S-T11 row missing")
    expect(report.get("determinism", {}).get(
        "cold_start_regenerations_required") == 3,
        "cold-start requirement is not three")
    expect(report.get("determinism", {}).get("pinned_python")
           == reference.PINNED_PYTHON, "pinned Python mismatch")
    return ok


def check_contract(errors: list[str]) -> bool:
    if not CONTRACT.is_file():
        errors.append("contract.json missing")
        return False
    try:
        contract = reference.read_strict_json(CONTRACT)
    except (OSError, ValueError) as error:
        errors.append("contract_strict_json_failed:" + str(error))
        return False
    ok = _check_common(contract, "contract", errors)
    try:
        reference.assert_no_float(contract)
    except ValueError as error:
        errors.append("contract:" + str(error))
        ok = False

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, "contract:" + message, errors) and ok

    expect(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID,
           "schema id mismatch")
    expect(len(contract.get("tool_profile_requirements", []))
           == len(reference.TOOL_REQUIREMENTS), "tool requirement count")
    expect(len(contract.get("required_artifacts", []))
           == len(reference.REQUIRED_ARTIFACTS), "artifact count")
    expect(contract.get("reproduction", {}).get(
        "cold_start_regenerations") == 3, "cold-start count")
    expect(contract.get("caller_asset_contract", {}).get(
        "required_python_version") == reference.PINNED_PYTHON,
        "contract python version")
    expect(contract.get("caller_asset_contract", {}).get(
        "required_rights_cleared_audio_acknowledged") is True,
        "contract rights acknowledgement not required")
    return ok


def check_task_row_identity(errors: list[str]) -> bool:
    try:
        projection = reference.board_row_projection()
    except (OSError, ValueError) as error:
        errors.append("task_board_identity_failed:" + str(error))
        return False
    ok = True
    for label, path in (("report", REPORT), ("contract", CONTRACT)):
        try:
            document = reference.read_strict_json(path)
        except (OSError, ValueError) as error:
            errors.append(label + "_identity_read_failed:" + str(error))
            ok = False
            continue
        identity = document.get("task_row_identity", {})
        ok = _expect(identity.get("stable_sha256")
                     == projection["stable_sha256"],
                     f"{label}:task identity digest is stale", errors) and ok
        ok = _expect(identity.get("stable_fields")
                     == projection["stable_fields"],
                     f"{label}:stable fields differ from the board",
                     errors) and ok
        ok = _expect(identity.get("claim") == projection["claim"],
                     f"{label}:claim differs from the board", errors) and ok
        encoded = reference.canonical_text(document)
        if re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', encoded):
            errors.append(label + ":contains a whole-file TASKS.json digest")
            ok = False
    return ok


def check_assets(errors: list[str]) -> bool:
    try:
        probes = reference.absence_probes()
        modules = reference.module_absence_probes()
    except (OSError, ValueError) as error:
        errors.append("absence_probe_failed:" + str(error))
        return False
    summary = reference.absence_summary(probes)
    module_summary = reference.module_absence_summary(modules)
    ok = True
    ok = _expect(summary["all_probes_absent"] is True,
                 "an absence probe is present; re-evaluate the blocker",
                 errors) and ok
    ok = _expect(summary["present_count"] == 0,
                 "an absence probe reports a present artifact", errors) and ok
    ok = _expect(module_summary["all_modules_absent"] is True,
                 "a host or SDK module is present; re-evaluate the blocker",
                 errors) and ok
    if REPORT.is_file():
        report = reference.read_strict_json(REPORT)
        audit = report.get("asset_audit", {})
        ok = _expect(audit.get("observed_absence_probes") == probes,
                     "asset audit observation is stale", errors) and ok
        ok = _expect(audit.get("observed_module_probes") == modules,
                     "module audit observation is stale", errors) and ok
        runtime = reference.runtime_probe()
        ok = _expect(runtime["pinned_python_match"] is True,
                     "pinned_python_mismatch:" + runtime["interpreter_version"],
                     errors) and ok
        ok = _expect(audit.get("runtime") == runtime,
                     "runtime audit observation is stale", errors) and ok
    return ok


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        text = ((HERE / name).read_text(encoding="utf-8") if
                (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        text = ((HERE / name).read_text(encoding="utf-8") if
                (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_markdown_spdx:" + name)
    reuse_path = SDK / "REUSE.toml"
    if not reuse_path.is_file():
        errors.append("reuse_toml_missing")
    else:
        reuse = reuse_path.read_text(encoding="utf-8")
        reuse_token = "SPDX-License-" + 'Identifier = "Apache-2.0"'
        if '"docs/**"' not in reuse or reuse_token not in reuse:
            errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            errors.append("task_symlink:" + path.name)
        if path.name in {"CMakeLists.txt", "provider.json", "adapter.json"}:
            errors.append("provider_artifact:" + path.name)
        if path.is_file() and path.name in {"LICENSE", "LICENSE.txt",
                                            "COPYING", "NOTICE"}:
            errors.append("vendored_license_file:" + path.name)


def check_readme(errors: list[str]) -> None:
    if not README.is_file():
        errors.append("README missing")
        return
    text = README.read_text(encoding="utf-8")
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
                  "BLK-01", "BLK-06", "Tool", "tool", "LiveKit", "Python",
                  "pinned", reference.TASK, reference.TITLE,
                  reference.BASE_COMMIT,
                  "No pinned/tested LiveKit host package pair",
                  "reopen"):
        if token not in text:
            errors.append("README is missing token: " + token)
    try:
        reference.verify_readme_digests(text)
    except (OSError, ValueError) as error:
        errors.append("readme_digest_table_failed:" + str(error))


def check_sources_reproduction(errors: list[str]) -> None:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONHASHSEED="0", SOURCE_ROOT=str(SOURCE_ROOT))
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("committed_artifacts_not_reproducible:" +
                      (result.stderr.strip() or result.stdout.strip()))


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
    changed: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK), *arguments],
                              capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
    base = reference.scope_base(SDK)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            base_paths = reference.scope_changed_paths(SDK, base)
        except ValueError as error:
            errors.append(str(error))
        else:
            for path in reference.scope_violations(base_paths):
                errors.append("base_out_of_scope_change:" + path)
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    workspace = scratch / "audioml"
    sdk = workspace / "worktrees/audio-sdk/SDK-LIVEKIT-PYTHON-HOST-ADAPTER"
    target = sdk / reference.TASK_PREFIX
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    link = workspace / "audio-benchmark-platform"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(SOURCE_ROOT / "audio-benchmark-platform")
    for relative in sorted(reference.BOUNDARY_PINS):
        boundary = sdk / relative
        boundary.parent.mkdir(parents=True, exist_ok=True)
        boundary.symlink_to(reference.WORKTREE / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    names = ("contract.json", "report.json", "report.json.sha256",
             "SOURCES.sha256", "README.md")
    committed = tuple((HERE / name).read_bytes() for name in names)
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONHASHSEED="0", SOURCE_ROOT=str(SOURCE_ROOT))
    root_parent = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    with tempfile.TemporaryDirectory(
            prefix="sdk-livekit-host-adapter-cold-",
            dir=root_parent) as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py"],
                                     cwd=target, capture_output=True,
                                     text=True, env=environment)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" +
                              process.stderr.strip())
                continue
            generated = tuple((target / name).read_bytes() for name in names)
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[1]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_profile_source(errors)
    pins = check_pins(errors)
    report_ok = check_report(errors)
    contract_ok = check_contract(errors)
    identity_ok = check_task_row_identity(errors)
    assets_ok = check_assets(errors)
    check_licensing(errors)
    check_readme(errors)
    check_sources_reproduction(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} report_ok={report_ok} "
              f"contract_ok={contract_ok} identity_ok={identity_ok} "
              f"assets_ok={assets_ok} cold_starts={len(digests)} "
              f"report_sha256={digest} changed_files={len(changed)} "
              f"failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(GATE_IDS)} blockers={len(BLOCKER_IDS)} "
          f"tool_items={len(reference.TOOL_REQUIREMENTS)} "
          f"adverse_cases={len(reference.ADVERSE_CASE_IDS)} "
          f"cold_starts=3/3 byte_identical=true profile=Tool "
          f"status={reference.STATUS} decision=DEFER "
          f"report_sha256={digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
