# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic blocker evidence for SDK-VOICEFILTER.

Standard library only. VoiceFilter has no exact pinned open Google
weights/runtime, no exact licensed third-party substitute admitted as this
candidate, no exact reproducible runtime/task geometry, and no qualified
spatial evidence present for this task in this worktree. This module records
a fail-closed DEFER blocker package; it never downloads, fabricates,
registers, or executes VoiceFilter.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

TASK = "SDK-VOICEFILTER"
COMPONENT = "voicefilter"
TITLE = "VoiceFilter"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "spatial"
STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
BRANCH = "swarm/SDK-VOICEFILTER"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
WRITE_SCOPE = "docs/task-evidence/voicefilter/ only"
TASK_PREFIX = "docs/task-evidence/voicefilter/"
CONTRACT_ID = "audio-sdk/voicefilter-blocker/0.1"
REPORT_SCHEMA = "audio-sdk/voicefilter-report/0.1"

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
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
}
BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LINKED_ROW_IDS = ("SDK-VOICEFILTER", "SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER")
STABLE_ROW_FIELDS = ("id", "repository", "mode", "component", "depends_on", "title", "evidence", "deliverable", "acceptance", "write_scope")

WORKSPACE_PROBES = (
    "data/checkouts/voicefilter",
    "data/checkouts/VoiceFilter",
    "data/models/voicefilter",
    "data/models/VoiceFilter",
    "data/reference/voicefilter",
    "third_party/voicefilter",
    "research/voicefilter",
    "research/voice-enhancement-20261101/repos/voicefilter",
    "research/voice-enhancement-20261101/models/voicefilter",
)
WORKTREE_PROBES = (
    "adapters/voicefilter",
    "schemas/providers/voicefilter",
    "third_party/voicefilter",
    "tools/voicefilter",
)
HOME_PROBES = ("~/.cache/voicefilter", "~/.cache/huggingface/hub/models--*voicefilter*", "~/Library/voicefilter")

NON_CLAIMS = [
    "No VoiceFilter source, checkpoint, weights, enrollment/reference audio, runtime, config, or extracted target audio is present, downloaded, imported, linked, or executed.",
    "No real corpus, enrolled speaker, consented reference utterance, listening, device timing, benchmark, or release result is produced or claimed.",
    "No provider registration, descriptor, registry, default, public API/ABI, shared build, CI, board, handoff, ruleset, or main change is made.",
    "No network access or download is attempted; absent artifacts are not fabricated, reconstructed, mirrored, or substituted.",
    "No third-party substitute is treated as the original VoiceFilter candidate without exact identity, rights, and evidence.",
    "No sibling spatial/TSE evidence is inherited, pooled, or treated as this task's result.",
    "Missing, invalid, nonfinite, or adverse cases do not qualify; this package is proposal-only blocker evidence.",
]

RELEASE_GATES = [
    ("RG-01", "Exact source/checkpoint provenance", "Provide immutable VoiceFilter or separately identified substitute source revision, reviewed license text, exact checkpoint/weights identity, and per-file digests."),
    ("RG-02", "Exact assets, rights, and enrollment protocol", "Provide caller-selected exact checkpoint/weights/config/reference-cue assets with immutable digests and reviewed license, consent, redistribution, and output-use terms; freeze enrollment/reference protocol."),
    ("RG-03", "Pinned runtime and task geometry", "Provide reproducible pinned runtime and exact task geometry: sample rate, channels/layout, frame/hop/reset/drain, reference timing, cue conditioning, and adapter contract."),
    ("RG-04", "API/ABI and installed-v0 compatibility", "Define a versioned optional adapter boundary preserving installed v0 behavior; no default/API/ABI/shared build change without independent review."),
    ("RG-05", "Deterministic conformance and adverse rejection", "Run deterministic fixture conformance with 3x cold-start byte-identical regen and strict rejection of missing/invalid/nonfinite/adverse/malformed cases."),
    ("RG-06", "Matched spatial evidence", "Provide rights-cleared matched Spatial-profile evidence: geometry/layout/timestamp calibration, source/target/reference conditions, localization/activity/extraction labels, leakage, target damage, channel loss, and room/reference changes."),
    ("RG-07", "Target execution and availability", "Measure paced target-device/runtime CPU, memory, deadline, availability, and failure behavior for the exact configuration."),
    ("RG-08", "Independent review and release decision", "Obtain exact-head independent review, hosted CI, and explicit release approval; missing/adverse results remain non-qualifying."),
]

