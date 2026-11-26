# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the LibriSpeech / Common Voice intake gate.

It checks strict JSON, canonical bytes, exact pins, DEFER/not-qualified
semantics, dataset-scoped absence and rights, overlap separation, Evidence
profile mapping, stable linked-row identity (never the full mutable board),
licensing, prohibited artifacts, task-local git scope and three cold-start
byte-identical regenerations. It never writes package evidence.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_PREFIX = reference.TASK_PREFIX
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
TASK_ID = reference.TASK
COMPONENT = reference.COMPONENT
BASE_COMMIT = reference.BASE_COMMIT
GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]
EXPECTED_LINK = dict(reference.EXPECTED_LINK)
ARTIFACT_FILES = tuple(sorted(run.CONTRACT_ARTIFACTS))
ALLOWED_FILES = set(run.MANIFEST_FILES) | {"contract.json", "SOURCES.sha256"}
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".tsv", ".csv", ".onnx",
    ".pt", ".pth", ".ckpt", ".safetensors", ".bin", ".so", ".dylib", ".a",
    ".o", ".zip", ".tar", ".gz", ".whl", ".npy", ".pyc", ".wasm", ".elf",
    ".hex",
}


class VerificationError(AssertionError):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def strict_load(path: Path) -> Any:
    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise VerificationError("duplicate JSON key in " + path.name)
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise VerificationError("nonfinite JSON constant in " + path.name +
                                ": " + token)

    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text, object_pairs_hook=pairs,
                          parse_constant=constant)
    except json.JSONDecodeError as error:
        raise VerificationError("invalid JSON in " + path.name + ": " +
                                str(error))


def canonical_bytes(value: Any) -> bytes:
    return reference.canonical_bytes(value)


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def check(condition: bool, message: str, problems: List[str]) -> None:
    if not condition:
        problems.append(message)


