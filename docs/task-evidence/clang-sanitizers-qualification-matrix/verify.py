# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the task-local sanitizer/fuzz matrix evidence.

Checks the SOURCES.sha256 manifest, strict JSON, the report sidecar,
byte-identical in-memory report regeneration, SPDX headers, the pinned base
commit and git write scope. It never writes to the worktree.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
ADAPTER = HERE / "adapter.json"
TASK_PREFIX = "docs/task-evidence/clang-sanitizers-qualification-matrix/"
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value}")


def _load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"),
                         parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} root is not an object")
    return payload


def check_pins(errors: list[str]) -> int:
    lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append(f"malformed pin line: {line!r}")
            continue
        digest, raw_path = parts
        kind, _, relative = raw_path.partition(":")
        root = {"source": SOURCE_ROOT, "worktree": SDK_ROOT,
                "task": HERE}.get(kind)
        if root is None or not relative:
            errors.append(f"unknown pin root: {raw_path}")
            continue
        path = root / relative
        if not path.is_file():
            errors.append(f"pinned file missing: {raw_path}")
        elif _digest(path.read_bytes()) != digest:
            errors.append(f"pinned bytes changed: {raw_path}")
    return len(lines)


def _digest(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def check_json(errors: list[str]) -> int:
    loaded = 0
    for path in (REPORT, ADAPTER):
        try:
            payload = _load(path)
        except (OSError, ValueError) as error:
            errors.append(f"invalid JSON {path.name}: {error}")
            continue
        loaded += 1
        if payload.get("base_commit") != BASE_COMMIT:
            errors.append(f"{path.name} base commit is not pinned")
    try:
        sidecar = SIDECAR.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        errors.append(f"missing sidecar: {error}")
        return loaded
    if len(sidecar) != 1 or sidecar[0].split("  ")[-1] != REPORT.name:
        errors.append("malformed report.json.sha256 sidecar")
    elif sidecar[0].split("  ", 1)[0] != _digest(REPORT.read_bytes()):
        errors.append("report sidecar digest mismatch")
    return loaded + 1


def check_reproduction(errors: list[str]) -> str:
    sys.path.insert(0, str(HERE))
    import fixture  # noqa: PLC0415 - deterministic task-local module

    expected = fixture.canonical_report_bytes(fixture.build_report())
    actual = REPORT.read_bytes()
    if expected != actual:  # explicit cmp-equivalent byte comparison
        errors.append("report.json is not byte-reproducible")
    return _digest(actual)


def check_licensing(errors: list[str]) -> int:
    checked = 0
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append(f"missing SPDX header: {path.name}")
        checked += 1
    for path in (ADAPTER, REPORT):
        try:
            spdx = _load(path).get("spdx", {})
        except (OSError, ValueError):
            continue
        if (spdx.get("license") != SPDX_LICENSE
                or spdx.get("copyright") != SPDX_COPYRIGHT):
            errors.append(f"missing SPDX metadata: {path.name}")
        checked += 1
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")
    return checked


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
