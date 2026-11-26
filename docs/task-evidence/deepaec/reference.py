# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local reference for SDK-DEEPAEC (DeepAEC).

The exact licensed DeepAEC paper, source revision, weights, runtime and numeric
output are absent and the canonical identity itself is unresolved. This module
therefore implements **no** DeepAEC layer, weight, network, echo canceller,
ONNX graph, adapter or runtime. It provides only:

* strict fail-closed JSON/config/manifest/identity parsers;
* a canonical-name resolver that refuses every near-name and related-paper
  substitution and returns ``identity_unresolved`` for the exact recorded name;
* a frozen synthetic two-channel (render/capture) room fixture and exact
  integer delay-estimation / ERLE / near-end-SNR arithmetic used purely to
  exercise the Room-profile measurement accounting;
* a caller-supplied future-asset admission manifest validator with an adverse
  rejection matrix;
* deterministic report and contract builders.

Nothing here reads audio, a weight file, a source tree or a runtime, and nothing
here is a candidate result. All evidence is task-local, synthetic and
unqualified.
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
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA = "audio-sdk/deepaec-readiness/0.1"
TASK_ID = "SDK-DEEPAEC"
TITLE = "DeepAEC"
COMPONENT = "deepaec"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "91c16ba867dd9cba8a41bd9202d00712d409277a"
BRANCH = "swarm/SDK-DEEPAEC"
REVIEWER = "reviewer-DEEPAEC"
PROFILE = "room"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
STATUS = "proposal_only_incomplete"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_NS = 62500
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS

Q15 = 32768
MAX_Q15 = 32767
MIN_Q15 = -32768

ROOM_LENGTH = 9600
MAX_LAG_SAMPLES = 1600
PATH_DELAY_SAMPLES = 480
PATH_TAPS: Tuple[Tuple[int, int], ...] = ((0, 12000), (37, -3000), (113, 1500))
DELAYED_RENDER_EXTRA_SAMPLES = 320
MAX_MILLIDB = 300000
MIN_MILLIDB = -300000

CANONICAL_RECORDED_NAME = "DeepAEC"
RECORDED_STATUS = "unavailable/blocked"
RECORDED_FINDING = (
    "Exact canonical name/citation/checkpoint unresolved; no substitute used"
)

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

REGIONS: Tuple[Dict[str, Any], ...] = (
    {"name": "echo_only", "start": 0, "end": 3200,
     "render": True, "echo": True, "near": False, "noise_amplitude": 300},
    {"name": "near_end_only", "start": 3200, "end": 6400,
     "render": True, "echo": False, "near": True, "noise_amplitude": 300},
    {"name": "double_talk", "start": 6400, "end": 9600,
     "render": True, "echo": True, "near": True, "noise_amplitude": 300},
)
REGION_KEYS = {"name", "start", "end", "render", "echo", "near",
               "noise_amplitude"}
DELAY_ESTIMATE_REGION = (MAX_LAG_SAMPLES, 3200)

SOURCE_PINS = {
    "research/voice-enhancement-20261101/candidate_matrix.csv": (
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245"
    ),
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md": (
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4"
    ),
    "research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md": (
        "5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14"
    ),
    "research/voice-enhancement-20261101/findings.md": (
        "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c"
    ),
    "research/aec_research_20261028.md": (
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180"
    ),
    "audio-benchmark-platform/plan/INVENTORY.json": (
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c"
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
    ".github/workflows/ci.yml": (
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415"
    ),
    "README.md": (
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35"
    ),
    "docs/task-evidence/aecmos/report.json": (
        "8055f6627d462c124182743469109a850087c11773899a6f64b02309be16c320"
    ),
    "docs/task-evidence/webrtc-aec3/report.json": (
        "da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283"
    ),
    "docs/task-evidence/nlms-aec/report.json": (
        "2910e9e986259a9de738822c35a2908e47a836a9daabc292118f6c7389988f6a"
    ),
    "docs/task-evidence/rls-aec/report.json": (
        "3fd2611c1b4619fab5858a78ee62920b66fd7acfb6aaac79b613dffd169e3b25"
    ),
    "docs/task-evidence/cagcrn-joint-aec-and-ns/report.json": (
        "697eb9feb470d529ba8132a8d597cb52308f46f5d2c6afd36803de268f9d7828"
    ),
    "docs/task-evidence/localvqe-compact-echo-only/report.json": (
        "28b17d5ee0afa2f017009456ef58d0fbac6383bf64744682e7400079df862369"
    ),
}

BOARD_ROW_STABLE_SHA256 = (
    "b4c62f1b2d0d44bae239617bf2586a9a789ec04122fadcf436e61d8ea5f226e9"
)
BOARD_LINKED_ROWS_SHA256 = (
    "00ad9e8c5db7be8a5b0e93e4bcdd727b4d811bf78f5af2bbfff4984091039c8b"
)

