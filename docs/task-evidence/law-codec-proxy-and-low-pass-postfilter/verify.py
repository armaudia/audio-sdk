# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the law-codec-proxy evidence package.

It checks strict JSON, canonical bytes, exact pins, blocker semantics, stable
linked-row identity, licensing, prohibited artifacts, task-local git scope and
three cold-start byte-identical regenerations. It never writes package
evidence.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List, Tuple

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_PREFIX = reference.TASK_PREFIX
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
TASK_ID = reference.TASK
COMPONENT = reference.COMPONENT
BASE_COMMIT = reference.BASE_COMMIT
GATE_IDS = reference.GATE_IDS

ARTIFACT_FILES = (
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
REPORT_ARTIFACT_FILES = reference.REPORT_ARTIFACT_FILES
CONTRACT_ARTIFACT_FILES = tuple(
    name for name in ARTIFACT_FILES if name not in ("contract.json",))
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
PROHIBITED_SUFFIXES = reference.PROHIBITED_SUFFIXES
BLOCKER_KEYS = {
    "status", "artifact", "source", "codec_reference", "runtime", "corpus",
    "rights_requirement", "expected_license", "pinned_revision",
    "source_digest", "runtime_digest", "codec_conformance_vectors",
    "pilot_numbers_are_provenance_only", "no_upstream_parity_claim",
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
        return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as error:
        raise VerificationError("invalid JSON in " + path.name + ": " +
                                str(error))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True).encode("utf-8")


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
    check(contract.get("task") == TASK_ID, "contract task mismatch", problems)
    check(contract.get("component") == COMPONENT,
          "contract component mismatch", problems)
    check(contract.get("title") == "\u00b5-law codec proxy and low-pass "
                                   "postfilter",
          "contract title mismatch", problems)
    check(contract.get("branch") == reference.BRANCH,
          "contract branch mismatch", problems)
    check(contract.get("base_commit") == BASE_COMMIT,
          "contract base commit mismatch", problems)
    check(contract.get("decision") == "DEFER", "contract decision is not DEFER",
          problems)
    check(contract.get("status") == "proposal_only_incomplete",
          "contract status is not proposal_only_incomplete", problems)
    check(contract.get("comparison_status") ==
          "blocked_exact_codec_reference_runtime_corpus_and_rights_absent",
          "contract comparison status mismatch", problems)
    qualification = contract.get("qualification", {})
    check(qualification == reference.qualification(),
          "contract qualification mismatch", problems)
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
    for flag in ("public_api_abi_changed", "provider_registered",
                 "descriptor_registration", "enabled_by_default",
                 "shared_cmake_changed", "ci_changed",
                 "board_or_handoff_changed", "real_corpus_or_weights",
                 "real_codec_media_read", "benchmark_claim", "release_claim",
                 "listening_result", "device_timing_measured"):
        check(boundary.get(flag) is False, "boundary flag is not false: " +
              flag, problems)
    check(boundary.get("format") == {
        "sample_rate_hz": 16000, "channels": 1,
        "sample_format": "float32", "frame_samples": 160,
    }, "contract v0 format mismatch", problems)
    blocker = contract.get("upstream_blocker", {})
    check(set(blocker) == BLOCKER_KEYS, "upstream blocker schema mismatch",
          problems)
    check(blocker.get("status") ==
          "blocked_exact_codec_reference_runtime_corpus_and_rights_absent",
          "upstream blocker status mismatch", problems)
    check((blocker.get("source") or {}).get("status") == "present_pinned",
          "source is not recorded as present and pinned", problems)
    check((blocker.get("source") or {}).get("real_codec") is False,
          "source is recorded as a real codec", problems)
    check((blocker.get("source") or {}).get("license") == "not_recorded",
          "source licence is not recorded as absent", problems)
    codec = blocker.get("codec_reference") or {}
    check(codec.get("status") == "absent" and codec.get("g711") is False and
          codec.get("real_transport_codec") is False,
          "codec reference is not absent", problems)
    check(codec.get("sha256") is None and codec.get("byte_count") is None,
          "codec reference has fabricated identity", problems)
    runtime = blocker.get("runtime") or {}
    check(runtime.get("status") == "unpinned_not_admitted" and
          runtime.get("pinned") is False and
          runtime.get("admitted") is False,
          "runtime is not absent/unpinned", problems)
    check(runtime.get("runtime_digest") is None and
          runtime.get("wheel_digests") is False,
          "runtime has fabricated identity", problems)
    corpus = blocker.get("corpus") or {}
    check(corpus.get("status") == "absent" and corpus.get("present") is False and
          corpus.get("rights_cleared") is False,
          "corpus is not absent/uncleared", problems)
    check(blocker.get("pinned_revision") is None and
          blocker.get("source_digest") is None and
          blocker.get("runtime_digest") is None,
          "blocker has a fabricated top-level pin", problems)
    check(blocker.get("codec_conformance_vectors", {}).get("status") ==
          "absent", "conformance vectors are not absent", problems)
    check(blocker.get("pilot_numbers_are_provenance_only") is True,
          "pilot numbers are not provenance only", problems)
    check(blocker.get("no_upstream_parity_claim") is True,
          "upstream parity claim is not disabled", problems)
    check("consent" in str(blocker.get("rights_requirement")).lower(),
          "rights requirement does not mention consent", problems)
    check("redistribution" in str(blocker.get("rights_requirement")).lower(),
          "rights requirement does not mention redistribution", problems)
    gates = contract.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8,
          "contract does not carry eight release gates", problems)
    if isinstance(gates, list):
        check([gate.get("id") for gate in gates] == GATE_IDS,
              "contract gate ids mismatch", problems)
        check(all(gate.get("status") == "blocked" for gate in gates),
              "a contract release gate is not blocked", problems)
        check(all(gate.get("reason") and gate.get("reopen")
                  for gate in gates),
              "a contract gate lacks reason/reopen", problems)
    check(contract.get("geometry") == report.get("geometry"),
          "contract and report geometry differ", problems)
    check(contract.get("codec_boundary") == report.get("codec_boundary"),
          "contract and report codec boundary differ", problems)
    check(contract.get("evidence_entry") == report.get("evidence_entry"),
          "contract and report evidence entry differ", problems)
    check(contract.get("inventory_link") == report.get("inventory_link"),
          "contract and report inventory link differ", problems)
    check(set(contract.get("local_files", [])) == set(ARTIFACT_FILES),
          "contract local file list mismatch", problems)


