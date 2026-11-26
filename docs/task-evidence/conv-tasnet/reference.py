# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local Conv-TasNet separation boundary evidence.

This is an original, stdlib-only synthetic probe written for this task. It is
NOT Conv-TasNet source, a Conv-TasNet build, a licensed Conv-TasNet runtime, a
Conv-TasNet weight file or a Conv-TasNet result. No upstream code, learned
encoder, mask estimator, decoder, weight, corpus or asset is present, copied,
downloaded, loaded or executed.

The probe consumes caller-owned mono 16 kHz float32 160-sample mixture frames,
runs a fixed complementary integer band-split surrogate, pins the separation
model and the scoring permutation independently, and measures permutation-
invariant SI-SDR, interference leakage and target damage on frozen synthetic
two-source signals. It exists only to exercise strict parsing, exact fixture
arithmetic, online state, reset, block invariance, permutation and leakage
scoring, and adverse rejection at a task-local proposal boundary. It is
proposal-only, incomplete and not qualified.
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
REPORT_SCHEMA = "audio-sdk/conv-tasnet-report/0.1"
TASK_ID = "SDK-CONV-TASNET"
TITLE = "Conv-TasNet"
COMPONENT = "conv-tasnet"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "6967a728b5c4048fb01ed4522a76a6906fbcffe2"
BRANCH = "swarm/SDK-CONV-TASNET"
REVIEWER = "reviewer-CONV-TASNET"
PROFILE = "spatial"
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

SOURCE_COUNT = 2
FIXTURE_LENGTH = 8064
NOISE_AMPLITUDE = 30
CALIBRATION_REGION = (0, 2000)
EVALUATION_REGION = (4000, 8000)
FINAL_PARTIAL_VALID = 137
MAX_REPORTED_MILLIDB = 999000
FLOOR_MILLIDB = -999000
INT_SCALE = 32768.0
INT_SCALE_SQ = INT_SCALE * INT_SCALE

# Fixed complementary 25-tap low/high band splitter, Q15 integer arithmetic.
# The high band is the declared 12-sample delayed input minus the low band, so
# the two outputs reconstruct the delayed mixture exactly.
FILTER_SCALE = 32768
FILTER_TAPS: Tuple[int, ...] = (
    -44, -31, 0, 84, 259, 552, 972, 1497, 2079, 2649,
    3131, 3454, 3564, 3454, 3131, 2649, 2079, 1497, 972, 552,
    259, 84, 0, -31, -44,
)
CONTENT_DELAY_SAMPLES = 12
MODEL_ID = "fixed-complementary-band-split/0.1"
SEPARATION_MODEL_SHA256 = (
    "3c12c51eb81c707f16b09343a01fb172a1cdf21c0b23aec68bef15ce3e2b3d75"
)
SCORING_ID = "permutation-pinned-si-sdr-leakage/0.1"
SCORING_PROTOCOL_SHA256 = (
    "55a6943bfd861ed30fb75e69429010d2a9ae0975a4a40b604b5067af78f4baaa"
)

CANDIDATE_PAPER_REFERENCE = "https://arxiv.org/abs/1809.07454"

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

TONE_ENVELOPE = (0, 240, 720, 1400, 2200, 3000, 2800, 2100,
                 1300, 600, 120, 0, 180, 650, 1300, 700)
TONE_SCALE = 3000
TONE_AMPLITUDE = 12000
BROADBAND_ENVELOPE = (0, 300, 900, 1400, 1800, 1200, 600, 200)
BROADBAND_SCALE = 1800
BROADBAND_AMPLITUDE = 9000

SOURCES_SPEC: Tuple[Dict[str, Any], ...] = (
    {"name": "tonal_low_band", "kind": "sine_table_envelope",
     "envelope_period_samples": 100, "amplitude": TONE_AMPLITUDE},
    {"name": "broadband_high_band", "kind": "alternating_lcg_envelope",
     "envelope_period_samples": 50, "amplitude": BROADBAND_AMPLITUDE},
)

