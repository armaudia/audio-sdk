# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, read-only category evidence map for SDK-SURVEY-TRN-01.

This module maps the original TRN-01 method families, named source leads and
historical executions to pinned inventory, board and task-local evidence. It is
stdlib-only. It does not load a corpus, model, runtime, device or audio file; it
does not listen, benchmark, register a provider or claim a release. Every
adverse case below is produced by actually invoking a validator against a
read-only snapshot, never by writing a canned result.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
TASK = "SDK-SURVEY-TRN-01"
CATEGORY_ID = "TRN-01"
SLUG = "survey-trn-01"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "c9296ae96a2b58efae559bd22e7760122c886df8"
BRANCH = "swarm/SDK-SURVEY-TRN-01"
BOARD_SNAPSHOT = "board-snapshot.json"
BOARD_SNAPSHOT_SHA256 = "dcd077b07cf38071a0696eaf8d5312d8ea422aca4b9cbd67f0268fdf0baf3967"
BOARD_SNAPSHOT_SOURCE_SHA256 = (
    "a48298d0e43690ae2de563e9d73c9122266056fe2f5d1f4b2f6c64f2a5f3a351"
)
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio_categories.md":
        "97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905",
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/category_registry.json":
        "cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
}
EVIDENCE_PINS: Dict[str, str] = {
    "docs/task-evidence/bungee-basic/README.md":
        "ee6edcc68764888500aed41963169e6e311cec447b511fcbd1f2d4189453d485",
    "docs/task-evidence/granular-tsm/README.md":
        "d97f06911fd90667288fe571c7a3f4210ece629f7e839c1d41200ceec48ec0a0",
    "docs/task-evidence/ola-sola/README.md":
        "5d7de4612ad4d04cad544e4060aba607916f0fd013471388cc74fb55168bd731",
    "docs/task-evidence/phase-vocoder-baseline/README.md":
        "915bd51e7de4b223bdd61bb5ff823e7a0558f03e324f154d7d3d4c77d14f9790",
    "docs/task-evidence/psola-praat/README.md":
        "7e64ec614937533168ef31c34d4c8ec4aa7d6d52670e663f0f88ce5f4ec7a6ef",
    "docs/task-evidence/rubber-band-r3-offline/README.md":
        "de528246089b9f0d2a1ea597ac0cbbb119d5541b2b22a0a383b4d03b7a85aeab",
    "docs/task-evidence/rubber-band-r3-streaming/README.md":
        "04583e07678079f1ed179a1b15f50599693a7bc6f6a813237a71d0005d810d97",
    "docs/task-evidence/signalsmith-stretch/README.md":
        "446398e0c3aa27528e5ceacf1d4d0b6102f8c8e541c76aa6ac2a8abe62691934",
    "docs/task-evidence/soundtouch/README.md":
        "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
    "docs/task-evidence/sonic/README.md":
        "40f2fdcf708a75fbc3e0df296fabfecd296118e6a9eaee67fc34f8dec0e419cb",
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
LOCAL_PIN_PATHS = [
    "README.md",
    "board-snapshot.json",
    "board-snapshot.json.license",
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
]

SCOPE: Dict[str, bool] = {
    "category_evidence_map_only": True,
    "source_text_only": True,
    "board_text_only": True,
    "task_local_only": True,
    "real_corpus": False,
    "real_weights": False,
    "runtime_executed": False,
    "real_audio": False,
    "listening": False,
    "device_timing": False,
    "public_benchmark": False,
    "release_claim": False,
}
BOUNDARY: Dict[str, Any] = {
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "descriptor_registry_change": False,
    "shared_cmakelists_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "ci_change": False,
    "board_write": False,
    "shared_repo_write": False,
}
FORMAT: Dict[str, Any] = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}
TOOL_PROVENANCE = [
    "Only pinned text inventories, board records, registry entries and task-local README files are read.",
    "No network fetch, corpus, weights, runtime, device, listening or benchmark execution is performed.",
]
MISSING_EVIDENCE = [
    "Rights-cleared unfamiliar-speech and music cohort with exact labels.",
    "Independent blind listening for pitch and transient audibility.",
    "Pinned target playback pacing, variable sample-count and deadline evidence.",
    "Opt-in provider intake and licensing clearance.",
    "Explicit public default selection.",
    "Exact source/output interval parity with an approved external reference.",
]
GATE_NAMES = [
    "real_cohort",
    "independent_listening",
    "target_playback_pacing",
    "provider_intake",
    "public_default_selection",
    "exact_reference_parity",
]

