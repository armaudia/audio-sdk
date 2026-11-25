# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Byte-identical regeneration for the SDK-SURVEY-CLN-07 evidence map.

Run ``python3.12 run.py all`` from this directory. No network, media, runtime,
board or handoff state is read or written beyond the pinned documents verified
by ``reference.py``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict

import reference

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

LOCAL_FILES = (
    "README.md",
    "SOURCES.sha256",
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

CONTRACT_EXCLUDED = ("contract.json", "SOURCES.sha256")
SOURCES_EXCLUDED = ("SOURCES.sha256",)


def _read(name: str) -> bytes:
    return (HERE / name).read_bytes()


def _write(name: str, data: bytes) -> None:
    (HERE / name).write_bytes(data)


def report_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_report())


def digest_bytes(data: bytes) -> str:
    return reference.sha256_bytes(data)


def write_report() -> str:
    data = report_bytes()
    _write("report.json", data)
    return digest_bytes(data)


def write_report_sha256(digest: str | None = None) -> str:
    if digest is None:
        digest = digest_bytes(_read("report.json"))
    data = (digest + "  report.json\n").encode("ascii")
    _write("report.json.sha256", data)
    return digest


def build_contract() -> bytes:
    report_digest = digest_bytes(report_bytes())
    report_sha256_bytes = (report_digest + "  report.json\n").encode("ascii")
    artifact_pins: Dict[str, str] = {}
    for name in sorted(LOCAL_FILES):
        if name in CONTRACT_EXCLUDED:
            continue
        if name == "report.json":
            data = report_bytes()
        elif name == "report.json.sha256":
            data = report_sha256_bytes
        else:
            data = _read(name)
        artifact_pins[name] = digest_bytes(data)

    contract = {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": "audio-sdk/task-evidence-contract/0.1",
        "task": reference.TASK,
        "title": reference.TITLE,
        "component": reference.COMPONENT,
        "branch": reference.BRANCH,
        "base_commit": reference.BASE_COMMIT,
        "profile": reference.PROFILE,
        "category_id": reference.CATEGORY_ID,
        "legacy_family": reference.LEGACY_FAMILY,
        "category_scope": dict(reference.CATEGORY_SCOPE),
        "spatial_boundary": dict(reference.SPATIAL_BOUNDARY),
        "adjacent_boundary": dict(reference.ADJACENT_BOUNDARY),
        "deliverable": "Bounded category evidence map; no execution, qualification, rights or release claim.",
        "write_scope": ["Category evidence map and bounded gap handoff"],
        "status": reference.STATUS,
        "qualification": {
            "decision": reference.DECISION,
            "status": reference.QUALIFICATION_STATUS,
            "qualification_status": reference.QUALIFICATION_STATUS,
            "readiness": reference.READINESS,
            "proposal_only": True,
            "survey_status": "incomplete",
            "qualifies": False,
            "processor_exposure": False,
            "missing_result_promoted": False,
        },
        "follow_up_policy": {
            "invent_new_tasks": False,
            "board_only": True,
            "allowed_modes": ["feasibility", "research-control", "foundation", "external-adapter"],
            "linked_task_ids": [link["task_id"] for link in reference.BOARD_LINKS],
        },
        "public_surface": dict(reference.BOUNDARY),
        "scope": dict(reference.SCOPE),
        "artifact_pins": artifact_pins,
        "source_pins": dict(reference.SOURCE_PINS),
        "boundary_pins": dict(reference.WORKTREE_PINS),
        "mutable_provenance": {
            "gate": False,
            "path": reference.BOARD_PATH,
            "note": "Board status is mutable and never hashed into canonical bytes; linked id/title/mode are gated in report.json.",
        },
        "license_sidecars": {
            "contract.json": "contract.json.license",
            "report.json": "report.json.license",
            "report.json.sha256": "report.json.sha256.license",
            "SOURCES.sha256": "SOURCES.sha256.license",
        },
        "release_gates": [gate["id"] for gate in reference.RELEASE_GATES],
        "reproduction": {
            "all": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            "order": "report.json -> report.json.sha256 -> contract.json -> SOURCES.sha256",
        },
    }
    return reference.canonical_bytes(contract)


def write_contract() -> bytes:
    data = build_contract()
    _write("contract.json", data)
    return data


def sources_bytes() -> bytes:
    rows = []
    for name in sorted(LOCAL_FILES):
        if name in SOURCES_EXCLUDED:
            continue
        rows.append((reference.sha256_file(HERE / name), "local:" + name))
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        rows.append((digest, "source:" + path))
    for path, digest in sorted(reference.WORKTREE_PINS.items()):
        rows.append((digest, "worktree:" + path))
    rows.sort(key=lambda row: row[1])
    return "".join("%s  %s\n" % row for row in rows).encode("ascii")


def write_sources() -> bytes:
    data = sources_bytes()
    _write("SOURCES.sha256", data)
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact",
        nargs="?",
        default="all",
        choices=("all", "report", "sha256", "contract", "sources"),
    )
    args = parser.parse_args(argv)

    if args.artifact in ("all", "report"):
        digest = write_report()
        print("report.json " + digest)
    if args.artifact in ("all", "sha256"):
        digest = write_report_sha256()
        print("report.json.sha256 " + digest)
    if args.artifact in ("all", "contract"):
        data = write_contract()
        print("contract.json " + digest_bytes(data))
    if args.artifact in ("all", "sources"):
        data = write_sources()
        print("SOURCES.sha256 " + digest_bytes(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
