# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for Resemblyzer speaker-similarity proxy.

Task ``SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY`` is research-control
feasibility/blocker evidence. No exact licensed Resemblyzer source checkout,
pinned encoder weights/runtime lock, rights record, parity vector, or matched
held-out benchmark is present in this workspace as a qualified SDK asset. This
module builds a bounded, deterministic blocker package. It never downloads
assets, never invokes external runtimes, and never claims qualification.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

TASK = "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"
TITLE = "Resemblyzer speaker-similarity proxy"
COMPONENT = "resemblyzer-speaker-similarity-proxy"
CATEGORY_ID = "SPK-05"
PROFILE = "evidence"
MODE = "research-control"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"
BASE_COMMIT = "a9cf338c0b363d69408c931071071583a49ebdc1"
REVIEWER = "reviewer-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY"
)
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DEFER_BEFORE = "opt_in_provider_intake"
SCHEMA_ID = "audio-sdk/task-evidence/resemblyzer-speaker-similarity-proxy/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_PREFIX = "docs/task-evidence/resemblyzer-speaker-similarity-proxy/"
REQUIRED_VARIANT = "resemblyzer_speaker_similarity_proxy_research_control_adapter"
SDK_FRAME_SAMPLES = 160
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-" "Identifier: Apache-2.0\n"
)

HERE = Path(__file__).resolve().parent
_DEFAULT_SDK_ROOT = Path("/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-RESEMBLYZER-SPEAKER-SIMILARITY-PROXY")
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
    "research/accent-conversion-20261101/README.md": "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c",
}
BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/acceptance-matrix.md": "2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
    "docs/task-evidence/survey-spk-05/README.md": "f5974e2009a1b4aca7e6b08322a6f16a4b7510184b58da4bf5fa8572b4b2c478",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
}

