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
TEMP_ROOT = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
TASK_PREFIX = "docs/task-evidence/pesq-polqa-and-3quest/"
PIN_LINE = re.compile(r"^([0-9a-f]{64})  ((?:pkg|source|worktree):[A-Za-z0-9_./-]+)$")


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
    authored = {path.name for path in HERE.iterdir() if path.is_file() and path.name not in ("SOURCES.sha256",) and not path.name.endswith(".pyc") and "__pycache__" not in path.name}
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
    expect(report.get("profile") == "evidence", "profile mismatch")
    expect(report.get("mode") == reference.MODE, "mode mismatch")
    expect(report.get("status") == "proposal_only_incomplete", "status mismatch")
    expect(report.get("evidence_status") == "incomplete", "evidence_status mismatch")
    expect(report.get("proposal_only") is True, "proposal_only not true")
    expect(report.get("decision") == "DEFER", "decision not DEFER")
    expect(report.get("defer_before") == "processor_exposure", "defer_before mismatch")
    expect(report.get("qualification_status") == "not_qualified", "qualification_status mismatch")
    expect(report.get("base_commit") == reference.BASE_COMMIT, "base_commit mismatch")
    expect(report.get("branch") == reference.BRANCH, "branch mismatch")
    q = report.get("qualification", {})
    expect(q.get("status") == "not_qualified", "nested qualification status mismatch")
    expect(q.get("candidate_qualified") is False, "candidate_qualified not false")
    expect(q.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing")
    expect(q.get("blocked_gate_count") == 8, "blocked gate count not 8")
    expect(isinstance(q.get("blocked_gate_ids"), list) and len(q["blocked_gate_ids"]) == 8, "blocked gate ids not 8")
    gates = report.get("gates", [])
    expect(isinstance(gates, list) and len(gates) == 8, "gates not 8")
    expect(all(isinstance(g, dict) and g.get("status") == "blocked" for g in gates), "gate not blocked")
    blockers = report.get("exact_blockers", [])
    expect(isinstance(blockers, list) and len(blockers) == 8, "blockers not 8")
    controls = report.get("reference_protocol", {}).get("adverse_controls", [])
    expect(isinstance(controls, list) and len(controls) >= 10, "insufficient adverse controls")
    expect(all(c.get("result") == "rejected" for c in controls), "adverse control not rejected")
    expect(report.get("reference_protocol", {}).get("model_executed") is False, "model_executed not false")
    expect(report.get("source_pins") == reference.SOURCE_PINS, "source pins mismatch")
    expect(report.get("boundary_pins") == reference.BOUNDARY_PINS, "boundary pins mismatch")
    expect(report.get("scope") == reference.SCOPE, "scope mismatch")
    expect(report.get("boundary") == reference.BOUNDARY, "boundary mismatch")
    return ok


def check_contract(contract: Dict[str, Any] | None, errors: List[str]) -> bool:
    if contract is None:
        return False
    ok = True
    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, message, errors) and ok
    expect(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID, "contract schema mismatch")
    expect(contract.get("task") == reference.TASK, "contract task mismatch")
    expect(contract.get("decision") == "DEFER", "contract decision mismatch")
    expect(contract.get("qualification_status") == "not_qualified", "contract qualification mismatch")
    expect(contract.get("proposal_only") is True, "contract proposal_only mismatch")
    expect(contract.get("status") == "proposal_only_incomplete", "contract status mismatch")
    expect(len(contract.get("gates", [])) == 8, "contract gates not 8")
    expect(len(contract.get("exact_blockers", [])) == 8, "contract blockers not 8")
    expect(contract.get("source_pins") == reference.SOURCE_PINS, "contract source pins mismatch")
    expect(contract.get("boundary_pins") == reference.BOUNDARY_PINS, "contract boundary pins mismatch")
    cm = contract.get("caller_manifest_contract", {})
    expect(cm.get("present_behavior") == "validate_only_no_execution_no_network", "caller manifest behavior mismatch")
    expect(cm.get("asset_is_vendored") is False, "caller manifest vendored mismatch")
    return ok


def check_task_row_identity(report: Dict[str, Any] | None, contract: Dict[str, Any] | None, errors: List[str]) -> bool:
    if report is None or contract is None:
        return False
    ok = True
    live = reference.task_row_identity()
    for label, doc in (("report", report), ("contract", contract)):
        ident = doc.get("task_row_identity")
        if ident != live:
            errors.append(f"{label} task_row_identity mismatch")
            ok = False
        stable = (ident or {}).get("stable_fields", {})
        if stable.get("id") != reference.TASK:
            errors.append(f"{label} stable task id mismatch")
            ok = False
    # ensure mutable full TASKS.json digest is not embedded as a pin
    for text, label in ((report, "report"), (contract, "contract")):
        encoded = reference.canonical_bytes(text).decode("utf-8")
        if re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', encoded):
            errors.append(f"{label} contains a whole-file TASKS.json digest")
            ok = False
    return ok


