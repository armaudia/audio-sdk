# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local reference for SDK-METRICGAN-SPEECHBRAIN-VOICEBANK.

This package models the MetricGAN+ SpeechBrain VoiceBank boundary as a
*caller-supplied-asset reference*. The exact checkpoint, config, SpeechBrain
runtime and VoiceBank+DEMAND corpus are absent from this SDK worktree and were
not downloaded. Nothing here loads weights, reads media, invokes a vendor
runtime, measures a device clock, conducts listening, benchmarks the SDK or
makes a release claim.

The deterministic synthetic surrogate emulates only two *structural* properties
recorded for the real candidate: whole-utterance processing, and SpeechBrain's
``resynthesize`` unit-peak output normalization. Its measured numbers are
synthetic mechanism evidence, never a quality, parity or release result.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import scorer

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK_ID = "SDK-METRICGAN-SPEECHBRAIN-VOICEBANK"
TITLE = "MetricGAN+ SpeechBrain VoiceBank"
SLUG = "metricgan-speechbrain-voicebank"
COMPONENT = "metricgan-speechbrain-voicebank"
BASE_COMMIT = "6f58f3d721908806f8c4a0a1e0dc6de846cef54c"
BRANCH = "swarm/SDK-METRICGAN-SPEECHBRAIN-VOICEBANK"
REVIEWER = "reviewer-METRICGAN-SPEECHBRAIN-VOICEBANK"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
PROFILE = "enhancement"
FAMILY = "model_reference"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"

SAMPLE_RATE = 16000
SAMPLES = 16000
FRAME_SAMPLES = 160
MAX_WHOLE_UTTERANCE_SAMPLES = 480000
SEED_BASE = 20261125
ROUND_DIGITS = 9

# Exact candidate identity, quoted from pinned provenance. No bytes are read.
MODEL_REPO = "speechbrain/metricgan-plus-voicebank"
MODEL_REPO_REVISION = "be514d321f66b5352c5a8d59c44700f57aa8c8f5"
CHECKPOINT_NAME = "enhance_model.ckpt"
CHECKPOINT_SHA256 = "147bfb866bac8264603546e035bf283370e716ed2f4b7412d308d2bcee88304f"
CHECKPOINT_BYTES = 7586021
HYPERPARAMS_SHA256 = "7bcc0835243c27f78907de0df27bc5f33d533a675787ab2eff34188404ea225a"
CONFIG_SHA256 = "18cb713936f15ae4acf84f0fab863e617bfd6faba362bcf5752d85aa1f16f833"
MODEL_CARD_LICENSE = "Apache-2.0"
SPEECHBRAIN_VERSION = "1.0.3"
SPEECHBRAIN_WHEEL_SHA256 = "9859d4c1b1fb3af3b85523c0c89f52e45a04f305622ed55f31aa32dd2fba19e9"
RUNTIME_OVERLAY = "HyperPyYAML 1.2.3, sentencepiece 0.2.2, PyYAML 6.0.3, ruamel.yaml 0.18.17, ruamel.yaml.clib 0.2.15"
CORPUS_MIRROR = "JacobLinCool/VoiceBank-DEMAND-16k"
CORPUS_REVISION = "4497db342d7312978c45690591fda86117831940"
CORPUS_TEST_PAIRS = 824
CORPUS_TEST_SECONDS = 0.576
CORPUS_LICENSE = "CC BY 4.0"

FORMAT: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": FRAME_SAMPLES,
    "samples_per_call": FRAME_SAMPLES,
}
BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "installed_v0_geometry_preserved": True,
    "processor_exposure": False,
    "shared_build_or_ci_change": False,
}
SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_only": True,
    "real_runtime": False,
    "real_metrics": False,
    "weights_accessed": False,
    "model_downloaded": False,
    "corpus_downloaded": False,
    "runtime_installed": False,
    "real_media": False,
    "real_speech": False,
    "device_timing": False,
    "listening": False,
    "benchmark": False,
    "release_claim": False,
}
CLAIMS: Dict[str, bool] = {
    "real_metricgan_runtime": False,
    "real_speechbrain_runtime": False,
    "weights_accessed": False,
    "model_downloaded": False,
    "corpus_downloaded": False,
    "real_media_read": False,
    "real_quality_score_produced": False,
    "device_timing_measured": False,
    "listening_result_produced": False,
    "benchmark_result": False,
    "release_claim": False,
}

SOURCE_PIN_PATHS: Tuple[str, ...] = (
    "source:research/voice-enhancement-20261101/candidate_matrix.csv",
    "source:research/noise_suppression_candidate_census.md",
    "source:REALTIME_COMPONENT_CANDIDATES.md",
    "source:research/voice-enhancement-20261101/agent-metricgan-eval/REPORT.md",
    "source:research/voice-enhancement-20261101/agent-metricgan-eval/adapter.json",
    "source:research/voice-enhancement-20261101/agent-metricgan-eval/requirements.lock",
    "source:research/voice-enhancement-20261101/agent-denoise-trials/REPORT.md",
    "source:research/cpp-library-voicebank-demand-20261109.md",
    "source:research/voice-enhancement-20261101/agent-hush-fixture-audit/REPORT.md",
    "source:audio-benchmark-platform/plan/swarm/VERIFICATION.md",
)
BOUNDARY_PIN_PATHS: Tuple[str, ...] = (
    "worktree:CONTRACTS.md",
    "worktree:api/include/audio_sdk/provider_v0.h",
    "worktree:api/include/audio_sdk/session_v0.h",
    "worktree:REUSE.toml",
)

LOCAL_FILES: Tuple[str, ...] = (
    "ASSET-PROVENANCE.md",
    "README.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
    "check_licensing.py",
    "contract.json",
    "contract.json.license",
    "provider.json",
    "provider.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "scorer.py",
    "test_reference.py",
    "verify.py",
)

# ---- frozen fixture specification ---------------------------------------

