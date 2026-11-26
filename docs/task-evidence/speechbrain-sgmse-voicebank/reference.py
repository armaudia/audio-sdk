# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for SpeechBrain SGMSE-VoiceBank.

Feasibility evidence only. This package models a caller-supplied-asset
boundary with synthetic, integer-only structural controls. It does not
download, load, import or execute SpeechBrain, SGMSE, sgmse, PyTorch,
lightning, torchaudio, Hugging Face Hub or any enhancement runtime. No
checkpoint, corpus, real audio, listening result, device timing, benchmark
result or release claim is included, and no result here qualifies the
candidate.
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
SCHEMA_MANIFEST = "audio-sdk/speechbrain-sgmse-voicebank/caller-supplied/0.1"
TASK_ID = "SDK-SPEECHBRAIN-SGMSE-VOICEBANK"
TITLE = "SpeechBrain SGMSE-VoiceBank"
COMPONENT = "speechbrain-sgmse-voicebank"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "4c0f5464eeddff2204b527e8bc4ad09c41b2a657"
BRANCH = "swarm/SDK-SPEECHBRAIN-SGMSE-VOICEBANK"
REVIEWER = "reviewer-SPEECHBRAIN-SGMSE-VOICEBANK"
PROFILE = "enhancement"
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
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS

CENSUS_PATH = "research/noise_suppression_candidate_census.md"
MATRIX_PATH = "research/voice-enhancement-20261101/candidate_matrix.csv"
FINDINGS_PATH = "research/voice-enhancement-20261101/findings.md"
INVENTORY_REL = INVENTORY_PATH
VERIFICATION_REL = "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
SDK_README_REL = "audio-benchmark-platform/plan/audio-sdk/README.md"
SDK_CONTRACTS_REL = "audio-benchmark-platform/audio-sdk/CONTRACTS.md"

CENSUS_LINE = (
    "| **SpeechBrain SGMSE-VoiceBank** | Score-based diffusion; offline quality reference | "
    "Official Apache-2.0 model card and checkpoint; 16 kHz mono; reported PESQ 2.78, SI-SDR 17.8, STOI .957. | "
    "Include as offline/high-compute comparison; pin/hash, quantify sampling cost and CPU runtime. |"
)

EVIDENCE_ENTRIES: Tuple[Dict[str, Any], ...] = (
    {
        "path": CENSUS_PATH,
        "line": 41,
        "text": CENSUS_LINE,
        "class": "candidate_census_row",
        "note": "Source-bounded census row; provenance only, not a local result.",
    },
)

SOURCE_PINS: Dict[str, str] = {
    CENSUS_PATH: "525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a",
    MATRIX_PATH: "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    FINDINGS_PATH: "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c",
    INVENTORY_REL: "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    VERIFICATION_REL: "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    SDK_README_REL: "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    SDK_CONTRACTS_REL: "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
}

BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml": "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt": "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md": "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "README.md": "b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61",
    "REUSE.toml": "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py": "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}

BOARD_STABLE_SHA256 = "ed45cc640abbac44cea9af737a8bd890b199d55eca0053968e6629f1edf352ff"
INVENTORY_STABLE_SHA256 = "d8ffeccef2ce11150503adf472304d87fd85b8acce439562104f52e0675b69b1"
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

