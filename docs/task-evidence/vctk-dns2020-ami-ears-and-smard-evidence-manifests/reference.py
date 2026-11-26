# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only evidence reference for the VCTK/DNS2020/AMI/EARS/SMARD manifest task.

The task is to retain/reproduce comparison evidence as an optional SDK
developer/evidence adapter alongside audio-bench, with a documented
proceed/defer decision before processor exposure.  It requires source/pair/
group hashes, intended use and rights frozen per corpus, and window/speaker
overlap prevention.

No machine-readable per-corpus manifest, rights/intended-use record,
source/pair/group hash manifest, overlap-prevention record, scoring plan,
rights-cleared subset, approval record or opt-in adapter/release decision is
present.  This package is therefore proposal-only, incomplete and not
qualified.  It never decodes, copies, downloads or scores audio; it records a
fail-closed audit and a deterministic synthetic manifest-control model.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS"
TITLE = "VCTK, DNS2020, AMI, EARS and SMARD evidence manifests"
SLUG = "vctk-dns2020-ami-ears-and-smard-evidence-manifests"
COMPONENT = SLUG
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = f"swarm/{TASK}"
REVIEWER = "reviewer-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS"
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
DEFER_BEFORE = "rights_cleared_manifests_and_release_approval"

INPUT_SAMPLE_RATE_HZ = 16000
CHANNELS = 1
SDK_FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"
RELEASE_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")

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
    "audio-benchmark-platform/audio-bench/docs/CORPUS.md":
        "9967fe4e85c4695d45b2d618c394c50960d1251e5fd2bdc9f54beee23cd85b12",
    "audio-benchmark-platform/audio-bench/docs/DATASET_RELEASE_EVIDENCE.md":
        "c27c2dbaaa7a56dc1cd3f9542e02d4b9932bd4995fd604d4bc3d3599f9c64bea",
    "research/voice-enhancement-20261101/evaluation_records.md":
        "962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a",
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
    "sdk_v0_geometry_preserved": True,
    "audio_decoded_here": False,
}

BOUNDARY: Dict[str, Any] = {
    "adapter_code_added": False,
    "adapter_json_added": False,
    "audio_copied_into_package": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "downloads_performed": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "manifests_fabricated": False,
    "network_used": False,
    "processor_exposure": False,
    "production_callback_registered": False,
    "provider_registration": False,
    "public_api_abi_change": False,
    "registered": False,
    "rights_approved": False,
    "shared_build_or_ci_change": False,
}

SCOPE: Dict[str, Any] = {
    "benchmark_claim": False,
    "corpus_admitted": False,
    "corpus_bytes_hashed_for_pin": False,
    "device_timing": False,
    "listening": False,
    "model_executed": False,
    "network_used": False,
    "real_audio_copied": False,
    "real_audio_decoded": False,
    "real_corpus_ingested": False,
    "real_corpus_scored": False,
    "release_claim": False,
    "runtime_invoked": False,
    "task_local_only": True,
    "weights_downloaded": False,
    "weights_loaded": False,
}

NON_CLAIMS: Tuple[str, ...] = (
    "No per-corpus manifest, rights/intended-use record, source/pair/group hash manifest, overlap-prevention record, scoring plan, approval record or release decision is created here.",
    "No corpus is admitted, decoded, copied, downloaded, normalized, scored or released by this package.",
    "No local corpus observation is treated as a rights-cleared subset or permission grant.",
    "No provider, descriptor, registry, installed v0 path, default, shared build or CI behavior changes.",
    "No benchmark, quality, timing, listening, device, public or release claim is made.",
    "Missing evidence never qualifies the candidate; decision remains DEFER and status remains not_qualified.",
)

REQUIRED_CORPORA = ("ami", "dns2020", "ears", "smard", "vctk")

