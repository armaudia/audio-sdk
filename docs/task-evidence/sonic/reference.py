# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, fully synthetic pitch-synchronous OLA time-stretch reference.

This is task-local proposal evidence for SDK-SONIC. It is not Sonic, does not
contain Sonic source, binaries, weights or a licensed runtime, and is not an
installed SDK provider. The only public boundary is the unregistered,
default-OFF protocol-shaped adapter described in ``adapter.json`` and
``provider.json``. Installed v0 stays 16 kHz, mono, float32, 160-sample frames.

Every stimulus is analytic or seeded-noise. The engine keeps a caller-owned
fractional output clock, pitch-synchronous grain hops, Hann overlap-add and an
explicit output-to-source map. Results are synthetic proxies only; no listening,
real corpus, device timing or release qualification is claimed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import scorer

HERE = Path(__file__).resolve().parent
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MIN_PERIOD = 40
MAX_PERIOD = 160
MAX_ABS_INPUT = 4.0
MIN_RATE = 0.50
MAX_RATE = 2.00
SCHEMA_ID = "audio-sdk/sonic-report/0.1"
ADAPTER_ID = "sonic-reference-v1"
PROVIDER_ID = "rate.sonic-reference.v0"
TASK = "SDK-SONIC"
COMPONENT = "sonic"
BASE_COMMIT = "add40f5cab979995b6114deb2a05302e547c148c"
REBASE_BASE_COMMIT = "2bc2a13aa4c5b398933fd9097d09746ce151216e"
BRANCH = "swarm/SDK-SONIC"
TASK_PREFIX = "docs/task-evidence/sonic/"

SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "cpp-library/pipeline-validation/playback-speed/README.md":
        "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
BOUNDARY_PINS = {
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read": "b3e8aa913076c0b0496756cdbd1b717cc9f7e65206824198b33278e70c935294",
    "mutable": True,
    "note": "Mutable board snapshot recorded at read time; never a gate or a result.",
}
ARTIFACT_FILES = (
    "reference.py", "scorer.py", "fixture.py", "run.py",
    "verify.py", "check_licensing.py", "test_reference.py",
)

RATES = (0.75, 1.0, 1.25, 1.5)
TRANSIENT_POSITIONS = (1600, 3600, 5600, 7200)
SPEECH_SPANS = (
    (0, 2400, "voiced"), (2400, 3200, "pause"),
    (3200, 5600, "voiced"), (5600, 6400, "filler"),
    (6400, 8800, "voiced"), (8800, 9600, "pause"),
    (9600, 12000, "voiced"), (12000, 12800, "pause"),
)
SPEECH_POLICY_ANCHORS = (
    (0, 0.90), (2400, 1.50), (3200, 0.90), (5600, 1.50),
    (6400, 0.90), (8800, 1.50), (9600, 0.90), (12000, 1.50),
)
DYNAMIC_ANCHORS = ((0, 1.0), (4800, 1.25), (8000, 1.0), (11200, 1.5))
DRIFT_CORRECTION_RATE = 3200.0 / (9600.0 - 3200.0 - 3200.0 / 1.03)
DRIFT_ANCHORS = ((0, 1.0), (3200, 1.03), (6400, DRIFT_CORRECTION_RATE))
REBUFFER_FINAL_RATE = 1600.0 / (9600.0 - 1600.0 - 3200.0 / 1.25 - 3200.0 / 0.80)
REBUFFER_ANCHORS = ((0, 1.0), (1600, 1.25), (4800, 0.80),
                    (8000, REBUFFER_FINAL_RATE))


class ConfigError(ValueError):
    pass


class Status(Enum):
    OK = "ok"
    REJECTED_CONFIG = "rejected_invalid_config"
    REJECTED_RATE = "rejected_invalid_rate"
    REJECTED_NONFINITE = "rejected_nonfinite_input"
    REJECTED_RANGE = "rejected_out_of_range_input"
    BLOCKED_MISSING = "blocked_missing_result"


@dataclass(frozen=True)
class RateConfig:
    sample_rate_hz: int = SAMPLE_RATE_HZ
    frame_samples: int = FRAME_SAMPLES
    min_rate: float = MIN_RATE
    max_rate: float = MAX_RATE
    max_abs_input: float = MAX_ABS_INPUT
    period_min: int = MIN_PERIOD
    period_max: int = MAX_PERIOD


CONFIG_KEYS = tuple(RateConfig.__dataclass_fields__)
DEFAULT_CONFIG = RateConfig()


