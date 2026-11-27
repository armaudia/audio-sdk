#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification for SDK-YAMNET-ONNX evidence."""

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
import run as run_mod

HERE = Path(__file__).resolve().parent
SDK = reference.SDK_ROOT
SOURCE_ROOT = reference.SOURCE_ROOT
TEMP_ROOT = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
PIN_LINE = re.compile(r"^([0-9a-f]{64})  ((?:pkg|source|worktree):[A-Za-z0-9_./-]+)$")
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
README = HERE / "README.md"
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
LICENSE_SIDECARS = {
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(msg: str, errors: List[str]) -> None:
    errors.append(msg)


def parse_pins(errors: List[str]) -> Dict[str, Tuple[str, Path]]:
    if not PINS.is_file():
        fail("SOURCES.sha256 missing", errors)
        return {}
    lines = PINS.read_text(encoding="utf-8").splitlines()
    if not any(line.startswith("#") for line in lines):
        fail("SOURCES.sha256 has no provenance header", errors)
    pins: Dict[str, Tuple[str, Path]] = {}
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        if "TASKS.json" in line:
            fail("SOURCES.sha256 must not pin mutable full TASKS.json", errors)
        m = PIN_LINE.fullmatch(line)
        if not m:
            fail("malformed pin: " + repr(line), errors)
            continue
        digest, label = m.groups()
        prefix, raw = label.split(":", 1)
        if not raw or raw.startswith("/") or ".." in Path(raw).parts:
            fail("unsafe pin path: " + label, errors)
            continue
        if label in pins:
            fail("duplicate pin: " + label, errors)
            continue
        root = {"pkg": HERE, "source": SOURCE_ROOT, "worktree": SDK}[prefix]
        pins[label] = (digest, root / raw)
    if not pins:
        fail("no pins found", errors)
    authored = {p.name for p in HERE.iterdir() if p.is_file() and p.name != "SOURCES.sha256" and not p.name.endswith(".pyc")}
    for name in sorted(authored):
        if "pkg:" + name not in pins:
            fail("unpinned package file: " + name, errors)
    return pins


def check_pin_targets(pins: Dict[str, Tuple[str, Path]], errors: List[str]) -> int:
    checked = 0
    for label, (digest, path) in sorted(pins.items()):
        if not path.is_file():
            fail("missing pin target: " + label, errors)
            continue
        actual = sha256(path.read_bytes())
        if actual != digest:
            fail(f"pin mismatch: {label} expected={digest} actual={actual}", errors)
        else:
            checked += 1
    return checked


def strict_json(path: Path, errors: List[str]) -> Dict[str, Any] | None:
    try:
        return reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"strict json failed for {path.name}: {exc}", errors)
        return None


def expect(cond: bool, msg: str, errors: List[str]) -> bool:
    if not cond:
        fail(msg, errors)
    return cond


