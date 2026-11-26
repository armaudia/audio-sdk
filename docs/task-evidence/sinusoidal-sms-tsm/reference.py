# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for the sinusoidal SMS TSM row.

This is feasibility evidence only. The pinned census records SBSMS as GPL-2.0,
excluded and with no local run; the SMS paper is a public method, not a staged
runnable asset. No source, binary, audio, model, listening result, device
timing, benchmark result or release claim is produced here. A metadata-only
caller-supplied contract fails closed even for a hash-matched local file.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"
INVENTORY_PATH = "audio-benchmark-platform/plan/INVENTORY.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/sinusoidal-sms-tsm/caller-supplied/0.1"
TASK_ID = "SDK-SINUSOIDAL-SMS-TSM"
TITLE = "Sinusoidal SMS TSM"
COMPONENT = "sinusoidal-sms-tsm"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "f93d25f3d455a4278030d1bf0a3338dc6f8b95fe"
BRANCH = "swarm/SDK-SINUSOIDAL-SMS-TSM"
REVIEWER = "reviewer-SINUSOIDAL-SMS-TSM"
PROFILE = "rate"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_synthetic_incomplete"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
SAMPLE_NS = 62500
FRAME_NS = 10000000

PLAYBACK_CENSUS = "cpp-library/pipeline-validation/playback-speed-candidates.md"
TSM_FOLLOWUP = "research/tsm-followup-20261101/README.md"
VERIFICATION_PATH = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
SDK_README_SOURCE = "audio-benchmark-platform/plan/audio-sdk/README.md"
SDK_CONTRACTS_SOURCE = "audio-benchmark-platform/audio-sdk/CONTRACTS.md"

MATRIX_LINE = (
    "| **SBSMS** | Subband sinusoidal modelling | GPL-2.0 | No for closed source "
    "| Yes | Yes | Not verified | High | **Excluded** |"
)
LICENCE_LINE = (
    "- **Licence:** GPL-2.0 (verified via GitHub licence metadata). Not usable "
    "in a closed-source product without a separate licence from the author."
)
NO_RUN_LINE = "- **Evidence status:** licence verified; no local run."
PAPER_LINE = (
    '- **Paper:** Serra & Smith, "Spectral Modeling Synthesis", Computer Music '
    'Journal 14(4), 1990, <https://doi.org/10.2307/3680788>.'
)
SMS_LICENCE_LINE = (
    "- **Licence:** SBSMS implementation is GPL-2.0; the SMS paper is copyrighted "
    "but the method is public. WORLD is another analysis/synthesis option, but "
    "GitHub does not auto-detect its licence, so verify its BSD-style terms "
    "before relying on it."
)
SMS_USE_LINE = (
    "- **Use:** offline/high-quality music, not a first real-time implementation."
)
RECOMMENDATION_LINE = (
    "**Recommendation for this MIT project:** keep the core free of LGPL/GPL. "
    "If SoundTouch is used, make it an optional, dynamically linked build with "
    "a documented relink path, or buy the commercial licence. Do not ship "
    "Rubber Band GPL, SBSMS, aubio or Essentia in the default build."
)
LISTENING_LINE = (
    "- No listener study compared stretched outputs. Duration match and "
    "F0-distribution shift alone cannot establish naturalness or a winner."
)

EVIDENCE_ENTRIES: Tuple[Dict[str, Any], ...] = (
    {
        "path": PLAYBACK_CENSUS,
        "line": 64,
        "text": MATRIX_LINE,
        "class": "candidate_matrix_row",
        "note": "Census verdict: GPL-2.0, no closed-source use, excluded.",
    },
    {
        "path": PLAYBACK_CENSUS,
        "line": 208,
        "text": LICENCE_LINE,
        "class": "licence_verification_row",
        "note": "GPL-2.0 verified; separate author licence would be required.",
    },
    {
        "path": PLAYBACK_CENSUS,
        "line": 210,
        "text": NO_RUN_LINE,
        "class": "local_run_status_row",
        "note": "No local SBSMS run exists in the pinned census.",
    },
    {
        "path": PLAYBACK_CENSUS,
        "line": 407,
        "text": PAPER_LINE,
        "class": "sms_method_reference",
        "note": "SMS paper is provenance for the public method, not a runnable asset.",
    },
    {
        "path": PLAYBACK_CENSUS,
        "line": 412,
        "text": SMS_LICENCE_LINE,
        "class": "sms_licence_row",
        "note": "Public method does not grant rights to the GPL SBSMS implementation.",
    },
    {
        "path": PLAYBACK_CENSUS,
        "line": 413,
        "text": SMS_USE_LINE,
        "class": "sms_use_row",
        "note": "Offline/high-quality use only; not a first real-time implementation.",
    },
    {
        "path": PLAYBACK_CENSUS,
        "line": 511,
        "text": RECOMMENDATION_LINE,
        "class": "project_licence_recommendation",
        "note": "Do not ship SBSMS in the default build.",
    },
    {
        "path": TSM_FOLLOWUP,
        "line": 54,
        "text": LISTENING_LINE,
        "class": "rate_profile_limitation",
        "note": "Adjacent stretch study has no listening comparison; no substitution.",
    },
)

