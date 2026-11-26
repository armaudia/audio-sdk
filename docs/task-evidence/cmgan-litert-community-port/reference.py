# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local CMGAN-LiteRT boundary evidence.

This is an original, stdlib-only synthetic probe written for this task. It is
NOT CMGAN, NOT the litert-community/CMGAN-LiteRT port, and NOT a LiteRT runtime,
weight file, conversion, benchmark or result. No upstream code, model, weight,
delegate, Android target, corpus or asset is present, copied, downloaded,
loaded, imported or executed.

The probe consumes caller-owned 16 kHz mono float32 160-sample frames, runs a
bounded adaptive frame-energy suppressor, and measures paired SI-SDR, direct
SNR, clean preservation, peak and nonfinite behavior on a frozen synthetic
fixture. It exists only to exercise strict parsing, exact fixture arithmetic,
streaming state, reset, block invariance and adverse rejection at a task-local
proposal boundary. It is proposal-only, incomplete and not qualified.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

VERSION = "0.1.0"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
REPORT_SCHEMA = "audio-sdk/cmgan-litert-community-port-report/0.1"
TASK_ID = "SDK-CMGAN-LITERT-COMMUNITY-PORT"
TITLE = "CMGAN-LiteRT community port"
COMPONENT = "cmgan-litert-community-port"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "6967a728b5c4048fb01ed4522a76a6906fbcffe2"
BRANCH = "swarm/SDK-CMGAN-LITERT-COMMUNITY-PORT"
REVIEWER = "reviewer-CMGAN-LITERT-COMMUNITY-PORT"
PROFILE = "enhancement"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
STATUS = "proposal_only_synthetic_incomplete"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_NS = 62500
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS
PRECISION = "float32"

FIXTURE_LENGTH = 8000
ACTIVE_END = 6400
GAIN_FLOOR_MILLI = 150
NOISE_FLOOR_DECAY_NUM = 3
NOISE_FLOOR_DECAY_DEN = 4
NOISE_FLOOR_RISE_NUM = 1
NOISE_FLOOR_RISE_DEN = 2000
NONFINITE_FLOOR_MILLIDB = -999000
MAX_REPORTED_MILLIDB = 999000
INT_SCALE = 32768.0
INT_SCALE_SQ = INT_SCALE * INT_SCALE
FINAL_PARTIAL_VALID = 137

CANDIDATE_CARD_URL = "https://huggingface.co/litert-community/CMGAN-LiteRT"
CANDIDATE_REPORTED_PRECISION = "FP16"
CANDIDATE_REPORTED_PLATFORM = "Android/edge"
CANDIDATE_REPORTED_DEVICE_ISSUE = (
    "source-reported Galaxy NPU run failure; not independently reproduced"
)

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

SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"name": "speech_a", "start": 0, "end": 2400, "active": True},
    {"name": "pause", "start": 2400, "end": 3200, "active": False},
    {"name": "speech_b", "start": 3200, "end": 6400, "active": True},
    {"name": "tail_silence", "start": 6400, "end": 8000, "active": False},
)
SEGMENT_KEYS = {"name", "start", "end", "active"}
FIXTURE_KEYS = {"length_samples", "segments", "voice_scale", "noise_amplitude",
                "clean_seed", "noise_seed"}
VOICE_SCALE = 6000
NOISE_AMPLITUDE = 1600
CLEAN_SEED = 20261126
NOISE_SEED = 20261127

SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv": (
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245"
    ),
    "research/voice-enhancement-20261101/agent-denoise-trials/REPORT.md": (
        "c00e26847c119928f068cb5da00ba88106a2d977b67bf8b325ec27093eca8f4e"
    ),
    "research/voice-enhancement-20261101/agent-denoise/REPORT.md": (
        "eb1fef2ab460c11fe382d1a978ef762f91a1c1e93725e7ac443b9b5c05098b07"
    ),
    "research/noise_suppression_candidate_census.md": (
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a"
    ),
    "audio-benchmark-platform/plan/INVENTORY.json": (
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c"
    ),
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": (
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910"
    ),
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md": (
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69"
    ),
    "audio-benchmark-platform/audio-sdk/README.md": (
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35"
    ),
}

BOUNDARY_PINS = {
    "CONTRACTS.md": (
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69"
    ),
    "REUSE.toml": (
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8"
    ),
    "CMakeLists.txt": (
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04"
    ),
    "api/include/audio_sdk/provider_v0.h": (
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766"
    ),
    "api/include/audio_sdk/session_v0.h": (
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1"
    ),
    "scripts/ci.py": (
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f"
    ),
    "docs/task-evidence/metricgan-speechbrain-voicebank/README.md": (
        "0ce5593cda4ed6412d755ecd013c4ef65f3e1c50c4f264a1abb4782b57990f22"
    ),
    "docs/task-evidence/metricgan-speechbrain-voicebank/report.json": (
        "8f04d6f06cea71f6497277131d3b4adcb7b5381c5fc25b4fa646fe91476935e2"
    ),
    "docs/task-evidence/metricgan-speechbrain-voicebank/contract.json": (
        "f7cab2bb7aa92a43f7efb2c009ecc6f8b9b6cadf690f09cb5bb362186d720d00"
    ),
    "docs/task-evidence/cagcrn-joint-aec-and-ns/README.md": (
        "aeae96f49acad572294b69cafb1b581392c3c3c11171d60545eadd6ede3187c7"
    ),
    "docs/task-evidence/cagcrn-joint-aec-and-ns/report.json": (
        "697eb9feb470d529ba8132a8d597cb52308f46f5d2c6afd36803de268f9d7828"
    ),
}

BOARD_ROW_STABLE_SHA256 = (
    "1b332de57d71b72edc87bc7ed6c48d8e422146db04c39eec160e8d787a2f673c"
)

