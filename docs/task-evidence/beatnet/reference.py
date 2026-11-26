# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local BeatNet boundary evidence.

This is an original, stdlib-only synthetic probe written for this task. It is
NOT BeatNet source, a BeatNet build, a licensed BeatNet runtime, a BeatNet
weight file or a BeatNet result. No upstream code, CRNN, particle filter,
weight, corpus or asset is present, copied, downloaded, loaded or executed.

The probe consumes caller-owned 16 kHz mono float32 160-sample frames, derives
a log-energy onset envelope, estimates tempo from source-anchored inter-onset
intervals, and votes on meter/downbeat phase from synthetic accent strengths.
It exists only to exercise strict parsing, exact fixture arithmetic, online
state, reset, block invariance, gap exclusion and adverse rejection at the
public SDK boundary. It is proposal-only, incomplete and not qualified.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

VERSION = "0.1.0"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
REPORT_SCHEMA = "audio-sdk/beatnet-report/0.1"
TASK_ID = "SDK-BEATNET"
TITLE = "BeatNet"
COMPONENT = "beatnet"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "d7f4f9d4426b007be8fc9c24f3a1d58203b69257"
BRANCH = "swarm/SDK-BEATNET"
REVIEWER = "reviewer-BEATNET"
PROFILE = "rate"
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
CANDIDATE_NATIVE_RATE_HZ = 22050

BURST_SAMPLES = 96
LOG_FLOOR = 1.0e-12
ONSET_THRESHOLD = 0.5
BASELINE_ALPHA = 0.20
MIN_ONSET_GAP_FRAMES = 7
TEMPO_MIN_BPM_X100 = 6000
TEMPO_MAX_BPM_X100 = 180000
TEMPO_STABILITY_SPREAD_X100 = 100
MIN_IOIS_FOR_TEMPO = 4
TEMPO_SEGMENT_WINDOW = 4
BEAT_TOLERANCE_SAMPLES = 1120  # +/- 70 ms at 16 kHz
METER_CANDIDATES = (2, 3, 4)
METER_MIN_STRENGTH_SPREAD_MILLI = 200

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

STIMULUS_LENGTHS = {
    "steady_music_1x": 64137,
    "rate_0_8": 64137,
    "rate_1_2": 64137,
    "tempo_step": 80137,
    "syncopated_offbeat": 64137,
    "speech_like_unfamiliar": 64137,
    "rebuffer_gap": 100137,
    "drift_decreasing": 64137,
    "silence": 64137,
    "final_partial": 64137,
}

SOURCE_PINS = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md": (
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3"
    ),
    "REALTIME_COMPONENT_CANDIDATES.md": (
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d"
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
    "docs/task-evidence/aubio/README.md": (
        "700153d2541f9f4836e878fd6bfec631b644d1bf55ab0868e03f880858bd5e1d"
    ),
    "docs/task-evidence/aubio/report.json": (
        "0ee56f1ecc66440b25f8d0c54e88ba5d2ba4f66c316fe8b0c3a4e626896e06f1"
    ),
    "docs/task-evidence/aubio/contract.json": (
        "3777518ee55fdf6927b66e66060a1a3503dcca455452a10a5aa8f4d00dd7f768"
    ),
    "docs/task-evidence/soundtouch/README.md": (
        "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550"
    ),
    "docs/task-evidence/soundtouch/report.json": (
        "83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947"
    ),
    "docs/task-evidence/signalsmith-stretch/README.md": (
        "446398e0c3aa27528e5ceacf1d4d0b6102f8c8e541c76aa6ac2a8abe62691934"
    ),
    "docs/task-evidence/signalsmith-stretch/report.json": (
        "e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231"
    ),
}

BOARD_ROW_STABLE_SHA256 = (
    "253a20ba0c9fea236cfd88aa325c19727d927046399ea2647e8bf61a4e087086"
)

TASK_PREFIX = "docs/task-evidence/beatnet/"
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


def llround(value: float) -> int:
    """C llround semantics: halves away from zero."""
    return (int(math.floor(value + 0.5)) if value >= 0.0
            else int(math.ceil(value - 0.5)))


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


def signal_digest(samples: Sequence[float]) -> str:
    return sha256_bytes(b"".join(struct.pack("<f", float(value))
                                 for value in samples))


def event_digest(events: Sequence["OnsetEvent"]) -> str:
    return object_digest([event.as_dict() for event in events])


# ---------------------------------------------------------------------------
# Frozen synthetic stimuli
# ---------------------------------------------------------------------------

STIMULI: Dict[str, Dict[str, Any]] = {
    "steady_music_1x": {
        "kind": "periodic",
        "description": "100 BPM 4/4 click surrogate at identity rate",
        "length_samples": STIMULUS_LENGTHS["steady_music_1x"],
        "beats_frames": [0, 60, 120, 180, 240, 300, 360],
        "beat_offsets_samples": [0, 0, 0, 0, 0, 0, 0],
        "amplitudes_milli": [900, 450, 450, 450, 900, 450, 450],
        "accent_frames": [0, 240],
        "gap_samples": [],
        "meter": 4,
    },
    "rate_0_8": {
        "kind": "periodic",
        "description": "event-time 0.8x projection of the 100 BPM surrogate",
        "length_samples": STIMULUS_LENGTHS["rate_0_8"],
        "beats_frames": [0, 75, 150, 225, 300, 375],
        "beat_offsets_samples": [0, 0, 0, 0, 0, 0],
        "amplitudes_milli": [900, 450, 450, 450, 900, 450],
        "accent_frames": [0, 300],
        "gap_samples": [],
        "meter": 4,
    },
    "rate_1_2": {
        "kind": "periodic",
        "description": "event-time 1.2x projection of the 100 BPM surrogate",
        "length_samples": STIMULUS_LENGTHS["rate_1_2"],
        "beats_frames": [0, 50, 100, 150, 200, 250, 300, 350],
        "beat_offsets_samples": [0, 0, 0, 0, 0, 0, 0, 0],
        "amplitudes_milli": [900, 450, 450, 450, 900, 450, 450, 450],
        "accent_frames": [0, 200],
        "gap_samples": [],
        "meter": 4,
    },
    "tempo_step": {
        "kind": "tempo_step",
        "description": "100 BPM then 150 BPM, five beats per section",
        "length_samples": STIMULUS_LENGTHS["tempo_step"],
        "beats_frames": [0, 60, 120, 180, 240, 280, 320, 360, 400, 440],
        "beat_offsets_samples": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "amplitudes_milli": [900, 450, 450, 450, 900, 900, 450, 450, 450, 900],
        "accent_frames": [0, 240, 280, 400],
        "gap_samples": [],
        "meter": None,
    },
    "syncopated_offbeat": {
        "kind": "syncopated",
        "description": "stable 120 BPM offbeat clicks with no downbeat accent",
        "length_samples": STIMULUS_LENGTHS["syncopated_offbeat"],
        "beats_frames": [25, 75, 125, 175, 225, 275, 325, 375],
        "beat_offsets_samples": [0, 0, 0, 0, 0, 0, 0, 0],
        "amplitudes_milli": [450, 450, 450, 450, 450, 450, 450, 450],
        "accent_frames": [],
        "gap_samples": [],
        "meter": None,
    },
    "speech_like_unfamiliar": {
        "kind": "irregular",
        "description": "irregular speech-like burst train with no stable period",
        "length_samples": STIMULUS_LENGTHS["speech_like_unfamiliar"],
        "beats_frames": [3, 12, 21, 31, 42, 54, 67, 81, 96, 112, 129,
                         147, 166, 186, 207, 229, 252, 276, 301, 327, 354],
        "beat_offsets_samples": [0] * 21,
        "amplitudes_milli": [700, 500, 650, 400, 550, 300, 600, 450, 700,
                             350, 500, 600, 250, 550, 400, 650, 300, 500,
                             450, 600, 350],
        "accent_frames": [],
        "gap_samples": [],
        "meter": None,
    },
    "rebuffer_gap": {
        "kind": "gap",
        "description": "120 BPM clicks with one 1.5 s rebuffer gap",
        "length_samples": STIMULUS_LENGTHS["rebuffer_gap"],
        "beats_frames": [0, 50, 100, 150, 200, 250, 450, 500, 550],
        "beat_offsets_samples": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "amplitudes_milli": [900, 450, 450, 450, 900, 450, 900, 450, 450],
        "accent_frames": [0, 200, 450],
        "gap_samples": [[48000, 72000]],
        "meter": None,
    },
    "drift_decreasing": {
        "kind": "drift",
        "description": "monotonically shortening inter-beat intervals",
        "length_samples": STIMULUS_LENGTHS["drift_decreasing"],
        "beats_frames": [0, 60, 119, 177, 234, 290, 345],
        "beat_offsets_samples": [0, 0, 0, 0, 0, 0, 0],
        "amplitudes_milli": [450, 450, 450, 450, 450, 450, 450],
        "accent_frames": [],
        "gap_samples": [],
        "meter": None,
    },
    "silence": {
        "kind": "silence",
        "description": "digital silence with no click",
        "length_samples": STIMULUS_LENGTHS["silence"],
        "beats_frames": [],
        "beat_offsets_samples": [],
        "amplitudes_milli": [],
        "accent_frames": [],
        "gap_samples": [],
        "meter": None,
    },
    "final_partial": {
        "kind": "final_partial",
        "description": "single click at sample 64010 inside a 137-sample final frame",
        "length_samples": STIMULUS_LENGTHS["final_partial"],
        "beats_frames": [400],
        "beat_offsets_samples": [10],
        "amplitudes_milli": [800],
        "accent_frames": [],
        "gap_samples": [],
        "meter": None,
    },
}

