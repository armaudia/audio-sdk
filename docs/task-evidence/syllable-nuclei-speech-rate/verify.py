# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for SDK-SYLLABLE-NUCLEI-SPEECH-RATE blocker package."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

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


def _strict_json(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        payload = reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as error:  # noqa: BLE001
        errors.append("strict_json_failed:" + label + ":" + str(error))
        return {}
    if not isinstance(payload, dict):
        errors.append("json_root_not_object:" + label)
        return {}
    return payload


def _eq(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label)


def check_pins(errors: list[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    try:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
    except Exception as error:  # noqa: BLE001
        errors.append("strict_pin_rejection:" + str(error))
        return 0
    expected = reference.allowed_pin_keys()
    if len(pins) != len(expected):
        errors.append("incomplete_pin_manifest")
    for digest, raw in pins:
        path = reference.qualify_pin_path(raw)
        if not path.is_file():
            errors.append("pin_target_missing:" + raw)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("SOURCES.sha256_not_deterministic_bytes")
    return len(pins)


def check_json(errors: list[str]) -> dict[str, dict[str, Any]]:
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
    for name, payload in payloads.items():
        if reference.has_negative_zero(payload):
            errors.append("negative_zero_in_artifact:" + name)
    return payloads


def check_content(errors: list[str], payloads: dict[str, dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]
    for key, expected in (
        ("base_commit", reference.BASE_COMMIT),
        ("branch", reference.BRANCH),
        ("profile", reference.PROFILE),
        ("task_id", reference.TASK),
        ("title", reference.TITLE),
        ("component_id", reference.COMPONENT),
        ("status", reference.STATUS),
        ("evidence_status", reference.EVIDENCE_STATUS),
        ("qualification_status", reference.QUALIFICATION_STATUS),
        ("decision", reference.DECISION),
        ("defer_before", reference.DEFER_BEFORE),
    ):
        _eq(errors, "report:" + key, report.get(key), expected)
        _eq(errors, "contract:" + key, contract.get(key), expected)
    _eq(errors, "report_proposal_only", report.get("proposal_only"), True)
    _eq(errors, "report_no_missing_promoted", report.get("no_missing_result_qualifies_candidate"), True)
    board = report.get("board_row", {})
    _eq(errors, "board_full_hashed", board.get("full_tasks_json_hashed"), False)
    _eq(errors, "board_stable_sha", board.get("stable_sha256"), reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "board_stable_fields", board.get("stable_fields"), reference.BOARD_ROW_STABLE_FIELDS)
    _eq(errors, "board_digest", reference.board_row_digest(), reference.BOARD_ROW_STABLE_SHA256)
    gates = report.get("gates", [])
    _eq(errors, "gate_count", len(gates), 8)
    if any(g.get("status") != "blocked" for g in gates):
        errors.append("gate_not_blocked")
    if any(g.get("qualifies") is not False for g in gates):
        errors.append("gate_qualifies")
    cgates = contract.get("gates", [])
    _eq(errors, "contract_gate_count", len(cgates), 8)
    _eq(errors, "blocker_count", len(report.get("exact_blockers", [])), len(reference.EXACT_BLOCKERS))
    _eq(errors, "boundary", report.get("boundary"), reference.BOUNDARY)
    _eq(errors, "scope", report.get("scope"), reference.SCOPE)
    _eq(errors, "contract_boundary", contract.get("boundary"), reference.BOUNDARY)
    _eq(errors, "contract_scope", contract.get("scope"), reference.SCOPE)
    controls = report.get("controls", {})
    if not controls.get("adverse", {}).get("all_rejected"):
        errors.append("adverse_not_all_rejected")
    if controls.get("synthetic_surrogate", {}).get("qualified") is not False:
        errors.append("surrogate_promoted")
    if controls.get("synthetic_surrogate", {}).get("candidate_is_syllable_nuclei") is not False:
        errors.append("surrogate_claims_candidate")
    sr = report.get("candidate_source_reported", {})
    if sr.get("qualifies") is not False or sr.get("reproduced") is not False:
        errors.append("source_reported_promoted")
    if report.get("negative_claims") != list(reference.NEGATIVE_CLAIMS):
        errors.append("negative_claims_mismatch")


def check_readme(errors: list[str]) -> int:
    if not README.is_file():
        errors.append("README_missing")
        return 0
    text = README.read_text(encoding="utf-8")
    for phrase in ["DEFER", "not_qualified", "incomplete", "blocked", "Syllable-nuclei speech rate"]:
        if phrase not in text:
            errors.append("README_missing_phrase:" + phrase)
    try:
        counts = reference.verify_readme_digests(text)
    except Exception as error:  # noqa: BLE001
        errors.append("README_digest_mismatch:" + str(error))
        return 0
    if text != reference.update_readme_artifact_table(text):
        errors.append("README_artifact_table_stale")
    if f"<!-- {SPDX_COPYRIGHT} -->" not in text or f"<!-- {SPDX_LICENSE} -->" not in text:
        errors.append("missing_markdown_spdx:README.md")
    return sum(counts.values())


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in reference.LICENSE_SIDECARS:
        path = HERE / name
        sidecar = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in sidecar or SPDX_COPYRIGHT not in sidecar:
            errors.append("missing_license_sidecar:" + name)
    for path in sorted(HERE.glob("*.json")) + sorted(HERE.glob("*.sha256")):
        if not (HERE / (path.name + ".license")).is_file():
            errors.append("missing_sidecar_for:" + path.name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE_docs_coverage_missing")
    allowed = '"SPDX-License-" "Identifier: Apache-2.0"'
    token = "SPDX-License" + "-Identifier: Apache-2.0"
    for path in sorted(HERE.glob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        body = "\n".join(lines[2:])
        if token in body.replace(allowed, ""):
            errors.append("contiguous_spdx_token:" + path.name)


def check_scope(errors: list[str]) -> int:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("git_status_failed")
        return 0
    changed: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for args in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *args], capture_output=True, text=True, check=False)
        if diff.returncode != 0:
            errors.append("git_diff_check_failed:" + "_".join(args))
    expected_files = set(reference.LOCAL_FILES)
    actual_files = {p.name for p in HERE.iterdir() if p.is_file()}
    for name in sorted(actual_files - expected_files):
        errors.append("unexpected_task_file:" + name)
    for name in sorted(expected_files - actual_files):
        errors.append("missing_task_file:" + name)
    return len(changed)


def check_strict_rejections(errors: list[str]) -> int:
    result = reference.strict_rejection_examples()
    for key, total in (("bad_json", "bad_json_total"), ("bad_pins", "bad_pins_total"), ("bad_readme", "bad_readme_total")):
        if result[key + "_rejected"] != result[total]:
            errors.append("strict_parser_accepted_bad_" + key)
    return result["bad_json_rejected"] + result["bad_pins_rejected"] + result["bad_readme_rejected"]


def main() -> int:
    errors: list[str] = []
    checked_pins = check_pins(errors)
    payloads = check_json(errors)
    if payloads.get("report") and payloads.get("contract"):
        check_content(errors, payloads)
    checked_readme = check_readme(errors)
    check_licensing(errors)
    changed_files = check_scope(errors)
    strict_rejections = check_strict_rejections(errors)
    if errors:
        print("FAIL SDK-SYLLABLE-NUCLEI-SPEECH-RATE", len(errors))
        for e in errors:
            print(" -", e)
        return 1
    report_digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
    print(
        "PASS SDK-SYLLABLE-NUCLEI-SPEECH-RATE "
        f"report_sha256={report_digest} "
        f"checked_pins={checked_pins} "
        f"checked_readme_rows={checked_readme} "
        f"strict_rejections={strict_rejections} "
        f"scope_changes={changed_files}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
