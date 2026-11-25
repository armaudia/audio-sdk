# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local ENG category evidence map.

Only pinned inventory, plan and board records are read. ENG is the engineering
Delivery and audio interface support category (ENG-01..ENG-04), not a language
code. No audio, corpus, model, weights, codec, device, listening, benchmark or
release action is performed. All output is canonical stdlib-only JSON.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", str(SDK_ROOT.parents[2])))

TASK = "SDK-SURVEY-ENG-03"
TITLE = "ENG category evidence map"
SLUG = "survey-eng-03"
TASK_PREFIX = f"docs/task-evidence/{SLUG}/"
BASE_COMMIT = "c9296ae96a2b58efae559bd22e7760122c886df8"
BRANCH = "swarm/SDK-SURVEY-ENG-03"
SCHEMA_ID = f"audio-sdk/task-evidence/{SLUG}/report/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "evidence"
STATUS = "incomplete"
QUALIFICATION = "not_qualified"
DECISION = "DEFER"

CATEGORY_IDS = ["ENG-01", "ENG-02", "ENG-03", "ENG-04"]
CATEGORY_SOURCE_IDS = {
    "ENG-01": ["S42"],
    "ENG-02": ["S27", "S41"],
    "ENG-03": ["S41"],
    "ENG-04": ["S43", "S44", "S30"],
}
OWNING_TASK = {
    "ENG-01": "SDK-SURVEY-ENG-01",
    "ENG-02": "SDK-SURVEY-ENG-02",
    "ENG-03": "SDK-SURVEY-ENG-03",
    "ENG-04": "SDK-SURVEY-ENG-04",
}
CATEGORY_SCOPE = {
    "code": "ENG",
    "meaning": "engineering Delivery and audio interface support",
    "category_ids": CATEGORY_IDS,
    "not_a_language_scope": True,
    "excluded_examples": ["REC-02 language identification",
                          "whisper-tiny-en-int8-via-sherpa-onnx"],
}

SOURCE_PINS: Dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/swarm/TASKS.json":
        "16b37d5bc3a2018a1f1754ca2436727791d815e55ffc64bf6a3f420729bb8bd3",
}
SOURCE_PIN_SELECTORS = {
    "audio-benchmark-platform/plan/swarm/TASKS.json":
        "selected-board-task-records/0.1:id,mode,repository,title,component",
}
BOARD_PIN_TASK_IDS = [
    "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
    "SDK-BUFFER-OCCUPANCY-CONTROLLER",
    "SDK-CAPSC-BUFFER-OCCUPANCY-PACING",
    "SDK-COREAUDIO-AUDIOUNIT-DUPLEX-HOST",
    "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING",
    "SDK-OPUS-1-4-STANDARD-DECODER-PLC",
    "SDK-OPUS-DRED",
    "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE",
    "SDK-SPEEX-RESAMPLER",
    "SDK-SURVEY-ENG-01",
    "SDK-SURVEY-ENG-02",
    "SDK-SURVEY-ENG-03",
    "SDK-SURVEY-ENG-04",
    "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS",
    "SDK-WEBRTC-NETEQ",
]
BOARD_PIN_FIELDS = ("id", "mode", "repository", "title", "component")
# Frozen at report generation; mutable board status is an observation, not a pin.
BOARD_STATUS_SNAPSHOT = {
    "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT": "queued",
    "SDK-BUFFER-OCCUPANCY-CONTROLLER": "done",
    "SDK-CAPSC-BUFFER-OCCUPANCY-PACING": "queued",
    "SDK-COREAUDIO-AUDIOUNIT-DUPLEX-HOST": "done",
    "SDK-NUMPY-SCIPY-SOUNDFILE-WAV-AND-RESAMPLING": "done",
    "SDK-OPUS-1-4-STANDARD-DECODER-PLC": "done",
    "SDK-OPUS-DRED": "queued",
    "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE": "queued",
    "SDK-SPEEX-RESAMPLER": "queued",
    "SDK-SURVEY-ENG-01": "in_progress",
    "SDK-SURVEY-ENG-02": "in_progress",
    "SDK-SURVEY-ENG-03": "in_progress",
    "SDK-SURVEY-ENG-04": "in_progress",
    "SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS": "done",
    "SDK-WEBRTC-NETEQ": "queued",
}
BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    ".github/workflows/release.yml":
        "6fee1576bf3517cf8aa2a9f963988ea7aac41e16d32df506336a0ee408a4ebfc",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "docs/task-evidence/buffer-occupancy-controller/README.md":
        "862a94c9add8ecd5e15f09a543ff17100dc5680da00f8a0635a884509cb51a33",
    "docs/task-evidence/duplex-clocks/README.md":
        "8e1a355bd36e561e8f1b634a5f5ec351e15d1785be8b6f4713bef33ec97e0325",
    "docs/task-evidence/elastic-pcm-packets/README.md":
        "15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742",
    "docs/task-evidence/linear-interpolation-plc/README.md":
        "5102676797554c3e6bc83207a848d35b72783bead5eac13ad60c5a16bd940742",
    "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md":
        "9f91d406909fe2f9fa7cfd4b954639d081a12ab16005be761707b6f5c998f40c",
    "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md":
        "ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df",
    "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md":
        "7bcf299b29fee342daa7bae0f141e59d86680e16189e88c34a71d2c0e4fa2e75",
}
LOCAL_PIN_PATHS = [
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
]

