# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for the SimulStreaming feasibility row.

This package is feasibility evidence only. It models a caller-supplied-asset
boundary with synthetic, integer-only structural controls. It does not
implement, download, load, import or execute SimulStreaming, Whisper-Streaming,
Whisper, NeMo, sherpa-onnx or any other ASR runtime. No checkpoint, real audio,
WER/latency result, listening result, device timing, benchmark result or release
claim is included, and no result here qualifies the candidate.
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
SCHEMA_MANIFEST = "audio-sdk/simulstreaming/caller-supplied/0.1"
TASK_ID = "SDK-SIMULSTREAMING"
TITLE = "SimulStreaming"
COMPONENT = "simulstreaming"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "f93d25f3d455a4278030d1bf0a3338dc6f8b95fe"
BRANCH = "swarm/SDK-SIMULSTREAMING"
REVIEWER = "reviewer-SIMULSTREAMING"
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
FRAME_NS = FRAME_SAMPLES * SAMPLE_NS

MATRIX_PATH = "research/voice-enhancement-20261101/candidate_matrix.csv"
TRIALS_PATH = "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md"
SEGMENTATION_PATH = "research/voice-enhancement-20261101/agent-segmentation/REPORT.md"
REAUDIT_PATH = "research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md"
MATRIX_AUDIT_PATH = "research/voice-enhancement-20261101/agent-matrix-audit/REPORT.md"
FINDINGS_PATH = "research/voice-enhancement-20261101/findings.md"

MATRIX_LINE = (
    "Disfluency and TSM,Whisper-Streaming / SimulStreaming,unavailable/blocked,"
    '"No local ASR checkpoint, streaming runtime or adapter; no local WER/latency result.",'
    "Reference transcript / identity,"
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md; "
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md"
)
TRIALS_LINE = (
    "| Whisper-Streaming / SimulStreaming | No local ASR checkpoint or streaming "
    "adapter; `whisper`, `faster_whisper`, NeMo and sherpa-onnx were absent in the "
    "checked runtime. The AMI corpus includes transcript/alignment material, but "
    "ASR model weights and an isolated source/runtime are absent. No model was "
    "substituted. |"
)
SEGMENTATION_LINE = (
    "| SimulStreaming (additional current Whisper streaming candidate) | "
    "researched but not run | No project adapter or local run. | Official UFAL repo "
    "describes simultaneous/low-latency processing of Whisper and text models "
    "originally designed for offline use. Need pinned version, model "
    "checkpoint/license, language coverage, device, buffer/lookahead and latency "
    "measurement; not audio enhancement. [Official repo]"
    "(https://github.com/ufal/SimulStreaming). | This report. |"
)
REAUDIT_LINE = (
    "- **ASR/disfluency:** Whisper-Streaming/SimulStreaming and Streaming "
    "Conformer-TED/FastConformer still lack exact weights and streaming adapters. "
    "Filler/stutter text cleanup additionally lacks a measured ASR transcript "
    "stream and a semantic/disfluency reference task."
)
MATRIX_AUDIT_LINE = (
    "- **Disfluency and TSM:** Whisper-Streaming/SimulStreaming, streaming "
    "Conformer-TED/FastConformer, text or pattern cleanup, filler/stutter waveform "
    "gates, breath/click gates, neural WSOLA, phase vocoder with neural transient "
    "preservation, other speech TSM methods, and a separate FFmpeg atempo control "
    "appear."
)

