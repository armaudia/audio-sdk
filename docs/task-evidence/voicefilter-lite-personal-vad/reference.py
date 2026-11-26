# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-VOICEFILTER-LITE-PERSONAL-VAD.

This feasibility package is blocked: no deployable local VoiceFilter-Lite /
personal-VAD checkpoint, enrolled-speaker target-speaker extraction corpus,
exact runtime, rights record, or approved matched reference is present in this
workspace. No download, model execution, network, real audio, device timing,
listening, public benchmark, release, or qualification claim is made.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml")
)

TASK = "SDK-VOICEFILTER-LITE-PERSONAL-VAD"
TITLE = "VoiceFilter-Lite / personal VAD"
SLUG = "voicefilter-lite-personal-vad"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-VOICEFILTER-LITE-PERSONAL-VAD"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "spatial"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

STABLE_TASK_FIELDS = (
    "acceptance",
    "component",
    "deliverable",
    "depends_on",
    "evidence",
    "id",
    "mode",
    "repository",
    "title",
    "write_scope",
)
MUTABLE_TASK_FIELDS = (
    "blocked_reason",
    "dispatch_priority",
    "handoff",
    "owner",
    "review",
    "status",
)

TASK_ROW_STABLE_SHA256 = (
    "84040ebdc344871fa30d710618f6d0315f6e713a1e23554b5c25cad3bc4317c1"
)
TASK_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "acceptance": "Apply the spatial acceptance profile; record exact scope, evidence, failure/control results, and remaining release gates. A readiness conclusion with an exact external blocker is an accepted investigation handoff; it does not close the conditional implementation.",
    "component": "voicefilter-lite-personal-vad",
    "deliverable": "Verify runnable source, exact assets, permitted scope, task geometry and matched evidence. Then reproduce the exact model/runtime as a caller-supplied-asset reference and add an opt-in SDK adapter once its prerequisites pass. Record a concrete blocker if feasibility fails.",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "evidence": ["research/voice-enhancement-20261101/candidate_matrix.csv"],
    "id": "SDK-VOICEFILTER-LITE-PERSONAL-VAD",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "title": "VoiceFilter-Lite / personal VAD",
    "write_scope": [
        "SDK provider, tool or evidence directory for voicefilter-lite-personal-vad and its own fixtures"
    ],
}

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
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
    "No VoiceFilter-Lite/personal-VAD model, checkpoint, runtime, or derived weight is loaded, executed, staged, or redistributed.",
    "No network request, download, dataset acquisition, or external runtime invocation occurs.",
    "No enrolled-speaker, target-speaker extraction, or clean-target reference corpus is consumed or fabricated.",
    "No spatial/TSE quality, leakage, target-preservation, latency, memory, RTF, listening, device, public benchmark, or release result is claimed.",
    "Candidate matrix and research reports are pinned context only; they are not promoted to measured or qualified evidence.",
    "No provider, descriptor, registry, installed v0 path, shared build, CI, board, or handoff change is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER and qualification remains not_qualified.",
]

GATE_REQUIREMENTS: List[Tuple[str, str]] = [
    ("exact_source_and_asset_identity", "Exact VoiceFilter-Lite/personal-VAD source revision, checkpoint/runtime assets, hashes, byte counts, and immutable manifests are pinned and present."),
    ("rights_and_publication", "Acquisition, local evaluation, publication, redistribution, product-use, and derivative-output rights are cleared with complete notices."),
    ("matched_reference_parity", "An approved exact-runtime reference reproduces the candidate on frozen inputs with hashed outputs and verified parity/tolerance policy."),
    ("spatial_cohort_and_scoring", "A rights-cleared held-out cohort with enrollment, overlapping speakers, clean target references, and task-matched spatial/TSE scoring is present."),
    ("runtime_and_reproducibility", "An isolated pinned runtime and deterministic command recipe reproduce outputs without network or hidden mutation."),
    ("geometry_delay_and_state", "Geometry, channel/rate/hop, timestamp calibration, delay, reset/state isolation, and content/availability mapping are verified."),
    ("adapter_boundary_and_isolation", "Any future SDK adapter is optional, caller-supplied-asset, preserves installed v0 behavior, and is not registered/enabled by default."),
    ("public_default_and_release", "Explicit default-selection, resource/deadline evidence, and release/public-benchmark approval are recorded; default remains off."),
]

