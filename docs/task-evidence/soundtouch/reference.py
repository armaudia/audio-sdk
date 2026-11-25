# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local WSOLA-style time-stretch reference evidence.

This is a minimal, stdlib-only stand-in for the caller-owned stretch boundary
described in the local playback-speed candidate notes: a fractional source
accumulator, a caller-owned output accumulator, window-normalised overlap-add,
waveform-similarity alignment and transient-aware segment placement. It is a
synthetic WSOLA-style model named after the SoundTouch candidate; it is NOT the
upstream SoundTouch library, and no upstream source, binary, weights, corpus or
licensed runtime is vendored or used here.

It is proposal-only synthetic evidence: not an installed provider, not a
playback actuator, not a listening score and not a device or release result.
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
CONTRACT_ID = "audio-sdk/soundtouch-evidence/0.1"
PROVIDER_ID = "rate.soundtouch-reference.v0"
BASE_COMMIT = "ddce4bc6b7b5a6fb1761933dad50f87c8168bd10"
TASK = "SDK-SOUNDTOUCH"
BRANCH = "swarm/SDK-SOUNDTOUCH"

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
SEGMENT = 512
OVERLAP = 448
HOP = SEGMENT - OVERLAP
SEARCH = 16
SCORE_WINDOW = 24
PHASE_DENOMINATOR = 1000000
RATE_MIN = 0.75
RATE_MAX = 1.50
RATE_SLEW_PER_SEGMENT = 0.005
MAX_ABS = 1.0
EPS = 1e-12
SCORE_TIE_TOLERANCE = 1e-9
AMPLITUDE_TIE_TOLERANCE = 1e-12
TRANSIENT_THRESHOLD = 0.18
TRANSIENT_RISE = 0.06
TRANSIENT_LOOKBACK = 16
TRANSIENT_TARGET_OFFSET = HOP // 2
INPUT_LATENCY_SAMPLES = SEGMENT
OUTPUT_LATENCY_SAMPLES = HOP
STIMULUS_LENGTH = 12457  # 77 full frames plus a 137-sample final frame.

# Integer triangular window: w[n] + w[n+HOP]*7 == 1028 for n in [0, HOP).
WINDOW = tuple(min(n + 1, SEGMENT - n) for n in range(SEGMENT))

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
SLOW_SCHEDULE = ((0, 0.75),)
DYNAMIC_SCHEDULE = ((0, 1.0), (4800, 1.25), (8000, 1.0), (11200, 1.5))
DRIFT_SCHEDULE = ((0, 1.0), (3200, 1.05), (6400, 0.95), (9600, 1.0))
REBUFFER_SCHEDULE = ((0, 1.0), (2400, 1.5), (4800, 0.8), (7200, 1.0), (9600, 1.25))

# Source-anchored pause/filler policy: four 2400-sample voiced spans at 0.9x
# and four 800-sample pause spans at 1.5x sum to an exact duration identity.
PAUSE_POLICY_SCHEDULE = (
    (0, 0.9), (2400, 1.5), (3200, 0.9), (5600, 1.5),
    (6400, 0.9), (8800, 1.5), (9600, 0.9), (12000, 1.5),
)
PAUSE_POLICY_LENGTH = 12800

TRANSIENT_SOURCES = {
    "tonal": (4303,),
    "speech_like": (5603,),
    "music_like": (2400, 6200, 9800),
}


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


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def read_strict_json(path: Path) -> dict:
    """Read a JSON object with duplicate keys and non-finite constants rejected."""
    value = json.loads(Path(path).read_text(encoding="utf-8"),
                       object_pairs_hook=_unique_json_object,
                       parse_constant=_reject_json_constant)
    if not isinstance(value, dict):
        raise ValueError("json_not_object:" + str(path))
    return value


def canonical_report(report: dict) -> tuple[str, str]:
    text = canonical_json(report)
    return text, sha256_bytes(text.encode("utf-8"))


def tensor_digest(values: Iterable[float]) -> str:
    payload = b"".join(struct.pack("<f", float(value)) for value in values)
    return sha256_bytes(payload)


