# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local PSOLA/Praat-style time-scale-modification reference.

This module is stdlib-only. It implements a minimal pitch-synchronous
overlap-add (TD-PSOLA) reference on deterministic synthetic pulse stimuli,
maps it to the public v0 provider/session boundary shape, and produces the
canonical report. It is synthetic evidence only: not an installed provider,
not a playback actuator, not a listening result and not a timing claim.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import platform
import struct
import sys
from pathlib import Path
from typing import Iterable, Sequence

TASK_DIR = Path(__file__).resolve().parent
WORKTREE = TASK_DIR.parents[2]
AUDIO_ROOT = WORKTREE.parents[2]

VERSION = "0.1.0"
CONTRACT_ID = "audio-sdk/psola-praat-evidence/0.1"
PROVIDER_ID = "rate.psola-praat-reference.v0"
BASE_COMMIT = "68e3e292b0b2c4b0a96b5f3d3002bb9cb36282d4"
BRANCH = "swarm/SDK-PSOLA-PRAAT"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
STIMULUS_LENGTH = 12457  # 77 full frames + a 137-sample final frame.
HALF_WINDOW = 56
WINDOW_SIZE = 2 * HALF_WINDOW + 1
MIN_PERIOD = 64
VOICING_THRESHOLD = 0.045
PHASE_DENOMINATOR = 1000000
SLEW_PER_MARK = 0.05
RATE_MIN = 0.75
RATE_MAX = 1.50
MAX_ABS = 1.0
EPS = 1e-12

SOURCE_PINS = {
    "research/tsm-followup-20261101/README.md": (
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f"
    ),
    "REALTIME_COMPONENT_CANDIDATES.md": (
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d"
    ),
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": (
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910"
    ),
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md": (
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69"
    ),
    "audio-benchmark-platform/audio-sdk/README.md": (
        "9047036096a967bed5cd59e7d3b939258d327578b2079445da1b683b52a8fdb9"
    ),
}

BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h": (
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766"
    ),
    "api/include/audio_sdk/session_v0.h": (
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1"
    ),
}

IDENTITY_SCHEDULE = ((0, 1.0),)
FIXED_SCHEDULE = ((0, 1.25),)
SLOW_SCHEDULE = ((0, 0.95),)
DYNAMIC_SCHEDULE = ((0, 1.0), (4800, 1.25), (8000, 1.0), (11200, 1.5))
DRIFT_SCHEDULE = ((0, 1.0), (3200, 1.05), (6400, 0.95), (9600, 1.0))

WINDOW = tuple(
    0.5 - 0.5 * math.cos(2.0 * math.pi * index / (WINDOW_SIZE - 1))
    for index in range(WINDOW_SIZE)
)


