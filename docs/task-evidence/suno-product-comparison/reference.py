# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local blocker evidence for SDK-SUNO-PRODUCT-COMPARISON.

Suno is a product comparison / external market-context candidate. This package
records an explicit DEFER / incomplete / not_qualified decision because no
licensed, pinned, reproducible Suno source/runtime/output bundle is present for
an SDK adapter or processor qualification claim. The referenced market benchmark
is source-only context; it is not executable SDK evidence, not a rights-cleared
audio corpus, not device/runtime timing, and not a release claim.

The package is deterministic and stdlib-only. It does not download, copy,
import, load, execute, or vendor Suno code, weights, models, APIs, corpora, or
outputs. It does not register a provider, change installed v0 behavior, change
public ABI/contracts/descriptors/registries/defaults/shared build/CI, or make
benchmark/listening/timing/release claims.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]

TASK = "SDK-SUNO-PRODUCT-COMPARISON"
TITLE = "Suno product comparison"
SLUG = "suno-product-comparison"
COMPONENT = "suno-product-comparison"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "26bc48c58f9d69571571fa651862dcbe0fe1172d"
BRANCH = f"swarm/{TASK}"
REVIEWER = f"reviewer-{TASK.replace('SDK-', '')}"
CLAIM_WORKTREE = (
    "/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/"
    "SDK-SUNO-PRODUCT-COMPARISON"
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "external"
STATUS = "proposal_only_blocked_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "exact_source_rights_runtime_and_comparison_admission"

INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
MARKET_BENCHMARK_PATH = "research/cpp-lib-market-benchmark-20261109.md"

BOARD_ROW_STABLE_FIELDS: Dict[str, Any] = {
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE"],
    "id": TASK,
    "mode": "research-control",
    "repository": "audio-sdk",
    "title": TITLE,
}
BOARD_ROW_STABLE_SHA256 = (
    "4f76f45c33137b403b02176ab535f62ca89393ad28c7491240524d1f09488340")

SPDX_LI = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPY = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"

def board_row_digest() -> str:
    raw = json.dumps(BOARD_ROW_STABLE_FIELDS, sort_keys=True,
                     separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes())

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"

def _reject_constant(value: str) -> Any:
    raise ValueError(f"nonfinite_json_constant:{value}")

def strict_loads(text: str) -> Any:
    def object_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"duplicate_key:{key}")
            obj[key] = value
        return obj

    decoder = json.JSONDecoder(object_pairs_hook=object_pairs_hook,
                               parse_constant=_reject_constant)
    value, end = decoder.raw_decode(text)
    if text[end:].strip():
        raise ValueError("trailing_content")
    if not isinstance(value, dict):
        raise ValueError("root_not_object")
    return value

def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(has_negative_zero(v) for v in value)
    return False

def resolve_source_path(name: str) -> Path:
    env = os.environ.get("SOURCE_ROOT")
    if env:
        return Path(env) / name
    return SDK_ROOT.parents[2] / name

# ---------------------------------------------------------------------------
# Deterministic comparison evidence surrogate
# ---------------------------------------------------------------------------

# Fixed, synthetic comparison records used only to verify fail-closed handling
# of comparison metadata. These are NOT Suno outputs, not audio, not quality
# scores, and not release evidence.
COMPARISON_RECORDS: Tuple[Dict[str, Any], ...] = (
    {
        "candidate": "suno-product-comparison",
        "claim_type": "market_context",
        "evidence_kind": "source_only_research_note",
        "license_pinned": False,
        "outputs_present": False,
        "runtime_present": False,
        "weights_present": False,
    },
    {
        "candidate": "cpp-lib",
        "claim_type": "local_engineering_evidence",
        "evidence_kind": "separate_project_report",
        "license_pinned": False,
        "outputs_present": False,
        "runtime_present": False,
        "weights_present": False,
    },
)

REQUIRED_RECORD_FIELDS = {
    "candidate", "claim_type", "evidence_kind", "license_pinned",
    "outputs_present", "runtime_present", "weights_present",
}

