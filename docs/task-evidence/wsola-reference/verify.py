# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only fail-closed verifier for SDK-WSOLA-REFERENCE evidence package."""

from __future__ import annotations

import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = reference.WORKTREE
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "SPDX-" "License-Identifier: Apache-2.0"
SIDECAR_TEXT = SPDX_COPYRIGHT + "\n" + SPDX_LICENSE + "\n"
SIDECARS = (
    "contract.json.license", "report.json.license",
    "report.json.sha256.license", "SOURCES.sha256.license",
)
PIN_LINE = re.compile(r"^([0-9a-f]{64})  (\S+)$")


def _expect(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def check_interpreter(errors: list[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append(f"interpreter_mismatch:pinned={reference.REQUIRED_INTERPRETER}:observed={observed}")


def check_files(errors: list[str]) -> None:
    observed = {p.name for p in HERE.iterdir() if p.is_file() and not p.name.startswith(".")}
    extra = sorted(observed - reference.EXPECTED_DIR_FILES)
    missing = sorted(reference.EXPECTED_DIR_FILES - observed)
    if extra:
        errors.append("unexpected_files:" + ",".join(extra))
    if missing:
        errors.append("missing_files:" + ",".join(missing))


def check_pins(errors: list[str]) -> int:
    checked = 0
    for pins, root, label in (
        (reference.SOURCE_PINS, reference.AUDIO_ROOT, "source"),
        (reference.BOUNDARY_PINS, SDK_ROOT, "boundary"),
    ):
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                errors.append(f"{label}_pin_missing:{relative}")
                continue
            actual = reference.sha256_file(path)
            if actual != expected:
                errors.append(f"{label}_pin_mismatch:{relative}")
            else:
                checked += 1
    return checked


def check_readme(errors: list[str]) -> dict[str, int]:
    if not README.is_file():
        errors.append("readme_missing")
        return {}
    try:
        return reference.verify_readme_digests(README.read_text(encoding="utf-8"))
    except Exception as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return {}


def check_sources_manifest(errors: list[str]) -> None:
    if not PINS.is_file():
        errors.append("sources_manifest_missing")
        return
    if PINS.read_bytes() != run.reference.sources_bytes():
        errors.append("sources_manifest_drift")
    rows: dict[str, str] = {}
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        match = PIN_LINE.match(line)
        if not match:
            errors.append("malformed_sources_line:" + line[:80])
            continue
        digest, name = match.groups()
        if name in rows:
            errors.append("duplicate_sources_row:" + name)
            continue
        rows[name] = digest
    for name, digest in sorted(rows.items()):
        if name.startswith("source:"):
            path = reference.AUDIO_ROOT / name[len("source:"):]
        elif name.startswith("sdk:"):
            path = SDK_ROOT / name[len("sdk:"):]
        else:
            path = SDK_ROOT / name
        if not path.is_file():
            errors.append("sources_path_missing:" + name)
        elif reference.sha256_file(path) != digest:
            errors.append("sources_digest_mismatch:" + name)
    if reference.BOARD_TASK_ROW in rows:
        errors.append("mutable_board_file_must_not_be_pinned")


def check_contract(errors: list[str]) -> dict:
    if not CONTRACT.is_file():
        errors.append("contract_missing")
        return {}
    try:
        document = reference.read_strict_json(CONTRACT)
    except Exception as error:
        errors.append("contract_invalid:" + str(error))
        return {}
    expected = reference.build_contract()
    _expect(document == expected, "contract_does_not_match_builder", errors)
    _expect(CONTRACT.read_bytes() == reference.canonical_bytes(expected), "contract_not_canonical", errors)
    _expect(document.get("decision") == reference.DECISION, "contract_decision_mismatch", errors)
    _expect(document.get("qualification_status") == reference.QUALIFICATION_STATUS, "contract_qualification_mismatch", errors)
    _expect(document.get("task_row_identity", {}).get("whole_file_hashed") is False, "contract_whole_file_hashed", errors)
    _expect(len(document.get("gates", [])) == 8, "contract_gate_count_mismatch", errors)
    _expect(all(g.get("status") == "blocked" for g in document.get("gates", [])), "contract_gate_not_blocked", errors)
    return document


def check_report(errors: list[str]) -> dict:
    if not REPORT.is_file():
        errors.append("report_missing")
        return {}
    try:
        document = reference.read_strict_json(REPORT)
    except Exception as error:
        errors.append("report_invalid:" + str(error))
        return {}
    expected = reference.build_report()
    payload, digest = reference.canonical_report(expected)
    _expect(document == expected, "report_does_not_match_builder", errors)
    _expect(REPORT.read_bytes() == payload.encode("ascii"), "report_not_canonical", errors)
    if not SIDECAR.is_file():
        errors.append("report_sidecar_missing")
    elif SIDECAR.read_text(encoding="ascii") != digest + "  report.json\n":
        errors.append("report_sidecar_mismatch")
    for key, value in {
        "task": reference.TASK, "task_id": reference.TASK, "component": reference.COMPONENT_ID,
        "base_commit": reference.BASE_COMMIT, "branch": reference.BRANCH, "profile": reference.PROFILE,
        "decision": reference.DECISION, "status": reference.STATUS, "evidence_status": reference.EVIDENCE_STATUS,
        "qualification_status": reference.QUALIFICATION_STATUS,
    }.items():
        _expect(document.get(key) == value, f"report_field_mismatch:{key}", errors)
    q = document.get("qualification", {})
    _expect(q.get("not_qualified") is True, "report_not_qualified_missing", errors)
    _expect(q.get("candidate_qualified") is False, "report_candidate_qualified_not_false", errors)
    _expect(q.get("all_release_gates_blocked") is True, "report_all_gates_not_blocked", errors)
    gates = document.get("gates", [])
    _expect([g.get("id") for g in gates] == [f"RG-0{i}" for i in range(1, 9)], "gate_ids_mismatch", errors)
    for g in gates:
        _expect(g.get("status") == "blocked", f"gate_not_blocked:{g.get('id')}", errors)
        _expect(g.get("qualifies") is False, f"gate_qualifies:{g.get('id')}", errors)
    blockers = document.get("exact_blockers", [])
    _expect(len(blockers) == 4, "blocker_count_mismatch", errors)
    for b in blockers:
        _expect(b.get("status") == "open", f"blocker_not_open:{b.get('id')}", errors)
        _expect(b.get("qualifies") is False, f"blocker_qualifies:{b.get('id')}", errors)
    ident = document.get("task_row_identity", {})
    _expect(ident.get("whole_file_hashed") is False, "report_whole_file_hashed", errors)
    _expect(ident.get("stable_sha256") == reference.board_row_digest(), "report_stable_sha_mismatch", errors)
    boundary = document.get("boundary", {})
    for k in ("provider_registration", "default_selected", "public_api_abi_change", "installed_v0_behavior_change", "shared_build_or_ci_change", "network_used"):
        _expect(boundary.get(k) is False, f"boundary_{k}_not_false", errors)
    scope = document.get("scope", {})
    for k in ("real_audio", "listening", "device_timing", "benchmark_claim", "release_claim", "provider_registration", "public_api_abi_change"):
        _expect(scope.get(k) is False, f"scope_{k}_not_false", errors)
    rp = document.get("rate_profile", {})
    _expect(rp.get("profile_satisfied") is False, "rate_profile_satisfied", errors)
    _expect(rp.get("real_results") == 0, "rate_profile_real_results", errors)
    _expect(len(rp.get("rows", [])) == 8, "rate_profile_row_count", errors)
    return document


def check_licensing(errors: list[str]) -> None:
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("missing_license_sidecar:" + name)
        elif path.read_text(encoding="utf-8") != SIDECAR_TEXT:
            errors.append("license_sidecar_text_mismatch:" + name)
    for name in ("README.md", "LICENSES.md"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_LICENSE not in text:
            errors.append("missing_spdx_header:" + name)
    for name in ("reference.py", "run.py", "verify.py", "test_reference.py"):
        head = "\n".join((HERE / name).read_text(encoding="utf-8").splitlines()[:5])
        if SPDX_COPYRIGHT not in head or SPDX_LICENSE not in head:
            errors.append("missing_inline_spdx_header:" + name)


def _run_git(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(SDK_ROOT), *arguments],
                          capture_output=True, text=True, check=False)


def check_scope(errors: list[str]) -> bool:
    if not (SDK_ROOT / ".git").exists():
        return True
    ok = True
    status = _run_git("status", "--porcelain=v1", "--untracked-files=all")
    if status.returncode != 0:
        errors.append("git_status_failed:" + status.stderr.strip())
        return False
    for line in status.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
            ok = False
    for args in (("diff", "--check"), ("diff", "--cached", "--check")):
        diff = _run_git(*args)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_diff_check_failed:" + " ".join(args))
            ok = False
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
        ok = False
    else:
        try:
            paths = reference.scope_changed_paths(SDK_ROOT, base)
        except Exception as error:
            errors.append(str(error))
            ok = False
            paths = []
        for path in reference.scope_violations(paths):
            errors.append("base_out_of_scope_change:" + path)
            ok = False
    return ok


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    if not REPORT.is_file() or not CONTRACT.is_file() or not SIDECAR.is_file():
        errors.append("cannot_cold_start_without_committed_artifacts")
        return []
    tmp_root = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
    root = str(tmp_root) if tmp_root.is_dir() else None
    with tempfile.TemporaryDirectory(prefix="wsola-ref-verify-", dir=root) as td:
        target = Path(td)
        shutil.copy2(HERE / "reference.py", target / "reference.py")
        shutil.copy2(HERE / "run.py", target / "run.py")
        env = dict(os.environ)
        env["AUDIOML_ROOT"] = str(reference.AUDIO_ROOT)
        env["SOURCE_ROOT"] = str(reference.AUDIO_ROOT)
        env["SDK_ROOT"] = str(SDK_ROOT)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONHASHSEED"] = "0"
        digests: list[str] = []
        for _ in range(3):
            r = subprocess.run([sys.executable, str(target / "run.py"), "report.json"],
                               cwd=str(target), env=env, capture_output=True, text=True)
            if r.returncode != 0:
                errors.append("cold_start_run_failed:" + (r.stderr.strip() or r.stdout.strip()))
                return digests
            digests.append(hashlib.sha256((target / "report.json").read_bytes()).hexdigest())
        if len(set(digests)) != 1:
            errors.append("cold_start_not_byte_identical")
        if (target / "report.json").read_bytes() != REPORT.read_bytes():
            errors.append("cold_start_report_differs")
        if (target / "contract.json").read_bytes() != CONTRACT.read_bytes():
            errors.append("cold_start_contract_differs")
        if (target / "report.json.sha256").read_text(encoding="ascii") != SIDECAR.read_text(encoding="ascii"):
            errors.append("cold_start_sidecar_differs")
    return digests


def main() -> int:
    errors: list[str] = []
    check_interpreter(errors)
    check_files(errors)
    pins = check_pins(errors)
    readme = check_readme(errors)
    check_sources_manifest(errors)
    contract = check_contract(errors)
    report = check_report(errors)
    check_licensing(errors)
    scope_ok = check_scope(errors)
    repeats = check_cold_start_regeneration(errors)
    if errors:
        for e in errors:
            print("FAIL: " + e, file=sys.stderr)
        print(f"FAIL verification ({len(errors)} errors)", file=sys.stderr)
        return 1
    print(
        "PASS verify.py "
        f"version={platform.python_version()} "
        f"contract_sha256={reference.object_digest(contract)} "
        f"report_sha256={hashlib.sha256(REPORT.read_bytes()).hexdigest()} "
        f"gates={len(report.get('gates', []))} blockers={len(report.get('exact_blockers', []))} "
        f"pins={pins} readme_rows={','.join(f'{k}={v}' for k,v in sorted(readme.items()))} "
        f"scope_ok={scope_ok} cold_starts={len(repeats)}/3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
