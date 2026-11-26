# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local evidence for the noise-aware shaping plus DRC research-control lane.

The pinned research note ``research/listening_intelligibility_20261028.md``
records a small *offline* near-end listening enhancement screen with a
noise-aware water-filling approximation and a smoothed full-band compressor.
That note explicitly says the shaping is an approximation of OptFractASII with
broad FFT bands and an approximate importance vector, that the compressor is a
small research baseline, that only 12 EARS utterances and three GPLv3
VADToolkit maskers were used, and that no listener study exists.  The module
``src/audioml_eval/nele.py`` behind it is whole-file, numpy/scipy based and
non-causal.

This package therefore emits an explicit ``DEFER`` / ``incomplete`` /
``not_qualified`` blocker package.  It runs a deterministic, stdlib-only,
causal receiver-side *local approximation* (a bounded importance-weighted
noise-aware band shaper followed by a smoothed full-band DRC and a peak guard)
so that the installed v0 grid, finite output, zero content delay, bounded
energy equalization, state reset, strict JSON and adverse/missing/invalid/
nonfinite rejection can be checked mechanically.  The local approximation is
not the research candidate, not OptFractASII, has no official algorithm, no
model, no runtime and no real audio, and no observation from it may qualify the
candidate.

Nothing here imports the research module, numpy or scipy, downloads or copies a
corpus, executes a runtime, registers a provider, changes installed v0, a
descriptor, a registry, a default, a shared build or CI, or makes a listening,
device-timing, benchmark or release claim.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]

TASK = "SDK-NOISE-AWARE-SHAPING-PLUS-DRC"
TITLE = "Noise-aware shaping plus DRC"
SLUG = "noise-aware-shaping-plus-drc"
COMPONENT = "noise-aware-shaping-plus-drc"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "feb342c735740f32d64a668cf2234e488cdcdbfe"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-NOISE-AWARE-SHAPING-PLUS-DRC"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-NOISE-AWARE-SHAPING-PLUS-DRC"
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "dsp"
STATUS = "proposal_only_blocked_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "receiver_side_adapter_and_listener_admission"

RESEARCH_NOTE_LOCATOR = (
    "research/listening_intelligibility_20261028.md")
PUBLISHED_METHOD_LOCATOR = (
    "https://www.isca-archive.org/interspeech_2025/villani25_interspeech.html")
PUBLISHED_METHOD_DESIGNATION = (
    "OptFractASII: noise-dependent spectral redistribution with DRC")
# The local record establishes none of the values below.  They remain null.
UPSTREAM_COMMIT: str | None = None
UPSTREAM_VERSION: str | None = None
UPSTREAM_LICENSE: str | None = None
UPSTREAM_LICENSE_STATUS = "not_established"
UPSTREAM_PARAMETERS: str | None = None
UPSTREAM_PARAMETERS_STATUS = "not_recorded"
UPSTREAM_REFERENCE_OUTPUT: str | None = None
UPSTREAM_REFERENCE_OUTPUT_STATUS = "not_recorded"
UPSTREAM_RUNTIME: str | None = None
UPSTREAM_RUNTIME_STATUS = "not_recorded"
UPSTREAM_GEOMETRY_STATUS = "unverified"
UPSTREAM_RESEARCH_MODULE_PRESENT = True
UPSTREAM_RESEARCH_MODULE_STATUS = "offline_non_causal_prototype_not_sdk_reference"

SOURCE_PATH = "data/sources/noise-aware-shaping-plus-drc"
LICENSE_PATH = "data/licenses/noise-aware-shaping-plus-drc"
RUNTIME_ENV_PATH = "data/envs/noise-aware-shaping-plus-drc"
REFERENCE_OUTPUT_PATH = "data/reference/noise-aware-shaping-plus-drc"
CONFIGURATION_PATH = "data/config/noise-aware-shaping-plus-drc"
MASKER_COHORT_PATH = "data/cohorts/noise-aware-shaping-plus-drc"
LISTENER_OUTCOMES_PATH = "data/listening/noise-aware-shaping-plus-drc"

LISTENING_RESEARCH_PATH = "research/listening_intelligibility_20261028.md"
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
SDK_PLAN_PATH = "audio-benchmark-platform/plan/audio-sdk/README.md"

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-EVIDENCE",
    ],
    "id": TASK,
    "mode": "research-control",
    "repository": "audio-sdk",
    "title": TITLE,
}
BOARD_ROW_STABLE_SHA256 = (
    "d984ba1090f229f0001c9adc7e9bd983500657c7df127aa013f700b7ba6560d6")

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
TOTAL_FRAMES = 400
TOTAL_SAMPLES = TOTAL_FRAMES * FRAME_SAMPLES
CONTENT_DELAY_SAMPLES = 0
PEAK_CEILING = 0.95
BAND_EDGES_HZ = (100, 250, 500, 1000, 2000, 4000)
BAND_IMPORTANCE = (0.02, 0.04, 0.08, 0.16, 0.28, 0.27, 0.15)
FIXED_TILT_DB = (-4.0, -3.0, -1.5, 0.0, 1.5, 3.0, 4.0)
SHAPING_STRENGTH_DB = 6.0
SHAPING_LIMIT_DB = 6.0
EQ_LIMIT_DB = 12.0
ATTACK_MS = 5.0
RELEASE_MS = 120.0
THRESHOLD_DBFS = -24.0
RATIO = 3.0
MAX_GAIN_DB = 12.0
MIN_GAIN_DB = -24.0
STATIC_GAIN_DB = 6.0

SINE64: Tuple[int, ...] = (
    0, 3212, 6393, 9512, 12539, 15446, 18204, 20787,
    23170, 25329, 27245, 28898, 30273, 31356, 32137, 32609,
    32767, 32609, 32137, 31356, 30273, 28898, 27245, 25329,
    23170, 20787, 18204, 15446, 12539, 9512, 6393, 3212,
    0, -3212, -6393, -9512, -12539, -15446, -18204, -20787,
    -23170, -25329, -27245, -28898, -30273, -31356, -32137, -32609,
    -32767, -32609, -32137, -31356, -30273, -28898, -27245, -25329,
    -23170, -20787, -18204, -15446, -12539, -9512, -6393, -3212,
)

SEGMENT_FRAMES = 50
SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "silence-head", "start_frame": 0, "end_frame": 50,
     "kind": "silence"},
    {"id": "quiet-speech", "start_frame": 50, "end_frame": 100,
     "kind": "speech", "steps": (1, 2, 3), "amplitude": 800,
     "masker": "low", "masker_level": 0.020},
    {"id": "masked-speech", "start_frame": 100, "end_frame": 150,
     "kind": "speech", "steps": (2, 3, 5), "amplitude": 1600,
     "masker": "low", "masker_level": 0.120},
    {"id": "level-step-up", "start_frame": 150, "end_frame": 200,
     "kind": "speech", "steps": (2, 3, 5), "amplitude": 5000},
    {"id": "speech-clicks", "start_frame": 200, "end_frame": 250,
     "kind": "speech", "steps": (3, 4, 6), "amplitude": 1500,
     "click_period": 2048, "click_amplitude": 12000,
     "masker": "high", "masker_level": 0.050},
    {"id": "sweep", "start_frame": 250, "end_frame": 300,
     "kind": "sweep", "amplitude": 3000,
     "masker": "high", "masker_level": 0.080},
    {"id": "impulse-train", "start_frame": 300, "end_frame": 350,
     "kind": "impulse", "click_period": 1600, "click_amplitude": 20000},
    {"id": "silence-tail", "start_frame": 350, "end_frame": 400,
     "kind": "silence"},
)

VALID_MODES = (
    "identity",
    "static_gain",
    "fixed_tilt",
    "noise_aware_shaping",
    "compressor_only",
    "local_approximation",
)

BAND_ALPHA = tuple(
    math.exp(-2.0 * math.pi * edge / SAMPLE_RATE_HZ)
    for edge in BAND_EDGES_HZ)
BAND_COUNT = len(BAND_ALPHA) + 1
POWER_COEFF = 1.0 - math.exp(-1.0 / (0.020 * SAMPLE_RATE_HZ))
NOISE_FAST_COEFF = 1.0 - math.exp(-1.0 / (0.005 * SAMPLE_RATE_HZ))
NOISE_SLOW_COEFF = 1.0 - math.exp(-1.0 / (2.000 * SAMPLE_RATE_HZ))
SHAPING_COEFF = 1.0 - math.exp(-1.0 / (0.010 * SAMPLE_RATE_HZ))
EQ_COEFF = 1.0 - math.exp(-1.0 / (0.050 * SAMPLE_RATE_HZ))
ATTACK_COEFF = 1.0 - math.exp(-1.0 / (ATTACK_MS * 0.001 * SAMPLE_RATE_HZ))
RELEASE_COEFF = 1.0 - math.exp(-1.0 / (RELEASE_MS * 0.001 * SAMPLE_RATE_HZ))

CONFIG: Dict[str, Any] = {
    "algorithm": "local_surrogate_not_official_nele",
    "attack_ms": ATTACK_MS,
    "bands": list(BAND_EDGES_HZ),
    "channels": CHANNELS,
    "default_enabled": False,
    "energy_equalization": "bounded_causal",
    "epoch": 0,
    "frame_samples": FRAME_SAMPLES,
    "input_format": "float32",
    "masker_source": "oracle_synthetic",
    "mode": "local_approximation",
    "model_used": False,
    "noise_aware": True,
    "output_peak_ceiling": PEAK_CEILING,
    "ratio": RATIO,
    "real_runtime": False,
    "release_ms": RELEASE_MS,
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "session_id": "noise-aware-shaping-plus-drc-local-surrogate",
    "shaping_limit_db": SHAPING_LIMIT_DB,
    "streaming": True,
    "surrogate": True,
    "threshold_dbfs": THRESHOLD_DBFS,
}
REQUIRED_CONFIG_KEYS = set(CONFIG)