EVIDENCE_ENTRIES: Tuple[Dict[str, Any], ...] = (
    {
        "path": MATRIX_PATH,
        "line": 35,
        "text": MATRIX_LINE,
        "class": "candidate_census_row",
        "note": "Structured rate/TSM census row 34; unavailable/blocked, not a local result.",
    },
    {
        "path": TRIALS_PATH,
        "line": 11,
        "text": TRIALS_LINE,
        "class": "asr_trial_audit_row",
        "note": "Primary-source audit: no local ASR checkpoint, runtime or adapter; no model substituted.",
    },
    {
        "path": SEGMENTATION_PATH,
        "line": 26,
        "text": SEGMENTATION_LINE,
        "class": "streaming_asr_candidate_row",
        "note": "SimulStreaming researched but not run; version, weights, license and latency unpinned.",
    },
    {
        "path": REAUDIT_PATH,
        "line": 19,
        "text": REAUDIT_LINE,
        "class": "blocked_reaudit_row",
        "note": "Reaudit confirms exact weights and streaming adapters are still absent.",
    },
    {
        "path": MATRIX_AUDIT_PATH,
        "line": 23,
        "text": MATRIX_AUDIT_LINE,
        "class": "matrix_audit_row",
        "note": "Matrix audit lists the candidate without a local implementation or result.",
    },
)

SOURCE_PINS: Dict[str, str] = {
    MATRIX_PATH:
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    TRIALS_PATH:
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    SEGMENTATION_PATH:
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    REAUDIT_PATH:
        "5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14",
    MATRIX_AUDIT_PATH:
        "865b0031d357b7009c2876f997ca188440451fb65d5cef3561e9848f34eaf1d0",
    FINDINGS_PATH:
        "78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c",
    INVENTORY_PATH:
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/audio-sdk/CONTRACTS.md":
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
    "docs/task-evidence/survey-det-02/README.md":
        "40c05936132ed4add0d1a97a9139f42c170711130c447f18d36b11c7669221b1",
    "docs/task-evidence/survey-rec-01/README.md":
        "01e54b306313f13f97e1c9f4a08f5ebd98cbf570617644a028ae2bca3d4f4acb",
    "docs/task-evidence/fastconformer-streaming-asr/README.md":
        "12b8a50552a9dbb39fbed6d52bf543a7c54a53165101cf8d7f0aaa3abd5edebc",
    "docs/task-evidence/seed-tts/README.md":
        "5c9e4d3ec5e7940a8aa164cf6957aaebd2fa7be79d7a7b94afd92cb05bd52d83",
}

