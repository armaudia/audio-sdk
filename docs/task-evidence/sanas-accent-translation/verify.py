# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the Sanas Accent Translation evidence package.

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


def check_contract(contract: dict[str, Any], report: dict[str, Any],
                   errors: list[str]) -> None:
    check(contract.get("schema_id") == reference.CONTRACT_SCHEMA,
          "contract_schema", errors)
    check(contract.get("task") == reference.TASK, "contract_task", errors)
    check(contract.get("component") == reference.COMPONENT,
          "contract_component", errors)
    check(contract.get("base_commit") == reference.BASE_COMMIT,
          "contract_base", errors)
    check(contract.get("branch") == reference.BRANCH, "contract_branch", errors)
    check(contract.get("decision") == "DEFER", "contract_decision", errors)
    check(contract.get("status") == "proposal_only_incomplete",
          "contract_status", errors)
    check(contract.get("evidence_status") == "incomplete",
          "contract_evidence_status", errors)
    check(contract.get("qualification") == reference.qualification(),
          "contract_qualification", errors)
    boundary = contract.get("boundary", {})
    check(boundary == report.get("boundary"), "boundary_mismatch", errors)
    affirmative = ("task_local_write_only", "installed_v0_unchanged")
    for key in (
        "task_local_write_only", "installed_v0_unchanged",
        "public_api_abi_changed", "provider_registered",
        "descriptor_or_registry_changed", "enabled_by_default",
        "automatic_discovery_or_fallback", "shared_cmake_changed",
        "ci_changed", "board_or_handoff_changed", "vendor_terms_reviewed",
        "vendor_source_weights_or_runtime_present", "real_corpus_audio_present",
        "listening_or_device_timing_performed",
        "download_or_in_process_file_access", "benchmark_claim", "release_claim",
    ):
        check(boundary.get(key) is (key in affirmative),
              "boundary_value:" + key, errors)
    check(boundary.get("write_prefix") == reference.TASK_PREFIX,
          "boundary_write_prefix", errors)
    check(boundary.get("installed_v0_format") == {
        "sample_rate_hz": 16000, "channels": 1, "sample_format": "float32",
        "frame_samples": 160,
    }, "boundary_v0_format", errors)
    check(len(contract.get("release_gates", [])) == 8, "gate_count", errors)
    check([g.get("id") for g in contract.get("release_gates", [])]
          == ["RG-0" + str(n) for n in range(1, 9)], "gate_ids", errors)
    check(all(g.get("status") == "blocked" and g.get("qualifies") is False
              for g in contract.get("release_gates", [])),
          "gate_not_blocked", errors)
    check(len(contract.get("exact_blockers", [])) == 6, "blocker_count", errors)
    check(all(b.get("status") == "open"
              for b in contract.get("exact_blockers", [])),
          "blocker_not_open", errors)
    check(all(a.get("present") is False and a.get("verified") is False
              for a in contract.get("required_artifacts", [])),
          "artifact_present", errors)
    manifest = contract.get("tool_manifest_reference", {})
    check(manifest.get("status") == "absent" and manifest.get("caller_supplied") is False
          and manifest.get("accepted_manifest_present") is False,
          "manifest_reference_not_absent", errors)
    check(tuple(manifest.get("required_fields", []))
          == reference.TOOL_MANIFEST_REQUIRED_FIELDS,
          "manifest_required_fields", errors)
    assets = contract.get("external_assets", {})
    check(assets.get("status") == "absent" and assets.get("declared_count") == 0
          and assets.get("assets") == [] and assets.get("caller_supplied_exact_bytes") is False,
          "external_assets_not_absent", errors)
    check(contract.get("profile_source_check", {}).get("phrases_all_present") is True,
          "profile_phrases", errors)
    check(contract.get("evidence_entry", {}).get("text") == reference.EVIDENCE_TEXT,
          "evidence_text", errors)


