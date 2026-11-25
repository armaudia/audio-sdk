# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local Kokoro 82M evidence bundle three times.

Only this task-local directory is written. Pinned source and boundary files are
read-only inputs. No Kokoro source, weight, config, preset voice-style asset,
runtime, audio, network, model or inference path is used, downloaded or
produced.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

TASK_PREFIX = reference.TASK_PREFIX
REPEAT_COUNT = 3
LOCAL_PIN_FILES = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)
TARGETS = {"report.json", "sources", "all"}


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def canonical_report_bytes() -> tuple[bytes, str]:
    """Return canonical report bytes and their SHA-256 hex digest."""
    text, digest = reference.canonical_report(reference.build_report())
    return text.encode("utf-8"), digest


def sources_bytes() -> bytes:
    """Build the deterministic SHA-256 manifest from pinned read-only inputs."""
    rows: list[tuple[str, str]] = []
    for relative, expected in sorted(reference.SOURCE_PINS.items()):
        actual = reference.sha256_file(reference.AUDIO_ROOT / relative)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + relative)
        rows.append(("source:" + relative, actual))
    for relative, expected in sorted(reference.BOUNDARY_PINS.items()):
        actual = reference.sha256_file(reference.WORKTREE / relative)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + relative)
        rows.append((relative, actual))
    for name in LOCAL_PIN_FILES:
        path = HERE / name
        if not path.is_file():
            raise ValueError("local_pin_missing:" + name)
        rows.append((TASK_PREFIX + name, reference.sha256_file(path)))
    lines = [
        "# SHA-256 pins for SDK-KOKORO-82M task-local readiness evidence.",
        "# source: paths are relative to AUDIO_ROOT; other paths are SDK-worktree relative.",
        "# The mutable shared board is not pinned; only its stable row identity gates.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {name}" for name, digest in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def write_once(targets: set[str]) -> str:
    """Write the requested artifacts once and return the report digest."""
    digest = ""
    if "report.json" in targets:
        (HERE / "contract.json").write_bytes(contract_bytes())
        payload, digest = canonical_report_bytes()
        (HERE / "report.json").write_bytes(payload)
        (HERE / "report.json.sha256").write_bytes(
            f"{digest}  report.json\n".encode("ascii"))
    if "sources" in targets:
        (HERE / "SOURCES.sha256").write_bytes(sources_bytes())
    return digest


def main(argv: list[str]) -> int:
    requested = set(argv[1:]) or {"all"}
    if not requested or not requested <= TARGETS:
        print("usage: run.py [report.json|sources|all]", file=sys.stderr)
        return 2
    if "all" in requested:
        requested = {"report.json", "sources"}
    observed: list[tuple[str, str]] = []
    digest = ""
    for _ in range(REPEAT_COUNT):
        digest = write_once(requested)
        report_digest = (
            hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
            if "report.json" in requested else "-")
        sources_digest = (
            hashlib.sha256((HERE / "SOURCES.sha256").read_bytes()).hexdigest()
            if "sources" in requested else "-")
        observed.append((report_digest, sources_digest))
    if len(set(observed)) != 1 or any(part == "-" for part in observed[0]):
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    print(f"repeat={REPEAT_COUNT} byte_identical=true "
          f"report_sha256={observed[0][0]} sources_sha256={observed[0][1]} "
          f"sidecar_digest={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