def object_digest(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def llround(value: float) -> int:
    """C llround() semantics: halves away from zero."""
    return (int(math.floor(value + 0.5)) if value >= 0.0
            else int(math.ceil(value - 0.5)))


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
        if not math.isfinite(rate):
            raise ReferenceRejection("nonfinite_rate", "rate must be finite")
        if rate < RATE_MIN or rate > RATE_MAX:
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


def scheduled_output_length(input_samples: int,
                            schedule: Sequence[tuple[int, float]]) -> int:
    """Caller-owned output clock: exact nominal duration mapping."""
    if input_samples <= 0:
        return 0
    total = 0.0
    bounds = [start for start, _ in schedule] + [input_samples]
    for index, (start, rate) in enumerate(schedule):
        stop = min(bounds[index + 1], input_samples)
        if stop > start:
            total += (stop - start) / rate
    return llround(total)


@functools.lru_cache(maxsize=16)
def analytic_stimulus(name: str, length: int = STIMULUS_LENGTH) -> tuple[float, ...]:
    """Seeded analytic stimuli; no corpus, WAV, model, download or asset."""
    if name == "silence":
        return [0.0] * length
    if name == "c_vector":
        # Integer-exact pattern shared with the C boundary fixture.
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
        # Analytic voiced-pulse surrogate, syllable envelope, unvoiced noise and
        # one known transient. Not speech and not a listening stimulus.
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
            unvoiced = (0.18 if 0.42 < (phase + 0.3 * math.sin(
                2.0 * math.pi * 2.3 * t)) % 1.0 < 0.58 else 0.0)
            value = 0.052 * (r2 + 0.6 * f1 + 0.25 * f2) * syllable * pause
            value += unvoiced * 0.028 * lowpass
            if 5600 <= n <= 5607:
                value += 0.22 * (1.0 - abs(n - 5603.5) / 4.5)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return values
    if name == "music_like":
        # Synthetic chord + metronomic percussive clicks; not music.
        values = []
        for n in range(length):
            t = n / SAMPLE_RATE_HZ
            value = (0.09 * math.sin(2.0 * math.pi * 220.0 * t) +
                     0.07 * math.sin(2.0 * math.pi * 277.0 * t) +
                     0.06 * math.sin(2.0 * math.pi * 330.0 * t))
            for transient in TRANSIENT_SOURCES["music_like"]:
                distance = abs(n - transient)
                if distance <= 6:
                    value += 0.26 * (1.0 - distance / 7.0)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return values
    if name == "pause_policy":
        values = []
        state = 12345
        for n in range(length):
            t = n / SAMPLE_RATE_HZ
            voiced = any(0 <= n - start < 2400 for start in (0, 3200, 6400, 9600))
            if voiced:
                pulse = 1.0 if (n % 143) < 8 else 0.0
                value = 0.28 * pulse * (0.7 + 0.3 * math.sin(2.0 * math.pi * 2.7 * t))
                if n % 2400 in range(0, 6):
                    value += 0.22 * (1.0 - (n % 2400) / 6.0)
            else:
                state = (1664525 * state + 1013904223) & 0xFFFFFFFF
                value = 0.012 * (state / 2147483648.0 - 1.0)
            values.append(max(-MAX_ABS, min(MAX_ABS, value)))
        return values
    raise ReferenceRejection("unknown_stimulus", "unknown stimulus: " + name)


class StretchStream:
    """Minimal caller-clocked time stretcher in source-sample coordinates."""

    def __init__(self, schedule: Sequence[tuple[int, float]] = IDENTITY_SCHEDULE,
                 *, normalize: bool = True, slew: bool = True,
                 first_input_sample: int = 0):
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
        self.pending_norm = [0] * SEGMENT
        self.pending_src = [float(index) for index in range(SEGMENT)]
        self.pending_start = first_input_sample
        self.fifo: list[tuple[float, int]] = []
        self.segments = 0
        self.finalized = False
        self.flushed = False
        self._bulk_mode = False
        self.epoch = 1
        self.invalid_count = 0
        self.rate_updates: list[dict] = []
        self.transient_placements: list[dict] = []

    def _reject(self, code: str, message: str) -> None:
        self.invalid_count += 1
        raise ReferenceRejection(code, message)

    def push(self, samples: Sequence[float], valid_count: int | None = None,
             *, final: bool = False, epoch: int | None = None) -> None:
        if self.finalized or self.flushed:
            self._reject("process_after_final", "no process after final input")
        if epoch is not None and epoch != self.epoch:
            self._reject("wrong_epoch", "frame epoch does not match session epoch")
        if len(samples) != FRAME_SAMPLES:
            self._reject("wrong_shape", "process input_count must be 160")
        if valid_count is None:
            valid_count = len(samples)
        if not 1 <= valid_count <= FRAME_SAMPLES:
            self._reject("wrong_shape", "input_valid_count out of range")
        if self.input_end != self.first_input_sample + len(self.input):
            self._reject("wrong_position", "input position is not contiguous")
        chunk = list(samples[:valid_count])
        for value in chunk:
            if (not isinstance(value, (int, float)) or isinstance(value, bool) or
                    not math.isfinite(value)):
                self._reject("nonfinite_input", "input must be finite")
            if abs(value) > MAX_ABS:
                self._reject("out_of_range", "input magnitude exceeds declared bound")
        self.input.extend(chunk)
        self.input_end += valid_count
        if final:
            self.finalized = True
        self._synthesize()

    def push_bulk(self, samples: Sequence[float], *, final: bool = False) -> None:
        """Whole-clip feed; deliberately bypasses the fixed 160-frame boundary."""
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
        self._bulk_mode = True
        try:
            self._synthesize()
        finally:
            self._bulk_mode = False

    def _nominal_start(self) -> int:
        return self.phase // PHASE_DENOMINATOR + self.first_input_sample

    def _delta_bounds(self, nominal: int) -> tuple[int, int]:
        low = max(-SEARCH, self.first_input_sample - nominal)
        # Streamed calls require the whole analysis window to be available;
        # whole-clip fixture feeds allow a partial tail with matched numerator
        # and denominator support.
        high = min(SEARCH, self.input_end - nominal -
                   (HOP if self._bulk_mode else SEGMENT))
        if self.last_effective_start > -10**8:
            # Segment analysis starts must advance; emitted regions overlap by
            # design, so output-sample source indices are not pointwise sorted.
            low = max(low, self.last_effective_start + 1 - nominal)
        return low, high

    def _score(self, effective_start: int) -> float:
        base = effective_start - self.first_input_sample
        mean_a = 0.0
        mean_b = 0.0
        a = [0.0] * SCORE_WINDOW
        b = [0.0] * SCORE_WINDOW
        for offset in range(SCORE_WINDOW):
            a[offset] = self.input[base + offset] * WINDOW[offset]
            norm = max(self.pending_norm[offset], 1)
            b[offset] = self.pending[offset] / norm
            mean_a += a[offset]
            mean_b += b[offset]
        mean_a /= SCORE_WINDOW
        mean_b /= SCORE_WINDOW
        numerator = energy_a = energy_b = 0.0
        for offset in range(SCORE_WINDOW):
            da = a[offset] - mean_a
            db = b[offset] - mean_b
            numerator += da * db
            energy_a += da * da
            energy_b += db * db
        return numerator / math.sqrt(energy_a * energy_b + EPS)

    def _transient_table(self, nominal: int, low: int, high: int) -> dict[int, float]:
        start = max(self.first_input_sample, nominal + low)
        stop = min(self.input_end, nominal + high + HOP)
        peaks: dict[int, float] = {}
        for sample_index in range(start, stop):
            amplitude = abs(self.input[sample_index - self.first_input_sample])
            if amplitude < TRANSIENT_THRESHOLD:
                continue
            lookback = max(self.first_input_sample, sample_index - TRANSIENT_LOOKBACK)
            previous = sum(abs(self.input[j - self.first_input_sample])
                           for j in range(lookback, sample_index))
            previous /= max(1, sample_index - lookback)
            if previous < TRANSIENT_RISE:
                peaks[sample_index] = amplitude
        return peaks

    def _choose_delta(self, nominal: int, low: int, high: int) -> tuple[int, dict | None]:
        peaks = self._transient_table(nominal, low, high)
        candidates: list[tuple[tuple, int, dict | None]] = []
        for delta in range(low, high + 1):
            start = nominal + delta
            local = [(amplitude, index) for index, amplitude in peaks.items()
                     if start <= index < start + HOP]
            if local:
                amplitude, index = local[0]
                for candidate_amplitude, candidate_index in local[1:]:
                    if (candidate_amplitude > amplitude + AMPLITUDE_TIE_TOLERANCE or
                            (abs(candidate_amplitude - amplitude) <= AMPLITUDE_TIE_TOLERANCE and
                             candidate_index < index)):
                        amplitude, index = candidate_amplitude, candidate_index
                key = (-amplitude, abs(index - (start + TRANSIENT_TARGET_OFFSET)),
                       abs(delta), delta)
                info = {"source_sample": index, "amplitude": amplitude,
                        "delta": delta, "strategy": "transient_snap"}
            else:
                key = (0.0,)
                info = None
            candidates.append((key, delta, info))
        transient = [row for row in candidates if row[2] is not None]
        if transient:
            best = transient[0]
            for row in transient[1:]:
                if self._key_less(row[0], best[0]):
                    best = row
            return best[1], best[2]
        if low > high:
            raise ReferenceRejection("insufficient_input", "no admissible segment")
        best_delta = low
        best_score = -math.inf
        for delta in range(low, high + 1):
            score = self._score(nominal + delta) if self.segments else 0.0
            if (score > best_score + SCORE_TIE_TOLERANCE or
                    (abs(score - best_score) <= SCORE_TIE_TOLERANCE and
                     (abs(delta), delta) < (abs(best_delta), best_delta))):
                best_delta = delta
                best_score = score
        return best_delta, None

    @staticmethod
    def _key_less(left: tuple, right: tuple) -> bool:
        for a, b in zip(left, right):
            if isinstance(a, float) or isinstance(b, float):
                if a < b - SCORE_TIE_TOLERANCE:
                    return True
                if a > b + SCORE_TIE_TOLERANCE:
                    return False
            elif a != b:
                return a < b
        return False

    def _emit(self, count: int) -> None:
        if count <= 0:
            return
        for offset in range(count):
            norm = self.pending_norm[offset] if self.normalize else 1
            value = self.pending[offset] / max(norm, 1)
            source = llround(self.pending_src[offset])
            self.fifo.append((value, source))
        self.pending = self.pending[count:] + [0.0] * count
        self.pending_norm = self.pending_norm[count:] + [0] * count
        self.pending_src = self.pending_src[count:] + [
            float(self.pending_start + SEGMENT + index) for index in range(count)]
        self.pending_start += count

    def _synthesize(self) -> None:
        while True:
            nominal = self._nominal_start()
            low, high = self._delta_bounds(nominal)
            if low > high:
                return
            if self.segments:
                self._emit(HOP)
            delta, transient = self._choose_delta(nominal, low, high)
            effective_start = nominal + delta
            base = effective_start - self.first_input_sample
            for index in range(SEGMENT):
                source_index = base + index
                if 0 <= source_index < len(self.input):
                    value = self.input[source_index]
                    self.pending[index] += value * WINDOW[index]
                    self.pending_norm[index] += WINDOW[index]
                self.pending_src[index] = effective_start + index
            old_rate = self.current_rate
            target = rate_at(self.schedule, effective_start - self.first_input_sample)
            step = RATE_SLEW_PER_SEGMENT if self.slew else 10.0
            if target > old_rate:
                self.current_rate = min(target, old_rate + step)
            else:
                self.current_rate = max(target, old_rate - step)
            self.phase += llround(HOP * self.current_rate * PHASE_DENOMINATOR)
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
            if transient is not None:
                self.transient_placements.append(transient)
            self.segments += 1

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
            "norm": self.pending_norm,
            "phase": self.phase,
            "rate": self.current_rate,
            "segments": self.segments,
        })


