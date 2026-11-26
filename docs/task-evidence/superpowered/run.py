# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate SDK-SUPERPOWERED blocker evidence deterministically.

Writes only files under docs/task-evidence/superpowered/. No network, no
downloads, no Superpowered runtime, no mutable TASKS.json hash.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import reference  # noqa: E402


TARGETS = {"report.json", "contract.json", "SOURCES.sha256", "report.json.sha256", "all"}


def write_once(selected: set[str]) -> str:
    if "contract.json" in selected:
        (HERE / "contract.json").write_bytes(reference.canonical_bytes(reference.build_contract()))
    report = reference.build_report()
    digest = reference.report_digest(report)
    if "report.json" in selected:
        (HERE / "report.json").write_bytes(reference.canonical_bytes(report))
    if "report.json.sha256" in selected:
        (HERE / "report.json.sha256").write_text(digest + "  report.json\n", encoding="utf-8")
    if "SOURCES.sha256" in selected:
        (HERE / "SOURCES.sha256").write_text(reference.sources_manifest(), encoding="utf-8")
    return digest


def main(argv: list[str]) -> int:
    selected = set(argv[1:]) or {"all"}
    if not selected <= TARGETS:
        print("usage: run.py [report.json|contract.json|SOURCES.sha256|report.json.sha256|all]", file=sys.stderr)
        return 2
    if "all" in selected:
        selected = {"report.json", "contract.json", "SOURCES.sha256", "report.json.sha256"}
    digests = []
    for _ in range(3):
        digests.append(write_once(selected))
    if len(set(digests)) != 1:
        print("FAIL: non-deterministic regeneration", file=sys.stderr)
        return 1
    print(f"ok repeat=3 report_sha256={digests[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
