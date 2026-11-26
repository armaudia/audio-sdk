# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the sinusoidal SMS TSM evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on duplicate-key/nonfinite JSON, stale pins, stale canonical
artifacts, a stale README digest table, unpinned or vendored files, license
gaps, branch-diff scope changes outside this task directory, whitespace damage
or a dirty diff check. Never writes.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
SOURCES = HERE / "SOURCES.sha256"
README = HERE / "README.md"
REUSE_CONFIG = SDK_ROOT / "REUSE.toml"
SPDX_LICENSE = reference.SPDX_LICENSE
SPDX_COPYRIGHT = reference.SPDX_COPYRIGHT
LICENSE_SIDECARS = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)


def _fail(message: str, errors: List[str]) -> None:
    errors.append(message)


def _eq(errors: List[str], message: str, left: Any, right: Any) -> None:
    if left != right:
        _fail(message, errors)


def check_json(errors: List[str]) -> Dict[str, Any]:
    report = None
    contract = None
    for path in (REPORT, CONTRACT):
        try:
            text = path.read_text(encoding="utf-8")
            value = reference.strict_loads(text)
        except (OSError, ValueError, UnicodeError) as error:
            _fail("invalid_json:" + path.name + ":" + str(error), errors)
            continue
        if path == REPORT:
            report = value
        else:
            contract = value
    if not isinstance(report, dict) or not isinstance(contract, dict):
        return {}
    _eq(errors, "contract_schema_differs", contract.get("schema_id"),
        reference.SCHEMA_CONTRACT)
    _eq(errors, "report_schema_differs", report.get("schema_id"),
        reference.SCHEMA_REPORT)
    for key in ("task_id", "title", "component_id", "repository", "base_commit",
                "branch", "profile", "decision", "defer_before", "evidence_status",
                "qualification_status", "status", "format", "boundary", "scope",
                "gates", "exact_blockers", "negative_claims", "board_link",
                "caller_supplied_asset_contract", "source_reported",
                "asset_ledger"):
        _eq(errors, "contract/report differ:" + key, contract.get(key),
            report.get(key))
    return {"report": report, "contract": contract}