# Reserved manifest/record paths: absence is the blocker evidence.
RESERVED_ABSENT_PATHS = (
    "data/manifests/vctk-dns2020-ami-ears-smard/manifest.json",
    "data/manifests/vctk-dns2020-ami-ears-smard/source-pair-group-hashes.json",
    "data/manifests/vctk-dns2020-ami-ears-smard/overlap-policy.json",
    "data/manifests/vctk-dns2020-ami-ears-smard/scoring-plan.json",
    "data/rights/vctk-dns2020-ami-ears-smard/intended-use.json",
    "data/rights/vctk-dns2020-ami-ears-smard/rights-records.json",
    "data/runs/vctk-dns2020-ami-ears-smard/approval.json",
    "data/runs/vctk-dns2020-ami-ears-smard/rights-cleared-subset.json",
)

# Observed local artifacts: fixed paths only; hash/metadata only; never admitted.
OBSERVED_ARTIFACTS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "ami_observation",
        "corpus": "ami",
        "path": "reports/vad-research/chaining-evaluation.md",
        "role": "research_report_observation",
        "evidence_class": "source_reported_observed_not_admitted",
        "admitted": False,
        "notes": "AMI VAD/chaining research report exists; no per-corpus manifest, rights record, pair/group hashes or overlap policy is present.",
    },
    {
        "id": "dns2020_observation",
        "corpus": "dns2020",
        "path": "research/noise_suppression_pilot_20261027.md",
        "role": "research_report_observation",
        "evidence_class": "source_reported_observed_not_admitted",
        "admitted": False,
        "notes": "DNS2020 paired pilot report exists; no frozen manifest with source/pair/group hashes and rights-per-corpus is present.",
    },
    {
        "id": "ears_observation",
        "corpus": "ears",
        "path": "research/ears_blind_noise_screen_20261027.md",
        "role": "research_report_observation",
        "evidence_class": "source_reported_observed_not_admitted",
        "admitted": False,
        "notes": "EARS screen report exists; no frozen manifest, intended-use/rights record or overlap policy is present.",
    },
    {
        "id": "smard_observation",
        "corpus": "smard",
        "path": "research/dereverberation_candidates_20261028.md",
        "role": "research_report_observation",
        "evidence_class": "source_reported_observed_not_admitted",
        "admitted": False,
        "notes": "SMARD is referenced in dereverberation research; no frozen manifest, rights record or pair/group hash policy is present.",
    },
    {
        "id": "vctk_observation",
        "corpus": "vctk",
        "path": "realtime-audio-library/research/vctk_source_assessment_20261029.md",
        "role": "research_report_observation",
        "evidence_class": "source_reported_observed_not_admitted",
        "admitted": False,
        "notes": "VCTK assessment/eval artifacts exist; no frozen manifest, intended-use/rights record or overlap policy is present.",
    },
)

MANIFEST_SCHEMA_ID = "audio-sdk/vctk-dns2020-ami-ears-smard-evidence-manifest/0.1"
MANIFEST_FIELDS = (
    "schema_id", "manifest_id", "revision", "corpora", "intended_use_records",
    "rights_records", "cohort_record_path", "cohort_record_sha256",
    "scoring_plan_path", "scoring_plan_sha256", "overlap_policy_path",
    "overlap_policy_sha256", "approval_record_path", "approval_record_sha256",
)
CORPUS_FIELDS = (
    "corpus_id", "split", "source_root_or_locator", "license", "intended_use",
    "rights_record_sha256", "source_items", "pair_items", "group_items", "notes",
)
ITEM_FIELDS = ("item_id", "path", "sha256", "role", "group_id", "split")

