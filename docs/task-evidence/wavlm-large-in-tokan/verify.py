# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for SDK-WAVLM-LARGE-IN-TOKAN evidence.

Fails closed on stale pins/canonical artifacts, README digest mismatch, scope
violations (newest merge-base origin/main->main), missing base, dirty diff-check,
or any qualifying claim. Never writes.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
CONTRACT = HERE / "contract.json"
SIDECAR = HERE / "report.json.sha256"
SOURCES = HERE / "SOURCES.sha256"
README = HERE / "README.md"
REUSE = SDK_ROOT / "REUSE.toml"


def fail(msg: str, errors: List[str]) -> None:
    errors.append(msg)


def check_json(errors: List[str]) -> Dict[str, Any]:
    report = contract = None
    for p in (REPORT, CONTRACT):
        try:
            obj = reference.strict_loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            fail(f"invalid_json:{p.name}:{e}", errors)
            continue
        if p is REPORT:
            report = obj
        else:
            contract = obj
    if not isinstance(report, dict) or not isinstance(contract, dict):
        return {}
    if report.get("schema_id") != reference.SCHEMA_REPORT:
        fail("report_schema", errors)
    if contract.get("schema_id") != reference.SCHEMA_CONTRACT:
        fail("contract_schema", errors)
    for k in ("task_id","title","component_id","repository","base_commit","branch","profile","decision","evidence_status","qualification_status","status","format","boundary","scope","gates","exact_blockers","negative_claims","board_link","source_reported","voice_profile"):
        if report.get(k) != contract.get(k):
            fail("report_contract_mismatch:" + k, errors)
    return {"report": report, "contract": contract}


def check_policy(report: Dict[str, Any], errors: List[str]) -> None:
    if report.get("decision") != "DEFER": fail("decision_not_defer", errors)
    if report.get("evidence_status") != "incomplete": fail("status_not_incomplete", errors)
    if report.get("qualification_status") != "not_qualified": fail("qualification_not_not_qualified", errors)
    b = report.get("boundary", {})
    for k, v in b.items():
        if k == "format":
            continue
        if v is not False:
            fail("boundary_not_false:" + k, errors)
    s = report.get("scope", {})
    if s.get("synthetic_only") is not True or s.get("task_local_only") is not True:
        fail("scope_controls", errors)
    for k, v in s.items():
        if k not in {"synthetic_only", "task_local_only"} and v is not False:
            fail("scope_not_false:" + k, errors)
    gates = report.get("gates", [])
    if len(gates) != 8: fail("gate_count", errors)
    for g in gates:
        if g.get("status") != "blocked" or g.get("qualifies") is not False:
            fail("gate_not_blocked:" + str(g.get("id")), errors)
    blockers = report.get("exact_blockers", [])
    if len(blockers) < 6: fail("blocker_count", errors)
    ev = report.get("evidence_classes", {})
    for k in ("real_audio","listening","device_timing","benchmark","real_model_output"):
        if ev.get(k) is not False: fail("evidence_claimed:" + k, errors)
    if report.get("source_reported", {}).get("qualifies") is not False:
        fail("source_reported_qualifies", errors)
    absence = report.get("absence_summary", {})
    if absence.get("all_absent") is not True:
        fail("absence_present:" + str(absence.get("present_ids")), errors)
    adverse = report.get("adverse", {})
    if adverse.get("all_rejected") is not True:
        fail("adverse_not_all_rejected", errors)
    if adverse.get("metrics") is not None:
        fail("adverse_metrics_present", errors)
    board = report.get("board_link", {})
    if board.get("full_tasks_json_hashed") is not False:
        fail("mutable_board_hashed", errors)


def check_pins(errors: List[str]) -> None:
    for rel, digest in reference.SOURCE_PINS.items():
        p = reference.resolve_source(rel)
        if not p.is_file() or reference.sha256_file(p) != digest:
            fail("source_pin_stale:" + rel, errors)
    for rel, digest in reference.BOUNDARY_PINS.items():
        p = reference.resolve_worktree(rel)
        if not p.is_file() or reference.sha256_file(p) != digest:
            fail("boundary_pin_stale:" + rel, errors)


def check_canonical(errors: List[str]) -> None:
    report_payload = reference.report_bytes()
    sidecar_payload = reference.sidecar_bytes(report_payload)
    sources_payload = reference.sources_bytes(report_payload, sidecar_payload)
    report = reference.strict_loads(report_payload.decode("utf-8"))
    contract_payload = reference.contract_bytes(report_payload, sidecar_payload, sources_payload, report)
    for path, payload in ((REPORT, report_payload), (SIDECAR, sidecar_payload), (SOURCES, sources_payload), (CONTRACT, contract_payload)):
        if not path.is_file() or path.read_bytes() != payload:
            fail("noncanonical:" + path.name, errors)
    sidecar = SIDECAR.read_text(encoding="ascii").strip() if SIDECAR.is_file() else ""
    if sidecar != reference.sha256_bytes(report_payload) + "  report.json":
        fail("sidecar_mismatch", errors)


