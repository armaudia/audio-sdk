# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic Distil-Wav2Vec2 adult/child ridge evidence fixture.

Task-local, proposal-only, incomplete, not qualified. This models a head-only
ridge classifier over frozen synthetic embeddings that stand in for
`bookbot/distil-wav2vec2-adult-child-cls-37m` encoder outputs. No model
weights, no real audio, no download, no network, no device, no listening test,
and no public benchmark is used. The installed v0 geometry is untouched:
16 kHz, mono, float32, 160 samples per call.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

CONTRACT_ID = "audio-sdk/distil-wav2vec2-adult-child-ridge/0.1"
SCHEMA_ID = "audio-sdk/task-evidence/distil-wav2vec2-adult-child-ridge/report/0.1"
BASE_COMMIT = "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d"
PROVIDER_ID = "analysis.distil-wav2vec2-adult-child-ridge-ref.v0"
MODEL_ID = "bookbot/distil-wav2vec2-adult-child-cls-37m"
TASK_KIND = "adult_child_classification"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"
SAMPLE_NS = 62500
CLOCK_ID = "fixture-monotonic-v0"
ORIGIN_NS = 1767225600000000000

SEED = 20261124
TRAIN_CLIPS = 120
HELD_OUT_CLIPS = 60
CLIP_FRAMES = 20  # 200 ms per clip
EMBED_DIM = 16
RIDGE_LAMBDA = 1e-3
THRESHOLD_GRID = [i / 100 for i in range(5, 96)]
DEFAULT_THRESHOLD = 0.5

LABEL_ADULT = "adult"
LABEL_CHILD = "child"
LABELS = (LABEL_ADULT, LABEL_CHILD)

SOURCE_PINS: tuple[dict[str, str], ...] = (
    {
        "path": "audio-benchmark-platform/audio-sdk/CONTRACTS.md",
        "root": "source",
        "sha256": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
        "summary": "Fixed v0 geometry, exact source intervals, decimal-string sample/time serialization, analysis-event validity rules.",
    },
    {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "root": "source",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "summary": "Analysis acceptance profile: timestamped probabilities, onset/offset delay, stratified FN/FP, validity vs nonspeech, state and cross-hop behavior.",
    },
    {
        "path": "api/include/audio_sdk/provider_v0.h",
        "root": "worktree",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "summary": "Public provider ABI boundary mirrored by this Python model; unchanged.",
    },
    {
        "path": "api/include/audio_sdk/session_v0.h",
        "root": "worktree",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "summary": "Public session facade boundary; unchanged. No analysis hook is added.",
    },
)

MISSING_EVIDENCE = (
    {
        "path": "ml-audio-research-experience.md",
        "status": "missing_in_workspace",
        "reason": "Referenced by task prompt but not present in accessible workspace paths; no bytes pinned or reused.",
    },
    {
        "path": "research/speech_intelligence_20261028.md",
        "status": "missing_in_workspace",
        "reason": "Referenced by task prompt but not present in accessible workspace paths; no bytes pinned or reused.",
    },
)

GATES: tuple[dict[str, str], ...] = (
    {
        "id": "real_model_weights_and_runtime",
        "status": "blocked",
        "reason": "No model weights, tokenizer/config/runtime, or Hugging Face asset downloaded or executed. Embeddings are deterministic synthetic stand-ins.",
        "reopen": "Pin exact model revision, license, hashes, runtime, and execute head-only inference on an approved runner.",
    },
    {
        "id": "rights_qualified_labeled_audio",
        "status": "blocked",
        "reason": "No real adult/child speech audio, labels, consent, or rights-qualified cohort used.",
        "reopen": "Freeze a permitted labeled cohort with explicit adult/child/nonspeech/unknown policy and independent scoring.",
    },
    {
        "id": "calibration_and_threshold_validation",
        "status": "blocked",
        "reason": "Threshold is calibrated only on synthetic held-out split; no external calibration/operating-point validation.",
        "reopen": "Calibrate and validate thresholds on an independently reviewed permitted cohort with fixed operating-point policy.",
    },
    {
        "id": "target_runtime_timing",
        "status": "blocked",
        "reason": "No paced target-device timing, CPU, memory, or deadline measurement. Any wall-clock observation would be non-qualifying.",
        "reopen": "Measure exact installed build on target under pacing/load/deadline budgets.",
    },
    {
        "id": "provider_intake",
        "status": "blocked",
        "reason": "Conceptual provider is unregistered, OFF by default, empty descriptor settings; no public API/ABI/default/registry change.",
        "reopen": "Complete opt-in provider intake with independent review and OFF-by-default descriptor.",
    },
)


