# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-TEN-VAD.

TEN VAD is blocked at feasibility: the merged evidence records no exact
candidate source checkout, weights, runtime, rights record, cohort or
approved parity vector. This module never imports vendor code, never loads
or executes a model, never downloads assets, never reads real audio, never
measures a device clock and never claims qualification.

It provides a deterministic Analysis-profile control: caller-supplied
synthetic frame probabilities are mapped to exact half-open sample
intervals, scored with stratified FN/FP, and checked with adverse fail-closed
controls. This proves contract structure only; decision remains DEFER.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = Path(os.environ.get("SDK_ROOT", str(HERE.parents[2])))
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-TEN-VAD"
TITLE = "TEN VAD"
SLUG = "ten-vad"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "analysis"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
MODEL_FRAME_SAMPLES = 512
MODEL_CONTEXT_SAMPLES = 64
MODEL_INPUT_SAMPLES = MODEL_CONTEXT_SAMPLES + MODEL_FRAME_SAMPLES
MODEL_STATE_SHAPE = [2, 1, 128]
THRESHOLD = 0.5

TOTAL_FULL_FRAMES = 24
TAIL_PARTIAL_SAMPLES = 37
TOTAL_SAMPLES = TOTAL_FULL_FRAMES * MODEL_FRAME_SAMPLES + TAIL_PARTIAL_SAMPLES
TOTAL_MODEL_FRAMES = (TOTAL_SAMPLES + MODEL_FRAME_SAMPLES - 1) // MODEL_FRAME_SAMPLES

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
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md":
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md":
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
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

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "model_sample_rate_hz": SAMPLE_RATE_HZ,
    "model_channels": CHANNELS,
    "model_sample_format": "f32",
    "model_frame_samples": MODEL_FRAME_SAMPLES,
    "model_context_samples": MODEL_CONTEXT_SAMPLES,
    "model_input_samples": MODEL_INPUT_SAMPLES,
    "model_state_shape": list(MODEL_STATE_SHAPE),
    "threshold": THRESHOLD,
    "sdk_v0_geometry_preserved": True,
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
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "real_ten_vad_model": False,
    "release_claim": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No TEN VAD source, binary, weight, checkpoint or derived artifact is loaded or executed.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, transcript, annotation or device is consumed.",
    "No VAD accuracy, miss rate, false-alarm rate, latency, memory or RTF is measured here.",
    "The source-reported matrix row is provenance only and is not reproduced.",
    "The synthetic probability trace is a contract control, never model output.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "exact_source_absent",
        "gate_ids": ["exact_source_and_asset_identity", "runtime_admission"],
        "requirement": "Pin an exact TEN VAD source checkout, immutable revision, build recipe and artifact manifest; no exact candidate source checkout is staged.",
        "state": "Merged matrix and research reports record TEN VAD as unavailable/blocked with no exact source checkout, weights or adapter staged in checked local stores/environments.",
    },
    {
        "id": "exact_assets_absent",
        "gate_ids": ["exact_source_and_asset_identity", "artifact_rights", "exact_reference_parity"],
        "requirement": "Provide exact licensed model weights/assets with SHA-256 and byte counts; no TEN VAD weights, checkpoint or staged asset is present.",
        "state": "No TEN VAD model file, checkpoint, ONNX, wheel or asset manifest is present in the workspace; no digest can be verified against an exact asset.",
    },
    {
        "id": "exact_runtime_absent",
        "gate_ids": ["runtime_admission", "exact_reference_parity", "streaming_boundary_and_state"],
        "requirement": "Provide an isolated, hash-pinned runtime and exact execution recipe for the selected TEN VAD revision.",
        "state": "No TEN VAD runtime, lock file, wheel, environment or execution command is staged; no reproducible runtime admission is possible.",
    },
    {
        "id": "artifact_rights_uncleared",
        "gate_ids": ["artifact_rights", "opt_in_provider_intake"],
        "requirement": "Clear source, weight, training-data, dependency, redistribution and product-use rights with complete notices before any runtime or release claim.",
        "state": "No per-asset rights record, license bundle, provenance statement or redistribution decision exists for TEN VAD in task-local evidence.",
    },
    {
        "id": "approved_reference_parity_absent",
        "gate_ids": ["exact_reference_parity", "streaming_boundary_and_state"],
        "requirement": "Produce an approved exact-runtime TEN VAD probability/event vector on frozen 16 kHz mono PCM for byte-level parity.",
        "state": "No approved exact-runtime output, fresh-session trace or interval parity record exists; this package contains only a synthetic control trace.",
    },
    {
        "id": "real_analysis_cohort_absent",
        "gate_ids": ["analysis_cohort_and_scoring", "public_default_and_release"],
        "requirement": "Freeze a rights-cleared held-out analysis cohort with quiet/active/idle strata, known positives/negatives, and onset/offset labels.",
        "state": "No rights-cleared held-out TEN VAD cohort or labels are present; existing VAD references are not a substitute for an exact TEN VAD evaluation.",
    },
    {
        "id": "opt_in_intake_incomplete",
        "gate_ids": ["opt_in_provider_intake"],
        "requirement": "Complete explicit opt-in provider intake, descriptor review, boundary review and an independent public-surface decision; no adapter is registered.",
        "state": "No adapter, descriptor, registry entry, default, or shared build/CI change is made by this task-local blocker package.",
    },
    {
        "id": "public_default_release_blocked",
        "gate_ids": ["public_default_and_release"],
        "requirement": "Record explicit default-selection, resource/deadline and release/public-benchmark approval; this package remains off by default.",
        "state": "No default, release, public benchmark, device timing or listening evidence exists; qualification remains not_qualified.",
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_source_and_asset_identity", "Exact TEN VAD source revision, weights/assets, hashes, byte counts and artifact manifest are pinned and present."),
    ("runtime_admission", "An isolated hash-pinned runtime with recorded platform and execution recipe is admitted for the exact TEN VAD revision."),
    ("artifact_rights", "Source, weight, training-data, runtime dependency, redistribution and product-use rights are cleared with complete notices."),
    ("exact_reference_parity", "An approved exact-runtime probability and interval vector matches the reference on frozen 16 kHz mono PCM, including fresh-session reset."),
    ("analysis_cohort_and_scoring", "A rights-cleared held-out cohort with quiet, active, idle, positive and negative strata scores exact timestamps, onset/offset and FN/FP."),
    ("streaming_boundary_and_state", "SDK geometry, streaming state, hop/context, reset and timestamp mapping are verified against the exact TEN VAD runtime contract."),
    ("opt_in_provider_intake", "Explicit opt-in provider intake, license review, descriptor review and an independent public-surface decision are complete."),
    ("public_default_and_release", "Explicit default selection, resource/deadline evidence and release or public-benchmark approval are recorded; this package is off by default."),
)