REQUIRED_ASSET_FIELDS = {
    "algorithm_id",
    "algorithm_version",
    "algorithmic_latency_samples",
    "channels",
    "configuration_path",
    "configuration_sha256",
    "frame_samples",
    "license_path",
    "license_sha256",
    "listener_outcomes_path",
    "listener_outcomes_sha256",
    "masker_cohort_path",
    "masker_cohort_sha256",
    "output_energy_constraint_db",
    "qualification_authority",
    "reference_output_path",
    "reference_output_sha256",
    "runtime_path",
    "runtime_sha256",
    "sample_rate_hz",
    "source_archive_path",
    "source_archive_sha256",
    "source_commit",
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-qualified-artifact/0.1",
    "official_artifact_admitted_here": False,
    "present_behavior": (
        "validate_hash_geometry_and_artifact_shape_only; never load, import or "
        "execute; official identity and listener rights still require "
        "independent review"),
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "source archive, licence, runtime, configuration, reference output, "
        "masker cohort and listener outcomes are caller-owned absolute paths "
        "that exist",
        "SHA-256 of every hashed artifact matches the manifest",
        "source_commit is a 40-hex revision but is not admitted as official "
        "because no streaming reference revision was established",
        "geometry is 16000 Hz, mono, float32 and 160 samples with nonnegative "
        "latency",
        "algorithm_id is noise-aware-shaping-plus-drc and algorithm_version is "
        "nonempty",
        "output_energy_constraint_db is finite and nonpositive",
        "a hash-matched caller placeholder is never accepted as an official "
        "or listener-qualified artifact",
        "no download, copy, build, import, load or execution occurs here",
    ],
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, indent=2)
    return (text + "\n").encode("utf-8")


def strict_loads(text: str) -> Any:
    def pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise ValueError("non_finite:" + value)

    result = json.loads(text, object_pairs_hook=pairs, parse_constant=reject)
    if not isinstance(result, dict):
        raise ValueError("root_not_object")
    return result


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(item) for item in value)
    return False


def _metric(value: float | None) -> float | None:
    if value is None:
        return None
    if not math.isfinite(value):
        raise ValueError("metric_nonfinite")
    rounded = round(value, 9)
    return 0.0 if rounded == 0.0 else rounded


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(float(value)))


def workspace_root() -> Path:
    override = os.environ.get("SOURCE_ROOT")
    if override:
        return Path(override).resolve()
    for parent in HERE.parents:
        if (parent / "adapters").is_dir() and \
                (parent / "audio-benchmark-platform").is_dir():
            return parent
    raise ValueError("workspace_root_not_found")


def resolve_source_path(name: str) -> Path:
    return workspace_root() / name


def board_row_digest() -> str:
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return sha256(raw)


def _clip16(value: int) -> int:
    if value < -32768:
        return -32768
    if value > 32767:
        return 32767
    return int(value)


def _ramp(index: int, length: int, ramp: int = 80) -> int:
    if length <= 1:
        return ramp
    return max(0, min(index, length - 1 - index, ramp))


def _clean_track() -> List[int]:
    data = [0] * TOTAL_SAMPLES
    for segment in SEGMENTS:
        start = segment["start_frame"] * FRAME_SAMPLES
        end = segment["end_frame"] * FRAME_SAMPLES
        length = end - start
        kind = segment["kind"]
        if kind == "silence":
            continue
        if kind == "impulse":
            period = int(segment["click_period"])
            amplitude = int(segment["click_amplitude"])
            for index in range(0, length, period):
                data[start + index] = _clip16(amplitude)
            continue
        amplitude = int(segment["amplitude"])
        steps = tuple(int(step) for step in segment.get("steps", (1,)))
        phases = [0] * len(steps)
        weights = (8, 4, 2, 1)
        for index in range(length):
            envelope = _ramp(index, length)
            if kind == "sweep":
                step = 2 + (index * 20) // max(1, length)
                value = (SINE64[index * step % 64] * amplitude) // 32767
            else:
                total = 0
                for position, step in enumerate(steps):
                    phases[position] = (phases[position] + step) % 64
                    total += (SINE64[phases[position]] * amplitude *
                              weights[position]) // (32767 * 15)
                value = total
            value = (value * envelope) // max(1, 80)
            click_period = segment.get("click_period")
            if click_period and index % int(click_period) == 0:
                value += int(segment["click_amplitude"])
            data[start + index] = _clip16(data[start + index] + value)
    return data


def _lcg_samples(count: int, seed: int) -> List[float]:
    state = seed & 0x7FFFFFFF
    values: List[float] = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append(((state >> 8) & 0xFFFF) / 32768.0 - 1.0)
    return values


def _tilted_noise(kind: str, count: int, seed: int) -> List[float]:
    white = _lcg_samples(count, seed)
    if kind == "low":
        alpha = math.exp(-2.0 * math.pi * 250.0 / SAMPLE_RATE_HZ)
        state = 0.0
        result = []
        for value in white:
            state = alpha * state + (1.0 - alpha) * value
            result.append(state)
        return result
    if kind == "high":
        alpha = math.exp(-2.0 * math.pi * 3000.0 / SAMPLE_RATE_HZ)
        state = 0.0
        result = []
        for value in white:
            state = alpha * state + (1.0 - alpha) * value
            result.append(value - state)
        return result
    raise ValueError("unknown_masker_kind")


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / len(values))


def _masker_track() -> List[int]:
    data = [0] * TOTAL_SAMPLES
    for position, segment in enumerate(SEGMENTS):
        kind = segment.get("masker")
        if not kind:
            continue
        start = segment["start_frame"] * FRAME_SAMPLES
        end = segment["end_frame"] * FRAME_SAMPLES
        length = end - start
        raw = _tilted_noise(kind, length, 0x13579BDF + 7919 * position)
        level = float(segment["masker_level"])
        current = _rms(raw)
        scale = level / max(current, 1.0e-12)
        for index, value in enumerate(raw):
            data[start + index] = _clip16(int(round(value * scale * 32768.0)))
    return data


def build_fixture() -> Dict[str, Any]:
    clean = _clean_track()
    masker = _masker_track()
    mixed = [_clip16(clean[index] + masker[index])
             for index in range(TOTAL_SAMPLES)]
    return {"clean": clean, "masker": masker, "mix": mixed}


FIXTURE_COMPONENTS = build_fixture()


def as_float(values: Sequence[int]) -> List[float]:
    return [value / 32768.0 for value in values]


def component_digests(components: Dict[str, Any]) -> Dict[str, str]:
    return {
        name: sha256(b"".join(
            (int(value) & 0xFFFF).to_bytes(2, "little")
            for value in values))
        for name, values in components.items()
    }


FIXTURE_DIGESTS = component_digests(FIXTURE_COMPONENTS)


def fixture_spec() -> Dict[str, Any]:
    return {
        "bands_hz": list(BAND_EDGES_HZ),
        "channels": CHANNELS,
        "components": ["clean", "masker", "mix"],
        "frame_samples": FRAME_SAMPLES,
        "generator": (
            "fixed 64-entry integer sine table, integer phases, integer "
            "amplitude envelopes, a 31-bit LCG and one-pole low/high masker "
            "tilts; int16 quantised"),
        "masker_note": (
            "The masker is an oracle listener-side synthetic track, not an "
            "estimated or deployed noise estimate."),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "segments": [dict(segment) for segment in SEGMENTS],
        "total_frames": TOTAL_FRAMES,
        "total_samples": TOTAL_SAMPLES,
    }


FIXTURE_SPEC_DIGEST = sha256(canonical_bytes(fixture_spec()))


def _clip_db(value: float) -> float:
    return max(MIN_GAIN_DB, min(MAX_GAIN_DB, value))


def _db_to_lin(value: float) -> float:
    return 10.0 ** (value / 20.0)


def _gain_db(envelope: float) -> float:
    level_db = 20.0 * math.log10(max(envelope, 1.0e-9))
    if level_db <= THRESHOLD_DBFS:
        return 0.0
    return _clip_db((level_db - THRESHOLD_DBFS) * (1.0 / RATIO - 1.0))


def _env_step(envelope: float, value: float) -> float:
    coefficient = ATTACK_COEFF if value > envelope else RELEASE_COEFF
    return envelope + coefficient * (value - envelope)


class _Splitter:
    """Causal first-order subtractive band split; not a gammatone filterbank."""

    def __init__(self) -> None:
        self.state = [0.0] * len(BAND_ALPHA)

    def split(self, sample: float) -> List[float]:
        bands: List[float] = []
        rest = sample
        for index, alpha in enumerate(BAND_ALPHA):
            self.state[index] = alpha * self.state[index] + (1.0 - alpha) * rest
            band = self.state[index]
            bands.append(band)
            rest -= band
        bands.append(rest)
        return bands

    def snapshot(self) -> List[float]:
        return [round(value, 12) for value in self.state]


class _Processor:
    """Deterministic causal local approximation; not the research candidate."""

    def __init__(self, mode: str) -> None:
        if mode not in VALID_MODES:
            raise ValueError("unknown_mode")
        self.mode = mode
        self.signal = _Splitter()
        self.noise = _Splitter()
        self.band_env = [0.0] * BAND_COUNT
        self.noise_env = [0.0] * BAND_COUNT
        self.gain_db = [0.0] * BAND_COUNT
        self.equalizer_db = 0.0
        self.env_in = 0.0
        self.env_out = 0.0
        self.compressor_env = 0.0
        self.clipped = 0

    def _noise_gains(self) -> List[float]:
        total = sum(self.noise_env)
        if total <= 1.0e-15:
            share = [1.0 / BAND_COUNT] * BAND_COUNT
        else:
            share = [value / total for value in self.noise_env]
        weight = [max(0.0, share[index] * BAND_IMPORTANCE[index])
                  for index in range(BAND_COUNT)]
        total_weight = sum(weight)
        if total_weight <= 1.0e-15:
            normalised = [1.0] * BAND_COUNT
        else:
            normalised = [value * BAND_COUNT / total_weight for value in weight]
        return [max(-SHAPING_LIMIT_DB,
                    min(SHAPING_LIMIT_DB,
                        SHAPING_STRENGTH_DB * (value - 1.0)))
                for value in normalised]

    def _guard(self, value: float) -> float:
        if value > PEAK_CEILING:
            self.clipped += 1
            return PEAK_CEILING
        if value < -PEAK_CEILING:
            self.clipped += 1
            return -PEAK_CEILING
        return value

    def process_sample(self, sample: float, masker: float) -> float:
        if self.mode == "identity":
            return sample
        if self.mode == "static_gain":
            return self._guard(sample * _db_to_lin(STATIC_GAIN_DB))
        bands = self.signal.split(sample)
        if self.mode == "compressor_only":
            self.compressor_env = _env_step(self.compressor_env, abs(sample))
            return self._guard(sample * _db_to_lin(
                _gain_db(self.compressor_env)))
        noise_bands = self.noise.split(masker)
        for index in range(BAND_COUNT):
            power = bands[index] * bands[index]
            self.band_env[index] += POWER_COEFF * (
                power - self.band_env[index])
            noise_power = noise_bands[index] * noise_bands[index]
            coefficient = (NOISE_FAST_COEFF if noise_power >
                           self.noise_env[index] else NOISE_SLOW_COEFF)
            self.noise_env[index] += coefficient * (
                noise_power - self.noise_env[index])
        if self.mode == "fixed_tilt":
            target = list(FIXED_TILT_DB)
        else:
            target = self._noise_gains()
        for index in range(BAND_COUNT):
            self.gain_db[index] += SHAPING_COEFF * (
                target[index] - self.gain_db[index])
        shaped = 0.0
        for index in range(BAND_COUNT):
            shaped += bands[index] * _db_to_lin(self.gain_db[index])
        input_power = sample * sample
        output_power = shaped * shaped
        self.env_in += POWER_COEFF * (input_power - self.env_in)
        self.env_out += POWER_COEFF * (output_power - self.env_out)
        if self.env_in > 1.0e-14 and self.env_out > 1.0e-14:
            correction = 10.0 * math.log10(self.env_in / self.env_out)
            correction = max(-EQ_LIMIT_DB, min(EQ_LIMIT_DB, correction))
            self.equalizer_db += EQ_COEFF * (
                correction - self.equalizer_db)
        shaped *= _db_to_lin(self.equalizer_db)
        if self.mode == "local_approximation":
            self.compressor_env = _env_step(self.compressor_env, abs(shaped))
            shaped *= _db_to_lin(_gain_db(self.compressor_env))
        return self._guard(shaped)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "band_env": [round(value, 12) for value in self.band_env],
            "compressor_env": round(self.compressor_env, 12),
            "equalizer_db": round(self.equalizer_db, 12),
            "gain_db": [round(value, 12) for value in self.gain_db],
            "noise_env": [round(value, 12) for value in self.noise_env],
            "noise_splitter": self.noise.snapshot(),
            "signal_splitter": self.signal.snapshot(),
        }


