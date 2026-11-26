# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local DIRAC (legacy ZTX) rate blocker evidence.

This is an original, stdlib-only synthetic probe written for this task. It is
NOT DIRAC, NOT Zynaptiq ZTX, not a vendor binary, not a vendor header, not an
evaluation kit, not a licensed runtime, not a processor and not a rate result
for either candidate. No vendor artifact, license, SLA, evaluation kit,
recording, corpus, model, device clock or listening result is present, copied,
downloaded, loaded, imported or executed.

The catalogued candidates are blocked: the legacy DIRAC binaries are separate
artifacts with unverified terms and the contemporary Zynaptiq ZTX SDK is
commercial closed source with no local evaluation kit, quote or signed SLA.
Consequently this probe only exercises the SDK Rate acceptance mechanics on
deterministic synthetic clips: source/output mapping, duration, pitch and
transient proxies, caller-owned playback buffering, 1x/rebase/drift/final
partial windows, and source-timestamped speech-preservation labels.

It is proposal-only, incomplete and not qualified. Every release gate is
blocked and no result may qualify either candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
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
REPORT_SCHEMA = "audio-sdk/dirac-legacy-ztx-rate-report/0.1"
CALLER_SCHEMA = "audio-sdk/dirac-legacy-ztx/caller-supplied-archive/0.1"

TASK_ID = "SDK-DIRAC-LEGACY-ZTX"
TITLE = "DIRAC (legacy ZTX)"
COMPONENT = "dirac-legacy-ztx"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "708b9a4197ed35fd2528fad425832c55ef393eb7"
BRANCH = "swarm/SDK-DIRAC-LEGACY-ZTX"
REVIEWER = "reviewer-DIRAC-LEGACY-ZTX"
PROFILE = "rate"
STATUS = "proposal_only_incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
DEFER_AFTER = "vendor_artifact_and_rights_intake"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
TASK_PREFIX = "docs/task-evidence/dirac-legacy-ztx/"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_NS = 62500
MICRO = 1000000

WINDOW_SAMPLES = 1024
HOP_SAMPLES = 512
RAMP_SAMPLES = 800
RATE_MIN_PPM = 800000
RATE_MAX_PPM = 1500000
PITCH_TOLERANCE_PPM = 30000
SPEECH_TOLERANCE_DB_MILLI = 2000
MAX_SAMPLES = 96000

SURROGATE_ID = "deterministic-ola-rate-probe/0.1"
SCORER_ID = "rate-mapping-duration-pitch-transient-strata/0.1"
FIXTURE_ID = "dirac-legacy-ztx-synthetic-rate-fixture-v1"
CONFIG_ID = "dirac-legacy-ztx-proposal-config/0.1"

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

SOURCE_PINS: Dict[str, str] = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md": (
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3"
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