TASK_PREFIX = "docs/task-evidence/deepaec/"
ARTIFACT_FILES: Tuple[str, ...] = (
    "LICENSES.md",
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

PROVENANCE_PHRASES: Tuple[Tuple[str, str], ...] = (
    ("research/voice-enhancement-20261101/candidate_matrix.csv",
     "AEC,DeepAEC,unavailable/blocked,Exact canonical name/citation/checkpoint "
     "unresolved; no substitute used"),
    ("research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
     "No candidate with this exact canonical name, adapter, checkpoint or "
     "report was found in local records or primary-source search."),
    ("research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
     "Similar but distinct papers include Deep Echo Path Modeling and "
     "MSA-DPCRN"),
    ("research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
     "Need exact citation/repository/checkpoint identity before evaluating "
     "this name."),
    ("research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md",
     "DeepAEC and Dual-Path Echo Net remain ambiguous names without one "
     "canonical paper/source/checkpoint."),
    ("research/voice-enhancement-20261101/findings.md",
     "do not identify one verified source/checkpoint in this workspace"),
    ("research/voice-enhancement-20261101/findings.md",
     "No similar-sounding architecture was silently substituted."),
)

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


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


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


def int_signal_digest(samples: Sequence[int]) -> str:
    return sha256_bytes(struct.pack("<%di" % len(samples), *samples))


def quantize(value: object, label: str = "input") -> int:
    """Strict float32-boundary sample to exact Q15 integer; fail closed."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceRejection("invalid_sample:" + label)
    number = float(value)
    if not math.isfinite(number):
        raise ReferenceRejection("nonfinite_input:" + label)
    if number < -1.0 or number > 1.0:
        raise ReferenceRejection("sample_out_of_range:" + label)
    scaled = int(number * Q15)
    return MAX_Q15 if scaled > MAX_Q15 else scaled


def _energy(samples: Sequence[int], start: int, end: int) -> int:
    total = 0
    for index in range(start, end):
        value = int(samples[index])
        total += value * value
    return total


def _millidb(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        return MAX_MILLIDB
    if numerator <= 0:
        return MIN_MILLIDB
    value = 10000.0 * (math.log10(numerator) - math.log10(denominator))
    if value > MAX_MILLIDB:
        return MAX_MILLIDB
    if value < MIN_MILLIDB:
        return MIN_MILLIDB
    return int(round(value))


def snr_millidb(reference: Sequence[int], estimate: Sequence[int],
                start: int, end: int) -> int:
    signal_energy = _energy(reference, start, end)
    error = 0
    for index in range(start, end):
        difference = int(estimate[index]) - int(reference[index])
        error += difference * difference
    return _millidb(signal_energy, error)


def erle_millidb(capture: Sequence[int], residual: Sequence[int],
                 start: int, end: int) -> int:
    """Exact integer echo return loss enhancement in millidB."""
    return _millidb(_energy(capture, start, end), _energy(residual, start, end))


# ---------------------------------------------------------------------------
# Frozen synthetic render/capture room fixture (authored, not recorded)
# ---------------------------------------------------------------------------

def _lcg_values(seed: int, count: int) -> List[int]:
    state = seed & 0x7FFFFFFF
    values: List[int] = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append((state % 65535) - 32767)
    return values


def _voice_values(count: int, offsets: Tuple[int, int, int],
                  amplitude: int) -> List[int]:
    envelope = (3000, 2800, 2400, 1800, 1200, 0, 0, 1400, 2200, 3000)
    first, second, third = offsets
    values: List[int] = []
    for index in range(count):
        tone = (3 * SINE64[(index + first) % 64]
                + 2 * SINE64[(2 * index + second) % 64]
                + SINE64[(3 * index + third) % 64]) // 6
        level = envelope[(index // FRAME_SAMPLES) % len(envelope)]
        values.append(tone * level * amplitude // (32767 * 3000))
    return values


def room_geometry() -> Dict[str, Any]:
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "length_samples": ROOM_LENGTH,
        "duration_ns": ROOM_LENGTH * SAMPLE_NS,
        "path_delay_samples": PATH_DELAY_SAMPLES,
        "path_delay_ns": PATH_DELAY_SAMPLES * SAMPLE_NS,
        "path_taps": [{"offset_samples": offset, "coefficient_q15": gain}
                      for offset, gain in PATH_TAPS],
        "delayed_render_extra_samples": DELAYED_RENDER_EXTRA_SAMPLES,
        "regions": [dict(region) for region in REGIONS],
        "room_impulse_response": "synthetic_fixed_not_measured",
        "movement_modeled": False,
        "recorded_audio": False,
    }


def _region(name: str) -> Dict[str, Any]:
    for region in REGIONS:
        if region["name"] == name:
            return region
    raise ReferenceRejection("unknown_region:" + name)


def _echo_values(render: Sequence[int], extra_delay: int) -> List[int]:
    values = [0] * len(render)
    for index in range(len(render)):
        total = 0
        for offset, gain in PATH_TAPS:
            source = index - PATH_DELAY_SAMPLES - extra_delay - offset
            if source >= 0:
                total += int(render[source]) * gain
        values[index] = total >> 15
    return values


def build_room_fixture(extra_delay_samples: int = 0) -> Dict[str, Any]:
    """Build frozen synthetic render/capture Q15 signals; no audio is read."""
    _integer(extra_delay_samples, "extra_delay_samples", 0,
             MAX_LAG_SAMPLES)
    render = _voice_values(ROOM_LENGTH, (0, 7, 13), 12000)
    near_all = _voice_values(ROOM_LENGTH, (5, 11, 3), 8000)
    noise_base = _lcg_values(20261126, ROOM_LENGTH)
    echo_all = _echo_values(render, extra_delay_samples)
    echo = [0] * ROOM_LENGTH
    near = [0] * ROOM_LENGTH
    noise = [0] * ROOM_LENGTH
    for region in REGIONS:
        start, end = int(region["start"]), int(region["end"])
        for index in range(start, end):
            if region["echo"]:
                echo[index] = echo_all[index]
            if region["near"]:
                near[index] = near_all[index]
            noise[index] = (noise_base[index] * int(region["noise_amplitude"])
                            // 32767)
    capture = [max(MIN_Q15, min(MAX_Q15, echo[index] + near[index]
                                + noise[index]))
               for index in range(ROOM_LENGTH)]
    return {"render": render, "echo": echo, "near": near, "noise": noise,
            "capture": capture, "extra_delay_samples": extra_delay_samples}


# ---------------------------------------------------------------------------
# Exact integer room measurement arithmetic (synthetic oracle only)
# ---------------------------------------------------------------------------

def _prepare_signal(values: object, label: str,
                    length: int | None) -> List[int]:
    if values is None:
        raise ReferenceRejection("missing_input:" + label)
    if not isinstance(values, (list, tuple)):
        raise ReferenceRejection("invalid_frame:" + label)
    if len(values) == 0:
        raise ReferenceRejection("invalid_signal_length:" + label)
    if len(values) > 960000:
        raise ReferenceRejection("invalid_signal_length:" + label)
    if length is not None and len(values) != length:
        raise ReferenceRejection("signal_length_mismatch:" + label)
    prepared: List[int] = []
    for value in values:
        if isinstance(value, bool):
            raise ReferenceRejection("invalid_sample:" + label)
        if isinstance(value, int):
            if not MIN_Q15 <= value <= MAX_Q15:
                raise ReferenceRejection("sample_out_of_range:" + label)
            prepared.append(value)
        elif isinstance(value, float):
            prepared.append(quantize(value, label))
        else:
            raise ReferenceRejection("invalid_sample:" + label)
    return prepared


def prepare_room_case(render: object, capture: object,
                      max_lag_samples: object = MAX_LAG_SAMPLES
                      ) -> Dict[str, Any]:
    """Quantize and validate one task-local synthetic room case."""
    lag = _integer(max_lag_samples, "max_lag_samples", 1, MAX_LAG_SAMPLES)
    render_q15 = _prepare_signal(render, "render", None)
    capture_q15 = _prepare_signal(capture, "capture", len(render_q15))
    return {"render": render_q15, "capture": capture_q15,
            "max_lag_samples": lag}


def estimate_render_delay(render: Sequence[int], capture: Sequence[int],
                          max_lag_samples: int = MAX_LAG_SAMPLES,
                          start: int | None = None,
                          end: int | None = None) -> Dict[str, Any]:
    """Exact integer cross-correlation render-delay estimate.

    Returns ``lag_samples`` such that ``render[n - lag]`` best explains
    ``capture[n]``. A zero render reference is rejected, never guessed.
    """
    _integer(max_lag_samples, "max_lag_samples", 1, MAX_LAG_SAMPLES)
    length = len(render)
    _require(length > 0, "invalid_signal_length:render")
    _require(len(capture) == length, "signal_length_mismatch:capture")
    window_start = max_lag_samples if start is None else start
    window_end = length if end is None else end
    _integer(window_start, "start", 0, length)
    _integer(window_end, "end", 0, length)
    _require(window_end - window_start >= 1, "empty_estimate_window")
    _require(window_start - max_lag_samples >= 0, "estimate_window_too_early")
    capture_energy = _energy(capture, window_start, window_end)
    if capture_energy <= 0:
        raise ReferenceRejection("no_capture_signal")
    reference_energy = _energy(render, window_start - max_lag_samples,
                               window_end)
    if reference_energy <= 0:
        raise ReferenceRejection("no_render_reference")
    best: Dict[str, Any] | None = None
    for lag in range(0, max_lag_samples + 1):
        cross = 0
        for index in range(window_start, window_end):
            cross += int(render[index - lag]) * int(capture[index])
        lag_energy = _energy(render, window_start - lag, window_end - lag)
        denominator = lag_energy * capture_energy
        correlation_milli = (cross * cross * 1000 // denominator
                             if denominator > 0 else 0)
        candidate = {"lag_samples": lag,
                     "correlation_milli": correlation_milli}
        if (best is None
                or correlation_milli > best["correlation_milli"]
                or (correlation_milli == best["correlation_milli"]
                    and lag < best["lag_samples"])):
            best = candidate
    assert best is not None
    return {"lag_samples": best["lag_samples"],
            "correlation_milli": best["correlation_milli"],
            "evaluated_lags": max_lag_samples + 1,
            "window_start": window_start,
            "window_end": window_end,
            "exact_integer": True}


def _residual(capture: Sequence[int], echo: Sequence[int],
              start: int, end: int) -> List[int]:
    values = [0] * len(capture)
    for index in range(start, end):
        values[index] = max(MIN_Q15, min(MAX_Q15,
                                         int(capture[index]) - int(echo[index])))
    return values


def _case(name: str, region: Dict[str, Any]) -> Dict[str, Any]:
    return {"name": name, "start": region["start"], "end": region["end"],
            "qualifies": False, "scope": "synthetic_arithmetic_oracle"}


def room_case_results() -> Dict[str, Any]:
    """Score the frozen synthetic cases with exact oracle arithmetic."""
    base = build_room_fixture()
    delayed = build_room_fixture(DELAYED_RENDER_EXTRA_SAMPLES)
    echo_region = _region("echo_only")
    near_region = _region("near_end_only")
    talk_region = _region("double_talk")

    echo_residual = _residual(base["capture"], base["echo"],
                              echo_region["start"], echo_region["end"])
    talk_residual = _residual(base["capture"], base["echo"],
                              talk_region["start"], talk_region["end"])
    near_residual = _residual(base["capture"], base["echo"],
                              near_region["start"], near_region["end"])

    echo_case = _case("echo_only", echo_region)
    echo_case.update({
        "capture_energy": _energy(base["capture"], echo_region["start"],
                                  echo_region["end"]),
        "residual_energy": _energy(echo_residual, echo_region["start"],
                                   echo_region["end"]),
        "echo_return_loss_enhancement_millidb": erle_millidb(
            base["capture"], echo_residual, echo_region["start"],
            echo_region["end"]),
        "near_end_snr_millidb": None,
        "near_end_snr_code": "no_near_end_reference",
    })

    near_case = _case("near_end_only", near_region)
    near_case.update({
        "echo_return_loss_enhancement_millidb": None,
        "erle_code": "no_echo_component",
        "near_end_snr_millidb": snr_millidb(
            base["near"], near_residual, near_region["start"],
            near_region["end"]),
    })

    talk_case = _case("double_talk", talk_region)
    talk_case.update({
        "echo_return_loss_enhancement_millidb": None,
        "erle_code": "erle_only_on_far_end_only",
        "residual_over_capture_millidb": _millidb(
            _energy(talk_residual, talk_region["start"], talk_region["end"]),
            _energy(base["capture"], talk_region["start"],
                    talk_region["end"])),
        "near_end_snr_millidb": snr_millidb(
            base["near"], talk_residual, talk_region["start"],
            talk_region["end"]),
    })

    nominal = estimate_render_delay(base["render"], base["capture"],
                                    MAX_LAG_SAMPLES,
                                    DELAY_ESTIMATE_REGION[0],
                                    DELAY_ESTIMATE_REGION[1])
    shifted = estimate_render_delay(delayed["render"], delayed["capture"],
                                    MAX_LAG_SAMPLES,
                                    DELAY_ESTIMATE_REGION[0],
                                    DELAY_ESTIMATE_REGION[1])
    true_delayed = PATH_DELAY_SAMPLES + DELAYED_RENDER_EXTRA_SAMPLES

    missing = build_room_fixture()
    missing["render"] = [0] * ROOM_LENGTH
    try:
        estimate_render_delay(missing["render"], missing["capture"],
                              MAX_LAG_SAMPLES,
                              DELAY_ESTIMATE_REGION[0],
                              DELAY_ESTIMATE_REGION[1])
        missing_code = "accepted"
    except ReferenceRejection as error:
        missing_code = error.code

    return {
        "cases": [echo_case, near_case, talk_case],
        "delay_estimation": {
            "nominal": dict(nominal, expected_lag_samples=PATH_DELAY_SAMPLES,
                            error_samples=(nominal["lag_samples"]
                                           - PATH_DELAY_SAMPLES),
                            qualifies=False),
            "delayed_render": dict(shifted,
                                   expected_lag_samples=true_delayed,
                                   error_samples=(shifted["lag_samples"]
                                                  - true_delayed),
                                   qualifies=False),
            "missing_render": {
                "status": "not_estimable" if missing_code != "accepted"
                else "mismatch",
                "observed_code": missing_code,
                "expected_code": "no_render_reference",
                "lag_samples": None,
                "qualifies": False,
            },
        },
        "signal_digests": {
            "render": int_signal_digest(base["render"]),
            "echo": int_signal_digest(base["echo"]),
            "near": int_signal_digest(base["near"]),
            "noise": int_signal_digest(base["noise"]),
            "capture": int_signal_digest(base["capture"]),
            "delayed_capture": int_signal_digest(delayed["capture"]),
        },
    }


# ---------------------------------------------------------------------------
# Canonical identity resolver (exact match only; no alias merging)
# ---------------------------------------------------------------------------

RELATED_BUT_DISTINCT = (
    {
        "name": "Deep Echo Path Modeling",
        "recorded_as": "similar but distinct Interspeech 2024 paper",
        "paper_url": "https://www.isca-archive.org/interspeech_2024/"
                     "zhao24_interspeech.html",
        "substitutable": False,
        "reason": ("Different reported method and no shared canonical name, "
                   "known checkpoint, output contract or rights record."),
    },
    {
        "name": "MSA-DPCRN",
        "recorded_as": "similar but distinct Interspeech 2024 paper",
        "paper_url": "https://www.isca-archive.org/interspeech_2024/"
                     "ni24_interspeech.html",
        "substitutable": False,
        "reason": ("Different architecture and no shared canonical name, "
                   "known checkpoint, output contract or rights record."),
    },
    {
        "name": "DPCTNet",
        "recorded_as": "similar but distinct dual-path Interspeech 2022 paper",
        "paper_url": "https://www.isca-archive.org/interspeech_2022/"
                     "han22c_interspeech.html",
        "substitutable": False,
        "reason": ("Different dual-path formulation with no shared canonical "
                   "name, checkpoint, output contract or rights record."),
    },
    {
        "name": "Dual-Path Echo Net",
        "recorded_as": "separately unresolved AEC name in the same records",
        "paper_url": None,
        "substitutable": False,
        "reason": ("Also unresolved; the records state that no exact model by "
                   "this name, checkpoint or adapter exists locally."),
    },
)

SUBSTITUTION_PROBES = (
    "DeepAEC",
    "deepaec",
    "Deep AEC",
    "Deep-AEC",
    "DEEPAEC",
    " DeepAEC",
    "DeepAEC ",
    "DeepAEC (MSA-DPCRN)",
    "DeepAEC-v2",
    "Dual-Path Echo Net",
    "Deep Echo Path Modeling",
    "MSA-DPCRN",
    "DPCTNet",
    "",
)


def resolve_candidate_identity(name: object) -> Dict[str, Any]:
    """Exact, case-sensitive canonical-name resolution; never substitutes.

    The recorded row has no citation, DOI, repository or checkpoint identity,
    so even the exact recorded name resolves to ``identity_unresolved``. Near
    names and related papers are rejected as non-canonical.
    """
    if not isinstance(name, str) or name == "":
        raise ReferenceRejection("invalid_identity_name")
    if name != CANONICAL_RECORDED_NAME:
        raise ReferenceRejection("identity_name_not_canonical")
    raise ReferenceRejection("identity_unresolved_no_citation_no_checkpoint")


def identity_resolution_table() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for probe in SUBSTITUTION_PROBES:
        try:
            resolve_candidate_identity(probe)
            observed = "accepted"
        except ReferenceRejection as error:
            observed = error.code
        rows.append({
            "input": probe,
            "expected_code": ("invalid_identity_name" if probe == ""
                              else "identity_unresolved_no_citation_no_checkpoint"
                              if probe == CANONICAL_RECORDED_NAME
                              else "identity_name_not_canonical"),
            "observed_code": observed,
            "status": "rejected",
            "substitution_accepted": False,
            "qualifies": False,
        })
    return rows


# ---------------------------------------------------------------------------
# Caller-supplied future asset admission (never loaded or executed)
# ---------------------------------------------------------------------------

MANIFEST_FIELDS = {"schema_id", "cohort_id", "identity", "source", "weights",
                   "runtime", "render", "capture", "controls", "outcomes",
                   "rights"}
IDENTITY_FIELDS = {"canonical_name", "canonical_citation",
                   "canonical_paper_title", "canonical_repository",
                   "canonical_checkpoint_id", "identity_review_reference",
                   "substitute_of"}
SOURCE_FIELDS = {"revision", "archive_sha256", "license_id",
                  "license_review_reference"}
WEIGHTS_FIELDS = {"model_id", "revision", "sha256", "byte_count",
                  "model_card_present", "training_data_statement_present",
                  "license_id"}
RUNTIME_FIELDS = {"python", "framework", "framework_version", "device",
                  "intra_op_threads", "interop_op_threads",
                  "deterministic_algorithms", "offline", "lockfile_sha256"}
SIGNAL_FIELDS = {"path", "sha256", "sample_rate_hz", "channels", "samples",
                 "source", "rights_reference"}
CONTROL_KINDS = (
    "echo_only_case",
    "near_end_only_case",
    "double_talk_case",
    "no_render_reference_case",
    "delayed_render_case",
    "nonfinite_rejection_case",
)
OUTCOME_FIELDS = {"echo_return_loss_enhancement_millidb",
                  "near_end_preservation_millidb",
                  "alignment_error_samples", "nonfinite_output_count",
                  "sample_count", "double_talk_preservation_millidb"}
RIGHTS_FIELDS = {"dataset_terms_reference", "weights_terms_reference",
                 "output_use_reference", "review_reference",
                 "claims_qualified"}
MANIFEST_SCHEMA_ID = "audio-sdk/deepaec-room-cohort/0.1"


def _validate_signal(signal: object, label: str) -> None:
    _exact_keys(signal, SIGNAL_FIELDS, label)
    _absolute_path(signal["path"], label + "_path")
    _sha256(signal["sha256"], label + "_sha256")
    rate = _integer(signal["sample_rate_hz"], label + "_sample_rate_hz",
                    1, 384000)
    _require(rate == SAMPLE_RATE_HZ, "unsupported_sample_rate")
    channels = _integer(signal["channels"], label + "_channels", 1, 8)
    _require(channels == CHANNELS, "unsupported_channels")
    _integer(signal["samples"], label + "_samples", 1, 960000)
    _string(signal["source"], label + "_source", 1, 128)
    _string(signal["rights_reference"], label + "_rights_reference", 1, 128)


def _validate_controls(controls: object) -> None:
    _require(isinstance(controls, list), "invalid_controls")
    seen: List[str] = []
    for control in controls:
        _exact_keys(control, {"kind", "reference"}, "control")
        kind = _string(control["kind"], "control_kind", 1, 64)
        _string(control["reference"], "control_reference", 1, 128)
        if kind not in CONTROL_KINDS:
            raise ReferenceRejection("unknown_control_kind:" + kind)
        if kind in seen:
            raise ReferenceRejection("duplicate_control_kind:" + kind)
        seen.append(kind)
    for kind in CONTROL_KINDS:
        if kind not in seen:
            raise ReferenceRejection("missing_control_kind:" + kind)


def validate_future_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a future DeepAEC room cohort manifest; admit structure only."""
    _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    _require(manifest["schema_id"] == MANIFEST_SCHEMA_ID,
             "unexpected_manifest_schema")
    _string(manifest["cohort_id"], "cohort_id", 1, 64)

    identity = manifest["identity"]
    _exact_keys(identity, IDENTITY_FIELDS, "identity")
    name = _string(identity["canonical_name"], "canonical_name", 1, 64)
    if name != CANONICAL_RECORDED_NAME:
        raise ReferenceRejection("identity_substitution_attempt")
    citation = _string(identity["canonical_citation"], "canonical_citation",
                       1, 256)
    if "10." not in citation and "arxiv.org/abs/" not in citation:
        raise ReferenceRejection("missing_canonical_citation")
    _string(identity["canonical_paper_title"], "canonical_paper_title",
            4, 200)
    repository = _string(identity["canonical_repository"],
                         "canonical_repository", 1, 256)
    if not repository.startswith("https://"):
        raise ReferenceRejection("invalid_canonical_repository")
    _string(identity["canonical_checkpoint_id"], "canonical_checkpoint_id",
            4, 128)
    _string(identity["identity_review_reference"],
            "identity_review_reference", 1, 128)
    if identity["substitute_of"] is not None:
        raise ReferenceRejection("substitution_not_allowed")

    source = manifest["source"]
    _exact_keys(source, SOURCE_FIELDS, "source")
    _commit(source["revision"], "source_revision")
    _sha256(source["archive_sha256"], "source_archive_sha256")
    _string(source["license_id"], "source_license_id", 1, 64)
    _string(source["license_review_reference"],
            "source_license_review_reference", 1, 128)

    weights = manifest["weights"]
    _exact_keys(weights, WEIGHTS_FIELDS, "weights")
    _string(weights["model_id"], "weights_model_id", 1, 128)
    _commit(weights["revision"], "weights_revision")
    _sha256(weights["sha256"], "weights_sha256")
    _integer(weights["byte_count"], "weights_byte_count", 1, 1 << 40)
    if weights["model_card_present"] is not True:
        raise ReferenceRejection("model_card_absent")
    if weights["training_data_statement_present"] is not True:
        raise ReferenceRejection("training_data_statement_absent")
    _string(weights["license_id"], "weights_license_id", 1, 64)

    runtime = manifest["runtime"]
    _exact_keys(runtime, RUNTIME_FIELDS, "runtime")
    _string(runtime["python"], "runtime_python", 1, 16)
    _string(runtime["framework"], "runtime_framework", 1, 32)
    _string(runtime["framework_version"], "runtime_framework_version", 1, 32)
    _string(runtime["device"], "runtime_device", 1, 32)
    intra = _integer(runtime["intra_op_threads"], "runtime_intra_op_threads",
                     1, 64)
    inter = _integer(runtime["interop_op_threads"], "runtime_interop_op_threads",
                     1, 64)
    if intra != 1 or inter != 1:
        raise ReferenceRejection("nondeterministic_thread_count")
    if runtime["deterministic_algorithms"] is not True:
        raise ReferenceRejection("nondeterministic_algorithms")
    if runtime["offline"] is not True:
        raise ReferenceRejection("network_not_allowed")
    _sha256(runtime["lockfile_sha256"], "runtime_lockfile_sha256")

    _validate_signal(manifest["render"], "render")
    _validate_signal(manifest["capture"], "capture")
    render_samples = manifest["render"]["samples"]
    capture_samples = manifest["capture"]["samples"]
    if render_samples != capture_samples:
        raise ReferenceRejection("render_capture_length_mismatch")

    _validate_controls(manifest["controls"])

    outcomes = manifest["outcomes"]
    _exact_keys(outcomes, OUTCOME_FIELDS, "outcomes")
    _integer(outcomes["echo_return_loss_enhancement_millidb"],
             "outcome_echo_return_loss_enhancement_millidb", -100000, 120000)
    _integer(outcomes["near_end_preservation_millidb"],
             "outcome_near_end_preservation_millidb", -60000, 60000)
    _integer(outcomes["double_talk_preservation_millidb"],
             "outcome_double_talk_preservation_millidb", -60000, 60000)
    _integer(outcomes["alignment_error_samples"],
             "outcome_alignment_error_samples", 0, 16000)
    nonfinite = _integer(outcomes["nonfinite_output_count"],
                         "outcome_nonfinite_output_count", 0, 1)
    if nonfinite != 0:
        raise ReferenceRejection("nonfinite_output_reported")
    _integer(outcomes["sample_count"], "outcome_sample_count", 1, 960000)

    rights = manifest["rights"]
    _exact_keys(rights, RIGHTS_FIELDS, "rights")
    for field in ("dataset_terms_reference", "weights_terms_reference",
                  "output_use_reference", "review_reference"):
        _string(rights[field], "rights_" + field, 1, 128)
    if rights["claims_qualified"] is not False:
        raise ReferenceRejection("claims_qualified_not_allowed")

    return {"admitted": True, "loaded": False, "executed": False,
            "audio_read": False, "weights_read": False}


def _base_manifest() -> Dict[str, Any]:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "cohort_id": "synthetic-schema-control",
        "identity": {
            "canonical_name": "DeepAEC",
            "canonical_citation": "10.9999/synthetic-schema-control",
            "canonical_paper_title": "Synthetic Schema Control Not A Paper",
            "canonical_repository": "https://github.com/synthetic/schema-control",
            "canonical_checkpoint_id": "synthetic-schema-control",
            "identity_review_reference": "synthetic-schema-control",
            "substitute_of": None,
        },
        "source": {
            "revision": "0" * 40,
            "archive_sha256": "1" * 64,
            "license_id": "synthetic-control",
            "license_review_reference": "synthetic-schema-control",
        },
        "weights": {
            "model_id": "synthetic-schema-control",
            "revision": "2" * 40,
            "sha256": "3" * 64,
            "byte_count": 1,
            "model_card_present": True,
            "training_data_statement_present": True,
            "license_id": "synthetic-control",
        },
        "runtime": {
            "python": "3.12",
            "framework": "synthetic",
            "framework_version": "0.0.0",
            "device": "cpu",
            "intra_op_threads": 1,
            "interop_op_threads": 1,
            "deterministic_algorithms": True,
            "offline": True,
            "lockfile_sha256": "4" * 64,
        },
        "render": {
            "path": "/synthetic/render.raw",
            "sha256": "5" * 64,
            "sample_rate_hz": 16000,
            "channels": 1,
            "samples": 9600,
            "source": "synthetic-schema-control",
            "rights_reference": "synthetic-schema-control",
        },
        "capture": {
            "path": "/synthetic/capture.raw",
            "sha256": "6" * 64,
            "sample_rate_hz": 16000,
            "channels": 1,
            "samples": 9600,
            "source": "synthetic-schema-control",
            "rights_reference": "synthetic-schema-control",
        },
        "controls": [{"kind": kind, "reference": "synthetic-schema-control"}
                     for kind in CONTROL_KINDS],
        "outcomes": {
            "echo_return_loss_enhancement_millidb": 0,
            "near_end_preservation_millidb": 0,
            "double_talk_preservation_millidb": 0,
            "alignment_error_samples": 0,
            "nonfinite_output_count": 0,
            "sample_count": 9600,
        },
        "rights": {
            "dataset_terms_reference": "synthetic-schema-control",
            "weights_terms_reference": "synthetic-schema-control",
            "output_use_reference": "synthetic-schema-control",
            "review_reference": "synthetic-schema-control",
            "claims_qualified": False,
        },
    }


