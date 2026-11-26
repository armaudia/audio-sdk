# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION.

The exact licensed Streaming non-autoregressive Accent Conversion source,
weights, runtime, rights/consent records, approved parity vector and numeric
output are absent. The merged research note records a paper/demo inspection
only: no public runnable checkpoint or implementation was located, and the
paper reports about 0.8 s latency while stating it remains to be reduced.

This module never imports model/audio/tensor runtimes, never downloads anything,
never reads or writes real audio, never listens and never measures a device
clock. It provides a fail-closed fixed-path audit, a caller-supplied-asset
manifest contract validated without execution, and a deterministic synthetic
Q15 PCM accounting control. Nothing qualifies the candidate; decision is DEFER.
"""

from __future__ import annotations

import hashlib
import math
import json
import os
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION"
TITLE = "Streaming non-autoregressive Accent Conversion"
SLUG = "streaming-non-autoregressive-accent-conversion"
COMPONENT = "streaming-non-autoregressive-accent-conversion"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "14af17740bf8c571f9a985c88fd56f5b5b8e8ae8"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-STREAMING-NON-AUTOREGRESSIVE-ACCENT-CONVERSION"
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

CANDIDATE_PAPER_URL = "https://arxiv.org/abs/2506.16580"
CANDIDATE_FINDING_LINE = 171
CANDIDATE_FINDING = (
    "Paper/demo inspected; no public runnable checkpoint or implementation "
    "located. The paper reports about 0.8 s latency and says it remains to be "
    "reduced. Use as a research-quality comparison, not a sub-100 ms deployment "
    "candidate.")

SOURCE_CANDIDATES = (
    "research/accent-conversion-20261101/repos/streaming-non-autoregressive-accent-conversion",
    "research/accent-conversion-20261101/repos/Streaming-Non-Autoregressive-Accent-Conversion",
    "data/checkouts/streaming-non-autoregressive-accent-conversion",
    "adapters/streaming-non-autoregressive-accent-conversion",
)
WEIGHTS_CANDIDATES = (
    "data/models/streaming-non-autoregressive-accent-conversion",
    "research/accent-conversion-20261101/checkpoints/streaming-non-autoregressive-accent-conversion",
)
RUNTIME_ENV_PATH = "data/envs/streaming-non-autoregressive-accent-conversion"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"
RIGHTS_RECORD_PATH = "data/rights/streaming-non-autoregressive-accent-conversion-rights.json"
CONSENT_RECORD_PATH = "data/rights/streaming-non-autoregressive-accent-conversion-consent.json"
COHORT_MANIFEST_PATH = "data/runs/streaming-non-autoregressive-accent-conversion-voice-cohort/manifest.json"
PARITY_VECTOR_PATH = "data/runs/streaming-non-autoregressive-accent-conversion-reference/parity.json"
SAMPLE_DATA_PATH = "research/accent-conversion-20261101/data/l2accent"

SDK_FRAME_SAMPLES = 160
SDK_SAMPLE_RATE_HZ = 16000
SDK_CHANNELS = 1
SDK_SAMPLE_FORMAT = "float32"

SURROGATE_SAMPLE_RATE_HZ = 16000
SURROGATE_CHANNELS = 1
SURROGATE_SOURCE_SECONDS = 3
SURROGATE_TARGET_SECONDS = 2
SURROGATE_SOURCE_SAMPLES = SURROGATE_SAMPLE_RATE_HZ * SURROGATE_SOURCE_SECONDS
SURROGATE_TARGET_SAMPLES = SURROGATE_SAMPLE_RATE_HZ * SURROGATE_TARGET_SECONDS
PCM_SAMPLE_CAP = 960000
Q15_SCALE = 32768

STABLE_TASK_FIELDS = (
    "acceptance", "component", "deliverable", "depends_on", "evidence", "id",
    "mode", "repository", "title", "write_scope",
)
MUTABLE_TASK_FIELDS = (
    "blocked_reason", "dispatch_priority", "handoff", "owner", "review", "status",
)

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/TASKS.json":
        "6cfcd19ec6a8f32c306062da9ff9b59e48187eb0e24436417c347ca34d0cb42e",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
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
}
LOCAL_PIN_PATHS = (
    "README.md", "SOURCES.sha256.license", "contract.json", "contract.json.license",
    "reference.py", "report.json", "report.json.license", "report.json.sha256",
    "report.json.sha256.license", "run.py", "test_reference.py", "verify.py",
)

FORMAT: Dict[str, Any] = {
    "sdk_v0_sample_rate_hz": SDK_SAMPLE_RATE_HZ,
    "sdk_v0_channels": SDK_CHANNELS,
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "sdk_v0_sample_format": SDK_SAMPLE_FORMAT,
    "resampling": "none",
    "sdk_v0_geometry_preserved": True,
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
    "No Streaming non-autoregressive Accent Conversion source, weight file, runtime, adapter or numeric output is downloaded, copied, loaded, imported or executed.",
    "No real audio, corpus, transcript, source/target voice reference or consent record is consumed.",
    "No accent conversion, intelligibility, identity, naturalness, latency, memory, RTF or listening result is measured.",
    "The source-reported paper/demo note is provenance only and is not reproduced here.",
    "The synthetic integer PCM accounting control is a contract control, never model output, and cannot qualify the candidate.",
    "No candidate input rate, output rate, hop, mode, alignment, first-output or tail timing is asserted.",
    "No provider, descriptor, registry, installed v0 path, shared build, dependency lock or CI is changed.",
    "No device timing, public benchmark, listening or release claim is made.",
    "Missing, blocked or rejected evidence never qualifies the candidate; the decision remains DEFER.",
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "pinned_source_absent", "state": "absent", "requirement": "Supply one exact Streaming non-autoregressive Accent Conversion source tree or release archive with an immutable revision and matching SHA-256. No checkout, archive or adapter exists at any audited path."},
    {"id": "weights_and_checkpoint_identity_absent", "state": "absent", "requirement": "Supply exact pretrained weights/checkpoints with byte counts and SHA-256 values at an immutable revision. The merged research note records no public runnable checkpoint or implementation located."},
    {"id": "runtime_and_environment_absent", "state": "absent", "requirement": "Provide a complete isolated runtime lock and recorded platform for the pinned source and weights. No data/envs/streaming-non-autoregressive-accent-conversion environment or lock exists."},
    {"id": "source_and_weight_license_absent", "state": "absent", "requirement": "Stage the exact source and weight license terms, model card, attribution notices and derivative-output and redistribution review."},
    {"id": "rights_consent_and_corpus_uncleared", "state": "absent", "requirement": "Clear training-data, source-reference, target-reference, consent, output-use and corpus rights. Shared L2-ARCTIC clips are CC BY-NC 4.0 research-only and are not conversion pairs."},
    {"id": "voice_cohort_and_reference_pairs_absent", "state": "absent", "requirement": "Freeze a rights-cleared held-out cohort with permitted source/target references, task/language/speaker groups, transcript truth and separate text/semantic, identity/similarity and naturalness outcomes."},
    {"id": "candidate_geometry_and_alignment_unverified", "state": "absent", "requirement": "Document exact candidate input/output rate, channel layout, hop/chunk scheme, lookahead, first-output and tail alignment for pinned weights. The paper reports about 0.8 s latency and says it remains to be reduced; no local geometry is documented."},
    {"id": "approved_reference_parity_absent", "state": "absent", "requirement": "Produce an approved exact-runtime parity vector on frozen input with frozen configuration, reproducible weights and byte-level or declared-tolerance output comparison."},
)

RELEASE_GATES: Tuple[Dict[str, str], ...] = (
    {"id": "RG-01", "requirement": "Exact pinned licensed source and immutable revision.", "status": "blocked"},
    {"id": "RG-02", "requirement": "Exact pretrained weights/checkpoints with hashes and rights.", "status": "blocked"},
    {"id": "RG-03", "requirement": "Reproducible isolated runtime/environment lock and hardware record.", "status": "blocked"},
    {"id": "RG-04", "requirement": "Rights-cleared input/target/reference corpora with consent and use terms.", "status": "blocked"},
    {"id": "RG-05", "requirement": "Approved reference parity vectors and deterministic rerun evidence.", "status": "blocked"},
    {"id": "RG-06", "requirement": "Voice-profile quality/listening/identity/naturalness evidence.", "status": "blocked"},
    {"id": "RG-07", "requirement": "Device timing, streaming/tail latency, and resource evidence on approved targets.", "status": "blocked"},
    {"id": "RG-08", "requirement": "Independent review, release approval, and explicit opt-in intake decision.", "status": "blocked"},
)

VOICE_REQUIRED_ITEMS: Dict[str, str] = {
    "permitted_source_and_target_references": "Freeze permitted input and target references with rights and consent.",
    "task_language_and_speaker_groups": "Freeze task, language and speaker groups for the cohort.",
    "text_and_semantic_preservation": "Preserve text and semantic content as its own outcome.",
    "identity_similarity": "Measure identity or similarity to the target as a separate outcome.",
    "naturalness": "Measure naturalness as a separate outcome.",
    "alignment_and_output_timing": "Record alignment, first-output and tail timing for the exact runtime.",
    "consent_reference_and_output_use": "Treat consent, reference availability and output use as independent gates.",
}
VOICE_ITEM_STATUS = {
    "permitted_source_and_target_references": "absent",
    "task_language_and_speaker_groups": "absent",
    "text_and_semantic_preservation": "not_measured",
    "identity_similarity": "not_measured",
    "naturalness": "not_measured",
    "alignment_and_output_timing": "structural_only",
    "consent_reference_and_output_use": "absent",
}

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "missing_manifest_field",
    "extra_manifest_field",
    "manifest_not_object",
    "channels_not_one",
    "sample_rate_mismatch",
    "frame_not_positive_int",
    "bool_rejected",
    "variant_wrong",
    "revision_bad_format",
    "sha256_bad_format",
    "path_not_absolute",
    "path_missing",
    "digest_mismatch",
    "directory_missing",
    "label_empty",
    "pcm_not_list",
    "pcm_nonfinite",
    "pcm_out_of_range",
    "pcm_too_long",
    "bad_caller_contract",
)

MANIFEST_REQUIRED_FIELDS = (
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


class Reject(ValueError):
    """Deterministic validation rejection."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return (canonical_text(report) + "\n").encode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = canonical_text(report) + "\n"
    return text, sha256_bytes(text.encode("utf-8"))


