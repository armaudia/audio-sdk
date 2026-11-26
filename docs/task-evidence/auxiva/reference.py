# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local evidence for ``SDK-AUXIVA`` (AuxIVA).

The exact AuxIVA source, runtime, adapter, immutable revision, numeric output
and rights-cleared multi-channel corpus are absent.  This module therefore
builds a bounded, deterministic, stdlib-only **synthetic two-source /
two-microphone boundary surrogate** and emits a strict ``DEFER``,
``incomplete`` and ``not_qualified`` conclusion.

The surrogate is **not AuxIVA**.  It applies a frozen integer mixing matrix and
its exact inverse to fixed synthetic sources, and separately runs a fixed-step
second-order decorrelation control.  It records that row permutation and output
scale are not resolved by separation scores alone, which is exactly why an
exact-runtime, label-bearing multi-channel qualification is required.

Nothing here downloads, copies, imports, loads or executes AuxIVA, H-GTCRN,
Pyroomacoustics, Asteroid, a checkpoint, a native library, real audio, a corpus
or a device clock.  No provider, descriptor, registry, installed v0 path,
shared build, dependency lock, CI, board row or handoff is changed.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]

TASK_ID = "SDK-AUXIVA"
TITLE = "AuxIVA"
COMPONENT = "auxiva"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-AUXIVA"
BASE_COMMIT = "aacd6b19b51d4ae2d125ed40488a0e5a8357ec82"
TASK_PREFIX = "docs/task-evidence/auxiva/"
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"
REVIEWER = "reviewer-AUXIVA"

REPORT_SCHEMA = "audio-sdk/auxiva-report/0.1"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
GEOMETRY_SCHEMA = "audio-sdk/array-geometry/0.1"
PROFILE = "spatial"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"

SAMPLE_RATE_HZ = 16000
SAMPLE_PERIOD_NS = 62_500
CHANNELS = 2
FRAME_SAMPLES = 160
HOP_SAMPLES = 160
TOTAL_SAMPLES = 4096
SPEED_OF_SOUND_NM_PER_NS = 343
Q16 = 65_536
MAX_CHANNELS = 16
MAX_POSITION_NM = 10_000_000_000
MAX_SAMPLES = 1_000_000
MAX_ABS_SAMPLE = 1_000_000.0
MAX_MATRIX_ENTRY = 32.0
ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}\Z")

CONFIG_FIELDS = {
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "hop_samples",
    "sample_format",
    "clock_ppm",
}
GEOMETRY_FIELDS = {
    "schema_id",
    "array_id",
    "sample_rate_hz",
    "speed_of_sound_nm_per_ns",
    "reference_mic_id",
    "microphones",
    "source_direction",
}
MIC_FIELDS = {"id", "position_nm"}
CALLER_ASSET_FIELDS = {
    "adapter",
    "channels",
    "frame_samples",
    "license_id",
    "permutation_reference",
    "runtime_path",
    "runtime_sha256",
    "sample_format",
    "sample_rate_hz",
    "source_commit",
    "source_path",
    "source_sha256",
}

#: Stable read-only source pins, relative to the workspace root.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/noise_suppression_candidate_census.md":
        "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
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
    "docs/task-evidence/offline-multichannel-wpe/README.md":
        "8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9",
    "docs/task-evidence/offline-multichannel-wpe/report.json":
        "4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba",
    "docs/task-evidence/online-multichannel-wpe/README.md":
        "3615f6fc66d3c8d15a4cd77ccdc1f8a2e5f9c6cd9a1a20b9263814bfb2c34013",
    "docs/task-evidence/online-multichannel-wpe/report.json":
        "df76b6e78ab86bc21609d3a93d53bc175b9281962396cc3bf1acf8ea2d994e6f",
    "docs/task-evidence/speechbrain-sepformer-dns4/README.md":
        "1cc709249b21f2cdb5ad4bc3510b9479e3e07f6630aa45bea4cad22ea8698ecc",
    "docs/task-evidence/speechbrain-sepformer-dns4/report.json":
        "e56b83bde079fca411ca8d98890fcc75e8302834b0df268c0fc87d43b2d32013",
}

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

#: Files pinned by ``SOURCES.sha256``; it never pins itself.
PIN_FILES: Tuple[str, ...] = ARTIFACT_FILES + ("contract.json",)

BOARD_ROW_STABLE_SHA256 = (
    "6fb001411f83ec74f7aae69078af99afe6b8a19e722e9a957d4b5ddc3427778f")

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

SOURCE_A = {"id": "s1", "amplitude": 12000, "step": 1, "phase": 0}
SOURCE_B = {"id": "s2", "amplitude": 6000, "step": 7, "phase": 11}
MIXING_MATRIX: Tuple[Tuple[int, int], Tuple[int, int]] = ((3, 1), (2, 3))
INVERSE_MATRIX: Tuple[Tuple[int, int], Tuple[int, int]] = ((3, -1), (-2, 3))
SCALED_MATRIX: Tuple[Tuple[int, int], Tuple[int, int]] = ((6, -2), (-4, 6))
PERMUTED_MATRIX: Tuple[Tuple[int, int], Tuple[int, int]] = ((-2, 3), (3, -1))
IDENTITY_MATRIX: Tuple[Tuple[int, int], Tuple[int, int]] = ((1, 0), (0, 1))
EXACT_GAIN = 7
SCALED_GAIN = 14
BLIND_ITERATIONS = 16
BLIND_STEP = 0.25
BLIND_CLAMP = 4.0

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No AuxIVA source, runtime, adapter, revision, numeric output or checkpoint was produced, loaded or executed.",
    "No separation, quality, latency, benchmark, listening or release result is claimed.",
    "The synthetic boundary surrogate is not AuxIVA and cannot qualify the candidate.",
    "Multi-channel source permutation is not resolved; a row-permuted inverse is equally exact on the synthetic fixture.",
    "Output scale is not resolved; scale-invariant scoring cannot pin the separated waveform gain.",
    "No real corpus, multi-channel audio, speaker label, device clock or listener was used.",
    "H-GTCRN is a separate bundled component; its source, checkpoint, adapter and evidence are not pooled here.",
    "No provider, descriptor, registry, installed v0 path, shared build, dependency lock or CI was changed.",
)

REOPEN_CONDITION = (
    "Pin the exact licensed AuxIVA source or runtime and immutable revision, admit an "
    "isolated hash-pinned runtime, clear all artifact and corpus rights, reproduce exact "
    "multi-channel outputs, qualify source permutation and scale on a rights-cleared "
    "label-bearing held-out cohort, measure target timing and complete opt-in provider "
    "intake. Until then the candidate stays DEFER, incomplete and not qualified."
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


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def tensor_digest(values: Sequence[float]) -> str:
    import struct
    digest = hashlib.sha256()
    for value in values:
        digest.update(struct.pack("<d", float(value)))
    return digest.hexdigest()


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _as_int(value: Any, code: str, low: int, high: int) -> int:
    _require(_is_plain_int(value), code)
    _require(low <= value <= high, code)
    return value


def _as_id(value: Any, code: str) -> str:
    _require(isinstance(value, str) and ID_PATTERN.match(value) is not None, code)
    return value


def _as_number(value: Any, code: str, bound: float) -> float:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), code)
    number = float(value)
    _require(math.isfinite(number) and abs(number) <= bound, code)
    return number