def admission_control() -> Dict[str, Any]:
    manifest = _base_manifest()
    result = validate_future_manifest(manifest)
    return {
        "control_id": "synthetic_schema_control_not_evidence",
        "manifest_digest": object_digest(manifest),
        "admitted": result["admitted"],
        "loaded": result["loaded"],
        "executed": result["executed"],
        "audio_read": result["audio_read"],
        "placeholder_values": True,
        "is_real_cohort": False,
        "qualifies": False,
        "note": ("A schema-only control with placeholder values proves the "
                 "validator is not blanket-rejecting. It is not a citation, "
                 "recording, weight, measurement or result."),
    }


# ---------------------------------------------------------------------------
# Adverse rejection matrix
# ---------------------------------------------------------------------------

def _expect_reject(action) -> str:
    try:
        action()
    except ReferenceRejection as error:
        return error.code
    except ValueError as error:
        return str(error)
    return "accepted"


def _manifest_with(**changes: Any) -> Dict[str, Any]:
    manifest = _base_manifest()
    manifest.update(changes)
    return manifest


def _manifest_nested(section: str, **changes: Any) -> Dict[str, Any]:
    manifest = _base_manifest()
    nested = dict(manifest[section])
    nested.update(changes)
    manifest[section] = nested
    return manifest


