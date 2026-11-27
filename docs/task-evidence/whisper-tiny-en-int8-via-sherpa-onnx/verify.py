# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict verifier for whisper-tiny-en-int8-via-sherpa-onnx evidence package.

Checks: pins, README digest/tokens, contract/report schema, blockers/gates,
admission fail-closed, scope enforcement (branch diff vs newest merge-base of
origin/main or main; fail closed with scope_base_unavailable), working-tree
scope, reproducibility (3 cold starts), licensing sidecars, and no forbidden
artifacts.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def check_pins() -> None:
    pins = reference.pin_manifest()
    for k, v in pins.items():
        if v["sha256"] == "MISSING":
            fail(f"missing_pin_target:{k}")
        if v["sha256"] != v["expected"]:
            fail(f"pin_mismatch:{k}:{v['sha256']}!={v['expected']}")
    # README digest validation against pin/source
    readme = HERE / "README.md"
    text = readme.read_text(encoding="utf-8")
    for token in ["DEFER", "incomplete", "not_qualified", reference.TASK_ID, "Evidence", "scope_base_unavailable", "base_out_of_scope_change"]:
        if token not in text:
            fail(f"readme_missing_token:{token}")


def check_contract_report() -> dict:
    contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
    report = json.loads((HERE / "report.json").read_text(encoding="utf-8"))
    for k in ["task_id", "decision", "status", "qualification_status", "proposal_only"]:
        if contract.get(k) != report.get(k):
            fail(f"contract_report_mismatch:{k}")
    if report["decision"] != "DEFER" or report["status"] != "incomplete" or report["qualification_status"] != "not_qualified":
        fail("decision_status_mismatch")
    if not report.get("proposal_only"):
        fail("proposal_only_required")
    if len(report.get("release_gates", [])) != 8:
        fail("release_gate_count")
    if any(g.get("status") != "blocked" for g in report["release_gates"]):
        fail("release_gate_not_blocked")
    if len(report.get("blockers", [])) != 6:
        fail("blocker_count")
    if any(b.get("status") != "open" for b in report["blockers"]):
        fail("blocker_not_open")
    if report.get("summary", {}).get("qualifying_result_count", 1) != 0:
        fail("qualifying_result_present")
    # claims
    claims = report.get("claims", {})
    for k, v in claims.items():
        if v is not False:
            fail(f"claim_not_false:{k}")
    return report


def check_admission() -> None:
    cases = reference.admission_cases()
    by_id = {c["case_id"]: c for c in cases}
    if by_id["valid-shape-control"]["status"] != "accepted_for_schema_only":
        fail("admission_control_not_schema_only")
    for cid, c in by_id.items():
        if c["qualifies"] or c["counts_as_qualification"]:
            fail(f"admission_qualifies:{cid}")
        if cid != "valid-shape-control" and c["status"] != "rejected":
            fail(f"admission_not_rejected:{cid}")
    ctrl = reference.synthetic_scorer_control()
    if not ctrl.get("synthetic") or ctrl.get("qualifies"):
        fail("synthetic_control_invalid")


def check_scope() -> None:
    diff = reference.branch_diff_paths(reference.WORKTREE)
    if diff["status"] != "ok":
        fail("scope_base_unavailable")
    violations = diff.get("violations", [])
    if violations:
        fail("base_out_of_scope_change:" + ",".join(violations))
    wt = reference.working_tree_violations(reference.WORKTREE)
    if wt:
        fail("working_tree_out_of_scope:" + ",".join(wt))


def check_forbidden() -> None:
    for p in HERE.rglob("*"):
        if p.is_dir():
            continue
        if p.suffix.lower() in reference.FORBIDDEN_SUFFIXES:
            fail(f"forbidden_artifact:{p.relative_to(HERE)}")
        rel = p.relative_to(reference.WORKTREE).as_posix()
        if not rel.startswith(reference.TASK_PREFIX):
            fail(f"task_file_outside_prefix:{rel}")


def check_licensing() -> None:
    for name in ["LICENSES.md", "README.md", "reference.py", "run.py", "test_reference.py", "verify.py"]:
        text = (HERE / name).read_text(encoding="utf-8")
        if "SPDX-" "License-Identifier: Apache-2.0" not in text:
            fail(f"missing_spdx:{name}")
    for name in ["contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"]:
        text = (HERE / name).read_text(encoding="utf-8")
        if "SPDX-" "License-Identifier: Apache-2.0" not in text:
            fail(f"missing_sidecar_spdx:{name}")


def check_report_sidecar() -> None:
    report_bytes = (HERE / "report.json").read_bytes()
    digest = hashlib.sha256(report_bytes).hexdigest()
    sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if not sidecar.startswith(digest):
        fail("report_sidecar_mismatch")


def cold_start_regen(report: dict) -> None:
    hashes = []
    for i in range(3):
        with tempfile.TemporaryDirectory(prefix="whisper-int8-sherpa-verify-") as td:
            tmp = Path(td) / "pkg"
            shutil.copytree(HERE, tmp)
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["PYTHONHASHSEED"] = "0"
            env["SDK_ROOT"] = str(reference.WORKTREE)
            env["SOURCE_ROOT"] = str(reference.AUDIO_ROOT)
            env["EVIDENCE_HEAD"] = str(report.get("head", ""))
            env["EVIDENCE_BRANCH"] = str(report.get("branch", ""))
            proc = subprocess.run([sys.executable, "run.py"], cwd=tmp, env=env, text=True, capture_output=True)
            if proc.returncode != 0:
                fail(f"regen_failed:{i}:{proc.stdout}{proc.stderr}")
            hashes.append(sha256_file(tmp / "report.json"))
    if len(set(hashes)) != 1:
        fail(f"regen_nondeterministic:{hashes}")
    committed = sha256_file(HERE / "report.json")
    if hashes[0] != committed:
        fail(f"regen_mismatch_committed:{hashes[0]}!={committed}")


def main() -> int:
    check_pins()
    report = check_contract_report()
    check_admission()
    check_scope()
    check_forbidden()
    check_licensing()
    check_report_sidecar()
    cold_start_regen(report)
    print(
        "PASS "
        f"task={reference.TASK_ID} decision={report['decision']} "
        f"status={report['status']} qualification={report['qualification_status']} "
        f"head={report['head']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        fail(f"exception:{type(e).__name__}:{e}")