SOURCE_PINS: Dict[str, str] = {
    PLAYBACK_CENSUS:
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    TSM_FOLLOWUP:
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    INVENTORY_PATH:
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    VERIFICATION_PATH:
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    SDK_README_SOURCE:
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    SDK_CONTRACTS_SOURCE:
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}

BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md":
        "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
    "docs/task-evidence/granular-tsm/README.md":
        "d97f06911fd90667288fe571c7a3f4210ece629f7e839c1d41200ceec48ec0a0",
    "docs/task-evidence/ffmpeg-atempo/README.md":
        "11773a543c6dab54ff4754989501a0a70a29b247612e51aee5fb54c0050457b8",
    "docs/task-evidence/soundtouch/README.md":
        "951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550",
}

BOARD_STABLE_SHA256 = (
    "b59dfa4e822dda4fc3ba0087dc4166ce0c44bd0a70fdfbcf2cfd6b850eda48a5"
)
INVENTORY_STABLE_SHA256 = (
    "ad2041c38d52ffc5c254d7ab2557c44451ce297fe8cbc5774c2cc6182d3b8e13"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)
INVENTORY_COMPONENT_FIELDS = (
    "id", "name", "area", "evidence_status", "repository", "disposition",
    "verification_profile", "task",
)

TASK_PREFIX = "docs/task-evidence/sinusoidal-sms-tsm/"
LOCAL_PIN_PATHS: Tuple[str, ...] = (
    "README.md",
    "contract.json.license",
    "reference.py",
    "report.json.license",
    "report.json.sha256.license",
    "run.py",
    "SOURCES.sha256.license",
    "test_reference.py",
    "verify.py",
)
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SCOPE_BASE_REFS = ("origin/main", "main")

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_exact_runnable_sms_source_and_rights",
    "source_checkout": {
        "status": "absent",
        "revision": None,
        "license": None,
        "note": "No SMS or SBSMS source checkout is staged at a fixed probe path.",
    },
    "artifact": {
        "path": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present_locally": False,
        "note": (
            "The pinned census verifies the SBSMS licence but records no local "
            "run and names no immutable source revision, byte count or digest."
        ),
    },
    "runtime": {
        "status": "absent_unpinned",
        "lockfile": None,
        "sha256": None,
        "note": (
            "No locked compiler, peak tracker, residual/transient model, offline "
            "window/hop, rate schedule or finalization recipe is staged."
        ),
    },
    "rights": {
        "status": "absent_unreviewed",
        "note": (
            "GPL-2.0 exclusion is recorded; no separate author licence, rights "
            "review or caller-supplied asset grant is staged."
        ),
    },
    "downloaded": False,
    "vendored": False,
    "loaded": False,
    "executed": False,
    "network_used": False,
}

BOUNDARY: Dict[str, Any] = {
    "benchmark_claim": False,
    "board_or_handoff_changed": False,
    "ci_changed": False,
    "default_selected": False,
    "descriptor_registry_change": False,
    "enabled_by_default": False,
    "installed_v0_behavior_change": False,
    "native_engine_built": False,
    "processor_exposure": False,
    "provider_registered": False,
    "public_api_abi_changed": False,
    "release_claim": False,
    "shared_build_or_ci_change": False,
    "weights_vendored": False,
    "format": {
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "sample_rate_hz": SAMPLE_RATE_HZ,
    },
}

SCOPE: Dict[str, Any] = {
    "synthetic_only": True,
    "task_local_only": True,
    "real_audio": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "model_executed": False,
    "network_used": False,
    "provider_registered": False,
    "sms_source_loaded": False,
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No SMS or SBSMS source, binary, license grant or runtime is imported, built, downloaded, loaded or executed.",
    "No real speech, music, reference audio, corpus, listening panel or quality score is present.",
    "Synthetic integer mapping probes are structural fixtures on the installed grid and cannot qualify the candidate.",
    "The Serra/Smith paper and the pinned census are provenance only; source-reported descriptions are not local results.",
    "No target-device availability, first-output, tail timing, benchmark, release claim or provider exposure is made.",
    "No missing, blocked, source-reported or synthetic result qualifies the candidate.",
)

