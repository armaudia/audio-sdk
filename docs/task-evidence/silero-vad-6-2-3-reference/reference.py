# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-SILERO-VAD-6-2-3-REFERENCE.

The exact licensed Silero VAD 6.2.3 asset set is incomplete: the official
stateful ONNX graph is present only as an unqualified workspace build
dependency, while the official sequence graph, the pinned PyPI wheel, the
isolated NumPy 2.2.6 / ONNX Runtime 1.24.1 runtime, the complete source
revision, the per-weight rights record, the real analysis cohort and an
approved exact-runtime parity vector are absent.

This module therefore never imports NumPy or ONNX Runtime, never loads or
executes a model, never reads or writes audio, never downloads anything and
never measures a device clock.  It provides two verifiable pieces:

* a bounded, fail-closed ONNX header reader plus caller-supplied-asset
  contract checks, so an exact asset set can be validated without execution;
* a deterministic analysis-profile control that maps caller-supplied
  synthetic frame probabilities to exact half-open sample intervals.

Nothing in this package qualifies the candidate.  The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-SILERO-VAD-6-2-3-REFERENCE"
TITLE = "Silero VAD 6.2.3 reference"
SLUG = "silero-vad-6-2-3-reference"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "d50bf1d324bf2a98607b56c2dccbc72d7f143932"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "analysis"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# Exact upstream pins recorded by the merged Silero evidence packages.
STANDARD_ONNX_SHA256 = (
    "1a153a22f4509e292a94e67d6f9b85e8deb25b4988682b7e174c65279d8788e3")
STANDARD_ONNX_BYTES = 2327524
SEQUENCE_ONNX_SHA256 = (
    "9ccdacc4719d8aa7e45a77536bfabec45a03ba1f2fad5e241ab4060b24238a85")
WHEEL_SHA256 = (
    "7b7f5436cfcb02fae583a05b512ea96467fd449fe54cb49a5e4f06c51a1e43b8")
WHEEL_FILENAME = "silero_vad-6.2.3-py3-none-any.whl"
RUNTIME_LOCK_SHA256 = (
    "3a4f56764ebde51fc1da3e1b82d715488f7649547bc1616fffd0f549d7424528")
ONNXRUNTIME_VERSION = "1.24.1"
NUMPY_VERSION = "2.2.6"
SOURCE_TAG = "v6.2.3"
SOURCE_COMMIT_SHORT = "5cd7945"
SOURCE_COMMIT_PATTERN = re.compile(r"^5cd7945[0-9a-f]{33}$")

STANDARD_MODEL_PATH = "data/models/silero-vad-6.2.3/silero_vad.onnx"
SEQUENCE_MODEL_PATH = (
    "data/models/silero-vad-6.2.3/silero_vad_16k_sequence.onnx")
WHEEL_PATH = (
    "data/wheels/vad-candidates/silero-runtime/" + WHEEL_FILENAME)
RUNTIME_ENV_PATH = "data/envs/silero-vad-6.2.3"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
WHEEL_HASHES_PATH = RUNTIME_ENV_PATH + "/wheel-hashes.txt"
SOURCE_CHECKOUT_PATH = "data/checkouts/silero-vad-6.2.3"
HELDOUT_RESULTS_PATH = "data/runs/vad-chaining-ami-20261031-01/heldout-results.json"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
MODEL_FRAME_SAMPLES = 512
MODEL_CONTEXT_SAMPLES = 64
MODEL_INPUT_SAMPLES = MODEL_CONTEXT_SAMPLES + MODEL_FRAME_SAMPLES
MODEL_STATE_SHAPE = [2, 1, 128]
THRESHOLD = 0.5

TOTAL_FULL_FRAMES = 24
TAIL_PARTIAL_SAMPLES = 37
TOTAL_SAMPLES = TOTAL_FULL_FRAMES * MODEL_FRAME_SAMPLES + TAIL_PARTIAL_SAMPLES
TOTAL_MODEL_FRAMES = (TOTAL_SAMPLES + MODEL_FRAME_SAMPLES - 1) // MODEL_FRAME_SAMPLES

STABLE_TASK_FIELDS = (
    "acceptance",
    "component",
    "deliverable",
    "depends_on",
    "evidence",
    "id",
    "mode",
    "repository",
    "title",
    "write_scope",
)
MUTABLE_TASK_FIELDS = (
    "blocked_reason",
    "dispatch_priority",
    "handoff",
    "owner",
    "review",
    "status",
)

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/plans/F02/vad_sources.md":
        "374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "adapters/silero-vad/adapter.json":
        "45222fd98fe1bd76550d0529cdaa442783807a727880b168d7879eca4f54a60a",
    "adapters/silero-vad/run.py":
        "9f51a7b06440d8f7d0518928a291657803af96a79c0277101e259f870fec05d3",
    "reports/vad-research/attempt-silero-20261028-01/findings.md":
        "83d639d188c37618b3db2ca19454714a3137f35faf1eac89fd7ac489636b0b28",
    "reports/vad-research/attempt-open-models-20261028-01/assessment.md":
        "565d4330d625dd8eec9e607811df300749382feffc87ef54d5e4924e09448ad6",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "cpp-library/cmake/audio_enhance_models.json":
        "6b14470521a1ba599f572e236eb96c877dfe5777341eb402b9224c3eb5feedbe",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
LOCAL_PIN_PATHS = (
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "model_sample_rate_hz": SAMPLE_RATE_HZ,
    "model_channels": CHANNELS,
    "model_sample_format": "f32",
    "model_frame_samples": MODEL_FRAME_SAMPLES,
    "model_context_samples": MODEL_CONTEXT_SAMPLES,
    "model_input_samples": MODEL_INPUT_SAMPLES,
    "model_state_shape": list(MODEL_STATE_SHAPE),
    "threshold": THRESHOLD,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "sdk_callback_invoked": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "real_silero_model": False,
    "release_claim": False,
    "sequence_graph_loaded": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No Silero ONNX graph, checkpoint or derived weight is loaded or executed.",
    "No NumPy, ONNX Runtime or vendor wheel is imported, installed or invoked.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, transcript, annotation or device is consumed.",
    "No VAD accuracy, miss rate, false-alarm rate, latency, memory or RTF is measured here.",
    "The source-reported AMI values are provenance only and are not reproduced.",
    "The synthetic probability trace is a contract control, never model output.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "standard_streaming_onnx",
        "path": STANDARD_MODEL_PATH,
        "filename": "silero_vad.onnx",
        "sha256": STANDARD_ONNX_SHA256,
        "bytes": STANDARD_ONNX_BYTES,
        "graph": "stateful_one_frame_512_with_64_context",
        "required": True,
    },
    {
        "id": "offline_sequence_onnx",
        "path": SEQUENCE_MODEL_PATH,
        "filename": "silero_vad_16k_sequence.onnx",
        "sha256": SEQUENCE_ONNX_SHA256,
        "graph": "sequence_max_512_frames",
        "required": True,
    },
    {
        "id": "official_pypi_wheel",
        "path": WHEEL_PATH,
        "filename": WHEEL_FILENAME,
        "sha256": WHEEL_SHA256,
        "required": True,
        "not_trusted_published": True,
    },
    {
        "id": "isolated_runtime",
        "path": RUNTIME_ENV_PATH,
        "onnxruntime": ONNXRUNTIME_VERSION,
        "numpy": NUMPY_VERSION,
        "required": True,
    },
    {
        "id": "runtime_lock",
        "path": RUNTIME_LOCK_PATH,
        "sha256": RUNTIME_LOCK_SHA256,
        "required": True,
    },
    {
        "id": "full_source_revision",
        "tag": SOURCE_TAG,
        "recorded_short_commit": SOURCE_COMMIT_SHORT,
        "required": True,
        "full_40_hex_commit": None,
    },
    {
        "id": "per_weight_rights_record",
        "required": True,
        "status": "absent",
    },
    {
        "id": "historical_heldout_results",
        "path": HELDOUT_RESULTS_PATH,
        "required": True,
        "status": "absent",
    },
)