def adverse_rejections() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    def add(case_id: str, expected: str, action) -> None:
        observed = _expect_reject(action)
        cases.append({
            "case_id": case_id,
            "expected_code": expected,
            "observed_code": observed,
            "status": "rejected" if observed == expected else "mismatch",
            "state_unchanged": observed == expected,
        })

    add("duplicate_json_key", "duplicate_json_key:a",
        lambda: load_strict_json_text('{"a":1,"a":2}'))
    add("nan_json_constant", "nonfinite_json_constant:NaN",
        lambda: load_strict_json_text('{"a":NaN}'))
    add("infinity_json_constant", "nonfinite_json_constant:Infinity",
        lambda: load_strict_json_text('{"a":Infinity}'))
    add("malformed_json", "invalid_json",
        lambda: load_strict_json_text('{"a":'))
    add("array_json_root", "json_not_object",
        lambda: load_strict_json_text("[1,2]"))

    for probe in SUBSTITUTION_PROBES:
        expected = ("identity_unresolved_no_citation_no_checkpoint"
                    if probe == CANONICAL_RECORDED_NAME
                    else "identity_name_not_canonical")
        if probe == "":
            expected = "invalid_identity_name"
        add("identity_probe_" + (probe.strip() or "empty").replace(
            " ", "_").lower(),
            expected, lambda probe=probe: resolve_candidate_identity(probe))
    add("identity_bool", "invalid_identity_name",
        lambda: resolve_candidate_identity(True))

    manifest = _base_manifest()
    add("manifest_missing_field",
        "strict_keys_mismatch:manifest:identity",
        lambda: validate_future_manifest(
            {key: value for key, value in manifest.items()
             if key != "identity"}))
    add("manifest_extra_field", "strict_keys_mismatch:manifest:extra",
        lambda: validate_future_manifest({**manifest, "extra": 1}))
    add("manifest_wrong_schema", "unexpected_manifest_schema",
        lambda: validate_future_manifest(
            {**manifest, "schema_id": "audio-sdk/other/0.1"}))
    add("manifest_substitute_name", "identity_substitution_attempt",
        lambda: validate_future_manifest(
            _manifest_nested("identity", canonical_name="MSA-DPCRN")))
    add("manifest_missing_citation", "missing_canonical_citation",
        lambda: validate_future_manifest(
            _manifest_nested("identity", canonical_citation="pending")))
    add("manifest_relative_repository", "invalid_canonical_repository",
        lambda: validate_future_manifest(
            _manifest_nested("identity", canonical_repository="github.com/x")))
    add("manifest_substitute_of_set", "substitution_not_allowed",
        lambda: validate_future_manifest(
            _manifest_nested("identity", substitute_of="MSA-DPCRN")))
    add("manifest_bad_source_revision", "invalid_string:source_revision",
        lambda: validate_future_manifest(
            _manifest_nested("source", revision="not-a-revision")))
    add("manifest_bad_archive_sha", "invalid_sha256:source_archive_sha256",
        lambda: validate_future_manifest(
            _manifest_nested("source", archive_sha256="z" * 64)))
    add("manifest_empty_source_license", "invalid_string:source_license_id",
        lambda: validate_future_manifest(
            _manifest_nested("source", license_id="")))
    add("manifest_bad_weights_revision",
        "invalid_string:weights_revision",
        lambda: validate_future_manifest(
            _manifest_nested("weights", revision="3" * 39)))
    add("manifest_negative_byte_count", "invalid_integer:weights_byte_count",
        lambda: validate_future_manifest(
            _manifest_nested("weights", byte_count=-1)))
    add("manifest_model_card_absent", "model_card_absent",
        lambda: validate_future_manifest(
            _manifest_nested("weights", model_card_present=False)))
    add("manifest_training_terms_absent",
        "training_data_statement_absent",
        lambda: validate_future_manifest(
            _manifest_nested("weights",
                             training_data_statement_present=False)))
    add("manifest_two_threads", "nondeterministic_thread_count",
        lambda: validate_future_manifest(
            _manifest_nested("runtime", intra_op_threads=2)))
    add("manifest_nondeterministic", "nondeterministic_algorithms",
        lambda: validate_future_manifest(
            _manifest_nested("runtime", deterministic_algorithms=False)))
    add("manifest_online", "network_not_allowed",
        lambda: validate_future_manifest(
            _manifest_nested("runtime", offline=False)))
    add("manifest_bad_lockfile", "invalid_sha256:runtime_lockfile_sha256",
        lambda: validate_future_manifest(
            _manifest_nested("runtime", lockfile_sha256="9" * 63 + "z")))
    add("manifest_render_relative_path", "invalid_source_path:render_path",
        lambda: validate_future_manifest(
            _manifest_nested("render", path="render.raw")))
    add("manifest_render_bad_sha", "invalid_sha256:render_sha256",
        lambda: validate_future_manifest(
            _manifest_nested("render", sha256="g" * 64)))
    add("manifest_render_wrong_rate", "unsupported_sample_rate",
        lambda: validate_future_manifest(
            _manifest_nested("render", sample_rate_hz=8000)))
    add("manifest_render_stereo", "unsupported_channels",
        lambda: validate_future_manifest(
            _manifest_nested("render", channels=2)))
    add("manifest_render_zero_samples", "invalid_integer:render_samples",
        lambda: validate_future_manifest(
            _manifest_nested("render", samples=0)))
    add("manifest_length_mismatch", "render_capture_length_mismatch",
        lambda: validate_future_manifest(
            _manifest_nested("capture", samples=9601)))
    add("manifest_missing_control", "missing_control_kind:double_talk_case",
        lambda: validate_future_manifest(
            _manifest_with(controls=[
                {"kind": kind, "reference": "synthetic-schema-control"}
                for kind in CONTROL_KINDS if kind != "double_talk_case"])))
    add("manifest_duplicate_control",
        "duplicate_control_kind:near_end_only_case",
        lambda: validate_future_manifest(
            _manifest_with(controls=[
                {"kind": kind, "reference": "synthetic-schema-control"}
                for kind in CONTROL_KINDS]
                + [{"kind": "near_end_only_case",
                    "reference": "synthetic-schema-control"}])))
    add("manifest_unknown_control", "unknown_control_kind:magic_case",
        lambda: validate_future_manifest(
            _manifest_with(controls=[
                {"kind": kind, "reference": "synthetic-schema-control"}
                for kind in CONTROL_KINDS]
                + [{"kind": "magic_case",
                    "reference": "synthetic-schema-control"}])))
    add("manifest_nonfinite_outcome",
        "invalid_integer:outcome_echo_return_loss_enhancement_millidb",
        lambda: validate_future_manifest(
            _manifest_nested("outcomes",
                             echo_return_loss_enhancement_millidb=float("nan"))))
    add("manifest_outcome_out_of_range",
        "invalid_integer:outcome_near_end_preservation_millidb",
        lambda: validate_future_manifest(
            _manifest_nested("outcomes", near_end_preservation_millidb=99999)))
    add("manifest_nonfinite_output_reported",
        "nonfinite_output_reported",
        lambda: validate_future_manifest(
            _manifest_nested("outcomes", nonfinite_output_count=1)))
    add("manifest_claims_qualified", "claims_qualified_not_allowed",
        lambda: validate_future_manifest(
            _manifest_nested("rights", claims_qualified=True)))
    add("manifest_missing_rights_reference",
        "invalid_string:rights_review_reference",
        lambda: validate_future_manifest(
            _manifest_nested("rights", review_reference="")))

    room = build_room_fixture()
    add("room_missing_render", "missing_input:render",
        lambda: prepare_room_case(None, room["capture"]))
    add("room_missing_capture", "missing_input:capture",
        lambda: prepare_room_case(room["render"], None))
    add("room_length_mismatch", "signal_length_mismatch:capture",
        lambda: prepare_room_case(room["render"], room["capture"][:-1]))
    add("room_empty", "invalid_signal_length:render",
        lambda: prepare_room_case([], []))
    add("room_nonfinite_nan", "nonfinite_input:render",
        lambda: prepare_room_case([float("nan")] + room["render"][1:],
                                  room["capture"]))
    add("room_nonfinite_inf", "nonfinite_input:capture",
        lambda: prepare_room_case(room["render"],
                                  [float("inf")] + room["capture"][1:]))
    add("room_out_of_range", "sample_out_of_range:render",
        lambda: prepare_room_case([1.5] + room["render"][1:],
                                  room["capture"]))
    add("room_string_sample", "invalid_sample:capture",
        lambda: prepare_room_case(room["render"],
                                  ["x"] + room["capture"][1:]))
    add("room_bool_sample", "invalid_sample:capture",
        lambda: prepare_room_case(room["render"],
                                  [True] + room["capture"][1:]))
    add("room_zero_lag", "invalid_integer:max_lag_samples",
        lambda: prepare_room_case(room["render"], room["capture"],
                                  max_lag_samples=0))
    add("room_zero_render", "no_render_reference",
        lambda: estimate_render_delay([0] * ROOM_LENGTH, room["capture"],
                                      MAX_LAG_SAMPLES,
                                      DELAY_ESTIMATE_REGION[0],
                                      DELAY_ESTIMATE_REGION[1]))
    add("room_zero_capture", "no_capture_signal",
        lambda: estimate_render_delay(room["render"], [0] * ROOM_LENGTH,
                                      MAX_LAG_SAMPLES,
                                      DELAY_ESTIMATE_REGION[0],
                                      DELAY_ESTIMATE_REGION[1]))

    return cases


