# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the ContentVec evidence package.

It checks strict JSON, canonical bytes, exact pins, blocker semantics, stable
linked-row identity, licensing, prohibited artifacts, task-local git scope and
three cold-start byte-identical regenerations. It never writes package evidence.
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

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_PREFIX = "docs/task-evidence/contentvec/"
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
TASK_ID = "SDK-CONTENTVEC"
COMPONENT = "contentvec"
BASE_COMMIT = "6967a728b5c4048fb01ed4522a76a6906fbcffe2"
GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]
EXPECTED_LINK = {
    "task_id": TASK_ID,
    "title": "ContentVec",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
ARTIFACT_FILES = (
    "README.md",
    "LICENSES.md",
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
    ".tar", ".gz", ".whl", ".npz",
}
BLOCKER_KEYS = {
    "status", "artifact", "source", "weights", "runtime", "expected_license",
    "pinned_revision", "source_digest", "runtime_digest",
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
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


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
    check(contract.get("schema_id") == "audio-sdk/contentvec-contract/0.1",
          "contract schema mismatch", problems)
    check(contract.get("contract_version") == "0.1",
          "contract version mismatch", problems)
    check(contract.get("task") == TASK_ID, "contract task mismatch", problems)
    check(contract.get("component") == COMPONENT,
          "contract component mismatch", problems)
    check(contract.get("branch") == "swarm/SDK-CONTENTVEC",
          "contract branch mismatch", problems)
    check(contract.get("base_commit") == BASE_COMMIT,
          "contract base commit mismatch", problems)
    check(contract.get("decision") == "DEFER", "contract decision is not DEFER",
          problems)
    check(contract.get("status") == "proposal_only_not_qualified",
          "contract status is not proposal_only_not_qualified", problems)
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
    check(contract.get("comparison_status") ==
          "blocked_weights_and_runtime_absent",
          "contract comparison status mismatch", problems)
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
    check(blocker.get("status") == "blocked_weights_and_runtime_absent",
          "upstream blocker status mismatch", problems)
    source = blocker.get("source") or {}
    check(source.get("status") ==
          "consumer_present_pinned_upstream_source_absent",
          "consumer source is not recorded as present and pinned", problems)
    check(source.get("license") == "MIT",
          "consumer source licence is not recorded as MIT", problems)
    check(source.get("upstream_source_present") is False,
          "upstream ContentVec source is unexpectedly recorded present",
          problems)
    check(source.get("config_present") is True,
          "ContentVec config is not recorded present", problems)
    weights = blocker.get("weights") or {}
    check(weights.get("status") == "absent",
          "weights are not recorded as absent", problems)
    check(weights.get("sha256") is None,
          "blocker has a fabricated weight digest", problems)
    check(weights.get("byte_count") is None,
          "blocker has a fabricated weight byte count", problems)
    check(weights.get("expected_hidden_size") == 768,
          "blocker hidden size mismatch", problems)
    check(weights.get("expected_layer_count") == 12,
          "blocker layer count mismatch", problems)
    check(weights.get("expected_frame_stride_samples") == 320,
          "blocker stride mismatch", problems)
    check((blocker.get("runtime") or {}).get("status") == "absent_unpinned",
          "runtime is not recorded as absent", problems)
    check(blocker.get("runtime_digest") is None,
          "blocker has a fabricated runtime digest", problems)
    check(blocker.get("no_upstream_parity_claim") is True,
          "upstream parity claim is not disabled", problems)
    check("MIT" in str(blocker.get("expected_license")),
          "consumer licence is not recorded as MIT", problems)
    rights = str(blocker.get("rights_requirement")).lower()
    check("weight" in rights and "consent" in rights,
          "rights requirement does not cover weight terms and consent",
          problems)
    gates = contract.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8,
          "contract does not carry eight release gates", problems)
    if isinstance(gates, list):
        check([gate.get("id") for gate in gates] == GATE_IDS,
              "contract gate ids mismatch", problems)
        check(all(gate.get("status") == "blocked" for gate in gates),
              "a contract release gate is not blocked", problems)
    check(contract.get("geometry") == report.get("geometry"),
          "contract and report geometry differ", problems)


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") ==
          "audio-sdk/contentvec-reference-report/0.1",
          "report schema mismatch", problems)
    check(report.get("task") == TASK_ID, "report task mismatch", problems)
    check(report.get("component") == COMPONENT, "report component mismatch",
          problems)
    check(report.get("branch") == "swarm/SDK-CONTENTVEC",
          "report branch mismatch", problems)
    check(report.get("base_commit") == BASE_COMMIT,
          "report base commit mismatch", problems)
    check(report.get("decision") == "DEFER", "report decision is not DEFER",
          problems)
    check(report.get("status") == "proposal_only_not_qualified",
          "report status is not proposal_only_not_qualified", problems)
    check(report.get("qualification_status") == "not_qualified",
          "report qualification_status mismatch", problems)
    qualification = report.get("qualification", {})
    check(qualification.get("status") == "not_qualified" and
          qualification.get("candidate_qualified") is False and
          qualification.get("readiness") == "incomplete",
          "report qualification is not incomplete/not_qualified", problems)
    check(report.get("profile", {}).get("name") == "voice",
          "report profile is not voice", problems)
    reference_block = report.get("reference", {})
    check(reference_block.get("real_consumer_source_present") is True,
          "report does not record the pinned consumer source", problems)
    check(reference_block.get("real_contentvec_config_present") is True,
          "report does not record the pinned ContentVec config", problems)
    check(reference_block.get("real_contentvec_weights_present") is False,
          "report claims ContentVec weights are present", problems)
    check(reference_block.get("pinned_runtime_present") is False,
          "report claims a pinned runtime", problems)
    check(reference_block.get("candidate_processing") is False,
          "report claims candidate processing", problems)
    check(reference_block.get("real_corpus_read") is False,
          "report claims real corpus was read", problems)
    check(reference_block.get("upstream_parity") is False,
          "report claims parity", problems)
    source = report.get("source_probe", {})
    check(source.get("status") ==
          "consumer_present_pinned_upstream_source_absent" and
          source.get("present") is True,
          "source probe is not present/pinned", problems)
    check(source.get("revision") ==
          "81eed5e8f68b6bed1789f682fe78cdd324495afc",
          "source revision mismatch", problems)
    check(source.get("license") == "MIT", "source licence mismatch", problems)
    check(source.get("contentvec_config_present") is True and
          source.get("preprocessor_config_present") is True,
          "pinned ContentVec config is not recorded present", problems)
    check((source.get("upstream") or {}).get("present") is False,
          "upstream ContentVec source is unexpectedly present", problems)
    weights = report.get("weights_probe", {})
    check(weights.get("status") == "blocked_weights_absent" and
          weights.get("present") is False,
          "weights probe is not absent", problems)
    check(weights.get("sha256") is None and
          weights.get("byte_count") is None,
          "weights probe has fabricated identity", problems)
    runtime = report.get("runtime_probe", {})
    check(runtime.get("status") == "blocked_runtime_unpinned" and
          runtime.get("pinned") is False,
          "runtime probe is not absent/unpinned", problems)
    geometry = report.get("geometry", {})
    check(geometry.get("model_architecture") == "HubertModelWithFinalProj",
          "model architecture mismatch", problems)
    check(geometry.get("encoder_hidden_size") == 768,
          "encoder hidden size mismatch", problems)
    check(geometry.get("encoder_layer_count") == 12,
          "encoder layer count mismatch", problems)
    check(geometry.get("encoder_attention_heads") == 12,
          "encoder attention head count mismatch", problems)
    check(geometry.get("encoder_intermediate_size") == 3072,
          "encoder intermediate size mismatch", problems)
    check(geometry.get("conv_channels") == 512,
          "encoder convolution width mismatch", problems)
    check(geometry.get("conv_stride") == [5, 2, 2, 2, 2, 2, 2],
          "encoder convolution stride mismatch", problems)
    check(geometry.get("conv_receptive_field_samples") == 400,
          "encoder receptive field mismatch", problems)
    check(geometry.get("encoder_frame_stride_samples") == 320,
          "encoder stride mismatch", problems)
    check(geometry.get("encoder_frame_rate_hz") == 50.0,
          "encoder frame rate mismatch", problems)
    check(geometry.get("v0_frames_per_content_frame") == 2,
          "v0 frames per content frame mismatch", problems)
    check(geometry.get("classifier_proj_size") == 256,
          "classifier projection mismatch", problems)
    check(geometry.get("v1") == {
        "output_layer": 9, "feature_dim": 256,
        "path": "hidden_states[9] -> final_proj",
    }, "v1 path mismatch", problems)
    check(geometry.get("v2") == {
        "output_layer": 12, "feature_dim": 768,
        "path": "last_hidden_state",
    }, "v2 path mismatch", problems)
    check(geometry.get("measured_here") is False,
          "geometry claims local measurement", problems)
    history = report.get("historical_evidence", {})
    check(history.get("status") == "not_tested_no_local_result",
          "historical evidence status mismatch", problems)
    check(history.get("standalone_tested") is False,
          "historical evidence claims a standalone test", problems)
    check(history.get("timing") is None and history.get("quality") is None,
          "historical evidence carries a timing or quality result", problems)
    check(history.get("reproduced_here") is False and
          history.get("qualifies_candidate") is False,
          "historical evidence is claimed as reproduced/qualified", problems)
    candidate = report.get("candidates", {}).get(COMPONENT, {})
    check(candidate.get("status") == "blocked_weights_and_runtime_absent",
          "candidate status mismatch", problems)
    check(candidate.get("metrics") is None and
          candidate.get("qualifies_candidate") is False,
          "candidate carries metrics or qualifies", problems)
    check(candidate.get("supported_output_layers") == [9, 12],
          "candidate output layers mismatch", problems)
    required = report.get("required_results", {})
    check(isinstance(required, dict) and required, "required results missing",
          problems)
    check(all(value != "passed" and value != "qualified"
              for value in required.values()),
          "a required result is marked passed/qualified", problems)
    adverse = report.get("adverse", {})
    check(adverse.get("invalid_config_and_input", {}).get("all_rejected")
          is True, "invalid requests were accepted", problems)
    check(adverse.get("invalid_config_and_input", {}).get("accepted_count")
          == 0, "invalid request accepted count is nonzero", problems)
    check(adverse.get("invalid_json_numeric_fields", {}).get("all_rejected")
          is True, "invalid JSON was accepted", problems)
    check(adverse.get("missing_result", {}).get("metrics") is None and
          adverse.get("missing_result", {}).get("qualifies_candidate") is False,
          "missing result carries metrics or qualifies", problems)
    stimuli = report.get("stimulus_probe", {})
    check(stimuli.get("candidate_processing") is False,
          "stimulus probe claims candidate processing", problems)
    check(all(item.get("byte_identical") is True
              for item in stimuli.get("identity_control", {}).values()),
          "harness identity control is not bit exact", problems)
    check(all(item.get("measured_here") is False
              for item in stimuli.get("frame_stride_probe", {}).values()),
          "frame stride probe claims a measurement", problems)
    checks = report.get("local_harness_checks", {})
    check(all(value is True for value in checks.values()),
          "a local harness check is not true", problems)
    check(len(checks) >= 12, "local harness check set is too small", problems)
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
    check(report.get("no_missing_result_qualifies_candidate") is True,
          "missing-result guard is not enabled", problems)
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
    expected_sidecar = (sha256_file(REPORT_PATH) + "  report.json\n")
    check(sidecar == expected_sidecar, "report SHA-256 sidecar mismatch",
          problems)
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
    return len(pins) + len(report.get("source_pins", {})) + len(
        report.get("boundary_pins", {}))


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
    check(report.get("board_links") == [stable],
          "report board projection mismatch", problems)
    check(report.get("board_link_fields") ==
          ["task_id", "title", "mode", "repository", "component"],
          "board link fields mismatch", problems)
    expected = sha256_bytes(canonical_bytes([stable]))
    check(report.get("board_link_projection_sha256") == expected,
          "board projection digest mismatch", problems)
    check(contract.get("board_links") == [stable] and
          contract.get("board_link_projection_sha256") == expected,
          "contract board projection mismatch", problems)
    for mutable in ("status", "owner", "review", "handoff", "claim",
                    "history", "blocked_reason"):
        check(mutable in report.get("board_mutable_fields_excluded", []),
              "mutable board field not excluded: " + mutable, problems)


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
    for name in ("README.md", "LICENSES.md", "reference.py", "run.py",
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
    sys.path.insert(0, str(HERE))
    import reference  # noqa: PLC0415
    source = reference.source_probe()
    check(source.get("present") is True,
          "pinned consumer checkout is no longer present", problems)
    check((source.get("upstream") or {}).get("present") is False,
          "upstream ContentVec source appeared; revisit the blocker package",
          problems)
    weights = reference.weights_probe()
    check(weights.get("present") is False,
          "ContentVec weights appeared; revisit the blocker package",
          problems)
    runtime = reference.runtime_probe()
    check(runtime.get("pinned") is False,
          "a pinned ContentVec runtime appeared; revisit the blocker package",
          problems)


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
        ["git", "status", "--porcelain"], cwd=str(SDK_ROOT),
        capture_output=True, text=True, check=False)
    if process.returncode != 0:
        problems.append("git status failed in the SDK worktree")
        return
    for line in process.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        check(path.startswith(TASK_PREFIX),
              "change outside task-local scope: " + path, problems)


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
    except (OSError, VerificationError, ValueError, KeyError, TypeError) as error:
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
          "git_scope_ok=1 absent_weights_ok=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