# Curated, bounded map. Every component id below is checked against the pinned
# inventory and every follow-up id against the pinned board at report build time.
FAMILIES: List[Dict[str, Any]] = [
    {
        "id": "sola_wsola",
        "name": "SOLA / WSOLA",
        "original_text": "SOLA/WSOLA",
        "source_family": "classic",
        "components": [
            {"component_id": "soundtouch", "relation": "named_source_lead_S32",
             "note": "Source lead S32 names SoundTouch time and pitch scaling."},
            {"component_id": "ola-sola", "relation": "direct_family",
             "note": "Task-local OLA/SOLA synthetic reference exists."},
            {"component_id": "wsola-reference", "relation": "direct_family_open_gap",
             "note": "No task-local reference evidence; existing feasibility task is linked."},
        ],
        "gap_ids": ["gap-wsola-reference"],
    },
    {
        "id": "overlap_add",
        "name": "Overlap-add",
        "original_text": "overlap-add",
        "source_family": "classic",
        "components": [
            {"component_id": "ola-sola", "relation": "direct_family",
             "note": "Explicit OLA/SOLA inventory record and task-local evidence."},
            {"component_id": "sonic", "relation": "direct_family",
             "note": "Pitch-synchronous OLA synthetic reference, not an upstream Sonic runtime."},
            {"component_id": "granular-tsm", "relation": "adjacent_variant",
             "note": "Granular windowed OLA variant; not the original named family."},
            {"component_id": "psola-praat", "relation": "adjacent_variant",
             "note": "PSOLA is pitch-synchronous OLA; source report is offline-only."},
        ],
        "gap_ids": [],
    },
    {
        "id": "phase_vocoder",
        "name": "Phase vocoder",
        "original_text": "phase vocoder",
        "source_family": "classic",
        "components": [
            {"component_id": "phase-vocoder-baseline", "relation": "direct_family",
             "note": "Task-local synthetic phase-vocoder comparison exists."},
            {"component_id": "phase-locking-phase-vocoder", "relation": "direct_family_open_gap",
             "note": "Considered only; existing feasibility task is linked."},
            {"component_id": "transient-aware-phase-vocoder", "relation": "direct_family_open_gap",
             "note": "Considered only; existing feasibility task is linked."},
        ],
        "gap_ids": ["gap-phase-locking-phase-vocoder",
                    "gap-transient-aware-phase-vocoder"],
    },
    {
        "id": "disentangled_analysis_resynthesis",
        "name": "Disentangled analysis/resynthesis",
        "original_text": "Disentangled analysis/resynthesis families",
        "source_family": "ml",
        "components": [
            {"component_id": "neural-wsola", "relation": "ml_family_blocked",
             "note": "Blocked inventory state; feasibility task already on the board."},
            {"component_id": "rate-controlled-hifi-gan-speech-tsm", "relation": "ml_family_blocked",
             "note": "Blocked inventory state; weights and runtime not available here."},
            {"component_id": "tcn-speech-tsm", "relation": "ml_family_blocked",
             "note": "Blocked inventory state; no local runnable asset."},
            {"component_id": "stsm-film-neural-tsm", "relation": "ml_family_blocked",
             "note": "Blocked inventory state; no local runnable asset."},
            {"component_id": "neural-atsm", "relation": "ml_family_considered",
             "note": "Considered inventory state; no local runnable asset."},
            {"component_id": "phase-vocoder-with-neural-transient-preservation",
             "relation": "ml_family_blocked",
             "note": "Blocked inventory state; no local runnable asset."},
        ],
        "gap_ids": [
            "gap-neural-wsola",
            "gap-rate-controlled-hifi-gan-speech-tsm",
            "gap-tcn-speech-tsm",
            "gap-stsm-film-neural-tsm",
            "gap-neural-atsm",
            "gap-phase-vocoder-with-neural-transient-preservation",
        ],
    },
]

SOURCE_LEADS: List[Dict[str, Any]] = [
    {
        "source_id": "S32",
        "component_ids": ["soundtouch"],
        "match": "direct_named_lead",
        "historical_report_pin": "research/tsm-followup-20261101/README.md",
        "gap_ids": [],
    },
    {
        "source_id": "S33",
        "component_ids": ["rubber-band-r3-offline", "rubber-band-r3-streaming"],
        "match": "direct_named_lead",
        "historical_report_pin": "research/tsm-followup-20261101/README.md",
        "gap_ids": [],
    },
    {
        "source_id": "S51",
        "component_ids": ["rubber-band-r3-streaming", "d1-whole-clip-duration-planner",
                          "capsc-buffer-occupancy-pacing"],
        "match": "integration_and_variable_sample_count",
        "historical_report_pin": "REALTIME_COMPONENT_CANDIDATES.md",
        "gap_ids": ["gap-buffer-pacing"],
    },
]

