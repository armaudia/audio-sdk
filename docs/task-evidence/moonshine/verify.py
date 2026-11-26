# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-MOONSHINE DEFER evidence package.

Checks the Rate-profile source row, exact source/boundary pins, the fixed
absence-probe result, canonical report and contract bytes, the contract digest,
eight blocked release gates, six open blockers, the synthetic granularity and
admission controls, licensing/REUSE boundaries, merge-base task-local git scope
and three fresh byte-identical regenerations. It writes only to a temporary
directory.
"""

from __future__ import annotations

import hashlib
import os
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

# REUSE-IgnoreStart
SPDX_LICENSE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd

SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)


def check_profile_source(errors: list[str]) -> None:
    path = reference.AUDIO_ROOT / reference.PROFILE_SOURCE_REL
    if not path.is_file():
        errors.append("profile_source_missing")
        return
    rows = [line for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("| Rate |")]
    if len(rows) != 1:
        errors.append("rate_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)
    if reference.PROFILE_LABEL != "Rate":
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
            actual = reference.sha256_file(path)
            if actual != expected:
                errors.append(label + "_pin_mismatch:" + relative)
            checked += 1
    if reference.BOARD_TASK_ROW in reference.SOURCE_PINS \
            or reference.BOARD_TASK_ROW in reference.BOUNDARY_PINS:
        errors.append("mutable_board_pinned")
    return checked


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract_missing")
        return {}
    try:
        contract = reference.read_strict_json(CONTRACT)
        reference.validate_contract(contract)
    except ValueError as error:
        errors.append("contract_validation:" + str(error))
        return {}
    if contract.get("decision") != "DEFER" \
            or contract.get("status") != "proposal_only_incomplete" \
            or contract.get("qualification_status") != "not_qualified" \
            or contract.get("proposal_only") is not True \
            or contract.get("incomplete") is not True:
        errors.append("contract_disposition")
    if contract.get("board_file_pinned") is not False:
        errors.append("contract_board_pinned")
    if contract.get("evidence_status") != "incomplete":
        errors.append("contract_evidence_status")
    if CONTRACT.read_bytes() != reference.canonical_bytes(contract):
        errors.append("contract_not_canonical")
    return contract


def check_absence(errors: list[str]) -> dict:
    try:
        probes = reference._probes_block()
    except ValueError as error:
        errors.append("absence_rebuild:" + str(error))
        return {}
    summary = probes["summary"]
    if summary["all_probes_absent"] is not True \
            or summary["present_count"] != 0:
        errors.append("absence_present")
    if summary["probe_count"] != len(reference.SOURCE_PROBE_PATHS) + \
            len(reference.WEIGHTS_PROBE_PATHS) + \
            len(reference.RUNTIME_PROBE_PATHS) + \
            len(reference.HOME_PROBE_PATHS):
        errors.append("absence_probe_count")
    if summary["download_attempted"] is not False \
            or summary["network_used"] is not False \
            or summary["source_or_runtime_imported"] is not False:
        errors.append("absence_scope")
    return probes


def check_report(errors: list[str], contract: dict) -> dict:
    if not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}
    try:
        report = reference.read_strict_json(REPORT)
        reference._no_floats(report)
    except ValueError as error:
        errors.append("strict_json_failure:" + str(error))
        return {}

    if report.get("schema_id") != reference.REPORT_SCHEMA_ID:
        errors.append("report_schema_mismatch")
    for field, expected in (("task", reference.TASK),
                            ("component", reference.COMPONENT_ID),
                            ("mode", reference.MODE),
                            ("profile", reference.PROFILE),
                            ("decision", "DEFER"),
                            ("status", "proposal_only_incomplete"),
                            ("evidence_status", "incomplete"),
                            ("qualification_status", "not_qualified"),
                            ("proposal_only", True),
                            ("incomplete", True)):
        if report.get(field) != expected:
            errors.append("report_field:" + field)

    if contract:
        if report.get("contract_sha256") != reference.object_digest(contract):
            errors.append("contract_digest_mismatch")
        for key in ("disposition", "qualification", "scope", "boundary",
                    "public_v0_geometry", "non_claims", "upstream_record",
                    "required_artifacts", "exact_blockers", "required_results",
                    "peer_evidence", "reproduction"):
            if report.get(key) != contract.get(key):
                errors.append("contract_copy_mismatch:" + key)
        if report.get("gates") != contract.get("release_gates"):
            errors.append("contract_copy_mismatch:release_gates")
        if report.get("rate_profile", {}).get("rows") != \
                contract.get("rate_profile_requirements"):
            errors.append("contract_copy_mismatch:rate_profile")
        if report.get("rate_outcomes", {}).get("rows") != \
                contract.get("rate_outcomes"):
            errors.append("contract_copy_mismatch:rate_outcomes")

    absence = check_absence(errors)
    if absence and report.get("absence") != absence:
        errors.append("absence_mismatch")

    expected_source, expected_boundary = reference.verify_pins()
    if report.get("source_pins") != expected_source:
        errors.append("report_source_pins_mismatch")
    if report.get("boundary_pins") != expected_boundary:
        errors.append("report_boundary_pins_mismatch")

    upstream = report.get("upstream_record", {})
    if upstream.get("source_revision") is not None \
            or upstream.get("model_revision") is not None \
            or upstream.get("license_verified") is not False \
            or upstream.get("license_text_present") is not False \
            or upstream.get("admitted_as_result") is not False \
            or upstream.get("source_reported_only") is not True:
        errors.append("upstream_record_overclaim")
    for key in ("source_repository", "reported_finding", "reported_role"):
        if not upstream.get(key):
            errors.append("upstream_record_missing:" + key)

    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != "RG-{:02d}".format(index):
            errors.append("gate_id:" + str(index))
        if gate.get("status") != "blocked" \
                or gate.get("qualifies") is not False:
            errors.append("gate_not_blocked:" + str(gate.get("id")))
        if not gate.get("reopen_condition"):
            errors.append("gate_reopen_missing:" + str(gate.get("id")))
        if gate.get("linked_row") != \
                report.get("linked_row_identity", {}).get("projection"):
            errors.append("gate_linked_row:" + str(gate.get("id")))

    artifacts = report.get("required_artifacts", [])
    if len(artifacts) != 8:
        errors.append("artifact_count")
    for row in artifacts:
        if row.get("present") is not False \
                or row.get("verified") is not False \
                or row.get("licensed") is not False \
                or row.get("admitted") is not False \
                or row.get("blocked") is not True \
                or row.get("sha256") is not None \
                or row.get("revision") is not None \
                or row.get("bytes") is not None:
            errors.append("artifact_state:" + str(row.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6:
        errors.append("blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    for blocker in blockers:
        if blocker.get("status") != "open" \
                or blocker.get("qualifies") is not False:
            errors.append("blocker_state:" + str(blocker.get("id")))
        if blocker.get("artifact_id") not in artifact_ids:
            errors.append("blocker_artifact:" + str(blocker.get("id")))
        if not blocker.get("required_action") \
                or not blocker.get("statement"):
            errors.append("blocker_text:" + str(blocker.get("id")))
        if not blocker.get("linked_gates"):
            errors.append("blocker_gates:" + str(blocker.get("id")))

    rate_rows = report.get("rate_profile", {}).get("rows", [])
    if len(rate_rows) != 8:
        errors.append("rate_row_count")
    for row in rate_rows:
        if row.get("status") != "blocked" \
                or row.get("qualifies") is not False:
            errors.append("rate_row_not_blocked:" + str(row.get("id")))
    outcomes = report.get("rate_outcomes", {}).get("rows", [])
    if len(outcomes) != 8:
        errors.append("rate_outcome_count")
    for row in outcomes:
        if row.get("status") != "blocked" \
                or row.get("value") is not None \
                or row.get("qualifies") is not False:
            errors.append("rate_outcome_not_blocked:" + str(row.get("id")))

    try:
        expected_control = reference.granularity_control()
        expected_admission = reference.admission_controls()
    except ValueError as error:
        errors.append("control_rebuild:" + str(error))
    else:
        if report.get("granularity_control") != expected_control:
            errors.append("granularity_control_mismatch")
        if report.get("admission") != expected_admission:
            errors.append("admission_mismatch")

    control = report.get("granularity_control", {})
    summary = control.get("summary", {})
    if control.get("evidence_class") != \
            "synthetic_contract_control_not_evidence":
        errors.append("granularity_control_class")
    if control.get("qualifies") is not False \
            or summary.get("qualifying_results") != 0:
        errors.append("granularity_control_qualified")
    if summary.get("case_count") != 4 \
            or summary.get("boundary_stable_cases") != 2 \
            or summary.get("granularity_sensitive_cases") != 2 \
            or summary.get("overlapping_quantizations") != 1 \
            or summary.get("final_partial_cases") != 1:
        errors.append("granularity_control_counts")
    observed = control.get("observed", {})
    if observed.get("fine_vs_coarse_rate_differ") is not True \
            or observed.get("aligned_identity") is not True \
            or observed.get("final_partial_samples") != 65:
        errors.append("granularity_control_observed")
    for key in ("model_executed", "runtime_imported", "audio_read",
                "network_used"):
        if summary.get(key) is not False:
            errors.append("granularity_control_" + key)

    admission = report.get("admission", {})
    am = admission.get("summary", {})
    if am.get("qualifying_results") != 0 \
            or am.get("accepted_schema_controls") != 1 \
            or am.get("all_adverse_cases_rejected") is not True \
            or am.get("accepted_control_qualifies") is not False:
        errors.append("admission_summary_invalid")
    if am.get("rejected_count") != am.get("case_count") - 1:
        errors.append("admission_not_all_rejected")
    for key in ("state_advanced_on_rejection", "runtime_invoked",
                "weights_loaded", "audio_read", "inference_performed",
                "network_used"):
        if am.get(key) is not False:
            errors.append("admission_" + key)
    for case in admission.get("cases", []):
        if case.get("status") == "rejected":
            if case.get("code") in ("", "none") \
                    or case.get("qualifies") is not False \
                    or case.get("state_unchanged") is not True:
                errors.append("admission_case:" + str(case.get("id")))
        elif case.get("status") == "accepted":
            if case.get("qualifies") is not False \
                    or case.get("synthetic_schema_control") is not True \
                    or case.get("state_unchanged") is not False:
                errors.append("admission_control_case")
        else:
            errors.append("admission_case_status:" + str(case.get("id")))

    identity = report.get("linked_row_identity", {})
    if identity.get("projection") != reference.board_row_projection():
        errors.append("linked_projection_mismatch")
    if identity.get("sha256") != reference.board_row_digest(
            identity.get("projection", {})):
        errors.append("linked_projection_digest")
    if identity.get("gating") != "stable_identity_only":
        errors.append("linked_gating")
    if identity.get("board_file_pinned") is not False:
        errors.append("board_file_pinned")
    if identity.get("board_status_gates_anything") is not False:
        errors.append("board_status_gates")
    if identity.get("linked_rows") != reference.linked_rows():
        errors.append("linked_rows_mismatch")
    if identity.get("linked_rows_sha256") != reference.linked_rows_digest():
        errors.append("linked_rows_digest")
    for excluded in ("status", "owner", "claim", "review", "handoff",
                     "blocked_reason", "dispatch_priority"):
        if excluded in identity.get("projection", {}):
            errors.append("mutable_field_in_projection:" + excluded)

    required = report.get("required_results", {})
    for key, value in required.items():
        if key == "no_result_qualifies":
            if value is not True:
                errors.append("required_results_no_result_qualifies")
        elif value is not False:
            errors.append("required_results_present:" + key)

    payload = REPORT.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != digest + "  report.json\n":
        errors.append("report_sidecar_mismatch")
    if payload != reference.canonical_bytes(report):
        errors.append("report_not_canonical")
    if PINS.is_file():
        try:
            reference.verify_sources_manifest(PINS.read_bytes())
            expected_pins = run.sources_bytes()
        except ValueError as error:
            errors.append("sources_rebuild:" + str(error))
        else:
            if PINS.read_bytes() != expected_pins:
                errors.append("sources_manifest_mismatch")
    else:
        errors.append("sources_manifest_missing")
    return report


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        text = ((HERE / name).read_text(encoding="utf-8")
                if (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        text = ((HERE / name).read_text(encoding="utf-8")
                if (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_markdown_spdx:" + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    reuse_token = 'SPDX-License-' 'Identifier = "Apache-2.0"'
    # REUSE-IgnoreEnd
    if '"docs/**"' not in reuse or reuse_token not in reuse:
        errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in reference.FORBIDDEN_SUFFIXES:
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
            for path in base_paths:
                if path not in changed:
                    changed.append(path)
        committed = subprocess.run(
            ["git", "-C", str(SDK_ROOT), "diff", "--check", base + "..HEAD"],
            capture_output=True, text=True)
        if committed.returncode != 0 or committed.stdout.strip():
            errors.append("committed_git_diff_check_failed:"
                          + committed.stdout.strip())
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / ("cold-" + str(index))
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-MOONSHINE"
    target = sdk / reference.TASK_PREFIX
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
    env.pop("SOURCE_ROOT", None)
    with tempfile.TemporaryDirectory(prefix="sdk-moonshine-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run(
                [sys.executable, "run.py", "all"], cwd=target,
                capture_output=True, text=True, env=env)
            if process.returncode != 0:
                errors.append("cold_start_{}_failed:".format(index)
                              + process.stderr.strip())
                continue
            generated = (
                (target / "contract.json").read_bytes(),
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
            )
            if generated != committed:
                errors.append("cold_start_{}_bytes_differ".format(index))
            digests.append(hashlib.sha256(generated[1]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_profile_source(errors)
    pins = check_pins(errors)
    contract = check_contract(errors)
    report = check_report(errors, contract)
    check_licensing(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print("FAIL pins={} checks_ok={} cold_starts={} "
              "report_sha256={} changed_files={} failures={}".format(
                  pins, bool(report), len(digests), digest, len(changed),
                  len(errors)))
        return 1
    print("PASS pins={} gates={} blockers={} artifacts={} "
          "admission_cases={} granularity_cases={} cold_starts=3/3 "
          "byte_identical=true profile=Rate status={} decision=DEFER "
          "qualification={} report_sha256={} changed_files={}".format(
              pins, len(report["gates"]), len(report["exact_blockers"]),
              len(report["required_artifacts"]),
              len(report["admission"]["cases"]),
              len(report["granularity_control"]["cases"]),
              report["status"], report["qualification"]["status"], digest,
              len(changed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
