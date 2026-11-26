# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the CCF AATC unified restoration DEFER package.

Checks the Evidence-profile phrases, exact source/boundary/sibling pins, the
absent registration/dataset/pairing/baseline state, canonical report bytes and
digest, eight blocked gates, six open blockers, eight Evidence rows, all
controls, licensing/REUSE boundaries, task-local git scope and three fresh
byte-identical regenerations. It writes only to a temporary directory.
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
            if line.startswith("| Evidence |")]
    if len(rows) != 1:
        errors.append("evidence_profile_row_not_unique")
        return
    for phrase in reference.PROFILE_PHRASES:
        if phrase not in rows[0]:
            errors.append("profile_phrase_missing:" + phrase)
    if reference.PROFILE_LABEL != "Evidence":
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
        reference.validate_contract(contract)
    except ValueError as error:
        errors.append("contract_validation:" + str(error))
        return {}
    if contract.get("decision") != "DEFER" \
            or contract.get("status") != "incomplete" \
            or contract.get("qualification_status") != "not_qualified" \
            or contract.get("proposal_only") is not True:
        errors.append("contract_disposition")
    if contract.get("board_file_pinned") is not False:
        errors.append("contract_board_pinned")
    if CONTRACT.read_bytes() != reference.canonical_bytes(contract):
        errors.append("contract_not_canonical")
    return contract