REFERENCE_CONTRACT_FILES = tuple(ARTIFACT_FILES)


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") == reference.SCHEMA_ID,
          "report schema mismatch", problems)
    check(report.get("task") == TASK_ID, "report task mismatch", problems)
    check(report.get("component") == COMPONENT,
          "report component mismatch", problems)
    check(report.get("branch") == reference.BRANCH,
          "report branch mismatch", problems)
    check(report.get("base_commit") == BASE_COMMIT,
          "report base commit mismatch", problems)
    check(report.get("decision") == "DEFER", "report decision is not DEFER",
          problems)
    check(report.get("status") == "proposal_only_incomplete",
          "report status is not proposal_only_incomplete", problems)
    check(report.get("qualification_status") == "not_qualified",
          "report qualification_status mismatch", problems)
    qualification = report.get("qualification", {})
    check(qualification == reference.qualification(),
          "report qualification mismatch", problems)
    check(qualification.get("status") == "not_qualified" and
          qualification.get("candidate_qualified") is False and
          qualification.get("readiness") == "incomplete" and
          qualification.get("proposal_only") is True,
          "report qualification is not incomplete/not_qualified", problems)
    check(report.get("profile", {}).get("name") == "restoration",
          "report profile is not restoration", problems)
    check(len(report.get("profile_mapping", [])) == 4,
          "profile mapping is incomplete", problems)
    ref = report.get("reference", {})
    check(ref.get("pilot_source_present") is True,
          "report does not record the pinned pilot source", problems)
    for flag in ("pilot_runtime_admitted", "pilot_corpus_present",
                 "real_codec_reference_present",
                 "real_codec_runtime_present", "candidate_processing",
                 "real_corpus_read", "real_media_read", "downloads",
                 "upstream_parity", "pilot_numeric_parity", "frame_causal"):
        check(ref.get(flag) is False, "reference flag is not false: " + flag,
              problems)
    for flag in ("synthetic_only", "deterministic", "offline_only"):
        check(ref.get(flag) is True, "reference flag is not true: " + flag,
              problems)
    codec = report.get("codec_boundary", {})
    check(codec.get("is_g711_ulaw") is False,
          "report claims G.711 mu-law", problems)
    check(codec.get("is_real_transport_codec") is False,
          "report claims a real transport codec", problems)
    check(codec.get("keep_proxy_separate") is True,
          "report does not keep the proxy separate", problems)
    source = report.get("source_probe", {})
    check(source.get("status") == "present_pinned" and
          source.get("present") is True and source.get("verified") is True,
          "source probe is not present/pinned", problems)
    check(source.get("file_count") == len(reference.SOURCE_PINS),
          "source probe file count mismatch", problems)
    check(source.get("pilot_source_license") == "not_recorded",
          "source probe invents a licence", problems)
    for item in source.get("files", []):
        check(item.get("present") is True and item.get("matches_pin") is True,
              "source probe file is missing or changed: " +
              str(item.get("path")), problems)
    runtime = report.get("runtime_probe", {})
    check(runtime.get("status") == "unpinned_not_admitted" and
          runtime.get("pinned") is False and
          runtime.get("runtime_digest") is None,
          "runtime probe is not absent/unpinned", problems)
    check(runtime.get("unpinned_venv", {}).get("admitted") is False and
          runtime.get("unpinned_venv", {}).get(
              "wheel_digests_recorded") is False,
          "unpinned venv is admitted or has fabricated wheel digests",
          problems)
    check(runtime.get("audioop_policy") ==
          "not_admitted_deprecated_removed_in_python_3_13",
          "audioop is admitted as a codec reference", problems)
    check(runtime.get("admitted_modules") == [],
          "a runtime module is admitted", problems)
    check(runtime.get("live_interpreter_probe", "").startswith(
        "not embedded"), "runtime probe embeds a live interpreter", problems)
    check(runtime.get("downloads") is False and
          runtime.get("network_used") is False,
          "runtime probe records a download/network use", problems)
    corpus = report.get("corpus_probe", {})
    check(corpus.get("status") == "absent" and
          corpus.get("present") is False,
          "corpus is not absent", problems)
    check(corpus.get("real_audio_read") is False and
          corpus.get("media_read") is False and
          corpus.get("downloads") is False,
          "corpus probe claims a read", problems)
    check(corpus.get("frozen_pilot_clip_count") == 12,
          "frozen pilot clip count mismatch", problems)
    rights = report.get("rights_probe", {})
    check(rights.get("status") == "absent" and
          rights.get("entry_present") is False and
          rights.get("blocked") is True,
          "rights are not absent/blocked", problems)
    check(rights.get("consent") == "not_recorded",
          "rights probe invents consent", problems)
    codec_probe = report.get("codec_reference_probe", {})
    check(codec_probe.get("status") == "absent" and
          codec_probe.get("licensed_reference_present") is False and
          codec_probe.get("g711_reference_present") is False and
          codec_probe.get("admitted") is False,
          "codec reference probe is not absent", problems)
    check(codec_probe.get("conformance_vectors", {}).get("sha256") is None and
          codec_probe.get("conformance_vectors", {}).get("byte_count") is None,
          "codec conformance vectors have fabricated identity", problems)
    geometry = report.get("geometry", {})
    check(geometry.get("proxy_sample_rate_hz") == 8000,
          "proxy sample rate mismatch", problems)
    check(geometry.get("masking_companding_bits") == [4, 8],
          "proxy bits mismatch", problems)
    check(geometry.get("is_itu_t_g711") is False,
          "geometry claims G.711", problems)
    check(geometry.get("global_peak_normalisation") is True,
          "global peak normalisation is not recorded", problems)
    check(geometry.get("postfilter", {}).get("cutoff_hz") == 3900.0 and
          geometry.get("postfilter", {}).get("frame_causal") is False,
          "postfilter geometry mismatch", problems)
    resampler = geometry.get("resampler", {})
    check(resampler.get("admitted_ratios") == [[1, 2], [2, 1]],
          "resampler admitted ratios mismatch", problems)
    check(resampler.get("taps_formula") == "2 * 10 * max(up, down) + 1",
          "resampler tap formula mismatch", problems)
    check(resampler.get("taps_per_direction") == reference.RESAMPLE_TAPS == 41,
          "resampler declared taps disagree with the implemented formula",
          problems)
    check(resampler.get("composite_cascade_taps") ==
          reference.RESAMPLE_COMPOSITE_TAPS ==
          2 * reference.RESAMPLE_TAPS - 1,
          "resampler composite cascade taps mismatch", problems)
    check("taps" not in resampler and "up" not in resampler and
          "down" not in resampler,
          "resampler still reports ambiguous up/down/taps fields", problems)
    check((2, 2) not in reference.RESAMPLE_ADMITTED_RATIOS,
          "resampler admits the non-admitted (2, 2) ratio", problems)
    for up, down in reference.RESAMPLE_ADMITTED_RATIOS:
        taps = reference.resampler_tap_count(up, down)
        check(taps == resampler.get("taps_per_direction"),
              "declared taps do not match the implemented formula for " +
              "ratio " + str((up, down)), problems)
        coefficients = reference._firwin_lowpass(
            taps, 1.0 / max(up, down), reference.RESAMPLE_KAISER_BETA)
        check(len(coefficients) == resampler.get("taps_per_direction"),
              "implemented coefficient count does not match the declared " +
              "taps for ratio " + str((up, down)), problems)
    check(geometry.get("streaming_ready") is False,
          "geometry claims streaming readiness", problems)
    check(geometry.get("measured_here") is False,
          "geometry claims local measurement", problems)
    pilot = report.get("pilot_evidence", {})
    check(pilot.get("sha256") == reference.SOURCE_PINS[
        "reports/distortion-restoration/20261028-synthetic-screen.json"],
        "pilot report digest mismatch", problems)
    check(pilot.get("provenance_only") is True and
          pilot.get("reproduced_here") is False and
          pilot.get("qualifies_candidate") is False,
          "pilot evidence is claimed as reproduced/qualified", problems)
    for key, expected in reference.PILOT_CONDITIONS.items():
        observed = pilot.get("conditions", {}).get(key, {})
        check(observed.get("decoded_input") == expected["decoded_input"],
              "pilot decoded row mismatch: " + key, problems)
        check(observed.get("lowpass_decoder_postfilter") ==
              expected["lowpass_decoder_postfilter"],
              "pilot postfilter row mismatch: " + key, problems)
    fixture = report.get("fixture", {})
    check(fixture.get("results_role") ==
          "synthetic_fixture_control_not_qualifying",
          "fixture result role mismatch", problems)
    check(fixture.get("pilot_numeric_parity") is False,
          "fixture claims pilot numeric parity", problems)
    check(fixture.get("all_finite") is True and
          fixture.get("peak_bounded") is True,
          "fixture is not finite/peak bounded", problems)
    control = fixture.get("identity_control", {})
    check(control.get("decoded_bit_exact") is True and
          control.get("filtered_bit_exact") is False,
          "identity/filter control mismatch", problems)
    check(control.get("postfilter_max_abs_change", 0.0) > 0.0,
          "postfilter is unexpectedly identity", problems)
    conditions = fixture.get("conditions", {})
    check(set(conditions) == {"4bit", "8bit"},
          "fixture condition set mismatch", problems)
    for name, condition in conditions.items():
        check(condition.get("finite") is True and
              condition.get("peak_bounded") is True,
              "fixture condition is not finite/bounded: " + name, problems)
        for method in ("decoded_input", "lowpass_postfilter"):
            block = condition.get(method, {})
            check(block.get("stoi") is None and
                  block.get("stoi_status") ==
                  "not_computed_runtime_absent",
                  "fixture fabricates STOI: " + name + "/" + method, problems)
            check(isinstance(block.get("si_sdr_db"), (int, float)) or
                  block.get("si_sdr_perfect") is True,
                  "fixture metric is missing: " + name + "/" + method,
                  problems)
    check(conditions.get("4bit", {}).get("delta_si_sdr_db", 0.0) > 0.0,
          "4-bit fixture trend does not match the pilot sign", problems)
    check(conditions.get("8bit", {}).get("delta_si_sdr_db", 0.0) < 0.0,
          "8-bit fixture trend does not match the pilot sign", problems)
    adverse = report.get("adverse", {})
    invalid = adverse.get("invalid_config_and_input", {})
    check(invalid.get("all_rejected") is True and
          invalid.get("accepted_count") == 0,
          "an invalid frame request was accepted", problems)
    check(invalid.get("case_count", 0) >= 20,
          "invalid request coverage is too small", problems)
    json_adverse = adverse.get("invalid_json_numeric_fields", {})
    check(json_adverse.get("all_rejected") is True and
          json_adverse.get("accepted_count") == 0,
          "invalid JSON was accepted", problems)
    lifecycle = adverse.get("session_lifecycle", {})
    check(lifecycle.get("matches_expectation") is True and
          lifecycle.get("rejection_count") == 7,
          "session lifecycle expectation mismatch", problems)
    missing = adverse.get("missing_result", {})
    check(missing.get("status") == "blocked" and
          missing.get("metrics") is None and
          missing.get("qualifies_candidate") is False,
          "missing result carries metrics or qualifies", problems)
    required = report.get("required_results", {})
    check(isinstance(required, dict) and required, "required results missing",
          problems)
    check(all(value not in ("passed", "qualified")
              for value in required.values()),
          "a required result is marked passed/qualified", problems)
    checks = report.get("local_harness_checks", {})
    check(all(value is True for value in checks.values()),
          "a local harness check is not true", problems)
    check(len(checks) >= 20, "local harness check set is too small", problems)
    summary = report.get("harness_summary", {})
    check(summary.get("all_true") is True and
          summary.get("check_count") == len(checks),
          "harness summary mismatch", problems)
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
          "remaining gates mismatch", problems)
    check(report.get("no_missing_result_qualifies_candidate") is True,
          "missing-result guard is not enabled", problems)
    check(report.get("regression_count") == 0 and
          report.get("regressions") == [],
          "regression fields are not empty", problems)