def _as_triple(value: Any, code: str, bound: int) -> Tuple[int, int, int]:
    _require(isinstance(value, (list, tuple)) and len(value) == 3, code)
    return tuple(_as_int(item, code, -bound, bound) for item in value)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Strict configuration, geometry, matrix and channel validation
# ---------------------------------------------------------------------------

DEFAULT_CONFIG: Dict[str, Any] = {
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "channels": CHANNELS,
    "frame_samples": FRAME_SAMPLES,
    "hop_samples": HOP_SAMPLES,
    "sample_format": "float32",
    "clock_ppm": 0,
}


def validate_config(config: Any) -> Dict[str, Any]:
    _require(isinstance(config, dict), "config_not_object")
    _require(set(config) == CONFIG_FIELDS, "config_fields_mismatch")
    _require(_is_plain_int(config["sample_rate_hz"]), "invalid_sample_rate")
    _require(config["sample_rate_hz"] == SAMPLE_RATE_HZ, "invalid_sample_rate")
    _require(_is_plain_int(config["channels"]), "invalid_channels")
    _require(config["channels"] == CHANNELS, "invalid_channels")
    _require(_is_plain_int(config["frame_samples"]), "invalid_frame_samples")
    _require(config["frame_samples"] == FRAME_SAMPLES, "invalid_frame_samples")
    _require(_is_plain_int(config["hop_samples"]), "invalid_hop_samples")
    _require(config["hop_samples"] == HOP_SAMPLES, "invalid_hop_samples")
    _require(config["sample_format"] == "float32", "invalid_sample_format")
    _require(_is_plain_int(config["clock_ppm"]), "invalid_clock_ppm")
    _require(config["clock_ppm"] == 0, "unsupported_clock_drift")
    return dict(config)


GEOMETRY: Dict[str, Any] = {
    "schema_id": GEOMETRY_SCHEMA,
    "array_id": "auxiva-synthetic-linear-3",
    "sample_rate_hz": SAMPLE_RATE_HZ,
    "speed_of_sound_nm_per_ns": SPEED_OF_SOUND_NM_PER_NS,
    "reference_mic_id": "m0",
    "microphones": [
        {"id": "m0", "position_nm": [0, 0, 0]},
        {"id": "m1", "position_nm": [21_437_500, 0, 0]},
        {"id": "m2", "position_nm": [0, 21_437_500, 0]},
    ],
    "source_direction": [1, 0, 0],
}


