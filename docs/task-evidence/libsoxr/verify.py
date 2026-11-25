# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the SDK-LIBSOXR evidence package.

It checks pins, strict JSON, canonical report reproduction, three cold-start
regenerations, rate semantics, blocker status, stable board identity, licensing
headers, prohibited upstream artifacts and task-local git scope. It never
writes package evidence.
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
TASK_PREFIX = "docs/task-evidence/libsoxr/"
TASK_ID = "SDK-LIBSOXR"
GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]
PROHIBITED_NAMES = {
    "soxr.h", "soxr.h.in", "soxr.c", "rate.c", "fft4g64.c", "fft4g.c",
    "soxr-lsr.c", "pffft.c", "COPYING", "COPYING.LGPL", "COPYING.LESSER",
    "LGPL-2.1.txt", "LGPL-2.1-or-later.txt",
}
PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx", ".pt", ".bin",
    ".so", ".dylib", ".a", ".o", ".zip", ".tar", ".gz",
}
UPSTREAM_KEYS = {
    "status", "artifact", "expected_license", "pinned_revision",
    "source_digest", "no_upstream_parity_claim", "required_files",
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
        raise VerificationError("nonfinite JSON constant in " + path.name + ": " + token)

    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as error:
        raise VerificationError("invalid JSON in " + path.name + ": " + str(error))


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
    check(contract.get("task") == TASK_ID, "contract task mismatch", problems)
    check(contract.get("component") == "libsoxr", "contract component mismatch", problems)
    check(contract.get("branch") == "swarm/SDK-LIBSOXR", "contract branch mismatch", problems)
    check(contract.get("base_commit") ==
          "a91a45e32428df353dbf55a7a9fd2ec052760539",
          "contract base commit mismatch", problems)
    check(contract.get("decision") == "DEFER", "contract decision is not DEFER", problems)
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
    boundary = contract.get("boundary", {})
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
    check(boundary.get("format") == {
        "sample_rate_hz": 16000, "channels": 1,
        "sample_format": "float32", "frame_samples": 160,
    }, "contract v0 format mismatch", problems)
    blocker = contract.get("upstream_blocker", {})
    check(set(blocker) == UPSTREAM_KEYS, "upstream blocker schema mismatch", problems)
    check(blocker.get("status") == "blocked_upstream_absent",
          "upstream blocker status mismatch", problems)
    check(blocker.get("pinned_revision") is None,
          "upstream blocker has a fabricated revision", problems)
    check(blocker.get("source_digest") is None,
          "upstream blocker has a fabricated source digest", problems)
    check(blocker.get("no_upstream_parity_claim") is True,
          "upstream parity claim is not disabled", problems)
    check(blocker.get("expected_license") == "LGPL-2.1-or-later",
          "expected upstream licence mismatch", problems)
    gates = contract.get("release_gates", [])
    check([gate.get("id") for gate in gates] == GATE_IDS,
          "contract release gate identities mismatch", problems)
    check(len(gates) == 8 and all(gate.get("status") == "blocked"
                                 for gate in gates),
          "not all eight release gates are blocked", problems)
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


def check_pins(contract: Dict[str, Any], report: Dict[str, Any],
               problems: List[str]) -> int:
    checked = 0
    for name, digest in contract.get("artifact_pins", {}).items():
        path = HERE / name
        check(path.is_file(), "missing artifact " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest, "artifact pin mismatch: " + name, problems)
            checked += 1
    for name, digest in report.get("artifact_pins", {}).items():
        path = HERE / name
        check(path.is_file(), "missing report artifact " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest,
                  "report artifact pin mismatch: " + name, problems)
            checked += 1
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
    # SOURCES.sha256 must be parseable and every listed digest must match.
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
    check(SIDECAR_PATH.read_text(encoding="utf-8").strip() ==
          sha256_file(REPORT_PATH) + "  report.json",
          "report sidecar content mismatch", problems)
    return checked


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") == "audio-sdk/libsoxr-reference-report/0.1",
          "report schema mismatch", problems)
    check(report.get("task") == TASK_ID, "report task mismatch", problems)
    check(report.get("decision") == "DEFER", "report decision is not DEFER", problems)
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
    check(report.get("no_missing_result_qualifies_candidate") is True,
          "missing-result guard is disabled", problems)
    cases = report.get("rate_cases", {})
    check(len(cases) == 24, "expected 24 rate cases", problems)
    for name, case in cases.items():
        check(case.get("duration_exact") is True,
              "duration mismatch: " + name, problems)
        check(case.get("map_monotonic") is True,
              "non-monotonic map: " + name, problems)
        check(case.get("partition_ok") is True,
              "source partition failure: " + name, problems)
        check(case.get("nonfinite_count") == 0,
              "nonfinite output: " + name, problems)
        check(case.get("output_samples") == case.get("expected_output_samples"),
              "length mismatch: " + name, problems)
    required = report.get("required_results", {})
    check(bool(required) and all(value is True for value in required.values()),
          "a required local result is false", problems)
    gates = report.get("release_gates", [])
    check([gate.get("id") for gate in gates] == GATE_IDS,
          "report release gate identities mismatch", problems)
    check(len(gates) == 8 and all(gate.get("status") == "blocked"
                                 for gate in gates),
          "not all eight report gates are blocked", problems)
    adverse = report.get("adverse", {})
    for key in ("invalid_config_and_input", "invalid_json_numeric_fields"):
        block = adverse.get(key, {})
        check(block.get("all_rejected") is True,
              "adverse cases are not all rejected: " + key, problems)
        check(block.get("metrics") is None,
              "adverse block exposes metrics: " + key, problems)
        for case in block.get("cases", []):
            check(case.get("error") != "NOT_REJECTED",
                  "adverse case accepted: " + str(case), problems)
    missing = adverse.get("missing_result", {})
    check(missing.get("status") == "blocked", "missing result is not blocked", problems)
    check(missing.get("metrics") is None, "missing result exposes metrics", problems)
    check(missing.get("qualifies_candidate") is False,
          "missing result qualifies a candidate", problems)
    reference_block = report.get("reference", {})
    check(reference_block.get("real_libsoxr_source_or_binary") is False,
          "report claims real libsoxr source", problems)
    check(reference_block.get("upstream_parity") is False,
          "report reference claims parity", problems)
    check(reference_block.get("downloads") is False, "report claims downloads", problems)
    check(report.get("crosscheck", {}).get("byte_identical") is True,
          "crosscheck is not byte-identical", problems)
    check(report.get("alias_suppression", {}).get("filtered_suppression_db", 0) <= -40.0,
          "alias suppression is too weak", problems)
    check(report.get("image_rejection", {}).get("filtered_suppression_db", 0) <= -40.0,
          "image rejection is too weak", problems)
    check(report.get("speech_preservation", {}).get("voiced_to_pause_db", 0) >= 10.0,
          "speech preservation proxy is too weak", problems)
    partial = report.get("final_partial_window", {})
    check(partial.get("output_samples") == partial.get("expected_output_samples"),
          "final partial window length mismatch", problems)
    rebuffer = report.get("rebuffer", {})
    check(rebuffer.get("played_samples") == 9600,
          "rebuffer did not play all samples", problems)
    check(rebuffer.get("skipped_audio_samples") == 0,
          "rebuffer skipped audio", problems)
    variable = report.get("variable_rate", {})
    check(variable.get("duration_exact") is True,
          "variable-rate segment length mismatch", problems)
    check(variable.get("smooth_soxr_set_io_ratio_behavior_claimed") is False,
          "variable-rate parity is overclaimed", problems)


