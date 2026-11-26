# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the task-local SDK-OPUS-DEEP-PLC package.

The original directory is never written. Regeneration runs in three independent
scratch trees with fresh interpreter processes and symlinks to the pinned,
read-only source and boundary files.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = HERE.parents[2]
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
VERIFICATION = (reference.AUDIO_ROOT
                / "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
# REUSE-IgnoreStart
SPDX_LICENSE = "SPDX-License-Identifier: Apache-2.0"
# REUSE-IgnoreEnd
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
    ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus", ".pcap", ".pcapng",
    ".pt", ".pth", ".pyc", ".so", ".wasm", ".wav", ".weights",
}
GATE_IDS = ("RG-01", "RG-02", "RG-03", "RG-04", "RG-05", "RG-06", "RG-07",
            "RG-08")
ARTIFACT_IDS = ("ART-01", "ART-02", "ART-03", "ART-04", "ART-05", "ART-06")
BLOCKER_IDS = ("BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05", "BLK-06")
RESTORATION_IDS = ("RST-01", "RST-02", "RST-03", "RST-04", "RST-05")
MEASUREMENT_IDS = ("MR-01", "MR-02", "MR-03", "MR-04", "MR-05")


def strict_json(path: Path) -> dict:
    return reference.read_strict_json(path)