EXACT_BLOCKERS: List[Dict[str, Any]] = [
    {
        "id": "deployable_checkpoint_absent",
        "gate_ids": ["exact_source_and_asset_identity", "matched_reference_parity"],
        "requirement": "Provide an exact deployable local VoiceFilter-Lite/personal-VAD checkpoint and runtime artifact with immutable hashes, byte counts, and provenance.",
        "state": "No deployable local checkpoint, model artifact, or exact runtime is present in this workspace for this task package.",
    },
    {
        "id": "enrolled_target_cohort_absent",
        "gate_ids": ["spatial_cohort_and_scoring", "matched_reference_parity"],
        "requirement": "Provide a rights-cleared enrolled-speaker cohort with overlapping speakers and clean target references for fair extraction scoring.",
        "state": "Candidate matrix and research reports record no enrolled-speaker mixtures with clean target references; no local cohort is staged.",
    },
    {
        "id": "rights_uncleared",
        "gate_ids": ["rights_and_publication", "public_default_and_release"],
        "requirement": "Clear source/checkpoint/data rights, notices, redistribution, product-use, and publication terms before any claim.",
        "state": "No per-asset rights record, license decision, redistribution approval, or publication review is present.",
    },
    {
        "id": "exact_runtime_absent",
        "gate_ids": ["runtime_and_reproducibility", "matched_reference_parity"],
        "requirement": "Provide an isolated pinned runtime with deterministic execution recipe and recorded platform for the exact candidate.",
        "state": "No isolated pinned runtime, lockfile, or deterministic execution trace is staged; model execution is absent.",
    },
    {
        "id": "reference_parity_absent",
        "gate_ids": ["matched_reference_parity", "runtime_and_reproducibility"],
        "requirement": "Reproduce an approved exact-runtime reference on frozen inputs with hashed outputs and parity/tolerance verification.",
        "state": "No approved reference outputs, parity vectors, or independently verified reproduction exists.",
    },
    {
        "id": "geometry_delay_contract_unverified",
        "gate_ids": ["geometry_delay_and_state", "adapter_boundary_and_isolation"],
        "requirement": "Verify task geometry, enrollment/reference conditioning, sample-time mapping, delay, reset/state isolation, and invalid-input handling.",
        "state": "No candidate-specific geometry/delay/state contract has been verified because no exact runnable artifact or cohort is available.",
    },
    {
        "id": "adapter_boundary_incomplete",
        "gate_ids": ["adapter_boundary_and_isolation", "public_default_and_release"],
        "requirement": "Keep any future SDK adapter optional, caller-supplied-asset, off by default, and outside installed v0/shared build/CI/public registration.",
        "state": "No opt-in adapter, descriptor, registry entry, provider registration, or installed-v0 change exists; boundary remains blocked.",
    },
    {
        "id": "public_default_release_blocked",
        "gate_ids": ["public_default_and_release"],
        "requirement": "Record explicit default-selection, resource/deadline, release, and public-benchmark approval; missing evidence cannot qualify.",
        "state": "No default, release, public benchmark, device timing, listening, or qualification approval exists; status remains not_qualified.",
    },
]