CONDITION_SPECS: Dict[str, Dict[str, Any]] = {
    "voiced_steady": {
        "f0_hz": 118.0, "glide": 0.06, "syllabic_hz": 2.5, "fricative": 0.02,
        "rms": 0.08, "snr_db": 5.0, "masker": "white",
    },
    "voiced_modulated": {
        "f0_hz": 96.0, "glide": 0.12, "syllabic_hz": 4.0, "fricative": 0.05,
        "rms": 0.06, "snr_db": 10.0, "masker": "white",
    },
    "fricative_heavy": {
        "f0_hz": 210.0, "glide": 0.05, "syllabic_hz": 3.0, "fricative": 0.35,
        "rms": 0.05, "snr_db": 8.0, "masker": "white",
    },
    "low_level_speech": {
        "f0_hz": 132.0, "glide": 0.04, "syllabic_hz": 2.0, "fricative": 0.04,
        "rms": 0.012, "snr_db": 3.0, "masker": "white",
    },
    "babble_like": {
        "f0_hz": 104.0, "glide": 0.05, "syllabic_hz": 3.5, "fricative": 0.08,
        "rms": 0.07, "snr_db": 12.0, "masker": "modulated_multitone",
    },
    "clipped_input": {
        "f0_hz": 146.0, "glide": 0.05, "syllabic_hz": 2.8, "fricative": 0.06,
        "rms": 0.30, "snr_db": 6.0, "masker": "white", "clip_peak": 1.0,
    },
    "silence_control": {
        "silent": True, "rms": 0.0, "snr_db": 0.0, "masker": "white",
        "noise_rms": 0.01,
    },
}
CONDITIONS: Tuple[str, ...] = tuple(CONDITION_SPECS)
SCORED_CONDITIONS: Tuple[str, ...] = tuple(
    name for name in CONDITIONS if not CONDITION_SPECS[name].get("silent"))

VARIANTS: Tuple[str, ...] = (
    "identity_noisy",
    "level_only_peak_normalized",
    "mask_only",
    "peak_normalized_mask",
    "peak_normalized_mask_rms_matched",
    "wiener_baseline_surrogate",
)
CANDIDATE_VARIANT = "peak_normalized_mask"
PEAK_ONLY_VARIANT = "level_only_peak_normalized"
RMS_MATCHED_VARIANT = "peak_normalized_mask_rms_matched"
BASELINE_VARIANT = "wiener_baseline_surrogate"
CLEAN_PRESERVATION_VARIANTS: Tuple[str, ...] = (
    "identity_noisy", "mask_only", "peak_normalized_mask", "wiener_baseline_surrogate")

MASK_FRAME = 256
MASK_HOP = 128
MASK_NOISE_FRACTION = 0.6
MASK_GAIN_FLOOR = 0.2
MASK_SMOOTHING_BINS = 9
WIENER_GAIN_FLOOR = 0.2


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def rounded(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    result = round(float(value), ROUND_DIGITS)
    return 0.0 if result == 0.0 else result


# ---- deterministic synthetic signals ------------------------------------

def rng(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 4294967296.0


def _seed_for(name: str) -> int:
    return SEED_BASE + sum((index + 1) * ord(char) for index, char in enumerate(name))


def _gauss(stream) -> float:
    # Irwin-Hall sum of four uniforms: bounded, deterministic, no library state.
    total = 0.0
    for _ in range(4):
        total += next(stream)
    return (total - 2.0) * math.sqrt(3.0)


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(math.fsum(value * value for value in values) / len(values))


def _scale_to_rms(values: List[float], target: float) -> List[float]:
    current = _rms(values)
    if current <= 0.0:
        return list(values)
    factor = target / current
    return [value * factor for value in values]


def _speech_proxy(name: str, spec: Dict[str, Any]) -> List[float]:
    if spec.get("silent"):
        return [0.0] * SAMPLES
    stream = rng(_seed_for(name))
    phase = 0.0
    out: List[float] = []
    harmonics = 8
    for index in range(SAMPLES):
        position = index / SAMPLES
        frequency = spec["f0_hz"] * (1.0 + spec["glide"] * (position - 0.5))
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE
        envelope = 0.55 + 0.45 * math.sin(
            2.0 * math.pi * spec["syllabic_hz"] * position - math.pi / 2.0)
        voiced = math.fsum((1.0 / (harmonic ** 1.15)) * math.sin(harmonic * phase)
                           for harmonic in range(1, harmonics + 1))
        fricative = spec["fricative"] * _gauss(stream) * (
            0.5 + 0.5 * math.sin(2.0 * math.pi * spec["syllabic_hz"] * 3.0 * position))
        out.append(envelope * voiced + fricative)
    return _scale_to_rms(out, spec["rms"])


def _masker_proxy(name: str, spec: Dict[str, Any], target_rms: float) -> List[float]:
    stream = rng(_seed_for(name + ":masker"))
    out: List[float] = []
    if spec["masker"] == "modulated_multitone":
        tones = (220.0, 440.0, 660.0, 880.0, 1320.0, 1760.0)
        for index in range(SAMPLES):
            position = index / SAMPLES
            modulation = 0.6 + 0.4 * math.sin(2.0 * math.pi * 3.7 * position)
            value = math.fsum((1.0 / math.sqrt(rank + 1.0))
                              * math.sin(2.0 * math.pi * tone * position + 0.3 * rank)
                              for rank, tone in enumerate(tones))
            out.append(modulation * value)
    else:
        for _ in range(SAMPLES):
            out.append(_gauss(stream))
    return _scale_to_rms(out, target_rms)


def fixture(name: str) -> Dict[str, Any]:
    """Return a frozen synthetic clean/noisy pair; no media is read."""
    spec = CONDITION_SPECS[name]
    clean = _speech_proxy(name, spec)
    if spec.get("silent"):
        noise_rms = spec["noise_rms"]
        clean_rms = 0.0
    else:
        clean_rms = _rms(clean)
        noise_rms = clean_rms / (10.0 ** (spec["snr_db"] / 20.0))
    masker = _masker_proxy(name, spec, noise_rms)
    noisy = [left + right for left, right in zip(clean, masker)]
    clipped = False
    if spec.get("clip_peak") is not None:
        limit = spec["clip_peak"]
        clipped_values = [max(-limit, min(limit, value)) for value in noisy]
        clipped = any(value != original for value, original in zip(clipped_values, noisy))
        noisy = clipped_values
    return {
        "clean": clean,
        "noisy": noisy,
        "meta": {
            "samples": SAMPLES,
            "sample_rate_hz": SAMPLE_RATE,
            "seed": _seed_for(name),
            "target_snr_db": spec["snr_db"],
            "masker": spec["masker"],
            "input_clipped": clipped,
            "clean_rms": rounded(clean_rms),
            "noisy_rms": rounded(_rms(noisy)),
            "clean_sha256": _float32_digest(clean),
            "noisy_sha256": _float32_digest(noisy),
        },
    }


def _float32_digest(values: Sequence[float]) -> str:
    payload = b"".join(struct.pack("<f", value) for value in values)
    return sha256(payload)


# ---- deterministic DSP -----------------------------------------------------

def _fft(values: Sequence[complex], inverse: bool = False) -> List[complex]:
    size = len(values)
    if size == 0 or size & (size - 1):
        raise ValueError("fft length must be a positive power of two")
    data = list(values)
    reverse = 0
    for index in range(1, size):
        bit = size >> 1
        while reverse & bit:
            reverse ^= bit
            bit >>= 1
        reverse |= bit
        if index < reverse:
            data[index], data[reverse] = data[reverse], data[index]
    step = 2
    while step <= size:
        angle = (2.0 * math.pi / step) * (1.0 if inverse else -1.0)
        root = complex(math.cos(angle), math.sin(angle))
        half = step >> 1
        for start in range(0, size, step):
            twiddle = 1.0 + 0.0j
            for offset in range(half):
                even = data[start + offset]
                odd = data[start + offset + half] * twiddle
                data[start + offset] = even + odd
                data[start + offset + half] = even - odd
                twiddle *= root
        step <<= 1
    if inverse:
        data = [value / size for value in data]
    return data


def _hann(length: int) -> List[float]:
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * index / (length - 1))
            for index in range(length)]


