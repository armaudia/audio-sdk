# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the TRN-01 category evidence map.

Run with the pinned interpreter from this directory. This verifier never
rewrites evidence. It fails closed on stale, malformed, duplicated or missing
pins, non-canonical JSON, duplicate/nonfinite JSON keys, stale digest sidecars,
unlinked gaps, forbidden claims, licensing gaps and any worktree change outside
the task directory.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
REQUIRED_REPORT_KEYS = {
    "schema_id", "task_id", "category_id", "title", "base_commit", "branch",
    "profile", "status", "qualification_status", "decision",
    "no_missing_result_qualifies_candidate", "scope", "boundary", "format",
    "deliverable", "contract_id", "contract_sha256", "board_snapshot", "source_pins",
    "evidence_pins", "boundary_pins", "tool_provenance", "category",
    "verification_profile", "families", "source_leads", "historical_executions",
    "task_local_executions", "gaps", "gates", "missing_evidence", "adverse",
    "evidence_classes", "state_sha256", "repeatability",
    "comparison_inputs", "controls", "assets", "local_vs_reported_outcomes",
    "release_boundary",
}


def strict_json(path: Path) -> Dict[str, Any]:
    return reference.strict_json(path)


def allowed_pins() -> Dict[str, str]:
    allowed: Dict[str, str] = {}
    for path, digest in reference.SOURCE_PINS.items():
        allowed["source:" + path] = digest
    for path, digest in reference.EVIDENCE_PINS.items():
        allowed["evidence:" + path] = digest
    allowed.update(reference.BOUNDARY_PINS)
    for name in reference.LOCAL_PIN_PATHS:
        allowed[reference.TASK_PREFIX + name] = ""
    return allowed


