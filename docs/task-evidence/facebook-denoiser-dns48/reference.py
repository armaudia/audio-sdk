# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local reference for SDK-FACEBOOK-DENOISER-DNS48.

The exact licensed Facebook Denoiser ``dns48`` source tree, pretrained weight
files, PyTorch inference runtime and numeric output are absent, and the pinned
census records a CC-BY-NC 4.0 research-only licence for the repository and
models. This module therefore implements **no** Demucs layer, convolution,
weight tensor, PyTorch graph or Facebook Denoiser code path. It provides:

* strict fail-closed JSON/config/frame/manifest/use-scope parsers;
* a frozen synthetic 16 kHz mono paired clean/noisy fixture;
* a bounded integer-only ``CausalTwoWindowGateSurrogate`` used solely to
  exercise frame accounting, rejection and determinism mechanics;
* exact integer paired SI-SDR / SNR metrics (STOI is never computed);
* deterministic report and contract builders.

Nothing here reads audio, a weight file, a source tree or a runtime. Nothing
here is a candidate result. All evidence is task-local, synthetic and
unqualified. Facebook Denoiser ``dns48`` is a causal waveform Demucs model; the
surrogate is a frame-accounting fixture and is not a Demucs model, a streaming
claim, a latency claim or a licence conclusion.
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
REPORT_SCHEMA = "audio-sdk/facebook-denoiser-dns48-report/0.1"
TASK_ID = "SDK-FACEBOOK-DENOISER-DNS48"
TITLE = "Facebook Denoiser DNS48"
COMPONENT = "facebook-denoiser-dns48"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "9cf118bc32ff5ac801318158d97d5bb8dd947374"
BRANCH = "swarm/SDK-FACEBOOK-DENOISER-DNS48"
REVIEWER = "reviewer-FACEBOOK-DENOISER-DNS48"
PROFILE = "enhancement"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
STATUS = "proposal_only_synthetic_incomplete"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
HALF_FRAME = 80
SAMPLE_FORMAT = "float32"
SAMPLE_NS = 62500
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS

FIXTURE_LENGTH = 12000
Q15 = 32768
MAX_Q15 = 32767
MIN_Q15 = -32768

# Frozen surrogate constants (fixture-tuned, unqualified).
GATE_THRESHOLD_Q15 = 700
GAIN_FLOOR_MILLI = 250
MAX_MILLIDB = 999000
MIN_MILLIDB = -999000

CANDIDATE_HIDDEN_CHANNELS = 48
CANDIDATE_REPORTED_SAMPLE_RATE_HZ = 16000
CANDIDATE_REPORTED_ARTIFACT = "dns48"
CANDIDATE_REPORTED_LICENSE = "CC-BY-NC-4.0"
CANDIDATE_REPORTED_RUNTIME = (
    "Official archived PyTorch repository (census; not staged)"
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
    {"name": "clean_only_initial", "start": 0, "end": 2400,
     "speech": True, "noise_amplitude": 10},
    {"name": "noisy_speech", "start": 2400, "end": 4800,
     "speech": True, "noise_amplitude": 700},
    {"name": "noisy_speech_low_snr", "start": 4800, "end": 7200,
     "speech": True, "noise_amplitude": 2600},
    {"name": "noise_only_pause", "start": 7200, "end": 8400,
     "speech": False, "noise_amplitude": 1000},
    {"name": "clean_only_final", "start": 8400, "end": 9600,
     "speech": True, "noise_amplitude": 10},
    {"name": "noisy_speech_restore", "start": 9600, "end": 12000,
     "speech": True, "noise_amplitude": 1600},
)
SEGMENT_KEYS = {"name", "start", "end", "speech", "noise_amplitude"}
NOISY_REGIONS = ("noisy_speech", "noisy_speech_low_snr",
                 "noisy_speech_restore")
CLEAN_REGIONS = ("clean_only_initial", "clean_only_final")
PAUSE_REGION = ("noise_only_pause", 7200, 8400)
ALIGNMENT_REGION = ("clean_only_initial", 0, 2400)
ALIGNMENT_SHIFTS = (-16, -8, 0, 8, 16)
FINAL_PARTIAL_VALID = 137

SOURCE_PINS = {
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
    "docs/task-evidence/rnnoise-v0-2/README.md": (
        "d9b83840d67862ab1a196e3096aab64f1d1bf83c18411a06c0c1d62142e1eb74"
    ),
    "docs/task-evidence/rnnoise-v0-2/report.json": (
        "f635f1fcd7adbbc969ad99fe8445cb7188dcd733d3dcf1166a668de8b3085ec5"
    ),
    "docs/task-evidence/gtcrn-dns3-offline/report.json": (
        "b4768c1ee3b6f9934c576496a9f224a7293edc2c09993b11892c03535b8557bd"
    ),
    "docs/task-evidence/dasheng-denoiser/report.json": (
        "cdb85350b4f5d6ccc771813f72be1291049397678151f572127e768297045984"
    ),
    "docs/task-evidence/deepvqe-dns3-noise-suppression-configuration/"
    "report.json": (
        "b5c5eef3f22d39bf8ceea9a177b7d5d6b194ef21326a56742fe69c489e5b3455"
    ),
}

BOARD_ROW_STABLE_SHA256 = (
    "e7cd63d2e6c8016836a18c082c14b8eda79d3864a25ba6cef5d750803ebbcc15"
)

TASK_PREFIX = "docs/task-evidence/facebook-denoiser-dns48/"
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
PIN_FILES: Tuple[str, ...] = ARTIFACT_FILES + ("contract.json",)


