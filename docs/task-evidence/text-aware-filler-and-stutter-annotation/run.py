#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Generate deterministic task-local evidence artifacts."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

import reference  # noqa: E402


def regenerate(target: Path) -> tuple[bytes, bytes, str, str]:
    target.mkdir(parents=True, exist_ok=True)
    # copy package source files needed by reference
    for name in reference.PKG_FILES:
        src = ROOT / name
        if src.exists() and name not in {"report.json", "report.json.sha256", "contract.json", "SOURCES.sha256", "README.md"}:
            shutil.copy2(src, target / name)
    # also copy reference/run/verify/test/licenses as they are sources
    for name in ["reference.py", "run.py", "verify.py", "test_reference.py", "LICENSES.md"]:
        shutil.copy2(ROOT / name, target / name)
    # sidecars
    for name in ["contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"]:
        (target / name).write_text(reference.spdx_sidecar(), encoding="utf-8", newline="\n")

    # monkeypatch ROOT for generation? easier to run in subprocess
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["AUDIOBENCH_SOURCE_ROOT"] = str(reference.SOURCE_ROOT)
    env["AUDIO_SDK_WORKTREE_ROOT"] = str(reference.WORKTREE_ROOT)
    cmd = [sys.executable, "-B", str(target / "run.py"), "--emit", "--out-dir", str(target)]
    proc = subprocess.run(cmd, cwd=str(target), env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    report = (target / "report.json").read_bytes()
    contract = (target / "contract.json").read_bytes()
    sources = (target / "SOURCES.sha256").read_text(encoding="utf-8")
    readme = (target / "README.md").read_text(encoding="utf-8")
    return report, contract, sources, readme


def emit(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ["reference.py", "run.py", "verify.py", "test_reference.py", "LICENSES.md"]:
        src = ROOT / name
        dst = out_dir / name
        if src.exists() and src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
    for name in ["contract.json.license", "report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"]:
        (out_dir / name).write_text(reference.spdx_sidecar(), encoding="utf-8", newline="\n")
    report = reference.build_report()
    report_bytes = reference.canonical_json_bytes(report)
    (out_dir / "report.json").write_bytes(report_bytes)
    (out_dir / "report.json.license").write_text(reference.spdx_sidecar(), encoding="utf-8", newline="\n")
    (out_dir / "report.json.sha256").write_text(reference.sha256_bytes(report_bytes) + "  report.json\n", encoding="utf-8", newline="\n")
    (out_dir / "report.json.sha256.license").write_text(reference.spdx_sidecar(), encoding="utf-8", newline="\n")
    # README needs report present
    readme = reference.render_readme(report, root=out_dir)
    (out_dir / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    contract = reference.build_contract(report, root=out_dir)
    # write report and contract first for hashing
    (out_dir / "contract.json").write_bytes(reference.canonical_json_bytes(contract))
    (out_dir / "contract.json.license").write_text(reference.spdx_sidecar(), encoding="utf-8", newline="\n")
    sources = reference.render_sources_sha256(report, contract, root=out_dir)
    (out_dir / "SOURCES.sha256").write_text(sources, encoding="utf-8", newline="\n")
    (out_dir / "SOURCES.sha256.license").write_text(reference.spdx_sidecar(), encoding="utf-8", newline="\n")


def check_determinism() -> None:
    outputs = []
    for _ in range(3):
        with tempfile.TemporaryDirectory(prefix="ta-filler-stutter-") as td:
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["AUDIOBENCH_SOURCE_ROOT"] = str(reference.SOURCE_ROOT)
            env["AUDIO_SDK_WORKTREE_ROOT"] = str(reference.WORKTREE_ROOT)
            cmd = [sys.executable, "-B", str(ROOT / "run.py"), "--emit", "--out-dir", td]
            proc = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeError(proc.stdout + proc.stderr)
            t = Path(td)
            outputs.append((
                (t / "report.json").read_bytes(),
                (t / "contract.json").read_bytes(),
                (t / "SOURCES.sha256").read_bytes(),
                (t / "README.md").read_bytes(),
            ))
    if not (outputs[0] == outputs[1] == outputs[2]):
        raise RuntimeError("nondeterministic generation")


def write_all() -> None:
    check_determinism()
    emit(ROOT)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--readme", action="store_true")
    ap.add_argument("--out-dir")
    args = ap.parse_args()
    if args.emit:
        emit(Path(args.out_dir) if args.out_dir else ROOT)
        return 0
    if args.readme:
        report = reference.build_report()
        (ROOT / "README.md").write_text(reference.render_readme(report), encoding="utf-8", newline="\n")
        return 0
    if args.check:
        check_determinism()
        report = reference.build_report()
        contract = reference.build_contract(report)
        # compare to existing
        if reference.canonical_json_bytes(report) != (ROOT / "report.json").read_bytes():
            raise SystemExit("report.json mismatch")
        if reference.canonical_json_bytes(contract) != (ROOT / "contract.json").read_bytes():
            raise SystemExit("contract.json mismatch")
        if reference.render_sources_sha256(report, contract) != (ROOT / "SOURCES.sha256").read_text(encoding="utf-8"):
            raise SystemExit("SOURCES.sha256 mismatch")
        if reference.render_readme(report) != (ROOT / "README.md").read_text(encoding="utf-8"):
            raise SystemExit("README.md mismatch")
        print("ok")
        return 0
    write_all()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
