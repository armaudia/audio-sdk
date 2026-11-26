#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local evidence package."""

from __future__ import annotations

import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
TASK_PREFIX = reference.TASK_PREFIX
PIN_LINE = re.compile(
    r"^([0-9a-f]{64})  ((?:pkg|source|worktree):[A-Za-z0-9_./-]+)$")
SPDX_COPYRIGHT = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"


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
README = HERE / "README.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _expect(condition: bool, message: str, errors: List[str]) -> bool:
    if not condition:
        errors.append(message)
    return condition


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
        and path.name not in ("SOURCES.sha256",)
        and not path.name.endswith(".pyc")
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
        return reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        errors.append(f"strict json failed for {path.name}: {error}")
        return None


def _finite(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(float(value)))


def check_report(report: Dict[str, Any] | None,
                 errors: List[str]) -> bool:
    if report is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, message, errors) and ok

    expect(report.get("schema_id") == reference.REPORT_SCHEMA_ID,
           "report schema_id mismatch")
    expect(report.get("task_id") == reference.TASK, "task_id mismatch")
    expect(report.get("component") == reference.COMPONENT,
           "component mismatch")
    expect(report.get("title") == reference.TITLE, "title mismatch")
    expect(report.get("profile") == "dsp", "profile is not dsp")
    expect(report.get("status") == "proposal_only_incomplete",
           "status mismatch")
    expect(report.get("evidence_status") == "incomplete",
           "evidence_status mismatch")
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
    expect(qualification.get("defer_before") == "opt_in_adapter_exposure",
           "nested defer boundary mismatch")
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
                "network_used", "native_engine_built", "processor_exposure",
                "adapter_json_added", "readiness_json_added",
                "sdk_data_dir_added"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    expect(boundary.get("descriptor_settings") == {},
           "descriptor settings are not empty")

    scope = report.get("scope", {})
    for key in ("real_audio", "real_corpus", "real_weights",
                "real_device_response", "model_executed", "runtime_imported",
                "weights_downloaded", "network_used", "device_timing",
                "listening", "public_benchmark", "release_claim"):
        expect(scope.get(key) is False, "scope flag not false: " + key)
    expect(scope.get("task_local_only") is True,
           "task_local_only is not true")

    gates = report.get("gates", [])
    expected_gates = [name for name, _ in reference.GATE_REQUIREMENTS]
    expect([gate.get("id") for gate in gates] == expected_gates,
           "gate IDs or order mismatch")
    expect(expected_gates == [f"RG-0{index}" for index in range(1, 9)],
           "gate IDs are not RG-01..RG-08")
    expect(len(gates) == 8, "gate count is not eight")
    expect(all(gate.get("status") == "blocked" for gate in gates),
           "a gate is not blocked")
    expect(all(isinstance(gate.get("requirement"), str)
               and bool(gate["requirement"].strip()) for gate in gates),
           "gate requirement missing")

    blockers = report.get("exact_blockers", [])
    expected_blockers = [item["id"] for item in reference.EXACT_BLOCKERS]
    expect([item.get("id") for item in blockers] == expected_blockers,
           "blocker IDs or order mismatch")
    expect(len(blockers) == 8, "exact blocker count is not eight")
    expect(all(isinstance(item.get("state"), str)
               and bool(item["state"].strip()) for item in blockers),
           "blocker state missing")
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
    for key in ("dafx_2020_neural_parametric_eq",
                "dafx_2025_neural_multiband",
                "synthetic_inverse_eq_screen"):
        expect(context.get(key, {}).get("usable_as_candidate_metric") is False,
               f"{key} is marked usable as a candidate metric")
    expect(len(report.get("missing_historical_artifacts", [])) >= 1,
           "missing historical artifacts are not recorded")

    identity = report.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False,
           "task identity claims a whole-file hash")
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

    profile = report.get("dsp_profile", {})
    expect(profile.get("name") == "dsp", "dsp profile name mismatch")
    expect(profile.get("satisfied_for_qualification") == [],
           "dsp profile claims a qualified item")
    expect(profile.get("real_model_metrics") is None,
           "dsp profile has real-model metrics")
    expect(len(profile.get("required_items", []))
           == len(reference.DSP_REQUIREMENTS),
           "dsp requirement count mismatch")
    expect(all(item.get("qualification_effect") == "none"
               and item.get("satisfied_for_qualification") is False
               for item in profile.get("required_items", [])),
           "a dsp requirement has qualification effect")
    expect("device" in profile.get("plan_note", "")
           and "speaker" in profile.get("plan_note", "")
           and "gain" in profile.get("plan_note", ""),
           "dsp plan note does not state device/speaker/gain constraints")

    protocol = report.get("reference_protocol", {})
    expect(protocol.get("model_executed") is False,
           "reference protocol claims model execution")
    expect(protocol.get("executor") == "absent",
           "reference protocol executor is not absent")
    expect(protocol.get("surrogate") is True,
           "reference protocol is not labelled synthetic")
    expect(protocol.get("qualification_effect") == "none",
           "reference protocol has a qualification effect")
    expect(protocol.get("device_recovery_before_real_speech") is True,
           "device recovery ordering is missing")
    availability = protocol.get("availability", {})
    expect(availability.get("buffering_delay_samples") == 0,
           "surrogate buffering delay is not zero")
    expect(availability.get("candidate_delay_measured") is False,
           "candidate delay is claimed measured")
    expect(availability.get("synthetic_control_is_not_model_latency") is True,
           "synthetic control is presented as model latency")

    control = protocol.get("synthetic_control", {})
    expect(control.get("label") == reference.SURROGATE_LABEL,
           "surrogate label mismatch")
    expect(control.get("qualification_effect") == "none",
           "surrogate has a qualification effect")
    expect(control.get("candidate_model_executed") is False,
           "surrogate claims candidate execution")
    gradient = control.get("gradient_check", {})
    expect(gradient.get("passes") is True, "gradient check did not pass")
    expect(_finite(gradient.get("max_abs_difference"))
           and gradient["max_abs_difference"] < 1e-4,
           "gradient check error is not below 1e-4")
    exact = control.get("exact_recovery", {})
    expect(exact.get("qualifies") is False, "exact recovery qualifies")
    expect(_finite(exact.get("final_rmse_db"))
           and exact["final_rmse_db"] < 1e-4,
           "exact recovery did not converge")
    expect(_finite(exact.get("max_abs_gain_error_db"))
           and exact["max_abs_gain_error_db"] < 1e-3,
           "exact recovery gain error too large")
    device = control.get("device_recovery", {})
    expect(device.get("qualifies") is False, "device recovery qualifies")
    expect(device.get("split_label")
           == "synthetic_frequency_holdout_not_device_or_speaker_split",
           "device recovery split is mislabelled")
    expect(_finite(device.get("train_rmse_db"))
           and device["train_rmse_db"] > 0.0,
           "device train RMSE missing")
    expect(_finite(device.get("heldout_rmse_db"))
           and device["heldout_rmse_db"] > 0.0,
           "device held-out RMSE missing")
    expect(all(abs(value) <= device.get("gain_limit_db", 0)
               for value in device.get("gains_db", [])),
           "device gains exceed the declared limit")
    rejections = control.get("rejections", {})
    expect(rejections.get("all_rejected") is True,
           "adverse DSP inputs are not all rejected")
    expect(rejections.get("count") == 12,
           "DSP rejection case count is not twelve")
    measurements = control.get("dsp_measurements", {})
    for key in ("sweep", "step", "impulse", "silence",
                "clean_speech_surrogate", "frame_vs_whole", "reset",
                "headroom", "nonlinear_interaction"):
        expect(key in measurements, "missing DSP measurement: " + key)
    expect(measurements.get("sweep", {}).get("finite") is True,
           "sweep output is not finite")
    expect(measurements.get("impulse", {}).get("delay_samples") == 0,
           "impulse delay is not zero")
    expect(measurements.get("silence", {}).get("all_zero") is True,
           "silence is not all zero")
    expect(measurements.get("frame_vs_whole", {}).get("identical") is True,
           "frame and whole processing differ")
    expect(measurements.get("reset", {}).get("isolated") is True,
           "reset is not isolated")
    expect(measurements.get("nonlinear_interaction", {}).get("finite") is True,
           "nonlinear interaction is not finite")
    expect(measurements.get("nonlinear_interaction", {}).get(
        "bounded_by_one") is True,
        "nonlinear interaction exceeds the bounded output")
    adverse = control.get("adverse", [])
    expect(len(adverse) == 4, "adverse control count is not four")
    expect(all(item.get("qualifies") is False for item in adverse),
           "an adverse control claims qualification")
    expect(control.get("gain_limits", {}).get("enforced") is True,
           "gain limits are not enforced")

    admission = report.get("admission_controls", {})
    expect(admission.get("adverse_count") == 60,
           "adverse control count is not 60")
    expect(admission.get("adverse_all_rejected") is True,
           "adverse controls are not all rejected")
    expect(all(item.get("result") == "rejected"
               for item in admission.get("adverse", [])),
           "an adverse control was accepted")
    expect(admission.get("strict_json_all_rejected") is True,
           "strict JSON adverse controls are not all rejected")
    positive = admission.get("positive_control", {})
    expect(positive.get("accepted") is True and
           positive.get("qualifies") is False,
           "positive schema control is missing or claims qualification")
    expect(positive.get("label") == "synthetic_schema_control_not_evidence",
           "positive schema control is not labelled")
    expect(positive.get("executed") is False,
           "positive schema control claims execution")
    expect(positive.get("upstream_identity_verified") is False,
           "positive schema control claims upstream identity")

    controls = report.get("controls", {})
    expect(controls.get("missing_result_never_qualifies") is True,
           "missing-result control missing")
    expect(controls.get("nonfinite_never_counted_as_valid") is True,
           "nonfinite control missing")
    expect(controls.get("synthetic_control_never_qualifies") is True,
           "synthetic-control separation missing")
    expect(controls.get("real_device_or_speaker_split_present") is False,
           "real device or speaker split is claimed present")

    audit = report.get("asset_audit", {})
    expect(audit.get("qualified") is False, "asset audit claims qualification")
    expect(audit.get("audit_result") == "absent",
           "asset audit is not absent")
    expect(audit.get("any_present") is False,
           "asset audit observes a present artifact")

    requirements = report.get("candidate_requirements", [])
    expect(len(requirements) == 8, "candidate requirement count is not eight")
    expect(all(item.get("state") == "absent"
               for item in requirements),
           "a candidate requirement claims presence")

    schema = report.get("admission_schema", {})
    expect(schema.get("accepted_manifest_qualifies") is False,
           "admission schema claims a manifest qualifies")
    expect(schema.get("executed_in_this_package") is False,
           "admission schema claims execution")
    expect(schema.get("upstream_identity_verified") is False,
           "admission schema claims upstream identity")
    expect(set(schema.get("required_fields", []))
           == set(reference.ADMISSION_FIELDS),
           "admission schema field set differs")
    expect(report.get("determinism", {}).get(
        "cold_start_regenerations_required") == 3,
        "cold-start requirement is not three")
    return ok