def check_boundary(report: Dict[str, Any], contract: Dict[str, Any],
                   errors: List[str]) -> None:
    boundary = contract.get("boundary", {})
    if not isinstance(boundary, dict):
        _fail("boundary_not_object", errors)
        return
    for key, value in boundary.items():
        if key == "format":
            continue
        if value is not False:
            _fail("boundary_flag_not_false:" + key, errors)
    _eq(errors, "boundary_format_mismatch", boundary.get("format"),
        report.get("format"))
    scope = contract.get("scope", {})
    if not isinstance(scope, dict):
        _fail("scope_not_object", errors)
        return
    if (scope.get("synthetic_only") is not True
            or scope.get("task_local_only") is not True):
        _fail("scope_controls_not_true", errors)
    for key, value in scope.items():
        if key not in {"synthetic_only", "task_local_only"} and value is not False:
            _fail("scope_flag_not_false:" + key, errors)
    _eq(errors, "report_scope_mismatch", report.get("scope"), scope)

    _eq(errors, "decision_must_be_defer", report.get("decision"), "DEFER")
    _eq(errors, "defer_before_mismatch", report.get("defer_before"),
        "opt_in_adapter_exposure")
    _eq(errors, "evidence_status_must_be_incomplete", report.get("evidence_status"),
        "incomplete")
    _eq(errors, "qualification_must_be_not_qualified",
        report.get("qualification_status"), "not_qualified")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        _fail("missing_result_may_not_qualify", errors)

    evidence_classes = report.get("evidence_classes", {})
    for key in ("real_local_model_output", "real_audio", "listening",
                "device_timing", "benchmark"):
        if evidence_classes.get(key) is not False:
            _fail("evidence_class_claimed:" + key, errors)
    if (evidence_classes.get("source_reported") is not True
            or evidence_classes.get("synthetic") is not True):
        _fail("evidence_classes_not_labelled", errors)

    gates = report.get("gates", [])
    if not isinstance(gates, list) or len(gates) != 8:
        _fail("gate_count_mismatch", errors)
    else:
        expected_ids = ["RG-0" + str(index) for index in range(1, 9)]
        if [gate.get("id") for gate in gates] != expected_ids:
            _fail("gate_ids_mismatch", errors)
        for gate in gates:
            if (not isinstance(gate, dict) or gate.get("status") != "blocked"
                    or gate.get("qualifies") is not False
                    or not gate.get("reopen_condition")):
                _fail("nonblocking_gate:" + str(gate), errors)

    blockers = report.get("exact_blockers", [])
    if not isinstance(blockers, list) or len(blockers) != 4:
        _fail("blocker_count_mismatch", errors)
    else:
        expected_blockers = ["XB-01", "XB-02", "XB-03", "XB-04"]
        if [item.get("id") for item in blockers] != expected_blockers:
            _fail("blocker_ids_mismatch", errors)
        for item in blockers:
            if not item.get("detail") or not item.get("reopen"):
                _fail("incomplete_blocker:" + str(item.get("id")), errors)

    caller = report.get("caller_supplied_asset_contract", {})
    if (caller.get("schema_id") != reference.SCHEMA_MANIFEST
            or caller.get("loaded") is not False
            or caller.get("executed") is not False
            or caller.get("configuration_pinned") is not False):
        _fail("caller_asset_boundary_not_fail_closed", errors)

    probe = report.get("asset_resolution", {})
    if probe.get("present") is not False or probe.get("present_paths") != []:
        _fail("unexpected_staged_sms_asset", errors)
    if (probe.get("workspace_probe_count", 0) < 1
            or probe.get("sdk_worktree_probe_count", 0) < 1
            or probe.get("home_cache_probe_count", 0) < 1):
        _fail("absent_artifact_probes_missing", errors)

    ledger = report.get("asset_ledger", {})
    if (ledger.get("source_checkout", {}).get("status") != "absent"
            or ledger.get("artifact", {}).get("present_locally") is not False
            or ledger.get("downloaded") is not False
            or ledger.get("vendored") is not False
            or ledger.get("loaded") is not False
            or ledger.get("executed") is not False
            or ledger.get("network_used") is not False):
        _fail("asset_ledger_not_absent", errors)

    profile = report.get("rate_profile", {})
    if (profile.get("qualifies_candidate") is not False
            or profile.get("matched_evidence") != (
                "blocked_no_pinned_source_runtime_or_cohort")):
        _fail("rate_profile_qualifies", errors)
    items = profile.get("items", {})
    for key in ("pitch_preservation", "transient_audibility", "playback_buffering",
                "unfamiliar_speech", "unfamiliar_music", "silence", "rebuffer",
                "pause_filler_source_timestamps", "speech_preservation",
                "chunked_vs_single_identity", "reset_replay_behavior"):
        status = items.get(key)
        if not isinstance(status, str) or not status.startswith("blocked"):
            _fail("rate_profile_item_not_blocked:" + key, errors)
    geometry = profile.get("geometry", {})
    if (geometry.get("qualifies_candidate") is not False
            or geometry.get("measured") is not False
            or geometry.get("identity_1x_bit_exact") is not True
            or geometry.get("final_partial_samples") != 37):
        _fail("geometry_probe_invalid", errors)

    align = report.get("alignment", {})
    if (align.get("first_output_ns") is not None
            or align.get("tail_ns") is not None
            or align.get("measured") is not False
            or align.get("device_timing") is not False):
        _fail("alignment_timing_claimed", errors)

    adverse = report.get("adverse", {})
    if (adverse.get("all_rejected") is not True
            or adverse.get("caller_manifest", {}).get("all_rejected") is not True
            or adverse.get("invalid_json", {}).get("all_rejected") is not True
            or adverse.get("invalid_pins", {}).get("all_rejected") is not True):
        _fail("adverse_cases_not_all_rejected", errors)
    manifest_cases = adverse.get("caller_manifest", {}).get("cases", [])
    matched = [item for item in manifest_cases
               if item.get("id") == "hash_matched_still_unpinned"]
    if (len(matched) != 1
            or matched[0].get("observed") != "SINUSOIDAL_SMS_SOURCE_IDENTITY_UNPINNED"):
        _fail("hash_matched_manifest_not_fail_closed", errors)

    reported = report.get("source_reported", {})
    if reported.get("qualifies") is not False:
        _fail("source_reported_qualifies", errors)
    if len(reported.get("entries", [])) != 8:
        _fail("source_entry_count_mismatch", errors)

    inventory = report.get("inventory_link", {})
    if (inventory.get("stable_sha256") != reference.INVENTORY_STABLE_SHA256
            or inventory.get("evidence_path") != reference.PLAYBACK_CENSUS):
        _fail("inventory_link_mismatch", errors)
    if report.get("board_link", {}).get("stable_sha256") != reference.BOARD_STABLE_SHA256:
        _fail("board_stable_sha256_mismatch", errors)
    if report.get("licensing_analysis", {}).get("qualifies") is not False:
        _fail("licensing_qualifies", errors)
    if len(report.get("reopening_conditions", [])) != 4:
        _fail("reopening_conditions_mismatch", errors)


