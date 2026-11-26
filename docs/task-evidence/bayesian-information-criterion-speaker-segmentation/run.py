# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate or check the deterministic BIC speaker-segmentation evidence.

Run ``python3.12 run.py all`` from this directory. No network, media, runtime,
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
        "bic_implementation_contract": {
            "contract_id": "audio-sdk/bic-speaker-segmentation/offline-annotation-adapter/0.1",
            "variant": reference.REQUIRED_VARIANT,
            "absent_behavior": "reject_before_processing",
            "present_behavior": (
                "validate_absolute_paths_sha256_revision_geometry_and_variant_only; "
                "do_not_import_build_link_or_execute_any_segmenter"
            ),
            "qualification": reference.QUALIFICATION,
            "required_fields": list(reference.MANIFEST_FIELDS),
            "required_geometry": {
                "sample_rate_hz": reference.CONTROL_SAMPLE_RATE_HZ,
                "channels": reference.CONTROL_CHANNELS,
                "frame_samples": reference.SDK_FRAME_SAMPLES,
                "feature_dim": None,
                "window_frames": None,
                "hop_frames": None,
                "lookahead_frames": None,
                "penalty_weight": None,
                "threshold": None,
                "min_segment_frames": None,
                "status": "unestablished",
            },
            "required_source_revision": None,
            "revision_pin_available": False,
            "note": (
                "A structurally valid manifest is not a qualification. Every "
                "required file must be absolute, hash-pinned and reviewed; "
                "this package supplies no approval."
            ),
        },
        "caller_asset_contract": {
            "contract_id": "audio-sdk/bic-speaker-segmentation/caller-supplied-asset/0.1",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_absolute_paths_sha256_revision_geometry_and_variant_only",
            "required_fields": list(reference.MANIFEST_FIELDS),
            "required_geometry": {
                "sample_rate_hz": reference.CONTROL_SAMPLE_RATE_HZ,
                "channels": reference.CONTROL_CHANNELS,
                "frame_samples": reference.SDK_FRAME_SAMPLES,
                "feature_dim": None,
                "window_frames": None,
                "hop_frames": None,
                "lookahead_frames": None,
                "penalty_weight": None,
                "threshold": None,
                "min_segment_frames": None,
                "status": "unestablished",
            },
            "required_variant": reference.REQUIRED_VARIANT,
            "required_source_revision": None,
            "revision_pin_available": False,
            "qualification": reference.QUALIFICATION,
            "note": (
                "The manifest names the exact source, runtime, licence, rights, "
                "corpus, adapter config, parity vector and benchmark record. "
                "No such manifest is supplied here."
            ),
        },
        "bic_reference_formula": {
            "formula_id": reference.BIC_FORMULA_ID,
            "formula": (
                "D = N*ln|Sigma_pooled| - N1*ln|Sigma_left| - "
                "N2*ln|Sigma_right| - lambda*0.5*(d + d*(d+1)/2)*ln(N)"
            ),
            "sign_convention": "D > threshold favours a change point",
            "selection_policy": reference.BIC_SELECTION_POLICY,
            "implementation_origin": "task-local reference arithmetic, not an upstream implementation",
            "upstream_parity_target": None,
            "qualifies_candidate": False,
        },
        "scope": dict(reference.SCOPE),
        "boundary": dict(reference.BOUNDARY),
        "artifact_pins": artifact_pins,
        "source_pins": dict(reference.SOURCE_PINS),
        "boundary_pins": dict(reference.BOUNDARY_PINS),
        "mutable_provenance": {
            "gate": False,
            "path": reference.BOARD_PATH,
            "note": (
                "The mutable full board file is never hashed. Only stable "
                "linked-row identity is gated in task_row_identity."
            ),
        },
        "release_gates": [gate["id"] for gate in reference._gate_rows()],
        "license_sidecars": dict(LICENSE_SIDECARS),
        "reproduction": {
            "all": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            "order": "report.json -> report.json.sha256 -> contract.json -> SOURCES.sha256",
        },
    }
    if contract["decision"] != reference.DECISION:
        raise ValueError("contract decision changed")
    if contract["qualification"]["candidate_qualified"] is not False:
        raise ValueError("contract qualification claimed")
    if reference.BOARD_PATH in contract["source_pins"]:
        raise ValueError("contract pins the mutable board file")
    if len(contract["release_gates"]) != 8:
        raise ValueError("contract gate count changed")
    return reference.canonical_bytes(contract) + b"\n"


def sources_bytes() -> bytes:
    rows = []
    for name in sorted(LOCAL_FILES):
        if name in SOURCES_EXCLUDED:
            continue
        rows.append((sha256(_local_bytes(name)), "local:" + name))
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        rows.append((digest, "source:" + path))
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        rows.append((digest, "worktree:" + path))
    rows.sort(key=lambda row: row[1])
    return "".join("%s  %s\n" % row for row in rows).encode("ascii")


def write_report(out: Path) -> str:
    data = report_bytes()
    digest = sha256(data)
    out.mkdir(parents=True, exist_ok=True)
    (out / REPORT).write_bytes(data)
    (out / SIDECAR).write_bytes(sidecar_bytes(digest))
    return digest


def write_contract(out: Path) -> str:
    data = build_contract()
    out.mkdir(parents=True, exist_ok=True)
    (out / CONTRACT).write_bytes(data)
    return sha256(data)


def write_sources() -> str:
    data = sources_bytes()
    (HERE / SOURCES).write_bytes(data)
    return sha256(data)


def check_artifacts(out: Path) -> bool:
    report = report_bytes()
    digest = sha256(report)
    contract = build_contract()
    return (
        (out / REPORT).is_file()
        and (out / REPORT).read_bytes() == report
        and (out / SIDECAR).is_file()
        and (out / SIDECAR).read_bytes() == sidecar_bytes(digest)
        and (out / CONTRACT).is_file()
        and (out / CONTRACT).read_bytes() == contract
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact",
        nargs="?",
        default="all",
        choices=("all", "report", "sha256", "contract", "sources"),
    )
    parser.add_argument("--out", type=Path, default=HERE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    out = args.out.resolve()

    if args.artifact in ("report", "sha256", "contract", "all"):
        if args.check:
            ok = check_artifacts(out)
            print(
                "check=%s report_sha256=%s contract_sha256=%s"
                % (
                    "ok" if ok else "failed",
                    sha256(report_bytes()),
                    sha256(build_contract()),
                )
            )
            if not ok:
                return 1
        else:
            if args.artifact in ("report", "all"):
                digest = write_report(out)
                print("report.json " + digest)
            if args.artifact in ("sha256",):
                digest = sha256(report_bytes())
                out.mkdir(parents=True, exist_ok=True)
                (out / SIDECAR).write_bytes(sidecar_bytes(digest))
                print("report.json.sha256 " + digest)
            if args.artifact in ("contract", "all"):
                digest = write_contract(out)
                print("contract.json " + digest)

    if args.artifact in ("sources", "all"):
        if out != HERE:
            parser.error("sources may only target this package directory")
        digest = write_sources()
        print("SOURCES.sha256 " + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