TASK_PREFIX = "docs/task-evidence/speechbrain-sgmse-voicebank/"
LOCAL_PIN_PATHS: Tuple[str, ...] = (
    ".gitignore",
    ".gitignore.license",
    "README.md",
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
SPDX_LICENSE = "SPDX-" + "License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SCOPE_BASE_REFS = ("origin/main", "main")

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_exact_speechbrain_sgmse_voicebank_assets_unpinned",
    "source_checkout": {
        "status": "unreviewed_not_staged",
        "revision": None,
        "license": None,
        "note": "No SpeechBrain/SGMSE source checkout is staged at a fixed reviewed probe path for this task package.",
    },
    "checkpoint": {
        "artifact": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present_locally": False,
        "note": "No exact SGMSE-VoiceBank checkpoint/config artifact identity, byte count or SHA-256 is staged or verified here.",
    },
    "runtime": {
        "status": "absent_unpinned",
        "lockfile": None,
        "sha256": None,
        "note": "No locked SpeechBrain/PyTorch/SGMSE runtime, sampler settings, device contract or offline loader is staged.",
    },
    "cohort_and_rights": {
        "status": "absent_unreviewed",
        "note": "No rights-qualified VoiceBank/DEMAND or task-matched paired cohort with pinned scorer and clean references is staged.",
    },
    "adapter": {
        "status": "absent_unregistered",
        "provider_id": None,
        "descriptor_id": None,
        "note": "No adapter, provider table, descriptor or registry entry exists for this candidate.",
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
    "checkpoint_loaded": False,
    "network_used": False,
    "provider_registered": False,
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No SpeechBrain, SGMSE, sgmse, PyTorch, lightning, torchaudio or Hugging Face Hub source, weights, config, runtime or corpus is imported, built, downloaded, loaded or executed.",
    "No real audio, paired clean/noisy corpus, SI-SDR, STOI, PESQ, DNSMOS, listening result or device timing is present.",
    "Integer sample/frame controls are synthetic structural fixtures and cannot qualify enhancement quality, preservation, latency or runtime behavior.",
    "Source-reported upstream PESQ/SI-SDR/STOI figures are provenance only and are not local or target-device measurements.",
    "No device timing, benchmark result, release claim, provider exposure or public default selection is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
)

GATES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "RG-01", "title": "exact_source_weights_and_runtime_identity", "status": "blocked", "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "The exact SpeechBrain/SGMSE source revision, checkpoint/config artifacts, byte counts, SHA-256, locked runtime and licenses must be pinned.",
        "reopen_condition": "Stage and review exact licensed source, checkpoint/config identity and a locked offline runtime.",
    },
    {
        "id": "RG-02", "title": "caller_asset_boundary_and_installed_v0_geometry", "status": "blocked", "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Caller asset identity, 16 kHz mono float32 160-sample geometry and fail-closed loading must be verified without loading assets.",
        "reopen_condition": "Pass a hash-matched caller manifest against the pinned geometry through a public boundary without loading or executing assets.",
    },
    {
        "id": "RG-03", "title": "license_rights_and_corpus_consent", "status": "blocked", "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Code, checkpoint, training data, paired corpus rights, consent and output-use terms require explicit independent review.",
        "reopen_condition": "Reviewed rights records clear code, weights, data, consent and product use.",
    },
    {
        "id": "RG-04", "title": "frozen_paired_cohort_and_controls", "status": "blocked", "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Freeze a rights-cleared paired noisy/clean cohort with identity/noisy control and task-matched baseline under exact scorer/config pins.",
        "reopen_condition": "Stage a rights-cleared frozen paired cohort with identity/noisy control and an established task-matched baseline.",
    },
    {
        "id": "RG-05", "title": "paired_si_sdr_stoi_and_preservation", "status": "blocked", "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Report paired SI-SDR and STOI, clean-speech preservation, peaks and invalid outputs on permitted clean references.",
        "reopen_condition": "Produce matched paired SI-SDR/STOI, preservation, peak and invalid-output outcomes on the exact runtime.",
    },
    {
        "id": "RG-06", "title": "unpaired_screen_or_listening_when_authorized", "status": "blocked", "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Unpaired speech requires a separately labeled predictive screen or authorized listening; no screen/listening claim is made here.",
        "reopen_condition": "Run a separately labeled predictive screen or authorized listening with explicit rights and scope labels.",
    },
    {
        "id": "RG-07", "title": "state_memory_and_measured_timing", "status": "blocked", "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Report alignment, state, memory and measured content/availability timing for the exact runtime and execution profile.",
        "reopen_condition": "Measure alignment, state, memory and content/availability timing on the exact runtime.",
    },
    {
        "id": "RG-08", "title": "opt_in_intake_and_release", "status": "blocked", "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Opt-in provider intake, independent exact-head review and explicit public default/release approval are required before any exposure.",
        "reopen_condition": "A separate versioned intake passes independent review with the default OFF and explicit approval.",
    },
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "XB-01", "title": "exact_sgmse_voicebank_assets_unpinned",
        "detail": "No exact SpeechBrain SGMSE-VoiceBank source revision, checkpoint/config artifact, byte count, SHA-256, or locked runtime is staged in this worktree for execution. The census reports source-reported upstream metrics only; no local reproduction exists.",
        "reopen": "Provide exact licensed source/checkpoint/config identity with immutable revisions, byte counts, SHA-256 and a locked offline runtime.",
    },
    {
        "id": "XB-02", "title": "rights_cleared_paired_cohort_and_scorers_absent",
        "detail": "No rights-qualified paired noisy/clean cohort, scorer pin, identity/noisy control run, or task-matched baseline is staged. VoiceBank/DEMAND and related rights/redistribution terms are not reviewed here.",
        "reopen": "Stage a rights-cleared frozen paired cohort with pinned scorers, identity/noisy control and task-matched baseline.",
    },
    {
        "id": "XB-03", "title": "enhancement_profile_unmet",
        "detail": "No paired SI-SDR/STOI, clean-speech preservation, peak/invalid-output audit, alignment, state/memory/timing, unpaired screen, or listening evidence exists for this exact runtime.",
        "reopen": "Complete the enhancement profile on the exact runtime with matched controls and labeled evidence classes.",
    },
    {
        "id": "XB-04", "title": "opt_in_intake_and_release_gates_unmet",
        "detail": "No provider registration, opt-in intake, independent exact-head review, device timing, benchmark, or release approval exists. Default remains OFF.",
        "reopen": "Pass separate opt-in intake and independent review at exact head with default OFF before any exposure.",
    },
)

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "checkpoint_path", "checkpoint_sha256",
    "checkpoint_byte_count", "checkpoint_revision", "source_revision",
    "runtime_lock_digest", "rights_digest", "sample_rate_hz", "channels",
    "frame_samples", "sample_format", "paired_cohort_digest", "scorer_digest",
)
CONFIGURATIONS: Tuple[str, ...] = ("speechbrain-sgmse-voicebank-caller-supplied",)
SYNTH_SEED = 20261126
SAMPLE_COUNT = 165


