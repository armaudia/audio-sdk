# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-GENAID.

The exact licensed GenAID source, weights and runtime set is absent. The merged
research evidence records a code/demo inspection only: no inference weights
were downloaded, the method is accent-controlled text to speech with accent
embeddings rather than real-time audio-to-audio conversion, and no source
checkout, full 40-hex upstream revision, checkpoint digest, runtime lock or
rights-cleared voice cohort exists in this workspace.

This module therefore never imports PyTorch, torchaudio, Transformers, NumPy,
SoundFile or any TTS runtime, never loads or executes a model, never reads or
writes real audio, never downloads anything and never measures a device clock.
It provides three verifiable pieces:

* a fail-closed source/asset audit over fixed workspace paths that records the
  absent source, revision, weights, tokenizer, runtime, licence and rights
  records and probes fixed paths for accidental assets;
* a caller-supplied-asset manifest contract validated without execution, with
  every malformed, missing, invalid or nonfinite control rejected before use;
* a deterministic synthetic acceptance-accounting control at the public v0
  geometry that checks PCM validity, exact duration accounting and offline-only
  alignment without asserting any GenAID geometry.

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

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-GENAID"
TITLE = "GenAID"
SLUG = "genaid"
COMPONENT = "genaid"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "77d7800cac82899eb02a8aa55535d00e4faa8946"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-GENAID"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-GENAID")
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "voice"
MODE = "feasibility"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# Exact upstream identity recorded by the merged research evidence.  Only a
# repository URL was recorded; no resolved 40-hex revision exists, so none is
# invented here.
UPSTREAM_NAME = "GenAID"
UPSTREAM_RECORD_NAME = "AccentBox / GenAID"
UPSTREAM_REPO_URL = "https://github.com/jzmzhong/GenAID/"
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False
TASK_CONDITION = "accent_controlled_tts_with_accent_embeddings"
TASK_SCOPE = "accent_controlled_tts"
TASK_GEOMETRY_STATUS = "unestablished"
REAL_TIME_AUDIO_TO_AUDIO = False

# Control geometry is the public SDK v0 boundary, not GenAID geometry.
CONTROL_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160

# Fixed workspace paths used for the audit.  Absence is recorded, not filled.
RIGHTS_RECORD_PATH = "data/rights/genaid-rights.json"
COHORT_MANIFEST_PATH = "data/runs/genaid-voice-cohort/manifest.json"
PARITY_MANIFEST_PATH = "data/runs/genaid-parity/manifest.json"
RUNTIME_ENV_PATH = "data/envs/genaid"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
MISSING_SOURCE_PATH = "research/accent-conversion-20261101/repos/GenAID"
MISSING_WEIGHTS_PATH = "data/models/genaid/checkpoint"
MISSING_TOKENIZER_PATH = "data/models/genaid/tokenizer"
TEXT_INPUT_MANIFEST_PATH = "data/runs/genaid-voice-cohort/text-inputs.json"

