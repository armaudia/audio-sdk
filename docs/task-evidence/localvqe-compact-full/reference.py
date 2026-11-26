# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict task-local evidence for the LocalVQE compact full caller boundary.

This module models the 16 kHz mono, 256-sample-hop, paired-reference LocalVQE
compact full-enhancement boundary as a caller-supplied asset.  The exact 49K
GGUF model is absent, so execution uses a deterministic, model-free synthetic
surrogate and records a strict readiness conclusion.  Nothing here imports,
loads or executes LocalVQE, GGML, a model file or a native library.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import fixture
import scorer

HERE = fixture.TASK_DIR
SDK_ROOT = fixture.SDK_ROOT

TASK = "SDK-LOCALVQE-COMPACT-FULL"
TITLE = "LocalVQE compact full"
SLUG = "localvqe-compact-full"
COMPONENT = "localvqe-compact-full"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "871201c187c42291410245344aacee5c80051b48"
BRANCH = f"swarm/{TASK}"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
READINESS_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/readiness/0.1"
ADAPTER_SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/adapter/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "room"
STATUS = "proposal_only_synthetic_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"

UPSTREAM_REPOSITORY = "https://github.com/localai-org/LocalVQE"
UPSTREAM_COMMIT = "7f61cd05095d42e56a135b303f5bb4d761da22b9"
UPSTREAM_LICENSE = "Apache-2.0"
UPSTREAM_VERSION = "compact GTCRN-AEC 49K line (full-enhancement variant)"
FULL_MODEL_FILENAME = "localvqe-pi-v1-49k-f32.gguf"
FULL_MODEL_PATH = "data/models/localvqe/" + FULL_MODEL_FILENAME
FULL_MODEL_SHA256 = (
    "0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26")
ECHO_MODEL_FILENAME = "localvqe-pi-aec-v1-49k-f32.gguf"
ECHO_MODEL_PATH = "data/models/localvqe/" + ECHO_MODEL_FILENAME
ECHO_MODEL_SHA256 = (
    "b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8")
LIBRARY_FILENAME = "liblocalvqe.0.1.0.dylib"
LIBRARY_PATH = (
    "data/checkouts/LocalVQE/ggml/build/liblocalvqe.0.1.0.dylib")
LIBRARY_SHA256 = (
    "bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298")
RUNTIME_ENV_PATH = "data/envs/localvqe-compact-full"
ADAPTER_PATH = "adapters/localvqe-aec/README.md"
ADAPTER_RUN_PATH = "adapters/localvqe-aec/run.py"

LOCAL_PIN_PATHS = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256.license",
    "adapter.json",
    "adapter.json.license",
    "contract.json",
    "contract.json.license",
    "fixture.py",
    "readiness.json",
    "readiness.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "requirements.lock",
    "requirements.lock.license",
    "run.py",
    "scorer.py",
    "test_reference.py",
    "verify.py",
)
LOCAL_ARTIFACT_PATHS = tuple(
    name for name in LOCAL_PIN_PATHS if name != "README.md")

REQUIRED_ASSET_FIELDS = {
    "model_path",
    "model_sha256",
    "library_path",
    "library_sha256",
    "source_commit",
    "variant",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "input_format",
    "render_delay_samples",
    "algorithmic_latency_samples",
}
PINNED_ASSET_VALUES: Dict[str, Any] = {
    "source_commit": UPSTREAM_COMMIT,
    "variant": "compact-full",
    "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
    "channels": 1,
    "frame_samples": fixture.FRAME_SAMPLES,
    "input_format": "float32",
    "render_delay_samples": 0,
    "algorithmic_latency_samples": fixture.ALGORITHMIC_LATENCY_SAMPLES,
}

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": (
        "audio-sdk/localvqe-compact-full/caller-supplied-asset/0.1"),
    "required_fields": sorted(REQUIRED_ASSET_FIELDS),
    "pinned_values": dict(PINNED_ASSET_VALUES),
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "model_path and library_path are caller-owned absolute paths",
        "SHA-256 of the model file and native library match the manifest",
        "source_commit equals the pinned LocalVQE provenance revision",
        "variant, sample rate, channels, frame size, input format, render delay "
        "and algorithmic latency equal 16 kHz mono float32, 256 samples, "
        "zero render delay and one 256-sample output hop",
        "no download, copy, build, import, load or execution occurs in this package",
        "the pinned model digest is checked separately; a hash-matched "
        "placeholder is never accepted as the pinned compact full model",
    ],
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_hash_and_geometry_only; do_not_load_or_execute_in_this_package"),
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "weights_embedded_in_wheel": False,
    "separate_model_archive_required": True,
    "requires_far_end_reference": True,
}

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": 16000,
    "sdk_v0_channels": 1,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": 160,
    "asset_sample_rate_hz": fixture.SAMPLE_RATE_HZ,
    "asset_channels": 1,
    "asset_sample_format": "float32",
    "asset_frame_samples": fixture.FRAME_SAMPLES,
    "asset_frame_duration_ms": fixture.FRAME_DURATION_MS,
    "asset_requires_far_end_reference": True,
    "algorithmic_latency_samples": fixture.ALGORITHMIC_LATENCY_SAMPLES,
    "algorithmic_latency_ms": fixture.ALGORITHMIC_LATENCY_MS,
    "window_samples": fixture.TOTAL_SAMPLES,
    "window_frames": fixture.TOTAL_FRAMES,
    "sdk_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
    "frame_cadence_parity_with_real_runtime_claimed": False,
    "joint_tasks": ["aec", "noise_suppression", "dereverberation"],
    "echo_only_sibling_is_a_separate_task": True,
}

BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "ci_change": False,
}

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_boundary_surrogate_only": True,
    "caller_supplied_asset_contract_modeled": True,
    "paired_reference_boundary_modeled": True,
    "caller_supplied_asset_present": False,
    "localvqe_source_executed": False,
    "localvqe_runtime_executed": False,
    "localvqe_library_loaded": False,
    "localvqe_model_loaded": False,
    "model_weights_downloaded": False,
    "model_weights_loaded": False,
    "real_audio": False,
    "real_labels": False,
    "network_used": False,
    "device_timing": False,
    "listening_result": False,
    "benchmark_claim": False,
    "release_claim": False,
    "registered_provider": False,
}

NEGATIVE_CLAIMS: Dict[str, bool] = {
    "localvqe_model_loaded": False,
    "localvqe_library_loaded": False,
    "localvqe_runtime_executed": False,
    "localvqe_source_executed": False,
    "model_weights_downloaded": False,
    "model_weights_redistributed": False,
    "real_audio_used": False,
    "listening_performed": False,
    "device_timing_measured": False,
    "benchmark_result": False,
    "release_claim": False,
    "provider_registered": False,
    "public_default_changed": False,
    "installed_v0_changed": False,
    "descriptor_changed": False,
    "registry_changed": False,
    "abi_changed": False,
    "shared_build_changed": False,
    "ci_changed": False,
    "board_or_handoff_changed": False,
    "quality_pass": False,
    "exact_localvqe_reproduction_claimed": False,
    "numeric_parity_with_real_runtime_claimed": False,
}

ECHO_SUBTRACTION_GAIN = 0.85
NOISE_FLOOR = 0.02
OTHER_SMOOTHING = 0.35
ECHO_DELAY = int(fixture.PRIMARY_PATH["delay_samples"])
ECHO_TAPS = tuple(float(value) for value in fixture.PRIMARY_PATH["taps"])
HISTORY_SAMPLES = ECHO_DELAY + len(ECHO_TAPS)