def check_contract(contract: Dict[str, Any], report: Dict[str, Any],
                   problems: List[str]) -> None:
    check(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID,
          "contract schema mismatch", problems)
    check(contract.get("contract_version") == "0.1",
          "contract version mismatch", problems)
    for key, value in (
            ("task", TASK_ID), ("component", COMPONENT),
            ("title", reference.TITLE), ("repository", reference.REPOSITORY),
            ("mode", reference.MODE), ("branch", reference.BRANCH),
            ("base_commit", BASE_COMMIT),
            ("verification_profile", "evidence")):
        check(contract.get(key) == value, "contract mismatch: " + key,
              problems)
    check(contract.get("decision") == "DEFER",
          "contract decision is not DEFER", problems)
    check(contract.get("status") == "proposal_only_incomplete",
          "contract status is not proposal_only_incomplete", problems)
    check(contract.get("incomplete") is True,
          "contract is not marked incomplete", problems)
    check(contract.get("proposal_only") is True,
          "contract is not marked proposal only", problems)
    check(contract.get("evidence_status") == "incomplete",
          "contract evidence status mismatch", problems)
    check(contract.get("qualification_status") == "not_qualified",
          "contract qualification_status mismatch", problems)
    check(contract.get("defer_before") == reference.DEFER_BEFORE,
          "contract defer_before mismatch", problems)
    check(contract.get("comparison_status") == reference.COMPARISON_STATUS,
          "contract comparison status mismatch", problems)
    qualification = contract.get("qualification", {})
    check(qualification.get("status") == "not_qualified",
          "contract qualification is not not_qualified", problems)
    check(qualification.get("readiness") == "incomplete",
          "contract readiness is not incomplete", problems)
    check(qualification.get("decision") == "DEFER",
          "contract qualification decision mismatch", problems)
    check(qualification.get("candidate_qualified") is False and
          qualification.get("dataset_qualified") is False,
          "contract claims a qualified dataset", problems)
    check(qualification.get("rights_approved") is False,
          "contract claims rights approval", problems)
    check(qualification.get("representative_valid_result") is False,
          "contract claims a representative valid result", problems)
    check(qualification.get("all_required_results_present") is False,
          "contract claims all required results are present", problems)

    boundary = contract.get("boundary", {})
    check(boundary == report.get("boundary"),
          "contract and report boundary differ", problems)
    check(boundary.get("installed_v0_behavior_change") is False,
          "installed v0 boundary changed", problems)
    check(boundary.get("public_api_abi_change") is False,
          "public ABI boundary changed", problems)
    check(boundary.get("provider_registration") is False,
          "provider registered", problems)
    check(boundary.get("descriptor_registry_change") is False,
          "descriptor registry changed", problems)
    check(boundary.get("enabled_by_default") is False,
          "provider enabled by default", problems)
    check(boundary.get("default_selected") is False,
          "a default was selected", problems)
    check(boundary.get("shared_build_or_ci_change") is False,
          "shared build or CI changed", problems)
    check(boundary.get("board_or_handoff_changed") is False,
          "board or handoff changed", problems)
    check(boundary.get("real_corpus_read") is False,
          "real corpus read claimed", problems)
    check(boundary.get("audio_loaded") is False,
          "audio loaded claimed", problems)
    check(boundary.get("network_used") is False,
          "network use claimed", problems)
    check(boundary.get("benchmark_claim") is False,
          "benchmark claim present", problems)
    check(boundary.get("release_claim") is False,
          "release claim present", problems)
    check(boundary.get("format") == {
        "sample_rate_hz": 16000, "channels": 1,
        "frame_samples": 160, "sample_format": "float32",
    }, "contract v0 format mismatch", problems)

    blocker = contract.get("blocker", {})
    check(blocker.get("status") == reference.COMPARISON_STATUS,
          "contract blocker status mismatch", problems)
    check(blocker.get("no_fabricated_identity") is True,
          "contract permits fabricated identity", problems)
    check(blocker.get("no_upstream_parity_claim") is True,
          "contract claims upstream parity", problems)
    for dataset in ("librispeech", "common_voice"):
        block = blocker.get(dataset, {})
        check(block.get("status") == "absent",
              dataset + " is not recorded as absent", problems)
        check(block.get("archive_present") is False and
              block.get("prepared_manifest_present") is False,
              dataset + " claims local data or manifest", problems)
        check(block.get("rights_approved") is False,
              dataset + " claims rights approval", problems)
        for key in ("archive_sha256", "manifest_sha256", "item_count",
                    "duration_seconds"):
            check(block.get(key) is None,
                  dataset + " has a fabricated identity: " + key, problems)
    check(blocker["librispeech"].get("archive_md5") is None,
          "contract fabricates a local LibriSpeech MD5", problems)
    rights = str(blocker.get("rights_requirement", "")).lower()
    for word in ("license", "retention", "redistribution", "derived",
                 "privacy", "re-hosting"):
        check(word in rights, "rights requirement omits: " + word, problems)
    not_attempted = " ".join(blocker.get("not_attempted", [])).lower()
    for phrase in ("download", "manifest", "license", "speaker"):
        check(phrase in not_attempted,
              "not-attempted list omits: " + phrase, problems)
    check(bool(blocker.get("reopen")), "blocker has no reopen condition",
          problems)

    required = contract.get("required_artifacts", [])
    check(required == report.get("required_artifacts"),
          "contract and report required artifacts differ", problems)
    check(isinstance(required, list) and len(required) == 8,
          "contract does not carry eight required artifacts", problems)
    if isinstance(required, list):
        check([row.get("id") for row in required] ==
              ["A" + str(number) for number in range(1, 9)],
              "required artifact ids mismatch", problems)
        for row in required:
            check(row.get("status") == "absent",
                  "required artifact is not absent: " + str(row.get("id")),
                  problems)
            check(row.get("sha256") is None and row.get("byte_count") is None,
                  "required artifact has a fabricated identity: " +
                  str(row.get("id")), problems)
            check(row.get("rights_reviewed") is False,
                  "required artifact rights are claimed: " +
                  str(row.get("id")), problems)
    check(contract.get("missing_artifacts") ==
          report.get("missing_artifacts"),
          "missing artifact list mismatch", problems)

    gates = contract.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8,
          "contract does not carry eight release gates", problems)
    if isinstance(gates, list):
        check([gate.get("id") for gate in gates] == GATE_IDS,
              "contract gate ids mismatch", problems)
        check(all(gate.get("status") == "blocked" for gate in gates),
              "a contract release gate is not blocked", problems)
    check(contract.get("remaining_gates") == GATE_IDS,
          "contract remaining gates mismatch", problems)
    for key in ("datasets", "overlap_matrix", "evidence_separation", "rights",
                "external_boundary", "acceptance_profile", "presence_probe",
                "admission_controls", "required_results"):
        check(contract.get(key) == report.get(key),
              "contract and report differ: " + key, problems)
    check(contract.get("profile") == report.get("profile"),
          "contract and report profile differ", problems)

    canonical = contract.get("canonical_report", {})
    report_payload = REPORT_PATH.read_bytes()
    sidecar_payload = SIDECAR_PATH.read_bytes()
    check(canonical.get("file_sha256") == sha256_bytes(report_payload),
          "contract report file digest mismatch", problems)
    check(canonical.get("sidecar_sha256") == sha256_bytes(sidecar_payload),
          "contract sidecar digest mismatch", problems)
    check(canonical.get("canonical_digest") ==
          sha256_bytes(canonical_bytes(report)),
          "contract canonical report digest mismatch", problems)


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") == reference.SCHEMA_ID,
          "report schema mismatch", problems)
    for key, value in (
            ("task", TASK_ID), ("component", COMPONENT),
            ("title", reference.TITLE), ("repository", reference.REPOSITORY),
            ("mode", reference.MODE), ("branch", reference.BRANCH),
            ("base_commit", BASE_COMMIT),
            ("verification_profile", "evidence")):
        check(report.get(key) == value, "report mismatch: " + key, problems)
    check(report.get("decision") == "DEFER", "report decision is not DEFER",
          problems)
    check(report.get("status") == "proposal_only_incomplete",
          "report status is not proposal_only_incomplete", problems)
    check(report.get("incomplete") is True,
          "report is not marked incomplete", problems)
    check(report.get("proposal_only") is True,
          "report is not marked proposal only", problems)
    check(report.get("evidence_status") == "incomplete",
          "report evidence status mismatch", problems)
    check(report.get("qualification_status") == "not_qualified",
          "report qualification_status mismatch", problems)
    qualification = report.get("qualification", {})
    check(qualification.get("status") == "not_qualified" and
          qualification.get("dataset_qualified") is False and
          qualification.get("candidate_qualified") is False and
          qualification.get("rights_approved") is False and
          qualification.get("readiness") == "incomplete" and
          qualification.get("decision") == "DEFER" and
          qualification.get("proposal_only") is True,
          "report qualification is not incomplete/not_qualified", problems)
    check(report.get("profile", {}).get("name") == "evidence",
          "report profile is not evidence", problems)

    datasets = report.get("datasets", {})
    check(set(datasets) == set(reference.CORPORA),
          "report dataset set mismatch", problems)
    libri = datasets.get(reference.LIBRISPEECH_CORPUS_ID, {})
    common = datasets.get(reference.COMMON_VOICE_CORPUS_ID, {})
    for name, block in ((reference.LIBRISPEECH_CORPUS_ID, libri),
                        (reference.COMMON_VOICE_CORPUS_ID, common)):
        check(block.get("probe_status", "").startswith("blocked_"),
              name + " probe is not blocked", problems)
        check(block.get("archive_present") is False and
              block.get("prepared_manifest_present") is False,
              name + " claims data or a manifest", problems)
        local = block.get("local", {})
        for key in ("archive_sha256", "archive_byte_count", "manifest_sha256",
                    "item_count", "duration_seconds", "rights_record"):
            check(local.get(key) is None,
                  name + " has a fabricated local identity: " + key,
                  problems)
        check(local.get("speaker_split_verified") is False,
              name + " claims a verified speaker split", problems)
        rights = block.get("rights", {})
        check(rights.get("status") == "not_cleared",
              name + " rights are not blocked", problems)
        check(rights.get("license_text_present") is False,
              name + " claims a license text", problems)
        check(rights.get("license_text_sha256") is None,
              name + " has a fabricated license digest", problems)
    check(libri.get("reported", {}).get("reported_archive_md5") ==
          reference.LIBRISPEECH_REPORTED_MD5,
          "LibriSpeech reported MD5 changed", problems)
    check(common.get("reported", {}).get("dataset_id") ==
          "cmu5nqn1h00vwmi07b4dbk085",
          "Common Voice dataset id changed", problems)
    check(common.get("reported", {}).get("release") ==
          "sps-corpus-5.0-2026-09-11",
          "Common Voice release changed", problems)
    check(common.get("reported", {}).get("reported_clips") == 5898 and
          common.get("reported", {}).get("reported_speakers") == 642,
          "Common Voice reported counts changed", problems)
    check(common.get("reported", {}).get("native_sample_rate_hz") is None,
          "Common Voice native rate was invented", problems)
    check(libri.get("reported", {}).get("reported_license") == "CC BY 4.0",
          "LibriSpeech license label changed", problems)
    check(common.get("reported", {}).get("reported_license") == "CC0-1.0",
          "Common Voice license label changed", problems)
    check(common.get("reported", {}).get("source") !=
          libri.get("reported", {}).get("source"),
          "dataset sources are pooled", problems)

    blocker = report.get("blocker", {})
    check(blocker.get("status") == reference.COMPARISON_STATUS,
          "report blocker status mismatch", problems)
    check(blocker.get("no_fabricated_identity") is True,
          "report permits fabricated identity", problems)
    check(blocker.get("workspace_search") and blocker.get("reopen"),
          "report blocker lacks search or reopen text", problems)

    rights = report.get("rights", {})
    check(rights.get("status") == "blocked_rights_unrecorded",
          "report rights are not blocked", problems)
    check(rights.get("use_approved") is False and
          rights.get("retention_approved") is False and
          rights.get("listening_approved") is False and
          rights.get("redistribution_approved") is False,
          "report rights overclaim approval", problems)
    check(rights.get("librispeech", {}).get("reported_license") ==
          "CC BY 4.0" and
          rights.get("common_voice", {}).get("reported_license") ==
          "CC0-1.0",
          "report dataset licenses are pooled", problems)
    check(rights.get("common_voice", {}).get("download_terms_reviewed")
          is False,
          "Common Voice download terms are claimed reviewed", problems)

    matrix = report.get("overlap_matrix", [])
    check(isinstance(matrix, list) and len(matrix) == 6,
          "overlap matrix size mismatch", problems)
    if isinstance(matrix, list):
        check(all(row.get("exact_audit_present") is False for row in matrix),
              "an overlap audit is claimed present", problems)
        pairs = {(row.get("dataset"), row.get("model")) for row in matrix}
        for dataset in (reference.LIBRISPEECH_CORPUS_ID,
                        reference.COMMON_VOICE_CORPUS_ID):
            for model in reference.MODEL_IDS:
                check((dataset, model) in pairs,
                      "overlap pair missing: " + dataset + "/" + model,
                      problems)
        dpdfnet = [row for row in matrix
                   if row.get("dataset") == reference.LIBRISPEECH_CORPUS_ID
                   and row.get("model") == "dpdfnet"]
        check(bool(dpdfnet) and "LibriVox" in dpdfnet[0].get("reason", "") and
              "MLS" in dpdfnet[0].get("reason", ""),
              "DPDFNet / LibriVox / MLS overlap risk is lost", problems)

    separation = report.get("evidence_separation", {})
    check(separation.get("pooling") is False,
          "evidence kinds are pooled", problems)
    check(separation.get("human", {}).get("listening") is False,
          "human listening is claimed", problems)
    check(separation.get("source_reported", {}).get("status") ==
          "retained_not_reproduced",
          "source-reported evidence status mismatch", problems)

    profile = report.get("acceptance_profile", {})
    check(profile.get("profile") == "evidence",
          "acceptance profile name mismatch", problems)
    items = profile.get("required_items", {})
    check(items.get("representative_valid_result_validated", {}).get(
        "status") == "blocked",
        "representative valid result is not blocked", problems)
    check(items.get("invalid_or_missing_case_validated", {}).get(
        "status") == "recorded",
        "invalid/missing control is not recorded", problems)
    check(items.get("separation_of_evidence_kinds", {}).get("status") ==
          "declared_only",
          "evidence separation is overclaimed", problems)

    adverse = report.get("adverse", {})
    check(adverse.get("invalid_declarations", {}).get("all_rejected") is True
          and adverse.get("invalid_declarations", {}).get(
              "accepted_count") == 0,
          "invalid declarations were accepted", problems)
    check(adverse.get("invalid_json_numeric_fields", {}).get(
        "all_rejected") is True,
        "invalid JSON was accepted", problems)
    check(adverse.get("missing_result", {}).get("metrics") is None and
          adverse.get("missing_result", {}).get("qualifies") is False,
          "missing result carries metrics or qualifies", problems)

    controls = report.get("admission_controls", {})
    check(controls.get("admission_policy", {}).get(
        "admitting_branch_exists") is False,
        "an admitting branch exists", problems)
    check(controls.get("admission_policy", {}).get("always_defer") is True,
          "admission is not always DEFER", problems)
    check(controls.get("recorded_declaration_live", {}).get(
        "decision") == "DEFER",
        "live admission is not DEFER", problems)
    check(controls.get("representative_valid_result", {}).get(
        "present") is False,
        "representative valid result is present", problems)

    control = report.get("control_probe", {})
    check(control.get("byte_identical") is True,
          "structural control is not byte identical", problems)
    check(control.get("datasets_separate") is True,
          "structural control pools datasets", problems)
    check(control.get("candidate_processing") is False and
          control.get("real_corpus_read") is False,
          "structural control is presented as corpus evidence", problems)

    checks = report.get("local_harness_checks", {})
    check(all(value is True for value in checks.values()),
          "a local harness check is not true", problems)
    check(len(checks) >= 15, "local harness check set is too small", problems)
    gates = report.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8,
          "report does not carry eight release gates", problems)
    if isinstance(gates, list):
        check([gate.get("id") for gate in gates] == GATE_IDS,
              "report gate ids mismatch", problems)
        check(all(gate.get("status") == "blocked" for gate in gates),
              "a report release gate is not blocked", problems)
        check(all(gate.get("reason") for gate in gates),
              "a release gate lacks a reason", problems)
        check(all(gate.get("reopen") for gate in gates),
              "a release gate lacks a reopen condition", problems)
    check(report.get("remaining_gates") == GATE_IDS,
          "report remaining gates mismatch", problems)
    check(report.get("no_missing_result_qualifies") is True and
          report.get("no_result_qualifies") is True,
          "missing-result guard is not enabled", problems)
    check(report.get("board_full_file_hashed") is False,
          "report hashes the full mutable board", problems)
    external = report.get("external_boundary", {})
    check(external.get("documented") is True,
          "external boundary is not documented", problems)
    for key in ("librispeech_source_present", "librispeech_manifest_present",
                "common_voice_source_present",
                "common_voice_manifest_present", "license_text_present",
                "download_terms_accepted", "rights_approved", "scorer_present",
                "cohort_present", "representative_result_present",
                "adapter_implemented", "adapter_default_registration",
                "automatic_discovery"):
        check(external.get(key) is False,
              "external boundary claim is not false: " + key, problems)
    check(external.get("fallback") == "none",
          "an external fallback is claimed", problems)
    check(bool(report.get("source_evidence_statements")),
          "source evidence statements are missing", problems)
    check(bool(report.get("non_claims")) and bool(report.get("invariants")),
          "non-claims or invariants are missing", problems)