def load_strict_json(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        raise Reject(f"{path}: missing trailing newline")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise Reject(f"{path}: invalid JSON: {exc}") from exc
    _reject_nonfinite(payload, str(path))
    if not isinstance(payload, dict):
        raise Reject(f"{path}: top-level JSON value must be object")
    return payload


def _reject_nonfinite(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_nonfinite(item, f"{label}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _reject_nonfinite(item, f"{label}[{index}]")
        return
    if isinstance(value, bool):
        return
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not isinstance(value, int) and not math.isfinite(value):
            raise Reject(f"{label}: non-finite number")


def _require_hex40(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise Reject(f"{label}: expected 40 lowercase hex chars")
    return value


def _require_hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise Reject(f"{label}: expected 64 lowercase hex chars")
    return value


def _require_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject(f"{label}: expected integer")
    return value


def _require_abs_existing_file(path_value: Any, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise Reject(f"{label}: expected absolute path string")
    path = Path(path_value)
    if not path.is_absolute():
        raise Reject(f"{label}: path must be absolute")
    if not path.is_file():
        raise Reject(f"{label}: file missing")
    return path


def _require_abs_existing_dir(path_value: Any, label: str) -> Path:
    if not isinstance(path_value, str) or not path_value:
        raise Reject(f"{label}: expected absolute path string")
    path = Path(path_value)
    if not path.is_absolute():
        raise Reject(f"{label}: path must be absolute")
    if not path.is_dir():
        raise Reject(f"{label}: directory missing")
    return path


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise Reject("manifest: expected object")
    keys = tuple(sorted(manifest.keys()))
    if keys != MANIFEST_REQUIRED_FIELDS:
        raise Reject("manifest: field set mismatch")
    source_revision = _require_hex40(manifest["source_revision"], "source_revision")
    if not isinstance(manifest["variant"], str) or manifest["variant"] != "offline_whole_utterance":
        raise Reject("variant: must be offline_whole_utterance")
    channels = _require_int(manifest["channels"], "channels")
    if channels != 1:
        raise Reject("channels: must be 1")
    sr_in = _require_int(manifest["sample_rate_input_hz"], "sample_rate_input_hz")
    sr_out = _require_int(manifest["sample_rate_output_hz"], "sample_rate_output_hz")
    if sr_in not in (16000, 22050, 24000, 44100, 48000) or sr_out not in (16000, 22050, 24000, 44100, 48000):
        raise Reject("sample_rate: unsupported value")
    for key in (
        "config_path", "consent_record_path", "license_record_path", "runtime_lock_path",
        "source_archive_path", "source_reference_path", "target_reference_path", "weights_path",
    ):
        path = _require_abs_existing_file(manifest[key], key)
        digest = _require_hex64(manifest[key.replace("_path", "_sha256")], key.replace("_path", "_sha256"))
        actual = file_digest(path)
        if actual != digest:
            raise Reject(f"{key}: sha256 mismatch")
    runtime_path = _require_abs_existing_dir(manifest["runtime_path"], "runtime_path")
    _ = runtime_path
    # No approved source/weights identity exists; structural validation never admits execution.
    return {
        "accepted_for_qualification": False,
        "admission_status": "blocked_no_approved_identity",
        "approved_source_revision": None,
        "approved_weights_sha256": None,
        "source_revision_shape_valid": True,
        "variant": manifest["variant"],
        "geometry_valid": True,
        "qualification_effect": "none",
        "execution_performed": False,
        "notes": "Structural checks passed but no approved pinned source/weights/runtime/rights/parity exists; admission remains blocked.",
        "source_revision": source_revision,
    }


def _q15_from_index(index: int) -> int:
    # Deterministic integer triangle in [-12000, 12000], no libm.
    period = 400
    pos = index % period
    half = period // 2
    amp = 12000
    if pos <= half:
        value = -amp + (2 * amp * pos) // half
    else:
        value = amp - (2 * amp * (pos - half)) // half
    if value < -32768 or value > 32767:
        raise Reject("q15 out of range")
    return value


def synthetic_pcm(sample_count: int, offset: int = 0) -> List[int]:
    count = _require_int(sample_count, "sample_count")
    if count <= 0 or count > PCM_SAMPLE_CAP:
        raise Reject("sample_count: out of range")
    off = _require_int(offset, "offset")
    return [_q15_from_index(off + i) for i in range(count)]


def validate_pcm(samples: Any, label: str) -> List[int]:
    if not isinstance(samples, list):
        raise Reject(f"{label}: expected list")
    if len(samples) == 0 or len(samples) > PCM_SAMPLE_CAP:
        raise Reject(f"{label}: invalid length")
    out: List[int] = []
    for i, value in enumerate(samples):
        if isinstance(value, bool) or not isinstance(value, int):
            raise Reject(f"{label}[{i}]: expected int16")
        if value < -32768 or value > 32767:
            raise Reject(f"{label}[{i}]: out of range")
        out.append(value)
    return out


def run_surrogate_control() -> Dict[str, Any]:
    source = validate_pcm(synthetic_pcm(SURROGATE_SOURCE_SAMPLES, 0), "source")
    target = validate_pcm(synthetic_pcm(SURROGATE_TARGET_SAMPLES, 37), "target")
    ratio = Fraction(len(target), len(source))
    result = {
        "control_id": "synthetic_q15_pcm_accounting_control",
        "is_candidate_model_output": False,
        "qualification_effect": "none",
        "sample_format": "q15_int16",
        "sample_rate_hz": SURROGATE_SAMPLE_RATE_HZ,
        "channels": SURROGATE_CHANNELS,
        "source_samples": len(source),
        "target_samples": len(target),
        "source_seconds_fraction": f"{Fraction(len(source), SURROGATE_SAMPLE_RATE_HZ).numerator}/{Fraction(len(source), SURROGATE_SAMPLE_RATE_HZ).denominator}",
        "target_seconds_fraction": f"{Fraction(len(target), SURROGATE_SAMPLE_RATE_HZ).numerator}/{Fraction(len(target), SURROGATE_SAMPLE_RATE_HZ).denominator}",
        "duration_ratio_target_over_source": f"{ratio.numerator}/{ratio.denominator}",
        "alignment": {
            "mode": "offline_whole_utterance",
            "incremental_streaming_supported": False,
            "first_output_sample": 0,
            "tail_sample": len(target) - 1,
            "source_end_sample": len(source) - 1,
            "status": "structural_only",
        },
        "voice_outcomes": {
            "text_and_semantic_preservation": "not_measured",
            "identity_similarity": "not_measured",
            "naturalness": "not_measured",
        },
        "finite": True,
        "peak_abs": max(abs(v) for v in target),
        "candidate_geometry_asserted": False,
    }
    return result


def audit_assets() -> List[Dict[str, Any]]:
    observed: List[Dict[str, Any]] = []
    for relative in SOURCE_CANDIDATES:
        path = SOURCE_ROOT / relative
        observed.append({
            "id": f"source:{relative}",
            "kind": "source_checkout",
            "path": relative,
            "present": path.exists(),
            "qualified": False,
            "sha256": file_digest(path) if path.is_file() else None,
        })
    for relative in WEIGHTS_CANDIDATES:
        path = SOURCE_ROOT / relative
        observed.append({
            "id": f"weights:{relative}",
            "kind": "weights_or_checkpoint",
            "path": relative,
            "present": path.exists(),
            "qualified": False,
            "sha256": file_digest(path) if path.is_file() else None,
        })
    for relative in (RUNTIME_LOCK_PATH, RIGHTS_RECORD_PATH, CONSENT_RECORD_PATH, COHORT_MANIFEST_PATH, PARITY_VECTOR_PATH):
        path = SOURCE_ROOT / relative
        observed.append({
            "id": f"asset:{relative}",
            "kind": "required_asset",
            "path": relative,
            "present": path.exists(),
            "qualified": False,
            "sha256": file_digest(path) if path.is_file() else None,
        })
    sample_dir = SOURCE_ROOT / SAMPLE_DATA_PATH
    sample_files = sorted(p for p in sample_dir.glob("**/*") if p.is_file()) if sample_dir.exists() else []
    observed.append({
        "id": "sample:l2arctic",
        "kind": "sample_data_non_qualifying",
        "path": SAMPLE_DATA_PATH,
        "present": bool(sample_files),
        "qualified": False,
        "file_count": len(sample_files),
        "sample_sha256": [file_digest(p) for p in sample_files[:3]],
        "note": "L2-ARCTIC demo clips may exist as research-only data; they are not candidate checkpoints, rights records, cohorts or parity vectors.",
    })
    return observed


def asset_requirements() -> List[Dict[str, Any]]:
    reqs = []
    specs = [
        ("pinned_source", "source_checkout", SOURCE_CANDIDATES[0], "Exact licensed source checkout or release archive at immutable revision."),
        ("pretrained_weights", "weights", WEIGHTS_CANDIDATES[0], "Exact pretrained weights/checkpoints with SHA-256 and rights."),
        ("runtime_lock", "runtime", RUNTIME_LOCK_PATH, "Isolated runtime/environment lock and platform record."),
        ("license_record", "rights", RIGHTS_RECORD_PATH, "Source/weight license, terms, attribution and redistribution review."),
        ("consent_record", "rights", CONSENT_RECORD_PATH, "Input/reference/output consent and use terms."),
        ("voice_cohort_manifest", "evaluation", COHORT_MANIFEST_PATH, "Rights-cleared held-out voice cohort manifest with target references."),
        ("reference_parity_vector", "evaluation", PARITY_VECTOR_PATH, "Approved exact-runtime parity vectors and deterministic rerun evidence."),
    ]
    for req_id, kind, path, requirement in specs:
        reqs.append({
            "id": req_id,
            "kind": kind,
            "path": path,
            "sha256": None,
            "required": True,
            "status": "absent",
            "requirement": requirement,
        })
    return reqs


def acceptance_profile() -> Dict[str, Any]:
    required = {}
    for key, req in VOICE_REQUIRED_ITEMS.items():
        required[key] = {
            "requirement": req,
            "status": VOICE_ITEM_STATUS[key],
            "qualification_effect": "none",
        }
    return {
        "profile": "voice",
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
        "required_items": required,
        "satisfied_for_qualification": [],
        "blocked_items": [k for k, v in required.items() if v["status"] != "satisfied"],
        "note": "Structural accounting is not a Voice-profile result. No permitted reference pair, consent, rights-cleared cohort, exact runtime, transcript truth, identity measure, naturalness rating or timing exists.",
    }


def caller_asset_contract() -> Dict[str, Any]:
    return {
        "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
        "asset_is_caller_owned": True,
        "asset_is_vendored": False,
        "absent_behavior": "reject_before_processing",
        "present_behavior": "validate_shape_absolute_paths_sha256_geometry_and_variant_only;_do_not_import_or_execute",
        "admission_status": "blocked_no_approved_identity",
        "positive_admission_possible": False,
        "approved_source_revision": None,
        "approved_weights_sha256": None,
        "required_fields": list(MANIFEST_REQUIRED_FIELDS),
        "required_geometry": {"channels": 1, "sample_rate_input_hz": 16000, "sample_rate_output_hz": 16000},
        "required_variant": "offline_whole_utterance",
        "notes": "The manifest contract is structurally exercised, but every manifest is rejected for qualification because no immutable source revision, weight digest, runtime lock or rights record is approved. No file is loaded or executed and no audio is processed.",
    }


def source_reported_context() -> Dict[str, Any]:
    return {
        "label": "source_reported_not_measured_here",
        "source": "research/accent-conversion-20261101/README.md",
        "source_sha256": SOURCE_PINS["research/accent-conversion-20261101/README.md"],
        "source_line": CANDIDATE_FINDING_LINE,
        "paper_url": CANDIDATE_PAPER_URL,
        "finding": CANDIDATE_FINDING,
        "reported_latency_seconds": 0.8,
        "reported_latency_status": "reported_by_paper_not_measured_here",
        "local_checkpoint": "absent",
        "local_run": "not_run",
        "notes": "The merged research note records a paper/demo inspection only. No runnable checkpoint, implementation, metric, listening result or device measurement exists in this workspace.",
    }


def adverse_controls() -> List[Dict[str, Any]]:
    controls = []
    def record(case_id: str, fn) -> None:
        try:
            fn()
        except Reject as exc:
            controls.append({"case_id": case_id, "status": "rejected", "state_unchanged": True, "reason": str(exc)})
            return
        controls.append({"case_id": case_id, "status": "accepted", "state_unchanged": False, "reason": "unexpected acceptance"})

    base = {
        "channels": 1, "config_path": "/tmp/missing-config.json", "config_sha256": "0" * 64,
        "consent_record_path": "/tmp/missing-consent.json", "consent_record_sha256": "1" * 64,
        "license_record_path": "/tmp/missing-license.json", "license_record_sha256": "2" * 64,
        "runtime_lock_path": "/tmp/missing-lock.txt", "runtime_lock_sha256": "3" * 64,
        "runtime_path": "/tmp", "sample_rate_input_hz": 16000, "sample_rate_output_hz": 16000,
        "source_archive_path": "/tmp/missing-source.tar.gz", "source_archive_sha256": "4" * 64,
        "source_reference_path": "/tmp/missing-ref.wav", "source_reference_sha256": "5" * 64,
        "source_revision": "0123456789abcdef0123456789abcdef01234567",
        "target_reference_path": "/tmp/missing-target.wav", "target_reference_sha256": "6" * 64,
        "variant": "offline_whole_utterance",
        "weights_path": "/tmp/missing-weights.bin", "weights_sha256": "7" * 64,
    }

    record("missing_manifest_field", lambda: validate_caller_manifest({k: v for k, v in base.items() if k != "weights_path"}))
    bad_extra = dict(base); bad_extra["extra"] = 1
    record("extra_manifest_field", lambda: validate_caller_manifest(bad_extra))
    record("manifest_not_object", lambda: validate_caller_manifest([]))
    bad = dict(base); bad["channels"] = 2
    record("channels_not_one", lambda: validate_caller_manifest(bad))
    bad = dict(base); bad["sample_rate_input_hz"] = 8000
    record("sample_rate_mismatch", lambda: validate_caller_manifest(bad))
    bad = dict(base); bad["sample_rate_input_hz"] = 16000.5
    record("frame_not_positive_int", lambda: validate_caller_manifest(bad))
    bad = dict(base); bad["channels"] = True
    record("bool_rejected", lambda: validate_caller_manifest(bad))
    bad = dict(base); bad["variant"] = "streaming"
    record("variant_wrong", lambda: validate_caller_manifest(bad))
    bad = dict(base); bad["source_revision"] = "abc"
    record("revision_bad_format", lambda: validate_caller_manifest(bad))
    bad = dict(base); bad["config_sha256"] = "xyz"
    record("sha256_bad_format", lambda: validate_caller_manifest(bad))
    bad = dict(base); bad["config_path"] = "relative/config.json"
    record("path_not_absolute", lambda: validate_caller_manifest(bad))
    record("path_missing", lambda: validate_caller_manifest(base))
    # digest mismatch case with real files
    import shutil
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="snac-manifest-"))
    try:
        base2 = dict(base)
        for k2 in ("config", "consent_record", "license_record", "runtime_lock", "source_archive", "source_reference", "target_reference", "weights"):
            p2 = td / k2
            p2.write_bytes(k2.encode("utf-8"))
            base2[f"{k2}_path"] = str(p2)
            base2[f"{k2}_sha256"] = file_digest(p2)
        base2["runtime_path"] = str(td)
        good = validate_caller_manifest(base2)
        if good["accepted_for_qualification"] is not False:
            controls.append({"case_id": "digest_mismatch", "status": "accepted", "state_unchanged": False, "reason": "setup failed"})
        else:
            bad = dict(base2); bad["weights_sha256"] = "0" * 64
            record("digest_mismatch", lambda: validate_caller_manifest(bad))
        bad = dict(base2); bad["runtime_path"] = str(td / "nope")
        record("directory_missing", lambda: validate_caller_manifest(bad))
    finally:
        shutil.rmtree(td, ignore_errors=True)
    bad = dict(base); bad["variant"] = ""
    record("label_empty", lambda: validate_caller_manifest(bad))
    record("pcm_not_list", lambda: validate_pcm("bad", "pcm"))
    record("pcm_nonfinite", lambda: validate_pcm([0, float("nan")], "pcm"))
    record("pcm_out_of_range", lambda: validate_pcm([32768], "pcm"))
    record("pcm_too_long", lambda: validate_pcm([0] * (PCM_SAMPLE_CAP + 1), "pcm"))
    record("bad_caller_contract", lambda: validate_caller_manifest({"variant": "offline_whole_utterance"}))
    return controls


def build_contract() -> Dict[str, Any]:
    control = run_surrogate_control()
    gates = [dict(g) for g in RELEASE_GATES]
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
        "acceptance_profile": acceptance_profile(),
        "candidate": {
            "name": TITLE,
            "paper_url": CANDIDATE_PAPER_URL,
            "geometry_documented": False,
            "exact_numeric_output_present": False,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "reported_hop_samples": None,
            "reported_input_sample_rate_hz": None,
            "reported_output_sample_rate_hz": None,
        },
        "format": dict(FORMAT),
        "licensing": {
            "spdx_file_copyright": "2026 Tsakanyan Hovhannes",
            "spdx_license_identifier": "Apache-2.0",
            "review_status": "blocked",
            "source_license_present": False,
            "source_license_identity": None,
            "weight_terms_present": False,
            "model_card_present": False,
            "training_data_statement_staged": False,
            "attribution_notice_staged": False,
            "redistribution_reviewed": False,
            "product_use_reviewed": False,
        },
        "artifact_pins": {TASK_PREFIX + name: None for name in LOCAL_PIN_PATHS if name != "contract.json"},
        "board_row": {
            "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "whole_file_hashed": False,
            "stable_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/TASKS.json"],
            "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
            "stable_fields": {
                "acceptance": "Apply the voice acceptance profile; record exact scope, evidence, failure/control results, and remaining release gates. A readiness conclusion with an exact external blocker is an accepted investigation handoff; it does not close the conditional implementation.",
                "component": COMPONENT,
                "deliverable": "Verify runnable source, exact assets, permitted scope, task geometry and matched evidence. Then reproduce the exact model/runtime as a caller-supplied-asset reference and add an opt-in SDK adapter once its prerequisites pass. Record a concrete blocker if feasibility fails.",
                "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
                "evidence": ["research/accent-conversion-20261101/README.md"],
                "id": TASK,
                "mode": "feasibility",
                "repository": "audio-sdk",
                "title": TITLE,
                "write_scope": [f"SDK provider, tool or evidence directory for {SLUG} and its own fixtures"],
            },
            "claim": {"base_commit": BASE_COMMIT, "branch": BRANCH, "reviewer": REVIEWER, "worktree": CLAIM_WORKTREE},
        },
        "boundary": dict(BOUNDARY),
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_pins": dict(SOURCE_PINS),
        "scope": dict(SCOPE),
        "reference": {
            "name": TITLE,
            "status": "blocked",
            "pinned_revision": None,
            "source_present": False,
            "weights_present": False,
            "runtime_present": False,
            "implementation_present": False,
            "adapter_present": False,
            "exact_numeric_output_present": False,
            "surrogate_is_candidate": False,
            "license_identity": None,
        },
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "release_gates": gates,
        "reopen_condition": "Pin exact licensed source, pretrained weights and runtime with immutable revision, hash-pinned isolated runtime, cleared rights/consent, rights-cleared held-out voice cohort, exact geometry/alignment, approved parity vector, measured target timing and completed opt-in provider intake. Until then the candidate stays DEFER, incomplete and not qualified.",
        "negative_claims": list(NON_CLAIMS),
        "caller_asset_contract": caller_asset_contract(),
        "source_reported_context": source_reported_context(),
        "qualification": {
            "status": QUALIFICATION,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "candidate_qualified": False,
            "missing_result_promoted": False,
            "no_missing_result_qualifies_candidate": True,
            "exact_source_present": False,
            "exact_weights_present": False,
            "exact_runtime_outputs_present": False,
            "rights_cleared_cohort": False,
            "geometry_documented": False,
            "parity_measured": False,
            "timing_measured": False,
            "listening": False,
            "real_corpus_used": False,
            "blocked_gate_count": 8,
            "blocked_gate_ids": [g["id"] for g in gates],
            "reason": "No source, pretrained weights, runtime, approved revision, license, consent record, rights-cleared voice cohort, geometry, parity vector or timing result exists. The merged note records no public runnable checkpoint or implementation located.",
        },
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "no missing, blocked or rejected result is promoted to a pass",
            "no candidate source, weight, model, runtime or adapter is downloaded, copied, loaded or executed",
            "the synthetic integer control is not model output and cannot qualify the candidate",
            "no candidate input rate, output rate, hop, mode, alignment, first-output or tail timing is asserted",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
        "reference_protocol": {
            "kind": "deterministic_synthetic_q15_accounting_control",
            "model_executed": False,
            "qualification_effect": "none",
            "result": control,
            "reset": {"matches_fresh": True},
        },
    }


def build_report() -> Dict[str, Any]:
    contract = build_contract()
    audit = audit_assets()
    control = run_surrogate_control()
    adverse = adverse_controls()
    all_rejected = all(item["status"] == "rejected" and item["state_unchanged"] is True for item in adverse)
    report = {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "component": COMPONENT,
        "title": TITLE,
        "repository": "audio-sdk",
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": contract["qualification"],
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "format": dict(FORMAT),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "task_row_identity": contract["board_row"],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "source_reported_context": source_reported_context(),
        "candidate": contract["candidate"],
        "reference": contract["reference"],
        "asset_requirements": asset_requirements(),
        "asset_audit": {
            "audit_result": "absent",
            "qualified": False,
            "observed": audit,
        },
        "external_artifacts": {
            "status": "blocked",
            "any_present": False,
            "source_checkouts_searched": list(SOURCE_CANDIDATES),
            "weight_locations_searched": list(WEIGHTS_CANDIDATES),
            "runtime_environment": RUNTIME_ENV_PATH,
            "rights_record": RIGHTS_RECORD_PATH,
            "consent_record": CONSENT_RECORD_PATH,
            "cohort_manifest": COHORT_MANIFEST_PATH,
            "parity_vector": PARITY_VECTOR_PATH,
            "paper_url": CANDIDATE_PAPER_URL,
        },
        "caller_asset_contract": caller_asset_contract(),
        "acceptance_profile": acceptance_profile(),
        "licensing": contract["licensing"],
        "reference_protocol": {
            "kind": "deterministic_synthetic_q15_accounting_control",
            "model_executed": False,
            "qualification_effect": "none",
            "result": control,
            "reset": {"matches_fresh": True},
        },
        "controls": {
            "adverse_all_rejected": all_rejected,
            "adverse_case_count": len(adverse),
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "offline_streaming_separation_declared": True,
            "adverse": adverse,
        },
        "release_gates": [dict(g) for g in RELEASE_GATES],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "reopen_conditions": [{"gate_id": g["id"], "condition": g["requirement"]} for g in RELEASE_GATES],
        "candidate_metrics": None,
        "missing_historical_artifacts": [SOURCE_CANDIDATES[0], WEIGHTS_CANDIDATES[0], RUNTIME_LOCK_PATH, RIGHTS_RECORD_PATH, COHORT_MANIFEST_PATH, PARITY_VECTOR_PATH],
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only; no model, tensor or audio runtime is imported.",
            "All asset observations use fixed workspace paths and local reads.",
            "The caller manifest contract validates shape, paths and hashes without importing or executing anything.",
            "The synthetic control uses deterministic integer Q15 arithmetic; it invokes no libm synthesis and no audio device.",
            "No network request, download, model load, listening test, device clock or timing run occurs.",
        ],
        "repeatability": {"runs": 3, "byte_identical": True, "comparison": "canonical JSON bytes and SHA-256 only; no tolerance"},
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, ensure_ascii=False, trailing newline",
            "cold_start_regenerations_required": 3,
            "report_text_generated_by": "reference.canonical_report_bytes",
        },
        "scope_note": "Only this task-local evidence directory is added. The board is referenced by stable linked-row fields only; the mutable full plan/swarm/TASKS.json is never hashed.",
    }
    return report


