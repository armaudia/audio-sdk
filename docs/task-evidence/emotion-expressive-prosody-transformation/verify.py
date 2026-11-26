#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local evidence package."""

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
TASK_PREFIX = "docs/task-evidence/emotion-expressive-prosody-transformation/"
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
    authored = {
        path.name for path in HERE.iterdir()
        if path.is_file()
        and path.name != "SOURCES.sha256"
        and not path.name.endswith(".pyc")
        and "__pycache__" not in path.name
    }
    for name in sorted(authored):
        if "pkg:" + name not in pins:
            errors.append("unpinned package file: " + name)
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
        return reference.require_json_object(
            reference.load_strict_json(path))
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

    expect(report.get("task_id") == reference.TASK_ID, "task_id mismatch")
    expect(report.get("component") == reference.COMPONENT,
           "component mismatch")
    expect(report.get("title") == reference.TITLE, "title mismatch")
    expect(report.get("mode") == reference.MODE, "mode mismatch")
    expect(report.get("profile") == "voice", "profile is not voice")
    expect(report.get("schema_id") == reference.REPORT_SCHEMA,
           "schema_id mismatch")
    expect(report.get("status") == "proposal_only_incomplete",
           "status mismatch")
    expect(report.get("evidence_status") == "incomplete",
           "evidence_status mismatch")
    expect(report.get("proposal_only") is True,
           "proposal_only is not true")
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
    expect(qualification.get("real_candidate_metrics") is False,
           "qualification claims real candidate metrics")
    expect(isinstance(qualification.get("reason"), str)
           and bool(qualification["reason"].strip()),
           "qualification reason missing")

    boundary = report.get("boundary", {})
    for key in ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "production_callback_registered", "descriptor_registry_change",
                "shared_build_or_ci_change", "installed_v0_behavior_change",
                "asset_bundled", "weights_vendored", "network_used",
                "model_loaded", "processor_exposure"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    expect(boundary.get("descriptor_settings") == {},
           "descriptor settings are not empty")
    expect(boundary == reference.BOUNDARY, "boundary differs from constant")

    scope = report.get("scope", {})
    for key in ("real_audio", "real_corpus", "real_candidate_model",
                "real_weights", "model_executed", "weights_loaded",
                "weights_downloaded", "runtime_invoked", "network_used",
                "device_timing", "listening", "public_benchmark",
                "release_claim"):
        expect(scope.get(key) is False, "scope flag not false: " + key)
    expect(scope.get("task_local_only") is True,
           "task_local_only is not true")
    expect(scope.get("write_scope") == TASK_PREFIX, "scope write mismatch")
    expect(scope == reference.SCOPE, "scope differs from constant")

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
    expect(report.get("release_gates") == gates,
           "release_gates differ from gates")

    blockers = report.get("exact_blockers", [])
    expected_blockers = [item["id"] for item in reference.EXACT_BLOCKERS]
    expect([item.get("id") for item in blockers] == expected_blockers,
           "blocker IDs or order mismatch")
    expect(len(blockers) == 8, "exact blocker count is not eight")
    expect(all(item.get("state") == "absent" for item in blockers),
           "a blocker is not absent")
    expect(qualification.get("blocked_gate_ids")
           == [gate["id"] for gate in gates],
           "nested blocked gate IDs differ from gates")

    expect(report.get("status") not in ("qualified", "complete", "passed"),
           "status claims completion")
    expect(report.get("candidate_metrics") is None,
           "candidate_metrics is not null")
    context = report.get("source_reported_context", {})
    expect(context.get("label") == "source_reported_not_measured_here",
           "source-reported context is not labelled")
    expect(context.get("record") == reference.CANDIDATE_RECORD,
           "candidate record number mismatch")
    expect(context.get("record_status") == "unavailable/blocked",
           "candidate record status mismatch")
    for path in (reference.MISSING_SOURCE_PATH,
                 reference.MISSING_WEIGHTS_PATH,
                 reference.LABEL_SET_PATH,
                 reference.TARGET_VOICE_CONSENT_PATH,
                 reference.COHORT_MANIFEST_PATH,
                 reference.PARITY_MANIFEST_PATH,
                 reference.RIGHTS_RECORD_PATH):
        expect(path in report.get("missing_historical_artifacts", []),
               "missing artifact not recorded: " + path)

    identity = report.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False,
           "task identity claims a whole-file hash")
    expect(identity.get("full_tasks_json_hashed") is False,
           "task identity claims a full-board hash")
    expect(identity.get("source") == reference.TASK_BOARD_REL,
           "task identity source mismatch")
    expect(set(identity.get("excluded_mutable_fields", []))
           == set(reference.MUTABLE_TASK_FIELDS),
           "mutable field exclusion mismatch")
    expect(report.get("board_row") == identity,
           "board_row differs from task_row_identity")
    expect(report.get("source_pins") == reference.SOURCE_PINS,
           "report source pins differ")
    expect(report.get("boundary_pins") == reference.BOUNDARY_PINS,
           "report boundary pins differ")

    candidate = report.get("candidate", {})
    expect(candidate.get("record_status") == "unavailable/blocked",
           "candidate record status mismatch")
    expect(candidate.get("candidate_kind") == "unnamed_model_family",
           "candidate kind mismatch")
    expect(candidate.get("source_present") is False,
           "candidate claims a source")
    expect(candidate.get("source_revision") is None,
           "fabricated candidate revision")
    expect(candidate.get("source_sha256") is None,
           "fabricated candidate source digest")
    expect(candidate.get("weights_present") is False,
           "candidate claims weights")
    expect(candidate.get("weights_sha256") is None,
           "fabricated candidate weight digest")
    expect(candidate.get("runtime_present") is False,
           "candidate claims a runtime")
    expect(candidate.get("target_emotion_labels_present") is False,
           "candidate claims labels")
    expect(candidate.get("consent_cleared_target_voices_present") is False,
           "candidate claims consent")
    expect(candidate.get("geometry_documented") is False,
           "candidate claims geometry")
    expect(candidate.get("implemented_here") is False,
           "candidate claims implementation")
    expect(candidate.get("adapter_present") is False,
           "candidate claims an adapter")
    expect(candidate.get("exact_numeric_output_present") is False,
           "candidate claims numeric output")
    expect(report.get("format", {}).get("candidate_geometry_asserted") is False,
           "format asserts candidate geometry")
    expect(report.get("format", {}).get("target_emotion_labels_present")
           is False, "format claims target labels")

    profile = report.get("voice_profile", {})
    expect(profile.get("name") == "voice", "voice profile name mismatch")
    expect(profile.get("satisfied_for_qualification") == [],
           "voice profile claims a qualified item")
    expect(profile.get("real_model_metrics") is None,
           "voice profile has real-model metrics")
    expect(len(profile.get("required_items", []))
           == len(reference.VOICE_REQUIREMENTS),
           "voice requirement count mismatch")
    expect(all(item.get("qualification_effect") == "none"
               and item.get("satisfied_for_qualification") is False
               for item in profile.get("required_items", [])),
           "a voice requirement has qualification effect")

    protocol = report.get("reference_protocol", {})
    expect(protocol.get("model_executed") is False,
           "reference protocol claims model execution")
    expect(protocol.get("executor") == "absent",
           "reference protocol executor is not absent")
    expect(protocol.get("plan_source") == reference.CONTROL_PLAN_PROVENANCE,
           "plan source is not the labelled control")
    expect(protocol.get("qualification_effect") == "none",
           "reference protocol has a qualification effect")
    baseline = protocol.get("identity_baseline", {})
    expect(baseline.get("baseline") == reference.COMPARISON_BASELINE,
           "identity baseline label mismatch")
    expect(baseline.get("transformation_performed") is False,
           "identity baseline claims transformation")
    for key in ("sample_count_equal", "duration_equal", "digest_equal",
                "peak_bounded"):
        expect(baseline.get(key) is True, "identity baseline not true: " + key)
    expect(baseline.get("content_delay_samples") == 0,
           "identity baseline delay mismatch")
    expect(baseline.get("qualification_effect") == "none",
           "identity baseline has qualification effect")
    admission = protocol.get("target_condition_admission", {})
    expect(admission.get("identity_control_accepted") is True,
           "identity target not admitted")
    expect(admission.get("nonidentity_rejected") is True,
           "nonidentity target not rejected")
    expect(admission.get("accepted_labels") == ["identity"],
           "accepted label list mismatch")
    expect(admission.get("transformation_performed") is False,
           "target admission claims transformation")
    expect(admission.get("qualification_effect") == "none",
           "target admission has qualification effect")
    expect(protocol.get("alignment", {}).get("streaming_supported") is False,
           "reference protocol claims streaming")
    expect(protocol.get("alignment", {}).get("mode")
           == "offline_whole_utterance", "reference protocol mode mismatch")
    expect(protocol.get("alignment", {}).get("measured") is False,
           "reference protocol claims timing")
    expect(protocol.get("duration", {}).get("duration_ratio") == "1",
           "identity duration accounting mismatch")
    expect(protocol.get("duration", {}).get("sample_delta") == 0,
           "identity sample delta mismatch")
    expect(protocol.get("geometry", {}).get(
        "candidate_geometry_asserted") is False,
        "reference protocol asserts candidate geometry")
    expect(len(protocol.get("acceptance_outcomes", [])) == 5,
           "acceptance outcome count mismatch")
    expect(all(item.get("measured") is False
               and item.get("value") is None
               for item in protocol.get("acceptance_outcomes", [])),
           "an acceptance outcome claims a measurement")

    controls = report.get("controls", {})
    for key in ("adverse_all_rejected", "nonfinite_rejected",
                "missing_asset_rejected_before_processing",
                "missing_result_never_qualifies",
                "offline_streaming_separation_declared",
                "identity_baseline_exact",
                "nonidentity_target_rejected_before_processing",
                "absence_probes_all_absent"):
        expect(controls.get(key) is True, "control not true: " + key)
    adverse = controls.get("adverse", [])
    expect(len(adverse) == len(reference.ADVERSE_CASE_IDS),
           "adverse control count mismatch")
    expect([item.get("case") for item in adverse]
           == list(reference.ADVERSE_CASE_IDS),
           "adverse case IDs mismatch")
    expect(all(item.get("result") == "rejected" for item in adverse),
           "an adverse control was accepted")

    audit = report.get("asset_audit", {})
    expect(audit.get("qualified") is False, "asset audit claims qualification")
    expect(audit.get("audit_result") == "absent",
           "asset audit result mismatch")
    for key in ("source_present", "license_present", "weights_present",
                "emotion_label_set_present",
                "target_voice_consent_present", "runtime_env_present",
                "runtime_lock_present", "rights_record_present",
                "cohort_manifest_present", "parity_manifest_present",
                "reference_audio_present"):
        expect(audit.get(key) is False, "asset audit claims " + key)
    expect(audit.get("source_revision") is None,
           "asset audit claims a source revision")
    expect(audit.get("all_absence_probes_absent") is True,
           "asset audit has a present absence probe")

    requirements = {item.get("id"): item
                    for item in report.get("asset_requirements", [])}
    expect(set(requirements) == {
        "source_checkout", "model_checkpoint", "model_config",
        "target_emotion_label_set", "style_conditioning_asset",
        "target_voice_reference_and_consent", "exact_runtime",
        "rights_record", "voice_cohort", "parity_vector"},
        "asset requirement IDs differ")
    for key in ("model_checkpoint", "model_config",
                "target_emotion_label_set", "style_conditioning_asset",
                "target_voice_reference_and_consent"):
        expect(requirements.get(key, {}).get("sha256") is None,
               "fabricated asset digest: " + key)
    expect(requirements.get("model_checkpoint", {}).get("byte_count") is None,
           "fabricated checkpoint byte count")
    expect(requirements.get("source_checkout", {}).get("revision") is None,
           "fabricated source revision")
    expect(requirements.get("exact_runtime", {}).get("runtime_lock_sha256")
           is None, "fabricated runtime lock digest")

    caller = report.get("caller_asset_contract", {})
    expect(caller.get("absent_behavior") == "reject_before_processing",
           "caller asset absent behavior mismatch")
    expect(caller.get("asset_is_vendored") is False,
           "caller asset is marked vendored")
    expect(caller.get("required_source_revision") is None,
           "caller revision is fabricated")
    expect(caller.get("revision_pin_available") is False,
           "caller revision claims a pin")
    expect(caller.get("required_variant") == reference.CALLER_VARIANT,
           "caller variant pin mismatch")
    expect(caller.get("required_task_kind") == reference.TASK_KIND,
           "caller task kind mismatch")
    expect(caller.get("required_comparison_baseline")
           == reference.COMPARISON_BASELINE,
           "caller baseline mismatch")

    licensing = report.get("licensing", {})
    expect(licensing.get("package_license") == "Apache-2.0",
           "package licence mismatch")
    expect(licensing.get("review_status") == "blocked",
           "licensing review is not blocked")
    for key in ("license_text_staged", "weights_terms_staged",
                "training_data_statement_staged",
                "target_voice_consent_staged", "output_use_reviewed",
                "redistribution_reviewed", "product_use_reviewed",
                "corpus_rights_reviewed"):
        expect(licensing.get(key) is False, "licensing claims " + key)

    expect(report.get("determinism", {}).get(
        "cold_start_regenerations_required") == 3,
        "cold-start requirement is not three")

    try:
        reference.canonical_text(report)
    except reference.ReferenceRejection as error:
        expect(False, "report is not canonical (float/type): " + str(error))
    encoded = reference.canonical_text(report)
    if re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', encoded):
        expect(False, "report contains a whole-file TASKS.json digest")
    return ok