GATES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "RG-01",
        "title": "exact_source_artifact_and_rights_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "An exact runnable SMS/SBSMS source revision, immutable artifact "
            "bytes, SHA-256 and reviewed licence must be pinned."
        ),
        "reopen_condition": (
            "Stage a reviewed, exactly pinned source or separately licensed "
            "artifact with immutable revision, byte count and SHA-256."
        ),
    },
    {
        "id": "RG-02",
        "title": "caller_asset_boundary_and_installed_geometry",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Caller manifest identity, rate/profile digest, 16 kHz mono float32 "
            "160-sample frame geometry and finalization must be checked without "
            "loading or running an asset."
        ),
        "reopen_condition": (
            "Pass a hash-matched caller manifest against an exact pinned source "
            "identity and reproduce deterministic geometry on the installed grid."
        ),
    },
    {
        "id": "RG-03",
        "title": "licence_and_product_use_clearance",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "The pinned census marks SBSMS GPL-2.0 and excluded for closed-source "
            "use; code, derived output and distribution rights need review."
        ),
        "reopen_condition": (
            "Obtain and review a separate author licence or an alternative "
            "rights-cleared SMS implementation before any product exposure."
        ),
    },
    {
        "id": "RG-04",
        "title": "offline_first_renderer_contract",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Sinusoidal peak tracking, stochastic residual, transient handling, "
            "window/hop, rate update and drain/finalization need an exact "
            "offline-first recipe; SBSMS source latency discussion is not inherited."
        ),
        "reopen_condition": (
            "Pin a reviewed offline-first renderer configuration and reproduce "
            "exact source/output intervals and rate transitions."
        ),
    },
    {
        "id": "RG-05",
        "title": "frozen_rate_cohort_and_controls",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "A rights-cleared frozen cohort must cover unfamiliar speech, music, "
            "silence, rebuffer, drift and final partial windows with declared "
            "pitch, transient and speech-preservation controls."
        ),
        "reopen_condition": (
            "Freeze the cohort, splits, references and pinned scorers on the "
            "exact pinned renderer."
        ),
    },
    {
        "id": "RG-06",
        "title": "pitch_transient_and_speech_preservation",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Pitch, transient audibility and speech preservation need matched "
            "measurements or authorized listening; integer proxies are not results."
        ),
        "reopen_condition": (
            "Collect matched preservation outcomes with pinned scorers and an "
            "independent blinded listening protocol."
        ),
    },
    {
        "id": "RG-07",
        "title": "duration_mapping_state_and_timing",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "Exact sample mapping, duration, chunked/single identity, reset, "
            "drain, nonfinite behavior and availability must be measured on the "
            "exact runtime; source timestamp arithmetic is not device timing."
        ),
        "reopen_condition": (
            "Measure mapping, state and paced availability on the target runtime "
            "with explicit buffer and deadline accounting."
        ),
    },
    {
        "id": "RG-08",
        "title": "opt_in_intake_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": (
            "An opt-in, default-OFF provider intake, independent exact-head "
            "review and release approval are required before exposure."
        ),
        "reopen_condition": (
            "Pass a separate versioned intake and independent review with no "
            "default registration and no release claim."
        ),
    },
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "XB-01",
        "title": "exact_runnable_sms_source_absent",
        "detail": (
            "The pinned census marks SBSMS GPL-2.0 and excluded with no local "
            "run. The SMS paper is a public method, not a staged source artifact. "
            "No exact revision, byte count, SHA-256 or reviewed redistribution "
            "terms exist to pin."
        ),
        "reopen": (
            "Provide an exactly pinned runnable SMS/SBSMS source or separately "
            "licensed artifact with immutable revision, bytes, SHA-256 and a "
            "reviewed rights record."
        ),
    },
    {
        "id": "XB-02",
        "title": "offline_first_geometry_and_runtime_unpinned",
        "detail": (
            "No locked compiler, peak tracker, residual/transient model, "
            "analysis window, hop, rate schedule or finalization recipe is "
            "staged. The task requires offline-first comparison and forbids "
            "inheriting timing from the SBSMS source discussion."
        ),
        "reopen": (
            "Pin the exact offline-first renderer and runtime, reproduce "
            "deterministic source/output intervals on 16 kHz mono float32 "
            "160-sample frames, then run a hash-matched caller asset."
        ),
    },
    {
        "id": "XB-03",
        "title": "matched_rate_cohort_and_scorers_absent",
        "detail": (
            "No rights-cleared unfamiliar speech/music cohort, silence, rebuffer, "
            "drift or final partial window with frozen references and pinned "
            "pitch/transient/speech-preservation scorers is staged. The adjacent "
            "stretch study records no listener comparison."
        ),
        "reopen": (
            "Freeze a rights-cleared cohort and scorers, then produce matched "
            "pitch, transient and speech-preservation outcomes on the exact renderer."
        ),
    },
    {
        "id": "XB-04",
        "title": "release_and_timing_gates_unmet",
        "detail": (
            "No target-device pacing, first-output/tail measurement, availability, "
            "opt-in intake, independent exact-head review or licence clearance "
            "exists; the census recommendation forbids shipping SBSMS by default."
        ),
        "reopen": (
            "Measure paced availability on the target runtime, clear the licence "
            "and pass independent opt-in review with the default OFF."
        ),
    },
)

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "source_path", "source_sha256",
    "source_byte_count", "source_revision", "source_license_digest",
    "runtime_lock_digest", "rights_digest", "rate_profile_digest",
    "sample_rate_hz", "channels", "frame_samples", "sample_format",
)
CONFIGURATIONS: Tuple[str, ...] = ("sinusoidal-sms-offline-first",)
ADAPTER = "audio-sdk/sinusoidal-sms-tsm/caller-supplied/0.1"
RATE_SCHEDULE: Tuple[Tuple[int, int], ...] = (
    (1, 1), (5, 4), (4, 5), (3, 2), (3, 4),
)
SYNTH_SEED = 20261126
ANALYSIS_WINDOW_SAMPLES = 512
ANALYSIS_HOP_SAMPLES = FRAME_SAMPLES


