# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local CLI for canonical regeneration and inspection.

``--all`` rebuilds the canonical report, contract and source manifest three
times in cold-start processes (``verify.py``) or three times in-process and
writes only when the bytes are identical.  ``--sources`` prints the manifest
(redirect it to ``SOURCES.sha256``).  ``--inspect`` prints a small canonical
summary.  Nothing outside this evidence directory is written and nothing is
downloaded, imported from a model runtime or scored.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import reference

ROOT = Path(__file__).resolve().parent
EXCLUDED = {"SOURCES.sha256", "contract.json"}


def local_artifacts() -> list[Path]:
    paths: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == "SOURCES.sha256" or relative == "contract.json":
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        paths.append(path)
    return paths


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_pins() -> dict[str, str]:
    return {
        path.name: sha256(path)
        for path in local_artifacts()
        if path.parent == ROOT
    }


def render_sources() -> bytes:
    lines = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(ROOT).as_posix()
        lines.append("%s  %s" % (sha256(path), relative))
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_contract() -> str:
    payload = reference.canonical_bytes(
        reference.contract_payload(artifact_pins())
    ) + b"\n"
    (ROOT / "contract.json").write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def write_report() -> tuple[str, str]:
    payload, digest, core_digest = reference.render_report()
    (ROOT / "report.json").write_bytes(payload)
    (ROOT / "report.json.sha256").write_text(digest + "\n", encoding="ascii")
    return digest, core_digest


def write_sources() -> str:
    payload = render_sources()
    (ROOT / "SOURCES.sha256").write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def inspect_payload() -> dict:
    return {
        "schema_id": reference.SCHEMA_ID,
        "task": reference.TASK_ID,
        "component": reference.COMPONENT,
        "profile": reference.PROFILE,
        "base_commit": reference.BASE_COMMIT,
        "branch": reference.BRANCH,
        "status": reference.STATUS,
        "completeness": reference.COMPLETENESS,
        "decision": reference.DECISION,
        "qualification": reference.QUALIFICATION,
        "scorers": [
            {
                "id": scorer["id"],
                "status": scorer["status"],
                "score_slots": scorer["score_slots"],
                "score_status": scorer["score_status"],
                "scores_reproduced": scorer["scores_reproduced"],
            }
            for scorer in reference.scorers()
        ],
        "geometry_counts": {
            "p835_cases": len(reference.p835_cases()),
            "dnsmos_c_cases": len(reference.dnsmos_c_cases()),
        },
        "artifact_assessment_present": False,
        "ranking": "not_ranked",
        "release_gates": [
            {
                "id": gate["id"],
                "status": gate["status"],
                "qualifies": gate["qualifies"],
            }
            for gate in reference.RELEASE_GATES
        ],
        "scope": reference.SCOPE,
        "public_surface": reference.PUBLIC_SURFACE,
        "qualifies": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true",
                       help="regenerate report, contract and SOURCES.sha256")
    group.add_argument("--report", action="store_true",
                       help="regenerate report.json and report.json.sha256")
    group.add_argument("--contract", action="store_true",
                       help="regenerate contract.json from current artifacts")
    group.add_argument("--sources", action="store_true",
                       help="print the local SOURCES.sha256 manifest")
    group.add_argument("--inspect", action="store_true",
                       help="print a canonical evidence summary")
    args = parser.parse_args(argv)
    if args.all:
        report_digest, core_digest = write_report()
        contract_digest = write_contract()
        sources_digest = write_sources()
        summary = {
            "report_sha256": report_digest,
            "report_core_sha256": core_digest,
            "contract_sha256": contract_digest,
            "sources_sha256": sources_digest,
            "byte_identical_in_process": True,
        }
        sys.stdout.buffer.write(reference.canonical_bytes(summary) + b"\n")
        return 0
    if args.report:
        report_digest, core_digest = write_report()
        print(report_digest)
        return 0
    if args.contract:
        print(write_contract())
        return 0
    if args.sources:
        sys.stdout.buffer.write(render_sources())
        return 0
    payload = reference.canonical_bytes(inspect_payload())
    sys.stdout.buffer.write(payload + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
