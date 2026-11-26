# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the SDK-PSDN-ZERO-SHOT-AC evidence package.

Checks strict JSON, canonical bytes, exact pins, blocker semantics, stable
linked-row identity, licensing, prohibited artifacts, merge-base git scope and
three cold-start byte-identical regenerations. Never writes package evidence.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List, Tuple

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_PREFIX = reference.TASK_PREFIX
TASK_ID = reference.TASK
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
GATE_IDS = [f"RG-{i:02d}" for i in range(1, 9)]
ARTIFACT_FILES = (
    "README.md", "LICENSES.md", "contract.json", "reference.py", "report.json",
    "report.json.sha256", "run.py", "SOURCES.sha256", "test_reference.py", "verify.py",
    "contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license",
)
SIDECAR_FILES = ("contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license")
PROHIBITED_SUFFIXES = {".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx", ".pt", ".pth", ".ckpt", ".safetensors", ".bin", ".so", ".dylib", ".a", ".o", ".zip", ".tar", ".gz", ".whl"}
BLOCKER_KEYS = {
    "status", "artifact", "source", "weights", "runtime", "expected_license", "pinned_revision",
    "source_digest", "runtime_digest", "no_upstream_parity_claim", "rights_requirement",
    "workspace_search", "not_attempted", "reopen",
}


class VerificationError(AssertionError):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def strict_load(path: Path) -> Any:
    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise VerificationError("duplicate JSON key in " + path.name)
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise VerificationError("nonfinite JSON constant in " + path.name + ": " + token)

    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as error:
        raise VerificationError("invalid JSON in " + path.name + ": " + str(error))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(i) for i in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(i) for i in value)
    return True


def check(condition: bool, message: str, problems: List[str]) -> None:
    if not condition:
        problems.append(message)


def check_contract(contract: Dict[str, Any], report: Dict[str, Any], problems: List[str]) -> None:
    check(contract.get("schema_id") == reference.CONTRACT_SCHEMA, "contract schema mismatch", problems)
    check(contract.get("contract_version") == "0.1", "contract version mismatch", problems)
    check(contract.get("task") == TASK_ID, "contract task mismatch", problems)
    check(contract.get("component") == reference.COMPONENT, "contract component mismatch", problems)
    check(contract.get("branch") == reference.BRANCH, "contract branch mismatch", problems)
    check(contract.get("base_commit") == reference.BASE_COMMIT, "contract base commit mismatch", problems)
    check(contract.get("decision") == "DEFER", "contract decision is not DEFER", problems)
    check(contract.get("status") == "proposal_only_not_qualified", "contract status mismatch", problems)
    q = contract.get("qualification", {})
    check(q.get("status") == "not_qualified", "contract qualification not_qualified mismatch", problems)
    check(q.get("readiness") == "incomplete", "contract readiness mismatch", problems)
    check(q.get("decision") == "DEFER", "contract qualification decision mismatch", problems)
    check(q.get("candidate_qualified") is False, "contract claims qualified candidate", problems)
    check(q.get("upstream_parity") is False, "contract claims upstream parity", problems)
    check(q.get("all_required_results_present") is False, "contract claims all required results present", problems)
    check(q.get("proposal_only") is True, "contract not proposal only", problems)
    check(contract.get("comparison_status") == "blocked_source_weights_runtime_absent", "contract comparison status mismatch", problems)
    boundary = contract.get("boundary", {})
    check(boundary == report.get("boundary"), "contract and report boundary differ", problems)
    check(boundary.get("installed_v0_unchanged") is True, "installed v0 boundary changed", problems)
    check(boundary.get("public_api_abi_changed") is False, "public ABI boundary changed", problems)
    check(boundary.get("provider_registered") is False, "provider registered", problems)
    check(boundary.get("descriptor_registration") is False, "descriptor registered", problems)
    check(boundary.get("enabled_by_default") is False, "provider enabled by default", problems)
    check(boundary.get("shared_cmake_changed") is False, "shared CMake changed", problems)
    check(boundary.get("ci_changed") is False, "CI changed", problems)
    check(boundary.get("board_or_handoff_changed") is False, "board or handoff changed", problems)
    check(boundary.get("real_corpus_or_weights") is False, "real corpus or weights claimed", problems)
    check(boundary.get("benchmark_claim") is False, "benchmark claim present", problems)
    check(boundary.get("release_claim") is False, "release claim present", problems)
    check(boundary.get("format") == {"sample_rate_hz": 16000, "channels": 1, "sample_format": "float32", "frame_samples": 160}, "contract v0 format mismatch", problems)
    blocker = contract.get("upstream_blocker", {})
    check(set(blocker.keys()) == BLOCKER_KEYS, "upstream blocker schema mismatch", problems)
    check(blocker.get("status") == "blocked_source_weights_runtime_rights_absent", "upstream blocker status mismatch", problems)
    check((blocker.get("source") or {}).get("status") == "absent", "source not recorded absent", problems)
    check((blocker.get("source") or {}).get("revision") is None, "fabricated source revision", problems)
    check((blocker.get("source") or {}).get("tree_digest") is None, "fabricated source digest", problems)
    check((blocker.get("weights") or {}).get("status") == "absent", "weights not recorded absent", problems)
    check((blocker.get("runtime") or {}).get("status") == "blocked_runtime_unpinned", "runtime status mismatch", problems)
    check(blocker.get("no_upstream_parity_claim") is True, "upstream parity claim present", problems)
    gates = contract.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8, "release gates count mismatch", problems)
    check([g.get("id") for g in gates] == GATE_IDS, "release gate IDs mismatch", problems)
    check(all(g.get("status") == "blocked" and g.get("qualifies") is False for g in gates), "release gate not blocked/nonqualifying", problems)


def check_pins(contract: Dict[str, Any], report: Dict[str, Any], problems: List[str]) -> int:
    pins_checked = 0
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        target = WORKSPACE / path
        check(target.is_file(), "missing source pin target: " + path, problems)
        if target.is_file():
            check(sha256_file(target) == digest, "source pin changed: " + path, problems)
            pins_checked += 1
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        target = SDK_ROOT / path
        check(target.is_file(), "missing boundary pin target: " + path, problems)
        if target.is_file():
            check(sha256_file(target) == digest, "boundary pin changed: " + path, problems)
            pins_checked += 1
    artifact_pins = contract.get("artifact_pins", {})
    for name, digest in sorted(artifact_pins.items()):
        target = HERE / name
        check(target.is_file(), "missing artifact pin target: " + name, problems)
        if target.is_file():
            actual = sha256_file(target)
            check(actual == digest, "artifact pin mismatch: " + name, problems)
            pins_checked += 1
    report_artifacts = report.get("artifact_pins", {})
    for name, digest in report_artifacts.items():
        target = HERE / name
        if target.is_file():
            check(sha256_file(target) == digest, "report artifact pin mismatch: " + name, problems)
            pins_checked += 1
    sidecar = SIDECAR_PATH.read_text(encoding="utf-8") if SIDECAR_PATH.is_file() else ""
    check(sidecar == sha256_file(REPORT_PATH) + "  report.json\n", "sidecar mismatch", problems)
    pins_checked += 1
    return pins_checked


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") == reference.REPORT_SCHEMA, "report schema mismatch", problems)
    check(report.get("task") == TASK_ID, "report task mismatch", problems)
    check(report.get("component") == reference.COMPONENT, "report component mismatch", problems)
    check(report.get("decision") == "DEFER", "report decision mismatch", problems)
    check(report.get("qualification_status") == "not_qualified", "report qualification_status mismatch", problems)
    check(report.get("status") == "proposal_only_not_qualified", "report status mismatch", problems)
    gates = report.get("gates") or report.get("release_gates") or []
    check([g.get("id") for g in gates] == GATE_IDS, "report gate IDs mismatch", problems)
    check(all(g.get("status") == "blocked" for g in gates), "report gate not blocked", problems)
    check(report.get("no_missing_result_qualifies_candidate") is True, "missing result qualifies", problems)
    cand = (report.get("candidates") or {}).get(reference.COMPONENT, {})
    check(cand.get("qualifies_candidate") is False, "candidate qualifies", problems)
    check(cand.get("metrics") is None, "candidate metrics present", problems)
    adverse = report.get("adverse", {})
    inv = adverse.get("invalid_config_and_input", {})
    js = adverse.get("invalid_json_numeric_fields", {})
    miss = adverse.get("missing_result", {})
    reset = adverse.get("reset_validation", {})
    check(inv.get("all_rejected") is True and inv.get("accepted_count") == 0, "invalid config/input not rejected", problems)
    check(js.get("all_rejected") is True and js.get("accepted_count") == 0, "invalid json not rejected", problems)
    check(miss.get("qualifies_candidate") is False and miss.get("status") == "blocked", "missing result qualifies", problems)
    check(reset.get("matches_expectation") is True and reset.get("state_owned") is False, "reset validation mismatch", problems)
    check(report.get("historical_evidence", {}).get("qualifies") is False, "historical evidence qualifies", problems)
    check(report.get("reference", {}).get("real_psdn_source_present") is False, "source present", problems)
    check(report.get("reference", {}).get("real_psdn_weights_present") is False, "weights present", problems)
    check(report.get("reference", {}).get("pinned_runtime_present") is False, "runtime present", problems)
    links, digest = reference.board_link_projection()
    check(report.get("board_links") == links, "board links mismatch", problems)
    check(report.get("board_link_projection_sha256") == digest, "board link digest mismatch", problems)
    check(report.get("inventory_link") == reference.EXPECTED_INVENTORY, "inventory link mismatch", problems)
    entry = report.get("evidence_entry", {})
    check(entry.get("path") == reference.EVIDENCE_PATH, "evidence path mismatch", problems)
    check(entry.get("line") == reference.EVIDENCE_LINE, "evidence line mismatch", problems)
    check(entry.get("text") == reference.EVIDENCE_TEXT, "evidence text mismatch", problems)
    check(entry.get("sha256") == reference.SOURCE_PINS[reference.EVIDENCE_PATH], "evidence sha mismatch", problems)


def check_board(contract: Dict[str, Any], report: Dict[str, Any], problems: List[str]) -> None:
    if not BOARD_PATH.is_file():
        problems.append("board file missing")
        return
    board = strict_load(BOARD_PATH)
    tasks = board.get("tasks") if isinstance(board, dict) else None
    if not isinstance(tasks, list):
        problems.append("board tasks missing")
        return
    row = None
    for task in tasks:
        if isinstance(task, dict) and task.get("id") == TASK_ID:
            row = task
            break
    check(row is not None, "board row missing", problems)
    if row is None:
        return
    projection = {k: row.get(k) for k in reference.LINK_FIELDS}
    expected = {k: reference.LINKED_ROWS[0][k] for k in reference.LINK_FIELDS}
    check(projection == expected, "board projection mismatch", problems)
    check(contract.get("board_links")[0] == expected, "contract linked row mismatch", problems)
    check(report.get("board_links")[0] == expected, "report linked row mismatch", problems)


def check_licensing(problems: List[str]) -> None:
    for name in ARTIFACT_FILES:
        path = HERE / name
        check(path.is_file(), "missing artifact: " + name, problems)
        if not path.is_file():
            continue
        if name.endswith(".license"):
            content = path.read_text(encoding="utf-8")
            spdx = "SPDX-License-" + "Identifier: Apache-2.0"
            check(SPDX_NEEDLE in content or spdx in content, "missing SPDX in " + name, problems)
            continue
        if path.suffix in {".json", ".sha256"} or name == "SOURCES.sha256":
            lic = HERE / (name + ".license")
            check(lic.is_file(), "missing sidecar license for " + name, problems)
            continue
        head = path.read_text(encoding="utf-8", errors="replace")[:400]
        spdx = "SPDX-License-" + "Identifier: Apache-2.0"
        check(SPDX_NEEDLE in head or spdx in head, "missing SPDX in " + name, problems)
    contiguous = "SPDX" + "-License-" + "Identifier:"
    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        for lineno, line in enumerate((HERE / name).read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            if contiguous in line:
                problems.append("contiguous SPDX token in python string literal: %s:%d" % (name, lineno))


def check_absent(problems: List[str]) -> None:
    for path in HERE.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(HERE)
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES, "prohibited artifact present: " + str(rel), problems)
        name = path.name.lower()
        for needle in ("psdn", "weights", "checkpoint", "model"):
            if needle in name and name not in {p.name.lower() for p in HERE.iterdir()}:
                # allow package files named by task; flag suspicious model artifacts
                pass
    # specific suspicious patterns
    for pat in ("*.pt", "*.pth", "*.onnx", "*.safetensors", "*.ckpt", "*.wav", "*.flac", "*.mp3"):
        for found in HERE.glob(pat):
            problems.append("prohibited artifact present: " + found.name)


def check_reproduction(report_payload: bytes, problems: List[str]) -> bool:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.run([sys.executable, str(HERE / "run.py"), "--stdout-report"], cwd=str(HERE), capture_output=True, env=environment, check=False)
    if process.returncode != 0:
        problems.append("in-process report regeneration failed")
        return False
    check(process.stdout == report_payload, "in-process report bytes differ", problems)
    return process.stdout == report_payload


def check_cold_starts(problems: List[str]) -> int:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    outputs: List[bytes] = []
    for _ in range(3):
        process = subprocess.run([sys.executable, str(HERE / "run.py"), "--verify-repro"], cwd=str(HERE), capture_output=True, env=environment, check=False)
        if process.returncode != 0:
            problems.append("cold-start regeneration failed: " + process.stdout.decode("utf-8", "replace") + process.stderr.decode("utf-8", "replace"))
            continue
        outputs.append(process.stdout)
    check(len(outputs) == 3, "fewer than three cold starts succeeded", problems)
    if outputs:
        check(all(o == outputs[0] for o in outputs), "cold-start outputs differ", problems)
        check(b"ok=1\n" in outputs[0], "cold-start reproduction is not ok", problems)
    return len(outputs)


def check_git_scope(problems: List[str]) -> None:
    process = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=str(SDK_ROOT), capture_output=True, text=True, check=False)
    if process.returncode != 0:
        problems.append("git status failed in the SDK worktree")
        return
    for line in process.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        check(path.startswith(TASK_PREFIX), "change outside task-local scope: " + path, problems)
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        problems.append("scope_base_unavailable")
        return
    try:
        paths = reference.scope_changed_paths(SDK_ROOT, base)
    except ValueError as error:
        problems.append(str(error))
        return
    for path in reference.scope_violations(paths):
        problems.append("base_out_of_scope_change: " + path)


def main() -> int:
    problems: List[str] = []
    try:
        contract = strict_load(CONTRACT_PATH)
        report = strict_load(REPORT_PATH)
        report_payload = REPORT_PATH.read_bytes()
        check(isinstance(contract, dict), "contract root is not an object", problems)
        check(isinstance(report, dict), "report root is not an object", problems)
        check_contract(contract, report, problems)
        pins_checked = check_pins(contract, report, problems)
        check_report(report, problems)
        check_board(contract, report, problems)
        check_licensing(problems)
        check_absent(problems)
        reproduction_ok = check_reproduction(report_payload, problems)
        repeats = check_cold_starts(problems)
        check_git_scope(problems)
        check(report_payload.endswith(b"\n") and not report_payload.endswith(b"\n\n"), "report must have exactly one trailing newline", problems)
        check(finite_json(report), "report contains a nonfinite value", problems)
        check(finite_json(contract), "contract contains a nonfinite value", problems)
        check(canonical_bytes(report) + b"\n" == report_payload, "report bytes are not canonical", problems)
    except (OSError, VerificationError, ValueError, KeyError, TypeError) as error:
        problems.append("verification exception: " + str(error))
        reproduction_ok = False
        repeats = 0
        pins_checked = 0
    if problems:
        for problem in problems:
            print("FAIL: " + problem)
        print("verification_failed=" + str(len(problems)))
        return 1
    print("pins_ok=" + str(pins_checked) + " reproduction_ok=" + str(int(reproduction_ok)) + " repeats_ok=" + str(repeats) + " semantics_ok=1 boundary_ok=1 licensing_ok=1 git_scope_ok=1 absent_source_weights_ok=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
