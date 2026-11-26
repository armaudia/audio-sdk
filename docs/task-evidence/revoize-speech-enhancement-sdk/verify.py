#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification for Revoize speech enhancement evidence.

This script never writes into the package. It recomputes artifacts, checks
canonical bytes/digests, verifies licensing and git scope, repeats regeneration
in three fresh processes, and rejects invalid/missing/non-finite/overclaiming
evidence.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import reference
import run

HERE = Path(__file__).resolve().parent
TASK_PREFIX = reference.TASK_PREFIX
PIN_LINE = re.compile(r"^([0-9a-f]{64})  ((?:local|source|worktree):[A-Za-z0-9_./-]+)$")
TEMP_ROOT = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")


class VerifyError(Exception):
    pass


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise VerifyError(message)


def _check_spdx_header(name: str) -> None:
    head = "\n".join((HERE / name).read_text(encoding="utf-8").splitlines()[:5])
    _check("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes" in head, "missing copyright in " + name)
    _check("SPDX-License-" + "Identifier: Apache-2.0" in head, "missing license in " + name)


def _check_licenses() -> None:
    for name in ("README.md", "reference.py", "run.py", "test_reference.py", "verify.py"):
        _check_spdx_header(name)
    for name, sidecar in sorted(run.LICENSE_SIDECARS.items()):
        path = HERE / sidecar
        _check(path.is_file(), "missing SPDX sidecar: " + sidecar)
        _check(path.read_text(encoding="utf-8") == reference.LICENSE_TEXT, "invalid SPDX sidecar: " + sidecar)
    reuse = reference.SDK_ROOT / "REUSE.toml"
    _check(reuse.is_file(), "REUSE.toml missing")
    _check("docs/**" in reuse.read_text(encoding="utf-8"), "REUSE.toml does not cover docs/**")


def _check_unexpected_files() -> None:
    expected = set(run.LOCAL_FILES)
    actual = {p.name for p in HERE.iterdir() if p.is_file()}
    _check(not sorted(actual - expected), "unexpected task-local files: " + ",".join(sorted(actual - expected)))
    _check(not sorted(expected - actual), "missing task-local files: " + ",".join(sorted(expected - actual)))