def check_pins(contract: Dict[str, Any], report: Dict[str, Any],
               problems: List[str]) -> int:
    pins = contract.get("artifact_pins", {})
    check(set(pins) == set(ARTIFACT_FILES),
          "contract artifact pin set mismatch", problems)
    for name, digest in pins.items():
        path = HERE / name
        check(path.is_file(), "missing artifact: " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest,
                  "artifact pin mismatch: " + name, problems)
    check(pins.get("report.json") == sha256_file(REPORT_PATH),
          "report.json pin does not match bytes", problems)
    sidecar = SIDECAR_PATH.read_text(encoding="ascii")
    check(sidecar == (sha256_file(REPORT_PATH) + "  report.json\n"),
          "report SHA-256 sidecar mismatch", problems)
    for path, digest in report.get("source_pins", {}).items():
        target = WORKSPACE / path
        check(target.is_file(), "missing source pin target: " + path,
              problems)
        if target.is_file():
            check(sha256_file(target) == digest,
                  "source pin mismatch: " + path, problems)
        check(path != "audio-benchmark-platform/plan/swarm/TASKS.json",
              "mutable TASKS.json is directly pinned", problems)
    for path, digest in report.get("boundary_pins", {}).items():
        target = SDK_ROOT / path
        check(target.is_file(), "missing boundary pin target: " + path,
              problems)
        if target.is_file():
            check(sha256_file(target) == digest,
                  "boundary pin mismatch: " + path, problems)
    sources = SOURCES_PATH.read_text(encoding="utf-8")
    check("audio-benchmark-platform/plan/swarm/TASKS.json" not in sources,
          "mutable TASKS.json appears in SOURCES.sha256", problems)
    expected_sources = run.build_sources_bytes(
        REPORT_PATH.read_bytes(), SIDECAR_PATH.read_bytes()).decode("utf-8")
    check(sources == expected_sources,
          "SOURCES.sha256 is not deterministically generated", problems)
    for path, digest in report.get("source_pins", {}).items():
        check((digest + "  source:" + path) in sources,
              "source pin missing from SOURCES.sha256: " + path, problems)
    for path, digest in report.get("boundary_pins", {}).items():
        check((digest + "  " + path) in sources,
              "boundary pin missing from SOURCES.sha256: " + path, problems)
    for name in run.MANIFEST_FILES:
        if name == "report.json":
            digest = sha256_file(REPORT_PATH)
        elif name == "report.json.sha256":
            digest = sha256_file(SIDECAR_PATH)
        else:
            path = HERE / name
            check(path.is_file(), "manifest artifact missing: " + name,
                  problems)
            if not path.is_file():
                continue
            digest = sha256_file(path)
        check((digest + "  " + TASK_PREFIX + name) in sources,
              "manifest pin missing from SOURCES.sha256: " + name, problems)
    return (len(pins) + len(report.get("source_pins", {})) +
            len(report.get("boundary_pins", {})))