class ReferenceRejection(ValueError):
    """Deterministic, machine-readable rejection; no state is advanced."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


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


def _energy(samples: Sequence[int], start: int, end: int) -> int:
    total = 0
    for index in range(start, end):
        value = int(samples[index])
        total += value * value
    return total


def _millidb(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        return MAX_MILLIDB
    if numerator <= 0:
        return MIN_MILLIDB
    value = 10000.0 * (math.log10(numerator) - math.log10(denominator))
    return int(round(value))


def snr_millidb(reference: Sequence[int], estimate: Sequence[int],
                start: int, end: int) -> int:
    signal_energy = _energy(reference, start, end)
    error = 0
    for index in range(start, end):
        difference = int(estimate[index]) - int(reference[index])
        error += difference * difference
    return _millidb(signal_energy, error)


def si_sdr_millidb(reference: Sequence[int], estimate: Sequence[int],
                   start: int, end: int) -> int:
    """Exact integer scale-invariant SDR in millidB.

    SI-SDR = 10*log10(num^2 / (sum(est^2)*sum(ref^2) - num^2)) with
    num = <est, ref>; the logarithm is applied only after exact integer work.
    """
    residual = _energy(reference, start, end)
    if residual <= 0:
        return MIN_MILLIDB
    estimate_energy = _energy(estimate, start, end)
    cross = 0
    for index in range(start, end):
        cross += int(reference[index]) * int(estimate[index])
    target = cross * cross
    error = estimate_energy * residual - target
    return _millidb(target, error)


# ---------------------------------------------------------------------------
# Frozen synthetic fixture (authored clean reference + deterministic noise)
# ---------------------------------------------------------------------------

FIXTURE_KEYS = {"length_samples", "segments"}


def fixture_spec() -> Dict[str, Any]:
    return {
        "length_samples": FIXTURE_LENGTH,
        "segments": [dict(segment) for segment in SEGMENTS],
    }


def validate_fixture(spec: Dict[str, Any]) -> None:
    _exact_keys(spec, FIXTURE_KEYS, "fixture")
    length = _integer(spec["length_samples"], "length_samples", 160, 200000)
    _require(length == FIXTURE_LENGTH, "fixture_length_mismatch")
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
        _require(isinstance(segment["speech"], bool), "invalid_speech_flag")
        _integer(segment["noise_amplitude"], "noise_amplitude", 0, 4000)
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
    envelope = (3000, 2800, 2400, 1800, 1200, 0, 0, 1400, 2200, 3000)
    values: List[int] = []
    for index in range(count):
        tone = (3 * SINE64[index % 64]
                + 2 * SINE64[(2 * index + 7) % 64]
                + SINE64[(3 * index + 13) % 64]) // 6
        level = envelope[(index // FRAME_SAMPLES) % len(envelope)]
        values.append(tone * level * 8000 // (32767 * 3000))
    return values


def _segment_masks(length: int) -> Tuple[List[bool], List[int]]:
    speech = [False] * length
    noise = [0] * length
    for segment in SEGMENTS:
        for index in range(segment["start"], segment["end"]):
            speech[index] = bool(segment["speech"])
            noise[index] = int(segment["noise_amplitude"])
    return speech, noise


def build_fixture() -> Dict[str, Any]:
    """Build the frozen synthetic paired clean/noisy signals (Q15 integers)."""
    validate_fixture(fixture_spec())
    speech_mask, noise_levels = _segment_masks(FIXTURE_LENGTH)
    clean = [value if speech_mask[index] else 0
             for index, value in enumerate(_voice_values(FIXTURE_LENGTH))]
    noise_base = _lcg_values(20261127, FIXTURE_LENGTH)
    noise = [noise_base[index] * noise_levels[index] // 32767
             for index in range(FIXTURE_LENGTH)]
    mic = [max(MIN_Q15, min(MAX_Q15, clean[index] + noise[index]))
           for index in range(FIXTURE_LENGTH)]
    return {"clean": clean, "noise": noise, "mic": mic}


def _region(name: str) -> Tuple[int, int]:
    for segment in SEGMENTS:
        if segment["name"] == name:
            return int(segment["start"]), int(segment["end"])
    raise ReferenceRejection("unknown_region:" + name)


# ---------------------------------------------------------------------------
# Bounded causal dual-window integer gate (NOT Facebook Denoiser / Demucs)
# ---------------------------------------------------------------------------

CONFIG_KEYS = {"sample_rate_hz", "channels", "frame_samples", "sample_format",
               "clock_ppm", "resampling", "algorithmic_latency_samples"}


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
    return {"sample_rate_hz": rate, "channels": channels,
            "frame_samples": frame, "sample_format": config["sample_format"],
            "clock_ppm": clock, "resampling": config["resampling"],
            "algorithmic_latency_samples": latency}


def quantize(value: object, label: str = "input") -> int:
    """Strict float32-boundary sample to exact Q15 integer."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceRejection("invalid_sample:" + label)
    number = float(value)
    if not math.isfinite(number):
        raise ReferenceRejection("nonfinite_input:" + label)
    if number < -1.0 or number > 1.0:
        raise ReferenceRejection("sample_out_of_range:" + label)
    scaled = int(number * Q15)
    return MAX_Q15 if scaled > MAX_Q15 else scaled