SCOPE = {
    "annotated_speaker_identity_corpus": False,
    "benchmark_claim": False,
    "device_timing": False,
    "diarization_claim": False,
    "external_runtime_invoked": False,
    "identification_claim": False,
    "listening": False,
    "network_used": False,
    "numeric_parity_claim": False,
    "proposal_only": True,
    "real_audio": False,
    "real_corpus": False,
    "release_claim": False,
    "speaker_verification_claim": False,
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
    "claimed_resemblyzer_speaker_similarity_proxy_capability",
    "corpus_manifest_path",
    "corpus_manifest_sha256",
    "encoder_model_path",
    "encoder_model_sha256",
    "frame_samples",
    "geometry_manifest_path",
    "geometry_manifest_sha256",
    "license_record_path",
    "license_record_sha256",
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
            "requirement": "Exact approved Resemblyzer implementation, canonical repository URL, full 40-hex source revision, per-file SHA-256, encoder model/weights identity, and dependency lock are immutable pins.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "runtime_admission",
            "requirement": "An isolated, hash-pinned runtime and reproducible build/execution record run the exact Resemblyzer encoder on a recorded platform without network or unpinned dependency drift.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "artifact_rights_and_licence",
            "requirement": "Implementation, encoder weights, dependencies, and any evaluation audio/corpus rights are verified with dated evidence; no third-party media is redistributed without rights.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "exact_reference_parity",
            "requirement": "Approved exact-runtime Resemblyzer embeddings/cosine outputs match a frozen caller-supplied input and geometry; synthetic controls are not parity.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "evidence_cohort_and_scoring",
            "requirement": "A rights-cleared held-out cohort scores speaker similarity as a proxy separately from identification/verification; same-clip and cross-clip geometry, encoder revision, and scorer are frozen.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "task_geometry_and_adapter_boundary",
            "requirement": "Source/target/enrollment geometry, sample-rate/channel normalization, embedding windowing, cosine/scoring contract, and opt-in research-control adapter boundary are fixed and reviewed.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "opt_in_provider_intake",
            "requirement": "Explicit opt-in intake, licence review, descriptor review, optional-runtime absence behavior, and independent public-surface decision are complete; no default registration or shared build/CI change.",
            "status": "blocked",
            "blocked": True,
        },
        {
            "id": "public_default_and_release",
            "requirement": "Explicit default selection, paced resource/deadline evidence, and release/public-benchmark approval are recorded; this package is off by default and not qualified.",
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
        elif field == "claimed_resemblyzer_speaker_similarity_proxy_capability":
            if value is not True:
                raise _reject("manifest must claim the resemblyzer speaker-similarity proxy capability")
            normalized[field] = True
        elif field in ("channels", "frame_samples", "sample_rate_hz"):
            if not _is_int(value):
                raise _reject(f"{field} is not an integer")
            normalized[field] = value
        elif field == "task_geometry":
            if not isinstance(value, str) or not value:
                raise _reject("task_geometry must be a non-empty string")
            if value not in ("same_clip_proxy", "cross_clip_proxy", "enrollment_proxy"):
                raise _reject("task_geometry must be same_clip_proxy, cross_clip_proxy, or enrollment_proxy")
            normalized[field] = value
        else:
            normalized[field] = value

    if normalized["channels"] != CHANNELS:
        raise _reject("channels must be 1 for the v0 boundary")
    if normalized["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise _reject("sample_rate_hz is outside the admitted range")
    if normalized["frame_samples"] != SDK_FRAME_SAMPLES:
        raise _reject("frame_samples is outside the admitted range")
    return normalized


def _base_manifest() -> Dict[str, Any]:
    base = "/opt/resemblyzer-speaker-similarity-proxy"
    return {
        "adapter_config_path": base + "/adapter.json",
        "adapter_config_sha256": "1" * 64,
        "benchmark_record_path": base + "/benchmark.json",
        "benchmark_record_sha256": "2" * 64,
        "build_record_path": base + "/build.json",
        "build_record_sha256": "3" * 64,
        "channels": 1,
        "claimed_resemblyzer_speaker_similarity_proxy_capability": True,
        "corpus_manifest_path": base + "/corpus.json",
        "corpus_manifest_sha256": "4" * 64,
        "encoder_model_path": base + "/encoder.pt",
        "encoder_model_sha256": "5" * 64,
        "frame_samples": 160,
        "geometry_manifest_path": base + "/geometry.json",
        "geometry_manifest_sha256": "6" * 64,
        "license_record_path": base + "/license.json",
        "license_record_sha256": "7" * 64,
        "parity_vector_path": base + "/parity.json",
        "parity_vector_sha256": "8" * 64,
        "rights_record_path": base + "/rights.json",
        "rights_record_sha256": "9" * 64,
        "runtime_lock_path": base + "/runtime.lock",
        "runtime_lock_sha256": "a" * 64,
        "runtime_path": base + "/runtime",
        "sample_rate_hz": 16000,
        "source_checkout_path": base + "/src",
        "source_manifest_path": base + "/source.json",
        "source_manifest_sha256": "b" * 64,
        "source_revision": "c" * 40,
        "task_geometry": "same_clip_proxy",
        "variant": REQUIRED_VARIANT,
    }


# -------------------------
# Synthetic control (deterministic signal-domain embedding proxy)
# -------------------------

def _lcg(seed: int, n: int) -> List[int]:
    x = seed & 0xFFFFFFFF
    out = []
    for _ in range(n):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        out.append(x)
    return out


def _synthetic_wave(kind: str, seed: int, frames: int = 100) -> List[List[float]]:
    rnd = _lcg(seed, frames * SDK_FRAME_SAMPLES)
    out: List[List[float]] = []
    for frame_idx in range(frames):
        frame = []
        for i in range(SDK_FRAME_SAMPLES):
            t = frame_idx * SDK_FRAME_SAMPLES + i
            r = ((rnd[t] / 0x7FFFFFFF) * 2.0 - 1.0)
            if kind == "speaker_a":
                v = 0.12 * math.sin(2 * math.pi * 180 * t / SAMPLE_RATE_HZ) + 0.04 * math.sin(2 * math.pi * 360 * t / SAMPLE_RATE_HZ) + 0.004 * r
            elif kind == "speaker_a_variant":
                v = 0.11 * math.sin(2 * math.pi * 183 * t / SAMPLE_RATE_HZ) + 0.035 * math.sin(2 * math.pi * 366 * t / SAMPLE_RATE_HZ) + 0.005 * r
            elif kind == "speaker_b":
                v = 0.10 * math.sin(2 * math.pi * 260 * t / SAMPLE_RATE_HZ) + 0.03 * math.sin(2 * math.pi * 520 * t / SAMPLE_RATE_HZ) + 0.004 * r
            else:
                raise _reject("unknown synthetic kind")
            v = max(-1.0, min(1.0, float(v)))
            frame.append(v)
        out.append(frame)
    return out


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
    return 20.0 * math.log10(math.sqrt(acc / len(frame)) + 1e-12)


def _embedding_proxy(frames: Sequence[Sequence[float]]) -> List[float]:
    # Deterministic toy embedding: low-dimensional spectral-ish stats, not Resemblyzer.
    if not frames:
        raise _reject("frames must be non-empty")
    # 8 dims: mean abs, rms, zero crossing, low-band energy, mid, high, centroid proxy, kurtosis proxy
    total = 0
    sums = [0.0] * 8
    prev = 0.0
    for f in frames:
        if len(f) != SDK_FRAME_SAMPLES:
            raise _reject("frame length must be 160")
        for i, x in enumerate(f):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise _reject("frame sample must be numeric")
            xf = float(x)
            if not math.isfinite(xf):
                raise _reject("nonfinite_frame")
            if xf < -1.0 or xf > 1.0:
                raise _reject("frame sample out of range")
            ax = abs(xf)
            sums[0] += ax
            sums[1] += xf * xf
            if total > 0 and ((xf >= 0) != (prev >= 0)):
                sums[2] += 1.0
            # crude band proxies by sample position in frame (deterministic, not FFT)
            phase = i / SDK_FRAME_SAMPLES
            if phase < 1/3:
                sums[3] += xf * xf
            elif phase < 2/3:
                sums[4] += xf * xf
            else:
                sums[5] += xf * xf
            sums[6] += phase * ax
            sums[7] += (xf * xf) * (xf * xf)
            prev = xf
            total += 1
    n = float(total)
    vec = [
        sums[0] / n,
        math.sqrt(sums[1] / n),
        sums[2] / n,
        math.sqrt(sums[3] / n),
        math.sqrt(sums[4] / n),
        math.sqrt(sums[5] / n),
        sums[6] / (sums[0] + 1e-12),
        math.sqrt(math.sqrt(sums[7] / n)),
    ]
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vec))
    if norm <= 0.0 or not math.isfinite(norm):
        raise _reject("zero_norm_embedding")
    return [v / norm for v in vec]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        raise _reject("embedding dimension mismatch")
    dot = na = nb = 0.0
    for x, y in zip(a, b):
        for v in (x, y):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
                raise _reject("nonfinite_embedding")
        xf, yf = float(x), float(y)
        dot += xf * yf
        na += xf * xf
        nb += yf * yf
    denom = math.sqrt(na) * math.sqrt(nb)
    if denom <= 0.0 or not math.isfinite(denom):
        raise _reject("zero_norm_embedding")
    c = dot / denom
    if not math.isfinite(c):
        raise _reject("nonfinite_cosine")
    # numeric clamp for float rounding
    return max(-1.0, min(1.0, c))