GAPS: List[Dict[str, str]] = [
    {"id": "gap-wsola-reference", "family_id": "sola_wsola",
     "description": "WSOLA family has a considered inventory record but no task-local reference evidence.",
     "followup_task_id": "SDK-WSOLA-REFERENCE",
     "reopen_condition": "Compare Sonic, SoundTouch and a fixed-rate baseline under the Rate profile."},
    {"id": "gap-phase-locking-phase-vocoder", "family_id": "phase_vocoder",
     "description": "Phase-locking phase vocoder is considered only, with no task-local evidence.",
     "followup_task_id": "SDK-PHASE-LOCKING-PHASE-VOCODER",
     "reopen_condition": "Compare against the baseline phase vocoder at identical ratios."},
    {"id": "gap-transient-aware-phase-vocoder", "family_id": "phase_vocoder",
     "description": "Transient preservation for phase vocoder is considered only, with no task-local evidence.",
     "followup_task_id": "SDK-TRANSIENT-AWARE-PHASE-VOCODER",
     "reopen_condition": "Check consonant/transient preservation and ratio-switching artifact budgets."},
    {"id": "gap-neural-wsola", "family_id": "disentangled_analysis_resynthesis",
     "description": "Neural WSOLA is blocked locally with no runnable model, weights or runtime.",
     "followup_task_id": "SDK-NEURAL-WSOLA",
     "reopen_condition": "Verify exact runnable source and caller-supplied assets before an opt-in adapter."},
    {"id": "gap-rate-controlled-hifi-gan-speech-tsm",
     "family_id": "disentangled_analysis_resynthesis",
     "description": "Rate-controlled HiFi-GAN speech TSM is blocked locally with no runnable assets.",
     "followup_task_id": "SDK-RATE-CONTROLLED-HIFI-GAN-SPEECH-TSM",
     "reopen_condition": "Verify exact runnable source and caller-supplied assets before an opt-in adapter."},
    {"id": "gap-tcn-speech-tsm", "family_id": "disentangled_analysis_resynthesis",
     "description": "TCN speech TSM is blocked locally with no runnable assets.",
     "followup_task_id": "SDK-TCN-SPEECH-TSM",
     "reopen_condition": "Verify exact runnable source and caller-supplied assets before an opt-in adapter."},
    {"id": "gap-stsm-film-neural-tsm", "family_id": "disentangled_analysis_resynthesis",
     "description": "STSM-FiLM neural TSM is blocked locally with no runnable assets.",
     "followup_task_id": "SDK-STSM-FILM-NEURAL-TSM",
     "reopen_condition": "Verify exact runnable source and caller-supplied assets before an opt-in adapter."},
    {"id": "gap-neural-atsm", "family_id": "disentangled_analysis_resynthesis",
     "description": "Neural ATSM is considered only, with no runnable source or local evidence.",
     "followup_task_id": "SDK-NEURAL-ATSM",
     "reopen_condition": "Verify exact runnable source and caller-supplied assets before an opt-in adapter."},
    {"id": "gap-phase-vocoder-with-neural-transient-preservation",
     "family_id": "disentangled_analysis_resynthesis",
     "description": "Neural transient preservation is blocked locally with no runnable assets.",
     "followup_task_id": "SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION",
     "reopen_condition": "Verify exact runnable source and caller-supplied assets before an opt-in adapter."},
    {"id": "gap-buffer-pacing", "family_id": "source_lead_S51",
     "description": ("Variable sample-count pacing and slowing a continuous stream remains an open "
                     "handoff; source S51 describes integration and Rubber Band reported queue issues."),
     "followup_task_id": "SDK-CAPSC-BUFFER-OCCUPANCY-PACING",
     "reopen_condition": "Record queue debt, underruns and recovery under the Rate profile."},
]


