# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local Neural WSOLA evidence bundle three times.

Only this task-local directory is written. Pinned source and boundary files
are read-only inputs. No Neural WSOLA code, weight, checkpoint, runtime, audio,
inference or result is used or produced.
"""

from __future__ import annotations

import hashlib
import platform
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

TASK_PREFIX = reference.TASK_PREFIX
REPEAT_COUNT = 3
TARGETS = {"report.json", "sources", "readme", "all"}


def require_interpreter() -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        raise SystemExit(
            "run.py requires CPython %s (observed %s); the canonical bundle "
            "pins the interpreter used for regeneration."
            % (reference.REQUIRED_INTERPRETER, observed))


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def canonical_report_bytes() -> tuple[bytes, str]:
    text, digest = reference.canonical_report(reference.build_report())
    return text.encode("ascii"), digest


def sources_bytes() -> bytes:
    for relative, expected in sorted(reference.SOURCE_PINS.items()):
        actual = reference.sha256_file(reference.AUDIO_ROOT / relative)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + relative)
    for relative, expected in sorted(reference.BOUNDARY_PINS.items()):
        actual = reference.sha256_file(reference.WORKTREE / relative)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + relative)
    return reference.sources_bytes()


def readme_bytes() -> bytes:
    path = HERE / "README.md"
    text = path.read_text(encoding="utf-8")
    updated = reference.update_readme_tables(text)
    reference.verify_readme_digests(updated)
    return updated.encode("ascii")


def write_once(targets: set[str]) -> str:
    digest = ""
    if "report.json" in targets:
        (HERE / "contract.json").write_bytes(contract_bytes())
        payload, digest = canonical_report_bytes()
        (HERE / "report.json").write_bytes(payload)
        (HERE / "report.json.sha256").write_bytes(
            f"{digest}  report.json\n".encode("ascii"))
    if "readme" in targets:
        (HERE / "README.md").write_bytes(readme_bytes())
    if "sources" in targets:
        (HERE / "SOURCES.sha256").write_bytes(sources_bytes())
    return digest


def main(argv: list[str]) -> int:
    require_interpreter()
    requested = set(argv[1:]) or {"all"}
    if not requested or not requested <= TARGETS:
        print("usage: run.py [report.json|sources|readme|all]", file=sys.stderr)
        return 2
    if "all" in requested:
        requested = {"report.json", "readme", "sources"}
    observed: list[tuple[str, ...]] = []
    digest = ""
    for _ in range(REPEAT_COUNT):
        digest = write_once(requested)
        report_digest = (
            hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
            if "report.json" in requested else "-")
        readme_digest = (
            hashlib.sha256((HERE / "README.md").read_bytes()).hexdigest()
            if "readme" in requested else "-")
        sources_digest = (
            hashlib.sha256((HERE / "SOURCES.sha256").read_bytes()).hexdigest()
            if "sources" in requested else "-")
        observed.append((report_digest, readme_digest, sources_digest))
    if len(set(observed)) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    requested_parts = []
    if "report.json" in requested:
        requested_parts.append(observed[0][0])
    if "readme" in requested:
        requested_parts.append(observed[0][1])
    if "sources" in requested:
        requested_parts.append(observed[0][2])
    if any(part == "-" for part in requested_parts):
        print("FAIL: a requested artifact was not regenerated", file=sys.stderr)
        return 1
    print(f"repeat={REPEAT_COUNT} byte_identical=true "
          f"report_sha256={observed[0][0]} "
          f"readme_sha256={observed[0][1]} "
          f"sources_sha256={observed[0][2]} sidecar_digest={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
