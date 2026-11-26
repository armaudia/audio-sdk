# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for SDK-SOX-TEMPO evidence package.

Checks strict JSON, canonical bytes, exact pins, blocker semantics, stable
linked-row identity, licensing, prohibited artifacts, git scope and three
cold-start byte-identical regenerations. Never writes package evidence except
temp files in system temp dirs during regeneration checks.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run as run_mod  # noqa: E402

SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"
README_PATH = HERE / "README.md"
TASK_PREFIX = reference.TASK_PREFIX
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"

ARTIFACT_FILES = (
    "README.md", "contract.json", "reference.py", "report.json",
    "report.json.sha256", "run.py", "SOURCES.sha256", "test_reference.py", "verify.py",
)
SIDECAR_FILES = (
    "README.md.license", "contract.json.license", "reference.py.license",
    "report.json.license", "report.json.sha256.license", "run.py.license",
    "SOURCES.sha256.license", "test_reference.py.license", "verify.py.license",
)
PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".m4a", ".aac",
    ".onnx", ".pt", ".pth", ".ckpt", ".safetensors", ".bin", ".so",
    ".dylib", ".a", ".o", ".zip", ".tar", ".gz", ".whl", ".dll", ".exe",
}


class VerificationError(AssertionError):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def strict_load(path: Path) -> Any:
    def parse_constant(token: str) -> Any:
        raise VerificationError(f"{path.name}:nonfinite:{token}")

    def object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise VerificationError(f"{path.name}:duplicate_key:{key}")
            obj[key] = value
        return obj

    value = json.loads(path.read_text(encoding="utf-8"), parse_constant=parse_constant, object_pairs_hook=object_pairs_hook)
    walk_finite(value, path.name)
    return value


def walk_finite(value: Any, field: str) -> None:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise VerificationError(f"{field}:nonfinite")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            walk_finite(item, f"{field}[{i}]")
    elif isinstance(value, dict):
        for k, item in value.items():
            walk_finite(item, f"{field}.{k}")


def check(condition: bool, message: str, problems: List[str]) -> None:
    if not condition:
        problems.append(message)


def check_pins(problems: List[str]) -> None:
    for rel, expected in reference.SOURCE_PINS.items():
        path = WORKSPACE / rel
        check(path.is_file(), f"missing source pin: {rel}", problems)
        if path.is_file():
            check(sha256_file(path) == expected, f"source pin mismatch: {rel}", problems)
    for rel, expected in reference.BOUNDARY_PINS.items():
        path = SDK_ROOT / rel
        check(path.is_file(), f"missing boundary pin: {rel}", problems)
        if path.is_file():
            check(sha256_file(path) == expected, f"boundary pin mismatch: {rel}", problems)


