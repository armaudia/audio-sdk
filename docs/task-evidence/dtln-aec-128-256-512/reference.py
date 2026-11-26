# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local DTLN-AEC 128/256/512 feasibility evidence.

This is an original, stdlib-only synthetic probe written for this task. It is
NOT DTLN-AEC source, a TFLite graph, a licensed DTLN-AEC runtime, a DTLN-AEC
weight file or a DTLN-AEC result. No upstream code, recurrent state, mask
network, weight, corpus or audio asset is present, copied, downloaded, loaded or
executed.

The probe consumes caller-owned paired 16 kHz mono float32 microphone and
far-end render hops at the documented DTLN-AEC 512-sample block / 128-sample hop
geometry, runs a bounded integer-tap NLMS echo canceller and a deterministic
residual-energy gate through a 512/128 overlap-add frame clock, and measures
echo attenuation, near-end preservation, overlap behavior, delayed/missing
render failure and nonfinite rejection on frozen synthetic signals.

It exists only to exercise strict parsing, exact fixture arithmetic, online
state, reset, block invariance and adverse rejection at a task-local proposal
boundary. It is proposal-only, incomplete and not qualified. The exact DTLN-AEC
source, the 128/256/512 checkpoints, the TFLite runtime and the rights record
are absent and recorded as blockers.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import platform
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

VERSION = "0.1.0"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
REPORT_SCHEMA = "audio-sdk/dtln-aec-128-256-512-report/0.1"
TASK_ID = "SDK-DTLN-AEC-128-256-512"
TITLE = "DTLN-AEC 128/256/512"
COMPONENT = "dtln-aec-128-256-512"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "7c6653f5a7db7f6de34ad709a96a455a9ad3263a"
BRANCH = "swarm/SDK-DTLN-AEC-128-256-512"
REVIEWER = "reviewer-DTLN-AEC-128-256-512"
PROFILE = "room"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
STATUS = "proposal_only_synthetic_incomplete"

# Installed public v0 geometry, documented and preserved, never changed here.
SDK_RATE_HZ = 16000
SDK_CHANNELS = 1
SDK_FRAME_SAMPLES = 160
SDK_SAMPLE_FORMAT = "float32"

# Task-local probe geometry. The DTLN-AEC adapter documents 16 kHz mono with a
# 512-sample analysis block and 128-sample hops; the model's own content delay,
# recurrent-state shapes and numeric output are not documented or measured.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
BLOCK_SAMPLES = 512
HOP_SAMPLES = 128
MAGNITUDE_BINS = 257
SAMPLE_FORMAT = "float32"
SAMPLE_NS = 62500
SURROGATE_FRAMING_DELAY = BLOCK_SAMPLES - HOP_SAMPLES  # 384, surrogate only

UNIT_VARIANTS: Tuple[int, ...] = (128, 256, 512)
VARIANT_IDS: Tuple[str, ...] = tuple(f"dtln_aec_{units}"
                                    for units in UNIT_VARIANTS)

FIXTURE_LENGTH = 8192
TAIL_SAMPLES = 64
RENDER_DELAY_SAMPLES = 16
MU_NUM = 35
MU_DEN = 100
GAIN_FLOOR_MILLI = 250
GAIN_FULL_SNR_MILLI = 4000
NOISE_FLOOR_DECAY_NUM = 1
NOISE_FLOOR_DECAY_DEN = 2
NOISE_FLOOR_RISE_NUM = 1
NOISE_FLOOR_RISE_DEN = 2000
NONFINITE_FLOOR_MILLIDB = -999000
MAX_REPORTED_ERLE_MILLIDB = 999000
INT_SCALE = 32768.0
INT_SCALE_SQ = INT_SCALE * INT_SCALE

# Candidate facts documented by the local adapter README only.
CANDIDATE_SOURCE_URL = "https://github.com/breizhn/DTLN-aec"
CANDIDATE_PAPER_DOI = "10.1109/ICASSP39728.2021.9413510"
CANDIDATE_REPORTED_BLOCK = 512
CANDIDATE_REPORTED_HOP = 128
CANDIDATE_REPORTED_RATE_HZ = 16000
CANDIDATE_REPORTED_UNIT_VARIANTS: Tuple[int, ...] = UNIT_VARIANTS

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

ECHO_TAPS_BEFORE: Tuple[Tuple[int, int], ...] = (
    (0, 700), (4, 340), (8, -200), (12, 120), (16, 70), (20, -40), (24, 25),
)
ECHO_TAPS_AFTER: Tuple[Tuple[int, int], ...] = (
    (0, 480), (4, -300), (8, 240), (12, -150), (16, 80), (20, 45), (24, -30),
)
PATH_SWITCH_SAMPLE = 6144

SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"name": "echo_only_initial", "start": 0, "end": 2048,
     "render": True, "near": False, "noise_amplitude": 20},
    {"name": "near_only_clean", "start": 2048, "end": 4096,
     "render": False, "near": True, "noise_amplitude": 20},
    {"name": "overlap_double_talk", "start": 4096, "end": 6144,
     "render": True, "near": True, "noise_amplitude": 80},
    {"name": "echo_only_after_path_change", "start": 6144, "end": 7168,
     "render": True, "near": False, "noise_amplitude": 20},
    {"name": "near_only_noisy", "start": 7168, "end": 8192,
     "render": False, "near": True, "noise_amplitude": 120},
)
SEGMENT_KEYS = {"name", "start", "end", "render", "near", "noise_amplitude"}
ERLE_REGIONS = (
    ("echo_only_initial", 1024, 2048),
    ("echo_only_after_path_change", 6656, 7168),
)
NEAR_REGIONS = (
    ("near_only_clean", 2048, 4096),
    ("near_only_noisy", 7168, 8192),
)
OVERLAP_REGION = ("overlap_double_talk", 4096, 6144)
ALIGNMENT_PROBE_END = 2048
ALIGNMENT_REGION = (1024, 2048)
DELAYED_RENDER_SAMPLES = 256
FINAL_PARTIAL_VALID = 100