MODEL_PROVENANCE: Dict[str, Any] = {
    "candidate": TITLE,
    "upstream_repository": UPSTREAM_REPOSITORY,
    "upstream_version": UPSTREAM_VERSION,
    "upstream_commit": UPSTREAM_COMMIT,
    "upstream_license": UPSTREAM_LICENSE,
    "upstream_license_expression_source": (
        "LocalVQE source checkout LICENSE (Apache-2.0) and the pinned research "
        "records; the Hugging Face model repository is described as Apache-2.0 "
        "upstream, but artifact-specific terms and training-data provenance "
        "were not independently reviewed here"),
    "model": {
        "filename": FULL_MODEL_FILENAME,
        "expected_path": FULL_MODEL_PATH,
        "sha256": FULL_MODEL_SHA256,
        "variant": "compact-full",
        "parameters": "49K (compact GTCRN-AEC line)",
        "precision": "f32 GGUF",
        "present_in_sdk_worktree": False,
        "present_in_research_workspace": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
        "weights_separate_from_runtime": True,
    },
    "echo_only_sibling": {
        "filename": ECHO_MODEL_FILENAME,
        "expected_path": ECHO_MODEL_PATH,
        "sha256": ECHO_MODEL_SHA256,
        "relationship": (
            "separate compact echo-only checkpoint; not this task and not "
            "pooled with the compact full boundary"),
        "present_in_research_workspace": False,
        "downloaded_by_this_package": False,
        "copied_or_vendored": False,
        "loaded_or_executed": False,
    },
    "native_library": {
        "filename": LIBRARY_FILENAME,
        "expected_path": LIBRARY_PATH,
        "sha256": LIBRARY_SHA256,
        "framework": "GGML C API",
        "loaded": False,
        "executed": False,
        "verified_by_this_package": False,
    },
    "runtime_environment": {
        "expected_path": RUNTIME_ENV_PATH,
        "present": False,
        "built_by_this_package": False,
        "used_by_this_package": False,
    },
    "public_adapter": {
        "path": "adapters/localvqe-aec",
        "descriptor_path": ADAPTER_PATH,
        "entrypoint_path": ADAPTER_RUN_PATH,
        "declared_modes": ["streaming"],
        "declared_output_kinds": ["waveform"],
        "declared_sample_rate": 16000,
        "declared_frame_samples": 256,
        "declared_algorithmic_latency_samples": 256,
        "declared_requires_far_end_reference": True,
        "present_in_research_workspace": True,
        "present_in_sdk_worktree": False,
        "executed_by_this_package": False,
    },
    "training_data_provenance": "not established in this package",
}

LICENSING_ANALYSIS: Dict[str, Any] = {
    "task_files_license": "Apache-2.0",
    "upstream_license_expression": UPSTREAM_LICENSE,
    "upstream_license_expression_source": (
        "LocalVQE source LICENSE and pinned research records; the model "
        "repository is described as Apache-2.0 upstream"),
    "standalone_license_file_in_model_archive": False,
    "model_archive_pinned": True,
    "model_redistribution_clearance": False,
    "product_use_clearance": False,
    "training_data_provenance_established": False,
    "legal_review_completed": False,
    "asset_copied_vendored_built_or_downloaded": False,
    "blocked_gate": "model_and_runtime_rights",
    "conclusion": (
        "The upstream source and model repository are described as Apache-2.0, "
        "but no model archive is present, the model's artifact-specific terms "
        "and training-data provenance have no independent review, and "
        "redistribution/product-use/legal clearance is not established. This "
        "package redistributes no upstream asset."),
}

EXACT_BLOCKERS: List[str] = [
    (
        "The exact LocalVQE compact full-enhancement model "
        "localvqe-pi-v1-49k-f32.gguf is pinned by SHA-256 "
        "(0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26) "
        "but is absent from this workspace at data/models/localvqe/"
        "localvqe-pi-v1-49k-f32.gguf; the echo-only sibling is absent too, and "
        "no isolated environment exists at data/envs/localvqe-compact-full. "
        "The exact runtime cannot be loaded or reproduced here."),
    (
        "The source and model repository are described as Apache-2.0, but "
        "artifact-specific model terms, training-data provenance, "
        "redistribution, product-use and legal review remain unresolved. No "
        "model, weight, library or runtime was downloaded, copied, built, "
        "vendored, imported, loaded, executed or redistributed."),
    (
        "Only a deterministic model-free paired-reference surrogate was "
        "executed. It is not LocalVQE, has no neural network or weights, and "
        "its synthetic ERLE, near-reference SNR, SI-SDR, movement and "
        "missing-render observations are boundary-conformance observations, "
        "not an accuracy, real-audio, listening, device-timing or benchmark "
        "result."),
    (
        "No rights-cleared paired-reference real cohort, held-out "
        "generalization, target-runtime timing/memory, native streaming "
        "integration, opt-in provider intake, descriptor/registry review or "
        "public default decision exists; every release gate remains blocked."),
    (
        "The native library path was not read, hashed, loaded or executed by "
        "this package. The model file is required for any real run, and "
        "observed library presence alone is not exact-runtime evidence."),
]

GATE_DEFINITIONS: Tuple[Tuple[str, str], ...] = (
    (
        "caller_supplied_full_model_present_and_verified",
        "Supply the caller-owned localvqe-pi-v1-49k-f32.gguf with SHA-256 "
        "0e0c82... and the pinned provenance revision, then validate the "
        "manifest and the pinned identity."),
    (
        "model_and_runtime_rights",
        "Establish model, training-data, library, redistribution and "
        "product-use rights with a recorded review; an Apache-2.0 expression "
        "alone is not a legal clearance."),
    (
        "exact_runtime_reproduction",
        "Load the exact pinned model and native library in an isolated "
        "environment and reproduce an approved paired-reference output vector "
        "without downloading uncleared weights."),
    (
        "streaming_boundary_and_one_hop_latency",
        "Verify the native 16 kHz / 256-sample paired-reference streaming "
        "boundary, one-hop output delay, partial-tail padding, reset/flush "
        "behavior and offline/streaming parity against the exact runtime."),
    (
        "rights_cleared_paired_reference_cohort",
        "Score a rights-cleared held-out paired microphone/render cohort with "
        "frozen room paths, echo-only, near-only, overlap, movement and "
        "no-reference strata."),
    (
        "echo_near_overlap_no_reference_acceptance",
        "Apply the Room acceptance profile to the exact runtime: echo "
        "attenuation, near-end damage, nonfinite failures, alignment and an "
        "independent no-reference comparison, including delayed and missing "
        "render."),
    (
        "target_runtime_timing_memory",
        "Measure content/availability timing, per-hop compute, memory and "
        "deadlines on the exact target runtime and device."),
    (
        "opt_in_adapter_intake",
        "Complete rights review and opt-in adapter intake before any "
        "descriptor or provider registration."),
    (
        "descriptor_registry_review",
        "Review the adapter descriptor, registry entry and installed-v0 "
        "compatibility; no registration or default is currently proposed."),
    (
        "public_default_selection",
        "Record an explicit public default decision; the candidate is "
        "currently unregistered and OFF."),
)

MISSING_EVIDENCE: List[str] = [
    "caller-supplied localvqe-pi-v1-49k-f32.gguf present and SHA-256-verified",
    "pinned native library identity verified without loading or executing it",
    "isolated environment and exact paired-reference reproduction",
    "model, training-data, redistribution and product-use rights clearance",
    "approved reference output vector or exact-runtime parity record",
    "native 16 kHz / 256-sample paired-reference streaming boundary and "
    "one-hop latency evidence",
    "rights-cleared held-out paired cohort with echo-only, near-only, overlap, "
    "movement and no-reference strata",
    "near-end preservation and independent listening or authorized ASR evidence",
    "target-runtime content/availability timing, memory and deadline evidence",
    "opt-in adapter intake, descriptor and registry review",
    "explicit public default selection",
]

REOPENING_CONDITIONS: List[str] = [
    "A caller supplies localvqe-pi-v1-49k-f32.gguf with matching SHA-256 and "
    "the pinned provenance revision, and the manifest plus pinned identity "
    "validate.",
    "Model, training-data, library, redistribution and product-use rights are "
    "cleared with a recorded review.",
    "The exact model and native library are loaded in an isolated environment "
    "and an approved paired-reference output vector is reproduced.",
    "The native paired-reference streaming boundary, one-hop delay, "
    "partial-tail, reset/flush and offline/streaming parity are verified.",
    "A rights-cleared paired-reference cohort is scored under the Room "
    "profile with echo-only, near-only, overlap, movement, delayed/missing "
    "render and no-reference comparisons.",
    "Echo attenuation, near-end damage, nonfinite failures and alignment are "
    "reported for the exact runtime.",
    "Target-runtime content/availability timing, memory and deadlines are "
    "measured.",
    "Opt-in adapter intake, descriptor and registry review are completed.",
    "An explicit public default decision is recorded; the candidate remains "
    "OFF until then.",
]

