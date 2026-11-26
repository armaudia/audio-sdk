# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Canonical report, source-pin and contract generator for SDK-MEANVC.

The package is proposal evidence only. No MeanVC checkpoint, weights, runtime,
real corpus audio, model output or download is present or reconstructed. The
exact Apache-2.0 source checkout is pinned read-only by revision, tree object,
tree content digest and selected file digests. The generator writes bounded
task-local files and prints only digests.
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
WORKSPACE = HERE.parents[5]
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = WORKSPACE / reference.SOURCE_ROOT

MANIFEST_FILES = (
    "README.md",
    "LICENSES.md",
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "test_reference.py",
    "verify.py",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)

CONTRACT_ARTIFACTS = MANIFEST_FILES + ("SOURCES.sha256",)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def _file_payload(name: str) -> bytes:
    path = HERE / name
    if not path.is_file():
        raise SystemExit("missing package artifact: " + name)
    return path.read_bytes()


def build_sources_bytes(report_payload: bytes,
                        sidecar_payload: bytes) -> bytes:
    lines: List[str] = [
        "# SHA-256 pins for SDK-MEANVC; source: paths are workspace-relative, "
        "others SDK-worktree-relative.",
        "# The mutable full plan/swarm/TASKS.json is deliberately not pinned; "
        "only the stable linked-row identity is projected.",
        "# The pinned MeanVC checkout is evidence identity only; no "
        "checkpoint, weight, runtime or real corpus audio is included.",
    ]
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        target = WORKSPACE / path
        if not target.is_file():
            raise SystemExit("missing source pin target: " + path)
        if sha256_file(target) != digest:
            raise SystemExit("source pin changed: " + path)
        lines.append(digest + "  source:" + path)
    for relative, digest in sorted(reference.SOURCE_ARTIFACTS.items()):
        target = SOURCE_ROOT / relative
        if not target.is_file():
            raise SystemExit("missing source artifact: " + relative)
        if sha256_file(target) != digest:
            raise SystemExit("source artifact changed: " + relative)
        lines.append(digest + "  source:" + reference.SOURCE_ROOT + "/" +
                     relative)
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        target = SDK_ROOT / path
        if not target.is_file():
            raise SystemExit("missing boundary pin target: " + path)
        if sha256_file(target) != digest:
            raise SystemExit("boundary pin changed: " + path)
        lines.append(digest + "  " + path)
    for name in sorted(MANIFEST_FILES):
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = _file_payload(name)
        lines.append(sha256_bytes(payload) + "  " + reference.TASK_PREFIX + name)
    return ("\n".join(lines) + "\n").encode("utf-8")


def build_contract_bytes(report_payload: bytes,
                         report: Mapping[str, Any],
                         sidecar_payload: bytes,
                         sources_payload: bytes) -> bytes:
    pins: Dict[str, str] = {}
    for name in sorted(CONTRACT_ARTIFACTS):
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        elif name == "SOURCES.sha256":
            payload = sources_payload
        else:
            payload = _file_payload(name)
        pins[name] = sha256_bytes(payload)
    links, link_digest = reference.board_link_projection()
    blocker = dict(reference.UPSTREAM_BLOCKER)
    blocker["weights"] = dict(blocker["weights"])
    blocker["weights"]["required"] = [
        dict(item) for item in report["weights_probe"]["required"]]
    contract = {
        "artifact_pins": pins,
        "base_commit": reference.BASE_COMMIT,
        "board_link_fields": list(reference.LINK_FIELDS),
        "board_link_projection_sha256": link_digest,
        "board_links": links,
        "board_mutable_fields_excluded": list(
            reference.MUTABLE_FIELDS_EXCLUDED),
        "boundary": reference.boundary(),
        "boundary_pins": dict(reference.BOUNDARY_PINS),
        "branch": reference.BRANCH,
        "canonical_report": {
            "canonical_digest": sha256_bytes(canonical_bytes(report)),
            "file_sha256": sha256_bytes(report_payload),
            "format": ("canonical JSON: sort_keys=True, compact separators, "
                       "allow_nan=False, one trailing newline"),
            "sidecar_sha256": sha256_bytes(sidecar_payload),
        },
        "comparison_status":
            "blocked_weights_runtime_absent_source_pinned",
        "component": reference.COMPONENT,
        "contract_version": "0.1",
        "decision": "DEFER",
        "evidence_entry": report["evidence_entry"],
        "geometry": report["geometry"],
        "inventory_link": report["inventory_link"],
        "invariants": list(reference.INVARIANTS),
        "non_claims": list(reference.NON_CLAIMS),
        "paper_lead": report["paper_lead"],
        "profile": report["profile"],
        "qualification": reference.qualification(),
        "release_gates": [dict(gate) for gate in reference.GATES],
        "schema_id": reference.CONTRACT_SCHEMA_ID,
        "source_artifacts": dict(reference.SOURCE_ARTIFACTS),
        "source_evidence_statements": reference.source_evidence_statements(),
        "source_pins": dict(reference.SOURCE_PINS),
        "source_snapshot": {
            "repository": reference.UPSTREAM_REPOSITORY,
            "revision": reference.SOURCE_REVISION,
            "tree_object": reference.SOURCE_TREE_OBJECT,
            "tree_digest": reference.SOURCE_TREE_SHA256,
            "file_count": reference.SOURCE_FILE_COUNT,
            "license": reference.SOURCE_LICENSE,
            "license_sha256": reference.SOURCE_LICENSE_SHA256,
        },
        "status": "proposal_only_not_qualified",
        "task": reference.TASK,
        "upstream_blocker": blocker,
    }
    if not reference.finite_json(contract):
        raise SystemExit("contract contains a nonfinite value")
    return canonical_bytes(contract) + b"\n"