def _frames(samples: Sequence[float]) -> List[List[float]]:
    padded = list(samples)
    remainder = (len(padded) - MASK_FRAME) % MASK_HOP
    if remainder:
        padded.extend([0.0] * (MASK_HOP - remainder))
    if len(padded) < MASK_FRAME:
        padded.extend([0.0] * (MASK_FRAME - len(padded)))
    count = (len(padded) - MASK_FRAME) // MASK_HOP + 1
    return [padded[index * MASK_HOP:index * MASK_HOP + MASK_FRAME] for index in range(count)]


def _stft(samples: Sequence[float]) -> List[List[complex]]:
    window = _hann(MASK_FRAME)
    return [_fft([value * weight for value, weight in zip(frame, window)])
            for frame in _frames(samples)]


def _istft(spectra: Sequence[Sequence[complex]], length: int) -> List[float]:
    window = _hann(MASK_FRAME)
    bins = MASK_FRAME // 2 + 1
    output = [0.0] * (MASK_HOP * (len(spectra) - 1) + MASK_FRAME)
    weights = [0.0] * len(output)
    for index, spectrum in enumerate(spectra):
        full = list(spectrum[:bins])
        for offset in range(bins, MASK_FRAME):
            full.append(full[MASK_FRAME - offset].conjugate())
        frame = _fft(full, inverse=True)
        start = index * MASK_HOP
        for offset in range(MASK_FRAME):
            output[start + offset] += frame[offset].real * window[offset]
            weights[start + offset] += window[offset] * window[offset]
    result = [value / weight if weight > 1e-12 else 0.0
              for value, weight in zip(output, weights)]
    return result[:length]


def _mean_spectrum(magnitudes: Sequence[Sequence[float]]) -> List[float]:
    bins = MASK_FRAME // 2 + 1
    frames = len(magnitudes)
    return [math.fsum(float(row[band]) for row in magnitudes) / frames
            for band in range(bins)]


def _magnitudes(spectra: Sequence[Sequence[complex]]) -> List[List[float]]:
    bins = MASK_FRAME // 2 + 1
    return [[abs(row[band]) for band in range(bins)] for row in spectra]


def _apply_gains(spectra: Sequence[Sequence[complex]],
                 magnitudes: Sequence[Sequence[float]],
                 gains: Sequence[Sequence[float]]) -> List[List[complex]]:
    bins = MASK_FRAME // 2 + 1
    out: List[List[complex]] = []
    for row, magnitude, gain in zip(spectra, magnitudes, gains):
        masked = []
        for band in range(bins):
            factor = gain[band]
            masked.append(row[band] * factor if magnitude[band] > 0.0 else 0.0 + 0.0j)
        out.append(masked)
    return out


def _smooth(gains: Sequence[Sequence[float]], width: int) -> List[List[float]]:
    half = width // 2
    smoothed: List[List[float]] = []
    for row in gains:
        frame: List[float] = []
        for index in range(len(row)):
            low = max(0, index - half)
            high = min(len(row), index + half + 1)
            frame.append(math.fsum(row[low:high]) / (high - low))
        smoothed.append(frame)
    return smoothed


def _mask_gains(magnitudes: Sequence[Sequence[float]]) -> List[List[float]]:
    estimate = [MASK_NOISE_FRACTION * value for value in _mean_spectrum(magnitudes)]
    gains: List[List[float]] = []
    for row in magnitudes:
        frame_gains: List[float] = []
        for band, value in enumerate(row):
            ratio = estimate[band] / max(value, 1e-12)
            gain = math.sqrt(max(0.0, 1.0 - ratio * ratio))
            frame_gains.append(min(1.0, max(MASK_GAIN_FLOOR, gain)))
        gains.append(frame_gains)
    return _smooth(gains, MASK_SMOOTHING_BINS)


def _wiener_gains(magnitudes: Sequence[Sequence[float]]) -> List[List[float]]:
    estimate = [MASK_NOISE_FRACTION * value for value in _mean_spectrum(magnitudes)]
    gains: List[List[float]] = []
    for row in magnitudes:
        frame_gains: List[float] = []
        for band, value in enumerate(row):
            ratio = estimate[band] / max(value, 1e-12)
            frame_gains.append(min(1.0, max(WIENER_GAIN_FLOOR, 1.0 - ratio * ratio)))
        gains.append(frame_gains)
    return _smooth(gains, MASK_SMOOTHING_BINS)


def _masked(samples: Sequence[float], kind: str) -> List[float]:
    pad = MASK_FRAME
    padded = [0.0] * pad + list(samples) + [0.0] * pad
    spectra = _stft(padded)
    magnitudes = _magnitudes(spectra)
    if kind == "wiener":
        gains = _wiener_gains(magnitudes)
    else:
        gains = _mask_gains(magnitudes)
    restored = _istft(_apply_gains(spectra, magnitudes, gains), len(padded))
    return restored[pad:pad + len(samples)]


def _peak_normalize(samples: Sequence[float]) -> List[float]:
    peak = max((abs(value) for value in samples), default=0.0)
    if peak <= 0.0:
        return list(samples)
    return [value / peak for value in samples]


def _rms_match(samples: Sequence[float], reference: Sequence[float]) -> List[float]:
    target = _rms(reference)
    current = _rms(samples)
    if current <= 0.0 or target <= 0.0:
        return list(samples)
    factor = target / current
    return [value * factor for value in samples]


def apply_variant(variant: str, samples: Sequence[float]) -> List[float]:
    if variant == "identity_noisy":
        return list(samples)
    if variant == "level_only_peak_normalized":
        return _peak_normalize(samples)
    if variant == "mask_only":
        return _masked(samples, "mask")
    if variant == "peak_normalized_mask":
        return _peak_normalize(_masked(samples, "mask"))
    if variant == "peak_normalized_mask_rms_matched":
        return _rms_match(_peak_normalize(_masked(samples, "mask")), samples)
    if variant == "wiener_baseline_surrogate":
        return _masked(samples, "wiener")
    raise ValueError("unknown variant: " + variant)


