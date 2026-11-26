# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-TOKAN.

The exact licensed TokAN source/weights/runtime set is not complete. The
upstream source checkout *is* present at a full 40-hex revision, but the
repository ships no license file, the three inference checkpoints and the
WavLM-Large encoder cache are absent, no checkpoint SHA-256 is published in
the merged evidence, and no hash-pinned runtime or rights-cleared voice cohort
exists.

This module therefore never imports PyTorch, torchaudio, Transformers,
Resemblyzer, NumPy or SoundFile, never loads or executes a model, never reads
or writes real audio, never downloads anything and never measures a device
clock. It provides three verifiable pieces:

* a fail-closed source/asset audit over fixed workspace paths, including the
  exact upstream git revision and exact source-file SHA-256 pins;
* a caller-supplied-asset manifest contract for the inference bundle and
  runtime, validated without execution;
* a deterministic synthetic voice-acceptance accounting control that checks
  PCM validity, duration accounting and offline-only alignment.

Nothing in this package qualifies the candidate. The decision is ``DEFER``.
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

TASK = "SDK-TOKAN"
TITLE = "TokAN"
SLUG = "tokan"
COMPONENT = "tokan"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "2f4251b9abc92584b025f9b6ea665d9f3ec6e991"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# Exact upstream source identity.  The checkout is shallow but its HEAD, the
# refs/heads/main file and every pinned source file are read locally.
TOKAN_REPO_RELATIVE = "research/accent-conversion-20261101/repos/TokAN"
TOKAN_COMMIT = "cbfc09a2716003463a0501ceae04ee62809c3822"
TOKAN_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
TOKAN_HF_REPO = "Piping/TokAN"
TOKAN_HF_SUBFOLDER = "checkpoints/default"
WAVLM_MODEL_NAME = "microsoft/wavlm-large"
WAVLM_LAYER = 22

# Geometry reported by the pinned config and inference entry point.
INPUT_SAMPLE_RATE_HZ = 16000
OUTPUT_SAMPLE_RATE_HZ = 24000
CHANNELS = 1
HOP_SIZE = 480
FEATURE_DIM = 80
CODEBOOK_SIZE = 1024
SSL_DIM = 1024
SPEAKER_EMBED_DIM = 256
FLOW_EMBED_DIM = 384
DEFAULT_BEAM_SIZE = 10
DEFAULT_FLOW_STEPS = 32

# Source-reported approximate sizes only.  They are not byte pins.
CHECKPOINT_FILENAMES = ("arlm.pt", "quantizer.pt", "hift.pt")
CHECKPOINT_APPROX_MB = {"arlm.pt": 690, "quantizer.pt": 393, "hift.pt": 83}
WAVLM_APPROX_MB = 1200

# Fixed workspace paths used for the audit.  Absence is recorded, not filled.
RIGHTS_RECORD_PATH = "data/rights/tokan-rights.json"
COHORT_MANIFEST_PATH = "data/runs/tokan-voice-cohort/manifest.json"
RUNTIME_ENV_PATH = "data/envs/tokan"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
SAMPLE_DATA_PATH = "research/accent-conversion-20261101/data/l2accent"
MISSING_WEIGHTS_PATH = "checkpoints/default/arlm.pt"