def check_assets(report: Dict[str, Any] | None, errors: List[str]) -> bool:
    if report is None:
        return False
    audit = report.get("asset_audit", {})
    live = reference.audit_assets()
    if audit.get("observed") != live.get("observed"):
        errors.append("asset audit observation is stale")
        return False
    ok = True
    ok = _expect(live["all_absence_probes_absent"] is True, "absence probe present; re-evaluate blocker", errors) and ok
    return ok


def check_sources_reproduction(errors: List[str]) -> bool:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run([sys.executable, str(HERE / "run.py"), "sources", "--check"], cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("SOURCES.sha256 not reproducible: " + (result.stderr.strip() or result.stdout.strip()))
        return False
    return True


def check_reproduction(errors: List[str]) -> Tuple[bool, str, List[str]]:
    expected = reference.canonical_report_bytes(reference.build_report())
    digest = sha256(expected)
    expected_contract = reference.canonical_contract_bytes()
    ok = REPORT.is_file() and REPORT.read_bytes() == expected
    if not ok:
        errors.append("report.json is not byte-reproducible")
    sidecar = f"{digest}  report.json\n".encode("utf-8")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar:
        errors.append("report.json.sha256 mismatch")
        ok = False
    if not CONTRACT.is_file() or CONTRACT.read_bytes() != expected_contract:
        errors.append("contract.json is not byte-reproducible")
        ok = False
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    repeats: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="pesq-polqa-3quest-verify-", dir=root))
        try:
            for index in range(3):
                target = work / f"cold-{index}"
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
                r1 = subprocess.run([sys.executable, str(HERE / "run.py"), "report.json", "--out", str(target)], cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
                r2 = subprocess.run([sys.executable, str(HERE / "run.py"), "contract.json", "--out", str(target)], cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
                generated = target / "report.json"
                gside = target / "report.json.sha256"
                gcontract = target / "contract.json"
                if r1.returncode != 0 or r2.returncode != 0 or not generated.is_file():
                    errors.append(f"cold regeneration {index} failed: " + (r1.stderr.strip() or r1.stdout.strip() or r2.stderr.strip()))
                    ok = False
                    continue
                data = generated.read_bytes()
                repeats.append(sha256(data))
                if data != expected:
                    errors.append(f"cold regeneration {index} is not byte-identical")
                    ok = False
                if not gside.is_file() or gside.read_bytes() != sidecar:
                    errors.append(f"cold regeneration {index} sidecar differs")
                    ok = False
                if not gcontract.is_file() or gcontract.read_bytes() != expected_contract:
                    errors.append(f"cold regeneration {index} contract differs")
                    ok = False
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except OSError as error:
        errors.append("cold regeneration scratch unavailable: " + str(error))
        ok = False
    return ok, digest, repeats


def check_licensing(errors: List[str]) -> bool:
    copyright_line = reference.SPDX_COPYRIGHT
    license_line = reference.SPDX_LICENSE
    ok = True
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if path.suffix in (".py", ".md"):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
            if copyright_line not in head or license_line not in head:
                errors.append("missing SPDX header: " + path.name)
                ok = False
        elif path.suffix in (".json", ".sha256") and not path.name.endswith(".license"):
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
    result = subprocess.run(["git", "-C", str(SDK), "status", "--porcelain=v1", "--untracked-files=all"], capture_output=True, text=True, check=True)
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
    report_ok = check_report(report, errors)
    contract_ok = check_contract(contract, errors)
    identity_ok = check_task_row_identity(report, contract, errors)
    assets_ok = check_assets(report, errors)
    licensing_ok = check_licensing(errors)
    sources_ok = check_sources_reproduction(errors)
    reproduction_ok, digest, repeats = check_reproduction(errors)
    scope_ok = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"verify_result=FAILED pins={verified}/{len(pins)} json_ok={json_ok} report_ok={report_ok} contract_ok={contract_ok} identity_ok={identity_ok} assets_ok={assets_ok} licensing_ok={licensing_ok} sources_ok={sources_ok} scope_ok={scope_ok} reproduction_ok={reproduction_ok} report_sha256={digest}")
        return 1
    print(f"verify_result=OK pins={verified}/{len(pins)} json_ok={json_ok} report_ok={report_ok} contract_ok={contract_ok} identity_ok={identity_ok} assets_ok={assets_ok} licensing_ok={licensing_ok} sources_ok={sources_ok} scope_ok={scope_ok} reproduction_ok={reproduction_ok} cold_repeats={len(repeats)} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
