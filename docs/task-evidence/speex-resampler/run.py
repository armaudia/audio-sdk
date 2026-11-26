# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Canonical report, contract and source-pin generator for SDK-SPEEX-RESAMPLER.

The task-local adapter is unregistered and disabled by default. Only
``--report`` compiles and runs the pinned vendored SpeexDSP resampler against
synthetic fixtures. No C provider, installed target, descriptor, registry or
public ABI is added, and no file outside this directory is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

import reference

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "report.json"
DIGEST_PATH = ROOT / "report.json.sha256"
SOURCES_PATH = ROOT / "SOURCES.sha256"
CONTRACT_PATH = ROOT / "contract.json"
SOURCE_ARTIFACT_NAMES = tuple(sorted(
    set(reference.ARTIFACT_FILES) | {
        "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md",
        "contract.json", "report.json", "report.json.sha256",
    }))


def _sha256_file(path: Path) -> str:
    return reference.sha256_bytes(path.read_bytes())


def generate_report() -> str:
    report = reference.build_report()
    text, canonical_digest = reference.canonical_report(report)
    payload = text.encode("utf-8") + b"\n"
    REPORT_PATH.write_bytes(payload)
    file_digest = reference.sha256_bytes(payload)
    DIGEST_PATH.write_text(file_digest + "\n", encoding="ascii", newline="\n")
    print("canonical_digest=" + canonical_digest)
    print("report_file_digest=" + file_digest)
    return file_digest


def contract_manifest() -> Dict[str, Any]:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    _text, canonical_digest = reference.canonical_report(report)
    return {
        "schema_id": reference.CONTRACT_ID,
        "task": reference.TASK,
        "component": reference.COMPONENT,
        "contract_version": "0.1",
        "base_commit": reference.BASE_COMMIT,
        "branch": reference.BRANCH,
        "profile": {"name": "rate", "source": report["profile"]["source"]},
        "decision": "DEFER",
        "status": "proposal_only_not_qualified",
        "qualification_status": "not_qualified",
        "qualification": report["qualification"],
        "linked_row_identity": report["linked_row_identity"],
        "source_pins": reference.SOURCE_PINS,
        "boundary_pins": reference.BOUNDARY_PINS,
        "vendored_pins": reference.VENDORED_PINS,
        "board_snapshot": reference.BOARD_SNAPSHOT,
        "boundary": report["boundary"],
        "artifact_pins": {
            name: _sha256_file(ROOT / name)
            for name in reference.ARTIFACT_FILES
        },
        "canonical_report": {
            "canonical_digest": canonical_digest,
            "file_sha256": _sha256_file(REPORT_PATH),
            "sidecar_sha256": _sha256_file(DIGEST_PATH),
            "format": ("canonical JSON: sort_keys=True, compact separators, "
                       "allow_nan=False, one trailing newline"),
        },
        "invariants": list(report["non_claims"]),
        "gates": report["gates"],
        "remaining_gates": report["remaining_gates"],
    }


def generate_sources() -> str:
    contract = contract_manifest()
    CONTRACT_PATH.write_bytes(reference.canonical_bytes(contract) + b"\n")
    rows: List[str] = [
        "# SHA-256 pins for SDK-SPEEX-RESAMPLER. source: rows are relative to "
        "the workspace root; other rows are relative to this SDK worktree "
        "unless prefixed with " + reference.TASK_PREFIX + ".\n",
        "# board snapshot (mutable, provenance only): "
        + reference.BOARD_SNAPSHOT["path"] + "\n",
    ]
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        rows.append(digest + "  source:" + path + "\n")
    for path, digest in sorted({**reference.BOUNDARY_PINS,
                                **reference.VENDORED_PINS}.items()):
        rows.append(digest + "  " + path + "\n")
    for name in SOURCE_ARTIFACT_NAMES:
        rows.append(_sha256_file(ROOT / name) + "  "
                    + reference.TASK_PREFIX + name + "\n")
    payload_text = "".join(rows)
    SOURCES_PATH.write_text(payload_text, encoding="utf-8", newline="\n")
    digest = reference.sha256_bytes(payload_text.encode("utf-8"))
    print("contract_digest=" + _sha256_file(CONTRACT_PATH))
    print("sources_manifest_digest=" + digest)
    return digest


def crosscheck() -> Dict[str, Any]:
    first_text, _ = reference.canonical_report(reference.build_report())
    second_text, _ = reference.canonical_report(reference.build_report())
    probe = reference.repeat_probe()
    result = {
        "report_byte_identical": first_text == second_text,
        "report_sha256": reference.sha256_bytes(
            (first_text + "\n").encode("utf-8")),
        "repeat_probe": probe,
    }
    print("report_sha256=" + result["report_sha256"])
    print("repeat_runs=" + str(probe["runs"]))
    print("repeat_byte_identical=" + str(probe["byte_identical"]))
    if not result["report_byte_identical"] or not probe["byte_identical"]:
        raise SystemExit(1)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true",
                        help="regenerate report.json and its SHA-256 sidecar")
    parser.add_argument("--sources", action="store_true",
                        help="regenerate contract.json and SOURCES.sha256")
    parser.add_argument("--crosscheck", action="store_true",
                        help="compare in-process renders and three cold starts")
    options = parser.parse_args()
    selected = sum(bool(value) for value in (
        options.report, options.sources, options.crosscheck))
    if selected != 1:
        parser.error("select exactly one of --report, --sources or --crosscheck")
    if options.report:
        generate_report()
        return 0
    if options.sources:
        generate_sources()
        return 0
    crosscheck()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