def _validate_frame(values: object, valid_count: object) -> List[int]:
    count = _integer(valid_count, "valid_count", 1, FRAME_SAMPLES)
    if values is None:
        raise ReferenceRejection("missing_input")
    if not isinstance(values, (list, tuple)):
        raise ReferenceRejection("invalid_frame:input")
    if len(values) != FRAME_SAMPLES:
        raise ReferenceRejection("frame_count_mismatch:input")
    quantized: List[int] = []
    for index in range(count):
        quantized.append(quantize(values[index]))
    for index in range(count, FRAME_SAMPLES):
        value = values[index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceRejection("invalid_sample:input")
        if float(value) != 0.0:
            raise ReferenceRejection("padding_not_zero:input")
        quantized.append(0)
    return quantized


class CausalTwoWindowGateSurrogate:
    """Bounded causal integer frame gate with a frozen two-level gain.

    Each 160-sample frame is split into two contiguous half-windows. The
    larger integer mean magnitude selects gain 1000 per mille at or above the
    frozen 700 Q15 threshold and gain 250 below it. No future frame, learned
    weight, convolution, Demucs layer or PyTorch graph is used.

    This is a boundary-accounting fixture, not Facebook Denoiser ``dns48`` and
    not a streaming, latency or quality claim for the candidate.
    """

    def __init__(self, sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = CHANNELS, frame_samples: int = FRAME_SAMPLES,
                 sample_format: str = SAMPLE_FORMAT, epoch: int = 1):
        if (sample_rate_hz != SAMPLE_RATE_HZ or channels != CHANNELS
                or frame_samples != FRAME_SAMPLES
                or sample_format != SAMPLE_FORMAT):
            raise ReferenceRejection(
                "unsupported_config", "v0 accepts only 16000/1/160/float32")
        if (not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1):
            raise ReferenceRejection("invalid_epoch")
        self.epoch = epoch
        self.position = 0
        self.frames = 0
        self.gain_previous = 1000

    @property
    def state_bytes(self) -> int:
        return 28

    @property
    def state_digest(self) -> str:
        payload = struct.pack("<qqqi", self.epoch, self.position,
                              self.frames, self.gain_previous)
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
        self.gain_previous = 1000

    def process_frame(self, values: Sequence[float] | None,
                      valid_count: int = FRAME_SAMPLES,
                      epoch: int | None = None,
                      first_input_sample: int | None = None
                      ) -> Tuple[List[float], List[int]]:
        """Return (float32-boundary output, exact Q15 output); 160 each."""
        quantized = _validate_frame(values, valid_count)
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

        left_count = valid_count // 2
        right_count = valid_count - left_count
        left_energy = sum(abs(value) for value in quantized[:left_count])
        right_energy = sum(abs(value)
                           for value in quantized[left_count:valid_count])
        left_mean = left_energy // left_count if left_count else 0
        right_mean = right_energy // right_count if right_count else 0
        level = max(left_mean, right_mean)
        gain = (1000 if level >= GATE_THRESHOLD_Q15
                else GAIN_FLOOR_MILLI)
        self.gain_previous = gain
        output_q15 = [quantized[index] * gain // 1000
                      for index in range(valid_count)]
        self.position += valid_count
        self.frames += 1
        output_q15.extend([0] * (FRAME_SAMPLES - valid_count))
        output_float = [value / Q15 for value in output_q15]
        return output_float, output_q15


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


def run_stream(mic: Sequence[int], chunks: Sequence[int] | None = None,
               epoch: int = 1) -> Dict[str, Any]:
    surrogate = CausalTwoWindowGateSurrogate(epoch=epoch)
    plan = list(chunks) if chunks is not None else chunk_plan(len(mic))
    _require(sum(plan) == len(mic), "chunk_sum_mismatch")
    output_q15: List[int] = []
    output_float: List[float] = []
    offset = 0
    for chunk in plan:
        _require(chunk > 0, "invalid_chunk")
        chunk_end = offset + chunk
        while offset < chunk_end:
            size = min(FRAME_SAMPLES, chunk_end - offset)
            frame = [mic[index] / Q15
                     for index in range(offset, offset + size)]
            frame.extend([0.0] * (FRAME_SAMPLES - size))
            values, quantized = surrogate.process_frame(
                frame, valid_count=size)
            output_float.extend(values[:size])
            output_q15.extend(quantized[:size])
            offset += size
    return {"output": output_float, "q15": output_q15,
            "state_digest": surrogate.state_digest,
            "samples": len(output_q15)}


def _shift(values: Sequence[int], shift: int) -> List[int]:
    length = len(values)
    result = [0] * length
    for index in range(length):
        source = index - shift
        if 0 <= source < length:
            result[index] = int(values[source])
    return result


def _peak_milli(values: Sequence[int]) -> int:
    peak = 0
    for value in values:
        magnitude = abs(int(value))
        if magnitude > peak:
            peak = magnitude
    return peak * 1000 // Q15


def _finite_count(values: Sequence[float]) -> int:
    return sum(0 if math.isfinite(value) else 1 for value in values)


def fixture_run(epoch: int = 1,
                chunks: Sequence[int] | None = None) -> Dict[str, Any]:
    signals = build_fixture()
    run = run_stream(signals["mic"], chunks=chunks, epoch=epoch)
    noisy_rows = []
    for name in NOISY_REGIONS:
        start, end = _region(name)
        identity_si_sdr = si_sdr_millidb(signals["clean"], signals["mic"],
                                         start, end)
        surrogate_si_sdr = si_sdr_millidb(signals["clean"], run["q15"],
                                          start, end)
        identity_snr = snr_millidb(signals["clean"], signals["mic"],
                                   start, end)
        surrogate_snr = snr_millidb(signals["clean"], run["q15"],
                                    start, end)
        noisy_rows.append({
            "segment": name,
            "start": start,
            "end": end,
            "identity_si_sdr_millidb": identity_si_sdr,
            "surrogate_si_sdr_millidb": surrogate_si_sdr,
            "delta_si_sdr_millidb": surrogate_si_sdr - identity_si_sdr,
            "identity_snr_millidb": identity_snr,
            "surrogate_snr_millidb": surrogate_snr,
            "delta_snr_millidb": surrogate_snr - identity_snr,
            "qualifies": False,
        })
    clean_rows = []
    for name in CLEAN_REGIONS:
        start, end = _region(name)
        clean_rows.append({
            "segment": name,
            "start": start,
            "end": end,
            "si_sdr_millidb": si_sdr_millidb(signals["clean"], run["q15"],
                                             start, end),
            "snr_millidb": snr_millidb(signals["clean"], run["q15"],
                                       start, end),
            "level_change_millidb": _millidb(
                _energy(run["q15"], start, end),
                _energy(signals["clean"], start, end)),
            "peak_milli": _peak_milli(run["q15"][start:end]),
            "qualifies": False,
        })
    pause_start, pause_end = PAUSE_REGION[1], PAUSE_REGION[2]
    return {
        "signals": signals,
        "run": run,
        "noisy_regions": noisy_rows,
        "clean_regions": clean_rows,
        "pause": {
            "segment": PAUSE_REGION[0],
            "start": pause_start,
            "end": pause_end,
            "input_mic_energy": _energy(signals["mic"], pause_start,
                                        pause_end),
            "output_energy": _energy(run["q15"], pause_start, pause_end),
            "noise_attenuation_millidb": _millidb(
                _energy(signals["mic"], pause_start, pause_end),
                _energy(run["q15"], pause_start, pause_end)),
            "qualifies": False,
        },
        "signal_digests": {
            "clean": int_signal_digest(signals["clean"]),
            "noise": int_signal_digest(signals["noise"]),
            "mic": int_signal_digest(signals["mic"]),
            "output": int_signal_digest(run["q15"]),
        },
        "overall": {
            "max_peak_milli": _peak_milli(run["q15"]),
            "nonfinite_output_count": _finite_count(run["output"]),
        },
    }


def alignment_run() -> Dict[str, Any]:
    signals = build_fixture()
    run = run_stream(signals["mic"])
    name, start, end = ALIGNMENT_REGION
    probes = []
    for shift in ALIGNMENT_SHIFTS:
        shifted = _shift(signals["clean"], shift)
        probes.append({
            "shift_samples": shift,
            "si_sdr_millidb": si_sdr_millidb(shifted, run["q15"],
                                             start, end),
        })
    best = max(probes, key=lambda row: row["si_sdr_millidb"])
    return {
        "region": name,
        "status": "synthetic_surrogate_only",
        "candidate_streaming_reported": True,
        "candidate_alignment_documented": False,
        "surrogate_content_delay_samples": 0,
        "probes": probes,
        "best_shift_samples": best["shift_samples"],
        "zero_shift_best": best["shift_samples"] == 0,
        "qualifies": False,
    }


def streaming_check(offline: Dict[str, Any]) -> Dict[str, Any]:
    signals = offline["signals"]
    plan = chunk_plan(FIXTURE_LENGTH)
    streamed = run_stream(signals["mic"], chunks=plan)
    return {
        "status": "synthetic_surrogate_only",
        "chunks": plan,
        "accepted_samples": FIXTURE_LENGTH,
        "all_match": streamed["q15"] == offline["run"]["q15"],
        "offline_state_digest": offline["run"]["state_digest"],
        "streamed_state_digest": streamed["state_digest"],
        "scheduler_measured": False,
        "candidate_streaming": False,
        "candidate_streaming_reported": True,
        "qualifies": False,
    }


def reset_check() -> Dict[str, Any]:
    signals = build_fixture()
    probe_length = ALIGNMENT_REGION[2]
    mic = signals["mic"][:probe_length]
    carried = CausalTwoWindowGateSurrogate(epoch=1)
    offset = 0
    while offset < len(mic):
        frame = [mic[index] / Q15
                 for index in range(offset, min(offset + FRAME_SAMPLES,
                                                len(mic)))]
        count = len(frame)
        frame.extend([0.0] * (FRAME_SAMPLES - count))
        carried.process_frame(frame, valid_count=count)
        offset += FRAME_SAMPLES
    carried.reset(2, 0)
    offset = 0
    while offset < len(mic):
        frame = [mic[index] / Q15
                 for index in range(offset, min(offset + FRAME_SAMPLES,
                                                len(mic)))]
        count = len(frame)
        frame.extend([0.0] * (FRAME_SAMPLES - count))
        carried.process_frame(frame, valid_count=count, epoch=2)
        offset += FRAME_SAMPLES
    fresh = run_stream(mic, epoch=2)
    return {
        "status": "synthetic_surrogate_only",
        "epoch": 2,
        "accepted_samples": len(mic),
        "matches_fresh": carried.state_digest == fresh["state_digest"],
        "state_digest": carried.state_digest,
        "qualifies": False,
    }


def final_partial_check() -> Dict[str, Any]:
    signals = build_fixture()
    carrier = CausalTwoWindowGateSurrogate(epoch=1)
    frame = [signals["mic"][index] / Q15
             for index in range(FINAL_PARTIAL_VALID)]
    frame.extend([0.0] * (FRAME_SAMPLES - FINAL_PARTIAL_VALID))
    values, quantized = carrier.process_frame(
        frame, valid_count=FINAL_PARTIAL_VALID)
    return {
        "status": "synthetic_surrogate_only",
        "valid_count": FINAL_PARTIAL_VALID,
        "padding_zero": True,
        "output_samples": len(quantized),
        "advanced_samples": carrier.position,
        "tail_zero": all(value == 0 for value in quantized[
            FINAL_PARTIAL_VALID:]),
        "nonfinite_output_count": _finite_count(values),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied asset identity and use-scope (never loaded or executed)
# ---------------------------------------------------------------------------

CALLER_MANIFEST_FIELDS = {
    "adapter",
    "algorithmic_latency_samples",
    "artifact_format",
    "channels",
    "frame_samples",
    "input_format",
    "library_path",
    "library_sha256",
    "model_path",
    "model_sha256",
    "precision",
    "sample_rate_hz",
    "source_commit",
    "source_sha256",
    "variant",
    "weights_sha256",
}
ARTIFACT_FORMATS = {"pytorch"}
PRECISIONS = {"fp32", "fp16", "bf16"}
PERMITTED_USE_SCOPES = {"research_evaluation"}


def validate_caller_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    _exact_keys(manifest, CALLER_MANIFEST_FIELDS, "caller_manifest")
    _string(manifest["adapter"], "adapter", 1, 64)
    _string(manifest["variant"], "variant", 1, 64)
    _string(manifest["artifact_format"], "artifact_format", 1, 16)
    _string(manifest["precision"], "precision", 1, 16)
    rate = _integer(manifest["sample_rate_hz"], "sample_rate_hz", 1, 384000)
    channels = _integer(manifest["channels"], "channels", 1, 8)
    frame = _integer(manifest["frame_samples"], "frame_samples", 1, 4096)
    _integer(manifest["algorithmic_latency_samples"],
             "algorithmic_latency_samples", 0, 16000)
    _require(isinstance(manifest["input_format"], str),
             "invalid_input_format")
    if rate != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_sample_rate")
    if channels != CHANNELS:
        raise ReferenceRejection("unsupported_channels")
    if frame != FRAME_SAMPLES:
        raise ReferenceRejection("unsupported_frame_samples")
    if manifest["input_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("unsupported_sample_format")
    if manifest["artifact_format"] not in ARTIFACT_FORMATS:
        raise ReferenceRejection("unsupported_artifact_format")
    if manifest["precision"] not in PRECISIONS:
        raise ReferenceRejection("unsupported_precision")
    _absolute_path(manifest["model_path"], "model_path")
    _absolute_path(manifest["library_path"], "library_path")
    _sha256(manifest["model_sha256"], "model_sha256")
    _sha256(manifest["weights_sha256"], "weights_sha256")
    _sha256(manifest["source_sha256"], "source_sha256")
    _sha256(manifest["library_sha256"], "library_sha256")
    _commit(manifest["source_commit"], "source_commit")
    return {"validated": True, "loaded": False, "executed": False,
            "imported": False}


def validate_use_scope(scope: object) -> str:
    """Fail closed on any scope outside research evaluation.

    The pinned census records CC-BY-NC 4.0 for the repository and models; no
    product, commercial or redistribution scope is permitted by this package.
    """
    if not isinstance(scope, str):
        raise ReferenceRejection("invalid_use_scope")
    if scope not in PERMITTED_USE_SCOPES:
        raise ReferenceRejection("license_scope_not_permitted")
    return scope


# ---------------------------------------------------------------------------
# Adverse rejection matrix and valid controls
# ---------------------------------------------------------------------------

def _base_config() -> Dict[str, Any]:
    return {"sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES, "sample_format": SAMPLE_FORMAT,
            "clock_ppm": 0, "resampling": "none",
            "algorithmic_latency_samples": 0}


def _base_manifest() -> Dict[str, Any]:
    return {
        "adapter": "facebook-denoiser-dns48-reference",
        "algorithmic_latency_samples": 0,
        "artifact_format": "pytorch",
        "channels": 1,
        "frame_samples": 160,
        "input_format": "float32",
        "library_path": "/caller/facebook-denoiser-dns48/lib",
        "library_sha256": "3" * 64,
        "model_path": "/caller/facebook-denoiser-dns48/dns48.th",
        "model_sha256": "0" * 64,
        "precision": "fp32",
        "sample_rate_hz": 16000,
        "source_commit": "0" * 40,
        "source_sha256": "1" * 64,
        "variant": "dns48",
        "weights_sha256": "2" * 64,
    }


def _valid_frame() -> List[float]:
    return [0.0] * FRAME_SAMPLES


def _expect_reject(expected: str, action) -> str:
    try:
        action()
    except ReferenceRejection as error:
        return error.code
    except ValueError as error:
        return str(error)
    return "accepted"


def adverse_rejections() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    gate = CausalTwoWindowGateSurrogate(epoch=1)

    def add(case_id: str, expected: str, action,
            state_probe=None) -> None:
        before = state_probe() if state_probe is not None else None
        actual = _expect_reject(expected, action)
        after = state_probe() if state_probe is not None else None
        cases.append({
            "case_id": case_id,
            "expected_code": expected,
            "observed_code": actual,
            "status": "rejected" if actual == expected
            else "unexpected_acceptance",
            "state_unchanged": before == after,
        })

    def config(mutator) -> None:
        candidate = _base_config()
        mutator(candidate)
        validate_config(candidate)

    def frame(mutator) -> None:
        values = _valid_frame()
        count = [FRAME_SAMPLES]
        mutator(values, count)
        gate.process_frame(values, valid_count=count[0])

    def manifest(mutator) -> None:
        candidate = _base_manifest()
        mutator(candidate)
        validate_caller_manifest(candidate)

    # Strict JSON parsing.
    add("duplicate_json_key", "duplicate_json_key:x",
        lambda: load_strict_json_text('{"x":1,"x":2}'))
    add("nonfinite_json_nan", "nonfinite_json_constant:NaN",
        lambda: load_strict_json_text('{"x":NaN}'))
    add("nonfinite_json_infinity", "nonfinite_json_constant:Infinity",
        lambda: load_strict_json_text('{"x":Infinity}'))
    add("malformed_json", "invalid_json",
        lambda: load_strict_json_text('{"x":'))
    add("json_root_not_object", "json_not_object",
        lambda: load_strict_json_text("[1,2]"))

    # Configuration.
    add("config_missing_field", "strict_keys_mismatch:config:clock_ppm",
        lambda: config(lambda c: c.pop("clock_ppm")))
    add("config_extra_field", "strict_keys_mismatch:config:extra",
        lambda: config(lambda c: c.update(extra=1)))
    add("config_8k", "unsupported_sample_rate",
        lambda: config(lambda c: c.update(sample_rate_hz=8000)))
    add("config_44k1", "unsupported_sample_rate",
        lambda: config(lambda c: c.update(sample_rate_hz=44100)))
    add("config_stereo", "unsupported_channels",
        lambda: config(lambda c: c.update(channels=2)))
    add("config_256_frame", "unsupported_frame_samples",
        lambda: config(lambda c: c.update(frame_samples=256)))
    add("config_int16", "unsupported_sample_format",
        lambda: config(lambda c: c.update(sample_format="int16")))
    add("config_clock_drift", "unsupported_clock_drift",
        lambda: config(lambda c: c.update(clock_ppm=100)))
    add("config_linear_resampling", "unsupported_resampling",
        lambda: config(lambda c: c.update(resampling="linear")))
    add("config_negative_latency", "invalid_integer:algorithmic_latency_samples",
        lambda: config(lambda c: c.update(algorithmic_latency_samples=-1)))
    add("config_oversized_latency", "invalid_integer:algorithmic_latency_samples",
        lambda: config(lambda c: c.update(algorithmic_latency_samples=16001)))
    add("config_boolean_rate", "invalid_integer:sample_rate_hz",
        lambda: config(lambda c: c.update(sample_rate_hz=True)))
    add("config_oversized_rate", "invalid_integer:sample_rate_hz",
        lambda: config(lambda c: c.update(sample_rate_hz=999999)))

    # Frames and streaming state.
    add("frame_missing_input", "missing_input",
        lambda: gate.process_frame(None), lambda: gate.state_digest)
    add("frame_short", "frame_count_mismatch:input",
        lambda: gate.process_frame(_valid_frame()[:-1]),
        lambda: gate.state_digest)
    add("frame_long", "frame_count_mismatch:input",
        lambda: gate.process_frame(_valid_frame() + [0.0]),
        lambda: gate.state_digest)
    add("frame_zero_valid_count", "invalid_integer:valid_count",
        lambda: gate.process_frame(_valid_frame(), valid_count=0),
        lambda: gate.state_digest)
    add("frame_oversized_valid_count", "invalid_integer:valid_count",
        lambda: gate.process_frame(_valid_frame(), valid_count=161),
        lambda: gate.state_digest)
    add("frame_nan_sample", "nonfinite_input:input",
        lambda: frame(lambda v, c: v.__setitem__(0, float("nan"))),
        lambda: gate.state_digest)
    add("frame_infinity_sample", "nonfinite_input:input",
        lambda: frame(lambda v, c: v.__setitem__(0, float("inf"))),
        lambda: gate.state_digest)
    add("frame_out_of_range", "sample_out_of_range:input",
        lambda: frame(lambda v, c: v.__setitem__(0, 1.5)),
        lambda: gate.state_digest)
    add("frame_string_sample", "invalid_sample:input",
        lambda: frame(lambda v, c: v.__setitem__(0, "0.0")),
        lambda: gate.state_digest)
    add("frame_boolean_sample", "invalid_sample:input",
        lambda: frame(lambda v, c: v.__setitem__(0, True)),
        lambda: gate.state_digest)
    add("frame_nonzero_padding", "padding_not_zero:input",
        lambda: frame(lambda v, c: (c.__setitem__(0, 159),
                                    v.__setitem__(159, 0.5))),
        lambda: gate.state_digest)
    add("frame_epoch_mismatch", "epoch_mismatch",
        lambda: gate.process_frame(_valid_frame(), epoch=2),
        lambda: gate.state_digest)
    add("frame_position_mismatch", "input_position_mismatch",
        lambda: gate.process_frame(_valid_frame(), first_input_sample=1),
        lambda: gate.state_digest)

    # Reset.
    add("reset_epoch_zero", "invalid_epoch",
        lambda: gate.reset(0, 0), lambda: gate.state_digest)
    add("reset_epoch_equal", "invalid_epoch",
        lambda: gate.reset(1, 0), lambda: gate.state_digest)
    add("reset_negative_position", "invalid_first_input_sample",
        lambda: gate.reset(2, -1), lambda: gate.state_digest)
    add("reset_boolean_epoch", "invalid_epoch",
        lambda: gate.reset(True, 0), lambda: gate.state_digest)

    # Caller-supplied manifest identity and geometry.
    add("manifest_missing_field", "strict_keys_mismatch:caller_manifest:variant",
        lambda: manifest(lambda m: m.pop("variant")))
    add("manifest_extra_field", "strict_keys_mismatch:caller_manifest:extra",
        lambda: manifest(lambda m: m.update(extra=1)))
    add("manifest_wrong_rate", "unsupported_sample_rate",
        lambda: manifest(lambda m: m.update(sample_rate_hz=48000)))
    add("manifest_wrong_channels", "unsupported_channels",
        lambda: manifest(lambda m: m.update(channels=2)))
    add("manifest_wrong_frame", "unsupported_frame_samples",
        lambda: manifest(lambda m: m.update(frame_samples=320)))
    add("manifest_tensorflow_format", "unsupported_artifact_format",
        lambda: manifest(lambda m: m.update(artifact_format="tensorflow")))
    add("manifest_fp8_precision", "unsupported_precision",
        lambda: manifest(lambda m: m.update(precision="fp8")))
    add("manifest_relative_model_path", "invalid_source_path:model_path",
        lambda: manifest(lambda m: m.update(model_path="dns48.th")))
    add("manifest_relative_library_path", "invalid_source_path:library_path",
        lambda: manifest(lambda m: m.update(library_path="lib")))
    add("manifest_bad_model_hash", "invalid_sha256:model_sha256",
        lambda: manifest(lambda m: m.update(model_sha256="z" * 64)))
    add("manifest_bad_commit", "invalid_string:source_commit",
        lambda: manifest(lambda m: m.update(source_commit="x" * 40)))

    # Rights scope: CC-BY-NC 4.0 is research evaluation only here.
    add("scope_commercial_product", "license_scope_not_permitted",
        lambda: validate_use_scope("commercial_product"))
    add("scope_product_distribution", "license_scope_not_permitted",
        lambda: validate_use_scope("product_distribution"))
    add("scope_missing", "invalid_use_scope",
        lambda: validate_use_scope(None))

    # Fixture specification.
    add("fixture_bad_length", "fixture_length_mismatch",
        lambda: validate_fixture({"length_samples": 16000,
                                  "segments": fixture_spec()["segments"]}))
    add("fixture_bad_segment_count", "fixture_segment_count",
        lambda: validate_fixture({"length_samples": FIXTURE_LENGTH,
                                  "segments": []}))
    return cases


def valid_controls() -> Dict[str, Any]:
    gate = CausalTwoWindowGateSurrogate(epoch=1)
    values, quantized = gate.process_frame(_valid_frame())
    manifest = validate_caller_manifest(_base_manifest())
    scope = validate_use_scope("research_evaluation")
    return {
        "cases": [
            {
                "case_id": "valid_silent_frame",
                "status": "accepted",
                "output_samples": len(quantized),
                "advanced_samples": gate.position,
                "all_finite": all(math.isfinite(value) for value in values),
            },
            {
                "case_id": "valid_caller_manifest",
                "status": "accepted" if manifest["validated"] else "rejected",
                "loaded": manifest["loaded"],
                "executed": manifest["executed"],
            },
            {
                "case_id": "valid_research_scope",
                "status": "accepted" if scope == "research_evaluation"
                else "rejected",
            },
        ],
        "all_accepted": gate.position == FRAME_SAMPLES,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Report and contract builders
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
                "evidence": ("Frozen synthetic noisy microphone and authored "
                             "clean reference with an identity/noisy control "
                             "and per-region SI-SDR/SNR; no real recording."),
            },
            "task_matched_baseline": {
                "status": "blocked",
                "evidence": ("No established task-matched baseline is pinned, "
                             "licensed or run; sibling evidence is not reused."),
            },
            "paired_si_sdr": {
                "status": "synthetic_only",
                "evidence": ("Exact integer scale-invariant SDR in millidB "
                             "against an authored synthetic clean reference "
                             "only; no rights-cleared paired corpus."),
            },
            "paired_stoi": {
                "status": "blocked",
                "evidence": ("No pinned STOI scorer and no permitted "
                             "rights-cleared clean references; not computed "
                             "and not fabricated."),
            },
            "clean_speech_preservation": {
                "status": "synthetic_only",
                "evidence": ("SI-SDR, SNR, level change and peak on two "
                             "synthetic near-clean regions; no listening."),
            },
            "peaks_and_invalid_outputs": {
                "status": "synthetic_only",
                "evidence": ("Peak bound, clamping and nonfinite-output "
                             "counts on synthetic frames; no runtime."),
            },
            "unpaired_predictive_screen_or_listening": {
                "status": "blocked",
                "evidence": ("No predictive screen, authorized listening or "
                             "rights-cleared unpaired speech exists."),
            },
            "alignment_content_mapping": {
                "status": "synthetic_only",
                "evidence": ("Zero declared surrogate content delay with "
                             "-16/-8/0/+8/+16 shift probes on synthetic "
                             "audio; no candidate alignment is asserted."),
            },
            "runtime_availability_timing": {
                "status": "blocked",
                "evidence": ("No exact runtime, device clock, deadline, "
                             "availability or measured content delay."),
            },
            "streaming_state_and_reset": {
                "status": "blocked",
                "evidence": ("The census reports a streaming model, but no "
                             "staged runtime, frame geometry or reset "
                             "contract exists. Surrogate mechanics are not "
                             "candidate streaming."),
            },
            "runtime_memory": {
                "status": "blocked",
                "evidence": ("No measured runtime memory; only a declared "
                             "surrogate integer state size."),
            },
            "task_matched_heldout_qualification": {
                "status": "blocked",
                "evidence": ("No rights-cleared task-matched held-out paired "
                             "cohort, independent scorer or listening "
                             "result."),
            },
        },
    }


def _profile_blockers(profile: Dict[str, Any]) -> List[str]:
    return sorted(name for name, item in profile["required_items"].items()
                  if item["status"] == "blocked")


def _release_gates() -> List[Dict[str, str]]:
    rows = [
        ("RG-01", "Exact pinned Facebook Denoiser dns48 source, pretrained "
                  "weight file and PyTorch inference runtime with immutable "
                  "revisions, verified archived-repository lineage, licence "
                  "identity and an exact architecture/geometry record."),
        ("RG-02", "Isolated hash-pinned runtime admission with a reproducible "
                  "environment, verified weight identity, declared precision "
                  "and fail-closed absent-artifact behavior."),
        ("RG-03", "Code, weight, training-data and corpus rights plus "
                  "attribution, notices, redistribution, product-use, "
                  "generated-output and derivative-output review under the "
                  "recorded CC-BY-NC 4.0 research-only terms."),
        ("RG-04", "SDK boundary admission: caller-supplied asset identity, "
                  "causal streaming against frame-based geometry, content "
                  "delay, buffering and byte-level output parity."),
        ("RG-05", "Rights-cleared task-matched held-out paired qualification "
                  "with identity/noisy control, established baseline, paired "
                  "SI-SDR and STOI, clean-speech preservation, content "
                  "faithfulness and peaks."),
        ("RG-06", "Hallucination, insertion, deletion and nonfinite behavior "
                  "at the exact runtime, including clean and noise-only "
                  "controls."),
        ("RG-07", "Target-device compute, pacing, memory, latency and "
                  "throughput with independent listening and/or ASR content "
                  "controls."),
        ("RG-08", "Opt-in provider intake, descriptor review, independent "
                  "exact-head review and default/release approval."),
    ]
    return [{"id": gate, "requirement": text, "status": "blocked"}
            for gate, text in rows]


def _exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "pinned_facebook_denoiser_source_weights_runtime_absent",
            "requirement": ("Supply one exact licensed Facebook Denoiser dns48 "
                            "source tree, pretrained weight file and PyTorch "
                            "inference runtime with immutable revisions, byte "
                            "counts and SHA-256 digests."),
            "state": ("The pinned census records an official archived "
                      "repository with pretrained DNS models and streaming "
                      "evaluation. No Facebook Denoiser source, dns48 weight, "
                      "runtime, adapter or revision is staged at "
                      "data/checkouts/facebook-denoiser-dns48, "
                      "data/models/facebook-denoiser-dns48, "
                      "data/envs/facebook-denoiser-dns48 or "
                      "adapters/facebook-denoiser-dns48."),
        },
        {
            "id": "license_cc_by_nc_4_0_research_only",
            "requirement": ("Resolve repository and model rights. The pinned "
                            "census records CC-BY-NC 4.0, which permits no "
                            "commercial or product use; a product or "
                            "redistribution decision requires an exact "
                            "licence text, weight terms, training-data "
                            "statement, notice bundle and legal review."),
            "state": ("No upstream LICENSE text, model card copy, weight "
                      "terms, training-data statement, notice bundle or "
                      "product-use review is staged. The recorded CC-BY-NC "
                      "4.0 terms exclude the commercial selection and "
                      "product distribution this SDK release path requires, "
                      "so the candidate is research-evaluation only."),
        },
        {
            "id": "candidate_geometry_streaming_and_latency_unverified",
            "requirement": ("Document the exact dns48 input rate, channels, "
                            "hidden-channel width, hop, frame, streaming "
                            "boundary, output alignment, buffering, "
                            "algorithmic latency and precision for the pinned "
                            "artifacts."),
            "state": ("The pinned census reports a causal waveform Demucs "
                      "family with 48 hidden channels and a 16 kHz role only. "
                      "It records no hop, frame, channel layout, output "
                      "alignment, buffering, algorithmic latency, parameter "
                      "count or precision, so no candidate geometry or delay "
                      "is asserted."),
        },
        {
            "id": "sdk_enhancement_boundary_and_provider_integration_absent",
            "requirement": ("Admit the candidate asset through the accepted "
                            "caller-supplied contract, map its exact geometry "
                            "into the installed path and reproduce byte-level "
                            "output."),
            "state": ("Installed v0 accepts one 16 kHz mono float32 "
                      "160-sample stream with no model or asset admission "
                      "path. No descriptor, adapter, asset manifest or "
                      "output parity exists for Facebook Denoiser dns48."),
        },
        {
            "id": "rights_cleared_paired_cohort_and_scorer_absent",
            "requirement": ("Supply a rights-cleared task-matched held-out "
                            "paired clean/noisy cohort plus an independent "
                            "pinned SI-SDR/STOI/PESQ scorer, an established "
                            "baseline, content-faithfulness checks and "
                            "permitted listening."),
            "state": ("No real noisy/clean pair, corpus terms, held-out "
                      "split, pinned scorer, baseline run, hallucination "
                      "control or listening result is staged. Synthetic "
                      "integer fixtures cannot qualify the candidate."),
        },
        {
            "id": "compute_content_preservation_and_independent_review_absent",
            "requirement": ("Measure target-runtime compute, pacing, content "
                            "and availability timing, memory, nonfinite and "
                            "hallucination behavior and complete independent "
                            "review."),
            "state": ("The census flags an archived dependency stack and "
                      "unmeasured CPU real-time factor. No device clock, "
                      "RTF, memory, worker, listening, benchmark, provider "
                      "intake or release approval exists; no result may "
                      "qualify."),
        },
    ]


