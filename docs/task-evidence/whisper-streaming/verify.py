# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for SDK-WHISPER-STREAMING blocker evidence.

Checks strict JSON, canonical bytes, digests, pins, semantics, licensing,
git scope (newest merge-base origin/main/main, fail-closed), README digest
table, and three cold-start byte-identical regenerations. Writes only temp dirs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
SOURCES = HERE / "SOURCES.sha256"
README = HERE / "README.md"

# REUSE-IgnoreStart
SPDX_LICENSE = "SPDX-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd

SIDECARS = [
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
]
FORBIDDEN_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".m4a", ".mp4", ".pcap",
    ".onnx", ".pt", ".pth", ".bin", ".safetensors", ".ckpt", ".model",
    ".so", ".dylib", ".dll", ".a", ".o", ".exe", ".wasm", ".zip", ".tar", ".gz",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def check(condition: bool, msg: str, problems: List[str]) -> None:
    if not condition:
        problems.append(msg)


def strict_load(path: Path, problems: List[str]) -> Any | None:
    try:
        return reference.read_strict_json(path)
    except Exception as exc:  # noqa: BLE001
        problems.append(f"strict_json:{path.name}:{exc}")
        return None


def check_pins(problems: List[str]) -> int:
    checked = 0
    for rel, expected in sorted(reference.SOURCE_PINS.items()):
        path = reference.SOURCE_ROOT / rel
        if not path.is_file():
            problems.append("source_pin_missing:" + rel)
            continue
        actual = sha256_file(path)
        if actual != expected:
            problems.append("source_pin_mismatch:" + rel)
        else:
            checked += 1
    for rel, expected in sorted(reference.BOUNDARY_PINS.items()):
        path = SDK_ROOT / rel
        if not path.is_file():
            problems.append("boundary_pin_missing:" + rel)
            continue
        actual = sha256_file(path)
        if actual != expected:
            problems.append("boundary_pin_mismatch:" + rel)
        else:
            checked += 1
    return checked


