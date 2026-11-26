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
TASK_PREFIX = "docs/task-evidence/pulsevad/"
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
    expect(report.get("mode") == reference.MODE, "mode mismatch")
    expect(report.get("profile") == "analysis", "profile is not analysis")
    expect(report.get("status") == "proposal_only_incomplete", "status mismatch")
    expect(report.get("evidence_status") == "incomplete", "evidence_status mismatch")
    expect(report.get("proposal_only") is True, "proposal_only is not true")
    expect(report.get("decision") == "DEFER", "decision is not DEFER")
    expect(report.get("qualification_status") == "not_qualified", "qualification_status mismatch")
    expect(report.get("base_commit") == reference.BASE_COMMIT, "base_commit mismatch")
    expect(report.get("branch") == reference.BRANCH, "branch mismatch")

    qualification = report.get("qualification", {})
    expect(qualification.get("status") == "not_qualified", "nested qualification is not not_qualified")
    expect(qualification.get("candidate_qualified") is False, "candidate_qualified is not false")
    expect(qualification.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing")
    expect(qualification.get("decision") == "DEFER", "nested decision is not DEFER")
    expect(qualification.get("blocked_gate_count") == 8, "blocked gate count is not eight")
    expect(isinstance(qualification.get("blocked_gate_ids"), list) and len(qualification["blocked_gate_ids"]) == 8, "blocked gate id list is not eight")

    boundary = report.get("boundary", {})
    for key in ("registered", "enabled_by_default", "default_selected", "public_api_abi_change", "abi_change",
                "provider_registration", "production_callback_registered", "descriptor_registry_change",
                "shared_build_or_ci_change", "installed_v0_behavior_change", "asset_bundled",
                "adapter_runtime_bundled", "weights_vendored", "sdk_callback_invoked", "network_used", "vendor_runtime_invoked"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    expect(boundary.get("descriptor_settings") == {}, "descriptor settings are not empty")

    scope = report.get("scope", {})
    for key in ("real_audio", "real_corpus", "real_pulsevad_runtime", "model_executed", "weights_loaded",
                "weights_downloaded", "runtime_invoked", "vendor_runtime_invoked", "network_used",
                "device_timing", "listening", "public_benchmark", "release_claim"):
        expect(scope.get(key) is False, "scope flag not false: " + key)
    expect(scope.get("task_local_only") is True, "task_local_only is not true")

    gates = report.get("gates", [])
    expected_gates = [name for name, _ in reference.GATE_REQUIREMENTS]
    expect([gate.get("id") for gate in gates] == expected_gates, "gate IDs or order mismatch")
    expect(len(gates) == 8, "gate count is not eight")
    expect(all(gate.get("status") == "blocked" for gate in gates), "a gate is not blocked")

    blockers = report.get("exact_blockers", [])
    expected_blockers = [item["id"] for item in reference.EXACT_BLOCKERS]
    expect([item.get("id") for item in blockers] == expected_blockers, "blocker IDs or order mismatch")
    expect(len(blockers) == 8, "exact blocker count is not eight")
    expect(report.get("status") not in ("qualified", "complete", "passed"), "status claims completion")
    expect(report.get("candidate_metrics") is None, "candidate_metrics is not null")
    context = report.get("source_reported_context", {})
    expect(context.get("label") == "source_reported_not_measured_here", "source-reported context is not labelled")

    identity = report.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False, "task identity claims a whole-file hash")
    expect(identity.get("source") == "audio-benchmark-platform/plan/swarm/TASKS.json", "task identity source mismatch")
    expect(set(identity.get("excluded_mutable_fields", [])) == set(reference.MUTABLE_TASK_FIELDS), "excluded mutable field set mismatch")
    return ok


def check_contract(contract: Dict[str, Any] | None, report: Dict[str, Any] | None, errors: List[str]) -> bool:
    if contract is None or report is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, message, errors) and ok

    expect(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID, "contract schema mismatch")
    expect(contract.get("task") == reference.TASK, "contract task mismatch")
    expect(contract.get("decision") == "DEFER", "contract decision mismatch")
    expect(contract.get("qualification") == report.get("qualification"), "contract qualification differs from report")
    expect(contract.get("source_pins") == report.get("source_pins"), "contract source pins differ from report")
    expect(contract.get("boundary_pins") == report.get("boundary_pins"), "contract boundary pins differ from report")
    expect(contract.get("task_row_identity") == report.get("task_row_identity"), "contract task identity differs from report")
    expect(contract.get("caller_asset_contract") == report.get("caller_asset_contract"), "contract caller-asset contract differs from report")
    expect(contract.get("exact_blockers") == report.get("exact_blockers"), "contract blockers differ from report")
    expect(contract.get("gates") == report.get("gates"), "contract gates differ from report")
    return ok