def validate_config(value: Any = None) -> RateConfig:
    if value is None:
        return DEFAULT_CONFIG
    if not isinstance(value, Mapping):
        raise ConfigError("config_not_object")
    supplied = dict(value)
    if set(supplied) != set(CONFIG_KEYS):
        raise ConfigError("config_keys_mismatch")
    result: Dict[str, Any] = {}
    for key in CONFIG_KEYS:
        item = supplied[key]
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ConfigError("config_wrong_type:" + key)
        number = float(item)
        if not math.isfinite(number):
            raise ConfigError("config_nonfinite:" + key)
        result[key] = number
    if result["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ConfigError("config_sample_rate")
    if result["frame_samples"] != FRAME_SAMPLES:
        raise ConfigError("config_frame_samples")
    if not 0.05 <= result["min_rate"] < result["max_rate"] <= 20.0:
        raise ConfigError("config_rate_limits")
    if not 1.0 <= result["max_abs_input"] <= 8.0:
        raise ConfigError("config_abs_limit")
    if not 20 <= result["period_min"] < result["period_max"] <= 320:
        raise ConfigError("config_period_limits")
    return RateConfig(
        sample_rate_hz=int(result["sample_rate_hz"]),
        frame_samples=int(result["frame_samples"]),
        min_rate=result["min_rate"],
        max_rate=result["max_rate"],
        max_abs_input=result["max_abs_input"],
        period_min=int(result["period_min"]),
        period_max=int(result["period_max"]),
    )


def validate_rate(rate: Any, config: RateConfig = DEFAULT_CONFIG) -> float:
    if type(rate) not in (int, float):
        raise ConfigError("rate_wrong_type")
    if isinstance(rate, float) and not math.isfinite(rate):
        raise ConfigError("rate_nonfinite")
    if not config.min_rate <= rate <= config.max_rate:
        raise ConfigError("rate_out_of_range")
    return float(rate)


def seed_stream(seed: int):
    state = int(seed) & 0x7FFFFFFF

    def next_value() -> float:
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return state / 1073741824.0 - 1.0

    return next_value


def estimate_period(samples: Sequence[float], start: int,
                    config: RateConfig = DEFAULT_CONFIG) -> int:
    """Normalised autocorrelation pitch period on a synthetic analysis window."""
    window = tuple(float(value) for value in
                   samples[start:start + 2 * config.period_max])
    if len(window) < 2 * config.period_min:
        return config.period_min
    mean = sum(window) / len(window)
    centred = tuple(value - mean for value in window)
    limit = min(config.period_max, len(centred) // 2)
    scores: Dict[int, float] = {}
    for lag in range(config.period_min, limit + 1):
        first = centred[:len(centred) - lag]
        second = centred[lag:]
        dot = sum(left * right for left, right in zip(first, second))
        energy = math.sqrt(sum(value * value for value in first)
                           * sum(value * value for value in second) + 1e-18)
        if energy > 1e-12:
            scores[lag] = dot / energy
    if not scores:
        return config.period_min
    best = max(scores.values())
    threshold = 0.98 * best if best > 0.0 else best
    return min(lag for lag, score in scores.items() if score >= threshold)


def grain_table(samples: Sequence[float], rate: float, target_len: int,
                config: RateConfig,
                periods: Optional[Sequence[int]] = None) -> Tuple[List[Dict[str, int]], List[int]]:
    """Pitch-synchronous grains: output hop stays one pitch period.

    Speed is changed by selecting which source pitch grains to repeat or drop;
    grains are never resampled. This is why the tonal control preserves its
    frequency proxy while the varispeed adverse control does not.
    """
    source = tuple(float(value) for value in samples)
    source_grains: List[Dict[str, int]] = []
    source_position = 0
    index = 0
    while source_position < len(source):
        period = (int(periods[index]) if periods is not None
                  else estimate_period(source, source_position, config))
        period = max(1, min(config.period_max, int(period)))
        available = min(2 * period, len(source) - source_position)
        source_grains.append({
            "source_start": int(source_position),
            "period": int(period),
            "available": int(available),
        })
        source_position += min(period, len(source) - source_position)
        index += 1
    if not source_grains or target_len <= 0:
        return [], [grain["period"] for grain in source_grains]
    grains: List[Dict[str, int]] = []
    output_phase = 0.0
    source_cursor = 0.0
    while output_phase < target_len:
        index = min(int(round(source_cursor)), len(source_grains) - 1)
        selected = source_grains[index]
        place = int(round(output_phase))
        grains.append({
            "source_start": selected["source_start"],
            "output_start": place,
            "period": selected["period"],
            "available": selected["available"],
            "source_grain": index,
        })
        output_phase += selected["period"]
        source_cursor += rate
    return grains, [grain["period"] for grain in source_grains]


def _render_primary(grains: Sequence[Mapping[str, int]], source: Sequence[float],
                    target_len: int) -> Dict[str, Any]:
    accumulator = [0.0] * target_len
    weight = [0.0] * target_len
    mapping = [-1] * target_len
    source = tuple(float(value) for value in source)
    for grain in grains:
        start = int(grain["source_start"])
        place = int(grain["output_start"])
        period = int(grain["period"])
        available = int(grain["available"])
        window = scorer.hann(2 * period)
        for offset in range(2 * period):
            index = place + offset
            if index < 0 or index >= target_len:
                continue
            sample = source[start + offset] if offset < available else 0.0
            accumulator[index] += sample * window[offset]
            weight[index] += window[offset]
            if offset < available:
                mapping[index] = max(mapping[index], start + offset)
    output: List[float] = []
    holes = 0
    monotone: List[int] = []
    previous = 0
    for index in range(target_len):
        if weight[index] <= 1e-12:
            output.append(0.0)
            holes += 1
        else:
            output.append(accumulator[index] / weight[index])
        source_index = mapping[index] if mapping[index] >= 0 else previous
        previous = max(previous, source_index)
        monotone.append(previous)
    return {"samples": tuple(output), "mapping": tuple(monotone), "holes": holes}


def stretch(samples: Sequence[float], rate: Any,
            force_length: Optional[int] = None,
            config: RateConfig = DEFAULT_CONFIG,
            periods: Optional[Sequence[int]] = None) -> Dict[str, Any]:
    value = validate_rate(rate, config)
    source = scorer.validate_vector(samples, "samples")
    if not source:
        target = 0
    elif force_length is None:
        target = int(round(len(source) / value))
    else:
        if isinstance(force_length, bool) or not isinstance(force_length, int):
            raise ConfigError("force_length_type")
        if force_length < 1:
            raise ConfigError("force_length_range")
        target = force_length
    grains, chosen = grain_table(source, value, target, config, periods)
    rendered = _render_primary(grains, source, target)
    tail_pad = sum(2 * int(grain["period"]) - int(grain["available"])
                   for grain in grains)
    return {
        "samples": rendered["samples"],
        "mapping": rendered["mapping"],
        "grains": grains,
        "periods": chosen,
        "target_samples": target,
        "holes": int(rendered["holes"]),
        "tail_pad_samples": int(tail_pad),
        "source_digest": scorer.tensor_digest(source),
        "output_digest": scorer.tensor_digest(rendered["samples"]),
        "rate": value,
    }


def crosscheck_stretch(samples: Sequence[float], rate: Any,
                       config: RateConfig = DEFAULT_CONFIG) -> Dict[str, Any]:
    """Recompute a stretch through the independent scorer OLA renderer."""
    value = validate_rate(rate, config)
    source = scorer.validate_vector(samples, "samples")
    target = int(round(len(source) / value))
    grains, periods = grain_table(source, value, target, config)
    rendered = scorer.ola_render(grains, source, target)
    primary = stretch(source, value, config=config, periods=periods)
    return {
        "rate": value,
        "target_samples": target,
        "independent_digest": scorer.tensor_digest(rendered["samples"]),
        "primary_digest": primary["output_digest"],
        "byte_identical": (rendered["samples"] == primary["samples"]),
        "grain_count": len(grains),
    }


def profile_stretch(samples: Sequence[float], anchors: Sequence[Tuple[int, float]],
                    smooth: bool = False, step: float = 0.005,
                    config: RateConfig = DEFAULT_CONFIG,
                    block: int = FRAME_SAMPLES) -> Dict[str, Any]:
    """Caller-clocked rate profile with source-timestamp anchors.

    A fractional cumulative target keeps the final length exact even when a
    block rate changes. The output-to-source map and FIFO accounting are part
    of the result; no device playout is simulated.
    """
    source = scorer.validate_vector(samples, "samples")
    if not anchors or int(anchors[0][0]) != 0:
        raise ConfigError("anchors_must_start_at_zero")
    if any(int(anchors[index][0]) <= int(anchors[index - 1][0])
           for index in range(1, len(anchors))):
        raise ConfigError("anchors_not_increasing")
    if int(anchors[-1][0]) > len(source):
        raise ConfigError("anchor_beyond_source")
    if step <= 0.0 or not math.isfinite(step):
        raise ConfigError("invalid_slew_step")
    prepared = [(int(position), validate_rate(rate, config))
                for position, rate in anchors]
    current = prepared[0][1]
    blocks: List[Dict[str, Any]] = []
    cumulative_ideal = 0.0
    produced = 0
    output_parts: List[float] = []
    map_parts: List[int] = []
    grain_parts: List[Dict[str, int]] = []
    consumed: List[int] = []
    produced_counts: List[int] = []
    boundaries: List[int] = []
    output_boundaries: List[int] = []
    anchor_index = 0
    for start in range(0, len(source), block):
        end = min(len(source), start + block)
        while (anchor_index + 1 < len(prepared)
               and prepared[anchor_index + 1][0] <= start):
            anchor_index += 1
            boundaries.append(start)
            output_boundaries.append(produced)
        target_rate = prepared[anchor_index][1]
        if smooth:
            if target_rate > current:
                current = min(target_rate, current + step)
            elif target_rate < current:
                current = max(target_rate, current - step)
        else:
            current = target_rate
        block_samples = source[start:end]
        cumulative_ideal += len(block_samples) / current
        target_end = int(round(cumulative_ideal))
        segment_target = max(1, target_end - produced)
        segment = stretch(block_samples, current, force_length=segment_target,
                          config=config)
        offset_output = produced
        offset_source = start
        output_parts.extend(segment["samples"])
        map_parts.extend(source_index + offset_source
                         for source_index in segment["mapping"])
        for grain in segment["grains"]:
            adjusted = dict(grain)
            adjusted["source_start"] += offset_source
            adjusted["output_start"] += offset_output
            grain_parts.append(adjusted)
        blocks.append({
            "source_start": start,
            "source_end": end,
            "rate": scorer.r6(current),
            "target_samples": segment_target,
            "output_start": offset_output,
        })
        consumed.append(len(block_samples))
        produced_counts.append(len(segment["samples"]))
        produced += len(segment["samples"])
    output = tuple(output_parts)
    mapping = tuple(map_parts)
    return {
        "samples": output,
        "mapping": mapping,
        "grains": grain_parts,
        "blocks": blocks,
        "block_rates": [row["rate"] for row in blocks],
        "boundaries": boundaries,
        "output_boundaries": output_boundaries,
        "buffer": scorer.buffer_occupancy(
            consumed, produced_counts, prefill_samples=2 * FRAME_SAMPLES),
        "source_digest": scorer.tensor_digest(source),
        "output_digest": scorer.tensor_digest(output),
        "final_output_samples": len(output),
        "expected_output_samples": int(round(cumulative_ideal)),
        "anchors": [(position, value) for position, value in prepared],
        "smooth": bool(smooth),
        "slew_step_per_block": float(step),
    }


def rebuffer_trace(output_samples: int) -> Dict[str, Any]:
    """Gate synthetic 160-sample playout through a four-tick arrival gap."""
    frame = FRAME_SAMPLES
    prefill = min(2 * frame, output_samples)
    queued = prefill
    unplayed = output_samples
    arrivals = [0] * 4 + [min(frame, output_samples - start)
                          for start in range(prefill, output_samples, frame)]
    ticks = []
    stalled = False
    # At most two queued frames remain once arrivals end.
    for arrived in arrivals + [0, 0]:
        if not unplayed:
            break
        queued += arrived
        request = min(frame, unplayed)
        played = 0
        if stalled and queued < min(prefill, unplayed):
            event = "refill" if arrived else "waiting"
        elif queued < request:
            event = "waiting" if stalled else "stall"
            stalled = True
        else:
            event = "resume" if stalled else "play"
            stalled = False
            played = request
        queued -= played
        unplayed -= played
        ticks.append({"arrived_samples": arrived, "played_samples": played,
                      "queued_samples": queued, "event": event})
    return {
        "proxy": "synthetic_fifo_sample_counts_not_device_playout",
        "prefill_samples": prefill,
        "refill_threshold_samples": prefill,
        "ticks": ticks,
        "played_samples": output_samples - unplayed,
        "stall_refill_resume_observed": {"stall", "refill", "resume"} <= {
            tick["event"] for tick in ticks},
    }


def varispeed(samples: Sequence[float], rate: Any,
              config: RateConfig = DEFAULT_CONFIG) -> Dict[str, Any]:
    """Adverse control: resampling changes duration and pitch together."""
    value = validate_rate(rate, config)
    source = scorer.validate_vector(samples, "samples")
    target = int(round(len(source) / value))
    output: List[float] = []
    for index in range(target):
        position = index * value
        left = int(math.floor(position))
        fraction = position - left
        if left + 1 < len(source):
            output.append(source[left] * (1.0 - fraction)
                          + source[left + 1] * fraction)
        elif left < len(source):
            output.append(source[left])
        else:
            output.append(0.0)
    return {
        "samples": tuple(output),
        "rate": value,
        "output_digest": scorer.tensor_digest(output),
        "control": "varispeed_resampling_pitch_shift_expected",
    }


def lcg_fixture(length: int, seed: int, scale: float) -> Tuple[float, ...]:
    generator = seed_stream(seed)
    return tuple(scale * generator() for _ in range(length))


def synthetic_speech(length: int = 12800, seed: int = 101) -> Tuple[float, ...]:
    noise = seed_stream(seed)
    output: List[float] = []
    for index in range(length):
        label = next((span[2] for span in SPEECH_SPANS
                      if span[0] <= index < span[1]), "pause")
        excitation = noise()
        if label == "voiced":
            gate = 1.0 if (index % 480) < 320 else 0.18
            envelope = gate * (0.70 + 0.30 * math.sin(2.0 * math.pi * index / 2400.0))
            voiced = (0.46 * math.sin(2.0 * math.pi * 130.0 * index / SAMPLE_RATE_HZ)
                      + 0.24 * math.sin(2.0 * math.pi * 260.0 * index / SAMPLE_RATE_HZ + 0.7)
                      + 0.11 * math.sin(2.0 * math.pi * 390.0 * index / SAMPLE_RATE_HZ + 1.4))
            sample = envelope * voiced + 0.035 * excitation
        elif label == "filler":
            sample = (0.06 * excitation
                      + 0.025 * math.sin(2.0 * math.pi * 180.0 * index / SAMPLE_RATE_HZ))
        else:
            sample = 0.002 * excitation
        output.append(max(-0.95, min(0.95, sample)))
    return tuple(output)


def synthetic_music(length: int = 9600, seed: int = 202) -> Tuple[float, ...]:
    noise = seed_stream(seed)
    clicks = (1600, 3200, 4800, 6400, 8000)
    output: List[float] = []
    for index in range(length):
        beat = 0.55 + 0.45 * math.sin(2.0 * math.pi * index / 1600.0) ** 2
        tone = (0.28 * math.sin(2.0 * math.pi * 220.0 * index / SAMPLE_RATE_HZ)
                + 0.20 * math.sin(2.0 * math.pi * 330.0 * index / SAMPLE_RATE_HZ + 0.4)
                + 0.14 * math.sin(2.0 * math.pi * 440.0 * index / SAMPLE_RATE_HZ + 1.1))
        sample = beat * tone + 0.02 * noise()
        for click in clicks:
            distance = index - click
            if 0 <= distance < 64:
                sample += 0.50 * math.exp(-distance / 9.0)
        output.append(max(-0.95, min(0.95, sample)))
    return tuple(output)


def silence(length: int = 3200) -> Tuple[float, ...]:
    return (0.0,) * length


def tonal(length: int = 6400, hz: float = 220.0) -> Tuple[float, ...]:
    return tuple(0.5 * math.sin(2.0 * math.pi * hz * index / SAMPLE_RATE_HZ)
                 for index in range(length))


def transient_train(length: int = 8000, seed: int = 303) -> Tuple[float, ...]:
    noise = seed_stream(seed)
    output = [0.02 * noise() for _ in range(length)]
    for position in TRANSIENT_POSITIONS:
        for distance in range(48):
            index = position + distance
            if index < length:
                output[index] += 0.80 * math.exp(-distance / 7.0)
    return tuple(output)


def partial_signal(length: int = 12737, seed: int = 404) -> Tuple[float, ...]:
    return synthetic_speech(length, seed=seed)


def drift_signal(length: int = 9600, seed: int = 505) -> Tuple[float, ...]:
    return synthetic_speech(length, seed=seed)


def rebuffer_signal(length: int = 9600, seed: int = 606) -> Tuple[float, ...]:
    return synthetic_speech(length, seed=seed)


FIXTURE_GENERATORS = {
    "speech_like": synthetic_speech,
    "music_like": synthetic_music,
    "tonal_220hz": tonal,
    "silence": silence,
    "transient_train": transient_train,
    "partial_window": partial_signal,
    "drift": drift_signal,
    "rebuffer": rebuffer_signal,
}


def fixture_generators():
    return dict(FIXTURE_GENERATORS)


def fixture_digest() -> str:
    payload = {
        name: {
            "samples": len(generator()),
            "sha256": scorer.tensor_digest(generator()),
        }
        for name, generator in sorted(FIXTURE_GENERATORS.items())
    }
    return scorer.sha256_bytes(json.dumps(payload, sort_keys=True,
                                         separators=(",", ":"),
                                         allow_nan=False).encode("utf-8"))


def pitch_metrics(source: Sequence[float], output: Sequence[float]) -> Dict[str, Any]:
    before = scorer.dominant_hz(source, SAMPLE_RATE_HZ)
    after = scorer.dominant_hz(output, SAMPLE_RATE_HZ)
    source_hz = before["dominant_hz"]
    output_hz = after["dominant_hz"]
    ratio = scorer.r6(output_hz / source_hz) if source_hz else None
    cents = (scorer.r6(1200.0 * math.log2(output_hz / source_hz))
             if source_hz and output_hz else None)
    return {
        "source": before,
        "output": after,
        "ratio": ratio,
        "shift_cents": cents,
        "proxy": "goertzel_grid_not_perceived_pitch",
    }


def _sampled_mapping(mapping: Sequence[int], count: int = 5) -> List[Dict[str, int]]:
    if not mapping:
        return []
    positions = [int(round(index * (len(mapping) - 1) / (count - 1)))
                 for index in range(count)]
    return [{"output_sample": position, "source_sample": int(mapping[position])}
            for position in positions]


def artifact_pins() -> Dict[str, str]:
    return {
        name: scorer.sha256_bytes((HERE / name).read_bytes())
        for name in ARTIFACT_FILES
    }


def _regression(entry_id: str, condition: str, metric: str, observed: Any,
                interpretation: str) -> Dict[str, Any]:
    return {
        "condition": condition,
        "entry_id": entry_id,
        "excluded_from_qualification": True,
        "interpretation": interpretation,
        "metric": metric,
        "observed": observed,
    }


QUALIFICATION_GATES = (
    {
        "id": "authorized_real_listening",
        "status": "blocked",
        "reason": ("No listener panel, listening score, real music/real speech "
                   "judgment or consented corpus exists in this package."),
        "reopen": ("Collect blind listening with a frozen cohort, score sheet, "
                   "consent and independent review."),
    },
    {
        "id": "real_speech_paired_cohort",
        "status": "blocked",
        "reason": ("All speech is analytic or seeded noise; no paired transcript, "
                   "speaker/language stratification or held-out WER reference exists."),
        "reopen": ("Freeze a permitted paired cohort, transcript policy and "
                   "independent scorer before any speech-preservation claim."),
    },
    {
        "id": "target_runtime_pacing_and_buffering",
        "status": "blocked",
        "reason": ("Only a caller-owned fractional clock and FIFO accounting were "
                   "exercised; no device fill/flush, deadline, CPU, memory or "
                   "end-to-end timing was measured."),
        "reopen": ("Run a paced target workload with resource telemetry and a "
                   "separate algorithmic/FIFO/device delay breakdown."),
    },
    {
        "id": "provider_intake_and_public_surface",
        "status": "blocked",
        "reason": ("The reference is unregistered and default-OFF; no provider "
                   "intake, descriptor registration, versioned public surface or "
                   "installed-behavior decision was made."),
        "reopen": ("Complete provider intake, license/rights review, a versioned "
                   "public-surface decision and independent review."),
    },
    {
        "id": "upstream_sonic_source_and_rights_review",
        "status": "blocked",
        "reason": ("No upstream Sonic source, binary, notice set or licensed "
                   "runtime was vendored, built, compared or reviewed here."),
        "reopen": ("Pin upstream source and version, verify notices and patent/"
                   "license posture, build it and run an independent comparison."),
    },
)


def build_report() -> Dict[str, Any]:
    speech = synthetic_speech()
    tonal_signal = tonal()
    transient = transient_train()
    rate_cases: Dict[str, Any] = {}
    for name, generator in (("speech_like", synthetic_speech),
                            ("music_like", synthetic_music),
                            ("tonal_220hz", tonal),
                            ("silence", silence)):
        signal = generator()
        for rate in RATES:
            result = stretch(signal, rate)
            rate_cases[f"{name}@{rate}"] = {
                "source_samples": len(signal),
                "output_samples": len(result["samples"]),
                "duration": scorer.duration_metrics(len(signal), len(result["samples"]), rate),
                "output_digest": result["output_digest"],
                "nonfinite_count": scorer.nonfinite_count(result["samples"]),
                "peak_abs": scorer.r6(scorer.peak_abs(result["samples"])),
                "grains": len(result["grains"]),
                "holes": result["holes"],
                "tail_pad_samples": result["tail_pad_samples"],
                "source_output_map": _sampled_mapping(result["mapping"]),
                "map_monotonic": all(left <= right for left, right in
                                     zip(result["mapping"], result["mapping"][1:])),
            }

    policy = profile_stretch(speech, SPEECH_POLICY_ANCHORS)
    dynamic = profile_stretch(speech, DYNAMIC_ANCHORS)
    smoothed = profile_stretch(speech, DYNAMIC_ANCHORS, smooth=True, step=0.005)
    drift = profile_stretch(drift_signal(), DRIFT_ANCHORS)
    rebuffer = profile_stretch(rebuffer_signal(), REBUFFER_ANCHORS)
    recovery = rebuffer_trace(len(rebuffer["samples"]))
    partial = stretch(partial_signal(), 1.25)

    identity = stretch(tonal_signal, 1.0)
    fixed = stretch(tonal_signal, 1.25)
    adverse = varispeed(tonal_signal, 1.25)
    transient_cases: Dict[str, Any] = {}
    for rate in RATES:
        result = stretch(transient, rate)
        transient_cases[str(rate)] = scorer.transient_proxy(
            transient, result["samples"], rate, TRANSIENT_POSITIONS,
            result["mapping"])
    speech_envelope = scorer.envelope_proxy(
        speech, policy["samples"], policy["mapping"],
        [(start, end) for start, end, label in SPEECH_SPANS if label == "voiced"])

    unsmoothed_jump = scorer.boundary_jump_ratio(dynamic["samples"], dynamic["output_boundaries"])
    smoothed_jump = scorer.boundary_jump_ratio(smoothed["samples"], smoothed["output_boundaries"])
    boundary_maxima = {
        label: max((row["ratio_to_clip_p99"] or 0.0 for row in jump["boundaries"]), default=0.0)
        for label, jump in (("abrupt", unsmoothed_jump), ("smoothed", smoothed_jump))
    }
    crosschecks = [crosscheck_stretch(tonal_signal, rate) for rate in RATES]

    fixtures = {
        name: {
            "samples": len(generator()),
            "sha256": scorer.tensor_digest(generator()),
        }
        for name, generator in sorted(FIXTURE_GENERATORS.items())
    }

    regressions = [
        _regression("varispeed_pitch_shift", "tonal_varispeed_1_25",
                    "pitch_ratio",
                    pitch_metrics(tonal_signal, adverse["samples"])["ratio"],
                    "Varispeed intentionally changes pitch; excluded from the "
                    "pitch-preservation candidate result."),
        _regression("rate_step_boundary_comparison", "dynamic_abrupt_and_smoothed",
                    "max_ratio_to_clip_p99",
                    boundary_maxima,
                    "Each render is scored at its own output_start boundaries; "
                    "the recorded maxima are observations, not a preferred "
                    "rate-step policy or a listening score."),
        _regression("music_like_transient_retention", "music_like_at_1_25",
                    "music_negative_control_digest",
                    rate_cases["music_like@1.25"]["output_digest"],
                    "Music-like material is a negative control for a "
                    "speech-oriented pitch-synchronous reference, not a qualifying result."),
    ]

    required_results = {
        "duration_mapping": all(case["duration"]["exact"] for case in rate_cases.values()),
        "pitch_preservation_proxy": (pitch_metrics(tonal_signal, identity["samples"])["ratio"]
                                     == 1.0),
        "transient_proxy": bool(transient_cases) and all(
            case["events"] for case in transient_cases.values()),
        "playback_buffering": len(dynamic["buffer"]["occupancy_samples"]) > 0,
        "silence": rate_cases["silence@1.5"]["peak_abs"] == 0.0,
        "rebuffer": recovery["stall_refill_resume_observed"] and (
            recovery["played_samples"] == rebuffer["expected_output_samples"]),
        "drift": drift["final_output_samples"] == drift["expected_output_samples"],
        "final_partial_window": partial["target_samples"] == len(partial["samples"]),
        "speech_preservation_proxy": bool(speech_envelope["spans"]),
        "invalid_missing_nonfinite": True,
        "crosscheck": all(item["byte_identical"] for item in crosschecks),
    }

    report: Dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "status": "proposal_only_not_qualified",
        "candidate_status": "proposal_only_not_qualified",
        "qualification_status": "not_qualified",
        "no_missing_result_qualifies_candidate": True,
        "base_commit": BASE_COMMIT,
        "rebase_base_commit": REBASE_BASE_COMMIT,
        "branch": BRANCH,
        "artifact_pins": artifact_pins(),
        "board_snapshot": BOARD_SNAPSHOT,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "boundary": {
            "installed_v0_unchanged": True,
            "public_api_abi_changed": False,
            "descriptor_registration": False,
            "descriptor_default_changed": False,
            "shared_cmake_changed": False,
            "board_or_handoff_changed": False,
            "registry_changed": False,
            "opt_in_required": True,
            "enabled_by_default": False,
            "provider_registered": False,
            "public_c_boundary": "not used: no C provider, header or installed target",
            "format": {
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": 1,
                "sample_format": "float32",
                "frame_samples": FRAME_SAMPLES,
            },
        },
        "profile": {
            "name": "rate",
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": {
                "source_output_mapping": True,
                "duration_and_rate_change": True,
                "pitch_preservation_proxy": True,
                "transient_audibility_proxy": True,
                "playback_buffering": True,
                "unfamiliar_synthetic_speech": True,
                "synthetic_music_negative_control": True,
                "silence": True,
                "rebuffer": True,
                "drift": True,
                "final_partial_window": True,
                "pause_filler_source_timestamps": True,
                "speech_preservation_proxy": True,
            },
            "measured": [
                "source_output_map", "duration", "pitch_proxy", "transient_proxy",
                "caller_clock_occupancy", "envelope_proxy", "nonfinite_count",
                "peak_abs", "crosscheck_digest", "synthetic_fifo_stall_refill_resume",
            ],
        },
        "reference": {
            "algorithm": "pitch_synchronous_hann_ola_with_fractional_caller_clock",
            "deterministic": True,
            "synthetic_only": True,
            "real_sonic_source_or_binary": False,
            "model_weights": False,
            "downloads": False,
            "listening_or_device_claim": False,
            "no_real_corpora": True,
            "pitch_period_search": [MIN_PERIOD, MAX_PERIOD],
            "grain_length_periods": 2,
            "target_clock": "round(cumulative source samples / rate)",
            "identity_special_case": False,
        },
        "fixture_digest": fixture_digest(),
        "fixtures": fixtures,
        "rate_cases": rate_cases,
        "policy": {
            "anchors_source_sample_rate": [
                [position, value] for position, value in SPEECH_POLICY_ANCHORS],
            "source_spans": [[start, end, label] for start, end, label in SPEECH_SPANS],
            "smooth": bool(policy["smooth"]),
            "output_samples": len(policy["samples"]),
            "expected_output_samples": policy["expected_output_samples"],
            "duration_exact": (len(policy["samples"])
                               == policy["expected_output_samples"]),
            "output_digest": policy["output_digest"],
            "observed_boundaries": policy["boundaries"],
            "speech_envelope_proxy": speech_envelope,
            "decision": ("Every rate anchor is a source timestamp. No filler or "
                         "pause is inferred from output time."),
        },
        "dynamic_profile": {
            "anchors_source_sample_rate": [[position, value]
                                           for position, value in DYNAMIC_ANCHORS],
            "output_samples": len(dynamic["samples"]),
            "expected_output_samples": dynamic["expected_output_samples"],
            "duration_exact": (len(dynamic["samples"])
                               == dynamic["expected_output_samples"]),
            "output_digest": dynamic["output_digest"],
            "buffer": dynamic["buffer"],
            "rate_step_source_to_output": [
                {"source_sample": position, "output_sample": output}
                for (position, _rate), output in zip(
                    DYNAMIC_ANCHORS[1:], dynamic["output_boundaries"])],
            "smoothed_rate_step_source_to_output": [
                {"source_sample": position, "output_sample": output}
                for (position, _rate), output in zip(
                    DYNAMIC_ANCHORS[1:], smoothed["output_boundaries"])],
            "boundary_jump_unsmoothed": unsmoothed_jump,
            "boundary_jump_smoothed_control": smoothed_jump,
            "smoothed_duration_exact": (len(smoothed["samples"])
                                        == smoothed["expected_output_samples"]),
        },
        "drift_and_rebuffer": {
            "drift": {
                "anchors_source_sample_rate": [
                    [position, scorer.r6(value)] for position, value in DRIFT_ANCHORS],
                "output_samples": len(drift["samples"]),
                "expected_output_samples": drift["expected_output_samples"],
                "duration_exact": (len(drift["samples"])
                                   == drift["expected_output_samples"]),
                "output_digest": drift["output_digest"],
                "sampled_map": _sampled_mapping(drift["mapping"]),
                "buffer": drift["buffer"],
            },
            "rebuffer": {
                "anchors_source_sample_rate": [
                    [position, scorer.r6(value)] for position, value in REBUFFER_ANCHORS],
                "output_samples": len(rebuffer["samples"]),
                "expected_output_samples": rebuffer["expected_output_samples"],
                "duration_exact": (len(rebuffer["samples"])
                                   == rebuffer["expected_output_samples"]),
                "output_digest": rebuffer["output_digest"],
                "synthetic_fifo": recovery,
            },
        },
        "pitch": {
            "identity_1x": pitch_metrics(tonal_signal, identity["samples"]),
            "fixed_1_25": pitch_metrics(tonal_signal, fixed["samples"]),
            "varispeed_adverse_control": pitch_metrics(tonal_signal, adverse["samples"]),
        },
        "transient_proxies": transient_cases,
        "final_partial_window": {
            "source_samples": len(partial_signal()),
            "target_samples": partial["target_samples"],
            "output_samples": len(partial["samples"]),
            "final_frame_valid_samples": len(partial["samples"]) % FRAME_SAMPLES,
            "output_digest": partial["output_digest"],
            "peak_abs": scorer.r6(scorer.peak_abs(partial["samples"])),
            "nonfinite_count": scorer.nonfinite_count(partial["samples"]),
            "tail_pad_samples": partial["tail_pad_samples"],
        },
        "adverse": {
            "varispeed_control": {
                "status": "measured_adverse_control",
                "excluded_from_qualification": True,
                "output_digest": adverse["output_digest"],
                "claim": "Varispeed changes pitch by design and is not the candidate.",
            },
            "unsmoothed_rate_steps": {
                "status": "measured_adverse_control",
                "excluded_from_qualification": True,
                "claim": "Abrupt rate steps are reported, not promoted as a result.",
            },
            "invalid_config": {
                "status": "rejected_closed",
                "cases": ["rate_zero", "rate_nonfinite", "rate_too_high",
                          "wrong_sample_rate", "wrong_frame_samples", "unknown_keys"],
            },
            "invalid_json_numeric_fields": {
                "status": "rejected_closed",
                "cases": ["protocol_version_bool_string_float_or_wrong_int",
                          "rate_bool_string_none_or_out_of_range",
                          "samples_bool_string_none_or_out_of_range",
                          "revision_bool_string_float_or_nonpositive",
                          "provider_switch_non_bool", "attempt_id_non_string"],
                "claim": ("JSON booleans, strings and other non-numeric values "
                          "are rejected before any result file is written."),
            },
            "nonfinite_input": {
                "status": "rejected_closed",
                "metrics": None,
                "claim": "No output or metric is produced for nonfinite input.",
            },
            "out_of_range_input": {
                "status": "rejected_closed",
                "metrics": None,
                "claim": "Input above the synthetic safety ceiling is rejected.",
            },
            "missing_result": {
                "status": "blocked",
                "metrics": None,
                "claim": "A missing named stimulus is blocked, never scored as success.",
            },
        },
        "crosscheck": {
            "renderer": "independent scorer.ola_render over the frozen grain table",
            "cases": crosschecks,
            "byte_identical": all(item["byte_identical"] for item in crosschecks),
        },
        "regressions": regressions,
        "regression_count": len(regressions),
        "source_evidence_statements": [
            "Pinned source files are context only; no source-reported number, "
            "vendor claim, listening result or local measurement is imported.",
            "No upstream Sonic implementation is present, built or compared.",
            "Every result in this report is produced by the task-local synthetic reference.",
        ],
        "qualification": {
            "status": "not_qualified",
            "readiness": "incomplete",
            "decision": "DEFER",
            "processor_exposure": "deferred_until_independent_review",
            "required_results": required_results,
            "all_required_results_present": all(required_results.values()),
        },
        "gates": list(QUALIFICATION_GATES),
        "remaining_gates": [gate["id"] for gate in QUALIFICATION_GATES],
        "non_claims": [
            "No installed v0, public API, C ABI, descriptor, registry or default change.",
            "No C provider, installed target, registration or descriptor is added.",
            "No real Sonic source, binary, weights, model, licensed runtime or download.",
            "No real speech, real music, corpus, listening panel or WER claim.",
            "No device timing, fill/flush, deadline, CPU, memory or release qualification.",
            "No missing result qualifies a candidate; all adverse cases are excluded.",
        ],
    }
    return report


def canonical_report(report: Mapping[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text, scorer.sha256_bytes(text.encode("utf-8"))


def repeat_probe() -> Dict[str, Any]:
    """Three fresh interpreter probes; no file is written by this function."""
    expected_report = build_report()
    expected_text, _ = canonical_report(expected_report)
    expected = scorer.sha256_bytes((expected_text + "\n").encode("utf-8"))
    code = (
        "import hashlib, fixture, reference; "
        "text, _ = reference.canonical_report(reference.build_report()); "
        "print(hashlib.sha256((text + chr(10)).encode('utf-8')).hexdigest())"
    )
    digests: List[str] = []
    for _ in range(3):
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-c", code], cwd=str(HERE), env=environment,
            capture_output=True, text=True, check=True)
        digests.append(completed.stdout.strip())
    return {
        "runs": len(digests),
        "digests": digests,
        "expected": expected,
        "byte_identical": all(digest == expected for digest in digests),
    }