def check_pins(contract: Dict[str, Any], report: Dict[str, Any],
               problems: List[str]) -> int:
    pins = contract.get("artifact_pins", {})
    check(set(pins) == set(CONTRACT_ARTIFACT_FILES),
          "contract artifact pin set mismatch", problems)
    for name, digest in pins.items():
        path = HERE / name
        check(path.is_file(), "missing artifact: " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest,
                  "artifact pin mismatch: " + name, problems)
    report_pins = report.get("artifact_pins", {})
    check(set(report_pins) == set(REPORT_ARTIFACT_FILES),
          "report artifact pin set mismatch", problems)
    for name, digest in report_pins.items():
        path = HERE / name
        check(path.is_file(), "missing report artifact: " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest,
                  "report artifact pin mismatch: " + name, problems)
    check(pins.get("report.json") == sha256_file(REPORT_PATH),
          "report.json pin does not match bytes", problems)
    sidecar = SIDECAR_PATH.read_text(encoding="ascii")
    expected_sidecar = (sha256_file(REPORT_PATH) + "  report.json\n")
    check(sidecar == expected_sidecar, "report SHA-256 sidecar mismatch",
          problems)
    canonical = contract.get("canonical_report", {})
    check(canonical.get("file_sha256") == sha256_file(REPORT_PATH),
          "canonical report file digest mismatch", problems)
    check(canonical.get("sidecar_sha256") == sha256_file(SIDECAR_PATH),
          "canonical sidecar digest mismatch", problems)
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
    check(not any(line.rstrip().endswith("plan/swarm/TASKS.json")
                  for line in sources.splitlines()),
          "mutable TASKS.json is pinned in SOURCES.sha256", problems)
    for path, digest in report.get("source_pins", {}).items():
        check((digest + "  source:" + path) in sources,
              "source pin missing from SOURCES.sha256: " + path, problems)
    for path, digest in report.get("boundary_pins", {}).items():
        check((digest + "  " + path) in sources,
              "boundary pin missing from SOURCES.sha256: " + path, problems)
    for name in ARTIFACT_FILES:
        if name in ("contract.json", "SOURCES.sha256"):
            continue
        if (HERE / name).is_file():
            check((sha256_file(HERE / name) + "  " + TASK_PREFIX + name)
                  in sources,
                  "manifest pin missing from SOURCES.sha256: " + name,
                  problems)
    return len(pins) + len(report_pins) + len(
        report.get("source_pins", {})) + len(report.get("boundary_pins", {}))


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
    check(stable == reference.EXPECTED_LINK,
          "stable linked-row identity changed", problems)
    check(report.get("board_links") == [stable],
          "report board projection mismatch", problems)
    check(report.get("board_link_fields") == list(reference.LINK_FIELDS),
          "board link fields mismatch", problems)
    expected = sha256_bytes(canonical_bytes([stable]))
    check(report.get("board_link_projection_sha256") == expected,
          "board projection digest mismatch", problems)
    check(contract.get("board_links") == [stable] and
          contract.get("board_link_projection_sha256") == expected,
          "contract board projection mismatch", problems)
    for mutable in reference.MUTABLE_FIELDS_EXCLUDED:
        check(mutable in report.get("board_mutable_fields_excluded", []),
              "mutable board field not excluded: " + mutable, problems)


