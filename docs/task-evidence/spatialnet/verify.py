# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for SpatialNet task-local evidence package."""

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


def _fail(msg: str, errors: List[str]) -> None:
    errors.append(msg)


def _eq(errors: List[str], msg: str, left: Any, right: Any) -> None:
    if left != right:
        _fail(msg, errors)


def check_json(errors: List[str]) -> Dict[str, Any]:
    report = contract = None
    for path in (REPORT, CONTRACT):
        try:
            value = reference.strict_loads(path.read_text(encoding="utf-8"))
        except Exception as error:
            _fail("invalid_json:" + path.name + ":" + str(error), errors)
            continue
        if path == REPORT:
            report = value
        else:
            contract = value
    if not isinstance(report, dict) or not isinstance(contract, dict):
        return {}
    _eq(errors, "report_schema", report.get("schema_id"), reference.SCHEMA_REPORT)
    _eq(errors, "contract_schema", contract.get("schema_id"), reference.SCHEMA_CONTRACT)
    for key in ("task_id", "title", "component_id", "repository", "base_commit", "branch", "profile", "decision", "defer_before", "evidence_status", "qualification_status", "status", "format", "boundary", "scope", "gates", "exact_blockers", "negative_claims", "board_link", "source_reported"):
        _eq(errors, "contract_report_differ:" + key, contract.get(key), report.get(key))
    return {"report": report, "contract": contract}


def check_boundary(report: Dict[str, Any], errors: List[str]) -> None:
    boundary = report.get("boundary", {})
    if not isinstance(boundary, dict):
        _fail("boundary_not_object", errors)
        return
    for k, v in boundary.items():
        if k == "format":
            continue
        if k == "descriptor_settings":
            if v != {}:
                _fail("descriptor_settings_not_empty", errors)
            continue
        if v is not False:
            _fail("boundary_flag_not_false:" + k, errors)
    _eq(errors, "format", report.get("format"), {"sample_rate_hz": reference.SAMPLE_RATE_HZ, "channels": reference.CHANNELS, "sample_format": reference.SAMPLE_FORMAT, "frame_samples": reference.FRAME_SAMPLES})
    scope = report.get("scope", {})
    if not isinstance(scope, dict):
        _fail("scope_not_object", errors)
        return
    for k in ("synthetic_only", "task_local_only"):
        if scope.get(k) is not True:
            _fail("scope_true_missing:" + k, errors)
    for k, v in scope.items():
        if k not in ("synthetic_only", "task_local_only") and v is not False:
            _fail("scope_flag_not_false:" + k, errors)
    if report.get("decision") != "DEFER":
        _fail("decision_not_defer", errors)
    if report.get("evidence_status") != "incomplete":
        _fail("evidence_not_incomplete", errors)
    if report.get("qualification_status") != "not_qualified":
        _fail("qualification_not_not_qualified", errors)
    for gate in report.get("gates", []):
        if not isinstance(gate, dict) or gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            _fail("gate_not_blocked:" + str(gate), errors)
    if [g.get("id") for g in report.get("gates", [])] != ["RG-0" + str(i) for i in range(1, 9)]:
        _fail("gate_ids", errors)
    if len(report.get("exact_blockers", [])) != 4:
        _fail("blocker_count", errors)
    if report.get("adverse", {}).get("all_rejected") is not True:
        _fail("adverse_not_all_rejected", errors)
    classes = report.get("evidence_classes", {})
    for k in ("real_local_model_output", "real_audio", "real_multichannel_corpus", "listening", "device_timing", "benchmark", "release_claim"):
        if classes.get(k) is not False:
            _fail("evidence_class_claimed:" + k, errors)
    if report.get("source_reported", {}).get("qualifies") is not False:
        _fail("source_reported_qualifies", errors)
    if report.get("synthetic_control", {}).get("qualifies") is not False:
        _fail("synthetic_control_qualifies", errors)
    if report.get("no_missing_result_qualifies_candidate") is not True:
        _fail("no_missing_result_qualifies_candidate", errors)


def check_pins(errors: List[str]) -> None:
    for path, digest in reference.SOURCE_PINS.items():
        target = reference.SOURCE_ROOT / path
        if not target.is_file() or reference.sha256_file(target) != digest:
            _fail("source_pin_stale:" + path, errors)
    for path, digest in reference.BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file() or reference.sha256_file(target) != digest:
            _fail("boundary_pin_stale:" + path, errors)
    try:
        rows = reference.parse_pin_lines(SOURCES.read_text(encoding="utf-8"))
    except Exception as error:
        _fail("invalid_sources:" + str(error), errors)
        return
    report_payload = reference.report_bytes()
    sidecar_payload = reference.sidecar_bytes(report_payload)
    sources_payload = reference.sources_bytes(report_payload, sidecar_payload)
    expected = {k: d for d, k in reference.parse_pin_lines(sources_payload.decode("utf-8"))}
    actual = {k: d for d, k in rows}
    if len(rows) != len(actual):
        _fail("duplicate_sources_rows", errors)
    if set(actual) != set(expected):
        _fail("sources_key_set_mismatch", errors)
    for k, d in actual.items():
        target = reference.qualify_pin_path(k)
        if target.is_file() and reference.sha256_file(target) != d:
            _fail("local_pin_stale:" + k, errors)
    if set(expected) != set(reference.allowed_pin_keys()):
        _fail("unexpected_pin_keys", errors)