def _check_git_scope() -> None:
    process = subprocess.run(
        ["git", "-C", str(reference.SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all", "-z"],
        capture_output=True, text=True, check=False,
    )
    _check(process.returncode == 0, "git status failed")
    for entry in process.stdout.split("\0"):
        if not entry:
            continue
        path = entry[3:]
        _check(path.startswith(TASK_PREFIX), "out-of-scope git change: " + path)


def _check_pins() -> None:
    reference.verify_document_pins()
    _check(reference.BOARD_PATH not in reference.SOURCE_PINS, "mutable board pinned as source")
    _check(reference.BOARD_PATH not in reference.BOUNDARY_PINS, "mutable board pinned as boundary")


def _check_sources_manifest() -> None:
    raw = (HERE / "SOURCES.sha256").read_bytes()
    _check(raw == run.sources_bytes(), "SOURCES.sha256 is not byte-identical")
    parsed: List[Tuple[str, str]] = []
    for line in raw.decode("ascii").splitlines():
        match = PIN_LINE.fullmatch(line)
        _check(match is not None, "malformed SOURCES line: " + line)
        digest, label = match.groups()
        _, path = label.split(":", 1)
        _check(".." not in Path(path).parts, "traversing pin: " + label)
        parsed.append((label, digest))
    labels = [label for label, _ in parsed]
    _check(labels == sorted(labels), "SOURCES.sha256 is not sorted")
    _check(len(labels) == len(set(labels)), "SOURCES.sha256 has duplicates")
    _check("local:" + run.SOURCES not in labels, "SOURCES.sha256 pins itself")
    _check("source:" + reference.BOARD_PATH not in labels and "worktree:" + reference.BOARD_PATH not in labels, "mutable board in SOURCES.sha256")
    expected = {"local:" + n for n in run.LOCAL_FILES if n not in run.SOURCES_EXCLUDED}
    expected |= {"source:" + r for r in reference.SOURCE_PINS}
    expected |= {"worktree:" + r for r in reference.BOUNDARY_PINS}
    _check(set(labels) == expected, "SOURCES.sha256 coverage mismatch")
    for label, digest in parsed:
        kind, path = label.split(":", 1)
        base = HERE if kind == "local" else reference.SOURCE_ROOT if kind == "source" else reference.SDK_ROOT
        actual = reference.sha256_file(base / path)
        _check(actual == digest, "SOURCES digest mismatch: " + label)


def _check_contract() -> None:
    raw = (HERE / "contract.json").read_bytes()
    _check(raw == run.build_contract(), "contract.json is not byte-identical")
    contract = reference.strict_loads(raw.decode("utf-8"))
    _check(contract["SPDX-License-Identifier"] == "Apache-2.0", "contract licence")
    _check(contract["task_id"] == reference.TASK, "contract task")
    _check(contract["component"] == reference.COMPONENT, "contract component")
    _check(contract["base_commit"] == reference.BASE_COMMIT, "contract base")
    _check(contract["branch"] == reference.BRANCH, "contract branch")
    _check(contract["profile"] == reference.PROFILE, "contract profile")
    _check(contract["mode"] == reference.MODE, "contract mode")
    _check(contract["status"] == reference.STATUS, "contract status")
    _check(contract["decision"] == "DEFER", "contract decision")
    _check(contract["qualification_status"] == "not_qualified", "contract qualification")
    _check(contract["proposal_only"] is True, "contract proposal-only")
    q = contract["qualification"]
    _check(q["candidate_qualified"] is False, "contract claims qualification")
    _check(q["no_missing_result_qualifies_candidate"] is True, "contract missing-result rule")
    _check(q["synthetic_control_is_not_candidate_evidence"] is True, "contract synthetic rule")
    impl = contract["revoize_implementation_contract"]
    _check(impl["variant"] == reference.REQUIRED_VARIANT, "contract variant")
    _check(impl["qualification"] == "not_qualified", "contract impl qualification")
    _check(len(contract["release_gates"]) == 8, "contract gate count")
    _check(contract["mutable_provenance"]["gate"] is False, "contract mutable gate")
    _check(reference.BOARD_PATH not in contract["source_pins"], "contract pins board")
    _check(reference.BOARD_PATH not in contract["boundary_pins"], "contract pins board boundary")


def _check_report() -> Dict[str, Any]:
    raw = (HERE / "report.json").read_bytes()
    expected = run.report_bytes()
    _check(raw == expected, "report.json is not byte-identical")
    digest = run.sha256(raw)
    sidecar = (HERE / "report.json.sha256").read_bytes()
    _check(sidecar == run.sidecar_bytes(digest), "report sidecar mismatch")
    report = reference.strict_loads(raw.decode("utf-8"))
    _check(report["schema_id"] == reference.SCHEMA_ID, "report schema")
    _check(report["decision"] == "DEFER", "report decision")
    _check(report["status"] == reference.STATUS, "report status")
    _check(report["qualification_status"] == "not_qualified", "report qualification")
    _check(report["evidence_status"] == "incomplete", "report evidence status")
    _check(report["proposal_only"] is True, "report proposal-only")
    q = report["qualification"]
    _check(q["candidate_qualified"] is False, "report candidate qualified")
    _check(q["status"] == "not_qualified", "report nested qualification")
    _check(q["qualification_status"] == "not_qualified", "report nested qualification_status")
    _check(q["no_missing_result_qualifies_candidate"] is True, "report missing-result rule")
    _check(q["synthetic_control_is_not_candidate_evidence"] is True, "report synthetic rule")
    _check(len(report["gates"]) == 8, "report gate count")
    _check(all(g["blocked"] is True and g["status"] == "blocked" for g in report["gates"]), "report gates not blocked")
    _check(len(report["exact_blockers"]) == 8, "report blocker count")
    control = report["synthetic_control"]
    _check(control["qualifies_candidate"] is False, "synthetic control qualifies")
    _check(control["not_revoize"] is True, "synthetic control revoize flag")
    _check(control["not_real_audio_corpus"] is True, "synthetic control corpus flag")
    cm = report["candidate_metrics"]
    _check(cm["derived_from_synthetic_control"] is False, "candidate metrics derived")
    for k, v in cm.items():
        if k == "derived_from_synthetic_control":
            continue
        _check(isinstance(v, dict) and v.get("measured") is False and v.get("value") is None, "candidate metric not null: " + k)
    adverse = report["controls"]["adverse"]
    _check(len(adverse) >= 20, "too few adverse cases")
    _check(all(a["result"] == "rejected" for a in adverse), "adverse case accepted")
    _check(report["controls"]["all_adverse_rejected"] is True, "adverse flag")
    tri = report["task_row_identity"]
    _check(tri["whole_file_hashed"] is False, "task row whole file hashed")
    _check(reference.BOARD_PATH not in report["source_pins"], "report pins board")
    _check(reference.BOARD_PATH not in report["boundary_pins"], "report pins board boundary")
    for k, v in report["scope"].items():
        if k in ("feature_domain_synthetic_control", "proposal_only", "task_local_only"):
            _check(v is True, "scope flag should be true: " + k)
        else:
            _check(v is False, "scope flag should be false: " + k)
    for k, v in report["boundary"].items():
        _check(v is False, "boundary flag should be false: " + k)
    return report


def _cold_start_regen() -> List[str]:
    tmp_base = TEMP_ROOT if TEMP_ROOT.exists() else Path(tempfile.gettempdir())
    digests: List[str] = []
    for i in range(3):
        with tempfile.TemporaryDirectory(prefix="revoize-se-verify-", dir=str(tmp_base)) as td:
            tmp = Path(td)
            for name in run.LOCAL_FILES:
                shutil.copy2(HERE / name, tmp / name)
            env = os.environ.copy(); env["PYTHONDONTWRITEBYTECODE"] = "1"
            proc = subprocess.run([sys.executable, str(tmp / "run.py"), "all"], cwd=str(tmp), capture_output=True, text=True, env=env, check=False)
            _check(proc.returncode == 0, f"cold start run.py failed[{i}]: {proc.stderr}\n{proc.stdout}")
            digest = proc.stdout.strip().splitlines()[-1].strip()
            _check(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, f"bad digest[{i}]: {digest}")
            for name in (run.REPORT, run.SIDECAR, run.CONTRACT, run.SOURCES):
                _check((tmp / name).is_file(), f"missing artifact[{i}]: {name}")
            report = (tmp / run.REPORT).read_bytes()
            sidecar = (tmp / run.SIDECAR).read_bytes()
            _check(sidecar == run.sidecar_bytes(reference.sha256_bytes(report)), f"sidecar mismatch[{i}]")
            digests.append(reference.sha256_bytes(report))
    _check(len(set(digests)) == 1, "cold-start digests differ: " + ",".join(digests))
    return digests


def _check_manifest_rejection_contract() -> None:
    base = reference._base_manifest()
    normalized = reference.validate_manifest(base)
    _check(isinstance(normalized, dict), "manifest validation failed")
    bad = dict(base); bad.pop("runtime_package_sha256")
    try:
        reference.validate_manifest(bad)
        raise VerifyError("manifest missing field accepted")
    except reference.Reject:
        pass
    bad = dict(base); bad["variant"] = "wrong"
    try:
        reference.validate_manifest(bad)
        raise VerifyError("wrong variant accepted")
    except reference.Reject:
        pass
    bad = dict(base); bad["source_revision_or_release"] = "latest"
    try:
        reference.validate_manifest(bad)
        raise VerifyError("bad pin accepted")
    except reference.Reject:
        pass


def main() -> int:
    try:
        _check_unexpected_files()
        _check_licenses()
        _check_pins()
        _check_contract()
        report = _check_report()
        _check_sources_manifest()
        _check_git_scope()
        _check_manifest_rejection_contract()
        digests = _cold_start_regen()
        _check(report["decision"] == "DEFER", "final decision not DEFER")
        _check(report["qualification_status"] == "not_qualified", "final qualification not not_qualified")
        print(
            "PASS "
            f"decision={report['decision']} "
            f"status={report['status']} "
            f"qualification={report['qualification_status']} "
            f"gates={len(report['gates'])} "
            f"adverse={report['controls']['adverse_case_count']} "
            f"cold_start_sha256={digests[0]}"
        )
        return 0
    except VerifyError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL unexpected: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
