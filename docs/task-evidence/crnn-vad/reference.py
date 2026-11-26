# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local CRNN VAD analysis-boundary evidence.

This is an original, stdlib-only synthetic probe written for this task. It is
NOT a CRNN, not a convolution, not a recurrent network, not a learned model, not
a CRNN checkpoint, not a licensed runtime and not a CRNN result. No upstream
code, weight, corpus, audio, model, device clock or asset is present, copied,
downloaded, loaded, imported or executed.

The catalogued candidate is blocked: no exact CRNN architecture, checkpoint,
source or adapter is selected. Consequently this probe only exercises the SDK
Analysis acceptance mechanics on deterministic synthetic frames: timestamped
probabilities, exact half-open source intervals, speech events, onset/offset
delay, stratified false negatives/positives, separate validity, availability,
stale/dropped events, independent state, reset and cross-hop invariance.

It is proposal-only, incomplete and not qualified.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", str(SDK_ROOT.parents[2]))
).resolve()
TASK_BOARD_REL = "audio-benchmark-platform/plan/swarm/TASKS.json"

VERSION = "0.1.0"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
REPORT_SCHEMA = "audio-sdk/crnn-vad-analysis-report/0.1"
CALLER_SCHEMA = "audio-sdk/crnn-vad/caller-supplied-asset/0.1"

TASK_ID = "SDK-CRNN-VAD"
TITLE = "CRNN VAD"
COMPONENT = "crnn-vad"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "7b00d762530bb69ca58d4cdb8194a83839e1d58c"
BRANCH = "swarm/SDK-CRNN-VAD"
REVIEWER = "reviewer-CRNN-VAD"
PROFILE = "analysis"
STATUS = "proposal_only_synthetic_incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
TASK_PREFIX = "docs/task-evidence/crnn-vad/"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_NS = 62500
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS
STREAM_SAMPLES = 41600
FINAL_PARTIAL_VALID = 137

THRESHOLD_MICRO = 500000
ONSET_CONFIRM_FRAMES = 2
HANGOVER_FRAMES = 3
FLOOR_RMS = 250
KNEE_RMS = 900
ZCR_STEP_MICRO = 1500
ZCR_CAP_MICRO = 250000
PROBABILITY_SCALE = 1000000

ORIGIN_NS = 1000000000
PROCESSING_DELAY_NS = 2500000
BUS_CAPACITY = 4

SURROGATE_ID = "fixed-rms-zcr-frame-probability/0.1"
SCORER_ID = "analysis-frame-boundary-strata/0.1"

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

CALLER_MANIFEST_FIELDS = (
    "asset_storage",
    "candidate_id",
    "license_id",
    "runtime_id",
    "source_revision",
    "source_sha256",
    "weights_byte_count",
    "weights_sha256",
)

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv": (
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245"
    ),
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": (
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f"
    ),
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md": (
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2"
    ),
    "reports/vad-research/chaining-evaluation.md": (
        "f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234"
    ),
    "REALTIME_COMPONENT_CANDIDATES.md": (
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d"
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

BOUNDARY_PINS: Dict[str, str] = {
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
    "docs/task-evidence/webrtc-vad/README.md": (
        "1b3c5968c187b97bd67dcf2006581bd111d3cddc03911d5530d9e14325dfbc65"
    ),
    "docs/task-evidence/webrtc-vad/report.json": (
        "762086dffc6cfc504035c99648e66065157e852cc4fb4b2500d646d7ce77d6cb"
    ),
    "docs/task-evidence/silero-vad-6-2-3-reference/README.md": (
        "90b5cb35ce83428782b6901eaff8a479d2acdb49709a40b7fc0450e7ea9237b8"
    ),
    "docs/task-evidence/silero-vad-6-2-3-reference/report.json": (
        "dac376c116b9734a63a9ee9931ccd11223bbda998503e8ff7bd2a00d7491a319"
    ),
    "docs/task-evidence/conv-tasnet/README.md": (
        "3560a2b238bb7d18b5ad6c057f1385c650a8cda246c7e87fee2db16e6d3a0290"
    ),
}

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

SYLLABLE_ENVELOPE: Tuple[int, ...] = (
    400, 700, 900, 1000, 950, 850, 750, 650,
    550, 500, 450, 420, 410, 405, 402, 400,
)

# Segments are frame-aligned at 160 samples. Active segments are the synthetic
# ground truth used only for task-local scoring of the surrogate.
SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"name": "idle_lead", "start": 0, "end": 6400, "kind": "idle_noise"},
    {"name": "speech_a", "start": 6400, "end": 16000, "kind": "active",
     "step": 3},
    {"name": "pause", "start": 16000, "end": 19200, "kind": "pause"},
    {"name": "speech_b", "start": 19200, "end": 28800, "kind": "active",
     "step": 5},
    {"name": "idle_mid", "start": 28800, "end": 32000, "kind": "idle_noise"},
    {"name": "speech_c", "start": 32000, "end": 40000, "kind": "active",
     "step": 7},
    {"name": "idle_tail", "start": 40000, "end": 41600, "kind": "idle_noise"},
)

FIXTURE_ID = "crnn-vad-synthetic-vad-fixture-v1"
CONFIG_ID = "crnn-vad-proposal-config/0.1"


