#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local evidence package."""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import reference

HERE = Path(__file__).resolve().parent
SDK = reference.SDK_ROOT
AUDIO = reference.AUDIO_ROOT
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"
TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
SPDX_LICENSE = "SPDX-License-" "Identifier: Apache-2.0"


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append("interpreter_mismatch:" + observed)


def check_profile_source(errors: list[str]) -> None:
    text = (AUDIO / reference.PROFILE_SOURCE_REL).read_text(encoding="utf-8")
    lines = [line for line in text.splitlines()
             if line.startswith("| Enhancement ")]
    if len(lines) != 1:
        errors.append("enhancement_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in lines[0]:
            errors.append("enhancement_phrase_missing:" + phrase)


def check_pins(errors: list[str]) -> tuple[int, dict[str, str]]:
    if not PINS.is_file():
        errors.append("SOURCES.sha256_missing")
        return 0, {}
    text = PINS.read_text(encoding="utf-8")
    if not text.startswith("# SHA-256 pins for " + reference.TASK):
        errors.append("pins_header_mismatch")
    if any("plan/swarm/TASKS.json" in line
           for line in text.splitlines() if not line.startswith("#")):
        errors.append("mutable_task_board_pinned")
    try:
        rows = reference.parse_pin_lines(text)
    except ValueError as error:
        errors.append("pin_parse_failed:" + str(error))
        return 0, {}
    pins: dict[str, str] = {}
    for digest, label in rows:
        if label in pins:
            errors.append("duplicate_pin:" + label)
            continue
        pins[label] = digest
    expected_labels = (
        {"source:" + name for name in reference.SOURCE_PINS}
        | {"sdk:" + name for name in reference.BOUNDARY_PINS}
        | {reference.TASK_PREFIX + name for name in reference.LOCAL_FILES}
    )
    if set(pins) != expected_labels:
        errors.append("pin_label_set_mismatch")
    return len(pins), pins


def _pin_path(label: str) -> Path:
    if label.startswith("source:"):
        return AUDIO / label[len("source:"):]
    if label.startswith("sdk:"):
        return SDK / label[len("sdk:"):]
    return HERE / label[len(reference.TASK_PREFIX):]


def check_pin_targets(pins: dict[str, str], errors: list[str]) -> int:
    checked = 0
    for label, digest in sorted(pins.items()):
        path = _pin_path(label)
        if not path.is_file():
            errors.append("pin_target_missing:" + label)
            continue
        actual = reference.sha256_file(path)
        if actual != digest:
            errors.append("pin_digest_mismatch:" + label)
        else:
            checked += 1
    return checked


def strict_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        return reference.read_strict_json(path)
    except Exception as error:  # noqa: BLE001
        errors.append("strict_json_failed:" + path.name + ":" + str(error))
        return None


def _expect(flag: bool, message: str, errors: list[str]) -> None:
    if not flag:
        errors.append(message)


def check_report(report: dict[str, Any] | None,
                 errors: list[str]) -> dict[str, Any] | None:
    if report is None:
        return None

    def expect(flag: bool, message: str) -> None:
        _expect(flag, message, errors)

    expect(report.get("task_id") == reference.TASK, "task_id_mismatch")
    expect(report.get("component") == reference.COMPONENT_ID,
           "component_mismatch")
    expect(report.get("mode") == reference.MODE, "mode_mismatch")
    expect(report.get("profile") == reference.PROFILE, "profile_mismatch")
    expect(report.get("status") == reference.STATUS, "status_mismatch")
    expect(report.get("evidence_status") == reference.EVIDENCE_STATUS,
           "evidence_status_mismatch")
    expect(report.get("decision") == reference.DECISION, "decision_mismatch")
    expect(report.get("qualification_status")
           == reference.QUALIFICATION_STATUS, "qualification_mismatch")
    expect(report.get("base_commit") == reference.BASE_COMMIT,
           "base_commit_mismatch")
    expect(report.get("branch") == reference.BRANCH, "branch_mismatch")
    expect(report.get("candidate_metrics") is None,
           "candidate_metrics_not_null")

    qualification = report.get("qualification", {})
    expect(qualification.get("candidate_qualified") is False,
           "candidate_qualified_not_false")
    expect(qualification.get("no_missing_result_qualifies_candidate") is True,
           "missing_result_guard_missing")
    expect(qualification.get("blocked_gate_count") == 8,
           "blocked_gate_count_not_eight")

    scope = report.get("scope", {})
    for key in ("model_runtime_invoked", "runtime_invoked", "model_executed",
                "weights_loaded", "weights_downloaded", "network_used",
                "real_audio", "real_corpus", "listening", "device_timing",
                "public_benchmark", "release_claim", "caller_asset_present",
                "terms_review_performed", "provider_registration",
                "descriptor_registry_change", "default_selected",
                "enabled_by_default", "installed_v0_behavior_change",
                "public_api_abi_change", "abi_change",
                "shared_build_or_ci_change", "asset_bundled",
                "adapter_runtime_bundled", "weights_vendored",
                "sdk_callback_invoked", "production_callback_registered",
                "processor_exposure"):
        expect(scope.get(key) is False, "scope_flag_not_false:" + key)
    expect(scope.get("task_local_only") is True, "task_local_only_not_true")

    geometry = report.get("public_v0_geometry", {})
    expect(geometry.get("sample_rate_hz") == reference.V0_SAMPLE_RATE_HZ,
           "v0_rate_mismatch")
    expect(geometry.get("channels") == reference.V0_CHANNELS,
           "v0_channels_mismatch")
    expect(geometry.get("sample_format") == reference.V0_SAMPLE_FORMAT,
           "v0_format_mismatch")
    expect(geometry.get("frame_samples") == reference.V0_FRAME_SAMPLES,
           "v0_frame_mismatch")
    expect(geometry.get("registered") is False, "v0_registered_not_false")

    family = report.get("family_record", {})
    expect(family.get("family_name") == reference.FAMILY_NAME,
           "family_name_mismatch")
    expect(family.get("model_card_source") == reference.MODEL_CARD_SOURCE,
           "model_card_mismatch")
    expect(family.get("paper_source") == reference.PAPER_SOURCE,
           "paper_mismatch")
    expect(family.get("locally_verified") is False,
           "family_locally_verified")
    expect(family.get("admitted_as_result") is False,
           "family_admitted_as_result")

    recorded = report.get("recorded_identity", {})
    expect(recorded.get("locally_verified") is False,
           "recorded_identity_locally_verified")
    expect(recorded.get("source_reported_scores") is None,
           "source_scores_present")
    expect(recorded.get("candidate_store", {}).get("sample_rate_hz_reported")
           is None, "sample_rate_invented")
    expect(recorded.get("candidate_matrix", {}).get("family_row_present")
           is False, "candidate_matrix_row_invented")

    gates = report.get("release_gates", [])
    expect([gate.get("id") for gate in gates]
           == [gate for gate, _ in reference.RELEASE_GATES],
           "gate_ids_or_order_mismatch")
    expect(all(gate.get("status") == "blocked" for gate in gates),
           "a_release_gate_is_not_blocked")

    blockers = report.get("exact_blockers", [])
    expect([item.get("id") for item in blockers]
           == [item["id"] for item in reference.exact_blockers()],
           "blocker_ids_or_order_mismatch")
    expect(len(blockers) == 8, "blocker_count_not_eight")

    artifacts = report.get("required_artifacts", [])
    expect(all(item.get("sha256") is None and item.get("bytes") is None
               and item.get("locally_verified") is False
               and item.get("qualifies") is False for item in artifacts),
           "artifact_identity_invented")

    absence = report.get("absence_evidence", {}).get("summary", {})
    expect(absence.get("all_probes_absent") is True,
           "absence_probes_not_all_absent")
    expect(absence.get("probe_count") == len(reference.all_probes()),
           "absence_probe_count_mismatch")

    profile = report.get("enhancement_profile", {})
    expect(profile.get("name") == reference.PROFILE,
           "enhancement_profile_name_mismatch")
    expect([row["id"] for row in profile.get("required_items", [])]
           == [item[0] for item in reference.ENHANCEMENT_REQUIREMENTS],
           "enhancement_requirement_ids_mismatch")
    expect(profile.get("satisfied_for_qualification") == [],
           "enhancement_profile_satisfied")

    control = report.get("caller_asset_contract", {}).get("control", {})
    expect(control.get("all_rejected_rejected") is True,
           "adverse_controls_not_all_rejected")
    expect(control.get("synthetic_control_accepted") is True,
           "synthetic_control_not_accepted")
    expect(control.get("runtime_executed") is False,
           "admission_runtime_executed")

    identity = report.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False,
           "task_board_whole_file_hashed")
    expect(identity.get("board_path") == reference.BOARD_TASK_ROW,
           "task_board_path_mismatch")
    expect(set(identity.get("excluded_mutable_fields", []))
           == {"status", "owner", "claim", "review", "handoff",
               "blocked_reason", "dispatch_priority"},
           "excluded_mutable_fields_mismatch")
    return report


