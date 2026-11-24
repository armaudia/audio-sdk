# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic frame-causal synthetic streaming time-stretch reference.

This module is stdlib-only. It models a trial-clock overlap-add time scaler
with a bounded, strictly causal backward alignment search in the style of
WSOLA. It is *not* Rubber Band source, a binary, a model, a real corpus or a
playback device. The fixed-160 adapter emulation mirrors the public v0 shape
only so that the task-local C boundary can be cross-checked byte-for-byte.
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
CONTRACT_ID = "audio-sdk/rubber-band-r3-streaming-evidence/0.1"
PROVIDER_ID = "rate.rubber-band-r3-streaming-reference.v0"
BASE_COMMIT = "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d"
BASE_COMMIT_AT_CLAIM = "add40f5cab979995b6114deb2a05302e547c148c"
BRANCH = "swarm/SDK-RUBBER-BAND-R3-STREAMING"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
GRAIN_SAMPLES = 512
OVERLAP_SAMPLES = 384
DENSITY = 2
ANALYSIS_HOP = GRAIN_SAMPLES - OVERLAP_SAMPLES
SYNTH_HOP = ANALYSIS_HOP // DENSITY
PHASE_DENOMINATOR = 1000000
SEARCH_RANGE = 32
REF_OFFSET = 192
SEARCH_LEN = 128
RATE_MIN = 0.75
RATE_MAX = 1.50
MAX_RATE_STEP = 0.02
MAX_ABS = 1.0
EPS = 1e-12
STIMULUS_LENGTH = 12457  # 77 full frames plus a 137-sample final frame

ALLOWED_GRAIN_SAMPLES = (256, 512)
ALLOWED_OVERLAP_RATIOS = (0.5, 0.75, 0.875)
ALLOWED_DENSITIES = (1, 2)

SOURCE_PINS = {
    "research/tsm-followup-20261101/README.md": (
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f"
    ),
    "cpp-library/pipeline-validation/playback-speed-candidates.md": (
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3"
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
}

BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h": (
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766"
    ),
    "api/include/audio_sdk/session_v0.h": (
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1"
    ),
}
BOARD_SNAPSHOT = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_SHA256_AT_READ = "13f84d550de514eb19c5559abfce3fdcc86d56003cf4cb7731961acc0c81eddc"

IDENTITY_SCHEDULE = ((0, 1.0),)
DYNAMIC_SCHEDULE = ((0, 1.0), (3200, 1.25), (6400, 1.0), (9600, 1.5))
DRIFT_SCHEDULE = ((0, 1.0), (3200, 1.05), (6400, 0.95), (9600, 1.0))
FIXED_SCHEDULE = ((0, 1.25),)
# Source-timestamped synthetic pause/filler policy: speech is never sped up,
# filler and pause intervals recover playback budget, unfamiliar speech is
# slowed modestly. No ASR, VAD, model or listening result is implied.
POLICY_SCHEDULE = ((0, 1.0), (3200, 1.25), (4000, 1.0),
                   (5600, 1.5), (6800, 0.9))
REBUFFER_SCHEDULE = ((0, 1.0), (3200, 1.0), (4000, 1.25),
                     (5600, 1.0), (6400, 1.5), (7200, 1.0))
RATE_BOUNDARIES = (3200, 4000, 5600, 6400, 6800, 7200, 9600)

DEFAULT_SETTINGS = {
    "grain_samples": GRAIN_SAMPLES,
    "overlap_samples": OVERLAP_SAMPLES,
    "density": DENSITY,
}
DENSITY1_SETTINGS = {**DEFAULT_SETTINGS, "density": 1}
FIXED_BASELINE_SETTINGS = {"grain_samples": 512, "overlap_samples": 256,
                           "density": 1}
DEFAULT_CONFIG = {
    "provider_id": PROVIDER_ID,
    "schema_id": "audio-sdk/provider-config/0.1",
    "settings": DEFAULT_SETTINGS,
    "units": {},
}

