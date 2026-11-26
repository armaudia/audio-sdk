# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-PBSHIFT DEFER evidence package.

Checks Rate profile phrases, exact source/boundary/sibling pins, absent
runtime/artifact state, canonical report bytes and digest, eight blocked gates,
six open blockers, fail-closed gate/admission controls, licensing/REUSE
boundaries, task-local git scope, and three fresh byte-identical regenerations.
It writes only to a temporary directory.
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
SPDX_LICENSE = "SPDX-License-" + "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd

SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)


def check_profile_source(errors: list[str]) -> None:
    path = reference.AUDIO_ROOT / reference.PROFILE_SOURCE
    if not path.is_file():
        errors.append("profile_source_missing")
        return
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("| Rate |")]
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
        (reference.BOUNDARY_PINS, reference.WORKTREE, "boundary"),
        (reference.SIBLING_PINS, reference.WORKTREE, "sibling"),
    ):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append(label + "_pin_missing:" + relative)
                continue
            actual = reference.sha256_file(path)
            if actual != expected:
                errors.append(label + "_pin_mismatch:" + relative)
            checked += 1
    for pins in (reference.SOURCE_PINS, reference.BOUNDARY_PINS, reference.SIBLING_PINS):
        if reference.BOARD_TASK_ROW in pins:
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
    if CONTRACT.read_bytes() != reference.canonical_bytes(contract):
        errors.append("contract_not_canonical")
    return contract