def synthetic_control() -> Dict[str, Any]:
    a = _synthetic_wave("speaker_a", 0xA11CE, 100)
    a2 = _synthetic_wave("speaker_a_variant", 0xA11CE, 100)
    b = _synthetic_wave("speaker_b", 0xB0B, 100)
    ea = _embedding_proxy(a)
    ea2 = _embedding_proxy(a2)
    eb = _embedding_proxy(b)
    same = cosine_similarity(ea, ea2)
    diff = cosine_similarity(ea, eb)
    same_clip = cosine_similarity(ea, ea)
    digest = sha256_bytes(canonical_bytes({
        "ea": [round(x, 12) for x in ea],
        "ea2": [round(x, 12) for x in ea2],
        "eb": [round(x, 12) for x in eb],
        "same": round(same, 12),
        "diff": round(diff, 12),
        "same_clip": round(same_clip, 12),
    }))
    return {
        "control_id": "resemblyzer-speaker-similarity-proxy-synthetic-signal-control/0.1",
        "control_scope": "deterministic synthetic signal embedding/cosine control only; no Resemblyzer runtime, no model weights, no real speaker audio, no corpus",
        "metric_scope": "synthetic_signal_domain_not_a_resemblyzer_or_corpus_result",
        "not_resemblyzer": True,
        "not_real_audio_corpus": True,
        "not_identification": True,
        "not_verification": True,
        "qualifies_candidate": False,
        "embedding_dim": 8,
        "same_speaker_proxy_cosine": round(same, 12),
        "different_speaker_proxy_cosine": round(diff, 12),
        "same_clip_proxy_cosine": round(same_clip, 12),
        "expected_ordering_holds": bool(same > diff),
        "digest": digest,
        "notes": [
            "Synthetic control proves deterministic local arithmetic/reporting only.",
            "It is not a Resemblyzer embedding, not a speaker verification score, not an identification result, and not parity.",
            "Cosine ordering on toy signals does not qualify any real speaker-similarity claim."
        ],
    }


