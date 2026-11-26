# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the SDK-FACEBOOK-DENOISER-DNS64 package.

It checks strict JSON, canonical bytes, exact pins, DEFER/not-qualified
semantics, the reported non-commercial boundary, stable linked-row identity
(never the full mutable board), licensing, prohibited artifacts, task-local git
scope and three cold-start byte-identical regenerations. It never writes package
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
TASK_PREFIX = "docs/task-evidence/facebook-denoiser-dns64/"
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
TASK_ID = "SDK-FACEBOOK-DENOISER-DNS64"
COMPONENT = "facebook-denoiser-dns64"
BASE_COMMIT = "9cf118bc32ff5ac801318158d97d5bb8dd947374"
GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]
EXPECTED_LINK = {
    "task_id": TASK_ID,
    "title": "Facebook Denoiser DNS64",
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
    ".th", ".npz", ".h5",
}
BLOCKER_KEYS = {
    "status", "artifact", "source", "weights", "license", "runtime",
    "fixture", "geometry", "pinned_revision", "source_digest",
    "weights_digest", "license_digest", "runtime_digest", "fixture_digest",
    "geometry_digest", "no_upstream_parity_claim", "rights_requirement",
    "workspace_search", "not_attempted", "reopen",
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
                       ("branch", "swarm/SDK-FACEBOOK-DENOISER-DNS64"),
                       ("base_commit", BASE_COMMIT),
                       ("verification_profile", "enhancement")):
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
          "blocked_source_weights_runtime_license_and_fixture_absent",
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
    check(boundary.get("descriptor_default_changed") is False,
          "descriptor default changed", problems)
    check(boundary.get("enabled_by_default") is False,
          "provider enabled by default", problems)
    check(boundary.get("shared_cmake_changed") is False,
          "shared CMake changed", problems)
    check(boundary.get("ci_changed") is False, "CI changed", problems)
    check(boundary.get("board_or_handoff_changed") is False,
          "board or handoff changed", problems)
    check(boundary.get("registry_changed") is False,
          "registry changed", problems)
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
          "blocked_source_weights_runtime_license_and_fixture_absent",
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
    check((blocker.get("weights") or {}).get("variant") == "dns64",
          "weights variant mismatch", problems)
    check((blocker.get("weights") or {}).get("artifact_path") is None,
          "weights path is fabricated", problems)
    check((blocker.get("weights") or {}).get("sha256") is None,
          "weights digest is fabricated", problems)
    check((blocker.get("weights") or {}).get("byte_count") is None,
          "weights byte count is fabricated", problems)
    check((blocker.get("weights") or {}).get("checkpoint_terms") is None,
          "checkpoint terms are fabricated", problems)
    check((blocker.get("license") or {}).get("status") ==
          "blocked_noncommercial_use_not_approved",
          "license is not recorded as not approved", problems)
    check((blocker.get("license") or {}).get("reported_name") ==
          "CC-BY-NC-4.0", "reported license mismatch", problems)
    check((blocker.get("license") or {}).get("license_text_present") is False,
          "license text is claimed present", problems)
    check((blocker.get("license") or {}).get("license_text_sha256") is None,
          "license has a fabricated digest", problems)
    for key in ("commercial_use_approved", "noncommercial_use_approved",
                "redistribution_approved", "derived_output_approved",
                "host_target_approved"):
        check((blocker.get("license") or {}).get(key) is False,
              "license right is claimed: " + key, problems)
    check((blocker.get("runtime") or {}).get("status") == "absent_unpinned",
          "runtime is not recorded as absent", problems)
    check((blocker.get("runtime") or {}).get("sha256") is None,
          "runtime digest is fabricated", problems)
    check((blocker.get("runtime") or {}).get("lockfile") is None,
          "runtime lock is fabricated", problems)
    check((blocker.get("fixture") or {}).get("status") == "absent",
          "fixture is not recorded as absent", problems)
    check((blocker.get("fixture") or {}).get("corpus_rights") is False,
          "fixture corpus rights are claimed", problems)
    check((blocker.get("fixture") or {}).get("paired_clean_reference")
          is False, "paired clean reference is claimed", problems)
    check((blocker.get("fixture") or {}).get("scorer_pinned") is False,
          "a scorer is claimed pinned", problems)
    check((blocker.get("geometry") or {}).get("status") ==
          "unverified_absent", "geometry is not recorded as absent", problems)
    for key in ("sample_rate_hz", "channels", "frame_samples", "hop_samples",
                "state", "lookahead_samples", "output_scaling",
                "content_delay_samples"):
        check((blocker.get("geometry") or {}).get(key) is None,
              "geometry invents: " + key, problems)
    for key in ("pinned_revision", "source_digest", "weights_digest",
                "license_digest", "runtime_digest", "fixture_digest",
                "geometry_digest"):
        check(blocker.get(key) is None,
              "blocker has a fabricated digest: " + key, problems)
    check(blocker.get("no_upstream_parity_claim") is True,
          "upstream parity claim is not disabled", problems)
    rights = str(blocker.get("rights_requirement", "")).lower()
    for word in ("cc-by-nc", "non-commercial", "redistribution", "permission"):
        check(word in rights,
              "rights requirement omits: " + word, problems)
    not_attempted = " ".join(blocker.get("not_attempted", [])).lower()
    for phrase in ("clone", "license", "weights", "audio"):
        check(phrase in not_attempted,
              "not-attempted list omits: " + phrase, problems)
    check(bool(blocker.get("reopen")), "blocker has no reopen condition",
          problems)

    required = contract.get("required_artifacts", [])
    check(required == report.get("required_artifacts"),
          "contract and report required artifacts differ", problems)
    check(isinstance(required, list) and len(required) == 6,
          "contract does not carry six required artifacts", problems)
    if isinstance(required, list):
        check([row.get("id") for row in required] ==
              ["A1", "A2", "A3", "A4", "A5", "A6"],
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

    requirement = contract.get("artifact_requirement", {})
    check(requirement.get("status") == "unresolved",
          "artifact requirement is not unresolved", problems)
    for key in ("required_source", "required_weights", "required_runtime",
                "required_rights", "required_geometry", "required_fixture"):
        check(bool(requirement.get(key)),
              "artifact requirement omits: " + key, problems)
    unresolved = requirement.get("unresolved_fields", [])
    check(isinstance(unresolved, list) and len(unresolved) >= 15,
          "unresolved field set is too small", problems)
    for field in ("source_revision", "weights_artifact_sha256",
                  "runtime_version", "sample_rate_hz",
                  "content_delay_samples", "checkpoint_terms"):
        check(field in unresolved,
              "unresolved field missing: " + field, problems)

    gates = contract.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8,
          "contract does not carry eight release gates", problems)
    if isinstance(gates, list):
        check([gate.get("id") for gate in gates] == GATE_IDS,
              "contract gate ids mismatch", problems)
        check(all(gate.get("status") == "blocked" for gate in gates),
              "a contract release gate is not blocked", problems)
        check(all(gate.get("reason") for gate in gates),
              "a contract release gate lacks a reason", problems)
        check(all(gate.get("reopen") for gate in gates),
              "a contract release gate lacks a reopen condition", problems)
    check(contract.get("remaining_gates") == GATE_IDS,
          "contract remaining gates mismatch", problems)
    check(contract.get("geometry") == report.get("geometry"),
          "contract and report geometry differ", problems)
    check(contract.get("external_boundary") ==
          report.get("external_boundary"),
          "contract and report external boundary differ", problems)
    check(contract.get("asset_contract") == report.get("asset_contract"),
          "contract and report asset contract differ", problems)
    check(contract.get("external_boundary") == reference.EXTERNAL_BOUNDARY,
          "contract external boundary is not closed", problems)
    check(contract.get("asset_contract") == reference.ASSET_CONTRACT,
          "contract asset contract changed", problems)
    check(contract.get("profile") == report.get("profile"),
          "contract and report profile differ", problems)
    check(contract.get("profile", {}).get("source") ==
          reference.SOURCE_PINS[reference.PROFILE_SOURCE],
          "profile source pin mismatch", problems)

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
                       ("branch", "swarm/SDK-FACEBOOK-DENOISER-DNS64"),
                       ("base_commit", BASE_COMMIT),
                       ("verification_profile", "enhancement")):
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
    check(report.get("profile", {}).get("name") == "enhancement",
          "report profile is not enhancement", problems)

    reference_block = report.get("reference", {})
    for key in ("real_component_source_present",
                "model_weights_present",
                "eligible_runtime_present",
                "pinned_runtime_present", "matched_fixture_present",
                "license_text_present", "rights_approved",
                "candidate_geometry_verified", "upstream_parity",
                "downloads", "model_weights", "candidate_processing",
                "real_corpus_read"):
        check(reference_block.get(key) is False,
              "reference block claim is not false: " + key, problems)
    check(reference_block.get("synthetic_only") is True,
          "reference block is not synthetic-only", problems)
    check(reference_block.get("deterministic") is True,
          "reference block is not deterministic", problems)

    external = report.get("external_boundary", {})
    check(external == reference.EXTERNAL_BOUNDARY,
          "external boundary is not the declared closed boundary", problems)
    check(external.get("documented") is True,
          "external boundary is not documented", problems)
    check(external.get("license_reported") == "CC-BY-NC-4.0",
          "reported license mismatch", problems)
    check(external.get("host_target_approved") is False,
          "host target is claimed approved", problems)
    check(external.get("license_text_present") is False,
          "license text is claimed present", problems)
    check(external.get("commercial_use_approved") is False,
          "commercial use is claimed approved", problems)
    check(external.get("redistribution_approved") is False,
          "redistribution is claimed approved", problems)
    check(external.get("derived_output_approved") is False,
          "derived output is claimed approved", problems)
    check(external.get("source_present") is False,
          "source is claimed present", problems)
    check(external.get("weights_present") is False,
          "weights are claimed present", problems)
    check(external.get("local_runtime_present") is False,
          "local runtime is claimed present", problems)
    check(external.get("candidate_output_present") is False,
          "candidate output is claimed present", problems)
    check(external.get("adapter_implemented") is False,
          "an adapter is claimed implemented", problems)
    check(external.get("adapter_default_registration") is False,
          "adapter default registration is claimed", problems)
    check(external.get("automatic_discovery") is False,
          "automatic discovery is claimed", problems)
    check(external.get("fallback") == "none",
          "a fallback is claimed", problems)
    check(external.get("vendor_claims_separate_from_local_measurements")
          is True,
          "source claims are not separated from measurements", problems)

    source = report.get("source_probe", {})
    check(source.get("status") == "blocked_source_absent" and
          source.get("present") is False and source.get("found") == [],
          "source probe is not absent", problems)
    for key in ("revision", "tree_digest", "file_count", "license"):
        check(source.get(key) is None,
              "source probe has fabricated " + key, problems)
    weights = report.get("weights_probe", {})
    check(weights.get("status") == "blocked_weights_absent" and
          weights.get("present") is False and weights.get("found") == [],
          "weights probe is not absent", problems)
    check(weights.get("variant") == "dns64",
          "weights probe variant mismatch", problems)
    for key in ("artifact_path", "byte_count", "sha256", "checkpoint_terms"):
        check(weights.get(key) is None,
              "weights probe has fabricated " + key, problems)
    runtime = report.get("runtime_probe", {})
    check(runtime.get("status") == "blocked_runtime_unpinned" and
          runtime.get("pinned") is False and runtime.get("lockfiles") == [],
          "runtime probe is not absent/unpinned", problems)
    check(runtime.get("framework") is None and
          runtime.get("framework_version") is None and
          runtime.get("sha256") is None,
          "runtime probe has fabricated identity", problems)
    modules = runtime.get("modules", {})
    check(isinstance(modules, dict) and
          all(value is False for value in modules.values()),
          "a runtime module is unexpectedly present", problems)
    license_block = report.get("license_probe", {})
    check(license_block.get("status") ==
          "blocked_noncommercial_use_not_approved" and
          license_block.get("license_text_present") is False and
          license_block.get("commercial_use_approved") is False and
          license_block.get("noncommercial_use_approved") is False and
          license_block.get("redistribution_approved") is False and
          license_block.get("host_target_approved") is False,
          "license probe is not blocked", problems)
    check(license_block.get("license_text_sha256") is None,
          "license probe has a fabricated digest", problems)
    fixture = report.get("fixture_probe", {})
    check(fixture.get("status") == "blocked_matched_fixture_absent" and
          fixture.get("present") is False and fixture.get("found") == [],
          "fixture probe is not absent", problems)
    check(fixture.get("corpus_rights") is False and
          fixture.get("paired_clean_reference") is False and
          fixture.get("scorer_pinned") is False,
          "fixture probe overclaims rights or scoring", problems)
    rights = report.get("rights_probe", {})
    check(rights.get("status") == "blocked_rights_unrecorded" and
          rights.get("review") == "blocked" and
          rights.get("source_license") is None and
          rights.get("commercial_use_approved") is False and
          rights.get("input_corpus_rights") is False,
          "rights probe is not blocked", problems)

    geometry = report.get("geometry", {})
    check(geometry.get("target_variant") == "dns64",
          "geometry variant mismatch", problems)
    for key in ("documented_sample_rate_hz", "documented_channels",
                "documented_frame_samples", "documented_hop_samples",
                "documented_state", "documented_lookahead_samples",
                "documented_output_scaling",
                "documented_content_delay_samples",
                "v0_can_represent_declared_input"):
        check(geometry.get(key) is None,
              "geometry invents " + key, problems)
    check(geometry.get("candidate_geometry_in_pinned_sources") is False,
          "geometry claims a pinned candidate geometry", problems)
    check(geometry.get("verified_here") is False and
          geometry.get("measured_here") is False and
          geometry.get("candidate_output") is False,
          "geometry claims verification/measurement/output", problems)
    harness = geometry.get("local_harness_geometry", {})
    check(harness == {"channels": 1, "frame_samples": 160,
                      "sample_rate_hz": 16000, "installed_v0_only": True},
          "local harness geometry mismatch", problems)

    asset = report.get("asset_contract", {})
    check(asset == reference.ASSET_CONTRACT,
          "asset contract changed", problems)
    check(asset.get("loads_or_executes_artifact") is False and
          asset.get("hashes_caller_artifact") is False and
          asset.get("admits_without_rights_review") is False,
          "asset contract overclaims admission", problems)

    candidate = report.get("candidates", {}).get(reference.CANDIDATE, {})
    check(candidate.get("status") ==
          "blocked_source_weights_runtime_license_and_fixture_absent",
          "candidate status mismatch", problems)
    check(candidate.get("metrics") is None and
          candidate.get("result") is None and
          candidate.get("qualifies_candidate") is False,
          "candidate carries metrics or qualifies", problems)
    required = report.get("required_results", {})
    check(isinstance(required, dict) and required, "required results missing",
          problems)
    check(all(value.startswith("blocked_") or
              value.startswith("partial_")
              for value in required.values()),
          "a required result is not blocked/partial", problems)
    mapping = report.get("profile_mapping", {})
    check(isinstance(mapping, dict) and mapping, "profile mapping missing",
          problems)
    check(all(value.startswith("blocked_") or value.startswith("partial_")
              for value in mapping.values()),
          "a profile mapping item is not blocked/partial", problems)

    adverse = report.get("adverse", {})
    invalid = adverse.get("invalid_config_input_and_manifest", {})
    check(invalid.get("all_requests_rejected") is True,
          "invalid requests were accepted", problems)
    check(invalid.get("request_accepted_count") == 0,
          "invalid request accepted count is nonzero", problems)
    check(invalid.get("all_manifests_rejected") is True,
          "invalid manifests were accepted", problems)
    check(invalid.get("manifest_accepted_count") == 0,
          "invalid manifest accepted count is nonzero", problems)
    check(invalid.get("request_case_count", 0) >= 30,
          "request adverse set is too small", problems)
    check(invalid.get("manifest_case_count", 0) >= 20,
          "manifest adverse set is too small", problems)
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
    harness = stimuli.get("harness_geometry", {})
    check(harness.get("channels") == 1 and
          harness.get("frame_samples") == 160 and
          harness.get("sample_rate_hz") == 16000 and
          harness.get("candidate_geometry") is False and
          harness.get("installed_v0_only") is True,
          "harness geometry is overclaimed", problems)
    check(all(item.get("byte_identical") is True
              for item in stimuli.get("identity_control", {}).values()),
          "harness identity control is not bit exact", problems)

    paired = report.get("paired_harness_control", {})
    check(paired.get("candidate_processing") is False and
          paired.get("qualifies_candidate") is False,
          "paired harness control claims candidate processing", problems)
    check(paired.get("identity_output_equals_noisy") is True,
          "paired control identity relationship missing", problems)
    for key in ("identity_si_sdr_db", "snr_db"):
        value = paired.get(key)
        check(isinstance(value, (int, float)) and math.isfinite(value),
              "paired control metric is nonfinite: " + key, problems)
    shifts = paired.get("shift_si_sdr_db", {})
    check(set(shifts) == {"-8", "0", "8"},
          "paired shift probe set mismatch", problems)
    check(all(math.isfinite(value) for value in shifts.values()),
          "paired shift metric is nonfinite", problems)

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
    check(len(rows) == 1, "linked task row is missing or duplicated",
          problems)
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
    blob = (REPORT_PATH.read_text(encoding="utf-8") +
            CONTRACT_PATH.read_text(encoding="utf-8") +
            SOURCES_PATH.read_text(encoding="utf-8"))
    check("audio-benchmark-platform/plan/swarm/TASKS.json" not in blob,
          "the full mutable board path appears in a canonical artifact",
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
            if path.suffix == ".py":
                for number, line in enumerate(text.splitlines(), 1):
                    if SPDX_NEEDLE in line:
                        check(line.lstrip().startswith("#"),
                              "SPDX identifier outside a comment: " +
                              name + ":" + str(number), problems)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    # REUSE-IgnoreStart
    reuse_token = 'SPDX-License-Identifier = "Apache-2.0"'
    # REUSE-IgnoreEnd
    check('"docs/**"' in reuse and reuse_token in reuse,
          "REUSE docs coverage is missing", problems)
    for path in HERE.iterdir():
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES or
              path.name.endswith(".sha256"),
              "prohibited binary/audio/model artifact: " + path.name,
              problems)
        check(not path.is_symlink(), "task symlink: " + path.name, problems)
        check(path.name not in {"CMakeLists.txt", "provider.json",
                                "adapter.json"},
              "provider artifact: " + path.name, problems)
        check(not (path.is_file() and path.name.startswith("LICENSE")),
              "vendored license file: " + path.name, problems)


