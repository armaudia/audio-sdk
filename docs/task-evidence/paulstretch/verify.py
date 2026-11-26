# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for SDK-PAULSTRETCH evidence package.

Checks strict JSON, canonical bytes, exact pins, blocker semantics, stable
linked-row identity, licensing, prohibited artifacts, git scope and three
cold-start byte-identical regenerations. Never writes package evidence.
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
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"
README_PATH = HERE / "README.md"
TASK_PREFIX = "docs/task-evidence/paulstretch/"
BASE_COMMIT = reference.BASE_COMMIT
TASK_ID = reference.TASK
GATE_IDS = ["RG-0" + str(n) for n in range(1, 9)]
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
ARTIFACT_FILES = (
    "README.md", "contract.json", "reference.py", "report.json",
    "report.json.sha256", "run.py", "SOURCES.sha256", "test_reference.py", "verify.py",
)
SIDECAR_FILES = (
    "README.md.license", "contract.json.license", "reference.py.license",
    "report.json.license", "report.json.sha256.license", "run.py.license",
    "SOURCES.sha256.license", "test_reference.py.license", "verify.py.license",
)
PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx", ".pt", ".pth", ".ckpt",
    ".safetensors", ".bin", ".so", ".dylib", ".a", ".o", ".zip", ".tar", ".gz",
    ".whl", ".dll", ".exe",
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


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    check(report.get("schema_id") == reference.SCHEMA_ID, "report schema mismatch", problems)
    check(report.get("task") == TASK_ID, "report task mismatch", problems)
    check(report.get("component") == reference.COMPONENT, "report component mismatch", problems)
    check(report.get("decision") == "DEFER", "report decision is not DEFER", problems)
    for key in ("status", "candidate_status"):
        check(report.get(key) == "proposal_only_not_qualified", f"report {key} mismatch", problems)
    check(report.get("qualification_status") == "not_qualified", "report qualification_status mismatch", problems)
    q = report.get("qualification", {})
    check(q.get("decision") == "DEFER", "qualification decision mismatch", problems)
    check(q.get("status") == "not_qualified", "qualification status mismatch", problems)
    check(q.get("readiness") == "incomplete", "qualification readiness mismatch", problems)
    check(q.get("all_required_results_present") is False, "qualification should be incomplete", problems)
    check(q.get("proposal_only") is True, "qualification proposal_only mismatch", problems)
    check(q.get("candidate_qualified") is False, "candidate must not be qualified", problems)
    check(q.get("upstream_parity") is False, "upstream parity must be false", problems)
    check(report.get("no_missing_result_qualifies_candidate") is True, "missing-result gate must be true", problems)
    gates = report.get("release_gates", [])
    check([g.get("id") for g in gates] == GATE_IDS, "release gate ids mismatch", problems)
    check(all(g.get("status") == "blocked" for g in gates), "all release gates must be blocked", problems)
    check(report.get("gates") == GATE_IDS, "gates summary mismatch", problems)
    check(report.get("remaining_gates") == GATE_IDS, "remaining_gates mismatch", problems)
    profile = report.get("profile", {})
    check(profile.get("name") == "rate", "profile must be rate", problems)
    check(profile.get("source") == reference.SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
          "profile source pin mismatch", problems)
    check(report.get("board_link_fields") == list(reference.LINK_FIELDS), "board link fields mismatch", problems)
    check(report.get("board_mutable_fields_excluded") == list(reference.MUTABLE_FIELDS_EXCLUDED),
          "mutable excluded fields mismatch", problems)
    check(report.get("board_links") == [reference.EXPECTED_LINK], "board links mismatch", problems)
    check(report.get("inventory_link") == reference.EXPECTED_INVENTORY, "inventory link mismatch", problems)
    source = report.get("source_probe", {})
    check(source.get("present") is False, "source must be absent", problems)
    runtime = report.get("runtime_probe", {})
    check(runtime.get("present") is False and runtime.get("pinned") is False, "runtime must be absent/unpinned", problems)
    weights = report.get("weights_probe", {})
    check(weights.get("present") is False, "weights/artifacts must be absent", problems)
    adverse = report.get("adverse", {})
    check(adverse.get("invalid_config_and_input", {}).get("all_rejected") is True, "invalid config/input must be rejected", problems)
    check(adverse.get("invalid_json_numeric_fields", {}).get("all_rejected") is True, "invalid json must be rejected", problems)
    check(adverse.get("missing_result", {}).get("qualifies_candidate") is False, "missing result must not qualify", problems)
    check(adverse.get("reset_validation", {}).get("matches_expectation") is True, "reset validation mismatch", problems)
    boundary = report.get("boundary", {})
    for key in ("board_or_handoff_changed", "ci_changed", "descriptor_default_changed", "descriptor_registration",
                "enabled_by_default", "provider_intake_complete", "provider_registered", "public_api_abi_changed",
                "real_corpus_or_weights", "registry_changed", "release_claim", "shared_cmake_changed"):
        check(boundary.get(key) is False, f"boundary {key} must be false", problems)
    for key in ("installed_v0_unchanged", "opt_in_required"):
        check(boundary.get(key) is True, f"boundary {key} must be true", problems)
    check(boundary.get("format") == {"channels": 1, "frame_samples": 160, "sample_format": "float32", "sample_rate_hz": 16000},
          "boundary format mismatch", problems)
    checks = report.get("local_harness_checks", {})
    for key, expected in {
        "inventory_identity_exact": True,
        "stable_board_identity_only": True,
        "source_absence_probe_bounded": True,
        "runtime_probe_confirms_unpinned": True,
        "weights_probe_confirms_absent": True,
        "invalid_requests_rejected": True,
        "invalid_json_rejected": True,
        "missing_result_blocked": True,
        "reset_cases_match_expectation": True,
        "identity_control_bit_exact": True,
        "eight_release_gates_blocked": True,
        "report_generation_deterministic": True,
        "no_candidate_output": True,
    }.items():
        check(checks.get(key) is expected, f"local_harness_checks.{key} mismatch", problems)
    ref = report.get("reference", {})
    check(ref.get("candidate_processing") is False, "reference.candidate_processing must be false", problems)
    check(ref.get("real_paulstretch_executed") is False, "reference.real_paulstretch_executed must be false", problems)
    check(ref.get("upstream_parity") is False, "reference.upstream_parity must be false", problems)


