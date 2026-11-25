# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the deterministic SDK-LOCALVQE-COMPACT-ECHO-ONLY artifacts.

Usage::

    PYTHONDONTWRITEBYTECODE=1 SOURCE_ROOT=<workspace> python3 run.py

Builds the contract, report, report sidecar, README digest tables and
SOURCES.sha256 three times from cold start and requires byte-identical output
before writing. It never reads audio, downloads a model, loads a weight,
imports LocalVQE or executes a native runtime.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

TABLE_SECTIONS = (
    "source", "boundary", "artifacts", "external-absent", "external-runtime")
TABLE_HEADER = "| Key | SHA-256 |\n| --- | --- |"
TABLE_RE = re.compile(
    r"<!-- digest-table: ([a-z-]+) -->\n.*?\n<!-- digest-table: end -->",
    re.S)


def _rows(items: List[Tuple[str, str]]) -> str:
    return "\n".join(f"| `{key}` | `{digest}` |" for key, digest in items)


def _table_items() -> Dict[str, List[Tuple[str, str]]]:
    source = [("source:" + path, digest)
              for path, digest in sorted(reference.SOURCE_PINS.items())]
    boundary = [("sdk:" + path, digest)
                for path, digest in sorted(reference.BOUNDARY_PINS.items())]
    artifacts = [(name, reference.sha256_file(HERE / name))
                 for name in sorted(reference.LOCAL_ARTIFACT_PATHS)]
    absent = [(key, meta["sha256"])
              for key, meta in sorted(
                  reference.EXTERNAL_ASSET_PINS.items())]
    runtime = [(key, meta["sha256"])
               for key, meta in sorted(
                   reference.EXTERNAL_RUNTIME_PINS.items())]
    return {
        "source": source,
        "boundary": boundary,
        "artifacts": artifacts,
        "external-absent": absent,
        "external-runtime": runtime,
    }


def refresh_readme() -> bool:
    path = HERE / "README.md"
    text = path.read_text(encoding="utf-8")
    items = _table_items()
    updated = text
    for section in TABLE_SECTIONS:
        marker = f"<!-- digest-table: {section} -->"
        pattern = re.compile(
            re.escape(marker) + r"\n.*?\n<!-- digest-table: end -->", re.S)
        if not pattern.search(updated):
            raise RuntimeError("README table marker missing: " + section)
        block = marker + "\n" + TABLE_HEADER + "\n" + _rows(
            items[section]) + "\n<!-- digest-table: end -->"
        updated = pattern.sub(lambda _match, body=block: body, updated,
                              count=1)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def build() -> Dict[str, bytes]:
    report = reference.canonical_report_bytes(reference.build_report())
    contract = reference.contract_bytes()
    digest = hashlib.sha256(report).hexdigest()
    sidecar = f"{digest}  report.json\n".encode("ascii")
    return {"contract.json": contract, "report.json": report,
            "report.json.sha256": sidecar}


def main() -> int:
    snapshots: List[Dict[str, bytes]] = []
    for _ in range(3):
        snapshots.append(build())
    first = snapshots[0]
    for index, snapshot in enumerate(snapshots[1:], 2):
        if snapshot != first:
            raise SystemExit("cold_start_mismatch_at_" + str(index))
    for name, payload in first.items():
        (HERE / name).write_bytes(payload)
    refresh_readme()
    sources = reference.sources_bytes()
    (HERE / "SOURCES.sha256").write_bytes(sources)
    digest = hashlib.sha256(first["report.json"]).hexdigest()
    print(
        "wrote contract.json report.json report.json.sha256 README.md "
        f"SOURCES.sha256 report_sha256={digest} decision={reference.DECISION} "
        f"status={reference.STATUS} qualification={reference.QUALIFICATION} "
        f"gates={len(reference.GATE_DEFINITIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
