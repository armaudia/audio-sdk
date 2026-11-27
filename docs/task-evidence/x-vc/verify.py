# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for SDK-X-VC evidence package.

Checks strict JSON, canonical bytes, exact pins, blocker semantics, stable
linked-row identity, licensing, prohibited artifacts, task-local merge-base git
scope and three cold-start byte-identical regenerations. It never writes
package evidence.
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
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
TASK_ID = reference.TASK
COMPONENT = reference.COMPONENT
GATE_IDS = ["RG-0" + str(n) for n in range(1, 9)]
EXPECTED_LINK = dict(reference.EXPECTED_LINK)
ARTIFACT_FILES = (
    "README.md", "LICENSES.md", "contract.json", "reference.py", "report.json",
    "report.json.sha256", "run.py", "SOURCES.sha256", "test_reference.py", "verify.py",
    "contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license",
)
SIDECAR_FILES = (
    "contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license",
)
PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx", ".pt", ".pth", ".ckpt",
    ".safetensors", ".bin", ".so", ".dylib", ".a", ".o", ".zip", ".tar", ".gz", ".whl",
}
WEIGHT_KEYS = ("x_vc_checkpoint", "glm_4_voice_tokenizer", "eres2net")


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
        return all(finite_json(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(v) for v in value)
    return True


def check(condition: bool, message: str, problems: List[str]) -> None:
    if not condition:
        problems.append(message)


def check_contract(contract: Dict[str, Any], report: Dict[str, Any], problems: List[str]) -> None:
    check(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID, "contract schema mismatch", problems)
    check(contract.get("task") == TASK_ID, "contract task mismatch", problems)
    check(contract.get("component") == COMPONENT, "contract component mismatch", problems)
    check(contract.get("branch") == reference.BRANCH, "contract branch mismatch", problems)
    check(contract.get("base_commit") == reference.BASE_COMMIT, "contract base commit mismatch", problems)
    check(contract.get("decision") == "DEFER", "contract decision not DEFER", problems)
    check(contract.get("status") == "proposal_only_not_qualified", "contract status mismatch", problems)
    q = contract.get("qualification", {})
    check(q.get("status") == "not_qualified" and q.get("readiness") == "incomplete", "contract qualification mismatch", problems)
    check(q.get("candidate_qualified") is False and q.get("upstream_parity") is False, "contract claims qualification/parity", problems)
    check(q.get("proposal_only") is True, "contract not proposal only", problems)
    check(contract.get("comparison_status") == "blocked_weights_and_runtime_absent", "contract comparison status mismatch", problems)
    b = contract.get("boundary", {})
    check(b == report.get("boundary"), "contract/report boundary differ", problems)
    check(b.get("installed_v0_unchanged") is True, "installed v0 changed", problems)
    check(b.get("public_api_abi_changed") is False, "public ABI changed", problems)
    check(b.get("provider_registered") is False, "provider registered", problems)
    check(b.get("descriptor_registration") is False, "descriptor registered", problems)
    check(b.get("enabled_by_default") is False, "enabled by default", problems)
    check(b.get("shared_cmake_changed") is False, "shared cmake changed", problems)
    check(b.get("ci_changed") is False, "ci changed", problems)
    check(b.get("board_or_handoff_changed") is False, "board/handoff changed", problems)
    check(b.get("real_corpus_or_weights") is False, "real corpus/weights claimed", problems)
    check(b.get("benchmark_claim") is False, "benchmark claim", problems)
    check(b.get("release_claim") is False, "release claim", problems)
    check(b.get("format") == {"sample_rate_hz": 16000, "channels": 1, "sample_format": "float32", "frame_samples": 160}, "v0 format mismatch", problems)
    blocker = contract.get("upstream_blocker", {})
    check(blocker.get("status") == "blocked_weights_and_runtime_absent", "upstream blocker status mismatch", problems)
    check((blocker.get("source") or {}).get("status") == "present_pinned", "source not present_pinned", problems)
    weights = blocker.get("weights") or {}
    check(weights.get("status") == "absent", "weights not absent", problems)
    for k in WEIGHT_KEYS:
        a = weights.get(k) or {}
        check(a.get("status") == "absent" and a.get("present") is False, f"weight {k} not absent", problems)
        check(a.get("sha256") is None and a.get("byte_count") is None, f"fabricated weight digest/count {k}", problems)
    check((blocker.get("runtime") or {}).get("status") == "absent_unpinned", "runtime not absent_unpinned", problems)
    check(blocker.get("runtime_digest") is None, "fabricated runtime digest", problems)
    check(blocker.get("no_upstream_parity_claim") is True, "parity not disabled", problems)
    gates = contract.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8, "contract must carry 8 gates", problems)
    if isinstance(gates, list):
        check([g.get("id") for g in gates] == GATE_IDS, "contract gate ids mismatch", problems)
        check(all(g.get("status") == "blocked" for g in gates), "contract gate not blocked", problems)
    check(contract.get("geometry") == report.get("geometry"), "contract/report geometry differ", problems)
    check(contract.get("dependency_resolution") == report.get("dependency_resolution"), "contract/report dependency_resolution differ", problems)
    check(contract.get("inventory_link") == report.get("inventory_link"), "contract/report inventory differ", problems)


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") == reference.SCHEMA_ID, "report schema mismatch", problems)
    check(report.get("task") == TASK_ID, "report task mismatch", problems)
    check(report.get("decision") == "DEFER", "report decision not DEFER", problems)
    check(report.get("status") == "proposal_only_not_qualified", "report status mismatch", problems)
    check(report.get("qualification_status") == "not_qualified", "report qualification_status mismatch", problems)
    q = report.get("qualification", {})
    check(q.get("status") == "not_qualified" and q.get("readiness") == "incomplete" and q.get("candidate_qualified") is False, "report qualification mismatch", problems)
    check(report.get("profile", {}).get("name") == "voice", "profile not voice", problems)
    src = report.get("source_probe", {})
    check(src.get("status") == "present_pinned" and src.get("present") is True, "source probe mismatch", problems)
    check(src.get("revision") == reference.SOURCE_REVISION, "source revision mismatch", problems)
    check(src.get("license") == "MIT", "source license mismatch", problems)
    wts = report.get("weights_probe", {})
    check(wts.get("status") == "blocked_weights_absent" and wts.get("present") is False, "weights probe mismatch", problems)
    check(wts.get("sha256") is None and wts.get("byte_count") is None, "weights probe fabricated identity", problems)
    for k in WEIGHT_KEYS:
        a = wts.get(k) or {}
        check(a.get("present") is False and a.get("status") == "absent", f"weights probe {k} not absent", problems)
    check((wts.get("name_search") or {}).get("truncated") is False, "name search truncated", problems)
    hc = (wts.get("home_cache") or {}).get("huggingface") or {}
    mc = (wts.get("home_cache") or {}).get("modelscope") or {}
    check(hc.get("matches") == [] and mc.get("matches") == [], "dependency cache match appeared", problems)
    rt = report.get("runtime_probe", {})
    check(rt.get("status") == "blocked_runtime_unpinned" and rt.get("pinned") is False, "runtime probe mismatch", problems)
    check(not any((rt.get("importable_modules") or {}).get(m) for m in ["torch", "torchaudio", "transformers"]), "runtime module unexpectedly importable", problems)
    geom = report.get("geometry", {})
    check(geom.get("semantic_tokenizer_repository") == reference.GLM_TOKENIZER_REPO, "geometry tokenizer mismatch", problems)
    check(geom.get("speaker_embedding_dim") == 192 and geom.get("semantic_feature_width") == 1280, "geometry dims mismatch", problems)
    check(geom.get("measured_here") is False and geom.get("candidate_output") is False, "geometry claims measurement/output", problems)
    check(geom.get("declared_requirements") == reference.EXPECTED_REQUIREMENTS, "declared requirements mismatch", problems)
    hist = report.get("historical_evidence", {})
    check(hist.get("status") == "no_local_xvc_execution_record" and hist.get("records_found") == 0, "historical evidence mismatch", problems)
    check(hist.get("reproduced_here") is False and hist.get("qualifies_candidate") is False, "historical evidence claimed", problems)
    cand = report.get("candidates", {}).get("x-vc", {})
    check(cand.get("status") == "blocked_weights_and_runtime_absent" and cand.get("qualifies_candidate") is False, "candidate status mismatch", problems)
    check(cand.get("metrics") is None, "candidate has metrics", problems)
    adverse = report.get("adverse", {})
    check((adverse.get("invalid_config_and_input") or {}).get("all_rejected") is True, "invalid requests accepted", problems)
    check((adverse.get("invalid_config_and_input") or {}).get("dependency_case_count", 0) >= 7, "dependency case count too small", problems)
    check((adverse.get("invalid_json_numeric_fields") or {}).get("all_rejected") is True, "invalid json accepted", problems)
    check((adverse.get("reset_validation") or {}).get("matches_expectation") is True, "reset validation mismatch", problems)
    check((adverse.get("missing_result") or {}).get("qualifies_candidate") is False, "missing result qualifies", problems)
    checks = report.get("local_harness_checks", {})
    check(isinstance(checks, dict) and len(checks) >= 15 and all(v is True for v in checks.values()), "local harness checks not all true", problems)
    gates = report.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8, "report must carry 8 gates", problems)
    if isinstance(gates, list):
        check([g.get("id") for g in gates] == GATE_IDS, "report gate ids mismatch", problems)
        check(all(g.get("status") == "blocked" for g in gates), "report gate not blocked", problems)
    check(report.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing", problems)
    check(report.get("regression_count") == 0 and report.get("regressions") == [], "regression fields not empty", problems)


def check_pins(contract: Dict[str, Any], report: Dict[str, Any], problems: List[str]) -> int:
    pins = contract.get("artifact_pins", {})
    expected_names = tuple(n for n in ARTIFACT_FILES if n != "contract.json")
    check(set(pins) == set(expected_names), "contract artifact pin set mismatch", problems)
    for name, digest in pins.items():
        path = HERE / name
        check(path.is_file(), "missing artifact: " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest, "artifact pin mismatch: " + name, problems)
    check(pins.get("report.json") == sha256_file(REPORT_PATH), "report pin mismatch", problems)
    sidecar = SIDECAR_PATH.read_text(encoding="ascii")
    check(sidecar == (sha256_file(REPORT_PATH) + "  report.json\n"), "report sidecar mismatch", problems)
    for path, digest in report.get("source_pins", {}).items():
        target = WORKSPACE / path
        check(target.is_file(), "missing source pin target: " + path, problems)
        if target.is_file():
            check(sha256_file(target) == digest, "source pin mismatch: " + path, problems)
        check(path != "audio-benchmark-platform/plan/swarm/TASKS.json", "mutable TASKS.json pinned", problems)
    for path, digest in report.get("boundary_pins", {}).items():
        target = SDK_ROOT / path
        check(target.is_file(), "missing boundary pin target: " + path, problems)
        if target.is_file():
            check(sha256_file(target) == digest, "boundary pin mismatch: " + path, problems)
    sources = SOURCES_PATH.read_text(encoding="utf-8")
    check("audio-benchmark-platform/plan/swarm/TASKS.json" not in sources, "TASKS.json appears in SOURCES.sha256", problems)
    for path, digest in report.get("source_pins", {}).items():
        check((digest + "  source:" + path) in sources, "source pin missing from SOURCES: " + path, problems)
    for path, digest in report.get("boundary_pins", {}).items():
        check((digest + "  " + path) in sources, "boundary pin missing from SOURCES: " + path, problems)
    for name in ARTIFACT_FILES:
        if name in ("contract.json", "SOURCES.sha256"):
            continue
        if (HERE / name).is_file():
            check((sha256_file(HERE / name) + "  " + TASK_PREFIX + name) in sources, "manifest pin missing from SOURCES: " + name, problems)
    return len(pins) + len(report.get("source_pins", {})) + len(report.get("boundary_pins", {}))


def check_board(contract: Dict[str, Any], report: Dict[str, Any], problems: List[str]) -> None:
    board = strict_load(BOARD_PATH)
    check(isinstance(board, dict) and isinstance(board.get("tasks"), list), "TASKS.json shape invalid", problems)
    rows = [row for row in board.get("tasks", []) if isinstance(row, dict) and row.get("id") == TASK_ID]
    check(len(rows) == 1, "linked task row missing/duplicated", problems)
    if len(rows) != 1:
        return
    stable = {k: rows[0].get(k if k != "task_id" else "id") for k in reference.LINK_FIELDS}
    check(stable == EXPECTED_LINK, "stable linked-row identity changed", problems)
    check(report.get("board_links") == [stable], "report board projection mismatch", problems)
    expected = sha256_bytes(canonical_bytes([stable]))
    check(report.get("board_link_projection_sha256") == expected, "board projection digest mismatch", problems)
    check(contract.get("board_links") == [stable] and contract.get("board_link_projection_sha256") == expected, "contract board projection mismatch", problems)
    for mutable in ("status", "owner", "review", "handoff", "claim", "history", "blocked_reason"):
        check(mutable in report.get("board_mutable_fields_excluded", []), "mutable field not excluded: " + mutable, problems)


def check_inventory(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("inventory_link") == reference.EXPECTED_INVENTORY, "inventory link mismatch", problems)
    entry = report.get("evidence_entry", {})
    check(entry.get("line") == 20, "evidence line mismatch", problems)
    for token in ("X-VC", "5.01 GB", "GLM-4-Voice", "ERes2Net", "8 GB memory budget"):
        check(token in str(entry.get("text")), "evidence token missing: " + token, problems)


def check_licensing(problems: List[str]) -> None:
    for name in SIDECAR_FILES:
        path = HERE / name
        check(path.is_file(), "missing SPDX sidecar: " + name, problems)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            check("SPDX-FileCopyrightText:" in text, "sidecar lacks copyright: " + name, problems)
            check(SPDX_NEEDLE in text, "sidecar lacks Apache-2.0: " + name, problems)
    for name in ("README.md", "LICENSES.md", "reference.py", "run.py", "test_reference.py", "verify.py"):
        path = HERE / name
        check(path.is_file(), "missing package file: " + name, problems)
        if path.is_file():
            check(SPDX_NEEDLE in path.read_text(encoding="utf-8"), "missing SPDX header: " + name, problems)
    for path in HERE.iterdir():
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES, "prohibited binary/audio artifact: " + path.name, problems)