def _licensing() -> Dict[str, Any]:
    return {
        "reported_upstream_license": CANDIDATE_REPORTED_LICENSE,
        "license_text_staged": False,
        "attribution_required": True,
        "attribution_notice_staged": False,
        "weights_terms_staged": False,
        "training_data_statement_staged": False,
        "redistribution_reviewed": False,
        "product_use_reviewed": False,
        "generated_output_terms_staged": False,
        "review_status": "blocked",
        "permitted_scope_here": "research_evaluation_only",
        "commercial_use_permitted": False,
        "note": ("The pinned census records CC-BY-NC 4.0 for the repository "
                 "and models. No exact licence text, weight terms, "
                 "training-data statement, notice bundle or legal review is "
                 "staged, and non-commercial terms do not permit product or "
                 "redistribution use in this release path."),
    }


def _license_scope() -> Dict[str, Any]:
    return {
        "recorded_license": CANDIDATE_REPORTED_LICENSE,
        "permitted_scope": "research_evaluation_only",
        "permitted_use_scopes": sorted(PERMITTED_USE_SCOPES),
        "commercial_or_product_use_permitted": False,
        "redistribution_permitted": False,
        "rejection_code": "license_scope_not_permitted",
        "status": "blocked",
        "qualifies": False,
    }


def _candidate() -> Dict[str, Any]:
    return {
        "name": TITLE,
        "reported_artifact": CANDIDATE_REPORTED_ARTIFACT,
        "reported_algorithm": ("causal waveform Demucs speech denoiser with "
                               "48 hidden channels (census description; "
                               "architecture not verified)"),
        "reported_hidden_channels": CANDIDATE_HIDDEN_CHANNELS,
        "reported_parameter_count": None,
        "reported_input_sample_rate_hz": CANDIDATE_REPORTED_SAMPLE_RATE_HZ,
        "reported_streaming": True,
        "reported_offline_whole_utterance": False,
        "reported_license": CANDIDATE_REPORTED_LICENSE,
        "reported_repository_archived": True,
        "reported_runtime": CANDIDATE_REPORTED_RUNTIME,
        "reported_hop_samples": None,
        "reported_frame_samples": None,
        "reported_algorithmic_latency_samples": None,
        "reported_upstream_metrics": {
            "source": "research/noise_suppression_candidate_census.md",
            "values": None,
            "note": ("The pinned census records no numeric quality result for "
                     "Facebook Denoiser dns48; no PESQ, STOI or SI-SDR value "
                     "is asserted."),
        },
        "checkpoint_lineage_verified": False,
        "geometry_documented": False,
        "source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "exact_numeric_output_present": False,
    }


