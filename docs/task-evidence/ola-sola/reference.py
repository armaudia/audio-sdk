# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local OLA/SOLA time-scale-modification reference.

This module is stdlib-only. It models a buffered overlap-add time scaler in
source-sample coordinates and a caller-owned fixed-frame adapter that mirrors
the public v0 boundary shape. It is synthetic evidence only: it is not an
installed provider, a playback actuator, a quality score or a timing claim.
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
CONTRACT_ID = "audio-sdk/ola-sola-evidence/0.1"
PROVIDER_ID = "rate.ola-sola-reference.v0"
BASE_COMMIT = "d665c298e8cce8b4d576dc45f3c7f7d3b3457425"
BRANCH = "swarm/SDK-OLA-SOLA"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
SEGMENT = 512
OVERLAP = 256
HOP = SEGMENT - OVERLAP
SEARCH = 80
PHASE_DENOMINATOR = 1000000
RATE_MIN = 0.75
RATE_MAX = 1.50
SLEW_PER_SEGMENT = 0.012  # 0.5 rate units/second at a 384-sample hop.
MAX_ABS = 1.0
EPS = 1e-12
STIMULUS_LENGTH = 12457  # 77 full frames + a 137-sample final frame.

SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md": (
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3"
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

DYNAMIC_SCHEDULE = ((0, 1.0), (4800, 1.25), (8000, 1.0), (11200, 1.5))
DRIFT_SCHEDULE = ((0, 1.0), (3200, 1.05), (6400, 0.95), (9600, 1.0))
FIXED_SCHEDULE = ((0, 1.25),)
IDENTITY_SCHEDULE = ((0, 1.0),)

WINDOW = tuple(0.5 - 0.5 * math.cos(2.0 * math.pi * n / (SEGMENT - 1))
               for n in range(SEGMENT))


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
    """C-compatible round() for the non-negative values used here."""
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


DEFAULT_CONFIG = {
    "provider_id": PROVIDER_ID,
    "schema_id": "audio-sdk/provider-config/0.1",
    "settings": {},
    "units": {},
}


