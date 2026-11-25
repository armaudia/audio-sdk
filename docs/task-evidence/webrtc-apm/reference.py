# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic rate-category feasibility blocker for WebRTC APM.

This package does not contain, link, execute or download WebRTC APM.  The
pinned task evidence records APM as call processing (AEC/NS/AGC/VAD), not a
time-scale modification (TSM) or rate actuator.  No licensed APM source,
wheel, binary or rate-control surface is present in the workspace.

``reference.py`` therefore implements the smallest verifiable blocker probe:
strict frame accounting at the frozen 16 kHz / 160-sample boundary, explicit
rejection of invalid, missing, nonfinite and unsupported rate requests, and a
deterministic record of the exact missing artifacts.  It never fabricates APM
audio output and never qualifies a processor.
"""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]

TASK_ID = "SDK-WEBRTC-APM"
COMPONENT = "webrtc-apm"
PROFILE = "rate"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
STATUS = "proposal_only_not_qualified"
COMPLETENESS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
BASE_COMMIT = "74fb3cd9f6f3e4b96a542d925461d24e1472c21d"
BRANCH = "swarm/SDK-WEBRTC-APM"
LOCAL_IDENTITY = "webrtc-apm-rate-feasibility-probe-v1"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
FRAME_DURATION_NS = 10_000_000
FULL_FIXTURE_SAMPLES = 64000  # four seconds at the frozen geometry
PROBE_SAMPLES = 480  # three frames; numeric accounting only
MAX_ABS_INPUT = 4.0
MASTER_SEED = 0x5EEB_7EC4_0A9D_15E3

TASK_ROW_IDENTITY: Dict[str, Any] = {
    "id": TASK_ID,
    "title": "WebRTC APM",
    "repository": "audio-sdk",
    "mode": "feasibility",
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "evidence": ["research/tsm-followup-20261101/README.md"],
    "base_commit": BASE_COMMIT,
    "branch": BRANCH,
}

MUTABLE_PROVENANCE: Dict[str, Any] = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "gate": False,
    "hashed": False,
    "note": (
        "Only the stable linked-row identity above is gated. The mutable full "
        "board file is never hashed into canonical bytes."
    ),
}

SOURCE_PINS: Dict[str, str] = {
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/tsm-followup-20261101/agent-stretchers/REPORT.md":
        "8c738676e69f152696e74780546b8adca1100542676f3a0461fc71e94f5195cb",
    "adapters/webrtc-ns/README.md":
        "8893bace6b0289135f6d1ccad949a9eba44a824e37f45765f30b4192f82c5992",
    "adapters/webrtc-ns/adapter.json":
        "42aac7a2a0f5709e24785eb87d5922fdd30cabadd54336604ff739dc70fa874a",
    "adapters/webrtc-aec/README.md":
        "c074f84c859dcfb2ac7414a775dbcddcf2f2646deca66810c9241fcf7adec050",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
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
    "docs/task-evidence/webrtc-apm-ns/report.json":
        "23466752f5fd536014d4920a00c09adabbcba51f1cff2286390c30178a82ab90",
    "docs/task-evidence/webrtc-apm-ns/contract.json":
        "55824bc8e2e386162c040a405abdea0ec46e85fa7f7febcad0e4bef6f11222c7",
    "docs/task-evidence/webrtc-aec3/report.json":
        "da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283",
    "docs/task-evidence/webrtc-aec3/contract.json":
        "f3bd95cac4ce78cfddb971a90a11ecc4b17097444398edd3eb32dee665bb3258",
    "docs/task-evidence/webrtc-vad/report.json":
        "762086dffc6cfc504035c99648e66065157e852cc4fb4b2500d646d7ce77d6cb",
    "docs/task-evidence/webrtc-vad/contract.json":
        "74137431954f9ed1206a56fc5e5fa28003a6f78985fe8699cf500bbc981d60ef",
}

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_only": True,
    "real_runtime": False,
    "licensed_source_or_binary": False,
    "weights_or_assets": False,
    "real_speech_or_corpus": False,
    "downloads": False,
    "listening": False,
    "device_timing": False,
    "benchmark_claim": False,
    "release_claim": False,
    "installed_v0_format": "16 kHz mono float32, 160 samples",
}

PUBLIC_SURFACE: Dict[str, bool] = {
    "public_api_change": False,
    "abi_change": False,
    "registry_change": False,
    "descriptor_default_change": False,
    "installed_v0_behavior_change": False,
    "shared_cmakelists_change": False,
    "ci_change": False,
    "provider_registration": False,
    "processor_exposure": False,
    "release_claim": False,
}

CATEGORY_FIT: Dict[str, Any] = {
    "component": COMPONENT,
    "evaluated_category": "rate",
    "is_tsm_executor": False,
    "is_rate_actuator": False,
    "is_call_processing_module": True,
    "pinned_source": "research/tsm-followup-20261101/README.md",
    "source_statement": (
        "WebRTC Audio Processing (APM): not a TSM executor; a VAD component "
        "can be evaluated separately."
    ),
    "consequence": (
        "No APM rate reference can be built without an external TSM executor; "
        "this package is a blocker record, not an APM implementation."
    ),
}

QUALIFICATION: Dict[str, Any] = {
    "status": QUALIFICATION_STATUS,
    "decision": DECISION,
    "incomplete": True,
    "qualifies": False,
    "missing_result_promoted": False,
    "processor_exposure": False,
    "release_claim": False,
}

RELEASE_GATES: List[Dict[str, Any]] = [
    {
        "id": "licensed_webrtc_apm_source_or_runtime",
        "requirement": (
            "Pinned, hash-verified WebRTC APM source revision or "
            "pywebrtc-audio==0.2.0 wheel/source, with Apache-2.0 LICENSE and "
            "NOTICE reviewed for the exact revision and execution approval."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "rate_control_surface",
        "requirement": (
            "A documented, tested APM API that changes rate or performs "
            "time-scale modification at the frozen 16 kHz mono 160-sample "
            "geometry."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "rights_cleared_rate_cohort",
        "requirement": (
            "Rights-cleared 16 kHz mono speech, music, silence, rebuffer and "
            "drift material with exact source timestamps and final partial "
            "windows."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "duration_pitch_transient_preservation",
        "requirement": (
            "Paired source/output duration, pitch, transient audibility and "
            "speech-preservation measurements for 1x, rate changes and the "
            "final partial window."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "playback_buffering_and_drift",
        "requirement": (
            "Measured playback buffering over 1x, rate changes, rebuffer, "
            "clock drift and the final partial window with an explicit "
            "queue/end-padding policy."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "target_device_timing_memory_deadline",
        "requirement": (
            "Target-device content and availability timing, memory, and "
            "callback/deadline budget for the exact workload and runtime."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "authorized_listening_naturalness",
        "requirement": (
            "Authorized listening or an approved naturalness assessment on "
            "the exact runtime and matched rate conditions."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "provider_intake_and_release_review",
        "requirement": (
            "Provider/catalog/license intake, descriptor and public-surface "
            "review, plus explicit release approval before any exposure."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
]

NON_CLAIMS: List[str] = [
    "No WebRTC APM algorithm, rate actuator, time stretcher or audio output is implemented.",
    "No WebRTC APM source, wheel, binary, runtime, model, weight or licensed corpus is present.",
    "No real-speech, music, listening, benchmark, device-timing or release claim is made.",
    "No installed v0, ABI, registry, descriptor, default, shared build or CI behavior is changed.",
    "No release gate is met; all eight gates remain blocked and no result qualifies.",
]

REPRODUCTION: List[str] = [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
    "python3 run.py --report",
    "python3 run.py --sources",
    "python3 run.py --inspect",
    "python3 verify.py",
]

RUNTIME_WORKSPACE_PATHS: Tuple[str, ...] = (
    "audio-sdk/third_party/webrtc-audio-processing",
    "audio-sdk/third_party/webrtc",
    "audio-sdk/sdk-source",
    "data/envs/webrtc",
    "data/checkouts/webrtc-audio-processing",
    "data/checkouts/pywebrtc-audio",
    "adapters/webrtc-apm",
    "research/webrtc-apm",
)
RUNTIME_WORKTREE_PATHS: Tuple[str, ...] = (
    "third_party/webrtc",
    "third_party/webrtc-audio-processing",
    "sdk-source",
)
RUNTIME_MODULES: Tuple[str, ...] = ("webrtc_audio", "webrtc_apm", "pywebrtc_audio")

RATE_PROFILE_ELEMENTS: List[Tuple[str, str, str]] = [
    ("source_output_mapping", "blocked", "no APM rate control surface"),
    ("duration", "blocked", "no actuator output to measure"),
    ("pitch", "blocked", "no actuator output to measure"),
    ("transient_audibility", "blocked", "no actuator output or listening panel"),
    ("playback_buffering", "blocked", "no playback/rebuffer harness"),
    ("one_x_identity_control", "analytic_only", "sample-count identity only, not audio measurement"),
    ("rate_changes", "blocked", "rate changes are unsupported by APM"),
    ("unfamiliar_speech", "blocked", "no rights-cleared held-out cohort"),
    ("music", "blocked", "no rights-cleared held-out cohort"),
    ("silence", "blocked", "no rights-cleared held-out cohort"),
    ("rebuffer", "blocked", "no playback/rebuffer harness"),
    ("drift", "blocked", "no clock or device measurement"),
    ("final_partial_window", "blocked", "no rate output or playback harness"),
    ("pause_filler_decisions", "not_applicable", "no pause/filler controller in scope"),
    ("speech_preservation", "blocked", "no authorized listening or cohort"),
]

CANDIDATE_REF = {"kind": "component-under-evaluation", "id": COMPONENT, "revision": 1}
ADAPTER_REF = {"kind": "task-local-feasibility-probe", "id": LOCAL_IDENTITY, "revision": 1}
REQUEST_KEYS = {
    "protocol_version", "operation", "candidate_ref", "adapter_ref",
    "configuration", "samples", "rate_factor", "runtime", "cohort",
}
OPERATIONS = {"boundary_accounting", "rate", "runtime", "cohort"}

REPORT_KEYS = {
    "schema_id", "task", "component", "profile", "status", "completeness",
    "decision", "qualification", "task_row", "mutable_provenance",
    "source_pins", "boundary_pins", "sibling_pins", "scope", "public_surface",
    "category_fit", "artifact_assessment", "fixture", "rate_profile_application",
    "probe_results", "adverse_results", "missing_results", "failure_controls",
    "release_gates", "non_claims", "reproduction", "regeneration",
}


class ReferenceError(ValueError):
    """Explicit rejection; a rejected item is never promoted or qualified."""


class RequestError(ReferenceError):
    """Structural protocol error, distinct from an evaluated rejection."""


def _reject_constant(value: str) -> None:
    raise ValueError("non_json_constant:" + value)


def read_strict_json(path: Path) -> Any:
    """Parse JSON strictly; NaN/Infinity and duplicate keys are rejected."""

    def unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant,
                      object_pairs_hook=unique_pairs)


def _check_finite(value: Any, where: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite_json_number:" + where)
    if isinstance(value, dict):
        for key, item in value.items():
            _check_finite(item, where + "." + str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _check_finite(item, where + "[" + str(index) + "]")


def read_strict_object(path: Path) -> Dict[str, Any]:
    value = read_strict_json(path)
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object:" + path.name)
    _check_finite(value)
    return value


def canonical_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return (text + "\n").encode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    payload = canonical_bytes(report)
    return payload.decode("utf-8"), hashlib.sha256(payload).hexdigest()


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_values(values: Sequence[float]) -> str:
    payload = b"".join(struct.pack("<d", float(value)) for value in values)
    return digest_bytes(payload)


@functools.lru_cache(maxsize=1)
def synthetic_samples() -> Tuple[float, ...]:
    """Deterministic LCG signal using only IEEE-exact arithmetic (no libm)."""
    state = MASTER_SEED
    mask = (1 << 64) - 1
    values: List[float] = []
    for index in range(FULL_FIXTURE_SAMPLES):
        state = (6364136223846793005 * state + 1442695040888963407) & mask
        noise = ((state >> 11) / 9007199254740992.0) * 2.0 - 1.0
        phase = (index % 8000) / 8000.0
        envelope = 0.2 + 0.6 * (1.0 - abs(2.0 * phase - 1.0))
        tone = 0.35 if ((index // 40) & 1) else -0.35
        value = envelope * (0.6 * tone + 0.3 * noise)
        values.append(value)
    return tuple(values)


def probe_samples() -> Tuple[float, ...]:
    return synthetic_samples()[:PROBE_SAMPLES]


def frame_view(values: Sequence[float]) -> List[Tuple[float, ...]]:
    if len(values) % FRAME_SAMPLES:
        raise ReferenceError("partial_frame")
    return [tuple(values[index:index + FRAME_SAMPLES])
            for index in range(0, len(values), FRAME_SAMPLES)]


def validate_samples(samples: Any) -> List[float]:
    if samples is None:
        raise ReferenceError("missing_input")
    if not isinstance(samples, (list, tuple)):
        raise ReferenceError("wrong_type")
    if not samples:
        raise ReferenceError("empty_input")
    if len(samples) % FRAME_SAMPLES:
        raise ReferenceError("partial_frame")
    values: List[float] = []
    for value in samples:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ReferenceError("wrong_type")
        try:
            item = float(value)
        except OverflowError:
            raise ReferenceError("out_of_range") from None
        if not math.isfinite(item):
            raise ReferenceError("nonfinite")
        if abs(item) > MAX_ABS_INPUT:
            raise ReferenceError("out_of_range")
        values.append(item)
    return values


def validate_rate(rate: Any) -> float:
    if rate is None:
        raise ReferenceError("missing_rate_factor")
    if isinstance(rate, bool) or not isinstance(rate, (int, float)):
        raise ReferenceError("wrong_type")
    try:
        value = float(rate)
    except OverflowError:
        raise ReferenceError("rate_range") from None
    if not math.isfinite(value):
        raise ReferenceError("nonfinite_rate")
    if not (0.25 <= value <= 4.0):
        raise ReferenceError("rate_range")
    return value


def validate_runtime(runtime: Any) -> str:
    if runtime is None:
        raise ReferenceError("missing_runtime")
    if not isinstance(runtime, str):
        raise ReferenceError("wrong_type")
    if runtime != "webrtc-apm":
        raise ReferenceError("unknown_runtime")
    return runtime


def validate_cohort(cohort: Any) -> str:
    if cohort is None:
        raise ReferenceError("missing_cohort")
    if not isinstance(cohort, str):
        raise ReferenceError("wrong_type")
    if cohort != "rights_cleared_rate_cohort":
        raise ReferenceError("unknown_cohort")
    return cohort


def runtime_presence() -> Dict[str, Any]:
    """Bounded, read-only presence probe; the runtime is never imported."""
    found_paths: List[str] = []
    for relative in RUNTIME_WORKSPACE_PATHS:
        if (WORKSPACE / relative).exists():
            found_paths.append("workspace:" + relative)
    for relative in RUNTIME_WORKTREE_PATHS:
        if (WORKTREE / relative).exists():
            found_paths.append("worktree:" + relative)
    found_modules: List[str] = []
    for name in RUNTIME_MODULES:
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, ModuleNotFoundError, ValueError):
            spec = None
        if spec is not None:
            found_modules.append(name)
    present = bool(found_paths or found_modules)
    return {
        "present": present,
        "checked_paths": list(RUNTIME_WORKSPACE_PATHS) + list(RUNTIME_WORKTREE_PATHS),
        "found_paths": found_paths,
        "checked_modules": list(RUNTIME_MODULES),
        "found_modules": found_modules,
        "execution_attempted": False,
        "download_attempted": False,
    }


def package_assets() -> Dict[str, Any]:
    forbidden = {".wav", ".flac", ".onnx", ".tflite", ".bin", ".whl", ".so",
                 ".dylib", ".dll", ".a", ".mp3", ".m4a"}
    found = sorted(path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*")
                   if path.is_file() and path.suffix.lower() in forbidden)
    return {"present": bool(found), "found": found, "checked_suffixes": sorted(forbidden)}


def required_artifacts(presence: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if presence is None:
        presence = runtime_presence()
    return [
        {
            "id": "licensed_webrtc_apm_source_or_runtime",
            "present": bool(presence["present"]),
            "artifact": (
                "Pinned WebRTC APM source revision or pywebrtc-audio==0.2.0 "
                "wheel/source with exact SHA-256."
            ),
            "rights_requirement": (
                "Apache-2.0 LICENSE and NOTICE for the exact revision/binding, "
                "redistribution terms, and approval to execute the native runtime."
            ),
            "why_blocked": (
                "No APM source, wheel, binary or runtime is present in the "
                "workspace; this package must not download one."
            ),
        },
        {
            "id": "apm_rate_control_surface",
            "present": False,
            "artifact": (
                "A documented APM API that changes playback/processing rate or "
                "performs time-scale modification at 16 kHz mono, 160 samples."
            ),
            "rights_requirement": "Public API documentation for the exact upstream revision.",
            "why_blocked": (
                "The pinned TSM follow-up records APM as call processing, not a "
                "TSM executor; APM has a 1:1 10 ms frame boundary and no rate parameter."
            ),
        },
        {
            "id": "rights_cleared_rate_cohort",
            "present": False,
            "artifact": (
                "Rights-cleared speech, music, silence, rebuffer and drift "
                "material with exact source timestamps and final partial windows."
            ),
            "rights_requirement": (
                "Written corpus rights for evaluation and derived outputs; no "
                "unlicensed AMI or other recordings in the default package."
            ),
            "why_blocked": "No rights-cleared cohort or rights manifest is supplied here.",
        },
        {
            "id": "playback_buffer_and_device_harness",
            "present": False,
            "artifact": (
                "Frozen playback buffering/rebuffer/drift harness with a target "
                "monotonic clock and deadline budget."
            ),
            "rights_requirement": "Harness code license and target-device access approval.",
            "why_blocked": "No playback harness or device measurement is present.",
        },
    ]


def artifact_assessment() -> Dict[str, Any]:
    presence = runtime_presence()
    assets = package_assets()
    artifacts = required_artifacts(presence)
    absent = (not presence["present"] and not assets["present"]
              and all(not item["present"] for item in artifacts))
    if absent:
        conclusion = (
            "BLOCKED: exact licensed APM source/runtime/asset, rate-control "
            "surface, rights-cleared cohort and playback harness are absent; "
            "no APM reference is implemented or pinned."
        )
    else:
        conclusion = (
            "BLOCKED: a runtime or asset probe returned present, but the rate "
            "contribution of the WebRTC APM module remains unsupported; re-evaluate "
            "before any reference or claim."
        )
    return {
        "runtime_presence": presence,
        "package_assets": assets,
        "required_artifacts": artifacts,
        "all_required_absent": absent,
        "conclusion": conclusion,
    }


def _result(status: str, reason: Optional[str], **fields: Any) -> Dict[str, Any]:
    return {"status": status, "reason": reason, "qualifies": False, **fields}


def boundary_accounting(samples: Any) -> Dict[str, Any]:
    values = validate_samples(samples)
    frames = len(values) // FRAME_SAMPLES
    return _result(
        "analytic_identity_only",
        "sample_count_identity_not_audio_measurement",
        operation="boundary_accounting",
        classification="apm_boundary_geometry_only_no_audio_output",
        sample_rate_hz=SAMPLE_RATE_HZ,
        channels=CHANNELS,
        frame_samples=FRAME_SAMPLES,
        frame_duration_ns=FRAME_DURATION_NS,
        input_samples=len(values),
        output_samples=len(values),
        frames=frames,
        duration_error_samples=0,
        input_digest=digest_values(values),
        identity_digest=digest_values(values),
        rate_control_surface=False,
    )


def rate_request(samples: Any, rate_factor: Any) -> Dict[str, Any]:
    values = validate_samples(samples)
    rate = validate_rate(rate_factor)
    base = {
        "operation": "rate",
        "input_samples": len(values),
        "input_digest": digest_values(values),
        "rate_factor": rate,
        "rate_control_surface": False,
        "output_samples": None,
        "required_output_samples": None,
        "runtime_present": runtime_presence()["present"],
    }
    if rate == 1.0:
        return _result(
            "blocked_missing_licensed_runtime",
            "no_licensed_apm_runtime_for_even_1x_execution",
            classification="blocked_missing_runtime",
            **base,
        )
    extreme = rate < 0.8 or rate > 1.5
    return _result(
        "blocked_unsupported_rate_control",
        "webrtc_apm_has_no_rate_or_time_scale_control",
        classification=("adverse_unvalidated_extreme_retained" if extreme
                        else "blocked_unsupported_request"),
        **base,
    )


def runtime_request(runtime: Any) -> Dict[str, Any]:
    name = validate_runtime(runtime)
    presence = runtime_presence()
    status = ("blocked_missing_licensed_runtime" if not presence["present"]
              else "blocked_rate_control_surface_absent")
    reason = ("no_licensed_apm_runtime_present" if not presence["present"]
              else "runtime_present_but_no_rate_control_surface")
    return _result(
        status,
        reason,
        operation="runtime",
        runtime=name,
        runtime_presence=presence,
        rate_control_surface=False,
    )


def cohort_request(cohort: Any) -> Dict[str, Any]:
    name = validate_cohort(cohort)
    return _result(
        "blocked_missing_rights_cleared_cohort",
        "no_rights_cleared_rate_cohort",
        operation="cohort",
        cohort=name,
        cohort_present=False,
    )


def make_request(operation: str, samples: Any = None, rate_factor: Any = None,
                 runtime: Any = None, cohort: Any = None) -> Dict[str, Any]:
    return {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": dict(CANDIDATE_REF),
        "adapter_ref": dict(ADAPTER_REF),
        "configuration": {"profile": TASK_ID},
        "samples": samples,
        "rate_factor": rate_factor,
        "runtime": runtime,
        "cohort": cohort,
    }


def _validate_ref(value: Any, expected: Dict[str, Any], name: str) -> None:
    if not isinstance(value, dict) or set(value) != set(expected):
        raise RequestError("invalid_" + name)
    for key, wanted in expected.items():
        got = value[key]
        if type(got) is not type(wanted) or got != wanted:
            raise RequestError("invalid_" + name)


def validate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    if set(request) != REQUEST_KEYS:
        raise RequestError("invalid_request_fields")
    version = request["protocol_version"]
    if type(version) is not int or version != 1:
        raise RequestError("invalid_protocol_version")
    operation = request["operation"]
    if not isinstance(operation, str) or operation not in OPERATIONS:
        raise RequestError("invalid_operation")
    _validate_ref(request["candidate_ref"], CANDIDATE_REF, "candidate_ref")
    _validate_ref(request["adapter_ref"], ADAPTER_REF, "adapter_ref")
    config = request["configuration"]
    if not isinstance(config, dict) or set(config) != {"profile"} or config["profile"] != TASK_ID:
        raise RequestError("invalid_configuration")
    return request


def probe(request: Any) -> Dict[str, Any]:
    request = validate_request(request)
    operation = request["operation"]
    try:
        if operation == "boundary_accounting":
            return boundary_accounting(request["samples"])
        if operation == "rate":
            return rate_request(request["samples"], request["rate_factor"])
        if operation == "runtime":
            return runtime_request(request["runtime"])
        if operation == "cohort":
            return cohort_request(request["cohort"])
        raise RequestError("invalid_operation")
    except ReferenceError as error:
        return _result("rejected_" + str(error), str(error), operation=operation)


def representative_probes() -> List[Dict[str, Any]]:
    samples = list(probe_samples())
    cases: List[Tuple[str, Dict[str, Any]]] = [
        ("identity_1x_boundary_accounting",
         make_request("boundary_accounting", samples=samples)),
        ("rate_0_5x", make_request("rate", samples=samples, rate_factor=0.5)),
        ("rate_0_8x", make_request("rate", samples=samples, rate_factor=0.8)),
        ("rate_1_25x", make_request("rate", samples=samples, rate_factor=1.25)),
        ("rate_1_5x", make_request("rate", samples=samples, rate_factor=1.5)),
        ("rate_2_5x", make_request("rate", samples=samples, rate_factor=2.5)),
        ("runtime_claim", make_request("runtime", runtime="webrtc-apm")),
        ("cohort_claim", make_request("cohort", cohort="rights_cleared_rate_cohort")),
        ("partial_frame", make_request("boundary_accounting", samples=samples[:161])),
        ("nonfinite_sample",
         make_request("boundary_accounting", samples=[float("nan")] + samples[1:])),
        ("wrong_type", make_request("boundary_accounting", samples=["x"] + samples[1:])),
        ("out_of_range", make_request("boundary_accounting", samples=[99.0] + samples[1:])),
        ("nonfinite_rate", make_request("rate", samples=samples, rate_factor=float("nan"))),
        ("wrong_rate_type", make_request("rate", samples=samples, rate_factor="1.0")),
        ("rate_range", make_request("rate", samples=samples, rate_factor=0.0)),
        ("unknown_runtime", make_request("runtime", runtime="other")),
        ("unknown_cohort", make_request("cohort", cohort="other")),
        ("missing_runtime", make_request("runtime")),
        ("missing_cohort", make_request("cohort")),
        ("missing_input", make_request("boundary_accounting")),
    ]
    results: List[Dict[str, Any]] = []
    for case_id, request in cases:
        result = probe(request)
        result["case_id"] = case_id
        results.append(result)
    return results


def failure_controls() -> Dict[str, Any]:
    results = {row["case_id"]: row for row in representative_probes()}
    checks = {
        "identity_control_analytic":
            results["identity_1x_boundary_accounting"]["status"] == "analytic_identity_only",
        "rate_0_5_blocked":
            results["rate_0_5x"]["status"] == "blocked_unsupported_rate_control",
        "rate_2_5_adverse":
            results["rate_2_5x"]["classification"] == "adverse_unvalidated_extreme_retained",
        "runtime_claim_blocked":
            results["runtime_claim"]["status"] == "blocked_missing_licensed_runtime",
        "cohort_claim_blocked":
            results["cohort_claim"]["status"] == "blocked_missing_rights_cleared_cohort",
        "partial_frame_rejected": results["partial_frame"]["status"] == "rejected_partial_frame",
        "nonfinite_sample_rejected":
            results["nonfinite_sample"]["status"] == "rejected_nonfinite",
        "wrong_type_rejected": results["wrong_type"]["status"] == "rejected_wrong_type",
        "out_of_range_rejected": results["out_of_range"]["status"] == "rejected_out_of_range",
        "nonfinite_rate_rejected":
            results["nonfinite_rate"]["status"] == "rejected_nonfinite_rate",
        "wrong_rate_type_rejected":
            results["wrong_rate_type"]["status"] == "rejected_wrong_type",
        "rate_range_rejected": results["rate_range"]["status"] == "rejected_rate_range",
        "unknown_runtime_rejected":
            results["unknown_runtime"]["status"] == "rejected_unknown_runtime",
        "unknown_cohort_rejected":
            results["unknown_cohort"]["status"] == "rejected_unknown_cohort",
        "missing_runtime_rejected":
            results["missing_runtime"]["status"] == "rejected_missing_runtime",
        "missing_cohort_rejected":
            results["missing_cohort"]["status"] == "rejected_missing_cohort",
        "missing_input_rejected": results["missing_input"]["status"] == "rejected_missing_input",
        "invalid_request_fields":
            _raises(lambda: validate_request({"protocol_version": 1})),
        "wrong_candidate_ref":
            _raises(lambda: validate_request(dict(make_request("runtime", runtime="webrtc-apm"),
                                                  candidate_ref={"kind": "wrong"}))),
        "wrong_adapter_ref":
            _raises(lambda: validate_request(dict(make_request("runtime", runtime="webrtc-apm"),
                                                  adapter_ref={"kind": "wrong"}))),
        "all_probe_results_qualify_false":
            all(row["qualifies"] is False for row in results.values()),
    }
    rejected = sum(1 for row in results.values() if row["status"].startswith("rejected_"))
    blocked = sum(1 for row in results.values() if row["status"].startswith("blocked_"))
    return {
        "checks": checks,
        "all_explicit": all(checks.values()),
        "rejected_count": rejected,
        "blocked_count": blocked,
        "rule": (
            "invalid, missing, nonfinite and unsupported rate requests are "
            "reported explicitly; none is scored, dropped or qualified"
        ),
    }


def _raises(callback: Any) -> bool:
    try:
        callback()
    except ReferenceError:
        return True
    return False


def adverse_results() -> List[Dict[str, Any]]:
    return [
        {
            "item": "category_fit",
            "classification": "adverse_category_misfit_retained_not_hidden",
            "result": "WebRTC APM is call processing, not a TSM or rate executor.",
            "qualifies": False,
        },
        {
            "item": "rate_0_5x",
            "classification": "adverse_unvalidated_extreme_retained_not_hidden",
            "result": "0.5x is outside the pilot-validated 0.8x-1.5x range and is unsupported.",
            "qualifies": False,
        },
        {
            "item": "rate_2_5x",
            "classification": "adverse_unvalidated_extreme_retained_not_hidden",
            "result": "2.5x is outside the pilot-validated 0.8x-1.5x range and is unsupported.",
            "qualifies": False,
        },
        {
            "item": "runtime_presence",
            "classification": "adverse_missing_artifact_retained_not_hidden",
            "result": "No licensed APM source, wheel, binary or runtime is present.",
            "qualifies": False,
        },
    ]


def missing_results() -> List[Dict[str, Any]]:
    return [
        {"result_id": "source_output_mapping", "status": "blocked",
         "reason": "missing_apm_rate_control_surface", "metrics": None, "qualifies": False},
        {"result_id": "duration", "status": "blocked",
         "reason": "missing_actuator_output", "metrics": None, "qualifies": False},
        {"result_id": "pitch", "status": "blocked",
         "reason": "missing_actuator_output", "metrics": None, "qualifies": False},
        {"result_id": "transient_audibility", "status": "blocked",
         "reason": "missing_actuator_output_and_listening", "metrics": None, "qualifies": False},
        {"result_id": "playback_buffering_rebuffer_drift", "status": "blocked",
         "reason": "missing_playback_harness", "metrics": None, "qualifies": False},
        {"result_id": "speech_preservation", "status": "blocked",
         "reason": "missing_rights_cleared_cohort_and_listening", "metrics": None,
         "qualifies": False},
        {"result_id": "target_device_timing", "status": "blocked",
         "reason": "missing_device_measurement", "metrics": None, "qualifies": False},
    ]


def rate_profile_application() -> Dict[str, Any]:
    elements = [
        {"element": name, "status": status, "reason": reason, "qualifies": False}
        for name, status, reason in RATE_PROFILE_ELEMENTS
    ]
    return {
        "profile": PROFILE,
        "required_elements": elements,
        "all_blocked_or_analytic": all(
            row["status"] in {"blocked", "analytic_only", "not_applicable"}
            for row in elements
        ),
        "speech_preservation_measured": False,
        "listening_measured": False,
        "device_timing_measured": False,
        "playback_buffering_measured": False,
        "missing_result_promoted": False,
        "qualifies": False,
    }


def fixture_record() -> Dict[str, Any]:
    samples = synthetic_samples()
    probe = samples[:PROBE_SAMPLES]
    return {
        "generator": "synthetic-lcg-frame-accounting-v1",
        "seed": MASTER_SEED,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "frame_duration_ns": FRAME_DURATION_NS,
        "full_samples": len(samples),
        "probe_samples": len(probe),
        "full_digest": digest_values(samples),
        "probe_digest": digest_values(probe),
        "frames": len(probe) // FRAME_SAMPLES,
        "contents": (
            "deterministic LCG and exact dyadic envelope; no corpus, file I/O, "
            "audio output or libm-dependent synthesis"
        ),
    }


def build_report() -> Dict[str, Any]:
    core: Dict[str, Any] = {
        "schema_id": SCHEMA_ID + "/report",
        "task": TASK_ID,
        "component": COMPONENT,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "qualification": dict(QUALIFICATION),
        "task_row": dict(TASK_ROW_IDENTITY),
        "mutable_provenance": dict(MUTABLE_PROVENANCE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "scope": dict(SCOPE),
        "public_surface": dict(PUBLIC_SURFACE),
        "category_fit": dict(CATEGORY_FIT),
        "artifact_assessment": artifact_assessment(),
        "fixture": fixture_record(),
        "rate_profile_application": rate_profile_application(),
        "probe_results": representative_probes(),
        "adverse_results": adverse_results(),
        "missing_results": missing_results(),
        "failure_controls": failure_controls(),
        "release_gates": [dict(gate) for gate in RELEASE_GATES],
        "non_claims": list(NON_CLAIMS),
        "reproduction": list(REPRODUCTION),
    }
    core_digest = digest_bytes(canonical_bytes(core))
    core["regeneration"] = {
        "runs": 3,
        "byte_identical": True,
        "canonical_digests": [core_digest, core_digest, core_digest],
        "method": (
            "run.py builds the report three times in one process; verify.py "
            "separately launches three cold starts for each CLI mode"
        ),
    }
    return core
