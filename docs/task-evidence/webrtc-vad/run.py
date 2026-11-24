# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local CLI for the synthetic WebRTC-VAD analysis evidence.

``--report`` regenerates the canonical frozen report from three byte-identical
repeats.  ``--sources`` verifies pinned inputs and local artifacts.  The
``--crosscheck`` output is an independent recomputation of the same scores.
No option downloads, imports or executes a VAD wheel or native runtime.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import fixture
import reference

TASK_DIR = Path(__file__).resolve().parent
REPORT_FILE = TASK_DIR / "report.json"
SIDECAR_FILE = TASK_DIR / "report.json.sha256"
MANIFEST_FILE = TASK_DIR / "SOURCES.sha256"


def emit(value: Any) -> None:
    import sys
    sys.stdout.buffer.write(fixture.canonical_bytes(value))


def read_manifest() -> dict[str, str]:
    lines = MANIFEST_FILE.read_text(encoding="utf-8").splitlines()
    manifest: dict[str, str] = {}
    for line in lines:
        if not line:
            continue
        digest, name = line.split("  ", 1)
        if name in manifest:
            raise ValueError("duplicate_manifest_entry:" + name)
        manifest[name] = digest
    return manifest


def verify_pins() -> dict[str, Any]:
    sources: dict[str, str] = {}
    for name, expected in fixture.SOURCE_PINS.items():
        path = fixture.resolve_pin_path(name)
        if not path.is_file():
            raise ValueError("missing_pinned_source:" + name)
        actual = fixture.sha256_file(path)
        if actual != expected:
            raise ValueError("pinned_source_changed:" + name)
        sources[name] = actual
    local: dict[str, str] = {}
    for name, expected in read_manifest().items():
        path = TASK_DIR / name
        if not path.is_file():
            raise ValueError("missing_local_artifact:" + name)
        actual = fixture.sha256_file(path)
        if actual != expected:
            raise ValueError("local_artifact_changed:" + name)
        local[name] = actual
    board_path = fixture.resolve_pin_path(fixture.MUTABLE_BOARD)
    board_digest = fixture.sha256_file(board_path) if board_path.is_file() else "missing"
    return {
        "sources": sources,
        "local_artifacts": local,
        "mutable_provenance": {
            "path": fixture.MUTABLE_BOARD,
            "sha256_at_read": fixture.MUTABLE_BOARD_SHA256_AT_READ,
            "sha256_now": board_digest,
            "gate": False,
        },
        "verification": "exact SHA-256, missing or changed is a hard failure",
    }


def sources_payload() -> dict[str, Any]:
    core = verify_pins()
    core["counts"] = {"sources": len(core["sources"]),
                      "local_artifacts": len(core["local_artifacts"])}
    core["sources_sha256"] = fixture.sha256_bytes(fixture.canonical_bytes(core))
    return core


def regenerate() -> tuple[str, str]:
    """Generate three reports and write only when all three are byte-identical."""
    payloads: list[bytes] = []
    digests: list[str] = []
    for _ in range(3):
        text, digest = reference.canonical_report(reference.build_report())
        payloads.append(text.encode("utf-8"))
        digests.append(digest)
    if len(set(payloads)) != 1 or len(set(digests)) != 1:
        raise AssertionError("report_repeats_not_byte_identical")
    REPORT_FILE.write_bytes(payloads[0])
    SIDECAR_FILE.write_text(digests[0] + "\n", encoding="ascii")
    return digests[0], fixture.sha256_bytes(payloads[0])


def crosscheck_payload() -> dict[str, Any]:
    payloads = []
    for _ in range(3):
        payloads.append(fixture.canonical_bytes(reference.crosscheck_payload()))
    if len(set(payloads)) != 1:
        raise AssertionError("crosscheck_repeats_not_byte_identical")
    core = reference.crosscheck_payload()
    core["three_repeats"] = 3
    core["byte_identical"] = True
    return core


def inspect_payload() -> dict[str, Any]:
    return {
        "protocol_version": 1,
        "identity": reference.LOCAL_IDENTITY,
        "boundary_identity": reference.ADAPTER_ID,
        "status": reference.STATUS,
        "decision": reference.DECISION,
        "processor_exposure": reference.PROCESSOR_EXPOSURE,
        "registration": "unregistered; proposal only",
        "supported_formats": ["mono 16 kHz float32, 160-sample SDK frames"],
        "asset_readiness": [],
        "numeric_parity_with_wheel": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--report", action="store_true",
                       help="regenerate report.json and its sidecar from 3 identical repeats")
    group.add_argument("--sources", action="store_true",
                       help="verify and print pinned sources and local artifact digests")
    group.add_argument("--crosscheck", action="store_true",
                       help="print the independent deterministic crosscheck payload")
    group.add_argument("--inspect", action="store_true",
                       help="print the unregistered task-local boundary descriptor")
    options = parser.parse_args()
    if options.report:
        digest, file_digest = regenerate()
        print("task=" + reference.TASK)
        print("repeats=3 byte_identical=true")
        print("canonical_report_sha256=" + digest)
        print("report_file_sha256=" + file_digest)
    elif options.sources:
        emit(sources_payload())
    elif options.crosscheck:
        emit(crosscheck_payload())
    elif options.inspect:
        emit(inspect_payload())
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
