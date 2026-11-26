# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SE-AGCNET evidence package.

Checks DSP profile phrases, source/boundary pins, README digest tables, canonical
report bytes and sidecar, blocked artifacts/gates/blockers, fixed absence probes,
fail-closed admission cases, licensing/REUSE boundaries, task-local git scope via
newest merge-base, and three byte-identical cold regenerations. It writes only to
a temporary directory.
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
SPDX_LICENSE = "SPDX-License-" + "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan"
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
    rows = [line for line in PROFILE_SOURCE.read_text(encoding="utf-8").splitlines() if line.startswith("| DSP |")]
    if len(rows) != 1:
        errors.append("dsp_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)
    if reference.PROFILE_LABEL != "DSP":
        errors.append("profile_label_mismatch")


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in ((reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"), (reference.BOUNDARY_PINS, reference.WORKTREE, "boundary")):
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

    expected = {
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
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append("report_field:" + key)
    for key in ("proposal_only", "incomplete"):
        if report.get(key) is not True:
            errors.append("report_flag:" + key)
    if report.get("contract_sha256") != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")

    for report_key, contract_key in (
        ("disposition", "disposition"), ("boundary", "boundary"), ("scope", "exact_scope"),
        ("exact_scope", "exact_scope"), ("public_v0_geometry", "public_v0_geometry"),
        ("task_geometry", "task_geometry"), ("upstream_record", "upstream_record"),
        ("recorded_identity", "recorded_identity"), ("reported_metrics", "reported_metrics"),
        ("required_artifacts", "required_artifacts"), ("exact_blockers", "exact_blockers"),
        ("gates", "release_gates"), ("enhancement_profile", "enhancement_profile"),
        ("qualification", "qualification"),
    ):
        if report_key == "public_v0_geometry":
            continue
        if report.get(report_key) != contract.get(contract_key):
            errors.append("contract_copy_mismatch:" + report_key)

    qualification = report.get("qualification", {})
    if qualification.get("all_release_gates_blocked") is not True:
        errors.append("qualification_flag:all_release_gates_blocked")
    for key in ("real_result_present", "source_present", "exact_source_identity", "source_license_verified", "runtime_present", "runtime_pinned", "weights_present_locally", "weights_identity_verified", "rights_cleared_cohort", "exact_geometry_verified", "sdk_bridge_verified", "target_hardware_evidence_verified", "implementation_present", "reference_execution_result", "dsp_profile_result", "listening_result", "device_timing_result", "benchmark_result", "release_claim", "missing_result_promoted", "peer_result_inherited", "recorded_identity_only"):
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

    artifacts = report.get("required_artifacts", [])
    if len(artifacts) != 7:
        errors.append("artifact_count")
    for artifact in artifacts:
        if artifact.get("present") is not False or artifact.get("verified") is not False or artifact.get("blocked") is not True:
            errors.append("artifact_not_blocked:" + str(artifact.get("id")))
        if artifact.get("sha256") is not None or artifact.get("revision") is not None or artifact.get("bytes") is not None:
            errors.append("artifact_identity_invented:" + str(artifact.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6:
        errors.append("blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    gate_ids = {row.get("id") for row in gates}
    for blocker in blockers:
        if blocker.get("status") != "open":
            errors.append("blocker_not_open:" + str(blocker.get("id")))
        if blocker.get("qualifies") is not False:
            errors.append("blocker_qualifies:" + str(blocker.get("id")))
        if blocker.get("artifact_id") not in artifact_ids:
            errors.append("blocker_artifact:" + str(blocker.get("id")))
        if not blocker.get("required_action") or not blocker.get("reopen_condition"):
            errors.append("blocker_action_missing:" + str(blocker.get("id")))
        for gate in blocker.get("linked_gates", []):
            if gate not in gate_ids:
                errors.append("blocker_gate:" + str(blocker.get("id")))

    profile = report.get("enhancement_profile", {})
    rows = profile.get("requirement_rows", [])
    if len(rows) != len(reference.DSP_REQUIREMENTS):
        errors.append("dsp_row_count")
    for row in rows:
        if row.get("status") not in ("blocked", "documented"):
            errors.append("dsp_row_status:" + str(row.get("id")))
    summary = profile.get("row_summary", {})
    if summary.get("requirement_count") != len(rows) or summary.get("real_result_count") != 0 or summary.get("profile_satisfied") is not False:
        errors.append("dsp_summary_invalid")
    if profile.get("profile_source_check") != reference.profile_row_check():
        errors.append("dsp_profile_source_mismatch")

    absence = report.get("absence_summary", {})
    if absence.get("all_probes_absent") is not True or absence.get("present_count") != 0:
        errors.append("absence_not_clean")
    for probe in report.get("absence_probes", []):
        if probe.get("present"):
            errors.append("probe_present:" + str(probe.get("path")))

    admission = report.get("admission_controls", {})
    adm_summary = admission.get("summary", {})
    if adm_summary.get("qualifying_results") != 0:
        errors.append("admission_qualifying_result")
    if adm_summary.get("accepted_schema_controls") != 1:
        errors.append("admission_accepted_count")
    for case in admission.get("cases", []):
        if case.get("qualifies"):
            errors.append("admission_case_qualifies:" + str(case.get("id")))
        if case.get("id") != "accept_synthetic_control" and case.get("status") != "rejected":
            errors.append("admission_case_not_rejected:" + str(case.get("id")))

    sidecar = SIDECAR.read_text(encoding="ascii").strip()
    _, expected_digest = reference.canonical_report(report)
    expected_sidecar = f"{expected_digest}  report.json"
    if sidecar != expected_sidecar:
        errors.append("sidecar_mismatch")
    if reference.sha256_file(REPORT) != expected_digest:
        errors.append("report_file_digest_mismatch")
    if contract.get("board_row_digest") != reference.board_row_digest():
        errors.append("board_row_digest_mismatch")
    if contract.get("linked_rows_digest") != reference.linked_rows_digest():
        errors.append("linked_rows_digest_mismatch")
    return report


def check_readme_tables(errors: list[str]) -> None:
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    refreshed = reference.update_readme_tables(readme)
    if refreshed != readme:
        errors.append("readme_tables_stale")


def check_licensing(errors: list[str]) -> None:
    for name in reference.LOCAL_FILES:
        path = HERE / name
        if not path.is_file():
            errors.append("missing_local_file:" + name)
            continue
        if name.endswith(".license"):
            text = path.read_text(encoding="utf-8")
            if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
                errors.append("sidecar_missing_spdx:" + name)
            continue
        if name.endswith('.json') or name.endswith('.sha256') or name == 'SOURCES.sha256':
            side = HERE / (name + '.license')
            if not side.is_file():
                errors.append('missing_sidecar:' + name)
            continue
        text = path.read_text(encoding="utf-8")
        if SPDX_LICENSE not in text:
            errors.append("missing_spdx:" + name)
    for name in SIDECARS:
        if not (HERE / name).is_file():
            errors.append("missing_sidecar:" + name)

    # REUSE boundary: do not place contiguous SPDX token in Python string literals.
    contiguous = "SPDX-" + "License-Identifier: Apache-2.0"
    for py in ("reference.py", "run.py", "verify.py", "test_reference.py"):
        text = (HERE / py).read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if contiguous not in line:
                continue
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            if ("'" + contiguous + "'" in line) or ('"' + contiguous + '"' in line):
                errors.append(f"contiguous_spdx_literal:{py}:{line_no}")


def check_forbidden_files(errors: list[str]) -> None:
    for path in HERE.iterdir():
        if path.is_file() and path.suffix.lower() in reference.FORBIDDEN_SUFFIXES:
            errors.append("forbidden_file:" + path.name)
    present = {p.name for p in HERE.iterdir() if p.is_file()}
    extra = sorted(present - reference.EXPECTED_DIR_FILES)
    missing = sorted(reference.EXPECTED_DIR_FILES - present)
    for name in extra:
        errors.append("unexpected_file:" + name)
    for name in missing:
        errors.append("missing_expected_file:" + name)


def newest_merge_base() -> str:
    # read-only git inspection in worktree
    result = subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=SDK_ROOT, capture_output=True, text=True, check=False)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().splitlines()[0]
    result = subprocess.run(["git", "merge-base", "--all", "HEAD", "origin/main"], cwd=SDK_ROOT, capture_output=True, text=True, check=False)
    if result.returncode == 0 and result.stdout.strip():
        bases = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if bases:
            # newest by committer date
            dates = []
            for b in bases:
                dt = subprocess.run(["git", "show", "-s", "--format=%ct", b], cwd=SDK_ROOT, capture_output=True, text=True, check=False)
                dates.append((int(dt.stdout.strip() or "0"), b))
            dates.sort()
            return dates[-1][1]
    # fallback to HEAD~1 not ideal, but try origin/main direct
    result = subprocess.run(["git", "rev-parse", "origin/main"], cwd=SDK_ROOT, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return result.stdout.strip()
    raise RuntimeError("merge_base_unavailable")


def check_git_scope(errors: list[str]) -> None:
    try:
        base = newest_merge_base()
    except Exception as error:
        errors.append("merge_base_error:" + str(error))
        return
    diff = subprocess.run(["git", "diff", "--name-only", base + "..HEAD"], cwd=SDK_ROOT, capture_output=True, text=True, check=False)
    if diff.returncode != 0:
        errors.append("git_diff_failed")
        return
    changed = [line.strip() for line in diff.stdout.splitlines() if line.strip()]
    for path in changed:
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    # also ensure worktree clean except maybe untracked in task dir? we only check tracked scope; status checked separately by caller.


def check_regeneration(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="se-agcnet-verify-") as tmp:
        tmp_dir = Path(tmp)
        pkg = tmp_dir / "pkg"
        pkg.mkdir()
        for name in reference.LOCAL_FILES:
            shutil.copy2(HERE / name, pkg / name)
        # run run.py three times in temp copy by executing as script with cwd temp pkg; it writes only in its dir
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["SOURCE_ROOT"] = str(reference.AUDIO_ROOT)
        env["SDK_ROOT"] = str(reference.WORKTREE)
        digests = []
        for _ in range(3):
            proc = subprocess.run([sys.executable, str(pkg / "run.py"), "all"], cwd=pkg, capture_output=True, text=True, env=env)
            if proc.returncode != 0:
                errors.append("regen_failed:" + proc.stdout + proc.stderr)
                return
            digests.append((
                hashlib.sha256((pkg / "report.json").read_bytes()).hexdigest(),
                hashlib.sha256((pkg / "report.json.sha256").read_bytes()).hexdigest(),
                hashlib.sha256((pkg / "SOURCES.sha256").read_bytes()).hexdigest(),
            ))
        if len(set(digests)) != 1:
            errors.append("regen_not_deterministic")
        # compare to committed
        for name in ("report.json", "report.json.sha256", "SOURCES.sha256", "contract.json"):
            if (pkg / name).read_bytes() != (HERE / name).read_bytes():
                errors.append("regen_drift:" + name)


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_profile_source(errors)
    pin_count = check_pins(errors)
    check_sources_manifest(errors)
    report = check_report(errors)
    check_readme_tables(errors)
    check_licensing(errors)
    check_forbidden_files(errors)
    check_git_scope(errors)
    check_regeneration(errors)
    if errors:
        for e in errors:
            print("FAIL", e)
        print(f"FAIL count={len(errors)}")
        return 1
    print(
        "PASS"
        f" task={reference.TASK}"
        f" decision={reference.DECISION}"
        f" qualification={reference.QUALIFICATION_STATUS}"
        f" gates={len(report.get('gates', []))}"
        f" artifacts={len(report.get('required_artifacts', []))}"
        f" blockers={len(report.get('exact_blockers', []))}"
        f" probes={report.get('absence_summary', {}).get('probe_count', 0)}"
        f" pins={pin_count}"
        f" regen=3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
