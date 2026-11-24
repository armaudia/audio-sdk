# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the task-local offline tooling fixture.

Rechecks every SOURCES.sha256 pin, strict-loads both JSON files, regenerates
report.json in memory and requires byte identity, checks SPDX headers and
write scope, and refuses generated binaries in the evidence directory.
Nothing in the worktree is written.
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
SITE_PACKAGES = Path(os.environ.get(
    "PY312_SITE_PACKAGES",
    "/Users/htsakanyan/.pyenv/versions/3.12.16/lib/python3.12/site-packages"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
REPORT_SHA = HERE / "report.json.sha256"
MEASUREMENTS = HERE / "runtime-measurements.json"
TASK_PREFIX = "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
BINARY_SUFFIXES = (".wav", ".flac", ".mp3", ".ogg", ".so", ".dylib", ".dll",
                   ".a", ".o", ".pyc", ".pyd")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins(errors: list[str]) -> int:
    count = 0
    for raw in PINS.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#"):
            continue
        count += 1
        parts = raw.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append(f"malformed pin line: {raw!r}")
            continue
        digest, raw_path = parts
        if raw_path.startswith("source:"):
            path = SOURCE_ROOT / raw_path.split(":", 1)[1]
        elif raw_path.startswith("py312:"):
            path = SITE_PACKAGES / raw_path.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw_path
        if not path.is_file():
            errors.append(f"pinned file missing: {raw_path}")
        elif sha256(path.read_bytes()) != digest:
            errors.append(f"pinned bytes changed: {raw_path}")
    return count


def strict_json(path: Path, errors: list[str]) -> dict | None:
    def reject(value: str) -> None:
        raise ValueError(f"non-finite JSON constant {value}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"),
                             parse_constant=reject)
    except (OSError, ValueError) as error:
        errors.append(f"invalid JSON {path.name}: {error}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{path.name} root is not an object")
        return None
    if payload.get("base_commit") != BASE_COMMIT:
        errors.append(f"{path.name} base commit is not pinned")
    return payload


def check_json(errors: list[str]) -> int:
    checked = 0
    for path in (REPORT, MEASUREMENTS):
        if strict_json(path, errors) is not None:
            checked += 1
    digest_line = REPORT_SHA.read_text(encoding="utf-8").strip()
    if digest_line != sha256(REPORT.read_bytes()):
        errors.append("report.json.sha256 does not match report.json")
    else:
        checked += 1
    return checked


def check_reproduction(errors: list[str]) -> str:
    sys.path.insert(0, str(HERE))
    import fixture  # noqa: PLC0415 - deterministic task-local module

    expected = fixture.canonical_report_bytes(fixture.build_report())
    actual = REPORT.read_bytes()
    if expected != actual:
        errors.append("report.json is not byte-reproducible")
    return sha256(actual)


def check_licensing(errors: list[str]) -> int:
    checked = 0
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE_LINE not in head or SPDX_COPYRIGHT_LINE not in head:
            errors.append(f"missing SPDX header: {path.name}")
        else:
            checked += 1
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")
    return checked


def check_no_binaries(errors: list[str]) -> None:
    for path in HERE.iterdir():
        if path.is_file() and path.suffix.lower() in BINARY_SUFFIXES:
            errors.append(f"generated binary in evidence dir: {path.name}")


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
    licensing_count = check_licensing(errors)
    check_no_binaries(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"pins_ok={pin_count} json_ok={json_count} "
          f"licensing_ok={licensing_count} scope_ok=1 reproduction_ok=1 "
          f"report_sha256={report_digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
