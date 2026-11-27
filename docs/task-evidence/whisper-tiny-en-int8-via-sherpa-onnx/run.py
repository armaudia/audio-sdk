# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate whisper-tiny-en-int8-via-sherpa-onnx evidence bundle 3x.

Stdlib-only, deterministic, task-local writes only. No model/runtime/audio.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

TASK_PREFIX = reference.TASK_PREFIX
REPEAT = 3
LOCAL_PIN_FILES = reference.LOCAL_PIN_FILES


def build_sources() -> bytes:
    rows: list[tuple[str, str]] = []
    for rel, expected in sorted(reference.SOURCE_PINS.items()):
        actual = reference.sha256_file(reference.AUDIO_ROOT / rel)
        if actual != expected:
            raise reference.ReferenceError(f"source_pin_mismatch:{rel}:{actual}")
        rows.append((f"source:{rel}", actual))
    for rel, expected in sorted(reference.BOUNDARY_PINS.items()):
        actual = reference.sha256_file(reference.WORKTREE / rel)
        if actual != expected:
            raise reference.ReferenceError(f"boundary_pin_mismatch:{rel}:{actual}")
        rows.append((f"worktree:{rel}", actual))
    for name in LOCAL_PIN_FILES:
        if name == "SOURCES.sha256":
            continue
        p = HERE / name
        if not p.exists():
            raise reference.ReferenceError(f"missing_local_pin_file:{name}")
        rows.append((f"pkg:{name}", reference.sha256_file(p)))
    lines = [
        "# SHA-256 pins for SDK-WHISPER-TINY-EN-INT8-VIA-SHERPA-ONNX evidence.",
        "# source: paths relative to AUDIO_ROOT; worktree: relative to SDK worktree; pkg: task-local.",
        "# SOURCES.sha256 excludes itself.",
    ]
    for label, digest in rows:
        lines.append(f"{digest}  {label}")
    return ("\n".join(lines) + "\n").encode("ascii")


def write_once() -> dict[str, str]:
    contract = reference.build_contract()
    report = reference.build_report()
    # contract/report digests are self-consistent; report captures volatile head/branch,
    # so we normalize volatile fields for determinism check by keeping them as observed.
    contract_bytes = reference.canonical_bytes(contract)
    report_bytes = reference.canonical_bytes(report)
    report_sha = hashlib.sha256(report_bytes).hexdigest()

    (HERE / "contract.json").write_bytes(contract_bytes)
    (HERE / "report.json").write_bytes(report_bytes)
    (HERE / "report.json.sha256").write_text(f"{report_sha}  report.json\n", encoding="ascii")
    sources = build_sources()
    (HERE / "SOURCES.sha256").write_bytes(sources)
    return {
        "contract": hashlib.sha256(contract_bytes).hexdigest(),
        "report": report_sha,
        "sources": hashlib.sha256(sources).hexdigest(),
    }


def main() -> int:
    seen: list[dict[str, str]] = []
    for _ in range(REPEAT):
        seen.append(write_once())
    first = seen[0]
    ok = all(s == first for s in seen)
    print(f"repeat={REPEAT} byte_identical={str(ok).lower()} report_sha256={first['report']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