CALLER_ASSET_FIELDS = (
    "context_samples",
    "frame_samples",
    "license_record_path",
    "license_record_sha256",
    "model_path",
    "model_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "runtime_version",
    "sample_rate_hz",
    "sequence_model_path",
    "sequence_model_sha256",
    "source_revision",
    "state_shape",
)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "present_behavior": (
        "validate_hash_geometry_revision_and_onnx_header_only; "
        "do_not_load_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "separate_model_archive_required": True,
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "model, sequence, lock and rights paths are absolute and present",
        "SHA-256 values match the pinned artifact digests",
        "stateful graph header matches input/state/sr and output/stateN",
        "runtime version is exactly ONNX Runtime 1.24.1",
        "sample rate, channels and geometry equal 16 kHz mono 512/64",
        "source_revision is a full 40-hex commit beginning 5cd7945",
        "no download, copy, import, model load or execution occurs here",
    ],
    "weights_embedded_in_wheel": True,
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "offline_sequence_graph_absent",
        "requirement": (
            "Supply the official Silero 6.2.3 offline sequence graph "
            f"{SEQUENCE_MODEL_PATH} with SHA-256 {SEQUENCE_ONNX_SHA256}."),
        "state": (
            "No file named silero_vad_16k_sequence.onnx exists in the "
            "workspace; only the stateful standard graph is present."),
        "gate_ids": ["exact_asset_identity", "streaming_offline_separation"],
    },
    {
        "id": "exact_runtime_absent",
        "requirement": (
            "Provide an isolated, hash-pinned Python runtime with NumPy "
            f"{NUMPY_VERSION} and ONNX Runtime {ONNXRUNTIME_VERSION} at "
            f"{RUNTIME_ENV_PATH} with lock SHA-256 {RUNTIME_LOCK_SHA256}."),
        "state": (
            "The pinned environment is absent. An unrelated validation venv "
            "contains ONNX Runtime 1.31.1 and NumPy 2.4.6; the C dependency "
            "bundle contains ONNX Runtime 1.31.1. No 1.24.1 / 2.2.6 pair exists."),
        "gate_ids": ["runtime_admission", "exact_reference_parity"],
    },
    {
        "id": "official_wheel_and_lock_absent",
        "requirement": (
            "Supply the official PyPI wheel "
            f"{WHEEL_FILENAME} with SHA-256 {WHEEL_SHA256}, the exact "
            f"requirements lock {RUNTIME_LOCK_PATH}, and "
            f"{WHEEL_HASHES_PATH} as caller-owned artifacts."),
        "state": (
            "No silero-vad 6.2.3 wheel, dist-info directory, lock file or "
            "wheel-hash list is present anywhere in the workspace."),
        "gate_ids": ["exact_asset_identity", "runtime_admission"],
    },
    {
        "id": "full_source_revision_unpinned",
        "requirement": (
            "Record the immutable full 40-hex upstream commit for release tag "
            f"{SOURCE_TAG}; the available evidence records only the short "
            f"commit {SOURCE_COMMIT_SHORT}."),
        "state": (
            "The merged evidence records 'release tag commit 5cd7945' and no "
            "full revision. A short prefix is not an exact source pin."),
        "gate_ids": ["exact_asset_identity", "artifact_rights"],
    },
    {
        "id": "per_weight_rights_uncleared",
        "requirement": (
            "Clear artifact-specific weight, training-data, runtime dependency, "
            "redistribution and product-use rights with complete notices."),
        "state": (
            "The PyPI package declares MIT, but no per-weight terms or "
            "training-data provenance statement exists. The repository model "
            "manifest sets redistributed=false and requires independent review."),
        "gate_ids": ["artifact_rights"],
    },
    {
        "id": "standard_graph_present_but_unqualified",
        "requirement": (
            "Treat the stateful graph as admitted only after exact identity, "
            "rights review and approved-runtime parity are complete."),
        "state": (
            "cpp-library/.deps/silero_vad.onnx matches the pinned SHA-256 and "
            "the expected ONNX interface, but it is an unversioned build "
            "dependency outside task custody, with no signed 6.2.3 identity, "
            "rights record or parity run."),
        "gate_ids": ["exact_asset_identity", "artifact_rights", "exact_reference_parity"],
    },
    {
        "id": "real_analysis_cohort_absent",
        "requirement": (
            "Freeze a rights-cleared held-out cohort with continuous speech "
            "and nonspeech truth, quiet/active/idle strata, known positives "
            "and negatives, and onset/offset labels."),
        "state": (
            "No cohort is present. The inventory records "
            f"{HELDOUT_RESULTS_PATH} as a missing historical artifact, and the "
            "source-reported AMI result covers only three meetings."),
        "gate_ids": ["analysis_cohort_and_scoring", "exact_reference_parity"],
    },
    {
        "id": "approved_reference_parity_absent",
        "requirement": (
            "Produce an approved exact-runtime Silero 6.2.3 probability and "
            "interval vector on frozen PCM for byte-level parity."),
        "state": (
            "No approved exact-runtime output vector, fresh-session trace or "
            "interval parity record is available in this package."),
        "gate_ids": ["exact_reference_parity", "opt_in_provider_intake"],
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_asset_identity",
     "Stateful and sequence ONNX graphs plus the official wheel match exact "
     "SHA-256 pins; the full 40-hex upstream revision is recorded."),
    ("runtime_admission",
     "An isolated hash-pinned NumPy 2.2.6 / ONNX Runtime 1.24.1 environment "
     "with a complete lock and recorded platform is admitted."),
    ("artifact_rights",
     "Weight, training-data, runtime dependency, redistribution, product-use "
     "and derivative-output rights are cleared with complete notices."),
    ("exact_reference_parity",
     "An approved exact-runtime probability and interval vector matches the "
     "reference on frozen 16 kHz mono PCM, including fresh-session reset."),
    ("analysis_cohort_and_scoring",
     "A rights-cleared held-out cohort with quiet, active, idle, positive and "
     "negative strata scores exact timestamps, onset/offset and FN/FP."),
    ("streaming_offline_separation",
     "The stateful 512/64 streaming path and bounded 512-frame sequence path "
     "are separately reproduced and never pooled."),
    ("opt_in_provider_intake",
     "Explicit opt-in provider intake, license review, descriptor review and "
     "an independent public-surface decision are complete."),
    ("public_default_and_release",
     "Explicit default selection, resource/deadline evidence and release or "
     "public-benchmark approval are recorded; this package is off by default."),
)

