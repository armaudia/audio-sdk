# SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local blocker/reference evidence for SDK-RESEMBLE-ENHANCE-DENOISE-ONLY.

This package is proposal-only, incomplete and not qualified. It does not
download, load, execute, vendor or redistribute Resemble Enhance source,
weights, runtime, or audio. It records an exact blocker/readiness boundary when
the required licensed source/weights/runtime are absent.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))

TASK = "SDK-RESEMBLE-ENHANCE-DENOISE-ONLY"
TITLE = "Resemble Enhance denoise-only"
SLUG = "resemble-enhance-denoise-only"
COMPONENT = "resemble-enhance-denoise-only"
BASE_COMMIT = "a9cf338c0b363d69408c931071071583a49ebdc1"
BRANCH = f"swarm/{TASK}"
PROFILE = "enhancement"
STATUS = "proposal_only_incomplete"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_provider_or_reference_exposure"
REPORT_SCHEMA = "audio-sdk/task-evidence/resemble-enhance-denoise-only/report/0.1"
CONTRACT_SCHEMA = "audio-sdk/task-evidence-contract/0.1"

PUBLIC_SAMPLE_RATE_HZ = 16000
PUBLIC_CHANNELS = 1
PUBLIC_SAMPLE_FORMAT = "f32"
PUBLIC_FRAME_SAMPLES = 160

# Stable linked-row identity only; never hash mutable full TASKS.json.
LINKED_ROW_PROJECTION: Dict[str, Any] = {
    "id": TASK,
    "title": TITLE,
    "repository": "audio-sdk",
    "mode": "feasibility",
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "component": COMPONENT,
    "deliverable": (
        "Verify runnable source, exact assets, permitted scope, task geometry and matched evidence. "
        "Then reproduce the exact model/runtime as a caller-supplied-asset reference and add an opt-in "
        "SDK adapter once its prerequisites pass. Record a concrete blocker if feasibility fails."
    ),
    "acceptance": (
        "Apply the enhancement acceptance profile; record exact scope, evidence, failure/control results, "
        "and remaining release gates. A readiness conclusion with an exact external blocker is an accepted "
        "investigation handoff; it does not close the conditional implementation."
    ),
    "evidence": ["research/noise_suppression_candidate_census.md"],
}
LINKED_ROWS: List[Dict[str, Any]] = [
    LINKED_ROW_PROJECTION,
    {"id": "SDK-FND-AUDIT", "title": "Public provider intake and asset boundary", "repository": "audio-sdk", "mode": "foundation", "component": None},
    {"id": "SDK-FND-EVIDENCE", "title": "Task-matched conformance and reproducible benchmark evidence", "repository": "audio-sdk", "mode": "foundation", "component": None},
    {"id": "SDK-FND-PROVIDER", "title": "Provider integration boundaries and build fragments", "repository": "audio-sdk", "mode": "foundation", "component": None},
]

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md": "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/INVENTORY.json": "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md": "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "research/noise_suppression_candidate_census.md": "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
}