def check_contract(contract: Dict[str, Any] | None,
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
    expect(contract.get("task") == reference.TASK, "contract task mismatch")
    expect(contract.get("component") == reference.COMPONENT,
           "contract component mismatch")
    expect(contract.get("repository") == "audio-sdk",
           "contract repository mismatch")
    expect(contract.get("mode") == "feasibility", "contract mode mismatch")
    expect(contract.get("profile") == "dsp", "contract profile mismatch")
    expect(contract.get("status") == "proposal_only_incomplete",
           "contract status mismatch")
    expect(contract.get("evidence_status") == "incomplete",
           "contract evidence_status mismatch")
    expect(contract.get("decision") == "DEFER", "contract decision mismatch")
    expect(contract.get("defer_before") == "opt_in_adapter_exposure",
           "contract defer boundary mismatch")
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
    boundary = contract.get("boundary", {})
    expect(boundary.get("registered") is False, "contract is registered")
    expect(boundary.get("enabled_by_default") is False,
           "contract is enabled by default")
    expect(boundary.get("descriptor_settings") == {},
           "contract descriptor settings are not empty")
    expect(len(contract.get("gates", [])) == 8,
           "contract gate count is not eight")
    expect(all(gate.get("status") == "blocked"
               for gate in contract.get("gates", [])),
           "contract has a non-blocked gate")
    expect(len(contract.get("exact_blockers", [])) == 8,
           "contract blocker count is not eight")
    expect(contract.get("reproduction", {}).get(
        "cold_start_regenerations") == 3,
        "contract cold-start count is not three")
    expect(contract.get("reproduction", {}).get("byte_identical_required")
           is True, "contract does not require byte identity")
    expect(contract.get("task_row_identity", {}).get(
        "whole_file_hashed") is False,
        "contract task identity claims a whole-file hash")
    expect(contract.get("admission_schema", {}).get(
        "accepted_manifest_qualifies") is False,
        "contract admission schema claims qualification")
    surrogate = contract.get("surrogate_protocol", {})
    expect(surrogate.get("qualification_effect") == "none",
           "contract surrogate has a qualification effect")
    expect(surrogate.get("model_executed") is False,
           "contract surrogate claims execution")
    expect(surrogate.get("real_device_or_speaker_split") is False,
           "contract surrogate claims a real split")
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
    observed = audit.get("observations")
    live = reference.audit_assets()
    if observed != live["observations"]:
        errors.append("asset audit observation is stale")
        return False
    ok = True
    for key in ("any_present", "implementation_present", "weights_present",
                "runtime_present", "cohort_present", "frozen_run_present",
                "rights_present"):
        ok = _expect(live[key] is False,
                     f"artifact appeared ({key}); re-evaluate the blocker",
                     errors) and ok
    return ok


def check_report_digest(report: Dict[str, Any],
                        contract: Dict[str, Any],
                        errors: List[str]) -> bool:
    ok = True
    raw = REPORT.read_bytes()
    canonical, digest = reference.canonical_report(report)
    ok = _expect(raw == canonical.encode("utf-8"),
                 "report.json is not canonical JSON", errors) and ok
    if not SIDECAR.is_file():
        errors.append("report.json.sha256 missing")
        ok = False
    else:
        sidecar = SIDECAR.read_text(encoding="ascii").strip()
        ok = _expect(sidecar == digest,
                     "report.json.sha256 digest mismatch", errors) and ok
    ok = _expect(contract.get("reproduction", {}).get("report_sha256")
                 == digest,
                 "contract report digest mismatch", errors) and ok
    return ok


def check_sources_reproduction(errors: List[str]) -> bool:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True,
        check=False)
    if result.returncode != 0:
        errors.append(
            "committed artifacts are not reproducible: "
            + (result.stderr.strip() or result.stdout.strip()))
        return False
    return True