def check_pins(errors: List[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256_missing")
        return 0
    allowed = allowed_pins()
    seen = set()
    count = 0
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        count += 1
        try:
            key, digest = reference.verify_pin_line(line, allowed)
        except reference.ValidationError as error:
            errors.append(str(error))
            continue
        if key in seen:
            errors.append("duplicate_pin:" + key)
            continue
        seen.add(key)
        if key.startswith("source:"):
            path = reference.SOURCE_ROOT / key.split(":", 1)[1]
        elif key.startswith("evidence:"):
            path = SDK_ROOT / key.split(":", 1)[1]
        else:
            path = SDK_ROOT / key
        if not path.is_file():
            errors.append("pin_target_missing:" + key)
        elif reference.sha256(path.read_bytes()) != digest:
            errors.append("pinned_bytes_changed:" + key)
    for key in sorted(set(allowed) - seen):
        errors.append("pin_absent:" + key)
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("SOURCES.sha256_not_deterministic")
    return count


def check_report(errors: List[str]) -> Dict[str, Any]:
    try:
        report = strict_json(REPORT)
        contract = strict_json(CONTRACT)
        inputs = reference.load_inputs()
    except (OSError, ValueError, UnicodeError, KeyError, TypeError) as error:
        errors.append("strict_json_failed:" + str(error))
        return {}
    missing = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing:
        errors.append("report_missing_keys:" + ",".join(missing))
        return report
    raw = REPORT.read_bytes()
    if raw != reference.canonical_report_bytes(report):
        errors.append("report_not_canonical_bytes")
    if b"-0.0" in raw:
        errors.append("negative_zero_in_report")
    digest = reference.sha256(raw)
    expected_sidecar = f"{digest}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    if report["base_commit"] != reference.BASE_COMMIT or report["branch"] != reference.BRANCH:
        errors.append("base_commit_or_branch_mismatch")
    if report["profile"] != reference.PROFILE or report["category_id"] != reference.CATEGORY_ID:
        errors.append("profile_or_category_mismatch")
    if (report["status"] != reference.STATUS
            or report["qualification_status"] != reference.QUALIFICATION
            or report["decision"] != reference.DECISION
            or report["no_missing_result_qualifies_candidate"] is not True):
        errors.append("DEFER_incomplete_not_qualified_disposition_missing")
    if report["scope"] != reference.SCOPE:
        errors.append("scope_table_mismatch")
    if report["boundary"] != reference.BOUNDARY:
        errors.append("boundary_table_mismatch")
    if report["format"] != reference.FORMAT:
        errors.append("public_v0_geometry_changed")
    if report["source_pins"] != reference.SOURCE_PINS:
        errors.append("report_source_pins_mismatch")
    if report["evidence_pins"] != reference.EVIDENCE_PINS:
        errors.append("report_evidence_pins_mismatch")
    if report["boundary_pins"] != reference.BOUNDARY_PINS:
        errors.append("report_boundary_pins_mismatch")
    if report["contract_sha256"] != reference.sha256(CONTRACT.read_bytes()):
        errors.append("contract_digest_mismatch")
    expected_snapshot = {
        "path": reference.TASK_PREFIX + reference.BOARD_SNAPSHOT,
        "sha256": reference.BOARD_SNAPSHOT_SHA256,
        "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "source_sha256": reference.BOARD_SNAPSHOT_SOURCE_SHA256,
        "task_count": len(inputs["tasks"]),
        "live_board_read": False,
    }
    if report["board_snapshot"] != expected_snapshot:
        errors.append("board_snapshot_mismatch")
    if contract.get("board_snapshot") != expected_snapshot:
        errors.append("contract_board_snapshot_mismatch")
    if (contract.get("task") != reference.TASK
            or contract.get("category_id") != reference.CATEGORY_ID
            or contract.get("status") != reference.STATUS
            or contract.get("qualification_status") != reference.QUALIFICATION
            or contract.get("decision") != reference.DECISION
            or contract.get("profile") != reference.PROFILE):
        errors.append("contract_identity_mismatch")
    if (contract.get("source_pins") != reference.SOURCE_PINS
            or contract.get("evidence_pins") != reference.EVIDENCE_PINS
            or contract.get("boundary_pins") != reference.BOUNDARY_PINS):
        errors.append("contract_pin_tables_mismatch")
    if contract.get("scope") != reference.SCOPE or contract.get("boundary") != reference.BOUNDARY:
        errors.append("contract_scope_or_boundary_mismatch")
    if contract.get("release_gates") != [gate["reopen_condition"] for gate in reference.gates()]:
        errors.append("contract_gates_mismatch")
    category = report["category"]
    if not category.get("identical") or category.get("task") != reference.TASK:
        errors.append("category_crosscheck_failed")
    profile = report["verification_profile"]
    if (profile["profile"] != reference.PROFILE
            or profile["applied_to"] != "category_map_only"
            or profile["runtime_executed"] is not False
            or profile["pitch"] != "not_measured_no_rendered_audio"
            or profile["transient_audibility"] != "not_measured_no_listening"
            or profile["device_timing"] != "not_measured_no_device"):
        errors.append("verification_profile_claim_invalid")
    expected_families = [family["id"] for family in reference.FAMILIES]
    if [family["id"] for family in report["families"]] != expected_families:
        errors.append("family_set_mismatch")
    for family in report["families"]:
        source = next(item for item in reference.FAMILIES if item["id"] == family["id"])
        expected_components = [item["component_id"] for item in source["components"]]
        if [item["component_id"] for item in family["components"]] != expected_components:
            errors.append("family_component_mismatch:" + family["id"])
        if family["gap_ids"] != source["gap_ids"]:
            errors.append("family_gap_link_mismatch:" + family["id"])
    expected_leads = [lead["source_id"] for lead in reference.SOURCE_LEADS]
    if [lead["source_id"] for lead in report["source_leads"]] != expected_leads:
        errors.append("source_lead_set_mismatch")
    for lead in report["source_leads"]:
        if lead["url_fetched"] is not False or lead["classification"] != (
                "source_text_only_not_reproduced"):
            errors.append("source_lead_claim_invalid:" + lead["source_id"])
    valid_pins = (set(reference.SOURCE_PINS) | set(reference.EVIDENCE_PINS)
                  | set(reference.BOUNDARY_PINS))
    for key, expected in (
            ("comparison_inputs", reference.COMPARISON_INPUTS),
            ("controls", reference.CONTROLS),
            ("assets", reference.ASSETS)):
        items = report[key]
        if [item["id"] for item in items] != [item["id"] for item in expected]:
            errors.append(key + "_set_mismatch")
            continue
        for item in items:
            if item["source_pin"] not in valid_pins:
                errors.append(key + "_pin_unknown:" + item["id"])
            if key == "comparison_inputs" and not item.get("boundary"):
                errors.append("comparison_input_boundary_missing:" + item["id"])
            if key == "controls" and not item.get("role"):
                errors.append("control_role_missing:" + item["id"])
            if key == "assets" and not item.get("status"):
                errors.append("asset_status_missing:" + item["id"])
    outcome = report["local_vs_reported_outcomes"]
    if (outcome["reported"]["classification"] != "source_reported_not_reproduced"
            or outcome["local"]["classification"] !=
            "task_local_synthetic_reference_only"
            or outcome["reported"]["qualifies_candidate"] is not False
            or outcome["local"]["qualifies_candidate"] is not False):
        errors.append("outcome_classification_invalid")
    if (outcome["cross_comparison"]["performed"] is not False
            or outcome["cross_comparison"]["numeric_parity_claimed"] is not False
            or not outcome["cross_comparison"]["reason"]):
        errors.append("cross_comparison_not_gated")
    ledger_ids = [item["component_id"] for item in outcome["ledger"]]
    expected_ledger_ids = sorted(
        {item["component_id"] for item in report["historical_executions"]}
        | {item["component_id"] for item in report["task_local_executions"]})
    if ledger_ids != expected_ledger_ids:
        errors.append("outcome_ledger_set_mismatch")
    for item in outcome["ledger"]:
        if item["comparison_performed"] is not False or item["qualifies_candidate"] is not False:
            errors.append("outcome_ledger_promoted:" + item["component_id"])
    release = report["release_boundary"]
    if (release["release_allowed"] is not False or release["release_claim"] is not False
            or release["qualification_status"] != reference.QUALIFICATION
            or release["decision"] != reference.DECISION
            or release["installed_v0_geometry"] != reference.FORMAT
            or release["provider_registration"] is not False
            or release["enabled_by_default"] is not False
            or release["default_selected"] is not False
            or release["public_api_abi_change"] is not False
            or release["board_write"] is not False
            or release["handoff_write"] is not False):
        errors.append("release_boundary_claim_invalid")
    if release["blocked_gates"] != reference.GATE_NAMES or set(release["gated_claims"]) != {
            "pitch_preservation", "transient_audibility", "listening", "device_timing",
            "public_benchmark", "release"}:
        errors.append("release_boundary_gates_invalid")
    expected_components = set(reference.mapped_component_ids())
    report_components = set()
    for family in report["families"]:
        report_components.update(item["component_id"] for item in family["components"])
    for lead in report["source_leads"]:
        report_components.update(lead["mapped_component_ids"])
    if report_components != expected_components:
        errors.append("mapped_component_set_mismatch")
    if any(item["classification"] != "source_reported_not_reproduced"
           for item in report["historical_executions"]):
        errors.append("historical_source_report_promoted")
    if any(item["classification"] != "task_local_synthetic_reference_only"
           or item["qualifies_candidate"] is not False
           for item in report["task_local_executions"]):
        errors.append("task_local_evidence_promoted")
    expected_gaps = {gap["id"] for gap in reference.GAPS}
    report_gaps = {gap["id"] for gap in report["gaps"]}
    if report_gaps != expected_gaps:
        errors.append("gap_set_mismatch")
    tasks = inputs["tasks"]
    for gap in report["gaps"]:
        task = tasks.get(gap["followup_task_id"])
        if task is None or task["mode"] != "feasibility":
            errors.append("gap_not_linked_to_feasibility:" + gap["id"])
        elif (gap["followup_mode"] != "feasibility"
              or gap["followup_status"] != task["status"]
              or gap["linked_on_board"] is not True
              or gap["new_task_created"] is not False):
            errors.append("gap_board_fields_mismatch:" + gap["id"])
    if len(report["gates"]) != len(reference.GATE_NAMES) or any(
            gate["status"] != "blocked" or not gate["reopen_condition"]
            for gate in report["gates"]):
        errors.append("release_gates_not_blocked")
    state = reference.state_snapshot(inputs)
    if report["state_sha256"] != reference.state_digest(state):
        errors.append("state_snapshot_mismatch")
    fresh_adverse = reference.adverse(state)
    if report["adverse"] != fresh_adverse:
        errors.append("adverse_section_not_reproduced")
    if not fresh_adverse["all_rejected"] or not fresh_adverse["all_state_unchanged"]:
        errors.append("adverse_validation_not_strict")
    for case in report["adverse"]["cases"]:
        if case["status"] != "rejected" or case["state_unchanged"] is not True:
            errors.append("adverse_case_accepted:" + case["name"])
    repeat = report["repeatability"]
    fresh_repeat = reference.repeatability()
    if (repeat["count"] != 3 or repeat["byte_identical"] is not True
            or repeat["digests"] != fresh_repeat["digests"]
            or len(set(repeat["digests"])) != 1):
        errors.append("cold_start_repeat_mismatch")
    return report


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in ("SOURCES.sha256.license", "contract.json.license",
                 "report.json.license", "report.json.sha256.license"):
        text = (HERE / name).read_text(encoding="utf-8") if (HERE / name).is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml_docs_coverage_missing")


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
    changed = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            changed.append(path)
            if not path.startswith(reference.TASK_PREFIX):
                errors.append("out_of_scope_change:" + path)
    diff = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"],
                          capture_output=True, text=True)
    if diff.returncode != 0:
        errors.append("git_diff_check_failed:" + diff.stdout.strip())
    pinned = {reference.TASK_PREFIX + name for name in reference.LOCAL_PIN_PATHS}
    pinned.add(reference.TASK_PREFIX + "SOURCES.sha256")
    for path in sorted(HERE.iterdir()):
        if path.is_file() and reference.TASK_PREFIX + path.name not in pinned:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    report = check_report(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digest = reference.sha256(REPORT.read_bytes()) if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"pins_ok={pins == len(allowed_pins()) and not errors} "
              f"json_ok={bool(report)} reproduction_ok={not any('canonical' in e or 'sidecar' in e or 'repeat' in e for e in errors)} "
              f"report_sha256={digest} changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} files={len(changed)} profile=rate "
          f"status={report['status']} decision={report['decision']} "
          f"report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
