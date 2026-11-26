#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only fail-closed verification of the NVIDIA RE-USE boundary package."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run as generator  # noqa: E402

TASK_PREFIX = reference.TASK_PREFIX
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
SOURCES = HERE / "SOURCES.sha256"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_json(errors: List[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    report: Dict[str, Any] = {}
    contract: Dict[str, Any] = {}
    for path, target in ((REPORT, report), (CONTRACT, contract)):
        if not path.is_file():
            errors.append("missing " + path.name)
            continue
        try:
            parsed = reference.strict_json_loads(path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                target.update(parsed)
            else:
                errors.append(path.name + " root is not object")
        except reference.JsonError as error:
            errors.append(path.name + " is not strict JSON: " + str(error))
    return report, contract


def check_report(report: Dict[str, Any], errors: List[str]) -> bool:
    expected = reference.report_bytes()
    ok = REPORT.is_file() and REPORT.read_bytes() == expected
    if not ok:
        errors.append("report.json is not byte-reproducible")
    sidecar = (sha256(expected) + "  report.json\n").encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != sidecar:
        errors.append("report.json.sha256 mismatch")
        ok = False
    for key, want in (("decision", "DEFER"), ("qualification_status", "not_qualified"), ("status", "proposal_only_not_qualified")):
        if report.get(key) != want:
            errors.append("report " + key + " is not " + want)
            ok = False
    gates = report.get("release_gates", [])
    if len(gates) != 8 or any(gate.get("status") != "blocked" for gate in gates):
        errors.append("eight blocked release gates are not recorded")
        ok = False
    if report.get("board_full_file_hashed") is not False:
        errors.append("mutable full board is hashed")
        ok = False
    return ok


def check_contract(contract: Dict[str, Any], errors: List[str]) -> bool:
    try:
        report_payload = reference.report_bytes()
        report = reference.strict_json_loads(report_payload.decode("utf-8"))
        sidecar_payload = (sha256(report_payload) + "  report.json\n").encode("ascii")
        sources_payload = generator.build_sources_bytes(report_payload, sidecar_payload)
        expected = generator.build_contract_bytes(report_payload, report, sidecar_payload, sources_payload)
    except Exception as error:  # noqa: BLE001
        errors.append("cannot rebuild contract: " + str(error))
        return False
    ok = CONTRACT.is_file() and CONTRACT.read_bytes() == expected
    if not ok:
        errors.append("contract.json is not byte-reproducible")
    if contract.get("board_full_file_hashed") is not False:
        errors.append("contract hashes mutable full board")
        ok = False
    return ok


def check_sources(errors: List[str]) -> bool:
    try:
        report_payload = reference.report_bytes()
        sidecar_payload = (sha256(report_payload) + "  report.json\n").encode("ascii")
        expected = generator.build_sources_bytes(report_payload, sidecar_payload)
    except Exception as error:  # noqa: BLE001
        errors.append("cannot rebuild sources: " + str(error))
        return False
    ok = SOURCES.is_file() and SOURCES.read_bytes() == expected
    if not ok:
        errors.append("SOURCES.sha256 is not byte-reproducible")
    pin_line = re.compile(r"^[0-9a-f]{64}  (.+)$")
    for line in SOURCES.read_text(encoding="utf-8").splitlines() if SOURCES.exists() else []:
        match = pin_line.fullmatch(line)
        if match and "plan/swarm/TASKS.json" in match.group(1):
            errors.append("SOURCES.sha256 pins the mutable full board")
            ok = False
    return ok


def check_reproduction(errors: List[str]) -> Tuple[bool, List[str]]:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    digests: List[str] = []
    for index in range(3):
        result = subprocess.run(
            [sys.executable, str(HERE / "run.py"), "--stdout-report"],
            cwd=str(HERE), env=environment, capture_output=True, check=False)
        if result.returncode != 0:
            errors.append("cold report regeneration " + str(index) + " failed: " + result.stderr.decode("utf-8", "replace").strip())
            return False, digests
        digests.append(sha256(result.stdout))
    if len(set(digests)) != 1:
        errors.append("cold report regeneration is not byte-identical")
        return False, digests
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--verify-repro"],
        cwd=str(HERE), env=environment, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("committed bundle differs from generated bundle: " + (result.stderr.strip() or result.stdout.strip()))
        return False, digests
    return True, digests


def check_licensing(errors: List[str]) -> bool:
    copyright_line = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"
    license_line = "SPDX-" + "License-Identifier: Apache-2.0"
    ok = True
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if path.suffix in (".py", ".md"):
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
            if copyright_line not in head or license_line not in head:
                errors.append("missing SPDX header: " + path.name)
                ok = False
        elif path.suffix in (".json", ".sha256") and not path.name.endswith(".license"):
            sidecar = path.with_name(path.name + ".license")
            if not sidecar.is_file():
                errors.append("missing SPDX sidecar: " + sidecar.name)
                ok = False
                continue
            text = sidecar.read_text(encoding="utf-8")
            if copyright_line not in text or license_line not in text:
                errors.append("invalid SPDX sidecar: " + sidecar.name)
                ok = False
    license_sidecar = HERE / "SOURCES.sha256.license"
    if not license_sidecar.is_file():
        errors.append("missing SPDX sidecar: SOURCES.sha256.license")
        ok = False
    elif copyright_line not in license_sidecar.read_text(encoding="utf-8"):
        errors.append("invalid SPDX sidecar: SOURCES.sha256.license")
        ok = False
    reuse = HERE.parents[2] / "REUSE.toml"
    if not reuse.is_file() or '"docs/**"' not in reuse.read_text(encoding="utf-8"):
        errors.append("REUSE.toml does not cover docs/**")
        ok = False
    return ok


def check_scope(errors: List[str]) -> bool:
    sdk = HERE.parents[2]
    result = subprocess.run(
        ["git", "-C", str(sdk), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True, check=True)
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
    report, contract = check_json(errors)
    report_ok = check_report(report, errors)
    contract_ok = check_contract(contract, errors)
    sources_ok = check_sources(errors)
    reproduction_ok, digests = check_reproduction(errors)
    licensing_ok = check_licensing(errors)
    scope_ok = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print("verify_result=FAILED report_ok=" + str(report_ok) + " contract_ok=" + str(contract_ok) + " sources_ok=" + str(sources_ok) + " reproduction_ok=" + str(reproduction_ok) + " licensing_ok=" + str(licensing_ok) + " scope_ok=" + str(scope_ok))
        return 1
    print("verify_result=OK report_ok=True contract_ok=True sources_ok=True reproduction_ok=True cold_repeats=" + str(len(digests)) + " licensing_ok=True scope_ok=True report_sha256=" + digests[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