def validate_record(record: Any) -> Dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("record_not_object")
    if set(record.keys()) != REQUIRED_RECORD_FIELDS:
        raise ValueError("record_field_set_mismatch")
    for k in ("candidate", "claim_type", "evidence_kind"):
        v = record[k]
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"record_string_invalid:{k}")
    for k in ("license_pinned", "outputs_present", "runtime_present", "weights_present"):
        v = record[k]
        if not isinstance(v, bool):
            raise ValueError(f"record_bool_invalid:{k}")
    return {k: record[k] for k in sorted(record.keys())}

def deterministic_comparison_digest(records: Sequence[Dict[str, Any]]) -> str:
    normalized = [validate_record(r) for r in records]
    return sha256(canonical_bytes(normalized))

# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

def comparison_control() -> Dict[str, Any]:
    digest = deterministic_comparison_digest(COMPARISON_RECORDS)
    digest2 = deterministic_comparison_digest(list(COMPARISON_RECORDS))
    return {
        "byte_identical_digest": digest == digest2,
        "digest": digest,
        "record_count": len(COMPARISON_RECORDS),
        "records_valid": True,
    }

def record_adverse_control() -> Dict[str, Any]:
    cases: Dict[str, str] = {}

    def reject(name: str, record: Any) -> None:
        try:
            validate_record(record)
            cases[name] = "accepted"
        except Exception as exc:
            cases[name] = str(exc)

    base = dict(COMPARISON_RECORDS[0])
    reject("not_object", ["bad"])
    bad = dict(base)
    del bad["candidate"]
    reject("missing_field", bad)
    bad = dict(base)
    bad["extra"] = 1
    reject("extra_field", bad)
    reject("candidate_empty", {**base, "candidate": ""})
    reject("candidate_bool", {**base, "candidate": True})
    reject("license_pinned_string", {**base, "license_pinned": "false"})
    reject("outputs_present_int", {**base, "outputs_present": 1})
    reject("runtime_present_null", {**base, "runtime_present": None})
    reject("weights_present_float", {**base, "weights_present": 0.0})
    return {
        "rejected_all": all(v != "accepted" for v in cases.values()),
        "rejections": cases,
    }

def nonfinite_control() -> Dict[str, Any]:
    bad_cases = {
        "nan": '{"a": NaN}',
        "inf": '{"a": Infinity}',
        "neginf": '{"a": -Infinity}',
    }
    rejections: Dict[str, str] = {}
    for name, text in bad_cases.items():
        try:
            strict_loads(text)
            rejections[name] = "accepted"
        except Exception as exc:
            rejections[name] = str(exc)
    return {
        "rejected_all": all(v != "accepted" for v in rejections.values()),
        "rejections": rejections,
    }

def missing_artifact_control() -> Dict[str, Any]:
    required_absent = [
        "exact_suno_source_or_sdk_pin",
        "exact_model_or_service_runtime_pin",
        "rights_clearance_bundle",
        "frozen_comparison_corpus",
        "exact_output_bundle",
        "independent_score_or_listening_bundle",
        "target_runtime_timing_bundle",
        "opt_in_provider_intake",
    ]
    return {
        "all_absent": True,
        "missing": required_absent,
        "no_missing_result_qualifies": True,
    }

def scope_control() -> Dict[str, Any]:
    return {
        "no_network": True,
        "no_download": True,
        "no_runtime_execution": True,
        "no_weights": True,
        "no_real_audio": True,
        "no_provider_registration": True,
        "task_local_only": True,
    }