def check_contract(contract: Dict[str, Any] | None,
                   report: Dict[str, Any] | None,
                   errors: List[str]) -> bool:
    if contract is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, message, errors) and ok

    expect(contract.get("SPDX-FileCopyrightText")
           == "2026 Tsakanyan Hovhannes", "contract SPDX copyright missing")
    expect(contract.get("SPDX-License-Identifier") == "Apache-2.0",
           "contract SPDX license missing")
    expect(contract.get("task") == reference.TASK_ID, "contract task mismatch")
    expect(contract.get("component") == reference.COMPONENT,
           "contract component mismatch")
    expect(contract.get("repository") == "audio-sdk",
           "contract repository mismatch")
    expect(contract.get("mode") == reference.MODE, "contract mode mismatch")
    expect(contract.get("profile") == "voice", "contract profile mismatch")
    expect(contract.get("status") == "proposal_only_incomplete",
           "contract status mismatch")
    expect(contract.get("decision") == "DEFER", "contract decision mismatch")
    expect(contract.get("evidence_status") == "incomplete",
           "contract evidence status mismatch")
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
    expect(len(contract.get("exact_blockers", [])) == 8,
           "contract blocker count is not eight")
    expect(all(item.get("state") == "absent"
               for item in contract.get("exact_blockers", [])),
           "contract has a non-absent blocker")
    expect(contract.get("reproduction", {}).get(
        "cold_start_regenerations") == 3,
        "contract cold-start count is not three")
    expect(contract.get("task_row_identity", {}).get(
        "whole_file_hashed") is False,
        "contract task identity claims a whole-file hash")
    expect(contract.get("candidate", {}).get("source_revision") is None,
           "contract fabricates a source revision")
    expect(contract.get("caller_asset_contract", {}).get(
        "revision_pin_available") is False,
        "contract claims a caller revision pin")
    expect(isinstance(contract.get("invariants"), list)
           and len(contract["invariants"]) >= 8,
           "contract invariants missing")
    expect(any("DEFER" in item for item in contract.get("invariants", [])),
           "contract invariant does not mention DEFER")

    if report is not None:
        for key in ("board_row", "task_row_identity", "source_pins",
                    "boundary_pins", "gates", "release_gates",
                    "exact_blockers", "qualification", "format", "boundary",
                    "scope", "candidate", "voice_profile",
                    "reference_protocol"):
            expect(contract.get(key) == report.get(key),
                   "contract/report mismatch: " + key)
        expect(contract.get("task_row_identity", {}).get("stable_sha256")
               == report.get("task_row_identity", {}).get("stable_sha256"),
               "contract/report stable digest mismatch")

    artifact_pins = contract.get("artifact_pins", {})
    expect(isinstance(artifact_pins, dict) and bool(artifact_pins),
           "artifact pins missing")
    report_digest = None
    sidecar_digest = None
    if REPORT.is_file():
        report_digest = sha256(REPORT.read_bytes())
    if SIDECAR.is_file():
        sidecar_digest = sha256(SIDECAR.read_bytes())
    for name in reference.ARTIFACT_FILES:
        key = TASK_PREFIX + name
        if key not in artifact_pins:
            expect(False, "artifact pin missing: " + name)
            continue
        value = artifact_pins[key]
        expect(isinstance(value, str) and bool(re.fullmatch(
            r"[0-9a-f]{64}", value)), "bad artifact pin digest: " + name)
        if name == "report.json":
            expect(value == report_digest, "report.json pin is stale")
        elif name == "report.json.sha256":
            expect(value == sidecar_digest, "report.json.sha256 pin is stale")
        else:
            target = HERE / name
            if not target.is_file():
                expect(False, "artifact pin target missing: " + name)
            else:
                expect(value == sha256(target.read_bytes()),
                       "artifact pin is stale: " + name)
    expect(TASK_PREFIX + "contract.json" not in artifact_pins,
           "contract pins itself")
    return ok


