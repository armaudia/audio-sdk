# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for SDK-PESQ-POLQA-AND-3QUEST.

PESQ, POLQA and 3QUEST are licensed/proprietary perceptual quality
scorers/assessment systems.  No exact licensed reference implementation,
licensed runtime, entitlement, approved scorer binary, rights-cleared cohort,
or qualified execution environment is present in this workspace.  This module
never imports, downloads, executes, emulates, or fabricates any scorer, never
reads or writes real audio, never measures device timing, and never makes a
benchmark or release claim.

It provides bounded, verifiable artifacts:
* a fail-closed asset/runtime/rights audit over fixed workspace paths;
* a caller-supplied scorer manifest contract validated without execution;
* deterministic synthetic accounting/control fixtures that prove strict
  parsing, validity separation, and aggregation arithmetic only;
* canonical report/contract construction with DEFER / incomplete /
  not_qualified disposition and eight blocked release gates.

Missing evidence never qualifies a candidate.
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

TASK = "SDK-PESQ-POLQA-AND-3QUEST"
TITLE = "PESQ, POLQA and 3QUEST"
SLUG = "pesq-polqa-and-3quest"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "fb0ee3e326beb269c87358251aceb61352329635"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/" + TASK)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "evidence"
MODE = "research-control"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
DECISION = "DEFER"
QUALIFICATION = "not_qualified"
DEFER_BEFORE = "processor_exposure"
SPDX_COPYRIGHT = "SPDX-" + "FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"

SCORERS = ("pesq", "polqa", "3quest")
SOURCE_REVISION_PIN_AVAILABLE = False

