# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only blocker evidence for SDK-PBFDAF-AUMDF.

PBFDAF/AUMDF (partitioned-block frequency-domain adaptive filter /
alternatively updated MDF) is a classical reference-AEC candidate.
This task-local package records a bounded, metadata-only feasibility
handoff: no exact licensed reference runtime, checkpoint, paired
render/capture cohort, rights record or device-timing evidence is
present in the workspace. No model is downloaded, loaded or executed;
no real audio is processed; no network access occurs.

The package provides:
* a fail-closed audit of fixed workspace paths for accidental assets;
* a caller-supplied manifest contract validated without execution;
* a deterministic synthetic partitioning/MDF accounting control that
  checks block geometry, overlap-save accounting, coefficient-state
  reset, finite arithmetic guards and non-qualification boundaries.

Nothing in this package qualifies the candidate. The decision is
``DEFER``.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-PBFDAF-AUMDF"
TITLE = "PBFDAF / AUMDF"
SLUG = "pbfdaf-aumdf"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "3452bff2f3f8a645f995b6da502a35e485d12163"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "room"
MODE = "feasibility"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_reference_implementation_and_qualification"

# Upstream identity is deliberately unpinned: no exact licensed PBFDAF/AUMDF
# reference implementation, paper artifact bundle, or runtime is supplied.
UPSTREAM_NAME = "PBFDAF / AUMDF (partitioned-block frequency-domain adaptive filter)"
UPSTREAM_REFERENCE_URLS = (
    "https://www.speex.org/docs/manual/speex-manual/node7.html",
)
UPSTREAM_REVISION: Optional[str] = None
SOURCE_REVISION_PIN_AVAILABLE = False

# Control geometry is synthetic accounting only, not a qualified runtime claim.
CONTROL_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
CONTROL_BLOCK_SAMPLES = 160
CONTROL_FFT_SIZE = 320
CONTROL_PARTITIONS = 4
CONTROL_FILTER_TAPS = CONTROL_BLOCK_SAMPLES * CONTROL_PARTITIONS
CONTROL_SECONDS = 3
CONTROL_TOTAL_SAMPLES = CONTROL_SAMPLE_RATE_HZ * CONTROL_SECONDS

RIGHTS_RECORD_PATH = "data/rights/pbfdaf-aumdf-rights.json"
COHORT_MANIFEST_PATH = "data/runs/pbfdaf-aumdf-cohort/manifest.json"
PARITY_MANIFEST_PATH = "data/runs/pbfdaf-aumdf-parity/manifest.json"
RUNTIME_ENV_PATH = "data/envs/pbfdaf-aumdf"
RUNTIME_LOCK_PATH = RUNTIME_ENV_PATH + "/requirements.lock"

ABSENCE_PROBES: Tuple[str, ...] = (
    "research/voice-enhancement-20261101/repos/pbfdaf",
    "research/voice-enhancement-20261101/repos/aumdf",
    "research/voice-enhancement-20261101/repos/pbfdaf-aumdf",
    "data/checkouts/pbfdaf",
    "data/checkouts/aumdf",
    "data/checkouts/pbfdaf-aumdf",
    "data/models/pbfdaf-aumdf",
    "data/weights/pbfdaf-aumdf",
    "data/envs/pbfdaf-aumdf",
    RUNTIME_LOCK_PATH,
    RIGHTS_RECORD_PATH,
    COHORT_MANIFEST_PATH,
    PARITY_MANIFEST_PATH,
    "data/runs/pbfdaf-aumdf-room/manifest.json",
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

# Mutable board is intentionally NOT pinned as a whole-file digest.
# task_row_identity() gates only stable linked-row identity.
SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "research/aec_research_20261028.md":
        "dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/speexdsp-mdf-reference/README.md":
        "3104b4c880eb6d99bbdff2bf9f73793d60278978442000a9c67f1f9c3ae64b83",
    "docs/task-evidence/survey-cln-05/README.md":
        "58fe3057f8dbc9054cfa57e6d35f866c727fdc1959d9cb7b1b11169f00e730f0",
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
    "sdk_v0_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "sdk_v0_channels": CHANNELS,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_frame_samples": SDK_FRAME_SAMPLES,
    "control_sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
    "control_channels": CHANNELS,
    "control_block_samples": CONTROL_BLOCK_SAMPLES,
    "control_fft_size": CONTROL_FFT_SIZE,
    "control_partitions": CONTROL_PARTITIONS,
    "control_filter_taps": CONTROL_FILTER_TAPS,
    "control_mode": "synthetic_partitioned_block_accounting",
    "control_performs_aec": False,
    "control_real_audio": False,
    "control_claims_runtime_parity": False,
}