def check_report(report: dict[str, Any], errors: list[str]) -> None:
    check(report.get("schema_id") == reference.REPORT_SCHEMA,
          "report_schema", errors)
    check(report.get("decision") == "DEFER", "report_decision", errors)
    check(report.get("status") == "proposal_only_incomplete",
          "report_status", errors)
    check(report.get("evidence_status") == "incomplete",
          "report_evidence_status", errors)
    check(report.get("qualification_status") == "not_qualified",
          "report_qualification", errors)
    check(report.get("no_missing_result_qualifies_candidate") is True,
          "missing_result_qualifies", errors)
    check(report.get("source_reported_scores_labeled_separately") is True,
          "source_scores_not_labeled", errors)
    check(all(row.get("status") == "blocked"
              for row in report.get("voice_requirements", [])),
          "voice_requirement_not_blocked", errors)
    check(report.get("absence_evidence", {}).get("summary", {}).get("all_absent") is True,
          "absence_summary", errors)
    check(report.get("absence_evidence", {}).get("summary", {}).get("probe_count")
          == 14, "absence_probe_count", errors)
    probes = [row for group in ("workspace", "worktree", "home")
              for row in report.get("absence_evidence", {}).get(group, [])]
    check(all(row.get("present") is False for row in probes),
          "absence_probe_present", errors)
    links, link_digest = reference.board_link_projection()
    check(report.get("linked_rows") == links, "linked_rows", errors)
    check(report.get("linked_row_projection_sha256") == link_digest,
          "linked_row_digest", errors)
    entry = report.get("evidence_entry", {})
    check(entry.get("path") == reference.EVIDENCE_PATH
          and entry.get("line") == reference.EVIDENCE_LINE
          and entry.get("text") == reference.EVIDENCE_TEXT
          and entry.get("sha256") == reference.SOURCE_PINS[reference.EVIDENCE_PATH],
          "evidence_entry", errors)
    check(report.get("inventory_link") == reference.INVENTORY_LINK,
          "inventory_link", errors)


def check_inventory(errors: list[str]) -> None:
    path = reference.WORKSPACE / "audio-benchmark-platform/plan/INVENTORY.json"
    try:
        data = reference.strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("inventory_unreadable:" + str(error))
        return
    components = data.get("components", []) if isinstance(data, dict) else []
    rows = [row for row in components
            if isinstance(row, dict) and row.get("id") == reference.COMPONENT]
    check(len(rows) == 1, "inventory_row_count", errors)
    if len(rows) != 1:
        return
    row = rows[0]
    for key in ("name", "area", "evidence_status", "disposition", "task"):
        check(row.get(key) == reference.INVENTORY_LINK[key],
              "inventory_field:" + key, errors)
    evidence = row.get("evidence", [])
    check(len(evidence) == 1, "inventory_evidence_count", errors)
    if evidence:
        item = evidence[0]
        check(item.get("path") == reference.EVIDENCE_PATH
              and item.get("line") == reference.EVIDENCE_LINE
              and item.get("record_name") == reference.INVENTORY_LINK["record_name"]
              and item.get("finding") == reference.INVENTORY_LINK["finding"],
              "inventory_evidence", errors)


def check_pins(contract: dict[str, Any], report: dict[str, Any],
               errors: list[str]) -> int:
    count = 0
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        target = reference.WORKSPACE / path
        check(target.is_file() and reference.sha256_file(target) == digest,
              "source_pin:" + path, errors)
        count += 1
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        target = reference.SDK_ROOT / path
        check(target.is_file() and reference.sha256_file(target) == digest,
              "boundary_pin:" + path, errors)
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
            *[(reference.TASK_PREFIX + name, reference.sha256_file(HERE / name))
              for name in reference._local_manifest_paths()],
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
        check(target.is_file() and reference.sha256_file(target) == digest,
              "live_pin:" + path, errors)
        count += 1
    report_source_pins = report.get("source_pins")
    if isinstance(report_source_pins, dict):
        for key, digest in report_source_pins.items():
            check(digest == reference.SOURCE_PINS[key[len("source:"):]],
                  "report_source_pin:" + key, errors)
    sidecar = SIDECAR_PATH.read_text(encoding="utf-8") if SIDECAR_PATH.is_file() else ""
    check(sidecar == reference.sha256_bytes(REPORT_PATH.read_bytes()) + "  report.json\n",
          "sidecar", errors)
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
        check(counts.get(section) == len(expected[section]),
              "readme_row_count:" + section, errors)
    check(text == reference.update_readme_tables(text), "readme_tables_stale", errors)
    return sum(counts.values())


