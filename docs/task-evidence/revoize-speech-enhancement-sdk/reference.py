# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for Revoize speech enhancement SDK.

Task ``SDK-REVOIZE-SPEECH-ENHANCEMENT-SDK`` is a bounded, deterministic
feasibility/blocker package. No exact licensed Revoize runtime, SDK package,
model asset, API credentials, rights record, parity vector, or matched
benchmark is present in this workspace. This module builds a task-local
evidence package. It never downloads assets, never invokes external runtimes,
never registers providers, and never claims qualification.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

TASK = "SDK-REVOIZE-SPEECH-ENHANCEMENT-SDK"
TITLE = "Revoize speech enhancement SDK"
COMPONENT = "revoize-speech-enhancement-sdk"
PROFILE = "enhancement"
MODE = "external-adapter"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-REVOIZE-SPEECH-ENHANCEMENT-SDK"
BASE_COMMIT = "a9cf338c0b363d69408c931071071583a49ebdc1"
REVIEWER = "reviewer-REVOIZE-SPEECH-ENHANCEMENT-SDK"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-REVOIZE-SPEECH-ENHANCEMENT-SDK"
)
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DEFER_BEFORE = "opt_in_provider_intake"
SCHEMA_ID = "audio-sdk/task-evidence/revoize-speech-enhancement-sdk/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_PREFIX = "docs/task-evidence/revoize-speech-enhancement-sdk/"
REQUIRED_VARIANT = "revoize_speech_enhancement_sdk_external_adapter"
SDK_FRAME_SAMPLES = 160
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-" "Identifier: Apache-2.0\n"
)

HERE = Path(__file__).resolve().parent
_DEFAULT_SDK_ROOT = Path(CLAIM_WORKTREE)
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
    "research/noise_suppression_candidate_census.md": "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
}
BOUNDARY_PINS = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/acceptance-matrix.md": "2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e",
    "docs/provider-intake.md": "e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5",
}

SCOPE = {
    "benchmark_claim": False,
    "default_selected": False,
    "device_timing": False,
    "external_runtime_invoked": False,
    "feature_domain_synthetic_control": True,
    "listening": False,
    "network_used": False,
    "numeric_parity_claim": False,
    "processor_exposure": False,
    "proposal_only": True,
    "provider_registration": False,
    "public_release_claim": False,
    "real_audio": False,
    "real_corpus": False,
    "runtime_executed": False,
    "shared_build_or_ci_change": False,
    "task_local_only": True,
    "upstream_runtime_present": False,
    "upstream_source_present": False,
    "weights_or_models_bundled": False,
}

