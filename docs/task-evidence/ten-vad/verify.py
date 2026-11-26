#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local evidence package."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import reference

HERE = Path(__file__).resolve().parent
TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
TASK_PREFIX = "docs/task-evidence/ten-vad/"
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
            errors.append("SOURCES.sha256 must not pin the mutable full TASKS.json")
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
        path = {"pkg": HERE, "source": SOURCE_ROOT, "worktree": SDK}[prefix] / raw
        pins[label] = (digest, path)
    if not pins:
        errors.append("no pins found")
    authored = {
        path.name for path in HERE.iterdir()
        if path.is_file() and path.name not in ("SOURCES.sha256",)
        and not path.name.endswith(".pyc") and "__pycache__" not in path.name
    }
    for name in sorted(authored):
        if "pkg:" + name not in pins:
            errors.append("unpinned package file: " + name)
    return pins


def check_pin_targets(pins: Dict[str, Tuple[str, Path]], errors: List[str]) -> int:
    checked = 0
    for label, (digest, path) in sorted(pins.items()):
        if not path.is_file():
            errors.append("missing pin target: " + label)
            continue
        actual = sha256(path.read_bytes())
        if actual != digest:
            errors.append(f"pin mismatch: {label} expected={digest} actual={actual}")
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


def check_report(report: Dict[str, Any] | None, errors: List[str]) -> bool:
    if report is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, message, errors) and ok

    expect(report.get("task_id") == reference.TASK, "task_id mismatch")
    expect(report.get("component") == reference.COMPONENT, "component mismatch")
    expect(report.get("title") == reference.TITLE, "title mismatch")
    expect(report.get("profile") == "analysis", "profile is not analysis")
    expect(report.get("status") == "proposal_only_incomplete", "status mismatch")
    expect(report.get("evidence_status") == "incomplete", "evidence_status mismatch")
    expect(report.get("decision") == "DEFER", "decision is not DEFER")
    expect(report.get("defer_before") == "opt_in_adapter_exposure", "defer boundary mismatch")
    expect(report.get("qualification_status") == "not_qualified", "qualification_status mismatch")
    expect(report.get("base_commit") == reference.BASE_COMMIT, "base_commit mismatch")
    expect(report.get("branch") == reference.BRANCH, "branch mismatch")
    expect(report.get("worktree") == reference.CLAIM_WORKTREE, "worktree mismatch")
    expect(report.get("reviewer") == reference.REVIEWER, "reviewer mismatch")
    expect(report.get("format") == reference.FORMAT, "format mismatch")

    qualification = report.get("qualification", {})
    expect(qualification.get("status") == "not_qualified", "nested qualification is not not_qualified")
    expect(qualification.get("candidate_qualified") is False, "candidate_qualified is not false")
    expect(qualification.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing")
    expect(qualification.get("decision") == "DEFER", "nested decision is not DEFER")
    expect(qualification.get("blocked_gate_count") == 8, "blocked gate count is not eight")
    expect(isinstance(qualification.get("blocked_gate_ids"), list)
           and len(qualification["blocked_gate_ids"]) == 8, "blocked gate id list is not eight")
    expect(isinstance(qualification.get("reason"), str)
           and bool(qualification["reason"].strip()), "qualification reason missing")

    boundary = report.get("boundary", {})
    for key in ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "production_callback_registered", "descriptor_registry_change",
                "shared_build_or_ci_change", "installed_v0_behavior_change",
                "asset_bundled", "weights_vendored", "sdk_callback_invoked",
                "network_used", "adapter_json_added", "ci_change",
                "processor_exposure"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    expect(boundary.get("descriptor_settings") == {}, "descriptor settings are not empty")

    scope = report.get("scope", {})
    for key in ("real_audio", "real_corpus", "real_ten_vad_model",
                "model_executed", "weights_downloaded", "network_used",
                "device_timing", "listening", "public_benchmark", "release_claim"):
        expect(scope.get(key) is False, "scope flag not false: " + key)
    expect(scope.get("task_local_only") is True, "task_local_only is not true")

    gates = report.get("gates", [])
    expected_gates = [name for name, _ in reference.GATE_REQUIREMENTS]
    expect([gate.get("id") for gate in gates] == expected_gates, "gate IDs or order mismatch")
    expect(len(gates) == 8, "gate count is not eight")
    expect(all(gate.get("status") == "blocked" for gate in gates), "a gate is not blocked")
    expect(all(isinstance(gate.get("requirement"), str) and bool(gate["requirement"].strip())
               for gate in gates), "gate requirement missing")

    blockers = report.get("exact_blockers", [])
    expected_blockers = [item["id"] for item in reference.EXACT_BLOCKERS]
    expect([item.get("id") for item in blockers] == expected_blockers, "blocker IDs or order mismatch")
    expect(len(blockers) == 8, "exact blocker count is not eight")
    expect(all(isinstance(item.get("state"), str) and bool(item["state"].strip())
               for item in blockers), "blocker state missing")
    expect(qualification.get("blocked_gate_ids") == [gate["id"] for gate in gates],
           "nested blocked gate IDs differ from gates")

    expect(report.get("status") not in ("qualified", "complete", "passed"), "status claims completion")
    expect(report.get("candidate_metrics") is None, "candidate_metrics is not null")
    expect(report.get("source_reported_context", {}).get("label")
           == "source_reported_not_measured_here", "source-reported context is not labelled")

    identity = report.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False, "task identity claims a whole-file hash")
    expect(identity.get("source") == "audio-benchmark-platform/plan/swarm/TASKS.json",
           "task identity source mismatch")
    expect(set(identity.get("excluded_mutable_fields", [])) == set(reference.MUTABLE_TASK_FIELDS),
           "mutable field exclusion mismatch")
    expect(report.get("source_pins") == reference.SOURCE_PINS, "report source pins differ")
    expect(report.get("boundary_pins") == reference.BOUNDARY_PINS, "report boundary pins differ")

    profile = report.get("analysis_profile", {})
    expect(profile.get("name") == "analysis", "analysis profile name mismatch")
    expect(profile.get("satisfied_for_qualification") == [], "analysis profile claims a qualified item")
    expect(profile.get("real_model_metrics") is None, "analysis profile has real-model metrics")
    expect(len(profile.get("required_items", [])) == len(reference.ANALYSIS_REQUIREMENTS),
           "analysis requirement count mismatch")
    expect(all(item.get("qualification_effect") == "none"
               and item.get("satisfied_for_qualification") is False
               for item in profile.get("required_items", [])),
           "an analysis requirement has qualification effect")

    protocol = report.get("reference_protocol", {})
    expect(protocol.get("model_executed") is False, "reference protocol claims model execution")
    expect(protocol.get("executor") == "absent", "reference protocol executor is not absent")
    expect(protocol.get("probability_source") == reference.CONTROL_TRACE_PROVENANCE,
           "probability source is not the labelled control")
    expect(protocol.get("qualification_effect") == "none", "reference protocol has a qualification effect")

    controls = report.get("controls", {})
    expect(controls.get("adverse_all_rejected") is True, "adverse controls are not all rejected")
    expect(controls.get("unknown_never_counted_as_nonspeech") is True, "unknown validity separation missing")
    expect(controls.get("missing_result_never_qualifies") is True, "missing-result control missing")
    adverse = controls.get("adverse", [])
    expect(len(adverse) == 18, "adverse control count is not 18")
    expect(all(item.get("result") == "rejected" for item in adverse), "an adverse control was accepted")

    audit = report.get("asset_audit", {})
    expect(audit.get("qualified") is False, "asset audit claims qualification")
    expect(audit.get("audit_result") == "absent", "asset audit claims assets present")
    expect(audit.get("standard_graph_present") is False, "audit claims standard graph present")
    expect(audit.get("sequence_graph_present") is False, "audit claims sequence graph present")
    expect(audit.get("wheel_present") is False, "audit claims wheel present")
    expect(audit.get("runtime_pair_present") is False, "audit claims runtime present")
    expect(audit.get("rights_record_present") is False, "audit claims rights record present")

    expect(report.get("determinism", {}).get("cold_start_regenerations_required") == 3,
           "cold-start requirement is not three")
    return ok


