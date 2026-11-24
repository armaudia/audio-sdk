# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the task-local static-gain evidence package.

Rechecks every pin in SOURCES.sha256, strict-loads report.json, checks the
recorded report digest, regenerates report.json in memory and requires exact
byte equality, checks SPDX headers and git write scope. No file is written.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
DIGEST = HERE / "report.json.sha256"
TASK_PREFIX = "docs/task-evidence/ridge-static-gain/"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
PYTHON_FILES = ("reference.py", "run.py", "test_reference.py", "verify.py")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins(errors: list[str]) -> int:
    lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
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


def check_json(errors: list[str]) -> int:
    def reject(value: str) -> None:
        raise ValueError(f"non-finite JSON constant {value}")

    try:
        payload = json.loads(REPORT.read_text(encoding="utf-8"),
                             parse_constant=reject)
        if not isinstance(payload, dict):
            raise ValueError("report root is not an object")
        if payload.get("base_commit") != "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0":
            raise ValueError("base commit is not pinned")
        if payload.get("profile") != "DSP":
            raise ValueError("acceptance profile is not DSP")
    except (OSError, ValueError) as error:
        errors.append(f"invalid report.json: {error}")
        return 0
    try:
        digest_line = DIGEST.read_text(encoding="ascii").strip()
        recorded, name = digest_line.split("  ", 1)
        if len(recorded) != 64 or name != REPORT.name:
            raise ValueError("malformed digest line")
        if recorded != sha256(REPORT.read_bytes()):
            raise ValueError("report.json digest mismatch")
    except (OSError, ValueError) as error:
        errors.append(f"invalid report.json.sha256: {error}")
        return 1
    return 2


def check_reproduction(errors: list[str]) -> str:
    sys.path.insert(0, str(HERE))
    import reference  # noqa: PLC0415 - deterministic task-local module

    expected = reference.canonical_report_bytes(reference.build_report())
    actual = REPORT.read_bytes()
    if expected != actual:
        errors.append("report.json is not byte-reproducible")
    return sha256(actual)


def check_licensing(errors: list[str]) -> None:
    for name in PYTHON_FILES:
        head = "\n".join((HERE / name).read_text(
            encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE_LINE not in head or SPDX_COPYRIGHT_LINE not in head:
            errors.append(f"missing SPDX header: {name}")
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"], capture_output=True, text=True, check=True)
    changed: list[str] = []
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
    json_count = check_json(errors)
    report_digest = check_reproduction(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    ok = 0 if errors else 1
    print(f"pins_ok={pin_count if not errors else 0} "
          f"json_ok={json_count if not errors else 0} "
          f"licensing_ok={ok} scope_ok={ok} reproduction_ok={ok} "
          f"report_sha256={report_digest} changed_files={len(changed)}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