def check_board(contract: Dict[str, Any], report: Dict[str, Any],
                problems: List[str]) -> None:
    board = strict_load(BOARD_PATH)
    check(isinstance(board, dict) and isinstance(board.get("tasks"), list),
          "TASKS.json shape is invalid", problems)
    rows = [row for row in board.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    check(len(rows) == 1, "linked task row is missing or duplicated", problems)
    if len(rows) != 1:
        return
    stable = {
        "task_id": rows[0].get("id"),
        "title": rows[0].get("title"),
        "mode": rows[0].get("mode"),
        "repository": rows[0].get("repository"),
        "component": rows[0].get("component"),
    }
    check(stable == EXPECTED_LINK, "stable linked-row identity changed",
          problems)
    expected = sha256_bytes(canonical_bytes([stable]))
    check(report.get("board_links") == [stable],
          "report board projection mismatch", problems)
    check(report.get("board_link_fields") == list(reference.LINK_FIELDS),
          "board link fields mismatch", problems)
    check(report.get("board_link_projection_sha256") == expected,
          "board projection digest mismatch", problems)
    check(contract.get("board_links") == [stable] and
          contract.get("board_link_projection_sha256") == expected,
          "contract board projection mismatch", problems)
    check(contract.get("board_full_file_hashed") is False,
          "contract hashes the full mutable board", problems)
    for mutable in ("status", "owner", "review", "handoff", "claim",
                    "history", "blocked_reason", "dispatch_priority",
                    "depends_on", "write_scope"):
        check(mutable in report.get("board_mutable_fields_excluded", []),
              "mutable board field not excluded: " + mutable, problems)
    full_digest = sha256_file(BOARD_PATH)
    blob = (REPORT_PATH.read_text(encoding="utf-8") +
            CONTRACT_PATH.read_text(encoding="utf-8") +
            SOURCES_PATH.read_text(encoding="utf-8"))
    check(full_digest not in blob,
          "full mutable TASKS.json digest appears in a canonical artifact",
          problems)


def check_licensing(problems: List[str]) -> None:
    for name in SIDECAR_FILES:
        path = HERE / name
        check(path.is_file(), "missing SPDX sidecar: " + name, problems)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        check(SPDX_COPYRIGHT in text,
              "sidecar lacks copyright line: " + name, problems)
        check(SPDX_NEEDLE in text,
              "sidecar lacks Apache-2.0 line: " + name, problems)
    for name in ("README.md", "reference.py", "run.py",
                 "test_reference.py", "verify.py"):
        path = HERE / name
        check(path.is_file(), "missing package file: " + name, problems)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            check(SPDX_NEEDLE in text,
                  "missing SPDX header: " + name, problems)
            check(SPDX_COPYRIGHT in text,
                  "missing SPDX copyright: " + name, problems)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    reuse_token = "SPDX-License-" "Identifier = \"Apache-2.0\""
    check('"docs/**"' in reuse and reuse_token in reuse,
          "REUSE docs coverage is missing", problems)
    for path in HERE.iterdir():
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES or
              path.name.endswith(".sha256"),
              "prohibited binary/media/corpus artifact: " + path.name,
              problems)
        check(not path.is_symlink(), "task symlink: " + path.name, problems)
        check(path.name not in {"CMakeLists.txt", "provider.json",
                                "adapter.json"},
              "provider artifact: " + path.name, problems)
        check(not (path.is_file() and path.name.startswith("LICENSE")),
              "vendored license file: " + path.name, problems)


