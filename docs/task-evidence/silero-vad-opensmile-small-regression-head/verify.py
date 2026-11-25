# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local evidence package."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import check_licensing
import reference

HERE = Path(__file__).resolve().parent
TEMP_ROOT = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
TASK_PREFIX = "docs/task-evidence/silero-vad-opensmile-small-regression-head/"
PIN_LINE = re.compile(r"^([0-9a-f]{64})  ((?:pkg|source|worktree):[A-Za-z0-9_./-]+)$")


def sdk_root() -> Path:
    override = os.environ.get("SDK_ROOT")
    if override and (Path(override) / "REUSE.toml").is_file():
        return Path(override)
    cursor = HERE
    while cursor != cursor.parent:
        if (cursor / "REUSE.toml").is_file() and (cursor / "LICENSES").is_dir():
            return cursor
        cursor = cursor.parent
    return HERE.parents[2]


SDK = sdk_root()
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(raw: str) -> bool:
    return bool(raw) and not raw.startswith("/") and ".." not in Path(raw).parts


def parse_pins(errors: List[str]) -> Dict[str, Tuple[str, Path]]:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return {}
    lines = PINS.read_text(encoding="utf-8").splitlines()
    if not lines or not any(line.startswith("#") for line in lines):
        errors.append("SOURCES.sha256 has no provenance header")
    pins: Dict[str, Tuple[str, Path]] = {}
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        match = PIN_LINE.fullmatch(line)
        if not match:
            errors.append("malformed pin: " + repr(line))
            continue
        digest, label = match.groups()
        prefix, raw = label.split(":", 1)
        if not safe_relative(raw):
            errors.append("unsafe pin path: " + label)
            continue
        if label in pins:
            errors.append("duplicate pin: " + label)
            continue
        path = {"pkg": HERE, "source": SOURCE_ROOT, "worktree": SDK}[prefix] / raw
        pins[label] = (digest, path)
    if not pins:
        errors.append("no pins found")
    authored = {path.name for path in HERE.iterdir()
                if path.is_file() and path.name not in ("SOURCES.sha256",)
                and "__pycache__" not in path.name}
    for name in sorted(authored):
        if "pkg:" + name not in pins:
            errors.append("unpinned package file: " + name)
    return pins


def check_pin_targets(pins: Dict[str, Tuple[str, Path]], errors: List[str]) -> int:
    checked = 0
    for label, (digest, path) in sorted(pins.items()):
        if not path.is_file():
            errors.append("missing pin target: " + label)
            continue
        actual = sha256(path.read_bytes())
        if actual != digest:
            errors.append(f"pin mismatch: {label} expected={digest} actual={actual}")
        else:
            checked += 1
    return checked


def strict_json(path: Path, errors: List[str]) -> Dict[str, Any] | None:
    try:
        return reference.strict_loads(path.read_text(encoding="utf-8"))
    except Exception as error:
        errors.append(f"strict json failed for {path.name}: {error}")
        return None