def check_board(contract: Dict[str, Any], report: Dict[str, Any],
                problems: List[str]) -> None:
    board = strict_load(BOARD_PATH)
    tasks = {task["id"]: task for task in board.get("tasks", [])}
    locals_ = [row for row in contract.get("board_links", [])
               if row.get("task_id") == TASK_ID]
    check(len(locals_) == 1, "contract must link exactly one SDK-LIBSOXR row", problems)
    if locals_:
        row = locals_[0]
        task = tasks.get(TASK_ID, {})
        check(row.get("title") == task.get("title"), "board title mismatch", problems)
        check(row.get("mode") == task.get("mode"), "board mode mismatch", problems)
        check(row.get("repository") == task.get("repository"),
              "board repository mismatch", problems)
        check(row.get("component") == task.get("component"),
              "board component mismatch", problems)
    expected = []
    for row in contract.get("board_links", []):
        task = tasks.get(row.get("task_id"), {})
        expected.append({
            "task_id": row.get("task_id"),
            "title": task.get("title"),
            "mode": task.get("mode"),
            "repository": task.get("repository"),
            "component": task.get("component"),
        })
    expected.sort(key=lambda item: item["task_id"])
    digest = sha256_bytes(canonical_bytes(expected))
    check(digest == contract.get("board_link_projection_sha256"),
          "contract board projection digest mismatch", problems)
    check(digest == report.get("board_link_projection_sha256"),
          "report board projection digest mismatch", problems)
    check(report.get("board_links") == expected,
          "report board links differ from stable identity projection", problems)
    # Status, owner and history are deliberately absent from the projection.
    for row in expected:
        check("status" not in row and "owner" not in row and "history" not in row,
              "mutable board fields entered the projection", problems)


