# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Canonical report, source-pin and contract generator for SDK-LIBSOXR.

The package is proposal evidence only. No libsoxr source, binary, header or
licensed runtime is present, downloaded or reconstructed. The generator writes
bounded task-local files and prints only digests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

import reference

HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
SOURCES_PATH = HERE / "SOURCES.sha256"
CONTRACT_PATH = HERE / "contract.json"
WORKSPACE = HERE.parents[5]
SDK_ROOT = HERE.parents[2]

PACKAGE_SOURCE_FILES = (
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "check_licensing.py",
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "test_reference.py",
    "verify.py",
)
CONTRACT_ARTIFACTS = PACKAGE_SOURCE_FILES + ("SOURCES.sha256",)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def write_report() -> str:
    payload = reference.report_bytes()
    report = reference.strict_json_loads(payload.decode("utf-8"))
    if not isinstance(report, dict):
        raise SystemExit("report root is not an object")
    REPORT_PATH.write_bytes(payload)
    digest = sha256_bytes(payload)
    SIDECAR_PATH.write_text(digest + "  report.json\n", encoding="ascii",
                            newline="\n")
    canonical = canonical_bytes(report)
    print("canonical_digest=" + sha256_bytes(canonical))
    print("report_file_digest=" + digest)
    return digest


def write_sources() -> None:
    if not REPORT_PATH.is_file():
        raise SystemExit("generate report.json before SOURCES.sha256")
    lines: List[str] = [
        "# SHA-256 pins for SDK-LIBSOXR; source: paths are workspace-relative, "
        "others SDK-worktree-relative.",
        "# No libsoxr source, header, binary or archive is pinned because none is present.",
    ]
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        target = WORKSPACE / path
        if not target.is_file():
            raise SystemExit("missing source pin target: " + path)
        actual = sha256_file(target)
        if actual != digest:
            raise SystemExit("source pin changed: " + path)
        lines.append(digest + "  source:" + path)
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        target = SDK_ROOT / path
        if not target.is_file():
            raise SystemExit("missing boundary pin target: " + path)
        actual = sha256_file(target)
        if actual != digest:
            raise SystemExit("boundary pin changed: " + path)
        lines.append(digest + "  " + path)
    for name in PACKAGE_SOURCE_FILES:
        path = HERE / name
        if not path.is_file():
            raise SystemExit("missing package artifact: " + name)
        lines.append(sha256_file(path) + "  " + reference.TASK_PREFIX + name)
    SOURCES_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8",
                            newline="\n")
    print("sources_written=" + str(len(lines) - 2))


def build_contract() -> Dict[str, Any]:
    if not REPORT_PATH.is_file() or not SIDECAR_PATH.is_file():
        raise SystemExit("generate report.json and its sidecar first")
    report_payload = REPORT_PATH.read_bytes()
    report = reference.strict_json_loads(report_payload.decode("utf-8"))
    canonical = canonical_bytes(report)
    report_sha = sha256_bytes(report_payload)
    canonical_digest = sha256_bytes(canonical)
    sidecar_sha = sha256_file(SIDECAR_PATH)
    links, link_digest = reference.board_link_projection()
    pins = {name: sha256_file(HERE / name) for name in CONTRACT_ARTIFACTS}
    return {
        "contract_version": "0.1",
        "schema_id": "audio-sdk/libsoxr-contract/0.1",
        "task": reference.TASK,
        "component": reference.COMPONENT,
        "branch": reference.BRANCH,
        "base_commit": reference.BASE_COMMIT,
        "status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "qualification": reference.qualification(),
        "boundary": {
            "format": {
                "sample_rate_hz": reference.SAMPLE_RATE_HZ,
                "channels": 1,
                "sample_format": "float32",
                "frame_samples": reference.FRAME_SAMPLES,
            },
            "installed_v0_unchanged": True,
            "public_api_abi_changed": False,
            "public_c_boundary": "not used: no C provider, header or installed target",
            "provider_registered": False,
            "provider_intake_complete": False,
            "descriptor_registration": False,
            "descriptor_default_changed": False,
            "enabled_by_default": False,
            "opt_in_required": True,
            "registry_changed": False,
            "shared_cmake_changed": False,
            "ci_changed": False,
            "board_or_handoff_changed": False,
            "real_corpus_or_weights": False,
            "benchmark_claim": False,
            "release_claim": False,
        },
        "profile": {
            "name": "rate",
            "source": reference.SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        },
        "invariants": list(reference.INVARIANTS),
        "non_claims": list(reference.NON_CLAIMS),
        "source_pins": dict(reference.SOURCE_PINS),
        "boundary_pins": dict(reference.BOUNDARY_PINS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "canonical_report": {
            "format": ("canonical JSON: sort_keys=True, compact separators, "
                       "allow_nan=False, one trailing newline"),
            "file_sha256": report_sha,
            "canonical_digest": canonical_digest,
            "sidecar_sha256": sidecar_sha,
        },
        "artifact_pins": pins,
        "upstream_blocker": dict(reference.UPSTREAM_BLOCKER),
        "release_gates": [dict(gate) for gate in reference.GATES],
    }


def write_contract() -> None:
    contract = build_contract()
    CONTRACT_PATH.write_bytes(canonical_bytes(contract) + b"\n")
    print("contract_file_digest=" + sha256_file(CONTRACT_PATH))


def stdout_report() -> None:
    sys.stdout.buffer.write(reference.report_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true",
                       help="regenerate report.json and its SHA-256 sidecar")
    group.add_argument("--sources", action="store_true",
                       help="regenerate SOURCES.sha256")
    group.add_argument("--contract", action="store_true",
                       help="regenerate contract.json from frozen artifacts")
    group.add_argument("--stdout-report", action="store_true",
                       help="write canonical report bytes to stdout only")
    args = parser.parse_args()
    if args.report:
        write_report()
    elif args.sources:
        write_sources()
    elif args.contract:
        write_contract()
    else:
        stdout_report()
    return 0


if __name__ == "__main__":
    sys.exit(main())