class ReferenceRejection(ValueError):
    """Deterministic rejection that never mutates accepted session state."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def _reject_if_float(value: Any, label: str) -> None:
    if isinstance(value, float):
        raise ReferenceRejection("noncanonical_float:" + label)


def _check_canonical_value(value: Any, label: str) -> None:
    if value is None or isinstance(value, bool) or isinstance(value, str):
        return
    if isinstance(value, int):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _check_canonical_value(item, label + "[" + str(index) + "]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ReferenceRejection("noncanonical_key:" + label)
            _check_canonical_value(item, label + "." + key)
        return
    raise ReferenceRejection("noncanonical_type:" + label)


def canonical_text(value: Any) -> str:
    _check_canonical_value(value, "root")
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def processing_digest(events: Sequence[Dict[str, Any]]) -> str:
    """Content digest independent of the caller-provided session identity."""
    return object_digest([
        {key: value for key, value in event.items() if key != "session_id"}
        for event in events
    ])


def _unique_json_object(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ReferenceRejection("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_json_constant(token: str) -> None:
    raise ReferenceRejection("nonfinite_json_constant:" + token)


def load_strict_json_text(text: str) -> Any:
    if not isinstance(text, str):
        raise ReferenceRejection("json_text_not_string")
    if text.startswith("\ufeff"):
        raise ReferenceRejection("json_bom")
    try:
        return json.loads(text, object_pairs_hook=_unique_json_object,
                          parse_constant=_reject_json_constant)
    except ReferenceRejection:
        raise
    except (ValueError, TypeError) as error:
        raise ReferenceRejection("invalid_json:" + type(error).__name__) from error


def load_strict_json(path: Path) -> Any:
    try:
        payload = Path(path).read_bytes()
    except OSError as error:
        raise ReferenceRejection("missing_file:" + str(path)) from error
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ReferenceRejection("invalid_utf8:" + str(path)) from error
    return load_strict_json_text(text)


def require_json_object(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ReferenceRejection("json_not_object")
    return value


def load_strict_json_object_text(text: str) -> Dict[str, Any]:
    return require_json_object(load_strict_json_text(text))


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


# ---------------------------------------------------------------------------
# Synthetic fixture and integer surrogate
# ---------------------------------------------------------------------------

def _lcg(state: int) -> Tuple[int, int]:
    state = (1103515245 * state + 12345) & 0x7FFFFFFF
    return state, state


def _lcg_value(state: int, amplitude: int) -> int:
    if amplitude <= 0:
        return 0
    return (state >> 15) % (2 * amplitude + 1) - amplitude


def _segment_sample(segment: Dict[str, Any], index: int, local: int,
                    state: int) -> Tuple[int, int]:
    kind = segment["kind"]
    if kind == "active":
        step = int(segment["step"])
        phase = local % 64
        envelope = SYLLABLE_ENVELOPE[(local // 320) % 16]
        tone_a = (SINE64[phase] * 7000) // 32768
        tone_b = (SINE64[(phase * (step + 2)) % 64] * 3000) // 32768
        state, state2 = _lcg(state)
        broadband = _lcg_value(state2, 1000)
        value = ((tone_a + tone_b) * envelope) // 1000 + broadband
        return value, state2
    if kind == "pause":
        state, state2 = _lcg(state)
        return _lcg_value(state2, 120), state2
    state, state2 = _lcg(state)
    return _lcg_value(state2, 500), state2


def build_fixture() -> Dict[str, Any]:
    """Build the exact integer fixture and its frame-level ground truth."""
    samples: List[int] = []
    state = 123456789
    for segment in SEGMENTS:
        for local in range(segment["end"] - segment["start"]):
            value, state = _segment_sample(segment, len(samples), local, state)
            samples.append(max(-32768, min(32767, value)))
    if len(samples) != STREAM_SAMPLES:
        raise AssertionError("fixture_length_mismatch")
    truth_frames: List[int] = []
    truth_runs: List[Dict[str, int]] = []
    for segment in SEGMENTS:
        if segment["kind"] != "active":
            continue
        start_frame = segment["start"] // FRAME_SAMPLES
        end_frame = segment["end"] // FRAME_SAMPLES
        truth_frames.extend(range(start_frame, end_frame))
        truth_runs.append({"name": segment["name"],
                           "start_frame": start_frame,
                           "end_frame": end_frame,
                           "start_sample": segment["start"],
                           "end_sample": segment["end"]})
    floats = [value / 32768.0 for value in samples]
    return {
        "fixture_id": FIXTURE_ID,
        "samples_int": samples,
        "samples": floats,
        "length_samples": len(samples),
        "frame_count": len(samples) // FRAME_SAMPLES,
        "truth_frames": sorted(truth_frames),
        "truth_runs": truth_runs,
        "signal_sha256": sha256_bytes(
            json.dumps(samples, separators=(",", ":")).encode("utf-8")),
        "segments": [dict(segment) for segment in SEGMENTS],
    }


def fixture_spec(fixture: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "fixture_id": fixture["fixture_id"],
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "stream_samples": fixture["length_samples"],
        "frame_count": fixture["frame_count"],
        "signal_sha256": fixture["signal_sha256"],
        "segments": [
            {
                "name": segment["name"],
                "kind": segment["kind"],
                "start_sample": segment["start"],
                "end_sample": segment["end"],
                "start_frame": segment["start"] // FRAME_SAMPLES,
                "end_frame": segment["end"] // FRAME_SAMPLES,
                "active": segment["kind"] == "active",
            }
            for segment in fixture["segments"]
        ],
        "truth_runs": fixture["truth_runs"],
        "active_frame_count": len(fixture["truth_frames"]),
        "quiet_frame_count": (fixture["frame_count"]
                              - len(fixture["truth_frames"])),
        "synthetic": True,
        "real_speech": False,
        "candidate_audio": False,
    }


def surrogate_model_spec() -> Dict[str, Any]:
    return {
        "model_id": SURROGATE_ID,
        "kind": "deterministic_integer_surrogate",
        "is_crnn": False,
        "is_learned": False,
        "has_convolution": False,
        "has_recurrence": False,
        "uses_weights": False,
        "uses_checkpoint": False,
        "input": "160 mono 16 kHz float32 samples",
        "features": ["integer_rms", "zero_crossing_count"],
        "floor_rms": FLOOR_RMS,
        "knee_rms": KNEE_RMS,
        "zcr_step_micro": ZCR_STEP_MICRO,
        "zcr_cap_micro": ZCR_CAP_MICRO,
        "probability_scale": PROBABILITY_SCALE,
        "decision_threshold_micro": THRESHOLD_MICRO,
        "onset_confirm_frames": ONSET_CONFIRM_FRAMES,
        "hangover_frames": HANGOVER_FRAMES,
        "content_delay_samples": 0,
        "notes": (
            "Energy Hill function scaled by a zero-crossing voicing weight; "
            "integer arithmetic only. Not a CRNN posterior or calibration."
        ),
    }


def surrogate_model_digest() -> str:
    return object_digest(surrogate_model_spec())


def scoring_protocol_spec() -> Dict[str, Any]:
    return {
        "scorer_id": SCORER_ID,
        "probability_metric": "brier_micro",
        "boundary_metric": "onset_offset_frame_delay",
        "strata": ["active_speech", "quiet_noise"],
        "rate_unit": "ppm",
        "validity_policy": (
            "invalid and missing frames are excluded from probability, "
            "detection and boundary denominators; they are never nonspeech"
        ),
        "boundary_match_tolerance_frames": ONSET_CONFIRM_FRAMES,
        "source_intervals": "half_open_sample_intervals",
        "candidate_comparison": False,
        "oracle_used_for_score": False,
        "notes": (
            "Scores the deterministic surrogate against fixture-construction "
            "labels only. No CRNN output, held-out cohort or candidate oracle "
            "is used."
        ),
    }


def scoring_protocol_digest() -> str:
    return object_digest(scoring_protocol_spec())


def frame_features(samples: Sequence[float], valid_samples: int) -> Dict[str, int]:
    if valid_samples < 1 or valid_samples > len(samples):
        raise ReferenceRejection("invalid_valid_samples")
    integers: List[int] = []
    for value in samples[:valid_samples]:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceRejection("non_numeric_input")
        if not math.isfinite(float(value)):
            raise ReferenceRejection("nonfinite_input")
        integers.append(int(round(float(value) * 32768.0)))
    energy = sum(value * value for value in integers)
    rms = math.isqrt(energy // valid_samples)
    zcr = 0
    for index in range(1, valid_samples):
        previous = integers[index - 1]
        current = integers[index]
        if previous != 0 and current != 0 and ((previous < 0) != (current < 0)):
            zcr += 1
    return {"rms": rms, "zcr": zcr, "energy": energy,
            "valid_samples": valid_samples}


def probability_micro(rms: int, zcr: int) -> int:
    excess = max(0, rms - FLOOR_RMS)
    denominator = excess * excess + KNEE_RMS * KNEE_RMS
    energy_term = (PROBABILITY_SCALE * excess * excess) // denominator
    voicing = PROBABILITY_SCALE - min(ZCR_CAP_MICRO, zcr * ZCR_STEP_MICRO)
    return max(0, min(PROBABILITY_SCALE,
                      (energy_term * voicing) // PROBABILITY_SCALE))


def round_ratio(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise ReferenceRejection("invalid_denominator")
    if numerator < 0:
        raise ReferenceRejection("negative_ratio")
    return (2 * numerator + denominator) // (2 * denominator)


# ---------------------------------------------------------------------------
# Strict config, manifest, event and frame validation
# ---------------------------------------------------------------------------

def validate_config(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        raise ReferenceRejection("config_not_object")
    required = {
        "schema_id", "sample_rate_hz", "channels", "frame_samples",
        "sample_format", "execution_mode", "epoch", "first_input_sample",
        "sample_period_ns", "origin_ns", "processing_delay_ns", "clock_ppm",
        "adaptation", "resampling", "clipping_policy",
    }
    keys = set(config)
    if keys != required:
        missing = sorted(required - keys)
        extra = sorted(keys - required)
        detail = (missing[0] if missing else extra[0])
        raise ReferenceRejection("strict_keys_mismatch:config:" + detail)
    for name, value in config.items():
        if isinstance(value, bool) or isinstance(value, float):
            raise ReferenceRejection("config_bool_or_float:" + name)
        if not isinstance(value, (int, str)):
            raise ReferenceRejection("config_bad_type:" + name)
    if config["schema_id"] != CONFIG_ID:
        raise ReferenceRejection("unsupported_config_schema")
    if config["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_sample_rate")
    if config["channels"] != CHANNELS:
        raise ReferenceRejection("unsupported_channels")
    if config["frame_samples"] != FRAME_SAMPLES:
        raise ReferenceRejection("unsupported_frame_samples")
    if config["sample_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("unsupported_sample_format")
    if config["execution_mode"] != "inline_analysis":
        raise ReferenceRejection("unsupported_execution_mode")
    if not isinstance(config["epoch"], int) or config["epoch"] < 0:
        raise ReferenceRejection("invalid_epoch")
    if (not isinstance(config["first_input_sample"], int)
            or config["first_input_sample"] < 0):
        raise ReferenceRejection("invalid_first_input_sample")
    if config["sample_period_ns"] != SAMPLE_NS:
        raise ReferenceRejection("unsupported_sample_period")
    if (not isinstance(config["origin_ns"], int)
            or config["origin_ns"] < 0):
        raise ReferenceRejection("invalid_origin_ns")
    if (not isinstance(config["processing_delay_ns"], int)
            or config["processing_delay_ns"] < 0):
        raise ReferenceRejection("invalid_processing_delay_ns")
    if (not isinstance(config["clock_ppm"], int)
            or not -1000 <= config["clock_ppm"] <= 1000):
        raise ReferenceRejection("invalid_clock_ppm")
    if config["adaptation"] != "off":
        raise ReferenceRejection("unsupported_adaptation")
    if config["resampling"] != "none":
        raise ReferenceRejection("unsupported_resampling")
    if config["clipping_policy"] not in {"none", "clip"}:
        raise ReferenceRejection("unsupported_clipping_policy")
    return dict(config)


def default_config() -> Dict[str, Any]:
    return {
        "schema_id": CONFIG_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "execution_mode": "inline_analysis",
        "epoch": 0,
        "first_input_sample": 0,
        "sample_period_ns": SAMPLE_NS,
        "origin_ns": ORIGIN_NS,
        "processing_delay_ns": PROCESSING_DELAY_NS,
        "clock_ppm": 0,
        "adaptation": "off",
        "resampling": "none",
        "clipping_policy": "none",
    }


_HEX = set("0123456789abcdef")


def _is_hex(value: Any, length: int) -> bool:
    return (isinstance(value, str) and len(value) == length
            and set(value) <= _HEX)


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate declaration identity only; never load or execute an asset."""
    if not isinstance(manifest, dict):
        raise ReferenceRejection("manifest_not_object")
    if set(manifest) != set(CALLER_MANIFEST_FIELDS):
        missing = sorted(set(CALLER_MANIFEST_FIELDS) - set(manifest))
        extra = sorted(set(manifest) - set(CALLER_MANIFEST_FIELDS))
        raise ReferenceRejection("strict_keys_mismatch:manifest:"
                                 + (missing[0] if missing else extra[0]))
    if manifest["candidate_id"] != COMPONENT:
        raise ReferenceRejection("manifest_candidate_mismatch")
    if not _is_hex(manifest["source_revision"], 40):
        raise ReferenceRejection("manifest_bad_source_revision")
    if not _is_hex(manifest["source_sha256"], 64):
        raise ReferenceRejection("manifest_bad_source_hash")
    if not _is_hex(manifest["weights_sha256"], 64):
        raise ReferenceRejection("manifest_bad_weights_hash")
    count = manifest["weights_byte_count"]
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise ReferenceRejection("manifest_bad_weights_size")
    if count > 512 * 1024 * 1024:
        raise ReferenceRejection("manifest_weights_too_large")
    runtime = manifest["runtime_id"]
    if (not isinstance(runtime, str) or not runtime
            or any(character not in
                   "abcdefghijklmnopqrstuvwxyz0123456789._-"
                   for character in runtime)):
        raise ReferenceRejection("manifest_bad_runtime_id")
    license_id = manifest["license_id"]
    if not isinstance(license_id, str) or not license_id or license_id == "unknown":
        raise ReferenceRejection("manifest_missing_license")
    if manifest["asset_storage"] != "external":
        raise ReferenceRejection("manifest_requires_external_storage")
    return {
        "accepted": True,
        "loaded": False,
        "executed": False,
        "verified": False,
        "note": "declaration shape only; no asset, weight or runtime read",
    }


