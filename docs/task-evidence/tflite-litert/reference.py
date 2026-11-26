# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic blocker evidence for SDK-TFLITE-LITERT.

Standard library only. TFLite / LiteRT is a tooling/runtime candidate with no
exact pinned source, runtime, model, weights, rights-cleared matched evidence,
or qualified execution present for this task in this worktree. This module
records a fail-closed DEFER blocker package; it never downloads, fabricates,
registers, or executes LiteRT/TFLite.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

TASK = "SDK-TFLITE-LITERT"
COMPONENT = "tflite-litert"
TITLE = "TFLite / LiteRT"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "tool"
STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
BRANCH = "swarm/SDK-TFLITE-LITERT"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
WRITE_SCOPE = "docs/task-evidence/tflite-litert/ only"
TASK_PREFIX = "docs/task-evidence/tflite-litert/"
CONTRACT_ID = "audio-sdk/tflite-litert-blocker/0.1"
REPORT_SCHEMA = "audio-sdk/tflite-litert-report/0.1"

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
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
}
BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
}

LINKED_ROW_IDS = ("SDK-TFLITE-LITERT", "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
STABLE_ROW_FIELDS = ("id", "repository", "mode", "component", "depends_on", "title", "evidence", "deliverable", "acceptance", "write_scope")

WORKSPACE_PROBES = (
    "data/checkouts/tflite",
    "data/checkouts/litert",
    "data/checkouts/tensorflow-lite",
    "data/checkouts/LiteRT",
    "data/models/tflite",
    "data/models/litert",
    "data/reference/tflite-litert",
    "third_party/tflite",
    "third_party/litert",
    "research/tflite-litert",
)
WORKTREE_PROBES = (
    "adapters/tflite-litert",
    "schemas/providers/tflite-litert",
    "third_party/tflite",
    "third_party/litert",
    "tools/tflite-litert",
)
HOME_PROBES = ("~/.cache/tflite", "~/.cache/litert", "~/Library/tflite", "~/Library/litert")

NON_CLAIMS = [
    "No TFLite/LiteRT source, runtime, delegate, model, weights, binary, or documentation snapshot is present, downloaded, imported, linked, or executed.",
    "No real audio, corpus, device, listening, benchmark, signature-smoke, or parity result is produced or claimed.",
    "No provider registration, descriptor, registry, default, public API/ABI, shared build, CI, board, handoff, ruleset, or main change is made.",
    "Source-reported research notes are context only and are not promoted to measured evidence.",
    "No network access or download is attempted; absent artifacts are not fabricated.",
    "No sibling TFLite/LiteRT evidence is inherited, pooled, or treated as this task's result.",
]

RELEASE_GATES = [
    ("RG-01", "Exact source/runtime provenance", "Provide immutable TFLite/LiteRT source/runtime revision, build inputs, and versioned delegate/runtime provenance."),
    ("RG-02", "Rights and redistribution review", "Record reviewed license, attribution, redistribution, patent/export, and model/runtime terms for any intended artifact."),
    ("RG-03", "Pinned task geometry and assets", "Provide exact model/checkpoint/delegate geometry, sample rate/channels/frame/hop/reset/drain semantics, and immutable asset digests."),
    ("RG-04", "API/ABI compatibility intake", "Define a versioned optional adapter/tool boundary that preserves installed v0 behavior and does not change defaults or shared ABI."),
    ("RG-05", "Deterministic tool/runtime smoke", "Run deterministic signature smoke and adverse/missing/invalid/nonfinite rejection on pinned local assets without hidden network or host mutation."),
    ("RG-06", "Matched task evidence and parity", "Provide rights-cleared matched inputs and reference-backend parity/full-checkpoint evidence for the claimed task geometry."),
    ("RG-07", "Target execution and availability", "Measure paced target-device/runtime CPU, memory, deadline, availability, and delegate behavior for the exact configuration."),
    ("RG-08", "Independent review and release decision", "Obtain exact-head independent review, hosted CI, and explicit release approval; missing/adverse results remain non-qualifying."),
]

BLOCKERS = [
    ("BLK-01", "RG-01", "No exact pinned TFLite/LiteRT source/runtime revision or immutable build provenance is present in this worktree."),
    ("BLK-02", "RG-02", "No reviewed license/redistribution/patent/export decision for TFLite/LiteRT runtime, delegates, or candidate models is staged."),
    ("BLK-03", "RG-03", "No exact model, weights, delegate, task geometry, or immutable asset digest is present for a qualified claim."),
    ("BLK-04", "RG-05", "No deterministic native signature smoke, invalid/nonfinite rejection, or reproducible runtime execution evidence exists."),
    ("BLK-05", "RG-06", "No rights-cleared matched corpus or reference-backend parity/full-checkpoint evidence exists."),
    ("BLK-06", "RG-07", "No target-device timing, CPU/memory, availability, or delegate measurement exists."),
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
    pins["linked-row:" + TASK] = sha256_bytes(canonical_bytes(row).rstrip(b"\n"))
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
            "reason": "No exact pinned TFLite/LiteRT runtime/source, no reviewed rights, no deterministic/real/device evidence; generic runtime presence is not a qualified task result.",
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
            "inventory_finding": "TFLite/LiteRT is a tooling/runtime candidate; exact task geometry, pinned runtime/delegates, rights-reviewed assets, and matched parity/timing evidence are required before qualification.",
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