def write_report() -> str:
    payload = reference.report_bytes()
    report = reference.strict_json_loads(payload.decode("utf-8"))
    if not isinstance(report, dict):
        raise SystemExit("report root is not an object")
    REPORT_PATH.write_bytes(payload)
    SIDECAR_PATH.write_bytes(sidecar_bytes(payload))
    digest = sha256_bytes(payload)
    print("canonical_digest=" + sha256_bytes(canonical_bytes(report)))
    print("report_file_digest=" + digest)
    return digest


def write_sources() -> None:
    if not REPORT_PATH.is_file() or not SIDECAR_PATH.is_file():
        raise SystemExit("generate report.json and its sidecar first")
    payload = build_sources_bytes(REPORT_PATH.read_bytes(),
                                  SIDECAR_PATH.read_bytes())
    SOURCES_PATH.write_bytes(payload)
    print("sources_file_digest=" + sha256_bytes(payload))


def write_contract() -> None:
    if not REPORT_PATH.is_file() or not SIDECAR_PATH.is_file():
        raise SystemExit("generate report.json and its sidecar first")
    if not SOURCES_PATH.is_file():
        raise SystemExit("generate SOURCES.sha256 first")
    report_payload = REPORT_PATH.read_bytes()
    report = reference.strict_json_loads(report_payload.decode("utf-8"))
    payload = build_contract_bytes(
        report_payload, report, SIDECAR_PATH.read_bytes(),
        SOURCES_PATH.read_bytes())
    CONTRACT_PATH.write_bytes(payload)
    print("contract_file_digest=" + sha256_bytes(payload))


def verify_reproduction() -> int:
    report_payload = reference.report_bytes()
    report = reference.strict_json_loads(report_payload.decode("utf-8"))
    sidecar_payload = sidecar_bytes(report_payload)
    sources_payload = build_sources_bytes(report_payload, sidecar_payload)
    contract_payload = build_contract_bytes(
        report_payload, report, sidecar_payload, sources_payload)
    checks = (
        ("report.json", REPORT_PATH, report_payload),
        ("report.json.sha256", SIDECAR_PATH, sidecar_payload),
        ("SOURCES.sha256", SOURCES_PATH, sources_payload),
        ("contract.json", CONTRACT_PATH, contract_payload),
    )
    failed = 0
    for label, path, expected in checks:
        actual = path.read_bytes() if path.is_file() else b""
        if actual != expected:
            print("mismatch=" + label)
            failed += 1
    print("report_sha256=" + sha256_bytes(report_payload))
    print("sidecar_sha256=" + sha256_bytes(sidecar_payload))
    print("sources_sha256=" + sha256_bytes(sources_payload))
    print("contract_sha256=" + sha256_bytes(contract_payload))
    print("ok=" + ("1" if failed == 0 else "0"))
    return 0 if failed == 0 else 1


def stdout_report() -> None:
    sys.stdout.buffer.write(reference.report_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true",
                       help="regenerate every canonical artifact")
    group.add_argument("--report", action="store_true",
                       help="regenerate report.json and its SHA-256 sidecar")
    group.add_argument("--sources", action="store_true",
                       help="regenerate SOURCES.sha256")
    group.add_argument("--contract", action="store_true",
                       help="regenerate contract.json from frozen artifacts")
    group.add_argument("--stdout-report", action="store_true",
                       help="write canonical report bytes to stdout only")
    group.add_argument("--verify-repro", action="store_true",
                       help="regenerate all bytes in memory and compare")
    args = parser.parse_args()
    if args.all:
        write_report()
        write_sources()
        write_contract()
    elif args.report:
        write_report()
    elif args.sources:
        write_sources()
    elif args.contract:
        write_contract()
    elif args.stdout_report:
        stdout_report()
    else:
        return verify_reproduction()
    return 0


if __name__ == "__main__":
    sys.exit(main())
