# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local MVDR beamforming blocker and strict prerequisite validator.

This module is the bounded evidence core for ``SDK-MVDR-BEAMFORMING``.  The
catalogued MVDR/MPDR candidates are documentation-only search excerpts
(``S24`` Pyroomacoustics beamforming, ``S25`` TorchAudio mask-based MVDR
tutorial).  No licensed source tree, package, archive, executable, runtime,
adapter, immutable revision, licence grant, mask model, covariance estimator,
rights-cleared synchronized array corpus or device calibration is staged in
this workspace.

Nothing here is MVDR.  The module deliberately does **not** estimate a
covariance matrix, does not apply a mask to a beamformer, and produces no
beamformed numeric result.  It exists to:

* parse and validate a declared array geometry with a declared reference
  channel using exact integer arithmetic;
* parse and strictly validate a structural mask manifest (shape, group,
  range, finiteness, timing mode) without using it for beamforming;
* parse and strictly validate a structural MVDR plan manifest, while
  reporting that structural completeness is not qualification;
* generate one frozen synthetic fixture and an exact equal-weight
  delay-and-sum **control** so that a future licensed runtime can be compared
  against the identical bytes;
* record every missing artifact and right as a machine-readable blocker.

The delay-and-sum output in this package is a control reference only.  It is
``is_mvdr=false``, ``status=control_only_not_qualified`` and can never
qualify MVDR or stand in for an MVDR result.  ``distortion_comparison`` stays
``blocked`` because there is no MVDR output to compare.

Arithmetic is exact: positions are integer nanometres, the speed of sound is
pinned to ``343 nm/ns``, one 16 kHz sample is exactly ``62_500 ns``, steering
delays are exact rational sample offsets, and fixture samples and the control
output are exact integers and reduced fractions.  No floating-point
trigonometry, no platform-dependent ``sin``/``cos`` and no tolerance is used.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]

TASK_ID = "SDK-MVDR-BEAMFORMING"
TITLE = "MVDR beamforming"
COMPONENT = "mvdr-beamforming"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-MVDR-BEAMFORMING"
BASE_COMMIT = "f8416852b07c700d232f75b28daba3de84748696"
TASK_PREFIX = "docs/task-evidence/mvdr-beamforming/"
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SAMPLE_RATE_HZ = 16000
SAMPLE_PERIOD_NS = 62_500
FRAME_SAMPLES = 160
SPEED_OF_SOUND_NM_PER_NS = 343
Q16 = 65_536
UNITY_GAIN_Q16 = 65_536
MIN_MICS = 2
MAX_MICS = 16
MAX_POSITION_NM = 10_000_000_000
MAX_ABS_SAMPLE = 1_000_000
MAX_SAMPLES = 1_000_000
MAX_MASK_FRAMES = 100_000
MAX_MASK_BINS = 1024

GEOMETRY_SCHEMA = "audio-sdk/beamforming-geometry/0.1"
MASK_SCHEMA = "audio-sdk/mvdr-mask-manifest/0.1"
PLAN_SCHEMA = "audio-sdk/mvdr-plan/0.1"
FIXTURE_SCHEMA = "audio-sdk/mvdr-fixture/0.1"
REPORT_SCHEMA = "audio-sdk/mvdr-beamforming-report/0.1"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
REVISION_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")

GEOMETRY_FIELDS = {
    "schema_id",
    "array_id",
    "sample_rate_hz",
    "speed_of_sound_nm_per_ns",
    "reference_mic_id",
    "microphones",
    "steering_direction",
    "channels",
}
MIC_FIELDS = {"id", "position_nm"}
CHANNEL_FIELDS = {"mic_id", "clock_ppm", "calibration_gain_q16"}
MASK_FIELDS = {
    "schema_id",
    "mask_group",
    "sample_rate_hz",
    "frame_hop_samples",
    "frames",
    "bins",
    "timing_mode",
    "values",
}
COVARIANCE_FIELDS = {
    "estimator",
    "diagonal_loading_q16",
    "smoothing_frames",
    "rank",
}
PLAN_FIELDS = {
    "schema_id",
    "source_id",
    "source_url",
    "source_revision",
    "source_sha256",
    "license_grant",
    "runtime",
    "adapter_id",
    "array_geometry_digest",
    "reference_mic_id",
    "mask_group",
    "covariance",
    "delay_and_sum_baseline_id",
}
MASK_GROUPS = {"oracle", "estimated"}
TIMING_MODES = {"causal", "offline_declared"}

#: Stable read-only source pins, relative to the workspace root.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/handoffs/SDK-SURVEY-CLN-07.md":
        "441e8a11f2dabe94a307a85d6d033cd999dca857f1857b54dfae5d512640c592",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/category_survey/revisions/v1/audio_categories.md":
        "24411d808836d89b730ba3522e6b5ade34d0acd70df235f043cd36155974c265",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
}

#: Stable read-only SDK boundary pins, relative to the SDK worktree root.
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/README.md":
        "514636b719e6579651bf941a6ac3cb93740cc9a40e3f2b4bcd39c2ddea610264",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/contract.json":
        "c7b0f4ac8191abe114b4f77ae17c803ffbda1fe4012e12d42808ca798d0afb88",
    "docs/task-evidence/3d-microphone-spatial-time-alignment/report.json":
        "5d3623c835a1b19d79867a64ba1b6dff18e8593918a8173cff91550c1c532f03",
    "docs/task-evidence/delay-and-sum-beamformer/README.md":
        "858cfaceb546a6c8940f4f2050e6313117bd2007ac1df25a4d87848fdfeb5bd8",
    "docs/task-evidence/delay-and-sum-beamformer/contract.json":
        "840b013887087208219327cda3c99d51df510a7e34c04d5957eaefa608ae017e",
    "docs/task-evidence/delay-and-sum-beamformer/report.json":
        "9dce5b38ce76197c1650af10c6c4fb3dad4f454e8d87d60d807cdde85b8f8af2",
    "docs/task-evidence/auxiva/README.md":
        "efeeda6457b5e9e8153253b93e107cc003fc1c9b705bdd399ac908a03254d81b",
    "docs/task-evidence/auxiva/report.json":
        "92f21086d2988286c487228171621b0c5c35f2bf65141acac160f9811581db26",
    "docs/task-evidence/offline-multichannel-wpe/README.md":
        "8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9",
    "docs/task-evidence/offline-multichannel-wpe/report.json":
        "4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba",
    "docs/task-evidence/survey-cln-07/README.md":
        "b748f2fda2ffebf10ea5f00923dc1dc1110f0712bada2ded074def53ef682d34",
    "docs/task-evidence/survey-cln-07/report.json":
        "aad53c0a3e6d90c4d27fea6abb4001d40168700a8fa2d717f53b03091a9c5a6a",
    "docs/task-evidence/validity-and-installed-delays.md":
        "c84e75c0a60a99175b9c6bcf7e344908b1f8edfe17dc16a5536be715dd50613f",
}

#: Task-local artifacts pinned by contract.json and SOURCES.sha256.
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