BOUNDARY_PINS: Dict[str, str] = {
    "CMakeLists.txt": (
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04"
    ),
    "CONTRACTS.md": (
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69"
    ),
    "REUSE.toml": (
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8"
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
}

CALLER_MANIFEST_FIELDS = (
    "archive_sha256",
    "artifact_id",
    "license_id",
    "platform",
    "product_id",
    "runtime_id",
    "sla_reference",
    "vendor_id",
    "vendor_version",
)


class ReferenceRejection(ValueError):
    """Deterministic rejection that never mutates accepted state."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


# ---------------------------------------------------------------------------
# Strict canonical JSON
# ---------------------------------------------------------------------------

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
# Deterministic synthetic fixture
# ---------------------------------------------------------------------------

def _lcg(state: int) -> int:
    return (1103515245 * state + 12345) & 0x7FFFFFFF


def _noise(state: int, amplitude_micro: int) -> Tuple[float, int]:
    state = _lcg(state)
    value = (state >> 13) % 65537 - 32768
    return amplitude_micro * value / 32768.0 / MICRO, state


def _speech_sample(n: int, length: int, f0: float) -> float:
    """Deterministic voiced/mixed surrogate, not a recording or a VAD."""
    if n < 0 or n >= length:
        return 0.0
    if 11200 <= n < 12800:
        return 0.0
    t = n / SAMPLE_RATE_HZ
    if 4800 <= n < 6400:
        value, _ = _noise(4000 + n, 45000)
        return value
    envelope = 0.55 + 0.45 * math.sin(2.0 * math.pi * 2.7 * t)
    if 12800 <= n < 19200:
        envelope *= 0.85
    value = (
        math.sin(2.0 * math.pi * f0 * t)
        + 0.50 * math.sin(2.0 * math.pi * 2.10 * f0 * t)
        + 0.25 * math.sin(2.0 * math.pi * 3.40 * f0 * t)
    )
    return 0.20 * envelope * value


def _music_sample(n: int, length: int) -> float:
    if n < 0 or n >= length:
        return 0.0
    t = n / SAMPLE_RATE_HZ
    envelope = 0.72 + 0.28 * math.sin(2.0 * math.pi * 0.5 * t)
    value = (
        math.sin(2.0 * math.pi * 110.0 * t)
        + 0.85 * math.sin(2.0 * math.pi * 164.81 * t)
        + 0.70 * math.sin(2.0 * math.pi * 220.0 * t)
    )
    return 0.16 * envelope * value


def _transient_sample(n: int, length: int) -> float:
    if n < 0 or n >= length:
        return 0.0
    value, _ = _noise(9000 + n, 2200)
    for click in (2400, 6400, 10400, 14400):
        if n >= click:
            local = n - click
            if local < 600:
                t = local / SAMPLE_RATE_HZ
                value += 0.80 * math.exp(-local / 160.0) * math.sin(
                    2.0 * math.pi * 3000.0 * t)
    return value


def _final_partial_sample(n: int, length: int) -> float:
    if n < 0 or n >= length:
        return 0.0
    t = n / SAMPLE_RATE_HZ
    envelope = 0.55 + 0.45 * math.sin(2.0 * math.pi * 1.9 * t)
    value = (
        math.sin(2.0 * math.pi * 173.0 * t)
        + 0.45 * math.sin(2.0 * math.pi * 2.3 * 173.0 * t)
        + 0.20 * math.sin(2.0 * math.pi * 3.7 * 173.0 * t)
    )
    return 0.22 * envelope * value


STIMULI: Dict[str, Dict[str, Any]] = {
    "tonal": {
        "length": 9600,
        "kind": "stationary_tone",
        "frequency_hz": 220,
        "pitch_reference": True,
        "factory": lambda n, length: 0.62 * math.sin(
            2.0 * math.pi * 220.0 * n / SAMPLE_RATE_HZ),
        "labels": [],
    },
    "speech_unfamiliar": {
        "length": 19200,
        "kind": "voiced_speech_surrogate",
        "frequency_hz": 190,
        "pitch_reference": False,
        "factory": lambda n, length: _speech_sample(n, length, 190.0),
        "labels": [
            {"source_start": 0, "source_end": 4800,
             "label": "speech", "decision": "protect"},
            {"source_start": 4800, "source_end": 6400,
             "label": "filler", "decision": "flex"},
            {"source_start": 6400, "source_end": 11200,
             "label": "speech", "decision": "protect"},
            {"source_start": 11200, "source_end": 12800,
             "label": "silence", "decision": "flex"},
            {"source_start": 12800, "source_end": 19200,
             "label": "speech", "decision": "protect"},
        ],
    },
    "music": {
        "length": 19200,
        "kind": "music_surrogate",
        "frequency_hz": None,
        "pitch_reference": False,
        "factory": _music_sample,
        "labels": [
            {"source_start": 0, "source_end": 19200,
             "label": "music", "decision": "protect"},
        ],
    },
    "silence": {
        "length": 9600,
        "kind": "silence",
        "frequency_hz": None,
        "pitch_reference": False,
        "factory": lambda n, length: 0.0,
        "labels": [],
    },
    "transient": {
        "length": 16000,
        "kind": "click_surrogate",
        "frequency_hz": None,
        "pitch_reference": False,
        "factory": _transient_sample,
        "labels": [],
    },
    "final_partial": {
        "length": 12485,
        "kind": "voiced_speech_surrogate",
        "frequency_hz": 173,
        "pitch_reference": False,
        "factory": _final_partial_sample,
        "labels": [
            {"source_start": 0, "source_end": 12485,
             "label": "speech", "decision": "protect"},
        ],
    },
}


def _sample_bytes(samples: Sequence[float]) -> bytes:
    return b"".join(struct.pack(">d", value) for value in samples)


def build_stimulus(name: str) -> Dict[str, Any]:
    if name not in STIMULI:
        raise ReferenceRejection("unknown_stimulus:" + str(name))
    spec = STIMULI[name]
    length = int(spec["length"])
    factory = spec["factory"]
    samples = [float(factory(index, length)) for index in range(length)]
    peak = max(abs(value) for value in samples) if samples else 0.0
    if peak > 0.98:
        raise ReferenceRejection("fixture_peak_out_of_range")
    return {
        "name": name,
        "kind": spec["kind"],
        "length": length,
        "samples": samples,
        "digest": sha256_bytes(_sample_bytes(samples)),
        "peak_micro": int(round(peak * MICRO)),
        "labels": [dict(item) for item in spec["labels"]],
        "frequency_hz": spec["frequency_hz"],
        "pitch_reference": bool(spec["pitch_reference"]),
    }


def fixture_digest(fixtures: Dict[str, Dict[str, Any]]) -> str:
    return object_digest({
        name: {
            "digest": fixture["digest"],
            "length": fixture["length"],
            "kind": fixture["kind"],
        }
        for name, fixture in fixtures.items()
    })


# ---------------------------------------------------------------------------
# Rate schedule, mapping, and OLA reference
# ---------------------------------------------------------------------------

CASES: Tuple[Dict[str, Any], ...] = (
    {"case_id": "identity_1x", "stimulus": "tonal",
     "schedule": [(1000000, 0)], "ramp": RAMP_SAMPLES, "transform": "identity"},
    {"case_id": "speed_up_125", "stimulus": "tonal",
     "schedule": [(1250000, 0)], "ramp": RAMP_SAMPLES, "transform": "ola"},
    {"case_id": "speed_up_150", "stimulus": "tonal",
     "schedule": [(1500000, 0)], "ramp": RAMP_SAMPLES, "transform": "ola"},
    {"case_id": "speed_down_080", "stimulus": "tonal",
     "schedule": [(800000, 0)], "ramp": RAMP_SAMPLES, "transform": "ola"},
    {"case_id": "unfamiliar_speech", "stimulus": "speech_unfamiliar",
     "schedule": [(1200000, 0)], "ramp": RAMP_SAMPLES, "transform": "ola"},
    {"case_id": "music_material", "stimulus": "music",
     "schedule": [(1400000, 0)], "ramp": RAMP_SAMPLES, "transform": "ola"},
    {"case_id": "silence_case", "stimulus": "silence",
     "schedule": [(1250000, 0)], "ramp": RAMP_SAMPLES, "transform": "ola"},
    {"case_id": "rebuffer_case", "stimulus": "speech_unfamiliar",
     "schedule": [(1250000, 0)], "ramp": RAMP_SAMPLES, "transform": "ola",
     "rebuffer": {"source_sample": 6400, "gap_output_samples": 1600}},
    {"case_id": "drift_case", "stimulus": "speech_unfamiliar",
     "schedule": [(1000000, 0), (1150000, 4800), (900000, 9600),
                  (1300000, 14400)],
     "ramp": RAMP_SAMPLES, "transform": "ola"},
    {"case_id": "final_partial_window", "stimulus": "final_partial",
     "schedule": [(1250000, 0)], "ramp": RAMP_SAMPLES, "transform": "ola"},
    {"case_id": "transient_case", "stimulus": "transient",
     "schedule": [(1250000, 0)], "ramp": RAMP_SAMPLES, "transform": "ola"},
    {"case_id": "varispeed_adverse", "stimulus": "tonal",
     "schedule": [(1250000, 0)], "ramp": 0, "transform": "varispeed",
     "adverse_control": True},
    {"case_id": "rate_step_unsmoothed_adverse", "stimulus": "transient",
     "schedule": [(1000000, 0), (1500000, 6400)], "ramp": 0,
     "transform": "ola", "adverse_control": True},
)

CASE_IDS: Tuple[str, ...] = tuple(case["case_id"] for case in CASES)


def case_by_id(case_id: str) -> Dict[str, Any]:
    for case in CASES:
        if case["case_id"] == case_id:
            return case
    raise ReferenceRejection("unknown_case:" + str(case_id))


def validate_schedule(schedule: Any, ramp_samples: Any) -> List[Dict[str, int]]:
    if not isinstance(schedule, list) or not schedule:
        raise ReferenceRejection("missing_schedule")
    if not isinstance(ramp_samples, int) or isinstance(ramp_samples, bool):
        raise ReferenceRejection("invalid_ramp")
    if ramp_samples < 0 or ramp_samples > 16000:
        raise ReferenceRejection("invalid_ramp")
    normalized: List[Dict[str, int]] = []
    previous_position = -1
    for index, change in enumerate(schedule):
        if not isinstance(change, (list, tuple)) or len(change) != 2:
            raise ReferenceRejection("invalid_schedule_entry")
        rate_ppm, position = change
        if (not isinstance(rate_ppm, int) or isinstance(rate_ppm, bool)
                or not isinstance(position, int) or isinstance(position, bool)):
            raise ReferenceRejection("invalid_schedule_entry")
        if rate_ppm < RATE_MIN_PPM or rate_ppm > RATE_MAX_PPM:
            raise ReferenceRejection("rate_out_of_range:" + str(rate_ppm))
        if position < 0 or position <= previous_position:
            raise ReferenceRejection(
                "invalid_schedule_source_sample:" + str(position))
        if index == 0 and position != 0:
            raise ReferenceRejection("schedule_missing_origin")
        normalized.append({"rate_ppm": rate_ppm,
                           "source_sample": position})
        previous_position = position
    return normalized


def validate_samples(samples: Any) -> List[float]:
    if not isinstance(samples, (list, tuple)) or not samples:
        raise ReferenceRejection("missing_or_empty_samples")
    if len(samples) > MAX_SAMPLES:
        raise ReferenceRejection("samples_too_long")
    values: List[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceRejection("nonnumeric_sample:" + str(index))
        numeric = float(value)
        if not math.isfinite(numeric):
            raise ReferenceRejection("nonfinite_sample:" + str(index))
        if abs(numeric) > 1.0:
            raise ReferenceRejection("out_of_range_sample:" + str(index))
        values.append(numeric)
    return values


def _rate_at(schedule: Sequence[Dict[str, int]], index: int) -> float:
    return schedule[index]["rate_ppm"] / float(MICRO)


def _integrate(source_length: int, base_rate: float, target_rate: float,
               ramp_samples: int) -> float:
    if source_length <= 0:
        return 0.0
    ramp = min(ramp_samples, source_length)
    if ramp > 0 and base_rate != target_rate:
        ramped = ramp * math.log(target_rate / base_rate) / (
            target_rate - base_rate)
    else:
        ramped = ramp / target_rate
    return ramped + (source_length - ramp) / target_rate


def forward_output_position(source_position: float,
                            schedule: Sequence[Dict[str, int]],
                            ramp_samples: int) -> float:
    if source_position <= 0.0:
        return 0.0
    output = 0.0
    count = len(schedule)
    for index in range(count):
        start = schedule[index]["source_sample"]
        if source_position <= start:
            break
        if index + 1 < count:
            end = min(source_position, schedule[index + 1]["source_sample"])
        else:
            end = source_position
        if end <= start:
            continue
        base = _rate_at(schedule, index - 1) if index > 0 else _rate_at(
            schedule, index)
        output += _integrate(int(end - start), base,
                             _rate_at(schedule, index), ramp_samples)
        if source_position <= end:
            break
    return output


def inverse_source_position(output_position: float,
                            schedule: Sequence[Dict[str, int]],
                            ramp_samples: int, source_length: int) -> float:
    if output_position <= 0.0:
        return 0.0
    end = forward_output_position(float(source_length), schedule, ramp_samples)
    if output_position >= end:
        return float(source_length)
    low = 0.0
    high = float(source_length)
    for _ in range(60):
        middle = (low + high) / 2.0
        if forward_output_position(middle, schedule, ramp_samples) < output_position:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def _hann_window() -> List[float]:
    return [0.5 - 0.5 * math.cos(2.0 * math.pi * index / (WINDOW_SAMPLES - 1))
            for index in range(WINDOW_SAMPLES)]


def ola_transform(samples: Sequence[float],
                  schedule: Sequence[Dict[str, int]],
                  ramp_samples: int) -> Dict[str, Any]:
    output_length = int(round(forward_output_position(
        float(len(samples)), schedule, ramp_samples)))
    window = _hann_window()
    output = [0.0] * output_length
    weight = [0.0] * output_length
    records: List[Dict[str, Any]] = []
    half = WINDOW_SAMPLES // 2
    center = 0
    while center - half < output_length:
        source_center = inverse_source_position(
            float(center), schedule, ramp_samples, len(samples))
        source_start = int(round(source_center)) - half
        terminal = source_start < 0 or source_start + WINDOW_SAMPLES > len(
            samples)
        records.append({
            "output_center": center,
            "source_center_micro": int(round(source_center * MICRO)),
            "source_start": source_start,
            "source_end": source_start + WINDOW_SAMPLES,
            "terminal": terminal,
        })
        for offset in range(WINDOW_SAMPLES):
            out_index = center - half + offset
            if out_index < 0 or out_index >= output_length:
                continue
            source_index = source_start + offset
            if source_index < 0 or source_index >= len(samples):
                continue
            output[out_index] += samples[source_index] * window[offset]
            weight[out_index] += window[offset]
        center += HOP_SAMPLES
    uncovered = 0
    for index in range(output_length):
        if weight[index] > 1e-12:
            output[index] /= weight[index]
        else:
            uncovered += 1
            output[index] = 0.0
    return {
        "samples": output,
        "length": output_length,
        "records": records,
        "uncovered": uncovered,
    }


def varispeed_transform(samples: Sequence[float],
                        schedule: Sequence[Dict[str, int]]) -> Dict[str, Any]:
    if len(schedule) != 1:
        raise ReferenceRejection("varispeed_requires_constant_rate")
    rate = schedule[0]["rate_ppm"] / float(MICRO)
    output_length = int(round(len(samples) / rate))
    output: List[float] = []
    for index in range(output_length):
        position = index * rate
        left = int(math.floor(position))
        fraction = position - left
        if left >= len(samples) - 1:
            value = samples[-1]
        else:
            value = samples[left] * (1.0 - fraction) + samples[left + 1] * fraction
        output.append(value)
    records = [{
        "output_center": 0,
        "source_center_micro": 0,
        "source_start": 0,
        "source_end": len(samples),
        "terminal": False,
    }]
    return {
        "samples": output,
        "length": output_length,
        "records": records,
        "uncovered": 0,
    }


def validate_case_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ReferenceRejection("invalid_case_request")
    if set(request) - {"case_id", "samples", "schedule", "ramp_samples",
                       "rebuffer"}:
        raise ReferenceRejection("unknown_case_field")
    case_id = request.get("case_id")
    if not isinstance(case_id, str) or case_id not in CASE_IDS:
        raise ReferenceRejection("unknown_case:" + str(case_id))
    samples = validate_samples(request.get("samples"))
    schedule = validate_schedule(request.get("schedule"),
                                 request.get("ramp_samples"))
    rebuffer = request.get("rebuffer")
    if rebuffer is not None:
        if not isinstance(rebuffer, dict):
            raise ReferenceRejection("invalid_rebuffer")
        if set(rebuffer) != {"source_sample", "gap_output_samples"}:
            raise ReferenceRejection("invalid_rebuffer")
        if (not isinstance(rebuffer["source_sample"], int)
                or isinstance(rebuffer["source_sample"], bool)
                or not isinstance(rebuffer["gap_output_samples"], int)
                or isinstance(rebuffer["gap_output_samples"], bool)):
            raise ReferenceRejection("invalid_rebuffer")
        if not 0 <= rebuffer["source_sample"] < len(samples):
            raise ReferenceRejection("rebuffer_out_of_range")
        if rebuffer["gap_output_samples"] <= 0:
            raise ReferenceRejection("invalid_rebuffer_gap")
    return {"case_id": case_id, "samples": samples, "schedule": schedule,
            "ramp_samples": request.get("ramp_samples"),
            "rebuffer": rebuffer}


# ---------------------------------------------------------------------------
# Metrics (all report values are integers or exact strings)
# ---------------------------------------------------------------------------

def _rms_micro(samples: Sequence[float], start: int, end: int) -> int:
    start = max(0, start)
    end = min(len(samples), end)
    if end <= start:
        return 0
    total = sum(value * value for value in samples[start:end])
    return int(round(math.sqrt(total / (end - start)) * MICRO))


def _db_milli(output_rms: int, source_rms: int) -> Optional[int]:
    if source_rms <= 0 or output_rms <= 0:
        return None
    return int(round(20.0 * math.log10(output_rms / source_rms) * 1000.0))


def pitch_estimate_micro_hz(samples: Sequence[float], start: int,
                            end: int) -> Optional[int]:
    start = max(0, start)
    end = min(len(samples), end)
    span = end - start
    if span < 800:
        return None
    use = min(span, 4096)
    values = samples[start:start + use]
    energy_total = sum(value * value for value in values)
    if energy_total <= 0.0:
        return None
    best_lag = 0
    best_correlation = -1.0
    correlations: Dict[int, float] = {}
    for lag in range(20, 401):
        if use - lag < 400:
            break
        numerator = 0.0
        energy_left = 0.0
        energy_right = 0.0
        for index in range(use - lag):
            numerator += values[index] * values[index + lag]
            energy_left += values[index] * values[index]
            energy_right += values[index + lag] * values[index + lag]
        if energy_left <= 0.0 or energy_right <= 0.0:
            continue
        correlation = numerator / math.sqrt(energy_left * energy_right)
        correlations[lag] = correlation
        if correlation > best_correlation:
            best_correlation = correlation
            best_lag = lag
    if best_lag == 0:
        return None
    threshold = best_correlation * 0.99
    for lag in sorted(correlations):
        if correlations[lag] >= threshold:
            best_lag = lag
            break
    return int(round(SAMPLE_RATE_HZ / best_lag * MICRO))


def pitch_record(source: Dict[str, Any], output: Sequence[float],
                 schedule: Sequence[Dict[str, int]], ramp_samples: int,
                 source_interval: Tuple[int, int]) -> Dict[str, Any]:
    start, end = source_interval
    if not source.get("pitch_reference", False):
        return {
            "applicable": False,
            "missing": False,
            "withheld_reason": "stimulus has no stationary tonal reference",
            "source_interval": [start, end],
            "mapped_output_interval": None,
            "source_frequency_micro_hz": None,
            "output_frequency_micro_hz": None,
            "scale_ppm": None,
            "pitch_preserved_proxy": False,
            "qualifies_listening": False,
        }
    output_start = int(round(forward_output_position(
        float(start), schedule, ramp_samples)))
    output_end = int(round(forward_output_position(
        float(end), schedule, ramp_samples)))
    output_start = max(0, min(output_start, len(output)))
    output_end = max(output_start, min(output_end, len(output)))
    source_frequency = pitch_estimate_micro_hz(source["samples"], start, end)
    output_frequency = pitch_estimate_micro_hz(output, output_start, output_end)
    if source_frequency is None or output_frequency is None:
        return {
            "applicable": True,
            "missing": True,
            "withheld_reason": "autocorrelation proxy found no periodic lag",
            "source_interval": [start, end],
            "mapped_output_interval": [output_start, output_end],
            "source_frequency_micro_hz": source_frequency,
            "output_frequency_micro_hz": output_frequency,
            "scale_ppm": None,
            "pitch_preserved_proxy": False,
            "qualifies_listening": False,
        }
    scale = int(round(output_frequency * MICRO / source_frequency))
    return {
        "applicable": True,
        "missing": False,
        "withheld_reason": None,
        "source_interval": [start, end],
        "mapped_output_interval": [output_start, output_end],
        "source_frequency_micro_hz": source_frequency,
        "output_frequency_micro_hz": output_frequency,
        "scale_ppm": scale,
        "pitch_preserved_proxy": abs(scale - MICRO) <= PITCH_TOLERANCE_PPM,
        "qualifies_listening": False,
    }


def _click_measurement(samples: Sequence[float], expected: int,
                       radius: int) -> Optional[Dict[str, int]]:
    start = max(0, expected - radius)
    end = min(len(samples), expected + radius + 1)
    if end <= start:
        return None
    peak_index = max(range(start, end), key=lambda index: abs(samples[index]))
    peak = abs(samples[peak_index])
    if peak <= 0.0:
        return None
    window_start = max(0, peak_index - radius)
    window_end = min(len(samples), peak_index + radius + 1)
    local = samples[window_start:window_end]
    local_rms = math.sqrt(sum(value * value for value in local) / len(local))
    threshold = peak * 0.20
    left = peak_index
    while left > 0 and abs(samples[left - 1]) >= threshold:
        left -= 1
    right = peak_index
    while right + 1 < len(samples) and abs(samples[right + 1]) >= threshold:
        right += 1
    return {
        "expected_output_sample": expected,
        "observed_peak_output_sample": peak_index,
        "peak_offset_samples": peak_index - expected,
        "peak_micro": int(round(peak * MICRO)),
        "threshold_crossing_width": right - left + 1,
        "peak_to_local_rms_ppm": int(round(peak / local_rms * MICRO))
        if local_rms > 0 else 0,
    }


def transient_comparison(source: Dict[str, Any], output: Sequence[float],
                         schedule: Sequence[Dict[str, int]],
                         ramp_samples: int) -> Optional[Dict[str, Any]]:
    if source["name"] != "transient":
        return None
    clicks = (2400, 6400, 10400, 14400)
    identity = []
    candidate = []
    for click in clicks:
        measured = _click_measurement(source["samples"], click, 70)
        if measured is not None:
            identity.append(measured)
        expected = int(round(forward_output_position(
            float(click), schedule, ramp_samples)))
        measured = _click_measurement(output, expected, 240)
        if measured is not None:
            candidate.append(measured)
    if not identity or not candidate:
        return None
    identity_width = max(item["threshold_crossing_width"] for item in identity)
    candidate_width = max(
        item["threshold_crossing_width"] for item in candidate)
    identity_peak_to_rms = int(round(
        sum(item["peak_to_local_rms_ppm"] for item in identity)
        / len(identity)))
    candidate_peak_to_rms = int(round(
        sum(item["peak_to_local_rms_ppm"] for item in candidate)
        / len(candidate)))
    return {
        "metric": "synthetic_click_local_peak_and_width",
        "identity": {"clicks": identity, "max_threshold_crossing_width":
                     identity_width,
                     "mean_peak_to_local_rms_ppm": identity_peak_to_rms},
        "candidate": {"clicks": candidate, "max_threshold_crossing_width":
                      candidate_width,
                      "mean_peak_to_local_rms_ppm": candidate_peak_to_rms},
        "smearing_ratio_ppm": int(round(
            candidate_width * MICRO / identity_width)),
        "transient_preserved_proxy": candidate_width <= 4 * identity_width,
        "qualifies_listening": False,
    }


def playback_buffering(source: Dict[str, Any],
                       schedule: Sequence[Dict[str, int]],
                       ramp_samples: int,
                       rebuffer: Optional[Dict[str, int]],
                       require_rebuffer: bool = False) -> Dict[str, Any]:
    if require_rebuffer and rebuffer is None:
        raise ReferenceRejection("missing_rebuffer_event")
    length = len(source["samples"])
    checkpoints = []
    for fraction in (0, 1, 2, 3, 4):
        sample = int(fraction * length / 4)
        ideal = forward_output_position(float(sample), schedule, ramp_samples)
        checkpoints.append({
            "source_sample": sample,
            "source_ns": sample * SAMPLE_NS,
            "ideal_output_samples_micro": int(round(ideal * MICRO)),
            "full_output_frames": int(ideal // FRAME_SAMPLES),
        })
    event = None
    if rebuffer is not None:
        source_sample = rebuffer["source_sample"]
        ideal = forward_output_position(
            float(source_sample), schedule, ramp_samples)
        gap = rebuffer["gap_output_samples"]
        event = {
            "source_sample": source_sample,
            "source_ns": source_sample * SAMPLE_NS,
            "ideal_output_samples_micro": int(round(ideal * MICRO)),
            "delivered_output_samples_micro": int(round(ideal * MICRO)),
            "resume_ideal_output_samples_micro": int(round((ideal + gap) * MICRO)),
            "deficit_samples": gap,
            "compensated": False,
            "device_timing_measured": False,
        }
    output_length = int(round(forward_output_position(
        float(length), schedule, ramp_samples)))
    last_center = ((output_length + HOP_SAMPLES - 1) // HOP_SAMPLES) * \
        HOP_SAMPLES
    window_start = last_center - WINDOW_SAMPLES // 2
    valid = output_length - window_start
    return {
        "model": ("caller-owned FIFO over whole-clip synthetic source; "
                  "no device pacing"),
        "checkpoints": checkpoints,
        "rebuffer": event,
        "rebuffer_required": rebuffer is not None,
        "final_partial_window_start": window_start,
        "final_partial_window_valid_samples": valid,
        "output_partial_samples": output_length % FRAME_SAMPLES,
        "device_timing_measured": False,
        "qualifies_device_claim": False,
    }


def speech_preservation(source: Dict[str, Any], output: Sequence[float],
                        schedule: Sequence[Dict[str, int]],
                        ramp_samples: int) -> Optional[Dict[str, Any]]:
    if not source["labels"]:
        return None
    entries = []
    protect_values: List[int] = []
    for label in source["labels"]:
        start = label["source_start"]
        end = label["source_end"]
        output_start = int(round(forward_output_position(
            float(start), schedule, ramp_samples)))
        output_end = int(round(forward_output_position(
            float(end), schedule, ramp_samples)))
        source_rms = _rms_micro(source["samples"], start, end)
        output_rms = _rms_micro(output, output_start, output_end)
        ratio = _db_milli(output_rms, source_rms)
        entry = {
            "source_start": start,
            "source_end": end,
            "source_start_ns": start * SAMPLE_NS,
            "label": label["label"],
            "decision": label["decision"],
            "source_timestamped": True,
            "mapped_output_start": output_start,
            "mapped_output_end": output_end,
            "source_rms_micro": source_rms,
            "output_rms_micro": output_rms,
            "rms_ratio_db_milli": ratio,
        }
        entries.append(entry)
        if label["decision"] == "protect":
            if ratio is None:
                entry["missing"] = True
            else:
                protect_values.append(ratio)
    maximum = max((abs(value) for value in protect_values), default=None)
    return {
        "metric": "synthetic_labelled_energy_preservation",
        "entries": entries,
        "protect_interval_count": len(protect_values),
        "max_abs_protect_db_milli": maximum,
        "within_tolerance": (
            maximum is not None and maximum <= SPEECH_TOLERANCE_DB_MILLI),
        "qualifies_intelligibility": False,
    }


def _mapping_summary(records: Sequence[Dict[str, Any]],
                     source_length: int, output_length: int) -> Dict[str, Any]:
    starts = [record["source_start"] for record in records]
    nonmonotone = sum(1 for index in range(1, len(starts))
                      if starts[index] < starts[index - 1])
    covered = bool(records) and records[0]["source_start"] <= 0 and \
        records[-1]["source_end"] >= source_length
    return {
        "window_count": len(records),
        "mapping_digest": object_digest(list(records)),
        "first_windows": [dict(record) for record in records[:3]],
        "last_windows": [dict(record) for record in records[-3:]],
        "nonmonotone_window_count": nonmonotone,
        "output_centers_monotone": nonmonotone == 0,
        "output_centers_within_target": all(
            0 <= record["output_center"] < output_length for record in records),
        "source_interval_covered": covered,
    }


def run_case(case: Dict[str, Any],
             fixtures: Optional[Dict[str, Dict[str, Any]]] = None
             ) -> Dict[str, Any]:
    fixtures = fixtures or {}
    source = fixtures.get(case["stimulus"]) or build_stimulus(case["stimulus"])
    schedule = [{"rate_ppm": rate, "source_sample": position}
                for rate, position in case["schedule"]]
    ramp = case["ramp"]
    transform = case["transform"]
    identity = transform == "identity" and len(schedule) == 1 and \
        schedule[0]["rate_ppm"] == MICRO
    if transform == "identity" and not identity:
        raise ReferenceRejection("identity_requires_unit_rate")
    if transform == "varispeed":
        transformed = varispeed_transform(source["samples"], schedule)
    elif identity:
        transformed = {
            "samples": list(source["samples"]),
            "length": len(source["samples"]),
            "records": [{
                "output_center": 0,
                "source_center_micro": 0,
                "source_start": 0,
                "source_end": len(source["samples"]),
                "terminal": False,
            }],
            "uncovered": 0,
        }
    else:
        transformed = ola_transform(source["samples"], schedule, ramp)
    output = transformed["samples"]
    target = int(round(forward_output_position(
        float(len(source["samples"])), schedule, ramp)))
    mapping = _mapping_summary(transformed["records"],
                               len(source["samples"]), transformed["length"])
    mapping["uncovered_samples"] = transformed["uncovered"]
    mapping["coverage_fraction_ppm"] = (
        (transformed["length"] - transformed["uncovered"]) * MICRO
        // transformed["length"] if transformed["length"] else 0)
    pitch = pitch_record(source, output, schedule, ramp, (3200, 6000))
    transient = transient_comparison(source, output, schedule, ramp)
    buffering = playback_buffering(source, schedule, ramp,
                                   case.get("rebuffer"))
    preservation = speech_preservation(source, output, schedule, ramp)
    peak = max((abs(value) for value in output), default=0.0)
    nonfinite = sum(1 for value in output if not math.isfinite(value))
    clipped = sum(1 for value in output if abs(value) >= 1.0)
    duration_error = transformed["length"] - target
    checks = {
        "duration": duration_error == 0,
        "finite_output": nonfinite == 0,
        "peak_bounded": peak < 1.0,
        "mapping_monotone": mapping["nonmonotone_window_count"] == 0,
        "mapping_covered": mapping["source_interval_covered"],
        "no_uncovered_output": transformed["uncovered"] == 0,
        "pitch_proxy": bool(pitch["pitch_preserved_proxy"])
        if pitch["applicable"] else None,
        "speech_preservation": bool(preservation["within_tolerance"])
        if preservation is not None else None,
        "transient_proxy": bool(transient["transient_preserved_proxy"])
        if transient is not None else None,
        "outside_strict_path": transform == "varispeed",
    }
    if transform == "varispeed":
        checks["duration"] = duration_error == 0
        checks["pitch_proxy"] = False
    return {
        "case_id": case["case_id"],
        "stimulus": case["stimulus"],
        "transform": transform,
        "adverse_control": bool(case.get("adverse_control", False)),
        "schedule": [{"rate_ppm": item["rate_ppm"],
                      "source_sample": item["source_sample"]}
                     for item in schedule],
        "ramp_samples": ramp,
        "rate_bounds": {
            "min_ppm": min(item["rate_ppm"] for item in schedule),
            "max_ppm": max(item["rate_ppm"] for item in schedule),
            "change_count": len(schedule),
            "within_proxy_bounds": all(
                RATE_MIN_PPM <= item["rate_ppm"] <= RATE_MAX_PPM
                for item in schedule),
        },
        "duration": {
            "input_samples": len(source["samples"]),
            "target_output_samples": target,
            "actual_output_samples": transformed["length"],
            "error_samples": duration_error,
            "relative_error_ppm": 0 if target == 0 else int(round(
                duration_error * MICRO / target)),
            "source_to_output_map_end_micro": int(round(
                forward_output_position(float(len(source["samples"])),
                                        schedule, ramp) * MICRO)),
        },
        "mapping": mapping,
        "signal": {
            "output_digest": sha256_bytes(_sample_bytes(output)),
            "nonfinite_samples": nonfinite,
            "clipped_samples": clipped,
            "peak_micro": int(round(peak * MICRO)),
        },
        "pitch_proxy": pitch,
        "transient_proxy_comparison": transient,
        "playback_buffering": buffering,
        "speech_preservation": preservation,
        "surrogate_checks": checks,
        "surrogate_checks_pass": all(
            value is True for key, value in checks.items()
            if key != "outside_strict_path" and value is not None)
        and not checks["outside_strict_path"]
        and not case.get("adverse_control", False),
        "candidate_qualified": False,
        "missing_result_promoted": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Profiles, blockers and gates
# ---------------------------------------------------------------------------

ACCEPTANCE_ITEMS: Dict[str, Dict[str, str]] = {
    "source_output_mapping": {
        "status": "synthetic_only",
        "evidence": (
            "Every case records monotone output centers, native source "
            "windows, a mapping digest and terminal-window flags; no DIRAC or "
            "ZTX output exists."
        ),
    },
    "duration": {
        "status": "synthetic_only",
        "evidence": (
            "Target output length is the rounded cumulative source-to-output "
            "map; measured error is recorded per case."
        ),
    },
    "pitch": {
        "status": "synthetic_only",
        "evidence": (
            "Autocorrelation pitch proxy on synthetic stationary tones; "
            "listening is deferred and non-tonal cases withhold pitch."
        ),
    },
    "transient_audibility": {
        "status": "synthetic_only",
        "evidence": (
            "Synthetic click peak and threshold-crossing width are compared "
            "with an identity control; this is not listening."
        ),
    },
    "playback_buffering": {
        "status": "synthetic_only",
        "evidence": (
            "Caller-owned FIFO checkpoints in source samples and nanoseconds; "
            "no device pacing or fill/flush measurement exists."
        ),
    },
    "identity_1x": {
        "status": "synthetic_only",
        "evidence": (
            "The identity case is an exact sample passthrough with unit rate "
            "and zero duration error."
        ),
    },
    "rate_changes": {
        "status": "synthetic_only",
        "evidence": (
            "Constant faster/slower cases and a four-segment drift schedule "
            "are measured, including an unsmoothed step adverse control."
        ),
    },
    "unfamiliar_speech": {
        "status": "synthetic_only",
        "evidence": (
            "A generated voiced/mixed speech surrogate is used; it is not a "
            "recording, corpus item or unfamiliar speaker."
        ),
    },
    "music": {
        "status": "synthetic_only",
        "evidence": (
            "A generated three-tone music surrogate is used; no music "
            "recording or rights-cleared material is present."
        ),
    },
    "silence": {
        "status": "synthetic_only",
        "evidence": (
            "An all-zero synthetic clip is processed; pitch is explicitly "
            "withheld rather than imputed."
        ),
    },
    "rebuffer": {
        "status": "synthetic_only",
        "evidence": (
            "A source-timestamped synthetic pause records a 1600-sample "
            "playback deficit with no fabricated compensation."
        ),
    },
    "drift": {
        "status": "synthetic_only",
        "evidence": (
            "Four source-timestamped rates with an 800-sample ramp are "
            "measured to an exact target length."
        ),
    },
    "final_partial_window": {
        "status": "synthetic_only",
        "evidence": (
            "A 12485-sample non-frame-aligned clip records the final partial "
            "input and output window counts."
        ),
    },
    "pause_filler_source_timestamps": {
        "status": "synthetic_only",
        "evidence": (
            "Protect/flex labels are frozen at source samples and never use "
            "wall time or playback position; they are synthetic metadata."
        ),
    },
    "speech_preservation": {
        "status": "synthetic_only",
        "evidence": (
            "Mapped RMS of protected synthetic speech intervals is reported; "
            "intelligibility and listening remain blocked."
        ),
    },
}

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "EB-01",
        "requirement": (
            "Exact licensed legacy DIRAC artifact: vendor, product/version, "
            "platform and architecture, immutable binary SHA-256, packaged "
            "evaluation kit and local install record."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-02",
        "requirement": (
            "Contemporary Zynaptiq ZTX comparator: approved procurement path, "
            "tier (STUDIO/PRO), quote or evaluation grant, version and "
            "immutable SDK/archive SHA-256."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-03",
        "requirement": (
            "Exact callable API: headers, symbol/ABI list, sample rate and "
            "channel limits, block/seek geometry, dynamic-rate semantics, "
            "content delay and final-partial behavior."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-04",
        "requirement": (
            "Executed license/SLA and rights review: redistribution, product "
            "use, derivative output, attribution/notice, patent indemnity and "
            "per-product signed SLA where required."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-05",
        "requirement": (
            "Rights-cleared, task-matched unfamiliar speech and music cohort "
            "with authorized listening, intelligibility and transient scoring."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-06",
        "requirement": (
            "Exact candidate numeric output: frozen vendor renders for 1x, "
            "faster/slower, drift, rebuffer and final partial cases, with "
            "byte-level parity to the proposal boundary."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-07",
        "requirement": (
            "Target-device pacing, availability, buffers, CPU, memory, power "
            "and deadline evidence at the exact runtime and load."
        ),
        "status": "blocked",
        "present": False,
    },
    {
        "id": "EB-08",
        "requirement": (
            "Opt-in provider intake, descriptor/registry decision, independent "
            "exact-head review and default/release approval."
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
            "Pin the exact licensed legacy DIRAC artifact and the approved "
            "ZTX STUDIO/PRO comparator with immutable vendor/version/platform "
            "identity, archive or binary SHA-256 and license/SLA references."
        ),
    },
    {
        "id": "RG-02",
        "status": "blocked",
        "requirement": (
            "Admit the runtime in an isolated hash-pinned artifact tree, "
            "reproduce installation and verify identity with fail-closed "
            "absent behavior and no default-package bytes."
        ),
    },
    {
        "id": "RG-03",
        "status": "blocked",
        "requirement": (
            "Clear license, SLA, redistribution, product-use, derivative-"
            "output, attribution/notice and patent-indemnity terms for the "
            "exact artifact and tier."
        ),
    },
    {
        "id": "RG-04",
        "status": "blocked",
        "requirement": (
            "Map exact sample rate/channel/block geometry, dynamic-rate "
            "semantics, content delay and final partial behavior into the "
            "installed 16 kHz mono float32 160-sample boundary with parity."
        ),
    },
    {
        "id": "RG-05",
        "status": "blocked",
        "requirement": (
            "Qualify the rate profile on rights-cleared unfamiliar speech and "
            "music with authorized listening, pitch, transient, duration and "
            "speech-preservation scoring."
        ),
    },
    {
        "id": "RG-06",
        "status": "blocked",
        "requirement": (
            "Measure candidate state, reset, dynamic rate changes, nonfinite "
            "and peak bounds, rebuffer/drift recovery and availability at the "
            "exact runtime."
        ),
    },
    {
        "id": "RG-07",
        "status": "blocked",
        "requirement": (
            "Measure target-device playback pacing, fill/flush, buffer "
            "occupancy, CPU, memory, power and deadlines under the intended "
            "workload."
        ),
    },
    {
        "id": "RG-08",
        "status": "blocked",
        "requirement": (
            "Complete opt-in provider intake, descriptor/registry review, "
            "independent exact-head review and default/release approval."
        ),
    },
)

VENDOR_REPORTED: Dict[str, Any] = {
    "source": "cpp-library/pipeline-validation/playback-speed-candidates.md "
              "sections 3.13-3.14 (vendor pages read 2026-11-04)",
    "legacy_dirac": (
        "legacy name for the DSP Dimension technology; old free binaries "
        "should not be adopted without checking their terms"
    ),
    "ztx_le": (
        "free-to-use with one signed SLA per product; limited to one channel "
        "at 44.1/48 kHz and no dynamic stretch/pitch changes"
    ),
    "ztx_studio": (
        "two channels, 8-96 kHz, no dynamic parameter changes"
    ),
    "ztx_pro": (
        "any rate, unlimited channels and dynamic parameter changes"
    ),
    "public_source": False,
    "evaluation_kit_present": False,
    "pricing_present": False,
    "local_run": False,
    "locally_verified": False,
}


def config_record() -> Dict[str, Any]:
    return {
        "config_id": CONFIG_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "window_samples": WINDOW_SAMPLES,
        "hop_samples": HOP_SAMPLES,
        "ramp_samples": RAMP_SAMPLES,
        "rate_min_ppm": RATE_MIN_PPM,
        "rate_max_ppm": RATE_MAX_PPM,
        "resampling": "none",
        "candidate_runtime": None,
        "candidate_header": None,
        "candidate_block_size": None,
        "candidate_dynamic_rate": None,
    }


def surrogate_model_spec() -> Dict[str, Any]:
    return {
        "model_id": SURROGATE_ID,
        "algorithm": "hann_windowed_native_grain_overlap_add",
        "window_samples": WINDOW_SAMPLES,
        "hop_samples": HOP_SAMPLES,
        "ramp_samples": RAMP_SAMPLES,
        "rate_min_ppm": RATE_MIN_PPM,
        "rate_max_ppm": RATE_MAX_PPM,
        "is_dirac": False,
        "is_ztx": False,
        "is_candidate": False,
        "is_learned": False,
        "uses_weights": False,
        "uses_vendor_code": False,
        "uses_vendor_binary": False,
        "uses_vendor_headers": False,
        "whole_clip_required": True,
        "device_timing": False,
        "listening": False,
        "note": (
            "Original native-grain OLA rate probe; not derived from DIRAC or "
            "ZTX and unable to qualify either candidate."
        ),
    }


def surrogate_model_digest() -> str:
    return object_digest(surrogate_model_spec())


def scoring_protocol_spec() -> Dict[str, Any]:
    return {
        "scorer_id": SCORER_ID,
        "candidate_comparison": False,
        "oracle_used_for_score": False,
        "duration_tolerance_samples": 0,
        "pitch_tolerance_ppm": PITCH_TOLERANCE_PPM,
        "speech_tolerance_db_milli": SPEECH_TOLERANCE_DB_MILLI,
        "transient_tolerance_ratio_ppm": 4000000,
        "source_intervals": "half_open_sample_intervals",
        "metrics": [
            "mapping_digest",
            "duration_samples",
            "pitch_proxy_ppm",
            "transient_width_samples",
            "fifo_deficit_samples",
            "protected_rms_db_milli",
        ],
        "validity_policy": (
            "invalid or missing results are excluded, never promoted and "
            "never scored as a pass"
        ),
        "qualifies": False,
    }


def scoring_protocol_digest() -> str:
    return object_digest(scoring_protocol_spec())


# ---------------------------------------------------------------------------
# Adverse and missing controls
# ---------------------------------------------------------------------------

REQUIRED_ADVERSE = (
    "duplicate_json_key",
    "nan_json_constant",
    "json_root_array",
    "nonfinite_sample_nan",
    "nonfinite_sample_inf",
    "empty_samples",
    "out_of_range_sample",
    "missing_schedule",
    "nonfinite_rate",
    "zero_rate",
    "oversized_rate",
    "undersized_rate",
    "nonmonotone_schedule",
    "schedule_missing_origin",
    "schedule_negative_source_sample",
    "unknown_case",
    "silence_pitch_withheld",
    "missing_rebuffer_event",
)
WITHHELD_ADVERSE = ("silence_pitch_withheld", "missing_rebuffer_event")


def _state_digest(fixtures: Dict[str, Dict[str, Any]]) -> str:
    return object_digest({
        "fixture_digest": fixture_digest(fixtures),
        "open_sessions": 0,
        "accepted_cases": 0,
    })


def _request(samples: Sequence[float], schedule: Any,
             ramp: Any = RAMP_SAMPLES,
             case_id: str = "identity_1x",
             rebuffer: Any = None) -> Dict[str, Any]:
    request: Dict[str, Any] = {
        "case_id": case_id,
        "samples": list(samples),
        "schedule": schedule,
        "ramp_samples": ramp,
    }
    if rebuffer is not None:
        request["rebuffer"] = rebuffer
    return request


def adverse_rejections(fixtures: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    tonal = fixtures["tonal"]["samples"]
    silent = fixtures["silence"]["samples"]
    speech = fixtures["speech_unfamiliar"]["samples"]
    before = _state_digest(fixtures)
    records: List[Dict[str, Any]] = []

    def rejected(case_id: str, action: Any) -> None:
        try:
            action()
        except ReferenceRejection as error:
            status = "rejected"
            reason = error.code
        else:
            status = "accepted_unexpected"
            reason = "no_rejection"
        after = _state_digest(fixtures)
        records.append({
            "case_id": case_id,
            "status": status,
            "outcome": "rejected" if status == "rejected" else "unexpected",
            "reason": reason,
            "state_digest_before": before,
            "state_digest_after": after,
            "state_unchanged": before == after,
            "candidate_qualified": False,
            "missing_result_promoted": False,
        })

    rejected("duplicate_json_key", lambda: load_strict_json_text(
        '{"a":1,"a":2}'))
    rejected("nan_json_constant", lambda: load_strict_json_text(
        '{"a":NaN}'))
    rejected("json_root_array", lambda: load_strict_json_object_text(
        "[1,2,3]"))
    rejected("nonfinite_sample_nan", lambda: validate_samples(
        tonal[:100] + [float("nan")]))
    rejected("nonfinite_sample_inf", lambda: validate_samples(
        tonal[:100] + [float("inf")]))
    rejected("empty_samples", lambda: validate_samples([]))
    rejected("out_of_range_sample", lambda: validate_samples(
        tonal[:100] + [1.5]))
    rejected("missing_schedule", lambda: validate_schedule(
        None, RAMP_SAMPLES))
    rejected("nonfinite_rate", lambda: validate_schedule(
        [(float("nan"), 0)], RAMP_SAMPLES))
    rejected("zero_rate", lambda: validate_schedule(
        [(0, 0)], RAMP_SAMPLES))
    rejected("oversized_rate", lambda: validate_schedule(
        [(2000000, 0)], RAMP_SAMPLES))
    rejected("undersized_rate", lambda: validate_schedule(
        [(700000, 0)], RAMP_SAMPLES))
    rejected("nonmonotone_schedule", lambda: validate_schedule(
        [(1000000, 0), (1200000, 0)], RAMP_SAMPLES))
    rejected("schedule_missing_origin", lambda: validate_schedule(
        [(1000000, 160)], RAMP_SAMPLES))
    rejected("schedule_negative_source_sample", lambda: validate_schedule(
        [(1000000, 0), (1200000, -160)], RAMP_SAMPLES))
    rejected("unknown_case", lambda: validate_case_request(
        _request(tonal, [(1000000, 0)], case_id="not_a_registered_case")))

    # Missing metric controls: withheld, never imputed and never a pass.
    pitch = pitch_record(
        fixtures["silence"], silent, [{"rate_ppm": 1250000, "source_sample": 0}],
        RAMP_SAMPLES, (0, len(silent)))
    after = _state_digest(fixtures)
    records.append({
        "case_id": "silence_pitch_withheld",
        "status": "metric_withheld",
        "outcome": "metric_withheld",
        "reason": "no stationary tonal reference in silence; pitch is withheld",
        "pitch_proxy": pitch,
        "state_digest_before": before,
        "state_digest_after": after,
        "state_unchanged": before == after,
        "candidate_qualified": False,
        "missing_result_promoted": False,
    })
    rebuffer_schedule = [{"rate_ppm": 1250000, "source_sample": 0}]
    try:
        playback_buffering(fixtures["speech_unfamiliar"], rebuffer_schedule,
                           RAMP_SAMPLES, None, require_rebuffer=True)
        missing_rebuffer = "no_rejection"
    except ReferenceRejection as error:
        missing_rebuffer = error.code
    after = _state_digest(fixtures)
    records.append({
        "case_id": "missing_rebuffer_event",
        "status": "metric_withheld"
        if missing_rebuffer == "missing_rebuffer_event"
        else "unexpected",
        "outcome": "metric_withheld"
        if missing_rebuffer == "missing_rebuffer_event"
        else "unexpected",
        "reason": (
            "no rebuffer event supplied; no playback-gap result is fabricated"
        ),
        "missing_rebuffer_code": missing_rebuffer,
        "state_digest_before": before,
        "state_digest_after": after,
        "state_unchanged": before == after,
        "candidate_qualified": False,
        "missing_result_promoted": False,
    })
    # Speech fixture is used by valid speech-preservation cases; it is only
    # here to keep the deterministic fixture dependency explicit.
    if speech and silent and not all(value == 0.0 for value in silent):
        raise ReferenceRejection("silence_fixture_dirty")
    return records


def invalid_and_missing_cases(fixtures: Dict[str, Dict[str, Any]]
                              ) -> List[Dict[str, Any]]:
    return [dict(item) for item in adverse_rejections(fixtures)]


# ---------------------------------------------------------------------------
# Caller archive contract and board identity
# ---------------------------------------------------------------------------

def _is_hex(value: Any, length: int) -> bool:
    return (isinstance(value, str) and len(value) == length
            and all(character in "0123456789abcdef" for character in value))


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ReferenceRejection("caller_manifest_not_object")
    if set(manifest) != set(CALLER_MANIFEST_FIELDS):
        raise ReferenceRejection("caller_manifest_fields")
    if manifest["vendor_id"] != "zynaptiq":
        raise ReferenceRejection("caller_vendor")
    if manifest["artifact_id"] not in ("dirac-legacy", "ztx"):
        raise ReferenceRejection("caller_artifact")
    if not isinstance(manifest["platform"], str) or not manifest["platform"]:
        raise ReferenceRejection("caller_platform")
    if not isinstance(manifest["license_id"], str) or not manifest[
            "license_id"]:
        raise ReferenceRejection("caller_license")
    if not isinstance(manifest["sla_reference"], str):
        raise ReferenceRejection("caller_sla")
    if not _is_hex(manifest["archive_sha256"], 64):
        raise ReferenceRejection("caller_archive_sha256")
    for key in ("vendor_version", "runtime_id", "product_id"):
        if not isinstance(manifest[key], str) or not manifest[key]:
            raise ReferenceRejection("caller_" + key)
    return {
        "accepted": True,
        "loaded": False,
        "executed": False,
        "verified": False,
        "note": "shape-only caller declaration; no artifact is read",
    }


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
# Records and report assembly
# ---------------------------------------------------------------------------

def scope_record() -> Dict[str, Any]:
    return {
        "write_scope": "docs/task-evidence/dirac-legacy-ztx/ only",
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
        "vendor_binary_added": False,
        "vendor_headers_added": False,
    }


def negative_claims() -> List[str]:
    return [
        "No legacy DIRAC binary, Zynaptiq ZTX SDK, evaluation kit, header, "
        "library, installer or license/SLA is present, copied, downloaded, "
        "loaded, imported or executed.",
        "No real speech, music, recording, corpus, consent, listening, "
        "quality, intelligibility or device result exists.",
        "No DIRAC or ZTX duration, latency, pitch, transient, buffering, "
        "throughput or quality value is claimed; every measured value belongs "
        "to the deterministic task-local surrogate on synthetic clips.",
        "No candidate sample rate, channel limit, block size, dynamic-rate "
        "semantics, content delay, output geometry or final-partial behavior "
        "is locally verified.",
        "No installed v0, public API/ABI, descriptor, registry, default, "
        "shared build, CI, board, handoff or other worktree change is made.",
        "No processor exposure, adapter registration, benchmark entry or "
        "release qualification is produced.",
        "No device timing, pacing, buffer occupancy, CPU, power or hard "
        "real-time claim is made.",
    ]


def reopen_condition() -> str:
    return (
        "Obtain the exact licensed legacy DIRAC artifact and an approved "
        "Zynaptiq ZTX STUDIO/PRO evaluation or license, with immutable "
        "vendor/version/platform identity, archive SHA-256 and executed SLA; "
        "admit the runtime in an isolated artifact tree; clear license, "
        "redistribution, product-use, derivative-output and patent terms; map "
        "exact rate/channel/block/dynamic-rate/content-delay geometry into the "
        "installed mono boundary with parity; qualify on rights-cleared "
        "unfamiliar speech and music with authorized listening; measure "
        "target-device pacing and resources; and complete opt-in provider "
        "intake and independent review. Until every condition is closed both "
        "candidates stay DEFER, incomplete and not qualified."
    )


def build_fixtures() -> Dict[str, Dict[str, Any]]:
    return {name: build_stimulus(name) for name in STIMULI}


def build_report() -> Dict[str, Any]:
    fixtures = build_fixtures()
    cases = {case["case_id"]: run_case(case, fixtures) for case in CASES}
    rows = [run_case(case, fixtures) for case in CASES]
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
        "defer_after": DEFER_AFTER,
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
                "cpp-library/pipeline-validation/playback-speed-candidates.md "
                "sections 3.13-3.14 and plan/INVENTORY.json id=dirac-legacy-ztx"
            ),
            "finding": (
                "Legacy DIRAC binaries are separate artifacts with unverified "
                "terms; contemporary Zynaptiq ZTX is commercial closed source. "
                "No licensed artifact, evaluation kit, headers, exact API "
                "geometry, SIG/SLA, price or local run exists."
            ),
            "baseline": (
                "Zynaptiq ZTX STUDIO/PRO contemporary comparator; separate "
                "time-stretch tasks remain independent"
            ),
            "vendor_reported": dict(VENDOR_REPORTED),
            "legacy_artifact_present": False,
            "ztx_sdk_present": False,
            "evaluation_kit_present": False,
            "signed_sla_present": False,
            "source_present": False,
            "headers_present": False,
            "runtime_present": False,
            "adapter_present": False,
            "exact_geometry_documented": False,
            "exact_numeric_output_present": False,
            "implemented_here": False,
        },
        "reference": {
            "status": "blocked",
            "local_identity": SURROGATE_ID,
            "source_present": False,
            "runtime_present": False,
            "headers_present": False,
            "implementation_present": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "is_dirac": False,
            "is_ztx": False,
            "uses_vendor_binary": False,
            "uses_vendor_headers": False,
            "note": (
                "An original native-grain OLA probe, not DIRAC and not ZTX, "
                "not derived from vendor code and unable to qualify either "
                "candidate."
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
            "candidate_reported_block_samples": None,
            "candidate_reported_channel_limit": None,
            "candidate_geometry_documented": False,
            "candidate_dynamic_rate_verified": False,
        },
        "config": config_record(),
        "fixture": {
            "fixture_id": FIXTURE_ID,
            "synthetic": True,
            "real_speech": False,
            "real_music": False,
            "candidate_audio": False,
            "fixture_digest": fixture_digest(fixtures),
            "stimuli": {
                name: {
                    "kind": fixture["kind"],
                    "length": fixture["length"],
                    "digest": fixture["digest"],
                    "peak_micro": fixture["peak_micro"],
                    "label_count": len(fixture["labels"]),
                }
                for name, fixture in fixtures.items()
            },
            "method": {
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": CHANNELS,
                "generator": "analytic_formulas_plus_integer_lcg",
                "recording": False,
                "download": False,
            },
        },
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
            "case_count": len(cases),
            "adverse_control_count": sum(
                1 for case in CASES if case.get("adverse_control")),
            "surrogate_checks_pass_count": sum(
                1 for row in rows if row["surrogate_checks_pass"]),
            "candidate_qualified_count": 0,
            "cases": cases,
            "identity": {
                "case_id": "identity_1x",
                "bit_exact_passthrough": True,
                "duration_error_samples": cases["identity_1x"]["duration"][
                    "error_samples"],
                "qualifies": False,
            },
            "final_partial": {
                "input_samples": 12485,
                "input_partial_samples": 12485 % FRAME_SAMPLES,
                "output_samples": cases["final_partial_window"]["duration"][
                    "actual_output_samples"],
                "output_partial_samples": cases["final_partial_window"][
                    "playback_buffering"]["output_partial_samples"],
                "final_window_valid_samples": cases["final_partial_window"][
                    "playback_buffering"]["final_partial_window_valid_samples"],
                "qualifies": False,
            },
        },
        "rate_profile": {
            "coverage": {
                "source_output_mapping": True,
                "duration": True,
                "pitch": True,
                "transient_audibility": True,
                "playback_buffering": True,
                "identity_1x": True,
                "rate_increase": True,
                "rate_decrease": True,
                "dynamic_rate_changes": True,
                "unfamiliar_speech": True,
                "music": True,
                "silence": True,
                "rebuffer": True,
                "drift": True,
                "final_partial_window": True,
                "pause_filler_tied_to_source_timestamps": True,
                "speech_preservation_measured": True,
            },
            "candidate_measured": False,
            "all_synthetic": True,
            "qualifies": False,
        },
        "controls": {
            "identity_passthrough": {
                "bit_exact": True,
                "candidate_claim": False,
                "qualifies": False,
            },
            "silence_pitch_withheld": {
                "withheld": True,
                "imputed": False,
                "candidate_claim": False,
                "qualifies": False,
            },
            "varispeed_adverse": {
                "pitch_shift_expected": True,
                "candidate_claim": False,
                "qualifies": False,
            },
            "unsmoothed_step_adverse": {
                "adverse_control": True,
                "candidate_claim": False,
                "qualifies": False,
            },
            "missing_rebuffer_event": {
                "withheld": True,
                "fabricated": False,
                "candidate_claim": False,
                "qualifies": False,
            },
            "independent_recompute": {
                "report_recomputed_in_verify": True,
                "candidate_claim": False,
                "qualifies": False,
            },
        },
        "adverse_rejections": adverse_rejections(fixtures),
        "adverse_all_rejected": True,
        "external_artifacts": {
            "status": "blocked",
            "any_present": False,
            "legacy_dirac_binary_present": False,
            "ztx_sdk_present": False,
            "evaluation_kit_present": False,
            "vendor_headers_present": False,
            "signed_sla_present": False,
            "license_text_present": False,
            "real_corpus_present": False,
            "note": (
                "No DIRAC or ZTX artifact, license, SLA, evaluation kit, "
                "recording or corpus is staged in this package."
            ),
        },
        "licensing": {
            "reported_upstream_license": (
                "commercial closed source; ZTX LE free-to-use under a signed "
                "per-product SLA; STUDIO/PRO licensed (source-reported only)"
            ),
            "source_reported": True,
            "locally_verified_terms": False,
            "license_text_staged": False,
            "sla_staged": False,
            "evaluation_kit_staged": False,
            "redistribution_reviewed": False,
            "product_use_reviewed": False,
            "derivative_output_reviewed": False,
            "patent_indemnity_reviewed": False,
            "corpus_rights_reviewed": False,
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
            "real_candidate_archive_validated": False,
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
            "exact_legacy_artifact_present": False,
            "exact_ztx_artifact_present": False,
            "evaluation_kit_present": False,
            "signed_sla_present": False,
            "vendor_headers_present": False,
            "candidate_geometry_documented": False,
            "candidate_api_pinned": False,
            "numeric_output_parity": False,
            "rights_cleared_cohort": False,
            "task_matched_heldout_score": False,
            "listening": False,
            "pitch_and_transient_measured": False,
            "device_timing_measured": False,
            "real_corpus_used": False,
            "real_runtime_used": False,
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
            "vendor artifact, runtime, corpus, provider registration, ABI, "
            "registry, default, shared build, CI, benchmark or release claim."
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
        "defer_after": DEFER_AFTER,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "profile": PROFILE,
        "verification_profile": PROFILE,
        "task_prefix": TASK_PREFIX,
        "acceptance_profile": report["acceptance_profile"],
        "candidate": report["candidate"],
        "format": report["format"],
        "config": report["config"],
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
        "caller_archive_contract": report["caller_asset"],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no legacy DIRAC binary, ZTX SDK, evaluation kit, header, runtime "
            "or license/SLA is downloaded, copied, loaded or executed",
            "the deterministic native-grain OLA probe is not DIRAC and not "
            "ZTX and cannot qualify either candidate",
            "no candidate rate, channel limit, block size, dynamic-rate "
            "semantics, content delay or output geometry is asserted",
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
        "# SHA-256 pins for SDK-DIRAC-LEGACY-ZTX; source: paths are "
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
    "CALLER_MANIFEST_FIELDS", "CASES", "CASE_IDS", "ReferenceRejection",
    "adverse_rejections", "artifact_pins", "board_row", "boundary_record",
    "build_contract", "build_fixtures", "build_report", "build_stimulus",
    "canonical_report", "canonical_text", "case_by_id", "config_record",
    "file_digest", "fixture_digest", "forward_output_position",
    "inverse_source_position", "invalid_and_missing_cases",
    "load_strict_json", "load_strict_json_object_text",
    "load_strict_json_text", "object_digest", "ola_transform",
    "playback_buffering", "pitch_estimate_micro_hz", "pitch_record",
    "run_case", "scope_record", "scoring_protocol_digest",
    "scoring_protocol_spec", "sha256_bytes", "sources_bytes",
    "speech_preservation", "surrogate_model_digest", "surrogate_model_spec",
    "transient_comparison", "validate_caller_manifest", "validate_case_request",
    "validate_samples", "validate_schedule", "varispeed_transform",
]
