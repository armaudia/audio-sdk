# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-SPEECH-RATE-METER-INTON-CORE blocker package."""

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
    except Exception as error:  # noqa: BLE001
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
    except Exception as error:  # noqa: BLE001
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
    if payloads["report"].get("contract_sha256") != hashlib.sha256(CONTRACT.read_bytes()).hexdigest():
        errors.append("report_contract_digest_mismatch")
    for name, payload in payloads.items():
        if reference.has_negative_zero(payload):
            errors.append("negative_zero_in_artifact:" + name)
    return payloads


def check_content(errors: List[str], payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]
    _eq(errors, "base_commit_mismatch", report.get("base_commit"), reference.BASE_COMMIT)
    _eq(errors, "branch_mismatch", report.get("branch"), reference.BRANCH)
    _eq(errors, "profile_mismatch", report.get("profile"), reference.PROFILE)
    _eq(errors, "contract_profile_mismatch", contract.get("profile"), reference.PROFILE)
    for key, expected in (
        ("task_id", reference.TASK),
        ("title", reference.TITLE),
        ("component_id", reference.COMPONENT),
        ("status", reference.STATUS),
        ("evidence_status", reference.EVIDENCE_STATUS),
        ("qualification_status", reference.QUALIFICATION),
        ("decision", reference.DECISION),
        ("defer_before", reference.DEFER_BEFORE),
    ):
        _eq(errors, "report_disposition:" + key, report.get(key), expected)
        if key != "component_id":
            _eq(errors, "contract_disposition:" + key, contract.get(key), expected)
    qualification = report.get("qualification", {})
    _eq(errors, "qualification_status_nested", qualification.get("status"), reference.QUALIFICATION)
    _eq(errors, "qualification_not_qualified", qualification.get("not_qualified"), True)
    _eq(errors, "qualification_release_claim", qualification.get("release_claim"), False)
    _eq(errors, "qualification_missing_result_promoted", qualification.get("missing_result_promoted"), False)
    board = report.get("board_row", {})
    _eq(errors, "board_full_file_hashed", board.get("full_tasks_json_hashed"), False)
    _eq(errors, "board_stable_sha256", board.get("stable_sha256"), reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "board_stable_fields", board.get("stable_fields"), reference.BOARD_ROW_STABLE_FIELDS)
    _eq(errors, "board_digest_function", reference.board_row_digest(), reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "contract_board_sha", contract.get("board_row", {}).get("stable_sha256"), reference.BOARD_ROW_STABLE_SHA256)
    gates = report.get("gates", [])
    _eq(errors, "gate_count", len(gates), 8)
    if any(g.get("status") != "blocked" for g in gates):
        errors.append("gate_not_blocked")
    if any(g.get("qualifies") is not False for g in gates):
        errors.append("gate_qualifies")
    contract_gates = contract.get("gates", [])
    _eq(errors, "contract_gate_count", len(contract_gates), 8)
    if any(g.get("status") != "blocked" for g in contract_gates):
        errors.append("contract_gate_not_blocked")
    _eq(errors, "blocker_count", len(report.get("exact_blockers", [])), len(reference.EXACT_BLOCKERS))
    _eq(errors, "contract_blocker_count", len(contract.get("exact_blockers", [])), len(reference.EXACT_BLOCKERS))
    _eq(errors, "boundary_mismatch", report.get("boundary"), reference.BOUNDARY)
    _eq(errors, "contract_boundary_mismatch", contract.get("boundary"), reference.BOUNDARY)
    _eq(errors, "scope_mismatch", report.get("scope"), reference.SCOPE)
    _eq(errors, "contract_scope_mismatch", contract.get("scope"), reference.SCOPE)
    _eq(errors, "caller_asset_contract_mismatch", report.get("caller_asset_contract"), reference.CALLER_ASSET_CONTRACT)
    _eq(errors, "negative_claims_empty", bool(report.get("negative_claims")), True)
    _eq(errors, "missing_results_empty", bool(report.get("missing_results")), True)
    _eq(errors, "no_missing_result_qualifies", report.get("no_missing_result_qualifies_candidate"), True)
    _eq(errors, "proposal_only", report.get("proposal_only"), True)
    _eq(errors, "contract_proposal_only", contract.get("proposal_only"), True)
    _eq(errors, "upstream_commit", report.get("upstream", {}).get("commit"), None)
    _eq(errors, "upstream_source_present", report.get("upstream", {}).get("source_present"), False)
    controls = report.get("controls", {})
    for name in ("asset", "adverse"):
        c = controls.get(name, {})
        if not c:
            errors.append("control_missing:" + name)
    if controls.get("adverse", {}).get("valid_control", {}).get("qualified") is not False:
        errors.append("surrogate_control_promoted")
    if controls.get("surrogate_run", {}).get("qualified") is not False:
        errors.append("surrogate_run_promoted")