def check_absence_live(problems: List[str]) -> None:
    librispeech = reference.librispeech_probe()
    check(librispeech.get("present") is False,
          "LibriSpeech data appeared; revisit the blocker package", problems)
    common_voice = reference.common_voice_probe()
    check(common_voice.get("present") is False,
          "Common Voice data appeared; revisit the blocker package", problems)
    rights = reference.rights_probe()
    check(rights.get("use_approved") is False and
          rights.get("listening_approved") is False,
          "dataset rights are no longer blocked", problems)
    check(reference.collect_blockers(),
          "the blocker list unexpectedly became empty", problems)


def check_reproduction(report_payload: bytes,
                       problems: List[str]) -> bool:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    process = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--stdout-report"],
        cwd=str(HERE), capture_output=True, env=environment, check=False)
    if process.returncode != 0:
        problems.append("in-process report regeneration failed")
        return False
    check(process.stdout == report_payload, "in-process report bytes differ",
          problems)
    repro = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--verify-repro"],
        cwd=str(HERE), capture_output=True, env=environment, check=False)
    if repro.returncode != 0 or b"ok=1\n" not in repro.stdout:
        problems.append("in-memory bundle reproduction is not ok: " +
                        repro.stdout.decode("utf-8", "replace") +
                        repro.stderr.decode("utf-8", "replace"))
        return False
    return process.stdout == report_payload


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / ("cold-" + str(index))
    sdk = (scratch / "audioml/worktrees/audio-sdk" /
           "SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE")
    target = (sdk / "docs/task-evidence/"
              "librispeech-and-common-voice-evidence-intake")
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.WORKSPACE / relative)
    board = scratch / "audioml/audio-benchmark-platform/plan/swarm/TASKS.json"
    board.parent.mkdir(parents=True, exist_ok=True)
    board.symlink_to(BOARD_PATH)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.SDK_ROOT / relative)
    return target