SCOPE: Dict[str, Any] = {
    "source_and_board_record_mapping_only": True,
    "synthetic_state_controls_only": True,
    "real_corpus": False,
    "real_weights": False,
    "audio_runtime_executed": False,
    "model_runtime_executed": False,
    "vendor_runtime_executed": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "release_claim": False,
    "registered_provider": False,
    "task_local_only": True,
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
    "ci_workflow_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
}
FORMAT: Dict[str, Any] = {
    "sample_rate_hz": 16000,
    "channels": 1,
    "sample_format": "f32",
    "frame_samples": 160,
    "public_v0_geometry_preserved": True,
    "sdk_callback_invoked": False,
}
FOLLOW_UP_POLICY: Dict[str, Any] = {
    "invent_new_tasks": False,
    "board_only": True,
    "allowed_modes": ["feasibility"],
    "existing_feasibility_task_ids": [
        "SDK-SPEEX-RESAMPLER",
        "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
        "SDK-WEBRTC-NETEQ",
        "SDK-CAPSC-BUFFER-OCCUPANCY-PACING",
        "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE",
        "SDK-OPUS-DRED",
    ],
}
GATE_NAMES = [
    "rights_cleared_corpus",
    "pinned_runtime_and_assets",
    "independent_listening",
    "target_device_pacing",
    "provider_intake",
    "public_default_selection",
    "exact_reference_parity",
    "independent_review_and_board",
]
MISSING_EVIDENCE = [
    "rights-cleared frozen cohort for the intended workload",
    "pinned permitted runtime, assets and exact license notices",
    "independent listening for intelligibility, naturalness and pitch",
    "target-device pacing, rebuffer, drift, deadline and resource evidence",
    "opt-in provider intake and licensing clearance",
    "explicit public default selection",
    "exact parity with an approved external reference",
    "independent review and board transition",
]

