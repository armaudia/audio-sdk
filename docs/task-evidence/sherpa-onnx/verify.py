# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SHERPA-ONNX evidence package.

Checks the pinned Rate profile, all source/asset/boundary pins, README digest
tables, canonical report bytes and sidecar, exact absence probes, fail-closed
caller-manifest admission, licensing, task-local git scope via the newest
merge-base, and three byte-identical cold-start regenerations. It writes only
to a temporary directory.
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
        errors.append("rate_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)
    try:
        reference.profile_row_check()
    except (OSError, ValueError) as error:
        errors.append("profile_check_failed:" + str(error))


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
    if PINS.read_bytes() != run.sources_bytes():
        errors.append("sources_manifest_drift")


def check_absence(errors: list[str]) -> None:
    try:
        evidence = reference.absence_evidence()
    except ValueError as error:
        errors.append("absence_evidence:" + str(error))
        return
    summary = evidence["summary"]
    if summary["probe_count"] != 15 or summary["present_count"] != 0:
        errors.append("absence_summary_invalid")


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
        ("rate_profile", "rate_profile"),
        ("task_geometry", "task_geometry"),
        ("upstream_record", "upstream_record"),
        ("present_assets", "present_assets"),
        ("public_v0_geometry", "public_v0_geometry"),
        ("required_artifacts", "required_artifacts"),
        ("exact_blockers", "exact_blockers"),
        ("gates", "release_gates"),
        ("rights_gap", "rights_gap"),
        ("qualification", "qualification"),
        ("admission", "admission"),
        ("geometry_control", "geometry_control"),
        ("non_claims", "non_claims"),
        ("source_pins", "source_pins"),
        ("boundary_pins", "boundary_pins"),
        ("evidence_inputs", "evidence_inputs"),
        ("linked_row_identity", "linked_row_identity"),
    )
    for report_key, contract_key in copies:
        if report.get(report_key) != contract.get(contract_key):
            errors.append("contract_copy_mismatch:" + report_key)

    qualification = report.get("qualification", {})
    if qualification.get("all_release_gates_blocked") is not True:
        errors.append("qualification_gate_flag")
    for key in (
            "real_result_present", "source_present", "exact_source_identity",
            "runtime_present", "runtime_pinned", "weights_present",
            "weights_identified", "asset_registry_entry_present",
            "rights_cleared_cohort", "streaming_geometry_verified",
            "token_timestamps_verified", "implementation_present",
            "rate_profile_result", "device_timing_result", "benchmark_result",
            "release_claim", "missing_result_promoted",
            "peer_result_inherited"):
        if qualification.get(key) is not False:
            errors.append("qualification_flag:" + key)

    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != "RG-%02d" % index:
            errors.append("gate_id:" + str(index))
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("gate_not_blocked:" + str(gate.get("id")))
        if gate.get("linked_row") != reference.TASK:
            errors.append("gate_linked_row:" + str(gate.get("id")))
        if not gate.get("reopen_condition"):
            errors.append("gate_reopen_missing:" + str(gate.get("id")))

    artifacts = report.get("required_artifacts", [])
    if len(artifacts) != 10:
        errors.append("artifact_count")
    for artifact in artifacts:
        if (artifact.get("present") is not False
                or artifact.get("verified") is not False
                or artifact.get("blocked") is not True):
            errors.append("artifact_not_blocked:" + str(artifact.get("id")))
        if (artifact.get("sha256") is not None
                or artifact.get("bytes") is not None
                or artifact.get("revision") is not None):
            errors.append("artifact_identity_invented:" +
                          str(artifact.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6:
        errors.append("blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    gate_ids = {row.get("id") for row in gates}
    for blocker in blockers:
        if blocker.get("status") != "open" or blocker.get("qualifies") is not False:
            errors.append("blocker_not_open:" + str(blocker.get("id")))
        if blocker.get("artifact_id") not in artifact_ids:
            errors.append("blocker_artifact:" + str(blocker.get("id")))
        if not blocker.get("required_action") \
                or not blocker.get("reopen_condition"):
            errors.append("blocker_action_missing:" + str(blocker.get("id")))
        for gate in blocker.get("linked_gates", []):
            if gate not in gate_ids:
                errors.append("blocker_gate:" + str(blocker.get("id")))

    profile = report.get("rate_profile", {})
    rows = profile.get("requirement_rows", [])
    if len(rows) != 8:
        errors.append("rate_row_count")
    for row in rows:
        if row.get("status") != "blocked" or row.get("qualifies") is not False:
            errors.append("rate_row_status:" + str(row.get("id")))
    summary = profile.get("row_summary", {})
    if (summary.get("requirement_count") != len(rows)
            or summary.get("real_result_count") != 0
            or summary.get("profile_satisfied") is not False):
        errors.append("rate_summary_invalid")
    if profile.get("source_check") != reference.profile_row_check():
        errors.append("rate_profile_source_mismatch")

    assets = report.get("present_assets", {})
    model = assets.get("model_tree", {})
    if (model.get("tree_sha256") != reference.MODEL_TREE_SHA256
            or model.get("file_count") != 9
            or model.get("byte_count") != 256603197):
        errors.append("present_model_tree_mismatch")
    for flag in ("license_file_present", "model_card_present",
                 "official_archive_identity_present",
                 "output_use_decision_present",
                 "streaming_token_timestamp_model"):
        if model.get(flag) is not False:
            errors.append("present_model_flag:" + flag)
    runtime = assets.get("runtime", {})
    for flag in ("wheel_archive_present", "lockfile_present",
                 "offline_load_trace_present", "source_revision_present",
                 "third_party_notice_bundle_verified", "imported_or_executed"):
        if runtime.get(flag) is not False:
            errors.append("present_runtime_flag:" + flag)

    geometry = report.get("task_geometry", {})
    for key in ("sample_rate_hz", "channels", "sample_format", "frame_samples",
                "native_hop_samples", "buffering_delay_samples",
                "right_context_samples", "endpoint_policy", "decoding_state"):
        if geometry.get(key) is not None:
            errors.append("task_geometry_invented:" + key)
    for key in ("token_timestamp_capability_verified",
                "exact_geometry_verified", "installed_v0_mapping_present"):
        if geometry.get(key) is not False:
            errors.append("task_geometry_claim:" + key)
    installed = report.get("public_v0_geometry", {})
    if (installed.get("sample_rate_hz") != 16000
            or installed.get("channels") != 1
            or installed.get("sample_format") != "f32"
            or installed.get("frame_samples") != 160
            or installed.get("preserved") is not True
            or installed.get("sherpa_onnx_mapping_present") is not False):
        errors.append("installed_geometry_mismatch")

    upstream = report.get("upstream_record", {})
    if upstream.get("immutable_revision") is not None \
            or upstream.get("source_files_present") is not False \
            or upstream.get("license_identity_verified") is not False:
        errors.append("upstream_identity_invented")

    absence = report.get("absence_evidence", {})
    expected_absence = {
        "workspace_probes": reference.workspace_probes(),
        "worktree_probes": reference.worktree_probes(),
        "home_probes": reference.home_probes(),
    }
    for key, value in expected_absence.items():
        if absence.get(key) != value:
            errors.append("absence_" + key + "_mismatch")
    if absence.get("summary") != reference.absence_summary():
        errors.append("absence_summary_mismatch")

    inputs = report.get("evidence_inputs", [])
    if inputs != reference.evidence_inputs():
        errors.append("evidence_inputs_mismatch")
    for row in inputs:
        if row.get("sha256") != reference.SOURCE_PINS.get(row.get("path")):
            errors.append("evidence_input_pin_mismatch:" + str(row.get("path")))
        if row.get("is_result") is not False or row.get("qualifies") is not False:
            errors.append("evidence_input_promoted:" + str(row.get("path")))

    if report.get("linked_row_identity") != reference.linked_identity_block():
        errors.append("linked_identity_mismatch")

    if report.get("source_pins") != reference.pin_rows(
            reference.SOURCE_PINS, reference.AUDIO_ROOT):
        errors.append("report_source_pins_mismatch")
    if report.get("boundary_pins") != reference.pin_rows(
            reference.BOUNDARY_PINS, reference.WORKTREE):
        errors.append("report_boundary_pins_mismatch")

    admission = report.get("admission", {})
    expected_admission = reference.admission_cases()
    if admission.get("cases") != expected_admission["cases"]:
        errors.append("admission_cases_mismatch")
    if admission.get("controls") != expected_admission["controls"]:
        errors.append("admission_controls_mismatch")
    if admission.get("summary") != expected_admission["summary"]:
        errors.append("admission_summary_mismatch")
    case_summary = admission.get("summary", {})
    if case_summary.get("accepted_schema_controls") != 1 \
            or case_summary.get("qualifying_results") != 0 \
            or case_summary.get("rejected_count") != \
            case_summary.get("case_count", 0) - 1:
        errors.append("admission_summary_invalid")
    for case in admission.get("cases", []):
        if case.get("qualifies") is not False:
            errors.append("admission_case_qualifies:" + str(case.get("id")))
        if case.get("status") == "rejected" \
                and (case.get("state_unchanged") is not True
                     or not case.get("code")):
            errors.append("admission_case_invalid:" + str(case.get("id")))

    if report.get("geometry_control") != reference.geometry_control():
        errors.append("geometry_control_mismatch")
    if report.get("non_claims") != reference.NON_CLAIMS:
        errors.append("non_claim_mismatch")

    payload = REPORT.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != digest + "  report.json\n":
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
         "--untracked-files=all"], capture_output=True, text=True)
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
    for code in reference.scope_error_codes(SDK_ROOT):
        errors.append(code)
    return changed


def check_tests(errors: list[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = sum(1 for line in text.splitlines()
                if line.startswith("    def test_"))
    if count < 40:
        errors.append("fewer_than_40_reference_tests:" + str(count))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    process = subprocess.run(
        [sys.executable, "-m", "unittest", "-q", "test_reference.py"],
        cwd=HERE, capture_output=True, text=True, env=env, timeout=300)
    if process.returncode != 0:
        errors.append("test_suite_failed:" +
                      (process.stderr.strip() or process.stdout.strip()))
    return count


def _prepare_scratch(root: Path, index: int) -> Path:
    """Build an isolated tree whose parents resolve to a synthetic root.

    Every pinned input is a symlink to the real read-only bytes, so a cold
    run cannot mutate the workspace or the SDK worktree. The scratch root
    carries the two marker entries that _find_audio_root requires.
    """
    scratch = root / ("cold-" + str(index))
    sdk = scratch / "worktrees/audio-sdk/SDK-SHERPA-ONNX"
    target = sdk / reference.TASK_PREFIX
    target.mkdir(parents=True)
    (scratch / "research").mkdir(exist_ok=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    board = scratch / reference.BOARD_TASK_ROW
    board.parent.mkdir(parents=True, exist_ok=True)
    board.symlink_to(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
    for relative in sorted(reference.SOURCE_PINS):
        destination = scratch / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(reference.AUDIO_ROOT / relative)
    for relative in sorted(reference.BOUNDARY_PINS):
        destination = sdk / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(reference.WORKTREE / relative)
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
    with tempfile.TemporaryDirectory(prefix="sdk-sherpa-onnx-cold-") as tmp:
        root = Path(tmp)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"],
                                     cwd=target, capture_output=True,
                                     text=True, env=env, timeout=600)
            if process.returncode != 0:
                errors.append("cold_start_" + str(index) + "_failed:"
                              + process.stderr.strip())
                continue
            generated = (
                (target / "contract.json").read_bytes(),
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
                (target / "README.md").read_bytes(),
            )
            if generated != committed:
                errors.append("cold_start_" + str(index) + "_bytes_differ")
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
    check_absence(errors)
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
        print("FAIL pins=%d json_ok=%s readme_rows=%d tests=%d "
              "cold_starts=%d report_sha256=%s changed_files=%d "
              "failures=%d"
              % (pins, bool(report), readme_rows, tests, len(digests),
                 digest, len(changed), len(errors)))
        return 1
    print("PASS pins=%d gates=%d blockers=%d artifacts=%d rate_rows=%d "
          "admission_cases=%d readme_rows=%d tests=%d absence_probes=%d "
          "cold_starts=3/3 byte_identical=true profile=%s status=%s "
          "decision=%s report_sha256=%s changed_files=%d"
          % (pins, len(report["gates"]), len(report["exact_blockers"]),
             len(report["required_artifacts"]),
             len(report["rate_profile"]["requirement_rows"]),
             len(report["admission"]["cases"]), readme_rows, tests,
             report["absence_evidence"]["summary"]["probe_count"],
             reference.PROFILE, reference.STATUS, reference.DECISION,
             digest, len(changed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
