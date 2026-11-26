# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING.

This task is blocked: exact licensed VADToolkit/AMI source, annotations,
audio, rights record, runtime, and approved parity/reference scoring outputs
are not present in this worktree. No download, no vendor/runtime execution,
no real corpus, no device timing, and no qualification claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Sequence

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml")
)

TASK = "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING"
TITLE = "VADToolkit and AMI scoring tooling"
SLUG = "vadtoolkit-and-ami-scoring-tooling"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "evidence"
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

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/plans/F02/vad_accuracy_contract.md":
        "f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec",
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

TASK_ROW_STABLE_SHA256 = (
    "2b18653e9410c4422f5e477e5fe74c54c9d88a94452927da5edac192e35b152f"
)
TASK_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "acceptance": "Apply the evidence acceptance profile; record exact scope, evidence, failure/control results, and remaining release gates.",
    "component": "vadtoolkit-and-ami-scoring-tooling",
    "deliverable": "Retain or reproduce the comparison as an optional SDK developer/evidence adapter alongside audio-bench, with a documented proceed/defer decision before exposing it as a processor. Preserve explicit scored regions and separate weak annotations from held-out accuracy references.",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "evidence": ["research/plans/F02/vad_accuracy_contract.md"],
    "id": "SDK-VADTOOLKIT-AND-AMI-SCORING-TOOLING",
    "mode": "research-control",
    "repository": "audio-sdk",
    "title": "VADToolkit and AMI scoring tooling",
    "write_scope": [
        "SDK provider, tool or evidence directory for vadtoolkit-and-ami-scoring-tooling and its own fixtures"
    ],
}

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
    "network_used": False,
    "device_timing": False,
    "listening": False,
    "public_benchmark": False,
    "release_claim": False,
    "task_local_only": True,
}

NON_CLAIMS: List[str] = [
    "No VADToolkit or AMI source, binary, annotation, audio, weight, or derived artifact is loaded, executed, staged, or redistributed.",
    "No network request, download, dataset acquisition, or external runtime invocation occurs.",
    "No real audio, real corpus, real AMI meeting, or audEERING VADToolkit recording is consumed.",
    "No VAD accuracy, miss rate, false-alarm rate, onset/offset error, latency, memory, RTF, listening, device, public benchmark, or release result is claimed.",
    "The VAD accuracy contract and audEERING dataset notes are pinned context only; they are not promoted to measured or qualified evidence.",
    "No provider, descriptor, registry, installed v0 path, shared build, CI, board, or handoff change is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER and qualification remains not_qualified.",
]

EXACT_BLOCKERS: List[Dict[str, Any]] = [
    {
        "id": "exact_source_and_revision_absent",
        "gate_ids": ["exact_source_and_asset_identity", "runtime_and_reproducibility"],
        "requirement": "Pin exact VADToolkit/AMI tooling source revisions, immutable build/command recipes, and artifact manifests for every scored component.",
        "state": "No exact VADToolkit source checkout, AMI scoring tool revision, or immutable execution manifest is present in this worktree.",
    },
    {
        "id": "exact_assets_and_labels_absent",
        "gate_ids": ["exact_source_and_asset_identity", "rights_and_publication", "matched_reference_parity"],
        "requirement": "Provide exact licensed audio, annotation, scored-region, and reference artifacts with SHA-256/byte counts and complete provenance.",
        "state": "No audEERING VADToolkit package, AMI meeting audio/labels, or rights-cleared scored-region artifacts are present locally for this task package.",
    },
    {
        "id": "rights_and_publication_uncleared",
        "gate_ids": ["rights_and_publication", "public_default_and_release"],
        "requirement": "Clear acquisition, local evaluation, publication, redistribution, and derivative-output rights with complete notices before any claim.",
        "state": "No per-asset rights record, license decision, publication/release review, or redistribution approval is present.",
    },
    {
        "id": "reference_parity_absent",
        "gate_ids": ["matched_reference_parity", "analysis_cohort_and_scoring"],
        "requirement": "Reproduce a pinned reference scoring run on frozen inputs with byte-level or explicitly-toleranced verified outputs and hashed artifacts.",
        "state": "No approved VADToolkit/AMI reference output, parity vector, or independently verified scorer reproduction exists in this package.",
    },
    {
        "id": "cohort_scored_region_absent",
        "gate_ids": ["analysis_cohort_and_scoring", "weak_label_separation"],
        "requirement": "Freeze a rights-cleared held-out cohort with explicit scored regions, unknown gaps, and separated weak/advisory labels.",
        "state": "No held-out accuracy cohort, explicit scored-region manifest, or weak-label separation record is present; unknown gaps cannot be treated as nonspeech.",
    },
    {
        "id": "runtime_execution_absent",
        "gate_ids": ["runtime_and_reproducibility", "adapter_boundary_and_isolation"],
        "requirement": "Provide an isolated pinned runtime and deterministic execution recipe for the tooling under test.",
        "state": "No isolated VADToolkit/AMI runtime, lockfile, or deterministic execution trace is staged; no runtime claim is made.",
    },
    {
        "id": "adapter_boundary_incomplete",
        "gate_ids": ["adapter_boundary_and_isolation", "opt_in_provider_intake"],
        "requirement": "Define an optional SDK developer/evidence adapter boundary that preserves installed v0 behavior and does not expose the tooling as a processor.",
        "state": "No opt-in adapter, descriptor, registry entry, provider registration, or processor exposure exists; boundary remains blocked.",
    },
    {
        "id": "public_default_release_blocked",
        "gate_ids": ["public_default_and_release"],
        "requirement": "Record explicit default-selection, resource/deadline, release, and public-benchmark approval; missing evidence cannot qualify.",
        "state": "No default, release, public benchmark, device timing, listening, or qualification approval exists; status remains not_qualified.",
    },
]

