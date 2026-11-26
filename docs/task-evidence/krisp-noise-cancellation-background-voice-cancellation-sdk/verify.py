#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local Krisp NC/BVC package."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import reference

HERE = Path(__file__).resolve().parent
TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
TASK_PREFIX = reference.TASK_PREFIX
PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  ((?:pkg|source|worktree):[A-Za-z0-9_./-]+)$")


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
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", str(reference.SOURCE_ROOT)))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(raw: str) -> bool:
    return bool(raw) and not raw.startswith("/") and ".." not in Path(raw).parts


def parse_pins(errors: List[str]) -> Dict[str, Tuple[str, Path]]:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return {}
    lines = PINS.read_text(encoding="utf-8").splitlines()
    if not lines or not any(line.startswith("#") for line in lines):
        errors.append("SOURCES.sha256 has no provenance header")
    pins: Dict[str, Tuple[str, Path]] = {}
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        if "TASKS.json" in line:
            errors.append(
                "SOURCES.sha256 must not pin the mutable full TASKS.json")
        match = PIN_LINE.fullmatch(line)
        if not match:
            errors.append("malformed pin: " + repr(line))
            continue
        digest, label = match.groups()
        prefix, raw = label.split(":", 1)
        if not safe_relative(raw):
            errors.append("unsafe pin path: " + label)
            continue
        if label in pins:
            errors.append("duplicate pin: " + label)
            continue
        path = {"pkg": HERE, "source": SOURCE_ROOT,
                "worktree": SDK}[prefix] / raw
        pins[label] = (digest, path)
    if not pins:
        errors.append("no pins found")
    allowed = set(reference.LOCAL_PIN_PATHS) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned package file: " + path.name)
    for name in sorted(allowed - {"SOURCES.sha256"}):
        if "pkg:" + name not in pins:
            errors.append("missing package pin: " + name)
    return pins


def check_pin_targets(pins: Dict[str, Tuple[str, Path]],
                      errors: List[str]) -> int:
    checked = 0
    for label, (digest, path) in sorted(pins.items()):
        if not path.is_file():
            errors.append("missing pin target: " + label)
            continue
        actual = sha256(path.read_bytes())
        if actual != digest:
            errors.append(
                f"pin mismatch: {label} expected={digest} actual={actual}")
        else:
            checked += 1
    return checked


def strict_json(path: Path, errors: List[str]) -> Dict[str, Any] | None:
    try:
        return reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        errors.append(f"strict json failed for {path.name}: {error}")
        return None


def _expect(condition: bool, message: str, errors: List[str]) -> bool:
    if not condition:
        errors.append(message)
    return condition