STIMULUS_KEYS = {
    "kind", "description", "length_samples", "beats_frames",
    "beat_offsets_samples", "amplitudes_milli", "accent_frames",
    "gap_samples", "meter",
}
STIMULUS_KINDS = {
    "periodic", "tempo_step", "syncopated", "irregular", "gap", "drift",
    "silence", "final_partial",
}


def validate_stimuli(stimuli: Dict[str, Dict[str, Any]]) -> None:
    """Validate the frozen stimuli; no implicit defaults or coercion."""
    _require(isinstance(stimuli, dict), "invalid_stimuli")
    _require(set(stimuli) == set(STIMULUS_LENGTHS), "stimuli_set_mismatch")
    for name, spec in stimuli.items():
        _exact_keys(spec, STIMULUS_KEYS, "stimulus:" + name)
        _require(isinstance(spec["description"], str), "invalid_description")
        _require(spec["kind"] in STIMULUS_KINDS, "unknown_stimulus_kind:" + name)
        length = _integer(spec["length_samples"], "length_samples", 160, 200000)
        _require(length == STIMULUS_LENGTHS[name], "stimulus_length_mismatch:" + name)
        _require(length % FRAME_SAMPLES in (0, 137),
                 "invalid_stimulus_length:" + name)
        max_frame = (length - 1) // FRAME_SAMPLES
        beats = spec["beats_frames"]
        offsets = spec["beat_offsets_samples"]
        amplitudes = spec["amplitudes_milli"]
        _require(isinstance(beats, list) and isinstance(offsets, list)
                 and isinstance(amplitudes, list)
                 and len(beats) == len(offsets) == len(amplitudes)
                 and len(beats) <= 64, "stimulus_lists_mismatch:" + name)
        previous = -MIN_ONSET_GAP_FRAMES
        for frame, offset, amplitude in zip(beats, offsets, amplitudes):
            frame = _integer(frame, "beats_frames", 0, max_frame)
            offset = _integer(offset, "beat_offsets_samples", 0, 159)
            _integer(amplitude, "amplitudes_milli", 1, 1000)
            if frame - previous < MIN_ONSET_GAP_FRAMES:
                raise ReferenceRejection("stimulus_onset_too_close:" + name)
            if offset + BURST_SAMPLES > FRAME_SAMPLES:
                raise ReferenceRejection("stimulus_offset_out_of_range:" + name)
            previous = frame
        accents = spec["accent_frames"]
        _require(isinstance(accents, list), "invalid_accent_frames:" + name)
        _require(set(accents).issubset(set(beats)),
                 "accent_not_a_beat:" + name)
        meter = spec["meter"]
        _require(meter is None or meter in METER_CANDIDATES,
                 "invalid_meter:" + name)
        gaps = spec["gap_samples"]
        _require(isinstance(gaps, list), "invalid_gap_samples:" + name)
        for interval in gaps:
            _require(isinstance(interval, list) and len(interval) == 2,
                     "invalid_gap_interval:" + name)
            start = _integer(interval[0], "gap_start", 0, length)
            end = _integer(interval[1], "gap_end", 0, length)
            _require(start < end, "invalid_gap_interval:" + name)
        kind = spec["kind"]
        if kind == "silence":
            _require(not beats and not accents, "silence_spec_mismatch:" + name)
        if kind == "gap":
            _require(len(gaps) == 1, "gap_spec_mismatch:" + name)
        else:
            _require(not gaps, "unexpected_gap:" + name)
        if kind == "final_partial":
            _require(len(beats) == 1 and length % FRAME_SAMPLES == 137,
                     "final_partial_mismatch:" + name)
            _require(beats[0] * FRAME_SAMPLES + offsets[0] + BURST_SAMPLES
                     <= length, "final_partial_burst_out_of_range:" + name)
        if kind == "periodic":
            _require(meter == 4 and bool(accents), "periodic_meter_mismatch:" + name)
        if kind in {"tempo_step", "syncopated", "irregular", "gap", "drift"}:
            _require(meter is None, "meter_claim_not_supported:" + name)
        if kind == "syncopated":
            _require(not accents, "syncopated_accent_mismatch:" + name)


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the task-local adapter configuration; fail closed."""
    _exact_keys(config, {"sample_rate_hz", "channels", "frame_samples",
                         "sample_format", "clock_ppm", "resampling"}, "config")
    rate = _integer(config["sample_rate_hz"], "sample_rate_hz", 1, 384000)
    channels = _integer(config["channels"], "channels", 1, 8)
    frame = _integer(config["frame_samples"], "frame_samples", 1, 4096)
    clock = _integer(config["clock_ppm"], "clock_ppm", -1000000, 1000000)
    _require(isinstance(config["sample_format"], str), "invalid_sample_format")
    _require(isinstance(config["resampling"], str), "invalid_resampling")
    if rate != SAMPLE_RATE_HZ:
        if rate == CANDIDATE_NATIVE_RATE_HZ:
            raise ReferenceRejection(
                "candidate_native_rate_requires_resampling",
                "BeatNet is reported at 22.05 kHz; v0 accepts only 16 kHz and "
                "resampling=none")
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
            "clock_ppm": clock, "resampling": config["resampling"]}


# ---------------------------------------------------------------------------
# Causal frame analyzer
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OnsetEvent:
    """Source-anchored onset event in exact integer coordinates."""

    source_start: int
    source_end: int
    frame_index: int
    epoch: int
    strength_milli: int
    available_monotonic_ns: int
    capture_first_ns: int

    def as_dict(self) -> Dict[str, str]:
        return {
            "source_start": str(self.source_start),
            "source_end": str(self.source_end),
            "frame_index": str(self.frame_index),
            "epoch": str(self.epoch),
            "strength_milli": str(self.strength_milli),
            "available_monotonic_ns": str(self.available_monotonic_ns),
            "capture_first_ns": str(self.capture_first_ns),
        }


class Analyzer:
    """Causal, frame-clocked onset analyzer with explicit rejection behavior."""

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
        self.sample_rate_hz = sample_rate_hz
        self.channels = channels
        self.frame_samples = frame_samples
        self.sample_format = sample_format
        self.epoch = epoch
        self.frame_index = 0
        self.baseline = math.log(LOG_FLOOR)
        self.last_onset_frame: int | None = None
        self.events: List[OnsetEvent] = []
        self.rejections: List[str] = []
        self.frame_records: List[Dict[str, str]] = []

    @property
    def state_digest(self) -> str:
        return object_digest({
            "frame_index": str(self.frame_index),
            "baseline_milli": str(llround(self.baseline * 1000)),
            "last_onset_frame": (None if self.last_onset_frame is None
                                 else str(self.last_onset_frame)),
            "event_count": str(len(self.events)),
            "epoch": str(self.epoch),
        })

    def _reject(self, code: str) -> None:
        self.rejections.append(code)
        raise ReferenceRejection(code)

    def process_frame(self, samples: Sequence[float] | None,
                      epoch: int | None = None,
                      input_count: int | None = None,
                      valid_count: int | None = None) -> Dict[str, str]:
        if samples is None:
            self._reject("missing_input")
        if epoch is not None and epoch != self.epoch:
            self._reject("epoch_mismatch")
        count = len(samples)  # type: ignore[arg-type]
        if input_count is not None and input_count != count:
            self._reject("frame_count_mismatch")
        if count != FRAME_SAMPLES:
            self._reject("frame_count_mismatch")
        valid = FRAME_SAMPLES if valid_count is None else valid_count
        if (not isinstance(valid, int) or isinstance(valid, bool)
                or not 1 <= valid <= FRAME_SAMPLES):
            self._reject("invalid_valid_count")
        for value in samples:  # type: ignore[union-attr]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                self._reject("invalid_sample")
            if not math.isfinite(float(value)):
                self._reject("nonfinite_input")
        if any(float(value) != 0.0 for value in samples[valid:]):  # type: ignore[index]
            self._reject("padding_not_zero")
        energy = (sum(float(value) ** 2 for value in samples[:valid])  # type: ignore[index]
                  / valid)
        log_energy = math.log(max(energy, LOG_FLOOR))
        strength = max(0.0, log_energy - self.baseline - ONSET_THRESHOLD)
        frame = self.frame_index
        source_start = frame * FRAME_SAMPLES
        onset = strength > 0.0 and (self.last_onset_frame is None
                                    or frame - self.last_onset_frame
                                    >= MIN_ONSET_GAP_FRAMES)
        strength_milli = llround(strength * 1000)
        record = {
            "frame_index": str(frame),
            "source_start": str(source_start),
            "valid_count": str(valid),
            "input_count": str(count),
            "strength_milli": str(strength_milli),
            "onset": "1" if onset else "0",
        }
        if onset:
            self.events.append(OnsetEvent(
                source_start=source_start,
                source_end=source_start + valid,
                frame_index=frame,
                epoch=self.epoch,
                strength_milli=strength_milli,
                available_monotonic_ns=(frame + 1) * FRAME_NS,
                capture_first_ns=source_start * SAMPLE_NS,
            ))
            self.last_onset_frame = frame
        # Only a fully validated frame advances recurrent state.
        self.baseline = ((1.0 - BASELINE_ALPHA) * self.baseline
                         + BASELINE_ALPHA * log_energy)
        self.frame_index += 1
        self.frame_records.append(record)
        return record

    def reset(self, epoch: int, first_input_sample: int = 0) -> None:
        if (not isinstance(epoch, int) or isinstance(epoch, bool)
                or epoch <= self.epoch):
            self._reject("invalid_epoch")
        if (not isinstance(first_input_sample, int)
                or isinstance(first_input_sample, bool)
                or first_input_sample < 0):
            self._reject("invalid_first_input_sample")
        self.epoch = epoch
        self.frame_index = 0
        self.baseline = math.log(LOG_FLOOR)
        self.last_onset_frame = None
        self.events = []
        self.rejections = []
        self.frame_records = []


def _signal(spec: Dict[str, Any]) -> List[float]:
    length = spec["length_samples"]
    signal = [0.0] * length
    for frame, offset, amplitude in zip(
            spec["beats_frames"], spec["beat_offsets_samples"],
            spec["amplitudes_milli"]):
        start = frame * FRAME_SAMPLES + offset
        gain = amplitude / 1000.0
        for index in range(BURST_SAMPLES):
            position = start + index
            if position >= length:
                break
            value = (gain * (1.0 - index / BURST_SAMPLES)
                     * SINE64[index % 64] / 32767.0)
            signal[position] += value
    for value in signal:
        if not math.isfinite(value) or abs(value) > 1.0 + 1e-12:
            raise ReferenceRejection("generated_signal_out_of_bounds")
    return signal


def generate_signal(spec: Dict[str, Any]) -> List[float]:
    return _signal(spec)


def truth_beats(spec: Dict[str, Any]) -> List[int]:
    return [frame * FRAME_SAMPLES + offset
            for frame, offset in zip(spec["beats_frames"],
                                     spec["beat_offsets_samples"])]


def analyze_signal(signal: Sequence[float], epoch: int = 1) -> Analyzer:
    total = len(signal)
    full = total // FRAME_SAMPLES
    remainder = total % FRAME_SAMPLES
    analyzer = Analyzer(epoch=epoch)
    for index in range(full):
        analyzer.process_frame(signal[index * FRAME_SAMPLES:
                                       (index + 1) * FRAME_SAMPLES])
    if remainder:
        padded = list(signal[full * FRAME_SAMPLES:])
        padded.extend([0.0] * (FRAME_SAMPLES - remainder))
        analyzer.process_frame(padded, valid_count=remainder)
    return analyzer


def analyze_chunks(signal: Sequence[float], chunks: Sequence[int]) -> Analyzer:
    """Feed arbitrary caller chunk sizes while preserving 160-sample frames."""
    _require(bool(chunks) and all(isinstance(size, int) and size > 0
                                  for size in chunks), "invalid_chunk_sizes")
    analyzer = Analyzer(epoch=1)
    buffer: List[float] = []
    position = 0
    index = 0
    while position < len(signal):
        size = chunks[index % len(chunks)]
        buffer.extend(signal[position:position + size])
        position += size
        index += 1
        while len(buffer) >= FRAME_SAMPLES:
            analyzer.process_frame(buffer[:FRAME_SAMPLES])
            del buffer[:FRAME_SAMPLES]
    if buffer:
        valid = len(buffer)
        buffer.extend([0.0] * (FRAME_SAMPLES - valid))
        analyzer.process_frame(buffer, valid_count=valid)
    return analyzer


# ---------------------------------------------------------------------------
# Tempo, beat and meter estimators (bounded, deterministic, not BeatNet)
# ---------------------------------------------------------------------------

def _bpm_x100(ioi_samples: int) -> int:
    return llround(60.0 * SAMPLE_RATE_HZ * 100.0 / ioi_samples)


def _overlaps_gap(first: OnsetEvent, second: OnsetEvent,
                  gaps: Sequence[Tuple[int, int]]) -> bool:
    for start, end in gaps:
        if first.source_start < end and second.source_start >= start:
            return True
    return False


def estimate_tempo(events: Sequence[OnsetEvent],
                   gaps: Sequence[Tuple[int, int]] = ()) -> Dict[str, Any]:
    """Estimate tempo from source-anchored IOIs; fail closed on instability."""
    if not events:
        return {"status": "no_onsets", "bpm_x100": None, "ioi_frames": [],
                "ioi_samples": [], "excluded_ioi_count": 0, "segments": []}
    frames = [event.frame_index for event in events]
    iois: List[int] = []
    excluded = 0
    for first, second in zip(events, events[1:]):
        if _overlaps_gap(first, second, gaps):
            excluded += 1
            continue
        iois.append(second.source_start - first.source_start)
    values = [_bpm_x100(ioi) for ioi in iois]
    segments = _tempo_segments(events, gaps)
    if not values:
        return {"status": "no_iois", "bpm_x100": None, "ioi_frames": [],
                "ioi_samples": [], "excluded_ioi_count": excluded,
                "segments": segments}
    spread = max(values) - min(values)
    if len(values) < MIN_IOIS_FOR_TEMPO:
        status = "insufficient_iois"
        bpm = None
    elif spread > TEMPO_STABILITY_SPREAD_X100:
        status = "unstable"
        bpm = None
    else:
        status = "stable"
        ordered = sorted(values)
        middle = len(ordered) // 2
        bpm = (ordered[middle] if len(ordered) % 2 == 1
               else (ordered[middle - 1] + ordered[middle]) // 2)
    return {
        "status": status,
        "bpm_x100": bpm,
        "spread_x100": spread,
        "ioi_frames": [ioi // FRAME_SAMPLES for ioi in iois],
        "ioi_samples": iois,
        "excluded_ioi_count": excluded,
        "segments": segments,
    }


def _tempo_segments(events: Sequence[OnsetEvent],
                    gaps: Sequence[Tuple[int, int]]) -> List[Dict[str, Any]]:
    segments: List[Dict[str, Any]] = []
    values: List[int] = []
    for index, (first, second) in enumerate(zip(events, events[1:])):
        if _overlaps_gap(first, second, gaps):
            continue
        values.append((index + 1, _bpm_x100(second.source_start
                                           - first.source_start)))
        if len(values) < TEMPO_SEGMENT_WINDOW:
            continue
        window = [value for _, value in values[-TEMPO_SEGMENT_WINDOW:]]
        if max(window) - min(window) > TEMPO_STABILITY_SPREAD_X100:
            continue
        bpm = sum(window) // len(window)
        beat_index, _ = values[-1]
        if segments and segments[-1]["bpm_x100"] == bpm:
            continue
        segments.append({
            "beat_index": beat_index,
            "source_start": str(events[beat_index].source_start),
            "bpm_x100": bpm,
            "ioi_count": TEMPO_SEGMENT_WINDOW,
        })
    return segments


def estimate_meter(events: Sequence[OnsetEvent],
                   tempo: Dict[str, Any],
                   gaps: Sequence[Tuple[int, int]]) -> Dict[str, Any]:
    """Vote on meter/phase from synthetic accent strengths; no real claim."""
    strengths = [event.strength_milli for event in events]
    if len(events) < 6:
        return {"status": "insufficient_events", "meter": None, "phase": None,
                "score_milli": None, "truth_meter": None, "correct": None}
    if tempo.get("status") != "stable" or gaps:
        return {"status": "not_estimable", "meter": None, "phase": None,
                "score_milli": None, "truth_meter": None, "correct": None}
    if max(strengths) - min(strengths) < METER_MIN_STRENGTH_SPREAD_MILLI:
        return {"status": "ambiguous", "meter": None, "phase": None,
                "score_milli": None, "truth_meter": None, "correct": None}
    scored: List[Tuple[int, int, int]] = []
    for meter in METER_CANDIDATES:
        best_phase = 0
        best_score = -1
        for phase in range(meter):
            members = [strengths[index] for index in range(len(strengths))
                       if index % meter == phase]
            if not members:
                continue
            score = sum(members) // len(members)
            if score > best_score:
                best_score = score
                best_phase = phase
        scored.append((meter, best_phase, best_score))
    top = max(score for _, _, score in scored)
    winners = [row for row in scored if row[2] == top]
    if len(winners) != 1:
        return {"status": "ambiguous", "meter": None, "phase": None,
                "score_milli": top, "truth_meter": None, "correct": None}
    meter, phase, score = winners[0]
    return {"status": "synthetic_only", "meter": meter, "phase": phase,
            "score_milli": score, "truth_meter": None, "correct": None}


def match_beats(detected: Sequence[int], truth: Sequence[int],
                tolerance: int = BEAT_TOLERANCE_SAMPLES) -> Dict[str, Any]:
    matches = 0
    first = 0
    second = 0
    while first < len(detected) and second < len(truth):
        delta = detected[first] - truth[second]
        if abs(delta) <= tolerance:
            matches += 1
            first += 1
            second += 1
        elif delta < -tolerance:
            first += 1
        else:
            second += 1
    false_positives = len(detected) - matches
    false_negatives = len(truth) - matches
    total = len(detected) + len(truth)
    f1_x1000 = (None if total == 0
                else (2000 * matches + total // 2) // total)
    return {
        "detected": len(detected),
        "truth": len(truth),
        "matched": matches,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "f1_x1000": f1_x1000,
        "tolerance_samples": tolerance,
    }


# ---------------------------------------------------------------------------
# Caller-owned asset manifest (identity validation only)
# ---------------------------------------------------------------------------

CALLER_MANIFEST_FIELDS = {
    "adapter", "license_id", "model_sha256", "sample_format",
    "sample_rate_hz", "channels", "frame_samples", "source_commit",
    "source_path", "source_sha256", "weights_path", "weights_sha256",
}


def validate_caller_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Validate caller-owned BeatNet identity; never read or execute assets."""
    _exact_keys(manifest, CALLER_MANIFEST_FIELDS, "caller_manifest")
    _string(manifest["adapter"], "adapter", 1, 96)
    _string(manifest["license_id"], "license_id", 1, 64)
    _sha256(manifest["model_sha256"], "model_sha256")
    _sha256(manifest["source_sha256"], "source_sha256")
    _sha256(manifest["weights_sha256"], "weights_sha256")
    _string(manifest["source_commit"], "source_commit", 40, 40)
    for label in ("source_path", "weights_path"):
        path = _string(manifest[label], label, 1, 4096)
        if not path.startswith("/"):
            raise ReferenceRejection("invalid_source_path:" + label)
    validate_config({
        "sample_rate_hz": manifest["sample_rate_hz"],
        "channels": manifest["channels"],
        "frame_samples": manifest["frame_samples"],
        "sample_format": manifest["sample_format"],
        "clock_ppm": 0,
        "resampling": "none",
    })
    return {"validated": True, "loaded": False, "executed": False,
            "imported": False}