# ---------------------------------------------------------------------------
# Contract/report
# ---------------------------------------------------------------------------

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "exact_source_or_runtime_absent",
        "requirement": (
            "Provide exact, licensed, pinned Suno/source/runtime/API artifact "
            "identity (version, commit/hash, endpoint or package, terms) "
            "admissible for SDK evidence reproduction."),
        "state": (
            "No Suno source checkout, SDK package, model weight, API contract "
            "pin, or runtime artifact is present in this workspace. The task "
            "evidence cites a market-benchmark research note only."),
    },
    {
        "id": "rights_and_terms_unresolved",
        "requirement": (
            "Supply written rights/terms for source, model/service outputs, "
            "comparison corpora, redistribution, product use, and derivative "
            "evaluation artifacts."),
        "state": (
            "No rights-clearance or terms bundle is present. No Suno asset or "
            "output is copied, vendored, or used."),
    },
    {
        "id": "comparison_corpus_and_outputs_absent",
        "requirement": (
            "Provide a frozen, rights-cleared comparison corpus and exact "
            "pinned outputs for every compared system/configuration."),
        "state": (
            "No frozen comparison corpus, prompts, inputs, outputs, hashes, or "
            "reproducible run manifest is present."),
    },
    {
        "id": "independent_scoring_absent",
        "requirement": (
            "Provide independent task-matched scoring or authorized listening "
            "with controls, failure cases, and provenance."),
        "state": (
            "No independent score, listening result, or control run is "
            "present. This package makes no quality claim."),
    },
    {
        "id": "target_timing_absent",
        "requirement": (
            "Provide target-device/runtime timing, memory, deadline behavior, "
            "and availability evidence for the exact admitted configuration."),
        "state": (
            "No device timing, RTF, memory, or deadline evidence is present."),
    },
    {
        "id": "provider_intake_absent",
        "requirement": (
            "Complete OFF-by-default opt-in provider intake only after exact "
            "artifacts, rights, and evidence gates pass; no default/registry/"
            "ABI/shared-build/CI change in this task."),
        "state": (
            "No provider, descriptor, registry, default, shared build, CI, or "
            "installed-v0 change was made."),
    },
)

GATE_REQUIREMENTS: Tuple[Tuple[str, str], ...] = (
    ("exact_source_or_service_identity",
     "Exact Suno source/service/package/API identity is pinned with hashes/versions and admitted terms."),
    ("rights_and_redistribution_clearance",
     "Source, output, corpus, redistribution, product-use, and derivative-evidence rights are cleared."),
    ("frozen_comparison_corpus",
     "Rights-cleared frozen prompts/inputs/corpus and comparison protocol are pinned."),
    ("exact_output_bundle",
     "Exact pinned outputs/manifests for compared systems are present and hash-verified."),
    ("independent_scoring_or_listening",
     "Independent task-matched scoring or authorized listening with controls is present."),
    ("target_runtime_timing",
     "Target-device/runtime timing, memory, and deadline behavior are measured for admitted config."),
    ("failure_and_nonqualification_controls",
     "Missing/invalid/nonfinite/adverse cases fail closed; no missing result qualifies."),
    ("opt_in_provider_intake",
     "OFF-by-default opt-in provider intake reviewed without installed-v0/default/ABI/shared-build/CI changes."),
)

BOUNDARY: Dict[str, Any] = {
    "adapter_json_added": False,
    "asset_bundled": False,
    "ci_change": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "descriptor_settings": {},
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "onnxruntime_invoked": False,
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
    "benchmark_run": False,
    "device_timing_measured": False,
    "downloaded": False,
    "implementation_added": False,
    "listening_performed": False,
    "network_used": False,
    "provider_registered": False,
    "public_abi_changed": False,
    "real_assets_used": False,
    "registry_or_default_changed": False,
    "release_claim": False,
    "runtime_executed": False,
    "shared_build_or_ci_changed": False,
    "source_imported": False,
    "task_local_only": True,
    "weights_loaded": False,
    "write_scope": TASK_PREFIX + " only",
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No Suno source, model, weight, API runtime, or output bundle was downloaded, copied, vendored, imported, loaded, or executed.",
    "No quality, listening, timing, benchmark, default, or release claim is made.",
    "The market-benchmark research note is context only and does not qualify an SDK processor or adapter.",
    "No provider, descriptor, registry, installed v0 path, default, public ABI, shared build, dependency lock, or CI was changed.",
    "Missing or blocked artifacts do not qualify this candidate.",
)

