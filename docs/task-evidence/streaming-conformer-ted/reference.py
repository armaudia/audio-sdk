# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for Streaming Conformer-TED.

This package is proposal-only feasibility evidence. It records the exact
blocker state for Streaming Conformer-TED / FastConformer: no exact TED
checkpoint, streaming config or local ASR runtime is staged. It models an
installed-v0 geometry probe and a caller-supplied asset boundary with
synthetic, in-memory values only. It does not implement, vendor, download,
load or execute any model, runtime, corpus or audio asset. No real audio,
listening, device timing, benchmark or release result is included. The Rate
acceptance profile is mapped with every non-synthetic item left blocked.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import struct
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

TASK_DIR = Path(__file__).resolve().parent
SDK_ROOT = TASK_DIR.parents[2]
SOURCE_ROOT = SDK_ROOT.parents[2]
TASK_BOARD = "audio-benchmark-platform/plan/swarm/TASKS.json"

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/streaming-conformer-ted/caller-supplied/0.1"
TASK_ID = "SDK-STREAMING-CONFORMER-TED"
TITLE = "Streaming Conformer-TED"
COMPONENT = "streaming-conformer-ted"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "14af17740bf8c571f9a985c88fd56f5b5b8e8ae8"
BRANCH = "swarm/SDK-STREAMING-CONFORMER-TED"
REVIEWER = "reviewer-STREAMING-CONFORMER-TED"
PROFILE = "Rate"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_geometry_incomplete"
CONFIGURATION_ID = "streaming-conformer-ted.caller-manifest/0.1"

SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"

SOURCE_PINS: Dict[str, str] = {
    "research/voice-enhancement-20261101/candidate_matrix.csv":
        "3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245",
    "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md":
        "5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f",
    "research/voice-enhancement-20261101/agent-segmentation/REPORT.md":
        "ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2",
    "audio-benchmark-platform/plan/INVENTORY.json":
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
}

BOARD_STABLE_SHA256 = (
    "55bf3c17f13a75c60202daaaba6a4e64373907b24647544f79d76db0d5850bf5"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence", "quality",
)

TASK_PREFIX = "docs/task-evidence/streaming-conformer-ted/"
LOCAL_PIN_PATHS: Tuple[str, ...] = (
    "LICENSES.md",
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

SOURCE_LINES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "candidate-matrix-row",
        "path": "research/voice-enhancement-20261101/candidate_matrix.csv",
        "line": 36,
        "text": (
            'Disfluency and TSM,Streaming Conformer-TED / FastConformer,'
            'unavailable/blocked,"No exact TED checkpoint, streaming config '
            'or local ASR runtime; using another Conformer would change '
            'candidate identity.",Whisper streaming ASR; fixed transcript,'
            'research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md; '
            'research/voice-enhancement-20261101/agent-segmentation/REPORT.md'
        ),
    },
    {
        "id": "vad-asr-disposition",
        "path": "research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md",
        "line": 11,
        "text": (
            "| Whisper-Streaming / SimulStreaming | No local ASR checkpoint or streaming adapter; `whisper`, `faster_whisper`, NeMo and sherpa-onnx were absent in the checked runtime. The AMI corpus includes transcript/alignment material, but ASR model weights and an isolated source/runtime are absent. No model was substituted. |"
        ),
    },
    {
        "id": "segmentation-matrix",
        "path": "research/voice-enhancement-20261101/agent-segmentation/REPORT.md",
        "line": 53,
        "text": (
            "6. **TSM must be evaluated as a transformation.** Freeze target speed ratios and test intelligibility, F0/formant preservation, transient/onset artifacts, duration error, audio quality, and latency at both speech and music/transient stress inputs. Include identity-speed output as a speech-preservation check. A neural method and classical baseline need exactly the same inputs and targets."
        ),
    },
)

ABSENT_CANDIDATES: Tuple[str, ...] = (
    "research/voice-enhancement-20261101/repos/conformer-ted",
    "research/voice-enhancement-20261101/repos/fastconformer",
    "research/voice-enhancement-20261101/repos/NeMo",
    "data/checkouts/conformer-ted",
    "data/checkouts/fastconformer",
    "data/models/conformer-ted",
    "data/models/fastconformer",
    "data/checkpoints/conformer-ted",
    "third_party/conformer-ted",
    "third_party/fastconformer",
    "deps/conformer-ted",
    "deps/fastconformer",
)
SDK_ABSENT_CANDIDATES: Tuple[str, ...] = (
    "third_party/conformer-ted",
    "third_party/fastconformer",
    "deps/conformer-ted",
    "deps/fastconformer",
    "adapters/streaming-conformer-ted",
    "data/assets/streaming-conformer-ted",
    "docs/task-evidence/streaming-conformer-ted/assets",
)