# ---- metrics ---------------------------------------------------------------

def si_sdr_db(reference: Sequence[float], estimate: Sequence[float]) -> Tuple[Optional[float], Optional[str]]:
    if len(reference) != len(estimate) or not reference:
        return None, "length_mismatch"
    if not all(math.isfinite(value) for value in reference + estimate):
        return None, "nonfinite_input"
    left_mean = math.fsum(reference) / len(reference)
    right_mean = math.fsum(estimate) / len(estimate)
    left = [value - left_mean for value in reference]
    right = [value - right_mean for value in estimate]
    energy = math.fsum(value * value for value in left)
    if energy <= 1e-30:
        return None, "degenerate_reference"
    projection = math.fsum(a * b for a, b in zip(left, right)) / energy
    target = [projection * value for value in left]
    residual = [b - a for a, b in zip(target, right)]
    target_energy = math.fsum(value * value for value in target)
    residual_energy = math.fsum(value * value for value in residual)
    if residual_energy <= 1e-30:
        return None, "identical_or_negligible_error"
    if target_energy <= 1e-30:
        return None, "degenerate_projection"
    return 10.0 * math.log10(target_energy / residual_energy), None


def direct_snr_db(reference: Sequence[float], estimate: Sequence[float]) -> Tuple[Optional[float], Optional[str]]:
    if len(reference) != len(estimate) or not reference:
        return None, "length_mismatch"
    signal_energy = math.fsum(value * value for value in reference)
    error_energy = math.fsum((b - a) ** 2 for a, b in zip(reference, estimate))
    if signal_energy <= 1e-30:
        return None, "degenerate_reference"
    if error_energy <= 1e-30:
        return None, "identical_or_negligible_error"
    return 10.0 * math.log10(signal_energy / error_energy), None


def metrics(reference: Sequence[float], estimate: Sequence[float]) -> Dict[str, Any]:
    si_sdr, si_reason = si_sdr_db(reference, estimate)
    snr, snr_reason = direct_snr_db(reference, estimate)
    stoi_value, stoi_reason = scorer.stoi(reference, estimate, SAMPLE_RATE)
    peak = max((abs(value) for value in estimate), default=0.0)
    return {
        "si_sdr_db": rounded(si_sdr),
        "si_sdr_status": "scored" if si_sdr is not None else si_reason,
        "stoi": rounded(stoi_value),
        "stoi_status": "scored" if stoi_value is not None else stoi_reason,
        "direct_snr_db": rounded(snr),
        "direct_snr_status": "scored" if snr is not None else snr_reason,
        "peak_abs": rounded(peak),
        "at_full_scale": peak >= 1.0 - 1e-12,
        "rms": rounded(_rms(estimate)),
        "finite": all(math.isfinite(value) for value in estimate),
        "clipped": peak > 1.0,
        "samples": len(estimate),
    }


def delta_metrics(candidate: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Optional[float]]:
    def difference(key: str) -> Optional[float]:
        if candidate[key] is None or baseline[key] is None:
            return None
        return rounded(candidate[key] - baseline[key])
    return {
        "si_sdr_db": difference("si_sdr_db"),
        "stoi": difference("stoi"),
        "direct_snr_db": difference("direct_snr_db"),
    }


# ---- caller-supplied-asset boundary --------------------------------------