def check_absence_live(problems: List[str]) -> None:
    source = reference.source_probe()
    check(source.get("present") is False,
          "Facebook Denoiser source appeared; revisit the blocker package",
          problems)
    weights = reference.weights_probe()
    check(weights.get("present") is False,
          "a DNS64 weight appeared; revisit the blocker package", problems)
    license_block = reference.license_probe()
    check(license_block.get("commercial_use_approved") is False,
          "commercial use is no longer blocked", problems)
    check(license_block.get("license_text_present") is False,
          "a license text appeared; revisit the blocker package", problems)
    runtime = reference.runtime_probe()
    check(runtime.get("pinned") is False,
          "a pinned runtime appeared; revisit the blocker package", problems)
    fixture = reference.fixture_probe()
    check(fixture.get("present") is False,
          "a matched paired cohort appeared; revisit the blocker package",
          problems)
    rights = reference.rights_probe()
    check(rights.get("review") == "blocked",
          "rights review is no longer blocked", problems)


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
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-FACEBOOK-DENOISER-DNS64"
    target = sdk / "docs/task-evidence/facebook-denoiser-dns64"
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
            prefix="sdk-facebook-denoiser-cold-") as temporary:
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


def _git(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *arguments], cwd=str(SDK_ROOT),
                          capture_output=True, text=True, check=False)