def validate_frame(frame: Any, final: bool = False) -> List[float]:
    if not isinstance(frame, list):
        raise ValueError("frame_not_list")
    count = len(frame)
    if final:
        if count < 1 or count > FRAME_SAMPLES:
            raise ValueError("bad_final_length")
    elif count != FRAME_SAMPLES:
        raise ValueError("bad_frame_length")
    result: List[float] = []
    for sample in frame:
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise ValueError("bad_sample_type")
        value = float(sample)
        if not math.isfinite(value):
            raise ValueError("nonfinite_sample")
        if value < -1.0 or value > 1.0:
            raise ValueError("sample_out_of_range")
        result.append(value)
    return result


def validate_config(config: Any) -> None:
    if not isinstance(config, dict):
        raise ValueError("config_not_object")
    if set(config) != REQUIRED_CONFIG_KEYS:
        raise ValueError("config_key_set")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("sample_rate")
    if config["channels"] != CHANNELS:
        raise ValueError("channels")
    if config["frame_samples"] != FRAME_SAMPLES:
        raise ValueError("frame_samples")
    if config["input_format"] != "float32":
        raise ValueError("input_format")
    if config["algorithm"] != "local_surrogate_not_official_nele":
        raise ValueError("algorithm")
    if config["energy_equalization"] != "bounded_causal":
        raise ValueError("energy_equalization")
    if config["masker_source"] != "oracle_synthetic":
        raise ValueError("masker_source")
    if config["bands"] != list(BAND_EDGES_HZ):
        raise ValueError("bands")
    if config["mode"] not in VALID_MODES:
        raise ValueError("mode")
    if config["noise_aware"] is not True:
        raise ValueError("noise_aware")
    if config["streaming"] is not True:
        raise ValueError("streaming")
    if not _is_number(config["threshold_dbfs"]) or \
            not -60.0 <= float(config["threshold_dbfs"]) <= 0.0:
        raise ValueError("threshold")
    if not _is_number(config["ratio"]) or \
            not 1.0 <= float(config["ratio"]) <= 20.0:
        raise ValueError("ratio")
    if not _is_number(config["attack_ms"]) or \
            not 0.1 <= float(config["attack_ms"]) <= 500.0:
        raise ValueError("attack")
    if not _is_number(config["release_ms"]) or \
            not 1.0 <= float(config["release_ms"]) <= 5000.0:
        raise ValueError("release")
    if not _is_number(config["shaping_limit_db"]) or \
            not 0.0 <= float(config["shaping_limit_db"]) <= 24.0:
        raise ValueError("shaping_limit")
    if not _is_number(config["output_peak_ceiling"]) or \
            not 0.0 < float(config["output_peak_ceiling"]) <= 1.0:
        raise ValueError("ceiling")
    for key in ("default_enabled", "model_used", "real_runtime"):
        if config[key] is not False:
            raise ValueError(key)
    if config["surrogate"] is not True:
        raise ValueError("surrogate")
    session_id = config["session_id"]
    if not isinstance(session_id, str) or not session_id or \
            re.fullmatch(r"[\x21-\x7e]{1,96}", session_id) is None:
        raise ValueError("session_id")
    if not _is_int(config["epoch"]) or config["epoch"] < 0:
        raise ValueError("epoch")


class Session:
    def __init__(self, mode: str = "local_approximation", epoch: int = 0,
                 first_input_sample: int = 0) -> None:
        if mode not in VALID_MODES:
            raise ValueError("unknown_mode")
        if not _is_int(epoch) or epoch < 0:
            raise ValueError("bad_epoch")
        if not _is_int(first_input_sample) or first_input_sample < 0:
            raise ValueError("bad_first_input_sample")
        self.mode = mode
        self.epoch = epoch
        self.next_input_sample = first_input_sample
        self.accepted_samples = 0
        self.rejected_frames = 0
        self.processor = _Processor(mode)
        self.final = False

    def process(self, frame: Any, final: bool = False,
                masker: Any = None) -> Dict[str, Any]:
        if self.final:
            self.rejected_frames += 1
            raise ValueError("process_after_final")
        try:
            samples = validate_frame(frame, final)
            if masker is None:
                masker_samples = [0.0] * len(samples)
            else:
                masker_samples = validate_frame(masker, final)
                if len(masker_samples) != len(samples):
                    raise ValueError("masker_length")
        except ValueError:
            self.rejected_frames += 1
            raise
        padded = samples + [0.0] * (FRAME_SAMPLES - len(samples))
        masker_padded = masker_samples + [0.0] * (
            FRAME_SAMPLES - len(masker_samples))
        output = [
            self.processor.process_sample(sample, noise)
            for sample, noise in zip(padded, masker_padded)
        ]
        if any(not math.isfinite(value) for value in output):
            raise ValueError("nonfinite_output")
        self.accepted_samples += len(samples)
        self.next_input_sample += len(samples)
        if final:
            self.final = True
        return {
            "epoch": self.epoch,
            "flags": 2 if final else 0,
            "output": output,
            "produced_count": FRAME_SAMPLES,
            "source_first_sample": self.next_input_sample - FRAME_SAMPLES,
            "valid_count": len(samples),
        }

    def reset(self, epoch: int, first_input_sample: int) -> None:
        if not _is_int(epoch) or epoch <= self.epoch:
            raise ValueError("epoch_not_increasing")
        if not _is_int(first_input_sample) or first_input_sample < 0:
            raise ValueError("bad_first_input_sample")
        self.epoch = epoch
        self.next_input_sample = first_input_sample
        self.accepted_samples = 0
        self.rejected_frames = 0
        self.processor = _Processor(self.mode)
        self.final = False

    def state_digest(self) -> str:
        payload = {
            "accepted_samples": self.accepted_samples,
            "epoch": self.epoch,
            "final": self.final,
            "mode": self.mode,
            "next_input_sample": self.next_input_sample,
            "processor": self.processor.snapshot(),
        }
        return sha256(canonical_bytes(payload))


def run_samples(samples: Sequence[float], mode: str = "local_approximation",
                masker: Sequence[float] | None = None,
                chunk: int = FRAME_SAMPLES) -> List[float]:
    session = Session(mode)
    noise = list(masker) if masker is not None else [0.0] * len(samples)
    if len(noise) != len(samples):
        raise ValueError("masker_length")
    output: List[float] = []
    index = 0
    while index < len(samples):
        take = min(chunk, len(samples) - index)
        final = index + take == len(samples) and take < FRAME_SAMPLES
        result = session.process(list(samples[index:index + take]),
                                 final=final,
                                 masker=list(noise[index:index + take]))
        output.extend(result["output"][:result["valid_count"]])
        index += take
    return output


def run_chunked(samples: Sequence[float], sizes: Sequence[int],
                mode: str = "local_approximation",
                masker: Sequence[float] | None = None) -> List[float]:
    session = Session(mode)
    noise = list(masker) if masker is not None else [0.0] * len(samples)
    if len(noise) != len(samples):
        raise ValueError("masker_length")
    output: List[float] = []
    buffer: List[float] = []
    noise_buffer: List[float] = []
    index = 0
    for size in sizes:
        if index >= len(samples):
            break
        buffer.extend(samples[index:index + size])
        noise_buffer.extend(noise[index:index + size])
        index += min(size, len(samples) - index)
        while len(buffer) >= FRAME_SAMPLES:
            result = session.process(buffer[:FRAME_SAMPLES],
                                     masker=noise_buffer[:FRAME_SAMPLES])
            buffer = buffer[FRAME_SAMPLES:]
            noise_buffer = noise_buffer[FRAME_SAMPLES:]
            output.extend(result["output"][:result["valid_count"]])
    if index < len(samples):
        buffer.extend(samples[index:])
        noise_buffer.extend(noise[index:])
    while len(buffer) >= FRAME_SAMPLES:
        result = session.process(buffer[:FRAME_SAMPLES],
                                 masker=noise_buffer[:FRAME_SAMPLES])
        buffer = buffer[FRAME_SAMPLES:]
        noise_buffer = noise_buffer[FRAME_SAMPLES:]
        output.extend(result["output"][:result["valid_count"]])
    if buffer:
        result = session.process(buffer, final=True, masker=noise_buffer)
        output.extend(result["output"][:result["valid_count"]])
    return output


def _rms_db(samples: Sequence[float]) -> float:
    return 20.0 * math.log10(max(_rms(samples), 1.0e-12))


def tone_samples(frequency_hz: int, level_dbfs: float,
                 seconds: float = 0.25) -> List[float]:
    step = frequency_hz * 64 // SAMPLE_RATE_HZ
    if step < 1 or step > 32:
        raise ValueError("tone_frequency")
    amplitude = int(round(32767 * (10.0 ** (level_dbfs / 20.0))))
    count = int(SAMPLE_RATE_HZ * seconds)
    return [SINE64[index * step % 64] * amplitude / 32767.0 / 32768.0
            for index in range(count)]


def masker_samples(kind: str, level_dbfs: float,
                   seconds: float = 0.5) -> List[float]:
    count = int(SAMPLE_RATE_HZ * seconds)
    raw = _tilted_noise(kind, count, 0x2468ACE1)
    level = 10.0 ** (level_dbfs / 20.0)
    scale = level / max(_rms(raw), 1.0e-12)
    return [value * scale for value in raw]


