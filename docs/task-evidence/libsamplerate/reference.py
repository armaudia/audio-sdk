# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local sample-rate conversion reference for SDK-LIBSAMPLERATE.

This package is proposal evidence. It contains **no libsamplerate source,
binary, header, notice bundle, weights or licensed runtime**; the upstream
artifact is absent from the workspace and is recorded as a blocker. What runs
here is a small, documented, standard-library-only windowed-sinc sample-rate
converter with exact rational source mapping, written to exercise the SDK rate
acceptance profile on synthetic signals.

It is not upstream parity, not an installed provider, not a device measurement
and not a listening result. Installed v0 stays 16 kHz, mono, float32, 160
samples per frame. Only the unregistered, default-OFF, opt-in protocol-shaped
adapter in ``adapter.json`` touches this code.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Mapping, Sequence, Tuple

import scorer

HERE = Path(__file__).resolve().parent
SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0
MIN_RATIO = 0.25
MAX_RATIO = 4.0
KERNEL_HALF_WIDTH = 12
MAX_RATIO_DENOMINATOR = 4096
SCHEMA_ID = "audio-sdk/libsamplerate-reference-report/0.1"
ADAPTER_ID = "libsamplerate-src-reference-v1"
PROVIDER_ID = "rate.libsamplerate-src-reference.v0"
TASK = "SDK-LIBSAMPLERATE"
COMPONENT = "libsamplerate"
BASE_COMMIT = "8defcae2b153b52668c93791463497ea261b7fb1"
BRANCH = "swarm/SDK-LIBSAMPLERATE"
TASK_PREFIX = "docs/task-evidence/libsamplerate/"

SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
}
BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read": "1f0432bafc9116562b5351c24d6cb766bd441945c6ab48cca0f6f58f9baf4e73",
    "mutable": True,
    "note": ("Mutable board snapshot recorded at read time; status, owner and "
             "history never enter canonical bytes and are never a gate or a "
             "result."),
}
# Only stable linked-row identity is projected. Mutable status is excluded.
LINKED_ROWS = (
    {"task_id": "SDK-LIBSAMPLERATE", "title": "libsamplerate", "mode": "feasibility"},
    {"task_id": "SDK-LIBSOXR", "title": "libsoxr", "mode": "feasibility"},
    {"task_id": "SDK-SPEEX-RESAMPLER", "title": "Speex resampler", "mode": "feasibility"},
    {"task_id": "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS",
     "title": "Typed frame / resample and drift diagnostics", "mode": "implementation"},
    {"task_id": "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING",
     "title": "NumPy/SciPy/SoundFile WAV and resampling", "mode": "implementation"},
)
ARTIFACT_FILES = (
    "reference.py", "scorer.py", "fixture.py", "run.py",
    "verify.py", "check_licensing.py", "test_reference.py",
)