# ---------------------------------------------------------------------------
# Provenance, pins and board identity
# ---------------------------------------------------------------------------

def recipe_provenance() -> List[Dict[str, Any]]:
    """Quote-check the pinned notes; provenance only, not qualification."""
    rows: List[Dict[str, Any]] = []
    for path, phrase in PROVENANCE_PHRASES:
        text = (SOURCE_ROOT / path).read_text(encoding="utf-8")
        rows.append({"path": path, "phrase": phrase,
                     "present": phrase in text})
    return rows


def _verify_pins() -> None:
    for path, expected in SOURCE_PINS.items():
        full = SOURCE_ROOT / path
        _require(full.is_file(), "missing_source_pin:" + path)
        _require(file_digest(full) == expected, "stale_source_pin:" + path)
    for path, expected in BOUNDARY_PINS.items():
        full = SDK_ROOT / path
        _require(full.is_file(), "missing_boundary_pin:" + path)
        _require(file_digest(full) == expected, "stale_boundary_pin:" + path)
    _require(all(row["present"] for row in recipe_provenance()),
             "stale_provenance_phrase")


def _projection(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "repository": row["repository"],
        "mode": row["mode"],
        "depends_on": row["depends_on"],
        "component": row.get("component"),
    }


def board_row() -> Dict[str, Any]:
    """Read only stable linked-row identity; never hash the full board."""
    payload = load_strict_json(SOURCE_ROOT / TASK_BOARD)
    _require(isinstance(payload.get("tasks"), list), "invalid_task_board")
    rows = {row["id"]: row for row in payload["tasks"]
            if isinstance(row, dict) and "id" in row}
    _require(TASK_ID in rows, "task_row_missing")
    # Transitive dependency closure over stable fields only.
    seen: List[str] = []
    stack = [TASK_ID]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        _require(current in rows, "missing_linked_row:" + current)
        seen.append(current)
        for dependency in rows[current]["depends_on"]:
            if dependency not in seen:
                stack.append(dependency)
    linked = [_projection(rows[row_id]) for row_id in sorted(seen)]
    stable_fields = linked[0]
    stable_digest = object_digest(stable_fields)
    linked_digest = object_digest(linked)
    _require(stable_digest == BOARD_ROW_STABLE_SHA256,
             "unexpected_stable_board_identity")
    _require(linked_digest == BOARD_LINKED_ROWS_SHA256,
             "unexpected_linked_row_identity")
    return {
        "stable_fields": stable_fields,
        "stable_sha256": stable_digest,
        "linked_rows": linked,
        "linked_rows_sha256": linked_digest,
        "projected_fields": ["id", "title", "component", "mode", "repository",
                             "depends_on"],
        "linked_row_identity_only": True,
        "full_tasks_json_hashed": False,
        "mutable_board_fields_gate": False,
        "note": ("Only the stable linked-row projection is read and gated. "
                 "The mutable full plan/swarm/TASKS.json is never hashed, "
                 "pinned or used as a digest source."),
    }


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def _acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "render_and_reference_geometry_frozen": {
                "status": "synthetic_only",
                "evidence": ("Frozen synthetic 16 kHz mono render/capture "
                             "geometry with an authored integer path "
                             "(480-sample delay, three taps); no recorded "
                             "RIR, measured room or movement model."),
            },
            "echo_only_case": {
                "status": "synthetic_only",
                "evidence": ("Synthetic echo-only region with exact integer "
                             "oracle ERLE arithmetic; no candidate output."),
            },
            "near_end_only_case": {
                "status": "synthetic_only",
                "evidence": ("Synthetic near-end-only region with exact "
                             "integer oracle SNR arithmetic; no candidate "
                             "output."),
            },
            "overlap_double_talk_case": {
                "status": "synthetic_only",
                "evidence": ("Synthetic double-talk region with separate "
                             "echo and near-end accounting; no listening."),
            },
            "no_reference_case": {
                "status": "synthetic_only",
                "evidence": ("All-zero render reference is rejected with "
                             "no_render_reference; no value is guessed."),
            },
            "delayed_render_case": {
                "status": "synthetic_only",
                "evidence": ("Render path delayed by 320 samples; the exact "
                             "integer estimator recovers the shifted lag."),
            },
            "echo_attenuation": {
                "status": "blocked",
                "evidence": ("Only a synthetic oracle bound exists; no "
                             "DeepAEC candidate output was produced."),
            },
            "near_end_damage": {
                "status": "blocked",
                "evidence": ("Only synthetic oracle near-end SNR exists; no "
                             "candidate near-end damage was measured."),
            },
            "nonfinite_failures": {
                "status": "synthetic_only",
                "evidence": ("Nonfinite and invalid inputs are rejected by "
                             "the harness; candidate output is absent."),
            },
            "alignment_content_delay": {
                "status": "blocked",
                "evidence": ("No candidate content delay or runtime "
                             "alignment was measured."),
            },
            "reset_schedule_and_state": {
                "status": "synthetic_only",
                "evidence": ("The harness is a pure function with a declared "
                             "reset schedule; no candidate state exists."),
            },
            "rights_cleared_room_qualification": {
                "status": "blocked",
                "evidence": ("No rights-cleared paired render/capture "
                             "corpus, independent scorer or baseline."),
            },
            "no_reference_suppressor_comparison": {
                "status": "blocked",
                "evidence": ("No no-reference suppressor candidate, "
                             "independent comparison or measurement exists."),
            },
            "device_timing_resources": {
                "status": "blocked",
                "evidence": ("No runtime, device clock, deadline or resource "
                             "measurement exists."),
            },
        },
    }