def measure_tone_gain(mode: str, frequency_hz: int, level_dbfs: float,
                      masker: Sequence[float] | None = None) -> float:
    source = tone_samples(frequency_hz, level_dbfs, 0.5)
    noise = list(masker) if masker is not None else None
    output = run_samples(source, mode, noise)
    start = len(source) // 2
    gain = 20.0 * math.log10(max(_rms(output[start:]), 1.0e-12) /
                             max(_rms(source[start:]), 1.0e-12))
    return _metric(gain) or 0.0


def _band_powers(samples: Sequence[float], start: int) -> List[float]:
    splitter = _Splitter()
    sums = [0.0] * BAND_COUNT
    for index in range(start, len(samples)):
        bands = splitter.split(samples[index])
        for band in range(BAND_COUNT):
            sums[band] += bands[band] * bands[band]
    return sums


def multitone_probe() -> List[float]:
    source = [0.0] * int(SAMPLE_RATE_HZ * 0.5)
    for frequency in (250, 500, 1000, 2000, 4000, 6000):
        tone = tone_samples(frequency, -30.0, 0.5)
        for index, value in enumerate(tone):
            source[index] += value
    return source


def band_response(mode: str) -> Dict[str, Any]:
    source = multitone_probe()
    output = run_samples(source, mode)
    start = len(source) // 2
    input_power = _band_powers(source, start)
    output_power = _band_powers(output, start)
    response = {}
    for band in range(BAND_COUNT):
        ratio = 10.0 * math.log10(
            max(output_power[band], 1.0e-18) /
            max(input_power[band], 1.0e-18))
        response[str(band)] = _metric(ratio)
    return {
        "band_gain_db": response,
        "probe": "six equal tones at 250/500/1000/2000/4000/6000 Hz, "
                 "-30 dBFS each",
    }


def masker_response_control() -> Dict[str, Any]:
    low = masker_samples("low", -20.0, 0.5)
    high = masker_samples("high", -20.0, 0.5)
    result: Dict[str, Any] = {}
    for name, masker in (("low_masker", low), ("high_masker", high)):
        session = Session("noise_aware_shaping")
        index = 0
        while index < len(masker):
            frame = list(masker[index:index + FRAME_SAMPLES])
            session.process(frame, masker=frame)
            index += FRAME_SAMPLES
        result[name] = {
            "band_gain_db": [
                round(value, 9) for value in session.processor.gain_db],
            "equalizer_db": round(session.processor.equalizer_db, 9),
        }
    low_bands = result["low_masker"]["band_gain_db"]
    high_bands = result["high_masker"]["band_gain_db"]
    adapts = low_bands[1] > high_bands[1] and low_bands[6] < high_bands[6]
    return {
        "adapts_to_masker_band": adapts,
        "bands_hz": list(BAND_EDGES_HZ),
        "low_minus_high_band_1_db": round(low_bands[1] - high_bands[1], 9),
        "low_minus_high_band_6_db": round(low_bands[6] - high_bands[6], 9),
        "masker_level_dbfs": -20.0,
        "response": result,
    }


def level_transfer(mode: str) -> Dict[str, Any]:
    levels = [-30.0, -24.0, -18.0, -12.0, -6.0]
    gains = [measure_tone_gain(mode, 1000, level) for level in levels]
    output_levels = [level + gain for level, gain in zip(levels, gains)]
    mean_x = sum(levels) / len(levels)
    mean_y = sum(output_levels) / len(output_levels)
    numerator = sum((x - mean_x) * (y - mean_y)
                    for x, y in zip(levels, output_levels))
    denominator = sum((x - mean_x) ** 2 for x in levels)
    slope = numerator / denominator if denominator else 1.0
    return {
        "gain_db": [_metric(value) for value in gains],
        "input_dbfs": levels,
        "output_dbfs": [_metric(value) for value in output_levels],
        "slope_db_per_db": _metric(slope),
    }


def measure_step(mode: str, rising: bool) -> Dict[str, Any]:
    quiet = tone_samples(1000, -30.0, 0.5)
    loud = tone_samples(1000, -6.0, 0.5)
    source = quiet + loud if rising else loud + quiet
    output = run_samples(source, mode)
    step_index = len(quiet)

    def window_gain_db(start: int) -> float:
        count = 80
        input_window = source[start:start + count]
        output_window = output[start:start + count]
        return 20.0 * math.log10(max(_rms(output_window), 1.0e-12) /
                                 max(_rms(input_window), 1.0e-12))

    before = window_gain_db(max(0, step_index - 400))
    after = window_gain_db(len(source) - 400)
    transition = None
    if abs(after - before) <= 0.01:
        transition = 0.0
    else:
        for start in range(step_index, len(source) - 80, 40):
            if abs(window_gain_db(start) - after) <= 3.0:
                transition = (start + 80 - step_index) * 1000.0 / SAMPLE_RATE_HZ
                break
    return {
        "gain_after_db": _metric(after),
        "gain_before_db": _metric(before),
        "transition_ms": _metric(transition or 0.0),
    }


def _correlation(left: Sequence[float], right: Sequence[float]) -> float:
    count = len(left)
    if count == 0 or count != len(right):
        return 0.0
    mean_left = sum(left) / count
    mean_right = sum(right) / count
    numerator = sum((left[index] - mean_left) * (right[index] - mean_right)
                    for index in range(count))
    left_power = sum((value - mean_left) ** 2 for value in left)
    right_power = sum((value - mean_right) ** 2 for value in right)
    denominator = math.sqrt(left_power * right_power)
    if denominator <= 1.0e-15:
        return 0.0
    return numerator / denominator


def _measure_mode_uncached(mode: str) -> Dict[str, Any]:
    source = as_float(FIXTURE_COMPONENTS["clean"])
    masker = as_float(FIXTURE_COMPONENTS["masker"])
    output = run_samples(source, mode, masker)
    active_start = 50 * FRAME_SAMPLES
    active_end = 350 * FRAME_SAMPLES
    clipped = 0 if mode == "identity" else sum(
        1 for value in output if abs(value) >= PEAK_CEILING - 1.0e-12)
    silence_input = source[:4000]
    silence_output = output[:4000]
    gains = {
        str(frequency): measure_tone_gain(mode, frequency, -24.0)
        for frequency in (250, 500, 1000, 2000, 4000, 6000)
    }
    return {
        "band_response": band_response(mode),
        "clean_preservation_correlation": _metric(
            _correlation(source[active_start:active_end],
                         output[active_start:active_end])),
        "clipped_output_samples": clipped,
        "energy_neutral": abs(_rms_db(output) - _rms_db(source)) <= 1.0,
        "gain_db": _metric(_rms_db(output) - _rms_db(source)),
        "level_transfer": level_transfer(mode),
        "max_abs_output": _metric(max(abs(value) for value in output)),
        "nonfinite_output_samples": sum(
            1 for value in output if not math.isfinite(value)),
        "rms_in_dbfs": _metric(_rms_db(source)),
        "rms_out_dbfs": _metric(_rms_db(output)),
        "silence_exact_zero": all(value == 0.0 for value in silence_input) and
                              all(value == 0.0 for value in silence_output),
        "step_attack": measure_step(mode, True),
        "step_release": measure_step(mode, False),
        "tone_gain_db": gains,
    }


_MEASUREMENT_CACHE: Dict[str, Dict[str, Any]] = {}


def measure_mode(mode: str) -> Dict[str, Any]:
    if mode not in _MEASUREMENT_CACHE:
        _MEASUREMENT_CACHE[mode] = _measure_mode_uncached(mode)
    return _plain(_MEASUREMENT_CACHE[mode])


def impulse_control() -> Dict[str, Any]:
    source = [0.0] * 8000
    source[2000] = 0.25
    output = run_samples(source, "local_approximation")
    peak_index = max(range(len(output)), key=lambda index: abs(output[index]))
    return {
        "declared_delay_samples": CONTENT_DELAY_SAMPLES,
        "expected_output_index": 2000 + CONTENT_DELAY_SAMPLES,
        "observed_peak_index": peak_index,
        "peak_finite": math.isfinite(output[peak_index]),
    }


def silence_control() -> Dict[str, Any]:
    output = run_samples([0.0] * 512, "local_approximation")
    return {
        "exact_zero": all(value == 0.0 for value in output),
        "finite": all(math.isfinite(value) for value in output),
    }


def streaming_parity_control() -> Dict[str, Any]:
    source = as_float(FIXTURE_COMPONENTS["clean"][:4000])
    masker = as_float(FIXTURE_COMPONENTS["masker"][:4000])
    offline = run_samples(source, "local_approximation", masker)
    sizes = [160, 137, 641, 320, 1000, 73, 211, 160]
    streamed = run_chunked(source, sizes, "local_approximation", masker)
    return {
        "all_identical": offline == streamed,
        "chunk_sizes": sizes,
        "sample_count": len(source),
    }


def reset_control() -> Dict[str, Any]:
    source = as_float(FIXTURE_COMPONENTS["clean"][:1600])
    masker = as_float(FIXTURE_COMPONENTS["masker"][:1600])
    session = Session("local_approximation", epoch=0)
    for index in range(0, len(source), FRAME_SAMPLES):
        session.process(source[index:index + FRAME_SAMPLES],
                        masker=masker[index:index + FRAME_SAMPLES])
    session.reset(1, 0)
    reset_output: List[float] = []
    for index in range(0, len(source), FRAME_SAMPLES):
        result = session.process(source[index:index + FRAME_SAMPLES],
                                 masker=masker[index:index + FRAME_SAMPLES])
        reset_output.extend(result["output"])
    fresh = Session("local_approximation", epoch=1)
    fresh_output: List[float] = []
    for index in range(0, len(source), FRAME_SAMPLES):
        result = fresh.process(source[index:index + FRAME_SAMPLES],
                               masker=masker[index:index + FRAME_SAMPLES])
        fresh_output.extend(result["output"])
    epoch_zero_rejected = False
    try:
        session.reset(1, 0)
    except ValueError:
        epoch_zero_rejected = True
    negative_rejected = False
    try:
        fresh.reset(-1, 0)
    except ValueError:
        negative_rejected = True
    return {
        "epoch_zero_rejected": epoch_zero_rejected,
        "fresh_matches_reset": reset_output == fresh_output,
        "higher_epoch_accepted": session.epoch == 1,
        "negative_epoch_rejected": negative_rejected,
    }