class ReferenceRejection(ValueError):
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
        relative = key.split(":", 1)[1] if key.startswith("source:") else key
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
    return SDK_ROOT / key


def readme_pin_rows() -> List[Tuple[str, str]]:
    text = (TASK_DIR / "README.md").read_text(encoding="utf-8")
    start = "<!-- digest-table: source -->"
    middle = "<!-- digest-table: boundary -->"
    end = "<!-- digest-table: end -->"
    if text.count(start) != 1 or text.count(middle) != 1 or text.count(end) != 2:
        raise ValueError("digest_table_marker_mismatch")
    rows: List[Tuple[str, str]] = []
    for block in (text.split(start, 1)[1].split(end, 1)[0],
                  text.split(middle, 1)[1].split(end, 1)[0]):
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) < 3 or lines[1] != "| --- | --- |":
            raise ValueError("digest_table_header_mismatch")
        for line in lines[2:]:
            if not line.startswith("| `") or not line.endswith("` |"):
                raise ValueError("digest_table_row_malformed")
            key, digest = [part.strip() for part in line.strip("|").split("|")]
            rows.append((key[1:-1], digest[1:-1]))
    return rows


def board_link() -> Dict[str, Any]:
    payload = strict_load(SOURCE_ROOT / TASK_BOARD)
    rows = [row for row in payload.get("tasks", [])
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
    rows = [row for row in payload.get("components", [])
            if isinstance(row, dict) and row.get("id") == COMPONENT]
    if len(rows) != 1:
        raise ValueError("inventory_row_not_unique")
    row = rows[0]
    stable = {field: row[field] for field in INVENTORY_COMPONENT_FIELDS}
    digest = object_digest(stable)
    if digest != INVENTORY_STABLE_SHA256:
        raise ValueError("unexpected_inventory_identity")
    evidence = row.get("evidence", [])
    if not evidence:
        raise ValueError("inventory_evidence_absent")
    first = evidence[0]
    return {
        "stable_fields": stable,
        "stable_sha256": digest,
        "evidence_path": first.get("path"),
        "evidence_line": first.get("line"),
        "evidence_record_name": first.get("record_name"),
        "evidence_status": row.get("evidence_status"),
        "full_inventory_hashed": False,
        "note": "Inventory row and census record are provenance only; never a result.",
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
        if not target.is_file() or sha256_file(target) != digest:
            raise ValueError("stale_source_pin:" + path)
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file() or sha256_file(target) != digest:
            raise ValueError("stale_boundary_pin:" + path)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ReferenceRejection("INVALID_MANIFEST", "manifest must be object")
    keys = set(manifest)
    expected = set(CALLER_MANIFEST_FIELDS)
    if keys != expected:
        if keys - expected:
            raise ReferenceRejection("UNKNOWN_FIELD", "extra manifest fields")
        raise ReferenceRejection("MISSING_FIELD", "missing manifest fields")
    if manifest["adapter"] != SCHEMA_MANIFEST:
        raise ReferenceRejection("UNKNOWN_ADAPTER", "unsupported adapter ID")
    if manifest["configuration_id"] not in CONFIGURATIONS:
        raise ReferenceRejection("UNKNOWN_CONFIGURATION", "unsupported configuration")
    if (not isinstance(manifest["source_revision"], str)
            or re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"]) is None):
        raise ReferenceRejection("BAD_SOURCE_REVISION", "source revision malformed")
    if (manifest["sample_rate_hz"] != SAMPLE_RATE_HZ or manifest["channels"] != CHANNELS
            or manifest["frame_samples"] != FRAME_SAMPLES or manifest["sample_format"] != SAMPLE_FORMAT):
        raise ReferenceRejection("FORMAT_MISMATCH", "installed v0 format mismatch")
    if not isinstance(manifest["checkpoint_path"], str) or not Path(manifest["checkpoint_path"]).is_absolute():
        raise ReferenceRejection("RELATIVE_CHECKPOINT", "checkpoint path must be absolute")
    if not _is_sha256(manifest["checkpoint_sha256"]):
        raise ReferenceRejection("BAD_CHECKPOINT_DIGEST", "checkpoint SHA-256 malformed")
    if (not isinstance(manifest["checkpoint_byte_count"], int) or isinstance(manifest["checkpoint_byte_count"], bool)
            or manifest["checkpoint_byte_count"] <= 0):
        raise ReferenceRejection("BAD_BYTE_COUNT", "checkpoint byte count malformed")
    if not isinstance(manifest["checkpoint_revision"], str) or not manifest["checkpoint_revision"].strip():
        raise ReferenceRejection("MISSING_CHECKPOINT_REVISION", "revision required")
    for field, code in (
        ("runtime_lock_digest", "BAD_RUNTIME_DIGEST"),
        ("rights_digest", "BAD_RIGHTS_DIGEST"),
        ("paired_cohort_digest", "BAD_COHORT_DIGEST"),
        ("scorer_digest", "BAD_SCORER_DIGEST"),
    ):
        if not _is_sha256(manifest[field]):
            raise ReferenceRejection(code, field + " malformed")
    checkpoint = Path(manifest["checkpoint_path"])
    if not checkpoint.is_file():
        raise ReferenceRejection("ASSET_ABSENT", "declared checkpoint is absent")
    if sha256_file(checkpoint) != manifest["checkpoint_sha256"]:
        raise ReferenceRejection("ASSET_HASH_MISMATCH", "checkpoint SHA-256 mismatch")
    if checkpoint.stat().st_size != manifest["checkpoint_byte_count"]:
        raise ReferenceRejection("ASSET_SIZE_MISMATCH", "checkpoint byte count mismatch")
    raise ReferenceRejection(
        "SGMSE_VOICEBANK_ASSET_IDENTITY_UNPINNED",
        "hash-matched caller asset is still not an exact licensed SGMSE-VoiceBank checkpoint/config/runtime",
    )


def valid_manifest(checkpoint_path: str = "/absent/sgmse-voicebank.ckpt") -> Dict[str, Any]:
    return {
        "adapter": SCHEMA_MANIFEST,
        "configuration_id": CONFIGURATIONS[0],
        "checkpoint_path": checkpoint_path,
        "checkpoint_sha256": "0" * 64,
        "checkpoint_byte_count": 1,
        "checkpoint_revision": "caller-declared-revision",
        "source_revision": "0" * 40,
        "runtime_lock_digest": "0" * 64,
        "rights_digest": "0" * 64,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT,
        "paired_cohort_digest": "0" * 64,
        "scorer_digest": "0" * 64,
    }


def validate_reset(new_epoch: Any, first_sample: Any, current_epoch: int) -> Dict[str, Any]:
    if not isinstance(new_epoch, int) or isinstance(new_epoch, bool) or new_epoch < 0:
        raise ReferenceRejection("BAD_EPOCH", "invalid epoch")
    if not isinstance(first_sample, int) or isinstance(first_sample, bool) or first_sample < 0:
        raise ReferenceRejection("BAD_POSITION", "invalid first input sample")
    if new_epoch <= current_epoch:
        raise ReferenceRejection("EPOCH_NOT_INCREASING", "epoch must increase")
    return {"accepted": True, "epoch": new_epoch, "first_input_sample": first_sample}


def frame_windows(count: int = SAMPLE_COUNT) -> List[List[int]]:
    return [list(range(index, min(index + FRAME_SAMPLES, count)))
            for index in range(0, count, FRAME_SAMPLES)]


def synthetic_enhancement_fixture() -> Dict[str, Any]:
    windows = frame_windows()
    samples = [index for window in windows for index in window]
    canonical_samples = list(range(SAMPLE_COUNT))
    swapped = list(canonical_samples)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    inserted = canonical_samples + [SAMPLE_COUNT]
    truncated = canonical_samples[:-1]
    return {
        "label": "synthetic integer sample/frame controls; not audio, not enhancement output, not SI-SDR/STOI evidence",
        "seed": SYNTH_SEED,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "sample_ns": SAMPLE_NS,
        "frame_ns": FRAME_NS,
        "sample_count": SAMPLE_COUNT,
        "canonical_samples_sha256": object_digest(canonical_samples),
        "frame_count": len(windows),
        "final_partial_frame_samples": SAMPLE_COUNT % FRAME_SAMPLES,
        "final_frame_zero_padding": FRAME_SAMPLES - (SAMPLE_COUNT % FRAME_SAMPLES),
        "half_open_intervals": [
            {"frame": index, "start": index * FRAME_SAMPLES, "end": min((index + 1) * FRAME_SAMPLES, SAMPLE_COUNT)}
            for index in range(len(windows))
        ],
        "identity_control": {
            "source_interval_union_exact": samples == canonical_samples,
            "reassembled_samples_sha256": object_digest(samples),
            "qualifies_candidate": False,
        },
        "content_controls": [
            {"id": "exact", "samples_sha256": object_digest(canonical_samples), "preserved": True, "qualifies_candidate": False},
            {"id": "swap", "samples_sha256": object_digest(swapped), "preserved": swapped == canonical_samples, "qualifies_candidate": False},
            {"id": "insert", "samples_sha256": object_digest(inserted), "preserved": inserted == canonical_samples, "qualifies_candidate": False},
            {"id": "truncate", "samples_sha256": object_digest(truncated), "preserved": truncated == canonical_samples, "qualifies_candidate": False},
        ],
        "enhancement_controls": [
            {"id": "identity_noisy_control", "status": "synthetic_structural_only", "qualifies_candidate": False},
            {"id": "paired_si_sdr_stoi", "status": "blocked_no_clean_reference_or_runtime", "qualifies_candidate": False},
            {"id": "clean_speech_preservation", "status": "blocked_no_audio_or_runtime", "qualifies_candidate": False},
            {"id": "peak_and_invalid_outputs", "status": "blocked_no_runtime_outputs", "qualifies_candidate": False},
            {"id": "state_memory_timing", "status": "blocked_no_runtime", "qualifies_candidate": False},
        ],
        "coverage_controls": [
            {"id": "quiet_speech", "status": "blocked_no_corpus"},
            {"id": "active_speech", "status": "blocked_no_corpus"},
            {"id": "idle_noise", "status": "blocked_no_corpus"},
            {"id": "known_positives_negatives", "status": "blocked_no_corpus"},
            {"id": "unpaired_predictive_screen_or_listening", "status": "blocked_no_rights_or_runtime"},
        ],
        "note": "Only exact integer frame geometry is exercised. No enhancement quality, preservation, latency or runtime measurement is produced.",
    }


def alignment_probe() -> Dict[str, Any]:
    return {
        "label": "synthetic half-open interval mapping only; no measured enhancement timing",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "sample_ns": SAMPLE_NS,
        "frame_ns": FRAME_NS,
        "source_intervals": [[index * FRAME_SAMPLES, min((index + 1) * FRAME_SAMPLES, SAMPLE_COUNT)] for index in range(len(frame_windows()))],
        "modelled_content_offset_samples": 0,
        "first_output_ns": None,
        "tail_output_ns": None,
        "measured": False,
        "shift_probes": [
            {"shift_samples": 0, "accepted": True},
            {"shift_samples": -FRAME_SAMPLES, "accepted": False},
            {"shift_samples": FRAME_SAMPLES, "accepted": False},
        ],
        "content_delay": "blocked; no runtime",
        "availability_delay": "blocked; no runtime",
    }


def state_probe() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    checks = (
        ("fresh_epoch_2", (2, 0, 1), True),
        ("equal_epoch", (1, 0, 1), False),
        ("lower_epoch", (0, 0, 1), False),
        ("negative_epoch", (-1, 0, 1), False),
        ("negative_position", (2, -1, 1), False),
        ("bool_epoch", (True, 0, 1), False),
    )
    for name, args, expected in checks:
        try:
            validate_reset(*args)
            accepted = True
        except ReferenceRejection:
            accepted = False
        cases.append({"id": name, "accepted": accepted, "expected": expected})
    joined = [index for window in frame_windows() for index in window]
    return {
        "cases": cases,
        "matches_expectation": all(item["accepted"] == item["expected"] for item in cases),
        "state_owned": False,
        "chunk_invariance_digest": object_digest(joined),
        "chunk_invariance_exact": joined == list(range(SAMPLE_COUNT)),
        "note": "Model-free fixture state only; no provider, model or runtime state exists.",
    }


def adverse_cases() -> Dict[str, Any]:
    base = valid_manifest()
    cases: List[Dict[str, Any]] = []

    def add(case_id: str, mutate: Any, code: str) -> None:
        manifest = dict(base)
        mutate(manifest)
        try:
            validate_caller_manifest(manifest)
            observed = "UNEXPECTED_ACCEPT"
        except ReferenceRejection as error:
            observed = error.code
        cases.append({"id": case_id, "expected": code, "observed": observed, "accepted": observed == "UNEXPECTED_ACCEPT"})

    add("missing_field", lambda m: m.pop("frame_samples"), "MISSING_FIELD")
    add("unknown_field", lambda m: m.update(extra=1), "UNKNOWN_FIELD")
    add("wrong_adapter", lambda m: m.update(adapter="other"), "UNKNOWN_ADAPTER")
    add("wrong_configuration", lambda m: m.update(configuration_id="raw"), "UNKNOWN_CONFIGURATION")
    add("bad_source_revision", lambda m: m.update(source_revision="deadbeef"), "BAD_SOURCE_REVISION")
    add("wrong_rate", lambda m: m.update(sample_rate_hz=48000), "FORMAT_MISMATCH")
    add("wrong_channels", lambda m: m.update(channels=2), "FORMAT_MISMATCH")
    add("wrong_frame", lambda m: m.update(frame_samples=320), "FORMAT_MISMATCH")
    add("wrong_format", lambda m: m.update(sample_format="int16"), "FORMAT_MISMATCH")
    add("relative_checkpoint", lambda m: m.update(checkpoint_path="last.ckpt"), "RELATIVE_CHECKPOINT")
    add("absent_checkpoint", lambda m: None, "ASSET_ABSENT")
    add("bad_checkpoint_digest", lambda m: m.update(checkpoint_sha256="abc"), "BAD_CHECKPOINT_DIGEST")
    add("bad_byte_count", lambda m: m.update(checkpoint_byte_count=True), "BAD_BYTE_COUNT")
    add("bad_runtime_digest", lambda m: m.update(runtime_lock_digest="xyz"), "BAD_RUNTIME_DIGEST")
    add("bad_rights_digest", lambda m: m.update(rights_digest="xyz"), "BAD_RIGHTS_DIGEST")
    add("bad_cohort_digest", lambda m: m.update(paired_cohort_digest="xyz"), "BAD_COHORT_DIGEST")
    add("bad_scorer_digest", lambda m: m.update(scorer_digest="xyz"), "BAD_SCORER_DIGEST")
    try:
        validate_caller_manifest([])
        observed = "UNEXPECTED_ACCEPT"
    except ReferenceRejection as error:
        observed = error.code
    cases.append({"id": "manifest_not_object", "expected": "INVALID_MANIFEST", "observed": observed, "accepted": observed == "UNEXPECTED_ACCEPT"})
    good = sum(1 for item in cases if item["accepted"])
    return {"case_count": len(cases), "accepted_count": good, "all_rejected": good == 0, "cases": cases, "metrics": None, "note": "All caller manifests fail closed before any asset load or execution."}


def invalid_json_cases() -> Dict[str, Any]:
    texts = {
        "duplicate_key": '{"a":1,"a":2}',
        "nan_constant": '{"a":NaN}',
        "infinity_constant": '{"a":Infinity}',
        "negative_infinity_constant": '{"a":-Infinity}',
        "trailing_data": '{"a":1} extra',
        "invalid_syntax": '{"a":}',
        "empty_text": "",
    }
    cases: List[Dict[str, Any]] = []
    for name, text in texts.items():
        try:
            strict_loads(text)
            observed = "UNEXPECTED_ACCEPT"
        except ValueError:
            observed = "INVALID_JSON"
        cases.append({"id": name, "observed": observed, "accepted": observed == "UNEXPECTED_ACCEPT"})
    good = sum(1 for item in cases if item["accepted"])
    return {"case_count": len(cases), "accepted_count": good, "all_rejected": good == 0, "cases": cases, "metrics": None}


def invalid_pin_cases() -> Dict[str, Any]:
    texts = {
        "duplicate_key": "a" * 64 + "  source:duplicate\n" + "a" * 64 + "  source:duplicate\n",
        "short_digest": "abc  source:short\n",
        "missing_separator": "a" * 64 + " source:missing\n",
        "absolute_path": "a" * 64 + "  /absolute/path\n",
        "traversal": "a" * 64 + "  source:../escape\n",
    }
    cases: List[Dict[str, Any]] = []
    for name, text in texts.items():
        try:
            parse_pin_lines(text)
            observed = "UNEXPECTED_ACCEPT"
        except ValueError:
            observed = "INVALID_PIN"
        cases.append({"id": name, "observed": observed, "accepted": observed == "UNEXPECTED_ACCEPT"})
    good = sum(1 for item in cases if item["accepted"])
    return {"case_count": len(cases), "accepted_count": good, "all_rejected": good == 0, "cases": cases}


WORKSPACE_PROBE_PATHS: Tuple[str, ...] = (
    "data/checkouts/sgmse",
    "data/checkouts/sgmse-speechbrain",
    "data/models/speechbrain-sgmse-voicebank",
    "data/models/sgmse-voicebank",
    "data/envs/speechbrain-sgmse",
    "data/licenses/speechbrain-sgmse-voicebank",
    "data/rights/speechbrain-sgmse-voicebank.json",
    "adapters/speechbrain-sgmse-voicebank",
    "docs/task-evidence/speechbrain-sgmse-voicebank/checkpoint",
    "docs/task-evidence/speechbrain-sgmse-voicebank/runtime",
)
HOME_PROBE_PATHS: Tuple[str, ...] = (
    ".cache/huggingface/hub/models--speechbrain--sgmse-voicebank",
    ".cache/speechbrain",
)


def absent_artifact_probe() -> Dict[str, Any]:
    workspace = [{"path": path, "present": (SOURCE_ROOT / path).exists()} for path in WORKSPACE_PROBE_PATHS]
    worktree = [{"path": path, "present": (SDK_ROOT / path).exists()} for path in WORKSPACE_PROBE_PATHS]
    home = Path.home()
    home_rows = [{"path": "~/" + path, "present": (home / path).exists()} for path in HOME_PROBE_PATHS]
    present = [row["path"] for row in workspace + worktree + home_rows if row["present"]]
    return {
        "workspace_probes": workspace,
        "sdk_worktree_probes": worktree,
        "home_cache_probes": home_rows,
        "workspace_probe_count": len(workspace),
        "sdk_worktree_probe_count": len(worktree),
        "home_cache_probe_count": len(home_rows),
        "present": bool(present),
        "present_paths": present,
        "recursive_workspace_walk": False,
        "note": "Bounded read-only path probes; no download, import, load or audio read was attempted.",
    }


def source_reported() -> Dict[str, Any]:
    return {
        "entries": evidence_entries(),
        "census_status": "considered",
        "upstream_reported_metrics": {"pesq": 2.78, "si_sdr": 17.8, "stoi": 0.957, "scope": "upstream VoiceBank+DEMAND as reported in census; not local"},
        "separation": "Pinned census/inventory records are provenance only. Upstream reported metrics are source-reported and not local outputs or measurements.",
        "qualifies": False,
        "listening_performed_here": False,
        "inference_performed_here": False,
    }


def enhancement_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "identity_noisy_control_and_task_matched_baseline": {"status": "blocked", "evidence": "No exact runtime, paired cohort, identity/noisy control run, or task-matched baseline staged."},
            "paired_si_sdr_stoi_where_permitted": {"status": "blocked", "evidence": "No rights-cleared paired clean references, scorer pin, or runtime output exists."},
            "clean_speech_preservation_peaks_invalid_outputs": {"status": "blocked", "evidence": "No runtime output, peak audit or invalid-output audit exists."},
            "unpaired_predictive_screen_or_authorized_listening": {"status": "blocked", "evidence": "No unpaired screen, listening authorization, or result exists."},
            "alignment_state_memory_measured_timing": {"status": "blocked", "evidence": "No runtime alignment, state, memory or content/availability timing exists."},
            "synthetic_interval_controls_only": {"status": "synthetic_structural_only", "evidence": "Exact half-open 160-sample integer intervals only; no audio or enhancement result."},
        },
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    fixture = synthetic_enhancement_fixture()
    align = alignment_probe()
    state = state_probe()
    manifest_adverse = adverse_cases()
    json_adverse = invalid_json_cases()
    pin_adverse = invalid_pin_cases()
    probe = absent_artifact_probe()
    report: Dict[str, Any] = {
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
            "family_configurations": list(CONFIGURATIONS),
            "configuration_pinned": False,
            "format": dict(BOUNDARY["format"]),
            "loaded": False,
            "executed": False,
            "note": "Metadata-only reference. A hash-matched caller asset still fails as SGMSE_VOICEBANK_ASSET_IDENTITY_UNPINNED; no weights or runtime is promoted.",
        },
        "asset_resolution": probe,
        "synthetic_enhancement_fixture": fixture,
        "enhancement_profile": enhancement_profile(),
        "availability": {
            "status": "modelled_not_measured",
            "clock": "fixture-monotonic-not-device",
            "device_timing": False,
            "enhancement_result": False,
            "content_delay_claim": False,
            "availability_delay_claim": False,
        },
        "alignment": align,
        "state": state,
        "controls": {
            "identity": {"status": "bit_exact_synthetic_interval_only", "qualifies": False},
            "content_mismatch": {"status": "integer_interval_control_only", "qualifies": False},
            "independent_instances": {"status": "model_free", "qualifies": False},
        },
        "adverse": {
            "caller_manifest": manifest_adverse,
            "invalid_json": json_adverse,
            "invalid_pins": pin_adverse,
            "all_rejected": manifest_adverse["all_rejected"] and json_adverse["all_rejected"] and pin_adverse["all_rejected"],
            "metrics": None,
        },
        "comparison": {
            "status": "blocked_no_exact_assets_runtime_or_cohort",
            "identity_control": "synthetic integer interval only",
            "task_matched_baseline": "blocked",
            "qualifies_candidate": False,
        },
        "source_reported": source_reported(),
        "inventory_link": inventory_link(),
        "model_provenance": {
            "source_revision": None,
            "source_license": None,
            "checkpoint": dict(ASSET_LEDGER["checkpoint"]),
            "runtime": dict(ASSET_LEDGER["runtime"]),
            "identity_pinned": False,
        },
        "licensing_analysis": {
            "source_terms": "unreviewed; no staged source checkout",
            "checkpoint_terms": "unavailable and unreviewed",
            "training_data_terms": "unreviewed",
            "corpus_rights": "unreviewed",
            "output_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact licensed SpeechBrain SGMSE-VoiceBank source, checkpoint/config, bytes, SHA-256 and locked runtime",
            "rights-cleared paired noisy/clean cohort with pinned scorers and controls",
            "matched paired SI-SDR/STOI, preservation, peak and invalid-output outcomes on exact runtime",
            "alignment, state, memory and measured content/availability timing on exact runtime",
            "opt-in provider intake and independent release review with default OFF",
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
        "board_link": board_link(),
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "fresh_builds": 3,
            "comparison": "exact SHA-256 over bytes; no tolerance",
        },
    }
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines = [
        "# SHA-256 pins for SDK-SPEECHBRAIN-SGMSE-VOICEBANK.",
        "# source: paths are workspace-relative; other paths are SDK-worktree-relative.",
        "# Local task paths are SDK-worktree-relative. Missing assets are ledger entries, not file pins.",
        "# The mutable full plan/swarm/TASKS.json is never pinned; only stable row identity is gated.",
    ]
    for path in sorted(SOURCE_PINS):
        lines.append(SOURCE_PINS[path] + "  source:" + path)
    for path in sorted(BOUNDARY_PINS):
        lines.append(BOUNDARY_PINS[path] + "  " + path)
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        lines.append(sha256_bytes(payload) + "  " + TASK_PREFIX + name)
    return ("\n".join(lines) + "\n").encode("utf-8")


def contract_bytes(report_payload: bytes, sidecar_payload: bytes,
                   sources_payload: bytes, report: Dict[str, Any]) -> bytes:
    artifact_pins: Dict[str, str] = {}
    for name in LOCAL_PIN_PATHS:
        if name == "report.json":
            payload = report_payload
        elif name == "report.json.sha256":
            payload = sidecar_payload
        else:
            payload = (TASK_DIR / name).read_bytes()
        artifact_pins[TASK_PREFIX + name] = sha256_bytes(payload)
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
            "No SpeechBrain/SGMSE source, weights, config, audio, cohort or runtime artifact is bundled.",
            "Caller manifests are validated as metadata and never loaded or executed.",
            "Synthetic integer intervals are labelled and cannot qualify the candidate.",
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


def scope_base(worktree: Path, refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
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