# Public v0 geometry is preserved and never changed by this package.
SDK_FRAME_SAMPLES = 160

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
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/accent-conversion-20261101/run_tokan_compat.py":
        "79cd855e84a570bf1ffe3e90a391f8ca0980766d3d2d8e48ec6955a1abef8267",
    "research/accent-conversion-20261101/evaluate_tokan_metrics.py":
        "d16ca09a5fee69df90d09f868cdaafe569798176eeec4e38ff6794b12becfe36",
    "research/accent-conversion-20261101/results/tokan-metrics.json":
        "e4eddb01575ef102d820605d17378913cb9552fbb69ab9b97667c6e4eb90bde3",
    "research/accent-conversion-20261101/results/accent-classifier.json":
        "c1f2146f8b7a665bcb8e8cf42b14e2bd31e042d225653f467fef7f692e1d6d2b",
    "research/accent-conversion-20261101/repos/TokAN/README.md":
        "e1686415f5cb77ed570f0284322fa67883663d52bed081c0f1287fff42fb2700",
    "research/accent-conversion-20261101/repos/TokAN/infer_wav.py":
        "85ccde2fca4e2d8dc34c686c5a9c4ee2a80fa666e1e8d5c7a9b50c6b4fd82bd5",
    "research/accent-conversion-20261101/repos/TokAN/demo.py":
        "e3335c07e4b6901f446c15cc19d5fd4a1cc595c3807f94cb9f52135bfcae332f",
    "research/accent-conversion-20261101/repos/TokAN/configs/tokan.model-only.yaml":
        "63280ebc0d0ad68730e780a11cca927e0890e2164ba966424caf9a4580fc8f45",
    "research/accent-conversion-20261101/repos/TokAN/requirements.txt":
        "31baee3dc62a6a5b68130b158a9ff3ec0702203cce9f753dc3febd822cf95c7f",
    "research/accent-conversion-20261101/repos/TokAN/tokan/model/ssl_quant/vq_joint.py":
        "504097caf3fdad4911fa5e6643af853072959935bd3430335d21becc789d6a13",
    "research/accent-conversion-20261101/repos/TokAN/tokan/model/arlm/arlm.py":
        "67a79a80047d9df51c342da5155c038ba367dae9d9212c35d4b3ad115b00ae3b",
    "research/accent-conversion-20261101/repos/TokAN/tokan/model/hift/generator.py":
        "7845d767e9dc6b3c1189c3174c96a1e01a24bb032b75e17f6dec1608b934ee93",
    "research/accent-conversion-20261101/repos/TokAN/tokan/model/ssl_wrapper/wavlm_extractor.py":
        "e11d07fb6269834443ee33ecdc21dba0357d1e748ffe99f2a6f7033027cb34e4",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
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
    "sdk_v0_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "model_input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
    "model_output_sample_rate_hz": OUTPUT_SAMPLE_RATE_HZ,
    "model_channels": CHANNELS,
    "model_sample_format": "f32",
    "model_hop_samples": HOP_SIZE,
    "model_feature_dim": FEATURE_DIM,
    "model_codebook_size": CODEBOOK_SIZE,
    "model_ssl_dim": SSL_DIM,
    "model_speaker_embed_dim": SPEAKER_EMBED_DIM,
    "model_flow_embed_dim": FLOW_EMBED_DIM,
    "model_default_beam_size": DEFAULT_BEAM_SIZE,
    "model_default_flow_steps": DEFAULT_FLOW_STEPS,
    "model_mode": "offline_whole_utterance",
    "model_incremental_streaming": False,
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
    "real_tokan_model": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No TokAN, WavLM-Large, quantizer, flow decoder or HiFT weight is loaded or executed.",
    "No PyTorch, torchaudio, Transformers, Resemblyzer, NumPy or SoundFile runtime is imported.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, transcript, speaker reference or consent record is consumed.",
    "No accent conversion, WER, speaker similarity, naturalness, latency, memory or RTF is measured here.",
    "The source-reported three-clip observations are provenance only and are not reproduced.",
    "The synthetic PCM accounting control is a contract control, never model output.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "arlm_checkpoint",
        "filename": "arlm.pt",
        "hf_repo_id": TOKAN_HF_REPO,
        "hf_subfolder": TOKAN_HF_SUBFOLDER,
        "sha256": None,
        "recorded_size_approx_mb": CHECKPOINT_APPROX_MB["arlm.pt"],
        "required": True,
    },
    {
        "id": "quantizer_flow_checkpoint",
        "filename": "quantizer.pt",
        "hf_repo_id": TOKAN_HF_REPO,
        "hf_subfolder": TOKAN_HF_SUBFOLDER,
        "sha256": None,
        "recorded_size_approx_mb": CHECKPOINT_APPROX_MB["quantizer.pt"],
        "required": True,
    },
    {
        "id": "hift_checkpoint",
        "filename": "hift.pt",
        "hf_repo_id": TOKAN_HF_REPO,
        "hf_subfolder": TOKAN_HF_SUBFOLDER,
        "sha256": None,
        "recorded_size_approx_mb": CHECKPOINT_APPROX_MB["hift.pt"],
        "required": True,
    },
    {
        "id": "wavlm_large_encoder",
        "model_name": WAVLM_MODEL_NAME,
        "layer": WAVLM_LAYER,
        "sha256": None,
        "recorded_size_approx_mb": WAVLM_APPROX_MB,
        "required": True,
    },
    {
        "id": "exact_runtime",
        "recorded_python": "3.11.5",
        "recorded_transformers_compatibility_pin": "4.45.2",
        "recorded_setuptools_compatibility_pin": "80.9.0",
        "runtime_lock_sha256": None,
        "required": True,
    },
    {
        "id": "source_license_record",
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_and_consent_record",
        "path": RIGHTS_RECORD_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "voice_cohort",
        "path": COHORT_MANIFEST_PATH,
        "required": True,
        "status": "absent",
        "present_sample_clips": 3,
        "sample_licence": "L2-ARCTIC CC BY-NC 4.0 research-only",
    },
)

