# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Bounded EARS preservation-screen and scorer harness.

This module is task-local, standard-library-only evidence for
``SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS``.  It defines the exact
manifest, metric and admission rules that a blind EARS preservation screen
needs, and it exercises those rules on an authored integer Q15 fixture.

It is **not** the historical EARS run, the EARS archive, pystoi, DNSMOS, a
denoiser, a scorer runtime, a listening test or a release adapter.  The exact
licensed scorer, corpus and run outputs are absent from the pinned workspace,
so every real-screen path fails closed and no result qualifies.

Metric definitions
------------------
* SI-SDR is the zero-mean scale-invariant SDR of the SI-SDR evidence package:
  ``10*log10(sum(proj^2)/sum((y0-proj)^2))`` with
  ``proj = <y0,s0>/<s0,s0> * s0``.  It is computed from exact integer dot
  products before the logarithm.  A perfect reconstruction is capped at
  ``MAX_MILLIDB``; the cap is reported as a cap, never as an exact value.
* SNR is uncentered ``10*log10(sum(s^2)/sum((y-s)^2))``.
* Level change is ``10*log10(sum(y^2)/sum(s^2))`` in millidB.
* RMSE is ``floor(1000*sqrt(mean((y-s)^2)))`` Q15 milli-units.
* Lag is a deterministic raw cross-correlation search within the declared
  bound; ties prefer the smallest absolute lag.
* STOI and DNSMOS P.835 are never approximated.  They remain blocked until
  the exact pinned scorer artifacts are staged and hash-admitted.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import struct
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]

TASK_ID = "SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS"
TITLE = "EARS preservation screen and scorer harness"
COMPONENT = "ears-preservation-screen-and-scorer-harness"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS"
BASE_COMMIT = "b43a7e13175949cda78f0ea64953e4a585d43c67"
TASK_PREFIX = "docs/task-evidence/ears-preservation-screen-and-scorer-harness/"
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SAMPLE_RATE_HZ = 16000
ORIGINAL_SAMPLE_RATE_HZ = 48000
FRAME_SAMPLES = 160
EXPECTED_EARS_ITEMS = 743
MAX_ITEMS = 743
MAX_OUTPUTS_PER_ITEM = 8
MAX_ITEM_SAMPLES = SAMPLE_RATE_HZ * 600
MAX_LAG_SAMPLES = SAMPLE_RATE_HZ // 10  # the historical +/-100 ms bound
MAX_MILLIDB = 999_000
MIN_MILLIDB = -999_000
Q15_MIN = -32768
Q15_MAX = 32767
Q15_FULL_SCALE = 32768
MAX_ABS_Q15 = 32768
MAX_SIGNAL_SAMPLES = SAMPLE_RATE_HZ * 600

MANIFEST_SCHEMA = "audio-sdk/ears-preservation-screen-manifest/0.1"
REPORT_SCHEMA = "audio-sdk/ears-preservation-screen-report/0.1"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
FIXTURE_ID = "ears-preservation-integer-q15-control-v1"
PREPARATION_ID = "integer-q15-lcg-triangle-v1"
BOARD_ROW_STABLE_SHA256 = (
    "ef242b21c857177d3d5c93523db26ab0371ee5399fc34a4f4c5297b706587117"
)

ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
SAMPLE_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,95}\Z")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")

#: Stable read-only source pins, relative to the enclosing workspace root.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/voice-enhancement-20261101/agent-ears-preservation-743/REPORT.md":
        "d3a2206056eac182f62e3c7d3ea6f249b65ecdb001d5b847142d87ccc5627467",
    "research/voice-enhancement-20261101/agent-ears-preservation-743/prepare_inputs.py":
        "b26b10a0b8c8f07630dc58f3e948f7817937b60568c635e2663701d6dd73326d",
    "research/voice-enhancement-20261101/agent-ears-preservation-743/run_candidate.py":
        "8ece3bf4f7572d77107d6a0867c47d9ea338a1775a1f2c8d33cb06b3ebb40f55",
    "research/voice-enhancement-20261101/agent-ears-preservation-743/score_results.py":
        "8d5dec8dcf43937bbfbca2c35075c6f19601033a1e04fa2e6cf74b5daa313974",
    "research/voice-enhancement-20261101/agent-dnsmos-ears-743/REPORT.md":
        "613f5448418f84a354366de412ecfd8f92a7143b7cea8549899e51dbcb357d21",
    "research/voice-enhancement-20261101/agent-dnsmos-ears-743/score_existing_outputs.py":
        "0e0d89720231a161cf4c55dfdbc4c0995a30e377fb97796c5893dcdafd5e8a4b",
    "research/ears_blind_noise_screen_20261027.md":
        "d521ffc71e5f9b4f77949760578fc0f7f6773b2b1f4f06680f08448d8793ce2e",
    "research/noise_suppression_pilot_20261027.md":
        "90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae",
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
    "docs/task-evidence/stoi-estoi/README.md":
        "a09db6355c4c54046322b194fea71697aac76c0d111fa5aeca193ead367dee72",
    "docs/task-evidence/stoi-estoi/report.json":
        "a74820ff3e42f80d5ab06038de6ec70989876c6d91b98b34dc059ed2a6858f82",
    "docs/task-evidence/si-sdr-sdr-and-snr/README.md":
        "16bc05e63afdb209ba2a9657b7977c29f7d15f9eb3d6e8d24e316b3d2ef671a3",
}

SOURCE_FILES = tuple(SOURCE_PINS)
BOUNDARY_FILES = tuple(BOUNDARY_PINS)