def check_report(report: Dict[str, Any] | None,
                 errors: List[str]) -> bool:
    if report is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, message, errors) and ok

    expect(report.get("task_id") == reference.TASK, "task_id mismatch")
    expect(report.get("component") == reference.COMPONENT,
           "component mismatch")
    expect(report.get("title") == reference.TITLE, "title mismatch")
    expect(report.get("mode") == reference.MODE, "mode mismatch")
    expect(report.get("profile") == "enhancement", "profile is not enhancement")
    expect(report.get("status") == "proposal_only_incomplete",
           "status mismatch")
    expect(report.get("evidence_status") == "incomplete",
           "evidence_status mismatch")
    expect(report.get("proposal_only") is True,
           "proposal_only is not true")
    expect(report.get("incomplete") is True, "incomplete is not true")
    expect(report.get("decision") == "DEFER", "decision is not DEFER")
    expect(report.get("defer_before") == "opt_in_adapter_exposure",
           "defer boundary mismatch")
    expect(report.get("qualification_status") == "not_qualified",
           "qualification_status mismatch")
    expect(report.get("base_commit") == reference.BASE_COMMIT,
           "base_commit mismatch")
    expect(report.get("branch") == reference.BRANCH, "branch mismatch")
    expect(report.get("worktree") == reference.CLAIM_WORKTREE,
           "worktree mismatch")
    expect(report.get("reviewer") == reference.REVIEWER, "reviewer mismatch")
    expect(report.get("format") == reference.FORMAT, "format mismatch")

    qualification = report.get("qualification", {})
    expect(qualification.get("status") == "not_qualified",
           "nested qualification is not not_qualified")
    expect(qualification.get("candidate_qualified") is False,
           "candidate_qualified is not false")
    expect(qualification.get("no_missing_result_qualifies_candidate") is True,
           "missing-result guard missing")
    expect(qualification.get("decision") == "DEFER",
           "nested decision is not DEFER")
    expect(qualification.get("blocked_gate_count") == 8,
           "blocked gate count is not eight")
    expect(isinstance(qualification.get("blocked_gate_ids"), list)
           and len(qualification["blocked_gate_ids"]) == 8,
           "blocked gate id list is not eight")
    expect(isinstance(qualification.get("reason"), str)
           and bool(qualification["reason"].strip()),
           "qualification reason missing")

    boundary = report.get("boundary", {})
    for key in ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "production_callback_registered", "descriptor_registry_change",
                "shared_build_or_ci_change", "installed_v0_behavior_change",
                "asset_bundled", "weights_vendored", "sdk_callback_invoked",
                "network_used", "adapter_added", "vendor_sdk_imported",
                "vendor_sdk_linked"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    expect(boundary.get("descriptor_settings") == {},
           "descriptor settings are not empty")

    scope = report.get("scope", {})
    for key in ("real_audio", "real_corpus", "real_krisp_runtime",
                "model_executed", "weights_loaded", "weights_downloaded",
                "runtime_invoked", "vendor_runtime_executed",
                "vendor_sdk_imported", "vendor_output_read", "network_used",
                "device_timing", "listening", "benchmark_claim",
                "public_benchmark", "release_claim", "peer_evidence_inherited",
                "processed_data_present"):
        expect(scope.get(key) is False, "scope flag not false: " + key)
    expect(scope.get("task_local_only") is True,
           "task_local_only is not true")

    gates = report.get("gates", [])
    expected_gates = [name for name, _ in reference.GATE_REQUIREMENTS]
    expect([gate.get("id") for gate in gates] == expected_gates,
           "gate IDs or order mismatch")
    expect(len(gates) == 8, "gate count is not eight")
    expect(all(gate.get("status") == "blocked" for gate in gates),
           "a gate is not blocked")
    expect(all(isinstance(gate.get("requirement"), str)
               and bool(gate["requirement"].strip()) for gate in gates),
           "gate requirement missing")
    expect(report.get("remaining_gates") == expected_gates,
           "remaining gates mismatch")

    blockers = report.get("exact_blockers", [])
    expected_blockers = [item["id"] for item in reference.EXACT_BLOCKERS]
    expect([item.get("id") for item in blockers] == expected_blockers,
           "blocker IDs or order mismatch")
    expect(len(blockers) == len(reference.EXACT_BLOCKERS),
           "exact blocker count mismatch")
    expect(all(item.get("state") == "absent" for item in blockers),
           "a blocker is not absent")
    expect(all(isinstance(item.get("requirement"), str)
               and bool(item["requirement"].strip()) for item in blockers),
           "blocker requirement missing")

    artifacts = report.get("required_artifacts", [])
    expect(len(artifacts) == 8, "required artifact count is not eight")
    expect([item.get("id") for item in artifacts]
           == [item["id"] for item in reference.REQUIRED_ARTIFACTS],
           "required artifact IDs or order mismatch")
    expect(all(item.get("present") is False and item.get("verified") is False
               and item.get("blocked") is True and item.get("sha256") is None
               and item.get("bytes") is None for item in artifacts),
           "a required artifact claims presence or identity")

    expect(qualification.get("blocked_gate_ids")
           == [gate["id"] for gate in gates],
           "nested blocked gate IDs differ from gates")

    expect(report.get("status") not in ("qualified", "complete", "passed"),
           "status claims completion")
    expect(report.get("candidate_metrics") is None,
           "candidate_metrics is not null")
    expect(report.get("source_reported_context", {}).get("label")
           == "source_reported_not_measured_here",
           "source-reported context is not labelled")
    expect(report.get("source_reported_context", {}).get("report_line")
           == reference.VENDOR_RECORD_LINE,
           "source-reported line mismatch")
    expect(report.get("merged_sibling_krisp_packages") == [],
           "sibling Krisp packages are claimed merged")
    peers = report.get("peer_evidence", [])
    expect(bool(peers) and all(item.get("inherited_metrics") is False
                               for item in peers),
           "peer evidence is inherited")
    for missing in (reference.MISSING_SDK_PATH,
                    reference.MISSING_MODEL_BUNDLE_PATH,
                    reference.RUNTIME_ENV_PATH,
                    reference.RUNTIME_LOCK_PATH,
                    reference.RIGHTS_RECORD_PATH,
                    reference.COHORT_MANIFEST_PATH,
                    reference.VENDOR_OUTPUT_PATH,
                    reference.RESULTS_PATH):
        expect(missing in report.get("missing_historical_artifacts", []),
               "missing artifact is not recorded: " + missing)

    identity = report.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False,
           "task identity claims a whole-file hash")
    expect(identity.get("gating") == "stable_identity_only",
           "task identity gating mismatch")
    expect(identity.get("source")
           == "audio-benchmark-platform/plan/swarm/TASKS.json",
           "task identity source mismatch")
    expect(set(identity.get("excluded_mutable_fields", []))
           == set(reference.MUTABLE_TASK_FIELDS),
           "mutable field exclusion mismatch")
    expect(report.get("source_pins") == reference.SOURCE_PINS,
           "report source pins differ")
    expect(report.get("boundary_pins") == reference.BOUNDARY_PINS,
           "report boundary pins differ")

    vendor = report.get("vendor_identity", {})
    expect(vendor.get("vendor") == reference.VENDOR, "vendor name mismatch")
    expect(vendor.get("product") == reference.PRODUCT, "product mismatch")
    expect(vendor.get("release_version") is None,
           "fabricated vendor release")
    expect(vendor.get("abi_version") is None, "fabricated vendor ABI")
    expect(vendor.get("artifact_sha256") is None,
           "fabricated vendor artifact digest")
    expect(vendor.get("model_families_verified") == [],
           "vendor model families claim verification")
    expect(vendor.get("entitlement_approved") is False,
           "vendor entitlement claims approval")
    expect(vendor.get("runtime_present") is False,
           "vendor runtime claims presence")
    expect(vendor.get("vendor_output_present") is False,
           "vendor output claims presence")
    expect(vendor.get("terms_reviewed") is False,
           "vendor terms claim review")
    expect(report.get("format", {}).get("krisp_geometry_asserted") is False,
           "format asserts Krisp geometry")

    profile = report.get("enhancement_profile", {})
    expect(profile.get("name") == "enhancement",
           "enhancement profile name mismatch")
    expect(profile.get("satisfied_for_qualification") == [],
           "enhancement profile claims a qualified item")
    expect(profile.get("real_model_metrics") is None,
           "enhancement profile has real-model metrics")
    expect(len(profile.get("required_items", []))
           == len(reference.ENHANCEMENT_REQUIREMENTS),
           "enhancement requirement count mismatch")
    expect(profile.get("source_check", {}).get("all_phrases_present") is True,
           "enhancement profile source phrases missing")
    expect(all(item.get("qualification_effect") == "none"
               and item.get("satisfied_for_qualification") is False
               for item in profile.get("required_items", [])),
           "an enhancement requirement has qualification effect")

    protocol = report.get("reference_protocol", {})
    expect(protocol.get("model_executed") is False,
           "reference protocol claims model execution")
    expect(protocol.get("vendor_runtime_executed") is False,
           "reference protocol claims vendor execution")
    expect(protocol.get("executor") == "absent",
           "reference protocol executor is not absent")
    expect(protocol.get("plan_source") == reference.CONTROL_PLAN_PROVENANCE,
           "plan source is not the labelled control")
    expect(protocol.get("qualification_effect") == "none",
           "reference protocol has a qualification effect")
    expect(protocol.get("geometry", {}).get("krisp_geometry_asserted") is False,
           "reference protocol asserts Krisp geometry")
    expect(protocol.get("geometry", {}).get("task_scope")
           == reference.TASK_SCOPE, "reference protocol scope mismatch")
    expect(protocol.get("identity_energy", {}).get(
        "output_to_noisy_energy_ratio") == "1",
        "identity energy ratio mismatch")
    expect(protocol.get("scaled_energy", {}).get(
        "output_to_noisy_energy_ratio") == "1/4",
        "scaled energy ratio mismatch")
    expect(protocol.get("frames", {}).get("sample_conservation") is True,
           "frame accounting does not conserve samples")
    expect(protocol.get("frames", {}).get("vendor_timing_measured") is False,
           "frame accounting claims vendor timing")
    expect(protocol.get("frames", {}).get("device_timing_measured") is False,
           "frame accounting claims device timing")
    expect(all(item.get("measured") is False
               for item in protocol.get("acceptance_outcomes", [])),
           "an acceptance outcome claims a measurement")

    controls = report.get("controls", {})
    expect(controls.get("adverse_all_rejected") is True,
           "adverse controls are not all rejected")
    expect(controls.get("nonfinite_rejected") is True,
           "nonfinite rejection control missing")
    expect(controls.get("invalid_values_rejected") is True,
           "invalid-value control missing")
    expect(controls.get("missing_asset_rejected_before_processing") is True,
           "missing-asset control missing")
    expect(controls.get("missing_result_never_qualifies") is True,
           "missing-result control missing")
    expect(controls.get("identity_noisy_control_present") is True,
           "identity/noisy control missing")
    expect(controls.get("frame_mapping_declared") is True,
           "frame mapping declaration missing")
    expect(controls.get("scope_mismatch_rejected") is True,
           "scope mismatch control missing")
    expect(controls.get("validator_accepts_well_formed_manifest") is True,
           "positive manifest control missing")
    expect(controls.get("vendor_output_absent") is True,
           "vendor output presence is not recorded")
    expect(controls.get("absence_probes_all_absent") is True,
           "absence probes are not all absent")
    adverse = controls.get("adverse", [])
    expect(len(adverse) == len(reference.ADVERSE_CASE_IDS),
           "adverse control count mismatch")
    expect([item.get("case") for item in adverse]
           == list(reference.ADVERSE_CASE_IDS),
           "adverse control order mismatch")
    expect(all(item.get("result") == "rejected" for item in adverse),
           "an adverse control was accepted")

    audit = report.get("asset_audit", {})
    expect(audit.get("qualified") is False, "asset audit claims qualification")
    expect(audit.get("audit_result") == "absent",
           "asset audit result mismatch")
    expect(audit.get("sdk_present") is False,
           "asset audit claims an SDK")
    expect(audit.get("model_bundle_present") is False,
           "asset audit claims a model bundle")
    expect(audit.get("runtime_env_present") is False,
           "asset audit claims the runtime")
    expect(audit.get("runtime_lock_present") is False,
           "asset audit claims a runtime lock")
    expect(audit.get("license_record_present") is False,
           "asset audit claims a licence")
    expect(audit.get("rights_record_present") is False,
           "asset audit claims a rights record")
    expect(audit.get("cohort_manifest_present") is False,
           "asset audit claims a cohort")
    expect(audit.get("vendor_output_present") is False,
           "asset audit claims vendor output")
    expect(audit.get("results_present") is False,
           "asset audit claims results")
    expect(audit.get("all_absence_probes_absent") is True,
           "asset audit has a present absence probe")
    register = report.get("asset_registry", {})
    expect(register.get("krisp_entry_present") is False,
           "asset register claims a Krisp entry")
    expect(register.get("candidate_count") == 20,
           "asset register candidate count mismatch")

    requirements = {item.get("id"): item
                    for item in report.get("asset_requirements", [])}
    expect(set(requirements) == {
        "vendor_entitlement", "exact_release_and_platform_sdk",
        "model_bundle", "runtime_lock", "vendor_terms_record",
        "rights_and_consent_record", "rights_cleared_cohort",
        "vendor_output_bundle", "separated_external_results"},
        "asset requirement IDs differ")
    for key, requirement in requirements.items():
        expect(requirement.get("sha256") is None,
               "fabricated asset digest: " + key)
        expect(requirement.get("status") == "absent",
               "asset requirement is not absent: " + key)

    contract_data = report.get("caller_asset_contract", {})
    expect(contract_data.get("absent_behavior") == "reject_before_processing",
           "caller asset absent behavior mismatch")
    expect(contract_data.get("asset_is_vendored") is False,
           "caller asset is marked vendored")
    expect(contract_data.get("revision_pin_available") is False,
           "caller revision claims a pin")
    expect(contract_data.get("required_scope") == reference.CALLER_SCOPE,
           "caller scope pin mismatch")
    expect(contract_data.get("required_product") == reference.CALLER_PRODUCT,
           "caller product pin mismatch")
    expect(contract_data.get("allowed_sample_rates_hz")
           == list(reference.ALLOWED_RATES_HZ),
           "caller rate set mismatch")
    expect(report.get("determinism", {}).get(
        "cold_start_regenerations_required") == 3,
        "cold-start requirement is not three")
    return ok


