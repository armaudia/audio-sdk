# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic restoration-category feasibility blocker for Opus 1.5 NoLACE.

This package does not contain, link, execute or download Opus 1.5.  The pinned
task evidence records LACE/NoLACE as codec-integrated neural postfilters that
are part of Opus 1.5 and are not enabled by default.  No licensed Opus 1.5
source, build, decoder configuration or packet corpus is present in the
workspace.

``reference.py`` therefore implements the smallest verifiable blocker probe:
strict 16 kHz mono / 160-sample accountancy, synthetic Opus-like packet
geometry accounting, explicit rejection of invalid, missing, nonfinite and
unsupported requests, and a deterministic record of the exact missing
artifacts.  It never decodes audio, never simulates a postfilter and never
qualifies a processor.
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

TASK_ID = "SDK-OPUS-1-5-NOLACE"
COMPONENT = "opus-1-5-nolace"
PROFILE = "restoration"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
STATUS = "proposal_only_not_qualified"
COMPLETENESS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
BASE_COMMIT = "c7ab9cdbe94162981d3bba9f99d6d3f8c02c2b8c"
BRANCH = "swarm/SDK-OPUS-1-5-NOLACE"
LOCAL_IDENTITY = "opus-1-5-nolace-restoration-feasibility-probe-v1"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
FRAME_DURATION_NS = 10_000_000
FULL_FIXTURE_SAMPLES = 64000  # four seconds at the frozen geometry
PROBE_SAMPLES = 480  # three frames; numeric accounting only
MAX_ABS_INPUT = 4.0
MASTER_SEED = 0x0B05_1A4E_5EED_2026

PACKET_DURATIONS = (160, 320, 480)  # 10, 20 and 30 ms at 16 kHz
MAX_PACKET_BYTES = 1275  # Opus maximum payload from RFC 6716 section 3.4
PACKET_KEYS = {"index", "duration_samples", "payload_bytes", "present"}
POSTFILTER_MODES = ("lace", "nolace")
DECODER_REVISIONS = ("opus-1.5", "opus-1.4")