CALLER_ASSET_FIELDS = (
    "arlm_checkpoint_path",
    "arlm_checkpoint_sha256",
    "channels",
    "config_path",
    "config_sha256",
    "consent_record_path",
    "consent_record_sha256",
    "encoder_cache_manifest_path",
    "encoder_cache_manifest_sha256",
    "encoder_cache_path",
    "hift_checkpoint_path",
    "hift_checkpoint_sha256",
    "license_record_path",
    "license_record_sha256",
    "quantizer_checkpoint_path",
    "quantizer_checkpoint_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_input_hz",
    "sample_rate_output_hz",
    "source_revision",
    "speaker_reference_path",
    "speaker_reference_sha256",
    "variant",
)

CALLER_FILE_PAIRS = (
    ("arlm_checkpoint_path", "arlm_checkpoint_sha256"),
    ("quantizer_checkpoint_path", "quantizer_checkpoint_sha256"),
    ("hift_checkpoint_path", "hift_checkpoint_sha256"),
    ("encoder_cache_manifest_path", "encoder_cache_manifest_sha256"),
    ("config_path", "config_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("speaker_reference_path", "speaker_reference_sha256"),
    ("consent_record_path", "consent_record_sha256"),
)
CALLER_DIR_FIELDS = ("encoder_cache_path", "runtime_path")
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "offline_whole_utterance"

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": "audio-sdk/tokan/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_revision_geometry_and_offline_variant"
        "_only; do_not_import_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_source_revision": TOKAN_COMMIT,
    "required_geometry": {
        "sample_rate_input_hz": INPUT_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": OUTPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
    },
    "notes": (
        "Every checkpoint, encoder manifest, config, licence, runtime lock, "
        "speaker reference and consent record must exist at an absolute path "
        "and match its declared SHA-256 before a caller may process audio."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "checkpoints_absent",
        "state": "absent",
        "requirement": (
            "Supply the three Piping/TokAN checkpoints arlm.pt, quantizer.pt and "
            "hift.pt under checkpoints/default; none exists in the workspace or "
            "this worktree."),
    },
    {
        "id": "checkpoint_digests_unpublished",
        "state": "absent",
        "requirement": (
            "Publish exact byte counts and SHA-256 values for all three "
            "checkpoints and the WavLM-Large encoder manifest at one immutable "
            "Hugging Face revision; the merged evidence records approximate "
            "sizes only."),
    },
    {
        "id": "wavlm_encoder_cache_absent",
        "state": "absent",
        "requirement": (
            "Supply the microsoft/wavlm-large layer-22 encoder cache or a "
            "hash-pinned exported encoder with its manifest; no cached snapshot "
            "remains after the reported disk cleanup."),
    },
    {
        "id": "runtime_unpinned_and_absent",
        "state": "absent",
        "requirement": (
            "Provide a hash-pinned isolated runtime (Python 3.11.5 recorded, "
            "Transformers 4.45.2 and setuptools 80.9.0 compatibility pins) with "
            "a complete lock at data/envs/tokan/requirements.lock; the "
            "upstream requirements.txt leaves torch, torchaudio, NumPy, "
            "SciPy, SoundFile, Resemblyzer and vector_quantize_pytorch "
            "unpinned."),
    },
    {
        "id": "source_license_absent",
        "state": "absent",
        "requirement": (
            "Add the upstream artifact licence at the pinned commit "
            "cbfc09a2716003463a0501ceae04ee62809c3822; the checkout has no "
            "LICENSE, COPYING or licence declaration, so derivative and "
            "redistribution rights are unresolved."),
    },
    {
        "id": "rights_and_consent_uncleared",
        "state": "absent",
        "requirement": (
            "Clear weight, training-data, voice-reference, consent, output-use "
            "and redistribution rights with complete notices; the L2-ARCTIC "
            "samples are CC BY-NC 4.0 research-only and no consent record "
            "exists."),
    },
    {
        "id": "voice_cohort_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared voice cohort with permitted source and "
            "target references, language/speaker groups, text and semantic "
            "truth, and separate text-preservation, identity and naturalness "
            "scoring; only three demo clips exist."),
    },
    {
        "id": "approved_reference_parity_absent",
        "state": "absent",
        "requirement": (
            "Produce an approved exact-runtime TokAN parity vector on frozen "
            "16 kHz input, including beam size 10, 32 flow steps, offline "
            "whole-utterance alignment and fresh-process reset."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_asset_identity",
        "The full 40-hex TokAN revision, three checkpoint SHA-256 values, "
        "WavLM-Large manifest and source licence match exact pins.",
    ),
    (
        "runtime_admission",
        "An isolated hash-pinned runtime with the recorded compatibility pins "
        "and a complete lock is admitted on a recorded platform.",
    ),
    (
        "artifact_rights_and_consent",
        "Source, weight, training-data, speaker-reference, consent, output-use "
        "and redistribution rights are cleared with complete notices.",
    ),
    (
        "exact_reference_parity",
        "An approved exact-runtime TokAN output matches the reference on frozen "
        "16 kHz mono PCM for one frozen configuration.",
    ),
    (
        "voice_cohort_and_scoring",
        "A rights-cleared held-out cohort scores text/semantic preservation, "
        "identity/similarity and naturalness as separate outcomes.",
    ),
    (
        "offline_streaming_separation",
        "The offline whole-utterance path is reproduced and never presented as "
        "incremental streaming; first-output and tail timing are measured.",
    ),
    (
        "opt_in_provider_intake",
        "Explicit opt-in provider intake, licence review, descriptor review and "
        "an independent public-surface decision are complete.",
    ),
    (
        "public_default_and_release",
        "Explicit default selection, resource/deadline evidence and release or "
        "public-benchmark approval are recorded; this package is off by default.",
    ),
)