BOUNDARY_PINS: Dict[str, str] = {
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

LOCAL_PIN_PATHS = (
    "README.md",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)

EXACT_BLOCKERS: List[str] = [
    "Exact Resemble Enhance denoise-only source revision/archive and immutable license/provenance are not staged in this worktree; the census identifies an official repository with --denoise_only and MIT code, but no pinned commit, archive digest, or complete source snapshot is present here.",
    "Exact pretrained weights/assets, model-card or runtime terms, and redistribution/product-use clearance for the denoise-only path are absent; no weight, checkpoint, package, or runtime was downloaded, copied, built, or executed.",
    "No exact runnable runtime, reference-output parity vector, or task-matched enhancement evidence exists for this candidate in this worktree; no real audio, listening, device timing, benchmark, or release claim is produced.",
    "No rights-cleared real cohort, independent listening, target-runtime timing/memory/resource evidence, opt-in adapter/provider intake, or public/default decision exists; every release gate remains blocked."
]

GATE_DEFINITIONS: Tuple[Tuple[str, str], ...] = (
    ("source_revision_archive_and_license_provenance", "Supply immutable source revision/archive/tree digests and complete license/notice provenance for the exact denoise-only path."),
    ("weights_assets_and_terms", "Supply exact weights/assets with per-file byte counts and SHA-256 and reviewed model/runtime/redistribution/product-use terms."),
    ("exact_runtime_reproduction", "Reproduce the exact pinned runtime offline with deterministic settings and an approved reference-output parity vector."),
    ("native_or_caller_boundary", "Verify the exact caller/native boundary, sample-rate/channel/frame contract, delay/flush behavior, and fail-closed invalid-input handling."),
    ("real_cohort_enhancement_evidence", "Score a rights-cleared held-out real cohort under the Enhancement profile with paired metrics or separately labeled evidence."),
    ("independent_listening_and_preservation", "Collect independent listening/preservation review; synthetic or missing evidence cannot qualify."),
    ("target_runtime_timing_memory_resources", "Measure content/availability timing, memory, CPU, and deadline behavior on the exact target runtime."),
    ("opt_in_intake_and_public_surface", "Complete opt-in intake, descriptor/registry/release review, and explicit public/default decision; keep candidate unregistered and OFF until then."),
)

MISSING_EVIDENCE: List[str] = [
    "immutable Resemble Enhance denoise-only source revision/archive with complete license/notice provenance",
    "exact pretrained weights/assets with byte counts, SHA-256, and reviewed terms",
    "pinned offline runtime/environment with deterministic settings and reference parity vector",
    "verified caller/native boundary, delay/flush, and invalid-input behavior for exact geometry",
    "rights-cleared real enhancement cohort with task-matched baseline and preservation controls",
    "independent listening or human/preference review",
    "target-runtime timing, memory, CPU, and deadline measurements",
    "opt-in adapter/provider intake, descriptor/registry review, and explicit public/default decision",
]

REOPENING_CONDITIONS: List[str] = [
    "Provide the exact immutable source revision/archive and complete license/notice provenance for the denoise-only path.",
    "Provide exact weights/assets and reviewed redistribution/product-use/runtime terms; do not treat code license as weight clearance.",
    "Reproduce the exact runtime offline with deterministic settings and an approved reference-output parity vector.",
    "Verify the exact caller/native boundary, delay/flush, invalid-input, and state behavior under the Enhancement profile.",
    "Run rights-cleared real-cohort enhancement evaluation with preservation controls and independent listening.",
    "Measure target-runtime timing, memory, CPU, and deadlines on the intended deployment profile.",
    "Complete opt-in intake and explicit public/default decision before any registration, default, or release claim.",
    "Keep all release gates blocked until every required artifact and result is present and reviewed.",
]

BOUNDARY: Dict[str, Any] = {
    "task_local_only": True,
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "installed_v0_behavior_change": False,
    "ci_change": False,
    "benchmark_claim": False,
    "release_claim": False,
}

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "source_present": False,
    "weights_present": False,
    "runtime_present": False,
    "exact_runtime_reproduced": False,
    "real_audio": False,
    "real_labels": False,
    "network_used": False,
    "download_attempted": False,
    "model_executed": False,
    "weights_loaded": False,
    "device_timing": False,
    "listening_result": False,
    "benchmark_claim": False,
    "release_claim": False,
    "provider_registered": False,
    "public_default_changed": False,
}

NEGATIVE_CLAIMS: Dict[str, bool] = {
    "source_weights_runtime_present": False,
    "exact_runtime_reproduced": False,
    "model_loaded_or_executed": False,
    "weights_downloaded_or_redistributed": False,
    "real_audio_used": False,
    "listening_performed": False,
    "device_timing_measured": False,
    "benchmark_result_claimed": False,
    "release_claimed": False,
    "provider_registered": False,
    "public_default_changed": False,
    "installed_v0_changed": False,
    "abi_changed": False,
    "shared_build_changed": False,
    "ci_changed": False,
}