def check_profile_source(errors: list[str]) -> None:
    expected = reference.SOURCE_PINS.get(
        "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    if not VERIFICATION.is_file():
        errors.append("verification_source_missing")
        return
    if reference.sha256_file(VERIFICATION) != expected:
        errors.append("verification_source_unpinned")
    text = VERIFICATION.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines()
            if line.startswith("| Restoration |")]
    if len(rows) != 1:
        errors.append("restoration_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("restoration_profile_phrase_missing:" + phrase[:32])


def check_pins(errors: list[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    expected: dict[str, str | None] = {}
    for relative, digest in sorted(reference.SOURCE_PINS.items()):
        expected["source:" + relative] = digest
    for relative, digest in sorted(reference.BOUNDARY_PINS.items()):
        expected[relative] = digest
    for name in run.LOCAL_PIN_FILES:
        expected[run.TASK_PREFIX + name] = None
    seen: set[str] = set()
    count = 0
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        count += 1
        parts = line.split("  ", 1)
        if (len(parts) != 2 or len(parts[0]) != 64
                or any(char not in "0123456789abcdef" for char in parts[0])):
            errors.append("malformed_pin:" + repr(line))
            continue
        digest, name = parts
        if name not in expected:
            errors.append("unexpected_pin:" + name)
            continue
        if name in seen:
            errors.append("duplicate_pin:" + name)
            continue
        seen.add(name)
        if expected[name] is not None and expected[name] != digest:
            errors.append("pinned_digest_mismatch:" + name)
        path = (reference.AUDIO_ROOT / name.split(":", 1)[1]
                if name.startswith("source:") else SDK_ROOT / name)
        if not path.is_file():
            errors.append("pin_target_missing:" + name)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + name)
    for name in sorted(set(expected) - seen):
        errors.append("pin_absent:" + name)
    if PINS.read_bytes() != run.sources_bytes():
        errors.append("manifest_not_deterministically_generated")
    if reference.BOARD_TASK_ROW in expected:
        errors.append("mutable_board_file_pinned")
    return count


def check_report(errors: list[str]) -> dict:
    try:
        report = strict_json(REPORT)
        contract = strict_json(CONTRACT)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + str(error))
        return {}
    try:
        reference.validate_contract(contract)
        if contract != reference.build_contract():
            errors.append("contract_not_recomputed")
        generated = reference.canonical_bytes(reference.build_report())
    except (OSError, ValueError, TypeError) as error:
        errors.append("reference_build_failed:" + str(error))
        return report
    payload = REPORT.read_bytes()
    if payload != generated:
        errors.append("report_not_regenerated_bytes")
    if payload != reference.canonical_bytes(report):
        errors.append("report_not_canonical_bytes")
    digest = hashlib.sha256(payload).hexdigest()
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != (
            f"{digest}  report.json\n".encode("ascii")):
        errors.append("report_digest_sidecar_stale")
    if report.get("contract_sha256") != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")

    if report.get("task_id") != reference.TASK:
        errors.append("report_task_mismatch")
    if report.get("component_id") != reference.COMPONENT_ID:
        errors.append("report_component_mismatch")
    if report.get("contract_id") != reference.CONTRACT_ID:
        errors.append("report_contract_id_mismatch")
    if report.get("profile") != "restoration" or contract.get("profile") != \
            "restoration":
        errors.append("restoration_profile_not_applied")
    if report.get("mode") != "feasibility":
        errors.append("mode_mismatch")
    if report.get("status") != "incomplete":
        errors.append("status_mismatch")
    if report.get("decision") != "DEFER":
        errors.append("decision_not_defer")
    if report.get("qualification_status") != "not_qualified":
        errors.append("qualification_status_mismatch")
    if report.get("proposal_only") is not True:
        errors.append("proposal_only_not_true")
    disposition = report.get("disposition", {})
    if (disposition.get("promotion") != "defer"
            or disposition.get("production_exposure") != "DEFER"
            or disposition.get("status") != "incomplete"
            or disposition.get("decision") != "DEFER"
            or disposition.get("qualification_status") != "not_qualified"
            or disposition.get("proposal_only") is not True
            or disposition.get("incomplete") is not True
            or disposition.get("not_qualified") is not True
            or any(disposition.get(key) is not False for key in
                   ("expose_as_processor", "registered", "default_enabled",
                    "missing_result_qualifies"))):
        errors.append("disposition_not_defer_incomplete")

    for section in ("boundary", "scope"):
        for key, value in report.get(section, {}).items():
            if key == "task_local_only":
                if value is not True:
                    errors.append(section + ".task_local_only_not_true")
                continue
            if value is not False:
                errors.append(section + "." + key + "_claim")
    qualification = report.get("qualification", {})
    if (qualification.get("status") != "not_qualified"
            or qualification.get("readiness") != "incomplete"):
        errors.append("qualification_status_or_readiness")
    for key, value in qualification.items():
        if key in ("status", "readiness"):
            continue
        expected = key in ("all_release_gates_blocked", "not_qualified")
        if value is not expected:
            errors.append("qualification." + key)
    geometry = report.get("public_v0_geometry", {})
    if (geometry.get("sample_rate_hz") != 16000
            or geometry.get("channels") != 1
            or geometry.get("sample_format") != "f32"
            or geometry.get("frame_samples") != 160
            or geometry.get("preserved") is not True
            or geometry.get("sdk_callback_invoked") is not False):
        errors.append("public_geometry_changed")
    if report.get("write_scope") != reference.WRITE_SCOPE:
        errors.append("write_scope_mismatch")
    if report.get("exact_scope", {}).get("task_local_evidence_only") is not True:
        errors.append("exact_scope_not_task_local")

    probes = report.get("absence_evidence", {}).get("probes")
    recomputed = reference.absence_probes(reference.AUDIO_ROOT)
    if probes != recomputed:
        errors.append("absence_probes_mismatch")
    summary = report.get("absence_evidence", {}).get("summary", {})
    if (summary.get("present_count") != 0
            or summary.get("all_probes_absent") is not True
            or summary.get("download_attempted") is not False
            or summary.get("recursive_workspace_walk") is not False
            or summary.get("source_or_runtime_imported") is not False):
        errors.append("absence_summary_invalid")
    observed = report.get("absence_evidence", {}).get(
        "observed_unqualified_binaries", [])
    if observed != [reference.UNQUALIFIED_RUNTIME]:
        errors.append("unqualified_runtime_observation_changed")
    for row in observed:
        if (row.get("admitted") is not False
                or row.get("linked") is not False
                or row.get("executed_by_package") is not False
                or row.get("used_for_evidence") is not False
                or row.get("deep_plc_capability_verified") is not False):
            errors.append("unqualified_runtime_admitted")
        candidate = reference.AUDIO_ROOT / row["path"]
        if candidate.is_file() and reference.sha256_file(candidate) != \
                row["sha256"]:
            errors.append("unqualified_runtime_bytes_changed")
    for relative in ("third_party/opus", "data/checkouts/opus",
                     "dnn", "include/opus_deep_plc.h"):
        if (reference.WORKTREE / relative).exists() or (
                reference.AUDIO_ROOT / relative).exists():
            errors.append("deep_plc_artifact_appeared_without_reopen:"
                          + relative)

    artifacts = report.get("required_artifacts", [])
    if tuple(row.get("id") for row in artifacts) != ARTIFACT_IDS:
        errors.append("artifact_ids_mismatch")
    for row in artifacts:
        if (row.get("present") is not False or row.get("verified") is not False
                or row.get("blocked") is not True
                or row.get("sha256") is not None or not row.get("requirement")):
            errors.append("artifact_not_blocked:" + str(row.get("id")))

    blockers = report.get("exact_blockers", [])
    if tuple(row.get("id") for row in blockers) != BLOCKER_IDS:
        errors.append("blocker_ids_mismatch")
    artifact_ids = {row["id"] for row in artifacts}
    for row in blockers:
        if (row.get("status") != "open" or row.get("qualifies") is not False
                or row.get("artifact_id") not in artifact_ids
                or not row.get("required_action")):
            errors.append("blocker_not_open:" + str(row.get("id")))

    gates = report.get("gates", [])
    if tuple(row.get("id") for row in gates) != GATE_IDS:
        errors.append("gate_ids_mismatch")
    for row in gates:
        if (row.get("status") != "blocked" or row.get("qualifies") is not False
                or not row.get("reopen_condition")
                or row.get("linked_row") != {
                    "task_id": reference.TASK,
                    "component_id": reference.COMPONENT_ID,
                    "mode": "feasibility"}):
            errors.append("gate_not_blocked:" + str(row.get("id")))
    if report.get("remaining_gates") != list(GATE_IDS):
        errors.append("remaining_gates_mismatch")
    identity = report.get("linked_row_identity", {})
    if (identity.get("projection") != reference.BOARD_ROW_PROJECTION
            or identity.get("sha256") != reference.board_row_digest(
                reference.BOARD_ROW_PROJECTION)
            or identity.get("gating") != "stable_identity_only"
            or identity.get("board_file_pinned") is not False
            or identity.get("board_status_gates_anything") is not False
            or identity.get("linked_rows") != [
                dict(row) for row in reference.LINKED_ROWS]
            or identity.get("linked_rows_sha256") !=
            reference.linked_rows_digest()):
        errors.append("linked_row_identity_invalid")
    board_path = reference.AUDIO_ROOT / reference.BOARD_TASK_ROW
    if not board_path.is_file():
        errors.append("board_row_missing")
    else:
        try:
            projection = reference.board_row_projection(board_path)
        except (OSError, ValueError) as error:
            errors.append("board_row_unreadable:" + str(error))
        else:
            if projection != reference.BOARD_ROW_PROJECTION:
                errors.append("board_row_identity_drift")

    profile = report.get("restoration_profile", {})
    if (profile.get("status") != "blocked"
            or tuple(row.get("id") for row in profile.get("rows", [])) !=
            RESTORATION_IDS
            or any(row.get("status") != "blocked"
                   for row in profile.get("rows", []))):
        errors.append("restoration_profile_not_blocked")
    for key, value in profile.items():
        if key in ("profile", "rows", "status"):
            continue
        if value is not False:
            errors.append("restoration_profile_result_claimed:" + key)
    measurements = report.get("deep_plc_measurements", {})
    if (measurements.get("status") != "blocked"
            or tuple(row.get("id") for row in measurements.get("rows", [])) !=
            MEASUREMENT_IDS
            or any(row.get("status") != "blocked"
                   or row.get("value") is not None
                   for row in measurements.get("rows", []))):
        errors.append("deep_plc_measurement_not_blocked")
    for key in ("explicit_missing_events_measured",
                "concealed_intervals_measured", "output_peak_measured",
                "delay_measured", "relative_quality_measured"):
        if measurements.get(key) is not False:
            errors.append("deep_plc_measurement_claimed:" + key)
    policy = report.get("explicit_missing_event_policy", {})
    if (policy.get("policy") != "explicit_missing_packet_events_only"
            or policy.get("inferred_loss_from_sequence_gaps") is not False
            or policy.get("missing_packet_without_event") != "rejected"
            or policy.get("event_reported_to_decoder_required") is not True
            or policy.get("event_count_observed") is not None
            or policy.get("events_recorded") is not False
            or policy.get("concealment_intervals_recorded") is not False
            or policy.get("status") != "blocked"):
        errors.append("explicit_missing_event_policy_invalid")
    required = report.get("required_results", {})
    if required.get("no_result_qualifies") is not True:
        errors.append("no_result_qualifies_not_true")
    for key, value in required.items():
        if key == "no_result_qualifies":
            continue
        if value is not False:
            errors.append("required_result_claimed:" + key)
    if report.get("prohibited_claims") != list(reference.NON_CLAIMS):
        errors.append("prohibited_claims_changed")

    admission = report.get("admission", {})
    cases = admission.get("cases", [])
    expected_cases = reference.admission_controls()
    if cases != expected_cases["cases"]:
        errors.append("admission_cases_mismatch")
    if admission.get("schema_controls") != expected_cases["controls"]:
        errors.append("admission_controls_mismatch")
    summary = admission.get("summary", {})
    if (summary.get("case_count") != len(cases)
            or summary.get("rejected_count") != len(cases)
            or summary.get("accepted_schema_controls") != 1
            or summary.get("qualifying_results") != 0
            or summary.get("state_advanced_on_rejection") is not False
            or summary.get("runtime_invoked") is not False
            or summary.get("audio_read") is not False
            or summary.get("decoding_performed") is not False
            or summary.get("concealment_executed") is not False):
        errors.append("admission_summary_invalid")
    for case in cases:
        if (case.get("status") != "rejected"
                or case.get("qualifies") is not False
                or case.get("state_unchanged") is not True
                or not case.get("code")):
            errors.append("admission_case_not_rejected:" + str(case.get("id")))

    expected_source = {
        path: {"sha256": digest, "actual": digest, "verified": True}
        for path, digest in reference.SOURCE_PINS.items()}
    expected_boundary = {
        path: {"sha256": digest, "actual": digest, "verified": True}
        for path, digest in reference.BOUNDARY_PINS.items()}
    if report.get("source_pins") != expected_source:
        errors.append("report_source_pins_mismatch")
    if report.get("boundary_pins") != expected_boundary:
        errors.append("report_boundary_pins_mismatch")

    contract_copy_keys = (
        "disposition", "boundary", "scope", "public_v0_geometry",
        "exact_scope", "qualification", "required_artifacts",
        "exact_blockers", "profile_source", "explicit_missing_event_policy",
    )
    for key in contract_copy_keys:
        if report.get(key) != contract.get(key):
            errors.append("contract_copy_mismatch:" + key)
    if report.get("gates") != contract.get("release_gates"):
        errors.append("contract_copy_mismatch:release_gates")
    if report.get("prohibited_claims") != contract.get("non_claims"):
        errors.append("contract_copy_mismatch:non_claims")
    if report.get("restoration_profile", {}).get("rows") != \
            contract.get("restoration_profile_requirements"):
        errors.append("contract_copy_mismatch:restoration_profile")
    if report.get("deep_plc_measurements", {}).get("rows") != \
            contract.get("deep_plc_measurement_requirements"):
        errors.append("contract_copy_mismatch:deep_plc_measurements")
    if contract.get("admission_contract") != reference.admission_contract_block():
        errors.append("contract_admission_contract_mismatch")
    if contract.get("source_pins") != reference.SOURCE_PINS:
        errors.append("contract_source_pins_mismatch")
    if contract.get("boundary_pins") != reference.BOUNDARY_PINS:
        errors.append("contract_boundary_pins_mismatch")

    for value in _numbers(report):
        if isinstance(value, float):
            errors.append("report_contains_float")
            break
    return report


def _numbers(value: object):
    if isinstance(value, dict):
        for item in value.values():
            yield from _numbers(item)
    elif isinstance(value, list):
        for item in value:
            yield from _numbers(item)
    else:
        yield value


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        text = ((HERE / name).read_text(encoding="utf-8") if
                (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        text = ((HERE / name).read_text(encoding="utf-8") if
                (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_markdown_spdx:" + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    reuse_token = 'SPDX-License-Identifier = "Apache-2.0"'
    # REUSE-IgnoreEnd
    if '"docs/**"' not in reuse or reuse_token not in reuse:
        errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            errors.append("task_symlink:" + path.name)
        if path.name in {"CMakeLists.txt", "provider.json", "adapter.json"}:
            errors.append("provider_artifact:" + path.name)
        if path.is_file() and path.name in {"LICENSE", "LICENSE.txt",
                                            "COPYING", "NOTICE"}:
            errors.append("vendored_license_file:" + path.name)


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
        if not path.startswith(run.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *arguments],
                              capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-OPUS-DEEP-PLC"
    target = sdk / "docs/task-evidence/opus-deep-plc"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / relative)
    board = scratch / "audioml" / reference.BOARD_TASK_ROW
    board.parent.mkdir(parents=True, exist_ok=True)
    board.symlink_to(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
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
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(
            prefix="sdk-opus-deep-plc-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"],
                                     cwd=target, capture_output=True,
                                     text=True, env=env)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" +
                              process.stderr.strip())
                continue
            generated = (
                (target / "contract.json").read_bytes(),
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
            )
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[1]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_profile_source(errors)
    pins = check_pins(errors)
    report = check_report(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} checks_ok={bool(report)} "
              f"cold_starts={len(digests)} report_sha256={digest} "
              f"changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(report['gates'])} "
          f"blockers={len(report['exact_blockers'])} "
          f"admission_cases={len(report['admission']['cases'])} "
          f"cold_starts=3/3 byte_identical=true profile=Restoration "
          f"status={report['status']} decision=DEFER report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