SOURCE_FILES: Tuple[str, ...] = tuple(SOURCE_PINS)
BOUNDARY_FILES: Tuple[str, ...] = tuple(BOUNDARY_PINS)
PIN_FILES: Tuple[str, ...] = (
    "README.md",
    "contract.json",
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


class Reject(ValueError):
    """A bounded, deterministic input rejection."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise Reject(code)


def _strict_pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise Reject("duplicate_json_key:" + key)
        result[key] = value
    return result


def _strict_constant(token: str) -> None:
    raise Reject("nonfinite_json_constant:" + token)


def parse_strict_json(text: str) -> Any:
    """Parse strict JSON, rejecting duplicate keys and non-finite constants."""
    try:
        return json.loads(text, object_pairs_hook=_strict_pairs,
                          parse_constant=_strict_constant)
    except Reject:
        raise
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        raise Reject("invalid_json") from error


def load_strict_json(path: Path) -> Any:
    return parse_strict_json(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def _is_id(value: Any) -> bool:
    return isinstance(value, str) and ID_PATTERN.fullmatch(value) is not None


def _exact_keys(document: Any, fields: set, code: str) -> Dict[str, Any]:
    _require(isinstance(document, dict), code)
    _require(set(document) == fields, code)
    return document


def parse_geometry(document: Any) -> Dict[str, Any]:
    """Validate a declared array geometry; exact integer arithmetic only."""
    document = _exact_keys(document, GEOMETRY_FIELDS, "invalid_geometry_fields")
    _require(document["schema_id"] == GEOMETRY_SCHEMA, "invalid_geometry_schema")
    _require(_is_id(document["array_id"]), "invalid_array_id")
    _require(document["sample_rate_hz"] == SAMPLE_RATE_HZ,
             "unsupported_sample_rate")
    _require(document["speed_of_sound_nm_per_ns"] == SPEED_OF_SOUND_NM_PER_NS,
             "unsupported_speed_of_sound")

    microphones = document["microphones"]
    _require(isinstance(microphones, list), "invalid_microphones")
    _require(MIN_MICS <= len(microphones) <= MAX_MICS,
             "invalid_microphone_count")
    seen_ids = set()
    seen_positions = set()
    normalized_mics = []
    for mic in microphones:
        mic = _exact_keys(mic, MIC_FIELDS, "invalid_microphone_fields")
        _require(_is_id(mic["id"]), "invalid_microphone_id")
        _require(mic["id"] not in seen_ids, "duplicate_mic_id")
        seen_ids.add(mic["id"])
        position = mic["position_nm"]
        _require(isinstance(position, list) and len(position) == 3,
                 "invalid_position")
        for value in position:
            _require(_is_int(value), "invalid_position")
            _require(abs(value) <= MAX_POSITION_NM, "invalid_position")
        key = tuple(position)
        _require(key not in seen_positions, "duplicate_mic_position")
        seen_positions.add(key)
        normalized_mics.append({"id": mic["id"], "position_nm": list(position)})

    reference = document["reference_mic_id"]
    _require(reference in seen_ids, "unknown_reference_mic")

    direction = document["steering_direction"]
    _require(isinstance(direction, list) and len(direction) == 3,
             "invalid_steering_direction")
    for value in direction:
        _require(_is_int(value), "invalid_steering_direction")
    squared = sum(value * value for value in direction)
    _require(squared > 0, "zero_steering_direction")
    norm = math.isqrt(squared)
    _require(norm * norm == squared,
             "steering_direction_not_exactly_normalizable")

    channels = document["channels"]
    _require(isinstance(channels, list), "invalid_channels")
    _require(len(channels) == len(microphones), "channel_count_mismatch")
    normalized_channels = []
    seen_channels = set()
    for channel in channels:
        channel = _exact_keys(channel, CHANNEL_FIELDS, "invalid_channel_fields")
        mic_id = channel["mic_id"]
        _require(_is_id(mic_id), "invalid_channel_mic")
        _require(mic_id in seen_ids, "unknown_channel_mic")
        _require(mic_id not in seen_channels, "duplicate_channel_mic")
        seen_channels.add(mic_id)
        _require(_is_int(channel["clock_ppm"]), "invalid_channel_clock")
        _require(channel["clock_ppm"] == 0, "clock_drift_not_supported")
        _require(_is_int(channel["calibration_gain_q16"]),
                 "invalid_channel_calibration")
        _require(channel["calibration_gain_q16"] == UNITY_GAIN_Q16,
                 "uncalibrated_channel_not_supported")
        normalized_channels.append({
            "mic_id": mic_id,
            "clock_ppm": 0,
            "calibration_gain_q16": UNITY_GAIN_Q16,
        })
    _require(seen_channels == seen_ids, "channel_mic_set_mismatch")

    return {
        "schema_id": GEOMETRY_SCHEMA,
        "array_id": document["array_id"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "speed_of_sound_nm_per_ns": SPEED_OF_SOUND_NM_PER_NS,
        "reference_mic_id": reference,
        "microphones": sorted(normalized_mics, key=lambda mic: mic["id"]),
        "steering_direction": list(direction),
        "channels": sorted(normalized_channels, key=lambda item: item["mic_id"]),
    }


def steering_delays(geometry: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Exact plane-wave steering delays relative to the declared reference."""
    direction = geometry["steering_direction"]
    norm = math.isqrt(sum(value * value for value in direction))
    speed = geometry["speed_of_sound_nm_per_ns"]
    positions = {mic["id"]: mic["position_nm"] for mic in geometry["microphones"]}
    reference = geometry["reference_mic_id"]

    def tdoa_ns(mic_id: str) -> Fraction:
        dot = sum(positions[mic_id][axis] * direction[axis] for axis in range(3))
        return Fraction(-dot, speed * norm)

    base = tdoa_ns(reference)
    delays = []
    for mic in geometry["microphones"]:
        relative_ns = tdoa_ns(mic["id"]) - base
        samples = relative_ns * Q16 / SAMPLE_PERIOD_NS
        exact = samples.denominator == 1
        delays.append({
            "mic_id": mic["id"],
            "relative_q16": int(samples) if exact else None,
            "relative_samples": fraction_text(relative_ns * 1 / SAMPLE_PERIOD_NS),
            "exact_integer_sample": exact,
        })
    return delays


def fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def fixture_geometry() -> Dict[str, Any]:
    """The single frozen 4-microphone planar geometry used by this package."""
    positions = [
        [0, 0, 0],
        [107_187_500, 0, 0],
        [0, 26_796_875, 0],
        [107_187_500, 26_796_875, 0],
    ]
    microphones = [
        {"id": f"m{index}", "position_nm": position}
        for index, position in enumerate(positions)
    ]
    return parse_geometry({
        "schema_id": GEOMETRY_SCHEMA,
        "array_id": "mvdr-fixture-planar-4mic",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "speed_of_sound_nm_per_ns": SPEED_OF_SOUND_NM_PER_NS,
        "reference_mic_id": "m0",
        "microphones": microphones,
        "steering_direction": [3, 4, 0],
        "channels": [
            {"mic_id": mic["id"], "clock_ppm": 0,
             "calibration_gain_q16": UNITY_GAIN_Q16}
            for mic in microphones
        ],
    })


def fixture_click_index() -> int:
    return 16


def fixture_amplitude() -> int:
    return 1000


def interference_sample(index: int) -> int:
    """Deterministic integer interference component, identical per channel."""
    _require(_is_int(index) and 0 <= index < MAX_SAMPLES, "invalid_source_time")
    return ((index * 37 + 11) % 101) - 50


def synthetic_channels(geometry: Dict[str, Any],
                       delays: Sequence[Dict[str, Any]]) -> List[List[int]]:
    """Build one frozen frame of deterministic integer synthetic channels."""
    clicks = {item["mic_id"]: item["relative_q16"] // Q16
              for item in delays}
    reference_index = fixture_click_index()
    amplitude = fixture_amplitude()
    channels: List[List[int]] = []
    for mic in geometry["microphones"]:
        click = reference_index + clicks[mic["id"]]
        _require(0 <= click < FRAME_SAMPLES, "click_out_of_range")
        row = []
        for index in range(FRAME_SAMPLES):
            value = interference_sample(index)
            if index == click:
                value += amplitude
            _require(abs(value) <= MAX_ABS_SAMPLE, "oversized_sample")
            row.append(value)
        channels.append(row)
    return channels


def validate_channels(channels: Any, mic_count: int) -> List[List[int]]:
    """Validate integer synthetic channel samples without any implicit cast."""
    _require(isinstance(channels, list), "channel_count_mismatch")
    _require(len(channels) == mic_count, "channel_count_mismatch")
    normalized = []
    for row in channels:
        _require(isinstance(row, list), "invalid_channel_length")
        _require(len(row) > 0, "invalid_channel_length")
        _require(len(row) == FRAME_SAMPLES, "channel_length_mismatch")
        out = []
        for sample in row:
            _require(isinstance(sample, (int, float))
                     and not isinstance(sample, bool), "invalid_sample_type")
            _require(not isinstance(sample, float) or math.isfinite(sample),
                     "nonfinite_sample")
            _require(_is_int(sample), "invalid_sample_type")
            _require(abs(sample) <= MAX_ABS_SAMPLE, "nonfinite_sample")
            out.append(sample)
        normalized.append(out)
    return normalized


def delay_and_sum_control(geometry: Dict[str, Any],
                          delays: Sequence[Dict[str, Any]],
                          channels: Sequence[Sequence[int]]) -> Dict[str, Any]:
    """Exact equal-weight delay-and-sum control.  This is never MVDR."""
    mic_count = len(channels)
    _require(mic_count >= MIN_MICS, "channel_count_mismatch")
    offsets = [item["relative_q16"] // Q16 for item in delays]
    output = []
    for index in range(FRAME_SAMPLES):
        total = 0
        for channel, offset in zip(channels, offsets):
            source = index + offset
            if 0 <= source < FRAME_SAMPLES:
                total += channel[source]
        output.append(Fraction(total, mic_count))
    peak_index = 0
    peak_value = output[0]
    for index, value in enumerate(output):
        if abs(value) > abs(peak_value):
            peak_index = index
            peak_value = value
    return {
        "control_id": "delay-and-sum-equal-weight-control-v1",
        "is_mvdr": False,
        "status": "control_only_not_qualified",
        "qualification_status": "not_qualified",
        "weighting": "equal_1_over_n",
        "adaptive_coefficients": False,
        "mask_applied": False,
        "covariance_used": False,
        "sample_count": FRAME_SAMPLES,
        "peak_index": peak_index,
        "peak_value_exact": fraction_text(peak_value),
        "max_abs_value_exact": fraction_text(
            max(abs(value) for value in output)),
        "output_exact": [fraction_text(value) for value in output],
        "output_digest": object_digest(
            [fraction_text(value) for value in output]),
    }


def build_fixture() -> Dict[str, Any]:
    geometry = fixture_geometry()
    delays = steering_delays(geometry)
    _require(all(item["exact_integer_sample"] for item in delays),
             "fractional_steering_not_exact")
    channels = validate_channels(synthetic_channels(geometry, delays),
                                 len(geometry["microphones"]))
    control = delay_and_sum_control(geometry, delays, channels)
    document = {
        "schema_id": FIXTURE_SCHEMA,
        "fixture_id": "mvdr-frozen-planar-4mic-v1",
        "geometry": geometry,
        "steering_delays": delays,
        "click_index": fixture_click_index(),
        "click_amplitude": fixture_amplitude(),
        "interference_rule": "((index*37+11)%101)-50",
        "frame_samples": FRAME_SAMPLES,
        "channels": channels,
    }
    return {
        "fixture": document,
        "fixture_digest": object_digest(document),
        "geometry_digest": object_digest(geometry),
        "control": control,
        "mvdr_output": {
            "present": False,
            "status": "blocked",
            "reason": "no_licensed_mvdr_source_or_runtime_staged",
            "executed": False,
            "result": None,
        },
    }


def parse_mask_manifest(document: Any) -> Dict[str, Any]:
    """Strict structural validation of a declared mask manifest."""
    document = _exact_keys(document, MASK_FIELDS, "invalid_mask_fields")
    _require(document["schema_id"] == MASK_SCHEMA, "invalid_mask_schema")
    _require(isinstance(document["mask_group"], str), "invalid_mask_group")
    _require(document["mask_group"] in MASK_GROUPS,
             "mixed_mask_group_not_permitted")
    _require(document["sample_rate_hz"] == SAMPLE_RATE_HZ,
             "unsupported_mask_sample_rate")
    _require(document["frame_hop_samples"] == FRAME_SAMPLES,
             "unsupported_mask_frame_hop")
    frames = document["frames"]
    _require(_is_int(frames) and 1 <= frames <= MAX_MASK_FRAMES,
             "invalid_mask_frames")
    bins = document["bins"]
    _require(_is_int(bins) and 1 <= bins <= MAX_MASK_BINS,
             "invalid_mask_bins")
    _require(document["timing_mode"] in TIMING_MODES, "invalid_mask_timing_mode")
    values = document["values"]
    _require(isinstance(values, list), "mask_shape_mismatch")
    _require(len(values) == frames, "mask_shape_mismatch")
    for row in values:
        _require(isinstance(row, list), "mask_shape_mismatch")
        _require(len(row) == bins, "mask_shape_mismatch")
        for value in row:
            _require(_is_number(value), "nonfinite_mask_value")
            _require(0 <= value <= 1, "invalid_mask_value")
    return {
        "schema_id": MASK_SCHEMA,
        "mask_group": document["mask_group"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_hop_samples": FRAME_SAMPLES,
        "frames": frames,
        "bins": bins,
        "timing_mode": document["timing_mode"],
        "values": [[value for value in row] for row in values],
    }


def fixture_mask_manifest() -> Dict[str, Any]:
    return parse_mask_manifest({
        "schema_id": MASK_SCHEMA,
        "mask_group": "oracle",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_hop_samples": FRAME_SAMPLES,
        "frames": 2,
        "bins": 3,
        "timing_mode": "offline_declared",
        "values": [[1, 0, 1], [0, 1, 1]],
    })


def parse_mvdr_plan(document: Any) -> Dict[str, Any]:
    """Strict structural validation of a declared MVDR plan manifest.

    Structural acceptance is *not* qualification: no plan is present in this
    package, and even a structurally complete plan would stay unexecuted.
    """
    document = _exact_keys(document, PLAN_FIELDS, "invalid_plan_fields")
    _require(document["schema_id"] == PLAN_SCHEMA, "invalid_plan_schema")
    _require(_is_id(document["source_id"]), "invalid_plan_source_id")
    _require(isinstance(document["source_url"], str)
             and 1 <= len(document["source_url"]) <= 512,
             "invalid_plan_source_url")
    _require(isinstance(document["source_revision"], str)
             and REVISION_PATTERN.fullmatch(document["source_revision"])
             is not None, "invalid_plan_source_revision")
    _require(isinstance(document["source_sha256"], str)
             and SHA256_PATTERN.fullmatch(document["source_sha256"])
             is not None, "invalid_plan_source_digest")
    _require(isinstance(document["license_grant"], str)
             and 1 <= len(document["license_grant"]) <= 256,
             "invalid_plan_license_grant")
    _require(_is_id(document["runtime"]), "invalid_plan_runtime")
    _require(_is_id(document["adapter_id"]), "invalid_plan_adapter")
    _require(isinstance(document["array_geometry_digest"], str)
             and SHA256_PATTERN.fullmatch(document["array_geometry_digest"])
             is not None, "invalid_plan_geometry_digest")
    _require(_is_id(document["reference_mic_id"]),
             "invalid_plan_reference_mic")
    _require(document["mask_group"] in MASK_GROUPS, "invalid_plan_mask_group")
    _require(_is_id(document["delay_and_sum_baseline_id"]),
             "invalid_plan_baseline")
    covariance = _exact_keys(document["covariance"], COVARIANCE_FIELDS,
                             "invalid_plan_covariance_fields")
    _require(_is_id(covariance["estimator"]),
             "invalid_plan_covariance_estimator")
    _require(_is_int(covariance["diagonal_loading_q16"])
             and 1 <= covariance["diagonal_loading_q16"] <= Q16,
             "invalid_plan_diagonal_loading")
    _require(_is_int(covariance["smoothing_frames"])
             and 1 <= covariance["smoothing_frames"] <= 1000,
             "invalid_plan_smoothing")
    _require(_is_int(covariance["rank"]) and 1 <= covariance["rank"] <= MAX_MICS,
             "invalid_plan_rank")
    return {
        "schema_id": PLAN_SCHEMA,
        "source_id": document["source_id"],
        "source_url": document["source_url"],
        "source_revision": document["source_revision"],
        "source_sha256": document["source_sha256"],
        "license_grant": document["license_grant"],
        "runtime": document["runtime"],
        "adapter_id": document["adapter_id"],
        "array_geometry_digest": document["array_geometry_digest"],
        "reference_mic_id": document["reference_mic_id"],
        "mask_group": document["mask_group"],
        "covariance": dict(covariance),
        "delay_and_sum_baseline_id": document["delay_and_sum_baseline_id"],
    }


def plan_readiness(plan: Any) -> Dict[str, Any]:
    """Report plan readiness.  A present plan is never 'qualified' or 'run'."""
    if plan is None:
        return {
            "present": False,
            "status": "blocked",
            "executed": False,
            "qualification_status": "not_qualified",
            "missing": [
                "licensed_mvdr_source_and_runtime",
                "mask_estimator_or_oracle_definition",
                "covariance_estimator_configuration",
                "measured_array_geometry_and_calibration",
                "rights_cleared_synchronized_array_corpus",
                "heldout_spatial_scoring",
                "opt_in_provider_intake",
                "independent_review",
            ],
        }
    parsed = parse_mvdr_plan(plan)
    return {
        "present": True,
        "status": "structurally_complete_not_executed",
        "executed": False,
        "qualification_status": "not_qualified",
        "plan_digest": object_digest(parsed),
        "missing": [
            "staged_licensed_source_asset",
            "staged_mask_model_or_oracle_mask",
            "measured_array_geometry_and_calibration",
            "rights_cleared_synchronized_array_corpus",
            "heldout_spatial_scoring",
            "independent_review",
        ],
    }


def _structure_sample_plan() -> Dict[str, Any]:
    """Validator-only structural sample.  Never executed or reported."""
    return {
        "schema_id": PLAN_SCHEMA,
        "source_id": "s24",
        "source_url": "https://example.invalid/validator-sample",
        "source_revision": "0" * 40,
        "source_sha256": "0" * 64,
        "license_grant": "validator-sample-not-a-grant",
        "runtime": "validator-sample-runtime",
        "adapter_id": "validator-sample-adapter",
        "array_geometry_digest": "0" * 64,
        "reference_mic_id": "m0",
        "mask_group": "oracle",
        "covariance": {
            "estimator": "validator-sample-covariance",
            "diagonal_loading_q16": 1,
            "smoothing_frames": 1,
            "rank": 1,
        },
        "delay_and_sum_baseline_id": "delay-and-sum-equal-weight-control-v1",
    }


def _reject_code(function: Any) -> str:
    try:
        function()
    except Reject as error:
        return error.code
    return "accepted"


def _adverse_cases() -> List[Tuple[str, str, Any]]:
    geometry = fixture_geometry()
    mask = fixture_mask_manifest()
    plan = _structure_sample_plan()

    def mutate_geometry(mutator: Any) -> Any:
        document = json.loads(canonical_text(geometry))
        mutator(document)
        return lambda: parse_geometry(document)

    def mutate_mask(mutator: Any) -> Any:
        document = json.loads(canonical_text(mask))
        mutator(document)
        return lambda: parse_mask_manifest(document)

    def mutate_plan(mutator: Any) -> Any:
        document = json.loads(canonical_text(plan))
        mutator(document)
        return lambda: parse_mvdr_plan(document)

    def duplicate_position(document: Dict[str, Any]) -> None:
        document["microphones"][1]["position_nm"] = [0, 0, 0]

    def duplicate_id(document: Dict[str, Any]) -> None:
        document["microphones"][1]["id"] = "m0"

    def unknown_reference(document: Dict[str, Any]) -> None:
        document["reference_mic_id"] = "m9"

    def non_integer_position(document: Dict[str, Any]) -> None:
        document["microphones"][1]["position_nm"] = [1, 0, 0.5]

    def out_of_range_position(document: Dict[str, Any]) -> None:
        document["microphones"][1]["position_nm"] = [MAX_POSITION_NM + 1, 0, 0]

    def bad_direction(document: Dict[str, Any]) -> None:
        document["steering_direction"] = [1, 1, 0]

    def zero_direction(document: Dict[str, Any]) -> None:
        document["steering_direction"] = [0, 0, 0]

    def bad_rate(document: Dict[str, Any]) -> None:
        document["sample_rate_hz"] = 48000

    def bad_speed(document: Dict[str, Any]) -> None:
        document["speed_of_sound_nm_per_ns"] = 340

    def too_few_mics(document: Dict[str, Any]) -> None:
        document["microphones"] = document["microphones"][:1]
        document["channels"] = document["channels"][:1]

    def too_many_mics(document: Dict[str, Any]) -> None:
        document["microphones"] = [
            {"id": f"x{index}", "position_nm": [index + 1, 0, 0]}
            for index in range(MAX_MICS + 1)
        ]
        document["channels"] = [
            {"mic_id": f"x{index}", "clock_ppm": 0,
             "calibration_gain_q16": UNITY_GAIN_Q16}
            for index in range(MAX_MICS + 1)
        ]
        document["reference_mic_id"] = "x0"

    def extra_field(document: Dict[str, Any]) -> None:
        document["room"] = "none"

    def missing_channel(document: Dict[str, Any]) -> None:
        document["channels"] = document["channels"][:3]

    def duplicate_channel(document: Dict[str, Any]) -> None:
        document["channels"][1] = document["channels"][0]

    def unknown_channel(document: Dict[str, Any]) -> None:
        document["channels"][1]["mic_id"] = "m9"

    def drift(document: Dict[str, Any]) -> None:
        document["channels"][1]["clock_ppm"] = 5

    def uncalibrated(document: Dict[str, Any]) -> None:
        document["channels"][1]["calibration_gain_q16"] = UNITY_GAIN_Q16 - 1

    def bad_calibration_type(document: Dict[str, Any]) -> None:
        document["channels"][1]["calibration_gain_q16"] = "65536"

    def fractional_steering() -> None:
        document = fixture_geometry()
        document["microphones"][1]["position_nm"] = [1000, 0, 0]
        document["microphones"][2]["position_nm"] = [0, 1, 0]
        document["microphones"][3]["position_nm"] = [1, 1, 0]
        document["steering_direction"] = [1, 0, 0]
        parsed = parse_geometry(document)
        delays = steering_delays(parsed)
        _require(all(item["exact_integer_sample"] for item in delays),
                 "fractional_steering_not_exact")

    def nonfinite_sample() -> None:
        validate_channels([[0, 0, float("inf")] + [0] * (FRAME_SAMPLES - 3)]
                          * 2, 2)

    def invalid_sample_type() -> None:
        validate_channels([[0, 0, "0"] + [0] * (FRAME_SAMPLES - 3)] * 2, 2)

    def length_mismatch() -> None:
        validate_channels([[0] * (FRAME_SAMPLES - 1)] * 2, 2)

    def empty_channel() -> None:
        validate_channels([[]] * 2, 2)

    def oversized_sample() -> None:
        validate_channels([[0, 0, MAX_ABS_SAMPLE + 1]
                           + [0] * (FRAME_SAMPLES - 3)] * 2, 2)

    def bad_click() -> None:
        document = fixture_geometry()
        document["steering_direction"] = [1, 0, 0]
        document["microphones"][1]["position_nm"] = [-3_087_000_000, 0, 0]
        parsed = parse_geometry(document)
        synthetic_channels(parsed, steering_delays(parsed))

    def mask_negative(document: Dict[str, Any]) -> None:
        document["values"][0][0] = -0.1

    def mask_above_one(document: Dict[str, Any]) -> None:
        document["values"][0][0] = 1.5

    def mask_nonfinite(document: Dict[str, Any]) -> None:
        document["values"][0][0] = float("inf")

    def mask_frame_shape(document: Dict[str, Any]) -> None:
        document["values"] = document["values"][:1]

    def mask_bin_shape(document: Dict[str, Any]) -> None:
        document["values"][0] = document["values"][0][:2]

    def mask_mixed_group(document: Dict[str, Any]) -> None:
        document["mask_group"] = "oracle+estimated"

    def mask_extra_field(document: Dict[str, Any]) -> None:
        document["mask_oracle"] = True

    def plan_missing_revision(document: Dict[str, Any]) -> None:
        document["source_revision"] = None

    def plan_bad_digest(document: Dict[str, Any]) -> None:
        document["source_sha256"] = "z" * 64

    def plan_mixed_group(document: Dict[str, Any]) -> None:
        document["mask_group"] = "mixed"

    def plan_bad_rank(document: Dict[str, Any]) -> None:
        document["covariance"]["rank"] = 0

    def plan_extra_field(document: Dict[str, Any]) -> None:
        document["oracle_steering"] = True

    def duplicate_json() -> None:
        parse_strict_json('{"a":1,"a":2}')

    def nonfinite_json() -> None:
        parse_strict_json('{"a":NaN}')

    def invalid_json() -> None:
        parse_strict_json('{"a":}')

    return [
        ("duplicate_mic_position", "duplicate_mic_position",
         mutate_geometry(duplicate_position)),
        ("duplicate_mic_id", "duplicate_mic_id", mutate_geometry(duplicate_id)),
        ("unknown_reference_mic", "unknown_reference_mic",
         mutate_geometry(unknown_reference)),
        ("non_integer_position", "invalid_position",
         mutate_geometry(non_integer_position)),
        ("position_out_of_range", "invalid_position",
         mutate_geometry(out_of_range_position)),
        ("steering_direction_not_exactly_normalizable",
         "steering_direction_not_exactly_normalizable",
         mutate_geometry(bad_direction)),
        ("zero_steering_direction", "zero_steering_direction",
         mutate_geometry(zero_direction)),
        ("unsupported_sample_rate", "unsupported_sample_rate",
         mutate_geometry(bad_rate)),
        ("unsupported_speed_of_sound", "unsupported_speed_of_sound",
         mutate_geometry(bad_speed)),
        ("too_few_microphones", "invalid_microphone_count",
         mutate_geometry(too_few_mics)),
        ("too_many_microphones", "invalid_microphone_count",
         mutate_geometry(too_many_mics)),
        ("extra_geometry_field", "invalid_geometry_fields",
         mutate_geometry(extra_field)),
        ("missing_channel", "channel_count_mismatch",
         mutate_geometry(missing_channel)),
        ("duplicate_channel_mic", "duplicate_channel_mic",
         mutate_geometry(duplicate_channel)),
        ("unknown_channel_mic", "unknown_channel_mic",
         mutate_geometry(unknown_channel)),
        ("clock_drift_not_supported", "clock_drift_not_supported",
         mutate_geometry(drift)),
        ("uncalibrated_channel_not_supported",
         "uncalibrated_channel_not_supported", mutate_geometry(uncalibrated)),
        ("invalid_channel_calibration", "invalid_channel_calibration",
         mutate_geometry(bad_calibration_type)),
        ("fractional_steering_not_exact", "fractional_steering_not_exact",
         fractional_steering),
        ("nonfinite_sample", "nonfinite_sample", nonfinite_sample),
        ("invalid_sample_type", "invalid_sample_type", invalid_sample_type),
        ("channel_length_mismatch", "channel_length_mismatch",
         length_mismatch),
        ("empty_channel", "invalid_channel_length", empty_channel),
        ("oversized_sample", "nonfinite_sample", oversized_sample),
        ("click_out_of_range", "click_out_of_range", bad_click),
        ("invalid_mask_value_negative", "invalid_mask_value",
         mutate_mask(mask_negative)),
        ("invalid_mask_value_above_one", "invalid_mask_value",
         mutate_mask(mask_above_one)),
        ("nonfinite_mask_value", "nonfinite_mask_value",
         mutate_mask(mask_nonfinite)),
        ("mask_frame_shape_mismatch", "mask_shape_mismatch",
         mutate_mask(mask_frame_shape)),
        ("mask_bin_shape_mismatch", "mask_shape_mismatch",
         mutate_mask(mask_bin_shape)),
        ("mixed_mask_group_not_permitted", "mixed_mask_group_not_permitted",
         mutate_mask(mask_mixed_group)),
        ("mask_extra_field", "invalid_mask_fields",
         mutate_mask(mask_extra_field)),
        ("plan_missing_source_revision", "invalid_plan_source_revision",
         mutate_plan(plan_missing_revision)),
        ("plan_invalid_source_digest", "invalid_plan_source_digest",
         mutate_plan(plan_bad_digest)),
        ("plan_mixed_mask_group", "invalid_plan_mask_group",
         mutate_plan(plan_mixed_group)),
        ("plan_invalid_covariance_rank", "invalid_plan_rank",
         mutate_plan(plan_bad_rank)),
        ("plan_extra_field", "invalid_plan_fields",
         mutate_plan(plan_extra_field)),
        ("duplicate_json_key", "duplicate_json_key:a", duplicate_json),
        ("nonfinite_json_constant", "nonfinite_json_constant:NaN",
         nonfinite_json),
        ("invalid_json", "invalid_json", invalid_json),
    ]


def adverse_rejections() -> List[Dict[str, Any]]:
    """Run every bounded rejection with an unchanged fixture state."""
    before = build_fixture()["fixture_digest"]
    records = []
    for case_id, expected, function in _adverse_cases():
        actual = _reject_code(function)
        _require(actual == expected, "adverse_code_mismatch:" + case_id)
        records.append({
            "case_id": case_id,
            "status": "rejected",
            "code": actual,
            "state_unchanged": True,
        })
    after = build_fixture()["fixture_digest"]
    _require(before == after, "adverse_state_mutation")
    return records


def required_prerequisites() -> List[Dict[str, str]]:
    return [
        {
            "id": "licensed_mvdr_source_and_runtime",
            "requirement": "Pin one exact licensed MVDR/MPDR implementation or runtime with an immutable revision, archive/source identity, verified licence grant and declared adapter settings.",
            "state": "S24 and S25 are documentation/search excerpts only. No source tree, package, archive, executable, runtime, adapter or numeric output is staged; nothing was downloaded or vendored.",
        },
        {
            "id": "mask_estimator_or_oracle_definition",
            "requirement": "Supply the exact mask estimator checkpoint or an oracle-mask definition with frame/bin geometry, timing mode and group labelling kept separate.",
            "state": "Only a structural mask manifest is validated. No mask model, checkpoint, oracle mask or mask-quality result exists.",
        },
        {
            "id": "covariance_estimator_configuration",
            "requirement": "Pin the covariance estimator, diagonal loading, smoothing window, rank truncation and steering vector source exactly.",
            "state": "No covariance estimator is implemented or executed; the plan schema records the required fields but no plan is present.",
        },
        {
            "id": "measured_geometry_and_calibration",
            "requirement": "Supply measured microphone positions, orientation, per-channel gain calibration and a declared reference channel for the intended array.",
            "state": "This package declares one frozen integer synthetic geometry with unity-gain synchronous channels only.",
        },
        {
            "id": "rights_cleared_synchronized_array_corpus",
            "requirement": "Supply a rights-cleared synchronized real multichannel recording with consent/usage grant, target/reference conditions, movement and channel-loss strata.",
            "state": "No multichannel array recording, consent grant or condition label is staged. Adjacent synthetic two-channel WPE fixtures are not beamforming evidence.",
        },
        {
            "id": "device_synchronization_and_timing",
            "requirement": "Measure channel synchronization, clock offset/drift, calibration mismatch and target-device timing boundaries.",
            "state": "Synchronous channels are required and nonzero clock_ppm is rejected. No device clock, drift or deadline/RTF was measured.",
        },
        {
            "id": "task_matched_heldout_spatial_scoring",
            "requirement": "Supply held-out localization/activity/extraction labels plus leakage, target-damage, channel-loss and room/reference-change scoring with independent review.",
            "state": "No real target or interference stratum, held-out label set, scorer or benchmark result exists.",
        },
        {
            "id": "provider_intake_and_independent_review",
            "requirement": "Complete opt-in provider intake, descriptor/config review and independent exact-head review before any registration, default or release decision.",
            "state": "No descriptor, registration, default, ABI, shared build or CI change is made. RG-07 and RG-08 remain blocked.",
        },
    ]


def release_gates() -> List[Dict[str, str]]:
    return [
        {
            "id": "RG-01",
            "requirement": "Exact licensed MVDR/MPDR source or runtime with an immutable revision, archive/source identity, verified rights and declared adapter settings.",
            "status": "blocked",
        },
        {
            "id": "RG-02",
            "requirement": "Exact mask estimator or oracle-mask definition plus pinned covariance estimator, diagonal loading, smoothing and rank configuration.",
            "status": "blocked",
        },
        {
            "id": "RG-03",
            "requirement": "Measured array geometry, layout, orientation, per-channel calibration and a declared reference channel supplied by the intended device.",
            "status": "blocked",
        },
        {
            "id": "RG-04",
            "requirement": "Rights-cleared synchronized real multichannel corpus with consent/usage grant, target/reference conditions, movement and channel-loss strata.",
            "status": "blocked",
        },
        {
            "id": "RG-05",
            "requirement": "Exact-runtime parity with the pinned MVDR source on the frozen synthetic fixture, including mask shape/range rejection and reference timing.",
            "status": "blocked",
        },
        {
            "id": "RG-06",
            "requirement": "Measured channel synchronization, clock offset/drift, calibration mismatch, channel dropout and target-device timing within declared bounds.",
            "status": "blocked",
        },
        {
            "id": "RG-07",
            "requirement": "Task-matched held-out spatial scoring including distortion against the delay-and-sum control, leakage, target damage, channel loss and room/reference-change strata.",
            "status": "blocked",
        },
        {
            "id": "RG-08",
            "requirement": "Opt-in provider intake, descriptor/config review, independent exact-head review and explicit release approval; DEFER remains in force until RG-01 through RG-07 close.",
            "status": "blocked",
        },
    ]


def exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "licensed_source_or_runtime_absent",
            "requirement": "Pin one exact licensed MVDR/MPDR implementation or runtime with an immutable revision, archive/source identity and declared adapter settings.",
            "state": "The catalogued leads S24 (Pyroomacoustics beamforming) and S25 (TorchAudio mask-based MVDR tutorial) are search excerpts only. No source tree, package, archive, executable, licence grant, adapter or numeric output is staged; nothing was downloaded or vendored.",
        },
        {
            "id": "mask_and_covariance_configuration_absent",
            "requirement": "Supply the exact mask estimator or oracle-mask definition and pin covariance estimator, diagonal loading, smoothing, rank truncation and steering vector source.",
            "state": "Only structural validation exists. No mask model, checkpoint, oracle mask, covariance estimate or MVDR beamformer execution exists in this package.",
        },
        {
            "id": "rights_cleared_synchronized_array_corpus_absent",
            "requirement": "Supply a rights-cleared synchronized real multichannel recording with consent/usage grant, target/reference conditions, movement and channel-loss strata.",
            "state": "Only adjacent synthetic two-channel WPE fixtures and mono listening files exist in the pinned workspace. No multichannel array recording, consent grant or condition label is staged.",
        },
        {
            "id": "measured_geometry_and_calibration_absent",
            "requirement": "Supply measured microphone positions, orientation, per-channel gain calibration and a declared reference channel for the intended array.",
            "state": "This package declares one frozen integer synthetic geometry and unity-gain channels only. No measured layout, calibration file or device reference channel exists.",
        },
        {
            "id": "device_synchronization_and_timing_absent",
            "requirement": "Measure channel synchronization, clock offset/drift, calibration mismatch and target-device timing boundaries.",
            "state": "Synchronous channels are required and nonzero clock_ppm is rejected. No device clock, drift, capture timestamp or deadline/RTF result was measured.",
        },
        {
            "id": "task_matched_heldout_spatial_scoring_absent",
            "requirement": "Supply held-out spatial labels plus distortion, leakage, target-damage, channel-loss and room/reference-change scoring against the delay-and-sum control.",
            "state": "No real target or interference stratum, held-out label set, scorer, listening test or benchmark result exists. The frozen synthetic fixture cannot qualify any spatial claim.",
        },
        {
            "id": "provider_intake_and_independent_review_absent",
            "requirement": "Complete opt-in provider intake, descriptor/config review and independent exact-head review before any registration, default or release decision.",
            "state": "No descriptor, registration, default, ABI, shared build or CI change is made. RG-08 remains blocked.",
        },
    ]


def board_row() -> Dict[str, Any]:
    """Read only the stable linked-row identity; never hash the full board."""
    payload = load_strict_json(SOURCE_ROOT / TASK_BOARD)
    _require(isinstance(payload, dict) and isinstance(payload.get("tasks"), list),
             "invalid_task_board")
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
    return {
        "stable_fields": stable_fields,
        "stable_sha256": object_digest(stable_fields),
        "full_tasks_json_hashed": False,
        "note": "Only the stable linked-row identity is gated. The mutable full plan/swarm/TASKS.json is never hashed into, or pinned by, this package.",
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


def spatial_profile() -> Dict[str, Any]:
    return {
        "profile": "spatial",
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "geometry_and_layout": {
                "status": "declared_synthetic_only",
                "evidence": "One frozen 4-microphone planar geometry in integer nanometres with an exactly normalizable steering direction and a declared reference channel m0; no measured array, orientation or device layout.",
            },
            "timestamp_calibration": {
                "status": "declared_synthetic_only",
                "evidence": "Synchronous channels only: clock_ppm must be zero and calibration_gain_q16 must be unity. Exact 62,500 ns sample period; no device clock was measured.",
            },
            "source_target_reference_conditions_and_permissions": {
                "status": "blocked",
                "evidence": "No real recording, target/reference condition, consent or usage permission is staged.",
            },
            "task_matched_heldout_localization_activity_extraction": {
                "status": "blocked",
                "evidence": "No held-out array labels, localization/activity/extraction output or scorer exists; no MVDR output exists.",
            },
            "leakage_target_damage_channel_loss": {
                "status": "blocked",
                "evidence": "No real target, interference, leakage or channel-loss stratum exists; the delay-and-sum control is not an MVDR comparison.",
            },
            "room_reference_changes": {
                "status": "blocked",
                "evidence": "No room, RIR or reference-condition change is measured; adjacent WPE fixtures are not pooled into any MVDR result.",
            },
        },
        "mvdr_specific_items": {
            "mask_validity": {
                "status": "blocked",
                "evidence": "A structural mask manifest is validated for shape, group, range, finiteness and timing mode, but no mask model, checkpoint or mask-quality result exists, and no mask is applied to a beamformer.",
            },
            "reference_timing": {
                "status": "declared_synthetic_only",
                "evidence": "Exact rational plane-wave delays relative to m0 with integral 16 kHz sample offsets; no measured device reference timing.",
            },
            "channel_calibration": {
                "status": "declared_synthetic_only",
                "evidence": "Unity-gain synchronous channels only; non-unity calibration and clock drift are rejected.",
            },
            "distortion_against_delay_and_sum": {
                "status": "blocked",
                "evidence": "The frozen delay-and-sum control exists, but no MVDR output exists, so no distortion comparison can be computed.",
            },
        },
        "mapped_cases": {
            "frozen_synthetic_fixture": "one 160-sample planar 4-microphone fixture with exact integer steering delays and a matching exact delay-and-sum control",
            "mask_structure_validation": "declared 2x3 oracle mask validated structurally only; never applied",
            "plan_structure_validation": "MVDR plan schema validated structurally only; no plan is present in this package",
            "missing_licensed_runtime": "explicit blocked state with no output; never promoted",
            "missing_or_delayed_reference": "explicit rejection/missing evidence only; no real delayed-reference recording",
        },
        "not_applicable": [
            "echo attenuation, near-end damage, listening quality and benchmark scoring",
            "localization, tracking, neural mask estimation, separation, target extraction and neural beamforming",
        ],
    }


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report.  No files are written."""
    _verify_pins()

    built = build_fixture()
    geometry = built["fixture"]["geometry"]
    delays = built["fixture"]["steering_delays"]
    channels = built["fixture"]["channels"]
    control = built["control"]

    # Re-derive the control from the frozen bytes to prove side-effect freedom.
    rebuilt_control = delay_and_sum_control(geometry, delays, channels)
    _require(canonical_text(rebuilt_control) == canonical_text(control),
             "control_not_reproducible")
    _require(control["is_mvdr"] is False, "control_claims_mvdr")
    _require(control["mask_applied"] is False and control["covariance_used"] is False,
             "control_claims_mask_or_covariance")
    _require(control["status"] == "control_only_not_qualified",
             "control_status_promoted")
    _require(control["qualification_status"] == "not_qualified",
             "control_qualification_promoted")

    mask = fixture_mask_manifest()
    plan = plan_readiness(None)
    _require(plan["present"] is False and plan["executed"] is False,
             "mvdr_plan_present_but_unexecuted_contract")
    _require(plan["qualification_status"] == "not_qualified",
             "mvdr_plan_qualified")
    _require(plan["status"] == "blocked", "mvdr_plan_not_blocked")

    adverse = adverse_rejections()

    core = {
        "fixture_digest": built["fixture_digest"],
        "geometry_digest": built["geometry_digest"],
        "control_digest": control["output_digest"],
        "mask_digest": object_digest(mask),
        "adverse_digest": object_digest(adverse),
        "plan_digest": object_digest(plan),
    }
    core_digest = object_digest(core)
    repeat_digests = []
    for _ in range(3):
        again = build_fixture()
        repeat_digests.append(object_digest({
            "fixture_digest": again["fixture_digest"],
            "geometry_digest": again["geometry_digest"],
            "control_digest": again["control"]["output_digest"],
            "mask_digest": object_digest(fixture_mask_manifest()),
            "adverse_digest": object_digest(adverse_rejections()),
            "plan_digest": object_digest(plan_readiness(None)),
        }))
    repeat_digests.append(core_digest)
    _require(len(set(repeat_digests)) == 1, "core_digest_not_repeatable")

    report = {
        "schema_id": REPORT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_incomplete",
        "evidence_status": "incomplete",
        "decision": "DEFER",
        "defer_before": "opt_in_adapter_exposure",
        "verification_profile": "spatial",
        "scope": (
            "Task-local blocker record plus strict structural validation and "
            "one frozen synthetic fixture with an exact equal-weight "
            "delay-and-sum control. No licensed source, MVDR execution, mask "
            "model, covariance estimate, real array recording, runtime, "
            "device calibration, listening, benchmark or release result is "
            "present."
        ),
        "acceptance_profile": spatial_profile(),
        "format": {
            "installed_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "installed_v0_channels": 1,
            "installed_v0_frame_samples": FRAME_SAMPLES,
            "installed_v0_sample_format": "f32",
            "installed_v0_geometry_unchanged": True,
            "model_sample_rate_hz": SAMPLE_RATE_HZ,
            "model_channels_min": MIN_MICS,
            "model_channels_max": MAX_MICS,
            "model_frame_samples": FRAME_SAMPLES,
            "sample_period_ns": SAMPLE_PERIOD_NS,
            "speed_of_sound_nm_per_ns": SPEED_OF_SOUND_NM_PER_NS,
            "position_unit": "integer_nanometre",
            "steering_unit": "exact_rational_q16_sample",
            "added_content_delay_samples": 0,
            "clock_drift_supported": False,
            "per_channel_calibration": "unity_only",
        },
        "reference": {
            "reference_id": "mvdr-fixture-and-validation-only-v1",
            "reference_kind": "author_written_fixture_and_validator_not_mvdr",
            "catalogued_leads": ["S24", "S25"],
            "mvdr_implemented": False,
            "mvdr_executed": False,
            "mask_applied": False,
            "covariance_estimated": False,
            "model_weights": False,
            "downloads": False,
            "real_speech": False,
            "licensed_runtime": False,
            "catalogued_candidate_executed": False,
            "device_or_timing_claim": False,
            "registered": False,
            "default_enabled": False,
        },
        "candidate_execution": {
            "status": "blocked",
            "present": False,
            "executed": False,
            "result": None,
            "requirement": "Pin one exact licensed MVDR/MPDR source or runtime with immutable revision, archive identity, rights, mask/covariance configuration and adapter settings.",
            "observed_evidence": (
                "S24 (Pyroomacoustics beamforming implementation) and S25 "
                "(TorchAudio mask-based MVDR example) are search excerpts in "
                "research/category_registry.json. No source tree, package, "
                "archive, executable, licence grant, adapter, mask model or "
                "numeric output is staged in this workspace."
            ),
        },
        "mvdr_plan": plan,
        "mask_manifest": {
            "status": "structure_only_not_qualified",
            "qualification_status": "not_qualified",
            "present": True,
            "applied_to_beamformer": False,
            "quality_result": False,
            "manifest": mask,
            "manifest_digest": object_digest(mask),
            "note": "Shape/range/group/finiteness/timing validation only. No mask is applied and no mask-quality claim is made.",
        },
        "fixture": {
            "schema_id": built["fixture"]["schema_id"],
            "fixture_id": built["fixture"]["fixture_id"],
            "fixture_digest": built["fixture_digest"],
            "geometry_digest": built["geometry_digest"],
            "geometry": geometry,
            "steering_delays": delays,
            "click_index": built["fixture"]["click_index"],
            "click_amplitude": built["fixture"]["click_amplitude"],
            "interference_rule": built["fixture"]["interference_rule"],
            "frame_samples": FRAME_SAMPLES,
            "channels": channels,
            "status": "synthetic_declared_not_measured",
            "qualification_status": "not_qualified",
        },
        "delay_and_sum_control": {
            "case_id": "frozen_planar_4mic_delay_and_sum_control",
            "role": "distortion_reference_control_only",
            "is_catalogued_candidate": False,
            "control": control,
            "fixture_digest": built["fixture_digest"],
        },
        "distortion_comparison": {
            "status": "blocked",
            "mvdr_output_present": False,
            "delay_and_sum_control_present": True,
            "metric": None,
            "value": None,
            "reason": "no_licensed_mvdr_output_to_compare_against_the_frozen_delay_and_sum_control",
            "qualification_status": "not_qualified",
        },
        "adverse_rejections": adverse,
        "adverse_all_rejected": True,
        "adverse_case_count": len(adverse),
        "qualification": {
            "status": "not_qualified",
            "decision": "DEFER",
            "evidence_status": "incomplete",
            "proposal_only": True,
            "qualifies": False,
            "all_required_results_present": False,
            "missing_result_promoted": False,
            "catalogued_candidate_executed": False,
            "mvdr_output_present": False,
            "mask_quality_measured": False,
            "real_recording_evidence": False,
            "exact_runtime_parity": False,
            "device_timing": False,
            "heldout_scoring": False,
            "provider_intake": False,
        },
        "required_prerequisites": required_prerequisites(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "boundary": {
            "provider_registration": False,
            "descriptor_registry_change": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "default_selected": False,
            "enabled_by_default": False,
            "processor_exposure": False,
            "shared_build_or_ci_change": False,
            "sdk_data_dir_added": False,
            "asset_bundled": False,
            "weights_vendored": False,
            "board_or_handoff_changed": False,
        },
        "board_row": board_row(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "repeatability": {
            "runs": 3,
            "core_digest": core_digest,
            "core_digests": repeat_digests[:3],
            "byte_identical": True,
            "comparison": "exact SHA-256 over canonical core JSON; no tolerance",
        },
        "negative_claims": [
            "No exact licensed MVDR/MPDR source, runtime, mask model, covariance estimator, weight or device was used.",
            "No MVDR beamformed output, mask-quality result, distortion comparison or real multichannel recording exists.",
            "The delay-and-sum control is an author-written control reference, is not the catalogued candidate and cannot qualify MVDR.",
            "No localization, tracking, separation, target extraction, leakage, target-damage, listening, benchmark or release result is claimed.",
            "No provider registration, descriptor, registry, installed v0 default, ABI, shared build or CI was changed.",
        ],
        "reopen_condition": (
            "Supply a rights-cleared synchronized real multichannel corpus with "
            "measured geometry/calibration and a declared reference channel; "
            "pin one exact licensed MVDR/MPDR source or runtime with immutable "
            "revision, rights, mask/oracle definition and covariance "
            "configuration; reproduce exact-runtime parity on the frozen "
            "synthetic fixture; compute distortion against the delay-and-sum "
            "control; measure device synchronization and drift; score "
            "task-matched held-out spatial conditions with leakage, target "
            "damage and channel loss; complete opt-in provider intake and "
            "independent review before RG-08."
        ),
    }
    return report


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


def artifact_pins() -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in ARTIFACT_FILES:
        path = HERE / name
        _require(path.is_file(), "missing_artifact:" + name)
        pins[TASK_PREFIX + name] = file_digest(path)
    return pins


def build_contract() -> Dict[str, Any]:
    """Build contract.json after report.json, its sidecar and README exist."""
    pins = artifact_pins()
    gates = release_gates()
    blockers = exact_blockers()
    stable = board_row()
    return {
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_incomplete",
        "evidence_status": "incomplete",
        "decision": "DEFER",
        "defer_before": "opt_in_adapter_exposure",
        "qualification_status": "not_qualified",
        "verification_profile": "spatial",
        "scope": {
            "benchmark_claim": False,
            "device_timing": False,
            "distortion_comparison": False,
            "listening": False,
            "mask_quality_claim": False,
            "mvdr_execution": False,
            "network_access": False,
            "numeric_parity_claim": False,
            "processor_exposure": False,
            "public_default": False,
            "real_array_audio": False,
            "real_corpus": False,
            "real_speech": False,
            "release_claim": False,
            "runtime_invocation": False,
            "synthetic_only": True,
            "task_local_only": True,
            "weights": False,
        },
        "format": {
            "installed_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "installed_v0_channels": 1,
            "installed_v0_frame_samples": FRAME_SAMPLES,
            "installed_v0_geometry_preserved": True,
            "model_sample_rate_hz": SAMPLE_RATE_HZ,
            "model_channels_min": MIN_MICS,
            "model_channels_max": MAX_MICS,
            "model_frame_samples": FRAME_SAMPLES,
            "sample_period_ns": SAMPLE_PERIOD_NS,
            "speed_of_sound_nm_per_ns": SPEED_OF_SOUND_NM_PER_NS,
            "position_unit": "integer_nanometre",
            "added_content_delay_samples": 0,
        },
        "public_boundary": {
            "header": "api/include/audio_sdk/provider_v0.h",
            "session_header": "api/include/audio_sdk/session_v0.h",
            "abi_major": 0,
            "abi_minor": 1,
            "registration": "none; no provider, descriptor, registry entry or installed default is added",
            "c_provider_added": False,
            "public_api_abi_changed": False,
            "installed_v0_behavior_changed": False,
            "shared_build_or_ci_changed": False,
        },
        "reference": {
            "reference_id": "mvdr-fixture-and-validation-only-v1",
            "reference_kind": "author_written_fixture_and_validator_not_mvdr",
            "catalogued_leads": ["S24", "S25"],
            "mvdr_implemented": False,
            "mvdr_executed": False,
            "mask_applied": False,
            "covariance_estimated": False,
            "model_weights": False,
            "downloads": False,
            "catalogued_candidate_executed": False,
            "device_or_timing_claim": False,
            "registered": False,
            "default_enabled": False,
        },
        "board_row": stable,
        "required_prerequisites": required_prerequisites(),
        "exact_blockers": blockers,
        "release_gates": gates,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": pins,
        "negative_claims": [
            "No licensed MVDR source, runtime, mask model, covariance estimator, weight, corpus, real recording or device was used.",
            "No MVDR output, mask-quality, distortion, localization, leakage or release result exists.",
            "No provider registration, installed v0, ABI, registry, default, shared build or CI change exists.",
        ],
        "reopen_condition": (
            "Close RG-01 through RG-08 with a rights-cleared real array "
            "corpus, a pinned licensed MVDR/MPDR source or runtime, exact "
            "mask/covariance configuration, exact-runtime parity on the frozen "
            "fixture, distortion against the delay-and-sum control, measured "
            "device synchronization and calibration, held-out spatial scoring "
            "and independent opt-in provider review."
        ),
    }


def sources_bytes() -> bytes:
    """Regenerate SOURCES.sha256 bytes from hard pins plus live artifacts."""
    for path, expected in SOURCE_PINS.items():
        full = SOURCE_ROOT / path
        _require(full.is_file(), "missing_source_pin:" + path)
        _require(file_digest(full) == expected, "stale_source_pin:" + path)
    for path, expected in BOUNDARY_PINS.items():
        full = SDK_ROOT / path
        _require(full.is_file(), "missing_boundary_pin:" + path)
        _require(file_digest(full) == expected, "stale_boundary_pin:" + path)
    for name in PIN_FILES:
        _require((HERE / name).is_file(), "missing_artifact:" + name)

    lines = [
        "# SHA-256 pins for " + TASK_ID
        + "; source: paths are workspace-relative, others SDK-worktree-relative."
    ]
    for path in SOURCE_FILES:
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in BOUNDARY_FILES:
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for name in PIN_FILES:
        lines.append(f"{file_digest(HERE / name)}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")
