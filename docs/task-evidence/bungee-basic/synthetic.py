# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic synthetic PCM and analysis for the task-local Bungee reference.

No recorded speech, music, corpus, model or real audio is read. All stimuli are
analytic; every pitch/transient value is a numeric proxy, never a listening or
release claim.
"""

from __future__ import annotations

import hashlib
import math
import struct
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

RATE = 16_000
LENGTH = 16_003
MARKERS = (2_000, 5_000, 8_000, 11_000, 13_000)
CHUNK_CYCLE = (160, 240, 80)
RATE_CHANGES = ((0, "1"), (4_800, "0.8"), (9_600, "1.25"), (12_960, "1"))
CONSTANT_CASES = (("identity_1x", "1"), ("slower_0p8", "0.8"),
                  ("faster_1p25", "1.25"), ("faster_1p5", "1.5"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def round_half_up(value: Fraction) -> int:
    """Match C++ std::round for nonnegative values."""
    return math.floor(value + Fraction(1, 2))


def speed(speed_text: str) -> Fraction:
    return Fraction(speed_text)


def schedule_at(schedule: tuple[tuple[int, str], ...], source: int) -> str:
    result = schedule[0][1]
    for start, value in schedule:
        if source >= start:
            result = value
        else:
            break
    return result


def target_at(schedule: tuple[tuple[int, str], ...], source: int) -> int:
    """Cumulative source/output clock with rounding only at chunk boundaries."""
    total = Fraction(0)
    for index, (start, rate) in enumerate(schedule):
        if source <= start:
            break
        end = schedule[index + 1][0] if index + 1 < len(schedule) else source
        total += Fraction(min(end, source) - start, 1) / speed(rate)
    return round_half_up(total)


def chunk_sizes(length: int) -> list[int]:
    result = []
    consumed = 0
    index = 0
    while consumed < length:
        chunk = min(length - consumed, CHUNK_CYCLE[index % len(CHUNK_CYCLE)])
        result.append(chunk)
        consumed += chunk
        index += 1
    return result


def triangle(index: int, period: int = 40) -> float:
    # Binary-exact; no platform libm at zero crossings.
    return (period - 4 * abs(index % period - period // 2)) / 64


def stimulus(length: int = LENGTH) -> list[float]:
    if length <= max(MARKERS):
        raise ValueError("length must cover every marker")
    samples = [triangle(i) for i in range(length)]
    for marker in MARKERS:
        samples[marker] += 0.5
    if any(not math.isfinite(value) for value in samples):
        raise ValueError("nonfinite synthetic stimulus")
    return samples


def write_wav(path: Path, samples: list[float], rate: int = RATE) -> None:
    data = b"".join(struct.pack("<f", value) for value in samples)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI", b"RIFF", 36 + len(data), b"WAVE", b"fmt ", 16,
        3, 1, rate, rate * 4, 4, 32, b"data", len(data))
    path.write_bytes(header + data)


def read_wav(path: Path) -> list[float]:
    raw = path.read_bytes()
    if len(raw) < 44 or raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError(f"not RIFF/WAVE: {path}")
    position = 12
    data = b""
    while position + 8 <= len(raw):
        chunk_id = raw[position:position + 4]
        (length,) = struct.unpack("<I", raw[position + 4:position + 8])
        position += 8
        body = raw[position:position + length]
        if len(body) != length:
            raise ValueError(f"truncated WAV chunk: {path}")
        if chunk_id == b"fmt ":
            fmt, channels, rate, byte_rate, block_align, bits = struct.unpack(
                "<HHIIHH", body[:16])
            if (fmt, channels, rate, byte_rate, block_align, bits) != (
                    3, 1, RATE, RATE * 4, 4, 32):
                raise ValueError(f"unexpected WAV geometry: {path}")
        elif chunk_id == b"data":
            data = body
        position += length + (length & 1)
    if len(data) % 4:
        raise ValueError("truncated float32 WAV")
    return list(struct.unpack(f"<{len(data) // 4}f", data))


def crossings(samples: list[float]) -> int:
    return sum(a <= 0 < b for a, b in pairwise(samples))


def autocorr_period(samples: list[float], begin: int, end: int) -> int:
    """F0 proxy from normalized autocorrelation on a marker-free tone window."""
    window = samples[begin:end]
    if len(window) < 1024:
        raise ValueError("pitch window too short")
    best_lag, best_score = 0, float("-inf")
    for lag in range(24, 65):
        left = window[:len(window) - lag]
        right = window[lag:]
        numerator = sum(a * b for a, b in zip(left, right))
        energy = math.sqrt(sum(a * a for a in left) * sum(b * b for b in right))
        score = numerator / energy if energy else 0.0
        if score > best_score:
            best_lag, best_score = lag, score
    return best_lag


def pitch_proxy(samples: list[float], begin: int, end: int) -> dict[str, float | int]:
    lag = autocorr_period(samples, begin, end)
    return {"analysis_window": [begin, end], "best_lag_samples": lag,
            "proxy_hz": round(RATE / lag, 3),
            "positive_crossings_in_window": crossings(samples[begin:end]),
            "method": "normalized autocorrelation peak for lags 24..64; not listening"}


def finite_summary(samples: list[float]) -> dict[str, object]:
    finite = all(math.isfinite(value) for value in samples)
    return {"finite": finite, "samples": len(samples),
            "peak_abs": round(max((abs(v) for v in samples), default=0.0), 8)}


def expected_positions(native: list[dict], markers: tuple[int, ...]) -> list[dict]:
    """Use the engine's own source-coordinate mapping to locate each marker."""
    result = []
    for marker in markers:
        found = None
        for record in native:
            native_begin = record["native_source_begin"]
            native_end = record["native_source_end"]
            if native_begin is None or native_end is None or native_end <= native_begin:
                continue
            if not native_begin <= marker < native_end:
                continue
            output_begin, output_end = record["output"]
            fraction = (marker - native_begin) / (native_end - native_begin)
            expected = output_begin + fraction * (output_end - output_begin)
            found = {"marker_source_sample": marker, "expected_output_sample": round(expected, 3),
                     "search_window": [-24, 24]}
            break
        if found is None:
            raise ValueError(f"no native mapping covers marker {marker}")
        result.append(found)
    return result