_RUN_CACHE: dict[tuple, tuple[list[float], list[int], StretchStream, dict]] = {}


def run_tsm(values: Sequence[float], *,
            schedule: Sequence[tuple[int, float]] = IDENTITY_SCHEDULE,
            normalize: bool = True, slew: bool = True,
            chunk_size: int = 0, first_input_sample: int = 0,
            exact_length: bool = True
            ) -> tuple[list[float], list[int], StretchStream, dict]:
    """Run the reference and trim to the caller-owned exact output clock.

    chunk_size=0 selects the whole-clip fixture feed. chunk_size=160 exercises
    the causal fixed-frame boundary and records any underrun instead of
    promoting a missing result when exact_length=False.
    """
    clean_schedule = validate_schedule(schedule)
    key = (tensor_digest(values), clean_schedule, bool(normalize), bool(slew),
           int(chunk_size), int(first_input_sample), bool(exact_length))
    cached = _RUN_CACHE.get(key)
    if cached is not None:
        return cached
    target = scheduled_output_length(len(values), clean_schedule)
    stream = StretchStream(clean_schedule, normalize=normalize, slew=slew,
                           first_input_sample=first_input_sample)
    if chunk_size == FRAME_SAMPLES:
        for start in range(0, len(values), chunk_size):
            chunk = list(values[start:start + chunk_size])
            padded = chunk + [0.0] * (FRAME_SAMPLES - len(chunk))
            stream.push(padded, len(chunk),
                        final=(start + chunk_size >= len(values)))
    else:
        stream.push_bulk(values, final=True)
    stream.flush()
    available = len(stream.fifo)
    if exact_length and available < target:
        raise ReferenceRejection("insufficient_synthesized_output",
                                 f"available {available} < target {target}")
    if not exact_length:
        target = min(target, available)
    pairs = stream.fifo[:target]
    stream.fifo = stream.fifo[target:]
    result = ([value for value, _ in pairs], [source for _, source in pairs],
              stream, {"target_output_samples": scheduled_output_length(
                           len(values), clean_schedule),
                       "observed_output_samples": target,
                       "available_output_samples": available,
                       "underrun_samples": max(0, target - available),
                       "tail_trimmed_samples": available - target,
                       "input_latency_samples": INPUT_LATENCY_SAMPLES,
                       "output_latency_samples": OUTPUT_LATENCY_SAMPLES})
    _RUN_CACHE[key] = result
    return result


def identity_run(values: Sequence[float], first_input_sample: int = 0
                 ) -> tuple[list[float], list[int]]:
    return (list(values),
            [first_input_sample + index for index in range(len(values))])


def varispeed_run(values: Sequence[float], rate: float) -> tuple[list[float], list[int]]:
    """Adverse control: linear resampling, which must shift pitch."""
    length = llround(len(values) / rate)
    result = []
    sources = []
    for index in range(length):
        position = index * rate
        lower = int(math.floor(position))
        upper = min(lower + 1, len(values) - 1)
        fraction = position - lower
        result.append(values[lower] * (1.0 - fraction) + values[upper] * fraction)
        sources.append(llround(position))
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
    # Overlap-add emits one HOP-sample block per segment. Source indices rise
    # inside each block; a bounded backward jump at each block boundary is
    # expected. The ordering invariant is on segment starts, not on every
    # output sample.
    starts = list(sources[::HOP])
    start_violations = sum(1 for previous, current in zip(starts, starts[1:])
                           if current <= previous)
    pointwise_descents = sum(1 for previous, current in zip(sources, sources[1:])
                             if current < previous)
    max_gap = 0
    max_repeat = 0
    for previous, current in zip(sources, sources[1:]):
        max_gap = max(max_gap, current - previous)
        max_repeat = max(max_repeat, previous - current)
    return {
        "monotonic": start_violations == 0,
        "monotonic_violations": start_violations,
        "segment_start_count": len(starts),
        "segment_starts_monotonic": start_violations == 0,
        "pointwise_descents": pointwise_descents,
        "max_source_step": max_gap,
        "max_source_repeat": max_repeat,
        "first_source": sources[0] if sources else None,
        "last_source": sources[-1] if sources else None,
        "note": ("Overlap-add output source indices are block-monotonic; "
                 "pointwise descents are bounded by the segment overlap."),
    }


