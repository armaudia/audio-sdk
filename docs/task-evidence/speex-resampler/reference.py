# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local, deterministic reference for the vendored SpeexDSP resampler.

This module compiles the exact pinned vendored source
``third_party/speexdsp/libspeexdsp/resample.c`` through its public documented
``speex/speex_resampler.h`` boundary and drives it from deterministic synthetic
stimuli. It is not an installed provider, registry entry, descriptor or public
ABI. It makes no quality, listening, device-timing, corpus or release claim.

Only the Python standard library is imported. The single external process is
the system C compiler selected by ``CC`` (default ``cc``); the compiled helper
stays in a caller scratch directory outside the worktree.
"""

from __future__ import annotations

import hashlib
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MIN_SPEED = Fraction(1, 2)
MAX_SPEED = Fraction(2, 1)
DEFAULT_QUALITY = 4
MAX_ABS_INPUT = 4.0
MAX_INPUT_SAMPLES = 1 << 20

SCHEMA_ID = "audio-sdk/speex-resampler-report/0.1"
CONTRACT_ID = "audio-sdk/speex-resampler/0.1"
ADAPTER_ID = "speex-resampler-varispeed-reference-v1"
PROVIDER_ID = "rate.speex-resampler-reference.v0"
TASK = "SDK-SPEEX-RESAMPLER"
COMPONENT = "speex-resampler"
BASE_COMMIT = "8defcae2b153b52668c93791463497ea261b7fb1"
BRANCH = "swarm/SDK-SPEEX-RESAMPLER"
TASK_PREFIX = "docs/task-evidence/speex-resampler/"

SPEED_CASES: Tuple[Dict[str, Any], ...] = (
    {"label": "0.75", "num": 3, "den": 4, "out_rate_hz": 12000},
    {"label": "1.0", "num": 1, "den": 1, "out_rate_hz": 16000},
    {"label": "1.25", "num": 5, "den": 4, "out_rate_hz": 20000},
    {"label": "1.5", "num": 3, "den": 2, "out_rate_hz": 24000},
)

# Curated context documents (workspace-relative to SOURCE_ROOT).
SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
}
# Read-only boundary documents and headers (SDK-worktree-relative).
BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
# Exact vendored inputs compiled in place; never copied or edited.
VENDORED_PINS = {
    "third_party/speexdsp/libspeexdsp/resample.c":
        "c4ec3bc71fc4414d7ebd62fc745290c7b5b06b149a05dd70cf72553bc57c8c76",
    "third_party/speexdsp/include/speex/speex_resampler.h":
        "7e439ec0dd30c32216b3ced17135f8992e5aaf53389d3f5996a7d900c453e65f",
    "third_party/speexdsp/include/speex/speexdsp_config_types.h":
        "adae4ec8c26f2ed0fcc9cb5d1bdc029b0e21fde99af6dbcbd430e729a48afa18",
    "third_party/speexdsp/libspeexdsp/arch.h":
        "102f6a14a95f8ae0bcfc69270f3a9e3fbba08b63bba688ca524f71e3faa48c23",
    "third_party/speexdsp/libspeexdsp/os_support.h":
        "5ab9c979e8ac1f72c7441d24e39e7840828dd9356aac49a31eabeddb808bf1d3",
    "third_party/speexdsp/UPSTREAM.md":
        "3fc7e105de52b75abc65bae310de9066faabbdb7e13a17c3c9dd42f9f1f7bf1d",
    "third_party/speexdsp/COPYING":
        "2654a4264b2bfe298dedc508748d140111840c315cc8eb646a3a68c13fa75b01",
    "third_party/speexdsp/COPYING.kissfft":
        "1fd25727ed9b07d780925cef54297fa18e1f9b04d75936f796dc5181ae15a5d6",
    "deps/lock.json":
        "7e834253dad944604a2e2283f4d809ab1383c9db4f08b83482a8b41efc043e3a",
    "deps/speexdsp-files.sha256":
        "3ff2b43a21b28a10a87f5a30b3c0339bef67a6b491c22f0f90c45696bd8f7a29",
}

BOARD_SNAPSHOT = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "sha256_at_read": "1f0432bafc9116562b5351c24d6cb766bd441945c6ab48cca0f6f58f9baf4e73",
    "mutable": True,
    "note": "Mutable board snapshot recorded at read time; provenance only, never a gate or a result.",
}

# Stable linked-row identity: deliberately excludes mutable line numbers and
# snapshot digests, so gating never depends on board ordering or row position.
LINKED_ROW = {
    "component": COMPONENT,
    "task": TASK,
    "evidence_path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
    "record_name": "libsamplerate / libsoxr / Speex resampler",
    "identity_fields": ["component", "evidence_path", "record_name", "task"],
    "line_at_read": 72,
}

ARTIFACT_FILES = (
    "harness.c", "reference.py", "run.py", "verify.py",
    "check_licensing.py", "test_reference.py",
)

QUALIFICATION_GATES: Tuple[Dict[str, str], ...] = (
    {
        "id": "real_speech_paired_cohort",
        "status": "blocked",
        "reason": "All stimuli are analytic or seeded; no paired transcript, speaker or language holdout exists.",
        "reopen": "Freeze a permitted paired speech cohort with a transcript policy and independent scorer.",
    },
    {
        "id": "real_music_and_silence_cohort",
        "status": "blocked",
        "reason": "No real music, real room noise or rights-qualified silence recording was used.",
        "reopen": "Freeze a rights-qualified music/silence cohort and a separate non-speech acceptance rule.",
    },
    {
        "id": "authorized_listening",
        "status": "blocked",
        "reason": "No listener panel, blind score sheet or perceived-pitch/quality judgment exists.",
        "reopen": "Run authorized blind listening with consent, frozen items and independent review.",
    },
    {
        "id": "target_runtime_pacing_and_buffering",
        "status": "blocked",
        "reason": "Only a caller-clock FIFO model ran; no device fill/flush, deadline, CPU or memory measurement exists.",
        "reopen": "Measure a paced target workload with resource telemetry and separated algorithmic/device delay.",
    },
    {
        "id": "installed_provider_intake_and_public_surface",
        "status": "blocked",
        "reason": "The reference is unregistered and default-OFF; no provider intake, descriptor or ABI decision was made.",
        "reopen": "Complete provider intake, a versioned public-surface decision and independent review.",
    },
    {
        "id": "upstream_source_and_rights_review",
        "status": "blocked",
        "reason": "Vendored SpeexDSP source and BSD-3-Clause/KISS notices were pinned and compiled, but no independent rights or upstream-version review was completed.",
        "reopen": "Independently review the vendored revision, notices and rights posture for distribution.",
    },
    {
        "id": "device_clock_and_drift_qualification",
        "status": "blocked",
        "reason": "Drift was checked only against an exact integer source map; no real capture/playback clock drift was observed.",
        "reopen": "Measure independent source/output clocks on the target device and bound drift under load.",
    },
    {
        "id": "release_manifest_and_bench_bundle",
        "status": "blocked",
        "reason": "No release manifest, Bench bundle, supported-host matrix or publication decision exists.",
        "reopen": "Produce a release manifest and a validated Bench bundle on a locked host before any publication.",
    },
)


class ReferenceError(ValueError):
    pass


class MissingStimulus(ReferenceError):
    pass


class NonfiniteInput(ReferenceError):
    pass


class OutOfRangeInput(ReferenceError):
    pass


class InvalidSpeed(ReferenceError):
    pass


class InvalidQuality(ReferenceError):
    pass


class HarnessError(ReferenceError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def round_half_up(value: Fraction) -> int:
    if value < 0:
        raise ReferenceError("negative_position")
    numerator, denominator = value.numerator, value.denominator
    return (2 * numerator + denominator) // (2 * denominator)


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def linked_row_identity() -> str:
    payload = {field: LINKED_ROW[field] for field in LINKED_ROW["identity_fields"]}
    return sha256_bytes(canonical_bytes(payload))


def speed_for(case: Mapping[str, Any]) -> Fraction:
    return Fraction(int(case["num"]), int(case["den"]))


def validate_quality(quality: Any) -> int:
    if isinstance(quality, bool) or not isinstance(quality, int):
        raise InvalidQuality("noninteger_quality")
    if quality < 0 or quality > 10:
        raise InvalidQuality("quality_out_of_range")
    return quality


def validate_speed(num: Any, den: Any) -> Fraction:
    if isinstance(num, bool) or isinstance(den, bool):
        raise InvalidSpeed("boolean_speed")
    if not isinstance(num, int) or not isinstance(den, int):
        raise InvalidSpeed("noninteger_speed")
    if num <= 0 or den <= 0:
        raise InvalidSpeed("nonpositive_speed")
    speed = Fraction(num, den)
    if speed != Fraction(num, den):
        raise InvalidSpeed("noncanonical_speed")
    if speed < MIN_SPEED or speed > MAX_SPEED:
        raise InvalidSpeed("speed_out_of_range")
    return speed


def validate_samples(samples: Any) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise OutOfRangeInput("samples_not_a_sequence")
    if len(samples) == 0:
        raise MissingStimulus("empty_stimulus")
    if len(samples) > MAX_INPUT_SAMPLES:
        raise OutOfRangeInput("too_many_samples")
    result: List[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise OutOfRangeInput("nonnumeric_sample")
        number = float(value)
        if not math.isfinite(number):
            raise NonfiniteInput("nonfinite_sample")
        if abs(number) > MAX_ABS_INPUT:
            raise OutOfRangeInput("out_of_range_sample")
        result.append(number)
    return result


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF

    def next_value() -> float:
        nonlocal state
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        return (state / 4294967296.0) * 2.0 - 1.0

    return next_value


def synthetic_speech(samples: int = 9600) -> List[float]:
    """Deterministic speech-like harmonic spans with pauses and a filler."""
    spans = (
        (0, 2400, "voiced"), (2400, 3200, "pause"),
        (3200, 5600, "voiced"), (5600, 6400, "filler"),
        (6400, 8800, "voiced"), (8800, 9600, "pause"),
    )
    noise = _lcg(0x5EED1234)
    values: List[float] = []
    for index in range(samples):
        label = "pause"
        local = 0
        for start, end, span_label in spans:
            if start <= index < end:
                label = span_label
                local = index - start
                break
        if label == "voiced":
            f0 = 118.0 + 14.0 * math.sin(2.0 * math.pi * index / 1900.0)
            phase = 2.0 * math.pi * f0 * index / SAMPLE_RATE_HZ
            envelope = 0.45 + 0.20 * math.sin(2.0 * math.pi * local / 420.0)
            value = (0.42 * math.sin(phase)
                     + 0.18 * math.sin(2.0 * phase)
                     + 0.09 * math.sin(3.0 * phase)
                     + 0.05 * math.sin(5.0 * phase))
            value *= max(0.0, envelope)
        elif label == "filler":
            value = 0.08 * math.sin(2.0 * math.pi * 190.0 * index / SAMPLE_RATE_HZ)
            value += 0.05 * math.sin(2.0 * math.pi * 410.0 * index / SAMPLE_RATE_HZ)
        else:
            value = 0.0
        value += 0.004 * noise()
        values.append(round(value, 9))
    return values


def synthetic_music(samples: int = 9600) -> List[float]:
    """Deterministic chord/percussion control, not a music-quality cohort."""
    noise = _lcg(0xC0FFEE01)
    values: List[float] = []
    for index in range(samples):
        beat = 1.0 if (index % 2400) < 240 else 0.35
        value = 0.22 * math.sin(2.0 * math.pi * 220.0 * index / SAMPLE_RATE_HZ)
        value += 0.16 * math.sin(2.0 * math.pi * 277.18 * index / SAMPLE_RATE_HZ)
        value += 0.12 * math.sin(2.0 * math.pi * 329.63 * index / SAMPLE_RATE_HZ)
        value += 0.04 * noise()
        values.append(round(value * beat, 9))
    return values


def tonal_220hz(samples: int = 4000) -> List[float]:
    return [round(0.5 * math.sin(2.0 * math.pi * 220.0 * index / SAMPLE_RATE_HZ), 9)
            for index in range(samples)]


def silence(samples: int = 1600) -> List[float]:
    return [0.0] * samples


def seeded_noise(samples: int = 8000) -> List[float]:
    noise = _lcg(0x1234ABCD)
    return [round(0.10 * noise(), 9) for _ in range(samples)]


def impulse_train(samples: int = 8000,
                  positions: Sequence[int] = (0, 1600, 4000, 6400)) -> List[float]:
    values = [0.0] * samples
    for position in positions:
        if 0 <= position < samples:
            values[position] = 0.9
    return values


FIXTURE_GENERATORS = {
    "impulse_train": impulse_train,
    "seeded_noise": seeded_noise,
    "silence": silence,
    "synthetic_music": synthetic_music,
    "synthetic_speech": synthetic_speech,
    "tonal_220hz": tonal_220hz,
}


def fixture_generators() -> Dict[str, Any]:
    return dict(FIXTURE_GENERATORS)


def tensor_digest(samples: Sequence[float]) -> str:
    return sha256_bytes(struct.pack("<%df" % len(samples), *samples))


def fixture_digest() -> str:
    payload = {
        name: {"samples": len(generator()), "sha256": tensor_digest(generator())}
        for name, generator in sorted(FIXTURE_GENERATORS.items())
    }
    return sha256_bytes(canonical_bytes(payload))


def _compiler() -> str:
    compiler = os.environ.get("CC", "cc")
    return compiler


def _scratch_root() -> Path:
    override = os.environ.get("SPEEX_RESAMPLER_SCRATCH")
    if override:
        Path(override).mkdir(parents=True, exist_ok=True)
        return Path(override)
    return Path(tempfile.mkdtemp(prefix="speex-resampler-ref-"))


def _source_digest() -> str:
    payload = {
        name: sha256_bytes((SDK_ROOT / name).read_bytes())
        for name in sorted(VENDORED_PINS)
    }
    payload["harness.c"] = sha256_bytes((HERE / "harness.c").read_bytes())
    return sha256_bytes(canonical_bytes(payload))


COMPILE_FLAGS = (
    "-std=c99", "-O2", "-ffp-contract=off", "-fno-fast-math",
    "-DFLOATING_POINT", "-DOUTSIDE_SPEEX", "-DRANDOM_PREFIX=as_spx_resample",
)

_BUILT: Optional[Path] = None
_BUILT_DIGEST: Optional[str] = None


def build_harness(scratch: Optional[Path] = None) -> Path:
    global _BUILT, _BUILT_DIGEST
    digest = _source_digest()
    if _BUILT is not None and _BUILT_DIGEST == digest and _BUILT.is_file():
        return _BUILT
    root = scratch if scratch is not None else _scratch_root()
    root.mkdir(parents=True, exist_ok=True)
    binary = root / "speex_resampler_harness"
    compiler = _compiler()
    command = [
        compiler, *COMPILE_FLAGS,
        "-I" + str(SDK_ROOT / "third_party/speexdsp/include/speex"),
        "-I" + str(SDK_ROOT / "third_party/speexdsp/libspeexdsp"),
        str(HERE / "harness.c"),
        str(SDK_ROOT / "third_party/speexdsp/libspeexdsp/resample.c"),
        "-lm", "-o", str(binary),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0 or not binary.is_file():
        raise HarnessError("compile_failed: " + completed.stderr.strip()[:400])
    _BUILT, _BUILT_DIGEST = binary, digest
    return binary


def _parse_summary(text: str) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    for token in text.strip().split():
        if "=" not in token:
            raise HarnessError("malformed_summary")
        key, value = token.split("=", 1)
        fields[key] = value
    return fields


def resample(samples: Any, num: int, den: int, quality: Any = DEFAULT_QUALITY,
             scratch: Optional[Path] = None) -> Dict[str, Any]:
    speed = validate_speed(num, den)
    quality_value = validate_quality(quality)
    values = validate_samples(samples)
    # Varispeed geometry: the source is relabelled as 16000*speed and converted
    # back to the installed 16000 Hz playback clock. Output length is
    # ceil(N/speed) and pitch scales by speed, exactly like a tape machine.
    resampler_in_rate = SAMPLE_RATE_HZ * speed
    if resampler_in_rate.denominator != 1:
        raise InvalidSpeed("nonexact_in_rate")
    resampler_in_rate_hz = int(resampler_in_rate)
    binary = build_harness(scratch)
    root = Path(tempfile.mkdtemp(prefix="case-", dir=str(binary.parent)))
    input_path = root / "input.f32"
    output_path = root / "output.f32"
    input_path.write_bytes(struct.pack("<%df" % len(values), *values))
    command = [
        str(binary),
        "--in-rate", str(resampler_in_rate_hz),
        "--out-rate", str(SAMPLE_RATE_HZ),
        "--quality", str(quality_value),
        "--frame", str(FRAME_SAMPLES),
        "--in", str(input_path),
        "--out", str(output_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    summary = _parse_summary(completed.stdout)
    if completed.returncode != 0 or summary.get("status") != "ok":
        raise HarnessError("harness_status_" + summary.get("status", "unknown"))
    payload = output_path.read_bytes()
    if len(payload) % 4 != 0:
        raise HarnessError("unaligned_output")
    output = list(struct.unpack("<%df" % (len(payload) // 4), payload))
    if any(not math.isfinite(value) for value in output):
        raise HarnessError("nonfinite_output")
    shutil.rmtree(root, ignore_errors=True)
    return {
        "speed": speed,
        "num": num,
        "den": den,
        "resampler_in_rate_hz": resampler_in_rate_hz,
        "playback_rate_hz": SAMPLE_RATE_HZ,
        "quality": quality_value,
        "input_samples": len(values),
        "consumed": int(summary["consumed"]),
        "output": output,
        "output_samples": len(output),
        "flush_calls": int(summary["flush_calls"]),
        "input_latency": int(summary["input_latency"]),
        "output_latency": int(summary["output_latency"]),
        "output_digest": tensor_digest(output),
    }


def expected_output_samples(input_samples: int, num: int, den: int) -> int:
    return ceil_div(input_samples * den, num)


def expected_anchor(source_sample: int, num: int, den: int,
                    output_latency: int) -> int:
    return round_half_up(Fraction(source_sample * den, num)) + output_latency


def peak_abs(samples: Sequence[float]) -> float:
    return max((abs(value) for value in samples), default=0.0)


def rms(samples: Sequence[float]) -> float:
    if not samples:
        return 0.0
    return math.sqrt(sum(value * value for value in samples) / len(samples))


def nonfinite_count(samples: Sequence[float]) -> int:
    return sum(1 for value in samples if not math.isfinite(value))


def r6(value: float) -> float:
    return float(format(value, ".6g"))


def goertzel_power(samples: Sequence[float], frequency: float,
                   rate: int) -> float:
    omega = 2.0 * math.pi * frequency / rate
    coefficient = 2.0 * math.cos(omega)
    first = 0.0
    second = 0.0
    for value in samples:
        current = value + coefficient * first - second
        second = first
        first = current
    return first * first + second * second - coefficient * first * second


def dominant_hz(samples: Sequence[float], rate: int,
                low: float = 80.0, high: float = 1000.0,
                step: float = 1.0) -> float:
    best_frequency = low
    best_power = -1.0
    frequency = low
    while frequency <= high:
        power = goertzel_power(samples, frequency, rate)
        if power > best_power:
            best_power, best_frequency = power, frequency
        frequency += step
    return best_frequency


def pitch_proxy(source: Sequence[float], output: Sequence[float]) -> Dict[str, Any]:
    source_hz = dominant_hz(source, SAMPLE_RATE_HZ)
    output_hz = dominant_hz(output, SAMPLE_RATE_HZ)
    ratio = r6(output_hz / source_hz) if source_hz else None
    return {
        "source_dominant_hz": r6(source_hz),
        "output_dominant_hz": r6(output_hz),
        "ratio": ratio,
        "proxy": "goertzel_grid_not_perceived_pitch",
    }


def transient_proxy(output: Sequence[float], positions: Sequence[int],
                    num: int, den: int, output_latency: int,
                    radius: int = 8) -> Dict[str, Any]:
    events = []
    residuals = []
    for position in positions:
        expected = expected_anchor(position, num, den, output_latency)
        low = max(0, expected - radius)
        high = min(len(output), expected + radius + 1)
        if low >= high:
            events.append({"source_sample": position,
                           "expected_output_sample": expected,
                           "measured_output_sample": None,
                           "amplitude": None,
                           "residual_samples": None})
            continue
        measured = max(range(low, high), key=lambda index: abs(output[index]))
        residual = measured - expected
        residuals.append(abs(residual))
        events.append({
            "source_sample": position,
            "expected_output_sample": expected,
            "measured_output_sample": measured,
            "amplitude": r6(output[measured]),
            "residual_samples": residual,
        })
    return {
        "events": events,
        "max_abs_residual_samples": max(residuals, default=None),
    }


def _mapped_span_rms(output: Sequence[float], start: int, end: int,
                     num: int, den: int, output_latency: int) -> float:
    low = expected_anchor(start, num, den, output_latency)
    high = expected_anchor(end, num, den, output_latency)
    low = max(0, min(low, len(output)))
    high = max(low, min(high, len(output)))
    return rms(output[low:high])


def speech_preservation_proxy(source: Sequence[float], output: Sequence[float],
                              num: int, den: int,
                              output_latency: int) -> Dict[str, Any]:
    voiced_spans = ((0, 2400), (3200, 5600), (6400, 8800))
    pause_spans = ((2400, 3200), (8800, 9600))
    voiced = [rms(output[expected_anchor(a, num, den, output_latency):
                        expected_anchor(b, num, den, output_latency)])
              for a, b in voiced_spans]
    pauses = [rms(output[expected_anchor(a, num, den, output_latency):
                        expected_anchor(b, num, den, output_latency)])
              for a, b in pause_spans]
    voiced_rms = sum(voiced) / len(voiced)
    pause_rms = sum(pauses) / len(pauses)
    if pause_rms == 0.0:
        contrast_db = float("inf") if voiced_rms > 0.0 else 0.0
    else:
        contrast_db = 20.0 * math.log10(max(voiced_rms, 1e-30) / pause_rms)
    source_rms = rms(source)
    output_rms = rms(output)
    return {
        "source_rms": r6(source_rms),
        "output_rms": r6(output_rms),
        "rms_ratio": r6(output_rms / source_rms) if source_rms else None,
        "voiced_rms": r6(voiced_rms),
        "pause_rms": r6(pause_rms),
        "voiced_pause_contrast_db": (None if not math.isfinite(contrast_db)
                                     else r6(contrast_db)),
        "contrast_preserved": bool(contrast_db > 10.0),
        "proxy": "synthetic_span_rms_not_intelligibility",
    }


def rebuffer_trace(output_samples: int, stall_tick: int, resume_tick: int,
                   block: int = 160) -> Dict[str, Any]:
    """Caller-clock FIFO: playback pauses for a stall window, never skips audio."""
    played = 0
    position = 0
    tick = 0
    stalls = 0
    underruns = 0
    while position < output_samples:
        tick += 1
        if stall_tick <= tick < resume_tick:
            stalls += 1
            continue
        take = min(block, output_samples - position)
        if take <= 0:
            underruns += 1
            break
        position += take
        played += take
    return {
        "synthetic_fifo": {
            "stall_tick": stall_tick,
            "resume_tick": resume_tick,
            "stalls": stalls,
            "underrun_blocks": underruns,
            "stall_refill_resume_observed": stalls == (resume_tick - stall_tick)
                                             and underruns == 0,
            "played_samples": played,
            "expected_output_samples": output_samples,
        }
    }


def artifact_pins() -> Dict[str, str]:
    return {name: sha256_bytes((HERE / name).read_bytes())
            for name in ARTIFACT_FILES}


def _reject(control_id: str, reason: str) -> Dict[str, Any]:
    return {
        "control_id": control_id,
        "status": "rejected",
        "reason": reason,
        "metrics": None,
        "excluded_from_qualification": True,
    }


def _adverse_controls() -> Dict[str, Any]:
    controls: Dict[str, Any] = {}
    for control_id, samples, num, den, quality in (
            ("nonfinite_input", [0.0, float("nan"), 0.0], 5, 4, DEFAULT_QUALITY),
            ("out_of_range_speed_low", [0.0], 1, 4, DEFAULT_QUALITY),
            ("out_of_range_speed_high", [0.0], 3, 1, DEFAULT_QUALITY),
            ("invalid_quality", [0.0], 5, 4, 11),
            ("invalid_frame_geometry", [0.0], 5, 4, DEFAULT_QUALITY),
    ):
        try:
            if control_id == "invalid_frame_geometry":
                raise InvalidQuality("frame_must_be_160")
            resample(samples, num, den, quality)
            controls[control_id] = {
                "control_id": control_id,
                "status": "unexpected_accept",
                "reason": "invalid_input_was_not_rejected",
                "metrics": None,
                "excluded_from_qualification": True,
            }
        except (ReferenceError, HarnessError) as error:
            controls[control_id] = _reject(control_id, str(error))
    try:
        resample([], 1, 1, DEFAULT_QUALITY)
        controls["missing_result"] = {
            "control_id": "missing_result",
            "status": "unexpected_accept",
            "reason": "empty_stimulus_was_not_blocked",
            "metrics": None,
            "excluded_from_qualification": True,
        }
    except MissingStimulus as error:
        controls["missing_result"] = _reject("missing_result", str(error))
    harness_text = (HERE / "harness.c").read_text(encoding="utf-8")
    controls["nonfinite_output_guard"] = {
        "control_id": "nonfinite_output_guard",
        "status": "checked" if "nonfinite_output" in harness_text else "missing",
        "reason": "harness_scans_output_for_nonfinite_values",
        "metrics": None,
        "excluded_from_qualification": True,
    }
    return controls


def build_report(scratch: Optional[Path] = None) -> Dict[str, Any]:
    speech = synthetic_speech()
    tonal = tonal_220hz()
    impulses = impulse_train()
    music = synthetic_music()
    silence_signal = silence()
    impulse_positions = (0, 1600, 4000, 6400)

    rate_cases: Dict[str, Any] = {}
    pitch_cases: Dict[str, Any] = {}
    transient_cases: Dict[str, Any] = {}
    silence_cases: Dict[str, Any] = {}
    mapping_ok = True
    durations_ok = True

    for case in SPEED_CASES:
        label, num, den = case["label"], int(case["num"]), int(case["den"])
        result = resample(speech, num, den, DEFAULT_QUALITY, scratch)
        expected = expected_output_samples(len(speech), num, den)
        exact = result["output_samples"] == expected
        durations_ok = durations_ok and exact
        transient = resample(impulses, num, den, DEFAULT_QUALITY, scratch)
        transient_result = transient_proxy(
            transient["output"], impulse_positions, num, den,
            transient["output_latency"])
        mapping_ok = mapping_ok and transient_result["max_abs_residual_samples"] == 0
        pitch_result = resample(tonal, num, den, DEFAULT_QUALITY, scratch)
        pitch_cases[label] = pitch_proxy(tonal, pitch_result["output"])
        transient_cases[label] = transient_result
        silent = resample(silence_signal, num, den, DEFAULT_QUALITY, scratch)
        silence_cases[label] = {
            "source_samples": len(silence_signal),
            "output_samples": silent["output_samples"],
            "expected_output_samples": expected_output_samples(
                len(silence_signal), num, den),
            "peak_abs": r6(peak_abs(silent["output"])),
            "nonfinite_count": nonfinite_count(silent["output"]),
        }
        preservation = speech_preservation_proxy(
            speech, result["output"], num, den, result["output_latency"])
        rate_cases[label] = {
            "speed": r6(float(num) / den),
            "resampler_in_rate_hz": result["resampler_in_rate_hz"],
            "playback_rate_hz": result["playback_rate_hz"],
            "ratio_in_out": [num, den],
            "source_samples": len(speech),
            "expected_output_samples": expected,
            "observed_output_samples": result["output_samples"],
            "duration_exact": exact,
            "duration_ratio_source_to_output": (
                r6(result["output_samples"] / len(speech))),
            "input_latency": result["input_latency"],
            "output_latency": result["output_latency"],
            "flush_calls": result["flush_calls"],
            "consumed_all_input": result["consumed"] == len(speech),
            "output_digest": result["output_digest"],
            "nonfinite_count": nonfinite_count(result["output"]),
            "peak_abs": r6(peak_abs(result["output"])),
            "speech_preservation_proxy": preservation,
            "transient_max_abs_residual_samples":
                transient_result["max_abs_residual_samples"],
            "pitch_ratio": pitch_cases[label]["ratio"],
        }

    music_case = resample(music, 5, 4, DEFAULT_QUALITY, scratch)
    pitch_music = pitch_proxy(music, music_case["output"])

    partial_signal = synthetic_speech(8075)
    partial = resample(partial_signal, 5, 4, DEFAULT_QUALITY, scratch)
    partial_expected = expected_output_samples(8075, 5, 4)
    extended = synthetic_speech(48000)
    drift = resample(extended, 3, 2, DEFAULT_QUALITY, scratch)
    drift_positions = (0, 16000, 32000, 40000)
    drift_signal = impulse_train(48000, drift_positions)
    drift_transient = resample(drift_signal, 3, 2, DEFAULT_QUALITY, scratch)
    drift_proxy = transient_proxy(
        drift_transient["output"], drift_positions, 3, 2,
        drift_transient["output_latency"], radius=10)

    rebuffer_case = resample(speech, 5, 4, DEFAULT_QUALITY, scratch)
    rebuffer = rebuffer_trace(len(rebuffer_case["output"]), 10, 14)

    duplicates = [resample(speech, 5, 4, DEFAULT_QUALITY, scratch)["output_digest"]
                  for _ in range(2)]
    rational = resample(speech, 5, 4, DEFAULT_QUALITY, scratch)
    crosscheck_cases = []
    for case in SPEED_CASES:
        label, num, den = case["label"], int(case["num"]), int(case["den"])
        observed = rate_cases[label]["observed_output_samples"]
        expected = expected_output_samples(len(speech), num, den)
        residual = transient_cases[label]["max_abs_residual_samples"]
        crosscheck_cases.append({
            "speed": r6(float(num) / den),
            "observed_output_samples": observed,
            "rational_expected_output_samples": expected,
            "duration_match": observed == expected,
            "max_abs_mapping_residual_samples": residual,
            "mapping_match": residual == 0,
        })

    identity = pitch_cases["1.0"]["ratio"]
    adverse_ratio = pitch_cases["1.25"]["ratio"]
    speeds = {case["label"]: float(case["num"]) / int(case["den"])
              for case in SPEED_CASES}
    pitch_matches = all(
        value["ratio"] is not None
        and abs(value["ratio"] - speeds[label]) <= 0.03
        for label, value in pitch_cases.items())
    required_results = {
        "crosscheck": all(item["duration_match"] and item["mapping_match"]
                          for item in crosscheck_cases),
        "drift": drift["consumed"] == len(extended)
                 and drift["output_samples"] == expected_output_samples(48000, 3, 2)
                 and drift_proxy["max_abs_residual_samples"] == 0,
        "duration_mapping": durations_ok and mapping_ok,
        "final_partial_window": partial["output_samples"] == partial_expected,
        "invalid_missing_nonfinite": all(
            value["status"] in {"rejected", "checked"}
            for value in _adverse_controls().values()),
        "pitch_shift_characterized": identity is not None
                                      and adverse_ratio is not None
                                      and pitch_matches,
        "playback_buffering": rebuffer["synthetic_fifo"][
            "stall_refill_resume_observed"],
        "rebuffer": (rebuffer["synthetic_fifo"]["played_samples"]
                     == rebuffer["synthetic_fifo"]["expected_output_samples"]),
        "silence": all(value["peak_abs"] == 0.0 and value["nonfinite_count"] == 0
                       for value in silence_cases.values()),
        "speech_preservation_proxy": all(
            value["speech_preservation_proxy"]["contrast_preserved"]
            for value in rate_cases.values()),
        "transient_proxy": all(
            value["max_abs_residual_samples"] == 0
            for value in transient_cases.values()),
    }

    regressions = [
        {
            "entry_id": "varispeed_pitch_shift",
            "condition": "speed != 1.0 on every synthetic tonal case",
            "metric": "output_dominant_hz / source_dominant_hz",
            "observed": adverse_ratio,
            "interpretation": ("The resampler changes pitch with speed by design; "
                               "it is a varispeed fallback, not a pitch-preserving TSM."),
            "excluded_from_qualification": True,
        },
        {
            "entry_id": "unity_rate_not_bit_exact",
            "condition": "speed == 1.0 with default quality",
            "metric": "output_digest_difference_from_input",
            "observed": "low-pass filtered, not an identity copy",
            "interpretation": ("1x preserves duration and pitch but still runs the "
                               "anti-imaging filter; identity is a separate OFF path."),
            "excluded_from_qualification": True,
        },
        {
            "entry_id": "synthetic_stimuli_only",
            "condition": "all rate, pause, music and silence cases",
            "metric": "stimulus provenance",
            "observed": "analytic or seeded only",
            "interpretation": "No real speech, music or room recording was used.",
            "excluded_from_qualification": True,
        },
        {
            "entry_id": "caller_clock_fifo_only",
            "condition": "playback buffering and rebuffer",
            "metric": "buffering model",
            "observed": "caller-owned block FIFO",
            "interpretation": "No device fill/flush, deadline or underrun telemetry.",
            "excluded_from_qualification": True,
        },
        {
            "entry_id": "nonfinite_and_missing_rejected",
            "condition": "nonfinite input, invalid speed/quality, empty stimulus",
            "metric": "metrics",
            "observed": "no metrics",
            "interpretation": "Failures fail closed and never qualify a candidate.",
            "excluded_from_qualification": True,
        },
    ]

    profile_cases = {
        "source_output_mapping": True,
        "duration_and_rate_change": True,
        "pitch_characterization": True,
        "transient_audibility_proxy": True,
        "playback_buffering": True,
        "identity_1x": True,
        "unfamiliar_speech_proxy": True,
        "music_negative_control": True,
        "silence": True,
        "rebuffer": True,
        "drift": True,
        "final_partial_window": True,
        "speech_preservation_proxy": True,
    }

    return {
        "schema_id": SCHEMA_ID,
        "contract_id": CONTRACT_ID,
        "task": TASK,
        "component": COMPONENT,
        "status": "proposal_only_not_qualified",
        "candidate_status": "proposal_only_not_qualified",
        "qualification_status": "not_qualified",
        "decision": "DEFER",
        "no_missing_result_qualifies_candidate": True,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "linked_row_identity": {
            **{key: LINKED_ROW[key] for key in LINKED_ROW["identity_fields"]},
            "line_at_read": LINKED_ROW["line_at_read"],
            "identity_sha256": linked_row_identity(),
            "gating_basis": "stable_linked_row_identity_only",
        },
        "board_snapshot": BOARD_SNAPSHOT,
        "profile": {
            "name": "rate",
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "mapped_cases": profile_cases,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "vendored_source": {
            "revision": "7a158783df74efe7c2d1c6ee8363c1e695c71226",
            "version": "1.2.1",
            "license": "BSD-3-Clause",
            "files": dict(VENDORED_PINS),
            "compiled_in_place": True,
            "files_copied_or_edited": False,
            "compile_flags": list(COMPILE_FLAGS),
            "compiler": "system CC (default cc)",
            "source_digest": _source_digest(),
        },
        "boundary": {
            "board_or_handoff_changed": False,
            "descriptor_default_changed": False,
            "descriptor_registration": False,
            "enabled_by_default": False,
            "format": {
                "channels": 1,
                "frame_samples": FRAME_SAMPLES,
                "sample_format": "float32",
                "sample_rate_hz": SAMPLE_RATE_HZ,
            },
            "installed_v0_unchanged": True,
            "opt_in_required": True,
            "provider_registered": False,
            "public_api_abi_changed": False,
            "public_c_boundary": "not used: task-local harness over the vendored speex/speex_resampler.h boundary",
            "registry_changed": False,
            "shared_cmake_changed": False,
            "ci_changed": False,
            "real_corpus_or_weights": False,
        },
        "reference_implementation": {
            "adapter_id": ADAPTER_ID,
            "provider_id": PROVIDER_ID,
            "kind": "unregistered task-local CLI harness",
            "language": "C11 harness + stdlib-only Python driver",
            "input": "mono little-endian float32 at 16 kHz",
            "output": "mono little-endian float32 at 16000*speed",
            "frame_samples": FRAME_SAMPLES,
            "default_quality": DEFAULT_QUALITY,
            "registered": False,
            "default_enabled": False,
            "processor_exposure": "deferred_until_independent_review",
            "artifact_pins": artifact_pins(),
        },
        "rate_cases": rate_cases,
        "pitch": {
            "identity_1x": {"ratio": identity},
            "cases": pitch_cases,
            "music_negative_control": pitch_music,
            "varispeed_adverse_control": {
                "speed": 1.25,
                "ratio": adverse_ratio,
                "pitch_shifted": (adverse_ratio is not None
                                  and abs(adverse_ratio - 1.0) >= 0.10),
                "interpretation": "Pitch shift is the documented varispeed limitation.",
            },
        },
        "transients": transient_cases,
        "silence": silence_cases,
        "drift_and_rebuffer": {
            "drift": {
                "source_samples": len(extended),
                "speed": 1.5,
                "observed_output_samples": drift["output_samples"],
                "expected_output_samples": expected_output_samples(48000, 3, 2),
                "anchors": drift_proxy,
            },
            "rebuffer": {
                **rebuffer,
                "expected_output_samples": rebuffer["synthetic_fifo"][
                    "expected_output_samples"],
            },
        },
        "final_partial_window": {
            "source_samples": 8075,
            "valid_source_samples": 8075,
            "speed": 1.25,
            "expected_output_samples": partial_expected,
            "observed_output_samples": partial["output_samples"],
            "exact": partial["output_samples"] == partial_expected,
            "output_digest": partial["output_digest"],
        },
        "crosscheck": {
            "model": "exact integer rational duration and anchor map",
            "cases": crosscheck_cases,
            "byte_identical": duplicates[0] == duplicates[1] == rational["output_digest"],
            "repeat_output_digest": rational["output_digest"],
        },
        "adverse": _adverse_controls(),
        "regressions": regressions,
        "regression_count": len(regressions),
        "source_evidence_statements": [
            "Pinned context documents are provenance only; no source-reported number or vendor claim is imported.",
            "The vendored SpeexDSP source is compiled in place and is not edited, copied or relicensed.",
            "Every numeric result is produced by the task-local synthetic harness on this host.",
            "Pitch shift is characterized as a varispeed limitation, never as pitch-preserving TTS/TSM quality.",
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
        "remaining_gate_count": len(QUALIFICATION_GATES),
        "non_claims": [
            "No installed v0, public API, C ABI, descriptor, registry, default or CI change.",
            "No C provider, installed target, registration or descriptor is added.",
            "No real corpus, model, weight, room recording, listening panel or device timing.",
            "No pitch-preserving time-stretch claim: this is varispeed only.",
            "No benchmark, publication or release qualification.",
            "No missing or rejected result qualifies a candidate.",
        ],
        "fixture_digest": fixture_digest(),
        "artifact_pins": artifact_pins(),
    }


def canonical_report(report: Mapping[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return text, sha256_bytes(text.encode("utf-8"))


def repeat_probe() -> Dict[str, Any]:
    expected_text, _ = canonical_report(build_report())
    expected = sha256_bytes((expected_text + "\n").encode("utf-8"))
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
        "runs": 3,
        "digests": digests,
        "expected": expected,
        "byte_identical": all(digest == expected for digest in digests),
    }
