# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic blocker evidence for SDK-SUPERPOWERED.

Standard library only. Superpowered is a commercial, sunsetting playback-speed
SDK candidate marked "Do not adopt" in pinned research. No exact licensed
source, SDK binary, model, runtime, corpus, or device evidence is present in
this worktree. This module records a fail-closed DEFER blocker package; it
never downloads, fabricates, registers, or executes Superpowered.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

TASK = "SDK-SUPERPOWERED"
COMPONENT = "superpowered"
TITLE = "Superpowered"
REPOSITORY = "audio-sdk"
MODE = "research-control"
PROFILE = "rate"
STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
BRANCH = "swarm/SDK-SUPERPOWERED"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
WRITE_SCOPE = "docs/task-evidence/superpowered/ only"
TASK_PREFIX = "docs/task-evidence/superpowered/"
CONTRACT_ID = "audio-sdk/superpowered-blocker/0.1"
REPORT_SCHEMA = "audio-sdk/superpowered-report/0.1"
DECLARATION_SCHEMA = "audio-sdk/superpowered-asset-declaration/0.1"

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]


def _find_audio_root() -> Path:
    override = os.environ.get("AUDIOML_ROOT") or os.environ.get("SOURCE_ROOT")
    candidates = []
    if override:
        candidates.append(Path(override))
    candidates.extend(HERE.parents)
    candidates.append(Path("/Users/htsakanyan/workspace/audio/audioml"))
    for c in candidates:
        if (c / "audio-benchmark-platform/plan/swarm/TASKS.json").is_file():
            return c.resolve()
    raise RuntimeError("audio_root_not_found")


AUDIO_ROOT = _find_audio_root()

PLAN_PINS = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
}
BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
}

LINKED_ROW_IDS = ("SDK-SUPERPOWERED", "SDK-FND-AUDIT", "SDK-FND-EVIDENCE")
STABLE_ROW_FIELDS = ("id", "repository", "mode", "component", "depends_on", "title", "evidence", "deliverable", "acceptance", "write_scope")

WORKSPACE_PROBES = (
    "cpp-library/pipeline-validation/superpowered",
    "data/checkouts/superpowered",
    "data/checkouts/SuperpoweredSDK",
    "data/models/superpowered",
    "data/reference/superpowered",
    "data/audio/superpowered",
    "third_party/superpowered",
    "third_party/SuperpoweredSDK",
)
WORKTREE_PROBES = (
    "adapters/superpowered",
    "schemas/providers/superpowered",
    "third_party/superpowered",
    "build/check-env/lib/python3.12/site-packages/superpowered",
)
HOME_PROBES = ("~/.cache/superpowered", "~/SuperpoweredSDK", "~/Library/Superpowered")

NON_CLAIMS = [
    "No Superpowered SDK, source, binary, license key, model, runtime, or documentation snapshot is present, downloaded, imported, linked, or executed.",
    "No real audio, corpus, device, playback timing, listening, or benchmark result is produced or claimed.",
    "No provider registration, descriptor, registry, default, public API/ABI, shared build, CI, board, handoff, ruleset, or main change is made.",
    "Source-reported research notes are context only and are not promoted to measured evidence.",
    "No network access or download is attempted; absent artifacts are not fabricated.",
    "No sibling rate/TSM evidence is inherited, pooled, or treated as a Superpowered result.",
]

RELEASE_GATES = [
    ("RG-01", "Exact licensed Superpowered SDK provenance", "Provide immutable licensed SDK/source/binary provenance, version, and distribution terms reviewed for the target use."),
    ("RG-02", "Rights and redistribution review", "Record reviewed commercial/license terms, attribution, redistribution, patent, and export constraints for any intended artifact."),
    ("RG-03", "Pinned runtime and task geometry", "Provide a locked runtime/build with exact platform, sample rate, channels, frame/hop, latency, and reset/drain semantics."),
    ("RG-04", "API/ABI compatibility intake", "Define a versioned optional adapter boundary that preserves installed v0 behavior and does not change defaults or shared ABI."),
    ("RG-05", "Rate-profile deterministic evidence", "Run Rate-profile controls on pinned inputs with source/output mapping, duration, pitch, transients, buffering, and invalid/nonfinite/adverse rejection."),
    ("RG-06", "Matched real-corpus and listening evidence", "Provide rights-cleared matched speech/music cohorts with same-condition controls and authorized listening or labeled screens."),
    ("RG-07", "Target-device timing and availability", "Measure paced target-device playback workload with fill/flush, deadlines, CPU, memory, underruns, and availability telemetry."),
    ("RG-08", "Independent review and release decision", "Obtain exact-head independent review, hosted CI, and explicit release approval; missing/adverse results remain non-qualifying."),
]

