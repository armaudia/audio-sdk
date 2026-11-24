# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Exact-match scorer for the synthetic ABI/ownership parity crosscheck.

There are no tolerances, thresholds, rankings or qualification claims. A row
passes only when every contract-invariant field is identical to the frozen
model.  The scorer is used for both in-process self-checks and the recorded
task-local C harness output.
"""

from __future__ import annotations

from typing import Any, Dict, List


def result_invariants(row: Dict[str, Any]) -> Dict[str, bool]:
    """Check shape guarantees implied by the pinned v0 contract."""
    status = row.get("process_status")
    result = row.get("result")
    if status != "OK":
        return {"result_absent_on_failure": result is None}
    if not isinstance(result, dict) or result.get("status") not in ("OK", 0):
        return {"result_absent_on_failure": False, "result_status_ok": False}
    try:
        consumed = int(result["consumed_count"])
        produced = int(result["produced_count"])
        offset = int(result["valid_offset"])
        valid = int(result["valid_count"])
        flags = int(result["flags"])
    except (KeyError, TypeError, ValueError):
        return {"result_fields_present": False}
    return {
        "result_fields_present": True,
        "consumed_exactly_frame": consumed == 160,
        "produced_within_frame": 0 <= produced <= 160,
        "valid_window_within_output": 0 <= offset <= produced and valid <= produced - offset,
        "flags_are_contract_bits": flags >= 0 and flags <= 7,
    }


def score_case(expected: Dict[str, Any], observed: Dict[str, Any]) -> Dict[str, Any]:
    expected_process = expected["expected_process_status"] or "-"
    checks: Dict[str, bool] = {
        "case_id": expected["case_id"] == observed.get("case_id"),
        "kind": expected["kind"] == observed.get("kind"),
        "mutation": expected["mutation"] == observed.get("mutation"),
        "expected_create_status": expected["expected_create_status"] == observed.get("create_status"),
        "expected_process_status": expected_process == observed.get("process_status"),
        "events": expected["events"] == observed.get("events"),
        "input_digest": expected["input_digest"] == observed.get("input_digest"),
    }
    invariants = result_invariants(observed)
    checks.update(invariants)
    return {
        "case_id": expected["case_id"],
        "checks": checks,
        "passed": all(checks.values()),
    }


def score_all(expected_cases: List[Dict[str, Any]],
              observed_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(expected_cases) != len(observed_cases):
        return {
            "passed": False,
            "reason": "case_count_mismatch",
            "expected_count": len(expected_cases),
            "observed_count": len(observed_cases),
            "rows": [],
        }
    by_id = {row.get("case_id"): row for row in observed_cases}
    rows: List[Dict[str, Any]] = []
    for expected in expected_cases:
        observed = by_id.get(expected["case_id"])
        if observed is None:
            rows.append({
                "case_id": expected["case_id"],
                "checks": {"observed_case_present": False},
                "passed": False,
            })
        else:
            rows.append(score_case(expected, observed))
    return {
        "passed": all(row["passed"] for row in rows),
        "reason": None,
        "expected_count": len(expected_cases),
        "observed_count": len(observed_cases),
        "rows": rows,
    }


def summary(result: Dict[str, Any]) -> Dict[str, Any]:
    rows = result.get("rows", [])
    failed = [row["case_id"] for row in rows if not row.get("passed")]
    return {
        "passed": bool(result.get("passed")),
        "case_count": len(rows),
        "passed_count": len(rows) - len(failed),
        "failed_cases": failed,
        "scoring": "exact field and invariant equality; no tolerance or threshold",
    }