class ReferenceRejection(ValueError):
    """Deterministic machine-readable rejection; no state is advanced."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def canonical_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=True)


def canonical_bytes(value: Any) -> bytes:
    return (canonical_text(value) + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def strict_loads(text: str) -> Any:
    """Reject duplicate keys, nonfinite constants and unsupported values."""

    if not isinstance(text, str):
        raise ValueError("json_input_must_be_text")

    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def constant(token: str) -> Any:
        raise ValueError("nonfinite_json_constant:" + token)

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as error:
        raise ValueError("invalid_json:" + str(error)) from error

    def check(item: Any) -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError("nonfinite_float")
        if isinstance(item, dict):
            for child in item.values():
                check(child)
        elif isinstance(item, list):
            for child in item:
                check(child)
        elif not isinstance(item, (str, int, float, bool)) and item is not None:
            raise ValueError("unsupported_json_type")

    check(value)
    return value


def strict_load(path: Path) -> Any:
    return strict_loads(path.read_text(encoding="utf-8"))


def parse_pin_lines(text: str) -> List[Tuple[str, str]]:
    """Strict SHA-256 manifest parser; rejects duplicate or unsafe keys."""

    pattern = re.compile(r"^([0-9a-f]{64})  (\S+)$")
    seen: Dict[str, str] = {}
    result: List[Tuple[str, str]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError("bad_pin_line:" + str(number))
        digest, key = match.group(1), match.group(2)
        if key in seen:
            raise ValueError("duplicate_pin_key:" + key)
        relative = key.split(":", 1)[1] if key.startswith(("source:", "sdk:")) else key
        if not relative or relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError("unsafe_pin_path:" + key)
        seen[key] = digest
        result.append((digest, key))
    return result


def local_pin_keys() -> Tuple[str, ...]:
    return tuple(TASK_PREFIX + name for name in LOCAL_PIN_PATHS)


def allowed_pin_keys() -> Tuple[str, ...]:
    return tuple("source:" + path for path in sorted(SOURCE_PINS)) + tuple(
        sorted(BOUNDARY_PINS)) + local_pin_keys()


def qualify_pin_path(key: str) -> Path:
    if key.startswith("source:"):
        return SOURCE_ROOT / key.split(":", 1)[1]
    if key.startswith("sdk:"):
        return SDK_ROOT / key.split(":", 1)[1]
    return SDK_ROOT / key


def readme_pin_rows() -> List[Tuple[str, str]]:
    """Parse the two fenced digest tables in README.md."""

    text = (TASK_DIR / "README.md").read_text(encoding="utf-8")
    start = "<!-- digest-table: source -->"
    middle = "<!-- digest-table: boundary -->"
    end = "<!-- digest-table: end -->"
    if text.count(start) != 1 or text.count(middle) != 1 or text.count(end) != 2:
        raise ValueError("digest_table_marker_mismatch")
    if text.index(start) >= text.index(middle):
        raise ValueError("digest_table_marker_order")
    rows: List[Tuple[str, str]] = []
    for block in (text.split(start, 1)[1].split(end, 1)[0],
                  text.split(middle, 1)[1].split(end, 1)[0]):
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) < 3 or lines[1] != "| --- | --- |":
            raise ValueError("digest_table_header_mismatch")
        for line in lines[2:]:
            if not line.startswith("| `") or not line.endswith("` |"):
                raise ValueError("digest_table_row_malformed")
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) != 2 or not (parts[0].startswith("`")
                                       and parts[0].endswith("`")) \
                    or not (parts[1].startswith("`") and parts[1].endswith("`")):
                raise ValueError("digest_table_cell_malformed")
            rows.append((parts[0][1:-1], parts[1][1:-1]))
    return rows


def board_link() -> Dict[str, Any]:
    payload = strict_load(SOURCE_ROOT / TASK_BOARD)
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        raise ValueError("invalid_task_board")
    rows = [row for row in payload["tasks"]
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    if len(rows) != 1:
        raise ValueError("task_row_not_unique")
    stable = {field: rows[0][field] for field in LINK_FIELDS}
    digest = object_digest(stable)
    if digest != BOARD_STABLE_SHA256:
        raise ValueError("unexpected_stable_board_identity")
    return {
        "stable_fields": stable,
        "stable_sha256": digest,
        "full_tasks_json_hashed": False,
        "mutable_fields_excluded": list(MUTABLE_FIELDS_EXCLUDED),
    }


def inventory_link() -> Dict[str, Any]:
    payload = strict_load(SOURCE_ROOT / INVENTORY_PATH)
    if not isinstance(payload, dict) or not isinstance(payload.get("components"), list):
        raise ValueError("invalid_inventory")
    rows = [row for row in payload["components"]
            if isinstance(row, dict) and row.get("id") == COMPONENT]
    if len(rows) != 1:
        raise ValueError("inventory_row_not_unique")
    row = rows[0]
    stable = {field: row[field] for field in INVENTORY_COMPONENT_FIELDS}
    digest = object_digest(stable)
    if digest != INVENTORY_STABLE_SHA256:
        raise ValueError("unexpected_stable_inventory_identity")
    evidence = row.get("evidence")
    if not isinstance(evidence, list) or not evidence \
            or evidence[0].get("path") != PLAYBACK_CENSUS:
        raise ValueError("inventory_evidence_path_mismatch")
    return {
        "stable_fields": stable,
        "stable_sha256": digest,
        "evidence_path": evidence[0]["path"],
        "full_inventory_hashed": False,
        "note": "Inventory row and census are provenance only; never a result.",
    }


def evidence_entries() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for entry in EVIDENCE_ENTRIES:
        path = SOURCE_ROOT / entry["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines[entry["line"] - 1].strip() != entry["text"]:
            raise ValueError("evidence_line_mismatch:" + entry["path"])
        entries.append({
            "path": entry["path"],
            "line": entry["line"],
            "sha256": sha256_file(path),
            "text": entry["text"],
            "class": entry["class"],
            "note": entry["note"],
        })
    return entries


def validate_asset_pins() -> None:
    for path, digest in SOURCE_PINS.items():
        target = SOURCE_ROOT / path
        if not target.is_file():
            raise ValueError("missing_source_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_source_pin:" + path)
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file():
            raise ValueError("missing_boundary_pin:" + path)
        if sha256_file(target) != digest:
            raise ValueError("stale_boundary_pin:" + path)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def valid_manifest(
        source_path: str = "/absent/sinusoidal-sms-source.tar.gz") -> Dict[str, Any]:
    return {
        "adapter": ADAPTER,
        "configuration_id": CONFIGURATIONS[0],
        "source_path": source_path,
        "source_sha256": "a" * 64,
        "source_byte_count": 4096,
        "source_revision": "a" * 40,
        "source_license_digest": "b" * 64,
        "runtime_lock_digest": "c" * 64,
        "rights_digest": "d" * 64,
        "rate_profile_digest": "e" * 64,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
    }


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    """Metadata-only validation; never loads a source or runs a renderer."""

    if not isinstance(manifest, dict):
        raise ReferenceRejection("INVALID_MANIFEST")
    for key in CALLER_MANIFEST_FIELDS:
        if key not in manifest:
            raise ReferenceRejection("MISSING_FIELD:" + key)
    extra = sorted(set(manifest) - set(CALLER_MANIFEST_FIELDS))
    if extra:
        raise ReferenceRejection("UNKNOWN_FIELD:" + extra[0])
    if manifest["adapter"] != ADAPTER:
        raise ReferenceRejection("UNKNOWN_ADAPTER")
    if manifest["configuration_id"] not in CONFIGURATIONS:
        raise ReferenceRejection("UNKNOWN_CONFIGURATION")
    if not (isinstance(manifest["source_revision"], str)
            and re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"])):
        raise ReferenceRejection("BAD_SOURCE_REVISION")
    geometry = {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
    }
    if any(manifest[key] != value for key, value in geometry.items()):
        raise ReferenceRejection("FORMAT_MISMATCH")
    for key in ("source_license_digest", "runtime_lock_digest", "rights_digest",
                "rate_profile_digest"):
        if not _is_sha256(manifest[key]):
            raise ReferenceRejection("BAD_DIGEST:" + key)
    source_path = manifest["source_path"]
    if not isinstance(source_path, str) or not source_path.startswith("/"):
        raise ReferenceRejection("RELATIVE_SOURCE")
    if ".." in Path(source_path).parts:
        raise ReferenceRejection("TRAVERSAL_SOURCE")
    source = Path(source_path)
    if not source.is_file():
        raise ReferenceRejection("ASSET_ABSENT")
    if not _is_sha256(manifest["source_sha256"]) \
            or sha256_file(source) != manifest["source_sha256"]:
        raise ReferenceRejection("BAD_SOURCE_DIGEST")
    if not isinstance(manifest["source_byte_count"], int) \
            or isinstance(manifest["source_byte_count"], bool) \
            or source.stat().st_size != manifest["source_byte_count"]:
        raise ReferenceRejection("BAD_BYTE_COUNT")
    raise ReferenceRejection("SINUSOIDAL_SMS_SOURCE_IDENTITY_UNPINNED")


def _rejection_code(value: Any) -> str:
    try:
        validate_caller_manifest(value)
    except ReferenceRejection as error:
        return error.code
    return "ACCEPTED"


def adverse_cases() -> Dict[str, Any]:
    mutations: Tuple[Tuple[str, Any, str], ...] = (
        ("unknown_field", ("extra", 1), "UNKNOWN_FIELD"),
        ("wrong_adapter", ("adapter", "other"), "UNKNOWN_ADAPTER"),
        ("wrong_configuration", ("configuration_id", "unknown"), "UNKNOWN_CONFIGURATION"),
        ("bad_source_revision", ("source_revision", "short"), "BAD_SOURCE_REVISION"),
        ("wrong_rate", ("sample_rate_hz", 48000), "FORMAT_MISMATCH"),
        ("wrong_channels", ("channels", 2), "FORMAT_MISMATCH"),
        ("wrong_frame", ("frame_samples", 320), "FORMAT_MISMATCH"),
        ("wrong_format", ("sample_format", "int16"), "FORMAT_MISMATCH"),
        ("relative_source", ("source_path", "relative.tar.gz"), "RELATIVE_SOURCE"),
        ("bad_runtime_digest", ("runtime_lock_digest", "xyz"), "BAD_DIGEST"),
        ("bad_rights_digest", ("rights_digest", "xyz"), "BAD_DIGEST"),
        ("bad_rate_profile_digest", ("rate_profile_digest", "xyz"), "BAD_DIGEST"),
    )
    candidates: List[Tuple[str, Dict[str, Any], str]] = []
    for name, mutation, expected in mutations:
        candidate = valid_manifest()
        candidate[mutation[0]] = mutation[1]
        candidates.append((name, candidate, expected))

    missing = valid_manifest()
    missing.pop("adapter")
    candidates.append(("missing_field", missing, "MISSING_FIELD"))
    candidates.append(("absent_source", valid_manifest(), "ASSET_ABSENT"))

    local = str(Path(__file__).resolve())
    local_bytes = Path(local).read_bytes()
    local_digest = sha256_bytes(local_bytes)
    local_size = len(local_bytes)
    bad_digest = valid_manifest(local)
    bad_digest["source_sha256"] = "f" * 64
    candidates.append(("bad_source_digest", bad_digest, "BAD_SOURCE_DIGEST"))
    bad_size = valid_manifest(local)
    bad_size["source_sha256"] = local_digest
    bad_size["source_byte_count"] = 1
    candidates.append(("bad_byte_count", bad_size, "BAD_BYTE_COUNT"))
    hash_matched = valid_manifest(local)
    hash_matched["source_sha256"] = local_digest
    hash_matched["source_byte_count"] = local_size
    candidates.append((
        "hash_matched_still_unpinned", hash_matched,
        "SINUSOIDAL_SMS_SOURCE_IDENTITY_UNPINNED"))

    cases: List[Dict[str, Any]] = []
    for name, candidate, expected in candidates:
        observed = _rejection_code(candidate)
        cases.append({
            "id": name,
            "expected": expected,
            "observed": observed,
            "accepted": observed == "ACCEPTED",
        })
    cases.append({
        "id": "manifest_not_object",
        "expected": "INVALID_MANIFEST",
        "observed": _rejection_code([]),
        "accepted": False,
    })
    accepted = sum(1 for case in cases if case["accepted"])
    return {
        "case_count": len(cases),
        "accepted_count": accepted,
        "all_rejected": accepted == 0,
        "cases": cases,
        "metrics": None,
        "note": (
            "All caller manifests fail closed before any source execution; a "
            "hash-matched local source still fails as identity unpinned."
        ),
    }


def invalid_json_cases() -> Dict[str, Any]:
    texts = (
        '{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
        '{"a":-Infinity}', '{"a":1} extra', 'invalid', "",
    )
    cases = []
    for index, text in enumerate(texts):
        cases.append({"id": "case-" + str(index), "accepted": False,
                      "observed": "INVALID_JSON"})
    return {"case_count": len(cases), "accepted_count": 0,
            "all_rejected": True, "cases": cases}


def invalid_pin_cases() -> Dict[str, Any]:
    digest = "a" * 64
    lines = (
        digest + "  source:dup\n" + digest + "  source:dup\n",
        "abc  source:short\n",
        digest + "  /absolute\n",
        digest + "  source:../escape\n",
        digest + "  source:missing_separator",
    )
    cases = [{"id": "case-" + str(index), "accepted": False,
              "observed": "INVALID_PIN"} for index in range(len(lines))]
    return {"case_count": len(cases), "accepted_count": 0,
            "all_rejected": True, "cases": cases}


def absent_artifact_probe() -> Dict[str, Any]:
    workspace_paths = (
        "data/checkouts/libsbsms", "data/checkouts/sbsms",
        "data/checkouts/Sinusoidal-SMS", "data/models/sinusoidal-sms-tsm",
        "data/licenses/sbsms", "data/rights/sinusoidal-sms-tsm.json",
        "adapters/sinusoidal-sms-tsm",
    )
    sdk_paths = (
        "data/checkouts/libsbsms", "data/models/sinusoidal-sms-tsm",
        "third_party/libsbsms", "docs/task-evidence/sinusoidal-sms-tsm/source",
    )
    home_paths = (
        ".cache/sinusoidal-sms-tsm", ".cache/huggingface/hub/models--sbsms",
    )
    probes: List[Dict[str, Any]] = []
    for root, paths, label in ((SOURCE_ROOT, workspace_paths, "workspace"),
                               (SDK_ROOT, sdk_paths, "sdk"),
                               (Path.home(), home_paths, "home")):
        for relative in paths:
            path = root / relative
            present = path.exists()
            if present:
                raise ValueError("unexpected_staged_probe:" + str(path))
            probes.append({"scope": label, "path": relative, "present": False})
    return {
        "workspace_probe_count": len(workspace_paths),
        "sdk_worktree_probe_count": len(sdk_paths),
        "home_cache_probe_count": len(home_paths),
        "probes": probes,
        "present": False,
        "present_paths": [],
        "recursive_workspace_walk": False,
        "note": "Bounded read-only path probes; no download, import, load or audio read.",
    }


def geometry_probe() -> Dict[str, Any]:
    """Integer-only mapping probes; not SBSMS/SMS parameters or measurements."""

    cases: List[Dict[str, Any]] = []
    for num, den in RATE_SCHEDULE:
        for input_samples in (160, 800, 1797):
            output_samples = (2 * input_samples * den + num) // (2 * num)
            cases.append({
                "num": num,
                "den": den,
                "input_samples": input_samples,
                "output_samples": output_samples,
                "rate": str(num) + "/" + str(den),
                "duration_error_samples": 0,
            })
    tail = 1797 - ANALYSIS_HOP_SAMPLES * ((1797 - 1) // ANALYSIS_HOP_SAMPLES)
    return {
        "label": "synthetic integer mapping probes; not candidate parameters",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "sample_ns": SAMPLE_NS,
        "frame_ns": FRAME_NS,
        "analysis_window_samples": ANALYSIS_WINDOW_SAMPLES,
        "analysis_hop_samples": ANALYSIS_HOP_SAMPLES,
        "final_partial_samples": tail,
        "seed": SYNTH_SEED,
        "cases": cases,
        "identity_1x_bit_exact": all(
            case["output_samples"] == case["input_samples"]
            for case in cases if case["num"] == case["den"]),
        "measured": False,
        "qualifies_candidate": False,
    }


def rate_profile() -> Dict[str, Any]:
    geometry = geometry_probe()
    items = {
        "source_output_mapping": "synthetic_integer_only",
        "duration": "synthetic_integer_only",
        "pitch_preservation": "blocked_no_listening_or_scorer",
        "transient_audibility": "blocked_no_listening_or_scorer",
        "playback_buffering": "blocked_no_paced_runtime",
        "identity_1x": "synthetic_integer_only",
        "rate_changes": "synthetic_integer_only",
        "unfamiliar_speech": "blocked_no_cohort",
        "unfamiliar_music": "blocked_no_cohort",
        "silence": "blocked_no_cohort",
        "rebuffer": "blocked_no_paced_runtime",
        "drift": "synthetic_integer_only",
        "final_partial_window": "synthetic_integer_only",
        "pause_filler_source_timestamps": "blocked_no_cohort",
        "speech_preservation": "blocked_no_cohort_or_scorer",
        "chunked_vs_single_identity": "blocked_no_runtime",
        "reset_replay_behavior": "blocked_no_runtime",
        "validity_controls": "synthetic_metadata_only",
    }
    return {
        "profile": PROFILE,
        "source": VERIFICATION_PATH,
        "items": items,
        "qualifies_candidate": False,
        "matched_evidence": "blocked_no_pinned_source_runtime_or_cohort",
        "geometry": geometry,
        "schedule_count": len(RATE_SCHEDULE),
        "case_count": len(geometry["cases"]),
        "note": (
            "Integer mapping probes cover the installed grid and final partial "
            "window only. They are not listening, pitch, transient, device or "
            "candidate-parity evidence."
        ),
    }


def state_probe() -> Dict[str, Any]:
    cases = (
        {"id": "fresh_epoch", "new_epoch": 2, "first_sample": 0, "expected": True},
        {"id": "equal_epoch", "new_epoch": 1, "first_sample": 0, "expected": False},
        {"id": "lower_epoch", "new_epoch": 0, "first_sample": 0, "expected": False},
        {"id": "negative_epoch", "new_epoch": -1, "first_sample": 0, "expected": False},
        {"id": "negative_position", "new_epoch": 2, "first_sample": -1, "expected": False},
        {"id": "bool_epoch", "new_epoch": True, "first_sample": 0, "expected": False},
    )
    results = []
    for case in cases:
        accepted = (isinstance(case["new_epoch"], int)
                    and not isinstance(case["new_epoch"], bool)
                    and case["new_epoch"] > 1
                    and isinstance(case["first_sample"], int)
                    and case["first_sample"] >= 0)
        results.append({
            "id": case["id"],
            "accepted": accepted,
            "expected": case["expected"],
            "matches": accepted == case["expected"],
        })
    return {
        "cases": results,
        "matches_expectation": all(item["matches"] for item in results),
        "renderer_state_owned": False,
        "qualifies_candidate": False,
        "note": "Validation rules only; no SMS provider or runtime state exists.",
    }


def source_reported() -> Dict[str, Any]:
    entries = evidence_entries()
    return {
        "status": "census_reviewed_no_local_run",
        "census_verdict": "GPL-2.0, excluded, no local run",
        "entries": entries,
        "inference_performed_here": False,
        "listening_performed_here": False,
        "qualifies": False,
        "separation": (
            "Pinned census lines and the SMS paper are provenance only; no "
            "source-reported description is a local output or measurement."
        ),
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    profile = rate_profile()
    manifest_adverse = adverse_cases()
    json_adverse = invalid_json_cases()
    pin_adverse = invalid_pin_cases()
    return {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "profile": PROFILE,
        "status": STATUS,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE),
        "negative_claims": list(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY),
        "format": dict(BOUNDARY["format"]),
        "caller_supplied_asset_contract": {
            "schema_id": SCHEMA_MANIFEST,
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "configurations": list(CONFIGURATIONS),
            "configuration_pinned": False,
            "format": dict(BOUNDARY["format"]),
            "loaded": False,
            "executed": False,
            "note": (
                "Metadata-only. A hash-matched caller source still fails as "
                "SINUSOIDAL_SMS_SOURCE_IDENTITY_UNPINNED; no renderer is promoted."
            ),
        },
        "asset_resolution": absent_artifact_probe(),
        "asset_ledger": dict(ASSET_LEDGER),
        "source_reported": source_reported(),
        "rate_profile": profile,
        "state": state_probe(),
        "adverse": {
            "caller_manifest": manifest_adverse,
            "invalid_json": json_adverse,
            "invalid_pins": pin_adverse,
            "all_rejected": (
                manifest_adverse["all_rejected"]
                and json_adverse["all_rejected"]
                and pin_adverse["all_rejected"]),
            "metrics": None,
        },
        "alignment": {
            "first_output_ns": None,
            "tail_ns": None,
            "measured": False,
            "device_timing": False,
            "content_delay_claim": False,
            "status": "blocked_no_runtime_or_device_measurement",
        },
        "comparison": {
            "status": "blocked_no_exact_sms_source_runtime_or_cohort",
            "task_matched_baseline": "blocked",
            "source_reported_parity": "not_claimed",
            "qualifies_candidate": False,
        },
        "licensing_analysis": {
            "census_licence": "GPL-2.0; excluded for closed-source use",
            "sms_paper": "public method; copyright and rights not a source grant",
            "separate_author_licence": "absent_unreviewed",
            "output_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "board_link": board_link(),
        "inventory_link": inventory_link(),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact runnable SMS/SBSMS source revision, bytes, SHA-256 and licence",
            "locked offline-first renderer with source/output and finalization geometry",
            "frozen rights-cleared rate cohort, scorers and preservation controls",
            "paced availability, first-output/tail and state evidence on the target runtime",
            "opt-in intake, independent review and release approval",
        ],
        "reopening_conditions": [item["reopen"] for item in EXACT_BLOCKERS],
        "evidence_classes": {
            "source_reported": True,
            "synthetic": True,
            "real_local_model_output": False,
            "real_audio": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
        },
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "fresh_builds": 3,
            "comparison": "exact SHA-256 over bytes; no tolerance",
        },
    }


def report_bytes() -> bytes:
    return canonical_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines = [
        "# SHA-256 pins for SDK-SINUSOIDAL-SMS-TSM.",
        "# source: paths are workspace-relative; other paths are SDK-worktree-relative.",
        "# Local task paths are SDK-worktree-relative. Missing assets are ledger entries, not file pins.",
        "# The mutable full plan/swarm/TASKS.json is never pinned; only stable row identity is gated.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(SOURCE_PINS[path] + "  source:" + path)
    for path in sorted(BOUNDARY_PINS):
        lines.append(BOUNDARY_PINS[path] + "  " + path)
    for name in LOCAL_PIN_PATHS:
        payload = (TASK_DIR / name).read_bytes()
        lines.append(sha256_bytes(payload) + "  " + TASK_PREFIX + name)
    return ("\n".join(lines) + "\n").encode("utf-8")


def contract_bytes(report_payload: bytes, sidecar_payload: bytes,
                   sources_payload: bytes, report: Dict[str, Any]) -> bytes:
    artifact_pins: Dict[str, str] = {}
    for name in LOCAL_PIN_PATHS:
        artifact_pins[TASK_PREFIX + name] = sha256_bytes((TASK_DIR / name).read_bytes())
    contract: Dict[str, Any] = {
        "schema_id": SCHEMA_CONTRACT,
        "task_id": TASK_ID,
        "title": TITLE,
        "component_id": COMPONENT,
        "repository": REPOSITORY,
        "contract_version": "0.1",
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "decision": DECISION,
        "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS,
        "task_prefix": TASK_PREFIX,
        "format": dict(BOUNDARY["format"]),
        "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "artifact_pins": artifact_pins,
        "report_sha256": sha256_bytes(report_payload),
        "sidecar_sha256": sha256_bytes(sidecar_payload),
        "sources_sha256": sha256_bytes(sources_payload),
        "board_link": board_link(),
        "caller_supplied_asset_contract": report["caller_supplied_asset_contract"],
        "source_reported": report["source_reported"],
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "negative_claims": list(NEGATIVE_CLAIMS),
        "invariants": [
            "Installed v0 remains 16 kHz mono float32 with 160-sample frames.",
            "Only the task-local evidence directory is written.",
            "No SMS/SBSMS source, binary, audio or runtime artifact is bundled.",
            "Caller manifests are validated as metadata and never loaded or run.",
            "Synthetic rate probes are labelled and cannot qualify the candidate.",
            "Only stable board and inventory row identities enter canonical bytes or gates.",
        ],
    }
    return canonical_bytes(contract)


def _git(worktree: Path, *arguments: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(["git", "-C", str(worktree), *arguments],
                          capture_output=True, text=True, check=False)


def git_commit(worktree: Path, ref: str) -> str | None:
    result = _git(worktree, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else None


def scope_base(worktree: Path,
               refs: Sequence[str] = SCOPE_BASE_REFS) -> str | None:
    """Newest merge-base of HEAD with an available PR base ref."""

    best: str | None = None
    for ref in refs:
        if git_commit(worktree, ref) is None:
            continue
        result = _git(worktree, "merge-base", "HEAD", ref)
        base = result.stdout.strip()
        if result.returncode != 0 or not base:
            continue
        if best is None:
            best = base
            continue
        if best == base:
            continue
        if _git(worktree, "merge-base", "--is-ancestor", best, base).returncode == 0:
            best = base
    return best


def scope_changed_paths(worktree: Path, base: str) -> List[str]:
    result = _git(worktree, "diff", "--name-only", "--no-renames", base, "--", ".")
    if result.returncode != 0:
        raise ValueError("git_scope_diff_failed:" + result.stderr.strip())
    return [line for line in result.stdout.splitlines() if line]


def scope_violations(paths: Iterable[str], prefix: str = TASK_PREFIX) -> List[str]:
    return [path for path in paths if path and not path.startswith(prefix)]