BOARD_STABLE_SHA256 = (
    "f1320dc5de33e8c529ccde6b8625beb1c3d39097c68ca14b26308aa17c4fe28a"
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

TASK_PREFIX = "docs/task-evidence/simulstreaming/"
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
    "status": "absent_exact_asr_weights_streaming_runtime_and_adapter_unpinned",
    "source_checkout": {
        "status": "absent",
        "revision": None,
        "license": None,
        "note": "No SimulStreaming or Whisper-Streaming source checkout is staged at any fixed probe path.",
    },
    "checkpoint": {
        "artifact": None,
        "revision": None,
        "byte_count": None,
        "sha256": None,
        "present_locally": False,
        "note": (
            "The pinned census and audits do not name a downloadable licensed ASR "
            "checkpoint, immutable revision, byte count or SHA-256."
        ),
    },
    "runtime": {
        "status": "absent_unpinned",
        "lockfile": None,
        "sha256": None,
        "note": (
            "No locked Python/GPU runtime, tokenizer, backend, offline loader, "
            "buffer/lookahead policy or partial/final commit geometry is staged."
        ),
    },
    "cohort_and_rights": {
        "status": "absent_unreviewed",
        "note": (
            "No rights-qualified conversational corpus with utterance and turn "
            "boundaries, reference transcripts, pinned scorer, held-out split or "
            "independent label review is staged."
        ),
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
    "No SimulStreaming, Whisper-Streaming, Whisper, NeMo or sherpa-onnx source, weights, tokenizer, backend or runtime is imported, built, downloaded, loaded or executed.",
    "No ASR transcript, word timestamp, WER, endpoint delay, first-output measurement, listening result or real audio is present.",
    "Integer sample/frame controls are synthetic structural fixtures and cannot qualify duration, rate, pitch, transient, speech-preservation or endpoint evidence.",
    "Source-reported 3.3 s latency and upstream repository descriptions are provenance only and are not local or target-device measurements.",
    "No device timing, benchmark result, release claim, provider exposure or public default selection is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
)

GATES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "RG-01",
        "title": "exact_source_weights_and_streaming_runtime_identity",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "The exact SimulStreaming source revision, weights, byte count, SHA-256, locked backend/runtime and model license must be pinned.",
        "reopen_condition": "Stage and review an exact licensed ASR artifact identity and locked offline streaming runtime.",
    },
    {
        "id": "RG-02",
        "title": "caller_asset_boundary_and_installed_v0_geometry",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Caller asset identity, configuration, 16 kHz mono float32 160-sample geometry, transcript contract and finalization must be verified without loading an asset.",
        "reopen_condition": "Pass a hash-matched caller manifest against the exact pinned geometry and reproduce an exact run through the public boundary.",
    },
    {
        "id": "RG-03",
        "title": "license_rights_and_cohort_consent",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Code, checkpoint, training data, conversational corpus consent, transcript availability and output use require explicit independent review.",
        "reopen_condition": "Reviewed rights records clear code, weights, data, consent, availability and product use.",
    },
    {
        "id": "RG-04",
        "title": "frozen_permitted_cohort_and_endpoint_labels",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Freeze a speaker/session-disjoint conversational cohort with utterance and turn boundaries, reference transcripts, unknown regions and independent label review.",
        "reopen_condition": "Stage a rights-cleared frozen cohort with pinned splits and independently reviewed endpoint labels.",
    },
    {
        "id": "RG-05",
        "title": "source_output_mapping_duration_pitch_and_transients",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Measure source/output mapping, duration, pitch, transient audibility and playback buffering at 1x and rate changes, including unfamiliar speech, music, silence, rebuffer, drift and the final partial window.",
        "reopen_condition": "Produce matched rate-profile controls with exact sample intervals on the pinned runtime.",
    },
    {
        "id": "RG-06",
        "title": "matched_wer_latency_and_holdout_outcomes",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Report stratified WER/CER, cutoff and end-of-turn delay with identity, fixed-timer, VAD-only, oracle-alignment and alternative-model controls on the pinned cohort.",
        "reopen_condition": "Collect matched, uncertainty-labelled WER and latency outcomes with independent controls.",
    },
    {
        "id": "RG-07",
        "title": "paced_streaming_state_max_wait_and_device_timing",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Verify causal partial/final commits, maximum-wait fallback, overlap/barge-in, dropped/stale chunks, reset state and measured availability on the target device.",
        "reopen_condition": "Measure paced streaming state, dropped/stale behavior and target-device availability on the exact runtime.",
    },
    {
        "id": "RG-08",
        "title": "opt_in_intake_and_release",
        "status": "blocked",
        "qualifies": False,
        "linked_row": TASK_ID,
        "statement": "Opt-in provider intake, independent exact-head review and explicit public default/release approval are required before any exposure.",
        "reopen_condition": "A separate versioned intake passes independent review with the default OFF and explicit approval.",
    },
)

