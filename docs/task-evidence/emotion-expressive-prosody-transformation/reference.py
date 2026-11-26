# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for the task-local
SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION package.

The exact licensed input-speech emotion/expressive-prosody transformation
source, checkpoint, target-emotion label set, consent-cleared target voices and
hash-pinned runtime are absent. The merged research record (candidate matrix
record 57) is ``unavailable/blocked`` and names no model, checkpoint, label set
or repository revision, so none is invented here.

This module never imports a model or audio runtime, never loads or executes a
model, never reads or writes real audio, never downloads anything and never
measures a device clock. It provides four verifiable pieces:

* a fail-closed source/asset audit over fixed workspace paths that records the
  absent source, checkpoint, label set, target-voice consent, runtime, rights
  record, cohort and parity records and probes fixed paths for accidental
  assets;
* a caller-supplied-asset manifest contract validated without execution, with
  every malformed, missing, invalid or nonfinite control rejected before use;
* a fail-closed target-condition admission that accepts only the identity
  prosody baseline and rejects every non-identity emotion/prosody target because
  the candidate transform is absent;
* a deterministic synthetic identity-prosody accounting control at the public
  v0 geometry (16 kHz mono float32, 160 samples per frame) that checks exact
  source/identity sample preservation and offline-only alignment without
  asserting any candidate geometry or output.

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
from typing import Any, Dict, List, Optional, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = Path(
    os.environ.get("SDK_ROOT", str(TASK_DIR.parents[2]))
).resolve()
SOURCE_ROOT = Path(
    os.environ.get("SOURCE_ROOT", str(SDK_ROOT.parents[2]))
).resolve()
TASK_BOARD_REL = "audio-benchmark-platform/plan/swarm/TASKS.json"

VERSION = "0.1.0"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
REPORT_SCHEMA = (
    "audio-sdk/emotion-expressive-prosody-transformation-report/0.1")
CALLER_SCHEMA = (
    "audio-sdk/emotion-expressive-prosody-transformation/"
    "caller-supplied-asset/0.1")

TASK_ID = "SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION"
TITLE = "Emotion / expressive prosody transformation"
COMPONENT = "emotion-expressive-prosody-transformation"
REPOSITORY = "audio-sdk"
MODE = "feasibility"
PROFILE = "voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
QUALIFICATION = "not_qualified"
BASE_COMMIT = "b43a7e13175949cda78f0ea64953e4a585d43c67"
BRANCH = "swarm/SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION"
REVIEWER = "reviewer-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    + TASK_ID)
TASK_PREFIX = (
    "docs/task-evidence/emotion-expressive-prosody-transformation/")

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_PERIOD_NS = 62500

PROBABILITY_SCALE = 1000000
MICRO_SCALE = 1000000
TARGET_INTENSITY_FULL = 1000
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000
CONTROL_SOURCE_SAMPLES = 32000
CONTROL_LEAD_SAMPLES = 4000
CONTROL_VOICED_END = 24000
CONTROL_TAIL_START = 30000
CONTROL_VOICED_PERIOD = 80
CONTROL_VOICED_AMPLITUDE_MICRO = 300000
CONTROL_NOISE_AMPLITUDE_MICRO = 8000
PCM_SAMPLE_CAP = 10000000
MAX_MANIFEST_BYTES = 8 * 1024 ** 3

TASK_KIND = "speech_to_speech_prosody_transformation"
COMPARISON_BASELINE = "identity_prosody"
CALLER_VARIANT = "offline_whole_utterance"
IDENTITY_LABEL = "identity"
MAX_TARGET_INTENSITY = 1000

CANDIDATE_RECORD = 57
CANDIDATE_RECORD_PATH = (
    "research/voice-enhancement-20261101/candidate_matrix.csv")
CANDIDATE_REPORT_PATHS = (
    "research/voice-enhancement-20261101/"
    "agent-transform-spatial-trials/REPORT.md",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md",
)

MISSING_SOURCE_PATH = (
    "data/checkouts/emotion-expressive-prosody-transformation")
MISSING_WEIGHTS_PATH = (
    "data/models/emotion-expressive-prosody-transformation/checkpoint")
LABEL_SET_PATH = "data/labels/emotion-expressive-prosody-labels.json"
TARGET_VOICE_CONSENT_PATH = (
    "data/rights/emotion-expressive-prosody-target-voice-consent.json")
RIGHTS_RECORD_PATH = (
    "data/rights/emotion-expressive-prosody-rights.json")
COHORT_MANIFEST_PATH = (
    "data/runs/emotion-expressive-prosody-cohort/manifest.json")
PARITY_MANIFEST_PATH = (
    "data/runs/emotion-expressive-prosody-parity/manifest.json")
RUNTIME_ENV_PATH = "data/envs/emotion-expressive-prosody-transformation"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"

