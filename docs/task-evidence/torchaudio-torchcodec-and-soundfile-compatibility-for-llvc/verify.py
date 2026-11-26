# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the LLVC audio-I/O compatibility package.

It checks strict JSON, canonical bytes, exact pins, blocker semantics, stable
linked-row identity, licensing, prohibited artifacts, task-local git scope and
three cold-start byte-identical regenerations. It never writes package evidence.
"""

from __future__ import annotations

import hashlib
import importlib.util
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
TASK_PREFIX = (
    "docs/task-evidence/"
    "torchaudio-torchcodec-and-soundfile-compatibility-for-llvc/")
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
TASK_ID = "SDK-TORCHAUDIO-TORCHCODEC-AND-SOUNDFILE-COMPATIBILITY-FOR-LLVC"
TITLE = "TorchAudio, TorchCodec and SoundFile compatibility for LLVC"
COMPONENT = "torchaudio-torchcodec-and-soundfile-compatibility-for-llvc"
BRANCH = (
    "swarm/SDK-TORCHAUDIO-TORCHCODEC-AND-SOUNDFILE-COMPATIBILITY-FOR-LLVC")
BASE_COMMIT = "8bd03e2d9d08d550bb4b2ac28425c71eaf8a0ba9"
GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]
EXPECTED_LINK = {
    "task_id": TASK_ID,
    "title": TITLE,
    "mode": "implementation",
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
    ".tar", ".gz", ".whl",
}
BLOCKER_KEYS = {
    "status", "artifact", "present", "missing", "exact_error",
    "expected_license", "rights_requirement", "runtime_digest",
    "no_upstream_parity_claim", "not_attempted", "reopen",
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
    check(contract.get("schema_id") == reference_schema_id(),
          "contract schema mismatch", problems)
    check(contract.get("contract_schema_id") ==
          "audio-sdk/task-evidence-contract/0.2",
          "contract schema generation mismatch", problems)
    check(contract.get("task") == TASK_ID, "contract task mismatch", problems)
    check(contract.get("title") == TITLE, "contract title mismatch", problems)
    check(contract.get("component") == COMPONENT,
          "contract component mismatch", problems)
    check(contract.get("mode") == "implementation",
          "contract mode mismatch", problems)
    check(contract.get("branch") == BRANCH, "contract branch mismatch",
          problems)
    check(contract.get("base_commit") == BASE_COMMIT,
          "contract base commit mismatch", problems)
    check(contract.get("profile") == "tool", "contract profile mismatch",
          problems)
    check(contract.get("profile_label") == "Tool",
          "contract profile label mismatch", problems)
    check(contract.get("decision") == "DEFER",
          "contract decision is not DEFER", problems)
    check(contract.get("status") == "incomplete",
          "contract status is not incomplete", problems)
    check(contract.get("proposal_only") is True,
          "contract is not proposal only", problems)
    check(contract.get("qualification_status") == "not_qualified",
          "contract qualification_status mismatch", problems)
    qualification = contract.get("qualification", {})
    check(qualification.get("status") == "not_qualified",
          "contract qualification is not not_qualified", problems)
    check(qualification.get("readiness") == "incomplete",
          "contract readiness is not incomplete", problems)
    check(qualification.get("proposal_only") is True,
          "contract qualification is not proposal only", problems)
    check(qualification.get("candidate_qualified") is False,
          "contract claims a qualified candidate", problems)
    check(qualification.get("runtime_present") is False,
          "contract claims a runtime", problems)
    check(qualification.get("shim_executed") is False,
          "contract claims shim execution", problems)
    check(qualification.get("tool_profile_result") is False,
          "contract claims a Tool result", problems)
    check(contract.get("scope") == report.get("scope"),
          "contract and report scope differ", problems)
    scope = contract.get("scope", {})
    for key in (
        "runtime_installed", "runtime_imported", "runtime_executed",
        "shim_executed", "network_used", "real_assets_used",
        "real_corpus_used", "provider_registered", "public_abi_changed",
        "registry_or_default_changed", "shared_build_or_ci_changed",
        "benchmark_run", "device_timing_measured", "listening_performed",
        "release_claim",
    ):
        check(scope.get(key) is False, "scope is open: " + key, problems)
    check(scope.get("task_local_only") is True,
          "scope is not task local", problems)
    check(contract.get("public_v0_geometry") == {
        "sample_rate_hz": 16000, "channels": 1,
        "sample_format": "float32", "frame_samples": 160, "changed": False,
    }, "public v0 geometry mismatch", problems)
    boundary = contract.get("boundary", {})
    check(boundary == report.get("boundary"),
          "contract and report boundary differ", problems)
    check(boundary.get("linked_row_identity_only") is True,
          "boundary is not identity only", problems)
    check(boundary.get("board_file_pinned") is False,
          "mutable board is pinned", problems)
    check(boundary.get("mutable_board_fields_gate") is False,
          "mutable board fields are gated", problems)
    blocker = contract.get("upstream_blocker", {})
    check(set(blocker) == BLOCKER_KEYS, "upstream blocker schema mismatch",
          problems)
    check(blocker.get("status") == "blocked_runtime_absent_and_unpinned",
          "upstream blocker status mismatch", problems)
    missing = blocker.get("missing", {})
    check((missing.get("torchaudio") or {}).get("status") == "absent",
          "torchaudio is not recorded absent", problems)
    check((missing.get("torchaudio") or {}).get("sha256") is None,
          "torchaudio has a fabricated digest", problems)
    check((missing.get("torchcodec") or {}).get("version") is None,
          "torchcodec has a fabricated version", problems)
    check((missing.get("torchcodec") or {}).get("sha256") is None,
          "torchcodec has a fabricated digest", problems)
    check((missing.get("soundfile") or {}).get("sha256") is None,
          "soundfile has a fabricated digest", problems)
    check((missing.get("venv") or {}).get("status") == "absent",
          "evaluation venv is not recorded absent", problems)
    check(blocker.get("runtime_digest") is None,
          "blocker has a fabricated runtime digest", problems)
    check(blocker.get("no_upstream_parity_claim") is True,
          "upstream parity claim is not disabled", problems)
    check("consent" in str(blocker.get("rights_requirement")).lower(),
          "rights requirement does not mention consent", problems)
    check("libsndfile" in str(blocker.get("expected_license")),
          "libsndfile terms are not recorded", problems)
    gates = contract.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8,
          "contract does not carry eight release gates", problems)
    if isinstance(gates, list):
        check([gate.get("id") for gate in gates] == GATE_IDS,
              "contract gate ids mismatch", problems)
        check(all(gate.get("status") == "blocked" for gate in gates),
              "a contract release gate is not blocked", problems)
        check(all(gate.get("qualifies") is False for gate in gates),
              "a contract release gate qualifies", problems)
    check(contract.get("required_results") == report.get("required_results"),
          "contract and report required results differ", problems)
    check(contract.get("historical_timing") == report.get("historical_timing"),
          "contract and report timing differ", problems)


def reference_schema_id() -> str:
    return (
        "audio-sdk/"
        "torchaudio-torchcodec-and-soundfile-compatibility-for-llvc/0.1")


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") == "audio-sdk/task-evidence-report/0.3",
          "report schema mismatch", problems)
    check(report.get("task_schema_id") == reference_schema_id(),
          "report task schema mismatch", problems)
    check(report.get("task") == TASK_ID, "report task mismatch", problems)
    check(report.get("title") == TITLE, "report title mismatch", problems)
    check(report.get("component") == COMPONENT,
          "report component mismatch", problems)
    check(report.get("mode") == "implementation", "report mode mismatch",
          problems)
    check(report.get("branch") == BRANCH, "report branch mismatch", problems)
    check(report.get("base_commit") == BASE_COMMIT,
          "report base commit mismatch", problems)
    check(report.get("decision") == "DEFER",
          "report decision is not DEFER", problems)
    check(report.get("status") == "incomplete",
          "report status is not incomplete", problems)
    check(report.get("proposal_only") is True,
          "report is not proposal only", problems)
    check(report.get("qualification_status") == "not_qualified",
          "report qualification_status mismatch", problems)
    qualification = report.get("qualification", {})
    check(qualification.get("status") == "not_qualified" and
          qualification.get("candidate_qualified") is False and
          qualification.get("readiness") == "incomplete",
          "report qualification is not incomplete/not_qualified", problems)
    check(report.get("profile") == "tool", "report profile is not tool",
          problems)
    check(report.get("profile_label") == "Tool",
          "report profile label mismatch", problems)

    readiness = report.get("runtime_readiness", {})
    check(readiness.get("blocked") is True,
          "runtime is not recorded blocked", problems)
    check(readiness.get("exact_runtime_present") is False,
          "report claims an exact runtime", problems)
    check(readiness.get("pinned") is False,
          "report claims a pinned runtime", problems)
    check(readiness.get("runtime_imported") is False,
          "report claims a runtime import", problems)
    check(readiness.get("model_executed") is False,
          "report claims model execution", problems)
    check(readiness.get("status") == "blocked_runtime_absent_unpinned",
          "runtime status mismatch", problems)
    availability = readiness.get("package_availability_any_interpreter", {})
    check(availability.get("torchaudio") is False,
          "torchaudio is recorded present", problems)
    check(availability.get("torchcodec") is False,
          "torchcodec is recorded present", problems)
    for row in readiness.get("partial_installations", []):
        check(row.get("qualified") is False,
              "a partial installation is qualified", problems)

    absence = report.get("absence_evidence", {})
    check(absence.get("all_exact_runtime_artifacts_absent") is True,
          "exact runtime artifacts are recorded present", problems)
    check(absence.get("exact_runtime_artifacts_found") == [],
          "exact runtime artifact found", problems)

    shim = report.get("shim_reference", {})
    check(shim.get("status") == "pinned_source_checks_pass",
          "shim source checks did not pass", problems)
    check(shim.get("executed") is False,
          "shim claims source execution", problems)
    check(len(shim.get("checks", [])) == 4,
          "shim override checks are incomplete", problems)
    check(len(shim.get("upstream_checks", [])) == 3,
          "upstream API checks are incomplete", problems)
    check(all(item.get("present") is True
              for item in shim.get("checks", [])),
          "a shim override is missing", problems)
    check(all(item.get("present") is True
              for item in shim.get("upstream_checks", [])),
          "an upstream API call is missing", problems)

    api_surface = report.get("api_surface", [])
    check(len(api_surface) == 4, "API surface is incomplete", problems)
    check(all(item.get("executed_here") is False for item in api_surface),
          "an API surface row claims execution", problems)

    wav = report.get("wav_contract_probe", {})
    check(wav.get("real_soundfile_used") is False,
          "WAV model claims real SoundFile", problems)
    check(wav.get("real_torchaudio_used") is False,
          "WAV model claims real TorchAudio", problems)
    check(wav.get("candidate_processing") is False,
          "WAV model claims candidate processing", problems)
    check(wav.get("all_sample_counts_exact") is True,
          "WAV model sample counts are not exact", problems)
    check(wav.get("all_channel_orientations_ok") is True,
          "WAV channel orientation is wrong", problems)
    check(wav.get("all_roundtrips_byte_identical") is True,
          "WAV round trips are not byte identical", problems)
    check(wav.get("all_quantization_within_bound") is True,
          "WAV quantization exceeds the bound", problems)
    check(wav.get("all_rejections_closed") is True,
          "WAV malformed cases were accepted", problems)
    check(len(wav.get("cases", [])) == 5, "WAV case set is incomplete",
          problems)
    identity = wav.get("identity_control", {})
    check(identity.get("encode_byte_identical") is True and
          identity.get("decode_digest_identical") is True,
          "WAV identity control is not bit exact", problems)

    adverse = report.get("adverse", {})
    for name in ("invalid_requests", "invalid_json", "wav_rejections"):
        block = adverse.get(name, {})
        check(block.get("all_rejected") is True,
              "adverse group was accepted: " + name, problems)
        check(block.get("accepted_count") == 0,
              "adverse accepted count is nonzero: " + name, problems)
    check(adverse.get("invalid_requests", {}).get("case_count", 0) >= 22,
          "request rejection set is too small", problems)
    check(adverse.get("wav_rejections", {}).get("case_count", 0) >= 12,
          "WAV rejection set is too small", problems)
    check(adverse.get("missing_result", {}).get("metrics") is None and
          adverse.get("missing_result", {}).get(
              "qualifies_candidate") is False,
          "missing result carries metrics or qualifies", problems)

    tool = report.get("tool_profile", {})
    check(tool.get("profile") == "tool" and tool.get("label") == "Tool",
          "tool profile header mismatch", problems)
    check(tool.get("satisfied") is False,
          "tool profile claims satisfaction", problems)
    requirements = tool.get("requirements", [])
    check(len(requirements) == 9, "tool profile rows are incomplete",
          problems)
    check(all(row.get("status") in ("blocked", "not_run", "synthetic_pass")
              for row in requirements),
          "a tool profile row claims a real pass", problems)

    artifacts = report.get("required_artifacts", [])
    check(len(artifacts) == 8, "required artifact set is incomplete", problems)
    check(sum(1 for row in artifacts if row.get("present")) == 1,
          "present artifact count mismatch", problems)
    check(sum(1 for row in artifacts if row.get("blocked")) == 7,
          "blocked artifact count mismatch", problems)
    check(artifacts[0].get("present") is True and
          artifacts[0].get("verified") is True,
          "pinned source artifact is not present/verified", problems)

    blockers = report.get("exact_blockers", [])
    check(len(blockers) == 6, "exact blocker set is incomplete", problems)
    check(all(row.get("qualifies") is False for row in blockers),
          "an exact blocker qualifies", problems)

    timing = report.get("historical_timing", {})
    check(timing.get("chunk_samples") == 208, "chunk geometry mismatch",
          problems)
    check(timing.get("chunk_ms") == 13.0, "chunk duration mismatch", problems)
    check(timing.get("algorithmic_latency_samples") == 240,
          "algorithmic latency mismatch", problems)
    check(timing.get("chunk_count") == 743, "chunk count mismatch", problems)
    check(timing.get("measured_here") is False,
          "timing claims local measurement", problems)
    check(timing.get("shim_overhead_measured") is False,
          "shim overhead claims measurement", problems)

    required = report.get("required_results", {})
    check(isinstance(required, dict) and required,
          "required results missing", problems)
    check(all(value not in ("passed", "qualified", "measured")
              for value in required.values()),
          "a required result is marked passed/qualified", problems)

    gates = report.get("release_gates", [])
    check(isinstance(gates, list) and len(gates) == 8,
          "report does not carry eight release gates", problems)
    if isinstance(gates, list):
        check([gate.get("id") for gate in gates] == GATE_IDS,
              "report gate ids mismatch", problems)
        check(all(gate.get("status") == "blocked" for gate in gates),
              "a report release gate is not blocked", problems)
        check(all(gate.get("statement") and gate.get("reopen_condition")
                  for gate in gates),
              "a release gate lacks a statement or reopen condition",
              problems)
    check(report.get("no_missing_result_qualifies_candidate") is True,
          "missing-result guard is not enabled", problems)
    counts = report.get("counts", {})
    check(counts.get("qualifying_results") == 0,
          "qualifying results count is nonzero", problems)
    check(counts.get("blocked_artifacts") == 7,
          "blocked artifact count mismatch in counts", problems)
    check(report.get("regression_count") == 0 and
          report.get("regressions") == [],
          "regression fields are not empty", problems)


def check_pins(contract: Dict[str, Any], report: Dict[str, Any],
               problems: List[str]) -> int:
    pins = contract.get("artifact_pins", {})
    expected_names = (
        "README.md", "LICENSES.md", "reference.py", "report.json",
        "report.json.sha256", "run.py", "test_reference.py", "verify.py",
        "contract.json.license", "report.json.license",
        "report.json.sha256.license", "SOURCES.sha256.license",
        "SOURCES.sha256",
    )
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
        check(path != "audio-benchmark-platform/plan/swarm/TASKS.json",
              "mutable TASKS.json is directly pinned", problems)
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
    check(report.get("linked_row_identity") == stable,
          "report linked-row projection mismatch", problems)
    check(report.get("board_link_fields") ==
          ["task_id", "title", "mode", "repository", "component"],
          "board link fields mismatch", problems)
    expected = sha256_bytes(canonical_bytes([stable]))
    check(report.get("linked_row_sha256") == expected,
          "linked-row projection digest mismatch", problems)
    check(contract.get("linked_row_identity") == stable and
          contract.get("linked_row_sha256") == expected,
          "contract linked-row projection mismatch", problems)
    for mutable in ("status", "owner", "review", "handoff", "claim",
                    "history", "blocked_reason", "depends_on"):
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
        check(not re.match(r"^(G_\d+\.pth|.*\.onnx|.*\.whl)$", path.name),
              "prohibited model/package artifact: " + path.name, problems)


def check_absent(problems: List[str]) -> None:
    sys.path.insert(0, str(HERE))
    import reference  # noqa: PLC0415
    for module in ("torchaudio", "torchcodec"):
        try:
            found = importlib.util.find_spec(module) is not None
        except (ImportError, AttributeError, ValueError):
            found = False
        check(found is False,
              module + " appeared; the blocker package must be revisited",
              problems)
    check(not (reference.EVAL_ROOT / ".venv-eval").exists(),
          "the evaluation virtualenv appeared; the blocker package must be "
          "revisited", problems)
    check((reference.WORKSPACE / reference.SHIM_WRAPPER_PATH).is_file(),
          "the pinned shim wrapper is missing", problems)
    shim = reference.shim_source_probe()
    check(shim.get("status") == "pinned_source_checks_pass",
          "the pinned shim source checks no longer pass", problems)
    readiness = reference.runtime_readiness()
    check(readiness.get("exact_runtime_present") is False,
          "an exact runtime appeared; the blocker package must be revisited",
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
    print("PASS pins_ok=" + str(pins_checked) +
          " reproduction_ok=" + str(int(reproduction_ok)) +
          " cold_starts=" + str(repeats) + "/3 byte_identical=true" +
          " profile=Tool status=incomplete decision=DEFER" +
          " qualification=not_qualified runtime=absent gates=8/8-blocked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