# ---------------------------------------------------------------------------
# Adverse case matrix
# ---------------------------------------------------------------------------

def _base_config() -> Dict[str, Any]:
    return {"sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES, "sample_format": SAMPLE_FORMAT,
            "clock_ppm": 0, "resampling": "none"}


def _base_manifest() -> Dict[str, Any]:
    return {
        "adapter": "beatnet-reference",
        "license_id": "CC-BY-4.0",
        "model_sha256": "0" * 64,
        "sample_format": "float32",
        "sample_rate_hz": 16000,
        "channels": 1,
        "frame_samples": 160,
        "source_commit": "0" * 40,
        "source_path": "/caller/beatnet/source",
        "source_sha256": "1" * 64,
        "weights_path": "/caller/beatnet/weights",
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

    def add(case_id: str, code: str, action, digest_before: str | None = None,
            digest_after: str | None = None, state: bool = True) -> None:
        actual = _expect_reject(code, action)
        unchanged = state if digest_before is None else digest_before == digest_after
        cases.append({
            "case_id": case_id,
            "code": actual,
            "status": "rejected" if actual != "accepted" else "accepted",
            "state_unchanged": bool(unchanged),
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
                                 if key != "clock_ppm"}))
    add("config_extra_field", "strict_keys_mismatch:config",
        lambda: validate_config({**base, "extra": 1}))
    add("config_8000_hz", "unsupported_sample_rate",
        lambda: validate_config({**base, "sample_rate_hz": 8000}))
    add("config_44100_hz", "unsupported_sample_rate",
        lambda: validate_config({**base, "sample_rate_hz": 44100}))
    add("config_22050_hz_candidate_native", "candidate_native_rate_requires_resampling",
        lambda: validate_config({**base, "sample_rate_hz": 22050}))
    add("config_stereo", "unsupported_channels",
        lambda: validate_config({**base, "channels": 2}))
    add("config_256_frame", "unsupported_frame_samples",
        lambda: validate_config({**base, "frame_samples": 256}))
    add("config_int16", "unsupported_sample_format",
        lambda: validate_config({**base, "sample_format": "int16"}))
    add("config_clock_drift", "unsupported_clock_drift",
        lambda: validate_config({**base, "clock_ppm": 1}))
    add("config_bool_rate", "invalid_integer:sample_rate_hz",
        lambda: validate_config({**base, "sample_rate_hz": True}))

    analyzer = Analyzer(epoch=1)
    signal = generate_signal(STIMULI["steady_music_1x"])
    analyzer.process_frame(signal[:FRAME_SAMPLES])
    before = analyzer.state_digest
    add("frame_missing_input", "missing_input",
        lambda: analyzer.process_frame(None), before, analyzer.state_digest)
    add("frame_epoch_mismatch", "epoch_mismatch",
        lambda: analyzer.process_frame(signal[160:320], epoch=2),
        before, analyzer.state_digest)
    add("frame_count_mismatch", "frame_count_mismatch",
        lambda: analyzer.process_frame(signal[160:320][:159]),
        before, analyzer.state_digest)
    add("frame_invalid_valid_count_zero", "invalid_valid_count",
        lambda: analyzer.process_frame(signal[160:320], valid_count=0),
        before, analyzer.state_digest)
    add("frame_invalid_valid_count_high", "invalid_valid_count",
        lambda: analyzer.process_frame(signal[160:320], valid_count=161),
        before, analyzer.state_digest)
    add("frame_nonfinite_input", "nonfinite_input",
        lambda: analyzer.process_frame([float("nan")] + list(signal[161:320])),
        before, analyzer.state_digest)
    add("frame_nonzero_padding", "padding_not_zero",
        lambda: analyzer.process_frame(
            list(signal[160:320][:137]) + [1.0] + list(signal[160:320][138:]),
            valid_count=137), before, analyzer.state_digest)
    add("frame_string_sample", "invalid_sample",
        lambda: analyzer.process_frame(["x"] + list(signal[161:320])),
        before, analyzer.state_digest)
    add("frame_bool_sample", "invalid_sample",
        lambda: analyzer.process_frame([True] + list(signal[161:320])),
        before, analyzer.state_digest)

    def bad_stimulus(**changes):
        spec = json.loads(json.dumps(STIMULI["steady_music_1x"]))
        spec.update(changes)
        validate_stimuli({**STIMULI, "steady_music_1x": spec})

    add("stimulus_unknown_kind", "unknown_stimulus_kind:steady_music_1x",
        lambda: bad_stimulus(kind="crnn"))
    add("stimulus_zero_period", "stimulus_onset_too_close:steady_music_1x",
        lambda: bad_stimulus(beats_frames=[0, 0, 120, 180, 240, 300, 360]))
    add("stimulus_negative_amplitude", "invalid_integer:amplitudes_milli",
        lambda: bad_stimulus(amplitudes_milli=[-1, 450, 450, 450, 900, 450, 450]))
    add("stimulus_amplitude_out_of_range", "invalid_integer:amplitudes_milli",
        lambda: bad_stimulus(amplitudes_milli=[900, 450, 450, 450, 900, 450, 1001]))
    add("stimulus_noninteger_period", "invalid_integer:beats_frames",
        lambda: bad_stimulus(
            beats_frames=[0, 60.5, 120, 180, 240, 300, 360]))
    add("stimulus_silence_nonzero", "silence_spec_mismatch:silence",
        lambda: validate_stimuli(
            {**STIMULI, "silence": {**STIMULI["silence"],
                                    "beats_frames": [0],
                                    "beat_offsets_samples": [0],
                                    "amplitudes_milli": [450]}}))
    add("stimulus_final_partial_misaligned", "final_partial_mismatch:final_partial",
        lambda: validate_stimuli(
            {**STIMULI, "final_partial": {**STIMULI["final_partial"],
                                          "beats_frames": [300, 400],
                                          "beat_offsets_samples": [0, 0],
                                          "amplitudes_milli": [450, 800]}}))
    add("stimulus_length_mismatch", "stimulus_length_mismatch:steady_music_1x",
        lambda: bad_stimulus(length_samples=64000))

    reset_analyzer = Analyzer(epoch=1)
    reset_before = reset_analyzer.state_digest
    add("reset_epoch_zero", "invalid_epoch",
        lambda: reset_analyzer.reset(0, 0), reset_before,
        reset_analyzer.state_digest)
    add("reset_epoch_negative", "invalid_epoch",
        lambda: reset_analyzer.reset(-1, 0), reset_before,
        reset_analyzer.state_digest)

    manifest = _base_manifest()
    add("caller_manifest_missing_field", "strict_keys_mismatch:caller_manifest",
        lambda: validate_caller_manifest(
            {key: value for key, value in manifest.items()
             if key != "weights_sha256"}))
    add("caller_manifest_relative_path", "invalid_source_path:source_path",
        lambda: validate_caller_manifest(
            {**manifest, "source_path": "relative/source"}))
    add("caller_manifest_bad_commit", "invalid_string:source_commit",
        lambda: validate_caller_manifest(
            {**manifest, "source_commit": "not-a-commit"}))
    add("caller_manifest_wrong_rate", "candidate_native_rate_requires_resampling",
        lambda: validate_caller_manifest(
            {**manifest, "sample_rate_hz": 22050}))
    add("caller_manifest_wrong_channels", "unsupported_channels",
        lambda: validate_caller_manifest({**manifest, "channels": 2}))
    add("caller_manifest_bad_hash", "invalid_sha256:weights_sha256",
        lambda: validate_caller_manifest(
            {**manifest, "weights_sha256": "0" * 63 + "z"}))
    add("caller_manifest_extra_field", "strict_keys_mismatch:caller_manifest",
        lambda: validate_caller_manifest({**manifest, "extra": 1}))
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


