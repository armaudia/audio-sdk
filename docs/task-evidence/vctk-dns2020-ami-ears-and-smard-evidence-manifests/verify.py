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
    expect(report.get("profile") == "evidence", "profile is not evidence")
    expect(report.get("status") == "proposal_only_incomplete", "status mismatch")
    expect(report.get("evidence_status") == "incomplete", "evidence_status mismatch")
    expect(report.get("decision") == "DEFER", "decision is not DEFER")
    expect(report.get("qualification_status") == "not_qualified", "qualification_status mismatch")
    expect(report.get("base_commit") == reference.BASE_COMMIT, "base_commit mismatch")
    expect(report.get("branch") == reference.BRANCH, "branch mismatch")

    qualification = report.get("qualification", {})
    expect(qualification.get("status") == "not_qualified", "nested qualification is not not_qualified")
    expect(qualification.get("candidate_qualified") is False, "candidate_qualified is not false")
    expect(qualification.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing")
    expect(qualification.get("blocked_gate_count") == 8, "blocked gate count is not eight")
    expect(len(qualification.get("blocked_gate_ids", [])) == 8, "blocked gate id list is not eight")

    boundary = report.get("boundary", {})
    for key in ("registered", "enabled_by_default", "default_selected", "public_api_abi_change",
                "provider_registration", "production_callback_registered", "descriptor_registry_change",
                "shared_build_or_ci_change", "installed_v0_behavior_change", "network_used",
                "adapter_json_added", "ci_change", "processor_exposure", "rights_approved"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    expect(boundary.get("descriptor_settings") == {}, "descriptor settings are not empty")

    scope = report.get("scope", {})
    for key in ("benchmark_claim", "corpus_admitted", "device_timing", "listening", "model_executed",
                "network_used", "real_audio_copied", "real_audio_decoded", "real_corpus_ingested",
                "real_corpus_scored", "release_claim", "runtime_invoked", "weights_downloaded", "weights_loaded"):
        expect(scope.get(key) is False, "scope flag not false: " + key)
    expect(scope.get("task_local_only") is True, "task_local_only is not true")

    gates = report.get("gates", [])
    expected_gates = [name for name, _ in reference.GATE_REQUIREMENTS]
    expect([g.get("id") for g in gates] == expected_gates, "gate IDs or order mismatch")
    expect(all(g.get("status") == "blocked" for g in gates), "a gate is not blocked")
    blockers = report.get("exact_blockers", [])
    expect([b.get("id") for b in blockers] == [b["id"] for b in reference.EXACT_BLOCKERS], "blocker IDs mismatch")
    expect(len(blockers) == 8, "exact blocker count is not eight")

    identity = report.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False, "task identity claims a whole-file hash")
    expect(set(identity.get("excluded_mutable_fields", [])) == set(reference.MUTABLE_TASK_FIELDS), "mutable field exclusion mismatch")
    expect(report.get("source_pins") == reference.SOURCE_PINS, "report source pins differ")
    expect(report.get("boundary_pins") == reference.BOUNDARY_PINS, "report boundary pins differ")

    controls = report.get("controls", {})
    adverse = controls.get("adverse", [])
    expect(len(adverse) >= 15, "adverse control count too small")
    expect(all(item.get("result") == "rejected" for item in adverse), "an adverse control was accepted")
    expect(controls.get("adverse_all_rejected") is True, "adverse_all_rejected missing")
    expect(controls.get("missing_result_never_qualifies") is True, "missing-result control missing")

    audit = report.get("asset_audit", {})
    expect(audit.get("qualified") is False, "asset audit claims qualification")
    expect(audit.get("admitted_count") == 0, "asset audit admitted count is not zero")

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
    expect(contract.get("profile") == "evidence", "contract profile mismatch")
    expect(contract.get("decision") == "DEFER", "contract decision mismatch")
    expect(contract.get("qualification", {}).get("status") == "not_qualified", "contract qualification mismatch")
    expect(contract.get("task_row_identity", {}).get("stable_sha256") == reference.task_row_identity()["stable_sha256"], "contract task-row identity mismatch")
    expect(len(contract.get("gates", [])) == 8, "contract gate count mismatch")
    expect(all(g.get("status") == "blocked" for g in contract.get("gates", [])), "contract gate not blocked")
    return ok


def check_sidecar(errors: List[str]) -> bool:
    if not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("report or sidecar missing")
        return False
    digest = sha256(REPORT.read_bytes())
    expected = f"{digest}  report.json\n".encode("utf-8")
    if SIDECAR.read_bytes() != expected:
        errors.append("report sidecar mismatch")
        return False
    return True


def check_cold_start(errors: List[str]) -> bool:
    temp_root = TEMP_ROOT if TEMP_ROOT.is_dir() else Path(tempfile.gettempdir())
    ok = True
    for index in range(3):
        with tempfile.TemporaryDirectory(prefix=f"vctk-dns2020-ami-ears-smard-cold-{index}-", dir=temp_root) as tmp:
            cmd = [sys.executable, str(HERE / "run.py"), "report.json", "--out", tmp]
            proc = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                errors.append(f"cold-start run {index} failed: {proc.stdout}\n{proc.stderr}")
                ok = False
                continue
            generated = Path(tmp) / "report.json"
            side = Path(tmp) / "report.json.sha256"
            if not generated.is_file() or not side.is_file():
                errors.append(f"cold-start run {index} missing outputs")
                ok = False
                continue
            if generated.read_bytes() != REPORT.read_bytes():
                errors.append(f"cold-start run {index} report bytes differ")
                ok = False
            if side.read_bytes() != SIDECAR.read_bytes():
                errors.append(f"cold-start run {index} sidecar bytes differ")
                ok = False
    return ok


def main() -> int:
    errors: List[str] = []
    pins = parse_pins(errors)
    checked = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    report_ok = check_report(report, errors)
    contract_ok = check_contract(contract, errors)
    sidecar_ok = check_sidecar(errors)
    cold_ok = check_cold_start(errors)
    if errors:
        print("VERIFY FAILED")
        for err in errors:
            print("- " + err)
        return 1
    print("VERIFY PASS")
    print(f"pins_checked={checked}")
    print(f"report_ok={report_ok} contract_ok={contract_ok} sidecar_ok={sidecar_ok} cold_start_ok={cold_ok}")
    print(f"report_sha256={sha256(REPORT.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