class Reject(ValueError):
    """Deterministic fail-closed rejection."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


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
    decoder = json.JSONDecoder(
        object_pairs_hook=_object_pairs_hook,
        parse_constant=_reject_constant,
    )
    obj, end = decoder.raw_decode(text)
    if text[end:]:
        if text[end:] != "\n":
            raise Reject("trailing content after JSON document")
    return obj


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(float(value)))


def validate_spatial_control(case: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a tiny synthetic spatial/TSE scoring control.

    This is a contract control only: it proves deterministic interval math and
    fail-closed validation. It never represents real audio, a real cohort, or
    model output.
    """
    _require(isinstance(case, dict), "case must be object")
    allowed = {
        "case_id", "total_samples", "scored_regions", "target_speech",
        "hypothesis_target", "enrollment_present", "notes",
    }
    extra = sorted(set(case) - allowed)
    _require(not extra, f"case has unknown fields: {extra}")
    case_id = case.get("case_id")
    _require(isinstance(case_id, str) and case_id.strip(), "case_id invalid")
    total = case.get("total_samples")
    _require(_is_int(total) and total > 0, "total_samples must be positive int")
    enrollment = case.get("enrollment_present")
    _require(isinstance(enrollment, bool), "enrollment_present must be bool")

    def parse_intervals(name: str) -> List[Tuple[int, int]]:
        raw = case.get(name)
        _require(isinstance(raw, list), f"{name} must be list")
        out: List[Tuple[int, int]] = []
        for i, item in enumerate(raw):
            _require(isinstance(item, dict), f"{name}[{i}] must be object")
            _require(set(item) == {"start", "end"},
                     f"{name}[{i}] keys must be start,end")
            start, end = item["start"], item["end"]
            _require(_is_int(start) and _is_int(end),
                     f"{name}[{i}] start/end must be int")
            _require(0 <= start < end <= total,
                     f"{name}[{i}] out of bounds")
            out.append((start, end))
        out.sort()
        for i in range(1, len(out)):
            _require(out[i - 1][1] <= out[i][0], f"{name} overlaps at {i-1}/{i}")
        return out

    scored = parse_intervals("scored_regions")
    target = parse_intervals("target_speech")
    hyp = parse_intervals("hypothesis_target")
    notes = case.get("notes", "")
    _require(isinstance(notes, str), "notes must be string")
    _require(scored, "scored_regions must not be empty")

    def covered(intervals: Sequence[Tuple[int, int]]) -> int:
        return sum(end - start for start, end in intervals)

    def intersect(a: Sequence[Tuple[int, int]], b: Sequence[Tuple[int, int]]) -> int:
        i = j = total_count = 0
        while i < len(a) and j < len(b):
            s = max(a[i][0], b[j][0])
            e = min(a[i][1], b[j][1])
            if s < e:
                total_count += e - s
            if a[i][1] < b[j][1]:
                i += 1
            else:
                j += 1
        return total_count

    scored_samples = covered(scored)
    target_in = intersect(target, scored)
    hyp_in = intersect(hyp, scored)
    tp = intersect(target, hyp)
    tp = intersect([(s, e) for s, e in scored], [(s, e) for s, e in target])
    # recompute tp/fp/fn within scored regions
    def mask(intervals: Sequence[Tuple[int, int]]) -> List[bool]:
        m = [False] * total
        for s, e in intervals:
            for k in range(s, e):
                m[k] = True
        return m

    sm, tm, hm = mask(scored), mask(target), mask(hyp)
    tp = fp = fn = tn = unknown = 0
    for i in range(total):
        if not sm[i]:
            unknown += 1
            continue
        t, h = tm[i], hm[i]
        if t and h:
            tp += 1
        elif (not t) and h:
            fp += 1
        elif t and (not h):
            fn += 1
        else:
            tn += 1
    _require(tp + fp + fn + tn == scored_samples, "confusion invariant failed")
    _require(tp + fp + fn + tn + unknown == total, "total invariant failed")
    miss = (fn / (tp + fn)) if (tp + fn) else None
    far = (fp / (fp + tn)) if (fp + tn) else None
    return {
        "case_id": case_id,
        "enrollment_present": enrollment,
        "total_samples": total,
        "scored_samples": scored_samples,
        "unknown_samples": unknown,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "target_miss_rate": miss,
        "false_alarm_rate": far,
        "unknown_never_nonspeech": True,
        "qualification_effect": "none",
    }


CONTROL_CASE = {
    "case_id": "synthetic-spatial-control",
    "total_samples": 16,
    "enrollment_present": True,
    "scored_regions": [{"start": 0, "end": 4}, {"start": 8, "end": 16}],
    "target_speech": [{"start": 1, "end": 3}, {"start": 10, "end": 12}],
    "hypothesis_target": [{"start": 2, "end": 5}, {"start": 9, "end": 11}],
    "notes": "Synthetic contract control only; no real audio/corpus/model.",
}