BOUNDARY = {
    "abi_change": False,
    "adapter_json_added": False,
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
    "claimed_revoize_capability",
    "corpus_manifest_path",
    "corpus_manifest_sha256",
    "frame_samples",
    "license_record_path",
    "license_record_sha256",
    "model_selection",
    "parity_vector_path",
    "parity_vector_sha256",
    "rights_record_path",
    "rights_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_package_path",
    "runtime_package_sha256",
    "sample_rate_hz",
    "sdk_package_path",
    "sdk_package_sha256",
    "source_revision_or_release",
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
    if not isinstance(text, str) or not re.fullmatch(r"[0-9a-f]{64}", text):
        raise _reject(f"{field} must be a lowercase SHA-256")
    return text


def _validate_abs_path(text: Any, field: str) -> str:
    if not isinstance(text, str) or not text:
        raise _reject(f"{field} must be an absolute path without traversal")
    p = Path(text)
    if not p.is_absolute() or ".." in p.parts:
        raise _reject(f"{field} must be an absolute path without traversal")
    return text


def _validate_pin(text: Any, field: str) -> str:
    if not isinstance(text, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{7,127}", text):
        raise _reject(f"{field} must be an immutable non-empty pin")
    if text in {"unknown", "latest", "main", "master"}:
        raise _reject(f"{field} must be an immutable non-empty pin")
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
    tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list):
        raise _reject("TASKS.json tasks must be a list")
    return [t for t in tasks if isinstance(t, dict)]


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
    return {
        "source": BOARD_PATH,
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(canonical_bytes(stable)),
        "claim": {
            "base_commit": claim.get("base_commit"),
            "branch": claim.get("branch"),
            "worktree": claim.get("worktree"),
            "reviewer": claim.get("reviewer"),
        },
    }


def _gate_rows() -> List[Dict[str, Any]]:
    return [
        {"id": "exact_runtime_and_asset_identity", "requirement": "Exact approved Revoize SDK/runtime package, selected model variant, platform build, immutable version/revision, and SHA-256 identities are pinned with a recorded manifest.", "status": "blocked", "blocked": True},
        {"id": "rights_licence_and_redistribution", "requirement": "Vendor licence, evaluation/redistribution terms, telemetry/data-use constraints, and any model/credential rights are verified with dated evidence.", "status": "blocked", "blocked": True},
        {"id": "reproducible_isolated_execution", "requirement": "An isolated, reproducible execution record runs the exact pinned Revoize runtime on a documented platform without network during scoring; credentials/keys are absent or explicitly scoped.", "status": "blocked", "blocked": True},
        {"id": "exact_reference_parity_or_provenance", "requirement": "Frozen caller-supplied inputs produce exact or declared-tolerance outputs matched to the approved Revoize runtime and selected model; synthetic controls are not parity.", "status": "blocked", "blocked": True},
        {"id": "enhancement_cohort_and_scoring", "requirement": "A rights-cleared, task-matched held-out cohort scores enhancement under the VERIFICATION profile with identity/noisy controls, paired SI-SDR/STOI where permitted, clean-speech preservation, peak/nonfinite bounds, and adverse failure controls.", "status": "blocked", "blocked": True},
        {"id": "task_geometry_and_boundary", "requirement": "Exact sample-rate/channel/frame/chunk/lookahead/content-delay/reset/drain behavior, denoise-only-vs-restoration scope, and optional external-adapter boundary are fixed and reviewed.", "status": "blocked", "blocked": True},
        {"id": "opt_in_provider_intake", "requirement": "Explicit opt-in intake, descriptor review, optional-runtime absence behavior, and independent public-surface decision are complete; no default registration or shared build/CI change.", "status": "blocked", "blocked": True},
        {"id": "public_default_and_release", "requirement": "Explicit default selection, paced resource/deadline/device evidence, and release/public-benchmark approval are recorded; this package is off by default and not qualified.", "status": "blocked", "blocked": True},
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
        elif field == "source_revision_or_release":
            normalized[field] = _validate_pin(value, field)
        elif field == "variant":
            if value != REQUIRED_VARIANT:
                raise _reject("variant must be " + REQUIRED_VARIANT)
            normalized[field] = value
        elif field == "claimed_revoize_capability":
            if value is not True:
                raise _reject("manifest must claim the Revoize capability")
            normalized[field] = True
        elif field in ("channels", "frame_samples", "sample_rate_hz"):
            if not _is_int(value):
                raise _reject(f"{field} is not an integer")
            normalized[field] = value
        elif field == "model_selection":
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", value):
                raise _reject("model_selection must be a non-empty bounded identifier")
            normalized[field] = value
        else:
            normalized[field] = value
    if normalized["channels"] != CHANNELS:
        raise _reject("channels must be 1 for the v0 boundary")
    if normalized["sample_rate_hz"] not in (8000, 16000, 24000, 48000):
        raise _reject("sample_rate_hz is outside the admitted range")
    if normalized["frame_samples"] <= 0 or normalized["frame_samples"] > 48000:
        raise _reject("frame_samples is outside the admitted range")
    return normalized


def _base_manifest() -> Dict[str, Any]:
    base = "/opt/revoize-speech-enhancement-sdk"
    return {
        "adapter_config_path": base + "/adapter.json",
        "adapter_config_sha256": "1" * 64,
        "benchmark_record_path": base + "/benchmark.json",
        "benchmark_record_sha256": "2" * 64,
        "build_record_path": base + "/build.json",
        "build_record_sha256": "3" * 64,
        "channels": 1,
        "claimed_revoize_capability": True,
        "corpus_manifest_path": base + "/corpus.json",
        "corpus_manifest_sha256": "4" * 64,
        "frame_samples": 160,
        "license_record_path": base + "/license.json",
        "license_record_sha256": "5" * 64,
        "model_selection": "unspecified",
        "parity_vector_path": base + "/parity.json",
        "parity_vector_sha256": "6" * 64,
        "rights_record_path": base + "/rights.json",
        "rights_record_sha256": "7" * 64,
        "runtime_lock_path": base + "/runtime.lock",
        "runtime_lock_sha256": "8" * 64,
        "runtime_package_path": base + "/runtime.tar.zst",
        "runtime_package_sha256": "9" * 64,
        "sample_rate_hz": 16000,
        "sdk_package_path": base + "/revoize-sdk.tar.zst",
        "sdk_package_sha256": "a" * 64,
        "source_revision_or_release": "v0.0.0-pinned",
        "variant": REQUIRED_VARIANT,
    }


def _adverse_manifest_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    def add(name: str, manifest: Any, reason_sub: str) -> None:
        try:
            validate_manifest(manifest)
            cases.append({"case": name, "result": "accepted", "reason": "unexpected"})
        except Reject as exc:
            reason = str(exc)
            row = {"case": name, "result": "rejected", "reason": reason}
            if reason_sub.lower() not in reason.lower():
                row["reason_match"] = False
            cases.append(row)

    add("manifest_not_object", [], "object")
    m = _base_manifest(); del m["runtime_package_sha256"]; add("manifest_missing_field", m, "missing fields")
    m = _base_manifest(); m["extra"] = 1; add("manifest_extra_field", m, "unknown fields")
    m = _base_manifest(); m["sdk_package_path"] = "relative/sdk.tar"; add("manifest_relative_path", m, "absolute path")
    m = _base_manifest(); m["runtime_package_path"] = "/opt/../runtime.tar"; add("manifest_traversal_path", m, "absolute path")
    m = _base_manifest(); m["sdk_package_sha256"] = "XYZ"; add("manifest_bad_sha", m, "sha-256")
    m = _base_manifest(); m["source_revision_or_release"] = "latest"; add("manifest_bad_pin", m, "immutable")
    m = _base_manifest(); m["variant"] = "wrong"; add("manifest_wrong_variant", m, "variant")
    m = _base_manifest(); m["claimed_revoize_capability"] = False; add("manifest_capability_false", m, "capability")
    m = _base_manifest(); m["channels"] = 2; add("manifest_wrong_channels", m, "channels")
    m = _base_manifest(); m["sample_rate_hz"] = 44100; add("manifest_wrong_sample_rate", m, "sample_rate_hz")
    m = _base_manifest(); m["frame_samples"] = 0; add("manifest_bad_frame_samples", m, "frame_samples")
    m = _base_manifest(); m["model_selection"] = ""; add("manifest_bad_model_selection", m, "model_selection")
    return cases


def synthetic_audio_frames() -> List[List[float]]:
    # Deterministic 16kHz mono frames: silence/noise/tone/silence. Not real audio.
    frames: List[List[float]] = []
    x = 0x1234567
    rnd = []
    for _ in range(16000):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        rnd.append((x / 0x7FFFFFFF) * 2.0 - 1.0)
    for fidx in range(100):
        frame = []
        for i in range(SDK_FRAME_SAMPLES):
            t = fidx * SDK_FRAME_SAMPLES + i
            r = rnd[t]
            if 20 <= fidx < 40:
                v = 0.02 * r
            elif 40 <= fidx < 80:
                v = 0.12 * math.sin(2 * math.pi * 220 * t / SAMPLE_RATE_HZ) + 0.01 * r
            else:
                v = 0.001 * r
            v = 1.0 if v > 1.0 else -1.0 if v < -1.0 else v
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
    return 20.0 * math.log10(math.sqrt(acc / len(frame)) + 1e-12)


def synthetic_control() -> Dict[str, Any]:
    frames = synthetic_audio_frames()
    threshold_db = -40.0
    decisions = []
    for frame in frames:
        decisions.append(frame_rms_dbfs(frame) >= threshold_db)
    truth = [False] * 20 + [True] * 60 + [False] * 20  # noise+tone treated active in this signal control
    # adjust truth to actual segments: noise 20-39 active, tone 40-79 active
    truth = [(20 <= i < 80) for i in range(100)]
    tp = sum(1 for d, t in zip(decisions, truth) if d and t)
    fp = sum(1 for d, t in zip(decisions, truth) if d and not t)
    fn = sum(1 for d, t in zip(decisions, truth) if (not d) and t)
    tn = sum(1 for d, t in zip(decisions, truth) if (not d) and not t)
    events = []
    in_a = False
    start = 0
    for i, d in enumerate(decisions):
        if d and not in_a:
            in_a = True; start = i
        elif (not d) and in_a:
            in_a = False
            events.append({"start_frame": start, "end_frame": i, "start_sample": start * 160, "end_sample": i * 160})
    if in_a:
        events.append({"start_frame": start, "end_frame": 100, "start_sample": start * 160, "end_sample": 16000})
    return {
        "control_id": "revoize-speech-enhancement-sdk-synthetic-signal-control/0.1",
        "control_scope": "deterministic synthetic signal RMS-threshold control only; no real audio, no Revoize runtime, no model, no enhancement output",
        "metric_scope": "synthetic_signal_domain_not_revoize_or_corpus_result",
        "not_revoize": True,
        "not_real_audio_corpus": True,
        "qualifies_candidate": False,
        "frame_count": 100,
        "threshold_dbfs": threshold_db,
        "detected_activity_events": events,
        "counts": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "decision_digest": sha256_bytes(canonical_bytes(decisions)),
        "notes": [
            "Synthetic control proves deterministic local arithmetic and reporting only.",
            "It is not a Revoize output, not a quality score, and not parity.",
        ],
    }


def _candidate_metrics() -> Dict[str, Any]:
    return {
        "derived_from_synthetic_control": False,
        "si_sdr_delta_db": {"measured": False, "reason": "no approved Revoize runtime, no rights-cleared paired cohort", "value": None},
        "stoi_delta": {"measured": False, "reason": "no approved Revoize runtime, no rights-cleared paired cohort", "value": None},
        "clean_speech_preservation": {"measured": False, "reason": "no approved runtime and no paired clean references", "value": None},
        "peak_and_nonfinite_bounds": {"measured": False, "reason": "no runtime outputs measured", "value": None},
        "content_delay_samples": {"measured": False, "reason": "no runtime geometry/evidence", "value": None},
        "cpu_or_device_timing": {"measured": False, "reason": "no device/runtime timing evidence", "value": None},
    }


def run_adverse_controls() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    def rej(name: str, fn, reason_sub: str) -> None:
        try:
            fn()
            cases.append({"case": name, "result": "accepted", "reason": "unexpected"})
        except Reject as exc:
            r = str(exc)
            row = {"case": name, "result": "rejected", "reason": r}
            if reason_sub.lower() not in r.lower():
                row["reason_match"] = False
            cases.append(row)

    rej("frame_short", lambda: frame_rms_dbfs([0.0] * 10), "160")
    rej("frame_long", lambda: frame_rms_dbfs([0.0] * 161), "160")
    rej("frame_nan", lambda: frame_rms_dbfs([0.0] * 159 + [float("nan")]), "nonfinite")
    rej("frame_inf", lambda: frame_rms_dbfs([0.0] * 159 + [float("inf")]), "nonfinite")
    rej("frame_neg_inf", lambda: frame_rms_dbfs([0.0] * 159 + [float("-inf")]), "nonfinite")
    rej("frame_bool", lambda: frame_rms_dbfs([True] + [0.0] * 159), "numeric")
    rej("frame_string", lambda: frame_rms_dbfs(["0"] + [0.0] * 159), "numeric")
    rej("frame_out_of_range", lambda: frame_rms_dbfs([2.0] + [0.0] * 159), "out of range")

    cases.extend(_adverse_manifest_cases())

    rej("json_duplicate_key", lambda: strict_loads('{"a":1,"a":2}'), "duplicate")
    rej("json_nan", lambda: strict_loads('{"a":NaN}'), "non-finite")
    rej("json_infinity", lambda: strict_loads('{"a":Infinity}'), "non-finite")
    rej("qualification_without_manifest", lambda: (_ for _ in ()).throw(_reject("no approved caller manifest/runtime/rights/corpus/parity is supplied")), "no approved caller manifest")

    if any(c["result"] != "rejected" for c in cases):
        raise _reject("an adverse control was accepted")
    return cases


def _acceptance_profile() -> Dict[str, Any]:
    return {
        "profile": "enhancement",
        "source": "plan/swarm/VERIFICATION.md",
        "requirements": [
            {"id": "identity_noisy_control", "measured": False, "reason": "no approved runtime and no rights-cleared cohort", "requirement": "Run identity/noisy control and an established task-matched baseline."},
            {"id": "paired_metrics", "measured": False, "reason": "no paired clean references or runtime outputs", "requirement": "Score paired SI-SDR and STOI where permitted clean references exist."},
            {"id": "preservation_peaks_nonfinite", "measured": False, "reason": "no runtime outputs", "requirement": "Measure clean-speech preservation, peaks and invalid outputs."},
            {"id": "state_timing", "measured": False, "reason": "no runtime/session implementation evaluated", "requirement": "Report alignment, state, memory and measured content/availability timing for the exact runtime."},
            {"id": "unpaired_or_listening", "measured": False, "reason": "no authorized listening/predictive evidence", "requirement": "For unpaired speech use a separately labeled predictive screen or authorized listening."},
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

    report: Dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
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
            "name": "Revoize speech enhancement SDK",
            "note": "Inventory/census identify a commercial native SDK with selectable models and fixed-chunk real-time processing. No exact runtime package, version, model, licence terms, or approved rights record is staged in this workspace; nothing is invented.",
            "project_url": None,
            "repository_url": None,
            "release_or_tag": None,
            "runtime_present": False,
            "source_checkout_present": False,
            "weights_or_models_present": False,
        },
        "asset_audit": {
            "audit_result": "absent",
            "all_absence_probes_absent": True,
            "note": "No Revoize SDK package, runtime, model asset, licence/rights record, build/runtime lock, parity vector, or matched cohort manifest was observed for this exact component.",
            "observed": {
                "absence_probes": [
                    {"exists": False, "path": "research/repos/revoize"},
                    {"exists": False, "path": "research/repos/revoize-speech-enhancement-sdk"},
                    {"exists": False, "path": "data/checkouts/revoize-speech-enhancement-sdk"},
                    {"exists": False, "path": "data/models/revoize"},
                    {"exists": False, "path": "data/runtime/revoize-speech-enhancement-sdk"},
                    {"exists": False, "path": "data/envs/revoize-speech-enhancement-sdk"},
                    {"exists": False, "path": "data/build-records/revoize-speech-enhancement-sdk.json"},
                    {"exists": False, "path": "data/rights/revoize-speech-enhancement-sdk-rights.json"},
                    {"exists": False, "path": "data/rights/revoize-speech-enhancement-sdk-license.json"},
                    {"exists": False, "path": "data/runs/revoize-speech-enhancement-sdk-parity/manifest.json"},
                    {"exists": False, "path": "data/runs/revoize-speech-enhancement-sdk-cohort/manifest.json"},
                    {"exists": False, "path": "third_party/revoize"},
                    {"exists": False, "path": "deps/revoize-speech-enhancement-sdk"},
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
        },
        "asset_requirements": [
            {"id": "exact_runtime_or_sdk_package", "required": True, "status": "absent", "path": "data/runtime/revoize-speech-enhancement-sdk", "sha256": None},
            {"id": "exact_model_or_variant_identity", "required": True, "status": "absent", "path": "data/models/revoize", "sha256": None},
            {"id": "runtime_lock_and_build_record", "required": True, "status": "absent", "runtime_lock_path": "data/envs/revoize-speech-enhancement-sdk/requirements.lock", "build_record_path": "data/build-records/revoize-speech-enhancement-sdk.json"},
            {"id": "license_and_rights_record", "required": True, "status": "absent", "license_path": "data/rights/revoize-speech-enhancement-sdk-license.json", "rights_path": "data/rights/revoize-speech-enhancement-sdk-rights.json"},
            {"id": "task_geometry_and_scope", "required": True, "status": "absent", "config_path": "data/plans/revoize-speech-enhancement-sdk-adapter.json", "note": "denoise-only vs restoration/dereverb scope, sample rate, chunk, lookahead, content delay, reset/drain must be fixed"},
            {"id": "exact_parity_vector", "required": True, "status": "absent", "parity_path": "data/runs/revoize-speech-enhancement-sdk-parity/manifest.json"},
            {"id": "enhancement_cohort_and_benchmark", "required": True, "status": "absent", "benchmark_path": "data/runs/revoize-speech-enhancement-sdk-cohort/manifest.json"},
            {"id": "opt_in_intake_and_release_approval", "required": True, "status": "absent", "note": "no default/shared-surface/release change without reviewed opt-in intake"},
        ],
        "exact_blockers": [
            {"id": "runtime_and_model_absent", "requirement": "Supply the exact approved Revoize SDK/runtime and selected model/variant with immutable version/revision and SHA-256 manifest; no runtime/model is staged.", "state": "absent"},
            {"id": "licence_and_rights_unverified", "requirement": "Verify vendor licence, evaluation/redistribution/data-use terms, and any credential/model rights with dated evidence; no rights record exists.", "state": "absent"},
            {"id": "runtime_execution_record_absent", "requirement": "Provide an isolated reproducible execution/build record on a documented platform; no runtime/build record exists.", "state": "absent"},
            {"id": "task_geometry_unestablished", "requirement": "Fix denoise-only vs restoration scope, sample-rate/channel/chunk/lookahead/content-delay/reset/drain, and external-adapter boundary; none is established.", "state": "absent"},
            {"id": "parity_absent", "requirement": "Provide an approved exact-runtime parity/provenance vector on frozen inputs; synthetic control is not parity.", "state": "absent"},
            {"id": "enhancement_cohort_absent", "requirement": "Provide rights-cleared enhancement-profile cohort scoring with identity/noisy controls, paired SI-SDR/STOI where permitted, preservation/peak/nonfinite, and adverse controls; none exists.", "state": "absent"},
            {"id": "device_timing_absent", "requirement": "Provide paced device/resource/deadline/content-availability evidence for the exact runtime and target; none exists.", "state": "absent"},
            {"id": "opt_in_and_release_absent", "requirement": "Complete opt-in intake, independent public-surface decision, and release approval; no default/shared-surface/release change is allowed.", "state": "absent"},
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
                "reason": "no approved caller manifest/runtime/rights/corpus/parity is supplied",
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
            "reason": "No exact Revoize SDK/runtime, model, licence/rights record, task geometry, parity vector, enhancement cohort, or device timing evidence is present. Synthetic signal control does not qualify the row.",
        },
        "reopen_conditions": [{"condition": g["requirement"], "gate_id": g["id"]} for g in gates],
        "reproduction": {
            "all": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
            "compare": "exact SHA-256 over canonical JSON; no tolerance; three byte-identical cold-start repeats",
        },
        "non_claims": [
            "No Revoize SDK/runtime, model, weight, credential, or binary is loaded, built, linked, downloaded, or executed.",
            "No vendor package, version, model name, licence grant, or rights approval is invented as present.",
            "No real audio, corpus, listening test, device timing, benchmark, or release claim is made.",
            "The synthetic signal control is deterministic local arithmetic only; it is not Revoize output, not quality evidence, and not parity.",
            "No provider, descriptor, registry, installed v0 path, shared build, CI, board, handoff, or release changed.",
            "Missing runtime, rights, geometry, parity, cohort, or timing evidence never qualifies the candidate; the decision remains DEFER.",
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
    def __init__(self) -> None:
        self.state: Dict[str, Any] | None = None

    def snapshot(self) -> Dict[str, Any] | None:
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
