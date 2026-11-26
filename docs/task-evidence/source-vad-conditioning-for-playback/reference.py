# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic task-local evidence builder for Source/VAD playback conditioning.

This package is feasibility evidence only. It models a caller-supplied-asset
intake boundary and a model-free typed-annotation rate envelope. It does not
import, load, link, execute, copy, vendor or download a VAD model, an ASR gate,
a playback actuator, a research implementation or an audio corpus. No real
audio, listening, device timing, benchmark or release result is claimed.
"""

from __future__ import annotations

from fractions import Fraction
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

SCHEMA_REPORT = "audio-sdk/task-evidence-report/0.1"
SCHEMA_CONTRACT = "audio-sdk/task-evidence-contract/0.1"
SCHEMA_MANIFEST = "audio-sdk/source-vad-conditioning-for-playback/caller-supplied/0.1"
SCHEMA_ENVELOPE = "audio-sdk/source-vad-conditioning-for-playback/envelope/0.1"
TASK_ID = "SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK"
TITLE = "Source/VAD conditioning for playback"
COMPONENT = "source-vad-conditioning-for-playback"
REPOSITORY = "audio-sdk"
BASE_COMMIT = "022a7ad3cedf35aba70ef93b32b71ae51e1e30ca"
BRANCH = "swarm/SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK"
REVIEWER = "reviewer-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK"
PROFILE = "Rate"
DECISION = "DEFER"
DEFER_BEFORE = "opt_in_adapter_exposure"
EVIDENCE_STATUS = "incomplete"
QUALIFICATION_STATUS = "not_qualified"
STATUS = "proposal_only_asset_intake_incomplete_not_qualified"

# Installed v0 geometry only. No provider, default or ABI is changed.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "float32"
FIXTURE_SAMPLES = 16000
MIN_DWELL_SAMPLES = 3200  # 200 ms at 16 kHz, from the pinned design note.
RATE_MIN = Fraction(3, 4)
RATE_MAX = Fraction(3, 2)

SOURCE_PINS: Dict[str, str] = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "cpp-library/pipeline-validation/playback-speed/README.md":
        "a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f",
    "cpp-library/pipeline-validation/playback-speed/results/report.md":
        "9c9383297b1160dbe4f7261f789b493d70354b11930f4d8527b20b0ca8c87c34",
    "cpp-library/pipeline-validation/playback-speed/results/results.json":
        "69b5bcc4dc3740bacc182e93419b6a83d5c3eebba7d9b4dfdd8fe4b09813cfc1",
    "REALTIME_COMPONENT_CANDIDATES.md":
        "294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d",
    "research/tsm-followup-20261101/README.md":
        "01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f",
    "research/voice-enhancement-20261101/agent-vad-chain-followup/REPORT.md":
        "4e1de799b62ab7fee1a0def421ed9d152d1ccdb0c966141e9bc09ddb5e6e10b2",
    "adapters/silero-vad/adapter.json":
        "45222fd98fe1bd76550d0529cdaa442783807a727880b168d7879eca4f54a60a",
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
    "schemas/descriptor.schema.json":
        "9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba",
    "schemas/effective-config.schema.json":
        "55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea",
    "docs/task-evidence/silero-vad-pause-duration-rules/README.md":
        "b6e422c591364dffa8b6ab0d3c9c78a579a6c85c88f831d86ee8c9d27593ab1f",
    "docs/task-evidence/silero-vad-pause-duration-rules/report.json":
        "9aebd32c6dc61cf4c5d3d5e0b38fd82a2f083792a453bf9db9548e52cfa5b22d",
    "docs/task-evidence/aix-speed-asr-guided-planner/README.md":
        "4a5748b4e8d4c723b5ef2ce606c270c2d14b07beb9930b062520190cf0d8b28c",
    "docs/task-evidence/aix-speed-asr-guided-planner/report.json":
        "a71ce94ad0b701c9d302edf1c74338c7d1586d573a7295510fd3584b26110873",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/README.md":
        "1ccece1085e1d6e821891feffb0c19fc494227bfd5e8a656657ffd7081cf959c",
}

SOURCE_LINES: Tuple[Dict[str, Any], ...] = (
    {
        "id": "content-gate-classes",
        "path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "line": 616,
        "text": "**Content gate.** Classify 20–50 ms frames, then aggregate into segments of at least 200–300 ms:",
    },
    {
        "id": "vad-silence-action",
        "path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "line": 620,
        "text": "| Silence / pause | VAD (Silero is already vendored) | Compress hard, or cut with a 5–10 ms crossfade |",
    },
    {
        "id": "lookahead-unavoidable",
        "path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "line": 649,
        "text": "**Lookahead is unavoidable.** You cannot slow the start of an utterance after you have already played it. The output must be delayed by the classifier's lookahead `L` (roughly 200–500 ms for streaming ASR partials; 0.5–1 s for reliable word timestamps). That `L` is added latency even at 1.0× and must be reported separately from the stretcher's algorithmic delay. Without lookahead, the first 200–500 ms of a fast utterance plays at 1.0×.",
    },
    {
        "id": "s1-no-semantics",
        "path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "line": 664,
        "text": "1. **S1 — no semantics:** VAD + syllable rate + silence compression. This already delivers most of the benefit and needs no ASR.",
    },
    {
        "id": "gate-partly-done",
        "path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "line": 1015,
        "text": "2. **P1 (partly done):** the content gate exists as a Vosk batch call in the harness (IoU 0.94–0.95 against construction-time labels on TTS). It has **not** been measured as a block-streaming gate, and its word timestamps are uncalibrated. The planned sherpa-onnx streaming gate remains P1.",
    },
    {
        "id": "pre-screen-limited",
        "path": "cpp-library/pipeline-validation/playback-speed-candidates.md",
        "line": 1028,
        "text": "The pre-screen does **not** establish a WER difference between D1 and D2, and no listener has scored the output. Carry **D2 + Sonic** as the cost baseline and **D2 + Bungee** as the quality reference into the next gate. Do not choose the gate or the planner on three clips.",
    },
    {
        "id": "vad-candidate-comparison",
        "path": "REALTIME_COMPONENT_CANDIDATES.md",
        "line": 10,
        "text": "| Silero VAD 6.2.3 | Stateful speech detection | 68.35 µs per 20 ms frame; held-out AMI FN 19.43%, FP 8.20%. Stateful C++ path exists. |",
    },
    {
        "id": "typed-annotation-plan-note",
        "path": "audio-benchmark-platform/plan/INVENTORY.json",
        "line": 8231,
        "text": '"plan_note": "Use typed content annotations and measured unknown-span behavior, without turning every silence decision into deletion.",',
    },
    {
        "id": "rate-profile",
        "path": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "line": 21,
        "text": "| Rate | Measure source/output mapping, duration, pitch, transient audibility and playback buffering. Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window. Keep pause or filler decisions tied to source timestamps and measure speech preservation. |",
    },
)

BOARD_STABLE_SHA256 = (
    "09fef7c15128cd042ef7b4e088c1dd88b5e02e4475ba9a07d53614304af21ff9"
)
LINK_FIELDS = ("id", "title", "repository", "mode", "depends_on", "component")
MUTABLE_FIELDS_EXCLUDED = (
    "status", "owner", "claim", "review", "handoff", "blocked_reason",
    "dispatch_priority", "history", "write_scope", "deliverable", "acceptance",
    "evidence",
)
TASK_PREFIX = "docs/task-evidence/source-vad-conditioning-for-playback/"
LOCAL_PIN_PATHS: Tuple[str, ...] = (
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

BOUNDARY: Dict[str, Any] = {
    "format": {
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "sample_format": SAMPLE_FORMAT,
        "frame_samples": FRAME_SAMPLES,
    },
    "registered": False,
    "enabled_by_default": False,
    "default_selected": False,
    "descriptor_settings": {},
    "public_api_abi_change": False,
    "provider_registration": False,
    "processor_exposure": False,
    "adapter_exposure": False,
    "shared_build_change": False,
    "ci_change": False,
    "board_or_handoff_change": False,
}

SCOPE: Dict[str, Any] = {
    "task_local_only": True,
    "synthetic_only": True,
    "caller_assets_present": False,
    "real_audio": False,
    "listening": False,
    "device_timing": False,
    "benchmark": False,
    "release_claim": False,
    "model_download": False,
    "provider_default_or_abi_change": False,
}

NEGATIVE_CLAIMS: Tuple[str, ...] = (
    "No VAD model, ASR gate, syllable estimator or time-stretcher is loaded or executed.",
    "No exact caller source, weights, runtime lock, typed annotation schema or rights-cleared cohort is present.",
    "No real audio is read, written, rendered, played or listened to.",
    "No device timing, callback deadline, pacing or buffer occupancy result is measured.",
    "No source-reported VAD score, pre-screen RTF, WER proxy or IoU is reproduced or promoted.",
    "No silence decision is represented as deletion; unknown spans are retained and explicitly typed.",
    "No provider, descriptor, registry entry, default, ABI, shared-build or CI file is changed.",
    "No benchmark, release, public admission or qualification result is claimed.",
)

REQUIRED_ASSETS: Tuple[Dict[str, Any], ...] = (
    {
        "asset_id": "source-vad-conditioning.source-revision",
        "role": "runnable_source_revision",
        "storage": "external",
        "declared_sha256": None,
        "declared_byte_count": None,
        "present_locally": False,
    },
    {
        "asset_id": "source-vad-conditioning.vad-weights",
        "role": "exact_vad_weights",
        "storage": "external",
        "declared_sha256": None,
        "declared_byte_count": None,
        "present_locally": False,
    },
    {
        "asset_id": "source-vad-conditioning.runtime-lock",
        "role": "locked_runtime_and_dependencies",
        "storage": "external",
        "declared_sha256": None,
        "declared_byte_count": None,
        "present_locally": False,
    },
    {
        "asset_id": "source-vad-conditioning.annotation-schema",
        "role": "typed_content_annotation_schema",
        "storage": "external",
        "declared_sha256": None,
        "declared_byte_count": None,
        "present_locally": False,
    },
    {
        "asset_id": "source-vad-conditioning.cohort-manifest",
        "role": "rights_cleared_matched_cohort_manifest",
        "storage": "external",
        "declared_sha256": None,
        "declared_byte_count": None,
        "present_locally": False,
    },
    {
        "asset_id": "source-vad-conditioning.reference-output",
        "role": "matched_reference_output",
        "storage": "external",
        "declared_sha256": None,
        "declared_byte_count": None,
        "present_locally": False,
    },
)

CALLER_MANIFEST_FIELDS: Tuple[str, ...] = (
    "schema_id", "task_id", "candidate_id", "candidate_family", "fixture_id",
    "source_revision", "source_license_id", "runtime_lock_id",
    "annotation_schema_id", "cohort_manifest_id", "reference_output_id",
    "attestation", "rate_policy_id", "evidence_class", "credential_review_id",
    "counsel_review_id", "assets",
)
CALLER_ASSET_FIELDS: Tuple[str, ...] = (
    "asset_id", "path", "sha256", "byte_count", "storage", "license_id",
    "rights_attestation",
)
FIXED_ATTESTATION = (
    "caller-owned assets supplied by exact id, byte count and sha256; no SDK "
    "file access, download or default exposure"
)
ASSET_ROOT = "/caller-owned/source-vad-conditioning"
MAX_ASSET_BYTES = 512 * 1024 * 1024


class ReferenceRejection(ValueError):
    """Fail-closed rejection with a stable machine-readable code."""

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
    text = README_PATH.read_text(encoding="utf-8")
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


README_PATH = TASK_DIR / "README.md"


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
        lines = (SOURCE_ROOT / item["path"]).read_text(encoding="utf-8").splitlines()
        if lines[item["line"] - 1].strip() != item["text"]:
            raise ValueError("source_line_mismatch:" + item["id"])
        entries.append({
            "id": item["id"],
            "path": item["path"],
            "line": item["line"],
            "sha256": sha256_file(SOURCE_ROOT / item["path"]),
            "text": item["text"],
        })
    return {"entries": entries, "line_count": len(entries)}


def validate_asset_pins() -> None:
    for path, digest in SOURCE_PINS.items():
        target = SOURCE_ROOT / path
        if not target.is_file() or sha256_file(target) != digest:
            raise ValueError("source_pin_stale:" + path)
    for path, digest in BOUNDARY_PINS.items():
        target = SDK_ROOT / path
        if not target.is_file() or sha256_file(target) != digest:
            raise ValueError("boundary_pin_stale:" + path)
    source_lines()


ABSENT_PREFIXES: Tuple[str, ...] = (
    "data/sources/source-vad-conditioning",
    "data/models/source-vad-conditioning",
    "data/envs/source-vad-conditioning",
    "data/reference/source-vad-conditioning",
    "data/licenses/source-vad-conditioning",
)


def absent_artifact_probe() -> Dict[str, Any]:
    found: Dict[str, List[str]] = {"workspace": [], "sdk_worktree": []}
    for key, base in (("workspace", SOURCE_ROOT), ("sdk_worktree", SDK_ROOT)):
        for prefix in ABSENT_PREFIXES:
            path = base / prefix
            if path.exists() or any(base.glob(prefix + "*")):
                found[key].append(prefix)
    return {
        "present": False,
        "required_asset_count": len(REQUIRED_ASSETS),
        "workspace_found": found["workspace"],
        "sdk_worktree_found": found["sdk_worktree"],
        "searched_prefixes": list(ABSENT_PREFIXES),
        "note": "Path absence is not a runtime, rights or quality result.",
    }


def asset_pins_absent() -> bool:
    probe = absent_artifact_probe()
    return not probe["workspace_found"] and not probe["sdk_worktree_found"]


def valid_manifest(*, root: str = ASSET_ROOT) -> Dict[str, Any]:
    assets: List[Dict[str, Any]] = []
    for item in REQUIRED_ASSETS:
        relative = item["asset_id"].split(".", 1)[1].replace("-", "_") + ".bin"
        payload = ("caller-supplied synthetic placeholder for "
                   + item["asset_id"]).encode("utf-8")
        assets.append({
            "asset_id": item["asset_id"],
            "path": root + "/" + relative,
            "sha256": sha256_bytes(payload),
            "byte_count": len(payload),
            "storage": "external",
            "license_id": "caller-declared-not-reviewed",
            "rights_attestation": "caller-attested-not-verified",
        })
    return {
        "schema_id": SCHEMA_MANIFEST,
        "task_id": TASK_ID,
        "candidate_id": COMPONENT,
        "candidate_family": "rate-and-content",
        "fixture_id": "synthetic-16k-mono-160-frame-1s",
        "source_revision": "a" * 40,
        "source_license_id": "caller-declared-not-reviewed",
        "runtime_lock_id": "runtime-lock-shape-only",
        "annotation_schema_id": "typed-annotation-schema-shape-only",
        "cohort_manifest_id": "rights-cleared-cohort-shape-only",
        "reference_output_id": "matched-reference-output-shape-only",
        "attestation": FIXED_ATTESTATION,
        "rate_policy_id": "rate-envelope-0.1",
        "evidence_class": "caller_supplied_shape_only",
        "credential_review_id": "review-shape-only",
        "counsel_review_id": "counsel-shape-only",
        "assets": assets,
    }


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate_caller_manifest(manifest: Any) -> Dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ReferenceRejection("MANIFEST_NOT_OBJECT")
    if set(manifest) != set(CALLER_MANIFEST_FIELDS):
        raise ReferenceRejection("SCHEMA_FIELD_SET")
    if manifest["schema_id"] != SCHEMA_MANIFEST:
        raise ReferenceRejection("MANIFEST_SCHEMA_MISMATCH")
    if manifest["task_id"] != TASK_ID:
        raise ReferenceRejection("TASK_ID_MISMATCH")
    if manifest["candidate_id"] != COMPONENT:
        raise ReferenceRejection("CANDIDATE_ID_MISMATCH")
    if manifest["candidate_family"] != "rate-and-content":
        raise ReferenceRejection("CANDIDATE_FAMILY_MISMATCH")
    for field in ("fixture_id", "source_license_id", "runtime_lock_id",
                  "annotation_schema_id", "cohort_manifest_id",
                  "reference_output_id", "credential_review_id",
                  "counsel_review_id"):
        if not isinstance(manifest[field], str) or not manifest[field]:
            raise ReferenceRejection("IDENTIFIER_INVALID:" + field)
    if not isinstance(manifest["source_revision"], str) \
            or re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"]) is None:
        raise ReferenceRejection("SOURCE_REVISION_INVALID")
    if manifest["attestation"] != FIXED_ATTESTATION:
        raise ReferenceRejection("ATTESTATION_INVALID")
    if manifest["rate_policy_id"] != "rate-envelope-0.1":
        raise ReferenceRejection("RATE_POLICY_INVALID")
    if manifest["evidence_class"] != "caller_supplied_shape_only":
        raise ReferenceRejection("EVIDENCE_CLASS_INVALID")
    if manifest["credential_review_id"] == manifest["counsel_review_id"]:
        raise ReferenceRejection("EVIDENCE_CLASS_COLLISION")
    assets = manifest["assets"]
    if not isinstance(assets, list) or len(assets) != len(REQUIRED_ASSETS):
        raise ReferenceRejection("ASSET_SET_MISMATCH")
    expected_ids = [item["asset_id"] for item in REQUIRED_ASSETS]
    if sorted(asset.get("asset_id") for asset in assets
              if isinstance(asset, dict)) != sorted(expected_ids):
        raise ReferenceRejection("ASSET_SET_MISMATCH")
    paths: List[str] = []
    for asset in assets:
        if not isinstance(asset, dict) or set(asset) != set(CALLER_ASSET_FIELDS):
            raise ReferenceRejection("ASSET_FIELD_SET")
        path = asset["path"]
        if not isinstance(path, str) or not path.startswith("/"):
            raise ReferenceRejection("ASSET_PATH_NOT_ABSOLUTE")
        if ".." in Path(path).parts or path.startswith("//"):
            raise ReferenceRejection("ASSET_PATH_TRAVERSAL")
        if path in paths:
            raise ReferenceRejection("ASSET_PATH_DUPLICATE")
        paths.append(path)
        if not _is_sha256(asset["sha256"]):
            raise ReferenceRejection("ASSET_SHA256_INVALID")
        if not _is_int(asset["byte_count"]) or not 0 < asset["byte_count"] <= MAX_ASSET_BYTES:
            raise ReferenceRejection("ASSET_BYTE_COUNT_INVALID")
        if asset["storage"] != "external":
            raise ReferenceRejection("ASSET_STORAGE_INVALID")
        if not isinstance(asset["license_id"], str) or not asset["license_id"]:
            raise ReferenceRejection("ASSET_LICENSE_INVALID")
        if not isinstance(asset["rights_attestation"], str) or not asset["rights_attestation"]:
            raise ReferenceRejection("ASSET_RIGHTS_INVALID")
    return manifest


def verify_assets(manifest: Any, payloads: Dict[str, bytes]) -> Dict[str, Any]:
    normalized = validate_caller_manifest(manifest)
    checked: List[Dict[str, Any]] = []
    for asset in normalized["assets"]:
        payload = payloads.get(asset["path"])
        if payload is None:
            raise ReferenceRejection("ASSET_ABSENT")
        if len(payload) != asset["byte_count"]:
            raise ReferenceRejection("ASSET_BYTE_COUNT_MISMATCH")
        if sha256_bytes(payload) != asset["sha256"]:
            raise ReferenceRejection("ASSET_HASH_MISMATCH")
        checked.append({
            "asset_id": asset["asset_id"],
            "byte_count": asset["byte_count"],
            "sha256": asset["sha256"],
        })
    return {
        "assets": checked,
        "count": len(checked),
        "qualifies": False,
        "note": "Hash-matched bytes are shape-only; no source is parsed or executed.",
    }


def valid_envelope() -> Dict[str, Any]:
    return {
        "schema_id": SCHEMA_ENVELOPE,
        "fixture_id": "synthetic-16k-mono-160-frame-1s",
        "source_end": FIXTURE_SAMPLES,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "rate_policy_id": "rate-envelope-0.1",
        "is_synthetic_control": True,
        "is_candidate_result": False,
        "segments": [
            {"id": "seg-00-unknown", "start": 0, "end": 3200,
             "class": "unknown", "rate_num": 1, "rate_den": 1,
             "label": "synthetic-annotation-unknown"},
            {"id": "seg-01-speech", "start": 3200, "end": 8000,
             "class": "speech", "rate_num": 4, "rate_den": 5,
             "label": "synthetic-annotation-speech"},
            {"id": "seg-02-silence", "start": 8000, "end": 12800,
             "class": "silence", "rate_num": 4, "rate_den": 3,
             "label": "synthetic-annotation-silence"},
            {"id": "seg-03-speech", "start": 12800, "end": 16000,
             "class": "speech", "rate_num": 1, "rate_den": 1,
             "label": "synthetic-annotation-speech"},
        ],
    }


ENVELOPE_FIELDS = (
    "schema_id", "fixture_id", "source_end", "sample_rate_hz", "channels",
    "frame_samples", "rate_policy_id", "is_synthetic_control",
    "is_candidate_result", "segments",
)
SEGMENT_FIELDS = ("id", "start", "end", "class", "rate_num", "rate_den", "label")


def validate_envelope(envelope: Any) -> Dict[str, Any]:
    if not isinstance(envelope, dict):
        raise ReferenceRejection("ENVELOPE_NOT_OBJECT")
    if set(envelope) != set(ENVELOPE_FIELDS):
        raise ReferenceRejection("ENVELOPE_FIELD_SET")
    if envelope["schema_id"] != SCHEMA_ENVELOPE:
        raise ReferenceRejection("ENVELOPE_SCHEMA_MISMATCH")
    if envelope["fixture_id"] != "synthetic-16k-mono-160-frame-1s":
        raise ReferenceRejection("FIXTURE_ID_MISMATCH")
    for field in ("source_end", "sample_rate_hz", "channels", "frame_samples"):
        if not _is_int(envelope[field]):
            raise ReferenceRejection("GEOMETRY_TYPE_INVALID:" + field)
    if (envelope["sample_rate_hz"], envelope["channels"], envelope["frame_samples"],
            envelope["source_end"]) != (SAMPLE_RATE_HZ, CHANNELS, FRAME_SAMPLES,
                                        FIXTURE_SAMPLES):
        raise ReferenceRejection("GEOMETRY_MISMATCH")
    if envelope["rate_policy_id"] != "rate-envelope-0.1":
        raise ReferenceRejection("RATE_POLICY_INVALID")
    if envelope["is_synthetic_control"] is not True:
        raise ReferenceRejection("SYNTHETIC_FLAG_INVALID")
    if envelope["is_candidate_result"] is not False:
        raise ReferenceRejection("CANDIDATE_CLAIM")
    segments = envelope["segments"]
    if not isinstance(segments, list) or not segments:
        raise ReferenceRejection("SEGMENTS_INVALID")
    rows: List[Dict[str, Any]] = []
    output_end = 0
    ids: List[str] = []
    for segment in segments:
        if not isinstance(segment, dict) or set(segment) != set(SEGMENT_FIELDS):
            raise ReferenceRejection("SEGMENT_FIELD_SET")
        if not isinstance(segment["id"], str) or not segment["id"]:
            raise ReferenceRejection("SEGMENT_ID_INVALID")
        if segment["id"] in ids:
            raise ReferenceRejection("SEGMENT_ID_DUPLICATE")
        ids.append(segment["id"])
        start, end = segment["start"], segment["end"]
        if not _is_int(start) or not _is_int(end):
            raise ReferenceRejection("INTERVAL_TYPE_INVALID")
        if start < 0 or end <= start or end > envelope["source_end"]:
            raise ReferenceRejection("INTERVAL_RANGE_INVALID")
        if end - start < MIN_DWELL_SAMPLES:
            raise ReferenceRejection("MIN_DWELL_VIOLATION")
        label = segment["class"]
        if label not in ("speech", "silence", "unknown"):
            raise ReferenceRejection("CONTENT_CLASS_INVALID")
        num, den = segment["rate_num"], segment["rate_den"]
        if not _is_int(num) or not _is_int(den) or num <= 0 or den <= 0 or num > 100 or den > 100:
            raise ReferenceRejection("RATE_INVALID")
        rate = Fraction(num, den)
        if rate < RATE_MIN or rate > RATE_MAX:
            raise ReferenceRejection("RATE_OUT_OF_RANGE")
        if label == "speech" and rate > 1:
            raise ReferenceRejection("SPEECH_SPEEDUP_FORBIDDEN")
        if label == "silence" and rate < 1:
            raise ReferenceRejection("SILENCE_SLOWDOWN_FORBIDDEN")
        if label == "unknown" and rate != 1:
            raise ReferenceRejection("UNKNOWN_RATE_VIOLATION")
        length = end - start
        produced = Fraction(length * den, num)
        if produced.denominator != 1:
            raise ReferenceRejection("NONINTEGER_OUTPUT_BOUNDARY")
        produced_int = int(produced)
        rows.append({
            "id": segment["id"],
            "source_start": start,
            "source_end": end,
            "class": label,
            "rate": str(rate),
            "output_start": output_end,
            "output_end": output_end + produced_int,
            "output_samples": produced_int,
            "retained": label != "unknown" or produced_int == length,
        })
        output_end += produced_int
    cursor = 0
    for segment in segments:
        if segment["start"] != cursor:
            raise ReferenceRejection("INTERVAL_GAP_OR_OVERLAP")
        cursor = segment["end"]
    if cursor != envelope["source_end"]:
        raise ReferenceRejection("UNCOVERED_TAIL")
    if output_end != envelope["source_end"]:
        raise ReferenceRejection("DURATION_NOT_CLOSED")
    return {
        "schema_id": SCHEMA_ENVELOPE,
        "segments": rows,
        "source_end": envelope["source_end"],
        "output_end": output_end,
        "rate_min": str(RATE_MIN),
        "rate_max": str(RATE_MAX),
        "min_dwell_samples": MIN_DWELL_SAMPLES,
        "qualifies": False,
    }


def envelope_adverse_cases() -> Dict[str, Any]:
    cases: List[Tuple[str, Any, str]] = []

    def add(name: str, mutate: Any, code: str) -> None:
        cases.append((name, mutate, code))

    add("boolean_source_end", lambda e: e.update(source_end=True), "GEOMETRY_TYPE_INVALID:source_end")
    add("wrong_sample_rate", lambda e: e.update(sample_rate_hz=48000), "GEOMETRY_MISMATCH")
    add("wrong_channels", lambda e: e.update(channels=2), "GEOMETRY_MISMATCH")
    add("wrong_frame_samples", lambda e: e.update(frame_samples=480), "GEOMETRY_MISMATCH")
    add("candidate_claim", lambda e: e.update(is_candidate_result=True), "CANDIDATE_CLAIM")
    add("not_synthetic", lambda e: e.update(is_synthetic_control=False), "SYNTHETIC_FLAG_INVALID")
    add("extra_field", lambda e: e.update(extra="x"), "ENVELOPE_FIELD_SET")
    add("missing_field", lambda e: e.pop("rate_policy_id"), "ENVELOPE_FIELD_SET")
    add("empty_segments", lambda e: e.update(segments=[]), "SEGMENTS_INVALID")
    add("gap", lambda e: e["segments"][1].update(start=3300), "INTERVAL_GAP_OR_OVERLAP")
    add("overlap", lambda e: e["segments"][2].update(start=7900), "INTERVAL_GAP_OR_OVERLAP")
    add("uncovered_tail", lambda e: e.update(segments=e["segments"][:3]), "UNCOVERED_TAIL")
    add("zero_length", lambda e: e["segments"][1].update(end=3200), "INTERVAL_RANGE_INVALID")
    add("duplicate_id", lambda e: e["segments"][1].update(id="seg-00-unknown"), "SEGMENT_ID_DUPLICATE")
    add("unsupported_class", lambda e: e["segments"][1].update(**{"class": "music"}), "CONTENT_CLASS_INVALID")
    add("speech_speedup", lambda e: e["segments"][1].update(rate_num=6, rate_den=5), "SPEECH_SPEEDUP_FORBIDDEN")
    add("silence_slowdown", lambda e: e["segments"][2].update(rate_num=3, rate_den=4), "SILENCE_SLOWDOWN_FORBIDDEN")
    add("unknown_as_silence", lambda e: e["segments"][0].update(rate_num=4, rate_den=3), "UNKNOWN_RATE_VIOLATION")
    add("rate_below_floor", lambda e: e["segments"][1].update(rate_num=2, rate_den=3), "RATE_OUT_OF_RANGE")
    add("rate_above_ceiling", lambda e: e["segments"][1].update(rate_num=8, rate_den=5), "RATE_OUT_OF_RANGE")
    add("zero_denominator", lambda e: e["segments"][1].update(rate_den=0), "RATE_INVALID")
    add("noninteger_output", lambda e: e["segments"][1].update(end=8001, rate_num=4, rate_den=5), "NONINTEGER_OUTPUT_BOUNDARY")
    add("duration_not_closed", lambda e: e["segments"][2].update(rate_num=1, rate_den=1), "DURATION_NOT_CLOSED")
    def short_dwell(e: Dict[str, Any]) -> None:
        e["segments"][1]["end"] = 6300
        e["segments"][2]["start"] = 6300
    add("short_dwell", short_dwell, "MIN_DWELL_VIOLATION")
    results: List[Dict[str, Any]] = []
    for name, mutate, expected in cases:
        candidate = valid_envelope()
        mutate(candidate)
        actual = "NOT_REJECTED"
        try:
            validate_envelope(candidate)
        except ReferenceRejection as error:
            actual = error.code
        results.append({
            "id": name,
            "expected_code": expected,
            "actual_code": actual,
            "rejected": actual != "NOT_REJECTED",
        })
    for row in results:
        if row["actual_code"] != row["expected_code"]:
            raise ReferenceRejection("ADVERSE_CODE_MISMATCH:" + row["id"])
    return {
        "cases": results,
        "case_count": len(results),
        "accepted_count": sum(1 for row in results if not row["rejected"]),
        "all_rejected": all(row["rejected"] for row in results),
        "metrics": None,
    }


def manifest_adverse_cases() -> Dict[str, Any]:
    cases: List[Tuple[str, Any, str]] = []

    def add(name: str, mutate: Any, code: str) -> None:
        cases.append((name, mutate, code))

    add("manifest_not_object", lambda m: None, "MANIFEST_NOT_OBJECT")
    add("missing_field", lambda m: m.pop("attestation"), "SCHEMA_FIELD_SET")
    add("extra_field", lambda m: m.update(extra="x"), "SCHEMA_FIELD_SET")
    add("wrong_task", lambda m: m.update(task_id="SDK-OTHER"), "TASK_ID_MISMATCH")
    add("wrong_candidate", lambda m: m.update(candidate_id="other"), "CANDIDATE_ID_MISMATCH")
    add("short_revision", lambda m: m.update(source_revision="a" * 39), "SOURCE_REVISION_INVALID")
    add("bad_attestation", lambda m: m.update(attestation="unchecked"), "ATTESTATION_INVALID")
    add("bad_rate_policy", lambda m: m.update(rate_policy_id="other"), "RATE_POLICY_INVALID")
    add("wrong_evidence_class", lambda m: m.update(evidence_class="benchmark"), "EVIDENCE_CLASS_INVALID")
    add("colliding_review_ids", lambda m: m.update(counsel_review_id=m["credential_review_id"]),
        "EVIDENCE_CLASS_COLLISION")
    add("missing_asset", lambda m: m["assets"].pop(), "ASSET_SET_MISMATCH")
    add("extra_asset", lambda m: m["assets"].append(dict(m["assets"][0])), "ASSET_SET_MISMATCH")
    add("relative_path", lambda m: m["assets"][0].update(path="relative/file.bin"),
        "ASSET_PATH_NOT_ABSOLUTE")
    add("traversal_path", lambda m: m["assets"][0].update(path="/caller-owned/../escape.bin"),
        "ASSET_PATH_TRAVERSAL")
    add("duplicate_path", lambda m: m["assets"][1].update(path=m["assets"][0]["path"]),
        "ASSET_PATH_DUPLICATE")
    add("uppercase_hash", lambda m: m["assets"][0].update(sha256="A" * 64), "ASSET_SHA256_INVALID")
    add("short_hash", lambda m: m["assets"][0].update(sha256="a" * 63), "ASSET_SHA256_INVALID")
    add("zero_byte_count", lambda m: m["assets"][0].update(byte_count=0), "ASSET_BYTE_COUNT_INVALID")
    add("oversize_byte_count", lambda m: m["assets"][0].update(byte_count=MAX_ASSET_BYTES + 1),
        "ASSET_BYTE_COUNT_INVALID")
    add("embedded_storage", lambda m: m["assets"][0].update(storage="embedded"), "ASSET_STORAGE_INVALID")
    add("extra_asset_field", lambda m: m["assets"][0].update(extra="x"), "ASSET_FIELD_SET")
    results: List[Dict[str, Any]] = []
    for name, mutate, expected in cases:
        candidate = valid_manifest()
        if name == "manifest_not_object":
            candidate = "not-an-object"  # type: ignore[assignment]
        else:
            mutate(candidate)
        actual = "NOT_REJECTED"
        try:
            validate_caller_manifest(candidate)
        except ReferenceRejection as error:
            actual = error.code
        results.append({
            "id": name,
            "expected_code": expected,
            "actual_code": actual,
            "rejected": actual != "NOT_REJECTED",
        })
    for row in results:
        if row["actual_code"] != row["expected_code"]:
            raise ReferenceRejection("ADVERSE_CODE_MISMATCH:" + row["id"])
    absent_code = "NOT_REJECTED"
    mismatch_code = "NOT_REJECTED"
    size_code = "NOT_REJECTED"
    manifest = valid_manifest()
    try:
        verify_assets(manifest, {})
    except ReferenceRejection as error:
        absent_code = error.code
    payloads = {asset["path"]: b"x" * asset["byte_count"] for asset in manifest["assets"]}
    try:
        verify_assets(manifest, payloads)
    except ReferenceRejection as error:
        mismatch_code = error.code
    matched = {asset["path"]: ("caller-supplied synthetic placeholder for "
                               + asset["asset_id"]).encode("utf-8")
               for asset in manifest["assets"]}
    accepted_shape = verify_assets(manifest, matched)
    wrong_size = dict(matched)
    wrong_size[manifest["assets"][0]["path"]] = b"x"
    try:
        verify_assets(manifest, wrong_size)
    except ReferenceRejection as error:
        size_code = error.code
    return {
        "cases": results,
        "case_count": len(results),
        "accepted_count": sum(1 for row in results if not row["rejected"]),
        "all_rejected": all(row["rejected"] for row in results),
        "asset_checks": {
            "absent_code": absent_code,
            "hash_mismatch_code": mismatch_code,
            "byte_count_mismatch_code": size_code,
            "hash_matched_shape_only": accepted_shape["count"],
            "hash_matched_qualifies": accepted_shape["qualifies"],
        },
        "metrics": None,
    }


def invalid_json_cases() -> Dict[str, Any]:
    samples = ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
               '{"a":-Infinity}', '{"a":1} extra', "")
    results = []
    for index, text in enumerate(samples):
        rejected = False
        try:
            strict_loads(text)
        except ValueError:
            rejected = True
        results.append({"id": "json-" + str(index), "rejected": rejected})
    return {
        "cases": results,
        "case_count": len(results),
        "accepted_count": sum(1 for row in results if not row["rejected"]),
        "all_rejected": all(row["rejected"] for row in results),
    }


def invalid_pin_cases() -> Dict[str, Any]:
    digest = "a" * 64
    samples = (
        digest + "  source:duplicate\n" + digest + "  source:duplicate\n",
        "abc  source:short\n",
        digest + "  /absolute\n",
        digest + "  source:../escape\n",
    )
    results = []
    for index, text in enumerate(samples):
        rejected = False
        try:
            parse_pin_lines(text)
        except ValueError:
            rejected = True
        results.append({"id": "pin-" + str(index), "rejected": rejected})
    return {
        "cases": results,
        "case_count": len(results),
        "accepted_count": sum(1 for row in results if not row["rejected"]),
        "all_rejected": all(row["rejected"] for row in results),
    }


def identity_control() -> Dict[str, Any]:
    pattern = [(index * 37 % 251) - 125 for index in range(FIXTURE_SAMPLES)]
    payload = canonical_bytes(pattern)
    envelope = valid_envelope()
    for segment in envelope["segments"]:
        segment["rate_num"] = 1
        segment["rate_den"] = 1
    mapping = validate_envelope(envelope)
    output = list(pattern)
    byte_identical = canonical_bytes(output) == payload
    return {
        "label": "integer identity, not VAD-conditioned output",
        "pattern_sha256": sha256_bytes(payload),
        "output_sha256": sha256_bytes(canonical_bytes(output)),
        "alternating_integer_sequence_byte_identical": byte_identical,
        "source_end": mapping["source_end"],
        "output_end": mapping["output_end"],
        "qualifies": False,
    }


def unknown_span_probe() -> Dict[str, Any]:
    envelope = valid_envelope()
    mapping = validate_envelope(envelope)
    unknown = mapping["segments"][0]
    # Counterfactual arithmetic only: this envelope deliberately fails the
    # duration-closure validator, so it is not passed through that validator.
    wrong_unknown_length = int(Fraction(unknown["source_end"] - unknown["source_start"]) * 3 / 4)
    return {
        "source_interval": [unknown["source_start"], unknown["source_end"]],
        "class": "unknown",
        "retained": True,
        "rate": unknown["rate"],
        "output_samples": unknown["output_samples"],
        "wrong_policy_class": "silence",
        "wrong_policy_output_samples": wrong_unknown_length,
        "wrong_policy_lost_samples": unknown["output_samples"] - wrong_unknown_length,
        "silence_decision_is_deletion": False,
        "unknown_promoted_to_nonspeech": False,
        "qualifies": False,
        "note": "Synthetic annotation arithmetic only; no measured classifier behavior.",
    }


def rate_profile() -> Dict[str, Any]:
    rows = [
        ("source_output_mapping", "Exact half-open sample intervals",
         "four contiguous typed segments, integer output boundaries"),
        ("duration", "Source/output duration and rate closure",
         "16000 source samples -> 16000 output samples"),
        ("pitch", "Pitch audibility", "not_measured_no_rendered_audio"),
        ("transient_audibility", "Transient audibility", "not_measured_no_rendered_audio"),
        ("playback_buffering", "Buffering, fill/flush and gap behavior",
         "no device FIFO; no timing claim"),
        ("rate_cases", "1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial",
         "synthetic classes only at 1, 4/5 and 4/3; no unfamiliar speech or music"),
        ("pause_timestamps", "Pause/filler decisions tied to source timestamps",
         "typed intervals in 160-sample source coordinates"),
        ("speech_preservation", "Measured speech preservation",
         "not_measured_without_clean references or listening"),
        ("unknown_span", "Measured unknown-span behavior",
         "synthetic retention control; no classifier measurement"),
    ]
    return {
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md:21",
        "items": [
            {
                "id": item_id,
                "requirement": requirement,
                "synthetic_control": control,
                "status": "blocked",
                "qualifies": False,
            }
            for item_id, requirement, control in rows
        ],
        "item_count": len(rows),
        "qualifies": False,
    }


GATES: Tuple[Dict[str, Any], ...] = (
    {"id": "RG-01", "name": "exact_runnable_source", "status": "blocked",
     "qualifies": False, "missing": "exact source revision and build lock"},
    {"id": "RG-02", "name": "exact_assets_and_rights", "status": "blocked",
     "qualifies": False, "missing": "six caller assets with SHA-256, byte count and licence review"},
    {"id": "RG-03", "name": "installed_v0_boundary", "status": "blocked",
     "qualifies": False, "missing": "opt-in intake without ABI, registry or default change"},
    {"id": "RG-04", "name": "typed_content_annotations", "status": "blocked",
     "qualifies": False, "missing": "validated annotation schema on matched input"},
    {"id": "RG-05", "name": "unknown_span_behavior", "status": "blocked",
     "qualifies": False, "missing": "measured classifier unknown/deletion behavior"},
    {"id": "RG-06", "name": "rate_profile_evidence", "status": "blocked",
     "qualifies": False, "missing": "duration, pitch, transient, buffering and preservation evidence"},
    {"id": "RG-07", "name": "playback_pacing_and_listening", "status": "blocked",
     "qualifies": False, "missing": "target-device pacing, crossfade and listening result"},
    {"id": "RG-08", "name": "public_admission_review", "status": "blocked",
     "qualifies": False, "missing": "rights, counsel and opt-in release decision"},
)

EXACT_BLOCKERS: Tuple[Dict[str, Any], ...] = (
    {
        "id": "B-01",
        "blocker": (
            "No exact runnable source revision exists for the source/VAD "
            "conditioning policy. The pinned candidate note describes VAD + "
            "syllable rate + silence compression and a Vosk batch gate; the "
            "streaming gate is still planned, and no implementation revision "
            "is pinned."
        ),
        "reopen": (
            "Supply a 40-hex source revision, SHA-256 of the exact source "
            "archive, build lock and caller attestation through the manifest; "
            "verify hashes without downloading or executing source here."
        ),
    },
    {
        "id": "B-02",
        "blocker": (
            "No exact rights-cleared assets exist: VAD weights, runtime lock, "
            "typed annotation schema, cohort manifest, matched reference output "
            "and source each lack byte count, SHA-256, licence and consent "
            "review."
        ),
        "reopen": (
            "Caller supplies all six external assets by id, byte count and "
            "SHA-256 with reviewed licence/consent sidecars and verified bytes; "
            "no embedded asset or SDK file access is accepted."
        ),
    },
    {
        "id": "B-03",
        "blocker": (
            "No matched Rate-profile evidence exists. The pinned pre-screen "
            "used three clips and a batch gate, with no listener result, no "
            "block-streaming gate, no pitch/transient score and no measured "
            "unknown-span or speech-preservation result."
        ),
        "reopen": (
            "Run a rights-cleared matched cohort at installed 16 kHz mono "
            "float32/160-sample geometry and report exact source intervals, "
            "duration, pitch, transients, buffering, speech preservation and "
            "typed unknown-span outcomes separately."
        ),
    },
    {
        "id": "B-04",
        "blocker": (
            "No opt-in adapter intake or release decision exists, and the "
            "pinned note requires counsel review of the real-time playback "
            "policy before a shipping path is considered."
        ),
        "reopen": (
            "Obtain credential review, counsel posture and an application-local "
            "opt-in decision with no default, public registry or ABI change; "
            "keep public admission a separate later gate."
        ),
    },
)

SOURCE_REPORTED: Dict[str, Any] = {
    "qualifies": False,
    "entries": [
        {
            "id": "SR-01",
            "claim": "VAD + syllable rate + silence compression is staged S1 and needs no ASR",
            "source": "cpp-library/pipeline-validation/playback-speed-candidates.md:664",
        },
        {
            "id": "SR-02",
            "claim": "Silence can be compressed or cut with a 5-10 ms crossfade",
            "source": "cpp-library/pipeline-validation/playback-speed-candidates.md:620",
        },
        {
            "id": "SR-03",
            "claim": "Vosk content gate is batch-only, with uncalibrated timestamps",
            "source": "cpp-library/pipeline-validation/playback-speed-candidates.md:1015",
        },
        {
            "id": "SR-04",
            "claim": "Pre-screen has no listener result and cannot select a planner on three clips",
            "source": "cpp-library/pipeline-validation/playback-speed-candidates.md:1028",
        },
        {
            "id": "SR-05",
            "claim": "Silero VAD held-out AMI FN/FP and WebRTC/Speex numbers are separate candidate results",
            "source": "REALTIME_COMPONENT_CANDIDATES.md:9-13",
        },
    ],
    "separation": (
        "All entries are source-reported provenance. None is reproduced, "
        "pooled with the synthetic control or promoted to a candidate result."
    ),
}


def build_report() -> Dict[str, Any]:
    validate_asset_pins()
    envelope = validate_envelope(valid_envelope())
    probe = absent_artifact_probe()
    manifest_adverse = manifest_adverse_cases()
    envelope_adverse = envelope_adverse_cases()
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
            "required_asset_fields": list(CALLER_ASSET_FIELDS),
            "required_assets": [dict(item) for item in REQUIRED_ASSETS],
            "asset_root": ASSET_ROOT,
            "loaded": False,
            "executed": False,
            "note": "Metadata and byte-hash intake only; hash-matched assets still fail release gates.",
        },
        "typed_envelope": envelope,
        "identity_control": identity_control(),
        "unknown_span_probe": unknown_span_probe(),
        "rate_profile": rate_profile(),
        "asset_resolution": probe,
        "adverse": {
            "caller_manifest": manifest_adverse,
            "typed_envelope": envelope_adverse,
            "invalid_json": json_adverse,
            "invalid_pins": pin_adverse,
            "all_rejected": (manifest_adverse["all_rejected"]
                             and envelope_adverse["all_rejected"]
                             and json_adverse["all_rejected"]
                             and pin_adverse["all_rejected"]),
            "metrics": None,
        },
        "source_reported": dict(SOURCE_REPORTED),
        "source_lines": source_lines(),
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "gates": [dict(gate) for gate in GATES],
        "exact_blockers": [dict(item) for item in EXACT_BLOCKERS],
        "missing_evidence": [
            "exact runnable source revision, archive hash and build lock",
            "six exact external assets with byte counts, SHA-256 and rights sidecars",
            "validated typed-annotation schema on matched input",
            "measured unknown-span, deletion and crossfade behavior",
            "Rate-profile duration, pitch, transient, buffering and preservation results",
            "target pacing, listening and opt-in credential/counsel review",
        ],
        "reopening_conditions": [item["reopen"] for item in EXACT_BLOCKERS],
        "evidence_classes": {
            "source_reported": True,
            "synthetic": True,
            "caller_supplied_shape_only": True,
            "real_local_model_output": False,
            "real_audio": False,
            "listening": False,
            "device_timing": False,
            "benchmark": False,
            "release_claim": False,
        },
        "board_link": board_link(),
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
        "# SHA-256 pins for SDK-SOURCE-VAD-CONDITIONING-FOR-PLAYBACK.",
        "# source: paths are workspace-relative; other external paths are SDK-worktree-relative.",
        "# Local paths are SDK-worktree-relative. Missing caller assets are ledger entries, not file pins.",
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
            "No source, model, audio or runtime artifact is bundled, downloaded or executed.",
            "Caller manifests are validated as metadata and byte hashes only.",
            "Silence is compressed, never deleted; unknown spans are retained at rate 1.",
            "Model-free integer controls cannot qualify the candidate.",
            "All provider, default, ABI, registry, shared-build and CI flags remain false.",
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


if __name__ == "__main__":
    print("reference builder: import run.py to generate canonical artifacts")
