# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the PBFDAF/AUMDF blocker evidence package."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
TEMP_ROOT = Path(os.environ.get("TEMP_ROOT", "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode"))

sys.path.insert(0, str(HERE))
import reference  # noqa: E402

REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
SOURCES = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def sha256(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def _expect(ok: bool, msg: str, errors: List[str]) -> bool:
    if not ok:
        errors.append(msg)
    return ok


def strict_load(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    def reject_const(x: str):
        raise ValueError("non-finite JSON")
    obj = json.loads(text, parse_constant=reject_const)
    # duplicate key detection
    dupes: List[str] = []
    def pairs_hook(items):
        d = {}
        for k, v in items:
            if k in d:
                dupes.append(k)
            d[k] = v
        return d
    json.loads(text, parse_constant=reject_const, object_pairs_hook=pairs_hook)
    if dupes:
        raise ValueError(f"duplicate keys: {dupes}")
    if not isinstance(obj, dict):
        raise ValueError("expected object")
    return obj


def check_strict_json(errors: List[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    report = strict_load(REPORT)
    contract = strict_load(CONTRACT)
    _expect(REPORT.read_bytes().endswith(b"\n"), "report.json missing trailing newline", errors)
    _expect(CONTRACT.read_bytes().endswith(b"\n"), "contract.json missing trailing newline", errors)
    _expect(report == json.loads(reference.canonical_report_bytes(report).decode("utf-8")), "report.json not canonical", errors)
    _expect(contract == json.loads(reference.canonical_contract_bytes().decode("utf-8")), "contract.json not canonical", errors)
    return report, contract


def check_report_contract(report: Dict[str, Any], contract: Dict[str, Any], errors: List[str]) -> None:
    _expect(report["task_id"] == reference.TASK, "task mismatch", errors)
    _expect(report["decision"] == "DEFER", "decision not DEFER", errors)
    _expect(report["evidence_status"] == "incomplete", "evidence not incomplete", errors)
    _expect(report["qualification_status"] == "not_qualified", "qualification not not_qualified", errors)
    _expect(report["qualification"]["candidate_qualified"] is False, "candidate qualified", errors)
    _expect(report["qualification"]["no_missing_result_qualifies_candidate"] is True, "missing result can qualify", errors)
    _expect(contract["decision"] == "DEFER", "contract decision mismatch", errors)
    _expect(contract["qualification"]["status"] == "not_qualified", "contract qualification mismatch", errors)
    _expect(len(report["gates"]) == 8, "gate count", errors)
    _expect(all(g["status"] == "blocked" for g in report["gates"]), "gate not blocked", errors)
    _expect(report["profile"] == "room", "profile mismatch", errors)
    _expect(report["boundary"]["public_api_abi_change"] is False, "boundary changed", errors)
    _expect(report["boundary"]["provider_registration"] is False, "provider registration", errors)

    # no whole-file TASKS.json digest/hash
    report_text = REPORT.read_text(encoding="utf-8")
    _expect("3154212165862651640b2388b4ce8dd62b5a71ad808152820f9b3831488beb89" not in report_text,
            "report contains mutable full TASKS.json digest", errors)
    _expect('"whole_file_hashed":false' in report_text, "whole_file_hashed missing/true", errors)
    _expect(re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', report_text) is None,
            "report pins TASKS.json as digest entry", errors)

    # stable row identity only
    identity = report.get("task_row_identity", {})
    _expect(identity.get("whole_file_hashed") is False, "task_row whole_file_hashed", errors)
    _expect(set(identity.get("stable_fields", {}).keys()) == set(reference.STABLE_TASK_FIELDS), "stable fields mismatch", errors)
    _expect("owner" in identity.get("excluded_mutable_fields", []), "owner not excluded", errors)


def check_pins(errors: List[str]) -> bool:
    ok = True
    for rel, expected in reference.SOURCE_PINS.items():
        path = SOURCE_ROOT / rel
        ok = _expect(path.is_file(), f"missing source pin target {rel}", errors) and ok
        if path.is_file():
            ok = _expect(sha256(path.read_bytes()) == expected, f"source pin mismatch {rel}", errors) and ok
    for rel, expected in reference.BOUNDARY_PINS.items():
        path = SDK_ROOT / rel
        ok = _expect(path.is_file(), f"missing boundary pin target {rel}", errors) and ok
        if path.is_file():
            ok = _expect(sha256(path.read_bytes()) == expected, f"boundary pin mismatch {rel}", errors) and ok
    return ok


def check_assets(errors: List[str]) -> bool:
    live = reference.audit_assets()
    ok = True
    ok = _expect(live["all_absence_probes_absent"] is True, "absence probe present; re-evaluate blocker", errors) and ok
    ok = _expect(live["source_checkout_present"] is False, "source checkout appeared", errors) and ok
    ok = _expect(live["weights_present"] is False, "weights appeared", errors) and ok
    ok = _expect(live["rights_record_present"] is False, "rights record appeared", errors) and ok
    ok = _expect(live["cohort_manifest_present"] is False, "cohort manifest appeared", errors) and ok
    ok = _expect(live["parity_manifest_present"] is False, "parity manifest appeared", errors) and ok
    return ok


def check_reproduction(errors: List[str]) -> Tuple[bool, str]:
    expected = reference.canonical_report_bytes(reference.build_report())
    digest = sha256(expected)
    sidecar = f"{digest}  report.json\n".encode("utf-8")
    ok = _expect(REPORT.read_bytes() == expected, "report.json not reproducible", errors)
    ok = _expect(SIDECAR.read_bytes() == sidecar, "report sidecar mismatch", errors) and ok
    ok = _expect(CONTRACT.read_bytes() == reference.canonical_contract_bytes(), "contract not reproducible", errors) and ok

    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    with tempfile.TemporaryDirectory(prefix="pbfdaf-verify-", dir=root) as td:
        work = Path(td)
        digests = []
        for i in range(3):
            out = work / f"cold-{i}"
            for target in ("report.json", "contract.json"):
                r = subprocess.run([sys.executable, str(HERE / "run.py"), target, "--out", str(out)],
                                   cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
                ok = _expect(r.returncode == 0, f"cold {i} {target} failed: {r.stderr or r.stdout}", errors) and ok
            if (out / "report.json").is_file():
                digests.append(sha256((out / "report.json").read_bytes()))
        ok = _expect(len(set(digests)) == 1, f"cold-start digests differ: {digests}", errors) and ok
    return ok, digest


def check_sources(errors: List[str]) -> bool:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, str(HERE / "run.py"), "sources", "--check"],
                       cwd=str(HERE), env=env, capture_output=True, text=True, check=False)
    return _expect(r.returncode == 0, f"SOURCES.sha256 not reproducible: {r.stderr or r.stdout}", errors)


def check_readme(errors: List[str]) -> bool:
    text = README.read_text(encoding="utf-8")
    ok = True
    for needle in ["DEFER", "incomplete", "not_qualified", "SDK-PBFDAF-AUMDF", "whole plan/swarm/TASKS.json"]:
        ok = _expect(needle in text, f"README missing {needle}", errors) and ok
    return ok


def check_licensing(errors: List[str]) -> bool:
    ok = True
    for path in list(HERE.glob("*.py")) + [README]:
        text = path.read_text(encoding="utf-8")
        ok = _expect(SPDX_LICENSE in text, f"missing license in {path.name}", errors) and ok
        ok = _expect(SPDX_COPYRIGHT in text, f"missing copyright in {path.name}", errors) and ok
    for name in ["report.json.license", "report.json.sha256.license", "contract.json.license", "SOURCES.sha256.license"]:
        path = HERE / name
        ok = _expect(path.is_file(), f"missing sidecar {name}", errors) and ok
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            ok = _expect(SPDX_LICENSE in text, f"sidecar missing license {name}", errors) and ok
    return ok


def check_scope(errors: List[str]) -> bool:
    env = dict(os.environ)
    r = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
                       capture_output=True, text=True, check=False)
    ok = _expect(r.returncode == 0, "git status failed", errors)
    allowed = reference.TASK_PREFIX
    for line in r.stdout.splitlines():
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        ok = _expect(path.startswith(allowed) or path == allowed.rstrip("/"), f"out-of-scope change: {path}", errors) and ok
    return ok


def check_diff(errors: List[str]) -> bool:
    r = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"], capture_output=True, text=True, check=False)
    return _expect(r.returncode == 0, f"git diff --check failed: {r.stdout}{r.stderr}", errors)


def main() -> int:
    errors: List[str] = []
    report, contract = check_strict_json(errors)
    check_report_contract(report, contract, errors)
    pins_ok = check_pins(errors)
    assets_ok = check_assets(errors)
    repro_ok, digest = check_reproduction(errors)
    sources_ok = check_sources(errors)
    readme_ok = check_readme(errors)
    licensing_ok = check_licensing(errors)
    scope_ok = check_scope(errors)
    diff_ok = check_diff(errors)
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print(f"OK pins={pins_ok} assets={assets_ok} repro={repro_ok} sources={sources_ok} readme={readme_ok} licensing={licensing_ok} scope={scope_ok} diff={diff_ok} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