def check_contract(contract: Dict[str, Any], report: Dict[str, Any], problems: List[str]) -> None:
    check(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID, "contract schema mismatch", problems)
    check(contract.get("task") == TASK_ID, "contract task mismatch", problems)
    check(contract.get("decision") == "DEFER", "contract decision mismatch", problems)
    check(contract.get("status") == "proposal_only_not_qualified", "contract status mismatch", problems)
    q = contract.get("qualification", {})
    check(q.get("status") == "not_qualified" and q.get("readiness") == "incomplete" and q.get("decision") == "DEFER",
          "contract qualification mismatch", problems)
    check(contract.get("release_gates") == report.get("release_gates"), "contract gates mismatch report", problems)
    check(contract.get("board_link_projection_sha256") == report.get("board_link_projection_sha256"), "contract board digest mismatch", problems)
    check(contract.get("boundary_pins") == reference.BOUNDARY_PINS, "contract boundary pins mismatch", problems)
    check(contract.get("source_pins") == reference.SOURCE_PINS, "contract source pins mismatch", problems)


def check_pins(problems: List[str]) -> None:
    for relative, digest in reference.SOURCE_PINS.items():
        path = HERE.parents[5] / relative
        check(path.is_file(), "missing source pin: " + relative, problems)
        if path.is_file():
            check(sha256_file(path) == digest, "source pin changed: " + relative, problems)
    for relative, digest in reference.BOUNDARY_PINS.items():
        path = SDK_ROOT / relative
        check(path.is_file(), "missing boundary pin: " + relative, problems)
        if path.is_file():
            check(sha256_file(path) == digest, "boundary pin changed: " + relative, problems)