# Fixed absence probes.  Every probe must stay absent; any appearance forces a
# re-evaluation instead of silently promoting the candidate.
ABSENCE_PROBES: Tuple[str, ...] = (
    "research/accent-conversion-20261101/repos/GenAID",
    "research/accent-conversion-20261101/repos/genaid",
    "research/accent-conversion-20261101/repos/AccentBox",
    "research/accent-conversion-20261101/hf-cache/models--jzmzhong--GenAID",
    "research/accent-conversion-20261101/hf-cache/hub/models--jzmzhong--GenAID",
    "data/checkouts/GenAID",
    "data/checkouts/genaid",
    "data/models/GenAID",
    "data/models/genaid",
    "data/weights/GenAID",
    "data/weights/genaid",
    "data/envs/genaid",
    "data/envs/genaid/requirements.lock",
    "data/rights/genaid-rights.json",
    "data/runs/genaid-voice-cohort/manifest.json",
    "data/runs/genaid-parity/manifest.json",
)

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
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
}
BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".gitattributes":
        "7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
}
LOCAL_PIN_PATHS = (
    "LICENSES.md",
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
    "sdk_v0_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "genaid_geometry_status": TASK_GEOMETRY_STATUS,
    "genaid_geometry_asserted": False,
    "control_input_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_output_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_channels": CHANNELS,
    "control_sample_format": "f32",
    "control_mode": "offline_whole_utterance",
    "control_incremental_streaming": False,
    "task_scope": TASK_SCOPE,
    "real_time_audio_to_audio": REAL_TIME_AUDIO_TO_AUDIO,
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
    "real_genaid_model": False,
    "real_time_audio_to_audio": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No GenAID or AccentBox source, checkpoint, accent embedding, tokenizer "
    "or text frontend is loaded or executed.",
    "No PyTorch, torchaudio, Transformers, NumPy, SoundFile or TTS runtime is "
    "imported.",
    "No network request, download, staging or asset redistribution occurs.",
    "No real audio, corpus, transcript, text input, speaker reference or "
    "consent record is consumed.",
    "No speech synthesis, accent conversion, WER, speaker similarity, "
    "naturalness, latency, memory or RTF is measured here.",
    "No GenAID output, duration ratio, alignment or accent condition is "
    "claimed; the synthetic control is a contract fixture only.",
    "Sibling AccentBox, AccentCL, TokAN, MeanVC2 and Seed-VC observations are "
    "provenance only and are not attributed to GenAID.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI "
    "changed.",
    "No listening, device timing, public benchmark or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "source_checkout",
        "recorded_url": UPSTREAM_REPO_URL,
        "revision": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "upstream_revision",
        "recorded_url": UPSTREAM_REPO_URL,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "inference_weights",
        "recorded_size_approx_mb": None,
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "accent_condition_assets",
        "kind": "accent_embedding_or_accent_label_bundle",
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "text_frontend_and_tokenizer",
        "kind": "grapheme_phoneme_tokenizer_lexicon_declared_by_upstream",
        "sha256": None,
        "required": True,
        "status": "absent",
    },
    {
        "id": "exact_runtime",
        "recorded_python": None,
        "runtime_lock_sha256": None,
        "required": True,
        "status": "absent",
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
        "permitted_text_inputs_manifest": TEXT_INPUT_MANIFEST_PATH,
        "sibling_sample_clips_are_genaid": False,
    },
)

CALLER_ASSET_FIELDS = (
    "accent_embedding_path",
    "accent_embedding_sha256",
    "channels",
    "checkpoint_path",
    "checkpoint_sha256",
    "config_path",
    "config_sha256",
    "consent_record_path",
    "consent_record_sha256",
    "license_record_path",
    "license_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_output_hz",
    "scope",
    "source_checkout_path",
    "source_revision",
    "target_accent_label",
    "target_accent_reference_path",
    "target_accent_reference_sha256",
    "text_input_manifest_path",
    "text_input_manifest_sha256",
    "tokenizer_path",
    "tokenizer_sha256",
    "variant",
)