def check_report(errors: list[str], contract: dict) -> dict:
    if not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}
    try:
        report = reference.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("strict_json_failure:" + str(error))
        return {}
    for key, value in (("schema_id", reference.REPORT_SCHEMA_ID), ("task", reference.TASK), ("component", reference.COMPONENT_ID), ("decision", "DEFER"), ("status", "incomplete"), ("qualification_status", "not_qualified")):
        if report.get(key) != value:
            errors.append("report_field:" + key)
    if report.get("proposal_only") is not True:
        errors.append("report_not_proposal_only")
    if contract:
        if report.get("contract_sha256") != reference.object_digest(contract):
            errors.append("contract_digest_mismatch")
        for key in ("disposition", "qualification", "scope", "boundary", "public_v0_geometry", "non_claims", "observed_provenance", "required_artifacts", "exact_blockers", "required_results", "reproduction"):
            if report.get(key) != contract.get(key):
                errors.append("contract_copy_mismatch:" + key)
        if report.get("gates") != contract.get("release_gates"):
            errors.append("contract_copy_mismatch:release_gates")
        if report.get("rate_profile", {}).get("rows") != contract.get("rate_profile_requirements"):
            errors.append("contract_copy_mismatch:rate_profile")
        if report.get("rate_outcomes", {}).get("rows") != contract.get("rate_outcomes"):
            errors.append("contract_copy_mismatch:rate_outcomes")
    if report.get("source_presence") != reference.source_presence():
        errors.append("source_presence_mismatch")
    presence = report.get("source_presence", {})
    if presence.get("candidate_note_present") is not True or presence.get("pbshift_runtime_present") is not False or presence.get("exact_licensed_source_weights_runtime_present") is not False:
        errors.append("presence_state")
    for key in ("admitted", "download_attempted", "network_used", "runtime_imported", "audio_read", "audio_played", "benchmark_run", "qualifies"):
        if presence.get(key) is not False:
            errors.append("presence_used:" + key)
    if report.get("license_findings") != reference.license_marker_probe():
        errors.append("license_findings_mismatch")
    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("gate_count")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}" or gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("gate_invalid:" + str(index))
        if not gate.get("reopen_condition"):
            errors.append("gate_reopen_missing:" + str(index))
    artifacts = report.get("required_artifacts", [])
    if len(artifacts) != 9:
        errors.append("artifact_count")
    for row in artifacts:
        if row.get("present") is not False or row.get("verified") is not False or row.get("licensed") is not False or row.get("admitted") is not False or row.get("blocked") is not True or row.get("sha256") is not None:
            errors.append("artifact_state:" + str(row.get("id")))
    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6:
        errors.append("blocker_count")
    artifact_ids = {row.get("id") for row in artifacts}
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False or row.get("artifact_id") not in artifact_ids or not row.get("required_action"):
            errors.append("blocker_invalid:" + str(row.get("id")))
    for row in report.get("rate_profile", {}).get("rows", []):
        if row.get("status") != "blocked" or row.get("qualifies") is not False:
            errors.append("rate_row_not_blocked:" + str(row.get("id")))
    for row in report.get("rate_outcomes", {}).get("rows", []):
        if row.get("status") != "blocked" or row.get("value") is not None or row.get("qualifies") is not False:
            errors.append("rate_outcome_not_blocked:" + str(row.get("id")))
    if report.get("gate_control") != reference.gate_control():
        errors.append("gate_control_mismatch")
    if report.get("admission") != reference.admission_controls():
        errors.append("admission_mismatch")
    summary = report.get("admission", {}).get("summary", {})
    if summary.get("qualifying_results") != 0 or summary.get("accepted_schema_controls") != 1 or summary.get("all_rejected") is not True or summary.get("all_codes_match") is not True:
        errors.append("admission_summary_invalid")
    for case in report.get("admission", {}).get("cases", []):
        if case.get("status") != "rejected" or case.get("qualifies") is not False or case.get("state_unchanged") is not True or case.get("code") != case.get("expected_code"):
            errors.append("admission_case:" + str(case.get("id")))
    identity = report.get("linked_row_identity", {})
    if identity.get("projection") != reference.board_row_projection(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW):
        errors.append("linked_projection_mismatch")
    if identity.get("sha256") != reference.board_row_digest(identity.get("projection", {})):
        errors.append("linked_projection_digest")
    if identity.get("gating") != "stable_identity_only" or identity.get("board_file_pinned") is not False or identity.get("board_status_gates_anything") is not False:
        errors.append("linked_gating")
    if identity.get("linked_rows") != [dict(r) for r in reference.LINKED_ROWS] or identity.get("linked_rows_sha256") != reference.linked_rows_digest():
        errors.append("linked_rows_mismatch")
    required = report.get("required_results", {})
    for key, value in required.items():
        if key == "no_result_qualifies":
            if value is not True:
                errors.append("required_results_no_result_qualifies")
        elif value is not False:
            errors.append("required_results_present:" + key)
    expected_source = {p: {"sha256": d, "actual": d, "verified": True} for p, d in reference.SOURCE_PINS.items()}
    expected_boundary = {p: {"sha256": d, "actual": d, "verified": True} for p, d in reference.BOUNDARY_PINS.items()}
    expected_sibling = {p: {"sha256": d, "actual": d, "verified": True} for p, d in reference.SIBLING_PINS.items()}
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
    if not PINS.is_file():
        errors.append("sources_manifest_missing")
    else:
        try:
            reference.verify_sources_manifest(PINS.read_bytes())
            expected_pins = run.sources_bytes()
        except ValueError as error:
            errors.append("sources_rebuild:" + str(error))
        else:
            if PINS.read_bytes() != expected_pins:
                errors.append("sources_manifest_mismatch")
    return report


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        text = (HERE / name).read_text(encoding="utf-8") if (HERE / name).is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    text = (HERE / "README.md").read_text(encoding="utf-8") if (HERE / "README.md").is_file() else ""
    if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
        errors.append("missing_markdown_spdx:README.md")
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    reuse_token = 'SPDX-License-' + 'Identifier = "Apache-2.0"'
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
        if path.is_file() and path.name in {"LICENSE", "LICENSE.txt", "COPYING", "NOTICE"}:
            errors.append("vendored_license_file:" + path.name)


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"], capture_output=True, text=True)
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
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *arguments], capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "") + "_failed:" + diff.stdout.strip())
    allowed = set(reference.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-PBSHIFT"
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
    for probe in reference.PRESENCE_PROBES:
        source = reference.AUDIO_ROOT / probe
        if source.exists():
            link = scratch / "audioml" / probe
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(source)
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
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    env.pop("AUDIOML_ROOT", None)
    with tempfile.TemporaryDirectory(prefix="sdk-pbshift-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"], cwd=target, capture_output=True, text=True, env=env)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" + process.stderr.strip())
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
    contract = check_contract(errors)
    report = check_report(errors, contract)
    check_licensing(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = hashlib.sha256(REPORT.read_bytes()).hexdigest() if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} checks_ok={bool(report)} cold_starts={len(digests)} report_sha256={digest} changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(report['gates'])} blockers={len(report['exact_blockers'])} artifacts={len(report['required_artifacts'])} admission_cases={len(report['admission']['cases'])} cold_starts=3/3 byte_identical=true profile=Rate status={report['status']} decision=DEFER report_sha256={digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