def check_licensing(problems: List[str]) -> None:
    required = [
        "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "reference.py",
        "run.py", "verify.py", "test_reference.py", "check_licensing.py",
        "contract.json", "report.json", "report.json.sha256", "SOURCES.sha256",
    ]
    for name in required:
        check((HERE / name).is_file(), "missing licensing artifact " + name, problems)
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        check("SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes" in head,
              "missing copyright SPDX in " + path.name, problems)
        check("SPDX" "-License-Identifier: Apache-2.0" in head,
              "missing licence SPDX in " + path.name, problems)
    for name in ("README.md", "LICENSE", "THIRD_PARTY_NOTICES.md"):
        head = "\n".join((HERE / name).read_text(encoding="utf-8").splitlines()[:5])
        check("SPDX" in head, "missing SPDX note in " + name, problems)
    notices = (HERE / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    check("libsoxr" in notices and "LGPL-2.1-or-later" in notices,
          "third-party notice is incomplete", problems)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    check('"docs/**"' in reuse and
          'SPDX' '-License-Identifier = "Apache-2.0"' in reuse,
          "REUSE.toml does not cover docs/** as Apache-2.0", problems)
    check((SDK_ROOT / "LICENSES/Apache-2.0.txt").is_file(),
          "LICENSES/Apache-2.0.txt missing", problems)


def check_absent_upstream(problems: List[str]) -> None:
    for path in sorted(HERE.iterdir()):
        if path.name in {"__pycache__"}:
            continue
        check(path.name not in PROHIBITED_NAMES,
              "prohibited upstream artifact present: " + path.name, problems)
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES,
              "prohibited binary/audio artifact present: " + path.name, problems)
    for path in HERE.rglob("*"):
        if path.is_file():
            check(path.name not in PROHIBITED_NAMES,
                  "prohibited upstream artifact present: " + path.name, problems)
            check(path.suffix.lower() not in PROHIBITED_SUFFIXES,
                  "prohibited binary/audio artifact present: " + str(path), problems)


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
    check(diff_check.returncode == 0, "git diff --check reported whitespace errors",
          problems)


def check_cold_starts(report_payload: bytes, problems: List[str]) -> int:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    repeats = 0
    for _index in range(3):
        process = subprocess.run(
            [sys.executable, str(HERE / "run.py"), "--stdout-report"],
            cwd=str(HERE), capture_output=True, env=environment, check=False)
        if process.returncode != 0:
            problems.append("cold-start report generation failed")
            continue
        check(process.stdout == report_payload,
              "cold-start report bytes differ", problems)
        repeats += 1
    return repeats


def check_reproduction(report_payload: bytes, problems: List[str]) -> bool:
    process = subprocess.run(
        [sys.executable, "-c",
         "import reference,sys;sys.stdout.buffer.write(reference.report_bytes())"],
        cwd=str(HERE), capture_output=True, check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if process.returncode != 0:
        problems.append("in-process report regeneration failed")
        return False
    return process.stdout == report_payload


def main() -> int:
    problems: List[str] = []
    try:
        contract = strict_load(CONTRACT_PATH)
        report = strict_load(REPORT_PATH)
        report_payload = REPORT_PATH.read_bytes()
        check(isinstance(contract, dict), "contract root is not an object", problems)
        check(isinstance(report, dict), "report root is not an object", problems)
        check_contract(contract, report, problems)
        pins_checked = check_pins(contract, report, problems)
        check_report(report, problems)
        check_board(contract, report, problems)
        check_licensing(problems)
        check_absent_upstream(problems)
        reproduction_ok = check_reproduction(report_payload, problems)
        repeats = check_cold_starts(report_payload, problems)
        check_git_scope(problems)
        check(report_payload.endswith(b"\n") and b"\n\n" not in report_payload,
              "report must have exactly one trailing newline", problems)
        check(finite_json(report), "report contains a nonfinite value", problems)
        check(finite_json(contract), "contract contains a nonfinite value", problems)
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
          " semantics_ok=1 boundary_ok=1 licensing_ok=1 git_scope_ok=1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
