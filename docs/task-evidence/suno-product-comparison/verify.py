# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-SUNO-PRODUCT-COMPARISON blocker package.

Checks exact pins, strict JSON, canonical bytes, report/contract regeneration,
report digest sidecar, README digest tables, disposition/gates, external
artifact absence, strict rejection controls, SPDX sidecars, task-local scope,
whitespace and test count. Never writes and never hashes the mutable full
``plan/swarm/TASKS.json``.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
README = HERE / "README.md"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".license", ".txt"}

def _strict_json(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        errors.append("strict_json_failed:" + label + ":" + str(error))
        return {}
    if not isinstance(payload, dict):
        errors.append("json_root_not_object:" + label)
        return {}
    return payload

def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label)

def check_pins(errors: List[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    try:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
    except Exception as error:
        errors.append("strict_pin_rejection:" + str(error))
        return 0
    expected = reference.allowed_pin_keys()
    if set(p for _, p in pins) != expected:
        errors.append("incomplete_pin_manifest")
    for digest, raw in pins:
        if raw.startswith("source:"):
            path = reference.resolve_source_path(raw.split(":", 1)[1])
        elif raw.startswith("sdk:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw
        if not path.is_file():
            errors.append("pin_target_missing:" + raw)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("SOURCES.sha256_not_deterministic_bytes")
    return len(pins)

def check_json(errors: List[str]) -> Dict[str, Dict[str, Any]]:
    payloads = {
        "contract": _strict_json(CONTRACT, errors, "contract"),
        "report": _strict_json(REPORT, errors, "report"),
    }
    if not all(payloads.values()):
        return payloads
    if CONTRACT.read_bytes() != reference.contract_bytes():
        errors.append("contract_not_canonical_bytes")
    if REPORT.read_bytes() != reference.canonical_report_bytes(payloads["report"]):
        errors.append("report_not_canonical_bytes")
    if REPORT.read_bytes() != reference.canonical_report_bytes():
        errors.append("report_not_regenerated_bytes")
    second = reference.canonical_report_bytes(reference.build_report())
    third = reference.canonical_report_bytes(reference.build_report())
    if REPORT.read_bytes() != second or second != third:
        errors.append("report_not_cold_start_deterministic")
    report_digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
    expected_sidecar = f"{report_digest}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    if payloads["report"].get("contract_sha256") != hashlib.sha256(
            CONTRACT.read_bytes()).hexdigest():
        errors.append("report_contract_digest_mismatch")
    for name, payload in payloads.items():
        if reference.has_negative_zero(payload):
            errors.append("negative_zero_in_artifact:" + name)
    return payloads

def check_content(errors: List[str], payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads.get("report", {})
    contract = payloads.get("contract", {})
    if not report or not contract:
        return
    _eq(errors, "report_key_set_mismatch", set(report), reference.REQUIRED_REPORT_KEYS)
    _eq(errors, "contract_key_set_mismatch", set(contract), reference.REQUIRED_CONTRACT_KEYS)
    _eq(errors, "base_commit_mismatch", report.get("base_commit"), reference.BASE_COMMIT)
    _eq(errors, "branch_mismatch", report.get("branch"), reference.BRANCH)
    _eq(errors, "profile_not_applied", report.get("profile"), reference.PROFILE)
    _eq(errors, "contract_profile_not_applied", contract.get("profile"), reference.PROFILE)
    _eq(errors, "report_proposal_only", report.get("proposal_only"), True)
    _eq(errors, "contract_proposal_only", contract.get("proposal_only"), True)
    for key, expected in (
            ("task_id", reference.TASK),
            ("title", reference.TITLE),
            ("component_id", reference.COMPONENT),
            ("status", reference.STATUS),
            ("evidence_status", reference.EVIDENCE_STATUS),
            ("qualification_status", reference.QUALIFICATION),
            ("decision", reference.DECISION),
            ("defer_before", reference.DEFER_BEFORE)):
        _eq(errors, "report_disposition_mismatch:" + key, report.get(key), expected)
        if key != "component_id":
            _eq(errors, "contract_disposition_mismatch:" + key, contract.get(key), expected)

    qualification = report.get("qualification", {})
    _eq(errors, "qualification_status_nested", qualification.get("status"), reference.QUALIFICATION)
    _eq(errors, "qualification_not_qualified", qualification.get("not_qualified"), True)
    _eq(errors, "qualification_readiness", qualification.get("readiness"), "incomplete")
    _eq(errors, "qualification_missing_result_promoted", qualification.get("missing_result_promoted"), False)
    _eq(errors, "qualification_release_claim", qualification.get("release_claim"), False)
    _eq(errors, "qualification_all_release_gates_blocked", qualification.get("all_release_gates_blocked"), True)
    _eq(errors, "qualification_contract_status", contract.get("qualification", {}).get("status"), reference.QUALIFICATION)

    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")
    if not report.get("missing_results"):
        errors.append("missing_results_empty")
    if not report.get("negative_claims"):
        errors.append("negative_claims_empty")

    board = report.get("board_row", {})
    _eq(errors, "board_full_file_hashed", board.get("full_tasks_json_hashed"), False)
    _eq(errors, "board_stable_sha256_mismatch", board.get("stable_sha256"), reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "board_stable_fields_mismatch", board.get("stable_fields"), reference.BOARD_ROW_STABLE_FIELDS)
    _eq(errors, "board_digest_function", reference.board_row_digest(), reference.BOARD_ROW_STABLE_SHA256)

    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("gate_count_not_eight")
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("gate_not_blocked:" + str(gate.get("id")))

    boundary = report.get("boundary", {})
    for k, v in boundary.items():
        if k == "descriptor_settings":
            if v != {}:
                errors.append("boundary_descriptor_settings_not_empty")
        elif v is not False:
            errors.append("boundary_not_false:" + k)

    scope = report.get("scope", {})
    for k in ("benchmark_run", "device_timing_measured", "downloaded", "implementation_added",
              "listening_performed", "network_used", "provider_registered", "public_abi_changed",
              "real_assets_used", "registry_or_default_changed", "release_claim", "runtime_executed",
              "shared_build_or_ci_changed", "source_imported", "weights_loaded"):
        if scope.get(k) is not False:
            errors.append("scope_not_false:" + k)
    if scope.get("task_local_only") is not True:
        errors.append("scope_not_task_local_only")

    controls = report.get("controls", {})
    for name in ("comparison_digest", "missing_artifacts", "nonfinite", "record_adverse", "scope"):
        if name not in controls:
            errors.append("control_missing:" + name)
    if controls.get("record_adverse", {}).get("rejected_all") is not True:
        errors.append("record_adverse_not_rejected_all")
    if controls.get("nonfinite", {}).get("rejected_all") is not True:
        errors.append("nonfinite_not_rejected_all")
    if controls.get("missing_artifacts", {}).get("no_missing_result_qualifies") is not True:
        errors.append("missing_artifacts_rule_failed")
    if controls.get("comparison_digest", {}).get("byte_identical_digest") is not True:
        errors.append("comparison_digest_not_stable")

def check_readme(errors: List[str]) -> None:
    if not README.is_file():
        errors.append("README missing")
        return
    text = README.read_text(encoding="utf-8")
    try:
        tables = reference.parse_readme_tables(text)
    except Exception as error:
        errors.append("readme_table_parse:" + str(error))
        return
    expected = reference.expected_readme_keys()
    for section in reference.README_SECTIONS:
        actual = {k for k, _, _ in tables.get(section, [])}
        if actual != expected[section]:
            errors.append("readme_keys_mismatch:" + section)
    for section in ("source", "boundary"):
        for key, digest, _ in tables.get(section, []):
            if section == "source":
                want = reference.SOURCE_PINS.get(key.split(":", 1)[1])
            else:
                want = reference.BOUNDARY_PINS.get(key.split(":", 1)[1])
            if want != digest:
                errors.append("readme_digest_mismatch:" + key)
    for name, digest, size in tables.get("artifacts", []):
        p = HERE / name
        if not p.exists():
            errors.append("readme_artifact_missing:" + name)
            continue
        if reference.sha256_file(p) != digest:
            errors.append("readme_artifact_digest_mismatch:" + name)
        if size != p.stat().st_size:
            errors.append("readme_artifact_size_mismatch:" + name)
    if reference.update_readme_artifact_table(text) != text:
        errors.append("readme_artifact_table_stale")

def check_scope_and_text(errors: List[str]) -> None:
    actual = {p.name for p in HERE.iterdir() if p.is_file()}
    if actual != reference.EXPECTED_DIR_FILES:
        errors.append("task_local_file_set_mismatch")
    for name in LICENSE_SIDECARS:
        p = HERE / name
        if not p.is_file():
            errors.append("license_sidecar_missing:" + name)
            continue
        text = p.read_text(encoding="utf-8")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("license_sidecar_missing_spdx:" + name)
    for p in HERE.rglob("*"):
        if not p.is_file() or p.suffix not in TEXT_SUFFIXES:
            continue
        data = p.read_bytes()
        if b"\r\n" in data:
            errors.append("crlf:" + p.name)
        if data and not data.endswith(b"\n"):
            errors.append("missing_final_newline:" + p.name)
        if b"\n\n\n" in data:
            errors.append("excess_blank_lines:" + p.name)

def check_tests(errors: List[str]) -> int:
    test_file = HERE / "test_reference.py"
    if not test_file.is_file():
        errors.append("test_reference.py missing")
        return 0
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "test_reference"],
        cwd=str(HERE),
        capture_output=True,
        text=True,
        env={**dict(os.environ), "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    if proc.returncode != 0:
        errors.append("unittest_failed")
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    count = 0
    for line in (proc.stderr + "\n" + proc.stdout).splitlines():
        if line.startswith("Ran ") and " test" in line:
            try:
                count = int(line.split()[1])
            except Exception:
                pass
    if count < 10:
        errors.append("test_count_too_low")
    return count

def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    payloads = check_json(errors)
    check_content(errors, payloads)
    check_readme(errors)
    check_scope_and_text(errors)
    test_count = check_tests(errors)
    if errors:
        print("VERIFY FAIL")
        for e in errors:
            print("-", e)
        return 1
    print(
        "VERIFY PASS "
        f"pins={pins} tests={test_count} "
        f"report_sha256={hashlib.sha256(REPORT.read_bytes()).hexdigest()} "
        f"decision={reference.DECISION} status={reference.STATUS} "
        f"qualification={reference.QUALIFICATION} gates={len(reference.GATE_REQUIREMENTS)}"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