MATCHED_COMPONENTS: Dict[str, List[Dict[str, str]]] = {
    "ENG-01": [
        {"component_id": "numpy-scipy-soundfile-wav-and-resampling",
         "evidence_path": "docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md",
         "outcome": "offline tool fixture; not an SDK rate path"},
        {"component_id": "typed-frame-resample-and-drift-diagnostics",
         "evidence_path": "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md",
         "outcome": "source-coordinate conversions only; no measured device delay"},
    ],
    "ENG-02": [
        {"component_id": "typed-frame-resample-and-drift-diagnostics",
         "evidence_path": "docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md",
         "outcome": "integer ppm source clock map; no live drift observation"},
        {"component_id": "coreaudio-audiounit-duplex-host",
         "evidence_path": "CONTRACTS.md",
         "outcome": "partial host record; device-clock evidence still blocked"},
    ],
    "ENG-03": [
        {"component_id": "webrtc-neteq",
         "evidence_path": "docs/task-evidence/elastic-pcm-packets/README.md",
         "outcome": "considered source lead; no NetEq trace replay executed"},
        {"component_id": "buffer-occupancy-controller",
         "evidence_path": "docs/task-evidence/buffer-occupancy-controller/README.md",
         "outcome": "synthetic queue control law only; no device underrun evidence"},
    ],
    "ENG-04": [
        {"component_id": "opus-1-4-standard-decoder-plc",
         "evidence_path": "docs/task-evidence/opus-1-4-standard-decoder-plc/README.md",
         "outcome": "synthetic decoder-PLC-style control; no codec stream invoked"},
        {"component_id": "opus-packetization-fec-dtx-and-comfort-noise",
         "evidence_path": "docs/task-evidence/elastic-pcm-packets/README.md",
         "outcome": "considered source lead; packet trace contract only"},
    ],
}

GAP_DEFINITIONS: Dict[str, List[Dict[str, Optional[str]]]] = {
    "ENG-01": [
        {"id": "ENG-01-G1",
         "statement": "No exact pinned resampler source, asset or matched rate-conversion run exists for the S42 lead; the component is only catalogued as considered.",
         "follow_up_task_id": "SDK-SPEEX-RESAMPLER",
         "no_task_reason": None,
         "reopen_condition": "Pin the resampler source/version, permitted scope, exact conversion test and matched cost/delay evidence."},
        {"id": "ENG-01-G2",
         "statement": "Framing/channel mapping has model-free conversion evidence only; no installed-consumer conversion cost or content-delay result exists.",
         "follow_up_task_id": None,
         "no_task_reason": "Board has no feasibility task for generic framing/channel mapping; typed-frame diagnostics is a done implementation task, not a feasibility follow-up.",
         "reopen_condition": "Agree an installed-consumer conversion fixture and measure cost/content delay in chain accounting."},
    ],
    "ENG-02": [
        {"id": "ENG-02-G1",
         "statement": "No live clock drift or calibrated alignment evidence exists for the S27/S41 leads; the clock fixture is explicitly model-free.",
         "follow_up_task_id": "SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT",
         "no_task_reason": None,
         "reopen_condition": "Freeze geometry, timestamp calibration and held-out alignment labels with measured drift traces."},
        {"id": "ENG-02-G2",
         "statement": "No measured render/reference synchronization trace covers gap, discontinuity and teardown behavior on the intended target.",
         "follow_up_task_id": None,
         "no_task_reason": "Board has no feasibility task for render/reference synchronization; SDK-FND-DUPLEX is a done foundation, not a feasibility follow-up.",
         "reopen_condition": "Pin a duplex trace fixture, device clock domains and target teardown evidence."},
    ],
    "ENG-03": [
        {"id": "ENG-03-G1",
         "statement": "No real NetEq jitter-buffer trace replay or codec-integrated playout run exists for the S41 lead.",
         "follow_up_task_id": "SDK-WEBRTC-NETEQ",
         "no_task_reason": None,
         "reopen_condition": "Pin permitted NetEq source/version, trace replay, codec integration and target playout evidence."},
        {"id": "ENG-03-G2",
         "statement": "No adaptive playout controller has matched queue debt, underrun and recovery evidence; API block size is not total latency.",
         "follow_up_task_id": "SDK-CAPSC-BUFFER-OCCUPANCY-PACING",
         "no_task_reason": None,
         "reopen_condition": "Separate playout control from speech estimation and record queue debt, underruns, recovery and device timing."},
    ],
    "ENG-04": [
        {"id": "ENG-04-G1",
         "statement": "No pinned packet trace demonstrates codec negotiation, packet duration, FEC, DTX or comfort noise through a receive/transmit packet contract.",
         "follow_up_task_id": "SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE",
         "no_task_reason": None,
         "reopen_condition": "Pin codec/source, packet trace and license scope; verify features without treating them as generic enhancement."},
        {"id": "ENG-04-G2",
         "statement": "No matched bitrate, redundancy, jitter and delay evidence exists for redundancy-assisted recovery.",
         "follow_up_task_id": "SDK-OPUS-DRED",
         "no_task_reason": None,
         "reopen_condition": "Use a matching encoder/decoder, measure bitrate, redundancy, jitter and delay, and keep blind recovery separate."},
        {"id": "ENG-04-G3",
         "statement": "Network/codec behavior is not separated from generic enhancement in a blocked receive pipeline.",
         "follow_up_task_id": None,
         "no_task_reason": "Board has SDK-PIPE-RECEIVE as a blocked pipeline task, not a feasibility follow-up; no feasibility task exists for this gap.",
         "reopen_condition": "Unblock the receive pipeline with pinned Opus runtime and limiter reproducibility before any matched receive claim."},
    ],
}