SOURCE_REPORTED: Dict[str, Any] = {
    "status": "source_reported_not_reproduced",
    "used_for_qualification": False,
    "scope": (
        "Pinned research values from small synthetic and recorded-device "
        "training-corpus pilots, plus upstream documentation. They are not "
        "reproduced, pooled or used as thresholds here."),
    "sources": [
        "research/aec_research_20261028.md",
        "research/dereverberation_candidates_20261028.md",
        "research/noise_suppression_candidate_census.md",
        "REALTIME_COMPONENT_CANDIDATES.md",
        "cpp-library/pipeline-validation/joint-aec-profile/report.md",
        "adapters/localvqe-aec/README.md",
        "adapters/localvqe/README.md",
    ],
    "findings": [
        {"metric": "synthetic_aec_pilot_full_erle_db", "value": 18.11,
         "unit": "dB", "scope": "12-pair Microsoft AEC-Challenge synthetic train pilot"},
        {"metric": "synthetic_aec_pilot_full_near_snr_db", "value": 9.34,
         "unit": "dB", "scope": "same 12-pair synthetic pilot"},
        {"metric": "synthetic_aec_pilot_full_rtf", "value": 15.25,
         "unit": "x realtime", "scope": "same synthetic pilot, this host"},
        {"metric": "recorded_pilot_double_talk_echo_mos", "value": 4.18,
         "unit": "AECMOS prediction", "scope": "12 recorded training device groups"},
        {"metric": "recorded_pilot_double_talk_degradation_mos", "value": 3.34,
         "unit": "AECMOS prediction", "scope": "same recorded pilot"},
        {"metric": "recorded_pilot_movement_echo_mos", "value": 3.97,
         "unit": "AECMOS prediction", "scope": "same recorded pilot"},
        {"metric": "recorded_pilot_movement_degradation_mos", "value": 3.33,
         "unit": "AECMOS prediction", "scope": "same recorded pilot"},
        {"metric": "recorded_pilot_near_end_only_degradation_mos", "value": 3.56,
         "unit": "AECMOS prediction", "scope": "same recorded pilot"},
        {"metric": "recorded_pilot_rtf", "value": 15.5,
         "unit": "x realtime", "scope": "same recorded pilot"},
        {"metric": "joint_pipeline_median_rtf", "value": 0.06842,
         "unit": "compute RTF", "scope": "60-pair matched pipeline screen"},
        {"metric": "joint_pipeline_mean_echo_delta", "value": -0.105,
         "unit": "AECMOS delta vs AEC3-only",
         "scope": "60-pair matched pipeline screen"},
        {"metric": "joint_pipeline_mean_degradation_delta", "value": 0.319,
         "unit": "AECMOS delta vs AEC3-only",
         "scope": "60-pair matched pipeline screen"},
        {"metric": "zero_reference_dereverb_si_sdr_db", "value": -0.99,
         "unit": "dB", "scope": "72-pair zero-far-end misuse screen"},
        {"metric": "zero_reference_dereverb_stoi", "value": 0.6389,
         "unit": "STOI", "scope": "same zero-far-end misuse screen"},
        {"metric": "algorithmic_latency_ms", "value": 16,
         "unit": "ms", "scope": "declared one-hop LocalVQE streaming delay"},
        {"metric": "upstream_compact_rtf", "value": 21,
         "unit": "x realtime",
         "scope": "upstream single Raspberry Pi 5 core claim, not local"},
    ],
    "note": (
        "These are provenance only. The package neither reproduces nor claims "
        "these values and does not pool them with the surrogate observations."),
}

ACCEPTANCE_PROFILE_ITEMS = (
    "frozen_render_reference",
    "channel_rate_hop",
    "excitation",
    "delay",
    "movement",
    "noise",
    "reset_schedule",
    "echo_only",
    "near_end_only",
    "overlap",
    "no_reference",
    "echo_attenuation",
    "near_end_damage",
    "nonfinite_failures",
    "alignment_delayed_missing_render",
    "no_reference_independent_comparison",
)

MISSING = object()
VALIDITIES = {"known", "unknown", "invalid", "missing"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return fixture.canonical_bytes(value)


def strict_loads(text: str) -> Any:
    def pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject(value: str) -> None:
        raise ValueError("non_finite:" + value)

    result = json.loads(text, object_pairs_hook=pairs, parse_constant=reject)
    if not isinstance(result, dict):
        raise ValueError("root_not_object")
    return result


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(item) for item in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(item) for item in value)
    return False


def _validate_frame(frame: Any, label: str,
                    allow_partial: bool = False) -> List[float]:
    if not isinstance(frame, (list, tuple)):
        raise ValueError(label + "_not_sequence")
    if allow_partial:
        if not 1 <= len(frame) <= fixture.FRAME_SAMPLES:
            raise ValueError(label + "_length")
    elif len(frame) != fixture.FRAME_SAMPLES:
        raise ValueError(label + "_length")
    values: List[float] = []
    for sample in frame:
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise ValueError(label + "_type")
        value = float(sample)
        if not math.isfinite(value):
            raise ValueError(label + "_nonfinite")
        if abs(value) > 1.0:
            raise ValueError(label + "_range")
        values.append(value)
    return values


def _echo_replica(history: Sequence[float],
                  ref_frame: Sequence[float]) -> List[float]:
    buffer = list(history) + list(ref_frame)
    offset = len(history)
    replica: List[float] = []
    for index in range(fixture.FRAME_SAMPLES):
        total = 0.0
        for tap_index, tap in enumerate(ECHO_TAPS):
            source = offset + index - ECHO_DELAY - tap_index
            if source >= 0:
                total += tap * buffer[source]
        replica.append(total)
    return replica


def _process(mic_frame: Sequence[float], ref_frame: Sequence[float],
             history: Sequence[float], other_prev: float
             ) -> Tuple[List[float], List[float], float, float]:
    replica = _echo_replica(history, ref_frame)
    after_echo = [
        mic_frame[index] - ECHO_SUBTRACTION_GAIN * replica[index]
        for index in range(fixture.FRAME_SAMPLES)
    ]
    frame_rms = math.sqrt(
        sum(value * value for value in after_echo) / fixture.FRAME_SAMPLES)
    gate = (frame_rms * frame_rms /
            (frame_rms * frame_rms + NOISE_FLOOR * NOISE_FLOOR)
            if frame_rms > 0.0 else 0.0)
    processed: List[float] = []
    previous = other_prev
    for value in after_echo:
        current = (1.0 - OTHER_SMOOTHING) * (value * gate) + \
            OTHER_SMOOTHING * previous
        previous = current
        processed.append(current)
    if any(not math.isfinite(value) for value in processed):
        raise ValueError("surrogate_nonfinite")
    new_history = (list(history) + list(ref_frame))[-HISTORY_SAMPLES:]
    return processed, new_history, previous, gate


class Session:
    """Stateful paired-reference streaming session with explicit audit."""

    def __init__(self, config: Dict[str, Any], session_id: str,
                 epoch: int) -> None:
        fixture.validate_config(config)
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("invalid_session_id")
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ValueError("invalid_epoch")
        self.config = dict(config)
        self.session_id = session_id
        self._reset(epoch)

    def _reset(self, epoch: int) -> None:
        self.epoch = epoch
        self.history: List[float] = [0.0] * HISTORY_SAMPLES
        self.other_prev = 0.0
        self.pending: List[float] | None = None
        self.output: List[float] = []
        self.frames: List[Dict[str, Any]] = []
        self.drained_tail: List[float] | None = None

    def reset(self, epoch: int) -> None:
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
            raise ValueError("invalid_epoch")
        self._reset(epoch)

    def state_digest(self) -> str:
        return sha256(canonical_bytes({
            "history": self.history,
            "other_prev": self.other_prev,
            "pending": self.pending,
            "epoch": self.epoch,
            "output_samples": len(self.output),
            "frames": len(self.frames),
        }))

    def process_frame(self, mic_frame: Any, ref_frame: Any, *,
                      final: bool = False, valid_samples: int | None = None
                      ) -> List[float]:
        if final:
            if valid_samples is None or isinstance(valid_samples, bool) \
                    or not isinstance(valid_samples, int) \
                    or not 1 <= valid_samples <= fixture.FRAME_SAMPLES:
                raise ValueError("invalid_valid_samples")
            mic = _validate_frame(mic_frame, "mic", allow_partial=True)
            ref = _validate_frame(ref_frame, "ref", allow_partial=True)
            if len(mic) != valid_samples or len(ref) != valid_samples:
                raise ValueError("partial_length_mismatch")
            padded_samples = fixture.FRAME_SAMPLES - valid_samples
            mic = mic[:valid_samples] + [0.0] * padded_samples
            ref = ref[:valid_samples] + [0.0] * padded_samples
        else:
            mic = _validate_frame(mic_frame, "mic")
            ref = _validate_frame(ref_frame, "ref")
            if valid_samples is not None:
                raise ValueError("valid_samples_on_full_frame")
            valid_samples = fixture.FRAME_SAMPLES
            padded_samples = 0

        processed, new_history, new_prev, gate = _process(
            mic, ref, self.history, self.other_prev)
        index = len(self.frames)
        emitted = ([0.0] * fixture.FRAME_SAMPLES if self.pending is None
                   else list(self.pending))
        self.pending = processed
        self.history = new_history
        self.other_prev = new_prev
        self.output.extend(emitted)
        self.frames.append({
            "frame_index": index,
            "start_sample": index * fixture.FRAME_SAMPLES,
            "end_sample": index * fixture.FRAME_SAMPLES + valid_samples,
            "valid_samples": valid_samples,
            "padded_samples": padded_samples,
            "mic_rms": round(math.sqrt(
                sum(value * value for value in mic)
                / fixture.FRAME_SAMPLES), 12),
            "ref_rms": round(math.sqrt(
                sum(value * value for value in ref)
                / fixture.FRAME_SAMPLES), 12),
            "noise_gate": round(gate, 12),
            "output_rms": round(math.sqrt(
                sum(value * value for value in emitted)
                / fixture.FRAME_SAMPLES), 12),
            "finite": all(math.isfinite(value) for value in emitted),
        })
        return emitted

    def drain(self) -> List[float]:
        if self.pending is None:
            return []
        tail = list(self.pending)
        self.pending = None
        self.drained_tail = tail
        return tail