def check_pins(errors: List[str]) -> None:
    for path, digest in reference.SOURCE_PINS.items():
        target = reference.SOURCE_ROOT / path
        if not target.is_file() or reference.sha256_file(target) != digest:
            _fail("source_pin_stale:" + path, errors)
    for path, digest in reference.BOUNDARY_PINS.items():
        target = reference.SDK_ROOT / path
        if not target.is_file() or reference.sha256_file(target) != digest:
            _fail("boundary_pin_stale:" + path, errors)
    fresh_report = reference.report_bytes()
    fresh_sidecar = reference.sidecar_bytes(fresh_report)
    try:
        rows = reference.parse_pin_lines(SOURCES.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        _fail("invalid_sources_manifest:" + str(error), errors)
        return
    expected = {key: digest for digest, key in reference.parse_pin_lines(
        reference.sources_bytes(fresh_report, fresh_sidecar).decode("utf-8"))}
    actual = {key: digest for digest, key in rows}
    if len(rows) != len(actual):
        _fail("duplicate_sources_rows", errors)
    if set(actual) != set(expected):
        _fail("sources_key_set_mismatch", errors)
    for key, digest in actual.items():
        target = reference.qualify_pin_path(key)
        if target.is_file() and reference.sha256_file(target) != digest:
            _fail("local_pin_stale:" + key, errors)
    if set(expected) != set(reference.allowed_pin_keys()):
        _fail("unexpected_pin_keys", errors)


def check_canonical(errors: List[str]) -> None:
    report_payload = reference.report_bytes()
    sidecar_payload = reference.sidecar_bytes(report_payload)
    sources_payload = reference.sources_bytes(report_payload, sidecar_payload)
    report = reference.strict_loads(report_payload.decode("utf-8"))
    contract_payload = reference.contract_bytes(
        report_payload, sidecar_payload, sources_payload, report)
    for path, payload in ((REPORT, report_payload), (SIDECAR, sidecar_payload),
                          (SOURCES, sources_payload), (CONTRACT, contract_payload)):
        if not path.is_file() or path.read_bytes() != payload:
            _fail("noncanonical_artifact:" + path.name, errors)
    sidecar = SIDECAR.read_text(encoding="ascii").strip() if SIDECAR.is_file() else ""
    if sidecar != reference.sha256_bytes(report_payload) + "  report.json":
        _fail("sidecar_digest_mismatch", errors)


def check_readme(errors: List[str]) -> None:
    try:
        rows = reference.readme_pin_rows()
    except (OSError, ValueError, UnicodeError) as error:
        _fail("readme_digest_table_invalid:" + str(error), errors)
        return
    expected: Dict[str, str] = {}
    for path in sorted(reference.SOURCE_PINS):
        expected["source:" + path] = reference.SOURCE_PINS[path]
    for path in sorted(reference.BOUNDARY_PINS):
        expected[path] = reference.BOUNDARY_PINS[path]
    text = README.read_text(encoding="utf-8")
    tokens = ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
              "Sinusoidal SMS TSM", "GPL-2.0", "excluded", "no local run",
              "no substitution", "synthetic", "blocked", "16 kHz",
              reference.TASK_ID, reference.BASE_COMMIT)
    for token in tokens:
        if token not in text:
            _fail("readme_token_missing:" + token, errors)
    actual = dict(rows)
    if len(rows) != len(actual):
        _fail("readme_duplicate_rows", errors)
    if set(actual) != set(expected):
        _fail("readme_table_key_mismatch", errors)
    for key, digest in actual.items():
        if key in expected and digest != expected[key]:
            _fail("readme_digest_stale:" + key, errors)


