# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate task-local WORLD vocoder blocker evidence deterministically."""

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
TARGETS = {"report.json", "sources", "readme", "all"}


def require_interpreter() -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        raise SystemExit(f"run.py requires CPython {reference.REQUIRED_INTERPRETER} (observed {observed})")


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def report_bytes() -> tuple[bytes, str]:
    text, digest = reference.canonical_report(reference.build_report())
    return text.encode("utf-8"), digest


def sources_bytes() -> bytes:
    for rel, expected in sorted(reference.SOURCE_PINS.items()):
        actual = reference.sha256_file(reference.AUDIO_ROOT / rel)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + rel)
    for rel, expected in sorted(reference.BOUNDARY_PINS.items()):
        actual = reference.sha256_file(reference.WORKTREE / rel)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + rel)
    return reference.sources_bytes()


def readme_bytes() -> bytes:
    text = (HERE / "README.md").read_text(encoding="utf-8")
    updated = reference.update_readme_digests(text)
    reference.verify_readme_digests(updated)
    return updated.encode("utf-8")


def write_once(targets: set[str]) -> str:
    digest = ""
    if "report.json" in targets:
        (HERE / "contract.json").write_bytes(contract_bytes())
        payload, digest = report_bytes()
        (HERE / "report.json").write_bytes(payload)
        (HERE / "report.json.sha256").write_bytes(f"{digest}  report.json\n".encode("ascii"))
    if "readme" in targets:
        (HERE / "README.md").write_bytes(readme_bytes())
    if "sources" in targets:
        # SOURCES pins README bytes; generate README first when both requested.
        if "readme" not in targets and (HERE / "README.md").is_file():
            pass
        (HERE / "SOURCES.sha256").write_bytes(sources_bytes())
    return digest


def main(argv: list[str]) -> int:
    require_interpreter()
    requested = set(argv[1:]) or {"all"}
    if not requested <= TARGETS:
        print("usage: run.py [report.json|sources|readme|all]", file=sys.stderr)
        return 2
    if "all" in requested:
        requested = {"report.json", "readme", "sources"}
    observed = []
    digest = ""
    for _ in range(REPEAT_COUNT):
        digest = write_once(requested)
        r = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest() if "report.json" in requested else "-"
        m = hashlib.sha256((HERE / "README.md").read_bytes()).hexdigest() if "readme" in requested else "-"
        s = hashlib.sha256((HERE / "SOURCES.sha256").read_bytes()).hexdigest() if "sources" in requested else "-"
        observed.append((r, m, s))
    if len(set(observed)) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    print(f"repeat={REPEAT_COUNT} byte_identical=true report_sha256={observed[0][0]} readme_sha256={observed[0][1]} sources_sha256={observed[0][2]} sidecar_digest={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