VOICE_REQUIREMENTS: Tuple[Tuple[str, str, str], ...] = (
    (
        "permitted_source_and_target_references",
        "Freeze permitted input and target references with rights and consent.",
        "absent",
    ),
    (
        "task_language_and_speaker_groups",
        "Freeze task, language and speaker groups for the cohort.",
        "absent",
    ),
    (
        "text_and_semantic_preservation",
        "Preserve text and semantic content as its own outcome.",
        "not_measured",
    ),
    (
        "identity_similarity",
        "Measure identity or similarity to the target as a separate outcome.",
        "not_measured",
    ),
    (
        "naturalness",
        "Measure naturalness as a separate outcome.",
        "not_measured",
    ),
    (
        "alignment_and_output_timing",
        "Record alignment, first-output and tail timing for the exact runtime.",
        "structural_only",
    ),
    (
        "consent_reference_and_output_use",
        "Treat consent, reference availability and output use as independent gates.",
        "absent",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source": "research/accent-conversion-20261101/README.md",
    "source_sha256": SOURCE_PINS[
        "research/accent-conversion-20261101/README.md"],
    "clips": [
        {
            "l1_group": "Arabic",
            "utterance": "ABA a0046",
            "input_duration_s": 4.539,
            "output_duration_s": 3.0,
            "duration_ratio": 0.661,
            "runtime_s": 78.89,
            "rtf": 17.38,
            "whisper_tiny_wer": 0.0,
            "resemblyzer_cosine": 0.838,
        },
        {
            "l1_group": "Hindi",
            "utterance": "RRBI a0391",
            "input_duration_s": 3.49,
            "output_duration_s": 3.18,
            "duration_ratio": 0.911,
            "runtime_s": 63.74,
            "rtf": 18.26,
            "whisper_tiny_wer": 0.0,
            "resemblyzer_cosine": 0.798,
        },
        {
            "l1_group": "Korean",
            "utterance": "HJK a0103",
            "input_duration_s": 3.042,
            "output_duration_s": 2.76,
            "duration_ratio": 0.907,
            "runtime_s": 62.55,
            "rtf": 20.56,
            "whisper_tiny_wer": 0.0,
            "resemblyzer_cosine": 0.874,
        },
    ],
    "notes": (
        "Three demo utterances with the source clip also used as the speaker "
        "reference. WER is against Whisper-tiny transcripts, not manual truth. "
        "The accent-classifier proxy did not show consistent movement toward "
        "General American, and no blinded human listening occurred."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_voice_acceptance_plan_not_model_output")

CONTROL_SOURCE_SAMPLES = INPUT_SAMPLE_RATE_HZ * 3
CONTROL_OUTPUT_SAMPLES = OUTPUT_SAMPLE_RATE_HZ * 2
PCM_SAMPLE_CAP = 10_000_000

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "pcm_empty",
    "pcm_not_sequence",
    "pcm_none",
    "pcm_wrong_rate",
    "pcm_stereo",
    "pcm_nan",
    "pcm_pos_inf",
    "pcm_neg_inf",
    "pcm_out_of_range",
    "pcm_bool",
    "pcm_string",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_short_revision",
    "manifest_wrong_revision",
    "manifest_wrong_input_rate",
    "manifest_wrong_output_rate",
    "manifest_wrong_channels",
    "manifest_wrong_variant",
    "manifest_missing_asset",
)

MAX_MANIFEST_BYTES = 8 * 1024 ** 3


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
# Source checkout and asset audit.  Fixed local reads only; no network.
# ---------------------------------------------------------------------------

def _read_git_head(repository: Path) -> Optional[str]:
    marker = repository / ".git"
    if not marker.exists():
        return None
    if marker.is_file():
        try:
            text = marker.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if not text.startswith("gitdir:"):
            return None
        target = Path(text.split(":", 1)[1].strip())
        if not target.is_absolute():
            target = (repository / target).resolve()
    else:
        target = marker
    head_path = target / "HEAD"
    if not head_path.is_file():
        return None
    try:
        head = head_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not head.startswith("ref: "):
        return head if TOKAN_COMMIT_PATTERN.fullmatch(head) else None
    ref = head.split(":", 1)[1].strip()
    ref_path = target / ref
    if ref_path.is_file():
        try:
            value = ref_path.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        return value if TOKAN_COMMIT_PATTERN.fullmatch(value) else None
    packed = target / "packed-refs"
    if packed.is_file():
        try:
            for line in packed.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("^"):
                    continue
                digest, _, name = line.partition(" ")
                if name == ref and TOKAN_COMMIT_PATTERN.fullmatch(digest):
                    return digest
        except OSError:
            return None
    return None


def _license_candidates(repository: Path) -> List[str]:
    found: List[str] = []
    if not repository.is_dir():
        return found
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING",
                 "COPYING.md", "COPYING.txt"):
        if (repository / name).is_file():
            found.append(name)
    return found


def _checkpoint_paths() -> Dict[str, Path]:
    repository = SOURCE_ROOT / TOKAN_REPO_RELATIVE
    return {
        filename: repository / "checkpoints" / "default" / filename
        for filename in CHECKPOINT_FILENAMES
    }


def _wavlm_cache_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "research/accent-conversion-20261101/hf-cache/hub"
        / "models--microsoft--wavlm-large",
        SOURCE_ROOT / "research/accent-conversion-20261101/hf-cache"
        / "models--microsoft--wavlm-large",
        SOURCE_ROOT / "data/models/wavlm-large",
    ]