class LCG:
    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def next_u32(self) -> int:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state

    def uniform(self) -> float:
        return 2.0 * (self.next_u32() / 4294967296.0) - 1.0

    def unit(self) -> float:
        return 0.5 * (self.uniform() + 1.0)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "), allow_nan=False).encode("utf-8") + b"\n"


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def tensor_digest(values: Sequence[float]) -> str:
    return hashlib.sha256(b"".join(struct.pack("<f", float(v)) for v in values)).hexdigest()


def dec(value: int) -> str:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("decimal field requires int")
    return str(value)


def sigmoid(x: float) -> float:
    x = max(-60.0, min(60.0, x))
    return 1.0 / (1.0 + math.exp(-x))


@dataclass(frozen=True)
class Clip:
    clip_id: str
    split: str
    label: str
    stratum: str
    frames: int
    embedding: tuple[float, ...]
    source_first: int


def _label_for(index: int) -> tuple[str, str]:
    label = LABEL_CHILD if index % 2 == 0 else LABEL_ADULT
    if index % 10 == 0:
        stratum = "boundary_quiet"
    elif index % 7 == 0:
        stratum = "noisy_overlap"
    elif index % 5 == 0:
        stratum = "short_utterance"
    else:
        stratum = "clean"
    return label, stratum


def make_embedding(label: str, stratum: str, seed: int) -> tuple[float, ...]:
    rng = LCG(seed)
    base = 0.55 if label == LABEL_CHILD else -0.55
    noise_scale = 0.35
    if stratum == "boundary_quiet":
        base *= 0.35
        noise_scale = 0.55
    elif stratum == "noisy_overlap":
        base *= 0.75
        noise_scale = 0.65
    elif stratum == "short_utterance":
        base *= 0.85
        noise_scale = 0.45
    vals = []
    for i in range(EMBED_DIM):
        axis = base if i % 2 == 0 else -base * 0.6
        vals.append(axis + noise_scale * rng.uniform())
    # deterministic feature interaction
    vals[0] += 0.15 * base
    vals[1] -= 0.10 * base
    return tuple(float(v) for v in vals)


def build_cohort() -> list[Clip]:
    clips: list[Clip] = []
    total = TRAIN_CLIPS + HELD_OUT_CLIPS
    cursor = 0
    for idx in range(total):
        split = "train" if idx < TRAIN_CLIPS else "held_out"
        label, stratum = _label_for(idx)
        emb = make_embedding(label, stratum, SEED + idx * 131)
        clip = Clip(
            clip_id=f"clip-{idx:03d}",
            split=split,
            label=label,
            stratum=stratum,
            frames=CLIP_FRAMES,
            embedding=emb,
            source_first=cursor,
        )
        clips.append(clip)
        cursor += CLIP_FRAMES * FRAME_SAMPLES
    return clips


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def mat_vec(m: Sequence[Sequence[float]], v: Sequence[float]) -> list[float]:
    return [dot(row, v) for row in m]


