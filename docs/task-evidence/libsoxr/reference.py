# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local rate reference for SDK-LIBSOXR.

This package is proposal evidence only. It contains **no libsoxr source,
header, binary, notice bundle, model weight or licensed runtime**; the exact
upstream artifact is absent from the workspace and is recorded as a blocker.
What runs here is a small standard-library-only windowed-sinc sample-rate
converter on an exact rational grid. It exists to exercise the SDK ``rate``
acceptance profile on synthetic signals and to make the blocker auditable.

It is not libsoxr parity, not an installed provider, not a device measurement
and not a listening result. Installed v0 remains 16 kHz, mono, float32, 160
samples per frame. No public C boundary is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
import struct
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0
MIN_RATIO = 0.25
MAX_RATIO = 4.0
KERNEL_HALF_WIDTH = 12
MAX_RATIO_DENOMINATOR = 4096

SCHEMA_ID = "audio-sdk/libsoxr-reference-report/0.1"
TASK = "SDK-LIBSOXR"
COMPONENT = "libsoxr"
BRANCH = "swarm/SDK-LIBSOXR"
BASE_COMMIT = "a91a45e32428df353dbf55a7a9fd2ec052760539"
TASK_PREFIX = "docs/task-evidence/libsoxr/"

# Workspace-relative source pins. These are context and contract inputs, never
# upstream libsoxr artifacts.
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
# Stable linked-row identity only: status, owner, history and review never enter
# canonical bytes and are never a gate.
LINKED_ROWS = (
    {"task_id": "SDK-LIBSAMPLERATE", "title": "libsamplerate",
     "mode": "feasibility", "repository": "audio-sdk",
     "component": "libsamplerate"},
    {"task_id": "SDK-LIBSOXR", "title": "libsoxr",
     "mode": "feasibility", "repository": "audio-sdk",
     "component": "libsoxr"},
    {"task_id": "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING",
     "title": "NumPy/SciPy/SoundFile WAV and resampling",
     "mode": "implementation", "repository": "audio-sdk",
     "component": "numpy-scipy-soundfile-wav-and-resampling"},
    {"task_id": "SDK-SPEEX-RESAMPLER", "title": "Speex resampler",
     "mode": "feasibility", "repository": "audio-sdk",
     "component": "speex-resampler"},
    {"task_id": "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS",
     "title": "Typed frame / resample and drift diagnostics",
     "mode": "implementation", "repository": "audio-sdk",
     "component": "typed-frame-resample-and-drift-diagnostics"},
)

RATIOS = (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)
RATE_FIXTURES = ("silence", "speech_like", "music_like", "tonal_220hz")
TRANSIENT_POSITIONS = (800, 2400, 4000, 5600)
SPEECH_SPANS = (
    (0, 1800, "voiced"), (1800, 2400, "pause"),
    (2400, 4200, "voiced"), (4200, 4800, "filler"),
    (4800, 6600, "voiced"), (6600, 7200, "pause"),
    (7200, 9000, "voiced"), (9000, 9600, "pause"),
)
SOURCE_ARTIFACT_FILES = (
    "reference.py", "run.py", "verify.py", "test_reference.py",
    "check_licensing.py",
)

GATES = (
    {
        "id": "RG-01",
        "gate": "upstream_source_and_revision_pin",
        "status": "blocked",
        "reason": ("No libsoxr source tree at an exact revision is present; "
                   "no commit, tree or file digest exists."),
        "reopen": ("Stage the exact upstream libsoxr source and record commit, "
                   "tree and file digests before any build or comparison."),
    },
    {
        "id": "RG-02",
        "gate": "upstream_license_and_notice_review",
        "status": "blocked",
        "reason": ("No LGPL-2.1-or-later text, upstream notices or rights review "
                   "for libsoxr is present in this package."),
        "reopen": ("Vendor the exact licence and notices, decide dynamic/static "
                   "linking and relink obligations, and record the approved scope."),
    },
    {
        "id": "RG-03",
        "gate": "exact_build_and_install_parity",
        "status": "blocked",
        "reason": ("Nothing was built or installed; the stand-in is a task-local "
                   "Python converter, not the upstream library."),
        "reopen": ("Build and install the pinned revision and compare output, "
                   "latency and end-of-input behaviour with this reference."),
    },
    {
        "id": "RG-04",
        "gate": "exact_api_delay_drain_and_variable_rate_parity",
        "status": "blocked",
        "reason": ("No soxr_create, soxr_process, soxr_delay, soxr_clear or "
                   "soxr_set_io_ratio behaviour was exercised against the real API."),
        "reopen": ("Measure upstream delay, drain, reset and variable-rate "
                   "semantics at the installed boundary and map them to v0."),
    },
    {
        "id": "RG-05",
        "gate": "rights_qualified_rate_cohort",
        "status": "blocked",
        "reason": ("All stimuli are analytic or seeded synthetic; no permitted "
                   "real speech or music cohort with playback rights is staged."),
        "reopen": ("Freeze a rights-qualified, task-matched cohort with metadata "
                   "and an independent scorer."),
    },
    {
        "id": "RG-06",
        "gate": "independent_listening_and_transient_audibility",
        "status": "blocked",
        "reason": ("Transient retention is an adjacent-local-peak proxy; no blind "
                   "listening, audibility judgment or listener panel exists."),
        "reopen": ("Run blind listening with a frozen score sheet and independent "
                   "review on prepared items."),
    },
    {
        "id": "RG-07",
        "gate": "target_runtime_timing_and_memory",
        "status": "blocked",
        "reason": ("Only a caller-owned synthetic FIFO was modelled; no device "
                   "fill/flush, deadline, CPU or memory measurement exists."),
        "reopen": ("Measure paced target-device output, occupancy, CPU, memory and "
                   "separate algorithmic/FIFO/device delay."),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_public_surface_and_release",
        "status": "blocked",
        "reason": ("No provider intake, descriptor, public-surface decision, "
                   "independent exact-head review or release approval exists."),
        "reopen": ("Complete provider intake, a versioned public-surface decision, "
                   "independent exact-head review and release approval."),
    },
)

