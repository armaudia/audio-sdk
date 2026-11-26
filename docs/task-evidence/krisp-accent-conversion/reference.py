# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-KRISP-ACCENT-CONVERSION.

Krisp Accent Conversion is a closed commercial SDK/model.  No licensed SDK
package, model bundle, entitlement, vendor release identity, runtime, terms
record, accent-direction map, rights-cleared cohort or reference output exists
in this workspace.  The merged accent-conversion research package inspected the
vendor documentation only and records the candidate as "closed/proprietary
model, not locally downloadable".

This module therefore never imports a vendor SDK, never links or executes a
model, never reads or writes real audio, never handles an entitlement token,
never downloads anything and never measures a device clock.  It provides four
verifiable pieces:

* a fail-closed vendor-boundary audit over fixed workspace paths;
* a caller-supplied vendor-package manifest contract, validated without
  importing, linking or executing anything;
* a deterministic synthetic 16 kHz / mono / 160-frame *pass-through accounting
  control* that exercises exact frame and content-interval bookkeeping,
  direction exactness, invalid/missing/nonfinite rejection and a declared
  delay mapping - explicitly not accent conversion and not model output;
* the canonical evidence report model.

Nothing in this package qualifies the candidate.  The decision is ``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-KRISP-ACCENT-CONVERSION"
TITLE = "Krisp Accent Conversion"
SLUG = "krisp-accent-conversion"
COMPONENT = "krisp-accent-conversion"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "f006454da9a72fbfd394e2b5bd05105201a9cd29"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "voice"
MODE = "external-adapter"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "vendor_runtime_entitlement_and_opt_in_adapter"

# Vendor identity is unpublished.  No source repository, vendor release ID or
# artifact digest is invented.  The public documentation locator is retained as
# provenance only.
VENDOR_NAME = "Krisp Accent Conversion"
VENDOR_DOC_URL = "https://sdk-docs.krisp.ai/docs/accent-conversion"
VENDOR_DEVICE_URL = "https://sdk-docs.krisp.ai/docs/rtc-accent-conversion-device-sdk"
VENDOR_RELEASE_ID: Optional[str] = None
RELEASE_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")

# Recorded task geometry.  The SDK v0 frame boundary is fixed.  The vendor
# frame/hop contract is unpublished, so the adapter geometry is a caller
# requirement, not a vendor observation.
INPUT_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"
VARIANT = "vendor_sdk_caller_frame_160"
MAX_BUFFERING_DELAY_SAMPLES = 16000
DECLARED_SYNTHETIC_DELAY_SAMPLES = 160

# Recorded vendor claim only.  It is not a local measurement and not a pin.
VENDOR_REPORTED_LATENCY_MS = 180

# Fixed workspace paths.  Absence is recorded, never filled.
VENDOR_SDK_ROOT_PATH = "data/vendor/krisp/accent-conversion"
MODEL_BUNDLE_PATH = "checkpoints/krisp-accent-conversion"
RUNTIME_ENV_PATH = "data/envs/krisp-accent-conversion"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
LICENSE_RECORD_PATH = "data/licenses/krisp-accent-conversion/license.json"
ENTITLEMENT_RECORD_PATH = (
    "data/rights/krisp-accent-conversion-entitlement.json")
CONSENT_RECORD_PATH = "data/rights/krisp-accent-conversion-consent.json"
DIRECTION_MAP_PATH = "data/krisp-accent-conversion/accent-directions.json"
COHORT_MANIFEST_PATH = "data/runs/krisp-accent-conversion-cohort/manifest.json"
TARGET_REFERENCE_PATH = "data/reference/krisp-accent-conversion/targets.json"
RESEARCH_SAMPLE_PATH = "research/accent-conversion-20261101/data/l2accent"

VENDOR_ARTIFACT_SUFFIXES = (
    ".aar", ".bin", ".dylib", ".framework", ".mlmodel", ".mlpackage",
    ".onnx", ".so", ".tflite", ".xcframework",
)
MODEL_ARTIFACT_SUFFIXES = (
    ".bin", ".ckpt", ".mlmodel", ".onnx", ".pt", ".pth", ".safetensors",
    ".tflite",
)
ALLOWED_RUNTIME_PLATFORMS = (
    "android-arm64",
    "darwin-arm64",
    "darwin-x86_64",
    "ios-arm64",
    "linux-x86_64",
)

