# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Canonical generator for the SDK-NVIDIA-RE-USE evidence package.

The package is proposal evidence only. No NVIDIA RE-USE weights, runtime,
license text, corpus or candidate output is present or reconstructed.
Regeneration is repeated three times and must be byte-identical.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Mapping

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
SOURCES_PATH = HERE / "SOURCES.sha256"
CONTRACT_PATH = HERE / "contract.json"
REGEN_REPEATS = 3

MANIFEST_FILES = (
    "README.md",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
CONTRACT_ARTIFACTS = MANIFEST_FILES + ("SOURCES.sha256",)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return reference.canonical_bytes(value)


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def _file_payload(name: str) -> bytes:
    path = HERE / name
    if not path.is_file():
        raise SystemExit("missing package artifact: " + name)
    return path.read_bytes()


def build_sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines: List[str] = [
        "# SHA-256 pins for SDK-NVIDIA-RE-USE task-local evidence; source: paths are workspace-relative, other paths are SDK-worktree-relative.",
        "# The mutable full plan/swarm/TASKS.json is deliberately not pinned; only the stable linked-row identity is projected.",
        "# contract.json is excluded because it pins this manifest; no weights, runtime, license text or audio file is present to pin.",
    ]
    for path, digest in sorted(reference.SOURCE_PINS.items()):
        target = reference.WORKSPACE / path
        if not target.is_file():
            raise SystemExit("missing source pin target: " + path)
        if sha256_file(target) != digest:
            raise SystemExit("source pin changed: " + path)
        lines.append(digest + "  source:" + path)
    for path, digest in sorted(reference.BOUNDARY_PINS.items()):
        target = reference.SDK_ROOT / path
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


def build_contract_bytes(report_payload: bytes, report: Mapping[str, Any], sidecar_payload: bytes, sources_payload: bytes) -> bytes:
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
    contract = {
        "schema_id": reference.CONTRACT_SCHEMA_ID,
        "contract_version": "0.1",
        "task": reference.TASK,
        "component": reference.COMPONENT,
        "mode": reference.MODE,
        "branch": reference.BRANCH,
        "base_commit": reference.BASE_COMMIT,
        "verification_profile": reference.VERIFICATION_PROFILE,
        "status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "incomplete": True,
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "qualification": reference.qualification(),
        "comparison_status": "blocked_artifact_runtime_license_rights_and_fixture_absent",
        "upstream_blocker": dict(reference.UPSTREAM_BLOCKER),
        "required_artifacts": [dict(row) for row in reference.REQUIRED_ARTIFACTS],
        "missing_artifacts": [row["artifact"] for row in reference.REQUIRED_ARTIFACTS if row["status"] == "absent"],
        "artifact_requirement": {
            "status": "unresolved",
            "required_source": "The exact NVIDIA Real-time RE-USE model revision and community Swift/MLX port revision, with path, byte count, SHA-256 and provenance.",
            "required_weights": "The immutable model.safetensors (or approved equivalent) addressed by path, byte count and SHA-256.",
            "required_runtime": "A compatible pinned Swift/MLX or approved runtime, built CLI/binary with SHA-256, lock/build record and host/toolchain parity evidence.",
            "required_rights": "The exact NSCLv1 license text/version and a written decision covering research, redistribution, product use, derived output and attribution.",
            "required_geometry": "Verified operating point, sample rate, channels, frame/hop, state, lookahead and content delay.",
            "required_fixture": "A rights-cleared task-matched cohort with pinned SI-SDR/STOI scorer and held-out cases.",
            "unresolved_fields": [
                "model_revision", "model_sha256", "model_byte_count", "weights_path",
                "license_text_sha256", "license_version", "written_use_decision",
                "runtime_version", "cli_sha256", "build_lock_digest", "host_toolchain",
                "sample_rate_hz", "channels", "frame_samples", "hop_samples", "lookahead_samples",
                "content_delay_samples", "cohort_rights", "evaluation_overlap",
            ],
        },
        "asset_contract": dict(reference.ASSET_CONTRACT),
        "geometry": report["geometry"],
        "external_boundary": dict(reference.EXTERNAL_BOUNDARY),
        "boundary": reference.boundary(),
        "profile": report["profile"],
        "invariants": list(reference.INVARIANTS),
        "non_claims": list(reference.NON_CLAIMS),
        "source_evidence_statements": reference.source_evidence_statements(),
        "release_gates": [dict(gate) for gate in reference.GATES],
        "remaining_gates": [gate["id"] for gate in reference.GATES],
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_link_fields": list(reference.LINK_FIELDS),
        "board_mutable_fields_excluded": list(reference.MUTABLE_FIELDS_EXCLUDED),
        "board_full_file_hashed": False,
        "source_pins": dict(reference.SOURCE_PINS),
        "boundary_pins": dict(reference.BOUNDARY_PINS),
        "artifact_pins": pins,
        "canonical_report": {
            "canonical_digest": sha256_bytes(canonical_bytes(report)),
            "file_sha256": sha256_bytes(report_payload),
            "sidecar_sha256": sha256_bytes(sidecar_payload),
            "format": "canonical JSON: sort_keys=True, compact separators, allow_nan=False, exactly one trailing newline",
        },
        "generated_by": "run.py --all",
    }
    if not reference.finite_json(contract):
        raise SystemExit("contract contains a nonfinite value")
    return canonical_bytes(contract) + b"\n"


def build_bundle() -> Dict[str, bytes]:
    report_payload = reference.report_bytes()
    report = reference.strict_json_loads(report_payload.decode("utf-8"))
    if not isinstance(report, dict):
        raise SystemExit("report root is not an object")
    sidecar_payload = sidecar_bytes(report_payload)
    sources_payload = build_sources_bytes(report_payload, sidecar_payload)
    contract_payload = build_contract_bytes(report_payload, report, sidecar_payload, sources_payload)
    return {
        "report.json": report_payload,
        "report.json.sha256": sidecar_payload,
        "SOURCES.sha256": sources_payload,
        "contract.json": contract_payload,
    }


def write_bundle(bundle: Mapping[str, bytes]) -> None:
    for name, payload in bundle.items():
        (HERE / name).write_bytes(payload)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--report", action="store_true")
    group.add_argument("--sources", action="store_true")
    group.add_argument("--contract", action="store_true")
    group.add_argument("--stdout-report", action="store_true")
    group.add_argument("--verify-repro", action="store_true")
    args = parser.parse_args(argv)

    if args.stdout_report:
        sys.stdout.buffer.write(reference.report_bytes())
        return 0

    if args.verify_repro:
        bundle = build_bundle()
        errors = [name for name, payload in bundle.items() if not (HERE / name).is_file() or (HERE / name).read_bytes() != payload]
        for name in errors:
            print("mismatch=" + name)
        print("report_sha256=" + sha256_bytes(bundle["report.json"]))
        print("sidecar_sha256=" + sha256_bytes(bundle["report.json.sha256"]))
        print("sources_sha256=" + sha256_bytes(bundle["SOURCES.sha256"]))
        print("contract_sha256=" + sha256_bytes(bundle["contract.json"]))
        print("ok=" + ("1" if not errors else "0"))
        return 0 if not errors else 1

    if args.report:
        bundle = build_bundle()
        selected = {name: bundle[name] for name in ("report.json", "report.json.sha256")}
    elif args.sources:
        bundle = build_bundle()
        selected = {"SOURCES.sha256": bundle["SOURCES.sha256"]}
    elif args.contract:
        bundle = build_bundle()
        selected = {"contract.json": bundle["contract.json"]}
    else:
        selected = dict(build_bundle())

    observed: List[Dict[str, str]] = []
    for _ in range(REGEN_REPEATS):
        write_bundle(selected)
        observed.append({name: sha256_bytes((HERE / name).read_bytes()) for name in sorted(selected)})
    if len({json.dumps(item, sort_keys=True) for item in observed}) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    print("repeat=" + str(REGEN_REPEATS) + " byte_identical=true")
    for name in sorted(observed[0]):
        print(name + "_sha256=" + observed[0][name])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