def validate_geometry(geometry: Any) -> Dict[str, Any]:
    _require(isinstance(geometry, dict), "geometry_not_object")
    _require(set(geometry) == GEOMETRY_FIELDS, "geometry_fields_mismatch")
    _require(geometry["schema_id"] == GEOMETRY_SCHEMA, "invalid_geometry_schema")
    _as_id(geometry["array_id"], "invalid_array_id")
    _require(_is_plain_int(geometry["sample_rate_hz"]), "invalid_sample_rate")
    _require(geometry["sample_rate_hz"] == SAMPLE_RATE_HZ, "invalid_sample_rate")
    _require(_is_plain_int(geometry["speed_of_sound_nm_per_ns"]),
             "invalid_speed_of_sound")
    _require(geometry["speed_of_sound_nm_per_ns"] == SPEED_OF_SOUND_NM_PER_NS,
             "invalid_speed_of_sound")
    reference = _as_id(geometry["reference_mic_id"], "invalid_reference_mic")
    mics = geometry["microphones"]
    _require(isinstance(mics, list), "invalid_microphones")
    _require(2 <= len(mics) <= MAX_CHANNELS, "invalid_microphone_count")
    normalized: List[Dict[str, Any]] = []
    seen_ids = set()
    seen_positions = set()
    for mic in mics:
        _require(isinstance(mic, dict), "invalid_microphone")
        _require(set(mic) == MIC_FIELDS, "microphone_fields_mismatch")
        mic_id = _as_id(mic["id"], "invalid_mic_id")
        _require(mic_id not in seen_ids, "duplicate_mic_id")
        seen_ids.add(mic_id)
        position = _as_triple(mic["position_nm"], "invalid_position",
                              MAX_POSITION_NM)
        _require(position not in seen_positions, "duplicate_mic_position")
        seen_positions.add(position)
        normalized.append({"id": mic_id, "position_nm": list(position)})
    _require(reference in seen_ids, "unknown_reference_mic")
    direction = _as_triple(geometry["source_direction"],
                           "invalid_source_direction", 1_000_000)
    norm_squared = sum(component * component for component in direction)
    norm = math.isqrt(norm_squared)
    _require(norm > 0 and norm * norm == norm_squared,
             "direction_not_exactly_normalizable")
    return {
        "schema_id": GEOMETRY_SCHEMA,
        "array_id": geometry["array_id"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "speed_of_sound_nm_per_ns": SPEED_OF_SOUND_NM_PER_NS,
        "reference_mic_id": reference,
        "microphones": normalized,
        "source_direction": list(direction),
        "direction_norm": norm,
    }


def geometry_record() -> Dict[str, Any]:
    normalized = validate_geometry(GEOMETRY)
    direction = normalized["source_direction"]
    norm = normalized["direction_norm"]
    speed = normalized["speed_of_sound_nm_per_ns"]
    tdoa_ns: List[int] = []
    for mic in normalized["microphones"]:
        projection = sum(a * b for a, b in zip(mic["position_nm"], direction))
        # Exact rational plane-wave delay in integer nanoseconds.
        numerator = -projection
        denominator = speed * norm
        _require(numerator % denominator == 0, "nonexact_tdoa")
        tdoa_ns.append(numerator // denominator)
    relative_q16 = [
        value * Q16 // SAMPLE_PERIOD_NS for value in tdoa_ns
    ]
    return {
        "array_id": normalized["array_id"],
        "capture_offset_ns": [0] * len(tdoa_ns),
        "clock_ppm": 0,
        "direction_norm": norm,
        "exact_integer_samples": all(value % Q16 == 0 for value in relative_q16),
        "microphone_count": len(tdoa_ns),
        "microphones": normalized["microphones"],
        "reference_mic_id": normalized["reference_mic_id"],
        "relative_q16": relative_q16,
        "relative_samples": [value // Q16 for value in relative_q16],
        "sample_period_ns": SAMPLE_PERIOD_NS,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "source_direction": normalized["source_direction"],
        "speed_of_sound_nm_per_ns": speed,
        "tdoa_ns": tdoa_ns,
    }


def validate_matrix(matrix: Any) -> List[List[float]]:
    _require(isinstance(matrix, (list, tuple)) and len(matrix) == 2,
             "invalid_matrix_shape")
    rows: List[List[float]] = []
    for row in matrix:
        _require(isinstance(row, (list, tuple)) and len(row) == 2,
                 "invalid_matrix_shape")
        rows.append([_as_number(value, "invalid_matrix_entry", MAX_MATRIX_ENTRY)
                     for value in row])
    determinant = rows[0][0] * rows[1][1] - rows[0][1] * rows[1][0]
    _require(abs(determinant) > 1e-12, "singular_matrix")
    return rows


def validate_channels(channels: Any) -> List[List[float]]:
    _require(isinstance(channels, (list, tuple)) and len(channels) == CHANNELS,
             "invalid_channel_count")
    normalized: List[List[float]] = []
    length = None
    for channel in channels:
        _require(isinstance(channel, (list, tuple)), "invalid_channel")
        _require(len(channel) > 0, "empty_channel")
        if length is None:
            length = len(channel)
        _require(len(channel) == length, "channel_length_mismatch")
        _require(len(channel) <= MAX_SAMPLES, "channel_too_long")
        values: List[float] = []
        for sample in channel:
            _require(isinstance(sample, (int, float))
                     and not isinstance(sample, bool), "invalid_sample")
            number = float(sample)
            _require(math.isfinite(number), "nonfinite_sample")
            _require(abs(number) <= MAX_ABS_SAMPLE, "sample_out_of_range")
            values.append(number)
        normalized.append(values)
    return normalized


# ---------------------------------------------------------------------------
# Deterministic fixture and separation controls
# ---------------------------------------------------------------------------

def source_signals() -> Tuple[List[int], List[int]]:
    first = [
        (SOURCE_A["amplitude"] * SINE64[(index + SOURCE_A["phase"]) % 64]) >> 15
        for index in range(TOTAL_SAMPLES)
    ]
    second = [
        (SOURCE_B["amplitude"]
         * SINE64[(index * SOURCE_B["step"] + SOURCE_B["phase"]) % 64]) >> 15
        for index in range(TOTAL_SAMPLES)
    ]
    return first, second


def mix_sources(first: Sequence[float],
                second: Sequence[float]) -> Tuple[List[float], List[float]]:
    _require(len(first) == len(second) and len(first) > 0, "source_length_mismatch")
    left: List[float] = []
    right: List[float] = []
    for one, two in zip(first, second):
        left.append(MIXING_MATRIX[0][0] * one + MIXING_MATRIX[0][1] * two)
        right.append(MIXING_MATRIX[1][0] * one + MIXING_MATRIX[1][1] * two)
    return left, right


def apply_matrix(matrix: Any,
                 channels: Any) -> Tuple[List[float], List[float]]:
    normalized_matrix = validate_matrix(matrix)
    normalized_channels = validate_channels(channels)
    first, second = normalized_channels
    left = [
        normalized_matrix[0][0] * one + normalized_matrix[0][1] * two
        for one, two in zip(first, second)
    ]
    right = [
        normalized_matrix[1][0] * one + normalized_matrix[1][1] * two
        for one, two in zip(first, second)
    ]
    return left, right


def rms(values: Sequence[float]) -> float:
    _require(len(values) > 0, "empty_signal")
    return math.sqrt(sum(value * value for value in values) / len(values))


def max_abs(values: Sequence[float]) -> float:
    _require(len(values) > 0, "empty_signal")
    return max(abs(value) for value in values)


def nonfinite_count(values: Sequence[float]) -> int:
    return sum(0 if math.isfinite(value) else 1 for value in values)


def correlation(first: Sequence[float], second: Sequence[float]) -> float:
    _require(len(first) == len(second) and len(first) > 0, "source_length_mismatch")
    energy_first = sum(value * value for value in first)
    energy_second = sum(value * value for value in second)
    _require(energy_first > 0 and energy_second > 0, "zero_energy_source")
    cross = sum(one * two for one, two in zip(first, second))
    return round(cross / math.sqrt(energy_first * energy_second), 12)


def si_sdr_db(output: Sequence[float], reference: Sequence[float]) -> Any:
    """Scale-invariant SI-SDR in dB, or ``None`` for an exact/zero reference."""
    _require(len(output) == len(reference) and len(output) > 0,
             "signal_length_mismatch")
    reference_energy = sum(value * value for value in reference)
    if reference_energy == 0:
        return None
    numerator = sum(one * two for one, two in zip(output, reference))
    alpha = numerator / reference_energy
    residual = sum((one - alpha * two) ** 2
                   for one, two in zip(output, reference))
    if residual == 0:
        return None
    return round(10.0 * math.log10(alpha * alpha * reference_energy / residual), 9)


def gain_estimate(output: Sequence[float], reference: Sequence[float]) -> float:
    reference_energy = sum(value * value for value in reference)
    _require(reference_energy > 0, "zero_energy_source")
    return round(sum(one * two for one, two in zip(output, reference))
                 / reference_energy, 9)


def _score_matrix(table: List[List[Any]]) -> Dict[str, Any]:
    permutations = ((0, 1), (1, 0))
    totals: List[Any] = []
    exact_counts: List[int] = []
    for mapping in permutations:
        values = [table[index][mapping[index]] for index in range(2)]
        exact_counts.append(sum(1 for value in values if value is None))
        if any(value is None for value in values):
            totals.append(None)
        else:
            totals.append(round(sum(values), 9))
    # Prefer the assignment with more exact (zero-residual) outputs, then the
    # higher finite SI-SDR sum.  Two fully exact permutations are ambiguous.
    if exact_counts[0] != exact_counts[1]:
        best_index = 0 if exact_counts[0] > exact_counts[1] else 1
    else:
        first_sum = totals[0] if totals[0] is not None else -math.inf
        second_sum = totals[1] if totals[1] is not None else -math.inf
        best_index = 0 if first_sum >= second_sum else 1
    if exact_counts[0] == exact_counts[1] == 2:
        margin: Any = 0.0
        ambiguous = True
    elif totals[0] is not None and totals[1] is not None:
        margin = round(abs(totals[0] - totals[1]), 9)
        ambiguous = margin == 0.0
    else:
        margin = None
        ambiguous = exact_counts[0] == exact_counts[1]
    return {
        "assignment": list(permutations[best_index]),
        "assignment_ambiguous": ambiguous,
        "assignment_margin_db": margin,
        "assignment_score_db": totals[best_index],
        "exact_output_count": exact_counts[best_index],
        "score_alone_resolves_permutation": False,
        "si_sdr_table_db": table,
        "total_db": totals,
    }


def _case(case_id: str, matrix: Any, expected_sources: Any,
          expected_gain: Any, description: str,
          sources: Tuple[Sequence[float], Sequence[float]]) -> Dict[str, Any]:
    first, second = sources
    mixture = mix_sources(first, second)
    left, right = apply_matrix(matrix, [list(mixture[0]), list(mixture[1])])
    outputs = (left, right)
    refs = (first, second)
    table = [[si_sdr_db(output, ref) for ref in refs] for output in outputs]
    residual = 0.0
    if expected_sources is None:
        # Identity control: output must equal the raw synthetic mixture.
        for output, reference in zip(outputs, mixture):
            for value, target in zip(output, reference):
                residual = max(residual, abs(value - target))
    else:
        for output, source_index in zip(outputs, expected_sources):
            for value, reference in zip(output, refs[source_index]):
                residual = max(residual,
                               abs(value - expected_gain * reference))
    return {
        "case_id": case_id,
        "description": description,
        "expected_gain": expected_gain,
        "expected_sources": (None if expected_sources is None
                             else list(expected_sources)),
        "exact": residual == 0.0,
        "gain_estimates": [
            [gain_estimate(output, ref) for ref in refs] for output in outputs
        ],
        "max_abs": [round(max_abs(output), 9) for output in outputs],
        "max_abs_residual": round(residual, 9),
        "nonfinite_samples": sum(nonfinite_count(output) for output in outputs),
        "output_digests": [tensor_digest(output) for output in outputs],
        "output_rms": [round(rms(output), 9) for output in outputs],
        "permutation": _score_matrix(table),
        "scale_pinned": False,
        "status": "synthetic_surrogate_only_not_qualified",
    }


def control_cases() -> List[Dict[str, Any]]:
    first, second = source_signals()
    sources = (first, second)
    return [
        _case("matched_inverse_control", INVERSE_MATRIX, (0, 1), EXACT_GAIN,
              "Frozen integer inverse of the declared mixing matrix; exact "
              "separation with identity assignment.", sources),
        _case("permuted_inverse_control", PERMUTED_MATRIX, (1, 0), EXACT_GAIN,
              "Row-permuted inverse; equally exact separation with swapped "
              "assignment and no intrinsic label resolution.", sources),
        _case("scaled_inverse_control", SCALED_MATRIX, (0, 1), SCALED_GAIN,
              "Inverse multiplied by two; exact waveform shape with arbitrary "
              "output gain.", sources),
        _case("identity_control", IDENTITY_MATRIX, None, None,
              "Identity control: the raw mixture is passed through unchanged.",
              sources),
    ]


def blind_decorrelation(sources: Tuple[Sequence[float], Sequence[float]]
                        ) -> Dict[str, Any]:
    """Fixed-step second-order decorrelation; not AuxIVA and not adaptive IVA."""
    first, second = sources
    mixture = mix_sources(first, second)
    scale = 32768.0
    normalized = [[value / scale for value in channel] for channel in mixture]
    matrix = [[1.0, 0.0], [0.0, 1.0]]
    covariance_history: List[List[float]] = []
    for _ in range(BLIND_ITERATIONS):
        left = [matrix[0][0] * one + matrix[0][1] * two
                for one, two in zip(*normalized)]
        right = [matrix[1][0] * one + matrix[1][1] * two
                 for one, two in zip(*normalized)]
        c11 = sum(value * value for value in left) / len(left)
        c22 = sum(value * value for value in right) / len(right)
        c12 = sum(one * two for one, two in zip(left, right)) / len(left)
        covariance_history.append([round(c11, 12), round(c22, 12),
                                   round(c12, 12)])
        d11, d22, d12 = c11 - 1.0, c22 - 1.0, c12
        updated = [
            [matrix[0][0] - BLIND_STEP * (d11 * matrix[0][0] + d12 * matrix[1][0]),
             matrix[0][1] - BLIND_STEP * (d11 * matrix[0][1] + d12 * matrix[1][1])],
            [matrix[1][0] - BLIND_STEP * (d12 * matrix[0][0] + d22 * matrix[1][0]),
             matrix[1][1] - BLIND_STEP * (d12 * matrix[0][1] + d22 * matrix[1][1])],
        ]
        matrix = [[max(-BLIND_CLAMP, min(BLIND_CLAMP, value)) for value in row]
                  for row in updated]
    matrix = [[round(value, 12) for value in row] for row in matrix]
    left, right = apply_matrix(matrix, [list(first), list(second)])
    table = [[si_sdr_db(output, ref) for ref in (first, second)]
             for output in (left, right)]
    return {
        "covariance_history": covariance_history[-1],
        "iterations": BLIND_ITERATIONS,
        "limitation": "Second-order covariance decorrelation only; not AuxIVA "
                      "and cannot resolve rotation, source permutation or scale.",
        "matrix": matrix,
        "step": BLIND_STEP,
        "outputs": {
            "max_abs": [round(max_abs(left), 9), round(max_abs(right), 9)],
            "nonfinite_samples": nonfinite_count(left) + nonfinite_count(right),
            "output_digests": [tensor_digest(left), tensor_digest(right)],
            "output_rms": [round(rms(left), 9), round(rms(right), 9)],
            "permutation": _score_matrix(table),
            "status": "synthetic_surrogate_only_not_qualified",
        },
    }


# ---------------------------------------------------------------------------
# Fixed demixing session: validation, streaming, reset
# ---------------------------------------------------------------------------

class DemixSession:
    """Bounded fixed-matrix session used only to exercise the boundary.

    It is block invariant, has no adaptive or learned state, and never claims to
    be AuxIVA.  A rejected call leaves ``snapshot`` byte-identical.
    """

    def __init__(self, config: Any = None) -> None:
        self.config = validate_config(DEFAULT_CONFIG if config is None else config)
        self.matrix = [list(row) for row in INVERSE_MATRIX]
        self.accepted_samples = 0
        self.blocks = 0
        self.epoch = 1

    def snapshot(self) -> str:
        return object_digest({
            "accepted_samples": self.accepted_samples,
            "blocks": self.blocks,
            "epoch": self.epoch,
            "matrix": self.matrix,
        })

    def process(self, channels: Any) -> List[List[float]]:
        normalized = validate_channels(channels)
        left, right = apply_matrix(self.matrix, normalized)
        self.accepted_samples += len(normalized[0])
        self.blocks += 1
        return [left, right]

    def reset(self, epoch: Any = 1) -> None:
        _require(_is_plain_int(epoch) and epoch >= 1, "invalid_epoch")
        self.accepted_samples = 0
        self.blocks = 0
        self.epoch = epoch


def streaming_check(sources: Tuple[Sequence[float], Sequence[float]]
                    ) -> Dict[str, Any]:
    mixture = mix_sources(*sources)
    full_session = DemixSession()
    full = full_session.process([list(mixture[0]), list(mixture[1])])
    chunk_sizes = (160, 480, 800, 137, 641)
    results = []
    for chunk in chunk_sizes:
        session = DemixSession()
        collected: List[List[float]] = [[], []]
        for start in range(0, TOTAL_SAMPLES, chunk):
            block = [channel[start:start + chunk] for channel in mixture]
            output = session.process(block)
            collected[0].extend(output[0])
            collected[1].extend(output[1])
        results.append({
            "chunk_samples": chunk,
            "matches_offline": collected == full,
            "output_digests": [tensor_digest(collected[0]),
                               tensor_digest(collected[1])],
        })
    return {
        "accepted_samples": full_session.accepted_samples,
        "all_match": all(item["matches_offline"] for item in results),
        "chunks": list(chunk_sizes),
        "results": results,
    }


def reset_check() -> Dict[str, Any]:
    first, second = source_signals()
    mixture = mix_sources(first, second)
    session = DemixSession()
    session.process([mixture[0][:160], mixture[1][:160]])
    session.reset(1)
    fresh = DemixSession()
    after_reset = session.process([mixture[0][:160], mixture[1][:160]])
    fresh_output = fresh.process([mixture[0][:160], mixture[1][:160]])
    return {
        "epoch": session.epoch,
        "matches_fresh": after_reset == fresh_output,
        "accepted_samples": session.accepted_samples,
    }


# ---------------------------------------------------------------------------
# Caller-supplied exact asset contract (identity only, never executed)
# ---------------------------------------------------------------------------

def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    _require(isinstance(manifest, dict), "manifest_not_object")
    _require(set(manifest) == CALLER_ASSET_FIELDS, "manifest_fields_mismatch")
    _require(isinstance(manifest["license_id"], str)
             and 1 <= len(manifest["license_id"]) <= 64, "invalid_license")
    _require(isinstance(manifest["adapter"], str)
             and ID_PATTERN.match(manifest["adapter"]) is not None,
             "invalid_adapter")
    _require(isinstance(manifest["source_commit"], str)
             and COMMIT_PATTERN.match(manifest["source_commit"]) is not None,
             "invalid_source_commit")
    for key in ("source_sha256", "runtime_sha256"):
        _require(isinstance(manifest[key], str)
                 and SHA256_PATTERN.match(manifest[key]) is not None,
                 "invalid_" + key)
    for key in ("source_path", "runtime_path"):
        _require(isinstance(manifest[key], str)
                 and Path(manifest[key]).is_absolute(), "invalid_" + key)
    _require(manifest["sample_rate_hz"] == SAMPLE_RATE_HZ, "invalid_sample_rate")
    _require(manifest["channels"] == CHANNELS, "invalid_channels")
    _require(manifest["frame_samples"] == FRAME_SAMPLES, "invalid_frame_samples")
    _require(manifest["sample_format"] == "float32", "invalid_sample_format")
    _require(manifest["permutation_reference"] == "caller_labels",
             "invalid_permutation_reference")
    for key in ("source_path", "runtime_path"):
        path = Path(manifest[key])
        _require(path.is_file(), "asset_file_missing:" + key)
        expected = manifest["source_sha256" if key == "source_path"
                              else "runtime_sha256"]
        _require(file_digest(path) == expected, "asset_hash_mismatch:" + key)
    return {
        "adapter": manifest["adapter"],
        "channels": manifest["channels"],
        "executed": False,
        "frame_samples": manifest["frame_samples"],
        "imported": False,
        "license_id": manifest["license_id"],
        "loaded": False,
        "pinned_source": True,
        "sample_format": manifest["sample_format"],
        "sample_rate_hz": manifest["sample_rate_hz"],
        "source_commit": manifest["source_commit"],
        "status": "identity_validated_only_do_not_qualify",
        "verified_without_execution": True,
    }


def caller_asset_report() -> Dict[str, Any]:
    workspace_manifest = SOURCE_ROOT / "data/manifests/auxiva.json"
    return {
        "absent_behavior": "reject_before_processing",
        "asset_is_caller_owned": True,
        "asset_is_vendored": False,
        "contract_id": "audio-sdk/auxiva/caller-supplied-asset/0.1",
        "executed": False,
        "imported": False,
        "loaded": False,
        "manifest_present": workspace_manifest.is_file(),
        "present_behavior": "validate_identity_and_geometry_only; do_not_load_or_execute",
        "required_fields": sorted(CALLER_ASSET_FIELDS),
        "status": "blocked",
        "workspace_manifest": "data/manifests/auxiva.json",
    }


def external_artifacts() -> Dict[str, Any]:
    paths = {
        "source_checkout": SOURCE_ROOT / "data/checkouts/auxiva",
        "runtime_env": SOURCE_ROOT / "data/envs/auxiva",
        "weights": SOURCE_ROOT / "data/models/auxiva",
        "adapter": SOURCE_ROOT / "adapters/auxiva",
    }
    present = {name: path.exists() for name, path in paths.items()}
    return {
        "checked_paths": {name: str(path.relative_to(SOURCE_ROOT))
                          for name, path in paths.items()},
        "present": present,
        "any_present": any(present.values()),
        "status": "blocked",
        "note": "Observed presence would not be runtime admission, parity or rights evidence.",
    }


# ---------------------------------------------------------------------------
# Adverse rejection matrix
# ---------------------------------------------------------------------------

def _reject_code(callable_: Any) -> str:
    try:
        callable_()
    except Reject as error:
        return error.code
    return "ACCEPTED"


def adverse_rejections() -> List[Dict[str, Any]]:
    session = DemixSession()
    first, second = source_signals()
    mixture = mix_sources(first, second)
    channels = [mixture[0][:32], mixture[1][:32]]
    before = session.snapshot()
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    source_file = root / "source.bin"
    runtime_file = root / "runtime.bin"
    source_file.write_bytes(b"auxiva-source-placeholder")
    runtime_file.write_bytes(b"auxiva-runtime-placeholder")
    manifest = {
        "adapter": "auxiva",
        "channels": 2,
        "frame_samples": 160,
        "license_id": "caller-declared",
        "permutation_reference": "caller_labels",
        "runtime_path": str(runtime_file),
        "runtime_sha256": file_digest(runtime_file),
        "sample_format": "float32",
        "sample_rate_hz": 16000,
        "source_commit": "0" * 40,
        "source_path": str(source_file),
        "source_sha256": file_digest(source_file),
    }
    cases: List[Tuple[str, Any]] = [
        ("duplicate_json_key", lambda: parse_strict_json('{"a":1,"a":2}')),
        ("nan_json_constant", lambda: parse_strict_json('{"a":NaN}')),
        ("infinity_json_constant", lambda: parse_strict_json('{"a":Infinity}')),
        ("malformed_json", lambda: parse_strict_json("{")),
        ("config_missing_field",
         lambda: validate_config({key: value for key, value in DEFAULT_CONFIG.items()
                                  if key != "clock_ppm"})),
        ("config_extra_field",
         lambda: validate_config({**DEFAULT_CONFIG, "extra": 1})),
        ("config_8000_hz",
         lambda: validate_config({**DEFAULT_CONFIG, "sample_rate_hz": 8000})),
        ("config_mono",
         lambda: validate_config({**DEFAULT_CONFIG, "channels": 1})),
        ("config_256_frame",
         lambda: validate_config({**DEFAULT_CONFIG, "frame_samples": 256})),
        ("config_int16",
         lambda: validate_config({**DEFAULT_CONFIG, "sample_format": "int16"})),
        ("config_clock_drift",
         lambda: validate_config({**DEFAULT_CONFIG, "clock_ppm": 1})),
        ("config_bool_rate",
         lambda: validate_config({**DEFAULT_CONFIG, "sample_rate_hz": True})),
        ("geometry_duplicate_mic",
         lambda: validate_geometry({**GEOMETRY, "microphones": [
             {"id": "m0", "position_nm": [0, 0, 0]},
             {"id": "m0", "position_nm": [1, 0, 0]}]})),
        ("geometry_non_integer_position",
         lambda: validate_geometry({**GEOMETRY, "microphones": [
             {"id": "m0", "position_nm": [0, 0, 0]},
             {"id": "m1", "position_nm": [1.5, 0, 0]}]})),
        ("geometry_position_out_of_range",
         lambda: validate_geometry({**GEOMETRY, "microphones": [
             {"id": "m0", "position_nm": [0, 0, 0]},
             {"id": "m1", "position_nm": [MAX_POSITION_NM + 1, 0, 0]}]})),
        ("geometry_non_normalizable_direction",
         lambda: validate_geometry({**GEOMETRY, "source_direction": [1, 1, 0]})),
        ("geometry_unknown_reference",
         lambda: validate_geometry({**GEOMETRY, "reference_mic_id": "m9"})),
        ("matrix_wrong_shape", lambda: validate_matrix([[1, 0]])),
        ("matrix_singular", lambda: validate_matrix([[1, 1], [1, 1]])),
        ("matrix_nonfinite", lambda: validate_matrix([[1, 0], [0, "NaN"]])),
        ("matrix_bool_entry", lambda: validate_matrix([[True, 0], [0, 1]])),
        ("channels_length_mismatch", lambda: validate_channels(
            [[0.0, 1.0], [0.0]])),
        ("channels_empty", lambda: validate_channels([[], []])),
        ("channels_nonfinite", lambda: validate_channels(
            [[0.0, float("nan")], [0.0, 1.0]])),
        ("channels_out_of_range", lambda: validate_channels(
            [[0.0, MAX_ABS_SAMPLE + 1], [0.0, 1.0]])),
        ("channels_string_sample", lambda: validate_channels(
            [[0.0, "1"], [0.0, 1.0]])),
        ("channels_bool_sample", lambda: validate_channels(
            [[0.0, True], [0.0, 1.0]])),
        ("reset_epoch_zero", lambda: session.reset(0)),
        ("reset_epoch_negative", lambda: session.reset(-1)),
        ("caller_manifest_missing_field",
         lambda: validate_caller_asset({key: value for key, value in manifest.items()
                                        if key != "source_sha256"})),
        ("caller_manifest_relative_path",
         lambda: validate_caller_asset({**manifest, "source_path": "source.bin"})),
        ("caller_manifest_bad_commit",
         lambda: validate_caller_asset({**manifest, "source_commit": "abc"})),
        ("caller_manifest_wrong_rate",
         lambda: validate_caller_asset({**manifest, "sample_rate_hz": 48000})),
        ("caller_manifest_wrong_channels",
         lambda: validate_caller_asset({**manifest, "channels": 1})),
        ("caller_manifest_bad_hash",
         lambda: validate_caller_asset({**manifest, "source_sha256": "0" * 64})),
        ("caller_manifest_extra_field",
         lambda: validate_caller_asset({**manifest, "extra": 1})),
    ]
    records: List[Dict[str, Any]] = []
    for case_id, callable_ in cases:
        code = _reject_code(callable_)
        after = session.snapshot()
        records.append({
            "case_id": case_id,
            "code": code,
            "state_unchanged": before == after,
            "status": "rejected" if code != "ACCEPTED" else "accepted",
        })
    temporary.cleanup()
    return records


# ---------------------------------------------------------------------------
# Release gates, blockers, profile and board identity
# ---------------------------------------------------------------------------

def release_gates() -> List[Dict[str, Any]]:
    return [
        {
            "id": "RG-01",
            "requirement": "Exact pinned AuxIVA source or runtime with immutable revision, license identity and declared adapter settings.",
            "status": "blocked",
        },
        {
            "id": "RG-02",
            "requirement": "Isolated hash-pinned runtime admission, reproducible build and verified caller-owned asset identity without execution claims.",
            "status": "blocked",
        },
        {
            "id": "RG-03",
            "requirement": "Artifact, training-data, source, corpus, redistribution, product-use and derivative-output rights with complete notices.",
            "status": "blocked",
        },
        {
            "id": "RG-04",
            "requirement": "Exact-runtime multi-channel output vector and byte-level parity at the declared geometry, rate and hop.",
            "status": "blocked",
        },
        {
            "id": "RG-05",
            "requirement": "Multi-channel source-permutation qualification on label-bearing held-out mixtures, including ambiguous and swapped cases.",
            "status": "blocked",
        },
        {
            "id": "RG-06",
            "requirement": "Output scale, channel identity and deterministic reset qualification with a declared normalization policy.",
            "status": "blocked",
        },
        {
            "id": "RG-07",
            "requirement": "Rights-cleared held-out spatial separation scoring including leakage, target damage, channel loss and room/reference change strata.",
            "status": "blocked",
        },
        {
            "id": "RG-08",
            "requirement": "Target-device timing, opt-in provider intake, descriptor review, independent exact-head review and default/release approval.",
            "status": "blocked",
        },
    ]


def exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "pinned_auxiva_source_or_runtime_absent",
            "requirement": "Supply one exact licensed AuxIVA implementation or runtime, its immutable revision, source/license identity, build or archive identity and declared adapter settings.",
            "state": "No AuxIVA package, source tree, runtime, adapter, pinned revision or numeric output is staged. The only catalog mention places AuxIVA inside the separate H-GTCRN bundle; it does not identify a standalone AuxIVA source, revision or license.",
        },
        {
            "id": "multi_channel_permutation_and_scale_evidence_absent",
            "requirement": "Supply exact-runtime outputs on label-bearing multi-channel mixtures and qualify source permutation, output scale, channel identity and reset determinism.",
            "state": "The synthetic fixture shows a row-permuted inverse is equally exact and a scaled inverse is equally exact under scale-invariant scoring. No external label assignment, permutation resolver, normalization policy or exact-runtime output exists.",
        },
        {
            "id": "rights_cleared_multichannel_corpus_absent",
            "requirement": "Supply a rights-cleared multi-channel separated-speech corpus with source/reference labels, consent, array geometry, room conditions, leakage and target-damage strata.",
            "state": "No real multi-channel audio, speaker/source label, consent or usage grant, geometry manifest, corpus terms or held-out split is staged.",
        },
        {
            "id": "timing_and_task_matched_scoring_absent",
            "requirement": "Measure target-device timing and score task-matched held-out separation with independent metrics or permitted listening and independent review.",
            "state": "No device clock, deadline, RTF, memory result, held-out score, listening test, benchmark, provider intake or release approval exists; no result may qualify.",
        },
    ]


def spatial_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "geometry_and_layout": {
                "status": "synthetic_only",
                "evidence": "Frozen integer nanometre 3-microphone linear/planar fixture with an exactly normalizable direction; no measured array, orientation or device layout.",
            },
            "timestamp_calibration": {
                "status": "synthetic_only",
                "evidence": "Explicit integer capture offsets and zero clock drift; one-sample TDOA is exact at 16 kHz. No device clock was measured.",
            },
            "source_target_reference_conditions_and_permissions": {
                "status": "blocked",
                "evidence": "No real multi-channel recording, source/target condition, consent or usage permission is staged.",
            },
            "task_matched_heldout_localization_activity_extraction": {
                "status": "blocked",
                "evidence": "No held-out source labels, separation output or permutation-resolved scorer exists; the fixture is synthetic only.",
            },
            "leakage_target_damage_channel_loss": {
                "status": "blocked",
                "evidence": "No real target, interference, leakage or channel-loss stratum is available; synthetic crosstalk is not a qualification result.",
            },
            "room_reference_changes": {
                "status": "blocked",
                "evidence": "No room, RIR or reference-condition change is measured; WPE and H-GTCRN evidence are not pooled into this package.",
            },
        },
        "mapped_cases": {
            "matched_inverse_control": "frozen exact inverse of the declared synthetic mixing matrix",
            "permuted_inverse_control": "row-permuted exact inverse, showing unresolved source assignment",
            "scaled_inverse_control": "doubled exact inverse, showing unresolved output scale",
            "identity_control": "raw synthetic mixture passthrough",
            "blind_decorrelation_control": "fixed-step second-order decorrelation, not AuxIVA",
            "missing_or_delayed_evidence": "explicit rejection/missing evidence only; no real mixture",
        },
        "not_applicable": [
            "listening quality, benchmark scoring and release support",
            "real source localization, tracking, beamforming or target extraction",
            "echo attenuation and near-end damage",
        ],
    }


