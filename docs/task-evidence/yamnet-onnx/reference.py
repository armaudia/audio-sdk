# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-YAMNET-ONNX.

Feasibility package is blocked: no exact pinned YAMNet ONNX runtime/model asset
identity, rights/publication record, matched rate/content evidence, or approved
reference parity is present in this workspace. No download, model execution,
network, real audio, device timing, listening, public benchmark, release, or
qualification claim is made. AudioSet label handling and cadence are pinned as
advisory metadata requirements only.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent


def _find_sdk_root() -> Path:
    override = os.environ.get("SDK_ROOT")
    if override:
        p = Path(override)
        if (p / "REUSE.toml").is_file():
            return p.resolve()
    cur = HERE
    while cur != cur.parent:
        if (cur / "REUSE.toml").is_file() and (cur / "api/include/audio_sdk").is_dir():
            return cur.resolve()
        cur = cur.parent
    return HERE.parents[2].resolve()


SDK_ROOT = _find_sdk_root()


def _find_source_root() -> Path:
    override = os.environ.get("SOURCE_ROOT") or os.environ.get("AUDIOML_ROOT")
    candidates = [Path(override)] if override else []
    candidates.extend([SDK_ROOT.parent.parent, Path("/Users/htsakanyan/workspace/audio/audioml")])
    for c in candidates:
        if (c / "audio-benchmark-platform/plan/swarm/TASKS.json").is_file():
            return c.resolve()
    return Path("/Users/htsakanyan/workspace/audio/audioml")


SOURCE_ROOT = _find_source_root()

TASK = "SDK-YAMNET-ONNX"
TITLE = "YAMNet ONNX"
COMPONENT = "yamnet-onnx"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "rate"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"
BASE_COMMIT = "a8f2301a4d650b73b7fe5e77ac1d72f757d3fedc"
BRANCH = "swarm/SDK-YAMNET-ONNX"
REVIEWER = "reviewer-YAMNET-ONNX"
CLAIM_WORKTREE = "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-YAMNET-ONNX"
TASK_PREFIX = "docs/task-evidence/yamnet-onnx/"
SCHEMA_REPORT = "audio-sdk/task-evidence/yamnet-onnx/report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"

STABLE_TASK_FIELDS = (
    "acceptance", "component", "deliverable", "depends_on", "evidence",
    "id", "mode", "repository", "title", "write_scope",
)
MUTABLE_TASK_FIELDS = (
    "blocked_reason", "dispatch_priority", "handoff", "owner", "review", "status",
)

TASK_ROW_STABLE_SHA256 = "2cfe5276c47832afe73f0ed1a339571355cbc33f91a06b94bdf9f74fc552e3ad"
TASK_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "acceptance": "Apply the rate acceptance profile; record exact scope, evidence, failure/control results, and remaining release gates. A readiness conclusion with an exact external blocker is an accepted investigation handoff; it does not close the conditional implementation.",
    "component": "yamnet-onnx",
    "deliverable": "Verify runnable source, exact assets, permitted scope, task geometry and matched evidence. Then reproduce the exact model/runtime as a caller-supplied-asset reference and add an opt-in SDK adapter once its prerequisites pass. Record a concrete blocker if feasibility fails. Pin AudioSet label handling and cadence; keep scores advisory.",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "evidence": [
        "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "cpp-library/pipeline-validation/playback-speed-candidates.md",
    ],
    "id": "SDK-YAMNET-ONNX",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "title": "YAMNet ONNX",
    "write_scope": ["SDK provider, tool or evidence directory for yamnet-onnx and its own fixtures"],
}

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "cpp-library/pipeline-validation/playback-speed-candidates.md": "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
LOCAL_PIN_PATHS = (
    "README.md",
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

SCOPE_BASE_REFS = ("origin/main", "main")

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "sdk_callback_invoked": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "real_audio": False,
    "real_corpus": False,
    "real_dataset": False,
    "dataset_downloaded": False,
    "model_executed": False,
    "weights_downloaded": False,
    "runtime_invoked": False,
    "network_used": False,
    "device_timing": False,
    "listening": False,
    "public_benchmark": False,
    "release_claim": False,
    "task_local_only": True,
}

