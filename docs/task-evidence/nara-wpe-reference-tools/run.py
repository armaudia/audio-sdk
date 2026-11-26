# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the SDK-NARA-WPE-REFERENCE-TOOLS bundle byte-for-byte.

Only this task-local directory is written. The pinned source and boundary
files are read-only inputs; no NARA-WPE code, wheel, runtime, model, corpus or
asset is downloaded, imported, executed or produced.
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
LOCAL_PIN_FILES = reference.LOCAL_FILES
TARGETS = {"report.json", "contract.json", "readme", "sources", "all"}


def canonical_report_bytes() -> tuple[bytes, str]:
    payload = reference.canonical_report_bytes()
    return payload, hashlib.sha256(payload).hexdigest()


def write_once(targets: set[str]) -> tuple[str, str, str, str]:
    """Write once in dependency order and return the four output digests."""
    if "contract.json" in targets:
        (HERE / "contract.json").write_bytes(
            reference.canonical_contract_bytes())
    if "report.json" in targets:
        payload, digest = canonical_report_bytes()
        (HERE / "report.json").write_bytes(payload)
        (HERE / "report.json.sha256").write_bytes(
            f"{digest}  report.json\n".encode("ascii"))
    if "readme" in targets:
        readme = HERE / "README.md"
        original = readme.read_text(encoding="utf-8")
        updated = reference.update_readme_artifact_table(original)
        if updated != original:
            readme.write_text(updated, encoding="utf-8", newline="\n")
    if "sources" in targets:
        (HERE / "SOURCES.sha256").write_bytes(reference.sources_bytes())
    return (
        hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest(),
        hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest(),
        hashlib.sha256((HERE / "SOURCES.sha256").read_bytes()).hexdigest(),
        hashlib.sha256((HERE / "README.md").read_bytes()).hexdigest(),
    )


def main(argv: list[str]) -> int:
    requested = set(argv[1:]) or {"all"}
    if not requested or not requested <= TARGETS:
        print("usage: run.py [report.json|contract.json|readme|sources|all]",
              file=sys.stderr)
        return 2
    if "all" in requested:
        requested = {"report.json", "contract.json", "readme", "sources"}
    observed: list[tuple[str, str, str, str]] = []
    for _ in range(REPEAT_COUNT):
        observed.append(write_once(requested))
    if len(set(observed)) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    report_digest, contract_digest, sources_digest, readme_digest = observed[0]
    if not all(observed[0]):
        print("FAIL: empty output digest", file=sys.stderr)
        return 1
    print(f"repeat={REPEAT_COUNT} byte_identical=true "
          f"report_sha256={report_digest} "
          f"contract_sha256={contract_digest} "
          f"sources_sha256={sources_digest} "
          f"readme_sha256={readme_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