def check_task_row_identity(report: Dict[str, Any],
                            contract: Dict[str, Any],
                            errors: List[str]) -> bool:
    path = SOURCE_ROOT / reference.TASK_BOARD_REL
    if not path.is_file():
        errors.append("task board unavailable for identity check")
        return False
    try:
        document = reference.require_json_object(
            reference.load_strict_json(path))
    except Exception as error:
        errors.append("task board strict JSON failed: " + str(error))
        return False
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == reference.TASK_ID]
    if len(rows) != 1:
        errors.append("expected exactly one linked task row")
        return False
    row = rows[0]
    stable = {field: row.get(field)
              for field in reference.STABLE_TASK_FIELDS}
    digest = sha256(reference.canonical_text(stable).encode("utf-8"))
    ok = True
    ok = _expect(report.get("task_row_identity", {}).get("stable_sha256")
                 == digest, "report task identity digest is stale", errors) and ok
    ok = _expect(contract.get("task_row_identity", {}).get("stable_sha256")
                 == digest, "contract task identity digest is stale", errors) and ok
    ok = _expect(report.get("task_row_identity", {}).get("stable_fields")
                 == stable, "report stable fields differ from the board",
                 errors) and ok
    claim = row.get("claim") or {}
    for field, expected in (("base_commit", reference.BASE_COMMIT),
                            ("branch", reference.BRANCH),
                            ("worktree", reference.CLAIM_WORKTREE),
                            ("reviewer", reference.REVIEWER)):
        ok = _expect(claim.get(field) == expected,
                     "board claim " + field + " differs", errors) and ok
    for text, label in ((report, "report"), (contract, "contract")):
        encoded = reference.canonical_text(text)
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
    for key, message in (
            ("source_checkout_present",
             "a source checkout appeared; re-evaluate the blocker"),
            ("license_file_present",
             "a licence appeared; re-evaluate the rights blocker"),
            ("weights_present",
             "weights appeared; re-evaluate the blocker"),
            ("emotion_label_set_present",
             "an emotion label set appeared; re-evaluate the blocker"),
            ("target_voice_consent_present",
             "target-voice consent appeared; re-evaluate the blocker"),
            ("runtime_env_present",
             "a runtime environment appeared; re-evaluate the blocker"),
            ("runtime_lock_present",
             "a runtime lock appeared; re-evaluate the blocker"),
            ("rights_record_present",
             "a rights record appeared; re-evaluate the blocker"),
            ("cohort_manifest_present",
             "a cohort appeared; re-evaluate the blocker"),
            ("parity_manifest_present",
             "a parity vector appeared; re-evaluate the blocker"),
            ("reference_audio_present",
             "reference audio appeared; re-evaluate the blocker")):
        ok = _expect(live[key] is False, message, errors) and ok
    ok = _expect(live["source_revision"] is None,
                 "a source revision appeared; re-evaluate the blocker",
                 errors) and ok
    ok = _expect(live["all_absence_probes_absent"] is True,
                 "an absence probe is present; re-evaluate the blocker",
                 errors) and ok
    return ok


