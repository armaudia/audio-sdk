# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for Stream.FM speech enhancement.

Task ``SDK-STREAM-FM-SPEECH-ENHANCEMENT-CHECKPOINT`` is a bounded, deterministic
feasibility/blocker package. A local Stream.FM source checkout is present and
pinned, but no exact pretrained checkpoint bytes, rights-cleared model terms,
locked runtime, parity vector, enhancement cohort, or device timing evidence is
present. This module builds task-local evidence only. It never downloads assets,
never invokes external runtimes, never registers providers, and never claims
qualification.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

TASK = "SDK-STREAM-FM-SPEECH-ENHANCEMENT-CHECKPOINT"
TITLE = "Stream.FM speech-enhancement checkpoint"
COMPONENT = "stream-fm-speech-enhancement-checkpoint"
PROFILE = "enhancement"
MODE = "feasibility"
REPOSITORY = "audio-sdk"
BRANCH = "swarm/SDK-STREAM-FM-SPEECH-ENHANCEMENT-CHECKPOINT"
BASE_COMMIT = "14af17740bf8c571f9a985c88fd56f5b5b8e8ae8"
REVIEWER = "reviewer-STREAM-FM-SPEECH-ENHANCEMENT-CHECKPOINT"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-STREAM-FM-SPEECH-ENHANCEMENT-CHECKPOINT"
)
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DEFER_BEFORE = "opt_in_provider_intake"
SCHEMA_ID = "audio-sdk/task-evidence/stream-fm-speech-enhancement-checkpoint/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
BOARD_PATH = "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_PREFIX = "docs/task-evidence/stream-fm-speech-enhancement-checkpoint/"
REQUIRED_VARIANT = "streamfm_speech_enhancement_checkpoint_external_reference"
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
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/noise_suppression_candidate_census.md": "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    "data/checkouts/StreamFM/LICENSE": "8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef",
    "data/checkouts/StreamFM/README.md": "add959204bf4f7c69e00e65a88898533bcde0ae1558e9ea25e8d9e3fb7ad6014",
    "data/checkouts/StreamFM/config/streamfm_se_predgen.yaml": "965e76a643efe575983fa75c9540ad3f30547aae19fa0ed239f25295d1466a45",
    "data/checkouts/StreamFM/config/streamfm_se_predictor.yaml": "3ea1b97f152ea87006f3c8022784747f0d977f32337f1048690164927e3406fd",
    "data/checkouts/StreamFM/requirements.txt": "e8ed8ec3c71de0e03d40a778589de6122df3649fc72f9a0f343ad53e95d3fd88",
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
    "upstream_source_present": True,
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
    "benchmark_record_path",
    "benchmark_record_sha256",
    "build_record_path",
    "build_record_sha256",
    "channels",
    "checkpoint_path",
    "checkpoint_sha256",
    "claimed_streamfm_capability",
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
    "sample_rate_hz",
    "source_revision",
    "source_tree_sha256",
    "variant",
)
MANIFEST_PATH_FIELDS = tuple(f for f in MANIFEST_FIELDS if f.endswith("_path"))
MANIFEST_SHA_FIELDS = tuple(f for f in MANIFEST_FIELDS if f.endswith("_sha256"))

UPSTREAM = {
    "implementation_present": True,
    "license_spdx_reported": "AGPL-3.0-only",
    "license_verified": False,
    "name": "Stream.FM / MelFlow speech restoration",
    "project_page": "https://sp-uhh.github.io/streamfm_examples/",
    "repository_url": "https://github.com/sp-uhh/streamfm.git",
    "source_checkout_present": True,
    "source_revision": "ab2700c1154acc5c2ce67a5344182028336413f5",
    "weights_or_models_present": False,
    "weights_source_reported": "https://drive.google.com/drive/folders/1u2QKjGAdxblQVV8-qmifSM9AwhT86LER?usp=sharing",
}

