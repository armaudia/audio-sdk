# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the SDK-MICROSOFT-NSNET2-BASELINE blocker package.

It checks strict JSON, canonical bytes, exact pins, DEFER/not-qualified
semantics, the documented model boundary, stable linked-row identity (never the
full mutable board), licensing, prohibited artifacts, task-local git scope and
three cold-start byte-identical regenerations. It never writes package
evidence.
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
TASK_PREFIX = "docs/task-evidence/microsoft-nsnet2-baseline/"
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
TASK_ID = "SDK-MICROSOFT-NSNET2-BASELINE"
COMPONENT = "microsoft-nsnet2-baseline"
BASE_COMMIT = "0cc1e79e592d7fc25f054fcd98824053be281f5e"
GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]
EXPECTED_LINK = {
    "task_id": TASK_ID,
    "title": "Microsoft NSNet2 baseline",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
ARTIFACT_FILES = (
    "README.md",
    "contract.json",
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "SOURCES.sha256",
    "test_reference.py",
    "verify.py",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx", ".pt", ".pth",
    ".ckpt", ".safetensors", ".bin", ".so", ".dylib", ".a", ".o", ".zip",
    ".tar", ".gz", ".whl", ".npy", ".pyc", ".wasm", ".elf", ".hex",
}
BLOCKER_KEYS = {
    "status", "artifact", "source", "weights", "license", "hardware",
    "runtime", "config", "cohort", "scorer", "third_party",
    "pinned_revision",
    "source_digest", "weights_digest", "license_digest", "hardware_digest",
    "runtime_digest", "config_digest", "cohort_digest", "scorer_digest",
    "no_upstream_parity_claim", "rights_requirement", "workspace_search",
    "not_attempted", "reopen",
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
    for key, value in (("task", TASK_ID), ("component", COMPONENT),
                       ("mode", "feasibility"),
                       ("branch", "swarm/SDK-MICROSOFT-NSNET2-BASELINE"),
                       ("base_commit", BASE_COMMIT),
                       ("verification_profile", "Enhancement")):
        check(contract.get(key) == value, "contract mismatch: " + key,
              problems)
    check(contract.get("decision") == "DEFER",
          "contract decision is not DEFER", problems)
    check(contract.get("status") == "proposal_only_not_qualified",
          "contract status is not proposal_only_not_qualified", problems)
    check(contract.get("incomplete") is True,
          "contract is not marked incomplete", problems)
    check(contract.get("proposal_only") is True,
          "contract is not marked proposal only", problems)
    check(contract.get("qualification_status") == "not_qualified",
          "contract qualification_status mismatch", problems)
    check(contract.get("comparison_status") ==
          "blocked_official_artifact_terms_runtime_and_matched_cohort_absent",
          "contract comparison status mismatch", problems)
    qualification = contract.get("qualification", {})
    check(qualification.get("status") == "not_qualified",
          "contract qualification is not not_qualified", problems)
    check(qualification.get("readiness") == "incomplete",
          "contract readiness is not incomplete", problems)
    check(qualification.get("decision") == "DEFER",
          "contract qualification decision mismatch", problems)
    check(qualification.get("candidate_qualified") is False,
          "contract claims a qualified candidate", problems)
    check(qualification.get("upstream_parity") is False,
          "contract claims upstream parity", problems)
    check(qualification.get("all_required_results_present") is False,
          "contract claims all required results are present", problems)
    check(qualification.get("proposal_only") is True,
          "contract is not proposal only", problems)

    boundary = contract.get("boundary", {})
    check(boundary == report.get("boundary"),
          "contract and report boundary differ", problems)
    check(boundary.get("installed_v0_unchanged") is True,
          "installed v0 boundary changed", problems)
    check(boundary.get("public_api_abi_changed") is False,
          "public ABI boundary changed", problems)
    check(boundary.get("provider_registered") is False,
          "provider registered", problems)
    check(boundary.get("descriptor_registration") is False,
          "descriptor registered", problems)
    check(boundary.get("enabled_by_default") is False,
          "provider enabled by default", problems)
    check(boundary.get("shared_cmake_changed") is False,
          "shared CMake changed", problems)
    check(boundary.get("ci_changed") is False, "CI changed", problems)
    check(boundary.get("board_or_handoff_changed") is False,
          "board or handoff changed", problems)
    check(boundary.get("real_corpus_or_weights") is False,
          "real corpus or weights claimed", problems)
    check(boundary.get("benchmark_claim") is False,
          "benchmark claim present", problems)
    check(boundary.get("release_claim") is False,
          "release claim present", problems)
    check(boundary.get("format") == {
        "sample_rate_hz": 16000, "channels": 1,
        "sample_format": "float32", "frame_samples": 160,
    }, "contract v0 format mismatch", problems)

    blocker = contract.get("upstream_blocker", {})
    check(set(blocker) == BLOCKER_KEYS, "upstream blocker schema mismatch",
          problems)
    check(blocker.get("status") ==
          "blocked_official_artifact_terms_runtime_and_matched_cohort_absent",
          "upstream blocker status mismatch", problems)
    check((blocker.get("source") or {}).get("status") == "absent",
          "source is not recorded as absent", problems)
    check((blocker.get("source") or {}).get("revision") is None,
          "source has a fabricated revision", problems)
    check((blocker.get("source") or {}).get("tree_digest") is None,
          "source has a fabricated tree digest", problems)
    check((blocker.get("source") or {}).get("license") is None,
          "source has a fabricated license", problems)
    check((blocker.get("weights") or {}).get("status") == "absent",
          "weights are not recorded as absent", problems)
    for key in ("path", "sha256", "byte_count", "conversion_recipe",
                "precision", "quantization", "operator_set"):
        check((blocker.get("weights") or {}).get(key) is None,
              "weights have a fabricated " + key, problems)
    check((blocker.get("license") or {}).get("status") ==
          "blocked_model_terms_not_recorded",
          "license is not recorded as terms-not-recorded", problems)
    check((blocker.get("license") or {}).get("reported_name") is None,
          "license has a fabricated name", problems)
    check((blocker.get("license") or {}).get(
        "general_repository_notice_recorded") is True,
        "the general repository notice is not recorded", problems)
    check((blocker.get("license") or {}).get(
        "artifact_specific_model_terms_recorded") is False,
        "artifact-specific model terms are claimed recorded", problems)
    check((blocker.get("license") or {}).get(
        "reported_terms_recorded_in_pinned_evidence") is False,
        "license terms are claimed recorded", problems)
    check((blocker.get("license") or {}).get("license_text_present") is False,
          "license text is claimed present", problems)
    check((blocker.get("license") or {}).get("license_text_sha256") is None,
          "license has a fabricated digest", problems)
    check((blocker.get("license") or {}).get("model_terms_present") is False,
          "model terms are claimed present", problems)
    check((blocker.get("license") or {}).get("use_approved") is False,
          "use is claimed approved", problems)
    check((blocker.get("license") or {}).get(
        "redistribution_approved") is False,
        "redistribution is claimed approved", problems)
    check((blocker.get("hardware") or {}).get("status") == "absent",
          "hardware is not recorded as absent", problems)
    check((blocker.get("hardware") or {}).get("runner") is None,
          "hardware runner is fabricated", problems)
    check((blocker.get("hardware") or {}).get("firmware_sha256") is None,
          "firmware digest is fabricated", problems)
    check((blocker.get("hardware") or {}).get(
        "vendor_resource_figures_generalizable") is False,
        "vendor resource figures are generalized", problems)
    check((blocker.get("runtime") or {}).get("status") == "absent_unpinned",
          "runtime is not recorded as absent", problems)
    check((blocker.get("runtime") or {}).get("sha256") is None,
          "runtime digest is fabricated", problems)
    check((blocker.get("runtime") or {}).get(
        "portable_host_runtime") is None,
        "portable host runtime is fabricated", problems)
    check((blocker.get("runtime") or {}).get("onnxruntime_version") is None and
          (blocker.get("runtime") or {}).get("python_version") is None,
          "runtime version is fabricated", problems)
    check((blocker.get("config") or {}).get("status") == "absent",
          "config is not recorded as absent", problems)
    check((blocker.get("config") or {}).get("sha256") is None,
          "config has a fabricated digest", problems)
    check((blocker.get("cohort") or {}).get("status") == "absent",
          "cohort is not recorded as absent", problems)
    check((blocker.get("cohort") or {}).get("corpus_rights") is False,
          "cohort rights are claimed", problems)
    check((blocker.get("cohort") or {}).get(
        "clean_references_present") is False,
        "clean references are claimed present", problems)
    check((blocker.get("scorer") or {}).get("status") == "unapproved",
          "scorer is not recorded as unapproved", problems)
    check((blocker.get("scorer") or {}).get("approved_si_sdr") is False,
          "SI-SDR is claimed approved", problems)
    check((blocker.get("scorer") or {}).get("approved_stoi") is False,
          "STOI is claimed approved", problems)
    third_party = blocker.get("third_party") or {}
    check(third_party.get("accepted_as_official_artifact") is False and
          third_party.get("accepted_as_substitute") is False and
          third_party.get("weights_present_locally") is False,
          "third-party substitute is accepted or claims weights", problems)
    check(third_party.get("path") == reference.THIRD_PARTY_PATH,
          "third-party probe path mismatch", problems)
    for key in ("pinned_revision", "source_digest", "weights_digest",
                "license_digest", "hardware_digest", "runtime_digest",
                "config_digest", "cohort_digest", "scorer_digest"):
        check(blocker.get(key) is None,
              "blocker has a fabricated digest: " + key, problems)
    check(blocker.get("no_upstream_parity_claim") is True,
          "upstream parity claim is not disabled", problems)
    rights = str(blocker.get("rights_requirement", "")).lower()
    for word in ("license", "model", "terms", "permission", "consent"):
        check(word in rights, "rights requirement omits: " + word, problems)
    not_attempted = " ".join(blocker.get("not_attempted", [])).lower()
    for phrase in ("clone", "model", "license", "audio"):
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
    check(contract.get("geometry") == report.get("geometry"),
          "contract and report geometry differ", problems)
    check(contract.get("model_boundary") == report.get("model_boundary"),
          "contract and report model boundary differ", problems)
    check(contract.get("enhancement_control") ==
          report.get("enhancement_control"),
          "contract and report enhancement control differ", problems)
    check(contract.get("scorer") == report.get("scorer"),
          "contract and report scorer differ", problems)
    check(contract.get("model_boundary") == reference.MODEL_BOUNDARY,
          "contract model boundary is not closed", problems)

    canonical = contract.get("canonical_report", {})
    report_payload = REPORT_PATH.read_bytes()
    sidecar_payload = SIDECAR_PATH.read_bytes()
    check(canonical.get("file_sha256") == sha256_bytes(report_payload),
          "contract report file digest mismatch", problems)
    check(canonical.get("sidecar_sha256") ==
          sha256_bytes(sidecar_payload),
          "contract sidecar digest mismatch", problems)
    check(canonical.get("canonical_digest") ==
          sha256_bytes(canonical_bytes(report)),
          "contract canonical report digest mismatch", problems)


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") == reference.SCHEMA_ID,
          "report schema mismatch", problems)
    for key, value in (("task", TASK_ID), ("component", COMPONENT),
                       ("mode", "feasibility"),
                       ("branch", "swarm/SDK-MICROSOFT-NSNET2-BASELINE"),
                       ("base_commit", BASE_COMMIT),
                       ("verification_profile", "Enhancement")):
        check(report.get(key) == value, "report mismatch: " + key, problems)
    check(report.get("decision") == "DEFER", "report decision is not DEFER",
          problems)
    check(report.get("status") == "proposal_only_not_qualified",
          "report status is not proposal_only_not_qualified", problems)
    check(report.get("incomplete") is True,
          "report is not marked incomplete", problems)
    check(report.get("proposal_only") is True,
          "report is not marked proposal only", problems)
    check(report.get("qualification_status") == "not_qualified",
          "report qualification_status mismatch", problems)
    qualification = report.get("qualification", {})
    check(qualification.get("status") == "not_qualified" and
          qualification.get("candidate_qualified") is False and
          qualification.get("readiness") == "incomplete" and
          qualification.get("decision") == "DEFER" and
          qualification.get("proposal_only") is True,
          "report qualification is not incomplete/not_qualified", problems)
    check(report.get("profile", {}).get("name") == "Enhancement",
          "report profile is not Enhancement", problems)

    reference_block = report.get("reference", {})
    for key in ("real_component_source_present",
                "official_model_artifact_present",
                "component_config_present",
                "eligible_runner_present",
                "pinned_runtime_present",
                "portable_host_runtime_present",
                "matched_cohort_present",
                "approved_scorer_present",
                "license_text_present", "rights_approved",
                "upstream_parity", "downloads", "model_weights",
                "candidate_processing", "real_corpus_read",
                "third_party_accepted_as_official"):
        check(reference_block.get(key) is False,
              "reference block claim is not false: " + key, problems)
    check(reference_block.get("synthetic_only") is True,
          "reference block is not synthetic-only", problems)
    check(reference_block.get("deterministic") is True,
          "reference block is not deterministic", problems)

    model = report.get("model_boundary", {})
    check(model == reference.MODEL_BOUNDARY,
          "model boundary is not the declared closed boundary", problems)
    check(model.get("documented") is True,
          "model boundary is not documented", problems)
    check(model.get("sdk_disposition") == "sdk-model",
          "model boundary disposition mismatch", problems)
    check(model.get("host_target_eligible") is False,
          "host target is claimed eligible", problems)
    check(model.get("portable_adapter_present") is False,
          "a portable adapter is claimed present", problems)
    check(model.get("license_text_present") is False,
          "license text is claimed present", problems)
    check(model.get("model_terms_present") is False,
          "model terms are claimed present", problems)
    check(model.get("use_approved") is False,
          "use is claimed approved", problems)
    check(model.get("redistribution_approved") is False,
          "redistribution is claimed approved", problems)
    check(model.get("weights_present") is False,
          "model weights are claimed present", problems)
    check(model.get("local_runtime_present") is False,
          "local runtime is claimed present", problems)
    check(model.get("vendor_output_present") is False,
          "vendor output is claimed present", problems)
    check(model.get("adapter_implemented") is False,
          "an adapter is claimed implemented", problems)
    check(model.get("adapter_default_registration") is False,
          "adapter default registration is claimed", problems)
    check(model.get("automatic_discovery") is False,
          "automatic discovery is claimed", problems)
    check(model.get("fallback") == "none",
          "a fallback is claimed", problems)
    check(model.get("reported_parameter_count_is_local_measurement") is False,
          "the parameter count is claimed measured", problems)
    check(model.get("reported_parameter_count") is None,
          "a parameter count is invented", problems)
    check(model.get("third_party_accepted_as_official") is False,
          "a third-party reimplementation is accepted as official", problems)
    check(model.get("official_download_path_available") is False,
          "the official download path is claimed available", problems)
    check(model.get("general_repository_notice_recorded") is True,
          "the general repository notice is not recorded", problems)
    check(model.get("artifact_specific_model_terms_recorded") is False,
          "artifact-specific model terms are claimed", problems)
    check(model.get("vendor_claims_separate_from_local_measurements")
          is True,
          "vendor claims are not separated from measurements", problems)

    source = report.get("source_probe", {})
    check(source.get("status") == "blocked_official_source_absent" and
          source.get("present") is False and source.get("found") == [],
          "source probe is not absent", problems)
    for key in ("revision", "tree_digest", "file_count", "license"):
        check(source.get(key) is None,
              "source probe has fabricated " + key, problems)
    weights = report.get("weights_probe", {})
    check(weights.get("status") == "blocked_official_model_artifact_absent" and
          weights.get("present") is False and weights.get("found") == [],
          "weights probe is not absent", problems)
    for key in ("path", "sha256", "byte_count", "conversion_recipe",
                "precision", "quantization", "operator_set"):
        check(weights.get(key) is None,
              "weights probe has fabricated " + key, problems)
    license_block = report.get("license_probe", {})
    check(license_block.get("status") == "blocked_model_terms_not_recorded" and
          license_block.get("reported_name") is None and
          license_block.get("license_text_present") is False and
          license_block.get("model_terms_present") is False and
          license_block.get("use_approved") is False and
          license_block.get("redistribution_approved") is False and
          license_block.get("host_target_approved") is False,
          "license probe is not blocked", problems)
    check(license_block.get("general_repository_notice_recorded") is True and
          license_block.get("artifact_specific_model_terms_recorded") is False,
          "license probe misstates the general notice", problems)
    check("MIT" in str(license_block.get("reported_code_license")) and
          "CC BY 4.0" in str(
              license_block.get("reported_documentation_license")),
          "license probe misstates the source-reported general notice",
          problems)
    check(license_block.get("license_text_sha256") is None,
          "license probe has a fabricated digest", problems)
    hardware = report.get("hardware_probe", {})
    check(hardware.get("status") == "blocked_eligible_runner_absent" and
          hardware.get("runner") is None and
          hardware.get("hardware_attached") is None and
          hardware.get("firmware_sha256") is None,
          "hardware probe is not absent", problems)
    check(hardware.get("vendor_resource_figures_generalizable") is False,
          "hardware probe generalizes vendor figures", problems)
    runtime = report.get("runtime_probe", {})
    check(runtime.get("status") == "blocked_runtime_unpinned" and
          runtime.get("pinned") is False and runtime.get("lockfiles") == [],
          "runtime probe is not absent/unpinned", problems)
    check(runtime.get("python_version") is None and
          runtime.get("onnxruntime_version") is None and
          runtime.get("firmware_sha256") is None and
          runtime.get("portable_host_runtime") is None,
          "runtime probe has fabricated identity", problems)
    cohort = report.get("cohort_probe", {})
    check(cohort.get("status") == "blocked_matched_cohort_absent" and
          cohort.get("present") is False and cohort.get("found") == [],
          "cohort probe is not absent", problems)
    check(cohort.get("corpus_rights") is False and
          cohort.get("clean_references_present") is False,
          "cohort probe overclaims rights", problems)
    scorer = report.get("scorer_probe", {})
    check(scorer.get("status") == "unapproved_no_scorer_implemented" and
          scorer.get("approved_si_sdr") is False and
          scorer.get("approved_stoi") is False and
          scorer.get("authorized_listening") is False and
          scorer.get("predictive_screen_labeled") is False and
          scorer.get("calibrated_here") is False,
          "scorer probe is not unapproved", problems)
    check(scorer.get("sha256") is None,
          "scorer probe has a fabricated digest", problems)
    rights = report.get("rights_probe", {})
    check(rights.get("status") == "blocked_rights_unrecorded" and
          rights.get("review") == "blocked" and
          rights.get("source_license") is None and
          rights.get("use_approved") is False and
          rights.get("model_terms_present") is False and
          rights.get("input_corpus_rights") is False,
          "rights probe is not blocked", problems)
    third_party = report.get("third_party_probe", {})
    check(third_party.get("path") == reference.THIRD_PARTY_PATH and
          third_party.get("official_microsoft_nsnet2") is False and
          third_party.get("accepted_as_official_artifact") is False and
          third_party.get("accepted_as_substitute") is False and
          third_party.get("weights_present_locally") is False,
          "third-party probe accepts a substitute or claims weights",
          problems)
    check(isinstance(third_party.get("weight_candidates"), list),
          "third-party weight candidate list is malformed", problems)
    check(third_party.get("reported_license") in (None, "MIT"),
          "third-party license is misreported", problems)
    check(third_party.get("license_scope") in
          (None, "third-party repository code only; not official model terms"),
          "third-party license scope is misreported", problems)

    geometry = report.get("geometry", {})
    check(geometry.get("component") == "Microsoft NSNet2 baseline",
          "component name mismatch", problems)
    check(geometry.get("declared_sample_rates_hz") == [48000],
          "declared sample rates mismatch", problems)
    check(geometry.get("declared_frame_ms") == 20 and
          geometry.get("declared_hop_ms") is None,
          "declared frame/hop durations mismatch", problems)
    check(geometry.get("derived_frame_samples_at_48k") == 960 and
          geometry.get("derived_hop_samples_at_48k") is None,
          "derived sample counts mismatch", problems)
    check(geometry.get("derived_sample_counts_are_api_constants") is False,
          "derived sample counts are claimed as API constants", problems)
    check(geometry.get("reported_parameter_count") is None,
          "a parameter count is invented", problems)
    for key in ("declared_channels", "declared_feature_extraction",
                "declared_output_mapping", "declared_buffering_delay_samples",
                "declared_reset_drain_semantics", "declared_quantization"):
        check(geometry.get(key) is None,
              "geometry invents " + key, problems)
    check(geometry.get("local_channel_guard") == 64,
          "local channel guard mismatch", problems)
    check(geometry.get("official_download_path_available") is False,
          "the official download path is claimed available", problems)
    check(geometry.get("vendor_resource_figures_generalizable") is False,
          "geometry generalizes vendor figures", problems)
    check(geometry.get("verified_here") is False and
          geometry.get("measured_here") is False and
          geometry.get("candidate_output") is False and
          geometry.get("v0_can_represent_declared_input") is False,
          "geometry claims verification/measurement/output", problems)

    enhancement = report.get("enhancement_control", {})
    check(enhancement.get("status") == "not_evaluated_by_this_task" and
          enhancement.get("metrics") is None and
          enhancement.get("result") is None and
          enhancement.get("qualifies_candidate") is False and
          enhancement.get("quality_claim") is False and
          enhancement.get("intelligibility_claim") is False and
          enhancement.get("listening_claim") is False and
          enhancement.get("timing_claim") is False,
          "enhancement control is overclaimed", problems)
    for key in ("identity_noisy_control", "established_task_matched_baseline",
                "paired_si_sdr_db", "paired_stoi",
                "clean_speech_preservation", "peak_and_invalid_outputs",
                "alignment_and_content_delay", "state_and_reset", "memory",
                "measured_availability_timing"):
        check(enhancement.get(key) is None,
              "enhancement control invents " + key, problems)
    scorer_block = report.get("scorer", {})
    check(scorer_block.get("status") ==
          "unapproved_no_scorer_implemented" and
          scorer_block.get("calibrated_here") is False,
          "scorer block is not unapproved", problems)
    for key in ("si_sdr", "stoi", "dnsmos", "pesq", "listening_panel",
                "approved_scorer_sha256"):
        check(scorer_block.get(key) is None,
              "scorer block invents " + key, problems)

    candidate = report.get("candidates", {}).get(reference.CANDIDATE, {})
    check(candidate.get("status") ==
          "blocked_official_artifact_terms_runtime_and_matched_cohort_absent",
          "candidate status mismatch", problems)
    check(candidate.get("metrics") is None and
          candidate.get("result") is None and
          candidate.get("qualifies_candidate") is False,
          "candidate carries metrics or qualifies", problems)
    required = report.get("required_results", {})
    check(isinstance(required, dict) and required, "required results missing",
          problems)
    check(all(value.startswith("blocked_") or
              value.startswith("partial_") or
              value.startswith("not_evaluated_")
              for value in required.values()),
          "a required result is not blocked/partial/not-evaluated", problems)
    mapping = report.get("profile_mapping", {})
    check(isinstance(mapping, dict) and mapping, "profile mapping missing",
          problems)
    check(all(value.startswith("blocked_") or value.startswith("partial_")
              for value in mapping.values()),
          "a profile mapping item is not blocked/partial", problems)

    adverse = report.get("adverse", {})
    check(adverse.get("invalid_config_and_input", {}).get("all_rejected")
          is True, "invalid requests were accepted", problems)
    check(adverse.get("invalid_config_and_input", {}).get("accepted_count")
          == 0, "invalid request accepted count is nonzero", problems)
    check(adverse.get("invalid_json_numeric_fields", {}).get("all_rejected")
          is True, "invalid JSON was accepted", problems)
    check(adverse.get("invalid_json_numeric_fields", {}).get("accepted_count")
          == 0, "invalid JSON accepted count is nonzero", problems)
    check(adverse.get("missing_result", {}).get("metrics") is None and
          adverse.get("missing_result", {}).get("qualifies_candidate")
          is False,
          "missing result carries metrics or qualifies", problems)

    stimuli = report.get("stimulus_probe", {})
    check(stimuli.get("candidate_processing") is False,
          "stimulus probe claims candidate processing", problems)
    check(stimuli.get("harness_geometry", {}).get("channels") == 1 and
          stimuli.get("harness_geometry", {}).get("frame_samples") == 960 and
          stimuli.get("harness_geometry", {}).get("hop_samples") is None and
          stimuli.get("harness_geometry", {}).get("sample_rate_hz") == 48000
          and stimuli.get("harness_geometry", {}).get(
              "verified_model_geometry") is False,
          "harness geometry is overclaimed", problems)
    check(all(item.get("byte_identical") is True
              for item in stimuli.get("identity_control", {}).values()),
          "harness identity control is not bit exact", problems)

    checks = report.get("local_harness_checks", {})
    check(all(value is True for value in checks.values()),
          "a local harness check is not true", problems)
    check(len(checks) >= 20, "local harness check set is too small", problems)
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
    check(report.get("no_missing_result_qualifies_candidate") is True,
          "missing-result guard is not enabled", problems)
    check(report.get("board_full_file_hashed") is False,
          "report hashes the full mutable board", problems)
    check(report.get("regression_count") == 0 and
          report.get("regressions") == [],
          "regression fields are not empty", problems)
    classes = report.get("evidence_classes", [])
    check("no_quality_or_timing_measurement" in classes,
          "evidence classes omit the no-measurement label", problems)


def check_pins(contract: Dict[str, Any], report: Dict[str, Any],
               problems: List[str]) -> int:
    pins = contract.get("artifact_pins", {})
    expected_names = tuple(name for name in ARTIFACT_FILES
                           if name != "contract.json")
    check(set(pins) == set(expected_names),
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
        check(target.is_file(), "missing source pin target: " + path, problems)
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
    reuse_token = ("SPDX-License-" "Identifier = \"Apache-2.0\"")
    check('"docs/**"' in reuse and reuse_token in reuse,
          "REUSE docs coverage is missing", problems)
    for path in HERE.iterdir():
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES or
              path.name.endswith(".sha256"),
              "prohibited binary/audio/model artifact: " + path.name,
              problems)
        check(not path.is_symlink(), "task symlink: " + path.name, problems)
        check(path.name not in {"CMakeLists.txt", "provider.json",
                                "adapter.json",
                                "nsnet2.tflite", "nsnet2.onnx"},
              "provider or model artifact: " + path.name, problems)
        check(not (path.is_file() and path.name.startswith("LICENSE")),
              "vendored license file: " + path.name, problems)


def check_absence_live(problems: List[str]) -> None:
    source = reference.source_probe()
    check(source.get("present") is False,
          "official DNS-Challenge source appeared; revisit the blocker package",
          problems)
    weights = reference.weights_probe()
    check(weights.get("present") is False,
          "an official NSNet2 model artifact appeared; revisit the blocker "
          "package", problems)
    license_block = reference.license_probe()
    check(license_block.get("use_approved") is False,
          "use is no longer blocked", problems)
    check(license_block.get("license_text_present") is False,
          "a license text appeared; revisit the blocker package", problems)
    check(license_block.get("artifact_specific_model_terms_recorded") is False,
          "artifact-specific model terms appeared; revisit the blocker "
          "package", problems)
    hardware = reference.hardware_probe()
    check(hardware.get("runner") is None,
          "an approved runner appeared; revisit the blocker package",
          problems)
    runtime = reference.runtime_probe()
    check(runtime.get("pinned") is False,
          "a pinned runtime appeared; revisit the blocker package", problems)
    check(runtime.get("portable_host_runtime") is None,
          "a portable host runtime appeared; revisit the blocker package",
          problems)
    cohort = reference.cohort_probe()
    check(cohort.get("present") is False,
          "a matched cohort appeared; revisit the blocker package", problems)
    scorer = reference.scorer_probe()
    check(scorer.get("approved_si_sdr") is False,
          "an approved scorer appeared; revisit the blocker package",
          problems)
    rights = reference.rights_probe()
    check(rights.get("review") == "blocked",
          "rights review is no longer blocked", problems)
    third_party = reference.third_party_probe()
    check(third_party.get("accepted_as_official_artifact") is False and
          third_party.get("accepted_as_substitute") is False,
          "a third-party reimplementation is accepted", problems)
    check(third_party.get("weights_present_locally") is False,
          "third-party weights appeared; revisit the blocker package",
          problems)


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
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-MICROSOFT-NSNET2-BASELINE"
    target = sdk / "docs/task-evidence/microsoft-nsnet2-baseline"
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
    for relative in sorted(reference.THIRD_PARTY_PROBE_PATHS):
        source = reference.WORKSPACE / relative
        if source.exists():
            link = scratch / "audioml" / relative
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(source)
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
            prefix="sdk-microsoft-nsnet2-baseline-cold-") as temporary:
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
    allowed = set(run.MANIFEST_FILES) | {"contract.json", "SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            check(path.name in allowed,
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
          "byte_identical=true profile=Enhancement "
          "status=proposal_only_not_qualified decision=DEFER "
          "qualification=not_qualified gates_blocked=8 "
          "report_sha256=" + digest + " changed_files=" + str(len(changed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
