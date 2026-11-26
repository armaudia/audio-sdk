# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-PYROOMACOUSTICS evidence package.

Checks Tool/Room/Spatial profile phrases, source and boundary pins, README
digest tables, canonical report bytes and sidecar, eight blocked artifacts,
six open blockers, eight blocked gates, fixed absence probes, fail-closed
caller-tool cases, licensing/REUSE boundaries, task-local git scope via the
newest merge-base, and three byte-identical cold-start regenerations. It writes
only to a temporary directory.
"""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = reference.WORKTREE
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
PROFILE_SOURCE = reference.AUDIO_ROOT / reference.PROFILE_SOURCE_REL

# REUSE-IgnoreStart
SPDX_LICENSE = "SPDX-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd

SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append("verifier_interpreter_mismatch:" + observed)


def check_profile_source(errors: list[str]) -> None:
    if not PROFILE_SOURCE.is_file():
        errors.append("profile_source_missing")
        return
    rows = [line for line in PROFILE_SOURCE.read_text(encoding="utf-8")
            .splitlines() if line.startswith("| " + reference.PROFILE_LABEL
                                             + " |")]
    if len(rows) != 1:
        errors.append("profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)
    check = reference.profile_row_check()
    if not check["phrases_all_present"]:
        errors.append("room_spatial_phrases_missing")
    if reference.PROFILE_LABEL != "Tool":
        errors.append("profile_label_mismatch")


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in (
            (reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"),
            (reference.BOUNDARY_PINS, reference.WORKTREE, "boundary")):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append(label + "_pin_missing:" + relative)
                continue
            if reference.sha256_file(path) != expected:
                errors.append(label + "_pin_mismatch:" + relative)
            checked += 1
    return checked


def check_sources_manifest(errors: list[str]) -> None:
    if not PINS.is_file():
        errors.append("sources_manifest_missing")
        return
    text = PINS.read_text(encoding="ascii")
    try:
        rows = reference.parse_pin_lines(text)
    except ValueError as error:
        errors.append("sources_manifest_strict:" + str(error))
        return
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("sources_manifest_drift")
    if PINS.read_bytes() != run.sources_bytes():
        errors.append("sources_manifest_run_drift")
    if any(path == reference.BOARD_TASK_ROW or
           path == "source:" + reference.BOARD_TASK_ROW
           for _, path in rows):
        errors.append("mutable_board_pinned")
    expected_paths = {
        "source:" + name for name in reference.SOURCE_PINS
    } | {
        "sdk:" + name for name in reference.BOUNDARY_PINS
    } | {
        reference.TASK_PREFIX + name
        for name in reference._local_manifest_paths()
    }
    if {path for _, path in rows} != expected_paths:
        errors.append("sources_manifest_path_set_mismatch")


def check_report(errors: list[str]) -> dict:
    if not CONTRACT.is_file() or not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}
    try:
        contract = reference.read_strict_json(CONTRACT)
        report = reference.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("strict_json_failure:" + str(error))
        return {}
    try:
        reference.validate_contract(contract)
    except ValueError as error:
        errors.append("contract_validation:" + str(error))

    expected_fields = {
        "schema_id": reference.REPORT_SCHEMA_ID,
        "task_id": reference.TASK,
        "task": reference.TASK,
        "component_id": reference.COMPONENT_ID,
        "title": reference.TASK_TITLE,
        "mode": reference.MODE,
        "branch": reference.BRANCH,
        "base_commit": reference.BASE_COMMIT,
        "contract_id": reference.CONTRACT_ID,
        "profile": reference.PROFILE,
        "status": reference.STATUS,
        "evidence_status": reference.EVIDENCE_STATUS,
        "decision": reference.DECISION,
        "qualification_status": reference.QUALIFICATION_STATUS,
    }
    for key, value in expected_fields.items():
        if report.get(key) != value:
            errors.append("report_field:" + key)
    for key in ("proposal_only", "incomplete"):
        if report.get(key) is not True:
            errors.append("report_flag:" + key)
    if report.get("contract_sha256") != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")

    copies = (
        ("disposition", "disposition"),
        ("boundary", "boundary"),
        ("scope", "scope"),
        ("exact_scope", "exact_scope"),
        ("public_v0_geometry", "public_v0_geometry"),
        ("task_geometry", "task_geometry"),
        ("upstream_record", "reported_source_leads"),
        ("matched_evidence_boundary", "matched_evidence_boundary"),
        ("required_artifacts", "required_artifacts"),
        ("exact_blockers", "exact_blockers"),
        ("gates", "release_gates"),
        ("rights_gap", "rights_gap"),
        ("qualification", "qualification"),
    )
    for report_key, contract_key in copies:
        if report.get(report_key) != contract.get(contract_key):
            errors.append("contract_copy_mismatch:" + report_key)

    qualification = report.get("qualification", {})
    for key in ("all_release_gates_blocked", "recorded_identity_only",
                "schema_control_only"):
        if qualification.get(key) is not True:
            errors.append("qualification_flag_missing:" + key)
    for key in (
            "real_result_present", "source_present", "exact_source_identity",
            "source_license_verified", "runtime_present", "runtime_pinned",
            "wheel_identity_verified", "room_geometry_verified",
            "rir_evidence_present", "matched_labels_present",
            "rights_cleared_inputs", "implementation_present",
            "reference_execution_result", "tool_profile_result",
            "room_spatial_result", "listening_result", "device_timing_result",
            "benchmark_result", "release_claim", "missing_result_promoted",
            "peer_result_inherited", "synthetic_control_promoted"):
        if qualification.get(key) is not False:
            errors.append("qualification_flag:" + key)

    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != "RG-%02d" % index:
            errors.append("gate_id:" + str(index))
        if gate.get("status") != "blocked":
            errors.append("gate_not_blocked:" + str(gate.get("id")))
        if gate.get("qualifies") is not False:
            errors.append("gate_qualifies:" + str(gate.get("id")))
        if gate.get("linked_row") != reference.TASK:
            errors.append("gate_linked_row:" + str(gate.get("id")))
        if not gate.get("reopen_condition"):
            errors.append("gate_reopen_missing:" + str(gate.get("id")))

    artifacts = report.get("required_artifacts", [])
    if len(artifacts) != 8:
        errors.append("artifact_count")
    for artifact in artifacts:
        if artifact.get("present") is not False \
                or artifact.get("verified") is not False \
                or artifact.get("blocked") is not True:
            errors.append("artifact_not_blocked:" + str(artifact.get("id")))
        if artifact.get("sha256") is not None \
                or artifact.get("revision") is not None \
                or artifact.get("bytes") is not None:
            errors.append("artifact_identity_invented:" +
                          str(artifact.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6:
        errors.append("blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    gate_ids = {row.get("id") for row in gates}
    for index, blocker in enumerate(blockers, start=1):
        if blocker.get("id") != "BLK-%02d" % index:
            errors.append("blocker_id:" + str(index))
        if blocker.get("status") != "open":
            errors.append("blocker_not_open:" + str(blocker.get("id")))
        if blocker.get("qualifies") is not False:
            errors.append("blocker_qualifies:" + str(blocker.get("id")))
        if blocker.get("artifact_id") not in artifact_ids:
            errors.append("blocker_artifact:" + str(blocker.get("id")))
        if not blocker.get("detail") or not blocker.get("linked_gates"):
            errors.append("blocker_detail_missing:" + str(blocker.get("id")))
        for gate in blocker.get("linked_gates", []):
            if gate not in gate_ids:
                errors.append("blocker_gate:" + str(blocker.get("id")))

    profile = report.get("tool_profile", {})
    rows = profile.get("requirement_rows", [])
    if len(rows) != len(reference.TOOL_REQUIREMENTS):
        errors.append("tool_row_count")
    for row in rows:
        if row.get("status") not in ("blocked", "documented"):
            errors.append("tool_row_status:" + str(row.get("id")))
        if row.get("qualifies") is not False:
            errors.append("tool_row_qualifies:" + str(row.get("id")))
    summary = profile.get("row_summary", {})
    if summary.get("requirement_count") != len(rows) \
            or summary.get("real_result_count") != 0 \
            or summary.get("profile_satisfied") is not False:
        errors.append("tool_summary_invalid")
    if profile.get("profile_source_check") != reference.profile_row_check():
        errors.append("tool_profile_source_mismatch")

    geometry = report.get("task_geometry", {})
    if geometry != reference.task_geometry():
        errors.append("task_geometry_mismatch")
    for key in ("room_dimensions_m", "microphone_positions_m",
                "source_positions_m", "timestamp_calibration", "rir_identity",
                "excitation", "delay_movement_noise_schedule",
                "held_out_labels", "frame_samples", "hop_samples"):
        if geometry.get(key) is not None:
            errors.append("task_geometry_invented:" + key)
    if geometry.get("exact_geometry_verified") is not False \
            or geometry.get("sdk_v0_adapter_mapping_present") is not False \
            or geometry.get("synthetic_control_is_real_rir_evidence") is not False:
        errors.append("task_geometry_claim")
    if geometry.get("synthetic_control_label") != "synthetic_geometry_control":
        errors.append("synthetic_label_missing")

    upstream = report.get("upstream_record", {})
    if upstream != reference.registry_leads():
        errors.append("upstream_record_mismatch")
    if upstream.get("lead_count") != 3 \
            or upstream.get("revision_or_license_present") is not False:
        errors.append("upstream_identity_invented")

    boundary = report.get("matched_evidence_boundary", {})
    if boundary.get("results_promoted") is not False \
            or boundary.get("synthetic_controls_not_real_rir_evidence") \
            is not True:
        errors.append("matched_boundary_promoted")

    evidence = report.get("absence_evidence", {})
    expected_absence = {
        "workspace_probes": reference.workspace_probes(),
        "worktree_probes": reference.worktree_probes(),
        "home_probes": reference.home_probes(),
    }
    for key, value in expected_absence.items():
        if evidence.get(key) != value:
            errors.append("absence_" + key + "_mismatch")
    absence = evidence.get("summary", {})
    if absence != reference.absence_summary():
        errors.append("absence_summary_mismatch")
    if absence.get("probe_count") != 17 \
            or absence.get("workspace_probe_count") != 9 \
            or absence.get("worktree_probe_count") != 5 \
            or absence.get("home_probe_count") != 3 \
            or absence.get("present_count") != 0 \
            or absence.get("all_probes_absent") is not True:
        errors.append("absence_summary_invalid")

    inputs = report.get("evidence_inputs", [])
    if inputs != reference.evidence_inputs():
        errors.append("evidence_inputs_mismatch")
    if len(inputs) != len(reference.EVIDENCE_INPUT_PATHS):
        errors.append("evidence_input_count_mismatch")
    for row in inputs:
        if row.get("sha256") != reference.SOURCE_PINS.get(row.get("path")):
            errors.append("evidence_input_pin_mismatch:" +
                          str(row.get("path")))
        if row.get("is_result") is not False:
            errors.append("evidence_input_promoted:" + str(row.get("path")))
    if not any(row.get("mentions_pyroomacoustics") for row in inputs):
        errors.append("no_evidence_input_mentions_pyroomacoustics")

    identity = report.get("linked_row_identity", {})
    if identity != reference.linked_identity_block():
        errors.append("linked_identity_mismatch")

    expected_source = reference.pin_rows(reference.SOURCE_PINS,
                                         reference.AUDIO_ROOT)
    expected_boundary = reference.pin_rows(reference.BOUNDARY_PINS,
                                           reference.WORKTREE)
    if report.get("source_pins") != expected_source:
        errors.append("report_source_pins_mismatch")
    if report.get("boundary_pins") != expected_boundary:
        errors.append("report_boundary_pins_mismatch")

    admission = report.get("admission", {})
    expected_admission = reference.admission_controls()
    if admission.get("controls") != expected_admission["controls"]:
        errors.append("admission_contract_mismatch")
    if admission.get("cases") != expected_admission["cases"]:
        errors.append("admission_cases_mismatch")
    if admission.get("summary") != expected_admission["summary"]:
        errors.append("admission_summary_mismatch")
    case_summary = admission.get("summary", {})
    if case_summary.get("case_count") != 19 \
            or case_summary.get("accepted_schema_controls") != 1 \
            or case_summary.get("qualifying_results") != 0 \
            or case_summary.get("rejected_count") != 18 \
            or case_summary.get("all_cases_match_expected") is not True:
        errors.append("admission_summary_invalid")
    for key in ("state_advanced_on_rejection", "runtime_invoked",
                "candidate_source_imported", "audio_read", "network_used"):
        if case_summary.get(key) is not False:
            errors.append("admission_" + key)
    for case in admission.get("cases", []):
        if case.get("qualifies") is not False:
            errors.append("admission_case_qualifies:" + str(case.get("id")))
        if case.get("status") == "rejected" \
                and (case.get("state_unchanged") is not True
                     or not case.get("code")):
            errors.append("admission_case_invalid:" + str(case.get("id")))

    if len(report.get("prohibited_claims", [])) != 8:
        errors.append("non_claim_count")
    if report.get("prohibited_claims") != list(reference.NON_CLAIMS):
        errors.append("non_claim_mismatch")

    payload = REPORT.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != f"{digest}  report.json\n":
        errors.append("report_sidecar_mismatch")
    if payload != reference.canonical_bytes(report):
        errors.append("report_not_canonical")
    try:
        reference.assert_no_float(report)
    except ValueError as error:
        errors.append("report_float:" + str(error))
    return report


def check_readme(errors: list[str]) -> int:
    path = HERE / "README.md"
    if not path.is_file():
        errors.append("readme_missing")
        return 0
    text = path.read_text(encoding="utf-8")
    try:
        counts = reference.verify_readme_digests(text)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return 0
    expected = reference.expected_readme_keys()
    for name in reference.README_SECTIONS:
        if counts.get(name) != len(expected[name]):
            errors.append("readme_section_count_mismatch:" + name)
    if text != reference.update_readme_tables(text):
        errors.append("readme_tables_stale")
    return sum(counts.values())


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        path = HERE / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_markdown_spdx:" + name)
    for path in sorted(HERE.glob("*.json")) + sorted(HERE.glob("*.sha256")):
        if not (HERE / (path.name + ".license")).is_file():
            errors.append("missing_sidecar_for:" + path.name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    reuse_token = 'SPDX-License-Identifier = "Apache-2.0"'
    # REUSE-IgnoreEnd
    if '"docs/**"' not in reuse or reuse_token not in reuse:
        errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in reference.FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            errors.append("task_symlink:" + path.name)
        if path.name in {"CMakeLists.txt", "provider.json", "adapter.json",
                         "asset.json"}:
            errors.append("provider_artifact:" + path.name)
        if path.is_file() and path.name in {"LICENSE", "LICENSE.txt",
                                            "COPYING", "NOTICE"}:
            errors.append("vendored_license_file:" + path.name)
    actual = {path.name for path in HERE.iterdir() if path.is_file()}
    if actual != reference.EXPECTED_DIR_FILES:
        for name in sorted(actual - reference.EXPECTED_DIR_FILES):
            errors.append("unpinned_task_file:" + name)
        for name in sorted(reference.EXPECTED_DIR_FILES - actual):
            errors.append("expected_task_file_missing:" + name)
    if any(HERE.rglob("__pycache__")) or any(HERE.rglob("*.pyc")):
        errors.append("bytecode_cache_present")
    if [path.name for path in HERE.iterdir() if path.is_dir()]:
        errors.append("unexpected_subdirectory")


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
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
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *arguments],
                              capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            base_paths = reference.scope_changed_paths(SDK_ROOT, base)
        except ValueError as error:
            errors.append(str(error))
        else:
            for path in reference.scope_violations(base_paths):
                errors.append("base_out_of_scope_change:" + path)
    return changed


def check_tests(errors: list[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = sum(1 for line in text.splitlines()
                if line.startswith("    def test_"))
    if count < 30:
        errors.append("fewer_than_30_reference_tests:" + str(count))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    process = subprocess.run(
        [sys.executable, "-m", "unittest", "-q", "test_reference.py"],
        cwd=HERE, capture_output=True, text=True, env=env, timeout=300)
    if process.returncode != 0:
        errors.append("test_suite_failed:" +
                      (process.stderr.strip() or process.stdout.strip()))
    return count


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk" / reference.WORKTREE.name
    target = sdk / reference.TASK_PREFIX
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    audio = scratch / "audioml"
    for name in ("research", "audio-benchmark-platform"):
        link = audio / name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / name)
    for relative in sorted(reference.SOURCE_PINS):
        if "/" in relative:
            continue
        link = audio / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / relative)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.WORKTREE / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    committed = (
        (CONTRACT.read_bytes() if CONTRACT.is_file() else b""),
        (REPORT.read_bytes() if REPORT.is_file() else b""),
        (SIDECAR.read_bytes() if SIDECAR.is_file() else b""),
        (PINS.read_bytes() if PINS.is_file() else b""),
        ((HERE / "README.md").read_bytes()
         if (HERE / "README.md").is_file() else b""),
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="sdk-pyroomacoustics-cold-") as tmp:
        root = Path(tmp)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"],
                                     cwd=target, capture_output=True,
                                     text=True, env=env, timeout=300)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" +
                              process.stderr.strip())
                continue
            generated = (
                (target / "contract.json").read_bytes(),
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
                (target / "README.md").read_bytes(),
            )
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
    pins = check_pins(errors)
    check_sources_manifest(errors)
    report = check_report(errors)
    readme_rows = check_readme(errors)
    check_licensing(errors)
    tests = check_tests(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} json_ok={bool(report)} "
              f"readme_rows={readme_rows} tests={tests} "
              f"cold_starts={len(digests)} report_sha256={digest} "
              f"changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(report['gates'])} "
          f"blockers={len(report['exact_blockers'])} "
          f"artifacts={len(report['required_artifacts'])} "
          f"tool_rows={len(report['tool_profile']['requirement_rows'])} "
          f"admission_cases={len(report['admission']['cases'])} "
          f"readme_rows={readme_rows} tests={tests} "
          f"absence_probes={report['absence_evidence']['summary']['probe_count']} "
          f"cold_starts=3/3 byte_identical=true "
          f"profile={reference.PROFILE} status={reference.STATUS} "
          f"decision={reference.DECISION} report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