def _external_artifacts() -> Dict[str, Any]:
    paths = {
        "source_checkout": "data/checkouts/facebook-denoiser-dns48",
        "weights": "data/models/facebook-denoiser-dns48",
        "runtime_env": "data/envs/facebook-denoiser-dns48",
        "adapter": "adapters/facebook-denoiser-dns48",
        "caller_manifest": "data/manifests/facebook-denoiser-dns48.json",
    }
    present = {key: (SOURCE_ROOT / path).exists()
               for key, path in paths.items()}
    return {
        "checked_paths": paths,
        "present": present,
        "any_present": any(present.values()),
        "status": "blocked",
        "note": ("Observed presence would not be runtime admission, parity or "
                 "rights evidence."),
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
        "real_paired_audio": False,
        "real_clean_reference": False,
        "unpaired_screen": False,
        "device_timing": False,
        "listening": False,
        "runtime_invocation": False,
        "weights": False,
        "network_access": False,
        "benchmark_claim": False,
        "release_claim": False,
        "numeric_parity_claim": False,
        "provider_registration": False,
        "processor_exposure": False,
        "public_default": False,
    }


NEGATIVE_CLAIMS = (
    "No Facebook Denoiser dns48 source, weight file, Demucs layer, PyTorch "
    "graph, runtime, adapter, revision or numeric output was produced, "
    "downloaded, loaded or executed.",
    "No noise-suppression, quality, PESQ, STOI, latency, benchmark, listening or "
    "release result is claimed.",
    "The causal dual-window integer gate surrogate is not Facebook Denoiser "
    "and cannot qualify the candidate.",
    "No Facebook Denoiser input rate, hidden-channel width, hop, frame, "
    "channel layout, alignment, buffering, latency or precision is verified "
    "or asserted beyond the census description.",
    "Synthetic integer SI-SDR, SNR, level change and peak values are unqualified "
    "task-local observations only.",
    "STOI was not computed: no pinned scorer and no rights-cleared paired clean "
    "reference exists.",
    "No real noisy/clean recording, corpus, upstream score, device clock or "
    "listener was used.",
    "The recorded CC-BY-NC 4.0 terms are not a licence grant; no upstream "
    "licence text, attribution bundle, weight terms, training-data statement "
    "or product-use review is staged.",
    "No provider, descriptor, registry, installed v0 path, shared build, "
    "dependency lock or CI was changed.",
)

