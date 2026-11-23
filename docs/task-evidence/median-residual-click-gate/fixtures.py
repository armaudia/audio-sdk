"""Deterministic synthetic fixtures and source pins for the click-gate evidence.

No corpus, model, download or licensed asset is used. Every sample is generated
from a fixed integer seed and a hash-derived uniform stream; the source evidence
paths are pinned by SHA-256 and verified by the task-local tests.
"""

from __future__ import annotations

import hashlib
import math
import os
from pathlib import Path
from typing import Any

import reference

DEFAULT_AUDIOML_ROOT = "/Users/htsakanyan/workspace/audio/audioml"
AUDIOML_ROOT = Path(os.environ.get("AUDIOML_ROOT", DEFAULT_AUDIOML_ROOT))
SAMPLE_RATE_HZ = reference.SAMPLE_RATE_HZ
SDK_FRAME_SAMPLES = reference.SDK_FRAME_SAMPLES
NS_PER_SAMPLE = reference.NS_PER_SAMPLE
CLICK_GRID_SAMPLES = 6400
# Declared playback-rate bound for synthetic schedule controls (+/-25%). This
# is not a target-device clock tolerance; the drift fixture itself is 250 ppm.
MAX_ABS_DRIFT_PPM = 250000

SOURCE_PINS: dict[str, dict[str, str]] = {
    "candidate_matrix": {
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "sha256": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
        "use": "Record 38: waveform gates for breaths/clicks; partially evaluated",
    },
    "realtime_candidates": {
        "path": "REALTIME_COMPONENT_CANDIDATES.md",
        "sha256": "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
        "use": "Line 95: fixed median-residual click gate; transform RTF 0.000290",
    },
    "expanded_report": {
        "path": "research/voice-enhancement-20261101/agent-click-gate-expanded/REPORT.md",
        "sha256": "b8a42f9b0b782ad3aaa0be64da0d23b37c3c54b65a31caf252a4cd2ace88841e",
        "use": "Normative detector/repair: width 7 reflect median, threshold 0.35",
    },
    "expanded_script": {
        "path": "research/voice-enhancement-20261101/agent-click-gate-expanded/expand_click_gate.py",
        "sha256": "98a9b283029f049458c513b07762943447757c17986e47cc67c80ad974cf78b2",
        "use": "Exact source of the width/amplitude stress protocol",
    },
    "initial_report": {
        "path": "research/voice-enhancement-20261101/agent-click-gate-eval/REPORT.md",
        "sha256": "ae4b0065eabbb62fe8880c7a04dee146415d463c5ae6676db6329147a901e1cc",
        "use": "Initial one-sample click screen and its limits",
    },
    "initial_script": {
        "path": "research/voice-enhancement-20261101/agent-click-gate-eval/evaluate_click_gate.py",
        "sha256": "9195ddbdf7ea20da36fcd69ff72608b0eacefcee17cad7144cafbf37e0ff82e1",
        "use": "Exact source of the threshold sweep and repair rule",
    },
    "verification_profile": {
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "sha256": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
        "use": "Rate profile: mapping, duration, pitch, transients, buffering, rate cases",
    },
    "public_adapter_descriptor": {
        "path": "adapters/controls/adapter.json",
        "sha256": "3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599",
        "use": "Public protocol-v1 envelope shape reused by the task-local descriptor",
    },
    "public_adapter_runner": {
        "path": "adapters/controls/run.py",
        "sha256": "4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66",
        "use": "Public strict JSON/request validation pattern",
    },
}


def verify_source_pins(root: Path | None = None) -> dict[str, dict[str, Any]]:
    base = root or AUDIOML_ROOT
    result: dict[str, dict[str, Any]] = {}
    for name, pin in SOURCE_PINS.items():
        path = base / pin["path"]
        if not path.is_file():
            raise FileNotFoundError(f"missing pinned source: {pin['path']}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        result[name] = {
            "path": pin["path"],
            "expected_sha256": pin["sha256"],
            "actual_sha256": actual,
            "verified": actual == pin["sha256"],
            "use": pin["use"],
        }
    return result


def _uniform_bits(seed: int, index: int) -> int:
    payload = f"median-click-gate:{seed}:{index}".encode("ascii")
    return int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")


def uniform_signed(seed: int, index: int) -> float:
    return 2.0 * (_uniform_bits(seed, index) / 18446744073709551616.0) - 1.0


def _normalize(samples: list[float], peak: float = 0.25) -> list[float]:
    maximum = max((abs(value) for value in samples), default=0.0)
    scale = peak / maximum if maximum > 0 else 1.0
    return [reference.f32(value * scale) for value in samples]


