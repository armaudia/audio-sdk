# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-CONVERT-AND-SPEAK.

The exact licensed "Convert and Speak" source, weights, runtime and numeric
output are absent. The merged research note records only a paper/demo URL and
states that no runnable local checkpoint was found. This module therefore never
imports a model, audio or tensor runtime, never downloads anything, never reads
or writes real audio, never listens and never measures a device clock.

It provides three verifiable, bounded pieces:

* a fail-closed audit over fixed workspace paths for candidate source,
  weights, runtime, rights, consent and voice-cohort material;
* a caller-supplied-asset manifest contract that validates shape, identity and
  hashes only and always rejects admission because no immutable revision,
  weight digest or rights record is approved;
* a deterministic synthetic PCM voice-acceptance accounting control built from
  integer-only arithmetic. It is explicitly *not* Convert and Speak output.

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

TASK = "SDK-CONVERT-AND-SPEAK"
TITLE = "Convert and Speak"
SLUG = "convert-and-speak"
COMPONENT = "convert-and-speak"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "6967a728b5c4048fb01ed4522a76a6906fbcffe2"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"
VERSION = "0.1.0"
PROFILE = "voice"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# The candidate has no approved immutable identity. None is fabricated.
APPROVED_SOURCE_REVISION: Optional[str] = None
APPROVED_WEIGHTS_SHA256: Optional[str] = None
CANDIDATE_PAPER_DEMO_URL = "https://convert-and-speak.github.io/demo/"
CANDIDATE_FINDING_LINE = 172
CANDIDATE_FINDING = (
    "Paper/demo inspected; no runnable local checkpoint found. Strong "
    "accent-conversion research comparison with an autoregressive generation "
    "component; not a strict low-latency candidate.")

# Fixed workspace paths used by the audit. Absence is recorded, never filled.
SOURCE_CANDIDATES = (
    "research/accent-conversion-20261101/repos/ConvertAndSpeak",
    "research/accent-conversion-20261101/repos/convert-and-speak",
    "data/checkouts/convert-and-speak",
    "adapters/convert-and-speak",
)
WEIGHTS_CANDIDATES = (
    "data/models/convert-and-speak",
    "research/accent-conversion-20261101/checkpoints/convert-and-speak",
)
RUNTIME_ENV_PATH = "data/envs/convert-and-speak"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
RIGHTS_RECORD_PATH = "data/rights/convert-and-speak-rights.json"
CONSENT_RECORD_PATH = "data/rights/convert-and-speak-consent.json"
COHORT_MANIFEST_PATH = "data/runs/convert-and-speak-voice-cohort/manifest.json"
SAMPLE_DATA_PATH = "research/accent-conversion-20261101/data/l2accent"

# Installed v0 geometry is preserved and never changed by this package.
SDK_FRAME_SAMPLES = 160
SDK_SAMPLE_RATE_HZ = 16000
SDK_CHANNELS = 1
SDK_SAMPLE_FORMAT = "float32"

# Synthetic control geometry. This is the surrogate's geometry, not a claim
# about Convert and Speak, whose geometry is unknown.
SURROGATE_SAMPLE_RATE_HZ = 16000
SURROGATE_CHANNELS = 1
SURROGATE_SOURCE_SECONDS = 3
SURROGATE_TARGET_SECONDS = 2
SURROGATE_SOURCE_SAMPLES = SURROGATE_SAMPLE_RATE_HZ * SURROGATE_SOURCE_SECONDS
SURROGATE_TARGET_SAMPLES = SURROGATE_SAMPLE_RATE_HZ * SURROGATE_TARGET_SECONDS
PCM_SAMPLE_CAP = 960_000
Q15_SCALE = 32768

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
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "audio-benchmark-platform/audio-sdk/README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
}
BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/tokan/README.md":
        "425008e6836ea01e797c1bb86708532962d6e75ea0a8d332552b90ce0b2977df",
    "docs/task-evidence/tokan/report.json":
        "6cd151f2178d95d6e5c98b389a9b71f80097a01efaaa92a4450a7c26db1bcd13",
    "docs/task-evidence/chatterbox-vc/README.md":
        "7a624864df916ef87b32655e6e0894bfe00c3da94ca6969352be68654ee1443c",
    "docs/task-evidence/chatterbox-vc/report.json":
        "321fe22b052823b43d772871b5b694df03c0586c6754c04491d40406055b3dee",
    "docs/task-evidence/cosyvoice-2-0-5b/contract.json":
        "b7e38b9569a6d240bd551e54ecf0f42ca9e6b28b1702f88fb74a0497c3365dc3",
}
ARTIFACT_FILES = (
    "README.md",
    "SOURCES.sha256.license",
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
PIN_FILES = (
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
    "sdk_v0_sample_rate_hz": SDK_SAMPLE_RATE_HZ,
    "sdk_v0_channels": SDK_CHANNELS,
    "sdk_v0_sample_format": SDK_SAMPLE_FORMAT,
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "candidate_geometry_documented": False,
    "candidate_input_sample_rate_hz": None,
    "candidate_output_sample_rate_hz": None,
    "candidate_hop_samples": None,
    "candidate_mode_asserted": False,
    "surrogate_input_sample_rate_hz": SURROGATE_SAMPLE_RATE_HZ,
    "surrogate_output_sample_rate_hz": SURROGATE_SAMPLE_RATE_HZ,
    "surrogate_channels": SURROGATE_CHANNELS,
    "surrogate_mode": "offline_whole_utterance",
    "surrogate_incremental_streaming": False,
    "resampling": "none",
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
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "network_access": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "readiness_json_added": False,
    "registered": False,
    "sdk_data_dir_added": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "benchmark_claim": False,
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_access": False,
    "numeric_parity_claim": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_default": False,
    "real_audio": False,
    "real_candidate_model": False,
    "real_corpus": False,
    "release_claim": False,
    "runtime_invoked": False,
    "synthetic_only": True,
    "task_local_only": True,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No Convert and Speak source, weight file, runtime, adapter or numeric "
    "output is downloaded, copied, loaded, imported or executed.",
    "No autoregressive model, neural vocoder, content encoder or speaker "
    "encoder is present or invoked.",
    "No real audio, corpus, transcript, source/target voice reference or "
    "consent record is consumed.",
    "No accent conversion, text or semantic preservation, identity, "
    "naturalness, latency, memory, RTF or listening result is measured.",
    "The source-reported paper/demo finding is provenance only and is not "
    "reproduced here.",
    "The synthetic integer PCM accounting control is a contract control, never "
    "model output, and cannot qualify the candidate.",
    "No Convert and Speak input rate, output rate, hop, mode, alignment, "
    "first-output or tail timing is asserted.",
    "No provider, descriptor, registry, installed v0 path, shared build, "
    "dependency lock or CI is changed.",
    "No device timing, public benchmark, listening or release claim is made.",
    "Missing, blocked or rejected evidence never qualifies the candidate; the "
    "decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "candidate_source",
        "required": True,
        "sha256": None,
        "status": "absent",
        "candidate_paths": list(SOURCE_CANDIDATES),
    },
    {
        "id": "candidate_weights",
        "required": True,
        "sha256": None,
        "status": "absent",
        "candidate_paths": list(WEIGHTS_CANDIDATES),
    },
    {
        "id": "exact_runtime",
        "required": True,
        "runtime_lock_sha256": None,
        "status": "absent",
        "path": RUNTIME_ENV_PATH,
        "lock_path": RUNTIME_LOCK_PATH,
    },
    {
        "id": "source_and_weight_license_record",
        "required": True,
        "status": "absent",
        "path": None,
    },
    {
        "id": "rights_and_consent_record",
        "required": True,
        "status": "absent",
        "path": RIGHTS_RECORD_PATH,
        "consent_path": CONSENT_RECORD_PATH,
    },
    {
        "id": "voice_cohort",
        "required": True,
        "status": "absent",
        "path": COHORT_MANIFEST_PATH,
        "present_shared_sample_clips": 3,
        "sample_licence": "L2-ARCTIC CC BY-NC 4.0 research-only",
        "sample_role": "shared accent-evaluation clips, not Convert and Speak "
                       "input/target pairs",
    },
    {
        "id": "approved_reference_parity_vector",
        "required": True,
        "sha256": None,
        "status": "absent",
    },
)

