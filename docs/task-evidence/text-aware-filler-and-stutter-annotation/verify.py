#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Verify deterministic text-aware filler/stutter annotation evidence package."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))

import reference  # noqa: E402


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> int:
    report = reference.verify_all()
    # 3 cold regenerations in temp dirs
    digests = []
    for _ in range(3):
        with tempfile.TemporaryDirectory(prefix="tafs-verify-") as td:
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["AUDIOBENCH_SOURCE_ROOT"] = str(reference.SOURCE_ROOT)
            env["AUDIO_SDK_WORKTREE_ROOT"] = str(reference.WORKTREE_ROOT)
            cmd = [sys.executable, "-B", str(ROOT / "run.py"), "--emit", "--out-dir", td]
            proc = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True)
            if proc.returncode != 0:
                fail(proc.stdout + proc.stderr)
            t = Path(td)
            digests.append((
                reference.sha256_file(t / "report.json"),
                reference.sha256_file(t / "contract.json"),
                reference.sha256_file(t / "SOURCES.sha256"),
                reference.sha256_file(t / "README.md"),
            ))
    if not (digests[0] == digests[1] == digests[2]):
        fail("cold regeneration mismatch")
    if digests[0][0] != reference.sha256_file(ROOT / "report.json"):
        fail("report digest mismatch vs checked-in")

    scope = reference.scope_check()
    if not scope["base_available"]:
        fail("scope_base_unavailable")
    if scope["dirty_paths_out_of_scope"]:
        fail(f"dirty_out_of_scope:{scope['dirty_paths_out_of_scope']}")
    if scope["committed_paths_out_of_scope"]:
        fail(f"committed_out_of_scope:{scope['committed_paths_out_of_scope']}")

    if report["decision"] != "DEFER":
        fail("decision")
    if report["qualification_status"] != "not_qualified":
        fail("qualification")
    if report["blocked_gate_count"] != 8:
        fail("gate count")
    if not report["absence_all_absent"]:
        fail("absence probes")
    if not report["controls"]["adverse_all_rejected"]:
        fail("adverse")
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