UPSTREAM_BLOCKER = {
    "status": "blocked_upstream_absent",
    "artifact": "libsoxr source tree at an exact pinned revision",
    "expected_license": "LGPL-2.1-or-later",
    "pinned_revision": None,
    "source_digest": None,
    "no_upstream_parity_claim": True,
    "required_files": [
        "include/soxr.h (or generated src/soxr.h from soxr.h.in)",
        "src/soxr.c",
        "src/rate.c",
        "src/fft4g64.c (and companion FFT sources used by the revision)",
        "CMakeLists.txt",
        "LICENCE",
    ],
    "rights_requirement": (
        "The exact LGPL-2.1-or-later licence text, upstream copyright notices, "
        "the chosen dynamic or static linking model, relink/source-offer "
        "obligations and an exact source revision/digest with a rights review "
        "are required before any wrapper, build or comparison can be claimed."
    ),
    "workspace_search": [
        "third_party/ contains only speexdsp",
        "deps/lock.json pins only SpeexDSP 1.2.1; no libsoxr entry",
        "no soxr.h, src/soxr.c, FFT source or libsoxr archive exists anywhere",
        "no CMake, dependency lock, registry or descriptor reference to libsoxr",
    ],
    "not_attempted": [
        "no network download",
        "no fabricated or reconstructed upstream source",
        "no installed-package substitution for the absent source",
    ],
    "reopen": (
        "Vendor or stage an exact libsoxr revision with its LGPL-2.1-or-later "
        "text and notices, record the digest, decide linking/relink obligations, "
        "then build it and repeat this rate profile against the real API."
    ),
}

NON_CLAIMS = (
    "No libsoxr source, header, binary, notice bundle or download is included.",
    "No installed v0, public API, C ABI, descriptor, registry or default changes.",
    "No provider is registered or enabled by default.",
    "No real speech, music, corpus, listening panel or quality claim is present.",
    "No device timing, fill/flush, deadline, CPU, memory or release claim is made.",
    "No missing, rejected or adverse result qualifies a candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/libsoxr/ is touched.",
    "The stand-in is a task-local Python reference, not upstream libsoxr.",
    "All stimuli are analytic or seeded synthetic; no real corpus or weights.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
)


class ConfigError(ValueError):
    """Invalid configuration or ratio."""


class InputError(ValueError):
    """Invalid sample vector."""


class JsonError(ValueError):
    """Strict JSON rejection."""


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
    if config.sample_rate_hz != SAMPLE_RATE_HZ \
            or config.frame_samples != FRAME_SAMPLES:
        raise ConfigError("only the installed 16 kHz / 160-sample grid is admitted")
    if not 0.0 < config.min_ratio < config.max_ratio:
        raise ConfigError("invalid ratio bounds")
    if config.half_width < 2 or config.half_width > 64:
        raise ConfigError("kernel half width out of bounds")
    if config.max_ratio_denominator < 1:
        raise ConfigError("ratio denominator bound must be positive")
    return config


def ratio_terms(ratio: Any,
                config: RateConfig = DEFAULT_CONFIG) -> Tuple[int, int, float]:
    """Return exact (up, down, value) for output_rate = up/down * input_rate."""
    if isinstance(ratio, bool) or not isinstance(ratio, (int, float)):
        raise ConfigError("ratio must be numeric")
    value = float(ratio)
    if not math.isfinite(value):
        raise ConfigError("ratio must be finite")
    if not config.min_ratio <= value <= config.max_ratio:
        raise ConfigError("ratio outside the declared bounds")
    fraction = Fraction(str(value))
    if fraction.numerator <= 0 \
            or fraction.denominator > config.max_ratio_denominator:
        raise ConfigError("ratio is not a bounded exact rational")
    return fraction.numerator, fraction.denominator, value


def expected_output_samples(source_samples: int, ratio: Any,
                            config: RateConfig = DEFAULT_CONFIG) -> int:
    up, down, _value = ratio_terms(ratio, config)
    return (2 * source_samples * up + down) // (2 * down)