SOURCE_PINS = {
    "research/category_registry.json": (
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c"
    ),
    "audio-benchmark-platform/plan/INVENTORY.json": (
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c"
    ),
    "audio-benchmark-platform/plan/INVENTORY.md": (
        "5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130"
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
    "audio-benchmark-platform/plan/audio-sdk/README.md": (
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06"
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
    "docs/task-evidence/beam-tasnet-beam-guided-tasnet/README.md": (
        "a114f3b8ca0d870bf6059bed42c6a799dfce7b54b57fef124e3bb99bf1ae23f5"
    ),
    "docs/task-evidence/beam-tasnet-beam-guided-tasnet/report.json": (
        "52c470ef552a0dac700e7a041ccb95794677c241a8c9ff9717d8a49c79ef8d7b"
    ),
    "docs/task-evidence/beam-tasnet-beam-guided-tasnet/contract.json": (
        "adfab4e9cb4aee3e49e66472433fae27e55876400c6903ad3d1beff8e495c350"
    ),
    "docs/task-evidence/speechbrain-sepformer-dns4/README.md": (
        "1cc709249b21f2cdb5ad4bc3510b9479e3e07f6630aa45bea4cad22ea8698ecc"
    ),
    "docs/task-evidence/speechbrain-sepformer-dns4/report.json": (
        "e56b83bde079fca411ca8d98890fcc75e8302834b0df268c0fc87d43b2d32013"
    ),
    "docs/task-evidence/speechbrain-sepformer-dns4/contract.json": (
        "0443cccff0e709c0893e6821e090fa1145f40fc4f0933600bab256c8dadbcb1e"
    ),
    "docs/task-evidence/si-sdr-sdr-and-snr/README.md": (
        "16bc05e63afdb209ba2a9657b7977c29f7d15f9eb3d6e8d24e316b3d2ef671a3"
    ),
}

BOARD_ROW_STABLE_SHA256 = (
    "f603d3b98e53dc30ccc050caa94e2f8979a5a288b51318d17a951e83d86b9bf0"
)

TASK_PREFIX = "docs/task-evidence/conv-tasnet/"
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


def signal_digest(samples: Sequence[float | int]) -> str:
    return sha256_bytes(b"".join(struct.pack("<d", float(value))
                                 for value in samples))


def int_signal_digest(samples: Sequence[int]) -> str:
    return sha256_bytes(struct.pack("<%di" % len(samples), *samples))


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
        return FLOOR_MILLIDB
    value = 1000.0 * 10.0 * math.log10(numerator / denominator)
    return int(round(max(min(value, MAX_REPORTED_MILLIDB), FLOOR_MILLIDB)))


def _zero_mean(samples: Sequence[float]) -> List[float]:
    mean = sum(samples) / len(samples)
    return [value - mean for value in samples]


def si_sdr_millidb(estimate: Sequence[float], reference: Sequence[float],
                   start: int, end: int,
                   delay: int = CONTENT_DELAY_SAMPLES) -> int:
    """Zero-mean scale-invariant SDR in integer millidB on one region."""
    _require(0 <= start < end <= len(reference), "invalid_score_region")
    _require(end + delay <= len(estimate), "score_estimate_too_short")
    est = [float(estimate[index]) for index in range(start + delay, end + delay)]
    ref = [float(reference[index]) for index in range(start, end)]
    est = _zero_mean(est)
    ref = _zero_mean(ref)
    ref_energy = sum(value * value for value in ref)
    est_energy = sum(value * value for value in est)
    if ref_energy <= 0.0:
        return FLOOR_MILLIDB
    if est_energy <= 0.0:
        return FLOOR_MILLIDB
    projection = sum(est[index] * ref[index] for index in range(len(ref)))
    alpha = projection / ref_energy
    target_energy = alpha * alpha * ref_energy
    residual_energy = sum(
        (est[index] - alpha * ref[index]) ** 2 for index in range(len(ref)))
    return _db_millidb(target_energy, residual_energy)


def leakage_millidb(estimate: Sequence[float], interferer: Sequence[float],
                    target: Sequence[float], start: int, end: int,
                    delay: int = CONTENT_DELAY_SAMPLES) -> int:
    """Independent interference leakage relative to target energy."""
    _require(0 <= start < end <= len(target), "invalid_score_region")
    _require(end + delay <= len(estimate), "score_estimate_too_short")
    est = [float(estimate[index]) for index in range(start + delay, end + delay)]
    interf = [float(interferer[index]) for index in range(start, end)]
    targ = [float(target[index]) for index in range(start, end)]
    est = _zero_mean(est)
    interf = _zero_mean(interf)
    targ = _zero_mean(targ)
    interferer_energy = sum(value * value for value in interf)
    target_energy = sum(value * value for value in targ)
    if interferer_energy <= 0.0 or target_energy <= 0.0:
        return FLOOR_MILLIDB
    projection = sum(est[index] * interf[index] for index in range(len(interf)))
    alpha = projection / interferer_energy
    leak_energy = alpha * alpha * interferer_energy
    return _db_millidb(leak_energy, target_energy)


def level_change_millidb(estimate: Sequence[float],
                         reference: Sequence[float], start: int, end: int,
                         delay: int = CONTENT_DELAY_SAMPLES) -> int:
    _require(0 <= start < end <= len(reference), "invalid_score_region")
    _require(end + delay <= len(estimate), "score_estimate_too_short")
    est_energy = _energy(estimate, start + delay, end + delay)
    ref_energy = _energy(reference, start, end)
    return _db_millidb(est_energy, ref_energy)


def _check_finite(samples: Sequence[float]) -> int:
    return sum(0 if math.isfinite(value) else 1 for value in samples)


# ---------------------------------------------------------------------------
# Frozen synthetic two-source fixture
# ---------------------------------------------------------------------------

FIXTURE_KEYS = {
    "length_samples", "source_count", "noise_amplitude", "sources",
    "filter_taps", "filter_scale", "content_delay_samples",
    "calibration_region", "evaluation_region",
}
SOURCE_KEYS = {"name", "kind", "envelope_period_samples", "amplitude"}


def fixture_spec() -> Dict[str, Any]:
    return {
        "length_samples": FIXTURE_LENGTH,
        "source_count": SOURCE_COUNT,
        "noise_amplitude": NOISE_AMPLITUDE,
        "sources": [dict(source) for source in SOURCES_SPEC],
        "filter_taps": list(FILTER_TAPS),
        "filter_scale": FILTER_SCALE,
        "content_delay_samples": CONTENT_DELAY_SAMPLES,
        "calibration_region": list(CALIBRATION_REGION),
        "evaluation_region": list(EVALUATION_REGION),
    }


def _validate_region(value: object, label: str,
                     expected: Tuple[int, int]) -> None:
    _require(isinstance(value, list) and len(value) == 2,
             "invalid_region:" + label)
    start = _integer(value[0], "region_start", 0, FIXTURE_LENGTH)
    end = _integer(value[1], "region_end", 0, FIXTURE_LENGTH)
    _require((start, end) == expected, "region_mismatch:" + label)


def validate_fixture(spec: Dict[str, Any]) -> None:
    _exact_keys(spec, FIXTURE_KEYS, "fixture")
    length = _integer(spec["length_samples"], "length_samples", 160, 200000)
    _require(length == FIXTURE_LENGTH, "fixture_length_mismatch")
    count = _integer(spec["source_count"], "source_count", 2, 8)
    _require(count == SOURCE_COUNT, "fixture_source_count")
    noise = _integer(spec["noise_amplitude"], "noise_amplitude", 0, 1000)
    _require(noise == NOISE_AMPLITUDE, "fixture_noise_mismatch")
    sources = spec["sources"]
    _require(isinstance(sources, list) and len(sources) == len(SOURCES_SPEC),
             "fixture_source_list")
    for source, expected in zip(sources, SOURCES_SPEC):
        _exact_keys(source, SOURCE_KEYS, "source")
        _require(source["name"] == expected["name"], "fixture_source_name")
        _require(source["kind"] == expected["kind"], "fixture_source_kind")
        _integer(source["envelope_period_samples"],
                 "envelope_period_samples", 1, 4096)
        _require(source["envelope_period_samples"]
                 == expected["envelope_period_samples"],
                 "fixture_envelope_period")
        amplitude = _integer(source["amplitude"], "amplitude", 0, 32767)
        _require(amplitude == expected["amplitude"],
                 "fixture_source_amplitude")
    taps = spec["filter_taps"]
    _require(isinstance(taps, list) and len(taps) == len(FILTER_TAPS),
             "fixture_tap_count")
    for value, expected in zip(taps, FILTER_TAPS):
        _require(_integer(value, "filter_tap", -32768, 32768) == expected,
                 "fixture_tap_value")
    scale = _integer(spec["filter_scale"], "filter_scale", 1, 65536)
    _require(scale == FILTER_SCALE, "fixture_filter_scale")
    _require(sum(taps) == scale, "fixture_tap_sum")
    _require(taps == list(reversed(taps)), "fixture_tap_asymmetry")
    delay = _integer(spec["content_delay_samples"],
                     "content_delay_samples", 0, len(FILTER_TAPS) - 1)
    _require(delay == CONTENT_DELAY_SAMPLES, "fixture_delay_mismatch")
    _validate_region(spec["calibration_region"], "calibration",
                     CALIBRATION_REGION)
    _validate_region(spec["evaluation_region"], "evaluation",
                     EVALUATION_REGION)
    calibration_end = CALIBRATION_REGION[1]
    evaluation_start = EVALUATION_REGION[0]
    _require(calibration_end <= evaluation_start, "fixture_region_overlap")
    _require(EVALUATION_REGION[1] + CONTENT_DELAY_SAMPLES <= FIXTURE_LENGTH,
             "fixture_evaluation_exceeds_length")


def _lcg_values(seed: int, count: int) -> List[int]:
    state = seed & 0x7FFFFFFF
    values: List[int] = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append((state % 65535) - 32767)
    return values


def _tone_values(count: int) -> List[int]:
    values: List[int] = []
    for index in range(count):
        tone = (3 * SINE64[index % 64]
                + 2 * SINE64[(2 * index + 5) % 64]
                + SINE64[(3 * index + 11) % 64]) // 6
        level = TONE_ENVELOPE[(index // 100) % len(TONE_ENVELOPE)]
        values.append(tone * level * TONE_AMPLITUDE
                      // (32767 * TONE_SCALE))
    return values


def _broadband_values(count: int) -> List[int]:
    base = _lcg_values(20261126, count)
    values: List[int] = []
    for index in range(count):
        sign = 1 if index % 2 == 0 else -1
        level = BROADBAND_ENVELOPE[
            (index // 50) % len(BROADBAND_ENVELOPE)]
        values.append(base[index] * sign * level * BROADBAND_AMPLITUDE
                      // (32767 * BROADBAND_SCALE))
    return values


def build_fixture() -> Dict[str, Any]:
    """Build the frozen synthetic mixture and its permitted references."""
    validate_fixture(fixture_spec())
    sources = [_tone_values(FIXTURE_LENGTH),
               _broadband_values(FIXTURE_LENGTH)]
    noise_base = _lcg_values(20261127, FIXTURE_LENGTH)
    noise = [value * NOISE_AMPLITUDE // 32767 for value in noise_base]
    mixture = [
        max(-32768, min(32767, sources[0][index] + sources[1][index]
                        + noise[index]))
        for index in range(FIXTURE_LENGTH)
    ]
    return {
        "sources": sources,
        "noise": noise,
        "mixture": mixture,
    }


# ---------------------------------------------------------------------------
# Task-local complementary band-split surrogate
# ---------------------------------------------------------------------------

CONFIG_KEYS = {"sample_rate_hz", "channels", "frame_samples", "sample_format",
               "separated_source_count", "clock_ppm", "resampling"}


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the task-local probe configuration; fail closed."""
    _exact_keys(config, CONFIG_KEYS, "config")
    rate = _integer(config["sample_rate_hz"], "sample_rate_hz", 1, 384000)
    channels = _integer(config["channels"], "channels", 1, 8)
    frame = _integer(config["frame_samples"], "frame_samples", 1, 4096)
    count = _integer(config["separated_source_count"],
                     "separated_source_count", 1, 8)
    clock = _integer(config["clock_ppm"], "clock_ppm", -1000000, 1000000)
    _require(isinstance(config["sample_format"], str),
             "invalid_sample_format")
    _require(isinstance(config["resampling"], str), "invalid_resampling")
    if rate != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_sample_rate")
    if channels != CHANNELS:
        raise ReferenceRejection("unsupported_channels")
    if frame != FRAME_SAMPLES:
        raise ReferenceRejection("unsupported_frame_samples")
    if count != SOURCE_COUNT:
        raise ReferenceRejection("unsupported_source_count")
    if config["sample_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("unsupported_sample_format")
    if clock != 0:
        raise ReferenceRejection("unsupported_clock_drift")
    if config["resampling"] != "none":
        raise ReferenceRejection("unsupported_resampling")
    return {"sample_rate_hz": rate, "channels": channels,
            "frame_samples": frame, "sample_format": config["sample_format"],
            "separated_source_count": count, "clock_ppm": clock,
            "resampling": config["resampling"]}


def _validate_mono_frame(mixture: object, valid_count: object) -> int:
    count = _integer(valid_count, "valid_count", 1, FRAME_SAMPLES)
    if mixture is None:
        raise ReferenceRejection("missing_input")
    if not isinstance(mixture, (list, tuple)):
        raise ReferenceRejection("invalid_frame:input")
    if len(mixture) != FRAME_SAMPLES:
        raise ReferenceRejection("frame_count_mismatch:input")
    for index in range(count):
        value = mixture[index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceRejection("invalid_sample:input")
        if not math.isfinite(float(value)):
            raise ReferenceRejection("nonfinite_input:input")
    for index in range(count, FRAME_SAMPLES):
        value = mixture[index]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceRejection("invalid_sample:input")
        if float(value) != 0.0:
            raise ReferenceRejection("padding_not_zero:input")
    return count


class BandSplitSeparator:
    """Bounded complementary integer FIR band split with declared delay.

    The surrogate is not Conv-TasNet, is not learned, uses no weights and
    cannot qualify the candidate.
    """

    def __init__(self, sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = CHANNELS, frame_samples: int = FRAME_SAMPLES,
                 sample_format: str = SAMPLE_FORMAT,
                 separated_source_count: int = SOURCE_COUNT,
                 epoch: int = 1):
        if (sample_rate_hz != SAMPLE_RATE_HZ or channels != CHANNELS
                or frame_samples != FRAME_SAMPLES
                or sample_format != SAMPLE_FORMAT
                or separated_source_count != SOURCE_COUNT):
            raise ReferenceRejection(
                "unsupported_config",
                "v0 probe accepts only 16000/1/160/float32/2")
        if (not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1):
            raise ReferenceRejection("invalid_epoch")
        self.epoch = epoch
        self.position = 0
        self.frames = 0
        self.history = [0] * len(FILTER_TAPS)
        self.history_position = 0

    @property
    def state_digest(self) -> str:
        payload = struct.pack("<%di" % len(self.history), *self.history)
        payload += struct.pack("<qqqi", self.epoch, self.position,
                               self.history_position, self.frames)
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
        self.history = [0] * len(FILTER_TAPS)
        self.history_position = 0

    def process_frame(self, mixture: Sequence[float] | None,
                      valid_count: int = FRAME_SAMPLES,
                      epoch: int | None = None,
                      first_input_sample: int | None = None
                      ) -> Tuple[List[int], List[int]]:
        """Return (low_band, high_band); both contain 160 integer samples."""
        count = _validate_mono_frame(mixture, valid_count)
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

        low: List[int] = []
        high: List[int] = []
        taps = FILTER_TAPS
        tap_count = len(taps)
        for index in range(count):
            sample = int(round(float(mixture[index])))
            self.history[self.history_position] = sample
            newest = self.history[self.history_position::-1]
            oldest = self.history[:self.history_position:-1]
            window = newest + oldest
            total = 0
            for tap in range(tap_count):
                total += taps[tap] * window[tap]
            low_value = total // FILTER_SCALE
            low.append(low_value)
            high.append(window[CONTENT_DELAY_SAMPLES] - low_value)
            self.history_position = (self.history_position + 1) % tap_count
        self.position += count
        self.frames += 1
        low.extend([0] * (FRAME_SAMPLES - count))
        high.extend([0] * (FRAME_SAMPLES - count))
        return low, high


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


def run_stream(mixture: Sequence[int | float],
               chunks: Sequence[int] | None = None,
               epoch: int = 1) -> Dict[str, Any]:
    _require(isinstance(chunks, (list, tuple)) or chunks is None,
             "invalid_chunks")
    separator = BandSplitSeparator(epoch=epoch)
    plan = list(chunks) if chunks is not None else chunk_plan(len(mixture))
    _require(all(isinstance(size, int) and not isinstance(size, bool)
                 and size > 0 for size in plan), "invalid_chunk")
    _require(sum(plan) == len(mixture), "chunk_sum_mismatch")
    low: List[int] = []
    high: List[int] = []
    offset = 0
    for chunk in plan:
        chunk_end = offset + chunk
        while offset < chunk_end:
            size = min(FRAME_SAMPLES, chunk_end - offset)
            frame = [float(value) for value in mixture[offset:offset + size]]
            frame.extend([0.0] * (FRAME_SAMPLES - size))
            low_frame, high_frame = separator.process_frame(
                frame, valid_count=size)
            low.extend(low_frame[:size])
            high.extend(high_frame[:size])
            offset += size
    return {"low": low, "high": high, "state_digest": separator.state_digest,
            "samples": len(low)}


# ---------------------------------------------------------------------------
# Independent permutation pin and score
# ---------------------------------------------------------------------------

def _calibration_correlations(low: Sequence[int], high: Sequence[int],
                              sources: Sequence[Sequence[int]]) -> List[List[int]]:
    start, end = CALIBRATION_REGION
    outputs = (low, high)
    correlations: List[List[int]] = []
    for output in outputs:
        row: List[int] = []
        for source in sources:
            total = 0
            for index in range(start, end):
                total += (int(output[index + CONTENT_DELAY_SAMPLES])
                          * int(source[index]))
            row.append(total)
        correlations.append(row)
    return correlations


def _assignment(correlations: Sequence[Sequence[int]]) -> List[int]:
    identity = int(correlations[0][0]) + int(correlations[1][1])
    swapped = int(correlations[0][1]) + int(correlations[1][0])
    return [0, 1] if identity >= swapped else [1, 0]


def _assignment_sum_millidb(outputs: Sequence[Sequence[float]],
                            sources: Sequence[Sequence[float]],
                            assignment: Sequence[int]) -> int:
    values = []
    for source_index, output_index in enumerate(assignment):
        values.append(si_sdr_millidb(outputs[output_index],
                                     sources[source_index],
                                     *EVALUATION_REGION))
    return sum(values)


def separation_model_spec() -> Dict[str, Any]:
    return {
        "model_id": MODEL_ID,
        "algorithm": ("fixed complementary 25-tap integer low/high band "
                      "splitter with a 12-sample delayed-input high band"),
        "filter_taps": list(FILTER_TAPS),
        "filter_scale": FILTER_SCALE,
        "content_delay_samples": CONTENT_DELAY_SAMPLES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "separated_source_count": SOURCE_COUNT,
        "is_learned": False,
        "uses_weights": False,
        "is_conv_tasnet": False,
    }


def scoring_protocol_spec() -> Dict[str, Any]:
    return {
        "scoring_id": SCORING_ID,
        "metric": "zero_mean_scale_invariant_sdr",
        "units": "millidb",
        "calibration_region": list(CALIBRATION_REGION),
        "evaluation_region": list(EVALUATION_REGION),
        "alignment_delay_samples": CONTENT_DELAY_SAMPLES,
        "permutation_rule": "max_calibration_integer_correlation_sum",
        "permutation_source": "calibration_region_only",
        "leakage_measure": "orthogonal_projection_energy_ratio",
        "oracle_used_for_score": False,
    }


SCORING_KEYS = {
    "scoring_id", "metric", "units", "calibration_region",
    "evaluation_region", "alignment_delay_samples", "permutation_rule",
    "permutation_source", "leakage_measure", "oracle_used_for_score",
}
MODEL_SPEC_KEYS = {
    "model_id", "algorithm", "filter_taps", "filter_scale",
    "content_delay_samples", "sample_rate_hz", "channels", "frame_samples",
    "sample_format", "separated_source_count", "is_learned", "uses_weights",
    "is_conv_tasnet",
}


def validate_scoring_protocol(spec: Dict[str, Any]) -> None:
    _exact_keys(spec, SCORING_KEYS, "scoring")
    expected = scoring_protocol_spec()
    _require(spec == expected, "scoring_spec_mismatch")
    _require(spec["metric"] == "zero_mean_scale_invariant_sdr",
             "scoring_metric")
    _require(spec["oracle_used_for_score"] is False, "scoring_oracle_used")
    _validate_region(spec["calibration_region"], "calibration",
                     CALIBRATION_REGION)
    _validate_region(spec["evaluation_region"], "evaluation",
                     EVALUATION_REGION)


def validate_separation_model(spec: Dict[str, Any]) -> None:
    _exact_keys(spec, MODEL_SPEC_KEYS, "separation_model")
    expected = separation_model_spec()
    _require(spec == expected, "separation_model_mismatch")
    for key in ("is_learned", "uses_weights", "is_conv_tasnet"):
        _require(spec[key] is False, "separation_model_claim:" + key)


def fixture_run(epoch: int = 1, chunks: Sequence[int] | None = None
                ) -> Dict[str, Any]:
    fixture = build_fixture()
    run = run_stream(fixture["mixture"], chunks=chunks, epoch=epoch)
    low = [value / INT_SCALE for value in run["low"]]
    high = [value / INT_SCALE for value in run["high"]]
    sources = [[value / INT_SCALE for value in source]
               for source in fixture["sources"]]
    control = [value / INT_SCALE for value in fixture["mixture"]]
    correlations = _calibration_correlations(run["low"], run["high"],
                                             fixture["sources"])
    chosen = _assignment(correlations)
    oracle = _assignment([
        [sum(float(low[index]) * float(sources[source][index])
              for index in range(*EVALUATION_REGION))
         for source in range(SOURCE_COUNT)],
        [sum(float(high[index]) * float(sources[source][index])
              for index in range(*EVALUATION_REGION))
         for source in range(SOURCE_COUNT)],
    ])
    outputs = (low, high)
    chosen_sum = _assignment_sum_millidb(outputs, sources, chosen)
    swapped = [1 - chosen[0], 1 - chosen[1]]
    swapped_sum = _assignment_sum_millidb(outputs, sources, swapped)
    oracle_sum = _assignment_sum_millidb(outputs, sources, oracle)
    rows = []
    for source_index in range(SOURCE_COUNT):
        output_index = chosen[source_index]
        interferer = 1 - source_index
        estimate = outputs[output_index]
        rows.append({
            "source_index": source_index,
            "output_index": output_index,
            "evaluation_si_sdr_millidb": si_sdr_millidb(
                estimate, sources[source_index], *EVALUATION_REGION),
            "mixture_control_si_sdr_millidb": si_sdr_millidb(
                control, sources[source_index], *EVALUATION_REGION, delay=0),
            "target_level_change_millidb": level_change_millidb(
                estimate, sources[source_index], *EVALUATION_REGION),
            "interference_leakage_millidb": leakage_millidb(
                estimate, sources[interferer], sources[source_index],
                *EVALUATION_REGION),
            "peak_milli": max(
                abs(value) for value in
                estimate[EVALUATION_REGION[0] + CONTENT_DELAY_SAMPLES:
                         EVALUATION_REGION[1] + CONTENT_DELAY_SAMPLES]),
            "qualifies": False,
        })
        rows[-1]["improvement_millidb"] = (
            rows[-1]["evaluation_si_sdr_millidb"]
            - rows[-1]["mixture_control_si_sdr_millidb"])
        rows[-1]["peak_milli"] = int(round(rows[-1]["peak_milli"] * 1000.0))
    return {
        "fixture": fixture,
        "run": run,
        "outputs": outputs,
        "sources": sources,
        "control": control,
        "rows": rows,
        "permutation": {
            "calibration_correlations": correlations,
            "chosen_assignment": chosen,
            "oracle_evaluation_assignment": oracle,
            "matches_oracle": chosen == oracle,
            "chosen_evaluation_sum_millidb": chosen_sum,
            "swapped_evaluation_sum_millidb": swapped_sum,
            "oracle_evaluation_sum_millidb": oracle_sum,
            "margin_millidb": chosen_sum - swapped_sum,
            "score_uses_calibration_permutation": True,
            "oracle_used_for_score": False,
            "independently_pinned": chosen == oracle,
            "qualifies": False,
        },
        "signal_digests": {
            "source_0": int_signal_digest(fixture["sources"][0]),
            "source_1": int_signal_digest(fixture["sources"][1]),
            "noise": int_signal_digest(fixture["noise"]),
            "mixture": int_signal_digest(fixture["mixture"]),
            "low_band": int_signal_digest(run["low"]),
            "high_band": int_signal_digest(run["high"]),
        },
        "nonfinite_output_count": _check_finite(low) + _check_finite(high),
    }


def alignment_probe(run: Dict[str, Any]) -> Dict[str, Any]:
    """Declare the surrogate delay and show the independent lag estimate."""
    sources = run["sources"]
    estimate = run["outputs"][0]
    target = sources[0]
    best_lag = None
    best_score = FLOOR_MILLIDB
    for lag in (0, CONTENT_DELAY_SAMPLES, 2 * CONTENT_DELAY_SAMPLES):
        score = si_sdr_millidb(estimate, target, *EVALUATION_REGION,
                               delay=lag)
        if score > best_score:
            best_score = score
            best_lag = lag
    shifted = si_sdr_millidb(estimate, target, *EVALUATION_REGION,
                             delay=CONTENT_DELAY_SAMPLES + 1)
    missing = si_sdr_millidb([0.0] * len(estimate), target,
                             *EVALUATION_REGION)
    return {
        "declared_content_delay_samples": CONTENT_DELAY_SAMPLES,
        "estimated_peak_lag_samples": best_lag,
        "declared_lag_score_millidb": best_score,
        "one_sample_shift_score_millidb": shifted,
        "missing_source_floor_millidb": missing,
        "declared_lag_detected": best_lag == CONTENT_DELAY_SAMPLES,
        "one_sample_shift_detected": shifted < best_score,
        "device_timing_measured": False,
        "qualifies": False,
    }


def source_order_probe(run: Dict[str, Any]) -> Dict[str, Any]:
    """Swap the reference order only; the mixture bytes and output stay equal."""
    correlations = run["permutation"]["calibration_correlations"]
    swapped_correlations = [[row[1], row[0]] for row in correlations]
    swapped_choice = _assignment(swapped_correlations)
    return {
        "probe": "reference_order_swap_on_identical_mixture",
        "output_digest_unchanged": True,
        "original_assignment": run["permutation"]["chosen_assignment"],
        "swapped_assignment": swapped_choice,
        "assignment_flips": (swapped_choice
                             == [1 - value
                                 for value in run["permutation"][
                                     "chosen_assignment"]]),
        "room_change_measured": False,
        "qualifies": False,
    }


def channel_loss_probe(run: Dict[str, Any]) -> Dict[str, Any]:
    """Mono fixture: there is no second channel to lose."""
    missing = si_sdr_millidb([0.0] * len(run["outputs"][0]),
                             run["sources"][1], *EVALUATION_REGION)
    return {
        "applicable": False,
        "reason": "mono synthetic fixture; no channel or array to lose",
        "missing_source_score_millidb": missing,
        "channel_substitution_performed": False,
        "qualifies": False,
    }


def streaming_check(offline: Dict[str, Any]) -> Dict[str, Any]:
    fixture = offline["fixture"]
    plan = chunk_plan(FIXTURE_LENGTH)
    streamed = run_stream(fixture["mixture"], chunks=plan)
    return {
        "chunks": plan,
        "accepted_samples": FIXTURE_LENGTH,
        "low_all_match": streamed["low"] == offline["run"]["low"],
        "high_all_match": streamed["high"] == offline["run"]["high"],
        "all_match": (streamed["low"] == offline["run"]["low"]
                      and streamed["high"] == offline["run"]["high"]),
        "offline_state_digest": offline["run"]["state_digest"],
        "streamed_state_digest": streamed["state_digest"],
        "scheduler_measured": False,
        "qualifies": False,
    }


def reset_check() -> Dict[str, Any]:
    fixture = build_fixture()
    mixture = fixture["mixture"][:2000]
    carried = BandSplitSeparator(epoch=1)
    offset = 0
    while offset < len(mixture):
        frame = [float(value) for value in mixture[offset:offset + FRAME_SAMPLES]]
        count = len(frame)
        frame.extend([0.0] * (FRAME_SAMPLES - count))
        carried.process_frame(frame, valid_count=count)
        offset += FRAME_SAMPLES
    carried.reset(2, 0)
    offset = 0
    while offset < len(mixture):
        frame = [float(value) for value in mixture[offset:offset + FRAME_SAMPLES]]
        count = len(frame)
        frame.extend([0.0] * (FRAME_SAMPLES - count))
        carried.process_frame(frame, valid_count=count, epoch=2)
        offset += FRAME_SAMPLES
    fresh = run_stream(mixture, epoch=2)
    return {
        "epoch": 2,
        "accepted_samples": len(mixture),
        "matches_fresh": carried.state_digest == fresh["state_digest"],
        "state_digest": carried.state_digest,
        "qualifies": False,
    }


def final_partial_check() -> Dict[str, Any]:
    fixture = build_fixture()
    carrier = BandSplitSeparator(epoch=1)
    frame = [float(value) for value in fixture["mixture"][:FINAL_PARTIAL_VALID]]
    frame.extend([0.0] * (FRAME_SAMPLES - FINAL_PARTIAL_VALID))
    low, high = carrier.process_frame(frame, valid_count=FINAL_PARTIAL_VALID)
    return {
        "valid_count": FINAL_PARTIAL_VALID,
        "padding_zero": True,
        "output_samples": len(low),
        "advanced_samples": carrier.position,
        "low_tail_zero": all(value == 0 for value in low[FINAL_PARTIAL_VALID:]),
        "high_tail_zero": all(value == 0
                              for value in high[FINAL_PARTIAL_VALID:]),
        "nonfinite_output_count": _check_finite(low) + _check_finite(high),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied asset identity (never loaded or executed)
# ---------------------------------------------------------------------------

CALLER_MANIFEST_FIELDS = {
    "adapter",
    "algorithmic_latency_samples",
    "channels",
    "frame_samples",
    "input_format",
    "library_path",
    "library_sha256",
    "model_path",
    "model_sha256",
    "sample_rate_hz",
    "separated_source_count",
    "source_commit",
    "source_sha256",
    "variant",
    "weights_sha256",
}


def validate_caller_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Validate declaration syntax and identity only; never read any asset."""
    _exact_keys(manifest, CALLER_MANIFEST_FIELDS, "caller_manifest")
    _string(manifest["adapter"], "adapter", 1, 64)
    _string(manifest["variant"], "variant", 1, 64)
    rate = _integer(manifest["sample_rate_hz"], "sample_rate_hz", 8000, 48000)
    channels = _integer(manifest["channels"], "channels", 1, 8)
    frame = _integer(manifest["frame_samples"], "frame_samples", 16, 4096)
    count = _integer(manifest["separated_source_count"],
                     "separated_source_count", 1, 8)
    latency = _integer(manifest["algorithmic_latency_samples"],
                       "algorithmic_latency_samples", 0, 16000)
    _require(isinstance(manifest["input_format"], str),
             "invalid_input_format")
    if channels != CHANNELS:
        raise ReferenceRejection("unsupported_channels")
    if count != SOURCE_COUNT:
        raise ReferenceRejection("unsupported_source_count")
    if manifest["input_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("unsupported_sample_format")
    if rate not in range(8000, 48001):
        raise ReferenceRejection("unsupported_sample_rate")
    if frame not in range(16, 4097):
        raise ReferenceRejection("unsupported_frame_samples")
    if latency < 0:
        raise ReferenceRejection("unsupported_algorithmic_latency")
    _absolute_path(manifest["model_path"], "model_path")
    _absolute_path(manifest["library_path"], "library_path")
    _sha256(manifest["model_sha256"], "model_sha256")
    _sha256(manifest["weights_sha256"], "weights_sha256")
    _sha256(manifest["source_sha256"], "source_sha256")
    _sha256(manifest["library_sha256"], "library_sha256")
    _commit(manifest["source_commit"], "source_commit")
    return {"validated": True, "loaded": False, "executed": False,
            "imported": False, "declaration_only": True,
            "candidate_geometry_verified": False}


# ---------------------------------------------------------------------------
# Adverse rejection matrix
# ---------------------------------------------------------------------------

def _base_config() -> Dict[str, Any]:
    return {"sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES, "sample_format": SAMPLE_FORMAT,
            "separated_source_count": SOURCE_COUNT, "clock_ppm": 0,
            "resampling": "none"}


def _base_manifest() -> Dict[str, Any]:
    return {
        "adapter": "conv-tasnet-reference",
        "algorithmic_latency_samples": 0,
        "channels": 1,
        "frame_samples": 160,
        "input_format": "float32",
        "library_path": "/caller/conv-tasnet/lib",
        "library_sha256": "3" * 64,
        "model_path": "/caller/conv-tasnet/model",
        "model_sha256": "0" * 64,
        "sample_rate_hz": 16000,
        "separated_source_count": 2,
        "source_commit": "0" * 40,
        "source_sha256": "1" * 64,
        "variant": "conv-tasnet-2spk",
        "weights_sha256": "2" * 64,
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
    add("json_root_array", "json_not_object",
        lambda: load_strict_json_text('[1,2]'))
    add("config_missing_field", "strict_keys_mismatch:config",
        lambda: validate_config({key: value for key, value in base.items()
                                 if key != "clock_ppm"}))
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
    add("config_one_source", "unsupported_source_count",
        lambda: validate_config({**base, "separated_source_count": 1}))
    add("config_three_sources", "unsupported_source_count",
        lambda: validate_config({**base, "separated_source_count": 3}))
    add("config_clock_drift", "unsupported_clock_drift",
        lambda: validate_config({**base, "clock_ppm": 1}))
    add("config_linear_resampling", "unsupported_resampling",
        lambda: validate_config({**base, "resampling": "linear"}))
    add("config_bool_rate", "invalid_integer:sample_rate_hz",
        lambda: validate_config({**base, "sample_rate_hz": True}))
    add("config_bool_source_count", "invalid_integer:separated_source_count",
        lambda: validate_config({**base, "separated_source_count": True}))

    separator = BandSplitSeparator(epoch=1)
    fixture = build_fixture()
    frame = [float(value) for value in fixture["mixture"][:FRAME_SAMPLES]]
    separator.process_frame(frame)
    before = separator.state_digest

    def add_frame(case_id: str, code: str, action) -> None:
        actual = _expect_reject(code, action)
        cases.append({
            "case_id": case_id,
            "code": actual,
            "status": "rejected" if actual != "accepted" else "accepted",
            "state_unchanged": separator.state_digest == before,
        })

    add_frame("frame_missing_input", "missing_input",
              lambda: separator.process_frame(None))
    add_frame("frame_count_mismatch", "frame_count_mismatch:input",
              lambda: separator.process_frame(frame[:159]))
    add_frame("frame_valid_count_zero", "invalid_integer:valid_count",
              lambda: separator.process_frame(frame, valid_count=0))
    add_frame("frame_valid_count_high", "invalid_integer:valid_count",
              lambda: separator.process_frame(frame, valid_count=161))
    add_frame("frame_nonfinite_input", "nonfinite_input:input",
              lambda: separator.process_frame([float("nan")] + frame[1:]))
    add_frame("frame_negative_infinity", "nonfinite_input:input",
              lambda: separator.process_frame([float("-inf")] + frame[1:]))
    add_frame("frame_nonzero_padding", "padding_not_zero:input",
              lambda: separator.process_frame(
                  frame[:137] + [1.0] + frame[138:], valid_count=137))
    add_frame("frame_string_sample", "invalid_sample:input",
              lambda: separator.process_frame(["x"] + frame[1:]))
    add_frame("frame_bool_sample", "invalid_sample:input",
              lambda: separator.process_frame([True] + frame[1:]))
    add_frame("frame_input_position_mismatch", "input_position_mismatch",
              lambda: separator.process_frame(frame, first_input_sample=1))
    add_frame("frame_epoch_mismatch", "epoch_mismatch",
              lambda: separator.process_frame(frame, epoch=2))

    reset_before = separator.state_digest

    def add_reset(case_id: str, code: str, action) -> None:
        actual = _expect_reject(code, action)
        cases.append({
            "case_id": case_id,
            "code": actual,
            "status": "rejected" if actual != "accepted" else "accepted",
            "state_unchanged": separator.state_digest == reset_before,
        })

    add_reset("reset_epoch_zero", "invalid_epoch",
              lambda: separator.reset(0, 0))
    add_reset("reset_epoch_negative", "invalid_epoch",
              lambda: separator.reset(-1, 0))
    add_reset("reset_epoch_not_greater", "invalid_epoch",
              lambda: separator.reset(1, 0))
    add_reset("reset_negative_position", "invalid_first_input_sample",
              lambda: separator.reset(2, -1))

    manifest = _base_manifest()
    add("caller_manifest_missing_field",
        "strict_keys_mismatch:caller_manifest",
        lambda: validate_caller_manifest(
            {key: value for key, value in manifest.items()
             if key != "weights_sha256"}))
    add("caller_manifest_extra_field",
        "strict_keys_mismatch:caller_manifest",
        lambda: validate_caller_manifest({**manifest, "extra": 1}))
    add("caller_manifest_relative_model_path",
        "invalid_source_path:model_path",
        lambda: validate_caller_manifest(
            {**manifest, "model_path": "relative/model"}))
    add("caller_manifest_relative_library_path",
        "invalid_source_path:library_path",
        lambda: validate_caller_manifest(
            {**manifest, "library_path": "relative/lib"}))
    add("caller_manifest_bad_commit", "invalid_string:source_commit",
        lambda: validate_caller_manifest(
            {**manifest, "source_commit": "not-a-commit"}))
    add("caller_manifest_bad_model_hash", "invalid_sha256:model_sha256",
        lambda: validate_caller_manifest(
            {**manifest, "model_sha256": "0" * 63 + "z"}))
    add("caller_manifest_wrong_channels", "unsupported_channels",
        lambda: validate_caller_manifest({**manifest, "channels": 2}))
    add("caller_manifest_wrong_source_count", "unsupported_source_count",
        lambda: validate_caller_manifest(
            {**manifest, "separated_source_count": 3}))
    add("caller_manifest_wrong_format", "unsupported_sample_format",
        lambda: validate_caller_manifest(
            {**manifest, "input_format": "int16"}))
    add("caller_manifest_wrong_frame", "unsupported_frame_samples",
        lambda: validate_caller_manifest(
            {**manifest, "frame_samples": 8}))
    add("caller_manifest_negative_latency",
        "invalid_integer:algorithmic_latency_samples",
        lambda: validate_caller_manifest(
            {**manifest, "algorithmic_latency_samples": -1}))

    def bad_fixture(**changes):
        spec = fixture_spec()
        spec.update(changes)
        validate_fixture(spec)

    add("fixture_length_mismatch", "fixture_length_mismatch",
        lambda: bad_fixture(length_samples=7999))
    add("fixture_source_count", "fixture_source_count",
        lambda: bad_fixture(source_count=3))
    add("fixture_tap_count", "fixture_tap_count",
        lambda: bad_fixture(filter_taps=list(FILTER_TAPS[:-1])))
    add("fixture_tap_sum", "fixture_tap_sum",
        lambda: bad_fixture(filter_taps=[value + 1 for value in FILTER_TAPS]))
    add("fixture_tap_asymmetry", "fixture_tap_asymmetry",
        lambda: bad_fixture(filter_taps=[0] * len(FILTER_TAPS)))
    add("fixture_region_overlap", "fixture_region_overlap",
        lambda: bad_fixture(evaluation_region=[1000, 8000]))
    add("fixture_delay_mismatch", "fixture_delay_mismatch",
        lambda: bad_fixture(content_delay_samples=13))

    def bad_model(**changes):
        spec = separation_model_spec()
        spec.update(changes)
        validate_separation_model(spec)

    add("model_extra_field", "strict_keys_mismatch:separation_model",
        lambda: bad_model(extra=1))
    add("model_learned_claim", "separation_model_mismatch",
        lambda: bad_model(is_learned=True))
    add("model_tap_tamper", "separation_model_mismatch",
        lambda: bad_model(filter_taps=[0] * len(FILTER_TAPS)))

    def bad_scoring(**changes):
        spec = scoring_protocol_spec()
        spec.update(changes)
        validate_scoring_protocol(spec)

    add("scoring_extra_field", "strict_keys_mismatch:scoring",
        lambda: bad_scoring(extra=1))
    add("scoring_metric_tamper", "scoring_spec_mismatch",
        lambda: bad_scoring(metric="waveform_mse"))
    add("scoring_oracle_claim", "scoring_oracle_used",
        lambda: bad_scoring(oracle_used_for_score=True))

    add("chunk_sum_mismatch", "chunk_sum_mismatch",
        lambda: run_stream(fixture["mixture"], chunks=[160, 160]))
    add("chunk_zero", "invalid_chunk",
        lambda: run_stream(fixture["mixture"], chunks=[160, 0, 7840]))
    add("chunk_negative", "invalid_chunk",
        lambda: run_stream(fixture["mixture"], chunks=[160, -160, 8000]))
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
            "geometry_layout_timestamp_calibration": {
                "status": "blocked",
                "evidence": ("No array geometry, channel layout, device clock "
                             "or timestamp calibration exists; the fixture is "
                             "a mono synthetic mixture with sample indices."),
            },
            "source_target_reference_conditions": {
                "status": "synthetic_only",
                "evidence": ("Two declared synthetic sources, one fixed "
                             "mixture and one fixed noise level; no real "
                             "source, target or reference condition."),
            },
            "permissions": {
                "status": "blocked",
                "evidence": ("No corpus consent, licence or recording "
                             "permission exists."),
            },
            "task_matched_heldout_labels": {
                "status": "blocked",
                "evidence": ("No rights-cleared held-out two-speaker cohort, "
                             "source labels, mixed/clean pairs or scorer."),
            },
            "localization_activity": {
                "status": "blocked",
                "evidence": ("Not applicable to a mono generic separation "
                             "probe and no candidate output exists to score."),
            },
            "extraction": {
                "status": "synthetic_only",
                "evidence": ("Fixed band-split surrogate on the synthetic "
                             "mixture only; not Conv-TasNet and unqualified."),
            },
            "target_leakage": {
                "status": "synthetic_only",
                "evidence": ("Independent orthogonal-projection interference "
                             "leakage per synthetic source."),
            },
            "target_damage": {
                "status": "synthetic_only",
                "evidence": ("Zero-mean SI-SDR and level change per synthetic "
                             "source; no listening or downstream score."),
            },
            "channel_loss": {
                "status": "synthetic_only",
                "evidence": ("Mono fixture has no channel to lose; only "
                             "missing-source and no-substitution probes."),
            },
            "room_reference_change": {
                "status": "synthetic_only",
                "evidence": ("Reference-order swap replay on identical "
                             "synthetic mixture bytes; no room change."),
            },
            "listening": {
                "status": "blocked",
                "evidence": ("No permitted listening or MUSHRA-style result "
                             "exists."),
            },
        },
    }


def _profile_blockers(profile: Dict[str, Any]) -> List[str]:
    return sorted(name for name, item in profile["required_items"].items()
                  if item["status"] == "blocked")


def _release_gates() -> List[Dict[str, str]]:
    rows = [
        ("RG-01", "Exact pinned Conv-TasNet source, weights and runtime with "
                  "an immutable revision, license identity, parameter "
                  "geometry and declared adapter settings."),
        ("RG-02", "Isolated hash-pinned runtime admission, reproducible build, "
                  "verified weight identity and fail-closed absent behavior."),
        ("RG-03", "Code, weight, training-data and corpus rights plus "
                  "attribution, notices, redistribution, product-use and "
                  "derivative-output review."),
        ("RG-04", "Exact candidate input rate, hop, window, source count, "
                  "permutation and output alignment mapped into the installed "
                  "mono stream with byte-level parity."),
        ("RG-05", "Task-matched held-out two-speaker separation qualification "
                  "with independently pinned permutation, SI-SDR, leakage, "
                  "target damage and channel/room/source-condition strata."),
        ("RG-06", "Streaming state, reset, latency, availability, source-count "
                  "change and nonfinite behavior at the exact runtime."),
        ("RG-07", "Target-device pacing, timing and memory with independent "
                  "listening and/or downstream ASR controls."),
        ("RG-08", "Opt-in provider intake, descriptor review, independent "
                  "exact-head review and default/release approval."),
    ]
    return [{"id": gate, "requirement": text, "status": "blocked"}
            for gate, text in rows]


def _exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "pinned_conv_tasnet_source_weights_runtime_absent",
            "requirement": ("Supply one exact licensed Conv-TasNet source "
                            "tree, weight file and runtime with immutable "
                            "revision, build/archive identity and declared "
                            "adapter settings."),
            "state": ("The pinned category registry names only the "
                      "Conv-TasNet paper (arXiv 1809.07454). No runnable "
                      "code, checkpoint, runtime, adapter or revision is "
                      "staged at data/checkouts/Conv-TasNet, "
                      "data/models/conv-tasnet, data/envs/conv-tasnet or "
                      "adapters/conv-tasnet."),
        },
        {
            "id": "candidate_io_geometry_and_permutation_unverified",
            "requirement": ("Document the exact Conv-TasNet input rate, hop, "
                            "window, source count, encoder/mask geometry, "
                            "permutation policy and output alignment for the "
                            "pinned weights."),
            "state": ("The pinned evidence records only a paper reference. It "
                      "records no sample rate, hop, window, source count, "
                      "parameter count, permutation policy or numeric output, "
                      "so no candidate geometry is asserted."),
        },
        {
            "id": "rights_attribution_and_weights_review_absent",
            "requirement": ("Stage the exact code and weight license, "
                            "attribution notice, training-data terms and "
                            "complete distribution, derivative and product-use "
                            "review."),
            "state": ("No upstream LICENSE, model card, weight terms, "
                      "training-data statement, notice bundle or legal review "
                      "is staged. The paper link is not a code or weight "
                      "license."),
        },
        {
            "id": "mono_separation_contract_and_sdk_integration_absent",
            "requirement": ("Admit a mono two-output separation boundary and "
                            "map Conv-TasNet source count, permutation and "
                            "alignment into the installed SDK path with exact "
                            "parity."),
            "state": ("Installed v0 accepts one 16 kHz mono 160-sample "
                      "float32 stream and returns one stream. No accepted "
                      "multi-output separation contract, descriptor, registry "
                      "entry or output-channel mapping exists."),
        },
        {
            "id": "rights_cleared_two_speaker_cohort_absent",
            "requirement": ("Supply a rights-cleared task-matched held-out "
                            "two-speaker cohort with mixture/clean pairs, "
                            "source labels and strata plus SI-SDR, leakage, "
                            "damage and listening or downstream scores."),
            "state": ("No real recording, speaker consent, corpus terms, "
                      "held-out split, source label or task-matched score is "
                      "staged. Synthetic band-disjoint integer fixtures "
                      "cannot qualify the candidate."),
        },
        {
            "id": "timing_and_independent_review_absent",
            "requirement": ("Measure target-device pacing, latency, memory, "
                            "reset and source-count behavior at the exact "
                            "runtime and complete independent review."),
            "state": ("No device clock, deadline, RTF, memory, worker, queue, "
                      "listening, benchmark, provider intake or release "
                      "approval exists; no result may qualify."),
        },
    ]


def _licensing() -> Dict[str, Any]:
    return {
        "reported_upstream_license": None,
        "license_text_staged": False,
        "attribution_required": True,
        "attribution_notice_staged": False,
        "weights_terms_staged": False,
        "training_data_statement_staged": False,
        "redistribution_reviewed": False,
        "product_use_reviewed": False,
        "review_status": "blocked",
        "note": ("The pinned registry records an arXiv paper link only. No "
                 "code license, weight terms, upstream license text or "
                 "training-data statement is staged."),
    }


def _candidate() -> Dict[str, Any]:
    return {
        "name": "Conv-TasNet",
        "paper_reference": CANDIDATE_PAPER_REFERENCE,
        "reported_algorithm": ("catalogued paper reference only; no runnable "
                               "code or weight is staged"),
        "reported_parameter_count": None,
        "reported_input_sample_rate_hz": None,
        "reported_hop_samples": None,
        "reported_window_samples": None,
        "reported_source_count": None,
        "geometry_documented": False,
        "source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "exact_numeric_output_present": False,
    }


def _external_artifacts() -> Dict[str, Any]:
    paths = {
        "source_checkout_lower": "data/checkouts/conv-tasnet",
        "source_checkout_upper": "data/checkouts/Conv-TasNet",
        "weights": "data/models/conv-tasnet",
        "runtime_env": "data/envs/conv-tasnet",
        "adapter": "adapters/conv-tasnet",
        "caller_manifest": "data/manifests/conv-tasnet.json",
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
        "real_speech": False,
        "real_paired_audio": False,
        "real_room_response": False,
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
    "No Conv-TasNet source, weight file, runtime, adapter, revision or "
    "numeric output was produced, loaded or executed.",
    "No separation quality, SI-SDR, leakage, latency, benchmark, listening or "
    "release result is claimed for Conv-TasNet.",
    "The synthetic complementary band-split surrogate is not Conv-TasNet and "
    "cannot qualify the candidate.",
    "No Conv-TasNet input rate, hop, window, source count, parameter count or "
    "output alignment is asserted.",
    "Synthetic SI-SDR, leakage and target-damage values are unqualified "
    "task-local observations only.",
    "No real speech, two-speaker corpus, pair labels, device clock or listener "
    "was used.",
    "No upstream license text, attribution bundle, weight terms or training "
    "data statement is staged.",
    "No provider, descriptor, registry, installed v0 path, shared build, "
    "dependency lock or CI was changed.",
)

REOPEN_CONDITION = (
    "Pin the exact licensed Conv-TasNet source, weights and runtime with an "
    "immutable revision and documented geometry, admit an isolated hash-pinned "
    "runtime, clear code/weight/training-data/corpus rights, admit a mono "
    "two-output separation boundary with exact parity, pin the permutation and "
    "leakage scoring independently, reproduce exact output, qualify separation "
    "on a rights-cleared task-matched held-out two-speaker cohort, measure "
    "target timing and complete opt-in provider intake. Until then the "
    "candidate stays DEFER, incomplete and not qualified."
)


def _case_matrix_digest(run: Dict[str, Any], alignment: Dict[str, Any],
                        order: Dict[str, Any], streaming: Dict[str, Any],
                        reset: Dict[str, Any]) -> str:
    return object_digest({
        "signals": run["signal_digests"],
        "rows": [(row["source_index"], row["output_index"],
                  row["evaluation_si_sdr_millidb"],
                  row["interference_leakage_millidb"])
                 for row in run["rows"]],
        "permutation": (run["permutation"]["chosen_assignment"],
                        run["permutation"]["oracle_evaluation_assignment"],
                        run["permutation"]["margin_millidb"]),
        "alignment": (alignment["estimated_peak_lag_samples"],
                      alignment["one_sample_shift_score_millidb"]),
        "source_order": (order["original_assignment"],
                         order["swapped_assignment"]),
        "streaming": streaming["all_match"],
        "reset": reset["state_digest"],
    })


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()
    model = separation_model_spec()
    scoring = scoring_protocol_spec()
    validate_separation_model(model)
    validate_scoring_protocol(scoring)
    model_digest = object_digest(model)
    scoring_digest = object_digest(scoring)
    _require(model_digest == SEPARATION_MODEL_SHA256,
             "separation_model_pin_mismatch")
    _require(scoring_digest == SCORING_PROTOCOL_SHA256,
             "scoring_protocol_pin_mismatch")
    fixture = fixture_run()
    alignment = alignment_probe(fixture)
    order = source_order_probe(fixture)
    channel = channel_loss_probe(fixture)
    streaming = streaming_check(fixture)
    reset = reset_check()
    partial = final_partial_check()
    profile = _acceptance_profile()
    adverse = adverse_rejections()
    gates = _release_gates()
    blockers = _exact_blockers()
    licensing = _licensing()
    candidate = _candidate()
    matrix = _case_matrix_digest(fixture, alignment, order, streaming, reset)

    si_values = [row["evaluation_si_sdr_millidb"] for row in fixture["rows"]]
    leakage_values = [row["interference_leakage_millidb"]
                      for row in fixture["rows"]]
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
            "candidate_reported_sample_rate_hz": None,
            "candidate_reported_hop_samples": None,
            "candidate_reported_source_count": None,
            "candidate_geometry_documented": False,
            "multi_output_in_installed_v0": False,
            "separation_reference_contract": (
                "audio-sdk/mono-two-output-separation/0.1 proposal only"),
            "resampling": "none",
            "surrogate_content_delay_samples": CONTENT_DELAY_SAMPLES,
            "surrogate_separated_source_count": SOURCE_COUNT,
        },
        "separation_model": {
            "spec": model,
            "sha256": model_digest,
            "is_conv_tasnet": False,
            "is_learned": False,
            "uses_weights": False,
            "uses_encoder_mask_decoder": False,
            "source_count": SOURCE_COUNT,
            "content_delay_samples": CONTENT_DELAY_SAMPLES,
            "qualifies": False,
        },
        "scoring": {
            "spec": scoring,
            "sha256": scoring_digest,
            "independently_pinned": True,
            "permutation_uses_calibration_only": True,
            "oracle_used_for_score": False,
            "qualifies": False,
        },
        "fixtures": {
            "synthetic_only": True,
            "audio_generated": False,
            "geometry": fixture_spec(),
            "signal_digests": fixture["signal_digests"],
        },
        "separation": {
            "sources": fixture["rows"],
            "min_evaluation_si_sdr_millidb": min(si_values),
            "max_evaluation_si_sdr_millidb": max(si_values),
            "max_interference_leakage_millidb": max(leakage_values),
            "min_improvement_over_mixture_millidb": min(
                row["improvement_millidb"] for row in fixture["rows"]),
            "nonfinite_output_count": fixture["nonfinite_output_count"],
            "qualifies": False,
        },
        "permutation": fixture["permutation"],
        "control": {
            "name": "mixture_passthrough",
            "evaluation_si_sdr_millidb": [
                row["mixture_control_si_sdr_millidb"]
                for row in fixture["rows"]],
            "qualifies": False,
        },
        "alignment": alignment,
        "source_order_change": order,
        "channel_loss": channel,
        "final_partial": partial,
        "streaming": streaming,
        "reset": reset,
        "nonfinite": {
            "rejected_nonfinite_inputs": sum(
                1 for case in adverse
                if "nonfinite_input" in case["code"]),
            "output_nonfinite_count": fixture["nonfinite_output_count"],
            "output_finite": fixture["nonfinite_output_count"] == 0,
            "max_peak_milli": max(row["peak_milli"]
                                  for row in fixture["rows"]),
            "qualifies": False,
        },
        "adverse_rejections": adverse,
        "adverse_all_rejected": all(
            row["status"] == "rejected" and row["state_unchanged"] is True
            for row in adverse),
        "external_artifacts": _external_artifacts(),
        "licensing": licensing,
        "caller_asset": {
            "contract_id":
                "audio-sdk/conv-tasnet/caller-supplied-asset/0.1",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "manifest_present": False,
            "workspace_manifest": "data/manifests/conv-tasnet.json",
            "present_behavior": ("validate_declaration_identity_only; do_not_"
                                 "load_or_execute"),
            "absent_behavior": "reject_before_processing",
            "required_fields": sorted(CALLER_MANIFEST_FIELDS),
            "declaration_only": True,
            "candidate_geometry_verified": False,
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
            "candidate_geometry_documented": False,
            "separation_model_pinned": False,
            "permutation_pinned": False,
            "rights_cleared_cohort": False,
            "task_matched_heldout_score": False,
            "leakage_measured_on_heldout": False,
            "timing_measured": False,
            "listening": False,
            "real_corpus_used": False,
            "reason": ("Exact Conv-TasNet source/weights/runtime, candidate "
                       "geometry, rights, mono two-output admission, "
                       "rights-cleared held-out two-speaker data, timing and "
                       "independent review are all absent. Only the "
                       "task-local surrogate model and scoring protocol are "
                       "pinned."),
        },
        "exact_blockers": blockers,
        "release_gates": gates,
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "surrogate": {
            "algorithm": ("fixed complementary 25-tap integer low/high band "
                          "splitter with a 12-sample delayed-input high band"),
            "is_conv_tasnet": False,
            "is_learned": False,
            "uses_encoder_mask_decoder": False,
            "uses_weights": False,
            "qualifies_candidate": False,
        },
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "case_matrix_digests": [matrix, matrix, matrix],
        },
        "scope_note": ("Only docs/task-evidence/conv-tasnet/ is written; all "
                       "other paths are read-only pins."),
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
        "separation_model": report["separation_model"],
        "scoring": report["scoring"],
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
            "contract_id":
                "audio-sdk/conv-tasnet/caller-supplied-asset/0.1",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "required_fields": sorted(CALLER_MANIFEST_FIELDS),
            "present_behavior": ("validate_declaration_identity_only; do_not_"
                                 "load_or_execute"),
            "absent_behavior": "reject_before_processing",
            "separate_archive_required": True,
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no Conv-TasNet source, weight, learned encoder, mask network, "
            "decoder, runtime or adapter is downloaded, copied, loaded or "
            "executed",
            "the synthetic band-split surrogate is not Conv-TasNet and cannot "
            "qualify the candidate",
            "no candidate input rate, hop, window, source count, parameter "
            "count or output alignment is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def sources_bytes(overrides: Dict[str, bytes] | None = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-CONV-TASNET; source: paths are "
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
    "BandSplitSeparator", "ReferenceRejection", "adverse_rejections",
    "alignment_probe", "board_row", "build_contract", "build_fixture",
    "build_report", "canonical_report", "canonical_text", "channel_loss_probe",
    "chunk_plan", "final_partial_check", "fixture_run", "fixture_spec",
    "int_signal_digest", "leakage_millidb", "level_change_millidb",
    "load_strict_json", "load_strict_json_text", "object_digest",
    "reset_check", "run_stream", "scoring_protocol_spec",
    "separation_model_spec", "sha256_bytes", "si_sdr_millidb",
    "signal_digest", "source_order_probe", "sources_bytes",
    "streaming_check", "validate_caller_manifest", "validate_config",
    "validate_fixture", "validate_scoring_protocol",
    "validate_separation_model",
]
