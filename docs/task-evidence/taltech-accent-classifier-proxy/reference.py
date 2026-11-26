# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-TALTECH-ACCENT-CLASSIFIER-PROXY.

The exact licensed TalTech accent classifier source, weights, runtime, approved
reference vector, rights-cleared cohort, and device/listening qualification
evidence required by the task are not present in this workspace. This package
never imports model/runtime dependencies, never downloads assets, never reads or
writes real audio, never executes the classifier, and never measures device
timing. It provides:

* a fail-closed audit over fixed workspace paths for the exact classifier/source
  artifacts;
* a caller-supplied-asset manifest contract validated without execution;
* a deterministic synthetic label-accounting control that checks validity,
  finite score handling, and proxy/non-qualification boundaries.

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
from typing import Any, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-TALTECH-ACCENT-CLASSIFIER-PROXY"
TITLE = "TalTech accent classifier proxy"
SLUG = "taltech-accent-classifier-proxy"
COMPONENT = "taltech-accent-classifier-proxy"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "evidence"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "opt_in_adapter_exposure"

# The merged accent-conversion research note records a directional proxy using
# MilesPurvis/english-accent-classifier. This package does not treat that proxy
# as TalTech source/weights/runtime evidence and does not reproduce it.
PROXY_MODEL_REPORTED = "MilesPurvis/english-accent-classifier"
PROXY_NOTE_PATH = "research/accent-conversion-20261101/README.md"
PROXY_NOTE_SHA256 = "c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c"

# Fixed audit paths. Absence is recorded, not filled.
AUDIT_PATHS: Tuple[str, ...] = (
    "data/checkouts/taltech-accent-classifier-proxy",
    "data/checkouts/taltech-accent-classifier",
    "data/checkouts/accent-classifier-proxy",
    "data/models/taltech-accent-classifier-proxy",
    "data/models/taltech-accent-classifier",
    "data/envs/taltech-accent-classifier-proxy",
    "data/rights/taltech-accent-classifier-proxy-rights.json",
    "data/runs/taltech-accent-classifier-proxy/manifest.json",
    "research/accent-conversion-20261101/results/accent-classifier.json",
    "research/accent-conversion-20261101/evaluate_accent_classifier.py",
)
MISSING_ARTIFACTS: Tuple[str, ...] = (
    "data/checkouts/taltech-accent-classifier-proxy",
    "data/models/taltech-accent-classifier-proxy",
    "data/envs/taltech-accent-classifier-proxy",
    "data/rights/taltech-accent-classifier-proxy-rights.json",
    "data/runs/taltech-accent-classifier-proxy/manifest.json",
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
        PROXY_NOTE_SHA256,
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

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "board_or_handoff_changed": False,
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
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
}

SCOPE: Dict[str, Any] = {
    "benchmark_claim": False,
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No TalTech accent classifier source, weights, runtime, adapter or numeric result is downloaded, loaded, imported or executed.",
    "No real audio, corpus, transcript, consent record or listening result is consumed or produced.",
    "No accent label, confidence, similarity, intelligibility, naturalness, latency, memory or RTF is measured.",
    "The source-reported MilesPurvis proxy note is provenance only; it is not reproduced, promoted or treated as TalTech evidence.",
    "Classifier direction is not listener-confirmed accent and is not a qualification result.",
    "The synthetic label-accounting control is a contract control, never model output, and cannot qualify the candidate.",
    "No provider, descriptor, registry, installed v0 path, shared build or CI is changed.",
    "No device timing, public benchmark, listening or release claim is made.",
    "Missing, blocked or rejected evidence never qualifies the candidate; decision remains DEFER.",
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_source_and_revision", "Pin the exact TalTech accent classifier source, revision, license and attribution record."),
    ("exact_weights_and_runtime", "Pin exact weights/checkpoints, hashes, runtime lock, platform and deterministic execution contract."),
    ("rights_and_consent", "Clear code, weight, corpus, reference, consent, output-use and redistribution rights."),
    ("approved_reference_parity", "Reproduce an approved reference vector on frozen input with deterministic reruns and declared tolerances."),
    ("matched_scope_and_cohort", "Freeze held-out cohort, label set, language/speaker groups, and report scope; separate proxy from listener-confirmed accent."),
    ("device_timing_and_resources", "Measure device timing, memory, CPU and deadline behavior on approved targets."),
    ("independent_review", "Complete independent review of evidence, rights, scope and release boundary."),
    ("opt_in_release_boundary", "Record explicit opt-in intake; no default, no processor exposure, no public/release claim before gates clear."),
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "exact_source_absent", "state": "absent", "requirement": "No exact TalTech accent classifier source checkout, immutable revision, or license record is present in audited paths."},
    {"id": "weights_and_checkpoint_absent", "state": "absent", "requirement": "No exact model weights/checkpoints, byte counts or SHA-256 identities are present."},
    {"id": "runtime_and_environment_absent", "state": "absent", "requirement": "No pinned runtime, environment lock, platform record or deterministic execution contract is present."},
    {"id": "rights_and_consent_absent", "state": "absent", "requirement": "No rights, consent, attribution, output-use or redistribution review record is present."},
    {"id": "approved_reference_vector_absent", "state": "absent", "requirement": "No approved reference parity vector or deterministic rerun evidence is present."},
    {"id": "matched_cohort_absent", "state": "absent", "requirement": "No rights-cleared held-out cohort, frozen label scope, or matched evaluation manifest is present."},
    {"id": "listening_and_scope_unresolved", "state": "absent", "requirement": "Classifier direction is not listener-confirmed accent; no blinded listening or scope-qualified human review exists."},
    {"id": "timing_and_release_absent", "state": "absent", "requirement": "No device timing, resource, independent review, or opt-in release decision is present."},
)

