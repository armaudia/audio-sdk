#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only fail-closed verifier for VoiceBank+DEMAND/VOiCES/DNS5 evidence."""

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
TEMP_ROOT = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
PIN_LINE = re.compile(r"^([0-9a-f]{64})  ((?:pkg|source|worktree):[A-Za-z0-9_./-]+)$")
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
SOURCES = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"


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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _expect(ok: bool, msg: str, errors: List[str]) -> bool:
    if not ok:
        errors.append(msg)
    return ok


def strict_json(path: Path, errors: List[str]) -> Dict[str, Any] | None:
    try:
        return reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"strict json failed for {path.name}: {exc}")
        return None


def parse_pins(errors: List[str]) -> Dict[str, Tuple[str, Path]]:
    if not SOURCES.is_file():
        errors.append("SOURCES.sha256 missing")
        return {}
    lines = SOURCES.read_text(encoding="utf-8").splitlines()
    if not lines or not any(line.startswith("#") for line in lines):
        errors.append("SOURCES.sha256 has no provenance header")
    pins: Dict[str, Tuple[str, Path]] = {}
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        if "TASKS.json" in line:
            errors.append("SOURCES.sha256 must not pin mutable full TASKS.json")
        m = PIN_LINE.fullmatch(line)
        if not m:
            errors.append("malformed pin: " + repr(line))
            continue
        digest, label = m.groups()
        prefix, raw = label.split(":", 1)
        if raw.startswith("/") or ".." in Path(raw).parts:
            errors.append("unsafe pin path: " + label)
            continue
        if label in pins:
            errors.append("duplicate pin: " + label)
            continue
        base = {"pkg": HERE, "source": SOURCE_ROOT, "worktree": SDK}[prefix]
        pins[label] = (digest, base / raw)
    authored = {p.name for p in HERE.iterdir() if p.is_file() and p.name != "SOURCES.sha256" and not p.name.endswith(".pyc")}
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
            errors.append(f"pin mismatch: {label}")
        else:
            checked += 1
    return checked


def check_report(report: Dict[str, Any] | None, errors: List[str]) -> bool:
    if report is None:
        return False
    ok = True
    def expect(cond: bool, msg: str) -> None:
        nonlocal ok
        ok = _expect(cond, msg, errors) and ok
    expect(report.get("task_id") == reference.TASK, "task_id mismatch")
    expect(report.get("component") == reference.COMPONENT, "component mismatch")
    expect(report.get("profile") == "evidence", "profile mismatch")
    expect(report.get("status") == "proposal_only_incomplete", "status mismatch")
    expect(report.get("evidence_status") == "incomplete", "evidence_status mismatch")
    expect(report.get("decision") == "DEFER", "decision mismatch")
    expect(report.get("defer_before") == "opt_in_adapter_exposure", "defer boundary mismatch")
    expect(report.get("qualification_status") == "not_qualified", "qualification_status mismatch")
    expect(report.get("base_commit") == reference.BASE_COMMIT, "base_commit mismatch")
    expect(report.get("branch") == reference.BRANCH, "branch mismatch")
    expect(report.get("reviewer") == reference.REVIEWER, "reviewer mismatch")
    expect(report.get("worktree") == reference.CLAIM_WORKTREE, "worktree mismatch")
    q = report.get("qualification", {})
    expect(q.get("status") == "not_qualified", "nested qualification mismatch")
    expect(q.get("candidate_qualified") is False, "candidate_qualified not false")
    expect(q.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing")
    expect(q.get("blocked_gate_count") == 8, "blocked gate count mismatch")
    expect(isinstance(q.get("blocked_gate_ids"), list) and len(q["blocked_gate_ids"]) == 8, "blocked gate ids mismatch")
    boundary = report.get("boundary", {})
    for key in reference.BOUNDARY:
        expect(boundary.get(key) == reference.BOUNDARY[key], f"boundary mismatch: {key}")
    scope = report.get("scope", {})
    for key in reference.SCOPE:
        expect(scope.get(key) == reference.SCOPE[key], f"scope mismatch: {key}")
    gates = report.get("gates", [])
    expect([g.get("id") for g in gates] == [x[0] for x in reference.GATE_REQUIREMENTS], "gate IDs/order mismatch")
    expect(all(g.get("status") == "blocked" for g in gates), "non-blocked gate")
    blockers = report.get("exact_blockers", [])
    expect([b.get("id") for b in blockers] == [x["id"] for x in reference.EXACT_BLOCKERS], "blocker IDs/order mismatch")
    expect(len(blockers) == 8, "blocker count mismatch")
    identity = report.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False, "whole_file_hashed not false")
    expect(identity.get("stable_sha256") == reference.TASK_ROW_STABLE_SHA256, "stable sha mismatch")
    expect(set(identity.get("excluded_mutable_fields", [])) == set(reference.MUTABLE_TASK_FIELDS), "mutable fields mismatch")
    expect(report.get("source_pins") == reference.SOURCE_PINS, "source pins mismatch")
    expect(report.get("boundary_pins") == reference.BOUNDARY_PINS, "boundary pins mismatch")
    controls = report.get("controls", {})
    expect(controls.get("adverse_all_rejected") is True, "adverse controls not all rejected")
    expect(controls.get("tracks_separate") is True, "tracks_separate missing")
    expect(controls.get("acquisition_only_never_scorable") is True, "acquisition control missing")
    expect(controls.get("missing_result_never_qualifies") is True, "missing-result control missing")
    audit = report.get("asset_audit", {})
    expect(audit.get("audit_result") == "absent", "asset audit result mismatch")
    expect(audit.get("qualified") is False, "asset audit qualified")
    proto = report.get("reference_protocol", {})
    expect(proto.get("model_executed") is False, "protocol model_executed")
    expect(proto.get("executor") == "absent", "protocol executor mismatch")
    expect(proto.get("qualification_effect") == "none", "protocol qualification effect")
    expect(report.get("source_reported_context", {}).get("label") == "source_reported_not_measured_here", "source-reported label mismatch")
    expect(report.get("determinism", {}).get("cold_start_regenerations_required") == 3, "cold start mismatch")
    encoded = reference.canonical_bytes(report).decode("utf-8")
    expect('TASKS.json": "' not in encoded, "report contains whole-file TASKS digest")
    return ok