REOPEN_CONDITION = (
    "Replace the research-only blocker with an exact, legally reviewed "
    "Facebook Denoiser dns48 source/weight/runtime package whose terms permit "
    "the intended distribution and product use, or obtain an explicit rights "
    "decision; pin immutable revisions and digests, verify archived-repository "
    "lineage, document the exact geometry, latency and framewise mapping, "
    "admit an isolated hash-pinned runtime, map the asset through the "
    "caller-supplied SDK boundary and reproduce exact output, then run an "
    "established baseline and paired SI-SDR/STOI plus clean-preservation, "
    "hallucination and peak qualification on a rights-cleared task-matched "
    "held-out cohort, measure compute/availability/memory at the exact "
    "runtime and complete opt-in provider intake. Until then the candidate "
    "stays DEFER, incomplete and not qualified."
)


def _case_matrix_digest(run: Dict[str, Any], alignment: Dict[str, Any],
                        streaming: Dict[str, Any],
                        reset: Dict[str, Any]) -> str:
    return object_digest({
        "signals": run["signal_digests"],
        "noisy": [(row["segment"], row["identity_si_sdr_millidb"],
                   row["surrogate_si_sdr_millidb"],
                   row["delta_snr_millidb"])
                  for row in run["noisy_regions"]],
        "clean": [(row["segment"], row["si_sdr_millidb"],
                   row["level_change_millidb"])
                  for row in run["clean_regions"]],
        "pause": (run["pause"]["noise_attenuation_millidb"],),
        "alignment": (alignment["best_shift_samples"],
                      alignment["zero_shift_best"]),
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
            "length_samples": FIXTURE_LENGTH,
            "duration_ns": FIXTURE_LENGTH * SAMPLE_NS,
            "segments": [dict(segment) for segment in SEGMENTS],
        },
        "signal_digests": run["signal_digests"],
    }


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()
    fixture = fixture_run()
    alignment = alignment_run()
    streaming = streaming_check(fixture)
    reset = reset_check()
    partial = final_partial_check()
    profile = _acceptance_profile()
    adverse = adverse_rejections()
    controls = valid_controls()
    gates = _release_gates()
    blockers = _exact_blockers()
    licensing = _licensing()
    candidate = _candidate()
    matrix = _case_matrix_digest(fixture, alignment, streaming, reset)

    noisy_values = [row["surrogate_si_sdr_millidb"]
                    for row in fixture["noisy_regions"]]
    delta_values = [row["delta_si_sdr_millidb"]
                    for row in fixture["noisy_regions"]]
    clean_values = [row["si_sdr_millidb"]
                    for row in fixture["clean_regions"]]
    level_values = [row["level_change_millidb"]
                    for row in fixture["clean_regions"]]
    report: Dict[str, Any] = {
        "schema_id": REPORT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "version": VERSION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "profile": PROFILE,
        "acceptance_profile": profile,
        "profile_blockers": _profile_blockers(profile),
        "candidate": candidate,
        "reference": {
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "implementation_present": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "checkpoint_lineage_verified": False,
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
            "candidate_reported_sample_rate_hz":
                CANDIDATE_REPORTED_SAMPLE_RATE_HZ,
            "candidate_reported_hidden_channels": CANDIDATE_HIDDEN_CHANNELS,
            "candidate_streaming_reported": True,
            "candidate_offline_whole_utterance": False,
            "candidate_geometry_documented": False,
            "resampling": "none",
            "model_asset_in_installed_v0": False,
            "surrogate_content_delay_samples": 0,
            "surrogate_lookahead_samples": 0,
            "surrogate_algorithmic_latency_samples": 0,
            "surrogate_frame_causal": True,
        },
        "fixtures": _fixtures(fixture),
        "paired_metrics": {
            "reference": "authored synthetic clean Q15 signal",
            "control": "identity/noisy passthrough",
            "regions": fixture["noisy_regions"],
            "min_surrogate_si_sdr_millidb": min(noisy_values),
            "max_surrogate_si_sdr_millidb": max(noisy_values),
            "min_delta_si_sdr_millidb": min(delta_values),
            "mean_delta_si_sdr_millidb":
                sum(delta_values) // len(delta_values),
            "no_noisy_region_degraded": all(
                value >= 0 for value in delta_values),
            "qualifies": False,
        },
        "clean_preservation": {
            "regions": fixture["clean_regions"],
            "min_si_sdr_millidb": min(clean_values),
            "max_abs_level_change_millidb":
                max(abs(value) for value in level_values),
            "nonfinite_output_count": fixture["overall"][
                "nonfinite_output_count"],
            "qualifies": False,
        },
        "peaks_and_invalid": {
            "max_peak_milli": fixture["overall"]["max_peak_milli"],
            "peak_bound_milli": 1000,
            "clipped_samples": 0,
            "invalid_output_count": 0,
            "nonfinite_output_count": fixture["overall"][
                "nonfinite_output_count"],
            "qualifies": False,
        },
        "pause_attenuation": fixture["pause"],
        "stoi": {
            "status": "blocked",
            "value_millis": None,
            "reason": ("No pinned STOI scorer and no rights-cleared paired "
                       "clean references; not computed and not fabricated."),
            "qualifies": False,
        },
        "baseline": {
            "status": "blocked",
            "baseline_id": None,
            "reason": ("No established task-matched baseline is pinned, "
                       "licensed or run; sibling evidence is not imported."),
            "qualifies": False,
        },
        "alignment": alignment,
        "streaming": streaming,
        "reset": reset,
        "final_partial": partial,
        "state_and_memory": {
            "status": "synthetic_state_only",
            "surrogate_state_bytes": CausalTwoWindowGateSurrogate().state_bytes,
            "window_samples": FRAME_SAMPLES,
            "lookahead_stated": True,
            "memory_measured": False,
            "candidate_memory_measured": False,
            "qualifies": False,
        },
        "runtime_timing": {
            "status": "blocked_unmeasured",
            "content_delay_samples": 0,
            "candidate_content_delay_documented": False,
            "availability_modeled": False,
            "wall_clock_measured": False,
            "real_time_factor": None,
            "deadline_ns": None,
            "qualifies": False,
        },
        "listening": {
            "status": "not_run",
            "authorized": False,
            "result": None,
            "qualifies": False,
        },
        "nonfinite": {
            "rejected_nonfinite_inputs": sum(
                1 for case in adverse
                if case["observed_code"].startswith("nonfinite_input")),
            "output_nonfinite_count": fixture["overall"][
                "nonfinite_output_count"],
            "output_finite": fixture["overall"]["nonfinite_output_count"] == 0,
            "qualifies": False,
        },
        "adverse_rejections": adverse,
        "adverse_all_rejected": all(
            row["status"] == "rejected" and row["state_unchanged"] is True
            for row in adverse),
        "valid_controls": controls,
        "external_artifacts": _external_artifacts(),
        "licensing": licensing,
        "license_scope": _license_scope(),
        "caller_asset": {
            "contract_id": ("audio-sdk/facebook-denoiser-dns48/"
                            "caller-supplied-asset/0.1"),
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "manifest_present": False,
            "workspace_manifest":
                "data/manifests/facebook-denoiser-dns48.json",
            "present_behavior": ("validate_identity_geometry_only; do not load"
                                 "_or_execute"),
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
            "exact_runtime_outputs_present": False,
            "checkpoint_lineage_verified": False,
            "rights_cleared_cohort": False,
            "geometry_documented": False,
            "paired_control_qualified": False,
            "baseline_qualified": False,
            "si_sdr_qualified": False,
            "stoi_qualified": False,
            "clean_preservation_qualified": False,
            "peaks_validated": False,
            "alignment_qualified": False,
            "timing_measured": False,
            "memory_measured": False,
            "hallucination_checked": False,
            "listening": False,
            "real_corpus_used": False,
            "reason": ("Exact Facebook Denoiser dns48 source/weights/PyTorch "
                       "runtime, verified lineage, geometry, rights, "
                       "caller-asset admission, rights-cleared held-out data, "
                       "independent scorer, baseline, hallucination controls, "
                       "listening and timing are all absent."),
        },
        "exact_blockers": blockers,
        "release_gates": gates,
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "surrogate": {
            "algorithm": ("causal dual-window integer per-frame energy gate "
                          "(gain 250 or 1000 per mille; two contiguous "
                          "half-window mean-magnitude maxima; no smoothing, "
                          "no weights)"),
            "is_facebook_denoiser": False,
            "is_demucs": False,
            "is_learned": False,
            "uses_network": False,
            "uses_weight_file": False,
            "uses_convolution": False,
            "uses_quantization": False,
            "uses_float_arithmetic_in_signal_path": False,
            "is_generative": False,
            "qualifies_candidate": False,
        },
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "case_matrix_digests": [matrix, matrix, matrix],
        },
        "scope_note": ("Only docs/task-evidence/facebook-denoiser-dns48/ is "
                       "written; all other paths are read-only pins."),
    }
    return report