def h_gtcrn_separation() -> Dict[str, Any]:
    return {
        "bundled_component": "H-GTCRN",
        "h_gtcrn_adapter_present": False,
        "h_gtcrn_checkpoint_present": False,
        "h_gtcrn_evidence_pooled": False,
        "h_gtcrn_source_pinned": False,
        "note": "The census describes H-GTCRN as a two-microphone bundle combining GTCRN, FD-WPE, AuxIVA and spatial features. This package isolates AuxIVA, does not import H-GTCRN and does not reuse its adapter, checkpoint, runtime or evidence.",
        "this_package_uses_h_gtcrn": False,
    }


def reference_record() -> Dict[str, Any]:
    return {
        "adapter_present": False,
        "algorithm_family": "independent_vector_analysis",
        "algorithm_variant": "AuxIVA auxiliary-function IVA (catalogued, not staged)",
        "catalogued_candidate_used": False,
        "exact_numeric_output_present": False,
        "implementation_present": False,
        "license_identity": None,
        "pinned_revision": None,
        "runtime_present": False,
        "source_present": False,
        "status": "blocked",
        "surrogate_is_candidate": False,
    }


def format_record() -> Dict[str, Any]:
    return {
        "algorithm_latency_samples": 0,
        "algorithm_latency_ms": 0,
        "declared_channels": CHANNELS,
        "declared_frame_samples": FRAME_SAMPLES,
        "declared_hop_samples": HOP_SAMPLES,
        "declared_sample_format": "float32",
        "declared_sample_rate_hz": SAMPLE_RATE_HZ,
        "fixture_samples": TOTAL_SAMPLES,
        "proposed_stft_window": 512,
        "sdk_v0_channels": 1,
        "sdk_v0_frame_samples": 160,
        "sdk_v0_geometry_preserved": True,
        "sdk_v0_sample_format": "f32",
        "sdk_v0_sample_rate_hz": 16000,
    }