def check_canonical(errors: List[str]) -> None:
    report_payload = reference.report_bytes()
    sidecar_payload = reference.sidecar_bytes(report_payload)
    sources_payload = reference.sources_bytes(report_payload, sidecar_payload)
    report = reference.strict_loads(report_payload.decode("utf-8"))
    contract_payload = reference.contract_bytes(report_payload, sidecar_payload, sources_payload, report)
    for path, payload in ((REPORT, report_payload), (SIDECAR, sidecar_payload), (SOURCES, sources_payload), (CONTRACT, contract_payload)):
        if not path.is_file() or path.read_bytes() != payload:
            _fail("noncanonical_artifact:" + path.name, errors)
    sidecar = SIDECAR.read_text(encoding="ascii").strip() if SIDECAR.is_file() else ""
    if sidecar != reference.sha256_bytes(report_payload) + "  report.json":
        _fail("sidecar_digest_mismatch", errors)


def check_readme(errors: List[str]) -> None:
    try:
        rows = reference.readme_pin_rows()
    except Exception as error:
        _fail("readme_table_invalid:" + str(error), errors)
        return
    expected: Dict[str, str] = {}
    for path in sorted(reference.SOURCE_PINS):
        expected["source:" + path] = reference.SOURCE_PINS[path]
    for path in sorted(reference.BOUNDARY_PINS):
        expected[path] = reference.BOUNDARY_PINS[path]
    actual = dict(rows)
    if len(rows) != len(actual):
        _fail("readme_duplicate_rows", errors)
    if set(actual) != set(expected):
        _fail("readme_table_key_mismatch", errors)
    for k, d in actual.items():
        if k in expected and d != expected[k]:
            _fail("readme_digest_stale:" + k, errors)
    text = README.read_text(encoding="utf-8")
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08", "SpatialNet", "synthetic", "blocked", reference.TASK_ID, reference.BASE_COMMIT):
        if token not in text:
            _fail("readme_token_missing:" + token, errors)


def check_files(errors: List[str]) -> None:
    expected = {"README.md", "SOURCES.sha256", "SOURCES.sha256.license", "contract.json", "contract.json.license", "reference.py", "report.json", "report.json.license", "report.json.sha256", "report.json.sha256.license", "run.py", "test_reference.py", "verify.py"}
    actual = {p.name for p in HERE.iterdir() if p.is_file()}
    if actual != expected:
        _fail("unexpected_files:" + str(sorted(actual ^ expected)), errors)
    for p in HERE.rglob("*"):
        rel = p.relative_to(HERE).as_posix()
        if p.is_dir() and p.name == "__pycache__":
            _fail("pycache_present:" + rel, errors)
        if p.is_file() and p.name.endswith((".pyc", ".pyo")):
            _fail("compiled_python:" + rel, errors)
    for p in HERE.glob("*.py"):
        text = p.read_text(encoding="utf-8")
        head = "\n".join(text.splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            _fail("python_spdx_missing:" + p.name, errors)
        if "\t" in text:
            _fail("tab_character:" + p.name, errors)
    readme_text = README.read_text(encoding="utf-8")
    if f"<!-- {SPDX_COPYRIGHT} -->" not in readme_text or f"<!-- {SPDX_LICENSE} -->" not in readme_text:
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
    except Exception as error:
        _fail("scope_diff_failed:" + str(error), errors)
        return 1
    print("scope base " + base)
    violations = reference.scope_violations(changed)
    if violations:
        for p in violations:
            _fail("base_out_of_scope_change:" + p, errors)
        return 1
    print("scope changed paths " + str(len(changed)) + (" (none)" if not changed else ": " + ", ".join(changed)))
    return 0


def check_diff_check(errors: List[str]) -> None:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"], capture_output=True, text=True, check=False)
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
    check_boundary(report, errors)
    check_pins(errors)
    check_canonical(errors)
    check_readme(errors)
    check_files(errors)
    base_checked = check_scope(errors)
    check_diff_check(errors)
    repeats = check_repeatability(errors)
    total = 1 + 1 + len(reference.SOURCE_PINS) + len(reference.BOUNDARY_PINS) + 1 + base_checked + 1 + repeats + 1
    if errors:
        for e in errors:
            print("FAIL " + e, file=sys.stderr)
        print(f"verify: {len(errors)} failure(s)", file=sys.stderr)
        return 1
    print(f"verify: PASS ({total} checks; DEFER/incomplete/not_qualified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