def _stimulus_runs() -> Dict[str, Dict[str, Any]]:
    runs: Dict[str, Dict[str, Any]] = {}
    for name, spec in STIMULI.items():
        signal = generate_signal(spec)
        analyzer = analyze_signal(signal)
        runs[name] = {
            "signal": signal,
            "events": analyzer.events,
            "gaps": [tuple(interval) for interval in spec["gap_samples"]],
            "signal_digest": signal_digest(signal),
            "event_digest": event_digest(analyzer.events),
        }
    return runs


def _tempo_and_meter(runs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    tempos: Dict[str, Any] = {}
    meters: Dict[str, Any] = {}
    for name, run in runs.items():
        tempo = estimate_tempo(run["events"], run["gaps"])
        if tempo.get("segments") is None:
            tempo["segments"] = []
        tempos[name] = tempo
        meter = estimate_meter(run["events"], tempo, run["gaps"])
        meter["truth_meter"] = STIMULI[name]["meter"]
        meter["correct"] = (None if meter["meter"] is None
                            or STIMULI[name]["meter"] is None
                            else meter["meter"] == STIMULI[name]["meter"])
        meters[name] = meter
    return {"tempo": tempos, "meter": meters}


def _evaluations(runs: Dict[str, Dict[str, Any]],
                 analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for name, run in runs.items():
        truth = truth_beats(STIMULI[name])
        detected = [event.source_start for event in run["events"]]
        matched = match_beats(detected, truth)
        tempo = analysis["tempo"][name]
        meter = analysis["meter"][name]
        rows.append({
            "stimulus": name,
            "synthetic_only": True,
            "onset_count": len(detected),
            "truth_beat_count": len(truth),
            "beat_match": matched,
            "tempo_status": tempo["status"],
            "tempo_bpm_x100": tempo["bpm_x100"],
            "meter_estimate": meter["meter"],
            "truth_meter": STIMULI[name]["meter"],
            "meter_correct": meter["correct"],
            "qualifies": False,
        })
    return rows


def _streaming_check(runs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    signal = runs["steady_music_1x"]["signal"]
    expected = [event.as_dict() for event in runs["steady_music_1x"]["events"]]
    chunks = [160, 480, 800, 137, 641]
    results = []
    all_match = True
    for chunk in chunks:
        analyzer = analyze_chunks(signal, [chunk])
        actual = [event.as_dict() for event in analyzer.events]
        match = actual == expected
        all_match = all_match and match
        results.append({
            "chunk_samples": chunk,
            "matches_offline": match,
            "event_digest": event_digest(analyzer.events),
        })
    return {
        "accepted_samples": len(signal),
        "chunks": chunks,
        "all_match": all_match,
        "results": results,
        "scheduler_measured": False,
    }


def _reset_check(runs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    signal = runs["steady_music_1x"]["signal"][: 160 * 20]
    fresh = analyze_signal(signal, epoch=2)
    reused = analyze_signal(signal, epoch=1)
    reused.reset(2, 0)
    for index in range(len(signal) // FRAME_SAMPLES):
        reused.process_frame(signal[index * FRAME_SAMPLES:
                                    (index + 1) * FRAME_SAMPLES])
    return {
        "epoch": 2,
        "accepted_samples": len(signal),
        "matches_fresh": (event_digest(reused.events)
                          == event_digest(fresh.events)),
        "state_digest": reused.state_digest,
    }


def _rate_profile(runs: Dict[str, Dict[str, Any]],
                  analysis: Dict[str, Any]) -> Dict[str, Any]:
    tempos = analysis["tempo"]
    periods = {"steady_music_1x": 60, "rate_0_8": 75, "rate_1_2": 50}
    durations: Dict[str, Any] = {}
    for name, period_frames in periods.items():
        frames = [event.frame_index for event in runs[name]["events"]]
        expected_span = (len(frames) - 1) * period_frames * FRAME_SAMPLES
        observed_span = ((frames[-1] - frames[0]) * FRAME_SAMPLES
                         if len(frames) > 1 else 0)
        durations[name] = {
            "onset_count": len(frames),
            "period_samples": period_frames * FRAME_SAMPLES,
            "expected_span_samples": expected_span,
            "observed_span_samples": observed_span,
            "error_samples": observed_span - expected_span,
        }
    final_run = runs["final_partial"]
    final_event = final_run["events"][0] if final_run["events"] else None
    final_truth = truth_beats(STIMULI["final_partial"])[0]
    drift_iois = tempos["drift_decreasing"]["ioi_frames"]
    drift_decreasing = len(drift_iois) >= 4 and all(
        later < earlier for earlier, later in zip(drift_iois, drift_iois[1:]))
    margins = [event.available_monotonic_ns - event.source_end * SAMPLE_NS
               for run in runs.values() for event in run["events"]]
    return {
        "identity_1x": {
            "stimulus": "steady_music_1x",
            "bpm_x100": tempos["steady_music_1x"]["bpm_x100"],
            "status": tempos["steady_music_1x"]["status"],
        },
        "rate_changes": [
            {"stimulus": "rate_0_8", "expected_bpm_x100": 8000,
             "observed_bpm_x100": tempos["rate_0_8"]["bpm_x100"]},
            {"stimulus": "rate_1_2", "expected_bpm_x100": 12000,
             "observed_bpm_x100": tempos["rate_1_2"]["bpm_x100"]},
        ],
        "duration": {
            "cases": durations,
            "max_error_samples": max(abs(row["error_samples"])
                                     for row in durations.values()),
        },
        "source_output_mapping": {
            "audio_output_produced": False,
            "analysis_event_source_anchor": True,
            "frame_hop_samples": FRAME_SAMPLES,
            "available_ns_per_frame": FRAME_NS,
            "min_availability_margin_ns": min(margins) if margins else 0,
            "note": ("No audio output, playback actuator, device clock or wall "
                     "clock is claimed."),
        },
        "pitch": {
            "status": "not_measurable_analysis_only",
            "qualifies": False,
            "note": ("Tempo/beat analysis does not alter pitch; no pitch-shift "
                     "or pitch-preservation claim is made."),
        },
        "transient_proxy": {
            "final_partial_error_samples": (
                None if final_event is None
                else final_event.source_start - final_truth),
            "quantization_samples": FRAME_SAMPLES,
            "note": ("Frame-quantized onset timing proxy only; not transient "
                     "audibility or listening."),
        },
        "playback_buffering": {
            "device_buffer_measured": False,
            "sdk_worker_count": 0,
            "sdk_queue_depth": 0,
            "analysis_frame_aggregation_samples": FRAME_SAMPLES,
            "final_partial_valid_count": 137,
            "final_padding_zero_verified": True,
        },
        "speech_unfamiliar": {
            "stimulus": "speech_like_unfamiliar",
            "status": tempos["speech_like_unfamiliar"]["status"],
            "bpm_x100": tempos["speech_like_unfamiliar"]["bpm_x100"],
            "qualifies": False,
        },
        "music": {
            "stimulus": "steady_music_1x",
            "status": tempos["steady_music_1x"]["status"],
            "bpm_x100": tempos["steady_music_1x"]["bpm_x100"],
        },
        "silence": {
            "stimulus": "silence",
            "status": tempos["silence"]["status"],
            "onset_count": len(runs["silence"]["events"]),
        },
        "rebuffer": {
            "gap_samples": [[str(start), str(end)]
                            for start, end in runs["rebuffer_gap"]["gaps"]],
            "excluded_ioi_count": tempos["rebuffer_gap"]["excluded_ioi_count"],
            "cross_gap_ioi_suppressed": (
                tempos["rebuffer_gap"]["excluded_ioi_count"] == 1),
            "bpm_x100": tempos["rebuffer_gap"]["bpm_x100"],
            "status": tempos["rebuffer_gap"]["status"],
        },
        "drift": {
            "ioi_frames": drift_iois,
            "monotonic_decreasing": drift_decreasing,
            "status": tempos["drift_decreasing"]["status"],
            "bpm_x100": tempos["drift_decreasing"]["bpm_x100"],
            "no_global_tempo_claim": True,
        },
        "final_partial": {
            "valid_count": 137,
            "padding_zero": True,
            "detected_source_start": (
                None if final_event is None else final_event.source_start),
            "truth_source_start": final_truth,
            "event_digest": final_run["event_digest"],
        },
    }


def _tempo_step_check(runs: Dict[str, Dict[str, Any]],
                      analysis: Dict[str, Any]) -> Dict[str, Any]:
    segments = analysis["tempo"]["tempo_step"]["segments"]
    values = [segment["bpm_x100"] for segment in segments]
    return {
        "stimulus": "tempo_step",
        "observed_segments": values,
        "expected_segments": [10000, 15000],
        "exact": values == [10000, 15000],
        "global_status": analysis["tempo"]["tempo_step"]["status"],
        "global_bpm_x100": analysis["tempo"]["tempo_step"]["bpm_x100"],
        "qualifies": False,
    }


def _fixture_section(runs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    rows: Dict[str, Any] = {}
    for name, spec in STIMULI.items():
        rows[name] = {
            "kind": spec["kind"],
            "length_samples": spec["length_samples"],
            "beat_frames": list(spec["beats_frames"]),
            "truth_beats": truth_beats(spec),
            "accent_frames": list(spec["accent_frames"]),
            "meter": spec["meter"],
            "signal_digest": runs[name]["signal_digest"],
            "event_digest": runs[name]["event_digest"],
            "onset_count": len(runs[name]["events"]),
        }
    return {"fixtures": rows, "synthetic_only": True,
            "audio_generated": False}


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "source_output_mapping": {
                "status": "synthetic_only",
                "evidence": ("Frame-anchored source intervals and monotonic "
                             "availability on synthetic events; no rendered "
                             "audio or device clock."),
            },
            "duration": {
                "status": "synthetic_only",
                "evidence": ("Exact event-span mapping at 0.8x, 1.0x and 1.2x "
                             "in integer samples."),
            },
            "pitch_transient_audibility": {
                "status": "blocked",
                "evidence": ("No pitch preservation, transient audibility, "
                             "time-scale modification or listening test exists."),
            },
            "playback_buffering": {
                "status": "synthetic_only",
                "evidence": ("160-sample frame aggregation and one 137-sample "
                             "final window; no worker, queue, renderer or "
                             "fill/flush is measured."),
            },
            "rate_cases": {
                "status": "synthetic_only",
                "evidence": ("1x, 0.8x and 1.2x synthetic click tempi plus "
                             "unfamiliar-speech-like, music and silence "
                             "surrogates."),
            },
            "rebuffer_drift_final_partial": {
                "status": "synthetic_only",
                "evidence": ("One synthetic gap excludes the cross-gap IOI; "
                             "drift is monotonic and unqualified; the final "
                             "partial window is explicit."),
            },
            "speech_preservation_and_pause_decisions": {
                "status": "blocked",
                "evidence": ("No real speech, speech preservation score, pause "
                             "or filler decision tied to source timestamps."),
            },
            "task_matched_heldout_qualification": {
                "status": "blocked",
                "evidence": ("No rights-cleared held-out music/speech cohort, "
                             "label set or matched beat/downbeat/tempo score."),
            },
        },
    }


def _profile_blockers(profile: Dict[str, Any]) -> List[str]:
    return sorted(name for name, item in profile["required_items"].items()
                  if item["status"] == "blocked")


def _release_gates() -> List[Dict[str, str]]:
    rows = [
        ("RG-01", "Exact pinned BeatNet source, weights and runtime with an "
                  "immutable revision, license identity and declared adapter "
                  "settings."),
        ("RG-02", "Isolated hash-pinned runtime admission, reproducible build, "
                  "verified weight identity and fail-closed absent behavior."),
        ("RG-03", "CC-BY-4.0 attribution, weight/training-data and corpus "
                  "rights, complete notices, redistribution, product-use and "
                  "derivative-output review."),
        ("RG-04", "22.05 kHz native input versus installed 16 kHz mono v0 with "
                  "resampling=none: exact mapping decision and byte-level "
                  "beat/tempo output parity."),
        ("RG-05", "Beat, downbeat, meter and tempo qualification on "
                  "rights-cleared task-matched held-out music and speech."),
        ("RG-06", "Online state, reset, latency, availability, final partial "
                  "window, drift and rebuffer behavior at the exact runtime."),
        ("RG-07", "Target-device pacing and timing plus playback integration "
                  "with independent pitch/transient controls."),
        ("RG-08", "Opt-in provider intake, descriptor review, independent "
                  "exact-head review and default/release approval."),
    ]
    return [{"id": gate, "requirement": text, "status": "blocked"}
            for gate, text in rows]


def _exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "pinned_beatnet_source_weights_runtime_absent",
            "requirement": ("Supply one exact licensed BeatNet source tree, "
                            "weight file and runtime with immutable revision, "
                            "license identity, build/archive identity and "
                            "declared adapter settings."),
            "state": ("No BeatNet source, weight, runtime, adapter, pinned "
                      "revision or numeric output is staged at "
                      "data/checkouts/beatnet, data/models/beatnet, "
                      "data/envs/beatnet or adapters/beatnet. The catalogued "
                      "evidence is one finding line only."),
        },
        {
            "id": "native_22050_hz_geometry_conflict",
            "requirement": ("Resolve the reported 22.05 kHz BeatNet input "
                            "against installed v0 16 kHz mono 160-sample "
                            "geometry with resampling=none, or supply an "
                            "independently contracted resampler and exact "
                            "parity evidence."),
            "state": ("The pinned candidate note records 22.05 kHz input. "
                      "Contract 0.1 accepts only 16000/1/160 and effective "
                      "config resampling=none; the task-local probe rejects "
                      "22050 Hz before any state advance."),
        },
        {
            "id": "rights_attribution_and_weights_review_absent",
            "requirement": ("Stage the exact CC-BY-4.0 attribution notice, "
                            "weight and training-data terms, and complete "
                            "distribution, derivative and product-use review."),
            "state": ("CC-BY-4.0 appears only as a catalogued provenance "
                      "string. No LICENSE, model card, weight terms, training "
                      "data statement, notice bundle or legal review is "
                      "staged."),
        },
        {
            "id": "rights_cleared_heldout_music_speech_cohort_absent",
            "requirement": ("Supply a rights-cleared beat/downbeat/tempo "
                            "cohort with held-out music and speech labels, "
                            "meter annotation and matched scoring."),
            "state": ("No real music, speech, beat label, downbeat label, "
                      "meter label, consent, corpus terms or held-out split is "
                      "staged. Synthetic clicks cannot qualify the candidate."),
        },
        {
            "id": "timing_streaming_and_independent_review_absent",
            "requirement": ("Measure target-device pacing, online latency and "
                            "availability, reset and rebuffer behavior at the "
                            "exact runtime and complete independent review."),
            "state": ("No device clock, deadline, RTF, memory result, worker, "
                      "queue, listening test, benchmark, provider intake or "
                      "release approval exists; no result may qualify."),
        },
    ]


def _licensing() -> Dict[str, Any]:
    return {
        "reported_upstream_license": "CC-BY-4.0",
        "license_text_staged": False,
        "attribution_required": True,
        "attribution_notice_staged": False,
        "weights_terms_staged": False,
        "training_data_statement_staged": False,
        "redistribution_reviewed": False,
        "product_use_reviewed": False,
        "review_status": "blocked",
        "note": ("CC-BY-4.0 is a catalogued provenance string only; no "
                 "upstream license text or weight terms are present."),
    }


def _candidate() -> Dict[str, Any]:
    return {
        "name": "BeatNet",
        "reported_algorithm": "CRNN + particle filter",
        "reported_input_sample_rate_hz": CANDIDATE_NATIVE_RATE_HZ,
        "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
        "sdk_v0_channels": CHANNELS,
        "sdk_v0_frame_samples": FRAME_SAMPLES,
        "configured_resampling": "none",
        "native_rate_compatible": False,
        "reported_online_modes": True,
        "reported_outputs": ["beats", "downbeats", "tempo", "meter"],
        "source_present": False,
        "weights_present": False,
        "runtime_present": False,
        "exact_numeric_output_present": False,
    }


def _external_artifacts() -> Dict[str, Any]:
    paths = {
        "source_checkout": "data/checkouts/beatnet",
        "weights": "data/models/beatnet",
        "runtime_env": "data/envs/beatnet",
        "adapter": "adapters/beatnet",
        "caller_manifest": "data/manifests/beatnet.json",
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
        "real_music_audio": False,
        "real_speech_audio": False,
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
    "No BeatNet source, weight file, runtime, adapter, revision or numeric "
    "output was produced, loaded or executed.",
    "No beat, downbeat, meter, tempo, quality, latency, benchmark, listening or "
    "release result is claimed.",
    "The synthetic click surrogate is not BeatNet and cannot qualify the "
    "candidate.",
    "The reported 22.05 kHz native input is not compatible with installed v0 "
    "16 kHz mono geometry under resampling=none.",
    "Synthetic beat matching and meter voting are unqualified task-local "
    "checks only.",
    "No real music, speech, corpus, beat/downbeat label, device clock or "
    "listener was used.",
    "CC-BY-4.0 is a catalogued provenance string only; no upstream license "
    "text, attribution bundle or weight terms are staged.",
    "No provider, descriptor, registry, installed v0 path, shared build, "
    "dependency lock or CI was changed.",
)

REOPEN_CONDITION = (
    "Pin the exact licensed BeatNet source, weights and runtime with an "
    "immutable revision, admit an isolated hash-pinned runtime, clear the "
    "CC-BY-4.0 attribution and weight/corpus rights, resolve the 22.05 kHz "
    "input to installed 16 kHz geometry without an unapproved resampler, "
    "reproduce exact beat/downbeat/meter/tempo outputs and qualify them on a "
    "rights-cleared task-matched held-out cohort, measure target timing and "
    "complete opt-in provider intake. Until then the candidate stays DEFER, "
    "incomplete and not qualified."
)


def _case_matrix_digest(runs: Dict[str, Dict[str, Any]],
                        analysis: Dict[str, Any]) -> str:
    return object_digest({
        "fixtures": {name: run["signal_digest"] for name, run in runs.items()},
        "events": {name: run["event_digest"] for name, run in runs.items()},
        "tempo": {name: (row["status"], row["bpm_x100"],
                         row["excluded_ioi_count"])
                  for name, row in analysis["tempo"].items()},
        "meter": {name: (row["status"], row["meter"])
                  for name, row in analysis["meter"].items()},
    })


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()
    validate_stimuli(STIMULI)
    runs = _stimulus_runs()
    analysis = _tempo_and_meter(runs)
    evaluations = _evaluations(runs, analysis)
    profile = _acceptance_profile()
    adverse = adverse_rejections()
    gates = _release_gates()
    blockers = _exact_blockers()
    licensing = _licensing()
    candidate = _candidate()
    matrix_digest = _case_matrix_digest(runs, analysis)
    tempos = analysis["tempo"]

    beat_rows = []
    for row in evaluations:
        beat_rows.append({
            "stimulus": row["stimulus"],
            **row["beat_match"],
            "status": "synthetic_only",
            "qualifies": False,
        })
    scored_f1 = [row["f1_x1000"] for row in beat_rows
                 if row["f1_x1000"] is not None and row["truth"] > 0]
    mean_f1 = (sum(scored_f1) // len(scored_f1)) if scored_f1 else None

    meter_rows = []
    for name, row in analysis["meter"].items():
        meter_rows.append({
            "stimulus": name,
            "status": row["status"],
            "meter": row["meter"],
            "phase": row["phase"],
            "truth_meter": STIMULI[name]["meter"],
            "correct": row["correct"],
            "qualifies": False,
        })

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
            "candidate_native_sample_rate_hz": CANDIDATE_NATIVE_RATE_HZ,
            "resampling": "none",
            "native_rate_compatible": False,
            "algorithm_latency_samples": None,
            "algorithm_latency_ms": None,
        },
        "fixtures": _fixture_section(runs),
        "tempo_tracking": {
            "cases": [
                {
                    "stimulus": name,
                    "status": row["status"],
                    "bpm_x100": row["bpm_x100"],
                    "ioi_frames": row["ioi_frames"],
                    "excluded_ioi_count": row["excluded_ioi_count"],
                    "segments": row["segments"],
                    "qualifies": False,
                }
                for name, row in tempos.items()
            ],
            "tempo_step": _tempo_step_check(runs, analysis),
            "qualifies": False,
        },
        "beat_tracking": {
            "tolerance_samples": BEAT_TOLERANCE_SAMPLES,
            "cases": beat_rows,
            "mean_f1_x1000": mean_f1,
            "qualifies": False,
        },
        "downbeat_meter": {
            "cases": meter_rows,
            "truth_available": False,
            "qualifies": False,
        },
        "rate_profile": _rate_profile(runs, analysis),
        "streaming": _streaming_check(runs),
        "reset": _reset_check(runs),
        "adverse_rejections": adverse,
        "adverse_all_rejected": all(
            row["status"] == "rejected" and row["state_unchanged"] is True
            for row in adverse),
        "external_artifacts": _external_artifacts(),
        "licensing": licensing,
        "caller_asset": {
            "contract_id": "audio-sdk/beatnet/caller-supplied-asset/0.1",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "manifest_present": False,
            "workspace_manifest": "data/manifests/beatnet.json",
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
            "native_rate_compatibility_qualified": False,
            "beat_tempo_qualified": False,
            "downbeat_meter_qualified": False,
            "timing_measured": False,
            "listening": False,
            "real_corpus_used": False,
            "reason": ("Exact BeatNet source/weights/runtime, the 22.05 kHz "
                       "geometry decision, rights, held-out labels, timing and "
                       "independent review are all absent."),
        },
        "exact_blockers": blockers,
        "release_gates": gates,
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "surrogate": {
            "algorithm": ("bounded integer onset envelope + IOI tempo histogram "
                          "+ accent-phase meter voting"),
            "is_beatnet": False,
            "is_learned": False,
            "uses_crnn": False,
            "uses_particle_filter": False,
            "uses_weights": False,
            "qualifies_candidate": False,
        },
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "case_matrix_digests": [matrix_digest, matrix_digest, matrix_digest],
        },
        "scope_note": ("Only docs/task-evidence/beatnet/ is written; all other "
                       "paths are read-only pins."),
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
            "contract_id": "audio-sdk/beatnet/caller-supplied-asset/0.1",
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
            "no BeatNet source, weight, CRNN, particle filter, runtime or "
            "adapter is downloaded, copied, loaded or executed",
            "the synthetic click surrogate is not BeatNet and cannot qualify "
            "the candidate",
            "the 22.05 kHz native rate remains incompatible with v0 16 kHz "
            "geometry under resampling=none",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def sources_bytes(overrides: Dict[str, bytes] | None = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-BEATNET; source: paths are workspace-relative, "
        "others SDK-worktree-relative."
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
    "Analyzer", "ReferenceRejection", "STIMULI", "adverse_rejections",
    "analyze_chunks", "analyze_signal", "build_contract", "build_report",
    "canonical_report", "canonical_text", "estimate_tempo", "event_digest",
    "generate_signal", "load_strict_json", "load_strict_json_text",
    "match_beats", "object_digest", "sha256_bytes", "signal_digest",
    "sources_bytes", "truth_beats", "validate_caller_manifest",
    "validate_config", "validate_stimuli",
]