CALLER_ASSET_FIELDS = (
    "channels",
    "config_path",
    "config_sha256",
    "consent_record_path",
    "consent_record_sha256",
    "license_record_path",
    "license_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_input_hz",
    "sample_rate_output_hz",
    "source_archive_path",
    "source_archive_sha256",
    "source_reference_path",
    "source_reference_sha256",
    "source_revision",
    "target_reference_path",
    "target_reference_sha256",
    "variant",
    "weights_path",
    "weights_sha256",
)
CALLER_FILE_PAIRS = (
    ("source_archive_path", "source_archive_sha256"),
    ("weights_path", "weights_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("config_path", "config_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("consent_record_path", "consent_record_sha256"),
    ("source_reference_path", "source_reference_sha256"),
    ("target_reference_path", "target_reference_sha256"),
)
CALLER_DIR_FIELDS = ("runtime_path",)
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)
CALLER_VARIANT = "offline_whole_utterance"

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_shape_absolute_paths_sha256_geometry_and_variant_only; "
        "do_not_import_or_execute"),
    "admission_status": "blocked_no_approved_identity",
    "positive_admission_possible": False,
    "approved_source_revision": APPROVED_SOURCE_REVISION,
    "approved_weights_sha256": APPROVED_WEIGHTS_SHA256,
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": CALLER_VARIANT,
    "required_geometry": {
        "sample_rate_input_hz": SURROGATE_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SURROGATE_SAMPLE_RATE_HZ,
        "channels": SURROGATE_CHANNELS,
    },
    "notes": (
        "The manifest contract is structurally exercised, but every manifest "
        "is rejected because no immutable Convert and Speak revision, weight "
        "digest, runtime lock or rights record is approved. No file is loaded "
        "or executed and no audio is processed."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "pinned_source_absent",
        "state": "absent",
        "requirement": (
            "Supply one exact Convert and Speak source tree or release archive "
            "with an immutable revision and matching SHA-256. No checkout, "
            "archive or adapter exists at any audited path."),
    },
    {
        "id": "weights_and_checkpoint_identity_absent",
        "state": "absent",
        "requirement": (
            "Supply the exact conversion weights and any content-encoder, "
            "speaker-encoder or vocoder checkpoints with byte counts and "
            "SHA-256 values at an immutable revision. The merged research note "
            "records no runnable local checkpoint."),
    },
    {
        "id": "runtime_and_environment_absent",
        "state": "absent",
        "requirement": (
            "Provide a complete isolated runtime lock and recorded platform "
            "for the pinned source and weights. No data/envs/convert-and-speak "
            "environment or lock exists."),
    },
    {
        "id": "source_and_weight_license_absent",
        "state": "absent",
        "requirement": (
            "Stage the exact source and weight license terms, model card, "
            "attribution notices and derivative-output and redistribution "
            "review. The merged evidence records a paper/demo URL only."),
    },
    {
        "id": "rights_consent_and_corpus_uncleared",
        "state": "absent",
        "requirement": (
            "Clear training-data, source-reference, target-reference, consent, "
            "output-use and corpus rights. The shared L2-ARCTIC sample clips "
            "are CC BY-NC 4.0 research-only and are not conversion pairs."),
    },
    {
        "id": "voice_cohort_and_reference_pairs_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared held-out cohort with permitted source and "
            "target references, task/language/speaker groups, transcript truth "
            "and separate text/semantic, identity/similarity and naturalness "
            "outcomes. Only three shared demo clips exist."),
    },
    {
        "id": "candidate_geometry_and_alignment_unverified",
        "state": "absent",
        "requirement": (
            "Document the exact Convert and Speak input/output rate, channel "
            "layout, hop or chunk scheme, autoregressive lookahead, first-output "
            "and tail alignment for the pinned weights. None is published in "
            "the merged evidence."),
    },
    {
        "id": "approved_reference_parity_absent",
        "state": "absent",
        "requirement": (
            "Produce an approved exact-runtime Convert and Speak parity vector "
            "on frozen input with a frozen configuration, reproducible weights "
            "and byte-level or declared-tolerance output comparison."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "RG-01",
        "Exact pinned Convert and Speak source, weights and immutable revision "
        "with license identity, byte counts and SHA-256 values.",
    ),
    (
        "RG-02",
        "Isolated hash-pinned runtime admission, reproducible build and "
        "fail-closed absent behavior.",
    ),
    (
        "RG-03",
        "Code, weight, training-data, corpus, voice-reference, consent and "
        "output-use rights with attribution and notices.",
    ),
    (
        "RG-04",
        "Caller-supplied asset identity plus documented candidate geometry and "
        "content-delay mapping into the installed SDK v0 path.",
    ),
    (
        "RG-05",
        "Rights-cleared held-out voice cohort scoring text/semantic "
        "preservation, identity/similarity and naturalness separately.",
    ),
    (
        "RG-06",
        "Exact-runtime offline alignment, first-output and tail behavior, "
        "nonfinite handling, reset and state reproduction.",
    ),
    (
        "RG-07",
        "Target-device pacing, timing and memory with independent listening "
        "and/or ASR controls.",
    ),
    (
        "RG-08",
        "Opt-in provider intake, descriptor review, independent exact-head "
        "review and default/release approval.",
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
        "Treat consent, reference availability and output use as independent "
        "gates.",
        "absent",
    ),
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "source": "research/accent-conversion-20261101/README.md",
    "source_line": CANDIDATE_FINDING_LINE,
    "source_sha256": SOURCE_PINS[
        "research/accent-conversion-20261101/README.md"],
    "record_name": "Convert and Speak",
    "finding": CANDIDATE_FINDING,
    "paper_demo_url": CANDIDATE_PAPER_DEMO_URL,
    "reported_autoregressive_component": True,
    "reported_low_latency_candidate": False,
    "local_checkpoint": "absent",
    "local_run": "not_run",
    "reported_latency": None,
    "reported_sample_rate_hz": None,
    "notes": (
        "The merged research note is the only evidence link. It records an "
        "inspection of a paper/demo, not a download, checkpoint, run, metric, "
        "listening result or device measurement."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_voice_acceptance_plan_not_model_output")

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "pcm_empty",
    "pcm_not_sequence",
    "pcm_none",
    "pcm_wrong_rate_8000",
    "pcm_wrong_rate_44100",
    "pcm_stereo",
    "pcm_nan",
    "pcm_pos_inf",
    "pcm_neg_inf",
    "pcm_out_of_range_high",
    "pcm_out_of_range_low",
    "pcm_bool",
    "pcm_string",
    "pcm_too_long",
    "surrogate_epoch_zero",
    "surrogate_epoch_negative",
    "surrogate_epoch_non_increasing",
    "surrogate_negative_position",
    "surrogate_epoch_bool",
    "surrogate_nonfinite_input",
    "surrogate_nonfinite_output",
    "surrogate_wrong_epoch",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_short_revision",
    "manifest_nonhex_revision",
    "manifest_wrong_input_rate",
    "manifest_wrong_output_rate",
    "manifest_wrong_channels",
    "manifest_wrong_variant",
    "manifest_missing_asset",
    "manifest_unapproved_revision",
    "fixture_bad_source_length",
    "fixture_bad_target_length",
    "fixture_bad_rate",
    "fixture_bad_ratio",
)


class Reject(ValueError):
    """Fail-closed rejection for malformed, unsupported or unqualified input."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
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
                          separators=(",", ":"), allow_nan=False
                          ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise Reject("value is not canonical-JSON serializable") from error


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256(text.encode("utf-8"))


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


def load_strict_json(path: Path) -> Dict[str, Any]:
    return strict_loads(path.read_text(encoding="utf-8"))


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


# ---------------------------------------------------------------------------
# Fixed-path audit. Local reads only; never downloads or executes anything.
# ---------------------------------------------------------------------------

def _present_paths(relatives: Sequence[str]) -> Dict[str, bool]:
    return {relative: (SOURCE_ROOT / relative).exists()
            for relative in relatives}


def _sample_clips() -> List[str]:
    directory = SOURCE_ROOT / SAMPLE_DATA_PATH
    if not directory.is_dir():
        return []
    return sorted(path.name for path in directory.iterdir()
                  if path.is_file() and path.suffix.lower() == ".wav")


def audit_assets() -> Dict[str, Any]:
    source_candidates = _present_paths(SOURCE_CANDIDATES)
    weights_candidates = _present_paths(WEIGHTS_CANDIDATES)
    runtime_env = SOURCE_ROOT / RUNTIME_ENV_PATH
    runtime_lock = SOURCE_ROOT / RUNTIME_LOCK_PATH
    rights_record = SOURCE_ROOT / RIGHTS_RECORD_PATH
    consent_record = SOURCE_ROOT / CONSENT_RECORD_PATH
    cohort_manifest = SOURCE_ROOT / COHORT_MANIFEST_PATH
    clips = _sample_clips()
    return {
        "source_candidates": source_candidates,
        "source_present": any(source_candidates.values()),
        "weights_candidates": weights_candidates,
        "weights_present": any(weights_candidates.values()),
        "runtime_env_present": runtime_env.is_dir(),
        "runtime_lock_present": runtime_lock.is_file(),
        "rights_record_present": rights_record.is_file(),
        "consent_record_present": consent_record.is_file(),
        "cohort_manifest_present": cohort_manifest.is_file(),
        "sample_clips": clips,
        "sample_clip_count": len(clips),
        "sample_clip_role": (
            "shared L2-ARCTIC accent-evaluation clips, not Convert and Speak "
            "input/target pairs"),
        "candidate_geometry_documented": False,
        "candidate_revision": None,
        "candidate_weights_sha256": None,
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
    if stable["repository"] != "audio-sdk" or stable["mode"] != "feasibility":
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

def _triangle(index: int, period: int, amplitude_percent: int) -> float:
    """Integer-ratio triangle sample; no platform libm is involved."""
    return amplitude_percent * (
        period - 4 * abs(index % period - period // 2)) / (100.0 * period)


def _lcg(state: int) -> Tuple[int, int]:
    state = (1664525 * state + 1013904223) & 0xFFFFFFFF
    return state, state


def synthetic_source_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x70C0DE01
    for index in range(SURROGATE_SOURCE_SAMPLES):
        state, raw = _lcg(state)
        samples.append(
            _triangle(index, 37, 30)
            + 0.01 * ((raw / 4294967296.0) * 2.0 - 1.0))
    return samples


def synthetic_target_reference_pcm() -> List[float]:
    samples: List[float] = []
    state = 0x7A46E702
    for index in range(SURROGATE_TARGET_SAMPLES):
        state, raw = _lcg(state)
        samples.append(
            _triangle(index, 43, 25)
            + 0.01 * ((raw / 4294967296.0) * 2.0 - 1.0))
    return samples


def synthetic_poisoned_output() -> List[float]:
    """A deliberately nonfinite output sequence for the rejection control."""
    return [0.0, float("nan"), 0.0]


def validate_pcm(signal: Any, sample_rate_hz: int = SURROGATE_SAMPLE_RATE_HZ,
                 channels: int = SURROGATE_CHANNELS) -> List[float]:
    if isinstance(sample_rate_hz, bool) or not isinstance(sample_rate_hz, int):
        raise Reject("sample rate must be an integer")
    if sample_rate_hz != SURROGATE_SAMPLE_RATE_HZ:
        raise Reject("unsupported sample rate")
    if isinstance(channels, bool) or not isinstance(channels, int):
        raise Reject("channel count must be an integer")
    if channels != SURROGATE_CHANNELS:
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


def _to_q15(value: float) -> int:
    return int(value * Q15_SCALE)


def surrogate_transform(values: Sequence[float]) -> List[float]:
    """Bounded integer-only one-pole transform used as a structural control."""
    previous = 0
    output: List[float] = []
    for value in values:
        current = (3 * _to_q15(value) + previous) // 4
        output.append(current / Q15_SCALE)
        previous = current
    return output


class AccentSurrogate:
    """Offline synthetic accounting surrogate. Not a model and not the candidate."""

    def __init__(self, epoch: int = 1) -> None:
        if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 1:
            raise Reject("initial epoch must be a positive integer")
        self.epoch = epoch
        self.first_input_sample = 0
        self.processed_samples = 0
        self.previous_q15 = 0

    @property
    def state_digest(self) -> str:
        return sha256(canonical_bytes({
            "epoch": self.epoch,
            "first_input_sample": self.first_input_sample,
            "processed_samples": self.processed_samples,
            "previous_q15": self.previous_q15,
        }))

    def reset(self, epoch: Any, first_input_sample: Any) -> Dict[str, Any]:
        if isinstance(epoch, bool) or not isinstance(epoch, int):
            raise Reject("reset epoch must be an integer")
        if epoch < 1:
            raise Reject("reset epoch must be positive")
        if epoch <= self.epoch:
            raise Reject("reset epoch must strictly increase")
        if (isinstance(first_input_sample, bool)
                or not isinstance(first_input_sample, int)):
            raise Reject("reset position must be an integer")
        if first_input_sample < 0:
            raise Reject("reset position must be nonnegative")
        self.epoch = epoch
        self.first_input_sample = first_input_sample
        self.processed_samples = 0
        self.previous_q15 = 0
        return {
            "epoch": epoch,
            "first_input_sample": first_input_sample,
            "state_digest": self.state_digest,
        }

    def process(self, samples: Any, epoch: Optional[int] = None
                ) -> Tuple[List[float], Dict[str, Any]]:
        if epoch is not None and epoch != self.epoch:
            raise Reject("stale or unknown epoch")
        values = validate_pcm(samples)
        start = self.first_input_sample + self.processed_samples
        output = surrogate_transform(values)
        self.previous_q15 = _to_q15(output[-1])
        self.processed_samples += len(values)
        result = {
            "epoch": self.epoch,
            "mode": "offline_whole_utterance",
            "input_samples": len(values),
            "output_samples": len(output),
            "source_first_sample": start,
            "valid_offset": 0,
            "valid_count": len(output),
            "content_delay_samples": 0,
            "algorithmic_latency_samples": None,
            "nonfinite_output_count": 0,
        }
        return output, result


def pcm_summary(signal: Sequence[float], sample_rate_hz: int
                ) -> Dict[str, Any]:
    values = validate_pcm(signal, sample_rate_hz)
    peak = max(abs(value) for value in values)
    return {
        "samples": len(values),
        "sample_rate_hz": sample_rate_hz,
        "channels": SURROGATE_CHANNELS,
        "duration_s": fraction_text(Fraction(len(values), sample_rate_hz)),
        "peak_abs": peak,
        "nonfinite_samples": 0,
        "sha256": sha256(canonical_bytes(list(values))),
    }


def duration_accounting(source_samples: Any, output_samples: Any
                        ) -> Dict[str, Any]:
    for value in (source_samples, output_samples):
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject("sample count must be an integer")
        if value <= 0:
            raise Reject("sample counts must be positive")
    source_duration = Fraction(source_samples, SURROGATE_SAMPLE_RATE_HZ)
    output_duration = Fraction(output_samples, SURROGATE_SAMPLE_RATE_HZ)
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
    if isinstance(output_samples, bool) or not isinstance(output_samples, int):
        raise Reject("output sample count must be an integer")
    if output_samples <= 0:
        raise Reject("output sample count must be positive")
    return {
        "mode": "offline_whole_utterance",
        "streaming_supported": False,
        "first_output_sample": 0,
        "first_output_delay_samples": 0,
        "tail_samples": output_samples,
        "whole_clip_required": True,
        "device_timing_measured": False,
        "candidate_alignment_asserted": False,
        "note": (
            "Structural surrogate accounting only; it is not a Convert and "
            "Speak alignment or timing claim."),
    }


def fixture_spec() -> Dict[str, int]:
    return {
        "source_samples": SURROGATE_SOURCE_SAMPLES,
        "target_samples": SURROGATE_TARGET_SAMPLES,
        "sample_rate_hz": SURROGATE_SAMPLE_RATE_HZ,
        "channels": SURROGATE_CHANNELS,
        "qh15_scale": Q15_SCALE,
    }


def validate_fixture(spec: Any) -> Dict[str, int]:
    if not isinstance(spec, dict):
        raise Reject("fixture spec must be an object")
    expected = fixture_spec()
    if set(spec) != set(expected):
        raise Reject("fixture spec fields differ")
    for key, value in spec.items():
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject("fixture field must be an integer: " + key)
        if value != expected[key]:
            raise Reject("fixture field mismatch: " + key)
    return spec


# ---------------------------------------------------------------------------
# Caller-supplied-asset manifest. Identity checks only; no loading.
# ---------------------------------------------------------------------------

def manifest_shape(manifest: Any) -> Dict[str, Any]:
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
        if not isinstance(value, str) or not re.fullmatch(
                r"[0-9a-f]{64}", value):
            raise Reject("manifest " + field + " is not a lowercase SHA-256")
    for path_field, _ in CALLER_FILE_PAIRS:
        value = manifest[path_field]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + path_field + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + path_field + " must be absolute")
    for field in CALLER_DIR_FIELDS:
        value = manifest[field]
        if not isinstance(value, str) or not value:
            raise Reject("manifest " + field + " must be a path string")
        if not Path(value).is_absolute():
            raise Reject("manifest " + field + " must be absolute")
    revision = manifest["source_revision"]
    if not isinstance(revision, str) or not re.fullmatch(
            r"[0-9a-f]{40}", revision):
        raise Reject("manifest source_revision must be a full 40-hex commit")
    for field, expected_value in (
            ("sample_rate_input_hz", SURROGATE_SAMPLE_RATE_HZ),
            ("sample_rate_output_hz", SURROGATE_SAMPLE_RATE_HZ),
            ("channels", SURROGATE_CHANNELS)):
        value = manifest[field]
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject("manifest " + field + " must be an integer")
        if value != expected_value:
            raise Reject("manifest " + field + " mismatch")
    if manifest["variant"] != CALLER_VARIANT:
        raise Reject("manifest variant must be " + CALLER_VARIANT)
    return manifest


def _hash_file(path: Path) -> str:
    return sha256(path.read_bytes())


def validate_manifest_identity(manifest: Any) -> Dict[str, Any]:
    """Validate shape, absolute paths, hashes and geometry only.

    This is deliberately weaker than admission: it never executes or loads an
    asset and it does not decide that the identity is approved. A caller may
    use it to check that a local asset set matches a supplied manifest.
    """
    checked = manifest_shape(manifest)
    for field in CALLER_DIR_FIELDS:
        if not Path(checked[field]).is_dir():
            raise Reject("manifest " + field + " directory is missing")
    total_bytes = 0
    for path_field, sha_field in CALLER_FILE_PAIRS:
        path = Path(checked[path_field])
        if not path.is_file():
            raise Reject("manifest " + path_field + " file is missing")
        actual = _hash_file(path)
        if actual != checked[sha_field]:
            raise Reject("manifest " + path_field + " SHA-256 mismatch")
        total_bytes += path.stat().st_size
    return {
        "identity_valid": True,
        "source_revision": checked["source_revision"],
        "variant": CALLER_VARIANT,
        "sample_rate_input_hz": SURROGATE_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SURROGATE_SAMPLE_RATE_HZ,
        "channels": SURROGATE_CHANNELS,
        "files_checked": len(CALLER_FILE_PAIRS),
        "directories_checked": len(CALLER_DIR_FIELDS),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
    }


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    checked = validate_manifest_identity(manifest)
    if APPROVED_SOURCE_REVISION is None:
        raise Reject(
            "no approved immutable source revision is pinned for this package")
    if checked["source_revision"] != APPROVED_SOURCE_REVISION:
        raise Reject("manifest source_revision is not the approved revision")
    if APPROVED_WEIGHTS_SHA256 is None:
        raise Reject("no approved weights SHA-256 is pinned for this package")
    if manifest["weights_sha256"] != APPROVED_WEIGHTS_SHA256:
        raise Reject("manifest weights_sha256 is not the approved digest")
    return {
        "accepted": True,
        "source_revision": checked["source_revision"],
        "variant": CALLER_VARIANT,
        "sample_rate_input_hz": SURROGATE_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SURROGATE_SAMPLE_RATE_HZ,
        "channels": SURROGATE_CHANNELS,
        "files_checked": checked["files_checked"],
        "directories_checked": checked["directories_checked"],
        "total_asset_bytes": checked["total_asset_bytes"],
        "model_executed": False,
    }


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It exercises fail-closed shape and existence checks only. It never resolves
    to a real asset and can never trigger admission.
    """
    root = "/nonexistent/convert-and-speak-evidence-fixture"
    digest = "0" * 64
    return {
        "channels": SURROGATE_CHANNELS,
        "config_path": root + "/config.json",
        "config_sha256": digest,
        "consent_record_path": root + "/consent.json",
        "consent_record_sha256": digest,
        "license_record_path": root + "/rights.json",
        "license_record_sha256": digest,
        "runtime_lock_path": root + "/requirements.lock",
        "runtime_lock_sha256": digest,
        "runtime_path": root + "/runtime",
        "sample_rate_input_hz": SURROGATE_SAMPLE_RATE_HZ,
        "sample_rate_output_hz": SURROGATE_SAMPLE_RATE_HZ,
        "source_archive_path": root + "/source.tar.gz",
        "source_archive_sha256": digest,
        "source_reference_path": root + "/source.wav",
        "source_reference_sha256": digest,
        "source_revision": "0" * 40,
        "target_reference_path": root + "/target.wav",
        "target_reference_sha256": digest,
        "variant": CALLER_VARIANT,
        "weights_path": root + "/weights.bin",
        "weights_sha256": digest,
    }


def run_adverse_controls() -> List[Dict[str, Any]]:
    good_source = synthetic_source_pcm()
    good_manifest = _shape_only_manifest()

    def case(case_id: str, action, guard: Optional[AccentSurrogate] = None
             ) -> Dict[str, Any]:
        before = guard.state_digest if guard is not None else None
        try:
            action()
        except Reject as error:
            unchanged = (guard is None or guard.state_digest == before)
            return {"case_id": case_id, "status": "rejected",
                    "state_unchanged": unchanged, "reason": str(error)}
        except Exception as error:  # noqa: BLE001 - recorded, never swallowed
            return {"case_id": case_id, "status": "unexpected_error",
                    "state_unchanged": False,
                    "reason": type(error).__name__ + ": " + str(error)}
        return {"case_id": case_id, "status": "accepted",
                "state_unchanged": guard is None
                or guard.state_digest == before, "reason": ""}

    def wrong(key: str, value: Any):
        manifest = dict(good_manifest)
        manifest[key] = value
        return lambda: validate_caller_manifest(manifest)

    def drop(key: str):
        manifest = {k: v for k, v in good_manifest.items() if k != key}
        return lambda: validate_caller_manifest(manifest)

    resetting = AccentSurrogate(epoch=1)
    processing = AccentSurrogate(epoch=1)

    cases: List[Tuple[str, Any, Optional[AccentSurrogate]]] = [
        ("pcm_empty", lambda: validate_pcm([]), None),
        ("pcm_not_sequence", lambda: validate_pcm(b"\x00\x00"), None),
        ("pcm_none", lambda: validate_pcm(None), None),
        ("pcm_wrong_rate_8000", lambda: validate_pcm(good_source, 8000),
         None),
        ("pcm_wrong_rate_44100", lambda: validate_pcm(good_source, 44100),
         None),
        ("pcm_stereo", lambda: validate_pcm(
            good_source, SURROGATE_SAMPLE_RATE_HZ, 2), None),
        ("pcm_nan", lambda: validate_pcm([0.0, math.nan]), None),
        ("pcm_pos_inf", lambda: validate_pcm([0.0, math.inf]), None),
        ("pcm_neg_inf", lambda: validate_pcm([0.0, -math.inf]), None),
        ("pcm_out_of_range_high", lambda: validate_pcm([0.0, 1.5]), None),
        ("pcm_out_of_range_low", lambda: validate_pcm([0.0, -1.5]), None),
        ("pcm_bool", lambda: validate_pcm([0.0, True]), None),
        ("pcm_string", lambda: validate_pcm([0.0, "0.1"]), None),
        ("pcm_too_long", lambda: validate_pcm(
            [0.0] * (PCM_SAMPLE_CAP + 1)), None),
        ("surrogate_epoch_zero", lambda: resetting.reset(0, 0), resetting),
        ("surrogate_epoch_negative", lambda: resetting.reset(-1, 0),
         resetting),
        ("surrogate_epoch_non_increasing", lambda: resetting.reset(1, 0),
         resetting),
        ("surrogate_negative_position", lambda: resetting.reset(2, -1),
         resetting),
        ("surrogate_epoch_bool", lambda: resetting.reset(True, 0), resetting),
        ("surrogate_nonfinite_input", lambda: processing.process(
            [0.0, math.nan]), processing),
        ("surrogate_nonfinite_output",
         lambda: validate_pcm(synthetic_poisoned_output()), None),
        ("surrogate_wrong_epoch", lambda: processing.process(
            good_source[:160], epoch=99), processing),
        ("manifest_not_object", lambda: validate_caller_manifest([]), None),
        ("manifest_missing_field", drop("weights_sha256"), None),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x")), None),
        ("manifest_relative_path", wrong("weights_path", "weights.bin"), None),
        ("manifest_bad_sha", wrong("weights_sha256", "ABC"), None),
        ("manifest_short_revision", wrong("source_revision", "0" * 8), None),
        ("manifest_nonhex_revision", wrong("source_revision", "g" * 40),
         None),
        ("manifest_wrong_input_rate", wrong("sample_rate_input_hz", 22050),
         None),
        ("manifest_wrong_output_rate",
         wrong("sample_rate_output_hz", 24000), None),
        ("manifest_wrong_channels", wrong("channels", 2), None),
        ("manifest_wrong_variant",
         wrong("variant", "incremental_streaming"), None),
        ("manifest_missing_asset", lambda: validate_manifest_identity(
            dict(good_manifest, weights_path=(
                "/nonexistent/convert-and-speak/weights.bin"))), None),
        ("manifest_unapproved_revision", lambda: validate_caller_manifest(
            good_manifest), None),
        ("fixture_bad_source_length", lambda: validate_fixture(
            dict(fixture_spec(), source_samples=1)), None),
        ("fixture_bad_target_length", lambda: validate_fixture(
            dict(fixture_spec(), target_samples=1)), None),
        ("fixture_bad_rate", lambda: validate_fixture(
            dict(fixture_spec(), sample_rate_hz=8000)), None),
        ("fixture_bad_ratio", lambda: validate_fixture(
            dict(fixture_spec(), qh15_scale=1)), None),
    ]
    results = [case(case_id, action, guard)
               for case_id, action, guard in cases]
    if [item["case_id"] for item in results] != list(ADVERSE_CASE_IDS):
        raise Reject("adverse case count or order mismatch")
    return results


# ---------------------------------------------------------------------------
# Control and report model.
# ---------------------------------------------------------------------------

def build_control() -> Dict[str, Any]:
    source = synthetic_source_pcm()
    target = synthetic_target_reference_pcm()
    surrogate = AccentSurrogate(epoch=1)
    output, process_result = surrogate.process(source)
    output_checked = validate_pcm(output)
    source_summary = pcm_summary(source, SURROGATE_SAMPLE_RATE_HZ)
    target_summary = pcm_summary(target, SURROGATE_SAMPLE_RATE_HZ)
    output_summary = pcm_summary(output_checked, SURROGATE_SAMPLE_RATE_HZ)
    durations = duration_accounting(len(source), len(output))
    alignment = alignment_accounting(len(output))
    reset_before = surrogate.state_digest
    reset_result = surrogate.reset(2, 0)
    fresh = AccentSurrogate(epoch=2)
    reset_matches_fresh = surrogate.state_digest == fresh.state_digest
    adverse = run_adverse_controls()
    rejected = [item["case_id"] for item in adverse
                if item["status"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "qualification_effect": "none",
        "surrogate": {
            "name": "integer_q15_one_pole_offline_accounting_control",
            "coefficient": "3/4",
            "q15_scale": Q15_SCALE,
            "input_sample_rate_hz": SURROGATE_SAMPLE_RATE_HZ,
            "output_sample_rate_hz": SURROGATE_SAMPLE_RATE_HZ,
            "channels": SURROGATE_CHANNELS,
            "mode": "offline_whole_utterance",
            "incremental_streaming": False,
            "content_delay_samples": 0,
            "algorithmic_latency_samples": None,
            "uses_target_reference": False,
        },
        "fixtures": {
            "spec": fixture_spec(),
            "source_pcm": source_summary,
            "target_reference_pcm": target_summary,
            "output_pcm": output_summary,
            "target_reference_used_for_scoring": False,
        },
        "process_result": process_result,
        "duration": durations,
        "alignment": alignment,
        "reset": {
            "surrogate_only": True,
            "epoch": 2,
            "matches_fresh": reset_matches_fresh,
            "state_changed": reset_before != reset_result["state_digest"],
            "rejects_zero": True,
            "rejects_negative": True,
            "rejects_non_increasing": True,
            "candidate_reset_asserted": False,
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
                "reason": "synthetic structural alignment only; no device clock",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "pcm_nan", "pcm_pos_inf", "pcm_neg_inf",
                "surrogate_nonfinite_input", "surrogate_nonfinite_output"],
            "invalid_rejected": [
                "pcm_bool", "pcm_string", "pcm_out_of_range_high",
                "pcm_out_of_range_low", "pcm_wrong_rate_8000",
                "pcm_wrong_rate_44100", "pcm_stereo", "surrogate_epoch_bool",
                "surrogate_epoch_zero", "surrogate_epoch_negative",
                "surrogate_epoch_non_increasing",
                "surrogate_negative_position", "surrogate_wrong_epoch",
                "fixture_bad_source_length", "fixture_bad_target_length",
                "fixture_bad_rate", "fixture_bad_ratio"],
            "missing_rejected": [
                "pcm_empty", "pcm_none", "pcm_not_sequence",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_unapproved_revision"],
            "rejected_case_count": len(rejected),
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "adverse_all_rejected": all(
            item["status"] == "rejected" for item in adverse),
        "note": (
            "Synthetic PCM accounting control only. It is not Convert and "
            "Speak output, not real accent-conversion audio, not a quality or "
            "timing result and cannot qualify the candidate."),
    }


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_sha256": SOURCE_PINS[
            "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "required_items": {
            item: {
                "requirement": requirement,
                "status": status,
                "qualification_effect": "none",
            }
            for item, requirement, status in VOICE_REQUIREMENTS
        },
        "satisfied_for_qualification": [],
        "blocked_items": sorted(
            item for item, _, status in VOICE_REQUIREMENTS
            if status in {"absent", "not_measured"}),
        "note": (
            "Structural accounting is not a Voice-profile result. No permitted "
            "reference pair, consent, rights-cleared cohort, exact runtime, "
            "transcript truth, identity measure, naturalness rating or timing "
            "exists, so every item is absent, unmeasured or structural only."),
    }


def _audit_summary(observed: Dict[str, Any]) -> Dict[str, Any]:
    complete = (
        observed["source_present"]
        and observed["weights_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"]
        and observed["rights_record_present"]
        and observed["consent_record_present"]
        and observed["cohort_manifest_present"])
    return {
        "qualified": False,
        "audit_result": (
            "asset_set_complete_pending_parity" if complete else "absent"),
        "source_present": observed["source_present"],
        "weights_present": observed["weights_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "rights_record_present": observed["rights_record_present"],
        "consent_record_present": observed["consent_record_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "sample_clip_count": observed["sample_clip_count"],
        "observed": observed,
        "note": (
            "Presence of a source tree or weight directory would still not be "
            "a licence, approved revision, cohort, parity or quality result. "
            "This audit never promotes presence to qualification."),
    }


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    observed = audit_assets()
    audit = _audit_summary(observed)
    control = build_control()
    gates = [
        {"id": gate, "requirement": requirement, "status": "blocked"}
        for gate, requirement in GATE_REQUIREMENTS
    ]
    profile = _acceptance_profile()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "repository": "audio-sdk",
        "version": VERSION,
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
            "missing_result_promoted": False,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "blocked_gate_count": len(gates),
            "blocked_gate_ids": [gate["id"] for gate in gates],
            "exact_source_present": False,
            "exact_weights_present": False,
            "exact_runtime_outputs_present": False,
            "rights_cleared_cohort": False,
            "geometry_documented": False,
            "parity_measured": False,
            "timing_measured": False,
            "listening": False,
            "real_corpus_used": False,
            "reason": (
                "No Convert and Speak source, weights, runtime, approved "
                "revision, licence, consent record, rights-cleared voice "
                "cohort, geometry, parity vector or timing result exists. The "
                "merged note records only an inspected paper/demo."),
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
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "candidate": {
            "name": TITLE,
            "reported_architecture": "autoregressive accent-conversion research",
            "reported_autoregressive_component": True,
            "reported_input_sample_rate_hz": None,
            "reported_output_sample_rate_hz": None,
            "reported_hop_samples": None,
            "reported_parameter_count": None,
            "geometry_documented": False,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "exact_numeric_output_present": False,
        },
        "reference": {
            "name": TITLE,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "implementation_present": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "surrogate_is_candidate": False,
            "pinned_revision": APPROVED_SOURCE_REVISION,
            "license_identity": None,
            "status": "blocked",
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "external_artifacts": {
            "status": "blocked",
            "any_present": False,
            "source_checkouts_searched": list(SOURCE_CANDIDATES),
            "weight_locations_searched": list(WEIGHTS_CANDIDATES),
            "runtime_environment": RUNTIME_ENV_PATH,
            "rights_record": RIGHTS_RECORD_PATH,
            "consent_record": CONSENT_RECORD_PATH,
            "cohort_manifest": COHORT_MANIFEST_PATH,
            "paper_demo_url": CANDIDATE_PAPER_DEMO_URL,
        },
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "acceptance_profile": profile,
        "licensing": {
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "source_license_present": False,
            "source_license_identity": None,
            "weight_terms_present": False,
            "model_card_present": False,
            "attribution_notice_staged": False,
            "training_data_statement_staged": False,
            "redistribution_reviewed": False,
            "product_use_reviewed": False,
            "review_status": "blocked",
        },
        "reference_protocol": control,
        "controls": {
            "adverse_all_rejected": control["adverse_all_rejected"],
            "adverse_case_count": len(control["adverse"]),
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
            "adverse": control["adverse"],
        },
        "release_gates": gates,
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "reopen_conditions": [
            {"gate_id": gate, "condition": requirement}
            for gate, requirement in GATE_REQUIREMENTS
        ],
        "candidate_metrics": None,
        "missing_historical_artifacts": [
            SOURCE_CANDIDATES[0],
            WEIGHTS_CANDIDATES[0],
            RUNTIME_LOCK_PATH,
            RIGHTS_RECORD_PATH,
            COHORT_MANIFEST_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model, tensor or audio runtime is "
            "imported.",
            "All asset observations use fixed workspace paths and local reads.",
            "The caller manifest contract validates shape, paths and hashes "
            "without importing or executing anything.",
            "The synthetic control uses integer Q15 arithmetic and an LCG; it "
            "invokes no libm synthesis and no audio device.",
            "No network request, download, model load, listening test, device "
            "clock or timing run occurs.",
        ],
        "repeatability": {
            "runs": 3,
            "byte_identical": True,
            "comparison": "canonical JSON bytes and SHA-256 only; no tolerance",
        },
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_text_generated_by": "reference.canonical_report",
        },
        "scope_note": (
            "Only this task-local evidence directory is added. The board is "
            "referenced by stable linked-row fields only; the mutable full "
            "plan/swarm/TASKS.json is never hashed."),
    }


# ---------------------------------------------------------------------------
# Contract, artifact pins and source manifest.
# ---------------------------------------------------------------------------

def artifact_pins(report_digest: str, sidecar_digest: str) -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in ARTIFACT_FILES:
        if name == "report.json":
            pins[TASK_PREFIX + name] = report_digest
        elif name == "report.json.sha256":
            pins[TASK_PREFIX + name] = sidecar_digest
        else:
            full = HERE / name
            if not full.is_file():
                raise Reject("missing artifact: " + name)
            pins[TASK_PREFIX + name] = file_digest(full)
    return pins


def build_contract(report: Dict[str, Any],
                   report_digest: str) -> Dict[str, Any]:
    sidecar_digest = sha256((report_digest + "  report.json\n").encode("ascii"))
    return {
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": "feasibility",
        "version": VERSION,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "profile": PROFILE,
        "verification_profile": PROFILE,
        "task_prefix": TASK_PREFIX,
        "write_scope": TASK_PREFIX,
        "acceptance_profile": report["acceptance_profile"],
        "candidate": report["candidate"],
        "format": report["format"],
        "licensing": report["licensing"],
        "artifact_pins": artifact_pins(report_digest, sidecar_digest),
        "board_row": report["task_row_identity"],
        "boundary": report["boundary"],
        "boundary_pins": report["boundary_pins"],
        "source_pins": report["source_pins"],
        "scope": report["scope"],
        "reference": report["reference"],
        "exact_blockers": report["exact_blockers"],
        "release_gates": report["release_gates"],
        "reopen_condition": (
            "Pin the exact licensed Convert and Speak source, weights and "
            "runtime with an immutable revision, hash-pinned isolated runtime, "
            "cleared code/weight/training-data/corpus/consent rights, a "
            "rights-cleared held-out voice cohort, exact geometry and "
            "alignment, an approved parity vector, measured target timing and "
            "completed opt-in provider intake. Until then the candidate stays "
            "DEFER, incomplete and not qualified."),
        "negative_claims": report["non_claims"],
        "caller_asset_contract": report["caller_asset_contract"],
        "source_reported_context": report["source_reported_context"],
        "qualification": report["qualification"],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no Convert and Speak source, weight, model, runtime or adapter is "
            "downloaded, copied, loaded or executed",
            "the synthetic integer one-pole control is not Convert and Speak "
            "and cannot qualify the candidate",
            "no candidate input rate, output rate, hop, mode, alignment, "
            "first-output or tail timing is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
    }


def sources_bytes(overrides: Optional[Dict[str, bytes]] = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for SDK-CONVERT-AND-SPEAK; source: paths are "
        "workspace-relative, worktree: paths are SDK-worktree-relative, pkg: "
        "paths are task-local. The mutable full plan/swarm/TASKS.json is never "
        "hashed."
    ]
    for path, digest in sorted(SOURCE_PINS.items()):
        lines.append(f"{digest}  source:{path}")
    for path, digest in sorted(BOUNDARY_PINS.items()):
        lines.append(f"{digest}  worktree:{path}")
    for name in PIN_FILES:
        if name in overrides:
            digest = sha256(overrides[name])
        else:
            full = HERE / name
            if not full.is_file():
                raise Reject("missing artifact: " + name)
            digest = file_digest(full)
        lines.append(f"{digest}  pkg:{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")


__all__ = [
    "AccentSurrogate", "ADVERSE_CASE_IDS", "ASSET_REQUIREMENTS",
    "BOUNDARY_PINS", "CALLER_ASSET_FIELDS", "CONTROL_PLAN_PROVENANCE",
    "EXACT_BLOCKERS", "GATE_REQUIREMENTS", "MUTABLE_TASK_FIELDS",
    "NON_CLAIMS", "PIN_FILES", "Reject", "SOURCE_PINS", "STABLE_TASK_FIELDS",
    "VOICE_REQUIREMENTS", "artifact_pins", "audit_assets", "build_contract",
    "build_control", "build_report", "canonical_bytes", "canonical_report",
    "canonical_text", "duration_accounting", "file_digest", "fixture_spec",
    "fraction_text", "load_strict_json", "manifest_shape", "pcm_summary",
    "run_adverse_controls", "sha256", "sources_bytes", "strict_loads",
    "synthetic_poisoned_output", "synthetic_source_pcm",
    "synthetic_target_reference_pcm", "task_row_identity",
    "validate_caller_manifest", "validate_fixture", "validate_pcm",
]