# Fixed absence probes.  These are paths where licensed binaries/runtime/cohorts
# might accidentally appear; presence forces re-evaluation.
ABSENCE_PROBES: Tuple[str, ...] = (
    "data/models/pesq",
    "data/models/polqa",
    "data/models/3quest",
    "data/tools/pesq",
    "data/tools/polqa",
    "data/tools/3quest",
    "data/envs/pesq",
    "data/envs/polqa",
    "data/envs/3quest",
    "data/licenses/pesq",
    "data/licenses/polqa",
    "data/licenses/3quest",
    "data/rights/pesq-polqa-and-3quest-rights.json",
    "data/runs/pesq-polqa-and-3quest-cohort/manifest.json",
    "data/runs/pesq-polqa-and-3quest-reference/manifest.json",
    "research/voice-enhancement-20261101/repos/pesq",
    "research/voice-enhancement-20261101/repos/polqa",
    "research/voice-enhancement-20261101/repos/3quest",
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
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "research/cpp-lib-market-benchmark-20261109.md":
        "d1a4edbf72257ebb989d9639e542cf2c50152e323dc9081f2af868708064a3e7",
    "realtime-audio-library/evaluation/dns2020_noreverb_speexns_stoi_pesq_summary_20261029.json":
        "fa98caa89be8c19234d719a5ba04147960fe03723ae4397dbd09ead52765be6e",
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
    "docs/task-evidence/dnsmos-p-835-and-dnsmos-c/README.md":
        "eb7d069cc402aa37210dd2ebd43e45e840bc600693a947684e5341eb28fbd579",
    "docs/task-evidence/stoi-estoi/contract.json":
        "aa42da4c71b6eee281fca1ccc52f394c32d85cb2c65e31d1bc0a814a7726f7f5",
    "docs/task-evidence/si-sdr-sdr-and-snr/README.md":
        "16bc05e63afdb209ba2a9657b7977c29f7d15f9eb3d6e8d24e316b3d2ef671a3",
    "docs/task-evidence/quality-impairment-taxonomy/README.md":
        "77ad10fae3e41a06adad6cee377616c73dd8d7d458a76c9297aa55d837afcbe5",
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

BOUNDARY: Dict[str, Any] = {
    "abi_change": False,
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
    "model_or_scorer_executed": False,
    "network_used": False,
    "public_benchmark": False,
    "real_audio": False,
    "real_corpus": False,
    "release_claim": False,
    "runtime_invoked": False,
    "scores_fabricated": False,
    "task_local_only": True,
    "vendor_runtime_invoked": False,
    "weights_or_binaries_downloaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No PESQ, POLQA or 3QUEST binary, SDK, license, runtime or entitlement is present or executed.",
    "No score, rating, MOS, intelligibility, benchmark, device timing or listening result is fabricated.",
    "No real audio, cohort, or rights-cleared evaluation media is consumed or redistributed.",
    "No network request, download, or asset staging occurs.",
    "No provider registration, installed-v0/ABI/registry/default/shared-build/CI change is made.",
    "Historical/source-reported values are provenance only and are not reproduced or qualified here.",
    "Missing evidence never qualifies a candidate; decision remains DEFER.",
)

ASSET_REQUIREMENTS: Tuple[Dict[str, Any], ...] = (
    {"id": "pesq_license_and_runtime", "required": True, "status": "absent",
     "requirement": "Approved PESQ license/entitlement and exact executable/runtime with pinned revision and digest."},
    {"id": "polqa_license_and_runtime", "required": True, "status": "absent",
     "requirement": "Approved POLQA license/entitlement and exact executable/runtime with pinned revision and digest."},
    {"id": "quest3_license_and_runtime", "required": True, "status": "absent",
     "requirement": "Approved 3QUEST license/entitlement and exact executable/runtime with pinned revision and digest."},
    {"id": "rights_cleared_cohort", "required": True, "status": "absent",
     "requirement": "Rights-cleared, item-level pinned cohort with reference/degraded pairs and declared mode/sample rate."},
    {"id": "scorer_parity_vectors", "required": True, "status": "absent",
     "requirement": "Approved reference outputs/parity vectors for each scorer mode actually run."},
    {"id": "runtime_environment", "required": True, "status": "absent",
     "requirement": "Pinned isolated runtime/environment manifest; no incidental machine state may qualify."},
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "pesq_entitlement_absent", "state": "absent",
     "requirement": "Provide an approved PESQ license/entitlement and exact pinned runtime before any PESQ result can be considered."},
    {"id": "polqa_entitlement_absent", "state": "absent",
     "requirement": "Provide an approved POLQA license/entitlement and exact pinned runtime before any POLQA result can be considered."},
    {"id": "quest3_entitlement_absent", "state": "absent",
     "requirement": "Provide an approved 3QUEST license/entitlement and exact pinned runtime before any 3QUEST result can be considered."},
    {"id": "no_pinned_scorer_binaries", "state": "absent",
     "requirement": "Supply exact scorer binaries/sources with immutable revisions and SHA-256 digests; no binary is present."},
    {"id": "no_rights_cleared_cohort", "state": "absent",
     "requirement": "Supply a rights-cleared, item-level pinned cohort with declared mode, sample rate, alignment and permissions."},
    {"id": "no_parity_or_reference_outputs", "state": "absent",
     "requirement": "Supply approved parity/reference outputs for each scorer/mode; no local scorer output exists."},
    {"id": "no_approved_runtime", "state": "absent",
     "requirement": "Provide a pinned, isolated runtime/environment; incidental system tools cannot qualify."},
    {"id": "no_independent_release_review", "state": "absent",
     "requirement": "Independent review and explicit release/admission decision required before any processor/benchmark exposure."},
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("licensed_scorer_entitlements", "Approved licenses/entitlements for PESQ, POLQA and 3QUEST with permitted scope recorded."),
    ("exact_scorer_identity", "Exact scorer binaries/sources, revisions, digests, modes and command contracts are pinned."),
    ("pinned_runtime_environment", "Isolated pinned runtime/environment is admitted; no incidental system state qualifies."),
    ("rights_cleared_cohort", "Rights-cleared cohort with item-level identity, alignment, sample rate and permissions is frozen."),
    ("exact_reference_parity", "Approved reference outputs/parity vectors validate each scorer/mode on a frozen input."),
    ("evidence_profile_controls", "Evidence profile controls pass: pinned scorer/cohort/aggregation, invalid/missing case, and separated evidence classes."),
    ("processor_exposure_review", "Independent review explicitly decides whether any processor/adapter exposure is allowed; default remains off."),
    ("public_benchmark_release", "No public benchmark/release claim without explicit admission, rights, and qualified evidence."),
)

QUALIFICATION_REASON = (
    "No licensed PESQ/POLQA/3QUEST entitlement, no pinned scorer binary/runtime, "
    "no rights-cleared cohort, no parity/reference output, and no approved "
    "execution/review path exists. Missing evidence never qualifies."
)

