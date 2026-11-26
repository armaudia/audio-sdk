# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the Source/VAD playback-conditioning package.

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
            value = reference.strict_loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError) as error:
            _fail("invalid_json:" + path.name + ":" + str(error), errors)
            continue
        if path == REPORT:
            report = value
        else:
            contract = value
    if not isinstance(report, dict) or not isinstance(contract, dict):
        return {}
    _eq(errors, "contract/report schema differ",
        contract.get("schema_id"), reference.SCHEMA_CONTRACT)
    _eq(errors, "report schema differs", report.get("schema_id"), reference.SCHEMA_REPORT)
    for key in ("task_id", "title", "component_id", "repository", "base_commit",
                "branch", "profile", "decision", "defer_before", "evidence_status",
                "qualification_status", "status", "format", "boundary", "scope",
                "gates", "exact_blockers", "negative_claims", "board_link",
                "caller_supplied_asset_contract", "source_reported"):
        _eq(errors, "contract/report differ:" + key, contract.get(key), report.get(key))
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
        if key == "descriptor_settings":
            if value != {}:
                _fail("descriptor_settings_not_empty", errors)
            continue
        if value is not False:
            _fail("boundary_flag_not_false:" + key, errors)
    _eq(errors, "boundary format mismatch",
        boundary.get("format"), report.get("format"))
    _eq(errors, "format geometry", report.get("format"), {
        "sample_rate_hz": reference.SAMPLE_RATE_HZ,
        "channels": reference.CHANNELS,
        "sample_format": reference.SAMPLE_FORMAT,
        "frame_samples": reference.FRAME_SAMPLES,
    })
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
    _eq(errors, "report scope mismatch", report.get("scope"), scope)
    if report.get("decision") != "DEFER":
        _fail("decision_must_be_defer", errors)
    if report.get("evidence_status") != "incomplete":
        _fail("evidence_status_must_be_incomplete", errors)
    if report.get("qualification_status") != "not_qualified":
        _fail("qualification_must_be_not_qualified", errors)
    classes = report.get("evidence_classes", {})
    for key in ("real_local_model_output", "real_audio", "listening",
                "device_timing", "benchmark", "release_claim"):
        if classes.get(key) is not False:
            _fail("evidence_class_claimed:" + key, errors)
    for gate in report.get("gates", []):
        if not isinstance(gate, dict) or gate.get("status") != "blocked" \
                or gate.get("qualifies") is not False:
            _fail("nonblocking_gate:" + str(gate), errors)
    if [gate.get("id") for gate in report.get("gates", [])] != ["RG-0" + str(n)
                                                               for n in range(1, 9)]:
        _fail("gate_ids_mismatch", errors)
    if len(report.get("exact_blockers", [])) != 4:
        _fail("blocker_count_mismatch", errors)
    if not report.get("adverse", {}).get("all_rejected"):
        _fail("adverse_cases_not_all_rejected", errors)
    if report.get("identity_control", {}).get(
            "alternating_integer_sequence_byte_identical") is not True:
        _fail("identity_control_failed", errors)
    if report.get("identity_control", {}).get("qualifies") is not False:
        _fail("identity_control_qualifies", errors)
    probe = report.get("unknown_span_probe", {})
    if probe.get("retained") is not True or probe.get("rate") != "1" \
            or probe.get("silence_decision_is_deletion") is not False \
            or probe.get("qualifies") is not False:
        _fail("unknown_span_control_invalid", errors)
    if report.get("source_reported", {}).get("qualifies") is not False:
        _fail("source_reported_qualifies", errors)
    if report.get("typed_envelope", {}).get("output_end") != reference.FIXTURE_SAMPLES:
        _fail("envelope_duration_not_closed", errors)


def check_pins(errors: List[str]) -> None:
    for path, digest in reference.SOURCE_PINS.items():
        target = reference.SOURCE_ROOT / path
        if not target.is_file() or reference.sha256_file(target) != digest:
            _fail("source_pin_stale:" + path, errors)
    for path, digest in reference.BOUNDARY_PINS.items():
        target = reference.SDK_ROOT / path
        if not target.is_file() or reference.sha256_file(target) != digest:
            _fail("boundary_pin_stale:" + path, errors)
    try:
        rows = reference.parse_pin_lines(SOURCES.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        _fail("invalid_sources_manifest:" + str(error), errors)
        return
    report_payload = reference.report_bytes()
    sidecar_payload = reference.sidecar_bytes(report_payload)
    expected = {key: digest for digest, key in reference.parse_pin_lines(
        reference.sources_bytes(report_payload, sidecar_payload).decode("utf-8"))}
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
    if not reference.asset_pins_absent():
        _fail("caller_asset_pins_present", errors)


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
    tokens = ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
              "Source/VAD", "caller-supplied", "synthetic", "blocked",
              "160", "16 kHz", "unknown", "not deletion",
              reference.TASK_ID, reference.BASE_COMMIT)
    text = README.read_text(encoding="utf-8")
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
        _fail("git_diff_check_failed:" + (result.stdout + result.stderr).strip(), errors)


def check_repeatability(errors: List[str]) -> int:
    first = reference.report_bytes()
    for _ in range(2):
        if reference.report_bytes() != first:
            _fail("nondeterministic_report_build", errors)
            return 1
    report = reference.strict_loads(first.decode("utf-8"))
    if report.get("repeatability", {}).get("fresh_builds") != 3:
        _fail("repeatability_metadata_mismatch", errors)
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
        + 1 + base_checked + 1 + repeats + 1
    if errors:
        for error in errors:
            print("FAIL " + error, file=sys.stderr)
        print(f"verify: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print(f"verify: PASS ({total} checks; DEFER/incomplete/not_qualified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