MAX_MANIFEST_BYTES = 64 * 1024 ** 3

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
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/accent-conversion-20261101/README.md":
        "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
    "research/voice-enhancement-20261101/agent-transform-space/REPORT.md":
        "479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
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
    "sdk_v0_sample_format": SAMPLE_FORMAT,
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "adapter_input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
    "adapter_input_channels": CHANNELS,
    "adapter_input_sample_format": SAMPLE_FORMAT,
    "adapter_frame_samples": SDK_FRAME_SAMPLES,
    "adapter_variant": VARIANT,
    "adapter_streaming_claimed": False,
    "vendor_frame_hop_contract_published": False,
    "vendor_directions_published": False,
    "vendor_output_contract_published": False,
    "sdk_v0_geometry_preserved": True,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_code_added": False,
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "entitlement_token_handled": False,
    "installed_v0_behavior_change": False,
    "model_weights_vendored": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "sdk_callback_invoked": False,
    "shared_build_or_ci_change": False,
    "vendor_sdk_linked": False,
    "vendor_sdk_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "device_timing": False,
    "entitlement_used": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "real_krisp_model": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "vendor_sdk_linked": False,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No Krisp SDK, model bundle, runtime or entitlement is loaded, linked or executed.",
    "No vendor library, Python package, model runtime or audio decoder is imported.",
    "No network request, download, staging, token exchange or asset redistribution occurs.",
    "No real audio, corpus, transcript, target reference or consent record is consumed.",
    "No accent conversion, accent movement, identity, naturalness, latency, memory or RTF is measured here.",
    "The merged research finding and vendor latency figure are provenance only and are not reproduced or rescored.",
    "The synthetic pass-through accounting control is a contract control, never model output.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI changed.",
    "No ad-hoc adapter is prototyped without an approved public or user-supplied runtime.",
    "Missing evidence never qualifies the candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "vendor_sdk_package",
        "path": VENDOR_SDK_ROOT_PATH,
        "vendor_doc_url": VENDOR_DOC_URL,
        "release_id": None,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No licensed Krisp Accent Conversion SDK package or vendor release "
            "identity exists in the workspace; the model is closed and "
            "proprietary."),
    },
    {
        "id": "model_bundle",
        "path": MODEL_BUNDLE_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No accent-conversion model bundle, byte count or digest is "
            "published or present; only the vendor documentation was inspected."),
    },
    {
        "id": "exact_runtime",
        "runtime_lock_sha256": None,
        "runtime_platform": None,
        "required": True,
        "status": "absent",
        "note": (
            "No isolated Krisp runtime, package lock or recorded platform "
            "exists; no vendor runtime was ever installed."),
    },
    {
        "id": "entitlement_record",
        "path": ENTITLEMENT_RECORD_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No named evaluation agreement, subscription entitlement or usage "
            "rights record exists; no token is read, stored or handled here."),
    },
    {
        "id": "license_and_terms_record",
        "path": LICENSE_RECORD_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No vendor licence, evaluation terms, redistribution grant or "
            "product-use review has been observed."),
    },
    {
        "id": "rights_and_consent_record",
        "path": CONSENT_RECORD_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "Input-speech, speaker-reference, consent, output-use and "
            "redistribution rights are unresolved."),
    },
    {
        "id": "accent_direction_map",
        "path": DIRECTION_MAP_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "The vendor's supported English accent direction list, ordering "
            "and identifiers are unpublished in the merged evidence and are "
            "not invented here."),
    },
    {
        "id": "accent_cohort_and_targets",
        "path": COHORT_MANIFEST_PATH,
        "target_reference_path": TARGET_REFERENCE_PATH,
        "sha256": None,
        "required": True,
        "status": "absent",
        "note": (
            "No rights-cleared source-accent cohort, target-accent reference "
            "set, language/speaker grouping or held-out truth exists."),
    },
)

CALLER_ASSET_FIELDS = (
    "vendor_sdk_version",
    "vendor_release_id",
    "input_sample_rate_hz",
    "input_channels",
    "frame_samples",
    "sample_format",
    "variant",
    "vendor_sdk_package_path",
    "vendor_sdk_package_sha256",
    "model_bundle_path",
    "model_bundle_sha256",
    "runtime_library_path",
    "runtime_library_sha256",
    "runtime_platform",
    "entitlement_record_path",
    "entitlement_record_sha256",
    "license_record_path",
    "license_record_sha256",
    "consent_record_path",
    "consent_record_sha256",
    "direction_map_path",
    "direction_map_sha256",
    "cohort_manifest_path",
    "cohort_manifest_sha256",
    "target_reference_path",
    "target_reference_sha256",
)