def check_contract(contract: Dict[str, Any] | None,
                   pins: Dict[str, Tuple[str, Path]],
                   errors: List[str]) -> bool:
    if contract is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, message, errors) and ok

    expect(contract.get(reference.SPDX_COPYRIGHT_KEY)
           == "2026 Tsakanyan Hovhannes", "contract SPDX copyright missing")
    expect(contract.get(reference.SPDX_LICENSE_KEY) == "Apache-2.0",
           "contract SPDX license missing")
    expect(contract.get("task") == reference.TASK, "contract task mismatch")
    expect(contract.get("component") == reference.COMPONENT,
           "contract component mismatch")
    expect(contract.get("repository") == "audio-sdk",
           "contract repository mismatch")
    expect(contract.get("mode") == reference.MODE, "contract mode mismatch")
    expect(contract.get("profile") == "enhancement",
           "contract profile mismatch")
    expect(contract.get("status") == "proposal_only_incomplete",
           "contract status mismatch")
    expect(contract.get("decision") == "DEFER", "contract decision mismatch")
    expect(contract.get("qualification_status") == "not_qualified",
           "contract qualification status mismatch")
    expect(contract.get("base_commit") == reference.BASE_COMMIT,
           "contract base commit mismatch")
    expect(contract.get("branch") == reference.BRANCH,
           "contract branch mismatch")
    expect(contract.get("worktree") == reference.CLAIM_WORKTREE,
           "contract worktree mismatch")
    expect(contract.get("reviewer") == reference.REVIEWER,
           "contract reviewer mismatch")
    expect(contract.get("write_scope") == TASK_PREFIX,
           "contract write scope mismatch")
    expect(contract.get("qualification", {}).get("status") == "not_qualified",
           "contract qualification mismatch")
    expect(contract.get("qualification", {}).get("blocked_gate_count") == 8,
           "contract gate count mismatch")
    expect(contract.get("source_pins") == reference.SOURCE_PINS,
           "contract source pins differ")
    expect(contract.get("boundary_pins") == reference.BOUNDARY_PINS,
           "contract boundary pins differ")
    expect(contract.get("boundary", {}).get("registered") is False,
           "contract is registered")
    expect(contract.get("boundary", {}).get("enabled_by_default") is False,
           "contract is enabled by default")
    expect(contract.get("boundary", {}).get("descriptor_settings") == {},
           "contract descriptor settings are not empty")
    expect(len(contract.get("gates", [])) == 8,
           "contract gate count is not eight")
    expect(all(gate.get("status") == "blocked"
               for gate in contract.get("gates", [])),
           "contract has a non-blocked gate")
    expect(len(contract.get("exact_blockers", []))
           == len(reference.EXACT_BLOCKERS),
           "contract blocker count mismatch")
    expect(contract.get("reproduction", {}).get(
        "cold_start_regenerations") == 3,
        "contract cold-start count is not three")
    expect(contract.get("task_row_identity", {}).get(
        "whole_file_hashed") is False,
        "contract task identity claims a whole-file hash")
    expect(set(contract.get("source_pins", {}))
           == set(reference.SOURCE_PINS),
           "contract source pin set differs")
    expect(set(contract.get("boundary_pins", {}))
           == set(reference.BOUNDARY_PINS),
           "contract boundary pin set differs")
    expect(contract.get("sdk_presence", {}).get("present") is False,
           "contract claims an SDK")
    expect(contract.get("sdk_presence", {}).get("model_bundle_present")
           is False, "contract claims models")
    expect(contract.get("caller_asset_contract", {}).get(
        "revision_pin_available") is False,
        "contract claims a caller revision pin")
    return ok