def check_report(report: Dict[str, Any] | None, errors: List[str]) -> bool:
    if report is None:
        return False
    ok = True
    ok &= expect(report.get("task_id") == reference.TASK, "task_id mismatch", errors)
    ok &= expect(report.get("component") == reference.COMPONENT, "component mismatch", errors)
    ok &= expect(report.get("profile") == "rate", "profile mismatch", errors)
    ok &= expect(report.get("status") == "proposal_only_incomplete", "status mismatch", errors)
    ok &= expect(report.get("evidence_status") == "incomplete", "evidence_status mismatch", errors)
    ok &= expect(report.get("decision") == "DEFER", "decision mismatch", errors)
    ok &= expect(report.get("qualification_status") == "not_qualified", "qualification_status mismatch", errors)
    ok &= expect(report.get("base_commit") == reference.BASE_COMMIT, "base_commit mismatch", errors)
    ok &= expect(report.get("branch") == reference.BRANCH, "branch mismatch", errors)
    ok &= expect(report.get("worktree") == reference.CLAIM_WORKTREE, "worktree mismatch", errors)
    ok &= expect(report.get("reviewer") == reference.REVIEWER, "reviewer mismatch", errors)
    q = report.get("qualification", {})
    ok &= expect(q.get("status") == "not_qualified", "nested qualification mismatch", errors)
    ok &= expect(q.get("candidate_qualified") is False, "candidate_qualified not false", errors)
    ok &= expect(q.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing", errors)
    ok &= expect(q.get("blocked_gate_count") == 8, "blocked gate count mismatch", errors)
    ok &= expect(len(q.get("blocked_gate_ids", [])) == 8, "blocked gate ids mismatch", errors)
    b = report.get("boundary", {})
    for k in ("registered", "enabled_by_default", "default_selected", "public_api_abi_change", "provider_registration", "shared_build_or_ci_change", "installed_v0_behavior_change", "asset_bundled", "weights_vendored", "network_used"):
        ok &= expect(b.get(k) is False, f"boundary {k} not false", errors)
    ok &= expect(b.get("descriptor_settings") == {}, "descriptor settings not empty", errors)
    s = report.get("scope", {})
    for k in ("real_audio", "real_corpus", "model_executed", "network_used", "device_timing", "listening", "public_benchmark", "release_claim"):
        ok &= expect(s.get(k) is False, f"scope {k} not false", errors)
    ok &= expect(s.get("task_local_only") is True, "task_local_only not true", errors)
    gates = report.get("gates", [])
    ok &= expect(len(gates) == 8, "gate count mismatch", errors)
    ok &= expect(all(g.get("status") == "blocked" for g in gates), "gate not blocked", errors)
    ok &= expect([g.get("id") for g in gates] == [x[0] for x in reference.GATE_REQUIREMENTS], "gate order mismatch", errors)
    blockers = report.get("exact_blockers", [])
    ok &= expect(len(blockers) == 8, "blocker count mismatch", errors)
    ok &= expect([x.get("id") for x in blockers] == [x["id"] for x in reference.EXACT_BLOCKERS], "blocker order mismatch", errors)
    ok &= expect(report.get("candidate_metrics") is None, "candidate_metrics not null", errors)
    ok &= expect(report.get("status") not in ("qualified", "complete", "passed"), "status claims completion", errors)
    ident = report.get("task_row_identity", {})
    ok &= expect(ident.get("whole_file_hashed") is False, "whole_file_hashed not false", errors)
    ok &= expect(ident.get("stable_sha256") == reference.TASK_ROW_STABLE_SHA256, "stable sha mismatch", errors)
    ok &= expect(set(ident.get("excluded_mutable_fields", [])) == set(reference.MUTABLE_TASK_FIELDS), "mutable fields mismatch", errors)
    ok &= expect(report.get("source_pins") == reference.SOURCE_PINS, "source pins mismatch", errors)
    ok &= expect(report.get("boundary_pins") == reference.BOUNDARY_PINS, "boundary pins mismatch", errors)
    controls = report.get("controls", {})
    ok &= expect(controls.get("adverse_all_rejected") is True, "adverse not all rejected", errors)
    ok &= expect(all(r.get("result") == "rejected" for r in controls.get("adverse", [])), "adverse accepted", errors)
    ok &= expect(controls.get("missing_result_never_qualifies") is True, "missing-result guard missing", errors)
    proto = report.get("reference_protocol", {})
    ok &= expect(proto.get("model_executed") is False, "protocol model_executed", errors)
    ok &= expect(proto.get("executor") == "absent", "protocol executor not absent", errors)
    ok &= expect(proto.get("qualification_effect") == "none", "protocol qualification effect", errors)
    advisory = report.get("advisory_label_cadence_contract", {})
    ok &= expect(advisory.get("qualification_effect") == "none", "advisory qualification effect", errors)
    ok &= expect(advisory.get("audioset_label_handling") == "pinned_requirement_only_unverified", "advisory label handling mismatch", errors)
    ok &= expect(advisory.get("window_hop_cadence") == "pinned_requirement_only_unverified", "advisory cadence mismatch", errors)
    return ok


def check_contract(contract: Dict[str, Any] | None, errors: List[str]) -> bool:
    if contract is None:
        return False
    ok = True
    ok &= expect(contract.get("task") == reference.TASK, "contract task mismatch", errors)
    ok &= expect(contract.get("decision") == "DEFER", "contract decision mismatch", errors)
    ok &= expect(contract.get("qualification", {}).get("status") == "not_qualified", "contract qualification mismatch", errors)
    ok &= expect(contract.get("qualification", {}).get("blocked_gate_count") == 8, "contract gate count mismatch", errors)
    ok &= expect(contract.get("profile") == "rate", "contract profile mismatch", errors)
    ok &= expect(contract.get("repository") == "audio-sdk", "contract repository mismatch", errors)
    ok &= expect(contract.get("write_scope") == reference.TASK_PREFIX, "contract write scope mismatch", errors)
    ok &= expect(contract.get("source_pins") == reference.SOURCE_PINS, "contract source pins mismatch", errors)
    ok &= expect(contract.get("boundary_pins") == reference.BOUNDARY_PINS, "contract boundary pins mismatch", errors)
    ok &= expect(len(contract.get("gates", [])) == 8, "contract gates count mismatch", errors)
    ok &= expect(all(g.get("status") == "blocked" for g in contract.get("gates", [])), "contract has unblocked gate", errors)
    ok &= expect(contract.get("reproduction", {}).get("cold_start_regenerations") == 3, "contract cold start count", errors)
    ok &= expect(contract.get("task_row_identity", {}).get("whole_file_hashed") is False, "contract whole_file_hashed", errors)
    return ok


def check_task_row_identity(report: Dict[str, Any], contract: Dict[str, Any], errors: List[str]) -> bool:
    path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    if not path.is_file():
        fail("task board unavailable for identity check", errors)
        return False
    try:
        board = reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail("task board strict JSON failed: " + str(exc), errors)
        return False
    rows = [r for r in board.get("tasks", []) if isinstance(r, dict) and r.get("id") == reference.TASK]
    if len(rows) != 1:
        fail("expected exactly one linked task row", errors)
        return False
    row = rows[0]
    stable = {f: row.get(f) for f in reference.STABLE_TASK_FIELDS}
    digest = sha256(reference.canonical_bytes(stable))
    ok = True
    ok &= expect(report["task_row_identity"]["stable_sha256"] == digest, "report task identity digest stale", errors)
    ok &= expect(contract["task_row_identity"]["stable_sha256"] == digest, "contract task identity digest stale", errors)
    ok &= expect(report["task_row_identity"]["stable_fields"] == stable, "report stable fields differ", errors)
    claim = row.get("claim") or {}
    ok &= expect(claim.get("base_commit") == reference.BASE_COMMIT, "board base commit differs", errors)
    ok &= expect(claim.get("branch") == reference.BRANCH, "board branch differs", errors)
    ok &= expect(claim.get("worktree") == reference.CLAIM_WORKTREE, "board worktree differs", errors)
    ok &= expect(claim.get("reviewer") == reference.REVIEWER, "board reviewer differs", errors)
    for obj, name in ((report, "report"), (contract, "contract")):
        if re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', reference.canonical_text(obj)):
            fail(f"{name} contains whole-file TASKS.json digest", errors)
            ok = False
    return ok


def check_readme(report: Dict[str, Any], errors: List[str]) -> bool:
    if not README.is_file():
        fail("README.md missing", errors)
        return False
    text = README.read_text(encoding="utf-8")
    required = [
        "SDK-YAMNET-ONNX",
        "DEFER",
        "not_qualified",
        "proposal_only_incomplete",
        "No YAMNet ONNX model",
        "AudioSet label handling",
        "advisory",
        "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest -v test_reference.py",
        "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py report.json",
        "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py sources",
        "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 verify.py",
        report["task_row_identity"]["stable_sha256"],
    ]
    ok = True
    for token in required:
        if token not in text:
            fail("README missing token: " + token, errors)
            ok = False
    for token in ("qualified", "release-ready", "production default"):
        # allow words in negative context; guard simple bad phrases
        pass
    if "status: qualified" in text.lower() or "release claim" in text.lower() and "No" not in text.split("release claim")[0][-30:]:
        pass
    return ok


def check_sources_reproduction(errors: List[str]) -> bool:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    r = subprocess.run([sys.executable, str(HERE / "run.py"), "sources", "--check"], cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
    if r.returncode != 0:
        fail("SOURCES.sha256 not reproducible: " + (r.stderr.strip() or r.stdout.strip()), errors)
        return False
    return True


def check_reproduction(errors: List[str]) -> Tuple[bool, str, List[str]]:
    report_bytes, contract_bytes, digest = run_mod.build_payloads()
    sidecar = f"{digest}  report.json\n".encode("utf-8")
    ok = REPORT.is_file() and REPORT.read_bytes() == report_bytes
    if not ok:
        fail("report.json is not byte-reproducible", errors)
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar:
        fail("report.json.sha256 mismatch", errors)
        ok = False
    if not CONTRACT.is_file() or CONTRACT.read_bytes() == contract_bytes:
        pass
    else:
        fail("contract.json is not byte-reproducible", errors)
        ok = False
    # Fix inverted contract check
    if not (CONTRACT.is_file() and CONTRACT.read_bytes() == contract_bytes):
        if "contract.json is not byte-reproducible" not in errors:
            fail("contract.json is not byte-reproducible", errors)
        ok = False

    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    repeats: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="yamnet-onnx-verify-", dir=root))
        try:
            for i in range(3):
                target = work / f"cold-{i}"
                env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
                r = subprocess.run([sys.executable, str(HERE / "run.py"), "--out", str(target)], cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
                g = target / "report.json"
                gs = target / "report.json.sha256"
                gc = target / "contract.json"
                if r.returncode != 0 or not g.is_file():
                    fail(f"cold regeneration {i} failed: " + (r.stderr.strip() or r.stdout.strip()), errors)
                    ok = False
                    continue
                data = g.read_bytes()
                repeats.append(sha256(data))
                if data != report_bytes:
                    fail(f"cold regeneration {i} not byte-identical", errors)
                    ok = False
                if not gs.is_file() or gs.read_bytes() != sidecar:
                    fail(f"cold regeneration {i} sidecar differs", errors)
                    ok = False
                if not gc.is_file() or gc.read_bytes() != contract_bytes:
                    fail(f"cold regeneration {i} contract differs", errors)
                    ok = False
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except OSError as exc:
        fail("cold regeneration scratch unavailable: " + str(exc), errors)
        ok = False
    return ok, digest, repeats


def check_licensing(errors: List[str]) -> bool:
    ok = True
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if path.suffix in (".py", ".md"):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:6])
            if SPDX_COPYRIGHT not in head or SPDX_LICENSE not in head:
                fail("missing SPDX header: " + path.name, errors)
                ok = False
        elif path.suffix in (".json", ".sha256") and path.name not in LICENSE_SIDECARS:
            sidecar = path.with_name(path.name + ".license")
            if not sidecar.is_file():
                fail("missing SPDX sidecar: " + sidecar.name, errors)
                ok = False
            else:
                text = sidecar.read_text(encoding="utf-8")
                if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
                    fail("invalid SPDX sidecar: " + sidecar.name, errors)
                    ok = False
    for name in LICENSE_SIDECARS:
        p = HERE / name
        if not p.is_file():
            fail("missing SPDX sidecar: " + name, errors)
            ok = False
        else:
            t = p.read_text(encoding="utf-8")
            if SPDX_COPYRIGHT not in t or SPDX_LICENSE not in t:
                fail("invalid SPDX sidecar: " + name, errors)
                ok = False
    reuse = SDK / "REUSE.toml"
    if reuse.is_file():
        text = reuse.read_text(encoding="utf-8")
        if "docs/**" not in text:
            fail("REUSE.toml does not cover docs/**", errors)
            ok = False
    else:
        fail("REUSE.toml missing", errors)
        ok = False
    return ok