def check_files(errors: List[str]) -> None:
    expected = {
        "README.md", "SOURCES.sha256", "SOURCES.sha256.license",
        "contract.json", "contract.json.license", "reference.py", "report.json",
        "report.json.license", "report.json.sha256", "report.json.sha256.license",
        "run.py", "test_reference.py", "verify.py",
    }
    actual = {path.name for path in HERE.iterdir() if path.is_file()}
    if actual != expected:
        _fail("unexpected_files:" + str(sorted(actual ^ expected)), errors)
    for path in HERE.rglob("*"):
        relative = path.relative_to(HERE).as_posix()
        if path.is_dir() and path.name == "__pycache__":
            _fail("pycache_present:" + relative, errors)
        if path.is_file() and path.name.endswith((".pyc", ".pyo")):
            _fail("compiled_python_present:" + relative, errors)
    for path in HERE.iterdir():
        if path.is_file():
            text = path.read_bytes()
            if b"\r\n" in text:
                _fail("crlf_line_ending:" + path.name, errors)
            for number, line in enumerate(text.splitlines(), 1):
                if line.rstrip() != line:
                    _fail("trailing_whitespace:" + path.name + ":" + str(number),
                          errors)
    for path in HERE.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        head = "\n".join(text.splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            _fail("python_spdx_missing:" + path.name, errors)
        if "\t" in text:
            _fail("tab_character:" + path.name, errors)
    readme_text = README.read_text(encoding="utf-8")
    if f"<!-- {SPDX_COPYRIGHT} -->" not in readme_text \
            or f"<!-- {SPDX_LICENSE} -->" not in readme_text:
        _fail("markdown_spdx_missing:README.md", errors)
    for name in LICENSE_SIDECARS:
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            _fail("sidecar_spdx_missing:" + name, errors)
    reuse_text = REUSE_CONFIG.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse_text or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse_text:
        _fail("reuse_config_no_longer_covers_docs", errors)


def check_scope(errors: List[str]) -> int:
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        _fail("scope_base_unavailable", errors)
        return 1
    try:
        changed = reference.scope_changed_paths(SDK_ROOT, base)
    except ValueError as error:
        _fail("scope_diff_failed:" + str(error), errors)
        return 1
    print("scope base " + base)
    violations = reference.scope_violations(changed)
    if violations:
        for path in violations:
            _fail("base_out_of_scope_change:" + path, errors)
        return 1
    print("scope changed paths " + str(len(changed)) +
          (" (none)" if not changed else ": " + ", ".join(changed)))
    return 0


def check_diff_check(errors: List[str]) -> None:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"],
                            capture_output=True, text=True, check=False)
    if result.returncode != 0 or result.stdout.strip() or result.stderr.strip():
        _fail("git_diff_check_failed:" + (result.stdout + result.stderr).strip(),
              errors)


def check_repeatability(errors: List[str]) -> int:
    first = reference.report_bytes()
    for _ in range(2):
        if reference.report_bytes() != first:
            _fail("nondeterministic_report_build", errors)
            return 1
    report = reference.strict_loads(first.decode("utf-8"))
    if report.get("repeatability", {}).get("fresh_builds") != 3:
        _fail("repeatability_metadata_mismatch", errors)
        return 1
    return 3


def main() -> int:
    errors: List[str] = []
    data = check_json(errors)
    report = data.get("report", {})
    contract = data.get("contract", {})
    check_boundary(report, contract, errors)
    check_pins(errors)
    check_canonical(errors)
    check_readme(errors)
    check_files(errors)
    base_checked = check_scope(errors)
    check_diff_check(errors)
    repeats = check_repeatability(errors)
    total = 1 + 1 + len(reference.SOURCE_PINS) + len(reference.BOUNDARY_PINS) \
        + 1 + 1 + base_checked + 1 + repeats + 1
    if errors:
        for error in errors:
            print("FAIL " + error, file=sys.stderr)
        print(f"verify: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print(f"verify: PASS ({total} checks; DEFER/incomplete/not_qualified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
