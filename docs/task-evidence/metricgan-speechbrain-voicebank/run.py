# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the byte-identical report, digest sidecar and source manifest."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

MANIFEST_COMMENT = (
    "# SHA-256 pins for SDK-METRICGAN-SPEECHBRAIN-VOICEBANK; "
    "source: is workspace-relative, worktree: is SDK-worktree-relative.\n"
)


def resolve_pin(raw: str) -> Path:
    if raw.startswith("source:"):
        return reference.SOURCE_ROOT / raw.split(":", 1)[1]
    if raw.startswith("worktree:"):
        return reference.SDK_ROOT / raw.split(":", 1)[1]
    raise ValueError("unsupported pin prefix: " + raw)


def manifest_bytes() -> bytes:
    pins: dict[str, str] = {}
    for raw in reference.SOURCE_PIN_PATHS + reference.BOUNDARY_PIN_PATHS:
        path = resolve_pin(raw)
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing or non-regular pin target: " + raw)
        pins[raw] = reference.sha256_file(path)
    for name in reference.LOCAL_FILES:
        path = HERE / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing or non-regular local artifact: " + name)
        pins[f"worktree:docs/task-evidence/{reference.SLUG}/{name}"] = reference.sha256_file(path)
    if len(pins) != (len(reference.SOURCE_PIN_PATHS) + len(reference.BOUNDARY_PIN_PATHS)
                     + len(reference.LOCAL_FILES)):
        raise RuntimeError("duplicate pin path")
    lines = [MANIFEST_COMMENT.rstrip("\n")]
    lines.extend(f"{digest}  {raw}" for raw, digest in sorted(pins.items()))
    return ("\n".join(lines) + "\n").encode("utf-8")


def report_bytes() -> bytes:
    return reference.canonical_report_bytes(reference.build_report())


def write_report() -> str:
    payload = report_bytes()
    (HERE / "report.json").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (HERE / "report.json.sha256").write_text(f"{digest}  report.json\n", encoding="utf-8")
    return digest


def write_sources() -> int:
    payload = manifest_bytes()
    (HERE / "SOURCES.sha256").write_bytes(payload)
    return payload.count(b"\n") - 1


def main(argv: list[str]) -> int:
    modes = {"report.json", "--report", "--sources", "--all", "--digest"}
    if len(argv) != 2 or argv[1] not in modes:
        print("usage: run.py report.json | --report | --sources | --all | --digest",
              file=sys.stderr)
        return 2
    mode = argv[1]
    if mode in ("report.json", "--report", "--all", "--digest"):
        digest = write_report() if mode != "--digest" else hashlib.sha256(report_bytes()).hexdigest()
        print(f"report_sha256={digest} bytes={len(report_bytes())}")
    if mode in ("--sources", "--all"):
        print(f"source_pins={write_sources()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
