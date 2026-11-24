# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the nightly-release / installer evidence package.

Checks, in order: every SOURCES.sha256 pin, strict finite JSON plus the report
sidecar, byte-identical in-memory report regeneration, SPDX headers on new
Python files, and git write-scope. It never writes to the worktree. The
``reuse`` CLI is not installed locally, so licensing is checked using the
aggregate REUSE.toml docs/** annotation plus per-file SPDX headers.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
REPORT_SHA = HERE / "report.json.sha256"
TASK_PREFIX = "docs/task-evidence/nightly-release-evidence-installer/"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins(errors: list[str]) -> int:
    lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed pin line: " + repr(line))
            continue
        digest, raw = parts
        if raw.startswith("source:"):
            path = SOURCE_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("worktree:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            errors.append("unprefixed pin path: " + raw)
            continue
        if not path.is_file():
            errors.append("pinned file missing: " + str(path))
        elif sha256(path.read_bytes()) != digest:
            errors.append("pinned bytes changed: " + raw)
    return len(lines)


def check_json(errors: list[str]) -> int:
    def reject(value: str) -> None:
        raise ValueError("nonfinite JSON constant " + value)

    checked = 0
    try:
        payload = json.loads(REPORT.read_text(encoding="utf-8"),
                             parse_constant=reject)
        checked += 1
        if not isinstance(payload, dict):
            errors.append("report.json root is not an object")
        elif payload.get("base_commit") != (
                "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"):
            errors.append("report.json base commit is not pinned")
        elif payload.get("profile") != "Tool":
            errors.append("report.json profile is not Tool")
        elif payload.get("qualification_status") != "not_qualified":
            errors.append("report.json qualification_status is not not_qualified")
    except (OSError, ValueError) as error:
        errors.append("invalid report.json: " + str(error))
    expected_sidecar = sha256(REPORT.read_bytes()) + "  report.json\n"
    if REPORT_SHA.read_text(encoding="utf-8") != expected_sidecar:
        errors.append("report.json.sha256 sidecar mismatch")
    else:
        checked += 1
    return checked


def check_reproduction(errors: list[str]) -> str:
    sys.path.insert(0, str(HERE))
    import fixture  # noqa: PLC0415 - deterministic task-local module

    expected = fixture.canonical_report_bytes(fixture.build_report())
    actual = REPORT.read_bytes()
    if expected != actual:  # explicit byte comparison, not a hash-only check
        errors.append("report.json is not byte-reproducible")
    return sha256(actual)


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing SPDX header: " + path.name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"], capture_output=True, text=True, check=True)
    changed = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    return changed


def main() -> int:
    errors: list[str] = []
    pin_count = check_pins(errors)
    json_count = check_json(errors)
    report_digest = check_reproduction(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    pins_ok = not any("pin" in error or "scope:" in error for error in errors)
    json_ok = not any("json" in error or "sidecar" in error for error in errors)
    licensing_ok = not any("SPDX" in error or "REUSE" in error for error in errors)
    scope_ok = not any("outside task scope" in error for error in errors)
    reproduction_ok = not any("byte-reproducible" in error for error in errors)
    status_ok = (pins_ok and json_ok and licensing_ok and scope_ok
                 and reproduction_ok)
    if errors:
        for error in errors:
            print("FAIL: " + error)
    print(f"pins_ok={int(pins_ok and pin_count > 0)} "
          f"json_ok={int(json_ok and json_count == 2)} "
          f"licensing_ok={int(licensing_ok)} "
          f"scope_ok={int(scope_ok)} "
          f"reproduction_ok={int(reproduction_ok)} "
          f"pins={pin_count} json_files={json_count} "
          f"changed_files={len(changed)} report_sha256={report_digest}")
    return 0 if status_ok and not errors else 1


if __name__ == "__main__":
    sys.exit(main())
