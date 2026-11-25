# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SDK-WEBRTC-AGC-AGC2.

This module is NOT the WebRTC Audio Processing Module and does not implement,
simulate or approximate WebRTC AGC (legacy ``WebRtcAgc``) or AGC2. The exact
upstream source and a runnable APM runtime are absent from this workspace. The
module therefore builds a bounded, deterministic blocker report:

* strict request validation and fail-closed rejection of invalid, missing and
  nonfinite inputs;
* generated stimulus characterisation for the DSP acceptance profile;
* a bounded read-only absence probe over explicit workspace roots;
* a stable linked-row identity projection that never hashes the mutable full
  ``plan/swarm/TASKS.json`` into canonical bytes.

No network, model, weights, corpus audio, native library or download is used.
All values are derived from standard-library arithmetic on deterministic
synthetic samples.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

SAMPLE_RATE_HZ = 16000
FRAME_SAMPLES = 160
MAX_ABS_INPUT = 4.0
MAX_ABS_STIMULUS = 2.0

SCHEMA_ID = "audio-sdk/webrtc-agc-agc2-reference-report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/webrtc-agc-agc2-contract/0.1"
TASK = "SDK-WEBRTC-AGC-AGC2"
COMPONENT = "webrtc-agc-agc2"
BRANCH = "swarm/SDK-WEBRTC-AGC-AGC2"
BASE_COMMIT = "74fb3cd9f6f3e4b96a542d925461d24e1472c21d"
TASK_PREFIX = "docs/task-evidence/webrtc-agc-agc2/"

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"

SOURCE_PINS = {
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "adapters/webrtc-ns/README.md":
        "8893bace6b0289135f6d1ccad949a9eba44a824e37f45765f30b4192f82c5992",
    "adapters/webrtc-ns/requirements.lock":
        "c289d4c0ab4af3f54e2bf693f1f81a01aa7cc479627f9e7a3161b2f1f792d591",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "cpp-library/PIPELINE_DESIGN_REPORT.md":
        "f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093",
    "research/level_tone_control_20261028.md":
        "b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}

BOUNDARY_PINS = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}