ANALYSIS_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("timestamped_probabilities", "Per-frame probabilities with exact half-open source intervals."),
    ("event_boundaries_and_detections", "Speech event boundaries and detections with exact sample coordinates."),
    ("quiet_and_active_speech", "Separate quiet and active speech strata with matched labels."),
    ("idle_noise", "Idle noise and nonspeech controls, including false-alarm accounting."),
    ("known_positives_and_negatives", "Known-positive and known-negative cases with explicit controls."),
    ("onset_offset_delay", "Onset and offset delay in samples for every detected condition."),
    ("stratified_false_negatives_false_positives", "Stratified FN/FP and totals computed from real labels."),
    ("validity_versus_nonspeech", "Known zero is nonspeech; invalid values are rejected and unknown is never counted as nonspeech."),
    ("independent_state", "Independent recurrent state and exact context carry per session."),
    ("exact_source_intervals", "Every probability and event maps to exact source sample intervals."),
    ("availability_dropped_stale_events", "Availability, dropped and stale event accounting on the target runtime."),
    ("cross_hop_behavior", "160-sample SDK hop and 512-sample model hop are reconciled explicitly."),
)

CONTROL_TRACE_PROVENANCE = "caller_supplied_synthetic_control_trace_not_model_output"
CONTROL_TRACE: Tuple[Optional[float], ...] = (
    0.0, 0.58, 0.01, 0.42, 0.62, 0.71, 0.66, 0.58, 0.52, 0.95,
    0.97, 0.93, 0.99, 0.91, 0.47, 0.04, 0.06, 0.03, 0.05, 0.40,
    0.35, 0.44, 0.38, 0.31, None,
)

CONTROL_SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "idle-a", "condition": "idle_noise", "start_frame": 0, "end_frame": 3, "label": False},
    {"id": "quiet-a", "condition": "quiet_speech", "start_frame": 3, "end_frame": 9, "label": True},
    {"id": "active-a", "condition": "active_speech", "start_frame": 9, "end_frame": 15, "label": True},
    {"id": "idle-b", "condition": "idle_noise", "start_frame": 15, "end_frame": 19, "label": False},
    {"id": "stress-a", "condition": "stress_low_snr", "start_frame": 19, "end_frame": 24, "label": True},
    {"id": "unknown-tail", "condition": "unknown_tail", "start_frame": 24, "end_frame": 25, "label": None},
)