def check_cold_reproduction(errors: List[str]) -> Tuple[bool, List[str]]:
    expected = {
        name: (HERE / name).read_bytes()
        for name in ("report.json", "report.json.sha256", "contract.json",
                     "SOURCES.sha256")
    }
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    digests: List[str] = []
    ok = True
    try:
        work = Path(tempfile.mkdtemp(prefix="dbq-verify-", dir=root))
        try:
            for index in range(3):
                target = work / f"cold-{index}"
                environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
                result = subprocess.run(
                    [sys.executable, str(HERE / "run.py"), "--out", str(target)],
                    cwd=str(HERE), env=environment, capture_output=True,
                    text=True, check=False)
                if result.returncode != 0:
                    errors.append(
                        f"cold regeneration {index} failed: "
                        + (result.stderr.strip() or result.stdout.strip()))
                    ok = False
                    continue
                for name, data in expected.items():
                    generated = target / name
                    if not generated.is_file() or generated.read_bytes() != data:
                        errors.append(
                            f"cold regeneration {index} differs: {name}")
                        ok = False
                digests.append(sha256((target / "report.json").read_bytes()))
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except OSError as error:
        errors.append("cold regeneration scratch unavailable: " + str(error))
        ok = False
    if len(set(digests)) != 1:
        errors.append("cold report digests are not identical")
        ok = False
    return ok, digests