ANALYSIS_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    ("timestamped_probabilities",
     "Per-frame probabilities with exact half-open source intervals.",
     "control_only_structurally_verified"),
    ("event_boundaries_and_detections",
     "Speech event boundaries and detections with exact sample coordinates.",
     "control_only_structurally_verified"),
    ("quiet_and_active_speech",
     "Separate quiet and active speech strata with matched labels.",
     "blocked_no_real_model_or_cohort"),
    ("idle_noise",
     "Idle noise and nonspeech controls, including false-alarm accounting.",
     "blocked_no_real_model_or_cohort"),
    ("known_positives_and_negatives",
     "Known-positive and known-negative cases with explicit controls.",
     "blocked_no_real_model_or_cohort"),
    ("onset_offset_delay",
     "Onset and offset delay in samples for every detected condition.",
     "control_only_structurally_verified"),
    ("stratified_false_negatives_false_positives",
     "Stratified FN/FP and totals computed from real labels.",
     "blocked_no_real_model_or_cohort"),
    ("validity_versus_nonspeech",
     "Known zero is nonspeech; invalid values are rejected and unknown is "
     "never counted as nonspeech.",
     "control_only_structurally_verified"),
    ("independent_state",
     "Independent recurrent state and exact context carry per session.",
     "control_only_structurally_verified"),
    ("exact_source_intervals",
     "Every probability and event maps to exact source sample intervals.",
     "control_only_structurally_verified"),
    ("availability_dropped_stale_events",
     "Availability, dropped and stale event accounting on the target runtime.",
     "blocked_no_target_runtime"),
    ("cross_hop_behavior",
     "160-sample SDK hop and 512-sample model hop are reconciled explicitly.",
     "control_only_structurally_verified"),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "candidate_matrix": {
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "record": 2,
        "record_name": "Silero VAD 6.2.3",
        "heldout_ami_false_negative": "19.43%",
        "heldout_ami_false_positive": "8.20%",
        "reported_frame_time": "68.35 microseconds per 20 ms frame",
        "cohort_limit": "three held-out meetings",
    },
    "note": (
        "These values are copied from the merged research record. They are "
        "not reproduced, re-scored or promoted by this package."),
}

CONTROL_SEGMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "idle-a", "condition": "idle_noise", "start_frame": 0,
     "end_frame": 3, "label": False},
    {"id": "quiet-a", "condition": "quiet_speech", "start_frame": 3,
     "end_frame": 9, "label": True},
    {"id": "active-a", "condition": "active_speech", "start_frame": 9,
     "end_frame": 15, "label": True},
    {"id": "idle-b", "condition": "idle_noise", "start_frame": 15,
     "end_frame": 19, "label": False},
    {"id": "stress-a", "condition": "stress_low_snr", "start_frame": 19,
     "end_frame": 24, "label": True},
    {"id": "unknown-tail", "condition": "unknown_tail", "start_frame": 24,
     "end_frame": 25, "label": None},
)

CONTROL_TRACE: Tuple[Optional[float], ...] = (
    0.0, 0.58, 0.01,
    0.42, 0.62, 0.71, 0.66, 0.58, 0.52,
    0.95, 0.97, 0.93, 0.99, 0.91, 0.47,
    0.04, 0.06, 0.03, 0.05,
    0.40, 0.35, 0.44, 0.38, 0.31,
    None,
)
CONTROL_TRACE_PROVENANCE = (
    "caller_supplied_synthetic_control_trace_not_model_output")

ONNX_MAX_BYTES = 256 * 1024 * 1024