class ValidationError(ValueError):
    """Raised by a read-only validator when an input is rejected."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _reject_duplicate(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValidationError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValidationError("nonfinite_json_constant:" + token)


def strict_json_text(text: str) -> Dict[str, Any]:
    payload = json.loads(text, object_pairs_hook=_reject_duplicate,
                         parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValidationError("json_root_not_object")
    return payload


def strict_json(path: Path) -> Dict[str, Any]:
    return strict_json_text(path.read_text(encoding="utf-8"))


def _normalize_negzero(value: Any) -> Any:
    if isinstance(value, float):
        if value == 0.0 and math.copysign(1.0, value) < 0.0:
            return 0.0
        return value
    if isinstance(value, dict):
        return {key: _normalize_negzero(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_negzero(item) for item in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(_normalize_negzero(value), sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def verify_pin_line(line: str, allowed: Dict[str, str]) -> Tuple[str, str]:
    """Return (key, digest) for a well-formed pin line that is in ``allowed``."""
    parts = line.split("  ", 1)
    if len(parts) != 2 or len(parts[0]) != 64 or any(
            char not in "0123456789abcdef" for char in parts[0]):
        raise ValidationError("malformed_pin_line")
    digest, raw = parts
    if raw.startswith("source:"):
        key = raw
        expected = allowed.get(key)
    elif raw.startswith("evidence:"):
        key = raw
        expected = allowed.get(key)
    elif raw.startswith(TASK_PREFIX):
        key = raw
        expected = ""
    else:
        key = raw
        expected = allowed.get(key)
    if expected is None:
        raise ValidationError("unexpected_pin:" + raw)
    if expected and expected != digest:
        raise ValidationError("pin_digest_mismatch:" + raw)
    return key, digest


def verify_pins() -> None:
    snapshot_path = HERE / BOARD_SNAPSHOT
    if not snapshot_path.is_file() or sha256(snapshot_path.read_bytes()) != BOARD_SNAPSHOT_SHA256:
        raise ValidationError("board_snapshot_pin_stale")
    for relative, digest in SOURCE_PINS.items():
        path = SOURCE_ROOT / relative
        if not path.is_file() or sha256(path.read_bytes()) != digest:
            raise ValidationError("source_pin_stale:" + relative)
    for relative, digest in BOUNDARY_PINS.items():
        path = SDK_ROOT / relative
        if not path.is_file() or sha256(path.read_bytes()) != digest:
            raise ValidationError("boundary_pin_stale:" + relative)
    for relative, digest in EVIDENCE_PINS.items():
        path = SDK_ROOT / relative
        if not path.is_file() or sha256(path.read_bytes()) != digest:
            raise ValidationError("evidence_pin_stale:" + relative)


def load_inputs() -> Dict[str, Any]:
    verify_pins()
    inventory = strict_json(SOURCE_ROOT / "audio-benchmark-platform/plan/INVENTORY.json")
    board_snapshot = strict_json(HERE / BOARD_SNAPSHOT)
    registry = strict_json(SOURCE_ROOT / "research/category_registry.json")
    if (board_snapshot.get("schema_id") !=
            "audio-sdk/task-evidence/survey-trn-01/board-snapshot/0.1"
            or board_snapshot.get("source") !=
            "audio-benchmark-platform/plan/swarm/TASKS.json"
            or board_snapshot.get("source_sha256") != BOARD_SNAPSHOT_SOURCE_SHA256):
        raise ValidationError("board_snapshot_identity_mismatch")
    categories = {item["id"]: item for item in inventory["taxonomy"]}
    components = {item["id"]: item for item in inventory["components"]}
    tasks = {item["id"]: item for item in board_snapshot["tasks"]}
    registry_categories = {item["id"]: item for item in registry["categories"]}
    registry_sources = {item["id"]: item for item in registry["sources"]}
    if CATEGORY_ID not in categories or CATEGORY_ID not in registry_categories:
        raise ValidationError("category_pin_missing:" + CATEGORY_ID)
    for family in FAMILIES:
        for entry in family["components"]:
            if entry["component_id"] not in components:
                raise ValidationError("component_pin_missing:" + entry["component_id"])
    for lead in SOURCE_LEADS:
        if lead["source_id"] not in registry_sources:
            raise ValidationError("source_lead_pin_missing:" + lead["source_id"])
        for component_id in lead["component_ids"]:
            if component_id not in components:
                raise ValidationError("source_lead_component_missing:" + component_id)
    for gap in GAPS:
        task = tasks.get(gap["followup_task_id"])
        if task is None:
            raise ValidationError("followup_task_missing:" + gap["followup_task_id"])
        if task.get("mode") != "feasibility":
            raise ValidationError("followup_not_feasibility:" + gap["followup_task_id"])
    return {
        "inventory": inventory,
        "board_snapshot": board_snapshot,
        "registry": registry,
        "categories": categories,
        "components": components,
        "tasks": tasks,
        "registry_categories": registry_categories,
        "registry_sources": registry_sources,
    }


def state_snapshot(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Read-only board/component snapshot used for adverse-case state checks."""
    return {
        "tasks": {
            task_id: {"mode": task.get("mode"), "status": task.get("status")}
            for task_id, task in inputs["tasks"].items()
        },
        "components": {
            component_id: {
                "evidence_status": component.get("evidence_status"),
                "disposition": component.get("disposition"),
                "task": component.get("task"),
            }
            for component_id, component in inputs["components"].items()
        },
    }