def check_contract(contract: Dict[str, Any] | None, errors: List[str]) -> bool:
    if contract is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, message, errors) and ok

    expect(contract.get("SPDX-FileCopyrightText") == "2026 Tsakanyan Hovhannes", "contract SPDX copyright missing")
    expect(contract.get("SPDX-License-Identifier") == "Apache-2.0", "contract SPDX license missing")
    expect(contract.get("task") == reference.TASK, "contract task mismatch")
    expect(contract.get("component") == reference.COMPONENT, "contract component mismatch")
    expect(contract.get("repository") == "audio-sdk", "contract repository mismatch")
    expect(contract.get("profile") == "analysis", "contract profile mismatch")
    expect(contract.get("status") == "proposal_only_incomplete", "contract status mismatch")
    expect(contract.get("decision") == "DEFER", "contract decision mismatch")
    expect(contract.get("base_commit") == reference.BASE_COMMIT, "contract base commit mismatch")
    expect(contract.get("branch") == reference.BRANCH, "contract branch mismatch")
    expect(contract.get("worktree") == reference.CLAIM_WORKTREE, "contract worktree mismatch")
    expect(contract.get("reviewer") == reference.REVIEWER, "contract reviewer mismatch")
    expect(contract.get("write_scope") == TASK_PREFIX, "contract write scope mismatch")
    expect(contract.get("qualification", {}).get("status") == "not_qualified", "contract qualification mismatch")
    expect(contract.get("qualification", {}).get("blocked_gate_count") == 8, "contract gate count mismatch")
    expect(contract.get("source_pins") == reference.SOURCE_PINS, "contract source pins differ")
    expect(contract.get("boundary_pins") == reference.BOUNDARY_PINS, "contract boundary pins differ")
    expect(contract.get("boundary", {}).get("registered") is False, "contract is registered")
    expect(contract.get("boundary", {}).get("enabled_by_default") is False, "contract is enabled by default")
    expect(contract.get("boundary", {}).get("descriptor_settings") == {}, "contract descriptor settings are not empty")
    expect(len(contract.get("gates", [])) == 8, "contract gate count is not eight")
    expect(all(gate.get("status") == "blocked" for gate in contract.get("gates", [])), "contract has a non-blocked gate")
    expect(len(contract.get("exact_blockers", [])) == 8, "contract blocker count is not eight")
    expect(contract.get("reproduction", {}).get("cold_start_regenerations") == 3, "contract cold-start count is not three")
    expect(contract.get("task_row_identity", {}).get("whole_file_hashed") is False,
           "contract task identity claims a whole-file hash")
    return ok