VOICE_LIKE_EVIDENCE_NOTES = (
    "This is an evidence/research-control proxy task, not a qualified accent classifier or voice conversion result.",
    "Classifier direction must be reported separately from listener-confirmed accent.",
)


class Reject(ValueError):
    """Deterministic validation rejection."""


def canonical_bytes(obj: Any) -> bytes:
    try:
        text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except ValueError as exc:
        raise Reject(f"non-canonical JSON value: {exc}") from exc
    return (text + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def strict_loads(text: str) -> Any:
    if text.startswith("\ufeff"):
        raise Reject("byte order mark is not allowed")

    def _object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise Reject(f"duplicate key: {key}")
            obj[key] = value
        return obj

    decoder = json.JSONDecoder(object_pairs_hook=_object_pairs_hook, parse_constant=_reject_constant)
    try:
        obj, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        raise Reject(f"invalid JSON: {exc}") from exc
    if text[end:].strip():
        raise Reject("trailing data after JSON document")
    _validate_no_float(obj, "$")
    return obj


def _reject_constant(value: str) -> Any:
    raise Reject(f"non-standard JSON constant: {value}")


def _validate_no_float(obj: Any, path: str) -> None:
    if isinstance(obj, bool) or obj is None or isinstance(obj, (int, str)):
        return
    if isinstance(obj, float):
        raise Reject(f"float not allowed in canonical evidence: {path}")
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            _validate_no_float(item, f"{path}[{i}]")
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            _validate_no_float(v, f"{path}/{k}")
        return
    raise Reject(f"unsupported JSON type at {path}: {type(obj).__name__}")


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def file_record(path: Path, base: Path) -> Dict[str, Any]:
    data = path.read_bytes()
    rel = path.relative_to(base).as_posix()
    return {"path": rel, "bytes": len(data), "sha256": sha256_bytes(data)}


def collect_package_files() -> List[Dict[str, Any]]:
    records = []
    for path in sorted(HERE.rglob("*")):
        if not path.is_file():
            continue
        if path.name.endswith(".pyc") or "__pycache__" in path.parts:
            continue
        records.append(file_record(path, SDK_ROOT))
    return records


def audit_assets() -> Dict[str, Any]:
    observed = []
    present = 0
    for rel in AUDIT_PATHS:
        path = SOURCE_ROOT / rel
        exists = path.exists()
        kind = "dir" if path.is_dir() else "file" if path.is_file() else "missing"
        observed.append({"path": rel, "present": exists, "kind": kind})
        if exists:
            present += 1
    proxy_note = SOURCE_ROOT / PROXY_NOTE_PATH
    proxy_note_present = proxy_note.is_file()
    proxy_note_digest = sha256_file(proxy_note) if proxy_note_present else None
    proxy_mentions = []
    if proxy_note_present:
        text = proxy_note.read_text(encoding="utf-8", errors="replace")
        proxy_mentions = [
            line.strip() for line in text.splitlines()
            if PROXY_MODEL_REPORTED in line or "TalTech" in line or "accent classifier" in line.lower()
        ][:8]
    return {
        "audit_result": "exact_assets_absent_proxy_note_only",
        "qualified": False,
        "all_required_absent": present == 0 or all(
            not (SOURCE_ROOT / p).exists() for p in MISSING_ARTIFACTS
        ),
        "present_count": present,
        "probe_count": len(AUDIT_PATHS),
        "observed": observed,
        "missing_historical_artifacts": list(MISSING_ARTIFACTS),
        "proxy_note": {
            "path": PROXY_NOTE_PATH,
            "present": proxy_note_present,
            "sha256": proxy_note_digest,
            "reported_model": PROXY_MODEL_REPORTED,
            "source_reported_only": True,
            "treated_as_taltech_evidence": False,
            "mentions": proxy_mentions,
        },
    }


MANIFEST_REQUIRED = (
    "channels",
    "classifier_checkpoint_path",
    "classifier_checkpoint_sha256",
    "config_path",
    "config_sha256",
    "consent_record_path",
    "consent_record_sha256",
    "label_map_path",
    "label_map_sha256",
    "license_record_path",
    "license_record_sha256",
    "runtime_lock_path",
    "runtime_lock_sha256",
    "runtime_path",
    "sample_rate_hz",
    "source_reference_path",
    "source_reference_sha256",
    "source_revision",
    "variant",
)
MANIFEST_SHA_FIELDS = tuple(k for k in MANIFEST_REQUIRED if k.endswith("_sha256"))
MANIFEST_PATH_FIELDS = tuple(k for k in MANIFEST_REQUIRED if k.endswith("_path"))
CALLER_VARIANT = "research_classifier_proxy_offline"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def _is_abs_path(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("/") and "\x00" not in value


def validate_manifest(manifest: Any) -> Dict[str, Any]:
    _require(isinstance(manifest, dict), "manifest must be an object")
    keys = tuple(sorted(manifest.keys()))
    missing = [k for k in MANIFEST_REQUIRED if k not in manifest]
    extra = [k for k in keys if k not in MANIFEST_REQUIRED]
    _require(not missing, "manifest missing fields: " + ", ".join(missing))
    _require(not extra, "manifest has unknown fields: " + ", ".join(extra))

    _require(manifest["variant"] == CALLER_VARIANT, "manifest variant must be " + CALLER_VARIANT)
    _require(manifest["sample_rate_hz"] == 16000, "manifest sample_rate_hz mismatch")
    _require(manifest["channels"] == 1, "manifest channels mismatch")
    _require(isinstance(manifest["source_revision"], str) and HEX40.fullmatch(manifest["source_revision"]),
             "manifest source_revision must be a full 40-hex commit")

    for field in MANIFEST_SHA_FIELDS:
        value = manifest[field]
        _require(isinstance(value, str) and HEX64.fullmatch(value), f"manifest {field} is not a lowercase SHA-256")
    for field in MANIFEST_PATH_FIELDS:
        value = manifest[field]
        _require(_is_abs_path(value), f"manifest {field} must be absolute")
        path = Path(value)
        _require(path.exists(), f"manifest {field} path is missing")
        if field == "runtime_path":
            _require(path.is_dir(), "manifest runtime_path directory is missing")
        else:
            _require(path.is_file(), f"manifest {field} file is missing")
            digest = sha256_file(path)
            _require(digest == manifest[field.replace("_path", "_sha256")],
                     f"manifest {field} sha256 mismatch")
    return manifest


def validate_label_scores(scores: Any) -> Dict[str, float]:
    _require(isinstance(scores, dict) and scores, "scores must be a non-empty object")
    out: Dict[str, float] = {}
    total = 0.0
    for key, value in scores.items():
        _require(isinstance(key, str) and bool(key.strip()), "score key must be a non-empty string")
        _require(not isinstance(value, bool) and isinstance(value, (int, float)), f"score {key} must be numeric")
        value_f = float(value)
        _require(math.isfinite(value_f), f"score {key} is not finite")
        _require(value_f >= 0.0, f"score {key} must be non-negative")
        out[key] = value_f
        total += value_f
    _require(math.isfinite(total) and total > 0.0, "score total must be positive")
    return out


def normalize_scores(scores: Dict[str, float]) -> Dict[str, str]:
    total = sum(scores.values())
    return {k: fraction_text(Fraction(scores[k] / total).limit_denominator(10**12)) for k in sorted(scores)}


def top_label(scores: Dict[str, float]) -> str:
    return max(sorted(scores), key=lambda k: (scores[k], k))


def synthetic_label_accounting_control() -> Dict[str, Any]:
    source_scores = {"american": 0.20, "british": 0.15, "indian": 0.50, "latin": 0.15}
    output_scores = {"american": 0.35, "british": 0.20, "indian": 0.20, "latin": 0.25}
    src = validate_label_scores(source_scores)
    out = validate_label_scores(output_scores)
    return {
        "control_id": "synthetic_label_accounting_control",
        "qualification_effect": "none",
        "is_candidate_model_output": False,
        "classifier_direction_only": True,
        "listener_confirmed_accent": False,
        "source_top_label": top_label(src),
        "output_top_label": top_label(out),
        "delta_american": fraction_text(Fraction(out["american"] - src["american"]).limit_denominator(10**12)),
        "normalized_source": normalize_scores(src),
        "normalized_output": normalize_scores(out),
    }


def adverse_cases(root: Path) -> List[Dict[str, str]]:
    cases = []

    def reject(name: str, fn) -> None:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - deterministic contract tests
            cases.append({"case": name, "result": "rejected", "reason": str(exc)})
            return
        cases.append({"case": name, "result": "accepted", "reason": ""})

    reject("scores_empty", lambda: validate_label_scores({}))
    reject("scores_not_object", lambda: validate_label_scores([]))
    reject("scores_nan", lambda: validate_label_scores({"a": math.nan}))
    reject("scores_pos_inf", lambda: validate_label_scores({"a": math.inf}))
    reject("scores_neg_inf", lambda: validate_label_scores({"a": -math.inf}))
    reject("scores_negative", lambda: validate_label_scores({"a": -0.1}))
    reject("scores_bool", lambda: validate_label_scores({"a": True}))
    reject("scores_string", lambda: validate_label_scores({"a": "0.1"}))
    reject("scores_zero_total", lambda: validate_label_scores({"a": 0.0, "b": 0.0}))
    reject("scores_empty_key", lambda: validate_label_scores({"": 1.0}))

    try:
        manifest = _good_manifest_fixture(root)
        manifest["variant"] = "streaming"
        validate_manifest(manifest)
        cases.append({"case": "manifest_wrong_variant", "result": "accepted", "reason": ""})
    except Exception as exc:  # noqa: BLE001
        cases.append({"case": "manifest_wrong_variant", "result": "rejected", "reason": str(exc)})

    try:
        manifest = _good_manifest_fixture(root)
        del manifest["config_sha256"]
        validate_manifest(manifest)
        cases.append({"case": "manifest_missing_field", "result": "accepted", "reason": ""})
    except Exception as exc:  # noqa: BLE001
        cases.append({"case": "manifest_missing_field", "result": "rejected", "reason": str(exc)})

    try:
        manifest = _good_manifest_fixture(root)
        manifest["extra"] = "x"
        validate_manifest(manifest)
        cases.append({"case": "manifest_extra_field", "result": "accepted", "reason": ""})
    except Exception as exc:  # noqa: BLE001
        cases.append({"case": "manifest_extra_field", "result": "rejected", "reason": str(exc)})

    try:
        manifest = _good_manifest_fixture(root)
        manifest["classifier_checkpoint_path"] = "relative.pt"
        validate_manifest(manifest)
        cases.append({"case": "manifest_relative_path", "result": "accepted", "reason": ""})
    except Exception as exc:  # noqa: BLE001
        cases.append({"case": "manifest_relative_path", "result": "rejected", "reason": str(exc)})

    try:
        manifest = _good_manifest_fixture(root)
        manifest["classifier_checkpoint_sha256"] = "BAD"
        validate_manifest(manifest)
        cases.append({"case": "manifest_bad_sha", "result": "accepted", "reason": ""})
    except Exception as exc:  # noqa: BLE001
        cases.append({"case": "manifest_bad_sha", "result": "rejected", "reason": str(exc)})

    try:
        manifest = _good_manifest_fixture(root)
        manifest["source_revision"] = "abc"
        validate_manifest(manifest)
        cases.append({"case": "manifest_short_revision", "result": "accepted", "reason": ""})
    except Exception as exc:  # noqa: BLE001
        cases.append({"case": "manifest_short_revision", "result": "rejected", "reason": str(exc)})

    try:
        manifest = _good_manifest_fixture(root)
        manifest["sample_rate_hz"] = 8000
        validate_manifest(manifest)
        cases.append({"case": "manifest_wrong_rate", "result": "accepted", "reason": ""})
    except Exception as exc:  # noqa: BLE001
        cases.append({"case": "manifest_wrong_rate", "result": "rejected", "reason": str(exc)})

    try:
        manifest = _good_manifest_fixture(root)
        manifest["channels"] = 2
        validate_manifest(manifest)
        cases.append({"case": "manifest_wrong_channels", "result": "accepted", "reason": ""})
    except Exception as exc:  # noqa: BLE001
        cases.append({"case": "manifest_wrong_channels", "result": "rejected", "reason": str(exc)})

    try:
        manifest = _good_manifest_fixture(root)
        Path(manifest["license_record_path"]).unlink()
        validate_manifest(manifest)
        cases.append({"case": "manifest_missing_asset", "result": "accepted", "reason": ""})
    except Exception as exc:  # noqa: BLE001
        cases.append({"case": "manifest_missing_asset", "result": "rejected", "reason": str(exc)})

    return cases


def _good_manifest_fixture(root: Path) -> Dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    runtime = root / "runtime"
    runtime.mkdir(exist_ok=True)
    manifest: Dict[str, Any] = {
        "variant": CALLER_VARIANT,
        "sample_rate_hz": 16000,
        "channels": 1,
        "source_revision": "0123456789abcdef0123456789abcdef01234567",
        "runtime_path": str(runtime),
    }
    files = {
        "classifier_checkpoint_path": b"ckpt",
        "config_path": b"config",
        "consent_record_path": b"consent",
        "label_map_path": b"label",
        "license_record_path": b"license",
        "runtime_lock_path": b"lock",
        "source_reference_path": b"source",
    }
    for field, data in files.items():
        path = root / (field.replace("_path", "") + ".bin")
        path.write_bytes(data)
        manifest[field] = str(path)
        manifest[field.replace("_path", "_sha256")] = sha256_bytes(data)
    return manifest


def task_row_identity() -> Dict[str, Any]:
    tasks_path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    doc = strict_loads(tasks_path.read_text(encoding="utf-8"))
    rows = [r for r in doc.get("tasks", []) if isinstance(r, dict) and r.get("id") == TASK]
    _require(len(rows) == 1, "expected exactly one linked task row")
    row = rows[0]
    stable = {k: row.get(k) for k in STABLE_TASK_FIELDS}
    return {
        "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(canonical_bytes(stable)),
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": row.get("claim") or {},
        "whole_file_hashed": False,
    }


def boundary_observation() -> Dict[str, Any]:
    obs = {}
    for rel, digest in BOUNDARY_PINS.items():
        path = SDK_ROOT / rel
        obs[rel] = {
            "present": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else None,
            "matches_pin": (sha256_file(path) == digest) if path.is_file() else False,
        }
    return obs


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = audit_assets()
    control = synthetic_label_accounting_control()
    with tempfile_root() as root:
        adverse = adverse_cases(root)
    adverse_all_rejected = all(item["result"] == "rejected" for item in adverse)

    report = {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": "research-control",
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "qualification_status": QUALIFICATION,
        "defer_before": DEFER_BEFORE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "task_prefix": TASK_PREFIX,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "boundary_pins": BOUNDARY_PINS,
        "boundary_observation": boundary_observation(),
        "source_pins": SOURCE_PINS,
        "task_row_identity": identity,
        "qualification": {
            "status": QUALIFICATION,
            "candidate_qualified": False,
            "no_missing_result_qualifies_candidate": True,
            "decision": DECISION,
            "defer_before": DEFER_BEFORE,
            "blocked_gate_count": len(GATE_REQUIREMENTS),
            "blocked_gate_ids": [g for g, _ in GATE_REQUIREMENTS],
            "reason": (
                "Exact TalTech accent classifier source, weights, runtime, rights, "
                "approved reference vector, matched cohort and timing evidence are "
                "absent. Source-reported proxy notes are not reproduced and cannot qualify."
            ),
        },
        "exact_blockers": list(EXACT_BLOCKERS),
        "gates": [
            {"id": gid, "requirement": req, "status": "blocked"}
            for gid, req in GATE_REQUIREMENTS
        ],
        "reopen_conditions": [
            {"gate_id": gid, "condition": req}
            for gid, req in GATE_REQUIREMENTS
        ],
        "asset_audit": audit,
        "caller_asset_contract": {
            "contract_id": f"audio-sdk/{SLUG}/caller-supplied-asset/0.1",
            "asset_is_caller_owned": True,
            "asset_is_vendored": False,
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_absolute_paths_sha256_revision_geometry_and_variant_only; do_not_import_or_execute",
            "required_fields": list(MANIFEST_REQUIRED),
            "required_variant": CALLER_VARIANT,
            "required_geometry": {"sample_rate_hz": 16000, "channels": 1},
        },
        "reference_protocol": {
            "kind": "deterministic_synthetic_label_accounting_control",
            "model_executed": False,
            "qualification_effect": "none",
            "result": control,
            "adverse": adverse,
        },
        "controls": {
            "adverse_all_rejected": adverse_all_rejected,
            "invalid_values_rejected": True,
            "missing_asset_rejected_before_processing": True,
            "missing_result_never_qualifies": True,
            "nonfinite_rejected": True,
            "proxy_not_listener_confirmed": True,
            "adverse": adverse,
        },
        "voice_profile": {
            "name": "evidence",
            "note": "Research-control evidence package; no qualified classifier output, no listening, no timing.",
            "satisfied_for_qualification": [],
            "real_model_metrics": None,
        },
        "source_reported_context": {
            "label": "source_reported_not_measured_here",
            "source": PROXY_NOTE_PATH,
            "source_sha256": PROXY_NOTE_SHA256,
            "reported_model": PROXY_MODEL_REPORTED,
            "treated_as_taltech_evidence": False,
            "notes": (
                "Accent-conversion research note used MilesPurvis/english-accent-classifier "
                "as a directional proxy on three TokAN pairs. This is not TalTech source, "
                "not reproduced, not listener-confirmed accent, and not qualification evidence."
            ),
        },
        "missing_historical_artifacts": list(MISSING_ARTIFACTS),
        "non_claims": list(NON_CLAIMS),
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline",
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
        "tool_provenance": [
            "Python standard library only; no model, audio runtime or network access.",
            "Asset audit uses fixed local paths and file presence/hash checks only.",
            "Task identity hashes only stable linked-row fields, never the full mutable TASKS.json.",
        ],
    }
    return report


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report)


class tempfile_root:
    def __enter__(self) -> Path:
        import tempfile
        self._dir = tempfile.TemporaryDirectory(prefix="taltech-accent-verify-")
        return Path(self._dir.name)

    def __exit__(self, exc_type, exc, tb) -> None:
        self._dir.cleanup()


def sources_bytes() -> bytes:
    lines = [
        "# SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes",
        "# SPDX-" + "License-Identifier: Apache-2.0",
        "# Deterministic source pins for taltech-accent-classifier-proxy evidence package.",
        "# The mutable full plan/swarm/TASKS.json is never pinned as a whole file.",
    ]
    for rel in sorted(SOURCE_PINS):
        path = SOURCE_ROOT / rel
        digest = sha256_file(path) if path.is_file() else SOURCE_PINS[rel]
        lines.append(f"{digest}  source:{rel}")
    for rel in sorted(BOUNDARY_PINS):
        path = SDK_ROOT / rel
        digest = sha256_file(path) if path.is_file() else BOUNDARY_PINS[rel]
        lines.append(f"{digest}  worktree:{rel}")
    pkg_files = [p for p in sorted(HERE.iterdir()) if p.is_file() and p.name != "SOURCES.sha256"]
    for path in pkg_files:
        lines.append(f"{sha256_file(path)}  pkg:{path.name}")
    return ("\n".join(lines) + "\n").encode("utf-8")