FORMAT: Dict[str, Any] = {
    "public_sample_rate_hz": PUBLIC_SAMPLE_RATE_HZ,
    "public_channels": PUBLIC_CHANNELS,
    "public_sample_format": PUBLIC_SAMPLE_FORMAT,
    "public_frame_samples": PUBLIC_FRAME_SAMPLES,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def has_negative_zero(value: Any) -> bool:
    if isinstance(value, float):
        return value == 0.0 and math.copysign(1.0, value) < 0.0
    if isinstance(value, dict):
        return any(has_negative_zero(v) for v in value.values())
    if isinstance(value, list):
        return any(has_negative_zero(v) for v in value)
    return False


def strict_loads(text: str) -> Any:
    def object_pairs_hook(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
        obj: Dict[str, Any] = {}
        for k, v in pairs:
            if k in obj:
                raise ValueError(f"duplicate_key:{k}")
            obj[k] = v
        return obj

    def parse_constant(s: str) -> Any:
        raise ValueError(f"nonfinite:{s}")

    payload = json.loads(text, object_pairs_hook=object_pairs_hook, parse_constant=parse_constant)
    if not isinstance(payload, dict):
        raise ValueError("root_not_object")
    return payload


def stable_linked_row_projection_sha256() -> str:
    return sha256_bytes(canonical_bytes(LINKED_ROW_PROJECTION))


def stable_linked_rows_sha256() -> str:
    return sha256_bytes(canonical_bytes(LINKED_ROWS))


def _gate_objects() -> List[Dict[str, Any]]:
    return [
        {
            "id": f"RG-{idx:02d}",
            "name": name,
            "status": "blocked",
            "qualifies": False,
            "reopen_condition": reopen,
        }
        for idx, (name, reopen) in enumerate(GATE_DEFINITIONS, start=1)
    ]


def _absence_probe(name: str, present: bool = False, detail: str = "absent") -> Dict[str, Any]:
    return {"probe": name, "present": present, "detail": detail}


def absence_probes() -> List[Dict[str, Any]]:
    return [
        _absence_probe("data/checkouts/resemble-enhance"),
        _absence_probe("data/checkouts/resemble_enhance"),
        _absence_probe("data/envs/resemble-enhance"),
        _absence_probe("third_party/resemble-enhance"),
        _absence_probe("third_party/resemble_enhance"),
        _absence_probe("docs/task-evidence/resemble-enhance-denoise-only/weights"),
        _absence_probe("docs/task-evidence/resemble-enhance-denoise-only/assets"),
        _absence_probe("docs/task-evidence/resemble-enhance-denoise-only/runtime"),
    ]


def adverse_cases() -> Dict[str, Any]:
    manifest_fields = ["source_revision", "archive_sha256", "weights_sha256", "runtime_lock_sha256"]
    valid = {
        "source_revision": "0" * 40,
        "archive_sha256": "1" * 64,
        "weights_sha256": "2" * 64,
        "runtime_lock_sha256": "3" * 64,
    }

    def validate_manifest(m: Any) -> Dict[str, Any]:
        if not isinstance(m, dict):
            return {"status": "rejected", "reason": "manifest_not_object"}
        if set(m.keys()) != set(manifest_fields):
            return {"status": "rejected", "reason": "manifest_fields_mismatch"}
        for k in manifest_fields:
            v = m[k]
            if not isinstance(v, str):
                return {"status": "rejected", "reason": f"invalid_type:{k}"}
            if k == "source_revision" and (len(v) != 40 or any(c not in "0123456789abcdef" for c in v)):
                return {"status": "rejected", "reason": "invalid_source_revision"}
            if k != "source_revision" and (len(v) != 64 or any(c not in "0123456789abcdef" for c in v)):
                return {"status": "rejected", "reason": f"invalid_sha256:{k}"}
        # No assets present in this package; schema-valid manifest still cannot qualify.
        return {"status": "rejected", "reason": "required_assets_absent"}

    cases = {
        "missing_manifest": validate_manifest(None),
        "unknown_field": validate_manifest({**valid, "extra": "x"}),
        "invalid_source_revision": validate_manifest({**valid, "source_revision": "BAD"}),
        "invalid_sha256": validate_manifest({**valid, "weights_sha256": "zzz"}),
        "non_string_field": validate_manifest({**valid, "archive_sha256": 123}),
        "schema_valid_but_assets_absent": validate_manifest(valid),
    }
    all_rejected = all(c["status"] == "rejected" for c in cases.values())
    return {
        "all_rejected": all_rejected,
        "any_qualifying": False,
        "cases": cases,
    }


def build_report() -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "schema_id": REPORT_SCHEMA,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification": {
            "status": QUALIFICATION_STATUS,
            "qualified": False,
            "reason": "exact licensed source/weights/runtime absent; blocker package only",
        },
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "negative_claims": NEGATIVE_CLAIMS,
        "format": FORMAT,
        "linked_row_identity": {
            "policy": "stable_linked_row_identity_only; never hash mutable full plan/swarm/TASKS.json",
            "projection": LINKED_ROW_PROJECTION,
            "linked_rows": LINKED_ROWS,
            "projection_sha256": stable_linked_row_projection_sha256(),
            "linked_rows_sha256": stable_linked_rows_sha256(),
        },
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "absence_probes": absence_probes(),
        "exact_blockers": EXACT_BLOCKERS,
        "missing_evidence": MISSING_EVIDENCE,
        "reopening_conditions": REOPENING_CONDITIONS,
        "gates": _gate_objects(),
        "adverse_cases": adverse_cases(),
        "enhancement_profile_application": {
            "profile": "enhancement",
            "identity_noisy_control": "blocked - no exact runtime/assets",
            "established_task_matched_baseline": "blocked",
            "paired_si_sdr_stoi": "blocked - no rights-cleared real cohort or exact runtime",
            "clean_speech_preservation_peaks_invalid": "blocked",
            "unpaired_predictive_or_listening": "blocked",
            "alignment_state_memory_content_availability_timing": "blocked",
            "result_qualifies": False,
        },
    }
    report["repeatability"] = repeatability(report)
    return report


