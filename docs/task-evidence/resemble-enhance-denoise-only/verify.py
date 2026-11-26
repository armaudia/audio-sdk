# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for SDK-RESEMBLE-ENHANCE-DENOISE-ONLY blocker evidence."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
CONTRACT = HERE / "contract.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Hovhannes Tsakanyan"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)

REQUIRED_REPORT_KEYS = {
    "schema_id","task","title","component","base_commit","branch","profile","status","evidence_status",
    "qualification","decision","defer_before","no_missing_result_qualifies_candidate","scope","boundary",
    "negative_claims","format","linked_row_identity","source_pins","boundary_pins","absence_probes",
    "exact_blockers","missing_evidence","reopening_conditions","gates","adverse_cases",
    "enhancement_profile_application","repeatability",
}
REQUIRED_CONTRACT_KEYS = {
    "schema_id","task","title","component","base_commit","branch","profile","status","evidence_status",
    "qualification_status","decision","defer_before","no_missing_result_qualifies_candidate","scope","boundary",
    "format","linked_row_identity","source_pins","boundary_pins","absence_probes","exact_blockers",
    "missing_evidence","reopening_conditions","gates","adverse_cases",
}


def _strict_json(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as err:
        errors.append(f"strict_json_failed:{label}:{err}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"json_root_not_object:{label}")
        return {}
    return payload


def check_pins(errors: List[str]) -> None:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return
    try:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
    except Exception as err:
        errors.append(f"strict_pin_rejection:{err}")
        return
    expected = reference.allowed_pin_keys()
    if {n for _, n in pins} != expected:
        errors.append("pin_manifest_key_mismatch")
    for digest, raw in pins:
        if raw.startswith("source:"):
            path = reference.SOURCE_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("sdk:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("task:"):
            path = HERE / raw.split(":", 1)[1]
        else:
            errors.append(f"pin_bad_prefix:{raw}")
            continue
        if not path.is_file():
            errors.append(f"pin_target_missing:{raw}")
        elif reference.sha256_file(path) != digest:
            errors.append(f"pinned_bytes_changed:{raw}")
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("SOURCES.sha256_not_deterministic_bytes")


def check_json(errors: List[str]) -> Dict[str, Dict[str, Any]]:
    report = _strict_json(REPORT, errors, "report")
    contract = _strict_json(CONTRACT, errors, "contract")
    if not report or not contract:
        return {"report": report, "contract": contract}
    if REPORT.read_bytes() != reference.canonical_report_bytes(report):
        errors.append("report_not_canonical_bytes")
    if CONTRACT.read_bytes() != reference.contract_bytes():
        errors.append("contract_not_canonical_bytes")
    report_digest = reference.sha256_bytes(REPORT.read_bytes())
    expected_sidecar = f"{report_digest}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    if reference.has_negative_zero(report):
        errors.append("negative_zero_in_report")
    if reference.has_negative_zero(contract):
        errors.append("negative_zero_in_contract")
    return {"report": report, "contract": contract}


def check_content(errors: List[str], payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]
    missing = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing:
        errors.append("report_missing_keys:" + ",".join(missing))
        return
    missing = sorted(REQUIRED_CONTRACT_KEYS - set(contract))
    if missing:
        errors.append("contract_missing_keys:" + ",".join(missing))
    for k, expected in (
        ("task", reference.TASK), ("base_commit", reference.BASE_COMMIT), ("branch", reference.BRANCH),
        ("profile", reference.PROFILE), ("status", reference.STATUS), ("evidence_status", reference.EVIDENCE_STATUS),
        ("decision", reference.DECISION), ("defer_before", reference.DEFER_BEFORE),
    ):
        if report.get(k) != expected:
            errors.append(f"report_field_mismatch:{k}")
        if contract.get(k) != expected and k != "base_commit":  # base_commit present in contract too
            pass
    if contract.get("base_commit") != reference.BASE_COMMIT:
        errors.append("contract_base_commit_mismatch")
    if report["qualification"].get("status") != reference.QUALIFICATION_STATUS or report["qualification"].get("qualified") is not False:
        errors.append("qualification_not_blocked")
    if contract.get("qualification_status") != reference.QUALIFICATION_STATUS:
        errors.append("contract_qualification_mismatch")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")
    if report["scope"] != reference.SCOPE or contract["scope"] != reference.SCOPE:
        errors.append("scope_mismatch")
    if report["boundary"] != reference.BOUNDARY or contract["boundary"] != reference.BOUNDARY:
        errors.append("boundary_mismatch")
    for k, v in report["negative_claims"].items():
        if v is not False:
            errors.append(f"prohibited_claim:{k}")
    if report["linked_row_identity"].get("policy") != "stable_linked_row_identity_only; never hash mutable full plan/swarm/TASKS.json":
        errors.append("linked_row_policy_missing")
    if report["linked_row_identity"].get("projection_sha256") != reference.stable_linked_row_projection_sha256():
        errors.append("linked_row_projection_sha256_mismatch")
    if report["linked_row_identity"].get("linked_rows_sha256") != reference.stable_linked_rows_sha256():
        errors.append("linked_rows_sha256_mismatch")
    if report["source_pins"] != reference.SOURCE_PINS or contract["source_pins"] != reference.SOURCE_PINS:
        errors.append("source_pins_mismatch")
    if report["boundary_pins"] != reference.BOUNDARY_PINS or contract["boundary_pins"] != reference.BOUNDARY_PINS:
        errors.append("boundary_pins_mismatch")
    if report["exact_blockers"] != reference.EXACT_BLOCKERS:
        errors.append("exact_blockers_mismatch")
    if report["missing_evidence"] != reference.MISSING_EVIDENCE:
        errors.append("missing_evidence_mismatch")
    if report["reopening_conditions"] != reference.REOPENING_CONDITIONS:
        errors.append("reopening_conditions_mismatch")
    gates = report["gates"]
    if len(gates) != len(reference.GATE_DEFINITIONS):
        errors.append("gate_count_changed")
    if any(g.get("status") != "blocked" or g.get("qualifies") is not False for g in gates):
        errors.append("gate_not_blocked")
    adverse = report["adverse_cases"]
    if adverse.get("all_rejected") is not True or adverse.get("any_qualifying") is not False:
        errors.append("adverse_cases_not_all_rejected")
    for name, case in adverse.get("cases", {}).items():
        if case.get("status") != "rejected":
            errors.append(f"adverse_case_not_rejected:{name}")
    repeat = report["repeatability"]
    expected = reference.build_report()["repeatability"]
    if repeat != expected:
        errors.append("repeatability_mismatch")
    if repeat.get("count") != 3 or repeat.get("byte_identical") is not True or len(set(repeat.get("digests", []))) != 1:
        errors.append("cold_start_repeatability_failed")


def check_source_files(errors: List[str]) -> None:
    for rel, digest in {**reference.SOURCE_PINS}.items():
        p = reference.SOURCE_ROOT / rel
        if not p.is_file():
            errors.append(f"source_pin_missing:{rel}")
        elif reference.sha256_file(p) != digest:
            errors.append(f"source_pin_changed:{rel}")
    for rel, digest in reference.BOUNDARY_PINS.items():
        p = SDK_ROOT / rel
        if not p.is_file():
            errors.append(f"boundary_pin_missing:{rel}")
        elif reference.sha256_file(p) != digest:
            errors.append(f"boundary_pin_changed:{rel}")


def check_strict_rejections(errors: List[str]) -> None:
    r = reference.strict_rejection_examples()
    if r["bad_json_rejected"] != r["bad_json_total"]:
        errors.append("strict_json_accepted_bad_input")
    if r["bad_pins_rejected"] != r["bad_pins_total"]:
        errors.append("strict_pin_parser_accepted_bad_input")


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append(f"missing_python_spdx:{path.name}")
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    if SPDX_LICENSE not in readme or SPDX_COPYRIGHT not in readme:
        errors.append("missing_readme_spdx")
    for name in LICENSE_SIDECARS:
        p = HERE / name
        text = p.read_text(encoding="utf-8") if p.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append(f"missing_license_sidecar:{name}")
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE_docs_coverage_missing")


def check_scope(errors: List[str]) -> None:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return
    allowed_prefix = f"docs/task-evidence/{reference.SLUG}/"
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith(allowed_prefix):
            errors.append(f"out_of_scope_change:{path}")


def main() -> int:
    errors: List[str] = []
    check_pins(errors)
    payloads = check_json(errors)
    if payloads.get("report") and payloads.get("contract"):
        check_content(errors, payloads)
    check_source_files(errors)
    check_strict_rejections(errors)
    check_licensing(errors)
    check_scope(errors)
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1
    print("verify.py: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