def check_task_row_identity(report: Dict[str, Any],
                            contract: Dict[str, Any],
                            errors: List[str]) -> bool:
    relative = "audio-benchmark-platform/plan/swarm/TASKS.json"
    path = SOURCE_ROOT / relative
    if not path.is_file():
        errors.append("task board unavailable for identity check")
        return False
    try:
        document = reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        errors.append("task board strict JSON failed: " + str(error))
        return False
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == reference.TASK]
    if len(rows) != 1:
        errors.append("expected exactly one linked task row")
        return False
    row = rows[0]
    stable = {field: row.get(field) for field in reference.STABLE_TASK_FIELDS}
    digest = sha256(reference.canonical_bytes(stable))
    ok = True
    ok = _expect(report.get("task_row_identity", {}).get("stable_sha256")
                 == digest, "report task identity digest is stale", errors) and ok
    ok = _expect(contract.get("task_row_identity", {}).get("stable_sha256")
                 == digest, "contract task identity digest is stale", errors) and ok
    ok = _expect(report.get("task_row_identity", {}).get("stable_fields")
                 == stable, "report stable fields differ from the board", errors) and ok
    claim = row.get("claim") or {}
    ok = _expect(claim.get("base_commit") == reference.BASE_COMMIT,
                 "board claim base commit differs", errors) and ok
    ok = _expect(claim.get("branch") == reference.BRANCH,
                 "board claim branch differs", errors) and ok
    ok = _expect(claim.get("worktree") == reference.CLAIM_WORKTREE,
                 "board claim worktree differs", errors) and ok
    ok = _expect(claim.get("reviewer") == reference.REVIEWER,
                 "board claim reviewer differs", errors) and ok
    for text, label in ((report, "report"), (contract, "contract")):
        encoded = reference.canonical_bytes(text).decode("utf-8")
        if re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', encoded):
            _expect(False, f"{label} contains a whole-file TASKS.json digest",
                    errors)
            ok = False
    return ok