def state_digest(state: Dict[str, Any]) -> str:
    return sha256(canonical_bytes(state))


def gates() -> List[Dict[str, str]]:
    reopen = {
        "real_cohort": "Rights-cleared unfamiliar-speech and music cohort with exact labels.",
        "independent_listening": "Independent blind listening for pitch and transient audibility.",
        "target_playback_pacing": "Pinned target playback pacing, variable sample-count and deadline evidence.",
        "provider_intake": "Opt-in provider intake and licensing clearance.",
        "public_default_selection": "Explicit public default selection.",
        "exact_reference_parity": "Exact source/output interval parity with an approved external reference.",
    }
    return [{"name": name, "status": "blocked", "reopen_condition": reopen[name]}
            for name in GATE_NAMES]


def mapped_component_ids() -> List[str]:
    result = set()
    for family in FAMILIES:
        for entry in family["components"]:
            result.add(entry["component_id"])
    for lead in SOURCE_LEADS:
        result.update(lead["component_ids"])
    return sorted(result)


def validation_payload() -> Dict[str, Any]:
    """A minimal valid payload used as the read-only base for adverse cases."""
    return {
        "task_id": TASK,
        "category_id": CATEGORY_ID,
        "decision": DECISION,
        "status": STATUS,
        "qualification_status": QUALIFICATION,
        "no_missing_result_qualifies_candidate": True,
        "scope": copy.deepcopy(SCOPE),
        "boundary": copy.deepcopy(BOUNDARY),
        "gates": gates(),
        "gaps": copy.deepcopy(GAPS),
        "component_ids": mapped_component_ids(),
        "source_pins": copy.deepcopy(SOURCE_PINS),
        "evidence_pins": copy.deepcopy(EVIDENCE_PINS),
        "boundary_pins": copy.deepcopy(BOUNDARY_PINS),
    }