BLOCKERS = [
    ("BLK-01", "RG-01", "Original Google VoiceFilter weights/runtime are not open; no exact pinned licensed source/checkpoint identity is present for this task."),
    ("BLK-02", "RG-02", "No exact licensed reference/enrollment assets, consent/redistribution/output-use review, or frozen cue protocol is present."),
    ("BLK-03", "RG-03", "No pinned reproducible runtime or exact qualified spatial/task geometry/reference-timing adapter boundary is present."),
    ("BLK-04", "RG-05", "No deterministic VoiceFilter conformance execution or adverse/missing/invalid/nonfinite rejection evidence exists on pinned assets."),
    ("BLK-05", "RG-06", "No rights-cleared matched spatial cohort or spatial-profile result (geometry, labels, leakage, target damage, channel loss, room/reference changes) exists."),
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
        pins[f"linked-row:{dep}"] = sha256_bytes(canonical_bytes(linked_dep_row(dep)).rstrip(b"\n"))
    return pins


def actual_boundary_pins() -> dict[str, str]:
    return {p: sha256_file(resolve_worktree(p)) for p in BOUNDARY_PINS}


def spatial_profile_requirements() -> list[dict[str, Any]]:
    return [
        {
            "id": "SP-01",
            "requirement": "Record geometry, layout, timestamp calibration, source/target/reference conditions and permissions.",
            "status": "blocked",
            "evidence": "No exact VoiceFilter runtime, array/layout, timestamp calibration, or rights-cleared source/target/reference condition is present.",
        },
        {
            "id": "SP-02",
            "requirement": "Compare localization/activity/extraction with task-matched held-out labels.",
            "status": "blocked",
            "evidence": "No rights-cleared held-out target-speaker extraction labels or reproduced VoiceFilter outputs exist.",
        },
        {
            "id": "SP-03",
            "requirement": "Report leakage, target damage, channel loss, and changes in room/reference conditions.",
            "status": "blocked",
            "evidence": "No measured leakage, target damage, channel-loss, or room/reference-condition result exists.",
        },
        {
            "id": "SP-04",
            "requirement": "Keep exact source intervals, availability, dropped/stale events, and cross-hop behavior verifiable.",
            "status": "blocked",
            "evidence": "No deterministic runtime execution, source-interval accounting, or dropped/stale/cross-hop evidence exists.",
        },
        {
            "id": "SP-05",
            "requirement": "Freeze enrollment/reference cue protocol and target-absent/overlap controls.",
            "status": "blocked",
            "evidence": "No exact reference utterance/enrollment cue protocol, target-absent control, or overlap control is pinned.",
        },
        {
            "id": "SP-06",
            "requirement": "Use rights-cleared matched cohort with exact permissions and disclosure boundaries.",
            "status": "blocked",
            "evidence": "No rights-cleared enrolled-speaker mixture corpus with clean target references is present.",
        },
        {
            "id": "SP-07",
            "requirement": "Measure target-device pacing, CPU, memory, deadline, and availability for the exact runtime.",
            "status": "blocked",
            "evidence": "No pinned runtime or device timing measurement exists.",
        },
        {
            "id": "SP-08",
            "requirement": "Missing, invalid, nonfinite, or adverse cases fail closed and remain non-qualifying.",
            "status": "blocked",
            "evidence": "No executable VoiceFilter path exists; package records blocker and enforces fail-closed policy only.",
        },
    ]


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
        "spatial_profile_requirements": spatial_profile_requirements(),
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
            "reason": "Original Google VoiceFilter weights/runtime are not open and no exact licensed substitute/runtime/rights-cleared spatial evidence is present; missing/adverse results are non-qualifying.",
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
            "inventory_finding": "VoiceFilter is blocked/unavailable in inventory: original Google weights/runtime are not open; third-party substitutes are separate candidates.",
            "source_reported_only": True,
            "measured_result_present": False,
            "runtime_present": False,
            "licensed_source_present": False,
            "weights_present": False,
            "real_corpus_present": False,
            "device_timing_present": False,
            "listening_present": False,
        },
        "spatial_profile_requirements": contract["spatial_profile_requirements"],
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