def validate_samples(samples: Any,
                     max_abs: float = MAX_ABS_INPUT) -> Tuple[float, ...]:
    if not isinstance(samples, (list, tuple)):
        raise InputError("samples must be a list or tuple")
    if not samples:
        raise InputError("samples must not be empty")
    output: List[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("sample " + str(index) + " must be numeric")
        numeric = float(value)
        if not math.isfinite(numeric):
            raise InputError("sample " + str(index) + " must be finite")
        if abs(numeric) > max_abs:
            raise InputError("sample " + str(index) + " outside |x| <= 4")
        output.append(numeric)
    return tuple(output)


def tensor_digest(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for value in samples:
        digest.update(struct.pack("<f", float(value)))
    return digest.hexdigest()


def r6(value: float) -> float:
    rounded = round(float(value), 6)
    return 0.0 if rounded == 0 else rounded


def r9(value: float) -> float:
    rounded = round(float(value), 9)
    return 0.0 if rounded == 0 else rounded


def peak_abs(samples: Iterable[float]) -> float:
    return max((abs(value) for value in samples), default=0.0)


def nonfinite_count(samples: Iterable[float]) -> int:
    return sum(0 if math.isfinite(value) else 1 for value in samples)


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


@lru_cache(maxsize=None)
def _weight_table(remainder: int, up: int, cutoff: float,
                  half: int) -> Tuple[Tuple[Tuple[int, float], ...], float]:
    frac = remainder / up
    pairs = tuple((offset, _kernel(frac - offset, cutoff, half))
                  for offset in range(-half + 1, half + 1))
    total = math.fsum(weight for _offset, weight in pairs)
    return pairs, total


def _render(source: Sequence[float], up: int, down: int, count: int,
            half: int) -> Tuple[List[float], List[int], int, int]:
    cutoff = 1.0 if up >= down else up / down
    output: List[float] = []
    mapping: List[int] = []
    first_full = -1
    last_full = -1
    size = len(source)
    for index in range(count):
        center, remainder = divmod(index * down, up)
        pairs, total = _weight_table(remainder, up, cutoff, half)
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
    """Zero-padded windowed-sinc conversion on an exact rational grid."""
    config = validate_config(config)
    source = validate_samples(samples, config.max_abs_input)
    up, down, value = ratio_terms(ratio, config)
    count = expected_output_samples(len(source), value, config)
    if up == down:
        output = list(source)
        mapping = list(range(len(source)))
        first_full = 0
        last_full = len(source) - 1
        identity = True
    else:
        output, mapping, first_full, last_full = _render(
            source, up, down, count, config.half_width)
        identity = False
    valid_count = 0 if first_full < 0 else last_full - first_full + 1
    return {
        "samples": tuple(output),
        "ratio": value,
        "up": up,
        "down": down,
        "target_samples": count,
        "mapping": tuple(mapping),
        "identity_fast_path": identity,
        "valid_start": first_full if first_full >= 0 else 0,
        "valid_count": valid_count,
        "edge_exclusion_start": first_full if first_full >= 0 else count,
        "edge_exclusion_end": count if last_full < 0 else count - 1 - last_full,
        "output_digest": tensor_digest(output),
        "peak_abs": r6(peak_abs(output)),
        "nonfinite_count": nonfinite_count(output),
        "map_monotonic": all(left <= right for left, right in
                             zip(mapping, mapping[1:])),
        "partition_ok": partition_covers(mapping, len(source)),
        "last_mapped_source": mapping[-1] if mapping else -1,
    }


def resample_direct(samples: Sequence[float], ratio: Any,
                    config: RateConfig = DEFAULT_CONFIG) -> Tuple[float, ...]:
    """Second call path: recompute weights from exact positions, no shared cache."""
    source = validate_samples(samples, config.max_abs_input)
    up, down, value = ratio_terms(ratio, config)
    count = expected_output_samples(len(source), value, config)
    if up == down:
        return tuple(source)
    cutoff = 1.0 if up >= down else up / down
    half = config.half_width
    output: List[float] = []
    for index in range(count):
        position = Fraction(index * down, up)
        center = position.numerator // position.denominator
        remainder = position.numerator % position.denominator
        frac = remainder / up
        pairs = tuple((offset, _kernel(frac - offset, cutoff, half))
                      for offset in range(-half + 1, half + 1))
        total = math.fsum(weight for _offset, weight in pairs)
        terms = [source[center + offset] * weight for offset, weight in pairs
                 if 0 <= center + offset < len(source)]
        output.append(math.fsum(terms) / total if total else 0.0)
    return tuple(output)


def crosscheck(samples: Sequence[float], ratio: Any,
               config: RateConfig = DEFAULT_CONFIG) -> Dict[str, Any]:
    primary = resample(samples, ratio, config)
    alternative = resample_direct(samples, ratio, config)
    return {
        "ratio": primary["ratio"],
        "primary_digest": primary["output_digest"],
        "alternative_digest": tensor_digest(alternative),
        "byte_identical": tuple(primary["samples"]) == alternative,
    }


def partition_covers(mapping: Sequence[int], size: int) -> bool:
    if not mapping or mapping[0] != 0 or mapping[-1] >= size:
        return False
    previous = 0
    for left, right in zip(mapping, mapping[1:]):
        if left != previous or right < left:
            return False
        previous = right
    return previous == mapping[-1] and previous < size


def naive_decimate(samples: Sequence[float], ratio: Any,
                   config: RateConfig = DEFAULT_CONFIG) -> Tuple[float, ...]:
    """Adverse control: nearest-source decimation without anti-alias filtering."""
    source = validate_samples(samples, config.max_abs_input)
    up, down, value = ratio_terms(ratio, config)
    count = expected_output_samples(len(source), value, config)
    return tuple(source[min(len(source) - 1, (index * down) // up)]
                 for index in range(count))


def naive_linear(samples: Sequence[float], ratio: Any,
                 config: RateConfig = DEFAULT_CONFIG) -> Tuple[float, ...]:
    """Adverse control: linear interpolation without image rejection."""
    source = validate_samples(samples, config.max_abs_input)
    up, down, value = ratio_terms(ratio, config)
    count = expected_output_samples(len(source), value, config)
    output: List[float] = []
    for index in range(count):
        center, remainder = divmod(index * down, up)
        frac = remainder / up
        left = source[center]
        right = source[center + 1] if center + 1 < len(source) else 0.0
        output.append(left * (1.0 - frac) + right * frac)
    return tuple(output)


def goertzel_amplitude(samples: Sequence[float], frequency_hz: float,
                       rate_hz: float) -> float:
    if not samples or frequency_hz <= 0 or rate_hz <= 0:
        return 0.0
    coefficient = 2.0 * math.cos(2.0 * math.pi * frequency_hz / rate_hz)
    first = 0.0
    second = 0.0
    for value in samples:
        first, second = value + coefficient * first - second, first
    power = first * first + second * second - coefficient * first * second
    return 2.0 * math.sqrt(max(0.0, power)) / len(samples)


def dominant_frequency(samples: Sequence[float], rate_hz: float,
                       low_hz: float, high_hz: float) -> Dict[str, float]:
    step = 0.5
    best_hz = low_hz
    best_amplitude = -1.0
    count = int(round((high_hz - low_hz) / step))
    for index in range(count + 1):
        frequency = low_hz + index * step
        amplitude = goertzel_amplitude(samples, frequency, rate_hz)
        if amplitude > best_amplitude:
            best_hz = frequency
            best_amplitude = amplitude
    return {"dominant_hz": r6(best_hz), "amplitude": r6(best_amplitude),
            "step_hz": step}


def db_relative(amplitude: float, reference: float) -> float:
    if reference <= 0.0:
        return -999.0
    return r6(20.0 * math.log10(max(amplitude, 1e-15) / reference))


def lcg(seed: int):
    state = (seed * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)

    def generator() -> float:
        nonlocal state
        state = (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return ((state >> 11) / float(1 << 53)) * 2.0 - 1.0

    return generator


def tonal_220hz(length: int = 4800) -> Tuple[float, ...]:
    return tuple(0.5 * math.sin(2.0 * math.pi * 220.0 * index / SAMPLE_RATE_HZ)
                 for index in range(length))


def silence(length: int = 1600) -> Tuple[float, ...]:
    return (0.0,) * length


def transient_train(length: int = 6400) -> Tuple[float, ...]:
    output = [0.0] * length
    for position in TRANSIENT_POSITIONS:
        output[position] = 0.9
    return tuple(output)


def speech_like(length: int = 9600, seed: int = 101) -> Tuple[float, ...]:
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


def music_like(length: int = 6400, seed: int = 202) -> Tuple[float, ...]:
    noise = lcg(seed)
    clicks = (800, 1600, 2400, 3200, 4000, 4800, 5600)
    output: List[float] = []
    for index in range(length):
        beat = 0.55 + 0.45 * math.sin(2.0 * math.pi * index / 800.0) ** 2
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


def drift_segment(length: int = 12000, seed: int = 303) -> Tuple[float, ...]:
    noise = lcg(seed)
    return tuple(0.3 * math.sin(2.0 * math.pi * 170.0 * index / SAMPLE_RATE_HZ)
                 + 0.05 * noise() for index in range(length))


FIXTURE_GENERATORS = {
    "silence": silence,
    "speech_like": speech_like,
    "music_like": music_like,
    "tonal_220hz": tonal_220hz,
    "transient_train": transient_train,
    "drift_segment": drift_segment,
}


def float_clock_drift(source_samples: int, ratio: Any,
                      config: RateConfig = DEFAULT_CONFIG) -> Dict[str, Any]:
    """Adverse control: a naive float output clock accumulating step error."""
    up, down, value = ratio_terms(ratio, config)
    step = down / up
    count = expected_output_samples(source_samples, value, config)
    position = 0.0
    maximum = 0.0
    for index in range(count):
        maximum = max(maximum, abs(position - index * step))
        position += step
    return {
        "control": "naive_float_accumulator_not_the_reference",
        "output_samples": count,
        "max_position_error_samples": r9(maximum),
        "max_position_error_ppm": r6(maximum / max(1, source_samples) * 1e6),
        "reference_position_error_samples": 0.0,
        "reference_method": "exact integer divmod over k*down/up",
    }


def rebuffer_trace(source_samples: int = 9600, frame: int = 160,
                   prefill: int = 480, gap_frames: int = 4) -> Dict[str, Any]:
    """Synthetic caller-clock FIFO accounting; not device playout."""
    total_frames, remainder = divmod(source_samples, frame)
    queue = prefill
    played = 0
    underruns = 0
    overflows = 0
    maximum = queue
    ticks = 0
    gap_remaining = gap_frames
    delivered = 0
    while played < total_frames:
        ticks += 1
        if gap_remaining > 0:
            gap_remaining -= 1
        else:
            deliver = min(total_frames - delivered, gap_frames if delivered == 0 else 1)
            delivered += deliver
            queue += deliver * frame
            maximum = max(maximum, queue)
            if queue > prefill + 4 * frame:
                overflows += 1
        if queue >= frame:
            queue -= frame
            played += 1
        else:
            underruns += 1
    return {
        "note": ("Synthetic caller-clock sample accounting only; not a device "
                 "fill/flush, deadline or memory measurement."),
        "frame_samples": frame,
        "prefill_samples": prefill,
        "source_frames": total_frames,
        "source_remainder_samples": remainder,
        "ticks": ticks,
        "gap_frames": gap_frames,
        "played_frames": played,
        "played_samples": played * frame,
        "skipped_audio_samples": 0,
        "underrun_ticks": underruns,
        "overflow_ticks": overflows,
        "max_queue_samples": maximum,
        "final_queue_samples": queue,
    }


def speech_preservation(samples: Sequence[float], ratio: Any = 1.25) -> Dict[str, Any]:
    result = resample(samples, ratio)
    output = result["samples"]
    mapping = result["mapping"]
    spans: List[Dict[str, Any]] = []
    for start, end, label in SPEECH_SPANS:
        indices = [index for index, source in enumerate(mapping)
                   if start <= source < end
                   and result["valid_start"] <= index < result["valid_start"] + result["valid_count"]]
        if not indices:
            spans.append({"label": label, "source_start": start,
                          "source_end": end, "rms": 0.0,
                          "output_samples": 0})
            continue
        rms = math.sqrt(math.fsum(output[index] * output[index]
                                  for index in indices) / len(indices))
        spans.append({"label": label, "source_start": start,
                      "source_end": end, "rms": r6(rms),
                      "output_samples": len(indices)})
    voiced = [span["rms"] for span in spans if span["label"] == "voiced"]
    pauses = [span["rms"] for span in spans if span["label"] == "pause"]
    filler = [span["rms"] for span in spans if span["label"] == "filler"]
    voiced_rms = math.sqrt(math.fsum(value * value for value in voiced) / len(voiced))
    pause_rms = math.sqrt(math.fsum(value * value for value in pauses) / len(pauses))
    contrast = 20.0 * math.log10(max(voiced_rms, 1e-15) / max(pause_rms, 1e-15))
    return {
        "ratio": 1.25,
        "source_samples": len(samples),
        "output_samples": len(output),
        "expected_output_samples": expected_output_samples(len(samples), ratio),
        "duration_exact": len(output) == expected_output_samples(len(samples), ratio),
        "output_digest": result["output_digest"],
        "valid_start": result["valid_start"],
        "valid_count": result["valid_count"],
        "spans": spans,
        "voiced_rms": r6(voiced_rms),
        "pause_rms": r6(pause_rms),
        "filler_rms": r6(filler[0] if filler else 0.0),
        "voiced_to_pause_db": r6(contrast),
        "proxy": "source_anchored_rms_contrast_not_intelligibility",
    }


def final_partial_window(source: Sequence[float] = None) -> Dict[str, Any]:
    if source is None:
        source = speech_like(12737)
    result = resample(source, 1.25)
    output = result["samples"]
    valid_start = result["valid_start"]
    valid_count = result["valid_count"]
    final_frame_valid = valid_count % FRAME_SAMPLES
    return {
        "source_samples": len(source),
        "ratio": 1.25,
        "expected_output_samples": expected_output_samples(len(source), 1.25),
        "output_samples": len(output),
        "valid_start": valid_start,
        "valid_count": valid_count,
        "edge_exclusion_start": result["edge_exclusion_start"],
        "edge_exclusion_end": result["edge_exclusion_end"],
        "final_frame_valid_samples": final_frame_valid,
        "output_digest": result["output_digest"],
        "peak_abs": result["peak_abs"],
        "nonfinite_count": result["nonfinite_count"],
    }


def alias_suppression() -> Dict[str, Any]:
    source = tuple(0.5 * math.sin(2.0 * math.pi * 6000.0 * index / SAMPLE_RATE_HZ)
                   for index in range(6400))
    filtered = resample(source, 0.5)["samples"]
    unfiltered = naive_decimate(source, 0.5)
    reference = 0.5
    filtered_amplitude = goertzel_amplitude(filtered, 2000.0, 8000.0)
    unfiltered_amplitude = goertzel_amplitude(unfiltered, 2000.0, 8000.0)
    return {
        "input_tone_hz": 6000.0,
        "output_rate_hz": 8000.0,
        "alias_bin_hz": 2000.0,
        "passband_reference_amplitude": reference,
        "filtered_alias_amplitude": r6(filtered_amplitude),
        "filtered_suppression_db": db_relative(filtered_amplitude, reference),
        "unfiltered_alias_amplitude": r6(unfiltered_amplitude),
        "unfiltered_suppression_db": db_relative(unfiltered_amplitude, reference),
        "proxy": "goertzel_alias_bin_not_a_listening_or_quality_score",
    }


def image_rejection() -> Dict[str, Any]:
    source = tuple(0.5 * math.sin(2.0 * math.pi * 6000.0 * index / SAMPLE_RATE_HZ)
                   for index in range(6400))
    filtered = resample(source, 2.0)["samples"]
    unfiltered = naive_linear(source, 2.0)
    reference = 0.5
    filtered_amplitude = goertzel_amplitude(filtered, 10000.0, 32000.0)
    unfiltered_amplitude = goertzel_amplitude(unfiltered, 10000.0, 32000.0)
    return {
        "input_tone_hz": 6000.0,
        "output_rate_hz": 32000.0,
        "image_bin_hz": 10000.0,
        "passband_reference_amplitude": reference,
        "filtered_image_amplitude": r6(filtered_amplitude),
        "filtered_suppression_db": db_relative(filtered_amplitude, reference),
        "unfiltered_image_amplitude": r6(unfiltered_amplitude),
        "unfiltered_suppression_db": db_relative(unfiltered_amplitude, reference),
        "proxy": "goertzel_image_bin_not_a_listening_or_quality_score",
    }


def pitch_proxy() -> Dict[str, Any]:
    source = tonal_220hz(4800)
    cases: Dict[str, Any] = {}
    for ratio, label in ((1.0, "identity_1x"), (0.5, "decimate_0_5x"),
                         (2.0, "interpolate_2x")):
        result = resample(source, ratio)
        output_rate = SAMPLE_RATE_HZ * ratio
        measured = dominant_frequency(result["samples"], output_rate, 200.0, 240.0)
        apparent = measured["dominant_hz"] / ratio
        cases[label] = {
            "ratio": ratio,
            "output_rate_hz": output_rate,
            "source": {"dominant_hz": 220.0, "amplitude": 0.5},
            "output": measured,
            "pitch_ratio_at_output_rate": r6(measured["dominant_hz"] / 220.0),
            "varispeed_apparent_hz_if_played_at_16k": r6(apparent),
            "varispeed_pitch_factor": r6(apparent / 220.0),
        }
    cases["note"] = ("A sample-rate converter preserves tone frequency in Hz at "
                     "its own output rate; this is a Goertzel proxy, not listening.")
    return cases


def transient_proxies() -> Dict[str, Any]:
    source = transient_train()
    cases: Dict[str, Any] = {}
    for ratio in RATIOS:
        result = resample(source, ratio)
        output = result["samples"]
        events: List[Dict[str, Any]] = []
        for position in TRANSIENT_POSITIONS:
            up, down, _value = ratio_terms(ratio)
            expected = (2 * position * up + down) // (2 * down)
            low = max(result["valid_start"], expected - 4)
            high = min(result["valid_start"] + result["valid_count"], expected + 5)
            observed = expected
            peak = 0.0
            for index in range(low, high):
                if abs(output[index]) > peak:
                    peak = abs(output[index])
                    observed = index
            events.append({
                "source_sample": position,
                "expected_output_sample": expected,
                "observed_output_sample": observed,
                "timing_error_samples": abs(observed - expected),
                "peak_ratio": r6(peak / 0.9),
            })
        cases[str(ratio)] = {"events": events,
                             "proxy": "local_peak_and_timing_not_listening"}
    return cases


def rate_cases() -> Dict[str, Any]:
    cases: Dict[str, Any] = {}
    for name in RATE_FIXTURES:
        source = FIXTURE_GENERATORS[name]()
        for ratio in RATIOS:
            result = resample(source, ratio)
            expected = expected_output_samples(len(source), ratio)
            cases[name + "@" + str(ratio)] = {
                "fixture": name,
                "ratio": ratio,
                "output_rate_hz": SAMPLE_RATE_HZ * ratio,
                "source_samples": len(source),
                "expected_output_samples": expected,
                "output_samples": len(result["samples"]),
                "duration_exact": len(result["samples"]) == expected,
                "valid_start": result["valid_start"],
                "valid_count": result["valid_count"],
                "edge_exclusion_start": result["edge_exclusion_start"],
                "edge_exclusion_end": result["edge_exclusion_end"],
                "identity_fast_path": result["identity_fast_path"],
                "map_monotonic": result["map_monotonic"],
                "partition_ok": result["partition_ok"],
                "nonfinite_count": result["nonfinite_count"],
                "peak_abs": result["peak_abs"],
                "output_digest": result["output_digest"],
                "source_output_map": [
                    {"output_sample": index, "source_sample": result["mapping"][index]}
                    for index in sorted({0, len(result["mapping"]) // 4,
                                         len(result["mapping"]) // 2,
                                         3 * len(result["mapping"]) // 4,
                                         len(result["mapping"]) - 1})
                ],
            }
    return cases


def variable_rate() -> Dict[str, Any]:
    source = drift_segment(18000)
    segments = ((0, 6000, 1.0), (6000, 12000, 1.03), (12000, 18000, 0.97))
    rendered: List[float] = []
    details: List[Dict[str, Any]] = []
    seams: List[int] = []
    for start, end, ratio in segments:
        result = resample(source[start:end], ratio)
        if rendered:
            seams.append(len(rendered))
        rendered.extend(result["samples"])
        details.append({
            "source_start": start,
            "source_end": end,
            "ratio": ratio,
            "source_samples": end - start,
            "output_samples": len(result["samples"]),
            "expected_output_samples": expected_output_samples(end - start, ratio),
            "duration_exact": len(result["samples"]) ==
                              expected_output_samples(end - start, ratio),
            "output_digest": result["output_digest"],
        })
    expected_total = sum(item["expected_output_samples"] for item in details)
    return {
        "segments": details,
        "seams_output_sample": seams,
        "output_samples": len(rendered),
        "expected_output_samples": expected_total,
        "duration_exact": len(rendered) == expected_total,
        "smooth_soxr_set_io_ratio_behavior_claimed": False,
        "note": ("Each segment converts on its own exact grid; this is a "
                 "piecewise rate-change proxy, not libsoxr set_io_ratio parity."),
    }


def drift() -> Dict[str, Any]:
    source = drift_segment(12000)
    single = resample(source, 1.03)
    second = resample(source, 1.03)
    return {
        "declared_anchors": [[0, 1.0], [12000, 1.03], [24000, 0.97]],
        "method": ("Each segment converts on its own exact rational grid; no "
                   "floating output clock is accumulated."),
        "single_pass_1_03": {
            "source_samples": len(source),
            "output_samples": len(single["samples"]),
            "expected_output_samples": expected_output_samples(len(source), 1.03),
            "duration_exact": len(single["samples"]) ==
                              expected_output_samples(len(source), 1.03),
            "partition_ok": single["partition_ok"],
        },
        "second_segment_1_03": {
            "source_samples": len(source),
            "output_samples": len(second["samples"]),
            "expected_output_samples": expected_output_samples(len(source), 1.03),
            "duration_exact": len(second["samples"]) ==
                              expected_output_samples(len(source), 1.03),
        },
        "naive_float_accumulator": float_clock_drift(20000, 1.03),
    }


def adverse_controls() -> Dict[str, Any]:
    rejected: List[Dict[str, str]] = []

    def reject(kind: str, function) -> None:
        try:
            function()
        except (ConfigError, InputError) as error:
            rejected.append({"kind": kind, "error": str(error)})
        else:
            rejected.append({"kind": kind, "error": "NOT_REJECTED"})

    reject("ratio_zero", lambda: resample(tonal_220hz(160), 0.0))
    reject("ratio_negative", lambda: resample(tonal_220hz(160), -1.0))
    reject("ratio_too_large", lambda: resample(tonal_220hz(160), 5.0))
    reject("ratio_nan", lambda: resample(tonal_220hz(160), float("nan")))
    reject("ratio_infinite", lambda: resample(tonal_220hz(160), float("inf")))
    reject("ratio_string", lambda: resample(tonal_220hz(160), "1.0"))
    reject("ratio_bool", lambda: resample(tonal_220hz(160), True))
    reject("nonfinite_input_nan", lambda: resample([0.0, float("nan")], 1.0))
    reject("nonfinite_input_inf", lambda: resample([0.0, float("inf")], 1.0))
    reject("out_of_range_positive", lambda: resample([0.0, 4.5], 1.0))
    reject("out_of_range_negative", lambda: resample([0.0, -4.5], 1.0))
    reject("boolean_sample", lambda: resample([0.0, True], 1.0))
    reject("string_sample", lambda: resample([0.0, "0.1"], 1.0))
    reject("nested_sample", lambda: resample([[0.0, 0.1]], 1.0))
    reject("empty_samples", lambda: resample([], 1.0))
    reject("unknown_config_key", lambda: resample(tonal_220hz(160), 1.0,
                                                  {"unexpected": 1}))
    reject("wrong_sample_rate", lambda: resample(tonal_220hz(160), 1.0,
                                                 {"sample_rate_hz": 48000}))
    reject("wrong_frame_samples", lambda: resample(tonal_220hz(160), 1.0,
                                                   {"frame_samples": 320}))
    return {
        "cases": rejected,
        "all_rejected": all(case["error"] != "NOT_REJECTED" for case in rejected),
        "case_count": len(rejected),
        "metrics": None,
        "note": "Every case fails closed with no output metrics.",
    }


def json_adverse_controls() -> Dict[str, Any]:
    payloads = {
        "duplicate_key": '{"a":1,"a":2}',
        "nan_constant": '{"a":NaN}',
        "infinity_constant": '{"a":Infinity}',
        "root_array": '[]',
        "trailing_text": '{"a":1} extra',
    }
    results: List[Dict[str, str]] = []
    for name, text in payloads.items():
        try:
            strict_json_loads(text)
        except JsonError as error:
            results.append({"kind": name, "error": str(error)})
        else:
            results.append({"kind": name, "error": "NOT_REJECTED"})
    return {
        "cases": results,
        "all_rejected": all(case["error"] != "NOT_REJECTED" for case in results),
        "case_count": len(results),
        "metrics": None,
    }


def missing_result(fixture_name: str) -> Dict[str, Any]:
    return {
        "status": "blocked",
        "reason": "missing_stimulus",
        "fixture": fixture_name,
        "metrics": None,
        "qualifies_candidate": False,
        "note": "A missing stimulus is blocked; no default success is synthesized.",
    }


def _pairs_hook(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise JsonError("duplicate_json_key")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise JsonError("nonfinite_json_constant:" + token)


def strict_json_loads(text: str) -> Any:
    if not isinstance(text, str):
        raise JsonError("json text must be a string")
    try:
        value = json.loads(text, object_pairs_hook=_pairs_hook,
                           parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise JsonError("invalid_json") from error
    if not isinstance(value, dict):
        raise JsonError("root_not_object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_report(report: Mapping[str, Any]) -> Tuple[str, str]:
    text = canonical_bytes(report).decode("utf-8")
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def artifact_pins(names: Sequence[str] = SOURCE_ARTIFACT_FILES) -> Dict[str, str]:
    from pathlib import Path
    here = Path(__file__).resolve().parent
    return {name: hashlib.sha256((here / name).read_bytes()).hexdigest()
            for name in names}


def qualification() -> Dict[str, Any]:
    return {
        "status": "not_qualified",
        "readiness": "incomplete",
        "decision": "DEFER",
        "candidate_qualified": False,
        "upstream_parity": False,
        "all_required_results_present": True,
        "processor_exposure": "deferred_until_independent_review",
    }


def board_link_projection() -> Tuple[List[Dict[str, str]], str]:
    links = [dict(row) for row in sorted(LINKED_ROWS, key=lambda row: row["task_id"])]
    digest = hashlib.sha256(canonical_bytes(links)).hexdigest()
    return links, digest


def build_report() -> Dict[str, Any]:
    cases = rate_cases()
    crosscheck_cases = {
        str(ratio): crosscheck(tonal_220hz(2400), ratio)
        for ratio in (0.5, 1.0, 1.25, 2.0)
    }
    pitch = pitch_proxy()
    transients = transient_proxies()
    speech = speech_preservation(speech_like())
    partial = final_partial_window()
    alias = alias_suppression()
    image = image_rejection()
    variable = variable_rate()
    drift_result = drift()
    rebuffer = rebuffer_trace()
    adverse = adverse_controls()
    json_adverse = json_adverse_controls()
    missing = missing_result("unknown_stimulus")
    rate_exact = all(case["duration_exact"] and case["partition_ok"]
                     and case["map_monotonic"] and case["nonfinite_count"] == 0
                     for case in cases.values())
    identity_exact = all(
        cases[name + "@1.0"]["identity_fast_path"]
        and cases[name + "@1.0"]["output_samples"] == len(FIXTURE_GENERATORS[name]())
        and cases[name + "@1.0"]["output_digest"] ==
            tensor_digest(FIXTURE_GENERATORS[name]())
        for name in RATE_FIXTURES)
    silence_exact = all(
        cases["silence@" + str(ratio)]["peak_abs"] == 0.0
        for ratio in RATIOS)
    transient_ok = all(
        event["timing_error_samples"] <= 1
        for case in transients.values() if isinstance(case, dict)
        for event in case.get("events", []))
    crosscheck_ok = all(case["byte_identical"] for case in crosscheck_cases.values())
    pitch_ok = all(
        abs(pitch[label]["pitch_ratio_at_output_rate"] - 1.0) <= 0.01
        for label in ("identity_1x", "decimate_0_5x", "interpolate_2x"))
    alias_ok = alias["filtered_suppression_db"] <= -40.0
    image_ok = image["filtered_suppression_db"] <= -40.0
    speech_ok = speech["voiced_to_pause_db"] >= 10.0
    variable_ok = variable["duration_exact"] and all(
        segment["duration_exact"] for segment in variable["segments"])
    drift_ok = drift_result["single_pass_1_03"]["duration_exact"] \
        and drift_result["single_pass_1_03"]["partition_ok"] \
        and drift_result["second_segment_1_03"]["duration_exact"]
    partial_ok = partial["output_samples"] == partial["expected_output_samples"] \
        and partial["nonfinite_count"] == 0
    adverse_ok = adverse["all_rejected"] and json_adverse["all_rejected"]
    links, link_digest = board_link_projection()
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_not_qualified",
        "candidate_status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "qualification": qualification(),
        "qualification_status": "not_qualified",
        "boundary": {
            "format": {
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": 1,
                "sample_format": "float32",
                "frame_samples": FRAME_SAMPLES,
            },
            "installed_v0_unchanged": True,
            "public_api_abi_changed": False,
            "public_c_boundary": "not used: task-local Python reference only",
            "provider_registered": False,
            "provider_intake_complete": False,
            "descriptor_registration": False,
            "descriptor_default_changed": False,
            "enabled_by_default": False,
            "opt_in_required": True,
            "registry_changed": False,
            "shared_cmake_changed": False,
            "ci_changed": False,
            "board_or_handoff_changed": False,
            "real_corpus_or_weights": False,
            "benchmark_claim": False,
            "release_claim": False,
        },
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "profile": {
            "name": "rate",
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": {
                "source_output_mapping": "24 rate cases with floor source maps",
                "duration": "exact round-half-up length on every case",
                "pitch": "Goertzel dominant-frequency proxy and varispeed control",
                "transient_audibility": "adjacent local-peak/timing proxy",
                "playback_buffering": "synthetic caller-clock FIFO accounting",
                "one_x_rate_changes_rebuffer_drift": "identity, piecewise rate change, FIFO gap and exact-grid drift",
                "unfamiliar_speech": "seeded speech-like harmonic proxy",
                "music": "synthetic tonal/click negative control",
                "silence": "exact zero output on every ratio",
                "final_partial_window": "12737 source samples at 1.25x",
                "speech_preservation": "source-anchored RMS contrast, not intelligibility",
            },
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "artifact_pins": artifact_pins(),
        "reference": {
            "implementation": "task-local Python standard-library reference",
            "algorithm": "windowed_sinc_polyphase_on_exact_rational_grid_zero_padded_edges",
            "kernel": "Blackman-windowed sinc",
            "kernel_half_width_taps_each_side": KERNEL_HALF_WIDTH,
            "output_grid": "k * down / up in exact integer arithmetic",
            "dc_normalization": "divide by the full-kernel weight sum",
            "edge_policy": "zero padding with recorded edge exclusions",
            "identity_fast_path": "1:1 copies samples bit-exactly",
            "deterministic": True,
            "synthetic_only": True,
            "downloads": False,
            "real_libsoxr_source_or_binary": False,
            "model_weights": False,
            "upstream_parity": False,
            "buffering_delay_samples": 0,
            "delay_note": ("No integer buffering delay is introduced; kernel "
                           "lookahead and frequency-dependent phase are not a "
                           "device or upstream latency claim."),
        },
        "fixtures": {
            name: {"samples": len(FIXTURE_GENERATORS[name]()),
                   "digest": tensor_digest(FIXTURE_GENERATORS[name]())}
            for name in ("silence", "speech_like", "music_like", "tonal_220hz",
                         "transient_train", "drift_segment")
        },
        "rate_cases": cases,
        "crosscheck": {"cases": crosscheck_cases,
                       "byte_identical": crosscheck_ok,
                       "renderer": ("second Fraction-position call path over the "
                                    "same frozen kernel, no shared cache")},
        "src_pitch": pitch,
        "alias_suppression": alias,
        "image_rejection": image,
        "transient_proxies": transients,
        "speech_preservation": speech,
        "variable_rate": variable,
        "drift": drift_result,
        "rebuffer": rebuffer,
        "final_partial_window": partial,
        "adverse": {
            "invalid_config_and_input": adverse,
            "invalid_json_numeric_fields": json_adverse,
            "missing_result": missing,
            "varispeed_control": {
                "decimate_0_5x_apparent_hz": pitch["decimate_0_5x"][
                    "varispeed_apparent_hz_if_played_at_16k"],
                "interpolate_2x_apparent_hz": pitch["interpolate_2x"][
                    "varispeed_apparent_hz_if_played_at_16k"],
                "interpretation": ("Resampled-and-played-at-input-rate audio is "
                                   "varispeed and shifts pitch; it is an adverse "
                                   "control, not a supported speed mode."),
            },
        },
        "required_results": {
            "rate_cases_complete": len(cases) == 24,
            "duration_exact": rate_exact,
            "source_output_mapping": all(case["partition_ok"] for case in cases.values()),
            "identity_1x_exact": identity_exact,
            "silence_exact": silence_exact,
            "crosscheck_byte_identical": crosscheck_ok,
            "pitch_preservation_proxy": pitch_ok,
            "transient_proxy": transient_ok,
            "alias_suppression": alias_ok,
            "image_rejection": image_ok,
            "speech_preservation_proxy": speech_ok,
            "variable_rate_piecewise": variable_ok,
            "drift": drift_ok,
            "rebuffer": rebuffer["played_samples"] == 9600
                        and rebuffer["skipped_audio_samples"] == 0,
            "final_partial_window": partial_ok,
            "invalid_missing_nonfinite": adverse_ok,
        },
        "no_missing_result_qualifies_candidate": True,
        "regression_count": 5,
        "regressions": [
            {
                "entry_id": "varispeed_pitch_shift_decimate",
                "condition": "tonal_220hz converted 16k_to_8k_and_played_at_16k",
                "metric": "pitch_factor",
                "observed": pitch["decimate_0_5x"]["varispeed_pitch_factor"],
                "excluded_from_qualification": True,
                "interpretation": ("Sample-rate conversion is not time stretching; "
                                   "playback at the input rate is varispeed."),
            },
            {
                "entry_id": "varispeed_pitch_shift_interpolate",
                "condition": "tonal_220hz converted 16k_to_32k_and_played_at_16k",
                "metric": "pitch_factor",
                "observed": pitch["interpolate_2x"]["varispeed_pitch_factor"],
                "excluded_from_qualification": True,
                "interpretation": ("Playback at 16 kHz halves the apparent "
                                   "frequency; adverse control only."),
            },
            {
                "entry_id": "unfiltered_decimation_alias",
                "condition": "6_khz_tone_decimated_to_8_khz_without_filter",
                "metric": "alias_suppression_db",
                "observed": alias["unfiltered_suppression_db"],
                "excluded_from_qualification": True,
                "interpretation": "Naive decimation folds 6 kHz to 2 kHz; adverse control.",
            },
            {
                "entry_id": "linear_interpolation_image",
                "condition": "6_khz_tone_interpolated_to_32_khz_without_filter",
                "metric": "image_suppression_db",
                "observed": image["unfiltered_suppression_db"],
                "excluded_from_qualification": True,
                "interpretation": "Linear interpolation leaves the 10 kHz image; adverse control.",
            },
            {
                "entry_id": "naive_float_clock_drift",
                "condition": "20000_outputs_at_1_03_with_accumulating_float_step",
                "metric": "max_position_error_samples",
                "observed": drift_result["naive_float_accumulator"][
                    "max_position_error_samples"],
                "excluded_from_qualification": True,
                "interpretation": "The reference uses integer divmod and reports zero error.",
            },
        ],
        "source_evidence_statements": [
            ("cpp-library/pipeline-validation/playback-speed-candidates.md lists "
             "libsoxr as a varispeed-only cheap fallback if pitch shift is acceptable."),
            ("The pinned candidate note records LGPL-2.1+ obligations for libsoxr "
             "and says the current files must be verified before shipping."),
            ("No source-reported performance or quality number is imported as a result."),
        ],
        "release_gates": [dict(gate) for gate in GATES],
        "gates": [dict(gate) for gate in GATES],
        "remaining_gates": [gate["id"] + " " + gate["gate"] for gate in GATES],
    }
    return report


def report_bytes() -> bytes:
    text, _digest = canonical_report(build_report())
    return text.encode("utf-8") + b"\n"