def nonfinite_control() -> Dict[str, Any]:
    session = Session("local_approximation")
    masker_frame = [0.0] * FRAME_SAMPLES
    result = session.process([0.0] * FRAME_SAMPLES, masker=masker_frame)
    before_digest = session.state_digest()
    before_counter = session.accepted_samples
    rejected = 0
    for bad in (float("nan"), float("inf"), float("-inf")):
        frame = [0.0] * FRAME_SAMPLES
        frame[17] = bad
        try:
            session.process(frame, masker=masker_frame)
        except ValueError:
            rejected += 1
    for bad in (float("nan"), float("inf")):
        masker = [0.0] * FRAME_SAMPLES
        masker[23] = bad
        try:
            session.process([0.0] * FRAME_SAMPLES, masker=masker)
        except ValueError:
            rejected += 1
    after_digest = session.state_digest()
    after_counter = session.accepted_samples
    return {
        "accepted_counter_unchanged": before_counter == after_counter,
        "counted_as_silence": False,
        "nonfinite_rejected": rejected,
        "state_digest_unchanged": before_digest == after_digest,
        "valid_frame_produced": result["produced_count"] == FRAME_SAMPLES,
    }


def config_adverse_control() -> Dict[str, Any]:
    patches = {
        "algorithm_official": {"algorithm": "optfractasii"},
        "attack_zero": {"attack_ms": 0.0},
        "bands_wrong": {"bands": [100, 250, 500, 1000]},
        "bool_epoch": {"epoch": True},
        "channels_stereo": {"channels": 2},
        "default_enabled": {"default_enabled": True},
        "empty_session": {"session_id": ""},
        "energy_equalization_unbounded": {
            "energy_equalization": "whole_file"},
        "extra_key": {"extra": 1},
        "frame_320": {"frame_samples": 320},
        "input_int16": {"input_format": "int16"},
        "masker_estimated": {"masker_source": "estimated_runtime"},
        "model_used": {"model_used": True},
        "negative_epoch": {"epoch": -1},
        "noise_aware_false": {"noise_aware": False},
        "ratio_inf": {"ratio": float("inf")},
        "ratio_low": {"ratio": 0.5},
        "real_runtime": {"real_runtime": True},
        "release_zero": {"release_ms": 0.0},
        "sample_rate_48k": {"sample_rate_hz": 48000},
        "shaping_negative": {"shaping_limit_db": -1.0},
        "streaming_false": {"streaming": False},
        "surrogate_false": {"surrogate": False},
        "threshold_nan": {"threshold_dbfs": float("nan")},
        "threshold_positive": {"threshold_dbfs": 3.0},
        "unknown_mode": {"mode": "optfractasii"},
    }
    rejected = 0
    for patch in patches.values():
        config = dict(CONFIG)
        config.update(patch)
        try:
            validate_config(config)
        except ValueError:
            rejected += 1
    validate_config(dict(CONFIG))
    return {
        "accepted_baseline": True,
        "case_count": len(patches),
        "rejected_all": rejected == len(patches),
    }


def frame_adverse_control() -> Dict[str, Any]:
    cases = {
        "bool_sample": [True] * FRAME_SAMPLES,
        "empty": [],
        "empty_final": ("empty", True),
        "final_zero_length": ("zero", True),
        "infinity": [0.0] * 17 + [float("inf")] + [0.0] * 142,
        "long_final": [0.0] * 161,
        "long_nonfinal": [0.0] * 161,
        "nan": [0.0] * 17 + [float("nan")] + [0.0] * 142,
        "negative_infinity": [0.0] * 17 + [float("-inf")] + [0.0] * 142,
        "nested": [0.0] * 17 + [[1.0]] + [0.0] * 142,
        "none": [0.0] * 17 + [None] + [0.0] * 142,
        "out_of_range": [0.0] * 17 + [1.5] + [0.0] * 142,
        "short_nonfinal": [0.0] * 159,
        "string_outer": "[0.0]",
        "string_sample": [0.0] * 17 + ["0.0"] + [0.0] * 142,
        "zero_length": [],
    }
    rejected = 0
    for value in cases.values():
        if isinstance(value, tuple):
            frame, final = value[0], value[1]
        else:
            frame, final = value, False
        try:
            validate_frame(frame, final=final)
        except ValueError:
            rejected += 1
    masker_rejected = 0
    masker_cases = [
        [0.0] * 159,
        [0.0] * 161,
        [0.0] * 17 + [float("nan")] + [0.0] * 142,
        "[0.0]",
    ]
    for masker in masker_cases:
        try:
            validate_frame(masker)
        except ValueError:
            masker_rejected += 1
    length_rejected = 0
    session = Session("local_approximation")
    try:
        session.process([0.0] * FRAME_SAMPLES, masker=[0.0] * 159)
    except ValueError:
        length_rejected += 1
    return {
        "case_count": len(cases) + len(masker_cases) + 1,
        "masker_rejected_all": masker_rejected == len(masker_cases),
        "masker_length_rejected": length_rejected == 1,
        "rejected_all": rejected == len(cases),
    }


def _asset_manifest(root: Path) -> Dict[str, Any]:
    paths = {
        "source_archive_path": root / "source.tar",
        "license_path": root / "LICENSE.txt",
        "runtime_path": root / "runtime.bin",
        "configuration_path": root / "config.json",
        "reference_output_path": root / "output.f32",
        "masker_cohort_path": root / "maskers.bin",
        "listener_outcomes_path": root / "listening.json",
    }
    for name, path in paths.items():
        path.write_bytes(("caller-owned-placeholder:" + name).encode("ascii"))
    manifest: Dict[str, Any] = {
        "algorithm_id": COMPONENT,
        "algorithm_version": "caller-declared-v0",
        "algorithmic_latency_samples": 0,
        "channels": CHANNELS,
        "configuration_path": str(paths["configuration_path"]),
        "configuration_sha256": sha256_file(paths["configuration_path"]),
        "frame_samples": FRAME_SAMPLES,
        "license_path": str(paths["license_path"]),
        "license_sha256": sha256_file(paths["license_path"]),
        "listener_outcomes_path": str(paths["listener_outcomes_path"]),
        "listener_outcomes_sha256": sha256_file(
            paths["listener_outcomes_path"]),
        "masker_cohort_path": str(paths["masker_cohort_path"]),
        "masker_cohort_sha256": sha256_file(paths["masker_cohort_path"]),
        "output_energy_constraint_db": 0.0,
        "qualification_authority": "caller-owned-independent-review",
        "reference_output_path": str(paths["reference_output_path"]),
        "reference_output_sha256": sha256_file(
            paths["reference_output_path"]),
        "runtime_path": str(paths["runtime_path"]),
        "runtime_sha256": sha256_file(paths["runtime_path"]),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "source_archive_path": str(paths["source_archive_path"]),
        "source_archive_sha256": sha256_file(paths["source_archive_path"]),
        "source_commit": "a" * 40,
    }
    return manifest


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest_not_object")
    if set(manifest) != REQUIRED_ASSET_FIELDS:
        raise ValueError("manifest_key_set")
    path_fields = (
        "source_archive_path",
        "license_path",
        "runtime_path",
        "configuration_path",
        "reference_output_path",
        "masker_cohort_path",
        "listener_outcomes_path",
    )
    for field in path_fields:
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise ValueError("bad_path:" + field)
        path = Path(value)
        if not path.is_absolute() or not path.is_file():
            raise ValueError("missing_or_relative_path:" + field)
    for hash_field, path_field in (
            ("source_archive_sha256", "source_archive_path"),
            ("license_sha256", "license_path"),
            ("runtime_sha256", "runtime_path"),
            ("configuration_sha256", "configuration_path"),
            ("reference_output_sha256", "reference_output_path"),
            ("masker_cohort_sha256", "masker_cohort_path"),
            ("listener_outcomes_sha256", "listener_outcomes_path")):
        digest = manifest[hash_field]
        if not isinstance(digest, str) or \
                re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError("bad_hash:" + hash_field)
        if sha256_file(Path(manifest[path_field])) != digest:
            raise ValueError("hash_mismatch:" + hash_field)
    if not isinstance(manifest["source_commit"], str) or \
            re.fullmatch(r"[0-9a-f]{40}", manifest["source_commit"]) is None:
        raise ValueError("bad_commit")
    if manifest["algorithm_id"] != COMPONENT:
        raise ValueError("algorithm_id")
    if not isinstance(manifest["algorithm_version"], str) or \
            not manifest["algorithm_version"]:
        raise ValueError("algorithm_version")
    if not _is_int(manifest["sample_rate_hz"]) or \
            manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ValueError("sample_rate")
    if not _is_int(manifest["channels"]) or manifest["channels"] != CHANNELS:
        raise ValueError("channels")
    if not _is_int(manifest["frame_samples"]) or \
            manifest["frame_samples"] != FRAME_SAMPLES:
        raise ValueError("frame_samples")
    if not _is_int(manifest["algorithmic_latency_samples"]) or \
            not 0 <= manifest["algorithmic_latency_samples"] <= SAMPLE_RATE_HZ:
        raise ValueError("latency")
    if not _is_number(manifest["output_energy_constraint_db"]) or \
            float(manifest["output_energy_constraint_db"]) > 0.0:
        raise ValueError("energy_constraint")
    if not isinstance(manifest["qualification_authority"], str) or \
            not manifest["qualification_authority"]:
        raise ValueError("authority")
    return {
        "executed": False,
        "hashed_here": True,
        "loaded": False,
        "official_identity": False,
        "valid": True,
    }


def pinned_asset_identity(manifest: Any) -> Dict[str, Any]:
    validate_caller_asset(manifest)
    return {
        "admitted": False,
        "reason": "official_and_listener_identity_not_established",
    }


def asset_controls() -> Dict[str, Any]:
    rejected = 0
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        manifest = _asset_manifest(root)
        valid = validate_caller_asset(manifest)
        pinned = pinned_asset_identity(manifest)
        patches: Dict[str, Any] = {
            "absent_maskers": {"masker_cohort_path": str(root / "absent.bin")},
            "absent_source": {"source_archive_path": str(root / "absent.tar")},
            "bad_algorithm": {"algorithm_id": "optfractasii"},
            "bad_hash": {"source_archive_sha256": "0" * 64},
            "bad_listener_hash": {"listener_outcomes_sha256": "0" * 64},
            "bad_version": {"algorithm_version": ""},
            "bool_latency": {"algorithmic_latency_samples": True},
            "energy_positive": {"output_energy_constraint_db": 3.0},
            "extra_field": {"extra": 1},
            "latency_negative": {"algorithmic_latency_samples": -1},
            "missing_field": {"qualification_authority": None},
            "negative_commit": {"source_commit": "g" * 40},
            "relative_path": {"runtime_path": "runtime.bin"},
            "short_commit": {"source_commit": "a" * 39},
            "stereo": {"channels": 2},
            "zero_frame": {"frame_samples": 0},
            "zero_rate": {"sample_rate_hz": 0},
        }
        cases = len(patches)
        for patch in patches.values():
            candidate = dict(manifest)
            candidate.update(patch)
            try:
                validate_caller_asset(candidate)
            except ValueError:
                rejected += 1
    return {
        "case_count": cases,
        "pinned_identity_admitted": pinned["admitted"],
        "rejected_all": rejected == cases,
        "valid_manifest_accepted": valid["valid"] is True,
        "valid_manifest_executed": valid["executed"],
        "valid_manifest_loaded": valid["loaded"],
    }


EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "streaming_reference_and_license_absent",
        "requirement": (
            "Supply an exact licensed real-time receiver-side shaping-plus-DRC "
            "implementation at an immutable revision, with a reviewed licence, "
            "notice bundle and written product, redistribution and "
            "derivative-output terms, verified locally without a network "
            "download."),
        "state": (
            "No licensed streaming implementation exists at "
            "data/sources/noise-aware-shaping-plus-drc or "
            "data/licenses/noise-aware-shaping-plus-drc. The pinned research "
            "note cites a whole-file numpy/scipy prototype "
            "(src/audioml_eval/nele.py) that is explicitly a small research "
            "baseline, is non-causal and is not an SDK reference."),
    },
    {
        "id": "published_algorithm_and_parameters_absent",
        "requirement": (
            "Supply the published algorithm identity, gammatone filterbank or "
            "exact band set, standard importance vector, water-filling level, "
            "shaping limits, DRC thresholds, ratios, attack/release, energy "
            "constraint and configuration digest."),
        "state": (
            "The research note records broad FFT bands and an approximate "
            "SII-style importance vector, and says the method is deliberately "
            "not a faithful OptFractASII reproduction. No exact parameter set, "
            "version or configuration file is recorded or pinned."),
    },
    {
        "id": "runtime_and_reference_output_absent",
        "requirement": (
            "Admit a locked, hash-pinned runtime with exact dependency versions "
            "and approved exact-runtime output vectors for byte-level parity."),
        "state": (
            "No environment exists at data/envs/noise-aware-shaping-plus-drc "
            "and no reference output exists at "
            "data/reference/noise-aware-shaping-plus-drc. The research module "
            "was not imported and no parity run was attempted."),
    },
    {
        "id": "receiver_geometry_energy_and_delay_unverified",
        "requirement": (
            "Pin the deployed sample rate, channels, frame/hop, buffering and "
            "content delay, causal noise estimate, energy/loudness contract and "
            "gain slew, then reproduce them on one declared streaming path."),
        "state": (
            "The research screen restores whole-file target speech RMS, which "
            "is non-causal, and estimates noise from the complete masker file. "
            "No deployed geometry, causal masker estimator, energy constraint "
            "or content-delay measurement exists. This package's 16 kHz mono "
            "float32 160-sample zero-delay oracle-masker harness is a probe-only "
            "local approximation, not the research or deployed geometry."),
    },
    {
        "id": "rights_cleared_masker_and_listener_cohort_absent",
        "requirement": (
            "Supply rights-cleared target speech and an independent "
            "participant-level listener-side masker cohort with consent, "
            "hearing-profile/listening protocol and explicit output-use "
            "permissions."),
        "state": (
            "The research screen used 12 locally staged EARS anechoic "
            "utterances and three GPLv3 VADToolkit masker scenes, reused across "
            "clips and not independent. No release permission, consent, hearing "
            "profile, listening protocol or participant-level cohort exists for "
            "this task."),
    },
    {
        "id": "independent_qualification_absent",
        "requirement": (
            "Score independent intelligibility/quality and listening outcomes, "
            "measure output energy and target-device timing, and complete an "
            "OFF-by-default opt-in provider intake with independent review."),
        "state": (
            "No listener study, hearing profile, word recognition or "
            "listening-effort result exists. STOI/ESTOI are objective "
            "predictors only. No independent energy audit, device timing, "
            "provider intake or release approval exists; surrogate observations "
            "do not qualify the candidate."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_streaming_source_revision_and_license",
     "Immutable licensed real-time shaping-plus-DRC source revision, notice "
     "bundle and clean caller-owned checkout verified locally without a "
     "download."),
    ("published_algorithm_and_parameter_identity",
     "Exact published filterbank, importance vector, water-filling level, "
     "shaping limits, DRC parameters and configuration are pinned and "
     "reproduced."),
    ("pinned_runtime_and_reference_output",
     "Locked runtime with exact dependency versions, install/import digest "
     "and approved exact-runtime output vectors."),
    ("receiver_geometry_energy_and_content_delay",
     "Deployed rate, channels, frame/hop, causal noise estimate, energy "
     "constraint, gain slew and content delay are pinned and reproduced."),
    ("fixed_dsp_and_research_control_separation",
     "Identity, fixed-tilt, shaping-only, DRC-only and shaping-plus-DRC "
     "controls are measured separately with no pooled claim."),
    ("rights_cleared_masker_and_listener_cohort",
     "Rights-cleared target speech, independent listener-side maskers, "
     "consent, hearing profiles and output-use permissions are frozen."),
    ("independent_intelligibility_energy_and_timing",
     "Independent intelligibility and listening outcomes, an output-energy "
     "audit, target-device timing and adverse/missing/nonfinite controls."),
    ("opt_in_provider_intake_and_default_review",
     "OFF-by-default opt-in provider intake, descriptor review, exact-head "
     "review and explicit public default/release approval."),
)

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "listener_outcome_claimed": False,
    "native_engine_built": False,
    "numpy_or_scipy_imported": False,
    "onnxruntime_invoked": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "registered": False,
    "registry_or_default_change": False,
    "research_module_imported": False,
    "runtime_invoked": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "benchmark_run": False,
    "device_timing_measured": False,
    "downloaded": False,
    "implementation_added": False,
    "listening_performed": False,
    "network_used": False,
    "numpy_or_scipy_used": False,
    "provider_registered": False,
    "public_abi_changed": False,
    "real_assets_used": False,
    "registry_or_default_changed": False,
    "release_claim": False,
    "research_module_imported": False,
    "runtime_executed": False,
    "shared_build_or_ci_changed": False,
    "source_imported": False,
    "task_local_only": True,
    "weights_loaded": False,
    "write_scope": TASK_PREFIX + " only",
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No licensed streaming shaping-plus-DRC implementation, published "
    "OptFractASII parameter set, runtime call or reference output was "
    "reproduced or produced.",
    "No intelligibility, quality, listening, timing, benchmark or release "
    "result is claimed.",
    "The historical research screen is quoted as provenance only; it is not "
    "rerun, not independent and not an SDK result.",
    "The local causal six-band oracle-masker approximation is not the research "
    "candidate and not OptFractASII, and it cannot qualify the candidate.",
    "The 16 kHz mono float32 160-sample zero-delay harness is not the "
    "unverified research or deployed geometry.",
    "The oracle synthetic masker is not a deployed noise estimate and no "
    "listener-side masker rights are established.",
    "No real corpus, consenting listener, hearing profile, device clock or "
    "energy-audit qualification was used.",
    "No provider, descriptor, registry, installed v0 path, default, public "
    "ABI, research module, numpy/scipy dependency, shared build or CI was "
    "changed.",
    "A caller-owned hash-matched placeholder is never admitted as an official "
    "or listener-qualified artifact.",
)

SOURCE_PINS: Dict[str, str] = {
    LISTENING_RESEARCH_PATH:
        "f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a",
    INVENTORY_PATH:
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    VERIFICATION_PATH:
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    SDK_PLAN_PATH:
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)
EXPECTED_DIR_FILES = set(LOCAL_FILES) | {"SOURCES.sha256"}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->",
                 "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}

HISTORICAL_RESEARCH_SCREEN: Dict[str, Any] = {
    "candidates": {
        "drc_alone": {"mean_estoi": 0.5752, "mean_stoi": 0.6873},
        "fixed_tilt": {"mean_estoi": 0.5760, "mean_stoi": 0.7006},
        "identity": {"mean_estoi": 0.5719, "mean_stoi": 0.6897},
        "noise_aware_shaping": {"mean_estoi": 0.5627, "mean_stoi": 0.6876},
        "noise_aware_shaping_plus_drc": {
            "mean_estoi": 0.5683, "mean_stoi": 0.6898},
    },
    "conditions": {
        "masker_scenes": ["park", "bus_stop", "construction_site"],
        "masker_license": "GPLv3 VADToolkit scene recordings",
        "pairs_per_method": 108,
        "snr_db": [-5, 0, 5],
        "target_utterances": 12,
        "target_source": "locally staged EARS anechoic subset",
    },
    "is_candidate_result": False,
    "metrics": ["STOI", "ESTOI"],
    "note": (
        "Quoted from the pinned research note for provenance only. The screen "
        "uses objective predictors at equal target speech power, not listener "
        "outcomes; it is not rerun, not reproduced and not an SDK result."),
    "reproduced": False,
    "result_claim": False,
    "source_pin": LISTENING_RESEARCH_PATH,
    "verified_independently": False,
}


def _format_block() -> Dict[str, Any]:
    return {
        "sdk_v0_channels": CHANNELS,
        "sdk_v0_frame_samples": FRAME_SAMPLES,
        "sdk_v0_geometry_preserved": True,
        "sdk_v0_sample_format": "f32",
        "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
        "surrogate_channels": CHANNELS,
        "surrogate_content_delay_samples": CONTENT_DELAY_SAMPLES,
        "surrogate_frame_samples": FRAME_SAMPLES,
        "surrogate_sample_format": "float32",
        "surrogate_sample_rate_hz": SAMPLE_RATE_HZ,
        "upstream_channels": None,
        "upstream_content_delay_samples": None,
        "upstream_frame_samples": None,
        "upstream_geometry_verified": False,
        "upstream_hop_samples": None,
        "upstream_loudness_normalization": None,
        "upstream_output_energy_constraint_db": None,
        "upstream_sample_rate_hz": None,
    }


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "blocked_cases": [
            "no licensed streaming source, exact parameter set or runtime, so "
            "no exact output is reproduced",
            "no deployed receiver-side geometry, causal masker estimate, "
            "energy/loudness contract or content-delay measurement",
            "no rights-cleared independent masker cohort or listener protocol",
            "no listener outcome, hearing profile, word recognition or "
            "listening-effort result",
            "no independent output-energy audit or target-device timing",
            "no opt-in provider intake, descriptor review or release approval",
        ],
        "mapped_cases": [
            "identity, fixed-tilt, shaping-only, DRC-only and shaping-plus-DRC "
            "controls on the exact 16 kHz/160-sample grid",
            "deterministic synthetic sweeps, steps, impulses, silence, "
            "clicks and speech-like mixtures",
            "gain, tone response, level-transfer slope, attack/release, "
            "headroom and zero content delay",
            "bounded causal energy equalization and masker-band adaptation",
            "finite, peak, clipping, silence-exactness and nonfinite rejection",
            "state reset, stale epoch, chunk-boundary and streaming parity",
        ],
        "name": "DSP",
        "not_applicable": [
            "no qualified candidate artifact exists to evaluate",
            "the local approximation is not the research candidate",
            "no real corpus, listener or target device is available",
        ],
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
    }


