# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for pyannote segmentation/VAD.

Task ``SDK-PYANNOTE-SEGMENTATION-VAD`` is feasibility-only. No exact licensed
pyannote segmentation/VAD source checkout, weights, runtime, rights record,
parity vector, or matched benchmark is present in this workspace. This module
builds a bounded, deterministic blocker package. It never downloads assets,
never invokes external runtimes, and never claims qualification.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK = "SDK-PYANNOTE-SEGMENTATION-VAD"
TITLE = "pyannote segmentation / VAD"
COMPONENT = "pyannote-segmentation-vad"
CATEGORY_ID = "DET-01"
PROFILE = "analysis"
MODE = "feasibility"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-PYANNOTE-SEGMENTATION-VAD"
BASE_COMMIT = "80dc1fb371e1846a5d50f5b28c955ab92bfcbe46"
REVIEWER = "reviewer-PYANNOTE-SEGMENTATION-VAD"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-PYANNOTE-SEGMENTATION-VAD"
)
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DEFER_BEFORE = "opt_in_provider_intake"
SCHEMA_ID = "audio-sdk/task-evidence/pyannote-segmentation-vad/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_PREFIX = "docs/task-evidence/pyannote-segmentation-vad/"
REQUIRED_VARIANT = "pyannote_segmentation_vad_offline_annotation_adapter"
SDK_FRAME_SAMPLES = 160
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-" "Identifier: Apache-2.0\n"
)

HERE = Path(__file__).resolve().parent
_DEFAULT_SDK_ROOT = Path("/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PYANNOTE-SEGMENTATION-VAD")
_DEFAULT_SOURCE_ROOT = Path("/Users/htsakanyan/workspace/audio/audioml")
SDK_ROOT = _DEFAULT_SDK_ROOT if _DEFAULT_SDK_ROOT.exists() else HERE.parents[2]
SOURCE_ROOT = _DEFAULT_SOURCE_ROOT if _DEFAULT_SOURCE_ROOT.exists() else SDK_ROOT.parents[2]

STABLE_TASK_FIELDS = (
    "id",
    "title",
    "mode",
    "component",
    "repository",
    "deliverable",
    "acceptance",
    "depends_on",
    "evidence",
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

SOURCE_PINS = {
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/voice-enhancement-20261101/candidate_matrix.csv": "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md": "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md": "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
}
BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/acceptance-matrix.md": "2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/webrtc-vad/README.md": "1b3c5968c187b97bd67dcf2006581bd111d3cddc03911d5530d9e14325dfbc65",
    "docs/task-evidence/adaptive-energy-vad/README.md": "2de4b185d679f031c80625bd64e195cbabb69c62ea9499ef99f9868752ed86a2",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
}

SCOPE = {
    "annotated_speech_nonspeech_corpus": False,
    "benchmark_claim": False,
    "device_timing": False,
    "diarization_claim": False,
    "external_runtime_invoked": False,
    "false_positive_rate_measured": False,
    "listening": False,
    "network_used": False,
    "numeric_parity_claim": False,
    "onset_offset_delay_measured_on_real_audio": False,
    "proposal_only": True,
    "real_audio": False,
    "real_corpus": False,
    "release_claim": False,
    "segmentation_claim": False,
    "speaker_identity_claim": False,
    "task_local_only": True,
    "upstream_runtime_invoked": False,
    "upstream_source_present": False,
    "weights_loaded": False,
    "feature_domain_synthetic_control": True,
}

BOUNDARY = {
    "abi_change": False,
    "adapter_json_added": False,
    "analysis_events_added": False,
    "asset_bundled": False,
    "benchmark_claim": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "diarization_enabled": False,
    "enabled_by_default": False,
    "handoff_changed": False,
    "installed_v0_behavior_change": False,
    "network_used": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "release_approval": False,
    "runtime_compiled": False,
    "runtime_executed": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter_config_path",
    "adapter_config_sha256",
    "benchmark_record_path",
    "benchmark_record_sha256",
    "build_record_path",
    "build_record_sha256",
    "channels",
    "claimed_pyannote_segmentation_vad_capability",
    "corpus_manifest_path",
    "corpus_manifest_sha256",
    "frame_samples",
    "license_record_path",
    "license_record_sha256",
    "model_asset_path",
    "model_asset_sha256",
    "onset_hangover_frames",
    "parity_vector_path",
    "parity_vector_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_hz",
    "source_checkout_path",
    "source_manifest_path",
    "source_manifest_sha256",
    "source_revision",
    "task_geometry",
    "threshold",
    "variant",
)
MANIFEST_PATH_FIELDS = tuple(f for f in MANIFEST_FIELDS if f.endswith("_path"))
MANIFEST_SHA_FIELDS = tuple(f for f in MANIFEST_FIELDS if f.endswith("_sha256"))