NON_CLAIMS: List[str] = [
    "No YAMNet ONNX model, checkpoint, runtime, labels artifact, or derived weight is loaded, executed, staged, or redistributed.",
    "No network request, download, dataset acquisition, or external runtime invocation occurs.",
    "No real audio, real corpus, device timing, listening, public benchmark, or release/qualification claim is made.",
    "AudioSet label handling and cadence metadata are advisory contract pins only; no event detection quality is claimed.",
    "Candidate/source notes are pinned context only and are not promoted to measured or qualified evidence.",
    "No provider, descriptor, registry, installed v0 path, shared build, CI, board, or handoff change is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER and qualification remains not_qualified.",
]

GATE_REQUIREMENTS: List[Tuple[str, str]] = [
    ("exact_source_and_asset_identity", "Exact YAMNet ONNX source revision, ONNX model/checkpoint, AudioSet label map/class-name artifact, hashes, byte counts, and immutable manifests are pinned and present."),
    ("rights_and_publication", "Acquisition, local evaluation, publication, redistribution, product-use, and derivative-output rights for model/labels/data are cleared with complete notices."),
    ("matched_reference_parity", "An approved exact-runtime reference reproduces the candidate on frozen inputs with hashed outputs and verified parity/tolerance policy."),
    ("rate_cohort_and_scoring", "A rights-cleared held-out rate/content cohort with task-matched scoring, source/output mapping, duration/pitch/transient/playback controls is present."),
    ("runtime_and_reproducibility", "An isolated pinned runtime and deterministic command recipe reproduce outputs without network or hidden mutation."),
    ("label_cadence_and_contract", "AudioSet label handling, class ordering, score calibration/cadence, window/hop, and timestamp mapping are pinned and verified as advisory-only contract."),
    ("adapter_boundary_and_isolation", "Any future SDK adapter is optional, caller-supplied-asset, preserves installed v0 behavior, and is not registered/enabled by default."),
    ("public_default_and_release", "Explicit default-selection, resource/deadline evidence, and release/public-benchmark approval are recorded; default remains off."),
]

EXACT_BLOCKERS: List[Dict[str, Any]] = [
    {"id": "deployable_asset_absent", "gate_ids": ["exact_source_and_asset_identity", "matched_reference_parity"], "requirement": "Provide exact deployable local YAMNet ONNX model/checkpoint, AudioSet label map artifact, and immutable hashes/byte counts/provenance.", "state": "No exact local YAMNet ONNX model/checkpoint or pinned label-map artifact is staged in this workspace for this task package."},
    {"id": "rights_uncleared", "gate_ids": ["rights_and_publication", "public_default_and_release"], "requirement": "Clear model/label/data rights, notices, redistribution, product-use, and publication terms before any claim.", "state": "No per-asset rights record, license decision, redistribution approval, or publication review is present for a concrete staged candidate."},
    {"id": "exact_runtime_absent", "gate_ids": ["runtime_and_reproducibility", "matched_reference_parity"], "requirement": "Provide an isolated pinned runtime with deterministic execution recipe and recorded platform for the exact candidate.", "state": "No isolated pinned ONNX/runtime environment, lockfile, or deterministic execution trace is staged; model execution is absent."},
    {"id": "reference_parity_absent", "gate_ids": ["matched_reference_parity", "runtime_and_reproducibility"], "requirement": "Reproduce an approved exact-runtime reference on frozen inputs with hashed outputs and parity/tolerance verification.", "state": "No approved reference outputs, parity vectors, or independently verified reproduction exists."},
    {"id": "rate_cohort_absent", "gate_ids": ["rate_cohort_and_scoring", "public_default_and_release"], "requirement": "Provide rights-cleared held-out rate/content evidence with source/output mapping, duration/pitch/transient/playback controls and task-matched scoring.", "state": "No rights-cleared rate/content cohort or matched scoring run is staged; no real audio/corpus evidence is produced."},
    {"id": "label_cadence_unverified", "gate_ids": ["label_cadence_and_contract", "adapter_boundary_and_isolation"], "requirement": "Pin and verify AudioSet label handling, class ordering, score calibration/cadence, window/hop, and timestamp mapping; keep scores advisory.", "state": "Label handling and cadence are recorded as advisory contract requirements only; no exact model/runtime contract has been verified."},
    {"id": "adapter_boundary_incomplete", "gate_ids": ["adapter_boundary_and_isolation", "public_default_and_release"], "requirement": "Keep any future SDK adapter optional, caller-supplied-asset, off by default, and outside installed v0/shared build/CI/public registration.", "state": "No opt-in adapter, descriptor, registry entry, provider registration, or installed-v0 change exists; boundary remains blocked."},
    {"id": "public_default_release_blocked", "gate_ids": ["public_default_and_release"], "requirement": "Record explicit default-selection, resource/deadline, release, and public-benchmark approval; missing evidence cannot qualify.", "state": "No default, release, public benchmark, device timing, listening, or qualification approval exists; status remains not_qualified."},
]