def check_runtime_constraints(errors: List[str]) -> None:
    pkg = str(HERE)
    saved = sys.path[:]
    try:
        sys.path = [pkg] + [item for item in sys.path if item != pkg]
        for name in list(sys.modules):
            if name == "reference" or name.startswith("reference."):
                sys.modules.pop(name, None)
        import reference as pkg_reference  # noqa: WPS433
        for path in pkg_reference.ABSENCE_PROBES:
            if (SOURCE_ROOT / path).exists():
                errors.append("absence probe exists: " + path)
        controls = pkg_reference.run_adverse_controls()
        bad = [c["case"] for c in controls if c["result"] != "rejected"]
        if bad:
            errors.append("adverse controls not rejected: " + ", ".join(bad))
    except Exception as error:  # noqa: BLE001
        errors.append("runtime checks failed: " + type(error).__name__ + ": " + str(error))
    finally:
        sys.path = saved


def regenerate_three_times(errors: List[str]) -> None:
    base = TEMP_ROOT if TEMP_ROOT.is_dir() else Path(tempfile.gettempdir())
    base.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix="pulsevad-evidence-", dir=str(base)))
    try:
        digests = []
        for index in range(3):
            out = temp / f"run-{index}"
            out.mkdir()
            for target in ("report.json", "contract.json"):
                proc = subprocess.run(
                    [sys.executable, str(HERE / "run.py"), target, "--out", str(out)],
                    cwd=str(HERE), check=False, capture_output=True, text=True)
                if proc.returncode != 0:
                    errors.append(f"regeneration {index + 1} {target} failed rc={proc.returncode}: {proc.stderr.strip() or proc.stdout.strip()}")
                    return
            report_path = out / "report.json"
            if not report_path.is_file():
                errors.append(f"regeneration {index + 1} missing report.json")
                return
            digest = sha256(report_path.read_bytes())
            digests.append(digest)
            sidecar = out / "report.json.sha256"
            if not sidecar.is_file() or sidecar.read_text(encoding="utf-8").strip() != f"{digest}  report.json":
                errors.append(f"regeneration {index + 1} sidecar mismatch")
            contract_path = out / "contract.json"
            expected_contract = reference.canonical_contract_bytes()
            if not contract_path.is_file() or contract_path.read_bytes() != expected_contract:
                errors.append(f"regeneration {index + 1} contract mismatch")
        if len(set(digests)) != 1:
            errors.append("report bytes differed across 3 cold-start regenerations: " + ", ".join(digests))
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def main() -> int:
    errors: List[str] = []
    report_bytes = REPORT.read_bytes() if REPORT.is_file() else b""
    report_digest = sha256(report_bytes) if report_bytes else None
    sidecar = SIDECAR.read_text(encoding="utf-8").strip() if SIDECAR.is_file() else None
    pins = parse_pins(errors)
    pin_count = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    report_ok = check_report(report, errors)
    contract_ok = check_contract(contract, report, errors)
    if report_digest and sidecar != f"{report_digest}  report.json":
        errors.append("report sidecar mismatch")
    expected_report = reference.canonical_report_bytes(reference.build_report())
    if report_bytes != expected_report:
        errors.append("report.json is not byte-identical to canonical reference output")
    expected_contract = reference.canonical_contract_bytes()
    if not CONTRACT.is_file() or CONTRACT.read_bytes() != expected_contract:
        errors.append("contract.json is not byte-identical to canonical reference output")
    check_runtime_constraints(errors)
    regenerate_three_times(errors)

    result = "PASS" if not errors else "FAIL"
    if report_digest:
        print(f"report_sha256={report_digest}")
    print(f"pinned_targets_checked={pin_count}")
    print(f"task_row_hashed=stable_identity_only")
    print(f"result={result}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