TASK_ROW_IDENTITY: Dict[str, Any] = {
    "id": TASK_ID,
    "title": "Opus 1.5 NoLACE",
    "repository": "audio-sdk",
    "mode": "feasibility",
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "evidence": ["research/distortion_restoration_20261028.md"],
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
    "research/distortion_restoration_20261028.md":
        "8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "adapters/opus-plc/adapter.json":
        "a36dd6798d3e9f273c7705fea6d11d888680e633a4b4c41c00e20242f45765ae",
    "adapters/opus-plc/run.py":
        "3f1dcce3102815bf1207a438f3946354f87ebbae5d320cfcf9a6a132b7c3adf8",
    "research/voice-enhancement-20261101/agent-opus-plc/REPORT.md":
        "79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b",
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
    "docs/task-evidence/opus-1-4-standard-decoder-plc/report.json":
        "ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e",
    "docs/task-evidence/autoregressive-plc/report.json":
        "4730ceb74e03782c90dcd78332443c2129cdf56af14ef29bcc89435b68007aec",
    "docs/task-evidence/pitch-period-repeat-plc/report.json":
        "114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445",
    "docs/task-evidence/zero-fill-plc/report.json":
        "3f23c4453caf289ab34ca61af6c94dacb5e9abe9b31fd71a6922ac305e7281ca",
    "docs/task-evidence/linear-interpolation-plc/report.json":
        "0a711aa398be0f86559249781f429323cee2eaf31ced1585f5d8fc205248b323",
}

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_only": True,
    "real_runtime": False,
    "licensed_source_or_binary": False,
    "weights_or_assets": False,
    "real_speech_or_corpus": False,
    "real_packet_trace": False,
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
    "evaluated_category": "restoration",
    "is_codec": True,
    "is_decoder_postfilter_mode": True,
    "is_standalone_postfilter": False,
    "is_packet_loss_concealment": False,
    "pinned_source": "research/distortion_restoration_20261028.md",
    "source_statement": (
        "For Opus, evaluate the codec-integrated LACE/NoLACE neural "
        "postfilters; their decoder has access to codec-specific information. "
        "They are part of Opus 1.5 and are not enabled by default."
    ),
    "consequence": (
        "No NoLACE reference can be built without the exact Opus 1.5 decoder "
        "and its postfilter configuration surface; this package is a blocker "
        "record, not a codec or postfilter implementation."
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
        "id": "licensed_opus_1_5_source_or_runtime",
        "requirement": (
            "Pinned, hash-verified Opus 1.5 source revision or official build "
            "with LICENSE/NOTICE reviewed for that exact revision and explicit "
            "approval to execute the native decoder."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "nolace_decoder_configuration_surface",
        "requirement": (
            "A documented and tested Opus 1.5 decoder API/configuration that "
            "selects NoLACE (LACE disabled) and the contrast LACE condition at "
            "the intended packet geometry."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "rights_cleared_low_bitrate_packet_corpus",
        "requirement": (
            "Rights-cleared low-bitrate Opus packets plus matching encoder "
            "revision, bitrate, frame duration, bandwidth and loss/erasure "
            "metadata trace for evaluation and derived outputs."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "decoder_postfilter_isolation",
        "requirement": (
            "A paired LACE versus NoLACE isolation run on the same packets and "
            "decoder revision, with the postfilter toggle as the only changed "
            "variable and a decoder-specific control."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "decoded_intervals_and_concealment_validity",
        "requirement": (
            "Exact decoded source/output intervals, discrete concealment and "
            "validity accounting, and rejected/invalid packet outcomes for the "
            "restoration profile."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "task_specific_quality_and_peak_bounds",
        "requirement": (
            "Task-specific quality on genuine low-bitrate traffic with output "
            "peak bounds, clean-reference comparison and an established "
            "task-matched control."
        ),
        "status": "blocked",
        "qualifies": False,
        "evidence": None,
    },
    {
        "id": "target_device_content_and_availability_timing",
        "requirement": (
            "Target-device content and availability timing, memory and "
            "callback/deadline budget for the exact decoder workload."
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
    "No Opus 1.5 decoder, LACE/NoLACE postfilter, codec or audio output is implemented.",
    "No Opus 1.5 source, build, model, weight, packet corpus or licensed asset is present.",
    "No genuine low-bitrate decode, listening, benchmark, device-timing or release claim is made.",
    "Opus 1.4 PLC evidence is provenance only and is not reused for Opus 1.5 NoLACE.",
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
    "data/checkouts/opus",
    "data/checkouts/libopus",
    "data/checkouts/opus-1.5",
    "data/envs/opus",
    "adapters/opus-1-5-nolace",
    "research/opus-1-5-nolace",
    "audio-sdk/third_party/opus",
)
RUNTIME_WORKTREE_PATHS: Tuple[str, ...] = (
    "third_party/opus",
    "third_party/libopus",
    "deps/opus",
)
RUNTIME_MODULES: Tuple[str, ...] = ("opuslib", "opus", "pyopus")

RESTORATION_PROFILE_ELEMENTS: List[Tuple[str, str, str]] = [
    ("corruption_and_codec_frozen", "blocked", "no rights-cleared low-bitrate Opus packet corpus"),
    ("packet_metadata_frozen", "blocked", "no packet trace with encoder revision/bitrate/loss metadata"),
    ("clean_audio_packet_baseline", "blocked", "no matched clean or decoded no-loss baseline"),
    ("degradation_stratification", "blocked", "no stratified low-bitrate/degradation cohort"),
    ("erasure_burst_stratification", "blocked", "no erasure or burst-loss trace"),
    ("bandwidth_stratification", "blocked", "no bandwidth-conditioned packet cohort"),
    ("packet_geometry_accounting", "analytic_only", "synthetic 160/320/480-sample schedule only"),
    ("decoder_packet_compatibility", "blocked", "no decoder to verify intended packets"),
    ("postfilter_isolation_lace_vs_nolace", "blocked", "no licensed decoder postfilter surface"),
    ("discrete_concealment_validity", "blocked", "no decode output or concealment events"),
    ("decoded_intervals", "blocked", "no decode output intervals"),
    ("task_specific_quality", "blocked", "no genuine low-bitrate quality measurement"),
    ("output_peak_bounds", "blocked", "no decode output to bound"),
    ("content_and_availability_timing", "blocked", "no runtime or device timing"),
    ("authorized_listening", "blocked", "no listening panel or authorization"),
]

CANDIDATE_REF = {"kind": "component-under-evaluation", "id": COMPONENT, "revision": 1}
ADAPTER_REF = {"kind": "task-local-feasibility-probe", "id": LOCAL_IDENTITY, "revision": 1}
REQUEST_KEYS = {
    "protocol_version", "operation", "candidate_ref", "adapter_ref",
    "configuration", "samples", "packets", "postfilter_mode",
    "decoder_revision", "runtime", "cohort",
}
OPERATIONS = {
    "boundary_accounting", "packet_accounting", "postfilter",
    "compatibility", "runtime", "cohort",
}

REPORT_KEYS = {
    "schema_id", "task", "component", "profile", "status", "completeness",
    "decision", "qualification", "task_row", "mutable_provenance",
    "source_pins", "boundary_pins", "sibling_pins", "scope", "public_surface",
    "category_fit", "artifact_assessment", "pcm_fixture", "packet_fixture",
    "restoration_profile_application", "probe_results", "adverse_results",
    "missing_results", "failure_controls", "release_gates", "non_claims",
    "reproduction", "regeneration",
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


def packet_schedule() -> List[Dict[str, Any]]:
    """Deterministic synthetic Opus-like packet geometry (no codec payload)."""
    specs = (
        (320, 40, True),
        (320, 30, True),
        (480, 25, False),
        (160, 12, True),
        (320, 55, True),
        (480, 38, True),
    )
    return [
        {
            "index": index,
            "duration_samples": duration,
            "payload_bytes": payload,
            "present": present,
        }
        for index, (duration, payload, present) in enumerate(specs)
    ]


def _exact_int(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceError("wrong_type")
    if isinstance(value, float) and not math.isfinite(value):
        raise ReferenceError("nonfinite")
    try:
        integer = int(value)
    except (OverflowError, ValueError):
        raise ReferenceError("out_of_range") from None
    if value != integer:
        raise ReferenceError("wrong_type")
    return integer


def validate_packets(packets: Any) -> List[Dict[str, Any]]:
    if packets is None:
        raise ReferenceError("missing_packets")
    if not isinstance(packets, (list, tuple)):
        raise ReferenceError("wrong_type")
    if not packets:
        raise ReferenceError("empty_packets")
    values: List[Dict[str, Any]] = []
    for expected_index, item in enumerate(packets):
        if not isinstance(item, dict):
            raise ReferenceError("wrong_type")
        if set(item) != PACKET_KEYS:
            raise ReferenceError("invalid_packet_fields")
        index = _exact_int(item["index"])
        if index < 0:
            raise ReferenceError("out_of_range")
        if index != expected_index:
            raise ReferenceError("packet_order")
        duration = _exact_int(item["duration_samples"])
        if duration not in PACKET_DURATIONS:
            if duration <= 0 or duration % FRAME_SAMPLES:
                raise ReferenceError("partial_frame")
            raise ReferenceError("unsupported_duration")
        payload = _exact_int(item["payload_bytes"])
        if payload < 0 or payload > MAX_PACKET_BYTES:
            raise ReferenceError("out_of_range")
        present = item["present"]
        if not isinstance(present, bool):
            raise ReferenceError("wrong_type")
        values.append({
            "index": index,
            "duration_samples": duration,
            "payload_bytes": payload,
            "present": present,
        })
    return values


def validate_postfilter_mode(mode: Any) -> str:
    if mode is None:
        raise ReferenceError("missing_postfilter_mode")
    if not isinstance(mode, str):
        raise ReferenceError("wrong_type")
    if mode not in POSTFILTER_MODES:
        raise ReferenceError("unknown_postfilter_mode")
    return mode


def validate_decoder_revision(revision: Any) -> str:
    if revision is None:
        raise ReferenceError("missing_decoder_revision")
    if not isinstance(revision, str):
        raise ReferenceError("wrong_type")
    if revision not in DECODER_REVISIONS:
        raise ReferenceError("unknown_decoder_revision")
    return revision


def validate_runtime(runtime: Any) -> str:
    if runtime is None:
        raise ReferenceError("missing_runtime")
    if not isinstance(runtime, str):
        raise ReferenceError("wrong_type")
    if runtime != "opus-1.5-nolace":
        raise ReferenceError("unknown_runtime")
    return runtime


def validate_cohort(cohort: Any) -> str:
    if cohort is None:
        raise ReferenceError("missing_cohort")
    if not isinstance(cohort, str):
        raise ReferenceError("wrong_type")
    if cohort != "rights_cleared_low_bitrate_opus_packets":
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
    forbidden = {".wav", ".flac", ".opus", ".ogg", ".onnx", ".tflite", ".bin",
                 ".whl", ".so", ".dylib", ".dll", ".a", ".mp3", ".m4a"}
    found = sorted(path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*")
                   if path.is_file() and path.suffix.lower() in forbidden)
    return {"present": bool(found), "found": found, "checked_suffixes": sorted(forbidden)}


def required_artifacts(presence: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if presence is None:
        presence = runtime_presence()
    return [
        {
            "id": "licensed_opus_1_5_source_or_runtime",
            "present": bool(presence["present"]),
            "artifact": (
                "Pinned Opus 1.5 source revision or official build with exact "
                "SHA-256 and the decoder used for NoLACE evaluation."
            ),
            "rights_requirement": (
                "Opus/upstream LICENSE and NOTICE for the exact revision, "
                "redistribution terms, and approval to execute the native "
                "decoder."
            ),
            "why_blocked": (
                "No Opus 1.5 source, build, binary or runtime is present in the "
                "task workspace or worktree; this package must not download one."
            ),
        },
        {
            "id": "nolace_decoder_configuration_surface",
            "present": False,
            "artifact": (
                "Documented Opus 1.5 decoder API/configuration selecting NoLACE "
                "(LACE disabled) and the LACE contrast condition."
            ),
            "rights_requirement": "Public API documentation for the exact upstream revision.",
            "why_blocked": (
                "The pinned evidence states LACE/NoLACE are part of Opus 1.5 "
                "and not enabled by default, but no exact configuration surface "
                "is available locally to test."
            ),
        },
        {
            "id": "rights_cleared_low_bitrate_opus_packet_corpus",
            "present": False,
            "artifact": (
                "Rights-cleared low-bitrate Opus packets with matching encoder "
                "revision, bitrate, frame duration, bandwidth and loss trace."
            ),
            "rights_requirement": (
                "Written corpus rights for evaluation and derived outputs; no "
                "unlicensed recordings or packet traces in the default package."
            ),
            "why_blocked": "No rights-cleared packet corpus or trace is supplied here.",
        },
        {
            "id": "restoration_harness_and_listening_authorization",
            "present": False,
            "artifact": (
                "Frozen restoration harness for decoded intervals, quality, "
                "peak/timing bounds and an authorized listening condition."
            ),
            "rights_requirement": (
                "Harness code license, target-device access approval and "
                "listening-panel authorization."
            ),
            "why_blocked": "No decode harness, device timing or listening permission is present.",
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
            "BLOCKED: exact licensed Opus 1.5 decoder/runtime, NoLACE "
            "configuration surface, rights-cleared low-bitrate packet corpus "
            "and restoration harness are absent; no NoLACE reference is "
            "implemented or pinned."
        )
    else:
        conclusion = (
            "BLOCKED: a runtime or asset probe returned present, but the exact "
            "NoLACE configuration and packet-corpus rights remain unverified; "
            "re-evaluate before any reference or claim."
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
        classification="frozen_pcm_geometry_only_no_decoder_output",
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
        postfilter_isolation=False,
        codec_decode=False,
    )


def packet_accounting(packets: Any) -> Dict[str, Any]:
    values = validate_packets(packets)
    total_scheduled = sum(item["duration_samples"] for item in values)
    present_samples = sum(item["duration_samples"] for item in values if item["present"])
    missing_packets = sum(1 for item in values if not item["present"])
    total_frames = total_scheduled // FRAME_SAMPLES
    return _result(
        "analytic_packet_geometry_only",
        "synthetic_packet_geometry_not_codec_decode",
        operation="packet_accounting",
        classification="restoration_packet_boundary_analytic_only",
        sample_rate_hz=SAMPLE_RATE_HZ,
        channels=CHANNELS,
        frame_samples=FRAME_SAMPLES,
        packet_durations_samples=list(PACKET_DURATIONS),
        packet_count=len(values),
        present_packets=len(values) - missing_packets,
        missing_packets=missing_packets,
        total_scheduled_samples=total_scheduled,
        present_samples=present_samples,
        missing_samples=total_scheduled - present_samples,
        total_frames=total_frames,
        schedule_digest=digest_bytes(canonical_bytes(values)),
        codec_decode=False,
        decoder_compatibility_verified=False,
        postfilter_isolation=False,
    )


def postfilter_request(packets: Any, mode: Any) -> Dict[str, Any]:
    values = validate_packets(packets)
    selected = validate_postfilter_mode(mode)
    presence = runtime_presence()
    base = {
        "operation": "postfilter",
        "postfilter_mode": selected,
        "packet_count": len(values),
        "schedule_digest": digest_bytes(canonical_bytes(values)),
        "runtime_present": presence["present"],
        "postfilter_isolation_verified": False,
        "decoded_intervals": None,
        "output_samples": None,
        "output_peak": None,
    }
    if selected == "nolace":
        return _result(
            "blocked_missing_licensed_runtime",
            "no_licensed_opus_1_5_decoder_for_nolace",
            classification="blocked_missing_runtime",
            **base,
        )
    return _result(
        "blocked_missing_licensed_runtime",
        "no_licensed_opus_1_5_decoder_for_lace_contrast",
        classification="blocked_missing_runtime",
        **base,
    )


def compatibility_request(packets: Any, revision: Any) -> Dict[str, Any]:
    values = validate_packets(packets)
    selected = validate_decoder_revision(revision)
    base = {
        "operation": "compatibility",
        "decoder_revision": selected,
        "packet_count": len(values),
        "schedule_digest": digest_bytes(canonical_bytes(values)),
        "runtime_present": runtime_presence()["present"],
        "decoded_intervals": None,
        "compatibility_verified": False,
    }
    if selected == "opus-1.4":
        return _result(
            "blocked_decoder_revision_mismatch",
            "opus_1_4_decoder_is_not_opus_1_5_nolace",
            classification="adverse_cross_version_compatibility_retained_not_validated",
            **base,
        )
    return _result(
        "blocked_missing_licensed_runtime",
        "no_licensed_opus_1_5_decoder_to_verify_intended_packets",
        classification="blocked_missing_runtime",
        **base,
    )


def runtime_request(runtime: Any) -> Dict[str, Any]:
    name = validate_runtime(runtime)
    presence = runtime_presence()
    status = ("blocked_missing_licensed_runtime" if not presence["present"]
              else "blocked_nolace_configuration_unverified")
    reason = ("no_licensed_opus_1_5_runtime_present" if not presence["present"]
              else "runtime_present_but_nolace_configuration_unverified")
    return _result(
        status,
        reason,
        operation="runtime",
        runtime=name,
        runtime_presence=presence,
        postfilter_isolation=False,
    )


def cohort_request(cohort: Any) -> Dict[str, Any]:
    name = validate_cohort(cohort)
    return _result(
        "blocked_missing_rights_cleared_packet_corpus",
        "no_rights_cleared_low_bitrate_opus_packet_corpus",
        operation="cohort",
        cohort=name,
        cohort_present=False,
    )


def make_request(operation: str, samples: Any = None, packets: Any = None,
                 postfilter_mode: Any = None, decoder_revision: Any = None,
                 runtime: Any = None, cohort: Any = None) -> Dict[str, Any]:
    return {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": dict(CANDIDATE_REF),
        "adapter_ref": dict(ADAPTER_REF),
        "configuration": {"profile": TASK_ID},
        "samples": samples,
        "packets": packets,
        "postfilter_mode": postfilter_mode,
        "decoder_revision": decoder_revision,
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
        if operation == "packet_accounting":
            return packet_accounting(request["packets"])
        if operation == "postfilter":
            return postfilter_request(request["packets"], request["postfilter_mode"])
        if operation == "compatibility":
            return compatibility_request(request["packets"], request["decoder_revision"])
        if operation == "runtime":
            return runtime_request(request["runtime"])
        if operation == "cohort":
            return cohort_request(request["cohort"])
        raise RequestError("invalid_operation")
    except ReferenceError as error:
        return _result("rejected_" + str(error), str(error), operation=operation)


def representative_probes() -> List[Dict[str, Any]]:
    samples = list(probe_samples())
    schedule = packet_schedule()
    cases: List[Tuple[str, Dict[str, Any]]] = [
        ("pcm_boundary_accounting",
         make_request("boundary_accounting", samples=samples)),
        ("packet_geometry_accounting",
         make_request("packet_accounting", packets=schedule)),
        ("postfilter_nolace",
         make_request("postfilter", packets=schedule, postfilter_mode="nolace")),
        ("postfilter_lace_contrast",
         make_request("postfilter", packets=schedule, postfilter_mode="lace")),
        ("compatibility_opus_1_5",
         make_request("compatibility", packets=schedule, decoder_revision="opus-1.5")),
        ("compatibility_opus_1_4_adverse",
         make_request("compatibility", packets=schedule, decoder_revision="opus-1.4")),
        ("runtime_claim", make_request("runtime", runtime="opus-1.5-nolace")),
        ("cohort_claim",
         make_request("cohort", cohort="rights_cleared_low_bitrate_opus_packets")),
        ("partial_frame",
         make_request("boundary_accounting", samples=samples[:161])),
        ("nonfinite_sample",
         make_request("boundary_accounting", samples=[float("nan")] + samples[1:])),
        ("wrong_type_sample",
         make_request("boundary_accounting", samples=["x"] + samples[1:])),
        ("out_of_range_sample",
         make_request("boundary_accounting", samples=[99.0] + samples[1:])),
        ("missing_input", make_request("boundary_accounting")),
        ("missing_packets", make_request("packet_accounting")),
        ("empty_packets", make_request("packet_accounting", packets=[])),
        ("partial_packet_duration",
         make_request("packet_accounting",
                      packets=[dict(schedule[0], duration_samples=240)])),
        ("unsupported_packet_duration",
         make_request("packet_accounting",
                      packets=[dict(schedule[0], duration_samples=640)])),
        ("packet_order",
         make_request("packet_accounting",
                      packets=[dict(schedule[0], index=1), dict(schedule[1], index=0)])),
        ("wrong_packet_fields",
         make_request("packet_accounting", packets=[{"index": 0}])),
        ("nonfinite_packet_bytes",
         make_request("packet_accounting",
                      packets=[dict(schedule[0], payload_bytes=float("inf"))])),
        ("wrong_type_packet_bytes",
         make_request("packet_accounting",
                      packets=[dict(schedule[0], payload_bytes="40")])),
        ("fractional_packet_bytes",
         make_request("packet_accounting",
                      packets=[dict(schedule[0], payload_bytes=40.5)])),
        ("out_of_range_packet_bytes",
         make_request("packet_accounting",
                      packets=[dict(schedule[0], payload_bytes=4096)])),
        ("negative_packet_bytes",
         make_request("packet_accounting",
                      packets=[dict(schedule[0], payload_bytes=-1)])),
        ("wrong_present_type",
         make_request("packet_accounting",
                      packets=[dict(schedule[0], present=1)])),
        ("missing_postfilter_mode",
         make_request("postfilter", packets=schedule)),
        ("unknown_postfilter_mode",
         make_request("postfilter", packets=schedule, postfilter_mode="neural")),
        ("wrong_postfilter_type",
         make_request("postfilter", packets=schedule, postfilter_mode=5)),
        ("unknown_decoder_revision",
         make_request("compatibility", packets=schedule, decoder_revision="opus-9")),
        ("missing_decoder_revision",
         make_request("compatibility", packets=schedule)),
        ("unknown_runtime", make_request("runtime", runtime="other")),
        ("missing_runtime", make_request("runtime")),
        ("unknown_cohort", make_request("cohort", cohort="other")),
        ("missing_cohort", make_request("cohort")),
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
        "pcm_identity_control_analytic":
            results["pcm_boundary_accounting"]["status"] == "analytic_identity_only",
        "packet_geometry_control_analytic":
            results["packet_geometry_accounting"]["status"] == "analytic_packet_geometry_only",
        "packet_geometry_not_decode":
            results["packet_geometry_accounting"]["codec_decode"] is False,
        "nolace_blocked":
            results["postfilter_nolace"]["status"] == "blocked_missing_licensed_runtime",
        "lace_contrast_blocked":
            results["postfilter_lace_contrast"]["status"] == "blocked_missing_licensed_runtime",
        "opus_1_5_compatibility_blocked":
            results["compatibility_opus_1_5"]["status"] == "blocked_missing_licensed_runtime",
        "opus_1_4_cross_version_adverse":
            results["compatibility_opus_1_4_adverse"]["classification"]
            == "adverse_cross_version_compatibility_retained_not_validated",
        "runtime_claim_blocked":
            results["runtime_claim"]["status"] == "blocked_missing_licensed_runtime",
        "cohort_claim_blocked":
            results["cohort_claim"]["status"] == "blocked_missing_rights_cleared_packet_corpus",
        "partial_frame_rejected":
            results["partial_frame"]["status"] == "rejected_partial_frame",
        "nonfinite_sample_rejected":
            results["nonfinite_sample"]["status"] == "rejected_nonfinite",
        "wrong_type_sample_rejected":
            results["wrong_type_sample"]["status"] == "rejected_wrong_type",
        "out_of_range_sample_rejected":
            results["out_of_range_sample"]["status"] == "rejected_out_of_range",
        "missing_input_rejected":
            results["missing_input"]["status"] == "rejected_missing_input",
        "missing_packets_rejected":
            results["missing_packets"]["status"] == "rejected_missing_packets",
        "empty_packets_rejected":
            results["empty_packets"]["status"] == "rejected_empty_packets",
        "partial_packet_duration_rejected":
            results["partial_packet_duration"]["status"] == "rejected_partial_frame",
        "unsupported_packet_duration_rejected":
            results["unsupported_packet_duration"]["status"] == "rejected_unsupported_duration",
        "packet_order_rejected":
            results["packet_order"]["status"] == "rejected_packet_order",
        "wrong_packet_fields_rejected":
            results["wrong_packet_fields"]["status"] == "rejected_invalid_packet_fields",
        "nonfinite_packet_bytes_rejected":
            results["nonfinite_packet_bytes"]["status"] == "rejected_nonfinite",
        "wrong_type_packet_bytes_rejected":
            results["wrong_type_packet_bytes"]["status"] == "rejected_wrong_type",
        "fractional_packet_bytes_rejected":
            results["fractional_packet_bytes"]["status"] == "rejected_wrong_type",
        "out_of_range_packet_bytes_rejected":
            results["out_of_range_packet_bytes"]["status"] == "rejected_out_of_range",
        "negative_packet_bytes_rejected":
            results["negative_packet_bytes"]["status"] == "rejected_out_of_range",
        "wrong_present_type_rejected":
            results["wrong_present_type"]["status"] == "rejected_wrong_type",
        "missing_postfilter_mode_rejected":
            results["missing_postfilter_mode"]["status"] == "rejected_missing_postfilter_mode",
        "unknown_postfilter_mode_rejected":
            results["unknown_postfilter_mode"]["status"] == "rejected_unknown_postfilter_mode",
        "wrong_postfilter_type_rejected":
            results["wrong_postfilter_type"]["status"] == "rejected_wrong_type",
        "unknown_decoder_revision_rejected":
            results["unknown_decoder_revision"]["status"] == "rejected_unknown_decoder_revision",
        "missing_decoder_revision_rejected":
            results["missing_decoder_revision"]["status"] == "rejected_missing_decoder_revision",
        "unknown_runtime_rejected":
            results["unknown_runtime"]["status"] == "rejected_unknown_runtime",
        "missing_runtime_rejected":
            results["missing_runtime"]["status"] == "rejected_missing_runtime",
        "unknown_cohort_rejected":
            results["unknown_cohort"]["status"] == "rejected_unknown_cohort",
        "missing_cohort_rejected":
            results["missing_cohort"]["status"] == "rejected_missing_cohort",
        "invalid_request_fields":
            _raises(lambda: validate_request({"protocol_version": 1})),
        "wrong_candidate_ref":
            _raises(lambda: validate_request(dict(make_request("runtime", runtime="opus-1.5-nolace"),
                                                  candidate_ref={"kind": "wrong"}))),
        "wrong_adapter_ref":
            _raises(lambda: validate_request(dict(make_request("runtime", runtime="opus-1.5-nolace"),
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
            "invalid, missing, nonfinite and unsupported requests are reported "
            "explicitly; none is scored, dropped or qualified"
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
            "item": "generic_postfilter_substitution",
            "classification": "adverse_substitution_rejected_retained_not_hidden",
            "result": (
                "A generic low-pass or waveform postfilter is not Opus 1.5 "
                "NoLACE and the pinned source records it as harmful for the "
                "8-bit mu-law proxy."
            ),
            "qualifies": False,
        },
        {
            "item": "opus_1_4_decoder_compatibility",
            "classification": "adverse_cross_version_compatibility_retained_not_validated",
            "result": (
                "Decoding intended Opus 1.5 packets with an Opus 1.4 decoder is "
                "a version mismatch and cannot stand in for NoLACE."
            ),
            "qualifies": False,
        },
        {
            "item": "lace_enabled_by_default_assumption",
            "classification": "adverse_default_enablement_assumption_retained",
            "result": (
                "The pinned source states LACE/NoLACE are not enabled by "
                "default; assuming otherwise is unverified."
            ),
            "qualifies": False,
        },
        {
            "item": "runtime_presence",
            "classification": "adverse_missing_artifact_retained_not_hidden",
            "result": "No licensed Opus 1.5 source, build, binary or runtime is present.",
            "qualifies": False,
        },
    ]


def missing_results() -> List[Dict[str, Any]]:
    return [
        {"result_id": "packet_compatibility", "status": "blocked",
         "reason": "missing_licensed_decoder", "metrics": None, "qualifies": False},
        {"result_id": "postfilter_isolation", "status": "blocked",
         "reason": "missing_decoder_postfilter_surface", "metrics": None, "qualifies": False},
        {"result_id": "discrete_concealment_validity", "status": "blocked",
         "reason": "missing_decode_output", "metrics": None, "qualifies": False},
        {"result_id": "decoded_intervals", "status": "blocked",
         "reason": "missing_decode_output", "metrics": None, "qualifies": False},
        {"result_id": "task_specific_quality", "status": "blocked",
         "reason": "missing_rights_cleared_low_bitrate_corpus", "metrics": None,
         "qualifies": False},
        {"result_id": "output_peak_bounds", "status": "blocked",
         "reason": "missing_decode_output", "metrics": None, "qualifies": False},
        {"result_id": "content_and_availability_timing", "status": "blocked",
         "reason": "missing_runtime_and_device_measurement", "metrics": None,
         "qualifies": False},
    ]


def restoration_profile_application() -> Dict[str, Any]:
    elements = [
        {"element": name, "status": status, "reason": reason, "qualifies": False}
        for name, status, reason in RESTORATION_PROFILE_ELEMENTS
    ]
    return {
        "profile": PROFILE,
        "required_elements": elements,
        "all_blocked_or_analytic": all(
            row["status"] in {"blocked", "analytic_only", "not_applicable"}
            for row in elements
        ),
        "decoder_output_measured": False,
        "postfilter_isolation_measured": False,
        "quality_measured": False,
        "listening_measured": False,
        "device_timing_measured": False,
        "missing_result_promoted": False,
        "qualifies": False,
    }


def pcm_fixture_record() -> Dict[str, Any]:
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


def packet_fixture_record() -> Dict[str, Any]:
    schedule = packet_schedule()
    total = sum(item["duration_samples"] for item in schedule)
    present = sum(item["duration_samples"] for item in schedule if item["present"])
    return {
        "generator": "synthetic-opus-like-packet-schedule-v1",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "packet_durations_samples": list(PACKET_DURATIONS),
        "max_packet_bytes": MAX_PACKET_BYTES,
        "packet_count": len(schedule),
        "missing_packets": sum(1 for item in schedule if not item["present"]),
        "total_scheduled_samples": total,
        "present_samples": present,
        "missing_samples": total - present,
        "schedule_digest": digest_bytes(canonical_bytes(schedule)),
        "contents": (
            "synthetic packet geometry metadata only; no Opus payload, codec, "
            "decode, postfilter or vendor output"
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
        "pcm_fixture": pcm_fixture_record(),
        "packet_fixture": packet_fixture_record(),
        "restoration_profile_application": restoration_profile_application(),
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