CALLER_FILE_PAIRS = (
    ("checkpoint_path", "checkpoint_sha256"),
    ("accent_embedding_path", "accent_embedding_sha256"),
    ("config_path", "config_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("target_accent_reference_path", "target_accent_reference_sha256"),
    ("text_input_manifest_path", "text_input_manifest_sha256"),
    ("tokenizer_path", "tokenizer_sha256"),
    ("consent_record_path", "consent_record_sha256"),
)
CALLER_DIR_FIELDS = ("source_checkout_path", "runtime_path")
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "offline_whole_utterance"
CALLER_SCOPE = TASK_SCOPE
MIN_SAMPLE_RATE_HZ = 8000
MAX_SAMPLE_RATE_HZ = 192000

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_revision_shape_geometry_scope_and_"
        "offline_variant_only; do_not_import_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_scope": CALLER_SCOPE,
    "required_source_revision": UPSTREAM_REVISION,
    "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
    "required_geometry": {
        "channels": CHANNELS,
        "sample_rate_output_hz": None,
        "status": TASK_GEOMETRY_STATUS,
    },
    "notes": (
        "Every checkpoint, accent embedding, tokenizer, text-input manifest, "
        "config, licence, runtime lock, target-accent reference and consent "
        "record must exist at an absolute path and match its declared SHA-256 "
        "before a caller may process text or audio. No upstream revision is "
        "pinned because the merged evidence records only a repository URL. "
        "The scope is accent-controlled TTS, never audio-to-audio conversion."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "source_checkout_absent",
        "state": "absent",
        "requirement": (
            "Supply the GenAID source checkout at an immutable 40-hex "
            "revision under research/accent-conversion-20261101/repos or "
            "data/checkouts; no checkout exists in the workspace."),
    },
    {
        "id": "upstream_revision_unpinned",
        "state": "absent",
        "requirement": (
            "Resolve https://github.com/jzmzhong/GenAID/ to a full 40-hex "
            "commit and publish its per-file SHA-256 manifest; the merged "
            "evidence records only the repository URL."),
    },
    {
        "id": "inference_weights_absent",
        "state": "absent",
        "requirement": (
            "Supply the exact inference checkpoints with byte counts and "
            "SHA-256 values at one immutable revision; no weight was "
            "downloaded or identified by digest in the merged evidence."),
    },
    {
        "id": "accent_condition_assets_absent",
        "state": "absent",
        "requirement": (
            "Supply the accent label set, accent embedding table and target "
            "accent condition definition with digests; GenAID is "
            "accent-controlled TTS, so the target accent condition is a "
            "required asset rather than an audio-to-audio transform."),
    },
    {
        "id": "text_frontend_absent",
        "state": "absent",
        "requirement": (
            "Supply every text normalizer, grapheme/phoneme tokenizer, "
            "lexicon and text-frontend configuration declared by the "
            "resolved upstream revision, with byte counts and SHA-256 "
            "values; none is identified in the merged evidence or present "
            "in the workspace."),
    },
    {
        "id": "runtime_absent",
        "state": "absent",
        "requirement": (
            "Provide an isolated hash-pinned runtime with a complete lock at "
            "data/envs/genaid/requirements.lock and a recorded platform; no "
            "environment, package pin or lock exists."),
    },
    {
        "id": "source_license_unverified",
        "state": "absent",
        "requirement": (
            "Add the upstream artifact licence and terms at the resolved "
            "commit; no licence file, terms statement or redistribution grant "
            "is recorded in the merged evidence or present in the workspace."),
    },
    {
        "id": "rights_and_consent_uncleared",
        "state": "absent",
        "requirement": (
            "Clear weights, training-data, accent-label, text-input, speaker-"
            "reference, consent, output-use and redistribution rights with "
            "complete notices; no rights or consent record exists."),
    },
    {
        "id": "voice_cohort_and_parity_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared voice cohort with permitted text inputs "
            "and target-accent references, language/speaker groups, separate "
            "text, identity and naturalness outcomes, and an approved "
            "exact-runtime parity vector; no GenAID cohort or parity vector "
            "exists."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_source_and_asset_identity",
        "The full 40-hex source revision, checkpoint, accent embedding and "
        "tokenizer SHA-256 values, and the source licence match exact pins.",
    ),
    (
        "runtime_admission",
        "An isolated hash-pinned runtime with a complete lock is admitted on a "
        "recorded platform.",
    ),
    (
        "artifact_rights_and_consent",
        "Source, weight, training-data, accent-label, text-input, speaker-"
        "reference, consent, output-use and redistribution rights are cleared "
        "with complete notices.",
    ),
    (
        "exact_reference_parity",
        "An approved exact-runtime GenAID output matches the reference on a "
        "frozen caller-supplied text input for one frozen configuration.",
    ),
    (
        "voice_cohort_and_scoring",
        "A rights-cleared held-out cohort scores text/semantic preservation, "
        "identity/similarity and naturalness as separate outcomes.",
    ),
    (
        "task_scope_and_geometry",
        "The synthesis scope, accent condition, output sample rate and "
        "channel geometry are established and do not misrepresent an "
        "audio-to-audio converter.",
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
        "permitted_text_and_target_references",
        "Freeze permitted text inputs and target-accent references with "
        "rights and consent.",
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
        "Treat consent, reference availability and output use as independent "
        "gates.",
        "absent",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source": "research/accent-conversion-20261101/README.md",
    "source_sha256": SOURCE_PINS[
        "research/accent-conversion-20261101/README.md"],
    "record_name": UPSTREAM_RECORD_NAME,
    "evidence_line": 176,
    "repository_url": UPSTREAM_REPO_URL,
    "finding": (
        "Code/demo inspected; no inference weights downloaded. Accent-"
        "controlled TTS and accent embeddings rather than real-time audio-to-"
        "audio conversion. Useful if the product scope expands to synthesis."),
    "sibling_context_not_attributed": [
        "The sibling AccentBox task shares the same upstream URL but is a "
        "separate Voice blocker; no AccentBox asset, control or result is "
        "inherited here.",
        "AccentCL is a 7-class accent classifier with multi-gigabyte "
        "checkpoints and a Whisper-Large-v3 dependency; it is not GenAID.",
        "The three L2-ARCTIC demo clips and TokAN metrics are TokAN evidence, "
        "not GenAID evidence.",
        "MeanVC2, Seed-VC, RVC and the accent-classifier proxy are other "
        "candidate observations; none is a GenAID result.",
    ],
    "notes": (
        "No GenAID output, checkpoint, accent embedding, tokenizer or runtime "
        "was acquired. No duration, WER, similarity, naturalness, latency or "
        "RTF value is attributed to this candidate."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_voice_accounting_control_not_model_output")

CONTROL_SOURCE_SAMPLES = CONTROL_SAMPLE_RATE_HZ * 3
CONTROL_OUTPUT_SAMPLES = CONTROL_SAMPLE_RATE_HZ * 2
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
    "manifest_nonhex_revision",
    "manifest_wrong_variant",
    "manifest_wrong_scope",
    "manifest_channels_zero",
    "manifest_rate_below_range",
    "manifest_rate_bool",
    "manifest_empty_accent_label",
    "manifest_missing_asset",
    "manifest_missing_directory",
    "manifest_hash_mismatch",
)

MAX_MANIFEST_BYTES = 8 * 1024 ** 3
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")

# Built by adjacent-literal concatenation so no single Python string literal
# contains the contiguous SPDX marker token.
SPDX_COPYRIGHT_KEY = "SPDX-" "FileCopyrightText"
SPDX_LICENSE_KEY = "SPDX-" "License-Identifier"


class Reject(ValueError):
    """Fail-closed rejection for malformed, unsupported or unqualified input."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())


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
# Source checkout, asset and absence audit.  Fixed local reads only.
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
        SOURCE_ROOT / "research/accent-conversion-20261101/repos/GenAID",
        SOURCE_ROOT / "research/accent-conversion-20261101/repos/genaid",
        SOURCE_ROOT / "research/accent-conversion-20261101/repos/AccentBox",
        SOURCE_ROOT / "data/checkouts/GenAID",
        SOURCE_ROOT / "data/checkouts/genaid",
    ]


def _weights_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "data/models/genaid",
        SOURCE_ROOT / "data/models/GenAID",
        SOURCE_ROOT / "data/weights/genaid",
        SOURCE_ROOT / "research/accent-conversion-20261101/repos/GenAID/checkpoints",
        SOURCE_ROOT / "research/accent-conversion-20261101/repos/AccentBox/checkpoints",
    ]


def _text_frontend_candidates() -> List[Path]:
    return [
        SOURCE_ROOT / "data/models/genaid/tokenizer",
        SOURCE_ROOT / "data/models/genaid/text_frontend",
        SOURCE_ROOT / "research/accent-conversion-20261101/repos/GenAID/tokenizer",
        SOURCE_ROOT / "research/accent-conversion-20261101/repos/GenAID/text",
    ]


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
    readme = repository / "README.md" if repository is not None else None
    readme_declares = False
    if readme is not None and readme.is_file():
        try:
            text = readme.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            text = ""
        readme_declares = ("license" in text or "licence" in text
                           or "copyright" in text)
    weight_paths = _weights_candidates()
    frontend_paths = _text_frontend_candidates()
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    parity_manifest = SOURCE_ROOT / PARITY_MANIFEST_PATH
    probes = probe_absence()
    return {
        "source_checkout_path": MISSING_SOURCE_PATH,
        "source_checkout_present": repository is not None,
        "source_revision": revision,
        "source_revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "source_revision_matches": False,
        "source_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.is_dir()}
            for path in source_paths
        ],
        "license_files": licenses,
        "license_file_present": bool(licenses),
        "license_declared_in_readme": readme_declares,
        "weights_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in weight_paths
        ],
        "weights_present": any(path.exists() for path in weight_paths),
        "text_frontend_candidates": [
            {"path": str(path.relative_to(SOURCE_ROOT)),
             "present": path.exists()}
            for path in frontend_paths
        ],
        "text_frontend_present": any(path.exists()
                                     for path in frontend_paths),
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "rights_record_present": rights_record.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "parity_manifest_present": parity_manifest.is_file(),
        "absence_probes": probes,
        "all_absence_probes_absent": all(
            not item["exists"] for item in probes),
        "requested_config": {
            "task_scope": TASK_SCOPE,
            "condition": TASK_CONDITION,
            "geometry_status": TASK_GEOMETRY_STATUS,
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "upstream_revision": UPSTREAM_REVISION,
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
    if stable["repository"] != "audio-sdk" or stable["mode"] != MODE:
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
# Deterministic synthetic PCM and acceptance accounting.
# ---------------------------------------------------------------------------

def _triangle(index: int, period: int, scale: float) -> float:
    """Integer-only triangle sample; no platform libm is involved."""
    return scale * (period - 4 * abs(index % period - period // 2)) / 40.0


def _lcg(state: int) -> Tuple[int, float]:
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


def validate_pcm(signal: Any, sample_rate_hz: int = CONTROL_SAMPLE_RATE_HZ,
                 channels: int = CHANNELS) -> List[float]:
    if sample_rate_hz != CONTROL_SAMPLE_RATE_HZ:
        raise Reject("unsupported control sample rate")
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
    source_duration = Fraction(source_samples, CONTROL_SAMPLE_RATE_HZ)
    output_duration = Fraction(output_samples, CONTROL_SAMPLE_RATE_HZ)
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
            "No GenAID runtime exists, so alignment is not measured. This "
            "declares the offline-only accounting boundary; it is not a "
            "device or first-output timing result."),
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

    existing = _existing_file_manifest()
    cases = [
        ("pcm_empty", lambda: validate_pcm([])),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00")),
        ("pcm_none", lambda: validate_pcm(None)),
        ("pcm_wrong_rate", lambda: validate_pcm(good_source, 8000)),
        ("pcm_stereo", lambda: validate_pcm(good_source, CONTROL_SAMPLE_RATE_HZ, 2)),
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
            "checkpoint_path", "checkpoints/genaid.pt")),
        ("manifest_bad_sha", wrong("checkpoint_sha256", "ABC")),
        ("manifest_short_revision", wrong("source_revision", "77d7800")),
        ("manifest_nonhex_revision", wrong("source_revision", "g" * 40)),
        ("manifest_wrong_variant", wrong("variant", "incremental_streaming")),
        ("manifest_wrong_scope", wrong("scope", "audio_to_audio_conversion")),
        ("manifest_channels_zero", wrong("channels", 0)),
        ("manifest_rate_below_range", wrong("sample_rate_output_hz", 4000)),
        ("manifest_rate_bool", wrong("sample_rate_output_hz", True)),
        ("manifest_empty_accent_label", wrong("target_accent_label", "")),
        ("manifest_missing_asset", lambda: validate_caller_manifest(
            dict(existing, checkpoint_path=(
                "/nonexistent/genaid-fixtures/checkpoint.pt")))),
        ("manifest_missing_directory", lambda: validate_caller_manifest(
            dict(existing, runtime_path=(
                "/nonexistent/genaid-fixtures/no-runtime")))),
        ("manifest_hash_mismatch", lambda: validate_caller_manifest(
            dict(existing, checkpoint_sha256="0" * 64))),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    good = pcm_summary(good_source, CONTROL_SAMPLE_RATE_HZ)
    good_out = pcm_summary(good_output, CONTROL_SAMPLE_RATE_HZ)
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

    root = "/nonexistent/genaid-evidence-fixture"
    digest = "0" * 64
    return {
        "accent_embedding_path": root + "/accent-embedding.bin",
        "accent_embedding_sha256": digest,
        "channels": CHANNELS,
        "checkpoint_path": root + "/checkpoint.pt",
        "checkpoint_sha256": digest,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "consent_record_path": root + "/consent.json",
        "consent_record_sha256": digest,
        "license_record_path": root + "/rights.json",
        "license_record_sha256": digest,
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "runtime_path": root + "/runtime",
        "sample_rate_output_hz": CONTROL_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "source_checkout_path": root + "/source",
        "source_revision": "0" * 40,
        "target_accent_label": "general_american",
        "target_accent_reference_path": root + "/target.wav",
        "target_accent_reference_sha256": digest,
        "text_input_manifest_path": root + "/text-inputs.json",
        "text_input_manifest_sha256": digest,
        "tokenizer_path": root + "/tokenizer.bin",
        "tokenizer_sha256": digest,
        "variant": CALLER_VARIANT,
    }


def _existing_file_manifest() -> Dict[str, Any]:
    """A manifest whose referenced files really exist inside this package.

    It exercises file hashing and directory checks without reading audio or
    loading a model.  Duplicate paths are allowed; each pair carries the real
    digest so a single corrupted digest reaches the SHA-256 mismatch branch.
    """

    assignments = {
        "checkpoint_path": HERE / "reference.py",
        "accent_embedding_path": HERE / "run.py",
        "config_path": HERE / "README.md",
        "license_record_path": HERE / "LICENSES.md",
        "runtime_lock_path": HERE / "SOURCES.sha256.license",
        "target_accent_reference_path": HERE / "README.md",
        "text_input_manifest_path": HERE / "LICENSES.md",
        "tokenizer_path": HERE / "reference.py",
        "consent_record_path": HERE / "contract.json.license",
    }
    manifest: Dict[str, Any] = {
        "channels": CHANNELS,
        "runtime_path": str(SDK_ROOT),
        "sample_rate_output_hz": CONTROL_SAMPLE_RATE_HZ,
        "scope": CALLER_SCOPE,
        "source_checkout_path": str(HERE),
        "source_revision": "a" * 40,
        "target_accent_label": "general_american",
        "variant": CALLER_VARIANT,
    }
    for field, path in assignments.items():
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = sha256(path.read_bytes())
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
                raise Reject("asset exceeds the evidence cap")
            digest.update(chunk)
    return digest.hexdigest()


def _rate_value(manifest: Dict[str, Any], field: str) -> int:
    value = manifest[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject("manifest " + field + " must be an integer")
    if value < MIN_SAMPLE_RATE_HZ or value > MAX_SAMPLE_RATE_HZ:
        raise Reject("manifest " + field + " is outside the admitted range")
    return value


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
    if not isinstance(revision, str) or not COMMIT_PATTERN.fullmatch(revision):
        raise Reject("manifest source_revision must be a full 40-hex commit")
    channels = manifest["channels"]
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("manifest channels must be an integer")
    if channels != CHANNELS:
        raise Reject("manifest channels mismatch")
    output_rate = _rate_value(manifest, "sample_rate_output_hz")
    label = manifest["target_accent_label"]
    if not isinstance(label, str) or not re.fullmatch(
            r"[a-z][a-z0-9_]{1,63}", label):
        raise Reject("manifest target_accent_label is invalid")
    if manifest["scope"] != CALLER_SCOPE:
        raise Reject("manifest scope must be " + CALLER_SCOPE)
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
        "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "variant": CALLER_VARIANT,
        "scope": CALLER_SCOPE,
        "sample_rate_output_hz": output_rate,
        "channels": CHANNELS,
        "target_accent_label": label,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
    }


def build_control() -> Dict[str, Any]:
    source = synthetic_source_pcm()
    output = synthetic_output_pcm()
    source_summary = pcm_summary(source, CONTROL_SAMPLE_RATE_HZ)
    output_summary = pcm_summary(output, CONTROL_SAMPLE_RATE_HZ)
    durations = duration_accounting(len(source), len(output))
    alignment = alignment_accounting(len(output))
    adverse = run_adverse_controls()
    positive = validate_caller_manifest(_existing_file_manifest())
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "geometry": {
            "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
            "control_channels": CHANNELS,
            "genaid_geometry_status": TASK_GEOMETRY_STATUS,
            "genaid_geometry_asserted": False,
            "task_scope": TASK_SCOPE,
            "real_time_audio_to_audio": REAL_TIME_AUDIO_TO_AUDIO,
            "mode": "offline_whole_utterance",
            "incremental_streaming": False,
        },
        "source_pcm": source_summary,
        "output_pcm": output_summary,
        "duration": durations,
        "alignment": alignment,
        "accepted_control": {
            "id": "synthetic_structure_only_manifest",
            "accepted": positive["accepted"],
            "source_revision": positive["source_revision"],
            "scope": positive["scope"],
            "variant": positive["variant"],
            "files_checked": positive["files_checked"],
            "directories_checked": positive["directories_checked"],
            "model_executed": positive["model_executed"],
            "qualification_effect": "none",
            "note": (
                "The manifest hashes files inside this evidence package only. "
                "It is a structural positive control, not a GenAID asset set, "
                "and it cannot qualify the candidate."),
        },
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
                "reason": "no real target reference or embedder runtime",
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
                "pcm_wrong_rate", "pcm_stereo",
                "manifest_channels_zero", "manifest_rate_below_range",
                "manifest_rate_bool", "manifest_empty_accent_label",
                "manifest_wrong_scope"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_missing_directory"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic PCM accounting control only at the public v0 geometry. "
            "It is not GenAID output, not synthesized speech, not real "
            "accent-controlled audio, not a quality or timing result and "
            "cannot qualify the candidate."),
    }


# ---------------------------------------------------------------------------
# Report and contract model.
# ---------------------------------------------------------------------------

def _qualification_block(gates: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "status": QUALIFICATION,
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "blocked_gate_count": len(gates),
        "blocked_gate_ids": [gate["id"] for gate in gates],
        "reason": (
            "The GenAID source checkout, full upstream revision, inference "
            "weights, accent-condition assets, text frontend/tokenizer and "
            "hash-pinned runtime are absent; no licence, rights or consent "
            "record, rights-cleared voice cohort or approved parity vector "
            "exists, and the candidate is accent-controlled TTS rather than "
            "the task's audio-to-audio conversion geometry."),
    }


def _gates() -> List[Dict[str, str]]:
    return [
        {"id": gate, "requirement": requirement, "status": "blocked"}
        for gate, requirement in GATE_REQUIREMENTS
    ]


def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["source_checkout_present"]
        and observed["source_revision"] is not None
        and observed["license_file_present"]
        and observed["weights_present"]
        and observed["text_frontend_present"]
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
        "source_revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        "license_present": observed["license_file_present"],
        "weights_present": observed["weights_present"],
        "text_frontend_present": observed["text_frontend_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "rights_record_present": observed["rights_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "parity_manifest_present": observed["parity_manifest_present"],
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "observed": observed,
        "note": (
            "No GenAID source, revision, weight, tokenizer, runtime, licence, "
            "rights record or cohort was observed. The L2-ARCTIC clips and "
            "accent-classifier proxy belong to adjacent research packages "
            "and are not GenAID evidence."),
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = _asset_audit_summary()
    control = build_control()
    gates = _gates()
    qualification = _qualification_block(gates)
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
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": qualification,
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
        "upstream_identity": {
            "name": UPSTREAM_NAME,
            "record_name": UPSTREAM_RECORD_NAME,
            "repository_url": UPSTREAM_REPO_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "condition": TASK_CONDITION,
            "task_scope": TASK_SCOPE,
            "geometry_status": TASK_GEOMETRY_STATUS,
            "real_time_audio_to_audio": REAL_TIME_AUDIO_TO_AUDIO,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "absence_probes": audit["observed"]["absence_probes"],
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
            "scope_mismatch_rejected": True,
            "validator_accepts_well_formed_manifest": True,
            "absence_probes_all_absent": audit["all_absence_probes_absent"],
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
            MISSING_SOURCE_PATH,
            MISSING_WEIGHTS_PATH,
            MISSING_TOKENIZER_PATH,
            TEXT_INPUT_MANIFEST_PATH,
            COHORT_MANIFEST_PATH,
            RIGHTS_RECORD_PATH,
            PARITY_MANIFEST_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model or audio runtime is "
            "imported.",
            "Fixed workspace paths are probed for source, weights, tokenizer, "
            "runtime, rights and cohort presence.",
            "No source checkout is executed and no weight byte is read.",
            "No network request, download, audio device, model load or timing "
            "run occurs.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }


def build_contract() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = audit_assets()
    gates = _gates()
    qualification = _qualification_block(gates)
    return {
        SPDX_COPYRIGHT_KEY: "2026 Tsakanyan Hovhannes",
        SPDX_LICENSE_KEY: "Apache-2.0",
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification": qualification,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "task_row_identity": identity,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_checkout": {
            "path": MISSING_SOURCE_PATH,
            "present": audit["source_checkout_present"],
            "repository_url": UPSTREAM_REPO_URL,
            "revision": audit["source_revision"],
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
        },
        "upstream_identity": {
            "name": UPSTREAM_NAME,
            "record_name": UPSTREAM_RECORD_NAME,
            "repository_url": UPSTREAM_REPO_URL,
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "condition": TASK_CONDITION,
            "task_scope": TASK_SCOPE,
            "geometry_status": TASK_GEOMETRY_STATUS,
            "real_time_audio_to_audio": REAL_TIME_AUDIO_TO_AUDIO,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "gates": gates,
        "voice_profile_requirements": [
            {"id": item, "requirement": requirement, "status": status}
            for item, requirement, status in VOICE_REQUIREMENTS
        ],
        "missing_historical_artifacts": [
            MISSING_SOURCE_PATH,
            MISSING_WEIGHTS_PATH,
            MISSING_TOKENIZER_PATH,
            TEXT_INPUT_MANIFEST_PATH,
            COHORT_MANIFEST_PATH,
            RIGHTS_RECORD_PATH,
            PARITY_MANIFEST_PATH,
        ],
        "reproduction": {
            "tests": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "-m unittest -v test_reference.py"),
            "regenerate": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "run.py all"),
            "verify": (
                "PYTHONDONTWRITEBYTECODE=1 "
                "/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 "
                "verify.py"),
            "cold_start_regenerations": 3,
            "comparison": (
                "canonical JSON bytes, SHA-256 sidecar and source manifest "
                "only; no tolerance"),
        },
        "licensing": {
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "generated_json_sidecars": True,
            "source_asset_license": (
                "unverified; no source checkout, licence file or terms "
                "statement is present or recorded"),
        },
    }