SOURCE_PINS: Dict[str, str] = {
    INVENTORY_PATH:
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    VERIFICATION_PATH:
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    MARKET_BENCHMARK_PATH:
        "d1a4edbf72257ebb989d9639e542cf2c50152e323dc9081f2af868708064a3e7",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LOCAL_FILES: Tuple[str, ...] = (
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
EXPECTED_DIR_FILES = set(LOCAL_FILES) | {"SOURCES.sha256"}
ARTIFACT_TABLE_EXCLUDED = frozenset({"README.md", "SOURCES.sha256"})
README_SECTIONS = ("source", "boundary", "artifacts")
README_MARKERS = {
    "source": ("<!-- digest-table: source -->", "<!-- digest-table: end -->"),
    "boundary": ("<!-- digest-table: boundary -->", "<!-- digest-table: end -->"),
    "artifacts": ("<!-- DIGEST_TABLE_ARTIFACTS_START -->",
                  "<!-- DIGEST_TABLE_ARTIFACTS_END -->"),
}

REQUIRED_REPORT_KEYS = {
    "acceptance_profile", "base_commit", "board_row", "boundary", "branch",
    "caller_asset_contract", "claim", "component_id", "contract_sha256",
    "controls", "decision", "defer_before", "evidence_status",
    "exact_blockers", "format", "gates", "missing_results",
    "negative_claims", "no_missing_result_qualifies_candidate", "profile",
    "proposal_only", "qualification", "qualification_status",
    "reopen_condition", "scenario", "schema_id", "scope", "status",
    "surrogate", "task_id", "title", "upstream",
}
REQUIRED_CONTRACT_KEYS = {
    "acceptance_profile", "base_commit", "board_row", "boundary",
    "boundary_pins", "branch", "caller_asset_contract", "component_id",
    "decision", "defer_before", "evidence_status", "exact_blockers", "format",
    "gates", "invariants", "local_files", "negative_claims", "profile",
    "proposal_only", "qualification", "qualification_status",
    "reopen_condition", "reviewer", "scenario", "schema_id", "scope",
    "source_pins", "status", "task_id", "title", "upstream",
}

def _acceptance_profile() -> Dict[str, Any]:
    return {
        "blocked_cases": [
            "no exact Suno source/service/runtime identity with admissible terms",
            "no frozen rights-cleared comparison corpus and exact output bundle",
            "no independent scoring or authorized listening with controls",
            "no target-device/runtime timing, memory, or deadline evidence",
            "no OFF-by-default opt-in provider intake decision",
        ],
        "mapped_cases": [
            "exact task/component identity and stable board-row digest gate",
            "deterministic comparison-record metadata validation surrogate",
            "fail-closed rejection of missing/invalid/nonfinite comparison metadata",
            "explicit blocked release gates and not_qualified disposition",
            "task-local-only scope with no provider/ABI/build/CI/runtime changes",
        ],
        "name": PROFILE,
        "not_applicable": [
            "no Suno model, weights, API, runtime, or generated outputs are present",
            "no real audio corpus, listening session, or target-device timing is present",
            "no processor/adapter implementation is admitted in this package",
        ],
        "source": VERIFICATION_PATH,
    }

def _qualification_block() -> Dict[str, Any]:
    return {
        "all_release_gates_blocked": True,
        "exact_result_present": False,
        "missing_result_promoted": False,
        "not_qualified": True,
        "provider_intake_present": False,
        "quality_result_present": False,
        "readiness": "incomplete",
        "release_claim": False,
        "rights_clearance_present": False,
        "runtime_present": False,
        "source_present": False,
        "status": QUALIFICATION,
        "timing_result_present": False,
    }

def _surrogate_block() -> Dict[str, Any]:
    return {
        "candidate_result": False,
        "is_suno": False,
        "model_free": True,
        "network_free": True,
        "note": (
            "The deterministic comparison-record validator exercises only "
            "metadata fail-closed behavior. It is not Suno, not audio "
            "processing, and cannot qualify the candidate."),
        "type": "deterministic_comparison_metadata_surrogate",
    }

CALLER_ASSET_CONTRACT: Dict[str, Any] = {
    "absent_behavior": "reject_before_processing",
    "asset_is_caller_owned": True,
    "asset_is_vendored": False,
    "contract_id": f"audio-sdk/{SLUG}/caller-supplied-comparison-artifact/0.1",
    "present_behavior": (
        "validate_identity_terms_and_hashes_only; do_not_load_execute_or_"
        "redistribute_in_this_package"),
    "required_fields": [
        "comparison_corpus_sha256",
        "comparison_protocol_sha256",
        "output_bundle_sha256",
        "rights_bundle_sha256",
        "runtime_or_service_pin",
        "source_or_service_pin",
    ],
    "separate_rights_bundle_required": True,
    "verification": [
        "manifest is strict JSON with exactly the required fields",
        "all paths or identifiers are caller-owned and rights-reviewed before admission",
        "SHA-256 values match the exact admitted artifact bytes",
        "no download, copy, build, import, load, execution, or redistribution occurs here",
        "missing or unreviewed rights/runtime/output artifacts remain blocked and not_qualified",
    ],
}

FORMAT: Dict[str, Any] = {
    "comparison_type": "product_market_context_only",
    "installed_v0_geometry_preserved": True,
    "sdk_v0_channels": 1,
    "sdk_v0_frame_samples": 160,
    "sdk_v0_sample_format": "f32",
    "sdk_v0_sample_rate_hz": 16000,
    "task_local_evidence_only": True,
}

def _report_body() -> Dict[str, Any]:
    return {
        "acceptance_profile": _acceptance_profile(),
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "claim": {
            "base_commit": BASE_COMMIT,
            "branch": BRANCH,
            "reviewer": REVIEWER,
            "worktree": CLAIM_WORKTREE,
        },
        "component_id": COMPONENT,
        "contract_sha256": sha256(contract_bytes()),
        "controls": {
            "comparison_digest": comparison_control(),
            "missing_artifacts": missing_artifact_control(),
            "nonfinite": nonfinite_control(),
            "record_adverse": record_adverse_control(),
            "scope": scope_control(),
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "format": dict(FORMAT),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": req, "status": "blocked"}
            for gate, req in GATE_REQUIREMENTS
        ],
        "missing_results": [
            "exact Suno source/service/runtime identity and admissible terms",
            "rights-clearance bundle for source, outputs, corpus, and redistribution",
            "frozen rights-cleared comparison corpus and protocol",
            "exact pinned output bundle and manifests",
            "independent scoring or authorized listening with controls",
            "target-device/runtime timing, memory, and deadline evidence",
            "OFF-by-default opt-in provider intake decision",
        ],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "no_missing_result_qualifies_candidate": True,
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply exact Suno source/service/runtime identity and admissible "
            "rights/terms, a frozen rights-cleared comparison corpus/protocol, "
            "exact pinned output bundles, independent scoring or authorized "
            "listening with controls, target-device/runtime timing evidence, "
            "and an OFF-by-default opt-in provider intake decision. Until then "
            "the candidate stays DEFER, incomplete, and not_qualified."),
        "scenario": {
            "comparison_kind": "external_product_market_context",
            "id": "suno-product-comparison-external-blocker-v1",
            "is_audio_processing_runtime": False,
            "is_music_generation_product": True,
        },
        "schema_id": SCHEMA_ID,
        "scope": dict(SCOPE),
        "status": STATUS,
        "surrogate": _surrogate_block(),
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "admitted_runtime": False,
            "admitted_source": False,
            "evidence_kind": "source_only_research_note",
            "note": (
                "The referenced market benchmark is source-only context. No "
                "Suno source/runtime/output bundle is admitted by this package."),
            "reference_path": MARKET_BENCHMARK_PATH,
            "source_present": resolve_source_path(MARKET_BENCHMARK_PATH).exists(),
        },
    }