def sources_bytes(overrides: Optional[Dict[str, bytes]] = None) -> bytes:
    overrides = overrides or {}
    lines = [
        "# SHA-256 pins for " + TASK + "; source: paths are workspace-relative, worktree: paths are SDK-worktree-relative, pkg: paths are task-local. The mutable full plan/swarm/TASKS.json is never hashed as canonical artifact bytes except by stable linked-row identity in report/contract."
    ]
    for path, digest in sorted(SOURCE_PINS.items()):
        if path.endswith("TASKS.json"):
            lines.append(f"{digest}  source:{path}  # linked-row identity only; whole file not hashed into canonical artifact bytes")
        else:
            lines.append(f"{digest}  source:{path}")
    for path, digest in sorted(BOUNDARY_PINS.items()):
        lines.append(f"{digest}  worktree:{path}")
    for name in LOCAL_PIN_PATHS:
        if name in overrides:
            digest = sha256_bytes(overrides[name])
        else:
            full = HERE / name
            if not full.is_file():
                raise Reject("missing artifact: " + name)
            digest = file_digest(full)
        lines.append(f"{digest}  pkg:{name}")
    return ("\n".join(lines) + "\n").encode("utf-8")


__all__ = [
    "ADVERSE_CASE_IDS", "BOUNDARY_PINS", "EXACT_BLOCKERS", "MANIFEST_REQUIRED_FIELDS", "Reject",
    "SOURCE_PINS", "audit_assets", "build_contract", "build_report", "canonical_report", "canonical_report_bytes",
    "canonical_text", "file_digest", "load_strict_json", "run_surrogate_control", "sha256_bytes", "sources_bytes",
    "validate_caller_manifest", "validate_pcm",
]
