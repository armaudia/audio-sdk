# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic blocker evidence for SDK-VOICEFIXER.

Standard library only. VoiceFixer has no exact pinned licensed source,
checkpoint/weights, pinned runtime, rights-cleared matched cohort, or
qualified Restoration execution evidence present for this task in this
worktree. This module records a fail-closed DEFER blocker package; it never
downloads, fabricates, registers, or executes VoiceFixer.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

TASK = "SDK-VOICEFIXER"
COMPONENT = "voicefixer"
TITLE = "VoiceFixer"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "restoration"
STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
BRANCH = "swarm/SDK-VOICEFIXER"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
WRITE_SCOPE = "docs/task-evidence/voicefixer/ only"
TASK_PREFIX = "docs/task-evidence/voicefixer/"
CONTRACT_ID = "audio-sdk/voicefixer-blocker/0.1"
REPORT_SCHEMA = "audio-sdk/voicefixer-report/0.1"

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

# Pinned read-only sources. Full mutable TASKS.json is intentionally NOT pinned;
# only stable linked-row projections are hashed in source_pins.
PLAN_PINS = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
}
BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
}

LINKED_ROW_IDS = ("SDK-VOICEFIXER", "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
STABLE_ROW_FIELDS = ("id", "repository", "mode", "component", "depends_on", "title", "evidence", "deliverable", "acceptance", "write_scope")

WORKSPACE_PROBES = (
    "data/checkouts/voicefixer",
    "data/checkouts/VoiceFixer",
    "data/models/voicefixer",
    "data/models/VoiceFixer",
    "data/reference/voicefixer",
    "third_party/voicefixer",
    "research/voicefixer",
    "research/voice-enhancement-20261101/repos/voicefixer",
    "research/voice-enhancement-20261101/repos/VoiceFixer",
    "research/voice-enhancement-20261101/models/voicefixer",
)
WORKTREE_PROBES = (
    "adapters/voicefixer",
    "schemas/providers/voicefixer",
    "third_party/voicefixer",
    "tools/voicefixer",
)
HOME_PROBES = ("~/.cache/voicefixer", "~/.cache/huggingface/hub/models--*voicefixer*", "~/Library/voicefixer")

NON_CLAIMS = [
    "No VoiceFixer source, checkpoint, weights, runtime, config, or restored audio is present, downloaded, imported, linked, or executed.",
    "No real corpus, rights-cleared degraded/clean cohort, listening, device timing, benchmark, or release result is produced or claimed.",
    "No provider registration, descriptor, registry, default, public API/ABI, shared build, CI, board, handoff, ruleset, or main change is made.",
    "No network access or download is attempted; absent artifacts are not fabricated, reconstructed, mirrored, or substituted.",
    "No sibling restoration/enhancement evidence is inherited, pooled, or treated as this task's result.",
    "Missing, invalid, nonfinite, or adverse cases do not qualify; this package is proposal-only blocker evidence.",
]

RELEASE_GATES = [
    ("RG-01", "Exact source provenance", "Provide immutable VoiceFixer source revision, reviewed license text, and per-file digests for the exact canonical implementation."),
    ("RG-02", "Exact checkpoint/assets and rights", "Provide caller-selected exact checkpoint/weights/config/assets with immutable digests and reviewed license, redistribution, and output-use terms."),
    ("RG-03", "Pinned runtime and task geometry", "Provide reproducible pinned runtime and exact task geometry: sample rate, channels, frame/hop/reset/drain or offline boundary, degradation scope, and adapter contract."),
    ("RG-04", "API/ABI and installed-v0 compatibility", "Define a versioned optional adapter boundary preserving installed v0 behavior; no default/API/ABI/shared build change without independent review."),
    ("RG-05", "Deterministic conformance and adverse rejection", "Run deterministic fixture conformance with 3x cold-start byte-identical regen and strict rejection of missing/invalid/nonfinite/adverse cases."),
    ("RG-06", "Matched Restoration evidence", "Provide rights-cleared matched Restoration-profile evidence: frozen corruption/metadata/clean baseline, degradation/burst/bandwidth strata, concealment/validity, decoded intervals, task-specific quality, peak/timing bounds, and controls."),
    ("RG-07", "Target execution and availability", "Measure paced target-device/runtime CPU, memory, deadline, availability, and failure behavior for the exact configuration."),
    ("RG-08", "Independent review and release decision", "Obtain exact-head independent review, hosted CI, and explicit release approval; missing/adverse results remain non-qualifying."),
]

BLOCKERS = [
    ("BLK-01", "RG-01", "No exact pinned canonical VoiceFixer source revision or reviewed source-license bundle is present in this worktree."),
    ("BLK-02", "RG-02", "No exact licensed VoiceFixer checkpoint/weights/config/assets with immutable digests and reviewed rights/redistribution/output-use terms are present."),
    ("BLK-03", "RG-03", "No pinned reproducible runtime or exact qualified task geometry/adapter boundary is present."),
    ("BLK-04", "RG-05", "No deterministic VoiceFixer conformance execution or adverse/missing/invalid/nonfinite rejection evidence exists on pinned assets."),
    ("BLK-05", "RG-06", "No rights-cleared matched Restoration cohort or Restoration-profile result (corruption/metadata, degradation strata, concealment/validity, decoded intervals, quality, peak/timing bounds) exists."),
    ("BLK-06", "RG-07", "No target-device timing, CPU/memory, availability, or paced execution measurement exists."),
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
        expanded = os.path.expanduser(p)
        if "*" in expanded:
            from glob import glob

            probes.append({"path": p, "root": "home", "exists": len(glob(expanded)) > 0})
        else:
            probes.append({"path": p, "root": "home", "exists": Path(expanded).exists()})
    return probes


def actual_source_pins() -> dict[str, str]:
    pins = {p: sha256_file(resolve_source(p)) for p in PLAN_PINS}
    row = linked_row_projection()
    pins["linked-row:" + TASK] = sha256_bytes(canonical_bytes(row).rstrip(b"\n"))
    for dep in LINKED_ROW_IDS[1:]:
        pins["linked-row:" + dep] = sha256_bytes(canonical_bytes(linked_dep_row(dep)).rstrip(b"\n"))
    return pins


def actual_boundary_pins() -> dict[str, str]:
    return {p: sha256_file(resolve_worktree(p)) for p in BOUNDARY_PINS}


def restoration_profile_requirements() -> list[dict[str, Any]]:
    return [
        {
            "id": "RST-01",
            "requirement": "Freeze corruption, metadata and corresponding clean/audio packet baseline.",
            "status": "blocked",
            "evidence": "No exact VoiceFixer source, checkpoint, pinned runtime, or frozen corruption/metadata/clean baseline is present.",
        },
        {
            "id": "RST-02",
            "requirement": "Stratify by degradation, erasure burst and bandwidth.",
            "status": "blocked",
            "evidence": "No rights-cleared matched cohort with degradation, erasure burst, or bandwidth strata is present.",
        },
        {
            "id": "RST-03",
            "requirement": "Report discrete concealment/validity.",
            "status": "blocked",
            "evidence": "No deterministic VoiceFixer execution or concealment/validity accounting exists on pinned assets.",
        },
        {
            "id": "RST-04",
            "requirement": "Report decoded intervals.",
            "status": "blocked",
            "evidence": "No qualified restoration output or decoded-interval accounting exists.",
        },
        {
            "id": "RST-05",
            "requirement": "Report task-specific quality.",
            "status": "blocked",
            "evidence": "No task-matched restoration quality result or control comparison exists.",
        },
        {
            "id": "RST-06",
            "requirement": "Report bounds on output peaks and timing.",
            "status": "blocked",
            "evidence": "No output peak bound, timing bound, or paced runtime measurement exists.",
        },
    ]


def linked_row_identity() -> dict[str, Any]:
    row = linked_row_projection()
    deps = {d: linked_dep_row(d) for d in LINKED_ROW_IDS[1:]}
    return {
        "task": TASK,
        "stable_fields": list(STABLE_ROW_FIELDS),
        "mutable_board_hash_used": False,
        "projection": row,
        "projection_sha256": sha256_bytes(canonical_bytes(row).rstrip(b"\n")),
        "dependency_rows": deps,
        "dependency_row_sha256": {
            d: sha256_bytes(canonical_bytes(deps[d]).rstrip(b"\n")) for d in deps
        },
    }


def blockers() -> list[dict[str, Any]]:
    return [
        {"id": bid, "gate": gate, "status": "open", "qualifies": False, "summary": summary}
        for bid, gate, summary in BLOCKERS
    ]


def release_gates() -> list[dict[str, Any]]:
    return [
        {"id": gid, "title": title, "status": "blocked", "qualifies": False, "reopen_condition": reopen}
        for gid, title, reopen in RELEASE_GATES
    ]


def build_contract() -> dict[str, Any]:
    row = linked_row_projection()
    return {
        "schema": CONTRACT_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "decision": DECISION,
        "incomplete": True,
        "proposal_only": True,
        "qualification": {"status": QUALIFICATION_STATUS, "qualified": False, "not_qualified": True},
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "write_scope": WRITE_SCOPE,
        "dependencies": [linked_dep_row(d) for d in LINKED_ROW_IDS[1:]],
        "linked_row_identity": linked_row_identity(),
        "source_pins": actual_source_pins(),
        "boundary_pins": actual_boundary_pins(),
        "absence_probes": absence_probes(),
        "blockers": blockers(),
        "release_gates": release_gates(),
        "restoration_profile_requirements": restoration_profile_requirements(),
        "non_claims": NON_CLAIMS,
        "task_row_projection": row,
    }


def build_report() -> dict[str, Any]:
    probes = absence_probes()
    all_absent = all(not p["exists"] for p in probes)
    return {
        "schema": REPORT_SCHEMA,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "decision": DECISION,
        "incomplete": True,
        "proposal_only": True,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "not_qualified": True,
            "reason": "No exact pinned VoiceFixer source/checkpoint/runtime/rights-cleared matched cohort or qualified Restoration evidence; missing/adverse results are non-qualifying.",
        },
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "linked_row_identity": linked_row_identity(),
        "source_pins": actual_source_pins(),
        "boundary_pins": actual_boundary_pins(),
        "absence_summary": {
            "all_absent": all_absent,
            "probe_count": len(probes),
            "present_count": sum(1 for p in probes if p["exists"]),
            "present_paths": [p["path"] for p in probes if p["exists"]],
            "probes": probes,
        },
        "blockers": blockers(),
        "release_gates": release_gates(),
        "restoration_profile_requirements": restoration_profile_requirements(),
        "evidence": {
            "licensed_source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "real_corpus_present": False,
            "listening_present": False,
            "device_timing_present": False,
            "measured_result_present": False,
            "source_reported_only": True,
            "inventory_finding": "VoiceFixer is sdk-model in inventory; no exact pinned source/checkpoint/runtime/rights-cleared matched restoration evidence is present in this worktree.",
        },
        "dependencies": [linked_dep_row(d) for d in LINKED_ROW_IDS[1:]],
        "non_claims": NON_CLAIMS,
    }


def report_digest(report: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(report))


def sources_manifest() -> str:
    rows: list[tuple[str, str]] = []
    local = [
        "README.md",
        "contract.json",
        "reference.py",
        "report.json",
        "report.json.sha256",
        "run.py",
        "test_reference.py",
        "verify.py",
        "contract.json.license",
        "README.md.license",
        "report.json.license",
        "report.json.sha256.license",
        "SOURCES.sha256.license",
    ]
    for name in local:
        p = HERE / name
        if p.is_file():
            rows.append((sha256_file(p), name))
    for rel, digest in sorted(actual_source_pins().items()):
        rows.append((digest, "source:" + rel))
    for rel, digest in sorted(actual_boundary_pins().items()):
        rows.append((digest, "boundary:" + rel))
    rows.sort(key=lambda x: x[1])
    return "".join(f"{d}  {n}\n" for d, n in rows)