def _profile_blockers(profile: Dict[str, Any]) -> List[str]:
    return sorted(name for name, item in profile["required_items"].items()
                  if item["status"] == "blocked")


def _required_artifacts() -> List[Dict[str, Any]]:
    return [
        {
            "id": "ART-01",
            "kind": "pinned_candidate_records",
            "present": True,
            "verified": True,
            "blocked": False,
            "requirement": ("The exact pinned candidate matrix, transform-space, "
                            "blocked-reaudit and findings notes plus the "
                            "inventory row and Room profile that record the "
                            "unresolved DeepAEC identity."),
        },
        {
            "id": "ART-02",
            "kind": "canonical_identity_and_citation",
            "present": False,
            "verified": False,
            "blocked": True,
            "requirement": ("One exact canonical DeepAEC paper title, citation "
                            "with DOI or arXiv identifier, authors, official "
                            "repository and checkpoint identity with an "
                            "independent provenance review."),
        },
        {
            "id": "ART-03",
            "kind": "source_and_code_license",
            "present": False,
            "verified": False,
            "blocked": True,
            "requirement": ("The exact source revision (40-hex commit), "
                            "package/archive digest and the complete code "
                            "license and notice bundle."),
        },
        {
            "id": "ART-04",
            "kind": "weights_model_card_and_training_terms",
            "present": False,
            "verified": False,
            "blocked": True,
            "requirement": ("The exact weight identity, revision, byte count "
                            "and SHA-256, model card, training-data statement "
                            "and reviewed weight terms."),
        },
        {
            "id": "ART-05",
            "kind": "pinned_offline_runtime",
            "present": False,
            "verified": False,
            "blocked": True,
            "requirement": ("A locked offline runtime with exact package "
                            "hashes, install/import digests, one thread per "
                            "pool, deterministic settings and no network."),
        },
        {
            "id": "ART-06",
            "kind": "rights_cleared_room_corpus_and_scorer",
            "present": False,
            "verified": False,
            "blocked": True,
            "requirement": ("Rights-cleared paired render/capture recordings "
                            "or measured RIRs with channel/rate/hop, "
                            "excitation, delay, movement, noise and reset "
                            "schedule, plus an independent pinned scorer."),
        },
        {
            "id": "ART-07",
            "kind": "room_results_and_opt_in_intake",
            "present": False,
            "verified": False,
            "blocked": True,
            "requirement": ("Reproduced Room-profile results with controls, "
                            "target timing and resources, and a separate "
                            "versioned OFF-by-default provider/tool intake "
                            "with independent exact-head review."),
        },
    ]