def build_contract() -> Dict[str, Any]:
    report = build_report()
    return {
        "schema_id": CONTRACT_SCHEMA,
        "task": TASK,
        "title": TITLE,
        "component": COMPONENT,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "no_missing_result_qualifies_candidate": True,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "format": FORMAT,
        "linked_row_identity": report["linked_row_identity"],
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "absence_probes": absence_probes(),
        "exact_blockers": EXACT_BLOCKERS,
        "missing_evidence": MISSING_EVIDENCE,
        "reopening_conditions": REOPENING_CONDITIONS,
        "gates": _gate_objects(),
        "adverse_cases": adverse_cases(),
    }


def report_without_repeatability(report: Dict[str, Any]) -> Dict[str, Any]:
    body = dict(report)
    body.pop("repeatability", None)
    return body


def repeatability(report: Dict[str, Any]) -> Dict[str, Any]:
    body = report_without_repeatability(report)
    digests = [sha256_bytes(canonical_bytes(body)) for _ in range(3)]
    return {
        "count": 3,
        "byte_identical": len(set(digests)) == 1,
        "digests": digests,
        "scope": "report body excluding repeatability",
    }


def canonical_report_bytes(report: Dict[str, Any] | None = None) -> bytes:
    rep = build_report() if report is None else report
    # ensure repeatability is consistent with body
    body = report_without_repeatability(rep)
    rep2 = dict(body)
    rep2["repeatability"] = repeatability(rep2)
    return canonical_bytes(rep2)


def contract_bytes() -> bytes:
    return canonical_bytes(build_contract())


def sources_bytes() -> bytes:
    entries: List[Tuple[str, str]] = []
    for rel, digest in sorted(SOURCE_PINS.items()):
        entries.append((digest, f"source:{rel}"))
    for rel, digest in sorted(BOUNDARY_PINS.items()):
        entries.append((digest, f"sdk:{rel}"))
    for rel in sorted(LOCAL_PIN_PATHS):
        p = HERE / rel
        if p.exists():
            entries.append((sha256_file(p), f"task:{rel}"))
    entries.sort(key=lambda x: x[1])
    return ("".join(f"{d}  {n}\n" for d, n in entries)).encode("utf-8")


def allowed_pin_keys() -> set[str]:
    keys = {f"source:{k}" for k in SOURCE_PINS}
    keys |= {f"sdk:{k}" for k in BOUNDARY_PINS}
    keys |= {f"task:{k}" for k in LOCAL_PIN_PATHS}
    return keys


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    if not text.endswith("\n"):
        raise ValueError("pin_missing_final_newline")
    lines = text.splitlines()
    pins: List[Tuple[str, str]] = []
    seen = set()
    for line in lines:
        if not line or "  " not in line:
            raise ValueError("pin_bad_line")
        digest, name = line.split("  ", 1)
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("pin_bad_digest")
        if name in seen:
            raise ValueError("pin_duplicate")
        seen.add(name)
        pins.append((digest, name))
    names = [n for _, n in pins]
    if names != sorted(names):
        raise ValueError("pin_unsorted")
    return pins


def strict_rejection_examples() -> Dict[str, int]:
    bad_json = [
        '{"a":1,"a":2}',
        '[1,2,3]',
        '{"x":NaN}',
        '{"x":Infinity}',
        '{"x":-Infinity}',
    ]
    bad_json_rejected = 0
    for s in bad_json:
        try:
            strict_loads(s)
        except Exception:
            bad_json_rejected += 1
    bad_pins = [
        "abc  file\n",
        "0" * 64 + " file\n",
        ("0" * 64 + "  b\n" + "1" * 64 + "  a\n"),
        ("0" * 64 + "  a\n" + "0" * 64 + "  a\n"),
    ]
    bad_pins_rejected = 0
    for s in bad_pins:
        try:
            parse_pin_lines(s)
        except Exception:
            bad_pins_rejected += 1
    return {
        "bad_json_rejected": bad_json_rejected,
        "bad_json_total": len(bad_json),
        "bad_pins_rejected": bad_pins_rejected,
        "bad_pins_total": len(bad_pins),
    }


def upstream_git_identity() -> Dict[str, Any]:
    # No upstream checkout is required/present for this blocker package.
    return {
        "present": False,
        "reason": "exact upstream source/weights/runtime absent in worktree; blocker package only",
    }
