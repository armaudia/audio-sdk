# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the WavLM conversion encoder evidence package.

Checks strict JSON, canonical bytes and SHA-256 sidecar, exact source/boundary
and artifact pins, README digest tables, blocker and Voice-profile semantics,
licensing, absent prohibited artifacts, newest-merge-base task-local git scope,
and three byte-identical cold-start regenerations. Package evidence is never
written by this script.
"""

from __future__ import annotations

import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"
README_PATH = HERE / "README.md"
SIDECAR_FILES = (
    "contract.json.license", "report.json.license",
    "report.json.sha256.license", "SOURCES.sha256.license",
)
SPDX_LICENSE = "SPDX-License-" + "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"


class VerificationError(AssertionError):
    pass


def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def strict_load(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = reference.strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + path.name + ":" + str(error))
        return {}
    if not isinstance(value, dict):
        errors.append("json_root_not_object:" + path.name)
        return {}
    return value


def check_contract(contract: dict[str, Any], report: dict[str, Any], errors: list[str]) -> None:
    check(contract.get("schema_id") == reference.CONTRACT_SCHEMA, "contract_schema", errors)
    check(contract.get("task") == reference.TASK, "contract_task", errors)
    check(contract.get("component") == reference.COMPONENT, "contract_component", errors)
    check(contract.get("base_commit") == reference.BASE_COMMIT, "contract_base", errors)
    check(contract.get("branch") == reference.BRANCH, "contract_branch", errors)
    check(contract.get("decision") == "DEFER", "contract_decision", errors)
    check(contract.get("status") == "proposal_only_incomplete", "contract_status", errors)
    check(contract.get("evidence_status") == "incomplete", "contract_evidence_status", errors)
    check(contract.get("qualification") == reference.qualification(), "contract_qualification", errors)
    boundary = contract.get("boundary", {})
    check(boundary == report.get("boundary"), "boundary_mismatch", errors)
    affirmative = ("task_local_write_only", "installed_v0_unchanged")
    for key in (
        "task_local_write_only", "installed_v0_unchanged", "public_api_abi_changed",
        "provider_registered", "descriptor_or_registry_changed", "enabled_by_default",
        "automatic_discovery_or_fallback", "shared_cmake_changed", "ci_changed",
        "board_or_handoff_changed", "vendor_terms_reviewed", "vendor_source_weights_or_runtime_present",
        "real_corpus_audio_present", "listening_or_device_timing_performed",
        "download_or_in_process_file_access", "benchmark_claim", "release_claim",
    ):
        check(boundary.get(key) is (key in affirmative), "boundary_value:" + key, errors)
    check(boundary.get("write_prefix") == reference.TASK_PREFIX, "boundary_write_prefix", errors)
    check(boundary.get("installed_v0_format") == {
        "sample_rate_hz": 16000, "channels": 1, "sample_format": "float32", "frame_samples": 160,
    }, "boundary_v0_format", errors)
    check(len(contract.get("release_gates", [])) == 8, "gate_count", errors)
    check([g.get("id") for g in contract.get("release_gates", [])] == ["RG-0" + str(n) for n in range(1, 9)], "gate_ids", errors)
    check(all(g.get("status") == "blocked" and g.get("qualifies") is False for g in contract.get("release_gates", [])), "gate_not_blocked", errors)
    check(len(contract.get("exact_blockers", [])) == 6, "blocker_count", errors)
    check(all(b.get("status") == "open" for b in contract.get("exact_blockers", [])), "blocker_not_open", errors)
    check(all(a.get("present") is False and a.get("verified") is False for a in contract.get("required_artifacts", [])), "artifact_present", errors)
    manifest = contract.get("tool_manifest_reference", {})
    check(manifest.get("status") == "absent" and manifest.get("caller_supplied") is False and manifest.get("accepted_manifest_present") is False, "manifest_reference_not_absent", errors)
    assets = contract.get("external_assets", {})
    check(assets.get("status") == "absent" and assets.get("declared_count") == 0 and assets.get("assets") == [] and assets.get("caller_supplied_exact_bytes") is False, "external_assets_not_absent", errors)
    check(contract.get("profile_source_check", {}).get("phrases_all_present") is True, "profile_phrases", errors)
    check(contract.get("evidence_entry", {}).get("text") == reference.EVIDENCE_TEXT, "evidence_text", errors)
    check(contract.get("matrix_entry", {}).get("text") == reference.MATRIX_TEXT, "matrix_text", errors)


def check_report(report: dict[str, Any], errors: list[str]) -> None:
    check(report.get("schema_id") == reference.REPORT_SCHEMA, "report_schema", errors)
    check(report.get("decision") == "DEFER", "report_decision", errors)
    check(report.get("status") == "proposal_only_incomplete", "report_status", errors)
    check(report.get("evidence_status") == "incomplete", "report_evidence_status", errors)
    check(report.get("qualification_status") == "not_qualified", "report_qualification", errors)
    check(report.get("no_missing_result_qualifies_candidate") is True, "missing_result_qualifies", errors)
    check(report.get("source_reported_scores_labeled_separately") is True, "source_scores_not_labeled", errors)
    check(all(row.get("status") == "blocked" for row in report.get("voice_requirements", [])), "voice_requirement_not_blocked", errors)
    summary = report.get("absence_evidence", {}).get("summary", {})
    check(summary.get("all_absent") is True, "absence_summary", errors)
    check(summary.get("probe_count") == 12, "absence_probe_count", errors)
    probes = [row for group in ("workspace", "worktree", "home") for row in report.get("absence_evidence", {}).get(group, [])]
    check(all(row.get("present") is False for row in probes), "absence_probe_present", errors)
    links, link_digest = reference.board_link_projection()
    check(report.get("linked_rows") == links, "linked_rows", errors)
    check(report.get("linked_row_projection_sha256") == link_digest, "linked_row_digest", errors)
    entry = report.get("evidence_entry", {})
    check(entry.get("path") == reference.EVIDENCE_PATH and entry.get("line") == reference.EVIDENCE_LINE and entry.get("text") == reference.EVIDENCE_TEXT and entry.get("sha256") == reference.SOURCE_PINS[reference.EVIDENCE_PATH], "evidence_entry", errors)
    matrix = report.get("matrix_entry", {})
    check(matrix.get("path") == reference.MATRIX_PATH and matrix.get("line") == reference.MATRIX_LINE and matrix.get("text") == reference.MATRIX_TEXT and matrix.get("sha256") == reference.SOURCE_PINS[reference.MATRIX_PATH], "matrix_entry", errors)
    check(report.get("inventory_link") == reference.INVENTORY_LINK, "inventory_link", errors)


def check_inventory(errors: list[str]) -> None:
    path = reference.WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"
    try:
        data = reference.strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("inventory_unreadable:" + str(error))
        return
    components = data.get("components", []) if isinstance(data, dict) else []
    rows = [row for row in components if isinstance(row, dict) and row.get("id") == reference.COMPONENT]
    check(len(rows) == 1, "inventory_row_count", errors)
    if len(rows) != 1:
        return
    row = rows[0]
    for key in ("name", "area", "evidence_status", "disposition", "task"):
        check(row.get(key) == reference.INVENTORY_LINK[key], "inventory_field:" + key, errors)
    evidence = row.get("evidence", [])
    check(isinstance(evidence, list) and len(evidence) >= 2, "inventory_evidence_count", errors)
    paths = {item.get("path") for item in evidence if isinstance(item, dict)}
    check(reference.EVIDENCE_PATH in paths and reference.MATRIX_PATH in paths, "inventory_evidence_paths", errors)


def check_pins(errors: list[str]) -> int:
    count = 0
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        target = reference.WORKSPACE / path
        check(target.is_file() and reference.sha256_file(target) == digest, "source_pin:" + path, errors)
        count += 1
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        target = reference.SDK_ROOT / path
        check(target.is_file() and reference.sha256_file(target) == digest, "boundary_pin:" + path, errors)
        count += 1
    pin_text = SOURCES_PATH.read_text(encoding="utf-8") if SOURCES_PATH.is_file() else ""
    try:
        rows = reference.parse_pin_lines(pin_text)
    except ValueError as error:
        errors.append("sources_invalid:" + str(error))
        rows = []
    expected_rows = [
        (digest, path) for path, digest in (
            *[("source:" + name, digest) for name, digest in reference.SOURCE_PINS.items()],
            *[("sdk:" + name, digest) for name, digest in reference.BOUNDARY_PINS.items()],
            *[(reference.TASK_PREFIX + name, reference.sha256_file(HERE / name)) for name in reference._local_manifest_paths()],
            (reference.TASK_PREFIX + "README.md", reference.sha256_file(HERE / "README.md")),
        )
    ]
    check(len(rows) == len(expected_rows), "sources_row_count", errors)
    if rows:
        check(sorted(rows) == sorted(expected_rows), "sources_rows", errors)
    for digest, path in rows:
        if path.startswith("source:"):
            target = reference.WORKSPACE / path[len("source:"):]
        elif path.startswith("sdk:"):
            target = reference.SDK_ROOT / path[len("sdk:"):]
        else:
            target = HERE / path[len(reference.TASK_PREFIX):]
        check(target.is_file() and reference.sha256_file(target) == digest, "live_pin:" + path, errors)
        count += 1
    sidecar = SIDECAR_PATH.read_text(encoding="utf-8") if SIDECAR_PATH.is_file() else ""
    check(sidecar == reference.sha256_bytes(REPORT_PATH.read_bytes()) + "  report.json\n", "sidecar", errors)
    return count


def check_readme(errors: list[str]) -> int:
    text = README_PATH.read_text(encoding="utf-8") if README_PATH.is_file() else ""
    try:
        counts = reference.verify_readme_digests(text)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_digest_table:" + str(error))
        return 0
    expected = reference.expected_readme_keys()
    for section in reference.README_SECTIONS:
        check(counts.get(section) == len(expected[section]), "readme_row_count:" + section, errors)
    check(text == reference.update_readme_tables(text), "readme_tables_stale", errors)
    return sum(counts.values())


def check_license(errors: list[str]) -> None:
    for path in HERE.glob("*.license"):
        text = path.read_text(encoding="utf-8")
        check(SPDX_LICENSE in text, "license_missing_spdx:" + path.name, errors)
        check(SPDX_COPYRIGHT in text, "license_missing_copyright:" + path.name, errors)
    for name in SIDECAR_FILES:
        check((HERE / name).is_file(), "missing_sidecar:" + name, errors)


def check_no_prohibited_artifacts(errors: list[str]) -> None:
    allowed = set(reference.EXPECTED_DIR_FILES)
    for path in sorted(HERE.rglob("*")):
        rel = path.relative_to(HERE).as_posix()
        if path.is_dir():
            continue
        if rel not in allowed:
            errors.append("unexpected_file:" + rel)
        if path.suffix.lower() in reference.PROHIBITED_SUFFIXES:
            errors.append("prohibited_suffix:" + rel)
        if path.name == "__pycache__" or "/__pycache__/" in ("/" + rel):
            errors.append("pycache:" + rel)


def check_scope(errors: list[str]) -> list[str]:
    base = reference.scope_base(reference.SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
        return []
    paths = reference.scope_changed_paths(reference.SDK_ROOT, base)
    violations = reference.scope_violations(paths)
    for path in violations:
        errors.append("base_out_of_scope_change:" + path)
    return paths


def check_regen(errors: list[str]) -> tuple[str, str]:
    report_payload = reference.report_bytes()
    observed: list[tuple[str, str]] = []
    for _ in range(3):
        r = reference.report_bytes()
        s = reference.sources_bytes()
        observed.append((reference.sha256_bytes(r), reference.sha256_bytes(s)))
        check(r == report_payload, "report_regen_mismatch", errors)
    check(len(set(observed)) == 1, "regen_not_stable", errors)
    return observed[0]


def main() -> int:
    errors: list[str] = []
    contract = strict_load(CONTRACT_PATH, errors)
    report = strict_load(REPORT_PATH, errors)
    if contract and report:
        check_contract(contract, report, errors)
        check_report(report, errors)
    check_inventory(errors)
    pin_count = check_pins(errors)
    readme_count = check_readme(errors)
    check_license(errors)
    check_no_prohibited_artifacts(errors)
    scoped = check_scope(errors)
    report_sha, sources_sha = check_regen(errors)
    check(platform.python_version() == reference.REQUIRED_INTERPRETER
          or os.environ.get("AUDIO_SDK_ALLOW_PYTHON_MISMATCH") == "1",
          "python_version:" + platform.python_version(), errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print("task=" + reference.TASK)
    print("decision=DEFER")
    print("evidence_status=incomplete")
    print("qualification_status=not_qualified")
    print("report_sha256=" + report_sha)
    print("sources_sha256=" + sources_sha)
    print("pinned_digests_verified=" + str(pin_count))
    print("readme_digest_rows_verified=" + str(readme_count))
    print("scope_files=" + str(len(scoped)))
    print("ok=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