def check_external_absence(errors: List[str]) -> None:
    probes = [
        SDK_ROOT / "data/checkouts/speech-rate-meter",
        SDK_ROOT / "data/envs/speech-rate-meter-inton-core",
        SDK_ROOT / "adapters/speech-rate-meter-inton-core",
    ]
    for p in probes:
        if p.exists():
            errors.append("external_probe_present:" + str(p.relative_to(SDK_ROOT)))


def check_readme(errors: List[str]) -> int:
    try:
        text = README.read_text(encoding="utf-8")
    except Exception as error:  # noqa: BLE001
        errors.append("README_unreadable:" + str(error))
        return 0
    required = ["DEFER", "not_qualified", "incomplete", "blocked", "speech-rate-meter / inton-core"]
    for phrase in required:
        if phrase not in text:
            errors.append("README_missing_phrase:" + phrase)
    try:
        counts = reference.verify_readme_digests(text)
    except Exception as error:  # noqa: BLE001
        errors.append("README_digest_mismatch:" + str(error))
        return 0
    if text != reference.update_readme_artifact_table(text):
        errors.append("README_artifact_table_stale")
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
    text = README.read_text(encoding="utf-8") if README.exists() else ""
    if f"<!-- {SPDX_COPYRIGHT} -->" not in text or f"<!-- {SPDX_LICENSE} -->" not in text:
        errors.append("missing_markdown_spdx:README.md")
    for name in LICENSE_SIDECARS:
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


def check_scope(errors: List[str]) -> int:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return 0
    changed: List[str] = []
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
            errors.append("git_" + "_".join(args).replace("-", "") + "_failed")
    expected_files = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
    actual_files = {p.name for p in HERE.iterdir() if p.is_file()}
    if actual_files != expected_files:
        for name in sorted(actual_files - expected_files):
            errors.append("unpinned_task_file:" + name)
        for name in sorted(expected_files - actual_files):
            errors.append("pinned_task_file_missing:" + name)
    for path in sorted(HERE.iterdir()):
        if path.is_dir():
            errors.append("unexpected_subdirectory:" + path.name)
    if any(HERE.rglob("__pycache__")) or any(HERE.rglob("*.pyc")):
        errors.append("bytecode_cache_present")
    for path in sorted(HERE.glob("*")):
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            data = path.read_bytes()
            if b"\r" in data:
                errors.append("crlf_in_text_file:" + path.name)
            for n, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
                if line.rstrip() != line:
                    errors.append(f"trailing_whitespace:{path.name}:{n}")
                    break
    return len(changed)


def check_tests(errors: List[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = sum(1 for line in text.splitlines() if line.startswith("    def test_"))
    if count < 20:
        errors.append("fewer_than_20_reference_tests:" + str(count))
    return count


def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    payloads = check_json(errors)
    if all(payloads.values()):
        check_content(errors, payloads)
    check_external_absence(errors)
    readme_rows = check_readme(errors)
    strict_count = check_strict_rejections(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    tests = check_tests(errors)
    digest = hashlib.sha256(REPORT.read_bytes()).hexdigest() if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"pins={pins} readme_rows={readme_rows} strict_rejections={strict_count} report_sha256={digest} failures={len(errors)}")
        return 1
    print(
        f"PASS pins={pins} json_ok=2 readme_rows={readme_rows} strict_rejections_ok={strict_count} "
        f"licensing_ok=1 scope_ok=1 tests={tests} changed_files={changed} "
        f"profile={reference.PROFILE} status={reference.STATUS} qualification={reference.QUALIFICATION} "
        f"decision={reference.DECISION} report_sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