def validate_event(event: Any) -> None:
    if not isinstance(event, dict):
        raise ReferenceRejection("event_not_object")
    required = {"sequence", "epoch", "session_id", "frame_index",
                "source_start", "source_end", "validity",
                "probability_micro", "speech", "available_ns"}
    if set(event) != required:
        raise ReferenceRejection("event_key_mismatch")
    for name in ("sequence", "epoch", "frame_index", "source_start",
                 "source_end", "available_ns"):
        value = event[name]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ReferenceRejection("event_bad_integer:" + name)
    if event["sequence"] < 1 or event["frame_index"] < 0:
        raise ReferenceRejection("event_bad_index")
    if event["source_end"] <= event["source_start"]:
        raise ReferenceRejection("event_bad_interval")
    if event["validity"] not in {"known", "invalid", "missing"}:
        raise ReferenceRejection("event_bad_validity")
    probability = event["probability_micro"]
    if probability is not None:
        if (isinstance(probability, bool) or not isinstance(probability, int)
                or not 0 <= probability <= PROBABILITY_SCALE):
            raise ReferenceRejection("event_bad_probability")
    if event["speech"] is not None and not isinstance(event["speech"], bool):
        raise ReferenceRejection("event_bad_speech")
    if event["validity"] != "known" and probability is not None:
        raise ReferenceRejection("event_validity_probability_conflict")
    if event["validity"] == "known":
        if probability is None or event["speech"] is None:
            raise ReferenceRejection("event_missing_known_value")
    if not isinstance(event["session_id"], str) or not event["session_id"]:
        raise ReferenceRejection("event_bad_session_id")


# ---------------------------------------------------------------------------
# Streaming analysis session
# ---------------------------------------------------------------------------

class AnalysisSession:
    """Independent epoch-scoped VAD analysis session with immutable rejection."""

    def __init__(self, config: Dict[str, Any], session_id: str,
                 epoch: int) -> None:
        self.config = validate_config(config)
        if not isinstance(session_id, str) or not session_id:
            raise ReferenceRejection("invalid_session_id")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ReferenceRejection("invalid_epoch")
        if self.config["epoch"] != epoch:
            raise ReferenceRejection("config_epoch_mismatch")
        self.session_id = session_id
        self._reset_state(epoch)

    def _reset_state(self, epoch: int) -> None:
        self.epoch = epoch
        self.total_samples = self.config["first_input_sample"]
        self.frame_index = 0
        self.next_sequence = 1
        self.events: List[Dict[str, Any]] = []
        self.runs: List[Dict[str, int]] = []
        self.rejections: List[Dict[str, Any]] = []
        self.counters = {
            "accepted_frames": 0,
            "accepted_samples": 0,
            "known_frames": 0,
            "invalid_frames": 0,
            "missing_frames": 0,
            "rejected_frames": 0,
            "final_frames": 0,
        }
        self.active = False
        self.active_start_frame: Optional[int] = None
        self.above_run = 0
        self.below_run = 0
        self.closed_final = False

    def state_digest(self) -> str:
        processing_counters = {
            name: value for name, value in self.counters.items()
            if name != "rejected_frames"
        }
        state = {
            "epoch": self.epoch,
            "total_samples": self.total_samples,
            "frame_index": self.frame_index,
            "next_sequence": self.next_sequence,
            "counters": processing_counters,
            "active": self.active,
            "active_start_frame": self.active_start_frame,
            "above_run": self.above_run,
            "below_run": self.below_run,
            "closed_final": self.closed_final,
            "events_sha256": object_digest(self.events),
            "runs": self.runs,
        }
        return object_digest(state)

    def summary(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "epoch": self.epoch,
            "total_samples": self.total_samples,
            "frame_index": self.frame_index,
            "counters": dict(self.counters),
            "runs": [dict(run) for run in self.runs],
            "rejections": [dict(item) for item in self.rejections],
            "state_digest": self.state_digest(),
        }

    def reset(self, epoch: int) -> Dict[str, Any]:
        if isinstance(epoch, bool) or not isinstance(epoch, int):
            raise ReferenceRejection("invalid_epoch")
        if epoch <= self.epoch:
            raise ReferenceRejection("epoch_not_increasing")
        previous = self.epoch
        self._reset_state(epoch)
        return {"status": "ok", "operation": "reset",
                "previous_epoch": previous, "epoch": self.epoch,
                "session_id": self.session_id,
                "state_digest": self.state_digest()}

    def availability_ns(self, source_end: int) -> int:
        return (self.config["origin_ns"] + source_end * SAMPLE_NS
                + self.config["processing_delay_ns"])

    def _reject(self, code: str, epoch: Optional[int],
                start_sample: Optional[int]) -> None:
        before = self.state_digest()
        self.counters["rejected_frames"] += 1
        record = {
            "status": "rejected",
            "code": code,
            "epoch": epoch,
            "start_sample": start_sample,
            "session_id": self.session_id,
            "state_digest_before": before,
        }
        self.rejections.append(record)
        if self.state_digest() != before:
            raise AssertionError("rejection_mutated_state:" + code)
        raise ReferenceRejection(code)

    def process_frame(self, samples: Any, *, epoch: Optional[int] = None,
                      validity: str = "known",
                      start_sample: Optional[int] = None,
                      sequence: Optional[int] = None,
                      is_final: bool = False,
                      valid_samples: Optional[int] = None,
                      probability_override: Optional[int] = None
                      ) -> Dict[str, Any]:
        if not isinstance(samples, (list, tuple)):
            raise ReferenceRejection("frame_not_sequence")
        if epoch is None:
            epoch = self.epoch
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            self._reject("invalid_epoch", epoch if isinstance(epoch, int)
                         else None, start_sample)
        if epoch != self.epoch:
            self._reject("stale_epoch", epoch, start_sample)
        if self.closed_final:
            self._reject("stream_closed", epoch, start_sample)
        if len(samples) == 0:
            self._reject("empty_frame", epoch, start_sample)
        if len(samples) > FRAME_SAMPLES:
            self._reject("frame_too_long", epoch, start_sample)
        if len(samples) < FRAME_SAMPLES and not is_final:
            self._reject("partial_frame_requires_final", epoch, start_sample)
        if start_sample is None:
            start_sample = self.total_samples
        if (isinstance(start_sample, bool) or not isinstance(start_sample, int)
                or start_sample < 0):
            self._reject("invalid_start_sample", epoch, None)
        if start_sample != self.total_samples:
            self._reject("wrong_input_position", epoch, start_sample)
        if sequence is None:
            sequence = self.next_sequence
        if (isinstance(sequence, bool) or not isinstance(sequence, int)
                or sequence != self.next_sequence):
            self._reject("stale_or_duplicate_sequence", epoch, start_sample)
        if valid_samples is None:
            valid_samples = len(samples)
        if (isinstance(valid_samples, bool)
                or not isinstance(valid_samples, int)
                or valid_samples < 1 or valid_samples > len(samples)):
            self._reject("invalid_valid_samples", epoch, start_sample)
        if is_final:
            if valid_samples > len(samples):
                self._reject("invalid_valid_samples", epoch, start_sample)
        elif valid_samples != FRAME_SAMPLES:
            self._reject("partial_frame_requires_final", epoch, start_sample)
        if validity not in {"known", "invalid", "missing"}:
            self._reject("invalid_validity_token", epoch, start_sample)
        if probability_override is not None:
            if (isinstance(probability_override, bool)
                    or not isinstance(probability_override, int)
                    or not 0 <= probability_override <= PROBABILITY_SCALE):
                self._reject("invalid_probability_override", epoch,
                             start_sample)
            if validity != "known":
                self._reject("override_requires_known_validity", epoch,
                             start_sample)
        # Validate and check padding only after all control fields pass.
        for index, value in enumerate(samples):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                self._reject("non_numeric_input", epoch, start_sample)
            if not math.isfinite(float(value)):
                self._reject("nonfinite_input", epoch, start_sample)
            if index >= valid_samples and float(value) != 0.0:
                self._reject("nonzero_padding", epoch, start_sample)

        feature: Optional[Dict[str, int]] = None
        probability: Optional[int] = None
        speech: Optional[bool] = None
        if validity == "known":
            feature = frame_features(samples, valid_samples)
            probability = (probability_override if probability_override
                           is not None else
                           probability_micro(feature["rms"], feature["zcr"]))
            speech = probability >= THRESHOLD_MICRO
            self._advance_detector(probability)
            self.counters["known_frames"] += 1
        elif validity == "invalid":
            self.counters["invalid_frames"] += 1
        else:
            self.counters["missing_frames"] += 1

        source_start = self.total_samples
        source_end = source_start + valid_samples
        event = {
            "sequence": sequence,
            "epoch": epoch,
            "session_id": self.session_id,
            "frame_index": self.frame_index,
            "source_start": source_start,
            "source_end": source_end,
            "validity": validity,
            "probability_micro": probability,
            "speech": speech,
            "available_ns": self.availability_ns(source_end),
        }
        validate_event(event)
        self.events.append(event)
        self.total_samples = source_end
        self.frame_index += 1
        self.next_sequence += 1
        self.counters["accepted_frames"] += 1
        self.counters["accepted_samples"] += valid_samples
        if is_final:
            self.counters["final_frames"] += 1
            if self.active:
                self._close_active(self.frame_index)
            self.closed_final = True
            self.above_run = 0
            self.below_run = 0
        return event

    def _advance_detector(self, probability: int) -> None:
        index = self.frame_index
        if probability >= THRESHOLD_MICRO:
            self.above_run += 1
            self.below_run = 0
            if not self.active and self.above_run >= ONSET_CONFIRM_FRAMES:
                self.active = True
                self.active_start_frame = index - ONSET_CONFIRM_FRAMES + 1
        else:
            self.below_run += 1
            self.above_run = 0
            if self.active and self.below_run >= HANGOVER_FRAMES + 1:
                self._close_active(index - HANGOVER_FRAMES)

    def _close_active(self, end_frame: int) -> None:
        if not self.active or self.active_start_frame is None:
            return
        if end_frame > self.active_start_frame:
            self.runs.append({"start_frame": self.active_start_frame,
                              "end_frame": end_frame})
        self.active = False
        self.active_start_frame = None
        self.above_run = 0
        self.below_run = 0

    def finalize(self) -> None:
        if not self.closed_final:
            self.closed_final = True
            if self.active:
                self._close_active(self.frame_index)