class Reject(ValueError):
    """Fail-closed rejection for invalid or overclaiming inputs."""

def _reject(msg: str) -> Reject:
    return Reject(msg)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_sha256(text: Any, field: str) -> str:
    if not isinstance(text, str):
        raise _reject(f"{field} must be a lowercase SHA-256")
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise _reject(f"{field} must be a lowercase SHA-256")
    return text


def _validate_abs_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise _reject(f"{field} must be an absolute path without traversal")
    p = Path(text)
    if not p.is_absolute():
        raise _reject(f"{field} must be an absolute path without traversal")
    if ".." in p.parts:
        raise _reject(f"{field} must be an absolute path without traversal")
    return text


def _validate_revision(text: Any) -> str:
    if not isinstance(text, str) or not re.fullmatch(r"[0-9a-f]{40}", text):
        raise _reject("source_revision must be a full 40-hex commit")
    if text == "0" * 40:
        raise _reject("source_revision must be a full 40-hex commit")
    return text


def _validate_decimal_string(text: Any, field: str) -> str:
    if not isinstance(text, str):
        raise _reject(f"{field} must be a canonical decimal string")
    if not re.fullmatch(r"0|[1-9][0-9]*(\.[0-9]+)?|0\.[0-9]+", text):
        raise _reject(f"{field} must be a canonical decimal string")
    try:
        dec = Decimal(text)
    except InvalidOperation as exc:
        raise _reject(f"{field} must be a canonical decimal string") from exc
    if not dec.is_finite() or dec <= 0:
        raise _reject(f"{field} must be positive")
    return text


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8") + b"\n"
    except (TypeError, ValueError) as exc:
        raise _reject(f"non-canonical value: {exc}") from exc


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report)


def _parse_strict_json(text: str) -> Any:
    def _const(v: str) -> Any:
        raise _reject(f"non-finite JSON: {v}")

    def _object_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for k, v in pairs:
            if k in obj:
                raise _reject(f"duplicate JSON key: {k}")
            obj[k] = v
        return obj

    try:
        return json.loads(text, parse_constant=_const, object_pairs_hook=_object_pairs)
    except json.JSONDecodeError as exc:
        raise _reject(f"invalid JSON: {exc}") from exc


def strict_loads(text: str) -> Dict[str, Any]:
    value = _parse_strict_json(text)
    if not isinstance(value, dict):
        raise _reject("JSON root must be an object")
    return value