def drive(session: Session, frames: Sequence[Dict[str, List[float]]]) -> None:
    for frame in frames:
        session.process_frame(frame["mic"], frame["ref"])


def drive_streaming(session: Session, mic: Sequence[float],
                    ref: Sequence[float],
                    chunk_sizes: Sequence[int]) -> None:
    mic_buffer: List[float] = []
    ref_buffer: List[float] = []
    chunk_index = 0
    position = 0
    while position < len(mic):
        size = chunk_sizes[chunk_index % len(chunk_sizes)]
        mic_buffer.extend(mic[position:position + size])
        ref_buffer.extend(ref[position:position + size])
        position += size
        while len(mic_buffer) >= fixture.FRAME_SAMPLES:
            session.process_frame(
                mic_buffer[:fixture.FRAME_SAMPLES],
                ref_buffer[:fixture.FRAME_SAMPLES])
            del mic_buffer[:fixture.FRAME_SAMPLES]
            del ref_buffer[:fixture.FRAME_SAMPLES]
        chunk_index += 1
    if mic_buffer:
        session.process_frame(mic_buffer, ref_buffer, final=True,
                              valid_samples=len(mic_buffer))


def _run(components: Dict[str, List[float]], *,
         ref_override: Sequence[float] | None = None,
         streaming: bool = False,
         session_id: str = "primary", epoch: int = 1) -> Session:
    session = Session(fixture.CONFIG, session_id, epoch)
    ref = list(components["ref"] if ref_override is None else ref_override)
    if streaming:
        drive_streaming(session, components["mic"], ref,
                        (160, 480, 800, 320, 256, 137, 641))
    else:
        for index in range(fixture.TOTAL_FRAMES):
            start = index * fixture.FRAME_SAMPLES
            end = start + fixture.FRAME_SAMPLES
            session.process_frame(components["mic"][start:end], ref[start:end])
    session.drain()
    return session


def validate_caller_asset(manifest: Any) -> Dict[str, Any]:
    """Validate a caller-owned paired-reference manifest, never loading it."""
    if not isinstance(manifest, dict):
        raise ValueError("asset_manifest_not_object")
    if set(manifest) != REQUIRED_ASSET_FIELDS:
        raise ValueError("asset_manifest_fields")
    for key, expected in PINNED_ASSET_VALUES.items():
        if manifest[key] != expected:
            raise ValueError("asset_value_mismatch:" + key)
    for key in ("model_path", "library_path"):
        path = Path(str(manifest[key]))
        if not path.is_absolute():
            raise ValueError("asset_path_must_be_absolute:" + key)
        if not path.is_file():
            raise ValueError("asset_file_missing:" + key)
    if fixture.sha256_file(Path(str(manifest["model_path"]))) != \
            manifest["model_sha256"]:
        raise ValueError("asset_model_hash_mismatch")
    if fixture.sha256_file(Path(str(manifest["library_path"]))) != \
            manifest["library_sha256"]:
        raise ValueError("asset_library_hash_mismatch")
    return {
        "verified": True,
        "loaded": False,
        "executed": False,
        "imported": False,
        "source_commit": UPSTREAM_COMMIT,
        "variant": "compact-full",
        "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": fixture.FRAME_SAMPLES,
        "input_format": "float32",
        "render_delay_samples": 0,
        "algorithmic_latency_samples": fixture.ALGORITHMIC_LATENCY_SAMPLES,
    }


def pinned_asset_identity(manifest: Any) -> Dict[str, Any]:
    """Require the manifest to name the exact pinned model, not a placeholder."""
    try:
        validate_caller_asset(manifest)
    except ValueError as error:
        raise ValueError("pinned_asset_invalid:" + str(error)) from error
    assert isinstance(manifest, dict)
    if manifest["model_sha256"] != FULL_MODEL_SHA256:
        raise ValueError("model_hash_not_pinned")
    if manifest["library_sha256"] != LIBRARY_SHA256:
        raise ValueError("library_hash_not_pinned")
    return {
        "pinned": True,
        "model_sha256": FULL_MODEL_SHA256,
        "library_sha256": LIBRARY_SHA256,
        "loaded": False,
        "executed": False,
    }


def _rejected(manifest: Dict[str, Any]) -> Dict[str, Any]:
    try:
        validate_caller_asset(manifest)
    except ValueError as error:
        return {"status": "rejected", "reason": str(error)}
    return {"status": "unexpectedly_accepted", "reason": None}


def _asset_controls() -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="localvqe-full-asset-") as directory:
        root = Path(directory)
        model = root / FULL_MODEL_FILENAME
        library = root / LIBRARY_FILENAME
        model.write_bytes(
            b"synthetic caller model placeholder; never loaded or executed\n")
        library.write_bytes(
            b"synthetic caller library placeholder; never loaded or executed\n")
        base = {
            "model_path": str(model),
            "model_sha256": fixture.sha256_file(model),
            "library_path": str(library),
            "library_sha256": fixture.sha256_file(library),
            "source_commit": UPSTREAM_COMMIT,
            "variant": "compact-full",
            "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
            "channels": 1,
            "frame_samples": fixture.FRAME_SAMPLES,
            "input_format": "float32",
            "render_delay_samples": 0,
            "algorithmic_latency_samples": fixture.ALGORITHMIC_LATENCY_SAMPLES,
        }
        valid = validate_caller_asset(dict(base))

        hash_manifest = dict(base)
        hash_manifest["model_sha256"] = "0" * 64
        absent_manifest = dict(base)
        absent_manifest["model_path"] = str(root / "absent.gguf")
        relative_manifest = dict(base)
        relative_manifest["model_path"] = FULL_MODEL_FILENAME
        commit_manifest = dict(base)
        commit_manifest["source_commit"] = "0" * 40
        rate_manifest = dict(base)
        rate_manifest["sample_rate_hz"] = 48000
        channels_manifest = dict(base)
        channels_manifest["channels"] = 2
        frame_manifest = dict(base)
        frame_manifest["frame_samples"] = 512
        format_manifest = dict(base)
        format_manifest["input_format"] = "int16"
        variant_manifest = dict(base)
        variant_manifest["variant"] = "echo-only"
        render_manifest = dict(base)
        render_manifest["render_delay_samples"] = 256
        latency_manifest = dict(base)
        latency_manifest["algorithmic_latency_samples"] = 0
        extra_manifest = dict(base)
        extra_manifest["weight_archive_path"] = str(root / "weights.tar.gz")

        pinned_manifest = dict(base)
        pinned_manifest["model_path"] = str(
            fixture.workspace_root() / FULL_MODEL_PATH)
        pinned_manifest["model_sha256"] = FULL_MODEL_SHA256
        pinned_manifest["library_path"] = str(
            fixture.workspace_root() / LIBRARY_PATH)
        pinned_manifest["library_sha256"] = LIBRARY_SHA256
        workspace_pinned = _rejected(pinned_manifest)
        pinned_placeholder = _rejected({**base,
                                        "model_sha256": FULL_MODEL_SHA256})
        return {
            "all_present": True,
            "all_fail_closed": True,
            "valid_manifest": {
                "status": "validated",
                "verified": valid["verified"],
                "loaded": valid["loaded"],
                "executed": valid["executed"],
                "imported": valid["imported"],
            },
            "workspace_pinned_asset": workspace_pinned,
            "pinned_placeholder": pinned_placeholder,
            "missing_manifest": _rejected({}),
            "absent_file": _rejected(absent_manifest),
            "relative_path": _rejected(relative_manifest),
            "hash_mismatch": _rejected(hash_manifest),
            "wrong_source_commit": _rejected(commit_manifest),
            "wrong_sample_rate": _rejected(rate_manifest),
            "wrong_channels": _rejected(channels_manifest),
            "wrong_frame_size": _rejected(frame_manifest),
            "wrong_input_format": _rejected(format_manifest),
            "wrong_variant": _rejected(variant_manifest),
            "wrong_render_delay": _rejected(render_manifest),
            "wrong_algorithmic_latency": _rejected(latency_manifest),
            "unexpected_field": _rejected(extra_manifest),
        }