def check_task_row_identity(report: Dict[str, Any], contract: Dict[str, Any], errors: List[str]) -> bool:
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
    ok = _expect(report.get("task_row_identity", {}).get("stable_sha256") == digest,
                 "report task identity digest is stale", errors) and ok
    ok = _expect(contract.get("task_row_identity", {}).get("stable_sha256") == digest,
                 "contract task identity digest is stale", errors) and ok
    ok = _expect(report.get("task_row_identity", {}).get("stable_fields") == stable,
                 "report stable fields differ from the board", errors) and ok
    claim = row.get("claim") or {}
    ok = _expect(claim.get("base_commit") == reference.BASE_COMMIT, "board claim base commit differs", errors) and ok
    ok = _expect(claim.get("branch") == reference.BRANCH, "board claim branch differs", errors) and ok
    ok = _expect(claim.get("worktree") == reference.CLAIM_WORKTREE, "board claim worktree differs", errors) and ok
    ok = _expect(claim.get("reviewer") == reference.REVIEWER, "board claim reviewer differs", errors) and ok
    for text, label in ((report, "report"), (contract, "contract")):
        encoded = reference.canonical_bytes(text).decode("utf-8")
        if re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', encoded):
            _expect(False, f"{label} contains a whole-file TASKS.json digest", errors)
            ok = False
    return ok