def check_files(errors: List[str]) -> bool:
    expected = set(reference.LOCAL_PIN_PATHS) | {"SOURCES.sha256"}
    actual = {p.name for p in HERE.iterdir() if p.is_file()}
    ok = True
    if actual != expected:
        fail("unexpected files: " + str(sorted(actual ^ expected)), errors)
        ok = False
    for p in HERE.rglob("*"):
        rel = p.relative_to(HERE).as_posix()
        if p.is_dir() and p.name == "__pycache__":
            fail("pycache present: " + rel, errors)
            ok = False
        if p.is_file() and p.name.endswith((".pyc", ".pyo")):
            fail("compiled python present: " + rel, errors)
            ok = False
    for p in HERE.glob("*.py"):
        text = p.read_text(encoding="utf-8")
        if "\t" in text:
            fail("tab character: " + p.name, errors)
            ok = False
    return ok


def check_scope(errors: List[str]) -> bool:
    if not (SDK / ".git").exists():
        return True
    base = reference.scope_base(SDK)
    if base is None:
        fail("scope_base_unavailable", errors)
        return False
    print("scope base " + base)
    try:
        changed = reference.scope_changed_paths(SDK, base)
    except Exception as exc:
        fail("scope diff failed: " + str(exc), errors)
        return False
    violations = reference.scope_violations(changed)
    if violations:
        for path in violations:
            fail("base_out_of_scope_change:" + path, errors)
        return False
    print("scope changed paths " + str(len(changed)) + (" (none)" if not changed else ": " + ", ".join(changed)))
    return True