def check_contract(contract: dict[str, Any] | None,
                   report: dict[str, Any] | None,
                   errors: list[str]) -> None:
    if contract is None or report is None:
        return
    expect = lambda flag, message: _expect(flag, message, errors)  # noqa: E731
    expect(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID,
           "contract_schema_mismatch")
    expect(contract.get("decision") == reference.DECISION,
           "contract_decision_mismatch")
    for field in ("qualification", "task_row_identity", "scope", "boundary",
                  "source_pins", "boundary_pins", "family_record",
                  "recorded_identity", "task_geometry", "public_v0_geometry",
                  "rights_gap", "required_artifacts", "exact_blockers",
                  "release_gates", "reopen_conditions",
                  "caller_asset_contract"):
        expect(contract.get(field) == report.get(field),
               "contract_field_mismatch:" + field)


def check_readme(errors: list[str]) -> int:
    if not README.is_file():
        errors.append("README_missing")
        return 0
    text = README.read_text(encoding="utf-8")
    try:
        counts = reference.verify_readme_digests(text)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return 0
    for section in reference.README_SECTIONS:
        expected = len(reference.expected_readme_keys()[section])
        if counts.get(section) != expected:
            errors.append("readme_section_count_mismatch:" + section)
    try:
        if text != reference.update_readme_tables(text):
            errors.append("readme_tables_stale")
    except (OSError, ValueError) as error:
        errors.append("readme_render_failed:" + str(error))
    return sum(counts.values())