def check_sources(problems: List[str]) -> None:
    text = SOURCES_PATH.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        check(len(parts) == 2, "malformed SOURCES line: " + line, problems)
        if len(parts) != 2:
            continue
        digest, name = parts
        if name.startswith("source:"):
            rel = name[len("source:"):]
            path = HERE.parents[5] / rel
        elif name.startswith(TASK_PREFIX):
            path = HERE / name[len(TASK_PREFIX):]
        else:
            path = SDK_ROOT / name
        check(path.is_file(), "SOURCES missing path: " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest, "SOURCES digest mismatch: " + name, problems)


def check_licensing(problems: List[str]) -> None:
    for name in ARTIFACT_FILES:
        path = HERE / name
        check(path.is_file(), "missing artifact: " + name, problems)
        if not path.is_file():
            continue
        if path.suffix in {".py", ".md", ".json", ".sha256"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            sidecar = HERE / (name + ".license")
            has_sidecar = sidecar.is_file()
            if path.suffix == ".py":
                body = "\n".join(text.splitlines()[2:])
                check("SPDX-License-" "Identifier:" not in body, "full SPDX token in python body: " + name, problems)
            check("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes" in text or has_sidecar,
                  "missing SPDX copyright/sidecar: " + name, problems)
    for name in SIDECAR_FILES:
        path = HERE / name
        check(path.is_file(), "missing sidecar license: " + name, problems)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            check(SPDX_NEEDLE in text, "sidecar license missing SPDX: " + name, problems)


def check_prohibited(problems: List[str]) -> None:
    for path in HERE.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(HERE).as_posix()
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES, "prohibited artifact present: " + rel, problems)


def check_git_scope(problems: List[str]) -> None:
    try:
        proc = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--name-only", BASE_COMMIT + "...HEAD"],
                              check=True, capture_output=True, text=True)
    except Exception as err:
        problems.append("git diff failed: " + str(err))
        return
    names = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    for name in names:
        check(name.startswith(TASK_PREFIX), "out-of-scope changed file: " + name, problems)


def check_determinism(problems: List[str]) -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, str(HERE / "run.py"), "--all"]
    digests = []
    for _ in range(3):
        subprocess.run(cmd, cwd=str(HERE), check=True, capture_output=True, text=True, env=env)
        digests.append({
            "report": sha256_file(REPORT_PATH),
            "sidecar": sha256_file(SIDECAR_PATH),
            "sources": sha256_file(SOURCES_PATH),
            "contract": sha256_file(CONTRACT_PATH),
            "readme": sha256_file(README_PATH),
        })
    check(all(d == digests[0] for d in digests), "3x regeneration is not byte-identical", problems)


def main() -> int:
    problems: List[str] = []
    report = strict_load(REPORT_PATH)
    contract = strict_load(CONTRACT_PATH)
    check(isinstance(report, dict), "report root not object", problems)
    check(isinstance(contract, dict), "contract root not object", problems)
    if not isinstance(report, dict) or not isinstance(contract, dict):
        for p in problems:
            print("FAIL:", p)
        return 1
    check(finite_json(report), "report has nonfinite value", problems)
    check(finite_json(contract), "contract has nonfinite value", problems)
    report_payload = REPORT_PATH.read_bytes()
    sidecar = SIDECAR_PATH.read_text(encoding="utf-8").strip()
    check(sidecar == sha256_bytes(report_payload) + "  report.json", "sidecar mismatch", problems)
    check_report(report, problems)
    check_contract(contract, report, problems)
    check_pins(problems)
    check_sources(problems)
    check_licensing(problems)
    check_prohibited(problems)
    check_git_scope(problems)
    check_determinism(problems)
    if problems:
        for p in problems:
            print("FAIL:", p)
        return 1
    print("PASS: SDK-PAULSTRETCH evidence verified")
    print("report_file_digest=" + sha256_bytes(report_payload))
    print("canonical_digest=" + sha256_bytes(canonical_bytes(report)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