def check_git_scope(problems: List[str]) -> List[str]:
    process = _git("status", "--porcelain=v1", "--untracked-files=all")
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
    diff = _git("diff", "--check")
    check(diff.returncode == 0 and not diff.stdout.strip(),
          "git diff --check failed: " + diff.stdout.strip(), problems)

    base_process = _git("merge-base", "HEAD", "origin/main")
    base = base_process.stdout.strip()
    if base_process.returncode != 0 or not base:
        fallback = _git("merge-base", "HEAD", "main")
        base = fallback.stdout.strip()
        if fallback.returncode != 0 or not base:
            problems.append("scope_base_unavailable")
            base = ""
    if base:
        committed = _git("diff", "--name-only", "--diff-filter=ACMRD",
                         base + "..HEAD")
        if committed.returncode != 0:
            problems.append("committed scope diff failed")
        else:
            for path in committed.stdout.splitlines():
                if not path.strip():
                    continue
                check(path.startswith(TASK_PREFIX),
                      "base_out_of_scope_change: " + path, problems)
        committed_check = _git("diff", "--check", base + "..HEAD")
        check(committed_check.returncode == 0 and
              not committed_check.stdout.strip(),
              "committed git diff --check failed: " +
              committed_check.stdout.strip(), problems)

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
          "byte_identical=true profile=enhancement "
          "status=proposal_only_not_qualified decision=DEFER "
          "qualification=not_qualified gates_blocked=8 "
          "report_sha256=" + digest + " changed_files=" + str(len(changed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
