# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only task-local verification."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
REPORT_SHA = HERE / "report.json.sha256"
TASK_PREFIX = "docs/task-evidence/distil-wav2vec2-adult-child-ridge/"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins(errors: list[str]) -> int:
    lines = [l for l in PINS.read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append(f"malformed pin: {line!r}")
            continue
        digest, raw = parts
        if raw.startswith("source:"):
            path = SOURCE_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("worktree:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw
        if not path.is_file():
            errors.append(f"missing pin target: {raw}")
        elif sha256(path.read_bytes()) != digest:
            errors.append(f"pin mismatch: {raw}")
    return len(lines)


def strict_load(path: Path, errors: list[str]):
    def reject(x):
        raise ValueError(f"non-finite {x}")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)
    except Exception as e:
        errors.append(f"json invalid {path.name}: {e}")
        return None
    if not isinstance(obj, dict):
        errors.append(f"json root not object: {path.name}")
    return obj


def check_json(errors: list[str]) -> bool:
    report = strict_load(REPORT, errors)
    if report is None:
        return False
    if report.get("base_commit") != "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d":
        errors.append("base_commit mismatch")
    if report.get("status") != "proposal_only_synthetic_incomplete":
        errors.append("status mismatch")
    if report.get("qualification_status") != "not_qualified":
        errors.append("qualification_status mismatch")
    return True


def check_reproduction(errors: list[str]) -> tuple[bool, str]:
    sys.path.insert(0, str(HERE))
    import reference  # noqa
    expected = reference.canonical_report_bytes(reference.build_report())
    actual = REPORT.read_bytes()
    ok = expected == actual
    if not ok:
        errors.append("report.json not byte-reproducible")
    digest = sha256(actual)
    sha_line = REPORT_SHA.read_text(encoding="utf-8").strip() if REPORT_SHA.exists() else ""
    if sha_line != f"{digest}  report.json":
        errors.append("report.json.sha256 mismatch")
        ok = False
    return ok, digest


def check_licensing(errors: list[str]) -> bool:
    ok = True
    for p in sorted(HERE.glob("*.py")):
        head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_L not in head or SPDX_C not in head:
            errors.append(f"missing SPDX: {p.name}")
            ok = False
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml docs/** coverage missing")
        ok = False
    return ok


def check_scope(errors: list[str]) -> bool:
    r = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"], capture_output=True, text=True, check=True)
    ok = True
    for line in r.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            errors.append(f"out of scope change: {path}")
            ok = False
    return ok


def main() -> int:
    errors: list[str] = []
    pins = check_pins(errors)
    json_ok = check_json(errors)
    repro_ok, digest = check_reproduction(errors)
    lic_ok = check_licensing(errors)
    scope_ok = check_scope(errors)
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        print(f"pins_ok={not any('pin' in e for e in errors)} json_ok={json_ok} licensing_ok={lic_ok} scope_ok={scope_ok} reproduction_ok={repro_ok} report_sha256={digest}")
        return 1
    print(f"pins_ok=True json_ok=True licensing_ok=True scope_ok=True reproduction_ok=True pins={pins} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