def check_control(report: Dict[str, Any], errors: List[str]) -> bool:
    control = reference.build_control()
    ok = True
    ok = _expect(control["identity_baseline"]["digest_equal"] is True,
                 "identity baseline digest differs", errors) and ok
    ok = _expect(control["identity_baseline"]["sample_count_equal"] is True,
                 "identity baseline sample count differs", errors) and ok
    ok = _expect(control["target_condition_admission"][
        "nonidentity_rejected"] is True,
        "nonidentity target was admitted", errors) and ok
    ok = _expect(all(item["result"] == "rejected"
                     for item in control["adverse"]),
                 "an adverse control was accepted", errors) and ok
    ok = _expect(len(control["adverse"]) == len(reference.ADVERSE_CASE_IDS),
                 "adverse control count mismatch", errors) and ok
    ok = _expect(control["qualification_effect"] == "none",
                 "control has a qualification effect", errors) and ok
    return ok


def check_sources_reproduction(errors: List[str]) -> bool:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True,
        check=False)
    if result.returncode != 0:
        errors.append(
            "package is not reproducible: "
            + (result.stderr.strip() or result.stdout.strip()))
        return False
    return True


def check_reproduction(errors: List[str]) -> Tuple[bool, str, List[str]]:
    expected = reference.canonical_report(reference.build_report())[0].encode(
        "utf-8")
    digest = sha256(expected)
    ok = REPORT.is_file() and REPORT.read_bytes() == expected
    if not ok:
        errors.append("report.json is not byte-reproducible")
    sidecar = (digest + "\n").encode("utf-8")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar:
        errors.append("report.json.sha256 mismatch")
        ok = False
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    repeats: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="emotion-prosody-verify-", dir=root))
        try:
            for index in range(3):
                target = work / f"cold-{index}"
                shutil.copytree(HERE, target)
                environment = dict(
                    os.environ, PYTHONDONTWRITEBYTECODE="1",
                    SDK_ROOT=str(SDK), SOURCE_ROOT=str(SOURCE_ROOT))
                result = subprocess.run(
                    [sys.executable, str(target / "run.py")],
                    cwd=str(target), env=environment, capture_output=True,
                    text=True, check=False)
                generated = target / "report.json"
                generated_sidecar = target / "report.json.sha256"
                if result.returncode != 0 or not generated.is_file():
                    errors.append(
                        f"cold regeneration {index} failed: "
                        + (result.stderr.strip() or result.stdout.strip()))
                    ok = False
                    continue
                data = generated.read_bytes()
                repeats.append(sha256(data))
                if data != expected:
                    errors.append(
                        f"cold regeneration {index} is not byte-identical")
                    ok = False
                if (not generated_sidecar.is_file()
                        or generated_sidecar.read_bytes() != sidecar):
                    errors.append(
                        f"cold regeneration {index} sidecar differs")
                    ok = False
                for name in ("contract.json", "SOURCES.sha256"):
                    if (not (target / name).is_file()
                            or (target / name).read_bytes()
                            != (HERE / name).read_bytes()):
                        errors.append(
                            f"cold regeneration {index} differs: {name}")
                        ok = False
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except OSError as error:
        errors.append("cold regeneration scratch unavailable: " + str(error))
        ok = False
    return ok, digest, repeats