SOURCE_REPORTED_CONTEXT: Dict[str, Any] = {
    "label": "source_reported_not_measured_here",
    "pesq_historical_local": {
        "source": "realtime-audio-library/evaluation/dns2020_noreverb_speexns_stoi_pesq_summary_20261029.json",
        "source_sha256": SOURCE_PINS[
            "realtime-audio-library/evaluation/dns2020_noreverb_speexns_stoi_pesq_summary_20261029.json"],
        "status": "historical_local_not_reproduced_here",
        "notes": "Historical DNS 30-item Speex replay recorded PESQ/STOI deltas; not reproduced here, not a qualification, and rights/terms remain unresolved.",
    },
    "polqa_3quest": {
        "status": "cited_or_vendor_reported_not_locally_run",
        "notes": "POLQA/3QUEST mentioned in market/quality taxonomy sources; no local licensed run, no parity, no rights-cleared cohort, no qualification.",
    },
}


class Reject(ValueError):
    """Fail-closed validation error."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(obj: Any) -> bytes:
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                          allow_nan=False).encode("utf-8")
    except ValueError as exc:
        raise Reject(f"non_canonical_json:{exc}") from exc


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def canonical_contract_bytes(contract: Optional[Dict[str, Any]] = None) -> bytes:
    return canonical_bytes(contract or build_contract()) + b"\n"


def strict_loads(text: str) -> Dict[str, Any]:
    def _object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise Reject(f"duplicate_json_key:{key}")
            obj[key] = value
        return obj

    def _reject_constant(x: str):
        raise Reject(f"nonfinite_json_constant:{x}")

    try:
        parsed = json.loads(text, object_pairs_hook=_object_pairs_hook, parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise Reject(f"malformed_json:{exc}") from exc
    except Reject:
        raise
    if not isinstance(parsed, dict):
        raise Reject("json_root_not_object")
    return parsed


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _is_hex_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def _is_hex40(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{40}", value))


def _require_obj(value: Any, label: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise Reject(f"{label}_not_object")
    return value


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise Reject(f"{label}_not_bool")
    return value


def _require_int(value: Any, label: str, minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject(f"{label}_not_int")
    if minimum is not None and value < minimum:
        raise Reject(f"{label}_out_of_range")
    if maximum is not None and value > maximum:
        raise Reject(f"{label}_out_of_range")
    return value


def _require_finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Reject(f"{label}_not_number")
    num = float(value)
    if not math.isfinite(num):
        raise Reject(f"{label}_not_finite")
    return num


def _require_str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise Reject(f"{label}_not_nonempty_string")
    return value


def validate_pcm(signal: Any, sample_rate_hz: int, channels: int = 1, label: str = "signal") -> Dict[str, Any]:
    if not isinstance(signal, list) or not signal:
        raise Reject(f"{label}_must_be_nonempty_list")
    if channels != 1:
        raise Reject("channels_unsupported")
    if sample_rate_hz not in (8000, 16000, 48000):
        raise Reject("unsupported_sample_rate_hz")
    out: List[float] = []
    peak = 0.0
    for i, sample in enumerate(signal):
        s = _require_finite_number(sample, f"{label}[{i}]")
        if abs(s) > 1.0:
            raise Reject(f"{label}[{i}]_out_of_range")
        out.append(s)
        peak = max(peak, abs(s))
    return {
        "channels": 1,
        "sample_rate_hz": sample_rate_hz,
        "samples": len(out),
        "peak_abs": peak,
        "sha256": sha256_bytes(canonical_bytes(out)),
    }


def synthetic_control_pcm() -> Dict[str, Any]:
    # Deterministic synthetic 16 kHz mono control signal. Not speech, not a score.
    sr = 16000
    n = 320
    sig = []
    for i in range(n):
        t = i / sr
        v = 0.1 * math.sin(2 * math.pi * 440.0 * t) + 0.05 * math.sin(2 * math.pi * 1000.0 * t)
        sig.append(v)
    return {"sample_rate_hz": sr, "channels": 1, "signal": sig, "valid": validate_pcm(sig, sr, 1)}


def audit_assets() -> Dict[str, Any]:
    probes = []
    for rel in ABSENCE_PROBES:
        p = SOURCE_ROOT / rel
        probes.append({"path": rel, "exists": p.exists()})
    present = [p for p in probes if p["exists"]]
    observed = {
        "absence_probes": probes,
        "present_probe_count": len(present),
        "all_absence_probes_absent": len(present) == 0,
    }
    return {
        "all_absence_probes_absent": observed["all_absence_probes_absent"],
        "audit_result": "absent" if observed["all_absence_probes_absent"] else "present_requires_review",
        "observed": observed,
        "qualified": False,
    }


CALLER_MANIFEST_FIELDS = (
    "scorer", "mode", "binary_path", "binary_sha256", "license_record_path",
    "license_record_sha256", "runtime_lock_path", "runtime_lock_sha256",
    "rights_record_path", "rights_record_sha256", "cohort_manifest_path",
    "cohort_manifest_sha256", "parity_vector_path", "parity_vector_sha256",
    "source_revision", "variant",
)
CALLER_MANIFEST_FILE_PAIRS = (
    ("binary_path", "binary_sha256"),
    ("license_record_path", "license_record_sha256"),
    ("runtime_lock_path", "runtime_lock_sha256"),
    ("rights_record_path", "rights_record_sha256"),
    ("cohort_manifest_path", "cohort_manifest_sha256"),
    ("parity_vector_path", "parity_vector_sha256"),
)


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    obj = _require_obj(manifest, "manifest")
    keys = tuple(sorted(obj.keys()))
    if keys != tuple(sorted(CALLER_MANIFEST_FIELDS)):
        raise Reject(f"manifest_keys_mismatch:expected={sorted(CALLER_MANIFEST_FIELDS)}:got={sorted(obj.keys())}")
    scorer = _require_str(obj["scorer"], "manifest.scorer").lower()
    if scorer not in SCORERS:
        raise Reject("manifest.scorer_unknown")
    mode = _require_str(obj["mode"], "manifest.mode")
    variant = _require_str(obj["variant"], "manifest.variant")
    if variant != "offline_reference_comparison":
        raise Reject("manifest.variant_unsupported")
    revision = _require_str(obj["source_revision"], "manifest.source_revision")
    if not _is_hex40(revision):
        raise Reject("manifest.source_revision_not_40hex")
    for path_field, sha_field in CALLER_MANIFEST_FILE_PAIRS:
        path = _require_str(obj[path_field], f"manifest.{path_field}")
        if not os.path.isabs(path):
            raise Reject(f"manifest.{path_field}_not_absolute")
        digest = _require_str(obj[sha_field], f"manifest.{sha_field}")
        if not _is_hex_sha256(digest):
            raise Reject(f"manifest.{sha_field}_not_sha256")
        p = Path(path)
        if not p.is_file():
            raise Reject(f"manifest.{path_field}_missing")
        actual = sha256_file(p)
        if actual != digest:
            raise Reject(f"manifest.{path_field}_digest_mismatch")
    return {
        "accepted_for_validation_only": True,
        "qualified": False,
        "scorer": scorer,
        "mode": mode,
        "variant": variant,
        "source_revision": revision,
    }


def adverse_cases() -> List[Dict[str, Any]]:
    cases = []
    def add(case_id: str, fn):
        try:
            fn()
        except Reject as exc:
            cases.append({"case": case_id, "result": "rejected", "reason": str(exc)})
            return
        except Exception as exc:  # pragma: no cover - fail closed
            cases.append({"case": case_id, "result": "rejected", "reason": f"unexpected:{type(exc).__name__}"})
            return
        cases.append({"case": case_id, "result": "accepted", "reason": "UNEXPECTED_ACCEPT"})

    add("pcm_empty", lambda: validate_pcm([], 16000, 1))
    add("pcm_none", lambda: validate_pcm(None, 16000, 1))  # type: ignore[arg-type]
    add("pcm_wrong_rate", lambda: validate_pcm([0.0], 12345, 1))
    add("pcm_nan", lambda: validate_pcm([0.0, float('nan')], 16000, 1))
    add("pcm_inf", lambda: validate_pcm([0.0, float('inf')], 16000, 1))
    add("pcm_out_of_range", lambda: validate_pcm([1.5], 16000, 1))
    add("pcm_bool", lambda: validate_pcm([True], 16000, 1))  # type: ignore[list-item]
    add("pcm_str", lambda: validate_pcm(["0.1"], 16000, 1))  # type: ignore[list-item]
    add("manifest_not_object", lambda: validate_caller_manifest([]))
    add("manifest_missing_field", lambda: validate_caller_manifest({k: "x" for k in CALLER_MANIFEST_FIELDS[:-1]}))
    add("manifest_extra_field", lambda: validate_caller_manifest({**{k: "/tmp/x" if k.endswith('_path') else '0'*64 for k in CALLER_MANIFEST_FIELDS}, "extra": 1}))
    add("manifest_bad_scorer", lambda: validate_caller_manifest(_bad_manifest(scorer="unknown")))
    add("manifest_bad_variant", lambda: validate_caller_manifest(_bad_manifest(variant="streaming")))
    add("manifest_bad_revision", lambda: validate_caller_manifest(_bad_manifest(source_revision="abc")))
    add("manifest_relative_path", lambda: validate_caller_manifest(_bad_manifest(binary_path="relative.bin")))
    add("manifest_bad_sha", lambda: validate_caller_manifest(_bad_manifest(binary_sha256="zzz")))
    add("manifest_missing_file", lambda: validate_caller_manifest(_bad_manifest(binary_path="/tmp/does-not-exist-sdk-pesq-polqa-3quest.bin")))
    return cases


def _bad_manifest(**overrides: Any) -> Dict[str, Any]:
    base = {k: ("/tmp/nonexistent-sdk-pesq" if k.endswith('_path') else ('a'*40 if k=='source_revision' else ('0'*64 if k.endswith('_sha256') else ('pesq' if k=='scorer' else ('nb' if k=='mode' else 'offline_reference_comparison'))))) for k in CALLER_MANIFEST_FIELDS}
    base.update(overrides)
    return base


def task_row_identity() -> Dict[str, Any]:
    tasks_path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    data = json.loads(tasks_path.read_text(encoding="utf-8"))
    row = None
    for task in data.get("tasks", []):
        if task.get("id") == TASK:
            row = task
            break
    if row is None:
        raise Reject("task_row_not_found")
    stable = {k: row[k] for k in STABLE_TASK_FIELDS if k in row}
    claim = row.get("claim") or {}
    identity = {
        "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "stable_fields": stable,
        "claim": {k: claim.get(k) for k in ("base_commit", "branch", "reviewer", "worktree")},
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "whole_file_hashed": False,
    }
    identity["stable_sha256"] = sha256_bytes(canonical_bytes(stable))
    return identity


def gates() -> List[Dict[str, Any]]:
    return [{"id": gid, "requirement": req, "status": "blocked"} for gid, req in GATE_REQUIREMENTS]


def qualification() -> Dict[str, Any]:
    gate_ids = [g["id"] for g in gates()]
    return {
        "status": QUALIFICATION,
        "decision": DECISION,
        "candidate_qualified": False,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "blocked_gate_count": len(gate_ids),
        "blocked_gate_ids": gate_ids,
        "reason": QUALIFICATION_REASON,
    }


def build_report() -> Dict[str, Any]:
    pcm = synthetic_control_pcm()
    controls = adverse_cases()
    all_rejected = all(c["result"] == "rejected" for c in controls)
    asset_audit = audit_assets()
    identity = task_row_identity()
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "mode": MODE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": qualification(),
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "non_claims": list(NON_CLAIMS),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "asset_requirements": [dict(x) for x in ASSET_REQUIREMENTS],
        "exact_blockers": [dict(x) for x in EXACT_BLOCKERS],
        "gates": gates(),
        "asset_audit": asset_audit,
        "task_row_identity": identity,
        "reference_protocol": {
            "model_executed": False,
            "synthetic_control": {
                "kind": "deterministic_synthetic_pcm_accounting_only",
                "not_speech": True,
                "not_score": True,
                "qualification_effect": "none",
                **pcm["valid"],
            },
            "adverse_controls": controls,
            "adverse_all_rejected": all_rejected,
        },
        "source_reported_context": SOURCE_REPORTED_CONTEXT,
        "format": {
            "sdk_v0_sample_rate_hz": 16000,
            "sdk_v0_channels": 1,
            "sdk_v0_frame_samples": 160,
            "sdk_v0_sample_format": "f32",
            "sdk_v0_geometry_preserved": True,
            "scorer_execution": "none",
        },
    }


def build_contract() -> Dict[str, Any]:
    report = build_report()
    return {
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "mode": MODE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "proposal_only": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": report["qualification"],
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "non_claims": list(NON_CLAIMS),
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "asset_requirements": [dict(x) for x in ASSET_REQUIREMENTS],
        "exact_blockers": [dict(x) for x in EXACT_BLOCKERS],
        "gates": report["gates"],
        "task_row_identity": report["task_row_identity"],
        "caller_manifest_contract": {
            "contract_id": "audio-sdk/pesq-polqa-and-3quest/caller-supplied-scorer-manifest/0.1",
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "required_variant": "offline_reference_comparison",
            "accepted_scorers": list(SCORERS),
            "absent_behavior": "reject_before_processing",
            "present_behavior": "validate_only_no_execution_no_network",
            "asset_is_vendored": False,
        },
        "reproduction": {
            "command": "python3 run.py all",
            "tests": "python3 -m unittest -v test_reference.py",
            "verify": "python3 verify.py",
            "cold_start_regenerations": 3,
            "report_sha256_sidecar": "report.json.sha256",
            "sources_manifest": "SOURCES.sha256",
        },
    }