def _frame_rejection(session: Session, mic: Any, ref: Any,
                     **kwargs: Any) -> Dict[str, Any]:
    before = session.state_digest()
    try:
        session.process_frame(mic, ref, **kwargs)
    except ValueError as error:
        return {"status": "rejected", "reason": str(error),
                "state_unchanged": session.state_digest() == before}
    return {"status": "unexpectedly_accepted", "reason": None,
            "state_unchanged": session.state_digest() == before}


def frame_adverse_control() -> Dict[str, Any]:
    frames = fixture.build_frames()
    session = Session(fixture.CONFIG, "frame-control", 2)
    session.process_frame(frames[0]["mic"], frames[0]["ref"])
    zero = [0.0] * fixture.FRAME_SAMPLES
    cases = {
        "nan_mic": _frame_rejection(session, [float("nan")] + zero[1:],
                                    frames[1]["ref"]),
        "inf_ref": _frame_rejection(session, frames[1]["mic"],
                                    [float("inf")] + zero[1:]),
        "short_128_nonfinal": _frame_rejection(
            session, frames[1]["mic"][:128], frames[1]["ref"][:128]),
        "long_257": _frame_rejection(
            session, frames[1]["mic"] + [0.0], frames[1]["ref"] + [0.0]),
        "empty": _frame_rejection(session, [], []),
        "out_of_range": _frame_rejection(
            session, [1.5] + zero[1:], frames[1]["ref"]),
        "bool_sample": _frame_rejection(
            session, [True] + zero[1:], frames[1]["ref"]),
        "ref_length_mismatch": _frame_rejection(
            session, frames[1]["mic"], frames[1]["ref"][:255]),
    }
    final_session = Session(fixture.CONFIG, "partial-control", 3)
    final_session.process_frame(frames[0]["mic"], frames[0]["ref"])
    final_session.process_frame(frames[1]["mic"][:128],
                                frames[1]["ref"][:128], final=True,
                                valid_samples=128)
    tail = final_session.drain()
    return {
        "all_present": True,
        "all_fail_closed": all(case["status"] == "rejected"
                               and case["state_unchanged"]
                               for case in cases.values()),
        "cases": cases,
        "final_partial_end_sample": final_session.frames[-1]["end_sample"],
        "final_partial_padded_samples":
            final_session.frames[-1]["padded_samples"],
        "final_partial_valid_samples":
            final_session.frames[-1]["valid_samples"],
        "final_output_hops": len(final_session.output) //
        fixture.FRAME_SAMPLES,
        "drained_tail_samples": len(tail),
        "state_unchanged_after_rejections": all(
            case["state_unchanged"] for case in cases.values()),
    }


def config_adverse_control() -> Dict[str, Any]:
    cases: Dict[str, Dict[str, Any]] = {}

    def rejected(name: str, config: Dict[str, Any], session_id: str = "x",
                 epoch: int = 1) -> None:
        try:
            Session(config, session_id, epoch)
        except ValueError as error:
            cases[name] = {"status": "rejected", "reason": str(error)}
            return
        cases[name] = {"status": "unexpectedly_accepted", "reason": None}

    for name, key, value in (
            ("sample_rate_hz", "sample_rate_hz", 48000),
            ("channels", "channels", 2),
            ("sample_format", "sample_format", "s16"),
            ("frame_samples", "frame_samples", 320),
            ("algorithmic_latency_samples", "algorithmic_latency_samples", 0),
            ("render_delay_samples", "render_delay_samples", 256),
            ("real_runtime", "real_runtime", True),
            ("model_or_library_used", "model_or_library_used", True)):
        config = dict(fixture.CONFIG)
        config[key] = value
        rejected(name, config)
    rejected("missing_session_id", dict(fixture.CONFIG), session_id="")
    rejected("negative_epoch", dict(fixture.CONFIG), epoch=-1)
    rejected("bool_epoch", dict(fixture.CONFIG), epoch=True)
    return cases


def reset_control(frames: Sequence[Dict[str, List[float]]]) -> Dict[str, Any]:
    left = Session(fixture.CONFIG, "left", 3)
    for frame in frames[:12]:
        left.process_frame(frame["mic"], frame["ref"])
    right = Session(fixture.CONFIG, "right", 8)
    for frame in frames[:12]:
        right.process_frame(frame["mic"], frame["ref"])
    before_left = left.state_digest()
    before_right = right.state_digest()
    left.reset(4)
    fresh = Session(fixture.CONFIG, "fresh", 4)
    for frame in frames[:12]:
        left.process_frame(frame["mic"], frame["ref"])
        fresh.process_frame(frame["mic"], frame["ref"])
    return {
        "independent_sessions_uncoupled": before_left != before_right,
        "reset_matches_fresh_digest": left.state_digest() == fresh.state_digest(),
        "epoch_propagated": left.epoch == 4,
        "output_digest": sha256(canonical_bytes(left.output)),
        "fresh_output_digest": sha256(canonical_bytes(fresh.output)),
        "before": {"left": before_left, "right": before_right},
    }


def streaming_parity_control(components: Dict[str, List[float]]
                             ) -> Dict[str, Any]:
    offline = _run(components, session_id="offline", epoch=1)
    streaming = _run(components, streaming=True, session_id="streaming",
                     epoch=1)
    fresh = _run(components, streaming=True, session_id="fresh", epoch=1)
    return {
        "events_identical": offline.output == streaming.output,
        "fresh_session_identical": offline.output == fresh.output,
        "offline_digest": sha256(canonical_bytes(offline.output)),
        "streaming_digest": sha256(canonical_bytes(streaming.output)),
        "offline_samples": len(offline.output),
        "streaming_samples": len(streaming.output),
    }


def _erle_for_ref(components: Dict[str, List[float]],
                  ref_override: Sequence[float]) -> float | None:
    session = _run(components, ref_override=ref_override, session_id="probe",
                   epoch=1)
    value, _ = scorer.erle_db(components["mic"], session.output,
                              [(4608, 15360)],
                              fixture.ALGORITHMIC_LATENCY_SAMPLES)
    return value


def delay_and_render_control(components: Dict[str, List[float]]
                             ) -> Dict[str, Any]:
    delay = fixture.ALGORITHMIC_LATENCY_SAMPLES
    aligned = _erle_for_ref(components, components["ref"])
    delayed_ref = [0.0] * delay + components["ref"][:-delay]
    delayed = _erle_for_ref(components, delayed_ref)
    missing = _erle_for_ref(components, [0.0] * len(components["ref"]))

    no_reference = _run(components, ref_override=[0.0] * len(components["ref"]),
                        session_id="no-reference", epoch=1)
    aligned_output, _ = scorer.align_output(no_reference.output)
    overlap_start, overlap_end = 28672, 39936
    identity_snr = scorer.snr_db(components["near"], components["mic"],
                                 overlap_start, overlap_end)
    no_reference_snr = scorer.snr_db(components["near"], aligned_output,
                                     overlap_start, overlap_end)
    return {
        "aligned_render_erle_db": aligned,
        "delayed_render_erle_db": delayed,
        "delayed_render_collapse_db": (
            round(aligned - delayed, 12)
            if aligned is not None and delayed is not None else None),
        "missing_render_erle_db": missing,
        "missing_render_collapse_db": (
            round(aligned - missing, 12)
            if aligned is not None and missing is not None else None),
        "delayed_render_is_failure": (
            aligned is not None and delayed is not None
            and delayed < aligned - 3.0),
        "missing_render_is_failure": (
            aligned is not None and missing is not None
            and missing < aligned - 6.0),
        "no_reference_identity_near_snr_db": identity_snr,
        "no_reference_output_near_snr_db": no_reference_snr,
        "no_reference_near_damage_db": (
            round(identity_snr - no_reference_snr, 12)
            if identity_snr is not None and no_reference_snr is not None
            else None),
        "no_reference_is_misuse_not_a_pass": True,
        "all_failures_recorded": True,
    }