REQUIRED_ASSETS: Tuple[Dict[str, str], ...] = (
    {"id": "source_revision", "artifact": "exact Streaming Conformer-TED source revision"},
    {"id": "checkpoint", "artifact": "exact TED checkpoint and streaming config"},
    {"id": "runtime", "artifact": "pinned local ASR runtime/build identity"},
    {"id": "cohort", "artifact": "rights-cleared matched cohort with fixed transcript"},
)

ASSET_LEDGER: Dict[str, Any] = {
    "status": "absent_exact_source_checkpoint_runtime_and_cohort",
    "source_revision": {
        "revision": None, "archive_sha256": None, "present_locally": False,
        "license": None,
    },
    "checkpoint": {
        "path": None, "sha256": None, "byte_count": None, "present_locally": False,
        "streaming_config_sha256": None,
    },
    "runtime": {
        "path": None, "sha256": None, "byte_count": None, "present_locally": False,
        "build_id": None,
    },
    "cohort": {
        "path": None, "sha256": None, "present_locally": False, "rights_status": None,
    },
    "downloaded": False, "vendored": False, "loaded": False, "executed": False,
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
    "source_vendored": False,
    "weights_vendored": False,
    "format": {
        "channels": CHANNELS, "frame_samples": FRAME_SAMPLES,
        "sample_format": SAMPLE_FORMAT, "sample_rate_hz": SAMPLE_RATE_HZ,
    },
}

SCOPE: Dict[str, Any] = {
    "synthetic_only": True, "task_local_only": True, "benchmark": False,
    "descriptor_registration": False, "device_timing": False,
    "download_attempted": False, "external_executable_invoked": False,
    "listening": False, "network_used": False, "provider_registered": False,
    "real_audio": False, "release_claim": False, "model_executed": False,
    "runtime_executed": False,
}

NEGATIVE_CLAIMS: List[str] = [
    "No Streaming Conformer-TED or FastConformer source, checkpoint, config, runtime, binary or corpus is vendored, downloaded, loaded or executed.",
    "The caller-supplied asset validator is metadata-only and fails closed before any asset load or runtime invocation.",
    "Synthetic in-memory float32 frames are not real audio and not ASR output.",
    "No exact TED checkpoint, streaming config or local ASR runtime is present or substituted.",
    "No rights-cleared cohort, fixed transcript, WER/latency scorer or listening result is present.",
    "No target-runtime timing, pacing, memory, deadline or device measurement is made.",
    "No provider, descriptor, default, ABI, CONTRACTS, registry, shared build or CI behavior is changed.",
    "No benchmark, qualification, upstream-parity or release claim is made.",
    "No missing, blocked or synthetic result qualifies the candidate.",
]