def check_inventory(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("inventory_link") == reference.EXPECTED_INVENTORY,
          "inventory link mismatch", problems)
    entry = report.get("evidence_entry", {})
    check(entry.get("line") == 423, "evidence line mismatch", problems)
    check(entry.get("inventory_row_has_explicit_line") is False,
          "inventory evidence line claim mismatch", problems)
    for token in reference.EVIDENCE_TOKENS:
        check(token in str(entry.get("text")),
              "evidence token missing: " + token, problems)


def check_licensing(problems: List[str]) -> None:
    for name in SIDECAR_FILES:
        path = HERE / name
        check(path.is_file(), "missing SPDX sidecar: " + name, problems)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        check("SPDX-FileCopyrightText:" in text,
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
    for path in HERE.iterdir():
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES or
              path.name.endswith(".sha256"),
              "prohibited binary/audio artifact: " + path.name, problems)
        check(not re.match(r"^(.*\.pth|.*\.onnx|.*\.safetensors)$",
                           path.name),
              "prohibited model artifact: " + path.name, problems)


def check_absent(problems: List[str]) -> None:
    source = reference.source_probe()
    check(source.get("verified") is True,
          "pinned pilot source changed or disappeared", problems)
    codec = reference.codec_reference_probe()
    check(codec.get("status") == "absent" and
          codec.get("admitted") is False,
          "a licensed codec reference appeared; revisit the blocker package",
          problems)
    corpus = reference.corpus_probe()
    check(corpus.get("present") is False,
          "a corpus appeared; revisit the blocker package", problems)
    rights = reference.rights_probe()
    check(rights.get("entry_present") is False,
          "a rights entry appeared; revisit the blocker package", problems)
    report = strict_load(REPORT_PATH)
    runtime = reference.runtime_probe()
    check(runtime.get("pinned") is False,
          "a pinned runtime appeared; revisit the blocker package", problems)
    check(report.get("runtime_probe", {}).get("unpinned_venv", {}).get(
        "admitted") is False,
        "an unpinned runtime became admitted", problems)