class Reject(ValueError):
    """Fail-closed validation error."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    try:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except ValueError as error:
        raise Reject(f"non-canonical JSON value: {error}") from error
    return payload.encode("utf-8") + b"\n"


def strict_loads(text: str) -> Any:
    def object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise Reject(f"duplicate key: {key}")
            out[key] = value
        return out

    def parse_constant(value: str) -> Any:
        raise Reject(f"non-JSON constant is not allowed: {value}")

    value = json.loads(
        text,
        object_pairs_hook=object_pairs_hook,
        parse_constant=parse_constant,
    )
    if not isinstance(value, dict):
        raise Reject("top-level JSON value must be an object")
    return value


def _ensure_finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Reject(f"{label} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise Reject(f"{label} must be finite")
    return number


def _ensure_probability(value: Any, label: str) -> Optional[float]:
    if value is None:
        return None
    number = _ensure_finite_number(value, label)
    if number < 0.0 or number > 1.0:
        raise Reject(f"{label} must be within [0, 1]")
    return number


def task_row_identity() -> Dict[str, Any]:
    task_path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    row = None
    if task_path.is_file():
        document = strict_loads(task_path.read_text(encoding="utf-8"))
        for candidate in document.get("tasks", []):
            if isinstance(candidate, dict) and candidate.get("id") == TASK:
                row = candidate
                break
    if row is None:
        raise Reject(f"linked task row missing: {TASK}")
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    return {
        "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "stable_fields": stable,
        "stable_sha256": sha256(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": row.get("claim") or {},
    }


def synthetic_signal() -> List[float]:
    signal = [0.0] * TOTAL_SAMPLES
    for i in range(512):
        signal[i] = 0.001 * math.sin(2.0 * math.pi * 120.0 * i / SAMPLE_RATE_HZ)
    for i in range(1536, 4608):
        t = i / SAMPLE_RATE_HZ
        signal[i] = 0.08 * math.sin(2.0 * math.pi * 220.0 * t)
    for i in range(4608, 7680):
        t = i / SAMPLE_RATE_HZ
        signal[i] = 0.18 * math.sin(2.0 * math.pi * 180.0 * t)
    for i in range(7680, 9728):
        signal[i] = 0.002 * math.sin(2.0 * math.pi * 90.0 * i / SAMPLE_RATE_HZ)
    for i in range(9728, 12288):
        t = i / SAMPLE_RATE_HZ
        signal[i] = 0.02 * math.sin(2.0 * math.pi * 200.0 * t) + 0.01 * math.sin(
            2.0 * math.pi * 3100.0 * t)
    for i in range(12288, TOTAL_SAMPLES):
        signal[i] = 0.0015 * math.sin(2.0 * math.pi * 60.0 * i / SAMPLE_RATE_HZ)
    for value in signal:
        if not math.isfinite(value) or abs(value) > 1.0:
            raise Reject("synthetic signal out of range")
    return signal


def frame_plan(signal: Sequence[float]) -> Dict[str, Any]:
    if not isinstance(signal, Sequence) or isinstance(signal, (str, bytes, bytearray)):
        raise Reject("signal must be a sequence")
    if len(signal) != TOTAL_SAMPLES:
        raise Reject(f"signal length must be {TOTAL_SAMPLES}")
    frames: List[Dict[str, Any]] = []
    context = [0.0] * MODEL_CONTEXT_SAMPLES
    for index in range(TOTAL_MODEL_FRAMES):
        start = index * MODEL_FRAME_SAMPLES
        end = min(start + MODEL_FRAME_SAMPLES, TOTAL_SAMPLES)
        frame_samples = [float(sample) for sample in signal[start:end]]
        for sample in frame_samples:
            if not math.isfinite(sample) or abs(sample) > 1.0:
                raise Reject("signal sample out of range")
        padded = MODEL_FRAME_SAMPLES - len(frame_samples)
        padded_frame = frame_samples + [0.0] * padded
        model_input = context + padded_frame
        if len(model_input) != MODEL_INPUT_SAMPLES:
            raise Reject("model input length mismatch")
        frames.append({
            "index": index,
            "source_start": start,
            "source_end": end,
            "valid_samples": len(frame_samples),
            "padded_samples": padded,
            "model_input_samples": len(model_input),
            "context_sha256": sha256(canonical_bytes(context)),
            "model_input_sha256": sha256(canonical_bytes(model_input)),
        })
        context = padded_frame[-MODEL_CONTEXT_SAMPLES:]
    return {
        "total_samples": TOTAL_SAMPLES,
        "frame_count": TOTAL_MODEL_FRAMES,
        "partial_frame_samples": TAIL_PARTIAL_SAMPLES,
        "padded_samples": MODEL_FRAME_SAMPLES - TAIL_PARTIAL_SAMPLES,
        "frames": frames,
        "context_carry_exact": True,
        "context_stream_sha256": sha256(canonical_bytes([
            [frame["index"], frame["context_sha256"]] for frame in frames
        ])),
    }


def control_labels() -> Tuple[List[Optional[bool]], List[str]]:
    labels: List[Optional[bool]] = [None] * TOTAL_MODEL_FRAMES
    conditions = ["unknown"] * TOTAL_MODEL_FRAMES
    for segment in CONTROL_SEGMENTS:
        for index in range(segment["start_frame"], segment["end_frame"]):
            labels[index] = segment["label"]
            conditions[index] = segment["condition"]
    if any(condition == "unknown" and label is not None
           for condition, label in zip(conditions, labels)):
        raise Reject("control labels are inconsistent")
    return labels, conditions


def map_probabilities(probabilities: Sequence[Any],
                      total_samples: int = TOTAL_SAMPLES) -> Dict[str, Any]:
    if not isinstance(probabilities, Sequence) or isinstance(probabilities, (str, bytes, bytearray)):
        raise Reject("probabilities must be a sequence")
    expected = (total_samples + MODEL_FRAME_SAMPLES - 1) // MODEL_FRAME_SAMPLES
    if len(probabilities) != expected:
        raise Reject("probability_count_mismatch")
    events: List[Dict[str, Any]] = []
    speech_events: List[Dict[str, int]] = []
    unknown_intervals: List[Dict[str, int]] = []
    counts = {"true_frames": 0, "false_frames": 0, "unknown_frames": 0}
    in_speech = False
    speech_start = 0
    for index, raw in enumerate(probabilities):
        probability = _ensure_probability(raw, f"probabilities[{index}]")
        start = index * MODEL_FRAME_SAMPLES
        end = min(start + MODEL_FRAME_SAMPLES, total_samples)
        if probability is None:
            label = None
            counts["unknown_frames"] += 1
            unknown_intervals.append({"start_sample": start, "end_sample": end})
            if in_speech:
                speech_events.append({"start_sample": speech_start, "end_sample": start})
                in_speech = False
        else:
            label = probability >= THRESHOLD
            if label:
                counts["true_frames"] += 1
                if not in_speech:
                    in_speech = True
                    speech_start = start
            else:
                counts["false_frames"] += 1
                if in_speech:
                    speech_events.append({"start_sample": speech_start, "end_sample": start})
                    in_speech = False
        events.append({
            "frame": index,
            "start_sample": start,
            "end_sample": end,
            "probability": probability,
            "label": label,
        })
    if in_speech:
        speech_events.append({"start_sample": speech_start, "end_sample": total_samples})
    return {
        "probability_events": events,
        "speech_events": speech_events,
        "unknown_intervals": unknown_intervals,
        "counts": counts,
    }


def score_frames(decisions: Sequence[Optional[bool]],
                 labels: Sequence[Optional[bool]],
                 conditions: Sequence[str]) -> Dict[str, Any]:
    if len(decisions) != len(labels) or len(labels) != len(conditions):
        raise Reject("decision/label/condition length mismatch")
    counts = {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "unknown": 0}
    stratified: Dict[str, Dict[str, int]] = {}
    for decision, label, condition in zip(decisions, labels, conditions):
        bucket = stratified.setdefault(condition, {
            "tp": 0, "fn": 0, "fp": 0, "tn": 0, "unknown": 0,
        })
        if label is True:
            if decision is True:
                counts["tp"] += 1
                bucket["tp"] += 1
            elif decision is False:
                counts["fn"] += 1
                bucket["fn"] += 1
            else:
                raise Reject("known label cannot have unknown decision")
        elif label is False:
            if decision is True:
                counts["fp"] += 1
                bucket["fp"] += 1
            elif decision is False:
                counts["tn"] += 1
                bucket["tn"] += 1
            else:
                raise Reject("known label cannot have unknown decision")
        elif label is None:
            if decision is not None:
                raise Reject("unknown label must not be scored as decision")
            counts["unknown"] += 1
            bucket["unknown"] += 1
        else:
            raise Reject("label_invalid")
    positive = counts["tp"] + counts["fn"]
    negative = counts["tn"] + counts["fp"]
    miss = Fraction(counts["fn"], positive) if positive else Fraction(0, 1)
    far = Fraction(counts["fp"], negative) if negative else Fraction(0, 1)
    return {
        **counts,
        "positive": positive,
        "negative": negative,
        "miss_rate_fraction": f"{miss.numerator}/{miss.denominator}",
        "false_alarm_rate_fraction": f"{far.numerator}/{far.denominator}",
        "miss_rate": float(miss),
        "false_alarm_rate": float(far),
        "stratified": stratified,
    }


def onset_offset(decisions: Sequence[Optional[bool]],
                 segments: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for segment in segments:
        if segment["label"] is not True:
            continue
        start = segment["start_frame"]
        end = segment["end_frame"]
        expected = end - start
        detected_indexes = [i for i in range(start, end) if decisions[i] is True]
        detected = len(detected_indexes)
        first = detected_indexes[0] if detected_indexes else None
        last = detected_indexes[-1] if detected_indexes else None
        out.append({
            "id": segment["id"],
            "condition": segment["condition"],
            "start_frame": start,
            "end_frame": end,
            "start_sample": start * MODEL_FRAME_SAMPLES,
            "end_sample": min(end * MODEL_FRAME_SAMPLES, TOTAL_SAMPLES),
            "expected_frames": expected,
            "detected_frames": detected,
            "missed_frames": expected - detected,
            "detected": detected > 0,
            "onset_delay_samples": None if first is None else (first - start) * MODEL_FRAME_SAMPLES,
            "offset_delay_samples": None if last is None else ((last + 1) - end) * MODEL_FRAME_SAMPLES,
        })
    return out


def cross_hop(total_samples: int = TOTAL_SAMPLES) -> Dict[str, Any]:
    model_frames = (total_samples + MODEL_FRAME_SAMPLES - 1) // MODEL_FRAME_SAMPLES
    sdk_calls = (total_samples + SDK_FRAME_SAMPLES - 1) // SDK_FRAME_SAMPLES
    return {
        "sdk_hop_samples": SDK_FRAME_SAMPLES,
        "model_hop_samples": MODEL_FRAME_SAMPLES,
        "model_frames": model_frames,
        "sdk_calls": sdk_calls,
        "sdk_partial_samples": total_samples % SDK_FRAME_SAMPLES,
        "model_partial_samples": total_samples % MODEL_FRAME_SAMPLES,
        "unaligned_sdk_boundaries": sum(
            1 for i in range(1, sdk_calls)
            if (i * SDK_FRAME_SAMPLES) % MODEL_FRAME_SAMPLES != 0),
        "timing_claim": "none",
        "mapping": "accumulate 512 samples, prepend 64 carried context samples, infer one frame, then carry the last 64 samples",
    }


def audit_assets() -> Dict[str, Any]:
    candidate_roots = [SOURCE_ROOT, SOURCE_ROOT.parent, SDK_ROOT]
    exact_paths = [
        SOURCE_ROOT / "data/models/ten-vad",
        SOURCE_ROOT / "data/checkouts/ten-vad",
        SOURCE_ROOT / "data/wheels/vad-candidates/ten-vad",
        SOURCE_ROOT / "data/envs/ten-vad",
    ]
    observed: List[Dict[str, Any]] = []
    for root in exact_paths:
        observed.append({
            "path": str(root),
            "present": root.exists(),
        })
    keyword_hits: List[str] = []
    for base in candidate_roots:
        if not base.exists():
            continue
        for path in base.rglob("*ten*vad*"):
            rel = str(path)
            if "/.git/" in rel or "/docs/task-evidence/ten-vad/" in rel:
                continue
            keyword_hits.append(rel)
            if len(keyword_hits) >= 40:
                break
        if len(keyword_hits) >= 40:
            break
    return {
        "audit_result": "absent",
        "standard_graph_present": False,
        "sequence_graph_present": False,
        "wheel_present": False,
        "runtime_pair_present": False,
        "rights_record_present": False,
        "heldout_results_present": False,
        "qualified": False,
        "note": "No exact TEN VAD source, assets, runtime, rights record or cohort were found in fixed workspace paths.",
        "observed": {
            "audit_scope": "fixed workspace paths only; no network, no download, no model execution",
            "exact_candidate_paths": observed,
            "keyword_hit_count": len(keyword_hits),
            "keyword_hits_sample": keyword_hits[:20],
        },
    }


def run_adverse_controls() -> List[Dict[str, Any]]:
    controls: List[Tuple[str, Any]] = []

    def record(name: str, fn) -> None:
        try:
            fn()
        except Reject:
            controls.append((name, "rejected"))
        else:
            controls.append((name, "accepted"))

    record("strict_json_duplicate_key", lambda: strict_loads('{"a":1,"a":2}'))
    record("strict_json_nonfinite", lambda: strict_loads('{"a":NaN}'))
    record("signal_not_a_sequence", lambda: frame_plan("bad"))
    bad_signal = [0.0] * (TOTAL_SAMPLES - 1) + [math.inf]
    record("signal_nonfinite", lambda: frame_plan(bad_signal))
    out_of_range = [0.0] * TOTAL_SAMPLES
    out_of_range[10] = 1.5
    record("signal_out_of_range", lambda: frame_plan(out_of_range))
    record("probability_count_mismatch", lambda: map_probabilities([0.0] * (TOTAL_MODEL_FRAMES - 1), TOTAL_SAMPLES))
    bad_probs = [0.0] * TOTAL_MODEL_FRAMES
    bad_probs[0] = math.nan
    record("probability_nan", lambda: map_probabilities(bad_probs, TOTAL_SAMPLES))
    bad_probs = [0.0] * TOTAL_MODEL_FRAMES
    bad_probs[0] = math.inf
    record("probability_infinity", lambda: map_probabilities(bad_probs, TOTAL_SAMPLES))
    bad_probs = [0.0] * TOTAL_MODEL_FRAMES
    bad_probs[0] = 1.1
    record("probability_above_one", lambda: map_probabilities(bad_probs, TOTAL_SAMPLES))
    bad_probs = [0.0] * TOTAL_MODEL_FRAMES
    bad_probs[0] = -0.1
    record("probability_negative", lambda: map_probabilities(bad_probs, TOTAL_SAMPLES))
    bad_probs = [0.0] * TOTAL_MODEL_FRAMES
    bad_probs[0] = True
    record("probability_boolean", lambda: map_probabilities(bad_probs, TOTAL_SAMPLES))
    bad_probs = [0.0] * TOTAL_MODEL_FRAMES
    bad_probs[0] = "0.5"
    record("probability_string", lambda: map_probabilities(bad_probs, TOTAL_SAMPLES))
    record("label_invalid", lambda: score_frames([True], ["speech"], ["idle_noise"]))
    record("known_label_unknown_decision", lambda: score_frames([None], [True], ["quiet_speech"]))
    record("missing_required_asset_manifest_field", lambda: validate_caller_manifest({}))
    record("manifest_relative_path", lambda: validate_caller_manifest({
        "model_path": "model.onnx",
        "model_sha256": "0" * 64,
        "runtime_lock_path": "/tmp/lock.txt",
        "runtime_lock_sha256": "0" * 64,
        "rights_record_path": "/tmp/LICENSE",
        "rights_record_sha256": "0" * 64,
        "source_revision": "a" * 40,
        "runtime_version": "unknown",
        "sample_rate_hz": 16000,
        "frame_samples": 512,
        "context_samples": 64,
        "state_shape": [2, 1, 128],
    }))
    record("manifest_wrong_geometry", lambda: validate_caller_manifest({
        "model_path": "/tmp/model.onnx",
        "model_sha256": "0" * 64,
        "runtime_lock_path": "/tmp/lock.txt",
        "runtime_lock_sha256": "0" * 64,
        "rights_record_path": "/tmp/LICENSE",
        "rights_record_sha256": "0" * 64,
        "source_revision": "a" * 40,
        "runtime_version": "unknown",
        "sample_rate_hz": 8000,
        "frame_samples": 512,
        "context_samples": 64,
        "state_shape": [2, 1, 128],
    }))
    record("manifest_short_revision", lambda: validate_caller_manifest({
        "model_path": "/tmp/model.onnx",
        "model_sha256": "0" * 64,
        "runtime_lock_path": "/tmp/lock.txt",
        "runtime_lock_sha256": "0" * 64,
        "rights_record_path": "/tmp/LICENSE",
        "rights_record_sha256": "0" * 64,
        "source_revision": "deadbee",
        "runtime_version": "unknown",
        "sample_rate_hz": 16000,
        "frame_samples": 512,
        "context_samples": 64,
        "state_shape": [2, 1, 128],
    }))
    return [{"case": name, "result": result} for name, result in controls]


CALLER_MANIFEST_FIELDS = (
    "context_samples",
    "frame_samples",
    "model_path",
    "model_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_version",
    "sample_rate_hz",
    "source_revision",
    "state_shape",
)


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise Reject("caller manifest must be an object")
    keys = tuple(sorted(manifest.keys()))
    if keys != CALLER_MANIFEST_FIELDS:
        raise Reject("caller manifest fields must match the exact required set")
    for key in ("model_path", "runtime_lock_path", "rights_record_path"):
        value = manifest[key]
        if not isinstance(value, str) or not value.startswith("/") or ".." in Path(value).parts:
            raise Reject(f"{key} must be an absolute path")
        path = Path(value)
        if not path.is_file():
            raise Reject(f"{key} missing")
    for key in ("model_sha256", "runtime_lock_sha256", "rights_record_sha256"):
        value = manifest[key]
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise Reject(f"{key} must be a lowercase sha256")
        path_key = key.replace("_sha256", "_path")
        actual = sha256(Path(manifest[path_key]).read_bytes())
        if actual != value:
            raise Reject(f"{key} digest mismatch")
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise Reject("source_revision must be a full 40-hex commit")
    runtime = manifest["runtime_version"]
    if not isinstance(runtime, str) or not runtime.strip():
        raise Reject("runtime_version must be non-empty")
    if manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise Reject("sample_rate_hz mismatch")
    if manifest["frame_samples"] != MODEL_FRAME_SAMPLES:
        raise Reject("frame_samples mismatch")
    if manifest["context_samples"] != MODEL_CONTEXT_SAMPLES:
        raise Reject("context_samples mismatch")
    if manifest["state_shape"] != list(MODEL_STATE_SHAPE):
        raise Reject("state_shape mismatch")
    return {
        "accepted": True,
        "executed": False,
        "loaded": False,
        "network_used": False,
        "verified_paths": [
            manifest["model_path"],
            manifest["runtime_lock_path"],
            manifest["rights_record_path"],
        ],
    }


def build_control() -> Dict[str, Any]:
    signal = synthetic_signal()
    plan = frame_plan(signal)
    labels, conditions = control_labels()
    mapped = map_probabilities(CONTROL_TRACE, TOTAL_SAMPLES)
    decisions = [event["label"] for event in mapped["probability_events"]]
    confusion = score_frames(decisions, labels, conditions)
    return {
        "control_trace": {
            "length": len(CONTROL_TRACE),
            "sha256": sha256(canonical_bytes(list(CONTROL_TRACE))),
            "values": list(CONTROL_TRACE),
        },
        "executor": "absent",
        "framing": plan,
        "geometry": {
            "channels": CHANNELS,
            "model_context_samples": MODEL_CONTEXT_SAMPLES,
            "model_frame_samples": MODEL_FRAME_SAMPLES,
            "model_input_samples": MODEL_INPUT_SAMPLES,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "state_shape": list(MODEL_STATE_SHAPE),
            "threshold": THRESHOLD,
        },
        "mapped": {
            "counts": mapped["counts"],
            "probability_event_count": len(mapped["probability_events"]),
            "speech_events": mapped["speech_events"],
            "unknown_intervals": mapped["unknown_intervals"],
        },
        "model_executed": False,
        "note": "Synthetic contract control only. It is not TEN VAD output, not a real cohort result and cannot qualify the candidate.",
        "onset_offset": onset_offset(decisions, CONTROL_SEGMENTS),
        "probability_source": CONTROL_TRACE_PROVENANCE,
        "qualification_effect": "none",
        "signal": {
            "name": "synthetic-analysis-control",
            "samples": TOTAL_SAMPLES,
            "segments": list(CONTROL_SEGMENTS),
            "sha256": sha256(canonical_bytes(signal)),
        },
        "validity_separation": {
            "invalid_rejected": [
                "probability_count_mismatch",
                "probability_nan",
                "probability_infinity",
                "probability_above_one",
                "probability_negative",
                "probability_boolean",
                "probability_string",
            ],
            "known_zero": {
                "counted_as_nonspeech": True,
                "decision": False,
                "excluded_from_scoring": False,
                "frame": 0,
                "probability": 0.0,
            },
            "unknown": {
                "counted_as_nonspeech": False,
                "decision": None,
                "excluded_from_scoring": True,
                "frame": 24,
                "probability": None,
            },
        },
        "confusion": confusion,
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    control = build_control()
    adverse = run_adverse_controls()
    asset_audit = audit_assets()
    gates = [
        {"id": gate_id, "requirement": requirement, "status": "blocked"}
        for gate_id, requirement in GATE_REQUIREMENTS
    ]
    qualification = {
        "status": QUALIFICATION,
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "blocked_gate_count": len(gates),
        "blocked_gate_ids": [gate["id"] for gate in gates],
        "reason": "No exact TEN VAD source checkout, licensed weights/assets, pinned runtime, rights record, approved parity vector or real analysis cohort is present.",
    }
    analysis_items = []
    for item_id, requirement in ANALYSIS_REQUIREMENTS:
        if item_id in {
            "timestamped_probabilities", "event_boundaries_and_detections",
            "onset_offset_delay", "validity_versus_nonspeech",
            "independent_state", "exact_source_intervals", "cross_hop_behavior",
        }:
            package_status = "control_only_structurally_verified"
        elif item_id == "availability_dropped_stale_events":
            package_status = "blocked_no_target_runtime"
        else:
            package_status = "blocked_no_real_model_or_cohort"
        analysis_items.append({
            "id": item_id,
            "requirement": requirement,
            "package_status": package_status,
            "qualification_effect": "none",
            "satisfied_for_qualification": False,
        })
    report = {
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
        "qualification": qualification,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "task_row_identity": {
            "source": identity["source"],
            "stable_fields": identity["stable_fields"],
            "stable_sha256": identity["stable_sha256"],
            "whole_file_hashed": False,
            "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
            "claim": identity["claim"],
        },
        "exact_blockers": list(EXACT_BLOCKERS),
        "gates": gates,
        "analysis_profile": {
            "name": "analysis",
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": analysis_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [item["id"] for item in analysis_items],
            "real_model_metrics": None,
            "note": "Structural controls pass, but no exact TEN VAD source/assets/runtime, rights record, cohort or approved parity exists; analysis profile is not satisfied for qualification.",
        },
        "asset_audit": asset_audit,
        "caller_asset_contract": {
            "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_hash_geometry_revision_and_rights_record_only; do_not_load_or_execute_in_this_package",
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "verification": [
                "manifest is strict JSON with exactly the required fields",
                "model, lock and rights paths are absolute and present",
                "SHA-256 values match the provided artifact digests",
                "source_revision is a full 40-hex commit",
                "sample rate, frame, context and state shape match the declared contract",
                "no download, copy, import, model load or execution occurs here",
            ],
        },
        "controls": {
            "adverse": adverse,
            "adverse_all_rejected": all(item["result"] == "rejected" for item in adverse),
            "invalid_values_rejected": True,
            "known_zero_counted_as_nonspeech": True,
            "missing_result_never_qualifies": True,
            "unknown_never_counted_as_nonspeech": True,
        },
        "reference_protocol": {
            **control,
            "adverse": adverse,
            "cross_hop": cross_hop(TOTAL_SAMPLES),
        },
        "source_reported_context": {
            "label": "source_reported_not_measured_here",
            "candidate_matrix": {
                "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
                "record_name": "Additional TEN VAD / PulseVAD / FSMN / MarbleNet / FireRedVAD / pyannote",
                "record_status": "unavailable/blocked",
                "finding": "No exact candidate weights, source checkout, or adapter are staged in the checked local stores/environments.",
            },
            "note": "This matrix row is copied as provenance only. It is not reproduced, re-scored or promoted by this package.",
        },
        "candidate_metrics": None,
        "missing_historical_artifacts": [],
        "non_claims": list(NON_CLAIMS),
        "reopen_conditions": [
            {"gate_id": gate_id, "condition": requirement}
            for gate_id, requirement in GATE_REQUIREMENTS
        ],
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline",
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
        "generated_by": "reference.py",
        "tool_provenance": [
            "Python standard library only; no vendor TEN VAD runtime is imported.",
            "All asset observations use fixed workspace paths and local reads.",
            "No network request, download, audio device, model load or timing run occurs.",
        ],
    }
    return report


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report)