def check_assets(report: Dict[str, Any], errors: List[str]) -> bool:
    audit = report.get("asset_audit", {})
    live = reference.audit_assets()
    if audit.get("observed") != live.get("observed"):
        errors.append("asset audit observation is stale")
        return False
    ok = True
    ok = _expect(live["audit_result"] == "absent", "TEN VAD assets appeared; re-evaluate blocker", errors) and ok
    ok = _expect(live["qualified"] is False, "asset audit became qualified", errors) and ok
    return ok


def check_sources_reproduction(errors: List[str]) -> bool:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "sources", "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("SOURCES.sha256 is not reproducible: "
                      + (result.stderr.strip() or result.stdout.strip()))
        return False
    return True


def check_reproduction(errors: List[str]) -> Tuple[bool, str, List[str]]:
    expected = reference.canonical_report_bytes(reference.build_report())
    digest = sha256(expected)
    ok = REPORT.is_file() and REPORT.read_bytes() == expected
    if not ok:
        errors.append("report.json is not byte-reproducible")
    sidecar = f"{digest}  report.json\n".encode("utf-8")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar:
        errors.append("report.json.sha256 mismatch")
        ok = False
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    repeats: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="ten-vad-verify-", dir=root))
        try:
            for index in range(3):
                target = work / f"cold-{index}"
                environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
                result = subprocess.run(
                    [sys.executable, str(HERE / "run.py"), "--out", str(target)],
                    cwd=str(HERE), env=environment, capture_output=True,
                    text=True, check=False)
                generated = target / "report.json"
                generated_sidecar = target / "report.json.sha256"
                if result.returncode != 0 or not generated.is_file():
                    errors.append(f"cold regeneration {index} failed: "
                                  + (result.stderr.strip() or result.stdout.strip()))
                    ok = False
                    continue
                payload = generated.read_bytes()
                run_digest = sha256(payload)
                repeats.append(run_digest)
                if payload != expected:
                    errors.append(f"cold regeneration {index} produced different bytes")
                    ok = False
                expected_sidecar = f"{run_digest}  report.json\n".encode("utf-8")
                if not generated_sidecar.is_file() or generated_sidecar.read_bytes() != expected_sidecar:
                    errors.append(f"cold regeneration {index} sidecar mismatch")
                    ok = False
        finally:
            for child in sorted(work.rglob("*"), reverse=True):
                if child.is_file() or child.is_symlink():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            work.rmdir()
    except Exception as error:
        errors.append("cold regeneration failed: " + str(error))
        ok = False
    return ok, digest, repeats


def check_readme(errors: List[str]) -> bool:
    readme = HERE / "README.md"
    if not readme.is_file():
        errors.append("README.md missing")
        return False
    text = readme.read_text(encoding="utf-8")
    ok = True
    for token in (
        "DEFER",
        "not_qualified",
        "proposal-only",
        "incomplete",
        "1d937742e1a7a2d7424a10b049eabaf2afbb6b385c008ea6393cc70477",
        "cold-start",
        "No exact TEN VAD source",
    ):
        ok = _expect(token in text, f"README missing token: {token}", errors) and ok
    ok = _expect("SPDX-" + "License-Identifier:" not in text,
                 "README contains contiguous SPDX-License-Identifier token", errors) and ok
    return ok


def main() -> int:
    errors: List[str] = []
    pins = parse_pins(errors)
    checked = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    report_ok = check_report(report, errors)
    contract_ok = check_contract(contract, errors)
    identity_ok = False
    asset_ok = False
    if report_ok and contract_ok and report is not None and contract is not None:
        identity_ok = check_task_row_identity(report, contract, errors)
        asset_ok = check_assets(report, errors)
    sources_ok = check_sources_reproduction(errors)
    repro_ok, digest, repeats = check_reproduction(errors)
    readme_ok = check_readme(errors)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    print(f"task={reference.TASK}")
    print(f"report_sha256={digest}")
    print(f"pins_checked={checked}")
    print(f"report={report_ok} contract={contract_ok} identity={identity_ok} assets={asset_ok}")
    print(f"sources={sources_ok} reproduction={repro_ok} readme={readme_ok}")
    print(f"cold_start_digests={','.join(repeats)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