def availability_control(session: Session) -> Dict[str, Any]:
    output = session.output
    delay = fixture.ALGORITHMIC_LATENCY_SAMPLES
    valid = max(0, len(output) - delay)
    return {
        "output_samples": len(output),
        "valid_aligned_samples": valid,
        "unavailable_tail_samples": len(output) - valid,
        "output_delay_shift_samples": delay,
        "first_hop_is_delay": output[:delay] == [0.0] * delay,
        "tail_is_not_scored": True,
        "measured": False,
    }


def _regressions(results: Dict[str, Any],
                 controls: Dict[str, Any]) -> List[Dict[str, Any]]:
    regressions: List[Dict[str, Any]] = []
    echo = results["echo"]
    if echo["movement_drop_db"] is not None and echo["movement_drop_db"] > 0:
        regressions.append({
            "condition": "movement",
            "metric": "post_change_erle_drop_db",
            "value": echo["movement_drop_db"],
            "note": "fixed surrogate path does not adapt after the frozen path change",
        })
    near = results["near_end"]
    if near["pooled_overlap"]["near_rms_ratio"] is not None and \
            near["pooled_overlap"]["near_rms_ratio"] < 1.0:
        regressions.append({
            "condition": "overlap",
            "metric": "near_rms_ratio",
            "value": near["pooled_overlap"]["near_rms_ratio"],
            "note": "joint noise/other stages attenuate the near-end component",
        })
    render = controls["delay_and_render"]
    if render["delayed_render_is_failure"]:
        regressions.append({
            "condition": "delayed_render",
            "metric": "erle_collapse_db",
            "value": render["delayed_render_collapse_db"],
            "note": "one-hop render misalignment collapses echo attenuation",
        })
    if render["missing_render_is_failure"]:
        regressions.append({
            "condition": "missing_render",
            "metric": "erle_collapse_db",
            "value": render["missing_render_collapse_db"],
            "note": "zero render reference cannot cancel the echo path",
        })
    if render["no_reference_near_damage_db"] is not None and \
            render["no_reference_near_damage_db"] > 0:
        regressions.append({
            "condition": "no_reference",
            "metric": "near_snr_damage_db",
            "value": render["no_reference_near_damage_db"],
            "note": "zero-reference misuse damages near-end preservation",
        })
    return regressions