BLOCKERS = [
    ("BLK-01", "RG-01", "No exact licensed Superpowered SDK/source/binary provenance or immutable version is present in this worktree."),
    ("BLK-02", "RG-02", "No reviewed commercial/license/redistribution decision for Superpowered is staged; candidate is marked do-not-adopt and sunsetting."),
    ("BLK-03", "RG-03", "No pinned runtime, build, or verified task geometry for Superpowered is present."),
    ("BLK-04", "RG-05", "No deterministic Rate-profile execution, controls, or output validity evidence exists for Superpowered."),
    ("BLK-05", "RG-06", "No rights-cleared matched corpus, listening, or labeled quality screen exists."),
    ("BLK-06", "RG-07", "No target-device pacing, deadline, CPU/memory, or availability measurement exists."),
]


class ReferenceError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def canonical_bytes(obj: Any) -> bytes:
    return (canonical_json(obj) + "\n").encode("utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _reject_const(x: str) -> Any:
    raise ReferenceError("nonfinite_constant:" + x)


def _reject_dupes(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for k, v in pairs:
        if k in obj:
            raise ReferenceError("duplicate_key:" + k)
        obj[k] = v
    return obj


def _walk_no_float(x: Any) -> None:
    if isinstance(x, float):
        raise ReferenceError("float_not_allowed")
    if isinstance(x, dict):
        for v in x.values():
            _walk_no_float(v)
    elif isinstance(x, list):
        for v in x:
            _walk_no_float(v)


def loads_strict(text: str) -> Any:
    if text.startswith("\ufeff"):
        raise ReferenceError("bom_not_allowed")
    decoder = json.JSONDecoder(parse_constant=_reject_const, object_pairs_hook=_reject_dupes)
    obj, end = decoder.raw_decode(text)
    if text[end:].strip():
        raise ReferenceError("trailing_data")
    _walk_no_float(obj)
    return obj


def load_strict_json(path: Path) -> Any:
    try:
        return loads_strict(path.read_text(encoding="utf-8"))
    except ReferenceError as e:
        raise ReferenceError(str(e) + ":" + path.as_posix()) from e


def resolve_source(rel_path: str) -> Path:
    return (AUDIO_ROOT / rel_path).resolve()


def resolve_worktree(rel_path: str) -> Path:
    return (WORKTREE / rel_path).resolve()


def linked_row_projection() -> dict[str, Any]:
    tasks = load_json(resolve_source("audio-benchmark-platform/plan/swarm/TASKS.json"))
    for t in tasks.get("tasks", []):
        if t.get("id") == TASK:
            return {k: t[k] for k in STABLE_ROW_FIELDS if k in t}
    raise ReferenceError("task_row_not_found")


def linked_dep_row(task_id: str) -> dict[str, Any]:
    tasks = load_json(resolve_source("audio-benchmark-platform/plan/swarm/TASKS.json"))
    for t in tasks.get("tasks", []):
        if t.get("id") == task_id:
            keep = ("id", "repository", "mode", "title", "depends_on")
            return {k: t[k] for k in keep if k in t}
    raise ReferenceError("dep_row_not_found:" + task_id)


def absence_probes() -> list[dict[str, Any]]:
    probes = []
    for p in WORKSPACE_PROBES:
        probes.append({"path": p, "root": "audio_root", "exists": resolve_source(p).exists()})
    for p in WORKTREE_PROBES:
        probes.append({"path": p, "root": "worktree", "exists": resolve_worktree(p).exists()})
    for p in HOME_PROBES:
        probes.append({"path": p, "root": "home", "exists": Path(os.path.expanduser(p)).exists()})
    return probes


def actual_source_pins() -> dict[str, str]:
    pins = {p: sha256_file(resolve_source(p)) for p in PLAN_PINS}
    row = linked_row_projection()
    pins["linked-row:SDK-SUPERPOWERED"] = sha256_bytes(canonical_bytes(row).rstrip(b"\n"))
    for dep in LINKED_ROW_IDS[1:]:
        pins[f"linked-row:{dep}"] = sha256_bytes(canonical_bytes(linked_dep_row(dep)).rstrip(b"\n"))
    return pins


def actual_boundary_pins() -> dict[str, str]:
    return {p: sha256_file(resolve_worktree(p)) for p in BOUNDARY_PINS}


def build_contract() -> dict[str, Any]:
    row = linked_row_projection()
    return {
        "schema": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "write_scope": WRITE_SCOPE,
        "status": STATUS,
        "decision": DECISION,
        "qualification": {"status": QUALIFICATION_STATUS, "qualified": False, "not_qualified": True},
        "proposal_only": True,
        "incomplete": True,
        "linked_row_identity": {
            "task": TASK,
            "stable_fields": list(STABLE_ROW_FIELDS),
            "projection": row,
            "projection_sha256": sha256_bytes(canonical_bytes(row).rstrip(b"\n")),
            "mutable_board_hash_used": False,
        },
        "dependencies": [linked_dep_row(d) for d in LINKED_ROW_IDS[1:]],
        "source_pins": actual_source_pins(),
        "boundary_pins": actual_boundary_pins(),
        "absence_probes": absence_probes(),
        "release_gates": [
            {"id": gid, "title": title, "status": "blocked", "qualifies": False, "reopen_condition": reopen}
            for gid, title, reopen in RELEASE_GATES
        ],
        "blockers": [
            {"id": bid, "gate": gate, "status": "open", "qualifies": False, "summary": summary}
            for bid, gate, summary in BLOCKERS
        ],
        "non_claims": NON_CLAIMS,
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    probes = contract["absence_probes"]
    present = [p for p in probes if p["exists"]]
    return {
        "schema": REPORT_SCHEMA,
        "task": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "decision": DECISION,
        "proposal_only": True,
        "incomplete": True,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "not_qualified": True,
            "reason": "No exact licensed Superpowered source/binary/runtime, no reviewed rights, no deterministic/real/device evidence; candidate marked do-not-adopt and sunsetting.",
        },
        "linked_row_identity": contract["linked_row_identity"],
        "dependencies": contract["dependencies"],
        "source_pins": contract["source_pins"],
        "boundary_pins": contract["boundary_pins"],
        "absence_summary": {
            "probe_count": len(probes),
            "present_count": len(present),
            "all_absent": len(present) == 0,
            "present_paths": [p["path"] for p in present],
            "probes": probes,
        },
        "evidence": {
            "inventory_finding": "cpp-library/pipeline-validation/playback-speed-candidates.md marks Superpowered as 'Do not adopt' (commercial, sunsetting).",
            "source_reported_only": True,
            "measured_result_present": False,
            "runtime_present": False,
            "licensed_source_present": False,
            "weights_present": False,
            "real_corpus_present": False,
            "device_timing_present": False,
        },
        "release_gates": contract["release_gates"],
        "blockers": contract["blockers"],
        "non_claims": NON_CLAIMS,
    }


def report_digest(report: dict[str, Any] | None = None) -> str:
    obj = report if report is not None else build_report()
    return sha256_bytes(canonical_bytes(obj))


def sources_manifest() -> str:
    lines = []
    for p in sorted(HERE.iterdir()):
        if p.is_file() and p.name != "SOURCES.sha256":
            lines.append(f"{sha256_file(p)}  {p.name}")
    for k, v in sorted(actual_source_pins().items()):
        lines.append(f"{v}  source:{k}")
    for k, v in sorted(actual_boundary_pins().items()):
        lines.append(f"{v}  boundary:{k}")
    return "\n".join(lines) + "\n"