def _release_gates() -> List[Dict[str, str]]:
    rows = [
        ("RG-01", "canonical_identity_and_citation",
         "Resolve one exact canonical DeepAEC paper, citation/DOI, repository "
         "and checkpoint identity with an independent provenance review; "
         "related papers remain distinct candidates."),
        ("RG-02", "source_revision_and_code_license",
         "Pin the exact source revision and package digest, stage the complete "
         "license/notice bundle and record an independent terms review."),
        ("RG-03", "weights_model_card_and_training_terms",
         "Supply the exact weight identity, revision, byte count and SHA-256, "
         "model card, training-data statement and reviewed weight terms."),
        ("RG-04", "pinned_runtime_and_offline_load",
         "Provide a locked offline runtime with exact package hashes, import "
         "digests, one thread per pool, deterministic settings and a "
         "clean-room offline load."),
        ("RG-05", "rights_cleared_paired_room_corpus_and_scorer",
         "Freeze rights-cleared paired render/capture recordings or measured "
         "RIRs with geometry, delay, movement, noise and reset schedule plus "
         "an independent pinned scorer."),
        ("RG-06", "room_profile_qualification_with_controls",
         "Reproduce echo attenuation, near-end damage, alignment including "
         "delayed and missing render, double-talk, nonfinite behavior and a "
         "matched baseline on the qualified cohort."),
        ("RG-07", "target_timing_resources_and_deadlines",
         "Measure paced p50/p95/p99 latency, CPU/memory/energy, fill/flush "
         "and deadline behavior at the exact runtime on the intended device."),
        ("RG-08", "provider_intake_public_surface_and_release",
         "Open a separate versioned OFF-by-default opt-in intake with an exact "
         "descriptor/config, clean-install proof and independent exact-head "
         "review."),
    ]
    return [{"id": gate, "title": title, "requirement": text,
             "status": "blocked"} for gate, title, text in rows]


def _exact_blockers() -> List[Dict[str, str]]:
    return [
        {
            "id": "BLK-01",
            "linked_gates": ["RG-01"],
            "status": "open",
            "qualifies": False,
            "statement": ("The canonical identity is unresolved. The pinned "
                          "records name only 'DeepAEC' and state: 'Exact "
                          "canonical name/citation/checkpoint unresolved; no "
                          "substitute used'. No canonical paper title, DOI, "
                          "arXiv identifier, repository, author list or "
                          "checkpoint ID exists, and no local or primary-"
                          "source match was found."),
            "required_action": ("Supply the exact canonical paper citation "
                                "(DOI or arXiv identifier), title, authors, "
                                "official repository and checkpoint identity "
                                "with an independent provenance review. Named "
                                "nearby papers are separate candidates."),
        },
        {
            "id": "BLK-02",
            "linked_gates": ["RG-02"],
            "status": "open",
            "qualifies": False,
            "statement": ("No DeepAEC source checkout, archive, source "
                          "revision, code license or notice bundle exists. "
                          "Because the identity is unresolved, no source can "
                          "be attributed or pinned."),
            "required_action": ("After the identity resolves, stage the exact "
                                "source revision and package/archive digest, "
                                "complete license and notice text and an "
                                "independent terms review."),
        },
        {
            "id": "BLK-03",
            "linked_gates": ["RG-03"],
            "status": "open",
            "qualifies": False,
            "statement": ("No DeepAEC weight or checkpoint is present or "
                          "identified: no model ID, revision, byte count, "
                          "SHA-256, model card or training-data statement. "
                          "The pinned AEC note records only that DeepAEC does "
                          "not map cleanly to a specific checkpoint."),
            "required_action": ("Supply the exact weight identity, revision, "
                                "byte count and SHA-256, model card, "
                                "training-data statement and reviewed weight "
                                "terms."),
        },
        {
            "id": "BLK-04",
            "linked_gates": ["RG-04"],
            "status": "open",
            "qualifies": False,
            "statement": ("No pinned runtime or offline load exists. The "
                          "fixed candidate checkout, model, environment and "
                          "adapter probes are absent, and no lockfile, wheel "
                          "digest, import digest or deterministic thread "
                          "trace exists. No DeepAEC framework was imported."),
            "required_action": ("Provide a locked offline runtime with exact "
                                "package hashes, install/import digests, one "
                                "thread per pool, deterministic settings and "
                                "a clean-room offline load trace."),
        },
        {
            "id": "BLK-05",
            "linked_gates": ["RG-05", "RG-06"],
            "status": "open",
            "qualifies": False,
            "statement": ("No rights-cleared paired render/capture room "
                          "corpus, measured RIR set, independent scorer, "
                          "listening result or task-matched baseline exists. "
                          "The local AEC pilots use synthetic or "
                          "non-redistributable pilot audio and are different "
                          "candidates; their numbers are not reused here."),
            "required_action": ("Freeze a rights-cleared paired "
                                "render/capture cohort or measured RIRs with "
                                "channel/rate/hop, excitation, delay, "
                                "movement, noise and reset schedule, plus an "
                                "independent pinned scorer and baseline."),
        },
        {
            "id": "BLK-06",
            "linked_gates": ["RG-07", "RG-08"],
            "status": "open",
            "qualifies": False,
            "statement": ("No DeepAEC room-profile result, no-reference "
                          "suppressor comparison, target-device timing, "
                          "provider intake or release decision exists. Only "
                          "synthetic oracle arithmetic is present, and it "
                          "cannot qualify any candidate."),
            "required_action": ("After identity/source/weights/runtime/rights "
                                "clear, reproduce all Room cases with "
                                "controls, measure target timing and resources, "
                                "and open a separate OFF-by-default intake "
                                "with independent exact-head review."),
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
        "output_use_reviewed": False,
        "review_status": "blocked",
        "note": ("No upstream identity, license text, weight terms or "
                 "training-data statement exists; nothing can be attributed "
                 "or cleared."),
    }


def _external_artifacts() -> Dict[str, Any]:
    workspace_paths = {
        "source_checkout_upper": "data/checkouts/DeepAEC",
        "source_checkout_lower": "data/checkouts/deepaec",
        "weights_upper": "data/models/DeepAEC",
        "weights_lower": "data/models/deepaec",
        "runtime_env_upper": "data/envs/DeepAEC",
        "runtime_env_lower": "data/envs/deepaec",
        "adapter_upper": "adapters/DeepAEC",
        "adapter_lower": "adapters/deepaec",
        "caller_manifest": "data/manifests/deepaec.json",
        "room_corpus": "data/datasets/deepaec-room",
    }
    external_paths = {
        "huggingface_cache_upper": (
            "~/.cache/huggingface/hub/models--DeepAEC"),
        "huggingface_cache_lower": (
            "~/.cache/huggingface/hub/models--deepaec"),
        "torch_hub_cache": "~/.cache/torch/hub/checkpoints/DeepAEC",
        "pip_cache": "~/.cache/pip/deepaec",
    }
    present = {}
    for key, path in workspace_paths.items():
        present[key] = (SOURCE_ROOT / path).exists()
    for key, path in external_paths.items():
        present[key] = Path(path).expanduser().exists()
    return {
        "checked_paths": {**workspace_paths, **external_paths},
        "present": present,
        "present_count": sum(1 for value in present.values() if value),
        "any_present": any(present.values()),
        "recursive_walk": False,
        "status": "blocked",
        "note": ("Fixed probes only, no recursive workspace walk. Presence "
                 "would not be identity, runtime admission, parity or rights "
                 "evidence."),
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
        "real_render_capture_audio": False,
        "measured_rir": False,
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
    "No DeepAEC paper identity, source, weight, checkpoint, runtime, adapter "
    "or numeric output was produced, downloaded, loaded or executed.",
    "The canonical DeepAEC identity is unresolved; no nearby paper is treated "
    "as the same candidate.",
    "No AEC, ERLE, near-end, double-talk, alignment, benchmark, listening or "
    "release result is claimed.",
    "The synthetic integer oracle arithmetic is a task-local measurement "
    "control, not DeepAEC output, and cannot qualify the candidate.",
    "No DeepAEC input rate, hop, frame, channel layout, lookahead, content "
    "delay, architecture or quantization scheme is asserted.",
    "No real render/capture recording, RIR, corpus, device clock or listener "
    "was used.",
    "No upstream license text, attribution bundle, weight terms or "
    "training-data statement is staged.",
    "No provider, descriptor, registry, installed v0 path, shared build, "
    "dependency lock or CI was changed.",
)

REOPEN_CONDITION = (
    "Resolve one exact canonical DeepAEC paper/citation/repository/checkpoint "
    "identity and pin the exact source revision with its complete license and "
    "notice bundle; supply the exact weights, model card and training-data "
    "terms plus a pinned offline runtime; freeze a rights-cleared paired "
    "render/capture or measured-RIR room cohort with an independent scorer and "
    "baseline and reproduce echo-only, near-end-only, double-talk, "
    "delayed-render, missing-render and nonfinite cases with near-end "
    "preservation and alignment; measure target-device timing and resources; "
    "then open a separate versioned OFF-by-default intake with independent "
    "exact-head review. Until then the candidate stays DEFER, incomplete and "
    "not qualified."
)


def _room_digest(result: Dict[str, Any]) -> str:
    return object_digest({
        "signals": result["signal_digests"],
        "cases": [(case["name"],
                   case.get("echo_return_loss_enhancement_millidb"),
                   case.get("near_end_snr_millidb"))
                  for case in result["cases"]],
        "delay": (result["delay_estimation"]["nominal"]["lag_samples"],
                  result["delay_estimation"]["delayed_render"]["lag_samples"],
                  result["delay_estimation"]["missing_render"]["observed_code"]),
    })


def build_report() -> Dict[str, Any]:
    """Build the canonical deterministic report. No files are written."""
    _verify_pins()
    room = room_case_results()
    profile = _acceptance_profile()
    adverse = adverse_rejections()
    gates = _release_gates()
    blockers = _exact_blockers()
    licensing = _licensing()
    external = _external_artifacts()
    identity_rows = identity_resolution_table()
    admission = admission_control()
    room_digest = _room_digest(room)
    provenance = recipe_provenance()

    nonfinite_rejections = sum(
        1 for case in adverse
        if case["observed_code"].startswith("nonfinite_input"))
    substitution_rejected = sum(
        1 for row in identity_rows
        if row["observed_code"] == row["expected_code"])

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
        "candidate_identity": {
            "recorded_name": CANONICAL_RECORDED_NAME,
            "recorded_status": RECORDED_STATUS,
            "recorded_finding": RECORDED_FINDING,
            "canonical_citation": None,
            "canonical_doi": None,
            "canonical_arxiv_id": None,
            "canonical_repository": None,
            "canonical_checkpoint_id": None,
            "canonical_paper_title": None,
            "identity_resolved": False,
            "exact_canonical_match_count": 0,
            "resolver": {
                "exact_case_sensitive": True,
                "fuzzy_matching": False,
                "alias_merge": False,
                "near_name_substitution": False,
            },
            "substitution_probes": identity_rows,
            "substitution_probes_rejected": substitution_rejected,
            "substitution_probes_total": len(identity_rows),
            "all_substitutions_rejected": (
                substitution_rejected == len(identity_rows)),
            "related_but_distinct": [dict(row) for row in RELATED_BUT_DISTINCT],
            "status": "unresolved",
            "qualifies": False,
        },
        "reference_status": {
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "implementation_present": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "checkpoint_identity_verified": False,
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
            "candidate_reported_channels": None,
            "candidate_reported_lookahead_samples": None,
            "candidate_geometry_documented": False,
            "resampling": "none",
            "model_asset_in_installed_v0": False,
            "harness_content_delay_samples": 0,
        },
        "room_harness": {
            "synthetic_only": True,
            "audio_generated": False,
            "geometry": room_geometry(),
            "regions": [dict(region) for region in REGIONS],
            "signal_digests": room["signal_digests"],
            "cases": room["cases"],
            "delay_estimation": room["delay_estimation"],
            "oracle_scope": (
                "Exact integer arithmetic on an authored synthetic echo path "
                "with the known echo component removed; an oracle bound, not "
                "a DeepAEC or any-other-candidate result."),
            "case_matrix_digest": room_digest,
            "qualifies": False,
        },
        "baseline": {
            "status": "blocked",
            "baseline_id": None,
            "reason": ("No established task-matched baseline is pinned, "
                       "licensed or run; sibling AEC evidence is not "
                       "imported or pooled."),
            "qualifies": False,
        },
        "listening": {
            "status": "not_run",
            "authorized": False,
            "result": None,
            "qualifies": False,
        },
        "runtime_timing": {
            "status": "blocked_unmeasured",
            "content_delay_samples": None,
            "availability_modeled": False,
            "wall_clock_measured": False,
            "real_time_factor": None,
            "deadline_ns": None,
            "resource_measurement": False,
            "qualifies": False,
        },
        "state_and_memory": {
            "status": "synthetic_pure_function_only",
            "candidate_state_bytes": None,
            "harness_state_bytes": 0,
            "reset_schedule": "recompute_from_frozen_inputs",
            "memory_measured": False,
            "qualifies": False,
        },
        "nonfinite": {
            "rejected_nonfinite_inputs": nonfinite_rejections,
            "candidate_output_nonfinite_count": None,
            "candidate_output_finite": False,
            "qualifies": False,
        },
        "admission_control": admission,
        "adverse_rejections": adverse,
        "adverse_all_rejected": all(
            row["status"] == "rejected" and row["state_unchanged"] is True
            for row in adverse),
        "external_artifacts": external,
        "licensing": licensing,
        "provenance": {
            "phrases": provenance,
            "all_present": all(row["present"] for row in provenance),
            "is_qualification": False,
        },
        "caller_asset": {
            "contract_id": MANIFEST_SCHEMA_ID,
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "manifest_present": False,
            "workspace_manifest": "data/manifests/deepaec.json",
            "present_behavior": ("validate_identity_geometry_only; do not "
                                 "load_or_execute"),
            "absent_behavior": "reject_before_processing",
            "required_fields": sorted(MANIFEST_FIELDS),
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
            "canonical_identity_resolved": False,
            "exact_source_present": False,
            "exact_weights_present": False,
            "exact_runtime_outputs_present": False,
            "checkpoint_identity_verified": False,
            "rights_cleared_room_cohort": False,
            "geometry_and_delay_documented": False,
            "echo_attenuation_qualified": False,
            "near_end_damage_qualified": False,
            "alignment_qualified": False,
            "double_talk_qualified": False,
            "no_reference_comparison": False,
            "baseline_qualified": False,
            "nonfinite_output_qualified": False,
            "timing_measured": False,
            "memory_measured": False,
            "listening": False,
            "real_corpus_used": False,
            "reason": ("Canonical identity, exact source/weights/runtime, "
                       "rights-cleared room data, independent scorer, "
                       "baseline, listening, target timing and intake are all "
                       "absent. Synthetic oracle arithmetic cannot qualify."),
        },
        "exact_blockers": blockers,
        "required_artifacts": _required_artifacts(),
        "release_gates": gates,
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": list(NEGATIVE_CLAIMS),
        "surrogate": {
            "algorithm": ("exact integer delay-estimation, ERLE and SNR "
                          "arithmetic on a frozen synthetic room path with "
                          "the known echo component treated as an oracle; no "
                          "canceller, filter, network or weight"),
            "is_deepaec": False,
            "is_learned": False,
            "is_echo_canceller": False,
            "uses_network": False,
            "uses_weight_file": False,
            "uses_float_arithmetic_in_signal_path": False,
            "qualifies_candidate": False,
        },
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "case_matrix_digests": [room_digest, room_digest, room_digest],
        },
        "scope_note": ("Only docs/task-evidence/deepaec/ is written; all "
                       "other paths are read-only pins."),
    }
    return report