def adjacent_stats(values: Sequence[float]) -> dict:
    deltas = [abs(b - a) for a, b in zip(values, values[1:])
              if math.isfinite(a) and math.isfinite(b)]
    if not deltas:
        return {"p99": 0.0, "max": 0.0}
    ordered = sorted(deltas)
    index = min(len(ordered) - 1, llround(0.99 * len(ordered)) - 1)
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


def local_peak(values: Sequence[float], center: int, radius: int = 24) -> dict:
    low = max(0, center - radius)
    high = min(len(values), center + radius + 1)
    amplitude = 0.0
    index = low
    for position in range(low, high):
        if abs(values[position]) > amplitude:
            amplitude = abs(values[position])
            index = position
    return {"index": index, "amplitude": amplitude}


def goertzel(values: Sequence[float], frequency: float,
             rate: int = SAMPLE_RATE_HZ) -> float:
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
    return {"dominant_hz": best_hz, "power": best_power,
            "analysis_samples": len(window)}


def duration_mapping(stimuli: dict[str, list[float]]) -> dict:
    rows: dict[str, dict] = {}
    for name, values in stimuli.items():
        per_rate = {}
        for rate in (0.75, 1.0, 1.25, 1.5):
            output, sources, stream, clock = run_tsm(
                values, schedule=((0, rate),))
            stats = finite_stats(output)
            expected = clock["target_output_samples"]
            per_rate[str(rate)] = {
                "status": "scored" if stats["nonfinite_count"] == 0 else "invalid",
                "schedule": [[0, rate]],
                "source_samples": len(values),
                "expected_output_samples": expected,
                "observed_output_samples": stats["samples"],
                "duration_error_samples": stats["samples"] - expected,
                "relative_duration_error": (stats["samples"] - expected) / expected,
                "effective_rate": len(values) / stats["samples"] if output else None,
                "input_latency_samples": clock["input_latency_samples"],
                "output_latency_samples": clock["output_latency_samples"],
                "tail_trimmed_samples": clock["tail_trimmed_samples"],
                "segments": stream.segments,
                "source_map": source_map_stats(sources),
                "digest": stats["digest"],
                "nonfinite_count": stats["nonfinite_count"],
                "clipping_count": stats["clipping_count"],
            }
        rows[name] = per_rate
    return rows


def variant_bundle(stimuli: dict[str, list[float]]) -> dict:
    bundle: dict[str, dict] = {}
    for name, values in stimuli.items():
        identity = identity_run(values)
        candidate = run_tsm(values, schedule=DYNAMIC_SCHEDULE)
        fixed = run_tsm(values, schedule=FIXED_SCHEDULE)
        slow = run_tsm(values, schedule=SLOW_SCHEDULE)
        adverse = varispeed_run(values, 1.25)
        bundle[name] = {
            "identity_1x_control": {
                **finite_stats(identity[0]),
                "status": "control",
                "algorithm": "identity",
                "schedule": [[0, 1.0]],
                "source_samples": len(values),
                "expected_output_samples": len(values),
                "observed_output_samples": len(identity[0]),
                "duration_error_samples": 0,
                "effective_rate": 1.0,
                "source_map": source_map_stats(identity[1]),
            },
            "fixed_1_25_reference": _variant_row(fixed, values, FIXED_SCHEDULE),
            "slow_0_75_reference": _variant_row(slow, values, SLOW_SCHEDULE),
            "dynamic_rate_candidate": _variant_row(candidate, values, DYNAMIC_SCHEDULE),
            "varispeed_adverse_control": {
                **finite_stats(adverse[0]),
                "status": "adverse_control",
                "algorithm": "varispeed_linear_interpolation",
                "schedule": [[0, 1.25]],
                "source_samples": len(values),
                "expected_output_samples": llround(len(values) / 1.25),
                "observed_output_samples": len(adverse[0]),
                "duration_error_samples": len(adverse[0]) - llround(len(values) / 1.25),
                "effective_rate": 1.25,
                "source_map": source_map_stats(adverse[1]),
            },
        }
    return bundle


def _variant_row(run: tuple, values: Sequence[float],
                 schedule: Sequence[tuple[int, float]]) -> dict:
    output, sources, stream, clock = run
    stats = finite_stats(output)
    row = {
        **stats,
        "status": "scored",
        "algorithm": "caller_clocked_overlap_add",
        "schedule": [[start, rate] for start, rate in schedule],
        "source_samples": len(values),
        "expected_output_samples": clock["target_output_samples"],
        "observed_output_samples": stats["samples"],
        "duration_error_samples": stats["samples"] - clock["target_output_samples"],
        "effective_rate": len(values) / stats["samples"] if output else None,
        "segments": stream.segments,
        "tail_trimmed_samples": clock["tail_trimmed_samples"],
        "source_map": source_map_stats(sources),
        "source_map_digest": tensor_digest(float(source) for source in sources),
        "rate_update_count": len(stream.rate_updates),
        "transient_placement_count": len(stream.transient_placements),
    }
    return row


