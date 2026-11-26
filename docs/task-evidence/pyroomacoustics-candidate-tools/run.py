# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local SDK-PYROOMACOUSTICS evidence bundle three times.

Only docs/task-evidence/pyroomacoustics-candidate-tools/ is written. Pinned
source and SDK boundary files are read-only inputs. No PyRoomAcoustics source,
wheel, runtime, room simulation, RIR, audio or result is used or downloaded.
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
LOCAL_PIN_FILES = reference.LOCAL_FILES
TARGETS = {"report.json", "sources", "all"}


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
    return text.encode("utf-8"), digest


def refresh_readme() -> None:
    path = HERE / "README.md"
    path.write_text(reference.update_readme_tables(
        path.read_text(encoding="utf-8")), encoding="utf-8")


def sources_bytes() -> bytes:
    return reference.sources_bytes()


def write_once(targets: set[str]) -> str:
    digest = ""
    if "report.json" in targets:
        (HERE / "contract.json").write_bytes(contract_bytes())
        payload, digest = canonical_report_bytes()
        (HERE / "report.json").write_bytes(payload)
        (HERE / "report.json.sha256").write_bytes(
            f"{digest}  report.json\n".encode("ascii"))
        refresh_readme()
    if "sources" in targets:
        (HERE / "SOURCES.sha256").write_bytes(sources_bytes())
    return digest


def main(argv: list[str]) -> int:
    require_interpreter()
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