STABLE_TASK_SHA256 = "f114700359775aa3631e5fc5c9ed8cafd0eaa8494ad0634028f218dcea000ced"


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
    if text in {"unknown", "latest", "main", "master", "HEAD"}:
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
        raise _reject(f"non-canonical JSON value: {exc}") from exc


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def strict_loads(text: str) -> Any:
    def _reject_const(x: str) -> Any:
        raise _reject(f"non-finite JSON: {x}")

    def _object_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in pairs:
            if k in out:
                raise _reject(f"duplicate JSON key: {k}")
            out[k] = v
        return out

    try:
        value = json.loads(text, parse_constant=_reject_const, object_pairs_hook=_object_pairs)
    except json.JSONDecodeError as exc:
        raise _reject(f"invalid JSON: {exc}") from exc

    def _walk(v: Any) -> Any:
        if isinstance(v, dict):
            out: Dict[str, Any] = {}
            for k, vv in v.items():
                if not isinstance(k, str):
                    raise _reject("object key must be string")
                out[k] = _walk(vv)
            return out
        if isinstance(v, list):
            return [_walk(x) for x in v]
        if isinstance(v, bool) or v is None or isinstance(v, str):
            return v
        if isinstance(v, int):
            return int(v)
        if isinstance(v, float):
            if not math.isfinite(v):
                raise _reject("non-finite float")
            return float(v)
        raise _reject(f"unsupported JSON type: {type(v).__name__}")

    return _walk(value)


def _base_manifest() -> Dict[str, Any]:
    return {
        "benchmark_record_path": "/opt/streamfm/benchmark.json",
        "benchmark_record_sha256": "0" * 64,
        "build_record_path": "/opt/streamfm/build.json",
        "build_record_sha256": "1" * 64,
        "channels": CHANNELS,
        "checkpoint_path": "/opt/streamfm/streamfm_se_predgen.ckpt",
        "checkpoint_sha256": "2" * 64,
        "claimed_streamfm_capability": True,
        "corpus_manifest_path": "/opt/streamfm/corpus.json",
        "corpus_manifest_sha256": "3" * 64,
        "frame_samples": SDK_FRAME_SAMPLES,
        "license_record_path": "/opt/streamfm/license.json",
        "license_record_sha256": "4" * 64,
        "model_selection": "streamfm_se_predgen",
        "parity_vector_path": "/opt/streamfm/parity.json",
        "parity_vector_sha256": "5" * 64,
        "rights_record_path": "/opt/streamfm/rights.json",
        "rights_record_sha256": "6" * 64,
        "runtime_lock_path": "/opt/streamfm/runtime.lock",
        "runtime_lock_sha256": "7" * 64,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "source_revision": "ab2700c1154acc5c2ce67a5344182028336413f5",
        "source_tree_sha256": "8" * 64,
        "variant": REQUIRED_VARIANT,
    }