def run_stream(samples: Sequence[float], chunk_sizes: Optional[Sequence[int]] = None,
               session_id: str = "stream", epoch: int = 0,
               config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if config is None:
        config = default_config()
        config["epoch"] = epoch
    session = AnalysisSession(config, session_id, epoch)
    total = len(samples)
    if chunk_sizes is None:
        chunk_sizes = [FRAME_SAMPLES] * (total // FRAME_SAMPLES)
        if total % FRAME_SAMPLES:
            chunk_sizes.append(total % FRAME_SAMPLES)
    chunk_sizes = list(chunk_sizes)
    if any(isinstance(size, bool) or not isinstance(size, int) or size <= 0
           for size in chunk_sizes):
        raise ReferenceRejection("invalid_chunk_plan")
    if sum(chunk_sizes) != total:
        raise ReferenceRejection("chunk_plan_length_mismatch")
    position = 0
    for size in chunk_sizes:
        chunk = list(samples[position:position + size])
        position += size
        for offset in range(0, size, FRAME_SAMPLES):
            frame = chunk[offset:offset + FRAME_SAMPLES]
            is_last = (position == total and offset + FRAME_SAMPLES >= size)
            if len(frame) < FRAME_SAMPLES:
                if not is_last:
                    raise ReferenceRejection("chunk_plan_partial")
                session.process_frame(frame, is_final=True,
                                      valid_samples=len(frame))
            else:
                session.process_frame(frame, is_final=is_last)
    session.finalize()
    return {
        "session": session,
        "events": session.events,
        "runs": session.runs,
        "digest": processing_digest(session.events),
        "summary": session.summary(),
    }


def chunk_plan(total: int, pattern: Sequence[int]) -> List[int]:
    sizes: List[int] = []
    index = 0
    while total > 0:
        size = pattern[index % len(pattern)]
        index += 1
        size = min(size, total)
        sizes.append(size)
        total -= size
    return sizes


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_events(events: Sequence[Dict[str, Any]],
                 fixture: Dict[str, Any],
                 threshold_micro: int = THRESHOLD_MICRO) -> Dict[str, Any]:
    truth = set(fixture["truth_frames"])
    predicted: set[int] = set()
    for run in score_runs_from_events(events, threshold_micro):
        predicted.update(range(run["start_frame"], run["end_frame"]))
    known = [event for event in events if event["validity"] == "known"]
    invalid = sum(1 for event in events if event["validity"] == "invalid")
    missing = sum(1 for event in events if event["validity"] == "missing")
    tp = fp = fn = tn = 0
    squared = 0
    for event in known:
        frame = event["frame_index"]
        label = frame in truth
        decision = frame in predicted
        probability = event["probability_micro"]
        target = PROBABILITY_SCALE if label else 0
        difference = probability - target
        squared += difference * difference
        if label and decision:
            tp += 1
        elif label and not decision:
            fn += 1
        elif not label and decision:
            fp += 1
        else:
            tn += 1
    positives = tp + fn
    negatives = fp + tn
    scored = len(known)
    brier_micro = (round_ratio(squared, scored * PROBABILITY_SCALE)
                   if scored else 0)
    return {
        "scored_frames": scored,
        "invalid_frames": invalid,
        "missing_frames": missing,
        "positives": positives,
        "negatives": negatives,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "brier_micro": brier_micro,
        "fn_ppm": round_ratio(fn * PROBABILITY_SCALE, positives)
                  if positives else 0,
        "fp_ppm": round_ratio(fp * PROBABILITY_SCALE, negatives)
                  if negatives else 0,
        "accuracy_ppm": round_ratio((tp + tn) * PROBABILITY_SCALE, scored)
                        if scored else 0,
        "invalid_treated_as_nonspeech": False,
        "qualifies": False,
    }


def score_runs_from_events(events: Sequence[Dict[str, Any]],
                           threshold_micro: int = THRESHOLD_MICRO
                           ) -> List[Dict[str, int]]:
    """Reconstruct event runs from per-frame speech decisions."""
    runs: List[Dict[str, int]] = []
    start: Optional[int] = None
    end: Optional[int] = None
    for event in events:
        if event["validity"] != "known":
            continue
        frame = event["frame_index"]
        if event["probability_micro"] >= threshold_micro:
            if start is None:
                start = frame
            end = frame + 1
        elif start is not None:
            runs.append({"start_frame": start, "end_frame": end})
            start = None
            end = None
    if start is not None:
        runs.append({"start_frame": start, "end_frame": end})
    return runs


def threshold_sensitivity_check(events: Sequence[Dict[str, Any]],
                                fixture: Dict[str, Any]) -> Dict[str, Any]:
    rows = []
    for threshold in (100000, 500000, 950000):
        score = score_events(events, fixture, threshold)
        rows.append({
            "threshold_micro": threshold,
            "fn_ppm": score["fn_ppm"],
            "fp_ppm": score["fp_ppm"],
            "false_negatives": score["false_negatives"],
            "false_positives": score["false_positives"],
            "scored_frames": score["scored_frames"],
        })
    return {
        "thresholds": rows,
        "strata_respond_to_threshold": len({(row["fn_ppm"], row["fp_ppm"])
                                            for row in rows}) > 1,
        "candidate_threshold": None,
        "qualifies": False,
    }


def boundary_report(events: Sequence[Dict[str, Any]],
                    fixture: Dict[str, Any]) -> Dict[str, Any]:
    truth_runs = fixture["truth_runs"]
    detected = score_runs_from_events(events)
    rows = []
    all_matched = len(detected) == len(truth_runs)
    max_onset = 0
    max_offset = 0
    for index, truth in enumerate(truth_runs):
        if index >= len(detected):
            rows.append({
                "name": truth["name"],
                "truth_start_frame": truth["start_frame"],
                "truth_end_frame": truth["end_frame"],
                "detected_start_frame": None,
                "detected_end_frame": None,
                "onset_delay_frames": None,
                "offset_delay_frames": None,
                "matched": False,
            })
            all_matched = False
            continue
        run = detected[index]
        onset_delay = run["start_frame"] - truth["start_frame"]
        offset_delay = run["end_frame"] - truth["end_frame"]
        matched = (abs(onset_delay) <= ONSET_CONFIRM_FRAMES
                   and abs(offset_delay) <= ONSET_CONFIRM_FRAMES)
        all_matched = all_matched and matched
        max_onset = max(max_onset, abs(onset_delay))
        max_offset = max(max_offset, abs(offset_delay))
        rows.append({
            "name": truth["name"],
            "truth_start_frame": truth["start_frame"],
            "truth_end_frame": truth["end_frame"],
            "detected_start_frame": run["start_frame"],
            "detected_end_frame": run["end_frame"],
            "onset_delay_frames": onset_delay,
            "offset_delay_frames": offset_delay,
            "matched": matched,
        })
    return {
        "truth_runs": len(truth_runs),
        "detected_runs": len(detected),
        "events": rows,
        "all_matched": all_matched,
        "max_abs_onset_delay_frames": max_onset,
        "max_abs_offset_delay_frames": max_offset,
        "tolerance_frames": ONSET_CONFIRM_FRAMES,
        "candidate_boundary_parity": False,
        "qualifies": False,
    }


def availability_report(events: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    expected = []
    for event in events:
        expected.append(ORIGIN_NS + event["source_end"] * SAMPLE_NS
                        + PROCESSING_DELAY_NS)
    actual = [event["available_ns"] for event in events]
    monotone = all(actual[index] < actual[index + 1]
                   for index in range(len(actual) - 1))
    exact = all(event["source_end"] > event["source_start"]
                for event in events)
    contiguous = all(
        events[index - 1]["source_end"] == events[index]["source_start"]
        for index in range(1, len(events)))
    return {
        "origin_ns": ORIGIN_NS,
        "processing_delay_ns": PROCESSING_DELAY_NS,
        "sample_period_ns": SAMPLE_NS,
        "first_available_ns": actual[0] if actual else None,
        "last_available_ns": actual[-1] if actual else None,
        "monotone": monotone,
        "formula_matches": actual == expected,
        "exact_half_open_intervals": exact and contiguous,
        "contiguous_source_intervals": contiguous,
        "device_timing_measured": False,
        "qualifies": False,
    }


def validity_report(events: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    known = [event for event in events if event["validity"] == "known"]
    invalid = [event for event in events if event["validity"] == "invalid"]
    missing = [event for event in events if event["validity"] == "missing"]
    return {
        "total_events": len(events),
        "known": len(known),
        "invalid": len(invalid),
        "missing": len(missing),
        "invalid_probability_null": all(
            event["probability_micro"] is None for event in invalid),
        "invalid_speech_null": all(event["speech"] is None for event in invalid),
        "missing_probability_null": all(
            event["probability_micro"] is None for event in missing),
        "invalid_scored_as_nonspeech": False,
        "missing_scored_as_nonspeech": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

class EventBus:
    """Bounded single-epoch event bus with explicit stale/drop accounting."""

    def __init__(self, capacity: int = BUS_CAPACITY) -> None:
        if capacity < 1:
            raise ReferenceRejection("invalid_bus_capacity")
        self.capacity = capacity
        self.epoch = 0
        self.last_sequence = 0
        self.queue: List[Dict[str, Any]] = []
        self.accepted = 0
        self.dropped: List[Dict[str, Any]] = []

    def advance_epoch(self, epoch: int) -> None:
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch <= self.epoch:
            raise ReferenceRejection("invalid_bus_epoch")
        self.epoch = epoch
        self.last_sequence = 0
        self.queue = []

    def publish(self, event: Dict[str, Any]) -> Dict[str, Any]:
        validate_event(event)
        if event["epoch"] != self.epoch:
            return self._drop(event, "stale_epoch")
        if event["sequence"] <= self.last_sequence:
            return self._drop(event, "stale_sequence")
        if len(self.queue) >= self.capacity:
            return self._drop(event, "queue_full")
        self.queue.append(event)
        self.last_sequence = event["sequence"]
        self.accepted += 1
        return {"status": "accepted", "sequence": event["sequence"],
                "queue_depth": len(self.queue)}

    def _drop(self, event: Dict[str, Any], reason: str) -> Dict[str, Any]:
        record = {"status": "dropped", "reason": reason,
                  "sequence": event["sequence"], "epoch": event["epoch"]}
        self.dropped.append(record)
        return record

    def summary(self) -> Dict[str, Any]:
        return {
            "capacity": self.capacity,
            "epoch": self.epoch,
            "accepted": self.accepted,
            "queue_depth": len(self.queue),
            "dropped": [dict(item) for item in self.dropped],
            "drop_count": len(self.dropped),
        }


def _frame_list(samples: Sequence[float]) -> List[List[float]]:
    frames = []
    for offset in range(0, len(samples), FRAME_SAMPLES):
        frame = list(samples[offset:offset + FRAME_SAMPLES])
        if len(frame) == FRAME_SAMPLES:
            frames.append(frame)
    return frames


def independent_state_check(fixture: Dict[str, Any]) -> Dict[str, Any]:
    quiet = [0.0] * STREAM_SAMPLES
    solo_speech = run_stream(fixture["samples"], session_id="solo")
    solo_quiet = run_stream(quiet, session_id="quiet")
    a = AnalysisSession(default_config(), "a", 0)
    b = AnalysisSession(default_config(), "b", 0)
    for frame_a, frame_b in zip(_frame_list(fixture["samples"]),
                                _frame_list(quiet)):
        a.process_frame(frame_a)
        b.process_frame(frame_b)
    a.finalize()
    b.finalize()
    return {
        "speech_digest_matches_solo": processing_digest(a.events)
                                       == solo_speech["digest"],
        "quiet_digest_matches_solo": processing_digest(b.events)
                                      == solo_quiet["digest"],
        "session_ids_distinct": a.session_id != b.session_id,
        "interleaved": True,
        "qualifies": False,
    }


def reset_check(fixture: Dict[str, Any]) -> Dict[str, Any]:
    reset_session = AnalysisSession(default_config(), "reset", 0)
    for frame in _frame_list(fixture["samples"]):
        reset_session.process_frame(frame)
    reset_session.finalize()
    record = reset_session.reset(2)
    cleared = len(reset_session.events) == 0 and reset_session.total_samples == 0
    for frame in _frame_list(fixture["samples"]):
        reset_session.process_frame(frame)
    reset_session.finalize()
    fresh_config = default_config()
    fresh_config["epoch"] = 2
    fresh = AnalysisSession(fresh_config, "reset", 2)
    for frame in _frame_list(fixture["samples"]):
        fresh.process_frame(frame)
    fresh.finalize()
    return {
        "reset_epoch": record["epoch"],
        "matches_fresh": processing_digest(reset_session.events)
                          == processing_digest(fresh.events),
        "previous_events_cleared": cleared,
        "reset_state_digest": record["state_digest"],
        "fresh_state_digest": fresh.state_digest(),
        "qualifies": False,
    }


def final_partial_check(samples: Sequence[float]) -> Dict[str, Any]:
    prefix = list(samples[:FINAL_PARTIAL_VALID])
    config = default_config()
    session = AnalysisSession(config, "partial", 0)
    event = session.process_frame(prefix, is_final=True,
                                  valid_samples=FINAL_PARTIAL_VALID)
    session.finalize()
    padding = FRAME_SAMPLES - FINAL_PARTIAL_VALID
    return {
        "valid_count": FINAL_PARTIAL_VALID,
        "frame_samples": FRAME_SAMPLES,
        "padding_samples": padding,
        "accepted_samples": session.total_samples,
        "advanced_by_valid_count": session.total_samples == FINAL_PARTIAL_VALID,
        "padding_zero": True,
        "event_validity": event["validity"],
        "event_interval": [event["source_start"], event["source_end"]],
        "interval_exact": (event["source_end"] - event["source_start"]
                           == FINAL_PARTIAL_VALID),
        "post_final_rejected": _post_final_rejected(session, prefix),
        "qualifies": False,
    }


def _post_final_rejected(session: AnalysisSession,
                         frame: Sequence[float]) -> bool:
    try:
        session.process_frame(frame, is_final=True,
                              valid_samples=len(frame))
    except ReferenceRejection as error:
        return error.code == "stream_closed"
    return False


def cross_hop_check(fixture: Dict[str, Any]) -> Dict[str, Any]:
    total = fixture["length_samples"]
    plans = {
        "frame_160": [FRAME_SAMPLES] * (total // FRAME_SAMPLES),
        "cycle_15": chunk_plan(total, [160, 320, 480, 800, 640]),
        "cycle_22": chunk_plan(total, [800, 480, 160, 320, 640]),
        "whole": [total],
    }
    results = {}
    digests = []
    for name, plan in plans.items():
        run = run_stream(fixture["samples"], chunk_sizes=plan,
                         session_id="hop_" + name)
        results[name] = {
            "chunks": len(plan),
            "accepted_samples": run["summary"]["total_samples"],
            "digest": run["digest"],
        }
        digests.append(run["digest"])
    return {
        "plans": results,
        "all_match": len(set(digests)) == 1,
        "accepted_samples": total,
        "final_partial_tested_separately": True,
        "scheduler_measured": False,
        "qualifies": False,
    }


def event_bus_check(events: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    base = dict(events[0])
    bus = EventBus(capacity=4)
    accepted = 0
    for index in range(6):
        candidate = dict(base)
        candidate["sequence"] = index + 1
        candidate["frame_index"] = index
        candidate["source_start"] = index * FRAME_SAMPLES
        candidate["source_end"] = (index + 1) * FRAME_SAMPLES
        result = bus.publish(candidate)
        if result["status"] == "accepted":
            accepted += 1
    overflow = bus.summary()
    bus.advance_epoch(1)
    stale = dict(base)
    stale["sequence"] = 1
    stale["epoch"] = 0
    stale_result = bus.publish(stale)
    fresh = dict(base)
    fresh["sequence"] = 2
    fresh["epoch"] = 1
    bus.publish(fresh)
    backwards = dict(base)
    backwards["sequence"] = 1
    backwards["epoch"] = 1
    backwards_result = bus.publish(backwards)
    summary = bus.summary()
    return {
        "capacity": 4,
        "overflow_accepted": accepted,
        "overflow_dropped": overflow["drop_count"],
        "overflow_reasons": sorted({item["reason"]
                                    for item in overflow["dropped"]}),
        "stale_epoch_dropped": stale_result["reason"] == "stale_epoch",
        "stale_sequence_dropped": backwards_result["reason"] == "stale_sequence",
        "epoch_advance_clears_queue": summary["queue_depth"] == 1,
        "total_dropped": summary["drop_count"],
        "qualifies": False,
    }


def invalid_vs_nonspeech_check(fixture: Dict[str, Any]) -> Dict[str, Any]:
    session = AnalysisSession(default_config(), "validity", 0)
    frames = _frame_list(fixture["samples"])
    session.process_frame(frames[0], validity="known")
    session.process_frame(frames[1], validity="invalid")
    session.process_frame(frames[2], validity="missing")
    session.process_frame(frames[3], validity="known")
    session.finalize()
    score = score_events(session.events, fixture)
    return {
        "known_events": score["scored_frames"],
        "invalid_events": score["invalid_frames"],
        "missing_events": score["missing_frames"],
        "invalid_probability_is_null": (
            session.events[1]["probability_micro"] is None),
        "missing_probability_is_null": (
            session.events[2]["probability_micro"] is None),
        "invalid_counted_as_nonspeech": score["invalid_treated_as_nonspeech"],
        "denominator_excludes_invalid": (
            score["scored_frames"] == 2),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Adverse cases
# ---------------------------------------------------------------------------

def _run_rejection(records: List[Dict[str, Any]], case_id: str,
                   state_probe, action) -> None:
    """Measure live state before/after a rejection; never force the result."""
    digest_before = state_probe()
    try:
        action()
    except ReferenceRejection as error:
        digest_after = state_probe()
        if not error.code:
            raise AssertionError("rejection_without_code:" + case_id)
        records.append({
            "case_id": case_id,
            "code": error.code,
            "status": "rejected",
            "state_digest_before": digest_before,
            "state_digest_after": digest_after,
            "state_unchanged": digest_after == digest_before,
        })
        return
    raise AssertionError("adverse_case_accepted:" + case_id)


def _valid_manifest() -> Dict[str, Any]:
    return {
        "asset_storage": "external",
        "candidate_id": COMPONENT,
        "license_id": "caller-declared-license",
        "runtime_id": "caller.runtime.v0",
        "source_revision": "0" * 40,
        "source_sha256": "1" * 64,
        "weights_byte_count": 1048576,
        "weights_sha256": "2" * 64,
    }


def _event_sample(session: AnalysisSession) -> Dict[str, Any]:
    return dict(session.events[0])


def adverse_rejections(fixture: Dict[str, Any]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    config = default_config()
    control_session = AnalysisSession(config, "adverse-control", 0)

    json_cases = (
        ("duplicate_json_key", '{"a":1,"a":2}'),
        ("nan_json_constant", '{"a":NaN}'),
        ("infinity_json_constant", '{"a":Infinity}'),
        ("neg_infinity_json_constant", '{"a":-Infinity}'),
        ("malformed_json", '{"a":'),
        ("json_root_array", '[1,2]'),
        ("json_trailing_data", '{"a":1}{"b":2}'),
        ("json_bom", '\ufeff{"a":1}'),
    )
    for case_id, text in json_cases:
        probe = control_session.state_digest
        action = (lambda text=text: load_strict_json_object_text(text)
                  if case_id == "json_root_array"
                  else load_strict_json_text(text))
        _run_rejection(records, case_id, probe, action)

    bad_configs = []
    for name, updates in (
        ("config_missing_field", {"clock_ppm": "remove"}),
        ("config_extra_field", {"extra": 1}),
        ("config_8000_hz", {"sample_rate_hz": 8000}),
        ("config_44100_hz", {"sample_rate_hz": 44100}),
        ("config_stereo", {"channels": 2}),
        ("config_256_frame", {"frame_samples": 256}),
        ("config_int16", {"sample_format": "int16"}),
        ("config_bool_rate", {"sample_rate_hz": True}),
        ("config_negative_epoch", {"epoch": -1}),
        ("config_bad_mode", {"execution_mode": "processing_thread"}),
        ("config_nonfinite_ppm", {"clock_ppm": float("nan")}),
        ("config_missing_origin_ns", {"origin_ns": "remove"}),
        ("config_first_input_negative", {"first_input_sample": -1}),
        ("config_sample_period_mismatch", {"sample_period_ns": 62501}),
        ("config_float_epoch", {"epoch": 0.0}),
        ("config_unsupported_resampling", {"resampling": "linear"}),
    ):
        candidate = dict(config)
        if updates.get("clock_ppm") == "remove":
            candidate.pop("clock_ppm")
        elif updates.get("origin_ns") == "remove":
            candidate.pop("origin_ns")
        else:
            candidate.update(updates)
        bad_configs.append((name, candidate))
    for case_id, candidate in bad_configs:
        _run_rejection(records, case_id, control_session.state_digest,
                       lambda candidate=candidate: validate_config(candidate))

    session = AnalysisSession(default_config(), "adverse", 0)
    valid_frame = list(fixture["samples"][:FRAME_SAMPLES])
    session.process_frame(valid_frame)

    frame_cases = (
        ("frame_missing_samples", valid_frame[:159], {}),
        ("frame_too_long", valid_frame + [0.0], {}),
        ("frame_nonfinite_nan", valid_frame[:-1] + [float("nan")], {}),
        ("frame_nonfinite_inf", valid_frame[:-1] + [float("inf")], {}),
        ("frame_nonfinite_neg_inf", valid_frame[:-1] + [float("-inf")], {}),
        ("frame_string_sample", valid_frame[:-1] + ["0.0"], {}),
        ("frame_bool_sample", valid_frame[:-1] + [True], {}),
        ("frame_wrong_epoch", valid_frame, {"epoch": 9}),
        ("frame_negative_epoch", valid_frame, {"epoch": -1}),
        ("frame_wrong_start_sample", valid_frame, {"start_sample": 0}),
        ("frame_partial_without_final", valid_frame[:80], {}),
        ("frame_partial_zero_valid", valid_frame, {"is_final": True,
                                                   "valid_samples": 0}),
        ("frame_partial_too_large", valid_frame, {"is_final": True,
                                                  "valid_samples": 161}),
        ("frame_nonzero_padding", valid_frame, {"is_final": True,
                                                "valid_samples": 100}),
        ("frame_invalid_validity_token", valid_frame, {"validity": "unknown"}),
        ("frame_probability_override_high", valid_frame,
         {"probability_override": 1000001}),
        ("frame_probability_override_negative", valid_frame,
         {"probability_override": -1}),
        ("frame_override_requires_known", valid_frame,
         {"validity": "invalid", "probability_override": 100}),
        ("frame_duplicate_sequence", valid_frame, {"sequence": 1}),
        ("frame_sequence_backwards", valid_frame, {"sequence": 0}),
    )
    for case_id, samples, options in frame_cases:
        _run_rejection(records, case_id, session.state_digest,
                       lambda samples=samples, options=options:
                       session.process_frame(samples, **options))

    final_session = AnalysisSession(default_config(), "final", 0)
    final_session.process_frame(valid_frame[:137], is_final=True,
                                valid_samples=137)
    _run_rejection(records, "frame_after_final", final_session.state_digest,
                   lambda: final_session.process_frame(valid_frame,
                                                      is_final=True))

    manifest = _valid_manifest()
    manifest_cases = (
        ("manifest_missing_hash", {"weights_sha256": "remove"}),
        ("manifest_bad_hash", {"weights_sha256": "zz"}),
        ("manifest_relative_path", {"asset_storage": "relative"}),
        ("manifest_wrong_candidate", {"candidate_id": "crnn"}),
        ("manifest_missing_license", {"license_id": "unknown"}),
        ("manifest_extra_field", {"extra": 1}),
        ("manifest_missing_field", {"runtime_id": "remove"}),
        ("manifest_wrong_size", {"weights_byte_count": 0}),
        ("manifest_oversize", {"weights_byte_count": 512 * 1024 * 1024 + 1}),
        ("manifest_bad_revision", {"source_revision": "abc"}),
        ("manifest_bad_runtime", {"runtime_id": "Bad Runtime"}),
        ("manifest_vendored", {"asset_storage": "vendored"}),
    )
    for case_id, updates in manifest_cases:
        candidate = dict(manifest)
        for key, value in updates.items():
            if value == "remove":
                candidate.pop(key, None)
            else:
                candidate[key] = value
        _run_rejection(records, case_id, session.state_digest,
                       lambda candidate=candidate:
                       validate_caller_manifest(candidate))

    event = _event_sample(session)
    event_cases = (
        ("event_bad_epoch", {"epoch": "0"}),
        ("event_bad_interval", {"source_end": 0}),
        ("event_nonfinite_probability", {"probability_micro": float("nan")}),
        ("event_probability_out_of_range", {"probability_micro": 1000001}),
        ("event_bad_validity", {"validity": "unknown"}),
        ("event_missing_probability", {"probability_micro": None}),
        ("event_bad_speech", {"speech": "yes"}),
        ("event_extra_field", {"extra": 1}),
        ("event_bad_sequence", {"sequence": 0}),
    )
    for case_id, updates in event_cases:
        candidate = dict(event)
        candidate.update(updates)
        _run_rejection(records, case_id, session.state_digest,
                       lambda candidate=candidate: validate_event(candidate))

    reset_session = AnalysisSession(default_config(), "reset-adverse", 0)
    for case_id, epoch in (("reset_epoch_zero", 0),
                           ("reset_epoch_non_increasing", -1),
                           ("reset_epoch_bool", True)):
        _run_rejection(records, case_id, reset_session.state_digest,
                       lambda epoch=epoch: reset_session.reset(epoch))

    bus = EventBus(capacity=2)
    bus_probe = lambda: object_digest(bus.summary())
    _run_rejection(records, "bus_epoch_zero", bus_probe,
                   lambda: bus.advance_epoch(0))
    _run_rejection(records, "bus_epoch_bool", bus_probe,
                   lambda: bus.advance_epoch(True))

    _run_rejection(records, "chunk_plan_length_mismatch",
                   control_session.state_digest,
                   lambda: run_stream(fixture["samples"],
                                      chunk_sizes=[160, 160]))
    _run_rejection(records, "chunk_plan_zero",
                   control_session.state_digest,
                   lambda: run_stream(fixture["samples"],
                                      chunk_sizes=[0] * 260))
    return records


# ---------------------------------------------------------------------------
# Board identity (stable linked row only)
# ---------------------------------------------------------------------------

def board_row() -> Dict[str, Any]:
    payload = load_strict_json(SOURCE_ROOT / TASK_BOARD_REL)
    tasks = payload.get("tasks") if isinstance(payload, dict) else None
    if not isinstance(tasks, list):
        raise ReferenceRejection("board_tasks_missing")
    matches = [task for task in tasks
               if isinstance(task, dict) and task.get("id") == TASK_ID]
    if len(matches) != 1:
        raise ReferenceRejection("board_task_row_ambiguous")
    row = matches[0]
    stable = {
        "id": row.get("id"),
        "title": row.get("title"),
        "repository": row.get("repository"),
        "mode": row.get("mode"),
        "component": row.get("component"),
        "depends_on": row.get("depends_on"),
    }
    return {
        "full_tasks_json_hashed": False,
        "note": (
            "Only stable linked-row fields are read and gated. The mutable "
            "full plan/swarm/TASKS.json is never hashed, pinned or used as a "
            "digest source."
        ),
        "stable_fields": stable,
        "stable_sha256": object_digest(stable),
    }


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "EB-01",
        "requirement": (
            "Exact CRNN VAD architecture: layer topology, convolution and "
            "recurrent cell definitions, parameter count, input rate, hop, "
            "window, feature normalization and output frame geometry."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-02",
        "requirement": (
            "Exact checkpoint/weights artifact with immutable SHA-256, byte "
            "size, weight license and training-data statement."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-03",
        "requirement": (
            "Runnable source repository, immutable revision, build recipe, "
            "runtime/library identity and opt-in adapter or descriptor."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-04",
        "requirement": (
            "Code, weight, training-data and corpus rights plus attribution, "
            "notice, redistribution, product-use and derivative-output review."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-05",
        "requirement": (
            "Rights-cleared, label-complete, task-matched held-out speech "
            "cohort with frozen candidate outputs for accuracy, FN/FP and "
            "boundary qualification."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-06",
        "requirement": (
            "Exact candidate numeric output, calibration, timestamp/event "
            "protocol and byte-level parity with the proposal boundary."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-07",
        "requirement": (
            "Target-device pacing, availability, memory, power and deadline "
            "evidence at the exact runtime."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-08",
        "requirement": (
            "Opt-in provider intake, descriptor review, independent exact-head "
            "review and default/release approval."
        ),
        "status": "blocked",
        "present": False,
    },
)

RELEASE_GATES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "RG-01",
        "status": "blocked",
        "requirement": (
            "Pin the exact licensed CRNN VAD source, checkpoint and runtime "
            "with immutable revisions, weight digest, license identity and "
            "documented input/output geometry."
        ),
    },
    {
        "id": "RG-02",
        "status": "blocked",
        "requirement": (
            "Admit an isolated hash-pinned runtime, reproduce the build and "
            "verify weight identity with fail-closed absent behavior."
        ),
    },
    {
        "id": "RG-03",
        "status": "blocked",
        "requirement": (
            "Clear code, weight, training-data and corpus rights plus "
            "attribution, notices, redistribution, product-use and "
            "derivative-output review."
        ),
    },
    {
        "id": "RG-04",
        "status": "blocked",
        "requirement": (
            "Map exact candidate rate, hop, window, features, timestamps and "
            "event protocol into the installed mono boundary with byte-level "
            "parity."
        ),
    },
    {
        "id": "RG-05",
        "status": "blocked",
        "requirement": (
            "Qualify on a rights-cleared task-matched held-out speech cohort "
            "with independently pinned FN/FP, boundary, calibration and "
            "stratified validity scoring."
        ),
    },
    {
        "id": "RG-06",
        "status": "blocked",
        "requirement": (
            "Measure streaming state, reset, stale/dropped events, "
            "availability, cross-hop behavior and nonfinite handling at the "
            "exact runtime."
        ),
    },
    {
        "id": "RG-07",
        "status": "blocked",
        "requirement": (
            "Measure target-device pacing, timing, memory and power with "
            "independent listening or downstream controls as applicable."
        ),
    },
    {
        "id": "RG-08",
        "status": "blocked",
        "requirement": (
            "Complete opt-in provider intake, descriptor review, independent "
            "exact-head review and default/release approval."
        ),
    },
)

ACCEPTANCE_ITEMS: Dict[str, Dict[str, str]] = {
    "timestamped_probabilities_scored": {
        "status": "synthetic_only",
        "evidence": (
            "Per-frame timestamped probability_micro records are scored with "
            "an integer Brier metric on the synthetic fixture only."
        ),
    },
    "event_boundaries_scored": {
        "status": "synthetic_only",
        "evidence": (
            "Detected speech runs are compared with fixture-construction "
            "active segments; no candidate boundary output exists."
        ),
    },
    "quiet_and_active_speech": {
        "status": "synthetic_only",
        "evidence": (
            "The fixture declares active and quiet segments; labels come from "
            "construction, not from a CRNN."
        ),
    },
    "idle_noise": {
        "status": "synthetic_only",
        "evidence": (
            "Deterministic low-amplitude integer LCG noise covers lead, mid "
            "and tail idle regions."
        ),
    },
    "known_positives_and_negatives": {
        "status": "synthetic_only",
        "evidence": (
            "Frame labels are exact fixture-construction positives and "
            "negatives; there are no real recordings."
        ),
    },
    "onset_offset_delay": {
        "status": "synthetic_only",
        "evidence": (
            "Onset and offset frame delays are measured against the synthetic "
            "segment boundaries only."
        ),
    },
    "stratified_fn_fp": {
        "status": "synthetic_only",
        "evidence": (
            "FN/FP rates are stratified over active-speech and quiet-noise "
            "synthetic frames; no held-out cohort exists."
        ),
    },
    "validity_separate_from_nonspeech": {
        "status": "synthetic_only",
        "evidence": (
            "Invalid and missing frames carry null probability, are excluded "
            "from denominators and are never scored as nonspeech."
        ),
    },
    "independent_state": {
        "status": "synthetic_only",
        "evidence": (
            "Two interleaved sessions produce the same digests as independent "
            "solo runs."
        ),
    },
    "exact_source_intervals": {
        "status": "synthetic_only",
        "evidence": (
            "Every event uses exact half-open sample intervals; the final "
            "partial frame advances by its valid count only."
        ),
    },
    "availability": {
        "status": "synthetic_only",
        "evidence": (
            "Availability is a declared monotone synthetic formula; no device "
            "clock or measured service time exists."
        ),
    },
    "dropped_stale_events": {
        "status": "synthetic_only",
        "evidence": (
            "A bounded synthetic event bus records stale-epoch, stale-sequence "
            "and queue-full drops explicitly."
        ),
    },
    "cross_hop_behavior": {
        "status": "synthetic_only",
        "evidence": (
            "Four caller chunk plans reproduce identical event digests; no "
            "scheduler or device hop was measured."
        ),
    },
}


def scope_record() -> Dict[str, Any]:
    return {
        "write_scope": "docs/task-evidence/crnn-vad/ only",
        "board_touched": False,
        "handoffs_touched": False,
        "other_worktrees_touched": False,
        "shared_build_touched": False,
        "ci_touched": False,
        "provider_registered": False,
        "processor_exposed": False,
        "network_access": False,
        "downloaded_anything": False,
        "real_audio_used": False,
        "real_weights_used": False,
        "real_runtime_used": False,
        "installed_v0_changed": False,
    }


def boundary_record() -> Dict[str, Any]:
    return {
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "shared_build_or_ci_change": False,
        "processor_exposure": False,
        "adapter_json_added": False,
        "readiness_json_added": False,
        "asset_bundled": False,
        "weights_vendored": False,
        "native_engine_built": False,
        "sdk_data_dir_added": False,
        "network_access": False,
        "audio_added": False,
        "corpus_added": False,
    }


def negative_claims() -> List[str]:
    return [
        "No CRNN source, convolution, recurrent layer, checkpoint, weight, "
        "learned posterior, licensed runtime or adapter is present, copied, "
        "downloaded, loaded, imported or executed.",
        "No real speech, corpus, recording, consent, listening, quality, "
        "intelligibility, ASR or device result exists.",
        "No CRNN accuracy, FN/FP, calibration, boundary, latency or "
        "throughput value is claimed; all measured values belong to the "
        "deterministic surrogate on a synthetic fixture.",
        "No exact candidate sample rate, hop, window, feature normalization, "
        "parameter count, timestamp protocol or output geometry is asserted.",
        "No installed v0, public API/ABI, descriptor, registry, default, "
        "shared build, CI, board, handoff or other worktree change is made.",
        "No control signal, gate, endpointing rule, processor exposure or "
        "release qualification is produced.",
        "No device timing, pacing, power, production availability or hard "
        "real-time claim is made.",
    ]


def reopen_condition() -> str:
    return (
        "Pin the exact licensed CRNN VAD architecture, checkpoint and runtime "
        "with immutable source and weight digests, documented geometry and "
        "feature/timestamp protocol; admit an isolated hash-pinned runtime; "
        "clear code, weight, training-data and corpus rights; map exact "
        "candidate output into the installed mono boundary with parity; "
        "qualify FN/FP, boundary and calibration on a rights-cleared "
        "task-matched held-out speech cohort; measure target timing; and "
        "complete opt-in provider intake. Until every condition is closed the "
        "candidate stays DEFER, incomplete and not qualified."
    )


def build_report() -> Dict[str, Any]:
    fixture = build_fixture()
    run = run_stream(fixture["samples"], session_id="report")
    score = score_events(run["events"], fixture)
    boundaries = boundary_report(run["events"], fixture)
    availability = availability_report(run["events"])
    validity = validity_report(run["events"])
    drafting = AnalysisSession(default_config(), "validity-probe", 0)
    frames = _frame_list(fixture["samples"])
    drafting.process_frame(frames[0])
    drafting.process_frame(frames[1], validity="invalid")
    drafting.process_frame(frames[2], validity="missing")
    drafting.process_frame(frames[3])
    drafting.finalize()
    return {
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
        "acceptance_profile": {
            "profile": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "required_items": {name: dict(item)
                               for name, item in ACCEPTANCE_ITEMS.items()},
        },
        "profile_blockers": [],
        "candidate": {
            "name": TITLE,
            "evidence_status": "blocked",
            "source_record": (
                "research/voice-enhancement-20261101/candidate_matrix.csv "
                "record 3"
            ),
            "finding": (
                "No exact CRNN architecture/checkpoint/source or adapter is "
                "selected; accuracy and performance cannot be measured for an "
                "undefined candidate."
            ),
            "baseline": "WebRTC and Silero integration paths",
            "report_paths": [
                "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md",
                "research/voice-enhancement-20261101/agent-segmentation/REPORT.md",
            ],
            "paper_reference": None,
            "architecture": None,
            "checkpoint": None,
            "source_revision": None,
            "source_sha256": None,
            "weights_sha256": None,
            "parameter_count": None,
            "reported_sample_rate_hz": None,
            "reported_hop_samples": None,
            "reported_window_samples": None,
            "reported_output_geometry": None,
            "license": None,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "adapter_present": False,
            "geometry_documented": False,
            "exact_numeric_output_present": False,
            "implemented_here": False,
        },
        "reference": {
            "status": "blocked",
            "local_identity": SURROGATE_ID,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "implementation_present": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "surrogate_is_candidate": False,
            "surrogate_is_crnn": False,
            "note": (
                "The local probe is an original integer RMS/zero-crossing "
                "surrogate, not CRNN and not derived from candidate code."
            ),
        },
        "format": {
            "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
            "sdk_v0_channels": CHANNELS,
            "sdk_v0_frame_samples": FRAME_SAMPLES,
            "sdk_v0_sample_format": SAMPLE_FORMAT,
            "sdk_v0_sample_period_ns": SAMPLE_NS,
            "resampling": "none",
            "candidate_reported_sample_rate_hz": None,
            "candidate_reported_hop_samples": None,
            "candidate_geometry_documented": False,
        },
        "fixture": fixture_spec(fixture),
        "surrogate_model": {
            "sha256": surrogate_model_digest(),
            "spec": surrogate_model_spec(),
            "independently_pinned": True,
            "qualifies": False,
        },
        "scorer": {
            "sha256": scoring_protocol_digest(),
            "spec": scoring_protocol_spec(),
            "independently_pinned": True,
            "oracle_used_for_score": False,
            "qualifies": False,
        },
        "results": {
            "probabilities": {
                "scored_frames": score["scored_frames"],
                "brier_micro": score["brier_micro"],
                "accuracy_ppm": score["accuracy_ppm"],
                "probability_scale": PROBABILITY_SCALE,
                "candidate_probability_parity": False,
                "qualifies": False,
            },
            "boundaries": boundaries,
            "detections": {
                "positives": score["positives"],
                "negatives": score["negatives"],
                "true_positives": score["true_positives"],
                "false_positives": score["false_positives"],
                "false_negatives": score["false_negatives"],
                "true_negatives": score["true_negatives"],
                "fn_ppm": score["fn_ppm"],
                "fp_ppm": score["fp_ppm"],
                "strata": ["active_speech", "quiet_noise"],
                "heldout": False,
                "qualifies": False,
            },
            "validity": validity,
            "availability": availability,
            "events": {
                "total": len(run["events"]),
                "digest": run["digest"],
                "first_sequence": run["events"][0]["sequence"],
                "last_sequence": run["events"][-1]["sequence"],
                "sequence_contiguous": (
                    [event["sequence"] for event in run["events"]]
                    == list(range(1, len(run["events"]) + 1))
                ),
                "speech_events": len(run["runs"]),
                "qualifies": False,
            },
            "cross_hop": cross_hop_check(fixture),
        },
        "controls": {
            "independent_state": independent_state_check(fixture),
            "reset": reset_check(fixture),
            "final_partial": final_partial_check(fixture["samples"]),
            "event_bus": event_bus_check(run["events"]),
            "invalid_vs_nonspeech": invalid_vs_nonspeech_check(fixture),
            "threshold_sensitivity": threshold_sensitivity_check(
                run["events"], fixture),
            "config_adverse": {
                "rejected": True,
                "qualifies": False,
            },
            "frame_adverse": {
                "rejected": True,
                "qualifies": False,
            },
            "drafting_sessions_isolated": True,
        },
        "adverse_rejections": adverse_rejections(fixture),
        "adverse_all_rejected": True,
        "external_artifacts": {
            "status": "blocked",
            "any_present": False,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "adapter_present": False,
            "corpus_present": False,
            "note": (
                "No CRNN source, checkpoint, runtime, adapter, real audio or "
                "corpus is staged in this package."
            ),
        },
        "licensing": {
            "reported_upstream_license": None,
            "license_text_staged": False,
            "attribution_notice_staged": False,
            "weights_terms_staged": False,
            "training_data_statement_staged": False,
            "corpus_rights_reviewed": False,
            "redistribution_reviewed": False,
            "product_use_reviewed": False,
            "review_status": "blocked",
        },
        "caller_asset": {
            "contract_id": CALLER_SCHEMA,
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "required_fields": sorted(CALLER_MANIFEST_FIELDS),
            "present_behavior": (
                "validate_declaration_identity_only; do_not_load_or_execute"
            ),
            "absent_behavior": "reject_before_processing",
            "separate_archive_required": True,
            "status": "shape_only_not_qualified",
            "real_candidate_asset_validated": False,
        },
        "board_row": board_row(),
        "boundary": boundary_record(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "scope": scope_record(),
        "qualification": {
            "status": QUALIFICATION,
            "qualifies": False,
            "all_required_results_present": False,
            "missing_result_promoted": False,
            "exact_source_present": False,
            "exact_weights_present": False,
            "exact_runtime_outputs_present": False,
            "candidate_geometry_documented": False,
            "candidate_architecture_pinned": False,
            "checkpoint_pinned": False,
            "timestamped_probability_parity": False,
            "event_boundary_parity": False,
            "rights_cleared_cohort": False,
            "task_matched_heldout_score": False,
            "stratified_fn_fp_on_heldout": False,
            "calibration_measured": False,
            "timing_measured": False,
            "real_corpus_used": False,
            "listening": False,
        },
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "release_gates": [dict(item) for item in RELEASE_GATES],
        "reopen_condition": reopen_condition(),
        "negative_claims": negative_claims(),
        "repeatability": {
            "rounds": 3,
            "byte_identical": True,
            "note": (
                "run.py regenerates every generated payload three times and "
                "refuses to write unless all rounds are byte-identical."
            ),
        },
        "scope_note": (
            "Bounded, deterministic, task-local proposal evidence only; no "
            "candidate source, weight, runtime, corpus, provider registration, "
            "ABI, registry, default, shared build, CI, benchmark or release "
            "claim."
        ),
    }


def build_contract(report: Dict[str, Any], report_digest: str) -> Dict[str, Any]:
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
        "surrogate_model": report["surrogate_model"],
        "scorer": report["scorer"],
        "artifact_pins": artifact_pins(report_digest, sidecar_digest),
        "board_row": report["board_row"],
        "boundary": report["boundary"],
        "boundary_pins": report["boundary_pins"],
        "source_pins": report["source_pins"],
        "scope": report["scope"],
        "reference": report["reference"],
        "exact_blockers": report["exact_blockers"],
        "release_gates": report["release_gates"],
        "reopen_condition": report["reopen_condition"],
        "negative_claims": report["negative_claims"],
        "caller_asset_contract": report["caller_asset"],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no CRNN source, convolution, recurrent layer, checkpoint, weight, "
            "runtime or adapter is downloaded, copied, loaded or executed",
            "the integer RMS/zero-crossing surrogate is not CRNN and cannot "
            "qualify the candidate",
            "no candidate rate, hop, window, parameter count, timestamp "
            "protocol or output geometry is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


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


def sources_bytes(overrides: Optional[Dict[str, bytes]] = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-CRNN-VAD; source: paths are "
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
            if not full.is_file():
                raise ReferenceRejection("missing_artifact:" + name)
            digest = file_digest(full)
        lines.append(f"{digest}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")


__all__ = [
    "AnalysisSession", "EventBus", "ReferenceRejection", "adverse_rejections",
    "artifact_pins", "availability_report", "board_row", "boundary_report",
    "build_contract", "build_fixture", "build_report", "canonical_report",
    "canonical_text", "chunk_plan", "cross_hop_check", "default_config",
    "event_bus_check", "file_digest", "final_partial_check", "fixture_spec",
    "frame_features", "independent_state_check", "invalid_vs_nonspeech_check",
    "load_strict_json", "load_strict_json_text", "object_digest",
    "probability_micro", "reset_check", "run_stream", "score_events",
    "scoring_protocol_spec", "sha256_bytes", "source_pins", "sources_bytes",
    "surrogate_model_spec", "validate_caller_manifest", "validate_config",
    "validate_event",
]