def check_cold_starts(problems: List[str]) -> List[str]:
    committed = (
        REPORT_PATH.read_bytes() if REPORT_PATH.is_file() else b"",
        SIDECAR_PATH.read_bytes() if SIDECAR_PATH.is_file() else b"",
        SOURCES_PATH.read_bytes() if SOURCES_PATH.is_file() else b"",
        CONTRACT_PATH.read_bytes() if CONTRACT_PATH.is_file() else b"",
    )
    if not all(committed):
        problems.append("committed artifacts missing")
        return []
    digests: List[str] = []
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    with tempfile.TemporaryDirectory(
            prefix="sdk-libri-cv-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run(
                [sys.executable, "run.py", "--all"], cwd=target,
                capture_output=True, text=True, env=environment)
            if process.returncode != 0:
                problems.append("cold_start_" + str(index) + "_failed: " +
                                process.stdout.strip() +
                                process.stderr.strip())
                continue
            generated = (
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
                (target / "contract.json").read_bytes(),
            )
            if generated != committed:
                problems.append("cold_start_" + str(index) + "_bytes_differ")
            digests.append(sha256_bytes(generated[0]))
    if len(digests) != 3 or len(set(digests)) != 1:
        problems.append("cold_start_not_byte_identical")
    return digests


def check_git_scope(problems: List[str]) -> List[str]:
    process = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=str(SDK_ROOT), capture_output=True, text=True, check=False)
    if process.returncode != 0:
        problems.append("git status failed in the SDK worktree")
        return []
    changed: List[str] = []
    for line in process.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        check(path.startswith(TASK_PREFIX),
              "change outside task-local scope: " + path, problems)
    diff = subprocess.run(
        ["git", "diff", "--check"], cwd=str(SDK_ROOT),
        capture_output=True, text=True, check=False)
    check(diff.returncode == 0 and not diff.stdout.strip(),
          "git diff --check failed: " + diff.stdout.strip(), problems)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            check(path.name in ALLOWED_FILES,
                  "unpinned task file: " + path.name, problems)
    return changed