def check_licensing(errors: list[str]) -> None:
    for name in (*reference.LOCAL_FILES, "SOURCES.sha256"):
        path = HERE / name
        check(path.is_file(), "missing_file:" + name, errors)
        if not path.is_file():
            continue
        if name.endswith(".license"):
            text = path.read_text(encoding="utf-8", errors="replace")
            check(SPDX_LICENSE in text and SPDX_COPYRIGHT in text,
                  "license_sidecar:" + name, errors)
        elif name.endswith(".json") or name.endswith(".sha256"):
            sidecar = HERE / (name + ".license")
            check(sidecar.is_file(), "missing_sidecar:" + name, errors)
        else:
            head = path.read_text(encoding="utf-8", errors="replace")[:400]
            check(SPDX_LICENSE in head and SPDX_COPYRIGHT in head,
                  "spdx_header:" + name, errors)
    reuse = (reference.SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    check('"docs/**"' in reuse and 'SPDX-License-Identifier = "Apache-2.0"' in reuse,
          "reuse_docs_coverage", errors)


def check_absent(errors: list[str]) -> None:
    actual = {path.name for path in HERE.iterdir()}
    check(actual == reference.EXPECTED_DIR_FILES,
          "unexpected_dir_files:" + str(sorted(actual ^ reference.EXPECTED_DIR_FILES)),
          errors)
    for path in HERE.rglob("*"):
        if path.is_file():
            check(path.suffix.lower() not in reference.PROHIBITED_SUFFIXES,
                  "prohibited_artifact:" + str(path.relative_to(HERE)), errors)
    probes = reference.probe_rows()
    for group, rows in probes.items():
        for row in rows:
            check(row["present"] is False, "live_probe_present:" + group + ":" + row["path"], errors)


def _environment() -> dict[str, str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return environment


def check_reproduction(report_bytes: bytes, errors: list[str]) -> tuple[bool, int]:
    process = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--stdout-report"], cwd=str(HERE),
        capture_output=True, env=_environment(), timeout=120)
    ok = process.returncode == 0 and process.stdout == report_bytes
    check(ok, "stdout_report_mismatch", errors)
    outputs: list[bytes] = []
    for _ in range(3):
        result = subprocess.run(
            [sys.executable, str(HERE / "run.py"), "--verify-repro"], cwd=str(HERE),
            capture_output=True, env=_environment(), timeout=120)
        if result.returncode != 0:
            errors.append("cold_start_failed:"
                          + result.stdout.decode("utf-8", "replace")
                          + result.stderr.decode("utf-8", "replace"))
            continue
        outputs.append(result.stdout)
    check(len(outputs) == 3, "cold_start_count", errors)
    if outputs:
        check(all(item == outputs[0] for item in outputs),
              "cold_start_outputs_differ", errors)
        check(b"ok=1\n" in outputs[0], "cold_start_not_ok", errors)
    return ok, len(outputs)


def check_git_scope(errors: list[str]) -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=str(reference.SDK_ROOT), capture_output=True, text=True)
    if status.returncode != 0:
        errors.append("git_status_failed")
        return
    for line in status.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            check(path.startswith(reference.TASK_PREFIX),
                  "status_out_of_scope:" + path, errors)
    base = reference.scope_base(reference.SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
        return
    paths = reference.scope_changed_paths(reference.SDK_ROOT, base)
    for path in reference.scope_violations(paths):
        errors.append("base_out_of_scope_change:" + path)


def main() -> int:
    errors: list[str] = []
    pins = 0
    rows = 0
    reproduction = False
    cold_starts = 0
    if platform.python_version() != reference.REQUIRED_INTERPRETER:
        errors.append("interpreter_not_pinned:" + platform.python_version())
    try:
        contract = strict_load(CONTRACT_PATH, errors)
        report = strict_load(REPORT_PATH, errors)
        check_contract(contract, report, errors)
        pins = check_pins(contract, report, errors)
        check_report(report, errors)
        check_inventory(errors)
        rows = check_readme(errors)
        check_licensing(errors)
        check_absent(errors)
        reproduction, cold_starts = check_reproduction(
            REPORT_PATH.read_bytes(), errors)
        check_git_scope(errors)
        payload = REPORT_PATH.read_bytes()
        check(reference.canonical_bytes(report) + b"\n" == payload,
              "report_not_canonical", errors)
        check(payload.endswith(b"\n") and not payload.endswith(b"\n\n"),
              "report_trailing_newline", errors)
        check(reference.finite_json(report) and reference.finite_json(contract),
              "nonfinite_json", errors)
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append("verification_exception:" + str(error))
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print("verification_failed=" + str(len(errors)))
        return 1
    print("pins_ok=" + str(pins) + " readme_rows=" + str(rows)
          + " reproduction_ok=" + str(int(reproduction))
          + " cold_starts=" + str(cold_starts)
          + " scope_ok=1 licensing_ok=1 semantics_ok=1 boundary_ok=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