def validate_map(payload: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
    """Return all rejection reasons; never mutate ``payload`` or ``state``."""
    errors: List[str] = []
    required = {
        "task_id", "category_id", "decision", "status", "qualification_status",
        "no_missing_result_qualifies_candidate", "scope", "boundary", "gates",
        "gaps", "component_ids", "source_pins", "evidence_pins", "boundary_pins",
    }
    missing = sorted(required - set(payload))
    if missing:
        return ["missing_required_key:" + key for key in missing]
    if payload["task_id"] != TASK or payload["category_id"] != CATEGORY_ID:
        errors.append("task_or_category_mismatch")
    if (payload["decision"] != DECISION or payload["status"] != STATUS
            or payload["qualification_status"] != QUALIFICATION
            or payload["no_missing_result_qualifies_candidate"] is not True):
        errors.append("disposition_mismatch")
    for key, value in SCOPE.items():
        actual = payload["scope"].get(key)
        if key.startswith("real_") or key in {"runtime_executed", "listening",
                                              "device_timing", "public_benchmark",
                                              "release_claim"}:
            if actual is not False:
                errors.append("forbidden_scope_claim:" + key)
        elif actual is not True:
            errors.append("required_scope_flag_missing:" + key)
    for key, value in BOUNDARY.items():
        if key == "descriptor_settings":
            if value != {}:
                errors.append("descriptor_settings_not_empty")
        elif payload["boundary"].get(key) is not False:
            errors.append("boundary_claim_not_false:" + key)
    if len(payload["gates"]) != len(GATE_NAMES) or any(
            gate.get("status") != "blocked" or not gate.get("reopen_condition")
            for gate in payload["gates"]):
        errors.append("release_gate_not_blocked")
    task_state = state["tasks"]
    component_state = state["components"]
    gap_ids = set()
    for gap in payload["gaps"]:
        if gap["id"] in gap_ids:
            errors.append("duplicate_gap_id:" + gap["id"])
        gap_ids.add(gap["id"])
        followup = gap.get("followup_task_id")
        record = task_state.get(followup)
        if record is None:
            errors.append("unknown_followup_task:" + str(followup))
        elif record["mode"] != "feasibility":
            errors.append("followup_not_feasibility:" + str(followup))
    if gap_ids != {gap["id"] for gap in GAPS}:
        errors.append("gap_set_mismatch")
    for component_id in payload["component_ids"]:
        if component_id not in component_state:
            errors.append("unmapped_component:" + component_id)
    if set(payload["component_ids"]) != set(mapped_component_ids()):
        errors.append("component_set_mismatch")
    if (payload["source_pins"] != SOURCE_PINS or payload["evidence_pins"] != EVIDENCE_PINS
            or payload["boundary_pins"] != BOUNDARY_PINS):
        errors.append("pin_table_mismatch")
    return errors


def run_rejection(name: str, action: Callable[[], Any],
                  state: Dict[str, Any]) -> Dict[str, Any]:
    before = state_digest(state)
    status = "rejected"
    error = ""
    try:
        result = action()
    except ValidationError as exc:
        error = str(exc)
    except (ValueError, TypeError, KeyError) as exc:
        error = type(exc).__name__ + ":" + str(exc)
    else:
        if isinstance(result, list) and result:
            error = ",".join(str(item) for item in result[:3])
        else:
            status = "accepted"
            error = "unexpectedly_accepted:" + repr(result)[:80]
    after = state_digest(state)
    return {
        "name": name,
        "status": status,
        "error": error,
        "state_unchanged": before == after,
        "state_sha256": after,
    }


def adverse(state: Dict[str, Any]) -> Dict[str, Any]:
    base = validation_payload()

    def mutated(**changes: Any) -> Dict[str, Any]:
        payload = copy.deepcopy(base)
        payload.update(changes)
        return payload

    def with_scope(**changes: Any) -> Dict[str, Any]:
        payload = copy.deepcopy(base)
        payload["scope"].update(changes)
        return payload

    def with_boundary(**changes: Any) -> Dict[str, Any]:
        payload = copy.deepcopy(base)
        payload["boundary"].update(changes)
        return payload

    def with_gap_field(field: str, value: Any) -> Dict[str, Any]:
        payload = copy.deepcopy(base)
        payload["gaps"][0][field] = value
        return payload

    def with_pin(field: str, key: str, value: str) -> Dict[str, Any]:
        payload = copy.deepcopy(base)
        payload[field][key] = value
        return payload

    stale_pin = "0" * 64
    pin_line = stale_pin + "  source:audio-benchmark-platform/plan/INVENTORY.json"
    cases = [
        run_rejection("duplicate_json_key",
                      lambda: strict_json_text('{"decision":"DEFER","decision":"ALLOW"}'), state),
        run_rejection("nonfinite_nan",
                      lambda: strict_json_text('{"value":NaN}'), state),
        run_rejection("nonfinite_infinity",
                      lambda: strict_json_text('{"value":Infinity}'), state),
        run_rejection("missing_required_key",
                      lambda: _validate_removed_key(state), state),
        run_rejection("forbidden_release_claim",
                      lambda: validate_map(with_scope(release_claim=True), state), state),
        run_rejection("forbidden_runtime_execution",
                      lambda: validate_map(with_scope(runtime_executed=True), state), state),
        run_rejection("provider_registration_claim",
                      lambda: validate_map(with_boundary(registered=True), state), state),
        run_rejection("open_release_gate",
                      lambda: validate_map({"gates": [{"status": "open"}]}, state), state),
        run_rejection("unknown_followup_task",
                      lambda: validate_map(with_gap_field("followup_task_id",
                                                          "SDK-DOES-NOT-EXIST"), state), state),
        run_rejection("nonfeasibility_followup_link",
                      lambda: validate_map(with_gap_field("followup_task_id",
                                                          "SDK-FND-AUDIT"), state), state),
        run_rejection("unmapped_component",
                      lambda: validate_map(mutated(component_ids=["not-in-inventory"]), state),
                      state),
        run_rejection("stale_source_pin",
                      lambda: validate_map(with_pin("source_pins",
                                                    "audio-benchmark-platform/plan/INVENTORY.json",
                                                    stale_pin), state), state),
        run_rejection("malformed_pin_line",
                      lambda: verify_pin_line(pin_line, SOURCE_PINS), state),
    ]
    return {
        "all_rejected": all(case["status"] == "rejected" for case in cases),
        "all_state_unchanged": all(case["state_unchanged"] for case in cases),
        "state_sha256": state_digest(state),
        "cases": cases,
    }


def _validate_removed_key(state: Dict[str, Any]) -> List[str]:
    payload = copy.deepcopy(validation_payload())
    del payload["gates"]
    return validate_map(payload, state)


def category_crosscheck(inputs: Dict[str, Any]) -> Dict[str, Any]:
    inventory_category = inputs["categories"][CATEGORY_ID]
    registry_category = inputs["registry_categories"][CATEGORY_ID]
    fields = ["id", "name", "group", "scope", "purpose", "method_families",
              "input_output", "live_or_comparison_boundary", "source_ids"]
    inventory_subset = {field: inventory_category[field] for field in fields}
    registry_subset = {field: registry_category[field] for field in fields}
    return {
        "inventory": inventory_subset,
        "registry": registry_subset,
        "identical": inventory_subset == registry_subset,
        "discovery_status": inventory_category["discovery_status"],
        "candidate_census_status": inventory_category["candidate_census_status"],
        "benchmark_status": inventory_category["benchmark_status"],
        "task": inventory_category["task"],
    }


def local_evidence_path(component_id: str) -> str | None:
    prefix = "docs/task-evidence/" + component_id + "/README.md"
    return prefix if prefix in EVIDENCE_PINS else None


def family_map(inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = []
    for family in FAMILIES:
        components = []
        for entry in family["components"]:
            component_id = entry["component_id"]
            record = inputs["components"][component_id]
            component_task = inputs["tasks"].get(record.get("task"))
            evidence_path = local_evidence_path(component_id)
            components.append({
                "component_id": component_id,
                "name": record["name"],
                "area": record["area"],
                "disposition": record["disposition"],
                "evidence_status": record["evidence_status"],
                "inventory_task": record["task"],
                "board_status": component_task["status"] if component_task else None,
                "relation": entry["relation"],
                "note": entry["note"],
                "local_synthetic_evidence": evidence_path,
                "local_evidence_sha256": EVIDENCE_PINS.get(evidence_path) if evidence_path else None,
            })
        result.append({
            "id": family["id"],
            "name": family["name"],
            "original_text": family["original_text"],
            "source_family": family["source_family"],
            "components": components,
            "gap_ids": list(family["gap_ids"]),
            "coverage": ("mapped_with_local_synthetic_evidence" if any(
                item["local_synthetic_evidence"] for item in components)
                else "mapped_without_local_evidence"),
        })
    return result


def source_lead_map(inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = []
    for lead in SOURCE_LEADS:
        source = inputs["registry_sources"][lead["source_id"]]
        result.append({
            "source_id": lead["source_id"],
            "title": source["title"],
            "url": source["url"],
            "access_scope": source["access_scope"],
            "url_fetched": False,
            "match": lead["match"],
            "mapped_component_ids": list(lead["component_ids"]),
            "historical_report_pin": lead["historical_report_pin"],
            "classification": "source_text_only_not_reproduced",
            "gap_ids": list(lead["gap_ids"]),
        })
    return result


def historical_executions(inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = []
    for component_id in mapped_component_ids():
        record = inputs["components"][component_id]
        entries = [copy.deepcopy(item) for item in record.get("evidence", [])
                   if item.get("path") in SOURCE_PINS]
        if not entries:
            continue
        result.append({
            "component_id": component_id,
            "inventory_task": record["task"],
            "inventory_evidence_status": record["evidence_status"],
            "source_reported_entries": entries,
            "classification": "source_reported_not_reproduced",
        })
    return result


def task_local_executions(inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = []
    for path in sorted(EVIDENCE_PINS):
        component_id = path.split("/")[2]
        record = inputs["components"].get(component_id)
        component_task = inputs["tasks"].get(record["task"]) if record else None
        result.append({
            "component_id": component_id,
            "path": path,
            "sha256": EVIDENCE_PINS[path],
            "inventory_evidence_status": record["evidence_status"] if record else None,
            "board_status": component_task["status"] if component_task else None,
            "classification": "task_local_synthetic_reference_only",
            "qualifies_candidate": False,
        })
    return result


def gap_map(inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = []
    for gap in GAPS:
        task = inputs["tasks"][gap["followup_task_id"]]
        result.append({
            "id": gap["id"],
            "family_id": gap["family_id"],
            "description": gap["description"],
            "followup_task_id": gap["followup_task_id"],
            "followup_mode": task["mode"],
            "followup_status": task["status"],
            "followup_title": task["title"],
            "linked_on_board": True,
            "new_task_created": False,
            "reopen_condition": gap["reopen_condition"],
        })
    return result


def core_report() -> Dict[str, Any]:
    inputs = load_inputs()
    state = state_snapshot(inputs)
    errors = validate_map(validation_payload(), state)
    if errors:
        raise ValidationError("valid_payload_rejected:" + ",".join(errors))
    crosscheck = category_crosscheck(inputs)
    if not crosscheck["identical"]:
        raise ValidationError("category_pin_mismatch")
    families = family_map(inputs)
    gaps = gap_map(inputs)
    if {item["id"] for item in gaps} != {gap["id"] for gap in GAPS}:
        raise ValidationError("gap_map_incomplete")
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "category_id": CATEGORY_ID,
        "title": "Pitch-preserving speed / time-scale modification",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "no_missing_result_qualifies_candidate": True,
        "scope": copy.deepcopy(SCOPE),
        "boundary": copy.deepcopy(BOUNDARY),
        "format": copy.deepcopy(FORMAT),
        "deliverable": "Task-local category evidence map with linked feasibility gaps.",
        "contract_id": CONTRACT_SCHEMA_ID + ":" + TASK,
        "contract_sha256": sha256((HERE / "contract.json").read_bytes()),
        "board_snapshot": {
            "path": TASK_PREFIX + BOARD_SNAPSHOT,
            "sha256": BOARD_SNAPSHOT_SHA256,
            "source": "audio-benchmark-platform/plan/swarm/TASKS.json",
            "source_sha256": BOARD_SNAPSHOT_SOURCE_SHA256,
            "task_count": len(inputs["tasks"]),
            "live_board_read": False,
        },
        "source_pins": copy.deepcopy(SOURCE_PINS),
        "evidence_pins": copy.deepcopy(EVIDENCE_PINS),
        "boundary_pins": copy.deepcopy(BOUNDARY_PINS),
        "tool_provenance": list(TOOL_PROVENANCE),
        "category": crosscheck,
        "verification_profile": {
            "profile": PROFILE,
            "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "applied_to": "category_map_only",
            "runtime_executed": False,
            "pitch": "not_measured_no_rendered_audio",
            "transient_audibility": "not_measured_no_listening",
            "device_timing": "not_measured_no_device",
        },
        "families": families,
        "source_leads": source_lead_map(inputs),
        "historical_executions": historical_executions(inputs),
        "task_local_executions": task_local_executions(inputs),
        "gaps": gaps,
        "gates": gates(),
        "missing_evidence": list(MISSING_EVIDENCE),
        "adverse": adverse(state),
        "evidence_classes": [
            "inventory_text", "board_text", "registry_text", "source_reported_not_reproduced",
            "task_local_synthetic_reference_only", "category_map_only",
        ],
        "state_sha256": state_digest(state),
    }


def repeatability() -> Dict[str, Any]:
    """Three cold-start processes hashing the canonical core, without rewriting files."""
    code = ("import hashlib,sys;sys.path.insert(0,sys.argv[1]);import reference;"
            "print(hashlib.sha256(reference.canonical_report_bytes("
            "reference.core_report())).hexdigest())")
    digests = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code, str(HERE)],
                                capture_output=True, text=True, check=True, env=env)
        digests.append(result.stdout.strip())
    return {
        "count": 3,
        "method": "three_fresh_interpreters_canonical_core",
        "digests": digests,
        "byte_identical": len(set(digests)) == 1,
    }


def build_report() -> Dict[str, Any]:
    report = core_report()
    report["repeatability"] = repeatability()
    return report


def sources_bytes() -> bytes:
    """Deterministic manifest; local artifacts are digests of their current bytes."""
    lines = [
        "# SHA-256 pins for SDK-SURVEY-TRN-01.",
        "# source: paths are relative to SOURCE_ROOT; evidence: and plain paths are SDK-worktree relative.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in sorted(EVIDENCE_PINS):
        lines.append(f"{EVIDENCE_PINS[path]}  evidence:{path}")
    for path in sorted(BOUNDARY_PINS):
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for name in LOCAL_PIN_PATHS:
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")