def check_contract(contract: Dict[str, Any] | None, errors: List[str]) -> bool:
    if contract is None:
        return False
    ok = True
    def expect(cond: bool, msg: str) -> None:
        nonlocal ok
        ok = _expect(cond, msg, errors) and ok
    expect(contract.get("task") == reference.TASK, "contract task mismatch")
    expect(contract.get("profile") == "evidence", "contract profile mismatch")
    expect(contract.get("status") == "proposal_only_incomplete", "contract status mismatch")
    expect(contract.get("decision") == "DEFER", "contract decision mismatch")
    expect(contract.get("qualification", {}).get("status") == "not_qualified", "contract qualification mismatch")
    expect(contract.get("qualification", {}).get("blocked_gate_count") == 8, "contract blocked gate count mismatch")
    expect(contract.get("task_row_identity", {}).get("stable_sha256") == reference.TASK_ROW_STABLE_SHA256, "contract stable sha mismatch")
    expect(contract.get("task_row_identity", {}).get("whole_file_hashed") is False, "contract whole_file_hashed mismatch")
    expect(contract.get("source_pins") == reference.SOURCE_PINS, "contract source pins mismatch")
    expect(contract.get("boundary_pins") == reference.BOUNDARY_PINS, "contract boundary pins mismatch")
    expect(contract.get("boundary", {}).get("descriptor_settings") == {}, "contract descriptor settings mismatch")
    expect(len(contract.get("gates", [])) == 8, "contract gate count mismatch")
    expect(all(g.get("status") == "blocked" for g in contract.get("gates", [])), "contract gate status mismatch")
    expect(contract.get("reproduction", {}).get("cold_start_regenerations") == 3, "contract cold start mismatch")
    return ok