def _sample_clips() -> List[str]:
    directory = SOURCE_ROOT / SAMPLE_DATA_PATH
    if not directory.is_dir():
        return []
    return sorted(path.name for path in directory.iterdir()
                  if path.is_file() and path.suffix.lower() == ".wav")


def audit_assets() -> Dict[str, Any]:
    repository = SOURCE_ROOT / TOKAN_REPO_RELATIVE
    revision = _read_git_head(repository) if repository.is_dir() else None
    mismatches: List[str] = []
    checked = 0
    if repository.is_dir():
        for relative, digest in sorted(SOURCE_PINS.items()):
            if not relative.startswith(TOKAN_REPO_RELATIVE + "/"):
                continue
            local = SOURCE_ROOT / relative
            if not local.is_file():
                mismatches.append(relative)
                continue
            checked += 1
            if sha256(local.read_bytes()) != digest:
                mismatches.append(relative)
    checkpoints = {
        filename: path.is_file() for filename, path in _checkpoint_paths().items()
    }
    wavlm_present = any(path.exists() for path in _wavlm_cache_candidates())
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    licenses = _license_candidates(repository)
    readme = repository / "README.md"
    readme_declares = False
    if readme.is_file():
        try:
            text = readme.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            text = ""
        readme_declares = ("license" in text or "licence" in text
                           or "copyright" in text)
    return {
        "source_checkout_path": TOKAN_REPO_RELATIVE,
        "source_checkout_present": repository.is_dir(),
        "source_revision": revision,
        "source_revision_matches": revision == TOKAN_COMMIT,
        "source_files_checked": checked,
        "source_file_pins_match": (
            bool(checked) and not mismatches),
        "source_file_mismatches": mismatches,
        "license_files": licenses,
        "license_file_present": bool(licenses),
        "license_declared_in_readme": readme_declares,
        "checkpoint_dir_present": (
            repository / "checkpoints" / "default").is_dir(),
        "checkpoints_present": checkpoints,
        "all_checkpoints_present": all(checkpoints.values()),
        "wavlm_cache_present": wavlm_present,
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "rights_record_present": rights_record.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "sample_clips": _sample_clips(),
        "sample_clip_count": len(_sample_clips()),
        "requested_config": {
            "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
            "output_sample_rate_hz": OUTPUT_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "hop_size": HOP_SIZE,
            "feature_dim": FEATURE_DIM,
            "wavlm_layer": WAVLM_LAYER,
            "beam_size": DEFAULT_BEAM_SIZE,
            "flow_steps": DEFAULT_FLOW_STEPS,
        },
    }


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
# Deterministic synthetic PCM and voice-acceptance accounting.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, int]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def synthetic_source_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x70CAB1E5
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 37, 0.30) + 0.01 * noise)
    return samples


