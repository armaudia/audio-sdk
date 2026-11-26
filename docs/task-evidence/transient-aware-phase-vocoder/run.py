# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate task-local evidence three times; writes only this directory."""

from __future__ import annotations

import hashlib
import platform
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

REPEAT = 3


def require_interpreter() -> None:
    obs = platform.python_version()
    if obs != reference.REQUIRED_INTERPRETER:
        raise SystemExit(f"run.py requires CPython {reference.REQUIRED_INTERPRETER}, observed {obs}")


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def report_bytes() -> tuple[bytes, str]:
    text, digest = reference.canonical_report(reference.build_report())
    return text.encode("ascii"), digest


def sources_bytes() -> bytes:
    for rel, exp in sorted(reference.SOURCE_PINS.items()):
        act = reference.sha256_file(reference.AUDIO_ROOT / rel)
        if act != exp:
            raise ValueError("source_pin_mismatch:" + rel)
    for rel, exp in sorted(reference.BOUNDARY_PINS.items()):
        act = reference.sha256_file(reference.SDK_ROOT / rel)
        if act != exp:
            raise ValueError("boundary_pin_mismatch:" + rel)
    return reference.sources_bytes()


def readme_bytes() -> bytes:
    p = HERE / "README.md"
    text = p.read_text(encoding="utf-8")
    updated = reference.update_readme_tables(text)
    reference.verify_readme_digests(updated)
    return updated.encode("ascii")


def write_once(targets: set[str]) -> str:
    digest = ""
    if "report" in targets:
        (HERE / "contract.json").write_bytes(contract_bytes())
        payload, digest = report_bytes()
        (HERE / "report.json").write_bytes(payload)
        (HERE / "report.json.sha256").write_text(f"{digest}  report.json\n", encoding="ascii")
    if "readme" in targets:
        (HERE / "README.md").write_bytes(readme_bytes())
    if "sources" in targets:
        (HERE / "SOURCES.sha256").write_bytes(sources_bytes())
    return digest


def main(argv: list[str]) -> int:
    require_interpreter()
    req = set(argv[1:]) or {"all"}
    if not req <= {"all", "report", "sources", "readme"}:
        print("usage: run.py [report|sources|readme|all]", file=sys.stderr)
        return 2
    if "all" in req:
        req = {"report", "readme", "sources"}
    obs = []
    sidecar = ""
    for _ in range(REPEAT):
        sidecar = write_once(req)
        obs.append(tuple(hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in ["report.json", "README.md", "SOURCES.sha256", "contract.json"]))
    if len(set(obs)) != 1:
        print("FAIL: regeneration not byte-identical", file=sys.stderr)
        return 1
    print(f"repeat={REPEAT} byte_identical=true report_sha256={obs[0][0]} readme_sha256={obs[0][1]} sources_sha256={obs[0][2]} contract_sha256={obs[0][3]} sidecar={sidecar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