def local_contrast(samples: list[float], index: int) -> float:
    """Positive three-tap contrast; isolates the marker from the tone cusps."""
    return 2 * samples[index] - samples[index - 1] - samples[index + 1]


def impulse_probe(source: list[float], output: list[float], native: list[dict]) -> dict[str, object]:
    positions = expected_positions(native, MARKERS)
    checks = []
    for item in positions:
        center = int(round(item["expected_output_sample"]))
        window = range(max(1, center - 24), min(len(output) - 1, center + 25))
        observed = max(window, key=lambda index: local_contrast(output, index))
        contrast = local_contrast(output, observed)
        checks.append({**item, "observed_output_sample": observed,
                       "position_error_samples": observed - center,
                       "observed_local_contrast": round(contrast, 6),
                       "source_local_contrast": round(
                           local_contrast(source, item["marker_source_sample"]), 6),
                       "within_window": abs(observed - center) <= 24 and contrast > 0.15})
    return {"marker_positions": checks,
            "all_markers_located": all(item["within_window"] for item in checks),
            "audibility": "not_measured",
            "method": "maximum positive three-tap contrast in the native-mapped "
                      "+/-24 output window; numeric mapping proxy only"}


def mapping_summary(native: list[dict], target: int) -> dict[str, object]:
    source_monotone = all(a["source"][1] == b["source"][0] for a, b in pairwise(native))
    output_monotone = all(a["output"][1] == b["output"][0] for a, b in pairwise(native))
    finite_positions = all(
        record["native_source_begin"] is None
        or (math.isfinite(record["native_source_begin"]) and math.isfinite(record["native_source_end"]))
        for record in native)
    return {"calls": len(native),
            "first_source": native[0]["source"][0] if native else None,
            "final_source": native[-1]["source"][1] if native else None,
            "final_output": native[-1]["output"][1] if native else None,
            "target_frames": target,
            "source_intervals_contiguous": source_monotone,
            "output_intervals_contiguous": output_monotone,
            "native_positions_finite": finite_positions,
            "final_native_source_position": native[-1]["native_source_end"] if native else None}