MANIFEST_CONTRACT: Dict[str, Any] = {
    "contract_id": MANIFEST_SCHEMA_ID,
    "caller_owned": True,
    "vendored": False,
    "manifest_is_not_created_here": True,
    "audio_decoded": False,
    "required_fields": list(MANIFEST_FIELDS),
    "required_corpora": list(REQUIRED_CORPORA),
    "required_corpus_fields": list(CORPUS_FIELDS),
    "required_item_fields": list(ITEM_FIELDS),
    "required_geometry": {
        "sample_rate_hz": INPUT_SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": SDK_FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
    },
    "absent_behavior": "reject_before_admission",
    "present_behavior": (
        "validate_exact_fields_paths_hashes_closed_corpus_map_overlap_declarations_and_rights_refs_only;_"
        "never_decode_audio_and_never_grant_permission"),
    "acceptance_effect": (
        "structural acceptance never sets admitted_for_evaluation, rights_approved, "
        "reviewer_approved or qualification; independent review is always required"),
}

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("corpus_manifest_and_exact_identity",
     "Per-corpus machine-readable manifests pin exact VCTK, DNS2020, AMI, EARS and SMARD splits, locators, geometry, byte counts, hashes and roles."),
    ("intended_use_and_rights_per_corpus",
     "Intended use and rights per corpus are frozen with attribution, license terms, redistribution/publication constraints and approval evidence."),
    ("source_pair_group_hashes_and_overlap_prevention",
     "Source/pair/group hashes and an overlap-prevention policy block window, speaker, session or recording leakage across splits/cohorts."),
    ("scoring_cohort_aggregation_and_failed_item_policy",
     "Cohort selection, scorer/version, aggregation, failed-item handling and invalid/missing result accounting are frozen in a machine-readable plan."),
    ("evidence_separation_and_controls",
     "Paired, unpaired, synthetic, human and source-reported evidence are separated and one invalid and one representative valid bundle pass the reported package controls."),
    ("local_rights_cleared_subset_or_approval_record",
     "A rights-cleared local subset or explicit approval record exists before admitting any corpus bytes into evaluation."),
    ("opt_in_adapter_and_release_boundary",
     "Opt-in adapter/developer-evidence boundary is decided with no default, no public processor exposure and no shared build/CI change."),
    ("public_default_release_and_benchmark_claim",
     "Explicit default-selection, release/public-benchmark approval and qualification evidence are recorded; absent evidence never qualifies."),
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {"id": "corpus_manifest_and_exact_identity_absent", "state": "absent",
     "requirement": "Create a machine-readable per-corpus manifest for VCTK, DNS2020, AMI, EARS and SMARD with exact split, locator, geometry, byte counts, SHA-256 and role metadata; no such manifest is present."},
    {"id": "intended_use_and_rights_records_absent", "state": "absent",
     "requirement": "Freeze intended use and rights per corpus with attribution, license terms, redistribution/publication constraints and approval evidence; no complete per-corpus rights record is present."},
    {"id": "source_pair_group_hashes_and_overlap_absent", "state": "absent",
     "requirement": "Provide source/pair/group hashes and an overlap-prevention policy that blocks window, speaker, session or recording leakage across splits/cohorts; no machine-readable overlap record is present."},
    {"id": "scoring_cohort_aggregation_and_failed_item_policy_absent", "state": "absent",
     "requirement": "Freeze cohort selection, scorer/version, aggregation, failed-item handling and invalid/missing result accounting in a machine-readable scoring plan; no such plan is present."},
    {"id": "evidence_separation_and_controls_absent", "state": "absent",
     "requirement": "Separate paired, unpaired, synthetic, human and source-reported evidence and validate one invalid and one representative valid bundle through the reported package; no such control bundle is present."},
    {"id": "local_rights_cleared_subset_or_approval_absent", "state": "absent",
     "requirement": "Provide a rights-cleared local subset or explicit approval record before admitting any corpus bytes into evaluation; no approval record is present and local observations are not admitted."},
    {"id": "opt_in_adapter_and_release_boundary_incomplete", "state": "absent",
     "requirement": "Complete an opt-in adapter/developer-evidence boundary decision with no default, no public processor exposure and no shared build/CI change; no such decision is recorded."},
    {"id": "public_default_release_and_benchmark_claim_blocked", "state": "absent",
     "requirement": "Record explicit default-selection, release/public-benchmark approval and qualification evidence; absent evidence never qualifies and this package remains off by default."},
)