# ---------------------------------------------------------------------------
# Contract and manifest
# ---------------------------------------------------------------------------

def artifact_pins(report_digest: str, sidecar_digest: str) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in ARTIFACT_FILES:
        if name == "report.json":
            pins[TASK_PREFIX + name] = report_digest
        elif name == "report.json.sha256":
            pins[TASK_PREFIX + name] = sidecar_digest
        else:
            pins[TASK_PREFIX + name] = file_digest(TASK_DIR / name)
    return pins


def build_contract(report: Dict[str, Any],
                   report_digest: str) -> Dict[str, Any]:
    sidecar_digest = sha256_bytes((report_digest + "\n").encode("ascii"))
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
        "license_scope": report["license_scope"],
        "artifact_pins": artifact_pins(report_digest, sidecar_digest),
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
            "contract_id": ("audio-sdk/facebook-denoiser-dns48/"
                            "caller-supplied-asset/0.1"),
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "required_fields": sorted(CALLER_MANIFEST_FIELDS),
            "present_behavior": ("validate_identity_geometry_only; do not load"
                                 "_or_execute"),
            "absent_behavior": "reject_before_processing",
            "separate_archive_required": True,
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no Facebook Denoiser source, weight, Demucs layer, PyTorch graph, "
            "runtime or adapter is downloaded, copied, loaded or executed",
            "the causal dual-window integer gate surrogate is not Facebook "
            "Denoiser and cannot qualify the candidate",
            "the recorded CC-BY-NC 4.0 terms are treated as research-only and "
            "no product, commercial or redistribution use is permitted",
            "STOI is not computed without a pinned scorer and rights-cleared "
            "paired clean references",
            "no candidate hop, frame, alignment, buffering, latency or "
            "precision is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def sources_bytes(overrides: Dict[str, bytes] | None = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-FACEBOOK-DENOISER-DNS48; source: paths are "
        "workspace-relative, others SDK-worktree-relative."
    ]
    for path, digest in SOURCE_PINS.items():
        lines.append(f"{digest}  source:{path}")
    for path, digest in BOUNDARY_PINS.items():
        lines.append(f"{digest}  {path}")
    for name in PIN_FILES:
        if name in overrides:
            digest = sha256_bytes(overrides[name])
        else:
            full = TASK_DIR / name
            _require(full.is_file(), "missing_artifact:" + name)
            digest = file_digest(full)
        lines.append(f"{digest}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")


__all__ = [
    "CausalTwoWindowGateSurrogate", "ReferenceRejection", "SEGMENTS",
    "adverse_rejections", "alignment_run", "board_row", "build_contract",
    "build_fixture", "build_report", "canonical_report", "canonical_text",
    "chunk_plan", "file_digest", "final_partial_check", "fixture_run",
    "fixture_spec", "int_signal_digest", "load_strict_json",
    "load_strict_json_text", "object_digest", "quantize", "reset_check",
    "run_stream", "sha256_bytes", "si_sdr_millidb", "signal_digest",
    "snr_millidb", "sources_bytes", "streaming_check",
    "validate_caller_manifest", "validate_config", "validate_fixture",
    "validate_use_scope", "valid_controls",
]