def validate_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise _reject("manifest must be an object")
    keys = set(manifest.keys())
    required = set(MANIFEST_FIELDS)
    missing = sorted(required - keys)
    extra = sorted(keys - required)
    if missing:
        raise _reject("manifest missing fields: " + ", ".join(missing))
    if extra:
        raise _reject("manifest has unknown fields: " + ", ".join(extra))

    out: Dict[str, Any] = {}
    for field in MANIFEST_PATH_FIELDS:
        out[field] = _validate_abs_path(manifest[field], field)
    for field in MANIFEST_SHA_FIELDS:
        out[field] = _validate_sha256(manifest[field], field)

    out["claimed_streamfm_capability"] = manifest["claimed_streamfm_capability"]
    if out["claimed_streamfm_capability"] is not True:
        raise _reject("manifest must claim the Stream.FM capability")

    out["channels"] = manifest["channels"]
    if not _is_int(out["channels"]) or out["channels"] != CHANNELS:
        raise _reject("channels must be 1 for the v0 boundary")

    out["sample_rate_hz"] = manifest["sample_rate_hz"]
    if not _is_int(out["sample_rate_hz"]) or out["sample_rate_hz"] not in {8000, 16000, 24000, 48000}:
        raise _reject("sample_rate_hz is outside the admitted range")

    out["frame_samples"] = manifest["frame_samples"]
    if not _is_int(out["frame_samples"]) or out["frame_samples"] <= 0 or out["frame_samples"] > 48000:
        raise _reject("frame_samples is outside the admitted range")

    out["model_selection"] = manifest["model_selection"]
    if not isinstance(out["model_selection"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", out["model_selection"]):
        raise _reject("model_selection must be a non-empty bounded identifier")

    out["variant"] = manifest["variant"]
    if out["variant"] != REQUIRED_VARIANT:
        raise _reject(f"variant must be {REQUIRED_VARIANT}")

    out["source_revision"] = _validate_pin(manifest["source_revision"], "source_revision")
    out["source_tree_sha256"] = _validate_sha256(manifest["source_tree_sha256"], "source_tree_sha256")
    return out


def validate_frame(frame: Sequence[Any]) -> List[float]:
    if not isinstance(frame, (list, tuple)):
        raise _reject("frame must be a list")
    if len(frame) != SDK_FRAME_SAMPLES:
        raise _reject("frame length must be 160")
    out: List[float] = []
    for sample in frame:
        if isinstance(sample, bool) or not isinstance(sample, (int, float, Decimal)):
            raise _reject("frame sample must be numeric")
        try:
            value = float(sample)
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise _reject(f"frame sample is not numeric: {exc}") from exc
        if not math.isfinite(value):
            raise _reject("nonfinite_frame")
        if value < -1.0 or value > 1.0:
            raise _reject("frame sample out of range")
        out.append(value)
    return out


def synthetic_control() -> Dict[str, Any]:
    # Deterministic synthetic signal-control only. Not Stream.FM output.
    threshold_dbfs = -40.0
    threshold = 10.0 ** (threshold_dbfs / 20.0)
    active = list(range(20, 80))
    decisions: List[int] = []
    tp = tn = fp = fn = 0
    for frame_idx in range(100):
        is_active = frame_idx in active
        amp = 0.05 if is_active else 0.0001
        frame = [amp * math.sin(2.0 * math.pi * (k + 1) * (frame_idx + 1) / 321.0) for k in range(SDK_FRAME_SAMPLES)]
        rms = math.sqrt(sum(x * x for x in frame) / len(frame))
        detected = rms >= threshold
        decisions.append(1 if detected else 0)
        if detected and is_active:
            tp += 1
        elif detected and not is_active:
            fp += 1
        elif (not detected) and (not is_active):
            tn += 1
        else:
            fn += 1
    digest = sha256_bytes((",".join(str(d) for d in decisions)).encode("ascii"))
    return {
        "control_id": "stream-fm-speech-enhancement-checkpoint-synthetic-signal-control/0.1",
        "control_scope": "deterministic synthetic signal RMS-threshold control only; no real audio, no Stream.FM runtime, no checkpoint, no enhancement output",
        "counts": {"fn": fn, "fp": fp, "tn": tn, "tp": tp},
        "decision_digest": digest,
        "detected_activity_events": [{"end_frame": 80, "end_sample": 12800, "start_frame": 20, "start_sample": 3200}],
        "frame_count": 100,
        "metric_scope": "synthetic_signal_domain_not_streamfm_or_corpus_result",
        "not_real_audio_corpus": True,
        "not_streamfm": True,
        "notes": [
            "Synthetic control proves deterministic local arithmetic and reporting only.",
            "It is not a Stream.FM output, not a quality score, and not parity.",
        ],
        "qualifies_candidate": False,
        "threshold_dbfs": threshold_dbfs,
    }


def _gate_rows() -> List[Dict[str, Any]]:
    return [
        {"blocked": True, "id": "exact_runtime_and_asset_identity", "requirement": "Exact approved Stream.FM source revision, selected SE checkpoint variant, model config, byte counts, and SHA-256 identities are pinned with a recorded manifest.", "status": "blocked"},
        {"blocked": True, "id": "rights_licence_and_redistribution", "requirement": "AGPL-3.0 source obligations, checkpoint/model terms, training-data terms, corpus rights, and redistribution/evaluation constraints are verified with dated evidence.", "status": "blocked"},
        {"blocked": True, "id": "reproducible_isolated_execution", "requirement": "An isolated, reproducible execution record runs the exact pinned Stream.FM runtime/checkpoint on a documented platform without network during scoring; no undeclared download occurs.", "status": "blocked"},
        {"blocked": True, "id": "exact_reference_parity_or_provenance", "requirement": "Frozen caller-supplied inputs produce exact or declared-tolerance outputs matched to the approved Stream.FM checkpoint/runtime; synthetic controls are not parity.", "status": "blocked"},
        {"blocked": True, "id": "enhancement_cohort_and_scoring", "requirement": "A rights-cleared, task-matched held-out cohort scores enhancement under the VERIFICATION profile with identity/noisy controls, paired SI-SDR/STOI where permitted, clean-speech preservation, peak/nonfinite bounds, and adverse failure controls.", "status": "blocked"},
        {"blocked": True, "id": "task_geometry_and_boundary", "requirement": "Exact sample-rate/channel/frame/chunk/lookahead/content-delay/reset/drain behavior, SE-task scope, and optional external-adapter boundary are fixed and reviewed; installed v0 16 kHz mono 160-sample geometry is preserved unless a separately versioned contract is accepted.", "status": "blocked"},
        {"blocked": True, "id": "opt_in_provider_intake", "requirement": "Explicit opt-in intake, descriptor review, optional-runtime absence behavior, and independent public-surface decision are complete; no default registration or shared build/CI change.", "status": "blocked"},
        {"blocked": True, "id": "public_default_and_release", "requirement": "Explicit default selection, paced resource/deadline/device evidence, and release/public-benchmark approval are recorded; this package is off by default and not qualified.", "status": "blocked"},
    ]


def _exact_blockers() -> List[Dict[str, Any]]:
    return [
        {"id": "checkpoint_and_weights_absent", "requirement": "Supply exact approved Stream.FM SE checkpoint bytes, config, immutable revision/source identity, and SHA-256 manifest; no checkpoint weights are staged locally.", "state": "absent"},
        {"id": "licence_and_rights_unverified", "requirement": "Verify AGPL-3.0 source obligations, checkpoint/model distribution terms, training-data terms, and corpus/output rights with dated evidence; no rights record exists.", "state": "absent"},
        {"id": "runtime_execution_record_absent", "requirement": "Provide an isolated reproducible execution/build record on a documented platform; no locked runtime/execution record exists.", "state": "absent"},
        {"id": "task_geometry_unestablished", "requirement": "Fix SE task scope, sample-rate/channel/chunk/lookahead/content-delay/reset/drain, and external-adapter boundary; no accepted geometry record exists.", "state": "absent"},
        {"id": "parity_absent", "requirement": "Provide an approved exact-runtime parity/provenance vector on frozen inputs; synthetic control is not parity.", "state": "absent"},
        {"id": "enhancement_cohort_absent", "requirement": "Provide rights-cleared enhancement-profile cohort scoring with identity/noisy controls, paired SI-SDR/STOI where permitted, preservation/peak/nonfinite, and adverse controls; none exists.", "state": "absent"},
        {"id": "device_timing_absent", "requirement": "Provide paced device/resource/deadline/content-availability evidence for the exact runtime and target; none exists.", "state": "absent"},
        {"id": "opt_in_and_release_absent", "requirement": "Complete opt-in intake, independent public-surface decision, and release approval; no default/shared-surface/release change is allowed.", "state": "absent"},
    ]


def task_row_identity() -> Dict[str, Any]:
    stable = {
        "id": TASK,
        "title": TITLE,
        "mode": MODE,
        "component": COMPONENT,
        "repository": REPOSITORY,
        "deliverable": "Verify runnable source, exact assets, permitted scope, task geometry and matched evidence. Then reproduce the exact model/runtime as a caller-supplied-asset reference and add an opt-in SDK adapter once its prerequisites pass. Record a concrete blocker if feasibility fails.",
        "acceptance": "Apply the enhancement acceptance profile; record exact scope, evidence, failure/control results, and remaining release gates. A readiness conclusion with an exact external blocker is an accepted investigation handoff; it does not close the conditional implementation.",
        "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
        "evidence": ["research/noise_suppression_candidate_census.md"],
        "write_scope": ["SDK provider, tool or evidence directory for stream-fm-speech-enhancement-checkpoint and its own fixtures"],
    }
    digest = sha256_bytes(canonical_bytes(stable))
    if digest != STABLE_TASK_SHA256:
        raise _reject(f"stable task row digest mismatch: {digest}")
    return {
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "reviewer": REVIEWER,
            "worktree": CLAIM_WORKTREE,
        },
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "source": BOARD_PATH,
        "stable_fields": stable,
        "stable_sha256": digest,
        "whole_file_hashed": False,
    }


def verify_document_pins() -> None:
    for rel, expected in SOURCE_PINS.items():
        path = SOURCE_ROOT / rel
        if not path.is_file():
            raise _reject(f"missing source pin: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            raise _reject(f"source pin mismatch: {rel}")
    for rel, expected in BOUNDARY_PINS.items():
        path = SDK_ROOT / rel
        if not path.is_file():
            raise _reject(f"missing boundary pin: {rel}")
        actual = sha256_file(path)
        if actual != expected:
            raise _reject(f"boundary pin mismatch: {rel}")


def build_report() -> Dict[str, Any]:
    verify_document_pins()
    identity = task_row_identity()
    control = synthetic_control()
    blockers = _exact_blockers()
    gates = _gate_rows()
    adverse = adverse_cases()
    report = {
        "acceptance_profile": {
            "profile": PROFILE,
            "requirements": [
                {"id": "identity_noisy_control", "measured": False, "reason": "no approved runtime/checkpoint and no rights-cleared cohort", "requirement": "Run identity/noisy control and an established task-matched baseline."},
                {"id": "paired_metrics", "measured": False, "reason": "no paired clean references or runtime outputs", "requirement": "Score paired SI-SDR and STOI where permitted clean references exist."},
                {"id": "preservation_peaks_nonfinite", "measured": False, "reason": "no runtime outputs", "requirement": "Measure clean-speech preservation, peaks and invalid outputs."},
                {"id": "state_timing", "measured": False, "reason": "no runtime/session implementation evaluated", "requirement": "Report alignment, state, memory and measured content/availability timing for the exact runtime."},
                {"id": "unpaired_or_listening", "measured": False, "reason": "no authorized listening/predictive evidence", "requirement": "For unpaired speech use a separately labeled predictive screen or authorized listening."},
            ],
            "source": "plan/swarm/VERIFICATION.md",
        },
        "asset_audit": {
            "all_absence_probes_absent": True,
            "audit_result": "source_present_weights_runtime_absent",
            "benchmark_record_present": False,
            "build_record_present": False,
            "checkpoint_weights_present": False,
            "corpus_manifest_present": False,
            "license_record_present": False,
            "note": "A local Stream.FM source checkout is present at the pinned revision. No pretrained SE checkpoint weights, rights record, runtime lock, parity vector, or matched cohort manifest was observed for this exact component.",
            "observed": {
                "absence_probes": [
                    {"exists": False, "path": "data/models/streamfm"},
                    {"exists": False, "path": "data/checkpoints/streamfm"},
                    {"exists": False, "path": "data/runtime/streamfm-speech-enhancement-checkpoint"},
                    {"exists": False, "path": "data/envs/streamfm-speech-enhancement-checkpoint"},
                    {"exists": False, "path": "data/build-records/streamfm-speech-enhancement-checkpoint.json"},
                    {"exists": False, "path": "data/rights/streamfm-speech-enhancement-checkpoint-rights.json"},
                    {"exists": False, "path": "data/rights/streamfm-speech-enhancement-checkpoint-license.json"},
                    {"exists": False, "path": "data/runs/streamfm-speech-enhancement-checkpoint-parity/manifest.json"},
                    {"exists": False, "path": "data/runs/streamfm-speech-enhancement-checkpoint-cohort/manifest.json"},
                ],
                "source_checkout": {
                    "exists": True,
                    "path": "data/checkouts/StreamFM",
                    "revision": UPSTREAM["source_revision"],
                },
            },
            "parity_manifest_present": False,
            "rights_record_present": False,
            "runtime_lock_present": False,
            "runtime_present": False,
            "source_checkout_present": True,
        },
        "asset_requirements": [
            {"id": "exact_checkpoint_weights", "path": "data/checkpoints/streamfm", "required": True, "sha256": None, "status": "absent"},
            {"build_record_path": "data/build-records/streamfm-speech-enhancement-checkpoint.json", "id": "runtime_lock_and_build_record", "required": True, "runtime_lock_path": "data/envs/streamfm-speech-enhancement-checkpoint/requirements.lock", "status": "absent"},
            {"id": "license_and_rights_record", "license_path": "data/rights/streamfm-speech-enhancement-checkpoint-license.json", "required": True, "rights_path": "data/rights/streamfm-speech-enhancement-checkpoint-rights.json", "status": "absent"},
            {"config_path": "data/plans/streamfm-speech-enhancement-checkpoint-adapter.json", "id": "task_geometry_and_scope", "note": "SE scope, sample rate, chunk, lookahead, content delay, reset/drain, and SDK boundary must be fixed", "required": True, "status": "absent"},
            {"id": "exact_parity_vector", "parity_path": "data/runs/streamfm-speech-enhancement-checkpoint-parity/manifest.json", "required": True, "status": "absent"},
            {"benchmark_path": "data/runs/streamfm-speech-enhancement-checkpoint-cohort/manifest.json", "id": "enhancement_cohort_and_benchmark", "required": True, "status": "absent"},
            {"id": "opt_in_intake_and_release_approval", "note": "no default/shared-surface/release change without reviewed opt-in intake", "required": True, "status": "absent"},
        ],
        "base_commit": BASE_COMMIT,
        "boundary": dict(BOUNDARY),
        "boundary_pins": dict(BOUNDARY_PINS),
        "branch": BRANCH,
        "candidate_metrics": {
            "clean_speech_preservation": {"measured": False, "reason": "no approved runtime/checkpoint and no paired clean references", "value": None},
            "content_delay_samples": {"measured": False, "reason": "no runtime geometry/evidence", "value": None},
            "cpu_or_device_timing": {"measured": False, "reason": "no device/runtime timing evidence", "value": None},
            "derived_from_synthetic_control": False,
            "peak_and_nonfinite_bounds": {"measured": False, "reason": "no runtime outputs measured", "value": None},
            "si_sdr_delta_db": {"measured": False, "reason": "no approved Stream.FM runtime/checkpoint, no rights-cleared paired cohort", "value": None},
            "stoi_delta": {"measured": False, "reason": "no approved Stream.FM runtime/checkpoint, no rights-cleared paired cohort", "value": None},
        },
        "component": COMPONENT,
        "controls": {
            "adverse": adverse,
            "adverse_case_count": len(adverse),
            "all_adverse_rejected": True,
            "qualification_gate_without_manifest": {
                "qualification": QUALIFICATION,
                "qualifies": False,
                "reason": "no approved caller manifest/runtime/checkpoint/rights/corpus/parity is supplied",
            },
            "structural_manifest_validation_is_not_qualification": True,
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": blockers,
        "gates": gates,
        "generated_by": "reference.py",
        "mode": MODE,
        "mutable_provenance": {
            "gate": False,
            "note": "Board status is mutable and the full board file is never hashed. Only stable linked-row identity is gated in task_row_identity.",
            "path": BOARD_PATH,
        },
        "non_claims": [
            "No Stream.FM checkpoint weights, model asset, or external runtime is downloaded, loaded, built, linked, or executed.",
            "No vendor/model licence grant or rights approval is invented as present; AGPL-3.0 source obligations remain unresolved for distribution use.",
            "No real audio, corpus, listening test, device timing, benchmark, or release claim is made.",
            "The synthetic signal control is deterministic local arithmetic only; it is not Stream.FM output, not quality evidence, and not parity.",
            "No provider, descriptor, registry, installed v0 path, shared build, CI, board, handoff, or release changed.",
            "Missing checkpoint, rights, geometry, parity, cohort, or timing evidence never qualifies the candidate; the decision remains DEFER.",
        ],
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": {
            "candidate_qualified": False,
            "corpus_present": False,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "evidence_status": EVIDENCE_STATUS,
            "implementation_present": False,
            "no_missing_result_qualifies_candidate": True,
            "parity_present": False,
            "proposal_only": True,
            "qualification_status": QUALIFICATION,
            "reason": "Stream.FM source is pinned locally, but no exact checkpoint weights, rights record, locked runtime execution, task geometry, parity vector, enhancement cohort, or device timing evidence is present. Synthetic signal control does not qualify the row.",
            "release_qualification_present": False,
            "runtime_invoked": False,
            "status": QUALIFICATION,
            "synthetic_control_is_not_candidate_evidence": True,
        },
        "qualification_status": QUALIFICATION,
        "reopen_conditions": [{"condition": g["requirement"], "gate_id": g["id"]} for g in gates],
        "repository": REPOSITORY,
        "reproduction": {
            "all": "PYTHONDONTWRITEBYTECODE=1 python3 run.py all",
            "compare": "exact SHA-256 over canonical JSON; no tolerance; three byte-identical cold-start repeats",
            "tests": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
            "verify": "PYTHONDONTWRITEBYTECODE=1 python3 verify.py",
        },
        "reviewer": REVIEWER,
        "schema_id": SCHEMA_ID,
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "synthetic_control": control,
        "task_id": TASK,
        "task_row_identity": identity,
        "title": TITLE,
        "upstream_identity": dict(UPSTREAM),
        "worktree": CLAIM_WORKTREE,
    }
    _validate_report_invariants(report)
    return report


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report)


def _validate_report_invariants(report: Dict[str, Any]) -> None:
    if report["decision"] != DECISION:
        raise _reject("report decision changed")
    if report["qualification_status"] != QUALIFICATION:
        raise _reject("report qualification changed")
    if report["status"] != STATUS:
        raise _reject("report status changed")
    if report["evidence_status"] != EVIDENCE_STATUS:
        raise _reject("report evidence status changed")
    q = report["qualification"]
    if q["candidate_qualified"] is not False or q["status"] != QUALIFICATION or q["qualification_status"] != QUALIFICATION:
        raise _reject("report claims qualification")
    if not q["no_missing_result_qualifies_candidate"]:
        raise _reject("missing-result rule missing")
    if not q["synthetic_control_is_not_candidate_evidence"]:
        raise _reject("synthetic rule missing")
    if len(report["gates"]) != 8 or not all(g["blocked"] and g["status"] == "blocked" for g in report["gates"]):
        raise _reject("gate invariant failed")
    if len(report["exact_blockers"]) != 8:
        raise _reject("blocker count changed")
    if report["synthetic_control"]["qualifies_candidate"] is not False:
        raise _reject("synthetic control qualifies")
    for k, v in report["scope"].items():
        if k in {"feature_domain_synthetic_control", "proposal_only", "task_local_only", "upstream_source_present"}:
            if v is not True:
                raise _reject(f"scope flag should be true: {k}")
        elif v is not False:
            raise _reject(f"scope flag should be false: {k}")
    for k, v in report["boundary"].items():
        if v is not False:
            raise _reject(f"boundary flag should be false: {k}")
    if BOARD_PATH in report["source_pins"] or BOARD_PATH in report["boundary_pins"]:
        raise _reject("mutable board pinned")


def adverse_cases() -> List[Dict[str, str]]:
    cases: List[Dict[str, str]] = []

    def add(case: str, fn: Any) -> None:
        try:
            fn()
        except Reject as exc:
            cases.append({"case": case, "reason": str(exc), "result": "rejected"})
            return
        raise _reject(f"adverse case was accepted: {case}")

    add("frame_short", lambda: validate_frame([0.0] * 159))
    add("frame_long", lambda: validate_frame([0.0] * 161))
    add("frame_nan", lambda: validate_frame([0.0] * 159 + [float("nan")]))
    add("frame_inf", lambda: validate_frame([0.0] * 159 + [float("inf")]))
    add("frame_neg_inf", lambda: validate_frame([0.0] * 159 + [float("-inf")]))
    add("frame_bool", lambda: validate_frame([True] + [0.0] * 159))
    add("frame_string", lambda: validate_frame(["0.1"] + [0.0] * 159))  # type: ignore[list-item]
    add("frame_out_of_range", lambda: validate_frame([1.5] + [0.0] * 159))
    add("manifest_not_object", lambda: validate_manifest([]))
    base = _base_manifest()
    bad = dict(base); bad.pop("checkpoint_sha256")
    add("manifest_missing_field", lambda: validate_manifest(bad))
    bad = dict(base); bad["extra"] = 1
    add("manifest_extra_field", lambda: validate_manifest(bad))
    bad = dict(base); bad["checkpoint_path"] = "relative.ckpt"
    add("manifest_relative_path", lambda: validate_manifest(bad))
    bad = dict(base); bad["runtime_lock_path"] = "/opt/../runtime.lock"
    add("manifest_traversal_path", lambda: validate_manifest(bad))
    bad = dict(base); bad["checkpoint_sha256"] = "XYZ"
    add("manifest_bad_sha", lambda: validate_manifest(bad))
    bad = dict(base); bad["source_revision"] = "latest"
    add("manifest_bad_pin", lambda: validate_manifest(bad))
    bad = dict(base); bad["variant"] = "wrong"
    add("manifest_wrong_variant", lambda: validate_manifest(bad))
    bad = dict(base); bad["claimed_streamfm_capability"] = False
    add("manifest_capability_false", lambda: validate_manifest(bad))
    bad = dict(base); bad["channels"] = 2
    add("manifest_wrong_channels", lambda: validate_manifest(bad))
    bad = dict(base); bad["sample_rate_hz"] = 22050
    add("manifest_wrong_sample_rate", lambda: validate_manifest(bad))
    bad = dict(base); bad["frame_samples"] = 0
    add("manifest_bad_frame_samples", lambda: validate_manifest(bad))
    bad = dict(base); bad["model_selection"] = ""
    add("manifest_bad_model_selection", lambda: validate_manifest(bad))
    add("json_duplicate_key", lambda: strict_loads('{"a":1,"a":2}'))
    add("json_nan", lambda: strict_loads('[NaN]'))
    add("json_infinity", lambda: strict_loads('[Infinity]'))
    add("qualification_without_manifest", lambda: (_ for _ in ()).throw(_reject("no approved caller manifest/runtime/checkpoint/rights/corpus/parity is supplied")))
    return cases
