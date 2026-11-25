# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification for the SDK-BUNGEE-BASIC task-local evidence package."""

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
SIDECAR = HERE / "report.json.sha256"
TASK_PREFIX = "docs/task-evidence/bungee-basic/"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins(errors: list[str]) -> int:
    lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
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


def check_json(errors: list[str]) -> bool:
    def reject(value: str):
        raise ValueError(f"non-finite {value}")
    try:
        report = json.loads(REPORT.read_text(encoding="utf-8"), parse_constant=reject)
    except Exception as exc:
        errors.append(f"json invalid: {exc}")
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
    import reference  # noqa: E402
    expected = reference.canonical_report_bytes(reference.build_report())
    actual = REPORT.read_bytes()
    ok = expected == actual
    if not ok:
        errors.append("report.json is not byte-reproducible")
    digest = sha256(actual)
    if SIDECAR.read_text(encoding="utf-8").strip() != f"{digest}  report.json":
        errors.append("report.json.sha256 mismatch")
        ok = False
    return ok, digest


def check_licensing(errors: list[str]) -> bool:
    ok = True
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_L not in head or SPDX_C not in head:
            errors.append(f"missing SPDX: {path.name}")
            ok = False
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX' '-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml docs/** coverage missing")
        ok = False
    return ok


def check_scope(errors: list[str]) -> bool:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True, check=True)
    ok = True
    for line in result.stdout.splitlines():
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
    licensing_ok = check_licensing(errors)
    scope_ok = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"pins_ok={bool(pins)} json_ok={json_ok} licensing_ok={licensing_ok} "
              f"scope_ok={scope_ok} reproduction_ok={repro_ok} report_sha256={digest}")
        return 1
    print(f"pins_ok=True json_ok=True licensing_ok=True scope_ok=True "
          f"reproduction_ok=True pins={pins} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