def _published_controls() -> Dict[str, Any]:
    return {
        "optfractasii": {
            "designation": PUBLISHED_METHOD_DESIGNATION,
            "exact_algorithm_present": False,
            "exact_parameters_present": False,
            "license_present": False,
            "literature_locator": PUBLISHED_METHOD_LOCATOR,
            "reference_output_present": False,
            "reproduced": False,
            "result_claim": False,
            "runtime_present": False,
            "source_present": False,
            "status": "literature_locator_only",
        },
        "research_prototype": {
            "causal": False,
            "exact_parameters_present": False,
            "license_present": False,
            "locator": RESEARCH_NOTE_LOCATOR,
            "module_locator": "src/audioml_eval/nele.py",
            "reference_output_present": False,
            "reproduced": False,
            "result_claim": False,
            "runtime_present": False,
            "sdk_reference": False,
            "source_present": False,
            "status": "offline_non_causal_prototype_not_adapter",
            "whole_file_energy_normalization": True,
        },
        "separation": {
            "fixed_dsp_measured_locally": True,
            "historical_research_screen_reproduced": False,
            "local_approximation_is_published_control": False,
            "pooling_performed": False,
            "published_controls_reproduced": False,
        },
    }


def _qualification_block() -> Dict[str, Any]:
    return {
        "all_release_gates_blocked": True,
        "algorithm_identity_verified": False,
        "candidate_result_present": False,
        "energy_equalization_contract_verified": False,
        "fixed_dsp_separated": True,
        "geometry_verified": False,
        "historical_research_reproduced": False,
        "listener_outcomes_present": False,
        "listening_present": False,
        "local_approximation_is_candidate": False,
        "masker_cohort_rights_cleared": False,
        "missing_result_promoted": False,
        "not_qualified": True,
        "provider_intake_present": False,
        "published_control_reproduced": False,
        "quality_result_present": False,
        "readiness": "incomplete",
        "reference_output_present": False,
        "release_claim": False,
        "rights_cleared_cohort_present": False,
        "runtime_present": False,
        "source_licensed": False,
        "source_present": False,
        "status": QUALIFICATION,
        "timing_result_present": False,
    }


def _report_body() -> Dict[str, Any]:
    measurements = {mode: measure_mode(mode) for mode in VALID_MODES}
    return {
        "acceptance_profile": _acceptance_profile(),
        "asset_pins": {
            "asset:configuration": {
                "executed": False,
                "expected_path": CONFIGURATION_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(CONFIGURATION_PATH).exists(),
            },
            "asset:license": {
                "executed": False,
                "expected_path": LICENSE_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(LICENSE_PATH).exists(),
            },
            "asset:listener_outcomes": {
                "executed": False,
                "expected_path": LISTENER_OUTCOMES_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(LISTENER_OUTCOMES_PATH).exists(),
            },
            "asset:masker_cohort": {
                "executed": False,
                "expected_path": MASKER_COHORT_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(MASKER_COHORT_PATH).exists(),
            },
            "asset:reference_output": {
                "executed": False,
                "expected_path": REFERENCE_OUTPUT_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(REFERENCE_OUTPUT_PATH).exists(),
            },
            "asset:runtime": {
                "admitted": False,
                "executed": False,
                "expected_path": RUNTIME_ENV_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(RUNTIME_ENV_PATH).exists(),
            },
            "asset:source": {
                "executed": False,
                "expected_path": SOURCE_PATH,
                "hashed_here": False,
                "identity_status": "not_recorded",
                "loaded": False,
                "path_status": "candidate_location_not_upstream_verified",
                "present": resolve_source_path(SOURCE_PATH).exists(),
            },
        },
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "reviewer": REVIEWER,
            "worktree": CLAIM_WORKTREE,
        },
        "component_id": COMPONENT,
        "contract_sha256": sha256(canonical_bytes(contract_payload())),
        "controls": {
            "asset": asset_controls(),
            "config": config_adverse_control(),
            "frame": frame_adverse_control(),
            "impulse": impulse_control(),
            "masker_adaptation": masker_response_control(),
            "nonfinite": nonfinite_control(),
            "reset": reset_control(),
            "silence": silence_control(),
            "streaming_parity": streaming_parity_control(),
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "fixed_dsp_controls": {
            "compressor_only": {
                "candidate_result": False,
                "measurements": measurements["compressor_only"],
                "role": "local_dsp_control",
            },
            "fixed_tilt": {
                "candidate_result": False,
                "measurements": measurements["fixed_tilt"],
                "role": "fixed_dsp_control",
            },
            "identity": {
                "candidate_result": False,
                "measurements": measurements["identity"],
                "role": "mandatory_control",
            },
            "noise_aware_shaping": {
                "candidate_result": False,
                "measurements": measurements["noise_aware_shaping"],
                "role": "local_shaping_control",
            },
            "static_gain": {
                "candidate_result": False,
                "measurements": measurements["static_gain"],
                "role": "fixed_dsp_control",
            },
        },
        "fixture": {
            "channels": CHANNELS,
            "component_digests": FIXTURE_DIGESTS,
            "frames": TOTAL_FRAMES,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "spec_digest": FIXTURE_SPEC_DIGEST,
            "total_samples": TOTAL_SAMPLES,
        },
        "format": _format_block(),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": requirement,
             "status": "blocked"}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "historical_research_screen": HISTORICAL_RESEARCH_SCREEN,
        "local_approximation": {
            "algorithm": {
                "bands_hz": list(BAND_EDGES_HZ),
                "band_importance": list(BAND_IMPORTANCE),
                "content_delay_samples": CONTENT_DELAY_SAMPLES,
                "energy_equalization": "bounded causal 50 ms tracker, +/-12 dB",
                "gain_computer": (
                    "threshold -24 dBFS, ratio 3:1, 5 ms attack, 120 ms "
                    "release"),
                "masker_source": "oracle synthetic listener-side masker",
                "peak_ceiling": PEAK_CEILING,
                "shaping_limit_db": SHAPING_LIMIT_DB,
                "shaping_strength_db": SHAPING_STRENGTH_DB,
                "splitter": (
                    "causal first-order subtractive bands, not a gammatone "
                    "filterbank"),
            },
            "candidate_result": False,
            "id": "local_causal_noise_aware_shaping_plus_drc_surrogate",
            "is_optfractasii": False,
            "is_research_candidate": False,
            "measurements": measurements["local_approximation"],
            "model_free": True,
            "surrogate_only": True,
            "uses_real_corpus": False,
        },
        "measurements": measurements,
        "missing_results": [
            "licensed streaming shaping-plus-DRC source revision and licence",
            "published filterbank, importance vector, water-filling level and "
            "exact parameter set",
            "pinned runtime and approved reference output vectors",
            "deployed geometry, causal masker estimate, energy contract and "
            "content delay",
            "rights-cleared independent listener-side masker cohort",
            "listener outcomes, hearing profiles and listening protocol",
            "independent output-energy audit and target-device timing",
            "opt-in provider intake, descriptor review and default decision",
        ],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "no_missing_result_qualifies_candidate": True,
        "profile": PROFILE,
        "proposal_only": True,
        "published_controls_assessment": _published_controls(),
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply a licensed streaming source revision, the exact published "
            "algorithm and parameters, a locked runtime with approved "
            "reference outputs, the deployed receiver geometry with a causal "
            "masker estimate and energy contract, and a rights-cleared "
            "independent masker and listener cohort. Then score listener "
            "outcomes independently, audit output energy, measure target "
            "timing and complete OFF-by-default opt-in provider intake. Until "
            "then the candidate stays DEFER, incomplete and not qualified."),
        "schema_id": SCHEMA_ID,
        "scope": dict(SCOPE),
        "separation_from_siblings": {
            "no_pooling": True,
            "note": (
                "The full-band receive DRC, feed-forward compressor, envelope "
                "AGC, EBU R128/loudnorm, static target gain with peak ceiling, "
                "peak limiter, AdaptDRC/SSDRC and STOI/ESTOI packages are "
                "separate evidence. They use different candidates, fixtures "
                "and dispositions; this package does not pool, import, reuse "
                "or reinterpret their outputs, metrics or adapters."),
            "sibling_packages": [
                "docs/task-evidence/full-band-receive-drc",
                "docs/task-evidence/feed-forward-compressor",
                "docs/task-evidence/envelope-agc",
                "docs/task-evidence/ebu-r128-ffmpeg-loudnorm",
                "docs/task-evidence/static-target-gain-with-peak-ceiling",
                "docs/task-evidence/peak-limiter-reference",
                "docs/task-evidence/adaptdrc-ssdrc",
                "docs/task-evidence/stoi-estoi",
            ],
        },
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "algorithm_parameters": UPSTREAM_PARAMETERS,
            "algorithm_parameters_status": UPSTREAM_PARAMETERS_STATUS,
            "commit": UPSTREAM_COMMIT,
            "commit_status": "not_recorded",
            "geometry_status": UPSTREAM_GEOMETRY_STATUS,
            "license": UPSTREAM_LICENSE,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "note": (
                "The research note records an offline numpy/scipy prototype "
                "with broad FFT bands, an approximate importance vector and a "
                "small compressor, plus objective STOI/ESTOI only. No licensed "
                "streaming revision, version, parameter set, runtime or output "
                "vector was obtained or fabricated."),
            "published_method_designation": PUBLISHED_METHOD_DESIGNATION,
            "published_method_locator": PUBLISHED_METHOD_LOCATOR,
            "reference_output": UPSTREAM_REFERENCE_OUTPUT,
            "reference_output_status": UPSTREAM_REFERENCE_OUTPUT_STATUS,
            "research_module_present": UPSTREAM_RESEARCH_MODULE_PRESENT,
            "research_module_status": UPSTREAM_RESEARCH_MODULE_STATUS,
            "runtime": UPSTREAM_RUNTIME,
            "runtime_status": UPSTREAM_RUNTIME_STATUS,
            "source_licensed": False,
            "source_present": False,
            "version": UPSTREAM_VERSION,
            "version_status": "not_recorded",
        },
    }


