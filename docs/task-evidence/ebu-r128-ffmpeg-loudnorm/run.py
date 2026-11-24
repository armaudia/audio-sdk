# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local deterministic report and tool provenance."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import reference


def main() -> None:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: run.py <report.json> [tool-provenance.json]")
    report_path = Path(sys.argv[1])
    provenance_path = (Path(sys.argv[2]) if len(sys.argv) == 3
                       else report_path.parent / "tool-provenance.json")
    provenance_path.write_bytes(json.dumps(
        reference.TOOL_PROVENANCE, sort_keys=True, indent=2,
        ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n")
    report = reference.build_report()
    report_path.write_bytes(reference.canonical_report_bytes(report))
    digest = hashlib.sha256(report_path.read_bytes()).hexdigest()
    (report_path.parent / (report_path.name + ".sha256")).write_text(
        digest + "\n", encoding="utf-8")
    print("report_sha256=" + digest)
    print("fixture_digest=" + report["fixture_digest"])
    print("profile=" + report["profile"]
          + " qualification_status=" + report["qualification_status"]
          + " gates_blocked=" + str(sum(1 for gate in report["gates"].values()
                                        if gate["status"] == "blocked"))
          + " regressions=" + str(len(report["regressions"])))


if __name__ == "__main__":
    main()