def check_report_contract(report: Dict[str, Any], contract: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("task_id") == reference.TASK, "task_id mismatch", problems)
    check(report.get("component") == reference.COMPONENT, "component mismatch", problems)
    check(report.get("profile") == "rate", "profile mismatch", problems)
    check(report.get("decision") == "DEFER", "decision not DEFER", problems)
    check(report.get("status") == "proposal_only_incomplete", "status mismatch", problems)
    check(report.get("evidence_status") == "incomplete", "evidence_status mismatch", problems)
    check(report.get("qualification_status") == "not_qualified", "qualification_status mismatch", problems)
    check(report.get("proposal_only") is True, "proposal_only not true", problems)
    check(report.get("base_commit") == reference.BASE_COMMIT, "base_commit mismatch", problems)
    check(report.get("branch") == reference.BRANCH, "branch mismatch", problems)
    check(report.get("worktree") == reference.CLAIM_WORKTREE, "worktree mismatch", problems)
    check(report.get("reviewer") == reference.REVIEWER, "reviewer mismatch", problems)

    q = report.get("qualification", {})
    check(q.get("status") == "not_qualified", "qualification.status mismatch", problems)
    check(q.get("candidate_qualified") is False, "candidate_qualified not false", problems)
    check(q.get("all_release_gates_blocked") is True, "all_release_gates_blocked not true", problems)
    check(q.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing", problems)
    check(q.get("blocked_gate_count") == 8, "blocked_gate_count mismatch", problems)

    gates = report.get("gates", [])
    check(len(gates) == 8, "gate count mismatch", problems)
    check(all(g.get("status") == "blocked" for g in gates), "gate not blocked", problems)
    check(all(g.get("qualifies") is False for g in gates), "gate qualifies", problems)
    blockers = report.get("exact_blockers", [])
    check(len(blockers) == 8, "blocker count mismatch", problems)
    check(all(b.get("state") for b in blockers), "blocker missing state", problems)

    check(report.get("boundary") == contract.get("boundary"), "boundary mismatch", problems)
    check(report.get("scope") == contract.get("scope"), "scope mismatch", problems)
    check(report.get("non_claims") == contract.get("non_claims"), "non_claims mismatch", problems)
    check(report.get("gates") == contract.get("gates"), "gates mismatch", problems)
    check(report.get("exact_blockers") == contract.get("exact_blockers"), "exact_blockers mismatch", problems)
    check(report.get("rate_profile",{}).get("rows") == contract.get("rate_profile_requirements"), "report/contract mismatch:rate_profile", problems)
    check(report.get("quality_outcomes",{}).get("rows") == contract.get("quality_outcomes"), "report/contract mismatch:quality_outcomes", problems)
    check(report.get("timing",{}).get("rows") == contract.get("timing_requirements"), "report/contract mismatch:timing", problems)
    check(report.get("contract_sha256") == reference.object_digest(contract), "contract sha mismatch", problems)

    boundary = report.get("boundary", {})
    for k, v in reference.BOUNDARY.items():
        check(boundary.get(k) == v, f"boundary {k} mismatch", problems)
    scope = report.get("scope", {})
    for k, v in reference.SCOPE.items():
        check(scope.get(k) == v, f"scope {k} mismatch", problems)

    tri = report.get("task_row_identity", {})
    check(tri.get("whole_file_hashed") is False, "whole_file_hashed not false", problems)
    check(tri.get("stable_sha256") == reference.TASK_ROW_STABLE_SHA256, "task row sha mismatch", problems)
    check(tri.get("stable_fields") == reference.TASK_ROW_STABLE_FIELDS, "task row fields mismatch", problems)
    check(set(tri.get("excluded_mutable_fields", [])) == set(reference.MUTABLE_TASK_FIELDS), "mutable fields mismatch", problems)

    presence = report.get("source_presence", {})
    check(presence.get("all_absence_probes_absent") is True, "absence probes not all absent", problems)
    check(presence.get("model_executed") is False, "model_executed true", problems)
    check(presence.get("weights_used") is False, "weights_used true", problems)
    check(presence.get("runtime_imported") is False, "runtime_imported true", problems)
    check(presence.get("audio_read") is False, "audio_read true", problems)

    controls = report.get("controls", {})
    check(controls.get("adverse_all_rejected") is True, "adverse_all_rejected false", problems)
    check(controls.get("missing_result_never_qualifies") is True, "missing_result guard false", problems)
    for case in controls.get("adverse", []):
        check(case.get("result") == "rejected", f"adverse not rejected:{case.get('id')}", problems)
        check(case.get("qualifies") is False, f"adverse qualifies:{case.get('id')}", problems)

    doc = report.get("documented_context", {})
    check(doc.get("provenance_only") is True, "documented not provenance_only", problems)
    check(doc.get("reproduced_here") is False, "documented reproduced_here", problems)
    check(doc.get("used_for_evidence") is False, "documented used_for_evidence", problems)
    check(doc.get("qualifies") is False, "documented qualifies", problems)


def check_board_identity(report: Dict[str, Any], contract: Dict[str, Any], problems: List[str]) -> None:
    board_path = reference.SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    if not board_path.is_file():
        problems.append("board_missing")
        return
    board = strict_load(board_path, problems)
    if not isinstance(board, dict):
        return
    rows = [r for r in board.get("tasks", []) if isinstance(r, dict) and r.get("id") == reference.TASK]
    if len(rows) != 1:
        problems.append("board_row_missing_or_duplicated")
        return
    row = rows[0]
    stable = {f: row.get(f) for f in reference.STABLE_TASK_FIELDS}
    digest = reference.object_digest(stable)
    check(report["task_row_identity"]["stable_sha256"] == digest, "report stale task row digest", problems)
    check(contract["task_row_identity"]["stable_sha256"] == digest, "contract stale task row digest", problems)
    check(report["task_row_identity"]["stable_fields"] == stable, "report stable fields differ", problems)
    claim = row.get("claim") or {}
    check(claim.get("base_commit") == reference.BASE_COMMIT, "board base_commit differs", problems)
    check(claim.get("branch") == reference.BRANCH, "board branch differs", problems)
    check(claim.get("worktree") == reference.CLAIM_WORKTREE, "board worktree differs", problems)
    check(claim.get("reviewer") == reference.REVIEWER, "board reviewer differs", problems)
    for obj, name in ((report, "report"), (contract, "contract")):
        text = reference.canonical_text(obj)
        if re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', text):
            problems.append(f"{name}_contains_full_board_digest")
    linked = report.get("linked_row_identity", {})
    check(linked.get("board_file_pinned") is False, "board_file_pinned true", problems)
    check(linked.get("board_status_gates_anything") is False, "board_status_gates_anything true", problems)


def check_sources_manifest(problems: List[str]) -> None:
    expected = run.sources_bytes()
    if not SOURCES.is_file():
        problems.append("SOURCES.sha256 missing")
        return
    actual = SOURCES.read_bytes()
    if actual != expected:
        problems.append("SOURCES.sha256 not deterministic")
    text = actual.decode("ascii")
    if "plan/swarm/TASKS.json" in text:
        problems.append("SOURCES.sha256 pins mutable TASKS.json")
    for name in run.LOCAL_PIN_FILES:
        if f"  {reference.TASK_PREFIX}{name}" not in text:
            problems.append("missing_local_pin:" + name)


def parse_readme_digest_tables(text: str) -> Dict[str, Dict[str, str]]:
    tables: Dict[str, Dict[str, str]] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            heading = m.group(1).strip()
            if heading in {"Source pins", "Boundary pins", "Local artifact pins"}:
                current = heading
                tables[current] = {}
            else:
                current = None
            continue
        if current and line.startswith("|") and "`" in line:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) >= 2 and parts[0].startswith("`") and parts[1].startswith("`"):
                key = parts[0].strip("`")
                val = parts[1].strip("`")
                if re.fullmatch(r"[0-9a-f]{64}", val):
                    if key in tables[current]:
                        raise ValueError("duplicate_readme_row:" + current + ":" + key)
                    tables[current][key] = val
    for required in ("Source pins", "Boundary pins", "Local artifact pins"):
        if required not in tables:
            raise ValueError("missing_readme_table:" + required)
    return tables