def synthetic_output_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x5EED70CA
    for index in range(CONTROL_OUTPUT_SAMPLES):
        state, noise = _lcg(state)
        samples.append(_triangle(index, 41, 0.25) + 0.02 * noise)
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = INPUT_SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> List[float]:
    if sample_rate_hz not in (INPUT_SAMPLE_RATE_HZ, OUTPUT_SAMPLE_RATE_HZ):
        raise Reject("unsupported sample rate")
    if channels != CHANNELS:
        raise Reject("only mono is supported")
    if not isinstance(signal, (list, tuple)):
        raise Reject("signal must be a sample sequence")
    if not signal:
        raise Reject("signal must be nonempty")
    if len(signal) > PCM_SAMPLE_CAP:
        raise Reject("signal exceeds the evidence cap")
    checked: List[float] = []
    for index, sample in enumerate(signal):
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise Reject(f"sample {index} is not numeric")
        value = float(sample)
        if not math.isfinite(value):
            raise Reject(f"sample {index} is not finite")
        if value < -1.0 or value > 1.0:
            raise Reject(f"sample {index} is outside [-1, 1]")
        checked.append(value)
    return checked


def pcm_summary(signal: Sequence[float], sample_rate_hz: int) -> Dict[str, Any]:
    values = validate_pcm(signal, sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak,
        "nonfinite_samples": 0,
        "sha256": sha256(canonical_bytes(list(values))),
    }


def duration_accounting(source_samples: int, output_samples: int
                        ) -> Dict[str, Any]:
    if not isinstance(source_samples, int) or isinstance(source_samples, bool):
        raise Reject("source sample count must be an integer")
    if not isinstance(output_samples, int) or isinstance(output_samples, bool):
        raise Reject("output sample count must be an integer")
    if source_samples <= 0 or output_samples <= 0:
        raise Reject("sample counts must be positive")
    source_duration = Fraction(source_samples, INPUT_SAMPLE_RATE_HZ)
    output_duration = Fraction(output_samples, OUTPUT_SAMPLE_RATE_HZ)
    ratio = output_duration / source_duration
    return {
        "source_duration_s": fraction_text(source_duration),
        "output_duration_s": fraction_text(output_duration),
        "duration_ratio": fraction_text(ratio),
        "duration_ratio_float": float(ratio),
        "duration_ratio_interpretation": (
            "output_duration_divided_by_source_duration"),
    }