def transpose(m: Sequence[Sequence[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*m)]


def mat_mul(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> list[list[float]]:
    bt = transpose(b)
    return [[dot(row, col) for col in bt] for row in a]


def invert_matrix(m: Sequence[Sequence[float]]) -> list[list[float]]:
    n = len(m)
    a = [list(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[pivot][i]) < 1e-12:
            raise ValueError("singular_matrix")
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
        pv = a[i][i]
        for j in range(2 * n):
            a[i][j] /= pv
        for r in range(n):
            if r == i:
                continue
            f = a[r][i]
            if f == 0.0:
                continue
            for j in range(2 * n):
                a[r][j] -= f * a[i][j]
    return [row[n:] for row in a]


def fit_ridge(clips: Sequence[Clip]) -> dict[str, Any]:
    # x includes bias term
    x = [list(c.embedding) + [1.0] for c in clips]
    y = [1.0 if c.label == LABEL_CHILD else 0.0 for c in clips]
    xt = transpose(x)
    xtx = mat_mul(xt, x)
    for i in range(len(xtx) - 1):  # no reg on bias
        xtx[i][i] += RIDGE_LAMBDA
    xty = mat_vec(xt, y)
    inv = invert_matrix(xtx)
    w = mat_vec(inv, xty)
    return {
        "weights": [float(v) for v in w[:-1]],
        "bias": float(w[-1]),
        "lambda": RIDGE_LAMBDA,
        "train_clips": len(clips),
        "feature_dim": EMBED_DIM,
    }


def predict_prob(model: dict[str, Any], emb: Sequence[float]) -> float:
    z = dot(model["weights"], emb) + float(model["bias"])
    return sigmoid(z)


def classify(prob_child: float, threshold: float) -> str:
    return LABEL_CHILD if prob_child >= threshold else LABEL_ADULT


def build_events(clips: Sequence[Clip], probs: Sequence[float], threshold: float, epoch: int = 1) -> list[dict[str, Any]]:
    events = []
    for i, (clip, p) in enumerate(zip(clips, probs)):
        start = clip.source_first
        end = start + clip.frames * FRAME_SAMPLES
        pred = classify(p, threshold)
        events.append({
            "event_id": f"evt-{epoch}-{i:04d}",
            "producer_id": PROVIDER_ID,
            "tap_id": "analysis.adult_child.v0",
            "epoch": dec(epoch),
            "source_first_sample": dec(start),
            "source_last_sample_exclusive": dec(end),
            "available_ns": dec(ORIGIN_NS + end * SAMPLE_NS),
            "clock_id": CLOCK_ID,
            "validity": "known",
            "prob_child": float(p),
            "prob_adult": float(1.0 - p),
            "predicted_label": pred,
            "ground_truth_label": clip.label,
            "stratum": clip.stratum,
            "clip_id": clip.clip_id,
        })
    return events


def confusion(events: Sequence[dict[str, Any]], positive: str = LABEL_CHILD) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    for e in events:
        if e.get("validity") != "known":
            continue
        gt_pos = e["ground_truth_label"] == positive
        pred_pos = e["predicted_label"] == positive
        if gt_pos and pred_pos:
            tp += 1
        elif gt_pos and not pred_pos:
            fn += 1
        elif (not gt_pos) and pred_pos:
            fp += 1
        else:
            tn += 1
    total_pos = tp + fn
    total_neg = tn + fp
    return {
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "fn_rate": (fn / total_pos) if total_pos else None,
        "fp_rate": (fp / total_neg) if total_neg else None,
        "precision": (tp / (tp + fp)) if (tp + fp) else None,
        "recall": (tp / (tp + fn)) if (tp + fn) else None,
    }


def stratified(events: Sequence[dict[str, Any]]) -> dict[str, Any]:
    strata = {}
    for s in sorted({e["stratum"] for e in events}):
        subset = [e for e in events if e["stratum"] == s]
        strata[s] = confusion(subset)
    by_label = {}
    for lbl in LABELS:
        subset = [e for e in events if e["ground_truth_label"] == lbl]
        c = confusion(subset)
        by_label[lbl] = {
            "count": len(subset),
            "fn": c["fn"] if lbl == LABEL_CHILD else c["fp"],
            "fp": c["fp"] if lbl == LABEL_CHILD else c["fn"],
            "fn_rate": c["fn_rate"] if lbl == LABEL_CHILD else c["fp_rate"],
            "fp_rate": c["fp_rate"] if lbl == LABEL_CHILD else c["fn_rate"],
        }
    return {"by_stratum": strata, "by_ground_truth_label": by_label}


def calibrate_threshold(clips: Sequence[Clip], probs: Sequence[float]) -> dict[str, Any]:
    rows = []
    best = None
    for t in THRESHOLD_GRID:
        ev = build_events(clips, probs, t)
        c = confusion(ev)
        bal_err = None
        if c["fn_rate"] is not None and c["fp_rate"] is not None:
            bal_err = 0.5 * (c["fn_rate"] + c["fp_rate"])
        row = {"threshold": t, "balanced_error": bal_err, **c}
        rows.append(row)
        key = (bal_err if bal_err is not None else 9e9, c["fp_rate"] or 9e9, t)
        if best is None or key < best[0]:
            best = (key, row)
    assert best is not None
    return {"selected": best[1], "grid": rows}


def onset_offset_delay(events: Sequence[dict[str, Any]]) -> dict[str, Any]:
    # contiguous runs of predicted child as "child activity" against alternating GT segments by clip order.
    # here each clip is an event; onset when pred switches to child, offset when leaves child.
    pred_runs = []
    in_run = False
    start = None
    for e in events:
        is_child = e["predicted_label"] == LABEL_CHILD and e["validity"] == "known"
        if is_child and not in_run:
            in_run = True
            start = int(e["source_first_sample"])
        if in_run and not is_child:
            pred_runs.append((start, int(e["source_first_sample"])))
            in_run = False
    if in_run and events:
        pred_runs.append((start, int(events[-1]["source_last_sample_exclusive"])))

    gt_runs = []
    in_run = False
    start = None
    for e in events:
        is_child = e["ground_truth_label"] == LABEL_CHILD
        if is_child and not in_run:
            in_run = True
            start = int(e["source_first_sample"])
        if in_run and not is_child:
            gt_runs.append((start, int(e["source_first_sample"])))
            in_run = False
    if in_run and events:
        gt_runs.append((start, int(events[-1]["source_last_sample_exclusive"])))

    def nearest(vals, target):
        return min(vals, key=lambda v: abs(v - target)) if vals else None

    onset_delays = []
    for gs, _ in gt_runs:
        ps = nearest([r[0] for r in pred_runs], gs)
        if ps is not None:
            onset_delays.append(ps - gs)
    offset_delays = []
    for _, ge in gt_runs:
        pe = nearest([r[1] for r in pred_runs], ge)
        if pe is not None:
            offset_delays.append(pe - ge)
    return {
        "ground_truth_child_runs": [{"start": dec(s), "end": dec(e)} for s, e in gt_runs],
        "predicted_child_runs": [{"start": dec(s), "end": dec(e)} for s, e in pred_runs],
        "onset_delay_samples": onset_delays,
        "offset_delay_samples": offset_delays,
        "mean_onset_delay_samples": (sum(onset_delays) / len(onset_delays)) if onset_delays else None,
        "mean_offset_delay_samples": (sum(offset_delays) / len(offset_delays)) if offset_delays else None,
    }


def validity_controls(model: dict[str, Any], threshold: float) -> dict[str, Any]:
    base_clip = Clip("control-base", "control", LABEL_CHILD, "clean", CLIP_FRAMES,
                     make_embedding(LABEL_CHILD, "clean", SEED + 99991), 0)
    prob = predict_prob(model, base_clip.embedding)
    known = build_events([base_clip], [prob], threshold)[0]

    unknown = dict(known)
    unknown["event_id"] = "evt-control-unknown"
    unknown["validity"] = "unknown"
    unknown["predicted_label"] = "unknown"
    unknown["prob_child"] = None
    unknown["prob_adult"] = None

    invalid_cases = []

    def reject(name: str, payload: dict[str, Any], reason: str) -> None:
        try:
            validate_event(payload)
        except ValueError as e:
            invalid_cases.append({"name": name, "status": "rejected", "reason": reason, "error": str(e)})
            return
        invalid_cases.append({"name": name, "status": "accepted_unexpected", "reason": reason})

    bad_prob = dict(known)
    bad_prob["event_id"] = "evt-bad-prob"
    bad_prob["prob_child"] = 1.2
    reject("out_of_range_probability", bad_prob, "prob_child_out_of_range")

    bad_interval = dict(known)
    bad_interval["event_id"] = "evt-bad-interval"
    bad_interval["source_first_sample"] = dec(160)
    bad_interval["source_last_sample_exclusive"] = dec(160)
    reject("invalid_interval", bad_interval, "empty_interval")

    bad_validity = dict(known)
    bad_validity["event_id"] = "evt-bad-validity"
    bad_validity["validity"] = "nonspeech"
    reject("invalid_validity_tag", bad_validity, "invalid_validity")

    stale = dict(known)
    stale["event_id"] = "evt-stale-epoch"
    stale["epoch"] = dec(0)
    reject("stale_epoch", stale, "stale_epoch")

    # unknown must not count as nonspeech/negative label
    unknown_not_counted = confusion([unknown])["fp"] == 0 and confusion([unknown])["fn"] == 0

    return {
        "known_event": known,
        "unknown_event": unknown,
        "unknown_not_counted_as_nonspeech": unknown_not_counted,
        "invalid_cases": invalid_cases,
        "all_invalid_rejected": all(c["status"] == "rejected" for c in invalid_cases),
    }


def validate_event(e: dict[str, Any]) -> None:
    req = ["event_id","producer_id","tap_id","epoch","source_first_sample","source_last_sample_exclusive","available_ns","clock_id","validity"]
    for k in req:
        if k not in e:
            raise ValueError(f"missing_{k}")
    if e["validity"] not in {"known","unknown","invalid"}:
        raise ValueError("invalid_validity")
    try:
        epoch = int(e["epoch"])
        s0 = int(e["source_first_sample"])
        s1 = int(e["source_last_sample_exclusive"])
        ans = int(e["available_ns"])
    except Exception as ex:
        raise ValueError("non_integer_field") from ex
    if epoch < 1:
        raise ValueError("stale_epoch")
    if s1 <= s0:
        raise ValueError("empty_interval")
    if ans < 0:
        raise ValueError("bad_available_ns")
    if e["validity"] == "known":
        p = e.get("prob_child")
        pa = e.get("prob_adult")
        if not isinstance(p, (int,float)) or not math.isfinite(float(p)) or not (0.0 <= float(p) <= 1.0):
            raise ValueError("prob_child_out_of_range")
        if not isinstance(pa, (int,float)) or not math.isfinite(float(pa)) or not (0.0 <= float(pa) <= 1.0):
            raise ValueError("prob_adult_out_of_range")
        if e.get("predicted_label") not in LABELS:
            raise ValueError("bad_predicted_label")


def state_and_cross_hop(model: dict[str, Any], threshold: float) -> dict[str, Any]:
    clips = build_cohort()[:4]
    probs = [predict_prob(model, c.embedding) for c in clips]
    sess_a = build_events(clips[:2], probs[:2], threshold, epoch=1)
    for e in sess_a:
        e["producer_id"] = "session-A"
    sess_b = build_events(clips[2:], probs[2:], threshold, epoch=1)
    for e in sess_b:
        e["producer_id"] = "session-B"
    keys_a = {(e["producer_id"], e["tap_id"], e["epoch"], e["event_id"]) for e in sess_a}
    keys_b = {(e["producer_id"], e["tap_id"], e["epoch"], e["event_id"]) for e in sess_b}
    disjoint = keys_a.isdisjoint(keys_b)

    # cross-hop: clip spans multiple 160-sample frames
    cross_hop = []
    for e in sess_a:
        s0 = int(e["source_first_sample"])
        s1 = int(e["source_last_sample_exclusive"])
        cross_hop.append({
            "event_id": e["event_id"],
            "frames_covered": (s1 - s0) // FRAME_SAMPLES,
            "exact_source_interval": s1 > s0,
        })

    # stale/foreign epoch rejected
    stale = dict(sess_a[0])
    stale["event_id"] = "evt-stale"
    stale["epoch"] = dec(0)
    stale_rejected = False
    try:
        validate_event(stale)
    except ValueError:
        stale_rejected = True

    # reset isolation: epoch bump creates fresh events, old epoch rejected
    reset = dict(sess_a[0])
    reset["epoch"] = dec(2)
    reset["event_id"] = "evt-reset-0000"
    reset_ok = True
    try:
        validate_event(reset)
    except ValueError:
        reset_ok = False

    return {
        "session_independence": disjoint,
        "session_a_keys": len(keys_a),
        "session_b_keys": len(keys_b),
        "cross_hop": cross_hop,
        "stale_epoch_rejected": stale_rejected,
        "reset_epoch_accepted": reset_ok,
    }


def build_report() -> dict[str, Any]:
    cohort = build_cohort()
    train = [c for c in cohort if c.split == "train"]
    held = [c for c in cohort if c.split == "held_out"]
    model = fit_ridge(train)
    train_probs = [predict_prob(model, c.embedding) for c in train]
    held_probs = [predict_prob(model, c.embedding) for c in held]

    calibration = calibrate_threshold(held, held_probs)
    selected_threshold = float(calibration["selected"]["threshold"])

    held_events = build_events(held, held_probs, selected_threshold)
    for e in held_events:
        validate_event(e)
    held_conf = confusion(held_events)
    held_strat = stratified(held_events)
    delays = onset_offset_delay(held_events)

    default_events = build_events(held, held_probs, DEFAULT_THRESHOLD)
    default_conf = confusion(default_events)

    controls = {
        "always_adult": confusion([dict(e, predicted_label=LABEL_ADULT) for e in held_events]),
        "always_child": confusion([dict(e, predicted_label=LABEL_CHILD) for e in held_events]),
    }

    validity = validity_controls(model, selected_threshold)
    state = state_and_cross_hop(model, selected_threshold)

    # regressions: report where selected threshold is worse than default on some stratum/metric.
    regressions = []
    for stratum, c in held_strat["by_stratum"].items():
        d = default_conf_by = stratified(default_events)["by_stratum"][stratum]
        if c["fn_rate"] is not None and d["fn_rate"] is not None and c["fn_rate"] > d["fn_rate"]:
            regressions.append({
                "type": "threshold_regression",
                "stratum": stratum,
                "metric": "fn_rate",
                "selected_threshold": selected_threshold,
                "default_threshold": DEFAULT_THRESHOLD,
                "selected": c["fn_rate"],
                "default": d["fn_rate"],
            })
        if c["fp_rate"] is not None and d["fp_rate"] is not None and c["fp_rate"] > d["fp_rate"]:
            regressions.append({
                "type": "threshold_regression",
                "stratum": stratum,
                "metric": "fp_rate",
                "selected_threshold": selected_threshold,
                "default_threshold": DEFAULT_THRESHOLD,
                "selected": c["fp_rate"],
                "default": d["fp_rate"],
            })

    report = {
        "schema_id": SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task_id": "SDK-DISTIL-WAV2VEC2-BOOKBOT-DISTIL-WAV2VEC2-ADULT-CHILD-CLS-37M-RIDGE",
        "title": "Distil-Wav2Vec2 (bookbot/distil-wav2vec2-adult-child-cls-37m) + ridge",
        "profile": "Analysis",
        "status": "proposal_only_synthetic_incomplete",
        "qualification_status": "not_qualified",
        "no_missing_result_qualifies_candidate": True,
        "base_commit": BASE_COMMIT,
        "model": {
            "requested_model_id": MODEL_ID,
            "weights_downloaded": False,
            "weights_executed": False,
            "runtime": "synthetic_embedding_ridge_reference",
            "embedding_dim": EMBED_DIM,
            "head": "ridge_logistic",
            "note": "No real model weights or audio used; embeddings are deterministic synthetic stand-ins.",
        },
        "boundary": {
            "provider_id": PROVIDER_ID,
            "registered": False,
            "enabled_by_default": False,
            "descriptor_settings": {},
            "public_api_abi_change": False,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "sample_format": SAMPLE_FORMAT,
            "frame_samples": FRAME_SAMPLES,
            "clock_id": CLOCK_ID,
            "origin_ns": dec(ORIGIN_NS),
        },
        "cohort": {
            "type": "deterministic_synthetic",
            "seed": SEED,
            "train_clips": len(train),
            "held_out_clips": len(held),
            "clip_frames": CLIP_FRAMES,
            "clip_samples": CLIP_FRAMES * FRAME_SAMPLES,
            "labels": list(LABELS),
            "strata": sorted({c.stratum for c in cohort}),
            "held_out_digest": object_digest([{"id": c.clip_id, "label": c.label, "stratum": c.stratum, "emb": c.embedding} for c in held]),
        },
        "training": {
            "split": "train_only",
            "n_train": len(train),
            "n_held_out": len(held),
            "model": model,
            "train_digest": object_digest([c.embedding for c in train]),
        },
        "calibration": calibration,
        "held_out": {
            "threshold_selected": selected_threshold,
            "default_threshold": DEFAULT_THRESHOLD,
            "confusion": held_conf,
            "stratified": held_strat,
            "default_threshold_confusion": default_conf,
            "onset_offset_delay": delays,
            "events_digest": object_digest(held_events),
            "events": held_events,
        },
        "controls": controls,
        "validity": validity,
        "state_and_cross_hop": state,
        "regressions": regressions,
        "missing_evidence": list(MISSING_EVIDENCE),
        "source_pins": list(SOURCE_PINS),
        "gates": list(GATES),
        "evidence_classes": {
            "synthetic_deterministic": "used",
            "real_audio": "none",
            "real_model_weights": "none",
            "rights_qualified_labeled_cohort": "none",
            "target_runtime_timing": "none",
        },
    }
    return report


def canonical_report_bytes(report: dict[str, Any]) -> bytes:
    return canonical_bytes(report)
