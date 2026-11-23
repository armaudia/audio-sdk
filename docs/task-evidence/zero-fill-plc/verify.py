# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local byte, JSON, licensing and scope verification.

No ``reuse`` CLI is installed locally, so this performs the equivalent
first-party checks available here: SPDX headers on new Python files, the
aggregate ``docs/**`` annotation in REUSE.toml, strict JSON parsing,
byte-reproducible report regeneration (cmp by SHA-256 and exact bytes) and
git write-scope confirmation. It never writes to the worktree.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
MEASUREMENTS = HERE / "runtime-measurements.json"
TASK_PREFIX = "docs/task-evidence/zero-fill-plc/"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins(errors: list[str]) -> int:
    lines = []
    for raw in PINS.read_text(encoding="utf-8").splitlines():
        if raw and not raw.startswith("#"):
            lines.append(raw)
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append(f"malformed pin line: {line!r}")
            continue
        digest, raw_path = parts
        root = SOURCE_ROOT if raw_path.startswith("source:") else SDK_ROOT
        relative = raw_path.split(":", 1)[1] if ":" in raw_path else raw_path
        path = root / relative
        if not path.is_file():
            errors.append(f"pinned file missing: {path}")
        elif sha256(path.read_bytes()) != digest:
            errors.append(f"pinned bytes changed: {relative}")
    return len(lines)


def check_json(errors: list[str]) -> None:
    def reject(value: str) -> None:
        raise ValueError(f"non-finite JSON constant {value}")

    for path in (REPORT, MEASUREMENTS):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"),
                                 parse_constant=reject)
        except (OSError, ValueError) as error:
            errors.append(f"invalid JSON {path.name}: {error}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{path.name} root is not an object")
        elif payload.get("base_commit") != "a5ee614fbed11259134eb719159f726fe37d3664":
            errors.append(f"{path.name} base commit is not pinned")


def check_reproducible(errors: list[str]) -> str:
    sys.path.insert(0, str(HERE))
    import fixture  # noqa: PLC0415 - deterministic task-local module

    expected = fixture.canonical_report_bytes(fixture.build_report())
    actual = REPORT.read_bytes()
    if expected != actual:  # explicit cmp-equivalent byte comparison
        errors.append("report.json is not byte-reproducible")
    return sha256(actual)


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE_LINE not in head or SPDX_COPYRIGHT_LINE not in head:
            errors.append(f"missing SPDX header: {path.name}")
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
            errors.append(f"change outside task scope: {path}")
    return changed


def main() -> int:
    errors: list[str] = []
    pin_count = check_pins(errors)
    check_json(errors)
    report_digest = check_reproducible(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"pins_ok={pin_count} json_ok=2 report_sha256={report_digest} "
          f"licensing_ok=1 scope_ok=1 changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
