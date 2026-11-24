# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Cold-start byte-identity crosscheck for the synthetic evidence report."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Dict, List

import reference

ROOT = Path(__file__).resolve().parent
TEMP_ROOT = Path("/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")


def expected_bytes() -> Dict[str, bytes]:
    return {
        reference.REPORT: (ROOT / reference.REPORT).read_bytes(),
        reference.SIDECAR: (ROOT / reference.SIDECAR).read_bytes(),
    }


def run(repeats: int = 3) -> Dict[str, object]:
    """Regenerate the report in isolated cold-start processes and compare bytes."""
    expected = expected_bytes()
    problems: List[str] = []
    temp_root = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    work = Path(tempfile.mkdtemp(prefix="bench-subprocess-crosscheck-", dir=temp_root))
    try:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        for index in range(repeats):
            output = work / ("repeat-%d" % index)
            command = [sys.executable, str(ROOT / "run.py"), "--report", "--out", str(output)]
            completed = subprocess.run(command, cwd=str(ROOT), env=environment,
                                       capture_output=True, text=True, check=False)
            if completed.returncode != 0:
                problems.append("repeat %d failed: %s" % (index, completed.stderr.strip()))
                continue
            for name, data in expected.items():
                actual = (output / name).read_bytes()
                if actual != data:
                    problems.append("repeat %d differs: %s" % (index, name))
                    problems.append("  expected=" + reference.sha256_bytes(data))
                    problems.append("  actual=" + reference.sha256_bytes(actual))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return {
        "status": "ok" if not problems else "failed",
        "repeats": repeats,
        "report_sha256": reference.sha256_bytes(expected[reference.REPORT]),
        "problems": problems,
    }


if __name__ == "__main__":
    result = run()
    print("crosscheck_status=" + str(result["status"]))
    for problem in result["problems"]:
        print(problem, file=sys.stderr)
    raise SystemExit(0 if result["status"] == "ok" else 1)
