#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict verifier for whisper-timestamp-and-mfa-tooling task evidence."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent
WORKTREE = reference.WORKTREE
TASK_PREFIX = reference.TASK_PREFIX


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(errors: list[str], code: str) -> None:
    if code not in errors:
        errors.append(code)


def load_json_strict(path: Path) -> dict:
    obj = reference.strict_load(path)
    if not isinstance(obj, dict):
        raise reference.EvidenceError("json_not_object")
    return obj


def check_pins(errors: list[str]) -> None:
    pins = HERE / "SOURCES.sha256"
    if not pins.is_file():
        fail(errors, "missing_sources_sha256")
        return
    seen = set()
    for line in pins.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            fail(errors, "bad_sources_line")
            continue
        digest, name = parts
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            fail(errors, "bad_sources_digest")
        if name in seen:
            fail(errors, "duplicate_sources_pin")
        seen.add(name)
        if name.startswith("source:"):
            rel = name[len("source:"):]
            target = reference.AUDIO_ROOT / rel
        elif name.startswith("worktree:"):
            rel = name[len("worktree:"):]
            target = WORKTREE / rel
        elif name.startswith("pkg:"):
            rel = name[len("pkg:"):]
            target = HERE / rel
        else:
            fail(errors, "unknown_pin_prefix")
            continue
        if not target.is_file():
            fail(errors, f"missing_pin_target:{name}")
            continue
        if sha256(target) != digest:
            fail(errors, f"pin_mismatch:{name}")


def check_report_contract(errors: list[str]) -> tuple[dict, dict]:
    contract = load_json_strict(HERE / "contract.json")
    report = load_json_strict(HERE / "report.json")
    if contract.get("task") != reference.TASK or report.get("task") != reference.TASK:
        fail(errors, "task_mismatch")
    if report.get("decision") != "DEFER" or report.get("qualification_status") != "not_qualified":
        fail(errors, "decision_mismatch")
    if contract.get("contract_sha256") and contract.get("contract_sha256") != reference.sha256_bytes(reference.canonical_bytes(contract)):
        fail(errors, "contract_self_hash_mismatch")
    # report carries contract sha
    expected_contract = reference.sha256_bytes(reference.canonical_bytes(reference.build_contract()))
    if report.get("contract_sha256") != expected_contract:
        fail(errors, "contract_sha256_mismatch")
    # sidecar
    sidecar = HERE / "report.json.sha256"
    if not sidecar.is_file():
        fail(errors, "missing_report_sidecar")
    else:
        want = sha256(HERE / "report.json")
        got = sidecar.read_text(encoding="utf-8").strip().split()[0]
        if got != want:
            fail(errors, "report_sidecar_mismatch")
    # gates/blockers
    gates = report.get("gates", [])
    if len(gates) != 5 or not all(g.get("status") == "blocked" for g in gates):
        fail(errors, "gates_not_blocked")
    blockers = report.get("blockers", [])
    if len(blockers) != 5 or not all(b.get("status") == "open" for b in blockers):
        fail(errors, "blockers_not_open")
    if report.get("controls", {}).get("missing_result_qualifies") is not False:
        fail(errors, "missing_result_qualifies")
    if report.get("controls", {}).get("adverse_manifest_all_rejected") is not True:
        fail(errors, "adverse_not_all_rejected")
    # board projection
    proj = reference.board_row_projection()
    if report.get("board_row_projection") != proj:
        fail(errors, "board_projection_mismatch")
    if report.get("board_row_projection_sha256") != reference.sha256_bytes(reference.canonical_bytes(proj)):
        fail(errors, "board_projection_sha256_mismatch")
    return contract, report