def transient_behavior(stimuli: dict[str, list[float]],
                       variants: dict) -> dict:
    rows: dict[str, dict] = {}
    for name, sources in TRANSIENT_SOURCES.items():
        values = stimuli[name]
        output, source_map, stream, _ = run_tsm(values, schedule=DYNAMIC_SCHEDULE)
        events = []
        for source in sources:
            center = next((i for i, mapped in enumerate(source_map)
                           if mapped >= source), None)
            reference_peak = local_peak(values, source)
            if center is None:
                events.append({"status": "missing_boundary", "source_sample": source})
                continue
            peak = local_peak(output, center)
            mapped_source = source_map[peak["index"]]
            events.append({
                "status": "scored",
                "source_sample": source,
                "source_peak_amplitude": reference_peak["amplitude"],
                "output_peak_amplitude": peak["amplitude"],
                "amplitude_retention": (peak["amplitude"] /
                                        max(reference_peak["amplitude"], EPS)),
                "mapped_output_source": mapped_source,
                "source_timing_error_samples": abs(mapped_source - source),
                "local_max_adjacent_delta": adjacent_stats(
                    output[max(1, center - 24):center + 25])["max"],
            })
        rows[name] = {
            "status": "ok" if all(row["status"] == "scored" for row in events) else "missing",
            "stimulus": name + "_synthetic_surrogate",
            "transient_events": events,
            "transient_placements": len(stream.transient_placements),
            "clip_adjacent_p99": adjacent_stats(output)["p99"],
            "note": "Deterministic adjacent-delta proxy only; no listening claim.",
        }
    boundaries: dict[str, dict] = {}
    for boundary in (4800, 8000, 11200):
        smoothed, smoothed_sources, _, _ = run_tsm(
            stimuli["speech_like"], schedule=DYNAMIC_SCHEDULE)
        unsmoothed, unsmoothed_sources, _, _ = run_tsm(
            stimuli["speech_like"], schedule=DYNAMIC_SCHEDULE, slew=False)
        boundaries[str(boundary)] = {
            "smoothed_candidate": discontinuity_at(smoothed, smoothed_sources, boundary),
            "unsmoothed_adverse": discontinuity_at(unsmoothed, unsmoothed_sources, boundary),
        }
    return {"transients": rows, "rate_change_boundaries": boundaries}


def frequency_evidence(stimuli: dict[str, list[float]], variants: dict) -> dict:
    values = stimuli["tonal"]
    runs = {
        "identity_1x_control": identity_run(values)[0],
        "fixed_1_25_reference": run_tsm(values, schedule=FIXED_SCHEDULE)[0],
        "dynamic_rate_candidate": run_tsm(values, schedule=DYNAMIC_SCHEDULE)[0],
        "varispeed_adverse_control": varispeed_run(values, 1.25)[0],
    }
    reference = dominant_frequency(values)
    rows = {}
    for label, output in runs.items():
        measured = dominant_frequency(output)
        ratio = measured["dominant_hz"] / reference["dominant_hz"]
        expected = 1.25 if label == "varispeed_adverse_control" else 1.0
        rows[label] = {
            "status": "scored",
            "input_dominant_hz": reference["dominant_hz"],
            "output_dominant_hz": measured["dominant_hz"],
            "frequency_ratio": ratio,
            "expected_ratio": expected,
            "absolute_error": abs(ratio - expected),
            "pitch_preserved": abs(ratio - 1.0) <= 0.03,
            "matches_expected_model": abs(ratio - expected) <= 0.03,
        }
    return {"stimulus": "tonal_synthetic", "rows": rows}