EXACT_BLOCKERS: Tuple[Dict[str, str], ...] = (
    {
        "id": "XB-01",
        "title": "exact_asr_weights_and_streaming_runtime_absent",
        "detail": (
            "The pinned census marks Whisper-Streaming/SimulStreaming "
            "unavailable/blocked: no local ASR checkpoint, streaming runtime or "
            "adapter and no local WER/latency result. The trials audit found "
            "whisper, faster_whisper, NeMo and sherpa-onnx absent; the reaudit "
            "found no exact weights or streaming adapters. No exact checkpoint "
            "path, revision, byte count or SHA-256 exists to pin."
        ),
        "reopen": (
            "Provide the exact licensed ASR artifact with immutable revision, byte "
            "count and SHA-256, plus its reviewed source and redistribution terms."
        ),
    },
    {
        "id": "XB-02",
        "title": "runtime_task_contract_and_v0_output_geometry_unpinned",
        "detail": (
            "No locked backend, tokenizer, model, language coverage, "
            "buffer/lookahead policy, partial/final commit, chunking, maximum-wait "
            "or drain geometry is staged. Installed v0 accepts only 16 kHz mono "
            "float32 160-sample audio frames and has no transcript endpoint; a "
            "streaming ASR result cannot be substituted from frame counts."
        ),
        "reopen": (
            "Pin the exact runtime, transcript output contract and task geometry, "
            "then reproduce exact outputs with a hash-matched caller-supplied asset."
        ),
    },
    {
        "id": "XB-03",
        "title": "rights_cleared_turn_labelled_cohort_and_scorers_absent",
        "detail": (
            "No rights-qualified conversational corpus with utterance and turn "
            "boundaries, explicit unknown regions, reference transcripts, "
            "speaker/session-disjoint splits, independent label review or pinned "
            "WER/latency scorer is staged."
        ),
        "reopen": (
            "Stage a rights-cleared, turn-labelled frozen cohort with pinned "
            "scorers and independent controls."
        ),
    },
    {
        "id": "XB-04",
        "title": "rate_streaming_profile_and_release_gates_unmet",
        "detail": (
            "No local ASR output, WER/CER, cutoff or end-of-turn delay, "
            "source/output mapping, duration/pitch/transient, playback buffering, "
            "paced causal state, dropped/stale chunk, device timing, benchmark, "
            "opt-in intake or independent release review exists. The upstream "
            "3.3 s latency is source-reported, not local evidence."
        ),
        "reopen": (
            "Complete the rate and streaming profile on the exact runtime and pass "
            "independent opt-in review with the default OFF."
        ),
    },
)

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "checkpoint_path", "checkpoint_sha256",
    "checkpoint_byte_count", "checkpoint_revision", "source_revision",
    "runtime_lock_digest", "rights_digest", "sample_rate_hz", "channels",
    "frame_samples", "sample_format", "transcript_cohort_digest",
    "endpoint_label_digest",
)
CONFIGURATIONS: Tuple[str, ...] = (
    "whisper-streaming-local-agreement",
    "simulstreaming-alignment-based",
)
SYNTH_SEED = 20261126
SAMPLE_COUNT = 165


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
        if not line.strip():
            continue
        if line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError("bad_pin_line:" + str(number))
        digest, key = match.group(1), match.group(2)
        if key in seen:
            raise ValueError("duplicate_pin_key:" + key)
        if key.startswith("source:"):
            relative = key.split(":", 1)[1]
        elif key.startswith("sdk:"):
            relative = key.split(":", 1)[1]
        else:
            relative = key
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
            key, digest = [part.strip() for part in line.strip("|").split("|")]
            if not (key.startswith("`") and key.endswith("`")):
                raise ValueError("digest_table_key_malformed")
            if not (digest.startswith("`") and digest.endswith("`")):
                raise ValueError("digest_table_digest_malformed")
            rows.append((key[1:-1], digest[1:-1]))
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
    expected = {
        "id": COMPONENT,
        "name": TITLE,
        "evidence_status": "blocked",
        "repository": REPOSITORY,
        "verification_profile": PROFILE,
        "task": TASK_ID,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise ValueError("inventory_field_mismatch:" + key)
    evidence = row.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("inventory_evidence_absent")
    first = evidence[0]
    for key, value in (
        ("path", MATRIX_PATH),
        ("record", 34),
        ("record_name", "Whisper-Streaming / SimulStreaming"),
        ("record_status", "unavailable/blocked"),
        ("finding", "No local ASR checkpoint, streaming runtime or adapter; no local WER/latency result."),
    ):
        if first.get(key) != value:
            raise ValueError("inventory_evidence_mismatch:" + key)
    stable = {field: row[field] for field in INVENTORY_COMPONENT_FIELDS}
    return {
        "stable_fields": stable,
        "stable_sha256": object_digest(stable),
        "evidence_path": first["path"],
        "evidence_record": first["record"],
        "evidence_status": first["record_status"],
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


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    """Validate caller-supplied metadata only; never load or execute an asset."""

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
        raise ReferenceRejection("UNKNOWN_CONFIGURATION", "unsupported family configuration")
    if (not isinstance(manifest["source_revision"], str)
            or re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"]) is None):
        raise ReferenceRejection("BAD_SOURCE_REVISION", "source revision malformed")
    if (manifest["sample_rate_hz"] != SAMPLE_RATE_HZ
            or manifest["channels"] != CHANNELS
            or manifest["frame_samples"] != FRAME_SAMPLES
            or manifest["sample_format"] != SAMPLE_FORMAT):
        raise ReferenceRejection("FORMAT_MISMATCH", "installed v0 format mismatch")
    if not isinstance(manifest["checkpoint_path"], str) or not Path(
            manifest["checkpoint_path"]).is_absolute():
        raise ReferenceRejection("RELATIVE_CHECKPOINT", "checkpoint path must be absolute")
    if not _is_sha256(manifest["checkpoint_sha256"]):
        raise ReferenceRejection("BAD_CHECKPOINT_DIGEST", "checkpoint SHA-256 malformed")
    if (not isinstance(manifest["checkpoint_byte_count"], int)
            or isinstance(manifest["checkpoint_byte_count"], bool)
            or manifest["checkpoint_byte_count"] <= 0):
        raise ReferenceRejection("BAD_BYTE_COUNT", "checkpoint byte count malformed")
    if (not isinstance(manifest["checkpoint_revision"], str)
            or not manifest["checkpoint_revision"].strip()):
        raise ReferenceRejection("MISSING_CHECKPOINT_REVISION", "revision required")
    for field, code in (
        ("runtime_lock_digest", "BAD_RUNTIME_DIGEST"),
        ("rights_digest", "BAD_RIGHTS_DIGEST"),
        ("transcript_cohort_digest", "BAD_COHORT_DIGEST"),
        ("endpoint_label_digest", "BAD_LABEL_DIGEST"),
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
        "SIMULSTREAMING_ASSET_IDENTITY_UNPINNED",
        "hash-matched caller asset is still not an exact licensed streaming ASR checkpoint",
    )


def valid_manifest(checkpoint_path: str = "/absent/simulstreaming-checkpoint.safetensors") -> Dict[str, Any]:
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
        "transcript_cohort_digest": "0" * 64,
        "endpoint_label_digest": "0" * 64,
    }


def validate_reset(new_epoch: Any, first_sample: Any, current_epoch: int) -> Dict[str, Any]:
    if not isinstance(new_epoch, int) or isinstance(new_epoch, bool) or new_epoch < 0:
        raise ReferenceRejection("BAD_EPOCH", "invalid epoch")
    if (not isinstance(first_sample, int) or isinstance(first_sample, bool)
            or first_sample < 0):
        raise ReferenceRejection("BAD_POSITION", "invalid first input sample")
    if new_epoch <= current_epoch:
        raise ReferenceRejection("EPOCH_NOT_INCREASING", "epoch must increase")
    return {"accepted": True, "epoch": new_epoch, "first_input_sample": first_sample}


def frame_windows(count: int = SAMPLE_COUNT) -> List[List[int]]:
    return [list(range(index, min(index + FRAME_SAMPLES, count)))
            for index in range(0, count, FRAME_SAMPLES)]


def synthetic_rate() -> Dict[str, Any]:
    windows = frame_windows()
    samples = [index for window in windows for index in window]
    canonical_samples = list(range(SAMPLE_COUNT))
    swapped = list(canonical_samples)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    inserted = canonical_samples + [SAMPLE_COUNT]
    truncated = canonical_samples[:-1]
    return {
        "label": (
            "synthetic integer sample/frame controls; not audio, not ASR output, "
            "not a transcript, not WER/latency evidence"
        ),
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
            {"frame": index, "start": index * FRAME_SAMPLES,
             "end": min((index + 1) * FRAME_SAMPLES, SAMPLE_COUNT)}
            for index in range(len(windows))
        ],
        "identity_control": {
            "source_interval_union_exact": samples == canonical_samples,
            "reassembled_samples_sha256": object_digest(samples),
            "qualifies_candidate": False,
        },
        "content_controls": [
            {"id": "exact", "samples_sha256": object_digest(canonical_samples),
             "preserved": True, "qualifies_candidate": False},
            {"id": "swap", "samples_sha256": object_digest(swapped),
             "preserved": swapped == canonical_samples, "qualifies_candidate": False},
            {"id": "insert", "samples_sha256": object_digest(inserted),
             "preserved": inserted == canonical_samples, "qualifies_candidate": False},
            {"id": "truncate", "samples_sha256": object_digest(truncated),
             "preserved": truncated == canonical_samples, "qualifies_candidate": False},
        ],
        "rate_controls": [
            {"id": "rate_1x", "status": "synthetic_structural_only",
             "qualifies_candidate": False},
            {"id": "rate_changed", "status": "blocked_no_audio_renderer",
             "qualifies_candidate": False},
            {"id": "transient_audibility", "status": "blocked_no_audio_or_listening",
             "qualifies_candidate": False},
            {"id": "pitch_and_duration", "status": "blocked_no_audio_scorer",
             "qualifies_candidate": False},
        ],
        "coverage_controls": [
            {"id": "unfamiliar_speech", "status": "blocked_no_corpus"},
            {"id": "music", "status": "blocked_no_corpus"},
            {"id": "silence", "status": "blocked_no_corpus"},
            {"id": "rebuffer", "status": "blocked_no_paced_runtime"},
            {"id": "drift", "status": "blocked_no_paced_runtime"},
            {"id": "playback_buffering", "status": "blocked_no_target_device"},
        ],
        "note": (
            "Only exact integer frame geometry is exercised. No duration, pitch, "
            "transient, playback, transcript, endpoint or speech-preservation "
            "measurement is produced. Pause/filler decisions tied to source "
            "timestamps remain an unresolved semantic gate."
        ),
    }


def alignment_probe() -> Dict[str, Any]:
    return {
        "label": "synthetic half-open interval mapping only; no measured commit or output timing",
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "sample_ns": SAMPLE_NS,
        "frame_ns": FRAME_NS,
        "source_intervals": [[index * FRAME_SAMPLES,
                              min((index + 1) * FRAME_SAMPLES, SAMPLE_COUNT)]
                             for index in range(len(frame_windows()))],
        "modelled_content_offset_samples": 0,
        "first_output_ns": None,
        "tail_output_ns": None,
        "measured": False,
        "shift_probes": [
            {"shift_samples": 0, "accepted": True},
            {"shift_samples": -FRAME_SAMPLES, "accepted": False},
            {"shift_samples": FRAME_SAMPLES, "accepted": False},
        ],
        "partial_commit": "blocked; no pinned runtime or causal transcript path",
        "final_commit": "blocked; no finalization geometry or measured tail",
        "max_wait_fallback": "blocked; no paced runtime",
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
        "note": "Model-free fixture state only; no provider, decoder or model state exists.",
    }


def adverse_cases() -> Dict[str, Any]:
    base = valid_manifest()
    cases: List[Dict[str, Any]] = []

    def add(case_id: str, mutate: Any, code: str) -> None:
        manifest = dict(base)
        try:
            mutate(manifest)
            validate_caller_manifest(manifest)
            observed = "UNEXPECTED_ACCEPT"
        except ReferenceRejection as error:
            observed = error.code
        cases.append({"id": case_id, "expected": code, "observed": observed,
                      "accepted": observed == "UNEXPECTED_ACCEPT"})

    add("missing_field", lambda m: m.pop("frame_samples"), "MISSING_FIELD")
    add("unknown_field", lambda m: m.update(extra=1), "UNKNOWN_FIELD")
    add("wrong_adapter", lambda m: m.update(adapter="other"), "UNKNOWN_ADAPTER")
    add("wrong_configuration", lambda m: m.update(configuration_id="raw"),
        "UNKNOWN_CONFIGURATION")
    add("bad_source_revision", lambda m: m.update(source_revision="deadbeef"),
        "BAD_SOURCE_REVISION")
    add("wrong_rate", lambda m: m.update(sample_rate_hz=48000), "FORMAT_MISMATCH")
    add("wrong_channels", lambda m: m.update(channels=2), "FORMAT_MISMATCH")
    add("wrong_frame", lambda m: m.update(frame_samples=320), "FORMAT_MISMATCH")
    add("wrong_format", lambda m: m.update(sample_format="int16"), "FORMAT_MISMATCH")
    add("relative_checkpoint", lambda m: m.update(checkpoint_path="last.ckpt"),
        "RELATIVE_CHECKPOINT")
    add("absent_checkpoint", lambda m: None, "ASSET_ABSENT")
    add("bad_checkpoint_digest", lambda m: m.update(checkpoint_sha256="abc"),
        "BAD_CHECKPOINT_DIGEST")
    add("bad_byte_count", lambda m: m.update(checkpoint_byte_count=True),
        "BAD_BYTE_COUNT")
    add("bad_runtime_digest", lambda m: m.update(runtime_lock_digest="xyz"),
        "BAD_RUNTIME_DIGEST")
    add("bad_rights_digest", lambda m: m.update(rights_digest="xyz"),
        "BAD_RIGHTS_DIGEST")
    add("bad_cohort_digest", lambda m: m.update(transcript_cohort_digest="xyz"),
        "BAD_COHORT_DIGEST")
    add("bad_label_digest", lambda m: m.update(endpoint_label_digest="xyz"),
        "BAD_LABEL_DIGEST")
    try:
        validate_caller_manifest([])
        observed = "UNEXPECTED_ACCEPT"
    except ReferenceRejection as error:
        observed = error.code
    cases.append({"id": "manifest_not_object", "expected": "INVALID_MANIFEST",
                  "observed": observed, "accepted": observed == "UNEXPECTED_ACCEPT"})
    good = sum(1 for item in cases if item["accepted"])
    return {
        "case_count": len(cases),
        "accepted_count": good,
        "all_rejected": good == 0,
        "cases": cases,
        "metrics": None,
        "note": "All caller manifests fail closed before any asset load or execution.",
    }


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
        cases.append({"id": name, "observed": observed,
                      "accepted": observed == "UNEXPECTED_ACCEPT"})
    good = sum(1 for item in cases if item["accepted"])
    return {"case_count": len(cases), "accepted_count": good,
            "all_rejected": good == 0, "cases": cases, "metrics": None}


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
        cases.append({"id": name, "observed": observed,
                      "accepted": observed == "UNEXPECTED_ACCEPT"})
    good = sum(1 for item in cases if item["accepted"])
    return {"case_count": len(cases), "accepted_count": good,
            "all_rejected": good == 0, "cases": cases}


WORKSPACE_PROBE_PATHS: Tuple[str, ...] = (
    "data/checkouts/SimulStreaming",
    "data/checkouts/simulstreaming",
    "data/checkouts/whisper_streaming",
    "data/models/simulstreaming",
    "data/models/whisper-streaming",
    "data/envs/simulstreaming",
    "data/licenses/simulstreaming",
    "data/rights/simulstreaming.json",
    "adapters/simulstreaming",
    "docs/task-evidence/simulstreaming/checkpoint",
    "docs/task-evidence/simulstreaming/runtime",
)
HOME_PROBE_PATHS: Tuple[str, ...] = (
    ".cache/huggingface/hub/models--ufal--SimulStreaming",
    ".cache/huggingface/hub/models--openai--whisper-large-v3",
    ".cache/huggingface/hub/models--SYSTRAN--faster-whisper-large-v3",
    ".cache/whisper",
)


def absent_artifact_probe() -> Dict[str, Any]:
    workspace = [
        {"path": path, "present": (SOURCE_ROOT / path).exists()}
        for path in WORKSPACE_PROBE_PATHS
    ]
    worktree = [
        {"path": path, "present": (SDK_ROOT / path).exists()}
        for path in WORKSPACE_PROBE_PATHS
    ]
    home = Path.home()
    home_rows = [
        {"path": "~/" + path, "present": (home / path).exists()}
        for path in HOME_PROBE_PATHS
    ]
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
        "census_status": "unavailable/blocked",
        "audit_status": "No local ASR checkpoint or streaming adapter; no model substituted",
        "reaudit_status": "exact weights and streaming adapters still absent",
        "source_reported_latency": {
            "value": "3.3 s",
            "scope": "upstream Whisper-Streaming paper conditions; not local or mobile evidence",
            "qualifies": False,
        },
        "separation": (
            "Pinned records are provenance only. The upstream repository and paper "
            "descriptions are source-reported and are not local outputs or "
            "measurements. Whisper-Streaming and SimulStreaming are distinct from "
            "the unrelated ASR survey packages; no substitution is made."
        ),
        "qualifies": False,
        "listening_performed_here": False,
        "inference_performed_here": False,
    }