def check_licensing(errors: list[str]) -> None:
    actual = {path.name for path in HERE.iterdir() if path.is_file()}
    if actual != reference.EXPECTED_DIR_FILES:
        errors.append("package_file_set_mismatch")
    for name in actual:
        if name in ("README.md", "LICENSES.md", "reference.py", "run.py",
                    "test_reference.py", "verify.py"):
            header = (HERE / name).read_text(encoding="utf-8")[:400]
            if SPDX_LICENSE not in header:
                errors.append("missing_spdx_header:" + name)
        if name.endswith((".json", ".sha256")):
            sidecar = HERE / (name + ".license")
            if not sidecar.is_file():
                errors.append("missing_license_sidecar:" + name)
            elif SPDX_LICENSE not in sidecar.read_text(encoding="utf-8"):
                errors.append("bad_license_sidecar:" + name)
    for name in actual:
        if Path(name).suffix.lower() in reference.FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + name)


def check_tests(errors: list[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = sum(1 for line in text.splitlines()
                if line.startswith("    def test_"))
    if count < 30:
        errors.append("fewer_than_30_tests:" + str(count))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    process = subprocess.run(
        [sys.executable, "-m", "unittest", "-q", "test_reference.py"],
        cwd=HERE, capture_output=True, text=True, env=env, timeout=300)
    if process.returncode != 0:
        errors.append("test_suite_failed:"
                      + (process.stderr.strip() or process.stdout.strip()))
    return count


def check_scope(errors: list[str]) -> list[str]:
    status = subprocess.run(
        ["git", "-C", str(SDK), "status", "--porcelain=v1",
         "--untracked-files=all"], capture_output=True, text=True)
    if status.returncode != 0:
        errors.append("git_status_failed:" + status.stderr.strip())
        return []
    changed: list[str] = []
    for line in status.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK), *arguments],
                              capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
    base = reference.scope_base(SDK)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            base_paths = reference.scope_changed_paths(SDK, base)
        except ValueError as error:
            errors.append(str(error))
        else:
            for path in reference.scope_violations(base_paths):
                errors.append("base_out_of_scope_change:" + path)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = (scratch / "audioml/worktrees/audio-sdk"
           / reference.TASK.split("-", 1)[1])
    target = sdk / reference.TASK_PREFIX
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for name in ("research", "audio-benchmark-platform"):
        link = scratch / "audioml" / name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(AUDIO / name)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(SDK / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    committed = tuple(
        ((HERE / name).read_bytes() if (HERE / name).is_file() else b"")
        for name in ("contract.json", "report.json", "report.json.sha256",
                     "SOURCES.sha256", "README.md"))
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    base = TEMP_ROOT if TEMP_ROOT.is_dir() else Path(tempfile.gettempdir())
    base.mkdir(parents=True, exist_ok=True)
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(
            prefix="se-nac-codec-latent-enhancement-family-cold-", dir=str(base)) as raw:
        root = Path(raw)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run(
                [sys.executable, "run.py", "all"], cwd=target,
                capture_output=True, text=True, env=env, timeout=300)
            if process.returncode != 0:
                errors.append(
                    f"cold_start_{index}_failed:"
                    + (process.stderr.strip() or process.stdout.strip()))
                continue
            generated = tuple(
                (target / name).read_bytes() for name in
                ("contract.json", "report.json", "report.json.sha256",
                 "SOURCES.sha256", "README.md"))
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[1]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_profile_source(errors)
    pin_count, pins = check_pins(errors)
    checked = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    check_report(report, errors)
    check_contract(contract, report, errors)

    report_bytes = REPORT.read_bytes() if REPORT.is_file() else b""
    digest = hashlib.sha256(report_bytes).hexdigest() if report_bytes else "unavailable"
    sidecar = SIDECAR.read_text(encoding="utf-8").strip() if SIDECAR.is_file() else None
    if sidecar != f"{digest}  report.json":
        errors.append("report_sidecar_mismatch")
    if report_bytes:
        expected = reference.canonical_report_bytes()
        if report_bytes != expected:
            errors.append("report_not_canonical")

    readme_rows = check_readme(errors)
    check_licensing(errors)
    tests = check_tests(errors)
    changed = check_scope(errors)
    cold = check_cold_start_regeneration(errors)

    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pin_count} pins_verified={checked} "
              f"json_ok={bool(report)} readme_rows={readme_rows} "
              f"tests={tests} cold_starts={len(cold)} "
              f"report_sha256={digest} changed_files={len(changed)} "
              f"failures={len(errors)}")
        return 1
    print(f"PASS pins={pin_count} pins_verified={checked} "
          f"gates={len(report['release_gates'])} "
          f"blockers={len(report['exact_blockers'])} "
          f"artifacts={len(report['required_artifacts'])} "
          f"enhancement_rows="
          f"{len(report['enhancement_profile']['required_items'])} "
          f"admission_cases="
          f"{len(report['caller_asset_contract']['control']['cases'])} "
          f"readme_rows={readme_rows} tests={tests} "
          f"absence_probes="
          f"{report['absence_evidence']['summary']['probe_count']} "
          f"cold_starts=3/3 byte_identical=true "
          f"profile={reference.PROFILE} status={reference.STATUS} "
          f"decision={reference.DECISION} report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