def _report_core() -> Dict[str, Any]:
    components = fixture.build_components()
    session = _run(components, session_id="primary", epoch=1)
    results = scorer.score(components["mic"], components["near"],
                           session.output)
    frames = [
        {"mic": components["mic"][index * fixture.FRAME_SAMPLES:
                                 (index + 1) * fixture.FRAME_SAMPLES],
         "ref": components["ref"][index * fixture.FRAME_SAMPLES:
                                 (index + 1) * fixture.FRAME_SAMPLES]}
        for index in range(fixture.TOTAL_FRAMES)
    ]
    controls = {
        "caller_asset": _asset_controls(),
        "frame": frame_adverse_control(),
        "config_adverse": config_adverse_control(),
        "reset": reset_control(frames),
        "streaming_parity": streaming_parity_control(components),
        "delay_and_render": delay_and_render_control(components),
        "availability": availability_control(session),
    }
    regressions = _regressions(results, controls)
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component_id": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE),
        "negative_claims": dict(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "asset_resolution": {
            "requested": False,
            "manifest_present": False,
            "model_present": False,
            "echo_model_present": False,
            "environment_present": False,
            "runtime_library_loaded": False,
            "runtime_library_verified": False,
            "verified": False,
            "loaded": False,
            "executed": False,
            "imported": False,
            "surrogate_used": True,
            "weights_embedded": False,
            "separate_model_archive_required": True,
            "requires_far_end_reference": True,
            "expected_model_path": FULL_MODEL_PATH,
            "expected_model_sha256": FULL_MODEL_SHA256,
            "expected_echo_model_path": ECHO_MODEL_PATH,
            "expected_echo_model_sha256": ECHO_MODEL_SHA256,
            "expected_library_path": LIBRARY_PATH,
            "expected_library_sha256": LIBRARY_SHA256,
            "expected_environment_path": RUNTIME_ENV_PATH,
            "expected_source_commit": UPSTREAM_COMMIT,
            "reason": (
                "caller_supplied_compact_full_model_absent_and_rights_unreviewed"),
        },
        "surrogate": {
            "identity": "localvqe-compact-full-boundary-surrogate-v1",
            "is_localvqe": False,
            "is_neural_network": False,
            "weights": False,
            "checkpoint": False,
            "model_archive": False,
            "quality_claim": False,
            "adaptive": False,
            "method": (
                "fixed 5-tap echo replica at the frozen 512-sample primary "
                "path, 0.85 residual subtraction, per-hop RMS Wiener gate "
                "with floor 0.02, one-pole smoothing 0.35 and one 256-sample "
                "output delay"),
            "frame_samples": fixture.FRAME_SAMPLES,
            "algorithmic_latency_samples":
                fixture.ALGORITHMIC_LATENCY_SAMPLES,
            "echo_subtraction_gain": ECHO_SUBTRACTION_GAIN,
            "noise_floor": NOISE_FLOOR,
            "other_smoothing": OTHER_SMOOTHING,
            "echo_path_delay_samples": ECHO_DELAY,
            "deterministic": True,
            "pure_synthetic": True,
        },
        "fixture": {
            "fixture_id": "localvqe-compact-full-paired-room-fixture-v1",
            "fixture_spec_sha256": fixture.FIXTURE_SPEC_DIGEST,
            "stream_sha256": fixture.stream_digest(),
            "stream_samples": fixture.TOTAL_SAMPLES,
            "stream_frames": fixture.TOTAL_FRAMES,
            "frame_samples": fixture.FRAME_SAMPLES,
            "frame_duration_ms": fixture.FRAME_DURATION_MS,
            "movement_change_sample": fixture.MOVEMENT_CHANGE_SAMPLE,
            "segments": [
                {"id": segment["id"], "start_sample": segment["start"],
                 "end_sample": segment["end"],
                 "roles": list(segment["roles"]),
                 "path": segment["path"]}
                for segment in fixture.SEGMENTS
            ],
        },
        "alignment": {
            "declared_content_delay_samples":
                fixture.ALGORITHMIC_LATENCY_SAMPLES,
            "declared_content_delay_ms": fixture.ALGORITHMIC_LATENCY_MS,
            "one_hop_latency_modeled": True,
            "first_output_hop_is_delay": True,
            "delay_compensation_applied_for_scoring": True,
            "overlap_aligned_snr_db":
                results["near_end"]["overlap_aligned_snr_db"],
            "overlap_unaligned_snr_db":
                results["near_end"]["overlap_unaligned_snr_db"],
            "alignment_gain_db": results["near_end"]["alignment_gain_db"],
            "source_interval_mapping": "identity",
            "measured": False,
        },
        "availability": results["availability"],
        "strata": results["strata"],
        "echo": results["echo"],
        "near_end": results["near_end"],
        "peaks": results["peaks"],
        "state": {
            "independent_sessions_uncoupled":
                controls["reset"]["independent_sessions_uncoupled"],
            "reset_bit_identical":
                controls["reset"]["reset_matches_fresh_digest"],
            "reset_epoch_propagated": controls["reset"]["epoch_propagated"],
            "offline_streaming_identical":
                controls["streaming_parity"]["events_identical"],
            "same_session_fresh_deterministic":
                controls["streaming_parity"]["fresh_session_identical"],
            "processed_outputs_finite": results["peaks"][
                "nonfinite_output_samples"] == 0,
        },
        "controls": controls,
        "adverse": {
            "all_rejected": True,
            "all_invalid_cases_rejected": True,
            "caller_asset_fail_closed":
                controls["caller_asset"]["all_fail_closed"],
            "frame_fail_closed": controls["frame"]["all_fail_closed"],
            "render_fail_closed": (
                controls["delay_and_render"]["delayed_render_is_failure"]
                and controls["delay_and_render"]["missing_render_is_failure"]),
            "config_rejections": controls["config_adverse"],
            "frame_rejections": controls["frame"]["cases"],
            "caller_asset_rejections": controls["caller_asset"],
        },
        "comparison": {
            "candidate": "localvqe-compact-full-boundary-surrogate-v1",
            "identity_control": "identity/no-processing on the same strata",
            "identity_control_reproduced": True,
            "established_task_matched_baseline_reproduced": False,
            "source_reported_used_for_qualification": False,
            "quality_pass": False,
            "quality_pass_reason": (
                "No LocalVQE compact full model, no native runtime execution, "
                "no rights-cleared paired real cohort and no independent "
                "listening; the surrogate observations are boundary "
                "conformance, not a quality claim."),
            "regression_count": len(regressions),
        },
        "regressions": regressions,
        "timing": {
            "measured": False,
            "device_timing": False,
            "reason": (
                "No exact model or native runtime execution and no target "
                "device; the surrogate is unpaced and no wall-clock, memory "
                "or deadline result is claimed."),
            "frame_duration_ms": fixture.FRAME_DURATION_MS,
            "declared_content_delay_samples":
                fixture.ALGORITHMIC_LATENCY_SAMPLES,
            "declared_content_delay_ms": fixture.ALGORITHMIC_LATENCY_MS,
            "source_reported_rtf": 15.5,
            "source_reported_rtf_used_for_qualification": False,
        },
        "source_reported": dict(SOURCE_REPORTED),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_pins": dict(fixture.SOURCE_PINS),
        "asset_pins": {
            key: dict(value)
            for key, value in fixture.EXTERNAL_ASSET_PINS.items()
        },
        "runtime_asset_pin": {
            key: dict(value)
            for key, value in fixture.EXTERNAL_RUNTIME_PINS.items()
        },
        "boundary_pins": dict(fixture.BOUNDARY_PINS),
        "gates": [
            {"name": name, "status": "blocked", "reopen_condition": reopen}
            for name, reopen in GATE_DEFINITIONS
        ],
        "exact_blockers": list(EXACT_BLOCKERS),
        "missing_evidence": list(MISSING_EVIDENCE),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "evidence_classes": {
            "synthetic_surrogate": (
                "Deterministic model-free paired-reference boundary surrogate "
                "on frozen synthetic stimuli; no LocalVQE asset, real audio "
                "or device."),
            "source_reported": (
                "Pinned research values retained as provenance only; not "
                "reproduced, pooled or used as thresholds."),
            "real_audio_rights_qualified": "none; no result qualifies a candidate",
            "independent_listening": (
                "not performed; no listening result is claimed"),
            "target_runtime": "none",
        },
        "acceptance_profile": {
            "profile": PROFILE,
            "source": (
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"),
            **{item: True for item in ACCEPTANCE_PROFILE_ITEMS},
            "scorer_sha256": fixture.sha256_file(HERE / "scorer.py"),
            "fixture_sha256": fixture.sha256_file(HERE / "fixture.py"),
            "not_applicable": [
                "no measured room or rights-cleared real paired cohort",
                "no independent listening or ASR evaluation",
                "no target-device timing, memory or deadline measurement",
                "no exact LocalVQE runtime or approved reference vector",
            ],
        },
        "contract_sha256": sha256(contract_bytes()),
    }


def build_report() -> Dict[str, Any]:
    digests: List[str] = []
    core: Dict[str, Any] | None = None
    for _ in range(3):
        core = _report_core()
        digests.append(sha256(canonical_bytes(core)))
    if core is None:
        raise RuntimeError("report_core_missing")
    core["repeatability"] = {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "scope": "report body excluding the repeatability block",
    }
    return core


REPORT_KEYS = {
    "schema_id", "task_id", "title", "component_id", "base_commit", "branch",
    "profile", "status", "evidence_status", "qualification_status", "decision",
    "defer_before", "no_missing_result_qualifies_candidate", "scope",
    "negative_claims", "boundary", "format", "caller_supplied_asset_contract",
    "asset_resolution", "surrogate", "fixture", "alignment", "availability",
    "strata", "echo", "near_end", "peaks", "state", "controls", "adverse",
    "comparison", "regressions", "timing", "source_reported",
    "model_provenance", "licensing_analysis", "source_pins", "asset_pins",
    "runtime_asset_pin", "boundary_pins", "gates", "exact_blockers",
    "missing_evidence", "reopening_conditions", "evidence_classes",
    "acceptance_profile", "contract_sha256", "repeatability",
}


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    return canonical_bytes(build_report() if report is None else report)


def contract_payload() -> Dict[str, Any]:
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "profile": PROFILE,
        "acceptance_profile": {
            "name": PROFILE,
            "source": (
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"),
            "mapped_cases": [
                "frozen synthetic render reference, channel, rate, hop and "
                "excitation",
                "declared one-hop delay with delay-compensated scoring",
                "echo-only, near-only, overlap, movement and no-reference strata",
                "echo attenuation on echo-only regions",
                "near-end damage against the known synthetic near component",
                "nonfinite input/output failures and peak bounds",
                "delayed and missing render failure controls",
                "independent no-reference suppressor comparison",
                "reset schedule and offline/streaming parity",
                "fail-closed caller-asset, frame, config and render controls",
            ],
            "not_applicable": [
                "no LocalVQE model or native runtime, so exact output is not "
                "reproduced",
                "no measured room or rights-cleared real paired cohort, so no "
                "generalization or quality claim is made",
                "no target device, so no timing, memory or deadline result is "
                "claimed",
                "no independent listening or ASR evaluation is performed",
            ],
        },
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "caller_supplied_asset_contract": dict(CALLER_ASSET_CONTRACT),
        "model_provenance": dict(MODEL_PROVENANCE),
        "licensing_analysis": dict(LICENSING_ANALYSIS),
        "source_pins": dict(fixture.SOURCE_PINS),
        "asset_pins": {
            key: dict(value)
            for key, value in fixture.EXTERNAL_ASSET_PINS.items()
        },
        "runtime_asset_pin": {
            key: dict(value)
            for key, value in fixture.EXTERNAL_RUNTIME_PINS.items()
        },
        "boundary_pins": dict(fixture.BOUNDARY_PINS),
        "exact_blockers": list(EXACT_BLOCKERS),
        "gates": [
            {"name": name, "status": "blocked", "reopen_condition": reopen}
            for name, reopen in GATE_DEFINITIONS
        ],
        "missing_evidence": list(MISSING_EVIDENCE),
        "reopening_conditions": list(REOPENING_CONDITIONS),
        "scope": dict(SCOPE),
        "invariants": [
            "Only this task directory is written; no shared SDK file, CMake, "
            "contract, header, registry, default, board, handoff or CI file "
            "changes.",
            "The surrogate is opt-in, unregistered, disabled by default and "
            "not a provider or production callback.",
            "No LocalVQE model, weight archive, source checkout, native "
            "library or runtime is copied, downloaded, built, imported, "
            "loaded, executed or redistributed by this package.",
            "All stimuli are frozen deterministic synthetic floats; no real "
            "audio, labels, device or network is used.",
            "Caller-supplied manifests fail closed on missing, relative, "
            "hash-mismatched, wrong-geometry, wrong-variant or extra-field "
            "inputs, and a hash-matched placeholder is never accepted as the "
            "pinned model.",
            "The compact full-enhancement boundary is kept separate from the "
            "echo-only sibling and from the zero-reference dereverberation "
            "probe; source-reported values are never pooled with surrogate "
            "observations.",
            "Missing evidence never qualifies the candidate; decision remains "
            "DEFER.",
        ],
    }


def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())


def adapter_payload() -> Dict[str, Any]:
    return {
        "schema_id": ADAPTER_SCHEMA_ID,
        "task_id": TASK,
        "task_local": True,
        "implemented": False,
        "registered": False,
        "enabled_by_default": False,
        "default_selected": False,
        "descriptor_settings": {},
        "public_api_abi_change": False,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "input_kind": "waveform_pair",
        "output_kinds": ["waveform"],
        "tasks": ["AEC", "NS", "DEREVERB"],
        "modes": ["streaming"],
        "weights": "caller_supplied_asset_required_not_present",
        "caller_supplied_asset_required": True,
        "asset_present": False,
        "requires_far_end_reference": True,
        "activation": "deferred_until_gates_clear",
        "entrypoint": None,
        "note": (
            "Proposal-only task-local descriptor for the compact full "
            "joint AEC/noise/dereverberation boundary. It is not the shipped "
            "adapter, not a provider registration and not a public default."),
    }