def rate_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "source_output_mapping": {
                "status": "synthetic_structural_only",
                "evidence": "Exact half-open 160-sample integer intervals only; no rendered source/output pair.",
            },
            "duration_and_pitch": {
                "status": "blocked",
                "evidence": "No audio renderer, no duration/pitch scorer and no rate-change output exists.",
            },
            "transient_audibility": {
                "status": "blocked",
                "evidence": "No audio and no authorized listening result exists.",
            },
            "playback_buffering": {
                "status": "blocked",
                "evidence": "No paced runtime or target-device buffer measurement is staged.",
            },
            "rate_1x_and_rate_changes": {
                "status": "synthetic_structural_only",
                "evidence": "1x integer mapping only; rate changes are rejected as unmodelled.",
            },
            "unfamiliar_speech_music_silence": {
                "status": "blocked",
                "evidence": "No permitted corpus or content-conditioned fixture exists.",
            },
            "rebuffer_drift_and_final_partial_window": {
                "status": "synthetic_structural_only",
                "evidence": "Final 5-sample partial window geometry only; no rebuffer or drift measurement.",
            },
            "pause_filler_source_timestamps": {
                "status": "blocked",
                "evidence": "Only integer source positions are modelled; no semantic pause/filler decision exists.",
            },
            "speech_preservation_wer": {
                "status": "blocked",
                "evidence": "No reference transcript, pinned scorer or stratified WER/CER result exists.",
            },
            "streaming_partial_final_and_max_wait": {
                "status": "blocked",
                "evidence": "No causal decoder state, partial/final commit or maximum-wait fallback exists.",
            },
            "device_availability_and_dropped_stale_events": {
                "status": "blocked",
                "evidence": "No device clock, dropped chunk or stale partial audit exists.",
            },
        },
    }


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    rate = synthetic_rate()
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
            "note": (
                "Metadata-only reference. A hash-matched caller asset still fails as "
                "SIMULSTREAMING_ASSET_IDENTITY_UNPINNED; no weights or backend is promoted. "
                "Configuration IDs are task-local metadata labels, not a claim of an exact "
                "upstream SimulStreaming policy."
            ),
        },
        "asset_resolution": probe,
        "synthetic_rate": rate,
        "rate_profile": rate_profile(),
        "availability": {
            "status": "modelled_not_measured",
            "clock": "fixture-monotonic-not-device",
            "whole_response_available_after_final_interval": True,
            "device_timing": False,
            "streaming_result": False,
            "partial_commit_claim": False,
            "content_delay_claim": False,
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
            "all_rejected": (manifest_adverse["all_rejected"]
                             and json_adverse["all_rejected"]
                             and pin_adverse["all_rejected"]),
            "metrics": None,
        },
        "comparison": {
            "status": "blocked_no_exact_asr_asset_runtime_or_cohort",
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
            "cohort_consent": "unreviewed",
            "output_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "asset_ledger": dict(ASSET_LEDGER),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact licensed SimulStreaming source, weights, backend, revision, bytes and runtime",
            "rights-cleared turn-labelled conversational cohort, transcripts and pinned scorers",
            "matched rate, WER/CER and endpoint-delay outcomes on the exact runtime",
            "paced causal state, maximum-wait, dropped/stale and target-device timing",
            "opt-in provider intake and release approval",
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
        "# SHA-256 pins for SDK-SIMULSTREAMING.",
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
            "No ASR source, weights, audio, cohort or runtime artifact is bundled.",
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


def scope_base(worktree: Path,
               refs: Tuple[str, ...] = SCOPE_BASE_REFS) -> str | None:
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