RATE_PROFILE_REQUIREMENTS = [
    {"id": "RT-01", "requirement": "Measure source/output mapping, duration, pitch, transient audibility and playback buffering.", "status": "blocked", "qualification_effect": "none"},
    {"id": "RT-02", "requirement": "Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window.", "status": "blocked", "qualification_effect": "none"},
    {"id": "RT-03", "requirement": "Keep pause/filler decisions tied to source timestamps and measure speech preservation.", "status": "blocked", "qualification_effect": "none"},
    {"id": "RT-04", "requirement": "Record exact input/output cadence, window/hop, and AudioSet label handling; keep scores advisory.", "status": "blocked", "qualification_effect": "none"},
    {"id": "RT-05", "requirement": "Measure target-device/runtime CPU, memory, deadline, availability, and failure behavior for exact config.", "status": "blocked", "qualification_effect": "none"},
    {"id": "RT-06", "requirement": "Validate invalid/missing/nonfinite/adverse cases fail closed without qualification.", "status": "blocked", "qualification_effect": "none"},
    {"id": "RT-07", "requirement": "Reproduce exact model/runtime on frozen inputs with hashed outputs and parity/tolerance policy.", "status": "blocked", "qualification_effect": "none"},
    {"id": "RT-08", "requirement": "Obtain independent review and explicit release/default/public-benchmark approval before any qualifying claim.", "status": "blocked", "qualification_effect": "none"},
]