def _plain(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value

def build_report() -> Dict[str, Any]:
    report = _plain(_report_body())
    if has_negative_zero(report):
        raise ValueError("negative_zero_in_report")
    return report

def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    if report is None:
        report = build_report()
    return canonical_bytes(report)

def contract_payload() -> Dict[str, Any]:
    return {
        "acceptance_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "board_row": {
            "full_tasks_json_hashed": False,
            "note": (
                "Only the stable linked-row identity is gated. The mutable "
                "full plan/swarm/TASKS.json is never read into, hashed by, or "
                "pinned to this package."),
            "stable_fields": BOARD_ROW_STABLE_FIELDS,
            "stable_sha256": BOARD_ROW_STABLE_SHA256,
        },
        "boundary": dict(BOUNDARY),
        "boundary_pins": dict(BOUNDARY_PINS),
        "branch": BRANCH,
        "caller_asset_contract": CALLER_ASSET_CONTRACT,
        "component_id": COMPONENT,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "exact_blockers": [dict(b) for b in EXACT_BLOCKERS],
        "format": dict(FORMAT),
        "gates": [
            {"id": gate, "qualifies": False, "requirement": req, "status": "blocked"}
            for gate, req in GATE_REQUIREMENTS
        ],
        "invariants": [
            "decision is DEFER and qualification is not_qualified",
            "the package is proposal-only and incomplete",
            "no missing, blocked, or rejected result is promoted to a pass",
            "no Suno source/runtime/output/corpus is downloaded, copied, imported, loaded, or executed",
            "no claim is made from source-only context alone",
            "installed v0 remains 16 kHz mono float32 at 160 samples per frame",
            "only this task-local evidence directory is written",
            "the mutable full task board is never hashed",
        ],
        "local_files": sorted(LOCAL_FILES),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "profile": PROFILE,
        "proposal_only": True,
        "qualification": _qualification_block(),
        "qualification_status": QUALIFICATION,
        "reopen_condition": (
            "Supply exact Suno source/service/runtime identity and admissible "
            "rights/terms, a frozen rights-cleared comparison corpus/protocol, "
            "exact pinned output bundles, independent scoring or authorized "
            "listening with controls, target-device/runtime timing evidence, "
            "and an OFF-by-default opt-in provider intake decision."),
        "reviewer": REVIEWER,
        "scenario": {
            "comparison_kind": "external_product_market_context",
            "id": "suno-product-comparison-external-blocker-v1",
            "is_audio_processing_runtime": False,
            "is_music_generation_product": True,
        },
        "schema_id": CONTRACT_SCHEMA_ID,
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "status": STATUS,
        "task_id": TASK,
        "title": TITLE,
        "upstream": {
            "admitted_runtime": False,
            "admitted_source": False,
            "evidence_kind": "source_only_research_note",
            "reference_path": MARKET_BENCHMARK_PATH,
            "source_present": resolve_source_path(MARKET_BENCHMARK_PATH).exists(),
        },
    }