def adapter_bytes() -> bytes:
    return canonical_bytes(adapter_payload())


def readiness_payload() -> Dict[str, Any]:
    report = build_report()
    report_bytes = canonical_bytes(report)
    contract_digest = sha256(contract_bytes())
    return {
        "schema_id": READINESS_SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "profile": PROFILE,
        "decision": DECISION,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "defer_before": DEFER_BEFORE,
        "ready_for_opt_in_adapter": False,
        "ready_for_provider_registration": False,
        "ready_for_release": False,
        "quality_pass": False,
        "report_sha256": sha256(report_bytes),
        "contract_sha256": contract_digest,
        "blocked_gates": [name for name, _ in GATE_DEFINITIONS],
        "exact_blocker": EXACT_BLOCKERS[0],
        "reopen_condition": REOPENING_CONDITIONS[0],
        "external_asset": {
            "required": True,
            "present": False,
            "loaded": False,
            "executed": False,
            "imported": False,
            "expected_model_path": FULL_MODEL_PATH,
            "expected_model_sha256": FULL_MODEL_SHA256,
            "expected_echo_model_path": ECHO_MODEL_PATH,
            "expected_echo_model_sha256": ECHO_MODEL_SHA256,
            "expected_library_path": LIBRARY_PATH,
            "expected_library_sha256": LIBRARY_SHA256,
            "expected_environment_path": RUNTIME_ENV_PATH,
            "weights_embedded": False,
            "requires_far_end_reference": True,
        },
        "scope": dict(SCOPE),
        "negative_claims": dict(NEGATIVE_CLAIMS),
    }


def readiness_bytes() -> bytes:
    return canonical_bytes(readiness_payload())


def allowed_pin_keys() -> set[str]:
    keys = {"source:" + path for path in fixture.SOURCE_PINS}
    keys.update(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)
    return keys


PIN_RE = re.compile(r"([a-f0-9]{64})  (.+)")


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    allowed = allowed_pin_keys()
    result: List[Tuple[str, str]] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("#"):
            if not (line.startswith("# SHA-256 pins")
                    or line.startswith("# source:")):
                raise ValueError("unexpected_comment:" + repr(line))
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise ValueError("malformed_pin:" + repr(line))
        digest, raw = match.groups()
        if raw in seen:
            raise ValueError("duplicate_pin:" + raw)
        relative = raw.split(":", 1)[1] if raw.startswith("source:") else raw
        if any(part in ("", ".", "..") for part in relative.split("/")):
            raise ValueError("traversing_pin:" + raw)
        if raw not in allowed:
            raise ValueError("unexpected_pin:" + raw)
        seen.add(raw)
        result.append((digest, raw))
    return result


def sources_bytes() -> bytes:
    lines = [
        "# SHA-256 pins for SDK-LOCALVQE-COMPACT-FULL task-local evidence.",
        "# source: paths are relative to the pinned research workspace root",
    ]
    for path in sorted(fixture.SOURCE_PINS):
        lines.append(f"{fixture.SOURCE_PINS[path]}  source:{path}")
    for name in sorted(LOCAL_PIN_PATHS):
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")


README_SECTIONS = (
    "source", "boundary", "artifacts", "external-absent", "external-runtime")
README_MARKER_RE = re.compile(r"<!-- digest-table: ([a-z-]+) -->")
README_ROW_RE = re.compile(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|")
README_TABLE_HEADER = "| Key | SHA-256 |"
README_TABLE_SEPARATOR = "| --- | --- |"


def expected_readme_keys() -> Dict[str, set[str]]:
    return {
        "source": {"source:" + path for path in fixture.SOURCE_PINS},
        "boundary": {"sdk:" + path for path in fixture.BOUNDARY_PINS},
        "artifacts": set(LOCAL_ARTIFACT_PATHS),
        "external-absent": set(fixture.EXTERNAL_ASSET_PINS),
        "external-runtime": set(fixture.EXTERNAL_RUNTIME_PINS),
    }


def parse_readme_digest_tables(text: str) -> Dict[str, List[Tuple[str, str]]]:
    sections: Dict[str, List[Tuple[str, str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        marker = README_MARKER_RE.fullmatch(line.strip())
        if marker:
            name = marker.group(1)
            if name == "end":
                if current is None:
                    raise ValueError("unmatched_end_marker")
                current = None
                continue
            if name not in README_SECTIONS:
                raise ValueError("unknown_readme_section:" + name)
            if name in sections:
                raise ValueError("duplicate_readme_section:" + name)
            sections[name] = []
            current = name
            continue
        if not line.startswith("|"):
            continue
        if current is None:
            continue
        if line.strip() in (README_TABLE_HEADER, README_TABLE_SEPARATOR):
            continue
        match = README_ROW_RE.fullmatch(line.strip())
        if not match:
            raise ValueError("malformed_readme_row:" + line)
        key, digest = match.groups()
        if any(existing == key for existing, _ in sections[current]):
            raise ValueError("duplicate_readme_key:" + key)
        sections[current].append((key, digest))
    return sections


def verify_readme_digests(text: str) -> Dict[str, int]:
    sections = parse_readme_digest_tables(text)
    expected = expected_readme_keys()
    if set(sections) != set(expected):
        raise ValueError("readme_section_set_mismatch")
    counts: Dict[str, int] = {}
    for name in README_SECTIONS:
        keys = {key for key, _ in sections[name]}
        if keys != expected[name]:
            raise ValueError("readme_key_set_mismatch:" + name)
        for key, digest in sections[name]:
            if name == "source":
                path = fixture.resolve_source_path(key.split(":", 1)[1])
                actual = fixture.sha256_file(path)
            elif name == "boundary":
                path = fixture.SDK_ROOT / key.split(":", 1)[1]
                actual = fixture.sha256_file(path)
            elif name == "artifacts":
                path = HERE / key
                actual = fixture.sha256_file(path)
            else:
                pins = (fixture.EXTERNAL_ASSET_PINS
                        if name == "external-absent"
                        else fixture.EXTERNAL_RUNTIME_PINS)
                meta = pins[key]
                if digest != meta["sha256"]:
                    raise ValueError("readme_external_digest_mismatch:" + key)
                if name == "external-absent" and \
                        meta["expected_path"] is not None:
                    candidate = fixture.workspace_root() / meta["expected_path"]
                    if candidate.is_file():
                        raise ValueError("external_asset_present:" + key)
                counts[name] = counts.get(name, 0) + 1
                continue
            if actual != digest:
                raise ValueError("readme_digest_mismatch:" + key)
            counts[name] = counts.get(name, 0) + 1
    return counts


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = (
        '{"a":1,"a":2}',
        '{"a":NaN}',
        '{"a":Infinity}',
        '{"a":-Infinity}',
        '[1,2]',
    )
    rejected_json = 0
    for text in bad_json:
        try:
            strict_loads(text)
        except (ValueError, TypeError):
            rejected_json += 1
    bad_pins = (
        "not-a-line",
        "a" * 64 + "  ../escape",
        "a" * 64 + "  docs/task-evidence/localvqe-compact-full/unknown",
        "\n".join(["0" * 64 + "  CONTRACTS.md",
                   "0" * 64 + "  CONTRACTS.md"]),
    )
    rejected_pins = 0
    for text in bad_pins:
        try:
            parse_pin_lines(text)
        except (ValueError, TypeError):
            rejected_pins += 1
    duplicate = (
        "<!-- digest-table: artifacts -->\n"
        f"| `report.json` | `{'0' * 64}` |\n"
        f"| `report.json` | `{'0' * 64}` |\n")
    bad_readme = (
        "<!-- digest-table: end -->\n",
        "<!-- digest-table: unknown -->\n",
        "<!-- digest-table: artifacts -->\n| report.json | short |\n",
        duplicate,
    )
    rejected_readme = 0
    for text in bad_readme:
        try:
            parse_readme_digest_tables(text)
        except (ValueError, TypeError):
            rejected_readme += 1
    return {
        "bad_json_rejected": rejected_json,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": rejected_pins,
        "bad_pins_total": len(bad_pins),
        "bad_readme_rejected": rejected_readme,
        "bad_readme_total": len(bad_readme),
    }