def check_absent(problems: List[str]) -> None:
    src = reference.source_probe()
    check(src.get("present") is True and src.get("status") == "present_pinned", "pinned X-VC source not present", problems)
    wts = reference.weights_probe()
    check(wts.get("present") is False, "dependency weight appeared; blocker package must be revisited", problems)
    rt = reference.runtime_probe()
    check(rt.get("pinned") is False, "pinned runtime appeared; blocker package must be revisited", problems)


def check_reproduction(report_payload: bytes, problems: List[str]) -> bool:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONHASHSEED"] = "0"
    process = subprocess.run([sys.executable, str(HERE / "run.py"), "--stdout-report"], cwd=str(HERE), capture_output=True, env=env, check=False)
    if process.returncode != 0:
        problems.append("in-process report regeneration failed")
        return False
    check(process.stdout == report_payload, "in-process report bytes differ", problems)
    return process.stdout == report_payload


def check_cold_starts(problems: List[str]) -> int:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONHASHSEED"] = "0"
    outputs: List[bytes] = []
    for _ in range(3):
        process = subprocess.run([sys.executable, str(HERE / "run.py"), "--verify-repro"], cwd=str(HERE), capture_output=True, env=env, check=False)
        if process.returncode != 0:
            problems.append("cold-start regeneration failed: " + process.stdout.decode("utf-8", "replace") + process.stderr.decode("utf-8", "replace"))
            continue
        outputs.append(process.stdout)
    check(len(outputs) == 3, "fewer than three cold starts succeeded", problems)
    if outputs:
        check(all(o == outputs[0] for o in outputs), "cold-start outputs differ", problems)
        check(b"ok=1\n" in outputs[0], "cold-start reproduction not ok", problems)
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
    reproduction_ok = False
    repeats = 0
    pins_checked = 0
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
        check_inventory(report, problems)
        check_licensing(problems)
        check_absent(problems)
        reproduction_ok = check_reproduction(report_payload, problems)
        repeats = check_cold_starts(problems)
        check_git_scope(problems)
        check(report_payload.endswith(b"\n") and not report_payload.endswith(b"\n\n"), "report must have exactly one trailing newline", problems)
        check(finite_json(report), "report contains nonfinite value", problems)
        check(finite_json(contract), "contract contains nonfinite value", problems)
        check(canonical_bytes(report) + b"\n" == report_payload, "report bytes not canonical", problems)
    except (OSError, VerificationError, ValueError, KeyError, TypeError) as error:
        problems.append("verification exception: " + str(error))
    if problems:
        for problem in problems:
            print("FAIL: " + problem)
        print("verification_failed=" + str(len(problems)))
        return 1
    print("pins_ok=" + str(pins_checked) + " reproduction_ok=" + str(int(reproduction_ok)) + " repeats_ok=" + str(repeats) +
          " semantics_ok=1 boundary_ok=1 licensing_ok=1 git_scope_ok=1 absent_source_weights_ok=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
