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
TASK_PREFIX = reference.TASK_PREFIX
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
    authored = {
        path.name for path in HERE.iterdir()
        if path.is_file() and path.name != "SOURCES.sha256" and not path.name.endswith(".pyc")
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
    def expect(cond: bool, msg: str) -> None:
        nonlocal ok
        ok = _expect(cond, msg, errors) and ok

    expect(report.get("task_id") == reference.TASK, "task_id mismatch")
    expect(report.get("component") == reference.COMPONENT, "component mismatch")
    expect(report.get("profile") == "spatial", "profile is not spatial")
    expect(report.get("status") == "proposal_only_incomplete", "status mismatch")
    expect(report.get("evidence_status") == "incomplete", "evidence_status mismatch")
    expect(report.get("decision") == "DEFER", "decision is not DEFER")
    expect(report.get("qualification_status") == "not_qualified", "qualification_status mismatch")
    expect(report.get("base_commit") == reference.BASE_COMMIT, "base_commit mismatch")
    expect(report.get("branch") == reference.BRANCH, "branch mismatch")
    expect(report.get("worktree") == reference.CLAIM_WORKTREE, "worktree mismatch")
    expect(report.get("reviewer") == reference.REVIEWER, "reviewer mismatch")
    q = report.get("qualification", {})
    expect(q.get("status") == "not_qualified", "nested qualification not not_qualified")
    expect(q.get("candidate_qualified") is False, "candidate_qualified not false")
    expect(q.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing")
    expect(q.get("blocked_gate_count") == 8, "blocked gate count not 8")
    expect(len(q.get("blocked_gate_ids", [])) == 8, "blocked gate ids count not 8")
    b = report.get("boundary", {})
    for k in ("registered","enabled_by_default","default_selected","public_api_abi_change","provider_registration","shared_build_or_ci_change","installed_v0_behavior_change","asset_bundled","weights_vendored","network_used"):
        expect(b.get(k) is False, f"boundary {k} not false")
    expect(b.get("descriptor_settings") == {}, "descriptor settings not empty")
    s = report.get("scope", {})
    for k in ("real_audio","real_corpus","model_executed","network_used","device_timing","listening","public_benchmark","release_claim"):
        expect(s.get(k) is False, f"scope {k} not false")
    expect(s.get("task_local_only") is True, "task_local_only not true")
    gates = report.get("gates", [])
    expect(len(gates) == 8, "gate count not 8")
    expect(all(g.get("status") == "blocked" for g in gates), "a gate not blocked")
    expect([g.get("id") for g in gates] == [x[0] for x in reference.GATE_REQUIREMENTS], "gate IDs/order mismatch")
    blockers = report.get("exact_blockers", [])
    expect(len(blockers) == 8, "blocker count not 8")
    expect([x.get("id") for x in blockers] == [x["id"] for x in reference.EXACT_BLOCKERS], "blocker IDs/order mismatch")
    expect(report.get("candidate_metrics") is None, "candidate_metrics not null")
    expect(report.get("status") not in ("qualified","complete","passed"), "status claims completion")
    ident = report.get("task_row_identity", {})
    expect(ident.get("whole_file_hashed") is False, "whole_file_hashed not false")
    expect(ident.get("stable_sha256") == reference.TASK_ROW_STABLE_SHA256, "stable sha mismatch")
    expect(set(ident.get("excluded_mutable_fields", [])) == set(reference.MUTABLE_TASK_FIELDS), "mutable fields mismatch")
    expect(report.get("source_pins") == reference.SOURCE_PINS, "source pins mismatch")
    expect(report.get("boundary_pins") == reference.BOUNDARY_PINS, "boundary pins mismatch")
    controls = report.get("controls", {})
    expect(controls.get("adverse_all_rejected") is True, "adverse not all rejected")
    expect(controls.get("missing_result_never_qualifies") is True, "missing-result guard missing")
    expect(all(r.get("result") == "rejected" for r in controls.get("adverse", [])), "adverse accepted")
    proto = report.get("reference_protocol", {})
    expect(proto.get("model_executed") is False, "protocol model_executed")
    expect(proto.get("executor") == "absent", "protocol executor not absent")
    expect(proto.get("qualification_effect") == "none", "protocol qualification effect")
    return ok


def check_contract(contract: Dict[str, Any] | None, errors: List[str]) -> bool:
    if contract is None:
        return False
    ok = True
    def expect(cond: bool, msg: str) -> None:
        nonlocal ok
        ok = _expect(cond, msg, errors) and ok
    expect(contract.get("task") == reference.TASK, "contract task mismatch")
    expect(contract.get("decision") == "DEFER", "contract decision mismatch")
    expect(contract.get("qualification", {}).get("status") == "not_qualified", "contract qualification mismatch")
    expect(contract.get("qualification", {}).get("blocked_gate_count") == 8, "contract gate count mismatch")
    expect(contract.get("profile") == "spatial", "contract profile mismatch")
    expect(contract.get("repository") == "audio-sdk", "contract repository mismatch")
    expect(contract.get("write_scope") == TASK_PREFIX, "contract write scope mismatch")
    expect(contract.get("source_pins") == reference.SOURCE_PINS, "contract source pins mismatch")
    expect(contract.get("boundary_pins") == reference.BOUNDARY_PINS, "contract boundary pins mismatch")
    expect(len(contract.get("gates", [])) == 8, "contract gates count not 8")
    expect(all(g.get("status") == "blocked" for g in contract.get("gates", [])), "contract has unblocked gate")
    expect(contract.get("reproduction", {}).get("cold_start_regenerations") == 3, "contract cold start count")
    expect(contract.get("task_row_identity", {}).get("whole_file_hashed") is False, "contract whole_file_hashed")
    return ok


def check_task_row_identity(report: Dict[str, Any], contract: Dict[str, Any], errors: List[str]) -> bool:
    path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    if not path.is_file():
        errors.append("task board unavailable for identity check")
        return False
    try:
        board = reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        errors.append("task board strict JSON failed: " + str(error))
        return False
    rows = [r for r in board.get("tasks", []) if isinstance(r, dict) and r.get("id") == reference.TASK]
    if len(rows) != 1:
        errors.append("expected exactly one linked task row")
        return False
    row = rows[0]
    stable = {f: row.get(f) for f in reference.STABLE_TASK_FIELDS}
    digest = sha256(reference.canonical_bytes(stable))
    ok = True
    ok = _expect(report["task_row_identity"]["stable_sha256"] == digest, "report task identity digest stale", errors) and ok
    ok = _expect(contract["task_row_identity"]["stable_sha256"] == digest, "contract task identity digest stale", errors) and ok
    ok = _expect(report["task_row_identity"]["stable_fields"] == stable, "report stable fields differ", errors) and ok
    claim = row.get("claim") or {}
    ok = _expect(claim.get("base_commit") == reference.BASE_COMMIT, "board base commit differs", errors) and ok
    ok = _expect(claim.get("branch") == reference.BRANCH, "board branch differs", errors) and ok
    ok = _expect(claim.get("worktree") == reference.CLAIM_WORKTREE, "board worktree differs", errors) and ok
    ok = _expect(claim.get("reviewer") == reference.REVIEWER, "board reviewer differs", errors) and ok
    for obj, name in ((report, "report"), (contract, "contract")):
        if re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', reference.canonical_text(obj)):
            errors.append(f"{name} contains whole-file TASKS.json digest")
            ok = False
    return ok


def check_sources_reproduction(errors: List[str]) -> bool:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(HERE / "run.py"), "sources", "--check"],
                       cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        errors.append("SOURCES.sha256 not reproducible: " + (r.stderr.strip() or r.stdout.strip()))
        return False
    return True


def check_reproduction(errors: List[str]) -> Tuple[bool, str, List[str]]:
    report_bytes, contract_bytes = (reference.canonical_bytes(reference.build_report()), reference.canonical_bytes(reference.build_contract(reference.build_report())))
    digest = sha256(report_bytes)
    sidecar = f"{digest}  report.json\n".encode("utf-8")
    ok = REPORT.is_file() and REPORT.read_bytes() == report_bytes
    if not ok:
        errors.append("report.json is not byte-reproducible")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar:
        errors.append("report.json.sha256 mismatch")
        ok = False
    if not CONTRACT.is_file() or CONTRACT.read_bytes() != contract_bytes:
        errors.append("contract.json is not byte-reproducible")
        ok = False
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    repeats: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="vflite-vad-verify-", dir=root))
        try:
            for i in range(3):
                target = work / f"cold-{i}"
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
                r = subprocess.run([sys.executable, str(HERE / "run.py"), "--out", str(target)],
                                   cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
                g = target / "report.json"
                gs = target / "report.json.sha256"
                gc = target / "contract.json"
                if r.returncode != 0 or not g.is_file():
                    errors.append(f"cold regeneration {i} failed: " + (r.stderr.strip() or r.stdout.strip()))
                    ok = False
                    continue
                data = g.read_bytes()
                repeats.append(sha256(data))
                if data != report_bytes:
                    errors.append(f"cold regeneration {i} not byte-identical")
                    ok = False
                if not gs.is_file() or gs.read_bytes() != sidecar:
                    errors.append(f"cold regeneration {i} sidecar differs")
                    ok = False
                if not gc.is_file() or gc.read_bytes() != contract_bytes:
                    errors.append(f"cold regeneration {i} contract differs")
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
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:6])
            if copyright_line not in head or license_line not in head:
                errors.append("missing SPDX header: " + path.name)
                ok = False
        elif path.suffix in (".json", ".sha256") and not path.name.endswith(".license"):
            sidecar = path.with_name(path.name + ".license")
            if not sidecar.is_file():
                errors.append("missing SPDX sidecar: " + sidecar.name)
                ok = False
            else:
                text = sidecar.read_text(encoding="utf-8")
                if copyright_line not in text or license_line not in text:
                    errors.append("invalid SPDX sidecar: " + sidecar.name)
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
    result = subprocess.run(["git", "-C", str(SDK), "status", "--porcelain=v1", "--untracked-files=all"],
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
    contract_ok = check_contract(contract, errors) if contract is not None else False
    identity_ok = check_task_row_identity(report, contract, errors) if report is not None and contract is not None else False
    licensing_ok = check_licensing(errors)
    sources_ok = check_sources_reproduction(errors)
    reproduction_ok, digest, repeats = check_reproduction(errors)
    scope_ok = check_scope(errors)
    if errors:
        for e in errors:
            print("FAIL: " + e)
        print(f"verify_result=FAILED pins={verified}/{len(pins)} json_ok={json_ok} report_ok={report_ok} contract_ok={contract_ok} identity_ok={identity_ok} licensing_ok={licensing_ok} sources_ok={sources_ok} scope_ok={scope_ok} reproduction_ok={reproduction_ok} report_sha256={digest}")
        return 1
    print(f"verify_result=OK pins={verified}/{len(pins)} json_ok={json_ok} report_ok={report_ok} contract_ok={contract_ok} identity_ok={identity_ok} licensing_ok={licensing_ok} sources_ok={sources_ok} scope_ok={scope_ok} reproduction_ok={reproduction_ok} cold_repeats={len(repeats)} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