def check_licensing(errors: List[str]) -> bool:
    copyright_line = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"
    license_line = "SPDX-" + "License-Identifier: Apache-2.0"
    ok = True
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if path.suffix in (".py", ".md"):
            head = "\n".join(
                path.read_text(encoding="utf-8").splitlines()[:6])
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
    for name in ("SOURCES.sha256.license",):
        path = HERE / name
        if not path.is_file():
            errors.append("missing SPDX sidecar: " + name)
            ok = False
        else:
            text = path.read_text(encoding="utf-8")
            if copyright_line not in text or license_line not in text:
                errors.append("invalid SPDX sidecar: " + name)
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
        capture_output=True, text=True, check=True)
    ok = True
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            errors.append("out of scope change: " + path)
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
        check_contract(contract, report, errors)
        if contract is not None else False)
    identity_ok = (
        check_task_row_identity(report, contract, errors)
        if report is not None and contract is not None else False)
    assets_ok = check_assets(report, errors) if report is not None else False
    control_ok = check_control(report, errors) if report is not None else False
    licensing_ok = check_licensing(errors)
    sources_ok = check_sources_reproduction(errors)
    reproduction_ok, digest, repeats = check_reproduction(errors)
    scope_ok = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(
            f"FAILED pins={verified}/{len(pins)} json_ok={json_ok} "
            f"report_ok={report_ok} contract_ok={contract_ok} "
            f"identity_ok={identity_ok} assets_ok={assets_ok} "
            f"control_ok={control_ok} licensing_ok={licensing_ok} "
            f"sources_ok={sources_ok} scope_ok={scope_ok} "
            f"reproduction_ok={reproduction_ok} report_sha256={digest} "
            f"decision={reference.DECISION}")
        return 1
    print(
        f"PASS pins={verified}/{len(pins)} json_ok={json_ok} "
        f"report_ok={report_ok} contract_ok={contract_ok} "
        f"identity_ok={identity_ok} assets_ok={assets_ok} "
        f"control_ok={control_ok} licensing_ok={licensing_ok} "
        f"sources_ok={sources_ok} scope_ok={scope_ok} "
        f"reproduction_ok={reproduction_ok} gates=8 blockers=8 "
        f"cold_starts={len(repeats)}/3 report_sha256={digest} "
        f"decision={reference.DECISION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