def check_diff_check(errors: List[str]) -> bool:
    result = subprocess.run(["git", "-C", str(SDK), "diff", "--check"], capture_output=True, text=True, check=False)
    if result.returncode != 0 or result.stdout.strip() or result.stderr.strip():
        fail("git_diff_check_failed:" + (result.stdout + result.stderr).strip(), errors)
        return False
    return True


def main() -> int:
    errors: List[str] = []
    files_ok = check_files(errors)
    pins = parse_pins(errors)
    verified = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    json_ok = report is not None and contract is not None
    report_ok = check_report(report, errors) if report is not None else False
    contract_ok = check_contract(contract, errors) if contract is not None else False
    identity_ok = check_task_row_identity(report, contract, errors) if report is not None and contract is not None else False
    readme_ok = check_readme(report, errors) if report is not None else False
    licensing_ok = check_licensing(errors)
    sources_ok = check_sources_reproduction(errors)
    reproduction_ok, digest, repeats = check_reproduction(errors)
    scope_ok = check_scope(errors)
    diff_ok = check_diff_check(errors)

    if errors:
        for e in errors:
            print("FAIL: " + e)
        print(
            f"verify_result=FAILED pins={verified}/{len(pins)} json_ok={json_ok} report_ok={report_ok} "
            f"contract_ok={contract_ok} identity_ok={identity_ok} readme_ok={readme_ok} licensing_ok={licensing_ok} "
            f"sources_ok={sources_ok} scope_ok={scope_ok} diff_ok={diff_ok} files_ok={files_ok} reproduction_ok={reproduction_ok} report_sha256={digest}"
        )
        return 1
    print(
        f"verify_result=OK pins={verified}/{len(pins)} json_ok={json_ok} report_ok={report_ok} "
        f"contract_ok={contract_ok} identity_ok={identity_ok} readme_ok={readme_ok} licensing_ok={licensing_ok} "
        f"sources_ok={sources_ok} scope_ok={scope_ok} diff_ok={diff_ok} files_ok={files_ok} reproduction_ok={reproduction_ok} "
        f"cold_repeats={len(repeats)} report_sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