SPEECH_LABELS = (
    (0, 3200, "speech"),
    (3200, 4000, "filler"),
    (4000, 5600, "speech"),
    (5600, 6800, "pause"),
    (6800, 12457, "unfamiliar_speech"),
)


class ReferenceRejection(ValueError):
    """Deterministic rejection carrying a machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_json(report)
    return text, sha256_bytes(text.encode("utf-8"))


def tensor_digest(values: Iterable[float]) -> str:
    payload = b"".join(struct.pack("<f", float(value)) for value in values)
    return sha256_bytes(payload)


def object_digest(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def round_half_away(value: float) -> int:
    """C-compatible llround for the non-negative values used here."""
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
        raise ReferenceRejection("missing_rate_selection", "rate schedule required")
    clean: list[tuple[int, float]] = []
    previous = -1
    for row in schedule:
        if (not isinstance(row, (tuple, list)) or len(row) != 2 or
                not isinstance(row[0], int) or isinstance(row[0], bool) or
                not isinstance(row[1], (int, float)) or isinstance(row[1], bool)):
            raise ReferenceRejection("invalid_schedule", "malformed schedule row")
        start, rate = int(row[0]), float(row[1])
        if start <= previous or start < 0:
            raise ReferenceRejection("invalid_schedule", "rate starts must increase")
        if not math.isfinite(rate):
            raise ReferenceRejection("nonfinite_rate", "rate must be finite")
        if rate < RATE_MIN or rate > RATE_MAX:
            raise ReferenceRejection("rate_out_of_range", "rate outside declared bounds")
        previous = start
        clean.append((start, rate))
    if clean[0][0] != 0:
        raise ReferenceRejection("missing_rate_selection", "schedule must start at zero")
    return tuple(clean)


def validate_parameters(raw: object) -> dict:
    if not isinstance(raw, dict):
        raise ReferenceRejection("missing_parameter_set", "parameters must be an object")
    required = {"grain_samples", "overlap_samples", "density"}
    if not required.issubset(raw):
        raise ReferenceRejection("missing_parameter_set", "a parameter is missing")
    grain, overlap, density = (raw["grain_samples"], raw["overlap_samples"],
                               raw["density"])
    if any(not isinstance(value, int) or isinstance(value, bool)
           for value in (grain, overlap, density)):
        raise ReferenceRejection("invalid_parameters", "parameters must be integers")
    if grain not in ALLOWED_GRAIN_SAMPLES:
        raise ReferenceRejection("invalid_grain_size", "grain outside declared grid")
    if overlap <= 0 or overlap >= grain:
        raise ReferenceRejection("invalid_overlap", "overlap must lie inside the grain")
    ratio = overlap / grain
    if not any(math.isclose(ratio, allowed, rel_tol=1e-12, abs_tol=1e-12)
               for allowed in ALLOWED_OVERLAP_RATIOS):
        raise ReferenceRejection("invalid_overlap", "overlap ratio outside declared grid")
    if density not in ALLOWED_DENSITIES:
        raise ReferenceRejection("invalid_density", "density outside declared grid")
    analysis_hop = grain - overlap
    if analysis_hop % density != 0:
        raise ReferenceRejection("invalid_density", "density must divide analysis hop")
    synth_hop = analysis_hop // density
    if synth_hop <= 0:
        raise ReferenceRejection("invalid_density", "synthesis hop must be positive")
    return {"grain_samples": grain, "overlap_samples": overlap,
            "density": density, "analysis_hop_samples": analysis_hop,
            "synth_hop_samples": synth_hop, "overlap_ratio": ratio}


def validate_config(config: object) -> dict:
    required = {"provider_id", "schema_id", "settings", "units"}
    if not isinstance(config, dict) or set(config) != required:
        raise ReferenceRejection("invalid_config", "config keys do not match the schema")
    if config.get("provider_id") != PROVIDER_ID:
        raise ReferenceRejection("invalid_config", "wrong provider id")
    if config.get("schema_id") != "audio-sdk/provider-config/0.1":
        raise ReferenceRejection("invalid_config", "wrong config schema")
    if config.get("units") != {}:
        raise ReferenceRejection("invalid_config", "unexpected config units")
    validate_parameters(config.get("settings"))
    return dict(config)


@functools.lru_cache(maxsize=16)
def window_for(grain: int) -> tuple[float, ...]:
    """Exact rational Bartlett window; no libm dependence for C parity."""
    half = (grain + 1) // 2
    return tuple(float(min(index + 1, grain - index)) / float(half)
                 for index in range(grain))


def analytic_stimulus(name: str, length: int = STIMULUS_LENGTH) -> tuple[float, ...]:
    """Seeded analytic stimuli; no corpus, WAV, model or external asset."""
    if name == "silence":
        return (0.0,) * length
    if name == "c_vector":
        # Integer-only pattern shared byte-for-byte with the C boundary test.
        return tuple((((index * 41 + (index // 19) * 7) % 199 - 99) / 512.0)
                     for index in range(length))
    if name == "tonal":
        values = []
        for index in range(length):
            seconds = index / SAMPLE_RATE_HZ
            envelope = 0.16 + 0.09 * math.sin(2.0 * math.pi * 1.7 * seconds)
            value = envelope * math.sin(2.0 * math.pi * 220.0 * seconds)
            value += 0.035 * math.sin(2.0 * math.pi * 440.0 * seconds)
            if 4276 <= index <= 4324:
                value += 0.28 * (1.0 - abs(index - 4300) / 25.0)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return tuple(values)
    if name == "speech_like":
        # Formant/pulse surrogate with synthetic unfamiliar-speech character.
        state = 7102
        lowpass = 0.0
        r1 = r2 = f1 = f2 = 0.0
        values = []
        for index in range(length):
            seconds = index / SAMPLE_RATE_HZ
            f0 = 112.0 + 18.0 * math.sin(2.0 * math.pi * 0.9 * seconds)
            phase = (index * f0 / SAMPLE_RATE_HZ) % 1.0
            impulse = 1.0 if phase < (f0 / SAMPLE_RATE_HZ) else 0.0
            r1 = 0.965 * r1 + impulse
            r2 = 0.965 * r2 + r1
            f1 = 0.88 * f1 + 0.12 * r2
            f2 = 0.78 * f2 + 0.22 * r1
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            noise = state / 2147483648.0 - 1.0
            lowpass = 0.55 * lowpass + 0.45 * noise
            syllable = max(0.0, math.sin(2.0 * math.pi * 3.1 * seconds)) ** 2
            unvoiced = (0.18 if 0.42 < (phase + 0.3 * math.sin(
                2.0 * math.pi * 2.3 * seconds)) % 1.0 < 0.58 else 0.0)
            value = 0.052 * (r2 + 0.6 * f1 + 0.25 * f2) * syllable
            value += unvoiced * 0.028 * lowpass
            if 3200 <= index < 4000 or 5600 <= index < 6800:
                value *= 0.05  # synthetic filler / pause regions
            if 6800 <= index:
                value *= 0.78   # unfamiliar surrogate, not a real speaker
            if 5576 <= index <= 5624:
                value += 0.26 * (1.0 - abs(index - 5600) / 25.0)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return tuple(values)
    if name == "music_like":
        state = 9173
        values = []
        for index in range(length):
            seconds = index / SAMPLE_RATE_HZ
            chord = (0.11 * math.sin(2.0 * math.pi * 220.0 * seconds) +
                     0.09 * math.sin(2.0 * math.pi * 277.18 * seconds) +
                     0.07 * math.sin(2.0 * math.pi * 329.63 * seconds))
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            noise = state / 2147483648.0 - 1.0
            beat = math.exp(-((index % 2000) / 65.0) ** 2)
            value = chord * (0.7 + 0.3 * math.sin(2.0 * math.pi * 0.8 * seconds))
            value += 0.22 * beat * noise
            if 7176 <= index <= 7224:
                value += 0.24 * (1.0 - abs(index - 7200) / 25.0)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return tuple(values)
    raise ReferenceRejection("unknown_stimulus", "unknown stimulus: " + name)


class StreamTSM:
    """Causal OLA engine with bounded backward alignment search."""

    def __init__(self, schedule: Sequence[tuple[int, float]] = IDENTITY_SCHEDULE,
                 *, parameters: dict | None = None, alignment: bool = True,
                 normalize: bool = True, slew: bool = True,
                 first_input_sample: int = 0):
        self.params = validate_parameters(parameters or DEFAULT_SETTINGS)
        self.grain = int(self.params["grain_samples"])
        self.synth_hop = int(self.params["synth_hop_samples"])
        self.window = window_for(self.grain)
        self.schedule = validate_schedule(schedule)
        self.alignment = bool(alignment)
        self.normalize = bool(normalize)
        self.slew = bool(slew)
        self.first_input_sample = int(first_input_sample)
        self.input: list[float] = []
        self.input_start = int(first_input_sample)
        self.input_end = int(first_input_sample)
        self.phase = 0
        self.current_rate = self.schedule[0][1]
        self.target_rate = self.schedule[0][1]
        self.pending = [0.0] * self.grain
        self.pending_norm = [0.0] * self.grain
        self.pending_src = [float(first_input_sample + i)
                            for i in range(self.grain)]
        self.pending_start = int(first_input_sample)
        self.fifo: list[tuple[float, int]] = []
        self.segments = 0
        self.finalized = False
        self.flushed = False
        self.invalid_count = 0
        self.alignment_deltas: list[int] = []
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
        if valid_count == 0:
            self._reject("missing_input", "input_valid_count must be positive")
        if len(samples) != FRAME_SAMPLES:
            self._reject("wrong_shape", "process input_count must be 160")
        if not 1 <= valid_count <= FRAME_SAMPLES:
            self._reject("wrong_shape", "input_valid_count out of range")
        if self.input_end != self.first_input_sample + len(self.input):
            self._reject("wrong_position", "input position is not contiguous")
        chunk = list(samples[:valid_count])
        for value in chunk:
            if (not isinstance(value, (int, float)) or isinstance(value, bool)
                    or not math.isfinite(value)):
                self._reject("nonfinite_input", "input must be finite")
            if abs(value) > MAX_ABS:
                self._reject("out_of_range", "input magnitude exceeds declared bound")
        self.input.extend(chunk)
        self.input_end += valid_count
        if final:
            self.finalized = True
        self._synthesize()

    def push_bulk(self, samples: Sequence[float], *, final: bool = False) -> None:
        """Whole-clip feed outside the fixed 160-sample boundary."""
        if self.finalized or self.flushed:
            self._reject("process_after_final", "no process after final input")
        if self.input_end != self.first_input_sample + len(self.input):
            self._reject("wrong_position", "input position is not contiguous")
        chunk = [float(value) for value in samples]
        for value in chunk:
            if not math.isfinite(value):
                self._reject("nonfinite_input", "invalid bulk sample")
            if abs(value) > MAX_ABS:
                self._reject("out_of_range", "invalid bulk sample")
        self.input.extend(chunk)
        self.input_end += len(chunk)
        if final:
            self.finalized = True
        self._synthesize()

    def _emit(self, count: int) -> None:
        if count <= 0:
            return
        for offset in range(count):
            norm = self.pending_norm[offset] if self.normalize else 1.0
            value = self.pending[offset] / max(norm, EPS)
            self.fifo.append((value, int(round(self.pending_src[offset]))))
        tail = [float(self.pending_start + self.grain + index)
                for index in range(count)]
        self.pending = self.pending[count:] + [0.0] * count
        self.pending_norm = self.pending_norm[count:] + [0.0] * count
        self.pending_src = self.pending_src[count:] + tail
        self.pending_start += count

    def _search_delta(self, base: int) -> int:
        """Choose the best non-positive shift using only the current grain."""
        if not self.alignment:
            return 0
        # The correlation pair must fit inside the complete current grain for
        # every candidate shift, including the least-negative candidate.
        ref_offset = (self.grain - SEARCH_LEN) // 2
        best_delta = 0
        best_score: float | None = None
        for delta in range(0, -SEARCH_RANGE - 1, -1):
            candidate = base + delta
            if candidate < 0:
                continue
            score = 0.0
            for offset in range(SEARCH_LEN):
                score += (self.input[candidate + ref_offset + offset] *
                          self.input[base + ref_offset + offset])
            if best_score is None or score > best_score:
                best_score = score
                best_delta = delta
        return best_delta

    def _synthesize(self) -> None:
        while True:
            nominal = (self.phase // PHASE_DENOMINATOR) + self.input_start
            base = nominal - self.input_start
            if nominal + self.grain > self.input_end:
                return
            if self.segments:
                self._emit(self.synth_hop)
            delta = self._search_delta(base)
            candidate = base + delta
            for index in range(self.grain):
                weight = self.window[index]
                self.pending[index] += self.input[candidate + index] * weight
                self.pending_norm[index] += weight
                self.pending_src[index] = float(self.input_start + candidate + index)

            previous_rate = self.current_rate
            previous_target = self.target_rate
            target = rate_at(self.schedule, base)
            self.target_rate = target
            difference = target - previous_rate
            if not self.slew or abs(difference) <= MAX_RATE_STEP:
                self.current_rate = target
            else:
                step = MAX_RATE_STEP if difference > 0.0 else -MAX_RATE_STEP
                self.current_rate = previous_rate + step
            self.phase += round_half_away(
                self.synth_hop * self.current_rate * PHASE_DENOMINATOR)
            self.segments += 1
            self.alignment_deltas.append(delta)
            if previous_target != target or previous_rate != self.current_rate:
                self.rate_updates.append({
                    "segment": self.segments - 1,
                    "source_sample": nominal,
                    "source_ns": nominal * 62500,
                    "previous_rate": previous_rate,
                    "target_rate": target,
                    "applied_rate": self.current_rate,
                    "applied_step": self.current_rate - previous_rate,
                    "slewed": self.slew,
                })

    def flush(self) -> None:
        if self.flushed:
            return
        if not self.finalized:
            self._reject("missing_final_input", "flush requires final input")
        self._emit(self.grain)
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
            "deltas": self.alignment_deltas,
            "first_input_sample": self.first_input_sample,
        })


_RUN_CACHE: dict[tuple, tuple[list[float], list[int], StreamTSM]] = {}


def run_tsm(values: Sequence[float], *, schedule: Sequence[tuple[int, float]] = IDENTITY_SCHEDULE,
            parameters: dict | None = DEFAULT_SETTINGS, alignment: bool = True,
            normalize: bool = True, slew: bool = True,
            chunk_size: int = FRAME_SAMPLES,
            first_input_sample: int = 0) -> tuple[list[float], list[int], StreamTSM]:
    params = dict(parameters or DEFAULT_SETTINGS)
    key = (tensor_digest(values), tuple(schedule), canonical_json(params),
           bool(alignment), bool(normalize), bool(slew), int(chunk_size),
           int(first_input_sample))
    cached = _RUN_CACHE.get(key)
    if cached is not None:
        return cached
    stream = StreamTSM(schedule, parameters=params, alignment=alignment,
                       normalize=normalize, slew=slew,
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
    result = ([value for value, _ in pairs], [source for _, source in pairs],
              stream)
    _RUN_CACHE[key] = result
    return result


def identity_run(values: Sequence[float],
                 first_input_sample: int = 0) -> tuple[list[float], list[int]]:
    return (list(values),
            [first_input_sample + index for index in range(len(values))])


def varispeed_run(values: Sequence[float], rate: float) -> tuple[list[float], list[int]]:
    length = round_half_away(len(values) / rate)
    result: list[float] = []
    sources: list[int] = []
    for index in range(length):
        position = index * rate
        lower = int(math.floor(position))
        upper = min(lower + 1, len(values) - 1)
        fraction = position - lower
        result.append(values[lower] * (1.0 - fraction) + values[upper] * fraction)
        sources.append(round_half_away(position))
    return result, sources


def finite_stats(values: Sequence[float]) -> dict:
    finite = [math.isfinite(value) for value in values]
    peak = max((abs(value) for value in values if math.isfinite(value)),
               default=0.0)
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
    deltas = [abs(current - previous)
              for previous, current in zip(values, values[1:])
              if math.isfinite(previous) and math.isfinite(current)]
    if not deltas:
        return {"p99": 0.0, "max": 0.0}
    ordered = sorted(deltas)
    index = min(len(ordered) - 1, round_half_away(0.99 * len(ordered)) - 1)
    return {"p99": ordered[max(0, index)], "max": ordered[-1]}


def discontinuity_at(values: Sequence[float], sources: Sequence[int],
                     boundary: int, radius: int = 64) -> dict:
    index = next((position for position, source in enumerate(sources)
                  if source >= boundary), None)
    clip = adjacent_stats(values)
    if index is None:
        return {"status": "missing_boundary", "source_boundary": boundary,
                "clip_p99_adjacent_delta": clip["p99"]}
    low = max(1, index - radius)
    high = min(len(values), index + radius + 1)
    local = adjacent_stats(values[low:high])
    return {
        "status": "ok",
        "source_boundary": boundary,
        "output_index": index,
        "local_max_adjacent_delta": local["max"],
        "clip_p99_adjacent_delta": clip["p99"],
        "ratio_to_clip_p99": local["max"] / max(clip["p99"], EPS),
    }


def transient_at(values: Sequence[float], sources: Sequence[int],
                 boundary: int, radius: int = 24) -> dict:
    index = next((position for position, source in enumerate(sources)
                  if source >= boundary), None)
    if index is None:
        return {"status": "missing_boundary", "source_boundary": boundary,
                "local_peak_abs": None}
    low = max(0, index - radius)
    high = min(len(values), index + radius + 1)
    local = [abs(value) for value in values[low:high] if math.isfinite(value)]
    return {
        "status": "ok",
        "source_boundary": boundary,
        "output_index": index,
        "local_peak_abs": max(local, default=0.0),
        "analysis_window": [low, high],
        "audibility_measured": False,
    }


def goertzel(values: Sequence[float], frequency: float,
             rate: int = SAMPLE_RATE_HZ) -> float:
    coefficient = 2.0 * math.cos(2.0 * math.pi * frequency / rate)
    s1 = s2 = 0.0
    for index, value in enumerate(values):
        weight = 0.5 - 0.5 * math.cos(
            2.0 * math.pi * index / max(1, len(values) - 1))
        sample = value * weight
        s0 = sample + coefficient * s1 - s2
        s2, s1 = s1, s0
    return math.sqrt(max(0.0, s1 * s1 + s2 * s2 - coefficient * s1 * s2))


def dominant_frequency(values: Sequence[float], low: float = 120.0,
                       high: float = 520.0, *, start: int | None = None,
                       count: int = 2048) -> dict:
    if start is None:
        start = len(values) // 3
    stop = min(len(values), start + count)
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
    return {"dominant_hz": best_hz, "power": best_power,
            "analysis_interval": [start, stop],
            "analysis_samples": len(window)}


def expected_duration(schedule: Sequence[tuple[int, float]],
                      total_samples: int) -> float:
    bounds = [start for start, _ in schedule] + [total_samples]
    result = 0.0
    for index, (_, rate) in enumerate(schedule):
        result += (bounds[index + 1] - bounds[index]) / rate
    return result


def speech_preservation(sources: Sequence[int], schedule: Sequence[tuple[int, float]]
                       ) -> dict:
    """Policy compliance and coverage over source-timestamped intervals."""
    present = set(sources)
    rows = {}
    for start, end, label in SPEECH_LABELS:
        interval = range(start, min(end, STIMULUS_LENGTH))
        rate = rate_at(schedule, start)
        rows[str(start)] = {
            "label": label,
            "source_interval": [start, min(end, STIMULUS_LENGTH)],
            "source_ns_interval": [start * 62500, min(end, STIMULUS_LENGTH) * 62500],
            "applied_rate": rate,
            "rate_policy_ok": (rate <= 1.0 if label in ("speech", "unfamiliar_speech")
                               else rate >= 1.0),
            "covered_source_samples": sum(1 for sample in interval
                                          if sample in present),
            "source_samples": len(interval),
        }
    for row in rows.values():
        row["coverage"] = (row["covered_source_samples"] / row["source_samples"]
                           if row["source_samples"] else 0.0)
    return {
        "schedule": [[start, rate] for start, rate in schedule],
        "all_rate_decisions_at_source_timestamps": True,
        "rows": rows,
        "all_policy_rows_ok": all(row["rate_policy_ok"] for row in rows.values()),
        "protected_coverage_min": min(row["coverage"] for row in rows.values()
                                      if row["label"] in ("speech", "unfamiliar_speech")),
        "audibility_or_intelligibility_measured": False,
    }


class BoundaryEmitter:
    """Fixed-160 adapter emulation of the task-local C provider emission policy."""

    def __init__(self, schedule: Sequence[tuple[int, float]] = DYNAMIC_SCHEDULE):
        self.engine = StreamTSM(schedule, parameters=DEFAULT_SETTINGS)
        self.content: list[float] = []
        self.valid_counts: list[int] = []
        self.rejections: list[str] = []
        self.first_output_frame: int | None = None

    @staticmethod
    def target_valid(relative_first: int, valid: int,
                     schedule: Sequence[tuple[int, float]]) -> int:
        rate = rate_at(schedule, relative_first)
        return min(FRAME_SAMPLES, round_half_away(valid / rate))

    def push(self, frame: Sequence[float], valid: int, relative_first: int,
             schedule: Sequence[tuple[int, float]], *, final: bool = False) -> None:
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
        target = self.target_valid(relative_first, valid, schedule)
        count = min(target, len(self.engine.fifo))
        pairs = self.engine.read(count)
        if count and self.first_output_frame is None:
            self.first_output_frame = len(self.valid_counts)
        self.content.extend(value for value, _ in pairs)
        self.valid_counts.append(count)

    def run(self, values: Sequence[float],
            schedule: Sequence[tuple[int, float]] = DYNAMIC_SCHEDULE) -> dict:
        for start in range(0, len(values), FRAME_SAMPLES):
            chunk = list(values[start:start + FRAME_SAMPLES])
            padded = chunk + [0.0] * (FRAME_SAMPLES - len(chunk))
            self.push(padded, len(chunk), start, schedule,
                      final=(start + FRAME_SAMPLES >= len(values)))
        drain = len(self.engine.fifo)
        return {
            "content_digest": tensor_digest(self.content),
            "content_samples": len(self.content),
            "frames": len(self.valid_counts),
            "valid_counts": self.valid_counts,
            "drain_non_content_samples": drain,
            "first_output_frame": self.first_output_frame,
            "first_output_source_samples": (
                self.first_output_frame * FRAME_SAMPLES
                if self.first_output_frame is not None else None),
            "first_output_ms": (
                self.first_output_frame * FRAME_SAMPLES * 1000.0 / SAMPLE_RATE_HZ
                if self.first_output_frame is not None else None),
            "alignment_search_range_samples": SEARCH_RANGE,
            "rejections": self.rejections,
        }


def c_boundary_evidence(values: Sequence[float]) -> dict:
    expected = BoundaryEmitter().run(values)
    provider = TASK_DIR / "provider" / "rubber_band_r3_streaming_provider.c"
    config = TASK_DIR / "provider" / "config" / "config.json"
    expected["provider_source_digest"] = (sha256_file(provider)
                                          if provider.exists() else None)
    expected["config_digest"] = (sha256_file(config) if config.exists() else None)
    expected["status"] = "expected_from_python_model"
    return expected


def invalid_cases() -> dict:
    """Explicit invalid, missing, nonfinite and adverse cases; none qualifies."""
    results: dict[str, dict] = {}

    def record(label: str, fn) -> None:
        code = None
        try:
            fn()
        except ReferenceRejection as rejection:
            code = rejection.code
        results[label] = {"status": "rejected", "code": code,
                          "candidate_qualified": False}

    record("missing_parameter_set", lambda: validate_parameters(None))
    record("missing_density", lambda: validate_parameters(
        {"grain_samples": 512, "overlap_samples": 384}))
    record("invalid_grain_size", lambda: validate_parameters(
        {"grain_samples": 0, "overlap_samples": 0, "density": 2}))
    record("invalid_overlap", lambda: validate_parameters(
        {"grain_samples": 512, "overlap_samples": 512, "density": 2}))
    record("invalid_density_zero", lambda: validate_parameters(
        {"grain_samples": 512, "overlap_samples": 384, "density": 0}))
    record("invalid_density_divisor", lambda: validate_parameters(
        {"grain_samples": 512, "overlap_samples": 384, "density": 3}))
    record("missing_rate_selection", lambda: validate_schedule(None))
    record("nonfinite_rate", lambda: validate_schedule(
        ((0, 1.0), (1000, math.inf))))
    record("nan_rate", lambda: validate_schedule(((0, math.nan),)))
    record("rate_out_of_range", lambda: validate_schedule(((0, 1.9),)))
    record("invalid_config", lambda: validate_config(
        {**DEFAULT_CONFIG, "unknown": 1}))

    frame_cases = [
        ("nonfinite_input", [math.nan] + [0.0] * (FRAME_SAMPLES - 1),
         FRAME_SAMPLES, False, False),
        ("missing_valid_input", [0.0] * FRAME_SAMPLES, 0, False, False),
        ("wrong_shape", [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES - 1,
         False, False),
        ("wrong_position", [0.0] * FRAME_SAMPLES, FRAME_SAMPLES, True, False),
        ("process_after_final", [0.0] * FRAME_SAMPLES, FRAME_SAMPLES,
         False, True),
    ]
    for label, chunk, valid, corrupt_position, after_final in frame_cases:
        stream = StreamTSM(DYNAMIC_SCHEDULE, parameters=DEFAULT_SETTINGS)
        stream.push([0.0] * FRAME_SAMPLES, FRAME_SAMPLES)
        if corrupt_position:
            stream.input_end += 1
        if after_final:
            stream.finalized = True
        before = stream.state_digest()

        def attempt(chunk=chunk, valid=valid, stream=stream):
            stream.push(chunk, valid)

        code = None
        try:
            attempt()
        except ReferenceRejection as rejection:
            code = rejection.code
        results[label] = {"status": "rejected", "code": code,
                          "state_unchanged": stream.state_digest() == before,
                          "candidate_qualified": False}

    out_of_range = StreamTSM()
    try:
        out_of_range.push([1.5] + [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES)
    except ReferenceRejection as rejection:
        results["out_of_range"] = {"status": "rejected", "code": rejection.code,
                                   "candidate_qualified": False}
    unflushed = StreamTSM()
    unflushed.push([0.0] * FRAME_SAMPLES, FRAME_SAMPLES)
    try:
        unflushed.flush()
    except ReferenceRejection as rejection:
        results["missing_final_input"] = {
            "status": "rejected", "code": rejection.code,
            "candidate_qualified": False}
    return results
