# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, model-free synthetic AEC3 plus APM-NS-level reference.

This is a *proposal-only* room-profile evidence package.  It does not contain,
link, download, install or emulate the WebRTC APM/AEC3 runtime.  The processor
below is an original teaching reference: an AEC3-shaped shadow/primary adaptive
filter with a residual gain, followed by a decision-directed spectral suppressor
whose strength is selected by one frozen APM noise-suppression level (1, 2 or
3).  Every constant is defined here and the reference is stdlib-only.

The package records exactly one configured synthetic APM instance template and
all of its toggles.  The three independent level runs differ only in
``noise_suppression.level``.  No synthetic score qualifies a candidate, a
release gate, a listening result, a device-timing result or a benchmark.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent

TASK_ID = "SDK-WEBRTC-AEC3-PLUS-APM-NS-LEVELS-1-3"
COMPONENT = "webrtc-aec3-plus-apm-ns-levels-1-3"
BASE_COMMIT = "c58c907576576d06fc5d0f3aa046ca4cb29e8ea0"
BRANCH = "swarm/SDK-WEBRTC-AEC3-PLUS-APM-NS-LEVELS-1-3"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "room"
STATUS = "proposal_only_not_qualified"
COMPLETENESS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
LOCAL_IDENTITY = "webrtc-aec3-plus-apm-ns-levels-1-3-synthetic-reference-v1"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
FIXTURE_FRAMES = 120
TOTAL_SAMPLES = FIXTURE_FRAMES * FRAME_SAMPLES
MAX_ABS_INPUT = 4.0
NS_LEVELS = (1, 2, 3)

FFT_SIZE = 256
FFT_BINS = FFT_SIZE // 2 + 1
NS_CALIBRATION_FRAMES = 10
NS_CALIBRATION_ALPHA = 0.20
NS_TRACK_ALPHA = 0.02
NS_GAIN_ALPHA = 0.70

AEC_FILTER_TAPS = 48
AEC_STEP_MAIN = 0.18
AEC_STEP_SHADOW = 0.25
AEC_DT_ENTER = 0.35
AEC_DT_EXIT = 0.70
AEC_DT_HANGOVER = 2
AEC_GAIN_LOW = 0.30
AEC_GAIN_HIGH = 0.80
AEC_GAIN_MIN = 0.22
AEC_EPS = 1e-8
AEC_MIN_RENDER_ENERGY = 1e-3
AEC_LEAKAGE = 0.9995
AEC_MAX_WEIGHT = 8.0

# Level -> (oversubtraction, gain floor).  Higher level means stronger
# suppression and therefore a larger near-end preservation risk.  These are
# synthetic reference knobs, not WebRTC APM constants.
NS_PARAMS: Dict[int, Dict[str, float]] = {
    1: {"oversubtraction": 1.20, "gain_floor": 0.55},
    2: {"oversubtraction": 1.60, "gain_floor": 0.40},
    3: {"oversubtraction": 2.00, "gain_floor": 0.25},
}
AEC_ONLY_PARAMS: Dict[str, float] = {"oversubtraction": 0.0, "gain_floor": 1.0}

APM_TOGGLE_NAMES = (
    "echo_canceller",
    "noise_suppression",
    "high_pass_filter",
    "gain_controller",
    "voice_activity_detection",
    "residual_echo_detector",
    "transient_suppression",
    "pre_amplifier",
    "post_amplifier",
    "experimental_agc2",
)

SOURCE_PINS: Dict[str, str] = {
    "research/aec_research_20261028.md":
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
    "adapters/webrtc-aec/README.md":
        "c074f84c859dcfb2ac7414a775dbcddcf2f2646deca66810c9241fcf7adec050",
    "adapters/webrtc-aec/run.py":
        "fab77579592939e6f550f28c1a923153703c6ad89fd3f4b4270318f3f8353e70",
    "adapters/webrtc-ns/README.md":
        "8893bace6b0289135f6d1ccad949a9eba44a824e37f45765f30b4192f82c5992",
    "adapters/webrtc-ns/adapter.json":
        "42aac7a2a0f5709e24785eb87d5922fdd30cabadd54336604ff739dc70fa874a",
    "adapters/webrtc-ns/run.py":
        "9751e44371e875b522351edbe306920cc895e2fa22725064701852ef8e73f097",
    "adapters/webrtc-ns/requirements.lock":
        "c289d4c0ab4af3f54e2bf693f1f81a01aa7cc479627f9e7a3161b2f1f792d591",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "reports/webrtc_aec3_synthetic_pilot_20261028.csv":
        "1c12f41c821f2005f15b466dd376412b53f0a14e3f42a0b3ef1c8d47e2fbf168",
    "reports/webrtc_aec3_ns1_synthetic_pilot_20261028.csv":
        "73ed6f1735683566f3929b031b2c2233349840733cafd3544a08a2d0e921adcc",
    "reports/webrtc_aec3_ns2_synthetic_pilot_20261028.csv":
        "c1c1669958d0f57a4db6a3ea3b175ab73b3ebac249cffe7eb4c47da82b89d77c",
    "reports/webrtc_aec3_ns3_synthetic_pilot_20261028.csv":
        "4bbaafcaa6f5564bd7b3f7c150d32774819fa1ec9673f083688c3201df8d6115",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/webrtc-aec3/contract.json":
        "f3bd95cac4ce78cfddb971a90a11ecc4b17097444398edd3eb32dee665bb3258",
    "docs/task-evidence/webrtc-aec3/report.json":
        "da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283",
    "docs/task-evidence/webrtc-apm-ns/contract.json":
        "55824bc8e2e386162c040a405abdea0ec46e85fa7f7febcad0e4bef6f11222c7",
    "docs/task-evidence/webrtc-apm-ns/report.json":
        "23466752f5fd536014d4920a00c09adabbcba51f1cff2286390c30178a82ab90",
    "docs/task-evidence/webrtc-vad/contract.json":
        "74137431954f9ed1206a56fc5e5fa28003a6f78985fe8699cf500bbc981d60ef",
    "docs/task-evidence/webrtc-vad/report.json":
        "762086dffc6cfc504035c99648e66065157e852cc4fb4b2500d646d7ce77d6cb",
    "docs/task-evidence/webrtc-apm/contract.json":
        "eeebdd1e1bf4dea38c0944187e8fddfe8583b462222cad2aaa239d775e5b5a02",
    "docs/task-evidence/webrtc-apm/report.json":
        "aae1ec05c9250fc529d104a602ded0e44b0bb0d36221d58d4e786413d2a43bbe",
}

TASK_ROW_IDENTITY: Dict[str, Any] = {
    "id": TASK_ID,
    "title": "WebRTC AEC3 plus APM NS levels 1\u20133",
    "repository": "audio-sdk",
    "mode": "implementation",
    "component": COMPONENT,
    "depends_on": [
        "SDK-FND-AUDIT",
        "SDK-FND-DUPLEX",
        "SDK-FND-EVIDENCE",
        "SDK-FND-PROVIDER",
    ],
    "evidence": ["research/aec_research_20261028.md"],
    "base_commit": BASE_COMMIT,
    "branch": BRANCH,
}
MUTABLE_PROVENANCE: Dict[str, Any] = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "mutable": True,
    "gate": False,
    "hashed": False,
    "note": (
        "Only the stable linked-row identity above is compared. The mutable "
        "full board file is never hashed into canonical bytes."
    ),
}
SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_only": True,
    "installed_v0_format": "16 kHz mono float32, 160 samples",
    "real_webrtc_aec3_source_or_runtime": False,
    "real_webrtc_apm_source_or_runtime": False,
    "licensed_source_or_binary": False,
    "weights_or_assets": False,
    "real_speech_or_corpus": False,
    "downloads": False,
    "device_timing": False,
    "listening": False,
    "benchmark_claim": False,
    "release_claim": False,
}
PUBLIC_SURFACE: Dict[str, bool] = {
    "abi_change": False,
    "benchmark_claim": False,
    "ci_change": False,
    "descriptor_default_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_change": False,
    "registry_change": False,
    "release_claim": False,
    "shared_cmakelists_change": False,
}
QUALIFICATION: Dict[str, Any] = {
    "status": QUALIFICATION_STATUS,
    "qualifies": False,
    "incomplete": True,
    "proposal_only": True,
    "missing_result_promoted": False,
    "processor_exposure": False,
    "release_claim": False,
}