GATES: List[Dict[str, Any]] = [
    {"id": "RG-01", "title": "exact_source_checkpoint_and_runtime_identity", "status": "blocked",
     "qualifies": False, "linked_row": TASK_ID,
     "statement": "No exact Streaming Conformer-TED source revision, TED checkpoint, streaming config or local runtime identity is pinned.",
     "reopen_condition": "Stage an exact licensed source revision, TED checkpoint, streaming config and runtime with immutable digests and notices."},
    {"id": "RG-02", "title": "rights_and_license_clearance", "status": "blocked",
     "qualifies": False, "linked_row": TASK_ID,
     "statement": "No source, checkpoint, config, runtime or corpus rights/license review is complete for this exact candidate.",
     "reopen_condition": "Record reviewed rights and license terms for every required asset and target use."},
    {"id": "RG-03", "title": "matched_cohort_and_transcript_protocol", "status": "blocked",
     "qualifies": False, "linked_row": TASK_ID,
     "statement": "No rights-cleared matched cohort, fixed transcript policy or task-matched control is staged.",
     "reopen_condition": "Freeze a rights-cleared cohort with fixed transcripts, identity/control runs and an exact scoring protocol."},
    {"id": "RG-04", "title": "streaming_asr_quality_and_preservation", "status": "blocked",
     "qualifies": False, "linked_row": TASK_ID,
     "statement": "No WER, transcript-preservation, disfluency-handling or failure-case result exists for the exact candidate.",
     "reopen_condition": "Score the pinned candidate on the frozen cohort with agreed metrics, controls and failure-case analysis."},
    {"id": "RG-05", "title": "source_output_mapping_and_final_partial", "status": "blocked",
     "qualifies": False, "linked_row": TASK_ID,
     "statement": "No exact source/output mapping, timestamp, rate-change or final-partial evidence exists for the real candidate.",
     "reopen_condition": "Measure exact mapping, timestamps, drift and final-partial behavior on the pinned runtime."},
    {"id": "RG-06", "title": "alignment_state_memory_and_target_timing", "status": "blocked",
     "qualifies": False, "linked_row": TASK_ID,
     "statement": "No measured content mapping, state behavior, memory use or content/availability timing exists at a target runtime.",
     "reopen_condition": "Run a paced target harness with agreed coverage, margins, deadlines and resource limits."},
    {"id": "RG-07", "title": "opt_in_intake_and_public_default", "status": "blocked",
     "qualifies": False, "linked_row": TASK_ID,
     "statement": "No separate opt-in provider intake, OFF-default decision or registration review exists.",
     "reopen_condition": "Complete a separate provider intake with OFF default and an explicit public default decision."},
    {"id": "RG-08", "title": "independent_exact_head_review", "status": "blocked",
     "qualifies": False, "linked_row": TASK_ID,
     "statement": "No independent reviewer has approved the exact head and no board transition is recorded.",
     "reopen_condition": "Obtain independent exact-head approval and a coordinator-recorded board transition."},
]

EXACT_BLOCKERS: List[Dict[str, Any]] = [
    {"id": "XB-01", "status": "open", "qualifies": False, "linked_gates": ["RG-01", "RG-02"],
     "statement": "No exact Streaming Conformer-TED source revision, TED checkpoint, streaming config, local ASR runtime or rights-reviewed license bundle is present. Fixed absence probes and PATH lookup found no candidate artifact.",
     "reopen": "Stage an exact licensed source revision, TED checkpoint, streaming config and runtime with immutable digests, notices and rights review."},
    {"id": "XB-02", "status": "open", "qualifies": False, "linked_gates": ["RG-03", "RG-04"],
     "statement": "No rights-cleared matched cohort, fixed transcript policy, WER/scoring protocol, control or baseline is staged for the exact candidate.",
     "reopen": "Freeze the cohort, transcript policy, controls and scorer, then run the exact candidate on real inputs."},
    {"id": "XB-03", "status": "open", "qualifies": False, "linked_gates": ["RG-05", "RG-06"],
     "statement": "No real streaming output, source/output mapping, timestamp, memory, pacing or target-runtime availability evidence exists.",
     "reopen": "Execute the pinned runtime on target hardware and record mapping, state, memory and deadline evidence."},
    {"id": "XB-04", "status": "open", "qualifies": False, "linked_gates": ["RG-07", "RG-08"],
     "statement": "No opt-in intake, OFF-default decision, independent exact-head review or board transition exists.",
     "reopen": "Complete separate opt-in intake with default OFF and obtain independent exact-head approval before any exposure."},
]

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "adapter", "configuration_id", "sample_rate_hz", "channels",
    "sample_format", "frame_samples", "source_revision", "source_sha256",
    "source_byte_count", "checkpoint_path", "checkpoint_sha256",
    "checkpoint_byte_count", "streaming_config_path", "streaming_config_sha256",
    "runtime_path", "runtime_sha256", "runtime_byte_count", "license_id",
    "rights_review_id",
)