TASK_PREFIX = "docs/task-evidence/cmgan-litert-community-port/"
ARTIFACT_FILES: Tuple[str, ...] = (
    "README.md",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
CONTRACT_PIN_FILES: Tuple[str, ...] = ARTIFACT_FILES
LOCAL_PIN_FILES: Tuple[str, ...] = ARTIFACT_FILES + ("contract.json",)

SPDX = {
    "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
    "SPDX-License-Identifier": "Apache-2.0",
}


class ReferenceRejection(ValueError):
    """Deterministic, machine-readable rejection; no state is advanced."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


def _unique_json_object(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError("nonfinite_json_constant:" + value)


def load_strict_json_text(text: str) -> Dict[str, Any]:
    """Strict JSON object: no duplicate keys, no NaN/Infinity, object root."""
    try:
        value = json.loads(text, object_pairs_hook=_unique_json_object,
                           parse_constant=_reject_json_constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json") from error
    if not isinstance(value, dict):
        raise ValueError("json_not_object")
    return value


def load_strict_json(path: Path) -> Dict[str, Any]:
    return load_strict_json_text(Path(path).read_text(encoding="utf-8"))


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise ReferenceRejection(code)


def _exact_keys(value: object, keys: set[str], label: str) -> None:
    _require(isinstance(value, dict), "invalid_object:" + label)
    actual = set(value)  # type: ignore[arg-type]
    if actual != keys:
        raise ReferenceRejection(
            "strict_keys_mismatch:" + label + ":"
            + ",".join(sorted(actual ^ keys)))


def _integer(value: object, label: str, low: int, high: int) -> int:
    if (not isinstance(value, int) or isinstance(value, bool)
            or not low <= value <= high):
        raise ReferenceRejection("invalid_integer:" + label)
    return value


def _string(value: object, label: str, low: int, high: int) -> str:
    if not isinstance(value, str) or not low <= len(value) <= high:
        raise ReferenceRejection("invalid_string:" + label)
    return value


def _sha256(value: object, label: str) -> str:
    text = _string(value, label, 64, 64)
    if any(character not in "0123456789abcdef" for character in text):
        raise ReferenceRejection("invalid_sha256:" + label)
    return text


def _commit(value: object, label: str) -> str:
    text = _string(value, label, 40, 40)
    if any(character not in "0123456789abcdef" for character in text):
        raise ReferenceRejection("invalid_string:" + label)
    return text


def _absolute_path(value: object, label: str) -> str:
    text = _string(value, label, 1, 512)
    if not text.startswith("/"):
        raise ReferenceRejection("invalid_source_path:" + label)
    return text


def int_signal_digest(samples: Sequence[int]) -> str:
    return sha256_bytes(struct.pack("<%di" % len(samples), *samples))


def signal_digest(samples: Sequence[float]) -> str:
    return sha256_bytes(b"".join(struct.pack("<d", float(value))
                                 for value in samples))


def _energy(samples: Sequence[float | int], start: int, end: int) -> float:
    total = 0.0
    for index in range(start, end):
        value = float(samples[index])
        total += value * value
    return total


def _db_millidb(numerator: float, denominator: float) -> int:
    if denominator <= 0.0:
        return MAX_REPORTED_MILLIDB
    if numerator <= 0.0:
        return NONFINITE_FLOOR_MILLIDB
    value = 1000.0 * 10.0 * math.log10(numerator / denominator)
    return int(round(value))


def _si_sdr_millidb(clean: Sequence[float],
                    estimate: Sequence[float]) -> int:
    _require(len(clean) == len(estimate), "metric_length_mismatch")
    dot = 0.0
    estimate_energy = 0.0
    for index in range(len(clean)):
        dot += clean[index] * estimate[index]
        estimate_energy += estimate[index] * estimate[index]
    if estimate_energy <= 0.0:
        return NONFINITE_FLOOR_MILLIDB
    alpha = dot / estimate_energy
    target_energy = 0.0
    error_energy = 0.0
    for index in range(len(clean)):
        target = alpha * estimate[index]
        error = clean[index] - target
        target_energy += target * target
        error_energy += error * error
    return _db_millidb(target_energy, error_energy)


def _envelope_correlation_millipoints(clean: Sequence[float],
                                      output: Sequence[float]) -> int:
    clean_rms: List[float] = []
    output_rms: List[float] = []
    for start in range(0, len(clean) - FRAME_SAMPLES + 1, FRAME_SAMPLES):
        clean_rms.append(math.sqrt(
            sum(clean[index] * clean[index]
                for index in range(start, start + FRAME_SAMPLES))
            / FRAME_SAMPLES))
        output_rms.append(math.sqrt(
            sum(output[index] * output[index]
                for index in range(start, start + FRAME_SAMPLES))
            / FRAME_SAMPLES))
    mean_clean = sum(clean_rms) / len(clean_rms)
    mean_output = sum(output_rms) / len(output_rms)
    numerator = 0.0
    clean_var = 0.0
    output_var = 0.0
    for index in range(len(clean_rms)):
        centered_clean = clean_rms[index] - mean_clean
        centered_output = output_rms[index] - mean_output
        numerator += centered_clean * centered_output
        clean_var += centered_clean * centered_clean
        output_var += centered_output * centered_output
    if clean_var <= 0.0 or output_var <= 0.0:
        return 0
    return int(round(1000.0 * numerator / math.sqrt(clean_var * output_var)))


# ---------------------------------------------------------------------------
# Frozen synthetic fixture
# ---------------------------------------------------------------------------

def fixture_spec() -> Dict[str, Any]:
    return {
        "length_samples": FIXTURE_LENGTH,
        "segments": [dict(segment) for segment in SEGMENTS],
        "voice_scale": VOICE_SCALE,
        "noise_amplitude": NOISE_AMPLITUDE,
        "clean_seed": CLEAN_SEED,
        "noise_seed": NOISE_SEED,
    }


def validate_fixture(spec: Dict[str, Any]) -> None:
    _exact_keys(spec, FIXTURE_KEYS, "fixture")
    length = _integer(spec["length_samples"], "length_samples", 160, 200000)
    _require(length == FIXTURE_LENGTH, "fixture_length_mismatch")
    _integer(spec["voice_scale"], "voice_scale", 1, 32767)
    _integer(spec["noise_amplitude"], "noise_amplitude", 0, 32767)
    _integer(spec["clean_seed"], "clean_seed", 0, 0x7FFFFFFF)
    _integer(spec["noise_seed"], "noise_seed", 0, 0x7FFFFFFF)
    segments = spec["segments"]
    _require(isinstance(segments, list) and len(segments) == len(SEGMENTS),
             "fixture_segment_count")
    cursor = 0
    for segment in segments:
        _exact_keys(segment, SEGMENT_KEYS, "segment")
        _require(isinstance(segment["name"], str), "invalid_segment_name")
        start = _integer(segment["start"], "segment_start", 0, length)
        end = _integer(segment["end"], "segment_end", 0, length)
        _require(start == cursor and start < end, "segment_order_mismatch")
        _require(isinstance(segment["active"], bool), "invalid_active_flag")
        cursor = end
    _require(cursor == length, "segment_coverage_mismatch")


def _lcg_values(seed: int, count: int) -> List[int]:
    state = seed & 0x7FFFFFFF
    values: List[int] = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append((state % 65535) - 32767)
    return values


def _voice_values(count: int) -> List[int]:
    envelope = (0, 400, 1200, 2200, 3000, 2600, 1800, 900,
                0, 0, 300, 1000, 1800, 1200, 500, 0)
    values: List[int] = []
    for index in range(count):
        tone = (3 * SINE64[index % 64]
                + 2 * SINE64[(2 * index + 7) % 64]
                + SINE64[(3 * index + 13) % 64]) // 6
        level = envelope[(index // 80) % len(envelope)]
        values.append(tone * level * VOICE_SCALE // (32767 * 3000))
    return values


def _active_mask(length: int) -> List[bool]:
    active = [False] * length
    for segment in SEGMENTS:
        for index in range(segment["start"], segment["end"]):
            active[index] = bool(segment["active"])
    return active


def build_fixture() -> Dict[str, Any]:
    """Build a frozen synthetic clean/noise/noisy 16 kHz mono fixture."""
    validate_fixture(fixture_spec())
    active = _active_mask(FIXTURE_LENGTH)
    voice = _voice_values(FIXTURE_LENGTH)
    clean = [voice[index] if active[index] else 0
             for index in range(FIXTURE_LENGTH)]
    base = _lcg_values(NOISE_SEED, FIXTURE_LENGTH)
    noise = [value * NOISE_AMPLITUDE // 32767 for value in base]
    noisy = [max(-32768, min(32767, clean[index] + noise[index]))
             for index in range(FIXTURE_LENGTH)]
    return {"clean": clean, "noise": noise, "noisy": noisy}


# ---------------------------------------------------------------------------
# Task-local adaptive suppressor
# ---------------------------------------------------------------------------

CONFIG_KEYS = {"sample_rate_hz", "channels", "frame_samples", "sample_format",
               "clock_ppm", "resampling", "algorithmic_latency_samples",
               "precision"}


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the task-local probe configuration; fail closed."""
    _exact_keys(config, CONFIG_KEYS, "config")
    rate = _integer(config["sample_rate_hz"], "sample_rate_hz", 1, 384000)
    channels = _integer(config["channels"], "channels", 1, 8)
    frame = _integer(config["frame_samples"], "frame_samples", 1, 4096)
    clock = _integer(config["clock_ppm"], "clock_ppm", -1000000, 1000000)
    latency = _integer(config["algorithmic_latency_samples"],
                       "algorithmic_latency_samples", 0, 16000)
    _require(isinstance(config["sample_format"], str), "invalid_sample_format")
    _require(isinstance(config["resampling"], str), "invalid_resampling")
    _require(isinstance(config["precision"], str), "invalid_precision")
    if rate != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_sample_rate")
    if channels != CHANNELS:
        raise ReferenceRejection("unsupported_channels")
    if frame != FRAME_SAMPLES:
        raise ReferenceRejection("unsupported_frame_samples")
    if config["sample_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("unsupported_sample_format")
    if clock != 0:
        raise ReferenceRejection("unsupported_clock_drift")
    if config["resampling"] != "none":
        raise ReferenceRejection("unsupported_resampling")
    if latency != 0:
        raise ReferenceRejection("unsupported_algorithmic_latency")
    if config["precision"] != PRECISION:
        raise ReferenceRejection("unsupported_precision")
    return {"sample_rate_hz": rate, "channels": channels,
            "frame_samples": frame, "sample_format": config["sample_format"],
            "clock_ppm": clock, "resampling": config["resampling"],
            "algorithmic_latency_samples": latency,
            "precision": config["precision"]}


def _validate_frame(samples: object, valid_count: object) -> int:
    count = _integer(valid_count, "valid_count", 1, FRAME_SAMPLES)
    if samples is None:
        raise ReferenceRejection("missing_input")
    if not isinstance(samples, (list, tuple)):
        raise ReferenceRejection("invalid_frame:input")
    if len(samples) != FRAME_SAMPLES:
        raise ReferenceRejection("frame_count_mismatch:input")
    for index in range(count):
        value = samples[index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceRejection("invalid_sample:input")
        if not math.isfinite(float(value)):
            raise ReferenceRejection("nonfinite_input:input")
    for index in range(count, FRAME_SAMPLES):
        value = samples[index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceRejection("invalid_sample:input")
        if float(value) != 0.0:
            raise ReferenceRejection("padding_not_zero:input")
    return count


class AdaptiveEnergySuppressor:
    """Bounded deterministic frame-energy suppressor, not CMGAN or LiteRT."""

    def __init__(self, sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = CHANNELS, frame_samples: int = FRAME_SAMPLES,
                 sample_format: str = SAMPLE_FORMAT,
                 precision: str = PRECISION, epoch: int = 1):
        if (sample_rate_hz != SAMPLE_RATE_HZ or channels != CHANNELS
                or frame_samples != FRAME_SAMPLES
                or sample_format != SAMPLE_FORMAT
                or precision != PRECISION):
            raise ReferenceRejection(
                "unsupported_config", "v0 accepts only 16000/1/160/float32")
        if (not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1):
            raise ReferenceRejection("invalid_epoch")
        self.epoch = epoch
        self.position = 0
        self.frames = 0
        self.noise_floor = 0.0
        self.previous_gain_milli = 1000

    @property
    def state_digest(self) -> str:
        payload = struct.pack("<qqdqi", self.epoch, self.position,
                              self.noise_floor, self.frames,
                              self.previous_gain_milli)
        return sha256_bytes(payload)

    def reset(self, epoch: int, first_input_sample: int) -> None:
        if (not isinstance(epoch, int) or isinstance(epoch, bool)
                or epoch <= self.epoch):
            raise ReferenceRejection("invalid_epoch")
        if (not isinstance(first_input_sample, int)
                or isinstance(first_input_sample, bool)
                or first_input_sample < 0):
            raise ReferenceRejection("invalid_first_input_sample")
        self.epoch = epoch
        self.position = first_input_sample
        self.frames = 0
        self.noise_floor = 0.0
        self.previous_gain_milli = 1000

    def process_frame(self, samples: Sequence[float] | None,
                      valid_count: int = FRAME_SAMPLES,
                      epoch: int | None = None,
                      first_input_sample: int | None = None
                      ) -> List[float]:
        count = _validate_frame(samples, valid_count)
        expected_epoch = self.epoch if epoch is None else epoch
        if (not isinstance(expected_epoch, int)
                or isinstance(expected_epoch, bool)
                or expected_epoch != self.epoch):
            raise ReferenceRejection("epoch_mismatch")
        if (first_input_sample is not None
                and (not isinstance(first_input_sample, int)
                     or isinstance(first_input_sample, bool)
                     or first_input_sample != self.position)):
            raise ReferenceRejection("input_position_mismatch")

        power = 0.0
        for index in range(count):
            value = float(samples[index])
            power += value * value
        rms = math.sqrt(power / count)
        if self.noise_floor <= 0.0:
            self.noise_floor = rms
        elif rms < self.noise_floor:
            self.noise_floor = (
                NOISE_FLOOR_DECAY_NUM * self.noise_floor
                + (NOISE_FLOOR_DECAY_DEN - NOISE_FLOOR_DECAY_NUM) * rms
            ) / NOISE_FLOOR_DECAY_DEN
        else:
            self.noise_floor = (
                NOISE_FLOOR_RISE_NUM * rms
                + (NOISE_FLOOR_RISE_DEN - NOISE_FLOOR_RISE_NUM)
                * self.noise_floor
            ) / NOISE_FLOOR_RISE_DEN
        floor = max(self.noise_floor, 1.0e-12)
        if rms <= 0.0:
            target_gain = GAIN_FLOOR_MILLI
        else:
            ratio = floor / rms
            suppression = 1.0 - ratio * ratio
            if suppression <= (GAIN_FLOOR_MILLI / 1000.0) ** 2:
                target_gain = GAIN_FLOOR_MILLI
            else:
                target_gain = min(1000, max(
                    GAIN_FLOOR_MILLI,
                    int(round(1000.0 * math.sqrt(suppression)))))
        output: List[float] = []
        for index in range(count):
            gain = (self.previous_gain_milli
                    + (target_gain - self.previous_gain_milli)
                    * (index + 1) // count)
            output.append(float(samples[index]) * gain / 1000.0)
        output.extend([0.0] * (FRAME_SAMPLES - count))
        self.previous_gain_milli = target_gain
        self.position += count
        self.frames += 1
        return output


# ---------------------------------------------------------------------------
# Streaming driver and metrics
# ---------------------------------------------------------------------------

def chunk_plan(total: int, pattern: Sequence[int] = (160, 320, 480, 800,
                                                     640, 160)) -> List[int]:
    chunks: List[int] = []
    remaining = total
    index = 0
    while remaining > 0:
        size = pattern[index % len(pattern)]
        if size > remaining:
            size = remaining
        chunks.append(size)
        remaining -= size
        index += 1
    _require(sum(chunks) == total, "chunk_plan_mismatch")
    return chunks


def run_stream(noisy: Sequence[int], chunks: Sequence[int] | None = None,
               epoch: int = 1) -> Dict[str, Any]:
    suppressor = AdaptiveEnergySuppressor(epoch=epoch)
    plan = list(chunks) if chunks is not None else chunk_plan(len(noisy))
    _require(sum(plan) == len(noisy), "chunk_sum_mismatch")
    output: List[float] = []
    offset = 0
    for chunk in plan:
        _require(chunk > 0, "invalid_chunk")
        chunk_end = offset + chunk
        while offset < chunk_end:
            size = min(FRAME_SAMPLES, chunk_end - offset)
            frame = [float(value) / INT_SCALE
                     for value in noisy[offset:offset + size]]
            frame.extend([0.0] * (FRAME_SAMPLES - size))
            out_frame = suppressor.process_frame(frame, valid_count=size)
            output.extend(out_frame[:size])
            offset += size
    return {"output": output, "state_digest": suppressor.state_digest,
            "samples": len(output)}


def _metrics(clean: Sequence[int], estimate: Sequence[float],
             start: int = 0, end: int = FIXTURE_LENGTH) -> Dict[str, int]:
    clean_energy = _energy(clean, start, end) / INT_SCALE_SQ
    estimate_energy = _energy(estimate, start, end)
    error_energy = 0.0
    for index in range(start, end):
        difference = float(estimate[index]) - float(clean[index]) / INT_SCALE
        error_energy += difference * difference
    peak_milli = 0
    for index in range(start, end):
        value = abs(float(estimate[index]))
        if value * 1000.0 > peak_milli:
            peak_milli = int(round(value * 1000.0))
    clean_float = [float(clean[index]) / INT_SCALE
                   for index in range(start, end)]
    estimate_slice = [float(estimate[index]) for index in range(start, end)]
    return {
        "snr_millidb": _db_millidb(clean_energy, error_energy),
        "si_sdr_millidb": _si_sdr_millidb(clean_float, estimate_slice),
        "level_change_millidb": _db_millidb(estimate_energy, clean_energy),
        "peak_milli": peak_milli,
        "nonfinite_output_count": sum(
            0 if math.isfinite(value) else 1 for value in estimate_slice),
    }


def _identity_output(noisy: Sequence[int]) -> List[float]:
    return [float(value) / INT_SCALE for value in noisy]


def enhancement_run() -> Dict[str, Any]:
    fixture = build_fixture()
    identity = _identity_output(fixture["noisy"])
    run = run_stream(fixture["noisy"])
    identity_metrics = _metrics(fixture["clean"], identity)
    output_metrics = _metrics(fixture["clean"], run["output"])
    active_identity = _metrics(fixture["clean"], identity, 0, ACTIVE_END)
    active_output = _metrics(fixture["clean"], run["output"], 0, ACTIVE_END)
    return {
        "fixture": fixture,
        "identity": identity,
        "run": run,
        "identity_metrics": identity_metrics,
        "output_metrics": output_metrics,
        "active_identity_metrics": active_identity,
        "active_output_metrics": active_output,
        "delta_si_sdr_millidb": (output_metrics["si_sdr_millidb"]
                                 - identity_metrics["si_sdr_millidb"]),
        "delta_snr_millidb": (output_metrics["snr_millidb"]
                              - identity_metrics["snr_millidb"]),
        "envelope_correlation_millipoints": _envelope_correlation_millipoints(
            [float(value) / INT_SCALE for value in fixture["clean"]],
            run["output"]),
        "signal_digests": {
            "clean": int_signal_digest(fixture["clean"]),
            "noise": int_signal_digest(fixture["noise"]),
            "noisy": int_signal_digest(fixture["noisy"]),
            "identity_output": signal_digest(identity),
            "surrogate_output": signal_digest(run["output"]),
        },
    }


def streaming_check(run: Dict[str, Any]) -> Dict[str, Any]:
    plan = chunk_plan(FIXTURE_LENGTH)
    streamed = run_stream(run["fixture"]["noisy"], chunks=plan)
    return {
        "chunks": plan,
        "accepted_samples": FIXTURE_LENGTH,
        "all_match": streamed["output"] == run["run"]["output"],
        "offline_state_digest": run["run"]["state_digest"],
        "streamed_state_digest": streamed["state_digest"],
        "scheduler_measured": False,
        "qualifies": False,
    }


def reset_check() -> Dict[str, Any]:
    fixture = build_fixture()
    noisy = fixture["noisy"]
    carried = AdaptiveEnergySuppressor(epoch=1)
    offset = 0
    while offset < len(noisy):
        frame = [float(value) / INT_SCALE
                 for value in noisy[offset:offset + FRAME_SAMPLES]]
        count = len(frame)
        frame.extend([0.0] * (FRAME_SAMPLES - count))
        carried.process_frame(frame, valid_count=count)
        offset += FRAME_SAMPLES
    carried.reset(2, 0)
    offset = 0
    while offset < len(noisy):
        frame = [float(value) / INT_SCALE
                 for value in noisy[offset:offset + FRAME_SAMPLES]]
        count = len(frame)
        frame.extend([0.0] * (FRAME_SAMPLES - count))
        carried.process_frame(frame, valid_count=count, epoch=2)
        offset += FRAME_SAMPLES
    fresh = run_stream(noisy, epoch=2)
    return {
        "epoch": 2,
        "accepted_samples": len(noisy),
        "matches_fresh": carried.state_digest == fresh["state_digest"],
        "state_digest": carried.state_digest,
        "qualifies": False,
    }


def final_partial_check() -> Dict[str, Any]:
    fixture = build_fixture()
    carrier = AdaptiveEnergySuppressor(epoch=1)
    frame = [float(value) / INT_SCALE
             for value in fixture["noisy"][:FINAL_PARTIAL_VALID]]
    frame.extend([0.0] * (FRAME_SAMPLES - FINAL_PARTIAL_VALID))
    output = carrier.process_frame(frame, valid_count=FINAL_PARTIAL_VALID)
    return {
        "valid_count": FINAL_PARTIAL_VALID,
        "padding_zero": True,
        "output_samples": len(output),
        "advanced_samples": carrier.position,
        "tail_zero": all(value == 0.0
                         for value in output[FINAL_PARTIAL_VALID:]),
        "nonfinite_output_count": sum(
            0 if math.isfinite(value) else 1 for value in output),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied asset identity (never loaded or executed)
# ---------------------------------------------------------------------------

CALLER_MANIFEST_FIELDS = {
    "android_target",
    "candidate",
    "channels",
    "delegate",
    "frame_samples",
    "input_format",
    "model_byte_count",
    "model_path",
    "model_sha256",
    "precision",
    "runtime_path",
    "runtime_sha256",
    "runtime_version",
    "sample_rate_hz",
    "source_revision",
    "source_sha256",
    "source_url",
}

DELEGATES = {"none", "xnnpack", "gpu", "npu"}
CALLER_PRECISIONS = {"fp16", "float32"}


def validate_caller_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    _exact_keys(manifest, CALLER_MANIFEST_FIELDS, "caller_manifest")
    _string(manifest["candidate"], "candidate", 1, 64)
    _string(manifest["source_url"], "source_url", 1, 256)
    _string(manifest["runtime_version"], "runtime_version", 1, 64)
    _string(manifest["android_target"], "android_target", 1, 96)
    rate = _integer(manifest["sample_rate_hz"], "sample_rate_hz", 1, 384000)
    channels = _integer(manifest["channels"], "channels", 1, 8)
    frame = _integer(manifest["frame_samples"], "frame_samples", 1, 4096)
    byte_count = _integer(manifest["model_byte_count"], "model_byte_count",
                          1, 1 << 31)
    _require(isinstance(manifest["input_format"], str),
             "invalid_input_format")
    _require(isinstance(manifest["precision"], str), "invalid_precision")
    _require(isinstance(manifest["delegate"], str), "invalid_delegate")
    if rate != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_sample_rate")
    if channels != CHANNELS:
        raise ReferenceRejection("unsupported_channels")
    if frame != FRAME_SAMPLES:
        raise ReferenceRejection("unsupported_frame_samples")
    if manifest["input_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("unsupported_sample_format")
    if manifest["precision"] not in CALLER_PRECISIONS:
        raise ReferenceRejection("unsupported_precision")
    if manifest["delegate"] not in DELEGATES:
        raise ReferenceRejection("unsupported_delegate")
    _absolute_path(manifest["model_path"], "model_path")
    _absolute_path(manifest["runtime_path"], "runtime_path")
    _sha256(manifest["model_sha256"], "model_sha256")
    _sha256(manifest["runtime_sha256"], "runtime_sha256")
    _sha256(manifest["source_sha256"], "source_sha256")
    _commit(manifest["source_revision"], "source_revision")
    return {"validated": True, "loaded": False, "executed": False,
            "imported": False, "model_byte_count": byte_count}


# ---------------------------------------------------------------------------
# Adverse rejection matrix
# ---------------------------------------------------------------------------

def _base_config() -> Dict[str, Any]:
    return {"sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES, "sample_format": SAMPLE_FORMAT,
            "clock_ppm": 0, "resampling": "none",
            "algorithmic_latency_samples": 0, "precision": PRECISION}


def _base_manifest() -> Dict[str, Any]:
    return {
        "android_target": "example/Android/arm64-v8a",
        "candidate": "cmgan-litert-community-port",
        "channels": 1,
        "delegate": "npu",
        "frame_samples": 160,
        "input_format": "float32",
        "model_byte_count": 1024,
        "model_path": "/caller/cmgan-litert/model.tflite",
        "model_sha256": "0" * 64,
        "precision": "fp16",
        "runtime_path": "/caller/litert/liblitert.so",
        "runtime_sha256": "3" * 64,
        "runtime_version": "caller-supplied",
        "sample_rate_hz": 16000,
        "source_revision": "1" * 40,
        "source_sha256": "2" * 64,
        "source_url": CANDIDATE_CARD_URL,
    }


def _expect_reject(code: str, action) -> str:
    try:
        action()
    except ReferenceRejection as error:
        return error.code
    except ValueError as error:
        return str(error)
    return "accepted"


def adverse_rejections() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    def add(case_id: str, code: str, action) -> None:
        actual = _expect_reject(code, action)
        cases.append({
            "case_id": case_id,
            "code": actual,
            "status": "rejected" if actual != "accepted" else "accepted",
            "state_unchanged": bool(actual != "accepted"),
        })

    base = _base_config()
    add("duplicate_json_key", "duplicate_json_key:a",
        lambda: load_strict_json_text('{"a":1,"a":2}'))
    add("nan_json_constant", "nonfinite_json_constant:NaN",
        lambda: load_strict_json_text('{"a":NaN}'))
    add("infinity_json_constant", "nonfinite_json_constant:Infinity",
        lambda: load_strict_json_text('{"a":Infinity}'))
    add("malformed_json", "invalid_json",
        lambda: load_strict_json_text('{"a":'))
    add("config_missing_field", "strict_keys_mismatch:config",
        lambda: validate_config({key: value for key, value in base.items()
                                 if key != "precision"}))
    add("config_extra_field", "strict_keys_mismatch:config",
        lambda: validate_config({**base, "extra": 1}))
    add("config_8000_hz", "unsupported_sample_rate",
        lambda: validate_config({**base, "sample_rate_hz": 8000}))
    add("config_44100_hz", "unsupported_sample_rate",
        lambda: validate_config({**base, "sample_rate_hz": 44100}))
    add("config_stereo", "unsupported_channels",
        lambda: validate_config({**base, "channels": 2}))
    add("config_256_frame", "unsupported_frame_samples",
        lambda: validate_config({**base, "frame_samples": 256}))
    add("config_int16", "unsupported_sample_format",
        lambda: validate_config({**base, "sample_format": "int16"}))
    add("config_clock_drift", "unsupported_clock_drift",
        lambda: validate_config({**base, "clock_ppm": 1}))
    add("config_linear_resampling", "unsupported_resampling",
        lambda: validate_config({**base, "resampling": "linear"}))
    add("config_algorithmic_latency_nonzero", "unsupported_algorithmic_latency",
        lambda: validate_config({**base, "algorithmic_latency_samples": 160}))
    add("config_fp16_precision", "unsupported_precision",
        lambda: validate_config({**base, "precision": "fp16"}))
    add("config_bool_rate", "invalid_integer:sample_rate_hz",
        lambda: validate_config({**base, "sample_rate_hz": True}))

    suppressor = AdaptiveEnergySuppressor(epoch=1)
    fixture = build_fixture()
    frame = [float(value) / INT_SCALE
             for value in fixture["noisy"][:FRAME_SAMPLES]]
    suppressor.process_frame(frame)
    before = suppressor.state_digest

    def add_frame(case_id: str, code: str, action) -> None:
        actual = _expect_reject(code, action)
        cases.append({
            "case_id": case_id,
            "code": actual,
            "status": "rejected" if actual != "accepted" else "accepted",
            "state_unchanged": suppressor.state_digest == before,
        })

    add_frame("frame_missing_input", "missing_input",
              lambda: suppressor.process_frame(None))
    add_frame("frame_epoch_mismatch", "epoch_mismatch",
              lambda: suppressor.process_frame(frame, epoch=2))
    add_frame("frame_input_count_mismatch", "frame_count_mismatch:input",
              lambda: suppressor.process_frame(frame[:159]))
    add_frame("frame_valid_count_zero", "invalid_integer:valid_count",
              lambda: suppressor.process_frame(frame, valid_count=0))
    add_frame("frame_valid_count_high", "invalid_integer:valid_count",
              lambda: suppressor.process_frame(frame, valid_count=161))
    add_frame("frame_nonfinite_input", "nonfinite_input:input",
              lambda: suppressor.process_frame(
                  [float("nan")] + frame[1:]))
    add_frame("frame_nonzero_padding", "padding_not_zero:input",
              lambda: suppressor.process_frame(
                  frame[:137] + [1.0] + frame[138:], valid_count=137))
    add_frame("frame_string_sample", "invalid_sample:input",
              lambda: suppressor.process_frame(["x"] + frame[1:]))
    add_frame("frame_bool_sample", "invalid_sample:input",
              lambda: suppressor.process_frame([True] + frame[1:]))
    add_frame("frame_input_position_mismatch", "input_position_mismatch",
              lambda: suppressor.process_frame(frame, first_input_sample=1))

    reset_before = suppressor.state_digest

    def add_reset(case_id: str, code: str, action) -> None:
        actual = _expect_reject(code, action)
        cases.append({
            "case_id": case_id,
            "code": actual,
            "status": "rejected" if actual != "accepted" else "accepted",
            "state_unchanged": suppressor.state_digest == reset_before,
        })

    add_reset("reset_epoch_zero", "invalid_epoch",
              lambda: suppressor.reset(0, 0))
    add_reset("reset_epoch_negative", "invalid_epoch",
              lambda: suppressor.reset(-1, 0))
    add_reset("reset_epoch_not_greater", "invalid_epoch",
              lambda: suppressor.reset(1, 0))
    add_reset("reset_negative_position", "invalid_first_input_sample",
              lambda: suppressor.reset(2, -1))

    manifest = _base_manifest()
    add("caller_manifest_missing_field", "strict_keys_mismatch:caller_manifest",
        lambda: validate_caller_manifest(
            {key: value for key, value in manifest.items()
             if key != "model_sha256"}))
    add("caller_manifest_relative_model_path",
        "invalid_source_path:model_path",
        lambda: validate_caller_manifest(
            {**manifest, "model_path": "relative/model.tflite"}))
    add("caller_manifest_bad_commit", "invalid_string:source_revision",
        lambda: validate_caller_manifest(
            {**manifest, "source_revision": "not-a-commit"}))
    add("caller_manifest_bad_model_hash", "invalid_sha256:model_sha256",
        lambda: validate_caller_manifest(
            {**manifest, "model_sha256": "0" * 63 + "z"}))
    add("caller_manifest_wrong_rate", "unsupported_sample_rate",
        lambda: validate_caller_manifest(
            {**manifest, "sample_rate_hz": 8000}))
    add("caller_manifest_wrong_channels", "unsupported_channels",
        lambda: validate_caller_manifest({**manifest, "channels": 2}))
    add("caller_manifest_wrong_frame", "unsupported_frame_samples",
        lambda: validate_caller_manifest(
            {**manifest, "frame_samples": 256}))
    add("caller_manifest_wrong_format", "unsupported_sample_format",
        lambda: validate_caller_manifest(
            {**manifest, "input_format": "int16"}))
    add("caller_manifest_wrong_precision", "unsupported_precision",
        lambda: validate_caller_manifest(
            {**manifest, "precision": "int8"}))
    add("caller_manifest_unknown_delegate", "unsupported_delegate",
        lambda: validate_caller_manifest(
            {**manifest, "delegate": "magic"}))
    add("caller_manifest_zero_bytes", "invalid_integer:model_byte_count",
        lambda: validate_caller_manifest(
            {**manifest, "model_byte_count": 0}))
    add("caller_manifest_extra_field", "strict_keys_mismatch:caller_manifest",
        lambda: validate_caller_manifest({**manifest, "extra": 1}))

    def bad_fixture(**changes):
        spec = fixture_spec()
        spec.update(changes)
        validate_fixture(spec)

    add("fixture_length_mismatch", "fixture_length_mismatch",
        lambda: bad_fixture(length_samples=7999))
    add("fixture_segment_count", "fixture_segment_count",
        lambda: bad_fixture(segments=fixture_spec()["segments"][:-1]))
    add("fixture_segment_gap", "segment_order_mismatch",
        lambda: bad_fixture(segments=[
            {**segment, "start": segment["start"] + (1 if index == 1 else 0)}
            for index, segment in enumerate(fixture_spec()["segments"])
        ]))
    add("fixture_noise_negative", "invalid_integer:noise_amplitude",
        lambda: bad_fixture(noise_amplitude=-1))
    return cases


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def board_row() -> Dict[str, Any]:
    """Read only the stable linked-row identity; never hash the full board."""
    payload = load_strict_json(SOURCE_ROOT / TASK_BOARD)
    _require(isinstance(payload.get("tasks"), list), "invalid_task_board")
    rows = [row for row in payload["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    _require(len(rows) == 1, "task_row_not_unique")
    row = rows[0]
    stable_fields = {
        "id": row["id"],
        "title": row["title"],
        "repository": row["repository"],
        "mode": row["mode"],
        "depends_on": row["depends_on"],
        "component": row["component"],
    }
    digest = object_digest(stable_fields)
    _require(digest == BOARD_ROW_STABLE_SHA256,
             "unexpected_stable_board_identity")
    return {
        "stable_fields": stable_fields,
        "stable_sha256": digest,
        "full_tasks_json_hashed": False,
        "note": ("Only the stable linked-row fields are read and gated. The "
                 "mutable full plan/swarm/TASKS.json is never hashed, pinned "
                 "or used as a digest source."),
    }


def _verify_pins() -> None:
    for path, expected in SOURCE_PINS.items():
        full = SOURCE_ROOT / path
        _require(full.is_file(), "missing_source_pin:" + path)
        _require(file_digest(full) == expected, "stale_source_pin:" + path)
    for path, expected in BOUNDARY_PINS.items():
        full = SDK_ROOT / path
        _require(full.is_file(), "missing_boundary_pin:" + path)
        _require(file_digest(full) == expected, "stale_boundary_pin:" + path)


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "identity_noisy_control": {
                "status": "synthetic_only",
                "evidence": ("Exact passthrough identity/noisy control is "
                             "measured on the same frozen synthetic fixture."),
            },
            "task_matched_baseline": {
                "status": "blocked",
                "evidence": ("Official CMGAN and FastEnhancer Small are named "
                             "comparators only; neither baseline was run."),
            },
            "paired_si_sdr": {
                "status": "synthetic_only",
                "evidence": ("Paired SI-SDR and direct SNR in integer millidB "
                             "on generated clean references; no real corpus."),
            },
            "stoi": {
                "status": "blocked",
                "evidence": ("No permitted STOI scorer was executed for this "
                             "candidate; no intelligibility result is claimed."),
            },
            "clean_speech_preservation": {
                "status": "synthetic_only",
                "evidence": ("Active-region level change, paired SI-SDR and a "
                             "clearly labeled envelope-correlation proxy on "
                             "synthetic clean speech only."),
            },
            "peaks_and_invalid_outputs": {
                "status": "synthetic_only",
                "evidence": ("Peak bounds, finite-output counts and nonfinite "
                             "input rejection on synthetic frames only."),
            },
            "unpaired_predictive_screen": {
                "status": "blocked",
                "evidence": ("No unpaired speech, DNSMOS-style predictor or "
                             "separately labeled screen was run."),
            },
            "listening": {
                "status": "blocked",
                "evidence": ("No authorized listening test or listener panel "
                             "was performed."),
            },
            "alignment": {
                "status": "blocked",
                "evidence": ("Candidate content delay and output alignment are "
                             "undocumented; the surrogate declares 0 samples "
                             "and measures no device alignment."),
            },
            "state_memory_timing": {
                "status": "blocked_unmeasured",
                "evidence": ("No LiteRT runtime, delegate, Android device, "
                             "memory trace, RTF, deadline or availability "
                             "measurement exists."),
            },
            "heldout_qualification": {
                "status": "blocked",
                "evidence": ("No rights-cleared task-matched held-out cohort "
                             "or candidate-specific score exists."),
            },
        },
    }


def _profile_blockers(profile: Dict[str, Any]) -> List[str]:
    return sorted(name for name, item in profile["required_items"].items()
                  if item["status"] != "synthetic_only")


def _release_gates() -> List[Dict[str, str]]:
    rows = [
        ("RG-01", "Exact pinned CMGAN-LiteRT source/card, converted model, "
                  "LiteRT runtime, immutable revision, license identity and "
                  "artifact hashes with declared delegate and Android target."),
        ("RG-02", "Isolated hash-pinned LiteRT runtime admission, reproducible "
                  "conversion/build, verified model identity and fail-closed "
                  "absent behavior."),
        ("RG-03", "Code, weight, training-data, conversion/derivative and "
                  "corpus rights plus attribution, notices, redistribution, "
                  "product-use and output-use review."),
        ("RG-04", "Exact candidate I/O geometry: rate, channels, frame, STFT "
                  "hop/window, normalization, tensor layout, precision, "
                  "padding, content delay and lookahead from pinned metadata."),
        ("RG-05", "Local official-CMGAN reference backend versus LiteRT "
                  "numeric parity on identical frozen inputs, with an exact "
                  "tolerance and CPU plus target-device runs."),
        ("RG-06", "Enhancement qualification on a rights-cleared task-matched "
                  "held-out cohort with identity/noisy control, paired SI-SDR "
                  "and STOI where permitted, clean preservation, peaks and "
                  "invalid outputs."),
        ("RG-07", "Named Android target pacing, delegate timing/memory, "
                  "availability, reset/state behavior, documented NPU failure "
                  "mode and independent listening or predictive controls."),
        ("RG-08", "Opt-in provider intake, descriptor review, independent "
                  "exact-head review and default/release approval."),
    ]
    return [{"id": gate, "requirement": text, "status": "blocked"}
            for gate, text in rows]


def _exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "pinned_port_model_and_conversion_absent",
            "requirement": ("Supply one exact litert-community/CMGAN-LiteRT "
                            "revision with the converted model file name, "
                            "byte count and SHA-256, conversion script/source "
                            "revision, and declared tensor I/O metadata."),
            "state": ("The pinned research records only the public card URL "
                      "and a source-reported FP16 Android/edge conversion. No "
                      "immutable revision, model file, byte count, hash, "
                      "conversion record or tensor metadata is staged at "
                      "data/models/cmgan-litert or adapters/cmgan-litert."),
        },
        {
            "id": "litert_runtime_delegate_and_android_target_absent",
            "requirement": ("Supply the exact LiteRT runtime archive/version "
                            "and SHA-256, interpreter/delegate selection, and "
                            "one named Android device/OS/ABI target."),
            "state": ("No local LiteRT runtime or Android target exists. The "
                      "pinned research records vendor-reported device timing "
                      "and a failed Galaxy NPU run but no local runtime, "
                      "delegate, device clock, memory trace or reproduction."),
        },
        {
            "id": "official_cmgan_reference_and_parity_absent",
            "requirement": ("Admit an exact official CMGAN source/checkpoint "
                            "reference backend and define numeric parity "
                            "inputs, preprocessing, tolerance and output "
                            "mapping against the converted LiteRT model."),
            "state": ("No official CMGAN reference backend, checkpoint or "
                      "parity protocol is staged. Third-party conversion "
                      "parity is explicitly unverified, so no numeric, "
                      "quality or deployment claim is possible."),
        },
        {
            "id": "rights_and_conversion_review_absent",
            "requirement": ("Stage the exact code, card, weight, training-data "
                            "and corpus terms plus conversion/derivative, "
                            "attribution, redistribution, product-use and "
                            "output-use review."),
            "state": ("No license identity, license text, model card terms, "
                      "training-data statement, attribution notice or "
                      "conversion/derivative review is staged. The card is "
                      "third-party and its artifact terms are unverified."),
        },
        {
            "id": "rights_cleared_enhancement_cohort_absent",
            "requirement": ("Supply a rights-cleared task-matched held-out "
                            "cohort with clean references where permitted, "
                            "identity/noisy and established baselines, "
                            "paired SI-SDR/STOI, preservation, peaks, invalid "
                            "outputs and stratified failure results."),
            "state": ("Only a generated synthetic fixture exists. No real "
                      "speech, corpus terms, consent, held-out split, baseline "
                      "run or candidate-specific score is staged."),
        },
        {
            "id": "timing_listening_and_independent_review_absent",
            "requirement": ("Measure target-device pacing, delegate latency, "
                            "memory, availability and reset behavior at the "
                            "exact runtime, run independent listening or "
                            "predictive controls, and complete review."),
            "state": ("No device timing, RTF, memory, worker, queue, listening, "
                      "benchmark, provider intake or release approval exists; "
                      "no result may qualify."),
        },
    ]


def _licensing() -> Dict[str, Any]:
    return {
        "reported_upstream_license": None,
        "license_identity_asserted": False,
        "license_text_staged": False,
        "model_card_terms_verified": False,
        "weights_terms_staged": False,
        "training_data_statement_staged": False,
        "conversion_derivative_reviewed": False,
        "attribution_notice_staged": False,
        "redistribution_reviewed": False,
        "product_use_reviewed": False,
        "review_status": "blocked",
        "note": ("The pinned evidence identifies a third-party community card "
                 "only. No license identity, upstream text, weight terms, "
                 "training-data statement or conversion/derivative review is "
                 "staged, so no license is asserted."),
    }


def _candidate() -> Dict[str, Any]:
    return {
        "name": "CMGAN-LiteRT community port",
        "card_url": CANDIDATE_CARD_URL,
        "relation_to_official_cmgan": (
            "third-party re-authoring/conversion; not the official CMGAN "
            "checkpoint or evaluation"),
        "reported_precision": CANDIDATE_REPORTED_PRECISION,
        "reported_platform": CANDIDATE_REPORTED_PLATFORM,
        "reported_device_issue": CANDIDATE_REPORTED_DEVICE_ISSUE,
        "pinned_revision": None,
        "model_filename": None,
        "model_byte_count": None,
        "model_sha256": None,
        "runtime_version": None,
        "delegate": None,
        "android_target": None,
        "reported_input_sample_rate_hz": None,
        "reported_hop_samples": None,
        "reported_content_delay_samples": None,
        "geometry_documented": False,
        "source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "android_target_present": False,
        "conversion_parity_verified": False,
        "exact_numeric_output_present": False,
    }


def _external_artifacts() -> Dict[str, Any]:
    paths = {
        "source_checkout": "data/checkouts/CMGAN-LiteRT",
        "weights": "data/models/cmgan-litert",
        "runtime_env": "data/envs/litert",
        "adapter": "adapters/cmgan-litert",
        "caller_manifest": "data/manifests/cmgan-litert.json",
    }
    present = {key: (SOURCE_ROOT / path).exists()
               for key, path in paths.items()}
    return {
        "checked_paths": paths,
        "present": present,
        "any_present": any(present.values()),
        "status": "blocked",
        "note": ("Observed presence would not be runtime admission, conversion "
                 "parity, rights evidence or qualification."),
    }


def _boundary() -> Dict[str, bool]:
    return {
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "shared_build_or_ci_change": False,
        "ci_change": False,
        "processor_exposure": False,
        "adapter_json_added": False,
        "readiness_json_added": False,
        "asset_bundled": False,
        "weights_vendored": False,
        "native_engine_built": False,
        "sdk_data_dir_added": False,
        "audio_added": False,
        "corpus_added": False,
        "network_access": False,
    }


def _scope() -> Dict[str, bool]:
    return {
        "synthetic_only": True,
        "task_local_only": True,
        "real_corpus": False,
        "real_audio": False,
        "weights": False,
        "litert_runtime": False,
        "android_device": False,
        "conversion": False,
        "device_timing": False,
        "listening": False,
        "runtime_invocation": False,
        "network_access": False,
        "benchmark_claim": False,
        "release_claim": False,
        "numeric_parity_claim": False,
        "provider_registration": False,
        "processor_exposure": False,
        "public_default": False,
    }


NEGATIVE_CLAIMS = (
    "No CMGAN-LiteRT source, converted model, weight file, LiteRT runtime, "
    "delegate, Android target, adapter or numeric output was produced, "
    "downloaded, loaded, imported or executed.",
    "No CMGAN or LiteRT enhancement, quality, parity, latency, benchmark, "
    "listening or release result is claimed.",
    "The synthetic adaptive frame-energy suppressor is not CMGAN, not the "
    "community LiteRT port and cannot qualify the candidate.",
    "No candidate sample rate, hop, window, tensor layout, precision, "
    "content delay, lookahead or alignment is asserted.",
    "Synthetic SI-SDR, direct SNR, level change and envelope correlation are "
    "unqualified task-local observations only; they are not STOI or MOS.",
    "No real speech, corpus, clean reference, baseline run, device clock, "
    "listener or benchmark was used.",
    "No upstream license text, model-card terms, attribution bundle, "
    "training-data statement or conversion/derivative review is staged.",
    "No provider, descriptor, registry, installed v0 path, shared build, "
    "dependency lock or CI was changed.",
)

REOPEN_CONDITION = (
    "Pin the exact litert-community/CMGAN-LiteRT revision, converted model "
    "and LiteRT runtime with immutable hashes and a named Android target, "
    "clear code/weight/training-data/conversion/corpus rights, document exact "
    "I/O geometry and delay, reproduce numeric parity against an official "
    "CMGAN reference backend, qualify enhancement and preservation on a "
    "rights-cleared task-matched held-out cohort, measure target timing and "
    "listening, and complete opt-in provider intake. Until then the candidate "
    "stays DEFER, incomplete and not qualified."
)


def _matrix_digest(run: Dict[str, Any], streaming: Dict[str, Any],
                   reset: Dict[str, Any]) -> str:
    return object_digest({
        "signals": run["signal_digests"],
        "identity": (run["identity_metrics"]["si_sdr_millidb"],
                     run["identity_metrics"]["snr_millidb"]),
        "surrogate": (run["output_metrics"]["si_sdr_millidb"],
                      run["output_metrics"]["snr_millidb"]),
        "delta": (run["delta_si_sdr_millidb"], run["delta_snr_millidb"]),
        "streaming": streaming["all_match"],
        "reset": reset["state_digest"],
    })


def _fixtures(run: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "synthetic_only": True,
        "audio_generated": False,
        "geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
            "precision": PRECISION,
            "length_samples": FIXTURE_LENGTH,
            "duration_ns": FIXTURE_LENGTH * SAMPLE_NS,
            "active_end_sample": ACTIVE_END,
            "noise_amplitude": NOISE_AMPLITUDE,
            "voice_scale": VOICE_SCALE,
            "segments": [dict(segment) for segment in SEGMENTS],
        },
        "signal_digests": run["signal_digests"],
    }


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()
    run = enhancement_run()
    streaming = streaming_check(run)
    reset = reset_check()
    partial = final_partial_check()
    profile = _acceptance_profile()
    adverse = adverse_rejections()
    gates = _release_gates()
    blockers = _exact_blockers()
    matrix = _matrix_digest(run, streaming, reset)
    output_metrics = run["output_metrics"]
    identity_metrics = run["identity_metrics"]
    active_output = run["active_output_metrics"]

    report: Dict[str, Any] = {
        "schema_id": REPORT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "version": VERSION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "profile": PROFILE,
        "acceptance_profile": profile,
        "profile_blockers": _profile_blockers(profile),
        "candidate": _candidate(),
        "reference": {
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "implementation_present": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "license_identity": None,
            "pinned_revision": None,
            "status": "blocked",
            "surrogate_is_candidate": False,
        },
        "format": {
            "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "sdk_v0_channels": CHANNELS,
            "sdk_v0_frame_samples": FRAME_SAMPLES,
            "sdk_v0_sample_format": SAMPLE_FORMAT,
            "sdk_v0_precision": PRECISION,
            "candidate_reported_precision": CANDIDATE_REPORTED_PRECISION,
            "candidate_geometry_documented": False,
            "resampling": "none",
            "surrogate_algorithmic_latency_samples": 0,
            "surrogate_content_delay_samples": 0,
            "candidate_content_delay_samples": None,
        },
        "fixtures": _fixtures(run),
        "enhancement_profile": {
            "profile_source": (
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"),
            "required_items": profile["required_items"],
            "blockers": _profile_blockers(profile),
        },
        "identity_noisy_control": {
            "metrics": identity_metrics,
            "qualifies": False,
        },
        "surrogate_result": {
            "algorithm": ("bounded deterministic adaptive frame-energy "
                          "suppressor with per-frame gain ramp"),
            "is_cmgan": False,
            "is_litert": False,
            "is_learned": False,
            "uses_weights": False,
            "uses_stft": False,
            "uses_fp16": False,
            "metrics": output_metrics,
            "delta_si_sdr_millidb": run["delta_si_sdr_millidb"],
            "delta_snr_millidb": run["delta_snr_millidb"],
            "qualifies": False,
        },
        "clean_preservation": {
            "active_region": [0, ACTIVE_END],
            "identity": run["active_identity_metrics"],
            "surrogate": active_output,
            "envelope_correlation_millipoints_proxy": run[
                "envelope_correlation_millipoints"],
            "note": ("The envelope correlation is a task-local proxy, not "
                     "STOI, MOS or a listening result."),
            "qualifies": False,
        },
        "peaks_and_invalid_outputs": {
            "max_surrogate_peak_milli": output_metrics["peak_milli"],
            "max_identity_peak_milli": identity_metrics["peak_milli"],
            "nonfinite_output_count": output_metrics[
                "nonfinite_output_count"],
            "output_finite": output_metrics["nonfinite_output_count"] == 0,
            "nonfinite_inputs_rejected": sum(
                1 for case in adverse if "nonfinite_input" in case["code"]),
            "qualifies": False,
        },
        "stoi": {
            "status": "blocked_not_measured",
            "score": None,
            "scorer": None,
            "reason": ("No permitted STOI scorer was executed for this "
                       "candidate; synthetic envelope correlation is not "
                       "STOI."),
        },
        "task_matched_baseline": {
            "named_comparators": ["Official CMGAN", "FastEnhancer Small"],
            "status": "blocked_not_run",
            "result": None,
            "qualifies": False,
        },
        "alignment": {
            "surrogate_declared_delay_samples": 0,
            "candidate_declared_delay_samples": None,
            "measured": False,
            "qualifies": False,
        },
        "state_memory_timing": {
            "status": "blocked_unmeasured",
            "runtime_used": False,
            "device_used": False,
            "rtf": None,
            "peak_rss_bytes": None,
            "availability": None,
            "qualifies": False,
        },
        "unpaired_predictive_screen": {
            "status": "blocked_not_run",
            "result": None,
            "qualifies": False,
        },
        "listening": {
            "status": "blocked_not_run",
            "result": None,
            "qualifies": False,
        },
        "resource_usage": {
            "status": "blocked_unmeasured",
            "note": "No candidate runtime or device measurement exists.",
        },
        "final_partial": partial,
        "streaming": streaming,
        "reset": reset,
        "adverse_rejections": adverse,
        "adverse_all_rejected": all(
            row["status"] == "rejected" and row["state_unchanged"] is True
            for row in adverse),
        "external_artifacts": _external_artifacts(),
        "licensing": _licensing(),
        "caller_asset": {
            "contract_id": (
                "audio-sdk/cmgan-litert-community-port/"
                "caller-supplied-asset/0.1"),
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "manifest_present": False,
            "workspace_manifest": "data/manifests/cmgan-litert.json",
            "present_behavior": (
                "validate_identity_geometry_only; do_not_load_or_execute"),
            "absent_behavior": "reject_before_processing",
            "required_fields": sorted(CALLER_MANIFEST_FIELDS),
            "loaded": False,
            "executed": False,
            "imported": False,
            "status": "blocked",
        },
        "board_row": board_row(),
        "boundary": _boundary(),
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_pins": dict(SOURCE_PINS),
        "scope": _scope(),
        "qualification": {
            "status": QUALIFICATION,
            "qualifies": False,
            "all_required_results_present": False,
            "missing_result_promoted": False,
            "exact_source_present": False,
            "exact_weights_present": False,
            "exact_runtime_present": False,
            "android_target_present": False,
            "conversion_parity_verified": False,
            "rights_cleared_cohort": False,
            "geometry_documented": False,
            "baseline_run": False,
            "paired_si_sdr_on_real_data": False,
            "stoi_measured": False,
            "clean_preservation_measured_on_real_data": False,
            "timing_measured": False,
            "listening": False,
            "real_corpus_used": False,
            "reason": ("Exact port/model/runtime, Android target, conversion "
                       "parity, rights, documented geometry, rights-cleared "
                       "held-out data, timing, listening and independent "
                       "review are all absent."),
        },
        "exact_blockers": blockers,
        "release_gates": gates,
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "surrogate": {
            "algorithm": ("bounded deterministic adaptive frame-energy "
                          "suppressor with per-frame gain ramp"),
            "is_cmgan": False,
            "is_litert": False,
            "is_learned": False,
            "uses_weights": False,
            "uses_stft": False,
            "uses_fp16": False,
            "qualifies_candidate": False,
        },
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "case_matrix_digests": [matrix, matrix, matrix],
        },
        "scope_note": ("Only docs/task-evidence/cmgan-litert-community-port/ "
                       "is written; all other paths are read-only pins."),
    }
    return report


# ---------------------------------------------------------------------------
# Contract and manifest
# ---------------------------------------------------------------------------

def artifact_pins(artifacts: Dict[str, bytes]) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in CONTRACT_PIN_FILES:
        _require(name in artifacts, "missing_artifact:" + name)
        pins[TASK_PREFIX + name] = sha256_bytes(artifacts[name])
    return pins


def build_contract(report: Dict[str, Any], report_digest: str,
                   artifacts: Dict[str, bytes]) -> Dict[str, Any]:
    sidecar_digest = sha256_bytes(
        (report_digest + "  report.json\n").encode("ascii"))
    pins = artifact_pins(artifacts)
    _require(pins[TASK_PREFIX + "report.json"] == report_digest,
             "report_digest_mismatch")
    _require(pins[TASK_PREFIX + "report.json.sha256"] == sidecar_digest,
             "report_sidecar_digest_mismatch")
    return {
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "version": VERSION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "profile": PROFILE,
        "verification_profile": PROFILE,
        "task_prefix": TASK_PREFIX,
        "acceptance_profile": report["acceptance_profile"],
        "candidate": report["candidate"],
        "format": report["format"],
        "licensing": report["licensing"],
        "artifact_pins": pins,
        "board_row": report["board_row"],
        "boundary": report["boundary"],
        "boundary_pins": report["boundary_pins"],
        "source_pins": report["source_pins"],
        "scope": report["scope"],
        "reference": report["reference"],
        "exact_blockers": report["exact_blockers"],
        "release_gates": report["release_gates"],
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": report["negative_claims"],
        "caller_asset_contract": {
            "contract_id": (
                "audio-sdk/cmgan-litert-community-port/"
                "caller-supplied-asset/0.1"),
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "required_fields": sorted(CALLER_MANIFEST_FIELDS),
            "present_behavior": (
                "validate_identity_geometry_only; do_not_load_or_execute"),
            "absent_behavior": "reject_before_processing",
            "separate_archive_required": True,
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no CMGAN-LiteRT source, model, weight, LiteRT runtime, delegate, "
            "Android target or adapter is downloaded, copied, loaded, "
            "imported or executed",
            "the synthetic adaptive suppressor is not CMGAN or LiteRT and "
            "cannot qualify the candidate",
            "no candidate rate, hop, window, tensor layout, precision, delay "
            "or alignment is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def sources_bytes(overrides: Dict[str, bytes] | None = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-CMGAN-LITERT-COMMUNITY-PORT; source: paths "
        "are workspace-relative, worktree: is SDK-worktree-relative."
    ]
    pins: Dict[str, str] = {}
    for path, digest in SOURCE_PINS.items():
        pins["source:" + path] = digest
    for path, digest in BOUNDARY_PINS.items():
        pins["worktree:" + path] = digest
    for name in LOCAL_PIN_FILES:
        key = "worktree:" + TASK_PREFIX + name
        if name in overrides:
            digest = sha256_bytes(overrides[name])
        else:
            full = TASK_DIR / name
            _require(full.is_file(), "missing_artifact:" + name)
            digest = file_digest(full)
        pins[key] = digest
    _require("worktree:" + TASK_PREFIX + "SOURCES.sha256" not in pins,
             "manifest_self_pin")
    for key in sorted(pins):
        lines.append(f"{pins[key]}  {key}")
    return ("\n".join(lines) + "\n").encode("utf-8")


__all__ = [
    "AdaptiveEnergySuppressor", "ReferenceRejection", "SEGMENTS",
    "adverse_rejections", "artifact_pins", "board_row", "build_contract",
    "build_fixture", "build_report", "canonical_report", "canonical_text",
    "chunk_plan", "enhancement_run", "final_partial_check", "fixture_spec",
    "int_signal_digest", "load_strict_json", "load_strict_json_text",
    "object_digest", "reset_check", "run_stream", "sha256_bytes",
    "signal_digest", "sources_bytes", "streaming_check",
    "validate_caller_manifest", "validate_config", "validate_fixture",
]