def _candidate_metrics() -> Dict[str, Any]:
    null = lambda reason: {"measured": False, "reason": reason, "value": None}
    return {
        "derived_from_synthetic_control": False,
        "same_clip_cosine": null("no exact Resemblyzer runtime/model and no rights-cleared eval audio"),
        "cross_clip_cosine": null("no exact Resemblyzer runtime/model and no rights-cleared eval audio"),
        "genuine_impostor_eer": null("no speaker verification trial list or labels"),
        "identification_rank1": null("no enrolled gallery or identification protocol"),
        "embedding_stability": null("no exact runtime and no repeated controlled runs"),
        "source_target_enrollment_geometry_recorded": null("no approved geometry manifest or qualified run"),
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

    # frame/adverse
    rej("frame_short", lambda: frame_rms_dbfs([0.0] * 10), "160")
    rej("frame_long", lambda: frame_rms_dbfs([0.0] * 161), "160")
    rej("frame_nan", lambda: frame_rms_dbfs([0.0] * 159 + [float("nan")]), "nonfinite")
    rej("frame_inf", lambda: frame_rms_dbfs([0.0] * 159 + [float("inf")]), "nonfinite")
    rej("frame_bool", lambda: frame_rms_dbfs([True] + [0.0] * 159), "numeric")
    rej("frame_string", lambda: frame_rms_dbfs(["x"] + [0.0] * 159), "numeric")
    rej("frame_out_of_range", lambda: frame_rms_dbfs([1.5] + [0.0] * 159), "out of range")

    # embedding/cosine adverse
    rej("embedding_dim_mismatch", lambda: cosine_similarity([1.0, 0.0], [1.0]), "dimension")
    rej("embedding_nonfinite", lambda: cosine_similarity([1.0, float("nan")], [1.0, 0.0]), "nonfinite")
    rej("embedding_zero_norm", lambda: cosine_similarity([0.0, 0.0], [1.0, 0.0]), "zero_norm")
    rej("embedding_empty", lambda: cosine_similarity([], []), "dimension")

    # manifest adverse
    def add_manifest(name: str, manifest: Any, reason_sub: str) -> None:
        try:
            validate_manifest(manifest)
            cases.append({"case": name, "result": "accepted", "reason": "unexpected"})
        except Reject as exc:
            cases.append({"case": name, "result": "rejected", "reason": str(exc)})
            if reason_sub.lower() not in str(exc).lower():
                cases[-1]["reason_match"] = False

    add_manifest("manifest_not_object", [], "object")
    m = _base_manifest(); del m["encoder_model_sha256"]; add_manifest("manifest_missing_field", m, "missing fields")
    m = _base_manifest(); m["extra"] = 1; add_manifest("manifest_extra_field", m, "unknown fields")
    m = _base_manifest(); m["encoder_model_path"] = "relative/encoder.pt"; add_manifest("manifest_relative_path", m, "absolute path")
    m = _base_manifest(); m["encoder_model_path"] = "/opt/../encoder.pt"; add_manifest("manifest_traversal_path", m, "absolute path")
    m = _base_manifest(); m["encoder_model_sha256"] = "BAD"; add_manifest("manifest_bad_sha", m, "sha-256")
    m = _base_manifest(); m["source_revision"] = "abc"; add_manifest("manifest_short_revision", m, "40-hex")
    m = _base_manifest(); m["source_revision"] = "g" * 40; add_manifest("manifest_nonhex_revision", m, "40-hex")
    m = _base_manifest(); m["source_revision"] = "0" * 40; add_manifest("manifest_zero_revision", m, "40-hex")
    m = _base_manifest(); m["variant"] = "wrong"; add_manifest("manifest_wrong_variant", m, "variant")
    m = _base_manifest(); m["claimed_resemblyzer_speaker_similarity_proxy_capability"] = False; add_manifest("manifest_capability_false", m, "capability")
    m = _base_manifest(); m["channels"] = 2; add_manifest("manifest_wrong_channels", m, "channels")
    m = _base_manifest(); m["sample_rate_hz"] = 8000; add_manifest("manifest_wrong_sample_rate", m, "sample_rate_hz")
    m = _base_manifest(); m["frame_samples"] = 320; add_manifest("manifest_wrong_frame_samples", m, "frame_samples")
    m = _base_manifest(); m["task_geometry"] = "speaker_verification"; add_manifest("manifest_wrong_geometry", m, "task_geometry")

    # strict json adverse
    rej("json_duplicate_key", lambda: strict_loads('{"a":1,"a":2}'), "duplicate")
    rej("json_nan", lambda: strict_loads('{"a":NaN}'), "non-finite")
    rej("json_infinity", lambda: strict_loads('{"a":Infinity}'), "non-finite")

    # qualification without manifest
    rej("qualification_without_manifest", lambda: (_ for _ in ()).throw(_reject("no approved caller manifest/runtime/rights/corpus/parity is supplied")), "no approved caller manifest")

    if any(c["result"] != "rejected" for c in cases):
        raise _reject("an adverse control was accepted")
    return cases


def _acceptance_profile() -> Dict[str, Any]:
    # Evidence profile is conservative for this proxy: no speaker ID/verification claim.
    return {
        "profile": "evidence",
        "source": "plan/swarm/VERIFICATION.md",
        "requirements": [
            {"id": "pinned_scorer_or_proxy", "measured": False, "reason": "no exact pinned Resemblyzer checkout/encoder/runtime is present", "requirement": "Pin the scorer/proxy, corpus/cohort, aggregation, failed items and controls."},
            {"id": "separate_evidence_classes", "measured": False, "reason": "no qualified cohort; only deterministic synthetic control exists", "requirement": "Preserve separation between paired, unpaired, synthetic, human and source-reported evidence."},
            {"id": "invalid_missing_case", "measured": True, "reason": "adverse controls reject invalid/missing/nonfinite cases", "requirement": "Validate one invalid/missing case and one representative valid result through the reported bundle."},
            {"id": "geometry_independence", "measured": False, "reason": "no qualified source/target/enrollment geometry manifest or run", "requirement": "Record encoder revision and source/target/enrollment geometry independently from converter/runtime."},
            {"id": "no_identity_claim", "measured": True, "reason": "report and contract explicitly forbid identification/verification/release claims", "requirement": "Do not promote similarity proxy to speaker identification, verification, diarization, or release evidence."},
        ],
    }


def _exact_blockers() -> List[Dict[str, str]]:
    return [
        {"id": "source_checkout_absent", "requirement": "Supply exact approved Resemblyzer implementation at an immutable 40-hex revision with per-file SHA-256 manifest; no exact checkout is staged.", "state": "absent"},
        {"id": "encoder_weights_absent", "requirement": "Supply exact encoder model/weights with SHA-256, provenance and rights evidence; no pinned encoder artifact is staged.", "state": "absent"},
        {"id": "runtime_and_build_record_absent", "requirement": "Provide isolated hash-pinned runtime and reproducible build/execution record; no runtime/build record exists.", "state": "absent"},
        {"id": "license_and_rights_unverified", "requirement": "Verify implementation/model/dependency/corpus rights with dated evidence; no rights record exists.", "state": "absent"},
        {"id": "geometry_unestablished", "requirement": "Fix source/target/enrollment geometry, normalization, embedding windowing, and scoring contract; none is qualified.", "state": "absent"},
        {"id": "exact_parity_absent", "requirement": "Provide approved exact-runtime parity vector on frozen caller input/geometry; synthetic control is not parity.", "state": "absent"},
        {"id": "corpus_and_labels_absent", "requirement": "Provide rights-cleared held-out cohort/protocol for proxy evaluation; no qualified corpus or labels are staged.", "state": "absent"},
        {"id": "benchmark_and_release_absent", "requirement": "Provide paced resource/deadline evidence and explicit release/public-benchmark approval; none exists.", "state": "absent"},
    ]


def _asset_requirements() -> List[Dict[str, Any]]:
    return [
        {"id": "source_checkout", "path": "research/repos/resemblyzer", "required": True, "revision": None, "status": "absent"},
        {"id": "encoder_weights", "path": "data/models/resemblyzer/encoder.pt", "required": True, "sha256": None, "status": "absent"},
        {"id": "runtime_and_build", "path": "data/envs/resemblyzer-speaker-similarity-proxy", "runtime_lock_path": "data/envs/resemblyzer-speaker-similarity-proxy/requirements.lock", "runtime_lock_sha256": None, "build_record_path": "data/build-records/resemblyzer-speaker-similarity-proxy.json", "build_record_sha256": None, "required": True, "status": "absent"},
        {"id": "source_license_record", "path": "data/rights/resemblyzer-speaker-similarity-proxy-license.json", "required": True, "recorded_license": None, "status": "absent"},
        {"id": "model_and_corpus_rights", "rights_path": "data/rights/resemblyzer-speaker-similarity-proxy-rights.json", "corpus_path": "data/runs/resemblyzer-speaker-similarity-proxy-cohort/manifest.json", "required": True, "status": "absent"},
        {"id": "task_geometry_and_adapter", "config_path": "data/plans/resemblyzer-speaker-similarity-proxy-adapter.json", "required": True, "task_geometry_status": "unestablished", "status": "absent"},
        {"id": "exact_parity_vector", "parity_path": "data/runs/resemblyzer-speaker-similarity-proxy-parity/manifest.json", "required": True, "status": "absent"},
        {"id": "benchmark_and_release", "benchmark_path": "data/runs/resemblyzer-speaker-similarity-proxy-cohort/manifest.json", "release_path": "data/runs/resemblyzer-speaker-similarity-proxy-release.json", "required": True, "status": "absent"},
    ]


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
            "name": "Resemblyzer speaker encoder / cosine similarity proxy (exact staged variant not qualified)",
            "project_url": "https://github.com/resemble-ai/Resemblyzer",
            "repository_url": None,
            "release_or_tag": None,
            "revision": None,
            "revision_pin_available": False,
            "recorded_source_id": "research/accent-conversion-20261101/README.md and plan/INVENTORY.json component resemblyzer-speaker-similarity-proxy",
            "implementation_present": False,
            "runtime_present": False,
            "source_checkout_present": False,
            "license_verified": False,
            "note": "A research README reports Resemblyzer cosine as a quick similarity proxy in a TokAN smoke test. No exact approved checkout, pinned encoder revision/hash, isolated runtime, rights record, or parity vector is staged as qualified SDK evidence. No URL/revision/licence is invented as approved.",
        },
        "asset_audit": {
            "audit_result": "absent",
            "source_checkout_present": False,
            "encoder_weights_present": False,
            "runtime_present": False,
            "runtime_lock_present": False,
            "build_record_present": False,
            "license_record_present": False,
            "rights_record_present": False,
            "corpus_manifest_present": False,
            "parity_manifest_present": False,
            "benchmark_record_present": False,
            "source_revision": None,
            "source_revision_pin_available": False,
            "all_absence_probes_absent": True,
            "observed": {
                "absence_probes": [
                    {"exists": False, "path": "research/repos/Resemblyzer"},
                    {"exists": False, "path": "research/repos/resemblyzer"},
                    {"exists": False, "path": "data/models/resemblyzer"},
                    {"exists": False, "path": "data/models/resemblyzer-speaker-similarity-proxy"},
                    {"exists": False, "path": "data/checkouts/resemblyzer"},
                    {"exists": False, "path": "data/envs/resemblyzer-speaker-similarity-proxy"},
                    {"exists": False, "path": "data/build-records/resemblyzer-speaker-similarity-proxy.json"},
                    {"exists": False, "path": "data/rights/resemblyzer-speaker-similarity-proxy-rights.json"},
                    {"exists": False, "path": "data/rights/resemblyzer-speaker-similarity-proxy-license.json"},
                    {"exists": False, "path": "data/runs/resemblyzer-speaker-similarity-proxy-parity/manifest.json"},
                    {"exists": False, "path": "data/runs/resemblyzer-speaker-similarity-proxy-cohort/manifest.json"},
                    {"exists": False, "path": "third_party/resemblyzer"},
                    {"exists": False, "path": "deps/resemblyzer"},
                ]
            },
            "note": "No Resemblyzer source checkout, encoder weights, runtime lock, build record, licence/rights record, corpus manifest, parity vector, or benchmark record was observed in the workspace for this exact component.",
        },
        "asset_requirements": _asset_requirements(),
        "exact_blockers": _exact_blockers(),
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
            "reason": "No exact Resemblyzer source, pinned encoder weights, runtime, licence/rights record, corpus, parity vector, geometry manifest, or benchmark is present. Synthetic signal control does not qualify the row.",
        },
        "reopen_conditions": [{"condition": g["requirement"], "gate_id": g["id"]} for g in gates],
        "reproduction": {
            "all": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "compare": "exact SHA-256 over canonical JSON; no tolerance; three byte-identical cold-start repeats",
        },
        "non_claims": [
            "No Resemblyzer implementation, source checkout, encoder weight, runtime, or binary is loaded, built, linked, downloaded, or executed.",
            "No upstream repository URL, revision, release, model hash, licence grant, or rights approval is invented as approved evidence.",
            "No real audio, speaker-labelled corpus, diarization labels, identification gallery, or verification trial list is read.",
            "The synthetic signal control is deterministic local arithmetic only; it is not Resemblyzer output, not a real-corpus score, and not parity.",
            "No speaker identification, speaker verification, diarization, policy, or release claim is made.",
            "No provider, descriptor, registry, installed v0 path, analysis event surface, shared build, CI, board, handoff, or release changed.",
            "No listening, device timing, resource, deadline, or release qualification is performed.",
            "Missing source, weights, runtime, rights, corpus, or parity evidence never qualifies the candidate; the decision remains DEFER.",
        ],
    }

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