def check_contract(contract: Dict[str, Any], report: Dict[str, Any], problems: List[str]) -> None:
    check(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID, "contract schema mismatch", problems)
    check(contract.get("task") == reference.TASK, "contract task mismatch", problems)
    check(contract.get("component") == reference.COMPONENT, "contract component mismatch", problems)
    check(contract.get("decision") == "DEFER", "contract decision mismatch", problems)
    check(contract.get("status") == "proposal_only_not_qualified", "contract status mismatch", problems)
    q = contract.get("qualification", {})
    check(q.get("status") == "not_qualified", "contract qualification status mismatch", problems)
    check(q.get("readiness") == "incomplete", "contract readiness mismatch", problems)
    check(q.get("decision") == "DEFER", "contract qualification decision mismatch", problems)
    check(q.get("candidate_qualified") is False, "contract candidate_qualified mismatch", problems)
    check(q.get("proposal_only") is True, "contract proposal_only mismatch", problems)
    check(q.get("no_missing_result_qualifies_candidate") is True, "contract missing-result gate mismatch", problems)
    check(contract.get("release_gates") == report.get("release_gates"), "contract/report gates mismatch", problems)
    check(contract.get("boundary") == report.get("boundary"), "contract/report boundary mismatch", problems)
    check(contract.get("board_link") == report.get("board_link", {}).get("projection"), "contract board projection mismatch", problems)
    check(contract.get("inventory_link") == report.get("inventory_link", {}).get("projection"), "contract inventory projection mismatch", problems)


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") == reference.SCHEMA_ID, "report schema mismatch", problems)
    check(report.get("decision") == "DEFER", "report decision mismatch", problems)
    check(report.get("status") == "proposal_only_not_qualified", "report status mismatch", problems)
    check(report.get("qualification_status") == "not_qualified", "report qualification mismatch", problems)
    check(report.get("readiness") == "incomplete", "report readiness mismatch", problems)
    check(report.get("candidate_qualified") is False, "candidate must not be qualified", problems)
    check(report.get("proposal_only") is True, "report must be proposal_only", problems)
    check(report.get("no_missing_result_qualifies_candidate") is True, "missing result gate mismatch", problems)
    check(report.get("gates") == reference.GATE_IDS, "gate IDs mismatch", problems)
    check(report.get("remaining_gates") == reference.GATE_IDS, "remaining gates mismatch", problems)
    check(all(g.get("status") == "blocked" for g in report.get("release_gates", [])), "all release gates must be blocked", problems)
    ev = report.get("evidence", {})
    check(ev.get("path") == reference.EVIDENCE_PATH, "evidence path mismatch", problems)
    check(ev.get("line") == reference.EVIDENCE_LINE, "evidence line mismatch", problems)
    check(ev.get("text") == reference.EVIDENCE_TEXT, "evidence text mismatch", problems)
    check(ev.get("sha256") == reference.SOURCE_PINS[reference.EVIDENCE_PATH], "evidence digest mismatch", problems)
    adverse = report.get("adverse", {})
    check(adverse.get("invalid_requests_all_rejected") is True, "invalid requests must be rejected", problems)
    check(adverse.get("invalid_json_all_rejected") is True, "invalid json must be rejected", problems)
    check(adverse.get("reset_validation_matches_expectation") is True, "reset validation mismatch", problems)
    check(adverse.get("missing_result_qualifies_candidate") is False, "missing result must not qualify", problems)
    boundary = report.get("boundary", {})
    for key in ("provider_registered", "descriptor_registration", "enabled_by_default", "public_api_abi_changed", "registry_changed", "shared_cmake_changed", "ci_changed", "board_or_handoff_changed", "real_corpus_or_weights", "benchmark_claim", "release_claim", "runtime_execution_attempted"):
        check(boundary.get(key) is False, f"boundary {key} must be false", problems)
    for key in ("task_local_only", "opt_in_required", "installed_v0_unchanged"):
        check(boundary.get(key) is True, f"boundary {key} must be true", problems)


def check_sidecar(problems: List[str]) -> None:
    report_payload = REPORT_PATH.read_bytes()
    sidecar = SIDECAR_PATH.read_text(encoding="utf-8").strip()
    check(sidecar == sha256_bytes(report_payload) + "  report.json", "report sidecar mismatch", problems)


def check_sources(problems: List[str]) -> None:
    text = SOURCES_PATH.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.strip()]
    seen = set()
    for line in lines:
        if "  " not in line:
            problems.append(f"malformed SOURCES line: {line}")
            continue
        digest, rel = line.split("  ", 1)
        check(rel not in seen, f"duplicate SOURCES entry: {rel}", problems)
        seen.add(rel)
        if rel.startswith(reference.TASK_PREFIX):
            path = HERE / rel[len(reference.TASK_PREFIX):]
        elif rel.startswith("audio-benchmark-platform/") or rel.startswith("cpp-library/"):
            path = WORKSPACE / rel
        else:
            path = SDK_ROOT / rel
        check(path.is_file(), f"SOURCES missing path: {rel}", problems)
        if path.is_file():
            check(sha256_file(path) == digest, f"SOURCES digest mismatch: {rel}", problems)


def check_licensing(problems: List[str]) -> None:
    for name in ARTIFACT_FILES:
        path = HERE / name
        check(path.is_file(), f"missing artifact: {name}", problems)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        sidecar = HERE / (name + ".license")
        has_sidecar = sidecar.is_file()
        if path.suffix == ".py":
            body = "\n".join(text.splitlines()[2:])
            check("SPDX-License-" "Identifier:" not in body, f"full SPDX token in python body: {name}", problems)
            check(SPDX_COPYRIGHT in text, f"missing SPDX copyright: {name}", problems)
        else:
            check(SPDX_COPYRIGHT in text or has_sidecar, f"missing SPDX copyright/sidecar: {name}", problems)
    for name in SIDECAR_FILES:
        path = HERE / name
        check(path.is_file(), f"missing sidecar: {name}", problems)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            check(SPDX_LICENSE in text, f"sidecar missing SPDX license: {name}", problems)
            check(SPDX_COPYRIGHT in text, f"sidecar missing SPDX copyright: {name}", problems)


def check_prohibited(problems: List[str]) -> None:
    for path in HERE.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(HERE).as_posix()
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES, f"prohibited artifact present: {rel}", problems)


def check_git_scope(problems: List[str]) -> None:
    scope = reference.diff_scope(SDK_ROOT)
    check(scope["status"] != "scope_base_unavailable", "scope_base_unavailable", problems)
    if scope["status"] == "base_out_of_scope_change":
        for item in scope.get("out_of_scope_files", []):
            problems.append(f"base_out_of_scope_change: {item}")
    # Ensure every changed file is task-local
    for item in scope.get("changed_files", []):
        check(item.startswith(TASK_PREFIX), f"changed file outside task prefix: {item}", problems)