def check_readme(errors: list[str], report: dict) -> None:
    readme = HERE / "README.md"
    if not readme.is_file():
        fail(errors, "missing_readme")
        return
    text = readme.read_text(encoding="utf-8")
    for token in ["DEFER", "not_qualified", "RG-01", "BLK-01", "SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING"]:
        if token not in text:
            fail(errors, f"readme_missing:{token}")
    # digest table validation if present
    report_sha = sha256(HERE / "report.json")
    contract_sha = sha256(HERE / "contract.json")
    if report_sha not in text:
        fail(errors, "readme_missing_report_digest")
    if contract_sha not in text:
        fail(errors, "readme_missing_contract_digest")


def check_scope(errors: list[str]) -> None:
    scope = reference.check_scope(WORKTREE, TASK_PREFIX)
    if scope["status"] == "scope_base_unavailable":
        fail(errors, "scope_base_unavailable")
        return
    for p in scope.get("violations", []):
        fail(errors, "base_out_of_scope_change:" + p)
    # git diff --check
    proc = subprocess.run(["git","-C",str(WORKTREE),"diff","--check"], capture_output=True, text=True)
    if proc.returncode != 0:
        fail(errors, "git_diff_check_failed")


def check_cold_regen(errors: list[str]) -> None:
    expected_report = (HERE / "report.json").read_bytes()
    expected_contract = (HERE / "contract.json").read_bytes()
    expected_sidecar = (HERE / "report.json.sha256").read_bytes()
    with tempfile.TemporaryDirectory(prefix="whisper-mfa-verify-") as td:
        tmp = Path(td)
        # copy package
        pkg = tmp / "pkg"
        pkg.mkdir()
        for f in HERE.iterdir():
            if f.is_file():
                (pkg / f.name).write_bytes(f.read_bytes())
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONHASHSEED"] = "0"
        env["SOURCE_ROOT"] = str(reference.AUDIO_ROOT)
        env["WORKTREE_ROOT"] = str(WORKTREE)
        for i in range(3):
            proc = subprocess.run([sys.executable, "run.py", "all"], cwd=pkg, env=env, capture_output=True, text=True)
            if proc.returncode != 0:
                fail(errors, f"regen_failed:{i}:{proc.stderr.strip()[:200]}")
                return
            if (pkg / "report.json").read_bytes() != expected_report:
                fail(errors, f"report_nondeterministic:{i}")
            if (pkg / "contract.json").read_bytes() != expected_contract:
                fail(errors, f"contract_nondeterministic:{i}")
            if (pkg / "report.json.sha256").read_bytes() != expected_sidecar:
                fail(errors, f"sidecar_nondeterministic:{i}")


def check_tests(errors: list[str]) -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONHASHSEED"] = "0"
    proc = subprocess.run([sys.executable, "-m", "unittest", "-q", "test_reference.py"], cwd=HERE, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        fail(errors, "tests_failed")


def check_no_forbidden_changes(errors: list[str]) -> None:
    forbidden = [
        "CONTRACTS.md","CMakeLists.txt","REUSE.toml",".github/workflows/ci.yml",
        "api/include/audio_sdk/provider_v0.h","api/include/audio_sdk/session_v0.h",
    ]
    scope = reference.check_scope(WORKTREE, TASK_PREFIX)
    if scope["status"] == "ok":
        for p in scope.get("changed", []):
            if p in forbidden or not p.startswith(TASK_PREFIX):
                fail(errors, "forbidden_or_out_of_scope:" + p)


def main() -> int:
    errors: list[str] = []
    try:
        contract, report = check_report_contract(errors)
    except Exception as e:
        fail(errors, f"report_contract_exception:{type(e).__name__}")
        report = {}
        contract = {}
    check_pins(errors)
    check_readme(errors, report if isinstance(report, dict) else {})
    check_scope(errors)
    check_no_forbidden_changes(errors)
    check_tests(errors)
    check_cold_regen(errors)
    if errors:
        print("VERIFY_FAIL")
        for e in errors:
            print(e)
        return 1
    print("VERIFY_OK")
    print(f"task={reference.TASK}")
    print(f"report_sha256={sha256(HERE / 'report.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
