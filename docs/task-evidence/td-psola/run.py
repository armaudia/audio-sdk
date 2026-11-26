# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local TD-PSOLA evidence bundle three times."""

from __future__ import annotations

import hashlib
import platform
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

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


def require_interpreter() -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        raise SystemExit(
            "run.py requires CPython %s (observed %s)"
            % (reference.REQUIRED_INTERPRETER, observed))


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def canonical_report_bytes() -> tuple[bytes, str]:
    text, digest = reference.canonical_report(reference.build_report())
    return text.encode("ascii"), digest


def sources_bytes() -> bytes:
    rows = reference.local_pin_rows()
    for name in LOCAL_PIN_FILES:
        path = HERE / name
        if not path.is_file():
            raise ValueError("local_pin_missing:" + name)
        rows.append((reference.TASK_PREFIX + name, reference.sha256_file(path)))
    lines = [
        "# SHA-256 pins for SDK-TD-PSOLA evidence.",
        "# source: paths are relative to AUDIO_ROOT; other paths are SDK-worktree relative.",
        "# The mutable shared board is not pinned; only stable linked-row identity gates.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {name}" for digest, name in ((d, n) for n, d in rows))
    return ("\n".join(lines) + "\n").encode("ascii")


def write_once(targets: set[str]) -> str:
    digest = ""
    if "report.json" in targets:
        (HERE / "contract.json").write_bytes(contract_bytes())
        payload, digest = canonical_report_bytes()
        (HERE / "report.json").write_bytes(payload)
        (HERE / "report.json.sha256").write_bytes((digest + "  report.json\n").encode("ascii"))
    if "sources" in targets:
        (HERE / "SOURCES.sha256").write_bytes(sources_bytes())
    return digest


def main(argv: list[str]) -> int:
    require_interpreter()
    requested = set(argv[1:]) or {"all"}
    if not requested <= TARGETS:
        print("usage: run.py [report.json|sources|all]", file=sys.stderr)
        return 2
    if "all" in requested:
        requested = {"report.json", "sources"}
    observed: list[tuple[str, str]] = []
    digest = ""
    for _ in range(REPEAT_COUNT):
        digest = write_once(requested)
        report_digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest() if "report.json" in requested else "-"
        sources_digest = hashlib.sha256((HERE / "SOURCES.sha256").read_bytes()).hexdigest() if "sources" in requested else "-"
        observed.append((report_digest, sources_digest))
    if len(set(observed)) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    print(
        f"repeat={REPEAT_COUNT} byte_identical=true report_sha256={observed[0][0]} sources_sha256={observed[0][1]} sidecar_digest={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
