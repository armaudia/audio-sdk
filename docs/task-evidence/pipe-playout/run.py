# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local pipe-playout evidence bundle 3x.

Only this task-local directory (or an explicit scratch output directory) is
written. Pinned source and boundary files are read-only inputs. No Bungee code,
native library, real audio, model, runtime, listening result or device timing is
used, downloaded or produced.
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


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def report_bytes() -> tuple[bytes, str]:
    text, digest = reference.canonical_report(reference.build_report())
    return text.encode("utf-8"), digest


def _pin_rows() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for relative, expected in sorted(reference.SOURCE_PINS.items()):
        path = reference.AUDIO_ROOT / relative
        if not path.is_file():
            raise ValueError("source_pin_missing:" + relative)
        actual = reference.sha256_file(path)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + relative)
        rows.append(("source:" + relative, actual))
    for relative, expected in sorted(reference.BOUNDARY_PINS.items()):
        path = reference.WORKTREE / relative
        if not path.is_file():
            raise ValueError("boundary_pin_missing:" + relative)
        actual = reference.sha256_file(path)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + relative)
        rows.append(("boundary:" + relative, actual))
    return rows


def sources_bytes(root: Path) -> bytes:
    rows = _pin_rows()
    for name in LOCAL_PIN_FILES:
        path = root / name
        if not path.is_file():
            path = HERE / name
        if not path.is_file():
            raise ValueError("local_pin_missing:" + name)
        rows.append((TASK_PREFIX + name, reference.sha256_file(path)))
    lines = [
        "# SHA-256 pins for SDK-PIPE-PLAYOUT readiness evidence.",
        "# source: paths are relative to AUDIO_ROOT; boundary: to the SDK "
        "worktree.",
        "# Task-local paths are worktree-relative. The mutable shared board is "
        "not pinned;",
        "# only its stable projected row identity gates. SOURCES.sha256 "
        "excludes itself.",
    ]
    lines.extend(f"{digest}  {name}" for name, digest in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def write_once(root: Path) -> tuple[str, str, str, str]:
    root.mkdir(parents=True, exist_ok=True)
    contract = contract_bytes()
    (root / "contract.json").write_bytes(contract)
    payload, digest = report_bytes()
    (root / "report.json").write_bytes(payload)
    (root / "report.json.sha256").write_bytes(
        f"{digest}  report.json\n".encode("ascii"))
    sources = sources_bytes(root)
    (root / "SOURCES.sha256").write_bytes(sources)
    return (
        hashlib.sha256(contract).hexdigest(),
        hashlib.sha256(payload).hexdigest(),
        hashlib.sha256((root / "report.json.sha256").read_bytes()).hexdigest(),
        hashlib.sha256(sources).hexdigest(),
    )


def main(argv: list[str]) -> int:
    output = HERE
    arguments = list(argv[1:])
    if arguments:
        if len(arguments) != 2 or arguments[0] != "--output":
            print("usage: run.py [--output DIR]", file=sys.stderr)
            return 2
        output = Path(arguments[1]).resolve()
    observed: list[tuple[str, str, str, str]] = []
    for _ in range(REPEAT_COUNT):
        observed.append(write_once(output))
    if len(set(observed)) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    contract_digest, report_digest, sidecar_digest, sources_digest = observed[0]
    print(f"repeat={REPEAT_COUNT} byte_identical=true "
          f"contract_sha256={contract_digest} report_sha256={report_digest} "
          f"sidecar_sha256={sidecar_digest} sources_sha256={sources_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