def _qualifies_keys(value, errors: list[str], path: str = "") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            child = path + "/" + key
            if key.endswith("qualifies") and key != "no_result_qualifies" \
                    and item is not False:
                errors.append("qualifying_result_present:" + child)
            _qualifies_keys(item, errors, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _qualifies_keys(item, errors, f"{path}[{index}]")


def check_report(errors: list[str], contract: dict) -> dict:
    if not REPORT.is_file() or not SIDECAR.is_file():
        errors.append("committed_artifacts_missing")
        return {}
    try:
        report = reference.read_strict_json(REPORT)
    except ValueError as error:
        errors.append("strict_json_failure:" + str(error))
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
    qualification = report.get("qualification", {})
    if qualification.get("status") != "not_qualified" \
            or qualification.get("qualifying_results") != 0 \
            or qualification.get("blocked_release_gates") != 8 \
            or qualification.get("open_blockers") != 6:
        errors.append("report_qualification_copy")
    if contract:
        if report.get("contract_sha256") != reference.object_digest(contract):
            errors.append("contract_digest_mismatch")
        for key in ("disposition", "qualification", "scope", "boundary",
                    "public_v0_geometry", "non_claims", "observed_provenance",
                    "documented_challenge_envelope",
                    "synthetic_pairing_envelope", "required_artifacts",
                    "exact_blockers", "required_results", "reproduction",
                    "classical_baseline_guard", "challenge_record"):
            if report.get(key) != contract.get(key):
                errors.append("contract_copy_mismatch:" + key)
        if report.get("gates") != contract.get("release_gates"):
            errors.append("contract_copy_mismatch:release_gates")
        if report.get("evidence_profile", {}).get("rows") != \
                contract.get("evidence_profile_requirements"):
            errors.append("contract_copy_mismatch:evidence_profile")
        if report.get("evidence_outcomes", {}).get("rows") != \
                contract.get("evidence_outcomes"):
            errors.append("contract_copy_mismatch:evidence_outcomes")

    if report.get("source_presence") != reference.source_presence():
        errors.append("source_presence_mismatch")
    presence = report.get("source_presence", {})
    if presence.get("research_note_present") is not True:
        errors.append("research_note_missing")
    for key in ("registration_acceptance_present",
                "participant_agreement_present",
                "challenge_dataset_present",
                "organizer_pairing_present",
                "official_baseline_present",
                "official_scorer_present",
                "rights_cleared_cohort_present",
                "exact_challenge_artifact_present",
                "network_used", "download_attempted", "challenge_data_read",
                "audio_read", "audio_played", "qualifies"):
        if presence.get(key) is not False:
            errors.append("presence_open:" + key)
    if report.get("license_findings") != reference.license_findings():
        errors.append("license_findings_mismatch")
    findings = report.get("license_findings", {})
    for key, value in findings.items():
        if key == "registration_required_recorded":
            if value is not True:
                errors.append("license_registration_missing")
        elif value is not False:
            errors.append("license_open:" + key)

    note = report.get("observed_provenance", {}).get("research_note", {})
    if note.get("present") is not True \
            or note.get("records_registration_required") is not True \
            or note.get("records_no_single_universal_model") is not True \
            or note.get("records_no_neural_checkpoint") is not True:
        errors.append("research_note_provenance")
    guard = report.get("observed_provenance", {}).get(
        "classical_baseline_guard", {})
    if guard.get("is_unified_restorer") is not False \
            or guard.get("is_ccf_aatc_baseline") is not False \
            or guard.get("can_substitute") is not False \
            or guard.get("uses_registered_challenge_data") is not False:
        errors.append("classical_baseline_substitution")
    record = report.get("challenge_record", {})
    for key, value in record.items():
        if key == "evidence_class":
            continue
        if value is not False:
            errors.append("challenge_record_open:" + key)

    documented = report.get("documented_challenge_envelope", {})
    if documented.get("organizer_pairing_list_recorded") is not False \
            or documented.get("permitted_pair_list_recorded") is not False \
            or documented.get("dataset_identity_recorded") is not False \
            or documented.get("official_baseline_identity_recorded") is not False \
            or documented.get("semantics_verified_here") is not False \
            or documented.get("qualifies") is not False:
        errors.append("documented_envelope_overclaim")
    synthetic = report.get("synthetic_pairing_envelope", {})
    if synthetic.get("organizer_permitted") != 0 \
            or synthetic.get("multi_distortion_pairs") != 6 \
            or synthetic.get("permitted_for_qualification") is not False \
            or synthetic.get("qualifies") is not False:
        errors.append("synthetic_pairing_envelope")

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
    if len(artifacts) != 10:
        errors.append("artifact_count")
    else:
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

    rows = report.get("evidence_profile", {}).get("rows", [])
    if len(rows) != 8:
        errors.append("evidence_row_count")
    for row in rows:
        if row.get("status") != "blocked" \
                or row.get("qualifies") is not False:
            errors.append("evidence_row_not_blocked:" + str(row.get("id")))
    outcomes = report.get("evidence_outcomes", {}).get("rows", [])
    if len(outcomes) != 8:
        errors.append("evidence_outcome_count")
    for row in outcomes:
        if row.get("status") != "blocked" \
                or row.get("value") is not None \
                or row.get("qualifies") is not False:
            errors.append("evidence_outcome_not_blocked:" +
                          str(row.get("id")))

    try:
        expected = {
            "family_control": reference.family_control(),
            "degradation_control": reference.degradation_control(),
            "pair_control": reference.pair_control(),
            "aggregation_control": reference.aggregation_control(),
            "admission": reference.admission_controls(),
        }
    except ValueError as error:
        errors.append("control_rebuild:" + str(error))
    else:
        for key, value in expected.items():
            if report.get(key) != value:
                errors.append(key + "_mismatch")

    family = report.get("family_control", {}).get("summary", {})
    if family.get("case_count") != 18 \
            or family.get("accepted_count") != 4 \
            or family.get("rejected_count") != 14 \
            or family.get("all_codes_match") is not True \
            or family.get("qualifying_results") != 0:
        errors.append("family_control_summary")
    degradation = report.get("degradation_control", {}).get("summary", {})
    if degradation.get("case_count") != 14 \
            or degradation.get("accepted_count") != 7 \
            or degradation.get("rejected_count") != 7 \
            or degradation.get("all_codes_match") is not True:
        errors.append("degradation_control_summary")
    if degradation.get("clip_thresholds") != ["7/20", "11/20"] \
            or degradation.get("bwe_cutoff_fraction") != "7/32" \
            or degradation.get("codec_levels") != [256, 16] \
            or degradation.get("loss_rates") != ["1/10", "17/100"]:
        errors.append("degradation_control_arithmetic")
    pair = report.get("pair_control", {}).get("summary", {})
    if pair.get("case_count") != 10 \
            or pair.get("accepted_count") != 4 \
            or pair.get("rejected_count") != 6 \
            or pair.get("pair_count") != 6 \
            or pair.get("organizer_permitted_count") != 0 \
            or pair.get("permitted_for_qualification") is not False:
        errors.append("pair_control_summary")
    aggregation = report.get("aggregation_control", {}).get("summary", {})
    if aggregation.get("case_count") != 12 \
            or aggregation.get("accepted_count") != 2 \
            or aggregation.get("rejected_count") != 10 \
            or aggregation.get("unified_score_forbidden") is not True \
            or aggregation.get("qualifying_results") != 0:
        errors.append("aggregation_control_summary")
    admission = report.get("admission", {})
    summary = admission.get("summary", {})
    if summary.get("qualifying_results") != 0 \
            or summary.get("accepted_schema_controls") != 1:
        errors.append("admission_summary_invalid")
    if summary.get("case_count") != len(reference.mutations()) \
            or summary.get("case_count") != 37 \
            or summary.get("rejected_count") != summary.get("case_count"):
        errors.append("admission_not_all_rejected")
    if summary.get("all_codes_match") is not True:
        errors.append("admission_codes")
    for key in ("state_advanced_on_rejection", "vendor_sdk_loaded",
                "vendor_runtime_invoked", "challenge_data_read", "audio_read",
                "audio_rendered", "network_used"):
        if summary.get(key) is not False:
            errors.append("admission_" + key)
    control = admission.get("control", {})
    if control.get("schema_valid") is not True \
            or control.get("admitted") is not False \
            or control.get("qualifies") is not False:
        errors.append("admission_control")
    for case in admission.get("cases", []):
        if case.get("status") != "rejected" \
                or case.get("qualifies") is not False \
                or case.get("state_unchanged") is not True \
                or case.get("observed_code") != case.get("expected_code"):
            errors.append("admission_case:" + str(case.get("id")))

    identity = report.get("linked_row_identity", {})
    if identity.get("projection") != reference.board_row_projection(
            reference.AUDIO_ROOT / reference.BOARD_TASK_ROW):
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
    if identity.get("linked_rows") != [dict(row)
                                       for row in reference.LINKED_ROWS]:
        errors.append("linked_rows_mismatch")
    if identity.get("linked_rows_sha256") != reference.linked_rows_digest():
        errors.append("linked_rows_digest")

    required = report.get("required_results", {})
    for key, value in required.items():
        if key == "no_result_qualifies":
            if value is not True:
                errors.append("required_results_no_result_qualifies")
        elif value is not False:
            errors.append("required_results_present:" + key)

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
    _qualifies_keys(report, errors)
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
    allowed = set(reference.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/CCF-AATC-COLD"
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
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    env.pop("AUDIOML_ROOT", None)
    with tempfile.TemporaryDirectory(
            prefix="sdk-ccf-aatc-cold-") as temporary:
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
          f"admission_cases={len(report['admission']['cases'])} "
          f"cold_starts=3/3 byte_identical=true profile=Evidence "
          f"status={report['status']} decision=DEFER report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
