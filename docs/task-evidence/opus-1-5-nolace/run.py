# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic CLI for the Opus 1.5 NoLACE restoration blocker package.

``--report`` regenerates ``report.json`` and ``report.json.sha256`` only after
three byte-identical builds.  ``--sources`` prints the pinned local manifest.
``--inspect`` emits a compact deterministic disposition.  ``--request`` runs
the strict probe protocol.  Nothing here downloads, imports or executes a real
Opus 1.5 runtime, and no result qualifies a processor.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple

import reference

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
DIGEST_PATH = ROOT / "report.json.sha256"
SOURCES_PATH = ROOT / "SOURCES.sha256"


def read_manifest() -> Dict[str, str]:
    manifest: Dict[str, str] = {}
    for line in SOURCES_PATH.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        digest, name = line.split("  ", 1)
        if name in manifest:
            raise ValueError("duplicate_manifest_entry:" + name)
        manifest[name] = digest
    return manifest


def source_manifest() -> str:
    lines: List[str] = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or path == SOURCES_PATH:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        lines.append(reference.digest_file(path) + "  " + relative)
    return "\n".join(lines) + "\n"


def verify_pins() -> Dict[str, Any]:
    sources: Dict[str, str] = {}
    for name, expected in reference.SOURCE_PINS.items():
        path = reference.WORKSPACE / name
        if not path.is_file():
            raise ValueError("missing_source_pin:" + name)
        actual = reference.digest_file(path)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + name)
        sources[name] = actual
    boundary: Dict[str, str] = {}
    for name, expected in reference.BOUNDARY_PINS.items():
        path = reference.WORKTREE / name
        if not path.is_file():
            raise ValueError("missing_boundary_pin:" + name)
        actual = reference.digest_file(path)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + name)
        boundary[name] = actual
    siblings: Dict[str, str] = {}
    for name, expected in reference.SIBLING_PINS.items():
        path = reference.WORKTREE / name
        if not path.is_file():
            raise ValueError("missing_sibling_pin:" + name)
        actual = reference.digest_file(path)
        if actual != expected:
            raise ValueError("sibling_pin_mismatch:" + name)
        siblings[name] = actual
    local: Dict[str, str] = {}
    for name, expected in read_manifest().items():
        path = ROOT / name
        if not path.is_file():
            raise ValueError("missing_local_artifact:" + name)
        actual = reference.digest_file(path)
        if actual != expected:
            raise ValueError("local_artifact_mismatch:" + name)
        local[name] = actual
    return {
        "sources": sources,
        "boundary": boundary,
        "siblings": siblings,
        "local_artifacts": local,
        "counts": {"sources": len(sources), "boundary": len(boundary),
                   "siblings": len(siblings), "local_artifacts": len(local)},
        "verification": "exact SHA-256; missing or changed is a hard failure",
        "mutable_board_hashed": False,
    }


def regenerate() -> str:
    payloads: List[bytes] = []
    digests: List[str] = []
    for _ in range(3):
        text, digest = reference.canonical_report(reference.build_report())
        payloads.append(text.encode("utf-8"))
        digests.append(digest)
    if len(set(payloads)) != 1 or len(set(digests)) != 1:
        raise AssertionError("report_repeats_not_byte_identical")
    REPORT_PATH.write_bytes(payloads[0])
    DIGEST_PATH.write_text(digests[0] + "\n", encoding="ascii")
    return digests[0]


def inspect_payload() -> Dict[str, Any]:
    sidecar = DIGEST_PATH.read_text(encoding="ascii").strip() if DIGEST_PATH.is_file() else None
    return {
        "protocol_version": 1,
        "task": reference.TASK_ID,
        "component": reference.COMPONENT,
        "profile": reference.PROFILE,
        "status": reference.STATUS,
        "completeness": reference.COMPLETENESS,
        "decision": reference.DECISION,
        "qualification": dict(reference.QUALIFICATION),
        "release_gate_count": len(reference.RELEASE_GATES),
        "release_gate_statuses": [gate["status"] for gate in reference.RELEASE_GATES],
        "runtime_present": reference.runtime_presence()["present"],
        "processor_exposure": False,
        "registered": False,
        "default_enabled": False,
        "report_sidecar": sidecar,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true",
                        help="regenerate report.json and report.json.sha256")
    parser.add_argument("--sources", action="store_true",
                        help="print the SHA-256 manifest of package files")
    parser.add_argument("--inspect", action="store_true",
                        help="print a compact deterministic disposition")
    parser.add_argument("--request", type=Path, help="strict protocol-v1 probe request JSON")
    parser.add_argument("--result", type=Path, help="destination for canonical result JSON")
    options = parser.parse_args()
    selected = sum(bool(value) for value in
                   (options.report, options.sources, options.inspect, options.request))
    if selected != 1 or bool(options.result) != bool(options.request):
        parser.error("choose exactly one of --report, --sources, --inspect or --request/--result")
    if options.report:
        print(regenerate())
        return 0
    if options.sources:
        sys.stdout.write(source_manifest())
        return 0
    if options.inspect:
        sys.stdout.buffer.write(reference.canonical_bytes(inspect_payload()))
        return 0
    try:
        request = reference.read_strict_object(options.request)
        result = reference.probe(request)
        options.result.write_bytes(reference.canonical_bytes(result))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