def contract_bytes() -> bytes:
    return canonical_bytes(contract_payload())

# ---------------------------------------------------------------------------
# SOURCES.sha256 and README digest tables
# ---------------------------------------------------------------------------

def _local_manifest_paths() -> List[str]:
    return sorted(p.name for p in HERE.iterdir()
                  if p.is_file() and p.name != "SOURCES.sha256")

def sources_bytes() -> bytes:
    rows: List[Tuple[str, str]] = []
    for name, digest in SOURCE_PINS.items():
        rows.append((digest, "source:" + name))
    for name, digest in BOUNDARY_PINS.items():
        rows.append((digest, "sdk:" + name))
    for name in _local_manifest_paths():
        rows.append((sha256_file(HERE / name), TASK_PREFIX + name))
    rows.sort(key=lambda item: item[1])
    lines = [
        f"# SHA-256 pins for {TASK} task-local evidence.",
        "# source: paths are relative to the pinned research workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        f"# Full mutable plan/swarm/TASKS.json is never hashed; only "
        f"board_row.stable_sha256={BOARD_ROW_STABLE_SHA256} is gated.",
    ]
    for digest, path in rows:
        lines.append(f"{digest}  {path}")
    return ("\n".join(lines) + "\n").encode("ascii")

def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{64}  \S+", line) is None:
            raise ValueError(f"malformed_pin_line:{number}")
        digest, path = line.split("  ", 1)
        if not (path.startswith("source:") or path.startswith("sdk:") or
                path.startswith(TASK_PREFIX)):
            raise ValueError(f"unknown_pin_prefix:{number}")
        if path in seen:
            raise ValueError(f"duplicate_pin:{number}")
        seen.add(path)
        rows.append((digest, path))
    if not rows:
        raise ValueError("empty_pin_manifest")
    return rows

