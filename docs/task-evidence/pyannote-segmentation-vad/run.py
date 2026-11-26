# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate or check the deterministic pyannote segmentation/VAD evidence.

Run ``python3 run.py all`` from this directory. No network, media, runtime,
board mutation or handoff write occurs. The mutable full board file is never
hashed; only stable linked-row identity is projected into the report.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Dict

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

REPORT = "report.json"
SIDECAR = "report.json.sha256"
CONTRACT = "contract.json"
SOURCES = "SOURCES.sha256"

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
LICENSE_SIDECARS = {
    CONTRACT: "contract.json.license",
    REPORT: "report.json.license",
    SIDECAR: "report.json.sha256.license",
    SOURCES: "SOURCES.sha256.license",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def report_bytes() -> bytes:
    return reference.canonical_report_bytes(reference.build_report())


def sidecar_bytes(digest: str) -> bytes:
    return (digest + "  report.json\n").encode("ascii")


def _local_bytes(name: str, report: bytes | None = None) -> bytes:
    if name == REPORT:
        return report if report is not None else report_bytes()
    if name == SIDECAR:
        data = report if report is not None else report_bytes()
        return sidecar_bytes(sha256(data))
    return (HERE / name).read_bytes()


def build_contract() -> bytes:
    report = report_bytes()
    report_digest = sha256(report)
    artifact_pins: Dict[str, str] = {}
    for name in sorted(LOCAL_FILES):
        if name in CONTRACT_EXCLUDED:
            continue
        artifact_pins[name] = sha256(_local_bytes(name, report))

    identity = reference.task_row_identity()
    contract = {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": reference.CONTRACT_SCHEMA_ID,
        "task_id": reference.TASK,
        "title": reference.TITLE,
        "component": reference.COMPONENT,
        "category_id": reference.CATEGORY_ID,
        "branch": reference.BRANCH,
        "base_commit": reference.BASE_COMMIT,
        "worktree": reference.CLAIM_WORKTREE,
        "reviewer": reference.REVIEWER,
        "profile": reference.PROFILE,
        "mode": reference.MODE,
        "status": reference.STATUS,
        "decision": reference.DECISION,
        "qualification_status": reference.QUALIFICATION,
        "evidence_status": reference.EVIDENCE_STATUS,
        "defer_before": reference.DEFER_BEFORE,
        "proposal_only": True,
        "task_row_identity": identity,
        "qualification": {
            "decision": reference.DECISION,
            "status": reference.QUALIFICATION,
            "qualification_status": reference.QUALIFICATION,
            "candidate_qualified": False,
            "proposal_only": True,
            "implementation_present": False,
            "runtime_invoked": False,
            "parity_present": False,
            "corpus_present": False,
            "release_qualification_present": False,
            "no_missing_result_qualifies_candidate": True,
            "synthetic_control_is_not_candidate_evidence": True,
        },
        "pyannote_implementation_contract": {
            "contract_id": "audio-sdk/pyannote-segmentation-vad/offline-annotation-adapter/0.1",
            "variant": reference.REQUIRED_VARIANT,
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_absolute_paths_sha256_revision_geometry_and_variant_only; do_not_import_build_link_or_execute_any_runtime",
            "qualification": reference.QUALIFICATION,
            "required_fields": list(reference.MANIFEST_FIELDS),
            "required_geometry": {
                "sample_rate_hz": reference.SAMPLE_RATE_HZ,
                "channels": reference.CHANNELS,
                "frame_samples": reference.SDK_FRAME_SAMPLES,
                "task_geometry": ["vad", "segmentation", "vad+segmentation"],
                "threshold": "canonical decimal string > 0",
                "onset_hangover_frames": "integer >= 0",
                "status": "unestablished_until_exact_runtime_pinned",
            },
            "required_source_revision": None,
            "revision_pin_available": False,
            "note": "A structurally valid manifest is not qualification. Every required file must be absolute, hash-pinned and reviewed; this package supplies no approval.",
        },
        "scope": dict(reference.SCOPE),
        "boundary": dict(reference.BOUNDARY),
        "artifact_pins": artifact_pins,
        "source_pins": dict(reference.SOURCE_PINS),
        "boundary_pins": dict(reference.BOUNDARY_PINS),
        "mutable_provenance": {
            "gate": False,
            "path": reference.BOARD_PATH,
            "note": "The mutable full board file is never hashed. Only stable linked-row identity is gated in task_row_identity.",
        },
        "release_gates": [gate["id"] for gate in reference._gate_rows()],
        "license_sidecars": dict(LICENSE_SIDECARS),
        "reproduction": {
            "all": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "order": "report.json -> report.json.sha256 -> contract.json -> SOURCES.sha256",
        },
    }
    if contract["decision"] != reference.DECISION:
        raise ValueError("contract decision changed")
    if contract["qualification"]["candidate_qualified"] is not False:
        raise ValueError("contract qualification claimed")
    if reference.BOARD_PATH in contract["source_pins"] or reference.BOARD_PATH in contract["boundary_pins"]:
        raise ValueError("contract pins the mutable board file")
    if len(contract["release_gates"]) != 8:
        raise ValueError("contract gate count changed")
    return reference.canonical_bytes(contract)


def sources_bytes() -> bytes:
    report = report_bytes()
    lines = []
    for name in sorted(LOCAL_FILES):
        if name in SOURCES_EXCLUDED:
            continue
        lines.append(f"{sha256(_local_bytes(name, report))}  local:{name}")
    for rel in sorted(reference.SOURCE_PINS):
        lines.append(f"{reference.SOURCE_PINS[rel]}  source:{rel}")
    for rel in sorted(reference.BOUNDARY_PINS):
        lines.append(f"{reference.BOUNDARY_PINS[rel]}  worktree:{rel}")
    return ("\n".join(lines) + "\n").encode("ascii")


def write_atomic(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def cmd_report() -> str:
    data = report_bytes()
    digest = sha256(data)
    write_atomic(HERE / REPORT, data)
    write_atomic(HERE / SIDECAR, sidecar_bytes(digest))
    return digest


def cmd_contract() -> None:
    write_atomic(HERE / CONTRACT, build_contract())


def cmd_sources() -> None:
    write_atomic(HERE / SOURCES, sources_bytes())


def cmd_all() -> str:
    digest = cmd_report()
    cmd_contract()
    cmd_sources()
    return digest


def cmd_check() -> int:
    expected_report = report_bytes()
    expected_digest = sha256(expected_report)
    expected_sidecar = sidecar_bytes(expected_digest)
    expected_contract = build_contract()
    expected_sources = sources_bytes()
    ok = True
    for name, expected in (
        (REPORT, expected_report),
        (SIDECAR, expected_sidecar),
        (CONTRACT, expected_contract),
        (SOURCES, expected_sources),
    ):
        actual = (HERE / name).read_bytes()
        if actual != expected:
            print(f"MISMATCH {name}", file=sys.stderr)
            ok = False
    print(expected_digest if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["report", "contract", "sources", "all", "check"])
    args = parser.parse_args()
    if args.command == "report":
        print(cmd_report())
    elif args.command == "contract":
        cmd_report()
        cmd_contract()
    elif args.command == "sources":
        cmd_all()
    elif args.command == "all":
        print(cmd_all())
    elif args.command == "check":
        return cmd_check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