def check_licensing(errors: List[str]) -> bool:
    ok = True
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if path.suffix in (".py", ".md"):
            head = "\n".join(
                path.read_text(encoding="utf-8").splitlines()[:6])
            if SPDX_COPYRIGHT not in head or SPDX_LICENSE not in head:
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
            if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
                errors.append("invalid SPDX sidecar: " + sidecar.name)
                ok = False
    for name in ("SOURCES.sha256.license",):
        path = HERE / name
        if not path.is_file():
            errors.append("missing SPDX sidecar: " + name)
            ok = False
        else:
            text = path.read_text(encoding="utf-8")
            if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
                errors.append("invalid SPDX sidecar: " + name)
                ok = False
    reuse = SDK / "REUSE.toml"
    if reuse.is_file():
        text = reuse.read_text(encoding="utf-8")
        if ('docs/**' not in text
                or 'SPDX-License-Identifier = "Apache-2.0"' not in text):
            errors.append("REUSE.toml does not cover docs/** as Apache-2.0")
            ok = False
    else:
        errors.append("REUSE.toml missing")
        ok = False
    return ok


def check_readme(report: Dict[str, Any], errors: List[str]) -> bool:
    try:
        text = README.read_text(encoding="utf-8")
    except OSError as error:
        errors.append("README missing: " + str(error))
        return False
    ok = True
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
                  "dsp", "differentiable", "biquad", "device", "speaker",
                  "gain", reference.BASE_COMMIT, reference.TASK):
        if token not in text:
            errors.append("README is missing token: " + token)
            ok = False
    for digest in (list(reference.SOURCE_PINS.values())
                   + list(reference.BOUNDARY_PINS.values())):
        if digest not in text:
            errors.append("README is missing pinned digest: " + digest)
            ok = False
    if report:
        for item in report.get("exact_blockers", []):
            if item["id"] not in text:
                errors.append("README is missing blocker: " + item["id"])
                ok = False
        for gate in report.get("gates", []):
            if gate["id"] not in text:
                errors.append("README is missing gate: " + gate["id"])
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
    diff_check = subprocess.run(
        ["git", "-C", str(SDK), "diff", "--check"],
        capture_output=True, text=True, check=False)
    if diff_check.returncode != 0:
        errors.append("git diff --check failed: "
                      + (diff_check.stdout.strip()
                         or diff_check.stderr.strip()))
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
    contract_ok = check_contract(contract, errors) if contract is not None else False
    identity_ok = (
        check_task_row_identity(report, contract, errors)
        if report is not None and contract is not None else False)
    digest_ok = (
        check_report_digest(report, contract, errors)
        if report is not None and contract is not None else False)
    assets_ok = check_assets(report, errors) if report is not None else False
    licensing_ok = check_licensing(errors)
    readme_ok = check_readme(report or {}, errors)
    sources_ok = check_sources_reproduction(errors)
    cold_ok, repeats = check_cold_reproduction(errors)
    scope_ok = check_scope(errors)
    digest = sha256(REPORT.read_bytes()) if REPORT.is_file() else "missing"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(
            f"verify_result=FAILED pins={verified}/{len(pins)} json_ok={json_ok} "
            f"report_ok={report_ok} contract_ok={contract_ok} "
            f"identity_ok={identity_ok} digest_ok={digest_ok} "
            f"assets_ok={assets_ok} licensing_ok={licensing_ok} "
            f"readme_ok={readme_ok} sources_ok={sources_ok} cold_ok={cold_ok} "
            f"scope_ok={scope_ok} cold_repeats={len(repeats)} "
            f"report_sha256={digest}")
        return 1
    print(
        f"verify_result=OK pins={verified}/{len(pins)} json_ok={json_ok} "
        f"report_ok={report_ok} contract_ok={contract_ok} "
        f"identity_ok={identity_ok} digest_ok={digest_ok} "
        f"assets_ok={assets_ok} licensing_ok={licensing_ok} "
        f"readme_ok={readme_ok} sources_ok={sources_ok} cold_ok={cold_ok} "
        f"scope_ok={scope_ok} cold_repeats={len(repeats)} "
        f"report_sha256={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