def check_readme_table(problems: List[str], report: Dict[str, Any]) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    check("| Gate | Status | Reason | Reopen condition |" in text, "README missing gate table header", problems)
    for gate in report.get("release_gates", []):
        row = f"| {gate['id']} {gate['gate']} | {gate['status']} |"
        check(row in text, f"README missing gate row: {gate['id']}", problems)
        check(gate["reason"] in text, f"README missing gate reason: {gate['id']}", problems)
        check(gate["reopen"] in text, f"README missing gate reopen: {gate['id']}", problems)
    check("DEFER" in text, "README missing DEFER decision", problems)
    check("not_qualified" in text, "README missing not_qualified", problems)


def check_determinism(problems: List[str]) -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="sdk-sox-tempo-verify-") as td:
        tmp = Path(td)
        # copy package to temp dir to avoid mutating worktree artifacts except deterministic regeneration
        pkg = tmp / "pkg"
        pkg.mkdir()
        for path in HERE.iterdir():
            if path.is_file():
                (pkg / path.name).write_bytes(path.read_bytes())
        env["SDK_SOX_TEMPO_SDK_ROOT"] = str(SDK_ROOT)
        env["SDK_SOX_TEMPO_WORKSPACE"] = str(WORKSPACE)
        cmd = [sys.executable, str(pkg / "run.py"), "--all"]
        digests = []
        for _ in range(3):
            subprocess.run(cmd, cwd=str(pkg), check=True, capture_output=True, text=True, env=env)
            digests.append({
                "report": sha256_file(pkg / "report.json"),
                "sidecar": sha256_file(pkg / "report.json.sha256"),
                "contract": sha256_file(pkg / "contract.json"),
                "sources": sha256_file(pkg / "SOURCES.sha256"),
            })
        check(all(d == digests[0] for d in digests), "3x regeneration not byte-identical", problems)
        # also ensure regenerated report matches canonical builder in temp copy context
        prev_sdk = os.environ.get("SDK_SOX_TEMPO_SDK_ROOT")
        prev_ws = os.environ.get("SDK_SOX_TEMPO_WORKSPACE")
        os.environ["SDK_SOX_TEMPO_SDK_ROOT"] = str(SDK_ROOT)
        os.environ["SDK_SOX_TEMPO_WORKSPACE"] = str(WORKSPACE)
        sys.path.insert(0, str(pkg))
        try:
            for mod in ("reference", "run"):
                sys.modules.pop(mod, None)
            import importlib
            ref = importlib.import_module("reference")
            importlib.reload(ref)
            expected = ref.canonical_text(ref.build_report()).encode("utf-8")
            check((pkg / "report.json").read_bytes() == expected, "regenerated report not canonical", problems)
        finally:
            if str(pkg) in sys.path:
                sys.path.remove(str(pkg))
            for mod in ("reference", "run"):
                sys.modules.pop(mod, None)
            if prev_sdk is None:
                os.environ.pop("SDK_SOX_TEMPO_SDK_ROOT", None)
            else:
                os.environ["SDK_SOX_TEMPO_SDK_ROOT"] = prev_sdk
            if prev_ws is None:
                os.environ.pop("SDK_SOX_TEMPO_WORKSPACE", None)
            else:
                os.environ["SDK_SOX_TEMPO_WORKSPACE"] = prev_ws


def main() -> int:
    problems: List[str] = []
    try:
        report = strict_load(REPORT_PATH)
        contract = strict_load(CONTRACT_PATH)
    except Exception as err:  # noqa: BLE001
        print(f"FAIL: load error: {err}")
        return 1
    check(isinstance(report, dict), "report root not object", problems)
    check(isinstance(contract, dict), "contract root not object", problems)
    if problems:
        for p in problems:
            print(f"FAIL: {p}")
        return 1
    check_report(report, problems)
    check_contract(contract, report, problems)
    check_sidecar(problems)
    check_pins(problems)
    check_sources(problems)
    check_licensing(problems)
    check_prohibited(problems)
    check_readme_table(problems, report)
    check_git_scope(problems)
    check_determinism(problems)
    if problems:
        for p in problems:
            print(f"FAIL: {p}")
        return 1
    report_payload = REPORT_PATH.read_bytes()
    print("PASS: SDK-SOX-TEMPO evidence verified")
    print(f"report_file_digest={sha256_bytes(report_payload)}")
    print(f"canonical_digest={sha256_bytes(reference.canonical_bytes(report))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