CALLER_FILE_PAIRS = (
    ("vendor_sdk_package_path", "vendor_sdk_package_sha256"),
    ("model_bundle_path", "model_bundle_sha256"),
    ("runtime_library_path", "runtime_library_sha256"),
    ("entitlement_record_path", "entitlement_record_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("consent_record_path", "consent_record_sha256"),
    ("direction_map_path", "direction_map_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("target_reference_path", "target_reference_sha256"),
)
CALLER_SHA_FIELDS = tuple(sha for _, sha in CALLER_FILE_PAIRS)

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-vendor-package/0.1",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "entitlement_token_is_never_read": True,
    "absent_behavior": "reject_before_processing",
    "present_behavior": (
        "validate_absolute_paths_sha256_geometry_and_vendor_release_shape_only;"
        "_do_not_import_link_or_execute_in_this_package"),
    "required_fields": list(CALLER_ASSET_FIELDS),
    "required_variant": VARIANT,
    "required_release_id": VENDOR_RELEASE_ID,
    "release_policy": (
        "A caller must supply an exact vendor release ID, but no approved "
        "vendor release, entitlement or terms record has been observed.  "
        "Structural acceptance never sets vendor_release_approved, "
        "revision_pinned or qualification."),
    "required_geometry": {
        "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "input_channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
    },
    "allowed_runtime_platforms": list(ALLOWED_RUNTIME_PLATFORMS),
    "notes": (
        "The vendor SDK package, model bundle, runtime library, entitlement "
        "record, licence, consent, direction map, cohort manifest and target "
        "reference must exist at absolute paths and match declared SHA-256 "
        "values before a caller may process audio.  The validator never "
        "imports, links or executes a vendor artifact."),
}

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "vendor_sdk_artifact_absent",
        "state": "absent",
        "requirement": (
            "Supply a licensed Krisp Accent Conversion SDK package at one exact "
            "vendor release ID with a SHA-256 digest; no SDK package, source or "
            "release identity exists in the workspace."),
    },
    {
        "id": "model_bundle_digest_unpublished",
        "state": "absent",
        "requirement": (
            "Publish the exact model bundle name, byte count and SHA-256 for the "
            "licensed build; the merged evidence records no model digest and "
            "the model is not locally downloadable."),
    },
    {
        "id": "entitlement_and_terms_absent",
        "state": "absent",
        "requirement": (
            "Record a named evaluation entitlement plus the vendor licence, "
            "evaluation terms, redistribution grant and product-use approval; "
            "no agreement or terms text has been observed."),
    },
    {
        "id": "runtime_unpinned_and_absent",
        "state": "absent",
        "requirement": (
            "Provide an isolated hash-pinned runtime with a complete lock, "
            "recorded platform, ABI version and supported architectures; no "
            "Krisp environment was ever installed."),
    },
    {
        "id": "accent_directions_unpublished",
        "state": "absent",
        "requirement": (
            "Publish the exact supported English accent direction set, stable "
            "direction identifiers, ordering and source/target semantics; the "
            "merged evidence only says selected English directions exist."),
    },
    {
        "id": "rights_and_consent_uncleared",
        "state": "absent",
        "requirement": (
            "Clear input-speech, speaker-reference, consent, output-use and "
            "redistribution rights with complete notices for every evaluation "
            "clip."),
    },
    {
        "id": "matched_cohort_and_scoring_absent",
        "state": "absent",
        "requirement": (
            "Freeze a rights-cleared source-accent cohort with matched target "
            "references, language/speaker groups and held-out truth, then score "
            "content, identity, naturalness and accent movement separately."),
    },
    {
        "id": "approved_reference_parity_absent",
        "state": "absent",
        "requirement": (
            "Produce an approved exact-runtime parity vector on frozen 16 kHz "
            "mono PCM for one vendor release, including frame accounting, "
            "content delay, first output, tail and fresh-process reset."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    (
        "exact_vendor_sdk_and_model_identity",
        "The exact vendor release ID, SDK package SHA-256, model bundle digest "
        "and runtime library identity match approved pins.",
    ),
    (
        "entitled_runtime_admission",
        "A named entitlement plus an isolated hash-pinned runtime with a "
        "recorded platform and ABI is admitted for evaluation.",
    ),
    (
        "vendor_terms_and_rights",
        "Vendor licence, evaluation terms, redistribution, input-speech, "
        "speaker-reference, consent, output-use and notice requirements are "
        "cleared.",
    ),
    (
        "exact_reference_parity",
        "An approved exact-runtime output, frame accounting, content delay, "
        "first output and tail match the reference on frozen 16 kHz mono PCM.",
    ),
    (
        "accent_direction_and_cohort_scoring",
        "Exact direction identifiers and a rights-cleared held-out cohort score "
        "accent movement, content preservation, identity and naturalness with "
        "frozen language and speaker groups.",
    ),
    (
        "voice_outcome_separation",
        "Text/semantic preservation, identity/similarity, naturalness and "
        "alignment are reported as separate outcomes, never pooled with vendor "
        "claims.",
    ),
    (
        "opt_in_provider_intake",
        "A caller-supplied-runtime adapter is prototyped only after licence, "
        "entitlement, descriptor, ABI and independent public-surface review.",
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
        "Freeze task, language, accent-direction and speaker groups.",
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
    "secondary_source": (
        "research/voice-enhancement-20261101/agent-transform-space/REPORT.md"),
    "secondary_source_sha256": SOURCE_PINS[
        "research/voice-enhancement-20261101/agent-transform-space/REPORT.md"],
    "candidate": VENDOR_NAME,
    "vendor_doc_url": VENDOR_DOC_URL,
    "vendor_device_url": VENDOR_DEVICE_URL,
    "reported_status": "closed/proprietary model, not locally downloadable",
    "reported_disposition": "Product benchmark only",
    "reported_latency_approx_ms": VENDOR_REPORTED_LATENCY_MS,
    "reported_platforms": "device and server SDK; iOS and Android named",
    "reported_directions": "selected English accent directions",
    "reported_reason": (
        "Commercial SDK/model access entitlement absent; vendor latency is not "
        "locally reproducible."),
    "notes": (
        "The merged research package inspected vendor documentation only and "
        "never obtained, loaded or executed Krisp Accent Conversion.  No "
        "accent-conversion, identity, naturalness, accuracy, latency, memory or "
        "RTF result exists for the candidate in that evidence.  The vendor "
        "latency figure is a source claim, not a measured value."),
}

CONTROL_PLAN_PROVENANCE = (
    "caller_supplied_synthetic_16k_mono_160_frame_passthrough_accounting_control"
    "_not_model_output")

# Synthetic placeholder direction identifiers.  They are deliberately not
# vendor accent names, which are unpublished.
SYNTHETIC_DIRECTIONS: Tuple[Tuple[str, str], ...] = (
    ("synthetic_accent_a", "synthetic_accent_b"),
    ("synthetic_accent_c", "synthetic_accent_d"),
)

ACCEPTED_TOTAL_SAMPLES = 3 * SDK_FRAME_SAMPLES + 5

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "frame_short",
    "frame_long",
    "frame_bytes",
    "frame_none",
    "frame_nan",
    "frame_pos_inf",
    "frame_neg_inf",
    "frame_above_one",
    "frame_below_minus_one",
    "frame_bool",
    "frame_string",
    "direction_not_sequence",
    "direction_one",
    "direction_three",
    "direction_equal",
    "direction_unknown",
    "direction_non_ascii",
    "direction_non_string",
    "interval_negative_total",
    "interval_bool_total",
    "interval_negative_delay",
    "interval_delay_too_large",
    "interval_float_delay",
    "interval_nonfinite_delay",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_relative_path",
    "manifest_bad_sha",
    "manifest_empty_release",
    "manifest_short_release",
    "manifest_wrong_rate",
    "manifest_wrong_channels",
    "manifest_wrong_frame",
    "manifest_wrong_sample_format",
    "manifest_wrong_variant",
    "manifest_wrong_platform",
    "manifest_missing_asset",
    "manifest_duplicate_path",
    "manifest_wrong_bundle_hash",
)


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


# ---------------------------------------------------------------------------
# Vendor-boundary audit.  Fixed local reads only; no network, no execution.
# ---------------------------------------------------------------------------

def _artifact_files(directory: Path,
                    suffixes: Sequence[str]) -> List[str]:
    if not directory.is_dir():
        return []
    found: List[str] = []
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if name.endswith(tuple(suffixes)):
            found.append(path.relative_to(directory).as_posix())
    return sorted(found)


def _research_clip_count() -> int:
    directory = SOURCE_ROOT / RESEARCH_SAMPLE_PATH
    if not directory.is_dir():
        return 0
    return len([path for path in directory.iterdir()
                if path.is_file() and path.suffix.lower() == ".wav"])


def audit_assets() -> Dict[str, Any]:
    sdk_root = SOURCE_ROOT / VENDOR_SDK_ROOT_PATH
    model_root = SOURCE_ROOT / MODEL_BUNDLE_PATH
    vendor_files = _artifact_files(sdk_root, VENDOR_ARTIFACT_SUFFIXES)
    model_files = _artifact_files(model_root, MODEL_ARTIFACT_SUFFIXES)
    return {
        "vendor_sdk_root_path": VENDOR_SDK_ROOT_PATH,
        "vendor_sdk_root_present": sdk_root.is_dir(),
        "vendor_sdk_file_count": len(vendor_files),
        "vendor_sdk_files_found": vendor_files,
        "model_bundle_path": MODEL_BUNDLE_PATH,
        "model_bundle_dir_present": model_root.is_dir(),
        "model_bundle_file_count": len(model_files),
        "model_bundle_files_found": model_files,
        "release_id_known": VENDOR_RELEASE_ID is not None,
        "license_record_present": (SOURCE_ROOT / LICENSE_RECORD_PATH).is_file(),
        "entitlement_record_present": (
            SOURCE_ROOT / ENTITLEMENT_RECORD_PATH).is_file(),
        "consent_record_present": (
            SOURCE_ROOT / CONSENT_RECORD_PATH).is_file(),
        "direction_map_present": (SOURCE_ROOT / DIRECTION_MAP_PATH).is_file(),
        "cohort_manifest_present": (
            SOURCE_ROOT / COHORT_MANIFEST_PATH).is_file(),
        "target_reference_present": (
            SOURCE_ROOT / TARGET_REFERENCE_PATH).is_file(),
        "runtime_env_present": (SOURCE_ROOT / RUNTIME_ENV_PATH).is_dir(),
        "runtime_lock_present": (SOURCE_ROOT / RUNTIME_LOCK_PATH).is_file(),
        "research_demo_audio_clip_count": _research_clip_count(),
        "requested_config": {
            "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
            "input_channels": CHANNELS,
            "frame_samples": SDK_FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
            "variant": VARIANT,
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
# Task-local git scope
# ---------------------------------------------------------------------------
# The merged squash lands on `main`; later merges add unrelated sibling task
# packages. A fixed historical commit therefore cannot be the scope base: it
# would report those siblings as out-of-scope edits of this task. The base is
# the newest merge-base between HEAD and the PR base refs, so the comparison
# contains exactly the commits this branch added and fail-closed scope checks
# still catch any edit outside TASK_PREFIX.
SCOPE_BASE_REFS = ("origin/main", "main")


def _git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True)


def git_commit(worktree: Path, ref: str) -> Optional[str]:
    """Return the commit SHA a ref resolves to, or None when it is absent."""
    result = _git(worktree, "rev-parse", "--verify", "--quiet",
                  ref + "^{commit}")
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def scope_base(worktree: Path,
               refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> Optional[str]:
    """Newest merge-base between HEAD and an available PR base ref.

    Returns None only when no base ref exists, which the verifier treats as a
    fail-closed condition rather than a silent pass.
    """
    best: Optional[str] = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor",
                best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    """Paths changed by this branch relative to its merge-base."""
    result = _git(worktree, "diff", "--name-only", "--no-renames",
                  base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str],
                     prefix: str = TASK_PREFIX) -> List[str]:
    """Return changed paths outside the task-local write scope."""
    return [path for path in paths if path and not path.startswith(prefix)]


# ---------------------------------------------------------------------------
# Deterministic synthetic pass-through accounting control.
# ---------------------------------------------------------------------------

def synthetic_frame(index: int) -> List[float]:
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        raise Reject("frame index must be a nonnegative integer")
    return [((sample * 37 + index * 11) % 997 - 498) / 1000.0
            for sample in range(SDK_FRAME_SAMPLES)]


def validate_frame(samples: Any) -> List[float]:
    if not isinstance(samples, (list, tuple)):
        raise Reject("frame must be a sequence")
    if len(samples) != SDK_FRAME_SAMPLES:
        raise Reject("frame must contain exactly 160 samples")
    checked: List[float] = []
    for index, sample in enumerate(samples):
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise Reject(f"sample {index} is not numeric")
        value = float(sample)
        if not math.isfinite(value):
            raise Reject(f"sample {index} is not finite")
        if value < -1.0 or value > 1.0:
            raise Reject(f"sample {index} is outside [-1, 1]")
        checked.append(value)
    return checked


def validate_direction(direction: Any) -> Tuple[str, str]:
    if not isinstance(direction, (list, tuple)):
        raise Reject("direction must be a two-entry sequence")
    if len(direction) != 2:
        raise Reject("direction must contain exactly two entries")
    checked: List[str] = []
    for index, part in enumerate(direction):
        if not isinstance(part, str):
            raise Reject(f"direction entry {index} is not a string")
        if not part or not part.strip():
            raise Reject(f"direction entry {index} is empty")
        if not part.isascii():
            raise Reject(f"direction entry {index} is not ASCII")
        checked.append(part)
    if checked[0] == checked[1]:
        raise Reject("direction source and target must differ")
    pair = (checked[0], checked[1])
    if pair not in SYNTHETIC_DIRECTIONS:
        raise Reject("direction is not in the closed synthetic set")
    return pair


def passthrough_frame(samples: Any) -> Dict[str, Any]:
    checked = validate_frame(samples)
    output = list(checked)
    return {
        "consumed_count": SDK_FRAME_SAMPLES,
        "produced_count": SDK_FRAME_SAMPLES,
        "valid_offset": 0,
        "valid_count": SDK_FRAME_SAMPLES,
        "transform_applied": False,
        "converted_speech": False,
        "output_sha256": sha256(canonical_bytes(
            [f"{value:.6f}" for value in output])),
    }


def plan_intervals(accepted_total: int,
                   delay: int) -> List[Dict[str, Any]]:
    if isinstance(accepted_total, bool) or not isinstance(accepted_total, int):
        raise Reject("accepted_total must be an integer")
    if accepted_total < 0:
        raise Reject("accepted_total must be nonnegative")
    if isinstance(delay, bool) or not isinstance(delay, int):
        raise Reject("delay must be an integer")
    if delay < 0 or delay > MAX_BUFFERING_DELAY_SAMPLES:
        raise Reject("delay is outside the v0 buffering bound")

    calls: List[Dict[str, Any]] = []
    process_count = (accepted_total + SDK_FRAME_SAMPLES - 1) // SDK_FRAME_SAMPLES
    for index in range(process_count):
        start = index * SDK_FRAME_SAMPLES - delay
        end = start + SDK_FRAME_SAMPLES
        valid_offset = max(0, -start)
        valid_count = max(0, min(end, accepted_total) - max(start, 0))
        calls.append({
            "kind": "process",
            "call_index": index,
            "source_first_sample": start,
            "output_samples": SDK_FRAME_SAMPLES,
            "valid_offset": valid_offset,
            "valid_count": valid_count,
        })

    covered_start = process_count * SDK_FRAME_SAMPLES - delay
    remaining = max(0, accepted_total - max(0, covered_start))
    covered_end = max(0, covered_start)
    drain_index = 0
    while remaining > 0:
        valid_count = min(SDK_FRAME_SAMPLES, remaining)
        calls.append({
            "kind": "drain",
            "call_index": drain_index,
            "source_first_sample": covered_end,
            "output_samples": SDK_FRAME_SAMPLES,
            "valid_offset": 0,
            "valid_count": valid_count,
        })
        covered_end += valid_count
        remaining -= valid_count
        drain_index += 1
    return calls


def interval_coverage(plan: Sequence[Dict[str, Any]],
                      accepted_total: int) -> Dict[str, Any]:
    covered: List[int] = []
    for call in plan:
        start = call["source_first_sample"] + call["valid_offset"]
        covered.extend(range(start, start + call["valid_count"]))
    expected = list(range(accepted_total))
    duplicates = len(covered) != len(set(covered))
    return {
        "expected_samples": accepted_total,
        "covered_samples": len(covered),
        "duplicates": duplicates,
        "exact_union_match": (not duplicates) and covered == expected,
        "negative_coordinates": any(
            call["source_first_sample"] < 0 for call in plan),
    }


def build_control() -> Dict[str, Any]:
    plan = plan_intervals(ACCEPTED_TOTAL_SAMPLES,
                          DECLARED_SYNTHETIC_DELAY_SAMPLES)
    coverage = interval_coverage(plan, ACCEPTED_TOTAL_SAMPLES)
    frames = [synthetic_frame(0), synthetic_frame(1)]
    passthrough = [passthrough_frame(frame) for frame in frames]
    direction = validate_direction(SYNTHETIC_DIRECTIONS[0])
    adverse = run_adverse_controls()
    rejected = [item["case"] for item in adverse
                if item["result"] == "rejected"]
    return {
        "model_executed": False,
        "executor": "absent",
        "plan_source": CONTROL_PLAN_PROVENANCE,
        "variant": VARIANT,
        "geometry": {
            "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
            "input_channels": CHANNELS,
            "frame_samples": SDK_FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
            "mode": VARIANT,
            "incremental_streaming_claimed": False,
        },
        "synthetic_direction_set": [list(pair) for pair in SYNTHETIC_DIRECTIONS],
        "synthetic_direction_set_is_placeholder": True,
        "vendor_direction_names_available": False,
        "accepted_total_samples": ACCEPTED_TOTAL_SAMPLES,
        "declared_synthetic_delay_samples": DECLARED_SYNTHETIC_DELAY_SAMPLES,
        "plan": plan,
        "plan_sha256": sha256(canonical_bytes(plan)),
        "coverage": coverage,
        "selected_direction": list(direction),
        "passthrough": {
            "frame_count": len(frames),
            "records": passthrough,
            "input_sha256": sha256(canonical_bytes(
                [[f"{value:.6f}" for value in frame] for frame in frames])),
            "transform_applied": False,
            "converted_speech": False,
        },
        "acceptance_outcomes": [
            {
                "id": "accent_movement",
                "measured": False,
                "value": None,
                "reason": "no vendor runtime, direction map or cohort",
            },
            {
                "id": "text_and_semantic_preservation",
                "measured": False,
                "value": None,
                "reason": "no vendor output and no transcript scoring",
            },
            {
                "id": "identity_similarity",
                "measured": False,
                "value": None,
                "reason": "no speaker reference, embedder runtime or consent",
            },
            {
                "id": "naturalness",
                "measured": False,
                "value": None,
                "reason": "no converted audio and no authorized listener panel",
            },
            {
                "id": "alignment_and_output_timing",
                "measured": False,
                "value": None,
                "reason": "structural interval control only; no device clock",
            },
            {
                "id": "vendor_latency_reproduction",
                "measured": False,
                "value": None,
                "reason": "vendor ~180 ms figure is a source claim, not measured",
            },
        ],
        "validity_separation": {
            "synthetic_control_accepted": True,
            "nonfinite_rejected": [
                "frame_nan", "frame_pos_inf", "frame_neg_inf",
                "interval_nonfinite_delay"],
            "invalid_rejected": [
                "frame_above_one", "frame_below_minus_one", "frame_bool",
                "frame_string", "direction_equal", "direction_one",
                "direction_three", "direction_unknown", "direction_non_ascii",
                "direction_non_string", "interval_negative_total",
                "interval_bool_total", "interval_negative_delay",
                "interval_delay_too_large", "interval_float_delay",
                "manifest_wrong_rate", "manifest_wrong_channels",
                "manifest_wrong_frame", "manifest_wrong_sample_format",
                "manifest_wrong_variant", "manifest_wrong_platform",
                "manifest_wrong_bundle_hash"],
            "missing_rejected": [
                "frame_short", "frame_none", "direction_not_sequence",
                "manifest_missing_field", "manifest_missing_asset",
                "manifest_empty_release"],
            "rejected_cases": rejected,
        },
        "adverse": adverse,
        "qualification_effect": "none",
        "note": (
            "Synthetic pass-through accounting control only.  The direction "
            "names are placeholders, the frames are analytic, the transform is "
            "identity and no Krisp runtime exists.  This is not accent "
            "conversion, not model output and cannot qualify the candidate."),
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    good_frame = synthetic_frame(0)
    good_direction = SYNTHETIC_DIRECTIONS[0]
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
        ("frame_short", lambda: validate_frame(good_frame[:159])),
        ("frame_long", lambda: validate_frame(good_frame + [0.0])),
        ("frame_bytes", lambda: validate_frame(b"0" * 160)),
        ("frame_none", lambda: validate_frame(None)),
        ("frame_nan", lambda: validate_frame([math.nan] + good_frame[1:])),
        ("frame_pos_inf", lambda: validate_frame([math.inf] + good_frame[1:])),
        ("frame_neg_inf", lambda: validate_frame([-math.inf] + good_frame[1:])),
        ("frame_above_one", lambda: validate_frame([1.5] + good_frame[1:])),
        ("frame_below_minus_one", lambda: validate_frame(
            [-1.5] + good_frame[1:])),
        ("frame_bool", lambda: validate_frame([True] + good_frame[1:])),
        ("frame_string", lambda: validate_frame(["0.0"] + good_frame[1:])),
        ("direction_not_sequence", lambda: validate_direction("a->b")),
        ("direction_one", lambda: validate_direction([good_direction[0]])),
        ("direction_three", lambda: validate_direction(
            [good_direction[0], good_direction[1], "extra"])),
        ("direction_equal", lambda: validate_direction(
            ["synthetic_accent_a", "synthetic_accent_a"])),
        ("direction_unknown", lambda: validate_direction(
            ["synthetic_accent_a", "vendor_accent_z"])),
        ("direction_non_ascii", lambda: validate_direction(
            ["synthetic_accent_a", "accent\u00e9"])),
        ("direction_non_string", lambda: validate_direction(
            ["synthetic_accent_a", 7])),
        ("interval_negative_total", lambda: plan_intervals(-1, 0)),
        ("interval_bool_total", lambda: plan_intervals(True, 0)),
        ("interval_negative_delay", lambda: plan_intervals(160, -1)),
        ("interval_delay_too_large", lambda: plan_intervals(
            160, MAX_BUFFERING_DELAY_SAMPLES + 1)),
        ("interval_float_delay", lambda: plan_intervals(160, 160.0)),
        ("interval_nonfinite_delay", lambda: plan_intervals(160, math.nan)),
        ("manifest_not_object", lambda: validate_caller_manifest([])),
        ("manifest_missing_field", drop("target_reference_sha256")),
        ("manifest_extra_field", lambda: validate_caller_manifest(
            dict(good_manifest, extra_field="x"))),
        ("manifest_relative_path", wrong(
            "model_bundle_path", "vendor/model.bin")),
        ("manifest_bad_sha", wrong("model_bundle_sha256", "ABC")),
        ("manifest_empty_release", wrong("vendor_release_id", "")),
        ("manifest_short_release", wrong("vendor_release_id", "x")),
        ("manifest_wrong_rate", wrong("input_sample_rate_hz", 22050)),
        ("manifest_wrong_channels", wrong("input_channels", 2)),
        ("manifest_wrong_frame", wrong("frame_samples", 80)),
        ("manifest_wrong_sample_format", wrong("sample_format", "s16")),
        ("manifest_wrong_variant", wrong("variant", "vendor_native_stream")),
        ("manifest_wrong_platform", wrong("runtime_platform", "plan9-mips")),
        ("manifest_missing_asset", wrong(
            "runtime_library_path",
            "/nonexistent/krisp-evidence-fixture/runtime.dylib")),
        ("manifest_duplicate_path", wrong(
            "target_reference_path", good_manifest["cohort_manifest_path"])),
        ("manifest_wrong_bundle_hash", wrong(
            "model_bundle_sha256", "0" * 64)),
    ]
    results = [case(case_id, action) for case_id, action in cases]
    if len(results) != len(ADVERSE_CASE_IDS):
        raise Reject("adverse case count mismatch")
    return results


def _shape_only_manifest() -> Dict[str, Any]:
    """A shape-valid manifest whose assets are deliberately absent.

    It only exercises fail-closed shape checks.  Validation reaches the
    missing-asset branch before any asset is hashed.
    """

    root = "/nonexistent/krisp-evidence-fixture"
    digest = "0" * 64
    manifest: Dict[str, Any] = {
        "vendor_sdk_version": "9.9.9-synthetic",
        "vendor_release_id": "synthetic-release",
        "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "input_channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "variant": VARIANT,
        "runtime_platform": ALLOWED_RUNTIME_PLATFORMS[0],
    }
    for path_field, sha_field in CALLER_FILE_PAIRS:
        stem = path_field.replace("_path", "")
        manifest[path_field] = f"{root}/{stem}.bin"
        manifest[sha_field] = digest
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


def _absolute_path(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise Reject("manifest " + field + " must be a path string")
    path = Path(value)
    if not path.is_absolute():
        raise Reject("manifest " + field + " must be absolute")
    return path


def _sha_value(value: Any, field: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise Reject("manifest " + field + " is not a lowercase SHA-256")
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

    for field in ("vendor_sdk_version", "vendor_release_id"):
        value = manifest[field]
        if not isinstance(value, str) or len(value) < 2:
            raise Reject("manifest " + field + " is not an exact ASCII token")
        if not RELEASE_TOKEN.fullmatch(value):
            raise Reject("manifest " + field + " is not an exact ASCII token")
    if manifest["variant"] != VARIANT:
        raise Reject("manifest variant must be " + VARIANT)
    if manifest["sample_format"] != SAMPLE_FORMAT:
        raise Reject("manifest sample_format must be " + SAMPLE_FORMAT)
    if manifest["runtime_platform"] not in ALLOWED_RUNTIME_PLATFORMS:
        raise Reject("manifest runtime_platform is not in the allowed set")
    for field, expected_value in (
            ("input_sample_rate_hz", INPUT_SAMPLE_RATE_HZ),
            ("input_channels", CHANNELS),
            ("frame_samples", SDK_FRAME_SAMPLES)):
        value = manifest[field]
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject("manifest " + field + " must be an integer")
        if value != expected_value:
            raise Reject("manifest " + field + " mismatch")

    for sha_field in CALLER_SHA_FIELDS:
        _sha_value(manifest[sha_field], sha_field)
    file_paths: List[Tuple[str, Path]] = []
    for path_field, _sha_field in CALLER_FILE_PAIRS:
        file_paths.append(
            (path_field, _absolute_path(manifest[path_field], path_field)))
    resolved = [str(path) for _field, path in file_paths]
    if len(set(resolved)) != len(resolved):
        raise Reject("manifest asset paths must be unique")

    for field, path in file_paths:
        if not path.is_file():
            raise Reject("manifest " + field + " file is missing")

    total_bytes = 0
    for path_field, path in file_paths:
        declared = manifest[path_field.replace("_path", "_sha256")]
        if _hash_file(path) != declared:
            raise Reject("manifest " + path_field + " SHA-256 mismatch")
        total_bytes += path.stat().st_size

    return {
        "accepted": True,
        "accepted_for_qualification": False,
        "vendor_release_id": manifest["vendor_release_id"],
        "vendor_release_approved": False,
        "entitlement_approved": False,
        "revision_pinned": False,
        "variant": VARIANT,
        "input_sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "input_channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "runtime_platform": manifest["runtime_platform"],
        "files_checked": len(file_paths),
        "total_asset_bytes": total_bytes,
        "model_executed": False,
        "vendor_sdk_linked": False,
        "qualification_effect": "none",
    }


# ---------------------------------------------------------------------------
# Report model.
# ---------------------------------------------------------------------------

def _asset_audit_summary() -> Dict[str, Any]:
    observed = audit_assets()
    complete = (
        observed["vendor_sdk_root_present"]
        and observed["release_id_known"]
        and observed["vendor_sdk_file_count"] > 0
        and observed["model_bundle_dir_present"]
        and observed["model_bundle_file_count"] > 0
        and observed["license_record_present"]
        and observed["entitlement_record_present"]
        and observed["consent_record_present"]
        and observed["direction_map_present"]
        and observed["cohort_manifest_present"]
        and observed["target_reference_present"]
        and observed["runtime_env_present"]
        and observed["runtime_lock_present"])
    if complete:
        result = "asset_set_complete_pending_parity"
    elif observed["vendor_sdk_root_present"] or observed[
            "model_bundle_dir_present"]:
        result = "artifacts_present_unqualified"
    else:
        result = "absent"
    return {
        "qualified": False,
        "audit_result": result,
        "vendor_sdk_present": observed["vendor_sdk_root_present"],
        "vendor_sdk_file_count": observed["vendor_sdk_file_count"],
        "model_bundle_present": observed["model_bundle_dir_present"],
        "model_bundle_file_count": observed["model_bundle_file_count"],
        "release_id_known": observed["release_id_known"],
        "license_present": observed["license_record_present"],
        "entitlement_present": observed["entitlement_record_present"],
        "consent_present": observed["consent_record_present"],
        "direction_map_present": observed["direction_map_present"],
        "cohort_manifest_present": observed["cohort_manifest_present"],
        "target_reference_present": observed["target_reference_present"],
        "runtime_env_present": observed["runtime_env_present"],
        "runtime_lock_present": observed["runtime_lock_present"],
        "research_demo_audio_clip_count": observed[
            "research_demo_audio_clip_count"],
        "observed": observed,
        "note": (
            "A vendor package, model bundle or entitlement appearing does not "
            "publish an approved release, a digest, terms, a rights record, a "
            "direction map, a cohort or a parity vector.  Presence never "
            "qualifies the candidate."),
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
        "mode": MODE,
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
                "No licensed Krisp Accent Conversion SDK package, vendor "
                "release identity, model bundle digest, entitlement, terms "
                "record, hash-pinned runtime, accent-direction map, "
                "rights-cleared cohort, target reference or approved parity "
                "vector exists.  The merged research package inspected vendor "
                "documentation only and never ran the model."),
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
        "vendor_record": {
            "vendor": VENDOR_NAME,
            "documentation_url": VENDOR_DOC_URL,
            "device_sdk_url": VENDOR_DEVICE_URL,
            "release_id": VENDOR_RELEASE_ID,
            "release_id_approved": False,
            "source_available": False,
            "model_available": False,
            "entitlement_available": False,
            "proprietary": True,
            "adapter_prototyped": False,
        },
        "asset_requirements": [dict(item) for item in ASSET_REQUIREMENTS],
        "asset_audit": audit,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "voice_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS[
                "audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "applicable_outcome": (
                "accent-converted 16 kHz mono speech with separate text/semantic, "
                "identity/similarity and naturalness outcomes"),
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [
                item["id"] for item in profile_items],
            "real_model_metrics": None,
            "note": (
                "Structural accounting passes, but no licensed runtime, "
                "entitlement, terms record, consent record, direction map, "
                "rights-cleared cohort, target reference or approved parity "
                "exists, so the voice profile is not satisfied for "
                "qualification."),
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_control_not_streaming_claim": True,
            "vendor_direction_names_not_invented": True,
            "vendor_sdk_not_linked": True,
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
            VENDOR_SDK_ROOT_PATH + "/",
            MODEL_BUNDLE_PATH + "/",
            RUNTIME_LOCK_PATH,
            LICENSE_RECORD_PATH,
            ENTITLEMENT_RECORD_PATH,
            CONSENT_RECORD_PATH,
            DIRECTION_MAP_PATH,
            COHORT_MANIFEST_PATH,
            TARGET_REFERENCE_PATH,
        ],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no vendor SDK, model or audio runtime is imported.",
            "All asset observations use fixed workspace paths and local reads.",
            "No network request, download, token exchange, audio device, model load or timing run occurs.",
            "The synthetic direction set is an explicit placeholder, not vendor accent names.",
        ],
        "determinism": {
            "canonical_json": (
                "sort_keys=True, compact separators, allow_nan=False, "
                "trailing newline"),
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
    }
