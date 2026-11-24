# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only task-local verification: pins, strict JSON, reproduction, scope.

No ``reuse`` CLI is required: SPDX headers on new Python files and the REUSE.toml
``docs/**`` annotation are checked directly. The report is regenerated in
memory and compared byte-for-byte with the committed file; nothing is written.
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
REPORT_SHA = HERE / "report.json.sha256"
MEASUREMENTS = HERE / "runtime-measurements.json"
ADAPTER = HERE / "adapter.json"
TASK_PREFIX = "docs/task-evidence/rnnoise-speech-probability/"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins(errors: list[str]) -> int:
    lines = [raw for raw in PINS.read_text(encoding="utf-8").splitlines()
             if raw and not raw.startswith("#")]
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
            errors.append(f"pinned file missing: {relative}")
        elif sha256(path.read_bytes()) != digest:
            errors.append(f"pinned bytes changed: {relative}")
    return len(lines)


def strict_json(path: Path, errors: list[str], expected_base: bool = True) -> None:
    def reject(value: str) -> None:
        raise ValueError(f"non-finite JSON constant {value}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"),
                             parse_constant=reject)
    except (OSError, ValueError) as error:
        errors.append(f"invalid JSON {path.name}: {error}")
        return
    if not isinstance(payload, dict):
        errors.append(f"{path.name} root is not an object")
    elif expected_base and payload.get("base_commit") != (
            "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"):
        errors.append(f"{path.name} base commit is not pinned")


def check_json(errors: list[str]) -> int:
    strict_json(REPORT, errors)
    strict_json(MEASUREMENTS, errors, expected_base=False)
    strict_json(ADAPTER, errors, expected_base=False)
    return 3


def check_report_sha(errors: list[str]) -> str:
    digest = sha256(REPORT.read_bytes())
    expected = REPORT_SHA.read_text(encoding="utf-8").split()
    if len(expected) != 2 or expected[0] != digest or expected[1] != "report.json":
        errors.append("report.json.sha256 does not match report.json")
    return digest


def check_reproducible(errors: list[str]) -> bool:
    sys.path.insert(0, str(HERE))
    import reference  # noqa: PLC0415 - deterministic task-local module

    expected = reference.canonical_report_bytes(reference.build_report())
    ok = expected == REPORT.read_bytes()
    if not ok:
        errors.append("report.json is not byte-reproducible")
    return ok


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
    report_digest = check_report_sha(errors)
    reproduction_ok = check_reproducible(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"pins_ok=True json_ok=True licensing_ok=True scope_ok=True "
          f"reproduction_ok=True pins={pin_count} json_files={json_count} "
          f"report_sha256={report_digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