def main() -> int:
    problems: List[str] = []
    try:
        contract = strict_load(CONTRACT_PATH)
        report = strict_load(REPORT_PATH)
        report_payload = REPORT_PATH.read_bytes()
        check(isinstance(contract, dict), "contract root is not an object",
              problems)
        check(isinstance(report, dict), "report root is not an object",
              problems)
        check(finite_json(report), "report contains a nonfinite value",
              problems)
        check(finite_json(contract), "contract contains a nonfinite value",
              problems)
        check(canonical_bytes(report) + b"\n" == report_payload,
              "report bytes are not canonical", problems)
        check(canonical_bytes(contract) + b"\n" ==
              CONTRACT_PATH.read_bytes(),
              "contract bytes are not canonical", problems)
        check(report_payload.endswith(b"\n") and
              not report_payload.endswith(b"\n\n"),
              "report must have exactly one trailing newline", problems)
        check_contract(contract, report, problems)
        pins = check_pins(contract, report, problems)
        check_report(report, problems)
        check_board(contract, report, problems)
        check_licensing(problems)
        check_absence_live(problems)
        reproduction_ok = check_reproduction(report_payload, problems)
        digests = check_cold_starts(problems)
        changed = check_git_scope(problems)
    except (OSError, VerificationError, ValueError, KeyError, TypeError) as error:
        problems.append("verification exception: " + str(error))
        reproduction_ok = False
        digests = []
        pins = 0
        changed = []
    digest = (sha256_file(REPORT_PATH) if REPORT_PATH.is_file()
              else "unavailable")
    if problems:
        for problem in problems:
            print("FAIL: " + problem)
        print("verification_failed=" + str(len(problems)) +
              " report_sha256=" + digest)
        return 1
    print("PASS pins=" + str(pins) + " reproduction_ok=" +
          str(int(reproduction_ok)) + " cold_starts=3/3 "
          "byte_identical=true profile=evidence "
          "status=proposal_only_incomplete decision=DEFER "
          "qualification=not_qualified gates_blocked=8 "
          "report_sha256=" + digest + " changed_files=" + str(len(changed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