def check_report(report: Dict[str, Any] | None, errors: List[str]) -> bool:
    if report is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        if not condition:
            errors.append(message)
            ok = False

    expect(report.get("task_id") == reference.TASK_ID, "task_id mismatch")
    expect(report.get("base_commit") == reference.BASE_COMMIT, "base_commit mismatch")
    expect(report.get("profile") == "rate", "profile is not rate")
    expect(report.get("status") == "proposal_only_synthetic_incomplete", "status mismatch")
    expect(report.get("qualification_status") == "not_qualified", "qualification mismatch")
    expect(report.get("candidate_qualified") is False, "candidate_qualified is not false")
    expect(report.get("no_missing_result_qualifies_candidate") is True, "missing-result guard missing")
    expect(report.get("format") == reference.FORMAT, "v0 geometry changed")
    boundary = report.get("boundary", {})
    for key in ("registered", "enabled_by_default", "default_selected", "public_api_abi_change",
                "provider_registration", "production_callback_registered",
                "public_variable_frame_actuator"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    expect(boundary.get("descriptor_settings") == {}, "descriptor settings are not empty")
    expect(boundary.get("installed_v0_geometry_preserved") is True, "installed v0 geometry not preserved")
    expect(len(report.get("gates", [])) == len(reference.GATE_REOPEN), "gate count mismatch")
    expect(all(gate.get("status") == "blocked" for gate in report.get("gates", [])),
           "a gate is not blocked")
    expect(report.get("source_reported_context", {}).get("label") == "source_reported_not_measured_here",
           "source-reported context is not labeled")
    expect(report.get("observations", {}).get("silence", {}).get("nonfinite_samples") == 0,
           "nonfinite silence output")
    expect(report.get("observations", {}).get("impulse", {}).get("transient_proxy", {}).get("audibility")
           == "not_measured", "transient audibility claimed")
    expect(report.get("observations", {}).get("buffer_simulation", {}).get("device_timing")
           == "not_measured", "device timing claimed")
    expect(all(value in ("rejected", True) for group in report.get("adverse", {}).values()
               for value in group.values()), "an adverse case was not rejected")
    expect(bool(report.get("regressions")), "no regressions recorded")
    expect(bool(report.get("non_claims")), "non-claims missing")
    return ok


def check_contract(contract: Dict[str, Any] | None, pins: Dict[str, Tuple[str, Path]],
                   errors: List[str]) -> bool:
    if contract is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        if not condition:
            errors.append(message)
            ok = False

    expect(contract.get("task") == reference.TASK_ID, "contract task mismatch")
    expect(contract.get("base_commit") == reference.BASE_COMMIT, "contract base commit mismatch")
    expect(contract.get("verification_profile") == "rate", "contract profile mismatch")
    expect(contract.get("write_scope") == TASK_PREFIX, "contract write scope mismatch")
    expect(contract.get("status") == "proposal_only_synthetic_incomplete", "contract status mismatch")
    expect(contract.get("candidate_qualified") is False, "contract claims qualification")
    expect(contract.get("boundary", {}).get("registered") is False, "contract is registered")
    expect(contract.get("boundary", {}).get("enabled_by_default") is False, "contract enabled by default")
    source_pins = contract.get("source_pins", {})
    expected_sources = {label for label in pins if not label.startswith("pkg:")}
    expect(set(source_pins) == expected_sources, "contract source pin set differs from SOURCES.sha256")
    for label, expected in source_pins.items():
        if label in pins and pins[label][0] != expected:
            errors.append("contract pin digest differs: " + label)
            ok = False
    artifacts = contract.get("artifact_pins", {})
    for label, (digest, _path) in pins.items():
        if label.startswith("pkg:") and label.split(":", 1)[1] not in ("contract.json", "SOURCES.sha256"):
            if artifacts.get(label.split(":", 1)[1]) != digest:
                errors.append("artifact pin differs: " + label)
                ok = False
    return ok


def check_reproduction(errors: List[str]) -> Tuple[bool, str, List[str]]:
    expected = reference.canonical_report_bytes(reference.build_report())
    digest = sha256(expected)
    ok = REPORT.is_file() and REPORT.read_bytes() == expected
    if not ok:
        errors.append("report.json is not byte-reproducible")
    sidecar = f"{digest}  report.json\n".encode("utf-8")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar:
        errors.append("report.json.sha256 mismatch")
        ok = False
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    repeats: List[str] = []
    try:
        work = Path(tempfile.mkdtemp(prefix="silero-rate-verify-", dir=root))
        try:
            for index in range(3):
                target = work / f"cold-{index}"
                environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
                result = subprocess.run(
                    [sys.executable, str(HERE / "run.py"), "--out", str(target)],
                    cwd=str(HERE), env=environment, capture_output=True, text=True, check=False)
                generated = target / "report.json"
                if result.returncode != 0 or not generated.is_file():
                    errors.append(f"cold regeneration {index} failed: {result.stderr.strip()}")
                    ok = False
                    continue
                data = generated.read_bytes()
                repeats.append(sha256(data))
                if data != expected:
                    errors.append(f"cold regeneration {index} is not byte-identical")
                    ok = False
        finally:
            shutil.rmtree(work, ignore_errors=True)
    except OSError as error:
        errors.append("cold regeneration scratch unavailable: " + str(error))
        ok = False
    return ok, digest, repeats


def check_scope(errors: List[str]) -> bool:
    if not (SDK / ".git").exists():
        return True
    result = subprocess.run(["git", "-C", str(SDK), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True, check=True)
    ok = True
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            errors.append("out of scope change: " + path)
            ok = False
    return ok


def main() -> int:
    errors: List[str] = []
    pins = parse_pins(errors)
    verified = check_pin_targets(pins, errors)
    report = strict_json(REPORT, errors)
    contract = strict_json(CONTRACT, errors)
    json_ok = report is not None and contract is not None
    report_ok = check_report(report, errors)
    contract_ok = check_contract(contract, pins, errors)
    reproduction_ok, digest, repeats = check_reproduction(errors)
    licensing = check_licensing.check()
    if licensing["status"] != "ok":
        errors.extend("licensing: " + problem for problem in licensing["problems"])
    scope_ok = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"verify_result=FAILED pins={verified}/{len(pins)} json_ok={json_ok} "
              f"report_ok={report_ok} contract_ok={contract_ok} licensing_ok={licensing['status'] == 'ok'} "
              f"scope_ok={scope_ok} reproduction_ok={reproduction_ok} report_sha256={digest}")
        return 1
    print(f"verify_result=OK pins={verified}/{len(pins)} json_ok={json_ok} "
          f"report_ok={report_ok} contract_ok={contract_ok} licensing_ok=True scope_ok=True "
          f"reproduction_ok={reproduction_ok} cold_repeats={len(repeats)} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
