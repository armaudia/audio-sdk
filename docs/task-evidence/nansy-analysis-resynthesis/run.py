# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local NANSY analysis/resynthesis evidence three times.

Only this task-local directory is written. Pinned source and boundary files
are read-only inputs. No NANSY code, weight, config, runtime, real speech,
reference voice, resynthesis or result is used or produced.
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

REPEAT_COUNT = 3
TARGETS = {"report.json", "sources", "readme", "contract", "all"}


def require_interpreter() -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        raise SystemExit(
            "run.py requires CPython %s (observed %s); the canonical bundle "
            "pins the interpreter used for regeneration."
            % (reference.REQUIRED_INTERPRETER, observed))


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract()) + b"\n"


def sources_bytes() -> bytes:
    for relative, expected in sorted(reference.SOURCE_PINS.items()):
        actual = reference.sha256_file(reference.AUDIO_ROOT / relative)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + relative)
    for relative, expected in sorted(reference.BOUNDARY_PINS.items()):
        actual = reference.sha256_file(reference.SDK_ROOT / relative)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + relative)
    return reference.sources_bytes()


def readme_bytes() -> bytes:
    path = HERE / "README.md"
    text = path.read_text(encoding="utf-8")
    updated = reference.update_readme_tables(text)
    reference.verify_readme_digests(updated)
    return updated.encode("ascii")


def write_once(targets: set) -> str:
    digest = ""
    if "contract" in targets:
        (HERE / "contract.json").write_bytes(contract_bytes())
    if "report.json" in targets:
        payload = reference.report_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        (HERE / "report.json").write_bytes(payload)
        (HERE / "report.json.sha256").write_bytes(
            (digest + "  report.json\n").encode("ascii"))
    if "readme" in targets:
        (HERE / "README.md").write_bytes(readme_bytes())
    if "sources" in targets:
        (HERE / "SOURCES.sha256").write_bytes(sources_bytes())
    return digest


def main(argv: list[str]) -> int:
    require_interpreter()
    requested = set(argv[1:]) or {"all"}
    if not requested or not requested <= TARGETS:
        print("usage: run.py [report.json|contract|sources|readme|all]",
              file=sys.stderr)
        return 2
    if "all" in requested:
        requested = {"report.json", "contract", "readme", "sources"}
    observed: list[tuple[str, ...]] = []
    digest = ""
    for _ in range(REPEAT_COUNT):
        digest = write_once(requested)
        report_digest = (
            hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
            if "report.json" in requested else "-")
        contract_digest = (
            hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest()
            if "contract" in requested else "-")
        readme_digest = (
            hashlib.sha256((HERE / "README.md").read_bytes()).hexdigest()
            if "readme" in requested else "-")
        sources_digest = (
            hashlib.sha256((HERE / "SOURCES.sha256").read_bytes()).hexdigest()
            if "sources" in requested else "-")
        observed.append((report_digest, contract_digest,
                         readme_digest, sources_digest))
    if len(set(observed)) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    print("repeat=%d byte_identical=true report_sha256=%s "
          "contract_sha256=%s readme_sha256=%s sources_sha256=%s "
          "sidecar_digest=%s"
          % (REPEAT_COUNT, observed[0][0], observed[0][1],
             observed[0][2], observed[0][3], digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