class Reject(ValueError):
    """Deterministic fail-closed rejection."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"


def canonical_text(obj: Any) -> str:
    return canonical_bytes(obj).decode("utf-8")


def _reject_constant(value: str) -> Any:
    raise Reject(f"non-finite JSON constant: {value}")


def _object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    obj: Dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise Reject(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def strict_loads(text: str) -> Any:
    if text.startswith("\ufeff"):
        raise Reject("BOM not allowed")
    decoder = json.JSONDecoder(object_pairs_hook=_object_pairs_hook, parse_constant=_reject_constant)
    obj, end = decoder.raw_decode(text)
    tail = text[end:]
    if tail and tail != "\n":
        raise Reject("trailing content after JSON document")
    return obj


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_rate_control(case: Dict[str, Any]) -> Dict[str, Any]:
    """Tiny synthetic rate/content contract control. No audio/model."""
    _require(isinstance(case, dict), "case must be object")
    allowed = {"case_id", "total_samples", "scored_regions", "source_speech", "preserved_speech", "cadence_hop_samples", "notes"}
    extra = sorted(set(case) - allowed)
    _require(not extra, f"case has unknown fields: {extra}")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id.strip(), "case_id invalid")
    total = case.get("total_samples")
    _require(_is_int(total) and total > 0, "total_samples must be positive int")
    hop = case.get("cadence_hop_samples")
    _require(_is_int(hop) and hop > 0, "cadence_hop_samples must be positive int")
    notes = case.get("notes", "")
    _require(isinstance(notes, str), "notes must be string")

    def parse_intervals(name: str) -> List[Tuple[int, int]]:
        raw = case.get(name)
        _require(isinstance(raw, list), f"{name} must be list")
        out: List[Tuple[int, int]] = []
        for i, item in enumerate(raw):
            _require(isinstance(item, dict), f"{name}[{i}] must be object")
            _require(set(item) == {"start", "end"}, f"{name}[{i}] keys must be start,end")
            start, end = item["start"], item["end"]
            _require(_is_int(start) and _is_int(end), f"{name}[{i}] start/end must be int")
            _require(0 <= start < end <= total, f"{name}[{i}] out of bounds")
            out.append((start, end))
        out.sort()
        for i in range(1, len(out)):
            _require(out[i - 1][1] <= out[i][0], f"{name} overlaps at {i - 1}/{i}")
        return out

    scored = parse_intervals("scored_regions")
    source = parse_intervals("source_speech")
    preserved = parse_intervals("preserved_speech")
    _require(scored, "scored_regions must not be empty")

    sm = [False] * total
    src = [False] * total
    prv = [False] * total
    for arr, intervals in ((sm, scored), (src, source), (prv, preserved)):
        for s, e in intervals:
            for i in range(s, e):
                arr[i] = True
    tp = fp = fn = tn = unknown = 0
    for i in range(total):
        if not sm[i]:
            unknown += 1
            continue
        s, p = src[i], prv[i]
        if s and p:
            tp += 1
        elif (not s) and p:
            fp += 1
        elif s and (not p):
            fn += 1
        else:
            tn += 1
    scored_samples = tp + fp + fn + tn
    _require(scored_samples + unknown == total, "total invariant failed")
    miss = (fn / (tp + fn)) if (tp + fn) else None
    far = (fp / (fp + tn)) if (fp + tn) else None
    return {
        "case_id": case_id,
        "total_samples": total,
        "scored_samples": scored_samples,
        "unknown_samples": unknown,
        "cadence_hop_samples": hop,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "speech_miss_rate": miss,
        "false_alarm_rate": far,
        "unknown_never_nonspeech": True,
        "qualification_effect": "none",
    }


CONTROL_CASE = {
    "case_id": "synthetic-rate-control",
    "total_samples": 24,
    "cadence_hop_samples": 480,
    "scored_regions": [{"start": 0, "end": 8}, {"start": 12, "end": 24}],
    "source_speech": [{"start": 1, "end": 4}, {"start": 14, "end": 18}],
    "preserved_speech": [{"start": 2, "end": 5}, {"start": 13, "end": 17}],
    "notes": "Synthetic contract control only; no real audio/corpus/model.",
}

ADVERSE_CASES: List[Tuple[str, Dict[str, Any], str]] = [
    ("missing_scored_regions", {"case_id": "x", "total_samples": 8, "source_speech": [], "preserved_speech": [], "cadence_hop_samples": 1}, "scored_regions must be list"),
    ("bad_total", {"case_id": "x", "total_samples": 0, "scored_regions": [{"start": 0, "end": 1}], "source_speech": [], "preserved_speech": [], "cadence_hop_samples": 1}, "total_samples must be positive int"),
    ("overlap", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": 4}, {"start": 3, "end": 8}], "source_speech": [], "preserved_speech": [], "cadence_hop_samples": 1}, "scored_regions overlaps"),
    ("out_of_bounds", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": 9}], "source_speech": [], "preserved_speech": [], "cadence_hop_samples": 1}, "out of bounds"),
    ("bad_hop", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": 8}], "source_speech": [], "preserved_speech": [], "cadence_hop_samples": 0}, "cadence_hop_samples must be positive int"),
    ("unknown_field", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": 8}], "source_speech": [], "preserved_speech": [], "cadence_hop_samples": 1, "extra": 1}, "unknown fields"),
    ("bad_interval_key", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "finish": 8}], "source_speech": [], "preserved_speech": [], "cadence_hop_samples": 1}, "keys must be start,end"),
    ("non_int", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": "8"}], "source_speech": [], "preserved_speech": [], "cadence_hop_samples": 1}, "start/end must be int"),
]


def adverse_controls() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name, case, needle in ADVERSE_CASES:
        try:
            validate_rate_control(case)
            rows.append({"case": name, "result": "accepted", "error": "unexpected"})
        except Exception as exc:
            rows.append({"case": name, "result": "rejected", "error_contains": needle, "error": str(exc)})
    for name, text, needle in [
        ("strict_json_duplicate_key", '{"a":1,"a":2}', "duplicate JSON key"),
        ("strict_json_nonfinite", "[NaN]", "non-finite JSON constant"),
        ("strict_json_trailing", '{"a":1}x', "trailing content"),
    ]:
        try:
            strict_loads(text)
            rows.append({"case": name, "result": "accepted", "error": "unexpected"})
        except Exception as exc:
            rows.append({"case": name, "result": "rejected", "error_contains": needle, "error": str(exc)})
    return rows


def task_row_identity() -> Dict[str, Any]:
    return {
        "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "stable_sha256": TASK_ROW_STABLE_SHA256,
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "stable_fields": dict(TASK_ROW_STABLE_FIELDS),
    }


def scope_base(root: Path, refs: Sequence[str] = SCOPE_BASE_REFS) -> str | None:
    candidates: List[Tuple[int, int, str]] = []
    for idx, ref in enumerate(refs):
        result = subprocess.run(
            ["git", "-C", str(root), "merge-base", "HEAD", ref],
            capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            continue
        base = result.stdout.strip()
        if not base:
            continue
        dist = subprocess.run(
            ["git", "-C", str(root), "rev-list", "--count", base + "..HEAD"],
            capture_output=True, text=True, check=False,
        )
        count = int(dist.stdout.strip()) if dist.returncode == 0 and dist.stdout.strip().isdigit() else 10**9
        candidates.append((count, idx, base))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def scope_changed_paths(root: Path, base: str) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", base + "...HEAD"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise ValueError("scope diff failed: " + (result.stderr.strip() or result.stdout.strip()))
    out: List[str] = []
    for line in result.stdout.splitlines():
        p = line.strip()
        if p:
            out.append(p)
    return sorted(set(out))


def scope_violations(changed: Sequence[str]) -> List[str]:
    return [p for p in changed if not p.startswith(TASK_PREFIX)]


def build_report() -> Dict[str, Any]:
    control = validate_rate_control(CONTROL_CASE)
    adverse = adverse_controls()
    gates = [{"id": gid, "requirement": req, "status": "blocked"} for gid, req in GATE_REQUIREMENTS]
    blockers = [dict(item) for item in EXACT_BLOCKERS]
    return {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": {
            "status": QUALIFICATION,
            "candidate_qualified": False,
            "no_missing_result_qualifies_candidate": True,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "blocked_gate_count": len(gates),
            "blocked_gate_ids": [g["id"] for g in gates],
            "reason": "No exact local YAMNet ONNX asset/runtime/rights/rate-cohort/reference parity evidence is present; labels/cadence remain advisory-only and unverified.",
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "generated_by": "reference.py",
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "task_row_identity": task_row_identity(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_audit": {
            "audit_result": "absent",
            "qualified": False,
            "observed": [
                {"path": "data/models/yamnet-onnx", "present": False},
                {"path": "data/models/yamnet", "present": False},
                {"path": "third_party/yamnet-onnx", "present": False},
                {"path": "adapters/yamnet-onnx", "present": False},
            ],
            "note": "Fixed local probes only; no network/download/execution.",
        },
        "rate_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": list(RATE_PROFILE_REQUIREMENTS),
        },
        "gates": gates,
        "exact_blockers": blockers,
        "candidate_metrics": None,
        "reference_protocol": {
            "model_executed": False,
            "executor": "absent",
            "qualification_effect": "none",
            "notes": "No executable YAMNet ONNX reference is staged; this package records blockers only.",
        },
        "synthetic_control": control,
        "controls": {
            "adverse": adverse,
            "adverse_all_rejected": all(r["result"] == "rejected" for r in adverse),
            "missing_result_never_qualifies": True,
        },
        "source_reported_context": {
            "label": "source_reported_not_measured_here",
            "qualification_effect": "none",
            "items": [
                {"source": "cpp-library/pipeline-validation/playback-speed-candidates.md", "note": "YAMNet ONNX: generic event model, not podcast-tuned; AudioSet labels CC BY 4.0; 521 classes, 0.96s window / 0.48s hop."}
            ],
        },
        "advisory_label_cadence_contract": {
            "qualification_effect": "none",
            "audioset_label_handling": "pinned_requirement_only_unverified",
            "class_ordering": "pinned_requirement_only_unverified",
            "score_calibration": "advisory_only_unverified",
            "window_hop_cadence": "pinned_requirement_only_unverified",
            "timestamp_mapping": "pinned_requirement_only_unverified",
        },
        "non_claims": list(NON_CLAIMS),
        "reproduction": {
            "cold_start_regenerations": 3,
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
            "report": "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py report.json",
            "sources": "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py sources",
            "tests": "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest -v test_reference.py",
            "verify": "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 verify.py",
        },
    }


def build_contract(report: Dict[str, Any] | None = None) -> Dict[str, Any]:
    report = report or build_report()
    return {
        "schema_id": SCHEMA_CONTRACT,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "qualification": dict(report["qualification"]),
        "boundary": dict(report["boundary"]),
        "scope": dict(report["scope"]),
        "gates": list(report["gates"]),
        "exact_blockers": [{"id": b["id"], "requirement": b["requirement"]} for b in report["exact_blockers"]],
        "rate_profile_requirements": list(report["rate_profile"]["required_items"]),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "task_row_identity": {
            "source": report["task_row_identity"]["source"],
            "stable_sha256": report["task_row_identity"]["stable_sha256"],
            "whole_file_hashed": False,
            "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        },
        "non_claims": list(NON_CLAIMS),
        "reproduction": dict(report["reproduction"]),
        "licensing": {
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "generated_json_sidecars": True,
        },
    }