def check_task_row_identity(report: Dict[str, Any], contract: Dict[str, Any], errors: List[str]) -> bool:
    path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    if not path.is_file():
        errors.append("task board unavailable for identity check")
        return False
    doc = reference.strict_loads(path.read_text(encoding="utf-8"))
    rows = [r for r in doc.get("tasks", []) if isinstance(r, dict) and r.get("id") == reference.TASK]
    if len(rows) != 1:
        errors.append("expected exactly one linked task row")
        return False
    row = rows[0]
    stable = {k: row.get(k) for k in reference.STABLE_TASK_FIELDS}
    digest = sha256(reference.canonical_bytes(stable))
    ok = True
    ok = _expect(digest == reference.TASK_ROW_STABLE_SHA256, "board stable digest differs from pinned identity", errors) and ok
    ok = _expect(report.get("task_row_identity", {}).get("stable_sha256") == digest, "report stale task identity", errors) and ok
    ok = _expect(contract.get("task_row_identity", {}).get("stable_sha256") == digest, "contract stale task identity", errors) and ok
    claim = row.get("claim") or {}
    ok = _expect(claim.get("base_commit") == reference.BASE_COMMIT, "claim base_commit differs", errors) and ok
    ok = _expect(claim.get("branch") == reference.BRANCH, "claim branch differs", errors) and ok
    ok = _expect(claim.get("worktree") == reference.CLAIM_WORKTREE, "claim worktree differs", errors) and ok
    ok = _expect(claim.get("reviewer") == reference.REVIEWER, "claim reviewer differs", errors) and ok
    return ok


def check_assets(report: Dict[str, Any], errors: List[str]) -> bool:
    live = reference.audit_assets()
    if report.get("asset_audit", {}).get("observed") != live.get("observed"):
        errors.append("asset audit observation is stale")
        return False
    ok = True
    ok = _expect(live["audit_result"] == "absent", "required assets appeared; re-evaluate blockers", errors) and ok
    ok = _expect(live["qualified"] is False, "asset audit became qualified", errors) and ok
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
        work = Path(tempfile.mkdtemp(prefix="voicebank-demand-voices-dns5-verify-", dir=root))
        try:
            for i in range(3):
                target = work / f"cold-{i}"
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
                result = subprocess.run([sys.executable, str(HERE / "run.py"), "--out", str(target)], cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
                gen = target / "report.json"
                gen_side = target / "report.json.sha256"
                if result.returncode != 0 or not gen.is_file():
                    errors.append(f"cold regeneration {i} failed: " + (result.stderr.strip() or result.stdout.strip()))
                    ok = False
                    continue
                payload = gen.read_bytes()
                run_digest = sha256(payload)
                repeats.append(run_digest)
                if payload != expected:
                    errors.append(f"cold regeneration {i} produced different bytes")
                    ok = False
                expected_side = f"{run_digest}  report.json\n".encode("utf-8")
                if not gen_side.is_file() or gen_side.read_bytes() != expected_side:
                    errors.append(f"cold regeneration {i} sidecar mismatch")
                    ok = False
        finally:
            for child in sorted(work.rglob("*"), reverse=True):
                if child.is_file() or child.is_symlink():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            work.rmdir()
    except Exception as exc:
        errors.append("cold regeneration failed: " + str(exc))
        ok = False
    return ok, digest, repeats


def check_readme(errors: List[str]) -> bool:
    readme = HERE / "README.md"
    if not readme.is_file():
        errors.append("README.md missing")
        return False
    text = readme.read_text(encoding="utf-8")
    ok = True
    for token in ("DEFER", "not_qualified", "proposal-only", "incomplete", reference.TASK_ROW_STABLE_SHA256, "cold-start", "VoiceBank+DEMAND", "VOiCES", "DNS5"):
        ok = _expect(token in text, f"README missing token: {token}", errors) and ok
    ok = _expect("SPDX-" + "License-Identifier:" not in text, "README contains contiguous SPDX token", errors) and ok
    return ok


def main() -> int:
    errors: List[str] = []
    pins = parse_pins(errors)
    checked = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    report_ok = check_report(report, errors)
    contract_ok = check_contract(contract, errors)
    identity_ok = asset_ok = False
    if report_ok and contract_ok and report is not None and contract is not None:
        identity_ok = check_task_row_identity(report, contract, errors)
        asset_ok = check_assets(report, errors)
    sources_ok = check_sources_reproduction(errors)
    repro_ok, digest, repeats = check_reproduction(errors)
    readme_ok = check_readme(errors)
    if errors:
        print("FAIL")
        for e in errors:
            print("- " + e)
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