def check_reproduction(report_payload: bytes,
                       problems: List[str]) -> bool:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--stdout-report"],
        cwd=str(HERE), capture_output=True, env=environment, check=False)
    if process.returncode != 0:
        problems.append("in-process report regeneration failed")
        return False
    check(process.stdout == report_payload, "in-process report bytes differ",
          problems)
    return process.stdout == report_payload


def check_cold_starts(problems: List[str]) -> int:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    outputs: List[bytes] = []
    for _index in range(3):
        process = subprocess.run(
            [sys.executable, str(HERE / "run.py"), "--verify-repro"],
            cwd=str(HERE), capture_output=True, env=environment, check=False)
        if process.returncode != 0:
            problems.append("cold-start regeneration failed: " +
                            process.stdout.decode("utf-8", "replace") +
                            process.stderr.decode("utf-8", "replace"))
            continue
        outputs.append(process.stdout)
    check(len(outputs) == 3, "fewer than three cold starts succeeded",
          problems)
    if outputs:
        check(all(output == outputs[0] for output in outputs),
              "cold-start outputs differ", problems)
        check(b"ok=1\n" in outputs[0], "cold-start reproduction is not ok",
              problems)
    return len(outputs)


def check_git_scope(problems: List[str]) -> None:
    process = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=str(SDK_ROOT), capture_output=True, text=True, check=False)
    if process.returncode != 0:
        problems.append("git status failed in the SDK worktree")
        return
    for line in process.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        check(path.startswith(TASK_PREFIX),
              "change outside task-local scope: " + path, problems)
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        problems.append("scope_base_unavailable")
        return
    try:
        paths = reference.scope_changed_paths(SDK_ROOT, base)
    except reference.EvidenceError as error:
        problems.append(str(error))
        return
    for path in reference.scope_violations(paths):
        problems.append("base_out_of_scope_change: " + path)


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
        check_contract(contract, report, problems)
        pins_checked = check_pins(contract, report, problems)
        check_report(report, problems)
        check_board(contract, report, problems)
        check_inventory(report, problems)
        check_licensing(problems)
        check_absent(problems)
        reproduction_ok = check_reproduction(report_payload, problems)
        repeats = check_cold_starts(problems)
        check_git_scope(problems)
        check(report_payload.endswith(b"\n") and
              not report_payload.endswith(b"\n\n"),
              "report must have exactly one trailing newline", problems)
        check(finite_json(report), "report contains a nonfinite value",
              problems)
        check(finite_json(contract), "contract contains a nonfinite value",
              problems)
        check(canonical_bytes(report) + b"\n" == report_payload,
              "report bytes are not canonical", problems)
        check(canonical_bytes(contract) + b"\n" ==
              CONTRACT_PATH.read_bytes(), "contract bytes are not canonical",
              problems)
    except (OSError, VerificationError, ValueError, KeyError,
            TypeError) as error:
        problems.append("verification exception: " + str(error))
        reproduction_ok = False
        repeats = 0
        pins_checked = 0
    if problems:
        for problem in problems:
            print("FAIL: " + problem)
        print("verification_failed=" + str(len(problems)))
        return 1
    print("pins_ok=" + str(pins_checked) +
          " reproduction_ok=" + str(int(reproduction_ok)) +
          " repeats_ok=" + str(repeats) +
          " semantics_ok=1 boundary_ok=1 licensing_ok=1 "
          "git_scope_ok=1 absent_source_weights_ok=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