def check_assets(report: Dict[str, Any], errors: List[str]) -> bool:
    audit = report.get("asset_audit", {})
    observed = audit.get("observed", {})
    live = reference.audit_assets()
    if observed != live:
        errors.append("asset audit observation is stale")
        return False
    ok = True
    ok = _expect(live["sdk_present"] is False,
                 "a Krisp SDK appeared; re-evaluate the blocker", errors) and ok
    ok = _expect(live["model_bundle_present"] is False,
                 "a model bundle appeared; re-evaluate the blocker",
                 errors) and ok
    ok = _expect(live["runtime_env_present"] is False,
                 "a runtime appeared; re-evaluate the blocker", errors) and ok
    ok = _expect(live["runtime_lock_present"] is False,
                 "a runtime lock appeared; re-evaluate the blocker",
                 errors) and ok
    ok = _expect(live["license_record_present"] is False,
                 "a licence appeared; re-evaluate the rights blocker",
                 errors) and ok
    ok = _expect(live["rights_record_present"] is False,
                 "a rights record appeared; re-evaluate the blocker",
                 errors) and ok
    ok = _expect(live["cohort_manifest_present"] is False,
                 "a cohort appeared; re-evaluate the blocker", errors) and ok
    ok = _expect(live["vendor_output_present"] is False,
                 "vendor output appeared; re-evaluate the blocker",
                 errors) and ok
    ok = _expect(live["results_present"] is False,
                 "results appeared; re-evaluate the blocker", errors) and ok
    ok = _expect(live["all_absence_probes_absent"] is True,
                 "an absence probe is present; re-evaluate the blocker",
                 errors) and ok
    ok = _expect(live["asset_register"]["krisp_entry_present"] is False,
                 "a Krisp asset-register entry appeared; re-evaluate",
                 errors) and ok
    return ok