def check_sources(errors: List[str]) -> None:
    try:
        text = SOURCES.read_text(encoding="utf-8")
    except Exception as e:
        fail("sources_read:" + str(e), errors)
        return
    seen = set()
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            fail("sources_malformed:" + line, errors); continue
        digest, key = parts
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            fail("sources_bad_digest:" + key, errors)
        if key in seen:
            fail("sources_duplicate:" + key, errors)
        seen.add(key)
        if key.startswith("source:"):
            p = reference.resolve_source(key[len("source:"):])
        elif key.startswith(reference.TASK_PREFIX):
            p = reference.SDK_ROOT / key
        else:
            p = reference.SDK_ROOT / key
        if not p.is_file():
            fail("sources_missing:" + key, errors)
        elif reference.sha256_file(p) != digest:
            fail("sources_stale:" + key, errors)


def check_readme(errors: List[str]) -> None:
    try:
        text = README.read_text(encoding="utf-8")
    except Exception as e:
        fail("readme_read:" + str(e), errors); return
    for token in ("DEFER","incomplete","not_qualified","RG-01","RG-08","WavLM-Large","TokAN","base_out_of_scope_change","scope_base_unavailable",reference.TASK_ID,reference.BASE_COMMIT):
        if token not in text:
            fail("readme_missing_token:" + token, errors)
    start = "<!-- digest-table: source -->"
    end = "<!-- digest-table: end -->"
    boundary_start = "<!-- digest-table: boundary -->"
    def parse_table(s, e, prefix=""):
        if s not in text or e not in text:
            fail("readme_table_missing:" + s, errors); return {}
        block = text.split(s,1)[1].split(e,1)[0]
        rows = {}
        for line in block.splitlines():
            line=line.strip()
            if not line.startswith("|") or line.startswith("| ---"):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) != 2 or cols[0] == "Key":
                continue
            key = cols[0].strip("`")
            rows[prefix + key if prefix and not key.startswith(prefix) else key] = cols[1].strip("`")
        return rows
    src_rows = parse_table(start, end)
    bnd_rows = parse_table(boundary_start, end)
    expected_src = {"source:" + k: v for k, v in reference.SOURCE_PINS.items()}
    expected_bnd = dict(reference.BOUNDARY_PINS)
    if src_rows != expected_src:
        fail("readme_source_digest_mismatch", errors)
    if bnd_rows != expected_bnd:
        fail("readme_boundary_digest_mismatch", errors)


def check_files(errors: List[str]) -> None:
    expected = {"README.md","LICENSES.md","SOURCES.sha256","SOURCES.sha256.license","contract.json","contract.json.license","reference.py","report.json","report.json.license","report.json.sha256","report.json.sha256.license","run.py","test_reference.py","verify.py"}
    actual = {p.name for p in HERE.iterdir() if p.is_file()}
    if actual != expected:
        fail("unexpected_files:" + str(sorted(actual ^ expected)), errors)
    for p in HERE.rglob("*"):
        if p.is_dir() and p.name == "__pycache__":
            fail("pycache:" + p.relative_to(HERE).as_posix(), errors)
        if p.is_file() and p.suffix in {".pyc",".pyo"}:
            fail("compiled:" + p.relative_to(HERE).as_posix(), errors)
    for p in HERE.glob("*.py"):
        head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:4])
        if reference.SPDX_LICENSE not in head or reference.SPDX_COPYRIGHT not in head:
            fail("missing_spdx:" + p.name, errors)
    readme = README.read_text(encoding="utf-8")
    if "<!-- SPDX-" + "License-Identifier: Apache-2.0 -->" not in readme:
        fail("readme_spdx", errors)
    reuse = REUSE.read_text(encoding="utf-8")
    if 'docs/**' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        fail("reuse_docs_coverage_missing", errors)


def check_scope(errors: List[str]) -> None:
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        fail("scope_base_unavailable", errors)
        return
    print("scope base " + base)
    try:
        changed = reference.scope_changed_paths(SDK_ROOT, base)
    except Exception as e:
        fail("scope_diff_failed:" + str(e), errors)
        return
    violations = reference.scope_violations(changed)
    if violations:
        for v in violations:
            fail("base_out_of_scope_change:" + v, errors)
    print("scope changed paths " + str(len(changed)))


def check_diff_check(errors: List[str]) -> None:
    r = subprocess.run(["git","-C",str(SDK_ROOT),"diff","--check"], capture_output=True, text=True, check=False)
    if r.returncode != 0 or r.stdout.strip() or r.stderr.strip():
        fail("git_diff_check_failed:" + (r.stdout+r.stderr).strip(), errors)


def check_repeatability(errors: List[str]) -> None:
    r1 = reference.report_bytes()
    for _ in range(2):
        if reference.report_bytes() != r1:
            fail("nondeterministic_report", errors)
            return


def main() -> int:
    errors: List[str] = []
    data = check_json(errors)
    report = data.get("report", {})
    if report:
        check_policy(report, errors)
    check_pins(errors)
    check_canonical(errors)
    check_sources(errors)
    check_readme(errors)
    check_files(errors)
    check_scope(errors)
    check_diff_check(errors)
    check_repeatability(errors)
    if errors:
        for e in errors:
            print("FAIL " + e)
        return 1
    digest = reference.sha256_bytes(reference.report_bytes())
    print(f"PASS verify.py decision=DEFER status=incomplete qualification=not_qualified report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