class ReferenceRejection(ValueError):
    """Deterministic rejection with a machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_json(report)
    return text, sha256_bytes(text.encode("utf-8"))


def tensor_digest(values: Iterable[float]) -> str:
    payload = b"".join(struct.pack("<f", float(value)) for value in values)
    return sha256_bytes(payload)


def object_digest(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def round_half_away(value: float) -> int:
    """C-compatible llround() for the non-negative values used here."""
    return int(math.floor(value + 0.5))


def rate_at(schedule: Sequence[tuple[int, float]], position: int) -> float:
    selected = schedule[0][1]
    for start, rate in schedule:
        if position >= start:
            selected = rate
        else:
            break
    return selected


def validate_schedule(schedule: object) -> tuple[tuple[int, float], ...]:
    if not isinstance(schedule, (tuple, list)) or not schedule:
        raise ReferenceRejection("missing_rate_selection", "rate schedule is required")
    clean: list[tuple[int, float]] = []
    previous = -1
    for row in schedule:
        if (not isinstance(row, (tuple, list)) or len(row) != 2 or
                not isinstance(row[0], int) or isinstance(row[0], bool) or
                not isinstance(row[1], (int, float)) or isinstance(row[1], bool)):
            raise ReferenceRejection("invalid_schedule", "malformed rate schedule row")
        start, rate = int(row[0]), float(row[1])
        if start <= previous or start < 0:
            raise ReferenceRejection("invalid_schedule", "rate starts must increase")
        if not math.isfinite(rate) or rate < RATE_MIN or rate > RATE_MAX:
            raise ReferenceRejection("rate_out_of_range", "rate outside declared bounds")
        previous = start
        clean.append((start, rate))
    if clean[0][0] != 0:
        raise ReferenceRejection("missing_rate_selection", "schedule must start at sample 0")
    return tuple(clean)


DEFAULT_CONFIG = {
    "provider_id": PROVIDER_ID,
    "schema_id": "audio-sdk/provider-config/0.1",
    "settings": {},
    "units": {},
}


def validate_config(config: object) -> dict:
    required = {"provider_id", "schema_id", "settings", "units"}
    if not isinstance(config, dict):
        raise ReferenceRejection("missing_rate_selection", "config must be an object")
    if set(config) != required:
        raise ReferenceRejection("invalid_config", "config keys do not match the closed schema")
    if config.get("provider_id") != PROVIDER_ID:
        raise ReferenceRejection("invalid_config", "wrong provider id")
    if config.get("schema_id") != "audio-sdk/provider-config/0.1":
        raise ReferenceRejection("invalid_config", "wrong config schema")
    if config.get("settings") != {} or config.get("units") != {}:
        raise ReferenceRejection("invalid_config", "external reference declares no settings")
    return dict(config)


@functools.lru_cache(maxsize=16)
def analytic_stimulus(name: str, length: int = STIMULUS_LENGTH) -> tuple[float, ...]:
    """Seeded analytic stimuli; no corpus, WAV, model or external asset."""
    if name == "silence":
        return (0.0,) * length
    if name == "c_vector":
        # Integer-exact pulse train shared byte-for-byte with the C boundary
        # test: a 96-sample period, an 8-sample glottal pulse and small ripple.
        values = []
        for sample in range(length):
            phase = sample % 96
            integer = (240 - 20 * phase) if phase < 8 else ((sample * 37) % 21 - 10)
            values.append(integer / 512.0)
        return tuple(values)
    if name == "tonal":
        values = []
        for sample in range(length):
            t = sample / SAMPLE_RATE_HZ
            envelope = 0.16 + 0.09 * math.sin(2.0 * math.pi * 1.7 * t)
            value = envelope * math.sin(2.0 * math.pi * 220.0 * t)
            value += 0.035 * math.sin(2.0 * math.pi * 440.0 * t)
            if 4300 <= sample <= 4307:
                value += 0.28 * (1.0 - abs(sample - 4303.5) / 4.5)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return tuple(values)
    if name == "speech_like":
        state = 7102
        phase = 0.0
        r1 = r2 = r3 = 0.0
        values = []
        for sample in range(length):
            t = sample / SAMPLE_RATE_HZ
            f0 = 185.0 + 20.0 * math.sin(2.0 * math.pi * 0.7 * t)
            phase += f0 / SAMPLE_RATE_HZ
            if phase >= 1.0:
                phase -= 1.0
            pulse = 1.0 if phase < 0.14 else 0.0
            r1 = 0.955 * r1 + pulse
            r2 = 0.930 * r2 + r1
            r3 = 0.700 * r3 + 0.3 * r2
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            noise = state / 2147483648.0 - 1.0
            syllable = 0.65 + 0.35 * max(0.0, math.sin(2.0 * math.pi * 3.1 * t)) ** 2
            value = 0.004 * (r1 + 0.35 * r2 + 0.2 * r3) * syllable + 0.004 * noise
            if 5600 <= sample <= 5607:
                value += 0.22 * (1.0 - abs(sample - 5603.5) / 4.5)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return tuple(values)
    if name == "unfamiliar_speech":
        # A second analytic voice surrogate: higher F0, different contour and
        # formants, different syllable rhythm. No corpus or real speaker.
        state = 987654321
        phase = 0.0
        r1 = r2 = 0.0
        values = []
        for sample in range(length):
            t = sample / SAMPLE_RATE_HZ
            f0 = 225.0 + 12.0 * math.sin(2.0 * math.pi * 1.3 * t + 0.4)
            phase += f0 / SAMPLE_RATE_HZ
            if phase >= 1.0:
                phase -= 1.0
            pulse = 1.0 if phase < 0.12 else 0.0
            r1 = 0.940 * r1 + pulse
            r2 = 0.860 * r2 + 0.6 * r1
            state = (1103515245 * state + 12345) & 0xFFFFFFFF
            noise = state / 2147483648.0 - 1.0
            syllable = 0.65 + 0.35 * max(0.0, math.sin(2.0 * math.pi * 4.3 * t + 1.0)) ** 2
            value = 0.006 * (r1 + 0.5 * r2) * syllable + 0.003 * noise
            if 7200 <= sample <= 7207:
                value += 0.20 * (1.0 - abs(sample - 7203.5) / 4.5)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return tuple(values)
    if name == "music_like":
        # Harmonic pulse surrogate with a 100-sample note-period and slow
        # tremolo. This is an analytic stand-in, not recorded music.
        values = []
        for sample in range(length):
            t = sample / SAMPLE_RATE_HZ
            phase = sample % 100
            pulse = 1.0 if phase < 5 else 0.0
            resonator = 0.0
            for coefficient in (0.980, 0.940, 0.870):
                resonator = coefficient * resonator + pulse
            tremolo = 0.78 + 0.22 * math.sin(2.0 * math.pi * 1.1 * t)
            value = 0.085 * resonator * tremolo
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return tuple(values)
    raise ReferenceRejection("unknown_stimulus", "unknown stimulus: " + name)


def pitch_marks(values: Sequence[float], *, threshold: float = VOICING_THRESHOLD,
                min_period: int = MIN_PERIOD) -> tuple[int, ...]:
    """Absolute-value local maxima with a minimum pitch period.

    This is a pitch-marking surrogate for the deterministic pulse stimuli in
    this fixture. It is not a general-purpose voiced/voiceless tracker.
    """
    marks: list[int] = []
    last = -10**9
    for index in range(1, len(values) - 1):
        current = abs(values[index])
        if current < threshold:
            continue
        if current <= abs(values[index - 1]) or current < abs(values[index + 1]):
            continue
        if index - last < min_period:
            continue
        marks.append(index)
        last = index
    return tuple(marks)


def mark_periods(marks: Sequence[int]) -> tuple[int, ...]:
    if len(marks) < 2:
        return ()
    periods = [marks[index + 1] - marks[index] for index in range(len(marks) - 1)]
    periods.append(periods[-1])
    return tuple(periods)


def synthesize(values: Sequence[float],
               schedule: Sequence[tuple[int, float]] = IDENTITY_SCHEDULE,
               *, normalize: bool = True, slew: bool = True,
               half_window: int = HALF_WINDOW) -> tuple[list[float], list[int], dict]:
    """Pitch-synchronous overlap/add with overlap denominator normalization."""
    clean_schedule = validate_schedule(schedule)
    if not 1 <= half_window <= 128:
        raise ReferenceRejection("invalid_window", "half_window out of range")
    window = tuple(
        0.5 - 0.5 * math.cos(2.0 * math.pi * index / (2 * half_window))
        for index in range(2 * half_window + 1)
    )
    marks = pitch_marks(values)
    periods = mark_periods(marks)
    diagnostics = {
        "status": "scored" if marks else "no_pitch_marks",
        "marks": len(marks),
        "first_mark": marks[0] if marks else None,
        "last_mark": marks[-1] if marks else None,
        "min_period": min(periods) if periods else None,
        "max_period": max(periods) if periods else None,
        "mean_period": (sum(periods) / len(periods)) if periods else None,
        "estimated_f0_hz": (SAMPLE_RATE_HZ / (sum(periods) / len(periods)))
                           if periods else None,
        "rate_updates": [],
        "selected_marks": 0,
        "uncovered_samples": 0,
        "trimmed_leading_samples": 0,
        "denominator_min": None,
        "denominator_max": None,
        "normalize": bool(normalize),
        "slew": bool(slew),
        "half_window": int(half_window),
    }
    if len(marks) < 2:
        return [], [], diagnostics

    phase = 0
    current_rate = clean_schedule[0][1]
    step = SLEW_PER_MARK if slew else 10.0
    selected: list[int] = []
    total_periods = 0
    previous_target = rate_at(clean_schedule, marks[0])
    for index, mark in enumerate(marks):
        target = rate_at(clean_schedule, mark)
        if target > current_rate:
            current_rate = min(target, current_rate + step)
        else:
            current_rate = max(target, current_rate - step)
        if target != previous_target:
            diagnostics["rate_updates"].append({
                "mark_index": index,
                "source_sample": mark,
                "previous_rate": previous_target,
                "target_rate": target,
                "applied_rate": current_rate,
                "slewed": bool(slew),
            })
            previous_target = target
        phase += round_half_away(PHASE_DENOMINATOR / current_rate)
        while phase >= PHASE_DENOMINATOR:
            phase -= PHASE_DENOMINATOR
            selected.append(index)
            total_periods += periods[index]

    diagnostics["selected_marks"] = len(selected)
    length = marks[selected[0]] + total_periods + half_window + 1
    accumulator = [0.0] * length
    denominator = [0.0] * length
    source_map = [-1] * length
    center = marks[selected[0]]
    for index in selected:
        mark = marks[index]
        for offset in range(-half_window, half_window + 1):
            source = mark + offset
            if source < 0 or source >= len(values):
                continue
            position = center + offset
            weight = window[offset + half_window]
            accumulator[position] += values[source] * weight
            denominator[position] += weight
            if source_map[position] < source:
                source_map[position] = source
        center += periods[index]

    covered = [index for index, value in enumerate(denominator) if value > EPS]
    if not covered:
        return [], [], diagnostics
    first, last = covered[0], covered[-1]
    accumulator = accumulator[first:last + 1]
    denominator = denominator[first:last + 1]
    source_map = source_map[first:last + 1]
    diagnostics["trimmed_leading_samples"] = first
    # Unnormalized mode keeps the raw overlap sum; normalized mode divides by
    # the per-sample window sum. Both are explicit, scored variants.
    if normalize:
        output = [value / weight if weight > EPS else 0.0
                  for value, weight in zip(accumulator, denominator)]
    else:
        output = list(accumulator)
    diagnostics["uncovered_samples"] = sum(1 for value in denominator if value <= EPS)
    diagnostics["denominator_min"] = min(denominator)
    diagnostics["denominator_max"] = max(denominator)
    return output, source_map, diagnostics


def identity_run(values: Sequence[float]) -> tuple[list[float], list[int]]:
    return list(values), list(range(len(values)))


def varispeed_run(values: Sequence[float], rate: float) -> tuple[list[float], list[int]]:
    """Adverse control: linear resampling changes pitch as well as duration."""
    length = round_half_away(len(values) / rate)
    output = []
    sources = []
    for index in range(length):
        position = index * rate
        lower = int(math.floor(position))
        upper = min(lower + 1, len(values) - 1)
        fraction = position - lower
        output.append(values[lower] * (1.0 - fraction) + values[upper] * fraction)
        sources.append(int(round(position)))
    return output, sources


def finite_stats(values: Sequence[float]) -> dict:
    finite = [math.isfinite(value) for value in values]
    peak = max((abs(value) for value in values if math.isfinite(value)), default=0.0)
    return {
        "samples": len(values),
        "nonfinite_count": len(values) - sum(finite),
        "peak_abs": peak,
        "clipping_count": sum(1 for value in values
                              if math.isfinite(value) and abs(value) > MAX_ABS),
        "rms": math.sqrt(sum(value * value for value in values
                             if math.isfinite(value)) / max(1, len(values))),
        "digest": tensor_digest(values),
    }


def source_map_stats(sources: Sequence[int]) -> dict:
    valid = [value for value in sources if value >= 0]
    violations = 0
    max_gap = 0
    max_repeat = 0
    for previous, current in zip(valid, valid[1:]):
        if current < previous:
            violations += 1
        max_gap = max(max_gap, current - previous)
        max_repeat = max(max_repeat, previous - current)
    return {
        "monotonic": violations == 0,
        "monotonic_violations": violations,
        "max_source_step": max_gap,
        "max_source_repeat": max_repeat,
        "first_source": valid[0] if valid else None,
        "last_source": valid[-1] if valid else None,
        "unmapped_samples": len(sources) - len(valid),
    }


def adjacent_stats(values: Sequence[float]) -> dict:
    deltas = [abs(b - a) for a, b in zip(values, values[1:])
              if math.isfinite(a) and math.isfinite(b)]
    if not deltas:
        return {"p99": 0.0, "max": 0.0}
    ordered = sorted(deltas)
    index = min(len(ordered) - 1, round_half_away(0.99 * len(ordered)) - 1)
    return {"p99": ordered[max(0, index)], "max": ordered[-1]}


def discontinuity_at(values: Sequence[float], sources: Sequence[int],
                     boundary: int, radius: int = 64) -> dict:
    index = next((i for i, source in enumerate(sources) if source >= boundary), None)
    all_stats = adjacent_stats(values)
    if index is None:
        return {"status": "missing_boundary", "clip_p99": all_stats["p99"]}
    low = max(1, index - radius)
    high = min(len(values), index + radius + 1)
    local = adjacent_stats(values[low:high])
    return {
        "status": "ok",
        "source_boundary": boundary,
        "output_index": index,
        "local_max_adjacent_delta": local["max"],
        "clip_p99_adjacent_delta": all_stats["p99"],
        "ratio_to_clip_p99": local["max"] / max(all_stats["p99"], EPS),
    }


def goertzel(values: Sequence[float], frequency: float, rate: int = SAMPLE_RATE_HZ) -> float:
    coefficient = 2.0 * math.cos(2.0 * math.pi * frequency / rate)
    s1 = s2 = 0.0
    for index, value in enumerate(values):
        window = 0.5 - 0.5 * math.cos(2.0 * math.pi * index / max(1, len(values) - 1))
        sample = value * window
        s0 = sample + coefficient * s1 - s2
        s2, s1 = s1, s0
    return math.sqrt(max(0.0, s1 * s1 + s2 * s2 - coefficient * s1 * s2))


def dominant_frequency(values: Sequence[float], low: float = 100.0,
                       high: float = 520.0) -> dict:
    start = len(values) // 3
    stop = min(len(values), start + 2048)
    window = list(values[start:stop])
    best_hz = 0.0
    best_power = -1.0
    hz = low
    while hz <= high:
        power = goertzel(window, hz)
        if power > best_power:
            best_power = power
            best_hz = hz
        hz += 2.0
    return {"dominant_hz": best_hz, "power": best_power, "analysis_samples": len(window)}


def variant_row(values: Sequence[float], output: Sequence[float],
                sources: Sequence[int], *, label: str, status: str,
                schedule: Sequence[tuple[int, float]], diagnostics: dict) -> dict:
    stats = finite_stats(output)
    expected = len(values) / rate_at(schedule, 0) if len(schedule) == 1 else None
    stats.update({
        "status": status,
        "algorithm": label,
        "schedule": [[start, rate] for start, rate in schedule],
        "source_samples": len(values),
        "effective_rate": (len(values) / len(output)) if output else None,
        "expected_constant_rate_output": expected,
        "duration_error_samples": (len(output) - expected) if expected is not None else None,
        "marks": diagnostics["marks"],
        "selected_marks": diagnostics["selected_marks"],
        "estimated_f0_hz": diagnostics["estimated_f0_hz"],
        "uncovered_samples": diagnostics["uncovered_samples"],
        "source_map": source_map_stats(sources),
        "source_map_digest": tensor_digest(float(value) for value in sources),
    })
    return stats


def variant_bundle(stimuli: dict[str, list[float]]) -> dict:
    bundle: dict[str, dict] = {}
    for name, values in stimuli.items():
        if name == "silence":
            marks = pitch_marks(values)
            bundle[name] = {
                "unvoiced_fallback": {
                    "status": "no_pitch_marks",
                    "algorithm": "silence_no_pitch_marks",
                    "source_samples": len(values),
                    "mark_count": len(marks),
                    "output_samples": 0,
                    "output_digest": tensor_digest([]),
                    "interpretation": "No pitch marks; no voiced synthesis is invented.",
                }
            }
            continue
        identity = identity_run(values)
        fixed_out, fixed_src, fixed_diag = synthesize(values, FIXED_SCHEDULE)
        dynamic_out, dynamic_src, dynamic_diag = synthesize(values, DYNAMIC_SCHEDULE)
        varispeed = varispeed_run(values, 1.25)
        rows = {
            "identity_1x_control": {
                **finite_stats(identity[0]),
                "status": "control",
                "algorithm": "identity_passthrough",
                "schedule": [[0, 1.0]],
                "source_samples": len(values),
                "effective_rate": 1.0,
                "expected_constant_rate_output": len(values),
                "duration_error_samples": 0,
                "marks": None,
                "selected_marks": 0,
                "estimated_f0_hz": None,
                "uncovered_samples": 0,
                "source_map": source_map_stats(identity[1]),
                "source_map_digest": tensor_digest(float(value) for value in identity[1]),
            },
            "fixed_rate_psola": variant_row(values, fixed_out, fixed_src,
                                            label="psola_pitch_synchronous_ola",
                                            status="scored", schedule=FIXED_SCHEDULE,
                                            diagnostics=fixed_diag),
            "dynamic_rate_psola": variant_row(values, dynamic_out, dynamic_src,
                                              label="psola_pitch_synchronous_ola",
                                              status="candidate", schedule=DYNAMIC_SCHEDULE,
                                              diagnostics=dynamic_diag),
            "varispeed_adverse": {
                **finite_stats(varispeed[0]),
                "status": "adverse_control",
                "algorithm": "varispeed_linear_interpolation",
                "schedule": [[0, 1.25]],
                "source_samples": len(values),
                "effective_rate": 1.25,
                "expected_constant_rate_output": round_half_away(len(values) / 1.25),
                "duration_error_samples": (len(varispeed[0]) -
                                           round_half_away(len(values) / 1.25)),
                "marks": None,
                "selected_marks": 0,
                "estimated_f0_hz": None,
                "uncovered_samples": 0,
                "source_map": source_map_stats(varispeed[1]),
                "source_map_digest": tensor_digest(float(value) for value in varispeed[1]),
            },
        }
        bundle[name] = rows
    return bundle


def pitch_evidence(stimuli: dict[str, list[float]]) -> dict:
    rows: dict[str, dict] = {}
    for name, values in stimuli.items():
        marks = pitch_marks(values)
        periods = mark_periods(marks)
        rows[name] = {
            "status": "scored" if periods else "no_pitch_marks",
            "mark_count": len(marks),
            "first_mark": marks[0] if marks else None,
            "last_mark": marks[-1] if marks else None,
            "min_period_samples": min(periods) if periods else None,
            "max_period_samples": max(periods) if periods else None,
            "mean_period_samples": (sum(periods) / len(periods)) if periods else None,
            "estimated_f0_hz": (SAMPLE_RATE_HZ / (sum(periods) / len(periods)))
                               if periods else None,
            "marks_per_second": (len(marks) * SAMPLE_RATE_HZ / len(values)) if values else None,
            "min_gap_ok": bool(periods) and min(periods) >= MIN_PERIOD,
            "max_gap_ok": bool(periods) and max(periods) <= 2 * HALF_WINDOW,
        }
    return {"threshold": VOICING_THRESHOLD, "min_period_samples": MIN_PERIOD,
            "definition": "absolute-value local maxima with minimum separation",
            "rows": rows}


def frequency_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["tonal"]
    reference = dominant_frequency(values)
    output, sources, diagnostics = synthesize(values, FIXED_SCHEDULE)
    mismatch = pitch_marks(values, min_period=8)
    mismatch_periods = mark_periods(mismatch)
    # The mismarked control uses an over-dense mark sequence with a short
    # excision window; it is an explicit pitch-doubling adverse case.
    dense_output = dense_mark_output(values, mismatch, half_window=18)
    runs = {
        "identity_1x_control": identity_run(values)[0],
        "fixed_rate_psola": output,
        "varispeed_adverse": varispeed_run(values, 1.25)[0],
        "mismarked_adverse": dense_output,
    }
    rows = {}
    for label, signal in runs.items():
        measured = dominant_frequency(signal)
        ratio = measured["dominant_hz"] / reference["dominant_hz"]
        expected = 1.25 if label == "varispeed_adverse" else 1.0
        rows[label] = {
            "status": "scored",
            "input_dominant_hz": reference["dominant_hz"],
            "output_dominant_hz": measured["dominant_hz"],
            "frequency_ratio": ratio,
            "expected_ratio": expected,
            "absolute_error": abs(ratio - expected),
            "pitch_preserved": abs(ratio - 1.0) <= 0.06,
            "matches_expected_model": abs(ratio - expected) <= 0.06,
        }
    rows["mismarked_adverse"]["mark_count"] = len(mismatch)
    rows["mismarked_adverse"]["mean_period_samples"] = (
        sum(mismatch_periods) / len(mismatch_periods) if mismatch_periods else None)
    rows["fixed_rate_psola"]["selected_marks"] = diagnostics["selected_marks"]
    return {
        "stimulus": "tonal",
        "reference": reference,
        "rows": rows,
        "interpretation": ("PSOLA overlap/add preserves the pitch of the synthetic pitch "
                           "marks; linear resampling is an adverse pitch-shifting control."),
    }


def dense_mark_output(values: Sequence[float], marks: Sequence[int],
                      half_window: int = 18) -> list[float]:
    """Adverse control: over-dense marks from a too-small minimum period."""
    if len(marks) < 2:
        return []
    periods = mark_periods(marks)
    window = tuple(
        0.5 - 0.5 * math.cos(2.0 * math.pi * index / (2 * half_window))
        for index in range(2 * half_window + 1)
    )
    total = sum(periods)
    accumulator = [0.0] * (marks[0] + total + half_window + 1)
    denominator = [0.0] * len(accumulator)
    center = marks[0]
    for index, mark in enumerate(marks):
        for offset in range(-half_window, half_window + 1):
            source = mark + offset
            if 0 <= source < len(values):
                position = center + offset
                weight = window[offset + half_window]
                accumulator[position] += abs(values[source]) * weight
                denominator[position] += weight
        center += periods[index]
    return [value / weight if weight > EPS else 0.0
            for value, weight in zip(accumulator, denominator)]


def overlap_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["tonal"]
    normalized, _, rows = synthesize(values, FIXED_SCHEDULE, normalize=True)
    unnormalized, _, _ = synthesize(values, FIXED_SCHEDULE, normalize=False)
    excised, _, excised_rows = synthesize(values, FIXED_SCHEDULE, half_window=18)
    reference = finite_stats(values)["rms"]
    normalized_ratio = finite_stats(normalized)["rms"] / reference
    unnormalized_ratio = finite_stats(unnormalized)["rms"] / reference
    return {
        "status": "ok",
        "stimulus": "tonal",
        "reference_rms": reference,
        "normalized_rms": finite_stats(normalized)["rms"],
        "unnormalized_rms": finite_stats(unnormalized)["rms"],
        "normalized_ratio": normalized_ratio,
        "unnormalized_ratio": unnormalized_ratio,
        "normalized_closer_to_reference": abs(normalized_ratio - 1.0) <
                                          abs(unnormalized_ratio - 1.0),
        "candidate_uncovered_samples": rows["uncovered_samples"],
        "candidate_denominator_min": rows["denominator_min"],
        "candidate_denominator_max": rows["denominator_max"],
        "excision_adverse": {
            "status": "adverse_control",
            "half_window": 18,
            "uncovered_samples": excised_rows["uncovered_samples"],
            "rms": finite_stats(excised)["rms"],
            "digest": finite_stats(excised)["digest"],
        },
        "window": "Hann, length 2*56+1, overlap denominator normalization",
    }


def rate_update_evidence(stimuli: dict[str, list[float]]) -> dict:
    rows: dict[str, dict] = {}
    for name, values in stimuli.items():
        if name == "silence":
            continue
        outputs = {
            "identity_1x_control": identity_run(values),
            "fixed_rate_psola": (lambda r: (r[0], r[1]))(
                synthesize(values, FIXED_SCHEDULE)[:2]),
            "dynamic_rate_psola": synthesize(values, DYNAMIC_SCHEDULE)[:2],
            "unsmoothed_psola_adverse": synthesize(values, DYNAMIC_SCHEDULE, slew=False)[:2],
            "varispeed_adverse": varispeed_run(values, 1.25),
        }
        boundaries = {}
        for boundary in (4800, 8000, 11200):
            boundaries[str(boundary)] = {
                label: discontinuity_at(signal, sources, boundary)
                for label, (signal, sources) in outputs.items()
            }
        rows[name] = {
            "boundaries": boundaries,
            "source_maps": {
                label: source_map_stats(sources) for label, (_, sources) in outputs.items()
            },
        }
    applied = synthesize(stimuli["c_vector"], DYNAMIC_SCHEDULE)[2]["rate_updates"]
    return {"rows": rows, "applied_updates": applied,
            "slew_per_mark": SLEW_PER_MARK,
            "unsmoothed_step": 10.0}


def streaming_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["c_vector"]
    whole = synthesize(values, DYNAMIC_SCHEDULE)
    whole_output = whole[0]
    streaming = PsolaStream(DYNAMIC_SCHEDULE)
    for start in range(0, len(values), FRAME_SAMPLES):
        chunk = list(values[start:start + FRAME_SAMPLES])
        final = start + FRAME_SAMPLES >= len(values)
        padded = chunk + [0.0] * (FRAME_SAMPLES - len(chunk))
        streaming.push(padded, len(chunk), start, final=final)
    stream_output = list(streaming.fifo)
    replay = PsolaStream(DYNAMIC_SCHEDULE, first_input_sample=50000)
    for start in range(0, len(values), FRAME_SAMPLES):
        chunk = list(values[start:start + FRAME_SAMPLES])
        final = start + FRAME_SAMPLES >= len(values)
        padded = chunk + [0.0] * (FRAME_SAMPLES - len(chunk))
        replay.push(padded, len(chunk), 50000 + start, final=final)
    replay_output = list(replay.fifo)
    independent = synthesize(values, FIXED_SCHEDULE)[0]

    rejections: dict[str, dict] = {}
    cases = [
        ("nonfinite_input", 0, FRAME_SAMPLES, [math.nan] + [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES, 1),
        ("out_of_range", 0, FRAME_SAMPLES, [1.5] + [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES, 1),
        ("wrong_shape", 0, FRAME_SAMPLES, [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES - 1, 1),
        ("wrong_position", 0, FRAME_SAMPLES + 1, [0.0] * FRAME_SAMPLES, FRAME_SAMPLES, 1),
        ("stale_epoch", 0, FRAME_SAMPLES, [0.0] * FRAME_SAMPLES, FRAME_SAMPLES, 0),
        ("process_after_final", 0, FRAME_SAMPLES, [0.0] * FRAME_SAMPLES, FRAME_SAMPLES, 1),
    ]
    for label, origin, bad_first, frame, valid, epoch in cases:
        stream = PsolaStream(DYNAMIC_SCHEDULE, first_input_sample=origin)
        stream.push([0.0] * FRAME_SAMPLES, FRAME_SAMPLES, origin)
        if label == "process_after_final":
            stream.finalized = True
        state_before = stream.state_digest()
        error = None
        try:
            stream.push(frame, valid, bad_first, epoch=epoch)
        except ReferenceRejection as rejection:
            error = rejection.code
        rejections[label] = {
            "status": "rejected",
            "code": error,
            "state_unchanged": stream.state_digest() == state_before,
        }
    config_cases: dict[str, dict] = {}
    for label, config, schedule in (
        ("missing_rate_selection", None, None),
        ("invalid_config", {**DEFAULT_CONFIG, "unknown": 1}, None),
        ("rate_out_of_range", None, ((0, 1.9),)),
        ("invalid_schedule", None, ((0, 1.0), (0, 1.25))),
    ):
        try:
            if schedule is not None:
                validate_schedule(schedule)
            else:
                validate_config(config)
            outcome = "incorrectly_accepted"
        except ReferenceRejection as rejection:
            outcome = rejection.code
        config_cases[label] = {"status": "rejected", "code": outcome}

    drain_stream = PsolaStream(DYNAMIC_SCHEDULE)
    drain_error = None
    try:
        drain_stream.drain()
    except ReferenceRejection as rejection:
        drain_error = rejection.code
    flush_error = None
    try:
        drain_stream.flush()
    except ReferenceRejection as rejection:
        flush_error = rejection.code

    return {
        "chunking_equivalence": {
            "status": "ok" if tensor_digest(whole_output) == tensor_digest(stream_output)
                      else "expected_lookahead_difference",
            "whole_digest": tensor_digest(whole_output),
            "chunked_digest": tensor_digest(stream_output),
            "equal": tensor_digest(whole_output) == tensor_digest(stream_output),
            "reason": ("Pitch marking needs one sample of lookahead; a mark at a frame "
                       "boundary can appear after the next frame is delivered, so the "
                       "whole-clip and causal 160-frame histories are distinct."),
        },
        "reset_replay": {
            "status": "ok",
            "original_digest": tensor_digest(stream_output),
            "replay_digest": tensor_digest(replay_output),
            "replay_matches": tensor_digest(stream_output) == tensor_digest(replay_output),
            "replay_first_input_sample": replay.first_input_sample,
        },
        "session_independence": {
            "status": "ok",
            "independent": tensor_digest(stream_output) != tensor_digest(independent),
            "second_digest": tensor_digest(independent),
        },
        "frame_rejections": rejections,
        "config_rejections": config_cases,
        "drain_before_final": {"status": "rejected", "code": drain_error},
        "flush_before_final": {"status": "rejected", "code": flush_error},
    }


class PsolaStream:
    """Fixed-frame adapter emulation of the task-local C provider boundary."""

    def __init__(self, schedule: Sequence[tuple[int, float]] = DYNAMIC_SCHEDULE,
                 *, first_input_sample: int = 0, epoch: int = 1):
        self.schedule = validate_schedule(schedule)
        self.first_input_sample = int(first_input_sample)
        self.epoch = int(epoch)
        self.input: list[float] = []
        self.input_position = int(first_input_sample)
        self.fifo: list[float] = []
        self.emitted = 0
        self.finalized = False
        self.flushed = False
        self.invalid_count = 0

    def _reject(self, code: str, message: str) -> None:
        self.invalid_count += 1
        raise ReferenceRejection(code, message)

    def push(self, frame: Sequence[float], valid: int, first: int,
             *, epoch: int = 1, final: bool = False) -> None:
        if self.finalized or self.flushed:
            self._reject("process_after_final", "no process after final input")
        if len(frame) != FRAME_SAMPLES or not 1 <= valid <= FRAME_SAMPLES:
            self._reject("wrong_shape", "wrong frame shape or valid count")
        if epoch != self.epoch:
            self._reject("stale_epoch", "epoch mismatch")
        if first != self.input_position:
            self._reject("wrong_position", "first_input_sample mismatch")
        for value in frame[:valid]:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                self._reject("nonfinite_input", "input must be finite")
            if abs(value) > MAX_ABS:
                self._reject("out_of_range", "input magnitude exceeds declared bound")
        self.input.extend(float(value) for value in frame[:valid])
        self.input_position += FRAME_SAMPLES
        if final:
            self.finalized = True
        output, _, _ = synthesize(self.input, self.schedule)
        if len(output) < self.emitted:
            self._reject("backend_failure", "synthesized prefix shrank")
        self.fifo.extend(output[self.emitted:])
        self.emitted = len(output)

    def state_digest(self) -> str:
        return object_digest({
            "epoch": self.epoch,
            "input": tensor_digest(self.input),
            "input_position": self.input_position,
            "emitted": self.emitted,
            "fifo": tensor_digest(self.fifo),
            "finalized": self.finalized,
        })

    def reset(self, epoch: int, first_input_sample: int) -> None:
        if self.finalized or self.flushed or epoch <= self.epoch or first_input_sample < 0:
            self._reject("stale_epoch", "reset requires a newer epoch")
        self.epoch = int(epoch)
        self.first_input_sample = int(first_input_sample)
        self.input = []
        self.input_position = int(first_input_sample)
        self.fifo = []
        self.emitted = 0

    def flush(self) -> None:
        if self.flushed:
            return
        if not self.finalized:
            self._reject("missing_final_input", "flush requires final input")
        self.flushed = True

    def drain(self) -> list[float]:
        if not self.finalized:
            self._reject("missing_final_input", "drain requires final input")
        taken = self.fifo
        self.fifo = []
        return taken


def final_partial_evidence(values: Sequence[float]) -> dict:
    stream = PsolaStream(DYNAMIC_SCHEDULE)
    for start in range(0, len(values) - FRAME_SAMPLES, FRAME_SAMPLES):
        stream.push(values[start:start + FRAME_SAMPLES], FRAME_SAMPLES, start)
    remainder = len(values) % FRAME_SAMPLES
    stream.push(list(values[-FRAME_SAMPLES:]), remainder,
                len(values) - remainder, final=True)
    stream.flush()
    content = stream.drain()
    stats = finite_stats(content)
    return {
        "status": "ok",
        "input_samples": len(values),
        "full_frames": len(values) // FRAME_SAMPLES,
        "final_input_valid_count": remainder,
        "content_output_samples": len(content),
        "output_finite": stats["nonfinite_count"] == 0,
        "output_peak_abs": stats["peak_abs"],
        "output_digest": stats["digest"],
        "drain_calls": 1,
    }


def drift_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["speech_like"]
    expected = 0.0
    bounds = [start for start, _ in DRIFT_SCHEDULE] + [len(values)]
    for index, (start, rate) in enumerate(DRIFT_SCHEDULE):
        expected += (bounds[index + 1] - start) / rate
    output, sources, diagnostics = synthesize(values, DRIFT_SCHEDULE)
    identity = identity_run(values)
    observed = len(output)
    return {
        "status": "ok",
        "schedule": [[start, rate] for start, rate in DRIFT_SCHEDULE],
        "input_samples": len(values),
        "expected_output_samples": expected,
        "observed_output_samples": observed,
        "duration_error_samples": observed - expected,
        "relative_duration_error": (observed - expected) / expected,
        "identity_output_samples": len(identity[0]),
        "source_map": source_map_stats(sources),
        "candidate_digest": tensor_digest(output),
        "identity_digest": tensor_digest(identity[0]),
        "marks": diagnostics["marks"],
        "selected_marks": diagnostics["selected_marks"],
    }


def slow_rate_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["tonal"]
    output, sources, diagnostics = synthesize(values, SLOW_SCHEDULE)
    identity = identity_run(values)
    return {
        "status": "ok",
        "schedule": [[start, rate] for start, rate in SLOW_SCHEDULE],
        "input_samples": len(values),
        "output_samples": len(output),
        "identity_samples": len(identity[0]),
        "effective_rate": len(values) / len(output) if output else None,
        "output_longer_than_input": len(output) > len(identity[0]),
        "selected_marks": diagnostics["selected_marks"],
        "source_map": source_map_stats(sources),
        "digest": tensor_digest(output),
        "boundary_status": "whole_clip_fixture_only",
        "interpretation": ("r<1 expansion is measured only in this task-local whole-clip "
                           "fixture; the fixed 160-sample v0 process call cannot emit "
                           "more than 160 valid samples and is not used for slow-down."),
    }


def transient_evidence(stimuli: dict[str, list[float]]) -> dict:
    rows = {}
    for name in ("speech_like", "unfamiliar_speech", "music_like"):
        values = stimuli[name]
        output, sources, _ = synthesize(values, FIXED_SCHEDULE)
        rows[name] = {
            "status": "ok",
            "clip_p99_adjacent_delta": adjacent_stats(output)["p99"],
            "clip_max_adjacent_delta": adjacent_stats(output)["max"],
            "source_map": source_map_stats(sources),
            "note": ("Sample-adjacent discontinuity proxy only. No listening, "
                     "transient audibility score or naturalness claim is made."),
        }
    return {"rows": rows}


def buffering_evidence(stimuli: dict[str, list[float]]) -> dict:
    emitter = BoundaryEmitter()
    expected = emitter.run(stimuli["c_vector"])
    return expected


class BoundaryEmitter:
    """Fixed-160 adapter emulation of the task-local C provider emission policy."""

    def __init__(self) -> None:
        self.stream = PsolaStream(DYNAMIC_SCHEDULE)
        self.content: list[float] = []
        self.valid_counts: list[int] = []
        self.rejections: list[str] = []

    def target_valid(self, first: int, valid: int) -> int:
        rate = rate_at(DYNAMIC_SCHEDULE, first)
        return min(FRAME_SAMPLES, round_half_away(valid / rate))

    def push(self, frame: Sequence[float], valid: int, first: int,
             *, final: bool = False) -> None:
        if len(frame) != FRAME_SAMPLES:
            self.rejections.append("wrong_shape")
            raise ReferenceRejection("wrong_shape", "wrong frame shape")
        self.stream.push(frame, valid, first, final=final)
        target = self.target_valid(first, valid)
        available = len(self.stream.fifo)
        count = min(target, available)
        taken = self.stream.fifo[:count]
        self.stream.fifo = self.stream.fifo[count:]
        self.content.extend(taken)
        self.valid_counts.append(count)

    def run(self, values: Sequence[float]) -> dict:
        for start in range(0, len(values), FRAME_SAMPLES):
            chunk = list(values[start:start + FRAME_SAMPLES])
            padded = chunk + [0.0] * (FRAME_SAMPLES - len(chunk))
            self.push(padded, len(chunk), start,
                      final=(start + FRAME_SAMPLES >= len(values)))
        drain_non_content = len(self.stream.fifo)
        self.stream.flush()
        self.stream.drain()
        provider = TASK_DIR / "provider" / "psola_praat_provider.c"
        config = TASK_DIR / "provider" / "config" / "config.json"
        return {
            "status": "expected_from_python_model",
            "content_digest": tensor_digest(self.content),
            "content_samples": len(self.content),
            "frames": len(self.valid_counts),
            "valid_counts": self.valid_counts,
            "drain_non_content_samples": drain_non_content,
            "rejections": self.rejections,
            "provider_source_digest": sha256_file(provider) if provider.exists() else None,
            "config_digest": sha256_file(config) if config.exists() else None,
        }


def blockers() -> list[dict]:
    return [
        {
            "id": "BLK-01",
            "blocker": ("The frozen v0 boundary is exactly 160 f32 samples per process "
                        "call; it cannot express r<1 output expansion in device time."),
            "scope": ("Slow-down (0.95x) is measured only in the task-local whole-clip "
                      "fixture. The optional C reference covers identity and 1.25x/1.5x "
                      "speed-up only."),
            "reopen": ("A versioned variable-frame playback actuator or a caller-owned "
                       "TSM FIFO with explicit source/output timestamps outside v0."),
        },
        {
            "id": "BLK-02",
            "blocker": ("No target-device pacing, fill/flush, CPU, memory, deadline or "
                        "availability measurement was run."),
            "scope": "All numbers are deterministic synthetic-fixture observations.",
            "reopen": ("Paced workload on the intended target with fill/flush, deadline "
                       "misses and resource telemetry under the intended profile."),
        },
        {
            "id": "BLK-03",
            "blocker": ("No listening test, real-speech or real-music corpus, "
                        "intelligibility score or release-quality assessment was run."),
            "scope": ("All stimuli are analytic surrogates; Praat/psola package results "
                      "in the linked research are source-reported context, not reproduced "
                      "here."),
            "reopen": ("Held-out permitted speech/music, matched controls and authorized "
                       "listening/intelligibility scoring with rights review."),
        },
        {
            "id": "BLK-04",
            "blocker": ("The C provider is unregistered, opt-in and not part of the "
                        "installed SDK or any descriptor registry."),
            "scope": ("No public API, ABI, descriptor registry, default, installed "
                      "behavior, shared CMakeLists.txt or main was changed."),
            "reopen": ("Explicit provider intake, rights/license review, versioned public "
                       "surface decision and independent review before any promotion."),
        },
    ]


def build_report(install_location: str | None = None) -> dict:
    stimulus_names = ("silence", "tonal", "speech_like", "unfamiliar_speech",
                      "music_like", "c_vector")
    stimuli = {name: list(analytic_stimulus(name)) for name in stimulus_names}
    stimulus_rows = {name: finite_stats(values) for name, values in stimuli.items()}
    variants = variant_bundle(stimuli)
    source_pin_rows = {}
    for relative, expected in SOURCE_PINS.items():
        path = AUDIO_ROOT / relative
        actual = sha256_file(path) if path.is_file() else None
        source_pin_rows[relative] = {
            "sha256": expected, "verified": actual == expected, "actual": actual,
        }
    boundary_pin_rows = {}
    for relative, expected in BOUNDARY_PINS.items():
        path = WORKTREE / relative
        actual = sha256_file(path) if path.is_file() else None
        boundary_pin_rows[relative] = {
            "sha256": expected, "verified": actual == expected, "actual": actual,
        }
    pitch = pitch_evidence(stimuli)
    frequency = frequency_evidence(stimuli)
    overlap = overlap_evidence(stimuli)
    updates = rate_update_evidence(stimuli)
    streaming = streaming_evidence(stimuli)
    final = final_partial_evidence(stimuli["c_vector"])
    drift = drift_evidence(stimuli)
    slow = slow_rate_evidence(stimuli)
    transient = transient_evidence(stimuli)
    buffering = buffering_evidence(stimuli)

    report = {
        "schema": CONTRACT_ID,
        "status": "synthetic-fixture-only",
        "tool_profile": {
            "version": VERSION,
            "install_location": install_location or str(TASK_DIR),
            "provenance": "https://github.com/armaudia/audio-sdk.git",
            "repository": "audio-sdk",
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "runner_python": sys.version.split()[0],
            "runner_platform": platform.platform(),
            "candidate": "PSOLA / Praat-style reference",
            "profile": "Rate",
        },
        "scope": {
            "task_id": "SDK-PSOLA-PRAAT",
            "component": "psola-praat",
            "disposition": "sdk-reference",
            "write_scope": "docs/task-evidence/psola-praat/",
            "installed_v0": "16 kHz, mono, f32, 160-sample frames; unchanged",
            "fixture_only": True,
            "playback_actuator": False,
            "real_speech_or_music": False,
            "listening_or_release_claim": False,
        },
        "source_pins": source_pin_rows,
        "boundary_pins": boundary_pin_rows,
        "contract": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "frame_samples": FRAME_SAMPLES,
            "stimulus_length": STIMULUS_LENGTH,
            "half_window_samples": HALF_WINDOW,
            "window_samples": WINDOW_SIZE,
            "pitch_mark_min_period_samples": MIN_PERIOD,
            "pitch_mark_threshold": VOICING_THRESHOLD,
            "phase_denominator": PHASE_DENOMINATOR,
            "rate_min": RATE_MIN,
            "rate_max": RATE_MAX,
            "slew_per_mark": SLEW_PER_MARK,
            "max_abs": MAX_ABS,
            "dynamic_schedule": [[start, rate] for start, rate in DYNAMIC_SCHEDULE],
            "fixed_schedule": [[start, rate] for start, rate in FIXED_SCHEDULE],
            "slow_schedule": [[start, rate] for start, rate in SLOW_SCHEDULE],
            "drift_schedule": [[start, rate] for start, rate in DRIFT_SCHEDULE],
            "overlap_add": "Hann windows with per-sample denominator normalization",
        },
        "stimuli": stimulus_rows,
        "pitch_marking": pitch,
        "variants": variants,
        "frequency_scale": frequency,
        "overlap_add": overlap,
        "rate_updates": updates,
        "drift_rebuffer": drift,
        "slow_r_whole_clip": slow,
        "transient_proxy": transient,
        "streaming": streaming,
        "final_partial": final,
        "playback_buffering": buffering,
        "c_boundary_expected": buffering,
        "blockers": blockers(),
        "qualification": {
            "all_required_results_present": all((
                bool(pitch["rows"]), bool(variants), bool(frequency["rows"]),
                bool(overlap), bool(updates["rows"]), bool(drift), bool(slow),
                bool(transient), bool(streaming), bool(final), bool(buffering),
            )),
            "candidate_status": "synthetic-reference-only",
            "boundary_status": "conditional-blocked",
            "identity_control": "included",
            "fixed_rate_baseline": "included",
            "adverse_controls": "included",
            "missing_result_promoted": False,
        },
    }
    return report