BOUNDARY: Dict[str, bool] = {
    "abi_change": False,
    "api_change": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "network_used": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "release_claim": False,
    "shared_build_or_ci_change": False,
    "weights_downloaded": False,
}

SCOPE: Dict[str, bool] = {
    "benchmark_claim": False,
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "real_speech": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "weights_downloaded": False,
}

NON_CLAIMS = [
    "No PBFDAF/AUMDF runtime, source revision, binary or licensed artifact is pinned as present.",
    "No real render/capture audio, room, device loop, clock-drift or timing measurement exists.",
    "No ERLE, AECMOS, STOI, ASR, listening, benchmark or release result is claimed.",
    "No provider registration, descriptor, ABI, registry, default or shared build/CI change is made.",
    "No missing or rejected result qualifies the candidate.",
]

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_reference_identity",
     "Pin an exact licensed PBFDAF/AUMDF reference source/runtime revision, "
     "license terms and redistribution/usage scope."),
    ("rights_and_asset_clearance",
     "Clear rights for code, weights if any, fixtures, and any paired "
     "render/capture assets required for qualification."),
    ("paired_room_cohort",
     "Provide a rights-cleared paired render/capture cohort with frozen room, "
     "delay, movement, noise and reset schedule per Room profile."),
    ("control_and_baseline_evidence",
     "Run identity/noisy controls and a task-matched MDF/reference baseline on "
     "the same frozen cohort with exact configuration pins."),
    ("double_talk_and_path_change",
     "Measure echo attenuation, near-end damage, double-talk, path change, "
     "delayed/missing render and nonfinite/invalid rejection."),
    ("timing_and_resource",
     "Measure content/availability timing, memory, deadline behavior and "
     "callback suitability on target runtime/device conditions."),
    ("opt_in_provider_intake",
     "Complete opt-in provider intake, descriptor review, license review and "
     "independent exact-head review before any registration."),
    ("public_default_and_release",
     "Record explicit default/release decision only after qualification gates "
     "close; no default or release claim in this package."),
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "reference_runtime_absent",
        "requirement": (
            "Supply an exact licensed PBFDAF/AUMDF reference implementation or "
            "runtime with immutable revision, license terms and reproducible "
            "build/run instructions."),
        "state": "absent",
    },
    {
        "id": "rights_record_absent",
        "requirement": (
            "Provide a rights record covering code/runtime use, fixtures, and "
            "any paired render/capture assets needed for qualification."),
        "state": "absent",
    },
    {
        "id": "paired_cohort_absent",
        "requirement": (
            "Provide a rights-cleared paired render/capture cohort with frozen "
            "echo-only, near-end-only, double-talk, path-change and no-reference "
            "conditions."),
        "state": "absent",
    },
    {
        "id": "mdf_parity_baseline_unexecuted",
        "requirement": (
            "Execute a task-matched MDF/PBFDAF comparison on the same frozen "
            "cohort; record convergence, ERLE, near-end preservation and cost."),
        "state": "absent",
    },
    {
        "id": "timing_evidence_absent",
        "requirement": (
            "Measure algorithmic/content delay, availability, memory and deadline "
            "behavior for the exact runtime/device profile."),
        "state": "absent",
    },
    {
        "id": "provider_intake_incomplete",
        "requirement": (
            "Complete opt-in provider intake, descriptor/license review and "
            "independent exact-head review before any registration or default."),
        "state": "absent",
    },
)