def analyze_stream(source_path: Path, output_path: Path, meta: dict,
                   schedule: tuple[tuple[int, str], ...]) -> dict[str, object]:
    source = read_wav(source_path)
    output = read_wav(output_path)
    target = target_at(schedule, len(source)) + meta["caller_zero_tail_samples"]
    if meta["output_frames"] != len(output):
        raise ValueError("harness output count disagrees with WAV frames")
    source_pitch = pitch_proxy(source, 6_000, 7_800)
    output_pitch = pitch_proxy(output, 2_000, 3_800)
    return {
        "duration": {"source_frames": len(source), "target_frames": target,
                     "output_frames": len(output), "error_frames": len(output) - target,
                     "target_error_fraction": round(
                         (len(output) - target) / target if target else 0.0, 9)},
        "pitch_proxy": {"source": source_pitch, "output": output_pitch,
                        "output_over_source": round(
                            output_pitch["proxy_hz"] / source_pitch["proxy_hz"], 6),
                        "method": "source/output autocorrelation lag ratio; not listening"},
        "source_mapping": mapping_summary(meta["mapping"], target),
        "impulse_proxy": impulse_probe(source, output, meta["mapping"]),
        "finite_output": finite_summary(output),
        "native": {"edition": meta["edition"], "version": meta["version"],
                   "max_input_frame_count": meta["max_input_frame_count"],
                   "final_latency_input_frames": meta["final_latency_input_frames"],
                   "chunk_cycle": meta["chunk_cycle"], "schedule": meta["schedule"],
                   "drain": meta["drain"],
                   "caller_zero_tail_samples": meta["caller_zero_tail_samples"],
                   "native_mapping_records": meta["mapping"]},
        "output_sha256": sha256(output_path),
    }


def matched_linear_control(source: list[float],
                           schedule: tuple[tuple[int, str], ...]) -> list[float]:
    """Pitch-changing interpolation on exactly the same source and clock."""
    from reference import linear_control  # task-local prior fixture, not Bungee

    spans = []
    consumed = 0
    for chunk in chunk_sizes(len(source)):
        spans.append({"source": [consumed, consumed + chunk],
                      "output": [target_at(schedule, consumed),
                                 target_at(schedule, consumed + chunk)],
                      "rate": schedule_at(schedule, consumed)})
        consumed += chunk
    return linear_control(source, spans)


def analyze_control(source: list[float], output: list[float]) -> dict[str, object]:
    source_pitch = pitch_proxy(source, 6_000, 7_800)
    control_pitch = pitch_proxy(output, 2_000, 3_800)
    return {"duration": {"output_frames": len(output)},
            "pitch_proxy": {"source": source_pitch, "control": control_pitch,
                            "control_over_source": round(
                                control_pitch["proxy_hz"] / source_pitch["proxy_hz"], 6),
                            "method": "matched source, chunk schedule and target clock; "
                                      "interpolation changes pitch"},
            "finite_output": finite_summary(output),
            "role": "pitch-changing interpolation control on matched synthetic PCM; not Bungee"}


def analyze_granular(meta: dict) -> dict[str, object]:
    return {"mode": "granular_is_flushed", "edition": meta["edition"],
            "version": meta["version"], "source_frames": meta["source_frames"],
            "speed": meta["speed"], "grains": meta["grains"],
            "output_frames_including_preroll": meta["output_frames_including_preroll"],
            "is_flushed": meta["is_flushed"],
            "bounded_by_grains": meta["bounded_by_grains"],
            "finite_output": meta["finite_output"], "max_abs": meta["max_abs"],
            "max_input_frame_count": meta["max_input_frame_count"],
            "scope": "Native Stretcher isFlushed() probe, not Stream EOS or device flush"}