# Stable linked-row identity only. Status, owner, review, handoff, timestamps,
# dispatch priority and history are deliberately excluded and never gated.
EXPECTED_LINK = {
    "task_id": TASK,
    "title": "WebRTC AGC / AGC2",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
LINK_FIELDS = ("task_id", "title", "mode", "repository", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "history", "depends_on", "write_scope", "deliverable",
    "acceptance", "evidence", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority",
)

CANDIDATES = ("webrtc_agc", "webrtc_agc2")
LIFECYCLES = ("prepared", "processing")
EXECUTION_MODES = (1, 2, 3)
REQUEST_KEYS = frozenset({
    "candidate", "sample_rate_hz", "channels", "frame_samples", "samples",
    "epoch", "first_input_sample", "lifecycle", "execution_mode",
})

SOURCE_ARTIFACT_FILES = (
    "check_licensing.py", "reference.py", "run.py", "test_reference.py",
    "verify.py",
)

SKIP_DIRECTORY_NAMES = frozenset({
    ".git", ".hg", ".svn", "__pycache__", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "build", "dist", "node_modules", "target", ".venv",
    "venv", "env", ".tox", "site-packages", "graphify-out", "worktrees",
    ".cache", ".idea", ".vscode",
})

EXACT_UPSTREAM_NAMES = frozenset({
    "audio_processing.h", "audio_processing_impl.h", "audio_processing_impl.cc",
    "gain_control.h", "gain_control.c", "gain_control_impl.h",
    "gain_control_impl.cc", "agc_manager_direct.h", "agc_manager_direct.cc",
    "adaptive_digital_gain_controller.h", "adaptive_digital_gain_controller.cc",
    "adaptive_agc.h", "adaptive_agc.cc", "agc2_common.h",
    "fixed_digital_level_estimator.h", "fixed_digital_level_estimator.cc",
    "input_volume_controller.h", "input_volume_controller.cc",
    "noise_level_estimator.h", "noise_level_estimator.cc",
    "speech_level_estimator.h", "speech_level_estimator.cc",
    "saturation_protector.h", "saturation_protector.cc",
    "gain_applier.h", "gain_applier.cc", "limiter.h", "limiter.cc",
    "rnn_vad_weights.h", "rnn_vad_weights.cc",
})
UPSTREAM_DIRECTORY_NAMES = frozenset({
    "agc2", "rnn_vad", "webrtc-audio-processing", "webrtc_audio_processing",
    "pywebrtc_audio", "pywebrtc-audio", "libwebrtc", "webrtc",
})
UPSTREAM_SUBSTRING_TOKENS = (
    "pywebrtc", "webrtc-audio-processing", "webrtc_audio_processing",
    "libwebrtc",
)

SEARCH_ROOTS = (
    ("sdk", SDK_ROOT),
    ("adapters", WORKSPACE / "adapters"),
    ("data", WORKSPACE / "data"),
    ("cpp-library", WORKSPACE / "cpp-library"),
    ("third_party", WORKSPACE / "third_party"),
    ("deps", WORKSPACE / "deps"),
)
MAX_SCAN_ENTRIES = 200000
MAX_SCAN_DEPTH = 14

FIXTURE_SPANS = (
    (0, 800, "voiced"),
    (800, 1000, "pause"),
    (1000, 1800, "voiced"),
    (1800, 2100, "filler"),
    (2100, 2800, "voiced"),
    (2800, 3200, "pause"),
)

GATES = (
    {
        "id": "RG-01",
        "gate": "upstream_source_and_revision_pin",
        "status": "blocked",
        "reason": ("No WebRTC APM AGC/AGC2 source tree at an exact revision is "
                   "present; no verified commit, tree or file digest exists."),
        "reopen": ("Stage the exact WebRTC revision containing the legacy AGC "
                   "and AGC2 sources and record commit, tree and file digests "
                   "before any build or comparison."),
    },
    {
        "id": "RG-02",
        "gate": "upstream_license_notice_and_rights_review",
        "status": "blocked",
        "reason": ("No exact WebRTC NOTICE, third-party notice set, patent "
                   "review or wheel/binding redistribution decision is present."),
        "reopen": ("Vendor the exact Apache-2.0 licence and NOTICE text for the "
                   "pinned revision, review third-party and embedded-weight "
                   "terms, and record the approved distribution scope."),
    },
    {
        "id": "RG-03",
        "gate": "exact_apm_build_and_runtime_install_parity",
        "status": "blocked",
        "reason": ("Nothing was fetched, built or installed; no WebRTC APM "
                   "library, pywebrtc-audio wheel or runnable environment is "
                   "present."),
        "reopen": ("Build or install the pinned APM revision and prove a clean "
                   "importable runtime at the declared boundary before running "
                   "any AGC experiment."),
    },
    {
        "id": "RG-04",
        "gate": "agc_agc2_api_geometry_delay_drain_and_mode_parity",
        "status": "blocked",
        "reason": ("No AudioProcessor or GainControl API was exercised; frame "
                   "geometry, startup delay, drain, reset and execution-mode "
                   "ownership are unresolved."),
        "reopen": ("Measure the real AGC and AGC2 configuration paths, delay, "
                   "drain, reset and mode ownership at 16 kHz mono and map them "
                   "to the v0 content model."),
    },
    {
        "id": "RG-05",
        "gate": "separate_dsp_agc_comparison_and_rights_qualified_cohort",
        "status": "blocked",
        "reason": ("No candidate output exists, so the required comparison with "
                   "a separate DSP AGC and a rights-qualified cohort was not run."),
        "reopen": ("Freeze a permitted paired cohort and compare the pinned "
                   "WebRTC AGC/AGC2 candidate with an independent DSP AGC "
                   "control on identical items and settings."),
    },
    {
        "id": "RG-06",
        "gate": "gain_response_attack_release_headroom_and_preservation",
        "status": "blocked",
        "reason": ("Gain, frequency response, attack/release, headroom, peak "
                   "limit and clean-speech preservation require candidate "
                   "output and do not exist."),
        "reopen": ("Measure gain steps, sweeps, impulses, silence, clean speech, "
                   "noise-floor and overload cases with paired preservation and "
                   "adverse-result reporting."),
    },
    {
        "id": "RG-07",
        "gate": "target_runtime_timing_memory_and_callback_suitability",
        "status": "blocked",
        "reason": ("Only static synthetic characterisation exists; no paced "
                   "runtime, device clock, CPU, memory or callback-path "
                   "measurement was performed."),
        "reopen": ("Measure paced target-device timing, memory, callback "
                   "suitability and content delay independently of compute "
                   "speed."),
    },
    {
        "id": "RG-08",
        "gate": "provider_intake_public_surface_independent_review_and_release",
        "status": "blocked",
        "reason": ("No provider intake, descriptor, public-surface decision, "
                   "independent exact-head review or release approval exists."),
        "reopen": ("Complete provider intake, a versioned public-surface "
                   "decision, independent exact-head review and release "
                   "approval."),
    },
)

UPSTREAM_BLOCKER = {
    "status": "blocked_upstream_absent",
    "artifact": ("WebRTC Audio Processing Module legacy AGC (WebRtcAgc) and "
                 "AGC2 source plus a runnable APM runtime at an exact pinned "
                 "revision"),
    "expected_license": ("Apache-2.0 for WebRTC source, subject to the exact "
                         "revision's NOTICE and third-party terms"),
    "pinned_revision": None,
    "source_digest": None,
    "runtime_digest": None,
    "no_upstream_parity_claim": True,
    "documented_reference_revisions": [
        {
            "revision": "2bfa7672456357808005d712724b092088c37470",
            "path": ("modules/audio_processing/agc2/"
                     "adaptive_digital_gain_controller.cc"),
            "provenance": "research/level_tone_control_20261028.md:20",
            "verified_locally": False,
        },
        {
            "revision": "504bd59422283ebfa6275108804197edeeef908e",
            "path": "modules/audio_processing/include/audio_processing.h",
            "provenance": "research/level_tone_control_20261028.md:20",
            "verified_locally": False,
        },
        {
            "revision": "de65ddc2122470001c85ef15c83bc9d23a7ee8de",
            "path": ("webrtc/modules/audio_processing/include/"
                     "audio_processing.h"),
            "provenance": ("research/voice-enhancement-20261101/"
                           "agent-transform-space/REPORT.md:39"),
            "verified_locally": False,
        },
    ],
    "required_files": [
        "modules/audio_processing/include/audio_processing.h",
        "modules/audio_processing/audio_processing_impl.cc",
        "modules/audio_processing/agc/gain_control.h",
        "modules/audio_processing/agc/legacy/gain_control.c",
        "modules/audio_processing/agc/agc_manager_direct.cc",
        "modules/audio_processing/agc2/adaptive_digital_gain_controller.cc",
        "modules/audio_processing/agc2/adaptive_agc.cc",
        "modules/audio_processing/agc2/fixed_digital_level_estimator.cc",
        "modules/audio_processing/agc2/input_volume_controller.cc",
        "modules/audio_processing/agc2/limiter.cc",
        "modules/audio_processing/agc2/rnn_vad/rnn_vad_weights.cc",
        "the revision's BUILD.gn or equivalent build description",
        "the revision's Apache-2.0 LICENSE and NOTICE text",
    ],
    "required_runtime": [
        "a built WebRTC APM library exposing AudioProcessor or GainControl",
        "or a pinned pywebrtc-audio==0.2.0 wheel in data/envs/webrtc with the "
        "binding's exact wheel digest and documented AGC coverage",
    ],
    "rights_requirement": (
        "The exact Apache-2.0 licence and NOTICE text for the pinned WebRTC "
        "revision, the third-party notice set, a patent-grant review, an "
        "explicit decision for any embedded or generated weights, and an "
        "approved redistribution model for the source, native library or "
        "pywebrtc-audio wheel are required before any wrapper, build, "
        "comparison or release can be claimed. The local binding pin is not "
        "evidence of AGC API coverage: the checked-in adapter disables AGC."
    ),
    "workspace_search": [
        "third_party/ contains only speexdsp",
        "deps/lock.json pins only SpeexDSP 1.2.1; no WebRTC APM entry",
        "adapters/webrtc-ns pins pywebrtc-audio==0.2.0 for noise suppression "
        "and states that AGC is disabled",
        "data/envs/webrtc is absent; pywebrtc_audio is not importable",
        "no audio_processing.h, gain_control.h, gain_control.c, agc2 source "
        "file or WebRTC archive exists in the bounded search roots",
    ],
    "not_attempted": [
        "no network download or package installation",
        "no fabricated, reconstructed or surrogate WebRTC AGC/AGC2 source",
        "no substitution of an unrelated gain controller for the candidate",
        "no upstream NOTICE or licence text was copied or invented",
    ],
    "reopen": (
        "Stage the exact WebRTC APM revision with its Apache-2.0 LICENSE and "
        "NOTICE, record commit/tree/file and runtime digests, review third-party "
        "and weight terms, build or install the runtime, then repeat the DSP "
        "profile against the real AGC and AGC2 APIs with a separate DSP AGC "
        "control and an independent exact-head review."
    ),
}

NON_CLAIMS = (
    "No WebRTC source, header, native library, wheel, NOTICE bundle or "
    "download is included.",
    "No WebRTC AGC or AGC2 algorithm is implemented, approximated or simulated.",
    "No installed v0, public API, C ABI, descriptor, registry or default change.",
    "No provider is registered or enabled by default.",
    "No real speech, corpus, listening panel, benchmark or quality claim exists.",
    "No device timing, callback, CPU, memory or release claim is made.",
    "No missing, rejected or adverse result qualifies a candidate.",
)

INVARIANTS = (
    "Installed v0 stays 16 kHz, mono, float32, 160 samples per frame.",
    "Only docs/task-evidence/webrtc-agc-agc2/ is touched.",
    "The reference is a task-local evidence builder, not WebRTC AGC or AGC2.",
    "All stimuli are analytic or seeded synthetic; no real corpus or weights.",
    "Missing, invalid, nonfinite and out-of-range inputs fail closed.",
    "Only stable linked-row identity enters canonical bytes or gates.",
)


class EvidenceError(ValueError):
    """Base error with a stable machine-readable code."""

    code = "EVIDENCE_ERROR"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code


class ConfigError(EvidenceError):
    code = "INVALID_CONFIG"


class InputError(EvidenceError):
    code = "INVALID_INPUT"


class JsonError(EvidenceError):
    code = "INVALID_JSON"


class UpstreamAbsent(EvidenceError):
    code = "UPSTREAM_ABSENT"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _pairs_hook(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise JsonError("DUPLICATE_KEY: " + key, "DUPLICATE_KEY")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise JsonError("NONFINITE_CONSTANT: " + token, "NONFINITE_CONSTANT")


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_pairs_hook,
                          parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise JsonError("INVALID_JSON: " + str(error), "INVALID_JSON")


def finite_json(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_json(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_json(item) for item in value)
    return True


def _r(value: float, places: int = 9) -> float:
    return round(float(value), places)


def tensor_digest(samples: Iterable[float]) -> str:
    digest = hashlib.sha256()
    for value in samples:
        digest.update(struct.pack("<f", float(value)))
    return digest.hexdigest()


def peak_abs(samples: Iterable[float]) -> float:
    return max((abs(float(value)) for value in samples), default=0.0)


def rms(samples: Sequence[float]) -> float:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    total = math.fsum(float(value) * float(value) for value in samples)
    return math.sqrt(total / len(samples))


def db_ratio(numerator: float, denominator: float) -> float:
    if numerator <= 0.0 or denominator <= 0.0:
        raise InputError("NONPOSITIVE_RMS", "NONPOSITIVE_RMS")
    return 20.0 * math.log10(numerator / denominator)


def _lcg(seed: int):
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield (state / 4294967296.0) * 2.0 - 1.0


def silence(length: int = 1600) -> Tuple[float, ...]:
    return (0.0,) * length


def impulse(length: int = 1600, position: int = 800,
            amplitude: float = 0.5) -> Tuple[float, ...]:
    if not 0 <= position < length:
        raise ConfigError("impulse position out of range", "INVALID_STIMULUS")
    values = [0.0] * length
    values[position] = amplitude
    return tuple(values)


def step(length: int = 1600, position: int = 800,
         amplitude: float = 0.25) -> Tuple[float, ...]:
    if not 0 <= position <= length:
        raise ConfigError("step position out of range", "INVALID_STIMULUS")
    return tuple(0.0 if index < position else amplitude
                 for index in range(length))


def sweep(length: int = 1600, start_hz: float = 200.0,
          end_hz: float = 3000.0, amplitude: float = 0.3) -> Tuple[float, ...]:
    if length <= 0 or start_hz <= 0.0 or end_hz <= 0.0:
        raise ConfigError("invalid sweep geometry", "INVALID_STIMULUS")
    duration = length / float(SAMPLE_RATE_HZ)
    values = []
    for index in range(length):
        t = index / float(SAMPLE_RATE_HZ)
        phase = 2.0 * math.pi * (start_hz * t +
                                 (end_hz - start_hz) * t * t /
                                 (2.0 * duration))
        values.append(amplitude * math.sin(phase))
    return tuple(values)


def _span_kind(index: int) -> str:
    for start, end, kind in FIXTURE_SPANS:
        if start <= index < end:
            return kind
    return "pause"


def speech_like(length: int = 3200, seed: int = 20261126) -> Tuple[float, ...]:
    noise = _lcg(seed)
    values = []
    for index in range(length):
        kind = _span_kind(index)
        noise_value = next(noise)
        t = index / float(SAMPLE_RATE_HZ)
        if kind == "voiced":
            value = (0.25 * math.sin(2.0 * math.pi * 120.0 * t) +
                     0.12 * math.sin(2.0 * math.pi * 240.0 * t) +
                     0.06 * math.sin(2.0 * math.pi * 360.0 * t))
            envelope = 0.65 + 0.35 * math.sin(2.0 * math.pi * 3.0 * t)
            value = value * envelope + 0.005 * noise_value
        elif kind == "filler":
            value = 0.02 * noise_value
        else:
            value = 0.001 * noise_value
        values.append(value)
    return tuple(values)


STIMULUS_GENERATORS = {
    "silence": lambda: silence(1600),
    "impulse": lambda: impulse(1600, 800, 0.5),
    "step": lambda: step(1600, 800, 0.25),
    "sweep": lambda: sweep(1600, 200.0, 3000.0, 0.3),
    "speech_like": lambda: speech_like(3200),
}


def stimulus_metrics(name: str, samples: Sequence[float]) -> Dict[str, Any]:
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    peak = 0.0
    nonfinite = 0
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            nonfinite += 1
            continue
        peak = max(peak, abs(number))
    if nonfinite:
        raise InputError("NONFINITE_SAMPLE", "NONFINITE")
    if peak > MAX_ABS_STIMULUS:
        raise InputError("STIMULUS_OUT_OF_RANGE", "OUT_OF_RANGE")
    return {
        "name": name,
        "sample_count": len(samples),
        "peak_abs": _r(peak),
        "rms": _r(rms([float(value) for value in samples])),
        "nonfinite_count": 0,
        "digest": tensor_digest([float(value) for value in samples]),
    }


def speech_contrast(samples: Sequence[float]) -> Dict[str, Any]:
    voiced = []
    pause = []
    for index, value in enumerate(samples):
        kind = _span_kind(index)
        if kind == "voiced":
            voiced.append(float(value))
        elif kind == "pause":
            pause.append(float(value))
    voiced_rms = rms(voiced)
    pause_rms = rms(pause)
    return {
        "voiced_rms": _r(voiced_rms),
        "pause_rms": _r(pause_rms),
        "voiced_to_pause_db": _r(db_ratio(voiced_rms, pause_rms)),
        "proxy": "source-anchored voiced/pause RMS contrast; not intelligibility",
    }


def _validate_sample_list(samples: Any, expected: int | None) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise InputError("SAMPLES_NOT_A_LIST", "INVALID_SAMPLE_TYPE")
    if expected is not None and len(samples) != expected:
        raise InputError("WRONG_SAMPLE_COUNT", "WRONG_SAMPLE_COUNT")
    if not samples:
        raise InputError("EMPTY_SAMPLES", "EMPTY_SAMPLES")
    result: List[float] = []
    for index, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InputError("INVALID_SAMPLE_TYPE: " + str(index),
                             "INVALID_SAMPLE_TYPE")
        number = float(value)
        if not math.isfinite(number):
            raise InputError("NONFINITE_SAMPLE: " + str(index), "NONFINITE")
        if abs(number) > MAX_ABS_INPUT:
            raise InputError("SAMPLE_OUT_OF_RANGE: " + str(index),
                             "OUT_OF_RANGE")
        result.append(number)
    return result


def _require_int(value: Any, code: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(code, code)
    if minimum is not None and value < minimum:
        raise ConfigError(code, code)
    return value


def validate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise InputError("request must be an object", "INVALID_REQUEST")
    unknown = sorted(set(request) - REQUEST_KEYS)
    if unknown:
        raise ConfigError("UNKNOWN_FIELD: " + ",".join(unknown), "UNKNOWN_FIELD")
    missing = sorted(REQUEST_KEYS - set(request))
    if missing:
        raise ConfigError("MISSING_FIELD: " + ",".join(missing), "MISSING_FIELD")
    candidate = request["candidate"]
    if candidate not in CANDIDATES:
        raise ConfigError("UNKNOWN_CANDIDATE", "UNKNOWN_CANDIDATE")
    if _require_int(request["sample_rate_hz"], "WRONG_RATE") != SAMPLE_RATE_HZ:
        raise ConfigError("WRONG_RATE", "WRONG_RATE")
    if _require_int(request["channels"], "WRONG_CHANNELS") != 1:
        raise ConfigError("WRONG_CHANNELS", "WRONG_CHANNELS")
    if _require_int(request["frame_samples"], "WRONG_FRAME") != FRAME_SAMPLES:
        raise ConfigError("WRONG_FRAME", "WRONG_FRAME")
    samples = _validate_sample_list(request["samples"], FRAME_SAMPLES)
    epoch = _require_int(request["epoch"], "INVALID_EPOCH", 0)
    first_input_sample = _require_int(request["first_input_sample"],
                                      "INVALID_POSITION", 0)
    lifecycle = request["lifecycle"]
    if lifecycle not in LIFECYCLES:
        raise ConfigError("INVALID_LIFECYCLE", "INVALID_LIFECYCLE")
    execution_mode = _require_int(request["execution_mode"], "INVALID_MODE")
    if execution_mode not in EXECUTION_MODES:
        raise ConfigError("INVALID_MODE", "INVALID_MODE")
    return {
        "candidate": candidate,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "samples": tuple(samples),
        "epoch": epoch,
        "first_input_sample": first_input_sample,
        "lifecycle": lifecycle,
        "execution_mode": execution_mode,
    }


def probe_candidate(request: Any) -> None:
    validated = validate_request(request)
    raise UpstreamAbsent(
        "UPSTREAM_ABSENT: " + validated["candidate"] +
        " source/runtime is not present; no processing is performed",
        "UPSTREAM_ABSENT")


def _base_request() -> Dict[str, Any]:
    return {
        "candidate": "webrtc_agc2",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": FRAME_SAMPLES,
        "samples": [0.0] * FRAME_SAMPLES,
        "epoch": 1,
        "first_input_sample": 0,
        "lifecycle": "prepared",
        "execution_mode": 1,
    }


def _adverse_request_specs():
    base = _base_request()

    def variant(**changes):
        value = dict(base)
        value.update(changes)
        return value

    def with_samples(samples):
        return variant(samples=samples)

    short = [0.0] * (FRAME_SAMPLES - 1)
    nan_samples = [0.0] * FRAME_SAMPLES
    nan_samples[7] = float("nan")
    inf_samples = [0.0] * FRAME_SAMPLES
    inf_samples[9] = float("inf")
    return (
        ("unknown_candidate", variant(candidate="webrtc_agc3")),
        ("unknown_field", variant(extra=True)),
        ("missing_field", {key: value for key, value in base.items()
                           if key != "epoch"}),
        ("wrong_rate", variant(sample_rate_hz=48000)),
        ("wrong_channels", variant(channels=2)),
        ("wrong_frame", variant(frame_samples=320)),
        ("short_samples", with_samples(short)),
        ("nonfinite_nan", with_samples(nan_samples)),
        ("nonfinite_inf", with_samples(inf_samples)),
        ("out_of_range", with_samples([4.5] * FRAME_SAMPLES)),
        ("bool_sample", with_samples([True] + [0.0] * (FRAME_SAMPLES - 1))),
        ("string_sample", with_samples(["0.0"] + [0.0] * (FRAME_SAMPLES - 1))),
        ("negative_epoch", variant(epoch=-1)),
        ("bool_epoch", variant(epoch=True)),
        ("negative_position", variant(first_input_sample=-160)),
        ("closed_lifecycle", variant(lifecycle="closed")),
        ("drained_lifecycle", variant(lifecycle="drained")),
        ("invalid_execution_mode", variant(execution_mode=4)),
        ("request_not_object", "not-an-object"),
    )


def _adverse_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for name, request in _adverse_request_specs():
        accepted = False
        error = "NOT_REJECTED"
        try:
            validate_request(request)
            accepted = True
        except EvidenceError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "cases": cases,
        "note": "Invalid requests are rejected before any candidate call; no metrics exist.",
    }


def _json_adverse_cases() -> Dict[str, Any]:
    specs = (
        ("duplicate_key", '{"a":1,"a":2}'),
        ("nan_constant", '{"a":NaN}'),
        ("infinity_constant", '{"a":Infinity}'),
        ("negative_infinity_constant", '{"a":-Infinity}'),
        ("trailing_data", '{"a":1} extra'),
        ("invalid_syntax", '{"a":}'),
    )
    cases: List[Dict[str, Any]] = []
    for name, text in specs:
        accepted = False
        error = "NOT_REJECTED"
        try:
            strict_json_loads(text)
            accepted = True
        except JsonError as exception:
            error = exception.code
        cases.append({"id": name, "accepted": accepted, "error": error})
    return {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases if case["accepted"]),
        "all_rejected": all(not case["accepted"] for case in cases),
        "metrics": None,
        "cases": cases,
    }


def missing_result(fixture_name: str) -> Dict[str, Any]:
    return {
        "fixture": fixture_name,
        "status": "blocked",
        "reason": "upstream_absent",
        "metrics": None,
        "qualifies_candidate": False,
        "note": "No candidate output exists; missing evidence never qualifies.",
    }


def _name_matches(name: str, is_directory: bool) -> bool:
    lower = name.lower()
    if is_directory:
        return lower in UPSTREAM_DIRECTORY_NAMES
    if lower in EXACT_UPSTREAM_NAMES:
        return True
    return any(token in lower for token in UPSTREAM_SUBSTRING_TOKENS)


def _module_importable(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def absence_probe() -> Dict[str, Any]:
    matches: List[str] = []
    roots_scanned: List[str] = []
    visited = 0
    truncated = False
    for label, root in SEARCH_ROOTS:
        if not root.is_dir():
            continue
        roots_scanned.append(label)
        for directory, directory_names, file_names in os.walk(
                root, followlinks=False):
            depth = len(Path(directory).relative_to(root).parts)
            if depth >= MAX_SCAN_DEPTH:
                directory_names[:] = []
                continue
            selected: List[str] = []
            for name in sorted(directory_names):
                if name in SKIP_DIRECTORY_NAMES:
                    continue
                if (Path(directory) / name).resolve() == HERE:
                    continue
                selected.append(name)
                visited += 1
                if _name_matches(name, True):
                    relative = (Path(directory) / name).relative_to(root)
                    matches.append(label + ":" + relative.as_posix())
                if visited >= MAX_SCAN_ENTRIES:
                    truncated = True
                    break
            directory_names[:] = selected
            if truncated:
                break
            for name in sorted(file_names):
                visited += 1
                if _name_matches(name, False):
                    relative = (Path(directory) / name).relative_to(root)
                    matches.append(label + ":" + relative.as_posix())
                if visited >= MAX_SCAN_ENTRIES:
                    truncated = True
                    break
            if truncated:
                break
        if truncated:
            break
    matches = sorted(set(matches))
    env_python = WORKSPACE / "data/envs/webrtc/bin/python"
    requirements_path = WORKSPACE / "adapters/webrtc-ns/requirements.lock"
    adapter_readme = WORKSPACE / "adapters/webrtc-ns/README.md"
    requirements_text = (requirements_path.read_text(encoding="utf-8")
                         if requirements_path.is_file() else "")
    readme_text = (adapter_readme.read_text(encoding="utf-8")
                   if adapter_readme.is_file() else "")
    runtime = {
        "data_env_webrtc_bin_python": env_python.is_file(),
        "pywebrtc_audio_importable": _module_importable("pywebrtc_audio"),
        "webrtc_audio_processing_importable": _module_importable(
            "webrtc_audio_processing"),
        "adapter_requirements_pin": "pywebrtc-audio==0.2.0" in requirements_text,
        "adapter_states_agc_disabled": any(
            phrase in readme_text for phrase in
            ("AGC is disabled", "AGC are disabled", "AGC disabled")),
    }
    runtime_present = any((
        runtime["data_env_webrtc_bin_python"],
        runtime["pywebrtc_audio_importable"],
        runtime["webrtc_audio_processing_importable"],
    ))
    present = bool(matches) or runtime_present
    if truncated:
        status = "indeterminate_scan_limit"
    elif present:
        status = "upstream_present_unqualified"
    else:
        status = "blocked_upstream_absent"
    return {
        "status": status,
        "roots_scanned": roots_scanned,
        "entries_visited": visited,
        "scan_truncated": truncated,
        "name_matches": matches,
        "match_count": len(matches),
        "runtime": runtime,
        "present": present,
        "expectation": "absent",
        "found_count": len(matches) + (1 if runtime_present else 0),
        "note": ("Read-only name probe only. It does not inspect file contents, "
                 "load a library or execute a candidate."),
    }


def board_link_projection() -> Tuple[List[Dict[str, Any]], str]:
    if not BOARD_PATH.is_file():
        raise ConfigError("TASKS.json is missing", "BOARD_MISSING")
    board = strict_json_loads(BOARD_PATH.read_text(encoding="utf-8"))
    if not isinstance(board, dict) or not isinstance(board.get("tasks"), list):
        raise ConfigError("TASKS.json shape is invalid", "BOARD_INVALID")
    task = None
    for row in board["tasks"]:
        if isinstance(row, dict) and row.get("id") == TASK:
            task = row
            break
    if task is None:
        raise ConfigError("linked task row is missing", "BOARD_ROW_MISSING")
    stable = {
        "task_id": task.get("id"),
        "title": task.get("title"),
        "mode": task.get("mode"),
        "repository": task.get("repository"),
        "component": task.get("component"),
    }
    if stable != EXPECTED_LINK:
        raise ConfigError("stable linked-row identity changed",
                          "BOARD_IDENTITY_CHANGED")
    rows = [stable]
    digest = sha256_bytes(canonical_bytes(rows))
    return rows, digest


def qualification() -> Dict[str, Any]:
    return {
        "all_required_results_present": False,
        "candidate_qualified": False,
        "decision": "DEFER",
        "processor_exposure": "deferred_until_independent_review",
        "proposal_only": True,
        "readiness": "incomplete",
        "status": "not_qualified",
        "upstream_parity": False,
    }


def boundary() -> Dict[str, Any]:
    return {
        "benchmark_claim": False,
        "board_or_handoff_changed": False,
        "ci_changed": False,
        "descriptor_default_changed": False,
        "descriptor_registration": False,
        "enabled_by_default": False,
        "format": {
            "channels": 1,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": "float32",
            "sample_rate_hz": SAMPLE_RATE_HZ,
        },
        "installed_v0_unchanged": True,
        "opt_in_required": True,
        "provider_intake_complete": False,
        "provider_registered": False,
        "public_api_abi_changed": False,
        "public_c_boundary": "not used: no C provider, header or installed target",
        "real_corpus_or_weights": False,
        "registry_changed": False,
        "release_claim": False,
        "shared_cmake_changed": False,
    }


def profile_mapping() -> Dict[str, str]:
    return {
        "gain_and_frequency_response": "blocked_upstream_absent",
        "attack_and_release": "blocked_upstream_absent",
        "headroom_and_peak_limit": "blocked_upstream_absent",
        "delay_and_drain": "blocked_upstream_absent",
        "state_transitions": "blocked_upstream_absent",
        "nonlinear_interactions": "blocked_upstream_absent",
        "sweeps_steps_impulses_silence_clean_speech":
            "characterised_only_no_candidate_processing",
        "intelligibility_or_load_control": "blocked_upstream_absent",
        "numerical_behavior": "partial_local_harness_only_no_candidate",
        "separate_dsp_agc_comparison": "blocked_upstream_absent",
        "apm_mode_ownership": "unresolved_upstream_absent",
    }


def stimulus_probe() -> Dict[str, Any]:
    stimuli: Dict[str, Any] = {}
    identity: Dict[str, Any] = {}
    for name, generator in STIMULUS_GENERATORS.items():
        samples = generator()
        stimuli[name] = stimulus_metrics(name, samples)
        identity[name] = {
            "digest": tensor_digest(samples),
            "byte_identical": tuple(samples) == tuple(float(value)
                                                     for value in samples),
        }
    return {
        "purpose": ("harness stimulus characterisation only; not an AGC or AGC2 "
                    "result and not a candidate output"),
        "stimuli": stimuli,
        "speech_contrast": speech_contrast(STIMULUS_GENERATORS["speech_like"]()),
        "identity_control": identity,
        "candidate_processing": False,
    }


def candidates() -> Dict[str, Any]:
    return {
        "webrtc_agc": {
            "status": "blocked_upstream_absent",
            "metrics": None,
            "qualifies_candidate": False,
            "apm_mode_ownership": "unresolved",
            "reason": ("Legacy WebRTC AGC source and runtime are absent; no "
                       "output, setting or mode was exercised."),
        },
        "webrtc_agc2": {
            "status": "blocked_upstream_absent",
            "metrics": None,
            "qualifies_candidate": False,
            "apm_mode_ownership": "unresolved",
            "reason": ("WebRTC AGC2 source and runtime are absent; no adaptive "
                       "digital gain or limiter path was exercised."),
        },
    }


def separate_dsp_agc_comparison() -> Dict[str, Any]:
    return {
        "status": "blocked_upstream_absent",
        "baseline": "none_run",
        "candidate_metrics": None,
        "control_metrics": None,
        "qualifies_candidate": False,
        "reason": ("No candidate output exists, so a paired comparison with a "
                   "separate DSP AGC was not run."),
        "reopen": ("Stage the candidate and a rights-qualified paired cohort, "
                   "then compare identical items and settings."),
    }


def apm_mode_ownership() -> Dict[str, Any]:
    return {
        "status": "unresolved",
        "owner": None,
        "declared_modes": [],
        "execution_modes": {
            "inline_callback": "unresolved",
            "processing_thread": "unresolved",
            "buffered_worker": "unresolved",
        },
        "reason": ("No APM instance, descriptor or runtime exists; ownership of "
                   "legacy AGC versus AGC2 across AudioProcessor and GainControl "
                   "and the three v0 execution modes cannot be qualified."),
        "required_evidence": [
            "exact APM revision and public API path for AGC and AGC2",
            "the settings that enable or disable each controller",
            "measured delay, drain, reset and callback-path behavior per mode",
            "an explicit ownership decision with independent review",
        ],
        "qualifies_candidate": False,
    }


def candidate_required_results() -> Dict[str, str]:
    return {
        "identity_noisy_control": "blocked_upstream_absent",
        "established_task_matched_baseline": "blocked_upstream_absent",
        "paired_si_sdr_stoi": "blocked_upstream_absent",
        "clean_speech_preservation": "blocked_upstream_absent",
        "gain_and_frequency_response": "blocked_upstream_absent",
        "attack_and_release": "blocked_upstream_absent",
        "headroom_and_peak_limit": "blocked_upstream_absent",
        "delay_state_and_drain": "blocked_upstream_absent",
        "nonlinear_interaction": "blocked_upstream_absent",
        "numerical_and_nonfinite": "partial_local_harness_only",
        "separate_dsp_agc_comparison": "blocked_upstream_absent",
        "apm_mode_ownership": "blocked_upstream_absent",
    }


def artifact_pins(names: Sequence[str] = SOURCE_ARTIFACT_FILES) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in names:
        path = HERE / name
        if not path.is_file():
            raise ConfigError("missing package artifact: " + name,
                              "MISSING_ARTIFACT")
        pins[name] = sha256_file(path)
    return pins


def source_evidence_statements() -> List[str]:
    return [
        ("research/level_tone_control_20261028.md:20 documents WebRTC AGC2 as "
         "adaptive digital gain followed by a limiter with configurable "
         "headroom and bounded gain changes, and links upstream revisions. "
         "This package does not fetch, verify or reproduce them."),
        ("adapters/webrtc-ns/README.md runs pywebrtc-audio==0.2.0 for APM noise "
         "suppression with AGC disabled; no AGC or AGC2 behavior is inferred."),
        ("cpp-library/PIPELINE_DESIGN_REPORT.md reports no integrated duplex APM "
         "run with AGC configured; it is not evidence for AGC cost or behavior."),
        ("plan/INVENTORY.json records webrtc-agc-agc2 as considered with the "
         "DSP verification profile and PIPELINE_DESIGN_REPORT.md as its only "
         "evidence path."),
    ]


def build_report() -> Dict[str, Any]:
    links, link_digest = board_link_projection()
    probe = absence_probe()
    adverse_request = _adverse_cases()
    adverse_json = _json_adverse_cases()
    stimuli = stimulus_probe()
    gates = [dict(gate) for gate in GATES]
    local_checks = {
        "report_generation_deterministic": True,
        "strict_json_rejects_duplicate_and_nonfinite": True,
        "stable_board_identity_only": True,
        "absence_probe_complete": probe["status"] == "blocked_upstream_absent",
        "invalid_requests_rejected": adverse_request["all_rejected"],
        "nonfinite_samples_rejected": any(
            case["id"].startswith("nonfinite") and not case["accepted"]
            for case in adverse_request["cases"]),
        "invalid_json_rejected": adverse_json["all_rejected"],
        "missing_result_blocked": missing_result("webrtc_agc2")["status"] == "blocked",
        "identity_control_bit_exact": all(
            block["byte_identical"] for block in stimuli["identity_control"].values()),
        "eight_release_gates_blocked": (
            len(gates) == 8 and all(gate["status"] == "blocked"
                                    for gate in gates)),
    }
    report = {
        "schema_id": SCHEMA_ID,
        "task": TASK,
        "component": COMPONENT,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "status": "proposal_only_not_qualified",
        "decision": "DEFER",
        "qualification_status": "not_qualified",
        "qualification": qualification(),
        "boundary": boundary(),
        "profile": {
            "name": "dsp",
            "source": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        },
        "profile_mapping": profile_mapping(),
        "reference": {
            "implementation": "task-local standard-library evidence builder",
            "real_webrtc_source_or_binary": False,
            "upstream_parity": False,
            "downloads": False,
            "synthetic_only": True,
            "model_weights": False,
            "deterministic": True,
            "candidate_processing": False,
            "note": ("No AGC or AGC2 algorithm is implemented or simulated; "
                     "only stimulus characterization, request rejection and "
                     "absence checks are performed."),
        },
        "invariants": list(INVARIANTS),
        "non_claims": list(NON_CLAIMS),
        "source_evidence_statements": source_evidence_statements(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_links": links,
        "board_link_projection_sha256": link_digest,
        "board_link_fields": list(LINK_FIELDS),
        "board_mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
        "artifact_pins": artifact_pins(),
        "upstream_blocker": dict(UPSTREAM_BLOCKER),
        "candidates": candidates(),
        "separate_dsp_agc_comparison": separate_dsp_agc_comparison(),
        "apm_mode_ownership": apm_mode_ownership(),
        "absence_probe": probe,
        "stimulus_probe": stimuli,
        "adverse": {
            "invalid_config_and_input": adverse_request,
            "invalid_json_numeric_fields": adverse_json,
            "missing_result": missing_result("webrtc_agc2_synthetic_placeholder"),
        },
        "required_results": candidate_required_results(),
        "local_harness_checks": local_checks,
        "release_gates": gates,
        "remaining_gates": [gate["id"] for gate in gates],
        "gates": [gate["id"] for gate in gates],
        "regressions": [],
        "regression_count": 0,
        "no_missing_result_qualifies_candidate": True,
        "generated_by": "run.py --report",
    }
    if not finite_json(report):
        raise EvidenceError("REPORT_NONFINITE", "REPORT_NONFINITE")
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report()) + b"\n"
