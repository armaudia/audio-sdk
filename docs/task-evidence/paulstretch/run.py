# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Canonical report, sources and contract generator for SDK-PAULSTRETCH.

Proposal-only blocker evidence. No PaulStretch source/runtime/weights/real
corpus are present or executed. The generator writes bounded task-local files
and prints only digests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Mapping

import reference

HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
SOURCES_PATH = HERE / "SOURCES.sha256"
CONTRACT_PATH = HERE / "contract.json"
README_PATH = HERE / "README.md"
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]

MANIFEST_FILES = (
    "README.md",
    "contract.json",
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "SOURCES.sha256",
    "test_reference.py",
    "verify.py",
)
SOURCES_FILES = (
    "README.md",
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "test_reference.py",
    "verify.py",
)
LICENSE_FILES = (
    "README.md.license",
    "contract.json.license",
    "reference.py.license",
    "report.json.license",
    "report.json.sha256.license",
    "run.py.license",
    "SOURCES.sha256.license",
    "test_reference.py.license",
    "verify.py.license",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def build_sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines: List[str] = [
        "# SHA-256 pins for SDK-PAULSTRETCH; source: paths are workspace-relative, others SDK-worktree-relative.",
        "# The mutable full plan/swarm/TASKS.json is deliberately not pinned; only stable linked-row identity is projected.",
        "# No PaulStretch source/runtime/binary/real corpus is included.",
    ]
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        target = WORKSPACE / path
        if not target.is_file():
            raise SystemExit("missing source pin target: " + path)
        if sha256_file(target) != digest:
            raise SystemExit("source pin changed: " + path)
        lines.append(digest + "  source:" + path)
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        target = SDK_ROOT / path
        if not target.is_file():
            raise SystemExit("missing boundary pin target: " + path)
        if sha256_file(target) != digest:
            raise SystemExit("boundary pin changed: " + path)
        lines.append(digest + "  " + path)
    for name in sorted(SOURCES_FILES):
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (HERE / name).read_bytes()
        lines.append(sha256_bytes(payload) + "  " + reference.TASK_PREFIX + name)
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_contract_bytes(report_payload: bytes, report: Mapping[str, Any],
                         sidecar_payload: bytes, sources_payload: bytes) -> bytes:
    artifact_pins = {}
    for name in sorted(MANIFEST_FILES):
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        elif name == "SOURCES.sha256":
            payload = sources_payload
        elif name == "contract.json":
            payload = b"{}"
        else:
            payload = (HERE / name).read_bytes()
        artifact_pins[name] = sha256_bytes(payload)
    contract = {
        "artifact_pins": artifact_pins,
        "base_commit": reference.BASE_COMMIT,
        "board_link_fields": list(reference.LINK_FIELDS),
        "board_link_projection_sha256": report["board_link_projection_sha256"],
        "board_links": report["board_links"],
        "board_mutable_fields_excluded": list(reference.MUTABLE_FIELDS_EXCLUDED),
        "boundary": report["boundary"],
        "boundary_pins": dict(reference.BOUNDARY_PINS),
        "branch": reference.BRANCH,
        "canonical_report": {
            "canonical_digest": sha256_bytes(canonical_bytes(report)),
            "file_sha256": sha256_bytes(report_payload),
            "format": "canonical JSON: sort_keys=True, compact separators, allow_nan=False, one trailing newline",
            "sidecar_sha256": sha256_bytes(sidecar_payload),
        },
        "comparison_status": "blocked_source_runtime_rights_absent",
        "component": reference.COMPONENT,
        "contract_version": "0.1",
        "decision": "DEFER",
        "evidence_entry": report["evidence_entry"],
        "invariants": list(reference.INVARIANTS),
        "non_claims": list(reference.NON_CLAIMS),
        "profile": report["profile"],
        "qualification": report["qualification"],
        "release_gates": report["release_gates"],
        "schema_id": reference.CONTRACT_SCHEMA_ID,
        "source_evidence_statements": report["source_evidence_statements"],
        "source_pins": dict(reference.SOURCE_PINS),
        "status": "proposal_only_not_qualified",
        "task": reference.TASK,
        "upstream_blocker": report["upstream_blocker"],
    }
    if not reference.finite_json(contract):
        raise SystemExit("contract contains a nonfinite value")
    return canonical_bytes(contract) + b"\n"


def write_report() -> str:
    report = reference.build_report()
    payload = canonical_bytes(report) + b"\n"
    REPORT_PATH.write_bytes(payload)
    SIDECAR_PATH.write_bytes(sidecar_bytes(payload))
    README_PATH.write_text(reference.render_markdown(report), encoding="utf-8")
    digest = sha256_bytes(payload)
    print("canonical_digest=" + sha256_bytes(canonical_bytes(report)))
    print("report_file_digest=" + digest)
    return digest


def write_sources() -> None:
    if not REPORT_PATH.is_file() or not SIDECAR_PATH.is_file():
        raise SystemExit("generate report.json and its sidecar first")
    payload = build_sources_bytes(REPORT_PATH.read_bytes(), SIDECAR_PATH.read_bytes())
    SOURCES_PATH.write_bytes(payload)
    print("sources_file_digest=" + sha256_bytes(payload))


def write_contract() -> None:
    if not REPORT_PATH.is_file() or not SIDECAR_PATH.is_file() or not SOURCES_PATH.is_file():
        raise SystemExit("generate report.json, sidecar and SOURCES.sha256 first")
    report_payload = REPORT_PATH.read_bytes()
    report = reference.strict_json_loads(report_payload.decode("utf-8"))
    payload = build_contract_bytes(report_payload, report, SIDECAR_PATH.read_bytes(), SOURCES_PATH.read_bytes())
    CONTRACT_PATH.write_bytes(payload)
    print("contract_file_digest=" + sha256_bytes(payload))


def ensure_licenses() -> None:
    for name in LICENSE_FILES:
        path = HERE / name
        if path.is_file():
            continue
        path.write_text(
            "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
            + "SPDX-License-" + "Identifier: Apache-2.0\n",
            encoding="utf-8",
        )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--sources", action="store_true")
    parser.add_argument("--contract", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args(argv)
    if not any([args.report, args.sources, args.contract, args.all]):
        parser.error("select --report, --sources, --contract, or --all")
    ensure_licenses()
    if args.all:
        write_report()
        # fixed-point: contract includes SOURCES; SOURCES includes contract
        for _ in range(3):
            write_sources()
            write_contract()
        write_sources()
        write_contract()
    else:
        if args.report:
            write_report()
        if args.sources:
            write_sources()
        if args.contract:
            write_contract()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