def check_artifacts(errors: List[str]) -> bool:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "all", "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True,
        check=False)
    if result.returncode != 0:
        errors.append(
            "generated artifacts are not reproducible: "
            + (result.stderr.strip() or result.stdout.strip()))
        return False
    return True


def _prepare_scratch(root: Path, index: int) -> Tuple[Path, Path, Path]:
    workspace = root / f"cold-{index}" / "audioml"
    sdk = workspace / "worktrees/audio-sdk/SDK-KRISP"
    target = sdk / TASK_PREFIX
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for name in ("audio-benchmark-platform", "research"):
        link = workspace / name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(SOURCE_ROOT / name)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(SDK / relative)
    return workspace, sdk, target


def check_cold_start_regeneration(errors: List[str]) -> List[str]:
    committed = (
        (CONTRACT.read_bytes() if CONTRACT.is_file() else b""),
        (REPORT.read_bytes() if REPORT.is_file() else b""),
        (SIDECAR.read_bytes() if SIDECAR.is_file() else b""),
        (PINS.read_bytes() if PINS.is_file() else b""),
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: List[str] = []
    scratch_root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    try:
        with tempfile.TemporaryDirectory(
                prefix="sdk-krisp-cold-", dir=scratch_root) as temporary:
            root = Path(temporary)
            for index in range(1, 4):
                workspace, sdk, target = _prepare_scratch(root, index)
                environment = dict(
                    os.environ, PYTHONDONTWRITEBYTECODE="1",
                    PYTHONHASHSEED="0", SOURCE_ROOT=str(workspace),
                    SDK_ROOT=str(sdk))
                process = subprocess.run(
                    [sys.executable, "run.py", "all"], cwd=target,
                    capture_output=True, text=True, env=environment)
                if process.returncode != 0:
                    errors.append(
                        f"cold_start_{index}_failed:"
                        + (process.stderr.strip() or process.stdout.strip()))
                    continue
                generated = (
                    (target / "contract.json").read_bytes(),
                    (target / "report.json").read_bytes(),
                    (target / "report.json.sha256").read_bytes(),
                    (target / "SOURCES.sha256").read_bytes(),
                )
                if generated != committed:
                    errors.append(f"cold_start_{index}_bytes_differ")
                digests.append(hashlib.sha256(generated[1]).hexdigest())
    except OSError as error:
        errors.append("cold regeneration scratch unavailable: " + str(error))
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def check_licensing(errors: List[str]) -> bool:
    copyright_line = "SPDX-" "FileCopyrightText: 2026 Tsakanyan Hovhannes"
    license_line = "SPDX-" "License-Identifier: Apache-2.0"
    ok = True
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if path.suffix in (".py", ".md"):
            head = "\n".join(
                path.read_text(encoding="utf-8").splitlines()[:8])
            if copyright_line not in head or license_line not in head:
                errors.append("missing SPDX header: " + path.name)
                ok = False
        elif path.suffix in (".json", ".sha256") and not path.name.endswith(
                ".license"):
            sidecar = path.with_name(path.name + ".license")
            if not sidecar.is_file():
                errors.append("missing SPDX sidecar: " + sidecar.name)
                ok = False
                continue
            text = sidecar.read_text(encoding="utf-8")
            if copyright_line not in text or license_line not in text:
                errors.append("invalid SPDX sidecar: " + sidecar.name)
                ok = False
    sidecar = HERE / "SOURCES.sha256.license"
    if not sidecar.is_file():
        errors.append("missing SPDX sidecar: SOURCES.sha256.license")
        ok = False
    else:
        text = sidecar.read_text(encoding="utf-8")
        if copyright_line not in text or license_line not in text:
            errors.append("invalid SPDX sidecar: SOURCES.sha256.license")
            ok = False
    reuse = SDK / "REUSE.toml"
    if reuse.is_file():
        text = reuse.read_text(encoding="utf-8")
        if '"docs/**"' not in text and "docs/**" not in text:
            errors.append("REUSE.toml does not cover docs/**")
            ok = False
    else:
        errors.append("REUSE.toml missing")
        ok = False
    return ok


def check_scope(errors: List[str]) -> bool:
    if not (SDK / ".git").exists():
        return True
    result = subprocess.run(
        ["git", "-C", str(SDK), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("git status failed: " + result.stderr.strip())
        return False
    ok = True
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        if not path.startswith(TASK_PREFIX):
            errors.append("out of scope change: " + path)
            ok = False
    for arguments in (
            ["diff", "--name-only", reference.BASE_COMMIT, "--"],
            ["diff", "--cached", "--name-only", reference.BASE_COMMIT, "--"]):
        diff = subprocess.run(
            ["git", "-C", str(SDK), *arguments],
            capture_output=True, text=True, check=False)
        if diff.returncode != 0:
            errors.append(
                "git diff against base failed: " + diff.stderr.strip())
            ok = False
            continue
        for path in diff.stdout.splitlines():
            path = path.strip()
            if path and not path.startswith(TASK_PREFIX):
                errors.append("base out of scope change: " + path)
                ok = False
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(
            ["git", "-C", str(SDK), *arguments],
            capture_output=True, text=True, check=False)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append(
                "git " + " ".join(arguments).replace("--", "")
                + " failed: " + diff.stdout.strip())
            ok = False
    return ok


def main() -> int:
    errors: List[str] = []
    pins = parse_pins(errors)
    verified = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    json_ok = report is not None and contract is not None
    report_ok = check_report(report, errors) if report is not None else False
    contract_ok = (
        check_contract(contract, pins, errors) if contract is not None else False)
    identity_ok = (
        check_task_row_identity(report, contract, errors)
        if report is not None and contract is not None else False)
    assets_ok = check_assets(report, errors) if report is not None else False
    licensing_ok = check_licensing(errors)
    artifacts_ok = check_artifacts(errors)
    cold = check_cold_start_regeneration(errors)
    scope_ok = check_scope(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(
            f"verify_result=FAILED pins={verified}/{len(pins)} "
            f"json_ok={json_ok} report_ok={report_ok} "
            f"contract_ok={contract_ok} identity_ok={identity_ok} "
            f"assets_ok={assets_ok} licensing_ok={licensing_ok} "
            f"artifacts_ok={artifacts_ok} scope_ok={scope_ok} "
            f"cold_starts={len(cold)} report_sha256={digest}")
        return 1
    print(
        f"verify_result=OK pins={verified}/{len(pins)} json_ok={json_ok} "
        f"report_ok={report_ok} contract_ok={contract_ok} "
        f"identity_ok={identity_ok} assets_ok={assets_ok} "
        f"licensing_ok={licensing_ok} artifacts_ok={artifacts_ok} "
        f"scope_ok={scope_ok} cold_starts={len(cold)}/3 byte_identical=true "
        f"profile=Enhancement status={reference.STATUS} decision=DEFER "
        f"report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