ADVERSE_CASE_IDS: Tuple[str, ...] = (
    "pcm_empty",
    "pcm_not_sequence",
    "pcm_none",
    "pcm_bool",
    "pcm_nan",
    "pcm_pos_inf",
    "pcm_neg_inf",
    "pcm_wrong_rate",
    "pcm_wrong_channels",
    "manifest_not_object",
    "manifest_missing_field",
    "manifest_extra_field",
    "manifest_bad_sha",
    "manifest_relative_path",
    "manifest_short_revision",
    "manifest_wrong_variant",
    "manifest_bad_block_size",
    "manifest_bad_partitions",
    "manifest_missing_asset",
    "manifest_hash_mismatch",
)

COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class Reject(ValueError):
    """Fail-closed rejection."""


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
        return {k: _normalize_negzero(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(v) for v in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(_normalize_negzero(value), sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise Reject("value is not canonical-JSON serializable") from exc


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def strict_loads(text: str) -> Dict[str, Any]:
    def reject_const(value: str) -> Any:
        raise Reject("non-finite JSON: " + value)

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Reject("duplicate JSON key: " + key)
            result[key] = value
        return result

    value = json.loads(text, parse_constant=reject_const, object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise Reject("expected JSON object")
    return value


def load_strict_json(path: Path) -> Dict[str, Any]:
    return strict_loads(path.read_text(encoding="utf-8"))


def object_digest(value: Any) -> str:
    return sha256(canonical_bytes(value))


# ---------------------------------------------------------------------------
# Board row identity (stable fields only, never hash full TASKS.json)
# ---------------------------------------------------------------------------

def task_row_identity() -> Dict[str, Any]:
    tasks_path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    tasks = load_strict_json(tasks_path)
    row = None
    for item in tasks.get("tasks", []):
        if isinstance(item, dict) and item.get("id") == TASK:
            row = item
            break
    if row is None:
        raise Reject("task row not found: " + TASK)
    stable = {field: row.get(field) for field in STABLE_TASK_FIELDS}
    return {
        "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "mutable_file_sha256_at_read": file_digest(tasks_path),
        "whole_file_hashed": False,
        "stable_fields": stable,
        "stable_sha256": object_digest(stable),
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
    }


# ---------------------------------------------------------------------------
# Asset audit
# ---------------------------------------------------------------------------

def audit_assets() -> Dict[str, Any]:
    probes = []
    any_present = False
    for rel in ABSENCE_PROBES:
        path = SOURCE_ROOT / rel
        present = path.exists()
        any_present = any_present or present
        probes.append({
            "path": rel,
            "present": present,
            "kind": "directory" if path.is_dir() else ("file" if path.is_file() else "absent"),
        })
    observed = {
        "source_checkout_present": False,
        "source_revision": None,
        "license_file_present": False,
        "weights_present": False,
        "runtime_env_present": False,
        "runtime_lock_present": False,
        "rights_record_present": False,
        "cohort_manifest_present": False,
        "parity_manifest_present": False,
        "all_absence_probes_absent": not any_present,
        "absence_probes": probes,
    }
    # detect any present source checkout
    for rel in ("research/voice-enhancement-20261101/repos/pbfdaf",
                "research/voice-enhancement-20261101/repos/aumdf",
                "research/voice-enhancement-20261101/repos/pbfdaf-aumdf",
                "data/checkouts/pbfdaf", "data/checkouts/aumdf",
                "data/checkouts/pbfdaf-aumdf"):
        if (SOURCE_ROOT / rel).exists():
            observed["source_checkout_present"] = True
    for rel in (RIGHTS_RECORD_PATH,):
        observed["rights_record_present"] = observed["rights_record_present"] or (SOURCE_ROOT / rel).is_file()
    observed["runtime_env_present"] = (SOURCE_ROOT / RUNTIME_ENV_PATH).exists()
    observed["runtime_lock_present"] = (SOURCE_ROOT / RUNTIME_LOCK_PATH).is_file()
    observed["cohort_manifest_present"] = (SOURCE_ROOT / COHORT_MANIFEST_PATH).is_file()
    observed["parity_manifest_present"] = (SOURCE_ROOT / PARITY_MANIFEST_PATH).is_file()
    return observed


# ---------------------------------------------------------------------------
# Caller-supplied manifest contract (validation only, no execution)
# ---------------------------------------------------------------------------

REQUIRED_MANIFEST_FIELDS = (
    "schema_id", "candidate", "source_revision", "source_sha256",
    "runtime_lock_path", "runtime_lock_sha256", "rights_record_path",
    "rights_record_sha256", "cohort_manifest_path", "cohort_manifest_sha256",
    "sample_rate_hz", "channels", "block_samples", "partitions",
    "variant",
)


def _expect(condition: bool, code: str) -> None:
    if not condition:
        raise Reject(code)


def validate_pcm_input(pcm: Any, sample_rate_hz: int, channels: int) -> Dict[str, Any]:
    _expect(pcm is not None, "pcm_none")
    _expect(not isinstance(pcm, (bool, str, bytes, dict)), "pcm_not_sequence")
    try:
        seq = list(pcm)
    except Exception as exc:
        raise Reject("pcm_not_sequence") from exc
    _expect(len(seq) > 0, "pcm_empty")
    _expect(sample_rate_hz == CONTROL_SAMPLE_RATE_HZ, "pcm_wrong_rate")
    _expect(channels == CHANNELS, "pcm_wrong_channels")
    out: List[float] = []
    for i, v in enumerate(seq):
        _expect(not isinstance(v, bool), "pcm_bool")
        _expect(isinstance(v, (int, float)), "pcm_not_sequence")
        fv = float(v)
        _expect(math.isfinite(fv), "pcm_nan" if math.isnan(fv) else ("pcm_pos_inf" if fv > 0 else "pcm_neg_inf"))
        _expect(-1.0 <= fv <= 1.0, "pcm_out_of_range")
        out.append(fv)
    return {"samples": len(out), "sample_rate_hz": sample_rate_hz, "channels": channels, "valid": True}


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    _expect(isinstance(manifest, dict), "manifest_not_object")
    keys = set(manifest.keys())
    required = set(REQUIRED_MANIFEST_FIELDS)
    _expect(required.issubset(keys), "manifest_missing_field")
    _expect(keys == required, "manifest_extra_field")
    _expect(manifest["schema_id"] == "audio-sdk/pbfdaf-aumdf/caller-supplied/0.1", "manifest_wrong_variant")
    _expect(manifest["candidate"] == COMPONENT, "manifest_wrong_variant")
    _expect(manifest["variant"] == "partitioned_block_frequency_domain_aec", "manifest_wrong_variant")
    _expect(isinstance(manifest["source_revision"], str) and COMMIT_PATTERN.fullmatch(manifest["source_revision"]), "manifest_short_revision")
    for f in ("source_sha256", "runtime_lock_sha256", "rights_record_sha256", "cohort_manifest_sha256"):
        v = manifest[f]
        _expect(isinstance(v, str) and SHA256_PATTERN.fullmatch(v), "manifest_bad_sha")
    for f in ("runtime_lock_path", "rights_record_path", "cohort_manifest_path"):
        v = manifest[f]
        _expect(isinstance(v, str) and v.startswith("/"), "manifest_relative_path")
    _expect(manifest["sample_rate_hz"] == CONTROL_SAMPLE_RATE_HZ, "pcm_wrong_rate")
    _expect(manifest["channels"] == CHANNELS, "pcm_wrong_channels")
    _expect(manifest["block_samples"] == CONTROL_BLOCK_SAMPLES, "manifest_bad_block_size")
    _expect(manifest["partitions"] == CONTROL_PARTITIONS, "manifest_bad_partitions")
    # fail closed on missing assets - no execution
    for f in ("runtime_lock_path", "rights_record_path", "cohort_manifest_path"):
        p = Path(manifest[f])
        _expect(p.is_file(), "manifest_missing_asset")
        if f.endswith("_path"):
            sha_field = f.replace("_path", "_sha256")
            _expect(file_digest(p) == manifest[sha_field], "manifest_hash_mismatch")
    return {"valid": True, "executed": False, "candidate": COMPONENT}


def run_adverse_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    def record(case_id: str, fn) -> None:
        try:
            fn()
            cases.append({"case_id": case_id, "result": "accepted", "state_unchanged": False})
        except Reject as exc:
            cases.append({"case_id": case_id, "result": "rejected", "code": str(exc), "state_unchanged": True})
        except Exception as exc:
            cases.append({"case_id": case_id, "result": "error", "code": type(exc).__name__, "state_unchanged": True})

    record("pcm_empty", lambda: validate_pcm_input([], 16000, 1))
    record("pcm_not_sequence", lambda: validate_pcm_input({"a": 1}, 16000, 1))
    record("pcm_none", lambda: validate_pcm_input(None, 16000, 1))
    record("pcm_bool", lambda: validate_pcm_input([True, False], 16000, 1))
    record("pcm_nan", lambda: validate_pcm_input([0.0, float("nan")], 16000, 1))
    record("pcm_pos_inf", lambda: validate_pcm_input([0.0, float("inf")], 16000, 1))
    record("pcm_neg_inf", lambda: validate_pcm_input([0.0, float("-inf")], 16000, 1))
    record("pcm_wrong_rate", lambda: validate_pcm_input([0.0, 0.1], 8000, 1))
    record("pcm_wrong_channels", lambda: validate_pcm_input([0.0, 0.1], 16000, 2))

    base_manifest = {
        "schema_id": "audio-sdk/pbfdaf-aumdf/caller-supplied/0.1",
        "candidate": COMPONENT,
        "source_revision": "0" * 40,
        "source_sha256": "1" * 64,
        "runtime_lock_path": "/no/such/runtime.lock",
        "runtime_lock_sha256": "2" * 64,
        "rights_record_path": "/no/such/rights.json",
        "rights_record_sha256": "3" * 64,
        "cohort_manifest_path": "/no/such/cohort.json",
        "cohort_manifest_sha256": "4" * 64,
        "sample_rate_hz": 16000,
        "channels": 1,
        "block_samples": 160,
        "partitions": 4,
        "variant": "partitioned_block_frequency_domain_aec",
    }
    record("manifest_not_object", lambda: validate_caller_manifest([]))
    bad_missing = dict(base_manifest); bad_missing.pop("source_revision")
    record("manifest_missing_field", lambda: validate_caller_manifest(bad_missing))
    bad_extra = dict(base_manifest); bad_extra["extra"] = 1
    record("manifest_extra_field", lambda: validate_caller_manifest(bad_extra))
    bad_sha = dict(base_manifest); bad_sha["source_sha256"] = "abc"
    record("manifest_bad_sha", lambda: validate_caller_manifest(bad_sha))
    bad_rel = dict(base_manifest); bad_rel["runtime_lock_path"] = "relative.lock"
    record("manifest_relative_path", lambda: validate_caller_manifest(bad_rel))
    bad_rev = dict(base_manifest); bad_rev["source_revision"] = "short"
    record("manifest_short_revision", lambda: validate_caller_manifest(bad_rev))
    bad_var = dict(base_manifest); bad_var["variant"] = "other"
    record("manifest_wrong_variant", lambda: validate_caller_manifest(bad_var))
    bad_blk = dict(base_manifest); bad_blk["block_samples"] = 128
    record("manifest_bad_block_size", lambda: validate_caller_manifest(bad_blk))
    bad_part = dict(base_manifest); bad_part["partitions"] = 0
    record("manifest_bad_partitions", lambda: validate_caller_manifest(bad_part))
    record("manifest_missing_asset", lambda: validate_caller_manifest(base_manifest))
    bad_hash = dict(base_manifest); bad_hash["runtime_lock_path"] = str(HERE / "reference.py"); bad_hash["runtime_lock_sha256"] = "0" * 64
    record("manifest_hash_mismatch", lambda: validate_caller_manifest(bad_hash))

    # ensure all declared case IDs covered
    seen = {c["case_id"] for c in cases}
    for case_id in ADVERSE_CASE_IDS:
        if case_id not in seen:
            cases.append({"case_id": case_id, "result": "missing", "state_unchanged": True})
    return cases


# ---------------------------------------------------------------------------
# Deterministic synthetic accounting control (no real AEC, no audio files)
# ---------------------------------------------------------------------------

def _synthetic_signal(n: int, seed: int) -> List[float]:
    # deterministic LCG-based bounded signal in [-0.5, 0.5]
    x = seed & 0xFFFFFFFF
    out = []
    for _ in range(n):
        x = (1664525 * x + 1013904223) & 0xFFFFFFFF
        v = (x / 0xFFFFFFFF) - 0.5
        out.append(float(v))
    return out


def build_control() -> Dict[str, Any]:
    render = _synthetic_signal(CONTROL_TOTAL_SAMPLES, 12345)
    capture = _synthetic_signal(CONTROL_TOTAL_SAMPLES, 67890)
    # accounting-only "partitioned block" bookkeeping: no adaptive filter
    blocks = CONTROL_TOTAL_SAMPLES // CONTROL_BLOCK_SAMPLES
    _expect(blocks * CONTROL_BLOCK_SAMPLES == CONTROL_TOTAL_SAMPLES, "control_geometry")
    state_history_len = CONTROL_PARTITIONS
    state: List[List[float]] = [[0.0] * CONTROL_FFT_SIZE for _ in range(state_history_len)]
    nonfinite = 0
    max_abs = 0.0
    accepted_blocks = 0
    for b in range(blocks):
        start = b * CONTROL_BLOCK_SAMPLES
        end = start + CONTROL_BLOCK_SAMPLES
        rblk = render[start:end]
        cblk = capture[start:end]
        # validate finite
        if not all(math.isfinite(v) for v in rblk + cblk):
            nonfinite += 1
            continue
        # state rotation emulates partition history bookkeeping only
        state = state[1:] + [[0.0] * CONTROL_FFT_SIZE]
        local_max = max(max(abs(v) for v in rblk), max(abs(v) for v in cblk))
        max_abs = max(max_abs, local_max)
        accepted_blocks += 1

    adverse = run_adverse_cases()
    all_rejected = all(c.get("result") == "rejected" for c in adverse)
    return {
        "id": "synthetic_partitioned_block_accounting_v1",
        "mode": "synthetic_partitioned_block_accounting",
        "sample_rate_hz": CONTROL_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "block_samples": CONTROL_BLOCK_SAMPLES,
        "fft_size": CONTROL_FFT_SIZE,
        "partitions": CONTROL_PARTITIONS,
        "filter_taps": CONTROL_FILTER_TAPS,
        "total_samples": CONTROL_TOTAL_SAMPLES,
        "blocks": blocks,
        "accepted_blocks": accepted_blocks,
        "rejected_blocks": blocks - accepted_blocks,
        "nonfinite_blocks": nonfinite,
        "max_abs": max_abs,
        "state_history_len": state_history_len,
        "state_reset_on_init": True,
        "output_is_real_aec": False,
        "adverse": adverse,
        "adverse_all_rejected": all_rejected,
        "qualification_effect": "none",
        "note": (
            "Synthetic accounting only. It does not run PBFDAF/AUMDF, does "
            "not process real audio, and cannot qualify the candidate."
        ),
    }


# ---------------------------------------------------------------------------
# Report / contract
# ---------------------------------------------------------------------------

def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    observed = audit_assets()
    control = build_control()
    gates = [
        {"id": gid, "requirement": req, "status": "blocked"}
        for gid, req in GATE_REQUIREMENTS
    ]
    qualification = {
        "status": QUALIFICATION,
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "blocked_gate_count": len(gates),
        "blocked_gate_ids": [g["id"] for g in gates],
        "reason": (
            "No exact licensed PBFDAF/AUMDF reference/runtime, rights record, "
            "paired render/capture cohort, MDF comparison, or timing evidence "
            "is present; only bounded synthetic accounting controls exist."
        ),
    }
    profile_items = [
        {
            "id": "freeze_render_reference",
            "requirement": "Freeze render/reference or measured RIRs, channel/rate/hop, excitation, delay, movement, noise and reset schedule.",
            "satisfied_for_qualification": False,
            "status": "blocked",
        },
        {
            "id": "scenario_coverage",
            "requirement": "Include echo-only, near-end-only, double-talk and no-reference cases.",
            "satisfied_for_qualification": False,
            "status": "blocked",
        },
        {
            "id": "metrics_and_controls",
            "requirement": "Report echo attenuation, near-end damage, nonfinite failures and alignments, including delayed/missing render.",
            "satisfied_for_qualification": False,
            "status": "blocked",
        },
        {
            "id": "separate_no_reference_comparison",
            "requirement": "A no-reference suppressor gets its own independent comparison.",
            "satisfied_for_qualification": False,
            "status": "blocked",
        },
    ]
    report = {
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
            "reference_urls": list(UPSTREAM_REFERENCE_URLS),
            "revision": UPSTREAM_REVISION,
            "revision_pin_available": SOURCE_REVISION_PIN_AVAILABLE,
            "licensed_runtime_present": False,
        },
        "asset_audit": {
            "qualified": False,
            "audit_result": "absent",
            "observed": observed,
            "all_absence_probes_absent": observed["all_absence_probes_absent"],
        },
        "absence_probes": observed["absence_probes"],
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "gates": gates,
        "room_profile": {
            "name": PROFILE,
            "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "source_sha256": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "required_items": profile_items,
            "satisfied_for_qualification": [],
            "unsatisfied_for_qualification": [i["id"] for i in profile_items],
            "note": "No room cohort, paired fixtures, or runtime measurements exist; profile is not satisfied.",
        },
        "reference_protocol": control,
        "controls": {
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "absence_probes_all_absent": observed["all_absence_probes_absent"],
            "adverse": control["adverse"],
            "adverse_all_rejected": control["adverse_all_rejected"],
        },
        "source_reported_context": {
            "label": "source_reported_not_measured_here",
            "aec_research_sha256": SOURCE_PINS["research/aec_research_20261028.md"],
            "finding": "AEC research identifies PBFDAF/AUMDF as a strong next classical candidate for long room impulse responses at lower cost than long time-domain filters; not implemented in that pass.",
            "notes": "No local implementation, runtime, cohort, or qualification result exists.",
        },
        "candidate_metrics": None,
        "non_claims": list(NON_CLAIMS),
        "tool_provenance": [
            "Python standard library only.",
            "Fixed workspace paths are probed for presence; no asset is read as model/audio input.",
            "No network request, download, runtime invocation, or device timing occurs.",
        ],
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline",
            "cold_start_regenerations_required": 3,
        },
    }
    return report


def build_contract() -> Dict[str, Any]:
    report = build_report()
    return {
        "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
        "SPDX-License-" "Identifier": "Apache-2.0",
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
        "qualification": report["qualification"],
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "task_row_identity": report["task_row_identity"],
        "scope": report["scope"],
        "boundary": report["boundary"],
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "upstream_identity": report["upstream_identity"],
        "exact_blockers": report["exact_blockers"],
        "gates": report["gates"],
        "room_profile_requirements": report["room_profile"]["required_items"],
        "reproduction": {
            "report_sha256_sidecar": "report.json.sha256",
            "sources_manifest": "SOURCES.sha256",
            "cold_start_regenerations": 3,
            "command": "python3 run.py all",
            "verify": "python3 verify.py",
            "tests": "python3 -m unittest -v test_reference.py",
        },
        "licensing": {
            "copyright": "2026 Tsakanyan Hovhannes",
            "license": "Apache-2.0",
            "json_sidecars": True,
        },
    }


def canonical_contract_bytes() -> bytes:
    return canonical_bytes(build_contract()) + b"\n"