class Reject(ValueError):
    """Fail-closed rejection for malformed, unsupported or unqualified input."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(_normalize_negzero(value), sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise Reject("value is not canonical-JSON serializable") from error


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_loads(text: str) -> Dict[str, Any]:
    """Parse JSON while rejecting non-finite constants and duplicate keys."""

    def reject(value: str) -> Any:
        raise Reject("non-finite JSON: " + value)

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Reject("duplicate JSON key: " + key)
            result[key] = value
        return result

    value = json.loads(text, parse_constant=reject, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise Reject("expected JSON object")
    return value


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# ---------------------------------------------------------------------------
# Bounded ONNX protobuf header reader.  It never executes the graph.
# ---------------------------------------------------------------------------

def _pb_varint(data: bytes, offset: int, end: int) -> Tuple[int, int]:
    value = 0
    shift = 0
    while offset < end and shift <= 63:
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7f) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7
    raise Reject("truncated or overlong protobuf varint")


def _pb_fields(data: bytes) -> List[Tuple[int, int, Any]]:
    fields: List[Tuple[int, int, Any]] = []
    offset = 0
    end = len(data)
    while offset < end:
        key, offset = _pb_varint(data, offset, end)
        number, wire = key >> 3, key & 7
        if number == 0:
            raise Reject("protobuf field number zero")
        if wire == 0:
            value, offset = _pb_varint(data, offset, end)
        elif wire == 1:
            if offset + 8 > end:
                raise Reject("truncated fixed64 protobuf field")
            value = data[offset:offset + 8]
            offset += 8
        elif wire == 2:
            length, offset = _pb_varint(data, offset, end)
            if length > end - offset:
                raise Reject("truncated length-delimited protobuf field")
            value = data[offset:offset + length]
            offset += length
        elif wire == 5:
            if offset + 4 > end:
                raise Reject("truncated fixed32 protobuf field")
            value = data[offset:offset + 4]
            offset += 4
        else:
            raise Reject(f"unsupported protobuf wire type {wire}")
        fields.append((number, wire, value))
    return fields


def _pb_values(fields: Sequence[Tuple[int, int, Any]], number: int,
               wire: int) -> List[Any]:
    return [value for field, item_wire, value in fields
            if field == number and item_wire == wire]


def _pb_one(fields: Sequence[Tuple[int, int, Any]], number: int,
            wire: int) -> Optional[Any]:
    values = _pb_values(fields, number, wire)
    if not values:
        return None
    if len(values) != 1:
        raise Reject(f"repeated protobuf field {number}")
    return values[0]


def _utf8(raw: bytes, label: str, allow_empty: bool = False) -> str:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise Reject(f"invalid UTF-8 in {label}") from error
    if "\x00" in text:
        raise Reject(f"NUL-containing {label}")
    if not text and not allow_empty:
        raise Reject(f"empty {label}")
    return text


def _parse_tensor_type(raw: bytes) -> Dict[str, Any]:
    type_fields = _pb_fields(raw)
    tensor = _pb_one(type_fields, 1, 2)
    if tensor is None:
        raise Reject("value info is not a tensor type")
    tensor_fields = _pb_fields(tensor)
    elem_type = _pb_one(tensor_fields, 1, 0)
    if elem_type is None:
        raise Reject("tensor elem_type missing")
    shape_raw = _pb_one(tensor_fields, 2, 2)
    dims: List[Optional[int]] = []
    if shape_raw is not None:
        for field, wire, value in _pb_fields(shape_raw):
            if field != 1 or wire != 2:
                continue
            dim_fields = _pb_fields(value)
            dim_value = _pb_one(dim_fields, 1, 0)
            dim_param = _pb_one(dim_fields, 2, 2)
            if dim_value is not None and dim_param is not None:
                raise Reject("dimension has both value and parameter")
            dims.append(int(dim_value) if dim_value is not None else None)
    return {"elem_type": int(elem_type), "dims": dims}


def _parse_value_info(raw: bytes) -> Dict[str, Any]:
    fields = _pb_fields(raw)
    name_raw = _pb_one(fields, 1, 2)
    if name_raw is None:
        raise Reject("value info name missing")
    type_raw = _pb_one(fields, 2, 2)
    if type_raw is None:
        raise Reject("value info type missing")
    return {"name": _utf8(name_raw, "value info name"),
            **_parse_tensor_type(type_raw)}


def parse_onnx_model(data: bytes) -> Dict[str, Any]:
    """Parse the ModelProto header without loading tensors or executing nodes."""
    if not isinstance(data, (bytes, bytearray)):
        raise Reject("ONNX input must be bytes")
    if len(data) < 16:
        raise Reject("ONNX model is too short")
    if len(data) > ONNX_MAX_BYTES:
        raise Reject("ONNX model exceeds the 256 MiB evidence cap")
    top = _pb_fields(bytes(data))
    ir_version = _pb_one(top, 1, 0)
    producer_raw = _pb_one(top, 2, 2)
    producer = _utf8(producer_raw, "producer name") if producer_raw else ""
    graph_raw = _pb_one(top, 7, 2)
    if graph_raw is None:
        raise Reject("ONNX graph missing")
    graph = _pb_fields(graph_raw)
    graph_name_raw = _pb_one(graph, 2, 2)
    graph_name = (_utf8(graph_name_raw, "graph name")
                  if graph_name_raw is not None else "")
    inputs = [_parse_value_info(value) for field, wire, value in graph
              if field == 11 and wire == 2]
    outputs = [_parse_value_info(value) for field, wire, value in graph
               if field == 12 and wire == 2]
    initializer_count = sum(1 for field, wire, _ in graph
                            if field == 5 and wire == 2)
    node_count = sum(1 for field, wire, _ in graph
                     if field == 1 and wire == 2)
    opset: List[Dict[str, Any]] = []
    for field, wire, value in top:
        if field != 8 or wire != 2:
            continue
        opset_fields = _pb_fields(value)
        domain_raw = _pb_one(opset_fields, 1, 2)
        version = _pb_one(opset_fields, 2, 0)
        if version is None:
            raise Reject("opset version missing")
        opset.append({
            "domain": _utf8(domain_raw, "opset domain", allow_empty=True)
            if domain_raw is not None else "",
            "version": int(version),
        })
    metadata: List[Dict[str, str]] = []
    for field, wire, value in top:
        if field != 14 or wire != 2:
            continue
        meta_fields = _pb_fields(value)
        key = _pb_one(meta_fields, 1, 2)
        val = _pb_one(meta_fields, 2, 2)
        if key is not None and val is not None:
            metadata.append({"key": _utf8(key, "metadata key"),
                             "value": _utf8(val, "metadata value")})
    return {
        "ir_version": int(ir_version) if ir_version is not None else 0,
        "producer_name": producer,
        "graph_name": graph_name,
        "node_count": node_count,
        "initializer_count": initializer_count,
        "inputs": inputs,
        "outputs": outputs,
        "opset": opset,
        "metadata": metadata,
    }


def validate_standard_interface(model: Dict[str, Any]) -> None:
    """Fail closed unless the header is the expected stateful Silero graph."""
    if model.get("ir_version") != 8:
        raise Reject("unexpected ONNX IR version")
    if not any(opset.get("domain") == "" and opset.get("version") == 16
               for opset in model.get("opset", [])):
        raise Reject("missing default-domain opset 16")
    inputs = {item.get("name"): item for item in model.get("inputs", [])}
    outputs = {item.get("name"): item for item in model.get("outputs", [])}
    if set(inputs) != {"input", "state", "sr"}:
        raise Reject("unexpected standard graph input names")
    if set(outputs) != {"output", "stateN"}:
        raise Reject("unexpected standard graph output names")
    if inputs["input"]["elem_type"] != 1 or len(inputs["input"]["dims"]) != 2:
        raise Reject("standard 'input' must be rank-2 float32")
    state = inputs["state"]
    if state["elem_type"] != 1 or len(state["dims"]) != 3:
        raise Reject("standard 'state' must be rank-3 float32")
    if state["dims"][0] != 2 or state["dims"][2] != 128:
        raise Reject("standard 'state' must be [2,1,128]")
    if state["dims"][1] not in (None, 1):
        raise Reject("standard 'state' middle dimension must be 1")
    if inputs["sr"]["elem_type"] != 7 or inputs["sr"]["dims"] != []:
        raise Reject("standard 'sr' must be a scalar int64")
    if outputs["output"]["elem_type"] != 1 or len(outputs["output"]["dims"]) != 2:
        raise Reject("standard 'output' must be rank-2 float32")
    if outputs["output"]["dims"][1] != 1:
        raise Reject("standard 'output' trailing dimension must be 1")
    if outputs["stateN"]["elem_type"] != 1 or len(outputs["stateN"]["dims"]) != 3:
        raise Reject("standard 'stateN' must be rank-3 float32")


def verify_asset_bytes(data: bytes, expected_sha256: str) -> Dict[str, Any]:
    if not isinstance(expected_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", expected_sha256):
        raise Reject("expected SHA-256 must be 64 lowercase hex characters")
    digest = sha256(data)
    if digest != expected_sha256:
        raise Reject("asset SHA-256 mismatch")
    model = parse_onnx_model(data)
    validate_standard_interface(model)
    return {
        "bytes": len(data),
        "sha256": digest,
        "ir_version": model["ir_version"],
        "producer_name": model["producer_name"],
        "opset": model["opset"],
        "inputs": model["inputs"],
        "outputs": model["outputs"],
        "node_count": model["node_count"],
        "initializer_count": model["initializer_count"],
    }


def inspect_onnx_asset(path: Path, expected_sha256: str) -> Dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise Reject("ONNX asset is absent")
    data = path.read_bytes()
    summary = verify_asset_bytes(data, expected_sha256)
    summary["path"] = str(path)
    return summary


# ---------------------------------------------------------------------------
# Fixed-path asset audit.  No network, no download, no symlink following.
# ---------------------------------------------------------------------------

def _observe_file(relative: str) -> Dict[str, Any]:
    path = SOURCE_ROOT / relative
    if not path.is_file():
        return {"path": relative, "present": False, "bytes": None,
                "sha256": None}
    data = path.read_bytes()
    return {"path": relative, "present": True, "bytes": len(data),
            "sha256": sha256(data)}


def _observe_onnx(relative: str, expected_sha256: str) -> Dict[str, Any]:
    observation = _observe_file(relative)
    if not observation["present"]:
        return observation
    observation["matches_required_sha256"] = (
        observation["sha256"] == expected_sha256)
    path = SOURCE_ROOT / relative
    try:
        data = path.read_bytes()
        model = parse_onnx_model(data)
        validate_standard_interface(model)
    except (Reject, OSError) as error:
        observation["interface_ok"] = False
        observation["interface_error"] = str(error)
    else:
        observation["interface_ok"] = True
        observation["ir_version"] = model["ir_version"]
        observation["producer_name"] = model["producer_name"]
        observation["opset"] = model["opset"]
        observation["inputs"] = model["inputs"]
        observation["outputs"] = model["outputs"]
    return observation


def _dist_version(site: Path, distribution: str) -> Optional[str]:
    for info in sorted(site.glob(distribution + "-*.dist-info")):
        metadata = info / "METADATA"
        if not metadata.is_file():
            continue
        try:
            text = metadata.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if line.startswith("Version: "):
                version = line[9:].strip()
                if version:
                    return version
    return None


def _observe_runtime_root(relative: str) -> Dict[str, Any]:
    path = SOURCE_ROOT / relative
    observation: Dict[str, Any] = {"path": relative, "present": path.exists()}
    if not path.exists():
        return observation
    versions: Dict[str, str] = {}
    if path.is_dir():
        for distribution in ("onnxruntime", "numpy"):
            version = _dist_version(path, distribution)
            if version is not None:
                versions[distribution] = version
        c_runtime = None
        for child in sorted(path.iterdir()):
            match = re.fullmatch(
                r"onnxruntime-[A-Za-z0-9_.]+-[A-Za-z0-9_]+-"
                r"([0-9]+\.[0-9]+\.[0-9]+)", child.name)
            if match:
                c_runtime = match.group(1)
                break
        if c_runtime is not None:
            versions["onnxruntime_c_api"] = c_runtime
    observation["versions"] = versions
    return observation


def audit_assets() -> Dict[str, Any]:
    standard_paths = (
        "cpp-library/.deps/silero_vad.onnx",
        STANDARD_MODEL_PATH,
    )
    sequence_paths = (SEQUENCE_MODEL_PATH,)
    wheel_paths = (WHEEL_PATH,)
    runtime_roots = (
        RUNTIME_ENV_PATH,
        "cpp-library/pipeline-validation/playback-speed/.venv/"
        "lib/python3.11/site-packages",
        "cpp-library/.deps",
    )
    source_roots = (SOURCE_CHECKOUT_PATH, "data/checkouts/silero-vad")
    rights_paths = (
        "data/models/silero-vad-6.2.3/LICENSE",
        "data/models/silero-vad-6.2.3/LICENSE.md",
        "data/models/silero-vad-6.2.3/NOTICE",
        "data/models/silero-vad-6.2.3/PROVENANCE.md",
        "data/envs/silero-vad-6.2.3/LICENSE",
    )
    standard = [_observe_onnx(path, STANDARD_ONNX_SHA256)
                for path in standard_paths]
    sequence = [_observe_file(path) for path in sequence_paths]
    wheels = [_observe_file(path) for path in wheel_paths]
    runtimes = [_observe_runtime_root(path) for path in runtime_roots]
    sources = [{"path": path, "present": (SOURCE_ROOT / path).exists()}
               for path in source_roots]
    rights = [_observe_file(path) for path in rights_paths]
    heldout = _observe_file(HELDOUT_RESULTS_PATH)
    runtime_pair = any(
        item.get("versions", {}).get("onnxruntime") == ONNXRUNTIME_VERSION
        and item.get("versions", {}).get("numpy") == NUMPY_VERSION
        for item in runtimes)
    standard_present = any(
        item["present"] and item.get("matches_required_sha256") is True
        and item.get("interface_ok") is True for item in standard)
    return {
        "standard_candidates": standard,
        "sequence_candidates": sequence,
        "wheel_candidates": wheels,
        "runtime_roots": runtimes,
        "source_checkouts": sources,
        "rights_records": rights,
        "heldout_results": heldout,
        "standard_graph_present": standard_present,
        "sequence_graph_present": any(item["present"] for item in sequence),
        "wheel_present": any(item["present"] for item in wheels),
        "runtime_pair_present": runtime_pair,
        "source_checkout_present": any(item["present"] for item in sources),
        "rights_record_present": any(item["present"] for item in rights),
        "heldout_results_present": heldout["present"],
        "runtime_requirement": {
            "onnxruntime": ONNXRUNTIME_VERSION,
            "numpy": NUMPY_VERSION,
            "lock_sha256": RUNTIME_LOCK_SHA256,
        },
        "audit_scope": (
            "fixed workspace paths only; no network, no download, "
            "no model execution"),
    }


# ---------------------------------------------------------------------------
# Task-row identity: stable linked-row fields only; never the whole file.
# ---------------------------------------------------------------------------

def task_row_identity() -> Dict[str, Any]:
    relative = "audio-benchmark-platform/plan/swarm/TASKS.json"
    path = SOURCE_ROOT / relative
    if not path.is_file():
        raise Reject("task board is unavailable at " + relative)
    try:
        document = strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        raise Reject("task board unreadable") from error
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK]
    if len(rows) != 1:
        raise Reject("expected exactly one linked task row")
    row = rows[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK or stable["component"] != COMPONENT:
        raise Reject("linked task row identity mismatch")
    if stable["repository"] != "audio-sdk" or stable["mode"] != "implementation":
        raise Reject("linked task row repository/mode mismatch")
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise Reject("linked task row claim missing")
    if claim.get("base_commit") != BASE_COMMIT:
        raise Reject("claim base commit mismatch")
    if claim.get("branch") != BRANCH:
        raise Reject("claim branch mismatch")
    if claim.get("worktree") != CLAIM_WORKTREE:
        raise Reject("claim worktree mismatch")
    if claim.get("reviewer") != REVIEWER:
        raise Reject("claim reviewer mismatch")
    return {
        "source": relative,
        "stable_fields": stable,
        "stable_sha256": sha256(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": {
            "base_commit": claim["base_commit"],
            "branch": claim["branch"],
            "worktree": claim["worktree"],
            "reviewer": claim["reviewer"],
        },
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic signal and framing.
# ---------------------------------------------------------------------------

def triangle(index: int, period: int) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, int]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_signal() -> List[float]:
    samples: List[float] = []
    state = 0x5EED1234
    for index in range(TOTAL_SAMPLES):
        frame = index // MODEL_FRAME_SAMPLES
        state, noise = _lcg(state)
        if frame in (0, 1, 2, 15, 16, 17, 18):
            value = 0.002 * noise
        elif 3 <= frame <= 8:
            value = 0.05 * triangle(index, 37) + 0.02 * triangle(index, 53)
        elif 9 <= frame <= 14:
            value = 0.35 * triangle(index, 29) + 0.15 * triangle(index, 41)
        elif 19 <= frame <= 23:
            value = 0.03 * triangle(index, 31) + 0.01 * noise
        else:
            value = 0.20 * triangle(index, 23)
        samples.append(value)
    return samples


def validate_signal(signal: Any, sample_rate_hz: int = SAMPLE_RATE_HZ,
                    channels: int = CHANNELS) -> List[float]:
    if sample_rate_hz != SAMPLE_RATE_HZ or channels != CHANNELS:
        raise Reject("only 16 kHz mono is supported")
    if not isinstance(signal, (list, tuple)) or not signal:
        raise Reject("signal must be a nonempty sample sequence")
    if len(signal) > 10_000_000:
        raise Reject("signal exceeds the evidence cap")
    clean: List[float] = []
    for index, sample in enumerate(signal):
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise Reject(f"sample {index} is not a number")
        value = float(sample)
        if not math.isfinite(value):
            raise Reject(f"sample {index} is not finite")
        if abs(value) > 8.0:
            raise Reject(f"sample {index} exceeds the amplitude cap")
        clean.append(value)
    return clean


def frame_plan(signal: Any) -> Dict[str, Any]:
    samples = validate_signal(signal)
    frame_count = (len(samples) + MODEL_FRAME_SAMPLES - 1) // MODEL_FRAME_SAMPLES
    context = [0.0] * MODEL_CONTEXT_SAMPLES
    frames: List[Dict[str, Any]] = []
    contexts: List[List[float]] = []
    carry_ok = True
    for index in range(frame_count):
        start = index * MODEL_FRAME_SAMPLES
        end = min(start + MODEL_FRAME_SAMPLES, len(samples))
        frame = samples[start:end] + [0.0] * (MODEL_FRAME_SAMPLES - (end - start))
        expected = [0.0] * MODEL_CONTEXT_SAMPLES if index == 0 else carry
        if context != expected:
            carry_ok = False
        contexts.append(list(context))
        model_input = context + frame
        frames.append({
            "index": index,
            "source_start": start,
            "source_end": end,
            "valid_samples": end - start,
            "padded_samples": MODEL_FRAME_SAMPLES - (end - start),
            "model_input_samples": len(model_input),
            "context_sha256": sha256(canonical_bytes(context)),
            "model_input_sha256": sha256(canonical_bytes(model_input)),
        })
        carry = frame[-MODEL_CONTEXT_SAMPLES:]
        context = carry
    padded = frame_count * MODEL_FRAME_SAMPLES - len(samples)
    return {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "total_samples": len(samples),
        "frame_samples": MODEL_FRAME_SAMPLES,
        "context_samples": MODEL_CONTEXT_SAMPLES,
        "model_input_samples": MODEL_INPUT_SAMPLES,
        "state_shape": list(MODEL_STATE_SHAPE),
        "frame_count": frame_count,
        "padded_samples": padded,
        "partial_frame_samples": len(samples) % MODEL_FRAME_SAMPLES,
        "context_carry_exact": carry_ok,
        "context_stream_sha256": sha256(canonical_bytes(contexts)),
        "frames": frames,
    }


# ---------------------------------------------------------------------------
# Probability validation, interval mapping and analysis scoring.
# ---------------------------------------------------------------------------

def _probability(value: Any, index: int) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Reject(f"probability {index} is not a number")
    number = float(value)
    if not math.isfinite(number):
        raise Reject(f"probability {index} is not finite")
    if number < 0.0 or number > 1.0:
        raise Reject(f"probability {index} is outside [0,1]")
    return number


def map_probabilities(probabilities: Any, total_samples: int,
                      threshold: float = THRESHOLD) -> Dict[str, Any]:
    if threshold != THRESHOLD:
        raise Reject("only the pinned threshold 0.5 is supported")
    if type(total_samples) is not int or total_samples <= 0:
        raise Reject("total_samples must be a positive integer")
    frame_count = (
        total_samples + MODEL_FRAME_SAMPLES - 1) // MODEL_FRAME_SAMPLES
    if not isinstance(probabilities, (list, tuple)):
        raise Reject("probabilities must be a sequence")
    if len(probabilities) != frame_count:
        raise Reject("probability count does not match frame count")
    values = [_probability(item, index)
              for index, item in enumerate(probabilities)]
    decisions = [None if value is None else value >= threshold
                 for value in values]
    events: List[Dict[str, Any]] = []
    unknown: List[Dict[str, int]] = []
    run_start: Optional[int] = None
    for index, decision in enumerate(decisions):
        start = index * MODEL_FRAME_SAMPLES
        if decision is True and run_start is None:
            run_start = start
        elif decision is not True and run_start is not None:
            events.append({"start_sample": run_start, "end_sample": start})
            run_start = None
        if decision is None:
            unknown.append({
                "start_sample": start,
                "end_sample": min(start + MODEL_FRAME_SAMPLES, total_samples),
            })
    if run_start is not None:
        events.append({"start_sample": run_start,
                       "end_sample": total_samples})
    probability_events = []
    for index, value in enumerate(values):
        start = index * MODEL_FRAME_SAMPLES
        probability_events.append({
            "index": index,
            "start_sample": start,
            "end_sample": min(start + MODEL_FRAME_SAMPLES, total_samples),
            "probability": value,
            "label": decisions[index],
        })
    return {
        "frame_count": frame_count,
        "threshold": threshold,
        "probability_events": probability_events,
        "speech_events": events,
        "unknown_intervals": unknown,
        "counts": {
            "true_frames": sum(1 for item in decisions if item is True),
            "false_frames": sum(1 for item in decisions if item is False),
            "unknown_frames": sum(1 for item in decisions if item is None),
        },
        "trace_sha256": sha256(canonical_bytes(values)),
    }


def score_frames(decisions: Sequence[Optional[bool]],
                 labels: Sequence[Optional[bool]],
                 conditions: Sequence[str]) -> Dict[str, Any]:
    if not (len(decisions) == len(labels) == len(conditions)):
        raise Reject("decision, label and condition lengths differ")
    totals = {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "unknown": 0}
    strata: Dict[str, Dict[str, int]] = {}
    for index, (decision, label, condition) in enumerate(
            zip(decisions, labels, conditions)):
        if decision not in (True, False, None):
            raise Reject(f"decision {index} is invalid")
        if label not in (True, False, None):
            raise Reject(f"label {index} is invalid")
        if not isinstance(condition, str) or not condition:
            raise Reject(f"condition {index} is invalid")
        bucket = strata.setdefault(
            condition, {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "unknown": 0})
        if label is None:
            totals["unknown"] += 1
            bucket["unknown"] += 1
            continue
        if decision is None:
            raise Reject(f"known label {index} has unknown decision")
        if label and decision:
            totals["tp"] += 1
            bucket["tp"] += 1
        elif label and not decision:
            totals["fn"] += 1
            bucket["fn"] += 1
        elif not label and decision:
            totals["fp"] += 1
            bucket["fp"] += 1
        else:
            totals["tn"] += 1
            bucket["tn"] += 1
    positive = totals["tp"] + totals["fn"]
    negative = totals["fp"] + totals["tn"]
    miss = Fraction(totals["fn"], positive) if positive else Fraction(0, 1)
    false_alarm = (
        Fraction(totals["fp"], negative) if negative else Fraction(0, 1))
    return {
        **totals,
        "positive": positive,
        "negative": negative,
        "miss_rate_fraction": fraction_text(miss),
        "false_alarm_rate_fraction": fraction_text(false_alarm),
        "miss_rate": round(float(miss), 6),
        "false_alarm_rate": round(float(false_alarm), 6),
        "stratified": strata,
    }


def onset_offset(decisions: Sequence[Optional[bool]],
                 segments: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(decisions, (list, tuple)) or not decisions:
        raise Reject("decisions must be a nonempty sequence")
    results: List[Dict[str, Any]] = []
    for segment in segments:
        start = segment.get("start_frame")
        end = segment.get("end_frame")
        if type(start) is not int or type(end) is not int or not 0 <= start < end:
            raise Reject("invalid positive segment")
        if end > len(decisions):
            raise Reject("positive segment exceeds the decision trace")
        detected = [index for index in range(start, end)
                    if decisions[index] is True]
        expected = end - start
        missed = expected - len(detected)
        results.append({
            "id": segment.get("id"),
            "condition": segment.get("condition"),
            "start_frame": start,
            "end_frame": end,
            "start_sample": start * MODEL_FRAME_SAMPLES,
            "end_sample": end * MODEL_FRAME_SAMPLES,
            "expected_frames": expected,
            "detected_frames": len(detected),
            "missed_frames": missed,
            "onset_delay_samples": (
                (detected[0] - start) * MODEL_FRAME_SAMPLES
                if detected else None),
            "offset_delay_samples": (
                ((detected[-1] + 1) - end) * MODEL_FRAME_SAMPLES
                if detected else None),
            "detected": bool(detected),
        })
    return results


def control_labels() -> Tuple[List[Optional[bool]], List[str]]:
    labels: List[Optional[bool]] = []
    conditions: List[str] = []
    for segment in CONTROL_SEGMENTS:
        count = segment["end_frame"] - segment["start_frame"]
        labels.extend([segment["label"]] * count)
        conditions.extend([segment["condition"]] * count)
    if len(labels) != TOTAL_MODEL_FRAMES:
        raise Reject("control labels do not cover every model frame")
    return labels, conditions


def cross_hop(total_samples: int) -> Dict[str, Any]:
    if type(total_samples) is not int or total_samples <= 0:
        raise Reject("total_samples must be a positive integer")
    sdk_calls = (total_samples + SDK_FRAME_SAMPLES - 1) // SDK_FRAME_SAMPLES
    model_frames = (
        total_samples + MODEL_FRAME_SAMPLES - 1) // MODEL_FRAME_SAMPLES
    unaligned = sum(1 for call in range(1, sdk_calls)
                    if (call * SDK_FRAME_SAMPLES) % MODEL_FRAME_SAMPLES)
    return {
        "sdk_hop_samples": SDK_FRAME_SAMPLES,
        "model_hop_samples": MODEL_FRAME_SAMPLES,
        "sdk_calls": sdk_calls,
        "sdk_partial_samples": total_samples % SDK_FRAME_SAMPLES,
        "model_frames": model_frames,
        "model_partial_samples": total_samples % MODEL_FRAME_SAMPLES,
        "unaligned_sdk_boundaries": unaligned,
        "mapping": (
            "accumulate 512 samples, prepend 64 carried context samples, "
            "infer one frame, then carry the last 64 samples"),
        "timing_claim": "none",
    }


# ---------------------------------------------------------------------------
# Caller-supplied-asset manifest.  Validation only; never execution.
# ---------------------------------------------------------------------------

def _absolute_file(manifest: Dict[str, Any], field: str) -> Path:
    raw = manifest.get(field)
    if not isinstance(raw, str) or not raw:
        raise Reject(f"{field} must be a nonempty string")
    path = Path(raw)
    if not path.is_absolute():
        raise Reject(f"{field} must be an absolute path")
    if not path.is_file():
        raise Reject(f"{field} does not exist")
    return path


def _sha_field(manifest: Dict[str, Any], field: str) -> str:
    raw = manifest.get(field)
    if not isinstance(raw, str) or not re.fullmatch(r"[0-9a-f]{64}", raw):
        raise Reject(f"{field} must be 64 lowercase hex characters")
    return raw


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise Reject("caller manifest must be a JSON object")
    if set(manifest) != set(CALLER_ASSET_FIELDS):
        missing = sorted(set(CALLER_ASSET_FIELDS) - set(manifest))
        extra = sorted(set(manifest) - set(CALLER_ASSET_FIELDS))
        raise Reject(f"caller manifest fields differ missing={missing} extra={extra}")
    if manifest.get("runtime_version") != ONNXRUNTIME_VERSION:
        raise Reject("runtime_version must be exactly " + ONNXRUNTIME_VERSION)
    if manifest.get("sample_rate_hz") != SAMPLE_RATE_HZ:
        raise Reject("sample_rate_hz must be 16000")
    if manifest.get("frame_samples") != MODEL_FRAME_SAMPLES:
        raise Reject("frame_samples must be 512")
    if manifest.get("context_samples") != MODEL_CONTEXT_SAMPLES:
        raise Reject("context_samples must be 64")
    if manifest.get("state_shape") != MODEL_STATE_SHAPE:
        raise Reject("state_shape must be [2,1,128]")
    revision = manifest.get("source_revision")
    if not isinstance(revision, str) or not SOURCE_COMMIT_PATTERN.fullmatch(revision):
        raise Reject("source_revision must be the full 40-hex 5cd7945 commit")
    model_path = _absolute_file(manifest, "model_path")
    sequence_path = _absolute_file(manifest, "sequence_model_path")
    lock_path = _absolute_file(manifest, "runtime_lock_path")
    rights_path = _absolute_file(manifest, "license_record_path")
    runtime_path = manifest.get("runtime_path")
    if not isinstance(runtime_path, str) or not Path(runtime_path).is_absolute():
        raise Reject("runtime_path must be an absolute path")
    if not Path(runtime_path).is_dir():
        raise Reject("runtime_path does not exist")
    model_sha = _sha_field(manifest, "model_sha256")
    sequence_sha = _sha_field(manifest, "sequence_model_sha256")
    lock_sha = _sha_field(manifest, "runtime_lock_sha256")
    rights_sha = _sha_field(manifest, "license_record_sha256")
    if model_sha != STANDARD_ONNX_SHA256:
        raise Reject("model_sha256 does not match the pinned standard graph")
    if sequence_sha != SEQUENCE_ONNX_SHA256:
        raise Reject("sequence_model_sha256 does not match the pinned sequence graph")
    if lock_sha != RUNTIME_LOCK_SHA256:
        raise Reject("runtime_lock_sha256 does not match the pinned lock")
    if sha256(model_path.read_bytes()) != model_sha:
        raise Reject("model file SHA-256 mismatch")
    if sha256(sequence_path.read_bytes()) != sequence_sha:
        raise Reject("sequence file SHA-256 mismatch")
    if sha256(lock_path.read_bytes()) != lock_sha:
        raise Reject("runtime lock SHA-256 mismatch")
    if sha256(rights_path.read_bytes()) != rights_sha:
        raise Reject("rights record SHA-256 mismatch")
    verify_asset_bytes(model_path.read_bytes(), STANDARD_ONNX_SHA256)
    return {
        "accepted": True,
        "executed": False,
        "loaded": False,
        "model_path": str(model_path),
        "model_sha256": model_sha,
        "sequence_model_path": str(sequence_path),
        "sequence_model_sha256": sequence_sha,
        "runtime_path": runtime_path,
        "runtime_version": ONNXRUNTIME_VERSION,
        "runtime_lock_sha256": lock_sha,
        "source_revision": revision,
        "license_record_sha256": rights_sha,
        "standard_graph_header_validated": True,
        "sequence_graph_header_validated": False,
        "note": "validation only; no model, runtime or audio was executed",
    }


# ---------------------------------------------------------------------------
# Adverse controls.  Each case is actually invoked and must fail closed.
# ---------------------------------------------------------------------------

def run_adverse_controls() -> List[Dict[str, str]]:
    cases: List[Tuple[str, Any]] = [
        ("strict_json_duplicate_key",
         lambda: strict_loads('{"a":1,"a":2}')),
        ("strict_json_nonfinite",
         lambda: strict_loads('{"a":NaN}')),
        ("signal_not_a_sequence", lambda: frame_plan("not-a-signal")),
        ("signal_nonfinite", lambda: frame_plan([0.0] * 512 + [math.inf])),
        ("signal_out_of_range", lambda: frame_plan([0.0] * 512 + [9.0])),
        ("probability_count_mismatch",
         lambda: map_probabilities([0.1] * 3, TOTAL_SAMPLES)),
        ("probability_nan",
         lambda: map_probabilities([math.nan] * TOTAL_MODEL_FRAMES, TOTAL_SAMPLES)),
        ("probability_infinity",
         lambda: map_probabilities([math.inf] * TOTAL_MODEL_FRAMES, TOTAL_SAMPLES)),
        ("probability_above_one",
         lambda: map_probabilities([1.1] * TOTAL_MODEL_FRAMES, TOTAL_SAMPLES)),
        ("probability_negative",
         lambda: map_probabilities([-0.1] * TOTAL_MODEL_FRAMES, TOTAL_SAMPLES)),
        ("probability_boolean",
         lambda: map_probabilities([True] * TOTAL_MODEL_FRAMES, TOTAL_SAMPLES)),
        ("probability_string",
         lambda: map_probabilities(["0.5"] * TOTAL_MODEL_FRAMES, TOTAL_SAMPLES)),
        ("label_invalid",
         lambda: score_frames([True], ["speech"], ["idle_noise"])),
        ("onnx_truncated", lambda: parse_onnx_model(b"\x08")),
        ("onnx_bad_wire_type", lambda: parse_onnx_model(b"\x0f\x00")),
        ("onnx_wrong_hash",
         lambda: verify_asset_bytes(b"not-an-onnx-model", "0" * 64)),
        ("caller_manifest_not_object", lambda: validate_caller_manifest([])),
        ("caller_manifest_missing_field",
         lambda: validate_caller_manifest({"runtime_version": ONNXRUNTIME_VERSION})),
        ("caller_manifest_relative_path",
         lambda: validate_caller_manifest({
             "context_samples": 64,
             "frame_samples": 512,
             "license_record_path": "/nonexistent/LICENSE",
             "license_record_sha256": "0" * 64,
             "model_path": "relative-silero_vad.onnx",
             "model_sha256": STANDARD_ONNX_SHA256,
             "runtime_lock_path": "/nonexistent/requirements.lock",
             "runtime_lock_sha256": RUNTIME_LOCK_SHA256,
             "runtime_path": "relative-runtime",
             "runtime_version": ONNXRUNTIME_VERSION,
             "sample_rate_hz": SAMPLE_RATE_HZ,
             "sequence_model_path": "/nonexistent/sequence.onnx",
             "sequence_model_sha256": SEQUENCE_ONNX_SHA256,
             "source_revision": SOURCE_COMMIT_SHORT + "a" * 33,
             "state_shape": list(MODEL_STATE_SHAPE),
         })),
    ]
    results: List[Dict[str, str]] = []
    for name, function in cases:
        try:
            function()
        except (Reject, OSError, ValueError):
            results.append({"case": name, "result": "rejected"})
        else:
            results.append({"case": name, "result": "accepted"})
    return results


def build_control() -> Dict[str, Any]:
    signal = synthetic_signal()
    plan = frame_plan(signal)
    labels, conditions = control_labels()
    mapped = map_probabilities(CONTROL_TRACE, len(signal))
    decisions = [event["label"] for event in mapped["probability_events"]]
    confusion = score_frames(decisions, labels, conditions)
    onset = onset_offset(
        decisions,
        [segment for segment in CONTROL_SEGMENTS
         if segment["label"] is True])
    adverse = run_adverse_controls()
    known_zero = {
        "frame": 0,
        "probability": CONTROL_TRACE[0],
        "decision": decisions[0],
        "counted_as_nonspeech": True,
        "excluded_from_scoring": False,
    }
    unknown = {
        "frame": TOTAL_MODEL_FRAMES - 1,
        "probability": None,
        "decision": None,
        "counted_as_nonspeech": False,
        "excluded_from_scoring": True,
    }
    return {
        "model_executed": False,
        "executor": "absent",
        "probability_source": CONTROL_TRACE_PROVENANCE,
        "geometry": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "model_frame_samples": MODEL_FRAME_SAMPLES,
            "model_context_samples": MODEL_CONTEXT_SAMPLES,
            "model_input_samples": MODEL_INPUT_SAMPLES,
            "state_shape": list(MODEL_STATE_SHAPE),
            "threshold": THRESHOLD,
        },
        "signal": {
            "name": "synthetic-analysis-control",
            "samples": len(signal),
            "sha256": sha256(canonical_bytes(signal)),
            "segments": [dict(segment) for segment in CONTROL_SEGMENTS],
        },
        "framing": {
            "frame_count": plan["frame_count"],
            "padded_samples": plan["padded_samples"],
            "partial_frame_samples": plan["partial_frame_samples"],
            "context_carry_exact": plan["context_carry_exact"],
            "context_stream_sha256": plan["context_stream_sha256"],
            "frames": plan["frames"],
        },
        "control_trace": {
            "length": len(CONTROL_TRACE),
            "sha256": mapped["trace_sha256"],
            "values": list(CONTROL_TRACE),
        },
        "mapped": {
            "probability_event_count": len(mapped["probability_events"]),
            "speech_events": mapped["speech_events"],
            "unknown_intervals": mapped["unknown_intervals"],
            "counts": mapped["counts"],
        },
        "confusion": confusion,
        "onset_offset": onset,
        "validity_separation": {
            "known_zero": known_zero,
            "unknown": unknown,
            "invalid_rejected": [
                item["case"] for item in adverse
                if item["case"].startswith("probability_")
                and item["result"] == "rejected"
            ],
        },
        "cross_hop": cross_hop(len(signal)),
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic contract control only.  It is not Silero output, not a "
            "real cohort result and cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report model.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    standard_ok = observed["standard_graph_present"]
    complete = (
        standard_ok
        and observed["sequence_graph_present"]
        and observed["wheel_present"]
        and observed["runtime_pair_present"]
        and observed["source_checkout_present"]
        and observed["rights_record_present"]
        and observed["heldout_results_present"])
    if complete:
        result = "asset_set_complete_pending_parity"
    elif standard_ok:
        result = "partial_unqualified"
    else:
        result = "absent"
    return {
        "qualified": False,
        "audit_result": result,
        "standard_graph_present": observed["standard_graph_present"],
        "sequence_graph_present": observed["sequence_graph_present"],
        "wheel_present": observed["wheel_present"],
        "runtime_pair_present": observed["runtime_pair_present"],
        "runtime_1_24_1_and_numpy_2_2_6_present": observed["runtime_pair_present"],
        "source_checkout_present": observed["source_checkout_present"],
        "rights_record_present": observed["rights_record_present"],
        "heldout_results_present": observed["heldout_results_present"],
        "observed": observed,
        "note": (
            "Presence is not qualification. A matching graph header does not "
            "establish 6.2.3 identity, rights, runtime parity or accuracy."),
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = _asset_audit_summary()
    control = build_control()
    gates = [
        {"id": gate, "requirement": requirement, "status": "blocked"}
        for gate, requirement in GATE_REQUIREMENTS
    ]
    profile_items = [
        {
            "id": item,
            "requirement": requirement,
            "package_status": status,
            "satisfied_for_qualification": False,
            "qualification_effect": "none",
        }
        for item, requirement, status in ANALYSIS_REQUIREMENTS
    ]
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": {
            "status": QUALIFICATION,
            "candidate_qualified": False,
            "no_missing_result_qualifies_candidate": True,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "blocked_gate_count": len(gates),
            "blocked_gate_ids": [gate["id"] for gate in gates],
            "reason": (
                "The exact sequence graph, official wheel, pinned 1.24.1 / "
                "2.2.6 runtime, full source revision, per-weight rights record, "
                "real analysis cohort and approved parity vector are absent."),
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "generated_by": "reference.py",
        "format": FORMAT,
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "task_row_identity": identity,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "analysis_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_model_metrics": None,
            "note": (
                "Structural controls pass, but no real model, rights-cleared "
                "cohort, target runtime or approved parity exists, so the "
                "analysis profile is not satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "unknown_never_counted_as_nonspeech": True,
            "invalid_values_rejected": True,
            "known_zero_counted_as_nonspeech": True,
            "missing_result_never_qualifies": True,
            "adverse": control["adverse"],
            "adverse_all_rejected": all(
                item["result"] == "rejected" for item in control["adverse"]),
        },
        "gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": [HELDOUT_RESULTS_PATH],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; NumPy and ONNX Runtime are not imported.",
            "The ONNX header is parsed with a bounded protobuf reader; no node runs.",
            "All asset observations use fixed workspace paths and local reads.",
            "No network request, download, audio device, model load or timing run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }
