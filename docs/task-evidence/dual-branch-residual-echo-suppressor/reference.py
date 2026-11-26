# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local dual-branch residual echo suppressor boundary evidence.

This is an original, stdlib-only synthetic probe written for this task. It is
NOT the catalogued dual-branch residual echo suppressor candidate source, a
candidate build, a licensed candidate runtime, a candidate weight file or a
candidate result. No upstream code, dual-branch layer, recurrent or attention
block, weight, corpus or asset is present, copied, downloaded, loaded or
executed.

The probe consumes caller-owned paired 16 kHz mono float32 160-sample capture
and render frames, runs a bounded integer-tap NLMS paired-reference canceller
front end plus a deterministic residual gate, and measures echo attenuation,
near-end preservation, double-talk behavior, delayed/missing render failure and
nonfinite rejection on frozen synthetic signals. The canceller front end is an
explicit, fixed surrogate for the paired-reference attachment named by the task
plan note; it is not a candidate component. The probe exists only to exercise
strict parsing, exact fixture arithmetic, online state, reset, block invariance
and adverse rejection at a task-local proposal boundary. It is proposal-only,
incomplete and not qualified.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

VERSION = "0.1.0"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
REPORT_SCHEMA = "audio-sdk/dual-branch-residual-echo-suppressor-report/0.1"
TASK_ID = "SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR"
TITLE = "Dual-branch residual echo suppressor"
COMPONENT = "dual-branch-residual-echo-suppressor"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "7c6653f5a7db7f6de34ad709a96a455a9ad3263a"
BRANCH = "swarm/SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR"
REVIEWER = "reviewer-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR"
PROFILE = "room"
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

FIXTURE_LENGTH = 16000
TAIL_SAMPLES = 64
RENDER_DELAY_SAMPLES = 32
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

CANDIDATE_REPORTED_PARAMETERS: int | None = None
CANDIDATE_REPORTED_RATE_HZ: int | None = None

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
    (0, 620), (3, 310), (7, -180), (11, 140), (15, 80), (19, -50), (23, 30),
)
ECHO_TAPS_AFTER: Tuple[Tuple[int, int], ...] = (
    (0, 430), (3, -260), (7, 210), (11, -130), (15, 90), (19, 40), (23, -25),
)
PATH_SWITCH_SAMPLE = 9600

SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"name": "echo_only_initial", "start": 0, "end": 3200,
     "render": True, "near": False, "noise_amplitude": 20},
    {"name": "near_only_clean", "start": 3200, "end": 6400,
     "render": False, "near": True, "noise_amplitude": 20},
    {"name": "overlap_double_talk", "start": 6400, "end": 9600,
     "render": True, "near": True, "noise_amplitude": 80},
    {"name": "echo_only_after_path_change", "start": 9600, "end": 12800,
     "render": True, "near": False, "noise_amplitude": 20},
    {"name": "near_only_noisy", "start": 12800, "end": 16000,
     "render": False, "near": True, "noise_amplitude": 120},
)
SEGMENT_KEYS = {"name", "start", "end", "render", "near", "noise_amplitude"}
ERLE_REGIONS = (
    ("echo_only_initial", 1600, 3200),
    ("echo_only_after_path_change", 11200, 12800),
)
NEAR_REGIONS = (
    ("near_only_clean", 3200, 6400),
    ("near_only_noisy", 12800, 16000),
)
OVERLAP_REGION = ("overlap_double_talk", 6400, 9600)
ALIGNMENT_PROBE_END = 3200
ALIGNMENT_REGION = (1600, 3200)
DELAYED_RENDER_SAMPLES = 64
FINAL_PARTIAL_VALID = 137

SOURCE_PINS = {
    "REALTIME_COMPONENT_CANDIDATES.md": (
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d"
    ),
    "research/aec_research_20261028.md": (
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180"
    ),
    "research/voice-enhancement-20261101/candidate_matrix.csv": (
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245"
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
    "audio-benchmark-platform/plan/audio-sdk/README.md": (
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06"
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
    "docs/task-evidence/SDK-SPEEX-MDF-RESIDUAL-POSTFILTER.md": (
        "b9efbe044c002485d4b5dbcc87ef8bf040daead08f9284f3ce19f61e6a32cc45"
    ),
    "docs/task-evidence/speex-mdf-residual-postfilter/README.md": (
        "16c7643cc5550cd7358ee48f7dec62eb4045a3384364246cd357269ce0c28da9"
    ),
    "docs/task-evidence/speex-mdf-residual-postfilter/report.json": (
        "ad15c446442058b82c003f15527637edae02a819a2033b0f289bc89042b170b6"
    ),
    "docs/task-evidence/erle-and-double-talk-preservation/report.json": (
        "6860139e8c1a9f5c01fa219f81b6b8f5ee3f43160dd139d00e45cfb853d63b50"
    ),
    "docs/task-evidence/localvqe-compact-echo-only/README.md": (
        "ed8c3a54297c929154283184eb9fad79b09f57ab4e77a31fb30f993c688e579a"
    ),
    "docs/task-evidence/localvqe-compact-echo-only/report.json": (
        "28b17d5ee0afa2f017009456ef58d0fbac6383bf64744682e7400079df862369"
    ),
    "docs/task-evidence/cagcrn-joint-aec-and-ns/README.md": (
        "aeae96f49acad572294b69cafb1b581392c3c3c11171d60545eadd6ede3187c7"
    ),
    "docs/task-evidence/cagcrn-joint-aec-and-ns/report.json": (
        "697eb9feb470d529ba8132a8d597cb52308f46f5d2c6afd36803de268f9d7828"
    ),
    "docs/task-evidence/survey-cln-06/README.md": (
        "4f9e0c0d901b8a45f3513c918b6f532fa16bed366ce0dee8a642e1bd46b0b96a"
    ),
    "docs/task-evidence/survey-cln-06/report.json": (
        "b9db38650de9225a8cff7488f1e84b1a8c6062541300e758baa1f6ae58cfa1dc"
    ),
    "docs/task-evidence/aec-challenge-paired-render-capture-fixtures/README.md": (
        "de5b37cb55275da0f130c2eb524c15f4f12fed18171725596156789ef8b41ccf"
    ),
    "docs/task-evidence/aec-challenge-paired-render-capture-fixtures/report.json": (
        "da409a1500043ec303e35360de2124aff90c1bee9552939916f387103f69f512"
    ),
    "docs/task-evidence/webrtc-aec3/report.json": (
        "da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283"
    ),
    "docs/task-evidence/nlms-aec/README.md": (
        "83084ed97c02e21764f9a41daa2184e23afc13d86466dd40e0dfb0fc670bb9e0"
    ),
}

BOARD_ROW_STABLE_SHA256 = (
    "29f45acfebaef9781d4083d1e1236913a4f4f3e54f7b9c3ed11ee622300ffd9d"
)

TASK_PREFIX = "docs/task-evidence/dual-branch-residual-echo-suppressor/"
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
    length = _integer(spec["length_samples"], "length_samples", 160, 200000)
    _require(length == FIXTURE_LENGTH, "fixture_length_mismatch")
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
                      for value in _lcg_values(20261028, FIXTURE_LENGTH)],
                     render_mask)
    near = _masked(_voice_values(FIXTURE_LENGTH), near_mask)
    noise_base = _lcg_values(20261029, FIXTURE_LENGTH)
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
# Task-local paired-reference residual chain
# ---------------------------------------------------------------------------

CONFIG_KEYS = {"sample_rate_hz", "channels", "frame_samples", "sample_format",
               "clock_ppm", "resampling", "render_delay_samples",
               "algorithmic_latency_samples"}


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the task-local probe configuration; fail closed."""
    _exact_keys(config, CONFIG_KEYS, "config")
    rate = _integer(config["sample_rate_hz"], "sample_rate_hz", 1, 384000)
    channels = _integer(config["channels"], "channels", 1, 8)
    frame = _integer(config["frame_samples"], "frame_samples", 1, 4096)
    clock = _integer(config["clock_ppm"], "clock_ppm", -1000000, 1000000)
    delay = _integer(config["render_delay_samples"], "render_delay_samples",
                     0, 480)
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
    if delay != RENDER_DELAY_SAMPLES:
        raise ReferenceRejection("unsupported_render_delay")
    if latency != 0:
        raise ReferenceRejection("unsupported_algorithmic_latency")
    return {"sample_rate_hz": rate, "channels": channels,
            "frame_samples": frame, "sample_format": config["sample_format"],
            "clock_ppm": clock, "resampling": config["resampling"],
            "render_delay_samples": delay,
            "algorithmic_latency_samples": latency}


def _validate_paired_frame(mic: object, render: object,
                           valid_count: object) -> int:
    count = _integer(valid_count, "valid_count", 1, FRAME_SAMPLES)
    for label, values in (("mic", mic), ("render", render)):
        if values is None:
            raise ReferenceRejection("missing_input" if label == "mic"
                                     else "missing_render")
        if not isinstance(values, (list, tuple)):
            raise ReferenceRejection("invalid_frame:" + label)
        if len(values) != FRAME_SAMPLES:
            raise ReferenceRejection("frame_count_mismatch:" + label)
        for index in range(count):
            value = values[index]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ReferenceRejection("invalid_sample:" + label)
            if not math.isfinite(float(value)):
                raise ReferenceRejection("nonfinite_input:" + label)
        for index in range(count, FRAME_SAMPLES):
            value = values[index]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ReferenceRejection("invalid_sample:" + label)
            if float(value) != 0.0:
                raise ReferenceRejection("padding_not_zero:" + label)
    return count


class PairedReferenceResidualChain:
    """Bounded NLMS echo canceller plus deterministic residual noise gate."""

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
        self.weights = [0.0] * TAIL_SAMPLES
        self.history = [0.0] * TAIL_SAMPLES
        self.history_position = 0
        self.noise_floor = 0.0
        self.last_gain_milli = 1000

    @property
    def state_digest(self) -> str:
        payload = struct.pack("<%dd" % TAIL_SAMPLES, *self.weights)
        payload += struct.pack("<%dd" % TAIL_SAMPLES, *self.history)
        payload += struct.pack("<qqdqi", self.epoch, self.position,
                               self.noise_floor, self.history_position,
                               self.last_gain_milli)
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
        self.weights = [0.0] * TAIL_SAMPLES
        self.history = [0.0] * TAIL_SAMPLES
        self.history_position = 0
        self.noise_floor = 0.0
        self.last_gain_milli = 1000

    def _frame_gain_milli(self, residual: Sequence[float]) -> int:
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

    def process_frame(self, mic: Sequence[float] | None,
                      render: Sequence[float] | None,
                      valid_count: int = FRAME_SAMPLES,
                      epoch: int | None = None,
                      first_input_sample: int | None = None
                      ) -> Tuple[List[float], List[float]]:
        """Return (output, pre-gate residual); both are 160 samples."""
        count = _validate_paired_frame(mic, render, valid_count)
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
            capture = float(mic[index]) / 32768.0
            reference = float(render[index]) / 32768.0
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

        gain_milli = self._frame_gain_milli(residual)
        output = [value * gain_milli / 1000.0 for value in residual]
        self.position += count
        self.frames += 1
        output.extend([0.0] * (FRAME_SAMPLES - count))
        residual.extend([0.0] * (FRAME_SAMPLES - count))
        return output, residual


class NoReferenceResidualGate:
    """Independent no-reference control: gate the microphone, no AEC."""

    def __init__(self, epoch: int = 1):
        if (not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 1):
            raise ReferenceRejection("invalid_epoch")
        self.epoch = epoch
        self.position = 0
        self.noise_floor = 0.0
        self.last_gain_milli = 1000

    def process_frame(self, mic: Sequence[float], valid_count: int = 160
                      ) -> List[float]:
        count = _validate_paired_frame(mic, [0] * FRAME_SAMPLES, valid_count)
        values = [float(mic[index]) / 32768.0 for index in range(count)]
        power = sum(value * value for value in values) / count
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
        output = [value * gain / 1000.0 for value in values]
        self.position += count
        output.extend([0.0] * (FRAME_SAMPLES - count))
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


def run_stream(mic: Sequence[int], render: Sequence[int],
               chunks: Sequence[int] | None = None,
               epoch: int = 1) -> Dict[str, Any]:
    _require(len(mic) == len(render), "paired_length_mismatch")
    suppressor = PairedReferenceResidualChain(epoch=epoch)
    plan = list(chunks) if chunks is not None else chunk_plan(len(mic))
    _require(sum(plan) == len(mic), "chunk_sum_mismatch")
    output: List[float] = []
    residual: List[float] = []
    offset = 0
    for chunk in plan:
        _require(chunk > 0, "invalid_chunk")
        chunk_end = offset + chunk
        while offset < chunk_end:
            size = min(FRAME_SAMPLES, chunk_end - offset)
            mic_frame = list(mic[offset:offset + size])
            render_frame = list(render[offset:offset + size])
            mic_frame.extend([0] * (FRAME_SAMPLES - size))
            render_frame.extend([0] * (FRAME_SAMPLES - size))
            out_frame, residual_frame = suppressor.process_frame(
                mic_frame, render_frame, valid_count=size)
            output.extend(out_frame[:size])
            residual.extend(residual_frame[:size])
            offset += size
    return {"output": output, "residual": residual,
            "state_digest": suppressor.state_digest,
            "samples": len(output)}


def run_no_reference(mic: Sequence[int]) -> List[float]:
    gate = NoReferenceResidualGate()
    output: List[float] = []
    for offset in range(0, len(mic), FRAME_SAMPLES):
        frame = list(mic[offset:offset + FRAME_SAMPLES])
        count = len(frame)
        frame.extend([0] * (FRAME_SAMPLES - count))
        values = gate.process_frame(frame, valid_count=count)
        output.extend(values[:count])
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
    mic_energy = _energy(signals["mic"], 0, FIXTURE_LENGTH) / INT_SCALE_SQ
    residual_energy = _energy(run["residual"], 0, FIXTURE_LENGTH)
    out_energy = _energy(run["output"], 0, FIXTURE_LENGTH)
    erle_rows = []
    for name, start, end in ERLE_REGIONS:
        chain = _region_metrics(signals["mic"], run["output"],
                                signals["near"], start, end)
        aec_only_energy = _energy(run["residual"], start, end)
        region_mic_energy = _energy(signals["mic"], start, end) / INT_SCALE_SQ
        erle_rows.append({
            "segment": name,
            "start": start,
            "end": end,
            "erle_millidb": chain["erle_millidb"],
            "aec_only_erle_millidb": _db_millidb(region_mic_energy,
                                                 aec_only_energy),
            "qualifies": False,
        })
    near_rows = []
    for name, start, end in NEAR_REGIONS:
        metrics = _region_metrics(signals["mic"], run["output"],
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
    overlap = _region_metrics(signals["mic"], run["output"],
                              signals["near"], *OVERLAP_REGION[1:])
    return {
        "signals": signals,
        "run": run,
        "overall": {
            "erle_millidb": _db_millidb(mic_energy, out_energy),
            "aec_only_erle_millidb": _db_millidb(mic_energy,
                                                 residual_energy),
            "near_reference_snr_millidb": _region_metrics(
                signals["mic"], run["output"], signals["near"], 0,
                FIXTURE_LENGTH)["near_reference_snr_millidb"],
            "nonfinite_output_count": _check_finite(run["output"]),
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
            "output": signal_digest(run["output"]),
        },
    }


def alignment_run() -> Dict[str, Any]:
    signals = build_fixture()
    mic = signals["mic"][:ALIGNMENT_PROBE_END]
    render = signals["render"][:ALIGNMENT_PROBE_END]
    aligned = run_stream(mic, render)
    delayed_render = ([0] * DELAYED_RENDER_SAMPLES
                      + list(render[:-DELAYED_RENDER_SAMPLES]))
    delayed = run_stream(mic, delayed_render)
    missing = run_stream(mic, [0] * len(mic))
    start, end = ALIGNMENT_REGION
    aligned_erle = _db_millidb(_energy(mic, start, end) / INT_SCALE_SQ,
                               _energy(aligned["output"], start, end))
    delayed_erle = _db_millidb(_energy(mic, start, end) / INT_SCALE_SQ,
                               _energy(delayed["output"], start, end))
    missing_erle = _db_millidb(_energy(mic, start, end) / INT_SCALE_SQ,
                               _energy(missing["output"], start, end))
    return {
        "declared_render_delay_samples": RENDER_DELAY_SAMPLES,
        "surrogate_content_delay_samples": 0,
        "aligned_erle_millidb": aligned_erle,
        "delayed_render_erle_millidb": delayed_erle,
        "missing_render_erle_millidb": missing_erle,
        "delayed_render_detected": delayed_erle + 6000 < aligned_erle,
        "missing_render_detected": missing_erle + 6000 < aligned_erle,
        "missing_render_frame_rejected": True,
        "missing_render_rejected_before_processing": False,
        "zero_render_probe_is_not_missing_frame": True,
        "candidate_alignment_verified": False,
        "qualifies": False,
    }


def no_reference_comparison(run: Dict[str, Any]) -> Dict[str, Any]:
    signals = run["signals"]
    output = run_no_reference(signals["mic"])
    start, end = ERLE_REGIONS[0][1], ERLE_REGIONS[0][2]
    gate_erle = _db_millidb(_energy(signals["mic"], start, end) / INT_SCALE_SQ,
                            _energy(output, start, end))
    aec_erle = run["erle_regions"][0]["aec_only_erle_millidb"]
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
    plan = chunk_plan(FIXTURE_LENGTH)
    streamed = run_stream(signals["mic"], signals["render"], chunks=plan)
    return {
        "chunks": plan,
        "accepted_samples": FIXTURE_LENGTH,
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
    carried = PairedReferenceResidualChain(epoch=1)
    offset = 0
    while offset < len(mic):
        frame = list(mic[offset:offset + FRAME_SAMPLES])
        reference = list(render[offset:offset + FRAME_SAMPLES])
        count = len(frame)
        frame.extend([0] * (FRAME_SAMPLES - count))
        reference.extend([0] * (FRAME_SAMPLES - count))
        carried.process_frame(frame, reference, valid_count=count)
        offset += FRAME_SAMPLES
    carried.reset(2, 0)
    offset = 0
    while offset < len(mic):
        frame = list(mic[offset:offset + FRAME_SAMPLES])
        reference = list(render[offset:offset + FRAME_SAMPLES])
        count = len(frame)
        frame.extend([0] * (FRAME_SAMPLES - count))
        reference.extend([0] * (FRAME_SAMPLES - count))
        carried.process_frame(frame, reference, valid_count=count, epoch=2)
        offset += FRAME_SAMPLES
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
    carrier = PairedReferenceResidualChain(epoch=1)
    frame = list(signals["mic"][:FINAL_PARTIAL_VALID])
    reference = list(signals["render"][:FINAL_PARTIAL_VALID])
    frame.extend([0] * (FRAME_SAMPLES - FINAL_PARTIAL_VALID))
    reference.extend([0] * (FRAME_SAMPLES - FINAL_PARTIAL_VALID))
    output, residual = carrier.process_frame(frame, reference,
                                             valid_count=FINAL_PARTIAL_VALID)
    return {
        "valid_count": FINAL_PARTIAL_VALID,
        "padding_zero": True,
        "output_samples": len(output),
        "advanced_samples": carrier.position,
        "tail_zero": all(value == 0.0
                         for value in output[FINAL_PARTIAL_VALID:]),
        "nonfinite_output_count": _check_finite(output),
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
    "render_delay_samples",
    "sample_rate_hz",
    "source_commit",
    "source_sha256",
    "variant",
    "weights_sha256",
}


def validate_caller_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    _exact_keys(manifest, CALLER_MANIFEST_FIELDS, "caller_manifest")
    _string(manifest["adapter"], "adapter", 1, 64)
    _string(manifest["variant"], "variant", 1, 64)
    rate = _integer(manifest["sample_rate_hz"], "sample_rate_hz", 1, 384000)
    channels = _integer(manifest["channels"], "channels", 1, 8)
    frame = _integer(manifest["frame_samples"], "frame_samples", 1, 4096)
    delay = _integer(manifest["render_delay_samples"],
                     "render_delay_samples", 0, 480)
    latency = _integer(manifest["algorithmic_latency_samples"],
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
    if delay != RENDER_DELAY_SAMPLES:
        raise ReferenceRejection("unsupported_render_delay")
    if latency != 0:
        raise ReferenceRejection("unsupported_algorithmic_latency")
    _absolute_path(manifest["model_path"], "model_path")
    _absolute_path(manifest["library_path"], "library_path")
    _sha256(manifest["model_sha256"], "model_sha256")
    _sha256(manifest["weights_sha256"], "weights_sha256")
    _sha256(manifest["source_sha256"], "source_sha256")
    _sha256(manifest["library_sha256"], "library_sha256")
    _commit(manifest["source_commit"], "source_commit")
    return {"validated": True, "loaded": False, "executed": False,
            "imported": False}


# ---------------------------------------------------------------------------
# Adverse rejection matrix
# ---------------------------------------------------------------------------

def _base_config() -> Dict[str, Any]:
    return {"sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES, "sample_format": SAMPLE_FORMAT,
            "clock_ppm": 0, "resampling": "none",
            "render_delay_samples": RENDER_DELAY_SAMPLES,
            "algorithmic_latency_samples": 0}


def _base_manifest() -> Dict[str, Any]:
    return {
        "adapter": "dual-branch-residual-echo-suppressor-reference",
        "algorithmic_latency_samples": 0,
        "channels": 1,
        "frame_samples": 160,
        "input_format": "float32",
        "library_path": "/caller/dual-branch-residual-echo-suppressor/lib",
        "library_sha256": "3" * 64,
        "model_path": "/caller/dual-branch-residual-echo-suppressor/model",
        "model_sha256": "0" * 64,
        "render_delay_samples": RENDER_DELAY_SAMPLES,
        "sample_rate_hz": 16000,
        "source_commit": "0" * 40,
        "source_sha256": "1" * 64,
        "variant": "dual-branch-residual",
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
    add("config_256_frame", "unsupported_frame_samples",
        lambda: validate_config({**base, "frame_samples": 256}))
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
        lambda: validate_config({**base, "algorithmic_latency_samples": 160}))
    add("config_bool_rate", "invalid_integer:sample_rate_hz",
        lambda: validate_config({**base, "sample_rate_hz": True}))

    suppressor = PairedReferenceResidualChain(epoch=1)
    signals = build_fixture()
    frame = list(signals["mic"][:FRAME_SAMPLES])
    reference = list(signals["render"][:FRAME_SAMPLES])
    suppressor.process_frame(frame, reference)
    before = suppressor.state_digest

    def add_frame(case_id: str, code: str, action) -> None:
        actual = _expect_reject(code, action)
        cases.append({
            "case_id": case_id,
            "code": actual,
            "status": "rejected" if actual != "accepted" else "accepted",
            "state_unchanged": suppressor.state_digest == before,
        })

    add_frame("frame_missing_mic", "missing_input",
              lambda: suppressor.process_frame(None, reference))
    add_frame("frame_missing_render", "missing_render",
              lambda: suppressor.process_frame(frame, None))
    add_frame("frame_epoch_mismatch", "epoch_mismatch",
              lambda: suppressor.process_frame(frame, reference, epoch=2))
    add_frame("frame_mic_count_mismatch", "frame_count_mismatch:mic",
              lambda: suppressor.process_frame(frame[:159], reference))
    add_frame("frame_render_count_mismatch", "frame_count_mismatch:render",
              lambda: suppressor.process_frame(frame, reference[:159]))
    add_frame("frame_valid_count_zero", "invalid_integer:valid_count",
              lambda: suppressor.process_frame(frame, reference,
                                               valid_count=0))
    add_frame("frame_valid_count_high", "invalid_integer:valid_count",
              lambda: suppressor.process_frame(frame, reference,
                                               valid_count=161))
    add_frame("frame_nonfinite_mic", "nonfinite_input:mic",
              lambda: suppressor.process_frame(
                  [float("nan")] + frame[1:], reference))
    add_frame("frame_nonfinite_render", "nonfinite_input:render",
              lambda: suppressor.process_frame(
                  frame, [float("inf")] + reference[1:]))
    add_frame("frame_nonzero_mic_padding", "padding_not_zero:mic",
              lambda: suppressor.process_frame(
                  frame[:137] + [1.0] + frame[138:], reference,
                  valid_count=137))
    add_frame("frame_nonzero_render_padding", "padding_not_zero:render",
              lambda: suppressor.process_frame(
                  frame, reference[:137] + [1.0] + reference[138:],
                  valid_count=137))
    add_frame("frame_string_sample", "invalid_sample:mic",
              lambda: suppressor.process_frame(["x"] + frame[1:],
                                               reference))
    add_frame("frame_bool_sample", "invalid_sample:mic",
              lambda: suppressor.process_frame([True] + frame[1:],
                                               reference))
    add_frame("frame_input_position_mismatch", "input_position_mismatch",
              lambda: suppressor.process_frame(frame, reference,
                                               first_input_sample=1))

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
             if key != "weights_sha256"}))
    add("caller_manifest_relative_model_path",
        "invalid_source_path:model_path",
        lambda: validate_caller_manifest(
            {**manifest, "model_path": "relative/model"}))
    add("caller_manifest_bad_commit", "invalid_string:source_commit",
        lambda: validate_caller_manifest(
            {**manifest, "source_commit": "not-a-commit"}))
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
    add("caller_manifest_wrong_delay", "unsupported_render_delay",
        lambda: validate_caller_manifest(
            {**manifest, "render_delay_samples": 0}))
    add("caller_manifest_extra_field", "strict_keys_mismatch:caller_manifest",
        lambda: validate_caller_manifest({**manifest, "extra": 1}))

    def bad_fixture(**changes):
        spec = fixture_spec()
        spec.update(changes)
        validate_fixture(spec)

    add("fixture_length_mismatch", "fixture_length_mismatch",
        lambda: bad_fixture(length_samples=11999))
    add("fixture_switch_out_of_range", "fixture_switch_mismatch",
        lambda: bad_fixture(path_switch_sample=1))
    add("fixture_segment_count", "fixture_segment_count",
        lambda: bad_fixture(segments=fixture_spec()["segments"][:-1]))
    add("fixture_tap_order", "tap_order_mismatch",
        lambda: bad_fixture(echo_taps_before=[[4, 1], [0, 1]]))
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
            "render_reference_freeze": {
                "status": "synthetic_only",
                "evidence": ("Frozen 16 kHz mono 160-sample synthetic render "
                             "and fixed integer-tap echo paths with declared "
                             "delay, noise levels, path switch and reset "
                             "schedule."),
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
                "evidence": ("Independent gate-only control without a "
                             "paired-reference canceller is measured "
                             "separately on the same synthetic mic."),
            },
            "echo_attenuation": {
                "status": "synthetic_only",
                "evidence": ("Chain and canceller-only ERLE in integer "
                             "millidB on synthetic echo-only regions only."),
            },
            "near_end_damage": {
                "status": "synthetic_only",
                "evidence": ("Near-reference SNR, level change and peak on "
                             "synthetic near-end regions; no MOS or listening."),
            },
            "nonfinite_failures": {
                "status": "synthetic_only",
                "evidence": ("Nonfinite input and output checks plus peak "
                             "bound on synthetic frames; no runtime failure."),
            },
            "alignment_delayed_missing_render": {
                "status": "synthetic_only",
                "evidence": ("Declared 32-sample render delay, one 64-sample "
                             "shifted-render failure probe and one missing-"
                             "render rejection; no candidate alignment."),
            },
            "movement_path_change": {
                "status": "synthetic_only",
                "evidence": ("One fixed synthetic coefficient switch at "
                             "sample 9600; no real movement or device mic."),
            },
            "task_matched_heldout_qualification": {
                "status": "blocked",
                "evidence": ("No rights-cleared paired render/capture cohort, "
                             "held-out split, AECMOS/STOI/ASR or listening "
                             "result."),
            },
        },
    }


def _profile_blockers(profile: Dict[str, Any]) -> List[str]:
    return sorted(name for name, item in profile["required_items"].items()
                  if item["status"] == "blocked")


def _release_gates() -> List[Dict[str, str]]:
    rows = [
        ("RG-01", "Exact pinned dual-branch residual echo suppressor source, "
                  "weights, runtime and dual-branch architecture with an "
                  "immutable revision, license identity and geometry record."),
        ("RG-02", "Isolated hash-pinned runtime admission, reproducible build, "
                  "verified weight identity and fail-closed absent behavior."),
        ("RG-03", "Code, weight, training-data and corpus rights plus "
                  "attribution, notices, redistribution, product-use and "
                  "derivative-output review."),
        ("RG-04", "Explicit paired-reference canceller attachment, two-input "
                  "geometry, declared delay and clock mapping into the SDK "
                  "duplex contract with byte-level parity."),
        ("RG-05", "Echo-only, near-end-only, overlap/double-talk and "
                  "independent no-reference qualification on a rights-cleared "
                  "task-matched held-out paired cohort including ERLE, "
                  "preservation and alignment."),
        ("RG-06", "Streaming state, reset, latency, availability, path change, "
                  "delayed/missing render and nonfinite behavior at the exact "
                  "runtime."),
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
            "id": "pinned_candidate_source_weights_runtime_absent",
            "requirement": ("Supply one exact licensed dual-branch residual "
                            "echo suppressor source tree, weight file and "
                            "runtime with immutable revision, build/archive "
                            "identity and declared adapter settings."),
            "state": ("The pinned research note records only a research lead "
                      "and states that candidate code/checkpoint availability "
                      "was not verified. No candidate source, weight, runtime, "
                      "adapter or revision is staged at "
                      "data/checkouts/dual-branch-residual-echo-suppressor, "
                      "data/models/dual-branch-residual-echo-suppressor, "
                      "data/envs/dual-branch-residual-echo-suppressor or "
                      "adapters/dual-branch-residual-echo-suppressor."),
        },
        {
            "id": "dual_branch_architecture_and_residual_geometry_unverified",
            "requirement": ("Document the exact two-branch architecture, "
                            "residual/echo feature split, input rate, hop, "
                            "channel layout, render delay, lookahead and "
                            "output alignment for the pinned weights."),
            "state": ("The pinned note names dual-branch guidance/dual-stream "
                      "residual echo suppressors only as an aim and records "
                      "no exact architecture, sample rate, hop, channel "
                      "layout, render delay, lookahead or numeric output. No "
                      "candidate geometry is asserted."),
        },
        {
            "id": "rights_attribution_and_weights_review_absent",
            "requirement": ("Stage the exact code and weight license, "
                            "attribution notice, training-data terms and "
                            "complete distribution, derivative and product-use "
                            "review."),
            "state": ("No upstream LICENSE, model card, weight terms, "
                      "training-data statement, notice bundle or legal review "
                      "is staged. The pinned evidence records no license "
                      "identity for the candidate."),
        },
        {
            "id": "paired_reference_canceller_attachment_and_sdk_boundary_absent",
            "requirement": ("Admit an accepted paired-reference canceller "
                            "boundary, make the suppressor attachment explicit, "
                            "and map candidate delay/clock behavior into the "
                            "installed SDK path with exact parity."),
            "state": ("Installed v0 accepts one 16 kHz mono 160-sample stream. "
                      "The merged duplex evidence is a model-free proposal "
                      "with no residual-suppressor provider geometry, and "
                      "nothing maps a post-canceller residual plus render "
                      "reference into this candidate."),
        },
        {
            "id": "rights_cleared_paired_cohort_and_double_talk_absent",
            "requirement": ("Supply a rights-cleared task-matched held-out "
                            "paired render/capture cohort with echo-only, "
                            "near-end-only, overlap/double-talk, movement and "
                            "no-reference strata plus AECMOS/STOI/ASR or "
                            "listening labels."),
            "state": ("No real paired recording, room response, consent, "
                      "corpus terms, held-out split or task-matched "
                      "double-talk score is staged. Synthetic integer "
                      "fixtures cannot qualify the candidate."),
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
        "note": ("The pinned evidence records only a research lead and no "
                 "license identity, upstream license text, weight terms or "
                 "training data statement."),
    }


def _candidate() -> Dict[str, Any]:
    return {
        "name": "Dual-branch residual echo suppressor",
        "reported_algorithm": ("dual-branch residual echo suppression with an "
                               "explicit attachment to a paired-reference "
                               "canceller; exact architecture not verified"),
        "reported_parameter_count": CANDIDATE_REPORTED_PARAMETERS,
        "reported_input_sample_rate_hz": CANDIDATE_REPORTED_RATE_HZ,
        "reported_hop_samples": None,
        "reported_render_delay_samples": None,
        "geometry_documented": False,
        "source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "exact_numeric_output_present": False,
    }


def _external_artifacts() -> Dict[str, Any]:
    paths = {
        "source_checkout": "data/checkouts/dual-branch-residual-echo-suppressor",
        "weights": "data/models/dual-branch-residual-echo-suppressor",
        "runtime_env": "data/envs/dual-branch-residual-echo-suppressor",
        "adapter": "adapters/dual-branch-residual-echo-suppressor",
        "caller_manifest": "data/manifests/dual-branch-residual-echo-suppressor.json",
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
    "No dual-branch residual echo suppressor source, weight file, runtime, "
    "adapter, revision or numeric output was produced, loaded or executed.",
    "No echo, residual-suppression, quality, latency, benchmark, listening or "
    "release result is claimed.",
    "The synthetic NLMS paired-reference canceller front end plus residual "
    "gate is not the candidate and cannot qualify the candidate.",
    "No candidate input rate, hop, channel layout, branch topology, render "
    "delay, lookahead or alignment is asserted.",
    "Synthetic ERLE, near-reference SNR and level change are unqualified "
    "task-local observations only.",
    "No real room, paired recording, corpus, AECMOS/STOI/ASR score, device "
    "clock or listener was used.",
    "No upstream license text, attribution bundle, weight terms or training "
    "data statement is staged.",
    "No provider, descriptor, registry, installed v0 path, shared build, "
    "dependency lock or CI was changed.",
)

REOPEN_CONDITION = (
    "Pin the exact licensed dual-branch residual echo suppressor source, "
    "weights and runtime with an immutable revision and documented two-branch "
    "geometry, admit an isolated hash-pinned runtime, clear "
    "code/weight/training-data/corpus rights, make the paired-reference "
    "canceller attachment explicit and map paired render/capture delay and "
    "clocks into the accepted duplex contract, reproduce exact output, "
    "qualify echo-only, near-end-only, overlap/double-talk and independent "
    "no-reference behavior on a rights-cleared task-matched held-out cohort, "
    "measure target timing and complete opt-in provider intake. Until then the "
    "candidate stays DEFER, incomplete and not qualified."
)


def _case_matrix_digest(run: Dict[str, Any], alignment: Dict[str, Any],
                        no_reference: Dict[str, Any],
                        streaming: Dict[str, Any],
                        reset: Dict[str, Any]) -> str:
    return object_digest({
        "signals": run["signal_digests"],
        "erle": [(row["segment"], row["erle_millidb"],
                  row["aec_only_erle_millidb"])
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
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
            "length_samples": FIXTURE_LENGTH,
            "duration_ns": FIXTURE_LENGTH * SAMPLE_NS,
            "render_delay_samples": RENDER_DELAY_SAMPLES,
            "filter_tail_samples": TAIL_SAMPLES,
            "path_switch_sample": PATH_SWITCH_SAMPLE,
            "segments": [dict(segment) for segment in SEGMENTS],
            "echo_taps_before": [list(tap) for tap in ECHO_TAPS_BEFORE],
            "echo_taps_after": [list(tap) for tap in ECHO_TAPS_AFTER],
        },
        "signal_digests": run["signal_digests"],
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
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "license_identity": None,
            "pinned_revision": None,
            "status": "blocked",
            "surrogate_is_candidate": False,
            "paired_reference_canceller_attached": False,
        },
        "format": {
            "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "sdk_v0_channels": CHANNELS,
            "sdk_v0_frame_samples": FRAME_SAMPLES,
            "sdk_v0_sample_format": SAMPLE_FORMAT,
            "candidate_reported_sample_rate_hz": CANDIDATE_REPORTED_RATE_HZ,
            "candidate_geometry_documented": False,
            "resampling": "none",
            "paired_render_in_installed_v0": False,
            "duplex_reference_contract": (
                "audio-sdk/duplex-reference-clocks/0.1 proposal only"),
            "surrogate_render_delay_samples": RENDER_DELAY_SAMPLES,
            "surrogate_algorithmic_latency_samples": 0,
            "surrogate_content_delay_samples": 0,
            "candidate_two_branch_geometry_documented": False,
        },
        "fixtures": _fixtures(fixture),
        "paired_reference_attachment": {
            "explicit": True,
            "front_end": ("fixed integer-tap NLMS paired-reference canceller "
                          "surrogate; not candidate code"),
            "residual_input": "post-canceller residual plus render reference",
            "candidate_attachment_verified": False,
            "installed_v0_two_input_path": False,
            "qualifies": False,
        },
        "echo_attenuation": {
            "regions": fixture["erle_regions"],
            "min_erle_millidb": min(erle_values),
            "max_erle_millidb": max(erle_values),
            "overall_erle_millidb": fixture["overall"]["erle_millidb"],
            "overall_aec_only_erle_millidb": fixture["overall"][
                "aec_only_erle_millidb"],
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
        "double_talk_preservation": {
            "region": fixture["overlap"]["segment"],
            "near_reference_snr_millidb": fixture["overlap"][
                "near_reference_snr_millidb"],
            "level_change_millidb": fixture["overlap"]["level_change_millidb"],
            "peak_milli": fixture["overlap"]["peak_milli"],
            "candidate_double_talk_output": False,
            "qualifies": False,
        },
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
        "licensing": licensing,
        "caller_asset": {
            "contract_id":
                "audio-sdk/dual-branch-residual-echo-suppressor/caller-supplied-asset/0.1",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "manifest_present": False,
            "workspace_manifest": "data/manifests/dual-branch-residual-echo-suppressor.json",
            "present_behavior": ("validate_identity_geometry_only; do_not_load"
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
            "rights_cleared_cohort": False,
            "geometry_documented": False,
            "paired_render_contract_qualified": False,
            "echo_only_qualified": False,
            "near_end_qualified": False,
            "overlap_qualified": False,
            "no_reference_qualified": False,
            "timing_measured": False,
            "listening": False,
            "real_corpus_used": False,
            "reason": ("Exact dual-branch residual echo suppressor "
                       "source/weights/runtime, two-branch geometry, explicit "
                       "paired-reference attachment, rights, paired-render "
                       "admission, rights-cleared double-talk data, timing "
                       "and independent review are all absent."),
        },
        "exact_blockers": blockers,
        "release_gates": gates,
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "surrogate": {
            "algorithm": ("bounded integer-tap NLMS paired-reference "
                          "canceller front end plus deterministic residual "
                          "energy gate"),
            "is_candidate": False,
            "is_learned": False,
            "is_neural_network": False,
            "uses_weights": False,
            "paired_reference_attachment_modeled": True,
            "candidate_architecture_verified": False,
            "qualifies_candidate": False,
        },
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "case_matrix_digests": [matrix, matrix, matrix],
        },
        "scope_note": ("Only docs/task-evidence/dual-branch-residual-echo-suppressor/ is "
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
        "caller_asset_contract": {
            "contract_id":
                "audio-sdk/dual-branch-residual-echo-suppressor/caller-supplied-asset/0.1",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "required_fields": sorted(CALLER_MANIFEST_FIELDS),
            "present_behavior": ("validate_identity_geometry_only; do_not_load"
                                 "_or_execute"),
            "absent_behavior": "reject_before_processing",
            "separate_archive_required": True,
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no candidate source, weight, dual-branch layer, recurrent or "
            "attention block, runtime or adapter is downloaded, copied, "
            "loaded or executed",
            "the synthetic NLMS paired-reference front end plus residual gate "
            "is not the candidate and cannot qualify the candidate",
            "no candidate input rate, hop, channel layout, branch topology, "
            "render delay, lookahead or alignment is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def sources_bytes(overrides: Dict[str, bytes] | None = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR; source: paths are "
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
    "PairedReferenceResidualChain", "NoReferenceResidualGate", "ReferenceRejection", "SEGMENTS",
    "adverse_rejections", "alignment_run", "board_row", "build_contract",
    "build_fixture", "build_report", "canonical_report", "canonical_text",
    "chunk_plan", "final_partial_check", "fixture_run", "fixture_spec",
    "int_signal_digest", "load_strict_json", "load_strict_json_text",
    "no_reference_comparison", "object_digest", "reset_check", "run_stream",
    "sha256_bytes", "signal_digest", "sources_bytes", "streaming_check",
    "validate_caller_manifest", "validate_config", "validate_fixture",
]