def alignment_accounting(output_samples: int) -> Dict[str, Any]:
    return {
        "mode": "offline_whole_utterance",
        "streaming_supported": False,
        "first_output_sample": 0,
        "first_output_delay_samples": 0,
        "tail_samples": output_samples,
        "whole_clip_required": True,
        "note": (
            "TokAN inference is offline and non-incremental; these values are "
            "declared by the pinned source and are not a device measurement."),
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_source = synthetic_source_pcm()
    good_output = synthetic_output_pcm()
    good_manifest = _shape_only_manifest()

    def case(case_id: str, action) -> Dict[str, str]:
        try:
            action()
        except Reject as error:
            return {"case": case_id, "result": "rejected",
                    "reason": str(error)}
        except Exception as error:  # noqa: BLE001 - recorded, never swallowed
            return {"case": case_id, "result": "unexpected_error",
                    "reason": type(error).__name__ + ": " + str(error)}
        return {"case": case_id, "result": "accepted", "reason": ""}

    def wrong(key: str, value: Any):
        manifest = dict(good_manifest)
        manifest[key] = value
        return lambda: validate_caller_manifest(manifest)

    def drop(key: str):
        manifest = {k: v for k, v in good_manifest.items() if k != key}
        return lambda: validate_caller_manifest(manifest)

    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_source, 8000)),
        ("pcm_stereo", lambda: validate_pcm(good_source, INPUT_SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("hift_checkpoint_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "arlm_checkpoint_path", "checkpoints/default/arlm.pt")),
        ("manifest_bad_sha", wrong("arlm_checkpoint_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "cbfc09a2")),
        ("manifest_wrong_revision", wrong("source_revision", "0" * 40)),
        ("manifest_wrong_input_rate", wrong("sample_rate_input_hz", 22050)),
        ("manifest_wrong_output_rate", wrong("sample_rate_output_hz", 16000)),
        ("manifest_wrong_channels", wrong("channels", 2)),
        ("manifest_wrong_variant", wrong("variant", "incremental_streaming")),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(good_manifest, arlm_checkpoint_path=(
                "/nonexistent/tokan-checkpoints/arlm.pt")))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    good = pcm_summary(good_source, INPUT_SAMPLE_RATE_HZ)
    good_out = pcm_summary(good_output, OUTPUT_SAMPLE_RATE_HZ)
    if good["samples"] != CONTROL_SOURCE_SAMPLES:
        raise Reject("synthetic source control mismatch")
    if good_out["samples"] != CONTROL_OUTPUT_SAMPLES:
        raise Reject("synthetic output control mismatch")
    return results


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It is only used to exercise fail-closed shape checks.  Validation reaches
    the missing-asset branch before any file is read.
    """

    root = "/nonexistent/tokan-evidence-fixture"
    digest = "0" * 64
    return {
        "arlm_checkpoint_path": root + "/arlm.pt",
        "arlm_checkpoint_sha256": digest,
        "channels": CHANNELS,
        "config_path": root + "/tokan.model-only.yaml",
        "config_sha256": digest,
        "consent_record_path": root + "/consent.json",
        "consent_record_sha256": digest,
        "encoder_cache_manifest_path": root + "/encoder-manifest.json",
        "encoder_cache_manifest_sha256": digest,
        "encoder_cache_path": root + "/encoder",
        "hift_checkpoint_path": root + "/hift.pt",
        "hift_checkpoint_sha256": digest,
        "license_record_path": root + "/rights.json",
        "license_record_sha256": digest,
        "quantizer_checkpoint_path": root + "/quantizer.pt",
        "quantizer_checkpoint_sha256": digest,
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "runtime_path": root + "/runtime",
        "sample_rate_input_hz": INPUT_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": OUTPUT_SAMPLE_RATE_HZ,
        "source_revision": TOKAN_COMMIT,
        "speaker_reference_path": root + "/reference.wav",
        "speaker_reference_sha256": digest,
        "variant": CALLER_VARIANT,
    }


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_MANIFEST_BYTES:
                raise Reject("asset exceeds the evidence cap")
            digest.update(chunk)
    return digest.hexdigest()


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise Reject("manifest must be an object")
    expected = set(CALLER_ASSET_FIELDS)
    present = set(manifest)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        raise Reject("manifest missing fields: " + ",".join(missing))
    if extra:
        raise Reject("manifest has unknown fields: " + ",".join(extra))
    for field in CALLER_SHA_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise Reject("manifest " + field + " is not a lowercase SHA-256")
    for first, _ in CALLER_FILE_PAIRS:
        value = manifest[first]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + first + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + first + " must be absolute")
    for field in CALLER_DIR_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + field + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + field + " must be absolute")
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not TOKAN_COMMIT_PATTERN.fullmatch(
            revision):
        raise Reject("manifest source_revision must be a full 40-hex commit")
    if revision != TOKAN_COMMIT:
        raise Reject("manifest source_revision does not match the pinned TokAN commit")
    for field, expected_value in (
            ("sample_rate_input_hz", INPUT_SAMPLE_RATE_HZ),
            ("sample_rate_output_hz", OUTPUT_SAMPLE_RATE_HZ),
            ("channels", CHANNELS)):
        value = manifest[field]
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject("manifest " + field + " must be an integer")
        if value != expected_value:
            raise Reject("manifest " + field + " mismatch")
    if manifest["variant"] != CALLER_VARIANT:
        raise Reject("manifest variant must be " + CALLER_VARIANT)
    for field in CALLER_DIR_FIELDS:
        if not Path(manifest[field]).is_dir():
            raise Reject("manifest " + field + " directory is missing")
    total_bytes = 0
    for path_field, sha_field in CALLER_FILE_PAIRS:
        path = Path(manifest[path_field])
        if not path.is_file():
            raise Reject("manifest " + path_field + " file is missing")
        actual = _hash_file(path)
        if actual != manifest[sha_field]:
            raise Reject("manifest " + path_field + " SHA-256 mismatch")
        total_bytes += path.stat().st_size
    return {
        "accepted": True,
        "source_revision": revision,
        "variant": CALLER_VARIANT,
        "sample_rate_input_hz": INPUT_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": OUTPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
    }


def build_control() -> Dict[str, Any]:
    source = synthetic_source_pcm()
    output = synthetic_output_pcm()
    source_summary = pcm_summary(source, INPUT_SAMPLE_RATE_HZ)
    output_summary = pcm_summary(output, OUTPUT_SAMPLE_RATE_HZ)
    durations = duration_accounting(len(source), len(output))
    alignment = alignment_accounting(len(output))
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
            "output_sample_rate_hz": OUTPUT_SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "hop_size": HOP_SIZE,
            "mode": "offline_whole_utterance",
            "incremental_streaming": False,
        },
        "source_pcm": source_summary,
        "output_pcm": output_summary,
        "duration": durations,
        "alignment": alignment,
        "acceptance_outcomes": [
            {
                "id": "text_and_semantic_preservation",
                "measured": False,
                "value": None,
                "reason": "no real model, transcript truth or cohort",
            },
            {
                "id": "identity_similarity",
                "measured": False,
                "value": None,
                "reason": "no real speaker reference or embedder runtime",
            },
            {
                "id": "naturalness",
                "measured": False,
                "value": None,
                "reason": "no authorized listening panel",
            },
            {
                "id": "alignment_and_output_timing",
                "measured": False,
                "value": None,
                "reason": "structural offline alignment only; no device clock",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "manifest_missing_field", "manifest_missing_asset"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic PCM accounting control only. It is not TokAN output, "
            "not real accent-conversion audio, not a quality or timing result "
            "and cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report model.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["source_checkout_present"]
        and observed["source_revision_matches"]
        and observed["source_file_pins_match"]
        and observed["license_file_present"]
        and observed["all_checkpoints_present"]
        and observed["wavlm_cache_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["rights_record_present"]
        and observed["cohort_manifest_present"])
    if complete:
        result = "asset_set_complete_pending_parity"
    elif observed["source_checkout_present"]:
        result = "source_present_assets_unqualified"
    else:
        result = "absent"
    return {
        "qualified": False,
        "audit_result": result,
        "source_present": observed["source_checkout_present"],
        "source_revision_matches": observed["source_revision_matches"],
        "source_file_pins_match": observed["source_file_pins_match"],
        "license_present": observed["license_file_present"],
        "all_checkpoints_present": observed["all_checkpoints_present"],
        "wavlm_cache_present": observed["wavlm_cache_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "rights_record_present": observed["rights_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "sample_clip_count": observed["sample_clip_count"],
        "observed": observed,
        "note": (
            "An exact source revision and matching source-file hashes are not "
            "a licence, weights, runtime, cohort or quality result. Presence "
            "of the source does not qualify the candidate."),
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
        for item, requirement, status in VOICE_REQUIREMENTS
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
                "The source checkout is exact but unlicensed, the three "
                "checkpoints and WavLM-Large encoder are absent, no exact "
                "checkpoint digest or hash-pinned runtime is published, no "
                "rights-cleared voice cohort or consent record exists and no "
                "approved parity vector is available."),
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
        "source_checkout": {
            "path": TOKAN_REPO_RELATIVE,
            "revision": TOKAN_COMMIT,
            "hf_repo_id": TOKAN_HF_REPO,
            "hf_subfolder": TOKAN_HF_SUBFOLDER,
            "wavlm_model": WAVLM_MODEL_NAME,
            "wavlm_layer": WAVLM_LAYER,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "voice_profile": {
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
                "Structural accounting passes, but no real model, licensed "
                "reference set, consent record, rights-cleared cohort, target "
                "runtime or approved parity exists, so the voice profile is "
                "not satisfied for qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
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
        "missing_historical_artifacts": [
            MISSING_WEIGHTS_PATH,
            COHORT_MANIFEST_PATH,
            RIGHTS_RECORD_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model or audio runtime is imported.",
            "The source checkout is inspected by reading .git/HEAD and refs plus file hashes.",
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