class Rejected(Exception):
    """Raised before any state change when an input fails validation."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    """Canonical JSON: sorted keys, compact separators, no NaN/Infinity."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def canonical_report_bytes(report: Dict[str, Any]) -> bytes:
    return canonical_bytes(report) + b"\n"


def _reject_duplicate(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise Rejected("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise Rejected("nonfinite_json_constant:" + token)


def strict_json_bytes(raw: bytes) -> Dict[str, Any]:
    try:
        payload = json.loads(raw.decode("utf-8"),
                             object_pairs_hook=_reject_duplicate,
                             parse_constant=_reject_constant)
    except Rejected:
        raise
    except (UnicodeError, ValueError) as error:
        raise Rejected("invalid_json:" + type(error).__name__) from error
    if not isinstance(payload, dict):
        raise Rejected("root_not_object")
    return payload


def strict_json_path(path: Path) -> Dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise Rejected("missing_file:" + str(path)) from error
    return strict_json_bytes(raw)


def board_snapshot_bytes(board: Dict[str, Any]) -> bytes:
    """Stable identity/mode fields only; mutable board status is not pinned."""
    tasks = _index_by_id(board.get("tasks"), "tasks")
    selected: Dict[str, Any] = {}
    for task_id in BOARD_PIN_TASK_IDS:
        task = tasks.get(task_id)
        if task is None:
            raise Rejected("board_snapshot_task_missing:" + task_id)
        selected[task_id] = {field: task.get(field) for field in BOARD_PIN_FIELDS}
    return canonical_bytes(selected) + b"\n"


def validate_pins() -> Dict[str, bool]:
    verified: Dict[str, bool] = {}
    for relative, expected in SOURCE_PINS.items():
        path = SOURCE_ROOT / relative
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise Rejected("source_pin_missing:" + relative) from error
        actual = sha256(board_snapshot_bytes(strict_json_bytes(raw))) if (
            relative in SOURCE_PIN_SELECTORS) else sha256(raw)
        if actual != expected:
            raise Rejected("source_pin_mismatch:" + relative)
        verified["source:" + relative] = True
    for relative, expected in BOUNDARY_PINS.items():
        path = SDK_ROOT / relative
        try:
            actual = sha256(path.read_bytes())
        except OSError as error:
            raise Rejected("boundary_pin_missing:" + relative) from error
        if actual != expected:
            raise Rejected("boundary_pin_mismatch:" + relative)
        verified[relative] = True
    return verified


def _index_by_id(items: Any, label: str) -> Dict[str, Dict[str, Any]]:
    if not isinstance(items, list):
        raise Rejected("bad_record_list:" + label)
    result: Dict[str, Dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise Rejected("bad_record:" + label)
        if item["id"] in result:
            raise Rejected("duplicate_record_id:" + item["id"])
        result[item["id"]] = item
    return result


def validate_map(categories: Any, board_tasks: Dict[str, Dict[str, Any]]) -> None:
    """Validate a map before it is allowed to become state."""
    if not isinstance(categories, dict) or set(categories) != set(CATEGORY_IDS):
        raise Rejected("category_set_mismatch")
    for category_id in CATEGORY_IDS:
        entry = categories[category_id]
        if not isinstance(entry, dict):
            raise Rejected("category_not_object:" + category_id)
        required = {"category_id", "owning_task", "name", "scope", "purpose",
                    "method_families", "source_ids", "source_leads",
                    "matched_components", "historical_executions", "gaps",
                    "live_or_comparison_boundary", "local_vs_reported",
                    "release_boundary", "status", "qualification_status"}
        if not required <= set(entry):
            raise Rejected("missing_category_keys:" + category_id)
        if entry["owning_task"] != OWNING_TASK[category_id]:
            raise Rejected("owning_task_mismatch:" + category_id)
        families = entry["method_families"]
        if not isinstance(families, dict) or set(families) != {"classic", "ml"}:
            raise Rejected("method_family_mismatch:" + category_id)
        source_ids = entry["source_ids"]
        if (not isinstance(source_ids, list) or source_ids !=
                CATEGORY_SOURCE_IDS[category_id]):
            raise Rejected("invalid_source_ids:" + category_id)
        lead_ids = [lead.get("id") for lead in entry["source_leads"]]
        if lead_ids != source_ids:
            raise Rejected("source_lead_mismatch:" + category_id)
        if not isinstance(entry["gaps"], list):
            raise Rejected("invalid_gaps:" + category_id)
        for gap in entry["gaps"]:
            if not isinstance(gap, dict) or gap.get("invented") is not False:
                raise Rejected("invented_or_invalid_gap:" + category_id)
            task_id = gap.get("follow_up_task_id")
            if task_id is None:
                if not gap.get("no_task_reason"):
                    raise Rejected("missing_no_task_reason:" + gap.get("id", "?"))
                continue
            task = board_tasks.get(task_id)
            if task is None:
                raise Rejected("unknown_follow_up_task:" + task_id)
            if task.get("mode") != "feasibility":
                raise Rejected("follow_up_not_feasibility:" + task_id)
    for known in FOLLOW_UP_POLICY["existing_feasibility_task_ids"]:
        task = board_tasks.get(known)
        if task is None or task.get("mode") != "feasibility":
            raise Rejected("policy_task_not_feasibility:" + known)


class MapState:
    """Immutable-by-convention map state; rejected inputs never mutate it."""

    def __init__(self, categories: Dict[str, Any],
                 board_tasks: Dict[str, Dict[str, Any]]) -> None:
        self._categories = categories
        self._board_tasks = board_tasks

    def digest(self) -> str:
        return sha256(canonical_bytes(self._categories))

    def apply(self, raw: Any) -> Dict[str, Any]:
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        payload = strict_json_bytes(raw) if isinstance(raw, bytes) else raw
        validate_map(payload, self._board_tasks)
        self._categories = payload
        return {"status": "accepted", "state_digest": self.digest()}


def _evidence_entries(component: Dict[str, Any]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for item in component.get("evidence", [])[:2]:
        if not isinstance(item, dict):
            raise Rejected("bad_component_evidence")
        result.append({
            "path": item.get("path"),
            "line": item.get("line"),
            "record": item.get("record"),
            "record_name": item.get("record_name"),
            "finding": item.get("finding"),
            "report_paths": item.get("report_paths", []),
        })
    return result


def build_categories(inventory: Dict[str, Any],
                     board: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    taxonomy = _index_by_id(inventory.get("taxonomy"), "taxonomy")
    sources = _index_by_id(inventory.get("taxonomy_sources"), "taxonomy_sources")
    components = _index_by_id(inventory.get("components"), "components")
    tasks = _index_by_id(board.get("tasks"), "tasks")
    result: Dict[str, Dict[str, Any]] = {}
    for category_id in CATEGORY_IDS:
        row = taxonomy.get(category_id)
        if row is None:
            raise Rejected("taxonomy_category_missing:" + category_id)
        source_leads = []
        for source_id in row.get("source_ids", []):
            lead = sources.get(source_id)
            if lead is None:
                raise Rejected("source_lead_missing:" + source_id)
            source_leads.append({
                "id": lead["id"],
                "title": lead.get("title"),
                "url": lead.get("url"),
                "researcher": lead.get("researcher"),
                "access_scope": lead.get("access_scope"),
            })
        matched = []
        for link in MATCHED_COMPONENTS[category_id]:
            component_id = link["component_id"]
            component = components.get(component_id)
            if component is None:
                raise Rejected("component_missing:" + component_id)
            component_task = tasks.get(component.get("task", ""))
            if component_task is None:
                raise Rejected("component_task_missing:" + component_id)
            evidence_path = link["evidence_path"]
            if evidence_path not in BOUNDARY_PINS:
                raise Rejected("component_evidence_unpinned:" + evidence_path)
            matched.append({
                "component_id": component_id,
                "name": component.get("name"),
                "inventory_evidence_status": component.get("evidence_status"),
                "inventory_disposition": component.get("disposition"),
                "inventory_task_id": component.get("task"),
                "board_mode": component_task.get("mode"),
                "board_status": BOARD_STATUS_SNAPSHOT[component_task["id"]],
                "evidence_path": evidence_path,
                "evidence_sha256": BOUNDARY_PINS[evidence_path],
                "outcome": link["outcome"],
                "qualifies_candidate": False,
            })
        gaps = []
        for definition in GAP_DEFINITIONS[category_id]:
            task_id = definition["follow_up_task_id"]
            if task_id is None:
                mode = None
                status = "no_board_task"
            else:
                follow_up = tasks.get(task_id)
                if follow_up is None:
                    raise Rejected("follow_up_missing:" + task_id)
                if follow_up.get("mode") != "feasibility":
                    raise Rejected("follow_up_not_feasibility:" + task_id)
                mode = follow_up.get("mode")
                status = BOARD_STATUS_SNAPSHOT[task_id]
            gaps.append({
                "id": definition["id"],
                "statement": definition["statement"],
                "actionable": True,
                "linked_source_ids": row.get("source_ids", []),
                "follow_up_task_id": task_id,
                "follow_up_mode": mode,
                "follow_up_status": status,
                "no_task_reason": definition["no_task_reason"],
                "invented": False,
                "reopen_condition": definition["reopen_condition"],
            })
        result[category_id] = {
            "category_id": category_id,
            "owning_task": OWNING_TASK[category_id],
            "name": row.get("name"),
            "scope": row.get("scope"),
            "purpose": row.get("purpose"),
            "method_families": {
                "classic": row.get("method_families", {}).get("classic"),
                "ml": row.get("method_families", {}).get("ml"),
            },
            "source_ids": row.get("source_ids", []),
            "source_leads": source_leads,
            "matched_components": matched,
            "historical_executions": [
                _evidence_entries(components[link["component_id"]])[0]
                for link in MATCHED_COMPONENTS[category_id]
            ],
            "gaps": gaps,
            "live_or_comparison_boundary": row.get("live_or_comparison_boundary"),
            "local_vs_reported": {
                "local": "Pinned records and README evidence only; no audio, runtime, corpus or device execution.",
                "reported": "Inventory evidence_status and board status values are catalogued records, not reproduced results.",
                "not_pooled": True,
            },
            "release_boundary": "No provider registration, default selection, ABI/shared-build/CI change or release claim.",
            "status": STATUS,
            "qualification_status": QUALIFICATION,
        }
    validate_map(result, tasks)
    return result


def adverse(categories: Dict[str, Dict[str, Any]],
            board_tasks: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    initial = copy.deepcopy(categories)
    state = MapState(copy.deepcopy(categories), board_tasks)
    before = state.digest()
    mutations: Dict[str, Any] = {}

    missing = copy.deepcopy(initial)
    del missing["ENG-04"]
    mutations["missing_category"] = missing

    unknown = copy.deepcopy(initial)
    unknown["ENG-03"]["gaps"][0]["follow_up_task_id"] = "SDK-NOT-A-TASK"
    mutations["unknown_follow_up_task"] = unknown

    nonfeasible = copy.deepcopy(initial)
    nonfeasible["ENG-01"]["gaps"][0]["follow_up_task_id"] = "SDK-FND-ELASTIC"
    mutations["nonfeasibility_follow_up"] = nonfeasible

    invented = copy.deepcopy(initial)
    invented["ENG-02"]["gaps"][0]["invented"] = True
    mutations["invented_task_flag"] = invented

    families = copy.deepcopy(initial)
    families["ENG-01"]["method_families"] = {"classic": "only"}
    mutations["invalid_method_family"] = families

    source_ids = copy.deepcopy(initial)
    source_ids["ENG-02"]["source_ids"] = ["S999"]
    mutations["invalid_source_id"] = source_ids

    no_keys = copy.deepcopy(initial)
    del no_keys["ENG-01"]["gaps"]
    mutations["missing_required_key"] = no_keys

    mutations["duplicate_key"] = b'{"ENG-01":{},"ENG-01":{}}'
    mutations["nonfinite"] = b'{"ENG-01":{"score":NaN}}'
    mutations["infinity"] = b'{"ENG-01":{"score":Infinity}}'

    cases: Dict[str, Any] = {}
    for name, payload in mutations.items():
        try:
            state.apply(payload)
            cases[name] = {"status": "not_rejected", "reason": "none",
                           "state_unchanged": state.digest() == before}
        except Rejected as error:
            cases[name] = {"status": "rejected", "reason": error.reason,
                           "state_unchanged": state.digest() == before}
    after = state.digest()
    return {
        "cases": cases,
        "all_rejected": all(item["status"] == "rejected" for item in cases.values()),
        "state_unchanged": all(item["state_unchanged"] for item in cases.values())
                           and before == after,
        "state_digest_before": before,
        "state_digest_after": after,
        "valid_map_accepted": MapState(copy.deepcopy(initial),
                                       board_tasks).apply(canonical_bytes(initial))[
                                           "status"] == "accepted",
    }


def repeatability() -> Dict[str, Any]:
    """Three cold-start processes hashing the canonical core report."""
    code = ("import hashlib,sys;sys.path.insert(0,sys.argv[1]);import reference;"
            "print(hashlib.sha256(reference.canonical_report_bytes("
            "reference.core_report())).hexdigest())")
    digests: List[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code, str(HERE)],
                                capture_output=True, text=True, check=True, env=env)
        digests.append(result.stdout.strip())
    return {"count": 3, "method": "three_fresh_interpreters_canonical_core",
            "digests": digests, "byte_identical": len(set(digests)) == 1}


def gates() -> List[Dict[str, str]]:
    conditions = {
        "rights_cleared_corpus": "Rights-cleared frozen cohort and exact labels for the intended workload.",
        "pinned_runtime_and_assets": "Pinned permitted runtime, assets and license notices with exact scope.",
        "independent_listening": "Independent listening for intelligibility, naturalness and pitch; proxies cannot qualify.",
        "target_device_pacing": "Measured target-device pacing, clock, rebuffer, deadline and resource evidence.",
        "provider_intake": "Licensing review and opt-in provider intake; no registration before approval.",
        "public_default_selection": "Explicit public default decision; currently off and unregistered.",
        "exact_reference_parity": "Exact parity with an approved external reference for the same inputs.",
        "independent_review_and_board": "Independent review and board transition after task-local evidence.",
    }
    return [{"name": name, "status": "blocked", "reopen_condition": conditions[name]}
            for name in GATE_NAMES]


def core_report() -> Dict[str, Any]:
    pin_verification = validate_pins()
    inventory = strict_json_path(SOURCE_ROOT /
                                  "audio-benchmark-platform/plan/INVENTORY.json")
    board = strict_json_path(SOURCE_ROOT /
                              "audio-benchmark-platform/plan/swarm/TASKS.json")
    taxonomy = _index_by_id(inventory.get("taxonomy"), "taxonomy")
    categories = build_categories(inventory, board)
    board_tasks = _index_by_id(board.get("tasks"), "tasks")
    categories_by_id = {key: value for key, value in categories.items()}
    inventory_source_ids = set(sources["id"] for sources in
                               inventory.get("taxonomy_sources", [])
                               if isinstance(sources, dict) and "id" in sources)
    controls = {
        "identity": {
            "category_ids_match_inventory":
                set(categories) == set(CATEGORY_IDS),
            "method_family_keys_match_inventory": all(
                set(categories[key]["method_families"]) ==
                set(taxonomy[key].get("method_families", {})) for key in CATEGORY_IDS),
            "source_leads_resolved": all(
                set(lead["id"] for lead in entry["source_leads"]) <= inventory_source_ids
                for entry in categories.values()),
            "matched_component_tasks_resolved": all(
                item["board_status"] is not None
                for entry in categories.values()
                for item in entry["matched_components"]),
        },
        "named_control": {
            "id": "catalogued_only_no_component_claim",
            "description": "Catalogued source status and considered component status are not reproduced results.",
        },
        "candidate": {
            "id": "category_evidence_map",
            "description": "Deterministic source/board mapping with synthetic adverse controls.",
            "not_qualifying": True,
        },
        "all_present": True,
    }
    controls["all_present"] = all(controls["identity"].values())
    return {
        "schema_id": SCHEMA_ID,
        "task_id": TASK,
        "title": TITLE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "profile_application": {
            "profile": PROFILE,
            "source": SOURCE_PINS["audio-benchmark-platform/plan/swarm/VERIFICATION.md"],
            "status": "partial_synthetic_only",
            "scorer": "reference.py canonical report builder; not a corpus scorer",
            "corpus": None,
            "cohort": None,
            "invalid_case": "adverse cases are executed against a stateful validator",
            "representative_valid_result": "category map built from pinned inventory and board records",
            "no_cohort_or_scorer_claim": True,
        },
        "status": STATUS,
        "qualification_status": QUALIFICATION,
        "decision": DECISION,
        "no_missing_result_qualifies_candidate": True,
        "category_scope": CATEGORY_SCOPE,
        "scope": SCOPE,
        "boundary": BOUNDARY,
        "format": FORMAT,
        "deliverable": "Task-local evidence map with matched components and linked feasibility follow-ups.",
        "contract_id": f"{CONTRACT_SCHEMA_ID}:{TASK}",
        "contract_sha256": sha256((HERE / "contract.json").read_bytes()),
        "source_pins": SOURCE_PINS,
        "source_pin_selectors": SOURCE_PIN_SELECTORS,
        "boundary_pins": BOUNDARY_PINS,
        "source_pin_verification": pin_verification,
        "board_status_is_observation_only": True,
        "follow_up_policy": FOLLOW_UP_POLICY,
        "controls": controls,
        "categories": categories_by_id,
        "adverse": adverse(categories, board_tasks),
        "missing_evidence": MISSING_EVIDENCE,
        "evidence_classes": ["inventory_taxonomy", "board_task_records",
                             "pinned_component_evidence_readmes",
                             "synthetic_state_controls", "proposal_only"],
        "gates": gates(),
    }


def build_report() -> Dict[str, Any]:
    report = core_report()
    report["repeatability"] = repeatability()
    return report


def sources_bytes() -> bytes:
    """Deterministic manifest; local artifact digests come from current bytes."""
    lines = [
        "# SHA-256 pins for SDK-SURVEY-ENG-03.",
        "# source: paths are relative to SOURCE_ROOT; other paths are SDK-worktree relative.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(f"{SOURCE_PINS[path]}  source:{path}")
    for path in sorted(BOUNDARY_PINS):
        lines.append(f"{BOUNDARY_PINS[path]}  {path}")
    for name in LOCAL_PIN_PATHS:
        lines.append(f"{sha256((HERE / name).read_bytes())}  {TASK_PREFIX}{name}")
    return ("\n".join(lines) + "\n").encode("ascii")