# ---------------------------------------------------------------------------
# Contract and source pin manifest
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
        "candidate_identity": report["candidate_identity"],
        "reference_status": report["reference_status"],
        "format": report["format"],
        "licensing": report["licensing"],
        "artifact_pins": artifact_pins(report_digest, sidecar_digest),
        "board_row": report["board_row"],
        "boundary": report["boundary"],
        "boundary_pins": report["boundary_pins"],
        "source_pins": report["source_pins"],
        "scope": report["scope"],
        "exact_blockers": report["exact_blockers"],
        "required_artifacts": report["required_artifacts"],
        "release_gates": report["release_gates"],
        "reopen_condition": REOPEN_CONDITION,
        "negative_claims": report["negative_claims"],
        "admission_schema": {
            "schema_id": MANIFEST_SCHEMA_ID,
            "admission_only": True,
            "manifest_fields": sorted(MANIFEST_FIELDS),
            "identity_fields": sorted(IDENTITY_FIELDS),
            "source_fields": sorted(SOURCE_FIELDS),
            "weights_fields": sorted(WEIGHTS_FIELDS),
            "runtime_fields": sorted(RUNTIME_FIELDS),
            "signal_fields": sorted(SIGNAL_FIELDS),
            "control_kinds": list(CONTROL_KINDS),
            "outcome_fields": sorted(OUTCOME_FIELDS),
            "rights_fields": sorted(RIGHTS_FIELDS),
            "canonical_name_required": CANONICAL_RECORDED_NAME,
            "max_signal_samples": 960000,
            "qualifies": False,
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "the canonical identity is unresolved and no near name or related "
            "paper is substituted",
            "no DeepAEC source, weight, network layer, runtime or adapter is "
            "downloaded, copied, loaded or executed",
            "the synthetic integer oracle arithmetic is not DeepAEC and "
            "cannot qualify the candidate",
            "no candidate input rate, hop, frame, channel layout, lookahead or "
            "content delay is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def sources_bytes(overrides: Dict[str, bytes] | None = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-DEEPAEC; source: paths are "
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
    "ReferenceRejection", "admission_control", "adverse_rejections",
    "artifact_pins", "board_row", "build_contract", "build_report",
    "build_room_fixture", "canonical_report", "canonical_text",
    "erle_millidb", "estimate_render_delay", "file_digest",
    "identity_resolution_table", "int_signal_digest", "load_strict_json",
    "load_strict_json_text", "object_digest", "prepare_room_case", "quantize",
    "recipe_provenance", "resolve_candidate_identity", "room_case_results",
    "room_geometry", "sha256_bytes", "snr_millidb", "sources_bytes",
    "validate_future_manifest",
]