def allowed_pin_keys() -> set[str]:
    return ({"source:" + name for name in SOURCE_PINS} |
            {"sdk:" + name for name in BOUNDARY_PINS} |
            {TASK_PREFIX + name for name in _local_manifest_paths()})

def expected_readme_keys() -> Dict[str, set[str]]:
    return {
        "source": {"source:" + name for name in SOURCE_PINS},
        "boundary": {"sdk:" + name for name in BOUNDARY_PINS},
        "artifacts": {
            name for name in _local_manifest_paths()
            if name not in ARTIFACT_TABLE_EXCLUDED
        },
    }

def _section_text(text: str, section: str) -> str:
    start, end = README_MARKERS[section]
    if text.count(start) != 1:
        raise ValueError("readme_marker_count:" + section)
    si = text.index(start) + len(start)
    ei = text.find(end, si)
    if ei < 0:
        raise ValueError("readme_marker_missing:" + section)
    return text[si:ei]

def parse_readme_tables(text: str) -> Dict[str, List[Tuple[str, str, int | None]]]:
    tables: Dict[str, List[Tuple[str, str, int | None]]] = {}
    for section in README_SECTIONS:
        body = _section_text(text, section)
        rows: List[Tuple[str, str, int | None]] = []
        for line in body.splitlines():
            if not line.startswith("| `"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) not in (2, 3):
                raise ValueError(f"readme_row_shape:{section}")
            key = cells[0].strip("`")
            digest = cells[1].strip("`")
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError(f"readme_bad_digest:{section}:{key}")
            size = None
            if len(cells) == 3:
                if not re.fullmatch(r"\d+", cells[2]):
                    raise ValueError(f"readme_bad_size:{section}:{key}")
                size = int(cells[2])
            rows.append((key, digest, size))
        tables[section] = rows
    return tables

def render_readme_table(rows: List[Tuple[str, str, int | None]],
                        with_size: bool) -> str:
    if with_size:
        lines = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
    else:
        lines = ["| Key | SHA-256 |", "| --- | --- |"]
    for key, digest, size in rows:
        if with_size:
            lines.append(f"| `{key}` | `{digest}` | {size} |")
        else:
            lines.append(f"| `{key}` | `{digest}` |")
    return "\n".join(lines)

def update_readme_artifact_table(text: str) -> str:
    start, end = README_MARKERS["artifacts"]
    si = text.index(start) + len(start)
    ei = text.index(end, si)
    rows = []
    for name in _local_manifest_paths():
        if name in ARTIFACT_TABLE_EXCLUDED:
            continue
        p = HERE / name
        rows.append((name, sha256_file(p), p.stat().st_size))
    rows.sort(key=lambda r: r[0])
    table = "\n\n" + render_readme_table(rows, with_size=True) + "\n"
    return text[:si] + table + text[ei:]
