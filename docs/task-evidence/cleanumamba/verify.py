# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-CLEANUMAMBA DEFER evidence package.

Checks the Enhancement-profile phrases, exact source/boundary/sibling pins, the
observed upstream commit/tree/checkpoint ledger, strict canonical JSON, the
report digest sidecar, README digest tables, fail-closed manifest and frame
controls, eight blocked gates, six open blockers, licensing/REUSE boundaries,
task-local git scope and three fresh byte-identical regenerations. It writes
only to a temporary directory.
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
SPDX_LICENSE = "SPDX-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd

SIDECARS = (
    "SOURCES.sha256.license",
    "UPSTREAM_MANIFEST.json.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)


def check_profile_source(errors: list[str]) -> None:
    path = (reference.AUDIO_ROOT /
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    if not path.is_file():
        errors.append("profile_source_missing")
        return
    rows = [line for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("| Enhancement |")]
    if len(rows) != 1:
        errors.append("enhancement_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)
    if reference.PROFILE_LABEL != "Enhancement":
        errors.append("profile_label_mismatch")


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in (
            (reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"),
            (reference.BOUNDARY_PINS, reference.WORKTREE, "boundary"),
            (reference.SIBLING_PINS, reference.WORKTREE, "sibling")):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append(label + "_pin_missing:" + relative)
                continue
            actual = reference.sha256_file(path)
            if actual != expected:
                errors.append(label + "_pin_mismatch:" + relative)
            checked += 1
    for pins in (reference.SOURCE_PINS, reference.BOUNDARY_PINS,
                 reference.SIBLING_PINS):
        if reference.BOARD_TASK_ROW in pins:
            errors.append("mutable_board_pinned")
    return checked


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract_missing")
        return {}
    try:
        contract = reference.read_strict_json(CONTRACT)
    except ValueError as error:
        errors.append("contract_strict_json:" + str(error))
        return {}
    if contract.get("schema_id") != reference.CONTRACT_SCHEMA_ID:
        errors.append("contract_schema_mismatch")
    if contract.get("task") != reference.TASK:
        errors.append("contract_task_mismatch")
    if contract.get("component") != reference.COMPONENT_ID:
        errors.append("contract_component_mismatch")
    if contract.get("decision") != "DEFER" \
            or contract.get("status") != "incomplete" \
            or contract.get("qualification_status") != "not_qualified" \
            or contract.get("proposal_only") is not True:
        errors.append("contract_disposition")
    if contract.get("board_file_pinned") is not False:
        errors.append("contract_board_pinned")
    if CONTRACT.read_bytes() != reference.canonical_bytes(contract):
        errors.append("contract_not_canonical")
    try:
        expected = reference.build_contract()
    except ValueError as error:
        errors.append("contract_rebuild:" + str(error))
    else:
        if contract != expected:
            errors.append("contract_rebuild_mismatch")
    return contract


def check_report(errors: list[str], contract: dict) -> dict:
    if not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}
    try:
        report = reference.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("report_strict_json:" + str(error))
        return {}
    if report.get("schema_id") != reference.REPORT_SCHEMA_ID:
        errors.append("report_schema_mismatch")
    if report.get("task") != reference.TASK:
        errors.append("report_task_mismatch")
    if report.get("component") != reference.COMPONENT_ID:
        errors.append("report_component_mismatch")
    if report.get("decision") != "DEFER":
        errors.append("report_decision_not_defer")
    if report.get("status") != "incomplete":
        errors.append("report_status_not_incomplete")
    if report.get("qualification_status") != "not_qualified":
        errors.append("report_qualification_not_not_qualified")
    if report.get("proposal_only") is not True:
        errors.append("report_not_proposal_only")
    if contract:
        if report.get("contract_sha256") != reference.object_digest(contract):
            errors.append("contract_digest_mismatch")
        for key in (
                "disposition", "qualification", "scope", "boundary",
                "public_v0_geometry", "non_claims", "license_findings",
                "exact_blockers", "required_artifacts", "required_results",
                "upstream_observation", "checkpoint_ledger",
                "geometry_control", "enhancement_profile_requirements",
                "caller_asset", "reproduction", "linked_row_identity"):
            if report.get(key) != contract.get(key):
                errors.append("contract_copy_mismatch:" + key)
        if report.get("gates") != contract.get("release_gates"):
            errors.append("contract_copy_mismatch:release_gates")

    try:
        expected_manifest = reference.manifest_control()
        expected_frame = reference.frame_control()
        expected_ledger = reference.checkpoint_ledger_control()
        expected_geometry = reference.geometry_control()
    except ValueError as error:
        errors.append("control_rebuild:" + str(error))
    else:
        if report.get("manifest_control") != expected_manifest:
            errors.append("manifest_control_mismatch")
        if report.get("frame_control") != expected_frame:
            errors.append("frame_control_mismatch")
        if report.get("checkpoint_ledger") != expected_ledger:
            errors.append("checkpoint_ledger_mismatch")
        if report.get("geometry_control") != expected_geometry:
            errors.append("geometry_control_mismatch")

    if report.get("source_presence") != reference.source_presence():
        errors.append("source_presence_mismatch")
    presence = report.get("source_presence", {})
    if presence.get("upstream_metadata_observed") is not True:
        errors.append("upstream_metadata_missing")
    if presence.get("any_probe_present") is not False \
            or presence.get("upstream_source_bytes_present") is not False \
            or presence.get("checkpoint_bytes_present") is not False \
            or presence.get("runtime_environment_present") is not False:
        errors.append("external_artifact_present")
    if presence.get("admitted") is not False \
            or presence.get("network_used") is not False \
            or presence.get("download_attempted") is not False \
            or presence.get("runtime_imported") is not False \
            or presence.get("runtime_invoked") is not False \
            or presence.get("audio_read") is not False \
            or presence.get("audio_played") is not False \
            or presence.get("qualifies") is not False:
        errors.append("presence_used")
    if presence.get("task_license_file_present") is not False:
        errors.append("task_license_file_present")

    license_findings = report.get("license_findings", {})
    if license_findings.get("license_metadata_field_present") is not False \
            or license_findings.get(
                "license_file_present_at_pinned_commit") is not False \
            or license_findings.get("license_text_staged") is not False \
            or license_findings.get("checkpoint_specific_terms_present") \
            is not False \
            or license_findings.get("qualifies") is not False:
        errors.append("license_findings_overclaim")
    if license_findings.get("readme_license_badge_claims_mit") is not True:
        errors.append("license_badge_missing")
    if license_findings.get("license_path_http_status_observed") != 404:
        errors.append("license_http_status")

    observation = report.get("upstream_observation", {})
    if observation.get("head_commit") != reference.UPSTREAM_HEAD:
        errors.append("upstream_commit_mismatch")
    if observation.get("root_tree_sha1") != reference.UPSTREAM_TREE:
        errors.append("upstream_tree_mismatch")
    if observation.get("license_blob_in_tree") is not False:
        errors.append("upstream_license_blob_present")
    if observation.get("readme_sha256") != reference.UPSTREAM_README_SHA256:
        errors.append("upstream_readme_sha256")
    if observation.get("readme_git_blob_sha1") != \
            reference.UPSTREAM_README_GIT_BLOB_SHA1:
        errors.append("upstream_readme_blob")
    if observation.get("manifest_sha256") != reference.sha256_file(
            HERE / "UPSTREAM_MANIFEST.json"):
        errors.append("upstream_manifest_digest")
    metrics = observation.get("source_reported_metrics", {})
    if metrics.get("qualifies") is not False:
        errors.append("source_metrics_qualify")
    if observation.get("declared_runtime", {}).get("cpu_path_verified") \
            is not False:
        errors.append("cpu_path_overclaim")

    ledger = report.get("checkpoint_ledger", {})
    if ledger.get("checkpoint_count") != 18:
        errors.append("checkpoint_count")
    if ledger.get("checkpoint_bytes") != 261837694:
        errors.append("checkpoint_bytes")
    if ledger.get("family_counts") != {"E6": 6, "E8": 7, "experiments": 5}:
        errors.append("checkpoint_family_counts")
    if ledger.get("checkpoints_with_published_sha256") != 0:
        errors.append("checkpoint_sha256_published")
    if ledger.get("license_blob_present") is not False:
        errors.append("checkpoint_license_blob")
    if ledger.get("qualifies") is not False:
        errors.append("checkpoint_ledger_qualifies")
    for row in ledger.get("checkpoint_rows", []):
        if row.get("present") is not False \
                or row.get("published_sha256") is not None \
                or row.get("licensed") is not False \
                or row.get("admitted") is not False \
                or row.get("qualifies") is not False:
            errors.append("checkpoint_row_state:" + str(row.get("path")))

    control = report.get("manifest_control", {})
    summary = control.get("summary", {})
    if summary.get("case_count") != 30 \
            or summary.get("rejected_count") != 30 \
            or summary.get("admitted_count") != 0 \
            or summary.get("qualifying_results") != 0 \
            or summary.get("all_codes_match") is not True:
        errors.append("manifest_summary")
    if summary.get("asset_loaded") is not False \
            or summary.get("asset_executed") is not False \
            or summary.get("network_used") is not False:
        errors.append("manifest_asset_activity")
    control_row = control.get("control", {})
    if control_row.get("schema_valid") is not True \
            or control_row.get("admitted") is not False \
            or control_row.get("qualifies") is not False:
        errors.append("manifest_control_row")
    for case in control.get("cases", []):
        if case.get("status") != "rejected" \
                or case.get("observed_code") != case.get("expected_code") \
                or case.get("qualifies") is not False \
                or case.get("state_unchanged") is not True:
            errors.append("manifest_case:" + str(case.get("id")))

    frame = report.get("frame_control", {})
    frame_summary = frame.get("summary", {})
    if frame_summary.get("case_count") != 13 \
            or frame_summary.get("accepted_count") != 2 \
            or frame_summary.get("rejected_count") != 11 \
            or frame_summary.get("all_codes_match") is not True:
        errors.append("frame_summary")
    if frame_summary.get("audio_read") is not False \
            or frame_summary.get("runtime_invoked") is not False:
        errors.append("frame_activity")

    geometry = report.get("geometry_control", {})
    arithmetic = geometry.get("arithmetic", {})
    if arithmetic.get("e6_lookahead_samples") != 192 \
            or arithmetic.get("e8_lookahead_samples") != 768 \
            or arithmetic.get("demo_chunk_mod_frame_samples") != 96 \
            or arithmetic.get("e6_lookahead_mod_frame_samples") != 32 \
            or arithmetic.get("e8_lookahead_mod_frame_samples") != 128:
        errors.append("geometry_arithmetic")
    if geometry.get("checks", {}).get("v0_frame_aligned_chunk") is not False \
            or geometry.get("checks", {}).get("lookahead_measured") \
            is not False:
        errors.append("geometry_overclaim")

    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}":
            errors.append("gate_id:" + str(index))
        if gate.get("status") != "blocked":
            errors.append("gate_not_blocked:" + str(gate.get("id")))
        if gate.get("qualifies") is not False:
            errors.append("gate_qualifies:" + str(gate.get("id")))
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
                or row.get("sha256") is not None:
            errors.append("artifact_state:" + str(row.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6:
        errors.append("blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    for blocker in blockers:
        if blocker.get("status") != "open":
            errors.append("blocker_not_open:" + str(blocker.get("id")))
        if blocker.get("qualifies") is not False:
            errors.append("blocker_qualifies:" + str(blocker.get("id")))
        if blocker.get("artifact_id") not in artifact_ids:
            errors.append("blocker_artifact:" + str(blocker.get("id")))
        if not blocker.get("required_action"):
            errors.append("blocker_action_missing:" + str(blocker.get("id")))

    rows = report.get("enhancement_profile_requirements", [])
    if len(rows) != 9:
        errors.append("enhancement_row_count")
    for row in rows:
        if row.get("status") != "blocked" \
                or row.get("qualifies") is not False:
            errors.append("enhancement_row_not_blocked:" + str(row.get("id")))
    outcomes = report.get("enhancement_outcomes", [])
    if len(outcomes) != 9:
        errors.append("enhancement_outcome_count")
    for row in outcomes:
        if row.get("status") != "blocked" \
                or row.get("value") is not None \
                or row.get("qualifies") is not False:
            errors.append("enhancement_outcome_not_blocked:" +
                          str(row.get("id")))

    required = report.get("required_results", {})
    for key, value in required.items():
        if key == "no_result_qualifies":
            if value is not True:
                errors.append("required_results_no_result_qualifies")
        elif value is not False:
            errors.append("required_results_present:" + key)

    identity = report.get("linked_row_identity", {})
    if identity.get("projection") != reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW):
        errors.append("linked_projection_mismatch")
    if identity.get("sha256") != reference.object_digest(
            identity.get("projection", {})):
        errors.append("linked_projection_digest")
    if identity.get("gating") != "stable_identity_only":
        errors.append("linked_gating")
    if identity.get("board_file_pinned") is not False:
        errors.append("board_file_pinned")
    if identity.get("board_status_gates_anything") is not False:
        errors.append("board_status_gates")

    expected_source = {
        path: {"sha256": digest, "actual": digest, "verified": True}
        for path, digest in reference.SOURCE_PINS.items()}
    expected_boundary = {
        path: {"sha256": digest, "actual": digest, "verified": True}
        for path, digest in reference.BOUNDARY_PINS.items()}
    expected_sibling = {
        path: {"sha256": digest, "actual": digest, "verified": True}
        for path, digest in reference.SIBLING_PINS.items()}
    if report.get("source_pins") != expected_source:
        errors.append("report_source_pins_mismatch")
    if report.get("boundary_pins") != expected_boundary:
        errors.append("report_boundary_pins_mismatch")
    if report.get("sibling_pins") != expected_sibling:
        errors.append("report_sibling_pins_mismatch")

    payload = REPORT.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if SIDECAR.read_text(encoding="ascii") != f"{digest}  report.json\n":
        errors.append("report_sidecar_mismatch")
    if payload != reference.canonical_bytes(report):
        errors.append("report_not_canonical")
    try:
        reference._no_floats(report)
    except ValueError as error:
        errors.append("report_float:" + str(error))

    try:
        reference.verify_readme_digests(
            (HERE / "README.md").read_text(encoding="utf-8"))
    except ValueError as error:
        errors.append("readme_digest_table_failed:" + str(error))
    if (HERE / "SOURCES.sha256").is_file():
        try:
            reference.verify_sources_manifest(PINS.read_bytes())
            if PINS.read_bytes() != reference.sources_bytes():
                errors.append("sources_manifest_mismatch")
        except ValueError as error:
            errors.append("sources_rebuild:" + str(error))
    else:
        errors.append("sources_manifest_missing")
    return report


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
    text = ((HERE / "README.md").read_text(encoding="utf-8")
            if (HERE / "README.md").is_file() else "")
    if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
        errors.append("missing_markdown_spdx:README.md")
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
                         "readiness.json"}:
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
        if path.endswith("/__pycache__") or "__pycache__/" in path:
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
    allowed = set(reference.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-CLEANUMAMBA-COLD"
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
    for relative in sorted(reference.SIBLING_PINS):
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
    env.pop("AUDIOML_ROOT", None)
    with tempfile.TemporaryDirectory(prefix="sdk-cleanumamba-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run(
                [sys.executable, "run.py", "all"], cwd=target,
                capture_output=True, text=True, env=env)
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
        print(f"FAIL pins={pins} checks_ok={bool(report)} "
              f"cold_starts={len(digests)} report_sha256={digest} "
              f"changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(report['gates'])} "
          f"blockers={len(report['exact_blockers'])} "
          f"artifacts={len(report['required_artifacts'])} "
          f"manifest_cases={len(report['manifest_control']['cases'])} "
          f"checkpoints={report['checkpoint_ledger']['checkpoint_count']} "
          f"cold_starts=3/3 byte_identical=true profile=Enhancement "
          f"status={report['status']} decision=DEFER report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