SOURCE_PINS = {
    "research/aec_research_20261028.md": (
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180"
    ),
    "research/voice-enhancement-20261101/evaluation_records.md": (
        "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a"
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
    "adapters/dtln-aec/README.md": (
        "d19deb34e849fdb19fa3bf942ccb285397252fb233e67ce23a41bc1eda0524c5"
    ),
    "adapters/dtln-aec/run.py": (
        "526a293faa68241f513c7fba5633f33a2429d65fee25a100c0fe4409baa53e98"
    ),
    "tests/test_dtln_aec_adapter.py": (
        "bcc1405d17a50bb426fc047e1658c60b38338d2022d758053ee1fbba65d5699e"
    ),
    "data/checkouts/DTLN/pretrained_model/model_1.tflite": (
        "91281a38e80fe9fd330e28eda7e16fe4e483ee5199a3e687a099939013c25de0"
    ),
    "data/checkouts/DTLN/pretrained_model/model_2.tflite": (
        "7ae37ec802862d8a65b5cdabfbcbbe22caaf7cd39e79adf574d15837d1520830"
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
    "docs/task-evidence/dtln-onnx/README.md": (
        "aa4d3f0e1f75730c7e1e13f8ed1e75291eeb863d0f64284459b97d0b669d5abe"
    ),
    "docs/task-evidence/dtln-onnx/contract.json": (
        "a498c80cdf8f764af8e102f986e6c39a3e4fa8757cdb2e95495a73214324947b"
    ),
    "docs/task-evidence/dtln-onnx/report.json": (
        "db37b4c88bf81bca5e0397dd3fcb5d45ffccf95a217cd1f59e198f2fae562bdf"
    ),
    "docs/task-evidence/cagcrn-joint-aec-and-ns/README.md": (
        "aeae96f49acad572294b69cafb1b581392c3c3c11171d60545eadd6ede3187c7"
    ),
    "docs/task-evidence/cagcrn-joint-aec-and-ns/contract.json": (
        "28870f4d014b198b05bde47c299250ae280442353696bf228f70caf146070668"
    ),
    "docs/task-evidence/cagcrn-joint-aec-and-ns/report.json": (
        "697eb9feb470d529ba8132a8d597cb52308f46f5d2c6afd36803de268f9d7828"
    ),
    "docs/task-evidence/erle-and-double-talk-preservation/README.md": (
        "0f8ddc78f41459734f4ed096eb71789ecf5bcc809d833c5b65f63319ef11db2e"
    ),
    "docs/task-evidence/nlms-aec/report.json": (
        "2910e9e986259a9de738822c35a2908e47a836a9daabc292118f6c7389988f6a"
    ),
    "docs/task-evidence/webrtc-aec3/report.json": (
        "da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283"
    ),
    "docs/task-evidence/aec-challenge-paired-render-capture-fixtures/README.md": (
        "de5b37cb55275da0f130c2eb524c15f4f12fed18171725596156789ef8b41ccf"
    ),
}

BOARD_ROW_STABLE_SHA256 = (
    "3fa62c1416835948a9d1e78f6eb5a3a9249f9654e4d852fb2a9b3251e514626b"
)

TASK_PREFIX = "docs/task-evidence/dtln-aec-128-256-512/"
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
        return MAX_REPORTED_ERLE_MILLIDB
    if numerator <= 0.0:
        return NONFINITE_FLOOR_MILLIDB
    value = 1000.0 * 10.0 * math.log10(numerator / denominator)
    return int(round(value))


# ---------------------------------------------------------------------------
# Frozen synthetic fixture
# ---------------------------------------------------------------------------

FIXTURE_KEYS = {"length_samples", "segments", "path_switch_sample",
                "echo_taps_before", "echo_taps_after", "render_delay_samples"}


def fixture_spec() -> Dict[str, Any]:
    return {
        "length_samples": FIXTURE_LENGTH,
        "segments": [dict(segment) for segment in SEGMENTS],
        "path_switch_sample": PATH_SWITCH_SAMPLE,
        "echo_taps_before": [list(tap) for tap in ECHO_TAPS_BEFORE],
        "echo_taps_after": [list(tap) for tap in ECHO_TAPS_AFTER],
        "render_delay_samples": RENDER_DELAY_SAMPLES,
    }


def validate_fixture(spec: Dict[str, Any]) -> None:
    _exact_keys(spec, FIXTURE_KEYS, "fixture")
    length = _integer(spec["length_samples"], "length_samples", HOP_SAMPLES,
                      200000)
    _require(length == FIXTURE_LENGTH, "fixture_length_mismatch")
    _require(length % HOP_SAMPLES == 0, "fixture_not_hop_aligned")
    switch = _integer(spec["path_switch_sample"], "path_switch_sample",
                      0, length)
    _require(switch == PATH_SWITCH_SAMPLE, "fixture_switch_mismatch")
    delay = _integer(spec["render_delay_samples"], "render_delay_samples",
                     0, TAIL_SAMPLES - 1)
    _require(delay == RENDER_DELAY_SAMPLES, "fixture_delay_mismatch")
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
        _require(isinstance(segment["render"], bool), "invalid_render_flag")
        _require(isinstance(segment["near"], bool), "invalid_near_flag")
        _integer(segment["noise_amplitude"], "noise_amplitude", 0, 1000)
        cursor = end
    _require(cursor == length, "segment_coverage_mismatch")
    for key in ("echo_taps_before", "echo_taps_after"):
        taps = spec[key]
        _require(isinstance(taps, list) and 1 <= len(taps) <= 32,
                 "invalid_echo_taps")
        previous = -1
        for tap in taps:
            _require(isinstance(tap, list) and len(tap) == 2,
                     "invalid_echo_tap")
            offset = _integer(tap[0], "tap_offset", 0, TAIL_SAMPLES - 1)
            _integer(tap[1], "tap_gain", -1024, 1024)
            _require(offset > previous, "tap_order_mismatch")
            previous = offset
        _require(delay + previous < TAIL_SAMPLES,
                 "tap_exceeds_filter_tail")


def _lcg_values(seed: int, count: int) -> List[int]:
    state = seed & 0x7FFFFFFF
    values: List[int] = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append((state % 65535) - 32767)
    return values


def _voice_values(count: int) -> List[int]:
    envelope = (0, 300, 900, 1600, 2400, 3000, 2600, 2000,
                1200, 500, 0, 0, 200, 700, 1400, 800)
    values: List[int] = []
    for index in range(count):
        tone = (3 * SINE64[index % 64]
                + 2 * SINE64[(2 * index + 7) % 64]
                + SINE64[(3 * index + 13) % 64]) // 6
        level = envelope[(index // 100) % len(envelope)]
        values.append(tone * level * 3500 // (32767 * 3000))
    return values


def _masked(values: Sequence[int], active: Sequence[bool]) -> List[int]:
    return [value if active[index] else 0
            for index, value in enumerate(values)]


def _segment_masks(length: int) -> Tuple[List[bool], List[bool], List[int]]:
    render = [False] * length
    near = [False] * length
    noise = [0] * length
    for segment in SEGMENTS:
        for index in range(segment["start"], segment["end"]):
            render[index] = bool(segment["render"])
            near[index] = bool(segment["near"])
            noise[index] = int(segment["noise_amplitude"])
    return render, near, noise


def echo_path(render: Sequence[int], switch_sample: int) -> List[int]:
    out = [0] * len(render)
    for index in range(len(render)):
        taps = (ECHO_TAPS_BEFORE if index < switch_sample
                else ECHO_TAPS_AFTER)
        total = 0
        for offset, gain in taps:
            source = index - RENDER_DELAY_SAMPLES - offset
            if source >= 0:
                total += render[source] * gain
        out[index] = total // 1024
    return out


def build_fixture() -> Dict[str, Any]:
    """Build the frozen synthetic paired render/capture signals."""
    validate_fixture(fixture_spec())
    render_mask, near_mask, noise_levels = _segment_masks(FIXTURE_LENGTH)
    render = _masked([value * 8000 // 32767
                      for value in _lcg_values(20261126, FIXTURE_LENGTH)],
                     render_mask)
    near = _masked(_voice_values(FIXTURE_LENGTH), near_mask)
    noise_base = _lcg_values(20261127, FIXTURE_LENGTH)
    noise = [noise_base[index] * noise_levels[index] // 32767
             for index in range(FIXTURE_LENGTH)]
    echo = echo_path(render, PATH_SWITCH_SAMPLE)
    mic = [max(-32768, min(32767, echo[index] + near[index] + noise[index]))
           for index in range(FIXTURE_LENGTH)]
    return {
        "render": render,
        "near": near,
        "noise": noise,
        "echo": echo,
        "mic": mic,
    }


# ---------------------------------------------------------------------------
# Task-local two-stage surrogate at the 512/128 frame clock
# ---------------------------------------------------------------------------

CONFIG_KEYS = {"sample_rate_hz", "channels", "block_samples", "hop_samples",
               "sample_format", "clock_ppm", "resampling",
               "render_delay_samples", "algorithmic_latency_samples"}


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the task-local probe configuration; fail closed."""
    _exact_keys(config, CONFIG_KEYS, "config")
    rate = _integer(config["sample_rate_hz"], "sample_rate_hz", 1, 384000)
    channels = _integer(config["channels"], "channels", 1, 8)
    block = _integer(config["block_samples"], "block_samples", 1, 4096)
    hop = _integer(config["hop_samples"], "hop_samples", 1, 4096)
    clock = _integer(config["clock_ppm"], "clock_ppm", -1000000, 1000000)
    delay = _integer(config["render_delay_samples"], "render_delay_samples",
                     0, 512)
    latency = _integer(config["algorithmic_latency_samples"],
                       "algorithmic_latency_samples", 0, 16000)
    _require(isinstance(config["sample_format"], str), "invalid_sample_format")
    _require(isinstance(config["resampling"], str), "invalid_resampling")
    if rate != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_sample_rate")
    if channels != CHANNELS:
        raise ReferenceRejection("unsupported_channels")
    if block != BLOCK_SAMPLES:
        raise ReferenceRejection("unsupported_block_samples")
    if hop != HOP_SAMPLES:
        raise ReferenceRejection("unsupported_hop_samples")
    if config["sample_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("unsupported_sample_format")
    if clock != 0:
        raise ReferenceRejection("unsupported_clock_drift")
    if config["resampling"] != "none":
        raise ReferenceRejection("unsupported_resampling")
    if delay != RENDER_DELAY_SAMPLES:
        raise ReferenceRejection("unsupported_render_delay")
    if latency != 0:
        raise ReferenceRejection("unsupported_algorithmic_latency")
    return {"sample_rate_hz": rate, "channels": channels,
            "block_samples": block, "hop_samples": hop,
            "sample_format": config["sample_format"],
            "clock_ppm": clock, "resampling": config["resampling"],
            "render_delay_samples": delay,
            "algorithmic_latency_samples": latency}


def _validate_paired_hop(mic: object, render: object,
                         valid_count: object) -> int:
    count = _integer(valid_count, "valid_count", 1, HOP_SAMPLES)
    for label, values in (("mic", mic), ("render", render)):
        if values is None:
            raise ReferenceRejection("missing_input" if label == "mic"
                                     else "missing_render")
        if not isinstance(values, (list, tuple)):
            raise ReferenceRejection("invalid_frame:" + label)
        if len(values) != HOP_SAMPLES:
            raise ReferenceRejection("frame_count_mismatch:" + label)
        for index in range(count):
            value = values[index]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ReferenceRejection("invalid_sample:" + label)
            if not math.isfinite(float(value)):
                raise ReferenceRejection("nonfinite_input:" + label)
        for index in range(count, HOP_SAMPLES):
            value = values[index]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ReferenceRejection("invalid_sample:" + label)
            if float(value) != 0.0:
                raise ReferenceRejection("padding_not_zero:" + label)
    return count


class StreamingSurrogate:
    """Bounded NLMS echo canceller plus deterministic residual-energy gate.

    Stage 1 is a 64-tap integer-fed NLMS echo canceller over the far-end
    reference. Stage 2 is a deterministic gain on the per-hop residual energy.
    Both are processed through a 512-sample frame clock with 128-sample hops
    and overlap-add; the framing itself contributes a 384-sample
    block-minus-hop delay. This is not DTLN-AEC.
    """

    def __init__(self, sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = CHANNELS, block_samples: int = BLOCK_SAMPLES,
                 hop_samples: int = HOP_SAMPLES,
                 sample_format: str = SAMPLE_FORMAT, epoch: int = 1):
        if (sample_rate_hz != SAMPLE_RATE_HZ or channels != CHANNELS
                or block_samples != BLOCK_SAMPLES
                or hop_samples != HOP_SAMPLES
                or sample_format != SAMPLE_FORMAT):
            raise ReferenceRejection(
                "unsupported_config",
                "probe accepts only 16000/1/512/128/float32")
        if (not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1):
            raise ReferenceRejection("invalid_epoch")
        self.epoch = epoch
        self.position = 0
        self.hops = 0
        self.weights = [0.0] * TAIL_SAMPLES
        self.history = [0.0] * TAIL_SAMPLES
        self.history_position = 0
        self.noise_floor = 0.0
        self.last_gain_milli = 1000
        self.out_overlap = [0.0] * BLOCK_SAMPLES

    @property
    def state_digest(self) -> str:
        payload = struct.pack("<%dd" % TAIL_SAMPLES, *self.weights)
        payload += struct.pack("<%dd" % TAIL_SAMPLES, *self.history)
        payload += struct.pack("<%dd" % BLOCK_SAMPLES, *self.out_overlap)
        payload += struct.pack("<qqdqi", self.epoch, self.position,
                               self.noise_floor, self.history_position,
                               self.last_gain_milli)
        payload += struct.pack("<q", self.hops)
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
        self.hops = 0
        self.weights = [0.0] * TAIL_SAMPLES
        self.history = [0.0] * TAIL_SAMPLES
        self.history_position = 0
        self.noise_floor = 0.0
        self.last_gain_milli = 1000
        self.out_overlap = [0.0] * BLOCK_SAMPLES

    def _hop_gain_milli(self, residual: Sequence[float]) -> int:
        power = sum(value * value for value in residual) / len(residual)
        rms = math.sqrt(power)
        if self.noise_floor <= 0.0:
            self.noise_floor = rms
        elif rms < self.noise_floor:
            self.noise_floor = (NOISE_FLOOR_DECAY_NUM
                                * self.noise_floor
                                + (NOISE_FLOOR_DECAY_DEN
                                   - NOISE_FLOOR_DECAY_NUM) * rms) \
                / NOISE_FLOOR_DECAY_DEN
        else:
            self.noise_floor = (NOISE_FLOOR_RISE_NUM * rms
                                + (NOISE_FLOOR_RISE_DEN
                                   - NOISE_FLOOR_RISE_NUM)
                                * self.noise_floor) / NOISE_FLOOR_RISE_DEN
        floor = max(self.noise_floor, 1.0e-12)
        snr_milli = int(round(1000.0 * rms / floor))
        if snr_milli >= GAIN_FULL_SNR_MILLI:
            gain = 1000
        elif snr_milli <= 1000:
            gain = GAIN_FLOOR_MILLI
        else:
            gain = GAIN_FLOOR_MILLI + (
                (1000 - GAIN_FLOOR_MILLI) * (snr_milli - 1000)
                // (GAIN_FULL_SNR_MILLI - 1000))
        self.last_gain_milli = gain
        return gain

    def process_hop(self, mic: Sequence[float] | None,
                    render: Sequence[float] | None,
                    valid_count: int = HOP_SAMPLES,
                    epoch: int | None = None,
                    first_input_sample: int | None = None
                    ) -> Dict[str, Any]:
        count = _validate_paired_hop(mic, render, valid_count)
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

        residual: List[float] = []
        for index in range(count):
            capture = float(mic[index]) / INT_SCALE
            reference = float(render[index]) / INT_SCALE
            self.history[self.history_position] = reference
            newest = self.history[self.history_position::-1]
            oldest = self.history[:self.history_position:-1]
            window = newest + oldest
            estimate = 0.0
            for tap in range(TAIL_SAMPLES):
                estimate += self.weights[tap] * window[tap]
            error = capture - estimate
            residual.append(error)
            norm = 0.0
            for tap in range(TAIL_SAMPLES):
                norm += window[tap] * window[tap]
            coefficient = (MU_NUM / MU_DEN) * error / (norm + 1.0e-9)
            for tap in range(TAIL_SAMPLES):
                self.weights[tap] += coefficient * window[tap]
            self.history_position = (self.history_position + 1) \
                % TAIL_SAMPLES

        gain_milli = self._hop_gain_milli(residual)
        gated = [value * gain_milli / 1000.0 for value in residual]
        gated.extend([0.0] * (HOP_SAMPLES - count))
        frame = [0.0] * (BLOCK_SAMPLES - HOP_SAMPLES) + gated
        self.out_overlap = self.out_overlap[HOP_SAMPLES:] \
            + [0.0] * HOP_SAMPLES
        for index in range(BLOCK_SAMPLES):
            self.out_overlap[index] += frame[index]
        emitted = list(self.out_overlap[:HOP_SAMPLES])
        self.position += count
        self.hops += 1
        return {"emitted": emitted, "gated": gated, "residual": residual,
                "gain_milli": gain_milli}


# ---------------------------------------------------------------------------
# Streaming driver and metrics
# ---------------------------------------------------------------------------

def chunk_plan(total: int, pattern: Sequence[int] = (128, 256, 384, 640,
                                                     512, 128)) -> List[int]:
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


def run_stream(mic: Sequence[int], render: Sequence[int],
               chunks: Sequence[int] | None = None,
               epoch: int = 1) -> Dict[str, Any]:
    """Run the probe on paired signals; output is delayed by one block-hop.

    The paired signals are padded with one block-minus-hop of zeros so the
    frame clock can flush the queued content. ``aligned`` removes exactly that
    deterministic surrogate framing delay for scoring.
    """
    _require(len(mic) == len(render), "paired_length_mismatch")
    surrogate = StreamingSurrogate(epoch=epoch)
    mic_ext = list(mic) + [0] * SURROGATE_FRAMING_DELAY
    render_ext = list(render) + [0] * SURROGATE_FRAMING_DELAY
    plan = list(chunks) if chunks is not None else chunk_plan(len(mic_ext))
    _require(sum(plan) == len(mic_ext), "chunk_sum_mismatch")
    output: List[float] = []
    mic_buffer: List[int] = []
    render_buffer: List[int] = []
    offset = 0
    for chunk in plan:
        _require(chunk > 0, "invalid_chunk")
        end = offset + chunk
        mic_buffer.extend(mic_ext[offset:end])
        render_buffer.extend(render_ext[offset:end])
        offset = end
        while len(mic_buffer) >= HOP_SAMPLES:
            mic_hop = mic_buffer[:HOP_SAMPLES]
            render_hop = render_buffer[:HOP_SAMPLES]
            del mic_buffer[:HOP_SAMPLES]
            del render_buffer[:HOP_SAMPLES]
            result = surrogate.process_hop(mic_hop, render_hop)
            output.extend(result["emitted"])
    if mic_buffer:
        count = len(mic_buffer)
        mic_hop = mic_buffer + [0] * (HOP_SAMPLES - count)
        render_hop = render_buffer + [0] * (HOP_SAMPLES - count)
        result = surrogate.process_hop(mic_hop, render_hop,
                                       valid_count=count)
        output.extend(result["emitted"])
    _require(len(output) >= SURROGATE_FRAMING_DELAY + len(mic),
             "short_stream_output")
    aligned = output[SURROGATE_FRAMING_DELAY:
                     SURROGATE_FRAMING_DELAY + len(mic)]
    return {"output": output, "aligned": aligned,
            "state_digest": surrogate.state_digest,
            "samples": len(output)}


class NoiseGateOnly:
    """Independent no-reference control: gate the microphone, no AEC."""

    def __init__(self, epoch: int = 1):
        if (not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1):
            raise ReferenceRejection("invalid_epoch")
        self.epoch = epoch
        self.position = 0
        self.noise_floor = 0.0
        self.last_gain_milli = 1000

    def process_hop(self, mic: Sequence[int]) -> List[float]:
        _require(len(mic) == HOP_SAMPLES, "frame_count_mismatch:mic")
        values = [float(value) / INT_SCALE for value in mic]
        power = sum(value * value for value in values) / HOP_SAMPLES
        rms = math.sqrt(power)
        if self.noise_floor <= 0.0:
            self.noise_floor = rms
        elif rms < self.noise_floor:
            self.noise_floor = 0.5 * (self.noise_floor + rms)
        else:
            self.noise_floor = (rms + 1999 * self.noise_floor) / 2000
        floor = max(self.noise_floor, 1.0e-12)
        snr_milli = int(round(1000.0 * rms / floor))
        if snr_milli >= GAIN_FULL_SNR_MILLI:
            gain = 1000
        elif snr_milli <= 1000:
            gain = GAIN_FLOOR_MILLI
        else:
            gain = GAIN_FLOOR_MILLI + (
                (1000 - GAIN_FLOOR_MILLI) * (snr_milli - 1000)
                // (GAIN_FULL_SNR_MILLI - 1000))
        self.last_gain_milli = gain
        self.position += HOP_SAMPLES
        return [value * gain / 1000.0 for value in values]


def run_no_reference(mic: Sequence[int]) -> List[float]:
    gate = NoiseGateOnly()
    output: List[float] = []
    for offset in range(0, len(mic), HOP_SAMPLES):
        hop = list(mic[offset:offset + HOP_SAMPLES])
        hop.extend([0] * (HOP_SAMPLES - len(hop)))
        output.extend(gate.process_hop(hop))
    return output


def _region_metrics(mic: Sequence[int], output: Sequence[float],
                    near: Sequence[int], start: int, end: int) -> Dict[str, int]:
    mic_energy = _energy(mic, start, end) / INT_SCALE_SQ
    out_energy = _energy(output, start, end)
    near_energy = _energy(near, start, end) / INT_SCALE_SQ
    error_energy = 0.0
    for index in range(start, end):
        difference = float(output[index]) - float(near[index]) / INT_SCALE
        error_energy += difference * difference
    peak_milli = 0
    for index in range(start, end):
        value = abs(float(output[index]))
        if value * 1000.0 > peak_milli:
            peak_milli = int(round(value * 1000.0))
    return {
        "erle_millidb": _db_millidb(mic_energy, out_energy),
        "near_reference_snr_millidb": _db_millidb(near_energy, error_energy),
        "level_change_millidb": _db_millidb(out_energy, near_energy),
        "peak_milli": peak_milli,
    }


def _check_finite(samples: Sequence[float]) -> int:
    return sum(0 if math.isfinite(value) else 1 for value in samples)


def fixture_run(epoch: int = 1, chunks: Sequence[int] | None = None
                ) -> Dict[str, Any]:
    signals = build_fixture()
    run = run_stream(signals["mic"], signals["render"], chunks=chunks,
                     epoch=epoch)
    output = run["aligned"]
    mic_energy = _energy(signals["mic"], 0, FIXTURE_LENGTH) / INT_SCALE_SQ
    out_energy = _energy(output, 0, FIXTURE_LENGTH)
    erle_rows = []
    for name, start, end in ERLE_REGIONS:
        joint = _region_metrics(signals["mic"], output,
                                signals["near"], start, end)
        erle_rows.append({
            "segment": name,
            "start": start,
            "end": end,
            "erle_millidb": joint["erle_millidb"],
            "qualifies": False,
        })
    near_rows = []
    for name, start, end in NEAR_REGIONS:
        metrics = _region_metrics(signals["mic"], output,
                                  signals["near"], start, end)
        near_rows.append({
            "segment": name,
            "start": start,
            "end": end,
            "near_reference_snr_millidb": metrics[
                "near_reference_snr_millidb"],
            "level_change_millidb": metrics["level_change_millidb"],
            "peak_milli": metrics["peak_milli"],
            "qualifies": False,
        })
    overlap = _region_metrics(signals["mic"], output,
                              signals["near"], *OVERLAP_REGION[1:])
    return {
        "signals": signals,
        "run": run,
        "aligned": output,
        "overall": {
            "erle_millidb": _db_millidb(mic_energy, out_energy),
            "near_reference_snr_millidb": _region_metrics(
                signals["mic"], output, signals["near"], 0,
                FIXTURE_LENGTH)["near_reference_snr_millidb"],
            "nonfinite_output_count": _check_finite(output),
        },
        "erle_regions": erle_rows,
        "near_regions": near_rows,
        "overlap": {
            "segment": OVERLAP_REGION[0],
            "start": OVERLAP_REGION[1],
            "end": OVERLAP_REGION[2],
            "near_reference_snr_millidb": overlap[
                "near_reference_snr_millidb"],
            "level_change_millidb": overlap["level_change_millidb"],
            "peak_milli": overlap["peak_milli"],
            "qualifies": False,
        },
        "signal_digests": {
            "render": int_signal_digest(signals["render"]),
            "near": int_signal_digest(signals["near"]),
            "noise": int_signal_digest(signals["noise"]),
            "echo": int_signal_digest(signals["echo"]),
            "mic": int_signal_digest(signals["mic"]),
            "output": signal_digest(output),
        },
    }


def _erle_for_output(mic: Sequence[int], output: Sequence[float],
                     start: int, end: int) -> int:
    return _db_millidb(_energy(mic, start, end) / INT_SCALE_SQ,
                       _energy(output, start, end))


def alignment_run() -> Dict[str, Any]:
    signals = build_fixture()
    mic = signals["mic"][:ALIGNMENT_PROBE_END]
    render = signals["render"][:ALIGNMENT_PROBE_END]
    aligned = run_stream(mic, render)["aligned"]
    delayed_render = ([0] * DELAYED_RENDER_SAMPLES
                      + list(render[:-DELAYED_RENDER_SAMPLES]))
    delayed = run_stream(mic, delayed_render)["aligned"]
    missing = run_stream(mic, [0] * len(mic))["aligned"]
    start, end = ALIGNMENT_REGION
    aligned_erle = _erle_for_output(mic, aligned, start, end)
    delayed_erle = _erle_for_output(mic, delayed, start, end)
    missing_erle = _erle_for_output(mic, missing, start, end)
    return {
        "declared_render_delay_samples": RENDER_DELAY_SAMPLES,
        "surrogate_framing_delay_samples": SURROGATE_FRAMING_DELAY,
        "candidate_model_delay_measured": False,
        "aligned_erle_millidb": aligned_erle,
        "delayed_render_erle_millidb": delayed_erle,
        "missing_render_erle_millidb": missing_erle,
        "delayed_render_detected": delayed_erle + 6000 < aligned_erle,
        "missing_render_detected": missing_erle + 6000 < aligned_erle,
        "missing_render_hop_rejected": _expect_reject(
            "missing_render",
            lambda: StreamingSurrogate().process_hop(
                [0] * HOP_SAMPLES, None)) == "missing_render",
        "qualifies": False,
    }


def no_reference_comparison(run: Dict[str, Any]) -> Dict[str, Any]:
    signals = run["signals"]
    output = run_no_reference(signals["mic"])
    start, end = ERLE_REGIONS[0][1], ERLE_REGIONS[0][2]
    gate_erle = _erle_for_output(signals["mic"], output, start, end)
    aec_erle = run["erle_regions"][0]["erle_millidb"]
    near_start, near_end = NEAR_REGIONS[0][1], NEAR_REGIONS[0][2]
    gate_near = _region_metrics(signals["mic"], output,
                                signals["near"], near_start, near_end)
    aec_near = run["near_regions"][0]
    return {
        "control": "independent_no_reference_noise_gate",
        "control_echo_erle_millidb": gate_erle,
        "aec_echo_erle_millidb": aec_erle,
        "aec_echo_gain_over_control_millidb": aec_erle - gate_erle,
        "control_near_reference_snr_millidb": gate_near[
            "near_reference_snr_millidb"],
        "aec_near_reference_snr_millidb": aec_near[
            "near_reference_snr_millidb"],
        "control_peak_milli": gate_near["peak_milli"],
        "nonfinite_output_count": _check_finite(output),
        "qualifies": False,
    }


def streaming_check(offline: Dict[str, Any]) -> Dict[str, Any]:
    signals = offline["signals"]
    plan = chunk_plan(FIXTURE_LENGTH + SURROGATE_FRAMING_DELAY)
    streamed = run_stream(signals["mic"], signals["render"], chunks=plan)
    return {
        "chunks": plan,
        "accepted_samples": FIXTURE_LENGTH,
        "output_samples": len(streamed["output"]),
        "all_match": streamed["output"] == offline["run"]["output"],
        "offline_state_digest": offline["run"]["state_digest"],
        "streamed_state_digest": streamed["state_digest"],
        "scheduler_measured": False,
        "qualifies": False,
    }


def reset_check() -> Dict[str, Any]:
    signals = build_fixture()
    mic = signals["mic"][:ALIGNMENT_PROBE_END]
    render = signals["render"][:ALIGNMENT_PROBE_END]
    carried = StreamingSurrogate(epoch=1)
    mic_ext = mic + [0] * SURROGATE_FRAMING_DELAY
    render_ext = render + [0] * SURROGATE_FRAMING_DELAY
    offset = 0
    while offset < len(mic_ext):
        carried.process_hop(list(mic_ext[offset:offset + HOP_SAMPLES]),
                            list(render_ext[offset:offset + HOP_SAMPLES]))
        offset += HOP_SAMPLES
    carried.reset(2, 0)
    offset = 0
    while offset < len(mic_ext):
        carried.process_hop(list(mic_ext[offset:offset + HOP_SAMPLES]),
                            list(render_ext[offset:offset + HOP_SAMPLES]),
                            epoch=2)
        offset += HOP_SAMPLES
    fresh = run_stream(mic, render, epoch=2)
    return {
        "epoch": 2,
        "accepted_samples": len(mic),
        "matches_fresh": carried.state_digest == fresh["state_digest"],
        "state_digest": carried.state_digest,
        "qualifies": False,
    }


def final_partial_check() -> Dict[str, Any]:
    signals = build_fixture()
    carrier = StreamingSurrogate(epoch=1)
    hop = list(signals["mic"][:FINAL_PARTIAL_VALID])
    reference = list(signals["render"][:FINAL_PARTIAL_VALID])
    hop.extend([0] * (HOP_SAMPLES - FINAL_PARTIAL_VALID))
    reference.extend([0] * (HOP_SAMPLES - FINAL_PARTIAL_VALID))
    result = carrier.process_hop(hop, reference,
                                 valid_count=FINAL_PARTIAL_VALID)
    gated = result["gated"]
    return {
        "valid_count": FINAL_PARTIAL_VALID,
        "padding_zero": all(value == 0.0
                            for value in gated[FINAL_PARTIAL_VALID:]),
        "output_samples": len(result["emitted"]),
        "advanced_samples": carrier.position,
        "tail_zero": all(value == 0.0
                         for value in gated[FINAL_PARTIAL_VALID:]),
        "nonfinite_output_count": _check_finite(result["emitted"]),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied DTLN-AEC asset identity (never loaded or executed)
# ---------------------------------------------------------------------------

CALLER_MANIFEST_FIELDS = {
    "variant",
    "stage1_path", "stage1_sha256", "stage1_bytes",
    "stage2_path", "stage2_sha256", "stage2_bytes",
    "sample_rate_hz", "channels", "block_samples", "hop_samples",
    "input_format", "source_commit", "source_sha256",
    "runtime", "runtime_version", "declared_content_delay_samples",
}
RUNTIME_IDS = {"tflite_runtime", "tensorflow"}


def validate_caller_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Validate caller-supplied identity only; never open, load or execute."""
    _exact_keys(manifest, CALLER_MANIFEST_FIELDS, "caller_manifest")
    variant = _string(manifest["variant"], "variant", 1, 64)
    if variant not in VARIANT_IDS:
        raise ReferenceRejection("unsupported_variant")
    rate = _integer(manifest["sample_rate_hz"], "sample_rate_hz", 1, 384000)
    channels = _integer(manifest["channels"], "channels", 1, 8)
    block = _integer(manifest["block_samples"], "block_samples", 1, 4096)
    hop = _integer(manifest["hop_samples"], "hop_samples", 1, 4096)
    _integer(manifest["stage1_bytes"], "stage1_bytes", 1, 2 ** 31 - 1)
    _integer(manifest["stage2_bytes"], "stage2_bytes", 1, 2 ** 31 - 1)
    _integer(manifest["declared_content_delay_samples"],
             "declared_content_delay_samples", 0, 16000)
    if rate != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_sample_rate")
    if channels != CHANNELS:
        raise ReferenceRejection("unsupported_channels")
    if block != BLOCK_SAMPLES:
        raise ReferenceRejection("unsupported_block_samples")
    if hop != HOP_SAMPLES:
        raise ReferenceRejection("unsupported_hop_samples")
    if manifest["input_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("unsupported_sample_format")
    runtime = _string(manifest["runtime"], "runtime", 1, 32)
    if runtime not in RUNTIME_IDS:
        raise ReferenceRejection("unsupported_runtime")
    _string(manifest["runtime_version"], "runtime_version", 1, 32)
    stage1 = _absolute_path(manifest["stage1_path"], "stage1_path")
    stage2 = _absolute_path(manifest["stage2_path"], "stage2_path")
    if stage1 == stage2:
        raise ReferenceRejection("duplicate_stage_path")
    if stage1.rsplit("/", 1)[-1] != variant + "_1.tflite":
        raise ReferenceRejection("stage1_name_mismatch")
    if stage2.rsplit("/", 1)[-1] != variant + "_2.tflite":
        raise ReferenceRejection("stage2_name_mismatch")
    _sha256(manifest["stage1_sha256"], "stage1_sha256")
    _sha256(manifest["stage2_sha256"], "stage2_sha256")
    _sha256(manifest["source_sha256"], "source_sha256")
    _commit(manifest["source_commit"], "source_commit")
    return {"validated": True, "loaded": False, "executed": False,
            "imported": False}


def runtime_probe() -> Dict[str, Any]:
    """Probe runtime importability only; never import or invoke a runtime."""
    def available(name: str) -> bool:
        try:
            return importlib.util.find_spec(name) is not None
        except (ImportError, ValueError):
            return False

    return {
        "tflite_runtime_importable": available("tflite_runtime"),
        "tensorflow_importable": available("tensorflow"),
        "interpreter": "CPython %d.%d.%d" % sys.version_info[:3],
        "platform": platform.system() + " " + platform.machine(),
    }


def gate_caller_assets(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Fail-closed identity/size/hash/runtime gate; never loads or executes."""
    validate_caller_manifest(manifest)
    for stage in ("stage1", "stage2"):
        path = Path(manifest[stage + "_path"])
        if not path.is_file():
            return {"status": "blocked_asset_absent", "stage": stage,
                    "loaded": False, "executed": False, "imported": False}
        if path.stat().st_size != manifest[stage + "_bytes"]:
            return {"status": "blocked_size_mismatch", "stage": stage,
                    "loaded": False, "executed": False, "imported": False}
        if file_digest(path) != manifest[stage + "_sha256"]:
            return {"status": "blocked_hash_mismatch", "stage": stage,
                    "loaded": False, "executed": False, "imported": False}
    probe = runtime_probe()
    if manifest["runtime"] == "tflite_runtime":
        available = probe["tflite_runtime_importable"]
    else:
        available = probe["tensorflow_importable"]
    if not available:
        return {"status": "blocked_runtime_unavailable",
                "stage": None, "loaded": False, "executed": False,
                "imported": False}
    return {"status": "eligible_unexecuted", "stage": None,
            "loaded": False, "executed": False, "imported": False}


# ---------------------------------------------------------------------------
# Adverse rejection matrix
# ---------------------------------------------------------------------------

def _base_config() -> Dict[str, Any]:
    return {"sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
            "block_samples": BLOCK_SAMPLES, "hop_samples": HOP_SAMPLES,
            "sample_format": SAMPLE_FORMAT, "clock_ppm": 0,
            "resampling": "none",
            "render_delay_samples": RENDER_DELAY_SAMPLES,
            "algorithmic_latency_samples": 0}


def _base_manifest() -> Dict[str, Any]:
    return {
        "block_samples": 512,
        "channels": 1,
        "declared_content_delay_samples": 0,
        "hop_samples": 128,
        "input_format": "float32",
        "runtime": "tflite_runtime",
        "runtime_version": "2.14.0",
        "sample_rate_hz": 16000,
        "source_commit": "0" * 40,
        "source_sha256": "1" * 64,
        "stage1_bytes": 1000,
        "stage1_path": "/caller-assets/dtln-aec/dtln_aec_128_1.tflite",
        "stage1_sha256": "2" * 64,
        "stage2_bytes": 2000,
        "stage2_path": "/caller-assets/dtln-aec/dtln_aec_128_2.tflite",
        "stage2_sha256": "3" * 64,
        "variant": "dtln_aec_128",
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
                                 if key != "render_delay_samples"}))
    add("config_extra_field", "strict_keys_mismatch:config",
        lambda: validate_config({**base, "extra": 1}))
    add("config_8000_hz", "unsupported_sample_rate",
        lambda: validate_config({**base, "sample_rate_hz": 8000}))
    add("config_44100_hz", "unsupported_sample_rate",
        lambda: validate_config({**base, "sample_rate_hz": 44100}))
    add("config_stereo", "unsupported_channels",
        lambda: validate_config({**base, "channels": 2}))
    add("config_256_block", "unsupported_block_samples",
        lambda: validate_config({**base, "block_samples": 256}))
    add("config_64_hop", "unsupported_hop_samples",
        lambda: validate_config({**base, "hop_samples": 64}))
    add("config_int16", "unsupported_sample_format",
        lambda: validate_config({**base, "sample_format": "int16"}))
    add("config_clock_drift", "unsupported_clock_drift",
        lambda: validate_config({**base, "clock_ppm": 1}))
    add("config_linear_resampling", "unsupported_resampling",
        lambda: validate_config({**base, "resampling": "linear"}))
    add("config_render_delay_zero", "unsupported_render_delay",
        lambda: validate_config({**base, "render_delay_samples": 0}))
    add("config_algorithmic_latency_nonzero",
        "unsupported_algorithmic_latency",
        lambda: validate_config({**base, "algorithmic_latency_samples": 128}))
    add("config_bool_rate", "invalid_integer:sample_rate_hz",
        lambda: validate_config({**base, "sample_rate_hz": True}))

    surrogate = StreamingSurrogate(epoch=1)
    signals = build_fixture()
    hop = list(signals["mic"][:HOP_SAMPLES])
    reference = list(signals["render"][:HOP_SAMPLES])
    surrogate.process_hop(hop, reference)
    before = surrogate.state_digest

    def add_hop(case_id: str, code: str, action) -> None:
        actual = _expect_reject(code, action)
        cases.append({
            "case_id": case_id,
            "code": actual,
            "status": "rejected" if actual != "accepted" else "accepted",
            "state_unchanged": surrogate.state_digest == before,
        })

    add_hop("hop_missing_mic", "missing_input",
            lambda: surrogate.process_hop(None, reference))
    add_hop("hop_missing_render", "missing_render",
            lambda: surrogate.process_hop(hop, None))
    add_hop("hop_epoch_mismatch", "epoch_mismatch",
            lambda: surrogate.process_hop(hop, reference, epoch=2))
    add_hop("hop_mic_count_mismatch", "frame_count_mismatch:mic",
            lambda: surrogate.process_hop(hop[:127], reference))
    add_hop("hop_render_count_mismatch", "frame_count_mismatch:render",
            lambda: surrogate.process_hop(hop, reference[:127]))
    add_hop("hop_valid_count_zero", "invalid_integer:valid_count",
            lambda: surrogate.process_hop(hop, reference, valid_count=0))
    add_hop("hop_valid_count_high", "invalid_integer:valid_count",
            lambda: surrogate.process_hop(hop, reference, valid_count=129))
    add_hop("hop_nonfinite_mic", "nonfinite_input:mic",
            lambda: surrogate.process_hop(
                [float("nan")] + hop[1:], reference))
    add_hop("hop_nonfinite_render", "nonfinite_input:render",
            lambda: surrogate.process_hop(
                hop, [float("inf")] + reference[1:]))
    add_hop("hop_nonzero_mic_padding", "padding_not_zero:mic",
            lambda: surrogate.process_hop(
                hop[:100] + [1.0] + hop[101:], reference, valid_count=100))
    add_hop("hop_nonzero_render_padding", "padding_not_zero:render",
            lambda: surrogate.process_hop(
                hop, reference[:100] + [1.0] + reference[101:],
                valid_count=100))
    add_hop("hop_string_sample", "invalid_sample:mic",
            lambda: surrogate.process_hop(["x"] + hop[1:], reference))
    add_hop("hop_bool_sample", "invalid_sample:mic",
            lambda: surrogate.process_hop([True] + hop[1:], reference))
    add_hop("hop_input_position_mismatch", "input_position_mismatch",
            lambda: surrogate.process_hop(hop, reference,
                                          first_input_sample=1))

    reset_before = surrogate.state_digest

    def add_reset(case_id: str, code: str, action) -> None:
        actual = _expect_reject(code, action)
        cases.append({
            "case_id": case_id,
            "code": actual,
            "status": "rejected" if actual != "accepted" else "accepted",
            "state_unchanged": surrogate.state_digest == reset_before,
        })

    add_reset("reset_epoch_zero", "invalid_epoch",
              lambda: surrogate.reset(0, 0))
    add_reset("reset_epoch_negative", "invalid_epoch",
              lambda: surrogate.reset(-1, 0))
    add_reset("reset_epoch_not_greater", "invalid_epoch",
              lambda: surrogate.reset(1, 0))
    add_reset("reset_negative_position", "invalid_first_input_sample",
              lambda: surrogate.reset(2, -1))

    manifest = _base_manifest()
    add("caller_manifest_missing_field",
        "strict_keys_mismatch:caller_manifest",
        lambda: validate_caller_manifest(
            {key: value for key, value in manifest.items()
             if key != "stage2_sha256"}))
    add("caller_manifest_unsupported_variant", "unsupported_variant",
        lambda: validate_caller_manifest(
            {**manifest, "variant": "dtln_aec_64"}))
    add("caller_manifest_relative_stage1",
        "invalid_source_path:stage1_path",
        lambda: validate_caller_manifest(
            {**manifest, "stage1_path": "relative/dtln_aec_128_1.tflite"}))
    add("caller_manifest_duplicate_stage_path", "duplicate_stage_path",
        lambda: validate_caller_manifest(
            {**manifest, "stage2_path": manifest["stage1_path"]}))
    add("caller_manifest_stage1_name_mismatch", "stage1_name_mismatch",
        lambda: validate_caller_manifest(
            {**manifest, "stage1_path":
             "/caller-assets/dtln-aec/dtln_aec_256_1.tflite"}))
    add("caller_manifest_stage2_name_mismatch", "stage2_name_mismatch",
        lambda: validate_caller_manifest(
            {**manifest, "stage2_path":
             "/caller-assets/dtln-aec/dtln_aec_256_2.tflite"}))
    add("caller_manifest_bad_commit", "invalid_string:source_commit",
        lambda: validate_caller_manifest(
            {**manifest, "source_commit": "not-a-commit"}))
    add("caller_manifest_bad_stage1_hash", "invalid_sha256:stage1_sha256",
        lambda: validate_caller_manifest(
            {**manifest, "stage1_sha256": "0" * 63 + "z"}))
    add("caller_manifest_zero_stage2_bytes", "invalid_integer:stage2_bytes",
        lambda: validate_caller_manifest({**manifest, "stage2_bytes": 0}))
    add("caller_manifest_wrong_rate", "unsupported_sample_rate",
        lambda: validate_caller_manifest(
            {**manifest, "sample_rate_hz": 8000}))
    add("caller_manifest_wrong_channels", "unsupported_channels",
        lambda: validate_caller_manifest({**manifest, "channels": 2}))
    add("caller_manifest_wrong_block", "unsupported_block_samples",
        lambda: validate_caller_manifest(
            {**manifest, "block_samples": 256}))
    add("caller_manifest_wrong_hop", "unsupported_hop_samples",
        lambda: validate_caller_manifest({**manifest, "hop_samples": 64}))
    add("caller_manifest_negative_delay",
        "invalid_integer:declared_content_delay_samples",
        lambda: validate_caller_manifest(
            {**manifest, "declared_content_delay_samples": -1}))
    add("caller_manifest_unknown_runtime", "unsupported_runtime",
        lambda: validate_caller_manifest(
            {**manifest, "runtime": "onnxruntime"}))
    add("caller_manifest_empty_runtime_version",
        "invalid_string:runtime_version",
        lambda: validate_caller_manifest(
            {**manifest, "runtime_version": ""}))
    add("caller_manifest_extra_field",
        "strict_keys_mismatch:caller_manifest",
        lambda: validate_caller_manifest({**manifest, "extra": 1}))

    def bad_fixture(**changes):
        spec = fixture_spec()
        spec.update(changes)
        validate_fixture(spec)

    add("fixture_length_mismatch", "fixture_length_mismatch",
        lambda: bad_fixture(length_samples=8191))
    add("fixture_switch_out_of_range", "fixture_switch_mismatch",
        lambda: bad_fixture(path_switch_sample=1))
    add("fixture_segment_count", "fixture_segment_count",
        lambda: bad_fixture(segments=fixture_spec()["segments"][:-1]))
    add("fixture_tap_order", "tap_order_mismatch",
        lambda: bad_fixture(echo_taps_before=[[4, 1], [0, 1]]))
    add("fixture_delay_mismatch", "fixture_delay_mismatch",
        lambda: bad_fixture(render_delay_samples=0))
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


# ---------------------------------------------------------------------------
# Task-local git scope
# ---------------------------------------------------------------------------
# The merged squash lands on `main`; later merges add unrelated sibling task
# packages. A fixed historical commit therefore cannot be the scope base: it
# would report those siblings as out-of-scope edits of this task. The base is
# the newest merge-base between HEAD and the PR base refs, so the comparison
# contains exactly the commits this branch added and fail-closed scope checks
# still catch any edit outside TASK_PREFIX.
SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> str | None:
    """Return the commit SHA a ref resolves to, or None when it is absent."""
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base between HEAD and an available PR base ref.

    Returns None only when no base ref exists, which the verifier treats as a
    fail-closed condition rather than a silent pass.
    """
    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> list[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> list[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]


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
            "render_reference_freeze": {
                "status": "synthetic_only",
                "evidence": ("Frozen 16 kHz mono 512/128 synthetic render and "
                             "capture with fixed integer-tap echo paths, "
                             "declared 16-sample delay, noise levels, one path "
                             "switch and a reset schedule."),
            },
            "echo_only": {
                "status": "synthetic_only",
                "evidence": ("Two synthetic far-end-only regions, before and "
                             "after a path change; no real room or recording."),
            },
            "near_end_only": {
                "status": "synthetic_only",
                "evidence": ("Two synthetic near-end-only regions with known "
                             "clean near component and injected noise."),
            },
            "overlap_double_talk": {
                "status": "synthetic_only",
                "evidence": ("One synthetic render plus near-end overlap "
                             "region; no varying SER, real device or listener."),
            },
            "no_reference_comparison": {
                "status": "synthetic_only",
                "evidence": ("Independent gate-only control without AEC is "
                             "measured separately on the same synthetic mic."),
            },
            "echo_attenuation": {
                "status": "synthetic_only",
                "evidence": ("ERLE in integer millidB on synthetic echo-only "
                             "regions only; no real-room claim."),
            },
            "near_end_damage": {
                "status": "synthetic_only",
                "evidence": ("Near-reference SNR, level change and peak on "
                             "synthetic near-end regions; no MOS or listening."),
            },
            "nonfinite_failures": {
                "status": "synthetic_only",
                "evidence": ("Nonfinite input and output checks plus peak "
                             "bound on synthetic hops; no runtime failure."),
            },
            "alignment_delayed_missing_render": {
                "status": "synthetic_only",
                "evidence": ("Declared 16-sample render delay, a 256-sample "
                             "shifted-render failure probe and an all-zero "
                             "missing-render probe; a missing render hop is "
                             "rejected before processing."),
            },
            "movement_path_change": {
                "status": "synthetic_only",
                "evidence": ("One fixed synthetic coefficient switch at "
                             "sample 6144; no real movement or device mic."),
            },
            "task_matched_heldout_qualification": {
                "status": "blocked",
                "evidence": ("No rights-cleared paired AEC cohort, held-out "
                             "split, AECMOS/STOI/ASR or listening result."),
            },
        },
    }


def _profile_blockers(profile: Dict[str, Any]) -> List[str]:
    return sorted(name for name, item in profile["required_items"].items()
                  if item["status"] == "blocked")


def _release_gates() -> List[Dict[str, str]]:
    rows = [
        ("RG-01", "Exact pinned DTLN-AEC source, the 128/256/512 two-stage "
                  "checkpoints and a TFLite runtime with an immutable "
                  "revision, license identity, parameter/geometry record and "
                  "declared adapter settings."),
        ("RG-02", "Isolated hash-pinned TFLite runtime admission, reproducible "
                  "build, verified stage-1/stage-2 weight identity and "
                  "recurrent-state shapes, and fail-closed absent behavior."),
        ("RG-03", "Code, weight, training-data and corpus rights plus "
                  "attribution, notices, redistribution, product-use and "
                  "derivative-output review."),
        ("RG-04", "Paired render/capture 512/128 geometry, declared content "
                  "delay and clock mapping into the SDK duplex contract with "
                  "byte-level output parity."),
        ("RG-05", "Echo-only, near-end-only, overlap and no-reference "
                  "qualification on a rights-cleared task-matched held-out "
                  "paired cohort including ERLE, preservation and alignment."),
        ("RG-06", "Streaming recurrent state, reset, latency, availability, "
                  "path change, delayed/missing render and nonfinite behavior "
                  "at the exact runtime."),
        ("RG-07", "Target-device pacing, timing and memory with independent "
                  "listening and/or ASR controls."),
        ("RG-08", "Opt-in provider intake, descriptor review, independent "
                  "exact-head review and default/release approval."),
    ]
    return [{"id": gate, "requirement": text, "status": "blocked"}
            for gate, text in rows]


def _exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "pinned_dtln_aec_source_weights_runtime_absent",
            "requirement": ("Supply the exact licensed DTLN-AEC source export, "
                            "the selected 128/256/512 two-stage TFLite "
                            "checkpoints and a pinned tflite-runtime or "
                            "TensorFlow environment with immutable revision, "
                            "file SHA-256, byte sizes and state shapes."),
            "state": ("No DTLN-AEC checkout, checkpoint or runtime is staged at "
                      "data/checkouts/DTLN-aec, data/models/dtln-aec or "
                      "data/envs/dtln-aec. data/checkouts/DTLN contains only "
                      "generic DTLN speech-enhancement TFLite weights, which "
                      "the pinned research note explicitly rejects as a "
                      "substitute. tflite_runtime and TensorFlow are not "
                      "importable in the pinned CPython 3.12.16 evidence "
                      "interpreter. The local adapter wrapper is present but "
                      "has mock-interpreter coverage only."),
        },
        {
            "id": "candidate_model_delay_state_and_parity_unverified",
            "requirement": ("Document and verify the exact DTLN-AEC 16 kHz "
                            "mono 512-sample block, 128-sample hop, model "
                            "content delay, four recurrent-state shapes, "
                            "input/output tensor order and numeric output for "
                            "each selected variant."),
            "state": ("The pinned adapter README documents 16 kHz mono, a "
                      "512-sample analysis block and 128-sample hops, but not "
                      "the model content delay, recurrent-state shapes or "
                      "numeric output. The wrapper adds a 384-sample "
                      "block-minus-hop framing delay of its own; the model "
                      "delay remains unmeasured and no parity vector exists."),
        },
        {
            "id": "rights_attribution_and_weights_review_absent",
            "requirement": ("Stage the DTLN-AEC code and weight license, "
                            "attribution notice, model card, training-data "
                            "terms and complete distribution, derivative and "
                            "product-use review."),
            "state": ("No DTLN-AEC LICENSE, model card, weight terms, "
                      "training-data statement, notice bundle or legal review "
                      "is staged. The generic DTLN MIT license is not a "
                      "DTLN-AEC license and is not accepted as one."),
        },
        {
            "id": "paired_render_contract_and_sdk_integration_absent",
            "requirement": ("Admit an accepted paired render/capture boundary "
                            "and map DTLN-AEC delay/clock behavior into the "
                            "installed SDK path with exact parity."),
            "state": ("Installed v0 accepts one 16 kHz mono float32 160-sample "
                      "stream. The merged duplex evidence is a model-free "
                      "proposal with no AEC provider geometry, and nothing "
                      "maps a far-end render input into this candidate."),
        },
        {
            "id": "rights_cleared_paired_cohort_absent",
            "requirement": ("Supply a rights-cleared task-matched held-out "
                            "paired render/capture cohort with echo-only, "
                            "near-end-only, overlap, movement and no-reference "
                            "strata plus AECMOS/STOI/ASR or listening labels."),
            "state": ("No real paired recording, room response, consent, "
                      "corpus terms, held-out split or task-matched score is "
                      "staged. Synthetic integer fixtures cannot qualify the "
                      "candidate."),
        },
        {
            "id": "timing_and_independent_review_absent",
            "requirement": ("Measure target-device pacing, latency, memory and "
                            "reset/path-change behavior at the exact runtime "
                            "and complete independent review."),
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
        "generic_dtln_mit_not_accepted": True,
        "note": ("No DTLN-AEC license identity, license text, weight terms or "
                 "training-data statement is staged. The pinned generic DTLN "
                 "MIT license covers a different model and is not accepted as "
                 "DTLN-AEC permission."),
    }


def _candidate() -> Dict[str, Any]:
    return {
        "name": "DTLN-AEC 128/256/512",
        "reported_source_url": CANDIDATE_SOURCE_URL,
        "reported_paper_doi": CANDIDATE_PAPER_DOI,
        "reported_unit_variants": list(CANDIDATE_REPORTED_UNIT_VARIANTS),
        "reported_parameter_count": None,
        "reported_input_sample_rate_hz": CANDIDATE_REPORTED_RATE_HZ,
        "reported_block_samples": CANDIDATE_REPORTED_BLOCK,
        "reported_hop_samples": CANDIDATE_REPORTED_HOP,
        "reported_content_delay_samples": None,
        "io_geometry_documented": True,
        "model_delay_documented": False,
        "state_shapes_documented": False,
        "source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "exact_numeric_output_present": False,
    }


def _external_artifacts() -> Dict[str, Any]:
    paths = {
        "source_checkout": "data/checkouts/DTLN-aec",
        "weights": "data/models/dtln-aec",
        "runtime_env": "data/envs/dtln-aec",
        "generic_dtln_checkout": "data/checkouts/DTLN",
        "adapter_wrapper": "adapters/dtln-aec",
        "caller_manifest": "data/manifests/dtln-aec.json",
    }
    present = {key: (SOURCE_ROOT / path).exists()
               for key, path in paths.items()}
    return {
        "checked_paths": paths,
        "present": present,
        "any_present": any(present[key] for key in
                           ("source_checkout", "weights", "runtime_env",
                            "caller_manifest")),
        "generic_dtln_is_candidate": False,
        "status": "blocked",
        "note": ("The generic DTLN checkout and the local adapter wrapper are "
                 "present but are not the DTLN-AEC checkpoints, runtime or "
                 "rights evidence. Observed presence would not be runtime "
                 "admission, parity or rights evidence."),
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
    "No DTLN-AEC source, TFLite graph, recurrent state, weight file, runtime, "
    "revision or numeric output was produced, loaded or executed.",
    "No echo, noise-suppression, quality, latency, benchmark, listening or "
    "release result is claimed.",
    "The synthetic NLMS plus residual-gate surrogate is not DTLN-AEC and "
    "cannot qualify the candidate.",
    "The DTLN-AEC model content delay, recurrent-state shapes, tensor order "
    "and numeric output are not asserted.",
    "Synthetic ERLE, near-reference SNR and level change are unqualified "
    "task-local observations only.",
    "The generic DTLN speech-enhancement TFLite weights are not DTLN-AEC "
    "weights and are not used as a substitute.",
    "No real room, paired recording, corpus, AECMOS/STOI/ASR score, device "
    "clock or listener was used.",
    "No upstream license text, attribution bundle, weight terms or training "
    "data statement is staged.",
    "No provider, descriptor, registry, installed v0 path, shared build, "
    "dependency lock or CI was changed.",
)

REOPEN_CONDITION = (
    "Pin the exact licensed DTLN-AEC source and the selected 128/256/512 "
    "two-stage TFLite checkpoints with immutable revision, file hashes, byte "
    "sizes and state shapes; admit an isolated hash-pinned tflite-runtime or "
    "TensorFlow environment; clear code/weight/training-data/corpus rights; "
    "map paired render/capture delay and clocks into the accepted duplex "
    "contract; reproduce exact output; qualify echo-only, near-end-only, "
    "overlap and no-reference behavior on a rights-cleared task-matched "
    "held-out cohort; measure target timing and complete opt-in provider "
    "intake. Until then the candidate stays DEFER, incomplete and not "
    "qualified."
)


def _case_matrix_digest(run: Dict[str, Any], alignment: Dict[str, Any],
                        no_reference: Dict[str, Any],
                        streaming: Dict[str, Any],
                        reset: Dict[str, Any]) -> str:
    return object_digest({
        "signals": run["signal_digests"],
        "erle": [(row["segment"], row["erle_millidb"])
                 for row in run["erle_regions"]],
        "near": [(row["segment"], row["near_reference_snr_millidb"],
                  row["level_change_millidb"]) for row in run["near_regions"]],
        "overlap": (run["overlap"]["near_reference_snr_millidb"],
                    run["overlap"]["level_change_millidb"]),
        "alignment": (alignment["aligned_erle_millidb"],
                      alignment["delayed_render_erle_millidb"],
                      alignment["missing_render_erle_millidb"]),
        "no_reference": (no_reference["control_echo_erle_millidb"],
                         no_reference["aec_echo_erle_millidb"]),
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
            "block_samples": BLOCK_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "magnitude_bins": MAGNITUDE_BINS,
            "sample_format": SAMPLE_FORMAT,
            "length_samples": FIXTURE_LENGTH,
            "duration_ns": FIXTURE_LENGTH * SAMPLE_NS,
            "render_delay_samples": RENDER_DELAY_SAMPLES,
            "filter_tail_samples": TAIL_SAMPLES,
            "path_switch_sample": PATH_SWITCH_SAMPLE,
            "surrogate_framing_delay_samples": SURROGATE_FRAMING_DELAY,
            "segments": [dict(segment) for segment in SEGMENTS],
            "echo_taps_before": [list(tap) for tap in ECHO_TAPS_BEFORE],
            "echo_taps_after": [list(tap) for tap in ECHO_TAPS_AFTER],
        },
        "signal_digests": run["signal_digests"],
    }


def _caller_asset_spec() -> Dict[str, Any]:
    return {
        "contract_id":
            "audio-sdk/dtln-aec-128-256-512/caller-supplied-asset/0.1",
        "asset_is_caller_owned": True,
        "asset_is_vendored": False,
        "variants": list(VARIANT_IDS),
        "variant_unit_counts": list(UNIT_VARIANTS),
        "stage_files_per_variant": 2,
        "file_name_pattern": "<variant>_1.tflite and <variant>_2.tflite",
        "required_geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "block_samples": BLOCK_SAMPLES,
            "hop_samples": HOP_SAMPLES,
            "input_format": SAMPLE_FORMAT,
        },
        "manifest_present": False,
        "workspace_manifest": "data/manifests/dtln-aec.json",
        "present_behavior":
            "validate_identity_geometry_size_hash_runtime_only;"
            "_do_not_load_or_execute",
        "absent_behavior": "reject_before_processing",
        "required_fields": sorted(CALLER_MANIFEST_FIELDS),
        "runtime_ids": sorted(RUNTIME_IDS),
        "probe_manifest": _base_manifest(),
        "probe_gate": gate_caller_assets(_base_manifest()),
        "loaded": False,
        "executed": False,
        "imported": False,
        "status": "blocked",
    }


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()
    fixture = fixture_run()
    alignment = alignment_run()
    control = no_reference_comparison(fixture)
    streaming = streaming_check(fixture)
    reset = reset_check()
    partial = final_partial_check()
    profile = _acceptance_profile()
    adverse = adverse_rejections()
    gates = _release_gates()
    blockers = _exact_blockers()
    licensing = _licensing()
    candidate = _candidate()
    matrix = _case_matrix_digest(fixture, alignment, control, streaming,
                                 reset)

    erle_values = [row["erle_millidb"] for row in fixture["erle_regions"]]
    near_values = [row["near_reference_snr_millidb"]
                   for row in fixture["near_regions"]]
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
            "adapter_wrapper_present": True,
            "adapter_wrapper_mock_tested_only": True,
            "exact_numeric_output_present": False,
            "license_identity": None,
            "pinned_revision": None,
            "status": "blocked",
            "surrogate_is_candidate": False,
        },
        "format": {
            "sdk_v0_sample_rate_hz": SDK_RATE_HZ,
            "sdk_v0_channels": SDK_CHANNELS,
            "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
            "sdk_v0_sample_format": SDK_SAMPLE_FORMAT,
            "candidate_reported_sample_rate_hz": CANDIDATE_REPORTED_RATE_HZ,
            "candidate_reported_block_samples": CANDIDATE_REPORTED_BLOCK,
            "candidate_reported_hop_samples": CANDIDATE_REPORTED_HOP,
            "candidate_model_delay_documented": False,
            "resampling": "none",
            "paired_render_in_installed_v0": False,
            "duplex_reference_contract": (
                "audio-sdk/duplex-reference-clocks/0.1 proposal only"),
            "surrogate_render_delay_samples": RENDER_DELAY_SAMPLES,
            "surrogate_framing_delay_samples": SURROGATE_FRAMING_DELAY,
            "surrogate_algorithmic_latency_samples": 0,
        },
        "fixtures": _fixtures(fixture),
        "echo_attenuation": {
            "regions": fixture["erle_regions"],
            "min_erle_millidb": min(erle_values),
            "max_erle_millidb": max(erle_values),
            "overall_erle_millidb": fixture["overall"]["erle_millidb"],
            "qualifies": False,
        },
        "near_end_preservation": {
            "regions": fixture["near_regions"],
            "min_near_reference_snr_millidb": min(near_values),
            "max_level_change_millidb": max(
                abs(row["level_change_millidb"])
                for row in fixture["near_regions"]),
            "nonfinite_output_count": fixture["overall"][
                "nonfinite_output_count"],
            "qualifies": False,
        },
        "overlap_double_talk": fixture["overlap"],
        "no_reference_comparison": control,
        "alignment": alignment,
        "nonfinite": {
            "rejected_nonfinite_inputs": sum(
                1 for case in adverse
                if "nonfinite_input" in case["code"]),
            "output_nonfinite_count": fixture["overall"][
                "nonfinite_output_count"],
            "output_finite": fixture["overall"]["nonfinite_output_count"] == 0,
            "max_peak_milli": max(
                row["peak_milli"] for row in fixture["near_regions"]),
            "qualifies": False,
        },
        "movement_path_change": {
            "switch_sample": PATH_SWITCH_SAMPLE,
            "before_erle_millidb": fixture["erle_regions"][0][
                "erle_millidb"],
            "after_erle_millidb": fixture["erle_regions"][1]["erle_millidb"],
            "real_movement": False,
            "qualifies": False,
        },
        "final_partial": partial,
        "streaming": streaming,
        "reset": reset,
        "adverse_rejections": adverse,
        "adverse_all_rejected": all(
            row["status"] == "rejected" and row["state_unchanged"] is True
            for row in adverse),
        "external_artifacts": _external_artifacts(),
        "runtime_probe": runtime_probe(),
        "licensing": licensing,
        "caller_asset": _caller_asset_spec(),
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
            "rights_cleared_cohort": False,
            "io_geometry_documented": True,
            "model_delay_documented": False,
            "state_shapes_documented": False,
            "paired_render_contract_qualified": False,
            "echo_only_qualified": False,
            "near_end_qualified": False,
            "overlap_qualified": False,
            "no_reference_qualified": False,
            "timing_measured": False,
            "listening": False,
            "real_corpus_used": False,
            "reason": ("Exact DTLN-AEC source/checkpoints/runtime, model "
                       "delay and state shapes, rights, paired-render "
                       "admission, rights-cleared held-out data, timing and "
                       "independent review are all absent."),
        },
        "exact_blockers": blockers,
        "release_gates": gates,
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "surrogate": {
            "algorithm": ("bounded 64-tap NLMS echo canceller plus "
                          "deterministic residual-energy gate at a 512/128 "
                          "overlap-add frame clock"),
            "is_dtln_aec": False,
            "is_learned": False,
            "uses_tflite": False,
            "uses_recurrent_state": False,
            "uses_weights": False,
            "uses_mask_network": False,
            "qualifies_candidate": False,
        },
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "case_matrix_digests": [matrix, matrix, matrix],
        },
        "scope_note": ("Only docs/task-evidence/dtln-aec-128-256-512/ is "
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
        "caller_asset_contract": report["caller_asset"],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no DTLN-AEC source, TFLite graph, checkpoint, recurrent state, "
            "runtime or adapter is downloaded, copied, loaded or executed",
            "the synthetic NLMS plus residual-gate surrogate is not DTLN-AEC "
            "and cannot qualify the candidate",
            "the DTLN-AEC model content delay, state shapes, tensor order and "
            "numeric output are not asserted",
            "generic DTLN speech-enhancement TFLite weights are not accepted "
            "as DTLN-AEC weights",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def sources_bytes(overrides: Dict[str, bytes] | None = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-DTLN-AEC-128-256-512; source: paths are "
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
    "StreamingSurrogate", "NoiseGateOnly", "ReferenceRejection", "SEGMENTS",
    "adverse_rejections", "alignment_run", "board_row", "build_contract",
    "build_fixture", "build_report", "canonical_report", "canonical_text",
    "chunk_plan", "final_partial_check", "fixture_run", "fixture_spec",
    "gate_caller_assets", "int_signal_digest", "load_strict_json",
    "load_strict_json_text", "no_reference_comparison", "object_digest",
    "reset_check", "run_stream", "runtime_probe", "scope_base",
    "scope_changed_paths", "scope_violations", "sha256_bytes",
    "signal_digest", "sources_bytes", "streaming_check",
    "validate_caller_manifest", "validate_config", "validate_fixture",
]