def speech_like(length: int, seed: int) -> tuple[list[float], list[bool]]:
    """Unfamiliar synthetic speech-like material: harmonic source + syllable envelope.

    This is generated here, not drawn from a corpus. Consonant-like noise bursts
    are labelled transient controls and stay below the fixed 0.35 gate threshold.
    """
    syllable = max(64, length // 4)
    f0s = (112.0, 139.0, 97.0, 124.0)
    bursts = {start: width for start, width in
              ((syllable, 8), (2 * syllable + 11, 6), (3 * syllable - 9, 7))}
    samples: list[float] = []
    transients: list[bool] = []
    for index in range(length):
        time = index / SAMPLE_RATE_HZ
        unit = index % syllable
        envelope = 0.06 + 0.94 * (0.5 - 0.5 * math.cos(2.0 * math.pi * unit / syllable))
        f0 = f0s[min(3, index // syllable)]
        jitter = 0.0015 * uniform_signed(seed + 1, index // 16)
        phase = 2.0 * math.pi * (f0 + jitter) * time
        voiced = (0.62 * math.sin(phase)
                  + 0.23 * math.sin(2.0 * phase + 0.31)
                  + 0.11 * math.sin(3.0 * phase + 0.72)
                  + 0.04 * math.sin(5.0 * phase + 1.13))
        noise = 0.006 * uniform_signed(seed + 2, index)
        burst = 0.0
        marked = False
        for start, width in bursts.items():
            if start <= index < start + width:
                burst = 0.12 * uniform_signed(seed + 3, index - start)
                marked = True
        samples.append(envelope * voiced + noise + burst)
        transients.append(marked)
    return _normalize(samples), transients


def music_like(length: int, seed: int) -> tuple[list[float], list[bool]]:
    """Synthetic music-like chord with low-amplitude percussion transients."""
    frequencies = (220.0, 277.18, 329.63)
    hits = {start: 2 for start in range(320, length, 640)}
    samples: list[float] = []
    transients: list[bool] = []
    for index in range(length):
        time = index / SAMPLE_RATE_HZ
        tone = sum(math.sin(2.0 * math.pi * value * time + 0.2 * order)
                   for order, value in enumerate(frequencies)) / len(frequencies)
        hit = 0.0
        marked = False
        for start, width in hits.items():
            if start <= index < start + width:
                hit = 0.12 * uniform_signed(seed + 5, index - start)
                marked = True
        samples.append(0.85 * tone + hit + 0.004 * uniform_signed(seed + 6, index))
        transients.append(marked)
    return _normalize(samples), transients


def inject_clicks(clean: list[float], seed: int, width: int, amplitude: float,
                  *, event_count: int = 8, spacing: int = 640,
                  start_offset: int = 173) -> tuple[list[float], list[bool]]:
    corrupted = list(clean)
    labels = [False] * len(clean)
    for event in range(event_count):
        start = start_offset + event * spacing
        if start + width >= len(clean):
            break
        sign = 1.0 if _uniform_bits(seed + 7, event) & 1 else -1.0
        for offset in range(width):
            corrupted[start + offset] = reference.f32(
                corrupted[start + offset] + sign * amplitude)
            labels[start + offset] = True
    return corrupted, labels


def _segment_duration_ns(segment: dict[str, Any]) -> int:
    samples = segment["end"] - segment["start"]
    return samples * NS_PER_SAMPLE * segment["rate_den"] // segment["rate_num"]


def make_rate_plan(kind: str, length: int) -> dict[str, Any]:
    """Piecewise-exact integer source-sample -> playback-nanosecond maps."""
    specs: list[tuple[int, int, int, int, int]]
    if kind == "constant_1x":
        specs = [(0, length, 1, 1, 0)]
    elif kind == "constant_08x":
        specs = [(0, length, 4, 5, 0)]
    elif kind == "midstream_125_080":
        boundary_a, boundary_b = length // 4, 3 * length // 4
        specs = [(0, boundary_a, 1, 1, 0),
                 (boundary_a, boundary_b, 5, 4, 0),
                 (boundary_b, length, 4, 5, 0)]
    elif kind == "rebuffer_80ms":
        boundary = length // 2
        specs = [(0, boundary, 1, 1, 0),
                 (boundary, length, 1, 1, 80_000_000)]
    elif kind == "drift_250ppm":
        specs = [(0, length, 1000250, 1000000, 0)]
    elif kind == "rate_change_partial":
        specs = [(0, 160, 1, 1, 0), (160, length, 5, 4, 0)]
    else:
        raise ValueError("unknown_rate_plan:" + kind)
    origin = 0
    segments: list[dict[str, Any]] = []
    for number, (start, end, num, den, gap) in enumerate(specs):
        origin += gap
        segment = {"start": start, "end": end, "rate_num": num, "rate_den": den,
                   "origin_ns": origin, "rebuffer_ns_before": gap,
                   "segment_index": number}
        segments.append(segment)
        origin += _segment_duration_ns(segment)
    return {"clock_id": "synthetic-source-monotonic-v1", "segments": segments}


def validate_rate_plan(plan: Any, length: int) -> dict[str, Any]:
    if not isinstance(plan, dict) or set(plan) != {"clock_id", "segments"}:
        raise ValueError("invalid_rate_plan")
    if plan["clock_id"] != "synthetic-source-monotonic-v1":
        raise ValueError("invalid_clock_domain")
    segments = plan["segments"]
    if not isinstance(segments, list) or not segments:
        raise ValueError("invalid_rate_plan")
    expected_origin = 0
    cursor = 0
    for index, segment in enumerate(segments):
        keys = {"start", "end", "rate_num", "rate_den", "origin_ns",
                "rebuffer_ns_before", "segment_index"}
        if not isinstance(segment, dict) or set(segment) != keys:
            raise ValueError("invalid_rate_plan_segment")
        if segment["segment_index"] != index or segment["start"] != cursor:
            raise ValueError("invalid_rate_plan_order")
        if not isinstance(segment["end"], int) or segment["end"] <= cursor:
            raise ValueError("invalid_rate_plan_interval")
        for name in ("rate_num", "rate_den", "origin_ns", "rebuffer_ns_before"):
            value = segment[name]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("invalid_rate_plan_" + name)
        if segment["rate_num"] == 0 or segment["rate_den"] == 0:
            raise ValueError("invalid_rate_plan_rate")
        drift_ppm = abs(1.0 - segment["rate_num"] / segment["rate_den"]) * 1_000_000.0
        if not math.isfinite(drift_ppm) or drift_ppm > MAX_ABS_DRIFT_PPM:
            raise ValueError("rate_drift_bound_exceeded")
        expected_origin += segment["rebuffer_ns_before"]
        if segment["origin_ns"] != expected_origin:
            raise ValueError("invalid_rate_plan_origin")
        expected_origin += _segment_duration_ns(segment)
        cursor = segment["end"]
    if cursor != length:
        raise ValueError("rate_plan_length_mismatch")
    return plan


def playback_time_ns(plan: dict[str, Any], source_index: int) -> int:
    validate_rate_plan(plan, plan["segments"][-1]["end"])
    for segment in plan["segments"]:
        if segment["start"] <= source_index < segment["end"]:
            delta = source_index - segment["start"]
            return segment["origin_ns"] + delta * NS_PER_SAMPLE * segment["rate_den"] // segment["rate_num"]
    if source_index == plan["segments"][-1]["end"]:
        return playback_end_ns(plan)
    raise ValueError("source_index_out_of_rate_plan")


def playback_end_ns(plan: dict[str, Any]) -> int:
    last = plan["segments"][-1]
    return last["origin_ns"] + _segment_duration_ns(last)


def rate_change_boundaries(plan: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for segment in plan["segments"]:
        if segment["start"] == 0:
            continue
        index = segment["start"]
        result.append({
            "source_sample": index,
            "source_ns": index * NS_PER_SAMPLE,
            "playback_ns": playback_time_ns(plan, index),
            "rate_num": segment["rate_num"],
            "rate_den": segment["rate_den"],
            "rebuffer_ns_before": segment["rebuffer_ns_before"],
        })
    return result


CLICK_WIDTHS = (1, 2, 3, 5)
CLICK_AMPLITUDES = (0.20, 0.40, 0.75)
CLICK_CASES = tuple(
    f"click_w{width}_a{int(amplitude * 1000):03d}"
    for width in CLICK_WIDTHS for amplitude in CLICK_AMPLITUDES)

RATE_CASES = (
    "speech_1x", "speech_rate_125_080", "music_1x", "music_rate_08",
    "silence_1x", "silence_drift", "rebuffer_speech",
    "final_partial_speech", "rate_change_partial",
)

CASE_IDS = CLICK_CASES + RATE_CASES


def build_case(case_id: str) -> dict[str, Any]:
    if case_id not in CASE_IDS:
        raise ValueError("unknown_case:" + case_id)
    if case_id in CLICK_CASES:
        width = int(case_id.split("_")[1][1:])
        amplitude = int(case_id.split("_")[2][1:]) / 1000.0
        clean, transients = speech_like(CLICK_GRID_SAMPLES, 731001)
        samples, labels = inject_clicks(clean, 731001 + width * 17 + int(amplitude * 1000),
                                        width, amplitude)
        plan = make_rate_plan("constant_1x", CLICK_GRID_SAMPLES)
        return {
            "case_id": case_id, "material": "unfamiliar speech-like synthetic + injected clicks",
            "seed": 731001, "clean": clean, "samples": samples, "labels": labels,
            "transient_labels": transients, "rate_plan": plan,
            "playback_end_ns": playback_end_ns(plan),
            "rate_change_boundaries": [],
            "note": (f"width={width} samples, amplitude=+/-{amplitude:.2f}, "
                     "isolated deterministic square pulses"),
        }

    length = CLICK_GRID_SAMPLES
    seed = 842003
    material = ""
    clean: list[float]
    transients: list[bool]
    labels: list[bool]
    plan_kind = "constant_1x"
    note = ""
    if case_id == "speech_1x":
        clean, transients = speech_like(length, seed)
        labels = [False] * length
        material = "unfamiliar speech-like synthetic"
        note = "identity playback rate; no injected clicks"
    elif case_id == "speech_rate_125_080":
        clean, transients = speech_like(length, seed)
        samples, labels = inject_clicks(clean, 842019, 1, 0.75)
        clean = samples
        plan_kind = "midstream_125_080"
        material = "unfamiliar speech-like synthetic + clicks"
        note = "1x -> 1.25x -> 0.8x playback schedule with source-timestamped boundary"
    elif case_id in ("music_1x", "music_rate_08"):
        clean, transients = music_like(length, seed + 31)
        labels = [False] * length
        plan_kind = "constant_1x" if case_id == "music_1x" else "constant_08x"
        material = "synthetic music-like chord with low-amplitude percussion transients"
        note = ("1x playback" if case_id == "music_1x" else
                "0.8x playback schedule; source-domain samples and pitch are unchanged")
    elif case_id in ("silence_1x", "silence_drift"):
        clean = [0.0] * length
        transients = [False] * length
        labels = [False] * length
        plan_kind = "constant_1x" if case_id == "silence_1x" else "drift_250ppm"
        material = "digital silence"
        note = "no content; decision count and output digests must be zero/identity"
    elif case_id == "rebuffer_speech":
        clean, transients = speech_like(length, seed)
        samples, labels = inject_clicks(clean, 842041, 1, 0.75)
        clean = samples
        plan_kind = "rebuffer_80ms"
        material = "unfamiliar speech-like synthetic + clicks + rebuffer"
        note = "80 ms rebuffer inserted at a source-timestamped boundary; no samples added or dropped"
    elif case_id == "final_partial_speech":
        length = 165
        clean, transients = speech_like(length, seed + 97)
        samples, labels = inject_clicks(clean, 842053, 1, 0.75, event_count=2,
                                        spacing=84, start_offset=17)
        clean = samples
        material = "unfamiliar speech-like synthetic final partial window"
        note = "165 valid source samples; last v0 frame has valid_count<160 and final padding"
    elif case_id == "rate_change_partial":
        length = 325
        clean, transients = speech_like(length, seed + 113)
        samples, labels = inject_clicks(clean, 842067, 1, 0.75, event_count=2,
                                        spacing=120, start_offset=29)
        clean = samples
        plan_kind = "rate_change_partial"
        material = "unfamiliar speech-like synthetic partial window with midstream 1.25x rate"
        note = "325 source samples, rate change at source sample 160, final partial window"
    else:
        raise ValueError("unhandled_case:" + case_id)

    plan = make_rate_plan(plan_kind, length)
    validate_rate_plan(plan, length)
    return {
        "case_id": case_id, "material": material, "seed": seed, "clean": clean,
        "samples": clean, "labels": labels, "transient_labels": transients,
        "rate_plan": plan, "playback_end_ns": playback_end_ns(plan),
        "rate_change_boundaries": rate_change_boundaries(plan), "note": note,
    }


def case_inputs_digest(case_id: str) -> str:
    case = build_case(case_id)
    return reference.digest_samples(case["samples"])


def aggregate_click_counts(cases: list[dict[str, Any]]) -> dict[str, Any]:
    table: dict[str, Any] = {}
    for width in CLICK_WIDTHS:
        table[str(width)] = {}
        for amplitude in CLICK_AMPLITUDES:
            key = f"w{width}_a{int(amplitude * 1000):03d}"
            rows = [case["detections"] for case in cases if case["case_id"] == "click_" + key]
            if len(rows) != 1:
                raise ValueError("missing_click_result:" + key)
            detections = rows[0]
            table[str(width)][f"{amplitude:.2f}"] = {
                "tp_samples": detections["tp_samples"],
                "fp_samples": detections["fp_samples"],
                "fn_samples": detections["fn_samples"],
                "recall": detections["recall"],
                "labeled_click_samples": detections["labeled_click_samples"],
            }
    return table
