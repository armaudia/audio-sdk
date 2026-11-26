# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local synthetic geometry and asynchronous-reference time-alignment model.

This module is a *bounded boundary surrogate* for
``SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT``.  It validates an explicit
integer 3-D array geometry, computes exact plane-wave time differences at
16 kHz and aligns deterministic synthetic channels given explicit asynchronous
capture offsets.  It is **not** the catalogued candidate, contains no licensed
source, real array recording, runtime or device calibration, and can never
qualify the component.

Exact arithmetic
----------------

* Positions are integer nanometres.
* The pinned speed of sound is ``343 nm/ns`` (343 m/s).
* One 16 kHz sample is exactly ``62_500 ns`` (CONTRACTS.md timing record).
* A direction is an integer vector with an exactly integral norm, so the unit
  vector is exact and no floating-point trigonometry is used.
* Alignment is a fixed-point ``q16`` sample delay.  Integer delays are exact;
  a non-integral residual is applied with linear interpolation and is labelled
  a surrogate, never a qualified sub-sample result.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]

TASK_ID = "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT"
TITLE = "3D microphone spatial / time alignment"
COMPONENT = "3d-microphone-spatial-time-alignment"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT"
BASE_COMMIT = "0eec1f8f9fa420cbae18501583897f4b5faaaf2d"
TASK_PREFIX = "docs/task-evidence/3d-microphone-spatial-time-alignment/"
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SAMPLE_RATE_HZ = 16000
SAMPLE_PERIOD_NS = 62_500
FRAME_SAMPLES = 160
SPEED_OF_SOUND_NM_PER_NS = 343
Q16 = 65_536
MAX_MICS = 16
MAX_POSITION_NM = 10_000_000_000
MAX_CAPTURE_OFFSET_NS = 1_000_000_000
MAX_ABS_SAMPLE = 1_000_000.0
MAX_SAMPLES = 1_000_000
GEOMETRY_SCHEMA = "audio-sdk/array-geometry/0.1"
REPORT_SCHEMA = "audio-sdk/3d-microphone-spatial-time-alignment-report/0.1"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")

GEOMETRY_FIELDS = {
    "schema_id",
    "array_id",
    "sample_rate_hz",
    "speed_of_sound_nm_per_ns",
    "reference_mic_id",
    "microphones",
    "source_direction",
    "channels",
}
MIC_FIELDS = {"id", "position_nm"}
CHANNEL_FIELDS = {"mic_id", "capture_offset_ns", "clock_ppm"}

#: Stable read-only source pins, relative to the workspace root.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/category_survey/sources.md":
        "9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/pilot_source_research.md":
        "c9db16172ffaa1bcf8b5cc334d9401173528c31d1ec966176d6e99a0bbe52fe5",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md":
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b",
    "research/dereverberation_candidates_20261028.md":
        "6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468",
    "adapters/wpe/README.md":
        "b36f1af3151ea28df9b6c12f3adb90d0b4f28f4315d0aeccd0ff9c99050c703e",
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
    "docs/task-evidence/online-multichannel-wpe/README.md":
        "3615f6fc66d3c8d15a4cd77ccdc1f8a2e5f9c6cd9a1a20b9263814bfb2c34013",
    "docs/task-evidence/online-multichannel-wpe/report.json":
        "df76b6e78ab86bc21609d3a93d53bc175b9281962396cc3bf1acf8ea2d994e6f",
    "docs/task-evidence/offline-multichannel-wpe/README.md":
        "8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9",
    "docs/task-evidence/offline-multichannel-wpe/report.json":
        "4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba",
    "docs/task-evidence/duplex-clocks/README.md":
        "8e1a355bd36e561e8f1b634a5f5ec351e15d1785be8b6f4713bef33ec97e0325",
    "docs/task-evidence/duplex-clocks/contract.json":
        "c09f5a45862fda31039be5b7ebccff07be904c606d51a6f3accde9bea6f04cb4",
    "docs/task-evidence/coreaudio-audiounit-duplex-host/README.md":
        "5940548cc525820e09a39e608adc74f9ad18db53360c7adb5aa955c87e852b54",
    "docs/task-evidence/pipe-capture/README.md":
        "cbaa97236a3eeca4d3065a421fcc41100e4c6bea1692fd698aada6c8b68376a3",
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