GATE_REQUIREMENTS: List[Dict[str, str]] = [
    ("exact_source_and_asset_identity", "Exact VADToolkit/AMI source revisions, commands, audio/annotation assets, hashes, byte counts, and manifests are pinned and present."),
    ("rights_and_publication", "Acquisition, local evaluation, publication, redistribution, and derivative-output rights are cleared with complete notices."),
    ("matched_reference_parity", "A pinned reference scoring run is reproduced on frozen inputs with hashed outputs and verified parity/tolerance policy."),
    ("analysis_cohort_and_scoring", "A rights-cleared held-out cohort with explicit scored regions scores miss/FAR/onset/offset using deterministic rules; unknown remains unknown."),
    ("weak_label_separation", "Weak, advisory, transcript-derived, or incomplete labels are separated from held-out accuracy references and cannot qualify alone."),
    ("runtime_and_reproducibility", "An isolated pinned runtime and deterministic command recipe reproduce the tooling outputs without network or hidden mutation."),
    ("adapter_boundary_and_isolation", "Any future SDK adapter is optional, task-local/dev-evidence only, preserves installed v0 behavior, and is not exposed as a processor."),
    ("public_default_and_release", "Explicit default-selection, resource/deadline evidence, and release/public-benchmark approval are recorded; default remains off."),
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


def _object_pairs_hook(pairs: List[tuple[str, Any]]) -> Dict[str, Any]:
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
            raise Reject("trailing data after strict JSON value")
    _walk_strict(obj)
    return obj


def _reject_constant(value: str) -> Any:
    raise Reject(f"non-finite JSON constant: {value}")


def _walk_strict(obj: Any) -> None:
    if isinstance(obj, dict):
        seen = set()
        for key, value in obj.items():
            if not isinstance(key, str):
                raise Reject("JSON object key is not a string")
            if key in seen:
                raise Reject(f"duplicate JSON key: {key}")
            seen.add(key)
            _walk_strict(value)
    elif isinstance(obj, list):
        for item in obj:
            _walk_strict(item)
    elif isinstance(obj, bool) or obj is None or isinstance(obj, str):
        return
    elif isinstance(obj, int):
        return
    elif isinstance(obj, float):
        if not math.isfinite(obj):
            raise Reject("non-finite float")
    else:
        raise Reject(f"unsupported JSON type: {type(obj).__name__}")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _reject_unknown_fields(obj: Dict[str, Any], allowed: Sequence[str], label: str) -> None:
    extra = sorted(set(obj.keys()) - set(allowed))
    if extra:
        raise Reject(f"{label} has unknown fields: {extra}")


def normalize_interval(interval: Any, label: str) -> Dict[str, int]:
    if not isinstance(interval, dict):
        raise Reject(f"{label} must be an object")
    _reject_unknown_fields(interval, ("start", "end"), label)
    start = interval.get("start")
    end = interval.get("end")
    if not isinstance(start, int) or isinstance(start, bool):
        raise Reject(f"{label}.start must be int")
    if not isinstance(end, int) or isinstance(end, bool):
        raise Reject(f"{label}.end must be int")
    if start < 0 or end <= start:
        raise Reject(f"{label} must satisfy 0 <= start < end")
    return {"start": start, "end": end}


def normalize_intervals(intervals: Any, label: str) -> List[Dict[str, int]]:
    if not isinstance(intervals, list):
        raise Reject(f"{label} must be a list")
    out = [normalize_interval(item, f"{label}[{i}]") for i, item in enumerate(intervals)]
    out.sort(key=lambda x: (x["start"], x["end"]))
    for i in range(1, len(out)):
        prev = out[i - 1]
        cur = out[i]
        if cur["start"] < prev["end"]:
            raise Reject(f"{label} overlaps at {i - 1}/{i}")
    return out


def validate_case(case: Any) -> Dict[str, Any]:
    if not isinstance(case, dict):
        raise Reject("case must be an object")
    _reject_unknown_fields(case, ("case_id", "total_samples", "scored_regions", "reference_speech", "hypothesis_speech", "weak_labels", "notes"), "case")
    case_id = case.get("case_id")
    if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", case_id):
        raise Reject("case_id invalid")
    total = case.get("total_samples")
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        raise Reject("total_samples must be positive int")
    scored = normalize_intervals(case.get("scored_regions"), "scored_regions")
    ref = normalize_intervals(case.get("reference_speech"), "reference_speech")
    hyp = normalize_intervals(case.get("hypothesis_speech"), "hypothesis_speech")
    weak = normalize_intervals(case.get("weak_labels", []), "weak_labels")
    notes = case.get("notes", "")
    if not isinstance(notes, str):
        raise Reject("notes must be string")
    for name, intervals in ("scored_regions", scored), ("reference_speech", ref), ("hypothesis_speech", hyp), ("weak_labels", weak):
        for it in intervals:
            if it["end"] > total:
                raise Reject(f"{name} interval exceeds total_samples")
    return {
        "case_id": case_id,
        "total_samples": total,
        "scored_regions": scored,
        "reference_speech": ref,
        "hypothesis_speech": hyp,
        "weak_labels": weak,
        "notes": notes,
    }


def intersect(a: List[Dict[str, int]], b: List[Dict[str, int]]) -> List[Dict[str, int]]:
    out: List[Dict[str, int]] = []
    i = j = 0
    while i < len(a) and j < len(b):
        start = max(a[i]["start"], b[j]["start"])
        end = min(a[i]["end"], b[j]["end"])
        if start < end:
            out.append({"start": start, "end": end})
        if a[i]["end"] < b[j]["end"]:
            i += 1
        elif b[j]["end"] < a[i]["end"]:
            j += 1
        else:
            i += 1
            j += 1
    return out


def subtract(regions: List[Dict[str, int]], cuts: List[Dict[str, int]]) -> List[Dict[str, int]]:
    if not regions:
        return []
    if not cuts:
        return [dict(r) for r in regions]
    out: List[Dict[str, int]] = []
    j = 0
    for region in regions:
        cur = region["start"]
        end = region["end"]
        while j < len(cuts) and cuts[j]["end"] <= cur:
            j += 1
        k = j
        while k < len(cuts) and cuts[k]["start"] < end:
            cut = cuts[k]
            if cut["start"] > cur:
                out.append({"start": cur, "end": min(cut["start"], end)})
            cur = max(cur, cut["end"])
            if cur >= end:
                break
            if cut["end"] <= end:
                k += 1
            else:
                break
        if cur < end:
            out.append({"start": cur, "end": end})
    return normalize_intervals(out, "subtract")


def total_samples(intervals: List[Dict[str, int]]) -> int:
    return sum(it["end"] - it["start"] for it in intervals)


def score_case(case: Any) -> Dict[str, Any]:
    c = validate_case(case)
    scored = c["scored_regions"]
    ref = intersect(c["reference_speech"], scored)
    hyp = intersect(c["hypothesis_speech"], scored)
    nonspeech = subtract(scored, ref)
    tp_i = intersect(ref, hyp)
    fn_i = subtract(ref, hyp)
    fp_i = intersect(nonspeech, hyp)
    tn_i = subtract(nonspeech, hyp)
    tp = total_samples(tp_i)
    fn = total_samples(fn_i)
    fp = total_samples(fp_i)
    tn = total_samples(tn_i)
    miss = None if (tp + fn) == 0 else fn / (tp + fn)
    far = None if (fp + tn) == 0 else fp / (fp + tn)
    weak_in_scored = intersect(c["weak_labels"], scored)
    weak_outside = subtract(c["weak_labels"], scored)
    scored_total = total_samples(scored)
    unknown = c["total_samples"] - scored_total
    return {
        "case_id": c["case_id"],
        "total_samples": c["total_samples"],
        "scored_samples": scored_total,
        "unknown_samples": unknown,
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "tn": tn,
        "speech_miss_rate": miss,
        "false_alarm_rate": far,
        "weak_scored_samples": total_samples(weak_in_scored),
        "weak_outside_scored_samples": total_samples(weak_outside),
        "weak_labels_never_accuracy_reference": True,
        "unknown_never_nonspeech": True,
    }


CONTROL_CASE = {
    "case_id": "synthetic-control",
    "total_samples": 16,
    "scored_regions": [{"start": 0, "end": 4}, {"start": 8, "end": 16}],
    "reference_speech": [{"start": 1, "end": 3}, {"start": 10, "end": 12}],
    "hypothesis_speech": [{"start": 2, "end": 5}, {"start": 9, "end": 11}],
    "weak_labels": [{"start": 4, "end": 8}],
    "notes": "Synthetic contract control only; no real audio/corpus.",
}

ADVERSE_CASES: List[Dict[str, Any]] = [
    {"name": "missing_total_samples", "case": {"case_id": "bad", "scored_regions": [], "reference_speech": [], "hypothesis_speech": []}},
    {"name": "non_int_total_samples", "case": {**CONTROL_CASE, "case_id": "bad1", "total_samples": "16"}},
    {"name": "zero_total_samples", "case": {**CONTROL_CASE, "case_id": "bad2", "total_samples": 0}},
    {"name": "overlapping_scored_regions", "case": {**CONTROL_CASE, "case_id": "bad3", "scored_regions": [{"start": 0, "end": 5}, {"start": 4, "end": 8}]}},
    {"name": "inverted_interval", "case": {**CONTROL_CASE, "case_id": "bad4", "reference_speech": [{"start": 5, "end": 2}]}},
    {"name": "out_of_bounds", "case": {**CONTROL_CASE, "case_id": "bad5", "hypothesis_speech": [{"start": 15, "end": 17}]}},
    {"name": "boolean_interval", "case": {**CONTROL_CASE, "case_id": "bad6", "reference_speech": [{"start": False, "end": 2}]}},
    {"name": "unknown_field", "case": {**CONTROL_CASE, "case_id": "bad7", "extra": 1}},
    {"name": "bad_case_id", "case": {**CONTROL_CASE, "case_id": "Bad ID"}},
    {"name": "notes_not_string", "case": {**CONTROL_CASE, "case_id": "bad8", "notes": 1}},
    {"name": "weak_labels_overlap", "case": {**CONTROL_CASE, "case_id": "bad9", "weak_labels": [{"start": 1, "end": 3}, {"start": 2, "end": 4}]}},
    {"name": "interval_not_object", "case": {**CONTROL_CASE, "case_id": "bad10", "scored_regions": [1]}},
]

ABSENCE_PROBES = [
    ("source_root", "data/datasets/audeering-vadtoolkit"),
    ("source_root", "data/datasets/audeering-vadtoolkit/benchmark-v1"),
    ("source_root", "data/datasets/ami"),
    ("source_root", "data/checkouts/vadtoolkit"),
    ("source_root", "data/checkouts/VADToolkit"),
    ("source_root", "data/models/vadtoolkit"),
    ("source_root", "research/vadtoolkit"),
    ("worktree", "third_party/vadtoolkit"),
    ("worktree", "third_party/ami"),
    ("worktree", "tools/vadtoolkit"),
    ("worktree", "tools/ami-scoring"),
]


def _root_for(name: str) -> Path:
    if name == "source_root":
        return SOURCE_ROOT
    if name == "worktree":
        return SDK_ROOT
    raise Reject(f"unknown root {name}")


def audit_assets() -> Dict[str, Any]:
    observed = []
    for root_name, rel in ABSENCE_PROBES:
        path = _root_for(root_name) / rel
        observed.append({
            "root": root_name,
            "path": rel,
            "present": path.exists(),
        })
    return {
        "audit_result": "absent" if not any(x["present"] for x in observed) else "present",
        "qualified": False,
        "observed": observed,
    }


def run_adverse_controls() -> List[Dict[str, Any]]:
    results = []
    for item in ADVERSE_CASES:
        try:
            score_case(item["case"])
        except Reject as exc:
            results.append({"case": item["name"], "result": "rejected", "error": str(exc)})
        else:
            results.append({"case": item["name"], "result": "accepted"})
    try:
        strict_loads('{"a":1,"a":2}')
    except Reject as exc:
        results.append({"case": "strict_json_duplicate_key", "result": "rejected", "error": str(exc)})
    else:
        results.append({"case": "strict_json_duplicate_key", "result": "accepted"})
    try:
        strict_loads('{"x":NaN}')
    except Reject as exc:
        results.append({"case": "strict_json_nonfinite", "result": "rejected", "error": str(exc)})
    else:
        results.append({"case": "strict_json_nonfinite", "result": "accepted"})
    return results


def task_row_identity() -> Dict[str, Any]:
    return {
        "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "stable_fields": dict(TASK_ROW_STABLE_FIELDS),
        "stable_sha256": TASK_ROW_STABLE_SHA256,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "whole_file_hashed": False,
    }


def build_report() -> Dict[str, Any]:
    control = score_case(CONTROL_CASE)
    adverse = run_adverse_controls()
    gates = [{"id": gid, "requirement": req, "status": "blocked"} for gid, req in GATE_REQUIREMENTS]
    blocked_ids = [g["id"] for g in gates]
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
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
            "blocked_gate_count": len(gates),
            "blocked_gate_ids": blocked_ids,
            "reason": "Exact VADToolkit/AMI source, licensed audio/annotations/scored regions, rights/publication clearance, pinned runtime, parity outputs, and held-out scoring evidence are absent.",
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "task_row_identity": task_row_identity(),
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "non_claims": list(NON_CLAIMS),
        "exact_blockers": [dict(x) for x in EXACT_BLOCKERS],
        "gates": gates,
        "reopen_conditions": [{"gate_id": g["id"], "condition": g["requirement"]} for g in gates],
        "asset_audit": audit_assets(),
        "reference_protocol": {
            "kind": "synthetic_scoring_control_only",
            "model_executed": False,
            "executor": "absent",
            "qualification_effect": "none",
            "control_case": CONTROL_CASE,
            "control_result": control,
            "notes": [
                "Synthetic interval arithmetic control only; not VADToolkit, not AMI, not real audio.",
                "Unknown samples outside scored regions are never counted as nonspeech.",
                "Weak/advisory labels are reported separately and never qualify accuracy.",
            ],
        },
        "controls": {
            "adverse_all_rejected": all(x["result"] == "rejected" for x in adverse),
            "adverse": adverse,
            "unknown_never_counted_as_nonspeech": control["unknown_never_nonspeech"],
            "weak_labels_never_accuracy_reference": control["weak_labels_never_accuracy_reference"],
            "missing_result_never_qualifies": True,
        },
        "source_reported_context": {
            "label": "source_reported_not_measured_here",
            "note": "vad_accuracy_contract.md is pinned as planning/context evidence only. It reports audEERING VADToolkit as staged but not full-accuracy qualified; no local dataset/runtime/parity evidence is promoted here.",
        },
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline",
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
        "tool_provenance": [
            "Python standard library only.",
            "No network, no download, no model/runtime execution, no audio device.",
            "Asset audit uses fixed local path probes only.",
        ],
    }


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report)
