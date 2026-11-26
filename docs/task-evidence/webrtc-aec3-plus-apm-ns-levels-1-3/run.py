# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local CLI for canonical regeneration and inspection.

``--report`` rebuilds the canonical report three times and writes only when the
bytes are identical.  ``--sources`` prints the local SHA-256 manifest (redirect
it to ``SOURCES.sha256``).  ``--inspect`` prints a small canonical summary.
Nothing outside this evidence directory is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import reference

ROOT = Path(__file__).resolve().parent
EXCLUDED = {"SOURCES.sha256"}


def local_artifacts() -> list[Path]:
    paths: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in EXCLUDED:
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        paths.append(path)
    return paths


def render_sources() -> bytes:
    lines = []
    for path in local_artifacts():
        relative = path.relative_to(ROOT).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append("%s  %s" % (digest, relative))
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_report() -> str:
    payload, digest, canonical_digest = reference.render_report()
    (ROOT / "report.json").write_bytes(payload)
    (ROOT / "report.json.sha256").write_text(digest + "\n", encoding="ascii")
    return canonical_digest


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
        "configured_apm_instance": reference.configured_apm_payload(),
        "release_gates": [
            {"id": gate["id"], "status": gate["status"], "qualifies": gate["qualifies"]}
            for gate in reference.RELEASE_GATES
        ],
        "scope": reference.SCOPE,
        "public_surface": reference.PUBLIC_SURFACE,
        "qualifies": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true",
                       help="regenerate report.json and report.json.sha256")
    group.add_argument("--sources", action="store_true",
                       help="print the local SOURCES.sha256 manifest")
    group.add_argument("--inspect", action="store_true",
                       help="print a canonical configured-instance summary")
    args = parser.parse_args(argv)
    if args.report:
        digest = write_report()
        print(digest)
        return 0
    if args.sources:
        sys.stdout.buffer.write(render_sources())
        return 0
    payload = reference.canonical_bytes(inspect_payload())
    sys.stdout.buffer.write(payload + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