class ReferenceRejection(AssertionError):
    """A fail-closed task-local validation rejection."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(code + ": " + message)
        self.code = code
        self.message = message


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


def source_lines() -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for item in SOURCE_LINES:
        path = SOURCE_ROOT / item["path"]
        lines = path.read_text(encoding="utf-8").splitlines()
        if lines[item["line"] - 1].strip() != item["text"]:
            raise ValueError("source_line_mismatch:" + item["id"])
        entries.append({
            "id": item["id"], "path": item["path"], "line": item["line"],
            "sha256": sha256_file(path), "text": item["text"],
        })
    return {"entries": entries, "line_count": len(entries)}


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


def _hex_digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _next_u32(state: int) -> Tuple[int, int]:
    state = (1103515245 * state + 12345) & 0xFFFFFFFF
    return state, state


def synthetic_float_samples(count: int, seed: int = 0xC0A4E8ED) -> List[float]:
    state = seed
    values: List[float] = []
    for _ in range(count):
        state, draw = _next_u32(state)
        values.append(((draw >> 8) / 0xFFFFFF - 0.5) * 0.5)
    return values


def synthetic_frame(index: int) -> List[float]:
    return synthetic_float_samples(FRAME_SAMPLES, 0xC0A4E8ED + index)


def valid_manifest() -> Dict[str, Any]:
    return {
        "adapter": SCHEMA_MANIFEST,
        "configuration_id": CONFIGURATION_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
        "source_revision": "caller-declared-unverified",
        "source_sha256": "0" * 64,
        "source_byte_count": 1,
        "checkpoint_path": "/absent/conformer-ted.ckpt",
        "checkpoint_sha256": "0" * 64,
        "checkpoint_byte_count": 1,
        "streaming_config_path": "/absent/streaming.yaml",
        "streaming_config_sha256": "0" * 64,
        "runtime_path": "/absent/runtime",
        "runtime_sha256": "0" * 64,
        "runtime_byte_count": 1,
        "license_id": "caller-declared-unverified",
        "rights_review_id": "caller-declared-unverified",
    }


def validate_caller_manifest(manifest: Any,
                             source_bytes: bytes | None = None,
                             checkpoint_bytes: bytes | None = None,
                             config_bytes: bytes | None = None,
                             runtime_bytes: bytes | None = None) -> None:
    if not isinstance(manifest, dict):
        raise ReferenceRejection("MANIFEST_NOT_OBJECT", "manifest must be an object")
    if set(manifest) != set(CALLER_MANIFEST_FIELDS):
        raise ReferenceRejection("MANIFEST_FIELD_SET", "manifest field set mismatch")
    if manifest["adapter"] != SCHEMA_MANIFEST:
        raise ReferenceRejection("WRONG_ADAPTER", "unsupported adapter schema")
    if manifest["configuration_id"] != CONFIGURATION_ID:
        raise ReferenceRejection("WRONG_CONFIGURATION", "unsupported configuration")
    if manifest["sample_rate_hz"] != SAMPLE_RATE_HZ:
        raise ReferenceRejection("WRONG_SAMPLE_RATE", "only 16000 Hz is admitted")
    if manifest["channels"] != CHANNELS:
        raise ReferenceRejection("WRONG_CHANNELS", "only mono is admitted")
    if manifest["sample_format"] != SAMPLE_FORMAT:
        raise ReferenceRejection("WRONG_SAMPLE_FORMAT", "only float32 is admitted")
    if manifest["frame_samples"] != FRAME_SAMPLES:
        raise ReferenceRejection("WRONG_FRAME_SAMPLES", "only 160-sample frames are admitted")
    for path_key in ("checkpoint_path", "streaming_config_path", "runtime_path"):
        value = manifest[path_key]
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise ReferenceRejection("RELATIVE_ASSET_PATH", path_key + " must be absolute")
    for digest_key in ("source_sha256", "checkpoint_sha256", "streaming_config_sha256", "runtime_sha256"):
        if not _hex_digest(manifest[digest_key]):
            raise ReferenceRejection("BAD_ASSET_DIGEST", digest_key + " malformed")
    for count_key in ("source_byte_count", "checkpoint_byte_count", "runtime_byte_count"):
        if not _positive_int(manifest[count_key]):
            raise ReferenceRejection("BAD_BYTE_COUNT", count_key + " malformed")
    for text_key in ("source_revision", "license_id", "rights_review_id"):
        value = manifest[text_key]
        if not isinstance(value, str) or not value.strip():
            raise ReferenceRejection("MISSING_IDENTITY", text_key + " required")
    if source_bytes is None:
        raise ReferenceRejection("ASSET_ABSENT", "caller source bytes were not supplied")
    if len(source_bytes) != manifest["source_byte_count"]:
        raise ReferenceRejection("ASSET_SIZE_MISMATCH", "source byte count mismatch")
    if sha256_bytes(source_bytes) != manifest["source_sha256"]:
        raise ReferenceRejection("ASSET_HASH_MISMATCH", "source SHA-256 mismatch")
    if checkpoint_bytes is None:
        raise ReferenceRejection("ASSET_ABSENT", "caller checkpoint bytes were not supplied")
    if len(checkpoint_bytes) != manifest["checkpoint_byte_count"]:
        raise ReferenceRejection("ASSET_SIZE_MISMATCH", "checkpoint byte count mismatch")
    if sha256_bytes(checkpoint_bytes) != manifest["checkpoint_sha256"]:
        raise ReferenceRejection("ASSET_HASH_MISMATCH", "checkpoint SHA-256 mismatch")
    if config_bytes is None:
        raise ReferenceRejection("ASSET_ABSENT", "caller streaming config bytes were not supplied")
    if sha256_bytes(config_bytes) != manifest["streaming_config_sha256"]:
        raise ReferenceRejection("ASSET_HASH_MISMATCH", "streaming config SHA-256 mismatch")
    if runtime_bytes is not None:
        if len(runtime_bytes) != manifest["runtime_byte_count"]:
            raise ReferenceRejection("RUNTIME_SIZE_MISMATCH", "runtime byte count mismatch")
        if sha256_bytes(runtime_bytes) != manifest["runtime_sha256"]:
            raise ReferenceRejection("RUNTIME_HASH_MISMATCH", "runtime SHA-256 mismatch")
    raise ReferenceRejection(
        "CANDIDATE_IDENTITY_UNPINNED",
        "hash-matched bytes are still not an exact licensed TED checkpoint, streaming config and reviewed runtime",
    )


def invalid_json_cases() -> Dict[str, Any]:
    cases = []
    for case_id, text in (
            ("duplicate_key", '{"a":1,"a":2}'),
            ("nan_constant", '{"a":NaN}'),
            ("infinity_constant", '{"a":Infinity}'),
            ("negative_infinity_constant", '{"a":-Infinity}'),
            ("trailing_data", '{"a":1} extra'),
            ("invalid_syntax", '{"a":'),
            ("empty_text", "")):
        try:
            strict_loads(text)
            accepted, observed = True, "ACCEPTED"
        except ValueError:
            accepted, observed = False, "INVALID_JSON"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {"case_count": len(cases), "cases": cases,
            "accepted_count": sum(1 for c in cases if c["accepted"]),
            "all_rejected": all(not c["accepted"] for c in cases), "metrics": None}


def invalid_pin_cases() -> Dict[str, Any]:
    digest = "a" * 64
    samples = (
        ("duplicate_key", digest + "  source:dup\n" + digest + "  source:dup\n"),
        ("short_digest", "abc  source:short\n"),
        ("missing_separator", digest + " source:missing\n"),
        ("absolute_path", digest + "  /absolute\n"),
        ("traversal", digest + "  source:../escape\n"),
    )
    cases = []
    for case_id, text in samples:
        try:
            parse_pin_lines(text)
            accepted, observed = True, "ACCEPTED"
        except ValueError:
            accepted, observed = False, "INVALID_PIN"
        cases.append({"accepted": accepted, "id": case_id, "observed": observed})
    return {"case_count": len(cases), "cases": cases,
            "accepted_count": sum(1 for c in cases if c["accepted"]),
            "all_rejected": all(not c["accepted"] for c in cases)}


def adverse_cases() -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    source = b"synthetic-source"
    checkpoint = b"synthetic-checkpoint"
    config = b"synthetic-config"

    def probe(case_id: str, mutate: Any, candidate: Any = None,
              supplied: Tuple[bytes | None, bytes | None, bytes | None] = (source, checkpoint, config)) -> None:
        manifest = valid_manifest() if candidate is None else candidate
        mutate(manifest)
        try:
            validate_caller_manifest(manifest, *supplied)
            observed = "ACCEPTED"
        except ReferenceRejection as error:
            observed = error.code
        cases.append({"accepted": observed == "ACCEPTED", "id": case_id, "observed": observed})

    probe("missing_field", lambda m: m.pop("sample_rate_hz"))
    probe("unknown_field", lambda m: m.update({"unexpected": 1}))
    probe("wrong_adapter", lambda m: m.update({"adapter": "other"}))
    probe("wrong_configuration", lambda m: m.update({"configuration_id": "other"}))
    probe("wrong_sample_rate", lambda m: m.update({"sample_rate_hz": 48000}))
    probe("wrong_channels", lambda m: m.update({"channels": 2}))
    probe("wrong_sample_format", lambda m: m.update({"sample_format": "int16"}))
    probe("wrong_frame_samples", lambda m: m.update({"frame_samples": 320}))
    probe("relative_checkpoint_path", lambda m: m.update({"checkpoint_path": "relative.ckpt"}))
    probe("absent_source", lambda m: None, supplied=(None, checkpoint, config))
    probe("bad_source_digest", lambda m: m.update({"source_sha256": "f" * 64}))
    probe("bad_source_byte_count", lambda m: m.update({"source_byte_count": 99}))
    probe("absent_checkpoint", lambda m: None, supplied=(source, None, config))
    probe("bad_checkpoint_digest", lambda m: m.update({"checkpoint_sha256": "f" * 64}))
    probe("absent_config", lambda m: None, supplied=(source, checkpoint, None))
    probe("bad_config_digest", lambda m: m.update({"streaming_config_sha256": "f" * 64}))
    probe("missing_identity", lambda m: m.update({"rights_review_id": ""}))
    probe("manifest_not_object", lambda m: None, candidate=["not", "an", "object"])
    return {
        "case_count": len(cases), "cases": cases,
        "accepted_count": sum(1 for c in cases if c["accepted"]),
        "all_rejected": all(not c["accepted"] for c in cases),
        "metrics": None,
        "note": "All cases fail closed before any model/runtime load or quality metric.",
    }


def geometry_probe() -> Dict[str, Any]:
    full_frames = [synthetic_frame(index) for index in range(2)]
    final_valid = synthetic_frame(2)[:5]
    final_frame = final_valid + [0.0] * (FRAME_SAMPLES - len(final_valid))
    frames = full_frames + [final_frame]
    accepted_samples = FRAME_SAMPLES * len(full_frames) + len(final_valid)
    intervals = [[index * FRAME_SAMPLES, (index + 1) * FRAME_SAMPLES]
                 for index in range(len(full_frames))]
    intervals.append([FRAME_SAMPLES * len(full_frames), accepted_samples])
    covered: List[int] = []
    for start, end in intervals:
        covered.extend(range(start, end))
    all_values = [value for frame in frames for value in frame]
    frame_bytes = [struct.pack("<" + str(FRAME_SAMPLES) + "f", *frame) for frame in frames]
    return {
        "label": "model-free 16 kHz mono float32 160-sample geometry; not ASR output",
        "sample_rate_hz": SAMPLE_RATE_HZ, "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT, "frame_samples": FRAME_SAMPLES,
        "frame_count": len(frames), "accepted_samples": accepted_samples,
        "final_valid_samples": len(final_valid),
        "final_zero_padding_samples": FRAME_SAMPLES - len(final_valid),
        "source_intervals": intervals,
        "partition_ok": covered == list(range(accepted_samples)),
        "frame_sha256": [sha256_bytes(payload) for payload in frame_bytes],
        "nonfinite_count": sum(1 for value in all_values if not math.isfinite(value)),
        "peak_abs": max(abs(value) for value in all_values),
        "identity_control": {"repeat_frame_byte_identical": synthetic_frame(0) == synthetic_frame(0), "qualifies": False},
        "declared_task_local_buffering_delay_samples": 0,
        "content_delay_claimed": False,
        "note": "Exact integer intervals and in-memory float32 values only. No model, runtime, audio decode, device clock or listening is used.",
    }


def asset_pins_absent() -> bool:
    for group in ("source_revision", "checkpoint", "runtime", "cohort"):
        for key, value in ASSET_LEDGER[group].items():
            if key.endswith("present_locally"):
                if value is not False:
                    return False
            elif value is not None:
                return False
    return not any(ASSET_LEDGER[key] for key in ("downloaded", "vendored", "loaded", "executed"))


def absent_artifact_probe() -> Dict[str, Any]:
    workspace_found = [path for path in ABSENT_CANDIDATES if (SOURCE_ROOT / path).exists()]
    sdk_found = [path for path in SDK_ABSENT_CANDIDATES if (SDK_ROOT / path).exists()]
    return {
        "note": "Bounded read-only path probes; no download, import or load attempted.",
        "present": bool(workspace_found or sdk_found),
        "workspace_candidates": list(ABSENT_CANDIDATES),
        "sdk_worktree_candidates": list(SDK_ABSENT_CANDIDATES),
        "workspace_found": workspace_found,
        "sdk_worktree_found": sdk_found,
        "method": "explicit candidate paths only; no recursive filesystem walk",
    }


def rate_profile() -> Dict[str, Any]:
    return {
        "profile": PROFILE,
        "source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "required_items": {
            "source_output_mapping": {
                "status": "synthetic_only", "qualifies": False,
                "evidence": "Integer frame intervals only; no real ASR or rate transform output.",
            },
            "duration": {
                "status": "synthetic_only", "qualifies": False,
                "evidence": "Exact integer frame arithmetic; no real audio duration measurement.",
            },
            "pitch": {
                "status": "blocked", "qualifies": False,
                "evidence": "No pitch measurement, audio, or listening performed.",
            },
            "transient_audibility": {
                "status": "blocked", "qualifies": False,
                "evidence": "No audio output or audibility protocol exists.",
            },
            "playback_buffering": {
                "status": "synthetic_only", "qualifies": False,
                "evidence": "160-frame aggregation arithmetic; no device buffer or pacing.",
            },
            "rate_changes": {
                "status": "blocked", "qualifies": False,
                "evidence": "No exact streaming runtime or rate-change measurement exists.",
            },
            "unfamiliar_speech_music_silence": {
                "status": "blocked", "qualifies": False,
                "evidence": "No rights-cleared held-out cohort exists.",
            },
            "rebuffer_drift_final_partial": {
                "status": "synthetic_only", "qualifies": False,
                "evidence": "One synthetic final-partial probe; no paced workload or drift clock.",
            },
            "speech_preservation_and_pause_decisions": {
                "status": "blocked", "qualifies": False,
                "evidence": "No transcript, speech preservation score or source-tied decision exists.",
            },
        },
        "matched_evidence_status": "blocked",
    }


def source_reported() -> Dict[str, Any]:
    lines = source_lines()
    return {
        "entries": lines["entries"],
        "line_count": lines["line_count"],
        "census_facts": {
            "candidate": "Streaming Conformer-TED / FastConformer",
            "status": "unavailable/blocked",
            "exact_ted_checkpoint_present": False,
            "exact_streaming_config_present": False,
            "local_asr_runtime_present": False,
            "substitution_changes_identity": True,
        },
        "excluded_from_local_evidence": [
            "NeMo cache-aware FastConformer/RNNT is a source-reported analogue only; it is not this exact TED candidate.",
            "No WER, latency, or streaming quality number is present for the exact candidate.",
            "The synthetic geometry probe is not audio and not ASR output.",
        ],
        "listening_performed_here": False,
        "qualifies": False,
    }


def enhancement_profile() -> Dict[str, Any]:
    """Back-compat name for report shape consistency with other evidence packages."""
    return rate_profile()


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    probe = absent_artifact_probe()
    manifest_adverse = adverse_cases()
    json_adverse = invalid_json_cases()
    pin_adverse = invalid_pin_cases()
    geometry = geometry_probe()
    manifest = valid_manifest()
    manifest["source_sha256"] = sha256_bytes(b"synthetic-source")
    manifest["source_byte_count"] = len(b"synthetic-source")
    manifest["checkpoint_sha256"] = sha256_bytes(b"synthetic-checkpoint")
    manifest["checkpoint_byte_count"] = len(b"synthetic-checkpoint")
    manifest["streaming_config_sha256"] = sha256_bytes(b"synthetic-config")
    try:
        validate_caller_manifest(manifest, b"synthetic-source", b"synthetic-checkpoint", b"synthetic-config")
        manifest_outcome = "ACCEPTED"
    except ReferenceRejection as error:
        manifest_outcome = error.code
    if manifest_outcome != "CANDIDATE_IDENTITY_UNPINNED":
        raise ValueError("unexpected_caller_manifest_outcome:" + manifest_outcome)

    report: Dict[str, Any] = {
        "schema_id": SCHEMA_REPORT,
        "task_id": TASK_ID, "title": TITLE, "component_id": COMPONENT,
        "repository": REPOSITORY, "base_commit": BASE_COMMIT, "branch": BRANCH,
        "profile": PROFILE, "status": STATUS, "decision": DECISION,
        "defer_before": DEFER_BEFORE, "evidence_status": EVIDENCE_STATUS,
        "qualification_status": QUALIFICATION_STATUS,
        "no_missing_result_qualifies_candidate": True,
        "scope": dict(SCOPE), "negative_claims": list(NEGATIVE_CLAIMS),
        "boundary": dict(BOUNDARY), "format": dict(BOUNDARY["format"]),
        "caller_supplied_asset_contract": {
            "schema_id": SCHEMA_MANIFEST,
            "configuration_id": CONFIGURATION_ID,
            "required_fields": list(CALLER_MANIFEST_FIELDS),
            "required_assets": [dict(item) for item in REQUIRED_ASSETS],
            "validated_outcome": manifest_outcome,
            "loaded": False, "executed": False,
            "note": "Metadata and in-memory byte validation only. Hash-matched bytes still fail as CANDIDATE_IDENTITY_UNPINNED.",
        },
        "geometry_probe": geometry,
        "rate_profile": rate_profile(),
        "asset_resolution": probe,
        "asset_ledger": dict(ASSET_LEDGER),
        "asset_pins_absent": asset_pins_absent(),
        "adverse": {
            "caller_manifest": manifest_adverse,
            "invalid_json": json_adverse,
            "invalid_pins": pin_adverse,
            "all_rejected": (manifest_adverse["all_rejected"] and json_adverse["all_rejected"] and pin_adverse["all_rejected"]),
            "metrics": None,
        },
        "comparison": {
            "status": "blocked_no_exact_ted_checkpoint_or_runtime_or_matched_cohort",
            "identity_control": "synthetic integer frame control only",
            "task_matched_baseline": "blocked",
            "qualifies_candidate": False,
        },
        "source_reported": source_reported(),
        "available_evidence": {
            "status": "synthetic_geometry_only", "clock": "no runtime clock",
            "real_model_output": False, "device_timing": False,
            "content_delay_claim": False, "first_output_or_tail": "blocked_not_measured",
        },
        "licensing_analysis": {
            "exact_source_license": "unreviewed",
            "exact_checkpoint_license": "unreviewed",
            "runtime_license": "unreviewed",
            "corpus_rights": "unreviewed",
            "product_use": "unreviewed",
            "qualifies": False,
        },
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [gate["statement"] for gate in GATES],
        "reopening_conditions": [item["reopen"] for item in EXACT_BLOCKERS],
        "evidence_classes": {
            "source_reported": True, "synthetic": True, "model_free_geometry": True,
            "real_local_model_output": False, "real_audio": False, "listening": False,
            "device_timing": False, "benchmark": False,
        },
        "board_link": board_link(),
        "repeatability": {
            "canonical": "sorted keys, compact separators, allow_nan=False, one trailing LF",
            "fresh_builds": 3, "comparison": "exact SHA-256 over bytes; no tolerance",
        },
    }
    return report


def report_bytes() -> bytes:
    return canonical_bytes(build_report())


def sidecar_bytes(report_payload: bytes) -> bytes:
    return (sha256_bytes(report_payload) + "  report.json\n").encode("ascii")


def sources_bytes(report_payload: bytes, sidecar_payload: bytes) -> bytes:
    lines = [
        "# SHA-256 pins for SDK-STREAMING-CONFORMER-TED.",
        "# source: paths are workspace-relative; other external paths are SDK-worktree-relative.",
        "# Local paths are SDK-worktree-relative. Absent assets are ledger entries, not file pins.",
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
        "task_id": TASK_ID, "title": TITLE, "component_id": COMPONENT,
        "repository": REPOSITORY, "contract_version": "0.1",
        "base_commit": BASE_COMMIT, "branch": BRANCH, "reviewer": REVIEWER,
        "profile": PROFILE, "decision": DECISION, "defer_before": DEFER_BEFORE,
        "evidence_status": EVIDENCE_STATUS, "qualification_status": QUALIFICATION_STATUS,
        "status": STATUS, "task_prefix": TASK_PREFIX,
        "format": dict(BOUNDARY["format"]), "boundary": dict(BOUNDARY),
        "scope": dict(SCOPE), "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS), "asset_ledger": dict(ASSET_LEDGER),
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
            "The caller-supplied asset reference is metadata-only and never executed.",
            "Only the task-local evidence directory is written.",
            "No source, checkpoint, config, runtime, audio or corpus artifact is bundled.",
            "No missing, blocked or synthetic result qualifies the candidate.",
            "Only stable board-row identity enters canonical bytes or gates.",
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