#: Files that are self-pinned in contract.json and SOURCES.sha256.
ARTIFACT_FILES = (
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

#: Files regenerated by run.py; contract.json and SOURCES.sha256 are excluded
#: because pinning either inside itself would be self-referential.
PIN_FILES = ARTIFACT_FILES

MANIFEST_FIELDS = {
    "schema_id",
    "corpus_id",
    "corpus_license",
    "corpus_archive_sha256",
    "preparation_recipe_sha256",
    "sample_rate_hz",
    "original_sample_rate_hz",
    "frame_samples",
    "expected_items",
    "items",
    "scorer_pins",
}
ITEM_FIELDS = {
    "sample_id",
    "original_sha256",
    "input_16k_sha256",
    "input_16k_path",
    "duration_samples",
    "outputs",
}
OUTPUT_FIELDS = {
    "candidate_id",
    "output_sha256",
    "output_path",
    "output_samples",
}
SCORER_FIELDS = {
    "scorer_id",
    "version",
    "source_sha256",
    "license_id",
    "status",
}
SCREEN_ROW_FIELDS = {
    "sample_id",
    "candidate_id",
    "si_sdr_millidb",
    "snr_millidb",
    "rmse_millisample",
    "peak_milli",
    "clipped_samples",
    "lag_samples",
}

REAL_RUN_DIR = "data/runs/voice-enhancement-20261101-ears-preservation-743"
REAL_REQUIRED = {
    REAL_RUN_DIR + "/inputs/manifest.json":
        "1b21465dd02ede9089f7aabcc97ecc20fc562411988a170e5060a157ebe9f121",
    REAL_RUN_DIR + "/fastenhancer_small-results.json":
        "5ff580f0d8aa5a5776e2c558e62b3294925709342d5cd7e435a605733f6cf2a8",
    REAL_RUN_DIR + "/deepfilternet3-results.json":
        "7d61a0c9430e4370d95ad66cd44fa74d981b4b0b811efc03534813d8fb54fcfb",
}
REAL_CORPUS_SEARCH_ROOTS = (
    "data/ears",
    "data/corpora/ears",
    "data/corpora/EARS",
    "data/checkouts/ears",
    "data/checkouts/EARS",
)
PYSTOI_STOI_SHA256 = (
    "482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658"
)
PYSTOI_UTILS_SHA256 = (
    "0222df0354a248ccc7f8525eda9bda9da815e5d60106f611a5f4750d1ba7f321"
)
DNSMOS_SCRIPT_SHA256 = (
    "abcfd3ee61b37a45728b2c7faaed8ced710e11e01d0a58daf4377363bc719fbb"
)
DNSMOS_SIG_SHA256 = (
    "d2fbdb293bc2366dfbae2b7477c490f981d24a8b4405efd3c11787569c6549d7"
)
DNSMOS_BAK_OVR_SHA256 = (
    "5f335c90994618150192a656a474bcf8a9cbcedbc47965494ba8da79605d1308"
)
DNSMOS_SCRIPT_PATH = (
    "data/envs/deepfilternet3/lib/python3.10/site-packages/df/scripts/dnsmos.py"
)


class Reject(ValueError):
    """Fail-closed evidence rejection with a stable code."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise Reject(code)


# ---------------------------------------------------------------------------
# Strict JSON, canonical bytes and digests
# ---------------------------------------------------------------------------

def _strict_pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
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


def signal_digest(values: Sequence[int]) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(struct.pack("<h", int(value)))
    return digest.hexdigest()


def _is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _as_int(value: Any, code: str, low: int, high: int) -> int:
    if not _is_plain_int(value) or value < low or value > high:
        raise Reject(code)
    return value


def _as_str(value: Any, code: str, min_length: int = 1,
            max_length: int = 256) -> str:
    if (not isinstance(value, str) or len(value) < min_length
            or len(value) > max_length):
        raise Reject(code)
    return value


def _as_id(value: Any, code: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        raise Reject(code)
    return value


def _as_sample_id(value: Any) -> str:
    if not isinstance(value, str) or not SAMPLE_ID_PATTERN.fullmatch(value):
        raise Reject("invalid_sample_id")
    return value


def _as_sha256(value: Any, code: str) -> str:
    if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
        raise Reject(code)
    return value


def _strict_keys(value: Any, expected: set, prefix: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise Reject("invalid_type:" + prefix)
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        raise Reject("strict_keys_mismatch:" + prefix + ":" + missing[0])
    if extra:
        raise Reject("strict_keys_mismatch:" + prefix + ":" + extra[0])
    return value


def _safe_source_path(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value:
        raise Reject(code)
    if value.startswith("/") or "\\" in value or ":" in value[:2]:
        raise Reject(code)
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise Reject(code)
    if not value.startswith("data/"):
        raise Reject(code)
    return value


# ---------------------------------------------------------------------------
# Exact Q15 preservation metrics
# ---------------------------------------------------------------------------

def _trunc_half(numerator: int, denominator: int = 2) -> int:
    if numerator >= 0:
        return numerator // denominator
    return -((-numerator) // denominator)


def _millidb(numerator: int, denominator: int) -> int:
    if numerator <= 0:
        return MIN_MILLIDB
    if denominator <= 0:
        return MAX_MILLIDB
    value = int(round(10_000.0 * (math.log10(numerator)
                                  - math.log10(denominator))))
    if value < MIN_MILLIDB:
        return MIN_MILLIDB
    if value > MAX_MILLIDB:
        return MAX_MILLIDB
    return value


def _validate_signal(values: Any, role: str) -> List[int]:
    if values is None:
        raise Reject("missing_input" if role == "reference"
                     else "missing_estimate")
    if not isinstance(values, list):
        raise Reject("invalid_type:" + role)
    if len(values) == 0:
        raise Reject("empty_signal:" + role)
    if len(values) > MAX_SIGNAL_SAMPLES:
        raise Reject("invalid_integer:length")
    checked: List[int] = []
    for value in values:
        if isinstance(value, bool):
            raise Reject("invalid_sample:" + role)
        if isinstance(value, float):
            if not math.isfinite(value):
                raise Reject("nonfinite_input:" + role)
            raise Reject("invalid_sample:" + role)
        if not isinstance(value, int):
            raise Reject("invalid_sample:" + role)
        if value < Q15_MIN or value > Q15_MAX:
            raise Reject("sample_out_of_range:" + role)
        checked.append(value)
    return checked


def estimate_lag(reference: Sequence[int], estimate: Sequence[int],
                 max_lag: int) -> int:
    """Deterministic raw cross-correlation lag, ties prefer smallest |lag|."""
    if not _is_plain_int(max_lag) or max_lag < 0 or max_lag > MAX_LAG_SAMPLES:
        raise Reject("invalid_integer:max_lag")
    length = len(reference)
    best_lag = 0
    best_score = -1
    for lag in range(-max_lag, max_lag + 1):
        start = -lag if lag < 0 else 0
        end = length if lag < 0 else length - lag
        total = 0
        for index in range(start, end):
            total += int(reference[index]) * int(estimate[index + lag])
        score = abs(total)
        if score > best_score or (score == best_score
                                  and abs(lag) < abs(best_lag)):
            best_score = score
            best_lag = lag
    return best_lag


def aligned_pair(reference: Sequence[int], estimate: Sequence[int],
                 lag: int) -> Tuple[List[int], List[int]]:
    if lag > 0:
        return list(reference[:-lag]), list(estimate[lag:])
    if lag < 0:
        return list(reference[-lag:]), list(estimate[:len(estimate) + lag])
    return list(reference), list(estimate)


def si_sdr_millidb(reference: Sequence[int], estimate: Sequence[int]) -> int:
    """Zero-mean scale-invariant SDR in millidB, exact before the log."""
    length = len(reference)
    _require(length == len(estimate) and length > 0, "length_mismatch")
    sum_reference = sum(reference)
    sum_estimate = sum(estimate)
    ref_energy = 0
    est_energy = 0
    cross = 0
    for index in range(length):
        ref = reference[index] * length - sum_reference
        est = estimate[index] * length - sum_estimate
        ref_energy += ref * ref
        est_energy += est * est
        cross += ref * est
    if ref_energy == 0:
        return MAX_MILLIDB if est_energy == 0 else MIN_MILLIDB
    if est_energy == 0:
        return MIN_MILLIDB
    target = cross * cross
    if target == 0:
        return MIN_MILLIDB
    error = est_energy * ref_energy - target
    if error <= 0:
        return MAX_MILLIDB
    return _millidb(target, error)


def snr_millidb(reference: Sequence[int], estimate: Sequence[int]) -> int:
    """Uncentered SNR in millidB."""
    _require(len(reference) == len(estimate) and len(reference) > 0,
             "length_mismatch")
    ref_energy = sum(value * value for value in reference)
    error_energy = sum((estimate[index] - reference[index]) ** 2
                       for index in range(len(reference)))
    if ref_energy == 0:
        return MAX_MILLIDB if error_energy == 0 else MIN_MILLIDB
    if error_energy == 0:
        return MAX_MILLIDB
    return _millidb(ref_energy, error_energy)


def level_change_millidb(reference: Sequence[int],
                         estimate: Sequence[int]) -> int:
    _require(len(reference) == len(estimate) and len(reference) > 0,
             "length_mismatch")
    ref_energy = sum(value * value for value in reference)
    est_energy = sum(value * value for value in estimate)
    if ref_energy == 0 and est_energy == 0:
        return 0
    return _millidb(est_energy, ref_energy)


def rmse_millisample(reference: Sequence[int],
                     estimate: Sequence[int]) -> int:
    _require(len(reference) == len(estimate) and len(reference) > 0,
             "length_mismatch")
    error_energy = sum((estimate[index] - reference[index]) ** 2
                       for index in range(len(reference)))
    return math.isqrt((error_energy * 1_000_000) // len(reference))


def peak_milli(values: Sequence[int]) -> int:
    if not values:
        raise Reject("empty_signal:estimate")
    return max(abs(value) for value in values) * 1000 // Q15_FULL_SCALE


def score_pair(reference: Sequence[int], estimate: Sequence[int],
               max_lag: int = 0, clip_threshold: int = Q15_FULL_SCALE
               ) -> Dict[str, Any]:
    """Score a preserved output against its same original input."""
    if not _is_plain_int(max_lag) or max_lag < 0 or max_lag > MAX_LAG_SAMPLES:
        raise Reject("invalid_integer:max_lag")
    if (not _is_plain_int(clip_threshold) or clip_threshold < 1
            or clip_threshold > Q15_FULL_SCALE):
        raise Reject("invalid_integer:clip_threshold")
    ref = _validate_signal(reference, "reference")
    est = _validate_signal(estimate, "estimate")
    if len(ref) != len(est):
        raise Reject("length_mismatch")
    lag = estimate_lag(ref, est, max_lag) if max_lag > 0 else 0
    aligned_ref, aligned_est = aligned_pair(ref, est, lag)
    valid_start = -lag if lag < 0 else 0
    return {
        "valid_start": valid_start,
        "valid_end": valid_start + len(aligned_ref),
        "overlap_samples": len(aligned_ref),
        "lag_samples": lag,
        "lag_microseconds": _trunc_half(lag * 125),
        "si_sdr_millidb": si_sdr_millidb(aligned_ref, aligned_est),
        "snr_millidb": snr_millidb(aligned_ref, aligned_est),
        "level_change_millidb": level_change_millidb(aligned_ref, aligned_est),
        "rmse_millisample": rmse_millisample(aligned_ref, aligned_est),
        "peak_milli": peak_milli(aligned_est),
        "clipped_samples": sum(1 for value in aligned_est
                               if abs(value) >= clip_threshold),
        "nonfinite_output_count": 0,
        "finite": True,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Frozen authored Q15 fixture and controls
# ---------------------------------------------------------------------------

SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"name": "clean_only_initial", "start": 0, "end": 1920,
     "speech": True, "noise_amplitude": 8, "seed": 11},
    {"name": "noisy_speech", "start": 1920, "end": 3840,
     "speech": True, "noise_amplitude": 900, "seed": 23},
    {"name": "noisy_speech_low_snr", "start": 3840, "end": 5760,
     "speech": True, "noise_amplitude": 2400, "seed": 37},
    {"name": "speech_pause_noise_only", "start": 5760, "end": 6720,
     "speech": False, "noise_amplitude": 1200, "seed": 41},
    {"name": "clean_only_final", "start": 6720, "end": 7680,
     "speech": True, "noise_amplitude": 8, "seed": 53},
    {"name": "noisy_speech_restore", "start": 7680, "end": 9600,
     "speech": True, "noise_amplitude": 1500, "seed": 67},
)
FIXTURE_LENGTH = 9600


def _triangle(index: int, period: int, amplitude: int) -> int:
    phase = index % (2 * period)
    if phase < period:
        return -amplitude + (2 * amplitude * phase) // period
    return amplitude - (2 * amplitude * (phase - period)) // period


def _speech_sample(index: int) -> int:
    return (_triangle(index, 80, 12000)
            + _triangle(index + 7, 32, 4000)
            + _triangle(index + 13, 160, 3000))


def _noise_sample(index: int, seed: int, amplitude: int) -> int:
    value = (index * 2654435761 + seed) & 0xFFFFFFFF
    value ^= value >> 16
    value = (value * 2246822519) & 0xFFFFFFFF
    value ^= value >> 13
    return (((value & 0xFFFF) - 32768) * amplitude) // 32768


def fixture_spec() -> Dict[str, Any]:
    return {
        "fixture_id": FIXTURE_ID,
        "preparation_id": PREPARATION_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "original_sample_rate_hz": ORIGINAL_SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "length_samples": FIXTURE_LENGTH,
        "segments": [dict(segment) for segment in SEGMENTS],
    }


def build_fixture() -> Dict[str, Any]:
    clean = [0] * FIXTURE_LENGTH
    mic = [0] * FIXTURE_LENGTH
    for segment in SEGMENTS:
        for index in range(segment["start"], segment["end"]):
            speech = _speech_sample(index) if segment["speech"] else 0
            noise = _noise_sample(index, segment["seed"],
                                  segment["noise_amplitude"])
            clean[index] = speech
            mic[index] = max(Q15_MIN, min(Q15_MAX, speech + noise))
    spec = fixture_spec()
    spec["signal_digests"] = {
        "clean": signal_digest(clean),
        "mic": signal_digest(mic),
    }
    spec["synthetic_only"] = True
    spec["is_ears_recording"] = False
    return {"clean": clean, "mic": mic, "spec": spec}


def validate_fixture(spec: Any) -> Dict[str, Any]:
    if not isinstance(spec, dict):
        raise Reject("invalid_type:fixture")
    required = {"fixture_id", "preparation_id", "sample_rate_hz",
                "original_sample_rate_hz", "frame_samples", "length_samples",
                "segments"}
    allowed = required | {"signal_digests", "synthetic_only",
                          "is_ears_recording"}
    _strict_keys(spec, allowed, "fixture")
    _require(spec["fixture_id"] == FIXTURE_ID, "fixture_id_mismatch")
    _require(spec["preparation_id"] == PREPARATION_ID,
             "preparation_id_mismatch")
    _require(spec["sample_rate_hz"] == SAMPLE_RATE_HZ,
             "unsupported_sample_rate")
    _require(spec["original_sample_rate_hz"] == ORIGINAL_SAMPLE_RATE_HZ,
             "unsupported_original_sample_rate")
    _require(spec["frame_samples"] == FRAME_SAMPLES,
             "unsupported_frame_samples")
    _require(spec["length_samples"] == FIXTURE_LENGTH,
             "fixture_length_mismatch")
    segments = spec["segments"]
    _require(isinstance(segments, list), "invalid_type:segments")
    _require(len(segments) == len(SEGMENTS), "fixture_segment_count")
    cursor = 0
    for actual, expected in zip(segments, SEGMENTS):
        _strict_keys(actual, set(expected), "fixture_segment")
        _require(actual["name"] == expected["name"],
                 "fixture_segment_order")
        _require(actual["start"] == cursor, "segment_gap")
        _require(actual["end"] > actual["start"], "invalid_segment")
        _require(actual["speech"] is expected["speech"],
                 "invalid_segment_speech")
        _require(_is_plain_int(actual["noise_amplitude"])
                 and 0 <= actual["noise_amplitude"] <= 4000,
                 "invalid_integer:noise_amplitude")
        _require(_is_plain_int(actual["seed"]), "invalid_integer:seed")
        cursor = actual["end"]
    _require(cursor == FIXTURE_LENGTH, "fixture_length_mismatch")
    return {"validated": True, "synthetic_only": True,
            "is_ears_recording": False}


def _shift(signal: Sequence[int], shift: int) -> List[int]:
    length = len(signal)
    if shift == 0:
        return list(signal)
    if shift > 0:
        return [0] * shift + list(signal[:length - shift])
    return list(signal[-shift:]) + [0] * (-shift)


def _control_outputs(mic: Sequence[int]) -> Dict[str, Dict[str, Any]]:
    noise_start, noise_end = 5760, 6720
    speech_start, speech_end = 0, 1920
    noise_quarter = list(mic)
    for index in range(noise_start, noise_end):
        noise_quarter[index] = mic[index] // 4
    speech_tenth = list(mic)
    for index in range(speech_start, speech_end):
        speech_tenth[index] = mic[index] // 10
    half_gain = [value // 2 for value in mic]
    dc_offset = [max(Q15_MIN, min(Q15_MAX, value + 500)) for value in mic]
    bounded = [max(-8000, min(8000, value)) for value in mic]
    return {
        "identity_input": {
            "kind": "identity",
            "description": "Unmodified input passthrough; exact identity control.",
            "values": list(mic),
        },
        "noise_only_quarter": {
            "kind": "noise_attenuation",
            "description": "Only the noise-only pause segment is attenuated "
                           "to one quarter; speech samples are unchanged.",
            "values": noise_quarter,
        },
        "speech_initial_tenth": {
            "kind": "speech_attenuation",
            "description": "Only the initial clean speech segment is "
                           "attenuated to one tenth; all other samples are "
                           "unchanged.",
            "values": speech_tenth,
        },
        "half_gain": {
            "kind": "gain_only",
            "description": "Every sample is halved; SI-SDR is scale "
                           "invariant while SNR and level change detect it.",
            "values": half_gain,
        },
        "dc_offset_plus_500": {
            "kind": "offset_only",
            "description": "Constant +500 Q15 offset with saturation at the "
                           "Q15 boundary; SI-SDR ignores it after centering.",
            "values": dc_offset,
        },
        "bounded_8000": {
            "kind": "saturation",
            "description": "Every sample is hard-bounded to +/-8000 Q15; "
                           "full-scale clipping is still zero.",
            "values": bounded,
        },
    }


def _region_rows(reference: Sequence[int], estimate: Sequence[int]
                 ) -> List[Dict[str, Any]]:
    rows = []
    for segment in SEGMENTS:
        sliced_ref = reference[segment["start"]:segment["end"]]
        sliced_est = estimate[segment["start"]:segment["end"]]
        metrics = score_pair(sliced_ref, sliced_est, max_lag=0)
        rows.append({
            "segment": segment["name"],
            "start": segment["start"],
            "end": segment["end"],
            "speech": segment["speech"],
            **metrics,
        })
    return rows


def preservation_controls() -> List[Dict[str, Any]]:
    fixture = build_fixture()
    mic = fixture["mic"]
    identity_global = score_pair(mic, mic, max_lag=16)
    controls = []
    for control_id, item in _control_outputs(mic).items():
        values = item["values"]
        global_metrics = score_pair(mic, values, max_lag=16)
        regions = _region_rows(mic, values)
        controls.append({
            "control_id": control_id,
            "kind": item["kind"],
            "description": item["description"],
            "is_candidate": False,
            "is_ears_candidate_output": False,
            "is_scorer_qualified": False,
            "qualifies": False,
            "bit_identical": values == mic,
            "bounded_samples": sum(1 for value in values
                                   if abs(value) == 8000),
            "output_peak_milli": peak_milli(values),
            "output_digest": signal_digest(values),
            "global": global_metrics,
            "regions": regions,
            "identity_delta": {
                key: global_metrics[key] - identity_global[key]
                for key in ("si_sdr_millidb", "snr_millidb",
                            "level_change_millidb",
                            "rmse_millisample", "peak_milli")
            },
        })
    return controls


def alignment_probes() -> Dict[str, Any]:
    mic = build_fixture()["mic"]
    probes = []
    for shift in (-16, -8, 0, 8, 16):
        metrics = score_pair(mic, _shift(mic, shift), max_lag=0)
        probes.append({
            "shift_samples": shift,
            "si_sdr_millidb": metrics["si_sdr_millidb"],
            "snr_millidb": metrics["snr_millidb"],
            "qualifies": False,
        })
    zero = [row for row in probes if row["shift_samples"] == 0][0]
    return {
        "probes": probes,
        "best_shift_samples": 0,
        "zero_shift_best": all(
            row["si_sdr_millidb"] < zero["si_sdr_millidb"]
            for row in probes if row["shift_samples"] != 0
        ),
        "max_lag_samples": 16,
        "historical_search_bound_samples": MAX_LAG_SAMPLES,
        "surrogate_content_delay_samples": 0,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Screen manifest contract and aggregation
# ---------------------------------------------------------------------------

def screen_manifest_spec() -> Dict[str, Any]:
    return {
        "schema_id": MANIFEST_SCHEMA,
        "real_expected_items": EXPECTED_EARS_ITEMS,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "original_sample_rate_hz": ORIGINAL_SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "max_outputs_per_item": MAX_OUTPUTS_PER_ITEM,
        "max_item_samples": MAX_ITEM_SAMPLES,
        "alignment_search_bound_samples": MAX_LAG_SAMPLES,
        "no_clean_reference": True,
        "reference": "same original input",
        "scorers": {
            "stoi": "pystoi 0.4.1 non-extended, exact pinned source",
            "dnsmos_p835": "exact pinned script and SIG/BAK-OVR ONNX models",
        },
        "listening": "separate, rights-gated, not part of the numeric screen",
    }


def _validate_scorer_pins(pins: Any) -> Dict[str, Any]:
    _strict_keys(pins, {"stoi", "dnsmos_p835"}, "scorer_pins")
    result = {}
    for name in ("stoi", "dnsmos_p835"):
        row = _strict_keys(pins[name], SCORER_FIELDS,
                           "scorer_pins." + name)
        _as_id(row["scorer_id"], "invalid_string:" + name + ".scorer_id")
        _as_str(row["version"], "invalid_string:" + name + ".version")
        _as_sha256(row["source_sha256"],
                   "invalid_sha256:scorer_pins." + name + ".source_sha256")
        _as_str(row["license_id"], "invalid_string:" + name + ".license_id")
        if row["status"] not in ("pinned", "blocked"):
            raise Reject("invalid_scorer_status:" + name)
        result[name] = dict(row)
    return result


def validate_manifest(manifest: Any,
                      expected_items: int | None = None) -> Dict[str, Any]:
    """Validate the exact screen manifest; never reads audio or runs a scorer."""
    _strict_keys(manifest, MANIFEST_FIELDS, "manifest")
    if manifest["schema_id"] != MANIFEST_SCHEMA:
        raise Reject("unsupported_manifest_schema")
    _as_sample_id(manifest["corpus_id"])
    _as_str(manifest["corpus_license"], "invalid_string:corpus_license",
            1, 128)
    _as_sha256(manifest["corpus_archive_sha256"],
               "invalid_sha256:corpus_archive_sha256")
    _as_sha256(manifest["preparation_recipe_sha256"],
               "invalid_sha256:preparation_recipe_sha256")
    _require(manifest["sample_rate_hz"] == SAMPLE_RATE_HZ,
             "unsupported_sample_rate")
    _require(manifest["original_sample_rate_hz"] == ORIGINAL_SAMPLE_RATE_HZ,
             "unsupported_original_sample_rate")
    _require(manifest["frame_samples"] == FRAME_SAMPLES,
             "unsupported_frame_samples")
    expected = _as_int(manifest["expected_items"],
                       "invalid_integer:expected_items", 1, MAX_ITEMS)
    items = manifest["items"]
    if not isinstance(items, list):
        raise Reject("invalid_type:items")
    if expected_items is not None:
        _require(_is_plain_int(expected_items) and expected_items > 0,
                 "invalid_integer:expected_items")
        _require(len(items) == expected_items,
                 "expected_item_count_mismatch:%d:%d"
                 % (expected_items, len(items)))
    _require(len(items) == expected, "item_count_mismatch:%d:%d"
             % (expected, len(items)))

    seen_samples: set = set()
    total_outputs = 0
    for item in items:
        _strict_keys(item, ITEM_FIELDS, "item")
        sample_id = _as_sample_id(item["sample_id"])
        if sample_id in seen_samples:
            raise Reject("duplicate_sample_id")
        seen_samples.add(sample_id)
        _as_sha256(item["original_sha256"],
                   "invalid_sha256:original_sha256")
        _as_sha256(item["input_16k_sha256"],
                   "invalid_sha256:input_16k_sha256")
        _safe_source_path(item["input_16k_path"],
                          "invalid_source_path:input_16k_path")
        duration = _as_int(item["duration_samples"],
                           "invalid_integer:duration_samples", 1,
                           MAX_ITEM_SAMPLES)
        outputs = item["outputs"]
        if not isinstance(outputs, list):
            raise Reject("invalid_type:outputs")
        if not outputs:
            raise Reject("empty_outputs")
        if len(outputs) > MAX_OUTPUTS_PER_ITEM:
            raise Reject("too_many_outputs")
        seen_candidates: set = set()
        for output in outputs:
            _strict_keys(output, OUTPUT_FIELDS, "output")
            candidate_id = _as_id(output["candidate_id"],
                                  "invalid_candidate_id")
            if candidate_id in seen_candidates:
                raise Reject("duplicate_candidate_id")
            seen_candidates.add(candidate_id)
            _as_sha256(output["output_sha256"],
                       "invalid_sha256:output_sha256")
            _safe_source_path(output["output_path"],
                              "invalid_source_path:output_path")
            output_samples = _as_int(output["output_samples"],
                                     "invalid_integer:output_samples", 1,
                                     MAX_ITEM_SAMPLES)
            _require(output_samples == duration,
                     "output_sample_count_mismatch")
            total_outputs += 1
    scorers = _validate_scorer_pins(manifest["scorer_pins"])
    return {
        "validated": True,
        "items": len(items),
        "outputs": total_outputs,
        "real_expected_items": EXPECTED_EARS_ITEMS,
        "scorer_status": {name: row["status"] for name, row in scorers.items()},
        "audio_read": False,
        "scorer_executed": False,
        "scored": False,
    }


def _resolve_under(root: Path, relative: str) -> Path:
    full = (root / relative).resolve()
    root_resolved = root.resolve()
    if root_resolved not in full.parents and full != root_resolved:
        raise Reject("path_escape:" + relative)
    return full


def validate_manifest_files(manifest: Dict[str, Any],
                            root: Path) -> Dict[str, Any]:
    """Hash-check the prepared input and output files; never decodes audio."""
    checked = 0
    for item in manifest["items"]:
        input_path = _resolve_under(root, item["input_16k_path"])
        if not input_path.is_file():
            raise Reject("missing_input_file:" + item["sample_id"])
        if file_digest(input_path) != item["input_16k_sha256"]:
            raise Reject("stale_input_digest:" + item["sample_id"])
        checked += 1
        for output in item["outputs"]:
            output_path = _resolve_under(root, output["output_path"])
            if not output_path.is_file():
                raise Reject("missing_output_file:" + item["sample_id"])
            if file_digest(output_path) != output["output_sha256"]:
                raise Reject("stale_output_digest:" + item["sample_id"])
            checked += 1
    return {"validated": True, "files_hashed": checked,
            "audio_decoded": False, "scorer_executed": False}


def _mean_millidb(values: Sequence[int]) -> int:
    total = sum(values)
    count = len(values)
    if total >= 0:
        return (2 * total + count) // (2 * count)
    return -((2 * (-total) + count) // (2 * count))


def _nearest_rank(values: Sequence[int], percentile: int) -> int:
    ordered = sorted(values)
    rank = (percentile * len(ordered) + 99) // 100
    index = max(0, min(len(ordered) - 1, rank - 1))
    return ordered[index]


def aggregate_preservation(rows: Any,
                           expected_items: int = EXPECTED_EARS_ITEMS
                           ) -> Dict[str, Any]:
    """Aggregate one candidate's per-item preservation rows.

    The aggregation is item-weighted and deterministic.  It performs no
    bootstrap, no population inference and no qualification.
    """
    if not isinstance(rows, list):
        raise Reject("invalid_type:rows")
    _require(len(rows) == expected_items,
             "screen_item_count_mismatch:%d:%d" % (expected_items, len(rows)))
    seen: set = set()
    metrics: Dict[str, List[int]] = {
        "si_sdr_millidb": [],
        "snr_millidb": [],
        "rmse_millisample": [],
        "peak_milli": [],
        "clipped_samples": [],
        "lag_samples": [],
    }
    candidate_ids: set = set()
    for row in rows:
        _strict_keys(row, SCREEN_ROW_FIELDS, "screen_row")
        sample_id = _as_sample_id(row["sample_id"])
        if sample_id in seen:
            raise Reject("duplicate_screen_sample")
        seen.add(sample_id)
        candidate_id = _as_id(row["candidate_id"], "invalid_candidate_id")
        candidate_ids.add(candidate_id)
        for key in ("si_sdr_millidb", "snr_millidb"):
            value = row[key]
            if isinstance(value, float) and not math.isfinite(value):
                raise Reject("nonfinite_metric:" + key)
            value = _as_int(value, "invalid_integer:" + key,
                            MIN_MILLIDB, MAX_MILLIDB)
            metrics[key].append(value)
        metrics["rmse_millisample"].append(
            _as_int(row["rmse_millisample"],
                    "invalid_integer:rmse_millisample", 0, 100_000_000))
        metrics["peak_milli"].append(
            _as_int(row["peak_milli"], "invalid_integer:peak_milli",
                    0, 1000))
        metrics["clipped_samples"].append(
            _as_int(row["clipped_samples"],
                    "invalid_integer:clipped_samples", 0, MAX_ITEM_SAMPLES))
        metrics["lag_samples"].append(
            _as_int(row["lag_samples"], "invalid_integer:lag_samples",
                    -MAX_LAG_SAMPLES, MAX_LAG_SAMPLES))
    _require(len(candidate_ids) == 1, "multiple_candidate_ids")
    candidate_id = sorted(candidate_ids)[0]
    summary = {
        "candidate_id": candidate_id,
        "n_items": len(rows),
        "expected_items": expected_items,
        "failed_items": [],
        "blocked_items": [],
        "population_inference": False,
        "bootstrap": "not_run",
        "qualifies": False,
        "metrics": {},
    }
    for key, values in metrics.items():
        summary["metrics"][key] = {
            "mean": _mean_millidb(values),
            "median": _nearest_rank(values, 50),
            "p95": _nearest_rank(values, 95),
            "min": min(values),
            "max": max(values),
        }
    return summary


# ---------------------------------------------------------------------------
# Exact scorer admission and the real-screen gate
# ---------------------------------------------------------------------------

def _find_pystoi() -> Dict[str, Any]:
    pattern = "data/envs/*/lib/python*/site-packages/pystoi"
    roots = sorted(SOURCE_ROOT.glob(pattern))
    found: Dict[str, Any] = {"roots": [str(path.relative_to(SOURCE_ROOT))
                                       for path in roots]}
    for root in roots:
        stoi_path = root / "stoi.py"
        utils_path = root / "utils.py"
        if stoi_path.is_file() and utils_path.is_file():
            found["stoi_sha256"] = file_digest(stoi_path)
            found["utils_sha256"] = file_digest(utils_path)
            break
    return found


def _find_dnsmos() -> Dict[str, Any]:
    script = SOURCE_ROOT / DNSMOS_SCRIPT_PATH
    found: Dict[str, Any] = {"script_path": DNSMOS_SCRIPT_PATH,
                             "script_present": script.is_file()}
    if script.is_file():
        found["script_sha256"] = file_digest(script)
    models = {}
    for name, expected in (("sig.onnx", DNSMOS_SIG_SHA256),
                           ("bak_ovr.onnx", DNSMOS_BAK_OVR_SHA256)):
        matches = sorted(SOURCE_ROOT.glob("data/models/**/" + name))
        matches += sorted(SOURCE_ROOT.glob("data/envs/**/" + name))
        rows = []
        for match in matches:
            rows.append({
                "path": str(match.relative_to(SOURCE_ROOT)),
                "sha256": file_digest(match),
                "expected_sha256": expected,
            })
        models[name] = rows
    found["models"] = models
    return found


def scorer_registry() -> Dict[str, Any]:
    """Report exact scorer presence; never import, load or execute one."""
    pystoi = _find_pystoi()
    stoi_ok = (pystoi.get("stoi_sha256") == PYSTOI_STOI_SHA256
               and pystoi.get("utils_sha256") == PYSTOI_UTILS_SHA256)
    dnsmos = _find_dnsmos()
    sig_ok = any(row["sha256"] == DNSMOS_SIG_SHA256
                 for row in dnsmos["models"]["sig.onnx"])
    bak_ok = any(row["sha256"] == DNSMOS_BAK_OVR_SHA256
                 for row in dnsmos["models"]["bak_ovr.onnx"])
    dnsmos_ok = (dnsmos.get("script_sha256") == DNSMOS_SCRIPT_SHA256
                 and sig_ok and bak_ok)
    return {
        "stoi": {
            "scorer_id": "pystoi-non-extended",
            "version": "0.4.1",
            "license_id": "MIT",
            "algorithm": "non-extended STOI, no per-utterance tuning",
            "required_source_sha256": {
                "stoi.py": PYSTOI_STOI_SHA256,
                "utils.py": PYSTOI_UTILS_SHA256,
            },
            "observed": pystoi,
            "present": bool(pystoi.get("stoi_sha256")),
            "pinned": stoi_ok,
            "status": "pinned" if stoi_ok else (
                "digest_mismatch" if pystoi.get("stoi_sha256") else "blocked"),
            "executed": False,
            "result": None,
            "qualifies": False,
            "reason": ("Exact pystoi 0.4.1 source is not staged in the "
                       "workspace environment; no STOI value is computed or "
                       "imported.") if not stoi_ok else
                      "Exact pystoi source digest admitted; execution still "
                      "requires a real rights-cleared screen.",
        },
        "dnsmos_p835": {
            "scorer_id": "dnsmos-p835",
            "version": "historical-local",
            "license_id": "not_staged",
            "algorithm": "P.835 SIG and BAK/OVL ONNX prediction",
            "required_sha256": {
                "dnsmos.py": DNSMOS_SCRIPT_SHA256,
                "sig.onnx": DNSMOS_SIG_SHA256,
                "bak_ovr.onnx": DNSMOS_BAK_OVR_SHA256,
            },
            "observed": dnsmos,
            "present": bool(dnsmos.get("script_present")),
            "pinned": dnsmos_ok,
            "status": "pinned" if dnsmos_ok else (
                "digest_mismatch" if dnsmos.get("script_sha256") else
                "blocked"),
            "executed": False,
            "result": None,
            "qualifies": False,
            "reason": ("Exact DNSMOS script and SIG/BAK-OVR models are not "
                       "staged at their documented paths; no predicted MOS "
                       "is computed or imported.") if not dnsmos_ok else
                      "Exact DNSMOS artifacts admitted; execution still "
                      "requires a real rights-cleared screen.",
        },
    }


def admit_scorer(name: str) -> Dict[str, Any]:
    registry = scorer_registry()
    if name not in registry:
        raise Reject("unsupported_scorer:" + str(name))
    row = registry[name]
    if not row["pinned"]:
        raise Reject("missing_scorer_artifact:" + name)
    return {"scorer_id": row["scorer_id"], "admitted": True,
            "executed": False, "result": None}


def real_screen_gate() -> Dict[str, Any]:
    """Fail closed on absent corpus, run outputs or exact scorers."""
    present: Dict[str, bool] = {}
    digests: Dict[str, Any] = {}
    missing: List[str] = []
    mismatched: List[str] = []
    for relative, expected in REAL_REQUIRED.items():
        path = SOURCE_ROOT / relative
        short = relative[len(REAL_RUN_DIR) + 1:]
        exists = path.is_file()
        present[short] = exists
        if not exists:
            missing.append(short)
            continue
        observed = file_digest(path)
        digests[short] = {"expected": expected, "observed": observed,
                          "matches": observed == expected}
        if observed != expected:
            mismatched.append(short)
    corpus_roots = [root for root in REAL_CORPUS_SEARCH_ROOTS
                    if (SOURCE_ROOT / root).exists()]
    registry = scorer_registry()
    for name, row in registry.items():
        if not row["pinned"]:
            missing.append("scorer:" + name)
    seen: set = set()
    missing = [item for item in missing
               if not (item in seen or seen.add(item))]
    status = "blocked" if (missing or mismatched or not corpus_roots) else "ready"
    return {
        "status": status,
        "run_directory": REAL_RUN_DIR,
        "required_items": EXPECTED_EARS_ITEMS,
        "present": present,
        "digests": digests,
        "missing": missing,
        "mismatched": mismatched,
        "corpus_search_roots": list(REAL_CORPUS_SEARCH_ROOTS),
        "corpus_root_present": bool(corpus_roots),
        "corpus_roots_found": corpus_roots,
        "scorers": registry,
        "scoring_invoked": False,
        "audio_read": False,
        "items_scored": 0,
        "qualifies": False,
        "reason": ("The exact EARS archive, prepared inputs, candidate "
                   "outputs and/or pinned scorers are absent. No real item "
                   "was read, decoded or scored.") if status == "blocked"
                  else "Inputs and scorers are present; scoring is still not "
                       "invoked by this evidence package.",
    }


def require_real_screen() -> None:
    gate = real_screen_gate()
    if gate["status"] != "ready":
        first = gate["missing"][0] if gate["missing"] else (
            gate["mismatched"][0] if gate["mismatched"] else "corpus_root")
        raise Reject("blocked_real_screen:" + first)


# ---------------------------------------------------------------------------
# Adverse, missing and invalid input matrix
# ---------------------------------------------------------------------------

def _base_manifest() -> Dict[str, Any]:
    fixture = build_fixture()
    mic = fixture["mic"]
    clean = fixture["clean"]
    items = []
    for index in range(2):
        start = index * 320
        end = start + 320
        sample_id = "synthetic-%04d" % (index + 1)
        items.append({
            "sample_id": sample_id,
            "original_sha256": signal_digest(clean[start:end]),
            "input_16k_sha256": signal_digest(mic[start:end]),
            "input_16k_path": "data/runs/task-local-synthetic/%s-input.wav"
                              % sample_id,
            "duration_samples": 320,
            "outputs": [{
                "candidate_id": "identity-control",
                "output_sha256": signal_digest(mic[start:end]),
                "output_path":
                    "data/runs/task-local-synthetic/%s-output.wav" % sample_id,
                "output_samples": 320,
            }],
        })
    return {
        "schema_id": MANIFEST_SCHEMA,
        "corpus_id": "task-local-synthetic-control",
        "corpus_license": "Apache-2.0 authored synthetic fixture",
        "corpus_archive_sha256": sha256_bytes(FIXTURE_ID.encode("utf-8")),
        "preparation_recipe_sha256":
            sha256_bytes(PREPARATION_ID.encode("utf-8")),
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "original_sample_rate_hz": ORIGINAL_SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "expected_items": 2,
        "items": items,
        "scorer_pins": {
            "stoi": {
                "scorer_id": "pystoi-non-extended",
                "version": "0.4.1",
                "source_sha256": PYSTOI_STOI_SHA256,
                "license_id": "MIT",
                "status": "blocked",
            },
            "dnsmos_p835": {
                "scorer_id": "dnsmos-p835",
                "version": "historical-local",
                "source_sha256": DNSMOS_SCRIPT_SHA256,
                "license_id": "not_staged",
                "status": "blocked",
            },
        },
    }


def _mutate(mutator: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
    manifest = copy.deepcopy(_base_manifest())
    mutator(manifest)
    return manifest


def _valid_rows(count: int = 2) -> List[Dict[str, Any]]:
    return [{
        "sample_id": "synthetic-%04d" % (index + 1),
        "candidate_id": "identity-control",
        "si_sdr_millidb": 999000,
        "snr_millidb": 999000,
        "rmse_millisample": 0,
        "peak_milli": 200,
        "clipped_samples": 0,
        "lag_samples": 0,
    } for index in range(count)]


def _adverse_definitions() -> List[Tuple[str, str, Callable[[], Any]]]:
    fixture = build_fixture()
    mic = fixture["mic"][:320]
    clean = fixture["clean"][:320]

    def remove_manifest_field(key: str) -> Callable[[], Any]:
        return lambda: validate_manifest(_mutate(lambda m: m.pop(key)))

    def set_manifest_field(key: str, value: Any) -> Callable[[], Any]:
        return lambda: validate_manifest(_mutate(lambda m: m.__setitem__(key, value)))

    def item_mutation(index: int,
                      mutator: Callable[[Dict[str, Any]], None]
                      ) -> Callable[[], Any]:
        def run() -> Any:
            manifest = _base_manifest()
            mutator(manifest["items"][index])
            return validate_manifest(manifest)
        return run

    def output_mutation(mutator: Callable[[Dict[str, Any]], None]
                        ) -> Callable[[], Any]:
        def run() -> Any:
            manifest = _base_manifest()
            mutator(manifest["items"][0]["outputs"][0])
            return validate_manifest(manifest)
        return run

    def pin_mutation(name: str,
                     mutator: Callable[[Dict[str, Any]], None]
                     ) -> Callable[[], Any]:
        def run() -> Any:
            manifest = _base_manifest()
            mutator(manifest["scorer_pins"][name])
            return validate_manifest(manifest)
        return run

    def row_mutation(mutator: Callable[[Dict[str, Any]], None]
                     ) -> Callable[[], Any]:
        def run() -> Any:
            rows = _valid_rows()
            mutator(rows[0])
            return aggregate_preservation(rows, expected_items=2)
        return run

    return [
        ("duplicate_json_key", "duplicate_json_key:a",
         lambda: parse_strict_json('{"a":1,"a":2}')),
        ("nan_json_constant", "nonfinite_json_constant:NaN",
         lambda: parse_strict_json('{"a":NaN}')),
        ("infinity_json_constant", "nonfinite_json_constant:Infinity",
         lambda: parse_strict_json('{"a":Infinity}')),
        ("malformed_json", "invalid_json",
         lambda: parse_strict_json('{"a":')),
        ("manifest_missing_field",
         "strict_keys_mismatch:manifest:corpus_license",
         remove_manifest_field("corpus_license")),
        ("manifest_extra_field", "strict_keys_mismatch:manifest:extra",
         lambda: validate_manifest(
             _mutate(lambda m: m.__setitem__("extra", 1)))),
        ("manifest_schema", "unsupported_manifest_schema",
         set_manifest_field("schema_id", "audio-sdk/other/0.1")),
        ("manifest_corpus_id", "invalid_sample_id",
         set_manifest_field("corpus_id", "EARS Archive")),
        ("manifest_license_empty", "invalid_string:corpus_license",
         set_manifest_field("corpus_license", "")),
        ("manifest_8000_hz", "unsupported_sample_rate",
         set_manifest_field("sample_rate_hz", 8000)),
        ("manifest_44100_hz", "unsupported_sample_rate",
         set_manifest_field("sample_rate_hz", 44100)),
        ("manifest_original_16k", "unsupported_original_sample_rate",
         set_manifest_field("original_sample_rate_hz", 16000)),
        ("manifest_256_frame", "unsupported_frame_samples",
         set_manifest_field("frame_samples", 256)),
        ("manifest_zero_items", "invalid_integer:expected_items",
         set_manifest_field("expected_items", 0)),
        ("manifest_744_items", "invalid_integer:expected_items",
         set_manifest_field("expected_items", 744)),
        ("manifest_items_not_list", "invalid_type:items",
         set_manifest_field("items", {})),
        ("manifest_item_count", "expected_item_count_mismatch:3:2",
         lambda: validate_manifest(_base_manifest(), expected_items=3)),
        ("manifest_bad_corpus_hash", "invalid_sha256:corpus_archive_sha256",
         set_manifest_field("corpus_archive_sha256", "0" * 63)),
        ("item_missing_outputs", "strict_keys_mismatch:item:outputs",
         item_mutation(0, lambda row: row.pop("outputs"))),
        ("item_extra_field", "strict_keys_mismatch:item:extra",
         item_mutation(0, lambda row: row.__setitem__("extra", 1))),
        ("item_duplicate_sample", "duplicate_sample_id",
         item_mutation(1, lambda row: row.__setitem__(
             "sample_id", "synthetic-0001"))),
        ("item_bad_sample_id", "invalid_sample_id",
         item_mutation(0, lambda row: row.__setitem__(
             "sample_id", "Synthetic 1"))),
        ("item_bad_input_hash", "invalid_sha256:input_16k_sha256",
         item_mutation(0, lambda row: row.__setitem__(
             "input_16k_sha256", "f" * 63))),
        ("item_absolute_path", "invalid_source_path:input_16k_path",
         item_mutation(0, lambda row: row.__setitem__(
             "input_16k_path", "/tmp/input.wav"))),
        ("item_traversal_path", "invalid_source_path:input_16k_path",
         item_mutation(0, lambda row: row.__setitem__(
             "input_16k_path", "data/../input.wav"))),
        ("item_wrong_prefix", "invalid_source_path:input_16k_path",
         item_mutation(0, lambda row: row.__setitem__(
             "input_16k_path", "model/input.wav"))),
        ("item_zero_duration", "invalid_integer:duration_samples",
         item_mutation(0, lambda row: row.__setitem__(
             "duration_samples", 0))),
        ("item_huge_duration", "invalid_integer:duration_samples",
         item_mutation(0, lambda row: row.__setitem__(
             "duration_samples", MAX_ITEM_SAMPLES + 1))),
        ("item_empty_outputs", "empty_outputs",
         item_mutation(0, lambda row: row.__setitem__("outputs", []))),
        ("output_missing_field", "strict_keys_mismatch:output:output_sha256",
         output_mutation(lambda row: row.pop("output_sha256"))),
        ("output_extra_field", "strict_keys_mismatch:output:extra",
         output_mutation(lambda row: row.__setitem__("extra", 1))),
        ("output_bad_candidate", "invalid_candidate_id",
         output_mutation(lambda row: row.__setitem__(
             "candidate_id", "Identity Candidate"))),
        ("output_sample_mismatch", "output_sample_count_mismatch",
         output_mutation(lambda row: row.__setitem__("output_samples", 319))),
        ("output_duplicate_candidate", "duplicate_candidate_id",
         lambda: (lambda m: (m["items"][0]["outputs"].append(
             copy.deepcopy(m["items"][0]["outputs"][0])),
             validate_manifest(m))[1])(_base_manifest())),
        ("scorer_missing", "strict_keys_mismatch:scorer_pins:stoi",
         lambda: validate_manifest(_mutate(
             lambda m: m["scorer_pins"].pop("stoi")))),
        ("scorer_bad_status", "invalid_scorer_status:stoi",
         pin_mutation("stoi", lambda row: row.__setitem__(
             "status", "qualified"))),
        ("scorer_bad_hash",
         "invalid_sha256:scorer_pins.stoi.source_sha256",
         pin_mutation("stoi", lambda row: row.__setitem__(
             "source_sha256", "a" * 63))),
        ("signal_missing_reference", "missing_input",
         lambda: score_pair(None, mic)),
        ("signal_missing_estimate", "missing_estimate",
         lambda: score_pair(mic, None)),
        ("signal_empty", "empty_signal:reference",
         lambda: score_pair([], [])),
        ("signal_length_mismatch", "length_mismatch",
         lambda: score_pair(mic, mic[:-1])),
        ("signal_nan", "nonfinite_input:reference",
         lambda: score_pair([float("nan")] + mic[1:], mic)),
        ("signal_inf", "nonfinite_input:estimate",
         lambda: score_pair(mic, mic[:-1] + [float("inf")])),
        ("signal_out_of_range", "sample_out_of_range:reference",
         lambda: score_pair([40000] + mic[1:], mic)),
        ("signal_string", "invalid_sample:reference",
         lambda: score_pair(["x"] + mic[1:], mic)),
        ("signal_bool", "invalid_sample:reference",
         lambda: score_pair([True] + mic[1:], mic)),
        ("lag_negative", "invalid_integer:max_lag",
         lambda: score_pair(mic, mic, max_lag=-1)),
        ("lag_too_large", "invalid_integer:max_lag",
         lambda: score_pair(mic, mic, max_lag=MAX_LAG_SAMPLES + 1)),
        ("clip_zero", "invalid_integer:clip_threshold",
         lambda: score_pair(mic, mic, clip_threshold=0)),
        ("clip_too_large", "invalid_integer:clip_threshold",
         lambda: score_pair(mic, mic, clip_threshold=40000)),
        ("aggregate_count", "screen_item_count_mismatch:2:1",
         lambda: aggregate_preservation(_valid_rows(1), expected_items=2)),
        ("aggregate_duplicate", "duplicate_screen_sample",
         lambda: (lambda rows: (rows[1].__setitem__(
             "sample_id", "synthetic-0001"),
             aggregate_preservation(rows, expected_items=2))[1])(_valid_rows())),
        ("aggregate_missing_field",
         "strict_keys_mismatch:screen_row:snr_millidb",
         row_mutation(lambda row: row.pop("snr_millidb"))),
        ("aggregate_nonfinite", "nonfinite_metric:si_sdr_millidb",
         row_mutation(lambda row: row.__setitem__(
             "si_sdr_millidb", float("nan")))),
        ("aggregate_out_of_range", "invalid_integer:si_sdr_millidb",
         row_mutation(lambda row: row.__setitem__(
             "si_sdr_millidb", MAX_MILLIDB + 1))),
        ("aggregate_bad_sample", "invalid_sample_id",
         row_mutation(lambda row: row.__setitem__(
             "sample_id", "Synthetic 1"))),
        ("manifest_files_missing", "missing_input_file:synthetic-0001",
         lambda: validate_manifest_files(
             _base_manifest(),
             Path("/nonexistent-ears-preservation-evidence-root"))),
        ("scorer_absent", "missing_scorer_artifact:stoi",
         lambda: admit_scorer("stoi")),
        ("scorer_unknown", "unsupported_scorer:bogus",
         lambda: admit_scorer("bogus")),
        ("real_screen_blocked",
         "blocked_real_screen:inputs/manifest.json",
         require_real_screen),
    ]


def adverse_rejections() -> List[Dict[str, Any]]:
    results = []
    for case_id, expected, callable_case in _adverse_definitions():
        try:
            callable_case()
        except Reject as error:
            observed = error.code
        else:
            raise Reject("adverse_case_not_rejected:" + case_id)
        if observed != expected:
            raise Reject("adverse_code_mismatch:%s:%s:%s"
                         % (case_id, expected, observed))
        results.append({
            "case_id": case_id,
            "expected_code": expected,
            "observed_code": observed,
            "status": "rejected",
            "state_unchanged": True,
        })
    return results


# ---------------------------------------------------------------------------
# Stable board identity, pins and report construction
# ---------------------------------------------------------------------------

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
        "note": "Only the stable linked-row identity is gated. The mutable "
                "full plan/swarm/TASKS.json is never hashed into, or pinned "
                "by, this package.",
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


def acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": "evidence",
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "scorer_corpus_and_cohort_pinned": {
                "status": "blocked",
                "evidence": "No EARS archive, prepared cohort manifest, "
                            "pystoi 0.4.1 source or DNSMOS script/models are "
                            "staged; nothing is pinned as an executable "
                            "scorer or corpus.",
            },
            "aggregation_and_failed_items": {
                "status": "synthetic_only",
                "evidence": "Deterministic item-weighted mean/median/p95 and "
                            "explicit failed/blocked lists are exercised on "
                            "authored integer controls only; no real cohort "
                            "aggregation exists.",
            },
            "paired_unpaired_synthetic_human_separation": {
                "status": "synthetic_only",
                "evidence": "The harness labels input-referenced preservation "
                            "as synthetic and never mixes it with paired "
                            "clean-reference, human listening or "
                            "source-reported values.",
            },
            "invalid_and_valid_case_validation": {
                "status": "synthetic_only",
                "evidence": "A representative valid control row and an "
                            "invalid/missing case are validated through the "
                            "same report; all synthetic controls remain "
                            "unqualified.",
            },
            "rights_provenance_and_listening_separation": {
                "status": "blocked",
                "evidence": "EARS is CC BY-NC 4.0 local non-commercial "
                            "research material. No archive item, consent, "
                            "speaker label, listening set or playback right "
                            "is staged or granted.",
            },
            "exact_runtime_or_source": {
                "status": "blocked",
                "evidence": "No exact scorer runtime, source revision, "
                            "container, dependency lock, model digest or "
                            "candidate output is present for admission.",
            },
        },
        "not_applicable": [
            "paired clean-reference SI-SDR/STOI accuracy, which needs a "
            "rights-cleared paired corpus rather than the input itself",
            "processor quality, denoising benefit, listener preference and "
            "benchmark ranking",
            "SDK provider registration, descriptor, installed v0, ABI or "
            "shared build behavior",
        ],
    }


def historical_screen() -> Dict[str, Any]:
    return {
        "source_report":
            "research/voice-enhancement-20261101/"
            "agent-ears-preservation-743/REPORT.md",
        "source_sha256": SOURCE_PINS[
            "research/voice-enhancement-20261101/"
            "agent-ears-preservation-743/REPORT.md"],
        "retained": True,
        "reproduced": False,
        "values_imported": False,
        "qualified": False,
        "corpus": {
            "id": "EARS blind speech-input archive",
            "items": 743,
            "duration_seconds": 7204.4,
            "original_sample_rate_hz": 48000,
            "prepared_sample_rate_hz": 16000,
            "license": "CC BY-NC 4.0",
            "use": "local non-commercial research only",
            "redistributed": False,
            "staged": False,
        },
        "protocol": {
            "reference": "same original input; no clean paired reference",
            "alignment_search_ms": 100,
            "metrics_reported": [
                "STOI versus input",
                "SI-SDR versus input",
                "RMSE versus input",
                "estimated lag",
                "peak and clipping",
                "transform RTF",
            ],
            "stoi_scorer": "pystoi 0.4.1",
            "dnsmos": "DNSMOS P.835 no-reference prediction, separate report",
            "speaker_labels": False,
            "transcripts": False,
            "listening": False,
        },
        "reported_aggregate": {
            "fastenhancer_small": {
                "mean_stoi_vs_input_milli": 745,
                "delta_stoi_vs_identity_milli": -255,
                "mean_si_sdr_vs_input_millidb": 5704,
                "mean_rmse_vs_input_micro": 16000,
                "mean_transform_rtf_milli": 31,
                "p95_transform_rtf_milli": 32,
            },
            "deepfilternet3": {
                "mean_stoi_vs_input_milli": 748,
                "delta_stoi_vs_identity_milli": -252,
                "mean_si_sdr_vs_input_millidb": 3859,
                "mean_rmse_vs_input_micro": 17640,
                "mean_transform_rtf_milli": 24,
                "p95_transform_rtf_milli": 25,
            },
        },
        "reported_values_are": "source-reported historical aggregates; not "
                               "recomputed, rerun, imported as this package's "
                               "result or used to qualify any candidate",
        "separate_historical_evidence": {
            "ears_blind_12_clip_dnsmos":
                "research/ears_blind_noise_screen_20261027.md",
            "dns_paired_30_item_pilot":
                "research/noise_suppression_pilot_20261027.md",
            "pooled": False,
        },
    }


def exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "exact_ears_archive_and_rights_absent",
            "requirement": "Stage the exact EARS archive with per-item "
                           "SHA-256, the CC BY-NC 4.0 terms, item provenance "
                           "and a rights review that permits the intended "
                           "screen and any listening use.",
            "state": "No EARS audio, archive digest, item manifest, rights "
                     "grant or licence copy is staged under data/. The "
                     "historical report describes 743 mono 48 kHz WAVs but "
                     "none is present; nothing was downloaded.",
        },
        {
            "id": "prepared_inputs_and_candidate_outputs_absent",
            "requirement": "Stage the exact prepared 16 kHz input manifest "
                           "and every candidate output with matching item, "
                           "sample count and SHA-256.",
            "state": "The documented run directory "
                     "data/runs/voice-enhancement-20261101-ears-preservation-743 "
                     "is absent, including inputs/manifest.json, "
                     "fastenhancer_small-results.json and "
                     "deepfilternet3-results.json. No output was regenerated.",
        },
        {
            "id": "pinned_stoi_scorer_and_runtime_absent",
            "requirement": "Stage and hash-admit pystoi 0.4.1 non-extended "
                           "STOI with its exact source, dependency lock and "
                           "licence review.",
            "state": "No pystoi source is staged in data/envs and no NumPy/"
                     "SciPy scoring environment exists. The STOI port in the "
                     "sibling stoi-estoi package is not imported or treated "
                     "as the licensed scorer.",
        },
        {
            "id": "pinned_dnsmos_models_and_runtime_absent",
            "requirement": "Stage the exact DNSMOS P.835 script plus SIG and "
                           "BAK/OVL ONNX models with immutable SHA-256, model "
                           "terms and a declared window/hop.",
            "state": "The documented dnsmos.py path and both ONNX model "
                     "digests are absent. No predicted SIG, BAK or OVL value "
                     "is computed or imported.",
        },
        {
            "id": "real_cohort_protocol_and_aggregation_absent",
            "requirement": "Freeze the 743-item cohort, inclusion/exclusion "
                           "rules, per-item failure policy, aggregation, "
                           "bootstrap or uncertainty method and declared "
                           "item-level scope.",
            "state": "Only synthetic integer controls are exercised. No real "
                     "cohort, item list, failure inventory, uncertainty "
                     "procedure or independent review result is staged.",
        },
        {
            "id": "rights_gated_listening_and_speaker_labels_absent",
            "requirement": "Provide a separate rights-cleared listening "
                           "design with consent/playback permission, "
                           "randomized conditions, speaker labels and "
                           "independent analysis.",
            "state": "EARS has no speaker labels in the historical run and "
                     "no permitted listening set or listener result is "
                     "staged. Listening remains a separate blocked gate, "
                     "never a proxy for the numeric screen.",
        },
        {
            "id": "harness_publication_and_independent_review_absent",
            "requirement": "Review the opt-in developer/evidence harness, "
                           "its exact pins, fail-closed behavior and scope "
                           "before any SDK adapter publication or processor "
                           "exposure.",
            "state": "No provider, descriptor, registry entry, default, "
                     "shared build or CI change is made. The harness is "
                     "task-local, proposal-only and independently un-reviewed "
                     "at this pinned head.",
        },
    ]


def release_gates() -> List[Dict[str, str]]:
    return [
        {
            "id": "RG-01",
            "requirement": "Exact EARS archive, item provenance, CC BY-NC "
                           "4.0 terms and a written rights/redistribution "
                           "review for the intended screen and listening use.",
            "status": "blocked",
        },
        {
            "id": "RG-02",
            "requirement": "Exact prepared 16 kHz input manifest and every "
                           "candidate output with matching item identity, "
                           "sample count and SHA-256.",
            "status": "blocked",
        },
        {
            "id": "RG-03",
            "requirement": "Hash-admitted pystoi 0.4.1 and DNSMOS P.835 "
                           "script/models with exact source, dependency, "
                           "licence and model terms.",
            "status": "blocked",
        },
        {
            "id": "RG-04",
            "requirement": "Frozen no-clean-reference protocol: input "
                           "reference, +/-100 ms lag bound, per-item failure "
                           "policy, deterministic item-weighted aggregation "
                           "and declared uncertainty.",
            "status": "blocked",
        },
        {
            "id": "RG-05",
            "requirement": "Representative valid and invalid/missing real "
                           "items validated through the exact reported "
                           "bundle, including nonfinite and geometry "
                           "rejection.",
            "status": "blocked",
        },
        {
            "id": "RG-06",
            "requirement": "Separate rights-cleared listening or ASR/content "
                           "control with speaker labels, randomized "
                           "conditions and independent analysis.",
            "status": "blocked",
        },
        {
            "id": "RG-07",
            "requirement": "Opt-in developer/evidence harness review with "
                           "exact pins and no SDK provider, descriptor, "
                           "registry, default, ABI, shared build or CI "
                           "change.",
            "status": "blocked",
        },
        {
            "id": "RG-08",
            "requirement": "Explicit proceed/defer decision and independent "
                           "exact-head approval before any processor or "
                           "public benchmark exposure.",
            "status": "blocked",
        },
    ]


def qualification() -> Dict[str, Any]:
    return {
        "status": "not_qualified",
        "qualifies": False,
        "all_required_results_present": False,
        "missing_result_promoted": False,
        "real_corpus_used": False,
        "real_scorer_executed": False,
        "real_candidate_outputs_present": False,
        "rights_cleared": False,
        "listening": False,
        "timing_measured": False,
        "synthetic_controls_executed": True,
        "synthetic_controls_qualified": False,
        "reason": "The exact EARS archive, prepared inputs, candidate "
                  "outputs, pystoi/DNSMOS scorer artifacts, rights grant and "
                  "real cohort protocol are absent. Only authored synthetic "
                  "controls ran; every real-screen path fails closed.",
    }


def _control_matrix() -> List[Dict[str, Any]]:
    matrix = []
    for control in preservation_controls():
        matrix.append({
            "control_id": control["control_id"],
            "output_digest": control["output_digest"],
            "si_sdr_millidb": control["global"]["si_sdr_millidb"],
            "snr_millidb": control["global"]["snr_millidb"],
            "level_change_millidb":
                control["global"]["level_change_millidb"],
            "rmse_millisample": control["global"]["rmse_millisample"],
            "lag_samples": control["global"]["lag_samples"],
        })
    return matrix


def build_report() -> Dict[str, Any]:
    _verify_pins()
    fixture = build_fixture()
    validate_fixture(fixture["spec"])
    controls = preservation_controls()
    identity = [row for row in controls
                if row["control_id"] == "identity_input"][0]
    adverse = adverse_rejections()
    registry = scorer_registry()
    gate = real_screen_gate()
    matrix = _control_matrix()
    matrix_digest = object_digest(matrix)
    fixture_digest = object_digest(fixture["spec"])
    board = board_row()
    _require(board["stable_sha256"] == BOARD_ROW_STABLE_SHA256,
             "stale_board_row")
    report = {
        "schema_id": REPORT_SCHEMA,
        "version": "0.1.0",
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_synthetic_incomplete",
        "evidence_status": "incomplete",
        "decision": "DEFER",
        "defer_before": "processor_exposure",
        "verification_profile": "evidence",
        "scope": {
            "benchmark_claim": False,
            "device_timing": False,
            "listening": False,
            "network_access": False,
            "numeric_parity_claim": False,
            "processor_exposure": False,
            "provider_registration": False,
            "public_default": False,
            "real_clean_reference": False,
            "real_corpus": False,
            "real_paired_audio": False,
            "release_claim": False,
            "runtime_invocation": False,
            "synthetic_only": True,
            "task_local_only": True,
            "unpaired_screen": False,
            "weights": False,
        },
        "scope_note": "Only docs/task-evidence/"
                      "ears-preservation-screen-and-scorer-harness/ is "
                      "written; all other paths are read-only pins.",
        "acceptance_profile": acceptance_profile(),
        "screen_contract": screen_manifest_spec(),
        "historical_screen": historical_screen(),
        "format": {
            "installed_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "installed_v0_channels": 1,
            "installed_v0_frame_samples": FRAME_SAMPLES,
            "installed_v0_geometry_preserved": True,
            "original_sample_rate_hz": ORIGINAL_SAMPLE_RATE_HZ,
            "prepared_sample_rate_hz": SAMPLE_RATE_HZ,
            "sample_format": "Q15 integer synthetic; no audio file",
            "reference": "same original input, no clean reference",
            "alignment_search_bound_samples": MAX_LAG_SAMPLES,
            "expected_ears_items": EXPECTED_EARS_ITEMS,
            "real_audio_decoded": False,
        },
        "fixture": {
            "spec": fixture["spec"],
            "fixture_digest": fixture_digest,
            "audio_generated": False,
            "audio_file_written": False,
            "synthetic_only": True,
            "is_ears_recording": False,
        },
        "scorer_harness": {
            "harness_id": "ears-preservation-scorer-harness-v1",
            "reference_kind": "authored_integer_q15_controls_not_candidate",
            "metrics": {
                "si_sdr": "zero-mean, scale-invariant, exact integers "
                          "before the logarithm, millidB",
                "snr": "uncentered SNR, millidB",
                "level_change": "output/input energy ratio, millidB",
                "rmse": "floor(1000*sqrt(mean squared error)), Q15 "
                        "milli-units",
                "lag": "deterministic cross-correlation, ties prefer "
                       "smallest absolute lag",
                "peak_and_clipping": "Q15 peak milli-units and samples at "
                                     "or above the declared threshold",
            },
            "stoi": "blocked; never approximated",
            "dnsmos_p835": "blocked; never approximated",
            "rtf": "not measured; no runtime",
            "memory": "not measured; no runtime",
            "listening": "not run; rights-gated and separate",
            "bootstrap": "not run; no population inference",
            "qualification": "not_qualified",
        },
        "scorers": registry,
        "real_screen": gate,
        "preservation_controls": controls,
        "identity_control": {
            "control_id": identity["control_id"],
            "bit_identical": identity["bit_identical"],
            "si_sdr_millidb": identity["global"]["si_sdr_millidb"],
            "snr_millidb": identity["global"]["snr_millidb"],
            "rmse_millisample": identity["global"]["rmse_millisample"],
            "lag_samples": identity["global"]["lag_samples"],
            "exact_value_is_capped": True,
            "cap_millidb": MAX_MILLIDB,
            "qualifies": False,
        },
        "alignment": alignment_probes(),
        "adverse_rejections": adverse,
        "adverse_all_rejected": True,
        "aggregate_example": aggregate_preservation(
            [{
                "sample_id": "synthetic-%04d" % (index + 1),
                "candidate_id": "identity-control",
                "si_sdr_millidb": 999000,
                "snr_millidb": 999000,
                "rmse_millisample": 0,
                "peak_milli": 226,
                "clipped_samples": 0,
                "lag_samples": 0,
            } for index in range(2)],
            expected_items=2,
        ),
        "qualification": qualification(),
        "exact_blockers": exact_blockers(),
        "release_gates": release_gates(),
        "boundary": {
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
            "network_access": False,
            "processor_exposure": False,
            "provider_registration": False,
            "public_api_abi_change": False,
            "readiness_json_added": False,
            "registered": False,
            "sdk_data_dir_added": False,
            "shared_build_or_ci_change": False,
            "weights_vendored": False,
        },
        "board_row": board,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "mode": "three in-process report builds plus three cold-start "
                    "run.py rounds",
            "control_matrix_digests": [matrix_digest, matrix_digest,
                                       matrix_digest],
            "fixture_digest": fixture_digest,
        },
        "negative_claims": [
            "No EARS audio, prepared input, candidate output, corpus or "
            "rights grant was downloaded, copied, decoded or staged.",
            "No pystoi, DNSMOS, NumPy, SciPy, ONNX Runtime, model or scorer "
            "was imported, loaded or executed.",
            "No STOI, DNSMOS, predicted MOS, SI-SDR, SNR, RMSE, RTF, memory "
            "or listening result for any real candidate exists.",
            "The authored integer Q15 controls are not a denoiser, not an "
            "EARS item and cannot qualify any component.",
            "Historical source-reported aggregates are retained with "
            "provenance only; they are not reproduced, pooled or promoted.",
            "No provider, descriptor, registry, installed v0 path, ABI, "
            "default, shared build, dependency lock or CI was changed.",
        ],
        "reopen_condition": "Stage the exact EARS archive and rights grant, "
                            "the prepared 16 kHz input manifest and candidate "
                            "outputs, exact pystoi 0.4.1 and DNSMOS P.835 "
                            "artifacts, a frozen 743-item no-clean-reference "
                            "protocol with representative valid/invalid "
                            "validation, a separate rights-cleared listening "
                            "control and independent exact-head review. Until "
                            "then the decision remains DEFER, the evidence "
                            "incomplete and the qualification not_qualified.",
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
    report = build_report()
    text, report_digest = canonical_report(report)
    _require(file_digest(HERE / "report.json") ==
             sha256_bytes(text.encode("utf-8")), "stale_report")
    _require((HERE / "report.json.sha256").read_text(encoding="ascii") ==
             report_digest + "\n", "stale_report_sidecar")
    pins = artifact_pins()
    board = board_row()
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
        "defer_before": "processor_exposure",
        "qualification_status": "not_qualified",
        "verification_profile": "evidence",
        "scope": dict(report["scope"]),
        "format": dict(report["format"]),
        "screen_contract": dict(report["screen_contract"]),
        "public_boundary": {
            "header": "api/include/audio_sdk/provider_v0.h",
            "session_header": "api/include/audio_sdk/session_v0.h",
            "abi_major": 0,
            "abi_minor": 1,
            "registration": "none; no provider, descriptor, registry entry "
                            "or installed default is added",
            "c_provider_added": False,
            "public_api_abi_changed": False,
            "installed_v0_behavior_changed": False,
            "shared_build_or_ci_changed": False,
        },
        "reference": {
            "reference_id": FIXTURE_ID,
            "reference_kind": "author_written_synthetic_q15_controls_not_"
                              "candidate",
            "metrics": ["si_sdr", "snr", "level_change", "rmse", "lag",
                        "peak", "clipping"],
            "stoi": "blocked",
            "dnsmos_p835": "blocked",
            "real_corpus": False,
            "real_scorer": False,
            "candidate_outputs": False,
            "downloads": False,
            "network_access": False,
            "processor_exposure": False,
            "registered": False,
            "default_enabled": False,
        },
        "board_row": board,
        "exact_blockers": report["exact_blockers"],
        "release_gates": report["release_gates"],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "artifact_pins": pins,
        "negative_claims": report["negative_claims"],
        "reopen_condition": report["reopen_condition"],
    }


def sources_bytes() -> bytes:
    """Regenerate SOURCES.sha256 bytes from hard pins plus live artifacts."""
    _verify_pins()
    for name in PIN_FILES:
        _require((HERE / name).is_file(), "missing_artifact:" + name)
    lines = [
        "# SHA-256 pins for " + TASK_ID
        + "; source: paths are workspace-relative, others "
          "SDK-worktree-relative."
    ]
    for path in SOURCE_FILES:
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in BOUNDARY_FILES:
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for name in PIN_FILES:
        lines.append(f"{file_digest(HERE / name)}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")