class ConfigRejected(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class InputRejected(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class AssetUnavailable(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


CONFIG_KEYS = {"variant", "gain_floor", "noise_fraction"}


class ReferenceHarness:
    """Validation-shaped harness for synthetic frames; no asset is loaded."""

    def __init__(self, config: Dict[str, Any]) -> None:
        if not isinstance(config, dict):
            raise ConfigRejected("rejected_type")
        unknown = set(config) - CONFIG_KEYS
        if unknown:
            raise ConfigRejected("rejected_unknown_key")
        missing = CONFIG_KEYS - set(config)
        if missing:
            raise ConfigRejected("rejected_missing_key")
        variant = config["variant"]
        if not isinstance(variant, str):
            raise ConfigRejected("rejected_type")
        if variant not in VARIANTS:
            raise ConfigRejected("rejected_unknown_variant")
        for key in ("gain_floor", "noise_fraction"):
            value = config[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ConfigRejected("rejected_type")
            if not math.isfinite(float(value)):
                raise ConfigRejected("rejected_nonfinite")
        if not 0.0 < float(config["gain_floor"]) <= 1.0:
            raise ConfigRejected("rejected_range")
        if not 0.0 < float(config["noise_fraction"]) <= 2.0:
            raise ConfigRejected("rejected_range")
        self.config = dict(config)
        self.state_token = 0
        self.finished = False
        self.closed = False

    def process(self, samples: Sequence[float], rate: int = SAMPLE_RATE,
                channels: int = 1) -> List[float]:
        if self.closed or self.finished:
            raise InputRejected("rejected_session")
        if rate != SAMPLE_RATE:
            raise InputRejected("rejected_rate")
        if channels != 1:
            raise InputRejected("rejected_channels")
        if not samples:
            raise InputRejected("rejected_geometry")
        if len(samples) > MAX_WHOLE_UTTERANCE_SAMPLES:
            raise InputRejected("rejected_length")
        if not all(math.isfinite(value) for value in samples):
            raise InputRejected("rejected_nonfinite")
        output = apply_variant(self.config["variant"], samples)
        self.state_token += 1
        return output

    def finish(self) -> None:
        self.finished = True

    def close(self) -> None:
        self.closed = True


class CallerAssetReference:
    """Accepts a caller-supplied asset descriptor; never loads or infers bytes."""

    def __init__(self, asset: Dict[str, Any]) -> None:
        self.asset = dict(asset)
        self.loaded = False
        if not self.asset.get("present"):
            raise AssetUnavailable("asset_unavailable")
        if not self.asset.get("declared_identity"):
            raise AssetUnavailable("asset_identity_undeclared")
        if self.asset.get("declared_identity") != self.asset.get("observed_identity"):
            raise AssetUnavailable("asset_digest_mismatch")
        if self.asset.get("load_requested"):
            raise AssetUnavailable("asset_load_not_permitted_in_task")

    def descriptor(self) -> Dict[str, Any]:
        return {
            "checkpoint_name": CHECKPOINT_NAME,
            "checkpoint_sha256": CHECKPOINT_SHA256,
            "checkpoint_bytes": CHECKPOINT_BYTES,
            "model_repo": MODEL_REPO,
            "model_repo_revision": MODEL_REPO_REVISION,
            "loaded": False,
            "executed": False,
            "surrogate_substituted": True,
        }


def asset_boundary_probe() -> Dict[str, Any]:
    cases = {
        "absent": {"present": False},
        "identity_undeclared": {"present": True},
        "digest_mismatch": {"present": True, "declared_identity": "a" * 64,
                            "observed_identity": "b" * 64},
        "load_requested": {"present": True, "declared_identity": CHECKPOINT_SHA256,
                           "observed_identity": CHECKPOINT_SHA256,
                           "load_requested": True},
        "declared_but_unverified": {"present": True, "declared_identity": CHECKPOINT_SHA256,
                                    "observed_identity": CHECKPOINT_SHA256},
    }
    outcomes: Dict[str, Any] = {}
    for name, asset in cases.items():
        try:
            reference = CallerAssetReference(asset)
        except AssetUnavailable as error:
            outcomes[name] = {"status": error.code, "loaded": False, "executed": False}
        else:
            outcomes[name] = {
                "status": "descriptor_accepted_no_bytes_read",
                "loaded": reference.loaded,
                "executed": False,
            }
    return outcomes


# ---- adverse cases ---------------------------------------------------------

def adverse_cases() -> Dict[str, Any]:
    base = {"variant": "peak_normalized_mask", "gain_floor": MASK_GAIN_FLOOR,
            "noise_fraction": MASK_NOISE_FRACTION}
    configs = {
        "unknown_key": {**base, "extra": 1},
        "missing_key": {"variant": "peak_normalized_mask"},
        "wrong_type": {**base, "gain_floor": "0.05"},
        "nonfinite": {**base, "gain_floor": float("nan")},
        "out_of_range": {**base, "gain_floor": 0.0},
        "unknown_variant": {**base, "variant": "metricgan_real_checkpoint"},
        "empty_config": {},
    }
    config_results: Dict[str, Any] = {}
    for name, config in configs.items():
        try:
            ReferenceHarness(config)
        except ConfigRejected as error:
            config_results[name] = {"status": error.code, "controller_created": False}
        else:
            config_results[name] = {"status": "accepted", "controller_created": True}

    harness = ReferenceHarness(base)
    signal = fixture("voiced_steady")["noisy"]

    def attempt(samples: Sequence[float], rate: int = SAMPLE_RATE,
                channels: int = 1) -> str:
        probe = ReferenceHarness(base)
        try:
            probe.process(samples, rate=rate, channels=channels)
        except InputRejected as error:
            if probe.state_token != 0:
                raise RuntimeError("state advanced on rejection")
            return error.code
        return "accepted"

    frame_results = {
        "empty": attempt([]),
        "nonfinite": attempt([0.0, float("inf"), 1.0]),
        "wrong_rate": attempt(signal, rate=8000),
        "stereo": attempt(signal, channels=2),
        "oversize": attempt([0.0] * (MAX_WHOLE_UTTERANCE_SAMPLES + 1)),
        "all_zero": attempt([0.0] * 1024),
        "dsp_state_unchanged": all(
            code.startswith("rejected_")
            for code in (attempt([]), attempt([0.0, float("nan")]),
                         attempt(signal, channels=2))),
    }
    silenced = metrics([0.0] * 1024, harness.process([0.0] * 1024))
    lifecycle_harness = ReferenceHarness(base)
    lifecycle_harness.finish()
    try:
        lifecycle_harness.process(signal)
        finish_status = "accepted"
    except InputRejected as error:
        finish_status = error.code
    closing_harness = ReferenceHarness(base)
    closing_harness.close()
    try:
        closing_harness.process(signal)
        close_status = "accepted"
    except InputRejected as error:
        close_status = error.code
    clipped = fixture("clipped_input")
    clipped_metrics = metrics(clipped["clean"], clipped["noisy"])
    return {
        "config_rejections": config_results,
        "frame_rejections": frame_results,
        "lifecycle": {"finish_then_process": finish_status,
                      "close_then_process": close_status},
        "validity": {
            "silence_metrics": silenced,
            "silence_degenerate": silenced["stoi"] is None,
            "clipped_input_recorded": clipped["meta"]["input_clipped"] is True,
            "clipped_input_peak": clipped_metrics["peak_abs"],
            "invalid_excluded": True,
            "missing_result_not_promoted": True,
            "unknown_never_counted_as_scored": True,
        },
    }


# ---- report ----------------------------------------------------------------

SCORE_KEYS = ("si_sdr_db", "stoi", "direct_snr_db")


def _variant_entry(reference: Sequence[float], samples: Sequence[float],
                   baseline: Dict[str, Any]) -> Dict[str, Any]:
    result = metrics(reference, samples)
    return {
        "status": "measured_synthetic",
        "metrics": result,
        "delta_vs_identity_noisy": delta_metrics(result, baseline),
    }


def build_report() -> Dict[str, Any]:
    conditions: Dict[str, Any] = {}
    regressions: List[Dict[str, Any]] = []
    for name in CONDITIONS:
        frozen = fixture(name)
        clean, noisy = frozen["clean"], frozen["noisy"]
        baseline = metrics(clean, noisy)
        variants: Dict[str, Any] = {}
        for variant in VARIANTS:
            processed = apply_variant(variant, noisy)
            entry = _variant_entry(clean, processed, baseline)
            variants[variant] = entry
            delta = entry["delta_vs_identity_noisy"]
            if name in SCORED_CONDITIONS:
                for metric in ("si_sdr_db", "stoi"):
                    value = delta[metric]
                    if value is not None and value < 0.0:
                        regressions.append({
                            "condition": name,
                            "variant": variant,
                            "metric": metric,
                            "delta": value,
                            "interpretation": (
                                "Synthetic surrogate is worse than the noisy identity control; "
                                "recorded verbatim, not hidden and not a quality claim."),
                        })
        conditions[name] = {
            "status": "measured_synthetic" if name in SCORED_CONDITIONS else "validity_control",
            "fixture": frozen["meta"],
            "input_metrics": baseline,
            "variants": variants,
        }

    representative = fixture("voiced_steady")
    identity_input = metrics(representative["clean"], representative["noisy"])
    wiener_input = metrics(representative["clean"],
                           apply_variant(BASELINE_VARIANT, representative["noisy"]))
    candidate_input = metrics(representative["clean"],
                              apply_variant(CANDIDATE_VARIANT, representative["noisy"]))
    controls = {
        "all_present": True,
        "identity": {"name": "identity_noisy", "status": "measured_synthetic",
                     "exact_passthrough": True, "metrics": identity_input},
        "named_baseline": {"name": "noisy_input_no_processing",
                           "status": "measured_synthetic", "metrics": identity_input},
        "candidate": {"name": CANDIDATE_VARIANT, "status": "surrogate_only",
                      "metrics": candidate_input},
        "classical_reference": {"name": BASELINE_VARIANT, "status": "surrogate_only",
                                "metrics": wiener_input},
    }

    clean_preservation: Dict[str, Any] = {}
    for name in SCORED_CONDITIONS:
        clean = fixture(name)["clean"]
        identity = metrics(clean, clean)
        entries: Dict[str, Any] = {}
        for variant in CLEAN_PRESERVATION_VARIANTS:
            processed = apply_variant(variant, clean)
            result = metrics(clean, processed)
            entries[variant] = {
                "status": "measured_synthetic",
                "metrics": result,
                "delta_vs_clean_identity": delta_metrics(result, identity),
            }
        clean_preservation[name] = {
            "status": "measured_synthetic",
            "identity": {
                "name": "clean_identity",
                "metrics": identity,
                "note": ("Identity has zero error by construction, so finite SI-SDR and "
                         "direct-SNR are undefined here; STOI is 1.0."),
            },
            "variants": entries,
        }

    peak_records: Dict[str, Any] = {}
    for name in CONDITIONS:
        frozen = fixture(name)
        entry: Dict[str, Any] = {}
        for variant in VARIANTS:
            result = metrics(frozen["clean"], apply_variant(variant, frozen["noisy"]))
            entry[variant] = {
                "peak_abs": result["peak_abs"],
                "finite": result["finite"],
                "clipped": result["clipped"],
                "at_full_scale": result["at_full_scale"],
                "samples": result["samples"],
            }
        peak_records[name] = entry
    clipped_count = sum(1 for entry in peak_records.values()
                        for record in entry.values() if record["clipped"])
    nonfinite_count = sum(1 for entry in peak_records.values()
                          for record in entry.values() if not record["finite"])
    full_scale_count = sum(1 for entry in peak_records.values()
                           for record in entry.values() if record["at_full_scale"])

    peak_delta_snr = [
        conditions[name]["variants"][PEAK_ONLY_VARIANT]["delta_vs_identity_noisy"]["direct_snr_db"]
        for name in SCORED_CONDITIONS]
    peak_stoi_change = [
        conditions[name]["variants"][PEAK_ONLY_VARIANT]["delta_vs_identity_noisy"]["stoi"]
        for name in SCORED_CONDITIONS
        if conditions[name]["variants"][PEAK_ONLY_VARIANT]["delta_vs_identity_noisy"]["stoi"] is not None]
    rms_delta_snr = [
        conditions[name]["variants"][RMS_MATCHED_VARIANT]["delta_vs_identity_noisy"]["direct_snr_db"]
        for name in SCORED_CONDITIONS]
    candidate_delta_snr = [
        conditions[name]["variants"][CANDIDATE_VARIANT]["delta_vs_identity_noisy"]["direct_snr_db"]
        for name in SCORED_CONDITIONS]
    si_sdr_change = [
        conditions[name]["variants"][RMS_MATCHED_VARIANT]["metrics"]["si_sdr_db"]
        - conditions[name]["variants"][CANDIDATE_VARIANT]["metrics"]["si_sdr_db"]
        for name in SCORED_CONDITIONS
        if conditions[name]["variants"][RMS_MATCHED_VARIANT]["metrics"]["si_sdr_db"] is not None
        and conditions[name]["variants"][CANDIDATE_VARIANT]["metrics"]["si_sdr_db"] is not None]
    stoi_change = [
        conditions[name]["variants"][RMS_MATCHED_VARIANT]["metrics"]["stoi"]
        - conditions[name]["variants"][CANDIDATE_VARIANT]["metrics"]["stoi"]
        for name in SCORED_CONDITIONS
        if conditions[name]["variants"][RMS_MATCHED_VARIANT]["metrics"]["stoi"] is not None
        and conditions[name]["variants"][CANDIDATE_VARIANT]["metrics"]["stoi"] is not None]

    enhancement_profile = {
        "profile_source": "plan/swarm/VERIFICATION.md#Enhancement",
        "paired_clean_reference": {
            "available": True,
            "kind": "synthetic_generated",
            "real_corpus_used": False,
            "real_clean_reference_used": False,
            "note": "Pairing exists only because both sides are generated by this fixture.",
        },
        "scores": ["paired_si_sdr_db", "paired_stoi", "direct_snr_db"],
        "stoi_scorer": {
            "identity": scorer.SCORER_ID,
            "port_of": "pystoi " + scorer.PYSTOI_VERSION + " non-extended algorithm",
            "algorithm_pins": list(scorer.PYSTOI_ALGORITHM_PINS),
            "crosscheck_status": "inherited_pinned_port_not_recrosschecked_here",
        },
        "controls": ["identity", "named_baseline"],
        "task_matched_baseline": {
            "status": "blocked_external_assets",
            "documented_comparators": ["DeepFilterNet3", "FastEnhancer Small",
                                       "ClearerVoice FRCRN"],
            "reproduced": False,
            "local_surrogate": BASELINE_VARIANT,
            "local_surrogate_is_not_a_baseline_result": True,
            "reopen_condition": (
                "Install the rights-cleared pinned comparators and a permitted matched "
                "cohort, then rerun both sides on the same frozen inputs."),
        },
        "clean_preservation": {
            "status": "measured_synthetic",
            "conditions": list(SCORED_CONDITIONS),
            "variant_set": list(CLEAN_PRESERVATION_VARIANTS),
        },
        "peaks_and_invalid_outputs": {
            "status": "measured_synthetic",
            "peak_records": peak_records,
            "invalid_outputs": nonfinite_count,
            "clipped_outputs": clipped_count,
            "at_full_scale_outputs": full_scale_count,
            "note": (
                "Peak clipping is judged against full scale on synthetic outputs only. "
                "The recorded offline RMS-matched diagnostic can exceed full scale; it is "
                "reported, not hidden, and is not a streaming configuration."),
        },
        "alignment": {
            "declared_content_delay_samples": 0,
            "measured_content_delay_samples": None,
            "measured": False,
            "whole_utterance_same_length": True,
            "status": "synthetic_same_length_only",
            "reopen_condition": (
                "Measure impulse and speech-alignment delay on the exact pinned runtime; "
                "the recorded local run applied no delay compensation."),
        },
        "state_memory_timing": {
            "session_state": "none; whole-utterance single pass",
            "streaming_supported": False,
            "algorithmic_latency_measured": False,
            "memory_measured": False,
            "cpu_time_measured": False,
            "status": "blocked_unmeasured",
            "reopen_condition": (
                "Measure per-call CPU, peak RSS, first-output delay and availability on "
                "the declared target with the exact checkpoint and runtime."),
        },
        "unpaired_predictive_screen": {
            "status": "blocked_not_run",
            "reason": "No real unpaired speech or authorized predictive scorer was used.",
            "reopen_condition": "Run a separately labeled predictive screen on permitted data.",
        },
        "listening": {
            "status": "blocked_not_run",
            "protocol": None,
            "reopen_condition": "Authorized independent listening under a declared protocol.",
        },
        "resource": {
            "measured": False,
            "recorded_provenance_only": {
                "mean_cpu_rtf": 0.00443,
                "peak_child_rss_bytes": 316047360,
                "host": "Darwin 27.2 arm64 Apple M1, CPU-only",
                "status": "recorded_provenance_only_not_reproduced",
            },
        },
        "mechanism_findings": {
            "unit_peak_normalization_pattern": {
                "peak_only_mean_delta_snr_db": rounded(
                    math.fsum(peak_delta_snr) / len(peak_delta_snr)),
                "peak_only_max_abs_delta_stoi": rounded(
                    max((abs(value) for value in peak_stoi_change), default=0.0)),
                "finding": (
                    "SpeechBrain-style unit-peak output normalization alone reproduces the "
                    "recorded pattern of a large negative direct-SNR delta with unchanged "
                    "paired SI-SDR and STOI: the deficit is level, not content."),
            },
            "rms_match_recovers_level_not_content": {
                "candidate_mean_delta_snr_db": rounded(
                    math.fsum(candidate_delta_snr) / len(candidate_delta_snr)),
                "rms_matched_mean_delta_snr_db": rounded(
                    math.fsum(rms_delta_snr) / len(rms_delta_snr)),
                "max_abs_si_sdr_change_db": rounded(
                    max((abs(value) for value in si_sdr_change), default=0.0)),
                "max_abs_stoi_change": rounded(
                    max((abs(value) for value in stoi_change), default=0.0)),
                "finding": (
                    "Matching output RMS to the caller input changes level only; paired "
                    "SI-SDR and STOI are unchanged, so the content deficit remains. The "
                    "recorded local run reported the same split."),
            },
            "scope": "synthetic mechanism demonstration only; not a quality or parity result",
        },
    }

    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "family": FAMILY,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "claims": dict(CLAIMS),
        "evidence_classes": [
            "synthetic_fixture",
            "boundary_review",
            "caller_supplied_asset_reference",
            "proposal_only",
        ],
        "enhancement_profile": enhancement_profile,
        "conditions": conditions,
        "controls": controls,
        "clean_preservation": clean_preservation,
        "regression_scan": {
            "completed": True,
            "count": len(regressions),
            "records": regressions,
        },
        "adverse": adverse_cases(),
        "caller_asset_boundary": {
            "model": "caller_supplied_asset_reference",
            "asset_identity": {
                "model_repo": MODEL_REPO,
                "model_repo_revision": MODEL_REPO_REVISION,
                "checkpoint_name": CHECKPOINT_NAME,
                "checkpoint_sha256": CHECKPOINT_SHA256,
                "checkpoint_bytes": CHECKPOINT_BYTES,
                "hyperparams_sha256": HYPERPARAMS_SHA256,
                "config_sha256": CONFIG_SHA256,
                "model_card_license": MODEL_CARD_LICENSE,
                "verification": "identity_quoted_from_provenance; bytes_absent_not_verified",
            },
            "runtime_identity": {
                "speechbrain_version": SPEECHBRAIN_VERSION,
                "speechbrain_wheel_sha256": SPEECHBRAIN_WHEEL_SHA256,
                "overlay": RUNTIME_OVERLAY,
                "installed_in_this_worktree": False,
            },
            "corpus_identity": {
                "mirror": CORPUS_MIRROR,
                "revision": CORPUS_REVISION,
                "test_pairs": CORPUS_TEST_PAIRS,
                "test_seconds": CORPUS_TEST_SECONDS,
                "dataset_license": CORPUS_LICENSE,
                "provenance_note": (
                    "Edinburgh DataShare VoiceBank+DEMAND deposit links CC BY 4.0; source "
                    "speech is CSTR VCTK (ODC-By for that deposit). The mirror's file-level "
                    "mapping to the deposit is unverified and no corpus is present here."),
                "download_attempted": False,
            },
            "probe": asset_boundary_probe(),
            "loaded": False,
            "executed": False,
            "surrogate_substituted": True,
        },
        "readiness": {
            "caller_supplied_asset_reference": True,
            "installed_adapter_added": False,
            "external_blockers": [
                {
                    "id": "checkpoint_assets_absent",
                    "requirement": "Exact checkpoint, hyperparams and config bytes available "
                                   "under approved terms, verified by SHA-256.",
                    "observation": (
                        f"{CHECKPOINT_NAME} ({CHECKPOINT_BYTES} bytes, SHA-256 "
                        f"{CHECKPOINT_SHA256}) is not present in this SDK worktree and no "
                        "download is permitted in this task."),
                    "reopen_condition": (
                        "Provide the exact bytes in approved storage with artifact-specific "
                        "redistribution approval and a verified digest match."),
                },
                {
                    "id": "pinned_runtime_absent",
                    "requirement": "Pinned SpeechBrain runtime installed under an approved "
                                   "isolated environment.",
                    "observation": (
                        f"SpeechBrain {SPEECHBRAIN_VERSION} (wheel SHA-256 "
                        f"{SPEECHBRAIN_WHEEL_SHA256}) with overlay {RUNTIME_OVERLAY} is not "
                        "installed in this worktree; no wheel was downloaded or installed."),
                    "reopen_condition": (
                        "Install the pinned runtime from approved artifacts, record the exact "
                        "environment and rerun the frozen protocol."),
                },
                {
                    "id": "corpus_provenance_uncleared",
                    "requirement": "Rights-cleared, file-level provenance-mapped VoiceBank+DEMAND "
                                   "test split.",
                    "observation": (
                        f"Corpus {CORPUS_MIRROR}@{CORPUS_REVISION} lists {CORPUS_LICENSE} for "
                        f"{CORPUS_TEST_PAIRS} pairs / {CORPUS_TEST_SECONDS} h; the Edinburgh "
                        "deposit license and CSTR VCTK ODC-By source terms are recorded, but "
                        "mirror file-level mapping and every redistribution question remain "
                        "unverified. No corpus is present and none was downloaded."),
                    "reopen_condition": (
                        "Map each test file to the licensed deposit, record attribution and "
                        "obtain written clearance for the intended evaluation and storage."),
                },
                {
                    "id": "recorded_quality_result_negative",
                    "requirement": "Candidate improves or preserves paired quality against the "
                                   "noisy identity control and a task-matched baseline.",
                    "observation": (
                        "The pinned local DNS2020 screen recorded mean ΔSNR −10.505 dB, "
                        "ΔSI-SDR −3.538 dB and ΔSTOI −0.00850 versus noisy identity, below all "
                        "three project comparators. Those values are provenance only and were "
                        "not reproduced here."),
                    "reopen_condition": (
                        "Produce new rights-cleared matched-cohort evidence that clears the "
                        "enhancement gates; the recorded result does not justify a default."),
                },
                {
                    "id": "installed_adapter_not_implemented",
                    "requirement": "Opt-in SDK adapter with validated caller-asset loading, "
                                   "alignment, state and failure policy.",
                    "observation": (
                        "No provider, descriptor, registry entry, shared build or installed-v0 "
                        "change exists; only this task-local synthetic harness was written."),
                    "reopen_condition": (
                        "After assets, runtime and corpus clear, implement an opt-in adapter "
                        "through provider intake with independent review."),
                },
            ],
            "asset_availability": {
                "checkpoint_bytes_present": False,
                "runtime_installed": False,
                "corpus_present": False,
                "download_attempted": False,
                "license_sidecars_present": True,
            },
            "reopen_condition_summary": (
                "Reopen only when the exact checkpoint/config/runtime bytes, the "
                "file-level-cleared VoiceBank+DEMAND test split and a new matched-cohort "
                "result all arrive together, followed by independent review and explicit "
                "default authorization."),
            "qualifies": False,
            "missing_result_promoted": False,
        },
        "historical_provenance": {
            "status": "recorded_provenance_only_not_reproduced_never_pooled",
            "recorded_dns_pilot": {
                "protocol": "CLN-01-exploratory DNS2020 no-reverb subset, 30 paired files, "
                            "300 seconds",
                "valid_pairs": 30,
                "mean_delta_snr_db": -10.505,
                "mean_delta_si_sdr_db": -3.538,
                "mean_delta_stoi": -0.00850,
                "rms_matched_mean_delta_snr_db": -3.387,
                "clean_input_mean_stoi": 0.9819,
                "clean_input_mean_delta_stoi": -0.01807,
                "mean_cpu_rtf": 0.00443,
                "peak_child_rss_bytes": 316047360,
                "status": "recorded_provenance_only",
            },
            "upstream_model_card_claim": {
                "voicebank_test_pesq": 3.15,
                "voicebank_test_stoi_percent": 93.0,
                "status": "source_reported_not_local_and_not_reproduced",
            },
            "candidate_matrix_row_status": "evaluated",
            "candidate_matrix_row_summary": (
                "MetricGAN+ SpeechBrain VoiceBank: 30 paired DNS2020 outputs plus clean "
                "diagnostics; significantly below DeepFilterNet3, FastEnhancer Small and "
                "ClearVoice FRCRN on the same pairs."),
        },
        "gates": [
            {
                "name": "checkpoint_config_rights",
                "status": "blocked",
                "blocked_by": "Exact checkpoint/hyperparams/config bytes are absent; "
                              "artifact-specific approval and digest verification are missing.",
                "reopen_condition": "Approved exact bytes in storage with verified SHA-256.",
            },
            {
                "name": "pinned_runtime",
                "status": "blocked",
                "blocked_by": "No pinned SpeechBrain runtime is installed in this worktree.",
                "reopen_condition": "Approved isolated install of the pinned runtime.",
            },
            {
                "name": "rights_cleared_corpus",
                "status": "blocked",
                "blocked_by": "No file-level-cleared VoiceBank+DEMAND test split is present.",
                "reopen_condition": "Provenance-mapped, attributed and cleared corpus.",
            },
            {
                "name": "matched_cohort_controls",
                "status": "blocked",
                "blocked_by": "No real matched cohort with identity, noisy and comparator "
                              "controls was run.",
                "reopen_condition": "Run the frozen paired protocol on cleared data.",
            },
            {
                "name": "quality_margin",
                "status": "blocked",
                "blocked_by": "The recorded local screen is negative; no qualifying margin "
                              "exists.",
                "reopen_condition": "New evidence clears the enhancement margin gates.",
            },
            {
                "name": "clean_preservation",
                "status": "blocked",
                "blocked_by": "Clean preservation is measured on synthetic signals only.",
                "reopen_condition": "Clean-speech preservation on permitted real speech.",
            },
            {
                "name": "independent_listening",
                "status": "blocked",
                "blocked_by": "No independent listening protocol or result was produced.",
                "reopen_condition": "Authorized independent listening result.",
            },
            {
                "name": "alignment_state_timing",
                "status": "blocked",
                "blocked_by": "Content delay, state, memory and availability were not measured "
                              "on the exact runtime.",
                "reopen_condition": "Measured alignment and timing on the declared target.",
            },
            {
                "name": "provider_intake",
                "status": "blocked",
                "blocked_by": "No provider intake, descriptor or catalog review was completed.",
                "reopen_condition": "Provider intake with independent review.",
            },
            {
                "name": "public_default_selection",
                "status": "blocked",
                "blocked_by": "No explicit default selection was authorized.",
                "reopen_condition": "Explicit written default authorization.",
            },
            {
                "name": "exact_reference_parity",
                "status": "blocked",
                "blocked_by": "No exact approved reference parity was established.",
                "reopen_condition": "Independent parity run against the approved reference.",
            },
        ],
        "missing_evidence": [
            "exact approved checkpoint/hyperparams/config bytes and terms",
            "pinned SpeechBrain runtime installed under approval",
            "file-level-cleared and provenance-mapped VoiceBank+DEMAND test split",
            "real matched cohort with identity, noisy and comparator controls",
            "non-negative quality margin on the intended workload",
            "real clean-speech preservation and invalid-output audit",
            "independent listening result",
            "measured content delay, state, memory and availability on the target",
            "provider intake, descriptor and catalog review",
            "explicit public default selection",
            "exact approved external reference parity",
        ],
        "no_missing_result_qualifies_candidate": True,
        "extra": {
            "live_default": False,
            "task_board_handoff_written": False,
            "reviewer": REVIEWER,
            "handoff_to": "SDK provider intake only after assets, corpus and evidence clear",
            "deliverable": (
                "Caller-supplied-asset reference boundary plus deterministic synthetic "
                "surrogate, strict readiness conclusion and exact external blocker."),
            "surrogate_scope": (
                "Whole-utterance bounded spectral mask with SpeechBrain-style unit-peak "
                "resynthesis normalization; mechanism demonstration only."),
        },
        "source_pin_paths": list(SOURCE_PIN_PATHS),
        "local_file_names": list(LOCAL_FILES),
    }