def tensor_digest(values: Sequence[float]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(struct.pack("<d", float(value)))
    return digest.hexdigest()


def _as_int(value: Any, code: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject(code)
    if value < low or value > high:
        raise Reject(code)
    return value


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _as_id(value: Any, code: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise Reject(code)
    return value


def _as_triple(value: Any, code: str, bound: int) -> Tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise Reject(code)
    return tuple(_as_int(v, code, -bound, bound) for v in value)  # type: ignore[return-value]


def _direction(value: Any) -> Tuple[Tuple[int, int, int], int]:
    n = _as_triple(value, "invalid_direction", 1_000_000)
    if n == (0, 0, 0):
        raise Reject("zero_direction")
    norm_sq = n[0] * n[0] + n[1] * n[1] + n[2] * n[2]
    norm = math.isqrt(norm_sq)
    if norm * norm != norm_sq:
        raise Reject("direction_not_exactly_normalizable")
    return n, norm


def validate_geometry(geometry: Any) -> Dict[str, Any]:
    """Validate an explicit integer 3-D array geometry.

    Returns a normalized view carrying exact time-difference and asynchronous
    reference offsets.  The input object is never mutated.
    """
    _require(isinstance(geometry, dict), "geometry_not_object")
    _require(set(geometry) == GEOMETRY_FIELDS, "invalid_geometry_fields")
    _require(geometry["schema_id"] == GEOMETRY_SCHEMA, "unsupported_geometry_schema")
    array_id = _as_id(geometry["array_id"], "invalid_array_id")
    _require(_is_plain_int(geometry["sample_rate_hz"])
             and geometry["sample_rate_hz"] == SAMPLE_RATE_HZ,
             "unsupported_sample_rate")
    _require(_is_plain_int(geometry["speed_of_sound_nm_per_ns"])
             and geometry["speed_of_sound_nm_per_ns"] == SPEED_OF_SOUND_NM_PER_NS,
             "unsupported_speed_of_sound")

    microphones = geometry["microphones"]
    _require(isinstance(microphones, list), "microphones_not_array")
    _require(2 <= len(microphones) <= MAX_MICS, "invalid_microphone_count")

    mic_ids: List[str] = []
    positions: List[Tuple[int, int, int]] = []
    for entry in microphones:
        _require(isinstance(entry, dict) and set(entry) == MIC_FIELDS,
                 "invalid_microphone_fields")
        mic_ids.append(_as_id(entry["id"], "invalid_mic_id"))
        position = _as_triple(entry["position_nm"], "invalid_position", MAX_POSITION_NM)
        positions.append(position)
    _require(len(set(mic_ids)) == len(mic_ids), "duplicate_mic_id")
    _require(len(set(positions)) == len(positions), "duplicate_mic_position")
    position_map = dict(zip(mic_ids, positions))

    reference_id = _as_id(geometry["reference_mic_id"], "invalid_reference_mic_id")
    _require(reference_id in position_map, "unknown_reference_mic")
    reference_position = position_map[reference_id]

    direction, norm = _direction(geometry["source_direction"])

    channels = geometry["channels"]
    _require(isinstance(channels, list), "channels_not_array")
    _require(len(channels) == len(mic_ids), "channel_mic_set_mismatch")
    normalized_channels: List[Dict[str, Any]] = []
    seen: List[str] = []
    for entry in channels:
        _require(isinstance(entry, dict) and set(entry) == CHANNEL_FIELDS,
                 "invalid_channel_fields")
        mic_id = _as_id(entry["mic_id"], "invalid_channel_mic")
        _require(mic_id in position_map, "unknown_channel_mic")
        _require(mic_id not in seen, "duplicate_channel_mic")
        seen.append(mic_id)
        offset = _as_int(entry["capture_offset_ns"], "capture_offset_out_of_range",
                         -MAX_CAPTURE_OFFSET_NS, MAX_CAPTURE_OFFSET_NS)
        _require(_is_plain_int(entry["clock_ppm"]) and entry["clock_ppm"] == 0,
                 "clock_drift_not_supported")
        normalized_channels.append(
            {"mic_id": mic_id, "capture_offset_ns": offset, "clock_ppm": 0})
    _require(sorted(seen) == sorted(mic_ids), "channel_mic_set_mismatch")

    denominator = SPEED_OF_SOUND_NM_PER_NS * norm
    tdoa_ns: List[int] = []
    for mic_id in mic_ids:
        position = position_map[mic_id]
        dot = sum((position[axis] - reference_position[axis]) * direction[axis]
                  for axis in range(3))
        # Plane wave: delay relative to the reference is -(d . u) / c.
        tdoa_ns.append(-(dot // denominator))

    delta_ns = [tdoa_ns[index] - channel["capture_offset_ns"]
                for index, channel in enumerate(normalized_channels)]
    reference_index = mic_ids.index(reference_id)
    reference_delta = delta_ns[reference_index]
    relative_ns = [value - reference_delta for value in delta_ns]
    relative_q16 = [(value * Q16) // SAMPLE_PERIOD_NS for value in relative_ns]
    exact = all(value % SAMPLE_PERIOD_NS == 0 for value in relative_ns)

    return {
        "array_id": array_id,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "reference_mic_id": reference_id,
        "reference_index": reference_index,
        "mic_ids": mic_ids,
        "positions_nm": positions,
        "position_map": position_map,
        "direction": direction,
        "direction_norm": norm,
        "channels": normalized_channels,
        "tdoa_ns": tdoa_ns,
        "delta_ns": delta_ns,
        "relative_ns": relative_ns,
        "relative_q16": relative_q16,
        "exact_integer_alignment": exact,
    }


def _samples(values: Any) -> List[float]:
    _require(isinstance(values, list), "channel_samples_not_array")
    _require(1 <= len(values) <= MAX_SAMPLES, "invalid_channel_length")
    output: List[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise Reject("invalid_sample_type")
        try:
            finite = float(value)
        except (OverflowError, ValueError) as error:
            raise Reject("nonfinite_sample") from error
        if not math.isfinite(finite) or abs(finite) > MAX_ABS_SAMPLE:
            raise Reject("nonfinite_sample")
        output.append(finite)
    return output


def align_channels(geometry: Any, channels: Any) -> Dict[str, Any]:
    """Align synthetic channels to the reference microphone coordinate.

    ``channels[i]`` is the sample sequence for geometry channel ``i``.
    Output sample ``n`` reads channel ``i`` at ``n + relative_q16[i]/Q16``.
    Positions outside the channel are explicit zero padding.
    """
    normalized = validate_geometry(geometry)
    _require(isinstance(channels, list), "channels_not_array")
    _require(len(channels) == len(normalized["channels"]), "channel_count_mismatch")
    parsed = [_samples(channel) for channel in channels]
    lengths = {len(channel) for channel in parsed}
    _require(len(lengths) == 1, "channel_length_mismatch")
    length = lengths.pop()

    outputs: List[List[float]] = []
    leading_zeros: List[int] = []
    trailing_zeros: List[int] = []
    for index, channel in enumerate(parsed):
        shift = normalized["relative_q16"][index]
        output: List[float] = []
        first = length
        last = -1
        for sample_index in range(length):
            read_q16 = sample_index * Q16 + shift
            base = read_q16 // Q16
            fraction = read_q16 - base * Q16
            left = channel[base] if 0 <= base < length else 0.0
            right = channel[base + 1] if 0 <= base + 1 < length else 0.0
            value = (left * (Q16 - fraction) + right * fraction) / Q16
            output.append(value)
            if value != 0.0:
                first = min(first, sample_index)
                last = max(last, sample_index)
        outputs.append(output)
        leading_zeros.append(first if first != length else length)
        trailing_zeros.append(length - 1 - last if last >= 0 else length)

    return {
        "channel_count": len(outputs),
        "sample_count": length,
        "relative_ns": list(normalized["relative_ns"]),
        "relative_q16": list(normalized["relative_q16"]),
        "exact_integer_alignment": normalized["exact_integer_alignment"],
        "outputs": outputs,
        "leading_zeros": leading_zeros,
        "trailing_zeros": trailing_zeros,
        "output_digests": [tensor_digest(channel) for channel in outputs],
    }


def click_fixture(geometry: Any, length: int, source_time_ns: int,
                  amplitudes: Any) -> List[List[float]]:
    """Place a deterministic click in every channel at its declared arrival.

    The click is a linear-interpolation split for a non-integral arrival.  For
    the exact integer fixtures the split is a single sample with the declared
    amplitude.
    """
    normalized = validate_geometry(geometry)
    _require(isinstance(length, int) and not isinstance(length, bool),
             "invalid_length")
    _require(2 <= length <= MAX_SAMPLES, "invalid_length")
    _require(isinstance(source_time_ns, int) and not isinstance(source_time_ns, bool),
             "invalid_source_time")
    _require(isinstance(amplitudes, list)
             and len(amplitudes) == len(normalized["channels"]),
             "amplitude_count_mismatch")

    fixture: List[List[float]] = []
    for index, amplitude in enumerate(amplitudes):
        if isinstance(amplitude, bool) or not isinstance(amplitude, (int, float)):
            raise Reject("invalid_amplitude")
        value = float(amplitude)
        if not math.isfinite(value) or abs(value) > MAX_ABS_SAMPLE:
            raise Reject("nonfinite_amplitude")
        arrival_q16 = ((source_time_ns + normalized["delta_ns"][index]) * Q16) \
            // SAMPLE_PERIOD_NS
        _require(0 <= arrival_q16 <= (length - 1) * Q16, "click_out_of_range")
        base = arrival_q16 // Q16
        fraction = arrival_q16 - base * Q16
        samples = [0.0] * length
        samples[base] += value * (Q16 - fraction) / Q16
        if fraction and base + 1 < length:
            samples[base + 1] += value * fraction / Q16
        fixture.append(samples)
    return fixture


def peak(values: Sequence[float]) -> Dict[str, Any]:
    best_index = None
    best_value = 0.0
    best_abs = 0.0
    for index, value in enumerate(values):
        magnitude = abs(value)
        if magnitude > best_abs:
            best_abs = magnitude
            best_value = value
            best_index = index
    return {"index": best_index, "value": best_value, "abs": best_abs}


def _expected_reference_index(normalized: Dict[str, Any],
                              source_time_ns: int) -> int:
    value = ((source_time_ns + normalized["delta_ns"]
              [normalized["reference_index"]]) * Q16) // SAMPLE_PERIOD_NS
    _require(value % Q16 == 0, "non_integral_reference_arrival")
    return value // Q16


def _sample_strings(values: Sequence[int]) -> List[str]:
    return [str(value) for value in values]


def _geometry_record(normalized: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "array_id": normalized["array_id"],
        "sample_rate_hz": normalized["sample_rate_hz"],
        "mic_count": len(normalized["mic_ids"]),
        "mic_ids": normalized["mic_ids"],
        "positions_nm": [list(position) for position in normalized["positions_nm"]],
        "reference_mic_id": normalized["reference_mic_id"],
        "source_direction": list(normalized["direction"]),
        "direction_norm": normalized["direction_norm"],
        "capture_offsets_ns": [channel["capture_offset_ns"]
                               for channel in normalized["channels"]],
        "clock_ppm": [channel["clock_ppm"] for channel in normalized["channels"]],
        "tdoa_ns": normalized["tdoa_ns"],
        "relative_ns": normalized["relative_ns"],
        "relative_q16": normalized["relative_q16"],
        "exact_integer_alignment": normalized["exact_integer_alignment"],
    }


def _case_geometry(case: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_id": GEOMETRY_SCHEMA,
        "array_id": case.get("array_id", case["case_id"]),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "speed_of_sound_nm_per_ns": SPEED_OF_SOUND_NM_PER_NS,
        "reference_mic_id": "m0",
        "microphones": [
            {"id": mic_id, "position_nm": list(position)}
            for mic_id, position in zip(case["mic_ids"], case["positions_nm"])
        ],
        "source_direction": list(case["direction"]),
        "channels": [
            {"mic_id": mic_id, "capture_offset_ns": offset, "clock_ppm": 0}
            for mic_id, offset in zip(case["mic_ids"], case["capture_offsets_ns"])
        ],
    }


def cases() -> List[Dict[str, Any]]:
    """Frozen synthetic geometry / asynchronous-offset cases."""
    return [
        {
            "case_id": "linear_3mic_axis",
            "axis": "linear",
            "mic_ids": ["m0", "m1", "m2"],
            "positions_nm": [(0, 0, 0),
                             (21_437_500, 0, 0),
                             (42_875_000, 0, 0)],
            "direction": (1, 0, 0),
            "capture_offsets_ns": [0, 125_000, -62_500],
            "source_time_ns": 500_000,
            "length": 24,
            "amplitudes": [0.75, -0.5, 0.25],
        },
        {
            "case_id": "planar_4mic_pythagorean",
            "axis": "planar",
            "mic_ids": ["m0", "m1", "m2", "m3"],
            "positions_nm": [(0, 0, 0),
                             (34_300_000, 0, 0),
                             (0, 34_300_000, 0),
                             (17_150_000, 17_150_000, 0)],
            "direction": (3, 4, 0),
            "capture_offsets_ns": [0, 2_500, 45_000, 117_500],
            "source_time_ns": 1_000_000,
            "length": 32,
            "amplitudes": [1.0, -0.75, 0.5, -0.25],
        },
    ]


def fractional_case() -> Dict[str, Any]:
    """A declared half-sample case used only as a non-exact surrogate control."""
    return {
        "case_id": "fractional_half_sample_control",
        "axis": "linear",
        "mic_ids": ["m0", "m1", "m2"],
        "positions_nm": [(0, 0, 0),
                         (10_718_750, 0, 0),
                         (-10_718_750, 0, 0)],
        "direction": (1, 0, 0),
        "capture_offsets_ns": [0, 0, 0],
        "source_time_ns": 500_000,
        "length": 24,
        "amplitudes": [1.0, 0.6, -0.4],
    }


def _evaluate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    geometry = _case_geometry(case)
    normalized = validate_geometry(geometry)
    fixture = click_fixture(geometry, case["length"], case["source_time_ns"],
                            case["amplitudes"])
    aligned = align_channels(geometry, fixture)
    expected_index = _expected_reference_index(normalized, case["source_time_ns"])
    peaks = [peak(channel) for channel in aligned["outputs"]]
    max_error = 0.0
    for actual, expected in zip(peaks, case["amplitudes"]):
        max_error = max(max_error, abs(actual["value"] - expected))
    index_ok = all(item["index"] == expected_index for item in peaks)
    amplitude_ok = max_error <= 1e-12
    exact = normalized["exact_integer_alignment"]
    if exact:
        _require(index_ok, "exact_case_peak_mismatch")
        _require(amplitude_ok, "exact_case_amplitude_mismatch")
    return {
        "case_id": case["case_id"],
        "axis": case["axis"],
        "geometry": _geometry_record(normalized),
        "source_time_ns": case["source_time_ns"],
        "sample_count": case["length"],
        "declared_amplitudes": case["amplitudes"],
        "expected_reference_index": expected_index,
        "aligned": {
            "relative_ns": _sample_strings(aligned["relative_ns"]),
            "relative_q16": aligned["relative_q16"],
            "relative_samples": [value / Q16 for value in aligned["relative_q16"]],
            "exact_integer_alignment": exact,
            "recovered_peak_indices": [item["index"] for item in peaks],
            "recovered_peak_values": [item["value"] for item in peaks],
            "max_abs_amplitude_error": max_error,
            "index_match": index_ok,
            "amplitude_match": amplitude_ok,
            "leading_zeros": aligned["leading_zeros"],
            "trailing_zeros": aligned["trailing_zeros"],
            "output_digests": aligned["output_digests"],
        },
        "fixture_digest": object_digest(fixture),
        "exact": exact,
    }


def _identity_control() -> Dict[str, Any]:
    case = cases()[0]
    geometry = _case_geometry(case)
    samples = [((index * 7) % 23 - 11) / 8.0 for index in range(case["length"])]
    channels = [list(samples) for _ in range(len(case["mic_ids"]))]
    aligned = align_channels(geometry, channels)
    reference = aligned["outputs"][0]
    return {
        "case_id": "reference_mic_identity",
        "description": "The reference microphone has relative_q16=0; its aligned output is bit-identical to the input control sequence.",
        "sample_count": len(samples),
        "relative_q16_reference": aligned["relative_q16"][0],
        "input_digest": tensor_digest(samples),
        "reference_output_digest": aligned["output_digests"][0],
        "bit_identical": reference == samples,
    }


def _reject_code(callable_: Any) -> str:
    try:
        callable_()
    except Reject as error:
        return error.code
    raise Reject("adverse_case_not_rejected")


def adverse_rejections() -> List[Dict[str, Any]]:
    base = _case_geometry(cases()[0])

    def mutate(**changes: Any) -> Dict[str, Any]:
        clone = json.loads(json.dumps(base))
        clone.update(changes)
        return clone

    def duplicate_position() -> None:
        clone = json.loads(json.dumps(base))
        clone["microphones"][1]["position_nm"] = [0, 0, 0]
        validate_geometry(clone)

    def duplicate_id() -> None:
        clone = json.loads(json.dumps(base))
        clone["microphones"][1]["id"] = "m0"
        validate_geometry(clone)

    def unknown_reference() -> None:
        validate_geometry(mutate(reference_mic_id="m9"))

    def non_integer_position() -> None:
        clone = json.loads(json.dumps(base))
        clone["microphones"][1]["position_nm"] = [1.5, 0, 0]
        validate_geometry(clone)

    def out_of_range_position() -> None:
        clone = json.loads(json.dumps(base))
        clone["microphones"][1]["position_nm"] = [MAX_POSITION_NM + 1, 0, 0]
        validate_geometry(clone)

    def bad_direction() -> None:
        validate_geometry(mutate(source_direction=[1, 1, 0]))

    def zero_direction() -> None:
        validate_geometry(mutate(source_direction=[0, 0, 0]))

    def bad_rate() -> None:
        validate_geometry(mutate(sample_rate_hz=48000))

    def bad_speed() -> None:
        validate_geometry(mutate(speed_of_sound_nm_per_ns=340))

    def missing_channel() -> None:
        clone = json.loads(json.dumps(base))
        clone["channels"].pop()
        validate_geometry(clone)

    def duplicate_channel() -> None:
        clone = json.loads(json.dumps(base))
        clone["channels"][1]["mic_id"] = "m0"
        validate_geometry(clone)

    def unknown_channel() -> None:
        clone = json.loads(json.dumps(base))
        clone["channels"][1]["mic_id"] = "m9"
        validate_geometry(clone)

    def drift() -> None:
        clone = json.loads(json.dumps(base))
        clone["channels"][1]["clock_ppm"] = 5
        validate_geometry(clone)

    def offset_range() -> None:
        clone = json.loads(json.dumps(base))
        clone["channels"][1]["capture_offset_ns"] = MAX_CAPTURE_OFFSET_NS + 1
        validate_geometry(clone)

    def extra_field() -> None:
        clone = json.loads(json.dumps(base))
        clone["unexpected"] = 1
        validate_geometry(clone)

    def nonfinite_sample() -> None:
        validate_geometry(base)
        align_channels(base, [[0.0] * 8, [float("nan")] * 8, [0.0] * 8])

    def sample_type() -> None:
        align_channels(base, [[0.0] * 8, ["0"] * 8, [0.0] * 8])

    def length_mismatch() -> None:
        align_channels(base, [[0.0] * 8, [0.0] * 7, [0.0] * 8])

    def empty_channel() -> None:
        align_channels(base, [[], [], []])

    def channel_count() -> None:
        align_channels(base, [[0.0] * 8, [0.0] * 8])

    def duplicate_json() -> None:
        parse_strict_json('{"a":1,"a":2}')

    def nonfinite_json() -> None:
        parse_strict_json('{"a":NaN}')

    def invalid_json() -> None:
        parse_strict_json('{"a":}')

    cases_ = [
        ("duplicate_mic_position", "duplicate_mic_position", duplicate_position),
        ("duplicate_mic_id", "duplicate_mic_id", duplicate_id),
        ("unknown_reference_mic", "unknown_reference_mic", unknown_reference),
        ("non_integer_position", "invalid_position", non_integer_position),
        ("position_out_of_range", "invalid_position", out_of_range_position),
        ("direction_not_exactly_normalizable", "direction_not_exactly_normalizable",
         bad_direction),
        ("zero_direction", "zero_direction", zero_direction),
        ("unsupported_sample_rate", "unsupported_sample_rate", bad_rate),
        ("unsupported_speed_of_sound", "unsupported_speed_of_sound", bad_speed),
        ("missing_channel", "channel_mic_set_mismatch", missing_channel),
        ("duplicate_channel_mic", "duplicate_channel_mic", duplicate_channel),
        ("unknown_channel_mic", "unknown_channel_mic", unknown_channel),
        ("clock_drift_not_supported", "clock_drift_not_supported", drift),
        ("capture_offset_out_of_range", "capture_offset_out_of_range", offset_range),
        ("invalid_geometry_fields", "invalid_geometry_fields", extra_field),
        ("nonfinite_sample", "nonfinite_sample", nonfinite_sample),
        ("invalid_sample_type", "invalid_sample_type", sample_type),
        ("channel_length_mismatch", "channel_length_mismatch", length_mismatch),
        ("empty_channel", "invalid_channel_length", empty_channel),
        ("channel_count_mismatch", "channel_count_mismatch", channel_count),
        ("duplicate_json_key", "duplicate_json_key:a", duplicate_json),
        ("nonfinite_json_constant", "nonfinite_json_constant:NaN", nonfinite_json),
        ("invalid_json", "invalid_json", invalid_json),
    ]

    before = object_digest(_evaluate_case(cases()[0]))
    records = []
    for case_id, expected, function in cases_:
        actual = _reject_code(function)
        _require(actual == expected, "adverse_code_mismatch:" + case_id)
        records.append({
            "case_id": case_id,
            "status": "rejected",
            "code": actual,
            "state_unchanged": True,
        })
    after = object_digest(_evaluate_case(cases()[0]))
    _require(before == after, "adverse_state_mutation")
    return records


def release_gates() -> List[Dict[str, Any]]:
    return [
        {
            "id": "RG-01",
            "requirement": "Exact licensed or device-authoritative 3-D array geometry, layout, orientation, channel calibration and capture pipeline with measured timestamp provenance.",
            "status": "blocked",
        },
        {
            "id": "RG-02",
            "requirement": "Pinned runnable spatial/time-alignment source or runtime with exact adapter settings, immutable revision and verified artifact rights.",
            "status": "blocked",
        },
        {
            "id": "RG-03",
            "requirement": "Rights-cleared synchronized real-array corpus with consent, geometry metadata, reference/target directions, movement, channel loss and room/reference conditions.",
            "status": "blocked",
        },
        {
            "id": "RG-04",
            "requirement": "Exact-runtime parity on known synthetic delays and asynchronous-reference offsets at the declared geometry and rate.",
            "status": "blocked",
        },
        {
            "id": "RG-05",
            "requirement": "Measured channel synchronization, clock offset/drift, geometry mismatch, channel dropout and target-device timing within declared bounds.",
            "status": "blocked",
        },
        {
            "id": "RG-06",
            "requirement": "Task-matched held-out localization/activity/extraction scoring, including leakage, target damage, channel loss and room/reference change strata.",
            "status": "blocked",
        },
        {
            "id": "RG-07",
            "requirement": "Opt-in provider intake, descriptor/config review and independent exact-head review; no registration or default change before this gate.",
            "status": "blocked",
        },
        {
            "id": "RG-08",
            "requirement": "Explicit public default selection and release approval; DEFER remains in force until RG-01 through RG-07 close.",
            "status": "blocked",
        },
    ]


def exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "licensed_geometry_and_real_array_corpus_absent",
            "requirement": "Supply a rights-cleared synchronized real 3-D microphone-array recording with microphone positions, orientation, calibration, channel timestamps, source/target/reference conditions, movement and a consent/usage grant.",
            "state": "No real array recording, geometry manifest, calibration file or consent grant is staged. Only adjacent synthetic two-channel WPE fixtures and mono 16/48 kHz listening WAVs exist.",
        },
        {
            "id": "pinned_source_or_runtime_absent",
            "requirement": "Pin one exact licensed spatial/time-alignment implementation or runtime, its immutable revision, build/archive identity and declared adapter settings.",
            "state": "S24/S25/S26 are search excerpts only; no package, source tree, runtime, adapter or numeric output is staged. The installed v0 provider/session ABI stays unchanged.",
        },
        {
            "id": "device_timing_calibration_absent",
            "requirement": "Measure channel synchronization, clock offset/drift, geometry mismatch, channel loss and target-device timing on the intended capture device.",
            "state": "This package declares integer nanosecond capture offsets only. Nonzero clock drift is rejected, no device clock was measured and no deadline/RTF result exists.",
        },
        {
            "id": "rights_and_task_matched_evidence_absent",
            "requirement": "Supply permissions plus task-matched held-out localization/activity/extraction labels and leakage, target-damage and channel-loss scoring, with independent review.",
            "state": "No corpus rights, held-out split, label set, metric result, listening test, benchmark, provider intake or release approval exists; no result may qualify.",
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
        "note": "Only the stable linked-row identity is gated. The mutable full plan/swarm/TASKS.json is never read into, hashed by or pinned to this package.",
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
                "status": "synthetic_only",
                "evidence": "Integer nanometre linear/planar synthetic geometries and exactly normalizable plane-wave directions; no measured array, orientation or device layout.",
            },
            "timestamp_calibration": {
                "status": "synthetic_only",
                "evidence": "Explicit integer nanosecond capture offsets and asynchronous-reference alignment; clock drift is rejected and no device clock was measured.",
            },
            "source_target_reference_conditions_and_permissions": {
                "status": "blocked",
                "evidence": "No real recording, reference/target condition, consent or usage permission is staged.",
            },
            "task_matched_heldout_localization_activity_extraction": {
                "status": "blocked",
                "evidence": "No held-out array labels, localization/activity/extraction output or scorer exists; this package is time alignment only.",
            },
            "leakage_target_damage_channel_loss": {
                "status": "blocked",
                "evidence": "No real target, interference, leakage or channel-loss stratum is available; integer alignment only controls its own synthetic fixture.",
            },
            "room_reference_changes": {
                "status": "blocked",
                "evidence": "No room, RIR or reference-condition change is measured; adjacent WPE fixtures are not pooled into an alignment result.",
            },
        },
        "mapped_cases": {
            "synthetic_exact_integer_delays": "two frozen geometries, 3 and 4 microphones, with declared asynchronous capture offsets",
            "fractional_residual_control": "half-sample linear-interpolation surrogate, labelled non-exact and never promoted",
            "reference_identity": "reference microphone passthrough control",
            "missing_or_delayed_reference": "explicit rejection/missing evidence only; no real delayed-reference recording",
        },
        "not_applicable": [
            "echo attenuation, near-end damage, listening quality and benchmark scoring",
            "real source localization, tracking, beamforming or target extraction",
        ],
    }


def _case_matrix(results: Sequence[Dict[str, Any]],
                 fractional: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "case_id": result["case_id"],
            "relative_q16": result["aligned"]["relative_q16"],
            "recovered_peak_indices": result["aligned"]["recovered_peak_indices"],
            "max_abs_amplitude_error": result["aligned"]["max_abs_amplitude_error"],
            "output_digests": result["aligned"]["output_digests"],
        }
        for result in results
    ] + [
        {
            "case_id": fractional["case_id"],
            "relative_q16": fractional["aligned"]["relative_q16"],
            "recovered_peak_indices": fractional["aligned"]["recovered_peak_indices"],
            "max_abs_amplitude_error": fractional["aligned"]["max_abs_amplitude_error"],
            "output_digests": fractional["aligned"]["output_digests"],
            "exact": fractional["exact"],
        }
    ]


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()

    results = [_evaluate_case(case) for case in cases()]
    fractional = _evaluate_case(fractional_case())
    identity = _identity_control()
    adverse = adverse_rejections()
    _require(not fractional["exact"], "fractional_control_claimed_exact")
    _require(identity["bit_identical"], "reference_identity_failed")
    _require(all(not result["aligned"]["max_abs_amplitude_error"]
                 for result in results), "exact_case_not_exact")

    matrix = _case_matrix(results, fractional)
    repeat_digests = []
    for _ in range(3):
        repeated = [_evaluate_case(case) for case in cases()]
        repeated_fractional = _evaluate_case(fractional_case())
        repeat_digests.append(object_digest(
            _case_matrix(repeated, repeated_fractional)))
    repeat_digests.append(object_digest(matrix))
    _require(len(set(repeat_digests)) == 1, "case_matrix_not_repeatable")

    report = {
        "schema_id": REPORT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_synthetic_incomplete",
        "evidence_status": "incomplete",
        "decision": "DEFER",
        "defer_before": "opt_in_adapter_exposure",
        "scope": (
            "Task-local deterministic integer geometry and asynchronous-reference "
            "time-alignment surrogate on synthetic channels. No licensed source, "
            "real array recording, runtime, device calibration, listening, "
            "benchmark or release result is present."
        ),
        "acceptance_profile": spatial_profile(),
        "format": {
            "installed_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "installed_v0_channels": 1,
            "installed_v0_frame_samples": FRAME_SAMPLES,
            "installed_v0_sample_format": "f32",
            "installed_v0_geometry_unchanged": True,
            "model_sample_rate_hz": SAMPLE_RATE_HZ,
            "model_channels_min": 2,
            "model_channels_max": MAX_MICS,
            "model_frame_samples": FRAME_SAMPLES,
            "sample_period_ns": SAMPLE_PERIOD_NS,
            "speed_of_sound_nm_per_ns": SPEED_OF_SOUND_NM_PER_NS,
            "position_unit": "integer_nanometre",
            "delay_unit": "integer_nanosecond_and_q16_sample",
            "added_content_delay_samples": 0,
            "clock_drift_supported": False,
        },
        "reference": {
            "reference_id": "geometry-time-alignment-surrogate-v1",
            "modes": ["synthetic_integer_alignment", "fractional_surrogate_control"],
            "candidate": "declared_geometry_alignment",
            "control": "reference_mic_identity",
            "exact_integer_alignment_only": True,
            "fractional_residual_is_surrogate": True,
            "model_weights": False,
            "downloads": False,
            "real_speech": False,
            "licensed_runtime": False,
            "device_or_timing_claim": False,
            "registered": False,
            "default_enabled": False,
        },
        "geometry_cases": [result["geometry"] for result in results],
        "known_synthetic_delays": [
            {
                "case_id": result["case_id"],
                "expected_reference_index": result["expected_reference_index"],
                "declared_amplitudes": result["declared_amplitudes"],
                "aligned": result["aligned"],
                "fixture_digest": result["fixture_digest"],
                "exact": result["exact"],
            }
            for result in results
        ],
        "fractional_residual_control": {
            "case_id": fractional["case_id"],
            "status": "surrogate_only_not_qualified",
            "expected_reference_index": fractional["expected_reference_index"],
            "declared_amplitudes": fractional["declared_amplitudes"],
            "aligned": fractional["aligned"],
            "fixture_digest": fractional["fixture_digest"],
            "exact": fractional["exact"],
            "note": "Half-sample arrivals use fixed-point linear interpolation. The resulting amplitude attenuation is reported, not promoted to a sub-sample qualification result.",
        },
        "identity_control": identity,
        "adverse_rejections": adverse,
        "adverse_all_rejected": True,
        "real_recordings": {
            "status": "blocked",
            "present": False,
            "executed": False,
            "result": None,
            "requirement": "Rights-cleared synchronized real 3-D microphone-array recording with geometry, calibration, timestamps, conditions and permissions.",
            "observed_evidence": (
                "Pinned workspace evidence contains adjacent synthetic two-channel "
                "WPE fixtures and mono 16/48 kHz listening WAVs only. The pinned "
                "spatial-trials follow-up reports no compatible multichannel "
                "speaker target corpus, no staged spatial model and no array "
                "geometry. No multichannel array recording, geometry manifest, "
                "calibration file or consent grant is staged."
            ),
        },
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "qualification": {
            "status": "not_qualified",
            "decision": "DEFER",
            "evidence_status": "incomplete",
            "proposal_only": True,
            "qualifies": False,
            "all_required_results_present": False,
            "missing_result_promoted": False,
            "real_recording_evidence": False,
            "exact_runtime_parity": False,
            "device_timing": False,
            "heldout_scoring": False,
            "provider_intake": False,
        },
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
            "case_matrix_digests": repeat_digests[:3],
            "byte_identical": True,
            "comparison": "exact SHA-256 over canonical case-matrix JSON; no tolerance",
        },
        "negative_claims": [
            "No licensed spatial/time-alignment source, runtime, model, weight, corpus or device was used.",
            "No real microphone-array recording, calibration or channel timestamp was measured.",
            "The synthetic geometry and integer alignment model is not the catalogued candidate.",
            "The fractional half-sample interpolation is a labelled surrogate and cannot qualify.",
            "No localization, tracking, beamforming, extraction, leakage, target-damage or quality result is claimed.",
            "No provider, descriptor, registry, installed v0 default, shared build or CI was changed.",
        ],
        "reopen_condition": (
            "Supply a rights-cleared synchronized real array corpus with geometry, "
            "calibration and timestamps; pin one exact licensed or device-authoritative "
            "source/runtime; reproduce exact-runtime parity on known synthetic delays; "
            "measure device synchronization and drift; score task-matched held-out "
            "conditions with leakage, target damage and channel loss; complete opt-in "
            "provider intake and independent review before RG-08."
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
    """Build contract.json after report.json and its sidecar are written."""
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
        "status": "proposal_only_synthetic_incomplete",
        "evidence_status": "incomplete",
        "decision": "DEFER",
        "defer_before": "opt_in_adapter_exposure",
        "qualification_status": "not_qualified",
        "verification_profile": "spatial",
        "scope": {
            "benchmark_claim": False,
            "device_timing": False,
            "listening": False,
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
            "model_channels_min": 2,
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
            "reference_id": "geometry-time-alignment-surrogate-v1",
            "modes": ["synthetic_integer_alignment", "fractional_surrogate_control"],
            "exact_integer_alignment_only": True,
            "fractional_residual_is_surrogate": True,
            "model_weights": False,
            "downloads": False,
            "device_or_timing_claim": False,
            "registered": False,
            "default_enabled": False,
        },
        "board_row": stable,
        "exact_blockers": blockers,
        "release_gates": gates,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": pins,
        "negative_claims": [
            "No licensed source, runtime, model, weight, corpus, real recording or device was used.",
            "No qualified alignment, localization, tracking, beamforming or release result exists.",
            "No provider registration, installed v0, ABI, registry, default, shared build or CI change exists.",
        ],
        "reopen_condition": (
            "Close RG-01 through RG-08 with a rights-cleared real array corpus, "
            "pinned licensed or device-authoritative source/runtime, exact-runtime "
            "parity, measured device synchronization, held-out scoring and "
            "independent opt-in provider review."
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