def check_readme(problems: List[str]) -> None:
    if not README.is_file():
        problems.append("README.md missing")
        return
    text = README.read_text(encoding="utf-8")
    try:
        tables = parse_readme_digest_tables(text)
    except Exception as exc:  # noqa: BLE001
        problems.append("readme_digest_table:" + str(exc))
        return
    # Validate source pins
    src = tables["Source pins"]
    if set(src.keys()) != set(reference.SOURCE_PINS.keys()):
        problems.append("readme_source_pin_keys_mismatch")
    for k, v in reference.SOURCE_PINS.items():
        if src.get(k) != v:
            problems.append("readme_source_pin_mismatch:" + k)
        path = reference.SOURCE_ROOT / k
        if path.is_file() and sha256_file(path) != src.get(k):
            problems.append("readme_source_live_mismatch:" + k)
    bnd = tables["Boundary pins"]
    if set(bnd.keys()) != set(reference.BOUNDARY_PINS.keys()):
        problems.append("readme_boundary_pin_keys_mismatch")
    for k, v in reference.BOUNDARY_PINS.items():
        if bnd.get(k) != v:
            problems.append("readme_boundary_pin_mismatch:" + k)
        path = SDK_ROOT / k
        if path.is_file() and sha256_file(path) != bnd.get(k):
            problems.append("readme_boundary_live_mismatch:" + k)
    local = tables["Local artifact pins"]
    # README cannot pin its own bytes stably; SOURCES.sha256 cannot pin itself.
    expected_local = {name for name in run.LOCAL_PIN_FILES if name not in {"README.md", "SOURCES.sha256"}}
    if set(local.keys()) != expected_local:
        problems.append("readme_local_pin_keys_mismatch")
    for name in expected_local:
        actual = sha256_file(HERE / name)
        if local.get(name) != actual:
            problems.append("readme_local_pin_mismatch:" + name)


def check_licensing(problems: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            problems.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            problems.append("missing_sidecar_spdx:" + name)
    for name in ("README.md", "LICENSES.md"):
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            problems.append("missing_markdown_spdx:" + name)
    for path in sorted(HERE.glob("*.json")) + sorted(HERE.glob("*.sha256")):
        sidecar = HERE / (path.name + ".license")
        if not sidecar.is_file():
            problems.append("missing_sidecar:" + path.name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    if 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
    # REUSE-IgnoreEnd
        problems.append("reuse_missing_apache")
    if '"docs/**"' not in reuse and "docs/**" not in reuse:
        problems.append("reuse_docs_not_covered")
    for path in HERE.iterdir():
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            problems.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            problems.append("symlink:" + path.name)
        if path.is_file() and path.name in {"LICENSE", "LICENSE.txt", "COPYING", "NOTICE"}:
            problems.append("vendored_license:" + path.name)


def check_scope(problems: List[str]) -> None:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        problems.append("git_status_failed")
        return
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(reference.TASK_PREFIX):
            problems.append("out_of_scope_change:" + path)
    for args in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *args], capture_output=True, text=True, check=False)
        if diff.returncode != 0 or diff.stdout.strip():
            problems.append("git_" + "_".join(a.replace("-", "") for a in args) + "_failed")

    base = reference.scope_base(SDK_ROOT)
    if base is None:
        problems.append("scope_base_unavailable")
        return
    try:
        changed = reference.scope_changed_paths(SDK_ROOT, base)
    except Exception as exc:  # noqa: BLE001
        problems.append("scope_diff_failed:" + str(exc))
        return
    for path in reference.scope_violations(changed):
        problems.append("base_out_of_scope_change:" + path)


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audio-sdk"
    target = sdk / reference.TASK_PREFIX.rstrip("/")
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for rel in sorted(reference.BOUNDARY_PINS):
        src = SDK_ROOT / rel
        dst = sdk / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copyfile(src, dst)
    return target