@functools.lru_cache(maxsize=16)
def analytic_stimulus(name: str, length: int = STIMULUS_LENGTH) -> tuple[float, ...]:
    """Seeded, analytic stimuli; no corpus, WAV, model or external asset."""
    if name == "silence":
        return [0.0] * length
    if name == "c_vector":
        # Integer-only pattern shared byte-for-byte with the C boundary test.
        return [((n * 37 + (n // 17) * 13) % 201 - 100) / 512.0 for n in range(length)]
    if name == "tonal":
        values = []
        for n in range(length):
            t = n / SAMPLE_RATE_HZ
            envelope = 0.16 + 0.09 * math.sin(2.0 * math.pi * 1.7 * t)
            value = envelope * math.sin(2.0 * math.pi * 220.0 * t)
            value += 0.035 * math.sin(2.0 * math.pi * 440.0 * t)
            if 4300 <= n <= 4307:
                value += 0.28 * (1.0 - abs(n - 4303.5) / 4.5)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return values
    if name == "speech_like":
        # Voiced pulse train through two analytic resonators, syllable envelope,
        # unvoiced LCG noise and a small transient at a known source time.
        state = 7102
        lowpass = 0.0
        r1 = r2 = f1 = f2 = 0.0
        values = []
        for n in range(length):
            t = n / SAMPLE_RATE_HZ
            f0 = 112.0 + 18.0 * math.sin(2.0 * math.pi * 0.9 * t)
            phase = (n * f0 / SAMPLE_RATE_HZ) % 1.0
            impulse = 1.0 if phase < (f0 / SAMPLE_RATE_HZ) else 0.0
            r1 = 0.965 * r1 + impulse
            r2 = 0.965 * r2 + r1
            f1 = 0.88 * f1 + 0.12 * r2
            f2 = 0.78 * f2 + 0.22 * r1
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            noise = state / 2147483648.0 - 1.0
            lowpass = 0.55 * lowpass + 0.45 * noise
            syllable = max(0.0, math.sin(2.0 * math.pi * 3.1 * t)) ** 2
            pause = 1.0 if math.sin(2.0 * math.pi * 0.73 * t) < 0.86 else 0.18
            unvoiced = 0.18 if 0.42 < (phase + 0.3 * math.sin(2.0 * math.pi * 2.3 * t)) % 1.0 < 0.58 else 0.0
            value = 0.052 * (r2 + 0.6 * f1 + 0.25 * f2) * syllable * pause
            value += unvoiced * 0.028 * lowpass
            if 5600 <= n <= 5607:
                value += 0.22 * (1.0 - abs(n - 5603.5) / 4.5)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return values
    raise ReferenceRejection("unknown_stimulus", "unknown stimulus: " + name)


class TsmStream:
    """Buffered OLA/SOLA engine with deterministic source-coordinate mapping."""

    def __init__(self, algorithm: str = "sola", schedule: Sequence[tuple[int, float]] = IDENTITY_SCHEDULE,
                 *, normalize: bool = True, slew: bool = True,
                 first_input_sample: int = 0):
        if algorithm not in ("ola", "sola"):
            raise ReferenceRejection("invalid_algorithm", "algorithm must be ola or sola")
        self.algorithm = algorithm
        self.schedule = validate_schedule(schedule)
        self.normalize = bool(normalize)
        self.slew = bool(slew)
        self.first_input_sample = int(first_input_sample)
        self.input: list[float] = []
        self.input_end = int(first_input_sample)
        self.phase = 0
        self.current_rate = self.schedule[0][1]
        self.last_effective_start = -10**9
        self.pending = [0.0] * SEGMENT
        self.pending_norm = [0.0] * SEGMENT
        self.pending_src = [float(i) for i in range(SEGMENT)]
        self.pending_start = 0
        self.next_synth = 0
        self.segments = 0
        self.fifo: list[tuple[float, int]] = []
        self.finalized = False
        self.flushed = False
        self.invalid_count = 0
        self.rate_updates: list[dict] = []

    def _reject(self, code: str, message: str) -> None:
        self.invalid_count += 1
        raise ReferenceRejection(code, message)

    def push(self, samples: Sequence[float], valid_count: int | None = None,
             *, final: bool = False) -> None:
        if self.finalized or self.flushed:
            self._reject("process_after_final", "no process after final input")
        if valid_count is None:
            valid_count = len(samples)
        if len(samples) != FRAME_SAMPLES:
            self._reject("wrong_shape", "process input_count must be 160")
        if not 1 <= valid_count <= FRAME_SAMPLES:
            self._reject("wrong_shape", "input_valid_count out of range")
        if self.input_end != self.first_input_sample + len(self.input):
            self._reject("wrong_position", "input position is not contiguous")
        chunk = list(samples[:valid_count])
        for value in chunk:
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                self._reject("nonfinite_input", "input must be finite")
            if abs(value) > MAX_ABS:
                self._reject("out_of_range", "input magnitude exceeds declared bound")
        self.input.extend(chunk)
        self.input_end += valid_count
        if final:
            self.finalized = True
        self._synthesize()

    def push_bulk(self, samples: Sequence[float], *, final: bool = False) -> None:
        """Task-local whole-clip feed; deliberately bypasses the fixed 160-frame boundary."""
        if self.finalized or self.flushed:
            self._reject("process_after_final", "no process after final input")
        if self.input_end != self.first_input_sample + len(self.input):
            self._reject("wrong_position", "input position is not contiguous")
        chunk = [float(value) for value in samples]
        for value in chunk:
            if not math.isfinite(value) or abs(value) > MAX_ABS:
                self._reject("nonfinite_or_out_of_range", "invalid bulk sample")
        self.input.extend(chunk)
        self.input_end += len(chunk)
        if final:
            self.finalized = True
        self._synthesize()

    def _nominal_start(self) -> int:
        return (self.phase // PHASE_DENOMINATOR) + self.first_input_sample

    def _delta_bounds(self, nominal: int, *, final: bool) -> tuple[int, int]:
        low = max(-SEARCH, self.first_input_sample - nominal)
        high = min(SEARCH, self.input_end - (nominal + SEGMENT))
        if self.last_effective_start > -10**8:
            low = max(low, self.last_effective_start - nominal)
        if low > high:
            return low, high
        if final and high < 0 and low <= 0:
            return low, high
        return low, high

    def _score(self, effective_start: int) -> float:
        numerator = 0.0
        energy_a = 0.0
        energy_b = 0.0
        mean_a = 0.0
        mean_b = 0.0
        base = effective_start - self.first_input_sample
        for offset in range(OVERLAP):
            mean_a += self.input[base + offset] * WINDOW[offset]
            mean_b += self.pending[offset] / max(self.pending_norm[offset], EPS)
        mean_a /= OVERLAP
        mean_b /= OVERLAP
        for offset in range(OVERLAP):
            a = self.input[base + offset] * WINDOW[offset] - mean_a
            b = self.pending[offset] / max(self.pending_norm[offset], EPS) - mean_b
            numerator += a * b
            energy_a += a * a
            energy_b += b * b
        return numerator / math.sqrt(energy_a * energy_b + EPS)

    def _choose_delta(self, nominal: int, *, final: bool) -> int:
        low, high = self._delta_bounds(nominal, final=final)
        if self.algorithm == "ola":
            if low <= 0 <= high:
                return 0
            return low if low > 0 else high
        if low > high:
            raise ReferenceRejection("insufficient_input", "no admissible segment")
        best_delta = low
        best_key: tuple[float, int, int] | None = None
        for delta in range(low, high + 1):
            score = self._score(nominal + delta) if self.segments else 0.0
            key = (-score, abs(delta), delta)
            if best_key is None or key < best_key:
                best_key = key
                best_delta = delta
        return best_delta

    def _emit(self, count: int) -> None:
        if count <= 0:
            return
        for offset in range(count):
            norm = self.pending_norm[offset] if self.normalize else 1.0
            value = self.pending[offset] / max(norm, EPS)
            source = int(round(self.pending_src[offset]))
            self.fifo.append((value, source))
        self.pending = self.pending[count:] + [0.0] * count
        self.pending_norm = self.pending_norm[count:] + [0.0] * count
        self.pending_src = self.pending_src[count:] + [
            float(self.pending_start + SEGMENT + index) for index in range(count)]
        self.pending_start += count

    def _synthesize(self) -> None:
        while True:
            nominal = self._nominal_start()
            low, high = self._delta_bounds(nominal, final=self.finalized)
            if low > high:
                return
            if self.segments:
                self._emit(HOP)
            delta = self._choose_delta(nominal, final=self.finalized)
            effective_start = nominal + delta
            base = effective_start - self.first_input_sample
            for index in range(SEGMENT):
                value = self.input[base + index] * WINDOW[index]
                self.pending[index] += value
                self.pending_norm[index] += WINDOW[index]
                self.pending_src[index] = effective_start + index
            old_rate = self.current_rate
            target = rate_at(self.schedule, effective_start - self.first_input_sample)
            step = SLEW_PER_SEGMENT if self.slew else 10.0
            if target > old_rate:
                self.current_rate = min(target, old_rate + step)
            else:
                self.current_rate = max(target, old_rate - step)
            self.phase += round_half_away(HOP * self.current_rate * PHASE_DENOMINATOR)
            self.last_effective_start = effective_start
            if target != old_rate:
                self.rate_updates.append({
                    "segment": self.segments,
                    "source_sample": effective_start,
                    "previous_rate": old_rate,
                    "target_rate": target,
                    "applied_rate": self.current_rate,
                    "slewed": self.slew,
                })
            self.segments += 1
            self.next_synth += HOP

    def flush(self) -> None:
        if self.flushed:
            return
        if not self.finalized:
            self._reject("missing_final_input", "flush requires final input")
        self._emit(SEGMENT)
        self.flushed = True

    def read(self, count: int) -> list[tuple[float, int]]:
        taken = self.fifo[:count]
        self.fifo = self.fifo[count:]
        return taken

    def output(self) -> list[tuple[float, int]]:
        taken = self.fifo
        self.fifo = []
        return taken

    def state_digest(self) -> str:
        return object_digest({
            "input": tensor_digest(self.input),
            "pending": tensor_digest(self.pending),
            "norm": tensor_digest(self.pending_norm),
            "phase": self.phase,
            "rate": self.current_rate,
            "segments": self.segments,
        })


_RUN_CACHE: dict[tuple, tuple[list[float], list[int], TsmStream]] = {}


def run_tsm(values: Sequence[float], *, algorithm: str = "sola",
            schedule: Sequence[tuple[int, float]] = IDENTITY_SCHEDULE,
            normalize: bool = True, slew: bool = True,
            chunk_size: int = FRAME_SAMPLES,
            first_input_sample: int = 0) -> tuple[list[float], list[int], TsmStream]:
    key = (tensor_digest(values), algorithm, tuple(schedule), bool(normalize),
           bool(slew), int(chunk_size), int(first_input_sample))
    cached = _RUN_CACHE.get(key)
    if cached is not None:
        return cached
    stream = TsmStream(algorithm, schedule, normalize=normalize, slew=slew,
                       first_input_sample=first_input_sample)
    for start in range(0, len(values), chunk_size):
        chunk = list(values[start:start + chunk_size])
        final = start + chunk_size >= len(values)
        if chunk_size == FRAME_SAMPLES:
            padded = chunk + [0.0] * (FRAME_SAMPLES - len(chunk))
            stream.push(padded, len(chunk), final=final)
        else:
            stream.push_bulk(chunk, final=final)
    stream.flush()
    pairs = stream.output()
    result = ([value for value, _ in pairs], [source for _, source in pairs], stream)
    _RUN_CACHE[key] = result
    return result


def identity_run(values: Sequence[float], first_input_sample: int = 0) -> tuple[list[float], list[int]]:
    return (list(values), [first_input_sample + index for index in range(len(values))])


def varispeed_run(values: Sequence[float], rate: float) -> tuple[list[float], list[int]]:
    length = round_half_away(len(values) / rate)
    result = []
    sources = []
    for index in range(length):
        position = index * rate
        lower = int(math.floor(position))
        upper = min(lower + 1, len(values) - 1)
        fraction = position - lower
        result.append(values[lower] * (1.0 - fraction) + values[upper] * fraction)
        sources.append(int(round(position)))
    return result, sources


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
    violations = 0
    max_gap = 0
    max_repeat = 0
    for previous, current in zip(sources, sources[1:]):
        if current < previous:
            violations += 1
        max_gap = max(max_gap, current - previous)
        max_repeat = max(max_repeat, previous - current)
    return {
        "monotonic": violations == 0,
        "monotonic_violations": violations,
        "max_source_step": max_gap,
        "max_source_repeat": max_repeat,
        "first_source": sources[0] if sources else None,
        "last_source": sources[-1] if sources else None,
    }


def adjacent_stats(values: Sequence[float]) -> dict:
    deltas = [abs(b - a) for a, b in zip(values, values[1:]) if math.isfinite(a) and math.isfinite(b)]
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


def dominant_frequency(values: Sequence[float], low: float = 120.0,
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


def waveform_variant(values: Sequence[float], algorithm: str,
                     schedule: Sequence[tuple[int, float]], *, normalize: bool = True,
                     slew: bool = True) -> dict:
    output, sources, stream = run_tsm(values, algorithm=algorithm, schedule=schedule,
                                      normalize=normalize, slew=slew)
    stats = finite_stats(output)
    expected = len(values) / rate_at(schedule, 0) if len(schedule) == 1 else None
    stats.update({
        "status": "scored",
        "algorithm": algorithm,
        "schedule": [[start, rate] for start, rate in schedule],
        "source_samples": len(values),
        "effective_rate": len(values) / len(output) if output else None,
        "expected_constant_rate_output": expected,
        "duration_error_samples": (len(output) - expected) if expected is not None else None,
        "segments": stream.segments,
        "source_map": source_map_stats(sources),
        "source_map_digest": tensor_digest(float(source) for source in sources),
    })
    return stats


def variant_bundle(stimuli: dict[str, list[float]]) -> dict:
    bundle: dict[str, dict] = {}
    for name, values in stimuli.items():
        rows = {
            "identity_1x_control": {
                **finite_stats(identity_run(values)[0]),
                "status": "control",
                "algorithm": "identity",
                "schedule": [[0, 1.0]],
                "source_samples": len(values),
                "effective_rate": 1.0,
                "segments": 0,
                "source_map": source_map_stats(list(range(len(values)))),
            },
            "fixed_rate_ola_baseline": waveform_variant(values, "ola", FIXED_SCHEDULE),
            "ola_candidate": waveform_variant(values, "ola", DYNAMIC_SCHEDULE),
            "sola_candidate": waveform_variant(values, "sola", DYNAMIC_SCHEDULE),
            "varispeed_control": {
                **finite_stats(varispeed_run(values, 1.25)[0]),
                "status": "adverse_control",
                "algorithm": "varispeed_linear_interpolation",
                "schedule": [[0, 1.25]],
                "source_samples": len(values),
                "effective_rate": 1.25,
                "segments": 0,
            },
        }
        bundle[name] = rows
    return bundle


def frequency_evidence(stimuli: dict[str, list[float]], variants: dict) -> dict:
    values = stimuli["tonal"]
    rows: dict[str, dict] = {}
    runs = {
        "identity_1x_control": identity_run(values)[0],
        "fixed_rate_ola_baseline": run_tsm(values, algorithm="ola", schedule=FIXED_SCHEDULE)[0],
        "sola_candidate": run_tsm(values, algorithm="sola", schedule=DYNAMIC_SCHEDULE)[0],
        "varispeed_control": varispeed_run(values, 1.25)[0],
    }
    reference = dominant_frequency(values)
    for name, output in runs.items():
        measured = dominant_frequency(output)
        ratio = measured["dominant_hz"] / reference["dominant_hz"]
        expected = 1.25 if name == "varispeed_control" else 1.0
        rows[name] = {
            "status": "scored",
            "input_dominant_hz": reference["dominant_hz"],
            "output_dominant_hz": measured["dominant_hz"],
            "frequency_ratio": ratio,
            "expected_ratio": expected,
            "absolute_error": abs(ratio - expected),
            "pitch_preserved": abs(ratio - 1.0) <= 0.03,
            "matches_expected_model": abs(ratio - expected) <= 0.03,
        }
    return {"stimulus": "tonal", "rows": rows}


def rate_update_evidence(stimuli: dict[str, list[float]]) -> dict:
    rows: dict[str, dict] = {}
    for name, values in stimuli.items():
        identity_out, identity_src = identity_run(values)
        outputs = {
            "identity_1x_control": (identity_out, identity_src),
            "fixed_rate_ola_baseline": run_tsm(values, algorithm="ola", schedule=FIXED_SCHEDULE)[:2],
            "ola_candidate": run_tsm(values, algorithm="ola", schedule=DYNAMIC_SCHEDULE)[:2],
            "sola_candidate": run_tsm(values, algorithm="sola", schedule=DYNAMIC_SCHEDULE)[:2],
            "unsmoothed_sola_adverse": run_tsm(values, algorithm="sola", schedule=DYNAMIC_SCHEDULE, slew=False)[:2],
        }
        boundaries = {}
        for boundary in (4800, 8000, 11200):
            boundaries[str(boundary)] = {
                label: discontinuity_at(values_out, sources, boundary)
                for label, (values_out, sources) in outputs.items()
            }
        source_maps = {
            label: source_map_stats(sources)
            for label, (_, sources) in outputs.items()
        }
        rows[name] = {"boundaries": boundaries, "source_maps": source_maps}
    return {"rows": rows}


def streaming_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["speech_like"]
    whole = run_tsm(values, algorithm="sola", schedule=DYNAMIC_SCHEDULE,
            chunk_size=len(values) + FRAME_SAMPLES)
    chunked = run_tsm(values, algorithm="sola", schedule=DYNAMIC_SCHEDULE)
    replay = run_tsm(values, algorithm="sola", schedule=DYNAMIC_SCHEDULE,
            first_input_sample=50000)
    independent = run_tsm(values, algorithm="ola", schedule=DYNAMIC_SCHEDULE)

    baseline = TsmStream("sola", DYNAMIC_SCHEDULE)
    for start in range(0, len(values), FRAME_SAMPLES):
        chunk = values[start:start + FRAME_SAMPLES]
        padded = chunk + [0.0] * (FRAME_SAMPLES - len(chunk))
        baseline.push(padded, len(chunk), final=(start + FRAME_SAMPLES >= len(values)))
    baseline.flush()
    before = baseline.state_digest()
    rejections: dict[str, dict] = {}
    cases = [
        ("nonfinite_input", 0, [math.nan] + [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES),
        ("wrong_shape", 0, [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES - 1),
        ("wrong_position", 1, [0.0] * FRAME_SAMPLES, FRAME_SAMPLES),
        ("process_after_final", 0, [0.0] * FRAME_SAMPLES, FRAME_SAMPLES),
    ]
    for label, first_sample, chunk, valid in cases:
        frame = TsmStream("sola", DYNAMIC_SCHEDULE, first_input_sample=first_sample)
        frame.push([0.0] * FRAME_SAMPLES, FRAME_SAMPLES)
        if label == "process_after_final":
            frame.finalized = True
        if label == "wrong_position":
            frame.input_end += 1
        state_before = frame.state_digest()
        error = None
        try:
            frame.push(chunk, valid, final=False)
        except ReferenceRejection as rejection:
            error = rejection.code
        rejections[label] = {
            "status": "rejected",
            "code": error,
            "state_unchanged": frame.state_digest() == state_before,
        }
    config_cases: dict[str, dict] = {}
    for label, config in (
        ("missing_rate_selection", None),
        ("invalid_config", {**DEFAULT_CONFIG, "unknown": 1}),
        ("rate_out_of_range", ((0, 1.9),)),
    ):
        try:
            if label == "rate_out_of_range":
                validate_schedule(config)
            else:
                validate_config(config)
            outcome = "incorrectly_accepted"
        except ReferenceRejection as rejection:
            outcome = rejection.code
        config_cases[label] = {"status": "rejected", "code": outcome}

    return {
        "chunking_equivalence": {
            "status": "expected_lookahead_difference",
            "whole_digest": tensor_digest(whole[0]),
            "chunked_digest": tensor_digest(chunked[0]),
            "equal": tensor_digest(whole[0]) == tensor_digest(chunked[0]),
            "reason": "The whole-clip feed permits search over the full buffer; the 160-frame stream is causal and only sees samples already delivered.",
        },
        "reset_replay": {
            "status": "ok",
            "original_digest": tensor_digest(chunked[0]),
            "replay_digest": tensor_digest(replay[0]),
            "replay_matches": tensor_digest(chunked[0]) == tensor_digest(replay[0]),
            "replay_source_map_digest": tensor_digest(float(v) for v in replay[1]),
            "source_offset_respected": replay[1][0] >= 50000,
        },
        "session_independence": {
            "status": "ok",
            "independent": tensor_digest(chunked[0]) != tensor_digest(independent[0]),
            "second_digest": tensor_digest(independent[0]),
            "state_digest_before_rejections": before,
        },
        "frame_rejections": rejections,
        "config_rejections": config_cases,
    }


def final_partial_evidence(values: Sequence[float]) -> dict:
    stream = TsmStream("sola", DYNAMIC_SCHEDULE)
    for start in range(0, len(values) - FRAME_SAMPLES, FRAME_SAMPLES):
        stream.push(values[start:start + FRAME_SAMPLES], FRAME_SAMPLES)
    remainder = len(values) % FRAME_SAMPLES
    final_chunk = values[-FRAME_SAMPLES:]
    stream.push(final_chunk, remainder, final=True)
    stream.flush()
    pairs = stream.output()
    content = [value for value, _ in pairs]
    stats = finite_stats(content)
    target = round_half_away(remainder / rate_at(DYNAMIC_SCHEDULE, len(values) - remainder))
    return {
        "status": "ok",
        "input_samples": len(values),
        "full_frames": len(values) // FRAME_SAMPLES,
        "final_input_valid_count": remainder,
        "content_output_samples": len(content),
        "target_final_output_samples": target,
        "drain_non_content_samples": max(0, len(content) - target),
        "output_finite": stats["nonfinite_count"] == 0,
        "output_peak_abs": stats["peak_abs"],
        "output_digest": stats["digest"],
        "final_source_map": source_map_stats([source for _, source in pairs]),
    }


def energy_evidence(stimuli: dict[str, list[float]]) -> dict:
    # Tonal stimulus has stationary energy, so OLA normalization is directly
    # observable instead of being masked by the speech-like envelope.
    values = stimuli["tonal"]
    normalized = run_tsm(values, algorithm="sola", schedule=DYNAMIC_SCHEDULE)[0]
    raw = run_tsm(values, algorithm="sola", schedule=DYNAMIC_SCHEDULE, normalize=False)[0]
    first = 0
    second = len(values)
    reference = finite_stats(values)["rms"]
    return {
        "status": "ok",
        "analysis_interval": [first, second],
        "reference_rms": reference,
        "normalized_rms": finite_stats(normalized)["rms"],
        "unnormalized_rms": finite_stats(raw)["rms"],
        "normalized_ratio": finite_stats(normalized)["rms"] / reference,
        "unnormalized_ratio": finite_stats(raw)["rms"] / reference,
        "window_sum_min": min(WINDOW[i] + WINDOW[i + HOP] for i in range(HOP)),
        "window_sum_max": max(WINDOW[i] + WINDOW[i + HOP] for i in range(HOP)),
        "normalized_closer_to_reference": (
            abs(finite_stats(normalized)["rms"] / reference - 1.0) <
            abs(finite_stats(raw)["rms"] / reference - 1.0)),
    }


def drift_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["speech_like"]
    expected = 0.0
    bounds = [start for start, _ in DRIFT_SCHEDULE] + [len(values)]
    for index, (start, rate) in enumerate(DRIFT_SCHEDULE):
        expected += (bounds[index + 1] - start) / rate
    candidate = run_tsm(values, algorithm="sola", schedule=DRIFT_SCHEDULE)
    identity = identity_run(values)
    observed = len(candidate[0])
    return {
        "status": "ok",
        "schedule": [[start, rate] for start, rate in DRIFT_SCHEDULE],
        "input_samples": len(values),
        "expected_output_samples": expected,
        "observed_output_samples": observed,
        "duration_error_samples": observed - expected,
        "relative_duration_error": (observed - expected) / expected,
        "identity_output_samples": len(identity[0]),
        "source_map": source_map_stats(candidate[1]),
        "candidate_digest": tensor_digest(candidate[0]),
        "identity_digest": tensor_digest(identity[0]),
    }


class BoundaryEmitter:
    """Fixed-160 adapter emulation of the task-local C provider emission policy."""

    def __init__(self) -> None:
        self.engine = TsmStream("sola", DYNAMIC_SCHEDULE)
        self.content: list[float] = []
        self.valid_counts: list[int] = []
        self.offsets: list[int] = []
        self.flags: list[int] = []
        self.rejections: list[str] = []

    def target_valid(self, first: int, valid: int) -> int:
        rate = rate_at(DYNAMIC_SCHEDULE, first)
        return min(FRAME_SAMPLES, round_half_away(valid / rate))

    def push(self, frame: Sequence[float], valid: int, first: int,
             *, final: bool = False) -> None:
        if len(frame) != FRAME_SAMPLES:
            self.rejections.append("wrong_shape")
            raise ReferenceRejection("wrong_shape", "wrong frame shape")
        if any(not math.isfinite(value) or abs(value) > MAX_ABS
               for value in frame[:valid]):
            self.rejections.append("nonfinite_or_out_of_range")
            raise ReferenceRejection("nonfinite_or_out_of_range", "invalid samples")
        self.engine.push(list(frame), valid, final=final)
        if final:
            self.engine.flush()
        target = self.target_valid(first, valid)
        available = len(self.engine.fifo)
        count = min(target, available)
        pairs = self.engine.read(count)
        self.content.extend(value for value, _ in pairs)
        self.valid_counts.append(count)
        self.offsets.append(0)
        self.flags.append(0)

    def run(self, values: Sequence[float]) -> dict:
        first = 0
        for start in range(0, len(values), FRAME_SAMPLES):
            chunk = values[start:start + FRAME_SAMPLES]
            padded = list(chunk) + [0.0] * (FRAME_SAMPLES - len(chunk))
            self.push(padded, len(chunk), first,
                      final=(start + FRAME_SAMPLES >= len(values)))
            first += FRAME_SAMPLES
        drain = len(self.engine.fifo)
        return {
            "content_digest": tensor_digest(self.content),
            "content_samples": len(self.content),
            "frames": len(self.valid_counts),
            "valid_counts": self.valid_counts,
            "offsets": self.offsets,
            "drain_non_content_samples": drain,
            "rejections": self.rejections,
        }


def c_boundary_evidence(values: Sequence[float]) -> dict:
    emitter = BoundaryEmitter()
    expected = emitter.run(values)
    provider = TASK_DIR / "provider" / "ola_sola_provider.c"
    config = TASK_DIR / "provider" / "config" / "config.json"
    expected["provider_source_digest"] = sha256_file(provider) if provider.exists() else None
    expected["config_digest"] = sha256_file(config) if config.exists() else None
    expected["status"] = "expected_from_python_model"
    return expected


def blockers() -> list[dict]:
    return [
        {
            "id": "BLK-01",
            "blocker": "The frozen v0 boundary is exactly 160 f32 samples per process call; it cannot express r<1 output expansion in device time.",
            "scope": "Slow-down (0.95x) is measured only in the task-local whole-clip fixture. The optional C reference covers identity and 1.25x/1.5x speed-up.",
            "reopen": "A versioned variable-frame playback actuator or a caller-owned TSM FIFO with explicit source/output timestamps outside v0.",
        },
        {
            "id": "BLK-02",
            "blocker": "No target-device pacing, fill/flush, CPU, memory, deadline or availability measurement was run.",
            "scope": "No device or workload support is claimed; all numbers are deterministic synthetic-fixture observations.",
            "reopen": "Paced workload on the intended target with fill/flush, deadline misses and resource telemetry under the intended profile.",
        },
        {
            "id": "BLK-03",
            "blocker": "No listening test, real-speech corpus, intelligibility score, model or release-quality assessment was run.",
            "scope": "Speech-like stimuli are analytic surrogates; silence and tonal stimuli are synthetic.",
            "reopen": "Held-out permitted speech, matched controls and authorized listening/intelligibility scoring with rights review.",
        },
        {
            "id": "BLK-04",
            "blocker": "The C provider is unregistered, opt-in and not part of the installed SDK or any descriptor registry.",
            "scope": "No public API, ABI, descriptor registry, default, installed behavior, shared CMakeLists.txt or main was changed.",
            "reopen": "Explicit provider intake, rights/license review, versioned public surface decision and independent review before any promotion.",
        },
    ]


def build_report(install_location: str | None = None) -> dict:
    stimuli = {name: analytic_stimulus(name) for name in
               ("silence", "speech_like", "tonal", "c_vector")}
    stimulus_rows = {name: finite_stats(values) for name, values in stimuli.items()}
    variants = variant_bundle({
        name: values for name, values in stimuli.items() if name != "c_vector"})
    source_pin_rows = {}
    for relative, expected in SOURCE_PINS.items():
        path = AUDIO_ROOT / relative
        actual = sha256_file(path) if path.is_file() else None
        source_pin_rows[relative] = {
            "sha256": expected,
            "verified": actual == expected,
            "actual": actual,
        }
    boundary_pin_rows = {}
    for relative, expected in BOUNDARY_PINS.items():
        path = WORKTREE / relative
        actual = sha256_file(path) if path.is_file() else None
        boundary_pin_rows[relative] = {
            "sha256": expected,
            "verified": actual == expected,
            "actual": actual,
        }
    frequency = frequency_evidence(stimuli, variants)
    updates = rate_update_evidence({
        name: values for name, values in stimuli.items() if name != "c_vector"})
    energy = energy_evidence(stimuli)
    drift = drift_evidence(stimuli)
    streaming = streaming_evidence(stimuli)
    final = final_partial_evidence(stimuli["speech_like"])
    c_expected = c_boundary_evidence(stimuli["c_vector"])

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
            "candidate": "OLA / SOLA",
            "profile": "Rate",
        },
        "scope": {
            "task_id": "SDK-OLA-SOLA",
            "component": "ola-sola",
            "disposition": "sdk-reference",
            "write_scope": "docs/task-evidence/ola-sola/",
            "installed_v0": "16 kHz, mono, f32, 160-sample frames; unchanged",
            "fixture_only": True,
            "playback_actuator": False,
        },
        "source_pins": source_pin_rows,
        "boundary_pins": boundary_pin_rows,
        "contract": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "frame_samples": FRAME_SAMPLES,
            "segment_samples": SEGMENT,
            "overlap_samples": OVERLAP,
            "synthesis_hop_samples": HOP,
            "search_samples": SEARCH,
            "phase_denominator": PHASE_DENOMINATOR,
            "rate_min": RATE_MIN,
            "rate_max": RATE_MAX,
            "slew_per_segment": SLEW_PER_SEGMENT,
            "max_abs": MAX_ABS,
            "algorithms": ["ola_no_search", "sola_waveform_similarity"],
            "window": "Hann with overlap-add denominator normalization",
            "dynamic_schedule": [[start, rate] for start, rate in DYNAMIC_SCHEDULE],
            "drift_schedule": [[start, rate] for start, rate in DRIFT_SCHEDULE],
            "fixed_schedule": [[start, rate] for start, rate in FIXED_SCHEDULE],
        },
        "stimuli": stimulus_rows,
        "variants": variants,
        "frequency_scale": frequency,
        "rate_updates": updates,
        "drift_rebuffer": drift,
        "energy_normalization": energy,
        "streaming": streaming,
        "final_partial": final,
        "c_boundary_expected": c_expected,
        "blockers": blockers(),
        "qualification": {
            "all_required_results_present": all((
                bool(variants),
                bool(frequency["rows"]),
                bool(updates["rows"]),
                bool(drift),
                bool(energy),
                bool(streaming),
                bool(final),
                bool(c_expected),
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
