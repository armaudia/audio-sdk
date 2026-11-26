# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for SDK-TARGET-SPEAKER-EXTRACTION-FAMILY blocker package."""

from __future__ import annotations

import hashlib
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
LICENSE_SIDECARS = ("SOURCES.sha256.license", "contract.json.license", "report.json.license", "report.json.sha256.license")
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".license", ".txt"}


def _strict_json(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
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
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_pin_rejection:" + str(error))
        return 0
    expected = reference.allowed_pin_keys()
    if len(pins) != len(expected):
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
    payloads = {"contract": _strict_json(CONTRACT, errors, "contract"), "report": _strict_json(REPORT, errors, "report")}
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
    if payloads["report"].get("contract_sha256") != hashlib.sha256(CONTRACT.read_bytes()).hexdigest():
        errors.append("report_contract_digest_mismatch")
    for name, payload in payloads.items():
        if reference.has_negative_zero(payload):
            errors.append("negative_zero_in_artifact:" + name)
    return payloads


def check_content(errors: List[str], payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]
    _eq(errors, "report_key_set_mismatch", set(report), reference.REQUIRED_REPORT_KEYS)
    _eq(errors, "contract_key_set_mismatch", set(contract), reference.REQUIRED_CONTRACT_KEYS)
    for key, expected in (("task_id", reference.TASK), ("title", reference.TITLE), ("component_id", reference.COMPONENT), ("status", reference.STATUS), ("evidence_status", reference.EVIDENCE_STATUS), ("qualification_status", reference.QUALIFICATION), ("decision", reference.DECISION), ("defer_before", reference.DEFER_BEFORE), ("profile", reference.PROFILE)):
        _eq(errors, "report_disposition_mismatch:" + key, report.get(key), expected)
        if key in contract:
            _eq(errors, "contract_disposition_mismatch:" + key, contract.get(key), expected)
    _eq(errors, "report_proposal_only", report.get("proposal_only"), True)
    _eq(errors, "contract_proposal_only", contract.get("proposal_only"), True)
    _eq(errors, "qualification_not_qualified", report.get("qualification", {}).get("status"), reference.QUALIFICATION)
    _eq(errors, "contract_qualification_not_qualified", contract.get("qualification", {}).get("status"), reference.QUALIFICATION)
    _eq(errors, "no_missing_result_rule", report.get("no_missing_result_qualifies_candidate"), True)
    _eq(errors, "board_full_file_hashed", report.get("board_row", {}).get("full_tasks_json_hashed"), False)
    _eq(errors, "board_stable_sha256", report.get("board_row", {}).get("stable_sha256"), reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "board_stable_fields", report.get("board_row", {}).get("stable_fields"), reference.BOARD_ROW_STABLE_FIELDS)
    _eq(errors, "board_digest_function", reference.board_row_digest(), reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "contract_board_sha", contract.get("board_row", {}).get("stable_sha256"), reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "contract_board_full_file_hashed", contract.get("board_row", {}).get("full_tasks_json_hashed"), False)
    _eq(errors, "contract_sha256_mismatch", report.get("contract_sha256"), hashlib.sha256(CONTRACT.read_bytes()).hexdigest())
    _eq(errors, "gate_count", len(report.get("gates", [])), 8)
    if any(g.get("status") != "blocked" or g.get("qualifies") is not False for g in report.get("gates", [])):
        errors.append("gate_not_blocked")
    if any(g.get("status") != "blocked" or g.get("qualifies") is not False for g in contract.get("gates", [])):
        errors.append("contract_gate_not_blocked")
    _eq(errors, "blocker_count", len(report.get("exact_blockers", [])), len(reference.EXACT_BLOCKERS))
    _eq(errors, "boundary_mismatch", report.get("boundary"), reference.BOUNDARY)
    _eq(errors, "contract_boundary_mismatch", contract.get("boundary"), reference.BOUNDARY)
    _eq(errors, "scope_mismatch", report.get("scope"), reference.SCOPE)
    _eq(errors, "contract_scope_mismatch", contract.get("scope"), reference.SCOPE)
    _eq(errors, "scope_task_local_only", report.get("scope", {}).get("task_local_only"), True)
    _eq(errors, "caller_asset_contract_mismatch", report.get("caller_asset_contract"), reference.CALLER_ASSET_CONTRACT)
    _eq(errors, "contract_caller_asset_mismatch", contract.get("caller_asset_contract"), reference.CALLER_ASSET_CONTRACT)
    upstream = report.get("upstream", {})
    if upstream.get("commit") is not None or upstream.get("license") is not None or upstream.get("checkpoint_identity") is not None:
        errors.append("upstream_identity_fabricated")
    _eq(errors, "upstream_source_present", upstream.get("source_present"), False)
    metrics = report.get("metrics", {})
    _eq(errors, "metrics_candidate_result", metrics.get("candidate_result"), False)
    _eq(errors, "metrics_surrogate_only", metrics.get("surrogate_only"), True)
    controls = report.get("controls", {})
    for name in ("asset", "config", "frame"):
        _eq(errors, "control_rejected_all:" + name, controls.get(name, {}).get("rejected_all"), True)
    _eq(errors, "streaming_parity", controls.get("streaming_parity", {}).get("all_identical"), True)
    _eq(errors, "reset_match", controls.get("reset", {}).get("fresh_matches_reset"), True)
    _eq(errors, "silence_exact_zero", controls.get("silence", {}).get("exact_zero"), True)
    _eq(errors, "delay_matches", controls.get("delay", {}).get("matches"), True)
    _eq(errors, "mono_rejected", controls.get("multichannel", {}).get("mono_rejected"), True)


def check_external_absence(errors: List[str]) -> None:
    for key, path in ():
        if reference.resolve_source_path(path).exists():
            errors.append("external_" + key + "_present_but_report_says_absent")
    # No fabricated upstream identity allowed
    report = reference.build_report()
    up = report.get("upstream", {})
    if any(up.get(k) is not None for k in ("commit", "license", "checkpoint_identity")):
        errors.append("upstream_identity_fabricated")


def check_readme(errors: List[str]) -> int:
    try:
        counts = reference.verify_readme_digests(README.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return 0
    expected = reference.expected_readme_keys()
    for name in reference.README_SECTIONS:
        if counts.get(name) != len(expected[name]):
            errors.append("readme_section_count_mismatch:" + name)
    if README.read_text(encoding="utf-8") != reference.update_readme_artifact_table(README.read_text(encoding="utf-8")):
        errors.append("readme_artifact_table_stale")
    return sum(counts.values())


def check_strict_rejections(errors: List[str]) -> int:
    result = reference.strict_rejection_examples()
    for key, total in (("bad_json", "bad_json_total"), ("bad_pins", "bad_pins_total"), ("bad_readme", "bad_readme_total")):
        if result[key + "_rejected"] != result[total]:
            errors.append("strict_parser_accepted_bad_" + key)
    return result["bad_json_rejected"] + result["bad_pins_rejected"] + result["bad_readme_rejected"]


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    text = README.read_text(encoding="utf-8")
    if f"<!-- {SPDX_COPYRIGHT} -->" not in text or f"<!-- {SPDX_LICENSE} -->" not in text:
        errors.append("missing_markdown_spdx:README.md")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        sidecar = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in sidecar or SPDX_COPYRIGHT not in sidecar:
            errors.append("missing_license_sidecar:" + name)


def check_whitespace(errors: List[str]) -> None:
    for path in sorted(HERE.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(HERE).as_posix()
        data = path.read_bytes()
        if b"\r" in data:
            errors.append("crlf:" + rel)
        if data and not data.endswith(b"\n"):
            errors.append("missing_final_newline:" + rel)
        for n, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), start=1):
            if line != line.rstrip():
                errors.append(f"trailing_whitespace:{rel}:{n}")
                break


def check_scope(errors: List[str]) -> None:
    payload = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", reference.TASK_PREFIX], cwd=SDK_ROOT, check=True, capture_output=True, text=True)
    for raw in payload.stdout.splitlines():
        rel = raw.strip()
        if not rel:
            continue
        name = Path(rel).name
        if name not in reference.LOCAL_FILES:
            errors.append("scope_escape:" + rel)


def check_tests(errors: List[str]) -> int:
    proc = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_reference.py"], cwd=HERE, capture_output=True, text=True)
    if proc.returncode != 0:
        errors.append("test_reference_failed")
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
    count = 0
    for line in (proc.stdout + proc.stderr).splitlines():
        if "Ran " in line and " test" in line:
            parts = line.split()
            for i, p in enumerate(parts):
                if p == "Ran" and i + 1 < len(parts):
                    try:
                        count = int(parts[i + 1])
                    except ValueError:
                        pass
    return count


def main() -> int:
    errors: List[str] = []
    pin_count = check_pins(errors)
    payloads = check_json(errors)
    if all(payloads.values()):
        check_content(errors, payloads)
    check_external_absence(errors)
    readme_count = check_readme(errors)
    rejection_count = check_strict_rejections(errors)
    check_licensing(errors)
    check_whitespace(errors)
    check_scope(errors)
    test_count = check_tests(errors)
    report = payloads.get("report", {})
    if errors:
        print(f"VERIFY FAIL: pin_entries={pin_count} readme_rows={readme_count} rejections={rejection_count} tests={test_count}")
        for error in errors:
            print(error)
        return 1
    print(f"VERIFY PASS: decision={report.get('decision')} status={report.get('status')} qualification={report.get('qualification_status')} gates={len(report.get('gates',[]))} pin_entries={pin_count} readme_rows={readme_count} rejections={rejection_count} tests={test_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