def _prepare_source_root(root: Path) -> Path:
    src_root = root / "source-root"
    for rel in sorted(reference.SOURCE_PINS):
        src = reference.SOURCE_ROOT / rel
        dst = src_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(src)
    board = src_root / "audio-benchmark-platform/plan/swarm/TASKS.json"
    board.parent.mkdir(parents=True, exist_ok=True)
    board.symlink_to(reference.SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json")
    return src_root


def check_cold_regeneration(problems: List[str]) -> List[str]:
    committed = (REPORT.read_bytes(), CONTRACT.read_bytes(), SIDECAR.read_bytes(), SOURCES.read_bytes())
    if not all(committed):
        problems.append("committed_artifacts_missing")
        return []
    digests: List[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="sdk-whisper-streaming-cold-") as td:
        root = Path(td)
        src_root = _prepare_source_root(root)
        for i in range(3):
            target = _prepare_scratch(root, i)
            sdk_scratch = target.parents[1]
            # defensive: ensure boundary pins present even if gitignored in worktree
            for rel in sorted(reference.BOUNDARY_PINS):
                src = SDK_ROOT / rel
                dst = sdk_scratch / rel
                if src.is_file() and not dst.is_file():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dst)
            scratch_env = dict(env)
            scratch_env["SDK_ROOT"] = str(sdk_scratch)
            scratch_env["SOURCE_ROOT"] = str(src_root)
            proc = subprocess.run([sys.executable, "run.py", "all"], cwd=target, capture_output=True, text=True, env=scratch_env)
            if proc.returncode != 0:
                problems.append(f"cold_start_{i+1}_failed:" + (proc.stderr.strip() or proc.stdout.strip())[-400:])
                continue
            got = (
                (target / "report.json").read_bytes(),
                (target / "contract.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
            )
            if got != committed:
                problems.append(f"cold_start_{i+1}_bytes_differ")
            digests.append(sha256_bytes(got[0]))
    if len(digests) != 3 or len(set(digests)) != 1:
        problems.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    problems: List[str] = []
    report = strict_load(REPORT, problems)
    contract = strict_load(CONTRACT, problems)
    pins_checked = check_pins(problems)
    check_sources_manifest(problems)
    if isinstance(report, dict) and isinstance(contract, dict):
        check_report_contract(report, contract, problems)
        check_board_identity(report, contract, problems)
    check_readme(problems)
    check_licensing(problems)
    check_scope(problems)
    repeats = check_cold_regeneration(problems)

    report_bytes = REPORT.read_bytes() if REPORT.is_file() else b""
    report_sha = sha256_bytes(report_bytes) if report_bytes else "missing"
    sidecar_expected = f"{report_sha}  report.json\n".encode("ascii")
    if SIDECAR.is_file() and SIDECAR.read_bytes() != sidecar_expected:
        problems.append("sidecar_mismatch")
    if isinstance(report, dict):
        if reference.canonical_file_bytes(report) != report_bytes:
            problems.append("report_not_canonical")
        if not report_bytes.endswith(b"\n") or report_bytes.endswith(b"\n\n"):
            problems.append("report_trailing_newline")

    if problems:
        for p in problems:
            print("FAIL: " + p)
        print(f"verify_result=FAILED pins={pins_checked} repeats={len(repeats)} report_sha256={report_sha} failures={len(problems)}")
        return 1
    print(f"verify_result=OK pins={pins_checked} gates=8 blockers=8 repeats=3/3 byte_identical=true profile=rate decision=DEFER status=proposal_only_incomplete report_sha256={report_sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