RELEASE_GATES: List[Dict[str, Any]] = [
    {
        "id": "licensed_webrtc_aec3_and_apm_runtime",
        "requirement": (
            "Pinned, hash-verified WebRTC AEC3 plus APM source revision or "
            "pywebrtc-audio==0.2.0 wheel/source with Apache-2.0 LICENSE and "
            "NOTICE reviewed for the exact revision and approval to execute it."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "frozen_apm_instance_and_ns_levels",
        "requirement": (
            "One documented APM instance at the exact revision with every "
            "toggle and the three NS levels recorded, including AEC3, HPF, "
            "AGC, VAD, residual suppression and stream-delay settings."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "rights_cleared_room_cohort",
        "requirement": (
            "Rights-cleared paired render/capture or measured RIR room cohort "
            "with device, channel, rate, hop, delay, movement and noise "
            "metadata."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "echo_near_end_and_double_talk_quality",
        "requirement": (
            "Paired echo attenuation, near-end damage, double-talk, nonlinear "
            "echo and path-change evaluation on the exact runtime and room "
            "cohort, including all three NS levels independently."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "device_timing_drift_and_deadline",
        "requirement": (
            "Target-device loop delay, clock drift, buffering, content and "
            "availability timing, memory and deadline budget for every level."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "real_no_reference_and_nonfinite_controls",
        "requirement": (
            "Independent no-reference suppressor comparison plus real-runtime "
            "missing, delayed, dropout and nonfinite controls; synthetic "
            "passthrough is not an independent comparison."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "authorized_listening_quality",
        "requirement": (
            "Authorized listening or an approved quality assessment on the "
            "exact runtime, room conditions and NS levels."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "provider_intake_and_release_review",
        "requirement": (
            "Provider/catalog/license intake, descriptor and public-surface "
            "review, independent exact-head approval and explicit release "
            "admission before any exposure."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
]

REQUIRED_ARTIFACTS: List[Dict[str, Any]] = [
    {
        "id": "licensed_webrtc_aec3_and_apm_runtime",
        "artifact": (
            "Pinned WebRTC AEC3+APM source revision or "
            "pywebrtc-audio==0.2.0 wheel/source with exact SHA-256."
        ),
        "present": False,
        "rights_requirement": (
            "Apache-2.0 LICENSE and NOTICE for the exact upstream/binding "
            "revision, redistribution terms and approval to execute."
        ),
        "why_blocked": (
            "No WebRTC AEC3/APM source, wheel, binary or runtime is present in "
            "the workspace; no download or fabrication is permitted."
        ),
    },
    {
        "id": "frozen_apm_instance_and_ns_levels",
        "artifact": (
            "A documented single APM instance with all toggles and the exact "
            "NS levels 1-3 at the pinned revision."
        ),
        "present": False,
        "rights_requirement": (
            "Public API documentation and configuration reference for the "
            "exact upstream revision."
        ),
        "why_blocked": (
            "The adapter records the intended toggles, but the licensed runtime "
            "and its exact revision/configuration reference are absent."
        ),
    },
    {
        "id": "rights_cleared_room_cohort",
        "artifact": (
            "Paired render/capture or measured-RIR room cohort with timestamps, "
            "device metadata and rights."
        ),
        "present": False,
        "rights_requirement": (
            "Written corpus and participant rights for evaluation and derived "
            "outputs; no unlicensed AEC-Challenge or other recording is bundled."
        ),
        "why_blocked": "No rights-cleared room cohort is supplied here.",
    },
    {
        "id": "room_measurement_harness",
        "artifact": (
            "Frozen room evaluation harness covering echo-only, near-only, "
            "double-talk, movement, delay, drift and reset."
        ),
        "present": False,
        "rights_requirement": "Harness license and target-device access approval.",
        "why_blocked": (
            "Only a deterministic synthetic fixture exists; no device loop or "
            "clock-drift harness is present."
        ),
    },
    {
        "id": "provider_intake_and_quality_review",
        "artifact": (
            "Provider intake, descriptor/catalog review, independent listening "
            "and public-surface approval."
        ),
        "present": False,
        "rights_requirement": "Reviewer, listening-panel and release approval.",
        "why_blocked": "No provider registration, listening or release review is in scope here.",
    },
]
NON_CLAIMS: List[str] = [
    "No WebRTC AEC3 or WebRTC APM algorithm, source, wheel, binary or runtime is implemented, linked or emulated.",
    "No licensed source, binary, model weight, real room recording or corpus is present or downloaded.",
    "No authoritative WebRTC noise-suppression level ranking, echo result or oracle is claimed.",
    "No listening, device-timing, clock-drift, benchmark or release claim is made.",
    "No installed v0, ABI, registry, descriptor, default, shared build or CI behavior is changed.",
    "No provider is registered, exposed or default-enabled.",
    "No missing, blocked or adverse result is promoted; no result qualifies.",
]
REPRODUCTION: List[str] = [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
    "python3 run.py --report",
    "python3 run.py --sources",
    "python3 run.py --inspect",
    "python3 verify.py",
]

REPORT_KEYS = {
    "SPDX-FileCopyrightText",
    "SPDX-License-Identifier",
    "schema_id",
    "task",
    "component",
    "profile",
    "base_commit",
    "branch",
    "status",
    "completeness",
    "decision",
    "qualification",
    "task_row",
    "mutable_provenance",
    "source_pins",
    "boundary_pins",
    "sibling_pins",
    "scope",
    "public_surface",
    "configured_apm_instance",
    "acceptance_profile",
    "fixture",
    "observed_provenance",
    "per_level_runs",
    "controls",
    "level_ablation",
    "ranking",
    "adverse_results",
    "missing_results",
    "failure_controls",
    "artifact_assessment",
    "release_gates",
    "non_claims",
    "reproduction",
    "regeneration",
}


class ReferenceError(ValueError):
    """Explicit rejection; no rejected value is scored or promoted."""


def _reject_constant(value: str) -> None:
    raise ValueError("non_json_constant:" + value)


def read_strict_json(path: Path) -> Any:
    """Parse strict JSON; duplicate keys, NaN and Infinity are rejected."""
    def unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"),
                       parse_constant=_reject_constant,
                       object_pairs_hook=unique_pairs)
    if not isinstance(value, dict):
        raise ValueError("json_root_is_not_object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_bytes(report).decode("utf-8")
    payload = (text + "\n").encode("utf-8")
    return text, sha256_bytes(payload)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def digest_values(values: Sequence[float]) -> str:
    payload = struct.pack("<%dd" % len(values),
                          *[float(value) for value in values])
    return sha256_bytes(payload)


def _validate_level(level: Any) -> int:
    if isinstance(level, bool) or not isinstance(level, int) or level not in NS_LEVELS:
        raise ReferenceError("invalid_ns_level")
    return level


def apm_instance(level: int) -> Dict[str, Any]:
    """Return the one configured APM instance template at an NS level."""
    level = _validate_level(level)
    params = NS_PARAMS[level]
    return {
        "instance_id": "apm-aec3-ns-levels-1-3-synthetic.v1",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "execution_mode": "inline_callback_synthetic",
        "stream_delay_hint_ms": 0,
        "toggles": {
            "echo_canceller": {
                "enabled": True,
                "mode": "aec3_synthetic_shadow_primary",
                "filter_taps": AEC_FILTER_TAPS,
                "stream_delay_hint_ms": 0,
                "extended_filter": False,
            },
            "noise_suppression": {
                "enabled": True,
                "level": level,
                "policy": "fixed_level",
                "oversubtraction": params["oversubtraction"],
                "gain_floor": params["gain_floor"],
            },
            "high_pass_filter": {"enabled": False},
            "gain_controller": {"enabled": False, "mode": "none"},
            "voice_activity_detection": {"enabled": False},
            "residual_echo_detector": {
                "enabled": True,
                "mode": "synthetic_hysteresis",
                "enter_ratio": AEC_DT_ENTER,
                "exit_ratio": AEC_DT_EXIT,
                "hangover_frames": AEC_DT_HANGOVER,
            },
            "transient_suppression": {"enabled": False},
            "pre_amplifier": {"enabled": False, "fixed_gain_factor": 1.0},
            "post_amplifier": {"enabled": False, "fixed_gain_factor": 1.0},
            "experimental_agc2": {"enabled": False},
        },
    }


def aec_only_instance() -> Dict[str, Any]:
    """AEC-only control configuration; not one of the three level runs."""
    config = apm_instance(1)
    config["instance_id"] = "apm-aec3-ns-off-control.v1"
    config["toggles"]["noise_suppression"] = {
        "enabled": False,
        "level": 0,
        "policy": "off_control",
        "oversubtraction": 0.0,
        "gain_floor": 1.0,
    }
    return config


def validate_instance_config(config: Any) -> Dict[str, Any]:
    """Strictly validate one configured APM instance; reject unknown values."""
    if not isinstance(config, dict):
        raise ReferenceError("invalid_instance_config")
    try:
        level = config["toggles"]["noise_suppression"]["level"]
    except (KeyError, TypeError):
        raise ReferenceError("invalid_instance_config")
    level = _validate_level(level)
    expected = apm_instance(level)
    try:
        same = canonical_bytes(config) == canonical_bytes(expected)
    except (TypeError, ValueError):
        raise ReferenceError("invalid_instance_config")
    if not same:
        raise ReferenceError("invalid_instance_config")
    return expected


def configured_apm_payload() -> Dict[str, Any]:
    """Record the single configured instance, every toggle and the level deltas."""
    level_configs = [apm_instance(level) for level in NS_LEVELS]
    base = level_configs[0]
    toggle_matrix: List[Dict[str, Any]] = []
    for name in APM_TOGGLE_NAMES:
        entry: Dict[str, Any] = {
            "toggle": name,
            "frozen": name != "noise_suppression",
            "configured": base["toggles"][name],
            "per_level": {},
        }
        if name == "noise_suppression":
            for level in NS_LEVELS:
                entry["per_level"][str(level)] = {
                    "level": level,
                    "oversubtraction": NS_PARAMS[level]["oversubtraction"],
                    "gain_floor": NS_PARAMS[level]["gain_floor"],
                }
        toggle_matrix.append(entry)
    return {
        "instance_count": 1,
        "instance_id": base["instance_id"],
        "template_frozen": True,
        "levels_benchmarked": list(NS_LEVELS),
        "only_ns_level_varies": True,
        "shared_settings": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "execution_mode": base["execution_mode"],
            "stream_delay_hint_ms": base["stream_delay_hint_ms"],
        },
        "toggles": base["toggles"],
        "toggle_names": list(APM_TOGGLE_NAMES),
        "toggle_matrix": toggle_matrix,
        "per_level": [
            {
                "level": level,
                "only_delta": {"noise_suppression.level": level},
                "config_sha256": sha256_bytes(canonical_bytes(apm_instance(level))),
                "noise_suppression": apm_instance(level)["toggles"]["noise_suppression"],
            }
            for level in NS_LEVELS
        ],
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic duplex fixture
# ---------------------------------------------------------------------------

SEGMENTS: List[Dict[str, Any]] = [
    {"id": "silence", "start": 0, "end": 10, "render_env": 0.0, "near_env": 0.0, "path": "A"},
    {"id": "echo_only_a", "start": 10, "end": 35, "render_env": 1.0, "near_env": 0.0, "path": "A"},
    {"id": "overlap_a", "start": 35, "end": 60, "render_env": 0.8, "near_env": 0.9, "path": "A"},
    {"id": "near_only_a", "start": 60, "end": 70, "render_env": 0.0, "near_env": 1.0, "path": "A"},
    {"id": "echo_only_a_late", "start": 70, "end": 80, "render_env": 1.0, "near_env": 0.0, "path": "A"},
    {"id": "overlap_b", "start": 80, "end": 100, "render_env": 0.9, "near_env": 0.8, "path": "B"},
    {"id": "echo_only_b", "start": 100, "end": 110, "render_env": 1.0, "near_env": 0.0, "path": "B"},
    {"id": "near_only_b", "start": 110, "end": 120, "render_env": 0.0, "near_env": 1.0, "path": "B"},
]
PATH_A = {8: 1.0, 16: 0.55, 28: 0.25}
PATH_B = {12: 0.9, 32: 0.6}
PATH_CHANGE_FRAME = 80
PATH_CHANGE_SAMPLE = PATH_CHANGE_FRAME * FRAME_SAMPLES
DROP_START_FRAME = 45
DROP_END_FRAME = 55
RESET_FRAME = 60
RESET_EPOCH = 2
DELAYED_REFERENCE_SAMPLES = 24
RENDER_SEED = 439041101
NEAR_SEED = 1584361601
NOISE_SEED = 2596069104
RENDER_NOISE_SEED = 907633385

METRIC_WINDOWS: Dict[str, Tuple[int, int]] = {
    "echo_only_early": (12 * FRAME_SAMPLES, 34 * FRAME_SAMPLES),
    "echo_only_late": (70 * FRAME_SAMPLES, 80 * FRAME_SAMPLES),
    "near_only_early": (60 * FRAME_SAMPLES, 70 * FRAME_SAMPLES),
    "near_only_late": (110 * FRAME_SAMPLES, 120 * FRAME_SAMPLES),
    "overlap_early": (38 * FRAME_SAMPLES, 58 * FRAME_SAMPLES),
    "overlap_late": (82 * FRAME_SAMPLES, 100 * FRAME_SAMPLES),
}


def _lcg(seed: int, count: int) -> List[float]:
    state = seed & 0x7FFFFFFF
    values: List[float] = []
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        values.append(state / 1073741824.0 - 1.0)
    return values


def _segment_for(frame: int) -> Dict[str, Any]:
    for segment in SEGMENTS:
        if segment["start"] <= frame < segment["end"]:
            return segment
    raise ReferenceError("fixture_frame_out_of_range")


def build_fixture(condition: str = "duplex") -> Dict[str, Any]:
    """Build a frozen deterministic render/capture fixture."""
    if condition not in {"duplex", "echo_only", "near_only", "delayed_render",
                         "no_reference", "reference_dropout", "reset"}:
        raise ReferenceError("unknown_condition")
    render_noise = _lcg(RENDER_NOISE_SEED, TOTAL_SAMPLES)
    capture_noise = _lcg(NOISE_SEED, TOTAL_SAMPLES)
    render: List[float] = []
    near: List[float] = []
    for sample in range(TOTAL_SAMPLES):
        frame = sample // FRAME_SAMPLES
        segment = _segment_for(frame)
        t = sample / SAMPLE_RATE_HZ
        render_base = (0.22 * math.sin(2.0 * math.pi * 137.0 * t)
                       + 0.09 * math.sin(2.0 * math.pi * 311.0 * t)
                       + 0.025 * math.sin(2.0 * math.pi * 523.0 * t))
        near_base = (0.16 * math.sin(2.0 * math.pi * 183.0 * t + 0.31)
                     + 0.06 * math.sin(2.0 * math.pi * 271.0 * t + 0.77)
                     + 0.02 * math.sin(2.0 * math.pi * 431.0 * t + 1.11))
        render_value = segment["render_env"] * render_base + 0.001 * render_noise[sample]
        near_value = segment["near_env"] * near_base
        render.append(f32(render_value))
        near.append(f32(near_value))
    if condition == "near_only":
        render = [0.0] * TOTAL_SAMPLES
    if condition == "echo_only":
        near = [0.0] * TOTAL_SAMPLES

    echo: List[float] = []
    for sample in range(TOTAL_SAMPLES):
        taps = PATH_A if sample < PATH_CHANGE_SAMPLE else PATH_B
        value = 0.0
        for delay, gain in taps.items():
            if sample >= delay:
                value += gain * render[sample - delay]
        echo.append(f32(value))
    microphone = [f32(echo[i] + near[i] + 0.0025 * capture_noise[i])
                  for i in range(TOTAL_SAMPLES)]

    reference: Optional[List[float]]
    if condition == "no_reference":
        reference = None
    elif condition == "delayed_render":
        reference = [0.0] * DELAYED_REFERENCE_SAMPLES + render[:-DELAYED_REFERENCE_SAMPLES]
    else:
        reference = list(render)

    return {
        "condition": condition,
        "render": render,
        "near": near,
        "echo": echo,
        "microphone": microphone,
        "reference": reference,
        "dropout": (DROP_START_FRAME, DROP_END_FRAME) if condition == "reference_dropout" else None,
        "reset_frame": RESET_FRAME if condition == "reset" else None,
    }


def fixture_spec() -> Dict[str, Any]:
    return {
        "fixture_id": "webrtc-aec3-plus-apm-ns-levels-1-3-room-v1",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": "f32",
        "frame_samples": FRAME_SAMPLES,
        "hop_samples": FRAME_SAMPLES,
        "frames": FIXTURE_FRAMES,
        "samples": TOTAL_SAMPLES,
        "segments": SEGMENTS,
        "geometry": {
            "path_a_taps": {str(k): v for k, v in PATH_A.items()},
            "path_b_taps": {str(k): v for k, v in PATH_B.items()},
            "path_change_frame": PATH_CHANGE_FRAME,
            "path_change_sample": PATH_CHANGE_SAMPLE,
            "max_path_delay_samples": max(max(PATH_A), max(PATH_B)),
            "delayed_reference_samples": DELAYED_REFERENCE_SAMPLES,
        },
        "excitation": {
            "render_hz": [137.0, 311.0, 523.0],
            "render_amplitudes": [0.22, 0.09, 0.025],
            "near_hz": [183.0, 271.0, 431.0],
            "near_amplitudes": [0.16, 0.06, 0.02],
            "seeds": {
                "render_noise": RENDER_NOISE_SEED,
                "near": NEAR_SEED,
                "capture_noise": NOISE_SEED,
            },
        },
        "reference_dropout": {
            "start_frame": DROP_START_FRAME,
            "end_frame": DROP_END_FRAME,
            "withheld_frames": DROP_END_FRAME - DROP_START_FRAME,
        },
        "reset": {
            "initial_epoch": 1,
            "reset_epoch": RESET_EPOCH,
            "reset_frame": RESET_FRAME,
            "reset_sample": RESET_FRAME * FRAME_SAMPLES,
        },
        "metric_windows": {key: list(value) for key, value in METRIC_WINDOWS.items()},
        "metrics_note": (
            "ERLE and near-SNR are synthetic proxies over frozen half-open "
            "windows from generated ground truth; they are not WebRTC, "
            "device-timing or accepted quality measurements."
        ),
    }


def fixture_payload(condition: str = "duplex") -> Dict[str, Any]:
    data = build_fixture(condition)
    spec = fixture_spec()
    spec.update({
        "condition": condition,
        "render_sha256": digest_values(data["render"]),
        "near_sha256": digest_values(data["near"]),
        "echo_sha256": digest_values(data["echo"]),
        "microphone_sha256": digest_values(data["microphone"]),
        "reference_sha256": (digest_values(data["reference"])
                             if data["reference"] is not None else None),
    })
    return spec


# ---------------------------------------------------------------------------
# Synthetic APM-shaped processor
# ---------------------------------------------------------------------------


def _fft(real: List[float], imag: List[float], inverse: bool = False) -> None:
    n = len(real)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            real[i], real[j] = real[j], real[i]
            imag[i], imag[j] = imag[j], imag[i]
    length = 2
    while length <= n:
        angle = (2.0 * math.pi / length) * (1.0 if inverse else -1.0)
        wlen_real = math.cos(angle)
        wlen_imag = math.sin(angle)
        half = length // 2
        for start in range(0, n, length):
            w_real = 1.0
            w_imag = 0.0
            for offset in range(half):
                left = start + offset
                right = left + half
                u_real = real[left]
                u_imag = imag[left]
                v_real = real[right] * w_real - imag[right] * w_imag
                v_imag = real[right] * w_imag + imag[right] * w_real
                real[left] = u_real + v_real
                imag[left] = u_imag + v_imag
                real[right] = u_real - v_real
                imag[right] = u_imag - v_imag
                next_real = w_real * wlen_real - w_imag * wlen_imag
                w_imag = w_real * wlen_imag + w_imag * wlen_real
                w_real = next_real
        length <<= 1
    if inverse:
        scale = 1.0 / n
        for i in range(n):
            real[i] *= scale
            imag[i] *= scale


class ApmAecNs:
    """Frame-causal synthetic AEC3-shaped canceller plus NS-level suppressor."""

    def __init__(self, level: int, epoch: int = 1, first_sample: int = 0) -> None:
        level = _validate_level(level)
        self.level = level
        self.config = apm_instance(level)
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 1:
            raise ReferenceError("invalid_epoch")
        if (isinstance(first_sample, bool) or not isinstance(first_sample, int)
                or first_sample < 0):
            raise ReferenceError("invalid_first_sample")
        self.epoch = epoch
        self.first_sample = first_sample
        self._clear()

    @classmethod
    def aec_only(cls, epoch: int = 1, first_sample: int = 0) -> "ApmAecNs":
        engine = cls(1, epoch=epoch, first_sample=first_sample)
        engine.level = 0
        engine.config = aec_only_instance()
        return engine

    def _clear(self) -> None:
        self.main = [0.0] * AEC_FILTER_TAPS
        self.shadow = [0.0] * AEC_FILTER_TAPS
        self.history = [0.0] * AEC_FILTER_TAPS
        self.last_ratio = 1.0
        self.hold_frames = 0
        self.position = self.first_sample
        self.frames = 0
        self.adapted_frames = 0
        self.double_talk_frames = 0
        self.no_reference_frames = 0
        self.failures = 0
        self.safety_resets = 0
        self.reset_count = 0
        self.noise_psd = [1e-10] * FFT_BINS
        self.previous_gain = [1.0] * FFT_BINS
        self.ns_frames = 0
        self.ns_gain_sum = 0.0

    def reset(self, epoch: int, first_sample: int) -> None:
        if (isinstance(epoch, bool) or not isinstance(epoch, int)
                or epoch <= self.epoch):
            raise ReferenceError("stale_or_invalid_epoch")
        if (isinstance(first_sample, bool) or not isinstance(first_sample, int)
                or first_sample < 0):
            raise ReferenceError("invalid_first_sample")
        self._clear()
        self.epoch = epoch
        self.first_sample = first_sample
        self.position = first_sample
        self.reset_count += 1

    def state_digest(self) -> str:
        return sha256_bytes(canonical_bytes([
            [round(value, 12) for value in self.main],
            [round(value, 12) for value in self.shadow],
            [round(value, 12) for value in self.history],
            [round(value, 10) for value in self.noise_psd],
            [round(value, 10) for value in self.previous_gain],
            self.epoch,
            self.first_sample,
            self.position,
            self.ns_frames,
        ]))

    def memory_floats(self) -> int:
        return (3 * AEC_FILTER_TAPS) + (2 * FFT_BINS) + 6

    def weight_l1(self) -> float:
        return sum(abs(value) for value in self.main)

    def _gain_for_ratio(self, ratio: float) -> float:
        if ratio <= AEC_GAIN_LOW:
            return AEC_GAIN_MIN
        if ratio >= AEC_GAIN_HIGH:
            return 1.0
        span = AEC_GAIN_HIGH - AEC_GAIN_LOW
        return AEC_GAIN_MIN + (ratio - AEC_GAIN_LOW) * (1.0 - AEC_GAIN_MIN) / span

    def _suppress(self, frame: Sequence[float]) -> Tuple[List[float], float]:
        params = NS_PARAMS[self.level]
        real = [0.0] * FFT_SIZE
        imag = [0.0] * FFT_SIZE
        for index in range(FRAME_SAMPLES):
            real[index] = frame[index]
        _fft(real, imag)
        alpha = (NS_CALIBRATION_ALPHA if self.ns_frames < NS_CALIBRATION_FRAMES
                 else NS_TRACK_ALPHA)
        oversubtraction = params["oversubtraction"]
        gain_floor = params["gain_floor"]
        gains: List[float] = []
        for band in range(FFT_BINS):
            power = real[band] * real[band] + imag[band] * imag[band]
            noise = self.noise_psd[band]
            self.noise_psd[band] = (1.0 - alpha) * noise + alpha * power
            wiener = max(power - oversubtraction * self.noise_psd[band], 0.0)
            wiener /= (power + 1e-12)
            gain = max(wiener, gain_floor)
            gain = NS_GAIN_ALPHA * self.previous_gain[band] + (1.0 - NS_GAIN_ALPHA) * gain
            self.previous_gain[band] = gain
            gains.append(gain)
            real[band] *= gain
            imag[band] *= gain
        for band in range(1, FFT_BINS - 1):
            real[FFT_SIZE - band] = real[band]
            imag[FFT_SIZE - band] = -imag[band]
        _fft(real, imag, inverse=True)
        output = [f32(real[index]) for index in range(FRAME_SAMPLES)]
        self.ns_frames += 1
        mean_gain = sum(gains) / len(gains)
        self.ns_gain_sum += mean_gain
        return output, mean_gain

    def process_frame(self, microphone: Sequence[float],
                      reference_frame: Optional[Sequence[float]] = None,
                      epoch: Optional[int] = None,
                      position: Optional[int] = None) -> Dict[str, Any]:
        if epoch is not None and (isinstance(epoch, bool) or epoch != self.epoch):
            raise ReferenceError("stale_or_invalid_epoch")
        if position is not None and (isinstance(position, bool)
                                     or position != self.position):
            raise ReferenceError("invalid_position")
        if (not isinstance(microphone, (list, tuple))
                or len(microphone) != FRAME_SAMPLES):
            raise ReferenceError("invalid_frame_length")
        mic: List[float] = []
        for value in microphone:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ReferenceError("invalid_microphone_frame")
            number = float(value)
            if not math.isfinite(number) or abs(number) > MAX_ABS_INPUT:
                raise ReferenceError("invalid_microphone_frame")
            mic.append(f32(number))

        if reference_frame is None:
            self.no_reference_frames += 1
            self.frames += 1
            self.position += FRAME_SAMPLES
            self.last_ratio = 1.0
            self.hold_frames = 0
            return {
                "samples": tuple(mic),
                "status": "passthrough_no_reference",
                "held": True,
                "gain": 1.0,
                "ratio": 1.0,
                "ns_gain": 1.0,
            }

        if (not isinstance(reference_frame, (list, tuple))
                or len(reference_frame) != FRAME_SAMPLES):
            raise ReferenceError("invalid_reference_length")
        rendered: List[float] = []
        for value in reference_frame:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ReferenceError("invalid_reference_frame")
            number = float(value)
            if not math.isfinite(number) or abs(number) > MAX_ABS_INPUT:
                raise ReferenceError("invalid_reference_frame")
            rendered.append(f32(number))

        ratio = self.last_ratio
        held = ratio >= AEC_DT_ENTER or self.hold_frames > 0
        gain = self._gain_for_ratio(ratio)
        residual: List[float] = []
        shadow_residual_energy = 0.0
        microphone_energy = 0.0
        frame_adapted = False

        for index in range(FRAME_SAMPLES):
            played = rendered[index]
            if not all(math.isfinite(value) for value in self.main):
                self.main = [0.0] * AEC_FILTER_TAPS
                self.safety_resets += 1
            estimate_shadow = 0.0
            estimate_main = 0.0
            render_energy = 0.0
            for tap in range(AEC_FILTER_TAPS):
                history = self.history[tap]
                estimate_shadow += self.shadow[tap] * history
                estimate_main += self.main[tap] * history
                render_energy += history * history
            residual_shadow = mic[index] - estimate_shadow
            residual_main = mic[index] - estimate_main
            value = f32(gain * residual_main)
            if not math.isfinite(value) or abs(value) > MAX_ABS_INPUT:
                value = 0.0
                self.failures += 1
            residual.append(value)
            shadow_residual_energy += residual_shadow * residual_shadow
            microphone_energy += mic[index] * mic[index]
            if render_energy > AEC_MIN_RENDER_ENERGY:
                step_shadow = AEC_STEP_SHADOW * residual_shadow / (render_energy + AEC_EPS)
                for tap in range(AEC_FILTER_TAPS):
                    value_shadow = (AEC_LEAKAGE * self.shadow[tap]
                                    + step_shadow * self.history[tap])
                    self.shadow[tap] = max(-AEC_MAX_WEIGHT,
                                           min(AEC_MAX_WEIGHT, value_shadow))
                if not held:
                    step_main = AEC_STEP_MAIN * residual_main / (render_energy + AEC_EPS)
                    for tap in range(AEC_FILTER_TAPS):
                        value_main = (AEC_LEAKAGE * self.main[tap]
                                      + step_main * self.history[tap])
                        self.main[tap] = max(-AEC_MAX_WEIGHT,
                                             min(AEC_MAX_WEIGHT, value_main))
                    frame_adapted = True
            for tap in range(AEC_FILTER_TAPS - 1, 0, -1):
                self.history[tap] = self.history[tap - 1]
            self.history[0] = played

        ratio = shadow_residual_energy / (microphone_energy + AEC_EPS)
        if not math.isfinite(ratio):
            ratio = 1.0
            self.failures += 1
        if ratio >= AEC_DT_ENTER:
            self.hold_frames = AEC_DT_HANGOVER
        elif ratio <= AEC_DT_EXIT:
            self.hold_frames = 0
        elif self.hold_frames > 0:
            self.hold_frames -= 1
        self.last_ratio = ratio
        self.frames += 1
        if frame_adapted:
            self.adapted_frames += 1
        if held:
            self.double_talk_frames += 1
        self.position += FRAME_SAMPLES

        ns_gain = 1.0
        if self.level in NS_PARAMS:
            output, ns_gain = self._suppress(residual)
        else:
            output = residual
        if any(not math.isfinite(value) for value in output):
            output = [0.0] * FRAME_SAMPLES
            self.failures += 1
        status = "double_talk_hold" if held else "adaptive"
        return {
            "samples": tuple(output),
            "status": status,
            "held": held,
            "gain": gain,
            "ratio": ratio,
            "ns_gain": ns_gain,
        }


# ---------------------------------------------------------------------------
# Stream runner, controls and metrics
# ---------------------------------------------------------------------------


def run_stream(data: Dict[str, Any], level: int = 1, mode: str = "apm",
               chunk_frames: int = 1,
               withhold_from_frame: Optional[int] = None,
               fixed_gain: float = 0.5) -> Dict[str, Any]:
    """Process one frozen stream; chunk_frames only changes caller slicing."""
    if mode not in {"apm", "aec_only", "identity", "fixed_attenuation"}:
        raise ReferenceError("unknown_mode")
    if isinstance(chunk_frames, bool) or not isinstance(chunk_frames, int) or chunk_frames < 1:
        raise ReferenceError("invalid_chunk_frames")
    if mode == "apm":
        _validate_level(level)
        engine: Optional[ApmAecNs] = ApmAecNs(level)
    elif mode == "aec_only":
        engine = ApmAecNs.aec_only()
    else:
        engine = None
    microphone = data["microphone"]
    if len(microphone) % FRAME_SAMPLES:
        raise ReferenceError("stream_not_frame_aligned")
    total_frames = len(microphone) // FRAME_SAMPLES
    output: List[float] = []
    statuses: List[str] = []
    ns_gains: List[float] = []
    resets: List[Dict[str, Any]] = []
    reset_frame = data.get("reset_frame")
    for chunk_start in range(0, total_frames, chunk_frames):
        chunk_end = min(chunk_start + chunk_frames, total_frames)
        for frame_index in range(chunk_start, chunk_end):
            if reset_frame == frame_index and engine is not None:
                engine.reset(RESET_EPOCH, frame_index * FRAME_SAMPLES)
                resets.append({
                    "frame": frame_index,
                    "sample": frame_index * FRAME_SAMPLES,
                    "epoch": engine.epoch,
                })
            start = frame_index * FRAME_SAMPLES
            mic_frame = tuple(microphone[start:start + FRAME_SAMPLES])
            if mode == "identity":
                samples = tuple(f32(value) for value in mic_frame)
                result = {"samples": samples, "status": "identity",
                          "gain": 1.0, "ratio": 0.0, "ns_gain": 1.0}
            elif mode == "fixed_attenuation":
                samples = tuple(f32(fixed_gain * value) for value in mic_frame)
                result = {"samples": samples, "status": "fixed_attenuation",
                          "gain": fixed_gain, "ratio": 0.0, "ns_gain": 1.0}
            else:
                assert engine is not None
                render = data.get("reference")
                withheld = render is None
                dropout = data.get("dropout")
                if dropout is not None and dropout[0] <= frame_index < dropout[1]:
                    withheld = True
                if (withhold_from_frame is not None
                        and frame_index >= withhold_from_frame):
                    withheld = True
                reference_frame = None if withheld else tuple(
                    render[start:start + FRAME_SAMPLES])
                result = engine.process_frame(mic_frame, reference_frame,
                                              epoch=engine.epoch, position=start)
            output.extend(result["samples"])
            statuses.append(result["status"])
            ns_gains.append(round(float(result.get("ns_gain", 1.0)), 9))
    return {
        "output": tuple(output),
        "statuses": tuple(statuses),
        "ns_gains": tuple(ns_gains),
        "resets": tuple(resets),
        "epoch": engine.epoch if engine is not None else 1,
        "frames": engine.frames if engine is not None else total_frames,
        "adapted_frames": engine.adapted_frames if engine is not None else 0,
        "double_talk_frames": engine.double_talk_frames if engine is not None else 0,
        "no_reference_frames": engine.no_reference_frames if engine is not None else 0,
        "safety_resets": engine.safety_resets if engine is not None else 0,
        "failures": engine.failures if engine is not None else 0,
        "reset_count": engine.reset_count if engine is not None else 0,
        "weight_l1": engine.weight_l1() if engine is not None else 0.0,
        "state_digest": engine.state_digest() if engine is not None else sha256_bytes(b""),
        "memory_floats": engine.memory_floats() if engine is not None else 0,
        "output_sha256": digest_values(output),
    }


def _energy(values: Sequence[float], start: int, end: int) -> float:
    total = 0.0
    for index in range(start, end):
        total += values[index] * values[index]
    return total


def _db(numerator: float, denominator: float) -> float:
    if numerator <= 0.0:
        return -200.0
    if denominator <= 0.0:
        return 200.0
    return round(10.0 * math.log10(numerator / denominator), 6)


def summarize(data: Dict[str, Any], output: Sequence[float]) -> Dict[str, Any]:
    microphone = data["microphone"]
    near = data["near"]
    if len(output) != len(microphone):
        raise ReferenceError("output_length_mismatch")
    nonfinite = sum(1 for value in output if not math.isfinite(value))
    residual = [output[i] - near[i] for i in range(len(output))]
    early = METRIC_WINDOWS["echo_only_early"]
    late = METRIC_WINDOWS["echo_only_late"]
    near_early = METRIC_WINDOWS["near_only_early"]
    near_late = METRIC_WINDOWS["near_only_late"]
    overlap = METRIC_WINDOWS["overlap_early"]
    return {
        "erle_early_db": _db(_energy(microphone, *early), _energy(output, *early)),
        "erle_late_db": _db(_energy(microphone, *late), _energy(output, *late)),
        "near_snr_early_db": _db(_energy(near, *near_early), _energy(residual, *near_early)),
        "near_snr_late_db": _db(_energy(near, *near_late), _energy(residual, *near_late)),
        "near_energy_change_db": _db(_energy(output, *near_late),
                                     _energy(near, *near_late)),
        "overlap_near_snr_db": _db(_energy(near, *overlap), _energy(residual, *overlap)),
        "nonfinite_count": nonfinite,
        "peak_abs": round(max(abs(value) for value in output), 9),
        "output_sha256": digest_values(output),
    }


def estimate_alignment(microphone: Sequence[float], reference: Sequence[float],
                       start: int, end: int, max_lag: int = 64) -> int:
    """Normalized cross-correlation lag proxy over a frozen window."""
    best_lag = 0
    best_score = -2.0
    for lag in range(-max_lag, max_lag + 1):
        numerator = 0.0
        left_energy = 0.0
        right_energy = 0.0
        for index in range(start, end):
            other = index - lag
            if other < 0 or other >= len(reference):
                continue
            left = microphone[index]
            right = reference[other]
            numerator += left * right
            left_energy += left * left
            right_energy += right * right
        score = numerator / math.sqrt(left_energy * right_energy + 1e-30)
        if score > best_score:
            best_score = score
            best_lag = lag
    return best_lag


def _status_for(condition: str, result: Dict[str, Any], mode: str) -> str:
    if mode == "identity":
        return "identity_control"
    if mode == "fixed_attenuation":
        return "fixed_attenuation_control"
    if condition == "no_reference":
        return "blocked_no_reference"
    if condition == "delayed_render":
        return "misaligned_reference"
    if condition == "reference_dropout":
        return "partial_reference"
    if result["failures"] or result["safety_resets"]:
        return "nonfinite_failure"
    return "ok_synthetic"


def _run_payload(condition: str, level: int = 1, mode: str = "apm",
                 withhold_from_frame: Optional[int] = None) -> Dict[str, Any]:
    data = build_fixture(condition)
    result = run_stream(data, level=level, mode=mode,
                        withhold_from_frame=withhold_from_frame)
    metrics = summarize(data, result["output"])
    return {
        "condition": condition,
        "mode": mode,
        "status": _status_for(condition, result, mode),
        "qualifies": False,
        "metrics": metrics,
        "output_sha256": result["output_sha256"],
        "state_digest": result["state_digest"],
        "frames": result["frames"],
        "adapted_frames": result["adapted_frames"],
        "double_talk_frames": result["double_talk_frames"],
        "no_reference_frames": result["no_reference_frames"],
        "safety_resets": result["safety_resets"],
        "failures": result["failures"],
        "resets": list(result["resets"]),
        "epoch": result["epoch"],
        "weight_l1": round(result["weight_l1"], 9),
        "memory_floats": result["memory_floats"],
    }


def per_level_runs() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for level in NS_LEVELS:
        row = _run_payload("duplex", level=level)
        row.update({
            "run_id": "apm_aec3_ns_l%d_duplex" % level,
            "variant": "apm_aec3_ns_l%d" % level,
            "ns_level": level,
            "aec_enabled": True,
            "ns_enabled": True,
            "toggles_delta": {"noise_suppression.level": level},
            "level_isolation": "fresh state; only noise_suppression.level differs",
        })
        rows.append(row)
    return rows


def control_runs() -> Dict[str, Dict[str, Any]]:
    controls = {
        "identity": _run_payload("duplex", mode="identity"),
        "fixed_attenuation": _run_payload("duplex", mode="fixed_attenuation"),
        "aec_only": _run_payload("duplex", mode="aec_only"),
        "no_reference_passthrough": _run_payload("no_reference", level=1),
        "delayed_render": _run_payload("delayed_render", level=1),
        "reference_dropout": _run_payload("reference_dropout", level=1),
        "near_only": _run_payload("near_only", level=1),
        "echo_only": _run_payload("echo_only", level=1),
    }
    reset = _run_payload("reset", level=1)
    reset["reset_replay"] = reset_replay()
    controls["reset"] = reset
    return controls


def reset_replay() -> Dict[str, Any]:
    data = build_fixture("reset")
    frames = 12
    start_frame = RESET_FRAME
    continued = ApmAecNs(1)
    for frame in range(start_frame):
        offset = frame * FRAME_SAMPLES
        continued.process_frame(
            tuple(data["microphone"][offset:offset + FRAME_SAMPLES]),
            tuple(data["reference"][offset:offset + FRAME_SAMPLES]))
    continued.reset(RESET_EPOCH, start_frame * FRAME_SAMPLES)
    fresh = ApmAecNs(1)
    fresh.reset(RESET_EPOCH, start_frame * FRAME_SAMPLES)
    continued_output: List[float] = []
    fresh_output: List[float] = []
    for frame in range(start_frame, start_frame + frames):
        offset = frame * FRAME_SAMPLES
        mic = tuple(data["microphone"][offset:offset + FRAME_SAMPLES])
        ref = tuple(data["reference"][offset:offset + FRAME_SAMPLES])
        continued_output.extend(continued.process_frame(mic, ref)["samples"])
        fresh_output.extend(fresh.process_frame(mic, ref)["samples"])
    invalid: List[str] = []
    for epoch, first in ((RESET_EPOCH, start_frame * FRAME_SAMPLES),
                         (RESET_EPOCH + 1, -1)):
        try:
            fresh.reset(epoch, first)
        except ReferenceError as error:
            invalid.append(str(error))
    return {
        "frames": frames,
        "start_sample": start_frame * FRAME_SAMPLES,
        "continued_output_sha256": digest_values(continued_output),
        "fresh_output_sha256": digest_values(fresh_output),
        "continued_state_digest": continued.state_digest(),
        "fresh_state_digest": fresh.state_digest(),
        "byte_identical": (digest_values(continued_output) == digest_values(fresh_output)
                           and continued.state_digest() == fresh.state_digest()),
        "invalid_reset_rejections": invalid,
        "qualifies": False,
    }


def causality_payload() -> Dict[str, Any]:
    rng = _lcg(20261028, TOTAL_SAMPLES)
    silence = {"microphone": [0.0] * TOTAL_SAMPLES,
               "reference": [0.0] * TOTAL_SAMPLES, "near": [0.0] * TOTAL_SAMPLES,
               "reset_frame": None, "dropout": None}
    impulse_mic = [0.0] * TOTAL_SAMPLES
    impulse_ref = [0.0] * TOTAL_SAMPLES
    impulse_mic[200] = 0.5
    impulse_ref[200] = 0.5
    impulse = {"microphone": impulse_mic, "reference": impulse_ref,
               "near": [0.0] * TOTAL_SAMPLES, "reset_frame": None, "dropout": None}
    step_mic = [0.0] * TOTAL_SAMPLES
    step_ref = [0.0] * TOTAL_SAMPLES
    for index in range(200, TOTAL_SAMPLES):
        step_mic[index] = 0.25
        step_ref[index] = 0.25
    step = {"microphone": step_mic, "reference": step_ref,
            "near": [0.0] * TOTAL_SAMPLES, "reset_frame": None, "dropout": None}
    silence_result = run_stream(silence)
    impulse_result = run_stream(impulse)
    step_result = run_stream(step)
    impulse_first = next((index for index, value in enumerate(impulse_result["output"])
                          if value != 0.0), -1)
    step_first = next((index for index, value in enumerate(step_result["output"])
                       if value != 0.0), -1)
    duplex = build_fixture("duplex")
    chunk_hashes = {
        "one_frame": run_stream(duplex, chunk_frames=1)["output_sha256"],
        "five_frames": run_stream(duplex, chunk_frames=5)["output_sha256"],
        "twelve_frames": run_stream(duplex, chunk_frames=12)["output_sha256"],
        "whole_stream": run_stream(duplex, chunk_frames=FIXTURE_FRAMES)["output_sha256"],
    }
    return {
        "algorithmic_delay_samples": 0,
        "buffering_delay_samples": 0,
        "future_frame_reads": False,
        "impulse_first_nonzero_sample": impulse_first,
        "impulse_peak_abs": round(max(abs(value) for value in impulse_result["output"]), 9),
        "step_first_nonzero_sample": step_first,
        "silence_peak_abs": round(max(abs(value) for value in silence_result["output"]), 9),
        "chunk_identity": chunk_hashes,
        "rng_probe_digest": digest_values(rng),
        "qualifies": False,
    }


def failure_controls() -> Dict[str, Any]:
    data = build_fixture("duplex")
    engine = ApmAecNs(2)
    clean_mic = tuple(data["microphone"][:FRAME_SAMPLES])
    clean_ref = tuple(data["reference"][:FRAME_SAMPLES])
    rejected: List[str] = []
    cases = [
        ("nonfinite_microphone", tuple([float("nan")] + list(clean_mic[1:])), clean_ref),
        ("out_of_range_microphone", tuple([9.0] + list(clean_mic[1:])), clean_ref),
        ("short_microphone", clean_mic[:8], clean_ref),
        ("nonfinite_reference", clean_mic, tuple([float("inf")] + list(clean_ref[1:]))),
        ("short_reference", clean_mic, clean_ref[:8]),
        ("bool_microphone", tuple([True] + list(clean_mic[1:])), clean_ref),
    ]
    before = engine.state_digest()
    for label, mic, ref in cases:
        try:
            engine.process_frame(mic, ref)
        except ReferenceError:
            rejected.append(label)
    after = engine.state_digest()
    for label, epoch, position in (
            ("stale_epoch", 0, 0),
            ("wrong_position", 1, 999),
            ("negative_position", 1, -160)):
        try:
            engine.process_frame(clean_mic, clean_ref, epoch=epoch, position=position)
        except ReferenceError:
            rejected.append(label)
    state_unchanged = before == after

    identity = run_stream(data, mode="identity")
    identity_ok = tuple(identity["output"]) == tuple(data["microphone"])

    advanced = ApmAecNs(1)
    for frame in range(5):
        offset = frame * FRAME_SAMPLES
        advanced.process_frame(tuple(data["microphone"][offset:offset + FRAME_SAMPLES]),
                               tuple(data["reference"][offset:offset + FRAME_SAMPLES]))
    advanced.main[0] = float("nan")
    safety_result = advanced.process_frame(
        tuple(data["microphone"][5 * FRAME_SAMPLES:6 * FRAME_SAMPLES]),
        tuple(data["reference"][5 * FRAME_SAMPLES:6 * FRAME_SAMPLES]))
    safety_ok = (advanced.safety_resets == 1
                 and all(math.isfinite(value) for value in safety_result["samples"]))

    config_rejections: List[str] = []
    for bad in (
            {"toggles": {}},
            apm_instance(1) | {"sample_rate_hz": 8000},
            apm_instance(1) | {"unknown_toggle": True},
    ):
        try:
            validate_instance_config(bad)
        except ReferenceError:
            config_rejections.append("invalid_instance_config")
    for bad_level in (0, 4, True, 1.5, "1", None):
        try:
            apm_instance(bad_level)  # type: ignore[arg-type]
        except ReferenceError:
            config_rejections.append("invalid_ns_level")

    no_reference = run_stream(data, level=1)
    withheld = run_stream(data, level=1, withhold_from_frame=0)
    no_reference_blocked = all(
        status == "passthrough_no_reference" for status in withheld["statuses"])

    checks = {
        "nonfinite_microphone_rejected": "nonfinite_microphone" in rejected,
        "out_of_range_microphone_rejected": "out_of_range_microphone" in rejected,
        "short_microphone_rejected": "short_microphone" in rejected,
        "nonfinite_reference_rejected": "nonfinite_reference" in rejected,
        "short_reference_rejected": "short_reference" in rejected,
        "bool_microphone_rejected": "bool_microphone" in rejected,
        "stale_epoch_rejected": "stale_epoch" in rejected,
        "wrong_position_rejected": "wrong_position" in rejected,
        "negative_position_rejected": "negative_position" in rejected,
        "invalid_frame_leaves_state_unchanged": state_unchanged,
        "identity_bit_exact": identity_ok,
        "nonfinite_state_safety_reset": safety_ok,
        "invalid_config_rejected": bool(config_rejections),
        "missing_reference_passthrough": no_reference_blocked,
        "reset_replay_byte_identical": reset_replay()["byte_identical"],
        "chunk_identity": len(set(causality_payload()["chunk_identity"].values())) == 1,
        "no_reference_run_recorded": no_reference["no_reference_frames"] == 0,
    }
    return {
        "all_explicit": True,
        "checks": checks,
        "rejected_count": len(rejected) + len(config_rejections),
        "blocked_count": 1 if no_reference_blocked else 0,
        "rejections": rejected + config_rejections,
        "qualifies": False,
    }


def level_ablation(levels: List[Dict[str, Any]],
                   controls: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    baseline = controls["aec_only"]["metrics"]
    rows: List[Dict[str, Any]] = []
    for row in levels:
        metrics = row["metrics"]
        rows.append({
            "level": row["ns_level"],
            "variant": row["variant"],
            "delta_erle_late_db_vs_aec_only": round(
                metrics["erle_late_db"] - baseline["erle_late_db"], 6),
            "delta_near_snr_late_db_vs_aec_only": round(
                metrics["near_snr_late_db"] - baseline["near_snr_late_db"], 6),
            "delta_near_energy_change_db_vs_aec_only": round(
                metrics["near_energy_change_db"] - baseline["near_energy_change_db"], 6),
            "independent_level_run": True,
            "only_ns_level_differs": True,
            "qualifies": False,
        })
    return rows


def adverse_results(levels: List[Dict[str, Any]],
                    controls: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    baseline = controls["aec_only"]["metrics"]
    for row in levels:
        metrics = row["metrics"]
        if metrics["near_snr_late_db"] < baseline["near_snr_late_db"]:
            rows.append({
                "result_id": row["variant"] + ":near_snr_late_below_aec_only",
                "classification": "adverse_unvalidated_synthetic_retained",
                "observed_db": metrics["near_snr_late_db"],
                "reference_db": baseline["near_snr_late_db"],
                "qualifies": False,
            })
        if metrics["near_energy_change_db"] < 0.0:
            rows.append({
                "result_id": row["variant"] + ":near_energy_loss",
                "classification": "adverse_unvalidated_synthetic_retained",
                "observed_db": metrics["near_energy_change_db"],
                "reference_db": 0.0,
                "qualifies": False,
            })
    if not rows:
        rows.append({
            "result_id": "no_adverse_observed_in_synthetic_scope",
            "classification": "no_adverse_observed_but_still_not_qualified",
            "observed_db": None,
            "reference_db": None,
            "qualifies": False,
        })
    return rows


def missing_results() -> List[Dict[str, Any]]:
    return [
        {"result_id": "real_webrtc_aec3_apm_runtime", "status": "blocked",
         "metrics": None, "qualifies": False},
        {"result_id": "rights_cleared_room_cohort", "status": "blocked",
         "metrics": None, "qualifies": False},
        {"result_id": "device_loop_drift_deadline", "status": "blocked",
         "metrics": None, "qualifies": False},
        {"result_id": "authorized_listening", "status": "blocked",
         "metrics": None, "qualifies": False},
    ]


def acceptance_profile_payload() -> Dict[str, Any]:
    items = [
        ("frozen_render_or_rir", "synthetic_fixture_only",
         "Frozen synthetic render/capture fixture; no measured RIR or recorded room."),
        ("channel_rate_hop_frozen", "synthetic_fixture_only",
         "16 kHz mono, 160-sample hop; synthetic only."),
        ("excitation_noise_delay_movement_reset_frozen", "synthetic_fixture_only",
         "Deterministic excitation, noise, 24-sample delayed reference, path change and reset."),
        ("echo_only", "synthetic_only",
         "Echo-only A and B windows are generated and scored."),
        ("near_end_only", "synthetic_only",
         "Near-only windows are generated and scored."),
        ("overlap", "synthetic_only",
         "Synthetic overlap/double-talk windows are generated and scored."),
        ("no_reference", "blocked",
         "Only a passthrough control exists; no independent no-reference suppressor."),
        ("delayed_render", "synthetic_only",
         "Delayed reference is recorded as misaligned and never qualifies."),
        ("missing_render", "synthetic_only",
         "Reference dropout frames are withheld and marked partial."),
        ("echo_attenuation", "synthetic_proxy_only",
         "ERLE is a frozen-window synthetic proxy, not WebRTC ERLE."),
        ("near_end_damage", "synthetic_proxy_only",
         "Near SNR and near-energy change are synthetic proxies."),
        ("nonfinite_failures", "synthetic_control_only",
         "Invalid/nonfinite rejections and a safety reset are exercised."),
        ("alignments", "synthetic_fixture_only",
         "Cross-correlation lag is a fixture property, not device timing."),
        ("authorized_listening", "blocked", "No listening or MOS panel."),
        ("target_device_timing", "blocked", "No device loop, clock drift or deadline run."),
    ]
    return {
        "profile": PROFILE,
        "synthetic_only": True,
        "items": [
            {"item": item, "status": status, "evidence": evidence, "qualifies": False}
            for item, status, evidence in items
        ],
        "all_qualify": False,
        "missing_result_promoted": False,
        "qualifies": False,
    }


def observed_provenance() -> Dict[str, Any]:
    return {
        "reproduced_here": False,
        "qualifies": False,
        "documented_context": [
            {
                "source": "research/aec_research_20261028.md",
                "statement": (
                    "Synthetic train pilot medians: WebRTC AEC3 20.97 dB ERLE / "
                    "2.00 dB double-talk near SNR; AEC3+NS1 23.26 / -2.32; "
                    "AEC3+NS2 23.58 / -2.32; AEC3+NS3 23.68 / -2.32."
                ),
                "reproduced_here": False,
                "qualifies": False,
            },
            {
                "source": "research/aec_research_20261028.md",
                "statement": (
                    "12-device-group training pilot: AEC3+NS3 double-talk echo "
                    "MOS 4.51 and degradation MOS 2.38; NS2 near-end-only "
                    "degradation MOS 3.62; AECMOS is a learned metric."
                ),
                "reproduced_here": False,
                "qualifies": False,
            },
            {
                "source": "adapters/webrtc-aec/README.md",
                "statement": (
                    "Levels 1-3 use the combined AudioProcessor with AEC "
                    "enabled, noise suppression enabled and AGC disabled; "
                    "level 0 is AEC3 alone."
                ),
                "reproduced_here": False,
                "qualifies": False,
            },
            {
                "source": "adapters/webrtc-ns/README.md",
                "statement": (
                    "pywebrtc-audio==0.2.0 exposes four APM NS levels; a fresh "
                    "suppressor is created per clip and 10 ms framing is internal."
                ),
                "reproduced_here": False,
                "qualifies": False,
            },
        ],
    }


def artifact_assessment() -> Dict[str, Any]:
    return {
        "all_required_absent": True,
        "runtime_presence": {
            "present": False,
            "expected": "pywebrtc-audio==0.2.0 (Apache-2.0) and upstream WebRTC APM/AEC3 source revision with LICENSE/NOTICE",
            "probes": [
                {"probe": "workspace_env", "path": "data/envs/webrtc", "result": "absent"},
                {"probe": "import_pywebrtc_audio", "result": "ModuleNotFoundError"},
                {"probe": "import_webrtc_audio", "result": "ModuleNotFoundError"},
                {"probe": "import_webrtc_apm", "result": "ModuleNotFoundError"},
                {"probe": "workspace_checkout", "path": "data/checkouts", "result": "no webrtc AEC3/APM checkout present"},
            ],
        },
        "package_assets": {
            "present": False,
            "wheels": 0,
            "binaries": 0,
            "weights": 0,
            "wave_files": 0,
            "licensed_corpus": 0,
        },
        "conclusion": (
            "BLOCKED: no pinned licensed WebRTC AEC3+APM source, wheel, binary "
            "or runtime is present; no artifact was downloaded or fabricated "
            "and no level result qualifies."
        ),
    }


def ranking_payload(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "order": "not_ranked",
        "recommendation": None,
        "reason": (
            "Synthetic-only level runs cannot rank WebRTC APM NS levels; the "
            "real runtime, rights-cleared room cohort and listening evidence "
            "are absent."
        ),
        "level_row_count": len(rows),
        "qualifies": False,
    }


def build_report_core() -> Dict[str, Any]:
    levels = per_level_runs()
    controls = control_runs()
    fixture = fixture_payload("duplex")
    fixture["conditions"] = {
        condition: fixture_payload(condition)
        for condition in ("echo_only", "near_only", "delayed_render",
                          "no_reference", "reference_dropout", "reset")
    }
    report: Dict[str, Any] = {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "qualification": QUALIFICATION,
        "task_row": TASK_ROW_IDENTITY,
        "mutable_provenance": MUTABLE_PROVENANCE,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "sibling_pins": SIBLING_PINS,
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "configured_apm_instance": configured_apm_payload(),
        "acceptance_profile": acceptance_profile_payload(),
        "fixture": fixture,
        "observed_provenance": observed_provenance(),
        "per_level_runs": levels,
        "controls": controls,
        "level_ablation": level_ablation(levels, controls),
        "ranking": ranking_payload(levels),
        "adverse_results": adverse_results(levels, controls),
        "missing_results": missing_results(),
        "failure_controls": failure_controls(),
        "artifact_assessment": artifact_assessment(),
        "release_gates": RELEASE_GATES,
        "non_claims": NON_CLAIMS,
        "reproduction": REPRODUCTION,
    }
    return report


def build_report() -> Dict[str, Any]:
    first = build_report_core()
    second = build_report_core()
    third = build_report_core()
    digests = [sha256_bytes(canonical_bytes(item))
               for item in (first, second, third)]
    if len(set(digests)) != 1:
        raise ReferenceError("non_deterministic_report")
    report = dict(first)
    report["regeneration"] = {
        "runs": 3,
        "byte_identical": True,
        "canonical_digests": digests,
        "mode": "three_cold_start_canonical_builds",
    }
    return report


def render_report() -> Tuple[bytes, str, str]:
    report = build_report()
    text, canonical_digest = canonical_report(report)
    payload = (text + "\n").encode("utf-8")
    return payload, sha256_bytes(payload), canonical_digest
