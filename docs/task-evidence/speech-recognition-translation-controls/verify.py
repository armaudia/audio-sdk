# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for speech-recognition-translation-controls evidence.

Usage: PYTHONDONTWRITEBYTECODE=1 python3 verify.py
Fails closed on duplicate/nonfinite JSON, stale pins/artifacts, scope escape,
license gaps, or dirty diff-check. Never writes.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
CONTRACT = HERE / "contract.json"
SIDECAR = HERE / "report.json.sha256"
SOURCES = HERE / "SOURCES.sha256"
README = HERE / "README.md"
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan"
LICENSE_SIDECARS = ["contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"]


def _fail(msg: str, errors: List[str]) -> None:
    errors.append(msg)


def _eq(errors: List[str], msg: str, left: Any, right: Any) -> None:
    if left != right:
        _fail(msg, errors)


def check_json(errors: List[str]) -> Dict[str, Any]:
    report = contract = None
    for path in (REPORT, CONTRACT):
        try:
            obj = reference.strict_loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            _fail(f"invalid_json:{path.name}:{exc}", errors)
            continue
        if path == REPORT:
            report = obj
        else:
            contract = obj
    if not isinstance(report, dict) or not isinstance(contract, dict):
        return {}
    _eq(errors, "contract_schema", contract.get("schema_id"), reference.SCHEMA_CONTRACT)
    _eq(errors, "report_schema", report.get("schema_id"), reference.SCHEMA_REPORT)
    for key in ("task_id", "title", "component_id", "repository", "base_commit", "branch", "profile", "decision", "defer_before", "evidence_status", "qualification_status", "status", "format", "boundary", "scope", "gates", "exact_blockers", "negative_claims", "board_link", "inventory_link", "caller_supplied_asset_contract", "asset_ledger"):
        _eq(errors, "contract/report differ:" + key, contract.get(key), report.get(key))
    return {"report": report, "contract": contract}


def check_boundary(report: Dict[str, Any], errors: List[str]) -> None:
    boundary = report.get("boundary", {})
    for k, v in boundary.items():
        if k == "format":
            continue
        if v is not False:
            _fail("boundary_not_false:" + k, errors)
    scope = report.get("scope", {})
    if scope.get("synthetic_only") is not True or scope.get("task_local_only") is not True:
        _fail("scope_controls_not_true", errors)
    for k, v in scope.items():
        if k not in {"synthetic_only", "task_local_only"} and v is not False:
            _fail("scope_not_false:" + k, errors)
    if report.get("decision") != "DEFER":
        _fail("decision_not_defer", errors)
    if report.get("evidence_status") != "incomplete":
        _fail("evidence_not_incomplete", errors)
    if report.get("qualification_status") != "not_qualified":
        _fail("qualification_not_not_qualified", errors)
    if report.get("no_missing_result_qualifies_candidate") is not True:
        _fail("missing_result_may_qualify", errors)
    gates = report.get("gates", [])
    if not isinstance(gates, list) or len(gates) != 8:
        _fail("gate_count", errors)
    else:
        for i, g in enumerate(gates, 1):
            if g.get("id") != f"RG-0{i}":
                _fail("gate_id:" + str(g.get("id")), errors)
            if g.get("status") != "blocked" or g.get("qualifies") is not False or not g.get("reopen_condition"):
                _fail("gate_not_blocked:" + str(g.get("id")), errors)
    blockers = report.get("exact_blockers", [])
    if not isinstance(blockers, list) or len(blockers) != 4:
        _fail("blocker_count", errors)
    evidence = report.get("evidence_classes", {})
    for k in ("real_local_model_output", "real_audio", "listening", "device_timing", "benchmark", "source_reported"):
        if evidence.get(k) is not False:
            _fail("evidence_class_claimed:" + k, errors)
    if evidence.get("synthetic") is not True:
        _fail("synthetic_not_labelled", errors)


def check_pins(errors: List[str]) -> None:
    sp = reference.verify_source_pins()
    if not sp["ok"]:
        _fail("source_pin_mismatch:" + str(sp["mismatches"]), errors)
    bp = reference.verify_boundary_pins()
    if not bp["ok"]:
        _fail("boundary_pin_mismatch:" + str(bp["mismatches"]), errors)
    bl = reference.board_link()
    if bl["stable_sha256"] != reference.BOARD_STABLE_SHA256:
        _fail("board_stable_sha256_mismatch", errors)
    il = reference.inventory_link()
    if il["stable_sha256"] != reference.INVENTORY_STABLE_SHA256:
        _fail("inventory_stable_sha256_mismatch", errors)


def check_artifacts(report: Dict[str, Any], contract: Dict[str, Any], errors: List[str]) -> None:
    report_payload = REPORT.read_bytes()
    sidecar_payload = SIDECAR.read_bytes()
    expected_sidecar = (reference.sha256_bytes(report_payload) + "  report.json\n").encode("utf-8")
    if sidecar_payload != expected_sidecar:
        _fail("sidecar_mismatch", errors)
    fresh_report = reference.report_bytes()
    if report_payload != fresh_report:
        _fail("stale_report", errors)
    fresh_sidecar = reference.sidecar_bytes(fresh_report)
    fresh_contract = reference.contract_bytes(fresh_report, fresh_sidecar, b"", reference.strict_loads(fresh_report.decode("utf-8")))
    fresh_sources = reference.sources_bytes(fresh_report, fresh_sidecar, fresh_contract)
    fresh_contract = reference.contract_bytes(fresh_report, fresh_sidecar, fresh_sources, reference.strict_loads(fresh_report.decode("utf-8")))
    fresh_sources = reference.sources_bytes(fresh_report, fresh_sidecar, fresh_contract)
    if CONTRACT.read_bytes() != fresh_contract:
        _fail("stale_contract", errors)
    if SOURCES.read_bytes() != fresh_sources:
        _fail("stale_sources", errors)
    for name in LICENSE_SIDECARS:
        p = HERE / name
        if not p.is_file():
            _fail("missing_sidecar:" + name, errors)
            continue
        text = p.read_text(encoding="utf-8")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            _fail("bad_sidecar:" + name, errors)
    if not README.is_file():
        _fail("missing_readme", errors)
    else:
        text = README.read_text(encoding="utf-8")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            _fail("readme_spdx_missing", errors)


def check_scope(errors: List[str]) -> None:
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        _fail("scope_base_unavailable", errors)
        return
    changed = reference.scope_changed_paths(SDK_ROOT, base)
    viol = reference.scope_violations(changed)
    if viol:
        _fail("scope_violation:" + ",".join(viol), errors)


def main() -> int:
    errors: List[str] = []
    objs = check_json(errors)
    if objs:
        check_boundary(objs["report"], errors)
        check_pins(errors)
        check_artifacts(objs["report"], objs["contract"], errors)
    check_scope(errors)
    proc = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        _fail("git_diff_check_failed:" + proc.stdout.strip() + proc.stderr.strip(), errors)
    if errors:
        for e in errors:
            print("FAIL: " + e)
        return 1
    print("PASS: speech-recognition-translation-controls evidence verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