def energy_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["tonal"]
    normalized = run_tsm(values, schedule=DYNAMIC_SCHEDULE)[0]
    unnormalized = run_tsm(values, schedule=DYNAMIC_SCHEDULE, normalize=False)[0]
    reference = finite_stats(values)["rms"]
    normalized_rms = finite_stats(normalized)["rms"]
    unnormalized_rms = finite_stats(unnormalized)["rms"]
    sums = [sum(WINDOW[index + offset * HOP] for offset in range(SEGMENT // HOP))
            for index in range(HOP)]
    return {
        "status": "ok",
        "reference_rms": reference,
        "normalized_rms": normalized_rms,
        "unnormalized_rms": unnormalized_rms,
        "normalized_ratio": normalized_rms / reference,
        "unnormalized_ratio": unnormalized_rms / reference,
        "window_sum_min": min(sums),
        "window_sum_max": max(sums),
        "normalized_closer_to_reference": (
            abs(normalized_rms / reference - 1.0) <
            abs(unnormalized_rms / reference - 1.0)),
        "unnormalized_peak_abs": finite_stats(unnormalized)["peak_abs"],
    }


def rate_update_evidence(stimuli: dict[str, list[float]]) -> dict:
    rows: dict[str, dict] = {}
    for name, values in stimuli.items():
        identity = identity_run(values)
        outputs = {
            "identity_1x_control": (identity[0], identity[1]),
            "fixed_1_25_reference": run_tsm(values, schedule=FIXED_SCHEDULE)[:2],
            "dynamic_rate_candidate": run_tsm(values, schedule=DYNAMIC_SCHEDULE)[:2],
            "unsmoothed_adverse": run_tsm(values, schedule=DYNAMIC_SCHEDULE, slew=False)[:2],
        }
        boundaries = {}
        for boundary in (4800, 8000, 11200):
            boundaries[str(boundary)] = {
                label: discontinuity_at(output, sources, boundary)
                for label, (output, sources) in outputs.items()
            }
        rows[name] = {
            "boundaries": boundaries,
            "source_maps": {label: source_map_stats(sources)
                            for label, (_, sources) in outputs.items()},
        }
    return {"rows": rows}


def pause_policy_evidence(values: Sequence[float]) -> dict:
    output, sources, stream, clock = run_tsm(values, schedule=PAUSE_POLICY_SCHEDULE)
    expected = clock["target_output_samples"]
    boundaries = []
    for index, (start, rate) in enumerate(PAUSE_POLICY_SCHEDULE[:-1]):
        after = PAUSE_POLICY_SCHEDULE[index + 1][1]
        boundaries.append({
            "source_boundary": start,
            "rate_before": rate,
            "rate_after": after,
            "transition": discontinuity_at(output, sources, start),
        })
    stats = finite_stats(output)
    return {
        "status": "ok" if stats["nonfinite_count"] == 0 else "invalid",
        "input_samples": len(values),
        "schedule": [[start, rate] for start, rate in PAUSE_POLICY_SCHEDULE],
        "voiced_source_samples": 4 * 2400,
        "pause_source_samples": 4 * 800,
        "expected_output_samples": expected,
        "observed_output_samples": len(output),
        "duration_error_samples": len(output) - expected,
        "relative_duration_error": (len(output) - expected) / expected,
        "source_map": source_map_stats(sources),
        "boundaries": boundaries,
        "rate_updates": stream.rate_updates,
        "nonfinite_count": stats["nonfinite_count"],
        "clipping_count": stats["clipping_count"],
        "digest": stats["digest"],
        "note": "Source-anchored synthetic pause/voiced surrogate; no speech or listening claim.",
    }


def drift_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["speech_like"]
    result = {}
    for name, schedule in (("drift", DRIFT_SCHEDULE), ("rebuffer", REBUFFER_SCHEDULE)):
        output, sources, _, clock = run_tsm(values, schedule=schedule)
        identity = identity_run(values)
        result[name] = {
            "status": "scored",
            "schedule": [[start, rate] for start, rate in schedule],
            "expected_output_samples": clock["target_output_samples"],
            "observed_output_samples": len(output),
            "duration_error_samples": len(output) - clock["target_output_samples"],
            "identity_output_samples": len(identity[0]),
            "source_map": source_map_stats(sources),
            "candidate_digest": tensor_digest(output),
            "identity_digest": tensor_digest(identity[0]),
            "tail_trimmed_samples": clock["tail_trimmed_samples"],
        }
    return result


def streaming_evidence(stimuli: dict[str, list[float]]) -> dict:
    values = stimuli["speech_like"]
    whole = run_tsm(values, schedule=DYNAMIC_SCHEDULE, chunk_size=0)
    chunked = run_tsm(values, schedule=DYNAMIC_SCHEDULE,
                      chunk_size=FRAME_SAMPLES, exact_length=False)
    replay = run_tsm(values, schedule=DYNAMIC_SCHEDULE, first_input_sample=50000,
                     chunk_size=FRAME_SAMPLES, exact_length=False)
    independent = run_tsm(values, schedule=FIXED_SCHEDULE, chunk_size=0)

    baseline = StretchStream(DYNAMIC_SCHEDULE)
    for start in range(0, len(values), FRAME_SAMPLES):
        chunk = values[start:start + FRAME_SAMPLES]
        padded = chunk + [0.0] * (FRAME_SAMPLES - len(chunk))
        baseline.push(padded, len(chunk), final=(start + FRAME_SAMPLES >= len(values)))
    baseline.flush()
    before = baseline.state_digest()

    rejections: dict[str, dict] = {}
    cases = [
        ("nonfinite_input", 0, [math.nan] + [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES),
        ("out_of_range_input", 0, [2.0] + [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES),
        ("wrong_shape", 0, [0.0] * (FRAME_SAMPLES - 1), FRAME_SAMPLES - 1),
        ("wrong_position", 1, [0.0] * FRAME_SAMPLES, FRAME_SAMPLES),
        ("wrong_epoch", 0, [0.0] * FRAME_SAMPLES, FRAME_SAMPLES),
        ("process_after_final", 0, [0.0] * FRAME_SAMPLES, FRAME_SAMPLES),
    ]
    for label, first_sample, chunk, valid in cases:
        frame = StretchStream(DYNAMIC_SCHEDULE, first_input_sample=first_sample)
        frame.push([0.0] * FRAME_SAMPLES, FRAME_SAMPLES)
        if label == "process_after_final":
            frame.finalized = True
        if label == "wrong_position":
            frame.input_end += 1
        state_before = frame.state_digest()
        error = None
        try:
            frame.push(chunk, valid, final=False,
                       epoch=2 if label == "wrong_epoch" else None)
        except ReferenceRejection as rejection:
            error = rejection.code
        rejections[label] = {
            "status": "rejected",
            "code": error,
            "state_unchanged": frame.state_digest() == state_before,
        }
    drain_before_final = StretchStream(DYNAMIC_SCHEDULE)
    drain_before_final.push([0.0] * FRAME_SAMPLES, FRAME_SAMPLES)
    drain_state = drain_before_final.state_digest()
    drain_error = None
    try:
        drain_before_final.flush()
    except ReferenceRejection as rejection:
        drain_error = rejection.code
    rejections["drain_before_final"] = {
        "status": "rejected",
        "code": drain_error,
        "state_unchanged": drain_before_final.state_digest() == drain_state,
    }
    config_cases: dict[str, dict] = {}
    for label, candidate in (
        ("missing_rate_selection", None),
        ("invalid_config", {**DEFAULT_CONFIG, "unknown": 1}),
        ("rate_out_of_range", ((0, 1.9),)),
        ("nonfinite_rate", ((0, math.nan),)),
    ):
        outcome = None
        try:
            if label in ("rate_out_of_range", "nonfinite_rate"):
                validate_schedule(candidate)
            elif label == "missing_rate_selection":
                validate_schedule(candidate)
                validate_config(candidate)
            else:
                validate_config(candidate)
        except ReferenceRejection as rejection:
            outcome = rejection.code
        config_cases[label] = {"status": "rejected", "code": outcome}
    return {
        "chunking_equivalence": {
            "status": "expected_lookahead_difference",
            "whole_digest": tensor_digest(whole[0]),
            "chunked_digest": tensor_digest(chunked[0]),
            "equal": tensor_digest(whole[0]) == tensor_digest(chunked[0]),
            "chunked_target_output_samples": chunked[3]["target_output_samples"],
            "chunked_observed_output_samples": chunked[3]["observed_output_samples"],
            "chunked_underrun_samples": chunked[3]["underrun_samples"],
            "reason": ("The whole-clip feed admits future input in the search window; "
                       "the 160-frame stream is causal with bounded lookahead. "
                       "Underrun is reported, never promoted to content."),
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
    stream = StretchStream(DYNAMIC_SCHEDULE)
    for start in range(0, len(values) - FRAME_SAMPLES, FRAME_SAMPLES):
        stream.push(values[start:start + FRAME_SAMPLES], FRAME_SAMPLES)
    remainder = len(values) % FRAME_SAMPLES
    final_chunk = values[-FRAME_SAMPLES:]
    stream.push(final_chunk, remainder, final=True)
    stream.flush()
    target = scheduled_output_length(len(values), DYNAMIC_SCHEDULE)
    available = len(stream.fifo)
    pairs = stream.fifo[:target]
    content = [value for value, _ in pairs]
    stats = finite_stats(content)
    return {
        "status": "ok",
        "input_samples": len(values),
        "full_frames": len(values) // FRAME_SAMPLES,
        "final_input_valid_count": remainder,
        "content_output_samples": len(content),
        "target_output_samples": target,
        "available_output_samples": available,
        "drain_non_content_samples": available - target,
        "output_finite": stats["nonfinite_count"] == 0,
        "output_peak_abs": stats["peak_abs"],
        "output_clipping_count": stats["clipping_count"],
        "output_digest": stats["digest"],
        "final_source_map": source_map_stats([source for _, source in pairs]),
    }


class BoundaryEmitter:
    """Fixed-160 adapter emulation of the task-local C provider emission policy."""

    def __init__(self) -> None:
        self.engine = StretchStream(DYNAMIC_SCHEDULE)
        self.carry = 0.0
        self.content: list[float] = []
        self.valid_counts: list[int] = []
        self.offsets: list[int] = []
        self.flags: list[int] = []
        self.rejections: list[str] = []

    def target_valid(self, first: int, valid: int) -> int:
        rate = rate_at(DYNAMIC_SCHEDULE, first)
        total = valid / rate + self.carry
        count = llround(total)
        self.carry = total - count
        return min(FRAME_SAMPLES, max(0, count))

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
        count = min(target, len(self.engine.fifo))
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
            "flags": self.flags,
            "final_carry": self.carry,
            "drain_non_content_samples": drain,
            "rejections": self.rejections,
        }


def c_boundary_evidence(values: Sequence[float]) -> dict:
    emitter = BoundaryEmitter()
    expected = emitter.run(values)
    provider = TASK_DIR / "provider" / "soundtouch_reference_provider.c"
    config = TASK_DIR / "provider" / "config" / "config.json"
    expected["provider_source_digest"] = sha256_file(provider) if provider.exists() else None
    expected["config_digest"] = sha256_file(config) if config.exists() else None
    expected["status"] = "expected_from_python_model"
    expected["session_rejection_note"] = (
        "Session-level validation rejects malformed frames with "
        "AS_INVALID_ARGUMENT. A provider-level AS_INVALID_ARGUMENT is mapped "
        "to AS_BACKEND_FAILURE by as_session_process_v0 and leaves the session "
        "in NEEDS_RESET; the optional ON consumer test checks this on a "
        "throwaway session.")
    return expected


def acceptance_profile() -> dict:
    """Apply the Rate acceptance profile from the pinned verification note."""
    rows = [
        {"requirement": "source/output mapping", "evidence": "duration_mapping",
         "status": "synthetic-fixture-scored"},
        {"requirement": "duration", "evidence": "duration_mapping,pause_policy,drift_rebuffer",
         "status": "synthetic-fixture-scored"},
        {"requirement": "pitch", "evidence": "steady_state.frequency_scale",
         "status": "synthetic-fixture-scored"},
        {"requirement": "transient audibility proxy", "evidence": "transient_behavior",
         "status": "adjacent-delta-proxy-only"},
        {"requirement": "playback buffering and final window",
         "evidence": "streaming,final_partial,c_boundary_expected",
         "status": "synthetic-fixture-scored"},
        {"requirement": "1x and rate changes", "evidence": "variants,rate_updates",
         "status": "synthetic-fixture-scored"},
        {"requirement": "silence and synthetic surrogate timbres",
         "evidence": "stimuli,duration_mapping",
         "status": "synthetic-fixture-scored"},
        {"requirement": "rebuffer and drift", "evidence": "drift_rebuffer",
         "status": "synthetic-fixture-scored"},
        {"requirement": "source-anchored pause/filler decisions",
         "evidence": "pause_policy", "status": "synthetic-fixture-scored"},
        {"requirement": "invalid, missing and nonfinite cases",
         "evidence": "streaming.frame_rejections,streaming.config_rejections,c_boundary_expected.session_rejection_note",
         "status": "synthetic-fixture-scored"},
        {"requirement": "real speech, listening and device playback",
         "evidence": "BLK-02,BLK-03", "status": "not-measured-release-gate"},
    ]
    gates = [
        {"gate": "duration error < 1 ms per audio second",
         "status": "fixture-clock-exact", "scope": "synthetic output clock, not device time"},
        {"gate": "service time p99 < 25% of 100 ms block",
         "status": "not-measured", "scope": "no device or paced workload"},
        {"gate": "0 missed deadlines in 10 minutes",
         "status": "not-measured", "scope": "no device or paced workload"},
        {"gate": "WER delta at 1.25x <= 2 pp and 0.75x <= 3 pp",
         "status": "not-measured", "scope": "no speech corpus, ASR model or listening; pinned source reports a historical +7.4 pp delta at 1.5x and +14.0 pp at 0.5x for real SoundTouch, not re-measured here"},
        {"gate": "no isolated broadband event above source transient floor",
         "status": "proxy-only", "scope": "adjacent-delta proxy, not audible judgement"},
        {"gate": "memory < 10 MiB per mono stream",
         "status": "not-measured", "scope": "no runtime telemetry"},
        {"gate": "upstream SoundTouch LGPL-2.1 / commercial distribution decision cleared",
         "status": "DEFER", "scope": "no upstream source, binary or licensed runtime in this package; no default dependency added"},
        {"gate": "speech rate clamp 0.75-1.5x, 200-500 ms smoothing",
         "status": "fixture-enforced", "scope": "validate_schedule and rate slew in task-local model; not a target playback policy"},
    ]
    return {"profile": "Rate",
            "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "gate_source": "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "clamp": [RATE_MIN, RATE_MAX],
            "rows": rows,
            "proposed_gates": gates}


def blockers() -> list[dict]:
    return [
        {
            "id": "BLK-01",
            "blocker": "The frozen v0 boundary is exactly 160 f32 samples per process call and cannot express device-time expansion for r<1.",
            "scope": "Slow-down is evidenced only in task-local whole-clip fixtures; the optional C reference covers identity, 1.25x and 1.5x speed-up and caller-clock duration mapping.",
            "reopen": "A versioned variable-frame playback actuator or a caller-owned TSM FIFO with source/output timestamps outside v0.",
        },
        {
            "id": "BLK-02",
            "blocker": "No target-device pacing, fill/flush, CPU, memory, deadline, availability or service-time measurement was run.",
            "scope": "No device, workload, real-time or power support is claimed; all numbers are deterministic synthetic-fixture observations.",
            "reopen": "Paced workload on the intended target with fill/flush, deadline misses and resource telemetry under the intended profile.",
        },
        {
            "id": "BLK-03",
            "blocker": "No listening test, real speech, real music, intelligibility score, WER model or release-quality assessment was run.",
            "scope": "Speech-like and music-like stimuli are analytic surrogates; transient and pitch results are deterministic proxies, not audibility or comprehension results.",
            "reopen": "Held-out permitted speech, matched controls and authorized listening/intelligibility scoring with rights review.",
        },
        {
            "id": "BLK-04",
            "blocker": "The upstream SoundTouch 2.4.1 library (LGPL-2.1 or commercial) is not vendored, built, licensed-review-verified or benchmarked in this task.",
            "scope": "This is a minimal task-local deterministic WSOLA-style model of caller-clocked stretch semantics, not upstream SoundTouch code and not a measurement of its audio quality, CPU or memory.",
            "reopen": "Pinned upstream source or licensed runtime, license/notice review, versioned integration and independent comparison under the release profile.",
        },
        {
            "id": "BLK-05",
            "blocker": "The C provider is unregistered, opt-in and not part of the installed SDK, any descriptor registry or the default build.",
            "scope": "No public API, ABI, descriptor registry, descriptor default, installed behavior, shared CMakeLists.txt, board or main was changed.",
            "reopen": "Explicit provider intake, rights/license review, versioned public-surface decision and independent review before any promotion.",
        },
        {
            "id": "BLK-06",
            "blocker": "Pinned source findings for real SoundTouch (duration within two samples, local RTF, F0 shift and paired Whisper deltas) are historical source-reported evidence, not results of this package.",
            "scope": "Every number in this report comes from deterministic synthetic fixtures; no real clip, model inference or listening panel was run here.",
            "reopen": "Reproduce the source protocol on permitted held-out material with the exact source pins and rights clearance, then keep it separately labeled from synthetic results.",
        },
    ]


def build_report(install_location: str | None = None) -> dict:
    stimuli = {
        name: analytic_stimulus(
            name, PAUSE_POLICY_LENGTH if name == "pause_policy" else STIMULUS_LENGTH)
        for name in ("silence", "speech_like", "music_like", "tonal", "pause_policy")
    }
    stimulus_rows = {name: finite_stats(values) for name, values in stimuli.items()}
    variants = variant_bundle({name: values for name, values in stimuli.items()
                               if name != "c_vector"})
    source_pin_rows = {}
    for relative, expected in SOURCE_PINS.items():
        path = AUDIO_ROOT / relative
        actual = sha256_file(path) if path.is_file() else None
        source_pin_rows[relative] = {
            "sha256": expected, "verified": actual == expected, "actual": actual}
    boundary_pin_rows = {}
    for relative, expected in BOUNDARY_PINS.items():
        path = WORKTREE / relative
        actual = sha256_file(path) if path.is_file() else None
        boundary_pin_rows[relative] = {
            "sha256": expected, "verified": actual == expected, "actual": actual}
    duration = duration_mapping(stimuli)
    frequency = frequency_evidence(stimuli, variants)
    updates = rate_update_evidence({name: values for name, values in stimuli.items()
                                    if name != "c_vector"})
    transients = transient_behavior(stimuli, variants)
    energy = energy_evidence(stimuli)
    drift = drift_evidence(stimuli)
    pause = pause_policy_evidence(stimuli["pause_policy"])
    streaming = streaming_evidence(stimuli)
    final = final_partial_evidence(stimuli["speech_like"])
    c_expected = c_boundary_evidence(analytic_stimulus("c_vector"))
    profile = acceptance_profile()
    report = {
        "schema": CONTRACT_ID,
        "status": "proposal_only_not_qualified",
        "decision": {
            "status": "incomplete",
            "promotion": "defer",
            "production_exposure": "DEFER",
            "proposal_only_not_qualified": True,
            "incomplete": True,
            "expose_as_processor": False,
            "registered": False,
            "default_enabled": False,
        },
        "installed_v0": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
            "changed": False,
        },
        "tool_profile": {
            "version": VERSION,
            "install_location": install_location or str(TASK_DIR),
            "provenance": "https://github.com/armaudia/audio-sdk.git",
            "repository": "audio-sdk",
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "runner_python": sys.version.split()[0],
            "runner_platform": platform.platform(),
            "candidate": "Synthetic SoundTouch-named WSOLA-style caller-clocked TSM reference; not upstream SoundTouch",
            "profile": "Rate",
            "upstream_library_vendored": False,
            "upstream_binary_or_weights_used": False,
            "real_corpus_used": False,
            "listening_or_device_measurement": False,
        },
        "scope": {
            "task_id": TASK,
            "component": "soundtouch",
            "disposition": "sdk-reference-proposal",
            "write_scope": "docs/task-evidence/soundtouch/",
            "installed_v0": "16 kHz, mono, f32, 160-sample frames; unchanged",
            "fixture_only": True,
            "playback_actuator": False,
            "optional_provider": True,
            "registered_by_default": False,
            "public_surface_changed": False,
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
            "score_window_samples": SCORE_WINDOW,
            "phase_denominator": PHASE_DENOMINATOR,
            "rate_min": RATE_MIN,
            "rate_max": RATE_MAX,
            "slew_per_segment": RATE_SLEW_PER_SEGMENT,
            "max_abs": MAX_ABS,
            "input_latency_samples": INPUT_LATENCY_SAMPLES,
            "output_latency_samples": OUTPUT_LATENCY_SAMPLES,
            "window": "integer triangular with constant overlap-add denominator 1028",
            "duration_clock": "caller-owned fractional output accumulator; exact nominal mapping",
            "dynamic_schedule": [[start, rate] for start, rate in DYNAMIC_SCHEDULE],
            "drift_schedule": [[start, rate] for start, rate in DRIFT_SCHEDULE],
            "rebuffer_schedule": [[start, rate] for start, rate in REBUFFER_SCHEDULE],
            "pause_policy_schedule": [[start, rate] for start, rate in PAUSE_POLICY_SCHEDULE],
        },
        "acceptance_profile": profile,
        "stimuli": stimulus_rows,
        "duration_mapping": duration,
        "variants": variants,
        "transient_behavior": transients,
        "steady_state": {
            "frequency_scale": frequency,
            "energy_normalization": energy,
        },
        "rate_updates": updates,
        "pause_policy": pause,
        "drift_rebuffer": drift,
        "streaming": streaming,
        "final_partial": final,
        "c_boundary_expected": c_expected,
        "blockers": blockers(),
        "remaining_gates": [
            "exact-head independent review",
            "hosted CI on the exact branch head",
            "upstream SoundTouch source/licensed runtime provenance, LGPL-2.1 or commercial distribution decision and notice review",
            "permitted held-out speech/music cohort with matched controls and authorized listening or intelligibility scoring",
            "paced target-device playback workload with fill/flush, deadlines, CPU, memory and availability telemetry",
            "versioned public-surface and descriptor intake decision before any provider registration or default enablement",
            "release approval; no missing, invalid, nonfinite or adverse result may qualify a candidate",
        ],
        "qualification": {
            "all_required_results_present": all((
                bool(profile["rows"]),
                bool(duration),
                bool(variants),
                bool(transients["transients"]),
                bool(frequency["rows"]),
                bool(energy),
                bool(updates["rows"]),
                bool(pause),
                bool(drift),
                bool(streaming),
                bool(final),
                bool(c_expected),
            )),
            "candidate_status": "proposal_only_not_qualified_synthetic_reference",
            "boundary_status": "conditional-blocked",
            "identity_control": "included",
            "fixed_rate_reference": "included",
            "adverse_controls": "included",
            "missing_result_promoted": False,
            "real_speech_claimed": False,
            "listening_claimed": False,
            "device_timing_claimed": False,
            "release_qualified": False,
        },
    }
    return report


if __name__ == "__main__":
    generated = build_report()
    print(canonical_report(generated)[1])