ARTIFACT_FILES: Tuple[str, ...] = (
    "README.md",
    "LICENSES.md",
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
    "research/voice-enhancement-20261101/candidate_matrix.csv": (
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245"
    ),
    "research/voice-enhancement-20261101/"
    "agent-transform-spatial-trials/REPORT.md": (
        "fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b"
    ),
    "research/voice-enhancement-20261101/"
    "agent-transform-space/REPORT.md": (
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4"
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

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": SAMPLE_FORMAT,
    "sdk_v0_frame_samples": FRAME_SAMPLES,
    "sdk_v0_sample_period_ns": SAMPLE_PERIOD_NS,
    "candidate_geometry_status": "unestablished",
    "candidate_geometry_asserted": False,
    "target_condition_status": "unestablished",
    "target_emotion_labels_present": False,
    "control_input_sample_rate_hz": SAMPLE_RATE_HZ,
    "control_output_sample_rate_hz": SAMPLE_RATE_HZ,
    "control_channels": CHANNELS,
    "control_sample_format": SAMPLE_FORMAT,
    "control_mode": "offline_whole_utterance",
    "control_incremental_streaming": False,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "audio_added": False,
    "ci_change": False,
    "corpus_added": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "model_loaded": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
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
    "real_candidate_model": False,
    "real_corpus": False,
    "real_weights": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "weights_downloaded": False,
    "weights_loaded": False,
    "write_scope": TASK_PREFIX,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No input-speech emotion/expressive-prosody model, checkpoint, config, "
    "target-emotion label set, style embedding, target voice or runtime is "
    "downloaded, copied, loaded, imported or executed.",
    "No PyTorch, torchaudio, Transformers, NumPy, SoundFile, vocoder or TTS "
    "runtime is imported.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, transcript, target voice, consent record or "
    "listening panel is consumed.",
    "No emotion realization, prosody change, content preservation, speaker "
    "similarity, naturalness, latency, memory, RTF or device timing is "
    "measured here.",
    "The synthetic identity-prosody control is an accounting control, never "
    "candidate output and never transformed speech.",
    "No candidate sample rate, frame size, label taxonomy, intensity scale, "
    "timing protocol or output geometry is asserted.",
    "No sibling accent, voice-conversion or TTS result is attributed to this "
    "row.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI "
    "changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_checkout",
        "recorded_url": None,
        "revision": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "model_checkpoint",
        "sha256": None,
        "byte_count": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "model_config",
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "target_emotion_label_set",
        "path": LABEL_SET_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "style_conditioning_asset",
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "target_voice_reference_and_consent",
        "path": TARGET_VOICE_CONSENT_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "exact_runtime",
        "runtime_lock_sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "rights_record",
        "path": RIGHTS_RECORD_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "voice_cohort",
        "path": COHORT_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
    {
        "id": "parity_vector",
        "path": PARITY_MANIFEST_PATH,
        "required": True,
        "status": "absent",
    },
)

CALLER_ASSET_FIELDS = (
    "asset_storage",
    "channels",
    "checkpoint_path",
    "checkpoint_sha256",
    "comparison_baseline",
    "emotion_label_set_path",
    "emotion_label_set_sha256",
    "model_config_path",
    "model_config_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_input_hz",
    "sample_rate_output_hz",
    "source_checkout_path",
    "source_revision",
    "style_conditioning_path",
    "style_conditioning_sha256",
    "target_emotion_label",
    "target_intensity_milli",
    "target_voice_consent_path",
    "target_voice_consent_sha256",
    "target_voice_reference_path",
    "target_voice_reference_sha256",
    "task_kind",
    "variant",
)

CALLER_FILE_PAIRS = (
    ("checkpoint_path", "checkpoint_sha256"),
    ("model_config_path", "model_config_sha256"),
    ("emotion_label_set_path", "emotion_label_set_sha256"),
    ("style_conditioning_path", "style_conditioning_sha256"),
    ("target_voice_reference_path", "target_voice_reference_sha256"),
    ("target_voice_consent_path", "target_voice_consent_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
)
CALLER_DIR_FIELDS = ("source_checkout_path", "runtime_path")
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": CALLER_SCHEMA,
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "asset_storage": "external",
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_revision_shape_geometry_task_kind_"
        "target_condition_and_offline_variant_only; do_not_import_or_execute_"
        "in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_task_kind": TASK_KIND,
    "required_comparison_baseline": COMPARISON_BASELINE,
    "required_variant": CALLER_VARIANT,
    "required_source_revision": None,
    "revision_pin_available": False,
    "required_geometry": {
        "channels": CHANNELS,
        "sample_rate_input_hz": None,
        "sample_rate_output_hz": None,
        "status": "unestablished",
    },
    "target_condition": {
        "label_required": True,
        "label_regex": "^[a-z][a-z0-9_]{1,63}$",
        "intensity_milli_min": 1,
        "intensity_milli_max": MAX_TARGET_INTENSITY,
        "label_set_asset_required": True,
    },
    "notes": (
        "Every checkpoint, config, emotion label set, style conditioning "
        "asset, target-voice reference, target-voice consent, rights record, "
        "runtime lock and runtime directory must exist at an absolute path and "
        "match its declared SHA-256 before a caller may process audio. The "
        "package never imports or executes the caller's source. No upstream "
        "revision is pinned because the merged record names no repository."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "input_speech_transform_model_absent",
        "state": "absent",
        "requirement": (
            "Name and supply the exact input-speech emotion/expressive-prosody "
            "transformation source at an immutable revision; candidate matrix "
            "record 57 names no model, repository, revision or per-file "
            "manifest, so no candidate identity can be pinned."),
    },
    {
        "id": "checkpoint_and_config_absent",
        "state": "absent",
        "requirement": (
            "Supply the exact inference checkpoint and model configuration "
            "with byte counts and SHA-256 values at one immutable revision; no "
            "checkpoint was downloaded, staged or identified by digest."),
    },
    {
        "id": "target_emotion_condition_absent",
        "state": "absent",
        "requirement": (
            "Supply the target emotion/style label taxonomy, intensity scale, "
            "style conditioning asset and any embedding table with digests; "
            "the record states that no target emotion labels are staged."),
    },
    {
        "id": "consent_cleared_target_voices_absent",
        "state": "absent",
        "requirement": (
            "Supply consent-cleared target/reference voices and permitted "
            "source/target pairs with explicit target-speaker consent, "
            "reference availability and output-use records; the record states "
            "that no consent-cleared target voices are staged."),
    },
    {
        "id": "runtime_absent",
        "state": "absent",
        "requirement": (
            "Provide an isolated hash-pinned runtime with a complete package "
            "lock at " + RUNTIME_LOCK_PATH + " and a recorded platform; no "
            "environment, package pin or lock exists."),
    },
    {
        "id": "rights_and_output_use_uncleared",
        "state": "absent",
        "requirement": (
            "Clear code, weight, training-data, corpus, target-voice, "
            "derivative-output, redistribution and product-use rights with "
            "complete notices; no rights record exists."),
    },
    {
        "id": "voice_cohort_and_parity_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared task-matched cohort with language, "
            "speaker and emotion groups, transcripts, held-out splits and an "
            "approved exact-runtime parity vector; no cohort or parity "
            "manifest exists."),
    },
    {
        "id": "geometry_timing_and_adapter_absent",
        "state": "absent",
        "requirement": (
            "Establish the exact candidate rate, channels, frame, streaming or "
            "offline mode, content delay, first-output/tail timing and host "
            "memory budget, then complete opt-in adapter intake; no candidate "
            "geometry or timing result exists."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_artifact_identity",
        "The exact model source, full 40-hex revision, checkpoint, config, "
        "emotion label set and style conditioning assets match immutable "
        "digests.",
    ),
    (
        "runtime_admission",
        "An isolated hash-pinned runtime with a complete lock is admitted on a "
        "recorded platform.",
    ),
    (
        "artifact_rights_consent_and_output_use",
        "Code, weight, training-data, corpus, target-voice, derivative-output, "
        "redistribution and product-use rights are cleared with complete "
        "notices and explicit consent.",
    ),
    (
        "exact_reference_parity",
        "An approved exact-runtime candidate output and its identity-prosody "
        "baseline match a frozen vector on one frozen input and configuration.",
    ),
    (
        "frozen_voice_cohort",
        "A rights-cleared, label-complete, task-matched held-out cohort covers "
        "language, speaker and emotion groups with frozen transcripts.",
    ),
    (
        "content_identity_emotion_naturalness_results",
        "Independent results separate text/semantic preservation, identity or "
        "similarity, target emotion realization and naturalness.",
    ),
    (
        "alignment_timing_and_streaming",
        "Alignment, first-output/tail timing, memory, streaming state and "
        "device deadline behaviour are measured for the exact runtime.",
    ),
    (
        "opt_in_adapter_intake_and_release",
        "Opt-in provider/adapter intake, descriptor review, independent "
        "exact-head review and explicit default/release approval are complete.",
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
        "Freeze task, language, speaker and emotion groups for the cohort.",
        "absent",
    ),
    (
        "text_and_semantic_preservation",
        "Preserve text and semantic content as its own outcome.",
        "not_measured",
    ),
    (
        "identity_similarity",
        "Measure identity or similarity as a separate outcome.",
        "not_measured",
    ),
    (
        "target_emotion_realization",
        "Measure the intended emotion/prosody target separately from content "
        "and identity.",
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
        "Treat consent, reference availability and output use as independent "
        "gates.",
        "absent",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source": CANDIDATE_RECORD_PATH,
    "source_sha256": SOURCE_PINS[CANDIDATE_RECORD_PATH],
    "record": CANDIDATE_RECORD,
    "record_name": TITLE,
    "record_status": "unavailable/blocked",
    "finding": (
        "No input-speech conversion model, target emotion labels or "
        "consent-cleared target voices are staged."),
    "comparison_baseline": "Identity prosody; fixed style/target-speaker pipeline",
    "report_paths": list(CANDIDATE_REPORT_PATHS),
    "sibling_context_not_attributed": [
        "No StyleTTS 2, CosyVoice, OpenVoice, Seed-VC, MeanVC2, LLVC or any "
        "other sibling TTS/voice-conversion result is attributed to this row.",
        "No accent-conversion result is attributed to this row.",
        "No F0 contour smoothing result is attributed to this row.",
        "The research audit did not run a candidate for this row.",
    ],
    "notes": (
        "No candidate output, checkpoint, label set or runtime was acquired. "
        "No duration, WER, emotion accuracy, similarity, naturalness, latency "
        "or RTF value is attributed to this candidate."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_identity_prosody_acceptance_plan_not_model_output")

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
    "manifest_nonhex_revision",
    "manifest_wrong_variant",
    "manifest_wrong_task_kind_tts",
    "manifest_wrong_task_kind_voice_conversion",
    "manifest_wrong_baseline",
    "manifest_channels_zero",
    "manifest_channels_float",
    "manifest_rate_below_range",
    "manifest_rate_above_range",
    "manifest_rate_bool",
    "manifest_empty_emotion_label",
    "manifest_bad_emotion_label",
    "manifest_intensity_zero",
    "manifest_intensity_above",
    "manifest_intensity_bool",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
    "manifest_missing_consent",
    "manifest_wrong_storage",
    "target_not_object",
    "target_missing_intensity",
    "target_unknown_label",
    "target_nonidentity_label",
    "target_intensity_not_full",
    "target_wrong_task_kind",
    "target_wrong_variant",
    "target_wrong_baseline",
)

COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
LABEL_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


class ReferenceRejection(ValueError):
    """Deterministic rejection that never mutates accepted state."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


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


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# ---------------------------------------------------------------------------
# Fixed-path source, asset and absence audit.
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
        return head if COMMIT_PATTERN.fullmatch(head) else None
    ref = head.split(":", 1)[1].strip()
    ref_path = target / ref
    if ref_path.is_file():
        try:
            value = ref_path.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        return value if COMMIT_PATTERN.fullmatch(value) else None
    packed = target / "packed-refs"
    if packed.is_file():
        try:
            for line in packed.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("^"):
                    continue
                digest, _, name = line.partition(" ")
                if name == ref and COMMIT_PATTERN.fullmatch(digest):
                    return digest
        except OSError:
            return None
    return None


def _license_candidates(repository: Path) -> List[str]:
    found: List[str] = []
    if not repository.is_dir():
        return found
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING",
                 "COPYING.md", "COPYING.txt", "NOTICE"):
        if (repository / name).is_file():
            found.append(name)
    return found


def _source_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / MISSING_SOURCE_PATH,
        SOURCE_ROOT / "data/checkouts/emotion-expressive-prosody",
        SOURCE_ROOT / "data/checkouts/expressive-prosody",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/"
        "emotion-expressive-prosody-transformation",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/"
        "expressive-prosody",
        SOURCE_ROOT / "research/voice-conversion-eval-20261101/repos/"
        "emotion-prosody",
    ]


def _weights_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "data/models/emotion-expressive-prosody-transformation",
        SOURCE_ROOT / "data/models/emotion-prosody",
        SOURCE_ROOT / "data/models/expressive-prosody",
        SOURCE_ROOT / "data/weights/emotion-expressive-prosody",
        SOURCE_ROOT / "research/voice-enhancement-20261101/repos/"
        "emotion-expressive-prosody-transformation/checkpoints",
    ]


ABSENCE_PROBES: Tuple[str, ...] = (
    "data/checkouts/emotion-expressive-prosody-transformation",
    "data/checkouts/emotion-expressive-prosody",
    "data/checkouts/expressive-prosody",
    "data/models/emotion-expressive-prosody-transformation",
    "data/models/emotion-prosody",
    "data/models/expressive-prosody",
    "data/weights/emotion-expressive-prosody",
    "data/labels/emotion-expressive-prosody-labels.json",
    "data/rights/emotion-expressive-prosody-rights.json",
    "data/rights/emotion-expressive-prosody-target-voice-consent.json",
    "data/envs/emotion-expressive-prosody-transformation",
    "data/envs/emotion-expressive-prosody-transformation/requirements.lock",
    "data/runs/emotion-expressive-prosody-cohort/manifest.json",
    "data/runs/emotion-expressive-prosody-parity/manifest.json",
    TASK_PREFIX + "reference_output.wav",
    TASK_PREFIX + "cohort",
)


def probe_absence() -> List[Dict[str, Any]]:
    return [
        {"path": relative, "exists": (SOURCE_ROOT / relative).exists()}
        for relative in ABSENCE_PROBES
    ]


def audit_assets() -> Dict[str, Any]:
    source_paths = _source_candidates()
    present_sources = [path for path in source_paths if path.is_dir()]
    repository = present_sources[0] if present_sources else None
    revision = _read_git_head(repository) if repository is not None else None
    licenses = _license_candidates(repository) if repository is not None else []
    weight_paths = _weights_candidates()
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    label_set = SOURCE_ROOT / LABEL_SET_PATH
    target_voice_consent = SOURCE_ROOT / TARGET_VOICE_CONSENT_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity_manifest = SOURCE_ROOT / PARITY_MANIFEST_PATH
    reference_audio = SOURCE_ROOT / (TASK_PREFIX + "reference_output.wav")
    probes = probe_absence()
    return {
        "source_checkout_path": MISSING_SOURCE_PATH,
        "source_checkout_present": repository is not None,
        "source_revision": revision,
        "source_revision_pin_available": False,
        "source_revision_matches": False,
        "source_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.is_dir()}
            for path in source_paths
        ],
        "license_files": licenses,
        "license_file_present": bool(licenses),
        "weights_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in weight_paths
        ],
        "weights_present": any(path.exists() for path in weight_paths),
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "rights_record_present": rights_record.is_file(),
        "emotion_label_set_present": label_set.is_file(),
        "target_voice_consent_present": target_voice_consent.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "reference_audio_present": reference_audio.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "task_kind": TASK_KIND,
            "comparison_baseline": COMPARISON_BASELINE,
            "geometry_status": "unestablished",
            "target_condition_status": "unestablished",
            "control_sample_rate_hz": SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": FRAME_SAMPLES,
            "upstream_revision": None,
        },
    }


def task_row_identity() -> Dict[str, Any]:
    path = SOURCE_ROOT / TASK_BOARD_REL
    if not path.is_file():
        raise ReferenceRejection("task board is unavailable at " + TASK_BOARD_REL)
    try:
        document = require_json_object(load_strict_json(path))
    except (OSError, UnicodeDecodeError) as error:
        raise ReferenceRejection("task board unreadable") from error
    rows = [row for row in document.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    if len(rows) != 1:
        raise ReferenceRejection("expected exactly one linked task row")
    row = rows[0]
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    if stable["id"] != TASK_ID or stable["component"] != COMPONENT:
        raise ReferenceRejection("linked task row identity mismatch")
    if stable["repository"] != REPOSITORY or stable["mode"] != MODE:
        raise ReferenceRejection("linked task row repository/mode mismatch")
    claim = row.get("claim")
    if not isinstance(claim, dict):
        raise ReferenceRejection("linked task row claim missing")
    if claim.get("base_commit") != BASE_COMMIT:
        raise ReferenceRejection("claim base commit mismatch")
    if claim.get("branch") != BRANCH:
        raise ReferenceRejection("claim branch mismatch")
    if claim.get("worktree") != CLAIM_WORKTREE:
        raise ReferenceRejection("claim worktree mismatch")
    if claim.get("reviewer") != REVIEWER:
        raise ReferenceRejection("claim reviewer mismatch")
    return {
        "source": TASK_BOARD_REL,
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(canonical_text(stable).encode("utf-8")),
        "full_tasks_json_hashed": False,
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "note": (
            "Only stable linked-row fields are read and gated. The mutable "
            "full plan/swarm/TASKS.json is never hashed, pinned or used as a "
            "digest source."),
        "claim": {
            "base_commit": claim["base_commit"],
            "branch": claim["branch"],
            "worktree": claim["worktree"],
            "reviewer": claim["reviewer"],
        },
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic PCM, identity control and target admission.
# ---------------------------------------------------------------------------

def _lcg(state: int) -> Tuple[int, float]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, (state / 4294967296.0) * 2.0 - 1.0


def _triangle(index: int, period: int) -> float:
    """Zero-mean triangle in [-1, 1]; integer phase arithmetic only."""
    phase = index % period
    return (2 * abs(2 * phase - period) - period) / float(period)


def synthetic_source_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x13579BDF
    amplitude = CONTROL_VOICED_AMPLITUDE_MICRO / MICRO_SCALE
    noise_amplitude = CONTROL_NOISE_AMPLITUDE_MICRO / MICRO_SCALE
    for index in range(CONTROL_SOURCE_SAMPLES):
        state, noise = _lcg(state)
        if index < CONTROL_LEAD_SAMPLES or index >= CONTROL_TAIL_START:
            value = 0.0
        elif index < CONTROL_VOICED_END:
            rising = (index - CONTROL_LEAD_SAMPLES) * MICRO_SCALE
            falling = (CONTROL_VOICED_END - index) * MICRO_SCALE
            ramp = min(MICRO_SCALE, rising // 2000, falling // 2000)
            value = (amplitude * _triangle(index, CONTROL_VOICED_PERIOD)
                     * (ramp / MICRO_SCALE) + noise_amplitude * noise)
        else:
            value = noise_amplitude * noise
        samples.append(value)
    return samples


def validate_pcm(signal: Any, sample_rate_hz: int = SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> List[float]:
    if isinstance(sample_rate_hz, bool) or not isinstance(sample_rate_hz, int):
        raise ReferenceRejection("invalid_sample_rate")
    if sample_rate_hz != SAMPLE_RATE_HZ:
        raise ReferenceRejection("unsupported_control_sample_rate")
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise ReferenceRejection("invalid_channels")
    if channels != CHANNELS:
        raise ReferenceRejection("only_mono_is_supported")
    if not isinstance(signal, (list, tuple)):
        raise ReferenceRejection("signal_must_be_a_sample_sequence")
    if not signal:
        raise ReferenceRejection("signal_must_be_nonempty")
    if len(signal) > PCM_SAMPLE_CAP:
        raise ReferenceRejection("signal_exceeds_the_evidence_cap")
    checked: List[float] = []
    for index, sample in enumerate(signal):
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise ReferenceRejection(f"sample_{index}_is_not_numeric")
        value = float(sample)
        if not math.isfinite(value):
            raise ReferenceRejection(f"sample_{index}_is_not_finite")
        if value < -1.0 or value > 1.0:
            raise ReferenceRejection(f"sample_{index}_is_outside_finite_range")
        checked.append(value)
    return checked


def _quantized_micro(values: Sequence[float]) -> List[int]:
    return [int(round(value * MICRO_SCALE)) for value in values]


def pcm_summary(signal: Sequence[float],
                sample_rate_hz: int = SAMPLE_RATE_HZ) -> Dict[str, Any]:
    values = validate_pcm(signal, sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_micro": int(round(peak * MICRO_SCALE)),
        "nonfinite_samples": 0,
        "digest_basis": "int_micro_quantized_samples",
        "quantization_micro": MICRO_SCALE,
        "sha256": object_digest(_quantized_micro(values)),
    }


def identity_transform(signal: Any) -> List[float]:
    """The task's declared comparison baseline: identity prosody, no change."""
    return list(validate_pcm(signal))


def admit_target_condition(condition: Any) -> Dict[str, Any]:
    """Fail closed: only the identity prosody baseline may be admitted."""
    if not isinstance(condition, dict):
        raise ReferenceRejection("target_condition_not_object")
    expected = {"comparison_baseline", "target_emotion_label",
                "target_intensity_milli", "task_kind", "variant"}
    present = set(condition)
    if present != expected:
        missing = sorted(expected - present)
        extra = sorted(present - expected)
        raise ReferenceRejection(
            "target_condition_keys_mismatch:"
            + ",".join(missing + extra))
    if condition["task_kind"] != TASK_KIND:
        raise ReferenceRejection("target_condition_wrong_task_kind")
    if condition["variant"] != CALLER_VARIANT:
        raise ReferenceRejection("target_condition_wrong_variant")
    if condition["comparison_baseline"] != COMPARISON_BASELINE:
        raise ReferenceRejection("target_condition_wrong_baseline")
    label = condition["target_emotion_label"]
    if not isinstance(label, str) or not LABEL_PATTERN.fullmatch(label):
        raise ReferenceRejection("target_condition_bad_label")
    intensity = condition["target_intensity_milli"]
    if isinstance(intensity, bool) or not isinstance(intensity, int):
        raise ReferenceRejection("target_condition_intensity_not_integer")
    if intensity < 1 or intensity > MAX_TARGET_INTENSITY:
        raise ReferenceRejection("target_condition_intensity_out_of_range")
    if label != IDENTITY_LABEL or intensity != TARGET_INTENSITY_FULL:
        raise ReferenceRejection(
            "absent_candidate_transform:" + label + ":" + str(intensity))
    return {
        "accepted": True,
        "identity_control": True,
        "transformation_performed": False,
        "target_emotion_label": label,
        "target_intensity_milli": intensity,
        "task_kind": TASK_KIND,
        "comparison_baseline": COMPARISON_BASELINE,
        "variant": CALLER_VARIANT,
        "qualification_effect": "none",
        "reason": (
            "identity prosody is the declared comparison baseline; no "
            "candidate transform, target label set or runtime exists"),
    }


def identity_target_condition() -> Dict[str, Any]:
    return {
        "comparison_baseline": COMPARISON_BASELINE,
        "target_emotion_label": IDENTITY_LABEL,
        "target_intensity_milli": TARGET_INTENSITY_FULL,
        "task_kind": TASK_KIND,
        "variant": CALLER_VARIANT,
    }


def duration_accounting(source_samples: int, output_samples: int
                        ) -> Dict[str, Any]:
    for value in (source_samples, output_samples):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ReferenceRejection("sample_count_must_be_integer")
        if value <= 0:
            raise ReferenceRejection("sample_count_must_be_positive")
    source_duration = Fraction(source_samples, SAMPLE_RATE_HZ)
    output_duration = Fraction(output_samples, SAMPLE_RATE_HZ)
    ratio = output_duration / source_duration
    return {
        "source_samples": source_samples,
        "output_samples": output_samples,
        "source_duration_s": fraction_text(source_duration),
        "output_duration_s": fraction_text(output_duration),
        "duration_ratio": fraction_text(ratio),
        "duration_ratio_interpretation": (
            "output_duration_divided_by_source_duration"),
        "sample_delta": output_samples - source_samples,
    }


def alignment_accounting(output_samples: int) -> Dict[str, Any]:
    if isinstance(output_samples, bool) or not isinstance(output_samples, int):
        raise ReferenceRejection("output_sample_count_must_be_integer")
    if output_samples <= 0:
        raise ReferenceRejection("output_sample_count_must_be_positive")
    return {
        "mode": "offline_whole_utterance",
        "streaming_supported": False,
        "incremental_streaming": False,
        "first_output_sample": 0,
        "first_output_delay_samples": 0,
        "tail_samples": output_samples,
        "whole_clip_required": True,
        "measured": False,
        "note": (
            "No candidate runtime exists, so alignment is not measured. This "
            "declares the offline-only accounting boundary; it is not device "
            "or first-output timing."),
    }


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent."""
    root = "/nonexistent/emotion-prosody-evidence-fixture"
    digest = "0" * 64
    return {
        "asset_storage": "external",
        "channels": CHANNELS,
        "checkpoint_path": root + "/checkpoint.bin",
        "checkpoint_sha256": digest,
        "comparison_baseline": COMPARISON_BASELINE,
        "emotion_label_set_path": root + "/labels.json",
        "emotion_label_set_sha256": digest,
        "model_config_path": root + "/config.json",
        "model_config_sha256": digest,
        "rights_record_path": root + "/rights.json",
        "rights_record_sha256": digest,
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "runtime_path": root + "/runtime",
        "sample_rate_input_hz": SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SAMPLE_RATE_HZ,
        "source_checkout_path": root + "/source",
        "source_revision": "0" * 40,
        "style_conditioning_path": root + "/style.bin",
        "style_conditioning_sha256": digest,
        "target_emotion_label": "calm",
        "target_intensity_milli": 700,
        "target_voice_consent_path": root + "/consent.json",
        "target_voice_consent_sha256": digest,
        "target_voice_reference_path": root + "/target.wav",
        "target_voice_reference_sha256": digest,
        "task_kind": TASK_KIND,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package."""
    assignments = {
        "checkpoint_path": TASK_DIR / "reference.py",
        "model_config_path": TASK_DIR / "run.py",
        "emotion_label_set_path": TASK_DIR / "LICENSES.md",
        "style_conditioning_path": TASK_DIR / "README.md",
        "target_voice_reference_path": TASK_DIR / "reference.py",
        "target_voice_consent_path": TASK_DIR / "contract.json.license",
        "rights_record_path": TASK_DIR / "verify.py",
        "runtime_lock_path": TASK_DIR / "test_reference.py",
    }
    manifest: Dict[str, Any] = {
        "asset_storage": "external",
        "channels": CHANNELS,
        "comparison_baseline": COMPARISON_BASELINE,
        "runtime_path": str(SDK_ROOT),
        "sample_rate_input_hz": SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SAMPLE_RATE_HZ,
        "source_checkout_path": str(TASK_DIR),
        "source_revision": "a" * 40,
        "target_emotion_label": "calm",
        "target_intensity_milli": 700,
        "task_kind": TASK_KIND,
        "variant": CALLER_VARIANT,
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = file_digest(path)
    return manifest


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
                raise ReferenceRejection("asset_exceeds_the_evidence_cap")
            digest.update(chunk)
    return digest.hexdigest()


def _rate_value(manifest: Dict[str, Any], field: str) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReferenceRejection("manifest_" + field + "_must_be_integer")
    if value < MIN_SAMPLE_RATE_HZ or value > MAX_SAMPLE_RATE_HZ:
        raise ReferenceRejection("manifest_" + field + "_outside_range")
    return value


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ReferenceRejection("manifest_must_be_object")
    expected = set(CALLER_ASSET_FIELDS)
    present = set(manifest)
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        raise ReferenceRejection("manifest_missing_fields:" + ",".join(missing))
    if extra:
        raise ReferenceRejection("manifest_unknown_fields:" + ",".join(extra))
    if manifest["asset_storage"] != "external":
        raise ReferenceRejection("manifest_asset_storage_must_be_external")
    if manifest["task_kind"] != TASK_KIND:
        raise ReferenceRejection("manifest_wrong_task_kind")
    if manifest["comparison_baseline"] != COMPARISON_BASELINE:
        raise ReferenceRejection("manifest_wrong_baseline")
    if manifest["variant"] != CALLER_VARIANT:
        raise ReferenceRejection("manifest_wrong_variant")
    for field in CALLER_SHA_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not re.fullmatch(
                r"[0-9a-f]{64}", value):
            raise ReferenceRejection(
                "manifest_" + field + "_is_not_lowercase_sha256")
    for path_field, _ in CALLER_FILE_PAIRS:
        value = manifest[path_field]
        if not isinstance(value, str) or not value:
            raise ReferenceRejection(
                "manifest_" + path_field + "_must_be_path")
        if not Path(value).is_absolute():
            raise ReferenceRejection(
                "manifest_" + path_field + "_must_be_absolute")
    for field in CALLER_DIR_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise ReferenceRejection(
                "manifest_" + field + "_must_be_path")
        if not Path(value).is_absolute():
            raise ReferenceRejection(
                "manifest_" + field + "_must_be_absolute")
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise ReferenceRejection(
            "manifest_source_revision_must_be_full_40_hex")
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise ReferenceRejection("manifest_channels_must_be_integer")
    if channels != CHANNELS:
        raise ReferenceRejection("manifest_channels_mismatch")
    input_rate = _rate_value(manifest, "sample_rate_input_hz")
    output_rate = _rate_value(manifest, "sample_rate_output_hz")
    label = manifest["target_emotion_label"]
    if not isinstance(label, str) or not LABEL_PATTERN.fullmatch(label):
        raise ReferenceRejection("manifest_target_emotion_label_invalid")
    intensity = manifest["target_intensity_milli"]
    if isinstance(intensity, bool) or not isinstance(intensity, int):
        raise ReferenceRejection("manifest_target_intensity_not_integer")
    if intensity < 1 or intensity > MAX_TARGET_INTENSITY:
        raise ReferenceRejection("manifest_target_intensity_out_of_range")
    for field in CALLER_DIR_FIELDS:
        if not Path(manifest[field]).is_dir():
            raise ReferenceRejection("manifest_" + field + "_directory_missing")
    total_bytes = 0
    for path_field, sha_field in CALLER_FILE_PAIRS:
        path = Path(manifest[path_field])
        if not path.is_file():
            raise ReferenceRejection("manifest_" + path_field + "_missing")
        actual = _hash_file(path)
        if actual != manifest[sha_field]:
            raise ReferenceRejection(
                "manifest_" + path_field + "_sha256_mismatch")
        total_bytes += path.stat().st_size
    return {
        "accepted": True,
        "source_revision": revision,
        "revision_pin_available": False,
        "task_kind": TASK_KIND,
        "comparison_baseline": COMPARISON_BASELINE,
        "variant": CALLER_VARIANT,
        "sample_rate_input_hz": input_rate,
        "sample_rate_output_hz": output_rate,
        "channels": CHANNELS,
        "target_emotion_label": label,
        "target_intensity_milli": intensity,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
        "audio_read": False,
    }


def run_adverse_controls() -> List[Dict[str, Any]]:
    good_source = synthetic_source_pcm()
    good_manifest = _shape_only_manifest()

    def case(case_id: str, action) -> Dict[str, Any]:
        try:
            action()
        except ReferenceRejection as error:
            return {"case": case_id, "result": "rejected",
                    "reason": error.code}
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

    def wrong_target(key: str, value: Any):
        condition = identity_target_condition()
        condition[key] = value
        return lambda: admit_target_condition(condition)

    def drop_target(key: str):
        condition = identity_target_condition()
        condition.pop(key)
        return lambda: admit_target_condition(condition)

    existing = _existing_file_manifest()
    nonidentity = identity_target_condition()
    nonidentity["target_emotion_label"] = "joyful"
    nonidentity["target_intensity_milli"] = 800
    reduced = identity_target_condition()
    reduced["target_intensity_milli"] = 500

    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_source, 8000)),
        ("pcm_stereo", lambda: validate_pcm(good_source, SAMPLE_RATE_HZ, 2)),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan])),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf])),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf])),
        ("pcm_out_of_range", lambda: validate_pcm([0.0, 1.5])),
        ("pcm_bool", lambda: validate_pcm([0.0, True])),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"])),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("checkpoint_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "checkpoint_path", "checkpoints/prosody.bin")),
        ("manifest_bad_sha", wrong("checkpoint_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "b43a7e1")),
        ("manifest_nonhex_revision", wrong("source_revision", "g" * 40)),
        ("manifest_wrong_variant", wrong("variant", "incremental_streaming")),
        ("manifest_wrong_task_kind_tts", wrong("task_kind", "text_to_speech")),
        ("manifest_wrong_task_kind_voice_conversion", wrong(
            "task_kind", "speech_to_speech_voice_conversion")),
        ("manifest_wrong_baseline", wrong(
            "comparison_baseline", "fixed_style_pipeline")),
        ("manifest_channels_zero", wrong("channels", 0)),
        ("manifest_channels_float", wrong("channels", 1.0)),
        ("manifest_rate_below_range", wrong("sample_rate_input_hz", 4000)),
        ("manifest_rate_above_range", wrong("sample_rate_output_hz", 384000)),
        ("manifest_rate_bool", wrong("sample_rate_output_hz", True)),
        ("manifest_empty_emotion_label", wrong("target_emotion_label", "")),
        ("manifest_bad_emotion_label", wrong(
            "target_emotion_label", "Joyful!")),
        ("manifest_intensity_zero", wrong("target_intensity_milli", 0)),
        ("manifest_intensity_above", wrong(
            "target_intensity_milli", MAX_TARGET_INTENSITY + 1)),
        ("manifest_intensity_bool", wrong("target_intensity_milli", True)),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, checkpoint_path=(
                "/nonexistent/emotion-prosody/checkpoint.bin")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, runtime_path=(
                "/nonexistent/emotion-prosody/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, checkpoint_sha256="0" * 64))),
        ("manifest_missing_consent", lambda: validate_caller_manifest(
            dict(existing, target_voice_consent_path=(
                "/nonexistent/emotion-prosody/consent.json")))),
        ("manifest_wrong_storage", wrong("asset_storage", "vendored")),
        ("target_not_object", lambda: admit_target_condition([])),
        ("target_missing_intensity", drop_target("target_intensity_milli")),
        ("target_unknown_label", wrong_target(
            "target_emotion_label", "not_a_real_label_")),
        ("target_nonidentity_label", lambda: admit_target_condition(
            nonidentity)),
        ("target_intensity_not_full", lambda: admit_target_condition(reduced)),
        ("target_wrong_task_kind", wrong_target("task_kind", "text_to_speech")),
        ("target_wrong_variant", wrong_target(
            "variant", "incremental_streaming")),
        ("target_wrong_baseline", wrong_target(
            "comparison_baseline", "fixed_style_pipeline")),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise ReferenceRejection("adverse_case_count_mismatch")
    if [item["case"] for item in results] != list(ADVERSE_CASE_IDS):
        raise ReferenceRejection("adverse_case_ids_mismatch")
    return results


def build_control() -> Dict[str, Any]:
    source = synthetic_source_pcm()
    output = identity_transform(source)
    source_summary = pcm_summary(source)
    output_summary = pcm_summary(output)
    duration = duration_accounting(len(source), len(output))
    alignment = alignment_accounting(len(output))
    accepted = admit_target_condition(identity_target_condition())
    rejected_names: List[str] = []
    for label, intensity in (("joyful", 800), ("sad", 500), ("angry", 1000)):
        condition = identity_target_condition()
        condition["target_emotion_label"] = label
        condition["target_intensity_milli"] = intensity
        try:
            admit_target_condition(condition)
        except ReferenceRejection:
            rejected_names.append(label)
    if len(rejected_names) != 3:
        raise ReferenceRejection("nonidentity_target_not_rejected")
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_sample_rate_hz": SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "control_frame_samples": FRAME_SAMPLES,
            "control_sample_format": SAMPLE_FORMAT,
            "candidate_geometry_status": "unestablished",
            "candidate_geometry_asserted": False,
            "target_condition_status": "unestablished",
            "mode": "offline_whole_utterance",
            "incremental_streaming": False,
        },
        "source_pcm": source_summary,
        "identity_output_pcm": output_summary,
        "identity_baseline": {
            "baseline": COMPARISON_BASELINE,
            "transformation_performed": False,
            "sample_count_equal": (
                source_summary["samples"] == output_summary["samples"]),
            "duration_equal": (
                source_summary["duration_s"] == output_summary["duration_s"]),
            "digest_equal": (
                source_summary["sha256"] == output_summary["sha256"]),
            "peak_bounded": output_summary["peak_micro"] <= MICRO_SCALE,
            "content_delay_samples": 0,
            "qualification_effect": "none",
        },
        "target_condition_admission": {
            "identity_control_accepted": accepted["accepted"],
            "identity_control": accepted["identity_control"],
            "accepted_labels": [IDENTITY_LABEL],
            "rejected_examples": rejected_names,
            "nonidentity_rejected": len(rejected_names) == 3,
            "transformation_performed": False,
            "requires_absent_candidate": True,
            "qualification_effect": "none",
        },
        "duration": duration,
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
                "reason": (
                    "no real source/target reference or speaker embedder "
                    "runtime"),
            },
            {
                "id": "target_emotion_realization",
                "measured": False,
                "value": None,
                "reason": "no label set, emotion scorer or candidate output",
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
                "reason": "structural offline accounting only; no device clock",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range",
                "pcm_wrong_rate", "pcm_stereo",
                "manifest_channels_zero", "manifest_channels_float",
                "manifest_rate_below_range", "manifest_rate_above_range",
                "manifest_rate_bool", "manifest_empty_emotion_label",
                "manifest_bad_emotion_label", "manifest_intensity_zero",
                "manifest_intensity_above", "manifest_intensity_bool",
                "target_unknown_label", "target_intensity_not_full"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_missing_directory", "manifest_missing_consent",
                "target_missing_intensity"],
            "fail_closed_target_rejected": [
                "target_nonidentity_label", "target_wrong_task_kind",
                "target_wrong_variant", "target_wrong_baseline"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic identity-prosody accounting control only at the public "
            "v0 geometry. It is not candidate output, not emotion-converted "
            "speech, not transformed prosody, not a quality or timing result "
            "and cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report model.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["source_checkout_present"]
        and observed["source_revision"] is not None
        and observed["license_file_present"]
        and observed["weights_present"]
        and observed["emotion_label_set_present"]
        and observed["target_voice_consent_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["rights_record_present"]
        and observed["cohort_manifest_present"]
        and observed["parity_manifest_present"])
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
        "source_revision": observed["source_revision"],
        "source_revision_pin_available": False,
        "license_present": observed["license_file_present"],
        "weights_present": observed["weights_present"],
        "emotion_label_set_present": observed["emotion_label_set_present"],
        "target_voice_consent_present": (
            observed["target_voice_consent_present"]),
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "rights_record_present": observed["rights_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "reference_audio_present": observed["reference_audio_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No emotion/expressive-prosody source, revision, checkpoint, "
            "label set, target-voice consent, runtime, licence, rights record, "
            "cohort or parity manifest was observed."),
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
        "schema_id": REPORT_SCHEMA,
        "task_id": TASK_ID,
        "component": COMPONENT,
        "title": TITLE,
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
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
            "real_candidate_metrics": False,
            "reason": (
                "The record names no input-speech emotion/expressive-prosody "
                "model, checkpoint, target-emotion label set or repository "
                "revision; no consent-cleared target voices, rights record, "
                "hash-pinned runtime, cohort, parity vector or exact geometry "
                "exists, so every release gate remains blocked."),
        },
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "generated_by": "reference.py",
        "format": FORMAT,
        "boundary": BOUNDARY,
        "scope": SCOPE,
        "board_row": identity,
        "task_row_identity": identity,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "candidate": {
            "name": TITLE,
            "record": "candidate_matrix.csv record " + str(CANDIDATE_RECORD),
            "record_name": TITLE,
            "record_status": "unavailable/blocked",
            "candidate_kind": "unnamed_model_family",
            "source_record": CANDIDATE_RECORD_PATH,
            "source_record_sha256": SOURCE_PINS[CANDIDATE_RECORD_PATH],
            "report_paths": list(CANDIDATE_REPORT_PATHS),
            "baseline": "Identity prosody; fixed style/target-speaker pipeline",
            "finding": (
                "No input-speech conversion model, target emotion labels or "
                "consent-cleared target voices are staged."),
            "source_present": False,
            "source_revision": None,
            "source_sha256": None,
            "weights_present": False,
            "weights_sha256": None,
            "runtime_present": False,
            "target_emotion_labels_present": False,
            "consent_cleared_target_voices_present": False,
            "geometry_documented": False,
            "implemented_here": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "evidence_status": "blocked",
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "licensing": {
            "package_license": "Apache-2.0",
            "upstream_license_reported": None,
            "license_text_staged": False,
            "weights_terms_staged": False,
            "training_data_statement_staged": False,
            "target_voice_consent_staged": False,
            "output_use_reviewed": False,
            "redistribution_reviewed": False,
            "product_use_reviewed": False,
            "corpus_rights_reviewed": False,
            "review_status": "blocked",
        },
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
                "Structural accounting passes, but no real model, permitted "
                "reference set, target-emotion label set, consent record, "
                "rights-cleared cohort, target runtime or approved parity "
                "exists, so the voice profile is not satisfied for "
                "qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
            "identity_baseline_exact": (
                control["identity_baseline"]["digest_equal"]),
            "nonidentity_target_rejected_before_processing": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
            "adverse": control["adverse"],
            "adverse_all_rejected": all(
                item["result"] == "rejected" for item in control["adverse"]),
        },
        "gates": gates,
        "release_gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_condition": (
            "Pin the exact licensed input-speech emotion/expressive-prosody "
            "source, checkpoint, config and runtime with immutable revisions "
            "and digests; supply target emotion/style labels, intensity scale "
            "and conditioning assets with digests; clear code, weight, "
            "training-data, corpus, target-voice, derivative-output, "
            "redistribution and product-use rights; freeze a rights-cleared "
            "task-matched cohort and parity vector; reproduce exact-runtime "
            "output against the identity-prosody baseline; measure content, "
            "identity, target emotion, naturalness, alignment and device "
            "timing; and complete opt-in adapter intake. Until every condition "
            "is closed the candidate stays DEFER, incomplete and not "
            "qualified."),
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            MISSING_SOURCE_PATH,
            MISSING_WEIGHTS_PATH,
            LABEL_SET_PATH,
            TARGET_VOICE_CONSENT_PATH,
            COHORT_MANIFEST_PATH,
            PARITY_MANIFEST_PATH,
            RIGHTS_RECORD_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model or audio runtime is imported.",
            "Fixed workspace paths are probed for source, weights, labels, consent, runtime, rights and cohort presence.",
            "No source checkout is executed and no weight byte is read.",
            "No network request, download, audio device, model load or timing run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline; no JSON floats"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }


def build_contract(report: Dict[str, Any], report_digest: str) -> Dict[str, Any]:
    sidecar_digest = sha256_bytes((report_digest + "\n").encode("utf-8"))
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-Identifier": "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK_ID,
        "title": TITLE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "version": VERSION,
        "mode": MODE,
        "profile": PROFILE,
        "verification_profile": PROFILE,
        "task_prefix": TASK_PREFIX,
        "write_scope": TASK_PREFIX,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": report["qualification"],
        "format": report["format"],
        "boundary": report["boundary"],
        "scope": report["scope"],
        "candidate": report["candidate"],
        "asset_requirements": report["asset_requirements"],
        "caller_asset_contract": report["caller_asset_contract"],
        "licensing": report["licensing"],
        "voice_profile": report["voice_profile"],
        "reference_protocol": report["reference_protocol"],
        "controls": {
            "identity_baseline_exact": report["controls"][
                "identity_baseline_exact"],
            "nonidentity_target_rejected_before_processing": report[
                "controls"]["nonidentity_target_rejected_before_processing"],
            "adverse_all_rejected": report["controls"]["adverse_all_rejected"],
            "adverse_case_count": len(report["controls"]["adverse"]),
        },
        "board_row": report["board_row"],
        "task_row_identity": report["task_row_identity"],
        "source_pins": report["source_pins"],
        "boundary_pins": report["boundary_pins"],
        "artifact_pins": artifact_pins(report_digest, sidecar_digest),
        "gates": report["gates"],
        "release_gates": report["release_gates"],
        "exact_blockers": report["exact_blockers"],
        "reopen_condition": report["reopen_condition"],
        "reopen_conditions": report["reopen_conditions"],
        "negative_claims": report["non_claims"],
        "missing_historical_artifacts": report["missing_historical_artifacts"],
        "determinism": report["determinism"],
        "reproduction": {
            "cold_start_regenerations": 3,
            "generator": "run.py",
            "check_command": "PYTHONDONTWRITEBYTECODE=1 python3 run.py --check",
            "verify_command": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no emotion/prosody model, checkpoint, config, label set, target "
            "voice or runtime is downloaded, copied, loaded or executed",
            "only the identity-prosody baseline is admitted; every non-identity "
            "target fails closed because the candidate transform is absent",
            "no candidate rate, frame, label taxonomy, intensity scale, timing "
            "protocol or output geometry is asserted",
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
        "# SHA-256 pins for SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION.",
        "# source: paths are relative to SOURCE_ROOT; worktree: paths are",
        "# relative to the SDK checkout; pkg: paths are relative to this",
        "# task-evidence directory. The mutable full plan/swarm/TASKS.json is",
        "# never hashed; only the linked-row stable identity is gated.",
    ]
    for path, digest in sorted(SOURCE_PINS.items()):
        lines.append(f"{digest}  source:{path}")
    for path, digest in sorted(BOUNDARY_PINS.items()):
        lines.append(f"{digest}  worktree:{path}")
    for name in sorted(PIN_FILES):
        if name in overrides:
            digest = sha256_bytes(overrides[name])
        else:
            full = TASK_DIR / name
            if not full.is_file():
                raise ReferenceRejection("missing_artifact:" + name)
            digest = file_digest(full)
        lines.append(f"{digest}  pkg:{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")


__all__ = [
    "ADVERSE_CASE_IDS",
    "BASE_COMMIT",
    "BOUNDARY",
    "BOUNDARY_PINS",
    "CALLER_ASSET_CONTRACT",
    "COMPONENT",
    "CONTROL_PLAN_PROVENANCE",
    "DECISION",
    "EXACT_BLOCKERS",
    "GATE_REQUIREMENTS",
    "MODE",
    "PROFILE",
    "ReferenceRejection",
    "SCOPE",
    "SOURCE_PINS",
    "TASK_ID",
    "admit_target_condition",
    "alignment_accounting",
    "artifact_pins",
    "audit_assets",
    "build_contract",
    "build_control",
    "build_report",
    "canonical_report",
    "canonical_text",
    "duration_accounting",
    "file_digest",
    "identity_target_condition",
    "identity_transform",
    "load_strict_json",
    "load_strict_json_text",
    "object_digest",
    "pcm_summary",
    "run_adverse_controls",
    "sha256_bytes",
    "sources_bytes",
    "synthetic_source_pcm",
    "task_row_identity",
    "validate_caller_manifest",
    "validate_pcm",
]