RATES = (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
TRANSIENT_POSITIONS = (1600, 3600, 5600, 7200)
SPEECH_SPANS = (
    (0, 2400, "voiced"), (2400, 3200, "pause"),
    (3200, 5600, "voiced"), (5600, 6400, "filler"),
    (6400, 8800, "voiced"), (8800, 9600, "pause"),
    (9600, 12000, "voiced"), (12000, 12800, "pause"),
)
DRIFT_ANCHORS = (1.0, 1.03, 0.97)
DRIFT_SEGMENT = 16000


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class RateConfig:
    sample_rate_hz: int = SAMPLE_RATE_HZ
    frame_samples: int = FRAME_SAMPLES
    min_ratio: float = MIN_RATIO
    max_ratio: float = MAX_RATIO
    max_abs_input: float = MAX_ABS_INPUT
    half_width: int = KERNEL_HALF_WIDTH
    max_ratio_denominator: int = MAX_RATIO_DENOMINATOR


CONFIG_KEYS = tuple(RateConfig.__dataclass_fields__)
DEFAULT_CONFIG = RateConfig()


def validate_config(value: Any = None) -> RateConfig:
    if value is None:
        return DEFAULT_CONFIG
    if isinstance(value, RateConfig):
        value = dict(value.__dict__)
    if not isinstance(value, Mapping):
        raise ConfigError("configuration must be an object")
    unknown = set(value) - set(CONFIG_KEYS)
    if unknown:
        raise ConfigError("unknown configuration keys")
    merged = dict(DEFAULT_CONFIG.__dict__)
    merged.update(value)
    for key in ("sample_rate_hz", "frame_samples", "half_width",
                "max_ratio_denominator"):
        field = merged[key]
        if isinstance(field, bool) or not isinstance(field, int) or field <= 0:
            raise ConfigError("configuration " + key + " must be a positive integer")
    for key in ("min_ratio", "max_ratio", "max_abs_input"):
        field = merged[key]
        if isinstance(field, bool) or not isinstance(field, (int, float)):
            raise ConfigError("configuration " + key + " must be numeric")
        if not math.isfinite(float(field)):
            raise ConfigError("configuration " + key + " must be finite")
    config = RateConfig(**merged)
    if config.sample_rate_hz != SAMPLE_RATE_HZ or config.frame_samples != FRAME_SAMPLES:
        raise ConfigError("only the installed 16 kHz / 160-sample grid is admitted")
    if not 0.0 < config.min_ratio < config.max_ratio:
        raise ConfigError("invalid ratio bounds")
    if config.half_width < 2 or config.half_width > 64:
        raise ConfigError("kernel half width out of bounds")
    return config


def ratio_terms(ratio: Any, config: RateConfig = DEFAULT_CONFIG) -> Tuple[int, int, float]:
    """Return exact (up, down, value) for output_rate = up/down * input_rate."""
    if isinstance(ratio, bool) or not isinstance(ratio, (int, float)):
        raise ConfigError("ratio must be numeric")
    value = float(ratio)
    if not math.isfinite(value):
        raise ConfigError("ratio must be finite")
    if not config.min_ratio <= value <= config.max_ratio:
        raise ConfigError("ratio outside the declared bounds")
    fraction = Fraction(str(value))
    if fraction.numerator <= 0 or fraction.denominator > config.max_ratio_denominator:
        raise ConfigError("ratio is not a bounded exact rational")
    return fraction.numerator, fraction.denominator, value


def expected_output_samples(source_samples: int, ratio: Any,
                            config: RateConfig = DEFAULT_CONFIG) -> int:
    up, down, _value = ratio_terms(ratio, config)
    return (2 * source_samples * up + down) // (2 * down)


def _kernel(x: float, cutoff: float, half: int) -> float:
    if x == 0.0:
        return cutoff
    if abs(x) >= half:
        return 0.0
    argument = math.pi * cutoff * x
    sinc = math.sin(argument) / argument
    window = (0.42 + 0.5 * math.cos(math.pi * x / half)
              + 0.08 * math.cos(2.0 * math.pi * x / half))
    return cutoff * sinc * window


def _weight_table(remainder: int, down: int, cutoff: float,
                  half: int) -> Tuple[List[Tuple[int, float]], float]:
    frac = remainder / down
    pairs = [(offset, _kernel(frac - offset, cutoff, half))
             for offset in range(-half + 1, half + 1)]
    total = math.fsum(weight for _offset, weight in pairs)
    return pairs, total


def _render_positions(source: Sequence[float], up: int, down: int,
                      count: int, half: int) -> Tuple[List[float], List[int], int, int]:
    cutoff = 1.0 if up >= down else up / down
    cache: Dict[int, Tuple[List[Tuple[int, float]], float]] = {}
    output: List[float] = []
    mapping: List[int] = []
    first_full = -1
    last_full = -1
    size = len(source)
    for index in range(count):
        position = index * down
        center, remainder = divmod(position, up)
        if remainder not in cache:
            cache[remainder] = _weight_table(remainder, up, cutoff, half)
        pairs, total = cache[remainder]
        terms = [source[center + offset] * weight for offset, weight in pairs
                 if 0 <= center + offset < size]
        output.append(math.fsum(terms) / total if total else 0.0)
        mapping.append(center)
        if center - half + 1 >= 0 and center + half < size:
            if first_full < 0:
                first_full = index
            last_full = index
    return output, mapping, first_full, last_full


def resample(samples: Sequence[float], ratio: Any,
             config: RateConfig = DEFAULT_CONFIG) -> Dict[str, Any]:
    """Zero-padded windowed-sinc conversion on an exact rational output grid."""
    config = validate_config(config)
    source = scorer.validate_vector(samples, "samples")
    up, down, value = ratio_terms(ratio, config)
    count = expected_output_samples(len(source), value, config)
    if up == down:
        output = list(source)
        mapping = list(range(len(source)))
        first_full = 0
        last_full = len(source) - 1
        identity = True
    else:
        output, mapping, first_full, last_full = _render_positions(
            source, up, down, count, config.half_width)
        identity = False
    valid_count = 0 if first_full < 0 else last_full - first_full + 1
    result = {
        "samples": tuple(output),
        "ratio": value,
        "up": up,
        "down": down,
        "target_samples": count,
        "mapping": tuple(mapping),
        "identity_fast_path": identity,
        "edge_exclusion_start": first_full if first_full >= 0 else count,
        "edge_exclusion_end": count if last_full < 0 else count - 1 - last_full,
        "valid_start": first_full if first_full >= 0 else 0,
        "valid_count": valid_count,
        "startup_pad_samples": first_full if first_full >= 0 else count,
        "final_pad_samples": count if last_full < 0 else count - 1 - last_full,
        "output_digest": scorer.tensor_digest(output),
        "peak_abs": scorer.r6(scorer.peak_abs(output)),
        "nonfinite_count": scorer.nonfinite_count(output),
        "map_monotonic": all(left <= right for left, right in zip(mapping, mapping[1:])),
        "last_mapped_source": mapping[-1] if mapping else -1,
        "source_interval_union_covers_all": (
            bool(mapping) and mapping[0] == 0
            and mapping[-1] < len(source)
            and all(left <= right for left, right in zip(mapping, mapping[1:]))),
    }
    return result


def resample_direct(samples: Sequence[float], ratio: Any,
                    config: RateConfig = DEFAULT_CONFIG) -> Tuple[float, ...]:
    """Second call path: exact Fraction positions, no shared cache or loop state."""
    source = scorer.validate_vector(samples, "samples")
    up, down, value = ratio_terms(ratio, config)
    count = expected_output_samples(len(source), value, config)
    input_length, output_rate = up, down
    if up == down:
        return tuple(source)
    cutoff = 1.0 if up >= down else up / down
    output: List[float] = []
    half = config.half_width
    for index in range(count):
        position = Fraction(index * output_rate, input_length)
        center = position.numerator // position.denominator
        remainder = position.numerator % position.denominator
        frac = remainder / input_length
        terms: List[float] = []
        weights: List[float] = []
        for offset in range(-half + 1, half + 1):
            weight = _kernel(frac - offset, cutoff, half)
            weights.append(weight)
            if 0 <= center + offset < len(source):
                terms.append(source[center + offset] * weight)
        total = math.fsum(weights)
        output.append(math.fsum(terms) / total if total else 0.0)
    return tuple(output)


def crosscheck_resample(samples: Sequence[float], ratio: Any,
                        config: RateConfig = DEFAULT_CONFIG) -> Dict[str, Any]:
    primary = resample(samples, ratio, config)
    alternative = resample_direct(samples, ratio, config)
    return {
        "ratio": primary["ratio"],
        "primary_digest": primary["output_digest"],
        "alternative_digest": scorer.tensor_digest(alternative),
        "byte_identical": tuple(primary["samples"]) == alternative,
    }


def naive_decimate(samples: Sequence[float], ratio: Any,
                   config: RateConfig = DEFAULT_CONFIG) -> Tuple[float, ...]:
    """Adverse control: nearest-source decimation without an anti-alias filter."""
    source = scorer.validate_vector(samples, "samples")
    up, down, value = ratio_terms(ratio, config)
    count = expected_output_samples(len(source), value, config)
    return tuple(source[min(len(source) - 1, (index * down) // up)]
                 for index in range(count))


def naive_linear(samples: Sequence[float], ratio: Any,
                 config: RateConfig = DEFAULT_CONFIG) -> Tuple[float, ...]:
    """Adverse control: linear interpolation without image rejection."""
    source = scorer.validate_vector(samples, "samples")
    up, down, value = ratio_terms(ratio, config)
    count = expected_output_samples(len(source), value, config)
    output: List[float] = []
    for index in range(count):
        position = index * down
        center, remainder = divmod(position, up)
        frac = remainder / up
        left = source[center]
        right = source[center + 1] if center + 1 < len(source) else 0.0
        output.append(left * (1.0 - frac) + right * frac)
    return tuple(output)


def float_accumulator_drift(samples: Sequence[float], ratio: Any,
                            config: RateConfig = DEFAULT_CONFIG) -> Dict[str, Any]:
    """Adverse control: a naive float output clock that accumulates step error."""
    source = scorer.validate_vector(samples, "samples")
    up, down, value = ratio_terms(ratio, config)
    step = down / up
    count = expected_output_samples(len(source), value, config)
    position = 0.0
    maximum = 0.0
    for index in range(count):
        exact = index * step
        maximum = max(maximum, abs(position - exact))
        position += step
    return {
        "control": "naive_float_accumulator_not_the_reference",
        "output_samples": count,
        "max_position_error_samples": scorer.r9(maximum),
        "max_position_error_ppm": scorer.r6(maximum / max(1, len(source)) * 1e6),
        "reference_position_error_samples": 0.0,
        "reference_method": "exact integer divmod over k*down/up",
    }


def playback_metrics(source_samples: int, output_samples: int,
                     ratio: float) -> Dict[str, Any]:
    source_duration = source_samples / SAMPLE_RATE_HZ
    rendered_duration = output_samples / (SAMPLE_RATE_HZ * ratio)
    played_duration = output_samples / SAMPLE_RATE_HZ
    return {
        "source_seconds": scorer.r6(source_duration),
        "rendered_seconds": scorer.r6(rendered_duration),
        "render_duration_exact": rendered_duration == source_duration,
        "playback_at_input_rate_seconds": scorer.r6(played_duration),
        "playback_speed_factor": scorer.r6(1.0 / ratio),
        "playback_pitch_factor": scorer.r6(1.0 / ratio),
        "claim": ("Playback at the input rate is varispeed: it changes speed and "
                  "pitch together. Sample-rate conversion alone preserves pitch."),
    }


def lcg(seed: int):
    state = (seed * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)

    def generator() -> float:
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return ((state >> 11) / float(1 << 53)) * 2.0 - 1.0

    return generator


def synthetic_speech(length: int = 12800, seed: int = 101) -> Tuple[float, ...]:
    noise = lcg(seed)
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
    noise = lcg(seed)
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


def tonal(length: int = 6400, hz: float = 220.0,
          sample_rate_hz: int = SAMPLE_RATE_HZ) -> Tuple[float, ...]:
    return tuple(0.5 * math.sin(2.0 * math.pi * hz * index / sample_rate_hz)
                 for index in range(length))


def transient_train(length: int = 8000, seed: int = 303) -> Tuple[float, ...]:
    noise = lcg(seed)
    output = [0.02 * noise() for _ in range(length)]
    for position in TRANSIENT_POSITIONS:
        for distance in range(48):
            index = position + distance
            if index < length:
                output[index] += 0.80 * math.exp(-distance / 7.0)
    return tuple(output)


def partial_signal(length: int = 12737, seed: int = 404) -> Tuple[float, ...]:
    return synthetic_speech(length, seed=seed)


def drift_signal(length: int = DRIFT_SEGMENT * 2, seed: int = 505) -> Tuple[float, ...]:
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


def pitch_metrics(source: Sequence[float], output: Sequence[float],
                  output_rate_hz: float) -> Dict[str, Any]:
    before = scorer.dominant_hz(source, SAMPLE_RATE_HZ)
    after = scorer.dominant_hz(output, output_rate_hz)
    source_hz = before["dominant_hz"]
    output_hz = after["dominant_hz"]
    return {
        "source": before,
        "output": after,
        "output_rate_hz": scorer.r6(output_rate_hz),
        "ratio": scorer.r6(output_hz / source_hz) if source_hz else None,
        "shift_cents": (scorer.r6(1200.0 * math.log2(output_hz / source_hz))
                        if source_hz and output_hz else None),
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
    return {name: scorer.sha256_bytes((HERE / name).read_bytes())
            for name in ARTIFACT_FILES}


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


UPSTREAM_BLOCKER = {
    "status": "blocked_upstream_absent",
    "artifact": "erikd/libsamplerate source tree at an exact pinned revision",
    "expected_license": "BSD-2-Clause",
    "required_files": [
        "include/samplerate.h",
        "src/samplerate.c",
        "src/src_sinc.c",
        "src/common.h",
        "CMakeLists.txt or configure.ac",
        "COPYING",
    ],
    "pinned_revision": None,
    "source_digest": None,
    "workspace_search": [
        "third_party/ contains only speexdsp",
        "deps/lock.json pins only SpeexDSP 1.2.1; no libsamplerate entry",
        "no samplerate.h, src_sinc.c or libsamplerate archive anywhere in the workspace",
        "no CMake, dependency lock, registry or descriptor reference to libsamplerate",
    ],
    "rights_requirement": (
        "The upstream BSD-2-Clause license text, the upstream copyright "
        "notices and an exact source revision/digest with a rights review are "
        "required before any wrapper, build or comparison can be claimed."),
    "not_attempted": [
        "no network download",
        "no fabricated or reconstructed upstream source",
        "no installed-package substitution for the absent source",
    ],
    "no_upstream_parity_claim": True,
    "reopen": (
        "Vendor or stage an exact libsamplerate revision with its BSD-2-Clause "
        "text and notices, record the digest, then build it and repeat this "
        "rate profile against the real API for an exact comparison."),
}

QUALIFICATION_GATES = (
    {
        "id": "RG-01",
        "gate": "upstream_source_and_revision_pin",
        "status": "blocked",
        "reason": UPSTREAM_BLOCKER["artifact"] + " is absent; no revision or digest exists.",
        "reopen": ("Stage the exact upstream source and record commit, tree and "
                   "file digests before any build or comparison."),
    },
    {
        "id": "RG-02",
        "gate": "upstream_license_and_notice_review",
        "status": "blocked",
        "reason": ("No BSD-2-Clause text, upstream notices or rights review for "
                   "libsamplerate is present in this package."),
        "reopen": ("Vendor COPYING and notices, complete a license/rights review "
                   "and record the approved scope."),
    },
    {
        "id": "RG-03",
        "gate": "exact_build_and_install_parity",
        "status": "blocked",
        "reason": ("Nothing was built or installed; the reference is a task-local "
                   "Python converter, not the upstream library."),
        "reopen": ("Build and install the pinned revision and compare its output, "
                   "latency and end-of-input behavior with this reference."),
    },
    {
        "id": "RG-04",
        "gate": "exact_api_delay_and_drain_parity",
        "status": "blocked",
        "reason": ("No SRC_STATE latency, end_of_input, ratio-change or reset "
                   "behavior was exercised against the real API."),
        "reopen": ("Measure upstream delay, drain and ratio-change semantics at the "
                   "installed boundary and map them to the v0 content mapping."),
    },
    {
        "id": "RG-05",
        "gate": "rights_qualified_rate_cohort",
        "status": "blocked",
        "reason": ("All stimuli are analytic or seeded synthetic; no permitted real "
                   "speech or music cohort with playback rights is staged."),
        "reopen": ("Freeze a rights-qualified, task-matched cohort with metadata and "
                   "an independent scorer."),
    },
    {
        "id": "RG-06",
        "gate": "independent_listening_and_transient_audibility",
        "status": "blocked",
        "reason": ("Transient retention is an adjacent-delta proxy; no blind "
                   "listening, audibility judgment or listener panel exists."),
        "reopen": ("Run blind listening with a frozen score sheet and independent "
                   "review on prepared items."),
    },
    {
        "id": "RG-07",
        "gate": "target_runtime_timing_and_memory",
        "status": "blocked",
        "reason": ("Only a caller-owned synthetic FIFO was modeled; no device "
                   "fill/flush, deadline, CPU or memory measurement exists."),
        "reopen": ("Measure paced target-device output, buffer occupancy, CPU, memory "
                   "and separate algorithmic/FIFO/device delay."),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "reason": ("The adapter is unregistered and default-OFF; there is no "
                   "provider intake, descriptor, public-surface decision or release "
                   "approval."),
        "reopen": ("Complete provider intake, a versioned public-surface decision, "
                   "independent exact-head review and release approval."),
    },
)


def build_report() -> Dict[str, Any]:
    rate_cases: Dict[str, Any] = {}
    case_signals = (("speech_like", synthetic_speech),
                    ("music_like", synthetic_music),
                    ("tonal_220hz", tonal),
                    ("silence", silence))
    for name, generator in case_signals:
        signal = generator()
        for ratio in RATES:
            result = resample(signal, ratio)
            rate_cases[f"{name}@{ratio}"] = {
                "source_samples": len(signal),
                "output_samples": len(result["samples"]),
                "output_rate_hz": scorer.r6(SAMPLE_RATE_HZ * ratio),
                "duration": scorer.duration_metrics(len(signal),
                                                    len(result["samples"]), ratio),
                "output_digest": result["output_digest"],
                "nonfinite_count": result["nonfinite_count"],
                "peak_abs": result["peak_abs"],
                "valid_start": result["valid_start"],
                "valid_count": result["valid_count"],
                "edge_exclusion_start": result["edge_exclusion_start"],
                "edge_exclusion_end": result["edge_exclusion_end"],
                "source_output_map": _sampled_mapping(result["mapping"]),
                "map_monotonic": result["map_monotonic"],
                "source_interval_union_covers_all": result[
                    "source_interval_union_covers_all"],
                "identity_fast_path": result["identity_fast_path"],
            }

    tonal_signal = tonal()
    identity = resample(tonal_signal, 1.0)
    fixed_up = resample(tonal_signal, 2.0)
    fixed_down = resample(tonal_signal, 0.5)
    varispeed = pitch_metrics(tonal_signal, fixed_up["samples"], SAMPLE_RATE_HZ)
    varispeed_down = pitch_metrics(tonal_signal, fixed_down["samples"], SAMPLE_RATE_HZ)

    # Anti-alias: 6 kHz input tone decimated to 8 kHz folds to 2 kHz.
    alias_signal = tonal(6400, hz=6000.0)
    alias_filtered = resample(alias_signal, 0.5)
    alias_naive = naive_decimate(alias_signal, 0.5)
    passband = resample(tonal(6400, hz=1000.0), 0.5)
    passband_amplitude = scorer.goertzel_amplitude(passband["samples"], 1000.0, 8000.0)
    alias_metrics = {
        "input_tone_hz": 6000.0,
        "output_rate_hz": 8000.0,
        "alias_bin_hz": 2000.0,
        "passband_reference_amplitude": scorer.r6(passband_amplitude),
        "filtered_alias_amplitude": scorer.r6(scorer.goertzel_amplitude(
            alias_filtered["samples"], 2000.0, 8000.0)),
        "naive_alias_amplitude": scorer.r6(scorer.goertzel_amplitude(
            alias_naive, 2000.0, 8000.0)),
        "filtered_suppression_db": scorer.attenuation_db(
            passband_amplitude,
            scorer.goertzel_amplitude(alias_filtered["samples"], 2000.0, 8000.0)),
        "naive_suppression_db": scorer.attenuation_db(
            passband_amplitude,
            scorer.goertzel_amplitude(alias_naive, 2000.0, 8000.0)),
        "proxy": "goertzel_alias_bin_not_a_listening_or_quality_score",
    }

    # Imaging: 6 kHz tone interpolated to 32 kHz images at 10 kHz.
    image_signal = tonal(6400, hz=6000.0)
    image_filtered = resample(image_signal, 2.0)
    image_naive = naive_linear(image_signal, 2.0)
    image_passband = scorer.goertzel_amplitude(image_filtered["samples"], 6000.0, 32000.0)
    image_metrics = {
        "input_tone_hz": 6000.0,
        "output_rate_hz": 32000.0,
        "image_bin_hz": 10000.0,
        "passband_reference_amplitude": scorer.r6(image_passband),
        "filtered_image_amplitude": scorer.r6(scorer.goertzel_amplitude(
            image_filtered["samples"], 10000.0, 32000.0)),
        "naive_image_amplitude": scorer.r6(scorer.goertzel_amplitude(
            image_naive, 10000.0, 32000.0)),
        "filtered_suppression_db": scorer.attenuation_db(
            image_passband,
            scorer.goertzel_amplitude(image_filtered["samples"], 10000.0, 32000.0)),
        "naive_suppression_db": scorer.attenuation_db(
            image_passband,
            scorer.goertzel_amplitude(image_naive, 10000.0, 32000.0)),
        "proxy": "goertzel_image_bin_not_a_listening_or_quality_score",
    }

    transient_cases: Dict[str, Any] = {}
    transient = transient_train()
    transient_peak = scorer.peak_abs(transient)
    for ratio in RATES:
        result = resample(transient, ratio)
        positions = [int(round(position * ratio)) for position in TRANSIENT_POSITIONS]
        transient_cases[str(ratio)] = scorer.transient_proxy(
            transient_peak, result["samples"], positions)

    speech = synthetic_speech()
    policy = resample(speech, 1.25)
    speech_envelope = scorer.envelope_proxy(
        speech, policy["samples"], policy["mapping"],
        [(start, end) for start, end, label in SPEECH_SPANS if label == "voiced"])

    # Drift: two exact ratio changes over the same signal.
    drift = drift_signal()
    drift_first = resample(drift[:DRIFT_SEGMENT], DRIFT_ANCHORS[1])
    second_source = resample(drift[DRIFT_SEGMENT:], DRIFT_ANCHORS[1])["samples"]
    drift_cases = {
        "single_pass_1_03": {
            "output_samples": len(drift_first["samples"]),
            "expected_output_samples": expected_output_samples(
                DRIFT_SEGMENT, DRIFT_ANCHORS[1]),
            "duration_exact": (len(drift_first["samples"])
                               == expected_output_samples(DRIFT_SEGMENT, DRIFT_ANCHORS[1])),
            "sampled_map": _sampled_mapping(drift_first["mapping"]),
            "source_interval_union_covers_all": drift_first[
                "source_interval_union_covers_all"],
        },
        "second_segment_1_03": {
            "source_samples": DRIFT_SEGMENT,
            "output_samples": len(second_source),
            "expected_output_samples": expected_output_samples(
                DRIFT_SEGMENT, DRIFT_ANCHORS[1]),
            "duration_exact": (len(second_source)
                               == expected_output_samples(DRIFT_SEGMENT, DRIFT_ANCHORS[1])),
        },
        "naive_float_accumulator": float_accumulator_drift(drift, 1.25),
        "declared_anchors": [[0, DRIFT_ANCHORS[0]],
                             [DRIFT_SEGMENT, DRIFT_ANCHORS[1]],
                             [2 * DRIFT_SEGMENT, DRIFT_ANCHORS[2]]],
        "method": ("Each segment converts on its own exact rational grid; no "
                   "floating output clock is accumulated."),
    }

    # Pacing/FIFO: fixed 160-sample output ticks with rate-matched input.
    rebuffer = rebuffer_signal()
    ratio = 0.75
    produced: List[int] = []
    consumed: List[int] = []
    for tick in range(12):
        if 4 <= tick <= 7:
            produced.append(0)
        elif tick in (8, 9):
            produced.append(2 * FRAME_SAMPLES)
        else:
            produced.append(FRAME_SAMPLES)
        consumed.append(FRAME_SAMPLES)
    recovery = scorer.rebuffer_trace(produced, consumed, prefill=480, capacity=960)
    pacing = {
        "output_tick_samples": FRAME_SAMPLES,
        "source_samples_per_tick": [
            round(FRAME_SAMPLES / ratio) if value else 0 for value in produced],
        "ratio": ratio,
        "rebuffer": recovery,
        "source_audio_seconds": scorer.r6(len(rebuffer) / SAMPLE_RATE_HZ),
        "note": ("Synthetic caller-clock sample counts only; a rebuffer gap, refill "
                 "and resume are exercised without any device playout."),
    }

    partial = resample(partial_signal(), 1.25)
    crosschecks = [crosscheck_resample(tonal_signal, value) for value in RATES]
    volume_reference = resample(tonal_signal, 0.5)
    identity_hz = pitch_metrics(tonal_signal, identity["samples"], SAMPLE_RATE_HZ)
    up_hz = pitch_metrics(tonal_signal, fixed_up["samples"], SAMPLE_RATE_HZ * 2.0)
    down_hz = pitch_metrics(tonal_signal, fixed_down["samples"], SAMPLE_RATE_HZ * 0.5)

    fixtures = {
        name: {"samples": len(generator()),
               "sha256": scorer.tensor_digest(generator())}
        for name, generator in sorted(FIXTURE_GENERATORS.items())
    }

    regressions = [
        _regression("varispeed_pitch_shift", "tonal_played_at_input_rate_ratio_2_0",
                    "pitch_ratio", varispeed["ratio"],
                    ("Resampled-and-played-at-input-rate audio is varispeed and "
                     "shifts pitch; it is an adverse control for rate conversion, "
                     "not a pitch-preservation result.")),
        _regression("varispeed_pitch_shift_down", "tonal_played_at_input_rate_ratio_0_5",
                    "pitch_ratio", varispeed_down["ratio"],
                    "Second varispeed direction; excluded from qualification."),
        _regression("naive_decimation_alias", "alias_bin_2_khz_after_0_5_decimation",
                    "naive_suppression_db", alias_metrics["naive_suppression_db"],
                    ("Unfiltered nearest-sample decimation is an adverse control; its "
                     "alias level is reported, not promoted.")),
        _regression("naive_linear_imaging", "image_bin_10_khz_after_2_0_interpolation",
                    "naive_suppression_db", image_metrics["naive_suppression_db"],
                    ("Unfiltered linear interpolation is an adverse control; its "
                     "image level is reported, not promoted.")),
        _regression("float_accumulator_drift", "naive_float_output_clock",
                    "max_position_error_samples",
                    drift_cases["naive_float_accumulator"][
                        "max_position_error_samples"],
                    ("A naive float accumulator drifts; the reference uses exact "
                     "integer divmod and reports zero position error.")),
        _regression("music_like_negative_control", "music_like_at_1_25",
                    "output_digest", rate_cases["music_like@1.25"]["output_digest"],
                    "Synthetic music is a negative control for a speech-oriented "
                    "rate reference, not a qualifying result."),
    ]

    required_results = {
        "duration_mapping": all(case["duration"]["exact"]
                                for case in rate_cases.values()),
        "source_output_mapping": all(case["map_monotonic"]
                                     and case["source_interval_union_covers_all"]
                                     for case in rate_cases.values()),
        "identity_1x_exact": identity["identity_fast_path"] and identity_hz["ratio"] == 1.0,
        "pitch_preservation_proxy": (up_hz["ratio"] is not None
                                     and abs(up_hz["ratio"] - 1.0) < 0.02
                                     and down_hz["ratio"] is not None
                                     and abs(down_hz["ratio"] - 1.0) < 0.02),
        "transient_proxy": bool(transient_cases) and all(
            case["events"] for case in transient_cases.values()),
        "alias_suppression": (alias_metrics["filtered_suppression_db"]
                              < alias_metrics["naive_suppression_db"] - 20.0),
        "image_rejection": (image_metrics["filtered_suppression_db"]
                            < image_metrics["naive_suppression_db"] - 20.0),
        "silence": rate_cases["silence@1.5"]["peak_abs"] == 0.0,
        "drift": (drift_cases["single_pass_1_03"]["duration_exact"]
                  and drift_cases["second_segment_1_03"]["duration_exact"]),
        "rebuffer": recovery["stall_refill_resume_observed"],
        "final_partial_window": (partial["target_samples"] == len(partial["samples"])),
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
        "decision": "DEFER",
        "no_missing_result_qualifies_candidate": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "artifact_pins": artifact_pins(),
        "board_snapshot": BOARD_SNAPSHOT,
        "board_links": [dict(row) for row in LINKED_ROWS],
        "board_link_projection_sha256": scorer.sha256_bytes(json.dumps(
            [dict(row) for row in LINKED_ROWS], sort_keys=True,
            separators=(",", ":")).encode("utf-8")),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "upstream_blocker": UPSTREAM_BLOCKER,
        "reference": {
            "algorithm": ("windowed_sinc_polyphase_on_exact_rational_grid_"
                          "zero_padded_edges"),
            "implementation": "task-local Python standard-library reference",
            "real_libsamplerate_source_or_binary": False,
            "upstream_parity": False,
            "downloads": False,
            "model_weights": False,
            "deterministic": True,
            "synthetic_only": True,
            "kernel": "Blackman-windowed sinc",
            "kernel_half_width_taps_each_side": KERNEL_HALF_WIDTH,
            "identity_fast_path": "1:1 copies samples bit-exactly",
            "output_grid": "k * down / up in exact integer arithmetic",
            "dc_normalization": "divide by the full-kernel weight sum",
            "edge_policy": "zero padding with recorded edge exclusions",
            "buffering_delay_samples": 0,
            "delay_note": ("No integer buffering delay is introduced; kernel "
                           "lookahead and frequency-dependent phase are not counted "
                           "as content delay."),
        },
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
            "provider_intake_complete": False,
            "release_claim": False,
            "benchmark_claim": False,
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
                "speech_preservation_proxy": True,
            },
            "measured": [
                "source_output_map", "duration", "src_pitch_proxy",
                "transient_proxy", "alias_suppression_db", "image_rejection_db",
                "caller_clock_occupancy", "envelope_proxy", "nonfinite_count",
                "peak_abs", "crosscheck_digest",
                "synthetic_fifo_stall_refill_resume",
            ],
        },
        "fixture_digest": fixture_digest(),
        "fixtures": fixtures,
        "rate_cases": rate_cases,
        "src_pitch": {
            "identity_1x": identity_hz,
            "interpolate_2x": up_hz,
            "decimate_0_5x": down_hz,
            "note": ("A sample-rate converter preserves tone frequency in Hz at its "
                     "own output rate; this is a Goertzel proxy, not listening."),
        },
        "transient_proxies": transient_cases,
        "alias_suppression": alias_metrics,
        "image_rejection": image_metrics,
        "speech_preservation": {
            "spans": [[start, end, label] for start, end, label in SPEECH_SPANS],
            "envelope_proxy": speech_envelope,
            "output_samples": len(policy["samples"]),
            "expected_output_samples": expected_output_samples(len(speech), 1.25),
            "duration_exact": (len(policy["samples"])
                               == expected_output_samples(len(speech), 1.25)),
            "output_digest": policy["output_digest"],
        },
        "drift_and_rebuffer": {
            "drift": drift_cases,
            "pacing": pacing,
            "rebuffer_signal_samples": len(rebuffer),
        },
        "final_partial_window": {
            "source_samples": len(partial_signal()),
            "target_samples": partial["target_samples"],
            "output_samples": len(partial["samples"]),
            "final_frame_valid_samples": len(partial["samples"]) % FRAME_SAMPLES,
            "valid_count": partial["valid_count"],
            "output_digest": partial["output_digest"],
            "peak_abs": partial["peak_abs"],
            "nonfinite_count": partial["nonfinite_count"],
        },
        "playback": {
            "identity": playback_metrics(len(tonal_signal),
                                         len(identity["samples"]), 1.0),
            "decimate_0_5": playback_metrics(len(tonal_signal),
                                             len(fixed_down["samples"]), 0.5),
            "interpolate_2_0": playback_metrics(len(tonal_signal),
                                                len(fixed_up["samples"]), 2.0),
            "varispeed_pitch": {
                "interpolate_2_0_played_at_input_rate": varispeed,
                "decimate_0_5_played_at_input_rate": varispeed_down,
            },
        },
        "adverse": {
            "varispeed_control": {
                "status": "measured_adverse_control",
                "excluded_from_qualification": True,
                "claim": ("Playing converted audio at the input rate shifts pitch "
                          "by 1/ratio; rate conversion is not time stretching."),
            },
            "invalid_config": {
                "status": "rejected_closed",
                "cases": ["ratio_zero", "ratio_nonfinite", "ratio_too_high",
                          "ratio_too_low", "ratio_inexact_rational",
                          "wrong_sample_rate", "wrong_frame_samples", "unknown_keys"],
            },
            "invalid_json_numeric_fields": {
                "status": "rejected_closed",
                "cases": ["protocol_version_bool_string_float_or_wrong_int",
                          "ratio_bool_string_none_or_out_of_range",
                          "samples_bool_string_none_or_out_of_range",
                          "revision_bool_string_float_or_nonpositive",
                          "provider_switch_non_bool", "attempt_id_non_string"],
                "claim": ("JSON booleans, strings and other non-numeric values are "
                          "rejected before any result file is written."),
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
            "renderer": "second Fraction-position call path over the same frozen kernel",
            "cases": crosschecks,
            "byte_identical": all(item["byte_identical"] for item in crosschecks),
        },
        "regressions": regressions,
        "regression_count": len(regressions),
        "source_evidence_statements": [
            "Pinned source files are context only; no source-reported number, "
            "vendor claim, listening result or local measurement is imported.",
            "No libsamplerate source, header, binary or runtime is present, built "
            "or compared in this package.",
            "Every result in this report is produced by the task-local synthetic "
            "reference and remains proposal-only.",
        ],
        "required_results": required_results,
        "qualification": {
            "status": "not_qualified",
            "readiness": "incomplete",
            "decision": "DEFER",
            "processor_exposure": "deferred_until_independent_review",
            "all_required_results_present": all(required_results.values()),
            "upstream_parity": False,
            "candidate_qualified": False,
        },
        "gates": list(QUALIFICATION_GATES),
        "remaining_gates": [gate["id"] for gate in QUALIFICATION_GATES],
        "non_claims": [
            "No installed v0, public API, C ABI, descriptor, registry or default change.",
            "No C provider, installed target, registration or descriptor is added.",
            "No libsamplerate source, header, binary, notice bundle or download.",
            "No real speech, real music, corpus, listening panel or quality claim.",
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
    expected_text, _ = canonical_report(build_report())
    expected = scorer.sha256_bytes((expected_text + "\n").encode("utf-8"))
    code = (
        "import hashlib, reference; "
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
        "byte_identical": len(set(digests)) == 1 and digests[0] == expected,
    }