def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def build_report() -> Dict[str, Any]:
    report = _plain(_report_body())
    if has_negative_zero(report):
        raise ValueError("negative_zero_in_report")
    return report


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    if report is None:
        report = build_report()
    return canonical_bytes(report)


REQUIRED_REPORT_KEYS = {
    "acceptance_profile",
    "asset_pins",
    "base_commit",
    "board_row",
    "boundary",
    "branch",
    "caller_asset_contract",
    "claim",
    "component_id",
    "contract_sha256",
    "controls",
    "decision",
    "defer_before",
    "evidence_status",
    "exact_blockers",
    "fixed_dsp_controls",
    "fixture",
    "format",
    "gates",
    "historical_research_screen",
    "local_approximation",
    "measurements",
    "missing_results",
    "negative_claims",
    "no_missing_result_qualifies_candidate",
    "profile",
    "proposal_only",
    "published_controls_assessment",
    "qualification",
    "qualification_status",
    "reopen_condition",
    "schema_id",
    "scope",
    "separation_from_siblings",
    "status",
    "task_id",
    "title",
    "upstream",
}


def contract_payload() -> Dict[str, Any]:
    return {
        "acceptance_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "note": (
                "Only the stable linked-row identity is gated. The mutable "
                "full plan/swarm/TASKS.json is never read into, hashed by or "
                "pinned to this package."),
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "boundary_pins": dict(BOUNDARY_PINS),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "component_id": COMPONENT,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(blocker) for blocker in EXACT_BLOCKERS],
        "format": _format_block(),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": requirement,
             "status": "blocked"}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "the package is proposal-only and incomplete",
            "no missing, blocked or rejected result is promoted to a pass",
            "no licensed source, runtime, reference output, corpus, masker "
            "cohort or listener is downloaded, copied, imported, loaded or "
            "executed",
            "fixed DSP controls, the historical research screen and the local "
            "approximation are never pooled",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
        "local_files": sorted(LOCAL_FILES),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply a licensed streaming source revision, the exact published "
            "algorithm and parameters, a locked runtime with approved "
            "reference outputs, the deployed receiver geometry with a causal "
            "masker estimate and energy contract, and a rights-cleared "
            "independent masker and listener cohort. Then score listener "
            "outcomes independently, audit output energy, measure target "
            "timing and complete OFF-by-default opt-in provider intake."),
        "reviewer": REVIEWER,
        "scenario": {
            "candidate_result": False,
            "channels": CHANNELS,
            "content_delay_samples": CONTENT_DELAY_SAMPLES,
            "energy_equalization": "bounded_causal",
            "id": "noise-aware-shaping-plus-drc-receiver-side-dsp-blocker-v1",
            "is_local_approximation": True,
            "masker_source": "oracle_synthetic",
            "note": (
                "The local approximation runs on the exact installed v0 grid "
                "with zero content delay and an oracle synthetic masker. It is "
                "not the research candidate and not OptFractASII; its geometry "
                "is not the unverified research or deployed geometry."),
            "task_geometry": "receiver-side noise-aware spectral shaping plus "
                             "dynamic-range compression ablation",
            "upstream_geometry_verified": False,
        },
        "schema_id": CONTRACT_SCHEMA_ID,
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "algorithm_parameters": UPSTREAM_PARAMETERS,
            "algorithm_parameters_status": UPSTREAM_PARAMETERS_STATUS,
            "commit": UPSTREAM_COMMIT,
            "commit_status": "not_recorded",
            "geometry_status": UPSTREAM_GEOMETRY_STATUS,
            "license": UPSTREAM_LICENSE,
            "license_status": UPSTREAM_LICENSE_STATUS,
            "published_method_designation": PUBLISHED_METHOD_DESIGNATION,
            "published_method_locator": PUBLISHED_METHOD_LOCATOR,
            "reference_output": UPSTREAM_REFERENCE_OUTPUT,
            "reference_output_status": UPSTREAM_REFERENCE_OUTPUT_STATUS,
            "research_module_present": UPSTREAM_RESEARCH_MODULE_PRESENT,
            "research_module_status": UPSTREAM_RESEARCH_MODULE_STATUS,
            "runtime": UPSTREAM_RUNTIME,
            "runtime_status": UPSTREAM_RUNTIME_STATUS,
            "source_licensed": False,
            "source_present": False,
            "version": UPSTREAM_VERSION,
            "version_status": "not_recorded",
        },
    }


REQUIRED_CONTRACT_KEYS = {
    "acceptance_profile",
    "base_commit",
    "board_row",
    "boundary",
    "boundary_pins",
    "branch",
    "caller_asset_contract",
    "component_id",
    "decision",
    "defer_before",
    "evidence_status",
    "exact_blockers",
    "format",
    "gates",
    "invariants",
    "local_files",
    "negative_claims",
    "profile",
    "proposal_only",
    "qualification",
    "qualification_status",
    "reopen_condition",
    "reviewer",
    "scenario",
    "schema_id",
    "scope",
    "source_pins",
    "status",
    "task_id",
    "title",
    "upstream",
}


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())


def _local_manifest_paths() -> List[str]:
    return sorted(path.name for path in HERE.iterdir()
                  if path.is_file() and path.name != "SOURCES.sha256")


def sources_bytes() -> bytes:
    rows: List[Tuple[str, str]] = []
    for name, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + name))
    for name, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + name))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned research workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        f"# Full mutable plan/swarm/TASKS.json is never hashed; only "
        f"board_row.stable_sha256={BOARD_ROW_STABLE_SHA256} is gated.",
    ]
    for digest, path in rows:
        lines.append(f"{digest}  {path}")
    return ("\n".join(lines) + "\n").encode("ascii")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError(f"malformed_pin_line:{number}")
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:") or
                path.startswith(TASK_PREFIX)):
            raise ValueError(f"unknown_pin_prefix:{number}")
        if path in seen:
            raise ValueError(f"duplicate_pin:{number}")
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows


def allowed_pin_keys() -> set[str]:
    return ({"source:" + name for name in SOURCE_PINS} |
            {"sdk:" + name for name in BOUNDARY_PINS} |
            {TASK_PREFIX + name for name in _local_manifest_paths()})


def expected_readme_keys() -> Dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {
            name for name in _local_manifest_paths()
            if name not in ARTIFACT_TABLE_EXCLUDED
        },
    }


def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise ValueError("readme_marker_count:" + section)
    start_index = text.index(start) + len(start)
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise ValueError("readme_marker_missing:" + section)
    return text[start_index:end_index]


def parse_readme_digest_tables(text: str) -> Dict[str, List[Tuple[str, str]]]:
    result: Dict[str, List[Tuple[str, str]]] = {}
    for section in README_SECTIONS:
        rows: List[Tuple[str, str]] = []
        for line in _section_text(text, section).splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not cells or not cells[0].startswith("`"):
                continue
            key = cells[0].strip("`")
            if section == "artifacts":
                if len(cells) != 3 or \
                        re.fullmatch(r"[0-9]+", cells[2]) is None:
                    raise ValueError("malformed_artifact_row:" + key)
                digest = cells[1].strip("`")
            else:
                if len(cells) != 2:
                    raise ValueError("malformed_digest_row:" + key)
                digest = cells[1].strip("`")
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError("malformed_digest:" + key)
            rows.append((key, digest))
        if len({key for key, _ in rows}) != len(rows):
            raise ValueError("duplicate_readme_row:" + section)
        result[section] = rows
    return result


def verify_readme_digests(text: str) -> Dict[str, int]:
    parsed = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    for section in README_SECTIONS:
        actual_keys = {key for key, _ in parsed[section]}
        if actual_keys != expected[section]:
            missing = sorted(expected[section] - actual_keys)
            extra = sorted(actual_keys - expected[section])
            raise ValueError(
                f"readme_key_mismatch:{section}:missing={missing}:extra={extra}")
        for key, digest in parsed[section]:
            if section == "source":
                expected_digest = SOURCE_PINS[key[len("source:"):]]
                path = resolve_source_path(key[len("source:"):])
            elif section == "boundary":
                expected_digest = BOUNDARY_PINS[key[len("sdk:"):]]
                path = SDK_ROOT / key[len("sdk:"):]
            else:
                expected_digest = sha256_file(HERE / key)
                path = HERE / key
            if digest != expected_digest:
                raise ValueError("readme_digest_mismatch:" + key)
            if path is not None and path.is_file() and \
                    sha256_file(path) != digest:
                raise ValueError("readme_live_digest_mismatch:" + key)
    for key, _ in parsed["artifacts"]:
        size = (HERE / key).stat().st_size
        line = f"| `{key}` | `{sha256_file(HERE / key)}` | {size} |"
        if line not in text:
            raise ValueError("readme_artifact_size_mismatch:" + key)
    return {section: len(rows) for section, rows in parsed.items()}


def render_artifact_table() -> str:
    rows = [
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->",
        "| Path | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
    ]
    for name in _local_manifest_paths():
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        path = HERE / name
        rows.append(f"| `{name}` | `{sha256_file(path)}` | "
                    f"{path.stat().st_size} |")
    rows.append("<!-- DIGEST_TABLE_ARTIFACTS_END -->")
    return "\n".join(rows)


def update_readme_artifact_table(text: str) -> str:
    block = render_artifact_table()
    start = text.index(README_MARKERS["artifacts"][0])
    end = text.index(README_MARKERS["artifacts"][1], start) + \
        len(README_MARKERS["artifacts"][1])
    return text[:start] + block + text[end:]


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = [
        '{"a":1,"a":2}',
        '{"a": NaN}',
        '{"a": Infinity}',
        '[]',
        '{"a":1} trailing',
    ]
    rejected_json = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except ValueError:
            rejected_json += 1
    bad_pins = [
        "not-a-pin",
        "0" * 64 + " source:one",
        "0" * 63 + "  source:one",
        "\n".join(["0" * 64 + "  source:one", "0" * 64 + "  source:one"]),
        "0" * 64 + "  other:one",
    ]
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except ValueError:
            rejected_pins += 1
    bad_readme = [
        "# no tables",
        "<!-- digest-table: source -->\n| `source:x` | `zz` |\n"
        "<!-- digest-table: end -->",
        "<!-- DIGEST_TABLE_ARTIFACTS_START -->\n"
        "| `a` | `" + "0" * 64 + "` |\n<!-- DIGEST_TABLE_ARTIFACTS_END -->",
    ]
    rejected_readme = 0
    for text in bad_readme:
        try:
            parse_readme_digest_tables(text)
        except ValueError:
            rejected_readme += 1
    return {
        "bad_json_rejected": rejected_json,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": rejected_pins,
        "bad_pins_total": len(bad_pins),
        "bad_readme_rejected": rejected_readme,
        "bad_readme_total": len(bad_readme),
    }