def scope_record() -> Dict[str, Any]:
    return {
        "asset_bundled": False,
        "benchmark_claim": False,
        "device_timing": False,
        "listening": False,
        "network_access": False,
        "numeric_parity_claim": False,
        "permutation_qualified": False,
        "processor_exposure": False,
        "provider_registration": False,
        "public_default": False,
        "real_corpus": False,
        "real_multichannel_audio": False,
        "release_claim": False,
        "runtime_invocation": False,
        "scale_qualified": False,
        "synthetic_only": True,
        "task_local_only": True,
        "weights": False,
    }


def boundary_record() -> Dict[str, Any]:
    return {
        "adapter_json_added": False,
        "asset_bundled": False,
        "audio_added": False,
        "ci_change": False,
        "corpus_added": False,
        "default_selected": False,
        "descriptor_registry_change": False,
        "enabled_by_default": False,
        "installed_v0_behavior_change": False,
        "native_engine_built": False,
        "onnxruntime_invoked": False,
        "processor_exposure": False,
        "provider_registration": False,
        "public_api_abi_change": False,
        "readiness_json_added": False,
        "registered": False,
        "sdk_data_dir_added": False,
        "shared_build_or_ci_change": False,
        "weights_vendored": False,
    }


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
    digest = object_digest(stable_fields)
    _require(digest == BOARD_ROW_STABLE_SHA256, "unexpected_stable_board_identity")
    return {
        "stable_fields": stable_fields,
        "stable_sha256": digest,
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


def _profile_blockers(profile: Dict[str, Any]) -> List[str]:
    return sorted(name for name, item in profile["required_items"].items()
                  if item["status"] == "blocked")


def _case_matrix_digest(controls: Sequence[Dict[str, Any]],
                        blind: Dict[str, Any]) -> str:
    matrix = [
        {
            "case_id": case["case_id"],
            "exact": case["exact"],
            "output_digests": case["output_digests"],
            "permutation": case["permutation"],
        }
        for case in controls
    ]
    matrix.append({
        "case_id": "blind_decorrelation_control",
        "matrix": blind["matrix"],
        "output_digests": blind["outputs"]["output_digests"],
    })
    return object_digest(matrix)


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()
    sources = source_signals()
    controls = control_cases()
    blind = blind_decorrelation(sources)
    adverse = adverse_rejections()
    matrix_digest = _case_matrix_digest(controls, blind)
    profile = spatial_profile()
    gates = release_gates()
    blockers = exact_blockers()
    first, second = sources
    energy_first = sum(value * value for value in first)
    energy_second = sum(value * value for value in second)

    return {
        "acceptance_profile": profile,
        "adverse_all_rejected": all(item["status"] == "rejected"
                                    and item["state_unchanged"]
                                    for item in adverse),
        "adverse_rejections": adverse,
        "base_commit": BASE_COMMIT,
        "blind_decorrelation_control": blind,
        "board_row": board_row(),
        "boundary": boundary_record(),
        "boundary_pins": dict(BOUNDARY_PINS),
        "branch": BRANCH,
        "caller_asset": caller_asset_report(),
        "component": COMPONENT,
        "controls": controls,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": blockers,
        "external_artifacts": external_artifacts(),
        "fixture": {
            "fixture_id": "auxiva-synthetic-two-source-two-mic-v1",
            "inverse_matrix": [list(row) for row in INVERSE_MATRIX],
            "mixing_matrix": [list(row) for row in MIXING_MATRIX],
            "samples": TOTAL_SAMPLES,
            "source_a": dict(SOURCE_A),
            "source_b": dict(SOURCE_B),
            "source_correlation": correlation(first, second),
            "source_energy": [energy_first, energy_second],
            "synthetic_only": True,
        },
        "format": format_record(),
        "geometry": geometry_record(),
        "h_gtcrn_separation": h_gtcrn_separation(),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "permutation_qualification": {
            "heldout_labels_present": False,
            "observed_on_synthetic": {
                "assignment_margin_db":
                    controls[0]["permutation"]["assignment_margin_db"],
                "matched_assignment":
                    controls[0]["permutation"]["assignment"],
                "permuted_assignment":
                    controls[1]["permutation"]["assignment"],
                "permuted_case_exact": controls[1]["exact"],
                "score_alone_resolves_permutation": False,
            },
            "reason": "A row-permuted inverse is equally exact on the synthetic fixture; no label-bearing held-out resolver or exact-runtime output exists.",
            "required": True,
            "status": "blocked",
        },
        "qualification": {
            "all_required_results_present": False,
            "exact_runtime_outputs_present": False,
            "exact_source_present": False,
            "listening": False,
            "missing_result_promoted": False,
            "permutation_qualified": False,
            "qualifies": False,
            "reason": "Exact source/runtime, rights-cleared multi-channel cohort, permutation/scale qualification, timing and independent review are all absent.",
            "rights_cleared_cohort": False,
            "scale_qualified": False,
            "status": QUALIFICATION,
            "timing_measured": False,
        },
        "reference": reference_record(),
        "reopen_condition": REOPEN_CONDITION,
        "repeatability": {
            "byte_identical": True,
            "case_matrix_digests": [matrix_digest, matrix_digest, matrix_digest],
            "runs": 3,
        },
        "repository": REPOSITORY,
        "reset": reset_check(),
        "scale_qualification": {
            "reason": "Scale-invariant SI-SDR scores both the exact inverse gain and a doubled inverse as exact; no normalization policy is declared.",
            "required": True,
            "status": "blocked",
            "synthetic_observation": {
                "exact_gain": EXACT_GAIN,
                "scaled_case_exact_up_to_gain": controls[2]["exact"],
                "scaled_gain": SCALED_GAIN,
                "scale_resolved": False,
                "si_sdr_scale_invariant": True,
            },
        },
        "schema_id": REPORT_SCHEMA,
        "scope": scope_record(),
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "streaming": streaming_check(sources),
        "task": TASK_ID,
        "title": TITLE,
        "profile": PROFILE,
        "profile_blockers": _profile_blockers(profile),
        "release_gates": gates,
        "surrogate": {
            "algorithm": "frozen integer mixing inverse and fixed-step second-order decorrelation",
            "is_auxiva": False,
            "is_h_gtcrn": False,
            "is_learned": False,
            "qualifies_candidate": False,
            "uses_weights": False,
        },
    }


def artifact_pins(report_digest: str) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in ARTIFACT_FILES:
        if name in ("contract.json", "report.json"):
            continue
        pins[TASK_PREFIX + name] = file_digest(HERE / name)
    pins[TASK_PREFIX + "report.json"] = report_digest
    return pins


def build_contract(report_digest: str) -> Dict[str, Any]:
    report = build_report()
    return {
        "acceptance_profile": report["acceptance_profile"],
        "artifact_pins": artifact_pins(report_digest),
        "base_commit": BASE_COMMIT,
        "board_row": report["board_row"],
        "boundary": report["boundary"],
        "boundary_pins": report["boundary_pins"],
        "branch": BRANCH,
        "caller_asset_contract": {
            "absent_behavior": "reject_before_processing",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "contract_id": "audio-sdk/auxiva/caller-supplied-asset/0.1",
            "present_behavior": "validate_identity_and_geometry_only; do_not_load_or_execute",
            "required_fields": sorted(CALLER_ASSET_FIELDS),
            "separate_archive_required": True,
        },
        "component": COMPONENT,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": report["exact_blockers"],
        "format": report["format"],
        "h_gtcrn_separation": report["h_gtcrn_separation"],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no AuxIVA, H-GTCRN, model, weight or runtime is downloaded, copied, loaded or executed",
            "the synthetic surrogate is not AuxIVA and cannot qualify the candidate",
            "source permutation and output scale remain unresolved",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
        "negative_claims": report["negative_claims"],
        "permutation_qualification": report["permutation_qualification"],
        "profile": PROFILE,
        "qualification_status": QUALIFICATION,
        "reference": report["reference"],
        "release_gates": report["release_gates"],
        "reopen_condition": REOPEN_CONDITION,
        "repository": REPOSITORY,
        "reviewer": REVIEWER,
        "scale_qualification": report["scale_qualification"],
        "schema_id": CONTRACT_SCHEMA,
        "scope": report["scope"],
        "source_pins": report["source_pins"],
        "status": STATUS,
        "task": TASK_ID,
        "task_prefix": TASK_PREFIX,
        "title": TITLE,
        "verification_profile": PROFILE,
    }


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-AUXIVA; source: paths are workspace-relative, "
        "others SDK-worktree-relative."
    ]
    for path, digest in SOURCE_PINS.items():
        lines.append(f"{digest}  source:{path}")
    for path, digest in BOUNDARY_PINS.items():
        lines.append(f"{digest}  {path}")
    for name in PIN_FILES:
        full = HERE / name
        _require(full.is_file(), "missing_artifact:" + name)
        lines.append(f"{file_digest(full)}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")