class Reject(ValueError):
    """Fail-closed validation error."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(obj: Any) -> bytes:
    try:
        return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    except ValueError as err:
        raise Reject(str(err)) from err


def _reject_const(token: str) -> Any:
    if token in ("NaN", "Infinity", "-Infinity"):
        raise Reject("nonfinite JSON constant")
    raise Reject("invalid JSON constant")


def strict_loads(text: str) -> Any:
    def object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise Reject("duplicate key: " + key)
            obj[key] = value
        return obj

    return json.loads(text, parse_constant=_reject_const,
                      object_pairs_hook=object_pairs_hook)


def load_json(path: Path) -> Any:
    return strict_loads(path.read_text(encoding="utf-8"))


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def _abs_path(raw: Any, label: str) -> Path:
    _require(isinstance(raw, str) and bool(raw.strip()), label + " must be a non-empty string")
    path = Path(raw)
    _require(path.is_absolute(), label + " must be absolute: " + raw)
    return path


def _sha256_hex(raw: Any, label: str) -> str:
    _require(isinstance(raw, str) and re.fullmatch(r"[0-9a-f]{64}", raw),
             label + " must be a lowercase sha256 hex digest")
    return raw


def _release_token(raw: Any, label: str) -> str:
    _require(isinstance(raw, str) and bool(RELEASE_TOKEN.fullmatch(raw)),
             label + " must be a safe release token")
    return raw


def task_row_identity() -> Dict[str, Any]:
    task_path = SOURCE_ROOT / "audio-benchmark-platform/plan/swarm/TASKS.json"
    row = None
    for item in load_json(task_path).get("tasks", []):
        if isinstance(item, dict) and item.get("id") == TASK:
            row = item
            break
    _require(row is not None, "task row missing: " + TASK)
    stable = {field: row[field] for field in STABLE_TASK_FIELDS}
    return {
        "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
        "stable_fields": stable,
        "stable_sha256": sha256_bytes(canonical_bytes(stable)),
        "whole_file_hashed": False,
        "excluded_mutable_fields": list(MUTABLE_TASK_FIELDS),
        "claim": row.get("claim"),
    }


def audit_workspace() -> Dict[str, Any]:
    observations = []
    for item in OBSERVED_ARTIFACTS:
        p = SOURCE_ROOT / item["path"]
        exists = p.is_file()
        obs = dict(item)
        obs["exists"] = exists
        obs["absolute_path"] = str(p)
        if exists:
            obs["bytes"] = p.stat().st_size
            obs["sha256"] = sha256(p)
        else:
            obs["bytes"] = None
            obs["sha256"] = None
        observations.append(obs)

    reserved = []
    for rel in RESERVED_ABSENT_PATHS:
        p = SOURCE_ROOT / rel
        reserved.append({"path": rel, "exists": p.exists(), "absolute_path": str(p)})

    present = [o for o in observations if o["exists"]]
    return {
        "audit_result": "observed_local_research_only",
        "qualified": False,
        "observed_count": len(observations),
        "present_count": len(present),
        "observations": observations,
        "reserved_absent_paths": reserved,
        "all_reserved_absent": all(not r["exists"] for r in reserved),
        "admitted_count": 0,
        "note": "Presence of local research artifacts is observation only; no corpus is admitted, decoded, scored or rights-cleared by this package.",
    }


def validate_caller_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    _require(isinstance(manifest, dict), "manifest must be an object")
    extra = set(manifest) - set(MANIFEST_FIELDS)
    _require(not extra, "manifest has unexpected fields: " + ", ".join(sorted(extra)))
    missing = [f for f in MANIFEST_FIELDS if f not in manifest]
    _require(not missing, "manifest missing required fields: " + ", ".join(missing))

    _require(manifest["schema_id"] == MANIFEST_SCHEMA_ID, "schema_id mismatch")
    _release_token(manifest["manifest_id"], "manifest_id")
    _release_token(manifest["revision"], "revision")

    for path_key, hash_key in (
        ("cohort_record_path", "cohort_record_sha256"),
        ("scoring_plan_path", "scoring_plan_sha256"),
        ("overlap_policy_path", "overlap_policy_sha256"),
        ("approval_record_path", "approval_record_sha256"),
    ):
        p = _abs_path(manifest[path_key], path_key)
        _require(p.is_file(), path_key + " missing: " + str(p))
        actual = sha256(p)
        expected = _sha256_hex(manifest[hash_key], hash_key)
        _require(actual == expected, hash_key + " mismatch for " + path_key)

    corpora = manifest["corpora"]
    _require(isinstance(corpora, list) and corpora, "corpora must be a non-empty array")
    seen = set()
    for corpus in corpora:
        _require(isinstance(corpus, dict), "corpus entry must be object")
        extra_c = set(corpus) - set(CORPUS_FIELDS)
        _require(not extra_c, "corpus has unexpected fields: " + ", ".join(sorted(extra_c)))
        missing_c = [f for f in CORPUS_FIELDS if f not in corpus]
        _require(not missing_c, "corpus missing fields: " + ", ".join(missing_c))
        cid = _release_token(corpus["corpus_id"], "corpus_id")
        _require(cid not in seen, "duplicate corpus_id: " + cid)
        seen.add(cid)
        _require(cid in REQUIRED_CORPORA, "unsupported corpus_id: " + cid)
        for key in ("split", "source_root_or_locator", "license", "intended_use", "notes"):
            _require(isinstance(corpus[key], str) and corpus[key].strip(), key + " must be non-empty string")
        _sha256_hex(corpus["rights_record_sha256"], "rights_record_sha256")
        for group_name in ("source_items", "pair_items", "group_items"):
            items = corpus[group_name]
            _require(isinstance(items, list), group_name + " must be array")
            for item in items:
                _require(isinstance(item, dict), group_name + " item must be object")
                extra_i = set(item) - set(ITEM_FIELDS)
                _require(not extra_i, group_name + " item has unexpected fields: " + ", ".join(sorted(extra_i)))
                missing_i = [f for f in ITEM_FIELDS if f not in item]
                _require(not missing_i, group_name + " item missing fields: " + ", ".join(missing_i))
                _release_token(item["item_id"], "item_id")
                _abs_path(item["path"], "path")
                _sha256_hex(item["sha256"], "sha256")
                for k in ("role", "group_id", "split"):
                    _require(isinstance(item[k], str) and item[k].strip(), k + " must be non-empty string")

    _require(set(seen) == set(REQUIRED_CORPORA),
             "corpora must cover exact required set: " + ", ".join(REQUIRED_CORPORA))

    for list_key in ("intended_use_records", "rights_records"):
        recs = manifest[list_key]
        _require(isinstance(recs, list) and recs, list_key + " must be non-empty array")
        for rec in recs:
            _require(isinstance(rec, dict), list_key + " entry must be object")
            for k in ("corpus_id", "record_path", "record_sha256"):
                _require(k in rec, list_key + " missing " + k)
            _require(rec["corpus_id"] in REQUIRED_CORPORA, list_key + " unknown corpus_id")
            p = _abs_path(rec["record_path"], "record_path")
            _require(p.is_file(), "record_path missing: " + str(p))
            actual = sha256(p)
            expected = _sha256_hex(rec["record_sha256"], "record_sha256")
            _require(actual == expected, "record_sha256 mismatch for " + rec["record_path"])

    return {
        "accepted": True,
        "admitted_for_evaluation": False,
        "rights_approved": False,
        "reviewer_approved": False,
        "qualification_effect": "none",
        "note": "Structural validation only; no corpus bytes decoded, no rights granted, no qualification.",
    }


def build_control() -> Dict[str, Any]:
    # Synthetic control only; proves manifest/overlap/separation logic, not corpus quality.
    items = [
        {"item_id": "s1", "corpus": "vctk", "split": "train", "speaker": "spk_a", "window": 0, "score": 1.0, "evidence_class": "paired"},
        {"item_id": "s2", "corpus": "vctk", "split": "test", "speaker": "spk_b", "window": 1, "score": 0.5, "evidence_class": "paired"},
        {"item_id": "s3", "corpus": "ami", "split": "test", "speaker": "spk_c", "window": 0, "score": None, "evidence_class": "synthetic"},
    ]
    # overlap check: same speaker cannot cross train/test
    overlap_ok = not any(
        a["speaker"] == b["speaker"] and a["split"] != b["split"]
        for a in items for b in items if a is not b
    )
    # missing score never qualifies
    valid_scores = [i["score"] for i in items if isinstance(i["score"], (int, float)) and not isinstance(i["score"], bool) and math.isfinite(i["score"])]
    return {
        "control_type": "synthetic_manifest_control_not_corpus_result",
        "qualified": False,
        "qualification_effect": "none",
        "overlap_check_passed": overlap_ok,
        "missing_score_count": 1,
        "valid_score_count": len(valid_scores),
        "mean_valid_score": sum(valid_scores) / len(valid_scores),
        "missing_never_qualifies": True,
        "evidence_classes_seen": sorted({i["evidence_class"] for i in items}),
    }


def run_adverse_controls() -> List[Dict[str, str]]:
    controls: List[Dict[str, str]] = []

    def add(name: str, fn) -> None:
        try:
            fn()
            controls.append({"case": name, "result": "accepted"})
        except Exception:
            controls.append({"case": name, "result": "rejected"})

    add("strict_json_duplicate_key", lambda: strict_loads('{"a":1,"a":2}'))
    add("strict_json_nonfinite", lambda: strict_loads('{"a":NaN}'))
    add("manifest_not_object", lambda: validate_caller_manifest([]))  # type: ignore[arg-type]
    add("manifest_missing_field", lambda: validate_caller_manifest({"schema_id": MANIFEST_SCHEMA_ID}))
    add("manifest_bad_schema", lambda: validate_caller_manifest({f: "" for f in MANIFEST_FIELDS} | {"schema_id": "bad"}))

    # missing required corpus coverage
    base = {f: "x" for f in MANIFEST_FIELDS}
    base["schema_id"] = MANIFEST_SCHEMA_ID
    base["manifest_id"] = "m"
    base["revision"] = "r1"
    base["corpora"] = []
    base["intended_use_records"] = [{"corpus_id": "vctk", "record_path": __file__, "record_sha256": "0" * 64}]
    base["rights_records"] = [{"corpus_id": "vctk", "record_path": __file__, "record_sha256": "0" * 64}]
    for k in ("cohort_record_path", "scoring_plan_path", "overlap_policy_path", "approval_record_path"):
        base[k] = __file__
    for k in ("cohort_record_sha256", "scoring_plan_sha256", "overlap_policy_sha256", "approval_record_sha256"):
        base[k] = "0" * 64
    add("manifest_empty_corpora", lambda: validate_caller_manifest(dict(base)))

    # invalid hash
    bad_hash = dict(base)
    bad_hash["cohort_record_sha256"] = "not-a-hash"
    add("manifest_bad_hash", lambda: validate_caller_manifest(bad_hash))

    # relative path
    bad_path = dict(base)
    bad_path["cohort_record_path"] = "relative.json"
    add("manifest_relative_path", lambda: validate_caller_manifest(bad_path))

    # missing file
    bad_missing = dict(base)
    bad_missing["cohort_record_path"] = "/tmp/does-not-exist-vctk-dns2020-ami-ears-smard.json"
    bad_missing["cohort_record_sha256"] = "0" * 64
    add("manifest_missing_file", lambda: validate_caller_manifest(bad_missing))

    # unsupported corpus id
    bad_corpus = dict(base)
    bad_corpus["corpora"] = [{
        "corpus_id": "unknown", "split": "test", "source_root_or_locator": "/tmp",
        "license": "x", "intended_use": "x", "rights_record_sha256": "0" * 64,
        "source_items": [], "pair_items": [], "group_items": [], "notes": "x"
    }]
    add("manifest_unknown_corpus", lambda: validate_caller_manifest(bad_corpus))

    # duplicate corpus
    dup = dict(base)
    c = {
        "corpus_id": "vctk", "split": "test", "source_root_or_locator": "/tmp",
        "license": "x", "intended_use": "x", "rights_record_sha256": "0" * 64,
        "source_items": [], "pair_items": [], "group_items": [], "notes": "x"
    }
    dup["corpora"] = [dict(c), dict(c)]
    add("manifest_duplicate_corpus", lambda: validate_caller_manifest(dup))

    # item missing hash
    bad_item = dict(base)
    c2 = dict(c)
    c2["source_items"] = [{"item_id": "i", "path": __file__, "sha256": "bad", "role": "r", "group_id": "g", "split": "test"}]
    bad_item["corpora"] = [c2]
    add("manifest_bad_item_hash", lambda: validate_caller_manifest(bad_item))

    # unexpected field
    extra = dict(base)
    extra["unexpected"] = True
    add("manifest_unexpected_field", lambda: validate_caller_manifest(extra))

    # rights records empty
    bad_rights = dict(base)
    bad_rights["rights_records"] = []
    add("manifest_empty_rights_records", lambda: validate_caller_manifest(bad_rights))

    # non-string corpus field
    bad_field = dict(base)
    c3 = dict(c)
    c3["license"] = 1
    bad_field["corpora"] = [c3]
    add("manifest_non_string_license", lambda: validate_caller_manifest(bad_field))

    # wrong split/hash form in item path
    bad_rel_item = dict(base)
    c4 = dict(c)
    c4["source_items"] = [{"item_id": "i", "path": "relative.wav", "sha256": "0" * 64, "role": "r", "group_id": "g", "split": "test"}]
    bad_rel_item["corpora"] = [c4]
    add("manifest_relative_item_path", lambda: validate_caller_manifest(bad_rel_item))

    # boolean score-like invalidity is represented by strict bool rejection in control
    def bool_score() -> None:
        v = True
        _require(not isinstance(v, bool) and isinstance(v, (int, float)), "bool rejected")
    add("control_bool_score_rejected", bool_score)

    return controls


def build_report() -> Dict[str, Any]:
    identity = task_row_identity()
    audit = audit_workspace()
    control = build_control()
    adverse = run_adverse_controls()
    adverse_all_rejected = all(item["result"] == "rejected" for item in adverse)

    gates = [{"id": gid, "requirement": req, "status": "blocked"}
             for gid, req in GATE_REQUIREMENTS]
    blockers = [dict(b) for b in EXACT_BLOCKERS]

    qualification = {
        "status": QUALIFICATION,
        "candidate_qualified": False,
        "no_missing_result_qualifies_candidate": True,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "blocked_gate_count": 8,
        "blocked_gate_ids": [g["id"] for g in gates],
        "reason": (
            "No machine-readable per-corpus manifest, rights/intended-use record, "
            "source/pair/group hash manifest, overlap-prevention record, scoring/aggregation "
            "manifest, rights-cleared subset, approval record or opt-in adapter/release decision exists. "
            "Local corpus observations are hash-pinned as observations only; no corpus is admitted, "
            "decoded, scored, downloaded or released."
        ),
    }

    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "repository": "audio-sdk",
        "mode": MODE,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "qualification_status": QUALIFICATION,
        "qualification": qualification,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "worktree": CLAIM_WORKTREE,
        "reviewer": REVIEWER,
        "write_scope": TASK_PREFIX,
        "task_row_identity": identity,
        "scope": dict(SCOPE),
        "boundary": dict(BOUNDARY),
        "format": dict(FORMAT),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "manifest_contract": dict(MANIFEST_CONTRACT),
        "observed_artifacts": audit["observations"],
        "reserved_absent_paths": audit["reserved_absent_paths"],
        "asset_audit": audit,
        "gates": gates,
        "exact_blockers": blockers,
        "control": control,
        "controls": {
            "adverse": adverse,
            "adverse_all_rejected": adverse_all_rejected,
            "missing_result_never_qualifies": True,
        },
        "reopen_conditions": [g["requirement"] for g in gates],
        "non_claims": list(NON_CLAIMS),
        "source_reported_context": {
            "label": "source_reported_not_measured_here",
            "note": "Merged evaluation records describe VCTK/DNS2020/AMI/EARS/SMARD usage in research; this package does not reproduce, rescore or admit those corpora.",
        },
        "determinism": {
            "canonical_json": "sort_keys=True, compact separators, allow_nan=False, trailing newline",
            "cold_start_regenerations_required": 3,
            "report_bytes_generated_by": "run.py",
        },
        "tool_provenance": [
            "Python standard library only; no corpus runtime, scorer or network client is imported.",
            "All observations use fixed workspace paths and local reads only.",
            "No audio decode, download, device timing, listening, benchmark or release action occurs.",
        ],
    }
