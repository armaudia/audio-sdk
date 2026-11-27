# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for SDK-WAVEFIT blocker evidence."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402

SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "contract.json.license",
    "README.md.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)


def _fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def check_json(errors: list[str]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for name in ("report.json", "contract.json", "report.json.sha256", "SOURCES.sha256"):
        p = HERE / name
        if not p.is_file():
            _fail("missing:" + name, errors)
    for name in ("report.json", "contract.json"):
        p = HERE / name
        try:
            obj = reference.read_strict_json(p)
        except Exception as e:
            _fail(f"invalid_json:{name}:{e}", errors)
            continue
        data[name] = obj
    return data


def check_contract_report(contract: dict, report: dict, errors: list[str]) -> None:
    expected_contract = reference.build_contract()
    expected_report = reference.build_report()
    if contract != expected_contract:
        _fail("contract_not_canonical_or_stale", errors)
    if report != expected_report:
        _fail("report_not_canonical_or_stale", errors)
    try:
        reference.validate_contract(contract)
    except Exception as e:
        _fail("contract_validate:" + str(e), errors)
    if (HERE / "contract.json").read_bytes() != reference.canonical_bytes(expected_contract):
        _fail("contract_bytes_not_canonical", errors)
    rep_text, _ = reference.canonical_report(expected_report)
    if (HERE / "report.json").read_bytes() != rep_text.encode("utf-8"):
        _fail("report_bytes_not_canonical", errors)


def check_digests(report: dict, errors: list[str]) -> None:
    text, expected = reference.canonical_report(report)
    side = (HERE / "report.json.sha256").read_text(encoding="utf-8")
    if side != expected + "  report.json\n":
        _fail("report_sha256_mismatch", errors)
    if (HERE / "report.json").read_text(encoding="utf-8") != text:
        _fail("report_canonical_mismatch", errors)
    sources = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
    if sources != reference.sources_bytes().decode("utf-8"):
        _fail("sources_manifest_mismatch", errors)
    for line in sources.splitlines():
        if not line or line.startswith("#"):
            continue
        digest, name = line.split("  ", 1)
        if name.startswith("source:"):
            path = reference.AUDIO_ROOT / name[len("source:"):]
        elif name.startswith("sdk:"):
            path = SDK_ROOT / name[len("sdk:"):]
        elif name.startswith(reference.TASK_PREFIX):
            path = SDK_ROOT / name
        else:
            _fail("sources_unknown_prefix:" + name, errors)
            continue
        if not path.is_file():
            _fail("sources_missing:" + name, errors)
            continue
        actual = reference.sha256_file(path)
        if actual != digest:
            _fail("sources_digest_mismatch:" + name, errors)


def check_pins(errors: list[str]) -> None:
    try:
        reference.pin_rows(reference.SOURCE_PINS, reference.AUDIO_ROOT)
        reference.pin_rows(reference.BOUNDARY_PINS, SDK_ROOT)
    except Exception as e:
        _fail("pin_check:" + str(e), errors)


def check_policy(contract: dict, report: dict, errors: list[str]) -> None:
    if contract.get("decision") != "DEFER" or report.get("decision") != "DEFER":
        _fail("decision_not_defer", errors)
    if contract.get("status") != "incomplete" or report.get("status") != "incomplete":
        _fail("status_not_incomplete", errors)
    if contract.get("qualification_status") != "not_qualified" or report.get("qualification_status") != "not_qualified":
        _fail("qualification_not_not_qualified", errors)
    for gate in report.get("gates", []):
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            _fail("gate_not_blocked:" + str(gate.get("id")), errors)
    if len(report.get("gates", [])) != 8:
        _fail("gate_count", errors)
    for blk in report.get("exact_blockers", []):
        if blk.get("status") != "open" or blk.get("qualifies") is not False:
            _fail("blocker_not_open:" + str(blk.get("id")), errors)
    if report.get("source_presence", {}).get("model_executed") is not False:
        _fail("model_executed_claimed", errors)
    if report.get("source_presence", {}).get("weights_used") is not False:
        _fail("weights_claimed", errors)
    summary = report.get("absence_evidence", {}).get("summary", {})
    if summary.get("all_probes_absent") is not True:
        _fail("absence_not_all_absent", errors)
    if report.get("linked_row_identity", {}).get("board_file_pinned") is not False:
        _fail("mutable_board_pinned", errors)
    if report.get("proposal_only") is not True:
        _fail("proposal_only_false", errors)
    # enhancement profile blocked
    for row in report.get("enhancement_profile", {}).get("rows", []):
        if row.get("status") != "blocked":
            _fail("profile_row_not_blocked:" + str(row.get("id")), errors)


def check_readme(errors: list[str]) -> None:
    p = HERE / "README.md"
    if not p.is_file():
        _fail("missing:README.md", errors)
        return
    text = p.read_text(encoding="utf-8")
    for phrase in ("proposal_only_incomplete", "decision `DEFER`", "qualification `not_qualified`", "eight release gates blocked"):
        if phrase not in text:
            _fail("readme_missing_phrase:" + phrase, errors)


def check_files(errors: list[str]) -> None:
    for name in LICENSE_SIDECARS:
        p = HERE / name
        if not p.is_file():
            _fail("missing_sidecar:" + name, errors)
            continue
        text = p.read_text(encoding="utf-8")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            _fail("sidecar_spdx_missing:" + name, errors)
    allowed = {"LICENSES.md","README.md","README.md.license","SOURCES.sha256","SOURCES.sha256.license","contract.json","contract.json.license","reference.py","report.json","report.json.license","report.json.sha256","report.json.sha256.license","run.py","test_reference.py","verify.py"}
    for p in sorted(HERE.iterdir()):
        if p.is_dir():
            if p.name == "__pycache__":
                _fail("bytecode_cache_present", errors)
            else:
                _fail("unexpected_subdir:" + p.name, errors)
            continue
        if p.suffix.lower() in {".wav", ".mp3", ".flac", ".onnx", ".pt", ".pth", ".ckpt", ".bin", ".safetensors"}:
            _fail("forbidden_artifact:" + p.name, errors)
        if p.name not in allowed:
            _fail("unexpected_file:" + p.name, errors)
    if any(HERE.rglob("*.pyc")):
        _fail("pyc_present", errors)


def check_scope(errors: list[str]) -> list[str]:
    r = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"], capture_output=True, text=True)
    if r.returncode != 0:
        _fail("git_status_failed:" + r.stderr.strip(), errors)
        return []
    changed = []
    for line in r.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            changed.append(path)
            if not path.startswith(reference.TASK_PREFIX):
                _fail("out_of_scope_change:" + path, errors)
    return changed


def check_git_diff(errors: list[str]) -> None:
    for args in (["diff", "--check"], ["diff", "--cached", "--check"]):
        r = subprocess.run(["git", "-C", str(SDK_ROOT), *args], capture_output=True, text=True)
        if r.returncode != 0:
            _fail("git_" + "_".join(args).replace("-", "") + "_failed:" + (r.stdout + r.stderr).strip()[:200], errors)


def check_tests(errors: list[str]) -> int:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    r = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_reference.py"], cwd=HERE, capture_output=True, text=True, env=env, timeout=300)
    if r.returncode != 0:
        _fail("test_suite_failed:" + (r.stderr.strip() or r.stdout.strip())[-400:], errors)
    # rough count
    count = sum(1 for line in (r.stderr + r.stdout).splitlines() if line.strip().startswith("test_") and "(test_reference." in line)
    return count


def check_cold_regen(errors: list[str]) -> None:
    committed = {
        name: (HERE / name).read_bytes()
        for name in ("contract.json", "report.json", "report.json.sha256", "SOURCES.sha256")
        if (HERE / name).is_file()
    }
    if len(committed) != 4:
        _fail("committed_artifacts_missing", errors)
        return
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="sdk-wavefit-cold-") as td:
        root = Path(td)
        for i in range(3):
            scratch_sdk = root / f"cold-{i}" / "sdk"
            task_dir = scratch_sdk / reference.TASK_PREFIX
            task_dir.mkdir(parents=True)
            for p in sorted(HERE.iterdir()):
                if p.is_file():
                    shutil.copy2(p, task_dir / p.name)
            # provide pinned boundary/source files via symlinks to real worktree/audio root
            for rel in reference.BOUNDARY_PINS:
                dst = scratch_sdk / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                src = SDK_ROOT / rel
                if src.exists() and not dst.exists():
                    dst.symlink_to(src)
            # source pins: symlink audio root structure
            audio_link = root / f"cold-{i}" / "audio"
            audio_link.mkdir(parents=True)
            for rel in reference.SOURCE_PINS:
                src = reference.AUDIO_ROOT / rel
                dst = audio_link / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.exists() and not dst.exists():
                    dst.symlink_to(src)
            # make AUDIO_ROOT discovery work by placing plan files
            # easier: set AUDIOML_ROOT env pointing to audio_link? reference._find_audio_root looks for plan/swarm/TASKS.json
            # but TASKS.json may not be in our pinned set; create minimal stub? No, avoid fabrication. Instead set env AUDIOML_ROOT to real AUDIO_ROOT.
            run_env = dict(env)
            run_env["AUDIOML_ROOT"] = str(reference.AUDIO_ROOT)
            r = subprocess.run([sys.executable, "run.py", "all"], cwd=task_dir, capture_output=True, text=True, env=run_env, timeout=120)
            if r.returncode != 0:
                _fail(f"cold_regen_{i}_failed:" + (r.stderr or r.stdout)[-300:], errors)
                return
            for name, payload in committed.items():
                got = (task_dir / name).read_bytes()
                if got != payload:
                    _fail(f"cold_regen_{i}_mismatch:{name}", errors)
                    return


def main() -> int:
    errors: list[str] = []
    data = check_json(errors)
    report = data.get("report.json", {})
    contract = data.get("contract.json", {})
    if report and contract:
        check_contract_report(contract, report, errors)
        check_digests(report, errors)
        check_policy(contract, report, errors)
    check_pins(errors)
    check_readme(errors)
    check_files(errors)
    changed = check_scope(errors)
    check_git_diff(errors)
    test_count = check_tests(errors)
    check_cold_regen(errors)
    if errors:
        for e in errors:
            print("FAIL: " + e)
        print(f"FAIL verify.py errors={len(errors)}")
        return 1
    _, digest = reference.canonical_report(report) if report else ("", "unknown")
    print(f"PASS verify.py decision=DEFER status=incomplete qualification=not_qualified gates=8 tests={test_count} changed_files={len(changed)} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