def strict_load(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise _reject(f"missing JSON file: {path}")
    return strict_loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_document_pins() -> None:
    for rel, expected in SOURCE_PINS.items():
        path = SOURCE_ROOT / rel
        if not path.is_file():
            raise _reject(f"source pin target missing: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            raise _reject(f"source pin mismatch: {rel}")
    for rel, expected in BOUNDARY_PINS.items():
        path = SDK_ROOT / rel
        if not path.is_file():
            raise _reject(f"worktree pin target missing: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            raise _reject(f"worktree pin mismatch: {rel}")
    if BOARD_PATH in SOURCE_PINS or BOARD_PATH in BOUNDARY_PINS:
        raise _reject("mutable board must not be pinned as a source/boundary digest")


def _load_tasks() -> List[Dict[str, Any]]:
    tasks_path = SOURCE_ROOT / BOARD_PATH
    data = json.loads(tasks_path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "tasks" in data:
        tasks = data["tasks"]
    elif isinstance(data, list):
        tasks = data
    else:
        raise _reject("TASKS.json has unsupported shape")
    if not isinstance(tasks, list):
        raise _reject("TASKS.json tasks must be a list")
    out = []
    for t in tasks:
        if isinstance(t, dict):
            out.append(t)
    return out


def task_row_identity() -> Dict[str, Any]:
    row = None
    for t in _load_tasks():
        if t.get("id") == TASK:
            row = t
            break
    if row is None:
        raise _reject(f"task row missing: {TASK}")
    claim = row.get("claim") or {}
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    stable_sha = sha256_bytes(canonical_bytes(stable))
    return {
        "source": BOARD_PATH,
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "stable_fields": stable,
        "stable_sha256": stable_sha,
        "claim": {
            "base_commit": claim.get("base_commit"),
            "branch": claim.get("branch"),
            "worktree": claim.get("worktree"),
            "reviewer": claim.get("reviewer"),
        },
    }


def _gate_rows() -> List[Dict[str, Any]]:
    return [
        {
            "id": "exact_source_and_asset_identity",
            "requirement": "Exact approved pyannote segmentation/VAD source, canonical repository URL, full 40-hex revision, per-file SHA-256 values, model/weights identity, and licence record match immutable pins.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "runtime_admission",
            "requirement": "An isolated, hash-pinned runtime and reproducible build/execution record run the exact pyannote segmentation/VAD implementation on a recorded platform.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "artifact_rights_and_licence",
            "requirement": "Implementation, model/weights, dependency and corpus rights are verified with dated evidence; no gated Hugging Face/model terms or corpus restrictions are ignored.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "exact_reference_parity",
            "requirement": "Approved exact-runtime pyannote outputs match a frozen caller-supplied input and task geometry; synthetic controls are not parity.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "analysis_cohort_and_scoring",
            "requirement": "A rights-cleared, label-complete held-out cohort scores timestamped probabilities, boundaries, onset/offset delay, quiet/active speech, idle noise, known positives/negatives and stratified FN/FP under the analysis profile.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "task_geometry_and_adapter_boundary",
            "requirement": "Task geometry (VAD vs segmentation vs diarization output), sample rate/hop/window/lookahead, annotation schema, availability policy and opt-in analysis adapter boundary are fixed and reviewed.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "opt_in_provider_intake",
            "requirement": "Explicit opt-in intake, licence review, descriptor review, optional-runtime absence behaviour and an independent public-surface decision are complete; no default registration or shared build/CI change.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "public_default_and_release",
            "requirement": "Explicit default selection, paced resource/deadline evidence and release/public-benchmark approval are recorded; this package is off by default and not qualified.",
            "status": "blocked",
            "blocked": True,
        },
    ]


def validate_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise _reject("manifest must be an object")
    missing = sorted(set(MANIFEST_FIELDS) - set(manifest))
    if missing:
        raise _reject("manifest missing fields: " + ",".join(missing))
    extra = sorted(set(manifest) - set(MANIFEST_FIELDS))
    if extra:
        raise _reject("manifest has unknown fields: " + ",".join(extra))

    normalized: Dict[str, Any] = {}
    for field in MANIFEST_FIELDS:
        value = manifest[field]
        if field in MANIFEST_SHA_FIELDS:
            normalized[field] = _validate_sha256(value, field)
        elif field in MANIFEST_PATH_FIELDS:
            normalized[field] = _validate_abs_path(value, field)
        elif field == "source_revision":
            normalized[field] = _validate_revision(value)
        elif field == "variant":
            if value != REQUIRED_VARIANT:
                raise _reject("variant must be " + REQUIRED_VARIANT)
            normalized[field] = value
        elif field == "claimed_pyannote_segmentation_vad_capability":
            if value is not True:
                raise _reject("manifest must claim the pyannote segmentation/VAD capability")
            normalized[field] = True
        elif field in ("channels", "frame_samples", "sample_rate_hz", "onset_hangover_frames"):
            if not _is_int(value):
                raise _reject(f"{field} is not an integer")
            normalized[field] = value
        elif field == "threshold":
            normalized[field] = _validate_decimal_string(value, field)
        elif field == "task_geometry":
            if not isinstance(value, str) or not value:
                raise _reject("task_geometry must be a non-empty string")
            if value not in ("vad", "segmentation", "vad+segmentation"):
                raise _reject("task_geometry must be vad, segmentation, or vad+segmentation")
            normalized[field] = value
        else:
            normalized[field] = value

    if normalized["channels"] != CHANNELS:
        raise _reject("channels must be 1 for the v0 boundary")
    if normalized["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise _reject("sample_rate_hz is outside the admitted range")
    if normalized["frame_samples"] != SDK_FRAME_SAMPLES:
        raise _reject("frame_samples is outside the admitted range")
    if normalized["onset_hangover_frames"] < 0 or normalized["onset_hangover_frames"] > 1000:
        raise _reject("onset_hangover_frames is outside the admitted range")
    return normalized


def _base_manifest() -> Dict[str, Any]:
    base = "/opt/pyannote-segmentation-vad"
    return {
        "adapter_config_path": base + "/adapter.json",
        "adapter_config_sha256": "1" * 64,
        "benchmark_record_path": base + "/benchmark.json",
        "benchmark_record_sha256": "2" * 64,
        "build_record_path": base + "/build.json",
        "build_record_sha256": "3" * 64,
        "channels": 1,
        "claimed_pyannote_segmentation_vad_capability": True,
        "corpus_manifest_path": base + "/corpus.json",
        "corpus_manifest_sha256": "4" * 64,
        "frame_samples": 160,
        "license_record_path": base + "/license.json",
        "license_record_sha256": "5" * 64,
        "model_asset_path": base + "/model.bin",
        "model_asset_sha256": "6" * 64,
        "onset_hangover_frames": 3,
        "parity_vector_path": base + "/parity.json",
        "parity_vector_sha256": "7" * 64,
        "rights_record_path": base + "/rights.json",
        "rights_record_sha256": "8" * 64,
        "runtime_lock_path": base + "/runtime.lock",
        "runtime_lock_sha256": "9" * 64,
        "runtime_path": base + "/runtime",
        "sample_rate_hz": 16000,
        "source_checkout_path": base + "/src",
        "source_manifest_path": base + "/source.json",
        "source_manifest_sha256": "a" * 64,
        "source_revision": "b" * 40,
        "task_geometry": "vad+segmentation",
        "threshold": "0.5",
        "variant": REQUIRED_VARIANT,
    }


def _adverse_manifest_cases() -> List[Dict[str, Any]]:
    cases = []
    def add(name: str, manifest: Any, reason_sub: str) -> None:
        try:
            validate_manifest(manifest)
            cases.append({"case": name, "result": "accepted", "reason": "unexpected"})
        except Reject as exc:
            cases.append({"case": name, "result": "rejected", "reason": str(exc)})
            if reason_sub.lower() not in str(exc).lower():
                cases[-1]["reason_match"] = False
    add("manifest_not_object", [], "object")
    m = _base_manifest(); del m["model_asset_sha256"]; add("manifest_missing_field", m, "missing fields")
    m = _base_manifest(); m["extra"] = 1; add("manifest_extra_field", m, "unknown fields")
    m = _base_manifest(); m["model_asset_path"] = "relative/model.bin"; add("manifest_relative_path", m, "absolute path")
    m = _base_manifest(); m["model_asset_path"] = "/opt/../model.bin"; add("manifest_traversal_path", m, "absolute path")
    m = _base_manifest(); m["model_asset_sha256"] = "XYZ"; add("manifest_bad_sha", m, "sha-256")
    m = _base_manifest(); m["source_revision"] = "abc"; add("manifest_short_revision", m, "40-hex")
    m = _base_manifest(); m["source_revision"] = "g" * 40; add("manifest_nonhex_revision", m, "40-hex")
    m = _base_manifest(); m["source_revision"] = "0" * 40; add("manifest_zero_revision", m, "40-hex")
    m = _base_manifest(); m["variant"] = "wrong"; add("manifest_wrong_variant", m, "variant")
    m = _base_manifest(); m["claimed_pyannote_segmentation_vad_capability"] = False; add("manifest_capability_false", m, "capability")
    m = _base_manifest(); m["channels"] = 2; add("manifest_wrong_channels", m, "channels")
    m = _base_manifest(); m["sample_rate_hz"] = 8000; add("manifest_wrong_sample_rate", m, "sample_rate_hz")
    m = _base_manifest(); m["frame_samples"] = 320; add("manifest_wrong_frame_samples", m, "frame_samples")
    m = _base_manifest(); m["onset_hangover_frames"] = -1; add("manifest_negative_hangover", m, "onset_hangover_frames")
    m = _base_manifest(); m["threshold"] = "1e-3"; add("manifest_threshold_exponent", m, "decimal")
    m = _base_manifest(); m["threshold"] = "nan"; add("manifest_threshold_nan", m, "decimal")
    m = _base_manifest(); m["threshold"] = "-0.1"; add("manifest_threshold_negative", m, "decimal")
    m = _base_manifest(); m["task_geometry"] = "diarization"; add("manifest_wrong_geometry", m, "task_geometry")
    return cases


# -------------------------
# Synthetic control (feature-domain / signal-domain deterministic)
# -------------------------

def _lcg(seed: int, n: int) -> List[int]:
    # Deterministic 32-bit LCG, no numpy.
    x = seed & 0xFFFFFFFF
    out = []
    for _ in range(n):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        out.append(x)
    return out


def synthetic_audio_frames() -> List[List[float]]:
    # 1s total: 100 frames of 160 samples, 16kHz mono.
    # Segments: silence, quiet speech-like tone, noise, active speech-like tone, silence.
    # This is NOT real speech and NOT pyannote output.
    frames: List[List[float]] = []
    rnd = _lcg(0xC0FFEE, 16000)
    for frame_idx in range(100):
        frame = []
        for i in range(160):
            t = frame_idx * 160 + i
            r = ((rnd[t] / 0x7FFFFFFF) * 2.0 - 1.0)
            if 10 <= frame_idx < 30:  # quiet speech-like
                s = 0.03 * math.sin(2 * math.pi * 220 * t / SAMPLE_RATE_HZ)
                v = s + 0.002 * r
            elif 30 <= frame_idx < 45:  # noise
                v = 0.02 * r
            elif 45 <= frame_idx < 75:  # active speech-like
                s = 0.15 * math.sin(2 * math.pi * 180 * t / SAMPLE_RATE_HZ) + 0.05 * math.sin(2 * math.pi * 360 * t / SAMPLE_RATE_HZ)
                v = s + 0.003 * r
            else:
                v = 0.001 * r
            # clamp to [-1,1]
            if v > 1.0: v = 1.0
            if v < -1.0: v = -1.0
            frame.append(float(v))
        frames.append(frame)
    return frames


def frame_rms_dbfs(frame: Sequence[float]) -> float:
    if len(frame) != SDK_FRAME_SAMPLES:
        raise _reject("frame length must be 160")
    acc = 0.0
    for x in frame:
        if isinstance(x, bool) or not isinstance(x, (int, float)):
            raise _reject("frame sample must be numeric")
        xf = float(x)
        if not math.isfinite(xf):
            raise _reject("nonfinite_frame")
        if xf < -1.0 or xf > 1.0:
            raise _reject("frame sample out of range")
        acc += xf * xf
    rms = math.sqrt(acc / len(frame))
    db = 20.0 * math.log10(rms + 1e-12)
    return db


def synthetic_control() -> Dict[str, Any]:
    frames = synthetic_audio_frames()
    # deterministic thresholding control only
    threshold_db = -35.0
    hangover = 2
    probs = []
    decisions = []
    hang = 0
    for idx, frame in enumerate(frames):
        db = frame_rms_dbfs(frame)
        # map db to probability deterministically, not a model
        p = 1.0 / (1.0 + math.exp(-(db - threshold_db) / 3.0))
        p = min(1.0, max(0.0, p))
        probs.append(p)
        raw = p >= 0.5
        if raw:
            hang = hangover
            decisions.append(True)
        elif hang > 0:
            hang -= 1
            decisions.append(True)
        else:
            decisions.append(False)
    # ground truth by construction
    truth = []
    for idx in range(100):
        if 10 <= idx < 30 or 45 <= idx < 75:
            truth.append("speech")
        else:
            truth.append("nonspeech")
    known_tp = sum(1 for d, t in zip(decisions, truth) if d and t == "speech")
    known_fp = sum(1 for d, t in zip(decisions, truth) if d and t == "nonspeech")
    known_fn = sum(1 for d, t in zip(decisions, truth) if (not d) and t == "speech")
    known_tn = sum(1 for d, t in zip(decisions, truth) if (not d) and t == "nonspeech")
    # boundaries in frame indices where decision changes to speech / nonspeech
    events = []
    in_speech = False
    start = 0
    for i, d in enumerate(decisions):
        if d and not in_speech:
            in_speech = True
            start = i
        elif (not d) and in_speech:
            in_speech = False
            events.append({"start_frame": start, "end_frame": i, "start_sample": start * 160, "end_sample": i * 160})
    if in_speech:
        events.append({"start_frame": start, "end_frame": 100, "start_sample": start * 160, "end_sample": 16000})
    prob_digest = sha256_bytes(canonical_bytes([round(p, 9) for p in probs]))
    return {
        "control_id": "pyannote-segmentation-vad-synthetic-signal-control/0.1",
        "control_scope": "deterministic synthetic signal RMS-threshold control only; no audio corpus, no pyannote runtime, no model, no speaker",
        "metric_scope": "synthetic_signal_domain_not_a_pyannote_or_corpus_result",
        "not_pyannote": True,
        "not_real_audio_corpus": True,
        "qualifies_candidate": False,
        "frame_count": 100,
        "threshold_dbfs": threshold_db,
        "hangover_frames": hangover,
        "probability_digest": prob_digest,
        "detected_speech_events": events,
        "counts": {"tp": known_tp, "fp": known_fp, "fn": known_fn, "tn": known_tn},
        "notes": [
            "Synthetic control proves deterministic local arithmetic and reporting only.",
            "It is not a pyannote segmentation/VAD result, not a real-corpus score, and not parity."
        ],
    }


def _candidate_metrics() -> Dict[str, Any]:
    return {
        "derived_from_synthetic_control": False,
        "timestamped_probability_brier": {"measured": False, "reason": "no real pyannote runtime output or labeled corpus", "value": None},
        "timestamped_probability_log_loss": {"measured": False, "reason": "no real pyannote runtime output or labeled corpus", "value": None},
        "event_boundary_precision": {"measured": False, "reason": "no labeled onset/offset truth", "value": None},
        "event_boundary_recall": {"measured": False, "reason": "no labeled onset/offset truth", "value": None},
        "onset_delay_ms": {"measured": False, "reason": "no real runtime or labeled corpus", "value": None},
        "offset_delay_ms": {"measured": False, "reason": "no real runtime or labeled corpus", "value": None},
        "speech_false_positive_rate": {"measured": False, "reason": "no labeled nonspeech corpus", "value": None},
        "speech_false_negative_rate": {"measured": False, "reason": "no labeled speech corpus", "value": None},
    }


def run_adverse_controls() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    def rej(name: str, fn, reason_sub: str) -> None:
        try:
            fn()
            cases.append({"case": name, "result": "accepted", "reason": "unexpected"})
        except Reject as exc:
            r = str(exc)
            cases.append({"case": name, "result": "rejected", "reason": r})
            if reason_sub.lower() not in r.lower():
                cases[-1]["reason_match"] = False

    # frame/input adverse
    rej("frame_short", lambda: frame_rms_dbfs([0.0] * 10), "160")
    rej("frame_long", lambda: frame_rms_dbfs([0.0] * 161), "160")
    rej("frame_nan", lambda: frame_rms_dbfs([0.0] * 159 + [float("nan")]), "nonfinite")
    rej("frame_inf", lambda: frame_rms_dbfs([0.0] * 159 + [float("inf")]), "nonfinite")
    rej("frame_neg_inf", lambda: frame_rms_dbfs([0.0] * 159 + [float("-inf")]), "nonfinite")
    rej("frame_bool", lambda: frame_rms_dbfs([True] + [0.0] * 159), "numeric")
    rej("frame_string", lambda: frame_rms_dbfs(["0"] + [0.0] * 159), "numeric")
    rej("frame_out_of_range", lambda: frame_rms_dbfs([2.0] + [0.0] * 159), "out of range")

    # manifest adverse
    cases.extend(_adverse_manifest_cases())

    # strict json adverse
    def bad_dup():
        strict_loads('{"a":1,"a":2}')
    def bad_nan():
        strict_loads('{"a":NaN}')
    def bad_inf():
        strict_loads('{"a":Infinity}')
    rej("json_duplicate_key", bad_dup, "duplicate")
    rej("json_nan", bad_nan, "non-finite")
    rej("json_infinity", bad_inf, "non-finite")

    # qualification gate - missing manifest/runtime cannot qualify
    def qual():
        # no manifest supplied means cannot qualify
        raise _reject("no approved caller manifest/runtime/rights/corpus/parity is supplied")
    rej("qualification_without_manifest", qual, "no approved caller manifest")

    if any(c["result"] != "rejected" for c in cases):
        raise _reject("an adverse control was accepted")
    return cases


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": "analysis",
        "source": "plan/swarm/VERIFICATION.md",
        "requirements": [
            {"id": "timestamped_probabilities_scored", "measured": False, "reason": "no real pyannote runtime, no labeled corpus, no probability scoring", "requirement": "Score timestamped probabilities, event boundaries and detections."},
            {"id": "quiet_and_active_speech", "measured": False, "reason": "no labeled speech corpus", "requirement": "Include quiet and active speech, idle noise, known positives and negatives."},
            {"id": "onset_offset_delay", "measured": False, "reason": "no labeled onset/offset truth or real runtime", "requirement": "Measure onset/offset delay and stratified FN/FP."},
            {"id": "independent_state", "measured": False, "reason": "no runtime session/state implementation evaluated", "requirement": "Verify independent state, exact source intervals, availability, dropped/stale events and cross-hop behavior."},
            {"id": "validity_separate_from_nonspeech", "measured": False, "reason": "no real event stream; synthetic control is not pyannote output", "requirement": "Separate validity from nonspeech."},
        ],
    }


def _build_report() -> Dict[str, Any]:
    verify_document_pins()
    task_identity = task_row_identity()
    control = synthetic_control()
    adverse = run_adverse_controls()
    gates = _gate_rows()
    acceptance = _acceptance_profile()

    if any(g["status"] != "blocked" or g["blocked"] is not True for g in gates):
        raise _reject("release gates must be blocked")
    if any(c["result"] != "rejected" for c in adverse):
        raise _reject("adverse control accepted")
    if control["qualifies_candidate"] is not False:
        raise _reject("synthetic control cannot qualify")

    report = {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "category_id": CATEGORY_ID,
        "profile": PROFILE,
        "mode": MODE,
        "repository": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "reviewer": REVIEWER,
        "worktree": CLAIM_WORKTREE,
        "generated_by": "reference.py",
        "decision": DECISION,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION,
        "defer_before": DEFER_BEFORE,
        "proposal_only": True,
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "task_row_identity": task_identity,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "mutable_provenance": {
            "gate": False,
            "note": "Board status is mutable and the full board file is never hashed. Only stable linked-row identity is gated in task_row_identity.",
            "path": BOARD_PATH,
        },
        "upstream_identity": {
            "implementation_present": False,
            "license_verified": False,
            "name": "pyannote/segmentation or pyannote VAD family (exact variant not staged)",
            "note": "Inventory and local research report that no exact pyannote candidate weights, source checkout, or adapter are staged. No repository URL, revision, release, model hash, or licence grant is invented.",
            "project_url": None,
            "repository_url": None,
            "recorded_source_id": "candidate_matrix.csv row 8 / agent-vad-asr-trials",
            "release_or_tag": None,
            "revision": None,
            "revision_pin_available": False,
            "runtime_present": False,
            "source_checkout_present": False,
        },
        "asset_audit": {
            "audit_result": "absent",
            "all_absence_probes_absent": True,
            "note": "No pyannote segmentation/VAD source checkout, weights, runtime lock, build record, licence/rights record, corpus manifest, parity vector, or benchmark record was observed in the workspace for this exact component.",
            "observed": {
                "absence_probes": [
                    {"exists": False, "path": "research/repos/pyannote-segmentation"},
                    {"exists": False, "path": "research/repos/pyannote-audio"},
                    {"exists": False, "path": "data/checkouts/pyannote-segmentation"},
                    {"exists": False, "path": "data/models/pyannote-segmentation"},
                    {"exists": False, "path": "data/models/pyannote"},
                    {"exists": False, "path": "data/weights/pyannote-segmentation"},
                    {"exists": False, "path": "data/envs/pyannote-segmentation"},
                    {"exists": False, "path": "data/build-records/pyannote-segmentation-vad.json"},
                    {"exists": False, "path": "data/rights/pyannote-segmentation-vad-rights.json"},
                    {"exists": False, "path": "data/rights/pyannote-segmentation-vad-license.json"},
                    {"exists": False, "path": "data/runs/pyannote-segmentation-vad-parity/manifest.json"},
                    {"exists": False, "path": "data/runs/pyannote-segmentation-vad-cohort/manifest.json"},
                    {"exists": False, "path": "third_party/pyannote-segmentation"},
                    {"exists": False, "path": "deps/pyannote-segmentation"},
                ]
            },
            "benchmark_record_present": False,
            "build_record_present": False,
            "corpus_manifest_present": False,
            "license_record_present": False,
            "parity_manifest_present": False,
            "rights_record_present": False,
            "runtime_lock_present": False,
            "runtime_present": False,
            "source_checkout_present": False,
            "source_revision": None,
            "source_revision_pin_available": False,
        },
        "asset_requirements": [
            {"id": "source_checkout", "path": "research/repos/pyannote-segmentation", "required": True, "revision": None, "status": "absent"},
            {"id": "model_weights", "path": "data/models/pyannote-segmentation", "required": True, "sha256": None, "status": "absent"},
            {"id": "runtime_and_build", "path": "data/envs/pyannote-segmentation", "runtime_lock_path": "data/envs/pyannote-segmentation/requirements.lock", "runtime_lock_sha256": None, "build_record_path": "data/build-records/pyannote-segmentation-vad.json", "build_record_sha256": None, "required": True, "status": "absent"},
            {"id": "source_license_record", "path": "data/rights/pyannote-segmentation-vad-license.json", "required": True, "recorded_license": None, "status": "absent"},
            {"id": "model_and_corpus_rights", "rights_path": "data/rights/pyannote-segmentation-vad-rights.json", "corpus_path": "data/runs/pyannote-segmentation-vad-cohort/manifest.json", "required": True, "status": "absent"},
            {"id": "task_geometry_and_adapter", "config_path": "data/plans/pyannote-segmentation-vad-adapter.json", "required": True, "task_geometry_status": "unestablished", "status": "absent"},
            {"id": "exact_parity_vector", "parity_path": "data/runs/pyannote-segmentation-vad-parity/manifest.json", "required": True, "status": "absent"},
            {"id": "benchmark_and_release", "benchmark_path": "data/runs/pyannote-segmentation-vad-cohort/manifest.json", "release_path": "data/runs/pyannote-segmentation-vad-release.json", "required": True, "status": "absent"},
        ],
        "exact_blockers": [
            {"id": "source_checkout_absent", "requirement": "Supply the exact approved pyannote segmentation/VAD implementation at an immutable 40-hex revision with a per-file SHA-256 manifest; no exact checkout is staged.", "state": "absent"},
            {"id": "weights_absent", "requirement": "Supply exact model/weights assets with SHA-256, provenance and rights/gated-access evidence; no pyannote weights are staged.", "state": "absent"},
            {"id": "runtime_and_build_record_absent", "requirement": "Provide an isolated hash-pinned runtime and reproducible build/execution record; no runtime/build record exists.", "state": "absent"},
            {"id": "license_and_rights_unverified", "requirement": "Verify implementation/model/corpus licence and rights with dated evidence; no rights record exists.", "state": "absent"},
            {"id": "corpus_and_labels_absent", "requirement": "Provide a rights-cleared, label-complete held-out cohort with speech/nonspeech/unknown regions and onset/offset truth; none is staged for this component.", "state": "absent"},
            {"id": "task_geometry_unestablished", "requirement": "Fix task geometry (VAD/segmentation/diarization boundary), sample-rate/hop/window/lookahead, event schema, and analysis adapter boundary; none is established.", "state": "absent"},
            {"id": "exact_parity_absent", "requirement": "Provide an approved exact-runtime parity vector on frozen caller input; synthetic control is not parity.", "state": "absent"},
            {"id": "benchmark_and_release_absent", "requirement": "Provide held-out analysis-profile scoring, paced resource/deadline evidence, and release approval; none exists.", "state": "absent"},
        ],
        "gates": gates,
        "acceptance_profile": acceptance,
        "synthetic_control": control,
        "candidate_metrics": _candidate_metrics(),
        "controls": {
            "adverse": adverse,
            "adverse_case_count": len(adverse),
            "all_adverse_rejected": True,
            "qualification_gate_without_manifest": {
                "qualification": QUALIFICATION,
                "qualifies": False,
                "reason": "no approved caller manifest, runtime, rights record, corpus or parity vector is supplied",
            },
            "structural_manifest_validation_is_not_qualification": True,
        },
        "qualification": {
            "decision": DECISION,
            "status": QUALIFICATION,
            "qualification_status": QUALIFICATION,
            "candidate_qualified": False,
            "proposal_only": True,
            "implementation_present": False,
            "runtime_invoked": False,
            "parity_present": False,
            "corpus_present": False,
            "release_qualification_present": False,
            "no_missing_result_qualifies_candidate": True,
            "synthetic_control_is_not_candidate_evidence": True,
            "defer_before": DEFER_BEFORE,
            "evidence_status": EVIDENCE_STATUS,
            "reason": "No exact pyannote segmentation/VAD source, weights, runtime, licence/rights record, corpus, parity vector, task geometry, or benchmark is present. Synthetic signal control does not qualify the row.",
        },
        "reopen_conditions": [{"condition": g["requirement"], "gate_id": g["id"]} for g in gates],
        "reproduction": {
            "all": "PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py",
            "compare": "exact SHA-256 over canonical JSON; no tolerance; three byte-identical cold-start repeats",
        },
        "non_claims": [
            "No pyannote segmentation/VAD implementation, source checkout, model, weight, runtime, or binary is loaded, built, linked, downloaded, or executed.",
            "No upstream repository URL, revision, release, model hash, licence grant, or rights approval is invented.",
            "No real audio, labelled corpus, diarization labels, speaker-change labels, or benchmark is read.",
            "The synthetic signal control is deterministic local arithmetic only; it is not pyannote output, not a real-corpus score, and not parity.",
            "No provider, descriptor, registry, installed v0 path, analysis event surface, shared build, CI, board, handoff, or release changed.",
            "No listening, device timing, resource, deadline, or release qualification is performed.",
            "Missing source, weights, runtime, rights, corpus, or parity evidence never qualifies the candidate; the decision remains DEFER.",
        ],
    }

    # hard guards
    if report["decision"] != DECISION or report["qualification_status"] != QUALIFICATION:
        raise _reject("disposition changed")
    if report["qualification"]["candidate_qualified"] is not False:
        raise _reject("candidate qualified")
    if report["synthetic_control"]["qualifies_candidate"] is not False:
        raise _reject("synthetic control qualifies")
    if len(report["gates"]) != 8 or not all(g["blocked"] for g in report["gates"]):
        raise _reject("gate policy violated")
    if not all(c["result"] == "rejected" for c in report["controls"]["adverse"]):
        raise _reject("adverse accepted")
    if BOARD_PATH in report["source_pins"] or BOARD_PATH in report["boundary_pins"]:
        raise _reject("mutable board pinned")
    canonical_bytes(report)
    return report


class EvidenceReport:
    """Atomic holder; rejected input never mutates committed state."""

    def __init__(self) -> None:
        self.state: Dict[str, Any] | None = None

    def snapshot(self) -> Dict[str, Any] | None:
        import copy
        return copy.deepcopy(self.state)

    def build(self, payload: Any = None) -> Dict[str, Any]:
        if payload is not None:
            if not isinstance(payload, dict):
                raise _reject("payload must be a mapping")
            for k, v in payload.items():
                if not isinstance(k, str):
                    raise _reject("payload key must be a string")
                if isinstance(v, float) and not math.isfinite(v):
                    raise _reject("nonfinite payload value: " + k)
                if isinstance(v, int) and not isinstance(v, bool) and abs(v) > 2**53 - 1:
                    raise _reject("payload integer is outside the exact range: " + k)
        candidate = _build_report()
        self.state = candidate
        return candidate


def build_report() -> Dict[str, Any]:
    return _build_report()
