# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the SDK-WEBRTC-AGC-AGC2 evidence package.

It checks strict JSON, canonical bytes, exact pins, blocker semantics, stable
linked-row identity, licensing, prohibited upstream artifacts, task-local git
scope and three cold-start byte-identical regenerations. It never writes
package evidence.
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
TASK_PREFIX = "docs/task-evidence/webrtc-agc-agc2/"
TASK_ID = "SDK-WEBRTC-AGC-AGC2"
BASE_COMMIT = "74fb3cd9f6f3e4b96a542d925461d24e1472c21d"
GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]
EXPECTED_LINK = {
    "task_id": "SDK-WEBRTC-AGC-AGC2",
    "title": "WebRTC AGC / AGC2",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "component": "webrtc-agc-agc2",
}
ARTIFACT_FILES = (
    "README.md", "LICENSE", "LICENSES.md", "THIRD_PARTY_NOTICES.md",
    "check_licensing.py", "contract.json", "reference.py", "report.json",
    "report.json.sha256", "run.py", "SOURCES.sha256", "test_reference.py",
    "verify.py", "contract.json.license", "report.json.license",
    "report.json.sha256.license", "SOURCES.sha256.license",
)
JSON_SIDECAR_FILES = (
    "contract.json", "report.json", "report.json.sha256", "SOURCES.sha256",
)
PROHIBITED_NAMES = {
    "audio_processing.h", "audio_processing_impl.h", "audio_processing_impl.cc",
    "gain_control.h", "gain_control.c", "gain_control_impl.h",
    "gain_control_impl.cc", "agc_manager_direct.h", "agc_manager_direct.cc",
    "adaptive_digital_gain_controller.h", "adaptive_digital_gain_controller.cc",
    "adaptive_agc.h", "adaptive_agc.cc", "agc2_common.h",
    "input_volume_controller.h", "input_volume_controller.cc",
    "rnn_vad_weights.h", "rnn_vad_weights.cc", "NOTICE", "COPYING",
}
PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx", ".pt", ".bin",
    ".so", ".dylib", ".a", ".o", ".zip", ".tar", ".gz", ".whl",
}
BLOCKER_KEYS = {
    "status", "artifact", "expected_license", "pinned_revision",
    "source_digest", "runtime_digest", "no_upstream_parity_claim",
    "documented_reference_revisions", "required_files", "required_runtime",
    "rights_requirement", "workspace_search", "not_attempted", "reopen",
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
    check(contract.get("schema_id") ==
          "audio-sdk/webrtc-agc-agc2-contract/0.1",
          "contract schema mismatch", problems)
    check(contract.get("contract_version") == "0.1",
          "contract version mismatch", problems)
    check(contract.get("task") == TASK_ID, "contract task mismatch", problems)
    check(contract.get("component") == "webrtc-agc-agc2",
          "contract component mismatch", problems)
    check(contract.get("branch") == "swarm/SDK-WEBRTC-AGC-AGC2",
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
    check(qualification.get("candidate_qualified") is False,
          "contract claims a qualified candidate", problems)
    check(qualification.get("upstream_parity") is False,
          "contract claims upstream parity", problems)
    check(qualification.get("all_required_results_present") is False,
          "contract claims all required results are present", problems)
    check(contract.get("comparison_status") == "blocked_upstream_absent",
          "contract comparison status mismatch", problems)
    check(contract.get("apm_mode_ownership_status") == "unresolved",
          "contract APM mode ownership is not unresolved", problems)
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
    check(blocker.get("status") == "blocked_upstream_absent",
          "upstream blocker status mismatch", problems)
    check(blocker.get("pinned_revision") is None,
          "upstream blocker has a fabricated revision", problems)
    check(blocker.get("source_digest") is None,
          "upstream blocker has a fabricated source digest", problems)
    check(blocker.get("runtime_digest") is None,
          "upstream blocker has a fabricated runtime digest", problems)
    check(blocker.get("no_upstream_parity_claim") is True,
          "upstream parity claim is not disabled", problems)
    check("Apache-2.0" in str(blocker.get("expected_license")),
          "expected upstream licence mismatch", problems)
    check(bool(blocker.get("rights_requirement")),
          "rights requirement is empty", problems)
    for revision in blocker.get("documented_reference_revisions", []):
        check(revision.get("verified_locally") is False,
              "documented revision claims local verification", problems)
    gates = contract.get("release_gates", [])
    check([gate.get("id") for gate in gates] == GATE_IDS,
          "contract release gate identities mismatch", problems)
    check(len(gates) == 8 and all(gate.get("status") == "blocked"
                                 for gate in gates),
          "not all eight contract release gates are blocked", problems)
    canonical = contract.get("canonical_report", {})
    report_payload = REPORT_PATH.read_bytes()
    report_value = strict_load(REPORT_PATH)
    check(canonical.get("file_sha256") == sha256_bytes(report_payload),
          "contract report file digest mismatch", problems)
    check(canonical.get("canonical_digest") ==
          sha256_bytes(canonical_bytes(report_value)),
          "contract canonical report digest mismatch", problems)
    check(canonical.get("sidecar_sha256") == sha256_file(SIDECAR_PATH),
          "contract sidecar digest mismatch", problems)
    check(contract.get("source_pins") == report.get("source_pins"),
          "contract and report source pins differ", problems)
    check(contract.get("boundary_pins") == report.get("boundary_pins"),
          "contract and report boundary pins differ", problems)
    check(contract.get("board_links") == report.get("board_links"),
          "contract and report board links differ", problems)
    check(contract.get("board_link_projection_sha256") ==
          report.get("board_link_projection_sha256"),
          "contract and report board projection differ", problems)


def check_pins(contract: Dict[str, Any], report: Dict[str, Any],
               problems: List[str]) -> int:
    checked = 0
    for name, digest in contract.get("artifact_pins", {}).items():
        path = HERE / name
        check(path.is_file(), "missing artifact " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest,
                  "artifact pin mismatch: " + name, problems)
            checked += 1
    check("contract.json" not in contract.get("artifact_pins", {}),
          "contract pins itself", problems)
    for name, digest in report.get("artifact_pins", {}).items():
        path = HERE / name
        check(path.is_file(), "missing report artifact " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest,
                  "report artifact pin mismatch: " + name, problems)
            checked += 1
    check("report.json" not in report.get("artifact_pins", {}),
          "report pins itself", problems)
    for path, digest in contract.get("source_pins", {}).items():
        target = WORKSPACE / path
        check(target.is_file(), "missing source pin " + path, problems)
        if target.is_file():
            check(sha256_file(target) == digest,
                  "source pin mismatch: " + path, problems)
            checked += 1
    for path, digest in contract.get("boundary_pins", {}).items():
        target = SDK_ROOT / path
        check(target.is_file(), "missing boundary pin " + path, problems)
        if target.is_file():
            check(sha256_file(target) == digest,
                  "boundary pin mismatch: " + path, problems)
            checked += 1
    lines = SOURCES_PATH.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([a-f0-9]{64})  (.+)", line)
        check(match is not None, "malformed SOURCES line: " + line, problems)
        if match is None:
            continue
        digest, name = match.groups()
        if name.startswith("source:"):
            target = WORKSPACE / name[len("source:"):]
        elif name.startswith(TASK_PREFIX):
            target = SDK_ROOT / name
        else:
            target = SDK_ROOT / name
        check(target.is_file(), "missing SOURCES target " + name, problems)
        if target.is_file():
            check(sha256_file(target) == digest,
                  "SOURCES digest mismatch: " + name, problems)
            checked += 1
    check(not any(line.endswith("  " + TASK_PREFIX + "contract.json")
                  for line in lines),
          "SOURCES includes contract.json (pin cycle)", problems)
    check(SIDECAR_PATH.read_text(encoding="utf-8").strip() ==
          sha256_file(REPORT_PATH) + "  report.json",
          "report sidecar content mismatch", problems)
    return checked


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") ==
          "audio-sdk/webrtc-agc-agc2-reference-report/0.1",
          "report schema mismatch", problems)
    check(report.get("task") == TASK_ID, "report task mismatch", problems)
    check(report.get("decision") == "DEFER", "report decision is not DEFER",
          problems)
    check(report.get("status") == "proposal_only_not_qualified",
          "report status mismatch", problems)
    check(report.get("qualification_status") == "not_qualified",
          "report qualification status mismatch", problems)
    qualification = report.get("qualification", {})
    check(qualification.get("status") == "not_qualified",
          "report qualification is not not_qualified", problems)
    check(qualification.get("readiness") == "incomplete",
          "report readiness is not incomplete", problems)
    check(qualification.get("candidate_qualified") is False,
          "report claims a qualified candidate", problems)
    check(qualification.get("upstream_parity") is False,
          "report claims upstream parity", problems)
    check(qualification.get("all_required_results_present") is False,
          "report claims all required results present", problems)
    check(report.get("no_missing_result_qualifies_candidate") is True,
          "missing-result guard is disabled", problems)
    probe = report.get("absence_probe", {})
    check(probe.get("status") == "blocked_upstream_absent",
          "absence probe is not blocked_upstream_absent", problems)
    check(probe.get("present") is False, "absence probe found upstream source",
          problems)
    check(probe.get("match_count") == 0, "absence probe has name matches",
          problems)
    check(probe.get("found_count") == 0, "absence probe found a runtime",
          problems)
    check(probe.get("scan_truncated") is False, "absence probe was truncated",
          problems)
    reference_block = report.get("reference", {})
    check(reference_block.get("real_webrtc_source_or_binary") is False,
          "report claims real WebRTC source", problems)
    check(reference_block.get("upstream_parity") is False,
          "report reference claims parity", problems)
    check(reference_block.get("downloads") is False,
          "report claims downloads", problems)
    check(reference_block.get("candidate_processing") is False,
          "report claims candidate processing", problems)
    candidates = report.get("candidates", {})
    check(sorted(candidates) == ["webrtc_agc", "webrtc_agc2"],
          "candidate identities mismatch", problems)
    for name, block in candidates.items():
        check(block.get("status") == "blocked_upstream_absent",
              "candidate is not blocked: " + name, problems)
        check(block.get("metrics") is None,
              "candidate exposes metrics: " + name, problems)
        check(block.get("qualifies_candidate") is False,
              "candidate claims qualification: " + name, problems)
        check(block.get("apm_mode_ownership") == "unresolved",
              "candidate APM ownership is resolved without evidence: " + name,
              problems)
    comparison = report.get("separate_dsp_agc_comparison", {})
    check(comparison.get("status") == "blocked_upstream_absent",
          "separate DSP AGC comparison is not blocked", problems)
    check(comparison.get("candidate_metrics") is None,
          "comparison exposes candidate metrics", problems)
    check(comparison.get("control_metrics") is None,
          "comparison exposes control metrics", problems)
    check(comparison.get("qualifies_candidate") is False,
          "comparison qualifies a candidate", problems)
    ownership = report.get("apm_mode_ownership", {})
    check(ownership.get("status") == "unresolved",
          "APM mode ownership is not unresolved", problems)
    check(ownership.get("owner") is None, "APM ownership has an owner",
          problems)
    check(ownership.get("declared_modes") == [],
          "APM ownership declares modes", problems)
    check(all(value == "unresolved"
              for value in ownership.get("execution_modes", {}).values()),
          "an APM execution mode is resolved without evidence", problems)
    check(ownership.get("qualifies_candidate") is False,
          "APM ownership qualifies a candidate", problems)
    required = report.get("required_results", {})
    check(bool(required), "required results are empty", problems)
    check(all(value in ("blocked_upstream_absent",
                        "partial_local_harness_only")
              for value in required.values()),
          "a required candidate result is falsely met", problems)
    check(required.get("numerical_and_nonfinite") ==
          "partial_local_harness_only",
          "numerical result is overclaimed", problems)
    local = report.get("local_harness_checks", {})
    check(bool(local) and all(local.values()),
          "a local harness check is false", problems)
    adverse = report.get("adverse", {})
    for key in ("invalid_config_and_input", "invalid_json_numeric_fields"):
        block = adverse.get(key, {})
        check(block.get("all_rejected") is True,
              "adverse cases are not all rejected: " + key, problems)
        check(block.get("accepted_count") == 0,
              "adverse block accepted a case: " + key, problems)
        check(block.get("metrics") is None,
              "adverse block exposes metrics: " + key, problems)
        for case in block.get("cases", []):
            check(case.get("accepted") is False,
                  "adverse case accepted: " + str(case), problems)
            check(case.get("error") != "NOT_REJECTED",
                  "adverse case has no rejection code: " + str(case),
                  problems)
    missing = adverse.get("missing_result", {})
    check(missing.get("status") == "blocked",
          "missing result is not blocked", problems)
    check(missing.get("metrics") is None, "missing result exposes metrics",
          problems)
    check(missing.get("qualifies_candidate") is False,
          "missing result qualifies a candidate", problems)
    stimuli = report.get("stimulus_probe", {})
    check(stimuli.get("candidate_processing") is False,
          "stimulus probe claims candidate processing", problems)
    check(all(block.get("byte_identical") is True
              for block in stimuli.get("identity_control", {}).values()),
          "identity control is not byte-identical", problems)
    check(stimuli.get("speech_contrast", {}).get("voiced_to_pause_db", 0) >= 10.0,
          "speech contrast proxy is too weak", problems)
    gates = report.get("release_gates", [])
    check([gate.get("id") for gate in gates] == GATE_IDS,
          "report release gate identities mismatch", problems)
    check(len(gates) == 8 and all(gate.get("status") == "blocked"
                                 for gate in gates),
          "not all eight report gates are blocked", problems)
    check(report.get("remaining_gates") == GATE_IDS,
          "remaining gates mismatch", problems)


def check_board(contract: Dict[str, Any], report: Dict[str, Any],
                problems: List[str]) -> None:
    board = strict_load(BOARD_PATH)
    tasks = {task["id"]: task for task in board.get("tasks", [])}
    locals_ = [row for row in contract.get("board_links", [])
               if row.get("task_id") == TASK_ID]
    check(len(locals_) == 1, "contract must link exactly one SDK row", problems)
    if locals_:
        row = locals_[0]
        task = tasks.get(TASK_ID, {})
        expected = {
            "task_id": task.get("id"),
            "title": task.get("title"),
            "mode": task.get("mode"),
            "repository": task.get("repository"),
            "component": task.get("component"),
        }
        check(row == expected, "stable board link mismatch", problems)
        check(expected == EXPECTED_LINK,
              "board stable identity changed from the frozen link", problems)
    expected_rows = [EXPECTED_LINK]
    digest = sha256_bytes(canonical_bytes(expected_rows))
    check(digest == contract.get("board_link_projection_sha256"),
          "contract board projection digest mismatch", problems)
    check(digest == report.get("board_link_projection_sha256"),
          "report board projection digest mismatch", problems)
    check(report.get("board_links") == expected_rows,
          "report board links differ from stable identity projection",
          problems)
    for row in expected_rows:
        for mutable in ("status", "owner", "history", "review", "handoff",
                        "blocked_reason", "dispatch_priority"):
            check(mutable not in row, "mutable board field entered projection",
                  problems)
    full_digest = sha256_file(BOARD_PATH)
    for name, path in (("report", REPORT_PATH), ("contract", CONTRACT_PATH),
                       ("sources", SOURCES_PATH)):
        payload = path.read_text(encoding="utf-8")
        check(full_digest not in payload,
              "mutable full TASKS.json digest entered " + name, problems)
        check("plan/swarm/TASKS.json" not in payload,
              "mutable TASKS.json path entered " + name, problems)


def check_licensing(problems: List[str]) -> None:
    for name in ARTIFACT_FILES:
        check((HERE / name).is_file(), "missing licensing artifact " + name,
              problems)
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        check("SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes" in head,
              "missing copyright SPDX in " + path.name, problems)
        check("SPDX" "-License-Identifier: Apache-2.0" in head,
              "missing licence SPDX in " + path.name, problems)
    for name in ("README.md", "LICENSE", "LICENSES.md",
                 "THIRD_PARTY_NOTICES.md"):
        head = "\n".join((HERE / name).read_text(encoding="utf-8")
                         .splitlines()[:6])
        check("SPDX" in head, "missing SPDX note in " + name, problems)
    for name in JSON_SIDECAR_FILES:
        sidecar = HERE / (name + ".license")
        check(sidecar.is_file(), "missing SPDX sidecar for " + name, problems)
        if sidecar.is_file():
            text = sidecar.read_text(encoding="utf-8")
            check("SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes" in text,
                  "bad copyright SPDX sidecar for " + name, problems)
            check("SPDX" "-License-Identifier: Apache-2.0" in text,
                  "bad licence SPDX sidecar for " + name, problems)
    notices = (HERE / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for token in ("WebRTC", "Apache-2.0", "AGC2", "absent"):
        check(token in notices, "third-party notice is missing " + token,
              problems)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    check('"docs/**"' in reuse and
          'SPDX' '-License-Identifier = "Apache-2.0"' in reuse,
          "REUSE.toml does not cover docs/** as Apache-2.0", problems)
    check((SDK_ROOT / "LICENSES/Apache-2.0.txt").is_file(),
          "LICENSES/Apache-2.0.txt missing", problems)


def check_absent_upstream(problems: List[str]) -> None:
    for path in HERE.rglob("*"):
        if not path.is_file():
            continue
        check(path.name.lower() not in PROHIBITED_NAMES,
              "prohibited upstream artifact present: " + str(path), problems)
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES,
              "prohibited binary/audio artifact present: " + str(path),
              problems)
    for directory_name in ("agc2", "rnn_vad", "webrtc", "pywebrtc_audio"):
        check(not (HERE / directory_name).exists(),
              "prohibited upstream directory present: " + directory_name,
              problems)


def check_git_scope(problems: List[str]) -> None:
    status = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "-z"],
        capture_output=True, check=False)
    if status.returncode != 0:
        problems.append("git status failed")
        return
    entries = status.stdout.decode("utf-8", "replace").split("\0")
    for entry in entries:
        if not entry:
            continue
        path = entry[3:] if len(entry) > 3 else entry
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        check(path.startswith(TASK_PREFIX),
              "change outside task scope: " + path, problems)
    diff_check = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "diff", "--check"],
        capture_output=True, check=False)
    check(diff_check.returncode == 0,
          "git diff --check reported whitespace errors", problems)


def check_reproduction(report_payload: bytes, problems: List[str]) -> bool:
    process = subprocess.run(
        [sys.executable, "-c",
         "import reference,sys;sys.stdout.buffer.write(reference.report_bytes())"],
        cwd=str(HERE), capture_output=True, check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if process.returncode != 0:
        problems.append("in-process report regeneration failed")
        return False
    check(process.stdout == report_payload,
          "in-process report bytes differ", problems)
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
    check(len(outputs) == 3, "fewer than three cold starts succeeded", problems)
    if outputs:
        check(all(output == outputs[0] for output in outputs),
              "cold-start outputs differ", problems)
        check(b"ok=1\n" in outputs[0], "cold-start reproduction is not ok",
              problems)
    return len(outputs)


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
        check_absent_upstream(problems)
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
          "git_scope_ok=1 absent_upstream_ok=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