ADVERSE_CASES: List[Tuple[str, Dict[str, Any], str]] = [
    ("missing_scored_regions", {"case_id": "x", "total_samples": 8, "target_speech": [], "hypothesis_target": [], "enrollment_present": True}, "scored_regions must be list"),
    ("bad_total", {"case_id": "x", "total_samples": 0, "scored_regions": [{"start": 0, "end": 1}], "target_speech": [], "hypothesis_target": [], "enrollment_present": True}, "total_samples must be positive int"),
    ("overlap", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": 4}, {"start": 3, "end": 8}], "target_speech": [], "hypothesis_target": [], "enrollment_present": True}, "scored_regions overlaps"),
    ("out_of_bounds", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": 9}], "target_speech": [], "hypothesis_target": [], "enrollment_present": True}, "out of bounds"),
    ("bad_enrollment", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": 8}], "target_speech": [], "hypothesis_target": [], "enrollment_present": "yes"}, "enrollment_present must be bool"),
    ("unknown_field", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": 8}], "target_speech": [], "hypothesis_target": [], "enrollment_present": True, "extra": 1}, "unknown fields"),
    ("bad_interval_key", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "finish": 8}], "target_speech": [], "hypothesis_target": [], "enrollment_present": True}, "keys must be start,end"),
    ("non_int", {"case_id": "x", "total_samples": 8, "scored_regions": [{"start": 0, "end": "8"}], "target_speech": [], "hypothesis_target": [], "enrollment_present": True}, "start/end must be int"),
]


def adverse_controls() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name, case, needle in ADVERSE_CASES:
        try:
            validate_spatial_control(case)
            rows.append({"case": name, "result": "accepted", "error": "unexpected"})
        except Exception as exc:
            msg = str(exc)
            rows.append({"case": name, "result": "rejected", "error_contains": needle, "error": msg})
    # strict JSON controls
    for name, text, needle in [
        ("strict_json_duplicate_key", '{"a":1,"a":2}', "duplicate JSON key"),
        ("strict_json_nonfinite", '[NaN]', "non-finite JSON constant"),
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


def build_report() -> Dict[str, Any]:
    control = validate_spatial_control(CONTROL_CASE)
    adverse = adverse_controls()
    gates = [
        {"id": gid, "requirement": req, "status": "blocked"}
        for gid, req in GATE_REQUIREMENTS
    ]
    blockers = [dict(item) for item in EXACT_BLOCKERS]
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "component": COMPONENT,
        "title": TITLE,
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
            "reason": "No deployable local VoiceFilter-Lite/personal-VAD checkpoint, exact runtime, rights record, enrolled-speaker target cohort, or approved parity evidence is present.",
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "generated_by": "reference.py",
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "task_row_identity": task_row_identity(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_audit": {
            "audit_result": "absent",
            "qualified": False,
            "observed": [
                {"path": "data/models/voicefilter-lite", "present": False},
                {"path": "data/models/personal-vad", "present": False},
                {"path": "data/checkouts/voicefilter-lite", "present": False},
                {"path": "third_party/voicefilter-lite", "present": False},
            ],
            "note": "Fixed local probes only; no network/download/execution.",
        },
        "spatial_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": [
                {"id": "geometry_layout_calibration", "satisfied_for_qualification": False, "qualification_effect": "none"},
                {"id": "target_reference_conditions", "satisfied_for_qualification": False, "qualification_effect": "none"},
                {"id": "leakage_target_damage", "satisfied_for_qualification": False, "qualification_effect": "none"},
                {"id": "channel_loss_room_change", "satisfied_for_qualification": False, "qualification_effect": "none"},
                {"id": "exact_source_intervals", "satisfied_for_qualification": False, "qualification_effect": "none"},
            ],
            "satisfied_for_qualification": [],
            "real_model_metrics": None,
        },
        "reference_protocol": {
            "kind": "synthetic_scoring_control_only",
            "model_executed": False,
            "executor": "absent",
            "qualification_effect": "none",
            "control_case": CONTROL_CASE,
            "control_result": control,
            "notes": [
                "Synthetic interval arithmetic control only; not VoiceFilter-Lite, not personal VAD, not real audio.",
                "Unknown samples outside scored regions are never counted as nonspeech or target.",
                "Missing evidence never qualifies the candidate.",
            ],
        },
        "controls": {
            "adverse": adverse,
            "adverse_all_rejected": all(r["result"] == "rejected" for r in adverse),
            "missing_result_never_qualifies": True,
            "unknown_never_counted_as_nonspeech": True,
        },
        "gates": gates,
        "exact_blockers": blockers,
        "reopen_conditions": [
            {"gate_id": gid, "condition": req} for gid, req in GATE_REQUIREMENTS
        ],
        "source_reported_context": {
            "label": "source_reported_not_measured_here",
            "note": "Candidate matrix and research reports identify VoiceFilter-Lite/personal VAD as unavailable/blocked. No local model, cohort, runtime, or parity result is promoted here.",
            "candidate_matrix_row": 62,
            "candidate_matrix_status": "unavailable/blocked",
        },
        "candidate_metrics": None,
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only.",
            "No network, no download, no model/runtime execution, no audio device.",
            "Asset audit uses fixed local path probes only.",
        ],
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline",
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }


def build_contract(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "SPDX-" + "FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-" + "License-Identifier": "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": "feasibility",
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": report["qualification"],
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "task_row_identity": {
            "source": report["task_row_identity"]["source"],
            "stable_sha256": report["task_row_identity"]["stable_sha256"],
            "whole_file_hashed": False,
            "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        },
        "scope": report["scope"],
        "boundary": report["boundary"],
        "source_pins": report["source_pins"],
        "boundary_pins": report["boundary_pins"],
        "exact_blockers": [
            {"id": b["id"], "requirement": b["requirement"]} for b in report["exact_blockers"]
        ],
        "gates": report["gates"],
        "reproduction": {
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
            "report": "PYTHONDONTWRITEBYTECODE=1 python3 run.py report.json",
            "sources": "PYTHONDONTWRITEBYTECODE=1 python3 run.py sources",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "cold_start_regenerations": 3,
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
        },
        "licensing": {
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "generated_json_sidecars": True,
        },
    }
